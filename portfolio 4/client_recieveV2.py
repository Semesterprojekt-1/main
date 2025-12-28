# pico_client_receiver.py
import network
import socket
import time
from stepper_motor import StepperMotor
from differential_drive import DifferentialDrive

#Defining the pins and motors
pins_right = [0,1,2,3]
pins_left = [4,5,6,7]

left = StepperMotor(pins_left, "MICRO", 20, 16000, 32, 200)
right = StepperMotor(pins_right, "MICRO", 20, 16000, 32, 200)
diff = DifferentialDrive(left, right)

# Disable AP interface
ap = network.WLAN(network.AP_IF)
ap.active(False)

# Enable STA
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.config(pm=0xa11140)
wlan.connect("PICO_LINK", "12345678")

# Wait for connection
for _ in range(20):
    if wlan.isconnected():
        break
    time.sleep(0.5)

print("Connected, IP:", wlan.ifconfig())

# Connect to server
server_addr = ("192.168.4.1", 1234)


#New code

while True:
    try:  
        s = socket.socket() # Needs to be in a while True loop in case client disconnects, so it doesn't just crash
        s.connect(server_addr) # Same story here
        print("Connected to server, waiting for data...")
        
        buffer = "" # Implement a buffer so we don't send incomplete data to the receiver/robot

        while True:
            data = s.recv(1024)  # Receive up to 1024 bytes
            
            if not data:
                print("Connection failed")
                break
            
            buffer += data.decode() # Ensures the data accumalates and doesn't overwrite eachother
            
            while "\n" in buffer: #Ensures we only continue the loop with complete data. One for x and one for y, so it doesn't crash the robot
                line, buffer = buffer.split("\n", 1) # line is our data list, and the rest makes it so it only splits the datalist after the first \n
                
                values = line.split(",") # Makes it so we get two values at either side of the comma, as those are the values we need for x and y
                if len(values) == 2: # Because we only want two values at a time
                    valueX = int(values[0]) # takes the first value in the list and converts from a string to an integer
                    valueY = int(values[1]) # takes the second value in the list and converts from a string to an integer
                    
                    # Control logic
                    
                    if valueY >= 51000:
                        diff.forward(4)
                    elif valueY <= 49000:
                        diff.backward(4)
                    elif valueX >= 51000:
                        diff.turn_in_place("left", 3)
                    elif valueX <= 49000:
                        diff.turn_in_place("right", 3)
                            
        s.close()  # Closes server
        
    except Exception as e: # Finds any error in the try block and saves them to the variable e
        print(f"Error: {e}, reconnecting...") # Prints the error found
        time.sleep(1) # So it doesn't "spam" the server with reconnection attempts
