import os
import sys
import uuid
import re
import threading
import queue
import tkinter as tk
from tkinter import ttk
from desktop_app.services.license_manager import LicenseManager
from app.core.path_resolver import get_asset_path as _get_asset_path

def get_device_id():
    """
    Retrieves the device fingerprint.
    """
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
    """
    Removes phonetic stress accents for visual display.
    """
    if not text:
        return ""
    text = text.replace('á', 'a')
    text = text.replace('í', 'i')
    text = text.replace('ú', 'u')
    text = re.sub(r'[òó](?=[^\W_])', 'o', text)
    text = re.sub(r'[èé](?=[^\W_])', 'e', text)
    text = re.sub(r'à(?=[^\W_])', 'a', text)
    text = re.sub(r'ì(?=[^\W_])', 'i', text)
    text = re.sub(r'ù(?=[^\W_])', 'u', text)
    return text

class TaskRunner:
    """
    Runs a task in a separate thread while showing a modal blocking dialog.
    This ensures serial execution and prevents UI interaction, avoiding race conditions.
    """
    def __init__(self, parent, title="Elaborazione...", message="Attendere prego..."):
        self.parent = parent
        self.title = title
        self.message = message
        self.queue = queue.Queue()
        self.dialog = None

    def run(self, target, *args, **kwargs):
        """
        Starts the task.
        target: The function to run.
        args, kwargs: Arguments for the function.
        Returns: The result of the function or raises the exception it raised.
        """
        self._create_dialog()

        # Wrap target to capture result/exception
        def thread_target():
            try:
                result = target(*args, **kwargs)
                self.queue.put(("success", result))
            except Exception as e:
                self.queue.put(("error", e))

        thread = threading.Thread(target=thread_target, daemon=True)
        thread.start()

        # Start polling
        self.parent.after(100, self._poll_queue)

        # Wait for window to close (blocking the main loop effectively for the user)
        self.parent.wait_window(self.dialog)

        # Process result
        if not self.queue.empty():
            status, payload = self.queue.get()
            if status == "success":
                return payload
            else:
                raise payload
        return None

    def _create_dialog(self):
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(self.title)
        self.dialog.geometry("300x150")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set() # Modal

        # Center the dialog
        self.dialog.update_idletasks()
        x = self.parent.winfo_rootx() + (self.parent.winfo_width() // 2) - (150)
        y = self.parent.winfo_rooty() + (self.parent.winfo_height() // 2) - (75)
        self.dialog.geometry(f"+{x}+{y}")

        # Content
        lbl = ttk.Label(self.dialog, text=self.message, font=("Segoe UI", 10))
        lbl.pack(pady=20)

        pb = ttk.Progressbar(self.dialog, mode="indeterminate")
        pb.pack(fill="x", padx=20, pady=10)
        pb.start(10)

        # Disable close button
        self.dialog.protocol("WM_DELETE_WINDOW", lambda: None)

    def _poll_queue(self):
        if not self.queue.empty():
            self.dialog.destroy()
        else:
            self.dialog.after(100, self._poll_queue)
