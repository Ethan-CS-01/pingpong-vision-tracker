/*
  ESP32 high-level command receiver for the PingPong Vision Tracker.

  IMPORTANT:
  This example deliberately does NOT drive the Cytron MDDS10 directly because
  motor-driver input mode and GPIO wiring must match your actual hardware.
  Use this sketch first to verify communication safely.

  Commands received from the PC:
    LEFT
    RIGHT
    FORWARD
    STOP
    SEARCH

  After serial communication is confirmed, replace the TODO functions below
  with the correct MDDS10 control method for your selected input mode.
*/

String command = "";

void stopMotors() {
  // TODO: add your verified MDDS10 stop command here.
}

void moveForward() {
  // TODO: add your verified MDDS10 forward command here.
}

void turnLeft() {
  // TODO: add your verified MDDS10 left-turn command here.
}

void turnRight() {
  // TODO: add your verified MDDS10 right-turn command here.
}

void searchForBall() {
  // Safe default: keep stopped until your search motion has been tested.
  stopMotors();
}

void setup() {
  Serial.begin(115200);
  stopMotors();
  Serial.println("ESP32 vision command receiver ready.");
}

void loop() {
  if (!Serial.available()) return;

  command = Serial.readStringUntil('\n');
  command.trim();
  command.toUpperCase();

  if (command == "FORWARD") {
    moveForward();
  } else if (command == "LEFT") {
    turnLeft();
  } else if (command == "RIGHT") {
    turnRight();
  } else if (command == "SEARCH") {
    searchForBall();
  } else {
    stopMotors();
  }

  Serial.print("CMD=");
  Serial.println(command);
}
