#!/usr/bin/env python3
"""Query the local Intelligence v2 SQLite store and print JSON."""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

from init_store import default_db_path


def rows_as_dicts(cursor: sqlite3.Cursor) -> list[dict]:
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=default_db_path())
    parser.add_argument("--domain")
    parser.add_argument("--subject")
    parser.add_argument("--predicate")
    parser.add_argument("--runs", action="store_true")
    parser.add_argument("--limit", type=int, default=50)
    args = parser.parse_args()

    if args.limit < 1 or args.limit > 1000:
        parser.error("--limit must be between 1 and 1000")
    if not args.db.exists():
        print(json.dumps({"error": "database_not_found", "path": str(args.db)}, ensure_ascii=False))
        return 1

    with sqlite3.connect(args.db) as connection:
        if args.runs:
            cursor = connection.execute(
                """
                SELECT run_id, domain, subject, data_as_of, completed_at,
                       validation_status, created_at
                FROM runs ORDER BY created_at DESC LIMIT ?
                """,
                (args.limit,),
            )
        else:
            clauses: list[str] = []
            params: list[object] = []
            if args.domain:
                clauses.append("domain = ?")
                params.append(args.domain)
            if args.subject:
                clauses.append("subject LIKE ?")
                params.append(f"%{args.subject}%")
            if args.predicate:
                clauses.append("predicate LIKE ?")
                params.append(f"%{args.predicate}%")
            where = " WHERE " + " AND ".join(clauses) if clauses else ""
            params.append(args.limit)
            cursor = connection.execute(
                """
                SELECT fact_id, run_id, domain, subject, predicate, value_json,
                       unit, as_of, confidence, review_status, scope,
                       source_ids_json, notes
                FROM facts
                """ + where + " ORDER BY as_of DESC, created_at DESC LIMIT ?",
                params,
            )
        result = rows_as_dicts(cursor)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

