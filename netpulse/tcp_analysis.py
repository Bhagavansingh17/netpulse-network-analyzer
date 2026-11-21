from collections import Counter
from typing import Iterable

from .models import PacketMetadata


def analyze_tcp(packets: Iterable[PacketMetadata]) -> dict:
    tcp_packets = [packet for packet in packets if packet.protocol == "TCP"]
    flag_counts = Counter(packet.tcp_flags or "" for packet in tcp_packets)
    syn = sum(
        1 for packet in tcp_packets
        if packet.tcp_flags and "S" in packet.tcp_flags and "A" not in packet.tcp_flags
    )
    syn_ack = sum(
        1 for packet in tcp_packets
        if packet.tcp_flags and "S" in packet.tcp_flags and "A" in packet.tcp_flags
    )
    ack = sum(
        1 for packet in tcp_packets
        if packet.tcp_flags and "A" in packet.tcp_flags
        and "S" not in packet.tcp_flags
        and "F" not in packet.tcp_flags
        and "R" not in packet.tcp_flags
    )
    fin = sum(
        1 for packet in tcp_packets
        if packet.tcp_flags and "F" in packet.tcp_flags
    )
    rst = sum(
        1 for packet in tcp_packets
        if packet.tcp_flags and "R" in packet.tcp_flags
    )

    flows = set()
    for packet in tcp_packets:
        if packet.src_ip and packet.dst_ip and packet.src_port is not None and packet.dst_port is not None:
            endpoints = tuple(sorted((
                (packet.src_ip, packet.src_port),
                (packet.dst_ip, packet.dst_port),
            )))
            flows.add(endpoints)

    retransmissions = 0
    seen_sequences: set[tuple[str, str, int, int, int]] = set()
    for packet in tcp_packets:
        if packet.src_ip and packet.dst_ip and packet.src_port is not None and packet.dst_port is not None and packet.tcp_seq is not None:
            key = (
                packet.src_ip,
                packet.dst_ip,
                packet.src_port,
                packet.dst_port,
                packet.tcp_seq,
            )
            if key in seen_sequences:
                retransmissions += 1
            else:
                seen_sequences.add(key)

    return {
        "tcp_packets": len(tcp_packets),
        "connections_observed": len(flows),
        "syn": syn,
        "syn_ack": syn_ack,
        "ack": ack,
        "fin": fin,
        "rst": rst,
        "potential_retransmissions": retransmissions,
    }


def print_tcp_analysis(result: dict) -> None:
    print("TCP ANALYSIS")
    print("============")
    print()
    print(f"TCP packets         : {result['tcp_packets']}")
    print(f"Connections observed: {result['connections_observed']}")
    print(f"SYN                 : {result['syn']}")
    print(f"SYN-ACK             : {result['syn_ack']}")
    print(f"ACK                 : {result['ack']}")
    print(f"FIN                 : {result['fin']}")
    print(f"RST                 : {result['rst']}")
    print(f"Potential retransmissions detected: {result['potential_retransmissions']}")
    print()
    print("Retransmission detection repeats a four-tuple with the same TCP sequence")
    print("number. This is heuristic and can be affected by captures, out-of-order")
    print("delivery, sequence reuse, tunneling, and packets outside the capture point.")
