# Configuration
SERVER_IP="192.168.56.104"  # Update with your server's IP
SERVER_PORT=8000
ATTACK_DURATION=100
PRE_ATTACK_LEGIT_TRAFFIC=20
POST_ATTACK_LEGIT_TRAFFIC=20
PCAP_FILE="capture.pcap"
ATTACK_METHOD="hping3"  # Options: hping3, raw
ATTACK_RATE=40000        # Packets per second (used only with raw method)

# Ensure the script is executed with root privileges
if [ "$EUID" -ne 0 ]; then
    echo "This script must be run as root. Use sudo."
    exit 1
fi

# Install necessary dependencies if missing
echo "Verifying required dependencies..."
which tcpdump >/dev/null || apt-get -y install tcpdump
which python3 >/dev/null || apt-get -y install python3
which hping3 >/dev/null || apt-get -y install hping3
pip3 list | grep -q scapy || pip3 install scapy

echo "Starting the experiment..."
echo "Ensure that the server is running at $SERVER_IP:$SERVER_PORT"

# Step 1: Start packet capture
echo "Initializing packet capture..."
tcpdump -i any -w "$PCAP_FILE" tcp port $SERVER_PORT -v &
TCPDUMP_PID=$!
sleep 2  # Allow tcpdump to start properly

# Step 2: Begin legitimate traffic
echo "Generating legitimate traffic..."
python3 tcp_client.py $SERVER_IP &
LEGITIMATE_PID=$!
echo "Legitimate traffic process ID: $LEGITIMATE_PID"

# Step 3: Introduce attack after a delay
echo "Waiting $PRE_ATTACK_LEGIT_TRAFFIC seconds before initiating the attack..."
sleep $PRE_ATTACK_LEGIT_TRAFFIC

echo "Launching SYN flood attack..."
python3 syn_flood_attack.py --target $SERVER_IP --port $SERVER_PORT --duration $ATTACK_DURATION --method $ATTACK_METHOD --rate $ATTACK_RATE &
ATTACK_PID=$!

# Step 4: Maintain attack duration
echo "Attack in progress for $ATTACK_DURATION seconds..."
sleep $ATTACK_DURATION

echo "Stopping the attack..."
kill -SIGINT $ATTACK_PID 2>/dev/null || true
wait $ATTACK_PID 2>/dev/null || true

# Step 5: Continue legitimate traffic for a while after the attack
echo "Maintaining legitimate traffic for $POST_ATTACK_LEGIT_TRAFFIC more seconds..."
sleep $POST_ATTACK_LEGIT_TRAFFIC

echo "Stopping legitimate traffic..."
kill -SIGINT $LEGITIMATE_PID
wait $LEGITIMATE_PID

# Step 6: Stop packet capture
echo "Finalizing packet capture..."
kill -SIGINT $TCPDUMP_PID
wait $TCPDUMP_PID

echo "Experiment completed successfully!"
echo "Captured traffic is saved in $PCAP_FILE"
echo "Proceed with traffic analysis."
