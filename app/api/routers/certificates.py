import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from app.api import deps
from app.db.models import Certificato, User as UserModel
from app.db.session import get_db
from app.schemas.schemas import (
    CertificatoAggiornamentoSchema,
    CertificatoCreazioneSchema,
    CertificatoSchema,
)
from app.services import certificate_logic, certificate_service
from app.utils.audit import log_security_action

router = APIRouter(prefix="/certificati", tags=["certificates"])

DATE_FORMAT_DMY: str = "%d/%m/%Y"


def _build_cert_schema(
    db: Session, cert: Certificato, status_map: dict[int, str] | None = None
) -> CertificatoSchema:
    """Helper to convert Certificato model to CertificatoSchema with calculated fields."""
    if status_map is None:
        status = certificate_logic.get_certificate_status(db, cert)
    else:
        status = status_map.get(int(cert.id), "attivo")

    # Determine employee identification
    if cert.dipendente:
        nome_display = f"{cert.dipendente.cognome} {cert.dipendente.nome}"
        matricola_display = cert.dipendente.matricola
        data_nascita_display = (
            cert.dipendente.data_nascita.strftime(DATE_FORMAT_DMY)
            if cert.dipendente.data_nascita
            else None
        )
    else:
        nome_display = cert.nome_dipendente_raw or "SCONOSCIUTO"
        matricola_display = None
        data_nascita_display = cert.data_nascita_raw

    # Determine failure reason
    fallimento_ragione = None
    if not cert.dipendente:
        fallimento_ragione = "Non trovato in anagrafica (matricola mancante)."

    return CertificatoSchema(
        id=int(cert.id),
        nome=nome_display,
        data_nascita=data_nascita_display,
        matricola=matricola_display,
        corso=cert.corso.nome_corso if cert.corso else "Corso sconosciuto",
        categoria=cert.corso.categoria_corso if cert.corso else "ALTRO",
        data_rilascio=cert.data_rilascio.strftime(DATE_FORMAT_DMY),
        data_scadenza=cert.data_scadenza_calcolata.strftime(DATE_FORMAT_DMY)
        if cert.data_scadenza_calcolata
        else None,
        stato_certificato=status,
        assegnazione_fallita_ragione=fallimento_ragione,
    )


@router.get(
    "/", response_model=list[CertificatoSchema], dependencies=[Depends(deps.verify_license)]
)
def get_certificati(
    db: Annotated[Session, Depends(get_db)], validated: bool | None = Query(None)
) -> Any:
    """Ritorna l'elenco dei certificati, filtrabili per stato validazione."""
    query = db.query(Certificato).options(
        selectinload(Certificato.dipendente), selectinload(Certificato.corso)
    )

    if validated is not None:
        from app.db.models import ValidationStatus

        if validated:
            query = query.filter(Certificato.stato_validazione == ValidationStatus.MANUAL)
        else:
            # Unvalidated = AUTOMATIC OR Orphaned (missing dipendente_id)
            query = query.filter(
                or_(
                    Certificato.stato_validazione == ValidationStatus.AUTOMATIC,
                    Certificato.dipendente_id.is_(None),
                )
            )

    certs = query.all()
    status_map = certificate_logic.get_bulk_certificate_statuses(db, list(certs))

    return [_build_cert_schema(db, c, status_map) for c in certs]


@router.get("/{certificato_id}", response_model=CertificatoSchema)
def get_certificato(
    certificato_id: int,
    db: Annotated[Session, Depends(get_db)],
    license_ok: Annotated[bool, Depends(deps.verify_license)],
) -> Any:
    """Ritorna i dettagli di un singolo certificato."""
    db_cert = db.get(Certificato, certificato_id)
    if not db_cert:
        raise HTTPException(status_code=404, detail="Certificato non trovato")
    return _build_cert_schema(db, db_cert)


@router.post(
    "/",
    response_model=CertificatoSchema,
    dependencies=[Depends(deps.check_write_permission), Depends(deps.verify_license)],
)
def create_certificato(
    certificato: CertificatoCreazioneSchema,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> Any:
    """Crea un nuovo certificato."""
    certificate_service.validate_cert_input(certificato)

    # Business Logic: Get or Create Course
    course = certificate_service.get_or_create_course(db, certificato.categoria, certificato.corso)

    # Check for duplicates
    if certificate_service.check_duplicate_cert(
        db, course.id, certificato.data_rilascio, certificato.dipendente_id, certificato.nome
    ):
        raise HTTPException(
            status_code=409, detail="Certificato già presente a sistema (esiste già)."
        )

    from app.db.models import ValidationStatus
    from app.utils.date_parser import parse_date_flexible

    data_rilascio_dt = parse_date_flexible(certificato.data_rilascio)
    data_scadenza_dt = (
        parse_date_flexible(certificato.data_scadenza) if certificato.data_scadenza else None
    )

    new_cert = Certificato(
        dipendente_id=certificato.dipendente_id,
        corso_id=course.id,
        data_rilascio=data_rilascio_dt,
        data_scadenza_calcolata=data_scadenza_dt,
        stato_validazione=ValidationStatus.MANUAL,
        nome_dipendente_raw=certificato.nome,
        data_nascita_raw=certificato.data_nascita,
    )

    # Resolve employee link (essential for homonyms)
    from app.services import matcher

    matcher.match_certificate_to_employee(db, new_cert)

    try:
        db.add(new_cert)
        db.commit()
        db.refresh(new_cert)
    except Exception as e:
        db.rollback()
        logging.error(f"Error creating certificate: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e

    certificate_service.archive_obsolete_certs(db, new_cert)

    log_security_action(
        db,
        current_user,
        "CERT_CREATE",
        f"Creato certificato ID {new_cert.id} per {certificato.nome}",
        category="DATA",
    )
    return _build_cert_schema(db, new_cert)


@router.put(
    "/{certificato_id}",
    response_model=CertificatoSchema,
    dependencies=[Depends(deps.check_write_permission), Depends(deps.verify_license)],
)
def update_certificato(
    certificato_id: int,
    certificato: CertificatoAggiornamentoSchema,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> Any:
    """Aggiorna un certificato esistente."""
    db_cert = db.get(Certificato, certificato_id)
    if not db_cert:
        raise HTTPException(status_code=404, detail="Certificato non trovato")

    # Keep old data for FS sync
    old_cert_data = certificate_service.get_orphan_cert_data(db_cert)

    # Validate category exists if provided
    if certificato.categoria:
        from app.db.models import Corso

        exists = db.query(Corso).filter(Corso.categoria_corso == certificato.categoria).first()
        if not exists:
            raise HTTPException(
                status_code=404, detail=f"Categoria '{certificato.categoria}' non trovata"
            )

    # Update fields
    update_data = certificato.model_dump(exclude_unset=True)
    certificate_service.update_cert_fields(db_cert, update_data, db)

    try:
        db.commit()
        db.refresh(db_cert)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}") from e

    certificate_service.sync_cert_file_system(db_cert, old_cert_data, db)

    log_security_action(
        db,
        current_user,
        "CERT_UPDATE",
        f"Aggiornato certificato ID {certificato_id}",
        category="DATA",
    )
    return _build_cert_schema(db, db_cert)


@router.put(
    "/{certificato_id}/valida",
    response_model=CertificatoSchema,
    dependencies=[Depends(deps.check_write_permission), Depends(deps.verify_license)],
)
def valida_certificato(
    certificato_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> Any:
    """Valida manualmente un certificato."""
    db_cert = db.get(Certificato, certificato_id)
    if not db_cert:
        raise HTTPException(status_code=404, detail="Certificato non trovato")

    from app.db.models import ValidationStatus

    db_cert.stato_validazione = ValidationStatus.MANUAL
    db.commit()
    db.refresh(db_cert)

    log_security_action(
        db,
        current_user,
        "CERT_VALIDATE",
        f"Validato certificato ID {certificato_id}",
        category="DATA",
    )
    return _build_cert_schema(db, db_cert)


@router.delete(
    "/{certificato_id}",
    dependencies=[Depends(deps.check_write_permission), Depends(deps.verify_license)],
)
def delete_certificato(
    certificato_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> Any:
    """Elimina un certificato."""
    db_cert = db.get(Certificato, certificato_id)
    if not db_cert:
        raise HTTPException(status_code=404, detail="Certificato non trovato")

    # Use service logic to archive file and delete from DB
    certificate_service.delete_certificato_logic(db, db_cert)

    log_security_action(
        db,
        current_user,
        "CERT_DELETE",
        f"Eliminato certificato ID {certificato_id}",
        category="DATA",
    )
    return {"message": "Certificato eliminato con successo"}
