# Assignment3 Part1

This repo contains Mininet scripts to demonstrate network loops with and without Spanning Tree Protocol (STP).

## Requirements

- Linux-based environment
- Python 3.x
- Mininet

## Run Instructions

0. Download Requirements
   ```bash
   sudo apt-get install mininet
   ```

1. Run the experiment **without STP**:
   ```bash
   sudo python3 network_loops_no_stp.py
   ```

2. Run the experiment **with STP**:
   ```bash
   sudo python3 network_loops_stp.py
   ```

3. The output will be saved in the following respective files:
    - `ping_results_without_stp.txt`
    - `ping_results_with_stp.txt`