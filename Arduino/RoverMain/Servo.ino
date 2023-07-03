#define stepSize 1 // Define the increment value for each step
#define stepDelay 5 // Define the delay between steps (in milliseconds)
#define servoAngle 105

void openCamera()
{
  int initialAngle = myServo.read();
  for (int angle = initialAngle; angle <= servoAngle; angle += stepSize) {
    myServo.write(angle);
    delay(stepDelay);
  }

}

void closeCamera()
{
  int initialAngle = myServo.read();
  for (int angle = servoAngle; angle >= 0; angle -= stepSize) {
    myServo.write(angle);
    delay(stepDelay);
  }
}
