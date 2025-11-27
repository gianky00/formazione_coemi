import sys
import pandas as pd
import pytest
from unittest.mock import MagicMock

# Mock modules to avoid GUI dependency issues if needed,
# though QAbstractTableModel usually works in headless if QApp exists (which pytest-qt provides or we mock)
# For this unit test of logic, we might need to mock if imports fail.

from desktop_app.views.database_view import CertificatoTableModel
from PyQt6.QtCore import Qt

def test_database_table_model_uppercase_and_no_escape():
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
    display_value = model.data(index, Qt.ItemDataRole.DisplayRole)

    # Verify: UPPERCASE applied?
    assert display_value == "SCATA' SALVATORE"
    assert "&#x27;" not in display_value

    # Test row 1, col 0 (Check simple case)
    index = model.index(1, 0)
    display_value = model.data(index, Qt.ItemDataRole.DisplayRole)
    assert display_value == "TEST VALUE"
