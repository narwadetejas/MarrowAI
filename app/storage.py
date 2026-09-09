"""SQLite persistence for the MarrowAI local application state."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1


class Database:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self._migrate()

    def _migrate(self) -> None:
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS schema_meta "
            "(key TEXT PRIMARY KEY, value TEXT NOT NULL)"
        )
        current = self.connection.execute(
            "SELECT value FROM schema_meta WHERE key = 'schema_version'"
        ).fetchone()
        version = int(current[0]) if current else 0
        if version < 1:
            self.connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL CHECK (source IN ('text', 'voice', 'system')),
                    text TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id INTEGER NOT NULL REFERENCES requests(id),
                    plan_json TEXT NOT NULL,
                    risk_tier TEXT NOT NULL CHECK (risk_tier IN ('safe', 'moderate', 'destructive')),
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                INSERT OR REPLACE INTO schema_meta(key, value) VALUES ('schema_version', '1');
                """
            )
        self.connection.commit()

    def record_event(self, event_type: str, message: str) -> None:
        self.connection.execute(
            "INSERT INTO events(event_type, message) VALUES (?, ?)",
            (event_type, message),
        )
        self.connection.commit()

    def record_request(self, source: str, text: str) -> int:
        cursor = self.connection.execute(
            "INSERT INTO requests(source, text) VALUES (?, ?)", (source, text)
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def record_plan(
        self, request_id: int, plan_json: str, risk_tier: str, status: str
    ) -> int:
        cursor = self.connection.execute(
            "INSERT INTO plans(request_id, plan_json, risk_tier, status) VALUES (?, ?, ?, ?)",
            (request_id, plan_json, risk_tier, status),
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def close(self) -> None:
        self.connection.close()

    def __enter__(self) -> "Database":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()
