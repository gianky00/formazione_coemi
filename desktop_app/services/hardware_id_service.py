import os
import uuid
import logging

logger = logging.getLogger(__name__)

# Cache the machine ID to avoid repeated expensive WMI calls and log spam
_cached_machine_id = None

def _get_windows_disk_serial():
    """
    Retrieves the serial number of the primary physical disk on Windows.
    This is a common and reliable binding target for licensing.
    """
    try:
        import pythoncom

        # Initialize COM for the current thread
        pythoncom.CoInitialize()

        try:
            # Encapsulate WMI logic in a nested function to ensure
            # all WMI objects are garbage collected BEFORE CoUninitialize is called.
            def _query_wmi():
                import wmi
                c = wmi.WMI()
                # Find the primary physical disk (usually DeviceID \\.\PHYSICALDRIVE0)
                for disk in c.Win32_DiskDrive():
                    if "PHYSICALDRIVE0" in disk.DeviceID:
                        serial = disk.SerialNumber.strip().rstrip('.')
                        logger.debug(f"Found disk serial for PHYSICALDRIVE0: {serial}")
                        return serial

                # Fallback if specific device not found, return the first one found
                if len(c.Win32_DiskDrive()) > 0:
                    first_disk = c.Win32_DiskDrive()[0]
                    serial = first_disk.SerialNumber.strip().rstrip('.')
                    logger.warning("PHYSICALDRIVE0 not found, using first disk serial as fallback.")
                    return serial
                return None

            return _query_wmi()

        finally:
            # Always uninitialize, but only after inner function returns (and its objects are dead)
            pythoncom.CoUninitialize()

    except ImportError:
        logger.error("WMI module not found. Cannot get disk serial on Windows.")
        return None
    except Exception as e:
        logger.error(f"Failed to get disk serial number via WMI: {e}")
        return None

def _get_mac_address():
    """
    Returns the MAC address as a string. Serves as a universal fallback.
    """
    try:
        mac = uuid.getnode()
        # Format MAC to a standard hex string
        return ':'.join(('%012X' % mac)[i:i+2] for i in range(0, 12, 2))
    except Exception as e:
        logger.error(f"Failed to get MAC address: {e}")
        return "00:00:00:00:00:00" # Ultimate fallback

def get_machine_id():
    """
    Gets the most reliable and consistent hardware ID for the current OS.
    - On Windows, it prioritizes the disk serial number.
    - Falls back to the MAC address if the disk serial cannot be retrieved.
    - Results are cached to avoid repeated expensive WMI calls.
    """
    global _cached_machine_id
    
    # Return cached value if available
    if _cached_machine_id is not None:
        return _cached_machine_id
    
    machine_id = None
    if os.name == 'nt':
        logger.debug("Windows OS detected. Attempting to get disk serial number.")
        machine_id = _get_windows_disk_serial()

    if not machine_id:
        logger.warning("Disk serial not found or OS is not Windows. Falling back to MAC address.")
        machine_id = _get_mac_address()

    logger.debug(f"Final determined Machine ID: {machine_id}")
    _cached_machine_id = machine_id
    return machine_id
