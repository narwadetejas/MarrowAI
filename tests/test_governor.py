from __future__ import annotations

from marrowai.governor import ResourceGovernor


def test_resource_governor_telemetry():
    gov = ResourceGovernor()
    telemetry = gov.get_telemetry()
    assert telemetry is not None
    assert isinstance(telemetry.cpu_percent, float)
    assert isinstance(telemetry.memory_available_mb, float)
    assert isinstance(telemetry.load_average, list)
    assert len(telemetry.load_average) == 3


def test_resource_governor_safe_check():
    gov = ResourceGovernor(min_memory_mb=1.0, max_load_per_core=100.0)
    safe, details = gov.is_safe_to_execute()
    assert safe is True
    assert "within safe" in details or "telemetry" in details


def test_resource_governor_flags_insufficient_memory():
    # Artificially set required memory extremely high (e.g. 100 terabytes)
    gov = ResourceGovernor(min_memory_mb=100_000_000.0)
    safe, details = gov.is_safe_to_execute()
    assert safe is False
    assert "Resource Governor" in details
    assert "Low memory" in details
