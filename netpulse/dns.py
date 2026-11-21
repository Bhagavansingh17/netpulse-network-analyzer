import socket
import time
from dataclasses import dataclass
from typing import Optional

from .utils import NetPulseError


@dataclass
class DNSResult:
    hostname: str
    addresses: list[str]
    latency_ms: Optional[float]
    success: bool
    error: Optional[str] = None


def resolve_hostname(hostname: str, timeout: float = 3.0) -> DNSResult:
    if not hostname or len(hostname) > 253:
        raise NetPulseError("Invalid hostname length")
    started = time.monotonic()
    try:
        socket.setdefaulttimeout(timeout)
        records = socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        elapsed = (time.monotonic() - started) * 1000
        return DNSResult(hostname, [], elapsed, False, str(exc))
    except OSError as exc:
        elapsed = (time.monotonic() - started) * 1000
        return DNSResult(hostname, [], elapsed, False, str(exc))
    elapsed = (time.monotonic() - started) * 1000
    addresses = list(dict.fromkeys(
        record[4][0] for record in records if record[4]
    ))
    return DNSResult(hostname, addresses, elapsed, bool(addresses))


def print_dns(result: DNSResult) -> None:
    print("DNS RESOLUTION")
    print("==============")
    print()
    print(f"Hostname : {result.hostname}")
    print(f"Latency  : {result.latency_ms:.3f} ms" if result.latency_ms is not None else "Latency  : Unknown")
    print(f"Result   : {'SUCCESS' if result.success else 'FAILURE'}")
    if result.addresses:
        print("Addresses:")
        for address in result.addresses:
            print(f"  {address}")
    elif result.error:
        print(f"Error: {result.error}")
