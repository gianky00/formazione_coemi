"""
Path Resolution Utility - Compatible con Dev, PyInstaller, Nuitka.

Questo modulo fornisce funzioni universali per la risoluzione dei path
che funzionano in tutti gli ambienti di esecuzione:
- Development mode (script Python)
- PyInstaller frozen (sys._MEIPASS)
- Nuitka compiled (sys.executable parent)

Author: Migration Team
Version: 1.0.0 (Nuitka Migration)
"""

import logging
import os
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def get_base_path() -> Path:
    """
    Ritorna il path base dell'applicazione.

    Compatibile con:
    - Dev mode: Cartella root del progetto (3 livelli sopra questo file)
    - PyInstaller: sys._MEIPASS (cartella temporanea estrazione)
    - Nuitka: Directory dell'eseguibile (sys.executable parent)

    Returns:
        Path: Path base assoluto dell'applicazione.

    Examples:
        >>> # Dev mode
        >>> get_base_path()
        WindowsPath('C:/Users/.../intelleo')

        >>> # Nuitka frozen
        >>> get_base_path()
        WindowsPath('C:/Program Files/Intelleo')
    """
    if getattr(sys, "frozen", False):
        # Modalità Frozen (PyInstaller o Nuitka)
        if hasattr(sys, "_MEIPASS"):
            # PyInstaller: usa la cartella di estrazione temporanea
            return Path(sys._MEIPASS)
        else:
            # Nuitka (o altro packager): usa la directory dell'eseguibile
            return Path(sys.executable).parent
    else:
        # Dev mode: script Python
        # Ritorna la root del progetto (3 livelli sopra: path_resolver.py -> core -> app -> root)
        return Path(__file__).resolve().parent.parent.parent


def get_asset_path(relative_path: str) -> Path:
    """
    Risolve un path relativo a un asset embedded nell'applicazione.

    Gli asset sono file distribuiti con l'applicazione (non dati utente),
    come la React SPA, icone, documentazione, etc.

    Args:
        relative_path: Path relativo dalla root dell'app.
            Esempio: "guide_frontend/dist/index.html"

    Returns:
        Path: Path assoluto all'asset.

    Note:
        Se l'asset non esiste, viene loggato un warning ma il path
        viene comunque ritornato (per permettere gestione errore al chiamante).

    Examples:
        >>> get_asset_path("guide_frontend/dist/index.html")
        WindowsPath('C:/Program Files/Intelleo/guide_frontend/dist/index.html')

        >>> get_asset_path("desktop_app/icons/icon.ico")
        WindowsPath('C:/Program Files/Intelleo/desktop_app/icons/icon.ico')
    """
    base = get_base_path()
    asset = base / relative_path

    # Log warning se asset non trovato (utile per debug)
    if not asset.exists():
        logger.warning(f"Asset non trovato: {asset}")

    return asset


def get_user_data_path() -> Path:
    """
    Ritorna il path per dati utente persistenti.

    I dati utente NON devono essere nella cartella dell'app (potrebbe essere
    read-only o richiedere privilegi admin). Usa directory standard OS.

    Posizioni per OS:
    - Windows: %LOCALAPPDATA%/Intelleo
    - Linux: ~/.local/share/Intelleo
    - macOS: ~/Library/Application Support/Intelleo

    Returns:
        Path: Directory dati utente (creata automaticamente se non esiste).

    Examples:
        >>> get_user_data_path()
        WindowsPath('C:/Users/User/AppData/Local/Intelleo')
    """
    if sys.platform == "win32":
        # Windows: usa LOCALAPPDATA
        appdata = Path(os.environ.get("LOCALAPPDATA", "C:/Users/Public/AppData/Local"))
        user_path = appdata / "Intelleo"
    elif sys.platform == "darwin":
        # macOS: usa Application Support
        home = Path.home()
        user_path = home / "Library" / "Application Support" / "Intelleo"
    else:
        # Linux e altri: usa .local/share
        home = Path.home()
        user_path = home / ".local" / "share" / "Intelleo"

    # Crea directory se non esiste
    user_path.mkdir(parents=True, exist_ok=True)

    return user_path


def get_license_path() -> Path:
    """
    Path discovery per file di licenza.

    Cerca la directory contenente i file di licenza (config.dat, pyarmor.rkey)
    in ordine di priorità:

    1. %LOCALAPPDATA%/Intelleo/Licenza (User data - preferito, scrivibile)
    2. {AppDir}/Licenza (Install dir - legacy, per retrocompatibilità)
    3. {AppDir}/ (Root fallback - per installazioni molto vecchie)

    Returns:
        Path: Directory licenza. Ritorna la prima che esiste e contiene
              config.dat, oppure la prima (user data) per creazione.

    Note:
        Se nessuna posizione contiene file validi, ritorna comunque
        la posizione user data per permettere la creazione dei file.

    Examples:
        >>> get_license_path()
        WindowsPath('C:/Users/User/AppData/Local/Intelleo/Licenza')
    """
    candidates = [
        get_user_data_path() / "Licenza",
        get_base_path() / "Licenza",
        get_base_path(),
    ]

    # Cerca la prima posizione che contiene config.dat
    for path in candidates:
        if path.exists() and (path / "config.dat").exists():
            logger.debug(f"License found at: {path}")
            return path

    # Se nessuna esiste con config.dat, ritorna la prima (user data) per creazione
    # Crea la directory se non esiste
    default_path = candidates[0]
    default_path.mkdir(parents=True, exist_ok=True)

    logger.debug(f"License path defaulting to: {default_path}")
    return default_path


def get_database_path() -> Path:
    """
    Ritorna il path predefinito per il file database.

    Il database è salvato nella directory dati utente per:
    - Persistenza tra aggiornamenti app
    - Scrivibilità garantita (no admin required)
    - Backup automatici nella stessa posizione

    Returns:
        Path: Path completo al file database.

    Examples:
        >>> get_database_path()
        WindowsPath('C:/Users/User/AppData/Local/Intelleo/database_documenti.db')
    """
    return get_user_data_path() / "database_documenti.db"


def get_logs_path() -> Path:
    """
    Ritorna il path per i file di log.

    Returns:
        Path: Directory logs (creata automaticamente se non esiste).

    Examples:
        >>> get_logs_path()
        WindowsPath('C:/Users/User/AppData/Local/Intelleo/logs')
    """
    logs_path = get_user_data_path() / "logs"
    logs_path.mkdir(parents=True, exist_ok=True)
    return logs_path


# =============================================================================
# Self-Diagnostics Test Block
# =============================================================================
if __name__ == "__main__":
    # Fix Windows console encoding for emoji support
    if sys.platform == "win32":
        import io

        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    # Test Guide HTML
    guide_html = get_asset_path("guide_frontend/dist/index.html")
    guide_status = "✅ EXISTS" if guide_html.exists() else "❌ NOT FOUND"

    # Test Icon
    icon_path = get_asset_path("desktop_app/icons/icon.ico")
    icon_status = "✅ EXISTS" if icon_path.exists() else "❌ NOT FOUND"

    # Test License Files
    lic_path = get_license_path()
    lic_files = ["config.dat", "pyarmor.rkey", "manifest.json"]
    for f in lic_files:
        full_path = lic_path / f
        status = "✅" if full_path.exists() else "❌"
