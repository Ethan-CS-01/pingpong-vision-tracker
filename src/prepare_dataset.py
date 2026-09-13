import argparse
import random
import shutil
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Split raw images and YOLO labels into train/val.")
    parser.add_argument("--images", default="data/raw")
    parser.add_argument("--labels", default="data/raw_labels")
    parser.add_argument("--val-ratio", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    img_dir = Path(args.images)
    lbl_dir = Path(args.labels)
    pairs = []

    for img in img_dir.iterdir():
        if img.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
            continue
        label = lbl_dir / f"{img.stem}.txt"
        if label.exists():
            pairs.append((img, label))

    if len(pairs) < 5:
        raise RuntimeError("Need at least 5 labeled images. 100-300+ is recommended.")

    random.Random(args.seed).shuffle(pairs)
    val_count = max(1, int(len(pairs) * args.val_ratio))
    val_set = set(img.name for img, _ in pairs[:val_count])

    for split in ("train", "val"):
        (Path("data/images") / split).mkdir(parents=True, exist_ok=True)
        (Path("data/labels") / split).mkdir(parents=True, exist_ok=True)

    for img, label in pairs:
        split = "val" if img.name in val_set else "train"
        shutil.copy2(img, Path("data/images") / split / img.name)
        shutil.copy2(label, Path("data/labels") / split / label.name)

    print(f"Prepared {len(pairs) - val_count} train and {val_count} validation images.")


if __name__ == "__main__":
    main()
