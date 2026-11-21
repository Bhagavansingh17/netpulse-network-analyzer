#!/usr/bin/env bash
set -euo pipefail

sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv iproute2 iputils-ping dnsutils traceroute tcpdump ethtool

python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e .

echo "NetPulse installed in .venv"
echo "Run: .venv/bin/netpulse --help"
