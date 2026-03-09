import traceback
import sys
from PySide6.QtCore import QObject, Signal, QRunnable, Slot

class WorkerSignals(QObject):
    """
    Segnali utilizzabili dal Worker per comunicare con la UI.
    """
    finished = Signal()
    error = Signal(tuple) # (type, value, traceback)
    result = Signal(object) # Qualsiasi risultato ritornato dal target
    progress = Signal(int)

class Worker(QRunnable):
    """
    Worker generico per eseguire funzioni in background nel pool di thread Qt.
    """
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        """
        Esegue la funzione passata e gestisce i segnali di ritorno.
        """
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()
