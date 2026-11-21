from netpulse.models import DiagnosticTest
from netpulse.packet_analysis import analyze_packets
from netpulse.models import PacketMetadata
from netpulse.tcp_analysis import analyze_tcp


def test_packet_analysis():
    packets = [
        PacketMetadata(1.0, "10.0.0.1", "10.0.0.2", "TCP", 1234, 443, 74),
        PacketMetadata(2.0, "10.0.0.2", "10.0.0.1", "TCP", 443, 1234, 74),
    ]
    result = analyze_packets(packets)
    assert result["total_packets"] == 2
    assert result["protocol_counts"]["TCP"] == 2


def test_tcp_analysis():
    packets = [
        PacketMetadata(1.0, "10.0.0.1", "10.0.0.2", "TCP", 1234, 443, 74, "S", 100),
        PacketMetadata(2.0, "10.0.0.2", "10.0.0.1", "TCP", 443, 1234, 74, "SA", 200),
        PacketMetadata(3.0, "10.0.0.1", "10.0.0.2", "TCP", 1234, 443, 74, "A", 101),
    ]
    result = analyze_tcp(packets)
    assert result["syn"] == 1
    assert result["syn_ack"] == 1
