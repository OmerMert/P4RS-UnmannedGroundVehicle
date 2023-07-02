import serial
import time

arduino = serial.Serial(
port = "COM6",
baudrate = 115200,
bytesize = serial.EIGHTBITS,
parity = serial.PARITY_NONE,
stopbits = serial.STOPBITS_ONE,
timeout = 5, #1-10s
xonxoff = False,
rtscts = False,
dsrdtr = False,
write_timeout = 2 #1-5s
)

def send_inputs_to_arduino(x,y,scan_mode):      #**************
    start_time = time.time()
    try:
        arduino.write(("TAKE_INPUTS").encode('utf-8'))
        if(arduino.readable()):
            data_read = arduino.readline().decode('utf-8').rstrip()
            if (data_read == "TAKE_INPUTS_ACK"):
                print(data_read)
                try:
                    arduino.write(("{} {} {}".format(x,y,scan_mode)).encode('utf-8'))
                    if(arduino.readable()):
                        data_read = arduino.readline().decode('utf-8').rstrip()
                        if data_read:
                            print(data_read)
                            elapsed_time = time.time() - start_time
                            print("Time elapsed: {:.6f} seconds".format(elapsed_time))
                            return 1  
                        else:
                            print(data_read)
                            elapsed_time = time.time() - start_time
                            print("Time elapsed: {:.6f} seconds".format(elapsed_time))
                            return 0      
                except Exception as err:
                    print(err)
                    elapsed_time = time.time() - start_time
                    print("Time elapsed: {:.6f} seconds".format(elapsed_time))
            else:
                elapsed_time = time.time() - start_time
                print("Time elapsed: {:.6f} seconds".format(elapsed_time))
                return 0      
    except Exception as err:
        print(err)
        elapsed_time = time.time() - start_time
        print("Time elapsed: {:.6f} seconds".format(elapsed_time))

def check_communication_with_arduino():         #**************
    start_time = time.time()
    try:
        arduino.write(("CHECK_COM").encode('utf-8'))
        if(arduino.readable()):
            data_read = arduino.readline().decode('utf-8').rstrip()
            if (data_read == "CHECK_COM_ACK"):
                print(data_read)
                elapsed_time = time.time() - start_time
                print("Time elapsed: {:.6f} seconds".format(elapsed_time))
                return 1
            else:
                print(data_read)
                elapsed_time = time.time() - start_time
                print("Time elapsed: {:.6f} seconds".format(elapsed_time))
                return 0      
    except Exception as err:
        print(err)
        elapsed_time = time.time() - start_time
        print("Time elapsed: {:.6f} seconds".format(elapsed_time))

def wait_object_detected():                     #**************
    start_time = time.time()
    try:
        if(arduino.readable()):
            data_read = arduino.readline().decode('utf-8').rstrip()
            if (data_read == "OBJECT_DETECTED"):
                print(data_read)
                elapsed_time = time.time() - start_time
                print("Time elapsed: {:.6f} seconds".format(elapsed_time))
                return 1
            else:
                print(data_read)
                elapsed_time = time.time() - start_time
                print("Time elapsed: {:.6f} seconds".format(elapsed_time))
                return 0
    except Exception as err:
        print(err)
        elapsed_time = time.time() - start_time
        print("Time elapsed: {:.6f} seconds".format(elapsed_time))
        return 0
    
def wait_scan_done():                           #**************
    start_time = time.time()
    try:
        if(arduino.readable()):
            data_read = arduino.readline().decode('utf-8').rstrip()
            if (data_read == "COMPLETED"):
                print(data_read)
                elapsed_time = time.time() - start_time
                print("Time elapsed: {:.6f} seconds".format(elapsed_time))
                return 1
            else:
                print("ahada burdayım")
                print(data_read)
                elapsed_time = time.time() - start_time
                print("Time elapsed: {:.6f} seconds".format(elapsed_time))
                return 0
    except Exception as err:
        print(err)
        elapsed_time = time.time() - start_time
        print("Time elapsed: {:.6f} seconds".format(elapsed_time))
        return 0