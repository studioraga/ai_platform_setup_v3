
"""R07 M1: research-only authenticated approval boundary.

HMAC is used to demonstrate record integrity and provenance
from a trusted issuer. The issuer must protect its signing key.

Not production qualification:
- No OIDC/JWT verification
- No organizational approval workflow
- No durable approval database
- No single-use approval consumption
- No key rotation or revocation service
"""

import hashlib
import hmac
import json

from dataclasses import asdict, dataclass
from typing import Any, Callable

from governed_runtime import (
    Approval,
    Denied,
    Principal,
    ToolCall,
    execute,
)


@dataclass(frozen=True)
class SignedApproval:
    approval: Approval
    key_id: str
    signature: str


def canonical_approval(approval: Approval, key_id: str) -> bytes:
    """Canonical serialization of every approval field."""
    payload = {
        "schema_version": 1,
        "key_id": key_id,
        "approval": asdict(approval),
    }

    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def issue_signed_approval(
    approval: Approval,
    *,
    key_id: str,
    signing_key: bytes,
) -> SignedApproval:
    """Trusted issuer operation. Never expose to the LLM."""

    if not isinstance(approval, Approval):
        raise TypeError("Approval required")

    if not key_id:
        raise ValueError("Key ID required")

    if not isinstance(signing_key, bytes) or len(signing_key) < 32:
        raise ValueError("Signing key must contain at least 32 bytes")

    signature = hmac.new(
        signing_key,
        canonical_approval(approval, key_id),
        hashlib.sha256,
    ).hexdigest()

    return SignedApproval(
        approval=approval,
        key_id=key_id,
        signature=signature,
    )


def verify_signed_approval(
    signed: SignedApproval,
    *,
    verification_keys: dict[str, bytes],
    authorized_approvers: frozenset[str],
) -> Approval:
    """Fail closed on missing, unknown or altered approval evidence."""

    if not isinstance(signed, SignedApproval):
        raise Denied("SIGNED_APPROVAL_REQUIRED")

    key = verification_keys.get(signed.key_id)

    if not isinstance(key, bytes) or len(key) < 32:
        raise Denied("APPROVAL_KEY_UNTRUSTED")

    if signed.approval.approver not in authorized_approvers:
        raise Denied("APPROVER_NOT_AUTHORIZED")

    expected = hmac.new(
        key,
        canonical_approval(signed.approval, signed.key_id),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected, signed.signature):
        raise Denied("APPROVAL_SIGNATURE_INVALID")

    return signed.approval


def execute_with_verified_approval(
    call: ToolCall,
    *,
    principal: Principal | None,
    device_tenants: dict[str, str],
    signed_approvals: dict[str, SignedApproval],
    verification_keys: dict[str, bytes],
    authorized_approvers: frozenset[str],
    executors: dict[str, Callable],
    audit: list[dict],
    seen_state_changes: set[str],
    now: float,
) -> Any:
    """Controlled ingress adapter for the existing governed runtime.

    The caller must not expose governed_runtime.execute directly
    to untrusted requests.
    """

    from governed_runtime import POLICY

    def deny(reason: str):
        audit.append({
            "request_id": getattr(call, "request_id", ""),
            "status": "DENIED",
            "reason": reason,
            "phase": "APPROVAL_ADMISSION",
        })
        raise Denied(reason)

    if not isinstance(call, ToolCall):
        deny("INVALID_TOOL_REQUEST")

    policy = POLICY.get(call.tool_name)

    # Unknown tools are rejected by the existing runtime.
    if policy is None:
        return execute(
            call,
            principal=principal,
            device_tenants=device_tenants,
            approvals={},
            executors=executors,
            audit=audit,
            seen_state_changes=seen_state_changes,
            now=now,
        )

    verified: dict[str, Approval] = {}

    if policy["approval_required"]:
        signed = signed_approvals.get(call.request_id)

        if signed is None:
            deny("SIGNED_APPROVAL_REQUIRED")

        try:
            approval = verify_signed_approval(
                signed,
                verification_keys=verification_keys,
                authorized_approvers=authorized_approvers,
            )
        except Denied as exc:
            deny(str(exc))

        verified[call.request_id] = approval

    return execute(
        call,
        principal=principal,
        device_tenants=device_tenants,
        approvals=verified,
        executors=executors,
        audit=audit,
        seen_state_changes=seen_state_changes,
        now=now,
    )
