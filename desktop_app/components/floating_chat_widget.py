import logging
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QGraphicsDropShadowEffect, QFrame, QApplication
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QTimer, QUrl, QPoint, QEvent, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QColor, QMouseEvent, QIcon

from desktop_app.chat.html_generator import get_chat_html
from desktop_app.chat.chat_controller import ChatController
from desktop_app.utils import load_colored_icon

class FloatingChatWidget(QWidget):
    def __init__(self, api_client, voice_service, parent=None):
        super().__init__(parent)
        self.voice_service = voice_service
        
        # Expanded/Collapsed sizes
        self.collapsed_size = QSize(80, 80) # Includes margin for shadow
        self.expanded_size = QSize(400, 600)
        self.current_target_size = self.collapsed_size

        # Init size
        self.resize(self.collapsed_size)
        
        # Window Flags & Attributes
        # REMOVED SubWindow to fix rendering freeze
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
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
                border-radius: 16px;
            }
        """)
        
        # Ensure Chat Frame has a fixed width
        self.chat_frame.setFixedWidth(380)

        # Shadow for Chat Frame
        chat_shadow = QGraphicsDropShadowEffect()
        chat_shadow.setBlurRadius(40)
        chat_shadow.setColor(QColor(0, 0, 0, 40))
        chat_shadow.setOffset(0, 10)
        self.chat_frame.setGraphicsEffect(chat_shadow)

        self.chat_layout = QVBoxLayout(self.chat_frame)
        self.chat_layout.setContentsMargins(0, 0, 0, 0)
        
        self.web_view = QWebEngineView()
        # FIX: Opaque background prevents rendering freeze/lag on input
        self.web_view.page().setBackgroundColor(Qt.GlobalColor.white)
        self.web_view.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        
        # Setup WebChannel
        self.channel = QWebChannel()
        self.controller = ChatController(api_client, self)
        self.channel.registerObject("backend", self.controller)
        self.web_view.page().setWebChannel(self.channel)
        
        self.web_view.setHtml(get_chat_html(), QUrl("qrc:///"))
        
        self.chat_layout.addWidget(self.web_view)
        
        # Initially hidden (opacity 0 or just hidden)
        self.chat_frame.hide()
        self.layout.addWidget(self.chat_frame)
        
        # FAB (Avatar)
        self.fab = QPushButton()
        self.fab.setFixedSize(60, 60)
        self.fab.setCursor(Qt.CursorShape.PointingHandCursor)
        self.fab.setIcon(load_colored_icon("user.svg", "#FFFFFF"))
        self.fab.setIconSize(QSize(32, 32))
        self.fab.setStyleSheet("""
            QPushButton {
                background-color: #1D4ED8;
                color: #FFFFFF;
                border: none;
                border-radius: 30px;
            }
            QPushButton:hover {
                background-color: #2563EB;
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background-color: #1E40AF;
            }
        """)
        
        # Glow Effect for FAB
        fab_shadow = QGraphicsDropShadowEffect()
        fab_shadow.setBlurRadius(20)
        fab_shadow.setColor(QColor(29, 78, 216, 80))
        fab_shadow.setOffset(0, 4)
        self.fab.setGraphicsEffect(fab_shadow)
        
        # We handle clicking manually via eventFilter to distinguish drag vs click
        self.fab.installEventFilter(self)
        self.layout.addWidget(self.fab)

        # Connect controller signal to JS and Voice
        self.controller.response_ready.connect(self.send_response_to_js)
        self.controller.response_ready.connect(self.speak_response)

        # Animation for Snapping
        self.snap_animation = QPropertyAnimation(self, b"pos")
        self.snap_animation.setDuration(400)
        self.snap_animation.setEasingCurve(QEasingCurve.Type.OutBack)

        # Animation for Expansion (Geometry)
        self.expand_animation = QPropertyAnimation(self, b"geometry")
        self.expand_animation.setDuration(300)
        self.expand_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

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

        # Update layout alignment
        self.layout.setAlignment(Qt.AlignmentFlag.AlignBottom | align_flag)

        # Animate
        self.snap_animation.setStartValue(self.pos())
        self.snap_animation.setEndValue(QPoint(int(target_x), self.y()))
        self.snap_animation.start()

    def toggle_chat(self):
        # Determine target geometry
        current_geo = self.geometry()

        if self.is_expanded:
            # Collapse
            self.chat_frame.hide()
            target_w = self.collapsed_size.width()
            target_h = self.collapsed_size.height()

            # Calculate new Y to keep bottom anchored
            new_y = current_geo.y() + (current_geo.height() - target_h)

            target_rect = QRect(current_geo.x(), new_y, target_w, target_h)

            self.fab.setIcon(load_colored_icon("user.svg", "#FFFFFF"))
            self.is_expanded = False
        else:
            # Expand
            self.chat_frame.show()
            target_w = self.expanded_size.width()
            target_h = self.expanded_size.height()

            # Calculate new Y to grow UPWARDS
            new_y = current_geo.y() - (target_h - current_geo.height())

            target_rect = QRect(current_geo.x(), new_y, target_w, target_h)

            self.fab.setIcon(load_colored_icon("chevron-down.svg", "#FFFFFF"))
            self.is_expanded = True

        # Animate
        self.expand_animation.setStartValue(current_geo)
        self.expand_animation.setEndValue(target_rect)
        self.expand_animation.start()

        # Re-snap to ensure it stays on edge if size changed
        QTimer.singleShot(300, self.snap_to_edge)

        # Focus input in WebEngine
        if self.is_expanded:
            self.web_view.setFocus()
            script = "setTimeout(function() { document.getElementById('message-input').focus(); }, 100);"
            self.web_view.page().runJavaScript(script)

    def send_response_to_js(self, text):
        safe_text = text.replace('\\', '\\\\').replace('`', '\\`')
        script = f"onLyraResponse(`{safe_text}`);"
        self.web_view.page().runJavaScript(script)

    def speak_response(self, text):
        if self.voice_service and not self.voice_service.is_muted:
            clean_text = text.replace('*', '').replace('#', '')
            self.voice_service.speak(clean_text)
