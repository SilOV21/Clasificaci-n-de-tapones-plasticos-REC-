"""Helpers to draw synthetic bottle-cap frames for the simulation."""
from __future__ import annotations

import cv2
import numpy as np


WIDTH = 640
HEIGHT = 480

COLOR_BGR = {
    "rojo": (40, 40, 220),
    "azul": (220, 100, 40),
    "amarillo": (40, 220, 230),
    "blanco": (240, 240, 240),
}


def _workbench(width: int = WIDTH, height: int = HEIGHT) -> np.ndarray:
    img = np.full((height, width, 3), 90, dtype=np.uint8)
    for x in range(0, width, 40):
        cv2.line(img, (x, 0), (x, height), (110, 110, 110), 1)
    for y in range(0, height, 40):
        cv2.line(img, (0, y), (width, y), (110, 110, 110), 1)
    cv2.rectangle(img, (40, 40), (width - 40, height - 40), (60, 60, 60), 2)
    return img


def make_cap_frame(color: str, phase: float = 0.0) -> np.ndarray:
    """Workbench background with a single colored cap at a moving position."""
    img = _workbench()
    bgr = COLOR_BGR.get(color.lower(), (200, 200, 200))

    cx = int(WIDTH / 2 + 120 * np.cos(phase))
    cy = int(HEIGHT / 2 + 60 * np.sin(phase))
    radius = 42

    cv2.circle(img, (cx, cy), radius + 4, (20, 20, 20), -1)
    cv2.circle(img, (cx, cy), radius, bgr, -1)
    cv2.circle(img, (cx, cy), radius // 3, (40, 40, 40), 2)
    cv2.putText(
        img,
        color.upper(),
        (20, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )
    return img


def make_debug_frame(color: str, box_id: int, phase: float = 0.0) -> np.ndarray:
    """Same as make_cap_frame but with detection overlay (green ring + box label)."""
    img = make_cap_frame(color, phase)
    cx = int(WIDTH / 2 + 120 * np.cos(phase))
    cy = int(HEIGHT / 2 + 60 * np.sin(phase))
    cv2.circle(img, (cx, cy), 50, (60, 220, 60), 3)
    cv2.line(img, (cx - 70, cy), (cx + 70, cy), (60, 220, 60), 1)
    cv2.line(img, (cx, cy - 70), (cx, cy + 70), (60, 220, 60), 1)
    cv2.putText(
        img,
        f"Box {box_id}  ({color})",
        (cx - 80, cy + 90),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (60, 220, 60),
        2,
        cv2.LINE_AA,
    )
    cv2.putText(
        img,
        "DEBUG",
        (WIDTH - 120, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (60, 220, 60),
        2,
        cv2.LINE_AA,
    )
    return img
