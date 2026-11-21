from dataclasses import dataclass, field
from typing import Optional


@dataclass
class InterfaceInfo:
    name: str
    state: str
    ipv4: str
    prefix: Optional[int]
    mac: Optional[str]
    mtu: Optional[int]
    default_interface: bool
    rx_packets: int = 0
    tx_packets: int = 0
    rx_bytes: int = 0
    tx_bytes: int = 0
    rx_errors: int = 0
    tx_errors: int = 0
    rx_dropped: int = 0
    tx_dropped: int = 0
    collisions: int = 0


@dataclass
class LatencyStats:
    target: str
    probes: int
    successful: int
    rtts_ms: list[float] = field(default_factory=list)
    packet_loss_percent: float = 0.0
    minimum_ms: Optional[float] = None
    average_ms: Optional[float] = None
    median_ms: Optional[float] = None
    stddev_ms: Optional[float] = None
    p95_ms: Optional[float] = None
    p99_ms: Optional[float] = None
    maximum_ms: Optional[float] = None
    jitter_ms: Optional[float] = None


@dataclass
class PacketMetadata:
    timestamp: float
    src_ip: Optional[str]
    dst_ip: Optional[str]
    protocol: str
    src_port: Optional[int]
    dst_port: Optional[int]
    length: int
    tcp_flags: Optional[str] = None
    tcp_seq: Optional[int] = None


@dataclass
class DiagnosticTest:
    name: str
    status: str
    value: str
    interpretation: str
    possible_causes: list[str] = field(default_factory=list)
