
bool wait_jetson_connection()
{
  Serial.println("");
  Serial.print("Waiting jetson start up..");
  while(!Serial) Serial.print(".."); // wait for serial port to connect jetson
  Serial.println("");
  
  Serial.print("Waiting jetson to establish connection..");
  while(!Serial.available())
  {
    Serial.print("..");
    delay(1000);
  }
  Serial.println("");
  
   String data_from_jetson = read_data_from_jetson();
    if(data_from_jetson == "START")
    {
      Serial.println("Jetson Connected");      
      return 1;
    }

  return 0;

    
}

bool is_object_detected()
{
    if(!Serial.available())
      return 0;

    String data_from_jetson = read_data_from_jetson();
    
    if(data_from_jetson == "STOP")
      return 1;
      
    return 0;
}


String read_data_from_jetson() {

   String data_from_jetson = "";
    while (Serial.available()) {
      char c = Serial.read();
      data_from_jetson += c;
      delay(1);
    }

    return data_from_jetson;

}

void send_data_to_jetson(String data) {
    Serial.println(data);
}
