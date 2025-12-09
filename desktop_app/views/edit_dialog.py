
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QDateEdit, QCheckBox, 
                             QDialogButtonBox, QFormLayout, QLabel, QComboBox, QListView,
                             QHBoxLayout, QFrame)
from PyQt6.QtCore import QDate, Qt
from desktop_app.constants import DATE_FORMAT_DISPLAY


class EditCertificatoDialog(QDialog):
    def __init__(self, data, categories, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Modifica Certificato")
        self.setMinimumWidth(500)

        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
            }
            QLabel {
                font-size: 14px;
                color: #374151;
            }
            QLabel#section_title {
                font-size: 16px;
                font-weight: 600;
                color: #1F2937;
                padding: 10px 0;
            }
            QLineEdit, QComboBox, QDateEdit {
                padding: 10px;
                border: 1px solid #D1D5DB;
                border-radius: 8px;
                font-size: 14px;
                background-color: #F9FAFB;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
                border: 2px solid #3B82F6;
                background-color: #FFFFFF;
            }
            QPushButton {
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }
            QCheckBox {
                font-size: 14px;
            }
        """)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Parse existing name into cognome/nome
        existing_name = data.get('nome', '')
        parts = existing_name.split() if existing_name else []
        existing_cognome = parts[0] if len(parts) > 0 else ''
        existing_nome = ' '.join(parts[1:]) if len(parts) > 1 else ''

        # === DATI DIPENDENTE ===
        section1 = QLabel("Dati Dipendente")
        section1.setObjectName("section_title")
        self.layout.addWidget(section1)

        self.form_layout = QFormLayout()
        self.form_layout.setSpacing(12)
        self.form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)

        # Cognome
        self.cognome_edit = QLineEdit(existing_cognome)
        self.cognome_edit.setPlaceholderText("Es: ROSSI")
        self.form_layout.addRow(QLabel("Cognome:"), self.cognome_edit)

        # Nome
        self.nome_edit = QLineEdit(existing_nome)
        self.nome_edit.setPlaceholderText("Es: MARIO")
        self.form_layout.addRow(QLabel("Nome:"), self.nome_edit)

        # Matricola
        self.matricola_edit = QLineEdit(str(data.get('matricola', '')) if data.get('matricola') else '')
        self.matricola_edit.setPlaceholderText("Es: 001234")
        self.form_layout.addRow(QLabel("Matricola:"), self.matricola_edit)

        self.layout.addLayout(self.form_layout)

        # Separator
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.HLine)
        sep1.setStyleSheet("background-color: #E5E7EB;")
        self.layout.addWidget(sep1)

        # === DATI DOCUMENTO ===
        section2 = QLabel("Dati Documento")
        section2.setObjectName("section_title")
        self.layout.addWidget(section2)

        self.form_layout2 = QFormLayout()
        self.form_layout2.setSpacing(12)
        self.form_layout2.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)

        # Documento
        self.corso_edit = QLineEdit(data.get('corso', ''))
        self.corso_edit.setPlaceholderText("Nome del documento/corso")
        self.form_layout2.addRow(QLabel("Documento:"), self.corso_edit)

        # Categoria
        self.categoria_edit = QComboBox()
        unique_categories = sorted(set(categories))
        self.categoria_edit.addItems(unique_categories)
        self.categoria_edit.setCurrentText(data.get('categoria', ''))
        self.categoria_edit.setEditable(False)
        self.categoria_edit.setView(QListView())
        self.categoria_edit.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.form_layout2.addRow(QLabel("Categoria:"), self.categoria_edit)

        self.layout.addLayout(self.form_layout2)

        # Separator
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("background-color: #E5E7EB;")
        self.layout.addWidget(sep2)

        # === DATE ===
        section3 = QLabel("Date")
        section3.setObjectName("section_title")
        self.layout.addWidget(section3)

        self.form_layout3 = QFormLayout()
        self.form_layout3.setSpacing(12)
        self.form_layout3.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)

        # Data Emissione
        self.data_rilascio_edit = QDateEdit()
        self.data_rilascio_edit.setDisplayFormat(DATE_FORMAT_DISPLAY)
        self.data_rilascio_edit.setCalendarPopup(True)
        rilascio_date = QDate.fromString(data.get('data_rilascio', ''), DATE_FORMAT_DISPLAY)
        self.data_rilascio_edit.setDate(rilascio_date if rilascio_date.isValid() else QDate.currentDate())
        self.form_layout3.addRow(QLabel("Data Emissione:"), self.data_rilascio_edit)

        # Warning label for date changes
        self.warning_label = QLabel("⚠️ Verifica la data di scadenza dopo aver modificato la data di emissione")
        self.warning_label.setStyleSheet("color: #F59E0B; font-weight: bold; font-size: 12px;")
        self.warning_label.setVisible(False)
        self.data_rilascio_edit.dateChanged.connect(lambda: self.warning_label.setVisible(True))
        self.form_layout3.addRow(self.warning_label)

        # Data Scadenza
        self.scadenza_checkbox = QCheckBox("Ha una data di scadenza")
        self.data_scadenza_edit = QDateEdit()
        self.data_scadenza_edit.setDisplayFormat(DATE_FORMAT_DISPLAY)
        self.data_scadenza_edit.setCalendarPopup(True)
        self.data_scadenza_edit.setEnabled(False)

        scadenza_date_str = str(data.get('data_scadenza', ''))
        if scadenza_date_str and scadenza_date_str.lower() != 'none':
            scadenza_date = QDate.fromString(scadenza_date_str, DATE_FORMAT_DISPLAY)
            if scadenza_date.isValid():
                self.data_scadenza_edit.setDate(scadenza_date)
                self.data_scadenza_edit.setEnabled(True)
                self.scadenza_checkbox.setChecked(True)

        self.scadenza_checkbox.toggled.connect(self.data_scadenza_edit.setEnabled)

        scadenza_layout = QHBoxLayout()
        scadenza_layout.addWidget(self.scadenza_checkbox)
        scadenza_layout.addWidget(self.data_scadenza_edit)
        self.form_layout3.addRow(QLabel("Scadenza:"), scadenza_layout)

        self.layout.addLayout(self.form_layout3)

        # Spacer
        self.layout.addStretch()

        # Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        ok_button = self.button_box.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setText("Salva")
        ok_button.setStyleSheet("background-color: #3B82F6; color: white;")
        
        cancel_button = self.button_box.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_button.setText("Annulla")
        cancel_button.setStyleSheet("background-color: transparent; border: 1px solid #D1D5DB; color: #374151;")

        self.layout.addWidget(self.button_box)

        self.adjustSize()

    def get_data(self):
        # Combine cognome and nome in the correct order
        cognome = self.cognome_edit.text().strip().upper()
        nome = self.nome_edit.text().strip().upper()
        nome_completo = f"{cognome} {nome}".strip()
        
        data_scadenza = self.data_scadenza_edit.date().toString(DATE_FORMAT_DISPLAY) if self.scadenza_checkbox.isChecked() else None
        
        result = {
            "nome": nome_completo,
            "corso": self.corso_edit.text().strip(),
            "categoria": self.categoria_edit.currentText(),
            "data_rilascio": self.data_rilascio_edit.date().toString(DATE_FORMAT_DISPLAY),
            "data_scadenza": data_scadenza
        }
        
        # Add matricola if provided
        matricola = self.matricola_edit.text().strip()
        if matricola:
            result["matricola"] = matricola
        
        return result
