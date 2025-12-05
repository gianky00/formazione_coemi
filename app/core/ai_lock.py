import threading

# Global lock to prevent race conditions between Chat and Extraction services
# when configuring the global genai library.
ai_global_lock = threading.RLock()
