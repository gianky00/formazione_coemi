import logging
import json
import os
from datetime import datetime
from google.cloud import aiplatform
from app.core.config import settings
from app.db.session import get_db
from app.db.models import Certificato, ValidationStatus
from sqlalchemy.orm import Session, selectinload
from google.cloud import storage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_validated_certificates(db: Session):
    """Fetches manually validated certificates from the database."""
    return db.query(Certificato).filter(
        Certificato.stato_validazione == ValidationStatus.MANUAL
    ).options(
        selectinload(Certificato.dipendente),
        selectinload(Certificato.corso)
    ).all()

def generate_training_data(certificates: list) -> str:
    """Generates a JSONL string from a list of certificates."""
    lines = []
    for cert in certificates:
        # Construct the input prompt
        input_content = f"Extract entities from the certificate for {cert.dipendente.nome} {cert.dipendente.cognome} for the course {cert.corso.nome_corso}."

        # Construct the output with the expected entities
        output_content = {
            "nome": f"{cert.dipendente.nome} {cert.dipendente.cognome}",
            "corso": cert.corso.nome_corso,
            "data_rilascio": cert.data_rilascio.strftime('%d/%m/%Y'),
            "data_scadenza": cert.data_scadenza_calcolata.strftime('%d/%m/%Y') if cert.data_scadenza_calcolata else None,
            "categoria": cert.corso.categoria_corso
        }

        # Create the JSON structure for the training data
        training_example = {
            "input_text": input_content,
            "output_text": json.dumps(output_content, ensure_ascii=False)
        }

        lines.append(json.dumps(training_example, ensure_ascii=False))

    return "\n".join(lines)


def upload_to_gcs(bucket_name: str, source_data: str, destination_blob_name: str):
    """Uploads a string to a GCS bucket."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_string(source_data)
        logger.info(f"Successfully uploaded to GCS: gs://{bucket_name}/{destination_blob_name}")
        return f"gs://{bucket_name}/{destination_blob_name}"
    except Exception as e:
        logger.error(f"Failed to upload to GCS: {e}")
        raise

def start_fine_tuning_job():
    """
    Orchestrates the fine-tuning process:
    1. Fetches validated certificates.
    2. Generates the training dataset.
    3. Uploads the dataset to GCS.
    4. Starts the Vertex AI fine-tuning job.
    """
    db = next(get_db())
    certificates = get_validated_certificates(db)

    if not certificates:
        logger.info("No validated certificates found to start a fine-tuning job.")
        return {"message": "No validated certificates found."}

    training_data = generate_training_data(certificates)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    dataset_filename = f"training_data_{timestamp}.jsonl"

    gcs_uri = upload_to_gcs(
        bucket_name=settings.GCS_BUCKET_NAME,
        source_data=training_data,
        destination_blob_name=dataset_filename
    )

    aiplatform.init(project=settings.GOOGLE_CLOUD_PROJECT, location="europe-west1")

    job = aiplatform.PipelineJob(
        display_name=f"fine-tuning-job-{timestamp}",
        template_path="https://us-kfp.pkg.dev/ml-pipeline/large-language-model-pipelines/tune-large-model/v2.0.0",
        parameter_values={
            "project": settings.GOOGLE_CLOUD_PROJECT,
            "model_display_name": f"tuned-gemini-{timestamp}",
            "dataset_uri": gcs_uri,
            "location": "europe-west1",
            "large_model_reference": "gemini-1.0-pro-001",
            "train_steps": 300,
        }
    )

    job.submit()
    return {"job_name": job.name, "job_id": job.resource_name}
