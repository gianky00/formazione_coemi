
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QFrame, QFormLayout
)
from PyQt6.QtCore import Qt
from dotenv import load_dotenv, set_key

class ConfigView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        # Title
        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)
        title = QLabel("Configurazione")
        title.setObjectName("viewTitle")
        title_layout.addWidget(title)
        description = QLabel("Gestisci le impostazioni e le chiavi API dell'applicazione.")
        description.setObjectName("viewDescription")
        title_layout.addWidget(description)
        self.layout.addLayout(title_layout)

        # Main settings card
        main_card = QFrame()
        main_card.setObjectName("card")
        self.form_layout = QFormLayout(main_card)
        self.form_layout.setSpacing(15)
        self.form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)

        # API Settings
        self.gemini_api_key_input = QLineEdit()
        self.gemini_api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.form_layout.addRow(QLabel("Gemini API Key:"), self.gemini_api_key_input)

        self.gcp_project_id_input = QLineEdit()
        self.form_layout.addRow(QLabel("Google Cloud Project ID:"), self.gcp_project_id_input)

        self.gcs_bucket_name_input = QLineEdit()
        self.form_layout.addRow(QLabel("Google Cloud Storage Bucket:"), self.gcs_bucket_name_input)

        self.layout.addWidget(main_card)
        self.layout.addStretch()

        # Save button
        self.save_button = QPushButton("Salva Modifiche")
        self.save_button.setObjectName("primary")
        self.save_button.clicked.connect(self.save_config)
        self.layout.addWidget(self.save_button, 0, Qt.AlignmentFlag.AlignRight)

        self.load_config()

    def get_env_path(self):
        # Assumes .env file is in the root directory of the project
        return os.path.join(os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ), '.env')

    def load_config(self):
        env_path = self.get_env_path()

        # Create .env if it doesn't exist
        if not os.path.exists(env_path):
            with open(env_path, 'w') as f:
                f.write("# Configuration file for Intelleo\n")

        load_dotenv(dotenv_path=env_path)

        self.gemini_api_key_input.setText(os.getenv("GEMINI_API_KEY", ""))
        self.gcp_project_id_input.setText(os.getenv("GOOGLE_CLOUD_PROJECT", ""))
        self.gcs_bucket_name_input.setText(os.getenv("GCS_BUCKET_NAME", ""))

    def save_config(self):
        env_path = self.get_env_path()
        try:
            set_key(env_path, "GEMINI_API_KEY", self.gemini_api_key_input.text())
            set_key(env_path, "GOOGLE_CLOUD_PROJECT", self.gcp_project_id_input.text())
            set_key(env_path, "GCS_BUCKET_NAME", self.gcs_bucket_name_input.text())

            QMessageBox.information(
                self,
                "Configurazione Salvata",
                "Le modifiche sono state salvate con successo. "
                "Per renderle effettive, riavvia l'applicazione."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Errore di Salvataggio",
                f"Impossibile salvare la configurazione: {e}"
            )
