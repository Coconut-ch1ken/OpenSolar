#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evaluators.scientific.common import (
    check_artifact_paths,
    finish,
    has_any_evidence_ids,
    limitations,
    outputs,
    require_non_empty_list,
    run_cli,
    validate_schema,
)

SCHEMA = "claim_verdict.v1"
ALLOWED_VERDICTS = {"supported", "partially_supported", "not_supported", "inconclusive"}


def evaluate(payload: dict[str, Any], path: str | Path | None = None):
    reasons, warnings = validate_schema(payload, SCHEMA)
    verdicts = require_non_empty_list(outputs(payload).get("verdicts"), "outputs.verdicts", reasons)
    top_limitations = limitations(payload)
    for index, verdict in enumerate(verdicts):
        if not isinstance(verdict, dict):
            reasons.append(f"verdicts[{index}] must be an object")
            continue
        if verdict.get("verdict") not in ALLOWED_VERDICTS:
            reasons.append(f"verdicts[{index}].verdict is not allowed")
        if not has_any_evidence_ids(verdict.get("evidence_ids")):
            reasons.append(f"verdicts[{index}].evidence_ids must contain at least one id")
        confidence = verdict.get("confidence")
        if isinstance(confidence, (int, float)) and confidence < 0.8:
            if not verdict.get("limitations") and not top_limitations:
                reasons.append(f"verdicts[{index}] confidence below 0.8 requires limitations")
    check_artifact_paths(payload, path, reasons)
    return finish(payload, reasons, warnings, path=path)


if __name__ == "__main__":
    raise SystemExit(run_cli(evaluate, SCHEMA))
