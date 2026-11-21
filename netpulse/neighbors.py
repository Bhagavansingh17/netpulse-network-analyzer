import json
from dataclasses import dataclass
from typing import Optional

from .utils import NetPulseError, require_command, run_command


@dataclass
class NeighborInfo:
    ip: str
    mac: Optional[str]
    interface: Optional[str]
    state: str


def get_neighbors() -> list[NeighborInfo]:
    ip = require_command("ip")
    code, stdout, stderr = run_command([ip, "-j", "neigh", "show"])
    if code != 0:
        raise NetPulseError(f"Could not query neighbour table: {stderr or 'unknown error'}")
    try:
        raw = json.loads(stdout or "[]")
    except json.JSONDecodeError as exc:
        raise NetPulseError("Could not parse Linux neighbour-table output") from exc
    neighbors = []
    for item in raw:
        states = item.get("state")
        state = ",".join(states) if isinstance(states, list) else str(states or "UNKNOWN")
        neighbors.append(NeighborInfo(
            ip=item.get("dst", ""),
            mac=item.get("lladdr"),
            interface=item.get("dev"),
            state=state,
        ))
    return neighbors


def print_neighbors(neighbors: list[NeighborInfo]) -> None:
    print("NETPULSE NEIGHBOR REPORT")
    print("========================")
    print()
    print(f"{'IP':18} {'MAC':18} {'Interface':12} {'State'}")
    for neighbor in neighbors:
        print(
            f"{neighbor.ip:18} "
            f"{neighbor.mac or '-':18} "
            f"{neighbor.interface or '-':12} "
            f"{neighbor.state}"
        )
    if not neighbors:
        print("No neighbour entries were reported.")
