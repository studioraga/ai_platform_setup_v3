import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tenant_query_guard import TrustedIdentity, query_for_tenant


base_url = os.environ["QDRANT_URL"]
collection = os.environ["QDRANT_COLLECTION"]


def transport(name, payload):
    url = f"{base_url}/collections/{name}/points/query"

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=10) as response:
        return json.load(response)


principal = TrustedIdentity("synthetic-principal", "tenant_a")

points = query_for_tenant(
    identity=principal,
    query_vector=[1.0, 0.0],
    transport=transport,
    collection=collection,
)

assert {p["id"] for p in points} == {101, 102}

try:
    query_for_tenant(
        identity=principal,
        requested_tenant="tenant_b",
        query_vector=[1.0, 0.0],
        transport=transport,
        collection=collection,
    )
except PermissionError:
    print("PASS: Cross-tenant request rejected")
else:
    raise AssertionError("Cross-tenant request was accepted")

print("PASS: Live tenant-scoped retrieval")
