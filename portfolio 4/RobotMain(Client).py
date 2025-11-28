import network
import socket
import time
from stepper_motor import StepperMotor
from p4_differential_drive import DifferentialDrive

SSID = "Victor's Galaxy A52"
PASSWORD = "ebpm3056"
SERVER_IP = "10.139.255.177" 
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

left = StepperMotor(pins_left, "MICRO", 40, 18000, 32, 200)
right = StepperMotor(pins_right, "MICRO", 40, 18000, 32, 200)
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
        s.settimeout(0) 
        buffer = ""
        lastX = 0
        lastY = 0

        while True:
            try:
                data = s.recv(1024)

                if data:  
                    buffer += data.decode()

                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)

                        values = line.split(",")
                        if len(values) == 2:
                            try:
                                lastX = int(values[0])
                                lastY = int(values[1])
                                print(lastX, lastY)
                            except:
                                pass  
            except OSError:
                # No data available 
                pass

            #Movement
            if lastY == 2 :
                diff.set_microsteps(32)
                diff.forward(4)
            elif lastY == 1 :
                diff.set_microsteps(80)
                diff.forward(4)
            elif lastY == -2 :
                diff.set_microsteps(32)
                diff.backward(4)
            elif lastY == -1 :
                diff.set_microsteps(80)
                diff.backward(4)
            elif lastX == 2 :
                diff.set_microsteps(32)
                diff.turn_in_place_steps("left", 4)
            elif lastX == 1 :
                diff.set_microsteps(80)
                diff.turn_in_place_steps("left", 4)
            elif lastX == -2:
                diff.set_microsteps(32)
                diff.turn_in_place_steps("right", 4)
            elif lastX == -1:
                diff.set_microsteps(80)
                diff.turn_in_place_steps("right", 4)
            
            
            else:
                time.sleep(0.005)


    except OSError as e:
        print("Connection error:", e)
        s.close()
        time.sleep(1)

