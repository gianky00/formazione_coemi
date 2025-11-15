from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QFileDialog, QFormLayout, QLineEdit, QMessageBox
import requests
import os

class ImportView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.upload_folder_button = QPushButton("Carica Cartella PDF")
        self.upload_folder_button.clicked.connect(self.upload_folder)
        self.layout.addWidget(self.upload_folder_button)

        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        self.layout.addWidget(self.results_display)


    def upload_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Seleziona Cartella")
        if folder_path:
            pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
            self.results_display.setText(f"Trovati {len(pdf_files)} file PDF. Inizio elaborazione...")
            for pdf_file in pdf_files:
                file_path = os.path.join(folder_path, pdf_file)
                self.process_pdf(file_path)

    def process_pdf(self, file_path):
        with open(file_path, 'rb') as f:
            files = {'file': (file_path, f, 'application/pdf')}
            try:
                response = requests.post("http://localhost:8000/upload-pdf/", files=files)
                if response.status_code == 200:
                    data = response.json()
                    entities = data.get('entities', {})

                    certificato = {
                        "nome": entities.get('nome', ''),
                        "corso": entities.get('corso', ''),
                        "categoria": entities.get('categoria', 'ALTRO'),
                        "data_rilascio": entities.get('data_rilascio', ''),
                        "data_scadenza": entities.get('data_scadenza', '')
                    }

                    # Automatically validate the data
                    response = requests.post("http://localhost:8000/certificati/", json=certificato)
                    if response.status_code != 200:
                        self.results_display.append(f"Errore durante il salvataggio di {os.path.basename(file_path)}: {response.text}")
                    else:
                        self.results_display.append(f"File {os.path.basename(file_path)} elaborato e salvato con successo.")
                else:
                    self.results_display.append(f"Errore durante l'elaborazione di {os.path.basename(file_path)}: {response.text}")
            except requests.exceptions.ConnectionError as e:
                self.results_display.append(f"Errore di connessione durante l'elaborazione di {os.path.basename(file_path)}: {e}")
