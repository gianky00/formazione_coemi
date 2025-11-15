from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QFileDialog, QFormLayout, QLineEdit, QMessageBox
import requests
import os
import shutil
from datetime import datetime
from ..api_client import API_URL

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
        base_folder = os.path.dirname(file_path)
        analyzed_folder = os.path.join(base_folder, "PDF ANALIZZATI")
        unanalyzed_folder = os.path.join(base_folder, "NON ANALIZZATI")

        os.makedirs(analyzed_folder, exist_ok=True)
        os.makedirs(unanalyzed_folder, exist_ok=True)

        original_filename = os.path.basename(file_path)

        try:
            with open(file_path, 'rb') as f:
                files = {'file': (original_filename, f, 'application/pdf')}
                response = requests.post(f"{API_URL}/upload-pdf/", files=files)

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

                # Save the certificate data
                save_response = requests.post(f"{API_URL}/certificati/", json=certificato)

                if save_response.status_code == 200:
                    self.results_display.append(f"File {original_filename} elaborato e salvato con successo.")

                    # Rename and move the file
                    try:
                        nome = entities.get('nome', 'NOME_NON_TROVATO')
                        categoria = entities.get('categoria', 'CATEGORIA_NON_TROVATA')
                        data_rilascio_str = entities.get('data_rilascio', '')

                        dt_object = datetime.strptime(data_rilascio_str, '%d/%m/%Y')
                        formatted_date = dt_object.strftime('%d-%m-%Y')

                        new_filename = f"{nome} {categoria} {formatted_date}.pdf"
                        shutil.move(file_path, os.path.join(analyzed_folder, new_filename))
                    except Exception as e:
                        self.results_display.append(f"Errore durante lo spostamento del file {original_filename}: {e}")
                        shutil.move(file_path, os.path.join(unanalyzed_folder, original_filename))
                else:
                    self.results_display.append(f"Errore durante il salvaggio di {original_filename}: {save_response.text}")
                    shutil.move(file_path, os.path.join(unanalyzed_folder, original_filename))
            else:
                self.results_display.append(f"Errore durante l'elaborazione di {original_filename}: {response.text}")
                shutil.move(file_path, os.path.join(unanalyzed_folder, original_filename))
        except (requests.exceptions.RequestException, IOError) as e:
            self.results_display.append(f"Errore critico durante l'elaborazione di {original_filename}: {e}")
            try:
                shutil.move(file_path, os.path.join(unanalyzed_folder, original_filename))
            except Exception as move_error:
                self.results_display.append(f"Impossibile spostare il file {original_filename}: {move_error}")
