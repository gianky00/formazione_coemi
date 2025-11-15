
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.models import CorsiMaster, Base

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# List of master courses and their validity in months
corsi_master_data = [
    {"nome_corso": "ANTINCENDIO", "validita_mesi": 60, "categoria_corso": "ANTINCENDIO E PRIMO SOCCORSO"},
    {"nome_corso": "PRIMO SOCCORSO", "validita_mesi": 36, "categoria_corso": "ANTINCENDIO E PRIMO SOCCORSO"},
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
    {"nome_corso": "AGGIORNAMENTO LAVORATORI ART.37", "validita_mesi": 60, "categoria_corso": "AGGIORNAMENTO LAVORATORI ART.37"},
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
]

def populate_corsi_master():
    db = SessionLocal()
    try:
        for corso_data in corsi_master_data:
            # Check if the course already exists
            db_corso = db.query(CorsiMaster).filter_by(nome_corso=corso_data["nome_corso"]).first()
            if db_corso:
                # Update validity and category if they have changed
                updated = False
                if db_corso.validita_mesi != corso_data["validita_mesi"]:
                    db_corso.validita_mesi = corso_data["validita_mesi"]
                    updated = True
                if db_corso.categoria_corso != corso_data["categoria_corso"]:
                    db_corso.categoria_corso = corso_data["categoria_corso"]
                    updated = True
                if updated:
                    print(f"Updated course: {corso_data['nome_corso']}")
            else:
                # Create a new course
                db_corso = CorsiMaster(**corso_data)
                db.add(db_corso)
                print(f"Added new course: {corso_data['nome_corso']}")

        db.commit()
        print("CorsiMaster table has been successfully populated/updated.")

    finally:
        db.close()

if __name__ == "__main__":
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    populate_corsi_master()
