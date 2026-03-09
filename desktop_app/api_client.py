from desktop_app.api.auth_api import AuthAPI
from desktop_app.api.base_client import BaseAPIClient
from desktop_app.api.certificati_api import CertificatiAPI
from desktop_app.api.dipendenti_api import DipendentiAPI
from desktop_app.api.system_api import SystemAPI


class APIClient(BaseAPIClient):
    """
    Client API composito per Intelleo.
    Mantiene la compatibilità con le View legacy pur essendo modularizzato internamente.
    """

    def __init__(self):
        super().__init__()
        self.auth = AuthAPI(self)
        self.dipendenti = DipendentiAPI(self)
        self.certificati = CertificatiAPI(self)
        self.system = SystemAPI(self)

    # --- Auth Compatibility ---
    def login(self, u, p):
        return self.auth.login(u, p)

    def logout(self):
        self.auth.logout()

    def change_password(self, o, n):
        return self.auth.change_password(o, n)

    def set_token(self, token_data):
        self.access_token = token_data.get("access_token")
        self.user_info = {
            "id": token_data.get("user_id"),
            "username": token_data.get("username"),
            "account_name": token_data.get("account_name"),
            "gender": token_data.get("gender"),
            "is_admin": token_data.get("is_admin"),
            "read_only": token_data.get("read_only", False),
            "lock_owner": token_data.get("lock_owner"),
            "previous_login": token_data.get("previous_login"),
            "require_password_change": token_data.get("require_password_change", False),
        }

    # --- Dipendenti Compatibility ---
    def get_dipendenti_list(self):
        return self.dipendenti.list()

    def get_dipendente_detail(self, id):
        return self.dipendenti.get(id)

    def create_dipendente(self, d):
        return self.dipendenti.create(d)

    def update_dipendente(self, id, d):
        return self.dipendenti.update(id, d)

    def delete_dipendente(self, id):
        return self.dipendenti.delete(id)

    def import_dipendenti_csv(self, path):
        return self.dipendenti.import_csv(path)

    # --- Certificati Compatibility ---
    def update_certificato(self, id, d):
        return self.certificati.update(id, d)

    def delete_certificato(self, id):
        return self.certificati.delete(id)

    # --- System Compatibility ---
    def trigger_maintenance(self):
        return self.system.trigger_maintenance()

    def get_lock_status(self):
        return self.system.get_lock_status()

    def get_users(self):
        return self.system.get_users()

    def update_user(self, id, d):
        return self.system.update_user(id, d)

    def delete_user(self, id):
        return self.system.delete_user(id)

    def create_user(self, u, p, is_admin=False):
        return self.system.create_user({"username": u, "password": p, "is_admin": is_admin})

    def get_mutable_config(self):
        return self.system.get_config()

    def update_mutable_config(self, d):
        return self.system.update_config(d)

    def get_audit_logs(self, **kwargs):
        return self.system.get_audit_logs(**kwargs)

    # --- Altro ---
    def send_chat_message(self, message, history=None):
        payload = {"message": message, "history": history or []}
        return self.post("/chat/", json=payload)
