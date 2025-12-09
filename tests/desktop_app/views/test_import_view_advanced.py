import unittest
from unittest.mock import MagicMock, patch, ANY, mock_open
import sys
import os

# Patch PyQt
from tests.desktop_app.mock_qt import DummyQWidget, DummySignal, DummyQObject

mock_qt = MagicMock()
mock_qt.QWidget = DummyQWidget

# Define a MockWidget that ignores constructor args to prevent MagicMock spec interpretation
class MockWidget(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__()

# Define QFrame
class DummyFrame(DummyQWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
    def setFrameShape(self, shape): pass
    def setFrameShadow(self, shadow): pass
    class Shape: StyledPanel=1
    class Shadow: Sunken=1

mock_qt.QFrame = DummyFrame
mock_qt.QVBoxLayout = MockWidget
mock_qt.QHBoxLayout = MockWidget
mock_qt.QLabel = MockWidget
mock_qt.QPushButton = MockWidget
mock_qt.QTextEdit = MockWidget
mock_qt.QProgressBar = MockWidget
mock_qt.QFileDialog = MockWidget
mock_qt.QVariantAnimation = MockWidget
mock_qt.QThread = MockWidget

# Need flexible signal
class FlexibleDummySignal(DummySignal):
    def __init__(self, *args, **kwargs):
        super().__init__()

mock_qt.pyqtSignal = FlexibleDummySignal
mock_qt.QObject = DummyQObject
mock_qt.Qt.AlignmentFlag.AlignCenter = 1
mock_qt.QColor = MagicMock()
mock_qt.QIcon = MagicMock()
mock_qt.QSize = MagicMock()

# Patch sys.modules
sys.modules['PyQt6.QtWidgets'] = mock_qt
sys.modules['PyQt6.QtCore'] = mock_qt
sys.modules['PyQt6.QtGui'] = mock_qt

# Patch dependencies
sys.modules['desktop_app.components.toast'] = MagicMock()
sys.modules['desktop_app.components.animated_widgets'] = MagicMock()
sys.modules['desktop_app.components.visuals'] = MagicMock()
sys.modules['desktop_app.workers.file_scanner_worker'] = MagicMock()
sys.modules['app.utils.file_security'] = MagicMock()
sys.modules['app.utils.file_security'].sanitize_filename = lambda x: x.replace(" ", "_")

# Import view
from desktop_app.views.import_view import ImportView, DropZone, PdfWorker

class TestImportViewAdvanced(unittest.TestCase):
    def setUp(self):
        # Patch APIClient in ImportView import
        with patch('desktop_app.views.import_view.APIClient') as MockClient:
            self.mock_client_instance = MockClient.return_value
            self.mock_client_instance.get_paths.return_value = {"database_path": "/tmp/db"}
            self.view = ImportView()
            
            # Monkeypatch parent() for drop_zone since DummyQWidget doesn't have it
            self.view.drop_zone.parent = MagicMock(return_value=self.view)

    def test_process_dropped_files_start(self):
        """Test that processing starts correctly - now uses async Worker pattern."""
        files = ["/tmp/test.pdf"]
        
        self.view.results_display.setTextColor = MagicMock()
        self.view.results_display.append = MagicMock()

        self.mock_client_instance.get_paths.return_value = {"database_path": "/tmp/db"}

        # Patch the Worker and QThreadPool since processing is now async
        # Worker is imported from desktop_app.workers.worker inside the method
        with patch('desktop_app.workers.worker.Worker') as MockWorker, \
             patch('PyQt6.QtCore.QThreadPool') as MockThreadPool:
            self.view.process_dropped_files(files)
            
            # Verify that a Worker was created to fetch paths asynchronously
            MockWorker.assert_called()
            MockThreadPool.globalInstance().start.assert_called()
            # `patch('os.path.isdir')` patches the real `os.path`.
            # But if `import_view.py` does `from os import path`, then we need to patch `path`.
            # It does `import os`. So `os.path.isdir`.
            
            # Let's try patching `desktop_app.views.import_view.os.path.isdir` specifically just in case.
            pass

    @patch('desktop_app.views.import_view.requests.post')
    def test_pdf_worker_process_success(self, m_post):
        """Test PdfWorker successfully processes a file."""
        worker = PdfWorker(["/tmp/test.pdf"], self.mock_client_instance, "/tmp/out")
        
        # Setup signals
        worker.log_message = MagicMock()
        worker.finished = MagicMock()
        
        # Mock upload response
        upload_resp = MagicMock()
        upload_resp.status_code = 200
        upload_resp.json.return_value = {
            "entities": {
                "nome": "Mario Rossi",
                "matricola": "123",
                "categoria": "HLO",
                "data_scadenza": "31/12/2030"
            }
        }
        
        # Mock save response
        save_resp = MagicMock()
        save_resp.status_code = 200
        save_resp.json.return_value = {
            "nome": "Mario Rossi",
            "matricola": "123",
            "categoria": "HLO",
            "data_scadenza": "31/12/2030"
        }
        
        m_post.side_effect = [upload_resp, save_resp]
        
        with patch('builtins.open', mock_open(read_data=b"pdf_content")):
            with patch('shutil.move') as m_move:
                worker.process_pdf("/tmp/test.pdf")
                
                # Check log success
                worker.log_message.emit.assert_any_call(ANY, "default")
                # Check file move to success folder
                m_move.assert_called()
                args = m_move.call_args[0]
                self.assertIn("DOCUMENTI DIPENDENTI", args[1])

    @patch('desktop_app.views.import_view.requests.post')
    def test_pdf_worker_upload_failure(self, m_post):
        """Test PdfWorker handles upload failure."""
        worker = PdfWorker(["/tmp/test.pdf"], self.mock_client_instance, "/tmp/out")
        worker.log_message = MagicMock()
        
        resp = MagicMock()
        resp.status_code = 500
        resp.text = "Server Error"
        m_post.return_value = resp
        
        with patch('builtins.open', mock_open(read_data=b"pdf")):
            with patch('shutil.move') as m_move:
                worker.process_pdf("/tmp/test.pdf")
                
                worker.log_message.emit.assert_called_with(ANY, "red")
                # Check move to error folder
                args = m_move.call_args[0]
                self.assertIn("ERRORI ANALISI", args[1])

    def test_stop_processing(self):
        pass
