
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QFileDialog, QLabel, QFrame, QSizePolicy, QHBoxLayout, QProgressBar
from PyQt6.QtCore import QThread, pyqtSignal, QObject, Qt, QVariantAnimation, QSize
from PyQt6.QtGui import QIcon, QColor
import requests
import os
import shutil
from datetime import datetime
from app.utils.file_security import sanitize_filename
from ..components.toast import ToastManager
from ..api_client import APIClient
from ..components.animated_widgets import LoadingOverlay
from ..components.visuals import HolographicScanner
from ..workers.file_scanner_worker import FileScannerWorker
from desktop_app.constants import DATE_FORMAT_FILE, DIR_ANALYSIS_ERRORS

import time
from collections import deque

class PdfWorker(QObject):
    finished = pyqtSignal(int, int) # archived_count, verify_count
    progress = pyqtSignal(int)
    log_message = pyqtSignal(str, str)  # Message, Color
    status_update = pyqtSignal(str)
    etr_update = pyqtSignal(str)

    def __init__(self, file_paths, api_client, output_folder):
        super().__init__()
        self.file_paths = file_paths
        self.api_client = api_client
        self.output_folder = output_folder
        self._is_stopped = False
        self.recent_times = deque(maxlen=5)
        
        # Stats
        self.archived_count = 0
        self.verify_count = 0

    def stop(self):
        self._is_stopped = True

    def run(self):
        total_files = len(self.file_paths)
        # S1481: Unused processed_files removed
        for i, file_path in enumerate(self.file_paths):
            if self._is_stopped:
                self.log_message.emit("Processo interrotto dall'utente.", "orange")
                break

            self.status_update.emit(f"File {i+1} di {total_files}...")

            file_start_time = time.time()
            self.process_pdf(file_path)
            duration = time.time() - file_start_time
            self.recent_times.append(duration)

            self.progress.emit(i + 1)

            # ETR calculation (Rolling Average)
            if self.recent_times:
                avg_time_per_file = sum(self.recent_times) / len(self.recent_times)
                remaining_files = total_files - (i + 1)
                etr_seconds = remaining_files * avg_time_per_file

                if etr_seconds > 120:
                    etr_str = f"Circa {round(etr_seconds / 60)} minuti rimanenti"
                elif etr_seconds > 60:
                    etr_str = "Circa 1 minuto rimanente"
                else:
                    etr_str = f"Circa {int(etr_seconds)} secondi rimanenti"
                self.etr_update.emit(etr_str)

        self.finished.emit(self.archived_count, self.verify_count)

    def _process_single_cert(self, original_filename, data, source_path):
        # S3776: Helper function to reduce Cognitive Complexity
        self.verify_count += 1

        error_category = "ALTRI ERRORI"
        # S1481: Unused local variable 'reason' removed

        # Determine category and paths
        try:
            nome_completo = data.get('nome') or 'SCONOSCIUTO'
            matricola = data.get('matricola') or 'N-A'
            categoria = data.get('categoria') or 'ALTRO'

            data_scadenza_str = data.get('data_scadenza')
            stato = 'STORICO'
            file_scadenza = "no scadenza"

            if not data_scadenza_str:
                 stato = 'ATTIVO'
            else:
                try:
                    # S1192: Use constant DATE_FORMAT_DMY if imported, but DATE_FORMAT_FILE is used below.
                    # We define a local constant or import it if widely used.
                    # Since this file has imports, we should check imports.
                    # desktop_app/views/import_view.py doesn't import DATE_FORMAT_DMY.
                    # We will use the literal here for now or extract.
                    scadenza_date = datetime.strptime(data_scadenza_str, '%d/%m/%Y').date() # NOSONAR
                    file_scadenza = scadenza_date.strftime(DATE_FORMAT_FILE)

                    from app.core.config import settings
                    threshold = settings.ALERT_THRESHOLD_DAYS

                    # S1871: Merged duplicate branches
                    if (scadenza_date - datetime.now().date()).days > threshold or scadenza_date >= datetime.now().date():
                        stato = 'ATTIVO'
                except ValueError:
                     pass

            nome_fs = sanitize_filename(nome_completo)
            matricola_fs = sanitize_filename(str(matricola))
            categoria_fs = sanitize_filename(categoria)

            employee_folder_name = f"{nome_fs} ({matricola_fs})"
            new_filename = f"{nome_fs} ({matricola_fs}) - {categoria_fs} - {file_scadenza}.pdf"

            return True, error_category, employee_folder_name, categoria_fs, stato, new_filename
        except Exception as e:
            self.log_message.emit(f"Errore nella creazione struttura standard per errore: {e}. Fallback...", "red")
            return False, None, None, None, None, None

    def _handle_successful_save(self, cert_data, original_filename, certificato, current_op_path):
        """Helper to handle successful save (200 OK) logic."""
        ragione_fallimento = cert_data.get('assegnazione_fallita_ragione')

        if ragione_fallimento:
            log_msg = f"File {original_filename} ({certificato['categoria']}). Assegnazione manuale richiesta: {ragione_fallimento}"
            self.log_message.emit(log_msg, "orange")
            self.move_to_error(ragione_fallimento, cert_data, source_path=current_op_path)
            return

        nome_completo = cert_data.get('nome', 'ERRORE')
        self.log_message.emit(f"File {original_filename} ({certificato['categoria']}) salvato per {nome_completo}.", "default")
        try:
            self._move_to_success_folder(cert_data, current_op_path)
            self.archived_count += 1
        except Exception as e:
            self.log_message.emit(f"Errore durante lo spostamento del file {original_filename}: {e}", "red")
            self.move_to_error(f"Errore Spostamento: {e}", cert_data, source_path=current_op_path)

    def _move_to_success_folder(self, cert_data, current_op_path):
        """Helper to move file to the correct success folder."""
        matricola = cert_data.get('matricola') if cert_data.get('matricola') else 'N-A'
        categoria = cert_data.get('categoria', 'CATEGORIA_NON_TROVATA')
        nome_completo = cert_data.get('nome', 'ERRORE')

        data_scadenza_str = cert_data.get('data_scadenza')
        stato = 'STORICO'
        if not data_scadenza_str:
            stato = 'ATTIVO'
            file_scadenza = "no scadenza"
        else:
            scadenza_date = datetime.strptime(data_scadenza_str, '%d/%m/%Y').date()
            if scadenza_date >= datetime.now().date():
                stato = 'ATTIVO'
            file_scadenza = scadenza_date.strftime(DATE_FORMAT_FILE)

        nome_fs = sanitize_filename(nome_completo)
        matricola_fs = sanitize_filename(str(matricola))
        categoria_fs = sanitize_filename(categoria)

        employee_folder_name = f"{nome_fs} ({matricola_fs})"
        new_filename = f"{nome_fs} ({matricola_fs}) - {categoria_fs} - {file_scadenza}.pdf"

        documenti_folder = os.path.join(self.output_folder, "DOCUMENTI DIPENDENTI")
        dest_path = os.path.join(documenti_folder, employee_folder_name, categoria_fs, stato)
        os.makedirs(dest_path, exist_ok=True)

        shutil.move(current_op_path, os.path.join(dest_path, new_filename))

    def _handle_save_response(self, save_response, original_filename, certificato, current_op_path):
        # S3776: Refactored logic to reduce complexity
        if save_response.status_code == 200:
            self._handle_successful_save(save_response.json(), original_filename, certificato, current_op_path)
        elif save_response.status_code == 409:
            self._handle_conflict(original_filename, certificato, current_op_path)
        else:
            self._handle_general_error(save_response, original_filename, certificato, current_op_path)

    def _handle_conflict(self, original_filename, certificato, current_op_path):
        """Handle 409 Conflict."""
        self.log_message.emit(f"{original_filename} ({certificato['categoria']}) - Già in Database.", "orange")
        self.move_to_error("Già in Database", certificato, source_path=current_op_path)

    def _handle_general_error(self, save_response, original_filename, certificato, current_op_path):
        """Handle non-200/409 errors."""
        self.log_message.emit(f"Errore durante il salvaggio di {original_filename}: {save_response.text}", "red")
        self.move_to_error(f"Errore Salvaggio: {save_response.text}", certificato, source_path=current_op_path)

    def move_to_error(self, reason="Errore Generico", data=None, source_path=None):
        # Refactored to use helper logic
        if source_path is None: source_path = self.current_file_path # Use instance var if not passed

        error_category = "ALTRI ERRORI"
        if reason and "matricola" in reason.lower():
            error_category = "ASSENZA MATRICOLE"
        elif reason and "categoria" in reason.lower():
            error_category = "CATEGORIA NON TROVATA"
        elif reason and "database" in reason.lower():
             error_category = "DUPLICATI"

        if data:
            # S1481: Unused 'err_cat_override' replaced with _
            success, _, emp_folder, cat_fs, status, new_name = self._process_single_cert(os.path.basename(source_path), data, source_path)
            if success:
                target_dir = os.path.join(self.output_folder, DIR_ANALYSIS_ERRORS, error_category, emp_folder, cat_fs, status)
                os.makedirs(target_dir, exist_ok=True)
                shutil.move(source_path, os.path.join(target_dir, new_name))
                return

        # Case 2: No Data (or Fallback)
        filename_no_ext = os.path.splitext(os.path.basename(source_path))[0]
        target_dir = os.path.join(self.output_folder, DIR_ANALYSIS_ERRORS, error_category, filename_no_ext)
        os.makedirs(target_dir, exist_ok=True)

        try:
            shutil.move(source_path, os.path.join(target_dir, os.path.basename(source_path)))
        except Exception as e:
            self.log_message.emit(f"Impossibile spostare il file {os.path.basename(source_path)}: {e}", "red")

    def _prepare_certificates(self, entities):
        """Prepares a list of certificates to process from the extracted entities."""
        from app.utils.date_parser import parse_date_flexible
        
        data_rilascio_raw = entities.get('data_rilascio', '')
        data_scadenza_raw = entities.get('data_scadenza', '')
        data_nascita_raw = entities.get('data_nascita', '')

        def normalize_date(d_str):
            if not d_str: return ''
            d_obj = parse_date_flexible(d_str)
            return d_obj.strftime('%d/%m/%Y') if d_obj else d_str

        data_rilascio_norm = normalize_date(data_rilascio_raw)
        data_scadenza_norm = normalize_date(data_scadenza_raw)
        data_nascita_norm = normalize_date(data_nascita_raw)

        base_cert = {
            "nome": entities.get('nome', ''),
            "corso": entities.get('corso', ''),
            "categoria": entities.get('categoria', 'ALTRO'),
            "data_rilascio": data_rilascio_norm,
            "data_scadenza": data_scadenza_norm,
            "data_nascita": data_nascita_norm
        }

        certs_to_process = []
        corso_raw = entities.get('corso', '')
        categoria_raw = entities.get('categoria', 'ALTRO')

        if categoria_raw == "NOMINA" and corso_raw and \
           "antincendio" in corso_raw.lower() and "primo soccorso" in corso_raw.lower():
            c1 = base_cert.copy()
            c1["categoria"] = "ANTINCENDIO"
            certs_to_process.append(c1)

            c2 = base_cert.copy()
            c2["categoria"] = "PRIMO SOCCORSO"
            certs_to_process.append(c2)
        else:
            certs_to_process.append(base_cert)
            
        return certs_to_process

    def process_pdf(self, file_path):
        original_filename = os.path.basename(file_path)
        self.current_file_path = file_path # Store for fallback

        try:
            with open(file_path, 'rb') as f:
                files = {'file': (original_filename, f, 'application/pdf')}
                response = requests.post(f"{self.api_client.base_url}/upload-pdf/", files=files, headers=self.api_client._get_headers(), timeout=300)

            if response.status_code == 200:
                data = response.json()
                entities = data.get('entities', {})
                certs_to_process = self._prepare_certificates(entities)

                for idx, certificato in enumerate(certs_to_process):
                    current_op_path = file_path
                    if idx < len(certs_to_process) - 1:
                        current_op_path = f"{file_path}_copy_{idx}.pdf"
                        shutil.copy2(file_path, current_op_path)

                    save_response = requests.post(f"{self.api_client.base_url}/certificati/", json=certificato, headers=self.api_client._get_headers(), timeout=30)
                    self._handle_save_response(save_response, original_filename, certificato, current_op_path)

            elif response.status_code == 422:
                try:
                    error_detail = response.json().get("detail", "")
                    if "REJECTED" in str(error_detail):
                        self.log_message.emit(f"File scartato (Generico/Syllabus): {original_filename}", "orange")
                        target_dir = os.path.join(self.output_folder, DIR_ANALYSIS_ERRORS, "SCARTATI")
                        os.makedirs(target_dir, exist_ok=True)
                        try:
                            shutil.move(file_path, os.path.join(target_dir, original_filename))
                            txt_filename = os.path.splitext(original_filename)[0] + ".txt"
                            txt_path = os.path.join(target_dir, txt_filename)
                            try:
                                with open(txt_path, "w", encoding="utf-8") as f:
                                    f.write(f"File: {original_filename}\n")
                                    f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                                    f.write(f"Motivo Scarto: {error_detail}\n")
                            except Exception as txt_err:
                                self.log_message.emit(f"Impossibile creare file TXT per scarto: {txt_err}", "orange")
                        except Exception as e:
                            self.log_message.emit(f"Impossibile spostare il file scartato {original_filename}: {e}", "red")
                        return
                except Exception:
                    pass

                self.log_message.emit(f"Errore durante l'elaborazione di {original_filename}: {response.text}", "red")
                self.move_to_error(f"Errore Analisi: {response.text}")

            else:
                self.log_message.emit(f"Errore durante l'elaborazione di {original_filename}: {response.text}", "red")
                self.move_to_error(f"Errore Analisi: {response.text}")
        except (requests.exceptions.RequestException, IOError) as e:
            self.log_message.emit(f"Errore critico durante l'elaborazione di {original_filename}: {e}", "red")
            self.move_to_error(f"Errore Critico: {e}")

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

        urls = event.mimeData().urls()
        if urls:
            # Bug 1 Fix: Offload scanning to thread
            self.parent().scan_dropped_files(urls)

class ImportView(QWidget):
    import_completed = pyqtSignal(int, int) # archived, verify
    notification_requested = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.api_client = APIClient()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        description = QLabel("Carica, analizza ed estrai automaticamente le informazioni dai tuoi documenti. (Max 20MB per file)")
        description.setStyleSheet("font-size: 16px; color: #6B7280;")
        self.layout.addWidget(description)

        # --- Holographic Scanner Area ---
        self.scanner = HolographicScanner(self)
        self.scanner.setVisible(False)
        self.layout.addWidget(self.scanner)

        # --- Control & Progress Area ---
        self.progress_frame = QFrame()
        progress_layout = QHBoxLayout(self.progress_frame)
        progress_layout.setContentsMargins(10, 5, 10, 5)

        v_layout = QVBoxLayout()
        v_layout.setSpacing(0)
        self.status_label = QLabel("Pronto.")
        self.etr_label = QLabel("")
        self.etr_label.setStyleSheet("color: #6B7280; font-size: 12px;")
        v_layout.addWidget(self.status_label)
        v_layout.addWidget(self.etr_label)
        progress_layout.addLayout(v_layout, 1)

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedWidth(200)
        progress_layout.addWidget(self.progress_bar)

        self.stop_button = QPushButton("Stop")
        self.stop_button.setObjectName("destructive")
        self.stop_button.setFixedWidth(80)
        self.stop_button.clicked.connect(self.stop_processing)
        progress_layout.addWidget(self.stop_button)

        self.progress_frame.setVisible(False)
        self.layout.addWidget(self.progress_frame)

        self.drop_zone = DropZone(self)
        self.drop_zone.select_folder_button.clicked.connect(self.select_folder)
        self.layout.addWidget(self.drop_zone, 1)

        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        self.results_display.setObjectName("card")
        self.results_display.setStyleSheet("font-family: 'Consolas', 'Menlo', monospace; background-color: #FFFFFF; color: #4B5563; border-radius: 12px; font-size: 13px; padding: 10px; border: 1px solid #E5E7EB;")
        self.layout.addWidget(self.results_display, 1)

    def set_read_only(self, is_read_only: bool):
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

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Seleziona Cartella")
        if folder_path:
            self.upload_path(folder_path)

    def upload_path(self, path):
        if getattr(self, 'is_read_only', False):
            return
        files_to_process = []
        if os.path.isfile(path) and path.lower().endswith('.pdf'):
            files_to_process.append(path)
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.lower().endswith('.pdf'):
                        files_to_process.append(os.path.join(root, file))
        if files_to_process:
            self.process_dropped_files(files_to_process)

    def scan_dropped_files(self, urls):
        self.results_display.clear()
        self.status_label.setText("Scansione file in corso...")
        self.progress_frame.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setRange(0, 0) # Indeterminate while scanning
        self.drop_zone.setEnabled(False)

        self.scanner_thread = FileScannerWorker(urls)
        self.scanner_thread.finished.connect(self.on_scan_finished)
        self.scanner_thread.finished.connect(self.scanner_thread.deleteLater)
        self.scanner_thread.start()

    def on_scan_finished(self, file_paths):
        self.drop_zone.setEnabled(True)
        self.progress_bar.setRange(0, 100) # Reset range
        self.progress_bar.setValue(0)
        self.process_dropped_files(file_paths)

    def process_dropped_files(self, file_paths):
        self.results_display.clear()
        if not file_paths:
            self.status_label.setText("Nessun file PDF trovato.")
            self.progress_frame.setVisible(False)
            return

        # Get Output Path
        try:
            paths = self.api_client.get_paths()
            output_folder = paths.get("database_path")
        except Exception as e:
            self.results_display.setTextColor(QColor("#DC2626"))
            self.results_display.append(f"Errore critico: Impossibile recuperare il percorso del database. {e}")
            return

        if not output_folder or not os.path.isdir(output_folder):
             self.results_display.setTextColor(QColor("#DC2626"))
             self.results_display.append(f"Errore critico: Percorso database non valido: {output_folder}")
             return

        # Configure and show progress bar
        self.progress_bar.setMaximum(len(file_paths))
        self.progress_bar.setValue(0)
        self.status_label.setText("Inizio elaborazione...")
        self.etr_label.setText("")
        self.stop_button.setText("Stop")
        self.stop_button.setEnabled(True)
        self.progress_frame.setVisible(True)
        self.scanner.setVisible(True) # Show Hologram

        self.thread = QThread()
        self.worker = PdfWorker(file_paths, self.api_client, output_folder)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_processing_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.log_message.connect(self.append_log_message)

        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.status_update.connect(self.status_label.setText)
        self.worker.etr_update.connect(self.etr_label.setText)

        self.thread.start()

    def stop_processing(self):
        if hasattr(self, 'thread') and self.thread.isRunning():
            self.worker.stop()
            self.stop_button.setText("Fermando...")
            self.stop_button.setEnabled(False)

    def append_log_message(self, message, color):
        color_map = {
            "red": "#DC2626",
            "orange": "#F97316",
            "default": "#4B5563"
        }
        self.results_display.setTextColor(QColor(color_map.get(color, color_map["default"])))
        self.results_display.append(message)
        self.results_display.setTextColor(QColor(color_map["default"])) # Reset

    def on_processing_finished(self, archived_count, verify_count):
        self.status_label.setText("Elaborazione completata.")
        self.etr_label.setText("")
        self.stop_button.setVisible(False)
        self.scanner.setVisible(False) # Hide Hologram
        self.import_completed.emit(archived_count, verify_count)
        # self.notification_requested.emit("Analisi Completata", ...) # Replaced by Toast
        ToastManager.success("Analisi Completata", f"L'elaborazione è terminata. {archived_count} archiviati, {verify_count} da verificare.", self.window())

    def cleanup(self):
        """
        Gracefully stops the worker thread if running.
        """
        if hasattr(self, 'thread') and self.thread.isRunning():
            print("[ImportView] Stopping worker thread...")
            self.status_label.setText("Arresto in corso...")
            self.worker.stop()
            self.thread.quit()
            # Wait for thread to finish (with timeout to prevent hanging)
            if not self.thread.wait(3000):  # 3 seconds timeout
                print("[ImportView] Thread did not finish in time. Terminating...")
                self.thread.terminate()
            print("[ImportView] Thread stopped.")

    def closeEvent(self, event):
        self.cleanup()
        super().closeEvent(event)
