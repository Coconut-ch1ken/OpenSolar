#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evaluators.scientific.common import finish, has_any_evidence_ids, outputs, run_cli, validate_schema

SCHEMA = "workflow_evolution.v1"


def evaluate(payload: dict[str, Any], path: str | Path | None = None):
    reasons, warnings = validate_schema(payload, SCHEMA)
    evolution = outputs(payload).get("evolution")
    if not isinstance(evolution, dict):
        reasons.append("outputs.evolution must be an object")
        return finish(payload, reasons, warnings, path=path)
    if not has_any_evidence_ids(evolution.get("evidence_ids")):
        reasons.append("outputs.evolution.evidence_ids must contain at least one id")
    if evolution.get("approval_state") in {"approved", "applied"} and not evolution.get("approval_ref"):
        reasons.append("approved or applied workflow evolution requires approval_ref")
    return finish(payload, reasons, warnings, path=path)


if __name__ == "__main__":
    raise SystemExit(run_cli(evaluate, SCHEMA))
