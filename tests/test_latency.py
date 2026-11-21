from netpulse.latency import calculate_latency_stats, percentile


def test_latency_statistics():
    stats = calculate_latency_stats("192.0.2.1", [1.0, 2.0, 3.0, 4.0, 100.0], 5)
    assert stats.minimum_ms == 1.0
    assert stats.maximum_ms == 100.0
    assert stats.packet_loss_percent == 0.0
    assert stats.successful == 5
    assert stats.jitter_ms is not None


def test_packet_loss_with_failed_probes():
    stats = calculate_latency_stats("192.0.2.1", [1.0, 2.0], 4)
    assert stats.packet_loss_percent == 50.0


def test_percentile_interpolation():
    assert abs(percentile([1.0, 2.0, 3.0, 4.0], 95) - 3.85) < 1e-9
    assert percentile([], 95) is None
