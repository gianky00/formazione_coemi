# Desktop UI Constants

# Colors
COLOR_WHITE = "#FFFFFF"
COLOR_TEXT_PRIMARY = "#1F2937"
COLOR_TEXT_SECONDARY = "#6B7280"
COLOR_BORDER = "#E5E7EB"
COLOR_ACCENT_BLUE = "#3B82F6"
COLOR_ACCENT_BLUE_LIGHT = "#93C5FD"
COLOR_ERROR_RED = "#DC2626"
COLOR_WARNING_ORANGE = "#D97706"
COLOR_SUCCESS_GREEN = "#10B981"
COLOR_WARNING_YELLOW_TEXT = "#FBBF24"

# Stylesheets
STYLE_QFRAME_CARD = """
    QFrame {
        background-color: #FFFFFF;
        border-radius: 12px;
        border: 1px solid #E5E7EB;
    }
"""

STYLE_LICENSE_VALID = "color: #93C5FD; font-size: 13px; font-weight: 500;"
STYLE_LICENSE_EXPIRING = "color: #FBBF24; font-size: 13px; font-weight: 600;"

# Formats
DATE_FORMAT_DISPLAY = "dd/MM/yyyy"
DATE_FORMAT_FILE = "%d_%m_%Y"

# Status Messages
STATUS_READ_ONLY = "Database in sola lettura"
STATUS_EXPIRING_SOON = "IN SCADENZA"
STATUS_ACTIVE = "ATTIVO"
STATUS_EXPIRED = "SCADUTI"

# Labels
LABEL_OPTIMIZE_DB = "Ottimizza Database Ora"
LABEL_LICENSE_EXPIRY = "Scadenza Licenza"
LABEL_HARDWARE_ID = "Hardware ID"

# Paths/Directories
DIR_ANALYSIS_ERRORS = "ERRORI ANALISI"
FILE_REQUIREMENTS = "requirements.txt"
FILE_MANIFEST = "manifest.json"
FILE_PYARMOR_KEY = "pyarmor.rkey"
FILE_CONFIG_DAT = "config.dat"
