import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QFrame, QFormLayout, QComboBox, QFileDialog, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QDialog, QDialogButtonBox, QCheckBox,
    QStackedWidget, QHeaderView, QDateEdit
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor
from desktop_app.api_client import APIClient

class UserDialog(QDialog):
    def __init__(self, parent=None, user_data=None):
        super().__init__(parent)
        self.setWindowTitle("Nuovo Utente" if not user_data else "Modifica Utente")
        self.resize(500, 400)
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
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
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
        except Exception:
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
                QMessageBox.critical(self, "Errore", str(e))

    def delete_user(self):
        user_id = self.get_selected_user_id()
        if not user_id: return
        if user_id == self.api_client.user_info.get("id"):
            QMessageBox.warning(self, "Azione Non Consentita", "Non puoi eliminare il tuo account.")
            return
        if QMessageBox.question(self, "Conferma", "Eliminare questo utente?") == QMessageBox.StandardButton.Yes:
            try:
                self.api_client.delete_user(user_id)
                self.refresh_users()
            except Exception as e:
                QMessageBox.critical(self, "Errore", str(e))

class GeneralSettingsWidget(QFrame):
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.setObjectName("card")
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)
        self.form_layout = QFormLayout()
        self.form_layout.setSpacing(15)
        self.form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)

        self.gemini_api_key_input = QLineEdit()
        self.gemini_api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.form_layout.addRow(QLabel("Gemini API Key:"), self.gemini_api_key_input)

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

        filter_layout = QHBoxLayout()
        self.user_filter = QComboBox()
        self.user_filter.addItem("Tutti gli utenti", None)
        filter_layout.addWidget(QLabel("Utente:"))
        filter_layout.addWidget(self.user_filter)
        self.category_filter = QComboBox()
        self.category_filter.addItem("Tutte le categorie", None)
        self.category_filter.addItems(["AUTH", "USER_MGMT", "CERTIFICATE", "SYSTEM", "CONFIG", "DATA"])
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
        self.refresh_btn = QPushButton("Aggiorna")
        self.refresh_btn.clicked.connect(self.refresh_logs)
        filter_layout.addWidget(self.refresh_btn)
        self.layout.addLayout(filter_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(["Data/Ora", "Severità", "Utente", "IP", "Geo", "Device ID", "Azione", "Categoria", "Dettagli"])
        header = self.table.horizontalHeader()
        for i in range(8):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.layout.addWidget(self.table)

    def refresh_logs(self):
        # Implementation omitted for brevity
        pass

class ConfigView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        self.api_client = APIClient()
        self.current_settings = {}

        description = QLabel("Gestisci le impostazioni e le chiavi API dell'applicazione.")
        description.setObjectName("viewDescription")
        self.layout.addWidget(description)

        self.nav_container = QFrame()
        self.nav_layout = QHBoxLayout(self.nav_container)
        self.nav_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.nav_layout.setSpacing(10)

        self.btn_general = QPushButton("Parametri generali")
        self.btn_general.setCheckable(True)
        self.btn_general.setChecked(True)
        self.btn_general.clicked.connect(lambda: self.switch_tab(0))
        self.btn_account = QPushButton("Account")
        self.btn_account.setCheckable(True)
        self.btn_account.clicked.connect(lambda: self.switch_tab(1))
        self.btn_audit = QPushButton("Log Attività")
        self.btn_audit.setCheckable(True)
        self.btn_audit.clicked.connect(lambda: self.switch_tab(2))

        for btn in [self.btn_general, self.btn_account, self.btn_audit]:
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedWidth(180)
            self.nav_layout.addWidget(btn)

        self.layout.addWidget(self.nav_container)

        self.stacked_widget = QStackedWidget()
        self.general_settings = GeneralSettingsWidget(self.api_client)
        self.user_management_widget = UserManagementWidget(self.api_client)
        self.audit_widget = AuditLogWidget(self.api_client)
        self.stacked_widget.addWidget(self.general_settings)
        self.stacked_widget.addWidget(self.user_management_widget)
        self.stacked_widget.addWidget(self.audit_widget)
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
        bottom_layout.addWidget(self.import_button)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.save_button)
        self.layout.addWidget(self.bottom_buttons_frame)

        self.general_settings.email_preset_combo.currentIndexChanged.connect(self.apply_email_preset)

    def set_read_only(self, is_read_only: bool):
        self.is_read_only = is_read_only
        self.save_button.setEnabled(not is_read_only)
        self.import_button.setEnabled(not is_read_only)
        self.user_management_widget.add_btn.setEnabled(not is_read_only)
        self.user_management_widget.edit_btn.setEnabled(not is_read_only)
        self.user_management_widget.delete_btn.setEnabled(not is_read_only)
        self.save_button.setToolTip("Database in sola lettura" if is_read_only else "")

    def switch_tab(self, index):
        self.stacked_widget.setCurrentIndex(index)
        self.btn_general.setChecked(index == 0)
        self.btn_account.setChecked(index == 1)
        self.btn_audit.setChecked(index == 2)
        self.bottom_buttons_frame.setVisible(index == 0)

    def showEvent(self, event):
        super().showEvent(event)
        if self.api_client and self.api_client.user_info:
            is_admin = self.api_client.user_info.get("is_admin", False)
            self.btn_account.setVisible(is_admin)
            self.btn_audit.setVisible(is_admin)
            if is_admin:
                self.load_config()
                self.user_management_widget.refresh_users()

    def load_config(self):
        try:
            self.current_settings = self.api_client.get_mutable_config()
            gs = self.general_settings
            gs.gemini_api_key_input.setText(self.current_settings.get("GEMINI_API_KEY", ""))
            gs.smtp_host_input.setText(self.current_settings.get("SMTP_HOST", ""))
            gs.smtp_port_input.setText(str(self.current_settings.get("SMTP_PORT", "")))
            gs.smtp_user_input.setText(self.current_settings.get("SMTP_USER", ""))
            gs.smtp_password_input.setText(self.current_settings.get("SMTP_PASSWORD", ""))
            gs.recipients_to_input.setText(self.current_settings.get("EMAIL_RECIPIENTS_TO", ""))
            gs.recipients_cc_input.setText(self.current_settings.get("EMAIL_RECIPIENTS_CC", ""))
            gs.alert_threshold_input.setText(str(self.current_settings.get("ALERT_THRESHOLD_DAYS", "60")))
            gs.alert_threshold_visite_input.setText(str(self.current_settings.get("ALERT_THRESHOLD_DAYS_VISITE", "30")))
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile caricare la configurazione: {e}")

    def apply_email_preset(self):
        preset = self.general_settings.email_preset_combo.currentText()
        gs = self.general_settings
        if preset == "Gmail":
            gs.smtp_host_input.setText("smtp.gmail.com")
            gs.smtp_port_input.setText("465")
        elif preset == "Outlook":
            gs.smtp_host_input.setText("smtp.office365.com")
            gs.smtp_port_input.setText("587")
        elif preset == "COEMI":
            gs.smtp_host_input.setText("smtps.aruba.it")
            gs.smtp_port_input.setText("465")

    def import_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleziona CSV", "", "CSV Files (*.csv)")
        if file_path:
            try:
                response = self.api_client.import_dipendenti_csv(file_path)
                QMessageBox.information(self, "Importazione Completata", response.get("message", "Successo"))
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Impossibile importare: {e}")

    def save_config(self):
        if getattr(self, 'is_read_only', False):
            return

        gs = self.general_settings
        new_settings = {
            "GEMINI_API_KEY": gs.gemini_api_key_input.text(),
            "SMTP_HOST": gs.smtp_host_input.text(),
            "SMTP_PORT": int(gs.smtp_port_input.text()) if gs.smtp_port_input.text().isdigit() else None,
            "SMTP_USER": gs.smtp_user_input.text(),
            "SMTP_PASSWORD": gs.smtp_password_input.text(),
            "EMAIL_RECIPIENTS_TO": gs.recipients_to_input.text(),
            "EMAIL_RECIPIENTS_CC": gs.recipients_cc_input.text(),
            "ALERT_THRESHOLD_DAYS": int(gs.alert_threshold_input.text()) if gs.alert_threshold_input.text().isdigit() else 60,
            "ALERT_THRESHOLD_DAYS_VISITE": int(gs.alert_threshold_visite_input.text()) if gs.alert_threshold_visite_input.text().isdigit() else 30,
        }

        # Filter out any keys that have not changed
        update_payload = {k: v for k, v in new_settings.items() if self.current_settings.get(k) != v}

        if not update_payload:
            QMessageBox.information(self, "Nessuna Modifica", "Nessuna modifica da salvare.")
            return

        try:
            self.api_client.update_mutable_config(update_payload)
            QMessageBox.information(self, "Salvato", "Configurazione salvata con successo. Le modifiche saranno attive al prossimo riavvio.")
            self.load_config() # Reload to update current_settings state
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile salvare la configurazione: {e}")
