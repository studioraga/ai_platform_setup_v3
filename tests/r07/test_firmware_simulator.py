"""R07 M5 firmware simulation tests."""
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "labs/r07"))
from firmware_simulator import FirmwareSimulator, FirmwareRefused


def device():
    return FirmwareSimulator(device_id="sensor-001", tenant_id="tenant_a")


def test_read():
    assert device().execute(device_id="sensor-001", command="read_measurement", arguments={})["status"] == "NOT_REPORTING"


def test_safe_reset():
    d = device()
    assert d.execute(device_id="sensor-001", command="reset_sensor_bus", arguments={})["reset_count"] == 1


def test_busy_denies_reset():
    d = device()
    d.set_operating_state("BUSY")
    with pytest.raises(FirmwareRefused, match="DEVICE_NOT_SAFE_TO_RESET"):
        d.execute(device_id="sensor-001", command="reset_sensor_bus", arguments={})
    assert d.reset_count == 0


def test_fault_denies():
    d = device()
    d.set_operating_state("FAULT")
    with pytest.raises(FirmwareRefused, match="FIRMWARE_FAULT_STATE"):
        d.execute(device_id="sensor-001", command="read_measurement", arguments={})


def test_unknown_command():
    with pytest.raises(FirmwareRefused, match="UNSUPPORTED_COMMAND"):
        device().execute(device_id="sensor-001", command="shell_execute", arguments={})


def test_wrong_device():
    with pytest.raises(FirmwareRefused, match="DEVICE_ID_MISMATCH"):
        device().execute(device_id="sensor-002", command="read_measurement", arguments={})


def test_invalid_args():
    with pytest.raises(FirmwareRefused, match="INVALID_ARGUMENTS"):
        device().execute(device_id="sensor-001", command="reset_sensor_bus", arguments={"force": True})
