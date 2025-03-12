#!/bin/bash
# mitigate_server.sh - Implement SYN flood protection measures

# Enable SYN cookies to prevent SYN flood attacks
echo "Activating SYN cookies for enhanced protection..."
sudo sysctl -w net.ipv4.tcp_syncookies=1

# Increase backlog queue size to handle more connections
echo "Tuning TCP backlog queue for better resilience..."
sudo sysctl -w net.ipv4.tcp_max_syn_backlog=2048

# Adjust SYN-ACK retries to optimize response behavior
echo "Modifying SYN-ACK retry count..."
sudo sysctl -w net.ipv4.tcp_synack_retries=2

echo "SYN flood protection settings have been applied."
echo "Updated kernel parameters:"
sudo sysctl net.ipv4.tcp_syncookies
sudo sysctl net.ipv4.tcp_max_syn_backlog
sudo sysctl net.ipv4.tcp_synack_retries

echo "Current firewall rules:"
sudo iptables -L -v
