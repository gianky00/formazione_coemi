from sqlalchemy.orm import Session
from app.db.models import Corso, User
from app.db.session import SessionLocal
from app.core.security import get_password_hash

def seed_database(db: Session = None):
    """
    Populates the database with a predefined list of master courses and the default admin user.
    """
    if db is None:
        db = SessionLocal()
        close_db = True
    else:
        close_db = False

    try:
        # --- Seed Courses ---
        corsi = [
            {"nome_corso": "ANTINCENDIO", "validita_mesi": 60, "categoria_corso": "ANTINCENDIO"}, # 5 anni
            {"nome_corso": "PRIMO SOCCORSO", "validita_mesi": 36, "categoria_corso": "PRIMO SOCCORSO"}, # 3 anni
            {"nome_corso": "ASPP", "validita_mesi": 60, "categoria_corso": "ASPP"}, # 5 anni
            {"nome_corso": "RSPP", "validita_mesi": 60, "categoria_corso": "RSPP"}, # 5 anni
            {"nome_corso": "ATEX", "validita_mesi": 60, "categoria_corso": "ATEX"}, # 5 anni
            {"nome_corso": "BLSD", "validita_mesi": 12, "categoria_corso": "BLSD"}, # 1 anno
            {"nome_corso": "CARROPONTE", "validita_mesi": 60, "categoria_corso": "CARROPONTE"}, # 5 anni
            {"nome_corso": "DIRETTIVA SEVESO", "validita_mesi": 60, "categoria_corso": "DIRETTiva SEVESO"}, # 5 anni
            {"nome_corso": "DIRIGENTI E FORMATORI", "validita_mesi": 60, "categoria_corso": "DIRIGENTI E FORMATORI"}, # 5 anni
            {"nome_corso": "GRU A TORRE E PONTE", "validita_mesi": 60, "categoria_corso": "GRU A TORRE E PONTE"}, # 5 anni
            {"nome_corso": "H2S", "validita_mesi": 60, "categoria_corso": "H2S"}, # 5 anni
            {"nome_corso": "IMBRACATORE", "validita_mesi": 60, "categoria_corso": "IMBRACATORE"}, # 5 anni
            {"nome_corso": "FORMAZIONE GENERICA ART.37", "validita_mesi": 60, "categoria_corso": "FORMAZIONE GENERICA ART.37"}, # 5 anni
            {"nome_corso": "PREPOSTO", "validita_mesi": 24, "categoria_corso": "PREPOSTO"}, # 2 anni
            {"nome_corso": "GRU SU AUTOCARRO", "validita_mesi": 60, "categoria_corso": "GRU SU AUTOCARRO"}, # 5 anni
            {"nome_corso": "PLE", "validita_mesi": 60, "categoria_corso": "PLE"}, # 5 anni
            {"nome_corso": "L5 PES PAV PEI C CANTIERE", "validita_mesi": 60, "categoria_corso": "L5 PES PAV PEI C CANTIERE"}, # 5 anni
            {"nome_corso": "LAVORI IN QUOTA", "validita_mesi": 60, "categoria_corso": "LAVORI IN QUOTA"}, # 5 anni
            {"nome_corso": "MACCHINE OPERATRICI", "validita_mesi": 60, "categoria_corso": "MACCHINE OPERATRICI"}, # 5 anni
            {"nome_corso": "MANITOU P.ROTATIVE", "validita_mesi": 60, "categoria_corso": "MANITOU P.ROTATIVE"}, # 5 anni
            {"nome_corso": "MEDICO COMPETENTE", "validita_mesi": 0, "categoria_corso": "MEDICO COMPETENTE"}, # Sempre valido
            {"nome_corso": "MULETTO CARRELISTI", "validita_mesi": 60, "categoria_corso": "MULETTO CARRELISTI"}, # 5 anni
            {"nome_corso": "SOPRAVVIVENZA E SALVATAGGIO IN MARE", "validita_mesi": 60, "categoria_corso": "SOPRAVVIVENZA E SALVATAGGIO IN MARE"}, # 5 anni
            {"nome_corso": "SPAZI CONFINATI DPI III E AUTORESPIRATORI", "validita_mesi": 60, "categoria_corso": "SPAZI CONFINATI DPI III E AUTORESPIRATORI"}, # 5 anni
            {"nome_corso": "HLO", "validita_mesi": 0, "categoria_corso": "HLO"}, # Sempre valido
            {"nome_corso": "TESSERA HLO", "validita_mesi": 0, "categoria_corso": "TESSERA HLO"}, # Scadenza da PDF
            {"nome_corso": "UNILAV", "validita_mesi": 0, "categoria_corso": "UNILAV"}, # Scadenza da PDF
            {"nome_corso": "PATENTE", "validita_mesi": 0, "categoria_corso": "PATENTE"}, # Scadenza da PDF
            {"nome_corso": "CARTA DI IDENTITA", "validita_mesi": 0, "categoria_corso": "CARTA DI IDENTITA"}, # Scadenza da PDF
            {"nome_corso": "MODULO RECESSO RAPPORTO DI LAVORO", "validita_mesi": 0, "categoria_corso": "MODULO RECESSO RAPPORTO DI LAVORO"}, # Senza scadenza
            {"nome_corso": "NOMINA", "validita_mesi": 0, "categoria_corso": "NOMINA"},
            {"nome_corso": "VISITA MEDICA", "validita_mesi": 0, "categoria_corso": "VISITA MEDICA"},
            {"nome_corso": "ALTRO", "validita_mesi": 0, "categoria_corso": "ALTRO"},
        ]

        for corso_data in corsi:
            db_corso = db.query(Corso).filter(Corso.nome_corso == corso_data["nome_corso"]).first()
            if not db_corso:
                new_corso = Corso(**corso_data)
                db.add(new_corso)

        # --- Seed Default Admin User ---
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                hashed_password=get_password_hash("allegretti@coemi"),
                account_name="Amministratore",
                is_admin=True
            )
            db.add(admin_user)

        db.commit()
    finally:
        if close_db:
            db.close()
