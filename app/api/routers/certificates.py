from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.db.models import User as UserModel
from app.db.session import get_db
from app.schemas import (
    CertificatoAggiornamentoSchema,
    CertificatoCreazioneSchema,
    CertificatoSchema,
)
from app.services.certificate_logic import get_bulk_certificate_statuses
from app.services.certificate_service import CertificateService
from app.utils.audit import log_security_action

router = APIRouter(prefix="/certificati", tags=["certificates"])


def get_cert_service(db: Annotated[Session, Depends(get_db)]) -> CertificateService:
    return CertificateService(db)


@router.get("/", response_model=list[CertificatoSchema])
def get_certificati(
    service: Annotated[CertificateService, Depends(get_cert_service)],
    validated: bool | None = None,
    license_ok: Annotated[bool, Depends(deps.verify_license)] = True,
) -> Any:
    """Ritorna l'elenco dei certificati."""
    certs = service.get_all(validated)
    status_map = get_bulk_certificate_statuses(service.db, certs.copy())
    return [service.build_schema(c, status_map) for c in certs]


@router.get("/{certificato_id}", response_model=CertificatoSchema)
def get_certificato(
    certificato_id: int,
    service: Annotated[CertificateService, Depends(get_cert_service)],
    license_ok: Annotated[bool, Depends(deps.verify_license)] = True,
) -> Any:
    """Ritorna i dettagli di un singolo certificato."""
    cert = service.get_by_id(certificato_id)
    if not cert:
        raise HTTPException(status_code=404, detail="Certificato non trovato")
    return service.build_schema(cert)


@router.post("/", response_model=CertificatoSchema)
def create_certificato(
    certificato: CertificatoCreazioneSchema,
    service: Annotated[CertificateService, Depends(get_cert_service)],
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
    license_ok: Annotated[bool, Depends(deps.verify_license)] = True,
) -> Any:
    """Crea un nuovo certificato."""
    new_cert = service.create(certificato)
    log_security_action(
        service.db,
        current_user,
        "CERT_CREATE",
        f"Creato certificato ID {new_cert.id} per {new_cert.nome_dipendente_raw}",
        category="DATA",
    )
    return service.build_schema(new_cert)


@router.put("/{certificato_id}", response_model=CertificatoSchema)
def update_certificato(
    certificato_id: int,
    certificato_data: CertificatoAggiornamentoSchema,
    service: Annotated[CertificateService, Depends(get_cert_service)],
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
    license_ok: Annotated[bool, Depends(deps.verify_license)] = True,
) -> Any:
    """Aggiorna un certificato esistente."""
    updated = service.update(certificato_id, certificato_data)
    log_security_action(
        service.db,
        current_user,
        "CERT_UPDATE",
        f"Aggiornato certificato ID {certificato_id}",
        category="DATA",
    )
    return service.build_schema(updated)


@router.put("/{certificato_id}/valida", response_model=CertificatoSchema)
def valida_certificato(
    certificato_id: int,
    service: Annotated[CertificateService, Depends(get_cert_service)],
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
    license_ok: Annotated[bool, Depends(deps.verify_license)] = True,
) -> Any:
    """Valida manualmente un certificato."""
    validated = service.validate(certificato_id)
    log_security_action(
        service.db,
        current_user,
        "CERT_VALIDATE",
        f"Validato certificato ID {certificato_id}",
        category="DATA",
    )
    return service.build_schema(validated)


@router.delete("/{certificato_id}")
def delete_certificato(
    certificato_id: int,
    service: Annotated[CertificateService, Depends(get_cert_service)],
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
    license_ok: Annotated[bool, Depends(deps.verify_license)] = True,
) -> Any:
    """Elimina un certificato."""
    service.delete(certificato_id)
    log_security_action(
        service.db,
        current_user,
        "CERT_DELETE",
        f"Eliminato certificato ID {certificato_id}",
        category="DATA",
    )
    return {"message": "Certificato eliminato con successo"}
