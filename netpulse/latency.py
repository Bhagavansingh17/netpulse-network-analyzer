import math
import re
import statistics
from typing import Iterable, Optional

from .models import LatencyStats
from .utils import NetPulseError, require_command, run_command


PING_RTT_PATTERN = re.compile(r"(?:time=|time<)\s*([0-9]+(?:\.[0-9]+)?)")


def percentile(values: list[float], percentile_value: float) -> Optional[float]:
    if not values:
        return None
    if not 0 <= percentile_value <= 100:
        raise ValueError("Percentile must be between 0 and 100")
    ordered = sorted(values)
    position = (len(ordered) - 1) * percentile_value / 100
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def calculate_latency_stats(target: str, rtts: Iterable[float], probes: int) -> LatencyStats:
    values = [float(value) for value in rtts]
    successful = len(values)
    loss = ((probes - successful) / probes * 100) if probes else 100.0
    differences = [
        abs(values[index] - values[index - 1])
        for index in range(1, len(values))
    ]
    stats = LatencyStats(
        target=target,
        probes=probes,
        successful=successful,
        rtts_ms=values,
        packet_loss_percent=max(0.0, loss),
    )
    if values:
        stats.minimum_ms = min(values)
        stats.average_ms = statistics.fmean(values)
        stats.median_ms = statistics.median(values)
        stats.stddev_ms = statistics.pstdev(values) if len(values) > 1 else 0.0
        stats.p95_ms = percentile(values, 95)
        stats.p99_ms = percentile(values, 99)
        stats.maximum_ms = max(values)
        stats.jitter_ms = statistics.fmean(differences) if differences else 0.0
    return stats


def measure_latency(
    target: str,
    probes: int = 100,
    timeout_seconds: float = 1.0,
) -> LatencyStats:
    if probes < 1:
        raise ValueError("Probe count must be at least 1")
    ping = require_command("ping")
    code, stdout, stderr = run_command(
        [ping, "-n", "-c", str(probes), "-W", str(max(1, int(timeout_seconds))), target],
        timeout=max(10.0, probes * timeout_seconds + 5),
    )
    rtts = [float(match) for match in PING_RTT_PATTERN.findall(stdout)]
    if code != 0 and not rtts:
        raise NetPulseError(
            f"Latency measurement failed for '{target}': "
            f"{stderr or 'host unreachable or ping unavailable'}"
        )
    return calculate_latency_stats(target, rtts, probes)


def print_latency(stats: LatencyStats, advanced: bool = False) -> None:
    print("LATENCY ANALYSIS")
    print("================")
    print()
    print(f"Target      : {stats.target}")
    print(f"Probes      : {stats.probes}")
    print(f"Successful  : {stats.successful}")
    print()
    print(f"Packet Loss : {stats.packet_loss_percent:.2f}%")
    print()
    print(f"Min         : {stats.minimum_ms:.3f} ms" if stats.minimum_ms is not None else "Min         : N/A")
    print(f"Average     : {stats.average_ms:.3f} ms" if stats.average_ms is not None else "Average     : N/A")
    print(f"Median      : {stats.median_ms:.3f} ms" if stats.median_ms is not None else "Median      : N/A")
    print(f"Std Dev     : {stats.stddev_ms:.3f} ms" if stats.stddev_ms is not None else "Std Dev     : N/A")
    print(f"p95         : {stats.p95_ms:.3f} ms" if stats.p95_ms is not None else "p95         : N/A")
    print(f"p99         : {stats.p99_ms:.3f} ms" if stats.p99_ms is not None else "p99         : N/A")
    print(f"Max         : {stats.maximum_ms:.3f} ms" if stats.maximum_ms is not None else "Max         : N/A")
    print(f"Jitter      : {stats.jitter_ms:.3f} ms" if stats.jitter_ms is not None else "Jitter      : N/A")
    if advanced:
        print()
        print("Measurement note:")
        print("- Results use the system ping utility and monotonic RTT timing.")
        print("- p95/p99 describe the slow tail, not only the average.")
        print("- Jitter is the mean absolute change between consecutive RTT samples.")
