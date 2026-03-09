from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.core.config import settings as local_settings
from desktop_app.utils import TaskRunner
from desktop_app.views.audit_view import AuditView


class ConfigView(QWidget):
    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        self.tabs.addTab(SettingsTab(self.controller), "Impostazioni")
        self.tabs.addTab(UsersTab(self.controller), "Gestione Utenti")
        self.tabs.addTab(AuditView(self.controller), "Audit Log")
        layout.addWidget(self.tabs)

    def refresh_data(self):
        pass


class SettingsTab(QScrollArea):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWidgetResizable(True)
        self.setStyleSheet("border: none;")
        self.content = QWidget()
        self.setWidget(self.content)
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QVBoxLayout(self.content)
        layout.setContentsMargins(30, 30, 30, 30)
        self.form = QFormLayout()
        self.form.setSpacing(15)

        self._add_header(layout, "Percorsi Sistema")
        self.edit_db = QLineEdit()
        self.edit_db.setReadOnly(True)
        self.form.addRow("Percorso Database:", self.edit_db)

        self._add_header(layout, "Integrazione AI")
        self.edit_gemini_analysis = QLineEdit()
        self.edit_gemini_analysis.setEchoMode(QLineEdit.Password)
        self.form.addRow("Gemini API Key (Analisi):", self.edit_gemini_analysis)
        self.edit_gemini_chat = QLineEdit()
        self.edit_gemini_chat.setEchoMode(QLineEdit.Password)
        self.form.addRow("Gemini API Key (Chat):", self.edit_gemini_chat)
        self.check_voice = QCheckBox("Abilita Assistente Vocale")
        self.form.addRow("", self.check_voice)

        self._add_header(layout, "Configurazione Email")
        self.edit_server = QLineEdit()
        self.form.addRow("Server SMTP:", self.edit_server)
        self.edit_port = QLineEdit()
        self.form.addRow("Porta:", self.edit_port)
        self.edit_email = QLineEdit()
        self.form.addRow("Email Mittente:", self.edit_email)
        self.edit_password = QLineEdit()
        self.edit_password.setEchoMode(QLineEdit.Password)
        self.form.addRow("Password:", self.edit_password)

        layout.addLayout(self.form)

        self.btn_save = QPushButton("SALVA TUTTO")
        self.btn_save.setProperty("class", "PrimaryButton")
        self.btn_save.clicked.connect(self.save_settings)
        layout.addWidget(self.btn_save)
        layout.addStretch()

    def _add_header(self, layout, text):
        lbl = QLabel(text)
        lbl.setProperty("class", "SectionHeader")
        layout.addWidget(lbl)

    def load_settings(self):
        try:
            data = self.controller.api_client.get_mutable_config()
            self.edit_db.setText(data.get("DATABASE_PATH", ""))
            self.edit_gemini_analysis.setText(data.get("GEMINI_API_KEY_ANALYSIS", ""))
            self.edit_gemini_chat.setText(data.get("GEMINI_API_KEY_CHAT", ""))
            self.check_voice.setChecked(data.get("VOICE_ASSISTANT_ENABLED", True))
            self.edit_server.setText(data.get("SMTP_SERVER", ""))
            self.edit_port.setText(str(data.get("SMTP_PORT", "587")))
            self.edit_email.setText(data.get("SMTP_USERNAME", ""))
        except Exception:
            pass

    def save_settings(self):
        data = {
            "GEMINI_API_KEY_ANALYSIS": self.edit_gemini_analysis.text(),
            "GEMINI_API_KEY_CHAT": self.edit_gemini_chat.text(),
            "VOICE_ASSISTANT_ENABLED": self.check_voice.isChecked(),
            "SMTP_SERVER": self.edit_server.text(),
            "SMTP_PORT": int(self.edit_port.text()) if self.edit_port.text().isdigit() else 587,
            "SMTP_USERNAME": self.edit_email.text(),
            "SMTP_PASSWORD": self.edit_password.text(),
        }
        try:
            TaskRunner(self, "Salvataggio").run(
                lambda: self.controller.api_client.update_mutable_config(data)
            )
            local_settings.save_mutable_settings(data)
            QMessageBox.information(self, "Successo", "Impostazioni salvate.")
        except Exception as e:
            QMessageBox.critical(self, "Errore", str(e))


class UsersTab(QWidget):
    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.setup_ui()
        self.refresh_users()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        toolbar = QHBoxLayout()
        btn_new = QPushButton("Nuovo Utente")
        btn_new.setProperty("class", "SuccessButton")
        btn_new.clicked.connect(self.add_user)
        toolbar.addWidget(btn_new)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Username", "Ruolo", "Ultimo Accesso"])
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.doubleClicked.connect(self.on_edit_user)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

    def refresh_users(self):
        try:
            users = self.controller.api_client.get_users()
            self.table.setRowCount(0)
            for u in users:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(u["id"])))
                self.table.setItem(row, 1, QTableWidgetItem(u["username"]))
                self.table.setItem(
                    row, 2, QTableWidgetItem("Admin" if u.get("is_admin") else "User")
                )
                self.table.setItem(row, 3, QTableWidgetItem(u.get("last_login", "")))
        except Exception:
            pass

    def add_user(self):
        if UserDialog(self, self.controller).exec():
            self.refresh_users()

    def on_edit_user(self):
        row = self.table.currentRow()
        if row >= 0:
            uid, uname = self.table.item(row, 0).text(), self.table.item(row, 1).text()
            is_adm = self.table.item(row, 2).text() == "Admin"
            if UserDialog(self, self.controller, uid, uname, is_adm).exec():
                self.refresh_users()


class UserDialog(QDialog):
    def __init__(self, parent, controller, user_id=None, username="", is_admin=False):
        super().__init__(parent)
        self.controller, self.user_id = controller, user_id
        self.setWindowTitle("Utente")
        self.setFixedWidth(350)
        self.setup_ui(username, is_admin)

    def setup_ui(self, username, is_admin):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.edit_user = QLineEdit(username)
        self.edit_pass = QLineEdit()
        self.edit_pass.setEchoMode(QLineEdit.Password)
        self.check_admin = QCheckBox("Amministratore")
        self.check_admin.setChecked(is_admin)
        form.addRow("Username:", self.edit_user)
        form.addRow("Password:", self.edit_pass)
        form.addRow("", self.check_admin)
        layout.addLayout(form)

        btn_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        if self.user_id:
            btn_del = QPushButton("ELIMINA")
            btn_del.setProperty("class", "DangerButton")
            btn_del.clicked.connect(self.delete_user)
            layout.addWidget(btn_del)
        btn_box.accepted.connect(self.save)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def save(self):
        data = {"username": self.edit_user.text(), "is_admin": self.check_admin.isChecked()}
        if self.edit_pass.text():
            data["password"] = self.edit_pass.text()
        try:
            if self.user_id:
                self.controller.api_client.update_user(self.user_id, data)
            else:
                self.controller.api_client.create_user(
                    data["username"], data.get("password", ""), is_admin=data["is_admin"]
                )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Errore", str(e))

    def delete_user(self):
        if QMessageBox.question(self, "Conferma", "Eliminare utente?") == QMessageBox.Yes:
            try:
                self.controller.api_client.delete_user(self.user_id)
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Errore", str(e))
