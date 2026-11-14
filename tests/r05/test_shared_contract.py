"""Shared offline consumer contracts for Governance v0.29.0 and v0.30.0.

Only imports APIs available in both wheels. No cloud, network, or production actions.
"""
from __future__ import annotations

from dataclasses import asdict
from importlib import metadata
from pathlib import Path
import os

import pytest

from portable_ai_governance.kernel.authorization import (
    AuthorizationEngine, AuthorizationRule,
)
from portable_ai_governance.kernel.budgets import BudgetExceeded, RunBudget
from portable_ai_governance.kernel.replay_cache import PersistentNonceCache, ReplayDetected
from portable_ai_governance.kernel.request_signing import sign_request, verify_request
from portable_ai_governance.kernel.state_machine import WorkflowState
from portable_ai_governance.kernel.types import AgentResult, PolicyDecision, Principal


def test_installed_distribution_and_isolated_location():
    import portable_ai_governance as package

    expected = os.environ["GOV_EXPECTED_VERSION"]
    assert metadata.version("portable-agentic-ai-governance") == expected
    assert "site-packages" in Path(package.__file__).resolve().parts
    # Historical v0.29.0 deliberately records __version__ = 0.21.1;
    # do not treat that known historical discrepancy as a regression.


def test_workflow_transition_contract():
    state = WorkflowState()
    assert state.state == "START"
    with pytest.raises(ValueError, match="illegal transition"):
        state.transition("COMPLETE")
    state.transition("VALIDATE_REQUEST")
    assert state.state == "VALIDATE_REQUEST"


def test_budget_boundary_contract():
    budget = RunBudget(max_steps=1, max_tool_calls=1)
    budget.consume_step()
    budget.consume_tool_call()
    with pytest.raises(BudgetExceeded, match="step budget exceeded"):
        budget.consume_step()
    with pytest.raises(BudgetExceeded, match="tool-call budget exceeded"):
        budget.consume_tool_call()


def test_signed_request_integrity_and_rejection():
    secret = b"shared-contract-test-key-material-32bytes"
    request = sign_request(
        secret, method="POST", path="/v1/action", body=b'{"ok":true}',
        timestamp=1700000000, nonce="shared-contract-nonce",
    )
    assert verify_request(secret, request, method="POST", path="/v1/action", body=b'{"ok":true}', now=1700000000)
    assert not verify_request(secret, request, method="POST", path="/v1/action", body=b'{"ok":false}', now=1700000000)
    assert not verify_request(secret, request, method="POST", path="/v1/other", body=b'{"ok":true}', now=1700000000)
    assert not verify_request(secret, request, method="POST", path="/v1/action", body=b'{"ok":true}', now=1700000400)
    with pytest.raises(ValueError, match="at least 32 bytes"):
        sign_request(b"short", method="POST", path="/", body=b"x")


def test_replay_cache_persistence_and_fail_closed(tmp_path):
    path = tmp_path / "nonces.json"
    PersistentNonceCache(path).consume("nonce-A", now=100)
    with pytest.raises(ReplayDetected):
        PersistentNonceCache(path).consume("nonce-A", now=101)
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(RuntimeError, match="fail closed"):
        PersistentNonceCache(path).consume("nonce-B", now=102)


def test_authorization_default_deny_and_explicit_deny():
    principal = Principal("alice", ("reader",), {"tenant": "A"})
    rules = (
        AuthorizationRule("read", ("reader",), resource_prefix="/tenant/"),
        AuthorizationRule("read", ("reader",), resource_prefix="/tenant/private", effect="deny"),
    )
    engine = AuthorizationEngine(rules)
    assert engine.authorize(principal, action="write", resource="/tenant/A")[0] is False
    assert engine.authorize(principal, action="read", resource="/tenant/A")[0] is True
    decision, reason = engine.authorize(principal, action="read", resource="/tenant/private/data")
    assert decision is False
    assert reason == "explicit deny rule"


def test_result_schema_contract():
    result = AgentResult(run_id="r-1", agent_id="agent-1", status="COMPLETE")
    serialized = result.as_dict()
    assert serialized == asdict(result)
    assert serialized["run_id"] == "r-1"
    assert serialized["proposed_actions"] == ()
    assert serialized["evidence_refs"] == ()
    decision = PolicyDecision(False, "CONTROL-1", "denied", True)
    assert asdict(decision) == {
        "allowed": False, "control_id": "CONTROL-1",
        "reason": "denied", "approval_required": True,
    }
