
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QFileDialog, QLabel, QFrame
from PyQt6.QtCore import QThread, pyqtSignal, QObject, Qt
from PyQt6.QtGui import QIcon
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

class DropZone(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                border: 1px solid #E0E0E0;
                border-radius: 15px;
                background-color: #F7F8FC;
            }
        """)
        self.setAcceptDrops(True)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_label = QLabel()
        icon_label.setPixmap(QIcon("desktop_app/icons/analizza.svg").pixmap(64, 64))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        text_label = QLabel("Trascina qui la tua cartella PDF per l'analisi")
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(text_label)

        self.select_folder_button = QPushButton("Oppure seleziona una cartella")
        layout.addWidget(self.select_folder_button)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            if url.isLocalFile() and os.path.isdir(url.toLocalFile()):
                self.parent().upload_folder(url.toLocalFile())
                break

class ImportView(QWidget):
    def __init__(self, progress_widget=None, progress_bar=None, progress_label=None):
        super().__init__()
        self.progress_widget = progress_widget
        self.progress_bar = progress_bar
        self.progress_label = progress_label
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Analisi Documenti")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.layout.addWidget(title)

        self.drop_zone = DropZone(self)
        self.drop_zone.select_folder_button.clicked.connect(self.select_folder)
        self.layout.addWidget(self.drop_zone)

        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        self.results_display.setStyleSheet("font-family: Consolas, monospace; background-color: #F0F0F0; border-radius: 5px;")
        self.layout.addWidget(self.results_display)

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Seleziona Cartella")
        if folder_path:
            self.upload_folder(folder_path)

    def upload_folder(self, folder_path):
        self.results_display.clear()
        pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]

        if not pdf_files:
            self.results_display.setText("Nessun file PDF trovato.")
            return

        self.results_display.setText(f"Trovati {len(pdf_files)} file PDF. Inizio elaborazione...")

        if self.progress_widget and self.progress_bar and self.progress_label:
            self.progress_bar.setMaximum(len(pdf_files))
            self.progress_bar.setValue(0)
            self.progress_label.setText("Inizio...")
            self.progress_widget.setVisible(True)

        self.thread = QThread()
        self.worker = PdfWorker(pdf_files, folder_path)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_processing_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.log_message.connect(self.results_display.append)

        if self.progress_bar and self.progress_label:
            self.worker.progress.connect(self.progress_bar.setValue)
            self.worker.status_update.connect(self.progress_label.setText)

        self.thread.start()

    def on_processing_finished(self):
        if self.progress_label:
            self.progress_label.setText("Elaborazione completata.")
