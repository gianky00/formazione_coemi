from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QDateEdit, QCheckBox, QDialogButtonBox, QFormLayout, QLabel, QComboBox
from PyQt6.QtCore import QDate, Qt

class EditCertificatoDialog(QDialog):
    def __init__(self, data, categories, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Modifica Certificato")
        self.layout = QVBoxLayout(self)

        self.form_layout = QFormLayout()
        self.nome_edit = QLineEdit(data['nome'])
        self.corso_edit = QLineEdit(data['corso'])
        self.categoria_edit = QComboBox()
        self.categoria_edit.addItems(categories)
        self.categoria_edit.setCurrentText(data['categoria'])

        self.data_rilascio_edit = QDateEdit()
        self.data_rilascio_edit.setDisplayFormat("dd/MM/yyyy")
        rilascio_date = QDate.fromString(data['data_rilascio'], "dd/MM/yyyy")
        self.data_rilascio_edit.setDate(rilascio_date if rilascio_date.isValid() else QDate.currentDate())

        self.scadenza_checkbox = QCheckBox("Ha una data di scadenza")
        self.data_scadenza_edit = QDateEdit()
        self.data_scadenza_edit.setDisplayFormat("dd/MM/yyyy")
        self.data_scadenza_edit.setEnabled(False)

        scadenza_date_str = str(data.get('data_scadenza', ''))
        if scadenza_date_str and scadenza_date_str.lower() != 'none':
            scadenza_date = QDate.fromString(scadenza_date_str, "dd/MM/yyyy")
            if scadenza_date.isValid():
                self.data_scadenza_edit.setDate(scadenza_date)
                self.data_scadenza_edit.setEnabled(True)
                self.scadenza_checkbox.setChecked(True)

        self.scadenza_checkbox.toggled.connect(self.data_scadenza_edit.setEnabled)

        self.form_layout.addRow(QLabel("Nome e Cognome:"), self.nome_edit)
        self.form_layout.addRow(QLabel("Corso:"), self.corso_edit)
        self.form_layout.addRow(QLabel("Categoria:"), self.categoria_edit)
        self.form_layout.addRow(QLabel("Data Rilascio:"), self.data_rilascio_edit)
        self.form_layout.addRow(self.scadenza_checkbox, self.data_scadenza_edit)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(self.button_box)
        self.adjustSize()

    def get_data(self):
        data_scadenza = self.data_scadenza_edit.date().toString("dd/MM/yyyy") if self.scadenza_checkbox.isChecked() else None
        return {
            "nome": self.nome_edit.text(),
            "corso": self.corso_edit.text(),
            "categoria": self.categoria_edit.currentText(),
            "data_rilascio": self.data_rilascio_edit.date().toString("dd/MM/yyyy"),
            "data_scadenza": data_scadenza
        }
