import pyttsx3
import threading
import queue
import time


class VoiceFeedback:
    def __init__(self):
        # TTS engine
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 150)

        # Priority queue: (priority_value, counter, text)
        self.queue: "queue.PriorityQueue[tuple[int, int, str]]" = queue.PriorityQueue()

        # For ordering within same priority
        self._counter = 0

        # For deduplication
        self._last_spoken_text: str | None = None
        self._last_spoken_time: float = 0.0
        self._dedupe_window_sec: float = 2.0  # ignore same text within 2 seconds

        # Background worker thread
        self.worker = threading.Thread(target=self._run, daemon=True)
        self.worker.start()

        # Lock for shared state
        self._lock = threading.Lock()

    def _priority_value(self, priority: str) -> int:
        """
        Map priority string to numeric value: lower = higher priority.
        """
        mapping = {"high": 0, "normal": 1, "low": 2}
        return mapping.get(priority, 1)

    def _run(self):
        """
        Worker loop: speak messages from the queue one by one.
        """
        while True:
            priority_value, _, text = self.queue.get()  # blocks until message

            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception:
                # Avoid crashing system due to audio backend issues
                pass

            # Update last spoken info (for dedupe)
            with self._lock:
                self._last_spoken_text = text
                self._last_spoken_time = time.time()

            time.sleep(0.05)  # tiny gap for stability

    def speak(
        self,
        text: str,
        priority: str = "normal",
        interrupt: bool = False,
        allow_repeat: bool = False,
    ):
        """
        Queue a message to be spoken.

        - priority: "high", "normal", "low"
        - interrupt: if True, stops current speech & clears queued low-priority messages
        - allow_repeat: if False, same text within a short window is ignored
        """
        now = time.time()

        # De-duplication: avoid spamming the same message every frame
        if not allow_repeat:
            with self._lock:
                if (
                    self._last_spoken_text == text
                    and (now - self._last_spoken_time) < self._dedupe_window_sec
                ):
                    return  # skip repeating the same line too soon

        if interrupt:
            # Try to stop current speech and flush queue
            try:
                self.engine.stop()
            except Exception:
                pass

            # Clear queued lower-priority messages
            try:
                while True:
                    self.queue.get_nowait()
            except queue.Empty:
                pass

        # Enqueue the new message
        with self._lock:
            self._counter += 1
            counter = self._counter

        priority_value = self._priority_value(priority)
        self.queue.put((priority_value, counter, text))
