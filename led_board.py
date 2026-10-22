"""
led_board.py

Renders a simulated LED information board (black background, bright
text) showing total spots, available spots, and the nearest available
spot's label. Swap render() for real hardware calls later (e.g. serial
write to an Arduino/ESP32 driving a P10 LED matrix) without touching
the rest of the project.
"""

import cv2
import numpy as np

import config

BOARD_W, BOARD_H = 480, 220
BG_COLOR = (10, 10, 10)
TEXT_COLOR = (0, 255, 60)      # LED-style green
WARN_COLOR = (0, 60, 255)      # red-ish for "FULL"


def render(total_spots: int, available_spots: int, nearest_label: str | None):
    board = np.full((BOARD_H, BOARD_W, 3), BG_COLOR, dtype=np.uint8)

    cv2.putText(board, "PARKING STATUS", (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, TEXT_COLOR, 2)

    cv2.putText(board, f"TOTAL:     {total_spots}", (20, 85),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, TEXT_COLOR, 2)

    avail_color = TEXT_COLOR if available_spots > 0 else WARN_COLOR
    cv2.putText(board, f"AVAILABLE: {available_spots}", (20, 125),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, avail_color, 2)

    if available_spots > 0 and nearest_label is not None:
        nearest_text = f"NEAREST -> {nearest_label}"
    else:
        nearest_text = "LOT FULL"
    cv2.putText(board, nearest_text, (20, 175),
                cv2.FONT_HERSHEY_SIMPLEX, 0.85,
                TEXT_COLOR if available_spots > 0 else WARN_COLOR, 2)

    cv2.imshow(config.LED_BOARD_WINDOW_NAME, board)
