"""Bounded single-process diagnostic executor, research-only."""
import json
import math
import subprocess
import sys
from pathlib import Path


class DeviceTimeout(Exception):
    pass


class DeviceExecutionError(Exception):
    pass


def run_diagnostic(*, device_id, diagnostic, timeout_seconds=10.0, simulate_delay_ms=0):
    if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, (int, float)) or not math.isfinite(timeout_seconds) or not 0 < timeout_seconds <= 30:
        raise ValueError("Invalid deadline")
    if not isinstance(device_id, str) or not device_id.strip():
        raise ValueError("Device ID required")
    if diagnostic not in {"sensor_bus_status", "battery_status"}:
        raise ValueError("Unsupported diagnostic")
    if isinstance(simulate_delay_ms, bool) or not isinstance(simulate_delay_ms, int) or not 0 <= simulate_delay_ms <= 5000:
        raise ValueError("Invalid simulation delay")

    worker = Path(__file__).with_name("device_worker.py")
    request = {"device_id": device_id, "diagnostic": diagnostic, "delay_ms": simulate_delay_ms}
    try:
        proc = subprocess.run(
            [sys.executable, str(worker)],
            input=json.dumps(request),
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise DeviceTimeout("DEVICE_WORKER_DEADLINE_EXCEEDED") from exc
    if proc.returncode != 0:
        raise DeviceExecutionError(f"DEVICE_WORKER_EXIT_{proc.returncode}")
    if len(proc.stdout) > 65536:
        raise DeviceExecutionError("OVERSIZED_DEVICE_RESPONSE")
    try:
        result = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise DeviceExecutionError("INVALID_DEVICE_RESPONSE") from exc
    if not isinstance(result, dict) or result.get("device_id") != device_id or result.get("diagnostic") != diagnostic or result.get("simulated") is not True:
        raise DeviceExecutionError("DEVICE_RESPONSE_MISMATCH")
    return result
