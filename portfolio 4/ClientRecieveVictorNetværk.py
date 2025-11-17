import network
import socket
import time
from stepper_motor import StepperMotor
from differential_drive import DifferentialDrive

SSID = "Victor's Galaxy A52"
PASSWORD = "ebpm3056"
SERVER_IP = "10.139.255.110"  # Replace with server Pico’s IP
SERVER_PORT = 1234

# Connect client Pico to Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

def connect_wifi():
    wlan.connect(SSID, PASSWORD)
    for _ in range(20):
        if wlan.isconnected():
            print("Client Wi-Fi connected, IP:", wlan.ifconfig()[0])
            return True
        time.sleep(0.5)
    return False

def connect_server():
    while True:
        try:
            s = socket.socket()
            s.connect((SERVER_IP, SERVER_PORT))
            print(f"Connected to server at {SERVER_IP}:{SERVER_PORT}")
            return s
        except OSError:
            print("Server unreachable, retrying in 2s...")
            time.sleep(2)
            
#Defining the pins and motors
pins_right = [0,1,2,3]
pins_left = [4,5,6,7]

left = StepperMotor(pins_left, "MICRO", 20, 16000, 32, 200)
right = StepperMotor(pins_right, "MICRO", 20, 16000, 32, 200)
diff = DifferentialDrive(left, right)

# Main loop
while True:
    if not wlan.isconnected():
        print("Connecting to Wi-Fi...")
        if not connect_wifi():
            print("Failed to connect, retrying in 2s...")
            time.sleep(2)
            continue

    s = connect_server()

    try:
        buffer = ""
        while True:
            data = s.recv(1024)
            
            if not data:
                print("Server disconnected")
                break
            
            buffer += data.decode()
            
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                #if line:  # skip empty lines
                    #print("Received:", line)
                    
                values = line.split(",") # Makes it so we get two values at either side of the comma, as those are the values we need for x and y
                if len(values) == 2: # Because we only want two values at a time
                    valueX = int(values[0]) # takes the first value in the list and converts from a string to an integer
                    valueY = int(values[1]) # takes the second value in the list and converts from a string to an integer
                    print(valueX,valueY)
                    
                    if valueY >= 51000:
                        diff.forward(4)
                    elif valueY <= 49000:
                        diff.backward(4)
                    elif valueX >= 51000:
                        diff.turn_in_place_steps("left", 4)
                    elif valueX <= 49000:
                        diff.turn_in_place_steps("right", 4)

    except OSError as e:
        print("Connection error:", e)
        s.close()
        time.sleep(1)

