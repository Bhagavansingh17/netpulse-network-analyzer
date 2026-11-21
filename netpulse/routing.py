import json
from dataclasses import dataclass
from typing import Optional

from .utils import NetPulseError, require_command, run_command


@dataclass
class RouteInfo:
    destination: str
    gateway: Optional[str]
    interface: Optional[str]
    metric: Optional[int]


def get_routes() -> list[RouteInfo]:
    ip = require_command("ip")
    code, stdout, stderr = run_command([ip, "-j", "route", "show"])
    if code != 0:
        raise NetPulseError(f"Could not query routing table: {stderr or 'unknown error'}")
    try:
        raw_routes = json.loads(stdout or "[]")
    except json.JSONDecodeError as exc:
        raise NetPulseError("Could not parse Linux routing-table output") from exc
    routes = []
    for item in raw_routes:
        routes.append(RouteInfo(
            destination=item.get("dst", "default"),
            gateway=item.get("gateway"),
            interface=item.get("dev"),
            metric=item.get("metric"),
        ))
    return routes


def get_default_route() -> Optional[RouteInfo]:
    return next((route for route in get_routes() if route.destination == "default"), None)


def print_routes(routes: list[RouteInfo]) -> None:
    print("NETPULSE ROUTING REPORT")
    print("=======================")
    print()
    print(f"{'Destination':16} {'Gateway':18} {'Interface':12} {'Metric'}")
    for route in routes:
        print(
            f"{route.destination:16} "
            f"{route.gateway or '-':18} "
            f"{route.interface or '-':12} "
            f"{route.metric if route.metric is not None else '-'}"
        )
    default = next((route for route in routes if route.destination == "default"), None)
    if default:
        print("\nRoute selection:")
        print(
            f"Destinations not matched by a more specific route use "
            f"{default.interface or 'the selected interface'}"
            + (f" via gateway {default.gateway}" if default.gateway else " directly")
            + "."
        )
