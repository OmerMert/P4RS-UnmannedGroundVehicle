
// PID constants for encoder
//float kp_enc = 25;
//float kd_enc = 0.45;
//float ki_enc = 0.01;

//float kp_enc = 9;
//float kd_enc = 0.001;
//float ki_enc = 0.00618;

float kp_enc = 2;
float kd_enc = 0.05;
float ki_enc = 0.000183;

float CIRCUMFERENCE = 37.7;
float ENC_COUNT_REV = 2400;//  ~= 12 * 9.68


// Pin definitions for motors and motor drivers
int ENCA = 2; // YELLOW
int ENCB = 3; // WHITE

int R_EN[] = {34, 30, 22, 50};
int R_PWM[] = {7, 9, 6, 8};     //
int L_EN[] = {35, 31, 24, 52};
int L_PWM[] = {5, 11, 4, 10};   //

float angle;

volatile int encoder_count = 0; 
long previous_time = 0;
float previous_e = 0;

int travelPwr = 100;
int turnPwr = 220;

float referance_angle = 0;


void setupMotors()
{
  pinMode(ENCA,INPUT);
  pinMode(ENCB,INPUT);

  for(int i = 0; i < 4; i++)
  {
    pinMode(R_EN[i], OUTPUT);
    pinMode(R_PWM[i], OUTPUT);
    pinMode(L_EN[i], OUTPUT);
    pinMode(L_PWM[i], OUTPUT);
    digitalWrite(R_EN[i], HIGH);
    digitalWrite(L_EN[i], HIGH);
  }

  attachInterrupt(digitalPinToInterrupt(ENCA),readEncoder,RISING);
}



int goTo(int travelDistance)
{
  checkLight();
  // set target encoder_counttion
  float turnnumber = travelDistance / CIRCUMFERENCE;
  int target = turnnumber * ENC_COUNT_REV;

  
  // time difference
  long current_time = micros();
  float delta_t = ((float) (current_time - previous_time))/( 1.0e6 );
  previous_time = current_time;

  int position = 0; 
  ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
    position = encoder_count;
  }
  
  // error
  //int e = position - target;
  int e = target - position;

  // derivative
  float dedt = (e-previous_e)/(delta_t);

  // integral
  float eintegral = eintegral + e*delta_t;

  // control signal
  float u = kp_enc*e + kd_enc*dedt + ki_enc*eintegral;

  // motor power
  float power = fabs(u);
  if( power > travelPwr){
    power = travelPwr;
  }

  // motor directionection
  int direction = 1; //CLOCKWISE ROTATION(CW)
  if(u<0){
    direction = -1; //COUNTER CLOCKWISE ROTATION(CCW)
  }

  // signal the motor
  setMotor(direction,power);

  // store previous error
  previous_e = e;
  
  int travelledDistance = (position / ENC_COUNT_REV * CIRCUMFERENCE);

  return travelledDistance;

}

bool rotate(float rotation_degree) {
  referance_angle = rotation_degree;
  signalLight(rotation_degree);
  long current_time = micros();
  float delta_t = ((float) (current_time - previous_time))/( 1.0e6 );
  previous_time = current_time;
  mpu.update();
  current_angle = mpu.getAngleZ();

  // error
  float e = rotation_degree - current_angle;

  // derivative
  float dedt = (e-previous_e)/(delta_t);

  // integral
  float eintegral = eintegral + e*delta_t;

  // control signal
  float u = kp_mpu*e + kd_mpu*dedt + ki_mpu*eintegral;

  // motor power
  float power = fabs(u);

  if( power > turnPwr){
    power = turnPwr;
  }

  if(e > 3){
      analogWrite(R_PWM[0], power);
      analogWrite(R_PWM[2], power);
      analogWrite(L_PWM[1], power);
      analogWrite(L_PWM[3], power);
  }else if(e < -3) {
      analogWrite(R_PWM[1], power);
      analogWrite(R_PWM[3], power);
      analogWrite(L_PWM[0], power);
      analogWrite(L_PWM[2], power);
  }else {
    stopMotor();
    return 1;
  }
  /*
    int direction = 1; //CLOCKWISE ROTATION(CW)
  if(u<0){
    direction = -1; //COUNTER CLOCKWISE ROTATION(CCW)
  }
  if(direction == 1){
      analogWrite(R_PWM[0], power);
      analogWrite(R_PWM[2], power);
      analogWrite(L_PWM[1], power);
      analogWrite(L_PWM[3], power);
  }else if(direction == -1) {
      analogWrite(R_PWM[1], power);
      analogWrite(R_PWM[3], power);
      analogWrite(L_PWM[0], power);
      analogWrite(L_PWM[2], power);
  }
  if(e < 1 || e > -1)
    return 1;
    */
  // store previous error
  previous_e = e;
  
  return 0;


/*
  mpu.update();
  float angleZ = mpu.getAngleZ();
  current_angle = angleZ;
  float e = rotation_degree - angleZ;
  
  if(e > 1){
      analogWrite(R_PWM[0], turnPwr);
      analogWrite(R_PWM[2], turnPwr);
      analogWrite(L_PWM[1], turnPwr);
      analogWrite(L_PWM[3], turnPwr);
  }else if(e < -1) {
      analogWrite(R_PWM[1], turnPwr);
      analogWrite(R_PWM[3], turnPwr);
      analogWrite(L_PWM[0], turnPwr);
      analogWrite(L_PWM[2], turnPwr);
  }else {
    //stopMotor();
    return 1;
  }

  
  return 0;*/
}

void setMotor(int direction, int pwm_value){

  int left_ofset_pwr = 0;
  int right_ofset_pwr = 0;
  
  int rotation = directionController();
  bool a = 0;
  if(a)
  {
  if (rotation == 1)
    right_ofset_pwr = 50;
  else if(rotation == -1)
    left_ofset_pwr = 50;
  }
  if(direction == 1){ //CLOCKWISE ROTATION(CW)
    analogWrite(R_PWM[0],pwm_value + left_ofset_pwr);
    analogWrite(R_PWM[1],pwm_value + right_ofset_pwr);
    analogWrite(R_PWM[2],pwm_value + left_ofset_pwr);
    analogWrite(R_PWM[3],pwm_value + right_ofset_pwr);
    for(int i = 0; i < 4; i++)
      analogWrite(L_PWM[i],0);
  }
  else if(direction == -1){ //COUNTER CLOCKWISE ROTATION(CCW)

    analogWrite(R_PWM[0],pwm_value + left_ofset_pwr);
    analogWrite(R_PWM[1],pwm_value + right_ofset_pwr);
    analogWrite(R_PWM[2],pwm_value + left_ofset_pwr);
    analogWrite(R_PWM[3],pwm_value + right_ofset_pwr);
  
  for(int i = 0; i < 4; i++)
      analogWrite(R_PWM[i],0);
  }
  else{
   for(int i = 0; i < 4; i++)
   {
      analogWrite(R_PWM[i],0);
      analogWrite(L_PWM[i],0);
   }

  }  

  
}



int directionController(){
  //mpu.update();
  float angleZ = mpu.getAngleZ();
  int dir = 0;
  float error_angle =  1;
  
  Serial.println(angleZ);
  if(angleZ > referance_angle + error_angle)
   dir = 1;
  else if ( angleZ < referance_angle - error_angle)
    dir = -1;
  
  return dir;

  
}


void stopMotor()
{    
  delay(500);
  for(int i = 0; i < 4; i++)
  {
    analogWrite(R_PWM[i],0);
    analogWrite(L_PWM[i],0);
  }

  
  encoder_count = 0; 
  previous_time = 0;
  previous_e = 0;


}

void readEncoder(){
  int b = digitalRead(ENCB);
  if(b > 0){
    encoder_count--;
  }
  else{
    encoder_count++;
  }
}
