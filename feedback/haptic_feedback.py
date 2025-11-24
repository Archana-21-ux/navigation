from gpiozero import PWMOutputDevice
import time
import threading


class HapticFeedback:
    def __init__(self):
        # GPIO pins: 17 = left, 27 = right, 22 = center
        self.left = PWMOutputDevice(17)
        self.right = PWMOutputDevice(27)
        self.center = PWMOutputDevice(22)

    def vibrate_left(self, level: str):
        threading.Thread(target=self._vibrate, args=(self.left, level), daemon=True).start()

    def vibrate_right(self, level: str):
        threading.Thread(target=self._vibrate, args=(self.right, level), daemon=True).start()

    def vibrate_center(self, level: str):
        threading.Thread(target=self._vibrate, args=(self.center, level), daemon=True).start()

    def _vibrate(self, motor: PWMOutputDevice, level: str):
        if level == "strong":
            # Two short strong pulses
            for _ in range(2):
                motor.value = 1.0
                time.sleep(0.3)
                motor.value = 0
                time.sleep(0.1)

        elif level == "short":
            motor.value = 1.0
            time.sleep(0.15)
            motor.value = 0

    def stop_all(self):
        """Turn off all motors (call on shutdown)."""
        self.left.value = 0
        self.right.value = 0
        self.center.value = 0
