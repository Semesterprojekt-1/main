import network
import socket
import time

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
addr = socket.getaddrinfo("0.0.0.0", PORT)[0][-1]  # Listen on all interfaces
server_socket = socket.socket()
server_socket.bind(addr)
server_socket.listen(1)
print(f"Server listening on port {PORT}...")

while True:
    try:
        print("Waiting for client to connect...")
        conn, client_addr = server_socket.accept()
        print(f"Client connected from {client_addr}")

        while True:
            try:
                message = "1"
                conn.send(message.encode())
                print(f"Sent: {message}")
                time.sleep(1)
            except OSError:
                print(f"Client {client_addr} disconnected")
                conn.close()
                break

    except Exception as e:
        print("Server error:", e)
        time.sleep(1)