import threading
import tkinter as tk
from tkinter import scrolledtext


class ChatView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#F3F4F6")

        self.setup_ui()
        self.history = []

    def setup_ui(self):
        # Header
        header = tk.Frame(self, bg="#1E3A8A", height=50)
        header.pack(fill="x")
        tk.Label(
            header,
            text="Lyra - Assistente Virtuale",
            bg="#1E3A8A",
            fg="white",
            font=("Segoe UI", 12, "bold"),
        ).pack(pady=10)

        # Chat History
        self.txt_history = scrolledtext.ScrolledText(
            self, state="disabled", wrap="word", font=("Segoe UI", 10)
        )
        self.txt_history.pack(fill="both", expand=True, padx=10, pady=10)

        # Input Area
        input_frame = tk.Frame(self, bg="#F3F4F6")
        input_frame.pack(fill="x", padx=10, pady=10)

        self.entry_msg = tk.Entry(input_frame, font=("Segoe UI", 10))
        self.entry_msg.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_msg.bind("<Return>", lambda e: self.send_message())

        btn_send = tk.Button(
            input_frame, text="Invia", bg="#1D4ED8", fg="white", command=self.send_message
        )
        btn_send.pack(side="right")

    def append_message(self, sender, text):
        self.txt_history.config(state="normal")
        tag = "user" if sender == "Tu" else "bot"

        self.txt_history.insert("end", f"{sender}: ", (tag + "_label",))
        self.txt_history.insert("end", f"{text}\n\n", (tag,))

        # Styling
        self.txt_history.tag_config(
            "user_label", foreground="#1D4ED8", font=("Segoe UI", 10, "bold")
        )
        self.txt_history.tag_config(
            "bot_label", foreground="#059669", font=("Segoe UI", 10, "bold")
        )

        self.txt_history.see("end")
        self.txt_history.config(state="disabled")

    def send_message(self):
        msg = self.entry_msg.get().strip()
        if not msg:
            return

        self.entry_msg.delete(0, "end")
        self.append_message("Tu", msg)

        # Send to API in background
        # Note: Chat can be slow, but blocking the whole UI for a chat might be annoying.
        # However, for stability, we use TaskRunner if we want to be safe,
        # OR we use a simple thread that updates UI via after().
        # Given "stability first" mantra, I will use a non-blocking thread for chat
        # because blocking the UI for LLM generation (seconds) makes the chat unusable.
        # But I must ensure thread safety. Tkinter is NOT thread safe.
        # So the thread must queue the result or use after().

        threading.Thread(target=self._chat_worker, args=(msg,), daemon=True).start()

    def _chat_worker(self, message):
        try:
            # Prepare history (last 10 messages)
            hist_payload = self.history[-10:]

            response = self.controller.api_client.send_chat_message(message, history=hist_payload)
            reply = response.get("response", "")

            # Update history
            self.history.append({"role": "user", "content": message})
            self.history.append({"role": "model", "content": reply})

            # Update UI on main thread
            self.after(0, lambda: self.append_message("Lyra", reply))

            # Voice feedback (optional)
            if hasattr(self.controller, "voice_service") and self.controller.voice_service:
                self.after(0, lambda: self.controller.voice_service.speak(reply))

        except Exception as e:
            self.after(0, lambda e=str(e): self.append_message("Sistema", f"Errore: {e}"))
