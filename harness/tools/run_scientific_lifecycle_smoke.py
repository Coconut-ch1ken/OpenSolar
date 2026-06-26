#!/usr/bin/env python3
"""Run a small scheduler-dispatched scientific lifecycle smoke."""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_HARNESS_DIR = Path(__file__).resolve().parents[1]
if str(REPO_HARNESS_DIR / "tools") not in sys.path:
    sys.path.insert(0, str(REPO_HARNESS_DIR / "tools"))

import run_scientific_node_smoke as node_smoke  # noqa: E402


DEFAULT_PAPER = "plugins/autosci/tests/fixtures/sample_paper.md"
DEFAULT_WORKFLOW_ID = "scientific_research_lifecycle_full_v1"
NODE_SPECS = [
    {
        "node_id": "literature_discover",
        "logical_operator": "ScientificLiteratureDiscoverer",
        "operator_id": "autosci-literature-discover-worker",
        "action": "discover_literature",
        "gate": "G_LITERATURE_DISCOVER",
        "evidence_name": "literature_discovery.json",
    },
    {
        "node_id": "paper_ingest",
        "logical_operator": "ScientificPaperIngestor",
        "operator_id": "autosci-paper-ingest-worker",
        "action": "ingest_paper",
        "gate": "G_PAPER_INGEST",
        "evidence_name": "research_paper.json",
    },
    {
        "node_id": "paper_analyze",
        "logical_operator": "ScientificPaperAnalyzer",
        "operator_id": "autosci-paper-analyze-worker",
        "action": "analyze_paper",
        "gate": "G_PAPER_ANALYZE",
        "evidence_name": "research_paper_analysis.json",
    },
    {
        "node_id": "memory_update_initial",
        "logical_operator": "ScientificMemoryUpdater",
        "operator_id": "autosci-memory-update-worker",
        "action": "update_memory",
        "gate": "G_MEMORY_UPDATE_INITIAL",
        "evidence_name": "research_memory_update.json",
    },
    {
        "node_id": "graph_update",
        "logical_operator": "ScientificGraphUpdater",
        "operator_id": "autosci-graph-update-worker",
        "action": "update_graph",
        "gate": "G_GRAPH_UPDATE",
        "evidence_name": "research_graph_update.json",
    },
    {
        "node_id": "claim_extract",
        "logical_operator": "ScientificClaimExtractor",
        "operator_id": "autosci-claim-extract-worker",
        "action": "extract_claims",
        "gate": "G_CLAIM_EXTRACT",
        "evidence_name": "research_claims.json",
    },
    {
        "node_id": "method_extract",
        "logical_operator": "ScientificMethodExtractor",
        "operator_id": "autosci-method-extract-worker",
        "action": "extract_methods",
        "gate": "G_METHOD_EXTRACT",
        "evidence_name": "research_method.json",
    },
    {
        "node_id": "code_evidence_map",
        "logical_operator": "ScientificCodeEvidenceMapper",
        "operator_id": "autosci-code-evidence-map-worker",
        "action": "map_code_evidence",
        "gate": "G_CODE_EVIDENCE_MAP",
        "evidence_name": "code_evidence_map.json",
    },
    {
        "node_id": "idea_generate",
        "logical_operator": "ScientificIdeaGenerator",
        "operator_id": "autosci-idea-worker",
        "action": "generate_ideas",
        "gate": "G_IDEA_GENERATE",
        "evidence_name": "idea_candidate.json",
    },
    {
        "node_id": "idea_evaluate",
        "logical_operator": "ScientificIdeaEvaluator",
        "operator_id": "autosci-idea-evaluate-worker",
        "action": "evaluate_ideas",
        "gate": "G_IDEA_EVALUATE",
        "evidence_name": "idea_evaluation.json",
    },
    {
        "node_id": "experiment_design",
        "logical_operator": "ScientificExperimentDesigner",
        "operator_id": "autosci-experiment-design-worker",
        "action": "design_experiment",
        "gate": "G_EXPERIMENT_DESIGN",
        "evidence_name": "experiment_plan.json",
    },
    {
        "node_id": "experiment_run",
        "logical_operator": "ScientificExperimentRunner",
        "operator_id": "autosci-experiment-run-worker",
        "action": "run_experiment",
        "gate": "G_EXPERIMENT_RUN",
        "evidence_name": "experiment_result.json",
    },
    {
        "node_id": "experiment_monitor",
        "logical_operator": "ScientificExperimentMonitor",
        "operator_id": "autosci-experiment-monitor-worker",
        "action": "monitor_experiment",
        "gate": "G_EXPERIMENT_MONITOR",
        "evidence_name": "experiment_status.json",
    },
    {
        "node_id": "claim_verify",
        "logical_operator": "ScientificClaimVerifier",
        "operator_id": "autosci-claim-verify-worker",
        "action": "verify_claim",
        "gate": "G_CLAIM_VERIFY",
        "evidence_name": "claim_verdict.json",
    },
    {
        "node_id": "report_draft",
        "logical_operator": "ScientificReportDrafter",
        "operator_id": "autosci-report-worker",
        "action": "write_report",
        "gate": "G_REPORT_DRAFT",
        "evidence_name": "scientific_report.json",
    },
    {
        "node_id": "artifact_review",
        "logical_operator": "ScientificArtifactReviewer",
        "operator_id": "autosci-artifact-review-worker",
        "action": "review_artifact",
        "gate": "G_ARTIFACT_REVIEW",
        "evidence_name": "artifact_review.json",
    },
    {
        "node_id": "memory_update_final",
        "logical_operator": "ScientificMemoryUpdater",
        "operator_id": "autosci-memory-update-worker",
        "action": "update_memory",
        "gate": "G_MEMORY_UPDATE_FINAL",
        "evidence_name": "final_research_memory_update.json",
    },
    {
        "node_id": "workflow_evolve",
        "logical_operator": "ScientificWorkflowEvolver",
        "operator_id": "autosci-workflow-evolve-worker",
        "action": "evolve_workflow",
        "gate": "G_WORKFLOW_EVOLVE",
        "evidence_name": "workflow_evolution.json",
    },
]
EXTERNAL_NODE_SPECS = [
    {
        "node_id": "report_plan",
        "logical_operator": "ScientificReportPlanner",
        "operator_id": "autosci-report-plan-worker",
        "action": "plan_report",
        "gate": "G_REPORT_PLAN",
        "evidence_name": "scientific_report_plan.json",
    },
    {
        "node_id": "publication_produce",
        "logical_operator": "ScientificPublicationProducer",
        "operator_id": "autosci-publication-compile-worker",
        "action": "compile_paper",
        "gate": "G_PUBLICATION_PRODUCE",
        "evidence_name": "publication_bundle.json",
    },
]
EXTERNAL_NODE_BY_ID = {spec["node_id"]: spec for spec in EXTERNAL_NODE_SPECS}
BLOCKED_EXTERNAL_NODE_DETAILS = {
    "report_plan": {
        "node_id": "report_plan",
        "logical_operator": "ScientificReportPlanner",
        "operator_id": "autosci-report-plan-worker",
        "action": "plan_report",
        "gate": "G_REPORT_PLAN",
        "status": "blocked",
        "reason": "Waiting for completed Review LLM artifact_review.v1 evidence.",
        "required_evidence": ["artifact_review.v1 with review_mode=review_llm and review_llm.status=completed"],
        "unblock_condition": "Provide completed Review LLM-backed artifact_review.v1 evidence, then dispatch report_plan.",
    },
    "publication_produce": {
        "node_id": "publication_produce",
        "logical_operator": "ScientificPublicationProducer",
        "operator_id": "autosci-publication-compile-worker",
        "action": "compile_paper",
        "gate": "G_PUBLICATION_PRODUCE",
        "status": "blocked",
        "reason": "Waiting for LaTeX/PDF compile evidence or approved compile runtime evidence.",
        "required_evidence": ["publication_bundle.v1 with existing files and compile/PDF evidence"],
        "unblock_condition": "Provide a compile target with LaTeX/PDF artifacts or approved runtime evidence, then dispatch publication_produce.",
    },
}
HUMAN_GATE_SPECS = [
    {
        "node_id": "idea_acceptance_gate",
        "logical_operator": "ScientificWorkflowEvolver",
        "operator_id": "human-approval-gate",
        "action": "approve_idea_selection",
        "gate": "G_HUMAN_IDEA_ACCEPTANCE",
        "evidence_name": "idea_acceptance_gate.json",
    },
    {
        "node_id": "results_acceptance_gate",
        "logical_operator": "ScientificWorkflowEvolver",
        "operator_id": "human-approval-gate",
        "action": "approve_results_acceptance",
        "gate": "G_HUMAN_RESULTS_ACCEPTANCE",
        "evidence_name": "results_acceptance_gate.json",
    },
]
HUMAN_GATE_BY_ID = {spec["node_id"]: spec for spec in HUMAN_GATE_SPECS}
HUMAN_GATE_AFTER_NODE = {
    "idea_evaluate": "idea_acceptance_gate",
    "claim_verify": "results_acceptance_gate",
}
HUMAN_GATE_APPROVAL_ATTR = {
    "idea_acceptance_gate": "idea_approval_ref",
    "results_acceptance_gate": "results_approval_ref",
}
HUMAN_GATE_BLOCKED_DETAILS = {
    "idea_acceptance_gate": {
        "reason": "Waiting for durable human approval of the selected idea before experiment design.",
        "required_evidence": ["Human approval evidence for accepted/rejected idea IDs"],
        "unblock_condition": "Provide --idea-approval-ref or resume with recorded idea approval evidence.",
    },
    "results_acceptance_gate": {
        "reason": "Waiting for durable human approval of experiment results before publication planning.",
        "required_evidence": ["Human approval evidence for accepted/rejected experiment verdict"],
        "unblock_condition": "Provide --results-approval-ref or resume with recorded results approval evidence.",
    },
}


def _utc_stamp() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")


def _resolve_harness_path(root: Path, raw: str | Path) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else root / path


def _rel(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _gate_lifecycle(summary_path: Path, harness_dir: Path) -> dict[str, Any]:
    env = os.environ.copy()
    env["HARNESS_DIR"] = str(harness_dir)
    proc = subprocess.run(
        [sys.executable, str(REPO_HARNESS_DIR / "evaluators/scientific/lifecycle_runtime_gate.py"), str(summary_path)],
        cwd=str(REPO_HARNESS_DIR),
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        payload = {
            "ok": False,
            "status": "failed",
            "reasons": [f"lifecycle_runtime_gate emitted non-json output: {proc.stdout.strip()}"],
            "warnings": [proc.stderr.strip()] if proc.stderr.strip() else [],
        }
    payload["exit_code"] = proc.returncode
    if proc.stderr.strip():
        payload.setdefault("warnings", []).append(proc.stderr.strip())
    return payload


def _blocked_external_node(job_id: str, node_id: str) -> dict[str, Any]:
    return {"job_id": job_id, **BLOCKED_EXTERNAL_NODE_DETAILS[node_id]}


def _blocked_human_gate(job_id: str, node_id: str) -> dict[str, Any]:
    spec = HUMAN_GATE_BY_ID[node_id]
    detail = HUMAN_GATE_BLOCKED_DETAILS[node_id]
    return {
        "job_id": job_id,
        "node_id": node_id,
        "logical_operator": spec["logical_operator"],
        "operator_id": spec["operator_id"],
        "action": spec["action"],
        "gate": spec["gate"],
        "status": "blocked",
        **detail,
    }


def _human_gate_approval_result(
    *,
    harness_dir: Path,
    job_id: str,
    spec: dict[str, str],
    approval_ref: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    node_id = spec["node_id"]
    output_dir = _resolve_harness_path(
        harness_dir,
        f"artifacts/scientific/scheduler-lifecycle-smoke/{job_id}/{node_id}",
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = output_dir / spec["evidence_name"]
    payload = {
        "schema": "workflow_evolution.v1",
        "task_id": f"task-{job_id}-{node_id}",
        "sprint_id": job_id,
        "node_id": node_id,
        "status": "completed",
        "inputs": {"approval_ref": approval_ref, "gate": spec["gate"]},
        "outputs": {
            "evolution": {
                "proposal_id": f"{node_id}-{approval_ref}",
                "scope": "scientific research lifecycle human gate",
                "change_type": "gate",
                "rationale": f"Human approval `{approval_ref}` was recorded as scheduler-visible lifecycle state.",
                "expected_effect": "Allow the scientific lifecycle to advance past a human approval pause without losing auditability.",
                "approval_state": "approved",
                "evidence_ids": [f"human-approval:{approval_ref}", node_id],
                "collected": {
                    "failed_nodes": [],
                    "gate_rejection_reasons": [],
                    "ambiguous_manuals_or_prompts": [],
                    "insufficient_schemas": [],
                    "poor_operator_bindings": [],
                    "human_intervention_points": [
                        {
                            "id": node_id,
                            "description": f"Approval ref `{approval_ref}` recorded for {node_id}.",
                        }
                    ],
                    "runtime_errors": [],
                },
                "review": {
                    "human_accept_reject_required": True,
                    "protected_core_edits_applied": False,
                    "application_state": "not_applied",
                    "approval_ref": approval_ref,
                },
            }
        },
        "artifacts": [],
        "provenance": {
            "operator_id": spec["operator_id"],
            "implementation_package": "harness.tools.run_scientific_lifecycle_smoke",
            "timestamp": dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        "limitations": ["Approval ref was supplied explicitly; no external side effect was executed by this gate."],
    }
    artifact_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    node_result = {
        "job_id": job_id,
        "node_id": node_id,
        "logical_operator": spec["logical_operator"],
        "operator_id": spec["operator_id"],
        "action": spec["action"],
        "status": "passed",
        "artifact_path": _rel(artifact_path, harness_dir),
        "artifact_sha256": _sha256(artifact_path),
        "expected_schema": "workflow_evolution.v1",
        "gate": spec["gate"],
        "approval_ref": approval_ref,
    }
    gate_result = {
        "job_id": job_id,
        "node_id": node_id,
        "gate": spec["gate"],
        "status": "passed",
        "ok": True,
        "reasons": [],
        "warnings": [],
        "approval_ref": approval_ref,
    }
    return node_result, gate_result


def _extra_inputs_for(
    spec: dict[str, str],
    node_results: dict[str, Any],
    args: argparse.Namespace | None = None,
) -> dict[str, Any]:
    node_id = spec["node_id"]
    inputs: dict[str, Any] = {"smoke_mode": True}
    discovery_path = (node_results.get("literature_discover") or {}).get("artifact_path")
    paper_path = (node_results.get("paper_ingest") or {}).get("artifact_path")
    claims_path = (node_results.get("claim_extract") or {}).get("artifact_path")
    method_path = (node_results.get("method_extract") or {}).get("artifact_path")
    code_path = (node_results.get("code_evidence_map") or {}).get("artifact_path")
    idea_path = (node_results.get("idea_generate") or {}).get("artifact_path")
    idea_eval_path = (node_results.get("idea_evaluate") or {}).get("artifact_path")
    experiment_plan_path = (node_results.get("experiment_design") or {}).get("artifact_path")
    experiment_result_path = (node_results.get("experiment_run") or {}).get("artifact_path")
    claim_verdict_path = (node_results.get("claim_verify") or {}).get("artifact_path")
    report_path = (node_results.get("report_draft") or {}).get("artifact_path")
    review_llm_evidence = list(getattr(args, "review_llm_evidence", None) or []) if args else []
    compile_target = str(getattr(args, "compile_target", "") or "") if args else ""
    experiment_approval_ref = str(getattr(args, "experiment_approval_ref", "") or "") if args else ""
    experiment_runtime_evidence = list(getattr(args, "experiment_runtime_evidence", None) or []) if args else []
    experiment_allowlist = list(getattr(args, "experiment_allowlist_evidence", None) or []) if args else []
    experiment_before = list(getattr(args, "experiment_before_artifact", None) or []) if args else []
    experiment_after = list(getattr(args, "experiment_after_artifact", None) or []) if args else []
    experiment_execute_approved = bool(getattr(args, "experiment_execute_approved", False)) if args else False
    experiment_executor_timeout = int(getattr(args, "experiment_executor_timeout_seconds", 120) or 120) if args else 120
    compile_approval_ref = str(getattr(args, "compile_approval_ref", "") or "") if args else ""
    compile_runtime_evidence = list(getattr(args, "compile_runtime_evidence", None) or []) if args else []
    compile_allowlist = list(getattr(args, "compile_allowlist_evidence", None) or []) if args else []
    compile_before = list(getattr(args, "compile_before_artifact", None) or []) if args else []
    compile_after = list(getattr(args, "compile_after_artifact", None) or []) if args else []
    compile_execute_approved = bool(getattr(args, "compile_execute_approved", False)) if args else False
    compile_executor_timeout = int(getattr(args, "compile_executor_timeout_seconds", 120) or 120) if args else 120
    has_experiment_runtime_contract = bool(
        experiment_approval_ref
        or experiment_runtime_evidence
        or experiment_allowlist
        or experiment_before
        or experiment_after
        or experiment_execute_approved
    )

    if node_id in {"memory_update_initial", "graph_update", "method_extract"} and paper_path:
        inputs["source_evidence"] = paper_path
    if node_id == "literature_discover":
        allow_network_fetch = bool(getattr(args, "allow_network_fetch", False)) if args else False
        require_online = bool(getattr(args, "require_online_source_evidence", False)) if args else False
        disable_fixture_fallback = bool(getattr(args, "disable_fixture_fallback", False)) if args else False
        discovery_query = str(getattr(args, "discovery_query", "") or "scheduler lifecycle smoke") if args else "scheduler lifecycle smoke"
        discovery_mode = str(getattr(args, "discovery_mode", "") or "") if args else ""
        discovery_limit = int(getattr(args, "discovery_limit", 3) or 3) if args else 3
        min_online_channels = int(getattr(args, "min_online_source_channels", 1) or 1) if args else 1
        source_runtime_evidence = list(getattr(args, "source_runtime_evidence", None) or []) if args else []
        source_allowlist = list(getattr(args, "source_allowlist_evidence", None) or []) if args else []
        source_before = list(getattr(args, "source_before_artifact", None) or []) if args else []
        source_after = list(getattr(args, "source_after_artifact", None) or []) if args else []
        source_approval_ref = str(getattr(args, "source_approval_ref", "") or "") if args else ""
        inputs.update({
            "query": discovery_query,
            "topic": discovery_query,
            "limit": discovery_limit,
            "allow_network_fetch": allow_network_fetch,
            "fixture_fallback": not (disable_fixture_fallback or require_online),
            "require_online_source_evidence": require_online,
            "min_online_source_channels": min_online_channels,
        })
        if discovery_mode:
            inputs["discover_mode"] = discovery_mode
        if source_approval_ref:
            inputs["approval_ref"] = source_approval_ref
        if source_runtime_evidence:
            inputs["runtime_evidence"] = source_runtime_evidence
        if source_allowlist:
            inputs["allowlist_evidence"] = source_allowlist
        if source_before:
            inputs["before_artifacts"] = source_before
        if source_after:
            inputs["after_artifacts"] = source_after
    if node_id in {"code_evidence_map", "idea_generate", "idea_evaluate"}:
        if claims_path:
            inputs["claims_evidence"] = claims_path
        if method_path:
            inputs["method_evidence"] = method_path
    if node_id == "code_evidence_map":
        inputs["repo_path"] = "plugins/autosci/tests/fixtures/sample_repo"
    if node_id in {"idea_generate", "idea_evaluate"}:
        if paper_path:
            inputs["paper_evidence"] = paper_path
        if idea_path:
            inputs["ideas_evidence"] = idea_path
    if node_id == "claim_verify":
        if claims_path:
            inputs["claims_evidence"] = claims_path
        if code_path:
            inputs["code_evidence"] = code_path
        if experiment_result_path:
            inputs["experiment_result_evidence"] = experiment_result_path
        inputs["claim_id"] = "claim-001"
    if node_id == "experiment_design":
        inputs.update({
            "claim_id": "claim-001",
            "execution_mode": "fixture",
        })
        if idea_eval_path:
            inputs["idea_evaluation_evidence"] = idea_eval_path
    if node_id == "experiment_run":
        inputs["execution_mode"] = "human_approved" if has_experiment_runtime_contract else "fixture"
        if experiment_plan_path:
            inputs["experiment_plan_evidence"] = experiment_plan_path
        if has_experiment_runtime_contract:
            if experiment_approval_ref:
                inputs["approval_ref"] = experiment_approval_ref
            if experiment_runtime_evidence:
                inputs["runtime_evidence"] = experiment_runtime_evidence
            if experiment_allowlist:
                inputs["allowlist_evidence"] = experiment_allowlist
            if experiment_before:
                inputs["before_artifacts"] = experiment_before
            if experiment_after:
                inputs["after_artifacts"] = experiment_after
            if experiment_execute_approved:
                inputs["execute_approved_side_effect"] = True
                inputs["executor_timeout_seconds"] = experiment_executor_timeout
        else:
            inputs["experiment_result"] = "plugins/autosci/tests/fixtures/sample_autosci_raw_experiment_result.json"
    if node_id == "experiment_monitor":
        inputs["execution_mode"] = "human_approved" if has_experiment_runtime_contract else "fixture"
        if experiment_plan_path:
            inputs["experiment_plan_evidence"] = experiment_plan_path
        if has_experiment_runtime_contract and experiment_runtime_evidence:
            inputs["collect"] = True
            if experiment_approval_ref:
                inputs["approval_ref"] = experiment_approval_ref
            if experiment_runtime_evidence:
                inputs["runtime_evidence"] = experiment_runtime_evidence
            if experiment_allowlist:
                inputs["allowlist_evidence"] = experiment_allowlist
            if experiment_before:
                inputs["before_artifacts"] = experiment_before
            if experiment_after:
                inputs["after_artifacts"] = experiment_after
        elif experiment_result_path:
            inputs["experiment_result_evidence"] = experiment_result_path
    if node_id == "report_draft":
        inputs.update({
            "claim_id": "claim-001",
            "experiment_id": "exp-supported-001",
            "report_id": "report-scheduler-lifecycle-smoke",
            "report_title": "Scheduler Lifecycle Smoke Report",
        })
        if claims_path:
            inputs["claims_evidence"] = claims_path
        if claim_verdict_path:
            inputs["claim_verdict_evidence"] = claim_verdict_path
        if experiment_result_path:
            inputs["experiment_result"] = experiment_result_path
        if code_path:
            inputs["code_evidence"] = code_path
        if method_path:
            inputs["method_evidence"] = method_path
        if idea_eval_path:
            inputs["idea_evaluation_evidence"] = idea_eval_path
        if paper_path:
            inputs["paper_evidence"] = paper_path
    if node_id == "memory_update_final" and report_path:
        inputs["source_evidence"] = report_path
    if node_id == "artifact_review":
        if report_path:
            inputs["target"] = report_path
            inputs["artifact_path"] = report_path
        inputs["difficulty"] = "standard"
        inputs["focus"] = "completeness"
    if node_id == "workflow_evolve":
        inputs["failed_run"] = {
            "workflow_id": DEFAULT_WORKFLOW_ID,
            "sprint_id": "scheduler-lifecycle-smoke-synthetic-failed-run",
            "nodes": [
                {
                    "id": "publication_produce",
                    "logical_operator": "ScientificPublicationProducer",
                    "gate": "G_PUBLICATION_PRODUCE",
                    "status": "failed",
                }
            ],
            "gate_results": {
                "G_PUBLICATION_PRODUCE": {
                    "status": "failed",
                    "reasons": [
                        "publication_produce currently lacks a scheduler-bound publication_bundle.v1 action"
                    ],
                }
            },
            "ambiguous_manuals_or_prompts": [
                {
                    "manual_id": "scientific-publication-produce.dispatch",
                    "description": "Scheduler publication dispatch does not yet distinguish report drafting from publication bundle compilation."
                }
            ],
            "insufficient_schemas": [],
            "poor_operator_bindings": [
                {
                    "logical_operator": "ScientificPublicationProducer",
                    "physical_operator": "autosci-report-worker",
                    "description": "Current report worker emits scientific_report.v1 as the primary evidence."
                }
            ],
            "human_intervention_points": [
                {
                    "point": "publication_compile_approval",
                    "description": "Compiled publication output requires explicit bounded compile or human-approved external execution."
                }
            ],
            "runtime_errors": [
                {
                    "error_id": "runtime.publication-bundle-action-missing",
                    "message": "No dedicated scheduler physical operator currently emits publication_bundle.v1."
                }
            ],
        }
    if node_id == "report_plan":
        inputs.update({
            "claim_id": "claim-001",
            "experiment_id": "exp-supported-001",
            "report_id": "report-scheduler-lifecycle-resume-plan",
            "report_title": "Scheduler Lifecycle Resumed Paper Plan",
            "target": "scheduler-lifecycle-resume",
        })
        if discovery_path:
            inputs["discovery_evidence"] = discovery_path
        if paper_path:
            inputs["paper_evidence"] = paper_path
        if claims_path:
            inputs["claims_evidence"] = claims_path
        if claim_verdict_path:
            inputs["claim_verdict_evidence"] = claim_verdict_path
        if experiment_result_path:
            inputs["experiment_result"] = experiment_result_path
        if code_path:
            inputs["code_evidence"] = code_path
        if method_path:
            inputs["method_evidence"] = method_path
        if idea_eval_path:
            inputs["idea_evaluation_evidence"] = idea_eval_path
        if review_llm_evidence:
            inputs["review_llm_evidence"] = review_llm_evidence
            inputs["artifact_review_evidence"] = review_llm_evidence
    if node_id == "publication_produce":
        inputs.update({
            "checklist": True,
            "title": "Scheduler Lifecycle Resumed Publication",
        })
        if compile_target:
            inputs["paper_path"] = compile_target
            inputs["target"] = compile_target
        if compile_approval_ref:
            inputs["approval_ref"] = compile_approval_ref
        if compile_runtime_evidence:
            inputs["runtime_evidence"] = compile_runtime_evidence
        if compile_allowlist:
            inputs["allowlist_evidence"] = compile_allowlist
        if compile_before:
            inputs["before_artifacts"] = compile_before
        if compile_after:
            inputs["after_artifacts"] = compile_after
        if compile_execute_approved:
            inputs["execute_approved_side_effect"] = True
            inputs["executor_timeout_seconds"] = compile_executor_timeout
    return inputs


def _node_args(
    args: argparse.Namespace,
    harness_dir: Path,
    job_id: str,
    spec: dict[str, str],
    node_results: dict[str, Any],
) -> argparse.Namespace:
    task_id = f"task-{job_id}-{spec['node_id']}"
    return argparse.Namespace(
        harness_dir=str(harness_dir),
        operator_id=spec["operator_id"],
        node_id=spec["node_id"],
        action=spec["action"],
        logical_operator=spec["logical_operator"],
        expected_schema=None,
        evidence_name=spec["evidence_name"],
        task_id=task_id,
        sprint_id=job_id,
        paper=args.paper,
        paper_id=f"paper-{job_id}",
        input_json=None,
        extra_inputs=_extra_inputs_for(spec, node_results, args),
        output_dir=f"artifacts/scientific/scheduler-lifecycle-smoke/{job_id}/{spec['node_id']}",
        out=None,
        timeout_seconds=float(args.timeout_seconds),
        lease_ttl_seconds=int(args.lease_ttl_seconds),
        allow_existing_result=bool(args.allow_existing_result),
    )


def _node_result_from_summary(
    *,
    node_summary: dict[str, Any],
    harness_dir: Path,
    job_id: str,
    gate_name: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    evidence_path = _resolve_harness_path(harness_dir, str(node_summary["evidence_path"]))
    artifact_hash = _sha256(evidence_path)
    bridge_result = node_summary.get("bridge_result") if isinstance(node_summary.get("bridge_result"), dict) else {}
    expected_schema = str(bridge_result.get("schema") or "research_paper.v1")
    node_result = {
        "job_id": job_id,
        "node_id": node_summary["node_id"],
        "logical_operator": node_summary["logical_operator"],
        "operator_id": node_summary["operator_id"],
        "action": node_summary["action"],
        "status": "passed" if node_summary.get("status") == "passed" else "failed",
        "artifact_path": node_summary["evidence_path"],
        "artifact_sha256": artifact_hash,
        "expected_schema": expected_schema,
        "gate": gate_name,
        "operator_result_path": node_summary["operator_result_path"],
        "bridge_result_path": node_summary["bridge_result_path"],
    }
    raw_gate = node_summary.get("gate_result") if isinstance(node_summary.get("gate_result"), dict) else {}
    gate_result = {
        "job_id": job_id,
        "node_id": node_summary["node_id"],
        "gate": gate_name,
        "status": str(raw_gate.get("status") or "failed"),
        "ok": bool(raw_gate.get("ok")),
        "reasons": raw_gate.get("reasons") or [],
        "warnings": raw_gate.get("warnings") or [],
    }
    return node_result, gate_result


def _ensure_lifecycle_node(lifecycle: dict[str, Any], spec: dict[str, str]) -> None:
    required_nodes = lifecycle.setdefault("required_nodes", [])
    if isinstance(required_nodes, list) and spec["node_id"] not in required_nodes:
        required_nodes.append(spec["node_id"])
    nodes = lifecycle.setdefault("nodes", [])
    if isinstance(nodes, list) and not any(
        isinstance(node, dict) and node.get("id") == spec["node_id"]
        for node in nodes
    ):
        nodes.append({
            "id": spec["node_id"],
            "logical_operator": spec["logical_operator"],
            "operator_id": spec["operator_id"],
            "action": spec["action"],
            "gate": spec["gate"],
        })


def _resume_evidence_supplied(args: argparse.Namespace, node_id: str) -> bool:
    if node_id == "report_plan":
        return bool(getattr(args, "review_llm_evidence", None))
    if node_id == "publication_produce":
        return bool(str(getattr(args, "compile_target", "") or "").strip())
    return False


def _write_and_gate_lifecycle(
    lifecycle: dict[str, Any],
    summary_path: Path,
    harness_dir: Path,
    *,
    blocked_nodes: dict[str, Any],
    checks: list[dict[str, str]],
    gate_check_name: str = "lifecycle_runtime_gate_passed",
) -> tuple[int, dict[str, Any]]:
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    lifecycle["summary_path"] = _rel(summary_path, harness_dir)
    summary_path.write_text(json.dumps(lifecycle, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lifecycle_gate = _gate_lifecycle(summary_path, harness_dir)
    lifecycle["lifecycle_gate_result"] = lifecycle_gate
    lifecycle_gate_ok = lifecycle_gate.get("ok") is True or (
        bool(blocked_nodes) and str(lifecycle_gate.get("status") or "") == "inconclusive"
    )
    checks.append({
        "check": gate_check_name,
        "status": "ok" if lifecycle_gate_ok else "error",
        "detail": str(lifecycle_gate.get("status")),
    })
    if all(item["status"] == "ok" for item in checks):
        lifecycle["lifecycle_status"] = "blocked" if blocked_nodes else "passed"
    else:
        lifecycle["lifecycle_status"] = "failed"
    lifecycle["summary_path"] = _rel(summary_path, harness_dir)
    summary_path.write_text(json.dumps(lifecycle, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if lifecycle["lifecycle_status"] == "passed":
        return 0, lifecycle
    if lifecycle["lifecycle_status"] == "blocked":
        return 3, lifecycle
    return 1, lifecycle


def run_resume(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    harness_dir = Path(args.harness_dir).expanduser().resolve()
    resume_summary_path = _resolve_harness_path(harness_dir, str(args.resume_summary))
    base = json.loads(resume_summary_path.read_text(encoding="utf-8"))
    if not isinstance(base, dict):
        raise ValueError(f"Lifecycle summary must be a JSON object: {resume_summary_path}")

    lifecycle = copy.deepcopy(base)
    job_id = str(lifecycle.get("job_id") or lifecycle.get("sprint_id") or args.job_id or f"job-scientific-lifecycle-resume-{_utc_stamp()}")
    lifecycle["job_id"] = job_id
    lifecycle["sprint_id"] = job_id
    lifecycle["execution_owner"] = "solar.operator_runtime.scheduler_lifecycle_resume"
    lifecycle["resume_source_summary_path"] = _rel(resume_summary_path, harness_dir)

    node_summaries = lifecycle.setdefault("node_summaries", {})
    node_results = lifecycle.setdefault("node_results", {})
    gate_results = lifecycle.setdefault("gate_results", {})
    blocked_nodes = lifecycle.setdefault("blocked_nodes", {})
    checks = lifecycle.setdefault("checks", [])
    if not isinstance(node_summaries, dict):
        node_summaries = lifecycle["node_summaries"] = {}
    if not isinstance(node_results, dict):
        node_results = lifecycle["node_results"] = {}
    if not isinstance(gate_results, dict):
        gate_results = lifecycle["gate_results"] = {}
    if not isinstance(blocked_nodes, dict):
        blocked_nodes = lifecycle["blocked_nodes"] = {}
    if not isinstance(checks, list):
        checks = lifecycle["checks"] = []

    stopped_for_human_gate = False
    resume_after_node: str | None = None
    human_gate_mode = bool(args.include_human_gates) or any(
        gate_id in blocked_nodes or gate_id in node_results for gate_id in HUMAN_GATE_BY_ID
    )
    for gate_node_id in ("idea_acceptance_gate", "results_acceptance_gate"):
        if gate_node_id not in blocked_nodes:
            continue
        gate_spec = HUMAN_GATE_BY_ID[gate_node_id]
        _ensure_lifecycle_node(lifecycle, gate_spec)
        approval_ref = str(getattr(args, HUMAN_GATE_APPROVAL_ATTR[gate_node_id]) or "").strip()
        if not approval_ref:
            checks.append({
                "check": f"{gate_node_id}_resume_waiting",
                "status": "ok",
                "detail": "required human approval evidence was not supplied",
            })
            stopped_for_human_gate = True
            continue
        node_result, gate_result = _human_gate_approval_result(
            harness_dir=harness_dir,
            job_id=job_id,
            spec=gate_spec,
            approval_ref=approval_ref,
        )
        node_results[gate_node_id] = node_result
        gate_results[gate_node_id] = gate_result
        blocked_nodes.pop(gate_node_id, None)
        checks.append({
            "check": f"{gate_node_id}_resumed_approved",
            "status": "ok",
            "detail": approval_ref,
        })
        resume_after_node = "idea_evaluate" if gate_node_id == "idea_acceptance_gate" else "claim_verify"
        stopped_for_human_gate = False

    if resume_after_node:
        start_index = next(
            (index + 1 for index, spec in enumerate(NODE_SPECS) if spec["node_id"] == resume_after_node),
            len(NODE_SPECS),
        )
        for spec in NODE_SPECS[start_index:]:
            node_id = spec["node_id"]
            if node_id in node_results:
                continue
            _ensure_lifecycle_node(lifecycle, spec)
            code, node_summary = node_smoke.run(_node_args(args, harness_dir, job_id, spec, node_results))
            node_summaries[node_id] = node_summary
            node_ok = code == 0 and node_summary.get("status") == "passed"
            checks.append({
                "check": f"{node_id}_resumed_dispatched",
                "status": "ok" if node_ok else "error",
                "detail": str(node_summary.get("status")),
            })
            if node_ok:
                node_result, gate_result = _node_result_from_summary(
                    node_summary=node_summary,
                    harness_dir=harness_dir,
                    job_id=job_id,
                    gate_name=spec["gate"],
                )
                node_results[node_id] = node_result
                gate_results[node_id] = gate_result
            else:
                break
            if human_gate_mode and node_id in HUMAN_GATE_AFTER_NODE:
                gate_node_id = HUMAN_GATE_AFTER_NODE[node_id]
                if gate_node_id in node_results:
                    continue
                gate_spec = HUMAN_GATE_BY_ID[gate_node_id]
                _ensure_lifecycle_node(lifecycle, gate_spec)
                approval_ref = str(getattr(args, HUMAN_GATE_APPROVAL_ATTR[gate_node_id]) or "").strip()
                if approval_ref:
                    node_result, gate_result = _human_gate_approval_result(
                        harness_dir=harness_dir,
                        job_id=job_id,
                        spec=gate_spec,
                        approval_ref=approval_ref,
                    )
                    node_results[gate_node_id] = node_result
                    gate_results[gate_node_id] = gate_result
                    checks.append({
                        "check": f"{gate_node_id}_resumed_approved",
                        "status": "ok",
                        "detail": approval_ref,
                    })
                else:
                    blocked_nodes[gate_node_id] = _blocked_human_gate(job_id, gate_node_id)
                    checks.append({
                        "check": f"{gate_node_id}_resume_blocked",
                        "status": "ok",
                        "detail": "waiting for durable human approval evidence",
                    })
                    stopped_for_human_gate = True
                    break

    for spec in EXTERNAL_NODE_SPECS:
        if stopped_for_human_gate:
            break
        node_id = spec["node_id"]
        _ensure_lifecycle_node(lifecycle, spec)
        if node_id not in blocked_nodes and node_id not in node_results:
            blocked_nodes[node_id] = _blocked_external_node(job_id, node_id)

        if node_id not in blocked_nodes:
            continue
        if not _resume_evidence_supplied(args, node_id):
            checks.append({
                "check": f"{node_id}_resume_waiting",
                "status": "ok",
                "detail": "required external evidence was not supplied",
            })
            continue

        code, node_summary = node_smoke.run(_node_args(args, harness_dir, job_id, spec, node_results))
        node_summaries[node_id] = node_summary
        node_ok = code == 0 and node_summary.get("status") == "passed"
        checks.append({
            "check": f"{node_id}_resumed_dispatched",
            "status": "ok" if node_ok else "error",
            "detail": str(node_summary.get("status")),
        })
        if node_ok:
            node_result, gate_result = _node_result_from_summary(
                node_summary=node_summary,
                harness_dir=harness_dir,
                job_id=job_id,
                gate_name=spec["gate"],
            )
            node_results[node_id] = node_result
            gate_results[node_id] = gate_result
            blocked_nodes.pop(node_id, None)

    output_root = _resolve_harness_path(
        harness_dir,
        args.output_dir or resume_summary_path.parent,
    )
    summary_path = _resolve_harness_path(
        harness_dir,
        args.out or output_root / "scientific_lifecycle_runtime.resumed.json",
    )
    lifecycle["lifecycle_status"] = "blocked" if blocked_nodes else "passed"
    return _write_and_gate_lifecycle(
        lifecycle,
        summary_path,
        harness_dir,
        blocked_nodes=blocked_nodes,
        checks=checks,
        gate_check_name="resume_lifecycle_runtime_gate_passed",
    )


def run(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    if args.resume_summary:
        return run_resume(args)

    harness_dir = Path(args.harness_dir).expanduser().resolve()
    job_id = args.job_id or f"job-scientific-lifecycle-smoke-{_utc_stamp()}"
    lifecycle_dir = _resolve_harness_path(
        harness_dir,
        args.output_dir or f"artifacts/scientific/scheduler-lifecycle-smoke/{job_id}",
    )
    summary_path = _resolve_harness_path(
        harness_dir,
        args.out or lifecycle_dir / "scientific_lifecycle_runtime.json",
    )

    node_summaries: dict[str, Any] = {}
    node_results: dict[str, Any] = {}
    gate_results: dict[str, Any] = {}
    blocked_nodes: dict[str, Any] = {}
    checks: list[dict[str, str]] = []
    executed_specs: list[dict[str, str]] = []
    human_gate_specs: list[dict[str, str]] = []
    stopped_for_human_gate = False

    for spec in NODE_SPECS:
        code, node_summary = node_smoke.run(_node_args(args, harness_dir, job_id, spec, node_results))
        executed_specs.append(spec)
        node_summaries[spec["node_id"]] = node_summary
        node_ok = code == 0 and node_summary.get("status") == "passed"
        checks.append({
            "check": f"{spec['node_id']}_dispatched",
            "status": "ok" if node_ok else "error",
            "detail": str(node_summary.get("status")),
        })
        if node_ok:
            node_result, gate_result = _node_result_from_summary(
                node_summary=node_summary,
                harness_dir=harness_dir,
                job_id=job_id,
                gate_name=spec["gate"],
            )
            node_results[spec["node_id"]] = node_result
            gate_results[spec["node_id"]] = gate_result
        else:
            break
        if args.include_human_gates and spec["node_id"] in HUMAN_GATE_AFTER_NODE:
            gate_node_id = HUMAN_GATE_AFTER_NODE[spec["node_id"]]
            gate_spec = HUMAN_GATE_BY_ID[gate_node_id]
            human_gate_specs.append(gate_spec)
            approval_ref = str(getattr(args, HUMAN_GATE_APPROVAL_ATTR[gate_node_id]) or "").strip()
            if approval_ref:
                node_result, gate_result = _human_gate_approval_result(
                    harness_dir=harness_dir,
                    job_id=job_id,
                    spec=gate_spec,
                    approval_ref=approval_ref,
                )
                node_results[gate_node_id] = node_result
                gate_results[gate_node_id] = gate_result
                checks.append({
                    "check": f"{gate_node_id}_approved",
                    "status": "ok",
                    "detail": approval_ref,
                })
            else:
                blocked_nodes[gate_node_id] = _blocked_human_gate(job_id, gate_node_id)
                checks.append({
                    "check": f"{gate_node_id}_blocked",
                    "status": "ok",
                    "detail": "waiting for durable human approval evidence",
                })
                stopped_for_human_gate = True
                break

    lifecycle_specs = [*executed_specs, *human_gate_specs] if args.include_human_gates else NODE_SPECS
    required_nodes = [spec["node_id"] for spec in lifecycle_specs]
    nodes = [
        {
            "id": spec["node_id"],
            "logical_operator": spec["logical_operator"],
            "operator_id": spec["operator_id"],
            "action": spec["action"],
            "gate": spec["gate"],
        }
        for spec in lifecycle_specs
    ]
    if args.dispatch_external_evidence and not stopped_for_human_gate and len(node_results) >= len(NODE_SPECS):
        for spec in EXTERNAL_NODE_SPECS:
            node_id = spec["node_id"]
            required_nodes.append(node_id)
            nodes.append({
                "id": node_id,
                "logical_operator": spec["logical_operator"],
                "operator_id": spec["operator_id"],
                "action": spec["action"],
                "gate": spec["gate"],
            })
            if not _resume_evidence_supplied(args, node_id):
                blocked_nodes[node_id] = _blocked_external_node(job_id, node_id)
                checks.append({
                    "check": f"{node_id}_external_evidence_supplied",
                    "status": "error",
                    "detail": "required external evidence was not supplied",
                })
                continue
            code, node_summary = node_smoke.run(_node_args(args, harness_dir, job_id, spec, node_results))
            node_summaries[node_id] = node_summary
            node_ok = code == 0 and node_summary.get("status") == "passed"
            checks.append({
                "check": f"{node_id}_dispatched",
                "status": "ok" if node_ok else "error",
                "detail": str(node_summary.get("status")),
            })
            if node_ok:
                node_result, gate_result = _node_result_from_summary(
                    node_summary=node_summary,
                    harness_dir=harness_dir,
                    job_id=job_id,
                    gate_name=spec["gate"],
                )
                node_results[node_id] = node_result
                gate_results[node_id] = gate_result

    if args.include_blocked_external and not stopped_for_human_gate:
        for node_id in EXTERNAL_NODE_BY_ID:
            if node_id in node_results or node_id in blocked_nodes:
                continue
            blocked = _blocked_external_node(job_id, node_id)
            required_nodes.append(node_id)
            nodes.append({
                "id": node_id,
                "logical_operator": blocked["logical_operator"],
                "operator_id": blocked["operator_id"],
                "action": blocked["action"],
                "gate": blocked["gate"],
            })
            blocked_nodes[node_id] = blocked
        checks.append({
            "check": "external_blocked_nodes_recorded",
            "status": "ok",
            "detail": ",".join(sorted(blocked_nodes)),
        })

    unblocked_required_nodes = [node_id for node_id in required_nodes if node_id not in blocked_nodes]
    nodes_ok = all(node_id in node_results for node_id in unblocked_required_nodes) and all(
        item["status"] == "ok" for item in checks
    )
    lifecycle_status = "passed" if nodes_ok and not blocked_nodes else "blocked" if nodes_ok else "failed"
    lifecycle = {
        "schema": "scientific_lifecycle.v1",
        "workflow_id": DEFAULT_WORKFLOW_ID,
        "job_id": job_id,
        "sprint_id": job_id,
        "lifecycle_status": lifecycle_status,
        "execution_owner": "solar.operator_runtime.scheduler_lifecycle_smoke",
        "required_nodes": required_nodes,
        "nodes": nodes,
        "node_results": node_results,
        "gate_results": gate_results,
        "blocked_nodes": blocked_nodes,
        "node_summaries": node_summaries,
        "checks": checks,
    }
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(lifecycle, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lifecycle_gate = _gate_lifecycle(summary_path, harness_dir)
    lifecycle["lifecycle_gate_result"] = lifecycle_gate
    lifecycle_gate_ok = lifecycle_gate.get("ok") is True or (
        bool(blocked_nodes) and str(lifecycle_gate.get("status") or "") == "inconclusive"
    )
    checks.append({
        "check": "lifecycle_runtime_gate_passed",
        "status": "ok" if lifecycle_gate_ok else "error",
        "detail": str(lifecycle_gate.get("status")),
    })
    if all(item["status"] == "ok" for item in checks):
        lifecycle["lifecycle_status"] = "blocked" if blocked_nodes else "passed"
    else:
        lifecycle["lifecycle_status"] = "failed"
    lifecycle["summary_path"] = _rel(summary_path, harness_dir)
    summary_path.write_text(json.dumps(lifecycle, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if lifecycle["lifecycle_status"] == "passed":
        return 0, lifecycle
    if lifecycle["lifecycle_status"] == "blocked":
        return 3, lifecycle
    return 1, lifecycle


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--harness-dir", default=str(Path(os.environ.get("HARNESS_DIR", REPO_HARNESS_DIR))))
    parser.add_argument("--job-id")
    parser.add_argument("--paper", default=DEFAULT_PAPER)
    parser.add_argument("--output-dir")
    parser.add_argument("--out", help="Optional lifecycle summary JSON path, relative to --harness-dir.")
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    parser.add_argument("--lease-ttl-seconds", type=int, default=120)
    parser.add_argument("--allow-existing-result", action="store_true")
    parser.add_argument("--include-blocked-external", action="store_true")
    parser.add_argument("--include-human-gates", action="store_true", help="Record native AutoSci human approval gates as scheduler-visible blocked/passed nodes.")
    parser.add_argument("--idea-approval-ref", help="Durable approval reference for the idea acceptance human gate.")
    parser.add_argument("--results-approval-ref", help="Durable approval reference for the results acceptance human gate.")
    parser.add_argument("--resume-summary", help="Blocked lifecycle summary JSON to resume, relative to --harness-dir.")
    parser.add_argument(
        "--review-llm-evidence",
        action="append",
        help="Completed artifact_review.v1 Review LLM evidence path used to unblock report_plan.",
    )
    parser.add_argument("--compile-target", help="LaTeX/PDF target path used to unblock publication_produce.")
    parser.add_argument("--compile-approval-ref", help="Approval reference for supplied or executed publication compile evidence.")
    parser.add_argument("--compile-runtime-evidence", action="append", help="Approved paper compile runtime evidence JSON.")
    parser.add_argument("--compile-allowlist-evidence", action="append", help="Allowlist evidence for publication compile runtime.")
    parser.add_argument("--compile-before-artifact", action="append", help="Before artifact for publication compile runtime.")
    parser.add_argument("--compile-after-artifact", action="append", help="After artifact for publication compile runtime.")
    parser.add_argument("--compile-execute-approved", action="store_true", help="Execute the approved allowlisted TeX command during publication_produce.")
    parser.add_argument("--compile-executor-timeout-seconds", type=int, default=120, help="Timeout for an approved publication compile command.")
    parser.add_argument("--allow-network-fetch", action="store_true", help="Allow discovery actions to call configured online sources.")
    parser.add_argument("--disable-fixture-fallback", action="store_true", help="Prevent discovery from using local fixture candidates.")
    parser.add_argument(
        "--require-online-source-evidence",
        action="store_true",
        help="Require completed non-fixture online literature discovery evidence.",
    )
    parser.add_argument("--min-online-source-channels", type=int, default=1)
    parser.add_argument("--discovery-query", help="Query for the literature discovery node.")
    parser.add_argument("--discovery-mode", help="Explicit discovery mode such as topic, anchors, wiki, or venue.")
    parser.add_argument("--discovery-limit", type=int, default=3)
    parser.add_argument("--source-approval-ref", help="Approval reference for supplied online source runtime evidence.")
    parser.add_argument("--source-runtime-evidence", action="append", help="Approved source-fetch runtime evidence JSON.")
    parser.add_argument("--source-allowlist-evidence", action="append", help="Allowlist evidence for source-fetch runtime.")
    parser.add_argument("--source-before-artifact", action="append", help="Before artifact for source-fetch runtime.")
    parser.add_argument("--source-after-artifact", action="append", help="After artifact for source-fetch runtime.")
    parser.add_argument("--experiment-approval-ref", help="Approval reference for supplied experiment runtime evidence.")
    parser.add_argument("--experiment-runtime-evidence", action="append", help="Approved experiment runtime/result evidence JSON.")
    parser.add_argument("--experiment-allowlist-evidence", action="append", help="Allowlist evidence for experiment runtime.")
    parser.add_argument("--experiment-before-artifact", action="append", help="Before artifact for experiment runtime.")
    parser.add_argument("--experiment-after-artifact", action="append", help="After artifact for experiment runtime.")
    parser.add_argument("--experiment-execute-approved", action="store_true", help="Execute the approved allowlisted experiment command during experiment_run.")
    parser.add_argument("--experiment-executor-timeout-seconds", type=int, default=120, help="Timeout for an approved experiment executor command.")
    parser.add_argument(
        "--dispatch-external-evidence",
        action="store_true",
        help="Dispatch report_plan and publication_produce in the same lifecycle run when their evidence is supplied.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    code, summary = run(args)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
