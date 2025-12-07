from PyQt6.QtCore import QThread, pyqtSignal
import os

class FileScannerWorker(QThread):
    finished = pyqtSignal(list)

    def __init__(self, urls):
        super().__init__()
        self.urls = urls

    def _process_url(self, url):
        """Helper to process a single URL."""
        if not url.isLocalFile():
            return []

        path = url.toLocalFile()
        found_files = []

        if os.path.isfile(path) and path.lower().endswith('.pdf'):
            found_files.append(path)
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.lower().endswith('.pdf'):
                        found_files.append(os.path.join(root, file))
        return found_files

    def run(self):
        # S3776: Refactored to reduce complexity
        files_to_process = []
        for url in self.urls:
            files_to_process.extend(self._process_url(url))
        self.finished.emit(files_to_process)
