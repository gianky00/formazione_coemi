import os
import sys
import uuid
import re
import threading
import queue
import time
import tkinter as tk
from tkinter import ttk
from desktop_app.services.license_manager import LicenseManager
from app.core.path_resolver import get_asset_path as _get_asset_path

import platform
import subprocess

def format_date_to_ui(date_val):
    """
    Standardizes date display to DD/MM/YYYY across the UI.
    Handles ISO strings (YYYY-MM-DD) and None values.
    """
    if not date_val or str(date_val).lower() == "none":
        return ""
    
    date_str = str(date_val)
    if "-" in date_str and len(date_str) >= 10:
        try:
            # ISO format YYYY-MM-DD
            parts = date_str[:10].split("-")
            return f"{parts[2]}/{parts[1]}/{parts[0]}"
        except:
            return date_str
    return date_str

def open_file(path):
    """
    Opens a file with the default system application in a cross-platform way.
    """
    try:
        if platform.system() == 'Windows':
            os.startfile(path)
        elif platform.system() == 'Darwin': # macOS
            subprocess.call(['open', path])
        else: # Linux
            subprocess.call(['xdg-open', path])
    except Exception as e:
        print(f"Error opening file: {e}")

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


class ProgressTaskRunner:
    """
    Runs a batch task with a determinate progress bar and ETA estimation.
    Shows: progress bar, current item, elapsed time, and estimated time remaining.
    """
    def __init__(self, parent, title="Elaborazione...", message="Attendere prego..."):
        self.parent = parent
        self.title = title
        self.message = message
        self.queue = queue.Queue()
        self.progress_queue = queue.Queue()
        self.dialog = None
        self.start_time = None
        self.total = 0
        self.current = 0
        self.cancelled = False

    def run(self, target, items, *args, **kwargs):
        """
        Runs the task on a list of items with progress tracking.
        target: Function to call for each item. Signature: target(item, progress_callback, *args, **kwargs)
                The progress_callback should be called with (current_index, total, status_message)
        items: List of items to process
        Returns: List of results or raises exception
        """
        self.total = len(items)
        if self.total == 0:
            return []

        self._create_dialog()
        self.start_time = time.time()

        # Wrap target to process items
        def thread_target():
            results = []
            errors = []
            try:
                for i, item in enumerate(items):
                    if self.cancelled:
                        break
                    try:
                        # Update progress
                        self.progress_queue.put((i, self.total, f"Elaborazione {i+1}/{self.total}..."))
                        result = target(item, *args, **kwargs)
                        results.append({"success": True, "result": result, "item": item})
                    except Exception as e:
                        results.append({"success": False, "error": str(e), "item": item})
                        errors.append(str(e))

                # Final update
                self.progress_queue.put((self.total, self.total, "Completato!"))
                self.queue.put(("success", {"results": results, "errors": errors}))
            except Exception as e:
                self.queue.put(("error", e))

        thread = threading.Thread(target=thread_target, daemon=True)
        thread.start()

        # Start polling
        self.parent.after(100, self._poll_queue)

        # Wait for window to close
        self.parent.wait_window(self.dialog)

        # Process result
        if not self.queue.empty():
            status, payload = self.queue.get()
            if status == "success":
                return payload
            else:
                raise payload
        return {"results": [], "errors": ["Operazione annullata"]}

    def _format_time(self, seconds):
        """Format seconds as HH:MM:SS or MM:SS."""
        if seconds < 0:
            return "--:--"
        if seconds >= 3600:
            h = int(seconds // 3600)
            m = int((seconds % 3600) // 60)
            s = int(seconds % 60)
            return f"{h}:{m:02d}:{s:02d}"
        else:
            m = int(seconds // 60)
            s = int(seconds % 60)
            return f"{m}:{s:02d}"

    def _create_dialog(self):
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(self.title)
        self.dialog.geometry("400x200")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # Center the dialog
        self.dialog.update_idletasks()
        x = self.parent.winfo_rootx() + (self.parent.winfo_width() // 2) - 200
        y = self.parent.winfo_rooty() + (self.parent.winfo_height() // 2) - 100
        self.dialog.geometry(f"+{x}+{y}")

        # Main frame
        frame = ttk.Frame(self.dialog, padding=20)
        frame.pack(fill="both", expand=True)

        # Message
        self.lbl_message = ttk.Label(frame, text=self.message, font=("Segoe UI", 10))
        self.lbl_message.pack(pady=(0, 10))

        # Status label (current item)
        self.lbl_status = ttk.Label(frame, text="Preparazione...", font=("Segoe UI", 9))
        self.lbl_status.pack(pady=(0, 5))

        # Progress bar
        self.progressbar = ttk.Progressbar(frame, mode="determinate", maximum=100)
        self.progressbar.pack(fill="x", pady=5)

        # Time labels frame
        time_frame = ttk.Frame(frame)
        time_frame.pack(fill="x", pady=5)

        self.lbl_elapsed = ttk.Label(time_frame, text="Trascorso: 0:00", font=("Segoe UI", 9))
        self.lbl_elapsed.pack(side="left")

        self.lbl_remaining = ttk.Label(time_frame, text="Rimanente: --:--", font=("Segoe UI", 9))
        self.lbl_remaining.pack(side="right")

        # Progress percentage
        self.lbl_percent = ttk.Label(frame, text="0%", font=("Segoe UI", 10, "bold"))
        self.lbl_percent.pack(pady=5)

        # Cancel button
        self.btn_cancel = ttk.Button(frame, text="Annulla", command=self._on_cancel)
        self.btn_cancel.pack(pady=(10, 0))

        # Disable close button
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _on_cancel(self):
        if tk.messagebox.askyesno("Conferma", "Annullare l'operazione in corso?"):
            self.cancelled = True
            self.btn_cancel.config(state="disabled")
            self.lbl_status.config(text="Annullamento in corso...")

    def _poll_queue(self):
        # Check for progress updates
        while not self.progress_queue.empty():
            try:
                current, total, status = self.progress_queue.get_nowait()
                self.current = current

                # Update progress bar
                progress_pct = (current / total * 100) if total > 0 else 0
                self.progressbar["value"] = progress_pct
                self.lbl_percent.config(text=f"{int(progress_pct)}%")
                self.lbl_status.config(text=status)

                # Calculate times
                elapsed = time.time() - self.start_time
                self.lbl_elapsed.config(text=f"Trascorso: {self._format_time(elapsed)}")

                if current > 0:
                    avg_time_per_item = elapsed / current
                    remaining_items = total - current
                    eta = avg_time_per_item * remaining_items
                    self.lbl_remaining.config(text=f"Rimanente: {self._format_time(eta)}")
            except queue.Empty:
                break

        # Check for completion
        if not self.queue.empty():
            self.dialog.destroy()
        else:
            self.dialog.after(100, self._poll_queue)
