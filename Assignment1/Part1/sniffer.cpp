


#include <iostream>
#include <pcap.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>
#include <netinet/udp.h>
#include <arpa/inet.h>
#include <cstring>
#include <ctime>
#include <sstream>
#include <iomanip>

using namespace std;

// Global variables for speed calculation
int total_packets = 0;
long long total_data = 0;
double start_time = -1, end_time = 0;
int last_packets = 0;  // Track packets received in the last 5 seconds
int last_10_sec_packets = 0; // Track packets received in the last 10 seconds
time_t last_print_time = 0;  // Stores the last time we printed stats
time_t last_packet_time = 0; // Tracks the last received packet time
const int IDLE_TIMEOUT = 10; // Timeout in seconds
const int MIN_PACKETS_THRESHOLD = 20; // Minimum packets in last 10 seconds

pcap_dumper_t *pcap_dumper = nullptr; // File dumper

void packet_handler(u_char *args, const struct pcap_pkthdr *header, const u_char *packet) {
    total_packets++;
    total_data += header->len;

    double packet_time = header->ts.tv_sec + header->ts.tv_usec / 1e6;
    if (start_time == -1) start_time = packet_time;
    end_time = packet_time;

    last_packet_time = time(nullptr); // Update last received packet time

    // Write packet to file
    if (pcap_dumper) {
        pcap_dump((u_char *)pcap_dumper, header, packet);
    }

    // Get the current time
    time_t current_time = time(nullptr);

    // Check if 5 seconds have passed
    if (current_time - last_print_time >= 5) {
        cout << "\n===== REAL-TIME PACKET STATS =====" << endl;
        cout << "Total Packets Captured So Far: " << total_packets << endl;
        cout << "Packets Received in Last 5 Seconds: " << (total_packets - last_packets) << endl;
        cout << "Total Data Transferred So Far: " << total_data << " bytes" << endl;
        
        if (total_packets - last_packets == 0) {
            cout << "No packets received in the last 5 seconds." << endl;
        }

        // Update for next interval
        last_packets = total_packets;
        last_print_time = current_time;
    }
}

int main(int argc, char **argv) {
    if (argc < 2) {
        cerr << "Usage: " << argv[0] << " <interface>" << endl;
        return 1;
    }

    char errbuf[PCAP_ERRBUF_SIZE];
    const char* device = argv[1];

    // Open the device for live capture
    pcap_t *handle = pcap_open_live(device, BUFSIZ, 1, 1000, errbuf);
    if (!handle) {
        cerr << "Failed to open device: " << errbuf << endl;
        return 1;
    }

    // Generate filename based on current time
    time_t now = time(nullptr);
    struct tm *tm_info = localtime(&now);
    stringstream filename;
    filename << put_time(tm_info, "%Y-%m-%d_%H-%M-%S") << ".pcap";
    
    // Open the pcap file for writing
    pcap_dumper = pcap_dump_open(handle, filename.str().c_str());
    if (!pcap_dumper) {
        cerr << "Failed to open output file for writing." << endl;
        return 1;
    }

    cout << "Capturing all packets on interface: " << device << endl;
    cout << "Saving packets to: " << filename.str() << endl;
    last_print_time = time(nullptr);  // Initialize first print time
    last_packet_time = time(nullptr); // Initialize last received packet time
    time_t last_10_sec_check = time(nullptr);

    // Capture loop with idle timeout check
    while (true) {
        struct pcap_pkthdr *header;
        const u_char *packet;
        int res = pcap_next_ex(handle, &header, &packet);
        if (res == 1) {
            packet_handler(nullptr, header, packet);
        }

        time_t current_time = time(nullptr);

        // Check if idle timeout has passed
        if (difftime(current_time, last_packet_time) >= IDLE_TIMEOUT) {
            cout << "\nIdle timeout reached. Stopping capture..." << endl;
            break;
        }

        // Check if 10 seconds have passed to evaluate packet count
        if (difftime(current_time, last_10_sec_check) >= 10) {
            int packets_in_last_10_sec = total_packets - last_10_sec_packets;
            if (packets_in_last_10_sec < MIN_PACKETS_THRESHOLD) {
                cout << "\nPacket threshold not met (" << packets_in_last_10_sec << " packets in last 10 sec). Stopping capture..." << endl;
                break;
            }
            last_10_sec_packets = total_packets;
            last_10_sec_check = current_time;
        }
    }

    // Close the pcap dumper
    if (pcap_dumper) {
        pcap_dump_close(pcap_dumper);
    }
    pcap_close(handle);

    // Compute final speed
    double duration = (end_time - start_time);
    double packets_per_sec = duration > 0 ? total_packets / duration : 0;
    double mbps = duration > 0 ? (total_data * 8) / (duration * 1e6) : 0;

    // Print final summary
    cout << "\n===== FINAL PACKET CAPTURE STATS =====" << endl;
    cout << "Total Packets Captured: " << total_packets << endl;
    cout << "Total Data Transferred: " << total_data << " bytes" << endl;
    cout << "Capture Duration: " << duration << " seconds" << endl;
    cout << "Packets Per Second (pps): " << packets_per_sec << endl;
    cout << "Throughput (Mbps): " << mbps << endl;

    return 0;
}
