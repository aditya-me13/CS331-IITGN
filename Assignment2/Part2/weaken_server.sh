# Store initial kernel parameters for later restoration
echo "Backing up existing kernel settings..."
initial_backlog=$(sysctl -n net.ipv4.tcp_max_syn_backlog)
initial_syncookies=$(sysctl -n net.ipv4.tcp_syncookies)
initial_retries=$(sysctl -n net.ipv4.tcp_synack_retries)

echo "Saved values:"
echo "net.ipv4.tcp_max_syn_backlog = $initial_backlog"
echo "net.ipv4.tcp_syncookies = $initial_syncookies"
echo "net.ipv4.tcp_synack_retries = $initial_retries"

# Modify settings to make the server more susceptible to SYN flood
echo "Applying modified network parameters..."
sudo sysctl -w net.ipv4.tcp_max_syn_backlog=128
sudo sysctl -w net.ipv4.tcp_syncookies=0
sudo sysctl -w net.ipv4.tcp_synack_retries=1

echo "Updated parameters:"
sudo sysctl net.ipv4.tcp_max_syn_backlog
sudo sysctl net.ipv4.tcp_syncookies
sudo sysctl net.ipv4.tcp_synack_retries

# Generate a script for restoring original settings
cat > reset_kernel_config.sh << EOF
#!/bin/bash
# reset_kernel_config.sh - Revert kernel parameters to their original values

echo "Reverting kernel settings to defaults..."
sudo sysctl -w net.ipv4.tcp_max_syn_backlog=$initial_backlog
sudo sysctl -w net.ipv4.tcp_syncookies=$initial_syncookies
sudo sysctl -w net.ipv4.tcp_synack_retries=$initial_retries

echo "Restored values:"
sudo sysctl net.ipv4.tcp_max_syn_backlog
sudo sysctl net.ipv4.tcp_syncookies
sudo sysctl net.ipv4.tcp_synack_retries
EOF

chmod +x reset_kernel_config.sh
echo "Run ./reset_kernel_config.sh to revert settings."
