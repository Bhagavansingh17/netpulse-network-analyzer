from netpulse.models import InterfaceInfo, LatencyStats, PacketMetadata


def test_interface_model():
    info = InterfaceInfo("eth0", "UP", "192.0.2.10", 24, "00:11:22:33:44:55", 1500, True)
    assert info.name == "eth0"
    assert info.prefix == 24


def test_packet_model():
    packet = PacketMetadata(1.0, "192.0.2.1", "198.51.100.2", "TCP", 1234, 443, 74)
    assert packet.protocol == "TCP"
