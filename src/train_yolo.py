import argparse
from ultralytics import YOLO


def main():
    parser = argparse.ArgumentParser(description="Fine-tune YOLO for ping-pong ball detection.")
    parser.add_argument("--model", default="yolo11n.pt")
    parser.add_argument("--data", default="data/pingpong.yaml")
    parser.add_argument("--epochs", type=int, default=60)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--device", default=None,
                        help="Examples: 0 for NVIDIA GPU, cpu for CPU. Omit for auto.")
    args = parser.parse_args()

    model = YOLO(args.model)
    kwargs = dict(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        project="runs",
        name="pingpong_ball",
        patience=15,
    )
    if args.device is not None:
        kwargs["device"] = args.device

    results = model.train(**kwargs)
    print(results)
    print("Best model should be under runs/pingpong_ball/weights/best.pt")


if __name__ == "__main__":
    main()
