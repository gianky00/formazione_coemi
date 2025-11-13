import unittest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.session import engine
from app.db.models import Base, CorsiMaster
from app.services.entity_extraction import extract_entities
from scripts.initialize_db import initialize_database

class TestServices(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Use the application's database for testing
        cls.engine = engine
        Base.metadata.create_all(bind=cls.engine)
        initialize_database() # Initialize with corsi
        cls.Session = sessionmaker(bind=cls.engine)

    def test_extract_entities(self):
        session = self.Session()
        text = "This is a test file.\nCourse: L4 GRU SU AUTOCARRO\nDate: 2024-01-01\nName: Mario Rossi"
        entities = extract_entities(text, session)
        self.assertEqual(entities['nome'], 'Mario Rossi')
        self.assertEqual(entities['corso'], 'L4 GRU SU AUTOCARRO')
        self.assertEqual(str(entities['data_rilascio']), '2024-01-01')
        self.assertEqual(str(entities['data_scadenza']), '2029-01-01')
        session.close()

if __name__ == '__main__':
    unittest.main()
