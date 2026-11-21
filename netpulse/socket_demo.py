import socket


def run_socket_server(protocol: str, port: int) -> None:
    if protocol == "tcp":
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(("0.0.0.0", port))
            server.listen()
            print(f"TCP echo server listening on 0.0.0.0:{port}")
            while True:
                connection, address = server.accept()
                with connection:
                    print(f"TCP connection from {address[0]}:{address[1]}")
                    while True:
                        data = connection.recv(4096)
                        if not data:
                            break
                        connection.sendall(data)
    else:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
            server.bind(("0.0.0.0", port))
            print(f"UDP echo server listening on 0.0.0.0:{port}")
            while True:
                data, address = server.recvfrom(4096)
                print(f"UDP datagram from {address[0]}:{address[1]} ({len(data)} bytes)")
                server.sendto(data, address)


def run_socket_client(host: str, port: int, protocol: str, message: str = "ping") -> None:
    import time
    payload = message.encode("utf-8")
    started = time.monotonic()
    if protocol == "tcp":
        with socket.create_connection((host, port), timeout=3) as client:
            client.sendall(payload)
            response = client.recv(4096)
    else:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
            client.settimeout(3)
            client.sendto(payload, (host, port))
            response, _ = client.recvfrom(4096)
    elapsed = (time.monotonic() - started) * 1000
    print(f"Echo received: {response.decode('utf-8', errors='replace')}")
    print(f"Application round-trip: {elapsed:.3f} ms")
