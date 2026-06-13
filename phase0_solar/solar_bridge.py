"""Bridge from Phase 0 claim-verification requests into Solar primitives.

This module is intentionally non-invasive. It uses local config fragments in
``phase0_solar/config`` and existing Solar loaders/routers, but it does not
write to ``harness/config`` or submit work to ``operator_runtime``.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .schemas import Phase0VerificationRequest, to_dict


CAPABILITY_ID = "cap.phase0-claim-verification"
LOGICAL_OPERATOR = "ResearchClaimVerifier"

PHASE0_DIR = Path(__file__).resolve().parent
REPO_ROOT = PHASE0_DIR.parent
DEFAULT_HARNESS_ROOT = REPO_ROOT / "harness"
LOCAL_CAPSULE_PATH = PHASE0_DIR / "config" / "capability-capsules" / "cap.phase0-claim-verification.yaml"
LOCAL_LOGICAL_OPERATORS_PATH = PHASE0_DIR / "config" / "logical-operators.fragment.json"


@dataclass(frozen=True)
class Phase0SolarPlan:
    request: Phase0VerificationRequest
    task_envelope: dict[str, Any]
    capsule_manifest_path: str
    capsule_validation_errors: tuple[str, ...]
    operator_candidates: tuple[str, ...]
    selected_actor: str | None
    rejected_actors: tuple[dict[str, str], ...]
    submission_ready: bool


def _ensure_harness_lib(harness_root: Path = DEFAULT_HARNESS_ROOT) -> None:
    lib_path = harness_root / "lib"
    if str(lib_path) not in sys.path:
        sys.path.insert(0, str(lib_path))


def build_task_envelope(
    request: Phase0VerificationRequest,
    *,
    artifact_refs: dict[str, str] | None = None,
) -> dict[str, Any]:
    return {
        "capability_native": True,
        "capability_capsule_id": CAPABILITY_ID,
        "logical_operator": LOGICAL_OPERATOR,
        "operator_id": LOGICAL_OPERATOR,
        "task_type": "verification",
        "objective": request.objective,
        "paper_source": request.paper_source,
        "repo_source": request.repo_source,
        "run_mode": request.run_mode,
        "human_gate_required": request.human_gate_required,
        "signals": ["paper", "claim", "verification", "benchmark", "evidence"],
        "source_metadata": dict(request.source_metadata),
        "artifact_refs": dict(artifact_refs or {}),
        "phase0_request": to_dict(request),
    }


def validate_local_capsule(
    *,
    harness_root: Path = DEFAULT_HARNESS_ROOT,
    capsule_path: Path = LOCAL_CAPSULE_PATH,
) -> tuple[dict[str, Any], tuple[str, ...]]:
    _ensure_harness_lib(harness_root)
    import capability_capsules as capsules

    manifest = capsules.load_capability_capsule_manifest(capsule_path)
    errors = tuple(
        capsules.validate_capability_capsule(
            manifest,
            schema_path=harness_root / "schemas" / "draft" / "capability-capsule.v1.draft.json",
        )
    )
    return manifest, errors


def route_local_operator(
    *,
    harness_root: Path = DEFAULT_HARNESS_ROOT,
    logical_operators_path: Path = LOCAL_LOGICAL_OPERATORS_PATH,
    unavailable: set[str] | None = None,
    quota_blocked: set[str] | None = None,
    risk_denied: set[str] | None = None,
) -> tuple[tuple[str, ...], str | None, tuple[dict[str, str], ...]]:
    _ensure_harness_lib(harness_root)
    from logical_operator_router import LogicalOperatorRouter

    router = LogicalOperatorRouter(
        bindings_path=logical_operators_path,
        actors_path=harness_root / "config" / "agent-actors.json",
    )
    candidates = tuple(actor_id for actor_id in router.get_candidates(LOGICAL_OPERATOR) if actor_id)
    selected, rejected = router.select_actor(
        LOGICAL_OPERATOR,
        unavailable=unavailable,
        quota_blocked=quota_blocked,
        risk_denied=risk_denied,
    )
    return candidates, selected, tuple(rejected)


def build_phase0_solar_plan(
    request: Phase0VerificationRequest,
    *,
    artifact_refs: dict[str, str] | None = None,
    harness_root: Path = DEFAULT_HARNESS_ROOT,
) -> Phase0SolarPlan:
    task_envelope = build_task_envelope(request, artifact_refs=artifact_refs)
    _, capsule_errors = validate_local_capsule(harness_root=harness_root)
    candidates, selected_actor, rejected = route_local_operator(harness_root=harness_root)
    return Phase0SolarPlan(
        request=request,
        task_envelope=task_envelope,
        capsule_manifest_path=str(LOCAL_CAPSULE_PATH),
        capsule_validation_errors=capsule_errors,
        operator_candidates=candidates,
        selected_actor=selected_actor,
        rejected_actors=rejected,
        submission_ready=not capsule_errors and selected_actor is not None,
    )
