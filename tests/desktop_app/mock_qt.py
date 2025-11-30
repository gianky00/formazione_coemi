import sys
import builtins
from unittest.mock import MagicMock

class DummySignal:
    def __init__(self):
        self._slots = []

    def connect(self, slot):
        self._slots.append(slot)

    def emit(self, *args, **kwargs):
        for slot in self._slots:
            slot(*args, **kwargs)

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

class DummyEnum:
    StyledPanel = 1
    Sunken = 1
    Password = 1
    Plain = 0
    HLine = 1
    Ok = 1
    Cancel = 2
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
    AA_ShareOpenGLContexts = 0
    DisplayRole = 0
    EditRole = 1
    UserRole = 256
    WindowActive = 1
    KeepAspectRatio = 1
    CustomContextMenu = 1
    SmoothTransformation = 1
    TextSelectableByMouse = 1

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

class DummyQAbstractTableModel(MagicMock):
    def __init__(self, *args, **kwargs):
        # Consume parent arg safely
        parent = kwargs.pop('parent', None)
        super().__init__(*args, **kwargs)

    def index(self, row, column, parent=None):
        return DummyQModelIndex(row, column)

class DummyQWidget:
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

    def __init__(self, text=None, *args, **kwargs):
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
        pass
    def hide(self):
        pass
    def setVisible(self, visible):
        pass
    def setWindowTitle(self, title):
        pass
    def setWindowFlags(self, flags):
        pass
    def windowFlags(self):
        return 0
    def setAttribute(self, attr, on):
        pass
    def raise_(self):
        pass
    def resize(self, w, h):
        pass
    def setGeometry(self, *args):
        pass
    def geometry(self):
        return MagicMock()
    def pos(self):
        return MagicMock()
    def move(self, x, y):
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
    def setMaximumWidth(self, width):
        pass
    def setContentsMargins(self, l, t, r, b):
        pass
    def setSpacing(self, spacing):
        pass
    def setCursor(self, cursor):
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
        pass
    def addItem(self, item, userData=None):
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
    def styleSheet(self):
        return ""
    def setGraphicsEffect(self, effect):
        pass
    def setChecked(self, checked):
        pass
    def isChecked(self):
        return True
    def setCurrentWidget(self, widget):
        pass
    def count(self):
        return len(self.widgets)
    def setEnabled(self, enabled):
        pass
    def selectionModel(self):
        m = MagicMock()
        m.hasSelection.return_value = True
        m.selectedRows.return_value = [1]
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
        pass
    def setMaximum(self, m):
        pass
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
        pass
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

class DummyQMainWindow(DummyQWidget):
    def setCentralWidget(self, widget):
        pass

class DummyQDialog(DummyQWidget):
    def exec(self):
        pass

class DummyQObject:
    def __init__(self, parent=None):
        pass
    def moveToThread(self, thread):
        pass
    def deleteLater(self):
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

    def toPyDate(self):
        from datetime import date
        return date.today()

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

class DummyQWebEngineView(DummyQWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.url = None
        self.html = None
    def setUrl(self, url):
        self.url = url
    def setHtml(self, html):
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
    mock_widgets.QFormLayout = DummyQFormLayout
    mock_widgets.QStackedWidget = DummyQWidget
    mock_widgets.QMessageBox = MagicMock()
    mock_widgets.QTableView = DummyQTableView
    mock_widgets.QHeaderView = DummyQHeaderView
    mock_widgets.QDateEdit = DummyQWidget
    mock_widgets.QCheckBox = DummyQWidget
    mock_widgets.QDialogButtonBox = DummyQWidget
    mock_widgets.QListView = DummyQWidget
    mock_widgets.QTreeWidget = DummyQWidget
    mock_widgets.QTreeWidgetItem = MagicMock
    mock_widgets.QSplitter = DummyQWidget
    mock_widgets.QGraphicsView = DummyQWidget
    mock_widgets.QGraphicsScene = DummyQWidget
    mock_widgets.QGraphicsRectItem = MagicMock
    mock_widgets.QGraphicsTextItem = MagicMock
    mock_widgets.QGraphicsLineItem = MagicMock
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
    mock_core.Qt = DummyQWidget # Reuse Enum
    mock_core.QSize = MagicMock()
    mock_core.QDate = DummyQDate
    mock_core.QObject = DummyQObject
    mock_core.QAbstractTableModel = DummyQAbstractTableModel
    mock_core.QTimer = MagicMock()
    mock_core.QPropertyAnimation = MagicMock()
    mock_core.QEasingCurve = MagicMock()
    mock_core.pyqtSignal = DummyPyQtSignal
    mock_core.QThreadPool = MagicMock()
    mock_core.QThread = MagicMock()
    mock_core.QRunnable = MagicMock
    mock_core.QPoint = MagicMock()
    mock_core.QRect = MagicMock()
    mock_core.QRectF = MagicMock()
    mock_core.QVariantAnimation = MagicMock()
    mock_core.QParallelAnimationGroup = MagicMock()

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

    return {
        'PyQt6.QtWidgets': mock_widgets,
        'PyQt6.QtCore': mock_core,
        'PyQt6.QtGui': mock_gui,
        'PyQt6.QtWebEngineWidgets': mock_web,
        'PyQt6.QtWebEngineCore': mock_web_core,
        'PyQt6.QtWebChannel': mock_webchannel,
        'PyQt6.QtPrintSupport': MagicMock(),
        'PyQt6.QtNetwork': MagicMock(),
    }

# Create the mock modules
mock_modules = mock_qt_modules()
QtWidgets = mock_modules['PyQt6.QtWidgets']
QtCore = mock_modules['PyQt6.QtCore']
