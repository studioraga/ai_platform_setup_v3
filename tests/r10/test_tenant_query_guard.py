import importlib.util
from pathlib import Path

import pytest


MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "labs/r10/tenant_query_guard.py"
)

spec = importlib.util.spec_from_file_location(
    "r10_tenant_query_guard", MODULE_PATH
)

module = importlib.util.module_from_spec(spec)

import sys
sys.modules[spec.name] = module
spec.loader.exec_module(module)

TrustedIdentity = module.TrustedIdentity
query_for_tenant = module.query_for_tenant


def identity():
    return TrustedIdentity("principal-1", "tenant_a")


def test_filter_is_derived_from_trusted_identity():
    captured = {}

    def transport(collection, payload):
        captured["payload"] = payload
        return {
            "result": {
                "points": [
                    {"id": 101, "payload": {"tenant_id": "tenant_a"}}
                ]
            }
        }

    result = query_for_tenant(
        identity=identity(),
        query_vector=[1.0, 0.0],
        transport=transport,
        collection="synthetic",
    )

    assert len(result) == 1
    assert captured["payload"]["filter"]["must"][0][
        "match"
    ]["value"] == "tenant_a"


def test_cross_tenant_request_denied_before_execution():
    invoked = False

    def transport(*args):
        nonlocal invoked
        invoked = True
        return {}

    with pytest.raises(PermissionError):
        query_for_tenant(
            identity=identity(),
            requested_tenant="tenant_b",
            query_vector=[1.0, 0.0],
            transport=transport,
            collection="synthetic",
        )

    assert invoked is False


def test_missing_identity_denied():
    with pytest.raises(PermissionError):
        query_for_tenant(
            identity=TrustedIdentity("", ""),
            query_vector=[1.0, 0.0],
            transport=lambda *args: {},
            collection="synthetic",
        )


def test_cross_tenant_provider_response_denied():
    def transport(*args):
        return {
            "result": {
                "points": [
                    {"id": 201, "payload": {"tenant_id": "tenant_b"}}
                ]
            }
        }

    with pytest.raises(PermissionError):
        query_for_tenant(
            identity=identity(),
            query_vector=[1.0, 0.0],
            transport=transport,
            collection="synthetic",
        )
