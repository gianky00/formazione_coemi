from typing import Annotated, Any
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api import deps
from app.core.config import settings
from app.db.session import get_db
from app.db.models import User as UserModel
from app.schemas import (
    DipendenteCreateSchema,
    DipendenteDetailSchema,
    DipendenteSchema,
    DipendenteUpdateSchema,
)
from app.services.employee_service import EmployeeService
from app.utils.audit import log_security_action
from app.utils.file_security import verify_file_signature

router = APIRouter(prefix="/dipendenti", tags=["employees"])

def get_employee_service(db: Annotated[Session, Depends(get_db)]) -> EmployeeService:
    return EmployeeService(db)

@router.get("", response_model=list[DipendenteSchema])
def get_dipendenti(
    service: Annotated[EmployeeService, Depends(get_employee_service)],
    license_ok: Annotated[bool, Depends(deps.verify_license)],
) -> Any:
    """Ritorna l'elenco di tutti i dipendenti."""
    return service.get_all()


@router.get("/{dipendente_id}", response_model=DipendenteDetailSchema)
def get_dipendente_detail(
    dipendente_id: int,
    service: Annotated[EmployeeService, Depends(get_employee_service)],
    license_ok: Annotated[bool, Depends(deps.verify_license)],
) -> Any:
    """Ritorna i dettagli di un singolo dipendente."""
    return service.get_detail(dipendente_id)


@router.post(
    "",
    response_model=DipendenteSchema,
    dependencies=[Depends(deps.check_write_permission), Depends(deps.verify_license)],
)
def create_dipendente(
    dipendente: DipendenteCreateSchema,
    service: Annotated[EmployeeService, Depends(get_employee_service)],
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> Any:
    """Crea un nuovo dipendente."""
    new_dip = service.create(dipendente)
    log_security_action(
        service.db, current_user, "DIPENDENTE_CREATE",
        f"Creato dipendente {new_dip.cognome} {new_dip.nome}", category="DATA"
    )
    return new_dip


@router.put(
    "/{dipendente_id}",
    response_model=DipendenteSchema,
    dependencies=[Depends(deps.check_write_permission), Depends(deps.verify_license)],
)
def update_dipendente(
    dipendente_id: int,
    dipendente_data: DipendenteUpdateSchema,
    service: Annotated[EmployeeService, Depends(get_employee_service)],
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> Any:
    """Aggiorna i dati di un dipendente."""
    updated = service.update(dipendente_id, dipendente_data)
    log_security_action(
        service.db, current_user, "DIPENDENTE_UPDATE",
        f"Aggiornato dipendente ID {dipendente_id}", category="DATA"
    )
    return updated


@router.delete(
    "/{dipendente_id}",
    dependencies=[Depends(deps.check_write_permission), Depends(deps.verify_license)],
)
def delete_dipendente(
    dipendente_id: int,
    service: Annotated[EmployeeService, Depends(get_employee_service)],
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> Any:
    """Elimina un dipendente dal sistema."""
    service.delete(dipendente_id)
    log_security_action(
        service.db, current_user, "DIPENDENTE_DELETE",
        f"Eliminato dipendente ID {dipendente_id}", category="DATA"
    )
    return {"message": "Dipendente eliminato con successo"}


@router.post(
    "/import-csv", dependencies=[Depends(deps.check_write_permission), Depends(deps.verify_license)]
)
async def import_dipendenti_csv(
    service: Annotated[EmployeeService, Depends(get_employee_service)],
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
    file: UploadFile = File(...),
) -> Any:
    """Importa dipendenti da un file CSV."""
    if not file.filename or not str(file.filename).endswith(".csv"):
        raise HTTPException(status_code=400, detail="Il file deve essere in formato CSV.")

    content = await file.read()
    if len(content) > settings.MAX_CSV_SIZE:
        raise HTTPException(status_code=413, detail="File troppo grande.")

    if not verify_file_signature(content, "csv"):
        raise HTTPException(status_code=400, detail="Contenuto file non valido.")

    result = service.import_csv(content)
    
    log_security_action(
        service.db, current_user, "DIPENDENTE_IMPORT",
        f"Importato CSV: {file.filename}. Orfani collegati: {result['linked_count']}", category="DATA"
    )

    return {
        "message": f"Importazione completata. {result['linked_count']} orfani collegati.",
        "warnings": result["warnings"],
    }
