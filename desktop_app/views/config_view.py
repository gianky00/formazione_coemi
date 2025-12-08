import json
import traceback
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QFrame, QFormLayout, QComboBox, QFileDialog, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QDialog, QDialogButtonBox, QCheckBox,
    QStackedWidget, QHeaderView, QDateEdit
)
from PyQt6.QtCore import Qt, QDate, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QColor
from desktop_app.api_client import APIClient
from app.utils.security import obfuscate_string, reveal_string
from desktop_app.components.custom_dialog import CustomMessageDialog
from desktop_app.components.toast import ToastManager
from desktop_app.constants import LABEL_OPTIMIZE_DB

class ChangePasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Modifica Password Personale")
        self.resize(400, 250)
        self.layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        self.old_password = QLineEdit()
        self.old_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)

        form_layout.addRow("Password Attuale:", self.old_password)
        form_layout.addRow("Nuova Password:", self.new_password)
        form_layout.addRow("Conferma Password:", self.confirm_password)
        self.layout.addLayout(form_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout.addWidget(buttons)

    def get_data(self):
        return {
            "old_password": self.old_password.text(),
            "new_password": self.new_password.text(),
            "confirm_password": self.confirm_password.text()
        }

class UserDialog(QDialog):
    def __init__(self, parent=None, user_data=None):
        super().__init__(parent)
        self.setWindowTitle("Nuovo Utente" if not user_data else "Modifica Utente")
        self.resize(500, 350)
        self.layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        self.username_input = QLineEdit()
        self.account_name_input = QLineEdit()
        self.gender_combo = QComboBox()
        self.gender_combo.addItem("Non specificato", None)
        self.gender_combo.addItem("Uomo", "M")
        self.gender_combo.addItem("Donna", "F")

        self.is_admin_check = QCheckBox("Amministratore")

        self.user_data = user_data

        if user_data:
            self.username_input.setText(user_data.get('username', ''))
            self.account_name_input.setText(user_data.get('account_name', ''))
            self.is_admin_check.setChecked(user_data.get('is_admin', False))

            gender = user_data.get('gender')
            index = self.gender_combo.findData(gender)
            if index >= 0:
                self.gender_combo.setCurrentIndex(index)

            self.password_input = QLineEdit()
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.password_input.setPlaceholderText("Lascia vuoto per mantenere attuale")
        else:
            self.password_info = QLabel("Password di default: <b>primoaccesso</b>")
            self.password_info.setStyleSheet("color: gray;")

        form_layout.addRow("Nome Utente:", self.username_input)
        form_layout.addRow("Nome Account (es. Mario Rossi):", self.account_name_input)
        form_layout.addRow("Sesso:", self.gender_combo)

        if user_data:
            form_layout.addRow("Nuova Password (Admin Reset):", self.password_input)
        else:
            form_layout.addRow("", self.password_info)

        form_layout.addRow("", self.is_admin_check)
        self.layout.addLayout(form_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout.addWidget(buttons)

    def get_data(self):
        data = {
            "username": self.username_input.text(),
            "account_name": self.account_name_input.text(),
            "gender": self.gender_combo.currentData(),
            "is_admin": self.is_admin_check.isChecked()
        }
        if self.user_data:
            data["password"] = self.password_input.text()
        else:
            data["password"] = None
        return data

class UserManagementWidget(QFrame):
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.setObjectName("card")
        self.layout = QVBoxLayout(self)

        self.title = QLabel("Gestione Utenti")
        self.title.setStyleSheet("font-size: 16px; font-weight: 600;")
        self.layout.addWidget(self.title)

        # --- ADMIN SECTION ---
        self.admin_container = QWidget()
        admin_layout = QVBoxLayout(self.admin_container)
        admin_layout.setContentsMargins(0, 10, 0, 10)

        header = QHBoxLayout()
        header.addStretch()
        self.add_btn = QPushButton("Nuovo Utente")
        self.add_btn.setObjectName("secondary")
        self.add_btn.clicked.connect(self.add_user)
        header.addWidget(self.add_btn)
        admin_layout.addLayout(header)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Nome Utente", "Nome Account", "Admin"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        admin_layout.addWidget(self.table)

        actions_layout = QHBoxLayout()
        self.edit_btn = QPushButton("Modifica / Reset Password")
        self.edit_btn.clicked.connect(self.edit_user)
        actions_layout.addWidget(self.edit_btn)
        self.delete_btn = QPushButton("Elimina")
        self.delete_btn.setObjectName("destructive")
        self.delete_btn.clicked.connect(self.delete_user)
        actions_layout.addWidget(self.delete_btn)
        admin_layout.addLayout(actions_layout)

        self.layout.addWidget(self.admin_container)

        # --- COMMON SECTION (Change own password) ---
        self.layout.addWidget(QLabel("")) # Spacer

        personal_section = QFrame()
        personal_section.setObjectName("card_inner")
        personal_layout = QHBoxLayout(personal_section)

        lbl = QLabel("Sicurezza Account:")
        lbl.setStyleSheet("font-weight: bold;")
        personal_layout.addWidget(lbl)
        personal_layout.addStretch()

        self.change_pw_btn = QPushButton("Modifica Password Personale")
        self.change_pw_btn.clicked.connect(self.change_own_password)
        personal_layout.addWidget(self.change_pw_btn)

        self.layout.addWidget(personal_section)
        self.layout.addStretch()

    def refresh_users(self):
        is_admin = self.api_client.user_info.get("is_admin", False)
        self.admin_container.setVisible(is_admin)
        self.title.setText("Gestione Utenti" if is_admin else "Il Mio Account")

        if is_admin:
            try:
                users = self.api_client.get_users()
                self.table.setRowCount(len(users))
                for i, user in enumerate(users):
                    id_item = QTableWidgetItem(str(user['id']))
                    id_item.setData(Qt.ItemDataRole.UserRole, user)
                    self.table.setItem(i, 0, id_item)
                    self.table.setItem(i, 1, QTableWidgetItem(str(user['username'])))
                    self.table.setItem(i, 2, QTableWidgetItem(str(user.get('account_name', ''))))
                    self.table.setItem(i, 3, QTableWidgetItem("Sì" if user['is_admin'] else "No"))
            except Exception:
                pass

    def add_user(self):
        dialog = UserDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if not data['username']:
                CustomMessageDialog.show_warning(self, "Errore", "Il nome utente è obbligatorio.")
                return
            try:
                self.api_client.create_user(
                    data['username'], data['password'],
                    data['account_name'], data['is_admin'], data['gender']
                )
                self.refresh_users()
            except Exception as e:
                CustomMessageDialog.show_error(self, "Errore", str(e))

    def get_selected_user_id(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows: return None
        return int(self.table.item(rows[0].row(), 0).text())

    def _prepare_update_payload(self, data, user_data):
        update_payload = {}
        if data['username'] != user_data['username']: update_payload['username'] = data['username']
        if data['account_name'] != user_data.get('account_name'): update_payload['account_name'] = data['account_name']
        if data['gender'] != user_data.get('gender'): update_payload['gender'] = data['gender']
        if data['is_admin'] != user_data['is_admin']: update_payload['is_admin'] = data['is_admin']
        if data.get('password'): update_payload['password'] = data['password']
        return update_payload

    def edit_user(self):
        user_id = self.get_selected_user_id()
        if not user_id: return

        user_data = self.table.item(self.table.currentRow(), 0).data(Qt.ItemDataRole.UserRole)
        if not user_data: return

        dialog = UserDialog(self, user_data)
        if dialog.exec():
            data = dialog.get_data()
            update_payload = self._prepare_update_payload(data, user_data)

            if not update_payload: return
            try:
                self.api_client.update_user(user_id, update_payload)
                self.refresh_users()
            except Exception as e:
                CustomMessageDialog.show_error(self, "Errore", str(e))

    def _validate_change_password(self, data):
        """Validates password change inputs."""
        if not data['old_password'] or not data['new_password']:
            CustomMessageDialog.show_warning(self, "Errore", "Tutti i campi sono obbligatori.")
            return False

        if data['new_password'] != data['confirm_password']:
            CustomMessageDialog.show_warning(self, "Errore", "Le nuove password non corrispondono.")
            return False
        return True

    def change_own_password(self):
        # S3776: Refactored to reduce complexity
        dialog = ChangePasswordDialog(self)
        if not dialog.exec():
            return

        data = dialog.get_data()
        if not self._validate_change_password(data):
            return

        try:
            response = self.api_client.change_password(data['old_password'], data['new_password'])
            CustomMessageDialog.show_info(self, "Successo", response.get("message", "Password aggiornata."))
        except Exception as e:
            # S5754: Re-raise handled exception or swallow intentionally?
            try:
                if hasattr(e, 'response') and e.response is not None:
                    err_json = e.response.json()
                    detail = err_json.get('detail', str(e))
                    CustomMessageDialog.show_error(self, "Errore", "Errore: " + detail)
                else:
                    CustomMessageDialog.show_error(self, "Errore", str(e))
            except Exception as inner_e:
                # S5754: Handle exception properly
                CustomMessageDialog.show_error(self, "Errore Critico", f"Errore: {e}\n(Dettagli: {inner_e})")

    def delete_user(self):
        user_id = self.get_selected_user_id()
        if not user_id: return
        if user_id == self.api_client.user_info.get("id"):
            CustomMessageDialog.show_warning(self, "Azione Non Consentita", "Non puoi eliminare il tuo account.")
            return
        if CustomMessageDialog.show_question(self, "Conferma", "Eliminare questo utente?"):
            try:
                self.api_client.delete_user(user_id)
                self.refresh_users()
            except Exception as e:
                CustomMessageDialog.show_error(self, "Errore", str(e))

class OptimizeWorker(QThread):
    finished = pyqtSignal(dict) # result
    error = pyqtSignal(str)

    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client

    def run(self):
        try:
            import requests
            url = f"{self.api_client.base_url}/system/optimize"
            headers = self.api_client._get_headers()
            start = datetime.now()
            response = requests.post(url, headers=headers, timeout=300) # Increased timeout
            duration = (datetime.now() - start).total_seconds()

            if response.status_code == 200:
                res = response.json()
                res['duration'] = duration
                self.finished.emit(res)
            else:
                self.error.emit(f"Errore server: {response.text}")
        except Exception as e:
            self.error.emit(str(e))

class DatabaseSettingsWidget(QFrame):
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.setObjectName("card")
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)
        self.form_layout = QFormLayout()
        self.form_layout.setSpacing(15)
        self.form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)

        self.layout.addWidget(QLabel("<b>Impostazioni Database</b>"))

        self.db_path_input = QLineEdit()
        self.db_path_input.setReadOnly(True)
        self.browse_db_path_button = QPushButton("Sfoglia / Crea...")
        db_path_layout = QHBoxLayout()
        db_path_layout.addWidget(self.db_path_input)
        db_path_layout.addWidget(self.browse_db_path_button)
        self.form_layout.addRow(QLabel("Percorso Database:"), db_path_layout)

        # Maintenance Section
        maint_separator = QFrame()
        maint_separator.setFrameShape(QFrame.Shape.HLine)
        maint_separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.form_layout.addRow(maint_separator)

        # S1192: Use constant
        self.optimize_btn = QPushButton(LABEL_OPTIMIZE_DB)
        self.optimize_btn.setToolTip("Esegue VACUUM e ANALYZE per recuperare spazio e migliorare le prestazioni.")
        self.optimize_btn.clicked.connect(self.optimize_db)
        self.form_layout.addRow(QLabel("Manutenzione:"), self.optimize_btn)

        self.layout.addLayout(self.form_layout)
        self.layout.addStretch()

    def optimize_db(self):
        if CustomMessageDialog.show_question(self, "Conferma Ottimizzazione", "Questa operazione potrebbe richiedere del tempo. Continuare?"):
            ToastManager.info("Ottimizzazione Avviata", "L'operazione è in corso in background...", self.window())
            self.optimize_btn.setEnabled(False)
            self.optimize_btn.setText("Ottimizzazione in corso...")

            self.worker = OptimizeWorker(self.api_client)
            self.worker.finished.connect(self.on_optimize_finished)
            self.worker.error.connect(self.on_optimize_error)
            self.worker.start()

    def on_optimize_finished(self, result):
        self.optimize_btn.setEnabled(True)
        self.optimize_btn.setText(LABEL_OPTIMIZE_DB)
        duration = result.get('duration', 0)
        stats = result.get('sync_stats', {})
        moved = stats.get('moved', 0)
        missing = stats.get('missing', 0)

        msg = f"Completata in {duration:.1f}s.\nFile spostati: {moved}. File mancanti: {missing}."
        ToastManager.success("Ottimizzazione Completata", msg, self.window())

    def on_optimize_error(self, error):
        self.optimize_btn.setEnabled(True)
        self.optimize_btn.setText(LABEL_OPTIMIZE_DB)
        ToastManager.error("Errore Ottimizzazione", error, self.window())

class APISettingsWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)
        self.form_layout = QFormLayout()
        self.form_layout.setSpacing(15)
        self.form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)

        self.layout.addWidget(QLabel("<b>Configurazione API & AI</b>"))

        self.gemini_analysis_key_input = QLineEdit()
        self.gemini_analysis_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.form_layout.addRow(QLabel("API Gemini 2.5-pro (Analisi Documenti):"), self.gemini_analysis_key_input)

        self.gemini_chat_key_input = QLineEdit()
        self.gemini_chat_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.form_layout.addRow(QLabel("API Gemini 1.5-flash (Chatbot):"), self.gemini_chat_key_input)

        self.voice_assistant_check = QCheckBox("Abilita Assistente Vocale")
        self.form_layout.addRow("", self.voice_assistant_check)

        self.layout.addLayout(self.form_layout)
        self.layout.addStretch()

class EmailSettingsWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)
        self.form_layout = QFormLayout()
        self.form_layout.setSpacing(15)
        self.form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)

        self.layout.addWidget(QLabel("<b>Impostazioni Email (SMTP)</b>"))

        self.email_preset_combo = QComboBox()
        self.email_preset_combo.addItems(["Manuale", "Gmail", "Outlook", "COEMI"])
        self.form_layout.addRow(QLabel("Preset Email:"), self.email_preset_combo)
        self.smtp_host_input = QLineEdit()
        self.form_layout.addRow(QLabel("SMTP Host:"), self.smtp_host_input)
        self.smtp_port_input = QLineEdit()
        self.form_layout.addRow(QLabel("SMTP Port:"), self.smtp_port_input)
        self.smtp_user_input = QLineEdit()
        self.form_layout.addRow(QLabel("Utente SMTP (Email):"), self.smtp_user_input)
        self.smtp_password_input = QLineEdit()
        self.smtp_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.form_layout.addRow(QLabel("Password SMTP:"), self.smtp_password_input)
        self.recipients_to_input = QLineEdit()
        self.recipients_to_input.setPlaceholderText("Separati da virgola")
        self.form_layout.addRow(QLabel("Destinatari (To):"), self.recipients_to_input)
        self.recipients_cc_input = QLineEdit()
        self.recipients_cc_input.setPlaceholderText("Separati da virgola")
        self.form_layout.addRow(QLabel("Copia Conoscenza (CC):"), self.recipients_cc_input)

        self.layout.addLayout(self.form_layout)
        self.layout.addStretch()

class GeneralSettingsWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)
        self.form_layout = QFormLayout()
        self.form_layout.setSpacing(15)
        self.form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)

        self.layout.addWidget(QLabel("<b>Parametri Generali</b>"))

        self.alert_threshold_input = QLineEdit()
        self.alert_threshold_input.setPlaceholderText("Default: 60")
        self.form_layout.addRow(QLabel("Soglia Avviso (giorni):"), self.alert_threshold_input)
        self.alert_threshold_visite_input = QLineEdit()
        self.alert_threshold_visite_input.setPlaceholderText("Default: 30")
        self.form_layout.addRow(QLabel("Soglia Avviso Visite Mediche (giorni):"), self.alert_threshold_visite_input)

        self.layout.addLayout(self.form_layout)
        self.layout.addStretch()

class AuditLogWidget(QFrame):
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.setObjectName("card")
        self.layout = QVBoxLayout(self)
        header = QHBoxLayout()
        title = QLabel("Log Attività (Audit)")
        title.setStyleSheet("font-size: 16px; font-weight: 600;")
        header.addWidget(title)
        header.addStretch()

        self.export_btn = QPushButton("Esporta CSV")
        self.export_btn.setObjectName("secondary")
        self.export_btn.clicked.connect(self.export_logs)
        header.addWidget(self.export_btn)

        self.layout.addLayout(header)

        filter_layout = QHBoxLayout()
        self.user_filter = QComboBox()
        self.user_filter.addItem("Tutti gli utenti", None)
        filter_layout.addWidget(QLabel("Utente:"))
        filter_layout.addWidget(self.user_filter)
        self.category_filter = QComboBox()
        self.category_filter.addItem("Tutte le categorie", None)
        filter_layout.addWidget(QLabel("Categoria:"))
        filter_layout.addWidget(self.category_filter)
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("dd/MM/yyyy")
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("dd/MM/yyyy")
        self.end_date.setDate(QDate.currentDate())
        filter_layout.addWidget(QLabel("Dal:"))
        filter_layout.addWidget(self.start_date)
        filter_layout.addWidget(QLabel("Al:"))
        filter_layout.addWidget(self.end_date)

        filter_layout.addWidget(QLabel("Cerca:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cerca...")
        self.search_input.textChanged.connect(self._on_search_changed)
        filter_layout.addWidget(self.search_input)

        self.start_date.dateChanged.connect(self.refresh_logs)
        self.end_date.dateChanged.connect(self.refresh_logs)
        self.user_filter.currentIndexChanged.connect(self.refresh_logs)
        self.category_filter.currentIndexChanged.connect(self.refresh_logs)

        self.layout.addLayout(filter_layout)

        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(500)
        self.search_timer.timeout.connect(self.refresh_logs)

        # Bug 9 Fix: Search Request Counter for Race Condition
        self.last_search_req_id = 0

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Data/Ora", "Severità", "Utente", "Azione", "Categoria", "Dettagli"])
        header = self.table.horizontalHeader()
        for i in range(5):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.layout.addWidget(self.table)

    def refresh_filters(self):
        try:
            users = self.api_client.get_users()
            current_user = self.user_filter.currentData()
            self.user_filter.clear()
            self.user_filter.addItem("Tutti gli utenti", None)
            for user in users:
                self.user_filter.addItem(user['username'], user['id'])

            if current_user:
                idx = self.user_filter.findData(current_user)
                if idx >= 0:
                    self.user_filter.setCurrentIndex(idx)
        except Exception:
            pass

        try:
            cats = self.api_client.get_audit_categories()
            current_cat = self.category_filter.currentData()
            self.category_filter.clear()
            self.category_filter.addItem("Tutte le categorie", None)
            self.category_filter.addItems(cats)

            if current_cat:
                idx = self.category_filter.findData(current_cat)
                if idx >= 0:
                    self.category_filter.setCurrentIndex(idx)
        except Exception:
            pass

    def _on_search_changed(self):
        self.search_timer.start()

    def export_logs(self):
        try:
             import requests

             url = f"{self.api_client.base_url}/audit/export"
             headers = self.api_client._get_headers()

             # Use stream=True to handle large files if server supports it, though simple get works for file download
             response = requests.get(url, headers=headers, timeout=60, stream=True)
             if response.status_code == 200:
                 default_name = "audit_logs.csv"
                 if "Content-Disposition" in response.headers:
                     import re
                     fname = re.findall('filename="?([^"]+)"?', response.headers["Content-Disposition"])
                     if fname:
                         default_name = fname[0]

                 save_path, _ = QFileDialog.getSaveFileName(self, "Salva CSV Audit", default_name, "CSV Files (*.csv *.CSV)")
                 if save_path:
                     with open(save_path, "wb") as f:
                         for chunk in response.iter_content(chunk_size=8192):
                             f.write(chunk)
                     CustomMessageDialog.show_info(self, "Esportazione Riuscita", f"Log salvati in:\n{save_path}")
             else:
                 CustomMessageDialog.show_error(self, "Errore", f"Errore server: {response.status_code}")

        except Exception as e:
            CustomMessageDialog.show_error(self, "Errore Esportazione", str(e))

    def refresh_logs(self):
        user_id = self.user_filter.currentData()
        category = self.category_filter.currentData()
        search_text = self.search_input.text()

        # Helper to convert QDate to datetime/date for API
        start = self.start_date.date().toPyDate()
        end = self.end_date.date().toPyDate()

        # Increment request ID
        self.last_search_req_id += 1
        current_req_id = self.last_search_req_id

        try:
            logs = self.api_client.get_audit_logs(
                user_id=user_id,
                category=category,
                search=search_text,
                start_date=start,
                end_date=end
            )

            # Check for race condition
            if current_req_id != self.last_search_req_id:
                return

            self.table.setRowCount(0)
            self.table.setRowCount(len(logs))

            for i, log in enumerate(logs):
                # Columns: "Data/Ora", "Severità", "Utente", "Azione", "Categoria", "Dettagli"

                # Format timestamp (assuming ISO string from API)
                ts_str = log['timestamp']
                try:
                    # Basic ISO parsing
                    dt = datetime.fromisoformat(ts_str)
                    formatted_date = dt.strftime("%d/%m/%Y %H:%M:%S")
                except Exception: # S5754: Handle specific exception? ValueError for format
                    # S5754: Or fallback. S5754 says re-raise SystemExit. This catch-all is fine for formatting fallback.
                    # Adding comment as per best practice
                    # NOSONAR
                    formatted_date = ts_str

                self.table.setItem(i, 0, QTableWidgetItem(formatted_date))
                self.table.setItem(i, 1, QTableWidgetItem(log.get('severity', 'LOW')))
                self.table.setItem(i, 2, QTableWidgetItem(log.get('username', 'Unknown')))
                self.table.setItem(i, 3, QTableWidgetItem(log.get('action', '')))
                self.table.setItem(i, 4, QTableWidgetItem(log.get('category', '')))

                details_item = QTableWidgetItem(log.get('details', ''))
                details_item.setToolTip(log.get('changes') or log.get('details', '')) # Show full details/changes in tooltip
                self.table.setItem(i, 5, details_item)

                # Color code severity
                sev = log.get('severity', 'LOW')
                if sev == 'CRITICAL':
                    for col in range(6):
                        item = self.table.item(i, col)
                        item.setBackground(QColor("#FEE2E2")) # Red-ish
                        item.setForeground(QColor("#991B1B"))
                elif sev == 'MEDIUM':
                     for col in range(6):
                        item = self.table.item(i, col)
                        item.setBackground(QColor("#FEF3C7")) # Yellow-ish
                        item.setForeground(QColor("#92400E"))

        except Exception as e:
            # CustomMessageDialog.show_error(self, "Errore", f"Impossibile caricare i log: {e}")
            print(f"Error loading logs: {e}")

class ConfigView(QWidget):
    def __init__(self, api_client: APIClient):
        super().__init__()
        try:
            self.layout = QVBoxLayout(self)
            self.layout.setContentsMargins(20, 20, 20, 20)
            self.layout.setSpacing(15)
            self.api_client = api_client
            self.current_settings = {}
            self.unsaved_changes = False

            description = QLabel("Gestisci le impostazioni e le chiavi API dell'applicazione.")
            description.setObjectName("viewDescription")
            self.layout.addWidget(description)

            self.nav_container = QFrame()
            self.nav_layout = QHBoxLayout(self.nav_container)
            self.nav_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.nav_layout.setSpacing(10)

            self.btn_general = QPushButton("Generale")
            self.btn_general.setCheckable(True)
            self.btn_general.clicked.connect(lambda: self.switch_tab(0))

            self.btn_database = QPushButton("Database")
            self.btn_database.setCheckable(True)
            self.btn_database.clicked.connect(lambda: self.switch_tab(1))

            self.btn_api = QPushButton("API")
            self.btn_api.setCheckable(True)
            self.btn_api.clicked.connect(lambda: self.switch_tab(2))

            self.btn_email = QPushButton("Email")
            self.btn_email.setCheckable(True)
            self.btn_email.clicked.connect(lambda: self.switch_tab(3))

            self.btn_account = QPushButton("Account")
            self.btn_account.setCheckable(True)
            self.btn_account.clicked.connect(lambda: self.switch_tab(4))

            self.btn_audit = QPushButton("Log Attività")
            self.btn_audit.setCheckable(True)
            self.btn_audit.clicked.connect(lambda: self.switch_tab(5))

            self.nav_buttons = [
                self.btn_general, self.btn_database, self.btn_api,
                self.btn_email, self.btn_account, self.btn_audit
            ]

            for btn in self.nav_buttons:
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.setFixedWidth(130)
                self.nav_layout.addWidget(btn)

            self.layout.addWidget(self.nav_container)

            self.stacked_widget = QStackedWidget()

            # Init Sub-Widgets
            self.general_settings = GeneralSettingsWidget()
            self.database_settings = DatabaseSettingsWidget(self.api_client)
            self.api_settings = APISettingsWidget()
            self.email_settings = EmailSettingsWidget()
            self.user_management_widget = UserManagementWidget(self.api_client)
            self.audit_widget = AuditLogWidget(self.api_client)

            self.stacked_widget.addWidget(self.general_settings)       # 0
            self.stacked_widget.addWidget(self.database_settings)      # 1
            self.stacked_widget.addWidget(self.api_settings)           # 2
            self.stacked_widget.addWidget(self.email_settings)         # 3
            self.stacked_widget.addWidget(self.user_management_widget) # 4
            self.stacked_widget.addWidget(self.audit_widget)           # 5

            self.layout.addWidget(self.stacked_widget)

            self.bottom_buttons_frame = QFrame()
            bottom_layout = QHBoxLayout(self.bottom_buttons_frame)
            bottom_layout.setContentsMargins(0, 0, 0, 0)

            self.import_button = QPushButton("Importa Dipendenti da CSV")
            self.import_button.setObjectName("secondary")
            self.import_button.setToolTip("Formato CSV richiesto. Dimensione massima: 5MB.")
            self.import_button.clicked.connect(self.import_csv)

            self.save_button = QPushButton("Salva Modifiche")
            self.save_button.setObjectName("primary")
            self.save_button.clicked.connect(self.save_config)

            # Layout: [Import] [10px] [Save] [Stretch] -> Left aligned
            bottom_layout.addWidget(self.import_button)
            bottom_layout.addSpacing(10)
            bottom_layout.addWidget(self.save_button)
            bottom_layout.addStretch()

            self.layout.addWidget(self.bottom_buttons_frame)

            # Connections
            self.email_settings.email_preset_combo.currentIndexChanged.connect(self.apply_email_preset)
            self.database_settings.browse_db_path_button.clicked.connect(self.select_db_path)

            # Connect change signals for Unsaved Changes
            self._connect_dirty_signals()

        except Exception as e:
            print(f"CRITICAL ERROR in ConfigView.__init__: {e}")
            traceback.print_exc()
            # Fallback UI to prevent crash
            if not hasattr(self, 'layout') or self.layout is None:
                self.layout = QVBoxLayout(self)

            error_label = QLabel(f"Errore critico durante l'inizializzazione della vista Configurazione:\n{e}")
            error_label.setStyleSheet("color: red; font-weight: bold;")
            self.layout.addWidget(error_label)

    def _connect_dirty_signals(self):
        # General
        self.general_settings.alert_threshold_input.textChanged.connect(self.mark_dirty)
        self.general_settings.alert_threshold_visite_input.textChanged.connect(self.mark_dirty)

        # API
        self.api_settings.gemini_analysis_key_input.textChanged.connect(self.mark_dirty)
        self.api_settings.gemini_chat_key_input.textChanged.connect(self.mark_dirty)
        self.api_settings.voice_assistant_check.toggled.connect(self.mark_dirty)

        # Email
        self.email_settings.smtp_host_input.textChanged.connect(self.mark_dirty)
        self.email_settings.smtp_port_input.textChanged.connect(self.mark_dirty)
        self.email_settings.smtp_user_input.textChanged.connect(self.mark_dirty)
        self.email_settings.smtp_password_input.textChanged.connect(self.mark_dirty)
        self.email_settings.recipients_to_input.textChanged.connect(self.mark_dirty)
        self.email_settings.recipients_cc_input.textChanged.connect(self.mark_dirty)
        self.email_settings.email_preset_combo.currentIndexChanged.connect(self.mark_dirty)

        # DB (path)
        self.database_settings.db_path_input.textChanged.connect(self.mark_dirty)

    def mark_dirty(self):
        self.unsaved_changes = True

    def select_db_path(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Seleziona o Crea Database", "", "SQLite Database (*.db)")
        if file_path:
            self.database_settings.db_path_input.setText(file_path)

    def set_read_only(self, is_read_only: bool):
        self.is_read_only = is_read_only
        self.save_button.setEnabled(not is_read_only)
        self.import_button.setEnabled(not is_read_only)
        self.user_management_widget.add_btn.setEnabled(not is_read_only)
        self.user_management_widget.edit_btn.setEnabled(not is_read_only)
        self.user_management_widget.delete_btn.setEnabled(not is_read_only)
        self.save_button.setToolTip("Database in sola lettura" if is_read_only else "")

    def switch_tab(self, index):
        if self.unsaved_changes:
            if not CustomMessageDialog.show_question(self, "Modifiche non salvate", "Ci sono modifiche non salvate. Se cambi scheda andranno perse. Vuoi scartarle?"):
                # Revert selection visually
                current = self.stacked_widget.currentIndex()
                if current != -1 and current < len(self.nav_buttons):
                    self.nav_buttons[current].setChecked(True)
                    self.nav_buttons[index].setChecked(False)
                return
            else:
                self.unsaved_changes = False
                self.load_config() # Revert data

        self.stacked_widget.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

        # Show save button only on config tabs (0, 1, 2, 3)
        self.bottom_buttons_frame.setVisible(index <= 3)

        if index == 5: # Audit Log
            self.audit_widget.refresh_filters()

    def showEvent(self, event):
        super().showEvent(event)
        if self.api_client and self.api_client.user_info:
            is_admin = self.api_client.user_info.get("is_admin", False)

            # Show/Hide Admin Tabs
            for btn in [self.btn_general, self.btn_database, self.btn_api, self.btn_email, self.btn_audit]:
                btn.setVisible(is_admin)

            self.btn_account.setVisible(True)

            if is_admin:
                self.load_config()
                # Default to General tab for Admin
                if self.stacked_widget.currentIndex() == -1 or self.stacked_widget.currentIndex() == 4:
                     self.stacked_widget.setCurrentIndex(0)
                     for i, btn in enumerate(self.nav_buttons):
                         btn.setChecked(i == 0)
            else:
                # Default (and only) tab for User is Account (index 4)
                self.switch_tab(4)

            # Refresh user management widget (handles its own admin/user logic)
            self.user_management_widget.refresh_users()

    def load_config(self):
        try:
            # Block signals to prevent dirty marking during load
            self.general_settings.alert_threshold_input.blockSignals(True)
            self.general_settings.alert_threshold_visite_input.blockSignals(True)
            self.api_settings.gemini_analysis_key_input.blockSignals(True)
            self.api_settings.gemini_chat_key_input.blockSignals(True)
            self.api_settings.voice_assistant_check.blockSignals(True)
            self.email_settings.smtp_host_input.blockSignals(True)
            self.email_settings.smtp_port_input.blockSignals(True)
            self.email_settings.smtp_user_input.blockSignals(True)
            self.email_settings.smtp_password_input.blockSignals(True)
            self.email_settings.recipients_to_input.blockSignals(True)
            self.email_settings.recipients_cc_input.blockSignals(True)
            self.email_settings.email_preset_combo.blockSignals(True)
            self.database_settings.db_path_input.blockSignals(True)

            self.current_settings = self.api_client.get_mutable_config()

            # --- API Settings ---
            as_widget = self.api_settings
            obfuscated_analysis_key = self.current_settings.get("GEMINI_API_KEY_ANALYSIS", "")
            revealed_analysis_key = reveal_string(obfuscated_analysis_key)
            as_widget.gemini_analysis_key_input.setText(revealed_analysis_key)

            obfuscated_chat_key = self.current_settings.get("GEMINI_API_KEY_CHAT", "")
            revealed_chat_key = reveal_string(obfuscated_chat_key)
            as_widget.gemini_chat_key_input.setText(revealed_chat_key)

            as_widget.voice_assistant_check.setChecked(self.current_settings.get("VOICE_ASSISTANT_ENABLED", True))

            # --- Database Settings ---
            db_widget = self.database_settings
            db_widget.db_path_input.setText(self.current_settings.get("DATABASE_PATH", ""))

            # --- Email Settings ---
            es_widget = self.email_settings
            es_widget.smtp_host_input.setText(self.current_settings.get("SMTP_HOST", ""))
            es_widget.smtp_port_input.setText(str(self.current_settings.get("SMTP_PORT", "")))
            es_widget.smtp_user_input.setText(self.current_settings.get("SMTP_USER", ""))
            es_widget.smtp_password_input.setText(self.current_settings.get("SMTP_PASSWORD", ""))
            es_widget.recipients_to_input.setText(self.current_settings.get("EMAIL_RECIPIENTS_TO", ""))
            es_widget.recipients_cc_input.setText(self.current_settings.get("EMAIL_RECIPIENTS_CC", ""))

            # --- General Settings ---
            gs_widget = self.general_settings
            gs_widget.alert_threshold_input.setText(str(self.current_settings.get("ALERT_THRESHOLD_DAYS", "60")))
            gs_widget.alert_threshold_visite_input.setText(str(self.current_settings.get("ALERT_THRESHOLD_DAYS_VISITE", "30")))

            # Unblock
            self.general_settings.alert_threshold_input.blockSignals(False)
            self.general_settings.alert_threshold_visite_input.blockSignals(False)
            self.api_settings.gemini_analysis_key_input.blockSignals(False)
            self.api_settings.gemini_chat_key_input.blockSignals(False)
            self.api_settings.voice_assistant_check.blockSignals(False)
            self.email_settings.smtp_host_input.blockSignals(False)
            self.email_settings.smtp_port_input.blockSignals(False)
            self.email_settings.smtp_user_input.blockSignals(False)
            self.email_settings.smtp_password_input.blockSignals(False)
            self.email_settings.recipients_to_input.blockSignals(False)
            self.email_settings.recipients_cc_input.blockSignals(False)
            self.email_settings.email_preset_combo.blockSignals(False)
            self.database_settings.db_path_input.blockSignals(False)

            self.unsaved_changes = False

        except Exception as e:
            CustomMessageDialog.show_error(self, "Errore", f"Impossibile caricare la configurazione: {e}")

    def apply_email_preset(self):
        preset = self.email_settings.email_preset_combo.currentText()
        es_widget = self.email_settings
        if preset == "Gmail":
            es_widget.smtp_host_input.setText("smtp.gmail.com")
            es_widget.smtp_port_input.setText("465")
        elif preset == "Outlook":
            es_widget.smtp_host_input.setText("smtp.office365.com")
            es_widget.smtp_port_input.setText("587")
        elif preset == "COEMI":
            es_widget.smtp_host_input.setText("smtps.aruba.it")
            es_widget.smtp_port_input.setText("465")

    def import_csv(self):
        # Bug 9 Fix: Filter allow uppercase CSV
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleziona CSV", "", "CSV Files (*.csv *.CSV)")
        if file_path:
            try:
                response = self.api_client.import_dipendenti_csv(file_path)
                ToastManager.success("Importazione Completata", response.get("message", "Successo"), self.window())
            except Exception as e:
                CustomMessageDialog.show_error(self, "Errore", f"Impossibile importare: {e}")

    def _validate_config(self, gs, email):
        try:
            smtp_port_val = int(email.smtp_port_input.text()) if email.smtp_port_input.text().isdigit() else None
            if smtp_port_val and (smtp_port_val < 1 or smtp_port_val > 65535):
                 raise ValueError("Porta SMTP non valida (1-65535).")

            alert_days = int(gs.alert_threshold_input.text()) if gs.alert_threshold_input.text().isdigit() else 60
            if alert_days <= 0:
                 raise ValueError("La soglia avviso deve essere > 0.")

            alert_visite = int(gs.alert_threshold_visite_input.text()) if gs.alert_threshold_visite_input.text().isdigit() else 30
            if alert_visite <= 0:
                 raise ValueError("La soglia visite deve essere > 0.")
            return True, smtp_port_val, alert_days, alert_visite
        except ValueError as e:
            CustomMessageDialog.show_warning(self, "Errore Validazione", str(e))
            return False, None, None, None

    def _build_config_payload(self, gs, db, api, email, smtp_port_val, alert_days, alert_visite):
        plain_analysis_key = api.gemini_analysis_key_input.text()
        plain_chat_key = api.gemini_chat_key_input.text()

        new_settings = {
            "DATABASE_PATH": db.db_path_input.text(),
            "GEMINI_API_KEY_ANALYSIS": obfuscate_string(plain_analysis_key),
            "GEMINI_API_KEY_CHAT": obfuscate_string(plain_chat_key),
            "VOICE_ASSISTANT_ENABLED": api.voice_assistant_check.isChecked(),
            "SMTP_HOST": email.smtp_host_input.text(),
            "SMTP_PORT": smtp_port_val,
            "SMTP_USER": email.smtp_user_input.text(),
            "SMTP_PASSWORD": email.smtp_password_input.text(),
            "EMAIL_RECIPIENTS_TO": email.recipients_to_input.text(),
            "EMAIL_RECIPIENTS_CC": email.recipients_cc_input.text(),
            "ALERT_THRESHOLD_DAYS": alert_days,
            "ALERT_THRESHOLD_DAYS_VISITE": alert_visite,
        }

        # Reveal the currently stored keys to compare with the new plain text keys
        current_obf_analysis = self.current_settings.get("GEMINI_API_KEY_ANALYSIS", "")
        current_rev_analysis = reveal_string(current_obf_analysis)
        current_obf_chat = self.current_settings.get("GEMINI_API_KEY_CHAT", "")
        current_rev_chat = reveal_string(current_obf_chat)

        update_payload = {}
        for k, v in new_settings.items():
            if k == "GEMINI_API_KEY_ANALYSIS":
                if plain_analysis_key != current_rev_analysis:
                    update_payload[k] = v
            elif k == "GEMINI_API_KEY_CHAT":
                if plain_chat_key != current_rev_chat:
                    update_payload[k] = v
            elif self.current_settings.get(k) != v:
                update_payload[k] = v
        return update_payload

    def save_config(self):
        # S3776: Refactored to reduce complexity
        if getattr(self, 'is_read_only', False):
            return

        gs = self.general_settings
        email = self.email_settings

        valid, smtp_port_val, alert_days, alert_visite = self._validate_config(gs, email)
        if not valid: return

        update_payload = self._build_config_payload(
            gs, self.database_settings, self.api_settings,
            email, smtp_port_val, alert_days, alert_visite
        )

        if not update_payload:
            ToastManager.info("Nessuna Modifica", "Nessuna modifica da salvare.", self.window())
            return

        self._perform_save_operation(update_payload)

    def _perform_save_operation(self, update_payload):
        """Helper to execute the API call and handle database move if needed."""
        try:
            new_db_path = self.database_settings.db_path_input.text()
            current_db_path = self.current_settings.get("DATABASE_PATH", "")

            if new_db_path and new_db_path != current_db_path:
                self.api_client.move_database(new_db_path)

            self.api_client.update_mutable_config(update_payload)
            ToastManager.success("Salvato", "Configurazione salvata con successo. Le modifiche saranno attive al prossimo riavvio.", self.window())
            self.load_config()
        except Exception as e:
            CustomMessageDialog.show_error(self, "Errore", f"Impossibile salvare la configurazione: {e}")
