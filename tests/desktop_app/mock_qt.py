import sys
import builtins
import datetime
from dateutil.relativedelta import relativedelta
from unittest.mock import MagicMock
import traceback

class DummySignal:
    def __init__(self):
        self._slots = []

    def connect(self, slot):
        self._slots.append(slot)

    def emit(self, *args, **kwargs):
        for slot in self._slots:
            try:
                slot(*args, **kwargs)
            except Exception:
                traceback.print_exc()

class DummyPyQtSignal:
    def __init__(self, *args):
        self.args = args
        self._signals = {}

    def __get__(self, instance, owner):
        if instance is None:
            return self
        if instance not in self._signals:
            self._signals[instance] = DummySignal()
        return self._signals[instance]

class DummyQObject:
    def __init__(self, parent=None):
        pass
    def moveToThread(self, thread):
        pass
    def deleteLater(self):
        pass
    def parent(self):
        return None

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
    AdjustToContents = 0
    WindowMaximizeButtonHint = 0
    AlignCenter = 0
    AlignLeft = 0
    AlignTop = 0
    AlignRight = 0
    AlignBottom = 0
    PointingHandCursor = 0
    Horizontal = 1
    Vertical = 2
    WA_TransparentForMouseEvents = 0
    WA_ShowWithoutActivating = 0
    WA_TranslucentBackground = 0
    WA_DeleteOnClose = 0
    AA_ShareOpenGLContexts = 0
    DisplayRole = 0
    EditRole = 1
    UserRole = 256
    WindowActive = 1
    KeepAspectRatio = 1
    CustomContextMenu = 1
    SmoothTransformation = 1
    TextSelectableByMouse = 1
    NoPen = 0
    FramelessWindowHint = 0
    Tool = 0
    WindowStaysOnTopHint = 0
    Dialog = 0
    SubWindow = 0
    transparent = 0
    white = 3
    WindowNoState = 0
    WindowMinimized = 1
    NoFrame = 0
    RichText = 1

    class Orientation:
        Horizontal = 1
        Vertical = 2

    class ContextMenuPolicy:
        CustomContextMenu = 1

    class TextInteractionFlag:
        TextBrowserInteraction = 1

    class WindowState:
        WindowNoState = 0
        WindowMinimized = 1

    class Shape:
        NoFrame = 0
        HLine = 1

    class GlobalColor:
        transparent = 0
        white = 3

    class ItemDataRole:
        DisplayRole = 0
        EditRole = 1
        UserRole = 256

    class ApplicationAttribute:
        AA_ShareOpenGLContexts = 0

    class AspectRatioMode:
        KeepAspectRatio = 1

    class TransformationMode:
        SmoothTransformation = 1

    class CursorShape:
        PointingHandCursor = 0

    class PenStyle:
        NoPen = 0

    class WindowType:
        FramelessWindowHint = 0
        Tool = 0
        WindowStaysOnTopHint = 0
        Dialog = 0
        SubWindow = 0

    class WidgetAttribute:
        WA_TranslucentBackground = 0
        WA_ShowWithoutActivating = 0
        WA_DeleteOnClose = 0
        WA_TransparentForMouseEvents = 0

    class BrushStyle:
        NoBrush = 0

    class AlignmentFlag:
        AlignCenter = 0
        AlignLeft = 0
        AlignRight = 0
        AlignTop = 0
        AlignBottom = 0
        AlignVCenter = 0
        AlignHCenter = 0

    class TextFlag:
        TextWordWrap = 0

    class EditTrigger:
        NoEditTriggers = 0
        DoubleClicked = 1

    class SelectionBehavior:
        SelectRows = 1
        SelectItems = 0

    class SelectionMode:
        ExtendedSelection = 1
        SingleSelection = 0
    
    class TextFormat:
        RichText = 1

class DummyQLayoutItem:
    def __init__(self, widget):
        self._widget = widget
    def widget(self):
        return self._widget

class DummyQModelIndex:
    def __init__(self, row=0, column=0):
        self._row = row
        self._column = column

    def row(self):
        return self._row

    def column(self):
        return self._column

    def isValid(self):
        return True

    def data(self, role=0):
        return None

class DummyQAbstractTableModel(DummyQObject):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent)
        self._data = []

    def index(self, row, column, parent=None):
        return DummyQModelIndex(row, column)

    def beginResetModel(self): pass
    def endResetModel(self): pass
    def layoutChanged(self):
        return DummySignal()
    def rowCount(self, parent=None): return 0
    def columnCount(self, parent=None): return 0
    def data(self, index, role=0): return None
    def flags(self, index): return 0
    def headerData(self, section, orientation, role=0): return None

class DummyQPoint:
    def __init__(self, x=0, y=0):
        self._x = x
        self._y = y
    def x(self): return self._x
    def y(self): return self._y
    def __add__(self, other):
        return DummyQPoint(self._x + other.x(), self._y + other.y())
    def __sub__(self, other):
        return DummyQPoint(self._x - other.x(), self._y - other.y())

class DummyQRect:
    def __init__(self, x=0, y=0, w=0, h=0):
        if hasattr(x, 'x') and hasattr(x, 'y'): # QRect(QPoint top_left, QSize size)
            self._x = int(x.x())
            self._y = int(x.y())
            # y is size (MagicMock)
            self._w = 100
            self._h = 100
            if hasattr(y, 'width'):
                try: self._w = int(y.width())
                except: pass
            if hasattr(y, 'height'):
                try: self._h = int(y.height())
                except: pass
        else:
            self._x = int(x)
            self._y = int(y)
            self._w = int(w)
            self._h = int(h)

    def x(self): return int(self._x)
    def y(self): return int(self._y)
    def width(self): return int(self._w)
    def height(self): return int(self._h)
    def contains(self, *args): return False
    def isValid(self): return True

    def translated(self, x, y):
        if hasattr(x, 'x') and hasattr(x, 'y'):
            dx, dy = x.x(), x.y()
        else:
            dx, dy = x, y
        return DummyQRect(self._x + dx, self._y + dy, self._w, self._h)

class DummyQWidget(DummyQObject):
    # Enum mocks
    Shape = DummyEnum
    Shadow = DummyEnum
    EchoMode = DummyEnum
    StandardButton = DummyEnum
    SizeAdjustPolicy = DummyEnum
    WindowType = DummyEnum
    CursorShape = DummyEnum
    AlignmentFlag = DummyEnum
    Orientation = DummyEnum
    WidgetAttribute = DummyEnum
    ApplicationAttribute = DummyEnum
    ItemDataRole = DummyEnum
    WindowState = DummyEnum
    AspectRatioMode = DummyEnum
    TransformationMode = DummyEnum
    ContextMenuPolicy = DummyEnum
    TextInteractionFlag = DummyEnum
    PenStyle = DummyEnum
    GlobalColor = DummyEnum
    BrushStyle = DummyEnum
    TextFlag = DummyEnum
    TextFormat = DummyEnum
    
    # We add these as attributes for instances that access them as nested classes
    EditTrigger = DummyEnum.EditTrigger
    SelectionBehavior = DummyEnum.SelectionBehavior
    SelectionMode = DummyEnum.SelectionMode
    StandardButton = DummyEnum # Expose StandardButton on DummyQWidget

    def __init__(self, text=None, parent=None, *args, **kwargs):
        super().__init__(parent)
        self._clicked = DummySignal()
        self._toggled = DummySignal()
        self._accepted = DummySignal()
        self._rejected = DummySignal()
        self._currentIndexChanged = DummySignal()
        self._returnPressed = DummySignal()
        self._textChanged = DummySignal()
        self._dateChanged = DummySignal()
        self.widgets = []
        self._text = text if isinstance(text, str) else ""

    def setLayout(self, layout):
        pass
    def layout(self):
        return MagicMock()
    def show(self):
        self._visible = True
    def hide(self):
        self._visible = False
    def setVisible(self, visible):
        self._visible = visible
    def showEvent(self, event):
        pass
    def closeEvent(self, event):
        pass
    def close(self):
        self.closeEvent(None)
        return True
    def isVisible(self):
        return getattr(self, '_visible', True)
    def blockSignals(self, block):
        return False
    def setUpdatesEnabled(self, enable):
        pass
    def setWindowTitle(self, title):
        pass
    def setWindowFlags(self, flags):
        pass
    def windowFlags(self):
        return 0
    def windowState(self):
        return DummyEnum.WindowNoState
    def isWindow(self):
        return False
    def showMaximized(self):
        pass
    def activateWindow(self):
        pass
    def setAttribute(self, attr, on=True):
        pass
    def raise_(self):
        pass
    def resizeEvent(self, event):
        pass
    def resize(self, *args):
        pass
    def size(self):
        return MagicMock()
    def setGeometry(self, *args):
        pass
    def geometry(self):
        return DummyQRect(0, 0, 100, 100)
    def pos(self):
        return DummyQPoint(0, 0)
    def move(self, x, y):
        pass
    def setObjectName(self, name):
        pass
    def setFixedWidth(self, width):
        pass
    def width(self):
        return 100
    def setFixedHeight(self, height):
        pass
    def height(self):
        return 100
    def setFixedSize(self, w, h):
        pass
    def setMinimumWidth(self, width):
        pass
    def setMinimumHeight(self, height):
        pass
    def setMinimumDate(self, date):
        pass
    def setSpecialValueText(self, text):
        pass
    def setMaximumWidth(self, width):
        pass
    def setContentsMargins(self, l, t, r, b):
        pass
    def setSpacing(self, spacing):
        pass
    def setCursor(self, cursor):
        pass
    def setMouseTracking(self, enable):
        pass
    def setTextInteractionFlags(self, flags):
        pass
    def setWordWrap(self, on):
        pass
    def setToolTip(self, text):
        pass
    def setProperty(self, name, value):
        pass
    def property(self, name):
        return "mock_property"
    def findChild(self, type, name=""):
        # Return a mock that can handle setText, etc.
        m = MagicMock()
        m.setText = MagicMock()
        return m
    def style(self):
        m = MagicMock()
        m.unpolish = MagicMock()
        m.polish = MagicMock()
        return m
    def addWidget(self, widget, *args, **kwargs):
        self.widgets.append(widget)
    def addLayout(self, layout, stretch=0):
        pass
    def addStretch(self, stretch=0):
        pass
    def itemAt(self, index):
        if 0 <= index < len(self.widgets):
            return DummyQLayoutItem(self.widgets[index])
        return None
    def addSpacing(self, spacing):
        pass
    def setStretch(self, index, stretch):
        pass
    def setEchoMode(self, mode):
        pass
    def setPlaceholderText(self, text):
        pass
    def setText(self, text):
        self._text = text
    def text(self):
        return self._text
    def currentText(self):
        return "mock text"
    def currentData(self):
        return None
    def currentIndex(self):
        return 0
    def addItems(self, items):
        self.widgets.extend(items)
    def addItem(self, item, userData=None):
        self.widgets.append(item)
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
    def styleSheet(self):
        return ""
    def setGraphicsEffect(self, effect):
        pass
    def setChecked(self, checked):
        self._checked = checked
    def isChecked(self):
        return getattr(self, '_checked', True)
    def setCurrentWidget(self, widget):
        pass
    def currentWidget(self):
        if self.widgets:
            return self.widgets[0]
        return None
    def widget(self, index):
        if 0 <= index < len(self.widgets):
            return self.widgets[index]
        return None
    def count(self):
        return len(self.widgets)
    def setEnabled(self, enabled):
        self._enabled = enabled
    def isEnabled(self):
        return getattr(self, '_enabled', True)
    def selectionModel(self):
        m = MagicMock()
        m.hasSelection.return_value = True
        m.selectedRows.return_value = [DummyQModelIndex(0, 0)]
        m.selectionChanged = DummySignal()
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
    def setEditTriggers(self, triggers):
        pass
    def setAlternatingRowColors(self, enable):
        pass
    def setModel(self, model):
        self._model = model
    def model(self):
        return getattr(self, '_model', None)
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
    def setCalendarPopup(self, enable):
        pass
    def setDate(self, date):
        pass
    def date(self):
        return DummyQDate()
    def button(self, which):
        return DummyQWidget()
    def adjustSize(self):
        pass
    def update(self):
        pass
    def repaint(self):
        pass
    def setCurrentText(self, text):
        pass
    def accept(self):
        pass
    def reject(self):
        pass
    def setReadOnly(self, ro):
        pass
    def viewport(self):
        m = MagicMock()
        m.mapToGlobal = MagicMock()
        m.width.return_value = 800
        return m
    def indexAt(self, pos):
        m = MagicMock()
        m.isValid.return_value = False
        return m
    def setContextMenuPolicy(self, policy):
        pass
    def setScene(self, scene):
        pass
    def setRange(self, min, max):
        pass
    def setTextVisible(self, v):
        pass
    def setValue(self, v):
        self._value = v
    def value(self):
        return getattr(self, '_value', 0)
    def maximum(self):
        return 100
    def setMaximum(self, m):
        pass
    def rect(self):
        # Return a DummyQRect compatible with paintEvent expectations
        return DummyQRect(0, 0, 100, 30)
    def indexOf(self, widget):
        if widget in self.widgets:
            return self.widgets.index(widget)
        return -1
    def insertWidget(self, i, w):
        pass
    def takeAt(self, i):
        return DummyQLayoutItem(MagicMock())
    def setSizes(self, sizes):
        pass
    def setHeaderLabels(self, labels):
        pass
    def setFont(self, font):
        pass
    def clear(self):
        self.widgets = []
        if getattr(self, '_model', None):
            self._model._data = []
    def setStartValue(self, v):
        pass
    def setEndValue(self, v):
        pass
    def setDuration(self, d):
        pass
    def setEasingCurve(self, c):
        pass
    def start(self):
        pass
    def stop(self):
        pass
    def valueChanged(self):
        return DummySignal()
    def finished(self):
        return DummySignal()
    def clicked(self):
        return self._clicked
    def setSceneRect(self, *args):
        pass
    def mapToGlobal(self, pos):
        return pos
    def exec(self, *args):
        pass
    def installEventFilter(self, filterObj):
        pass
    def setTextFormat(self, fmt):
        pass
    def setOpenExternalLinks(self, open):
        pass
    def setItemDelegateForColumn(self, col, delegate):
        pass

    def parent(self):
        return None

    def window(self):
        return self

    def setWindowOpacity(self, opacity):
        self._window_opacity = opacity
    def windowOpacity(self):
        return getattr(self, '_window_opacity', 1.0)

    # Signals
    @builtins.property
    def clicked(self):
        return self._clicked

    @builtins.property
    def toggled(self):
        return self._toggled

    @builtins.property
    def accepted(self):
        return self._accepted

    @builtins.property
    def rejected(self):
        return self._rejected

    @builtins.property
    def currentIndexChanged(self):
        return self._currentIndexChanged

    @builtins.property
    def returnPressed(self):
        return self._returnPressed

    @builtins.property
    def textChanged(self):
        return self._textChanged

    @builtins.property
    def dateChanged(self):
        return self._dateChanged

    @builtins.property
    def resized(self):
        return DummySignal()
    @builtins.property
    def itemClicked(self):
        return DummySignal()
    @builtins.property
    def customContextMenuRequested(self):
        return DummySignal()
    @builtins.property
    def import_completed(self):
        return DummySignal()
    @builtins.property
    def validation_completed(self):
        return DummySignal()
    @builtins.property
    def database_changed(self):
        return DummySignal()
    
    @builtins.property
    def linkActivated(self):
        return DummySignal()

class DummyQMainWindow(DummyQWidget):
    def setCentralWidget(self, widget):
        pass

class DummyQDialog(DummyQWidget):
    def exec(self):
        pass

class DummyQDate:
    def __init__(self, y=None, m=None, d=None):
        if y is None:
            self._date = datetime.date.today()
        elif m is not None and d is not None:
            self._date = datetime.date(y, m, d)
        elif isinstance(y, datetime.date):
            self._date = y
        else:
            self._date = datetime.date.today()

    @staticmethod
    def currentDate():
        return DummyQDate(datetime.date.today())

    @staticmethod
    def fromString(s, f):
        # Basic parsing for "dd/MM/yyyy" which is used in the view
        try:
            if "dd/MM/yyyy" in f:
                d = datetime.datetime.strptime(s, "%d/%m/%Y").date()
                return DummyQDate(d)
        except:
            pass
        return DummyQDate()

    def addDays(self, days):
        return DummyQDate(self._date + datetime.timedelta(days=days))

    def addMonths(self, months):
        return DummyQDate(self._date + relativedelta(months=months))

    def setDate(self, y, m, d):
        self._date = datetime.date(y, m, d)

    def year(self): return self._date.year
    def month(self): return self._date.month
    def day(self): return self._date.day

    def daysTo(self, other):
        if isinstance(other, DummyQDate):
            return (other._date - self._date).days
        return 0

    def toString(self, format_str):
        # Simple mapping for common Qt format strings to strftime
        fmt = format_str.replace("dd", "%d").replace("MM", "%m").replace("yyyy", "%Y")
        fmt = fmt.replace("MMM", "%b") # Abbreviated month
        return self._date.strftime(fmt)

    def toPyDate(self):
        return self._date

    def isValid(self):
        return True

    def __eq__(self, other):
        if isinstance(other, DummyQDate):
            return self._date == other._date
        return False

    def __le__(self, other):
        if isinstance(other, DummyQDate):
            return self._date <= other._date
        return False

    def __ge__(self, other):
        if isinstance(other, DummyQDate):
            return self._date >= other._date
        return False

    def __lt__(self, other):
        if isinstance(other, DummyQDate):
            return self._date < other._date
        return False

    def __gt__(self, other):
        if isinstance(other, DummyQDate):
            return self._date > other._date
        return False

class DummyQLocale:
    Language = MagicMock()
    Country = MagicMock()
    def __init__(self, *args):
        pass
    def toString(self, date, fmt):
        return "Jan 2025"

class DummyQTreeWidgetItem(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__()
        # Consume parent args to avoid MagicMock confusion if any

    def setData(self, col, role, value):
        pass

    def data(self, col, role):
        return None

class DummyQGraphicsTextItem(DummyQObject):
    def __init__(self, *args, **kwargs):
        super().__init__()
    def setFont(self, font): pass
    def setPos(self, x, y): pass
    def setDefaultTextColor(self, color): pass
    def boundingRect(self):
        m = MagicMock()
        m.width.return_value = 100
        return m

class DummyQGraphicsRectItem(DummyQObject):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self._z = 0

    def setBrush(self, brush): pass
    def setPen(self, pen): pass
    def setZValue(self, z): self._z = z
    def zValue(self): return self._z
    def setRect(self, x, y, w, h): pass
    def rect(self):
        m = MagicMock()
        m.x.return_value = 0
        m.width.return_value = 100
        return m
    def setData(self, key, value): pass
    def setToolTip(self, text): pass

class DummyQGraphicsLineItem(DummyQObject):
    def __init__(self, *args, **kwargs):
        super().__init__()
    def setPen(self, pen): pass
    def setLine(self, x1, y1, x2, y2): pass
    def line(self):
        m = MagicMock()
        m.x1.return_value = 0
        m.x2.return_value = 0
        return m

class DummyQGraphicsScene(DummyQWidget):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self._items = []

    def addItem(self, item):
        self._items.append(item)

    def items(self):
        return self._items

    def clear(self):
        self._items = []

    def setSceneRect(self, x, y, w, h):
        pass

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

class DummyQWebEngineView(DummyQWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.url = None
        self.html = None
    def setUrl(self, url):
        self.url = url
    def setHtml(self, html, baseUrl=None):
        self.html = html
    def page(self):
        page = MagicMock()
        return page
    def setPage(self, page):
        pass

class DummyQWebEnginePage(DummyQWidget):
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        pass

class DummyEffect(MagicMock):
    def __init__(self, *args, **kwargs):
        # Swallow arguments to prevent MagicMock from using them as spec/parent
        super().__init__()

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
    mock_widgets.QGridLayout = DummyQWidget
    mock_widgets.QFormLayout = DummyQFormLayout
    mock_widgets.QStackedWidget = DummyQWidget
    mock_widgets.QMessageBox = MagicMock()
    mock_widgets.QMessageBox.StandardButton = DummyEnum
    mock_widgets.QTableView = DummyQTableView
    mock_widgets.QHeaderView = DummyQHeaderView
    mock_widgets.QDateEdit = DummyQWidget
    mock_widgets.QCheckBox = DummyQWidget
    mock_widgets.QDialogButtonBox = DummyQWidget
    mock_widgets.QListView = DummyQWidget
    mock_widgets.QListWidget = DummyQWidget
    mock_widgets.QListWidgetItem = MagicMock
    mock_widgets.QTreeWidget = DummyQWidget
    mock_widgets.QTreeWidgetItem = DummyQTreeWidgetItem
    mock_widgets.QSplitter = DummyQWidget
    mock_widgets.QGraphicsView = DummyQWidget
    mock_widgets.QGraphicsScene = DummyQGraphicsScene
    mock_widgets.QGraphicsRectItem = DummyQGraphicsRectItem
    mock_widgets.QGraphicsTextItem = DummyQGraphicsTextItem
    mock_widgets.QGraphicsLineItem = DummyQGraphicsLineItem
    mock_widgets.QScrollBar = DummyQWidget
    mock_widgets.QProgressBar = DummyQWidget
    mock_widgets.QMenu = MagicMock()
    mock_widgets.QAction = MagicMock()
    mock_widgets.QStyledItemDelegate = MagicMock
    mock_widgets.QGraphicsOpacityEffect = DummyEffect
    mock_widgets.QGraphicsDropShadowEffect = DummyEffect
    mock_widgets.QTextEdit = DummyQWidget
    mock_widgets.QFileDialog = MagicMock()

    mock_core = MagicMock()
    mock_core.PYQT_VERSION = 0x060800 # Mock version 6.8.0
    mock_core.Qt = DummyEnum # Use Enum
    mock_core.QSize = MagicMock()
    mock_core.QDate = DummyQDate
    mock_core.QObject = DummyQObject
    mock_core.QAbstractTableModel = DummyQAbstractTableModel
    mock_widgets.QAbstractItemView = DummyQWidget # Use DummyQWidget as base for QAbstractItemView enum access
    mock_core.QTimer = MagicMock()
    mock_core.QCoreApplication = MagicMock()
    
    class DummyQPropertyAnimation(MagicMock):
        def __init__(self, target=None, prop_name=None, parent=None, **kwargs):
            super().__init__(**kwargs)
            self._finished = DummySignal()

        @property
        def finished(self):
            return self._finished
        
        def setStartValue(self, v): pass
        def setEndValue(self, v): pass
        def setDuration(self, d): pass
        def setEasingCurve(self, c): pass
        def state(self): return 0 # Stopped

        def start(self):
            # Auto-finish for tests
            self._finished.emit()
        
        def stop(self): pass

    mock_core.QPropertyAnimation = DummyQPropertyAnimation
    mock_core.QEasingCurve = MagicMock()
    mock_core.pyqtSignal = DummyPyQtSignal

    def dummy_pyqtSlot(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    mock_core.pyqtSlot = dummy_pyqtSlot

    mock_core.QThreadPool = MagicMock()
    
    class DummyQThread(DummyQObject):
        def __init__(self, parent=None):
            super().__init__(parent)
            self._started = DummySignal()
            self._finished = DummySignal()

        @property
        def started(self):
            return self._started

        @property
        def finished(self):
            return self._finished

        def start(self):
            self._started.emit()

        def quit(self): pass
        def wait(self): pass
        def isRunning(self): return False
        def run(self): pass

        @staticmethod
        def currentThread():
            return "MainThread"

    mock_core.QThread = DummyQThread
    mock_core.QRunnable = MagicMock

    mock_core.QPoint = DummyQPoint
    mock_core.QPointF = DummyQPoint
    mock_core.QRect = DummyQRect
    mock_core.QRectF = DummyQRect
    mock_core.QVariantAnimation = MagicMock()
    mock_core.QParallelAnimationGroup = MagicMock()
    mock_core.QUrl = MagicMock()
    mock_core.QUrl.fromLocalFile = MagicMock()
    mock_core.QLocale = DummyQLocale

    mock_media = MagicMock()
    mock_media.QSoundEffect = MagicMock()
    mock_media.QMediaPlayer = MagicMock()
    mock_media.QAudioOutput = MagicMock()

    mock_gui = MagicMock()
    mock_gui.QIcon = MagicMock()
    mock_gui.QPixmap = MagicMock()
    mock_gui.QColor = MagicMock()
    mock_gui.QBrush = MagicMock()
    mock_gui.QPen = MagicMock()
    mock_gui.QFont = MagicMock()
    mock_gui.QLinearGradient = MagicMock()
    mock_gui.QPainterPath = MagicMock()
    mock_gui.QPainter = MagicMock()
    mock_gui.QPageLayout = MagicMock()
    mock_gui.QPageSize = MagicMock()
    mock_gui.QImage = MagicMock()
    mock_gui.QDesktopServices = MagicMock()

    mock_web = MagicMock()
    mock_web.QWebEngineView = DummyQWebEngineView

    mock_web_core = MagicMock()
    mock_web_core.QWebEnginePage = DummyQWebEnginePage

    mock_webchannel = MagicMock()
    mock_webchannel.QWebChannel = MagicMock

    mock_pyqt6 = MagicMock()
    mock_pyqt6.QtWidgets = mock_widgets
    mock_pyqt6.QtCore = mock_core
    mock_pyqt6.QtGui = mock_gui
    mock_pyqt6.QtWebEngineWidgets = mock_web
    mock_pyqt6.QtWebEngineCore = mock_web_core
    mock_pyqt6.QtWebChannel = mock_webchannel
    mock_pyqt6.QtMultimedia = mock_media

    return {
        'PyQt6': mock_pyqt6,
        'PyQt6.QtWidgets': mock_widgets,
        'PyQt6.QtCore': mock_core,
        'PyQt6.QtGui': mock_gui,
        'PyQt6.QtWebEngineWidgets': mock_web,
        'PyQt6.QtWebEngineCore': mock_web_core,
        'PyQt6.QtWebChannel': mock_webchannel,
        'PyQt6.QtMultimedia': mock_media,
        'PyQt6.QtPrintSupport': MagicMock(),
        'PyQt6.QtNetwork': MagicMock(),
    }

# Create the mock modules
mock_modules = mock_qt_modules()
QtWidgets = mock_modules['PyQt6.QtWidgets']
QtCore = mock_modules['PyQt6.QtCore']
