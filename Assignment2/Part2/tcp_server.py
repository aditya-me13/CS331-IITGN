#!/usr/bin/env python3
# lightweight_tcp_server.py - A basic TCP server for handling incoming connections

import socket
import threading
import time

# Server Configuration
LISTEN_ADDRESS = '0.0.0.0'  # Accept connections on all available interfaces
LISTEN_PORT = 8000          # Port to bind the server to

def client_handler(connection, client_address):
    """Process a single client connection"""
    print(f"Incoming connection from {client_address}")
    session_start = time.time()
    
    try:
        # Send a welcome message
        connection.sendall(b'Greetings from the server!\n')
    finally:
        connection.close()
        session_end = time.time()
        print(f"Connection with {client_address} closed after {session_end - session_start:.4f} seconds")

def run_server():
    """Initialize and run the server"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server.bind((LISTEN_ADDRESS, LISTEN_PORT))
            server.listen(5)
            print(f"Server active on {LISTEN_ADDRESS}:{LISTEN_PORT}")
            
            while True:
                conn, addr = server.accept()
                thread = threading.Thread(target=client_handler, args=(conn, addr), daemon=True)
                thread.start()
        except KeyboardInterrupt:
            print("Server shutting down gracefully...")
        except Exception as err:
            print(f"Encountered an issue: {err}")

if __name__ == "__main__":
    run_server()