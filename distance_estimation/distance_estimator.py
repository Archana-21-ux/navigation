import torch
import cv2
import numpy as np
from PIL import Image
import depth_pro
from typing import List, Tuple

from object_detection.yolo_detector import Detection

OBSTACLE_DISTANCE_THRESHOLD = 2.0  


class DistanceEstimator:
    def __init__(self, use_gpu: bool = False):
        
        if use_gpu and torch.cuda.is_available():
            self.device = torch.device("cuda")
        else:
            self.device = torch.device("cpu")

        self.model, self.transform = self._load_depth_pro()
        self._cached_f_px: float | None = None  

    def _load_depth_pro(self):
       
        model, transform = depth_pro.create_model_and_transforms()
        model = model.to(self.device)
        model.eval()
        return model, transform

    def _get_focal_length_px(self, height: int, width: int) -> float:
      
        if self._cached_f_px is None:
            self._cached_f_px = float(max(height, width))
        return self._cached_f_px

    def estimate_distance(
        self,
        frame: np.ndarray,
        detections: List[Detection],
        max_detections: int | None = None,
    ) -> List[Tuple[Detection, float, bool]]:
       
        if not detections:
            return []

        if max_detections is not None:
            detections = detections[:max_detections]

        h, w = frame.shape[:2]
        f_px = self._get_focal_length_px(h, w)

        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)

        img_tensor = self.transform(pil_img).to(self.device)

        with torch.no_grad():
            prediction = self.model.infer(img_tensor, f_px=f_px)
            depth_map = prediction["depth"].squeeze().cpu().numpy()  

        dh, dw = depth_map.shape
        results: List[Tuple[Detection, float, bool]] = []

        for det in detections:
            x1, y1, x2, y2 = det.bbox
            center_x = (x1 + x2) / 2.0
            center_y = (y1 + y2) / 2.0

            cx = int(np.clip(center_x, 0, dw - 1))
            cy = int(np.clip(center_y, 0, dh - 1))

            distance_m = float(depth_map[cy, cx])  
            is_obstacle = distance_m < OBSTACLE_DISTANCE_THRESHOLD

            results.append((det, distance_m, is_obstacle))

        return results
