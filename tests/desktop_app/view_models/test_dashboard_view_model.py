
import pytest
from unittest.mock import Mock, patch
import pandas as pd
import requests
from desktop_app.view_models.dashboard_view_model import DashboardViewModel

@pytest.fixture
def mock_api_data():
    # The API returns 'nome' pre-formatted as "COGNOME NOME"
    return [
        {'id': 1, 'nome': 'ROSSI MARIO', 'categoria': 'Formazione', 'stato_certificato': 'attivo'},
        {'id': 2, 'nome': 'BIANCHI LUIGI', 'categoria': 'Sicurezza', 'stato_certificato': 'scaduto'},
        {'id': 3, 'nome': 'ROSSI MARIO', 'categoria': 'Sicurezza', 'stato_certificato': 'attivo'},
    ]

@patch('requests.get')
def test_load_data_success(mock_get, mock_api_data):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_api_data
    mock_get.return_value = mock_response

    vm = DashboardViewModel()

    # Connect to the signal to check if it's emitted
    data_changed_mock = Mock()
    vm.data_changed.connect(data_changed_mock)

    vm.load_data()

    data_changed_mock.assert_called_once()
    assert not vm.filtered_data.empty
    assert vm.filtered_data.shape[0] == 3
    # The view model renames 'nome' to 'Dipendente'
    assert list(vm.filtered_data['Dipendente']) == ['ROSSI MARIO', 'BIANCHI LUIGI', 'ROSSI MARIO']

@patch('requests.get')
def test_filter_data(mock_get, mock_api_data):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_api_data
    mock_get.return_value = mock_response

    vm = DashboardViewModel()
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
def test_get_filter_options(mock_get, mock_api_data):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_api_data
    mock_get.return_value = mock_response

    vm = DashboardViewModel()
    vm.load_data()

    options = vm.get_filter_options()

    assert options['dipendenti'] == ['BIANCHI LUIGI', 'ROSSI MARIO']
    assert options['categorie'] == ['Formazione', 'Sicurezza']
    assert options['stati'] == ['attivo', 'scaduto']

@patch('requests.get')
def test_load_data_failure(mock_get):
    mock_get.side_effect = requests.exceptions.RequestException("Connection error")

    vm = DashboardViewModel()

    error_mock = Mock()
    vm.error_occurred.connect(error_mock)

    data_changed_mock = Mock()
    vm.data_changed.connect(data_changed_mock)

    vm.load_data()

    error_mock.assert_called_once_with("Impossibile caricare i dati: Connection error")
    data_changed_mock.assert_called_once()
    assert vm.filtered_data.empty
