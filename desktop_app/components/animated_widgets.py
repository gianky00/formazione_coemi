from PyQt6.QtWidgets import QPushButton, QLineEdit, QFrame, QGraphicsOpacityEffect, QWidget
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty, QRect, QSize, QTimer, QPoint, QObject, pyqtSignal, QParallelAnimationGroup
from PyQt6.QtGui import QColor, QPalette, QPainter, QBrush, QPen

class AnimatedButton(QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._bg_color = QColor("#1D4ED8") # Default Primary
        self._text_color = QColor("white")
        self._border_radius = 8
        self.default_bg = QColor("#1D4ED8")
        self.hover_bg = QColor("#1E40AF")
        self.pressed_bg = QColor("#1E3A8A")

        # Ripple effect variables
        self._ripple_radius = 0
        self._ripple_opacity = 0.0
        self._ripple_center = QPoint()
        self._ripple_timer = QTimer(self)
        self._ripple_timer.setInterval(16) # ~60fps
        self._ripple_timer.timeout.connect(self._update_ripple)

        # Color animation
        self._color_anim = QPropertyAnimation(self, b"backgroundColor", self)
        self._color_anim.setDuration(150)

    @pyqtProperty(QColor)
    def backgroundColor(self):
        return self._bg_color

    @backgroundColor.setter
    def backgroundColor(self, color):
        self._bg_color = color
        self.update()

    def set_colors(self, default, hover, pressed, text=QColor("white")):
        self.default_bg = QColor(default)
        self._bg_color = self.default_bg
        self.hover_bg = QColor(hover)
        self.pressed_bg = QColor(pressed)
        self._text_color = QColor(text)
        self.update()

    def enterEvent(self, event):
        self._color_anim.stop()
        self._color_anim.setEndValue(self.hover_bg)
        self._color_anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._color_anim.stop()
        self._color_anim.setEndValue(self.default_bg)
        self._color_anim.start()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self._start_ripple(event.pos())
        self._bg_color = self.pressed_bg
        self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._color_anim.stop()
        self._color_anim.setEndValue(self.hover_bg if self.underMouse() else self.default_bg)
        self._color_anim.start()
        super().mouseReleaseEvent(event)

    def _start_ripple(self, pos):
        self._ripple_center = pos
        self._ripple_radius = 0
        self._ripple_opacity = 0.4
        self._ripple_timer.start()

    def _update_ripple(self):
        self._ripple_radius += 5
        self._ripple_opacity -= 0.02
        if self._ripple_opacity <= 0:
            self._ripple_timer.stop()
            self._ripple_opacity = 0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw Background
        path = QFrame.rect(self)
        painter.setBrush(QBrush(self._bg_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), self._border_radius, self._border_radius)

        # Draw Ripple
        if self._ripple_opacity > 0:
            painter.setBrush(QBrush(QColor(255, 255, 255, int(255 * self._ripple_opacity))))
            painter.drawEllipse(self._ripple_center, self._ripple_radius, self._ripple_radius)

        # Draw Text
        painter.setPen(self._text_color)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())


class AnimatedInput(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._border_color = QColor("#D1D5DB")
        self._border_width = 1.0

        self.default_border = QColor("#D1D5DB")
        self.hover_border = QColor("#3B82F6")
        self.focus_border = QColor("#2563EB")

        # Setup animations
        self._anim_color = QPropertyAnimation(self, b"borderColor", self)
        self._anim_color.setDuration(200)

        self._anim_width = QPropertyAnimation(self, b"borderWidth", self)
        self._anim_width.setDuration(200)

        # Apply base style to handle padding/text, but we'll draw border manually?
        # No, drawing border manually on QLineEdit is risky for text layout.
        # Strategy: Use QStyleSheet for base, but that prevents QPropertyAnimation on colors.
        # Alternative: Paint the border over the widget in paintEvent.
        self.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                background-color: #FFFFFF;
                border: none; /* We draw it */
                border-radius: 8px;
                font-size: 14px;
                color: #1F2937;
            }
        """)

    @pyqtProperty(QColor)
    def borderColor(self):
        return self._border_color

    @borderColor.setter
    def borderColor(self, color):
        self._border_color = color
        self.update()

    @pyqtProperty(float)
    def borderWidth(self):
        return self._border_width

    @borderWidth.setter
    def borderWidth(self, width):
        self._border_width = width
        self.update()

    def enterEvent(self, event):
        if not self.hasFocus():
            self._anim_color.stop()
            self._anim_color.setEndValue(self.hover_border)
            self._anim_color.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self.hasFocus():
            self._anim_color.stop()
            self._anim_color.setEndValue(self.default_border)
            self._anim_color.start()
        super().leaveEvent(event)

    def focusInEvent(self, event):
        self._anim_color.stop()
        self._anim_color.setEndValue(self.focus_border)
        self._anim_color.start()

        self._anim_width.stop()
        self._anim_width.setEndValue(2.0)
        self._anim_width.start()
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self._anim_color.stop()
        self._anim_color.setEndValue(self.default_border)
        self._anim_color.start()

        self._anim_width.stop()
        self._anim_width.setEndValue(1.0)
        self._anim_width.start()
        super().focusOutEvent(event)

    def paintEvent(self, event):
        # Let standard QLineEdit draw text and background
        super().paintEvent(event)

        # Draw animated border on top
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pen = QPen(self._border_color)
        pen.setWidthF(self._border_width)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        # Adjust rect for pen width
        rect = self.rect()
        margin = self._border_width / 2
        rect_f = list(rect.getRect())
        rect_f[0] += margin
        rect_f[1] += margin
        rect_f[2] -= 2 * margin
        rect_f[3] -= 2 * margin

        painter.drawRoundedRect(QRect(*[int(x) for x in rect_f]), 8, 8)


class CardWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E5E7EB;
            }
        """)

        # Shadow effect (simulated or real)
        # Real shadow using QGraphicsDropShadowEffect can be expensive.
        # We'll stick to border for now, maybe add shadow if requested.

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0)

    def animate_in(self, delay=0):
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(600)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        if delay > 0:
            QTimer.singleShot(delay, self.anim.start)
        else:
            self.anim.start()

class LoadingOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hide()
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.setInterval(16)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False) # Block mouse

    def start(self):
        if self.parent():
            self.resize(self.parent().size())
        self.show()
        self.raise_() # Ensure on top
        self.timer.start()

    def stop(self):
        self.timer.stop()
        self.hide()

    def update_animation(self):
        self.angle = (self.angle + 10) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Semi-transparent background
        painter.setBrush(QBrush(QColor(0, 0, 0, 100)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())

        # Draw Spinner
        center = self.rect().center()
        radius = 25

        painter.setPen(QPen(QColor("#3B82F6"), 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawArc(center.x() - radius, center.y() - radius, radius * 2, radius * 2, -self.angle * 16, 270 * 16)
