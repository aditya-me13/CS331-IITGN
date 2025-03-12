import os
import pyshark
import pandas as pd
import argparse
from scapy.all import rdpcap, TCP, IP

def filter_pcap_by_time(pcap, start_time, end_time):
    return [pkt for pkt in pcap if start_time <= float(pkt.sniff_time.timestamp()) <= end_time]

def calculate_throughput(pcap):
    if not pcap:
        return 0
    first_pkt_time = float(pcap[0].sniff_time.timestamp())
    last_pkt_time = float(pcap[-1].sniff_time.timestamp())
    total_bytes = sum(int(pkt.length) for pkt in pcap if hasattr(pkt, 'length'))
    duration = last_pkt_time - first_pkt_time
    return (total_bytes * 8 / duration) if duration > 0 else 0

def calculate_goodput(pcap):
    if not pcap:
        return 0
    tcp_data_bytes = sum(int(pkt.tcp.len) for pkt in pcap if hasattr(pkt, 'tcp') and hasattr(pkt.tcp, 'len'))
    first_pkt_time = float(pcap[0].sniff_time.timestamp())
    last_pkt_time = float(pcap[-1].sniff_time.timestamp())
    duration = last_pkt_time - first_pkt_time
    return (tcp_data_bytes * 8 / duration) if duration > 0 else 0

def calculate_max_window(pcap):
    return max((int(pkt.tcp.window_size_value) for pkt in pcap if hasattr(pkt, 'tcp') and hasattr(pkt.tcp, 'window_size_value')), default=0)

def calculate_packet_loss_rate(pcap_file):
    packets = rdpcap(pcap_file)
    sent_packets = {}
    for pkt in packets:
        if pkt.haslayer(TCP) and pkt.haslayer(IP):
            key = (pkt[IP].src, pkt[IP].dst, pkt[TCP].sport, pkt[TCP].dport)
            if pkt[TCP].flags == 2:  # SYN
                sent_packets[key] = sent_packets.get(key, 0) + 1
            elif pkt[TCP].flags in [4, 16]:  # RST or ACK
                if key in sent_packets:
                    sent_packets[key] -= 1
    lost_count = sum(v for v in sent_packets.values() if v > 0)
    total_sent = sum(sent_packets.values())
    return (lost_count / total_sent) if total_sent > 0 else 0

def main():
    parser = argparse.ArgumentParser(description="Analyze PCAP files and extract throughput, goodput, and more.")
    parser.add_argument('--start', type=int, default=None, help="Start time (seconds) for filtering packets")
    parser.add_argument('--end', type=int, default=None, help="End time (seconds) for filtering packets")
    args = parser.parse_args()

    PCAP_FOLDER = "pcap_files"
    output_file = "pcap_analysis.csv"

    existing_df = pd.read_csv(output_file) if os.path.exists(output_file) else pd.DataFrame(columns=["file_name", "throughput", "goodput", "max_window", "loss_rate"])
    processed_files = set(existing_df["file_name"]) if not existing_df.empty else set()

    results = []
    for file in os.listdir(PCAP_FOLDER):
        if (file.endswith(".pcap") or file.endswith('.pcapng')):
            pcap_path = os.path.join(PCAP_FOLDER, file)
            print(f"Processing {file}...")
            try:
                cap = pyshark.FileCapture(pcap_path, display_filter="tcp")
                if args.start is not None and args.end is not None:
                    cap = filter_pcap_by_time(cap, args.start, args.end)
                    file_name = f"{file}_{args.start}_{args.end}"
                else:
                    file_name = file
                
                if file_name in processed_files:
                    print(f"Skipping {file_name}, already processed.")
                    continue

                throughput = calculate_throughput(cap)
                goodput = calculate_goodput(cap)
                max_window = calculate_max_window(cap)
                loss_rate = calculate_packet_loss_rate(pcap_path)
                results.append([file_name, throughput, goodput, max_window, loss_rate])
                cap.close()
            except Exception as e:
                print(f"Error processing {file}: {e}")

    if results:
        new_df = pd.DataFrame(results, columns=["file_name", "throughput", "goodput", "max_window", "loss_rate"])
        final_df = pd.concat([existing_df, new_df], ignore_index=True)
        final_df.to_csv(output_file, index=False)
        print(f"Updated results saved to {output_file}")
    else:
        print("No new PCAP files to process.")

if __name__ == '__main__':
    main()
