
import pandas as pd
import requests
from PyQt6.QtCore import QObject, pyqtSignal, QThreadPool
from ..api_client import APIClient
from ..workers.data_worker import FetchCertificatesWorker, DeleteCertificatesWorker, UpdateCertificateWorker

class DatabaseViewModel(QObject):
    data_changed = pyqtSignal()
    error_occurred = pyqtSignal(str)
    operation_completed = pyqtSignal(str)
    loading_changed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self._df_original = pd.DataFrame()
        self._df_filtered = pd.DataFrame()
        self.api_client = APIClient()
        self.threadpool = QThreadPool()

    @property
    def filtered_data(self):
        return self._df_filtered

    def load_data(self):
        self.loading_changed.emit(True)
        worker = FetchCertificatesWorker(self.api_client, validated=True)
        worker.signals.result.connect(self._on_data_loaded)
        worker.signals.error.connect(self._on_error)
        # worker.signals.finished.connect(lambda: self.loading_changed.emit(False))
        # Better handle finished in _on_data_loaded to avoid race conditions/flicker?
        # Actually finished is emitted finally.

        # We'll use a wrapper or just connect directly.
        worker.signals.finished.connect(self._on_worker_finished)
        self.threadpool.start(worker)

    def _on_worker_finished(self):
        self.loading_changed.emit(False)

    def _on_data_loaded(self, data):
        if data:
            self._df_original = pd.DataFrame(data)
            # The API returns 'nome' pre-formatted as "COGNOME NOME"
            self._df_original.rename(columns={
                'nome': 'Dipendente',
                'data_rilascio': 'DATA_EMISSIONE',
                'corso': 'DOCUMENTO'
            }, inplace=True)
        else:
            self._df_original = pd.DataFrame()

        self._df_filtered = self._df_original.copy()
        self.data_changed.emit()

    def _on_error(self, error_message):
        self._df_original = pd.DataFrame()
        self._df_filtered = pd.DataFrame()
        # Ensure error_message is always a string
        safe_msg = str(error_message) if error_message else "Errore sconosciuto"
        self.error_occurred.emit(f"Errore durante il caricamento: {safe_msg}")
        self.data_changed.emit()

    def filter_data(self, dipendente, categoria, stato, search_text=""):
        if self._df_original.empty:
            return

        df_filtered = self._df_original.copy()

        if dipendente != "Tutti":
            df_filtered = df_filtered[df_filtered['Dipendente'] == dipendente]

        if categoria != "Tutti":
            df_filtered = df_filtered[df_filtered['categoria'] == categoria]

        if stato != "Tutti":
            # Map display state back to database state
            db_stato = stato
            if stato == "in scadenza":
                db_stato = "in_scadenza"
            df_filtered = df_filtered[df_filtered['stato_certificato'] == db_stato]

        if search_text:
            search_text = search_text.lower()
            mask = pd.Series([False] * len(df_filtered), index=df_filtered.index)

            # Columns to search in
            search_cols = ['Dipendente', 'DOCUMENTO', 'matricola', 'categoria']

            for col in search_cols:
                if col in df_filtered.columns:
                    # Robust string conversion and search
                    mask |= df_filtered[col].astype(str).str.lower().str.contains(search_text, na=False, regex=False)

            df_filtered = df_filtered[mask]

        self._df_filtered = df_filtered
        self.data_changed.emit()

    def get_filter_options(self):
        if self._df_original.empty:
            return {"dipendenti": [], "categorie": [], "stati": []}

        # Sorting might be slightly slow for 7k rows but negligible compared to network
        dipendenti = sorted(self._df_original['Dipendente'].unique())
        categorie = sorted(self._df_original['categoria'].unique())
        stati_db = sorted(self._df_original['stato_certificato'].unique())

        stati = [s.replace("in_scadenza", "in scadenza") for s in stati_db]

        return {"dipendenti": dipendenti, "categorie": categorie, "stati": stati}

    def delete_certificates(self, ids):
        if not ids:
            return

        self.loading_changed.emit(True)
        worker = DeleteCertificatesWorker(self.api_client, ids)
        worker.signals.result.connect(self._on_delete_completed)
        worker.signals.error.connect(self._on_error)
        worker.signals.finished.connect(self._on_worker_finished)
        self.threadpool.start(worker)

    def _on_delete_completed(self, result):
        success = result.get("success", 0)
        errors = result.get("errors", [])

        if success > 0:
            self.operation_completed.emit(f"{success} certificati cancellati con successo.")
            # Reload data to reflect changes
            self.load_data()

        if errors:
            full_error = "Alcuni errori:\n" + "\n".join(errors)
            self.error_occurred.emit(full_error)

    def update_certificate(self, cert_id, data):
        self.loading_changed.emit(True)
        worker = UpdateCertificateWorker(self.api_client, cert_id, data)
        worker.signals.result.connect(self._on_update_completed)
        worker.signals.error.connect(self._on_error)
        worker.signals.finished.connect(self._on_worker_finished)
        self.threadpool.start(worker)

    def _on_update_completed(self, success):
        if success:
            self.operation_completed.emit("Certificato aggiornato con successo.")
            self.load_data()
