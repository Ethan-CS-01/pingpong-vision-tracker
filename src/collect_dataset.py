import argparse
from pathlib import Path
import time

import cv2


def main():
    parser = argparse.ArgumentParser(description="Collect webcam images for ping-pong ball training.")
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--output", default="data/raw")
    parser.add_argument("--interval", type=float, default=0.35,
                        help="Minimum seconds between saved frames")
    args = parser.parse_args()

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera {args.camera}")

    print("SPACE = save image, A = toggle auto-capture, Q = quit")
    auto = False
    last_save = 0.0
    count = len(list(out.glob("*.jpg")))

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            preview = frame.copy()
            cv2.putText(preview, f"Saved: {count} | Auto: {auto}",
                        (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.imshow("Dataset Collector", preview)

            now = time.time()
            key = cv2.waitKey(1) & 0xFF

            should_save = key == ord(" ") or (auto and now - last_save >= args.interval)
            if should_save:
                path = out / f"pingpong_{int(now * 1000)}.jpg"
                cv2.imwrite(str(path), frame)
                count += 1
                last_save = now
                print(f"Saved {path}")

            if key in (ord("a"), ord("A")):
                auto = not auto
            elif key in (27, ord("q"), ord("Q")):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
