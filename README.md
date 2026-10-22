# Smart Parking Lot Availability System

Detects free/occupied parking spots from a camera feed using YOLO,
counts total vs available spots, finds the nearest available spot to
the entrance, and shows it all on a simulated LED information board.

## How it works

1. **Mark spots once** — click the 4 corners of each parking space on a
   reference frame and label it (A1, A2, ...).
2. **Detect vehicles** — YOLOv8 (pretrained, no training needed) finds
   cars/trucks/buses in each frame.
3. **Classify occupancy** — a spot is "occupied" if a vehicle box
   overlaps its polygon past a threshold.
4. **Count & locate** — total spots, available spots, and the nearest
   available spot to a fixed entrance point (straight-line distance).
5. **Display** — camera feed with colored spot outlines (red=occupied,
   green=available) + a simulated LED board window with the numbers.

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

`VIDEO_SOURCE` in `config.py` is set to `0` by default, which uses
your default webcam for a live feed. Change it to a file path (e.g.
`"parking_lot.mp4"`) to run on a recorded video instead, or an RTSP
URL for an IP camera.

## Usage

**Step 1 — Mark your parking spots** (one-time per camera angle):

```bash
python spot_marker.py
```
Click 4 corners per spot, type a label in the terminal, repeat for
every spot, then press `s` to save.

**Step 2 — Set the entrance point:**

Open `reference_frame.jpg` (saved automatically by spot_marker.py),
find the pixel coordinate of your entrance, and set it in
`config.py`:
```python
ENTRANCE_POINT = (x, y)
```

**Step 3 — Run the system:**

```bash
python main.py
```

Press `q` in the camera window to quit.

## Moving to a real LED board later

Everything the board needs (`total`, `available`, `nearest_label`) is
computed in `main.py` and currently passed to `led_board.render()`.
To drive real hardware (e.g. an ESP32/Arduino + P10 LED matrix), swap
the body of `render()` for a serial/WiFi write — nothing else in the
project needs to change.

## Notes / tuning

- `OVERLAP_THRESHOLD` in `config.py` controls how much of a spot must
  be covered by a car to count as occupied — raise it if partially
  visible neighboring cars are falsely marking spots occupied.
- `YOLO_CONFIDENCE` controls detection sensitivity.
- `STABILITY_FRAMES` (live camera only) is how many consecutive frames
  a spot must read the same way before its displayed state changes.
  Raise it if the count still flickers; lower it for a snappier
  response when a car actually parks/leaves.
- For a static overhead camera, a lighter classic-CV approach (pixel
  count / background subtraction per spot) can be swapped in for
  `detect_vehicle_boxes` + `classify_spots` if you want to avoid the
  YOLO dependency — ask and I can add that as an alternative.
