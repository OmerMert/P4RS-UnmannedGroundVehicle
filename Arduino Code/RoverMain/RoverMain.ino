//sudo chmod a+rw /dev/ttyUSB0

#include <util/atomic.h> // For the ATOMIC_BLOCK macro
#include <Arduino.h>
#include <Wire.h>
#include <MPU6050_light.h>
#include <Servo.h>

#define vehicleWidth 40 // 40 cm
#define servoPin 27
#define buzzer 13

#define ledRight 26
#define ledLeft 29
#define ldrPin A0

MPU6050 mpu(Wire);
Servo myServo;

// Scan parameters
int xDistance = 0;
int yDistance = 0;
int scanCycle = 0;
int edgeDistance = 0;

int desiredDistance = 0;
int traveledDistance = 0;
float current_angle = 0;

int x_value_from_ui;
int y_value_from_ui;
String scan_mode_from_ui;

enum Direction{
    UP,
    DOWN
}direction;

bool isFinished = false;

boolean ledState = LOW;
unsigned long ledTime = 0;

void setup() {
  
  Serial.begin(9600);

  setupMPU6050();
  //setupGPS();
  
  pinMode(buzzer, OUTPUT);
  myServo.attach(servoPin);
  myServo.write(0);
  pinMode(ledRight, OUTPUT);
  pinMode(ledLeft, OUTPUT);
  setupMotors();
  wait_jetson_connection();
    
  setupUI();
  // Connect to UI
  while(!UIConnection()) ;
  // Get X and Y form UI
  GetInputsFromUI();
    
  openCamera();

  
  setScanParams();
  delay(1000);
}


void loop() {

  
  if(scanCycle >= 0 && !isFinished)
  {
    if(!is_object_detected())
    {
      //Scan Algorithm
      traveledDistance = goTo(desiredDistance);
      if(traveledDistance == desiredDistance)
      {
          
          Serial.print("reached ");
          Serial.println(desiredDistance);

          stopMotor();
           
          edgeMovement();

          scanCycle--;
      }

    }else
    {
        // Foreign Object Detection
        alarm();
        stopMotor();
        Serial.println("FOD detected.");
        send_data_to_pc("OBJECT_DETECTED");
        // Send Coordinates of object
        String location_msg = getRelativeCoordinates() +  "," + "0,0";
        send_data_to_pc(location_msg);

        int remainedDistance = desiredDistance - traveledDistance;
        Serial.print("Remained Distance: ");
        Serial.println(remainedDistance);
        int distanceAfterTurning = 50;
        int distanceToPass = 70;
        passAroundObject(distanceAfterTurning, distanceToPass);
        desiredDistance = remainedDistance - distanceToPass;
        delay(100);
        
    }
  }else
  {
    // Finished Scan
    Serial.println("Completed");
    stopMotor();
    closeCamera();
    send_data_to_pc("COMPLETED");
    while(1);
  }
   
}

void setScanParams()
{
  xDistance = x_value_from_ui * 100;
  yDistance = y_value_from_ui * 100;
  
  if(scan_mode_from_ui == "Detailed")
    edgeDistance = vehicleWidth;
  else if(scan_mode_from_ui == "Normal")
    edgeDistance = vehicleWidth * 1.5;
  else if(scan_mode_from_ui == "Fast")
    edgeDistance = vehicleWidth * 2;
  
  scanCycle = xDistance / edgeDistance; 
  desiredDistance = yDistance;

}

void edgeMovement()
{
  
    if(scanCycle == 0)
    {
      isFinished = true;
      return;
    }
    
    int rotateAngle = current_angle;
    int offSetAngle = 0;
    if(direction == UP)
    {
        offSetAngle = -90;
        direction = DOWN;
    }else if(direction == DOWN){
        offSetAngle = 90;
        direction = UP;
    }
    
    rotateAngle = current_angle + offSetAngle;
    while(!rotate(rotateAngle));
    Serial.print("rotated "); Serial.println(rotateAngle);
    stopMotor();
    
    desiredDistance = edgeDistance;
    while(goTo(desiredDistance) != desiredDistance);
    Serial.println("reached "); Serial.println(vehicleWidth);
    Serial.println(current_angle);
    stopMotor();
    
    rotateAngle = current_angle + offSetAngle;;
    while(!rotate(rotateAngle));
    Serial.print("rotated "); Serial.println(rotateAngle);
    stopMotor();

              
    desiredDistance = yDistance;
}


void passAroundObject(int distanceAfterTurning, int distanceToPass)
{
   Serial.println("Passing around object...");

    int rotateAngle = current_angle - 90;
    while(!rotate(rotateAngle));

    stopMotor();
    
    while(goTo(distanceAfterTurning) != distanceAfterTurning);
    stopMotor();
    
    rotateAngle = current_angle + 90;
    while(!rotate(rotateAngle));
    stopMotor();
    
    while(goTo(distanceToPass) != distanceToPass);
    stopMotor();
    
    rotateAngle = current_angle + 90;
    while(!rotate(rotateAngle));
    stopMotor();
    
    while(goTo(distanceAfterTurning) != distanceAfterTurning);
    stopMotor();
    
    rotateAngle = current_angle - 90;
    while(!rotate(rotateAngle));
    stopMotor();
    send_data_to_jetson("PASSED");
    Serial.println("Passed.");
    
}

String getRelativeCoordinates()
{
  int relativeY = traveledDistance;
  int relativeX = xDistance - (scanCycle * edgeDistance);
  String relativeCord = String(relativeX) + "," + String(relativeY);

  return relativeCord;
  
}

void checkLight()
{
    int ldrValue = analogRead(ldrPin);
  // Check if the LDR value is above the threshold
  if (ldrValue < 500) {
    // Turn on the LED
    
    digitalWrite(ledRight, HIGH);
    digitalWrite(ledLeft, HIGH);
  } else {
    // Turn off the LED
    digitalWrite(ledRight, LOW);
    digitalWrite(ledLeft, LOW);
  }
}

int signalLight(int dir)
{
  unsigned long currentTime = millis(); // Geçerli zamanı al

  if (ledState == LOW) {
    if (currentTime - ledTime >= 500) {
      ledState = HIGH;
      ledTime = currentTime; 
    }
  } else {
    if (currentTime - ledTime >= 500) {
      ledState = LOW;
      ledTime = currentTime; 
    }
  }
  if(dir == 90)
  {
     digitalWrite(ledRight, ledState); 
     digitalWrite(ledLeft, LOW);
  }
   
  if(dir == -90)
  {
     digitalWrite(ledLeft, ledState);
     digitalWrite(ledLeft, LOW);
  }
   
}
