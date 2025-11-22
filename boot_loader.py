import sys
import os
import traceback
import ctypes
import datetime

# --- BLACK BOX BOOT LOADER ---
# Questo script funge da wrapper di sicurezza per l'avvio dell'applicazione.
# Cattura qualsiasi errore critico (ImportError, DLL load failed, ecc.)
# e lo mostra all'utente tramite una MessageBox nativa di Windows,
# oltre a scriverlo su un file di log sul Desktop.

def show_error(title, message):
    """Mostra una MessageBox nativa Windows senza dipendenze PyQt."""
    if os.name == 'nt':
        try:
            # 0x10 = MB_ICONHAND (Error icon)
            ctypes.windll.user32.MessageBoxW(0, message, title, 0x10)
        except:
            pass # Se fallisce anche questo, non possiamo farci nulla.
    else:
        # Fallback per Linux/Mac (solo print)
        print(f"CRITICAL ERROR [{title}]: {message}", file=sys.stderr)

def log_crash(error_msg):
    """Scrive il log dell'errore su file."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_content = f"""
========================================
INTELLEO CRASH REPORT - {timestamp}
========================================
Error: {error_msg}

System Info:
Python: {sys.version}
Platform: {sys.platform}
Executable: {sys.executable}
CWD: {os.getcwd()}

Traceback:
{traceback.format_exc()}
========================================
"""
    # 1. Scrivi nella cartella dell'applicazione
    try:
        with open("CRASH_LOG.txt", "a", encoding="utf-8") as f:
            f.write(log_content)
    except: pass

    # 2. Scrivi sul Desktop dell'utente (per massima visibilità)
    if os.name == 'nt':
        try:
            desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
            if os.path.exists(desktop):
                with open(os.path.join(desktop, "INTELLEO_CRASH_LOG.txt"), "a", encoding="utf-8") as f:
                    f.write(log_content)
        except: pass

def main():
    try:
        # Tenta di importare e avviare il launcher principale
        import launcher
        launcher.main()

    except Exception as e:
        error_msg = str(e)

        # Log su file
        log_crash(error_msg)

        # Feedback UI all'utente
        user_msg = f"Si è verificato un errore critico all'avvio.\n\nErrore: {error_msg}\n\nUn report dettagliato è stato salvato sul tuo Desktop (INTELLEO_CRASH_LOG.txt)."
        show_error("Intelleo - Errore Fatale", user_msg)

        sys.exit(1)

if __name__ == "__main__":
    main()
