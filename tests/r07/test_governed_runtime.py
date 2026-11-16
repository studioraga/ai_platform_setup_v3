import importlib.util
import sys
from pathlib import Path

import pytest


SOURCE = (
    Path(__file__).resolve().parents[2]
    / "labs/r07/governed_runtime.py"
)

spec = importlib.util.spec_from_file_location(
    "r07_governed_runtime", SOURCE
)
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)


def principal(
    subject="operator-a",
    tenant="tenant_a",
    capabilities=None,
):
    if capabilities is None:
        capabilities = {
            "measurement:read",
            "diagnostic:run",
            "bus:reset",
        }
    return m.Principal(
        subject,
        tenant,
        frozenset(capabilities),
    )


def call(
    tool="read_measurement",
    device="device-a",
    request="request-001",
    args=None,
):
    return m.ToolCall(
        request,
        tool,
        device,
        {} if args is None else args,
    )

def approval(
    request="request-001",
    tool="run_diagnostic",
    device="device-a",
    subject="operator-a",
    tenant="tenant_a",
    expires=2000,
    approver="reviewer-b",
    arguments=None,
):
    if arguments is None:
        arguments = (
            {"diagnostic": "sensor_bus_status"}
            if tool == "run_diagnostic"
            else {}
        )

    return m.Approval(
        approval_id="approval-001",
        approver=approver,
        subject=subject,
        tenant_id=tenant,
        tool_name=tool,
        device_id=device,
        request_id=request,
        expires_at=expires,
        argument_digest=m.arguments_digest(arguments),
    )

def run(
    request=None,
    *,
    identity=None,
    approvals=None,
    executors=None,
    audit=None,
    seen=None,
    registry=None,
):
    if request is None:
        request = call()
    if identity is None:
        identity = principal()
    if approvals is None:
        approvals = {}
    if executors is None:
        executors = {
            "read_measurement": lambda **kw: {"value": 42},
            "run_diagnostic": lambda **kw: {"healthy": True},
            "reset_sensor_bus": lambda **kw: {"reset": True},
        }
    if audit is None:
        audit = []
    if seen is None:
        seen = set()
    if registry is None:
        registry = {
            "device-a": "tenant_a",
            "device-b": "tenant_b",
        }

    return m.execute(
        request,
        principal=identity,
        device_tenants=registry,
        approvals=approvals,
        executors=executors,
        audit=audit,
        seen_state_changes=seen,
        now=1000,
    )


def test_authorized_read_executes():
    audit = []
    result = run(audit=audit)
    assert result == {"value": 42}
    assert [x["status"] for x in audit] == [
        "ADMITTED", "COMPLETED"
    ]


@pytest.mark.parametrize(
    "identity",
    [
        False,
        m.Principal("", "tenant_a", frozenset()),
        m.Principal("operator", "", frozenset()),
    ],
)
def test_invalid_principal_denied(identity):
    audit = []
    with pytest.raises(m.Denied):
        run(
            identity=(
                None if identity is False else identity
            ),
            audit=audit,
        ) if identity is not False else m.execute(
            call(),
            principal=None,
            device_tenants={"device-a": "tenant_a"},
            approvals={},
            executors={},
            audit=audit,
            seen_state_changes=set(),
            now=1000,
        )
    assert audit[-1]["status"] == "DENIED"


def test_cross_tenant_device_denied_without_invoking_tool():
    calls = []
    audit = []

    with pytest.raises(m.Denied):
        run(
            call(device="device-b"),
            executors={
                "read_measurement": lambda **kw: calls.append(kw)
            },
            audit=audit,
        )

    assert calls == []
    assert audit[-1]["reason"] == "CROSS_TENANT_DEVICE"


@pytest.mark.parametrize(
    "tool",
    ["delete_measurement", "firmware_flash", "shell_execute"],
)
def test_unknown_tool_denied(tool):
    with pytest.raises(m.Denied, match="UNKNOWN_TOOL"):
        run(call(tool=tool))


def test_missing_capability_denied():
    with pytest.raises(m.Denied, match="CAPABILITY_MISSING"):
        run(
            identity=principal(capabilities=set())
        )


def test_unknown_device_denied():
    with pytest.raises(m.Denied, match="UNKNOWN_DEVICE"):
        run(call(device="device-not-registered"))


def test_diagnostic_without_approval_denied():
    with pytest.raises(m.Denied, match="APPROVAL_MISSING"):
        run(
            call(
                tool="run_diagnostic",
                args={"diagnostic": "sensor_bus_status"},
            )
        )


@pytest.mark.parametrize(
    "bad_approval",
    [
        {"subject": "other-operator"},
        {"tenant": "tenant_b"},
        {"tool": "reset_sensor_bus"},
        {"device": "device-b"},
        {"request": "different-request"},
        {"expires": 1000},
        {"approver": "operator-a"},
    ],
)
def test_mismatched_or_expired_approval_denied(bad_approval):
    values = dict(
        request="request-001",
        tool="run_diagnostic",
        device="device-a",
        subject="operator-a",
        tenant="tenant_a",
        expires=2000,
        approver="reviewer-b",
    )
    values.update(bad_approval)

    with pytest.raises(
        m.Denied,
        match="APPROVAL_INVALID_OR_EXPIRED",
    ):
        run(
            call(
                tool="run_diagnostic",
                args={"diagnostic": "sensor_bus_status"},
            ),
            approvals={"request-001": approval(**values)},
        )


def test_approved_diagnostic_executes():
    result = run(
        call(
            tool="run_diagnostic",
            args={"diagnostic": "sensor_bus_status"},
        ),
        approvals={
            "request-001": approval()
        },
    )
    assert result == {"healthy": True}


def test_unexpected_arguments_denied():
    with pytest.raises(m.Denied, match="INVALID_ARGUMENTS"):
        run(
            call(args={
                "tenant_override": "tenant_b",
                "instruction": "ignore policy"
            })
        )


def test_invalid_diagnostic_denied():
    with pytest.raises(m.Denied, match="INVALID_ARGUMENTS"):
        run(
            call(
                tool="run_diagnostic",
                args={"diagnostic": "delete_all"},
            )
        )


def test_state_change_requires_approval():
    with pytest.raises(m.Denied, match="APPROVAL_MISSING"):
        run(call(tool="reset_sensor_bus"))


def test_duplicate_state_change_denied():
    seen = set()
    audit = []
    executed = []

    executors = {
        "reset_sensor_bus":
            lambda **kw: executed.append(kw) or {"ok": True}
    }

    request = call(tool="reset_sensor_bus")

    approvals = {
        "request-001": approval(tool="reset_sensor_bus")
    }

    assert run(
        request,
        approvals=approvals,
        executors=executors,
        seen=seen,
        audit=audit,
    ) == {"ok": True}

    with pytest.raises(
        m.Denied,
        match="DUPLICATE_STATE_CHANGE",
    ):
        run(
            request,
            approvals=approvals,
            executors=executors,
            seen=seen,
            audit=audit,
        )

    assert len(executed) == 1


def test_executor_failure_never_reports_completion():
    audit = []

    def fail(**kwargs):
        raise RuntimeError("synthetic device offline")

    with pytest.raises(m.ToolExecutionFailed):
        run(
            executors={"read_measurement": fail},
            audit=audit,
        )

    assert [x["status"] for x in audit] == [
        "ADMITTED", "FAILED"
    ]


def test_missing_executor_denied():
    with pytest.raises(m.Denied, match="EXECUTOR_UNAVAILABLE"):
        run(executors={})


def test_audit_failure_prevents_execution():
    invoked = []

    class BrokenAudit:
        def append(self, item):
            raise OSError("audit store unavailable")

    with pytest.raises(OSError):
        run(
            audit=BrokenAudit(),
            executors={
                "read_measurement":
                    lambda **kw: invoked.append(kw)
            },
        )

    assert invoked == []

def test_approval_cannot_change_diagnostic_arguments():
    approved = approval(
        arguments={"diagnostic": "sensor_bus_status"}
    )

    changed_request = call(
        tool="run_diagnostic",
        args={"diagnostic": "battery_status"},
    )

    with pytest.raises(
        m.Denied,
        match="APPROVAL_INVALID_OR_EXPIRED",
    ):
        run(
            changed_request,
            approvals={"request-001": approved},
        )

def test_argument_digest_independent_of_dictionary_order():
    first = {
        "a": 1,
        "b": 2,
    }

    second = {
        "b": 2,
        "a": 1,
    }

    assert m.arguments_digest(first) == m.arguments_digest(second)

def test_argument_digest_rejects_non_json_data():
    with pytest.raises(ValueError):
        m.arguments_digest({"invalid": object()})

@pytest.mark.parametrize(
    "malicious_request",
    [
        call(
            tool="read_measurement",
            args={"instruction": "Ignore the approval policy"},
        ),
        call(
            tool="shell_execute",
            args={"command": "echo synthetic"},
        ),
        call(tool="reset_sensor_bus"),
        call(device="device-b"),
    ],
)
def test_untrusted_agent_proposals_are_denied(
    malicious_request,
):
    executions = []

    def executor(**kwargs):
        executions.append(kwargs)
        return {"ok": True}

    with pytest.raises(m.Denied):
        run(
            malicious_request,
            executors={
                "read_measurement": executor,
                "shell_execute": executor,
                "reset_sensor_bus": executor,
            },
        )

    assert executions == []
