import cv2
from ultralytics import YOLO
from pathlib import Path
from typing import List, NamedTuple


class Detection(NamedTuple):
    class_name: str
    class_id: int
    confidence: float
    bbox: tuple  # (x1, y1, x2, y2)


# Model path relative to this file:
# blind_navigation/
#   object_detection/
#     yolo_detector.py
#     models/
#       yolov11n.pt
MODEL_PATH = Path(__file__).resolve().parent / "models" / "yolov11n.pt"

CONFIDENCE_THRESHOLD = 0.7


class YOLODetector:
    def __init__(self, conf_threshold: float = CONFIDENCE_THRESHOLD):
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"YOLO model not found at {MODEL_PATH}.")

        self.model = YOLO(str(MODEL_PATH))
        self.model.fuse()

        self.relevant_classes = ["person", "car", "bus", "truck", "bicycle", "motorcycle"]
        self.conf_threshold = conf_threshold

    def detect(self, frame) -> List[Detection]:
        """
        frame: NumPy image (BGR from OpenCV or Picamera2)
        Returns: list of Detection
        """
        results = self.model(frame, conf=self.conf_threshold, verbose=False)

        detections: List[Detection] = []

        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls)
                cls_name = self.model.names[cls_id]
                if cls_name not in self.relevant_classes:
                    continue

                conf = float(box.conf)
                x1, y1, x2, y2 = box.xyxy[0].tolist()

                detections.append(
                    Detection(
                        class_name=cls_name,
                        class_id=cls_id,
                        confidence=conf,
                        bbox=(x1, y1, x2, y2),
                    )
                )

        return detections
