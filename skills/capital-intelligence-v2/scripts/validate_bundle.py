#!/usr/bin/env python3
"""Validate a Hermes Intelligence Bundle v2 using only the Python stdlib."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


DOMAINS = {"demand", "policy", "capital", "industry", "competitive", "cross-domain"}
REVIEW_STATUSES = {"candidate", "verified", "rejected"}
SOURCE_SCOPES = {"internal_direct", "benchmark", "external_context", "public", "unknown"}
TOP_LEVEL = {
    "schema_version",
    "run_id",
    "domain",
    "request",
    "facts",
    "inferences",
    "gaps",
    "provenance",
    "run_manifest",
}


def _nonempty(value: Any) -> bool:
    return value is not None and value != "" and value != [] and value != {}


def _confidence(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and 0 <= value <= 1


def validate_bundle(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["bundle must be a JSON object"]

    missing = sorted(TOP_LEVEL - set(data))
    if missing:
        errors.append(f"missing top-level fields: {', '.join(missing)}")

    if data.get("schema_version") != "2.0":
        errors.append("schema_version must be '2.0'")
    if not _nonempty(data.get("run_id")):
        errors.append("run_id must be non-empty")
    if data.get("domain") not in DOMAINS:
        errors.append(f"domain must be one of {sorted(DOMAINS)}")

    request = data.get("request")
    if not isinstance(request, dict):
        errors.append("request must be an object")
    else:
        for field in ("query", "subject", "function_ids", "write_authorized"):
            if field not in request:
                errors.append(f"request.{field} is required")
        if "function_ids" in request and not isinstance(request["function_ids"], list):
            errors.append("request.function_ids must be an array")
        if "write_authorized" in request and not isinstance(request["write_authorized"], bool):
            errors.append("request.write_authorized must be boolean")

    provenance = data.get("provenance", [])
    if not isinstance(provenance, list):
        errors.append("provenance must be an array")
        provenance = []
    source_map: dict[str, dict[str, Any]] = {}
    for index, source in enumerate(provenance):
        prefix = f"provenance[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{prefix} must be an object")
            continue
        for field in ("source_id", "source_type", "title", "retrieved_at", "evidence_level", "source_scope"):
            if not _nonempty(source.get(field)):
                errors.append(f"{prefix}.{field} is required")
        source_id = source.get("source_id")
        if _nonempty(source_id):
            if source_id in source_map:
                errors.append(f"duplicate source_id: {source_id}")
            source_map[str(source_id)] = source
        if source.get("source_scope") not in SOURCE_SCOPES:
            errors.append(f"{prefix}.source_scope is invalid")
        url = str(source.get("url") or "").lower()
        if any(marker in url for marker in ("apikey=", "api_key=", "access_token=", "token=")):
            errors.append(f"{prefix}.url appears to contain a credential")

    facts = data.get("facts", [])
    if not isinstance(facts, list):
        errors.append("facts must be an array")
        facts = []
    fact_ids: set[str] = set()
    for index, fact in enumerate(facts):
        prefix = f"facts[{index}]"
        if not isinstance(fact, dict):
            errors.append(f"{prefix} must be an object")
            continue
        for field in ("fact_id", "subject", "predicate", "value", "as_of", "source_ids", "confidence", "review_status", "scope"):
            if not _nonempty(fact.get(field)) and field not in ("value", "confidence"):
                errors.append(f"{prefix}.{field} is required")
        fact_id = str(fact.get("fact_id") or "")
        if fact_id:
            if fact_id in fact_ids:
                errors.append(f"duplicate fact_id: {fact_id}")
            fact_ids.add(fact_id)
        if not _nonempty(fact.get("value")):
            errors.append(f"{prefix}.value must be non-empty; use gaps for missing data")
        source_ids = fact.get("source_ids")
        if not isinstance(source_ids, list) or not source_ids:
            errors.append(f"{prefix}.source_ids must be a non-empty array")
            source_ids = []
        missing_sources = [sid for sid in source_ids if sid not in source_map]
        if missing_sources:
            errors.append(f"{prefix}.source_ids missing from provenance: {missing_sources}")
        if not _confidence(fact.get("confidence")):
            errors.append(f"{prefix}.confidence must be between 0 and 1")
        if fact.get("review_status") not in REVIEW_STATUSES:
            errors.append(f"{prefix}.review_status is invalid")
        if fact.get("scope") not in SOURCE_SCOPES:
            errors.append(f"{prefix}.scope is invalid")
        if fact.get("review_status") == "verified" and source_ids:
            levels = {source_map.get(sid, {}).get("evidence_level") for sid in source_ids}
            if levels and levels <= {"search_snippet", None}:
                errors.append(f"{prefix} cannot be verified from search snippets only")

    inferences = data.get("inferences", [])
    if not isinstance(inferences, list):
        errors.append("inferences must be an array")
        inferences = []
    inference_ids: set[str] = set()
    valid_basis_ids = fact_ids | set(source_map)
    for index, inference in enumerate(inferences):
        prefix = f"inferences[{index}]"
        if not isinstance(inference, dict):
            errors.append(f"{prefix} must be an object")
            continue
        for field in ("inference_id", "subject", "conclusion", "basis_ids", "method", "confidence"):
            if not _nonempty(inference.get(field)) and field != "confidence":
                errors.append(f"{prefix}.{field} is required")
        inference_id = str(inference.get("inference_id") or "")
        if inference_id:
            if inference_id in inference_ids:
                errors.append(f"duplicate inference_id: {inference_id}")
            inference_ids.add(inference_id)
        basis_ids = inference.get("basis_ids")
        if not isinstance(basis_ids, list) or not basis_ids:
            errors.append(f"{prefix}.basis_ids must be a non-empty array")
        else:
            unknown = [basis for basis in basis_ids if basis not in valid_basis_ids]
            if unknown:
                errors.append(f"{prefix}.basis_ids are unknown: {unknown}")
        if not _confidence(inference.get("confidence")):
            errors.append(f"{prefix}.confidence must be between 0 and 1")

    gaps = data.get("gaps", [])
    if not isinstance(gaps, list):
        errors.append("gaps must be an array")
        gaps = []
    gap_ids: set[str] = set()
    for index, gap in enumerate(gaps):
        prefix = f"gaps[{index}]"
        if not isinstance(gap, dict):
            errors.append(f"{prefix} must be an object")
            continue
        for field in ("gap_id", "field", "reason", "detail", "next_action"):
            if not _nonempty(gap.get(field)):
                errors.append(f"{prefix}.{field} is required")
        gap_id = str(gap.get("gap_id") or "")
        if gap_id:
            if gap_id in gap_ids:
                errors.append(f"duplicate gap_id: {gap_id}")
            gap_ids.add(gap_id)

    manifest = data.get("run_manifest")
    if not isinstance(manifest, dict):
        errors.append("run_manifest must be an object")
    else:
        for field in (
            "started_at",
            "completed_at",
            "data_as_of",
            "used_tools",
            "unavailable_tools",
            "disabled_tools",
            "failed_calls",
            "validation_status",
        ):
            if field not in manifest:
                errors.append(f"run_manifest.{field} is required")
        for field in ("used_tools", "unavailable_tools", "disabled_tools", "failed_calls"):
            if field in manifest and not isinstance(manifest[field], list):
                errors.append(f"run_manifest.{field} must be an array")

    return errors


def load_bundle(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    try:
        data = load_bundle(args.bundle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 2

    errors = validate_bundle(data)
    if errors:
        print(f"INVALID: {len(errors)} error(s)", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    if not args.quiet:
        print(
            "VALID: "
            f"run={data['run_id']} domain={data['domain']} "
            f"facts={len(data['facts'])} inferences={len(data['inferences'])} "
            f"gaps={len(data['gaps'])} sources={len(data['provenance'])}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

