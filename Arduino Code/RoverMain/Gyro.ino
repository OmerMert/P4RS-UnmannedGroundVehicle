// PID constants for mpu6050
#define kp_mpu 8
#define kd_mpu 0.45
#define ki_mpu 0.00618

// Calibration values for the MPU6050 sensor
int16_t ax_cal, ay_cal, az_cal;
int16_t gx_cal, gy_cal, gz_cal;

// Read the sensor data
int16_t ax, ay, az; 
int16_t gx, gy, gz;


void setupMPU6050()
{
   Wire.begin();
 byte status = mpu.begin();
   Serial.print(F("MPU6050 status: "));
   Serial.println(status);

  // Calibrate the MPU6050 sensor
   while (status != 0) { } // stop everything if could not connect to MPU6050
 Serial.println(F("Calculating offsets, do not move MPU6050"));
   delay(1000);
   mpu.calcOffsets(); // gyro and accelero
    delay(1000);
    mpu.update();
}
