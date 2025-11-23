import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QFrame, QFormLayout, QComboBox, QFileDialog, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QDialog, QDialogButtonBox, QCheckBox,
    QStackedWidget, QButtonGroup, QHeaderView, QDateEdit
)
from PyQt6.QtCore import Qt, QDate
from dotenv import load_dotenv, set_key
from desktop_app.api_client import APIClient

class UserDialog(QDialog):
    def __init__(self, parent=None, user_data=None):
        super().__init__(parent)
        self.setWindowTitle("Nuovo Utente" if not user_data else "Modifica Utente")
        self.resize(500, 400)  # Increased size
        self.layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        self.username_input = QLineEdit()
        self.account_name_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.is_admin_check = QCheckBox("Amministratore")

        if user_data:
            self.username_input.setText(user_data.get('username', ''))
            self.account_name_input.setText(user_data.get('account_name', ''))
            self.is_admin_check.setChecked(user_data.get('is_admin', False))
            self.password_input.setPlaceholderText("Lascia vuoto per mantenere la password attuale")

        form_layout.addRow("Nome Utente:", self.username_input)
        form_layout.addRow("Nome Account (es. Mario Rossi):", self.account_name_input)
        form_layout.addRow("Password:", self.password_input)
        form_layout.addRow("", self.is_admin_check)

        self.layout.addLayout(form_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout.addWidget(buttons)

    def get_data(self):
        return {
            "username": self.username_input.text(),
            "account_name": self.account_name_input.text(),
            "password": self.password_input.text(),
            "is_admin": self.is_admin_check.isChecked()
        }

class UserManagementWidget(QFrame):
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.setObjectName("card")
        self.layout = QVBoxLayout(self)

        header = QHBoxLayout()
        title = QLabel("Gestione Utenti")
        title.setStyleSheet("font-size: 16px; font-weight: 600;")
        header.addWidget(title)
        header.addStretch()

        self.add_btn = QPushButton("Nuovo Utente")
        self.add_btn.setObjectName("secondary")
        self.add_btn.clicked.connect(self.add_user)
        header.addWidget(self.add_btn)

        self.layout.addLayout(header)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Nome Utente", "Nome Account", "Admin"])

        # Configure Header Resizing
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents) # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)          # Username
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)          # Account Name
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents) # Admin

        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.layout.addWidget(self.table)

        actions_layout = QHBoxLayout()
        self.edit_btn = QPushButton("Modifica / Reset Password")
        self.edit_btn.clicked.connect(self.edit_user)
        actions_layout.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("Elimina")
        self.delete_btn.setObjectName("destructive")
        self.delete_btn.clicked.connect(self.delete_user)
        actions_layout.addWidget(self.delete_btn)

        self.layout.addLayout(actions_layout)

    def refresh_users(self):
        try:
            users = self.api_client.get_users()
            self.table.setRowCount(len(users))
            for i, user in enumerate(users):
                self.table.setItem(i, 0, QTableWidgetItem(str(user['id'])))
                self.table.setItem(i, 1, QTableWidgetItem(str(user['username'])))
                self.table.setItem(i, 2, QTableWidgetItem(str(user.get('account_name', ''))))
                self.table.setItem(i, 3, QTableWidgetItem("Sì" if user['is_admin'] else "No"))
        except Exception as e:
            pass

    def add_user(self):
        dialog = UserDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if not data['username'] or not data['password']:
                QMessageBox.warning(self, "Errore", "Nome utente e password sono obbligatori.")
                return

            try:
                self.api_client.create_user(
                    data['username'], data['password'],
                    data['account_name'], data['is_admin']
                )
                self.refresh_users()
            except Exception as e:
                QMessageBox.critical(self, "Errore", str(e))

    def get_selected_user_id(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows: return None
        return int(self.table.item(rows[0].row(), 0).text())

    def edit_user(self):
        user_id = self.get_selected_user_id()
        if not user_id: return

        current_user_id = self.api_client.user_info.get("id")

        user_data = {
            "username": self.table.item(self.table.currentRow(), 1).text(),
            "account_name": self.table.item(self.table.currentRow(), 2).text(),
            "is_admin": self.table.item(self.table.currentRow(), 3).text() == "Sì"
        }

        dialog = UserDialog(self, user_data)
        if current_user_id == user_id:
             dialog.password_input.setPlaceholderText("Non puoi modificare la tua password da qui")
             dialog.password_input.setEnabled(False)

        if dialog.exec():
            data = dialog.get_data()
            update_payload = {}
            if data['username'] != user_data['username']: update_payload['username'] = data['username']
            if data['account_name'] != user_data['account_name']: update_payload['account_name'] = data['account_name']
            if data['is_admin'] != user_data['is_admin']: update_payload['is_admin'] = data['is_admin']
            if data['password']: update_payload['password'] = data['password']

            if not update_payload: return

            try:
                self.api_client.update_user(user_id, update_payload)
                self.refresh_users()
            except Exception as e:
                msg = str(e)
                if hasattr(e, 'response') and e.response is not None:
                     try: msg = e.response.json().get('detail', msg)
                     except: pass
                QMessageBox.critical(self, "Errore", msg)

    def delete_user(self):
        user_id = self.get_selected_user_id()
        if not user_id: return

        current_user_id = self.api_client.user_info.get("id")
        if user_id == current_user_id:
            QMessageBox.warning(self, "Azione Non Consentita", "Non puoi eliminare il tuo account.")
            return

        if QMessageBox.question(self, "Conferma", "Eliminare questo utente?") == QMessageBox.StandardButton.Yes:
            try:
                self.api_client.delete_user(user_id)
                self.refresh_users()
            except Exception as e:
                QMessageBox.critical(self, "Errore", str(e))

class GeneralSettingsWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)

        self.form_layout = QFormLayout()
        self.form_layout.setSpacing(15)
        self.form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)

        # API Settings
        self.gemini_api_key_input = QLineEdit()
        self.gemini_api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.form_layout.addRow(QLabel("Gemini API Key:"), self.gemini_api_key_input)

        self.gcp_project_id_input = QLineEdit()
        self.form_layout.addRow(QLabel("Google Cloud Project ID:"), self.gcp_project_id_input)

        self.gcs_bucket_name_input = QLineEdit()
        self.form_layout.addRow(QLabel("Google Cloud Storage Bucket:"), self.gcs_bucket_name_input)

        # SMTP Settings
        smtp_separator = QFrame()
        smtp_separator.setFrameShape(QFrame.Shape.HLine)
        smtp_separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.form_layout.addRow(smtp_separator)

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

        # Threshold Settings
        threshold_separator = QFrame()
        threshold_separator.setFrameShape(QFrame.Shape.HLine)
        threshold_separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.form_layout.addRow(threshold_separator)

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

        self.layout.addLayout(header)

        # Filters
        filter_layout = QHBoxLayout()

        self.user_filter = QComboBox()
        self.user_filter.addItem("Tutti gli utenti", None)
        # We need to populate this. We can do it when refreshing or in showEvent.
        # Since AuditLogWidget is initialized with api_client, we can try to fetch users if admin.

        filter_layout.addWidget(QLabel("Utente:"))
        filter_layout.addWidget(self.user_filter)

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("dd/MM/yyyy")
        self.start_date.setDate(QDate.currentDate().addDays(-30)) # Default last 30 days

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("dd/MM/yyyy")
        self.end_date.setDate(QDate.currentDate())

        filter_layout.addWidget(QLabel("Dal:"))
        filter_layout.addWidget(self.start_date)
        filter_layout.addWidget(QLabel("Al:"))
        filter_layout.addWidget(self.end_date)

        self.refresh_btn = QPushButton("Aggiorna")
        self.refresh_btn.clicked.connect(self.refresh_logs)
        filter_layout.addWidget(self.refresh_btn)

        self.layout.addLayout(filter_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Data/Ora", "Utente", "Azione", "Dettagli"])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)

        self.layout.addWidget(self.table)

    def refresh_logs(self):
        try:
            # Update users list if empty (lazy load)
            if self.user_filter.count() == 1:
                try:
                    users = self.api_client.get_users()
                    for u in users:
                        self.user_filter.addItem(u['username'], u['id'])
                except: pass

            user_id = self.user_filter.currentData()
            start_date = self.start_date.date().toPyDate()
            end_date = self.end_date.date().toPyDate()

            # Adjust end_date to include the whole day (23:59:59) or just pass date and let backend handle?
            # Backend compares timestamp. date >= start_date (00:00). date <= end_date (00:00).
            # So if we want to include today events, we need to handle time.
            # Let's just pass the date object, and backend should handle or we pass datetime.
            # My backend implementation: query.filter(AuditLog.timestamp <= end_date)
            # If I pass a date, sqlalchemy might cast?
            # Better to pass datetime at end of day.
            from datetime import datetime, time
            start_dt = datetime.combine(start_date, time.min)
            end_dt = datetime.combine(end_date, time.max)

            logs = self.api_client.get_audit_logs(limit=500, user_id=user_id, start_date=start_dt, end_date=end_dt)
            self.table.setRowCount(len(logs))
            for i, log in enumerate(logs):
                ts = log['timestamp']
                if 'T' in ts:
                    ts = ts.replace('T', ' ')
                if '.' in ts:
                    ts = ts.split('.')[0]

                self.table.setItem(i, 0, QTableWidgetItem(ts))
                self.table.setItem(i, 1, QTableWidgetItem(log['username']))
                self.table.setItem(i, 2, QTableWidgetItem(log['action']))
                self.table.setItem(i, 3, QTableWidgetItem(str(log['details'] or "")))
        except Exception as e:
            print(f"Error refreshing logs: {e}")
            pass

class ConfigView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        self.api_client = APIClient()

        description = QLabel("Gestisci le impostazioni e le chiavi API dell'applicazione.")
        description.setObjectName("viewDescription")
        self.layout.addWidget(description)

        # --- Top Navigation Tabs ---
        self.nav_container = QFrame()
        self.nav_layout = QHBoxLayout(self.nav_container)
        self.nav_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.nav_layout.setSpacing(10)

        self.btn_general = QPushButton("Parametri generali")
        self.btn_general.setCheckable(True)
        self.btn_general.setChecked(True)
        self.btn_general.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_general.setFixedWidth(180)
        self.btn_general.clicked.connect(lambda: self.switch_tab(0))

        self.btn_account = QPushButton("Account")
        self.btn_account.setCheckable(True)
        self.btn_account.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_account.setFixedWidth(180)
        self.btn_account.clicked.connect(lambda: self.switch_tab(1))

        self.btn_audit = QPushButton("Log Attività")
        self.btn_audit.setCheckable(True)
        self.btn_audit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_audit.setFixedWidth(180)
        self.btn_audit.clicked.connect(lambda: self.switch_tab(2))

        self.nav_layout.addWidget(self.btn_general)
        self.nav_layout.addWidget(self.btn_account)
        self.nav_layout.addWidget(self.btn_audit)

        self.layout.addWidget(self.nav_container)

        # Style the tabs
        self.setStyleSheet("""
            QPushButton[checkable="true"] {
                background-color: #FFFFFF;
                color: #6B7280;
                border: 1px solid #D1D5DB;
                border-radius: 20px;
                padding: 8px 16px;
                font-weight: 600;
            }
            QPushButton[checkable="true"]:checked {
                background-color: #1E3A8A;
                color: #FFFFFF;
                border: 1px solid #1E3A8A;
            }
            QPushButton[checkable="true"]:hover:!checked {
                background-color: #F3F4F6;
            }
        """)

        # --- Stacked Content ---
        self.stacked_widget = QStackedWidget()

        # Page 1: General Settings
        self.general_settings = GeneralSettingsWidget()
        self.stacked_widget.addWidget(self.general_settings)

        # Page 2: User Management
        self.user_management_widget = UserManagementWidget(self.api_client)
        self.stacked_widget.addWidget(self.user_management_widget)

        # Page 3: Audit Logs
        self.audit_widget = AuditLogWidget(self.api_client)
        self.stacked_widget.addWidget(self.audit_widget)

        self.layout.addWidget(self.stacked_widget)

        # --- Buttons (for General Settings) ---
        # These buttons should likely only be visible when General Settings is active
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

        bottom_layout.addWidget(self.import_button)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.save_button)

        self.layout.addWidget(self.bottom_buttons_frame)

        # Connect inner form logic
        self.general_settings.email_preset_combo.currentIndexChanged.connect(self.apply_email_preset)

        self.load_config()

    def switch_tab(self, index):
        self.stacked_widget.setCurrentIndex(index)
        self.btn_general.setChecked(index == 0)
        self.btn_account.setChecked(index == 1)
        self.btn_audit.setChecked(index == 2)

        # Hide general action buttons if not on general tab
        self.bottom_buttons_frame.setVisible(index == 0)

    def showEvent(self, event):
        super().showEvent(event)
        # Handle Admin visibility
        if self.api_client and self.api_client.user_info:
            is_admin = self.api_client.user_info.get("is_admin", False)
            self.btn_account.setVisible(is_admin)
            self.btn_audit.setVisible(is_admin)

            self.user_management_widget.api_client = self.api_client
            self.audit_widget.api_client = self.api_client

            if is_admin:
                self.user_management_widget.refresh_users()
                if self.stacked_widget.currentIndex() == 2:
                    self.audit_widget.refresh_logs()
        else:
            self.btn_account.setVisible(False)
            self.btn_audit.setVisible(False)

        # Reset to general tab if Account is hidden but active (rare case)
        if not self.btn_account.isVisible() and self.stacked_widget.currentIndex() in [1, 2]:
            self.switch_tab(0)

    def get_env_path(self):
        return os.path.join(os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ), '.env')

    def load_config(self):
        env_path = self.get_env_path()
        if not os.path.exists(env_path):
            with open(env_path, 'w') as f:
                f.write("# Configuration file for Intelleo\n")
        load_dotenv(dotenv_path=env_path)

        gs = self.general_settings
        gs.gemini_api_key_input.setText(os.getenv("GEMINI_API_KEY", ""))
        gs.gcp_project_id_input.setText(os.getenv("GOOGLE_CLOUD_PROJECT", ""))
        gs.gcs_bucket_name_input.setText(os.getenv("GCS_BUCKET_NAME", ""))
        gs.smtp_host_input.setText(os.getenv("SMTP_HOST", ""))
        gs.smtp_port_input.setText(os.getenv("SMTP_PORT", ""))
        gs.smtp_user_input.setText(os.getenv("SMTP_USER", ""))
        gs.smtp_password_input.setText(os.getenv("SMTP_PASSWORD", ""))
        gs.recipients_to_input.setText(os.getenv("EMAIL_RECIPIENTS_TO", ""))
        gs.recipients_cc_input.setText(os.getenv("EMAIL_RECIPIENTS_CC", ""))
        gs.alert_threshold_input.setText(os.getenv("ALERT_THRESHOLD_DAYS", "60"))
        gs.alert_threshold_visite_input.setText(os.getenv("ALERT_THRESHOLD_DAYS_VISITE", "30"))

    def apply_email_preset(self):
        preset = self.general_settings.email_preset_combo.currentText()
        gs = self.general_settings
        if preset == "Gmail":
            gs.smtp_host_input.setText("smtp.gmail.com")
            gs.smtp_port_input.setText("587")
        elif preset == "Outlook":
            gs.smtp_host_input.setText("smtp.office365.com")
            gs.smtp_port_input.setText("587")
        elif preset == "COEMI":
            gs.smtp_host_input.setText("smtps.aruba.it")
            gs.smtp_port_input.setText("587")

    def import_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleziona CSV", "", "CSV Files (*.csv)")
        if file_path:
            try:
                response = self.api_client.import_dipendenti_csv(file_path)
                QMessageBox.information(self, "Importazione Completata", response.get("message", "Successo"))
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Impossibile importare: {e}")

    def save_config(self):
        env_path = self.get_env_path()
        gs = self.general_settings
        try:
            set_key(env_path, "GEMINI_API_KEY", gs.gemini_api_key_input.text())
            set_key(env_path, "GOOGLE_CLOUD_PROJECT", gs.gcp_project_id_input.text())
            set_key(env_path, "GCS_BUCKET_NAME", gs.gcs_bucket_name_input.text())
            set_key(env_path, "SMTP_HOST", gs.smtp_host_input.text())
            set_key(env_path, "SMTP_PORT", gs.smtp_port_input.text())
            set_key(env_path, "SMTP_USER", gs.smtp_user_input.text())
            set_key(env_path, "SMTP_PASSWORD", gs.smtp_password_input.text())
            set_key(env_path, "EMAIL_RECIPIENTS_TO", gs.recipients_to_input.text())
            set_key(env_path, "EMAIL_RECIPIENTS_CC", gs.recipients_cc_input.text())
            set_key(env_path, "ALERT_THRESHOLD_DAYS", gs.alert_threshold_input.text())
            set_key(env_path, "ALERT_THRESHOLD_DAYS_VISITE", gs.alert_threshold_visite_input.text())

            # Audit Log
            try:
                self.api_client.create_audit_log("CONFIG_UPDATE", "Updated application settings (SMTP/API Keys/Thresholds).")
            except: pass

            QMessageBox.information(self, "Salvato", "Configurazione salvata. Riavviare per applicare.")
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile salvare: {e}")
