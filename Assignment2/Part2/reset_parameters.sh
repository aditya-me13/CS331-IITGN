#!/bin/bash
# reset_kernel_params.sh - Reset kernel parameters to predefined values

echo "Reverting kernel parameters to their previous settings..."

sudo sysctl -w net.ipv4.tcp_max_syn_backlog=8096
sudo sysctl -w net.ipv4.tcp_syncookies=0
sudo sysctl -w net.ipv4.tcp_synack_retries=1

echo "Updated kernel parameters:"
sudo sysctl net.ipv4.tcp_max_syn_backlog
sudo sysctl net.ipv4.tcp_syncookies
sudo sysctl net.ipv4.tcp_synack_retries
