from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QDialogButtonBox, QLabel
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl

class ContactDialog(QDialog):
    """
    A dialog window for contacting support via email.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Contatta il Supporto")
        self.layout = QVBoxLayout(self)

        self.label = QLabel("Scrivi il tuo messaggio qui sotto:")
        self.layout.addWidget(self.label)

        self.message_edit = QTextEdit()
        self.layout.addWidget(self.message_edit)

        self.button_box = QDialogButtonBox()
        self.button_box.addButton("Invia", QDialogButtonBox.ButtonRole.AcceptRole)
        self.button_box.addButton(QDialogButtonBox.StandardButton.Cancel)

        self.button_box.accepted.connect(self.send_email)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def send_email(self) -> None:
        """
        Opens the default email client with a pre-filled support email.
        """
        body = self.message_edit.toPlainText()
        url = QUrl(f"mailto:giancarlo.allegretti@coemi.it?subject=Supporto Intelleo&body={body}")
        QDesktopServices.openUrl(url)
        self.accept()
