import threading
import signal
import sys
import time

from picamera2 import Picamera2

from object_detection.yolo_detector import YOLODetector
from distance_estimation.distance_estimator import DistanceEstimator
from feedback.haptic_feedback import HapticFeedback
from feedback.voice_feedback import VoiceFeedback
from feedback.voice_input import VoiceInput
from navigation.route_planner import RoutePlanner
from gps_reader import GPSReader
from utils.helpers import log


class BlindNavigationSystem:
    def __init__(self):
        # --- Camera setup (Picamera2) ---
        self.camera = Picamera2()
        # Lower resolution → faster inference
        config = self.camera.create_preview_configuration(main={"size": (320, 240)})
        self.camera.configure(config)
        self.camera.start()

        # --- Core modules ---
        self.yolo = YOLODetector()
        self.depth = DistanceEstimator()
        self.haptic = HapticFeedback()
        self.voice = VoiceFeedback()
        self.voice_input = VoiceInput()
        self.gps = GPSReader()
        self.route_planner = None

        self.running = True
        self.current_step = None

        # Graceful Ctrl+C
        signal.signal(signal.SIGINT, self.shutdown)

    def startup(self):
        log("Initializing system...")
        self.voice.speak(
            "System starting. Where do you want to go?",
            priority="normal",
            allow_repeat=True,
        )

        destination = self.voice_input.listen_for_destination()
        if not destination:
            self.voice.speak(
                "No destination heard. Exiting.",
                priority="normal",
                allow_repeat=True,
            )
            sys.exit(1)

        self.voice.speak(
            f"Navigating to {destination}",
            priority="normal",
            allow_repeat=True,
        )

        current_pos = self.gps.get_current_position()
        if not current_pos:
            self.voice.speak(
                "GPS not available. Exiting.",
                priority="high",
                interrupt=True,
                allow_repeat=True,
            )
            sys.exit(1)

        self.route_planner = RoutePlanner()
        self.route_planner.plan_route(current_pos, destination)
        self.current_step = self.route_planner.get_next_instruction(current_pos)

        log("Startup complete.")

    def vision_loop(self):
        """
        Continuous camera monitoring for obstacle detection.
        Center motor vibrates for any obstacle.
        """
        while self.running:
            frame = self.camera.capture_array()  # NumPy array (H, W, 3)

            # YOLO detections
            detections = self.yolo.detect(frame)

            # Depth estimation for each detection
            obstacle_info = self.depth.estimate_distance(frame, detections)

            if obstacle_info:
                # Pick the closest object
                closest = min(obstacle_info, key=lambda x: x[1])
                det, dist, is_obstacle = closest

                if is_obstacle:
                    # Only center vibrates for any obstacle
                    if dist < 0.7:
                        self.haptic.vibrate_center("strong")
                        self.voice.speak(
                            "Obstacle ahead, stop!",
                            priority="high",
                            interrupt=True,
                            allow_repeat=False,
                        )
                    elif dist < 1.5:
                        self.haptic.vibrate_center("short")
                        self.voice.speak(
                            "Obstacle nearby.",
                            priority="normal",
                            interrupt=False,
                            allow_repeat=False,
                        )

            # ~10 FPS
            time.sleep(0.1)

    def navigation_loop(self):
        """
        Periodically checks GPS and route; gives turn-by-turn instructions.
        """
        while self.running:
            pos = self.gps.get_current_position()

            if pos and self.current_step:
                if self.route_planner.is_approaching_turn(pos, self.current_step):
                    instr = self.current_step.instruction
                    self.voice.speak(
                        instr,
                        priority="normal",
                        interrupt=False,
                        allow_repeat=True,
                    )

                    # Optional: use left/right haptics for turns
                    text = instr.lower()
                    if "left" in text:
                        self.haptic.vibrate_left("short")
                    elif "right" in text:
                        self.haptic.vibrate_right("short")

                self.current_step = self.route_planner.get_next_instruction(pos)

            time.sleep(1.0)

    def run(self):
        self.startup()

        vision_thread = threading.Thread(target=self.vision_loop, daemon=True)
        nav_thread = threading.Thread(target=self.navigation_loop, daemon=True)

        vision_thread.start()
        nav_thread.start()

        vision_thread.join()
        nav_thread.join()

    def shutdown(self, signum, frame):
        self.running = False

        # Stop camera
        self.camera.stop()

        # Stop motors
        self.haptic.stop_all()

        # 🔥 Close microphone audio stream (VERY IMPORTANT)
        try:
            self.voice_input.close()
        except Exception:
            pass  # ignore errors safely

        # Speak shutdown message
        self.voice.speak(
            "Shutting down.",
            priority="low",
            interrupt=False,
            allow_repeat=True,
        )

        sys.exit(0)


if __name__ == "__main__":
    system = BlindNavigationSystem()
    system.run()
