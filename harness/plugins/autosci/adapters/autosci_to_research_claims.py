"""Convert AutoSci raw claim data to `research_claims.v1` evidence."""

from __future__ import annotations

from typing import Any

from .common import evidence_base


def convert(raw: dict[str, Any], envelope: dict[str, Any] | None = None) -> dict[str, Any]:
    claims = []
    for idx, claim in enumerate(raw.get("claims") or [], start=1):
        claims.append({
            "claim_id": str(claim.get("claim_id") or claim.get("id") or f"claim-{idx:03d}"),
            "text": str(claim.get("text") or "Fixture claim"),
            "claim_type": str(claim.get("claim_type") or "result"),
            "source_anchor": str(claim.get("source_anchor") or "sample_paper.md#results"),
            "testability": str(claim.get("testability") or "testable"),
            "verification_status": "unverified",
            "evidence_ids": list(claim.get("evidence_ids") or ["paper:sample#results"]),
        })
    if not claims:
        claims.append({
            "claim_id": "claim-001",
            "text": "Fixture claim extracted from the sample paper.",
            "claim_type": "result",
            "source_anchor": "sample_paper.md#results",
            "testability": "testable",
            "verification_status": "unverified",
            "evidence_ids": ["paper:sample#results"],
        })
    return evidence_base("research_claims.v1", envelope, {"claims": claims})
