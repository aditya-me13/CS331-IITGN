#!/usr/bin/env python3
# tcp_client.py - Simulates legitimate TCP traffic to a server

import socket
import time
import sys
import threading
import signal

# Configuration
SERVER_IP = '192.168.56.104'  # Replace with the target server's IP
SERVER_PORT = 8000
RUNNING = True

def handle_exit(sig, frame):
    """Gracefully handle termination (Ctrl+C)"""
    global RUNNING
    print("\nShutting down client...")
    RUNNING = False
    sys.exit(0)

def send_request():
    """Establish a TCP connection and send a request to the server"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Measure connection time
            start_time = time.time()
            s.connect((SERVER_IP, SERVER_PORT))
            
            # Send message
            s.sendall(b'Hello from a legitimate client\n')
            
            # Receive response
            data = s.recv(1024)
            end_time = time.time()
            
            print(f"Request completed in {end_time - start_time:.4f} seconds, received: {data.decode().strip()}")
            return True
    except socket.timeout:
        print("Connection timed out")
    except ConnectionRefusedError:
        print("Connection refused - server may be down or overloaded")
    except Exception as e:
        print(f"Error: {e}")
    return False

def main():
    """Main function to send repeated requests"""
    global SERVER_IP
    if len(sys.argv) > 1:
        SERVER_IP = sys.argv[1]
    
    print(f"Starting TCP client to {SERVER_IP}:{SERVER_PORT}")
    print("Press Ctrl+C to stop")

    signal.signal(signal.SIGINT, handle_exit)
    
    success_count, fail_count = 0, 0

    while RUNNING:
        if send_request():
            success_count += 1
        else:
            fail_count += 1
        
        time.sleep(0.75)  # Randomized delay

        # Display statistics every 10 requests
        if (success_count + fail_count) % 10 == 0:
            print(f"Statistics: {success_count} successful, {fail_count} failed requests")

if __name__ == "__main__":
    main()
