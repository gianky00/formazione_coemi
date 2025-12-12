# Desktop App Core Module
"""
Core module per desktop_app.
Contiene componenti fondamentali per widget lifecycle protection.
Contiene componenti fondamentali per widget lifecycle protection e animation management.
"""

from .widget_guard import (
    is_widget_alive,
    safe_widget_context,
    WidgetGuardian,
)

from .animation_manager import (
    animation_manager,
    AnimationManager,
    fade_in,
    fade_out,
    slide_in,
    slide_out,
    animate_property,
    shake_widget,
    animate_geometry,
)

__all__ = [
    'is_widget_alive',
    'is_qobject_alive',
    'guard_widget_access',
    'guard_widget_access_with_fallback',
    'WidgetRef',
    'safe_widget_context',
    'WidgetGuardian',
    'animation_manager',
    'AnimationManager',
    'fade_in',
    'fade_out',
    'slide_in',
    'slide_out',
    'animate_property',
    'shake_widget',
    'animate_geometry',
]