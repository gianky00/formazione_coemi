import sys
import os

# Adjust the path to import from the desktop_app module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from desktop_app.services.hardware_id_service import get_machine_id

if __name__ == "__main__":
    """
    This script provides a simple command-line interface for administrators
    to get the correct machine ID, using the exact same logic as the client app.
    """
    machine_id = get_machine_id()
    if machine_id:
        print(machine_id)
    else:
        # Print an error to stderr if the ID could not be determined
        print("Error: Could not determine machine ID.", file=sys.stderr)
        sys.exit(1)
