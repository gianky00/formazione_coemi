import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Base, CorsiMaster
from app.services.ai_extraction import extract_entities_with_ai

class TestAIExtraction(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Use a temporary in-memory database for testing
        cls.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=cls.engine)

        # Manually insert test data
        Session = sessionmaker(bind=cls.engine)
        session = Session()
        corso = CorsiMaster(nome_corso="FORMAZIONE PREPOSTO", validita_mesi=60)
        session.add(corso)
        session.commit()
        session.close()

        cls.Session = sessionmaker(bind=cls.engine)

    def test_extract_entities_with_ai(self):
        session = self.Session()
        # Testo di esempio da un attestato
        text = """
        ATTESTATO DI FORMAZIONE
        Si certifica che il Sig. ANDRIANI SAVERIO
        ha frequentato il corso di FORMAZIONE PREPOSTO
        in data 03-09-2021
        """
        entities = extract_entities_with_ai(text, session)

        self.assertEqual(entities['dipendente'], 'ANDRIANI SAVERIO')
        self.assertEqual(entities['corso'], 'FORMAZIONE PREPOSTO')
        self.assertEqual(str(entities['data_rilascio']), '2021-09-03')
        # La data di scadenza dipende dalla logica di business e dai dati in CorsiMaster
        # Assumiamo che "FORMAZIONE PREPOSTO" abbia una validità di 60 mesi (5 anni)
        self.assertEqual(str(entities['data_scadenza']), '2026-09-03')

        session.close()

if __name__ == '__main__':
    unittest.main()
