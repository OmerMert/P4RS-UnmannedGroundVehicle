

String COMMAND;
String ACKMSG;


void setupUI()
{
    Serial1.begin(115200);
    while(!Serial1){}
}

bool UIConnection()
{
  while(!Serial1.available() ){checkLight();}
  COMMAND = read_data_from_pc();
  if (COMMAND == "CHECK_COM") {
    take_command_and_send_ack(COMMAND);
    Serial.println("UI connected");
    return 1;
  }
  
  return 0;
  
}

void GetInputsFromUI()
{
  while(!Serial1.available() );
  COMMAND = read_data_from_pc();
  if(COMMAND == "TAKE_INPUTS") { 
      take_command_and_send_ack(COMMAND);
      while(!Serial1.available() );
      take_inputs_and_send_ack();
  }

  
}

bool takeCompeltedAck()
{
  while(!Serial1.available() );
  COMMAND = read_data_from_pc();
  if(COMMAND == "OBJECT_DETECTED_ACK") { 
    return 1;
  }
  return 0;
}


//***** DEFINITION OF THE USER DEFINED FUNCTIONS *****
String read_data_from_pc() {
    String data_from_pc = "";
    while (Serial1.available()) {
      char c = Serial1.read();
      data_from_pc += c;
      delay(1);
    }
    delay(10);
    return data_from_pc;
}


void send_data_to_pc(String l_data_to_pc) {
    Serial1.println(l_data_to_pc);
}

void take_command_and_send_ack(String l_COMMAND) {
    ACKMSG = l_COMMAND + "_ACK";
    send_data_to_pc(ACKMSG);
}

void take_inputs_and_send_ack() {
    COMMAND = read_data_from_pc();
    int spaceIndex1 = COMMAND.indexOf(' ');
    int spaceIndex2 = COMMAND.indexOf(' ', spaceIndex1+1);
    x_value_from_ui = COMMAND.substring(0, spaceIndex1).toInt();
    y_value_from_ui = COMMAND.substring(spaceIndex1+1, spaceIndex2).toInt();
    scan_mode_from_ui = COMMAND.substring(spaceIndex2+1, COMMAND.length());
    ACKMSG = String(x_value_from_ui) + " " + String(y_value_from_ui) + " " + scan_mode_from_ui;
    //Serial.println("take_inputs_and_send_ack");
    //Serial.println(ACKMSG);
    send_data_to_pc(ACKMSG);
}
