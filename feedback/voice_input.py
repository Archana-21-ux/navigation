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
        
        print(prompt_text)  

        start_time = time.time()

        while True:
            if timeout is not None and (time.time() - start_time) > timeout
                return ""

            data = self.stream.read(self.chunk_size, exception_on_overflow=False)

            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                text = result.get("text", "").strip()
                if text:
                    return text

    def close(self):
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
