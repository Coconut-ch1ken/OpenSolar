#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evaluators.scientific.common import finish, has_any_evidence_ids, limitations, outputs, require_non_empty_list, run_cli, validate_schema

CANDIDATE_SCHEMA = "idea_candidate.v1"
EVALUATION_SCHEMA = "idea_evaluation.v1"


def evaluate(payload: dict[str, Any], path: str | Path | None = None):
    schema = str(payload.get("schema") or "")
    expected = EVALUATION_SCHEMA if schema == EVALUATION_SCHEMA else CANDIDATE_SCHEMA
    reasons, warnings = validate_schema(payload, expected)
    out = outputs(payload)
    if expected == CANDIDATE_SCHEMA:
        ideas = require_non_empty_list(out.get("ideas"), "outputs.ideas", reasons)
        for index, idea in enumerate(ideas):
            if not isinstance(idea, dict):
                reasons.append(f"ideas[{index}] must be an object")
                continue
            if not has_any_evidence_ids(idea.get("origin_evidence_ids")):
                reasons.append(f"ideas[{index}].origin_evidence_ids must contain at least one id")
    else:
        evaluations = require_non_empty_list(out.get("evaluations"), "outputs.evaluations", reasons)
        for index, evaluation in enumerate(evaluations):
            if not isinstance(evaluation, dict):
                reasons.append(f"evaluations[{index}] must be an object")
                continue
            if not has_any_evidence_ids(evaluation.get("evidence_ids")):
                reasons.append(f"evaluations[{index}].evidence_ids must contain at least one id")
            if evaluation.get("recommendation") in {"reject", "inconclusive"}:
                if not evaluation.get("risks") and not limitations(payload):
                    reasons.append(f"evaluations[{index}] reject/inconclusive recommendation requires risks or limitations")
    return finish(payload, reasons, warnings, path=path)


if __name__ == "__main__":
    raise SystemExit(run_cli(evaluate, CANDIDATE_SCHEMA))
