import os
import platform
import queue
import re
import subprocess
import threading
import time
import uuid

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
)

from app.core.path_resolver import get_asset_path as _get_asset_path
from desktop_app.services.license_manager import LicenseManager


def format_date_to_ui(date_val):
    if not date_val or str(date_val).lower() == "none":
        return ""
    date_str = str(date_val)
    if "-" in date_str and len(date_str) >= 10:
        try:
            parts = date_str[:10].split("-")
            return f"{parts[2]}/{parts[1]}/{parts[0]}"
        except (IndexError, ValueError):
            return date_str
    return date_str


def open_file(path):
    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.call(["open", path])
        else:
            subprocess.call(["xdg-open", path])
    except Exception:
        pass


def get_device_id():
    try:
        data = LicenseManager.get_license_data()
        if data and "Hardware ID" in data:
            return data["Hardware ID"]
    except Exception:
        pass
    return str(uuid.getnode())


def get_asset_path(relative_path):
    return str(_get_asset_path(relative_path))


def clean_text_for_display(text: str) -> str:
    if not text:
        return ""
    text = text.replace("á", "a").replace("í", "i").replace("ú", "u")
    text = re.sub(r"[òó](?=[^\W_])", "o", text)
    text = re.sub(r"[èé](?=[^\W_])", "e", text)
    text = re.sub(r"à(?=[^\W_])", "a", text)
    text = re.sub(r"ì(?=[^\W_])", "i", text)
    text = re.sub(r"ù(?=[^\W_])", "u", text)
    return text


class TaskRunner(QDialog):
    """
    Qt version of TaskRunner.
    """

    def __init__(self, parent, title="Elaborazione...", message="Attendere prego..."):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(300, 150)
        self.setWindowModality(Qt.WindowModal)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)
        layout = QVBoxLayout(self)
        self.lbl = QLabel(message)
        self.lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl)
        self.pb = QProgressBar()
        self.pb.setRange(0, 0)
        layout.addWidget(self.pb)
        self.queue = queue.Queue()

    def run(self, target, *args, **kwargs):
        def thread_target():
            try:
                result = target(*args, **kwargs)
                self.queue.put(("success", result))
            except Exception as e:
                self.queue.put(("error", e))

        threading.Thread(target=thread_target, daemon=True).start()
        timer = QTimer(self)
        timer.timeout.connect(self._poll_queue)
        timer.start(100)
        self.exec()
        if not self.queue.empty():
            status, payload = self.queue.get()
            if status == "success":
                return payload
            else:
                raise payload
        return None

    def _poll_queue(self):
        if not self.queue.empty():
            self.accept()


class ProgressTaskRunner(QDialog):
    """
    Qt version of ProgressTaskRunner.
    """

    def __init__(self, parent, title="Elaborazione...", message="Attendere prego..."):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(400, 220)
        self.setWindowModality(Qt.WindowModal)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        self.lbl_msg = QLabel(message)
        self.lbl_msg.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.lbl_msg)
        self.lbl_status = QLabel("Preparazione...")
        layout.addWidget(self.lbl_status)
        self.pb = QProgressBar()
        self.pb.setRange(0, 100)
        layout.addWidget(self.pb)
        time_layout = QHBoxLayout()
        self.lbl_elapsed = QLabel("Trascorso: 0:00")
        self.lbl_remaining = QLabel("Rimanente: --:--")
        time_layout.addWidget(self.lbl_elapsed)
        time_layout.addStretch()
        time_layout.addWidget(self.lbl_remaining)
        layout.addLayout(time_layout)
        self.btn_cancel = QPushButton("Annulla")
        self.btn_cancel.clicked.connect(self._on_cancel)
        layout.addWidget(self.btn_cancel, 0, Qt.AlignCenter)
        self.queue = queue.Queue()
        self.progress_queue = queue.Queue()
        self.start_time = None
        self.cancelled = False

    def run(self, target, items, *args, **kwargs):
        total = len(items)
        if total == 0:
            return []
        self.start_time = time.time()

        def thread_target():
            results, errors = [], []
            try:
                for i, item in enumerate(items):
                    if self.cancelled:
                        break
                    try:
                        self.progress_queue.put((i, total, f"Elaborazione {i + 1}/{total}..."))
                        result = target(item, *args, **kwargs)
                        results.append({"success": True, "result": result, "item": item})
                    except Exception as e:
                        results.append({"success": False, "error": str(e), "item": item})
                        errors.append(str(e))
                self.progress_queue.put((total, total, "Completato!"))
                self.queue.put(("success", {"results": results, "errors": errors}))
            except Exception as e:
                self.queue.put(("error", e))

        threading.Thread(target=thread_target, daemon=True).start()
        timer = QTimer(self)
        timer.timeout.connect(self._poll_queue)
        timer.start(100)
        self.exec()
        if not self.queue.empty():
            status, payload = self.queue.get()
            if status == "success":
                return payload
            else:
                raise payload
        return {"results": [], "errors": ["Operazione annullata"]}

    def _on_cancel(self):
        if QMessageBox.question(self, "Conferma", "Annullare?") == QMessageBox.Yes:
            self.cancelled = True
            self.btn_cancel.setEnabled(False)
            self.lbl_status.setText("Annullamento...")

    def _poll_queue(self):
        while not self.progress_queue.empty():
            current, total, status = self.progress_queue.get()
            self.pb.setValue(int(current / total * 100))
            self.lbl_status.setText(status)
            elapsed = time.time() - self.start_time
            self.lbl_elapsed.setText(f"Trascorso: {self._format_time(elapsed)}")
            if current > 0:
                self.lbl_remaining.setText(
                    f"Rimanente: {self._format_time((elapsed / current) * (total - current))}"
                )
        if not self.queue.empty():
            self.accept()

    def _format_time(self, seconds):
        if seconds < 0:
            return "--:--"
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        return f"{h}:{m:02d}:{s:02d}" if h > 0 else f"{m}:{s:02d}"
