#!/usr/bin/env python3
"""Initialize the local Hermes Intelligence v2 SQLite store."""

from __future__ import annotations

import argparse
import os
import sqlite3
from pathlib import Path


def default_db_path() -> Path:
    data = os.environ.get("MALIANG_DATA_DIR")
    if data:
        return Path(os.path.expanduser(data)) / "intelligence-v2" / "intelligence.db"
    return Path.home() / ".maliang" / "intelligence-v2" / "intelligence.db"


SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS runs (
    run_id TEXT PRIMARY KEY,
    domain TEXT NOT NULL,
    subject TEXT NOT NULL,
    query TEXT NOT NULL,
    function_ids_json TEXT NOT NULL,
    requested_as_of TEXT,
    data_as_of TEXT NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT NOT NULL,
    validation_status TEXT NOT NULL,
    manifest_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sources (
    source_id TEXT PRIMARY KEY,
    source_type TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT,
    raw_ref TEXT,
    published_at TEXT,
    retrieved_at TEXT NOT NULL,
    evidence_level TEXT NOT NULL,
    source_scope TEXT NOT NULL,
    source_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS facts (
    fact_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES runs(run_id) ON DELETE CASCADE,
    domain TEXT NOT NULL,
    subject TEXT NOT NULL,
    predicate TEXT NOT NULL,
    value_json TEXT NOT NULL,
    unit TEXT,
    period_start TEXT,
    period_end TEXT,
    as_of TEXT NOT NULL,
    confidence REAL NOT NULL,
    review_status TEXT NOT NULL,
    scope TEXT NOT NULL,
    source_ids_json TEXT NOT NULL,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_facts_domain_subject ON facts(domain, subject);
CREATE INDEX IF NOT EXISTS idx_facts_predicate ON facts(predicate);
CREATE INDEX IF NOT EXISTS idx_facts_as_of ON facts(as_of);

CREATE TABLE IF NOT EXISTS inferences (
    inference_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES runs(run_id) ON DELETE CASCADE,
    domain TEXT NOT NULL,
    subject TEXT NOT NULL,
    conclusion TEXT NOT NULL,
    basis_ids_json TEXT NOT NULL,
    method TEXT NOT NULL,
    confidence REAL NOT NULL,
    assumptions_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS gaps (
    gap_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES runs(run_id) ON DELETE CASCADE,
    domain TEXT NOT NULL,
    field TEXT NOT NULL,
    reason TEXT NOT NULL,
    detail TEXT NOT NULL,
    next_action TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS entities (
    entity_id TEXT PRIMARY KEY,
    entity_type TEXT NOT NULL,
    canonical_name TEXT NOT NULL,
    attributes_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS entity_aliases (
    alias TEXT NOT NULL,
    entity_id TEXT NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
    alias_type TEXT NOT NULL DEFAULT 'name',
    PRIMARY KEY(alias, entity_id)
);

CREATE TABLE IF NOT EXISTS collections (
    collection_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    item_type TEXT NOT NULL,
    item_id TEXT NOT NULL,
    note TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS feedback (
    feedback_id TEXT PRIMARY KEY,
    item_type TEXT NOT NULL,
    item_id TEXT NOT NULL,
    status TEXT NOT NULL,
    comment TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def initialize(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as connection:
        connection.executescript(SCHEMA)
        connection.commit()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=default_db_path())
    args = parser.parse_args()
    initialize(args.db)
    print(f"READY: {args.db}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

