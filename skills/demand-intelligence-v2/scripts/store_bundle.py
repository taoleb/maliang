#!/usr/bin/env python3
"""Validate and upsert one Intelligence Bundle v2 into SQLite."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

from init_store import default_db_path, initialize
from validate_bundle import load_bundle, validate_bundle


def compact(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def store(data: dict, db_path: Path) -> None:
    initialize(db_path)
    request = data["request"]
    manifest = data["run_manifest"]
    with sqlite3.connect(db_path) as connection:
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute(
            """
            INSERT OR REPLACE INTO runs (
                run_id, domain, subject, query, function_ids_json,
                requested_as_of, data_as_of, started_at, completed_at,
                validation_status, manifest_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["run_id"],
                data["domain"],
                request["subject"],
                request["query"],
                compact(request["function_ids"]),
                request.get("requested_as_of"),
                manifest["data_as_of"],
                manifest["started_at"],
                manifest["completed_at"],
                "valid",
                compact(manifest),
            ),
        )

        for source in data["provenance"]:
            connection.execute(
                """
                INSERT OR REPLACE INTO sources (
                    source_id, source_type, title, url, raw_ref, published_at,
                    retrieved_at, evidence_level, source_scope, source_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    source["source_id"],
                    source["source_type"],
                    source["title"],
                    source.get("url"),
                    source.get("raw_ref"),
                    source.get("published_at"),
                    source["retrieved_at"],
                    source["evidence_level"],
                    source["source_scope"],
                    compact(source),
                ),
            )

        for fact in data["facts"]:
            connection.execute(
                """
                INSERT OR REPLACE INTO facts (
                    fact_id, run_id, domain, subject, predicate, value_json,
                    unit, period_start, period_end, as_of, confidence,
                    review_status, scope, source_ids_json, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    fact["fact_id"],
                    data["run_id"],
                    data["domain"],
                    fact["subject"],
                    fact["predicate"],
                    compact(fact["value"]),
                    fact.get("unit"),
                    fact.get("period_start"),
                    fact.get("period_end"),
                    fact["as_of"],
                    fact["confidence"],
                    fact["review_status"],
                    fact["scope"],
                    compact(fact["source_ids"]),
                    fact.get("notes"),
                ),
            )

        for inference in data["inferences"]:
            connection.execute(
                """
                INSERT OR REPLACE INTO inferences (
                    inference_id, run_id, domain, subject, conclusion,
                    basis_ids_json, method, confidence, assumptions_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    inference["inference_id"],
                    data["run_id"],
                    data["domain"],
                    inference["subject"],
                    inference["conclusion"],
                    compact(inference["basis_ids"]),
                    inference["method"],
                    inference["confidence"],
                    compact(inference.get("assumptions", [])),
                ),
            )

        for gap in data["gaps"]:
            connection.execute(
                """
                INSERT OR REPLACE INTO gaps (
                    gap_id, run_id, domain, field, reason, detail, next_action
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    gap["gap_id"],
                    data["run_id"],
                    data["domain"],
                    gap["field"],
                    gap["reason"],
                    gap["detail"],
                    gap["next_action"],
                ),
            )
        connection.commit()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--db", type=Path, default=default_db_path())
    args = parser.parse_args()

    try:
        data = load_bundle(args.bundle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"STORE FAILED: {exc}", file=sys.stderr)
        return 2

    errors = validate_bundle(data)
    if errors:
        print("STORE REFUSED: bundle is invalid", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    store(data, args.db)
    print(
        f"STORED: run={data['run_id']} facts={len(data['facts'])} "
        f"inferences={len(data['inferences'])} gaps={len(data['gaps'])} db={args.db}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

