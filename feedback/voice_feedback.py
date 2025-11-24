import pyttsx3
import threading
import queue
import time


class VoiceFeedback:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 150)

        self.queue: "queue.PriorityQueue[tuple[int, int, str]]" = queue.PriorityQueue()

        self._counter = 0

        self._last_spoken_text: str | None = None
        self._last_spoken_time: float = 0.0
        self._dedupe_window_sec: float = 2.0  
        
        self.worker = threading.Thread(target=self._run, daemon=True)
        self.worker.start()

        self._lock = threading.Lock()

    def _priority_value(self, priority: str) -> int:
       
        mapping = {"high": 0, "normal": 1, "low": 2}
        return mapping.get(priority, 1)

    def _run(self):
            while True:
            priority_value, _, text = self.queue.get()  

            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception:
                pass

            with self._lock:
                self._last_spoken_text = text
                self._last_spoken_time = time.time()

            time.sleep(0.05)  

    def speak(
        self,
        text: str,
        priority: str = "normal",
        interrupt: bool = False,
        allow_repeat: bool = False,
    ):
       
        now = time.time()

        if not allow_repeat:
            with self._lock:
                if (
                    self._last_spoken_text == text
                    and (now - self._last_spoken_time) < self._dedupe_window_sec
                ):
                    return  
        if interrupt:
            
            try:
                self.engine.stop()
            except Exception:
                pass

           
            try:
                while True:
                    self.queue.get_nowait()
            except queue.Empty:
                pass

        with self._lock:
            self._counter += 1
            counter = self._counter

        priority_value = self._priority_value(priority)
        self.queue.put((priority_value, counter, text))
