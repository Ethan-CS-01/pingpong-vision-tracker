from src.control_logic import decide_motion


def test_no_detection():
    assert decide_motion(None, None, 640) == "SEARCH"


def test_left():
    assert decide_motion(100, 40, 640) == "LEFT"


def test_right():
    assert decide_motion(540, 40, 640) == "RIGHT"


def test_forward():
    assert decide_motion(320, 40, 640) == "FORWARD"


def test_stop_when_close():
    assert decide_motion(320, 150, 640) == "STOP"
