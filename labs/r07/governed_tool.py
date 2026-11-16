"""R07 isolated deterministic tool authorization prototype, not a production agent."""
from dataclasses import dataclass

@dataclass(frozen=True)
class ToolRequest:
    tenant: str
    action: str
    approved: bool
    resource_tenant: str

class Denied(Exception):
    pass

def execute(request: ToolRequest, *, audit: list[dict]) -> str:
    allowed = (request.approved and request.tenant == request.resource_tenant
               and request.action == 'read_measurement')
    audit.append({'action': request.action, 'allowed': allowed,
                  'tenant_match': request.tenant == request.resource_tenant})
    if not allowed:
        raise Denied('action denied by deterministic application policy')
    return 'synthetic-measurement'
