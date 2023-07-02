#include <TinyGPS++.h>

static const uint32_t GPSBaud = 9600;
// The TinyGPS++ object
TinyGPSPlus gps;

void setupGPS()
{
  Serial2.begin(GPSBaud);
}

String take_gps_location()
{
  String gps_message = "";
  while (!Serial2.available());
  String latitude = String(gps.location.lat(), 6);
  String longitude = String(gps.location.lng(), 6);
  gps_message = latitude + "," + longitude;
  return gps_message;
  
}
