# PingPong Vision Tracker

A GitHub-ready computer-vision upgrade for a table-tennis ball collection robot.

The project has two levels:

1. **OpenCV tracker** — works immediately with a webcam and does not require AI training.
2. **YOLO learning pipeline** — collect your own ping-pong images, label them locally, fine-tune an object detector, then track the ball in real time.

The optional serial layer can send high-level commands (`LEFT`, `RIGHT`, `FORWARD`, `STOP`, `SEARCH`) to an ESP32. Real motor control is intentionally kept disabled in the sample firmware until the actual Cytron MDDS10 wiring and mode are verified.

## Project structure

```text
PingPong-Vision-Tracker/
├─ src/
│  ├─ image_processing_core.py
│  ├─ color_tracker.py
│  ├─ collect_dataset.py
│  ├─ label_dataset.py
│  ├─ prepare_dataset.py
│  ├─ train_yolo.py
│  ├─ yolo_tracker.py
│  ├─ control_logic.py
│  └─ serial_control.py
├─ firmware/
│  └─ esp32_serial_receiver/
├─ data/
│  ├─ raw/
│  ├─ images/train/
│  ├─ images/val/
│  ├─ labels/train/
│  ├─ labels/val/
│  └─ pingpong.yaml
├─ docs/ARCHITECTURE.md
├─ INTERVIEW_PITCH.md
├─ requirements.txt
└─ .gitignore
```

## 1. Windows setup

Open PowerShell inside this folder.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, use Command Prompt:

```bat
.venv\Scripts\activate.bat
```

## 2. Run the immediate OpenCV tracker

For a white ball:

```powershell
python src/color_tracker.py --camera 0 --color white --show-mask
```

For an orange ball:

```powershell
python src/color_tracker.py --camera 0 --color orange --show-mask
```

Press **Q** or **Esc** to quit.

Tips:
- Put the ball in front of a contrasting background.
- Avoid overexposure if using a white ball.
- If your external camera is not camera 0, try `--camera 1`.

## 3. Let the model learn your ball

### Step A — collect images

```powershell
python src/collect_dataset.py --camera 0
```

Controls:
- **Space**: save one image
- **A**: auto-capture on/off
- **Q**: quit

Capture at least 100-300 images. Include:
- near/far ball
- left/right side
- different lighting
- different floor/table backgrounds
- partial occlusion
- multiple ball positions

### Step B — label each ball

```powershell
python src/label_dataset.py
```

Drag a rectangle around each ping-pong ball.
- **S** save and next
- **R** reset current image
- **Q** quit

### Step C — split train and validation data

```powershell
python src/prepare_dataset.py
```

### Step D — train YOLO

```powershell
python src/train_yolo.py --epochs 60
```

If you have a compatible NVIDIA GPU:

```powershell
python src/train_yolo.py --epochs 60 --device 0
```

The best model should appear under:

```text
runs/pingpong_ball/weights/best.pt
```

## 4. Run the learned AI tracker

```powershell
python src/yolo_tracker.py --model runs/pingpong_ball/weights/best.pt --camera 0
```

## 5. Optional ESP32 serial integration

First upload:

```text
firmware/esp32_serial_receiver/esp32_serial_receiver.ino
```

Then test PC-to-ESP32 communication only after confirming the correct COM port.

Example:

```powershell
python src/yolo_tracker.py --camera 0 --serial-port COM5 --autodrive
```

**Important:** the supplied ESP32 firmware intentionally leaves real motor-driver functions as TODO.
Verify the actual MDDS10 input mode and wiring before adding motor movement.

## 6. Suggested GitHub repository description

> Computer vision and YOLO-based ping-pong ball detection and tracking for an ESP32 mechatronics collection robot.

## Portfolio value

This project demonstrates:
- Python
- OpenCV image processing
- object detection
- dataset collection and labeling
- YOLO fine-tuning
- real-time tracking
- control logic
- ESP32 integration
- mechatronics + AI/automation
