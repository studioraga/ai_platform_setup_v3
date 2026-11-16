"""R07 M5 single-node SQLite audit persistence research; not tamper proof."""
import json
import sqlite3
import time
from pathlib import Path


class AuditStore:
    def __init__(self, database: str | Path):
        self.database = str(database)
        with self._connect() as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS audit_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    recorded_at REAL NOT NULL
                )
            """)

    def _connect(self):
        conn = sqlite3.connect(self.database, timeout=5)
        conn.execute("PRAGMA synchronous=FULL")
        conn.execute("PRAGMA busy_timeout=5000")
        return conn

    def append(self, *, request_id, event_type, payload):
        if not isinstance(request_id, str) or not request_id.strip():
            raise ValueError("Request ID required")
        if not isinstance(event_type, str) or not event_type.strip():
            raise ValueError("Event type required")
        if not isinstance(payload, dict):
            raise ValueError("Payload must be a dictionary")
        encoded = json.dumps(payload, sort_keys=True, allow_nan=False)
        with self._connect() as db:
            cursor = db.execute(
                "INSERT INTO audit_events (request_id, event_type, payload_json, recorded_at) VALUES (?, ?, ?, ?)",
                (request_id, event_type, encoded, time.time()),
            )
            return int(cursor.lastrowid)

    def events(self, request_id):
        with self._connect() as db:
            rows = db.execute(
                "SELECT event_id, event_type, payload_json, recorded_at FROM audit_events WHERE request_id=? ORDER BY event_id",
                (request_id,),
            ).fetchall()
        return [{
            "event_id": row[0], "event_type": row[1], "payload": json.loads(row[2]), "recorded_at": row[3]
        } for row in rows]
