"""Reasoning capsules, synthesis routing, evidence-first claims and output contracts.

Every test builds its inputs inline from the shipped catalog; none depends on a
retained run.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
for value in (ROOT / "harness" / "lib", ROOT / "harness"):
    if str(value) not in sys.path:
        sys.path.insert(0, str(value))

import elastic_planner as planner  # noqa: E402
import evaluation_plan  # noqa: E402
import graph_node_dispatcher as dispatcher  # noqa: E402
from evaluators.scientific import metric_recomputation_gate  # noqa: E402

REPORT_PLAN = "schema:schemas/evidence/scientific_report_plan.v1.schema.json"
CLAIM_VERDICT = "schema:schemas/evidence/claim_verdict.v1.schema.json"
REPORT = "schema:schemas/evidence/scientific_report.v1.schema.json"
EXPERIMENT_RESULT = "schema:schemas/evidence/experiment_result.v1.schema.json"
METRICS = "schema:schemas/evidence/metric_recomputation.v1.schema.json"
CLAIMS = "schema:schemas/evidence/research_claims.v1.schema.json"
PAPER = "schema:schemas/evidence/research_paper.v1.schema.json"
REQUEST_CONTEXT = "artifact.request_context"


@pytest.fixture(scope="module")
def catalog() -> dict:
    return planner.build_planning_catalog_snapshot()


def _requirement_ir(check: str) -> dict:
    return {
        "schema_version": "solar.requirement_ir.v1",
        "requirement_ir_id": "requirement-ir-test",
        "intent_ir_ref": {},
        "intent_acceptance_ref": {},
        "requirements": [
            {
                "requirement_id": "R1",
                "statement": "Produce the requested outcome: a report with measured results.",
                "priority": "must",
                "check": check,
                "acceptance": {"kind": "artifact_fields", "required_values": ["answer"]},
                "checkable": True,
            }
        ],
        "scope": {},
        "assumptions": [],
        "conflict_scan": {},
        "approvals": [],
        "rollback": {},
    }


def _report_node(*, verifier_ids: list[str]) -> dict:
    return {
        "node_id": "report",
        "requirement_ids": ["R1"],
        "depends_on": [],
        "consumes": [REPORT_PLAN, CLAIM_VERDICT],
        "produces": [{"artifact_type": REPORT, "verifier_ids": verifier_ids}],
        # The registry renderer declares a network effect (its model service);
        # the node must allow it or the renderer is never a candidate at all.
        "operator_requirements": {"effects": ["read", "write", "execute"], "execution_trust": "any", "network": "optional"},
    }


def _terminals(row: dict) -> set[str]:
    candidates = {c["candidate_id"]: c for c in row["search"]["candidates"]}
    return {candidates[cid]["steps"][-1]["capsule_id"] for cid in row["admitted_candidate_ids"]}


def test_operator_reasoning_class_is_derived_fail_closed() -> None:
    assert planner._operator_reasoning_class({"backend": "research_operator_registry"}) == "deterministic"
    assert planner._operator_reasoning_class({"backend": "command"}) == "deterministic"
    assert planner._operator_reasoning_class({"backend": "command", "provider": "openai"}) == "model"
    assert planner._operator_reasoning_class({"backend": "claude-cli"}) == "model"
    assert planner._operator_reasoning_class({"backend": "command", "reasoning": "model"}) == "model"
    assert planner._capsule_reasoning_class("x", {}, [], {}) == "deterministic"
    assert planner._capsule_reasoning_class("x", {}, ["op"], {"op": {"provider": "anthropic"}}) == "model"
    with pytest.raises(planner.ElasticPlannerError):
        planner._capsule_reasoning_class("x", {"reasoning": "magic"}, [], {})


def test_every_capsule_carries_a_reasoning_class(catalog: dict) -> None:
    rows = {row["capsule_id"]: row for row in catalog["capsules"]}
    assert all(row["reasoning_class"] in planner.REASONING_CLASSES for row in rows.values())
    # Registry renderers are deterministic; generic model builders reason.
    assert rows["cap.scientific-report-draft"]["reasoning_class"] == "deterministic"
    assert rows["cap.research-claim-verify"]["reasoning_class"] == "deterministic"
    assert rows["cap.scientific-report-synthesize"]["reasoning_class"] == "model"


def test_reasoning_capsule_is_bound_to_selectable_model_builders(catalog: dict) -> None:
    rows = {row["capsule_id"]: row for row in catalog["capsules"]}
    row = rows["cap.scientific-report-synthesize"]
    assert row["status"] == "stable"
    assert row["operator_compatibility"]["selectable_preferred"]
    assert "autosci-report-worker" in row["operator_compatibility"]["forbidden"]
    assert row["produces"] == [REPORT]


def test_model_routed_operators_declare_model_reasoning() -> None:
    operators = json.loads((ROOT / "harness" / "config" / "physical-operators.json").read_text(encoding="utf-8"))["operators"]
    routed = [k for k, v in operators.items() if "fixed_research_node_adapter.py" in str(v.get("command") or "")]
    assert routed and all(operators[k].get("reasoning") == "model" for k in routed)
    assert planner._operator_reasoning_class(operators["autosci-report-worker"]) == "deterministic"


def test_synthesis_requirement_ids_follow_the_owned_checks() -> None:
    requirement_ir = _requirement_ir("check.information_outcome_completeness.v1")
    assert planner.synthesis_requirement_ids(requirement_ir, ["R1"]) == ["R1"]
    assert planner.synthesis_requirement_ids(requirement_ir, ["R9"]) == []
    assert planner.synthesis_requirement_ids(_requirement_ir("check.intent_constraint_coverage.v1"), ["R1"]) == []
    assert planner.synthesis_requirement_ids(None, ["R1"]) == []


def test_synthesis_requirement_admits_only_reasoning_terminals(catalog: dict) -> None:
    row = planner._node_composition_row(
        _report_node(verifier_ids=["check.scientific.scientific_report.v1", "check.information_outcome_completeness.v1"]),
        catalog,
        requirement_ir=_requirement_ir("check.information_outcome_completeness.v1"),
    )
    assert row["synthesis_requirement_ids"] == ["R1"]
    assert row["status"] == "candidates_available", row["candidate_exclusions"][:3]
    assert _terminals(row) == {"cap.scientific-report-synthesize"}
    excluded = {
        reason for item in row["candidate_exclusions"] for reason in item["reason_codes"]
    }
    assert "TARGET_PRODUCER_CANNOT_SYNTHESIZE" in excluded


def test_without_synthesis_requirements_renderers_stay_admissible(catalog: dict) -> None:
    row = planner._node_composition_row(
        _report_node(verifier_ids=["check.scientific.scientific_report.v1"]),
        catalog,
        requirement_ir=_requirement_ir("check.intent_constraint_coverage.v1"),
    )
    assert row["synthesis_requirement_ids"] == []
    assert "cap.scientific-report-draft" in _terminals(row)
    assert not any(
        "TARGET_PRODUCER_CANNOT_SYNTHESIZE" in item["reason_codes"] for item in row["candidate_exclusions"]
    )


def test_synthesis_rule_applies_to_answering_output_not_intermediate_verdict(catalog: dict) -> None:
    node = {
        "node_id": "verify_and_report",
        "requirement_ids": ["R1"],
        "depends_on": [],
        "consumes": [EXPERIMENT_RESULT, METRICS, REPORT_PLAN],
        "produces": [
            {"artifact_type": CLAIM_VERDICT, "verifier_ids": ["check.scientific.claim_verdict.v1"]},
            {"artifact_type": REPORT, "verifier_ids": ["check.scientific.scientific_report.v1", "check.artifact_outcome_completeness.v1"]},
        ],
        "operator_requirements": {"effects": ["read", "write", "execute"], "execution_trust": "evidence_transform", "network": "forbidden"},
    }
    row = planner._node_composition_row(node, catalog, requirement_ir=_requirement_ir("check.artifact_outcome_completeness.v1"))
    assert row["synthesis_requirement_ids"] == ["R1"]
    assert row["status"] == "candidates_available", row["candidate_exclusions"][:3]
    assert _terminals(row) == {"cap.scientific-report-synthesize"}


def test_ab_primitives_are_registered_and_typed(catalog: dict) -> None:
    rows = {row["capsule_id"]: row for row in catalog["capsules"]}
    hyp = rows["cap.research-hypothesis-formulate"]
    assert hyp["reasoning_class"] == "model" and hyp["status"] == "stable"
    assert hyp["produces"] == [CLAIMS]
    verify = rows["cap.research-claim-verify-experimental"]
    assert verify["reasoning_class"] == "deterministic"
    assert METRICS in verify["consumes"]
    recompute = rows["cap.research-metric-recompute"]
    assert recompute["reasoning_class"] == "model" and recompute["produces"] == [METRICS]
    deliver = rows["cap.scientific-report-deliver"]
    assert deliver["produces"] == ["artifact.report"] and deliver["reasoning_class"] == "model"


def test_claims_come_from_evidence_when_the_node_holds_any(catalog: dict) -> None:
    def _claims_node(consumes: list[str], effects: list[str]) -> dict:
        return {
            "node_id": "claims",
            "requirement_ids": [],
            "depends_on": [],
            "consumes": consumes,
            "produces": [{"artifact_type": CLAIMS, "verifier_ids": ["check.scientific.research_claims.v1"]}],
            "operator_requirements": {"effects": effects, "execution_trust": "any", "network": "forbidden"},
        }

    def _admitted_capsules(row: dict) -> set[str]:
        candidates = {c["candidate_id"]: c for c in row["search"]["candidates"]}
        return {step["capsule_id"] for cid in row["admitted_candidate_ids"] for step in candidates[cid]["steps"]}

    no_evidence = planner._node_composition_row(_claims_node([REQUEST_CONTEXT], ["read", "write"]), catalog)
    assert "cap.research-hypothesis-formulate" in _admitted_capsules(no_evidence)

    with_paper = planner._node_composition_row(_claims_node([REQUEST_CONTEXT, PAPER], ["read", "write", "execute"]), catalog)
    assert "cap.research-hypothesis-formulate" not in _admitted_capsules(with_paper)
    reasons = {reason for item in with_paper["candidate_exclusions"] for reason in item["reason_codes"]}
    assert reasons & {"HYPOTHESIS_SHORTCUT_WITH_EVIDENCE_PRESENT", "HYPOTHESIS_SHORTCUT_EVIDENCE_PATH_AVAILABLE"}


def _envelope(schema: str, outputs: dict, limitations: list[str] | None = None) -> dict:
    return {
        "schema": schema,
        "task_id": "t1",
        "sprint_id": "s1",
        "node_id": "n1",
        "status": "completed",
        "inputs": {},
        "outputs": outputs,
        "artifacts": [{"type": "json", "path": "out.json"}],
        "provenance": {"operator_id": "op", "implementation_package": "pkg", "timestamp": "2026-01-01T00:00:00Z"},
        "limitations": limitations or [],
    }


def test_metric_recomputation_gate_requires_discrepancies_to_be_explained() -> None:
    base = {
        "experiment_id": "exp-1",
        "recomputed_from": [{"artifact_path": "artifacts/result.json", "sha256": "a" * 64}],
        "metrics": [{"name": "accuracy", "reported_value": 0.91, "recomputed_value": 0.88, "agreement": "differs"}],
        "evidence_ids": ["exp-1"],
    }
    silent = metric_recomputation_gate.evaluate(_envelope("metric_recomputation.v1", {"recomputation": base}))
    assert silent.status == "failed"
    assert any("explained" in r for r in silent.reasons)
    explained = _envelope("metric_recomputation.v1", {"recomputation": {**base, "discrepancies": ["seed mismatch"]}})
    assert metric_recomputation_gate.evaluate(explained).status == "passed"
    fake = _envelope(
        "metric_recomputation.v1",
        {"recomputation": {**base, "metrics": [{"name": "f1", "reported_value": 0.5, "recomputed_value": None, "agreement": "matches"}]}},
    )
    result = metric_recomputation_gate.evaluate(fake)
    assert result.status == "failed"
    assert any("without a recomputed_value" in r for r in result.reasons)


def test_new_evidence_types_have_auto_applied_deterministic_checks() -> None:
    registry = evaluation_plan.load_evaluation_check_registry()
    by_id = {row["check_id"]: row for row in registry["checks"]}
    for name in ("dataset_manifest", "metric_recomputation"):
        row = by_id[f"check.scientific.{name}.v1"]
        assert row["applies_to"]["auto_apply"] is True
        assert row["deterministic"]["implementation_ref"].endswith(f"{name}_gate:evaluate")


def test_worker_instruction_states_output_contract_for_schema_artifacts() -> None:
    node = {
        "id": "synthesize",
        "semantic_artifact_contract": {
            "produces": [
                {
                    "artifact_type": REPORT,
                    "materialization": {"kind": "file", "path": "scientific_report.v1.json", "route": "sprint_private"},
                    "verifier_ids": ["check.scientific.scientific_report.v1"],
                }
            ]
        },
    }
    block = dispatcher._output_contracts_block(node)
    assert "## Output Contracts" in block
    assert "schemas/evidence/scientific_report.v1.schema.json" in block
    assert "check.scientific.scientific_report.v1" in block
    assert "scientific_report.v1.json" in block
    assert dispatcher._output_contracts_block({"id": "x"}) == ""


def test_review_method_reflects_model_identity() -> None:
    class Model:
        provider = "codex"
        model = ""

    same = Model()
    assert planner._review_method(same) == "same_model_second_pass"
    assert planner._reviewer_record(same) == {"provider": "codex", "model": "configured_default", "independence": "unknown"}
    distinct = Model()
    distinct.independence = "distinct_model"
    assert planner._review_method(distinct) == "independent_model_call"
    assert planner._reviewer_record(distinct)["independence"] == "distinct_model"
