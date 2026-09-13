import cv2
import numpy as np

# Webcam + HSV range for a white ping-pong ball
cap = cv2.VideoCapture(0)
lower = np.array([0, 0, 165], dtype=np.uint8)
upper = np.array([179, 90, 255], dtype=np.uint8)

while True:
    ok, frame = cap.read()
    if not ok:
        break

    frame = cv2.flip(frame, 1)
    hsv = cv2.cvtColor(cv2.GaussianBlur(frame, (7, 7), 0), cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower, upper)

    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)
    command = "SEARCH"

    if contours:
        contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(contour)

        if area > 120:
            (x, y), radius = cv2.minEnclosingCircle(contour)
            cx, cy = int(x), int(y)
            radius = int(radius)
            frame_width = frame.shape[1]
            error = cx - frame_width / 2

            # High-level movement decision
            if abs(error) > 0.12 * frame_width:
                command = "LEFT" if error < 0 else "RIGHT"
            elif (2 * radius) / frame_width >= 0.16:
                command = "STOP"
            else:
                command = "FORWARD"

            cv2.circle(frame, (cx, cy), radius, (0, 255, 0), 2)
            cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
            cv2.putText(frame, f"PINGPONG | {command}", (20, 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv2.imshow("PingPong Image Processing", frame)
    cv2.imshow("Ball Mask", mask)

    if cv2.waitKey(1) & 0xFF in (27, ord("q")):
        break

cap.release()
cv2.destroyAllWindows()
