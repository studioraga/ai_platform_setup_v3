"""R07 M3 single-node recoverable-state research tests."""
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "labs/r07"))
from replay_store import ReplayStore, ReplayConflict


def test_first_and_duplicate(tmp_path):
    store = ReplayStore(tmp_path / "r.sqlite")
    claim = store.claim(request_id="r1", fingerprint="f1", now=100)
    assert claim.status == "NEW_CLAIM" and claim.token
    assert store.claim(request_id="r1", fingerprint="f1", now=101).status == "ALREADY_PROCESSING"


def test_changed_fingerprint_denied(tmp_path):
    store = ReplayStore(tmp_path / "r.sqlite")
    store.claim(request_id="r1", fingerprint="f1", now=100)
    with pytest.raises(ReplayConflict, match="REQUEST_FINGERPRINT_CONFLICT"):
        store.claim(request_id="r1", fingerprint="f2", now=101)


def test_persistent_completion(tmp_path):
    path = tmp_path / "r.sqlite"
    store = ReplayStore(path)
    claim = store.claim(request_id="r1", fingerprint="f1", now=100)
    store.complete(request_id="r1", generation=claim.generation, token=claim.token, result={"ok": True}, now=101)
    seen = ReplayStore(path).claim(request_id="r1", fingerprint="f1", now=900)
    assert seen.status == "COMPLETED" and seen.result == {"ok": True}


def test_wrong_owner_denied(tmp_path):
    store = ReplayStore(tmp_path / "r.sqlite")
    claim = store.claim(request_id="r1", fingerprint="f1", now=100)
    with pytest.raises(ReplayConflict):
        store.complete(request_id="r1", generation=claim.generation, token="attacker", result={"ok": True}, now=101)


def test_expiration_stays_uncertain(tmp_path):
    store = ReplayStore(tmp_path / "r.sqlite")
    store.claim(request_id="r1", fingerprint="f1", now=100, lease_seconds=10)
    assert store.claim(request_id="r1", fingerprint="f1", now=111).status == "OUTCOME_UNCERTAIN"
    assert store.claim(request_id="r1", fingerprint="f1", now=112).status == "OUTCOME_UNCERTAIN"


def test_expired_owner_cannot_complete(tmp_path):
    store = ReplayStore(tmp_path / "r.sqlite")
    claim = store.claim(request_id="r1", fingerprint="f1", now=100, lease_seconds=10)
    with pytest.raises(ReplayConflict, match="STALE_EXPIRED_OR_INVALID_COMPLETION"):
        store.complete(request_id="r1", generation=claim.generation, token=claim.token, result={}, now=111)


def test_explicit_uncertain(tmp_path):
    store = ReplayStore(tmp_path / "r.sqlite")
    claim = store.claim(request_id="r1", fingerprint="f1", now=100)
    store.mark_uncertain(request_id="r1", generation=claim.generation, token=claim.token)
    assert store.claim(request_id="r1", fingerprint="f1", now=101).status == "OUTCOME_UNCERTAIN"


def test_rejects_invalid_clock(tmp_path):
    store = ReplayStore(tmp_path / "r.sqlite")
    with pytest.raises(ValueError):
        store.claim(request_id="r1", fingerprint="f1", now=float("nan"))
