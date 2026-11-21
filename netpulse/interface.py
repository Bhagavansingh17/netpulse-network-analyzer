import json
from pathlib import Path
from typing import Optional

from .models import InterfaceInfo
from .utils import NetPulseError, require_command, run_command, read_counter


def get_default_interface() -> Optional[str]:
    ip = require_command("ip")
    code, stdout, stderr = run_command([ip, "-j", "route", "show", "default"])
    if code != 0:
        if stderr:
            raise NetPulseError(f"Could not query default route: {stderr}")
        return None
    try:
        routes = json.loads(stdout or "[]")
    except json.JSONDecodeError as exc:
        raise NetPulseError("Could not parse Linux default-route output") from exc
    if routes:
        return routes[0].get("dev")
    return None


def parse_interface_json(raw: str) -> list[dict]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise NetPulseError("Could not parse output from 'ip -j addr'") from exc
    if not isinstance(data, list):
        raise NetPulseError("Unexpected output from 'ip -j addr'")
    return data


def inspect_interface(name: Optional[str] = None) -> InterfaceInfo:
    ip = require_command("ip")
    code, stdout, stderr = run_command([ip, "-j", "addr", "show"])
    if code != 0:
        raise NetPulseError(f"Could not inspect interfaces: {stderr or 'unknown error'}")
    interfaces = parse_interface_json(stdout)

    default_name = get_default_interface()
    selected = name or default_name
    if not selected:
        raise NetPulseError(
            "No default interface was found. Specify an interface explicitly."
        )
    matches = [item for item in interfaces if item.get("ifname") == selected]
    if not matches:
        raise NetPulseError(f"Interface '{selected}' was not found")
    item = matches[0]

    ipv4 = ""
    prefix = None
    for address in item.get("addr_info", []):
        if address.get("family") == "inet":
            ipv4 = address.get("local", "")
            prefix = address.get("prefixlen")
            break
    state = str(item.get("operstate") or item.get("state") or "UNKNOWN").upper()
    base = Path("/sys/class/net") / selected / "statistics"
    return InterfaceInfo(
        name=selected,
        state=state,
        ipv4=ipv4,
        prefix=prefix,
        mac=item.get("address"),
        mtu=item.get("mtu"),
        default_interface=selected == default_name,
        rx_packets=read_counter(str(base / "rx_packets")),
        tx_packets=read_counter(str(base / "tx_packets")),
        rx_bytes=read_counter(str(base / "rx_bytes")),
        tx_bytes=read_counter(str(base / "tx_bytes")),
        rx_errors=read_counter(str(base / "rx_errors")),
        tx_errors=read_counter(str(base / "tx_errors")),
        rx_dropped=read_counter(str(base / "rx_dropped")),
        tx_dropped=read_counter(str(base / "tx_dropped")),
        collisions=read_counter(str(base / "collisions")),
    )


def list_interfaces() -> list[dict]:
    ip = require_command("ip")
    code, stdout, stderr = run_command([ip, "-j", "addr", "show"])
    if code != 0:
        raise NetPulseError(f"Could not list interfaces: {stderr or 'unknown error'}")
    return parse_interface_json(stdout)


def print_interface(info: InterfaceInfo) -> None:
    address = f"{info.ipv4}/{info.prefix}" if info.ipv4 and info.prefix is not None else (info.ipv4 or "None")
    print("NETPULSE INTERFACE REPORT")
    print("=========================")
    print()
    print(f"Interface : {info.name}")
    print(f"State     : {info.state}")
    print(f"IPv4      : {address}")
    print(f"MAC       : {info.mac or 'Unknown'}")
    print(f"MTU       : {info.mtu or 'Unknown'}")
    print(f"Default   : {'Yes' if info.default_interface else 'No'}")
    print()
    print(f"RX packets : {info.rx_packets}")
    print(f"TX packets : {info.tx_packets}")
    print(f"RX bytes   : {info.rx_bytes}")
    print(f"TX bytes   : {info.tx_bytes}")
    print(f"RX errors  : {info.rx_errors}")
    print(f"TX errors  : {info.tx_errors}")
    print(f"RX dropped : {info.rx_dropped}")
    print(f"TX dropped : {info.tx_dropped}")
