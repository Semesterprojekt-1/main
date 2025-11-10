import network
import socket
import time

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

conn, client_addr = s.accept()
print("Client connected from:", client_addr)

# Send data continuously
while True:
    message = "1"
    conn.send(message.encode())  # Send bytes
    print("Sent:", message)
    time.sleep(1)  # Send every 1 second

