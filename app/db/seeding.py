from sqlalchemy.orm import Session
from app.db.models import Corso
from app.db.session import SessionLocal

def seed_database(db: Session = None):
    """
    Populates the database with a predefined list of master courses.
    """
    if db is None:
        db = SessionLocal()
        close_db = True
    else:
        close_db = False

    try:
        corsi = [
            {"nome_corso": "ANTINCENDIO", "validita_mesi": 60, "categoria_corso": "ANTINCENDIO"},
            {"nome_corso": "PRIMO SOCCORSO", "validita_mesi": 36, "categoria_corso": "PRIMO SOCCORSO"},
            {"nome_corso": "ASPP", "validita_mesi": 60, "categoria_corso": "ASPP"},
            {"nome_corso": "RSPP", "validita_mesi": 60, "categoria_corso": "RSPP"},
            {"nome_corso": "ATEX", "validita_mesi": 60, "categoria_corso": "ATEX"},
            {"nome_corso": "BLSD", "validita_mesi": 12, "categoria_corso": "BLSD"},
            {"nome_corso": "CARROPONTE", "validita_mesi": 60, "categoria_corso": "CARROPONTE"},
            {"nome_corso": "DIRETTIVA SEVESO", "validita_mesi": 60, "categoria_corso": "DIRETTIVA SEVESO"},
            {"nome_corso": "DIRIGENTI E FORMATORI", "validita_mesi": 60, "categoria_corso": "DIRIGENTI E FORMATORI"},
            {"nome_corso": "GRU A TORRE E PONTE", "validita_mesi": 60, "categoria_corso": "GRU A TORRE E PONTE"},
            {"nome_corso": "H2S", "validita_mesi": 60, "categoria_corso": "H2S"},
            {"nome_corso": "IMBRACATORE", "validita_mesi": 60, "categoria_corso": "IMBRACATORE"},
            {"nome_corso": "FORMAZIONE GENERICA ART.37", "validita_mesi": 60, "categoria_corso": "FORMAZIONE GENERICA ART.37"},
            {"nome_corso": "PREPOSTO", "validita_mesi": 24, "categoria_corso": "PREPOSTO"},
            {"nome_corso": "GRU SU AUTOCARRO", "validita_mesi": 60, "categoria_corso": "GRU SU AUTOCARRO"},
            {"nome_corso": "PLE", "validita_mesi": 60, "categoria_corso": "PLE"},
            {"nome_corso": "PES PAV PEI C CANTIERE", "validita_mesi": 60, "categoria_corso": "PES PAV PEI C CANTIERE"},
            {"nome_corso": "LAVORI IN QUOTA", "validita_mesi": 60, "categoria_corso": "LAVORI IN QUOTA"},
            {"nome_corso": "MACCHINE OPERATRICI", "validita_mesi": 60, "categoria_corso": "MACCHINE OPERATRICI"},
            {"nome_corso": "MANITOU P.ROTATIVE", "validita_mesi": 60, "categoria_corso": "MANITOU P.ROTATIVE"},
            {"nome_corso": "MEDICO COMPETENTE", "validita_mesi": 0, "categoria_corso": "MEDICO COMPETENTE"},
            {"nome_corso": "MULETTO CARRELISTI", "validita_mesi": 60, "categoria_corso": "MULETTO CARRELISTI"},
            {"nome_corso": "SOPRAVVIVENZA E SALVATAGGIO IN MARE", "validita_mesi": 60, "categoria_corso": "SOPRAVVIVENZA E SALVATAGGIO IN MARE"},
            {"nome_corso": "SPAZI CONFINATI DPI III E AUTORESPIRATORI", "validita_mesi": 60, "categoria_corso": "SPAZI CONFINATI DPI III E AUTORESPIRATORI"},
            {"nome_corso": "HLO", "validita_mesi": 0, "categoria_corso": "HLO"},
            {"nome_corso": "NOMINE", "validita_mesi": 0, "categoria_corso": "NOMINE"},
            {"nome_corso": "VISITA MEDICA", "validita_mesi": 0, "categoria_corso": "VISITA MEDICA"},
            {"nome_corso": "ALTRO", "validita_mesi": 0, "categoria_corso": "ALTRO"},
        ]

        for corso_data in corsi:
            db_corso = db.query(Corso).filter(Corso.nome_corso == corso_data["nome_corso"]).first()
            if not db_corso:
                new_corso = Corso(**corso_data)
                db.add(new_corso)

        db.commit()
    finally:
        if close_db:
            db.close()
