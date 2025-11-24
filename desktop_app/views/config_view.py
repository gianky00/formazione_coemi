import os
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QFrame, QFormLayout, QComboBox, QFileDialog, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QDialog, QDialogButtonBox, QCheckBox,
    QStackedWidget, QButtonGroup, QHeaderView, QDateEdit
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor
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

                # Log changes
                changes = {}
                for k, v in update_payload.items():
                    old_v = user_data.get(k)
                    if k == "password":
                        changes[k] = {"old": "***", "new": "***"}
                    elif k == "is_admin":
                         changes[k] = {"old": user_data.get(k), "new": v}
                    else:
                        changes[k] = {"old": old_v, "new": v}

                try:
                    self.api_client.create_audit_log(
                        "USER_UPDATE",
                        f"Updated user {user_data['username']}",
                        category="USER_MGMT",
                        changes=json.dumps(changes)
                    )
                except: pass

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
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
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

        # Security Settings
        security_separator = QFrame()
        security_separator.setFrameShape(QFrame.Shape.HLine)
        security_separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.form_layout.addRow(security_separator)

        self.db_security_label = QLabel("Sicurezza Database:")
        self.db_security_status = QLabel("Caricamento...")
        self.db_security_btn = QPushButton("Attiva Protezione")
        self.db_security_btn.clicked.connect(self.toggle_db_security)

        security_layout = QHBoxLayout()
        security_layout.addWidget(self.db_security_status)
        security_layout.addWidget(self.db_security_btn)

        self.form_layout.addRow(self.db_security_label, security_layout)

        self.layout.addLayout(self.form_layout)
        self.layout.addStretch()

    def refresh_security_status(self):
        # Only if admin
        if not self.api_client.user_info or not self.api_client.user_info.get("is_admin"):
            self.db_security_label.setVisible(False)
            self.db_security_status.setVisible(False)
            self.db_security_btn.setVisible(False)
            return

        self.db_security_label.setVisible(True)
        self.db_security_status.setVisible(True)
        self.db_security_btn.setVisible(True)

        try:
            status = self.api_client.get_db_security_status()
            is_locked = status.get("locked", False)
            if is_locked:
                self.db_security_status.setText("🔒 BLINDATO (Crittografato)")
                self.db_security_status.setStyleSheet("color: green; font-weight: bold;")
                self.db_security_btn.setText("Sblocca (Rendi Leggibile)")
                self.db_security_btn.setObjectName("destructive") # Red button for unlocking
                self.db_security_btn.setStyleSheet("") # Reset if needed
            else:
                self.db_security_status.setText("🔓 APERTO (Non Protetto)")
                self.db_security_status.setStyleSheet("color: red; font-weight: bold;")
                self.db_security_btn.setText("Attiva Protezione (Blinda)")
                self.db_security_btn.setObjectName("primary")
        except Exception as e:
            self.db_security_status.setText("Errore stato")
            print(f"Error fetching security status: {e}")

    def toggle_db_security(self):
        current_text = self.db_security_status.text()
        is_locked = "BLINDATO" in current_text

        action = "SBLOCCARE" if is_locked else "BLINDARE"

        confirm = QMessageBox.question(
            self,
            "Conferma Sicurezza",
            f"Sei sicuro di voler {action} il database?\n\n"
            "Questa operazione richiede accesso esclusivo e potrebbe richiedere alcuni secondi.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:
            # We want to toggle to the OPPOSITE state
            new_state = not is_locked
            self.api_client.toggle_db_security(new_state)
            self.refresh_security_status()
            QMessageBox.information(self, "Successo", "Stato sicurezza aggiornato.")
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile aggiornare sicurezza: {e}")

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

        self.category_filter = QComboBox()
        self.category_filter.addItem("Tutte le categorie", None)
        self.category_filter.addItems(["AUTH", "USER_MGMT", "CERTIFICATE", "SYSTEM", "CONFIG", "DATA"])
        filter_layout.addWidget(QLabel("Categoria:"))
        filter_layout.addWidget(self.category_filter)

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
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(["Data/Ora", "Severità", "Utente", "IP", "Geo", "Device ID", "Azione", "Categoria", "Dettagli"])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.Stretch)

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
            category = self.category_filter.currentText() if self.category_filter.currentIndex() > 0 else None
            start_date = self.start_date.date().toPyDate()
            end_date = self.end_date.date().toPyDate()

            from datetime import datetime, time
            start_dt = datetime.combine(start_date, time.min)
            end_dt = datetime.combine(end_date, time.max)

            logs = self.api_client.get_audit_logs(limit=500, user_id=user_id, category=category, start_date=start_dt, end_date=end_dt)
            self.table.setRowCount(len(logs))
            for i, log in enumerate(logs):
                ts = log['timestamp']
                if 'T' in ts:
                    ts = ts.replace('T', ' ')
                if '.' in ts:
                    ts = ts.split('.')[0]

                # Format timestamp to DD/MM/YYYY HH:MM:SS if needed, but ISO is usually fine for logs or can be parsed
                try:
                    dt_ts = datetime.fromisoformat(ts)
                    ts = dt_ts.strftime("%d/%m/%Y %H:%M:%S")
                except: pass

                severity = log.get('severity', 'LOW')
                bg_color = None
                if severity == 'CRITICAL':
                    bg_color = QColor("#FECACA") # Light Red
                elif severity == 'MEDIUM':
                    bg_color = QColor("#FFEDD5") # Light Orange

                self.table.setItem(i, 0, QTableWidgetItem(ts))
                self.table.setItem(i, 1, QTableWidgetItem(severity))
                self.table.setItem(i, 2, QTableWidgetItem(log['username']))
                self.table.setItem(i, 3, QTableWidgetItem(log.get('ip_address') or ""))
                self.table.setItem(i, 4, QTableWidgetItem(log.get('geolocation') or ""))
                self.table.setItem(i, 5, QTableWidgetItem(log.get('device_id') or ""))
                self.table.setItem(i, 6, QTableWidgetItem(log['action']))
                self.table.setItem(i, 7, QTableWidgetItem(log.get('category') or ""))

                details_text = str(log.get('details') or "")
                changes_json = log.get('changes')
                if changes_json:
                    try:
                        changes_dict = json.loads(changes_json)
                        if changes_dict:
                            # Format changes: "Key: Old->New"
                            formatted_changes = []
                            for k, v in changes_dict.items():
                                if isinstance(v, dict) and 'old' in v and 'new' in v:
                                    formatted_changes.append(f"{k}: {v['old']} -> {v['new']}")
                                else:
                                    formatted_changes.append(f"{k}: {v}")

                            changes_str = ", ".join(formatted_changes)
                            details_text += f" [Modifiche: {changes_str}]"
                    except: pass

                item_details = QTableWidgetItem(details_text)
                if changes_json:
                     item_details.setToolTip(changes_json)

                self.table.setItem(i, 8, item_details)

                if bg_color:
                    for j in range(9):
                        item = self.table.item(i, j)
                        if item:
                            item.setBackground(bg_color)
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
        self.general_settings = GeneralSettingsWidget(self.api_client)
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

    def set_read_only(self, is_read_only: bool):
        print(f"[DEBUG] ConfigView.set_read_only: {is_read_only}")
        self.is_read_only = is_read_only
        self.save_button.setEnabled(not is_read_only)
        self.import_button.setEnabled(not is_read_only)

        # User Management
        self.user_management_widget.add_btn.setEnabled(not is_read_only)
        self.user_management_widget.edit_btn.setEnabled(not is_read_only)
        self.user_management_widget.delete_btn.setEnabled(not is_read_only)

        # Security
        self.general_settings.db_security_btn.setEnabled(not is_read_only)

        if is_read_only:
            self.save_button.setToolTip("Disabilitato in modalità Sola Lettura")
        else:
            self.save_button.setToolTip("")

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
                self.general_settings.refresh_security_status() # Refresh security status
                if self.stacked_widget.currentIndex() == 2:
                    self.audit_widget.refresh_logs()
        else:
            self.btn_account.setVisible(False)
            self.btn_audit.setVisible(False)

        # Reset to general tab if Account is hidden but active (rare case)
        if not self.btn_account.isVisible() and self.stacked_widget.currentIndex() in [1, 2]:
            self.switch_tab(0)

    def get_env_path(self):
        # Use User Data Directory for configuration to avoid PermissionError in Program Files
        try:
            from app.core.config import get_user_data_dir
            return str(get_user_data_dir() / '.env')
        except ImportError:
            # Fallback if app.core is not accessible
            if os.name == 'nt':
                app_data = os.getenv('LOCALAPPDATA')
                if not app_data:
                     app_data = os.path.expanduser("~\\AppData\\Local")
                base_dir = os.path.join(app_data, "Intelleo")
            else:
                base_dir = os.path.join(os.path.expanduser("~"), ".local", "share", "Intelleo")

            if not os.path.exists(base_dir):
                os.makedirs(base_dir)
            return os.path.join(base_dir, '.env')

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
        if getattr(self, 'is_read_only', False): return

        env_path = self.get_env_path()
        gs = self.general_settings

        old_settings = {
            "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", ""),
            "GOOGLE_CLOUD_PROJECT": os.getenv("GOOGLE_CLOUD_PROJECT", ""),
            "GCS_BUCKET_NAME": os.getenv("GCS_BUCKET_NAME", ""),
            "SMTP_HOST": os.getenv("SMTP_HOST", ""),
            "SMTP_PORT": os.getenv("SMTP_PORT", ""),
            "SMTP_USER": os.getenv("SMTP_USER", ""),
            "SMTP_PASSWORD": os.getenv("SMTP_PASSWORD", ""),
            "EMAIL_RECIPIENTS_TO": os.getenv("EMAIL_RECIPIENTS_TO", ""),
            "EMAIL_RECIPIENTS_CC": os.getenv("EMAIL_RECIPIENTS_CC", ""),
            "ALERT_THRESHOLD_DAYS": os.getenv("ALERT_THRESHOLD_DAYS", "60"),
            "ALERT_THRESHOLD_DAYS_VISITE": os.getenv("ALERT_THRESHOLD_DAYS_VISITE", "30"),
        }

        new_settings = {
            "GEMINI_API_KEY": gs.gemini_api_key_input.text(),
            "GOOGLE_CLOUD_PROJECT": gs.gcp_project_id_input.text(),
            "GCS_BUCKET_NAME": gs.gcs_bucket_name_input.text(),
            "SMTP_HOST": gs.smtp_host_input.text(),
            "SMTP_PORT": gs.smtp_port_input.text(),
            "SMTP_USER": gs.smtp_user_input.text(),
            "SMTP_PASSWORD": gs.smtp_password_input.text(),
            "EMAIL_RECIPIENTS_TO": gs.recipients_to_input.text(),
            "EMAIL_RECIPIENTS_CC": gs.recipients_cc_input.text(),
            "ALERT_THRESHOLD_DAYS": gs.alert_threshold_input.text(),
            "ALERT_THRESHOLD_DAYS_VISITE": gs.alert_threshold_visite_input.text(),
        }

        try:
            for key, value in new_settings.items():
                set_key(env_path, key, value)

            # Calculate Diff
            changes = {}
            for key, val in new_settings.items():
                old_val = old_settings.get(key)
                if old_val != val:
                    if "KEY" in key or "PASSWORD" in key:
                        changes[key] = {"old": "***", "new": "***"}
                    else:
                        changes[key] = {"old": old_val, "new": val}

            changes_json = json.dumps(changes) if changes else None

            # Audit Log
            try:
                self.api_client.create_audit_log(
                    "CONFIG_UPDATE",
                    "Updated application settings.",
                    category="CONFIG",
                    changes=changes_json
                )
            except: pass

            QMessageBox.information(self, "Salvato", "Configurazione salvata. Riavviare per applicare.")
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile salvare: {e}")
