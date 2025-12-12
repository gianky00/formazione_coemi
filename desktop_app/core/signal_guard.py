"""
Signal Guard - Gestione sicura di signal/slot PyQt6.

CRASH ZERO FASE 3 - Signal/Slot Hardening

Questo modulo fornisce utility per:
- Emissione sicura di segnali (previene crash su oggetti distrutti)
- Tracking delle connessioni per cleanup automatico
- Pattern per worker thread-safe

Uso tipico:
    # In un worker
    class MyWorker(QThread):
        progress = pyqtSignal(int)
        
        def __init__(self):
            super().__init__()
            self._emitter = SafeSignalEmitter(self)
        
        def run(self):
            for i in range(100):
                if not self._emitter.emit(self.progress, i):
                    break  # Owner distrutto, fermati
    
    # In una view
    class MyView(QWidget):
        def __init__(self):
            self._connections = ConnectionTracker()
        
        def _connect_worker(self):
            self._connections.connect(self.worker.progress, self.on_progress)
        
        def closeEvent(self, event):
            self._connections.disconnect_all()
"""

from __future__ import annotations

import logging
import weakref
from typing import Any, Callable, Optional, List
from dataclasses import dataclass

from PyQt6.QtCore import QObject, pyqtSignal, QMutex, QMutexLocker, Qt

logger = logging.getLogger(__name__)


class SafeSignalEmitter:
    """
    Wrapper per emissione sicura di segnali.
    
    Previene crash quando si tenta di emettere un segnale
    dopo che l'oggetto proprietario è stato distrutto.
    
    Thread-safe tramite QMutex.
    
    Example:
        class MyWorker(QThread):
            finished_signal = pyqtSignal(dict)
            error_signal = pyqtSignal(str)
            
            def __init__(self):
                super().__init__()
                self._emitter = SafeSignalEmitter(self)
            
            def run(self):
                try:
                    result = self._do_work()
                    self._emitter.emit(self.finished_signal, result)
                except Exception as e:
                    self._emitter.emit(self.error_signal, str(e))
            
            def stop(self):
                self._emitter.invalidate()
                self.requestInterruption()
    """
    
    def __init__(self, owner: QObject):
        """
        Args:
            owner: L'oggetto QObject che possiede i segnali
        """
        self._owner_ref = weakref.ref(owner) if owner else None
        self._is_valid = True
        self._mutex = QMutex()
        self._emit_count = 0
        self._failed_count = 0
    
    def emit(self, signal: pyqtSignal, *args: Any) -> bool:
        """
        Emette un segnale in modo sicuro.
        
        Args:
            signal: Il segnale PyQt da emettere
            *args: Argomenti del segnale
            
        Returns:
            True se emesso con successo, False se owner distrutto o invalidato
        """
        with QMutexLocker(self._mutex):
            if not self._is_valid:
                self._failed_count += 1
                return False
            
            if self._owner_ref is None:
                self._is_valid = False
                self._failed_count += 1
                return False
            
            owner = self._owner_ref()
            if owner is None:
                self._is_valid = False
                self._failed_count += 1
                return False
            
            try:
                signal.emit(*args)
                self._emit_count += 1
                return True
            except RuntimeError as e:
                # "wrapped C/C++ object has been deleted"
                logger.debug(f"Signal emit failed (owner destroyed): {e}")
                self._is_valid = False
                self._failed_count += 1
                return False
    
    def emit_if_valid(self, signal: pyqtSignal, *args: Any) -> bool:
        """Alias per emit() - più esplicito nel nome."""
        return self.emit(signal, *args)
    
    def invalidate(self) -> None:
        """
        Invalida l'emitter, impedendo future emissioni.
        
        Chiamare questo metodo quando si vuole fermare il worker
        o prima della distruzione dell'owner.
        """
        with QMutexLocker(self._mutex):
            self._is_valid = False
            logger.debug(f"SafeSignalEmitter invalidato (emits: {self._emit_count}, failed: {self._failed_count})")
    
    def is_valid(self) -> bool:
        """Verifica se l'emitter è ancora valido."""
        with QMutexLocker(self._mutex):
            return self._is_valid
    
    @property
    def stats(self) -> dict:
        """Ritorna statistiche sull'emitter."""
        with QMutexLocker(self._mutex):
            return {
                'emit_count': self._emit_count,
                'failed_count': self._failed_count,
                'is_valid': self._is_valid
            }


@dataclass
class TrackedConnection:
    """Rappresenta una connessione tracciata."""
    signal: pyqtSignal
    slot: Callable
    connection_type: Qt.ConnectionType
    description: str = ""


class ConnectionTracker:
    """
    Traccia connessioni signal/slot per cleanup automatico.
    
    Risolve il problema delle connessioni "orfane" che possono
    causare crash o memory leak quando la view viene distrutta.
    
    Example:
        class MyView(QWidget):
            def __init__(self):
                super().__init__()
                self._tracker = ConnectionTracker()
            
            def _setup_connections(self):
                self._tracker.connect(
                    self.worker.finished, 
                    self._on_finished,
                    description="Worker completion"
                )
                self._tracker.connect(
                    self.worker.error,
                    self._on_error
                )
            
            def closeEvent(self, event):
                disconnected = self._tracker.disconnect_all()
                logger.info(f"Disconnected {disconnected} signals")
                super().closeEvent(event)
    """
    
    def __init__(self):
        self._connections: List[TrackedConnection] = []
        self._mutex = QMutex()
    
    def connect(
        self,
        signal: pyqtSignal,
        slot: Callable,
        connection_type: Qt.ConnectionType = Qt.ConnectionType.AutoConnection,
        description: str = ""
    ) -> bool:
        """
        Connette un segnale a uno slot e traccia la connessione.
        
        Args:
            signal: Segnale PyQt
            slot: Funzione/metodo da connettere
            connection_type: Tipo di connessione Qt
            description: Descrizione opzionale per debug
            
        Returns:
            True se connesso con successo
        """
        try:
            signal.connect(slot, connection_type)
            
            with QMutexLocker(self._mutex):
                self._connections.append(TrackedConnection(
                    signal=signal,
                    slot=slot,
                    connection_type=connection_type,
                    description=description
                ))
            
            logger.debug(f"Connection tracked: {description or 'unnamed'}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect signal: {e}")
            return False
    
    def disconnect(self, signal: pyqtSignal, slot: Callable) -> bool:
        """
        Disconnette una specifica connessione.
        
        Args:
            signal: Segnale da disconnettere
            slot: Slot da disconnettere
            
        Returns:
            True se disconnesso
        """
        try:
            signal.disconnect(slot)
            
            with QMutexLocker(self._mutex):
                # Usa == per slot (callable equality) e confronto robusto per signal
                self._connections = [
                    c for c in self._connections
                    if not (c.slot == slot or c.slot is slot)
                ]
            
            return True
            
        except (TypeError, RuntimeError) as e:
            # Già disconnesso o oggetto distrutto
            logger.debug(f"Disconnect failed (already disconnected?): {e}")
            return False
    
    def disconnect_all(self) -> int:
        """
        Disconnette tutte le connessioni tracciate.
        
        Returns:
            Numero di connessioni disconnesse con successo
        """
        with QMutexLocker(self._mutex):
            connections = self._connections.copy()
            self._connections.clear()
        
        count = 0
        for conn in connections:
            try:
                conn.signal.disconnect(conn.slot)
                count += 1
                logger.debug(f"Disconnected: {conn.description or 'unnamed'}")
            except (TypeError, RuntimeError):
                # Già disconnesso o oggetto distrutto - va bene
                pass
        
        logger.debug(f"disconnect_all: {count}/{len(connections)} disconnected")
        return count
    
    def connection_count(self) -> int:
        """Ritorna il numero di connessioni attive tracciate."""
        with QMutexLocker(self._mutex):
            return len(self._connections)
    
    def clear(self) -> None:
        """Pulisce la lista senza disconnettere (per cleanup post-distruzione)."""
        with QMutexLocker(self._mutex):
            self._connections.clear()


class SafeWorkerMixin:
    """
    Mixin per worker (QThread/QRunnable) con emissione sicura.
    
    Fornisce:
    - SafeSignalEmitter pre-configurato
    - Metodo stop() standardizzato
    - Cleanup automatico
    
    Example:
        class MyWorker(SafeWorkerMixin, QThread):
            progress = pyqtSignal(int)
            result = pyqtSignal(dict)
            
            def run(self):
                for i in range(100):
                    if self.should_stop():
                        break
                    self.safe_emit(self.progress, i)
                
                self.safe_emit(self.result, {"done": True})
    """
    
    _safe_emitter: SafeSignalEmitter
    _stop_requested: bool = False
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._safe_emitter = SafeSignalEmitter(self)
        self._stop_requested = False
    
    def safe_emit(self, signal: pyqtSignal, *args: Any) -> bool:
        """
        Emette un segnale in modo sicuro.
        
        Returns:
            True se emesso, False se worker fermato o owner distrutto
        """
        if self._stop_requested:
            return False
        return self._safe_emitter.emit(signal, *args)
    
    def should_stop(self) -> bool:
        """
        Verifica se il worker deve fermarsi.
        
        Controlla sia il flag interno che isInterruptionRequested() per QThread.
        """
        if self._stop_requested:
            return True
        
        # Per QThread
        if hasattr(self, 'isInterruptionRequested'):
            return self.isInterruptionRequested()
        
        return False
    
    def request_stop(self) -> None:
        """
        Richiede l'arresto del worker.
        
        Invalida l'emitter e setta il flag di stop.
        """
        self._stop_requested = True
        self._safe_emitter.invalidate()
        
        # Per QThread
        if hasattr(self, 'requestInterruption'):
            self.requestInterruption()
        
        logger.debug(f"Stop requested for {self.__class__.__name__}")


def safe_emit(signal: pyqtSignal, *args: Any) -> bool:
    """
    Funzione helper per emissione sicura one-shot.
    
    Utile quando non si vuole creare un SafeSignalEmitter completo.
    
    Example:
        if not safe_emit(self.update_signal, new_value):
            logger.warning("Emit failed")
    """
    try:
        signal.emit(*args)
        return True
    except RuntimeError as e:
        logger.debug(f"safe_emit failed: {e}")
        return False


def disconnect_all_from_object(obj: QObject) -> int:
    """
    Disconnette TUTTI i segnali da un oggetto.
    
    Utile per cleanup completo prima della distruzione.
    
    Args:
        obj: L'oggetto da cui disconnettere
        
    Returns:
        Numero stimato di disconnessioni (non sempre accurato)
    """
    count = 0
    try:
        # Disconnetti tutti i segnali dell'oggetto
        obj.disconnect()
        count = 1  # Non possiamo sapere il numero esatto
    except (TypeError, RuntimeError):
        pass
    
    return count


__all__ = [
    'SafeSignalEmitter',
    'ConnectionTracker',
    'TrackedConnection',
    'SafeWorkerMixin',
    'safe_emit',
    'disconnect_all_from_object',
]
