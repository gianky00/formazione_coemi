
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QFrame, QFormLayout, QComboBox, QFileDialog, QHBoxLayout
)
from PyQt6.QtCore import Qt
from dotenv import load_dotenv, set_key
from desktop_app.api_client import APIClient

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

        # SMTP Settings
        smtp_separator = QFrame()
        smtp_separator.setFrameShape(QFrame.Shape.HLine)
        smtp_separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.form_layout.addRow(smtp_separator)

        self.email_preset_combo = QComboBox()
        self.email_preset_combo.addItems(["Manuale", "Gmail", "Outlook", "COEMI"])
        self.email_preset_combo.currentIndexChanged.connect(self.apply_email_preset)
        self.form_layout.addRow(QLabel("Preset Email:"), self.email_preset_combo)

        self.smtp_host_input = QLineEdit()
        self.form_layout.addRow(QLabel("SMTP Host:"), self.smtp_host_input)

        self.smtp_port_input = QLineEdit()
        self.form_layout.addRow(QLabel("SMTP Port:"), self.smtp_port_input)

        self.smtp_user_input = QLineEdit()
        self.form_layout.addRow(QLabel("Utente SMTP (Email):"), self.smtp_user_input)

        self.smtp_password_input = QLineEdit()
        self.smtp_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.form_layout.addRow(QLabel("Password SMTP:"), self.smtp_password_input)

        self.recipients_to_input = QLineEdit()
        self.recipients_to_input.setPlaceholderText("Separati da virgola")
        self.form_layout.addRow(QLabel("Destinatari (To):"), self.recipients_to_input)

        self.recipients_cc_input = QLineEdit()
        self.recipients_cc_input.setPlaceholderText("Separati da virgola")
        self.form_layout.addRow(QLabel("Copia Conoscenza (CC):"), self.recipients_cc_input)


        self.layout.addWidget(main_card)
        self.layout.addStretch()

        # Save button
        self.save_button = QPushButton("Salva Modifiche")
        self.save_button.setObjectName("primary")
        self.save_button.clicked.connect(self.save_config)

        self.import_button = QPushButton("Importa Dipendenti da CSV")
        self.import_button.setObjectName("secondary")
        self.import_button.clicked.connect(self.import_csv)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.import_button)
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        self.layout.addLayout(button_layout)

        self.load_config()
        self.api_client = APIClient()

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
        self.smtp_host_input.setText(os.getenv("SMTP_HOST", ""))
        self.smtp_port_input.setText(os.getenv("SMTP_PORT", ""))
        self.smtp_user_input.setText(os.getenv("SMTP_USER", ""))
        self.smtp_password_input.setText(os.getenv("SMTP_PASSWORD", ""))
        self.recipients_to_input.setText(os.getenv("EMAIL_RECIPIENTS_TO", ""))
        self.recipients_cc_input.setText(os.getenv("EMAIL_RECIPIENTS_CC", ""))

    def apply_email_preset(self):
        preset = self.email_preset_combo.currentText()
        if preset == "Gmail":
            self.smtp_host_input.setText("smtp.gmail.com")
            self.smtp_port_input.setText("587")
        elif preset == "Outlook":
            self.smtp_host_input.setText("smtp.office365.com")
            self.smtp_port_input.setText("587")
        elif preset == "COEMI":
            self.smtp_host_input.setText("smtps.aruba.it")
            self.smtp_port_input.setText("587")
        # Manual preset does not change anything

    def import_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleziona CSV", "", "CSV Files (*.csv)")
        if file_path:
            try:
                response = self.api_client.import_dipendenti_csv(file_path)
                QMessageBox.information(
                    self,
                    "Importazione Completata",
                    response.get("message", "Importazione dei dipendenti completata con successo.")
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Errore di Importazione",
                    f"Impossibile importare il file CSV: {e}"
                )

    def save_config(self):
        env_path = self.get_env_path()
        try:
            set_key(env_path, "GEMINI_API_KEY", self.gemini_api_key_input.text())
            set_key(env_path, "GOOGLE_CLOUD_PROJECT", self.gcp_project_id_input.text())
            set_key(env_path, "GCS_BUCKET_NAME", self.gcs_bucket_name_input.text())
            set_key(env_path, "SMTP_HOST", self.smtp_host_input.text())
            set_key(env_path, "SMTP_PORT", self.smtp_port_input.text())
            set_key(env_path, "SMTP_USER", self.smtp_user_input.text())
            set_key(env_path, "SMTP_PASSWORD", self.smtp_password_input.text())
            set_key(env_path, "EMAIL_RECIPIENTS_TO", self.recipients_to_input.text())
            set_key(env_path, "EMAIL_RECIPIENTS_CC", self.recipients_cc_input.text())

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
