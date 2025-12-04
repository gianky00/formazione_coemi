import sys
import pandas as pd
import pytest
import importlib
from unittest.mock import MagicMock

# Ensure we are using REAL PyQt6 for this test
# We clean sys.modules of any desktop_app modules that might have been mocked
@pytest.fixture(autouse=True)
def clean_imports():
    to_remove = [k for k in sys.modules if k.startswith('desktop_app')]
    for k in to_remove:
        del sys.modules[k]
    yield

def test_database_table_model_uppercase_and_no_escape():
    # Import inside test to ensure fresh import after cleaning sys.modules
    from desktop_app.views.database_view import CertificatoTableModel
    from PyQt6.QtCore import Qt, QCoreApplication

    # Ensure QCoreApplication exists (needed for some QAbstractItemModel mechanics)
    app = QCoreApplication.instance()
    if not app:
        app = QCoreApplication([])

    # Setup data with lowercase and special chars
    # The 'html.escape' would turn "'" into "&#x27;"
    # The requirement is UPPERCASE and NO ESCAPE.

    data = pd.DataFrame({
        'col1': ["scata' salvatore", "test value"],
        'col2': ["another", "value"]
    })
    model = CertificatoTableModel(data)

    # Test row 0, col 0
    index = model.index(0, 0)

    # Debug: Check if index is valid
    assert index.isValid(), "Index should be valid"

    display_value = model.data(index, Qt.ItemDataRole.DisplayRole)

    # Verify: UPPERCASE applied?
    assert display_value == "SCATA' SALVATORE"
    assert "&#x27;" not in display_value

    # Test row 1, col 0 (Check simple case)
    index = model.index(1, 0)
    display_value = model.data(index, Qt.ItemDataRole.DisplayRole)
    assert display_value == "TEST VALUE"
