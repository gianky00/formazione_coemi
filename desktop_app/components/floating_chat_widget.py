import logging
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QGraphicsDropShadowEffect,
                             QFrame, QLabel, QApplication)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import (Qt, QSize, pyqtSignal, QTimer, QUrl, QPoint, QPropertyAnimation,
                          QEasingCurve, QRect)
from PyQt6.QtGui import QColor, QIcon, QPainter, QBrush, QPen

from desktop_app.chat.html_generator import get_chat_html
from desktop_app.chat.chat_controller import ChatController

class FloatingChatWidget(QWidget):
    def __init__(self, api_client, voice_service, parent=None):
        super().__init__(parent)
        self.voice_service = voice_service
        self.api_client = api_client
        
        # Dimensions
        self.collapsed_size = QSize(70, 70)
        self.expanded_size = QSize(400, 600)

        self.resize(self.collapsed_size)
        
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.SubWindow)
        
        self.is_expanded = False
        self.dragging = False
        self.drag_start_position = QPoint()

        # Layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        self.layout.setSpacing(10)
        
        # 1. Chat Container (WebEngine)
        self.chat_frame = QFrame()
        self.chat_frame.setFixedHeight(500)
        self.chat_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 16px;
            }
        """)
        
        # Shadow for Chat Frame
        chat_shadow = QGraphicsDropShadowEffect()
        chat_shadow.setBlurRadius(40)
        chat_shadow.setColor(QColor(0, 0, 0, 40))
        chat_shadow.setOffset(0, 10)
        self.chat_frame.setGraphicsEffect(chat_shadow)

        self.chat_layout = QVBoxLayout(self.chat_frame)
        self.chat_layout.setContentsMargins(0, 0, 0, 0)
        
        self.web_view = QWebEngineView()
        self.web_view.page().setBackgroundColor(Qt.GlobalColor.transparent)
        
        # Setup WebChannel
        self.channel = QWebChannel()
        self.controller = ChatController(api_client, self)
        self.channel.registerObject("backend", self.controller)
        self.web_view.page().setWebChannel(self.channel)
        
        self.web_view.setHtml(get_chat_html(), QUrl("qrc:///"))
        
        self.chat_layout.addWidget(self.web_view)
        
        self.chat_frame.hide()
        self.layout.addWidget(self.chat_frame)
        
        # 2. Status Label (Thinking)
        self.status_label = QLabel("Analisi in corso...")
        self.status_label.setStyleSheet("""
            background-color: #1D4ED8;
            color: white;
            padding: 6px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.hide()

        # Add shadow to label
        lbl_shadow = QGraphicsDropShadowEffect()
        lbl_shadow.setBlurRadius(10)
        lbl_shadow.setColor(QColor(0, 0, 0, 30))
        self.status_label.setGraphicsEffect(lbl_shadow)

        self.layout.addWidget(self.status_label, alignment=Qt.AlignmentFlag.AlignRight)

        # 3. FAB (Floating Action Button)
        self.fab = QPushButton("✨") # Sparkle icon
        self.fab.setFixedSize(60, 60)
        self.fab.setCursor(Qt.CursorShape.PointingHandCursor)
        # Modern Light Theme Style for FAB
        self.fab.setStyleSheet("""
            QPushButton {
                background-color: #1D4ED8; /* Royal Blue */
                color: #FFFFFF;
                border: none;
                border-radius: 30px;
                font-family: 'Segoe UI Emoji', 'Segoe UI', sans-serif;
                font-size: 28px;
            }
            QPushButton:hover {
                background-color: #1E40AF;
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background-color: #1E3A8A;
            }
        """)
        
        # Glow Effect for FAB
        fab_shadow = QGraphicsDropShadowEffect()
        fab_shadow.setBlurRadius(25)
        fab_shadow.setColor(QColor(29, 78, 216, 120)) # Blue glow
        fab_shadow.setOffset(0, 4)
        self.fab.setGraphicsEffect(fab_shadow)
        
        self.fab.clicked.connect(self.toggle_chat)
        self.layout.addWidget(self.fab, alignment=Qt.AlignmentFlag.AlignRight)

        # 4. Connections
        # Fix Double-Speak: Only connect once
        try:
            self.controller.response_ready.disconnect()
        except:
            pass

        self.controller.response_ready.connect(self.send_response_to_js)
        self.controller.response_ready.connect(self.speak_response)

        # Thinking Status
        self.controller.thinking_status.connect(self.update_thinking_status)

        # Animation for Snapping
        self.anim = QPropertyAnimation(self, b"pos")
        self.anim.setEasingCurve(QEasingCurve.Type.OutBack)
        self.anim.setDuration(400)

    def toggle_chat(self):
        if self.dragging: return # Don't toggle if we just dragged

        if self.is_expanded:
            self.chat_frame.hide()
            self.resize(self.collapsed_size)
            self.is_expanded = False
            self.fab.setText("✨")
        else:
            self.resize(self.expanded_size)
            self.chat_frame.show()
            self.is_expanded = True
            self.fab.setText("×")
            self.web_view.setFocus()
        
        # If we expanded, we might be off-screen. Move slightly if needed?
        # For now, rely on user to drag it back if they moved it weirdly.

    def update_thinking_status(self, is_thinking):
        if is_thinking:
            self.status_label.show()
        else:
            self.status_label.hide()

    def send_response_to_js(self, text):
        safe_text = text.replace('\\', '\\\\').replace('`', '\\`')
        script = f"onLyraResponse(`{safe_text}`);"
        self.web_view.page().runJavaScript(script)

    def speak_response(self, text):
        if self.voice_service and not self.voice_service.is_muted:
            clean_text = text.replace('*', '').replace('#', '')
            self.voice_service.speak(clean_text)

    # --- Draggable Logic ---

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Allow drag only if collapsed
            if not self.is_expanded:
                self.dragging = True
                self.drag_start_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_start_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if self.dragging:
            self.dragging = False
            self.snap_to_edge()
            event.accept()

    def snap_to_edge(self):
        # Snap to nearest vertical edge (Left or Right)
        if not self.parent(): return

        parent_rect = self.parent().rect()
        my_rect = self.geometry()

        target_x = 0

        # Calculate distance to left vs right
        dist_left = my_rect.center().x() - parent_rect.left()
        dist_right = parent_rect.right() - my_rect.center().x()

        padding = 20

        if dist_left < dist_right:
            target_x = parent_rect.left() + padding
        else:
            target_x = parent_rect.right() - my_rect.width() - padding

        # Keep Y within bounds
        target_y = max(padding, min(my_rect.y(), parent_rect.bottom() - my_rect.height() - padding))

        self.anim.setStartValue(self.pos())
        self.anim.setEndValue(QPoint(target_x, target_y))
        self.anim.start()
