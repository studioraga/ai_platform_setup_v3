
"""R07 research-only deterministic governed tool executor.

Security boundary:
- The principal must come from trusted application identity handling.
- Device tenancy must come from a trusted device registry.
- Approvals must come from an authenticated authorization service.
- The AI model must not control these sources.

Limitations:
- No principal authentication or approval-store authenticity verification.
- No durable or distributed idempotency.
- No independently enforced execution deadline.
- No durable audit store.
- No physical hardware control or firmware-safety qualification.
"""

import hashlib
import json

from dataclasses import dataclass, field
from typing import Any, Callable


class Denied(Exception):
    """Action refused by deterministic application policy."""


class ToolExecutionFailed(Exception):
    """An authorized tool failed during execution."""


@dataclass(frozen=True)
class Principal:
    subject: str
    tenant_id: str
    capabilities: frozenset[str]


@dataclass(frozen=True)
class ToolCall:
    request_id: str
    tool_name: str
    device_id: str
    arguments: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Approval:
    approval_id: str
    approver: str
    subject: str
    tenant_id: str
    tool_name: str
    device_id: str
    request_id: str
    expires_at: float
    argument_digest: str


# Application-owned policy.
# These definitions are not controlled by model output.
POLICY = {
    "read_measurement": {
        "capability": "measurement:read",
        "approval_required": False,
        "state_changing": False,
    },
    "run_diagnostic": {
        "capability": "diagnostic:run",
        "approval_required": True,
        "state_changing": False,
    },
    "reset_sensor_bus": {
        "capability": "bus:reset",
        "approval_required": True,
        "state_changing": True,
    },
}


def arguments_digest(arguments: dict[str, Any]) -> str:
    """Return a deterministic SHA-256 digest of tool arguments.

    Canonical JSON key ordering ensures that equivalent dictionaries
    have matching digests regardless of insertion order.

    This digest binds arguments to an approval record. It does not
    authenticate the approval or prevent record forgery.
    """
    if not isinstance(arguments, dict):
        raise ValueError("Arguments must be a dictionary")

    try:
        encoded = json.dumps(
            arguments,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "Arguments must be JSON serializable"
        ) from exc

    return hashlib.sha256(encoded).hexdigest()


def execute(
    call: ToolCall,
    *,
    principal: Principal | None,
    device_tenants: dict[str, str],
    approvals: dict[str, Approval],
    executors: dict[str, Callable],
    audit: list[dict],
    seen_state_changes: set[str],
    now: float,
) -> Any:
    """Validate, authorize, and invoke a synthetic tool executor.

    Identity, registry, and approval inputs are assumed to originate
    from trusted application services.

    For state-changing tools, the in-memory replay set records an
    attempt before execution. Failure leaves the request marked,
    requiring manual reconciliation in this research prototype.
    """

    def record(status: str, reason: str) -> None:
        audit.append({
            "request_id": getattr(call, "request_id", ""),
            "tool": getattr(call, "tool_name", ""),
            "device_id": getattr(call, "device_id", ""),
            "principal": (
                principal.subject
                if isinstance(principal, Principal)
                else None
            ),
            "status": status,
            "reason": reason,
        })

    def deny(reason: str) -> None:
        record("DENIED", reason)
        raise Denied(reason)

    # 1. Trusted principal presence.
    if not isinstance(principal, Principal):
        deny("MISSING_PRINCIPAL")

    if not principal.subject or not principal.tenant_id:
        deny("INVALID_PRINCIPAL")

    # 2. Typed request validation.
    if not isinstance(call, ToolCall):
        deny("INVALID_TOOL_REQUEST")

    if (
        not isinstance(call.request_id, str)
        or not call.request_id.strip()
        or not isinstance(call.tool_name, str)
        or not call.tool_name.strip()
        or not isinstance(call.device_id, str)
        or not call.device_id.strip()
        or not isinstance(call.arguments, dict)
    ):
        deny("INVALID_TOOL_REQUEST")

    # 3. Application-owned tool policy.
    policy = POLICY.get(call.tool_name)

    if policy is None:
        deny("UNKNOWN_TOOL")

    # 4. Trusted device registry.
    resource_tenant = device_tenants.get(call.device_id)

    if not resource_tenant:
        deny("UNKNOWN_DEVICE")

    if resource_tenant != principal.tenant_id:
        deny("CROSS_TENANT_DEVICE")

    # 5. Capability authorization.
    if policy["capability"] not in principal.capabilities:
        deny("CAPABILITY_MISSING")

    # 6. Strict tool argument schemas.
    if call.tool_name in (
        "read_measurement",
        "reset_sensor_bus",
    ):
        if call.arguments:
            deny("INVALID_ARGUMENTS")

    elif call.tool_name == "run_diagnostic":
        if (
            set(call.arguments) != {"diagnostic"}
            or call.arguments.get("diagnostic")
            not in {
                "sensor_bus_status",
                "battery_status",
            }
        ):
            deny("INVALID_ARGUMENTS")

    # 7. Scoped approval verification.
    if policy["approval_required"]:
        approval = approvals.get(call.request_id)

        if not isinstance(approval, Approval):
            deny("APPROVAL_MISSING")

        digest = arguments_digest(call.arguments)

        if (
            not approval.approval_id
            or not approval.approver
            or approval.approver == principal.subject
            or approval.subject != principal.subject
            or approval.tenant_id != principal.tenant_id
            or approval.tool_name != call.tool_name
            or approval.device_id != call.device_id
            or approval.request_id != call.request_id
            or approval.expires_at <= now
            or approval.argument_digest != digest
        ):
            deny("APPROVAL_INVALID_OR_EXPIRED")

    # 8. Executor availability.
    executor = executors.get(call.tool_name)

    if executor is None or not callable(executor):
        deny("EXECUTOR_UNAVAILABLE")

    # 9. In-process state-changing replay control.
    if policy["state_changing"]:
        if call.request_id in seen_state_changes:
            deny("DUPLICATE_STATE_CHANGE")

    # 10. Audit admission before execution.
    # Failure to append prevents execution.
    record("ADMITTED", "POLICY_ACCEPTED")

    if policy["state_changing"]:
        seen_state_changes.add(call.request_id)

    # 11. Perform controlled execution.
    try:
        result = executor(
            device_id=call.device_id,
            arguments=dict(call.arguments),
        )
    except Exception as exc:
        record("FAILED", type(exc).__name__)
        raise ToolExecutionFailed(
            "TOOL_EXECUTION_FAILED"
        ) from exc

    # 12. Record the actual result.
    record("COMPLETED", "EXECUTOR_RETURNED")

    return result

