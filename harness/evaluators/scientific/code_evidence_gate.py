#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evaluators.scientific.common import finish, has_any_evidence_ids, outputs, require_non_empty_list, run_cli, validate_schema

SCHEMA = "code_evidence_map.v1"


def evaluate(payload: dict[str, Any], path: str | Path | None = None):
    reasons, warnings = validate_schema(payload, SCHEMA)
    mappings = require_non_empty_list(outputs(payload).get("mappings"), "outputs.mappings", reasons)
    for index, mapping in enumerate(mappings):
        if not isinstance(mapping, dict):
            reasons.append(f"mappings[{index}] must be an object")
            continue
        require_non_empty_list(mapping.get("files"), f"mappings[{index}].files", reasons)
        if not has_any_evidence_ids(mapping.get("evidence_ids")):
            reasons.append(f"mappings[{index}].evidence_ids must contain at least one id")
    return finish(payload, reasons, warnings, path=path)


if __name__ == "__main__":
    raise SystemExit(run_cli(evaluate, SCHEMA))
