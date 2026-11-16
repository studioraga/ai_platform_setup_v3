"""Disposable synthetic device subprocess, never real hardware."""
import json
import sys
import time


def main():
    try:
        request = json.load(sys.stdin)
        if not isinstance(request, dict) or set(request) != {"device_id", "diagnostic", "delay_ms"}:
            return 2
        device_id = request["device_id"]
        diagnostic = request["diagnostic"]
        delay = request["delay_ms"]
        if not isinstance(device_id, str) or not device_id:
            return 2
        if diagnostic not in {"sensor_bus_status", "battery_status"}:
            return 3
        if isinstance(delay, bool) or not isinstance(delay, int) or not 0 <= delay <= 5000:
            return 2
        time.sleep(delay / 1000)
        print(json.dumps({
            "device_id": device_id,
            "diagnostic": diagnostic,
            "status": "I2C_BUS_TIMEOUT" if diagnostic == "sensor_bus_status" else "BATTERY_OK",
            "simulated": True,
        }, sort_keys=True), flush=True)
        return 0
    except (ValueError, TypeError, KeyError):
        return 2


if __name__ == "__main__":
    sys.exit(main())
