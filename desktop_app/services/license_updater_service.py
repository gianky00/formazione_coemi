import os
import requests
import json
import hashlib
import shutil
import tempfile
from typing import Optional, Dict, Any
from desktop_app.services.path_service import get_license_dir

class LicenseUpdaterService:
    """
    Manages the license update process.
    Can operate in two modes:
    1. API-Dependent: Uses an `api_client` to fetch configuration from the running backend.
    2. Standalone (Headless): Uses a provided `config` dictionary, suitable for startup/launcher.
    """
    def __init__(self, api_client=None, config: Optional[Dict[str, Any]] = None):
        self.api_client = api_client
        self.config = config

    def _load_config(self):
        """Fetches updater config from the backend or uses provided config."""
        if self.config:
            return self.config

        if not self.api_client:
            raise RuntimeError("Nessun client API e nessuna configurazione fornita. Impossibile aggiornare.")

        try:
            response = self.api_client.get("/app_config/config/updater")
            self.config = response
        except Exception as e:
            print(f"Failed to load updater configuration: {e}")
            raise RuntimeError("Impossibile caricare la configurazione per l'aggiornamento.") from e
        return self.config

    @staticmethod
    def get_hardware_id():
        """
        Gets the definitive hardware ID from the centralized service.
        """
        from .hardware_id_service import get_machine_id
        return get_machine_id()

    @staticmethod
    def _calculate_sha256(filepath):
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def update_license(self, hardware_id):
        try:
            config = self._load_config()
        except RuntimeError as e:
            return False, str(e)

        # The configuration might not need a token if the repo is public, but we check for structure.
        if not all([config.get('repo_owner'), config.get('repo_name')]):
            return False, "La configurazione per l'aggiornamento ricevuta dal server è incompleta."

        # The API now requires a token for private repos.
        if not all([config.get('repo_owner'), config.get('repo_name'), config.get('github_token')]):
            return False, "La configurazione per l'aggiornamento ricevuta dal server è incompleta."

        api_url = f"https://api.github.com/repos/{config['repo_owner']}/{config['repo_name']}/contents/licenses/{hardware_id}"
        headers = {'Authorization': f"token {config['github_token']}"}

        try:
            # --- OTTIMIZZAZIONE: Controlla prima solo il manifest ---
            manifest_url = f"{api_url}/manifest.json"
            meta_res = requests.get(manifest_url, headers=headers, timeout=15)
            meta_res.raise_for_status()
            remote_manifest_data = meta_res.json()

            if 'download_url' not in remote_manifest_data:
                raise ValueError("URL di download non trovato per manifest.json.")

            content_res = requests.get(remote_manifest_data['download_url'], timeout=30)
            content_res.raise_for_status()
            remote_manifest = content_res.json()

            # Confronta con il manifest locale, se esiste
            local_manifest_path = os.path.join(get_license_dir(), "manifest.json")
            if os.path.exists(local_manifest_path):
                with open(local_manifest_path, 'r') as f:
                    local_manifest = json.load(f)
                if local_manifest == remote_manifest:
                    return True, "La licenza è già aggiornata all'ultima versione."

            # --- Se i manifest sono diversi, o quello locale non esiste, procedi con il download completo ---
            with tempfile.TemporaryDirectory() as temp_dir:
                # Salva il manifest remoto già scaricato
                with open(os.path.join(temp_dir, "manifest.json"), 'w') as f:
                    json.dump(remote_manifest, f)

                # Scarica gli altri file
                files_to_download = ["pyarmor.rkey", "config.dat"]
                for filename in files_to_download:
                    file_api_url = f"{api_url}/{filename}"
                    meta_res = requests.get(file_api_url, headers=headers, timeout=15)
                    meta_res.raise_for_status()
                    file_meta = meta_res.json()

                    if 'download_url' not in file_meta:
                        raise ValueError(f"URL di download non trovato per {filename}.")

                    content_res = requests.get(file_meta['download_url'], timeout=30)
                    content_res.raise_for_status()

                    with open(os.path.join(temp_dir, filename), "wb") as f:
                        f.write(content_res.content)

                # Verifica i checksum usando il manifest scaricato
                manifest_path = os.path.join(temp_dir, "manifest.json")
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)

                rkey_path = os.path.join(temp_dir, "pyarmor.rkey")
                config_path = os.path.join(temp_dir, "config.dat")

                if manifest["pyarmor.rkey"] != LicenseUpdaterService._calculate_sha256(rkey_path):
                    raise ValueError("Checksum per 'pyarmor.rkey' non valido.")
                if manifest["config.dat"] != LicenseUpdaterService._calculate_sha256(config_path):
                    raise ValueError("Checksum per 'config.dat' non valido.")

                # 3. Atomic Update to User Data Directory (No Elevation Needed)
                target_license_dir = get_license_dir()
                os.makedirs(target_license_dir, exist_ok=True) # Ensure dir exists

                # Move the validated files into the target directory, overwriting existing ones.
                shutil.move(rkey_path, os.path.join(target_license_dir, "pyarmor.rkey"))
                shutil.move(config_path, os.path.join(target_license_dir, "config.dat"))
                shutil.move(manifest_path, os.path.join(target_license_dir, "manifest.json"))

                return True, "Licenza aggiornata con successo. È necessario riavviare l'applicazione."

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return False, f"Nessuna licenza trovata per questo ID hardware ({hardware_id})."
            elif e.response.status_code == 401 or e.response.status_code == 403:
                return False, "Errore di autenticazione: Accesso non autorizzato. Contattare il supporto."
            return False, f"Errore di rete durante il download della licenza. Verificare la connessione."
        except (ValueError, KeyError) as e:
            return False, f"Errore di validazione: {e}"
        except Exception as e:
            return False, f"Errore imprevisto: {e}"


if __name__ == '__main__':
    # For testing purposes
    hw_id = LicenseUpdaterService.get_hardware_id()
    print(f"Detected Hardware ID: {hw_id}")
