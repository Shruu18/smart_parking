"""
main.py

Runs the full smart parking pipeline:
  1. Read frames from the configured video source.
  2. Detect vehicles with YOLO.
  3. Determine which parking spots are occupied (box/polygon overlap).
  4. Count total vs available spots.
  5. Find the nearest AVAILABLE spot to the entrance.
  6. Draw overlays on the camera feed and render the simulated LED board.

Run spot_marker.py first to create parking_spots.json.
"""

import json
import os
import sys

import cv2
from ultralytics import YOLO

import config
import geometry
import led_board


def load_spots():
    if not os.path.exists(config.SPOTS_FILE):
        sys.exit(
            f"'{config.SPOTS_FILE}' not found. Run spot_marker.py first "
            "to mark your parking spots."
        )
    with open(config.SPOTS_FILE) as f:
        return json.load(f)


def detect_vehicle_boxes(model, frame):
    """Run YOLO on a frame and return a list of (x1,y1,x2,y2) boxes
    for detected vehicles above the confidence threshold."""
    results = model.predict(
        frame, conf=config.YOLO_CONFIDENCE, verbose=False
    )[0]

    boxes = []
    for box in results.boxes:
        cls_id = int(box.cls[0])
        if cls_id in config.VEHICLE_CLASS_IDS:
            boxes.append(tuple(box.xyxy[0].tolist()))
    return boxes


def classify_spots(spots, vehicle_boxes, frame_shape):
    """Return spots annotated with an 'occupied' bool."""
    for spot in spots:
        occupied = False
        for vbox in vehicle_boxes:
            overlap = geometry.box_polygon_overlap_fraction(
                vbox, spot["points"], frame_shape
            )
            if overlap >= config.OVERLAP_THRESHOLD:
                occupied = True
                break
        spot["occupied"] = occupied
    return spots


class SpotStabilizer:
    """
    Smooths raw per-frame occupancy readings so the displayed count only
    changes once a spot has read the same way for STABILITY_FRAMES in a
    row. Without this, a single missed/extra detection on a live camera
    can make the count flicker even when no car actually moved.
    """

    def __init__(self):
        self._candidate = {}   # label -> last raw reading
        self._streak = {}      # label -> how many frames in a row it's held
        self._stable = {}      # label -> the current displayed state

    def update(self, spots):
        for spot in spots:
            label = spot["label"]
            raw = spot["occupied"]

            if label not in self._stable:
                # first time we've seen this spot: trust it immediately
                self._stable[label] = raw
                self._candidate[label] = raw
                self._streak[label] = config.STABILITY_FRAMES

            if raw == self._candidate[label]:
                self._streak[label] += 1
            else:
                self._candidate[label] = raw
                self._streak[label] = 1

            if self._streak[label] >= config.STABILITY_FRAMES:
                self._stable[label] = self._candidate[label]

            spot["occupied"] = self._stable[label]
        return spots


def find_nearest_available(spots, entrance_point):
    """Return the label of the available spot closest to the entrance,
    or None if the lot is full."""
    best_label = None
    best_dist = float("inf")
    for spot in spots:
        if spot["occupied"]:
            continue
        centroid = geometry.polygon_centroid(spot["points"])
        dist = geometry.euclidean_distance(entrance_point, centroid)
        if dist < best_dist:
            best_dist = dist
            best_label = spot["label"]
    return best_label


def draw_overlay(frame, spots, entrance_point, nearest_label):
    for spot in spots:
        color = (0, 0, 255) if spot["occupied"] else (0, 255, 0)
        pts = spot["points"]
        for i in range(4):
            cv2.line(frame, tuple(pts[i]), tuple(pts[(i + 1) % 4]), color, 2)

        centroid = geometry.polygon_centroid(pts)
        label_text = spot["label"]
        if spot["label"] == nearest_label:
            label_text += " *NEAREST*"
        cv2.putText(frame, label_text,
                    (int(centroid[0]) - 20, int(centroid[1])),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    cv2.circle(frame, entrance_point, 8, (255, 255, 0), -1)
    cv2.putText(frame, "ENTRANCE", (entrance_point[0] + 10, entrance_point[1]),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
    return frame


def main():
    spots_template = load_spots()
    model = YOLO(config.YOLO_MODEL)
    stabilizer = SpotStabilizer()

    cap = cv2.VideoCapture(config.VIDEO_SOURCE)
    if not cap.isOpened():
        sys.exit(f"Could not open VIDEO_SOURCE={config.VIDEO_SOURCE!r}")

    while True:
        ok, frame = cap.read()
        if not ok:
            break  # end of video (or loop it, see note below)

        vehicle_boxes = detect_vehicle_boxes(model, frame)

        # fresh copy each frame so occupancy state doesn't stick around
        spots = [dict(s) for s in spots_template]
        spots = classify_spots(spots, vehicle_boxes, frame.shape)
        spots = stabilizer.update(spots)

        total = len(spots)
        occupied_count = sum(1 for s in spots if s["occupied"])
        available = total - occupied_count
        nearest_label = find_nearest_available(spots, config.ENTRANCE_POINT)

        frame = draw_overlay(frame, spots, config.ENTRANCE_POINT, nearest_label)
        cv2.imshow(config.DISPLAY_WINDOW_NAME, frame)
        led_board.render(total, available, nearest_label)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
