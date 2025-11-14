from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QFileDialog, QFormLayout, QLineEdit, QMessageBox
import requests

class ImportView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.upload_button = QPushButton("Carica PDF")
        self.upload_button.clicked.connect(self.upload_pdf)
        self.layout.addWidget(self.upload_button)

        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        self.layout.addWidget(self.results_display)

        self.form_layout = QFormLayout()
        self.nome_input = QLineEdit()
        self.corso_input = QLineEdit()
        self.data_rilascio_input = QLineEdit()
        self.data_scadenza_input = QLineEdit()

        self.form_layout.addRow("Nome:", self.nome_input)
        self.form_layout.addRow("Corso:", self.corso_input)
        self.form_layout.addRow("Data Rilascio:", self.data_rilascio_input)
        self.form_layout.addRow("Data Scadenza:", self.data_scadenza_input)
        self.layout.addLayout(self.form_layout)

        self.validate_button = QPushButton("Convalida Dati")
        self.validate_button.clicked.connect(self.validate_data)
        self.layout.addWidget(self.validate_button)

    def validate_data(self):
        certificato = {
            "nome": self.nome_input.text(),
            "corso": self.corso_input.text(),
            "data_rilascio": self.data_rilascio_input.text(),
            "data_scadenza": self.data_scadenza_input.text()
        }
        try:
            response = requests.post("http://localhost:8000/certificati/", json=certificato)
            if response.status_code == 200:
                QMessageBox.information(self, "Successo", "Dati convalidati e salvati con successo.")
            else:
                QMessageBox.critical(self, "Errore", f"Errore durante la convalida: {response.text}")
        except requests.exceptions.ConnectionError as e:
            QMessageBox.critical(self, "Errore di connessione", f"Impossibile connettersi al server: {e}")

    def upload_pdf(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Seleziona PDF", "", "PDF Files (*.pdf)")
        if file_name:
            with open(file_name, 'rb') as f:
                files = {'file': (file_name, f, 'application/pdf')}
                try:
                    response = requests.post("http://localhost:8000/upload-pdf/", files=files)
                    if response.status_code == 200:
                        data = response.json()
                        self.results_display.setText(f"Testo estratto:\n{data['text']}")
                        entities = data.get('entities', {})
                        self.nome_input.setText(entities.get('nome', ''))
                        self.corso_input.setText(entities.get('corso', ''))
                        self.data_rilascio_input.setText(entities.get('data_rilascio', ''))
                        self.data_scadenza_input.setText(entities.get('data_scadenza', ''))
                    else:
                        self.results_display.setText(f"Errore: {response.text}")
                except requests.exceptions.ConnectionError as e:
                    self.results_display.setText(f"Errore di connessione: {e}")
