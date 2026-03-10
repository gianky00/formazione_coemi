import csv
import io
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session, selectinload

from app.db.models import Certificato, Dipendente
from app.schemas import (
    CertificatoSchema,
    DipendenteCreateSchema,
    DipendenteDetailSchema,
    DipendenteUpdateSchema,
)
from app.services import certificate_logic, matcher, sync_service
from app.utils.date_parser import parse_date_flexible

DATE_FORMAT_DMY: str = "%d/%m/%Y"


class EmployeeService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Dipendente]:
        """Ritorna l'elenco di tutti i dipendenti."""
        return self.db.query(Dipendente).all()

    def get_by_id(self, dipendente_id: int) -> Dipendente | None:
        """Ritorna un dipendente per ID."""
        return self.db.get(Dipendente, dipendente_id)

    def get_detail(self, dipendente_id: int) -> DipendenteDetailSchema:
        """Ritorna i dettagli di un dipendente inclusi i certificati con stato calcolato."""
        dipendente = (
            self.db.query(Dipendente)
            .options(selectinload(Dipendente.certificati).selectinload(Certificato.corso))
            .filter(Dipendente.id == dipendente_id)
            .first()
        )

        if not dipendente:
            raise HTTPException(status_code=404, detail="Dipendente non trovato")

        # Calcolo stato per tutti i certificati
        status_map = certificate_logic.get_bulk_certificate_statuses(
            self.db, list(dipendente.certificati)
        )

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

    def create(self, data: DipendenteCreateSchema) -> Dipendente:
        """Crea un nuovo dipendente con validazioni."""
        if data.matricola:
            if not data.matricola.strip():
                raise HTTPException(status_code=400, detail="La matricola non può essere vuota.")
            if self.db.query(Dipendente).filter(Dipendente.matricola == data.matricola).first():
                raise HTTPException(status_code=400, detail="Matricola già esistente.")

        if data.email and self.db.query(Dipendente).filter(Dipendente.email == data.email).first():
            raise HTTPException(status_code=400, detail="Email già esistente.")

        new_dipendente = Dipendente(**data.model_dump())
        self.db.add(new_dipendente)
        self.db.commit()
        self.db.refresh(new_dipendente)

        # Link potential orphan certificates
        sync_service.link_orphaned_certificates(self.db, new_dipendente)
        self.db.commit()
        return new_dipendente

    def update(self, dipendente_id: int, data: DipendenteUpdateSchema) -> Dipendente:
        """Aggiorna un dipendente esistente."""
        dipendente = self.get_by_id(dipendente_id)
        if not dipendente:
            raise HTTPException(status_code=404, detail="Dipendente non trovato")

        update_dict = data.model_dump(exclude_unset=True)
        self._validate_unique_constraints(dipendente, update_dict)

        for key, value in update_dict.items():
            setattr(dipendente, key, value)

        self.db.commit()
        self.db.refresh(dipendente)

        # Re-link certificates if name changed
        sync_service.link_orphaned_certificates(self.db, dipendente)
        self.db.commit()
        return dipendente

    def delete(self, dipendente_id: int) -> None:
        """Elimina un dipendente."""
        dipendente = self.get_by_id(dipendente_id)
        if not dipendente:
            raise HTTPException(status_code=404, detail="Dipendente non trovato")
        self.db.delete(dipendente)
        self.db.commit()

    def import_csv(self, content: bytes) -> dict[str, Any]:
        """Importa dipendenti da contenuto CSV."""
        try:
            decoded = content.decode("utf-8-sig")
        except UnicodeDecodeError:
            decoded = content.decode("iso-8859-1")

        stream = io.StringIO(decoded)
        reader = csv.DictReader(stream, delimiter=";")
        warnings: list[str] = []

        for i, row in enumerate(reader):
            self._process_csv_row(row, warnings)
            if (i + 1) % 50 == 0:
                self.db.commit()

        self.db.commit()
        linked_count = self.link_orphaned_certificates_after_import()
        if linked_count > 0:
            self.db.commit()

        return {"linked_count": linked_count, "warnings": warnings}

    def _validate_unique_constraints(
        self, dipendente: Dipendente, update_dict: dict[str, Any]
    ) -> None:
        if (
            "matricola" in update_dict
            and update_dict["matricola"] != dipendente.matricola
            and self.db.query(Dipendente)
            .filter(Dipendente.matricola == update_dict["matricola"])
            .first()
        ):
            raise HTTPException(status_code=400, detail="Matricola già esistente.")
        if (
            "email" in update_dict
            and update_dict["email"] != dipendente.email
            and update_dict["email"]
        ) and self.db.query(Dipendente).filter(Dipendente.email == update_dict["email"]).first():
            raise HTTPException(status_code=400, detail="Email già esistente.")

    def _process_csv_row(self, row: dict[str, Any], warnings: list[str]) -> None:
        nome = (row.get("Nome") or row.get("nome") or "").strip()
        cognome = (row.get("Cognome") or row.get("cognome") or "").strip()
        badge = (
            row.get("Badge") or row.get("Matricola") or row.get("matricola") or ""
        ).strip() or None

        if not nome or not cognome:
            return

        dob = parse_date_flexible(row.get("Data di nascita") or row.get("Data_nascita") or "")
        hiring = parse_date_flexible(
            row.get("Data di assunzione") or row.get("Data_assunzione") or ""
        )

        # Logic to find or create
        match = None
        if dob:
            match = (
                self.db.query(Dipendente)
                .filter(
                    Dipendente.nome.ilike(nome),
                    Dipendente.cognome.ilike(cognome),
                    Dipendente.data_nascita == dob,
                )
                .first()
            )

        if not match and badge:
            match = self.db.query(Dipendente).filter(Dipendente.matricola == badge).first()

        if match:
            match.nome, match.cognome = nome, cognome
            if dob:
                match.data_nascita = dob
            if hiring:
                match.data_assunzione = hiring
            if badge:
                match.matricola = badge
        else:
            self.db.add(
                Dipendente(
                    nome=nome,
                    cognome=cognome,
                    matricola=badge,
                    data_nascita=dob,
                    data_assunzione=hiring,
                )
            )

    def link_orphaned_certificates_after_import(self) -> int:
        from app.services.certificate_service import CertificateService

        cert_service = CertificateService(self.db)
        orphans = self.db.query(Certificato).filter(Certificato.dipendente_id.is_(None)).all()
        linked = 0
        for cert in orphans:
            if not cert.nome_dipendente_raw:
                continue
            dob = parse_date_flexible(cert.data_nascita_raw) if cert.data_nascita_raw else None
            match = matcher.find_employee_by_name(self.db, cert.nome_dipendente_raw, dob)
            if match:
                old_data = cert_service.get_orphan_data(cert)
                cert.dipendente_id = match.id
                linked += 1
                cert_service.sync_file_system(cert, old_data)
        return linked
