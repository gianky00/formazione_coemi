"""
Toast Notification Service for Intelleo.
Provides non-intrusive notifications that appear in the corner of the screen.
"""
import tkinter as tk
from tkinter import ttk
import threading
from collections import deque


class ToastNotification(tk.Toplevel):
    """A single toast notification window."""

    TYPES = {
        "info": {"bg": "#3B82F6", "icon": "i"},
        "success": {"bg": "#10B981", "icon": "✓"},
        "warning": {"bg": "#F59E0B", "icon": "⚠"},
        "error": {"bg": "#EF4444", "icon": "✕"},
        "alert": {"bg": "#8B5CF6", "icon": "!"},
    }

    def __init__(self, parent, title, message, toast_type="info", duration=5000, on_click=None, position_offset=0):
        super().__init__(parent)
        self.on_click = on_click
        self.duration = duration
        self._fade_id = None

        # Window configuration
        self.overrideredirect(True)  # No window decorations
        self.attributes('-topmost', True)
        self.attributes('-alpha', 0.0)  # Start invisible for fade-in

        config = self.TYPES.get(toast_type, self.TYPES["info"])

        # Main frame
        self.frame = tk.Frame(self, bg=config["bg"], cursor="hand2" if on_click else "arrow")
        self.frame.pack(fill="both", expand=True, padx=2, pady=2)

        # Content frame
        content = tk.Frame(self.frame, bg=config["bg"], padx=15, pady=12)
        content.pack(fill="both", expand=True)

        # Icon
        icon_label = tk.Label(content, text=config["icon"], font=("Segoe UI", 16, "bold"),
                              bg=config["bg"], fg="white")
        icon_label.pack(side="left", padx=(0, 10))

        # Text container
        text_frame = tk.Frame(content, bg=config["bg"])
        text_frame.pack(side="left", fill="both", expand=True)

        # Title
        title_label = tk.Label(text_frame, text=title, font=("Segoe UI", 10, "bold"),
                               bg=config["bg"], fg="white", anchor="w")
        title_label.pack(fill="x")

        # Message (wrap text)
        msg_label = tk.Label(text_frame, text=message, font=("Segoe UI", 9),
                             bg=config["bg"], fg="white", anchor="w", justify="left",
                             wraplength=280)
        msg_label.pack(fill="x")

        # Close button
        close_btn = tk.Label(content, text="×", font=("Segoe UI", 14, "bold"),
                             bg=config["bg"], fg="white", cursor="hand2")
        close_btn.pack(side="right", padx=(10, 0))
        close_btn.bind("<Button-1>", lambda e: self.close())

        # Bind click event
        if on_click:
            for widget in [self.frame, content, icon_label, title_label, msg_label, text_frame]:
                widget.bind("<Button-1>", lambda e: self._handle_click())

        # Position window
        self.update_idletasks()
        width = 350
        height = self.winfo_reqheight()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = screen_width - width - 20
        y = screen_height - height - 60 - position_offset  # Above taskbar

        self.geometry(f"{width}x{height}+{x}+{y}")

        # Start fade-in
        self._fade_in()

    def _fade_in(self, alpha=0.0):
        if alpha < 0.95:
            self.attributes('-alpha', alpha)
            self.after(20, lambda: self._fade_in(alpha + 0.1))
        else:
            self.attributes('-alpha', 0.95)
            # Schedule auto-close
            if self.duration > 0:
                self._fade_id = self.after(self.duration, self._fade_out)

    def _fade_out(self, alpha=0.95):
        if alpha > 0.05:
            self.attributes('-alpha', alpha)
            self._fade_id = self.after(30, lambda: self._fade_out(alpha - 0.1))
        else:
            self.close()

    def _handle_click(self):
        if self.on_click:
            self.on_click()
        self.close()

    def close(self):
        if self._fade_id:
            self.after_cancel(self._fade_id)
        try:
            self.destroy()
        except:
            pass


class ToastManager:
    """Manages toast notifications queue and display."""

    def __init__(self, parent):
        self.parent = parent
        self.active_toasts = []
        self.queue = deque()
        self.max_visible = 3  # Reduced to prevent overlap
        self.toast_height = 90
        self.toast_gap = 15  # Increased gap between toasts
        self.last_show_time = 0
        self.min_delay_between_toasts = 800  # Minimum delay between showing toasts (ms)

    def show(self, title, message, toast_type="info", duration=5000, on_click=None):
        """Show a toast notification."""
        import time
        current_time = int(time.time() * 1000)

        if len(self.active_toasts) >= self.max_visible:
            # Queue it with delay to prevent overlap
            self.queue.append((title, message, toast_type, duration, on_click))
            return

        # Enforce minimum delay between toasts
        time_since_last = current_time - self.last_show_time
        if time_since_last < self.min_delay_between_toasts and self.active_toasts:
            # Queue it to be shown after delay
            delay = self.min_delay_between_toasts - time_since_last
            self.parent.after(delay, lambda: self.show(title, message, toast_type, duration, on_click))
            return

        self.last_show_time = current_time
        offset = len(self.active_toasts) * (self.toast_height + self.toast_gap)
        toast = ToastNotification(
            self.parent, title, message, toast_type, duration, on_click, offset
        )
        self.active_toasts.append(toast)

        # Schedule cleanup check
        self.parent.after(duration + 500, self._cleanup)

    def _cleanup(self):
        """Remove closed toasts and show queued ones."""
        self.active_toasts = [t for t in self.active_toasts if t.winfo_exists()]

        # Reposition remaining toasts
        for i, toast in enumerate(self.active_toasts):
            try:
                offset = i * (self.toast_height + self.toast_gap)
                x = toast.winfo_x()
                screen_height = toast.winfo_screenheight()
                y = screen_height - toast.winfo_height() - 60 - offset
                toast.geometry(f"+{x}+{y}")
            except:
                pass

        # Show queued toasts
        while self.queue and len(self.active_toasts) < self.max_visible:
            title, message, toast_type, duration, on_click = self.queue.popleft()
            self.show(title, message, toast_type, duration, on_click)

    def show_info(self, title, message, duration=7000, on_click=None):
        self.show(title, message, "info", duration, on_click)

    def show_success(self, title, message, duration=6000, on_click=None):
        self.show(title, message, "success", duration, on_click)

    def show_warning(self, title, message, duration=10000, on_click=None):
        self.show(title, message, "warning", duration, on_click)

    def show_error(self, title, message, duration=12000, on_click=None):
        self.show(title, message, "error", duration, on_click)

    def show_alert(self, title, message, duration=10000, on_click=None):
        self.show(title, message, "alert", duration, on_click)
