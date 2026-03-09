from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app import __version__ as app_version
from desktop_app.utils.worker import Worker


class LoginView(QWidget):
    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # Center container
        self.container = QFrame()
        self.container.setObjectName("LoginContainer")
        self.container.setFixedSize(400, 450)

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(40, 40, 40, 40)
        container_layout.setSpacing(15)

        # Logo/Title
        self.lbl_title = QLabel("Intelleo")
        self.lbl_title.setObjectName("LoginTitle")
        self.lbl_title.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(self.lbl_title)

        self.lbl_subtitle = QLabel("Predict. Validate. Automate.")
        self.lbl_subtitle.setObjectName("LoginSubtitle")
        self.lbl_subtitle.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(self.lbl_subtitle)

        container_layout.addSpacing(20)

        # Fields
        container_layout.addWidget(QLabel("Username"))
        self.entry_user = QLineEdit()
        self.entry_user.setPlaceholderText("Inserisci username")
        container_layout.addWidget(self.entry_user)

        container_layout.addWidget(QLabel("Password"))
        self.entry_pass = QLineEdit()
        self.entry_pass.setEchoMode(QLineEdit.Password)
        self.entry_pass.setPlaceholderText("Inserisci password")
        self.entry_pass.returnPressed.connect(self.do_login)
        container_layout.addWidget(self.entry_pass)

        # Button
        self.btn_login = QPushButton("ACCEDI")
        self.btn_login.setProperty("class", "PrimaryButton")
        self.btn_login.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_login.clicked.connect(self.do_login)
        container_layout.addWidget(self.btn_login)

        # Status
        self.lbl_status = QLabel("")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setObjectName("StatusLabel")
        container_layout.addWidget(self.lbl_status)

        # Centering
        h_layout = QHBoxLayout()
        h_layout.addStretch()
        h_layout.addWidget(self.container)
        h_layout.addStretch()
        main_layout.addStretch()
        main_layout.addLayout(h_layout)
        main_layout.addStretch()

        # Footer
        footer = QLabel(f"Versione: {app_version}")
        footer.setStyleSheet("color: #6B7280; font-size: 11px;")
        main_layout.addWidget(footer, 0, Qt.AlignRight)

    def do_login(self):
        username = self.entry_user.text().strip()
        password = self.entry_pass.text().strip()

        if not username or not password:
            self.lbl_status.setText("Inserisci credenziali")
            return

        self._set_loading(True)
        self.lbl_status.setText("Connessione in corso...")
        self.lbl_status.setStyleSheet("color: blue;")

        # Create Worker
        worker = Worker(self.controller.api_client.login, username, password)
        worker.signals.result.connect(self.controller.on_login_success)
        worker.signals.error.connect(self._on_login_error)
        worker.signals.finished.connect(lambda: self._set_loading(False))

        # Execute in Pool
        self.controller.thread_pool.start(worker)

    def _set_loading(self, loading):
        self.entry_user.setEnabled(not loading)
        self.entry_pass.setEnabled(not loading)
        self.btn_login.setEnabled(not loading)

    def _on_login_error(self, error_tuple):
        _, value, _ = error_tuple
        msg = str(value)
        if "401" in msg:
            msg = "Credenziali non valide."
        self.lbl_status.setText(msg)
        self.lbl_status.setStyleSheet("color: red;")
        self.entry_pass.clear()
        self.entry_pass.setFocus()
