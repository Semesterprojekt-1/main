import network
import socket
import time

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
                if line:  # skip empty lines
                    print("Received:", line)

    except OSError as e:
        print("Connection error:", e)
        s.close()
        time.sleep(1)

