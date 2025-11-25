import os
import requests
import json
import hashlib
import shutil
import tempfile
from desktop_app.services.path_service import get_license_dir

class LicenseUpdaterService:
    def __init__(self, api_client):
        self.api_client = api_client
        self.config = None

    def _load_config(self):
        """Fetches updater config from the backend."""
        if not self.config:
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

        files_to_process = ["pyarmor.rkey", "config.dat", "manifest.json"]

        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # 1. Get file metadata (including download URLs) from GitHub API
                for filename in files_to_process:
                    file_api_url = f"{api_url}/{filename}"
                    meta_res = requests.get(file_api_url, headers=headers, timeout=15)
                    meta_res.raise_for_status()
                    file_meta = meta_res.json()

                    if 'download_url' not in file_meta:
                        raise ValueError(f"URL di download non trovato per {filename}.")

                    # 2. Download the actual file content from the download_url
                    content_res = requests.get(file_meta['download_url'], timeout=30)
                    content_res.raise_for_status()

                    with open(os.path.join(temp_dir, filename), "wb") as f:
                        f.write(content_res.content)

                # 2. Verify checksums
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

                # Move the validated files into the target directory, overwriting existing ones.
                # shutil.move is generally atomic on modern OSes.
                shutil.move(rkey_path, os.path.join(target_license_dir, "pyarmor.rkey"))
                shutil.move(config_path, os.path.join(target_license_dir, "config.dat"))
                # We can also move the manifest for future reference if needed
                shutil.move(manifest_path, os.path.join(target_license_dir, "manifest.json"))

                return True, "Licenza aggiornata con successo. Riavvia l'applicazione."

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    return False, f"Nessuna licenza trovata per l'ID hardware: {hardware_id}."
                return False, f"Errore di rete: {e}"
            except (ValueError, KeyError) as e:
                return False, f"Errore di validazione: {e}"
            except Exception as e:
                return False, f"Errore imprevisto: {e}"


if __name__ == '__main__':
    # For testing purposes
    hw_id = LicenseUpdaterService.get_hardware_id()
    print(f"Detected Hardware ID: {hw_id}")

    # Example of how to call the update
    # print("\nAttempting to update license...")
    # success, message = LicenseUpdaterService.update_license(hw_id)
    # print(f"Result: {success} - {message}")
