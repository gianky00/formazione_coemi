import csv
import io
from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.api import deps
from app.core.config import settings
from app.db.models import Certificato, Dipendente, User as UserModel
from app.db.session import get_db
from app.schemas.schemas import (
    CertificatoSchema,
    DipendenteCreateSchema,
    DipendenteDetailSchema,
    DipendenteSchema,
    DipendenteUpdateSchema,
)
from app.services import certificate_logic, employee_service
from app.services.sync_service import link_orphaned_certificates
from app.utils.audit import log_security_action
from app.utils.file_security import verify_file_signature

router = APIRouter(prefix="/dipendenti", tags=["employees"])

DATE_FORMAT_DMY: str = "%d/%m/%Y"
STR_DIP_NON_TROVATO: str = "Dipendente non trovato"


@router.get("", response_model=list[DipendenteSchema])
def get_dipendenti(
    db: Annotated[Session, Depends(get_db)],
    license_ok: Annotated[bool, Depends(deps.verify_license)],
) -> Any:
    """Ritorna l'elenco di tutti i dipendenti."""
    return db.query(Dipendente).all()


@router.get("/{dipendente_id}", response_model=DipendenteDetailSchema)
def get_dipendente_detail(
    dipendente_id: int,
    db: Annotated[Session, Depends(get_db)],
    license_ok: Annotated[bool, Depends(deps.verify_license)],
) -> Any:
    """Ritorna i dettagli di un singolo dipendente, inclusi i certificati con relativo stato."""
    dipendente = (
        db.query(Dipendente)
        .options(selectinload(Dipendente.certificati).selectinload(Certificato.corso))
        .filter(Dipendente.id == dipendente_id)
        .first()
    )

    if not dipendente:
        raise HTTPException(status_code=404, detail=STR_DIP_NON_TROVATO)

    # Calcolo stato per tutti i certificati
    status_map = certificate_logic.get_bulk_certificate_statuses(db, list(dipendente.certificati))

    cert_schemas = []
    for cert in dipendente.certificati:
        if not cert.corso:
            continue

        status = status_map.get(int(cert.id), "attivo")

        cert_schemas.append(
            CertificatoSchema(
                id=int(cert.id),
                nome=f"{dipendente.cognome} {dipendente.nome}",
                data_nascita=dipendente.data_nascita.strftime(DATE_FORMAT_DMY)
                if dipendente.data_nascita
                else None,
                matricola=dipendente.matricola,
                corso=cert.corso.nome_corso,
                categoria=cert.corso.categoria_corso or "General",
                data_rilascio=cert.data_rilascio.strftime(DATE_FORMAT_DMY),
                data_scadenza=cert.data_scadenza_calcolata.strftime(DATE_FORMAT_DMY)
                if cert.data_scadenza_calcolata
                else None,
                stato_certificato=status,
            )
        )

    return DipendenteDetailSchema(
        id=int(dipendente.id),
        matricola=dipendente.matricola,
        nome=dipendente.nome,
        cognome=dipendente.cognome,
        data_nascita=dipendente.data_nascita,
        email=dipendente.email,
        categoria_reparto=dipendente.categoria_reparto,
        data_assunzione=dipendente.data_assunzione,
        certificati=cert_schemas,
    )


@router.post(
    "",
    response_model=DipendenteSchema,
    dependencies=[Depends(deps.check_write_permission), Depends(deps.verify_license)],
)
def create_dipendente(
    dipendente: DipendenteCreateSchema,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> Any:
    """Crea un nuovo dipendente e tenta di collegare certificati orfani."""
    if dipendente.matricola:
        if not dipendente.matricola.strip():
            raise HTTPException(status_code=400, detail="La matricola non può essere vuota.")
        existing = db.query(Dipendente).filter(Dipendente.matricola == dipendente.matricola).first()
        if existing:
            raise HTTPException(status_code=400, detail="Matricola già esistente.")

    if dipendente.email:
        existing_email = db.query(Dipendente).filter(Dipendente.email == dipendente.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email già esistente.")

    new_dipendente = Dipendente(
        matricola=dipendente.matricola,
        nome=dipendente.nome,
        cognome=dipendente.cognome,
        data_nascita=dipendente.data_nascita,
        email=dipendente.email,
        mansione=dipendente.mansione,
        categoria_reparto=dipendente.categoria_reparto,
        data_assunzione=dipendente.data_assunzione,
    )
    db.add(new_dipendente)
    db.commit()
    db.refresh(new_dipendente)

    # Link potential orphan certificates
    link_orphaned_certificates(db, new_dipendente)
    db.commit()

    log_security_action(
        db,
        current_user,
        "DIPENDENTE_CREATE",
        f"Creato dipendente {dipendente.cognome} {dipendente.nome}",
        category="DATA",
    )
    return new_dipendente


@router.put(
    "/{dipendente_id}",
    response_model=DipendenteSchema,
    dependencies=[Depends(deps.check_write_permission), Depends(deps.verify_license)],
)
def update_dipendente(
    dipendente_id: int,
    dipendente_data: DipendenteUpdateSchema,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> Any:
    """Aggiorna i dati di un dipendente e ricollega certificati orfani se necessario."""
    dipendente = db.get(Dipendente, dipendente_id)
    if not dipendente:
        raise HTTPException(status_code=404, detail=STR_DIP_NON_TROVATO)

    update_dict = dipendente_data.model_dump(exclude_unset=True)
    employee_service.validate_unique_constraints(db, dipendente, update_dict)

    for key, value in update_dict.items():
        setattr(dipendente, key, value)

    db.commit()
    db.refresh(dipendente)

    # Link potential orphan certificates (if name changed)
    link_orphaned_certificates(db, dipendente)
    db.commit()

    log_security_action(
        db,
        current_user,
        "DIPENDENTE_UPDATE",
        f"Aggiornato dipendente ID {dipendente_id}",
        category="DATA",
    )
    return dipendente


@router.delete(
    "/{dipendente_id}",
    dependencies=[Depends(deps.check_write_permission), Depends(deps.verify_license)],
)
def delete_dipendente(
    dipendente_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> Any:
    """Elimina un dipendente dal sistema."""
    dipendente = db.get(Dipendente, dipendente_id)
    if not dipendente:
        raise HTTPException(status_code=404, detail=STR_DIP_NON_TROVATO)

    log_details = (
        f"Eliminato dipendente {dipendente.cognome} {dipendente.nome} (ID {dipendente_id})"
    )
    db.delete(dipendente)
    db.commit()

    log_security_action(db, current_user, "DIPENDENTE_DELETE", log_details, category="DATA")
    return {"message": "Dipendente eliminato con successo"}


@router.post(
    "/import-csv", dependencies=[Depends(deps.check_write_permission), Depends(deps.verify_license)]
)
async def import_dipendenti_csv(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
    file: UploadFile = File(...),
) -> Any:
    """Importa dipendenti da un file CSV e ricollega certificati orfani."""
    max_csv_size = settings.MAX_CSV_SIZE

    content_bytes = bytearray()
    while True:
        chunk = await file.read(1024 * 1024)
        if not chunk:
            break
        content_bytes.extend(chunk)
        if len(content_bytes) > max_csv_size:
            raise HTTPException(
                status_code=413,
                detail=f"File troppo grande. Limite: {max_csv_size // (1024 * 1024)}MB.",
            )

    content = bytes(content_bytes)

    if not file.filename or not str(file.filename).endswith(".csv"):
        raise HTTPException(status_code=400, detail="Il file deve essere un CSV.")

    if not verify_file_signature(content, "csv"):
        raise HTTPException(status_code=400, detail="Contenuto file non valido.")

    decoded_content = content.decode("utf-8", errors="replace")
    stream = io.StringIO(decoded_content)
    reader = csv.DictReader(stream, delimiter=";")

    warnings: list[str] = []
    batch_size = 50
    rows_processed = 0

    try:
        for row in reader:
            employee_service.process_csv_row(row, db, warnings)
            rows_processed += 1
            if rows_processed % batch_size == 0:
                db.commit()
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Errore integrità: {e!s}") from e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore importazione: {e!s}") from e

    linked_count = employee_service.link_orphaned_certificates_after_import(db)
    if linked_count > 0:
        db.commit()

    log_security_action(
        db,
        current_user,
        "DIPENDENTE_CREATE",
        f"Importato CSV: {file.filename}. Orfani collegati: {linked_count}",
        category="DATA",
    )

    return {
        "message": f"Importazione completata. {linked_count} certificati orfani collegati.",
        "warnings": warnings,
    }
