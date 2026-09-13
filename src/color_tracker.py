import argparse
from collections import deque

import cv2
import numpy as np

from control_logic import decide_motion
from serial_control import SerialCommandSender


PRESETS = {
    "white": ((0, 0, 165), (179, 90, 255)),
    "orange": ((3, 90, 90), (30, 255, 255)),
}


def largest_ball(mask, min_area=120.0, min_circularity=0.50):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    best = None
    best_area = 0.0

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < min_area:
            continue

        perimeter = cv2.arcLength(contour, True)
        if perimeter <= 0:
            continue
        circularity = 4 * np.pi * area / (perimeter * perimeter)
        if circularity < min_circularity:
            continue

        (x, y), radius = cv2.minEnclosingCircle(contour)
        if radius < 3:
            continue

        if area > best_area:
            best = (int(x), int(y), int(radius), area, circularity)
            best_area = area

    return best


def main():
    parser = argparse.ArgumentParser(description="Track a white/orange ping-pong ball with OpenCV.")
    parser.add_argument("--camera", type=int, default=0, help="Webcam index, usually 0")
    parser.add_argument("--color", choices=PRESETS, default="white")
    parser.add_argument("--serial-port", default=None, help="Example: COM5")
    parser.add_argument("--autodrive", action="store_true",
                        help="Actually send high-level commands over serial")
    parser.add_argument("--show-mask", action="store_true")
    args = parser.parse_args()

    lower, upper = PRESETS[args.color]
    lower = np.array(lower, dtype=np.uint8)
    upper = np.array(upper, dtype=np.uint8)

    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera {args.camera}")

    sender = SerialCommandSender(args.serial_port if args.autodrive else None)
    trail = deque(maxlen=32)

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            frame = cv2.flip(frame, 1)
            blurred = cv2.GaussianBlur(frame, (7, 7), 0)
            hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

            mask = cv2.inRange(hsv, lower, upper)
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

            detection = largest_ball(mask)
            command = "SEARCH"

            if detection:
                cx, cy, radius, area, circularity = detection
                trail.appendleft((cx, cy))
                command = decide_motion(cx, radius * 2, frame.shape[1])

                cv2.circle(frame, (cx, cy), radius, (0, 255, 0), 2)
                cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
                cv2.putText(
                    frame,
                    f"BALL x={cx} y={cy} r={radius} cmd={command}",
                    (20, 35),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.75,
                    (0, 255, 0),
                    2,
                )

                for i in range(1, len(trail)):
                    if trail[i - 1] is None or trail[i] is None:
                        continue
                    thickness = max(1, int(np.sqrt(32 / float(i + 1)) * 1.5))
                    cv2.line(frame, trail[i - 1], trail[i], (255, 255, 255), thickness)
            else:
                trail.appendleft(None)
                cv2.putText(
                    frame,
                    "BALL NOT FOUND - SEARCH",
                    (20, 35),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.75,
                    (0, 0, 255),
                    2,
                )

            center_x = frame.shape[1] // 2
            cv2.line(frame, (center_x, 0), (center_x, frame.shape[0]), (255, 255, 0), 1)

            if args.autodrive:
                sender.send(command)

            cv2.imshow("PingPong Vision Tracker - OpenCV", frame)
            if args.show_mask:
                cv2.imshow("Mask", mask)

            key = cv2.waitKey(1) & 0xFF
            if key in (27, ord("q")):
                break
    finally:
        sender.send("STOP")
        sender.close()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
