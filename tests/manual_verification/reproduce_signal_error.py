from PyQt6.QtCore import QThread, pyqtSignal, QObject
import sys

class Worker(QObject):
    sig_object = pyqtSignal(object)
    sig_dict = pyqtSignal(dict)

    def emit_object(self, val):
        self.sig_object.emit(val)

    def emit_dict(self, val):
        self.sig_dict.emit(val)

def test_signals():
    w = Worker()

    def on_obj(val):
        print(f"Object: {val}")

    w.sig_object.connect(on_obj)

    try:
        w.emit_object({"a": 1})
        print("Emitted dict via object signal OK")
    except Exception as e:
        print(f"Failed to emit dict via object signal: {e}")

    try:
        w.emit_object("string")
        print("Emitted str via object signal OK")
    except Exception as e:
        print(f"Failed to emit str via object signal: {e}")

if __name__ == "__main__":
    test_signals()
