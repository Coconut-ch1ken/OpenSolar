#!/usr/bin/env python3
"""Deterministic gate for metric_recomputation.v1 evidence."""
from __future__ import annotations

from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evaluators.scientific.common import (
    finish,
    has_any_evidence_ids,
    limitations,
    outputs,
    require_non_empty_list,
    run_cli,
    validate_schema,
)

SCHEMA = "metric_recomputation.v1"


def evaluate(payload: dict[str, Any], path: str | Path | None = None):
    reasons, warnings = validate_schema(payload, SCHEMA)
    recomputation = outputs(payload).get("recomputation")
    if not isinstance(recomputation, dict):
        reasons.append("outputs.recomputation must be an object")
        return finish(payload, reasons, warnings, path=path)
    metrics = require_non_empty_list(recomputation.get("metrics"), "outputs.recomputation.metrics", reasons)
    require_non_empty_list(recomputation.get("recomputed_from"), "outputs.recomputation.recomputed_from", reasons)
    if not has_any_evidence_ids(recomputation.get("evidence_ids")):
        reasons.append("outputs.recomputation.evidence_ids must contain at least one id")
    differs = [
        str(row.get("name"))
        for row in metrics
        if isinstance(row, dict) and row.get("agreement") in {"differs", "not_recomputable"}
    ]
    discrepancies = recomputation.get("discrepancies") if isinstance(recomputation.get("discrepancies"), list) else []
    if differs and not discrepancies and not limitations(payload):
        reasons.append(
            "metrics that differ or could not be recomputed must be explained in discrepancies or limitations: "
            + ", ".join(differs)
        )
    for row in metrics:
        if not isinstance(row, dict):
            continue
        if row.get("agreement") in {"matches", "within_tolerance"} and row.get("recomputed_value") is None:
            reasons.append(f"metric {row.get('name')!r} claims agreement without a recomputed_value")
    return finish(payload, reasons, warnings, path=path)


if __name__ == "__main__":
    raise SystemExit(run_cli(evaluate, SCHEMA))
