import contextlib
import os
import sqlite3
import sys
from pathlib import Path
from typing import Any

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QFileDialog, 
    QVBoxLayout, QWidget, QStackedWidget
)
from PySide6.QtCore import Qt, QTimer

from app import __version__ as app_version
from app.core.config import settings
from desktop_app.api_client import APIClient
from desktop_app.services.license_manager import LicenseManager
from desktop_app.services.notification_center import NotificationCenter
from desktop_app.services.proactive_service import ProactiveService
from desktop_app.services.toast_service import ToastManager
from desktop_app.services.update_checker import UpdateChecker
from desktop_app.services.voice_service import VoiceService

# Import View
from desktop_app.views.login_view import LoginView


class ApplicationController(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        
        self.setWindowTitle("Intelleo")
        self.resize(1024, 768)
        self.setMinimumSize(800, 600)
        
        # Central Widget for View Management
        self.central_stack = QStackedWidget()
        self.setCentralWidget(self.central_stack)

        # Maximize window on startup
        self.showMaximized()

        self.api_client = APIClient()
        self.voice_service = VoiceService()
        self.toast_manager = ToastManager(self)
        self.notification_center = NotificationCenter(self)
        self.proactive_service: Any = None

        # Inactivity Timer
        self.inactivity_timer = QTimer(self)
        self.inactivity_timer.setSingleShot(True)
        self.inactivity_timer.timeout.connect(self._on_inactivity)
        self.INACTIVITY_TIMEOUT_MS = 3600 * 1000  # 1 hour
        
        # Install Event Filter for inactivity
        QApplication.instance().installEventFilter(self)

    def eventFilter(self, obj, event):
        # Reset timer on any interaction
        try:
            from PySide6.QtCore import QEvent
            if event and event.type() in [QEvent.MouseButtonPress, QEvent.KeyPress, QEvent.Wheel]:
                self._reset_inactivity_timer()
        except Exception:
            pass
        return super().eventFilter(obj, event)

    def start(self) -> None:
        # 1. License Check
        if not self._check_license():
            sys.exit(1)

        # 2. Database Check
        if not self._check_database():
            sys.exit(1)

        # 3. Update Check (Async)
        self._check_updates()

        self.show()
        self.show_login()
        self._reset_inactivity_timer()

    def _check_updates(self) -> None:
        checker = UpdateChecker(app_version)

        def on_update(has_update: bool, version: str, url: str) -> None:
            if has_update:
                # Use QTimer to ensure UI thread interaction
                QTimer.singleShot(0, lambda: self._prompt_update(version, url))

        checker.check_for_updates(on_update)

    def _prompt_update(self, version: str, url: str) -> None:
        if QMessageBox.question(
            self, "Aggiornamento Disponibile", 
            f"Nuova versione {version} disponibile. Scaricare ora?",
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes:
            import webbrowser
            webbrowser.open(url)

    def _check_license(self) -> bool:
        try:
            data = LicenseManager.get_license_data()
            return True
        except Exception as e:
            QMessageBox.critical(self, "Errore Licenza", f"Impossibile avviare l'applicazione:\n{e}")
            return False

    def _check_database(self) -> bool:
        db_path = settings.DATABASE_PATH
        path_obj = Path(db_path) if db_path else None

        if path_obj and path_obj.exists() and path_obj.is_file():
            return True
        return self._prompt_db_recovery(path_obj)

    def _prompt_db_recovery(self, current_path: Path | None) -> bool:
        msg = f"Il database non è stato trovato al percorso:\n{current_path}\n\nÈ necessario selezionare un database esistente o crearne uno nuovo."
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Database Mancante")
        msg_box.setText(msg)
        select_btn = msg_box.addButton("Seleziona Esistente", QMessageBox.AcceptRole)
        create_btn = msg_box.addButton("Crea Nuovo", QMessageBox.RejectRole)
        msg_box.addButton(QMessageBox.Cancel)
        
        msg_box.exec()
        clicked = msg_box.clickedButton()

        if clicked == select_btn:
            path, _ = QFileDialog.getOpenFileName(
                self, "Seleziona Database", "", "SQLite DB (*.db);;All Files (*)"
            )
            if path:
                self._update_db_setting(path)
                return True
        elif clicked == create_btn:
            dir_path = QFileDialog.getExistingDirectory(self, "Seleziona Cartella per Nuovo Database")
            if dir_path:
                new_path = os.path.join(dir_path, "database_documenti.db")
                self._initialize_new_database(new_path)
                self._update_db_setting(new_path)
                return True

        return False

    def _update_db_setting(self, path: str) -> None:
        settings.save_mutable_settings({"DATABASE_PATH": str(path)})
        QMessageBox.information(
            self, "Riavvio Richiesto",
            "La configurazione del database è cambiata. L'applicazione verrà riavviata.",
        )
        self._restart_app()

    def _initialize_new_database(self, path_str: str) -> None:
        try:
            conn = sqlite3.connect(path_str)
            conn.execute("PRAGMA journal_mode=DELETE;")
            conn.commit()
            conn.close()

            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            from app.db.models import Base
            from app.db.seeding import seed_database

            db_url = f"sqlite:///{path_str}"
            engine = create_engine(db_url)
            Base.metadata.create_all(bind=engine)

            SessionLocal = sessionmaker(bind=engine)
            db = SessionLocal()
            seed_database(db)
            db.close()
        except Exception as e:
            QMessageBox.critical(self, "Errore Creazione", f"Impossibile creare il database:\n{e}")
            sys.exit(1)

    def _restart_app(self) -> None:
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def show_login(self) -> None:
        login_view = LoginView(self)
        self.central_stack.addWidget(login_view)
        self.central_stack.setCurrentWidget(login_view)

    def show_dashboard(self) -> None:
        from desktop_app.views.dashboard_view import DashboardView
        dashboard_view = DashboardView(self)
        self.central_stack.addWidget(dashboard_view)
        self.central_stack.setCurrentWidget(dashboard_view)

        # Voice Welcome
        name = self.api_client.user_info.get("account_name", "") if self.api_client.user_info else ""
        self.voice_service.speak(f"Benvenuto {name}")

        self.proactive_service = ProactiveService(
            self, self.toast_manager, self.notification_center
        )
        self.proactive_service.run_startup_analysis()

    def on_login_success(self, user_info: dict[str, Any]) -> None:
        is_read_only = user_info.get("read_only", False)
        lock_owner = user_info.get("lock_owner")

        if is_read_only:
            owner_str = str(lock_owner) if lock_owner else "un altro utente"
            QMessageBox.warning(
                self, "Modalità Sola Lettura",
                f"Il database è attualmente bloccato da {owner_str}.\n"
                "L'applicazione funzionerà in modalità limitata (niente modifiche).",
            )

        self.api_client.set_token(user_info)
        self.show_dashboard()
        self._reset_inactivity_timer()

    def logout(self) -> None:
        with contextlib.suppress(Exception):
            self.api_client.logout()
        self.show_login()

    def closeEvent(self, event) -> None:
        if QMessageBox.question(
            self, "Esci", "Vuoi davvero uscire?",
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes:
            self.logout()
            self.voice_service.cleanup()
            event.accept()
        else:
            event.ignore()

    def show_toast(self, title: str, message: str, toast_type: str = "info", duration: int = 5000, on_click: Any = None) -> None:
        if self.toast_manager:
            self.toast_manager.show(title, message, toast_type, duration, on_click)

    def _reset_inactivity_timer(self) -> None:
        self.inactivity_timer.start(self.INACTIVITY_TIMEOUT_MS)

    def _on_inactivity(self) -> None:
        # Check if we are already in login view
        if isinstance(self.centralWidget().currentWidget(), LoginView):
            return
        QMessageBox.warning(self, "Sessione Scaduta", "Disconnessione per inattività.")
        self.logout()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Style (Fusion for modern look)
    app.setStyle("Fusion")
    
    controller = ApplicationController()
    controller.start()
    sys.exit(app.exec())
