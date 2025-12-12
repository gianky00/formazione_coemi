# Desktop App Core Module
"""
Core module per desktop_app.

CRASH ZERO:
- FASE 1: Widget Lifecycle Protection (widget_guard)
- FASE 2: Animation Management (animation_manager)
- FASE 3: Signal/Slot Hardening (signal_guard)
- FASE 4: Error Boundaries & Self-Healing (error_boundary)
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

from .signal_guard import (
    SafeSignalEmitter,
    ConnectionTracker,
    SafeWorkerMixin,
    safe_emit,
    disconnect_all_from_object,
)

from .error_boundary import (
    ErrorBoundary,
    ErrorContext,
    ViewError,
    RecoverableError,
    TransientError,
    FatalViewError,
    StateCorruptionError,
    ErrorSeverity,
    error_boundary,
    suppress_errors,
    UIStateRecovery,
)

__all__ = [
    # FASE 1: Widget Guard
    'is_widget_alive',
    'is_qobject_alive',
    'guard_widget_access',
    'guard_widget_access_with_fallback',
    'WidgetRef',
    'safe_widget_context',
    'WidgetGuardian',
    # FASE 2: Animation Manager
    'animation_manager',
    'AnimationManager',
    'fade_in',
    'fade_out',
    'slide_in',
    'slide_out',
    'animate_property',
    'shake_widget',
    'animate_geometry',
    # FASE 3: Signal Guard
    'SafeSignalEmitter',
    'ConnectionTracker',
    'SafeWorkerMixin',
    'safe_emit',
    'disconnect_all_from_object',
    # FASE 4: Error Boundary
    'ErrorBoundary',
    'ErrorContext',
    'ViewError',
    'RecoverableError',
    'TransientError',
    'FatalViewError',
    'StateCorruptionError',
    'ErrorSeverity',
    'error_boundary',
    'suppress_errors',
    'UIStateRecovery',
]