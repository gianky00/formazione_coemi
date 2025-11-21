import sys
from unittest.mock import MagicMock

class DummySignal:
    def connect(self, slot):
        pass

class DummyEnum:
    StyledPanel = 1
    Sunken = 1
    Password = 1
    Plain = 0
    HLine = 1
    Ok = 1
    Cancel = 2
    AdjustToContents = 0

class DummyQWidget:
    # Enum mocks
    Shape = DummyEnum
    Shadow = DummyEnum
    EchoMode = DummyEnum
    StandardButton = DummyEnum
    SizeAdjustPolicy = DummyEnum

    def __init__(self, parent=None):
        self._clicked = DummySignal()
        self._toggled = DummySignal()
        self._accepted = DummySignal()
        self._rejected = DummySignal()
        self._currentIndexChanged = DummySignal()
    def setLayout(self, layout):
        pass
    def layout(self):
        return MagicMock()
    def show(self):
        pass
    def setWindowTitle(self, title):
        pass
    def resize(self, w, h):
        pass
    def setObjectName(self, name):
        pass
    def setFixedWidth(self, width):
        pass
    def setFixedHeight(self, height):
        pass
    def setFixedSize(self, w, h):
        pass
    def setMinimumWidth(self, width):
        pass
    def setMinimumHeight(self, height):
        pass
    def setContentsMargins(self, l, t, r, b):
        pass
    def setSpacing(self, spacing):
        pass
    def addWidget(self, widget, *args, **kwargs):
        pass
    def addLayout(self, layout):
        pass
    def addStretch(self):
        pass
    def addSpacing(self, spacing):
        pass
    def setEchoMode(self, mode):
        pass
    def setPlaceholderText(self, text):
        pass
    def setText(self, text):
        pass
    def text(self):
        return "mock text"
    def currentText(self):
        return "mock text"
    def addItems(self, items):
        pass
    def setFrameShape(self, shape):
        pass
    def setFrameShadow(self, shadow):
        pass
    def setFieldGrowthPolicy(self, policy):
        pass
    def addRow(self, label, field=None):
        pass
    def setAlignment(self, alignment):
        pass
    def setPixmap(self, pixmap):
        pass
    def setCheckable(self, checkable):
        pass
    def setIcon(self, icon):
        pass
    def setIconSize(self, size):
        pass
    def setStyleSheet(self, style):
        pass
    def setChecked(self, checked):
        pass
    def isChecked(self):
        return True
    def setCurrentWidget(self, widget):
        pass
    def count(self):
        return 5
    def setEnabled(self, enabled):
        pass
    def selectionModel(self):
        m = MagicMock()
        m.hasSelection.return_value = True
        m.selectedRows.return_value = [1]
        return m
    def setCurrentIndex(self, index):
        pass
    def setAcceptDrops(self, accept):
        pass
    def verticalHeader(self):
        m = MagicMock()
        m.setDefaultSectionSize = MagicMock()
        return m
    def horizontalHeader(self):
        m = MagicMock()
        m.setSectionResizeMode = MagicMock()
        return m
    def setSelectionBehavior(self, behavior):
        pass
    def setSelectionMode(self, mode):
        pass
    def setAlternatingRowColors(self, enable):
        pass
    def setModel(self, model):
        pass
    def setColumnHidden(self, col, hidden):
        pass
    def selectRow(self, row):
        pass
    def setShowGrid(self, show):
        pass
    def setEditable(self, editable):
        pass
    def setView(self, view):
        pass
    def setSizeAdjustPolicy(self, policy):
        pass
    def setDisplayFormat(self, format):
        pass
    def setDate(self, date):
        pass
    def date(self):
        return DummyQDate()
    def button(self, which):
        return DummyQWidget()
    def adjustSize(self):
        pass
    def setCurrentText(self, text):
        pass
    def accept(self):
        pass
    def reject(self):
        pass

    # Signals
    @property
    def clicked(self):
        return self._clicked

    @property
    def toggled(self):
        return self._toggled

    @property
    def accepted(self):
        return self._accepted

    @property
    def rejected(self):
        return self._rejected

    @property
    def currentIndexChanged(self):
        return self._currentIndexChanged

class DummyQMainWindow(DummyQWidget):
    def setCentralWidget(self, widget):
        pass

class DummyQDialog(DummyQWidget):
    def exec(self):
        pass

class DummyQDate:
    @staticmethod
    def currentDate():
        return DummyQDate()
    @staticmethod
    def fromString(s, f):
        return DummyQDate()

    def addDays(self, days):
        return DummyQDate()

    def addMonths(self, months):
        return DummyQDate()

    def day(self):
        return 1

    def daysTo(self, other):
        return 10

    def toString(self, format_str):
        return "Jan 2025"

    def isValid(self):
        return True

    def __le__(self, other):
        return True

    def __ge__(self, other):
        return True

class DummyQFormLayout(DummyQWidget):
    class FieldGrowthPolicy:
        AllNonFixedFieldsGrow = 1

class DummyQTableView(DummyQWidget):
    class SelectionBehavior:
        SelectRows = 1
    class SelectionMode:
        ExtendedSelection = 1

class DummyQHeaderView(DummyQWidget):
    class ResizeMode:
        ResizeToContents = 0
        Stretch = 1

# Mock module structure
def mock_qt_modules():
    mock_widgets = MagicMock()
    mock_widgets.QWidget = DummyQWidget
    mock_widgets.QMainWindow = DummyQMainWindow
    mock_widgets.QDialog = DummyQDialog
    mock_widgets.QFrame = DummyQWidget
    mock_widgets.QLabel = DummyQWidget
    mock_widgets.QPushButton = DummyQWidget
    mock_widgets.QLineEdit = DummyQWidget
    mock_widgets.QComboBox = DummyQWidget
    mock_widgets.QVBoxLayout = DummyQWidget
    mock_widgets.QHBoxLayout = DummyQWidget
    mock_widgets.QFormLayout = DummyQFormLayout
    mock_widgets.QStackedWidget = DummyQWidget
    mock_widgets.QMessageBox = MagicMock()
    mock_widgets.QTableView = DummyQTableView
    mock_widgets.QHeaderView = DummyQHeaderView
    mock_widgets.QDateEdit = DummyQWidget
    mock_widgets.QCheckBox = DummyQWidget
    mock_widgets.QDialogButtonBox = DummyQWidget
    mock_widgets.QListView = DummyQWidget

    mock_core = MagicMock()
    mock_core.Qt = MagicMock()
    mock_core.QSize = MagicMock()
    mock_core.QDate = DummyQDate
    mock_core.QAbstractTableModel = MagicMock

    mock_gui = MagicMock()
    mock_gui.QIcon = MagicMock()
    mock_gui.QPixmap = MagicMock()

    mock_web = MagicMock()
    mock_web.QWebEngineView = MagicMock

    return {
        'PyQt6.QtWidgets': mock_widgets,
        'PyQt6.QtCore': mock_core,
        'PyQt6.QtGui': mock_gui,
        'PyQt6.QtWebEngineWidgets': mock_web,
        'PyQt6.QtPrintSupport': MagicMock(),
        'PyQt6.QtNetwork': MagicMock(),
    }
