# Architecture

## Existing FYP concept

The original table-tennis ball collector is a mobile vacuum-style machine using an ESP32-based controller,
DC drive motors, sensors, and a vacuum motor.

## Vision upgrade

Camera -> Python/OpenCV or YOLO -> ball coordinates -> control logic -> optional USB serial -> ESP32 -> motor control

### Stage 1: no-training prototype
`color_tracker.py` detects a white or orange ping-pong ball using HSV color segmentation and contour circularity.

### Stage 2: learned detector
1. Capture real images with `collect_dataset.py`.
2. Draw bounding boxes locally with `label_dataset.py`.
3. Split the data with `prepare_dataset.py`.
4. Fine-tune YOLO with `train_yolo.py`.
5. Track the learned object with `yolo_tracker.py`.

## Why this is useful

Color segmentation is fast and easy to demonstrate, but it may fail under poor lighting or backgrounds.
A trained detector can learn the appearance of the ball across different lighting, distances and scenes.

## Hardware note

The repository sends only high-level commands over serial by default.
Before connecting commands to the real motor driver, verify the exact Cytron MDDS10 mode, GPIO mapping,
motor polarity and emergency-stop behavior on the physical machine.
