# Low-Latency Foundations

Latency is the time for work to travel through the system. Throughput is work per time and is not a direct substitute for latency. Queueing, NIC interrupt coalescing, kernel scheduling, NUMA placement, CPU frequency, context switches, memory bandwidth, and congestion can all increase latency.

CPU affinity can keep network work on selected cores, reducing migration and cache disruption. NUMA affects memory and device locality. Hardware timestamps and measurement position determine what is actually measured.

DPDK is a user-space polling and device-driver ecosystem that bypasses kernel network stacks. It can reduce overhead but requires dedicated hardware, memory, CPU, and operational care. OpenOnload-style technology accelerates sockets with kernel-bypass elements. NetPulse does not implement or claim either technology.
