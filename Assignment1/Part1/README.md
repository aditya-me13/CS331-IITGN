# Packet Sniffer Analysis and Metrics Extraction

## Overview

This project involves modifying a functional packet sniffer to analyze network traffic and extract key metrics. It includes:

1. Capturing and replaying network traffic using `tcpreplay`.
2. Extracting various network metrics from `.pcap` files.
3. Generating visualizations and statistical data from the captured packets.
4. Measuring network speed performance under different configurations.

## Requirements

Ensure you have the following installed:

- Python 3.x
- Scapy (`pip install scapy`)
- Matplotlib (`pip install matplotlib`)
- tqdm (`pip install tqdm`)
- Wireshark (optional for `.pcap` analysis)
- `tcpreplay` for replaying captured packets
- `libpcap` and `pcap` for C++-based packet sniffing

## Files Included

- `analyze_pcap.py`: Python script for processing `.pcap` files and extracting metrics.
- `packet_sniffer.cpp`: C++ program for live packet capture.
- `Captured.pcap`: Sample `.pcap` file for testing.
- `flows_by_source.csv`: Output file containing source IP flow counts.
- `flows_by_destination.csv`: Output file containing destination IP flow counts.
- `data_transferred.csv`: Output file containing data transferred per unique source-destination pair.
- `unique_pairs.csv`: Output file containing unique source-destination pairs.

## Instructions to Execute

### Step 1: Compile and Run the Packet Sniffer

1. Compile the C++ packet sniffer:
   ```sh
   g++ packet_sniffer.cpp -o packet_sniffer -lpcap
   ```
2. Run the packet sniffer on a network interface (e.g., `eth0`):
   ```sh
   sudo ./packet_sniffer eth0
   ```
   The program will save captured packets in a `.pcap` file with a timestamped filename.

### Step 2: Replay the Captured Packets

1. Use `tcpreplay` to replay the `.pcap` file:
   ```sh
   sudo tcpreplay -i eth0 1.pcap
   ```
The Packets captured by the sniffer program are stored and renamed as captured.pcap and analysis is run on the captured.pcap file

### Step 3: Analyze the Captured Packets

1. Run the Python script to analyze the captured packets:
   ```sh
   python analyze.py
   ```
2. The script outputs:
   - Total packets and data transferred.
   - Minimum, maximum, and average packet sizes.
   - Packet size distribution histogram.
   - Unique source-destination pairs.
   - Flow counts for each source and destination IP.
   - Source-destination pair with the highest data transfer.
   - CSV files containing extracted data.

## Metrics Extracted

1. **Total Data and Packet Statistics**

   - Total packets transferred.
   - Total data transferred in bytes.
   - Minimum, maximum, and average packet sizes.
   - Histogram of packet size distribution.

2. **Source-Destination Pairs**

   - Unique (source IP\:port, destination IP\:port) pairs.
   - CSV file (`unique_pairs.csv`) storing all unique connections.

3. **IP Flow Analysis**

   - Dictionary mapping each IP to total flows where it appears as a source.
   - Dictionary mapping each IP to total flows where it appears as a destination.
   - CSV files (`flows_by_source.csv` and `flows_by_destination.csv`).

4. **Top Data Transfer Pair**

   - Identifies the (source IP\:port, destination IP\:port) pair transferring the most data.

5. **Speed Performance Analysis**

   - Maximum packets per second (pps) and throughput in Mbps.
   - Performance comparisons:
     - Running `tcpreplay` and sniffer on the same Laptop.
     - Running `tcpreplay` on one machine and the sniffer on another.

## Results and Outputs

- Key statistics will be printed in the console.
- Data summaries and metrics will be stored in `.csv` files.
- A histogram visualization will be displayed showing packet size distribution.

