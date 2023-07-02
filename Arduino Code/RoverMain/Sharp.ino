#include <SharpIR.h>
/*
//Sharp Sensor Pins
#define front 1
#define left 2
#define right 3
#define back 4

#define model 1080
Model :
  GP2Y0A02YK0F --> 20150
  GP2Y0A21YK0F --> 1080
  GP2Y0A710K0F --> 100500
  GP2YA41SK0F --> 430


SharpIR frontSensor = SharpIR(front, model);
SharpIR leftSensor = SharpIR(left, model);
SharpIR rigthSensor = SharpIR(right, model);
SharpIR backSensor = SharpIR(back, model);

bool checkAround()
{
  int distance_front = frontSensor.getDistance();
  int distance_left = leftSensor.getDistance();
  int distance_rigth = rigthSensor.getDistance();
  int distance_back = backSensor.getDistance();
  
  Serial.println(distance_front);
  
  if((distance_front < 17) || (distance_left < 17) || (distance_rigth < 17) || (distance_back < 17))
    alarm();
  
  
  if(distance_front < 17)
    return 0;


  return 1;
  
}
*/
void alarm()
{
  tone(buzzer,440);
  delay(200);
  noTone(buzzer);

}
