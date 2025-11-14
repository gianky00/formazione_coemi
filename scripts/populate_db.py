
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
    {"nome_corso": "ANTINCENDIO E PRIMO SOCCORSO", "validita_mesi": 60},
    {"nome_corso": "ASPP", "validita_mesi": 60},
    {"nome_corso": "ATEX", "validita_mesi": 60},
    {"nome_corso": "BLSD", "validita_mesi": 24},
    {"nome_corso": "CARROPONTE", "validita_mesi": 60},
    {"nome_corso": "DIRETTIVA SEVESO", "validita_mesi": 60},
    {"nome_corso": "DIRIGENTI E FORMATORI", "validita_mesi": 60}, # Assuming 5 years for Dirigenti, Formatori is 3
    {"nome_corso": "GRU A TORRE E PONTE", "validita_mesi": 60},
    {"nome_corso": "H2S", "validita_mesi": 60},
    {"nome_corso": "IMBRACATORE E SEGNALETICA GESTUALE", "validita_mesi": 60},
    {"nome_corso": "L1 ART.37", "validita_mesi": 60},
    {"nome_corso": "L2 PREPOSTI", "validita_mesi": 24},
    {"nome_corso": "L4 GRU SU AUTOCARRO", "validita_mesi": 60},
    {"nome_corso": "L4 PLE", "validita_mesi": 60},
    {"nome_corso": "L5 PES PAV PEI C CANTIERE", "validita_mesi": 60},
    {"nome_corso": "LAVORI IN QUOTA", "validita_mesi": 60},
    {"nome_corso": "MACCHINE OPERATRICI", "validita_mesi": 60},
    {"nome_corso": "MANITOU P.ROTATIVE", "validita_mesi": 60},
    {"nome_corso": "MEDICO COMPETENTE", "validita_mesi": 36},
    {"nome_corso": "MULETTO CARRELISTI", "validita_mesi": 60},
    {"nome_corso": "SOPRAVVIVENZA E SALVATAGGIO IN MARE", "validita_mesi": 48},
    {"nome_corso": "SPAZI CONFINATI DPI III E AUTORESPIRATORI", "validita_mesi": 60},
]

def populate_corsi_master():
    db = SessionLocal()
    try:
        for corso_data in corsi_master_data:
            # Check if the course already exists
            db_corso = db.query(CorsiMaster).filter_by(nome_corso=corso_data["nome_corso"]).first()
            if db_corso:
                # Update the validity if it has changed
                if db_corso.validita_mesi != corso_data["validita_mesi"]:
                    db_corso.validita_mesi = corso_data["validita_mesi"]
                    print(f"Updated validity for course: {corso_data['nome_corso']}")
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
