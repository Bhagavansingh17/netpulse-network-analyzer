# Demonstration Scenarios

## Demo 1 — Healthy network
Run `netpulse interface`, `netpulse route`, `netpulse diagnose 1.1.1.1 --port 443`, and `netpulse latency 1.1.1.1 -n 100`. A healthy LAN result should show an UP interface, gateway neighbour state, DNS success, low gateway RTT, and no TCP failure. Do not publish values unless actually measured.

## Demo 2 — DNS failure
Temporarily misconfigure or block DNS only under an authorized test environment. `dns` should fail and `diagnose` should mark DNS failure. TCP tests by literal address help isolate DNS from routing and service availability.

## Demo 3 — High latency
Run gateway and remote latency separately. High remote RTT with normal gateway RTT points toward a path or remote/network issue. High gateway and remote RTT suggests local path, link, congestion, or host scheduling.

## Demo 4 — Packet loss
Increase loss in an authorized test environment or compare test results against an observed issue. Record loss, interface drops, RTT, and retransmissions. Loss is evidence, not proof of the cause.

## Demo 5 — TCP behavior
Capture with `sudo .venv/bin/netpulse capture --interface eth0 --duration 10 --tcp --host 192.0.2.10 --port 443`. A normal local TCP connection should contain SYN, SYN-ACK, ACK, data ACKs, and FIN/RST teardown, but capture location and timing change completeness.

## Demo 6 — Interface health
Run `netpulse health`. Zero counters do not prove perfect health, while RX drops or errors support further NIC, driver, queue, and link investigation.
