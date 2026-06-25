#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evaluators.scientific.common import finish, limitations, outputs, require_non_empty_string, run_cli, validate_schema

SCHEMA = "literature_discovery.v1"


def evaluate(payload: dict[str, Any], path: str | Path | None = None):
    reasons, warnings = validate_schema(payload, SCHEMA)
    out = outputs(payload)
    require_non_empty_string(out.get("query"), "outputs.query", reasons)
    candidates = out.get("candidates")
    if not isinstance(candidates, list):
        reasons.append("outputs.candidates must be an array")
        candidates = []
    mode = str(out.get("mode") or "unknown")
    limit = int(out.get("limit") or len(candidates) or 0)
    if limit <= 0:
        reasons.append("outputs.limit must be positive")
    if len(candidates) > limit:
        reasons.append(f"candidate count {len(candidates)} exceeds limit {limit}")

    evidence_status = str(payload.get("status") or "")
    if evidence_status == "completed" and not candidates:
        reasons.append("completed discovery must include at least one candidate")
    if evidence_status == "inconclusive":
        warnings.append("literature discovery is inconclusive; do not treat as a complete shortlist")
        if not limitations(payload):
            reasons.append("inconclusive discovery must explain limitations")
    if evidence_status == "failed":
        reasons.append("literature discovery evidence status is failed")

    for index, candidate in enumerate(candidates):
        if not isinstance(candidate, dict):
            reasons.append(f"candidates[{index}] must be an object")
            continue
        channels = candidate.get("source_channels")
        if not isinstance(channels, list) or not channels:
            reasons.append(f"candidates[{index}].source_channels must be non-empty")
            continue
        if mode != "fixture" and "local_fixture" in channels:
            reasons.append(f"candidates[{index}] uses local_fixture outside fixture mode")
        if not candidate.get("ranking_rationale"):
            reasons.append(f"candidates[{index}].ranking_rationale is required")

    if mode == "fixture":
        warnings.append("fixture discovery passed only as smoke evidence; it is not live literature discovery")
    return finish(payload, reasons, warnings, path=path)


if __name__ == "__main__":
    raise SystemExit(run_cli(evaluate, SCHEMA))
