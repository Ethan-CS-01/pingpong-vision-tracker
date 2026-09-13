from dataclasses import dataclass


@dataclass
class ControlConfig:
    deadband_ratio: float = 0.12
    near_ratio: float = 0.16


def decide_motion(cx: float | None, object_width: float | None,
                  frame_width: int, config: ControlConfig | None = None) -> str:
    """
    Convert a detected ball position into a high-level robot command.

    SEARCH  : no ball detected
    LEFT    : ball is left of the center
    RIGHT   : ball is right of the center
    FORWARD : ball is centered but still far away
    STOP    : ball is centered and close

    object_width/frame_width is used as a simple proximity estimate.
    """
    cfg = config or ControlConfig()

    if cx is None or object_width is None or frame_width <= 0:
        return "SEARCH"

    center = frame_width / 2.0
    error_ratio = (cx - center) / frame_width
    width_ratio = object_width / frame_width

    if abs(error_ratio) > cfg.deadband_ratio:
        return "LEFT" if error_ratio < 0 else "RIGHT"

    if width_ratio >= cfg.near_ratio:
        return "STOP"

    return "FORWARD"
