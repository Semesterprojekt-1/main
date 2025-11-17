import network
import socket
import time
from machine import ADC,Pin, I2C
import math
import ssd1306



SSID = "Victor's Galaxy A52"
PASSWORD = "ebpm3056"
PORT = 1234

#SSID = "AndroidAPa138"
#PASSWORD = "shle9732"
#PORT = 1234

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
addr = socket.getaddrinfo("0.0.0.0", PORT)[0][-1]  # Listen on all interfaces
server_socket = socket.socket()
server_socket.bind(addr)
server_socket.listen(1)
print(f"Server listening on port {PORT}...")


# Defining the adc's for x and y
adcX = ADC(26)
adcY = ADC(27)
i2c = I2C(0, scl=Pin(1), sda=Pin(0))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

while True:
    try:
        print("Waiting for client to connect...")
        conn, client_addr = server_socket.accept()
        print(f"Client connected from {client_addr}")

        while True:
            try:
                valueX = adcX.read_u16()
                valueY = adcY.read_u16()
                
                message =  f"{valueX},{valueY}\n"  #We are trying to send the x- and y values here
                conn.send((message + "\n").encode())
                print(f"Sent: {message}")
                time.sleep(0.15)
                
                if (valueX - 50500)<0:
                    speedX = (valueX - 50500) / 24000*100
                else:
                    speedX = (valueX - 50500) / 14000*100
                    
                if (valueY - 50300)<0:
                    speedY = (valueY - 50300) / 24000*100
                else:
                    speedY = (valueY - 50300) / 14000*100
                    
                speed = math.sqrt(speedX**2 + speedY**2)
                
                oled.fill(0)
                oled.text("Robot Speed:", 0, 0)
                oled.text("{:.1f}%".format(speed), 0, 20)
                oled.show()

            except OSError:
                print(f"Client {client_addr} disconnected")
                conn.close()
                break

    except KeyboardInterrupt:
        print("Server closed.")
        break
