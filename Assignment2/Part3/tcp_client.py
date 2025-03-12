import socket
import time
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description="TCP Client with Nagle's Algorithm and Delayed ACK configuration.")
parser.add_argument("--nagle", type=int, choices=[0, 1], required=True, help="Enable (1) or Disable (0) Nagle's Algorithm")
parser.add_argument("--delayed_ack", type=int, choices=[0, 1], required=True, help="Enable (1) or Disable (0) Delayed ACK")
args = parser.parse_args()

NAGLE_ENABLED = bool(args.nagle)
DELAYED_ACK = bool(args.delayed_ack)

# Configuration
SERVER_IP = '127.0.0.1'  # Change this to the server's IP
PORT = 5001
FILE_SIZE = 4096  # 4 KB file
TRANSFER_RATE = 40  # 40 bytes/second

# Create file data
file_data = b"A" * FILE_SIZE

# Create and configure socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, PORT))

# Configure Nagle’s Algorithm
client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, not NAGLE_ENABLED)

# Configure Delayed ACK if supported
if hasattr(socket, "TCP_QUICKACK"):
    client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_QUICKACK, not DELAYED_ACK)

print(f"Client connected to {SERVER_IP}:{PORT} | Nagle: {NAGLE_ENABLED}, Delayed ACK: {DELAYED_ACK}")

# Send data at a controlled rate
start_time = time.time()

for i in range(0, len(file_data), TRANSFER_RATE):
    chunk = file_data[i:i+TRANSFER_RATE]
    client_socket.send(chunk)
    time.sleep(1)  # 1-second delay for 40 B/s rate

end_time = time.time()

print(f"File sent successfully in {end_time - start_time:.2f} seconds.")

client_socket.close()
