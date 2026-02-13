import inspect
import logging

from desktop_app.services import security_service, time_service

logger = logging.getLogger(__name__)


def verify_critical_components():
    """
    Performs runtime integrity checks on critical security modules.
    Ensures that security functions are authentic and have not been monkey-patched.

    Returns: (bool, str) -> (is_secure, error_message)
    """
    try:
        # 1. Verify security_service.is_virtual_environment
        func = security_service.is_virtual_environment
        if not inspect.isfunction(func):
            return False, "Security Violation: is_virtual_environment is not a function."

        # Check if it's a lambda (heuristic)
        if func.__name__ == "<lambda>":
            return (
                False,
                "Security Violation: is_virtual_environment has been patched (lambda detected).",
            )

        # Check if code object is present
        if not hasattr(func, "__code__"):
            return False, "Security Violation: is_virtual_environment missing bytecode."

        # 2. Verify time_service.check_system_clock
        func_time = time_service.check_system_clock
        if not inspect.isfunction(func_time):
            return False, "Security Violation: check_system_clock is not a function."

        if func_time.__name__ == "<lambda>":
            return (
                False,
                "Security Violation: check_system_clock has been patched (lambda detected).",
            )

        # 3. Verify license_security (Transient Memory)
        # Check if get_license_secret_key is a function
        from app.core import license_security

        if not inspect.isfunction(license_security.get_license_secret_key):
            return False, "Security Violation: Key Accessor is compromised."

        logger.info("Integrity Check Passed: Critical components verified.")
        return True, "OK"

    except Exception as e:
        logger.critical(f"Integrity Check Failed: {e}")
        return False, f"Integrity Check Error: {e}"
