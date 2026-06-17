"""Convert AutoSci experiment results to `experiment_result.v1` evidence."""

from __future__ import annotations

from typing import Any

from .common import evidence_base


def convert(raw: dict[str, Any], envelope: dict[str, Any] | None = None) -> dict[str, Any]:
    result = {
        "experiment_id": str(raw.get("experiment_id") or "exp-001"),
        "outcome": str(raw.get("outcome") or "supports"),
        "metrics": list(raw.get("metrics") or [{"name": "fixture_passed", "value": True}]),
        "evidence_ids": list(raw.get("evidence_ids") or ["evidence:autosci-fixture"]),
    }
    return evidence_base("experiment_result.v1", envelope, {"result": result})
