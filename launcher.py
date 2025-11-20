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

def log_debug(msg):
    if getattr(sys, 'frozen', False):
        try:
            exe_dir = os.path.dirname(sys.executable)
            log_path = os.path.join(exe_dir, "debug_hwid.log")
            with open(log_path, "a") as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {msg}\n")
        except:
            pass

def get_hw_id_safe():
    log_debug("Attempting to get HWID...")
    try:
        from pyarmor_runtime import get_machine_id
        log_debug("Imported pyarmor_runtime successfully.")
        val = get_machine_id()
        return val.decode('utf-8') if isinstance(val, bytes) else str(val)
    except ImportError as e:
        log_debug(f"ImportError for standard pyarmor_runtime: {e}")
        # Fallback for pyarmor_runtime_xxxxxx in plain text scripts
        import importlib
        import pkgutil

        # 1. Try pkgutil first
        log_debug("Scanning pkgutil...")
        for finder, name, ispkg in pkgutil.iter_modules():
            if name.startswith("pyarmor_runtime_"):
                log_debug(f"Found candidate via pkgutil: {name}")
                try:
                    mod = importlib.import_module(name)
                    if hasattr(mod, 'get_machine_id'):
                        val = mod.get_machine_id()
                        return val.decode('utf-8') if isinstance(val, bytes) else str(val)
                except Exception as e:
                    log_debug(f"Failed to import {name}: {e}")
                    pass

        # 2. Explicit scan of sys._MEIPASS (for PyInstaller)
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            log_debug(f"Scanning _MEIPASS: {sys._MEIPASS}")
            try:
                for name in os.listdir(sys._MEIPASS):
                    if name.startswith("pyarmor_runtime_") and os.path.isdir(os.path.join(sys._MEIPASS, name)):
                         log_debug(f"Found candidate in _MEIPASS: {name}")
                         try:
                             files = os.listdir(os.path.join(sys._MEIPASS, name))
                             log_debug(f"Files in {name}: {files}")
                         except:
                             pass

                         try:
                             mod = importlib.import_module(name)
                             log_debug(f"Imported {name}. Attributes: {dir(mod)}")
                             if hasattr(mod, 'get_machine_id'):
                                 val = mod.get_machine_id()
                                 return val.decode('utf-8') if isinstance(val, bytes) else str(val)

                             # Fallback for direct extension import
                             try:
                                 submod = importlib.import_module(f"{name}.pyarmor_runtime")
                                 log_debug(f"Imported submodule {name}.pyarmor_runtime")
                                 if hasattr(submod, 'get_machine_id'):
                                      val = submod.get_machine_id()
                                      return val.decode('utf-8') if isinstance(val, bytes) else str(val)
                             except Exception as e:
                                 log_debug(f"Submodule import failed: {e}")

                         except Exception as e:
                             log_debug(f"Failed to import {name}: {e}")
                             pass
            except Exception as e:
                log_debug(f"Error scanning _MEIPASS: {e}")
                pass

        log_debug("Failed to find runtime.")
        return "N/A"
    except Exception as e:
        log_debug(f"Unexpected error in get_hw_id_safe: {e}")
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
