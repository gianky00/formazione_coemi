
import pandas as pd
import requests
from PyQt6.QtCore import QObject, pyqtSignal
from ..api_client import API_URL

class DashboardViewModel(QObject):
    data_changed = pyqtSignal()
    error_occurred = pyqtSignal(str)
    operation_completed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._df_original = pd.DataFrame()
        self._df_filtered = pd.DataFrame()

    @property
    def filtered_data(self):
        return self._df_filtered

    def load_data(self):
        try:
            response = requests.get(f"{API_URL}/certificati/?validated=true")
            response.raise_for_status()
            data = response.json()
            self._df_original = pd.DataFrame(data) if data else pd.DataFrame()
            self._df_filtered = self._df_original.copy()
            self.data_changed.emit()
        except requests.exceptions.RequestException as e:
            self._df_original = pd.DataFrame()
            self._df_filtered = pd.DataFrame()
            self.error_occurred.emit(f"Impossibile caricare i dati: {e}")
            self.data_changed.emit()

    def filter_data(self, dipendente, categoria, stato):
        if self._df_original.empty:
            return

        df_filtered = self._df_original.copy()

        if dipendente != "Tutti":
            df_filtered = df_filtered[df_filtered['nome'] == dipendente]

        if categoria != "Tutti":
            df_filtered = df_filtered[df_filtered['categoria'] == categoria]

        if stato != "Tutti":
            df_filtered = df_filtered[df_filtered['stato_certificato'] == stato]

        self._df_filtered = df_filtered
        self.data_changed.emit()

    def get_filter_options(self):
        if self._df_original.empty:
            return {"dipendenti": [], "categorie": [], "stati": []}

        dipendenti = sorted(self._df_original['nome'].unique())
        categorie = sorted(self._df_original['categoria'].unique())
        stati = sorted(self._df_original['stato_certificato'].unique())

        return {"dipendenti": dipendenti, "categorie": categorie, "stati": stati}

    def delete_certificates(self, ids):
        if not ids:
            return

        success_count = 0
        error_messages = []
        for cert_id in ids:
            try:
                response = requests.delete(f"{API_URL}/certificati/{cert_id}")
                response.raise_for_status()
                success_count += 1
            except requests.exceptions.RequestException as e:
                error_messages.append(f"ID {cert_id}: {e}")

        if success_count > 0:
            self.operation_completed.emit(f"{success_count} certificati cancellati con successo.")
            self.load_data()

        if error_messages:
            full_error_message = "Si sono verificati alcuni errori:\n" + "\n".join(error_messages)
            self.error_occurred.emit(full_error_message)

    def update_certificate(self, cert_id, data):
        try:
            response = requests.put(f"{API_URL}/certificati/{cert_id}", json=data)
            response.raise_for_status()
            self.operation_completed.emit("Certificato aggiornato con successo.")
            self.load_data()
            return True
        except requests.exceptions.RequestException as e:
            self.error_occurred.emit(f"Impossibile modificare il certificato: {e}")
            return False
