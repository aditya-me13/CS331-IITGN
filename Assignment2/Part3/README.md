# Task3: TCP Performance Analysis
---

This project analyzes the effect of **Nagle’s Algorithm** and **Delayed ACK** on TCP performance by transferring a **4 KB file** over a **TCP connection** at **40 bytes/second**. The traffic is captured using **Wireshark** and analyzed with `analyze_pcap.py`.


## **Running the Server and Client**
The server listens for incoming connections and receives data. The client connects to the server and transmits the **4 KB file** at **40 bytes/second**.

### **Usage:**
```bash
python tcp_server.py --nagle <0|1> --delayed_ack <0|1>
python tcp_client.py --nagle <0|1> --delayed_ack <0|1>
```

### **Arguments:**
- `--nagle 1` → Enables **Nagle’s Algorithm**
- `--nagle 0` → Disables **Nagle’s Algorithm**
- `--delayed_ack 1` → Enables **Delayed ACK**
- `--delayed_ack 0` → Disables **Delayed ACK**

### **Example Commands:**
```bash
python tcp_server.py --nagle 1 --delayed_ack 1  # Nagle ON, Delayed-ACK ON
python tcp_server.py --nagle 1 --delayed_ack 0  # Nagle ON, Delayed-ACK OFF
python tcp_client.py --nagle 0 --delayed_ack 1  # Nagle OFF, Delayed-ACK ON
python tcp_client.py --nagle 0 --delayed_ack 0  # Nagle OFF, Delayed-ACK OFF
```

## **Capturing Network Traffic with Wireshark**
Run **Wireshark** or **tcpdump** parallelly to capture packets:

### **Using Wireshark:**
1. Open **Wireshark**.
2. Start capturing on the relevant network interface (e.g., `eth0` or `lo` for localhost).
3. Filter traffic using:
   ```
   tcp.port == 5001
   ```
4. Save the capture as `capture.pcap`.

### **Using tcpdump:**
```bash
sudo tcpdump -i any port 5001 -w capture.pcap
```

Save the `.pcap` file into `pcap_files` directory for analysis. Use different names for different configurations.

## **Analyzing the Captured Packets**
After the file transfer completes, analyze the captured traffic using:
```bash
python analyze_pcap.py
```
This script extracts:
- **Throughput** (Total data transmitted / Time)
- **Goodput** (Useful data transmitted / Time)
- **Packet loss rate**
- **Maximum packet size**


## **Notes**
- Ensure the **server is running** before starting the **client**.
- Use **Wireshark** or **tcpdump** to capture traffic for analysis.
- Modify the **transfer rate** in `tcp_client.py` if needed.
