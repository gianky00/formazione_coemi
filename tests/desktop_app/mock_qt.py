import builtins
import contextlib
import datetime
import traceback
from unittest.mock import MagicMock
from dateutil.relativedelta import relativedelta

class DummySignal:
    def __init__(self):
        self._slots = []
    def connect(self, slot, connection_type=None):
        self._slots.append(slot)
    def emit(self, *args, **kwargs):
        for slot in self._slots:
            try: slot(*args, **kwargs)
            except Exception: traceback.print_exc()

class DummyQtSignal:
    def __init__(self, *args):
        self.args = args
        self._signals = {}
    def __get__(self, instance, owner):
        if instance is None: return self
        if instance not in self._signals: self._signals[instance] = DummySignal()
        return self._signals[instance]

class DummyQObject:
    def __init__(self, parent=None): pass
    def moveToThread(self, thread): pass
    def deleteLater(self): pass
    def parent(self): return None

class DummyEnum:
    StyledPanel = 1
    Sunken = 1
    Password = 1
    Plain = 0
    HLine = 1
    Ok = 1
    Cancel = 2
    Yes = 3
    No = 4
    AlignCenter = 0
    PointingHandCursor = 0
    Horizontal = 1
    Vertical = 2
    DisplayRole = 0
    EditRole = 1
    UserRole = 256
    KeepAspectRatio = 1
    CustomContextMenu = 1
    SmoothTransformation = 1
    NoPen = 0
    FramelessWindowHint = 0
    WindowNoState = 0
    RichText = 1

    class Orientation: Horizontal = 1; Vertical = 2
    class GlobalColor: transparent = 0; white = 3
    class AlignmentFlag: AlignCenter = 0; AlignLeft = 0; AlignRight = 0
    class EditTrigger: NoEditTriggers = 0; DoubleClicked = 1
    class SelectionBehavior: SelectRows = 1
    class SelectionMode: ExtendedSelection = 1

class DummyQWidget(DummyQObject):
    def __init__(self, text=None, parent=None, *args, **kwargs):
        super().__init__(parent)
        self.widgets = []
        self._text = text if isinstance(text, str) else ""
    def setLayout(self, layout): pass
    def show(self): pass
    def hide(self): pass
    def setWindowTitle(self, title): pass
    def setObjectName(self, name): pass
    def setProperty(self, name, value): pass
    def addWidget(self, widget, *args, **kwargs): self.widgets.append(widget)
    def setText(self, text): self._text = text
    def text(self): return self._text
    def exec(self): return 1
    @property
    def clicked(self): return DummySignal()

def mock_qt_modules():
    mock_widgets = MagicMock()
    mock_widgets.QWidget = DummyQWidget
    mock_widgets.QMainWindow = DummyQWidget
    mock_widgets.QDialog = DummyQWidget
    mock_widgets.QLabel = DummyQWidget
    mock_widgets.QPushButton = DummyQWidget
    mock_widgets.QLineEdit = DummyQWidget
    mock_widgets.QComboBox = DummyQWidget
    mock_widgets.QTableWidget = DummyQWidget
    mock_widgets.QVBoxLayout = DummyQWidget
    mock_widgets.QHBoxLayout = DummyQWidget
    mock_widgets.QFormLayout = DummyQWidget
    mock_widgets.QStackedWidget = DummyQWidget
    mock_widgets.QTabWidget = DummyQWidget
    mock_widgets.QScrollArea = DummyQWidget
    mock_widgets.QMessageBox = MagicMock()
    mock_widgets.QFileDialog = MagicMock()
    mock_widgets.QAbstractItemView = DummyEnum

    mock_core = MagicMock()
    mock_core.Qt = DummyEnum
    mock_core.Signal = DummyQtSignal
    mock_core.Slot = lambda *a, **k: (lambda f: f)
    mock_core.QTimer = MagicMock()
    mock_core.QThreadPool = MagicMock()
    mock_core.QRunnable = MagicMock()
    mock_core.QObject = DummyQObject

    mock_gui = MagicMock()
    mock_gui.QIcon = MagicMock()
    mock_gui.QPixmap = MagicMock()
    mock_gui.QColor = MagicMock()
    mock_gui.QBrush = MagicMock()
    mock_gui.QFont = MagicMock()

    return {
        "PySide6.QtWidgets": mock_widgets,
        "PySide6.QtCore": mock_core,
        "PySide6.QtGui": mock_gui,
    }

mock_modules = mock_qt_modules()
QtWidgets = mock_modules["PySide6.QtWidgets"]
QtCore = mock_modules["PySide6.QtCore"]
