# Part1: Congestion Control Coparison with Mininet

## Prerequisites
Ensure you have the necessary dependencies installed on your Linux-based system.

### Install Mininet and iperf3
```sh
sudo apt-get update
sudo apt-get install mininet iperf3 -y
```

### Install Required Python Packages
```sh
pip install mininet argparse
```

## Running the Main Script
Use the following command format to run the script:
```sh
sudo python3 script.py --option <option> --algo <algorithm> [--loss <loss_percentage>]
```

### Arguments:
- `--option`: Specifies the experiment type (choose from `a`, `b`, `c`, `d`).
- `--algo`: Specifies the TCP congestion control algorithm (choose from `vegas`, `highspeed`, `reno`, `cubic`, `bbr`, `htcp`).
- `--loss`: (Optional) Specifies packet loss percentage (only relevant for experiment `d`).

### Experiment Options
- **Option `a`**: Single client H1 running TCP with the specified congestion control algorithm.
- **Option `b`**: Staggered clients (H1, H3, H4) connecting to the server at different times.
- **Option `c`**: Bandwidth-constrained setup with multiple clients using different ports.
- **Option `d`**: Similar to option `c`, but with an added loss parameter affecting link quality.

### Example Commands
Run experiment `a` with TCP Reno:
```sh
sudo python3 script.py --option a --algo reno
```

Run experiment `d` with TCP BBR and 5% packet loss:
```sh
sudo python3 script.py --option d --algo bbr --loss 5
```

### Stopping the Experiment
If needed, you can stop Mininet and clean up the network using:
```sh
sudo mn -c
```

## Analysis Script:

### Overview
This script analyzes PCAP files to calculate key network metrics such as:
- Throughput
- Goodput
- Maximum Window Size
- Packet Loss Rate

### Installation
Before running the script, install the required dependencies:

```bash
pip install pyshark scapy pandas
```

### Capture using Wireshark:
While the script is running, simultaneously open Wireshark to capture packets on the `s4-eth2` interface. This will help in analyzing the congestion control mechanism in action. Save the `.pcap` file in the `pcap_files` directory for future reference.

### Usage:
Run analysis without any duration filter:
```bash
python analyze_pcap.py
```

Run analysis for a specific duration (e.g., 15s to 30s for part b):
```bash
python analyze_pcap.py --start 15 --end 30
```

This will be saved as entry `filename_start_end` in the `pcap_analysis.csv` file.

### Notice:
- Make sure that the pcap files are present in the `pcap_files` directory before running the analysis script.
- The script updates the existing CSV file instead of creating a new one.
- If no duration is specified, the entire PCAP file is analyzed, and the filename remains unchanged.
- The script avoids re-analyzing the same file for the same duration if the entry already exists in the CSV file.


