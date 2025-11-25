import os
import sys

def get_app_install_dir():
    """
    Restituisce la directory di installazione dell'applicazione,
    gestendo sia l'esecuzione da sorgente che da eseguibile 'frozen'.
    """
    if getattr(sys, 'frozen', False):
        # L'applicazione è 'frozen' (es. PyInstaller)
        return os.path.dirname(sys.executable)
    else:
        # L'applicazione è in esecuzione da sorgente
        return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

def get_user_data_dir():
    """
    Restituisce il percorso della cartella dati dell'utente per l'applicazione,
    creandola se non esiste.

    Su Windows: %LOCALAPPDATA%\\Intelleo
    Su Linux: ~/.local/share/Intelleo
    Su macOS: ~/Library/Application Support/Intelleo
    """
    if os.name == 'nt':  # Windows
        path = os.path.join(os.getenv('LOCALAPPDATA'), 'Intelleo')
    elif os.name == 'posix':
        # Linux (e potenzialmente macOS in alcuni casi)
        path = os.path.join(os.path.expanduser('~'), '.local', 'share', 'Intelleo')
        # Specifico per macOS
        if sys.platform == "darwin":
            path = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'Intelleo')
    else:
        # Fallback per altri sistemi operativi
        path = os.path.join(os.path.expanduser('~'), '.intelleo')

    os.makedirs(path, exist_ok=True)
    return path

def get_license_dir():
    """
    Restituisce il percorso della cartella 'Licenza' all'interno della
    cartella dati dell'utente.
    """
    path = os.path.join(get_user_data_dir(), "Licenza")
    os.makedirs(path, exist_ok=True)
    return path
