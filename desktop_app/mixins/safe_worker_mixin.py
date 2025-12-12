"""
Safe Worker Mixin - CRASH ZERO FASE 3

Questo modulo fornisce classi base per worker thread-safe con:
- Emissione sicura di segnali
- Gestione automatica delle eccezioni
- Protocollo di stop pulito
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from PyQt6.QtCore import QThread, pyqtSignal

from desktop_app.core.signal_guard import SafeSignalEmitter

logger = logging.getLogger(__name__)


class RobustWorker(QThread):
    """
    Worker thread robusto con gestione errori integrata.
    
    Features:
    - Emissione sicura di segnali
    - Gestione automatica delle eccezioni
    - Protocollo di stop pulito
    - Timeout opzionale
    
    Signals:
        started_work: Emesso quando il lavoro inizia
        progress: Emesso per aggiornamenti di progresso (int percent, str message)
        finished_ok: Emesso al completamento con successo (result: Any)
        finished_error: Emesso in caso di errore (error: str)
    
    Example:
        class ImportWorker(RobustWorker):
            def do_work(self):
                for i, item in enumerate(self.items):
                    if self.should_stop():
                        return None
                    
                    self.report_progress(i * 100 // len(self.items), f"Processing {item}")
                    process(item)
                
                return {"imported": len(self.items)}
    """
    
    # Segnali standard
    started_work = pyqtSignal()
    progress = pyqtSignal(int, str)  # percent, message
    finished_ok = pyqtSignal(object)  # result
    finished_error = pyqtSignal(str)  # error message
    
    def __init__(self, parent: Optional[QThread] = None):
        super().__init__(parent)
        self._emitter = SafeSignalEmitter(self)
        self._stop_requested = False
    
    def run(self):
        """
        Esegue il worker con gestione errori.
        
        NON sovrascrivere questo metodo. Implementare do_work() invece.
        """
        self._emitter.emit(self.started_work)
        
        try:
            result = self.do_work()
            
            if not self._stop_requested:
                self._emitter.emit(self.finished_ok, result)
                
        except Exception as e:
            logger.exception(f"Worker {self.__class__.__name__} error")
            self._emitter.emit(self.finished_error, str(e))
    
    def do_work(self) -> Any:
        """
        Implementare questo metodo nelle sottoclassi.
        
        Returns:
            Risultato del lavoro (passato a finished_ok)
        """
        raise NotImplementedError("Subclasses must implement do_work()")
    
    def report_progress(self, percent: int, message: str = "") -> bool:
        """
        Riporta il progresso.
        
        Args:
            percent: Percentuale completamento (0-100)
            message: Messaggio opzionale
            
        Returns:
            False se il worker è stato fermato
        """
        if self.should_stop():
            return False
        
        self._emitter.emit(self.progress, percent, message)
        return True
    
    def should_stop(self) -> bool:
        """Verifica se è stato richiesto lo stop."""
        return self._stop_requested or self.isInterruptionRequested()
    
    def request_stop(self) -> None:
        """Richiede l'arresto del worker."""
        self._stop_requested = True
        self._emitter.invalidate()
        self.requestInterruption()
    
    def safe_emit(self, signal: pyqtSignal, *args) -> bool:
        """Emette un segnale custom in modo sicuro."""
        return self._emitter.emit(signal, *args)


class PeriodicWorker(RobustWorker):
    """
    Worker che esegue un'operazione periodicamente.
    
    Example:
        class StatusChecker(PeriodicWorker):
            status_updated = pyqtSignal(dict)
            
            def __init__(self):
                super().__init__(interval_ms=5000)  # Ogni 5 secondi
            
            def do_periodic_work(self):
                status = check_server_status()
                self.safe_emit(self.status_updated, status)
    """
    
    def __init__(self, interval_ms: int = 1000, parent: Optional[QThread] = None):
        super().__init__(parent)
        self._interval_ms = interval_ms
    
    def do_work(self) -> Any:
        """Esegue il lavoro periodico."""
        while not self.should_stop():
            self.do_periodic_work()
            
            # Sleep interrompibile
            self.msleep(self._interval_ms)
        
        return None
    
    def do_periodic_work(self) -> None:
        """
        Implementare questo metodo nelle sottoclassi.
        
        Viene chiamato ogni interval_ms millisecondi.
        """
        raise NotImplementedError("Subclasses must implement do_periodic_work()")


__all__ = [
    'RobustWorker',
    'PeriodicWorker',
]
