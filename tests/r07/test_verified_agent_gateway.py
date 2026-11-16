"""R07 M2 signed identity to governed-tool integration tests."""

import base64
import json
import sys
from pathlib import Path

import pytest

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa


LAB = Path(__file__).resolve().parents[2] / "labs/r07"
sys.path.insert(0, str(LAB))

from approval_authority import issue_signed_approval
from governed_runtime import Approval, Denied, ToolCall, arguments_digest
from verified_agent_gateway import execute_verified_request
from verified_identity import IdentityConfig, IdentityDenied


PRIVATE_KEY = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

APPROVAL_KEY = b"synthetic-r07-m2-approval-signing-key-material"
APPROVAL_KEY_ID = "m2-lab-approval-key"

CONFIG = IdentityConfig(
    issuer="https://offline-issuer.invalid/",
    audience="principal-r07-lab",
    public_keys={"m2-lab-rsa-key": PRIVATE_KEY.public_key()},
    role_capabilities={
        "observer": frozenset({"measurement:read"}),
        "diagnostician": frozenset({"diagnostic:run"}),
    },
)


def encode(value):
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return base64.urlsafe_b64encode(encoded).rstrip(b"=").decode()


def token(*, tenant="tenant_a", roles=None):
    if roles is None:
        roles = ["observer", "diagnostician"]

    header = {
        "alg": "RS256",
        "typ": "JWT",
        "kid": "m2-lab-rsa-key",
    }

    claims = {
        "iss": CONFIG.issuer,
        "aud": CONFIG.audience,
        "sub": "operator-a",
        "tenant_id": tenant,
        "roles": roles,
        "iat": 900,
        "nbf": 900,
        "exp": 2000,
    }

    signing_input = f"{encode(header)}.{encode(claims)}"

    signature = PRIVATE_KEY.sign(
        signing_input.encode("ascii"),
        padding.PKCS1v15(),
        hashes.SHA256(),
    )

    signature_b64 = (
        base64.urlsafe_b64encode(signature)
        .rstrip(b"=")
        .decode()
    )

    return f"{signing_input}.{signature_b64}"


def make_call(*, tool="read_measurement", device="device-a"):
    arguments = (
        {"diagnostic": "sensor_bus_status"}
        if tool == "run_diagnostic"
        else {}
    )

    return ToolCall(
        request_id="m2-request-001",
        tool_name=tool,
        device_id=device,
        arguments=arguments,
    )


def signed_approval_for(call):
    approval = Approval(
        approval_id="m2-approval-001",
        approver="reviewer-b",
        subject="operator-a",
        tenant_id="tenant_a",
        tool_name=call.tool_name,
        device_id=call.device_id,
        request_id=call.request_id,
        expires_at=2000,
        argument_digest=arguments_digest(call.arguments),
    )

    return issue_signed_approval(
        approval,
        key_id=APPROVAL_KEY_ID,
        signing_key=APPROVAL_KEY,
    )


def invoke(
    bearer_token,
    *,
    call=None,
    signed_approvals=None,
    capabilities_executed=None,
):
    if call is None:
        call = make_call()

    if signed_approvals is None:
        signed_approvals = {}

    if capabilities_executed is None:
        capabilities_executed = []

    def read_measurement(**kwargs):
        capabilities_executed.append("read_measurement")
        return {"value": 42}

    def run_diagnostic(**kwargs):
        capabilities_executed.append("run_diagnostic")
        return {"status": "I2C_BUS_TIMEOUT", "simulated": True}

    return execute_verified_request(
        bearer_token=bearer_token,
        identity_config=CONFIG,
        call=call,
        signed_approvals=signed_approvals,
        verification_keys={APPROVAL_KEY_ID: APPROVAL_KEY},
        authorized_approvers=frozenset({"reviewer-b"}),
        device_tenants={
            "device-a": "tenant_a",
            "device-b": "tenant_b",
        },
        executors={
            "read_measurement": read_measurement,
            "run_diagnostic": run_diagnostic,
        },
        audit=[],
        seen_state_changes=set(),
        now=1000,
    )


def test_valid_identity_reads_own_tenant():
    result = invoke(token())
    assert result == {"value": 42}


def test_cross_tenant_device_is_denied():
    executed = []

    with pytest.raises(Denied, match="CROSS_TENANT_DEVICE"):
        invoke(
            token(),
            call=make_call(device="device-b"),
            capabilities_executed=executed,
        )

    assert executed == []


def test_invalid_token_is_rejected_before_execution():
    executed = []

    with pytest.raises(IdentityDenied, match="INVALID_TOKEN"):
        invoke(
            "not-a-valid-jwt",
            capabilities_executed=executed,
        )

    assert executed == []


def test_verified_identity_without_capability_is_denied():
    """A valid approval lets the runtime reach its capability check."""
    executed = []
    request = make_call(tool="run_diagnostic")
    signed = signed_approval_for(request)

    with pytest.raises(Denied, match="CAPABILITY_MISSING"):
        invoke(
            token(roles=["observer"]),
            call=request,
            signed_approvals={request.request_id: signed},
            capabilities_executed=executed,
        )

    assert executed == []


def test_missing_approval_precedes_capability_check():
    """Both missing: the approval adapter fails closed first."""
    executed = []

    with pytest.raises(Denied, match="SIGNED_APPROVAL_REQUIRED"):
        invoke(
            token(roles=["observer"]),
            call=make_call(tool="run_diagnostic"),
            signed_approvals={},
            capabilities_executed=executed,
        )

    assert executed == []


def test_diagnostic_requires_signed_approval():
    executed = []

    with pytest.raises(Denied, match="SIGNED_APPROVAL_REQUIRED"):
        invoke(
            token(),
            call=make_call(tool="run_diagnostic"),
            capabilities_executed=executed,
        )

    assert executed == []


def test_signed_approved_diagnostic_executes():
    call = make_call(tool="run_diagnostic")
    signed = signed_approval_for(call)
    executed = []

    result = invoke(
        token(),
        call=call,
        signed_approvals={call.request_id: signed},
        capabilities_executed=executed,
    )

    assert result["status"] == "I2C_BUS_TIMEOUT"
    assert result["simulated"] is True
    assert executed == ["run_diagnostic"]


def test_other_tenant_identity_cannot_use_tenant_a_approval():
    call = make_call(tool="run_diagnostic")
    signed = signed_approval_for(call)
    executed = []

    with pytest.raises(Denied, match="CROSS_TENANT_DEVICE"):
        invoke(
            token(tenant="tenant_b"),
            call=call,
            signed_approvals={call.request_id: signed},
            capabilities_executed=executed,
        )

    assert executed == []
