import logging
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QGraphicsDropShadowEffect, QFrame, QApplication
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QTimer, QUrl, QPoint, QEvent, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QMouseEvent

from desktop_app.chat.html_generator import get_chat_html
from desktop_app.chat.chat_controller import ChatController

class FloatingChatWidget(QWidget):
    def __init__(self, api_client, voice_service, parent=None):
        super().__init__(parent)
        self.voice_service = voice_service
        
        # Expanded/Collapsed sizes
        self.collapsed_size = QSize(80, 80) # Includes margin for shadow
        self.expanded_size = QSize(400, 600)

        # Init size
        self.resize(self.collapsed_size)
        
        # Transparent background for the container
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.SubWindow)
        
        self.is_expanded = False
        self.is_dragging = False
        self.drag_start_pos = QPoint()
        self.widget_start_pos = QPoint()
        self.user_has_moved = False

        # Layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10) # Margin for shadow
        self.layout.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        
        # Chat Container (WebEngine)
        self.chat_frame = QFrame()
        self.chat_frame.setFixedHeight(500)
        self.chat_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 12px;
            }
        """)
        
        # Ensure Chat Frame has a fixed width to prevent shrinking when aligned
        self.chat_frame.setFixedWidth(380)

        # Shadow for Chat Frame
        chat_shadow = QGraphicsDropShadowEffect()
        chat_shadow.setBlurRadius(40)
        chat_shadow.setColor(QColor(0, 0, 0, 30))
        chat_shadow.setOffset(0, 8)
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
        
        self.chat_frame.hide() # Initially hidden
        self.layout.addWidget(self.chat_frame)
        
        # FAB (Avatar)
        self.fab = QPushButton("L")
        self.fab.setFixedSize(60, 60)
        self.fab.setCursor(Qt.CursorShape.PointingHandCursor)
        self.fab.setStyleSheet("""
            QPushButton {
                background-color: #1D4ED8;
                color: #FFFFFF;
                border: 1px solid #1E40AF;
                border-radius: 30px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563EB;
                border-color: #3B82F6;
            }
        """)
        
        # Glow Effect for FAB
        fab_shadow = QGraphicsDropShadowEffect()
        fab_shadow.setBlurRadius(20)
        fab_shadow.setColor(QColor(29, 78, 216, 60))
        fab_shadow.setOffset(0, 4)
        self.fab.setGraphicsEffect(fab_shadow)
        
        # We handle clicking manually via eventFilter to distinguish drag vs click
        self.fab.installEventFilter(self)
        self.layout.addWidget(self.fab) # Alignment set dynamically

        # Connect controller signal to JS and Voice
        self.controller.response_ready.connect(self.send_response_to_js)
        self.controller.response_ready.connect(self.speak_response)

        # Animation for Snapping
        self.snap_animation = QPropertyAnimation(self, b"pos")
        self.snap_animation.setDuration(400)
        self.snap_animation.setEasingCurve(QEasingCurve.Type.OutBack)

    def eventFilter(self, source, event):
        if source == self.fab:
            if event.type() == QEvent.Type.MouseButtonPress:
                if event.button() == Qt.MouseButton.LeftButton:
                    self.is_dragging = False
                    self.drag_start_pos = event.globalPosition().toPoint()
                    self.widget_start_pos = self.pos()
                    return True # Consume

            elif event.type() == QEvent.Type.MouseMove:
                if event.buttons() & Qt.MouseButton.LeftButton:
                    delta = event.globalPosition().toPoint() - self.drag_start_pos
                    if not self.is_dragging and delta.manhattanLength() > 5:
                        self.is_dragging = True
                        # If expanded, collapse for smooth dragging
                        if self.is_expanded:
                            self.toggle_chat()

                    if self.is_dragging:
                        self.move(self.widget_start_pos + delta)
                        self.user_has_moved = True
                        return True

            elif event.type() == QEvent.Type.MouseButtonRelease:
                if event.button() == Qt.MouseButton.LeftButton:
                    if self.is_dragging:
                        self.snap_to_edge()
                    else:
                        self.toggle_chat()
                    self.is_dragging = False
                    return True

        return super().eventFilter(source, event)

    def snap_to_edge(self):
        """Snaps the widget to the nearest Left or Right edge."""
        if not self.parent():
            return

        parent_width = self.parent().width()
        current_x = self.x() + self.width() / 2

        target_x = 0
        align_flag = Qt.AlignmentFlag.AlignLeft

        # Snap Right
        if current_x > parent_width / 2:
            target_x = parent_width - self.width() - 20 # 20px padding
            align_flag = Qt.AlignmentFlag.AlignRight
        else:
            target_x = 20 # 20px padding
            align_flag = Qt.AlignmentFlag.AlignLeft

        # Update layout alignment to ensure expanded chat opens on the correct side relative to FAB
        # (Actually, QVBoxLayout stacks vertically. Alignment controls horizontal placement in the slot)
        # We need to change the layout alignment so that child widgets align to that side
        self.layout.setAlignment(Qt.AlignmentFlag.AlignBottom | align_flag)

        # Animate
        self.snap_animation.setStartValue(self.pos())
        self.snap_animation.setEndValue(QPoint(target_x, self.y()))
        self.snap_animation.start()

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
            # Re-snap to ensure it stays on edge if size changed
            # (Resizing expands inwards if aligned correctly, but let's be safe)
            QTimer.singleShot(0, self.snap_to_edge)

    def send_response_to_js(self, text):
        safe_text = text.replace('\\', '\\\\').replace('`', '\\`')
        script = f"onLyraResponse(`{safe_text}`);"
        self.web_view.page().runJavaScript(script)

    def speak_response(self, text):
        if self.voice_service and not self.voice_service.is_muted:
            clean_text = text.replace('*', '').replace('#', '')
            self.voice_service.speak(clean_text)
