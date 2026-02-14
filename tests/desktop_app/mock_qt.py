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
        """Connect slot, optionally with connection type (ignored in mock)."""
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

    def moveToThread(self, thread):  # NOSONAR
        # Mock implementation
        pass

    def deleteLater(self):  # NOSONAR
        # Mock implementation
        pass

    def parent(self):
        return None


class DummyEnum:
    StyledPanel = 1  # NOSONAR
    Sunken = 1  # NOSONAR
    Password = 1  # NOSONAR
    Plain = 0  # NOSONAR
    HLine = 1  # NOSONAR
    Ok = 1  # NOSONAR
    Cancel = 2  # NOSONAR
    Yes = 3  # NOSONAR
    No = 4  # NOSONAR
    AdjustToContents = 0  # NOSONAR
    WindowMaximizeButtonHint = 0  # NOSONAR
    AlignCenter = 0  # NOSONAR
    AlignLeft = 0  # NOSONAR
    AlignTop = 0  # NOSONAR
    AlignRight = 0  # NOSONAR
    AlignBottom = 0  # NOSONAR
    PointingHandCursor = 0  # NOSONAR
    Horizontal = 1  # NOSONAR
    Vertical = 2  # NOSONAR
    WA_TransparentForMouseEvents = 0  # NOSONAR
    WA_ShowWithoutActivating = 0  # NOSONAR
    WA_TranslucentBackground = 0  # NOSONAR
    WA_DeleteOnClose = 0  # NOSONAR
    AA_ShareOpenGLContexts = 0  # NOSONAR
    DisplayRole = 0  # NOSONAR
    EditRole = 1  # NOSONAR
    UserRole = 256  # NOSONAR
    WindowActive = 1  # NOSONAR
    KeepAspectRatio = 1  # NOSONAR
    CustomContextMenu = 1  # NOSONAR
    SmoothTransformation = 1  # NOSONAR
    TextSelectableByMouse = 1  # NOSONAR
    NoPen = 0  # NOSONAR
    FramelessWindowHint = 0  # NOSONAR
    Tool = 0  # NOSONAR
    WindowStaysOnTopHint = 0  # NOSONAR
    Dialog = 0  # NOSONAR
    SubWindow = 0  # NOSONAR
    transparent = 0
    white = 3
    WindowNoState = 0  # NOSONAR
    WindowMinimized = 1  # NOSONAR
    NoFrame = 0  # NOSONAR
    RichText = 1  # NOSONAR

    class ConnectionType:
        AutoConnection = 0  # NOSONAR
        DirectConnection = 1  # NOSONAR
        QueuedConnection = 2  # NOSONAR
        BlockingQueuedConnection = 3  # NOSONAR
        UniqueConnection = 128  # NOSONAR

    class Orientation:
        Horizontal = 1  # NOSONAR
        Vertical = 2  # NOSONAR

    class ContextMenuPolicy:
        CustomContextMenu = 1  # NOSONAR

    class TextInteractionFlag:
        TextBrowserInteraction = 1  # NOSONAR

    class WindowState:
        WindowNoState = 0  # NOSONAR
        WindowMinimized = 1  # NOSONAR

    class Shape:
        NoFrame = 0  # NOSONAR
        HLine = 1  # NOSONAR

    class GlobalColor:
        transparent = 0
        white = 3

    class ItemDataRole:
        DisplayRole = 0  # NOSONAR
        EditRole = 1  # NOSONAR
        UserRole = 256  # NOSONAR

    class ApplicationAttribute:
        AA_ShareOpenGLContexts = 0  # NOSONAR

    class AspectRatioMode:
        KeepAspectRatio = 1  # NOSONAR

    class TransformationMode:
        SmoothTransformation = 1  # NOSONAR

    class CursorShape:
        PointingHandCursor = 0  # NOSONAR

    class PenStyle:
        NoPen = 0  # NOSONAR

    class WindowType:
        FramelessWindowHint = 0  # NOSONAR
        Tool = 0  # NOSONAR
        WindowStaysOnTopHint = 0  # NOSONAR
        Dialog = 0  # NOSONAR
        SubWindow = 0  # NOSONAR

    class WidgetAttribute:
        WA_TranslucentBackground = 0  # NOSONAR
        WA_ShowWithoutActivating = 0  # NOSONAR
        WA_DeleteOnClose = 0  # NOSONAR
        WA_TransparentForMouseEvents = 0  # NOSONAR

    class BrushStyle:
        NoBrush = 0  # NOSONAR

    class AlignmentFlag:
        AlignCenter = 0  # NOSONAR
        AlignLeft = 0  # NOSONAR
        AlignRight = 0  # NOSONAR
        AlignTop = 0  # NOSONAR
        AlignBottom = 0  # NOSONAR
        AlignVCenter = 0  # NOSONAR
        AlignHCenter = 0  # NOSONAR

    class TextFlag:
        TextWordWrap = 0  # NOSONAR

    class EditTrigger:
        NoEditTriggers = 0  # NOSONAR
        DoubleClicked = 1  # NOSONAR

    class SelectionBehavior:
        SelectRows = 1  # NOSONAR
        SelectItems = 0  # NOSONAR

    class SelectionMode:
        ExtendedSelection = 1  # NOSONAR
        SingleSelection = 0  # NOSONAR

    class TextFormat:
        RichText = 1  # NOSONAR


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

    def isValid(self):  # NOSONAR
        return True

    def data(self, role=0):  # NOSONAR
        return None


class DummyQAbstractTableModel(DummyQObject):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent)
        self._data = []

    def index(self, row, column, parent=None):  # NOSONAR
        return DummyQModelIndex(row, column)

    def beginResetModel(self):  # NOSONAR
        # Mock implementation
        pass

    def endResetModel(self):  # NOSONAR
        # Mock implementation
        pass

    def layoutChanged(self):  # NOSONAR
        return DummySignal()

    def rowCount(self, parent=None):
        return 0  # NOSONAR

    def columnCount(self, parent=None):
        return 0  # NOSONAR

    def data(self, index, role=0):
        return None  # NOSONAR

    def flags(self, index):
        return 0  # NOSONAR

    def headerData(self, section, orientation, role=0):
        return None  # NOSONAR


class DummyQPoint:
    def __init__(self, x=0, y=0):
        self._x = x
        self._y = y

    def x(self):
        return self._x

    def y(self):
        return self._y

    def __add__(self, other):
        return DummyQPoint(self._x + other.x(), self._y + other.y())

    def __sub__(self, other):
        return DummyQPoint(self._x - other.x(), self._y - other.y())


class DummyQRect:
    def __init__(self, x=0, y=0, w=0, h=0):
        if hasattr(x, "x") and hasattr(x, "y"):  # QRect(QPoint top_left, QSize size)
            self._x = int(x.x())
            self._y = int(x.y())
            # y is size (MagicMock)
            self._w = 100
            self._h = 100
            if hasattr(y, "width"):
                with contextlib.suppress(BaseException):
                    self._w = int(y.width())
            if hasattr(y, "height"):
                with contextlib.suppress(BaseException):
                    self._h = int(y.height())
        else:
            self._x = int(x)
            self._y = int(y)
            self._w = int(w)
            self._h = int(h)

    def x(self):
        return int(self._x)

    def y(self):
        return int(self._y)

    def width(self):
        return int(self._w)

    def height(self):
        return int(self._h)

    def contains(self, *args):
        return False

    def isValid(self):
        return True  # NOSONAR

    def translated(self, x, y):
        if hasattr(x, "x") and hasattr(x, "y"):
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
    StandardButton = DummyEnum  # Expose StandardButton on DummyQWidget

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

    def setLayout(self, layout):  # NOSONAR
        # Mock implementation
        pass

    def layout(self):
        return MagicMock()

    def show(self):
        self._visible = True

    def hide(self):
        self._visible = False

    def setVisible(self, visible):  # NOSONAR
        self._visible = visible

    def showEvent(self, event):  # NOSONAR
        # Mock implementation
        pass

    def closeEvent(self, event):  # NOSONAR
        # Mock implementation
        pass

    def close(self):
        self.closeEvent(None)
        return True

    def isVisible(self):  # NOSONAR
        return getattr(self, "_visible", True)

    def blockSignals(self, block):  # NOSONAR
        return False

    def setUpdatesEnabled(self, enable):  # NOSONAR
        # Mock implementation
        pass

    def setWindowTitle(self, title):  # NOSONAR
        # Mock implementation
        pass

    def setWindowFlags(self, flags):  # NOSONAR
        # Mock implementation
        pass

    def windowFlags(self):  # NOSONAR
        return 0

    def windowState(self):  # NOSONAR
        return DummyEnum.WindowNoState

    def isWindow(self):  # NOSONAR
        return False

    def showMaximized(self):  # NOSONAR
        # Mock implementation
        pass

    def activateWindow(self):  # NOSONAR
        # Mock implementation
        pass

    def setAttribute(self, attr, on=True):  # NOSONAR
        # Mock implementation
        pass

    def raise_(self):
        # Mock implementation
        pass

    def resizeEvent(self, event):  # NOSONAR
        # Mock implementation
        pass

    def resize(self, *args):
        # Mock implementation
        pass

    def size(self):
        return MagicMock()

    def setGeometry(self, *args):  # NOSONAR
        # Mock implementation
        pass

    def geometry(self):
        return DummyQRect(0, 0, 100, 100)

    def pos(self):
        return DummyQPoint(0, 0)

    def move(self, x, y):
        # Mock implementation
        pass

    def setObjectName(self, name):  # NOSONAR
        # Mock implementation
        pass

    def setFixedWidth(self, width):  # NOSONAR
        # Mock implementation
        pass

    def width(self):
        return 100

    def setFixedHeight(self, height):  # NOSONAR
        # Mock implementation
        pass

    def height(self):
        return 100

    def setFixedSize(self, w, h):  # NOSONAR
        # Mock implementation
        pass

    def setMinimumWidth(self, width):  # NOSONAR
        # Mock implementation
        pass

    def setMinimumHeight(self, height):  # NOSONAR
        # Mock implementation
        pass

    def setMinimumDate(self, date):  # NOSONAR
        # Mock implementation
        pass

    def setSpecialValueText(self, text):  # NOSONAR
        # Mock implementation
        pass

    def setMaximumWidth(self, width):  # NOSONAR
        # Mock implementation
        pass

    def setContentsMargins(self, left, t, r, b):  # NOSONAR
        # Mock implementation
        pass

    def setSpacing(self, spacing):  # NOSONAR
        # Mock implementation
        pass

    def setCursor(self, cursor):  # NOSONAR
        # Mock implementation
        pass

    def setMouseTracking(self, enable):  # NOSONAR
        # Mock implementation
        pass

    def setTextInteractionFlags(self, flags):  # NOSONAR
        # Mock implementation
        pass

    def setWordWrap(self, on):  # NOSONAR
        # Mock implementation
        pass

    def setToolTip(self, text):  # NOSONAR
        # Mock implementation
        pass

    def setProperty(self, name, value):  # NOSONAR
        # Mock implementation
        pass

    def property(self, name):
        return "mock_property"

    def findChild(self, type, name=""):  # NOSONAR
        # Return a mock that can handle setText, etc.
        m = MagicMock()
        m.setText = MagicMock()
        return m

    def style(self):
        m = MagicMock()
        m.unpolish = MagicMock()
        m.polish = MagicMock()
        return m

    def addWidget(self, widget, *args, **kwargs):  # NOSONAR
        self.widgets.append(widget)

    def addLayout(self, layout, stretch=0):  # NOSONAR
        # Mock implementation
        pass

    def addStretch(self, stretch=0):  # NOSONAR
        # Mock implementation
        pass

    def itemAt(self, index):  # NOSONAR
        if 0 <= index < len(self.widgets):
            return DummyQLayoutItem(self.widgets[index])
        return None

    def addSpacing(self, spacing):  # NOSONAR
        # Mock implementation
        pass

    def setStretch(self, index, stretch):  # NOSONAR
        # Mock implementation
        pass

    def setEchoMode(self, mode):  # NOSONAR
        # Mock implementation
        pass

    def setPlaceholderText(self, text):  # NOSONAR
        # Mock implementation
        pass

    def setText(self, text):  # NOSONAR
        self._text = text

    def text(self):
        return self._text

    def currentText(self):  # NOSONAR
        return "mock text"

    def currentData(self):  # NOSONAR
        return None

    def currentIndex(self):  # NOSONAR
        return 0

    def addItems(self, items):  # NOSONAR
        self.widgets.extend(items)

    def addItem(self, item, userData=None):  # NOSONAR
        self.widgets.append(item)

    def setFrameShape(self, shape):  # NOSONAR
        # Mock implementation
        pass

    def setFrameShadow(self, shadow):  # NOSONAR
        # Mock implementation
        pass

    def setFieldGrowthPolicy(self, policy):  # NOSONAR
        # Mock implementation
        pass

    def addRow(self, label, field=None):  # NOSONAR
        # Mock implementation
        pass

    def setAlignment(self, alignment):  # NOSONAR
        # Mock implementation
        pass

    def setPixmap(self, pixmap):  # NOSONAR
        # Mock implementation
        pass

    def setCheckable(self, checkable):  # NOSONAR
        # Mock implementation
        pass

    def setIcon(self, icon):  # NOSONAR
        # Mock implementation
        pass

    def setIconSize(self, size):  # NOSONAR
        # Mock implementation
        pass

    def setStyleSheet(self, style):  # NOSONAR
        # Mock implementation
        pass

    def styleSheet(self):  # NOSONAR
        return ""

    def setGraphicsEffect(self, effect):  # NOSONAR
        # Mock implementation
        pass

    def setChecked(self, checked):  # NOSONAR
        self._checked = checked

    def isChecked(self):  # NOSONAR
        return getattr(self, "_checked", True)

    def setCurrentWidget(self, widget):  # NOSONAR
        # Mock implementation
        pass

    def currentWidget(self):  # NOSONAR
        if self.widgets:
            return self.widgets[0]
        return None

    def widget(self, index):
        if 0 <= index < len(self.widgets):
            return self.widgets[index]
        return None

    def count(self):
        return len(self.widgets)

    def setEnabled(self, enabled):  # NOSONAR
        self._enabled = enabled

    def isEnabled(self):  # NOSONAR
        return getattr(self, "_enabled", True)

    def selectionModel(self):  # NOSONAR
        m = MagicMock()
        m.hasSelection.return_value = True
        m.selectedRows.return_value = [DummyQModelIndex(0, 0)]
        m.selectionChanged = DummySignal()
        return m

    def setCurrentIndex(self, index):  # NOSONAR
        # Mock implementation
        pass

    def setAcceptDrops(self, accept):  # NOSONAR
        # Mock implementation
        pass

    def verticalHeader(self):  # NOSONAR
        m = MagicMock()
        m.setDefaultSectionSize = MagicMock()
        return m

    def horizontalHeader(self):  # NOSONAR
        m = MagicMock()
        m.setSectionResizeMode = MagicMock()
        return m

    def setSelectionBehavior(self, behavior):  # NOSONAR
        # Mock implementation
        pass

    def setSelectionMode(self, mode):  # NOSONAR
        # Mock implementation
        pass

    def setEditTriggers(self, triggers):  # NOSONAR
        # Mock implementation
        pass

    def setAlternatingRowColors(self, enable):  # NOSONAR
        # Mock implementation
        pass

    def setModel(self, model):  # NOSONAR
        self._model = model

    def model(self):
        return getattr(self, "_model", None)

    def setColumnHidden(self, col, hidden):  # NOSONAR
        # Mock implementation
        pass

    def selectRow(self, row):  # NOSONAR
        # Mock implementation
        pass

    def setShowGrid(self, show):  # NOSONAR
        # Mock implementation
        pass

    def setEditable(self, editable):  # NOSONAR
        # Mock implementation
        pass

    def setView(self, view):  # NOSONAR
        # Mock implementation
        pass

    def setSizeAdjustPolicy(self, policy):  # NOSONAR
        # Mock implementation
        pass

    def setDisplayFormat(self, format):  # NOSONAR
        # Mock implementation
        pass

    def setCalendarPopup(self, enable):  # NOSONAR
        # Mock implementation
        pass

    def setDate(self, date):  # NOSONAR
        # Mock implementation
        pass

    def date(self):
        return DummyQDate()

    def button(self, which):  # NOSONAR
        return DummyQWidget()

    def adjustSize(self):  # NOSONAR
        # Mock implementation
        pass

    def update(self):
        # Mock implementation
        pass

    def repaint(self):
        # Mock implementation
        pass

    def setCurrentText(self, text):  # NOSONAR
        # Mock implementation
        pass

    def accept(self):
        # Mock implementation
        pass

    def reject(self):
        # Mock implementation
        pass

    def setReadOnly(self, ro):  # NOSONAR
        # Mock implementation
        pass

    def viewport(self):
        m = MagicMock()
        m.mapToGlobal = MagicMock()
        m.width.return_value = 800
        return m

    def indexAt(self, pos):  # NOSONAR
        m = MagicMock()
        m.isValid.return_value = False
        return m

    def setContextMenuPolicy(self, policy):  # NOSONAR
        # Mock implementation
        pass

    def setScene(self, scene):  # NOSONAR
        # Mock implementation
        pass

    def setRange(self, min, max):  # NOSONAR
        # Mock implementation
        pass

    def setTextVisible(self, v):  # NOSONAR
        # Mock implementation
        pass

    def setValue(self, v):  # NOSONAR
        self._value = v

    def value(self):
        return getattr(self, "_value", 0)

    def maximum(self):
        return 100

    def setMaximum(self, m):  # NOSONAR
        # Mock implementation
        pass

    def rect(self):
        # Return a DummyQRect compatible with paintEvent expectations
        return DummyQRect(0, 0, 100, 30)

    def indexOf(self, widget):  # NOSONAR
        if widget in self.widgets:
            return self.widgets.index(widget)
        return -1

    def insertWidget(self, i, w):  # NOSONAR
        # Mock implementation
        pass

    def takeAt(self, i):  # NOSONAR
        return DummyQLayoutItem(MagicMock())

    def setSizes(self, sizes):  # NOSONAR
        # Mock implementation
        pass

    def setHeaderLabels(self, labels):  # NOSONAR
        # Mock implementation
        pass

    def setFont(self, font):  # NOSONAR
        # Mock implementation
        pass

    def clear(self):
        self.widgets = []
        if getattr(self, "_model", None):
            self._model._data = []

    def setStartValue(self, v):  # NOSONAR
        # Mock implementation
        pass

    def setEndValue(self, v):  # NOSONAR
        # Mock implementation
        pass

    def setDuration(self, d):  # NOSONAR
        # Mock implementation
        pass

    def setEasingCurve(self, c):  # NOSONAR
        # Mock implementation
        pass

    def start(self):
        # Mock implementation
        pass

    def stop(self):
        # Mock implementation
        pass

    def valueChanged(self):  # NOSONAR
        return DummySignal()

    def finished(self):
        return DummySignal()

    def clicked(self):
        return self._clicked

    def setSceneRect(self, *args):  # NOSONAR
        # Mock implementation
        pass

    def mapToGlobal(self, pos):  # NOSONAR
        return pos

    def exec(self, *args):
        # Mock implementation
        pass

    def installEventFilter(self, filterObj):  # NOSONAR
        # Mock implementation
        pass

    def setTextFormat(self, fmt):  # NOSONAR
        # Mock implementation
        pass

    def setOpenExternalLinks(self, open):  # NOSONAR
        # Mock implementation
        pass

    def setItemDelegateForColumn(self, col, delegate):  # NOSONAR
        # Mock implementation
        pass

    def parent(self):
        return None

    def window(self):
        return self

    def setWindowOpacity(self, opacity):  # NOSONAR
        self._window_opacity = opacity

    def windowOpacity(self):  # NOSONAR
        return getattr(self, "_window_opacity", 1.0)

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
    def currentIndexChanged(self):  # NOSONAR
        return self._currentIndexChanged

    @builtins.property
    def returnPressed(self):  # NOSONAR
        return self._returnPressed

    @builtins.property
    def textChanged(self):  # NOSONAR
        return self._textChanged

    @builtins.property
    def dateChanged(self):  # NOSONAR
        return self._dateChanged

    @builtins.property
    def resized(self):
        return DummySignal()

    @builtins.property
    def itemClicked(self):  # NOSONAR
        return DummySignal()

    @builtins.property
    def customContextMenuRequested(self):  # NOSONAR
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
    def linkActivated(self):  # NOSONAR
        return DummySignal()


class DummyQMainWindow(DummyQWidget):
    def setCentralWidget(self, widget):  # NOSONAR
        # Mock implementation
        pass


class DummyQDialog(DummyQWidget):
    def exec(self):
        # Mock implementation
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
    def currentDate():  # NOSONAR
        return DummyQDate(datetime.date.today())

    @staticmethod
    def fromString(s, f):  # NOSONAR
        # Basic parsing for "dd/MM/yyyy" which is used in the view
        try:
            if "dd/MM/yyyy" in f:
                d = datetime.datetime.strptime(s, "%d/%m/%Y").date()
                return DummyQDate(d)
        except ValueError:
            pass
        return DummyQDate()

    def addDays(self, days):  # NOSONAR
        return DummyQDate(self._date + datetime.timedelta(days=days))

    def addMonths(self, months):  # NOSONAR
        return DummyQDate(self._date + relativedelta(months=months))

    def setDate(self, y, m, d):  # NOSONAR
        self._date = datetime.date(y, m, d)

    def year(self):
        return self._date.year

    def month(self):
        return self._date.month

    def day(self):
        return self._date.day

    def daysTo(self, other):  # NOSONAR
        if isinstance(other, DummyQDate):
            return (other._date - self._date).days
        return 0

    def toString(self, format_str):  # NOSONAR
        # Simple mapping for common Qt format strings to strftime
        fmt = format_str.replace("dd", "%d").replace("MM", "%m").replace("yyyy", "%Y")
        fmt = fmt.replace("MMM", "%b")  # Abbreviated month
        return self._date.strftime(fmt)

    def toPyDate(self):  # NOSONAR
        return self._date

    def isValid(self):  # NOSONAR
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
    Language = MagicMock()  # NOSONAR
    Country = MagicMock()  # NOSONAR

    def __init__(self, *args):
        pass

    def toString(self, date, fmt):  # NOSONAR
        return "Jan 2025"


class DummyQTreeWidgetItem(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__()
        # Consume parent args to avoid MagicMock confusion if any

    def setData(self, col, role, value):  # NOSONAR
        # Mock implementation
        pass

    def data(self, col, role):  # NOSONAR
        return None


class DummyQGraphicsTextItem(DummyQObject):
    def __init__(self, *args, **kwargs):
        super().__init__()

    def setFont(self, font):  # NOSONAR
        pass

    def setPos(self, x, y):  # NOSONAR
        pass

    def setDefaultTextColor(self, color):  # NOSONAR
        pass

    def setZValue(self, value):  # NOSONAR
        pass

    def boundingRect(self):  # NOSONAR
        m = MagicMock()
        m.width.return_value = 100
        return m


class DummyQGraphicsRectItem(DummyQObject):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self._z = 0

    def setBrush(self, brush):  # NOSONAR
        pass

    def setPen(self, pen):  # NOSONAR
        pass

    def setZValue(self, z):  # NOSONAR
        self._z = z

    def zValue(self):  # NOSONAR
        return self._z

    def setRect(self, x, y, w, h):  # NOSONAR
        pass

    def rect(self):
        m = MagicMock()
        m.x.return_value = 0
        m.width.return_value = 100
        return m

    def setData(self, key, value):  # NOSONAR
        pass

    def setToolTip(self, text):  # NOSONAR
        pass


class DummyQGraphicsLineItem(DummyQObject):
    def __init__(self, *args, **kwargs):
        super().__init__()

    def setPen(self, pen):  # NOSONAR
        pass

    def setLine(self, x1, y1, x2, y2):  # NOSONAR
        pass

    def line(self):
        m = MagicMock()
        m.x1.return_value = 0
        m.x2.return_value = 0
        return m


class DummyQGraphicsScene(DummyQWidget):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self._items = []

    def addItem(self, item):  # NOSONAR
        self._items.append(item)

    def items(self):
        return self._items

    def clear(self):
        self._items = []

    def setSceneRect(self, x, y, w, h):  # NOSONAR
        # Mock implementation
        pass


class DummyQFormLayout(DummyQWidget):
    class FieldGrowthPolicy:
        AllNonFixedFieldsGrow = 1  # NOSONAR


class DummyQTableView(DummyQWidget):
    class SelectionBehavior:
        SelectRows = 1  # NOSONAR

    class SelectionMode:
        ExtendedSelection = 1  # NOSONAR

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setModel_called = False
        self._model_set = None

    def setModel(self, model):  # NOSONAR
        super().setModel(model)
        self.setModel_called = True
        self._model_set = model


class DummyQHeaderView(DummyQWidget):
    class ResizeMode:
        ResizeToContents = 0  # NOSONAR
        Stretch = 1  # NOSONAR


class DummyQWebEngineView(DummyQWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.url = None
        self.html = None

    def setUrl(self, url):  # NOSONAR
        self.url = url

    def setHtml(self, html, baseUrl=None):  # NOSONAR
        self.html = html

    def page(self):
        page = MagicMock()
        return page

    def setPage(self, page):  # NOSONAR
        # Mock implementation
        pass


class DummyQWebEnginePage(DummyQWidget):
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):  # NOSONAR
        # Mock implementation
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
    mock_core.PYQT_VERSION = 0x060800  # Mock version 6.8.0
    mock_core.Qt = DummyEnum  # Use Enum
    mock_core.QSize = MagicMock()
    mock_core.QDate = DummyQDate
    mock_core.QObject = DummyQObject
    mock_core.QAbstractTableModel = DummyQAbstractTableModel
    mock_widgets.QAbstractItemView = (
        DummyQWidget  # Use DummyQWidget as base for QAbstractItemView enum access
    )
    mock_core.QTimer = MagicMock()
    mock_core.QCoreApplication = MagicMock()

    class DummyQPropertyAnimation(MagicMock):
        def __init__(self, target=None, prop_name=None, parent=None, **kwargs):
            super().__init__(**kwargs)
            self._finished = DummySignal()

        @property
        def finished(self):
            return self._finished

        def setStartValue(self, v):
            pass  # NOSONAR

        def setEndValue(self, v):
            pass  # NOSONAR

        def setDuration(self, d):
            pass  # NOSONAR

        def setEasingCurve(self, c):
            pass  # NOSONAR

        def state(self):
            return 0  # Stopped

        def start(self):
            # Auto-finish for tests
            self._finished.emit()

        def stop(self):
            pass

    mock_core.QPropertyAnimation = DummyQPropertyAnimation
    mock_core.QEasingCurve = MagicMock()
    mock_core.pyqtSignal = DummyPyQtSignal

    def dummy_pyqtSlot(*args, **kwargs):  # NOSONAR
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

        def quit(self):
            pass

        def wait(self):
            pass

        def isRunning(self):
            return False  # NOSONAR

        def run(self):
            pass

        @staticmethod
        def currentThread():  # NOSONAR
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
        "PyQt6": mock_pyqt6,
        "PyQt6.QtWidgets": mock_widgets,
        "PyQt6.QtCore": mock_core,
        "PyQt6.QtGui": mock_gui,
        "PyQt6.QtWebEngineWidgets": mock_web,
        "PyQt6.QtWebEngineCore": mock_web_core,
        "PyQt6.QtWebChannel": mock_webchannel,
        "PyQt6.QtMultimedia": mock_media,
        "PyQt6.QtPrintSupport": MagicMock(),
        "PyQt6.QtNetwork": MagicMock(),
    }


# Create the mock modules
mock_modules = mock_qt_modules()
QtWidgets = mock_modules["PyQt6.QtWidgets"]
QtCore = mock_modules["PyQt6.QtCore"]
