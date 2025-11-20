import pytest
from unittest.mock import MagicMock, patch, call
import json
from datetime import date, timedelta
from app.services import ai_tuning
from app.db.models import Certificato, Corso, Dipendente

@pytest.fixture
def mock_db_session():
    with patch("app.services.ai_tuning.get_db") as mock_get_db:
        session = MagicMock()
        mock_get_db.return_value = iter([session]) # get_db is a generator
        yield session

@pytest.fixture
def sample_certificates():
    dip = Dipendente(matricola="123", nome="Mario", cognome="Rossi")
    corso = Corso(categoria_corso="ANTINCENDIO", nome_corso="Antincendio")
    cert = Certificato(
        dipendente=dip,
        corso=corso,
        data_rilascio=date(2023, 1, 1),
        data_scadenza_calcolata=date(2028, 1, 1),
        stato_validazione="MANUAL"
    )
    return [cert]

def test_get_validated_certificates(mock_db_session):
    # Mock the chain: db.query().filter().options().all()
    mock_query = mock_db_session.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_options = mock_filter.options.return_value
    mock_options.all.return_value = ["cert"]

    result = ai_tuning.get_validated_certificates(mock_db_session)
    assert result == ["cert"]

def test_generate_training_data(sample_certificates):
    result = ai_tuning.generate_training_data(sample_certificates)

    assert result # Not empty
    lines = result.split('\n')
    assert len(lines) == 1

    data = json.loads(lines[0])
    assert "input_text" in data
    assert "output_text" in data

    output = json.loads(data["output_text"])
    assert output["nome"] == "Mario Rossi"
    assert output["corso"] == "Antincendio"
    assert output["categoria"] == "ANTINCENDIO"
    assert output["data_rilascio"] == "01/01/2023"

def test_upload_to_gcs():
    with patch("app.services.ai_tuning.storage.Client") as MockClient:
        mock_bucket = MockClient.return_value.bucket.return_value
        mock_blob = mock_bucket.blob.return_value

        uri = ai_tuning.upload_to_gcs("bucket", "data", "blob.jsonl")

        assert uri == "gs://bucket/blob.jsonl"
        mock_blob.upload_from_string.assert_called_with("data")

def test_upload_to_gcs_error():
    with patch("app.services.ai_tuning.storage.Client", side_effect=Exception("GCS Error")):
        with pytest.raises(Exception, match="GCS Error"):
            ai_tuning.upload_to_gcs("bucket", "data", "blob")

def test_start_fine_tuning_job_success(mock_db_session, sample_certificates):
    # We mock get_validated_certificates to return sample data
    # This avoids complex DB mocking and tests the logic of the function itself
    with patch("app.services.ai_tuning.get_validated_certificates", return_value=sample_certificates), \
         patch("app.services.ai_tuning.upload_to_gcs", return_value="gs://bucket/file") as mock_upload, \
         patch("app.services.ai_tuning.aiplatform.init") as mock_init, \
         patch("app.services.ai_tuning.aiplatform.PipelineJob") as MockJob, \
         patch("app.services.ai_tuning.settings") as mock_settings:

        mock_settings.GCS_BUCKET_NAME = "test-bucket"
        mock_settings.GOOGLE_CLOUD_PROJECT = "test-project"

        job_instance = MockJob.return_value
        job_instance.name = "job-123"
        job_instance.resource_name = "projects/123/jobs/456"

        result = ai_tuning.start_fine_tuning_job()

        assert result["job_name"] == "job-123"
        mock_upload.assert_called_once()
        mock_init.assert_called_once()
        job_instance.submit.assert_called_once()

def test_start_fine_tuning_job_no_certs(mock_db_session):
    with patch("app.services.ai_tuning.get_validated_certificates", return_value=[]):
        result = ai_tuning.start_fine_tuning_job()
        assert result == {"message": "No validated certificates found."}
