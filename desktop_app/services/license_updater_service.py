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
        Executes the 'pyarmor hdinfo' command to get the definitive hardware ID.
        This ensures the ID matches what the license generator expects.
        """
        try:
            # In a development environment, run as a module. In a frozen app,
            # this will fail gracefully and move to the exception block.
            cmd = [sys.executable, "-m", "pyarmor.cli", "hdinfo"]

            # Set startup info for Windows to hide the console window
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                startupinfo=startupinfo
            )

            # Parse the output to find the disk serial
            for line in result.stdout.splitlines():
                if "Harddisk serial number is" in line:
                    hw_id = line.split()[-1]
                    print(f"PyArmor hdinfo successful: {hw_id}")
                    return hw_id

            print("PyArmor hdinfo ran but did not find a harddisk serial.")
            # If parsing fails, fall through to the exception block's fallback
            raise RuntimeError("Could not parse hdinfo output.")

        except (subprocess.CalledProcessError, FileNotFoundError, RuntimeError) as e:
            print(f"Could not get hardware ID from pyarmor ({e}), falling back to MAC address.")
            from desktop_app.utils import get_device_id
            hw_id = get_device_id()
            print(f"Fallback MAC address ID: {hw_id}")
            return hw_id
        except Exception as e:
            print(f"An unexpected error occurred while getting hardware ID: {e}")
            from desktop_app.utils import get_device_id
            return get_device_id()

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

                # 3. Atomic Update
                if getattr(sys, 'frozen', False):
                    base_dir = os.path.dirname(sys.executable)
                else:
                    base_dir = os.path.dirname(os.path.abspath(__file__)) # This is not ideal for dev

                target_dir = os.path.join(base_dir, "Licenza")
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)

                # Backup existing files
                backup_dir = os.path.join(base_dir, "Licenza_backup")
                if os.path.exists(target_dir):
                    if os.path.exists(backup_dir): shutil.rmtree(backup_dir)
                    shutil.move(target_dir, backup_dir)
                    os.makedirs(target_dir) # Recreate empty target

                try:
                    shutil.move(rkey_path, os.path.join(target_dir, "pyarmor.rkey"))
                    shutil.move(config_path, os.path.join(target_dir, "config.dat"))

                    # Success, cleanup backup
                    if os.path.exists(backup_dir):
                        shutil.rmtree(backup_dir)

                    return True, "Licenza aggiornata con successo. Riavvia l'applicazione."

                except Exception as move_err:
                    # Restore from backup
                    if os.path.exists(backup_dir):
                        if os.path.exists(target_dir): shutil.rmtree(target_dir)
                        shutil.move(backup_dir, target_dir)
                    raise move_err # Re-raise

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
