# NAT Experiment with Mininet

This repository contains code for running advanced NAT (Network Address Translation) experiments using Mininet, Open vSwitch, and Python.

## Overview

This experiment simulates a network environment with NAT functionality to demonstrate address translation concepts and measure performance metrics. The simulation creates a configurable topology with internal and external networks separated by a NAT device.

## Prerequisites

Before running the experiment, ensure you have the following installed:

- Linux environment (Ubuntu recommended)
- Mininet (for network emulation)
- Python 3.x
- Open vSwitch
- iperf3 (for performance testing)
- Root privileges (required for Mininet, iptables, and network configuration)

## Installation

### Install Mininet

```bash
sudo apt-get update
sudo apt-get install -y mininet
```

### Install Open vSwitch

```bash
sudo apt-get install -y openvswitch-switch
```

### Install iperf3

```bash
sudo apt-get install -y iperf3
```

### Install Python dependencies

```bash
sudo pip3 install mininet
```

## Usage

### Running the Experiment

1. Save the Python code into a file named `network_nat_advanced.py`

2. Execute the script with root privileges:

```bash
sudo python3 network_nat_advanced.py
```

3. The script will automatically:
   - Create the specified network topology
   - Configure NAT rules using iptables
   - Run basic connectivity tests


