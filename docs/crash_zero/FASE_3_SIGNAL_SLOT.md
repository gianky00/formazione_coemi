# 🔌 FASE 3: Signal/Slot Hardening

## Obiettivo
Rendere il sistema di signal/slot PyQt6 robusto contro crash causati da emissioni su oggetti distrutti e connessioni non disconnesse.

---

## 📚 Background Tecnico

### Il Problema
I signal/slot in PyQt6 possono causare crash quando:
1. Un worker emette un segnale dopo che la view ricevente è stata distrutta
2. Le connessioni non vengono disconnesse, causando memory leak
3. Signal emessi da thread secondari accedono a widget nel main thread distrutto

```python
# Esempio problematico
class ImportWorker(QThread):
    progress = pyqtSignal(int)
    
    def run(self):
        for i in range(100):
            time.sleep(0.1)
            self.progress.emit(i)  # CRASH se view chiusa!

class ImportView(QWidget):
    def start_import(self):
        self.worker = ImportWorker()
        self.worker.progress.connect(self.update_progress)
        self.worker.start()
    
    def closeEvent(self, event):
        # Worker continua a emettere, view distrutta → CRASH
        super().closeEvent(event)
```

---

## 🏗️ Architettura della Soluzione

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Signal/Slot Guard System                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │ SafeSignalEmitter│  │ConnectionTracker │  │  Worker Mixin    │  │
│  │                  │  │                  │  │                  │  │
│  │ - emit() safe    │  │ - connect()      │  │ - Auto cleanup   │  │
│  │ - invalidate()   │  │ - disconnect_all │  │ - Safe emit      │  │
│  │ - Thread safe    │  │ - Weak refs      │  │ - Stop protocol  │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📁 File da Creare

### 1. `desktop_app/core/signal_guard.py`

```python
"""
Signal Guard - Gestione sicura di signal/slot PyQt6.

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
from typing import Any, Callable, Optional, List, Tuple
from dataclasses import dataclass, field

from PyQt6.QtCore import QObject, pyqtSignal, QMutex, QMutexLocker, Qt, QThread

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
        self._owner_ref = weakref.ref(owner)
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
                self._connections = [
                    c for c in self._connections
                    if not (c.signal is signal and c.slot is slot)
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
```

---

### 2. `desktop_app/mixins/safe_worker_mixin.py`

```python
"""
Safe Worker Mixin - Estensione del mixin base per casi d'uso comuni.
"""

from __future__ import annotations

import logging
from typing import Any, Optional, Callable
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
```

---

### 3. `tests/desktop_app/core/test_signal_guard.py`

```python
"""
Test per il modulo signal_guard.
"""

import pytest
import time
from unittest.mock import MagicMock
from PyQt6.QtCore import QThread, pyqtSignal, QObject
from PyQt6.QtWidgets import QApplication
import sys


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


class TestSafeSignalEmitter:
    """Test per SafeSignalEmitter."""
    
    def test_emit_success(self, qapp):
        """Emissione su oggetto valido."""
        from desktop_app.core.signal_guard import SafeSignalEmitter
        
        class TestObj(QObject):
            test_signal = pyqtSignal(int)
        
        obj = TestObj()
        emitter = SafeSignalEmitter(obj)
        
        received = []
        obj.test_signal.connect(lambda x: received.append(x))
        
        assert emitter.emit(obj.test_signal, 42) is True
        assert received == [42]
    
    def test_emit_after_invalidate(self, qapp):
        """Emissione dopo invalidazione ritorna False."""
        from desktop_app.core.signal_guard import SafeSignalEmitter
        
        class TestObj(QObject):
            test_signal = pyqtSignal()
        
        obj = TestObj()
        emitter = SafeSignalEmitter(obj)
        
        emitter.invalidate()
        
        assert emitter.emit(obj.test_signal) is False
        assert emitter.is_valid() is False
    
    def test_stats(self, qapp):
        """Verifica statistiche."""
        from desktop_app.core.signal_guard import SafeSignalEmitter
        
        class TestObj(QObject):
            test_signal = pyqtSignal()
        
        obj = TestObj()
        emitter = SafeSignalEmitter(obj)
        
        emitter.emit(obj.test_signal)
        emitter.emit(obj.test_signal)
        emitter.invalidate()
        emitter.emit(obj.test_signal)  # Fallirà
        
        stats = emitter.stats
        assert stats['emit_count'] == 2
        assert stats['failed_count'] == 1


class TestConnectionTracker:
    """Test per ConnectionTracker."""
    
    def test_connect_and_disconnect(self, qapp):
        """Test connessione e disconnessione."""
        from desktop_app.core.signal_guard import ConnectionTracker
        
        class TestObj(QObject):
            test_signal = pyqtSignal(str)
        
        obj = TestObj()
        tracker = ConnectionTracker()
        
        received = []
        slot = lambda x: received.append(x)
        
        tracker.connect(obj.test_signal, slot, description="test connection")
        assert tracker.connection_count() == 1
        
        obj.test_signal.emit("hello")
        assert received == ["hello"]
        
        tracker.disconnect_all()
        assert tracker.connection_count() == 0
        
        obj.test_signal.emit("world")
        assert received == ["hello"]  # Non ricevuto
    
    def test_disconnect_all_multiple(self, qapp):
        """Test disconnessione multipla."""
        from desktop_app.core.signal_guard import ConnectionTracker
        
        class TestObj(QObject):
            sig1 = pyqtSignal()
            sig2 = pyqtSignal()
            sig3 = pyqtSignal()
        
        obj = TestObj()
        tracker = ConnectionTracker()
        
        tracker.connect(obj.sig1, lambda: None)
        tracker.connect(obj.sig2, lambda: None)
        tracker.connect(obj.sig3, lambda: None)
        
        assert tracker.connection_count() == 3
        
        disconnected = tracker.disconnect_all()
        assert disconnected == 3
        assert tracker.connection_count() == 0


class TestSafeWorkerMixin:
    """Test per SafeWorkerMixin."""
    
    def test_safe_emit_in_worker(self, qapp, qtbot):
        """Test emissione sicura in worker."""
        from desktop_app.core.signal_guard import SafeWorkerMixin
        
        class TestWorker(SafeWorkerMixin, QThread):
            done = pyqtSignal(int)
            
            def run(self):
                for i in range(5):
                    if self.should_stop():
                        break
                    self.safe_emit(self.done, i)
                    self.msleep(10)
        
        worker = TestWorker()
        results = []
        worker.done.connect(lambda x: results.append(x))
        
        worker.start()
        qtbot.waitUntil(lambda: not worker.isRunning(), timeout=1000)
        
        assert results == [0, 1, 2, 3, 4]
    
    def test_stop_worker(self, qapp, qtbot):
        """Test stop del worker."""
        from desktop_app.core.signal_guard import SafeWorkerMixin
        
        class InfiniteWorker(SafeWorkerMixin, QThread):
            tick = pyqtSignal()
            
            def run(self):
                while not self.should_stop():
                    self.safe_emit(self.tick)
                    self.msleep(10)
        
        worker = InfiniteWorker()
        ticks = [0]
        worker.tick.connect(lambda: ticks.__setitem__(0, ticks[0] + 1))
        
        worker.start()
        qtbot.wait(100)
        
        worker.request_stop()
        qtbot.waitUntil(lambda: not worker.isRunning(), timeout=1000)
        
        final_ticks = ticks[0]
        qtbot.wait(100)
        
        # Non dovrebbero arrivare altri tick
        assert ticks[0] == final_ticks


class TestRobustWorker:
    """Test per RobustWorker."""
    
    def test_successful_work(self, qapp, qtbot):
        """Test lavoro completato con successo."""
        from desktop_app.mixins.safe_worker_mixin import RobustWorker
        
        class SimpleWorker(RobustWorker):
            def do_work(self):
                return {"result": 42}
        
        worker = SimpleWorker()
        results = []
        worker.finished_ok.connect(lambda r: results.append(r))
        
        worker.start()
        qtbot.waitUntil(lambda: len(results) > 0, timeout=1000)
        
        assert results[0] == {"result": 42}
    
    def test_work_with_error(self, qapp, qtbot):
        """Test lavoro con errore."""
        from desktop_app.mixins.safe_worker_mixin import RobustWorker
        
        class FailingWorker(RobustWorker):
            def do_work(self):
                raise ValueError("Something went wrong")
        
        worker = FailingWorker()
        errors = []
        worker.finished_error.connect(lambda e: errors.append(e))
        
        worker.start()
        qtbot.waitUntil(lambda: len(errors) > 0, timeout=1000)
        
        assert "Something went wrong" in errors[0]
    
    def test_progress_reporting(self, qapp, qtbot):
        """Test reporting progresso."""
        from desktop_app.mixins.safe_worker_mixin import RobustWorker
        
        class ProgressWorker(RobustWorker):
            def do_work(self):
                for i in range(5):
                    self.report_progress(i * 25, f"Step {i}")
                return "done"
        
        worker = ProgressWorker()
        progress_updates = []
        worker.progress.connect(lambda p, m: progress_updates.append((p, m)))
        
        worker.start()
        qtbot.waitUntil(lambda: not worker.isRunning(), timeout=1000)
        
        assert len(progress_updates) == 5
        assert progress_updates[0] == (0, "Step 0")
        assert progress_updates[4] == (100, "Step 4")
```

---

## 📝 Istruzioni di Applicazione ai Worker Esistenti

### Refactoring `desktop_app/workers/chat_worker.py`

```python
# PRIMA
class ChatWorker(QThread):
    response_chunk = pyqtSignal(str)
    finished_signal = pyqtSignal()
    error_signal = pyqtSignal(str)
    
    def run(self):
        try:
            for chunk in self._stream():
                self.response_chunk.emit(chunk)  # Può crashare!
            self.finished_signal.emit()
        except Exception as e:
            self.error_signal.emit(str(e))

# DOPO
from desktop_app.mixins.safe_worker_mixin import RobustWorker

class ChatWorker(RobustWorker):
    response_chunk = pyqtSignal(str)
    
    def do_work(self):
        for chunk in self._stream():
            if self.should_stop():
                return None
            self.safe_emit(self.response_chunk, chunk)
        return {"completed": True}
    
    def _stream(self):
        # ... implementazione esistente ...
        pass
```

### Refactoring View che Usano Worker

```python
# In ogni view che usa worker
from desktop_app.core.signal_guard import ConnectionTracker

class ImportView(SafeWidgetMixin, QWidget):
    def __init__(self):
        super().__init__()
        self._connections = ConnectionTracker()
    
    def _start_import(self):
        self.worker = ImportWorker(self.file_path)
        
        # Usa ConnectionTracker invece di connect diretto
        self._connections.connect(self.worker.progress, self._on_progress)
        self._connections.connect(self.worker.finished_ok, self._on_success)
        self._connections.connect(self.worker.finished_error, self._on_error)
        
        self.worker.start()
    
    def closeEvent(self, event):
        # Disconnetti tutto e ferma worker
        self._connections.disconnect_all()
        
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.request_stop()
            self.worker.wait(1000)  # Attendi max 1 secondo
        
        super().closeEvent(event)
```

---

## ✅ Checklist di Completamento

- [ ] `desktop_app/core/signal_guard.py` creato
- [ ] `desktop_app/mixins/safe_worker_mixin.py` creato
- [ ] Test passano
- [ ] `chat_worker.py` refactored
- [ ] `csv_import_worker.py` refactored
- [ ] `data_worker.py` refactored
- [ ] `file_scanner_worker.py` refactored
- [ ] Tutte le view usano ConnectionTracker
- [ ] closeEvent disconnette e ferma worker

---

## ⏭️ Prossimo Step

Completata questa fase, procedi con **FASE 4: Error Boundaries** (`FASE_4_ERROR_BOUNDARIES.md`).
