from PyQt6.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QLineEdit, QScrollArea, QSizePolicy, QGraphicsDropShadowEffect,
    QGridLayout
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve, pyqtSignal, QSize, QTimer
from PyQt6.QtGui import QColor, QIcon, QPainter, QPainterPath
from desktop_app.utils import get_asset_path, load_colored_icon
from desktop_app.api_client import APIClient
from desktop_app.services.voice_service import VoiceService

class ChatBubble(QFrame):
    def __init__(self, text, is_user=False, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 5, 0, 5)
        
        self.bubble = QLabel(text)
        self.bubble.setWordWrap(True)
        self.bubble.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        # Max width constraint
        self.bubble.setMaximumWidth(220)
        
        # Styling
        if is_user:
            self.bubble.setStyleSheet("""
                background-color: #2563EB; 
                color: white; 
                border-radius: 12px; 
                padding: 8px 12px;
                border-bottom-right-radius: 2px;
            """)
            self.layout.addStretch()
            self.layout.addWidget(self.bubble)
        else:
            self.bubble.setStyleSheet("""
                background-color: #F3F4F6; 
                color: #1F2937; 
                border-radius: 12px; 
                padding: 8px 12px;
                border-bottom-left-radius: 2px;
                border: 1px solid #E5E7EB;
            """)
            self.layout.addWidget(self.bubble)
            self.layout.addStretch()

class SuggestionChip(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: #EFF6FF;
                color: #1D4ED8;
                border: 1px solid #BFDBFE;
                border-radius: 16px;
                padding: 6px 12px;
                text-align: left;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #DBEAFE;
            }
        """)

class FloatingChatWidget(QWidget):
    def __init__(self, api_client: APIClient, voice_service: VoiceService, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.voice_service = voice_service
        self.expanded = False
        
        # Fixed size for FAB, Expandable for Window
        self.setFixedSize(400, 600) # Max area needed
        
        # IMPORTANT: Translucent background to allow non-rectangular shapes
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Main Layout
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        self.layout.setContentsMargins(0, 0, 20, 20)
        
        # --- Chat Window ---
        self.chat_window = QFrame()
        self.chat_window.setFixedSize(320, 450)
        self.chat_window.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 16px;
                border: 1px solid #E5E7EB;
            }
        """)
        # Shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.chat_window.setGraphicsEffect(shadow)
        
        self.chat_layout = QVBoxLayout(self.chat_window)
        self.chat_layout.setContentsMargins(0, 0, 0, 0)
        self.chat_layout.setSpacing(0)
        
        # Header
        header = QFrame()
        header.setFixedHeight(60)
        header.setStyleSheet("background-color: #1D4ED8; border-top-left-radius: 16px; border-top-right-radius: 16px;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 0, 15, 0)
        
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        title = QLabel("Intelleo Assistant")
        title.setStyleSheet("color: white; font-weight: bold; font-size: 14px; border: none;")
        subtitle = QLabel("Online")
        subtitle.setStyleSheet("color: #BFDBFE; font-size: 11px; border: none;")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        
        header_layout.addLayout(title_box)
        header_layout.addStretch()
        
        self.mute_btn = QPushButton()
        self.mute_btn.setFixedSize(30, 30)
        self.mute_btn.setCheckable(True)
        self.mute_btn.setStyleSheet("""
            QPushButton { background: rgba(255,255,255,0.2); border-radius: 15px; border: none; }
            QPushButton:hover { background: rgba(255,255,255,0.3); }
            QPushButton:checked { background: #EF4444; }
        """)
        # Load Mute Icon (Speaker)
        # Assuming lucide icons volume-2.svg and volume-x.svg exist or using text
        # Fallback to Text if icons missing
        self.mute_btn.setText("🔊")
        self.mute_btn.clicked.connect(self.toggle_mute)
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton { background: transparent; color: white; border: none; font-size: 16px; }
            QPushButton:hover { background: rgba(255,255,255,0.2); border-radius: 15px; }
        """)
        close_btn.clicked.connect(self.toggle_expand)
        
        header_layout.addWidget(self.mute_btn)
        header_layout.addWidget(close_btn)
        
        self.chat_layout.addWidget(header)
        
        # Scroll Area for Messages
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background: transparent;")
        self.messages_layout = QVBoxLayout(self.scroll_content)
        self.messages_layout.addStretch() # Push messages down
        self.scroll_area.setWidget(self.scroll_content)
        self.chat_layout.addWidget(self.scroll_area)
        
        # Suggestions (Zero State)
        self.suggestions_frame = QFrame()
        self.suggestions_frame.setStyleSheet("background: transparent; border: none;")
        suggestions_layout = QGridLayout(self.suggestions_frame)
        suggestions_layout.setContentsMargins(10, 5, 10, 5)
        
        prompts = [
            "Certificati in scadenza?",
            "Chi deve rinnovare?",
            "Documenti da validare?",
            "Riassunto situazione."
        ]
        
        for i, prompt in enumerate(prompts):
            btn = SuggestionChip(prompt)
            btn.clicked.connect(lambda checked, p=prompt: self.send_message(p))
            suggestions_layout.addWidget(btn, i // 2, i % 2)
            
        self.chat_layout.addWidget(self.suggestions_frame)
        
        # Footer (Input)
        footer = QFrame()
        footer.setFixedHeight(60)
        footer.setStyleSheet("border-top: 1px solid #F3F4F6; background: white; border-bottom-left-radius: 16px; border-bottom-right-radius: 16px;")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(10, 10, 10, 10)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Chiedi a Intelleo...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E5E7EB;
                border-radius: 20px;
                padding: 5px 15px;
                background: #F9FAFB;
            }
            QLineEdit:focus { border: 1px solid #2563EB; }
        """)
        self.input_field.returnPressed.connect(lambda: self.send_message())
        
        self.send_btn = QPushButton("➤")
        self.send_btn.setFixedSize(36, 36)
        self.send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: white;
                border-radius: 18px;
                border: none;
                padding-left: 3px;
            }
            QPushButton:hover { background-color: #1D4ED8; }
        """)
        self.send_btn.clicked.connect(lambda: self.send_message())
        
        footer_layout.addWidget(self.input_field)
        footer_layout.addWidget(self.send_btn)
        self.chat_layout.addWidget(footer)
        
        self.layout.addWidget(self.chat_window)
        self.chat_window.hide() # Initial state
        
        # --- FAB Button ---
        self.fab = QPushButton()
        self.fab.setFixedSize(60, 60)
        self.fab.setCursor(Qt.CursorShape.PointingHandCursor)
        self.fab.setStyleSheet("""
            QPushButton {
                background-color: #1D4ED8;
                border-radius: 30px;
                border: none;
                
            }
            QPushButton:hover {
                background-color: #1E40AF;
                margin-top: -2px; 
            }
        """)
        # Shadow for FAB
        fab_shadow = QGraphicsDropShadowEffect(self)
        fab_shadow.setBlurRadius(15)
        fab_shadow.setColor(QColor(0, 0, 0, 60))
        fab_shadow.setYOffset(4)
        self.fab.setGraphicsEffect(fab_shadow)
        
        # Set Icon
        # We try to load the robot female icon
        # Or create a custom paint event? SVG is better.
        icon_path = "desktop_app/assets/icons/robot_female.svg"
        if get_asset_path(icon_path):
             # We want it white
             self.fab.setIcon(load_colored_icon("robot_female.svg", "#FFFFFF")) # Assuming it's in lucide folder logic or absolute
             # Actually load_colored_icon looks in 'desktop_app/icons/lucide/'. 
             # Our robot is in 'desktop_app/assets/icons/'.
             # Let's handle it manually or move it.
             pass
        
        # Set Icon manually
        pixmap = QIcon(get_asset_path("desktop_app/assets/icons/robot_female.svg")).pixmap(QSize(32, 32))
        self.fab.setIcon(QIcon(pixmap))
        self.fab.setIconSize(QSize(32, 32))
        
        self.fab.clicked.connect(self.toggle_expand)
        self.layout.addWidget(self.fab, alignment=Qt.AlignmentFlag.AlignRight)
        
        # Animation
        self.animation = QPropertyAnimation(self.chat_window, b"geometry")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.chat_history = []

    def toggle_expand(self):
        self.expanded = not self.expanded
        
        if self.expanded:
            self.chat_window.show()
            self.fab.hide()
            self.input_field.setFocus()
            # We could animate opacity or size. Geometry is tricky in a layout.
            # Simple visibility toggle is robust.
        else:
            self.chat_window.hide()
            self.fab.show()

    def toggle_mute(self):
        is_muted = self.voice_service.toggle_mute()
        self.mute_btn.setChecked(is_muted)
        self.mute_btn.setText("🔇" if is_muted else "🔊")

    def add_message(self, text, is_user=True):
        bubble = ChatBubble(text, is_user)
        self.messages_layout.addWidget(bubble)
        
        # Scroll to bottom
        QTimer.singleShot(100, lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        ))
        
        self.chat_history.append({"role": "user" if is_user else "model", "content": text})
        
        if is_user:
            self.suggestions_frame.hide()

    def send_message(self, text=None):
        msg = text or self.input_field.text().strip()
        if not msg:
            return
            
        self.input_field.clear()
        self.add_message(msg, is_user=True)
        
        # Disable input while processing?
        # self.input_field.setEnabled(False)
        
        # Call API in background (pseudo-code, need QThread or worker for API calls to not freeze UI)
        # Using a QTimer to simulate async delay for now, but should use a worker.
        # We can reuse a generic worker pattern or just blocking call if acceptable (Flash is fast).
        # Blocking call freezes UI. Better use a thread.
        
        from PyQt6.QtCore import QThread, pyqtSignal
        
        class ChatWorker(QThread):
            finished = pyqtSignal(dict)
            def __init__(self, api, message, history):
                super().__init__()
                self.api = api
                self.message = message
                self.history = history
            def run(self):
                try:
                    # Pass history excluding the last message we just added? 
                    # Or the full history? The API expects 'history' as context.
                    # We should pass current history minus the new message?
                    # The backend will append the new message to the history prompt.
                    # Let's pass the history collected so far.
                    resp = self.api.send_chat_message(self.message, self.history[:-1])
                    self.finished.emit(resp)
                except Exception as e:
                    self.finished.emit({"response": f"Errore di connessione: {e}"})

        self.worker = ChatWorker(self.api_client, msg, self.chat_history)
        self.worker.finished.connect(self.on_reply_received)
        self.worker.start()

    def on_reply_received(self, response):
        reply = response.get("response", "Errore nel ricevere la risposta.")
        self.add_message(reply, is_user=False)
        
        # Voice Output
        if not self.voice_service.is_muted:
            # Strip markdown asterisks for cleaner speech
            clean_text = reply.replace("*", "")
            self.voice_service.speak(clean_text)
