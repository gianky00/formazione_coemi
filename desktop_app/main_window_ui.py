    def cleanup(self):
        """
        Cleanup all background threads and child views.
        """
        # Stop System Check Thread
        if hasattr(self, 'check_thread') and self.check_thread.isRunning():
            print("[Dashboard] Stopping system check thread...")
            self.check_thread.quit()
            if not self.check_thread.wait(2000):
                 self.check_thread.terminate()

        # Cleanup Child Views
        for key, view in self.views.items():
            if view and hasattr(view, 'cleanup'):
                print(f"[Dashboard] Cleaning up view: {key}")
                try:
                    view.cleanup()
                except Exception as e:
                    print(f"[Dashboard] Error cleaning up {key}: {e}")

        # Worker Manager Global Cleanup
        try:
            from desktop_app.services.worker_manager import WorkerManager
            WorkerManager.instance().stop_all()
        except Exception as e:
            print(f"[Dashboard] WorkerManager cleanup failed: {e}")
