import socket
from typing import Optional

from .dns import resolve_hostname
from .interface import inspect_interface
from .routing import get_default_route
from .neighbors import get_neighbors
from .latency import measure_latency
from .tcp_test import test_tcp
from .models import DiagnosticTest
from .utils import NetPulseError


def gateway_address() -> Optional[str]:
    route = get_default_route()
    return route.gateway if route else None


def diagnose_host(host: str, port: int = 443, probes: int = 20) -> list[DiagnosticTest]:
    tests = []
    try:
        interface = inspect_interface()
        tests.append(DiagnosticTest(
            "Local interface",
            "PASS" if interface.state == "UP" else "WARN",
            interface.name,
            f"Interface operational state is {interface.state}.",
            [] if interface.state == "UP" else ["Interface link is down", "Administrator disabled the interface"],
        ))
        tests.append(DiagnosticTest(
            "Local IPv4",
            "PASS" if interface.ipv4 else "FAIL",
            interface.ipv4 or "Not configured",
            "An IPv4 address is available." if interface.ipv4 else "No IPv4 address was found.",
            [] if interface.ipv4 else ["DHCP failure", "Static address not configured"],
        ))
    except NetPulseError as exc:
        tests.append(DiagnosticTest("Local interface", "FAIL", "Unavailable", str(exc), ["Network tools missing", "No default interface"]))

    gateway = gateway_address()
    tests.append(DiagnosticTest(
        "Default gateway",
        "PASS" if gateway else "FAIL",
        gateway or "Not found",
        "A default route gateway was found." if gateway else "No default gateway is configured.",
        [] if gateway else ["Missing default route", "WAN or DHCP failure"],
    ))

    neighbors = get_neighbors()
    gateway_neighbor = next((item for item in neighbors if item.ip == gateway), None)
    if gateway:
        tests.append(DiagnosticTest(
            "Gateway neighbour",
            "PASS" if gateway_neighbor and gateway_neighbor.state != "FAILED" else "WARN",
            gateway_neighbor.state if gateway_neighbor else "No entry",
            "The gateway is present in the ARP/IPv6 neighbour table."
            if gateway_neighbor else "No gateway neighbour entry was observed.",
            [] if gateway_neighbor else ["ARP resolution failure", "Gateway not reachable", "Neighbour cache entry aging"],
        ))

    dns = resolve_hostname(host)
    tests.append(DiagnosticTest(
        "DNS resolution",
        "PASS" if dns.success else "FAIL",
        ", ".join(dns.addresses) if dns.addresses else (dns.error or "Failed"),
        f"Resolved in {dns.latency_ms:.3f} ms." if dns.success and dns.latency_ms is not None else "System DNS did not return an address.",
        [] if dns.success else ["DNS server unreachable", "Invalid hostname", "Search-domain/configuration issue"],
    ))

    try:
        gateway_stats = measure_latency(gateway, 5) if gateway else None
        if gateway_stats and gateway_stats.successful:
            tests.append(DiagnosticTest(
                "Gateway reachability",
                "PASS",
                f"{gateway_stats.average_ms:.3f} ms, {gateway_stats.packet_loss_percent:.1f}% loss",
                "ICMP echo reached the default gateway.",
                [],
            ))
        elif gateway:
            tests.append(DiagnosticTest(
                "Gateway reachability",
                "FAIL",
                "100% loss",
                "No ICMP response was received from the gateway.",
                ["Gateway blocked ICMP", "Link or local routing failure", "No ARP response"],
            ))
    except NetPulseError as exc:
        tests.append(DiagnosticTest("Gateway reachability", "FAIL", "Unavailable", str(exc), ["ping unavailable"]))

    try:
        remote_stats = measure_latency(host, probes)
        status = "PASS" if remote_stats.successful and remote_stats.packet_loss_percent < 100 else "FAIL"
        value = (
            f"{remote_stats.average_ms:.3f} ms average, "
            f"{remote_stats.packet_loss_percent:.1f}% loss"
            if remote_stats.successful
            else "No replies"
        )
        tests.append(DiagnosticTest(
            "ICMP reachability",
            status,
            value,
            "Replies were received from the target." if remote_stats.successful else "No ICMP reply was received.",
            [] if remote_stats.successful else ["Remote host blocking ICMP", "Routing failure", "Firewall policy", "Packet loss"],
        ))
    except NetPulseError as exc:
        tests.append(DiagnosticTest("ICMP reachability", "FAIL", "Unavailable", str(exc), ["ping unavailable", "invalid host"]))

    tcp = test_tcp(host, port)
    tests.append(DiagnosticTest(
        f"TCP port {port}",
        "PASS" if tcp.success else "FAIL",
        f"{tcp.connect_latency_ms:.3f} ms" if tcp.connect_latency_ms is not None else (tcp.error or "Failed"),
        "A TCP connection was established." if tcp.success else "A TCP handshake was not established.",
        [] if tcp.success else ["Port closed", "Firewall filtering", "Service unavailable", "Routing failure"],
    ))
    return tests


def print_diagnostics(host: str, tests: list[DiagnosticTest]) -> None:
    print("NETPULSE DIAGNOSTIC REPORT")
    print("==========================")
    print()
    print(f"Target: {host}")
    print()
    for test in tests:
        print(f"{test.name:22} : {test.status}")
        print(f"  Measured: {test.value}")
        print(f"  Evidence: {test.interpretation}")
        if test.possible_causes:
            print("  Possible causes:")
            for cause in test.possible_causes:
                print(f"    - {cause}")
        print()
    failures = [test for test in tests if test.status == "FAIL"]
    print("Assessment:")
    if failures:
        print(f"The diagnostic found {len(failures)} failing check(s). Investigate these first:")
        for failure in failures:
            print(f"- {failure.name}: {failure.value}")
    else:
        print("No direct failures were observed. If latency is high or variable, compare gateway and remote RTT.")
