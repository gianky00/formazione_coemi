from PyQt6.QtWidgets import QPushButton, QLineEdit, QFrame, QGraphicsOpacityEffect, QWidget, QVBoxLayout, QLabel, QProgressBar, QSizePolicy
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty, QRect, QSize, QTimer, QPoint, QObject, pyqtSignal, QParallelAnimationGroup, QPointF
from PyQt6.QtGui import QColor, QPalette, QPainter, QBrush, QPen
from desktop_app.services.sound_manager import SoundManager

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
        self._paint_offset = QPointF(0, 0) # For magnetic effect

        # Loading State
        self._is_loading = False
        self._spinner_angle = 0
        self._spinner_timer = QTimer(self)
        self._spinner_timer.setInterval(16)
        self._spinner_timer.timeout.connect(self._update_spinner)
        self._original_text = text

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

    def set_loading(self, loading: bool):
        self._is_loading = loading
        self.setEnabled(not loading)
        if loading:
            self._spinner_timer.start()
            self._original_text = self.text()
            self.setText("") # Clear text to draw spinner
        else:
            self._spinner_timer.stop()
            self.setText(self._original_text)
        self.update()

    def _update_spinner(self):
        self._spinner_angle = (self._spinner_angle + 10) % 360
        self.update()

    def enterEvent(self, event):
        SoundManager.instance().play_sound('hover')
        if not self._is_loading:
            self._color_anim.stop()
            self._color_anim.setEndValue(self.hover_bg)
            self._color_anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self._is_loading:
            self._color_anim.stop()
            self._color_anim.setEndValue(self.default_bg)
            self._color_anim.start()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        SoundManager.instance().play_sound('click')
        if not self._is_loading:
            self._start_ripple(event.pos())
            self._bg_color = self.pressed_bg
            self.update()
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if not self._is_loading:
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
        if not painter.isActive():
            return

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.translate(self._paint_offset)

        # Draw Background
        bg_color = self._bg_color
        if not self.isEnabled() and not self._is_loading:
            bg_color = QColor("#E5E7EB") # Disabled gray

        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), self._border_radius, self._border_radius)

        # Draw Ripple
        if self._ripple_opacity > 0:
            painter.setBrush(QBrush(QColor(255, 255, 255, int(255 * self._ripple_opacity))))
            painter.drawEllipse(self._ripple_center, self._ripple_radius, self._ripple_radius)

        # Draw Content
        if self._is_loading:
            # Draw Spinner
            center = self.rect().center()
            radius = min(self.width(), self.height()) / 4
            painter.setPen(QPen(QColor("white"), 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawArc(int(center.x() - radius), int(center.y() - radius), int(radius * 2), int(radius * 2), -self._spinner_angle * 16, 270 * 16)
        else:
            # Draw Text
            painter.setPen(self._text_color if self.isEnabled() else QColor("#9CA3AF"))
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
        super().paintEvent(event)
        painter = QPainter(self)
        if not painter.isActive():
            return

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pen = QPen(self._border_color)
        pen.setWidthF(self._border_width)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

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
        self.timer.timeout.connect(self._update_animation)
        self.timer.setInterval(16)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False) # Block mouse

        # Layout for Label and Progress Bar
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.setSpacing(10)

        # Spacer for Spinner (Visual reserve)
        # Spinner is ~50x50, drawn in paintEvent at center
        # We add top stretch, then a fixed spacer, then widgets, then bottom stretch
        self.layout.addStretch()
        self.layout.addSpacing(60) # Space for spinner

        self.label = QLabel("Caricamento...")
        self.label.setStyleSheet("color: white; font-size: 16px; font-weight: 600;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.hide()
        self.layout.addWidget(self.label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(300)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid white;
                border-radius: 5px;
                text-align: center;
                color: white;
                background-color: transparent;
            }
            QProgressBar::chunk {
                background-color: #3B82F6;
                width: 20px;
            }
        """)
        self.progress_bar.hide()
        self.layout.addWidget(self.progress_bar, alignment=Qt.AlignmentFlag.AlignCenter)

        self.layout.addStretch()

    def start(self):
        if self.parent():
            self.resize(self.parent().size())
        self.show()
        self.raise_()
        self.timer.start()

    def stop(self):
        self.timer.stop()
        self.hide()

    def show_spinner(self):
        self.label.hide()
        self.progress_bar.hide()
        self.start()

    def set_text(self, text):
        self.label.setText(text)
        self.label.show()
        self.start()

    def show_progress(self, value, total=None, message=None):
        if message:
            self.label.setText(message)
            self.label.show()

        if total is not None:
            self.progress_bar.setMaximum(total)

        self.progress_bar.setValue(value)
        self.progress_bar.show()
        self.start()

    def _update_animation(self):
        self.angle = (self.angle + 10) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        if not painter.isActive():
            return

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Semi-transparent background
        painter.setBrush(QBrush(QColor(0, 0, 0, 150)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())

        # Draw Spinner
        center = self.rect().center()
        # Offset spinner slightly up because we have label/bar below
        # No, keep it center, and layout moves label/bar below it.
        # But wait, layout centers its content. The layout has:
        # Stretch, Spacing(60), Label, Bar, Stretch.
        # So Spacing(60) is where spinner should be? No, Spacing(60) is empty space.
        # The center of the widget is roughly in the middle of that Spacing if layout is balanced.
        # Actually, let's just draw it at center.

        # Calculate visual center offset if needed, but absolute center is fine.
        radius = 25
        # Move up by 20px to make room for text below?
        spinner_center = QPoint(center.x(), center.y() - 20)

        # Adjust layout spacing to match this visual

        painter.setPen(QPen(QColor("#3B82F6"), 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawArc(spinner_center.x() - radius, spinner_center.y() - radius, radius * 2, radius * 2, -self.angle * 16, 270 * 16)

class MagneticButton(AnimatedButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setMouseTracking(True)
        self._target_offset = QPointF(0, 0)
        self._current_offset = QPointF(0, 0)

        self._magnet_timer = QTimer(self)
        self._magnet_timer.setInterval(16)
        self._magnet_timer.timeout.connect(self._update_magnet)
        self._magnet_timer.start()

    def mouseMoveEvent(self, event):
        # Calculate attraction
        center = QPointF(self.width()/2, self.height()/2)
        pos = QPointF(event.pos())

        # Attraction factor
        dist_x = pos.x() - center.x()
        dist_y = pos.y() - center.y()

        self._target_offset = QPointF(dist_x * 0.3, dist_y * 0.3)
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self._target_offset = QPointF(0, 0)
        super().leaveEvent(event)

    def _update_magnet(self):
        # Smooth spring physics
        diff = self._target_offset - self._current_offset
        if diff.manhattanLength() > 0.1:
            self._current_offset += diff * 0.15
            self._paint_offset = self._current_offset
            self.update()
