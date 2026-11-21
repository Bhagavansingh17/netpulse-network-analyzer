# Architecture

NetPulse uses a small CLI entry point and domain modules. `utils.py` centralizes subprocess execution and Linux command errors. Collection modules run `ip`, `ping`, `ethtool`, `/sys`, socket APIs, or Scapy. Analysis modules accept plain values or dataclasses and can be unit-tested without network access.

Collection and interpretation are intentionally separate. A failing command is surfaced as a typed `NetPulseError` instead of being converted into fake “OK” data.
