
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QFileDialog, QLabel, QFrame, QSizePolicy
from PyQt6.QtCore import QThread, pyqtSignal, QObject, Qt, QVariantAnimation, QSize
from PyQt6.QtGui import QIcon, QColor
import requests
import os
import shutil
from datetime import datetime
from ..api_client import APIClient
from ..components.animated_widgets import LoadingOverlay

class PdfWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    log_message = pyqtSignal(str)
    status_update = pyqtSignal(str)

    def __init__(self, file_paths, api_client):
        super().__init__()
        self.file_paths = file_paths
        self.api_client = api_client
        self._is_stopped = False
        self._start_time = 0

    def stop(self):
        self._is_stopped = True

    def run(self):
        total_files = len(self.file_paths)
        self._start_time = datetime.now()
        for i, file_path in enumerate(self.file_paths):
            if self._is_stopped:
                self.log_message.emit("<font color='orange'>Analisi interrotta dall'utente.</font>")
                break

            # ETR Calculation
            elapsed_time = (datetime.now() - self._start_time).total_seconds()
            avg_time_per_file = elapsed_time / (i + 1)
            remaining_files = total_files - (i + 1)
            etr_seconds = avg_time_per_file * remaining_files

            if etr_seconds > 60:
                etr_str = f"Circa {int(etr_seconds / 60)} minuti rimanenti"
            else:
                etr_str = f"Circa {int(etr_seconds)} secondi rimanenti"

            self.status_update.emit(f"Elaborazione {i+1} di {total_files} ({etr_str})")
            self.process_pdf(file_path)
            self.progress.emit(i + 1)
        self.finished.emit()

    def process_pdf(self, file_path):
        base_folder = os.path.dirname(file_path)
        analyzed_folder = os.path.join(base_folder, "DOCUMENTI ANALIZZATI ASSENZA MATRICOLE")
        unanalyzed_folder = os.path.join(base_folder, "DOCUMENTI NON ANALIZZATI")

        os.makedirs(analyzed_folder, exist_ok=True)
        os.makedirs(unanalyzed_folder, exist_ok=True)

        original_filename = os.path.basename(file_path)

        try:
            with open(file_path, 'rb') as f:
                files = {'file': (original_filename, f, 'application/pdf')}
                response = requests.post(f"{self.api_client.base_url}/upload-pdf/", files=files, headers=self.api_client._get_headers())

            if response.status_code == 200:
                data = response.json()
                entities = data.get('entities', {})

                # Normalizza il formato della data prima di inviarlo
                data_rilascio_raw = entities.get('data_rilascio', '')
                data_scadenza_raw = entities.get('data_scadenza', '')

                data_rilascio_norm = data_rilascio_raw.replace('-', '/') if data_rilascio_raw else ''
                data_scadenza_norm = data_scadenza_raw.replace('-', '/') if data_scadenza_raw else ''

                data_nascita_raw = entities.get('data_nascita', '')
                data_nascita_norm = data_nascita_raw.replace('-', '/') if data_nascita_raw else ''

                certificato = {
                    "nome": entities.get('nome', ''),
                    "corso": entities.get('corso', ''),
                    "categoria": entities.get('categoria', 'ALTRO'),
                    "data_rilascio": data_rilascio_norm,
                    "data_scadenza": data_scadenza_norm,
                    "data_nascita": data_nascita_norm
                }
                save_response = requests.post(f"{self.api_client.base_url}/certificati/", json=certificato, headers=self.api_client._get_headers())

                if save_response.status_code == 200:
                    cert_data = save_response.json()
                    ragione_fallimento = cert_data.get('assegnazione_fallita_ragione')

                    if ragione_fallimento:
                        log_msg = f"<font color='blue'>File {original_filename} analizzato. Assegnazione manuale richiesta: {ragione_fallimento}</font>"
                        self.log_message.emit(log_msg)
                        shutil.move(file_path, os.path.join(analyzed_folder, original_filename))
                    else:
                        nome_completo = cert_data.get('nome', 'ERRORE')
                        self.log_message.emit(f"<font color='green'>File {original_filename} elaborato e salvato per {nome_completo}.</font>")
                        try:
                            matricola = cert_data.get('matricola') if cert_data.get('matricola') else 'N-A'
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

                            employee_folder_name = f"{nome_completo} ({matricola})"
                            new_filename = f"{nome_completo} ({matricola}) - {categoria} - {file_scadenza}.pdf"

                            documenti_folder = os.path.join(base_folder, "DOCUMENTI DIPENDENTI")
                            dest_path = os.path.join(documenti_folder, employee_folder_name, categoria, stato)
                            os.makedirs(dest_path, exist_ok=True)

                            shutil.move(file_path, os.path.join(dest_path, new_filename))
                        except Exception as e:
                            self.log_message.emit(f"<font color='red'>Errore durante lo spostamento del file {original_filename}: {e}</font>")
                            shutil.move(file_path, os.path.join(unanalyzed_folder, original_filename))
                elif save_response.status_code == 409:
                    self.log_message.emit(f"<font color='orange'>{original_filename} - Documento risulta già in Database.</font>")
                    shutil.move(file_path, os.path.join(unanalyzed_folder, original_filename))
                else:
                    self.log_message.emit(f"<font color='red'>Errore durante il salvaggio di {original_filename}: {save_response.text}</font>")
                    shutil.move(file_path, os.path.join(unanalyzed_folder, original_filename))
            elif response.status_code == 401:
                self.log_message.emit(f"<font color='red'>Errore di autenticazione durante l'elaborazione di {original_filename}: API Key non valida o mancante.</font>")
                shutil.move(file_path, os.path.join(unanalyzed_folder, original_filename))
            else:
                self.log_message.emit(f"<font color='red'>Errore durante l'elaborazione di {original_filename}: {response.text}</font>")
                shutil.move(file_path, os.path.join(unanalyzed_folder, original_filename))
        except (requests.exceptions.RequestException, IOError) as e:
            self.log_message.emit(f"<font color='red'>Errore critico durante l'elaborazione di {original_filename}: {e}</font>")
            try:
                shutil.move(file_path, os.path.join(unanalyzed_folder, original_filename))
            except Exception as move_error:
                self.log_message.emit(f"<font color='red'>Impossibile spostare il file {original_filename}: {move_error}</font>")

class DropZone(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setObjectName("drop_zone")
        self.setAcceptDrops(True)

        # Initial Style
        self._bg_color = "#FFFFFF"
        self._border_color = "#E5E7EB"
        self.update_style(self._bg_color, self._border_color, "solid")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        icon_label = QLabel()
        icon_label.setPixmap(QIcon("desktop_app/icons/analizza.svg").pixmap(80, 80))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        main_text = QLabel("Trascina i tuoi file PDF qui (Max 20MB)")
        main_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_text.setStyleSheet("font-size: 20px; font-weight: 600; color: #1F2937; background: transparent;")
        layout.addWidget(main_text)

        sub_text = QLabel("oppure")
        sub_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub_text.setStyleSheet("font-size: 16px; color: #6B7280; background: transparent;")
        layout.addWidget(sub_text)

        self.select_folder_button = QPushButton("Seleziona Cartella")
        self.select_folder_button.setObjectName("secondary")
        self.select_folder_button.setFixedWidth(200)
        layout.addWidget(self.select_folder_button)

        # Animation Setup - Pulse Background Color
        self.pulse_anim = QVariantAnimation(self)
        self.pulse_anim.setDuration(1500)
        self.pulse_anim.setLoopCount(-1) # Infinite
        self.pulse_anim.setStartValue(QColor("#EFF6FF")) # Light Blue
        self.pulse_anim.setKeyValueAt(0.5, QColor("#DBEAFE")) # Blue-100
        self.pulse_anim.setEndValue(QColor("#EFF6FF"))
        self.pulse_anim.valueChanged.connect(self.on_pulse_value_changed)

    def update_style(self, bg_color, border_color, border_style="solid"):
        self.setStyleSheet(f"""
            QFrame#drop_zone {{
                background-color: {bg_color};
                border-radius: 12px;
                border: 2px {border_style} {border_color};
            }}
            QLabel {{ background: transparent; }}
        """)

    def on_pulse_value_changed(self, color):
        self.update_style(color.name(), "#3B82F6", "dashed")

    def dragEnterEvent(self, event):
        if getattr(self.parent(), 'is_read_only', False):
            event.ignore()
            return

        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.pulse_anim.start()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.pulse_anim.stop()
        self.update_style("#FFFFFF", "#E5E7EB", "solid")

    def dropEvent(self, event):
        self.pulse_anim.stop()
        self.update_style("#FFFFFF", "#E5E7EB", "solid")

        files_to_process = []
        for url in event.mimeData().urls():
            if url.isLocalFile():
                path = url.toLocalFile()
                if os.path.isfile(path) and path.lower().endswith('.pdf'):
                    files_to_process.append(path)
                elif os.path.isdir(path):
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            if file.lower().endswith('.pdf'):
                                files_to_process.append(os.path.join(root, file))

        if files_to_process:
            self.parent().process_dropped_files(files_to_process)

class ImportView(QWidget):
    import_completed = pyqtSignal()

    def __init__(self, progress_widget=None, progress_bar=None, progress_label=None):
        super().__init__()
        self.progress_widget = progress_widget
        self.progress_bar = progress_bar
        self.progress_label = progress_label
        self.api_client = APIClient()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        description = QLabel("Carica, analizza ed estrai automaticamente le informazioni dai tuoi documenti. (Max 20MB per file)")
        description.setStyleSheet("font-size: 16px; color: #6B7280;")
        self.layout.addWidget(description)

        self.drop_zone = DropZone(self)
        self.drop_zone.select_folder_button.clicked.connect(self.select_folder)
        self.layout.addWidget(self.drop_zone, 1)

        # New progress/control widgets
        self.progress_container = QFrame()
        self.progress_container.setObjectName("card")
        progress_layout = QVBoxLayout(self.progress_container)
        self.etr_label = QLabel("Pronto per l'analisi.")
        progress_layout.addWidget(self.etr_label)
        self.stop_button = QPushButton("Interrompi Analisi")
        self.stop_button.setObjectName("destructive")
        self.stop_button.clicked.connect(self.stop_processing)
        progress_layout.addWidget(self.stop_button)
        self.progress_container.setVisible(False)
        self.layout.addWidget(self.progress_container)

        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        self.results_display.setObjectName("card")
        self.results_display.setStyleSheet("font-family: 'Consolas', 'Menlo', monospace; background-color: #FFFFFF; color: #4B5563; border-radius: 12px; font-size: 13px; padding: 10px; border: 1px solid #E5E7EB;")
        self.layout.addWidget(self.results_display, 1)

        self.worker = None
        self.thread = None

    def set_read_only(self, is_read_only: bool):
        print(f"[DEBUG] ImportView.set_read_only: {is_read_only}")
        self.is_read_only = is_read_only
        if is_read_only:
            self.drop_zone.select_folder_button.setEnabled(False)
            self.drop_zone.select_folder_button.setToolTip("Database in sola lettura")
            self.drop_zone.setToolTip("Database in sola lettura")
            self.drop_zone.setAcceptDrops(False)
            self.drop_zone.setStyleSheet("QFrame#drop_zone { background-color: #F3F4F6; border: 2px solid #D1D5DB; }")
            self.results_display.setText("⚠️ Importazione disabilitata in modalità Sola Lettura.")
        else:
            self.drop_zone.select_folder_button.setEnabled(True)
            self.drop_zone.select_folder_button.setToolTip("")
            self.drop_zone.setToolTip("")
            self.drop_zone.setAcceptDrops(True)
            self.drop_zone.update_style("#FFFFFF", "#E5E7EB", "solid")
            if self.results_display.toPlainText() == "⚠️ Importazione disabilitata in modalità Sola Lettura.":
                self.results_display.clear()

    def resizeEvent(self, event):
        # Resize overlay when view resizes
        if self.loading_overlay.isVisible():
             self.loading_overlay.resize(self.size())
        super().resizeEvent(event)

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Seleziona Cartella")
        if folder_path:
            self.upload_path(folder_path)

    def upload_path(self, path):
        """
        Handles both single file path and directory path.
        """
        if getattr(self, 'is_read_only', False):
            QMessageBox.warning(self, "Sola Lettura", "Non puoi caricare file in modalità Sola Lettura.")
            return

        files_to_process = []
        if os.path.isfile(path):
             if path.lower().endswith('.pdf'):
                 files_to_process.append(path)
        elif os.path.isdir(path):
             for f in os.listdir(path):
                 if f.lower().endswith('.pdf'):
                     files_to_process.append(os.path.join(path, f))

        if files_to_process:
            self.process_dropped_files(files_to_process)
        else:
            self.results_display.setText("Nessun file PDF trovato nel percorso specificato.")

    def process_dropped_files(self, file_paths):
        self.results_display.clear()
        if not file_paths:
            self.results_display.setText("Nessun file PDF trovato.")
            return

        self.results_display.setText(f"Trovati {len(file_paths)} file PDF. Inizio elaborazione...")
        self.progress_container.setVisible(True)
        self.stop_button.setEnabled(True)
        self.drop_zone.setEnabled(False)

        self.thread = QThread()
        self.worker = PdfWorker(file_paths, self.api_client)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_processing_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.log_message.connect(self.results_display.append)
        self.worker.status_update.connect(self.etr_label.setText)

        # Connect progress to a progress bar if you have one
        # self.worker.progress.connect(self.progress_bar.setValue)

        self.thread.start()

    def stop_processing(self):
        if self.worker:
            self.worker.stop()
            self.stop_button.setText("Interruzione in corso...")
            self.stop_button.setEnabled(False)

    def on_processing_finished(self):
        self.etr_label.setText("Elaborazione completata.")
        self.stop_button.setText("Interrompi Analisi")
        self.stop_button.setEnabled(False)
        self.progress_container.setVisible(False)
        self.drop_zone.setEnabled(True)

        self.worker = None
        self.thread = None

        self.import_completed.emit()
