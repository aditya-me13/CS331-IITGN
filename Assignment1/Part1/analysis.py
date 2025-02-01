
from scapy.all import rdpcap
import matplotlib.pyplot as plt
from collections import defaultdict
import csv
from tqdm import tqdm  # Import tqdm for progress tracking

# Step 1: Load the pcap file
pcap_file = "Captured.pcap"
packets = rdpcap(pcap_file)

# Step 2: Analyze packet sizes
packet_sizes = [len(pkt) for pkt in packets]
total_packets = len(packets)
total_data = sum(packet_sizes)
min_size = min(packet_sizes)
max_size = max(packet_sizes)
avg_size = total_data / total_packets

print(f"Total Packets: {total_packets}")
print(f"Total Data: {total_data} bytes")
print(f"Min Packet Size: {min_size} bytes")
print(f"Max Packet Size: {max_size} bytes")
print(f"Average Packet Size: {avg_size:.2f} bytes")

# Plot histogram
plt.hist(packet_sizes, bins=20, color='blue', edgecolor='black')
plt.title("Packet Size Distribution")
plt.xlabel("Packet Size (bytes)")
plt.ylabel("Frequency")
plt.show()

# Step 3: Initialize dictionaries and sets
flows_by_src = defaultdict(int)    # Total flows where IP is source
flows_by_dst = defaultdict(int)    # Total flows where IP is destination
data_by_pair = defaultdict(int)    # Data transferred per (source IP:port, destination IP:port)
unique_pairs = set()               # Unique source-destination pairs

# Step 4: Process packets with tqdm progress tracking
print("\nProcessing packets...")
for pkt in tqdm(packets, desc="Analyzing", unit="pkt"):
    if pkt.haslayer('IP') and pkt.haslayer('TCP'):
        src_ip = pkt['IP'].src
        dst_ip = pkt['IP'].dst
        src_port = pkt['TCP'].sport
        dst_port = pkt['TCP'].dport
        packet_size = len(pkt)

        # Create source-destination key (including ports)
        src_dst_key = (f"{src_ip}:{src_port}", f"{dst_ip}:{dst_port}")

        # Add to unique pairs set
        unique_pairs.add(src_dst_key)

        # Count flows by IP
        flows_by_src[src_ip] += 1
        flows_by_dst[dst_ip] += 1

        # Track data transferred per source-destination pair
        data_by_pair[src_dst_key] += packet_size

# Step 5: Save dictionaries to CSV files
def save_dict_to_csv(dictionary, filename, header):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        for key, value in dictionary.items():
            writer.writerow([key, value])

# Save flows by source IP
save_dict_to_csv(flows_by_src, "flows_by_source.csv", ["Source IP", "Flow Count"])

# Save flows by destination IP
save_dict_to_csv(flows_by_dst, "flows_by_destination.csv", ["Destination IP", "Flow Count"])

# Save data transferred per source-destination pair
with open("data_transferred.csv", mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Source:Port", "Destination:Port", "Data Transferred (bytes)"])
    for (src, dst), data in data_by_pair.items():
        writer.writerow([src, dst, data])

# Save unique source-destination pairs
with open("unique_pairs.csv", mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Source:Port", "Destination:Port"])
    for src, dst in unique_pairs:
        writer.writerow([src, dst])

# Step 6: Find the source-destination pair that transferred the most data
top_src_dst_pair = max(data_by_pair, key=data_by_pair.get)
top_data_transferred = data_by_pair[top_src_dst_pair]

print(f"\nTop Source-Destination Pair: {top_src_dst_pair} transferred {top_data_transferred} bytes.")
print("Dictionaries saved to CSV files successfully.")
print(f"Total Unique Source-Destination Pairs: {len(unique_pairs)}")
