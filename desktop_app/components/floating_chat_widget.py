import logging
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QGraphicsDropShadowEffect, QFrame
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QTimer, QUrl
from PyQt6.QtGui import QColor, QIcon

from desktop_app.chat.html_generator import get_chat_html
from desktop_app.chat.chat_controller import ChatController

class FloatingChatWidget(QWidget):
    def __init__(self, api_client, voice_service, parent=None):
        super().__init__(parent)
        self.voice_service = voice_service
        
        # Expanded/Collapsed sizes
        self.collapsed_size = QSize(80, 80) # Includes margin for shadow
        self.expanded_size = QSize(400, 550)

        # Init size
        self.resize(self.collapsed_size)
        
        # Transparent background for the container
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.SubWindow)
        
        self.is_expanded = False

        # Layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10) # Margin for shadow
        self.layout.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        
        # Chat Container (WebEngine)
        self.chat_frame = QFrame()
        self.chat_frame.setFixedHeight(450)
        self.chat_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(20, 20, 40, 0.95);
                border: 1px solid rgba(100, 100, 255, 0.3);
                border-radius: 15px;
            }
        """)
        
        # Shadow for Chat Frame
        chat_shadow = QGraphicsDropShadowEffect()
        chat_shadow.setBlurRadius(30)
        chat_shadow.setColor(QColor(0, 0, 0, 100))
        chat_shadow.setOffset(0, 10)
        self.chat_frame.setGraphicsEffect(chat_shadow)

        self.chat_layout = QVBoxLayout(self.chat_frame)
        self.chat_layout.setContentsMargins(0, 0, 0, 0)
        
        self.web_view = QWebEngineView()
        self.web_view.page().setBackgroundColor(Qt.GlobalColor.transparent)
        
        # Setup WebChannel
        self.channel = QWebChannel()
        self.controller = ChatController(self)
        self.channel.registerObject("backend", self.controller)
        self.web_view.page().setWebChannel(self.channel)
        
        self.web_view.setHtml(get_chat_html(), QUrl("qrc:///"))
        
        self.chat_layout.addWidget(self.web_view)
        
        self.chat_frame.hide() # Initially hidden
        self.layout.addWidget(self.chat_frame)
        
        # FAB
        self.fab = QPushButton("L")
        self.fab.setFixedSize(60, 60)
        self.fab.setCursor(Qt.CursorShape.PointingHandCursor)
        self.fab.setStyleSheet("""
            QPushButton {
                background-color: #141428;
                color: #6366f1;
                border: 1px solid rgba(100, 100, 255, 0.5);
                border-radius: 30px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e1e38;
                border-color: #818cf8;
            }
        """)
        
        # Glow Effect for FAB
        fab_shadow = QGraphicsDropShadowEffect()
        fab_shadow.setBlurRadius(20)
        fab_shadow.setColor(QColor(99, 102, 241, 150))
        fab_shadow.setOffset(0, 0)
        self.fab.setGraphicsEffect(fab_shadow)
        
        self.fab.clicked.connect(self.toggle_chat)
        self.layout.addWidget(self.fab, alignment=Qt.AlignmentFlag.AlignRight)

        # Connect controller signal to JS and Voice
        self.controller.response_ready.connect(self.send_response_to_js)
        self.controller.response_ready.connect(self.speak_response)

    def toggle_chat(self):
        if self.is_expanded:
            self.chat_frame.hide()
            self.resize(self.collapsed_size)
            self.is_expanded = False
            self.fab.setText("L")
        else:
            self.resize(self.expanded_size)
            self.chat_frame.show()
            self.is_expanded = True
            self.fab.setText("×")
        
        # Notify parent to update position (since we changed size)
        if self.parent() and hasattr(self.parent(), 'resizeEvent'):
            QTimer.singleShot(0, lambda: self.parent().resizeEvent(None))

    def send_response_to_js(self, text):
        # Escape backticks and backslashes for JS template string
        safe_text = text.replace('\\', '\\\\').replace('`', '\\`')
        script = f"onLyraResponse(`{safe_text}`);"
        self.web_view.page().runJavaScript(script)

    def speak_response(self, text):
        if self.voice_service and not self.voice_service.is_muted:
            # Simple cleanup for speech (remove markdown)
            clean_text = text.replace('*', '').replace('#', '')
            self.voice_service.speak(clean_text)
