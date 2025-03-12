import socket
import time
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description="TCP Server with Nagle's Algorithm and Delayed ACK configuration.")
parser.add_argument("--nagle", type=int, choices=[0, 1], required=True, help="Enable (1) or Disable (0) Nagle's Algorithm")
parser.add_argument("--delayed_ack", type=int, choices=[0, 1], required=True, help="Enable (1) or Disable (0) Delayed ACK")
args = parser.parse_args()

NAGLE_ENABLED = bool(args.nagle)
DELAYED_ACK = bool(args.delayed_ack)

# Configuration
HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 5001

# Create and configure socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"Server listening on port {PORT} | Nagle: {NAGLE_ENABLED}, Delayed ACK: {DELAYED_ACK}")
conn, addr = server_socket.accept()
print("Connected by", addr)

# Configure Nagle’s Algorithm
conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, not NAGLE_ENABLED)

# Configure Delayed ACK if supported
if hasattr(socket, "TCP_QUICKACK"):
    conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_QUICKACK, not DELAYED_ACK)

received_data = b""
start_time = time.time()

while True:
    data = conn.recv(1024)
    if not data:
        break
    received_data += data

end_time = time.time()
print(f"Received {len(received_data)} bytes in {end_time - start_time:.2f} seconds.")

conn.close()
server_socket.close()
