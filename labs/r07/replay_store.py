"""Single-node SQLite request-state research; not distributed exactly-once."""

import json
import math
import secrets
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path


class ReplayConflict(Exception):
    pass


@dataclass(frozen=True)
class Claim:
    status: str
    generation: int | None = None
    token: str | None = None
    result: object | None = None


class ReplayStore:
    def __init__(self, database: str | Path):
        self.path = str(database)
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS claims (
                    request_id TEXT PRIMARY KEY,
                    fingerprint TEXT NOT NULL,
                    state TEXT NOT NULL,
                    generation INTEGER NOT NULL,
                    token TEXT NOT NULL,
                    lease_until REAL NOT NULL,
                    result_json TEXT
                )
            """)

    def _connect(self):
        conn = sqlite3.connect(self.path, timeout=5)
        conn.execute("PRAGMA busy_timeout=5000")
        conn.execute("PRAGMA synchronous=FULL")
        return conn

    @staticmethod
    def _when(now):
        value = time.time() if now is None else now
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError("Invalid clock")
        return float(value)

    def claim(self, *, request_id, fingerprint, lease_seconds=30.0, now=None):
        if not isinstance(request_id, str) or not request_id.strip():
            raise ValueError("Request ID required")
        if not isinstance(fingerprint, str) or not fingerprint.strip():
            raise ValueError("Fingerprint required")
        if isinstance(lease_seconds, bool) or not isinstance(lease_seconds, (int, float)) or not math.isfinite(lease_seconds) or not 0 < lease_seconds <= 3600:
            raise ValueError("Invalid lease")
        instant = self._when(now)
        owner = secrets.token_hex(24)
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT fingerprint, state, generation, lease_until, result_json FROM claims WHERE request_id=?",
                (request_id,),
            ).fetchone()
            if row is not None:
                old_fp, state, generation, deadline, result_json = row
                if old_fp != fingerprint:
                    raise ReplayConflict("REQUEST_FINGERPRINT_CONFLICT")
                if state == "COMPLETED":
                    return Claim("COMPLETED", generation, result=json.loads(result_json))
                if state == "UNCERTAIN" or instant >= deadline:
                    conn.execute(
                        "UPDATE claims SET state='UNCERTAIN' WHERE request_id=? AND state='PROCESSING'",
                        (request_id,),
                    )
                    return Claim("OUTCOME_UNCERTAIN", generation)
                return Claim("ALREADY_PROCESSING", generation)
            conn.execute(
                "INSERT INTO claims (request_id, fingerprint, state, generation, token, lease_until) VALUES (?, ?, 'PROCESSING', 1, ?, ?)",
                (request_id, fingerprint, owner, instant + lease_seconds),
            )
        return Claim("NEW_CLAIM", generation=1, token=owner)

    def complete(self, *, request_id, generation, token, result, now=None):
        instant = self._when(now)
        payload = json.dumps(result, sort_keys=True, allow_nan=False)
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            changed = conn.execute(
                """UPDATE claims SET state='COMPLETED', result_json=?
                   WHERE request_id=? AND generation=? AND token=?
                   AND state='PROCESSING' AND lease_until>?""",
                (payload, request_id, generation, token, instant),
            ).rowcount
            if changed != 1:
                raise ReplayConflict("STALE_EXPIRED_OR_INVALID_COMPLETION")

    def mark_uncertain(self, *, request_id, generation, token):
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            changed = conn.execute(
                "UPDATE claims SET state='UNCERTAIN' WHERE request_id=? AND generation=? AND token=? AND state='PROCESSING'",
                (request_id, generation, token),
            ).rowcount
            if changed != 1:
                raise ReplayConflict("STALE_OR_INVALID_OWNER")
