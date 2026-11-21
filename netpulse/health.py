import json
from pathlib import Path
from typing import Optional

from .interface import inspect_interface
from .models import InterfaceInfo
from .utils import NetPulseError, require_command, run_command


def get_ethtool_health(interface_name: str) -> dict:
    result = {}
    ethtool = require_command("ethtool")
    code, stdout, stderr = run_command([ethtool, interface_name], timeout=5)
    if code != 0:
        if "Operation not supported" in stderr:
            result["unsupported"] = "ethtool settings are not supported by this interface"
        elif stderr:
            result["unsupported"] = stderr
        return result
    for line in stdout.splitlines():
        stripped = line.strip()
        if ": " in stripped:
            key, value = stripped.split(": ", 1)
            result[key.lower().replace(" ", "_")] = value
    return result


def print_health(info: InterfaceInfo) -> None:
    print("INTERFACE HEALTH")
    print("================")
    print()
    print(f"Link        : {info.state}")
    print(f"MTU         : {info.mtu or 'Unknown'}")
    print(f"RX Errors   : {info.rx_errors}")
    print(f"TX Errors   : {info.tx_errors}")
    print(f"RX Drops    : {info.rx_dropped}")
    print(f"TX Drops    : {info.tx_dropped}")
    print(f"Collisions  : {info.collisions}")

    try:
        ethtool = get_ethtool_health(info.name)
    except NetPulseError as exc:
        ethtool = {"unsupported": str(exc)}
    if "speed" in ethtool:
        print(f"Speed       : {ethtool['speed']}")
    if "duplex" in ethtool:
        print(f"Duplex      : {ethtool['duplex']}")
    if "unsupported" in ethtool:
        print(f"NIC details : {ethtool['unsupported']}")

    warnings = []
    if info.rx_errors:
        warnings.append("RX errors detected; possible NIC/driver or link issues.")
    if info.tx_errors:
        warnings.append("TX errors detected; possible NIC/driver, queue, or link issues.")
    if info.rx_dropped:
        warnings.append("RX drops detected; possible congestion, buffer exhaustion, or driver/NIC issues.")
    if info.tx_dropped:
        warnings.append("TX drops detected; possible queue or NIC transmission issues.")
    if info.collisions:
        warnings.append("Collisions were reported; investigate duplex or legacy/shared-medium issues.")
    if warnings:
        print("\nWarning:")
        for warning in warnings:
            print(f"- {warning}")
