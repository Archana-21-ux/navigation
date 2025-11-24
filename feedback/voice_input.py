import vosk
import json
import pyaudio
import time
from typing import Optional


class VoiceInput:
    def __init__(
        self,
        model_path: str = "models/vosk-model-small-en-us-0.15",
        rate: int = 16000,
        chunk_size: int = 4000,
    ):
        """
        Offline speech recognition using Vosk.

        model_path: path to Vosk acoustic model directory
        rate: audio sample rate (Hz)
        chunk_size: number of frames to read per chunk
        """
        self.model = vosk.Model(model_path)
        self.rate = rate
        self.chunk_size = chunk_size

        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.rate,
            input=True,
            frames_per_buffer=8000,
        )
        self.stream.start_stream()

        self.recognizer = vosk.KaldiRecognizer(self.model, self.rate)

    def listen_for_destination(
        self,
        prompt_text: str = "Where do you want to go?",
        timeout: Optional[float] = 10.0,
    ) -> str:
        """
        Listens for a spoken destination and returns recognized text.

        This is a blocking call intended to be triggered (e.g., by a button).
        It returns either:
          - recognized text (lowercase string)
          - "" if nothing was understood before timeout

        timeout:
            - if None: wait indefinitely until something is spoken
            - if float: maximum number of seconds to wait
        """
        print(prompt_text)  # In production, your TTS already speaks the prompt.

        start_time = time.time()

        while True:
            if timeout is not None and (time.time() - start_time) > timeout:
                # No speech recognized within timeout
                return ""

            data = self.stream.read(self.chunk_size, exception_on_overflow=False)

            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                text = result.get("text", "").strip()
                if text:
                    return text

    def close(self):
        """
        Release audio resources. Call this once when shutting down the system.
        """
        try:
            if self.stream is not None:
                self.stream.stop_stream()
                self.stream.close()
        except Exception:
            pass

        try:
            if self.audio is not None:
                self.audio.terminate()
        except Exception:
            pass
