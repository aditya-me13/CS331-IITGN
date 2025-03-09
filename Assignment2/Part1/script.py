import argparse
from mininet.net import Mininet
from mininet.node import OVSController
from mininet.cli import CLI
from mininet.log import setLogLevel
from time import sleep
import sys

def run_iperf3_test(net, option, algo, loss):
    server = net.get('H7')
    clients = {
        'H1': net.get('H1'), 'H2': net.get('H2'), 'H3': net.get('H3'),
        'H4': net.get('H4'), 'H5': net.get('H5'), 'H6': net.get('H6')
    }

    print(f"*** Starting iperf3 server on H7 using {algo} congestion control")
    server.cmd('iperf3 -s -p 5201 -D')  # Start iperf3 server on H7
    
    if option == 'a':
        print(f"*** Running experiment (a): Single client H1 (TCP {algo})")
        clients['H1'].cmd(f'iperf3 -c {server.IP()} -p 5201 -b 10M -P 10 -t 150 -C {algo} > a_{algo}.txt &')
        sleep(150)
    
    elif option == 'b':
        print("*** Running experiment (b): Staggered clients")
        clients['H1'].cmd(f'iperf3 -c {server.IP()} -p 5201 -b 10M -P 10 -t 150 -C {algo} > b1_{algo}.txt &')
        sleep(15)
        input("Press Enter to continue...")

        clients['H3'].cmd(f'iperf3 -c {server.IP()} -p 5201 -b 10M -P 10 -t 120 -C {algo} > b1_{algo}.txt &')
        sleep(15)
        input("Press Enter to continue...")

        clients['H4'].cmd(f'iperf3 -c {server.IP()} -p 5201 -b 10M -P 10 -t 90 -C {algo} > b1_{algo}.txt &')
        sleep(15)
        input("Press Enter to continue...")
        # sleep(90)
    
    elif option == 'c' or option == 'd':
        print(f"*** Running experiment ({option}): Bandwidth configuration, with {algo} congestion control and loss = {loss}")
        
        clients['H3'].cmd(f'iperf3 -c {server.IP()} -p 5201 -b 10M -P 10 -t 150 -C {algo} &')
        sleep(150)
        input("Press Enter to continue...")

        clients["H1"].cmd(f'iperf3 -c {server.IP()} -p 5201 -b 10M -P 10 -t 150 -C {algo} &')
        clients["H2"].cmd(f'iperf3 -c {server.IP()} -p 5201 -b 10M -P 10 -t 150 -C {algo} &')
        sleep(150)
        input("Press Enter to continue...")

        clients["H1"].cmd(f'iperf3 -c {server.IP()} -p 5201 -b 10M -P 10 -t 150 -C {algo} &')
        clients["H3"].cmd(f'iperf3 -c {server.IP()} -p 5201 -b 10M -P 10 -t 150 -C {algo} &')
        sleep(150)
        input("Press Enter to continue...")

        clients["H1"].cmd(f'iperf3 -c {server.IP()} -p 5201 -b 10M -P 10 -t 150 -C {algo} &')
        clients["H3"].cmd(f'iperf3 -c {server.IP()} -p 5201 -b 10M -P 10 -t 150 -C {algo} &')
        clients["H4"].cmd(f'iperf3 -c {server.IP()} -p 5201 -b 10M -P 10 -t 150 -C {algo} &')
        sleep(150)
        input("Press Enter to continue...")
    
    print("*** Experiment completed. Stopping iperf3 server.")
    server.cmd('pkill iperf3')

def create_network(option, algo, loss = 0):
    net = Mininet(controller=OVSController)

    print("*** Adding Controller")
    net.addController('c0')

    print("*** Adding Hosts")
    hosts = {f'H{i}': net.addHost(f'H{i}') for i in range(1, 8)}

    print("*** Adding Switches")
    switches = {f'S{i}': net.addSwitch(f'S{i}') for i in range(1, 5)}

    print("*** Creating Links")
    net.addLink(hosts['H1'], switches['S1'])
    net.addLink(hosts['H2'], switches['S1'])
    net.addLink(hosts['H3'], switches['S2'])
    net.addLink(hosts['H4'], switches['S3'])
    net.addLink(hosts['H5'], switches['S3'])
    net.addLink(hosts['H6'], switches['S4'])
    net.addLink(hosts['H7'], switches['S4'])
    
    if(option == 'c' or option == 'd'):
        net.addLink(switches['S1'], switches['S2'], bw=100)
        net.addLink(switches['S2'], switches['S3'], bw=50, loss = loss)
        net.addLink(switches['S3'], switches['S4'], bw=100)
    else:
        net.addLink(switches['S1'], switches['S2'])
        net.addLink(switches['S2'], switches['S3'])
        net.addLink(switches['S3'], switches['S4'])
    
    print("*** Starting Network")
    net.start()
    run_iperf3_test(net, option, algo, loss)
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')

    parser = argparse.ArgumentParser(description="Run Mininet with iperf3 experiments")
    parser.add_argument('--option', type=str, required=True, choices=['a', 'b', 'c', 'd'],
                        help="Specify experiment: a, b, c, or d")
    parser.add_argument('--algo', type=str, required=True, choices=['vegas', 'highspeed', 'reno', 'cubic', 'bbr'],
                        help="Specify TCP congestion control algorithm: vegas, highspeed, reno, cubic, or bbr")
    parser.add_argument('--loss', type=int, default=0, help="Specify packet loss percentage for experiment d")
    
    args = parser.parse_args()

    create_network(args.option, args.algo, args.loss)
