"""ROS-independent orange ball detector, suitable for isolated unit tests."""

from dataclasses import dataclass
from typing import Optional, Sequence

import cv2
import numpy as np


@dataclass(frozen=True)
class BallDetection:
    center_x: int
    center_y: int
    radius: float
    area: float
    circularity: float


def detect_orange_ball(
    frame_bgr: np.ndarray,
    lower_hsv: Sequence[int] = (6, 110, 110),
    upper_hsv: Sequence[int] = (25, 255, 255),
    min_area: float = 400.0,
    min_radius: float = 15.0,
    min_circularity: float = 0.6,
    morphology_iterations: int = 3,
) -> Optional[BallDetection]:
    """Find largest valid orange circular region in a BGR image, else None.

    This is an appearance heuristic, not a learned object detector.
    """
    if frame_bgr is None or frame_bgr.ndim != 3 or frame_bgr.shape[2] != 3:
        raise ValueError('Expected a BGR image with shape (height, width, 3)')

    hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(
        hsv,
        np.array(lower_hsv, dtype=np.uint8),
        np.array(upper_hsv, dtype=np.uint8),
    )
    if morphology_iterations:
        mask = cv2.erode(mask, None, iterations=int(morphology_iterations))
        mask = cv2.dilate(mask, None, iterations=int(morphology_iterations))

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    best = None
    for contour in contours:
        area = float(cv2.contourArea(contour))
        if area <= min_area:
            continue
        perimeter = float(cv2.arcLength(contour, True))
        if perimeter <= 0:
            continue
        circularity = float(4.0 * np.pi * area / (perimeter * perimeter))
        if circularity <= min_circularity:
            continue
        (x, y), radius = cv2.minEnclosingCircle(contour)
        if radius <= min_radius:
            continue
        detection = BallDetection(round(x), round(y), radius, area, circularity)
        if best is None or detection.area > best.area:
            best = detection
    return best
