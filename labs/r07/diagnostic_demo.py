"""Synthetic governed embedded-device diagnostic demonstration."""

from governed_runtime import (
    Approval,
    Principal,
    ToolCall,
    arguments_digest,
    execute,
)


def main():
    audit = []
    seen_state_changes = set()

    principal = Principal(
        subject="operator-a",
        tenant_id="tenant_a",
        capabilities=frozenset({
            "measurement:read",
            "diagnostic:run",
        }),
    )

    device_tenants = {
        "temperature-sensor-001": "tenant_a",
        "temperature-sensor-002": "tenant_b",
    }

    def read_measurement(*, device_id, arguments):
        return {
            "device_id": device_id,
            "measurement": None,
            "device_status": "NOT_REPORTING",
        }

    def run_diagnostic(*, device_id, arguments):
        return {
            "device_id": device_id,
            "diagnostic": arguments["diagnostic"],
            "result": "I2C_BUS_TIMEOUT",
            "firmware_response": "SIMULATED",
        }

    executors = {
        "read_measurement": read_measurement,
        "run_diagnostic": run_diagnostic,
    }

    read_call = ToolCall(
        request_id="measurement-001",
        tool_name="read_measurement",
        device_id="temperature-sensor-001",
    )

    measurement = execute(
        read_call,
        principal=principal,
        device_tenants=device_tenants,
        approvals={},
        executors=executors,
        audit=audit,
        seen_state_changes=seen_state_changes,
        now=1000,
    )

    assert measurement["device_status"] == "NOT_REPORTING"

    diagnostic_call = ToolCall(
        request_id="diagnostic-001",
        tool_name="run_diagnostic",
        device_id="temperature-sensor-001",
        arguments={"diagnostic": "sensor_bus_status"},
    )

    approved = Approval(
        approval_id="synthetic-approval-001",
        approver="reviewer-b",
        subject=principal.subject,
        tenant_id=principal.tenant_id,
        tool_name=diagnostic_call.tool_name,
        device_id=diagnostic_call.device_id,
        request_id=diagnostic_call.request_id,
        expires_at=2000,
        argument_digest=arguments_digest(
            diagnostic_call.arguments
        ),
    )

    diagnostic = execute(
        diagnostic_call,
        principal=principal,
        device_tenants=device_tenants,
        approvals={diagnostic_call.request_id: approved},
        executors=executors,
        audit=audit,
        seen_state_changes=seen_state_changes,
        now=1000,
    )

    assert diagnostic["result"] == "I2C_BUS_TIMEOUT"
    assert diagnostic["firmware_response"] == "SIMULATED"

    assert [event["status"] for event in audit] == [
        "ADMITTED",
        "COMPLETED",
        "ADMITTED",
        "COMPLETED",
    ]

    print("Measurement:", measurement)
    print("Diagnostic:", diagnostic)
    print("Audit:", audit)
    print("PASS: Synthetic governed diagnostic workflow")


if __name__ == "__main__":
    main()
