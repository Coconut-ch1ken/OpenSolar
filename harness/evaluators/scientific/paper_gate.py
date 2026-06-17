#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evaluators.scientific.common import finish, outputs, require_non_empty_list, validate_schema, run_cli

SCHEMA = "research_paper.v1"


def evaluate(payload: dict[str, Any], path: str | Path | None = None):
    reasons, warnings = validate_schema(payload, SCHEMA)
    paper = outputs(payload).get("paper")
    if not isinstance(paper, dict):
        reasons.append("outputs.paper must be an object")
        return finish(payload, reasons, warnings, path=path)
    require_non_empty_list(paper.get("sections"), "outputs.paper.sections", reasons)
    if paper.get("parse_status") == "failed":
        reasons.append("paper parse_status is failed")
    if paper.get("parse_status") == "partial" and not payload.get("limitations"):
        reasons.append("partial paper parse requires limitations")
    return finish(payload, reasons, warnings, path=path)


if __name__ == "__main__":
    raise SystemExit(run_cli(evaluate, SCHEMA))
