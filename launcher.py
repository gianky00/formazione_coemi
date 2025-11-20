import sys
import os
import threading
import time

# Fix for PyInstaller OneFile: Set CWD to temporary dir
if getattr(sys, 'frozen', False):
    # Store the directory where the executable is located
    EXE_DIR = os.path.dirname(sys.executable)

    # Set DATABASE_URL to use the executable directory
    db_path = os.path.join(EXE_DIR, "scadenzario.db")
    if os.name == 'nt':
        db_path = db_path.replace('\\', '\\\\')

    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

    # Change working directory to _MEIPASS so assets can be found via relative paths
    os.chdir(sys._MEIPASS)

# Add current directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def get_hw_id_safe():
    try:
        from pyarmor_runtime import get_machine_id
        val = get_machine_id()
        return val.decode('utf-8') if isinstance(val, bytes) else str(val)
    except ImportError:
        # Fallback for pyarmor_runtime_xxxxxx in plain text scripts
        import importlib
        import pkgutil
        for finder, name, ispkg in pkgutil.iter_modules():
            if name.startswith("pyarmor_runtime_"):
                try:
                    mod = importlib.import_module(name)
                    if hasattr(mod, 'get_machine_id'):
                        val = mod.get_machine_id()
                        return val.decode('utf-8') if isinstance(val, bytes) else str(val)
                except:
                    pass
        return "N/A"
    except Exception:
        return "Error"

def run_backend():
    try:
        import uvicorn
        from app.main import app
        # Run uvicorn programmatically
        # 127.0.0.1 is safer than 0.0.0.0 for local desktop app
        uvicorn.run(app, host="127.0.0.1", port=8000, log_config=None)
    except Exception as e:
        # In a GUI app, stdout might be lost, but we print anyway
        print(f"Backend error: {e}")

def main():
    # Start backend thread
    t = threading.Thread(target=run_backend, daemon=True)
    t.start()

    # Start frontend
    try:
        from desktop_app.main import main as frontend_main
        frontend_main()
    except ImportError as e:
        # If desktop_app is obfuscated and license fails, import might fail?
        # Usually it raises RuntimeError during import
        import traceback
        traceback.print_exc()
        try:
            from tkinter import messagebox, Tk
            root = Tk()
            root.withdraw()

            hw_id = get_hw_id_safe()

            messagebox.showerror("Fatal Error", f"Failed to load application:\n{e}\n\nHWID: {hw_id}")
        except:
            print(f"Fatal Error: {e}")
    except Exception as e:
        # Catch generic errors
        import traceback
        traceback.print_exc()
        print(f"Fatal Error: {e}")

if __name__ == "__main__":
    main()
