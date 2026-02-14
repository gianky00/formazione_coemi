from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.models import Certificato, Dipendente
from app.services import matcher
from app.utils.date_parser import parse_date_flexible


def validate_unique_constraints(
    db: Session, dipendente: Dipendente, update_dict: dict[str, Any]
) -> None:
    """Checks for duplicate matricola or email before update."""
    if "matricola" in update_dict and update_dict["matricola"] != dipendente.matricola:
        mat = str(update_dict["matricola"])
        if not mat or not mat.strip():
            raise HTTPException(
                status_code=400, detail="La matricola non può essere vuota o solo spazi."
            )
        existing = db.query(Dipendente).filter(Dipendente.matricola == mat).first()
        if existing:
            raise HTTPException(status_code=400, detail="Matricola già esistente.")

        if (
            "email" in update_dict
            and update_dict["email"] != dipendente.email
            and update_dict["email"]
        ):
            existing_email = (
                db.query(Dipendente).filter(Dipendente.email == update_dict["email"]).first()
            )
            if existing_email:
                raise HTTPException(status_code=400, detail="Email già esistente.")


def handle_new_dipendente(db: Session, warnings: list[str], data: tuple[Any, ...]) -> None:
    """Helper to handle new or ambiguous employee logic during CSV import."""
    cognome, nome, parsed_data_nascita, badge, parsed_data_assunzione, _data_nascita_str = data

    found_by_identity = False
    if parsed_data_nascita:
        matches = (
            db.query(Dipendente)
            .filter(
                Dipendente.nome.ilike(nome),
                Dipendente.cognome.ilike(cognome),
                Dipendente.data_nascita == parsed_data_nascita,
            )
            .all()
        )
        if matches:
            found_by_identity = True
            if len(matches) > 1:
                warnings.append(
                    f"Ambiguità trovata per {cognome} {nome}: più dipendenti con stessa data nascita. Salto aggiornamento matricola."
                )
            else:
                m = matches[0]
                # Update matricola if different or missing
                if badge and m.matricola != badge:
                    old_badge = m.matricola
                    m.matricola = badge
                    warnings.append(
                        f"Aggiornata matricola per {cognome} {nome}: {old_badge} -> {badge}"
                    )
                # Update hiring date if missing
                if parsed_data_assunzione and not m.data_assunzione:
                    m.data_assunzione = parsed_data_assunzione

    if not found_by_identity and badge:
        existing = db.query(Dipendente).filter(Dipendente.matricola == badge).first()
        if existing:
            # Update existing with CSV data (Master Identity Update)
            existing.nome = nome
            existing.cognome = cognome
            if parsed_data_nascita:
                existing.data_nascita = parsed_data_nascita
            if parsed_data_assunzione:
                existing.data_assunzione = parsed_data_assunzione
            return

    if not found_by_identity:
        new_dip = Dipendente(
            nome=nome,
            cognome=cognome,
            matricola=badge,
            data_nascita=parsed_data_nascita,
            data_assunzione=parsed_data_assunzione,
        )
        db.add(new_dip)


def process_csv_row(row: dict[str, Any], db: Session, warnings: list[str]) -> None:
    """Processes a single row from the employees CSV."""
    # Handle variations in header names (underscore vs space)
    nome = (row.get("Nome") or row.get("nome") or "").strip()
    cognome = (row.get("Cognome") or row.get("cognome") or "").strip()
    badge = (
        row.get("Badge") or row.get("badge") or row.get("Matricola") or row.get("matricola") or ""
    ).strip() or None

    data_nascita_str = (row.get("Data di nascita") or row.get("Data_nascita") or "").strip()
    data_assunzione_str = (
        row.get("Data di assunzione") or row.get("Data_assunzione") or ""
    ).strip()

    if not nome or not cognome:
        return

    parsed_data_nascita = parse_date_flexible(data_nascita_str) if data_nascita_str else None
    parsed_data_assunzione = (
        parse_date_flexible(data_assunzione_str) if data_assunzione_str else None
    )

    handle_new_dipendente(
        db,
        warnings,
        (cognome, nome, parsed_data_nascita, badge, parsed_data_assunzione, data_nascita_str),
    )


def link_orphaned_certificates_after_import(db: Session) -> int:
    """Re-links orphaned certificates after a bulk employee import and syncs files."""
    from app.services import certificate_service

    orphans = db.query(Certificato).filter(Certificato.dipendente_id.is_(None)).all()
    linked_count = 0
    for cert in orphans:
        if not cert.nome_dipendente_raw:
            continue
        dob = parse_date_flexible(cert.data_nascita_raw) if cert.data_nascita_raw else None
        match = matcher.find_employee_by_name(db, cert.nome_dipendente_raw, dob)
        if match:
            # Capture old state for FS sync
            old_cert_data = certificate_service.get_orphan_cert_data(cert)
            cert.dipendente_id = match.id
            linked_count += 1
            # Sync file system immediately
            certificate_service.sync_cert_file_system(cert, old_cert_data, db)
    return linked_count
