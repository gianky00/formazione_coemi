import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QFrame, QFormLayout, QComboBox, QFileDialog, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QDialog, QDialogButtonBox, QCheckBox
)
from PyQt6.QtCore import Qt
from dotenv import load_dotenv, set_key
from desktop_app.api_client import APIClient

class UserDialog(QDialog):
    def __init__(self, parent=None, user_data=None):
        super().__init__(parent)
        self.setWindowTitle("Nuovo Utente" if not user_data else "Modifica Utente")
        self.resize(400, 300)
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
            # Disable username editing for existing users if desired, but API supports it.
            # Requirement: "admin must be able to overwrite/reset any user's password without knowing the old password"
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
        self.table.horizontalHeader().setStretchLastSection(True)
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
            # Fail silently or log if API call fails (e.g. not admin)
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

    def get_selected_username(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows: return None
        return self.table.item(rows[0].row(), 1).text()

    def edit_user(self):
        user_id = self.get_selected_user_id()
        if not user_id: return

        # Fetch current details? Or just use table data?
        # Better to just use dialog, pre-fill what we can.
        # We don't have password, which is fine.

        # Prevent editing own password via this tool if current user is this user?
        # Requirement: "l'admin non ha la possibilità di modificare la password sua"
        # If I am admin, I am logged in.
        current_username = self.api_client.user_info.get("username")
        selected_username = self.get_selected_username()

        if selected_username == "admin" and current_username == "admin":
             # Special hardcoded case: Admin cannot change Admin password
             # But maybe can change account name?
             pass

        # Actually, let's check against current user ID if available
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

class ConfigView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        self.api_client = APIClient() # Default instance, will be overwritten or updated

        description = QLabel("Gestisci le impostazioni e le chiavi API dell'applicazione.")
        description.setObjectName("viewDescription")
        self.layout.addWidget(description)

        # --- User Management Section (Hidden by default) ---
        self.user_management_widget = UserManagementWidget(self.api_client)
        self.user_management_widget.setVisible(False)
        self.layout.addWidget(self.user_management_widget)

        # Main settings card
        main_card = QFrame()
        main_card.setObjectName("card")
        self.form_layout = QFormLayout(main_card)
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
        self.email_preset_combo.currentIndexChanged.connect(self.apply_email_preset)
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

        self.layout.addWidget(main_card)
        self.layout.addStretch()

        # Save button
        self.save_button = QPushButton("Salva Modifiche")
        self.save_button.setObjectName("primary")
        self.save_button.clicked.connect(self.save_config)

        self.import_button = QPushButton("Importa Dipendenti da CSV")
        self.import_button.setObjectName("secondary")
        self.import_button.setToolTip("Formato CSV richiesto. Dimensione massima: 5MB.")
        self.import_button.clicked.connect(self.import_csv)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.import_button)
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        self.layout.addLayout(button_layout)

        self.load_config()

    def showEvent(self, event):
        super().showEvent(event)
        # Refresh User Management visibility
        if self.api_client and self.api_client.user_info:
            is_admin = self.api_client.user_info.get("is_admin", False)
            self.user_management_widget.setVisible(is_admin)
            self.user_management_widget.api_client = self.api_client # Ensure client is up to date
            if is_admin:
                self.user_management_widget.refresh_users()
        else:
            self.user_management_widget.setVisible(False)

    def get_env_path(self):
        # Assumes .env file is in the root directory of the project
        return os.path.join(os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ), '.env')

    def load_config(self):
        env_path = self.get_env_path()
        if not os.path.exists(env_path):
            with open(env_path, 'w') as f:
                f.write("# Configuration file for Intelleo\n")
        load_dotenv(dotenv_path=env_path)

        self.gemini_api_key_input.setText(os.getenv("GEMINI_API_KEY", ""))
        self.gcp_project_id_input.setText(os.getenv("GOOGLE_CLOUD_PROJECT", ""))
        self.gcs_bucket_name_input.setText(os.getenv("GCS_BUCKET_NAME", ""))
        self.smtp_host_input.setText(os.getenv("SMTP_HOST", ""))
        self.smtp_port_input.setText(os.getenv("SMTP_PORT", ""))
        self.smtp_user_input.setText(os.getenv("SMTP_USER", ""))
        self.smtp_password_input.setText(os.getenv("SMTP_PASSWORD", ""))
        self.recipients_to_input.setText(os.getenv("EMAIL_RECIPIENTS_TO", ""))
        self.recipients_cc_input.setText(os.getenv("EMAIL_RECIPIENTS_CC", ""))

    def apply_email_preset(self):
        preset = self.email_preset_combo.currentText()
        if preset == "Gmail":
            self.smtp_host_input.setText("smtp.gmail.com")
            self.smtp_port_input.setText("587")
        elif preset == "Outlook":
            self.smtp_host_input.setText("smtp.office365.com")
            self.smtp_port_input.setText("587")
        elif preset == "COEMI":
            self.smtp_host_input.setText("smtps.aruba.it")
            self.smtp_port_input.setText("587")

    def import_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleziona CSV", "", "CSV Files (*.csv)")
        if file_path:
            try:
                response = self.api_client.import_dipendenti_csv(file_path)
                QMessageBox.information(
                    self,
                    "Importazione Completata",
                    response.get("message", "Importazione dei dipendenti completata con successo.")
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Errore di Importazione",
                    f"Impossibile importare il file CSV: {e}"
                )

    def save_config(self):
        env_path = self.get_env_path()
        try:
            set_key(env_path, "GEMINI_API_KEY", self.gemini_api_key_input.text())
            set_key(env_path, "GOOGLE_CLOUD_PROJECT", self.gcp_project_id_input.text())
            set_key(env_path, "GCS_BUCKET_NAME", self.gcs_bucket_name_input.text())
            set_key(env_path, "SMTP_HOST", self.smtp_host_input.text())
            set_key(env_path, "SMTP_PORT", self.smtp_port_input.text())
            set_key(env_path, "SMTP_USER", self.smtp_user_input.text())
            set_key(env_path, "SMTP_PASSWORD", self.smtp_password_input.text())
            set_key(env_path, "EMAIL_RECIPIENTS_TO", self.recipients_to_input.text())
            set_key(env_path, "EMAIL_RECIPIENTS_CC", self.recipients_cc_input.text())

            QMessageBox.information(
                self,
                "Configurazione Salvata",
                "Le modifiche sono state salvate con successo. "
                "Per renderle effettive, riavvia l'applicazione."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Errore di Salvataggio",
                f"Impossibile salvare la configurazione: {e}"
            )
