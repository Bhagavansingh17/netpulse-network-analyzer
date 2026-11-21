from collections import Counter
from typing import Iterable

from .models import PacketMetadata
from .utils import format_bytes


def analyze_packets(packets: list[PacketMetadata]) -> dict:
    total = len(packets)
    total_bytes = sum(packet.length for packet in packets)
    timestamps = [packet.timestamp for packet in packets if packet.timestamp]
    duration = max(0.0, max(timestamps) - min(timestamps)) if timestamps else 0.0
    protocol_counts = Counter(packet.protocol for packet in packets)
    source_counts = Counter(packet.src_ip for packet in packets if packet.src_ip)
    destination_counts = Counter(packet.dst_ip for packet in packets if packet.dst_ip)
    port_counts = Counter(
        port
        for packet in packets
        for port in (packet.src_port, packet.dst_port)
        if port is not None
    )
    return {
        "total_packets": total,
        "total_bytes": total_bytes,
        "duration_seconds": duration,
        "packets_per_second": total / duration if duration > 0 else 0.0,
        "bytes_per_second": total_bytes / duration if duration > 0 else 0.0,
        "protocol_counts": protocol_counts,
        "source_counts": source_counts,
        "destination_counts": destination_counts,
        "port_counts": port_counts,
    }


def print_packet_analysis(result: dict) -> None:
    total = result["total_packets"]
    print("PACKET ANALYSIS")
    print("===============")
    print()
    print(f"Packets      : {total:,}")
    print(f"Total bytes  : {format_bytes(result['total_bytes'])}")
    print(f"Packets/sec  : {result['packets_per_second']:.1f}")
    print(f"Throughput   : {result['bytes_per_second'] * 8 / 1_000_000:.3f} Mbps")
    print()
    print("Protocols:")
    for protocol in ("TCP", "UDP", "ICMP", "ARP", "OTHER"):
        count = result["protocol_counts"].get(protocol, 0)
        percent = count / total * 100 if total else 0
        print(f"{protocol:12} {percent:6.1f}% ({count:,})")
    print()
    print("Top source addresses:")
    for address, count in result["source_counts"].most_common(5):
        print(f"{address:32} {count:,}")
    print()
    print("Top destination addresses:")
    for address, count in result["destination_counts"].most_common(5):
        print(f"{address:32} {count:,}")
    print()
    print("Top ports:")
    for port, count in result["port_counts"].most_common(5):
        print(f"{port:<32} {count:,}")
