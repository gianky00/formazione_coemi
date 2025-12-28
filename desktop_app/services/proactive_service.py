"""
Proactive Notification Service for Intelleo.
Analyzes data and provides intelligent suggestions and alerts.
"""
import threading
from datetime import datetime, timedelta
from collections import defaultdict


class ProactiveService:
    """
    Proactive service that monitors data and provides intelligent notifications.
    """

    def __init__(self, controller, toast_manager, notification_center=None):
        self.controller = controller
        self.toast = toast_manager
        self.notification_center = notification_center
        self.analysis_complete = False
        self.last_analysis = None

    def run_startup_analysis(self):
        """Run analysis in background after login."""
        thread = threading.Thread(target=self._analyze_all, daemon=True)
        thread.start()

    def _analyze_all(self):
        """Perform comprehensive analysis of all data."""
        try:
            # Small delay to let dashboard load
            import time
            time.sleep(2)

            # Fetch data
            certificates = self.controller.api_client.get("certificati", params={"validated": "true"})
            pending = self.controller.api_client.get("certificati", params={"validated": "false"})
            dipendenti = self.controller.api_client.get_dipendenti_list()

            # Run all analyses
            self._analyze_expiring_certificates(certificates)
            self._analyze_pending_validations(pending)  # Also handles orphans
            self._analyze_incomplete_employees(dipendenti)
            self._analyze_training_groups(certificates)
            self._suggest_maintenance()

            self.analysis_complete = True
            self.last_analysis = datetime.now()

        except Exception as e:
            print(f"Proactive analysis error: {e}")

    def _analyze_expiring_certificates(self, certificates):
        """Analyze expiring and expired certificates."""
        today = datetime.now().date()
        expired = []
        expiring_soon = []  # Within 30 days
        expiring_60 = []    # Within 60 days

        for cert in certificates:
            scadenza = cert.get("data_scadenza")
            if not scadenza or scadenza.lower() == "none":
                continue

            try:
                exp_date = datetime.strptime(scadenza, "%d/%m/%Y").date()
                days_left = (exp_date - today).days
                cert_info = {
                    "nome": cert.get("nome"),
                    "corso": cert.get("corso"),
                    "categoria": cert.get("categoria"),
                    "days_left": days_left,
                    "scadenza": scadenza
                }

                if days_left < 0:
                    expired.append(cert_info)
                elif days_left <= 30:
                    expiring_soon.append(cert_info)
                elif days_left <= 60:
                    expiring_60.append(cert_info)
            except:
                continue

        # Show notifications
        if expired:
            self._notify_on_main_thread(
                "error",
                f"{len(expired)} Certificati Scaduti!",
                self._format_cert_list(expired[:3], len(expired)),
                lambda: self._go_to_tab(3),  # Scadenzario
                category="certificates",
                action_label="Vai a Scadenzario"
            )

        if expiring_soon:
            self._notify_on_main_thread(
                "warning",
                f"{len(expiring_soon)} in Scadenza (30 giorni)",
                self._format_cert_list(expiring_soon[:3], len(expiring_soon)),
                lambda: self._go_to_tab(3),
                category="certificates",
                action_label="Vai a Scadenzario"
            )

        if expiring_60 and not expiring_soon:
            self._notify_on_main_thread(
                "alert",
                f"{len(expiring_60)} in Scadenza (60 giorni)",
                "Pianifica il rinnovo per tempo.",
                lambda: self._go_to_tab(3),
                category="certificates",
                action_label="Vai a Scadenzario"
            )

    def _analyze_pending_validations(self, pending):
        """Analyze pending certificate validations - separate orphans from regular pending."""
        if not pending:
            return

        # Separate orphans from certificates to validate
        orphans = [c for c in pending if not c.get("dipendente_id") and not c.get("matricola")]
        to_validate = [c for c in pending if c.get("dipendente_id") or c.get("matricola")]

        # Notify about certificates to validate
        if to_validate:
            count = len(to_validate)
            if count > 10:
                self._notify_on_main_thread(
                    "warning",
                    f"{count} Certificati da Convalidare",
                    "Sono presenti molti certificati in attesa di convalida.",
                    lambda: self._go_to_tab(1),  # Convalida
                    category="certificates",
                    action_label="Vai a Convalida"
                )
            else:
                self._notify_on_main_thread(
                    "info",
                    f"{count} Certificati da Convalidare",
                    "Clicca per visualizzare e convalidare.",
                    lambda: self._go_to_tab(1),
                    category="certificates",
                    action_label="Vai a Convalida"
                )

        # Notify about orphan certificates separately
        if orphans:
            count = len(orphans)
            self._notify_on_main_thread(
                "alert",
                f"{count} Certificati Orfani",
                "Certificati non associati a nessun dipendente. Verificare le anagrafiche.",
                lambda: self._go_to_tab(1),
                category="certificates",
                action_label="Vai a Convalida"
            )

    def _analyze_incomplete_employees(self, dipendenti):
        """Find employees with missing data."""
        incomplete = []

        for dip in dipendenti:
            missing = []
            if not dip.get("matricola"):
                missing.append("matricola")
            if not dip.get("data_nascita"):
                missing.append("data nascita")
            if not dip.get("mansione"):
                missing.append("mansione")

            if missing:
                incomplete.append({
                    "nome": f"{dip.get('cognome', '')} {dip.get('nome', '')}",
                    "missing": missing
                })

        if incomplete:
            self._notify_on_main_thread(
                "warning",
                f"{len(incomplete)} Dipendenti Incompleti",
                f"Dati mancanti: {', '.join(incomplete[0]['missing'][:2])}...",
                lambda: self._go_to_tab(4)  # Dipendenti
            )

    def _analyze_training_groups(self, certificates):
        """Group employees by expiring courses for training planning."""
        today = datetime.now().date()
        groups = defaultdict(list)

        for cert in certificates:
            scadenza = cert.get("data_scadenza")
            if not scadenza or scadenza.lower() == "none":
                continue

            try:
                exp_date = datetime.strptime(scadenza, "%d/%m/%Y").date()
                days_left = (exp_date - today).days

                if 0 < days_left <= 90:  # Expiring in next 3 months
                    categoria = cert.get("categoria", "ALTRO")
                    corso = cert.get("corso", "")
                    key = f"{categoria}"
                    groups[key].append({
                        "nome": cert.get("nome"),
                        "corso": corso,
                        "scadenza": scadenza,
                        "days_left": days_left
                    })
            except:
                continue

        # Find groups with multiple people (potential group training)
        large_groups = [(cat, emps) for cat, emps in groups.items() if len(emps) >= 3]

        if large_groups:
            largest = max(large_groups, key=lambda x: len(x[1]))
            cat, emps = largest

            self._notify_on_main_thread(
                "info",
                f"Suggerimento: Corso {cat}",
                f"{len(emps)} dipendenti in scadenza. Considera formazione di gruppo!",
                lambda: self._show_training_plan(cat, emps)
            )

    def _suggest_maintenance(self):
        """Suggest running maintenance if not done recently."""
        # This is a simple heuristic - could be enhanced
        self._notify_on_main_thread(
            "info",
            "Suggerimento",
            "Ricorda di eseguire backup periodici del database.",
            lambda: self._go_to_tab(6),  # Configurazione
            duration=4000
        )

    def _format_cert_list(self, certs, total):
        """Format a short list of certificates."""
        lines = []
        for c in certs:
            lines.append(f"• {c['nome']}: {c['categoria']}")
        if total > len(certs):
            lines.append(f"... e altri {total - len(certs)}")
        return "\n".join(lines)

    def _notify_on_main_thread(self, toast_type, title, message, on_click=None, duration=6000,
                                category=None, action_label=None):
        """Schedule notification on main thread and add to notification center."""
        def notify():
            # Show toast
            if toast_type == "error":
                self.toast.show_error(title, message, duration, on_click)
            elif toast_type == "warning":
                self.toast.show_warning(title, message, duration, on_click)
            elif toast_type == "success":
                self.toast.show_success(title, message, duration, on_click)
            elif toast_type == "alert":
                self.toast.show_alert(title, message, duration, on_click)
            else:
                self.toast.show_info(title, message, duration, on_click)

            # Add to notification center (without showing toast again)
            if self.notification_center:
                priority = {"error": 3, "warning": 2, "alert": 1, "info": 0, "success": 0}.get(toast_type, 0)
                self.notification_center.add(
                    title=title,
                    message=message,
                    notification_type=toast_type,
                    action=on_click,
                    action_label=action_label or "Vai",
                    category=category,
                    priority=priority,
                    show_toast=False  # Already shown above
                )

        self.controller.root.after(100, notify)

    def _go_to_tab(self, tab_index):
        """Navigate to a specific tab."""
        try:
            if hasattr(self.controller.current_view, 'notebook'):
                self.controller.current_view.notebook.select(tab_index)
        except:
            pass

    def _show_training_plan(self, categoria, employees):
        """Show a training plan suggestion dialog."""
        from tkinter import Toplevel, Label, Frame, Button, Text, Scrollbar, END

        dialog = Toplevel(self.controller.root)
        dialog.title(f"Piano Formazione: {categoria}")
        dialog.geometry("500x400")
        dialog.transient(self.controller.root)
        dialog.grab_set()

        # Header
        header = Frame(dialog, bg="#1E3A8A", height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        Label(header, text=f"Piano Formazione - {categoria}",
              font=("Segoe UI", 12, "bold"), bg="#1E3A8A", fg="white").pack(pady=12)

        # Content
        content = Frame(dialog, padx=20, pady=15)
        content.pack(fill="both", expand=True)

        Label(content, text=f"Dipendenti con {categoria} in scadenza nei prossimi 90 giorni:",
              font=("Segoe UI", 10, "bold"), anchor="w").pack(fill="x", pady=(0, 10))

        # Employee list
        text_frame = Frame(content)
        text_frame.pack(fill="both", expand=True)

        scrollbar = Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")

        text = Text(text_frame, font=("Consolas", 9), yscrollcommand=scrollbar.set, height=12)
        text.pack(fill="both", expand=True)
        scrollbar.config(command=text.yview)

        # Sort by expiry
        sorted_emps = sorted(employees, key=lambda x: x['days_left'])

        for emp in sorted_emps:
            days = emp['days_left']
            status = "SCADUTO" if days < 0 else f"{days} giorni"
            text.insert(END, f"• {emp['nome']}\n")
            text.insert(END, f"  Corso: {emp['corso']}\n")
            text.insert(END, f"  Scadenza: {emp['scadenza']} ({status})\n\n")

        text.config(state="disabled")

        # Suggestion
        Label(content, text=f"Suggerimento: Organizza un corso di gruppo per {len(employees)} persone.",
              font=("Segoe UI", 9, "italic"), fg="#059669").pack(fill="x", pady=10)

        # Close button
        Button(content, text="Chiudi", command=dialog.destroy,
               bg="#3B82F6", fg="white", font=("Segoe UI", 10)).pack(pady=10)

    def notify_sync_complete(self, success=True, message=""):
        """Notify when sync is complete."""
        if success:
            self._notify_on_main_thread(
                "success",
                "Sincronizzazione Completata",
                message or "I file sono stati sincronizzati correttamente.",
                duration=4000
            )
        else:
            self._notify_on_main_thread(
                "error",
                "Sincronizzazione Fallita",
                message or "Si è verificato un errore durante la sincronizzazione.",
                duration=6000
            )

    def notify_action_required(self, title, message, action=None):
        """Show a notification that requires user attention."""
        self._notify_on_main_thread("alert", title, message, action, duration=8000)
