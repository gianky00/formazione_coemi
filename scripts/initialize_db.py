import os
import sys
from sqlalchemy.orm import sessionmaker
from app.db.session import engine
from app.db.models import Base, CorsiMaster

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def initialize_database():
    Base.metadata.create_all(bind=engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    # Pre-caricamento dei corsi
    corsi = [
        {"Nome Corso": "L1 ART.37", "Validità (Mesi)": 60},
        {"Nome Corso": "L2 PREPOSTI", "Validità (Mesi)": 60},
        {"Nome Corso": "L4 GRU SU AUTOCARRO", "Validità (Mesi)": 60},
        {"Nome Corso": "L4 PLE", "Validità (Mesi)": 60},
        {"Nome Corso": "L5 PES PAV PEI", "Validità (Mesi)": 60},
        {"Nome Corso": "LAVORI IN QUOTA", "Validità (Mesi)": 60},
        {"Nome Corso": "ANTINCENDIO", "Validità (Mesi)": 36},
        {"Nome Corso": "PRIMO SOCCORSO", "Validità (Mesi)": 36},
        {"Nome Corso": "ASPP", "Validità (Mesi)": 60},
        {"Nome Corso": "ATEX", "Validità (Mesi)": 60},
        {"Nome Corso": "BLSD", "Validità (Mesi)": 24},
        {"Nome Corso": "CARROPONTE", "Validità (Mesi)": 60},
        {"Nome Corso": "DIRETTIVA SEVESO", "Validità (Mesi)": 60},
        {"Nome Corso": "DIRIGENTI", "Validità (Mesi)": 60},
        {"Nome Corso": "FORMATORI", "Validità (Mesi)": 36},
        {"Nome Corso": "GRU A TORRE", "Validità (Mesi)": 60},
        {"Nome Corso": "H2S", "Validità (Mesi)": 36},
        {"Nome Corso": "IMBRACATORE", "Validità (Mesi)": 60},
        {"Nome Corso": "MACCHINE OPERATRICI", "Validità (Mesi)": 60},
        {"Nome Corso": "MANITOU P.ROTATIVE", "Validità (Mesi)": 60},
        {"Nome Corso": "MULETTO CARRELLISTI", "Validità (Mesi)": 60},
        {"Nome Corso": "RLS", "Validità (Mesi)": 12},
        {"Nome Corso": "RSPP", "Validità (Mesi)": 60},
        {"Nome Corso": "SOPRAVVIVENZA MARE", "Validità (Mesi)": 48},
        {"Nome Corso": "SPAZI CONFINATI", "Validità (Mesi)": 60},
        {"Nome Corso": "HLO", "Validità (Mesi)": 0},
    ]

    for corso_data in corsi:
        existing_corso = session.query(CorsiMaster).filter_by(nome_corso=corso_data["Nome Corso"]).first()
        if not existing_corso:
            corso = CorsiMaster(
                nome_corso=corso_data["Nome Corso"],
                validita_mesi=corso_data["Validità (Mesi)"]
            )
            session.add(corso)

    session.commit()
    session.close()

if __name__ == "__main__":
    initialize_database()
    print("Database initialized and pre-configured courses loaded.")
