"""Convert AutoSci verdict-like data to `claim_verdict.v1` evidence."""

from __future__ import annotations

from typing import Any

from .common import evidence_base


OUTCOME_TO_VERDICT = {
    "supports": "supported",
    "partially_supports": "partially_supported",
    "refutes": "not_supported",
    "inconclusive": "inconclusive",
    "failed": "inconclusive",
}


def convert(raw: dict[str, Any], envelope: dict[str, Any] | None = None) -> dict[str, Any]:
    verdict = {
        "claim_id": str(raw.get("claim_id") or "claim-001"),
        "verdict": str(raw.get("verdict") or OUTCOME_TO_VERDICT.get(str(raw.get("outcome") or "supports"), "inconclusive")),
        "confidence": float(raw.get("confidence", 0.8)),
        "basis": str(raw.get("basis") or "Fixture experiment result is linked for adapter smoke validation."),
        "evidence_ids": list(raw.get("evidence_ids") or ["evidence:autosci-fixture"]),
        "limitations": list(raw.get("limitations") or ["fixture-mode verdict; not a real scientific claim verification"]),
    }
    return evidence_base("claim_verdict.v1", envelope, {"verdicts": [verdict]}, limitations=verdict["limitations"])
