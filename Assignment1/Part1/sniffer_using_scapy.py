from scapy.all import sniff, wrpcap
import threading
import time

# Global variables to store captured packets and count total packets
captured_packets = []
total_packets = 0  # Counter for total packets captured
start_time = time.time()  # Start time to calculate the PPS and Mbps

# Function to capture packets
def packet_handler(pkt):
    global captured_packets, total_packets
    captured_packets.append(pkt)
    total_packets += 1  # Increment total count
    # print(pkt.summary())  # Optional, to see packet summary during capture

# Function to print packets every 5 seconds and calculate speed
def print_packets_periodically():
    while True:
        time.sleep(5)  # Wait for 5 seconds
        if captured_packets:
            print(f"\nCaptured {len(captured_packets)} packets in the last 5 seconds.")
            print(f"📌 Total packets captured so far: {total_packets}")  # Print total count
        else:
            print("\nNo packets captured in the last 5 seconds.")
            print(f"📌 Total packets captured so far: {total_packets}")  # Print total count

# Function to calculate PPS (Packets Per Second) and Mbps (Megabits Per Second)
def calculate_speed():
    global start_time, total_packets
    current_time = time.time()
    elapsed_time = current_time - start_time  # Total time elapsed in seconds
    pps = total_packets / elapsed_time  # Packets per second
    total_bytes = sum(len(pkt) for pkt in captured_packets)  # Total bytes captured
    mbps = (total_bytes * 8) / (elapsed_time * 1e6)  # Convert bytes to Megabits per second
    return pps, mbps

# Function to save packets to a pcap file at the end
def save_to_pcap():
    print("\nSaving captured packets to file...")
    wrpcap("captured_packets.pcap", captured_packets)  # Write to pcap file
    print("Captured packets saved to captured_packets.pcap")

# Start the periodic print function in a separate thread
threading.Thread(target=print_packets_periodically, daemon=True).start()

# Start sniffing packets
try:
    print("Sniffing packets... (Press Ctrl+C to stop)")
    sniff(iface="eth0", prn=packet_handler, store=False)
except KeyboardInterrupt:
    print("\nCapture stopped manually by user.")

# After capture ends, calculate PPS and Mbps
pps, mbps = calculate_speed()
print(f"\nCapture session finished.")
print(f"Total packets captured: {total_packets}")
print(f"Total PPS (Packets Per Second): {pps:.2f} pps")
print(f"Total Mbps (Megabits Per Second): {mbps:.2f} Mbps")

# Save captured packets to a pcap file
save_to_pcap()
