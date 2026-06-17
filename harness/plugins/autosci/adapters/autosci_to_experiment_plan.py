"""Convert AutoSci experiment designs to `experiment_plan.v1` evidence."""

from __future__ import annotations

from typing import Any

from .common import evidence_base


def convert(raw: dict[str, Any], envelope: dict[str, Any] | None = None) -> dict[str, Any]:
    plan = {
        "experiment_id": str(raw.get("experiment_id") or "exp-001"),
        "objective": str(raw.get("objective") or "Validate the AutoSci adapter fixture path."),
        "hypothesis": str(raw.get("hypothesis") or "Fixture conversion produces valid Solar Evidence ABI output."),
        "variables": list(raw.get("variables") or ["adapter_action", "fixture_payload"]),
        "metrics": list(raw.get("metrics") or ["schema_present", "status_completed"]),
        "procedure": list(raw.get("procedure") or [
            "Run the bridge in fixture mode",
            "Write result.json and evidence.jsonl",
            "Validate required evidence fields",
        ]),
        "approval_required": bool(raw.get("approval_required", False)),
        "expected_artifacts": list(raw.get("expected_artifacts") or ["result.json", "evidence.jsonl"]),
    }
    return evidence_base("experiment_plan.v1", envelope, {"experiment_plan": plan})
