from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QComboBox, QFormLayout, QDialogButtonBox, QMessageBox
)
from PySide6.QtCore import Qt

from app.core.constants import CATEGORIE_STATICHE


class EditCertificatoDialog(QDialog):
    def __init__(self, parent, controller, cert_data):
        super().__init__(parent)
        self.controller = controller
        self.cert = cert_data
        self.parent_view = parent

        self.setWindowTitle(f"Modifica Certificato #{cert_data.get('id')}")
        self.setFixedWidth(500)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        form = QFormLayout()
        form.setSpacing(15)

        self.edit_dip = QLineEdit(self.cert.get("nome") or "")
        self.edit_corso = QLineEdit(self.cert.get("corso") or "")
        
        self.combo_cat = QComboBox()
        self.combo_cat.addItems(sorted(CATEGORIE_STATICHE))
        current_cat = self.cert.get("categoria") or "ALTRO"
        self.combo_cat.setCurrentText(current_cat if current_cat in CATEGORIE_STATICHE else "ALTRO")
        
        self.edit_ril = QLineEdit(self.cert.get("data_rilascio") or "")
        self.edit_scad = QLineEdit(self.cert.get("data_scadenza") or "")
        
        form.addRow("Dipendente:", self.edit_dip)
        form.addRow("Corso:", self.edit_corso)
        form.addRow("Categoria:", self.combo_cat)
        form.addRow("Rilascio (DD/MM/YYYY):", self.edit_ril)
        form.addRow("Scadenza (DD/MM/YYYY):", self.edit_scad)
        
        layout.addLayout(form)
        
        btn_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btn_box.button(QDialogButtonBox.Save).setText("SALVA MODIFICHE")
        btn_box.button(QDialogButtonBox.Save).setStyleSheet("background-color: #1D4ED8; color: white; font-weight: bold;")
        
        btn_box.accepted.connect(self.save)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def save(self):
        data = {
            "nome": self.edit_dip.text(),
            "corso": self.edit_corso.text(),
            "categoria": self.combo_cat.currentText(),
            "data_rilascio": self.edit_ril.text(),
            "data_scadenza": self.edit_scad.text(),
        }

        if not data["nome"]:
            QMessageBox.warning(self, "Errore", "Il nome dipendente è obbligatorio.")
            return

        try:
            self.controller.api_client.update_certificato(self.cert["id"], data)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Errore", str(e))
