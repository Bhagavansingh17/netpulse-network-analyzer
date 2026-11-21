# Interview Defense

## 1. What problem does this project solve?
It separates local interface, route, neighbour, DNS, ICMP, TCP, capture, and NIC-health evidence so a network problem can be located by layer instead of relying on one “ping works” or “ping fails” result.

## 2. Why Python?
Python is suitable for Linux system integration and structured diagnostic workflows. The hot-path packet-processing claim is explicitly avoided. Standard socket/subprocess APIs and Scapy keep the implementation understandable.

## 3. Why Linux?
The project targets Linux networking primitives: `ip`, `/sys/class/net`, `ping`, `ethtool`, and libpcap-based capture. Linux exposes route, neighbour, interface, and socket behavior directly.

## 4. What happens when you ping a host?
The host resolves if needed, chooses a route and interface, creates an ICMP Echo Request, receives an Echo Reply, and records RTT and loss. A router may forward it or block ICMP.

## 5. How does ARP work?
An IPv4 host on Ethernet broadcasts “who has this address?” The owner replies with its MAC. The result is cached in the neighbour table and can become stale or failed.

## 6. How does a switch learn MAC addresses?
A switch learns source MAC/address-to-port mappings by observing frames. Frames for unknown destinations are flooded to suitable ports; known destinations are forwarded only to the learned port.

## 7. What is the difference between MAC and IP?
MAC identifies an Ethernet interface segment locally and is rewritten at hops; IP identifies a logical endpoint and is used for end-to-end routing.

## 8. What happens when the destination is outside the subnet?
The host uses the most specific route and then the default gateway or another route. The gateway forwards it toward the destination.

## 9. What is a default gateway?
It is the next-hop router used when no more-specific route matches a destination.

## 10. What happens during a TCP three-way handshake?
The client sends SYN, the server replies SYN-ACK, and the client ACKs. The handshake creates per-flow state and sequence numbers.

## 11. What is a TCP retransmission?
A sender repeats TCP data or control packets because acknowledgements are missing or it believes delivery failed. Retransmission uses sequence information and timers.

## 12. How can packet loss affect latency?
Lost packets can trigger retransmission and congestion-control backoff, making application completion slower even if average RTT is low.

## 13. What is RTT?
Round-trip time is elapsed time between sending a request and receiving its associated response.

## 14. What is jitter?
NetPulse uses mean absolute change between consecutive successful RTT samples. It describes RTT variation, not the same thing as packet loss.

## 15. Why is p99 latency useful?
p99 shows the slow tail affecting a small fraction of operations. Average latency can hide one-percent events that dominate repeated jobs or user wait time.

## 16. How did you measure latency?
The `ping` command supplies real ICMP RTT samples. Jitter, averages, percentiles, and loss are calculated from those samples. DNS, TCP, and local timing use `time.monotonic()`.

## 17. Why use monotonic time?
Monotonic clocks do not move backward when wall-clock time or NTP changes, making elapsed-time measurements safer.

## 18. What does tcpdump capture?
tcpdump captures packet metadata and optionally payload bytes from an interface or BPF-selected subset. NetPulse uses Scapy/libpcap and does not record payloads.

## 19. What is libpcap?
libpcap is a packet-capture API that interfaces with the OS capture facility and supports filtering.

## 20. How does packet filtering work?
A BPF expression filters captured packets by protocol, address, port, or combinations before Python receives matching packets. It does not prove that dropped traffic was absent.

## 21. How did you detect TCP retransmissions?
NetPulse stores source/destination IP and ports plus sequence number and flags. Repeated flow/key/sequence is marked as a possible retransmission.

## 22. What are the limitations of retransmission detection?
The method can miss packets, flag legitimate repeated sequence values, and cannot track handoff or capture loss perfectly. It is not a full TCP reassembler.

## 23. How troubleshoot high latency?
Compare gateway and remote RTT, jitter and p99, route changes, loss, interface counters, congestion, and multiple destinations.

## 24. How troubleshoot packet loss?
Compare interfaces and hops, inspect RX/TX errors/drops, test gateway and remote separately, check duplex/NIC/driver behavior, and identify loss direction.

## 25. How troubleshoot DNS failure?
Compare resolution and TCP-to-IP behavior, verify resolvers/search domains, test timeout and authoritative options, and separate DNS failure from application failure.

## 26. How troubleshoot a broken default gateway?
Check route and gateway address, ARP/neighbour state, gateway reachability, DHCP or static configuration, VLAN, and forwarding state.

## 27. What does `ip route` show?
It shows route destinations, next hops, interfaces, metrics, and special routing rules selected by the kernel.

## 28. What does `ip neigh` show?
It shows local neighbour IP-to-MAC bindings, interfaces, and states such as REACHABLE, STALE, DELAY, PROBE, or FAILED.

## 29. What does `ss` show?
It lists sockets and listening or established TCP/UDP state.

## 30. What does `ethtool` provide?
Where supported, it reports link, speed, duplex, driver, and hardware/NIC settings.

## 31. What is MTU?
The maximum frame payload or packet size permitted on a link, commonly 1500 bytes on Ethernet IPv4 networks.

## 32. What happens with an MTU mismatch?
Packets may be fragmented or dropped, especially when ICMP fragmentation-needed or PMTU behavior is blocked. Symptoms vary between small and large transfers.

## 33. What is VLAN?
VLAN tagging logically separates Layer 2 domains on shared physical switching infrastructure.

## 34. What is a trunk?
A trunk carries multiple VLAN tags between switches or switches and virtualization/NIC endpoints.

## 35. What is STP?
Spanning Tree Protocol prevents loops in bridged Layer 2 networks while permitting redundant forwarding paths.

## 36. Why can switching loops be dangerous?
Loops multiply broadcasts and unknown frames, creating congestion and unstable MAC tables.

## 37. What is multicast?
One sender addresses a multicast group, and network elements distribute to subscribed receivers.

## 38. Why is multicast interesting for market-data systems?
Market-data feeds commonly fan out to many receivers. Multicast affects IGMP/PIM, NIC multicast filtering, joins, and loss visibility.

## 39. What is 10/25/40/100GbE?
It denotes Ethernet link rates. It does not itself guarantee application latency.

## 40. Why low latency matters in trading systems?
Decisions depend on market timestamps and short-lived opportunities. Queue and tail delay can affect decision, transport, and execution timing.

## 41. What is CPU pinning?
It constrains a process/thread to selected CPUs to reduce migration and improve cache or NUMA locality.

## 42. What is NUMA?
Non-uniform memory access makes memory or devices attached to different CPU sockets vary in latency and bandwidth.

## 43. What is DPDK?
DPDK provides user-space drivers and libraries for polling and high-rate packet processing while bypassing much of the kernel network stack.

## 44. What is kernel bypass?
Applications expose NIC queues or accelerated APIs without normal kernel socket/interrupt processing.

## 45. What is OpenOnload?
OpenOnload is an accelerated socket implementation that can bypass kernel networking for supported applications and configurations.

## 46. Why isn't this project equivalent to DPDK?
It uses Linux sockets, `ping`, Scapy, and normal interrupt/copy-based packet handling. It has no NIC polling or kernel bypass.

## 47. What improve in a month?
Add structured JSON and baseline reports, hardware timestamp support, richer TCP state, route tracing, packet-loss correlation, and controlled integration tests.

## 48. What happens if the NIC drops packets?
RX counters can increase; application protocols may see loss or incomplete bursts. Causes include queue overflow, memory pressure, filtering, driver bugs, or congestion.

## 49. How scale this tool?
Keep collection small and stateless, export structured JSON, run controlled collectors per host, and aggregate baselines. Avoid running broad scans.

## 50. What part was hardest?
Separating real observations from interpretation and ensuring a heuristic TCP or latency result is never presented as definitive.
