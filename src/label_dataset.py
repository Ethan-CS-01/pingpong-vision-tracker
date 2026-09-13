"""
Simple local YOLO box labeler.

Controls:
- Drag left mouse button around each ping-pong ball.
- S = save labels and go to next image.
- R = reset boxes for current image.
- Q = quit.

The script creates YOLO-format .txt labels under data/raw_labels/.
"""
import argparse
from pathlib import Path

import cv2

boxes = []
drawing = False
start_pt = None
current_pt = None


def mouse_callback(event, x, y, flags, param):
    global drawing, start_pt, current_pt, boxes
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        start_pt = (x, y)
        current_pt = (x, y)
    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        current_pt = (x, y)
    elif event == cv2.EVENT_LBUTTONUP and drawing:
        drawing = False
        x1, y1 = start_pt
        x2, y2 = x, y
        x1, x2 = sorted((x1, x2))
        y1, y2 = sorted((y1, y2))
        if x2 - x1 > 4 and y2 - y1 > 4:
            boxes.append((x1, y1, x2, y2))
        start_pt = None
        current_pt = None


def to_yolo(box, width, height):
    x1, y1, x2, y2 = box
    cx = ((x1 + x2) / 2) / width
    cy = ((y1 + y2) / 2) / height
    bw = (x2 - x1) / width
    bh = (y2 - y1) / height
    return f"0 {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}"


def main():
    global boxes, start_pt, current_pt

    parser = argparse.ArgumentParser()
    parser.add_argument("--images", default="data/raw")
    parser.add_argument("--labels", default="data/raw_labels")
    args = parser.parse_args()

    image_dir = Path(args.images)
    label_dir = Path(args.labels)
    label_dir.mkdir(parents=True, exist_ok=True)

    images = sorted([p for p in image_dir.iterdir()
                     if p.suffix.lower() in {".jpg", ".jpeg", ".png"}])
    if not images:
        raise RuntimeError(f"No images found in {image_dir}")

    cv2.namedWindow("YOLO Labeler")
    cv2.setMouseCallback("YOLO Labeler", mouse_callback)

    for idx, path in enumerate(images, start=1):
        image = cv2.imread(str(path))
        if image is None:
            continue

        h, w = image.shape[:2]
        boxes = []
        existing = label_dir / f"{path.stem}.txt"

        if existing.exists():
            for line in existing.read_text(encoding="utf-8").splitlines():
                parts = line.split()
                if len(parts) != 5:
                    continue
                _, cx, cy, bw, bh = map(float, parts)
                x1 = int((cx - bw / 2) * w)
                y1 = int((cy - bh / 2) * h)
                x2 = int((cx + bw / 2) * w)
                y2 = int((cy + bh / 2) * h)
                boxes.append((x1, y1, x2, y2))

        while True:
            display = image.copy()
            for x1, y1, x2, y2 in boxes:
                cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 0), 2)

            if drawing and start_pt and current_pt:
                cv2.rectangle(display, start_pt, current_pt, (0, 255, 255), 2)

            cv2.putText(display, f"{idx}/{len(images)} | Boxes: {len(boxes)} | S save | R reset | Q quit",
                        (12, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)
            cv2.imshow("YOLO Labeler", display)

            key = cv2.waitKey(20) & 0xFF
            if key in (ord("r"), ord("R")):
                boxes = []
            elif key in (ord("s"), ord("S")):
                lines = [to_yolo(b, w, h) for b in boxes]
                existing.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
                break
            elif key in (27, ord("q"), ord("Q")):
                cv2.destroyAllWindows()
                return

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
