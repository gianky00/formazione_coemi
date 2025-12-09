from PyQt6.QtCore import QObject, QThread, pyqtSignal, QMutex, QMutexLocker
import logging

logger = logging.getLogger(__name__)

class WorkerManager(QObject):
    _instance = None

    def __init__(self):
        super().__init__()
        self._workers = set()
        self._mutex = QMutex()

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = WorkerManager()
        return cls._instance

    def register_worker(self, worker: QThread):
        """
        Registers a worker thread to ensure it is tracked and can be cleaned up.
        """
        if not worker or not isinstance(worker, QThread):
            return

        with QMutexLocker(self._mutex):
            self._workers.add(worker)
            # Auto-unregister on finish
            worker.finished.connect(lambda: self.unregister_worker(worker))
            logger.debug(f"Worker registered: {worker}")

    def unregister_worker(self, worker: QThread):
        """
        Removes a worker from tracking.
        """
        with QMutexLocker(self._mutex):
            if worker in self._workers:
                self._workers.remove(worker)
                logger.debug(f"Worker unregistered: {worker}")

    def stop_all(self):
        """
        Stops all registered workers gracefully.
        """
        logger.info("Stopping all workers...")
        with QMutexLocker(self._mutex):
            workers_copy = list(self._workers)

        for worker in workers_copy:
            if worker.isRunning():
                logger.debug(f"Stopping worker: {worker}")
                worker.quit()
                if not worker.wait(2000): # 2s timeout
                    logger.warning(f"Worker {worker} did not stop. Terminating.")
                    worker.terminate()

        with QMutexLocker(self._mutex):
            self._workers.clear()
        logger.info("All workers stopped.")
