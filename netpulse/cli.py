import argparse
import logging
import sys

from .connectivity import diagnose_host, print_diagnostics
from .dns import print_dns, resolve_hostname
from .health import print_health
from .interface import inspect_interface, print_interface
from .latency import measure_latency, print_latency
from .neighbors import get_neighbors, print_neighbors
from .packet_analysis import analyze_packets, print_packet_analysis
from .packet_capture import build_capture_filter, capture_packets
from .routing import get_routes, print_routes
from .socket_demo import run_socket_client, run_socket_server
from .tcp_analysis import analyze_tcp, print_tcp_analysis
from .tcp_test import print_tcp_test, test_tcp
from .logging_config import configure_logging
from .utils import NetPulseError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="netpulse",
        description="NetPulse - Linux network latency and connectivity analyzer",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="enable debug logging")
    subparsers = parser.add_subparsers(dest="command", required=True)

    interface = subparsers.add_parser("interface", help="inspect a network interface")
    interface.add_argument("name", nargs="?", help="interface name (default: default route interface)")

    diagnose = subparsers.add_parser("diagnose", help="run end-to-end diagnostics")
    diagnose.add_argument("host")
    diagnose.add_argument("--port", type=int, default=443)
    diagnose.add_argument("--probes", type=int, default=20)

    latency = subparsers.add_parser("latency", help="measure RTT statistics")
    latency.add_argument("host")
    latency.add_argument("-n", "--probes", type=int, default=100)
    latency.add_argument("-W", "--timeout", type=float, default=1.0)
    latency.add_argument("--advanced", action="store_true")

    subparsers.add_parser("neighbors", help="display ARP/IPv6 neighbour table")
    subparsers.add_parser("route", help="display the Linux routing table")

    capture = subparsers.add_parser("capture", help="capture live packet metadata")
    capture.add_argument("--interface", "-i", required=True)
    capture.add_argument("--duration", "-d", type=int, default=30)
    capture.add_argument("--tcp", action="store_true")
    capture.add_argument("--udp", action="store_true")
    capture.add_argument("--icmp", action="store_true")
    capture.add_argument("--arp", action="store_true")
    capture.add_argument("--port", type=int)
    capture.add_argument("--host")

    subparsers.add_parser("health", help="analyze interface and NIC health")

    dns = subparsers.add_parser("dns", help="resolve a hostname")
    dns.add_argument("hostname")
    dns.add_argument("--timeout", type=float, default=3.0)

    tcp = subparsers.add_parser("tcp", help="test a TCP connection")
    tcp.add_argument("host")
    tcp.add_argument("port", type=int)
    tcp.add_argument("--timeout", type=float, default=3.0)

    server = subparsers.add_parser("socket-server", help="run a socket echo server")
    server.add_argument("--tcp", action="store_true")
    server.add_argument("--udp", action="store_true")
    server.add_argument("--port", type=int, default=9000)

    client = subparsers.add_parser("socket-client", help="run a socket echo client")
    client.add_argument("--host", required=True)
    client.add_argument("--port", type=int, default=9000)
    client.add_argument("--tcp", action="store_true")
    client.add_argument("--udp", action="store_true")
    client.add_argument("--message", default="ping")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_logging(args.verbose)
    try:
        if args.command == "interface":
            print_interface(inspect_interface(args.name))
        elif args.command == "diagnose":
            print_diagnostics(args.host, diagnose_host(args.host, args.port, args.probes))
        elif args.command == "latency":
            print_latency(measure_latency(args.host, args.probes, args.timeout), args.advanced)
        elif args.command == "neighbors":
            print_neighbors(get_neighbors())
        elif args.command == "route":
            print_routes(get_routes())
        elif args.command == "capture":
            protocols = []
            for name in ("tcp", "udp", "icmp", "arp"):
                if getattr(args, name):
                    protocols.append(name)
            capture_filter = build_capture_filter(protocols, args.port, args.host)
            packets = capture_packets(args.interface, args.duration, capture_filter)
            print_packet_analysis(analyze_packets(packets))
            print()
            print_tcp_analysis(analyze_tcp(packets))
            print()
            print("Metadata sample (payloads are never collected or displayed):")
            for packet in packets[:20]:
                print(
                    f"{packet.timestamp:.6f} "
                    f"{packet.src_ip or '-'} -> {packet.dst_ip or '-'} "
                    f"{packet.protocol} "
                    f"{packet.src_port or '-'}:{packet.dst_port or '-'} "
                    f"{packet.length} bytes"
                )
        elif args.command == "health":
            print_health(inspect_interface())
        elif args.command == "dns":
            print_dns(resolve_hostname(args.hostname, args.timeout))
        elif args.command == "tcp":
            print_tcp_test(test_tcp(args.host, args.port, args.timeout))
        elif args.command == "socket-server":
            protocol = "tcp" if args.tcp else "udp"
            run_socket_server(protocol, args.port)
        elif args.command == "socket-client":
            protocol = "tcp" if args.tcp else "udp"
            run_socket_client(args.host, args.port, protocol, args.message)
        return 0
    except (NetPulseError, ValueError, OSError) as exc:
        logging.getLogger("netpulse").error("%s", exc)
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
