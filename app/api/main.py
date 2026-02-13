import logging
from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api import deps
from app.core.config import settings
from app.db.models import Corso
from app.db.session import get_db
from app.services import ai_extraction, certificate_logic
from app.utils.date_parser import parse_date_flexible

router = APIRouter()

DATE_FORMAT_DMY: str = "%d/%m/%Y"


async def _read_file_securely(file: UploadFile, max_size: int) -> bytes:
    """Reads a file while enforcing a size limit to prevent memory exhaustion."""
    content_bytes = bytearray()
    while True:
        chunk = await file.read(1024 * 1024)  # Read in 1MB chunks
        if not chunk:
            break
        content_bytes.extend(chunk)
        if len(content_bytes) > max_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size allowed is {max_size // (1024 * 1024)}MB.",
            )
    return bytes(content_bytes)


def _normalize_extracted_dates(extracted_data: dict[str, Any]) -> None:
    """Standardizes date formats in the AI-extracted data."""
    for key in ["data_nascita", "data_rilascio", "data_scadenza"]:
        val = extracted_data.get(key)
        if not val or str(val).lower() == "none":
            extracted_data[key] = None
            continue

        try:
            parsed_date = parse_date_flexible(str(val))
            if parsed_date:
                extracted_data[key] = parsed_date.strftime(DATE_FORMAT_DMY)
        except Exception:
            extracted_data[key] = None


def _infer_expiration_date(db: Session, extracted_data: dict[str, Any]) -> None:
    """Attempts to calculate the expiration date if missing."""
    if extracted_data.get("data_scadenza") or not extracted_data.get("data_rilascio"):
        return

    try:
        corso_nome = str(extracted_data.get("corso") or "")
        categoria = str(extracted_data.get("categoria") or "")

        # Try to find a matching course to get its validity
        course = (
            db.query(Corso)
            .filter(Corso.nome_corso.ilike(f"%{corso_nome}%"))
            .filter(Corso.categoria_corso.ilike(f"%{categoria}%"))
            .first()
        )

        if course and course.validita_mesi > 0:
            rilascio = datetime.strptime(
                str(extracted_data["data_rilascio"]), DATE_FORMAT_DMY
            ).date()
            scadenza = certificate_logic.calculate_expiration_date(rilascio, course.validita_mesi)
            if scadenza:
                extracted_data["data_scadenza"] = scadenza.strftime(DATE_FORMAT_DMY)
    except Exception:
        pass


@router.post(
    "/upload-pdf",
    response_model=dict[str, Any],
    dependencies=[Depends(deps.verify_license)],
    tags=["Certificates"],
)
async def upload_pdf(
    db: Annotated[Session, Depends(get_db)],
    file: UploadFile = File(...),
) -> Any:
    """Legacy endpoint for PDF upload, with data normalization and inference."""
    pdf_bytes = await _read_file_securely(file, settings.MAX_UPLOAD_SIZE)

    try:
        extracted_data = ai_extraction.extract_entities_with_ai(pdf_bytes)

        if "error" in extracted_data:
            return extracted_data

        # Data normalization
        _normalize_extracted_dates(extracted_data)
        _infer_expiration_date(db, extracted_data)

        return extracted_data

    except Exception as e:
        logging.error(f"AI extraction failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Errore durante l'estrazione dati: {e!s}"
        ) from e


@router.get("/")
def read_root() -> dict[str, str]:
    """Base API health check."""
    return {"status": "ok", "message": "Intelleo API v1 ready"}
