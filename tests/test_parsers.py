from netpulse.interface import parse_interface_json
from netpulse.latency import PING_RTT_PATTERN


def test_parse_interface_json():
    value = '[{"ifname":"eth0","operstate":"UP","mtu":1500}]'
    assert parse_interface_json(value)[0]["ifname"] == "eth0"


def test_ping_rtt_regex():
    output = "64 bytes: time=1.23 ms\n64 bytes: time<1 ms"
    assert PING_RTT_PATTERN.findall(output) == ["1.23", "1"]
