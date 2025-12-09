"""
Thread Manager for safe QThread lifecycle management.
Prevents "QThread: Destroyed while thread is still running" errors.
"""

import logging
import sentry_sdk
from PyQt6.QtCore import QThread, QObject, pyqtSignal
from typing import Optional, Callable, Any
import threading
import functools

logger = logging.getLogger(__name__)


def thread_safe_exception_handler(func):
    """Decorator to catch and report exceptions in thread methods."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Exception in thread {func.__name__}: {e}", exc_info=True)
            if sentry_sdk.is_initialized():
                sentry_sdk.capture_exception(e)
            raise
    return wrapper


class SafeThread(QThread):
    """
    A QThread subclass with proper lifecycle management to prevent crashes.
    - Automatically captures exceptions to Sentry
    - Waits for completion before destruction
    - Provides safe cleanup methods
    """
    
    error_occurred = pyqtSignal(Exception)
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._is_stopping = False
        self._run_func: Optional[Callable] = None
        
    def set_run_function(self, func: Callable):
        """Set the function to run in the thread."""
        self._run_func = func
    
    def request_stop(self):
        """Request the thread to stop gracefully."""
        self._is_stopping = True
        
    def is_stopping(self) -> bool:
        """Check if stop has been requested."""
        return self._is_stopping
    
    def run(self):
        """Execute the thread's work with exception handling."""
        try:
            if self._run_func:
                self._run_func()
        except Exception as e:
            logger.error(f"Exception in SafeThread: {e}", exc_info=True)
            if sentry_sdk.is_initialized():
                sentry_sdk.capture_exception(e)
            try:
                self.error_occurred.emit(e)
            except RuntimeError:
                pass  # Widget might have been destroyed
    
    def safe_stop(self, timeout_ms: int = 3000) -> bool:
        """
        Safely stop the thread and wait for it to finish.
        Returns True if thread stopped successfully.
        """
        self._is_stopping = True
        
        if not self.isRunning():
            return True
            
        self.quit()
        finished = self.wait(timeout_ms)
        
        if not finished:
            logger.warning(f"Thread did not finish within {timeout_ms}ms, terminating...")
            self.terminate()
            self.wait(1000)  # Brief wait after terminate
            
        return finished


class ThreadManager:
    """
    Singleton manager for tracking and cleaning up all application threads.
    Call cleanup_all() before application exit.
    """
    
    _instance: Optional['ThreadManager'] = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._threads = []
        return cls._instance
    
    def register_thread(self, thread: QThread):
        """Register a thread for lifecycle tracking."""
        with self._lock:
            # Clean up finished threads
            self._threads = [t for t in self._threads if t.isRunning()]
            self._threads.append(thread)
    
    def cleanup_all(self, timeout_per_thread_ms: int = 2000):
        """
        Stop and wait for all registered threads.
        Call this before application exit.
        """
        with self._lock:
            threads_to_cleanup = list(self._threads)
        
        for thread in threads_to_cleanup:
            try:
                if thread.isRunning():
                    logger.debug(f"Cleaning up thread: {thread}")
                    if hasattr(thread, 'safe_stop'):
                        thread.safe_stop(timeout_per_thread_ms)
                    else:
                        thread.quit()
                        if not thread.wait(timeout_per_thread_ms):
                            thread.terminate()
            except RuntimeError:
                pass  # Thread already deleted
            except Exception as e:
                logger.error(f"Error cleaning up thread: {e}")
        
        with self._lock:
            self._threads.clear()


# Global instance
thread_manager = ThreadManager()


def install_thread_exception_hook():
    """
    Install a global exception hook for threads to capture to Sentry.
    Call this once at application startup.
    """
    original_init = threading.Thread.__init__
    
    def patched_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        original_run = self.run
        
        def patched_run():
            try:
                original_run()
            except Exception as e:
                logger.error(f"Unhandled exception in thread: {e}", exc_info=True)
                if sentry_sdk.is_initialized():
                    sentry_sdk.capture_exception(e)
                raise
        
        self.run = patched_run
    
    threading.Thread.__init__ = patched_init
