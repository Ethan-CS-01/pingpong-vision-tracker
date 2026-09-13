import time

try:
    import serial
except ImportError:
    serial = None


class SerialCommandSender:
    def __init__(self, port: str | None = None, baudrate: int = 115200,
                 min_interval: float = 0.12):
        self.port = port
        self.baudrate = baudrate
        self.min_interval = min_interval
        self._ser = None
        self._last_command = None
        self._last_time = 0.0

        if port:
            if serial is None:
                raise RuntimeError("pyserial is not installed. Run: pip install pyserial")
            self._ser = serial.Serial(port, baudrate=baudrate, timeout=0.1)
            time.sleep(1.5)

    @property
    def enabled(self) -> bool:
        return self._ser is not None

    def send(self, command: str):
        if not self._ser:
            return
        now = time.time()
        if command == self._last_command and now - self._last_time < self.min_interval:
            return
        self._ser.write((command.strip().upper() + "\n").encode("utf-8"))
        self._last_command = command
        self._last_time = now

    def close(self):
        if self._ser:
            self._ser.close()
            self._ser = None
