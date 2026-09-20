from __future__ import annotations

import os
from pathlib import Path
from .interfaces import SystemTelemetry


class ResourceGovernor:
    """Independent system resource governor (MA-CORE-005).

    Monitors system telemetry (CPU load and RAM availability) using kernel /proc
    interfaces with userspace fallback to prevent resource starvation or system lockups.
    """

    def __init__(
        self,
        min_memory_mb: float = 100.0,
        max_load_per_core: float = 8.0,
    ) -> None:
        self.min_memory_mb = min_memory_mb
        self.max_load_per_core = max_load_per_core

    def get_telemetry(self) -> SystemTelemetry:
        cores = os.cpu_count() or 1
        load_avg = self._read_loadavg()
        mem_available_mb, mem_percent = self._read_memory()

        is_healthy = True
        warnings = []

        if mem_available_mb is not None and mem_available_mb < self.min_memory_mb:
            is_healthy = False
            warnings.append(f"Low memory: {mem_available_mb:.1f}MB available (min {self.min_memory_mb}MB)")

        current_load = load_avg[0]
        if current_load > (cores * self.max_load_per_core):
            is_healthy = False
            warnings.append(f"High CPU load: {current_load:.2f} across {cores} cores")

        details = "; ".join(warnings) if warnings else "System telemetry is within safe operating bounds."

        # Approximate CPU percent from 1-min load average normalized by core count
        cpu_percent = min(100.0, max(0.0, (current_load / cores) * 100.0))

        return SystemTelemetry(
            cpu_percent=round(cpu_percent, 1),
            memory_available_mb=round(mem_available_mb or 0.0, 1),
            memory_percent=round(mem_percent or 0.0, 1),
            load_average=load_avg,
            is_healthy=is_healthy,
            details=details,
        )

    def is_safe_to_execute(self) -> tuple[bool, str]:
        telemetry = self.get_telemetry()
        if not telemetry.is_healthy:
            return False, f"Execution paused by Resource Governor: {telemetry.details}"
        return True, telemetry.details

    def _read_loadavg(self) -> list[float]:
        proc_load = Path("/proc/loadavg")
        if proc_load.is_file():
            try:
                parts = proc_load.read_text(encoding="utf-8").split()
                return [float(parts[0]), float(parts[1]), float(parts[2])]
            except Exception:
                pass
        try:
            if hasattr(os, "getloadavg"):
                return [float(x) for x in os.getloadavg()]
        except Exception:
            pass
        return [0.0, 0.0, 0.0]

    def _read_memory(self) -> tuple[float | None, float | None]:
        proc_mem = Path("/proc/meminfo")
        if proc_mem.is_file():
            try:
                mem_info: dict[str, float] = {}
                for line in proc_mem.read_text(encoding="utf-8").splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        num = v.strip().split()[0]
                        if num.isdigit():
                            mem_info[k.strip()] = float(num)
                total_kb = mem_info.get("MemTotal", 0.0)
                avail_kb = mem_info.get("MemAvailable", mem_info.get("MemFree", 0.0))
                if total_kb > 0:
                    avail_mb = avail_kb / 1024.0
                    used_percent = ((total_kb - avail_kb) / total_kb) * 100.0
                    return avail_mb, used_percent
            except Exception:
                pass

        # Userspace fallback estimation if /proc/meminfo is not available
        return 1024.0, 50.0
