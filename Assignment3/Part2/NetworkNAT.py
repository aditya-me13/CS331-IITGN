#!/usr/bin/env python3

"""
Custom network topology with NAT implementation using Mininet
"""

import os
import time
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import OVSController, OVSKernelSwitch
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel

class NetworkWithNATTopology(Topo):
    """Custom topology with NAT functionality between internal and external networks"""
    
    def _init_(self):
        """Initialize the topology"""
        super(NetworkWithNATTopology, self)._init_()
        self._create_topology()
        
    def _create_topology(self):
        """Build the network topology with switches, hosts and links"""
        # Create switches
        switches = {}
        for i in range(1, 5):
            switch_name = f's{i}'
            switches[switch_name] = self.addSwitch(switch_name, stp=True)
            
        # Create hosts with their IP addresses
        internal_hosts = {
            'h1': self.addHost('h1', ip='10.1.1.2/24'),
            'h2': self.addHost('h2', ip='10.1.1.3/24')
        }
        
        external_hosts = {
            'h3': self.addHost('h3', ip='10.0.0.4/24'),
            'h4': self.addHost('h4', ip='10.0.0.5/24'),
            'h5': self.addHost('h5', ip='10.0.0.6/24'),
            'h6': self.addHost('h6', ip='10.0.0.7/24'),
            'h7': self.addHost('h7', ip='10.0.0.8/24'),
            'h8': self.addHost('h8', ip='10.0.0.9/24')
        }
        
        # Create NAT router
        nat_router = self.addHost('h9')
        
        # Add links from internal hosts to NAT
        for host in internal_hosts.values():
            self.addLink(host, nat_router, delay='5ms')
            
        # Add link from NAT to external network
        self.addLink(nat_router, switches['s1'], delay='5ms')
        
        # Connect external hosts to switches
        self._connect_external_hosts(external_hosts, switches)
        
        # Interconnect switches to form network backbone
        self._interconnect_switches(switches)
        
    def _connect_external_hosts(self, hosts, switches):
        """Connect external hosts to their respective switches"""
        host_to_switch = {
            'h3': 's2', 'h4': 's2',
            'h5': 's3', 'h6': 's3',
            'h7': 's4', 'h8': 's4'
        }
        
        for host_name, host in hosts.items():
            switch_name = host_to_switch[host_name]
            self.addLink(host, switches[switch_name], delay='5ms')
            
    def _interconnect_switches(self, switches):
        """Create a mesh of connections between switches"""
        switch_connections = [
            ('s1', 's2'), ('s1', 's3'), ('s1', 's4'),
            ('s2', 's3'), ('s3', 's4')
        ]
        
        for sw1, sw2 in switch_connections:
            self.addLink(switches[sw1], switches[sw2], delay='7ms')


def configure_nat(nat_host):
    """Configure NAT routing and bridging"""
    # Create bridge interface
    nat_host.cmd('ip link add name br0 type bridge')
    nat_host.cmd('ip link set br0 up')
    
    # Add internal interfaces to bridge
    nat_host.cmd('ip link set h9-eth0 master br0')
    nat_host.cmd('ip link set h9-eth1 master br0')
    
    # Flush existing IP configurations
    nat_host.cmd("ip addr flush dev h9-eth0")
    nat_host.cmd("ip addr flush dev h9-eth1")
    nat_host.cmd("ip addr flush dev h9-eth2")
    
    # Set internal IP on bridge
    nat_host.cmd('ip addr add 10.1.1.1/24 dev br0')
    
    # Set external IPs
    nat_host.cmd('ip addr add 10.0.0.1/24 dev h9-eth2')
    nat_host.cmd('ip addr add 172.16.10.10/24 dev h9-eth2')
    
    # Enable IP forwarding
    nat_host.cmd('sysctl -w net.ipv4.ip_forward=1')
    
    # Configure NAT rules
    nat_host.cmd('iptables -t nat -F')
    nat_host.cmd('iptables -t nat -A POSTROUTING -s 10.1.1.0/24 -o h9-eth2 -j MASQUERADE')


def configure_routing(net):
    """Configure routing for all hosts"""
    # Set default gateway for internal hosts
    for host_name in ['h1', 'h2']:
        host = net.get(host_name)
        host.cmd('ip route add default via 10.1.1.1')
    
    # Set default gateway for external hosts
    for host_name in ['h3', 'h4', 'h5', 'h6', 'h7', 'h8']:
        host = net.get(host_name)
        host.cmd('ip route add default via 10.0.0.1')


def enable_stp(net):
    """Enable Spanning Tree Protocol on all switches"""
    for sw_name in ['s1', 's2', 's3', 's4']:
        sw = net.get(sw_name)
        sw.cmd('ovs-vsctl set Bridge {} stp_enable=true'.format(sw_name))


def run_connectivity_tests(net):
    """Run connectivity tests between hosts"""
    h1, h2, h5, h6, h8 = net.get('h1', 'h2', 'h5', 'h6', 'h8')
    test_results = {
        'internal_to_external': "",
        'external_to_internal': "",
        'performance': ""
    }
    
    # Test A: Internal hosts pinging external hosts
    print("Test A: Internal hosts pinging external hosts")
    for i in range(3):
        result = h1.cmd('ping -c 4 10.0.0.6')
        test_results['internal_to_external'] += f"\n--- Test {i+1}/3: Ping h5 from h1 ---\n{result}"
        
        result = h2.cmd('ping -c 4 10.0.0.4')
        test_results['internal_to_external'] += f"\n--- Test {i+1}/3: Ping h3 from h2 ---\n{result}"
    
    # Test B: External hosts pinging internal hosts
    print("Test B: External hosts pinging internal hosts")
    for i in range(3):
        result = h8.cmd('ping -c 4 10.1.1.2')
        test_results['external_to_internal'] += f"\n--- Test {i+1}/3: Ping h1 from h8 ---\n{result}"
        
        result = h6.cmd('ping -c 4 10.1.1.3')
        test_results['external_to_internal'] += f"\n--- Test {i+1}/3: Ping h2 from h6 ---\n{result}"
    
    # Test C: Performance tests with iperf3
    print("Test C: Performance tests with iperf3 (120s each)")
    test_results['performance'] += run_performance_tests(h1, h2, h6, h8)
    
    # Write results to files
    for test_type, content in test_results.items():
        with open(f"output_{test_type}.txt", "w") as f:
            f.write(content)


def run_performance_tests(h1, h2, h6, h8):
    """Run iperf3 performance tests between hosts"""
    performance_output = ""
    
    # Test 1: h6 -> h1
    performance_output += "\n--- iPerf3 Test: h6 client -> h1 server ---\n"
    h1.cmd('iperf3 -s -D')
    time.sleep(2)
    
    for i in range(3):
        result = h6.cmd('iperf3 -c 10.1.1.2 -t 120')
        performance_output += f"\n--- iPerf3 Test {i+1}/3: h6 -> h1 ---\n{result}"
        time.sleep(5)
    
    h1.cmd('pkill iperf3')
    
    # Test 2: h2 -> h8
    performance_output += "\n--- iPerf3 Test: h2 client -> h8 server ---\n"
    h8.cmd('iperf3 -s -D')
    time.sleep(2)
    
    for i in range(3):
        result = h2.cmd('iperf3 -c 10.0.0.9 -t 120')
        performance_output += f"\n--- iPerf3 Test {i+1}/3: h2 -> h8 ---\n{result}"
        time.sleep(5)
    
    h8.cmd('pkill iperf3')
    
    return performance_output


def main():
    """Main function to setup and run the network simulation"""
    # Clean up any previous Mininet setup
    os.system('mn -c')
    
    # Create network with custom topology
    topo = NetworkWithNATTopology()
    net = Mininet(
        topo=topo,
        controller=OVSController,
        switch=OVSKernelSwitch,
        link=TCLink
    )
    
    # Start network
    net.start()
    
    # Configure network
    enable_stp(net)
    configure_nat(net.get('h9'))
    configure_routing(net)
    
    print("Waiting 30 seconds for network to stabilize...")
    time.sleep(30)
    
    # Test connectivity
    net.pingAll()
    
    # Run detailed connectivity tests
    run_connectivity_tests(net)
    
    # Stop network
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    main()
