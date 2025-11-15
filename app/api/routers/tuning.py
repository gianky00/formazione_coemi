from fastapi import APIRouter, HTTPException
from app.services import ai_tuning
import logging
from google.cloud import aiplatform
from app.core.config import settings

router = APIRouter()

@router.post("/start-fine-tuning")
def start_fine_tuning():
    """Starts the fine-tuning job."""
    try:
        result = ai_tuning.start_fine_tuning_job()
        return result
    except Exception as e:
        logging.error(f"Failed to start fine-tuning job: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
def get_tuning_status():
    """Retrieves the status of running and completed tuning jobs."""
    try:
        aiplatform.init(project=settings.GOOGLE_CLOUD_PROJECT, location="europe-west1")
        jobs = aiplatform.PipelineJob.list()

        # Filter for tuning jobs and format the response
        tuning_jobs = [
            {
                "job_name": job.display_name,
                "job_id": job.name,
                "state": job.state.name,
                "create_time": job.create_time.isoformat(),
                "end_time": job.end_time.isoformat() if job.end_time else None
            }
            for job in jobs if "fine-tuning-job" in job.display_name
        ]

        return {"tuning_jobs": tuning_jobs}
    except Exception as e:
        logging.error(f"Failed to get tuning job status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
