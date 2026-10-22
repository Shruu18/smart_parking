"""
spot_marker.py

Run this once per camera setup to define where each parking spot is.

Controls:
  - Left click   : add a corner point (4 points = one spot polygon)
  - After 4 points, type a label in the terminal (e.g. A1) and press Enter
  - 'u'           : undo the last point
  - 's'           : save all spots to SPOTS_FILE and exit
  - 'q'           : quit without saving

Output: writes a JSON file like:
[
  {"label": "A1", "points": [[120,80],[210,80],[210,160],[120,160]]},
  {"label": "A2", "points": [[220,80],[310,80],[310,160],[220,160]]}
]
"""

import json
import os
import cv2

import config


def grab_reference_frame():
    """Get a still frame to mark spots on: reuse a saved one, or grab
    the first frame from the configured video source."""
    if os.path.exists(config.REFERENCE_FRAME):
        frame = cv2.imread(config.REFERENCE_FRAME)
        if frame is not None:
            return frame

    cap = cv2.VideoCapture(config.VIDEO_SOURCE)
    ok, frame = cap.read()
    cap.release()
    if not ok:
        raise RuntimeError(
            f"Could not read a frame from VIDEO_SOURCE={config.VIDEO_SOURCE!r}. "
            "Check the path/camera index in config.py."
        )
    cv2.imwrite(config.REFERENCE_FRAME, frame)
    return frame


class SpotMarker:
    def __init__(self, frame):
        self.base_frame = frame
        self.spots = []          # finished spots: [{"label": str, "points": [[x,y],...]}]
        self.current_points = [] # points for the spot being drawn

    def redraw(self):
        display = self.base_frame.copy()

        # draw finished spots
        for spot in self.spots:
            pts = spot["points"]
            for i in range(4):
                cv2.line(display, tuple(pts[i]), tuple(pts[(i + 1) % 4]), (0, 255, 0), 2)
            cx = sum(p[0] for p in pts) // 4
            cy = sum(p[1] for p in pts) // 4
            cv2.putText(display, spot["label"], (cx - 10, cy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        # draw in-progress points
        for i, p in enumerate(self.current_points):
            cv2.circle(display, tuple(p), 4, (0, 0, 255), -1)
            if i > 0:
                cv2.line(display, tuple(self.current_points[i - 1]), tuple(p), (0, 0, 255), 2)

        cv2.putText(display, f"Spots marked: {len(self.spots)}  |  u=undo  s=save  q=quit",
                    (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.imshow(config.DISPLAY_WINDOW_NAME, display)

    def on_mouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.current_points.append([x, y])
            if len(self.current_points) == 4:
                label = input("Enter label for this spot (e.g. A1): ").strip()
                if not label:
                    label = f"SPOT{len(self.spots) + 1}"
                self.spots.append({"label": label, "points": self.current_points})
                self.current_points = []
            self.redraw()

    def undo(self):
        if self.current_points:
            self.current_points.pop()
        elif self.spots:
            self.spots.pop()
        self.redraw()

    def save(self):
        with open(config.SPOTS_FILE, "w") as f:
            json.dump(self.spots, f, indent=2)
        print(f"Saved {len(self.spots)} spots to {config.SPOTS_FILE}")


def main():
    frame = grab_reference_frame()
    marker = SpotMarker(frame)

    cv2.namedWindow(config.DISPLAY_WINDOW_NAME)
    cv2.setMouseCallback(config.DISPLAY_WINDOW_NAME, marker.on_mouse)
    marker.redraw()

    while True:
        key = cv2.waitKey(20) & 0xFF
        if key == ord("u"):
            marker.undo()
        elif key == ord("s"):
            marker.save()
            break
        elif key == ord("q"):
            print("Quit without saving.")
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
