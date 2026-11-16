"""R10 research-only Qdrant tenant authorization boundary."""

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class TrustedIdentity:
    principal_id: str
    tenant_id: str


def query_for_tenant(
    *,
    identity: TrustedIdentity,
    query_vector: list[float],
    transport: Callable,
    collection: str,
    requested_tenant: str | None = None,
):
    if not identity.principal_id or not identity.tenant_id:
        raise PermissionError("Trusted identity required")

    if requested_tenant is not None:
        if requested_tenant != identity.tenant_id:
            raise PermissionError("Cross-tenant request denied")

    if len(query_vector) != 2:
        raise ValueError("Expected two-dimensional vector")

    payload = {
        "query": query_vector,
        "filter": {
            "must": [
                {
                    "key": "tenant_id",
                    "match": {"value": identity.tenant_id},
                }
            ]
        },
        "limit": 4,
        "with_payload": True,
    }

    response = transport(collection, payload)

    points = response["result"]["points"]

    # Defense in depth: validate the provider response.
    for point in points:
        tenant = point.get("payload", {}).get("tenant_id")

        if tenant != identity.tenant_id:
            raise PermissionError(
                "Provider returned a cross-tenant result"
            )

    return points
