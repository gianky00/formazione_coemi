"""
CSV Import Worker - Background thread for employee CSV import.
Prevents UI freezes and provides robust error handling.
"""

from PyQt6.QtCore import QThread, pyqtSignal
import sentry_sdk
import logging

logger = logging.getLogger(__name__)


class CSVImportWorker(QThread):
    """
    Worker thread for importing CSV files without blocking the UI.
    
    Signals:
        finished_success(dict): Emitted with response data on success
        finished_error(str): Emitted with error message on failure
        progress(int): Emitted with progress percentage (0-100)
    """
    finished_success = pyqtSignal(dict)
    finished_error = pyqtSignal(str)
    progress = pyqtSignal(int)
    
    def __init__(self, api_client, file_path, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.file_path = file_path
        self._is_cancelled = False
    
    def cancel(self):
        """Request cancellation of the import."""
        self._is_cancelled = True
    
    def run(self):
        """Execute the CSV import in background thread."""
        try:
            self.progress.emit(10)
            
            if self._is_cancelled:
                self.finished_error.emit("Importazione annullata")
                return
            
            self.progress.emit(30)
            
            # Perform the actual import
            response = self.api_client.import_dipendenti_csv(self.file_path)
            
            self.progress.emit(90)
            
            if self._is_cancelled:
                self.finished_error.emit("Importazione annullata")
                return
            
            # Ensure response is a dict
            if not isinstance(response, dict):
                response = {"message": str(response) if response else "Importazione completata"}
            
            self.progress.emit(100)
            self.finished_success.emit(response)
            
        except Exception as e:
            logger.error(f"CSV Import error: {e}", exc_info=True)
            sentry_sdk.capture_exception(e)
            
            # Extract detailed error message
            error_msg = self._extract_error_message(e)
            self.finished_error.emit(error_msg)
    
    def _extract_error_message(self, exception):
        """Extract a user-friendly error message from an exception."""
        error_msg = str(exception)
        
        if hasattr(exception, 'response') and exception.response is not None:
            try:
                response_json = exception.response.json()
                if isinstance(response_json, dict):
                    detail = response_json.get('detail')
                    if detail:
                        error_msg = str(detail)
                else:
                    error_msg = str(response_json)
            except Exception:
                if hasattr(exception.response, 'text'):
                    text = exception.response.text
                    error_msg = text[:500] if len(text) > 500 else text
        
        return error_msg
