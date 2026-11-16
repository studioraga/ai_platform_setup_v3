
"""R07 M1 signed-approval boundary tests."""

import importlib.util
import sys

from dataclasses import replace
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / "labs/r07"

sys.path.insert(0, str(LAB))

import governed_runtime as runtime
import approval_authority as authority


KEY = b"synthetic-r07-test-signing-key-32bytes-minimum"
KEY_ID = "r07-lab-key-001"


def principal():
    return runtime.Principal(
        subject="operator-a",
        tenant_id="tenant_a",
        capabilities=frozenset({
            "measurement:read",
            "diagnostic:run",
            "bus:reset",
        }),
    )


def request(tool="run_diagnostic", args=None):
    if args is None:
        args = (
            {"diagnostic": "sensor_bus_status"}
            if tool == "run_diagnostic"
            else {}
        )

    return runtime.ToolCall(
        request_id="request-001",
        tool_name=tool,
        device_id="device-a",
        arguments=args,
    )


def approval_for(call=None):
    if call is None:
        call = request()

    return runtime.Approval(
        approval_id="approval-001",
        approver="reviewer-b",
        subject="operator-a",
        tenant_id="tenant_a",
        tool_name=call.tool_name,
        device_id=call.device_id,
        request_id=call.request_id,
        expires_at=2000,
        argument_digest=runtime.arguments_digest(call.arguments),
    )


def signed_for(call=None):
    return authority.issue_signed_approval(
        approval_for(call),
        key_id=KEY_ID,
        signing_key=KEY,
    )


def invoke(call=None, signed=None, **overrides):
    if call is None:
        call = request()

    if signed is None:
        signed = signed_for(call)

    options = dict(
        principal=principal(),
        device_tenants={"device-a": "tenant_a"},
        signed_approvals={call.request_id: signed},
        verification_keys={KEY_ID: KEY},
        authorized_approvers=frozenset({"reviewer-b"}),
        executors={
            "run_diagnostic": lambda **kw: {"healthy": True},
            "read_measurement": lambda **kw: {"value": 42},
            "reset_sensor_bus": lambda **kw: {"reset": True},
        },
        audit=[],
        seen_state_changes=set(),
        now=1000,
    )

    options.update(overrides)

    return authority.execute_with_verified_approval(call, **options)


def test_genuine_lab_signature_permits_diagnostic():
    assert invoke() == {"healthy": True}


def test_valid_approval_signature_is_deterministic():
    a = signed_for()
    b = signed_for()
    assert a.signature == b.signature


def test_no_signed_approval_denied():
    with pytest.raises(
        runtime.Denied,
        match="SIGNED_APPROVAL_REQUIRED",
    ):
        invoke(signed_approvals={})


def test_unknown_key_denied():
    with pytest.raises(
        runtime.Denied,
        match="APPROVAL_KEY_UNTRUSTED",
    ):
        invoke(verification_keys={})


def test_unauthorized_approver_denied():
    with pytest.raises(
        runtime.Denied,
        match="APPROVER_NOT_AUTHORIZED",
    ):
        invoke(authorized_approvers=frozenset())


def test_tampered_approval_denied():
    original = signed_for()

    changed = replace(
        original,
        approval=replace(
            original.approval,
            tenant_id="tenant_b",
        ),
    )

    with pytest.raises(
        runtime.Denied,
        match="APPROVAL_SIGNATURE_INVALID",
    ):
        invoke(signed=changed)


def test_wrong_signature_denied():
    tampered = replace(
        signed_for(),
        signature="0" * 64,
    )

    with pytest.raises(
        runtime.Denied,
        match="APPROVAL_SIGNATURE_INVALID",
    ):
        invoke(signed=tampered)


def test_approved_arguments_cannot_be_changed():
    changed_call = request(
        args={"diagnostic": "battery_status"}
    )

    with pytest.raises(
        runtime.Denied,
        match="APPROVAL_INVALID_OR_EXPIRED",
    ):
        invoke(
            call=changed_call,
            signed=signed_for(request()),
        )


def test_expired_approval_denied():
    with pytest.raises(
        runtime.Denied,
        match="APPROVAL_INVALID_OR_EXPIRED",
    ):
        invoke(now=2000)


def test_cross_tenant_device_denied():
    with pytest.raises(
        runtime.Denied,
        match="CROSS_TENANT_DEVICE",
    ):
        invoke(device_tenants={"device-a": "tenant_b"})


def test_read_only_operation_without_approval():
    call = request(tool="read_measurement")

    assert invoke(
        call=call,
        signed_approvals={},
    ) == {"value": 42}


def test_direct_approval_object_is_not_accepted():
    with pytest.raises(
        runtime.Denied,
        match="SIGNED_APPROVAL_REQUIRED",
    ):
        invoke(signed=approval_for())


def test_short_signing_key_rejected():
    with pytest.raises(ValueError):
        authority.issue_signed_approval(
            approval_for(),
            key_id=KEY_ID,
            signing_key=b"short",
        )

def test_attacker_signed_approval_rejected():
    attacker_key = b"attacker-owned-synthetic-key-material-12345"

    forged = authority.issue_signed_approval(
        approval_for(),
        key_id=KEY_ID,
        signing_key=attacker_key,
    )

    with pytest.raises(
        runtime.Denied,
        match="APPROVAL_SIGNATURE_INVALID",
    ):
        invoke(signed=forged)
