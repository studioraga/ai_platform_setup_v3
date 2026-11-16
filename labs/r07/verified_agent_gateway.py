
"""R07 M2 offline verified-identity tool gateway.

The JWT is verified before the tool can execute.

The approval issuer, public keys, approver allowlist,
device registry and executors must be trusted application
configuration, not values supplied by an AI model.

This module is research-only; it does not provide a real
OIDC provider, JWKS rotation or durable replay control.
"""

from typing import Any, Callable

from approval_authority import (
    SignedApproval,
    execute_with_verified_approval,
)
from governed_runtime import ToolCall
from verified_identity import IdentityConfig, verify_jwt


def execute_verified_request(
    *,
    bearer_token: str,
    identity_config: IdentityConfig,
    call: ToolCall,
    signed_approvals: dict[str, SignedApproval],
    verification_keys: dict[str, bytes],
    authorized_approvers: frozenset[str],
    device_tenants: dict[str, str],
    executors: dict[str, Callable],
    audit: list[dict],
    seen_state_changes: set[str],
    now: float,
) -> Any:
    """Verify JWT identity before applying R07 tool authorization."""

    principal = verify_jwt(
        bearer_token,
        identity_config,
        now=now,
    )

    return execute_with_verified_approval(
        call,
        principal=principal,
        device_tenants=device_tenants,
        signed_approvals=signed_approvals,
        verification_keys=verification_keys,
        authorized_approvers=authorized_approvers,
        executors=executors,
        audit=audit,
        seen_state_changes=seen_state_changes,
        now=now,
    )
