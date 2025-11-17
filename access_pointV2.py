import network
import socket
import time
from stepper_motor import StepperMotor
from differential_drive import DifferentialDrive
from machine import ADC,Pin
import math


# Defining the adc's for x and y
adcX = ADC(26)
adcY = ADC(27)

# Setup Access Point
ap = network.WLAN(network.AP_IF)
ap.config(essid="PICO_LINK", password="12345678", pm=0xa11140)
ap.active(True)

while not ap.active():
    time.sleep(0.5)

print("AP active at:", ap.ifconfig())

# Create TCP server
addr = socket.getaddrinfo("0.0.0.0", 1234)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)
print("Waiting for client to connect...")


# New code attempt
while True:
    try:
        conn, client_addr = s.accept()
        print("Client connected from:", client_addr)
        
        # Send data continuously
        while True:
            try:
                valueX = adcX.read_u16()
                valueY = adcY.read_u16()
                
                message = f"{valueX},{valueY}\n"  #We are trying to send the x- and y values here
                conn.send(message.encode())  # Send bytes
                print("Sent:", message)
                
                time.sleep(0.1)  # Lowered the delay from 1 second to 0.1 to send more
                
            except:
                print("Disconnected")
                conn.close()
                break
            
    except KeyboardInterrupt: #So we can close the program efficiently
        print("Server closed")
        break
    
s.close() #Closes server

