import network
import socket
import time

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
s = socket.socket()
s.connect(server_addr)
print("Connected to server, waiting for data...")

while True:
    data = s.recv(1024)  # Receive up to 1024 bytes
    if data:
        print("Received:", data.decode())
    else:
        break
