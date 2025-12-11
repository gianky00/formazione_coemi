# Desktop App Core Module
"""
Core module per desktop_app.
Contiene componenti fondamentali per widget lifecycle protection.
"""

from .widget_guard import (
    is_widget_alive,
    is_qobject_alive,
    guard_widget_access,
    guard_widget_access_with_fallback,
    WidgetRef,
    safe_widget_context,
    WidgetGuardian,
)

__all__ = [
    'is_widget_alive',
    'is_qobject_alive',
    'guard_widget_access',
    'guard_widget_access_with_fallback',
    'WidgetRef',
    'safe_widget_context',
    'WidgetGuardian',
]
