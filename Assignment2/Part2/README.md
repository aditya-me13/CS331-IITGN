# Part 2: SYN-Flood Attack and Mitigation

## Prerequisites
Ensure that your Linux-based system has the required dependencies installed before proceeding.

### Install Mininet and Required Tools
Run the following command to install all necessary tools:

```sh
sudo apt update && sudo apt install -y python3 python3-pip tcpdump tshark hping3
pip3 install scapy matplotlib tqdm
```

## Experiment Setup
This experiment must be performed on two isolated VMs: one acting as the **Client** and the other as the **Server**.

### File Structure
The required scripts are distributed between the two VMs as follows:

| **Client VM**               | **Server VM**            |
|-----------------------------|--------------------------|
| `tcp_client.py`             | `tcp_server.py`         |
| `syn_flood_attack.py`       | `weaken_server.sh`      |
| `experiment_runner.sh`      | `mitigate_server.sh`    |

Additionally, the `analysis.py` script is used on the **Client VM** to analyze network traffic and generate graphs.

## Experiment Execution

### Step 1: Weaken the Server (Server VM)
Before launching the SYN-Flood attack, configure the server to be more vulnerable by running:

```sh
sudo bash weaken_server.sh
```

### Step 2: Start the Server (Server VM)
Run the TCP server script to start listening for connections:

```sh
sudo python3 tcp_server.py
```

### Step 3: Launch the Experiment (Client VM)
Run the experiment runner script to conduct the SYN-Flood attack:

```sh
sudo bash experiment_runner.sh
```

### Step 4: Analyze Network Traffic (Client VM)
Once the experiment is complete, analyze the captured network traffic using the analysis script:

```sh
sudo python3 analysis.py <your_pcap_file> --server_ip <server_ip> --server_port <server_port>
```

### Step 5: Mitigate the Attack (Server VM)
To enable mitigation techniques and protect the server, run the mitigation script:

```sh
sudo bash mitigate_server.sh
```

After mitigation, restart the server by following **Step 2** again.

## Notes
- Ensure both VMs are properly networked to communicate with each other. (Get the server ip address using `ifconfig` and replace it in the client side scripts wherever mentioned)
- The `analysis.py` script will generate visualizations and statistical summaries of the SYN-Flood attack.

