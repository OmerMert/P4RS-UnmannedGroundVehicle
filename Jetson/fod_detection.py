import jetson.inference
import jetson.utils
import serial
import time
import glob

net = jetson.inference.detectNet(argv=["--model=/home/gazitek/FOD_detection/model/ssd-mobilenet.onnx", 
"--labels=/home/gazitek/FOD_detection/model/labels.txt", 
"--input-blob=input_0", 
"--output-cvg=scores", 
"--output-bbox=boxes"])

camera = jetson.utils.videoSource("csi://0")      # '/dev/video0' for V4L2
display = jetson.utils.videoOutput("display://0") # 'my_video.mp4' for file


def find_available_ttyUSB():
    ttyUSB_ports = glob.glob('/dev/ttyUSB*')
    available_ports = []

    for port in ttyUSB_ports:
        try:
            with open(port, 'r') as test_file:
                available_ports.append(port)
        except (OSError, IOError):
            pass

    return available_ports

# Kullanılabilir TtyUSB portlarını bul
available_ttyUSB_ports = find_available_ttyUSB()


arduino = serial.Serial(available_ttyUSB_ports[0], 9600)

'''
def wait_message():
    while(1):
        if(arduino.readable()):
            break
        time.sleep(1)

#Establish Communication
while(1):
    send_data = "START"
    arduino.write(send_data.encode('utf-8'))
    time.sleep(1)
    wait_message()

    read_data = arduino.readline().decode()
    print("ee")
    print(read_data)
    if(read_data == "START_ACK"):
        break
'''
send_detection_message = True

send_data = "START"
arduino.write(send_data.encode('utf-8'))
time.sleep(1)

while display.IsStreaming():

	img = camera.Capture()
	detections = net.Detect(img) #detections contains objects in the image
	
	for detection in detections:
		try:
			if(send_detection_message):
				send_data = "STOP"
				arduino.write(send_data.encode('utf-8'))
				send_detection_message = False

			if(arduino.readable()):
				read_data = arduino.readline().decode('utf-8').rstrip()
				if(read_data == "PASSED"):
					send_detection_message = True
		except:
			pass
	
	display.Render(img)
	display.SetStatus("Object Detection | Network {:.0f} FPS".format(net.GetNetworkFPS()))

