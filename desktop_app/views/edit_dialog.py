
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QDateEdit, QCheckBox, QDialogButtonBox, QFormLayout, QLabel, QComboBox, QListView
from PyQt6.QtCore import QDate, Qt

class EditCertificatoDialog(QDialog):
    def __init__(self, data, categories, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Modifica Certificato")

        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 15px;
            }
            QLabel {
                font-size: 14px;
            }
            QLineEdit, QComboBox, QDateEdit {
                padding: 8px;
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 5px;
                font-size: 14px;
            }
        """)

        self.layout = QVBoxLayout(self)

        self.form_layout = QFormLayout()
        self.nome_edit = QLineEdit(data['nome'])
        self.corso_edit = QLineEdit(data['corso'])
        self.categoria_edit = QComboBox()

        unique_categories = sorted(list(set(categories)))
        self.categoria_edit.addItems(unique_categories)

        self.categoria_edit.setCurrentText(data['categoria'])
        self.categoria_edit.setEditable(False)
        self.categoria_edit.setView(QListView())
        self.categoria_edit.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)


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

        # Style buttons
        ok_button = self.button_box.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setStyleSheet("background-color: #0052CC; color: white;")
        cancel_button = self.button_box.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_button.setStyleSheet("background-color: transparent; border: 1px solid #E0E0E0; color: #555;")

        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(self.button_box)

        self.setMinimumWidth(400)
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
