import logging
import os
import sys

logger = logging.getLogger(__name__)

# Constants for detections
VM_PROCESSES = [
    "vmtoolsd.exe",
    "vmware-tray.exe",
    "vm3dservice.exe",  # VMware
    "vboxservice.exe",
    "vboxtray.exe",  # VirtualBox
    "qemu-ga.exe",  # QEMU
    "prl_cc.exe",
    "prl_tools.exe",  # Parallels
    "vmsrvc.exe",
    "vmusrvc.exe",  # Virtual PC
    "sbiesvc.exe",  # Sandboxie
]

ANALYSIS_TOOLS = [
    "wireshark.exe",
    "fiddler.exe",
    "charles.exe",  # Network Analysis
    "processhacker.exe",
    "procmon.exe",
    "procmon64.exe",  # Process Monitoring
    "cheatengine-x86_64.exe",
    "cheatengine-i386.exe",  # Memory Manipulation
    "x64dbg.exe",
    "x32dbg.exe",
    "ollydbg.exe",
    "ida64.exe",
    "ida.exe",  # Debuggers/Disassemblers
    "httpdebuggerui.exe",
    "dnspy.exe",
    "pestudio.exe",  # .NET/Traffic Analysis
]


def _get_running_processes_wmi():
    """
    Retrieves a list of running process names using WMI (Windows only).
    Returns an empty list on failure or non-Windows OS.
    """
    if os.name != "nt":
        return []

    try:
        import wmi

        c = wmi.WMI()
        # Retrieving just names is faster
        return [p.Name.lower() for p in c.Win32_Process()]
    except Exception as e:
        logger.error(f"Failed to query WMI for processes: {e}")
        return []


def is_virtual_environment():
    """
    Checks if the application is running inside a known Virtual Machine.
    Returns: (bool, str) -> (is_vm, reason_message)
    """
    # 1. Process Check
    running_processes = _get_running_processes_wmi()
    for proc in VM_PROCESSES:
        if proc.lower() in running_processes:
            logger.warning(f"VM Detection: Found process {proc}")
            return True, f"Esecuzione in virtual machine non consentita (Rilevato: {proc})."

    # 2. Disk/BIOS/Service Checks (if needed, but avoiding strict hardware IDs as per constraints)
    # The constraint was "NON USARE Hardware Fingerprinting composito... controlli su CPU, Motherboard...".
    # Checking for specific VM files/drivers is explicitly requested ("driver, file o processi").

    # Common VM Driver Files
    vm_files = [
        r"C:\Windows\System32\drivers\vboxguest.sys",
        r"C:\Windows\System32\drivers\vboxmouse.sys",
        r"C:\Windows\System32\drivers\vm3dmp.sys",
        r"C:\Windows\System32\drivers\vmtools.sys",
        r"C:\Windows\System32\drivers\vmmouse.sys",
        r"C:\Windows\System32\drivers\vmusbmouse.sys",
    ]

    if os.name == "nt":
        for fpath in vm_files:
            if os.path.exists(fpath):
                logger.warning(f"VM Detection: Found driver {fpath}")
                return True, "Esecuzione in virtual machine non consentita (Driver rilevati)."

    return False, ""


def is_analysis_tool_running():
    """
    Checks if known analysis/hacking tools are running.
    Returns: (bool, str) -> (is_tool_active, reason_message)
    """
    running_processes = _get_running_processes_wmi()
    for tool in ANALYSIS_TOOLS:
        if tool.lower() in running_processes:
            logger.warning(f"Security: Analysis tool detected: {tool}")
            return (
                True,
                f"Rilevato strumento di analisi non consentito: {tool}. Chiudere il programma e riprovare.",
            )

    return False, ""


def is_debugger_active():
    """
    Checks if a standard Python debugger is attached.
    Returns: (bool, str) -> (is_debug, reason_message)
    """
    if sys.gettrace() is not None:
        logger.warning("Security: Python debugger detected (sys.gettrace).")
        return True, "Debugger rilevato. L'applicazione non può essere eseguita in modalità debug."

    return False, ""
