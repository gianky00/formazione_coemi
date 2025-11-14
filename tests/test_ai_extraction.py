import unittest
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Base, CorsiMaster
from app.api.main import calculate_expiration_date

class TestBusinessLogic(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Usa un database in memoria per i test
        cls.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=cls.engine)

        # Inserisci dati di test per i corsi
        Session = sessionmaker(bind=cls.engine)
        session = Session()
        # Use a master course name that exists in our master list
        corso1 = CorsiMaster(nome_corso="L2 PREPOSTI", validita_mesi=24) # 2 anni
        corso2 = CorsiMaster(nome_corso="PRIMO SOCCORSO", validita_mesi=36) # 3 anni
        session.add(corso1)
        session.add(corso2)
        session.commit()
        session.close()

        cls.Session = sessionmaker(bind=cls.engine)

    @patch('app.services.ai_extraction.model')
    def test_end_to_end_logic(self, mock_gemini_model):

        # 1. Mock della risposta di Gemini
        mock_response_text = """
        ```json
        {
          "nome": "ARGENTATI IVANOE",
          "corso": "FORMAZIONE PREPOSTO",
          "data_rilascio": "14-01-2021",
          "corso_master": "L2 PREPOSTI"
        }
        ```
        """
        mock_gemini_response = MagicMock()
        mock_gemini_response.text = mock_response_text
        mock_gemini_model.generate_content.return_value = mock_gemini_response

        # 2. Chiama il servizio (che ora usa il mock)
        from app.services.ai_extraction import extract_entities_with_ai
        test_ocr_text = "Questo è un testo di OCR di esempio."
        gemini_result = extract_entities_with_ai(test_ocr_text)

        # Verifica che il mock sia stato chiamato e che il parsing sia corretto
        mock_gemini_model.generate_content.assert_called_once()
        self.assertEqual(gemini_result['nome'], "ARGENTATI IVANOE")
        self.assertEqual(gemini_result['corso'], "FORMAZIONE PREPOSTO")
        self.assertEqual(gemini_result['data_rilascio'], "14-01-2021")

        # 3. Ora, testa la logica di business con questo risultato
        session = self.Session()
        final_entities = calculate_expiration_date(gemini_result, session)
        session.close()

        # 4. Verifica il risultato finale
        self.assertEqual(final_entities['nome'], "ARGENTATI IVANOE")
        self.assertEqual(final_entities['corso'], "FORMAZIONE PREPOSTO")
        self.assertEqual(final_entities['data_rilascio'], "14/01/2021") # Controlla la formattazione DD/MM/YYYY
        self.assertEqual(final_entities['data_scadenza'], "14/01/2023") # Controlla il calcolo e la formattazione (2 anni)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
