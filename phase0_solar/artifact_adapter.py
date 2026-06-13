"""Adapters from existing Phase 0 artifacts into Solar overlay report inputs."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class NormalizedClaimRow:
    claim_id: str
    claim_type: str
    verification_mode: str
    claim_verdict_status: str
    execution_readiness_status: str
    broad_readiness_status: str
    validation_evidence: tuple[str, ...]
    planning_evidence: tuple[str, ...]
    blockers: tuple[str, ...]
    next_step: str


@dataclass(frozen=True)
class Phase0ArtifactReportBundle:
    source_matrix_path: str
    schema_version: str
    scope: str
    claims: tuple[NormalizedClaimRow, ...]
    claim_status_counts: dict[str, int]
    execution_readiness_summary: dict[str, int]
    detailed_readiness_counts: dict[str, int]
    paper_level_status: str
    full_paper_claim_status: str
    executable_target_count: int
    official_support_keys: tuple[str, ...]


def _as_tuple(value: Any) -> tuple[str, ...]:
    if not value:
        return ()
    if isinstance(value, list):
        return tuple(str(item) for item in value)
    return (str(value),)


def _broad_readiness(status: str) -> str:
    lowered = str(status or "").lower()
    if lowered in {"ready", "partially_ready", "not_ready", "blocked", "unknown"}:
        return lowered
    if lowered.startswith("ready_for_"):
        return "ready"
    if lowered.startswith("partially_ready"):
        return "partially_ready"
    if "blocked" in lowered:
        return "blocked"
    if "ready" in lowered:
        return "partially_ready"
    return "unknown"


def _paper_status_from_counts(counts: dict[str, int]) -> str:
    if counts.get("not_reproduced", 0) > 0:
        return "not_reproduced"
    if counts.get("blocked", 0) > 0:
        return "blocked"
    if counts.get("partially_reproduced", 0) > 0:
        return "partially_reproduced"
    if counts.get("not_testable", 0) > 0:
        return "not_testable"
    return "reproduced"


def load_phase0_matrix(path: str | Path) -> Phase0ArtifactReportBundle:
    matrix_path = Path(path)
    payload = json.loads(matrix_path.read_text(encoding="utf-8"))
    raw_claims = payload.get("claims", [])
    if not isinstance(raw_claims, list):
        raise ValueError("Phase 0 matrix must contain a claims list")

    rows: list[NormalizedClaimRow] = []
    for item in raw_claims:
        if not isinstance(item, dict):
            raise ValueError("Phase 0 matrix claims must be objects")
        readiness = str(item.get("execution_readiness_status") or "unknown")
        rows.append(
            NormalizedClaimRow(
                claim_id=str(item.get("claim_id") or ""),
                claim_type=str(item.get("claim_type") or "unknown"),
                verification_mode=str(item.get("verification_mode") or "unknown"),
                claim_verdict_status=str(item.get("claim_verdict_status") or item.get("status") or "blocked"),
                execution_readiness_status=readiness,
                broad_readiness_status=_broad_readiness(readiness),
                validation_evidence=_as_tuple(item.get("validation_evidence") or item.get("evidence")),
                planning_evidence=_as_tuple(item.get("planning_evidence")),
                blockers=_as_tuple(item.get("blockers")),
                next_step=str(item.get("next_step") or ""),
            )
        )

    claim_counts = dict(Counter(row.claim_verdict_status for row in rows))
    broad_readiness_counts = dict(Counter(row.broad_readiness_status for row in rows))
    detailed_readiness_counts = dict(Counter(row.execution_readiness_status for row in rows))
    paper_status = _paper_status_from_counts(claim_counts)

    return Phase0ArtifactReportBundle(
        source_matrix_path=str(matrix_path),
        schema_version=str(payload.get("schema_version") or "unknown"),
        scope=str(payload.get("scope") or ""),
        claims=tuple(rows),
        claim_status_counts=claim_counts,
        execution_readiness_summary=broad_readiness_counts,
        detailed_readiness_counts=detailed_readiness_counts,
        paper_level_status=paper_status,
        full_paper_claim_status="blocked" if claim_counts.get("blocked", 0) > 0 else paper_status,
        executable_target_count=len(payload.get("executable_targets") or []),
        official_support_keys=tuple(sorted((payload.get("official_support") or {}).keys())),
    )
