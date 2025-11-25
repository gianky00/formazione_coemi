import os
import uuid
import sys

def _get_windows_disk_serial():
    """
    Retrieves the serial number of the primary physical disk on Windows.
    This is a common and reliable binding target for licensing.
    """
    try:
        import wmi
        c = wmi.WMI()
        # Find the primary physical disk (usually DeviceID \\.\PHYSICALDRIVE0)
        for disk in c.Win32_DiskDrive():
            if "PHYSICALDRIVE0" in disk.DeviceID:
                return disk.SerialNumber.strip().rstrip('.')

        # Fallback if specific device not found, return the first one found
        return c.Win32_DiskDrive()[0].SerialNumber.strip().rstrip('.')
    except ImportError:
        print("Error: The 'WMI' module is not installed. Please run 'pip install wmi'.", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error: Failed to get disk serial number via WMI: {e}", file=sys.stderr)
        return None

def _get_mac_address():
    """
    Returns the MAC address as a string. Serves as a universal fallback.
    """
    try:
        mac = uuid.getnode()
        # Format MAC to a standard hex string
        return ':'.join(('%012X' % mac)[i:i+2] for i in range(0, 12, 2))
    except Exception:
        return None

def get_machine_id():
    """
    Gets the most reliable and consistent hardware ID for the current OS.
    """
    machine_id = None
    if os.name == 'nt':
        machine_id = _get_windows_disk_serial()

    if not machine_id:
        machine_id = _get_mac_address()

    return machine_id

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
