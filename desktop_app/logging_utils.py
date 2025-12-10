import sys
import traceback

def safe_print(*args, **kwargs):
    """
    Safely prints to stdout, preventing crashes if sys.stdout is None
    (common in frozen applications without console).
    """
    try:
        if sys.stdout is not None:
            print(*args, **kwargs)
    except Exception:
        pass

def safe_print_exc():
    """
    Safely prints the current exception traceback to stderr, preventing crashes
    if sys.stderr is None.
    """
    try:
        if sys.stderr is not None:
            traceback.print_exc()
    except Exception:
        pass
