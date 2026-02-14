"""
Notification Center Service for Intelleo.
Manages all notifications with persistence and retrieval for the notification bell.
"""

import contextlib
import threading
import tkinter as tk
from collections import deque
from datetime import datetime
from tkinter import ttk
from typing import ClassVar


class Notification:
    """Represents a single notification."""

    def __init__(
        self,
        title,
        message,
        notification_type="info",
        action=None,
        action_label=None,
        category=None,
        priority=0,
    ):
        self.id = id(self)
        self.title = title
        self.message = message
        self.notification_type = notification_type  # info, success, warning, error, alert
        self.action = action  # Callback function
        self.action_label = action_label  # Button label for action
        self.category = category  # e.g., "certificates", "employees", "system"
        self.priority = priority  # Higher = more important
        self.timestamp = datetime.now()
        self.read = False
        self.dismissed = False


class NotificationCenter:
    """
    Central notification management system.
    Stores notifications and provides retrieval for the notification panel.
    """

    MAX_NOTIFICATIONS = 100

    def __init__(self, controller):
        self.controller = controller
        self.notifications = deque(maxlen=self.MAX_NOTIFICATIONS)
        self.on_change_callbacks = []
        self._lock = threading.Lock()

    def add(
        self,
        title,
        message,
        notification_type="info",
        action=None,
        action_label=None,
        category=None,
        priority=0,
        show_toast=True,
    ):
        """Add a new notification."""
        notif = Notification(
            title=title,
            message=message,
            notification_type=notification_type,
            action=action,
            action_label=action_label,
            category=category,
            priority=priority,
        )

        with self._lock:
            self.notifications.appendleft(notif)

        # Show toast if requested
        if show_toast and hasattr(self.controller, "toast_manager"):
            self.controller.toast_manager.show(title, message, notification_type, on_click=action)

        # Notify listeners
        self._notify_change()

        return notif

    def get_all(self, include_dismissed=False):
        """Get all notifications."""
        with self._lock:
            if include_dismissed:
                return list(self.notifications)
            return [n for n in self.notifications if not n.dismissed]

    def get_unread(self):
        """Get unread notifications."""
        with self._lock:
            return [n for n in self.notifications if not n.read and not n.dismissed]

    def get_unread_count(self):
        """Get count of unread notifications."""
        return len(self.get_unread())

    def mark_read(self, notification_id):
        """Mark a notification as read."""
        with self._lock:
            for n in self.notifications:
                if n.id == notification_id:
                    n.read = True
                    break
        self._notify_change()

    def mark_all_read(self):
        """Mark all notifications as read."""
        with self._lock:
            for n in self.notifications:
                n.read = True
        self._notify_change()

    def dismiss(self, notification_id):
        """Dismiss a notification."""
        with self._lock:
            for n in self.notifications:
                if n.id == notification_id:
                    n.dismissed = True
                    break
        self._notify_change()

    def dismiss_all(self):
        """Dismiss all notifications."""
        with self._lock:
            for n in self.notifications:
                n.dismissed = True
        self._notify_change()

    def clear_all(self):
        """Clear all notifications."""
        with self._lock:
            self.notifications.clear()
        self._notify_change()

    def on_change(self, callback):
        """Register a callback for notification changes."""
        self.on_change_callbacks.append(callback)

    def _notify_change(self):
        """Notify all listeners of changes."""
        for callback in self.on_change_callbacks:
            with contextlib.suppress(BaseException):
                self.controller.root.after(0, callback)


class NotificationBell(tk.Frame):
    """
    Notification bell widget with badge showing unread count.
    """

    def __init__(self, parent, notification_center, on_click=None):
        super().__init__(parent, bg="#1E3A8A")
        self.notification_center = notification_center
        self.on_click_callback = on_click

        self.setup_ui()

        # Register for updates
        notification_center.on_change(self.update_badge)
        self.update_badge()

    def setup_ui(self):
        # Bell button
        self.btn_bell = tk.Label(
            self,
            text="\u25a0",  # Will be replaced with icon
            font=("Segoe UI Symbol", 14),
            bg="#1E3A8A",
            fg="white",
            cursor="hand2",
            padx=10,
        )
        self.btn_bell.pack(side="left")

        # Use a bell character
        try:
            self.btn_bell.config(text="\U0001f514")  # Bell emoji
        except Exception:
            self.btn_bell.config(text="[N]")  # Fallback

        # Badge (count)
        self.badge = tk.Label(
            self,
            text="0",
            font=("Segoe UI", 8, "bold"),
            bg="#EF4444",
            fg="white",
            width=2,
            height=1,
        )

        # Bind click
        self.btn_bell.bind("<Button-1>", self._on_click)
        self.badge.bind("<Button-1>", self._on_click)

    def _on_click(self, event):
        if self.on_click_callback:
            self.on_click_callback()

    def update_badge(self):
        """Update the badge count."""
        count = self.notification_center.get_unread_count()

        if count > 0:
            display = str(count) if count < 100 else "99+"
            self.badge.config(text=display)
            self.badge.place(relx=0.7, rely=0.1, anchor="center")

            # Animate badge for new notifications
            self._pulse_badge()
        else:
            self.badge.place_forget()

    def _pulse_badge(self):
        """Simple pulse animation for badge."""

        def pulse_step(step=0):
            if step < 3:
                colors = ["#EF4444", "#F87171", "#EF4444"]
                self.badge.config(bg=colors[step % len(colors)])
                self.after(200, lambda: pulse_step(step + 1))

        pulse_step()


class NotificationPanel(tk.Toplevel):
    """
    Dropdown panel showing all notifications.
    """

    ICONS: ClassVar[dict] = {
        "info": ("i", "#3B82F6"),
        "success": ("\u2713", "#10B981"),
        "warning": ("\u26a0", "#F59E0B"),
        "error": ("\u2717", "#EF4444"),
        "alert": ("!", "#8B5CF6"),
    }

    def __init__(self, parent, notification_center, controller):
        super().__init__(parent)
        self.notification_center = notification_center
        self.controller = controller

        # Window setup
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(bg="#FFFFFF")

        # Add shadow/border effect
        self.config(highlightbackground="#D1D5DB", highlightthickness=1)

        self.setup_ui()
        self.load_notifications()

        # Position near bell
        self.update_idletasks()
        self.position_panel(parent)

        # Close on click outside
        self.bind("<FocusOut>", lambda e: self.after(100, self._check_focus))
        self.focus_set()

    def setup_ui(self):
        # Header
        header = tk.Frame(self, bg="#F3F4F6", height=40)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header, text="Notifiche", font=("Segoe UI", 11, "bold"), bg="#F3F4F6", fg="#1F2937"
        ).pack(side="left", padx=15, pady=8)

        # Actions frame
        actions = tk.Frame(header, bg="#F3F4F6")
        actions.pack(side="right", padx=10)

        self.btn_mark_read = tk.Label(
            actions,
            text="Segna tutto letto",
            font=("Segoe UI", 9),
            fg="#3B82F6",
            bg="#F3F4F6",
            cursor="hand2",
        )
        self.btn_mark_read.pack(side="left", padx=5)
        self.btn_mark_read.bind("<Button-1>", lambda e: self._mark_all_read())

        self.btn_view_all = tk.Label(
            actions,
            text="Vedi tutto",
            font=("Segoe UI", 9),
            fg="#3B82F6",
            bg="#F3F4F6",
            cursor="hand2",
        )
        self.btn_view_all.pack(side="left", padx=5)
        self.btn_view_all.bind("<Button-1>", lambda e: self._open_notifications_view())

        # Scrollable content
        container = tk.Frame(self, bg="#FFFFFF")
        container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(
            container, bg="#FFFFFF", highlightthickness=0, width=380, height=350
        )
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)

        self.scrollable_frame = tk.Frame(self.canvas, bg="#FFFFFF")
        self.scrollable_frame.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=380)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mouse wheel scrolling (bind to canvas only, not all)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)

        # Empty state placeholder
        self.empty_label = tk.Label(
            self.scrollable_frame,
            text="Nessuna notifica",
            font=("Segoe UI", 10),
            fg="#9CA3AF",
            bg="#FFFFFF",
        )

    def _on_mousewheel(self, event):
        try:
            if self.winfo_exists():
                self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception:
            pass

    def load_notifications(self):
        """Load and display notifications."""
        # Clear existing
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        notifications = self.notification_center.get_all()[:20]  # Show last 20

        if not notifications:
            self.empty_label = tk.Label(
                self.scrollable_frame,
                text="Nessuna notifica",
                font=("Segoe UI", 10),
                fg="#9CA3AF",
                bg="#FFFFFF",
                pady=50,
            )
            self.empty_label.pack()
            return

        for notif in notifications:
            self._create_notification_item(notif)

    def _create_notification_item(self, notif):
        """Create a single notification item widget."""
        bg_color = "#F3F4F6" if notif.read else "#EFF6FF"

        frame = tk.Frame(self.scrollable_frame, bg=bg_color, cursor="hand2")
        frame.pack(fill="x", padx=5, pady=2)

        # Content frame
        content = tk.Frame(frame, bg=bg_color, padx=10, pady=8)
        content.pack(fill="x")

        # Icon
        icon, color = self.ICONS.get(notif.notification_type, ("i", "#3B82F6"))
        icon_label = tk.Label(
            content, text=icon, font=("Segoe UI", 12, "bold"), fg=color, bg=bg_color, width=2
        )
        icon_label.pack(side="left", padx=(0, 10))

        # Text content
        text_frame = tk.Frame(content, bg=bg_color)
        text_frame.pack(side="left", fill="x", expand=True)

        # Title with unread indicator
        title_text = notif.title
        if not notif.read:
            title_text = "\u2022 " + title_text  # Bullet point for unread

        title_label = tk.Label(
            text_frame,
            text=title_text,
            font=("Segoe UI", 9, "bold"),
            fg="#1F2937",
            bg=bg_color,
            anchor="w",
        )
        title_label.pack(fill="x")

        # Message (truncated)
        msg = notif.message[:80] + "..." if len(notif.message) > 80 else notif.message
        msg_label = tk.Label(
            text_frame,
            text=msg,
            font=("Segoe UI", 8),
            fg="#6B7280",
            bg=bg_color,
            anchor="w",
            wraplength=280,
        )
        msg_label.pack(fill="x")

        # Time
        time_str = notif.timestamp.strftime("%H:%M")
        if notif.timestamp.date() != datetime.now().date():
            time_str = notif.timestamp.strftime("%d/%m %H:%M")

        time_label = tk.Label(
            text_frame, text=time_str, font=("Segoe UI", 7), fg="#9CA3AF", bg=bg_color, anchor="w"
        )
        time_label.pack(fill="x")

        # Bind click events
        for widget in [frame, content, icon_label, text_frame, title_label, msg_label, time_label]:
            widget.bind("<Button-1>", lambda e, n=notif: self._on_notification_click(n))

        # Separator
        sep = tk.Frame(self.scrollable_frame, bg="#E5E7EB", height=1)
        sep.pack(fill="x")

    def _on_notification_click(self, notif):
        """Handle notification click."""
        self.notification_center.mark_read(notif.id)
        if notif.action:
            notif.action()
        self.destroy()

    def _mark_all_read(self):
        """Mark all notifications as read."""
        self.notification_center.mark_all_read()
        self.load_notifications()

    def _open_notifications_view(self):
        """Open full notifications view."""
        self.destroy()
        # Switch to notifications tab if exists, or open dialog
        if hasattr(self.controller, "current_view") and hasattr(
            self.controller.current_view, "notebook"
        ):
            # Find notifications tab
            notebook = self.controller.current_view.notebook
            for i in range(notebook.index("end")):
                if "Notifiche" in notebook.tab(i, "text"):
                    notebook.select(i)
                    return

        # Open standalone notifications window
        NotificationsWindow(self.controller.root, self.notification_center, self.controller)

    def position_panel(self, parent):
        """Position panel below the bell."""
        try:
            # Get bell position
            x = parent.winfo_rootx()
            y = parent.winfo_rooty() + parent.winfo_height()

            # Adjust if near screen edge
            screen_width = self.winfo_screenwidth()
            panel_width = 400

            if x + panel_width > screen_width:
                x = screen_width - panel_width - 10

            self.geometry(f"{panel_width}x400+{x}+{y}")
        except Exception:
            self.geometry("400x400+100+100")

    def _check_focus(self):
        """Check if focus is still on panel or its children."""
        try:
            focused = self.focus_get()
            if focused is None or (focused != self and not str(focused).startswith(str(self))):
                self.destroy()
        except Exception:
            pass


class NotificationsWindow(tk.Toplevel):
    """
    Full notifications view window with detailed list and suggestions.
    """

    ICONS: ClassVar[dict] = {
        "info": ("i", "#3B82F6"),
        "success": ("\u2713", "#10B981"),
        "warning": ("\u26a0", "#F59E0B"),
        "error": ("\u2717", "#EF4444"),
        "alert": ("!", "#8B5CF6"),
    }

    CATEGORY_LABELS: ClassVar[dict] = {
        "certificates": "Certificati",
        "employees": "Dipendenti",
        "system": "Sistema",
        "training": "Formazione",
    }

    def __init__(self, parent, notification_center, controller):
        super().__init__(parent)
        self.notification_center = notification_center
        self.controller = controller

        self.title("Centro Notifiche - Intelleo")
        self.geometry("800x600")
        self.minsize(600, 400)

        # Make modal
        self.transient(parent)
        self.grab_set()

        self.setup_ui()
        self.load_notifications()

        # Center window
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 800) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 600) // 2
        self.geometry(f"+{x}+{y}")

    def setup_ui(self):
        # Header
        header = tk.Frame(self, bg="#1E3A8A", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header, text="Centro Notifiche", font=("Segoe UI", 14, "bold"), bg="#1E3A8A", fg="white"
        ).pack(side="left", padx=20, pady=15)

        # Action buttons
        btn_frame = tk.Frame(header, bg="#1E3A8A")
        btn_frame.pack(side="right", padx=20)

        tk.Button(
            btn_frame,
            text="Segna tutto letto",
            bg="#3B82F6",
            fg="white",
            command=self._mark_all_read,
            relief="flat",
        ).pack(side="left", padx=5)
        tk.Button(
            btn_frame,
            text="Cancella tutto",
            bg="#6B7280",
            fg="white",
            command=self._clear_all,
            relief="flat",
        ).pack(side="left", padx=5)

        # Main content with sidebar
        main = tk.Frame(self, bg="#F3F4F6")
        main.pack(fill="both", expand=True)

        # Sidebar (filters)
        sidebar = tk.Frame(main, bg="#FFFFFF", width=200)
        sidebar.pack(side="left", fill="y", padx=(10, 0), pady=10)
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar, text="Filtri", font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#1F2937"
        ).pack(anchor="w", padx=15, pady=(15, 10))

        # Filter buttons
        self.filter_var = tk.StringVar(value="all")

        filters = [
            ("all", "Tutte", None),
            ("unread", "Non lette", None),
            ("error", "Errori", "#EF4444"),
            ("warning", "Avvisi", "#F59E0B"),
            ("info", "Info", "#3B82F6"),
        ]

        for value, label, _color in filters:
            rb = tk.Radiobutton(
                sidebar,
                text=label,
                variable=self.filter_var,
                value=value,
                bg="#FFFFFF",
                anchor="w",
                command=self.load_notifications,
            )
            rb.pack(fill="x", padx=15, pady=2)

        # Notifications list
        list_frame = tk.Frame(main, bg="#F3F4F6")
        list_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Scrollable list
        self.canvas = tk.Canvas(
            list_frame, bg="#FFFFFF", highlightthickness=1, highlightbackground="#E5E7EB"
        )
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.canvas.yview)

        self.scrollable_frame = tk.Frame(self.canvas, bg="#FFFFFF")
        self.scrollable_frame.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw"
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Resize canvas window when canvas resizes
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mouse wheel (bind to canvas only, not all)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        try:
            if self.winfo_exists():
                self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception:
            pass

    def load_notifications(self):
        """Load and display filtered notifications."""
        # Clear existing
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        filter_type = self.filter_var.get()
        notifications = self.notification_center.get_all()

        # Apply filter
        if filter_type == "unread":
            notifications = [n for n in notifications if not n.read]
        elif filter_type in ["error", "warning", "info"]:
            notifications = [n for n in notifications if n.notification_type == filter_type]

        if not notifications:
            tk.Label(
                self.scrollable_frame,
                text="Nessuna notifica",
                font=("Segoe UI", 11),
                fg="#9CA3AF",
                bg="#FFFFFF",
                pady=50,
            ).pack()
            return

        for notif in notifications:
            self._create_detailed_notification(notif)

    def _create_detailed_notification(self, notif):
        """Create detailed notification card."""
        bg_color = "#F9FAFB" if notif.read else "#EFF6FF"

        card = tk.Frame(self.scrollable_frame, bg=bg_color, relief="flat")
        card.pack(fill="x", padx=10, pady=5)

        # Card content
        content = tk.Frame(card, bg=bg_color, padx=15, pady=12)
        content.pack(fill="x")

        # Header row
        header_row = tk.Frame(content, bg=bg_color)
        header_row.pack(fill="x")

        # Icon and type
        icon, color = self.ICONS.get(notif.notification_type, ("i", "#3B82F6"))
        type_frame = tk.Frame(header_row, bg=color, padx=8, pady=2)
        type_frame.pack(side="left")
        tk.Label(
            type_frame,
            text=icon + " " + notif.notification_type.upper(),
            font=("Segoe UI", 8, "bold"),
            fg="white",
            bg=color,
        ).pack()

        # Category if present
        if notif.category:
            cat_label = self.CATEGORY_LABELS.get(notif.category, notif.category)
            tk.Label(
                header_row, text=cat_label, font=("Segoe UI", 8), fg="#6B7280", bg=bg_color
            ).pack(side="left", padx=10)

        # Time
        time_str = notif.timestamp.strftime("%d/%m/%Y %H:%M")
        tk.Label(header_row, text=time_str, font=("Segoe UI", 8), fg="#9CA3AF", bg=bg_color).pack(
            side="right"
        )

        # Title
        title_font = ("Segoe UI", 10, "bold") if not notif.read else ("Segoe UI", 10)
        tk.Label(
            content, text=notif.title, font=title_font, fg="#1F2937", bg=bg_color, anchor="w"
        ).pack(fill="x", pady=(8, 4))

        # Message
        tk.Label(
            content,
            text=notif.message,
            font=("Segoe UI", 9),
            fg="#4B5563",
            bg=bg_color,
            anchor="w",
            wraplength=500,
            justify="left",
        ).pack(fill="x")

        # Action buttons
        if notif.action or not notif.read:
            btn_frame = tk.Frame(content, bg=bg_color)
            btn_frame.pack(fill="x", pady=(10, 0))

            if notif.action:
                action_text = notif.action_label or "Vai"
                tk.Button(
                    btn_frame,
                    text=action_text,
                    bg="#3B82F6",
                    fg="white",
                    font=("Segoe UI", 8),
                    relief="flat",
                    command=lambda: self._execute_action(notif),
                ).pack(side="left", padx=(0, 5))

            if not notif.read:
                tk.Button(
                    btn_frame,
                    text="Segna letto",
                    bg="#6B7280",
                    fg="white",
                    font=("Segoe UI", 8),
                    relief="flat",
                    command=lambda n=notif: self._mark_read(n),
                ).pack(side="left", padx=5)

            tk.Button(
                btn_frame,
                text="Elimina",
                bg="#9CA3AF",
                fg="white",
                font=("Segoe UI", 8),
                relief="flat",
                command=lambda n=notif: self._dismiss(n),
            ).pack(side="right")

        # Separator
        sep = tk.Frame(self.scrollable_frame, bg="#E5E7EB", height=1)
        sep.pack(fill="x", padx=10)

    def _execute_action(self, notif):
        """Execute notification action."""
        self.notification_center.mark_read(notif.id)
        if notif.action:
            notif.action()
        self.load_notifications()

    def _mark_read(self, notif):
        """Mark single notification as read."""
        self.notification_center.mark_read(notif.id)
        self.load_notifications()

    def _dismiss(self, notif):
        """Dismiss notification."""
        self.notification_center.dismiss(notif.id)
        self.load_notifications()

    def _mark_all_read(self):
        """Mark all as read."""
        self.notification_center.mark_all_read()
        self.load_notifications()

    def _clear_all(self):
        """Clear all notifications."""
        from tkinter import messagebox

        if messagebox.askyesno("Conferma", "Cancellare tutte le notifiche?"):
            self.notification_center.clear_all()
            self.load_notifications()
