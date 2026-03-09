import os
from pathlib import Path
from typing import Any

from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_user_data_dir, settings
from app.db.models import Certificato, Corso, ValidationStatus
from app.schemas import (
    CertificatoAggiornamentoSchema,
    CertificatoCreazioneSchema,
    CertificatoSchema,
)
from app.services import certificate_file_service, certificate_logic, matcher, sync_service
from app.services.document_locator import find_document
from app.utils.date_parser import parse_date_flexible

DATE_FORMAT_DMY: str = "%d/%m/%Y"


class CertificateService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, validated: bool | None = None) -> list[Certificato]:
        """Ritorna l'elenco dei certificati filtrati."""
        query = self.db.query(Certificato).options(
            selectinload(Certificato.dipendente), selectinload(Certificato.corso)
        )

        if validated is not None:
            if validated:
                query = query.filter(Certificato.stato_validazione == ValidationStatus.MANUAL)
            else:
                query = query.filter(
                    or_(
                        Certificato.stato_validazione == ValidationStatus.AUTOMATIC,
                        Certificato.dipendente_id.is_(None),
                    )
                )
        return query.all()

    def get_by_id(self, cert_id: int) -> Certificato | None:
        """Ritorna un certificato per ID."""
        return self.db.get(Certificato, cert_id)

    def create(self, data: CertificatoCreazioneSchema) -> Certificato:
        """Crea un nuovo certificato con logica di business completa."""
        self._validate_input(data)
        course = self._get_or_create_course(data.categoria, data.corso)

        if self._check_duplicate(course.id, data.data_rilascio, data.dipendente_id, data.nome):
            raise HTTPException(status_code=409, detail="Certificato già presente")

        new_cert = Certificato(
            dipendente_id=data.dipendente_id,
            corso_id=course.id,
            data_rilascio=parse_date_flexible(data.data_rilascio),
            data_scadenza_calcolata=parse_date_flexible(data.data_scadenza)
            if data.data_scadenza
            else None,
            stato_validazione=ValidationStatus.MANUAL,
            nome_dipendente_raw=data.nome,
            data_nascita_raw=data.data_nascita,
        )

        matcher.match_certificate_to_employee(self.db, new_cert)

        try:
            self.db.add(new_cert)
            self.db.commit()
            self.db.refresh(new_cert)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e)) from e

        self._archive_obsolete(new_cert)
        self._try_link_file(new_cert, data)

        return new_cert

    def update(self, cert_id: int, data: CertificatoAggiornamentoSchema) -> Certificato:
        """Aggiorna un certificato e sincronizza il file system."""
        cert = self.get_by_id(cert_id)
        if not cert:
            raise HTTPException(status_code=404, detail="Certificato non trovato")

        old_data = self.get_orphan_data(cert)

        # Update fields
        update_dict = data.model_dump(exclude_unset=True)
        self._update_fields(cert, update_dict)

        try:
            self.db.commit()
            self.db.refresh(cert)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e)) from e

        self.sync_file_system(cert, old_data)
        return cert

    def validate(self, cert_id: int) -> Certificato:
        """Valida manualmente un certificato."""
        cert = self.get_by_id(cert_id)
        if not cert:
            raise HTTPException(status_code=404, detail="Certificato non trovato")
        cert.stato_validazione = ValidationStatus.MANUAL
        self.db.commit()
        return cert

    def delete(self, cert_id: int) -> None:
        """Elimina certificato e archivia il file."""
        cert = self.get_by_id(cert_id)
        if not cert:
            raise HTTPException(status_code=404, detail="Certificato non trovato")

        sync_service.archive_certificate_file(self.db, cert)
        self.db.delete(cert)
        self.db.commit()

    def build_schema(self, cert: Certificato, status_map: dict[int, str] | None = None) -> CertificatoSchema:
        """Helper per trasformare il modello in schema."""
        status = (
            status_map.get(int(cert.id), "attivo")
            if status_map
            else certificate_logic.get_certificate_status(self.db, cert)
        )

        if cert.dipendente:
            nome = f"{cert.dipendente.cognome} {cert.dipendente.nome}"
            matr = cert.dipendente.matricola
            dob = (
                cert.dipendente.data_nascita.strftime(DATE_FORMAT_DMY)
                if cert.dipendente.data_nascita
                else None
            )
        else:
            nome = cert.nome_dipendente_raw or "SCONOSCIUTO"
            matr = None
            dob = cert.data_nascita_raw

        return CertificatoSchema(
            id=int(cert.id),
            nome=nome,
            data_nascita=dob,
            matricola=matr,
            corso=cert.corso.nome_corso if cert.corso else "N/D",
            categoria=cert.corso.categoria_corso if cert.corso else "ALTRO",
            data_rilascio=cert.data_rilascio.strftime(DATE_FORMAT_DMY),
            data_scadenza=cert.data_scadenza_calcolata.strftime(DATE_FORMAT_DMY)
            if cert.data_scadenza_calcolata
            else None,
            stato_certificato=status,
            assegnazione_fallita_ragione=None
            if cert.dipendente
            else "Mancata associazione anagrafica",
        )

    def get_orphan_data(self, cert: Certificato) -> dict[str, Any]:
        return {
            "nome": f"{cert.dipendente.cognome} {cert.dipendente.nome}"
            if cert.dipendente
            else cert.nome_dipendente_raw,
            "matricola": cert.dipendente.matricola if cert.dipendente else None,
            "categoria": cert.corso.categoria_corso if cert.corso else None,
            "data_scadenza": cert.data_scadenza_calcolata.strftime(DATE_FORMAT_DMY)
            if cert.data_scadenza_calcolata
            else None,
        }

    def sync_file_system(self, cert: Certificato, old_data: dict[str, Any]) -> None:
        new_data = self.get_orphan_data(cert)
        if old_data == new_data:
            return

        db_path = settings.DOCUMENTS_FOLDER or str(get_user_data_dir())
        old_path = find_document(db_path, old_data) or cert.file_path

        if old_path and os.path.exists(old_path):
            status = certificate_logic.get_certificate_status(self.db, cert)
            certificate_file_service.handle_file_rename(Path(db_path), status, old_path, new_data)

    # --- Internal Helpers ---
    def _validate_input(self, data: Any) -> None:
        if not data.nome or not data.corso or not data.categoria or not data.data_rilascio:
            raise HTTPException(status_code=400, detail="Dati obbligatori mancanti.")

    def _get_or_create_course(self, cat: str, name: str) -> Corso:
        course = (
            self.db.query(Corso)
            .filter(Corso.nome_corso.ilike(name), Corso.categoria_corso.ilike(cat))
            .first()
        )
        if not course:
            course = Corso(nome_corso=name, categoria_corso=cat, validita_mesi=0)
            self.db.add(course)
            self.db.commit()
            self.db.refresh(course)
        return course

    def _check_duplicate(self, course_id: int, rilascio: Any, dip_id: int | None, nome: str | None) -> bool:
        dt = parse_date_flexible(str(rilascio))
        query = self.db.query(Certificato).filter(
            Certificato.corso_id == course_id, Certificato.data_rilascio == dt
        )
        if dip_id:
            query = query.filter(Certificato.dipendente_id == dip_id)
        else:
            query = query.filter(Certificato.nome_dipendente_raw == nome)
        return query.first() is not None

    def _archive_obsolete(self, cert: Certificato) -> None:
        if not cert.dipendente_id or not cert.corso:
            return
        older = (
            self.db.query(Certificato)
            .join(Corso)
            .filter(
                Certificato.dipendente_id == cert.dipendente_id,
                Corso.categoria_corso == cert.corso.categoria_corso,
                Certificato.id != cert.id,
                Certificato.data_rilascio < cert.data_rilascio,
            )
            .all()
        )
        for o in older:
            sync_service.archive_certificate_file(self.db, o)

    def _try_link_file(self, cert: Certificato, data: Any) -> None:
        db_path = settings.DOCUMENTS_FOLDER or str(get_user_data_dir())
        f_data = {
            "nome": data.nome,
            "matricola": cert.dipendente.matricola if cert.dipendente else None,
            "categoria": data.categoria,
            "data_scadenza": cert.data_scadenza_calcolata.strftime(DATE_FORMAT_DMY)
            if cert.data_scadenza_calcolata
            else None,
        }
        found = find_document(db_path, f_data)
        if found:
            cert.file_path = found
            self.db.commit()

    def _update_fields(self, cert: Certificato, data: dict[str, Any]) -> None:
        if "nome" in data: cert.nome_dipendente_raw = data["nome"]
        if "data_nascita" in data: cert.data_nascita_raw = data["data_nascita"]
        if "corso" in data or "categoria" in data:
            cat = data.get("categoria", cert.corso.categoria_corso if cert.corso else "ALTRO")
            name = data.get("corso", cert.corso.nome_corso if cert.corso else "Corso")
            cert.corso_id = self._get_or_create_course(cat, name).id
        if "data_rilascio" in data:
            dt = parse_date_flexible(data["data_rilascio"])
            if dt: cert.data_rilascio = dt

        if "data_scadenza" in data:
            cert.data_scadenza_manuale = parse_date_flexible(data["data_scadenza"])
        certificate_logic.calculate_combined_data(cert)
        matcher.match_certificate_to_employee(self.db, cert)
