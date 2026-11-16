"""R07 M5 SQLite audit persistence research tests."""
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "labs/r07"))
from audit_store import AuditStore


def test_reopen_persists(tmp_path):
    path = tmp_path / "audit.sqlite"
    eid = AuditStore(path).append(request_id="r1", event_type="ADMITTED", payload={"tool": "read"})
    records = AuditStore(path).events("r1")
    assert len(records) == 1 and records[0]["event_id"] == eid


def test_ordering(tmp_path):
    db = AuditStore(tmp_path / "audit.sqlite")
    db.append(request_id="r1", event_type="ADMITTED", payload={})
    db.append(request_id="r1", event_type="COMPLETED", payload={"ok": True})
    assert [e["event_type"] for e in db.events("r1")] == ["ADMITTED", "COMPLETED"]


def test_request_isolation(tmp_path):
    db = AuditStore(tmp_path / "audit.sqlite")
    db.append(request_id="r1", event_type="DENIED", payload={})
    assert db.events("r2") == []


def test_invalid_payload(tmp_path):
    db = AuditStore(tmp_path / "audit.sqlite")
    with pytest.raises(TypeError):
        db.append(request_id="r1", event_type="ADMITTED", payload={"bad": object()})


def test_missing_request_id(tmp_path):
    db = AuditStore(tmp_path / "audit.sqlite")
    with pytest.raises(ValueError):
        db.append(request_id="", event_type="ADMITTED", payload={})
