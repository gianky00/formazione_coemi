
import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import requests

@pytest.fixture
def mock_api_data():
    # The API returns 'nome' pre-formatted as "COGNOME NOME"
    return [
        {'id': 1, 'nome': 'ROSSI MARIO', 'categoria': 'Formazione', 'stato_certificato': 'attivo'},
        {'id': 2, 'nome': 'BIANCHI LUIGI', 'categoria': 'Sicurezza', 'stato_certificato': 'scaduto'},
        {'id': 3, 'nome': 'ROSSI MARIO', 'categoria': 'Sicurezza', 'stato_certificato': 'attivo'},
    ]

@pytest.fixture
def view_model():
    from desktop_app.view_models.database_view_model import DatabaseViewModel
    return DatabaseViewModel()

@patch('requests.get')
def test_load_data_success(mock_get, mock_api_data, view_model):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_api_data
    mock_get.return_value = mock_response

    vm = view_model
    vm.data_changed = MagicMock()

    vm.load_data()

    # Verify emit called
    vm.data_changed.emit.assert_called_once()
    assert not vm.filtered_data.empty
    assert vm.filtered_data.shape[0] == 3
    # The view model renames 'nome' to 'Dipendente'
    assert list(vm.filtered_data['Dipendente']) == ['ROSSI MARIO', 'BIANCHI LUIGI', 'ROSSI MARIO']

@patch('requests.get')
def test_filter_data(mock_get, mock_api_data, view_model):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_api_data
    mock_get.return_value = mock_response

    vm = view_model
    vm.load_data()

    # Filter by employee
    vm.filter_data('ROSSI MARIO', 'Tutti', 'Tutti')
    assert vm.filtered_data.shape[0] == 2
    assert all(vm.filtered_data['Dipendente'] == 'ROSSI MARIO')

    # Filter by category
    vm.filter_data('Tutti', 'Sicurezza', 'Tutti')
    assert vm.filtered_data.shape[0] == 2
    assert all(vm.filtered_data['categoria'] == 'Sicurezza')

    # Filter by status
    vm.filter_data('Tutti', 'Tutti', 'scaduto')
    assert vm.filtered_data.shape[0] == 1
    assert all(vm.filtered_data['stato_certificato'] == 'scaduto')

    # Combined filter
    vm.filter_data('ROSSI MARIO', 'Sicurezza', 'Tutti')
    assert vm.filtered_data.shape[0] == 1
    assert vm.filtered_data.iloc[0]['Dipendente'] == 'ROSSI MARIO'
    assert vm.filtered_data.iloc[0]['categoria'] == 'Sicurezza'

@patch('requests.get')
def test_get_filter_options(mock_get, mock_api_data, view_model):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_api_data
    mock_get.return_value = mock_response

    vm = view_model
    vm.load_data()

    options = vm.get_filter_options()

    assert options['dipendenti'] == ['BIANCHI LUIGI', 'ROSSI MARIO']
    assert options['categorie'] == ['Formazione', 'Sicurezza']
    assert options['stati'] == ['attivo', 'scaduto']

@patch('requests.get')
def test_load_data_failure(mock_get, view_model):
    mock_get.side_effect = requests.exceptions.RequestException("Connection error")

    vm = view_model
    vm.error_occurred = MagicMock()
    vm.data_changed = MagicMock()

    vm.load_data()

    vm.error_occurred.emit.assert_called_once_with("Impossibile caricare i dati: Connection error")
    vm.data_changed.emit.assert_called_once()
    assert vm.filtered_data.empty

@patch('requests.delete')
@patch('requests.get')
def test_delete_certificates_success(mock_get, mock_delete, view_model):
    # Setup load_data mock
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = [] # Empty after delete for simplicity

    # Setup delete mock
    mock_delete.return_value.status_code = 204

    vm = view_model
    vm.operation_completed = MagicMock()

    vm.delete_certificates([1, 2])

    assert mock_delete.call_count == 2
    vm.operation_completed.emit.assert_called_once_with("2 certificati cancellati con successo.")
    # Verify it reloads data
    assert mock_get.called

@patch('requests.delete')
def test_delete_certificates_partial_failure(mock_delete, view_model):
    # Success for ID 1, Failure for ID 2
    def side_effect(url, **kwargs):
        if url.endswith("/1"):
            resp = Mock()
            resp.status_code = 204
            return resp
        else:
            raise requests.exceptions.RequestException("Delete failed")

    mock_delete.side_effect = side_effect

    vm = view_model
    vm.load_data = Mock() # Mock load_data to avoid extra calls
    vm.operation_completed = MagicMock()
    vm.error_occurred = MagicMock()

    vm.delete_certificates([1, 2])

    vm.operation_completed.emit.assert_called_once_with("1 certificati cancellati con successo.")
    vm.error_occurred.emit.assert_called_once()
    assert "ID 2: Delete failed" in vm.error_occurred.emit.call_args[0][0]

@patch('requests.put')
@patch('requests.get')
def test_update_certificate_success(mock_get, mock_put, view_model):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = []

    mock_put.return_value.status_code = 200

    vm = view_model
    vm.operation_completed = MagicMock()

    result = vm.update_certificate(1, {"some": "data"})

    assert result is True
    vm.operation_completed.emit.assert_called_once_with("Certificato aggiornato con successo.")
    assert mock_get.called

@patch('requests.put')
def test_update_certificate_failure(mock_put, view_model):
    mock_put.side_effect = requests.exceptions.RequestException("Update failed")

    vm = view_model
    vm.error_occurred = MagicMock()

    result = vm.update_certificate(1, {"some": "data"})

    assert result is False
    vm.error_occurred.emit.assert_called_once_with("Impossibile modificare il certificato: Update failed")

def test_filter_data_empty(view_model):
    vm = view_model
    # _df_original is empty by default
    vm.filter_data("A", "B", "C")
    assert vm.filtered_data.empty

def test_get_filter_options_empty(view_model):
    vm = view_model
    options = vm.get_filter_options()
    assert options == {"dipendenti": [], "categorie": [], "stati": []}
