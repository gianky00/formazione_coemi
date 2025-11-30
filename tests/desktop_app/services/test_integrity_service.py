import pytest
from unittest.mock import patch, MagicMock
from desktop_app.services.integrity_service import verify_critical_components
from desktop_app.services import security_service

class TestIntegrityService:
    def test_verify_critical_components_valid(self):
        is_ok, msg = verify_critical_components()
        assert is_ok is True
        assert msg == "OK"

    def test_verify_detects_lambda_patch(self):
        # Save original
        original = security_service.is_virtual_environment

        # Monkey patch with lambda
        security_service.is_virtual_environment = lambda: (False, "Fake")

        try:
            is_ok, msg = verify_critical_components()
            assert is_ok is False
            assert "lambda detected" in msg
        finally:
            # Restore
            security_service.is_virtual_environment = original

    def test_verify_detects_non_function(self):
        original = security_service.is_virtual_environment

        # Monkey patch with object
        security_service.is_virtual_environment = "Not a function"

        try:
            is_ok, msg = verify_critical_components()
            assert is_ok is False
            assert "not a function" in msg
        finally:
            security_service.is_virtual_environment = original
