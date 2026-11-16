"""R07 M5 synthetic firmware-state refusal; no hardware I/O."""


class FirmwareRefused(Exception):
    pass


class FirmwareSimulator:
    ALLOWED = {"read_measurement", "run_diagnostic", "reset_sensor_bus"}

    def __init__(self, *, device_id, tenant_id):
        self.device_id = device_id
        self.tenant_id = tenant_id
        self.operating_state = "IDLE"
        self.reset_count = 0

    def set_operating_state(self, state):
        if state not in {"IDLE", "BUSY", "FAULT"}:
            raise ValueError("Unknown simulated firmware state")
        self.operating_state = state

    def execute(self, *, device_id, command, arguments):
        if device_id != self.device_id:
            raise FirmwareRefused("DEVICE_ID_MISMATCH")
        if command not in self.ALLOWED:
            raise FirmwareRefused("UNSUPPORTED_COMMAND")
        if not isinstance(arguments, dict):
            raise FirmwareRefused("INVALID_ARGUMENTS")
        if self.operating_state == "FAULT":
            raise FirmwareRefused("FIRMWARE_FAULT_STATE")
        if command == "read_measurement":
            if arguments:
                raise FirmwareRefused("INVALID_ARGUMENTS")
            return {"status": "NOT_REPORTING", "simulated": True}
        if command == "run_diagnostic":
            if set(arguments) != {"diagnostic"} or arguments["diagnostic"] not in {"sensor_bus_status", "battery_status"}:
                raise FirmwareRefused("INVALID_ARGUMENTS")
            return {"diagnostic": arguments["diagnostic"], "status": "I2C_BUS_TIMEOUT", "simulated": True}
        if command == "reset_sensor_bus":
            if arguments:
                raise FirmwareRefused("INVALID_ARGUMENTS")
            if self.operating_state != "IDLE":
                raise FirmwareRefused("DEVICE_NOT_SAFE_TO_RESET")
            self.reset_count += 1
            return {"reset_count": self.reset_count, "simulated": True}
        raise FirmwareRefused("UNREACHABLE_COMMAND")
