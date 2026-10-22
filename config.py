"""
Central configuration for the Smart Parking project.
Edit these values to match your camera setup.
"""

# --- Video / camera source ---
# 0 = default webcam, 1/2/... = other connected cameras,
# a file path = recorded video (put test videos in samples/, e.g.
# "samples/parking_demo.mp4"), or an RTSP/IP camera URL.
VIDEO_SOURCE = 0

# --- Files ---
SPOTS_FILE = "parking_spots.json"      # saved by spot_marker.py
REFERENCE_FRAME = "reference_frame.jpg"  # a single still frame used to mark spots

# --- YOLO model ---
# "yolov8n.pt" is the small/fast pretrained model. It already knows the
# COCO class "car" (class id 2) and "truck" (class id 7) out of the box,
# so no custom training is needed.
YOLO_MODEL = "yolov8n.pt"
YOLO_CONFIDENCE = 0.35
VEHICLE_CLASS_IDS = {2, 5, 7}  # car, bus, truck (COCO ids)

# --- Occupancy logic ---
# A parking spot is considered OCCUPIED if a detected vehicle's box
# overlaps the spot polygon by at least this fraction.
OVERLAP_THRESHOLD = 0.35

# On a live camera, a single frame's detection can flicker (a car
# briefly misdetected, motion blur, etc). A spot's displayed state only
# flips after it reads the same way for this many consecutive frames,
# so the count updates cleanly when a car actually parks or leaves.
STABILITY_FRAMES = 8

# --- Entrance location ---
# Pixel coordinate (x, y) of the parking lot entrance in the camera frame.
# Set this after marking your spots, by looking at the reference frame.
ENTRANCE_POINT = (50, 400)

# --- Display ---
DISPLAY_WINDOW_NAME = "Parking Lot Camera"
LED_BOARD_WINDOW_NAME = "LED Information Board"
