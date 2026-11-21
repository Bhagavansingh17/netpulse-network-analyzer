import socket
import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class TCPTestResult:
    target: str
    port: int
    success: bool
    dns_latency_ms: Optional[float]
    connect_latency_ms: Optional[float]
    resolved_address: Optional[str]
    error: Optional[str] = None


def test_tcp(host: str, port: int, timeout: float = 3.0) -> TCPTestResult:
    if not 1 <= port <= 65535:
        raise ValueError("Port must be between 1 and 65535")
    dns_start = time.monotonic()
    try:
        addresses = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        return TCPTestResult(host, port, False, None, None, None, f"DNS failure: {exc}")
    dns_latency = (time.monotonic() - dns_start) * 1000

    last_error = "No usable address returned"
    resolved_address = None
    for family, socktype, protocol, _, sockaddr in addresses:
        resolved_address = str(sockaddr[0])
        connect_start = time.monotonic()
        try:
            with socket.socket(family, socktype, protocol) as sock:
                sock.settimeout(timeout)
                sock.connect(sockaddr)
            return TCPTestResult(
                host,
                port,
                True,
                dns_latency,
                (time.monotonic() - connect_start) * 1000,
                resolved_address,
            )
        except OSError as exc:
            last_error = str(exc)
    return TCPTestResult(
        host,
        port,
        False,
        dns_latency,
        None,
        resolved_address,
        last_error,
    )


def print_tcp_test(result: TCPTestResult) -> None:
    print("TCP CONNECTIVITY")
    print("================")
    print()
    print(f"Target      : {result.target}")
    print(f"Port        : {result.port}")
    if result.resolved_address:
        print(f"Resolved IP : {result.resolved_address}")
    print(
        f"DNS         : {result.dns_latency_ms:.3f} ms"
        if result.dns_latency_ms is not None
        else "DNS         : FAILED"
    )
    print(
        f"TCP connect : {result.connect_latency_ms:.3f} ms"
        if result.connect_latency_ms is not None
        else "TCP connect : FAILED"
    )
    print(f"Result      : {'SUCCESS' if result.success else 'FAILURE'}")
    if result.error:
        print(f"Error       : {result.error}")
