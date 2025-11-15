from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QFileDialog, QFormLayout, QLineEdit, QMessageBox
from PyQt6.QtCore import QThread, pyqtSignal, QObject
import requests
import os
import shutil
from datetime import datetime
from ..api_client import API_URL

class PdfWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    log_message = pyqtSignal(str)
    status_update = pyqtSignal(str)

    def __init__(self, pdf_files, folder_path):
        super().__init__()
        self.pdf_files = pdf_files
        self.folder_path = folder_path

    def run(self):
        total_files = len(self.pdf_files)
        for i, pdf_file in enumerate(self.pdf_files):
            self.status_update.emit(f"Elaborazione file {i+1} di {total_files}...")
            file_path = os.path.join(self.folder_path, pdf_file)
            self.process_pdf(file_path)
            self.progress.emit(i + 1)
        self.finished.emit()

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
                certificato = { "nome": entities.get('nome', ''), "corso": entities.get('corso', ''), "categoria": entities.get('categoria', 'ALTRO'), "data_rilascio": entities.get('data_rilascio', ''), "data_scadenza": entities.get('data_scadenza', '') }
                save_response = requests.post(f"{API_URL}/certificati/", json=certificato)

                if save_response.status_code == 200:
                    self.log_message.emit(f"File {original_filename} elaborato e salvato con successo.")
                    try:
                        nome = entities.get('nome', 'NOME_NON_TROVATO')
                        categoria = entities.get('categoria', 'CATEGORIA_NON_TROVATA')
                        data_rilascio_str = entities.get('data_rilascio', '')
                        dt_object = datetime.strptime(data_rilascio_str, '%d/%m/%Y')
                        formatted_date = dt_object.strftime('%d-%m-%Y')
                        new_filename = f"{nome} {categoria} {formatted_date}.pdf"
                        shutil.move(file_path, os.path.join(analyzed_folder, new_filename))
                    except Exception as e:
                        self.log_message.emit(f"Errore durante lo spostamento del file {original_filename}: {e}")
                        shutil.move(file_path, os.path.join(unanalyzed_folder, original_filename))
                elif save_response.status_code == 409:
                    self.log_message.emit(f"{original_filename} - Documento risulta già in Database.")
                    shutil.move(file_path, os.path.join(unanalyzed_folder, original_filename))
                else:
                    self.log_message.emit(f"Errore durante il salvaggio di {original_filename}: {save_response.text}")
                    shutil.move(file_path, os.path.join(unanalyzed_folder, original_filename))
            else:
                self.log_message.emit(f"Errore durante l'elaborazione di {original_filename}: {response.text}")
                shutil.move(file_path, os.path.join(unanalyzed_folder, original_filename))
        except (requests.exceptions.RequestException, IOError) as e:
            self.log_message.emit(f"Errore critico durante l'elaborazione di {original_filename}: {e}")
            try:
                shutil.move(file_path, os.path.join(unanalyzed_folder, original_filename))
            except Exception as move_error:
                self.log_message.emit(f"Impossibile spostare il file {original_filename}: {move_error}")

class ImportView(QWidget):
    def __init__(self, progress_widget, progress_bar, progress_label):
        super().__init__()
        self.progress_widget = progress_widget
        self.progress_bar = progress_bar
        self.progress_label = progress_label
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
            self.results_display.clear()
            pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
            self.results_display.setText(f"Trovati {len(pdf_files)} file PDF. Inizio elaborazione...")

            self.progress_bar.setRange(0, len(pdf_files))
            self.progress_bar.setValue(0)
            self.progress_widget.setVisible(True)
            self.upload_folder_button.setEnabled(False)

            self.thread = QThread()
            self.worker = PdfWorker(pdf_files, folder_path)
            self.worker.moveToThread(self.thread)

            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.worker.progress.connect(self.progress_bar.setValue)
            self.worker.log_message.connect(self.results_display.append)
            self.worker.status_update.connect(self.progress_label.setText)

            self.thread.finished.connect(
                lambda: (
                    self.progress_widget.setVisible(False),
                    self.upload_folder_button.setEnabled(True),
                    self.results_display.append("\nElaborazione completata.")
                )
            )

            self.thread.start()
