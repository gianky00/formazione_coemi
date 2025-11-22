from PyQt6.QtWidgets import QStackedWidget, QLabel, QWidget, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QPoint
from PyQt6.QtGui import QPixmap, QPainter

class AnimatedStackedWidget(QStackedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.animation_duration = 300
        self.animation_type = "fade" # or "slide"

    def slide_in(self, index):
        if index == self.currentIndex():
            return

        current_widget = self.currentWidget()
        next_widget = self.widget(index)

        if not current_widget:
            self.setCurrentIndex(index)
            return

        # Ensure next widget has correct geometry
        next_widget.setGeometry(0, 0, self.width(), self.height())

        # Slide Animation
        offset = self.width()
        next_widget.move(offset, 0)
        self.setCurrentIndex(index) # Shows it
        next_widget.show()
        next_widget.raise_()

        # We need to keep the old widget visible during animation?
        # QStackedWidget hides the old one immediately when setCurrentIndex is called.
        # So we must use the "Screenshot Overlay" trick for the OLD widget,
        # and animate the NEW widget sliding in.

        # 1. Screenshot Old Widget
        pixmap = QPixmap(current_widget.size())
        current_widget.render(pixmap)

        overlay = QLabel(self)
        overlay.setPixmap(pixmap)
        overlay.setGeometry(current_widget.geometry())
        overlay.show()

        # 2. Setup New Widget (starts off-screen right)
        next_widget.move(offset, 0)

        # 3. Animate
        self.anim_group = QParallelAnimationGroup(self)

        anim_new = QPropertyAnimation(next_widget, b"pos")
        anim_new.setDuration(self.animation_duration)
        anim_new.setStartValue(QPoint(offset, 0))
        anim_new.setEndValue(QPoint(0, 0))
        anim_new.setEasingCurve(QEasingCurve.Type.OutQuad)

        anim_overlay = QPropertyAnimation(overlay, b"pos")
        anim_overlay.setDuration(self.animation_duration)
        anim_overlay.setStartValue(QPoint(0, 0))
        anim_overlay.setEndValue(QPoint(-offset, 0)) # Slide out to left
        anim_overlay.setEasingCurve(QEasingCurve.Type.OutQuad)

        self.anim_group.addAnimation(anim_new)
        self.anim_group.addAnimation(anim_overlay)

        def on_finished():
            overlay.hide()
            overlay.deleteLater()
            next_widget.move(0, 0) # Ensure exact placement

        self.anim_group.finished.connect(on_finished)
        self.anim_group.start()

    def fade_in(self, index):
        if index == self.currentIndex():
            return

        current_widget = self.currentWidget()
        next_widget = self.widget(index)

        if not current_widget:
            self.setCurrentIndex(index)
            return

        # Screenshot Old Widget
        pixmap = QPixmap(current_widget.size())
        current_widget.render(pixmap)

        overlay = QLabel(self)
        overlay.setPixmap(pixmap)
        overlay.setGeometry(current_widget.geometry())
        overlay.show()

        # Prepare New Widget
        self.setCurrentIndex(index)
        next_widget.setGeometry(self.rect())

        # Opacity Effect for Overlay (fade out old)
        effect = QGraphicsOpacityEffect(overlay)
        overlay.setGraphicsEffect(effect)

        self.anim = QPropertyAnimation(effect, b"opacity")
        self.anim.setDuration(self.animation_duration)
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.0)
        self.anim.setEasingCurve(QEasingCurve.Type.OutQuad)

        def on_finished():
            overlay.hide()
            overlay.deleteLater()

        self.anim.finished.connect(on_finished)
        self.anim.start()
