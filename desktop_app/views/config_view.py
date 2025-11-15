
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFrame
from PyQt6.QtCore import Qt

class ConfigView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Main content card
        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card.setFrameShadow(QFrame.Shadow.Raised)
        card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 15px;
                max-width: 400px;
            }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(15)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Title
        title = QLabel("Addestramento Modello AI")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title)

        # Description
        description = QLabel("Migliora l'accuratezza del riconoscimento analizzando i certificati convalidati.")
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setStyleSheet("font-size: 14px; color: #555;")
        card_layout.addWidget(description)

        # Action Button
        self.train_button = QPushButton("Avvia Addestramento")
        self.train_button.clicked.connect(self.start_training)
        card_layout.addWidget(self.train_button)

        self.layout.addWidget(card)

    def start_training(self):
        # Placeholder for the fine-tuning logic
        print("Fine-tuning the AI model...")
