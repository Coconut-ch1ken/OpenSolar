#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evaluators.scientific.common import GateResult, run_cli

SCHEMA = "scientific_lifecycle.v1"


def evaluate(payload: dict[str, Any], path: str | Path | None = None):
    reasons: list[str] = []
    warnings: list[str] = []
    nodes = payload.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        reasons.append("lifecycle graph must contain nodes")
        return _finish(reasons, warnings, path)
    ids = {str(node.get("id") or "") for node in nodes if isinstance(node, dict)}
    for index, node in enumerate(nodes):
        if not isinstance(node, dict):
            reasons.append(f"nodes[{index}] must be an object")
            continue
        node_id = str(node.get("id") or f"nodes[{index}]")
        if node.get("logical_operator") == "AutoSciRunner":
            reasons.append(f"{node_id} must not use AutoSciRunner")
        for field in ("logical_operator", "required_capabilities", "read_scope", "write_scope", "gate"):
            if not node.get(field):
                reasons.append(f"{node_id}.{field} is required")
        for dep in node.get("depends_on") or []:
            if dep not in ids:
                reasons.append(f"{node_id} depends on missing node {dep}")
        if node.get("logical_operator") in {"ScientificExperimentRunner", "ScientificExperimentMonitor"}:
            bounded = (node.get("execution_policy") or {}).get("mode") == "fixture_or_human_approved"
            if not bounded and not node.get("approval_gate"):
                reasons.append(f"{node_id} requires bounded execution mode or approval_gate")
    return _finish(reasons, warnings, path)


def _finish(reasons: list[str], warnings: list[str], path: str | Path | None):
    status = "failed" if reasons else "passed"
    return GateResult(
        ok=not reasons,
        status=status,
        reasons=reasons,
        warnings=warnings,
        schema=SCHEMA,
        path=str(path) if path else None,
        evidence_status="completed" if not reasons else "failed",
    )


if __name__ == "__main__":
    raise SystemExit(run_cli(evaluate, SCHEMA))
