from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton

class ConfigView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.improve_ai_button = QPushButton("Migliora IA")
        self.improve_ai_button.clicked.connect(self.improve_ai)
        self.layout.addWidget(self.improve_ai_button)

    def improve_ai(self):
        # Placeholder for the fine-tuning logic
        print("Fine-tuning the AI model...")
