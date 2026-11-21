# Networking Concepts

Ethernet carries frames between interfaces using MAC addresses. IP provides logical addressing and routing across networks. ARP resolves an IPv4 address to a MAC address on Ethernet. An IPv6 neighbour entry replaces ARP for equivalent neighbour discovery behavior.

ICMP reports IP reachability and errors. TCP establishes a sequence-aware connection with SYN, SYN-ACK, ACK, and FIN/RST teardown. UDP is connectionless. DNS maps names to addresses. Routes determine the next hop. MTU limits frame payload and mismatches can cause fragmentation or dropped packets.

Packet loss can trigger retransmission and may add retransmission timeout or congestion-window delay. Jitter is variation in successive RTT samples. p95/p99 quantify rare slow outcomes.
