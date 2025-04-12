from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel
import time

class LoopTopo(Topo):
    def build(self):
        # Switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')

        # Hosts with IPs
        h1 = self.addHost('h1', ip='10.0.0.2/24')
        h2 = self.addHost('h2', ip='10.0.0.3/24')
        h3 = self.addHost('h3', ip='10.0.0.4/24')
        h4 = self.addHost('h4', ip='10.0.0.5/24')
        h5 = self.addHost('h5', ip='10.0.0.6/24')
        h6 = self.addHost('h6', ip='10.0.0.7/24')
        h7 = self.addHost('h7', ip='10.0.0.8/24')
        h8 = self.addHost('h8', ip='10.0.0.9/24')

        # Host-Switch Links (5ms)
        self.addLink(h1, s1, cls=TCLink, delay='5ms')
        self.addLink(h2, s1, cls=TCLink, delay='5ms')
        self.addLink(h3, s2, cls=TCLink, delay='5ms')
        self.addLink(h4, s2, cls=TCLink, delay='5ms')
        self.addLink(h5, s3, cls=TCLink, delay='5ms')
        self.addLink(h6, s3, cls=TCLink, delay='5ms')
        self.addLink(h7, s4, cls=TCLink, delay='5ms')
        self.addLink(h8, s4, cls=TCLink, delay='5ms')

        # Switch-Switch Links (7ms)
        self.addLink(s1, s2, cls=TCLink, delay='7ms')
        self.addLink(s2, s3, cls=TCLink, delay='7ms')
        self.addLink(s3, s4, cls=TCLink, delay='7ms')
        self.addLink(s4, s1, cls=TCLink, delay='7ms')
        self.addLink(s1, s3, cls=TCLink, delay='7ms')  # This introduces a loop

def run():
    setLogLevel('info')
    topo = LoopTopo()
    net = Mininet(topo=topo, link=TCLink)
    net.start()

    output_file = "ping_results_without_stp.txt"

    with open(output_file, "w") as f:
        f.write("*** Running Ping Tests WITHOUT STP (Expect Loop Issues) ***\n\n")

        for i in range(3):
            f.write(f"--- Round {i+1} ---\n")

            f.write("Ping h1 -> h3\n")
            f.write(net.get('h1').cmd('ping -c 1 10.0.0.4'))

            f.write("Ping h5 -> h7\n")
            f.write(net.get('h5').cmd('ping -c 1 10.0.0.8'))

            f.write("Ping h8 -> h2\n")
            f.write(net.get('h8').cmd('ping -c 1 10.0.0.3'))

            f.write("\n\n")
            if i < 2:
                time.sleep(30)

    CLI(net)
    net.stop()

if __name__ == '__main__':
    run()