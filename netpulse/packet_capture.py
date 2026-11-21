import time
from typing import Optional

from .models import PacketMetadata
from .utils import NetPulseError


def build_capture_filter(
    protocols: list[str],
    port: Optional[int],
    host: Optional[str],
) -> Optional[str]:
    parts = []
    if protocols:
        if len(protocols) == 1:
            parts.append(protocols[0].lower())
        else:
            parts.append("(" + " or ".join(protocol.lower() for protocol in protocols) + ")")
    if port is not None:
        if not 1 <= port <= 65535:
            raise ValueError("Capture port must be between 1 and 65535")
        parts.append(f"port {port}")
    if host:
        import socket
        try:
            socket.inet_pton(socket.AF_INET, host)
        except OSError:
            try:
                socket.inet_pton(socket.AF_INET6, host)
            except OSError:
                raise ValueError("Capture host must be an IPv4 or IPv6 address")
        parts.append(f"host {host}")
    return " and ".join(parts) if parts else None


def capture_packets(
    interface: str,
    duration: int,
    bpf_filter: Optional[str] = None,
) -> list[PacketMetadata]:
    if not interface:
        raise ValueError("Capture interface is required")
    if duration < 1:
        raise ValueError("Capture duration must be at least 1 second")
    try:
        from scapy.all import AsyncSniffer, ARP, IP, IPv6, TCP, UDP, ICMP
    except ImportError as exc:
        raise NetPulseError(
            "Scapy is required for packet capture. Install it with "
            "'python3 -m pip install scapy'."
        ) from exc

    packets = []
    try:
        captured = AsyncSniffer(
            iface=interface,
            filter=bpf_filter,
            store=True,
        )
        captured.start()
        time.sleep(duration)
        captured.stop()
    except PermissionError as exc:
        raise NetPulseError(
            "Packet capture requires permission. Run on Linux with sudo or "
            "grant the process CAP_NET_RAW and CAP_NET_ADMIN."
        ) from exc
    except OSError as exc:
        raise NetPulseError(f"Packet capture failed: {exc}") from exc

    for packet in captured.results:
        src_ip = dst_ip = None
        protocol = "OTHER"
        src_port = dst_port = None
        tcp_flags = None
        tcp_seq = None
        if ARP in packet:
            protocol = "ARP"
            src_ip = getattr(packet[ARP], "psrc", None)
            dst_ip = getattr(packet[ARP], "pdst", None)
        elif IP in packet:
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
            if TCP in packet:
                protocol = "TCP"
                src_port = int(packet[TCP].sport)
                dst_port = int(packet[TCP].dport)
                tcp_flags = str(packet[TCP].flags)
                tcp_seq = int(packet[TCP].seq)
            elif UDP in packet:
                protocol = "UDP"
                src_port = int(packet[UDP].sport)
                dst_port = int(packet[UDP].dport)
            elif ICMP in packet:
                protocol = "ICMP"
        elif IPv6 in packet:
            src_ip = packet[IPv6].src
            dst_ip = packet[IPv6].dst
            if TCP in packet:
                protocol = "TCP"
                src_port = int(packet[TCP].sport)
                dst_port = int(packet[TCP].dport)
                tcp_flags = str(packet[TCP].flags)
                tcp_seq = int(packet[TCP].seq)
            elif UDP in packet:
                protocol = "UDP"
                src_port = int(packet[UDP].sport)
                dst_port = int(packet[UDP].dport)
            else:
                protocol = "ICMP"
        packets.append(PacketMetadata(
            timestamp=float(getattr(packet, "time", 0)),
            src_ip=src_ip,
            dst_ip=dst_ip,
            protocol=protocol,
            src_port=src_port,
            dst_port=dst_port,
            length=len(packet),
            tcp_flags=tcp_flags,
            tcp_seq=tcp_seq,
        ))
    return packets
