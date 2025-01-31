
#include <iostream>
#include <pcap.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>
#include <cstring>
#include <netinet/udp.h>

using namespace std;

void extract_smtp_subject(const u_char *payload, int size) {
    string data(reinterpret_cast<const char*>(payload), size);
    size_t subject_pos = data.find("Subject: ");
    if (subject_pos != string::npos) {
        size_t end_pos = data.find("\r\n", subject_pos);
        if (end_pos != string::npos) {
            cout << "Subject: " << data.substr(subject_pos + 9, end_pos - subject_pos - 9) << endl;
        }
    }
}

void extract_smtp_recipient(const u_char *payload, int size) {
    string data(reinterpret_cast<const char*>(payload), size);
    size_t to_pos = data.find("To: ");
    if (to_pos != string::npos) {
        size_t end_pos = data.find("\r\n", to_pos);
        if (end_pos != string::npos) {
            cout << "Recipient: " << data.substr(to_pos + 4, end_pos - to_pos - 4) << endl;
        }
    }
}

// Helper function to read DNS names with compression
string read_dns_name(const u_char* dns_payload, const u_char* packet_start, int& offset) {
    string name;
    int jumped = 0;
    int jump_count = 0;
    
    while (true) {
        if (jump_count > 10) return name; // Prevent infinite loops
        
        uint8_t len = dns_payload[offset];
        if (len == 0) {
            if (!jumped) offset++;
            break;
        }
        
        if ((len & 0xC0) == 0xC0) {
            if (!jumped) {
                offset += 2;
            }
            if (!dns_payload) return name;
            
            int jump_location = ((len & 0x3F) << 8) | dns_payload[offset + 1];
            dns_payload = packet_start + jump_location;
            offset = 0;
            jumped = 1;
            jump_count++;
            continue;
        }
        
        offset++;
        if (name.length() > 0) name += ".";
        name.append((char*)(dns_payload + offset), len);
        offset += len;
    }
    return name;
}

void extract_dns_info(const u_char *packet, int size) {
    if (size < 42) return;

    struct ip *iph = (struct ip *)(packet + 14);
    if (iph->ip_p != IPPROTO_UDP) return;

    struct udphdr *udph = (struct udphdr *)((u_char *)iph + (iph->ip_hl * 4));
    u_char *dns_payload = (u_char *)udph + sizeof(struct udphdr);
    
    // Get DNS header fields
    uint16_t flags = ntohs(*(uint16_t*)(dns_payload + 2));
    uint16_t qdcount = ntohs(*(uint16_t*)(dns_payload + 4));
    uint16_t ancount = ntohs(*(uint16_t*)(dns_payload + 6));
    
    // Skip DNS header
    int offset = 12;
    
    // Read question section
    string query_domain;
    if (qdcount > 0) {
        query_domain = read_dns_name(dns_payload, dns_payload, offset);
        offset += 4; // Skip QTYPE and QCLASS
    }
    
    // Only process if it's a response (QR bit set) and for our target domain
    if ((flags & 0x8000) && query_domain == "routerswitches.com") {
        // Print the DNS server IP that sent this response
        cout << "DNS Server Used: " << inet_ntoa(iph->ip_src) << endl;
        
        // Process answer section
        for (int i = 0; i < ancount; i++) {
            string answer_name = read_dns_name(dns_payload, dns_payload, offset);
            
            uint16_t type = ntohs(*(uint16_t*)(dns_payload + offset));
            uint16_t class_ = ntohs(*(uint16_t*)(dns_payload + offset + 2));
            uint32_t ttl = ntohl(*(uint32_t*)(dns_payload + offset + 4));
            uint16_t rdlength = ntohs(*(uint16_t*)(dns_payload + offset + 8));
            
            offset += 10;
            
            // If this is an A record (type 1)
            if (type == 1 && rdlength == 4) {
                struct in_addr addr;
                memcpy(&addr, dns_payload + offset, 4);
                cout << "Resolved IP: " << inet_ntoa(addr) << endl;
            }
            
            offset += rdlength;
        }
    }
}

void packet_handler(u_char *args, const struct pcap_pkthdr *header, const u_char *packet) {
    struct ip *iph = (struct ip *)(packet + 14);

    if (iph->ip_p == IPPROTO_TCP) {
        struct tcphdr *tcph = (struct tcphdr *)((u_char *)iph + (iph->ip_hl * 4));
        int payload_size = ntohs(iph->ip_len) - (iph->ip_hl * 4) - (tcph->th_off * 4);
        const u_char *payload = packet + 14 + (iph->ip_hl * 4) + (tcph->th_off * 4);

        if (ntohs(tcph->th_dport) == 25 || ntohs(tcph->th_dport) == 587 || ntohs(tcph->th_dport) == 465) {
            extract_smtp_subject(payload, payload_size);
            extract_smtp_recipient(payload, payload_size);
        }
    }

    if (iph->ip_p == IPPROTO_UDP) {
        extract_dns_info(packet, header->len);
    }
}

int main(int argc, char **argv) {
    if (argc < 2) {
        cerr << "Usage: " << argv[0] << " <pcap file>" << endl;
        return 1;
    }

    char errbuf[PCAP_ERRBUF_SIZE];
    pcap_t *handle = pcap_open_offline(argv[1], errbuf);
    if (!handle) {
        cerr << "Failed to open pcap file: " << errbuf << endl;
        return 1;
    }

    pcap_loop(handle, 0, packet_handler, nullptr);
    pcap_close(handle);
    
    return 0;
}
