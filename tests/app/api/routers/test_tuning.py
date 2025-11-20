from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)

def test_start_fine_tuning_success():
    with patch("app.api.routers.tuning.ai_tuning.start_fine_tuning_job") as mock_start:
        mock_start.return_value = {"job_name": "job-1", "job_id": "123"}

        response = client.post("/api/v1/tuning/start-fine-tuning")

        assert response.status_code == 200
        assert response.json() == {"job_name": "job-1", "job_id": "123"}

def test_start_fine_tuning_error():
    with patch("app.api.routers.tuning.ai_tuning.start_fine_tuning_job", side_effect=Exception("Start failed")):
        response = client.post("/api/v1/tuning/start-fine-tuning")

        assert response.status_code == 500
        assert "Start failed" in response.json()["detail"]

def test_get_tuning_status_success():
    with patch("app.api.routers.tuning.aiplatform") as mock_aiplatform, \
         patch("app.api.routers.tuning.settings") as mock_settings:

        mock_settings.GOOGLE_CLOUD_PROJECT = "proj"

        # Mock jobs
        job1 = MagicMock()
        job1.display_name = "fine-tuning-job-1"
        job1.name = "job1"
        job1.state.name = "SUCCEEDED"
        job1.create_time.isoformat.return_value = "2023-01-01"
        job1.end_time.isoformat.return_value = "2023-01-02"

        job2 = MagicMock()
        job2.display_name = "other-job" # Should be filtered out

        mock_aiplatform.PipelineJob.list.return_value = [job1, job2]

        response = client.get("/api/v1/tuning/status")

        assert response.status_code == 200
        jobs = response.json()["tuning_jobs"]
        assert len(jobs) == 1
        assert jobs[0]["job_name"] == "fine-tuning-job-1"
        assert jobs[0]["state"] == "SUCCEEDED"

def test_get_tuning_status_error():
    with patch("app.api.routers.tuning.aiplatform") as mock_aiplatform:
        mock_aiplatform.init.side_effect = Exception("Init error")

        response = client.get("/api/v1/tuning/status")

        assert response.status_code == 500
        assert "Init error" in response.json()["detail"]
