"""Phase 0 paper claim verification layer on top of Solar."""

from .comparator import compare_contract_to_observed, summarize_comparisons
from .schemas import (
    BenchmarkClaim,
    BenchmarkContract,
    ClaimComparison,
    HumanReviewDecision,
    ObservedMetric,
    Phase0EvidenceMap,
    Phase0RunManifest,
    Phase0VerificationRequest,
    Phase0VerificationSummary,
    SCHEMA_VERSION,
    to_dict,
)
from .solar_bridge import (
    CAPABILITY_ID,
    LOGICAL_OPERATOR,
    Phase0SolarPlan,
    build_phase0_solar_plan,
    build_task_envelope,
)

__all__ = [
    "BenchmarkClaim",
    "BenchmarkContract",
    "CAPABILITY_ID",
    "ClaimComparison",
    "HumanReviewDecision",
    "LOGICAL_OPERATOR",
    "ObservedMetric",
    "Phase0EvidenceMap",
    "Phase0RunManifest",
    "Phase0SolarPlan",
    "Phase0VerificationRequest",
    "Phase0VerificationSummary",
    "SCHEMA_VERSION",
    "build_phase0_solar_plan",
    "build_task_envelope",
    "compare_contract_to_observed",
    "summarize_comparisons",
    "to_dict",
]
