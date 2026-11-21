# Troubleshooting Methodology

Start with link state and IP configuration. Check the default route and gateway neighbour entry. Confirm gateway RTT, then DNS, then remote ICMP and the application TCP port. Compare gateway and remote RTT to identify local versus path/congestion delay.

For packet loss, compare gateway, remote, and alternating destinations. Check interface counters and NIC/driver logs. For DNS, test a literal IP and DNS queries, then inspect resolver configuration. For a broken gateway, verify route, gateway address, ARP/neighbor state, and gateway health.
