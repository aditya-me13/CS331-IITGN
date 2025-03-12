import argparse
import subprocess
import sys
import pickle
import os
import matplotlib.pyplot as plt
from tqdm import tqdm

def run_tshark(pcap_file):
    print("[INFO] Running tshark to extract packet data...")
    fields = [
        "-e", "frame.time_epoch", "-e", "ip.src", "-e", "ip.dst",
        "-e", "tcp.srcport", "-e", "tcp.dstport", "-e", "tcp.flags.syn",
        "-e", "tcp.flags.ack", "-e", "tcp.flags.fin", "-e", "tcp.flags.reset"
    ]
    cmd = ["tshark", "-r", pcap_file, "-Y", "tcp", "-T", "fields"] + fields
    try:
        output = subprocess.check_output(cmd, universal_newlines=True).strip().splitlines()
        print(f"[INFO] Extracted {len(output)} packets from the PCAP file.")
        return output
    except subprocess.CalledProcessError as e:
        sys.exit(f"[ERROR] Error running tshark: {e}")

def parse_packets(output):
    print("[INFO] Parsing extracted packet data...")
    packets = []
    for line in tqdm(output, desc="Parsing packets"):
        fields = line.split("\t")
        if len(fields) < 9:
            continue
        try:
            packets.append({
                "time": float(fields[0]), "src": fields[1], "dst": fields[2],
                "sport": fields[3], "dport": fields[4], "syn": fields[5],
                "ack": fields[6], "fin": fields[7], "rst": fields[8]
            })
        except (ValueError, IndexError):
            continue
    print(f"[INFO] Successfully parsed {len(packets)} valid packets.")
    return packets

def analyze_packets(packets, server_ip, server_port):
    print("[INFO] Analyzing TCP connections...")
    connections = {}
    for pkt in tqdm(packets, desc="Processing packets"):
        is_to_server = pkt["dst"] == server_ip and str(pkt["dport"]) == str(server_port)
        if is_to_server:
            conn_tuple = (pkt["src"], pkt["dst"], pkt["sport"], pkt["dport"])
            direction = "c2s"
        elif pkt["src"] == server_ip and str(pkt["sport"]) == str(server_port):
            conn_tuple = (pkt["dst"], pkt["src"], pkt["dport"], pkt["sport"])
            direction = "s2c"
        else:
            continue
        
        syn_flag, ack_flag = pkt["syn"] == "1", pkt["ack"] == "1"
        fin_flag, rst_flag = pkt["fin"] == "1", pkt["rst"] == "1"
        
        if syn_flag and not ack_flag and direction == "c2s":
            connections.setdefault(conn_tuple, {"start": pkt["time"], "end": None, "fin_ack_seen": False})
        
        if conn_tuple in connections and connections[conn_tuple]["end"] is None:
            if rst_flag:
                connections[conn_tuple]["end"] = pkt["time"]
            elif fin_flag and ack_flag:
                connections[conn_tuple]["fin_ack_seen"] = True
            elif ack_flag and connections[conn_tuple]["fin_ack_seen"]:
                connections[conn_tuple]["end"] = pkt["time"]
    print(f"[INFO] Identified {len(connections)} unique TCP connections.")
    return connections

def compute_durations(connections):
    print("[INFO] Computing connection durations...")
    start_times, durations = [], []
    min_start = min(info["start"] for info in connections.values())
    for info in connections.values():
        start_times.append(info["start"] - min_start)
        durations.append(info["end"] - info["start"] if info["end"] else 100.0)
    print("[INFO] Saving sorted connection durations to 'sorted_durations.pkl'")
    pickle.dump(sorted(durations), open("sorted_durations.pkl", "wb"))
    return start_times, durations

def plot_durations(start_times, durations, attack_start, attack_end):
    print("[INFO] Plotting connection durations...")
    plt.figure(figsize=(10, 6))
    plt.scatter(start_times, durations, c='deepskyblue', alpha=0.8, label='TCP connections')
    plt.xlabel("Connection Start Time", fontsize=12, fontweight='bold' )
    plt.ylabel("Connection Duration (s)",  fontsize=12, fontweight='bold')
    plt.title("SYN-Flood Attack in TCP Connections after Mitigation",  fontsize=12, fontweight='bold')
    if attack_start:
        plt.axvline(x=attack_start, color='red', linestyle='-', linewidth=2, label='Attack Start')
    if attack_end:
        plt.axvline(x=attack_end, color='green', linestyle='-', linewidth=2, label='Attack End')
    plt.legend()

    plt.grid(True, which='major', linestyle='-', linewidth=1.2, alpha=0.2, color='black')  # Darker main grid
    plt.grid(True, which='minor', linestyle='--', linewidth=0.6, alpha=0.2, color='gray')  # Lighter minor grid
    plt.minorticks_on()

    plt.xlim(-5, 145)
    plt.ylim(-5, 105)
    plt.savefig("results.png")
    print("[INFO] Saved plot as 'results.png'")
    plt.show()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pcap_file", help="Path to PCAP file")
    parser.add_argument("--server_ip", default="192.168.56.104")
    parser.add_argument("--server_port", type=int, default=8000)
    parser.add_argument("--attack_start", type=float, default=20)
    parser.add_argument("--attack_end", type=float, default=120)
    parser.add_argument("--load_packets", action="store_true")
    parser.add_argument("--load_connections", action="store_true")
    args = parser.parse_args()
    
    packets_pickle, connections_pickle = "packets.pkl", "connections.pkl"
    
    if args.load_packets and os.path.exists(packets_pickle):
        print("[INFO] Loading packet data from cache...")
        packets = pickle.load(open(packets_pickle, "rb"))
    else:
        packets = parse_packets(run_tshark(args.pcap_file))
        pickle.dump(packets, open(packets_pickle, "wb"))
        print("[INFO] Packet data saved to cache.")
    
    if args.load_connections and os.path.exists(connections_pickle):
        print("[INFO] Loading connections from cache...")
        connections = pickle.load(open(connections_pickle, "rb"))
    else:
        connections = analyze_packets(packets, args.server_ip, args.server_port)
        pickle.dump(connections, open(connections_pickle, "wb"))
        print("[INFO] Connections saved to cache.")
    
    start_times, durations = compute_durations(connections)
    plot_durations(start_times, durations, args.attack_start, args.attack_end)

if __name__ == "__main__":
    main()