"""R07 M4 deadline and refusal cases."""
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "labs/r07"))
from deadline_executor import run_diagnostic, DeviceTimeout


def test_sensor():
    assert run_diagnostic(device_id="sensor-001", diagnostic="sensor_bus_status")["status"] == "I2C_BUS_TIMEOUT"


def test_battery():
    assert run_diagnostic(device_id="sensor-001", diagnostic="battery_status")["status"] == "BATTERY_OK"


def test_unsupported_command():
    with pytest.raises(ValueError):
        run_diagnostic(device_id="sensor-001", diagnostic="flash_firmware")


@pytest.mark.parametrize("deadline", [0, -1, float("nan")])
def test_invalid_deadline(deadline):
    with pytest.raises(ValueError):
        run_diagnostic(device_id="sensor-001", diagnostic="battery_status", timeout_seconds=deadline)


def test_real_synthetic_timeout():
    with pytest.raises(DeviceTimeout, match="DEVICE_WORKER_DEADLINE_EXCEEDED"):
        run_diagnostic(device_id="sensor-001", diagnostic="sensor_bus_status", simulate_delay_ms=1500, timeout_seconds=0.1)
