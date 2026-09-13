import argparse

import cv2
from ultralytics import YOLO

from control_logic import decide_motion
from serial_control import SerialCommandSender


def main():
    parser = argparse.ArgumentParser(description="AI ping-pong ball tracker using a trained YOLO model.")
    parser.add_argument("--model", default="runs/pingpong_ball/weights/best.pt")
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--conf", type=float, default=0.35)
    parser.add_argument("--serial-port", default=None, help="Example: COM5")
    parser.add_argument("--autodrive", action="store_true")
    args = parser.parse_args()

    model = YOLO(args.model)
    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera {args.camera}")

    sender = SerialCommandSender(args.serial_port if args.autodrive else None)

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            result = model.predict(frame, conf=args.conf, verbose=False)[0]
            command = "SEARCH"
            best = None
            best_conf = -1.0

            if result.boxes is not None:
                for box in result.boxes:
                    conf = float(box.conf[0])
                    if conf > best_conf:
                        x1, y1, x2, y2 = map(float, box.xyxy[0].tolist())
                        best = (x1, y1, x2, y2, conf)
                        best_conf = conf

            if best:
                x1, y1, x2, y2, conf = best
                cx = (x1 + x2) / 2
                width = x2 - x1
                command = decide_motion(cx, width, frame.shape[1])

                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                cv2.circle(frame, (int(cx), int((y1 + y2) / 2)), 4, (0, 0, 255), -1)
                cv2.putText(frame, f"pingpong {conf:.2f} | {command}",
                            (int(x1), max(25, int(y1) - 8)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "No ball detected | SEARCH",
                            (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

            center_x = frame.shape[1] // 2
            cv2.line(frame, (center_x, 0), (center_x, frame.shape[0]), (255, 255, 0), 1)

            if args.autodrive:
                sender.send(command)

            cv2.imshow("PingPong AI Tracker", frame)
            if cv2.waitKey(1) & 0xFF in (27, ord("q")):
                break
    finally:
        sender.send("STOP")
        sender.close()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
