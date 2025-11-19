
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QFileDialog, QLabel, QFrame
from PyQt6.QtCore import QThread, pyqtSignal, QObject, Qt
from PyQt6.QtGui import QIcon
import requests
import os
import shutil
from datetime import datetime
from ..api_client import APIClient

class PdfWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    log_message = pyqtSignal(str)
    status_update = pyqtSignal(str)

    def __init__(self, pdf_files, folder_path, api_client):
        super().__init__()
        self.pdf_files = pdf_files
        self.folder_path = folder_path
        self.api_client = api_client

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
        unanalyzed_folder = os.path.join(base_folder, "NON ANALIZZATI")
        documenti_folder = os.path.join(base_folder, "DOCUMENTI DIPENDENTI")

        os.makedirs(unanalyzed_folder, exist_ok=True)
        os.makedirs(documenti_folder, exist_ok=True)

        original_filename = os.path.basename(file_path)

        try:
            with open(file_path, 'rb') as f:
                files = {'file': (original_filename, f, 'application/pdf')}
                response = requests.post(f"{self.api_client.base_url}/upload-pdf/", files=files)

            if response.status_code == 200:
                data = response.json()
                entities = data.get('entities', {})

                data_rilascio_raw = entities.get('data_rilascio', '')
                data_scadenza_raw = entities.get('data_scadenza', '')
                data_rilascio_norm = data_rilascio_raw.replace('-', '/') if data_rilascio_raw else ''
                data_scadenza_norm = data_scadenza_raw.replace('-', '/') if data_scadenza_raw else ''
                data_nascita_raw = entities.get('data_nascita', '')
                data_nascita_norm = data_nascita_raw.replace('-', '/') if data_nascita_raw else ''

                certificato = {
                    "nome_dipendente": entities.get('nome_dipendente', ''),
                    "cognome_dipendente": entities.get('cognome_dipendente', ''),
                    "corso": entities.get('corso', ''),
                    "categoria": entities.get('categoria', 'ALTRO'),
                    "data_rilascio": data_rilascio_norm,
                    "data_scadenza": data_scadenza_norm,
                    "data_nascita": data_nascita_norm
                }
                save_response = requests.post(f"{self.api_client.base_url}/certificati/", json=certificato)

                if save_response.status_code == 200:
                    self.log_message.emit(f"File {original_filename} elaborato e salvato con successo.")
                    try:
                        cert_data = save_response.json()

                        nome = cert_data.get('nome_dipendente', 'NOME_NON_TROVATO')
                        cognome = cert_data.get('cognome_dipendente', 'COGNOME_NON_TROVATO')
                        matricola = cert_data.get('matricola') if cert_data.get('matricola') else 'N-A'

                        employee_folder_name = f"{cognome} {nome} ({matricola})"

                        categoria = cert_data.get('categoria', 'CATEGORIA_NON_TROVATA')

                        data_scadenza_str = cert_data.get('data_scadenza')
                        stato = 'STORICO'
                        if not data_scadenza_str:
                            stato = 'ATTIVO'
                            file_scadenza = "no scadenza"
                        else:
                            scadenza_date = datetime.strptime(data_scadenza_str, '%d/%m/%Y').date()
                            if scadenza_date >= datetime.now().date():
                                stato = 'ATTIVO'
                            file_scadenza = scadenza_date.strftime('%d_%m_%Y')

                        new_filename = f"{cognome} {nome} ({matricola}) - {categoria} - {file_scadenza}.pdf"

                        # Create directory structure
                        dest_path = os.path.join(documenti_folder, employee_folder_name, categoria, stato)
                        os.makedirs(dest_path, exist_ok=True)

                        shutil.move(file_path, os.path.join(dest_path, new_filename))

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
        self.setObjectName("card")
        self.setAcceptDrops(True)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        icon_label = QLabel()
        icon_label.setPixmap(QIcon("desktop_app/icons/analizza.svg").pixmap(80, 80))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        main_text = QLabel("Trascina i tuoi file PDF qui")
        main_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_text.setStyleSheet("font-size: 20px; font-weight: 600; color: #1F2937;")
        layout.addWidget(main_text)

        sub_text = QLabel("oppure")
        sub_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub_text.setStyleSheet("font-size: 16px; color: #6B7280;")
        layout.addWidget(sub_text)

        self.select_folder_button = QPushButton("Seleziona Cartella")
        self.select_folder_button.setObjectName("secondary")
        self.select_folder_button.setFixedWidth(200)
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
    import_completed = pyqtSignal()

    def __init__(self, progress_widget=None, progress_bar=None, progress_label=None):
        super().__init__()
        self.progress_widget = progress_widget
        self.progress_bar = progress_bar
        self.progress_label = progress_label
        self.api_client = APIClient()
        self.layout = QVBoxLayout(self)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)

        title = QLabel("Analisi Documenti")
        title.setStyleSheet("font-size: 28px; font-weight: 700;")
        title_layout.addWidget(title)

        description = QLabel("Carica, analizza ed estrai automaticamente le informazioni dai tuoi documenti.")
        description.setStyleSheet("font-size: 16px; color: #6B7280;")
        title_layout.addWidget(description)

        self.layout.addLayout(title_layout)

        self.drop_zone = DropZone(self)
        self.drop_zone.select_folder_button.clicked.connect(self.select_folder)
        self.layout.addWidget(self.drop_zone, 1) # Make drop zone stretch

        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        self.results_display.setObjectName("card")
        self.results_display.setStyleSheet("font-family: 'Consolas', 'Menlo', monospace; background-color: #FFFFFF; color: #4B5563; border-radius: 12px; font-size: 13px;")
        self.layout.addWidget(self.results_display, 1) # Make results stretch

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
        self.worker = PdfWorker(pdf_files, folder_path, self.api_client)
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
        self.import_completed.emit()
