# AnimationManager - CRASH ZERO FASE 2
from __future__ import annotations
import logging, uuid, weakref
from dataclasses import dataclass, field
from typing import Optional, Callable, Any, Dict, Literal
from PyQt6.QtCore import QObject, QTimer, QMutex, QMutexLocker, QPoint, QRect, QEasingCurve, QAbstractAnimation, QPropertyAnimation
from PyQt6.QtWidgets import QWidget, QGraphicsOpacityEffect
from desktop_app.core.widget_guard import is_widget_alive, is_qobject_alive

logger = logging.getLogger(__name__)

@dataclass
class _AnimationEntry:
    animation_id: str
    animation_ref: weakref.ref
    owner_ref: weakref.ref
    name: str = ""
    timeout_ms: int = 5000
    on_timeout: Optional[Callable] = None
    timeout_timer: Optional[QTimer] = field(default=None, repr=False)
    def get_animation(self): 
        a = self.animation_ref()
        return a if a and is_qobject_alive(a) else None
    def get_owner(self): 
        o = self.owner_ref()
        return o if o and is_qobject_alive(o) else None
    def is_valid(self): return self.get_animation() is not None and self.get_owner() is not None

class AnimationManager(QObject):
    _instance = None
    _initialized = False
    def __new__(cls):
        if cls._instance is None: cls._instance = super().__new__(cls)
        return cls._instance
    def __init__(self):
        if AnimationManager._initialized: return
        super().__init__()
        self._mutex = QMutex()
        self._animations = {}
        self._owner_map = {}
        self._cleanup_timer = QTimer(self)
        self._cleanup_timer.setInterval(5000)
        self._cleanup_timer.timeout.connect(self._periodic_cleanup)
        self._cleanup_timer.start()
        AnimationManager._initialized = True
    @classmethod
    def instance(cls):
        if cls._instance is None: cls._instance = cls()
        return cls._instance
    def register(self, animation, owner, name="", timeout_ms=5000, on_timeout=None):
        if not is_qobject_alive(animation) or not is_qobject_alive(owner): return ""
        aid = str(uuid.uuid4())[:8]
        oid = id(owner)
        entry = _AnimationEntry(aid, weakref.ref(animation), weakref.ref(owner), name, timeout_ms, on_timeout)
        if timeout_ms > 0:
            t = QTimer()
            t.setSingleShot(True)
            t.setInterval(timeout_ms)
            t.timeout.connect(lambda: self._on_animation_timeout(aid))
            entry.timeout_timer = t
            t.start()
        try: animation.finished.connect(lambda: self._on_animation_finished(aid))
        except: pass
        try: owner.destroyed.connect(lambda: self._on_owner_destroyed(oid))
        except: pass
        with QMutexLocker(self._mutex):
            self._animations[aid] = entry
            if oid not in self._owner_map: self._owner_map[oid] = set()
            self._owner_map[oid].add(aid)
        return aid
    def cancel_by_id(self, aid):
        with QMutexLocker(self._mutex):
            e = self._animations.get(aid)
            return self._cancel_entry_locked(e) if e else False
    def cancel_all(self, owner):
        oid = id(owner)
        c = 0
        with QMutexLocker(self._mutex):
            for aid in self._owner_map.get(oid, set()).copy():
                e = self._animations.get(aid)
                if e and self._cancel_entry_locked(e): c += 1
        return c
    def _cancel_entry_locked(self, e):
        try:
            if e.timeout_timer:
                try: e.timeout_timer.stop(); e.timeout_timer.deleteLater()
                except: pass
            a = e.get_animation()
            if a:
                try: a.stop()
                except: pass
            self._animations.pop(e.animation_id, None)
            o = e.get_owner()
            if o:
                oid = id(o)
                if oid in self._owner_map:
                    self._owner_map[oid].discard(e.animation_id)
                    if not self._owner_map[oid]: del self._owner_map[oid]
            return True
        except: return False
    def is_animating(self, owner):
        with QMutexLocker(self._mutex):
            for aid in self._owner_map.get(id(owner), set()):
                e = self._animations.get(aid)
                if e:
                    a = e.get_animation()
                    if a and a.state() == QAbstractAnimation.State.Running: return True
        return False
    def get_active_count(self, owner=None):
        with QMutexLocker(self._mutex):
            return len(self._owner_map.get(id(owner), set())) if owner else len(self._animations)
    def _on_animation_finished(self, aid):
        with QMutexLocker(self._mutex):
            e = self._animations.get(aid)
            if e:
                if e.timeout_timer:
                    try: e.timeout_timer.stop()
                    except: pass
                self._cancel_entry_locked(e)
    def _on_animation_timeout(self, aid):
        with QMutexLocker(self._mutex):
            e = self._animations.get(aid)
            if not e: return
            if e.on_timeout:
                try: e.on_timeout()
                except: pass
            self._cancel_entry_locked(e)
    def _on_owner_destroyed(self, oid):
        with QMutexLocker(self._mutex):
            for aid in self._owner_map.get(oid, set()).copy():
                e = self._animations.get(aid)
                if e: self._cancel_entry_locked(e)
            self._owner_map.pop(oid, None)
    def _periodic_cleanup(self):
        with QMutexLocker(self._mutex):
            dead = [aid for aid, e in self._animations.items() if not e.is_valid()]
            for aid in dead:
                e = self._animations.get(aid)
                if e: self._cancel_entry_locked(e)
    def wait_completion(self, owner, timeout_ms=5000):
        from PyQt6.QtCore import QEventLoop
        t = 0
        while self.is_animating(owner):
            loop = QEventLoop()
            QTimer.singleShot(50, loop.quit)
            loop.exec()
            t += 50
            if t >= timeout_ms: return False
        return True

def fade_out(widget, duration_ms=300, on_finished=None, easing=QEasingCurve.Type.OutCubic):
    if not is_widget_alive(widget):
        if on_finished: on_finished()
        return ""
    effect = widget.graphicsEffect()
    if not isinstance(effect, QGraphicsOpacityEffect):
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
    anim = QPropertyAnimation(effect, b"opacity", widget)
    anim.setDuration(duration_ms)
    anim.setStartValue(effect.opacity() if effect.opacity() > 0 else 1.0)
    anim.setEndValue(0.0)
    anim.setEasingCurve(easing)
    if on_finished: anim.finished.connect(on_finished)
    aid = animation_manager.register(anim, widget, "fade_out", duration_ms + 1000)
    anim.start()
    return aid

def fade_in(widget, duration_ms=300, on_finished=None, easing=QEasingCurve.Type.OutCubic):
    if not is_widget_alive(widget):
        if on_finished: on_finished()
        return ""
    effect = widget.graphicsEffect()
    if not isinstance(effect, QGraphicsOpacityEffect):
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        effect.setOpacity(0.0)
    widget.show()
    anim = QPropertyAnimation(effect, b"opacity", widget)
    anim.setDuration(duration_ms)
    anim.setStartValue(effect.opacity())
    anim.setEndValue(1.0)
    anim.setEasingCurve(easing)
    if on_finished: anim.finished.connect(on_finished)
    aid = animation_manager.register(anim, widget, "fade_in", duration_ms + 1000)
    anim.start()
    return aid

def slide_out(widget, direction='left', duration_ms=300, on_finished=None, easing=QEasingCurve.Type.OutCubic):
    if not is_widget_alive(widget):
        if on_finished: on_finished()
        return ""
    sp = widget.pos()
    ep = QPoint(sp)
    parent = widget.parent()
    ps = parent.size() if parent and is_widget_alive(parent) else widget.size()
    if direction == 'left': ep.setX(-widget.width())
    elif direction == 'right': ep.setX(ps.width())
    elif direction == 'up': ep.setY(-widget.height())
    elif direction == 'down': ep.setY(ps.height())
    anim = QPropertyAnimation(widget, b"pos", widget)
    anim.setDuration(duration_ms)
    anim.setStartValue(sp)
    anim.setEndValue(ep)
    anim.setEasingCurve(easing)
    if on_finished: anim.finished.connect(on_finished)
    aid = animation_manager.register(anim, widget, f"slide_out_{direction}", duration_ms + 1000)
    anim.start()
    return aid

def slide_in(widget, direction='right', duration_ms=300, target_pos=None, on_finished=None, easing=QEasingCurve.Type.OutCubic):
    if not is_widget_alive(widget):
        if on_finished: on_finished()
        return ""
    ep = target_pos if target_pos else widget.pos()
    sp = QPoint(ep)
    parent = widget.parent()
    ps = parent.size() if parent and is_widget_alive(parent) else widget.size()
    if direction == 'left': sp.setX(-widget.width())
    elif direction == 'right': sp.setX(ps.width())
    elif direction == 'up': sp.setY(-widget.height())
    elif direction == 'down': sp.setY(ps.height())
    widget.move(sp)
    widget.show()
    anim = QPropertyAnimation(widget, b"pos", widget)
    anim.setDuration(duration_ms)
    anim.setStartValue(sp)
    anim.setEndValue(ep)
    anim.setEasingCurve(easing)
    if on_finished: anim.finished.connect(on_finished)
    aid = animation_manager.register(anim, widget, f"slide_in_{direction}", duration_ms + 1000)
    anim.start()
    return aid

def animate_property(target, property_name, start_value, end_value, duration_ms=300, easing=QEasingCurve.Type.OutCubic, on_finished=None, owner=None):
    if not is_qobject_alive(target):
        if on_finished: on_finished()
        return ""
    ao = owner if owner else target
    anim = QPropertyAnimation(target, property_name, target)
    anim.setDuration(duration_ms)
    anim.setStartValue(start_value)
    anim.setEndValue(end_value)
    anim.setEasingCurve(easing)
    if on_finished: anim.finished.connect(on_finished)
    pn = property_name.decode() if isinstance(property_name, bytes) else str(property_name)
    aid = animation_manager.register(anim, ao, f"property_{pn}", duration_ms + 1000)
    anim.start()
    return aid

def shake_widget(widget, amplitude=5, duration_ms=300, on_finished=None):
    if not is_widget_alive(widget):
        if on_finished: on_finished()
        return ""
    pos = widget.pos()
    anim = QPropertyAnimation(widget, b"pos", widget)
    anim.setDuration(duration_ms)
    anim.setLoopCount(3)
    anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
    anim.setKeyValueAt(0, pos)
    anim.setKeyValueAt(0.25, pos + QPoint(-amplitude, 0))
    anim.setKeyValueAt(0.75, pos + QPoint(amplitude, 0))
    anim.setKeyValueAt(1, pos)
    if on_finished: anim.finished.connect(on_finished)
    aid = animation_manager.register(anim, widget, "shake", duration_ms * 3 + 1000)
    anim.start()
    return aid

def animate_geometry(widget, target_geometry, duration_ms=300, easing=QEasingCurve.Type.OutCubic, on_finished=None):
    if not is_widget_alive(widget):
        if on_finished: on_finished()
        return ""
    return animate_property(widget, b"geometry", widget.geometry(), target_geometry, duration_ms, easing, on_finished, widget)

animation_manager = AnimationManager.instance()

__all__ = ['AnimationManager', 'animation_manager', 'fade_out', 'fade_in', 'slide_out', 'slide_in', 'animate_property', 'shake_widget', 'animate_geometry']
