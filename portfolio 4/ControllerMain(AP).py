import network
import socket
import time
from machine import ADC, Pin, I2C
import math
import ssd1306

SSID = "Victor's Galaxy A52"
PASSWORD = "ebpm3056"
PORT = 1234

# Connect server Pico to Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

# Wait for connection
for _ in range(20):
    if wlan.isconnected():
        break
    time.sleep(0.5)

if not wlan.isconnected():
    print("Failed to connect to Wi-Fi")
    raise SystemExit

print("Server Wi-Fi connected, IP:", wlan.ifconfig()[0])

# Setup TCP server
addr = socket.getaddrinfo("0.0.0.0", PORT)[0][-1] 
server_socket = socket.socket()
server_socket.bind(addr)
server_socket.listen(1)
print(f"Server listening on port {PORT}...")


# Defining the adc's for x and y
adcX = ADC(28)
adcY = ADC(27)
i2c = I2C(0, scl=Pin(17), sda=Pin(16))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
oled_update_counter = 0
killswitch = Pin(10, Pin.IN, Pin.PULL_UP)

while True:
    try:
        print("Waiting for client to connect...")
        conn, client_addr = server_socket.accept()
        print(f"Client connected from {client_addr}")
        
        

        while True:
            try:
                print(killswitch.value())
                if killswitch.value() == 0:
                    break                    
                valueX = adcX.read_u16()
                valueY = adcY.read_u16()
                print(valueX,valueY)

                if valueX == 65535:
                    valueX = 2
                elif valueX >=50000:
                    valueX = 1
                elif valueX <= 25300:
                    valueX = -2
                elif valueX <= 46000:
                    valueX = -1
                else:
                    valueX = 0
                    
                if valueY == 65535:
                    valueY = 2
                elif valueY >=50000:
                    valueY = 1
                elif valueY <= 25300:
                    valueY = -2
                elif valueY <= 46000:
                    valueY = -1
                else:
                    valueY = 0
                
                #Send x and y values
                message =  f"{valueX},{valueY}\n"  
                conn.send((message).encode())
                print(f"Sent: {message}")
                
                
                oled_update_counter += 1
                if oled_update_counter >= 10:
                    oled_update_counter = 0
                    speed="Stopped"
                    if abs(valueY)==1:
                        speed="Slow"
                    elif abs(valueY)==2:
                        speed="Fast"
                    elif abs(valueX)==2:
                        speed="Fast"
                    elif abs(valueX)==1:
                        speed="Slow"
                
                    oled.fill(0)
                    oled.text("Robot Speed:", 0, 0)
                    oled.text("{}".format(speed), 0, 20)
                    oled.show()
                time.sleep(0.2)

            except OSError:
                print(f"Client {client_addr} disconnected")
                conn.close()
                break

    except KeyboardInterrupt:
        print("Server closed.")
        break
