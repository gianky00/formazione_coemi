from PyQt6.QtCore import QThread, pyqtSignal
import os

class FileScannerWorker(QThread):
    finished = pyqtSignal(list)

    def __init__(self, urls):
        super().__init__()
        self.urls = urls

    def run(self):
        files_to_process = []
        for url in self.urls:
            if url.isLocalFile():
                path = url.toLocalFile()
                if os.path.isfile(path) and path.lower().endswith('.pdf'):
                    files_to_process.append(path)
                elif os.path.isdir(path):
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            if file.lower().endswith('.pdf'):
                                files_to_process.append(os.path.join(root, file))
        self.finished.emit(files_to_process)
