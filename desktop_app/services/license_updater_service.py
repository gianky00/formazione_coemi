import subprocess
import sys
import os
import requests
import json
import hashlib
import shutil
import tempfile

class LicenseUpdaterService:
    def __init__(self, api_client):
        self.api_client = api_client
        self.config = None

    def _load_config(self):
        """Fetches updater config from the backend."""
        if not self.config:
            try:
                response = self.api_client.get("/config/updater")
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

        if not all([config.get('github_token'), config.get('repo_owner'), config.get('repo_name')]):
            return False, "La configurazione per l'aggiornamento ricevuta dal server è incompleta."

        base_url = f"https://api.github.com/repos/{config['repo_owner']}/{config['repo_name']}/contents/licenses/{hardware_id}"
        headers = {
            "Authorization": f"token {config['github_token']}",
            "Accept": "application/vnd.github.v3.raw"
        }

        files_to_download = ["pyarmor.rkey", "config.dat", "manifest.json"]

        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # 1. Download files
                for filename in files_to_download:
                    url = f"{base_url}/{filename}"
                    res = requests.get(url, headers=headers, timeout=15)
                    res.raise_for_status()

                    with open(os.path.join(temp_dir, filename), "wb") as f:
                        f.write(res.content)

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

                # 3. Atomic Update with Elevated Privileges (Windows)
                if os.name != 'nt':
                    return False, "L'aggiornamento automatico della licenza e' supportato solo su Windows."

                if getattr(sys, 'frozen', False):
                    # In a frozen app, the executable is the base
                    base_dir = os.path.dirname(sys.executable)
                    python_exe = sys.executable # The frozen app itself
                else:
                    # In dev, we need to find the python interpreter
                    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
                    python_exe = sys.executable

                target_dir = os.path.join(base_dir, "Licenza")

                # The paths to our helper scripts
                vbs_script = os.path.join(base_dir, "tools", "elevate.vbs")
                copy_script = os.path.join(base_dir, "tools", "copy_license.py")

                # The command to execute with elevation
                command = [
                    "cscript",
                    f'"{vbs_script}"',
                    f'"{python_exe}"',
                    f'"{copy_script}"',
                    f'"{temp_dir}"',
                    f'"{target_dir}"'
                ]

                proc = subprocess.Popen(" ".join(command), shell=True)
                proc.wait() # Wait for the elevated process to complete

                # Check if the elevated script reported an error
                error_log = os.path.join(temp_dir, "copy_error.log")
                if os.path.exists(error_log):
                    with open(error_log, "r") as f:
                        error_details = f.read()
                    raise RuntimeError(f"Errore durante la copia dei file con privilegi elevati: {error_details}")

                # If we reach here, the copy was successful
                return True, "Licenza aggiornata con successo. Riavvia l'applicazione."

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    return False, f"Nessuna licenza trovata per l'ID: {hardware_id}."
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
