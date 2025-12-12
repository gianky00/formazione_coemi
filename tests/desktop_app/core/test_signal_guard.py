"""
Test per il modulo signal_guard - CRASH ZERO FASE 3
"""

import pytest
from unittest.mock import MagicMock
from PyQt6.QtCore import QThread, pyqtSignal, QObject
from PyQt6.QtTest import QTest


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
        
        obj.deleteLater()
    
    def test_emit_multiple_args(self, qapp):
        """Emissione con più argomenti."""
        from desktop_app.core.signal_guard import SafeSignalEmitter
        
        class TestObj(QObject):
            test_signal = pyqtSignal(int, str)
        
        obj = TestObj()
        emitter = SafeSignalEmitter(obj)
        
        received = []
        obj.test_signal.connect(lambda x, y: received.append((x, y)))
        
        assert emitter.emit(obj.test_signal, 42, "hello") is True
        assert received == [(42, "hello")]
        
        obj.deleteLater()
    
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
        
        obj.deleteLater()
    
    def test_emit_with_none_owner(self, qapp):
        """Emissione con owner None."""
        from desktop_app.core.signal_guard import SafeSignalEmitter
        
        emitter = SafeSignalEmitter(None)
        
        class TestObj(QObject):
            test_signal = pyqtSignal()
        
        obj = TestObj()
        assert emitter.emit(obj.test_signal) is False
        
        obj.deleteLater()
    
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
        assert stats['is_valid'] is False
        
        obj.deleteLater()
    
    def test_emit_if_valid_alias(self, qapp):
        """Test alias emit_if_valid."""
        from desktop_app.core.signal_guard import SafeSignalEmitter
        
        class TestObj(QObject):
            test_signal = pyqtSignal(int)
        
        obj = TestObj()
        emitter = SafeSignalEmitter(obj)
        
        received = []
        obj.test_signal.connect(lambda x: received.append(x))
        
        assert emitter.emit_if_valid(obj.test_signal, 100) is True
        assert received == [100]
        
        obj.deleteLater()


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
        
        obj.deleteLater()
    
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
        
        obj.deleteLater()
    
    def test_disconnect_specific(self, qapp):
        """Test disconnessione specifica."""
        from desktop_app.core.signal_guard import ConnectionTracker
        
        class TestObj(QObject):
            test_signal = pyqtSignal()
        
        obj = TestObj()
        tracker = ConnectionTracker()
        
        # Usa funzioni salvate invece di lambda per permettere disconnessione
        received = []
        
        def slot1():
            received.append(1)
        
        def slot2():
            received.append(2)
        
        tracker.connect(obj.test_signal, slot1)
        tracker.connect(obj.test_signal, slot2)
        
        assert tracker.connection_count() == 2
        
        # Verifica che entrambi ricevano
        obj.test_signal.emit()
        assert 1 in received and 2 in received
        received.clear()
        
        # Disconnetti solo slot1
        result = tracker.disconnect(obj.test_signal, slot1)
        assert result is True
        assert tracker.connection_count() == 1
        
        # Verifica che solo slot2 riceva
        obj.test_signal.emit()
        assert received == [2]
        
        obj.deleteLater()
    
    def test_clear_without_disconnect(self, qapp):
        """Test clear senza disconnettere."""
        from desktop_app.core.signal_guard import ConnectionTracker
        
        class TestObj(QObject):
            test_signal = pyqtSignal()
        
        obj = TestObj()
        tracker = ConnectionTracker()
        
        received = []
        slot = lambda: received.append(1)
        
        tracker.connect(obj.test_signal, slot)
        tracker.clear()
        
        assert tracker.connection_count() == 0
        
        # Signal still connected (we just cleared the tracker)
        obj.test_signal.emit()
        assert received == [1]
        
        obj.deleteLater()


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
        qtbot.waitUntil(lambda: not worker.isRunning(), timeout=2000)
        
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
        QTest.qWait(100)
        
        worker.request_stop()
        qtbot.waitUntil(lambda: not worker.isRunning(), timeout=2000)
        
        final_ticks = ticks[0]
        QTest.qWait(100)
        
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
        qtbot.waitUntil(lambda: len(results) > 0, timeout=2000)
        
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
        qtbot.waitUntil(lambda: len(errors) > 0, timeout=2000)
        
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
        qtbot.waitUntil(lambda: not worker.isRunning(), timeout=2000)
        
        assert len(progress_updates) == 5
        assert progress_updates[0] == (0, "Step 0")
        assert progress_updates[4] == (100, "Step 4")
    
    def test_started_work_signal(self, qapp, qtbot):
        """Test segnale started_work."""
        from desktop_app.mixins.safe_worker_mixin import RobustWorker
        
        class SimpleWorker(RobustWorker):
            def do_work(self):
                return None
        
        worker = SimpleWorker()
        started = [False]
        worker.started_work.connect(lambda: started.__setitem__(0, True))
        
        worker.start()
        qtbot.waitUntil(lambda: not worker.isRunning(), timeout=2000)
        
        assert started[0] is True
    
    def test_stop_during_work(self, qapp, qtbot):
        """Test stop durante il lavoro."""
        from desktop_app.mixins.safe_worker_mixin import RobustWorker
        
        class LongWorker(RobustWorker):
            iterations = []
            
            def do_work(self):
                for i in range(100):
                    if self.should_stop():
                        break
                    self.iterations.append(i)
                    self.msleep(10)
                return len(self.iterations)
        
        worker = LongWorker()
        worker.iterations = []
        
        worker.start()
        QTest.qWait(50)
        worker.request_stop()
        
        qtbot.waitUntil(lambda: not worker.isRunning(), timeout=2000)
        
        # Dovrebbe essere stato fermato prima di completare tutte le iterazioni
        assert len(worker.iterations) < 100


class TestSafeEmitHelper:
    """Test per la funzione helper safe_emit."""
    
    def test_safe_emit_success(self, qapp):
        """Test safe_emit con successo."""
        from desktop_app.core.signal_guard import safe_emit
        
        class TestObj(QObject):
            test_signal = pyqtSignal(int)
        
        obj = TestObj()
        received = []
        obj.test_signal.connect(lambda x: received.append(x))
        
        assert safe_emit(obj.test_signal, 42) is True
        assert received == [42]
        
        obj.deleteLater()


class TestDisconnectAllFromObject:
    """Test per disconnect_all_from_object."""
    
    def test_disconnect_all(self, qapp):
        """Test disconnessione completa."""
        from desktop_app.core.signal_guard import disconnect_all_from_object
        
        class TestObj(QObject):
            sig1 = pyqtSignal()
            sig2 = pyqtSignal()
        
        obj = TestObj()
        received = []
        
        obj.sig1.connect(lambda: received.append(1))
        obj.sig2.connect(lambda: received.append(2))
        
        obj.sig1.emit()
        obj.sig2.emit()
        assert received == [1, 2]
        
        count = disconnect_all_from_object(obj)
        assert count >= 0  # Il count esatto non è garantito
        
        received.clear()
        obj.sig1.emit()
        obj.sig2.emit()
        assert received == []  # Non ricevuti
        
        obj.deleteLater()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
