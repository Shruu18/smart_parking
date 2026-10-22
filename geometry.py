"""
geometry.py

Small geometry helpers used to decide whether a detected vehicle box
occupies a parking spot polygon, and to measure distance to the entrance.
"""

import math
import numpy as np
import cv2


def polygon_centroid(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return (sum(xs) / len(points), sum(ys) / len(points))


def euclidean_distance(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


def box_polygon_overlap_fraction(box_xyxy, polygon_points, frame_shape):
    """
    Returns the fraction (0..1) of the SPOT polygon's area that is
    covered by the detected vehicle's bounding box.

    box_xyxy: (x1, y1, x2, y2) of the detected vehicle
    polygon_points: list of [x, y] corners of the parking spot
    frame_shape: (height, width) of the frame, used to size the masks
    """
    h, w = frame_shape[:2]

    spot_mask = np.zeros((h, w), dtype=np.uint8)
    cv2.fillPoly(spot_mask, [np.array(polygon_points, dtype=np.int32)], 1)

    box_mask = np.zeros((h, w), dtype=np.uint8)
    x1, y1, x2, y2 = [int(v) for v in box_xyxy]
    x1, y1 = max(x1, 0), max(y1, 0)
    x2, y2 = min(x2, w - 1), min(y2, h - 1)
    if x2 <= x1 or y2 <= y1:
        return 0.0
    box_mask[y1:y2, x1:x2] = 1

    spot_area = spot_mask.sum()
    if spot_area == 0:
        return 0.0

    intersection = np.logical_and(spot_mask, box_mask).sum()
    return intersection / spot_area
