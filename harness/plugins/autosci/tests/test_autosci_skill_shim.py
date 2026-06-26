from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parents[3]
REPO = HARNESS.parent
SHIM = HARNESS / "plugins" / "autosci" / "bin" / "autosci_skill_shim.py"
GATE = HARNESS / "evaluators" / "scientific" / "autosci_skill_run_gate.py"
PAPER = HARNESS / "plugins" / "autosci" / "tests" / "fixtures" / "skillgen_operator_smoke_paper.md"


def run_shim(tmp_path: Path, *args: str, extra_env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["HARNESS_DIR"] = str(tmp_path)
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [sys.executable, str(SHIM), *args],
        cwd=HARNESS,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def run_gate(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(GATE), str(path)],
        cwd=HARNESS,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def write_pdf(path: Path, text: str) -> None:
    fitz = pytest.importorskip("fitz")
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text, fontsize=11)
    doc.save(path)
    doc.close()


def test_autosci_skill_shim_lists_configured_skills(tmp_path: Path) -> None:
    proc = run_shim(tmp_path, "skills", "list")
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["ok"] is True
    assert payload["count"] == 28
    skills = {item["skill"]: item for item in payload["skills"]}
    assert skills["ingest"]["solar_backend_action"] == "ingest_paper"
    assert skills["research"]["side_effect_policy"] == "approval_required"


def test_autosci_skill_shim_lists_skills_with_dollar_alias(tmp_path: Path) -> None:
    proc = run_shim(tmp_path, "$skills")
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["ok"] is True
    assert payload["count"] == 28
    assert {item["skill"] for item in payload["skills"]} >= {"ingest", "research", "poster"}


def test_autosci_skill_shim_runs_ingest_and_gate(tmp_path: Path) -> None:
    proc = run_shim(
        tmp_path,
        "skill",
        "ingest",
        "--paper",
        str(PAPER),
        "--smoke",
        "--run-id",
        "shim-ingest",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "ingest"
    assert summary["execution_status"] == "partial"
    assert summary["action_count"] == 2
    assert summary["workspace_updated_count"] > 0

    evidence_path = Path(summary["evidence_path"])
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    actions = payload["outputs"]["skill_run"]["actions"]
    assert [action["action"] for action in actions] == ["ingest_paper", "analyze_paper"]
    assert Path(actions[0]["evidence_path"]).exists()
    workspace = payload["outputs"]["skill_run"]["workspace"]
    assert Path(workspace["wiki_root"]).exists()
    assert (
        tmp_path
        / "artifacts/autosci/workspace/wiki/papers/paper-skillgen-operator-smoke-paper.md"
    ).exists()
    assert (tmp_path / "artifacts/autosci/workspace/wiki/index.md").exists()

    gate = run_gate(evidence_path)
    assert gate.returncode == 0, gate.stdout + gate.stderr


def test_autosci_skill_shim_runs_ingest_with_dollar_skill_alias(tmp_path: Path) -> None:
    proc = run_shim(
        tmp_path,
        "$skill",
        "ingest",
        "--paper",
        str(PAPER),
        "--smoke",
        "--run-id",
        "shim-dollar-skill-ingest",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "ingest"
    assert summary["execution_status"] == "partial"
    assert summary["action_count"] == 2


def test_autosci_skill_shim_runs_direct_dollar_skill(tmp_path: Path) -> None:
    proc = run_shim(
        tmp_path,
        "$ingest",
        "--paper",
        str(PAPER),
        "--smoke",
        "--run-id",
        "shim-dollar-ingest",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "ingest"
    assert summary["execution_status"] == "partial"
    assert summary["action_count"] == 2


def test_autosci_skill_shim_runs_single_token_dollar_command_with_flags(tmp_path: Path) -> None:
    proc = run_shim(
        tmp_path,
        "$survey --format latex --topic test --smoke --run-id shim-single-token-dollar-command",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "survey"
    assert summary["execution_status"] == "partial"
    assert summary["action_count"] > 0


def test_autosci_skill_shim_runs_text_dollar_command(tmp_path: Path) -> None:
    command = " ".join(
        [
            "$ingest",
            "--paper",
            shlex.quote(str(PAPER)),
            "--smoke",
            "--run-id",
            "shim-text-dollar-ingest",
        ]
    )
    proc = run_shim(tmp_path, "text", command)
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "ingest"
    assert summary["execution_status"] == "partial"
    assert summary["action_count"] == 2


def test_autosci_skill_shim_maps_positional_ingest_source(tmp_path: Path) -> None:
    proc = run_shim(
        tmp_path,
        "$ingest",
        str(PAPER),
        "--run-id",
        "shim-positional-ingest",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "ingest"
    assert summary["execution_status"] == "partial"
    assert summary["action_count"] == 2

    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    assert payload["inputs"]["paper_path"] == str(PAPER)
    action = payload["outputs"]["skill_run"]["actions"][0]
    paper = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    assert "Fixture abstract" not in json.dumps(paper)
    assert "SKILLGEN" in paper["outputs"]["paper"]["title"]
    artifact_paths = [artifact["path"] for artifact in paper["artifacts"]]
    assert not any("/OpenSolar/harness/artifacts/autosci/workspace/raw" in path for path in artifact_paths)


def test_autosci_skill_shim_ingests_pdf_with_extracted_text_and_no_fixture_leakage(tmp_path: Path) -> None:
    pdf_path = tmp_path / "raw" / "papers" / "SkillGen.pdf"
    write_pdf(
        pdf_path,
        "SKILLGEN: Verified Inference-Time Agent Skill Synthesis\n"
        "arXiv: 2601.00001\n"
        "Abstract\n"
        "This PDF describes inference-time skill synthesis with verifier gates and measurable gains.\n"
        "1. Introduction\n"
        "The pipeline trains reusable agent skills and evaluates repairs, regressions, and net gain.",
    )
    proc = run_shim(
        tmp_path,
        "$ingest",
        str(pdf_path),
        "--run-id",
        "shim-pdf-ingest-source-grounded",
        extra_env={"AUTOSCI_DISABLE_NETWORK_FETCH": "1"},
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "ingest"
    assert summary["execution_status"] == "partial"
    assert summary["action_count"] == 2

    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    assert action["gate_status"] == "passed"
    evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    paper = evidence["outputs"]["paper"]
    preparation = paper["preparation"]
    assert evidence["status"] == "completed"
    assert preparation["original_format"] == "pdf"
    assert preparation["extracted_text_path"]
    assert preparation["source_fetch_status"] == "skipped_network_disabled"
    assert paper["parse_status"] == "parsed"
    assert "SKILLGEN" in paper["title"]
    assert "Fixture abstract" not in json.dumps(evidence)
    artifact_types = {artifact["type"] for artifact in evidence["artifacts"]}
    assert {"extracted_pdf_text", "synthetic_latex"} <= artifact_types
    prepared_paths = [
        artifact["path"]
        for artifact in evidence["artifacts"]
        if artifact["type"] in {"extracted_pdf_text", "synthetic_latex"}
    ]
    assert all(path.startswith("artifacts/autosci/workspace/raw/tmp/papers/") for path in prepared_paths)


def test_autosci_skill_shim_accepts_original_ingest_followup_flags(tmp_path: Path) -> None:
    command = " ".join(
        [
            "$ingest",
            shlex.quote(str(PAPER)),
            "--discover",
            "--visualize",
            "--run-id",
            "shim-ingest-followup-flags",
        ]
    )
    proc = run_shim(tmp_path, "text", command)
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "ingest"
    assert summary["action_count"] == 2

    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    options = payload["inputs"]["native_options"]
    assert options["discover"] is True
    assert options["visualize"] is True


def test_autosci_skill_shim_accepts_discover_from_wiki_limit(tmp_path: Path) -> None:
    wiki_papers = tmp_path / "artifacts/autosci/workspace/wiki/papers"
    wiki_papers.mkdir(parents=True)
    wiki_papers.joinpath("seed.md").write_text(
        "---\ntitle: SkillGen Seed\narxiv: 2401.00001\n---\n# SkillGen Seed\n",
        encoding="utf-8",
    )
    env = dict(os.environ)
    env["HARNESS_DIR"] = str(tmp_path)
    env["AUTOSCI_DISABLE_NETWORK_FETCH"] = "1"
    proc = subprocess.run(
        [
            sys.executable,
            str(SHIM),
            "$discover",
            "--from-wiki",
            "--limit",
            "10",
            "--run-id",
            "shim-discover-from-wiki",
        ],
        cwd=HARNESS,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "discover"
    assert summary["execution_status"] == "partial"
    evidence_path = Path(summary["evidence_path"])
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    discovery = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    assert discovery["status"] == "inconclusive"
    assert discovery["outputs"]["mode"] == "wiki"
    assert discovery["outputs"]["limit"] == 10
    assert discovery["outputs"]["candidates"] == []
    assert "local_fixture" not in json.dumps(discovery)


def test_autosci_skill_shim_runs_research_pipeline(tmp_path: Path) -> None:
    proc = run_shim(
        tmp_path,
        "skill",
        "research",
        "--paper",
        str(PAPER),
        "--topic",
        "agent skill learning",
        "--smoke",
        "--run-id",
        "shim-research",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "research"
    assert summary["execution_status"] == "gated"
    assert summary["action_count"] == 16
    assert summary["failed_count"] == 0

    evidence_path = Path(summary["evidence_path"])
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    actions = [item["action"] for item in payload["outputs"]["skill_run"]["actions"]]
    assert actions == [
        "ingest_paper",
        "analyze_paper",
        "update_memory",
        "update_graph",
        "discover_literature",
        "extract_claims",
        "extract_methods",
        "map_code_evidence",
        "generate_ideas",
        "evaluate_ideas",
        "design_experiment",
        "run_experiment",
        "monitor_experiment",
        "verify_claim",
        "write_report",
        "evolve_workflow",
    ]
    assert (tmp_path / "artifacts/autosci/runs/shim-research/report.md").exists()
    assert (tmp_path / "artifacts/autosci/runs/shim-research/publication_bundle.json").exists()
    assert (tmp_path / "artifacts/autosci/workspace/wiki/ideas/idea-001.md").exists()
    assert (tmp_path / "artifacts/autosci/workspace/wiki/experiments/exp-001.md").exists()
    assert (tmp_path / "artifacts/autosci/workspace/wiki/outputs/report-skillgen-operator-smoke.md").exists()

    gate = run_gate(evidence_path)
    assert gate.returncode == 0, gate.stdout + gate.stderr


def test_autosci_skill_shim_research_start_from_writes_pipeline_artifacts(tmp_path: Path) -> None:
    proc = run_shim(
        tmp_path,
        "$research",
        "skillgen-main",
        "--venue",
        "ICLR",
        "--start-from",
        "stage3-collect",
        "--skip-paper",
        "--run-id",
        "shim-research-start-from",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "research"
    assert summary["execution_status"] == "gated"
    assert summary["action_count"] == 1
    assert summary["schema_only_count"] == 1

    progress = tmp_path / "artifacts/autosci/workspace/wiki/outputs/pipeline-progress.md"
    report = tmp_path / "artifacts/autosci/workspace/wiki/outputs/PIPELINE_REPORT.md"
    state_path = tmp_path / "artifacts/autosci/workspace/wiki/outputs/pipeline-state.json"
    assert progress.exists()
    assert report.exists()
    assert state_path.exists()
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["pipeline"]["target"] == "skillgen-main"
    assert state["pipeline"]["venue"] == "ICLR"
    assert state["pipeline"]["resume_from"] == "collect"
    assert state["pipeline"]["skip_paper"] is True

    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    assert payload["inputs"]["native_options"]["start_from"] == "stage3-collect"
    assert payload["inputs"]["native_options"]["skip_paper"] is True
    action = payload["outputs"]["skill_run"]["actions"][0]
    assert action["action"] == "run_research_lifecycle"
    assert action["schema"] == "workflow_evolution.v1"
    assert action["gate_status"] == "schema_only"
    evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    evolution = evidence["outputs"]["evolution"]
    assert evidence["status"] == "inconclusive"
    assert evolution["current_stage"] == "collect"
    assert any(artifact["type"] == "pipeline_progress_markdown" for artifact in evidence["artifacts"])
    assert any(artifact["type"] == "pipeline_report_markdown" for artifact in evidence["artifacts"])
    assert any(artifact["type"] == "pipeline_state_json" for artifact in evidence["artifacts"])


def test_autosci_skill_shim_research_lifecycle_completes_from_verified_stage_evidence(tmp_path: Path) -> None:
    wiki_root = tmp_path / "artifacts/autosci/workspace/wiki"
    for folder in ("papers", "ideas", "experiments", "outputs"):
        (wiki_root / folder).mkdir(parents=True, exist_ok=True)
    (wiki_root / "papers/paper-skillgen.md").write_text("# SkillGen Paper\n", encoding="utf-8")
    (wiki_root / "ideas/idea-skillgen.md").write_text("# SkillGen Idea\n", encoding="utf-8")
    (wiki_root / "experiments/exp-skillgen.md").write_text("# SkillGen Experiment\nstatus: completed\n", encoding="utf-8")
    (wiki_root / "outputs/paper-plan.md").write_text("# Paper Plan\n", encoding="utf-8")
    paper = tmp_path / "source-paper.md"
    paper.write_text("# Source Paper\nEvidence-backed source.\n", encoding="utf-8")
    allowlist = tmp_path / "research-allowlist.json"
    before = tmp_path / "research-before.json"
    after = tmp_path / "research-after.json"
    pdf = tmp_path / "paper-main.pdf"
    allowlist.write_text(json.dumps({"approved": True, "scope": "research lifecycle"}), encoding="utf-8")
    before.write_text(json.dumps({"state": "before"}), encoding="utf-8")
    after.write_text(json.dumps({"state": "after"}), encoding="utf-8")
    pdf.write_text("%PDF-1.4\n", encoding="utf-8")

    discovery = tmp_path / "discovery.json"
    discovery.write_text(
        json.dumps(
            {
                "schema": "literature_discovery.v1",
                "status": "completed",
                "outputs": {"candidates": [{"candidate_id": "paper:1", "title": "Prior Work"}]},
            }
        ),
        encoding="utf-8",
    )
    novelty = tmp_path / "novelty.json"
    novelty.write_text(
        json.dumps({"schema": "external_novelty.v1", "status": "completed", "outputs": {"sources": [{"id": "web:1"}]}}),
        encoding="utf-8",
    )
    review = tmp_path / "review-llm.json"
    review.write_text(
        json.dumps(
            {
                "schema": "artifact_review.v1",
                "status": "completed",
                "outputs": {
                    "review": {
                        "review_mode": "review_llm",
                        "review_available": True,
                        "score": 0.74,
                        "recommendation": "revise",
                        "evidence_ids": ["review-llm:research"],
                        "review_llm": {"status": "completed"},
                    },
                    "findings": [],
                },
            }
        ),
        encoding="utf-8",
    )
    exp_runtime = tmp_path / "exp-runtime.json"
    exp_runtime.write_text(
        json.dumps(
            {
                "schema": "autosci_runtime_evidence.v1",
                "status": "completed",
                "outputs": {
                    "runtime": {
                        "action": "run_experiment",
                        "status": "completed",
                        "exit_code": 0,
                        "result_collected": True,
                        "outcome": "supports",
                        "metrics": [{"name": "accuracy", "value": 0.91}],
                        "evidence_ids": ["runtime:research-exp"],
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    compile_runtime = tmp_path / "compile-runtime.json"
    compile_runtime.write_text(
        json.dumps(
            {
                "schema": "autosci_runtime_evidence.v1",
                "status": "completed",
                "outputs": {
                    "runtime": {
                        "action": "compile_paper",
                        "status": "completed",
                        "exit_code": 0,
                        "pdf_generated": True,
                        "pdf_path": str(pdf),
                        "evidence_ids": ["runtime:research-compile"],
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    proc = run_shim(
        tmp_path,
        "$research",
        "skillgen-main",
        "--paper",
        str(paper),
        "--approval-ref",
        "approval-research",
        "--allowlist-evidence",
        str(allowlist),
        "--runtime-evidence",
        str(exp_runtime),
        "--runtime-evidence",
        str(compile_runtime),
        "--before-artifact",
        str(before),
        "--after-artifact",
        str(after),
        "--after-artifact",
        str(pdf),
        "--discovery-evidence",
        str(discovery),
        "--novelty-evidence",
        str(novelty),
        "--review-llm-evidence",
        str(review),
        "--run-id",
        "shim-research-verified-lifecycle",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "research"
    assert summary["action_count"] == 1
    assert summary["passed_count"] == 1

    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    assert action["action"] == "run_research_lifecycle"
    assert action["gate_status"] == "passed"
    evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    evolution = evidence["outputs"]["evolution"]
    assert evidence["status"] == "completed"
    assert evolution["pipeline"]["status"] == "completed"
    assert evolution["current_stage"] == "completed"
    assert {stage["state"] for stage in evolution["stage_plan"]} == {"completed"}
    state_path = tmp_path / "artifacts/autosci/workspace/wiki/outputs/pipeline-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["pipeline"]["status"] == "completed"
    assert state["evidence_report"]["review_llm_completed"] is True
    assert state["evidence_report"]["experiment_runtime"]["verified"] is True
    assert state["evidence_report"]["compile_runtime"]["verified"] is True
    assert state["evidence_report"]["integrated_pdf"]["status"] == "completed"
    assert (tmp_path / "artifacts/autosci/workspace/paper/main.pdf").exists()


def test_autosci_skill_shim_research_lifecycle_completes_from_scheduler_summary(tmp_path: Path) -> None:
    lifecycle_summary = tmp_path / "scientific-lifecycle-summary.json"
    required_nodes = [
        "literature_discover",
        "paper_ingest",
        "paper_analyze",
        "memory_update_initial",
        "graph_update",
        "claim_extract",
        "method_extract",
        "code_evidence_map",
        "idea_generate",
        "idea_evaluate",
        "experiment_design",
        "experiment_run",
        "experiment_monitor",
        "claim_verify",
        "report_draft",
        "artifact_review",
        "memory_update_final",
        "workflow_evolve",
        "report_plan",
        "publication_produce",
    ]
    lifecycle_summary.write_text(
        json.dumps(
            {
                "schema": "scientific_lifecycle.v1",
                "workflow_id": "scientific_research_lifecycle_full_v1",
                "job_id": "job-scheduler-lifecycle-proof",
                "sprint_id": "job-scheduler-lifecycle-proof",
                "lifecycle_status": "passed",
                "required_nodes": required_nodes,
                "node_results": {
                    node_id: {
                        "node_id": node_id,
                        "status": "passed",
                    }
                    for node_id in required_nodes
                },
                "gate_results": {
                    node_id: {
                        "node_id": node_id,
                        "status": "passed",
                        "ok": True,
                    }
                    for node_id in required_nodes
                },
                "blocked_nodes": {},
                "lifecycle_gate_result": {"ok": True, "status": "passed"},
            }
        ),
        encoding="utf-8",
    )

    proc = run_shim(
        tmp_path,
        "$research",
        "skillgen-main",
        "--lifecycle-summary",
        str(lifecycle_summary),
        "--run-id",
        "shim-research-scheduler-summary",
    )

    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "research"
    assert summary["passed_count"] == 1

    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    assert action["action"] == "run_research_lifecycle"
    assert action["gate_status"] == "passed"
    evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    evolution = evidence["outputs"]["evolution"]
    assert evidence["status"] == "completed"
    assert evolution["pipeline"]["status"] == "completed"
    assert {stage["state"] for stage in evolution["stage_plan"]} == {"completed"}
    state_artifact = next(artifact for artifact in evidence["artifacts"] if artifact["type"] == "pipeline_state_json")
    state = json.loads((tmp_path / state_artifact["path"]).read_text(encoding="utf-8"))
    assert state["evidence_report"]["scheduler_lifecycle_completed"] is True
    assert state["evidence_report"]["scheduler_lifecycle"]["node_count"] == len(required_nodes)


def test_autosci_skill_shim_accepts_exp_run_native_options_without_fixture_fallback(tmp_path: Path) -> None:
    proc = run_shim(
        tmp_path,
        "$exp-run",
        "exp-001",
        "--env",
        "local",
        "--collect",
        "--run-id",
        "shim-exp-run-native",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "exp-run"
    assert summary["execution_status"] == "gated"
    assert summary["action_count"] == 1
    assert summary["schema_only_count"] == 1

    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    assert payload["inputs"]["target"] == "exp-001"
    assert payload["inputs"]["paper_path"] == ""
    assert payload["inputs"]["smoke"] is False
    assert payload["inputs"]["native_options"]["env"] == "local"
    assert payload["inputs"]["native_options"]["collect"] is True
    action = payload["outputs"]["skill_run"]["actions"][0]
    assert action["action"] == "monitor_experiment"
    assert action["schema"] == "experiment_status.v1"
    assert action["gate_status"] == "schema_only"
    status_evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    report = status_evidence["outputs"]["status_report"]
    assert status_evidence["status"] == "inconclusive"
    assert report["experiment_id"] == "exp-001"
    assert report["state"] == "unknown"
    assert any("Collect mode was requested" in item for item in report["observations"])
    assert any("Approval-gated external effects" in item for item in payload["limitations"])


def test_autosci_skill_shim_exp_status_pipeline_runs_monitor_action(tmp_path: Path) -> None:
    proc = run_shim(
        tmp_path,
        "$exp-status",
        "--pipeline",
        "skillgen-main",
        "--run-id",
        "shim-exp-status-pipeline",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "exp-status"
    assert summary["execution_status"] == "partial"
    assert summary["action_count"] == 1
    assert summary["schema_only_count"] == 1

    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    assert payload["inputs"]["native_options"]["pipeline"] == "skillgen-main"
    action = payload["outputs"]["skill_run"]["actions"][0]
    assert action["action"] == "monitor_experiment"
    status_evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    report = status_evidence["outputs"]["status_report"]
    assert status_evidence["status"] == "inconclusive"
    assert report["experiment_id"] == "skillgen-main"


def test_autosci_skill_shim_exp_status_pipeline_reads_wiki_experiment_state(tmp_path: Path) -> None:
    wiki_root = tmp_path / "artifacts/autosci/workspace/wiki"
    experiments = wiki_root / "experiments"
    logs = wiki_root / "logs"
    experiments.mkdir(parents=True)
    logs.mkdir(parents=True)
    (logs / "exp-skillgen.log").write_text("completed run\n", encoding="utf-8")
    (experiments / "exp-skillgen.md").write_text(
        "\n".join(
            [
                "---",
                "title: SkillGen Experiment",
                "experiment_id: exp-skillgen",
                "pipeline: skillgen-main",
                "status: completed",
                "outcome: supports",
                "run_log: ../logs/exp-skillgen.log",
                "evidence_ids:",
                "  - runtime:exp-skillgen",
                "---",
                "# SkillGen Experiment",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    proc = run_shim(
        tmp_path,
        "$exp-status",
        "--pipeline",
        "skillgen-main",
        "--run-id",
        "shim-exp-status-wiki-state",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "exp-status"
    assert summary["action_count"] == 1
    assert summary["passed_count"] == 1
    assert summary["schema_only_count"] == 0

    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    assert action["action"] == "monitor_experiment"
    assert action["gate_status"] == "passed"
    status_evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    report = status_evidence["outputs"]["status_report"]
    assert status_evidence["status"] == "completed"
    assert report["experiment_id"] == "exp-skillgen"
    assert report["state"] == "completed"
    assert "runtime:exp-skillgen" in report["evidence_ids"]
    artifact_types = {artifact["type"] for artifact in status_evidence["artifacts"]}
    assert {"wiki_state_resolver_json", "wiki_experiment_markdown", "wiki_experiment_run_log"} <= artifact_types


def test_autosci_skill_shim_blocks_unapproved_exp_run_deploy_without_fixture_support(tmp_path: Path) -> None:
    proc = run_shim(
        tmp_path,
        "$exp-run",
        "exp-skillgen",
        "--review",
        "--env",
        "local",
        "--run-id",
        "shim-exp-run-deploy-native",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "exp-run"
    assert summary["execution_status"] == "gated"
    assert summary["action_count"] > 1

    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    actions = payload["outputs"]["skill_run"]["actions"]
    plan_action = next(action for action in actions if action["action"] == "design_experiment")
    plan = json.loads(Path(plan_action["evidence_path"]).read_text(encoding="utf-8"))
    experiment_plan = plan["outputs"]["experiment_plan"]
    assert experiment_plan["execution_mode"] == "human_approved"
    assert "approval-gated native experiment" in experiment_plan["objective"]
    assert "fixture" not in json.dumps(experiment_plan).lower()
    result_action = next(action for action in actions if action["action"] == "run_experiment")
    result = json.loads(Path(result_action["evidence_path"]).read_text(encoding="utf-8"))
    experiment_result = result["outputs"]["result"]
    assert result["status"] == "inconclusive"
    assert experiment_result["outcome"] == "inconclusive"
    assert experiment_result["execution_mode"] == "human_approved"
    assert "fixture result collected" not in "\n".join(experiment_result["logs"])
    assert "evidence:autosci-fixture-result" not in json.dumps(experiment_result)
    assert any("approval is required and absent" in item for item in result["limitations"])


def test_autosci_skill_shim_exp_design_attaches_review_llm_validation(tmp_path: Path) -> None:
    review = tmp_path / "exp-design-review.json"
    review.write_text(
        json.dumps(
            {
                "schema": "artifact_review.v1",
                "task_id": "review-exp-design",
                "status": "completed",
                "outputs": {
                    "review": {
                        "artifact_id": "artifact:idea-skillgen-design",
                        "target": "idea-skillgen-design",
                        "review_mode": "review_llm",
                        "review_available": True,
                        "difficulty": "hard",
                        "focus": "method",
                        "score": 0.84,
                        "recommendation": "pass_with_caveats",
                        "evidence_ids": ["review:exp-design"],
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    proc = run_shim(
        tmp_path,
        "$exp-design",
        "idea-skillgen-design",
        "--review-llm-evidence",
        str(review),
        "--run-id",
        "shim-exp-design-review-llm",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "exp-design"
    assert summary["action_count"] == 1

    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    assert action["action"] == "design_experiment"
    assert action["schema"] == "experiment_plan.v1"
    assert action["gate_status"] == "passed"
    evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    plan = evidence["outputs"]["experiment_plan"]
    assert plan["experiment_id"] == "exp-idea-skillgen-design"
    assert plan["review_llm"]["status"] == "completed"
    assert plan["review_llm"]["recommendation"] == "pass_with_caveats"
    assert "review-exp-design" in plan["evidence_ids"]
    assert "review_llm_design_validation == completed" in plan["success_criteria"]
    assert any(artifact["type"] == "experiment_design_review_llm_evidence_json" for artifact in evidence["artifacts"])


def test_autosci_skill_shim_exp_run_uses_verified_runtime_evidence_and_mutates_wiki(tmp_path: Path) -> None:
    allowlist = tmp_path / "exp-allowlist.json"
    runtime = tmp_path / "exp-runtime.json"
    before = tmp_path / "exp-before.json"
    after = tmp_path / "exp-after.json"
    allowlist.write_text(json.dumps({"approved": True, "scope": "exp-approved"}), encoding="utf-8")
    before.write_text(json.dumps({"state": "planned"}), encoding="utf-8")
    after.write_text(json.dumps({"state": "completed"}), encoding="utf-8")
    runtime.write_text(
        json.dumps(
            {
                "schema": "autosci_runtime_evidence.v1",
                "task_id": "task-exp-approved-runtime",
                "sprint_id": "sprint-exp-approved-runtime",
                "node_id": "node-exp-approved-runtime",
                "status": "completed",
                "inputs": {"approval_ref": "approval-exp-approved"},
                "outputs": {
                    "runtime": {
                        "action": "run_experiment",
                        "status": "completed",
                        "approval_ref": "approval-exp-approved",
                        "exit_code": 0,
                        "command_run": "python run_exp.py --experiment exp-approved",
                        "outcome": "supports",
                        "result_collected": True,
                        "metrics": [{"name": "accuracy", "value": 0.91}],
                        "evidence_ids": ["runtime:exp-approved"],
                        "logs": ["approved experiment runtime completed"],
                    }
                },
                "artifacts": [{"type": "runtime_after", "path": str(after)}],
                "provenance": {
                    "operator_id": "test",
                    "implementation_package": "test",
                    "timestamp": "2026-06-24T00:00:00Z",
                },
                "limitations": [],
            }
        ),
        encoding="utf-8",
    )

    proc = run_shim(
        tmp_path,
        "$exp-run",
        "exp-approved",
        "--review",
        "--env",
        "local",
        "--approval-ref",
        "approval-exp-approved",
        "--allowlist-evidence",
        str(allowlist),
        "--runtime-evidence",
        str(runtime),
        "--before-artifact",
        str(before),
        "--after-artifact",
        str(after),
        "--run-id",
        "shim-exp-run-runtime-verified",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "exp-run"
    assert summary["execution_status"] == "gated"

    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    actions = payload["outputs"]["skill_run"]["actions"]
    result_action = next(action for action in actions if action["action"] == "run_experiment")
    assert result_action["status"] == "passed"
    result = json.loads(Path(result_action["evidence_path"]).read_text(encoding="utf-8"))
    experiment_result = result["outputs"]["result"]
    assert result["status"] == "completed"
    assert experiment_result["experiment_id"] == "exp-approved"
    assert experiment_result["outcome"] == "supports"
    assert experiment_result["metrics"] == [{"name": "accuracy", "value": 0.91}]
    assert experiment_result["command_run"] == "python run_exp.py --experiment exp-approved"
    assert "runtime:exp-approved" in experiment_result["evidence_ids"]
    assert "fixture result collected" not in "\n".join(experiment_result["logs"]).lower()
    artifact_types = {artifact["type"] for artifact in result["artifacts"]}
    assert {
        "approval_contract_json",
        "experiment_runtime_evidence_json",
        "wiki_experiment_state",
        "wiki_log",
        "wiki_graph_edges",
    }.issubset(artifact_types)

    state_path = tmp_path / "artifacts/autosci/workspace/wiki/experiments/exp-approved.md"
    assert state_path.exists()
    state_text = state_path.read_text(encoding="utf-8")
    assert "status: completed" in state_text
    assert "outcome: supports" in state_text
    assert "runtime:exp-approved" in state_text
    assert "produced_result" in (tmp_path / "artifacts/autosci/workspace/wiki/graph/edges.jsonl").read_text(encoding="utf-8")
    assert "completed `exp-approved`" in (tmp_path / "artifacts/autosci/workspace/wiki/log.md").read_text(encoding="utf-8")


def test_autosci_skill_shim_exp_run_executes_approved_native_command(tmp_path: Path) -> None:
    allowlist = tmp_path / "exp-native-allowlist.json"
    before = tmp_path / "exp-native-before.json"
    after = tmp_path / "exp-native-after.json"
    marker = tmp_path / "exp-native-marker.txt"
    marker_command_script = tmp_path / "exp_native_command.py"
    before.write_text(json.dumps({"state": "planned", "approved": True}), encoding="utf-8")
    after.write_text(json.dumps({"state": "completed", "approved": True}), encoding="utf-8")
    marker_command_script.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import argparse",
                "from pathlib import Path",
                "import json",
                "",
                "parser = argparse.ArgumentParser()",
                "parser.add_argument('--experiment-id', required=True)",
                "parser.add_argument('--marker', required=True)",
                "args = parser.parse_args()",
                "Path(args.marker).write_text('executed', encoding='utf-8')",
                "payload = {",
                "    'schema': 'experiment_result.v1',",
                "    'task_id': 'task-exp-native-run',",
                "    'sprint_id': 'sprint-exp-native-run',",
                "    'node_id': 'node-exp-native-run',",
                "    'status': 'completed',",
                "    'inputs': {'experiment_id': args.experiment_id},",
                "    'outputs': {",
                "        'result': {",
                "            'experiment_id': args.experiment_id,",
                "            'outcome': 'supports',",
                "            'metrics': [",
                "                {'name': 'f1', 'value': 0.88},",
                "            ],",
                "            'evidence_ids': ['runtime:exp-native'],",
                "            'logs': ['native command executed'],",
                "        }",
                "    },",
                "    'artifacts': [",
                "        {'type': 'experiment_runtime_output_json', 'path': str(args.marker), 'label': 'marker'},",
                "    ],",
                "    'provenance': {",
                "        'operator_id': 'test-script',",
                "        'implementation_package': 'test',",
                "        'timestamp': '2026-06-24T00:00:00Z',",
                "    },",
                "    'limitations': [],",
                "}",
                "print(json.dumps(payload))",
            ]
        ),
        encoding="utf-8",
    )
    marker_command_script.chmod(0o755)
    allowlist.write_text(
        json.dumps(
            {
                "commands": [
                    " ".join(
                        [
                            str(sys.executable),
                            str(marker_command_script),
                            "--experiment-id",
                            "{experiment_id}",
                            "--marker",
                            str(marker),
                        ]
                    )
                ],
            }
        ),
        encoding="utf-8",
    )

    proc = run_shim(
        tmp_path,
        "$exp-run",
        "exp-native-001",
        "--review",
        "--env",
        "local",
        "--approval-ref",
        "approval-exp-native-001",
        "--allowlist-evidence",
        str(allowlist),
        "--before-artifact",
        str(before),
        "--after-artifact",
        str(after),
        "--execute-approved",
        "--run-id",
        "shim-exp-run-native-command",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "exp-run"
    assert summary["execution_status"] == "gated"

    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = next(action for action in payload["outputs"]["skill_run"]["actions"] if action["action"] == "run_experiment")
    assert action["status"] == "passed"
    result = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    experiment_result = result["outputs"]["result"]
    assert result["status"] == "completed"
    assert experiment_result["experiment_id"] == "exp-native-001"
    assert experiment_result["outcome"] == "supports"
    assert "runtime:exp-native" in experiment_result["evidence_ids"]
    assert marker.exists()
    assert marker.read_text(encoding="utf-8") == "executed"
    assert "native command executed" in " ".join(experiment_result["logs"])
    assert "python" in experiment_result["command_run"]
    artifact_types = {artifact["type"] for artifact in result["artifacts"]}
    assert {
        "approval_contract_json",
        "experiment_runtime_evidence_json",
        "run_experiment_result_json",
        "executor_stdout",
        "executor_stderr",
    }.issubset(artifact_types)

    state_path = tmp_path / "artifacts/autosci/workspace/wiki/experiments/exp-native-001.md"
    state_text = state_path.read_text(encoding="utf-8")
    assert "status: completed" in state_text
    assert "outcome: supports" in state_text
    assert "runtime:exp-native" in state_text


def test_autosci_skill_shim_exp_collect_uses_verified_runtime_evidence(tmp_path: Path) -> None:
    allowlist = tmp_path / "collect-allowlist.json"
    runtime = tmp_path / "collect-runtime.json"
    before = tmp_path / "collect-before.json"
    after = tmp_path / "collect-after.json"
    allowlist.write_text(json.dumps({"approved": True, "scope": "exp-collect"}), encoding="utf-8")
    before.write_text(json.dumps({"state": "running"}), encoding="utf-8")
    after.write_text(json.dumps({"state": "completed"}), encoding="utf-8")
    runtime.write_text(
        json.dumps(
            {
                "schema": "autosci_runtime_evidence.v1",
                "task_id": "task-exp-collect-runtime",
                "sprint_id": "sprint-exp-collect-runtime",
                "node_id": "node-exp-collect-runtime",
                "status": "completed",
                "inputs": {"approval_ref": "approval-exp-collect"},
                "outputs": {
                    "runtime": {
                        "action": "run_experiment",
                        "status": "completed",
                        "approval_ref": "approval-exp-collect",
                        "exit_code": 0,
                        "command_run": "python collect_exp.py --experiment exp-collect",
                        "outcome": "partially_supports",
                        "result_collected": True,
                        "metrics": [{"name": "f1", "value": 0.77}],
                        "evidence_ids": ["runtime:exp-collect"],
                        "logs": ["approved collect completed"],
                    }
                },
                "artifacts": [{"type": "runtime_after", "path": str(after)}],
                "provenance": {
                    "operator_id": "test",
                    "implementation_package": "test",
                    "timestamp": "2026-06-24T00:00:00Z",
                },
                "limitations": [],
            }
        ),
        encoding="utf-8",
    )

    proc = run_shim(
        tmp_path,
        "$exp-run",
        "exp-collect",
        "--collect",
        "--approval-ref",
        "approval-exp-collect",
        "--allowlist-evidence",
        str(allowlist),
        "--runtime-evidence",
        str(runtime),
        "--before-artifact",
        str(before),
        "--after-artifact",
        str(after),
        "--run-id",
        "shim-exp-collect-runtime-verified",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "exp-run"
    assert summary["action_count"] == 1

    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    assert action["action"] == "monitor_experiment"
    assert action["status"] == "passed"
    evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    report = evidence["outputs"]["status_report"]
    assert evidence["status"] == "completed"
    assert report["experiment_id"] == "exp-collect"
    assert report["state"] == "completed"
    assert "runtime:exp-collect" in report["evidence_ids"]
    artifact_types = {artifact["type"] for artifact in evidence["artifacts"]}
    assert {"approval_contract_json", "experiment_runtime_evidence_json", "wiki_experiment_state"}.issubset(artifact_types)
    state_text = (tmp_path / "artifacts/autosci/workspace/wiki/experiments/exp-collect.md").read_text(encoding="utf-8")
    assert "status: completed" in state_text
    assert "outcome: partially_supports" in state_text
    assert "runtime:exp-collect" in state_text


def test_autosci_skill_shim_accepts_paper_plan_title_without_topic_fallback(tmp_path: Path) -> None:
    proc = run_shim(
        tmp_path,
        "$paper-plan",
        "idea-001",
        "--venue",
        "ICLR",
        "--title",
        "Skill Generation for Inference-Time Agents",
        "--run-id",
        "shim-paper-plan-native",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "paper-plan"
    assert summary["execution_status"] == "partial"
    assert summary["action_count"] == 1
    assert summary["schema_only_count"] == 1

    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    assert payload["inputs"]["target"] == "idea-001"
    assert payload["inputs"]["venue"] == "ICLR"
    assert payload["inputs"]["native_options"]["title"] == "Skill Generation for Inference-Time Agents"
    assert payload["inputs"]["topic"] == ""
    action = payload["outputs"]["skill_run"]["actions"][0]
    assert action["action"] == "plan_report"
    assert action["schema"] == "scientific_report.v1"
    report_evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    report = report_evidence["outputs"]["report"]
    assert report_evidence["status"] == "inconclusive"
    assert report["title"] == "Skill Generation for Inference-Time Agents"
    assert any(section["section_id"] == "review-gates" for section in report["sections"])
    assert (tmp_path / "artifacts/autosci/runs/shim-paper-plan-native/paper_plan.md").exists()


def test_autosci_skill_shim_paper_plan_completes_with_citations_and_review_llm(tmp_path: Path) -> None:
    discovery = tmp_path / "discovery.json"
    discovery.write_text(
        json.dumps(
            {
                "schema": "literature_discovery.v1",
                "task_id": "lit-skillgen",
                "status": "completed",
                "outputs": {
                    "query": "skill generation",
                    "candidates": [
                        {
                            "candidate_id": "arxiv:2601.00001",
                            "title": "SkillGen: Generating Skills for Agents",
                            "arxiv_id": "2601.00001",
                            "source_ref": "https://arxiv.org/abs/2601.00001",
                            "source_channels": ["search_s2"],
                        }
                    ],
                },
            }
        ),
        encoding="utf-8",
    )
    review = tmp_path / "review-llm.json"
    review.write_text(
        json.dumps(
            {
                "schema": "artifact_review.v1",
                "task_id": "review-paper-plan",
                "status": "completed",
                "outputs": {
                    "review": {
                        "review_available": True,
                        "review_mode": "review_llm",
                        "score": 0.82,
                        "recommendation": "accept",
                        "evidence_ids": ["review:paper-plan"],
                        "findings": [],
                        "review_llm": {"status": "completed"},
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    proc = run_shim(
        tmp_path,
        "$paper-plan",
        "idea-skillgen",
        "--title",
        "SkillGen Plan",
        "--discovery-evidence",
        str(discovery),
        "--review-llm-evidence",
        str(review),
        "--run-id",
        "shim-paper-plan-citation-review",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "paper-plan"
    assert summary["action_count"] == 1

    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    assert evidence["status"] == "completed"
    report = evidence["outputs"]["report"]
    figure_plan = next(section for section in report["sections"] if section["section_id"] == "figure-citation-plan")
    assert "SkillGen: Generating Skills for Agents" in figure_plan["body"]
    artifacts = {artifact["type"]: artifact["path"] for artifact in evidence["artifacts"]}
    citation_map = json.loads((tmp_path / artifacts["citation_map_json"]).read_text(encoding="utf-8"))
    assert citation_map["status"] == "completed"
    assert citation_map["citation_count"] == 1
    plan_json = json.loads((tmp_path / artifacts["paper_plan_json"]).read_text(encoding="utf-8"))
    assert plan_json["review_llm_completed"] is True


def test_autosci_skill_shim_paper_plan_attaches_verified_compile_handoff(tmp_path: Path) -> None:
    discovery = tmp_path / "discovery.json"
    discovery.write_text(
        json.dumps(
            {
                "schema": "literature_discovery.v1",
                "task_id": "lit-skillgen-plan-compile",
                "status": "completed",
                "outputs": {
                    "query": "skill generation",
                    "candidates": [
                        {
                            "candidate_id": "arxiv:2601.00001",
                            "title": "SkillGen: Generating Skills for Agents",
                            "arxiv_id": "2601.00001",
                            "source_ref": "https://arxiv.org/abs/2601.00001",
                        }
                    ],
                },
            }
        ),
        encoding="utf-8",
    )
    review = tmp_path / "review-llm.json"
    review.write_text(
        json.dumps(
            {
                "schema": "artifact_review.v1",
                "task_id": "review-paper-plan-compile",
                "status": "completed",
                "outputs": {
                    "review": {
                        "review_available": True,
                        "review_mode": "review_llm",
                        "recommendation": "accept",
                        "evidence_ids": ["review:paper-plan-compile"],
                        "review_llm": {"status": "completed"},
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    compiled_dir = tmp_path / "compiled-plan"
    compiled_dir.mkdir()
    pdf = compiled_dir / "main.pdf"
    pdf.write_text("%PDF-1.4\n", encoding="utf-8")
    before = tmp_path / "paper-plan-before.json"
    allowlist = tmp_path / "paper-plan-allowlist.json"
    runtime = tmp_path / "paper-plan-compile-runtime.json"
    before.write_text(json.dumps({"plan": "before"}), encoding="utf-8")
    allowlist.write_text(json.dumps({"approved": True, "scope": "paper-plan-compile-handoff"}), encoding="utf-8")
    runtime.write_text(
        json.dumps(
            {
                "schema": "autosci_runtime_evidence.v1",
                "task_id": "paper-plan-compile-runtime",
                "status": "completed",
                "outputs": {
                    "runtime": {
                        "action": "compile_paper",
                        "status": "completed",
                        "approval_ref": "approval-paper-plan-compile",
                        "exit_code": 0,
                        "pdf_generated": True,
                        "pdf_path": str(pdf),
                        "evidence_ids": ["runtime:paper-plan-compile"],
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    proc = run_shim(
        tmp_path,
        "$paper-plan",
        "idea-skillgen",
        "--title",
        "SkillGen Plan",
        "--discovery-evidence",
        str(discovery),
        "--review-llm-evidence",
        str(review),
        "--approval-ref",
        "approval-paper-plan-compile",
        "--allowlist-evidence",
        str(allowlist),
        "--before-artifact",
        str(before),
        "--runtime-evidence",
        str(runtime),
        "--after-artifact",
        str(pdf),
        "--run-id",
        "shim-paper-plan-compile-handoff",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "paper-plan"

    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    assert evidence["status"] == "completed"
    report = evidence["outputs"]["report"]
    assert report["compile_handoff"]["status"] == "completed"
    assert any(section["section_id"] == "compile-audit" for section in report["sections"])
    artifacts = {artifact["type"]: artifact["path"] for artifact in evidence["artifacts"]}
    assert {"paper_draft_compile_handoff_json", "paper_compile_runtime_evidence_json", "compiled_pdf"} <= set(artifacts)
    plan_json = json.loads((tmp_path / artifacts["paper_plan_json"]).read_text(encoding="utf-8"))
    assert plan_json["compile_handoff"]["verified"] is True
    assert "runtime:paper-plan-compile" in plan_json["compile_handoff"]["evidence_ids"]


def test_autosci_skill_shim_paper_draft_writes_latex_source(tmp_path: Path) -> None:
    proc = run_shim(
        tmp_path,
        "$paper-draft",
        "idea-001",
        "--venue",
        "ICLR",
        "--title",
        "Skill Generation for Inference-Time Agents",
        "--run-id",
        "shim-paper-draft-native",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "paper-draft"
    assert summary["execution_status"] == "partial"
    assert summary["action_count"] == 1
    assert summary["passed_count"] == 1

    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    assert payload["inputs"]["target"] == "idea-001"
    action = payload["outputs"]["skill_run"]["actions"][0]
    assert action["action"] == "write_report"
    assert action["schema"] == "scientific_report.v1"
    assert action["gate_status"] == "passed"
    report_evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    assert report_evidence["outputs"]["report"]["title"] == "Skill Generation for Inference-Time Agents"
    artifact_types = {artifact["type"] for artifact in report_evidence["artifacts"]}
    assert {"latex_source", "paper_sections_directory", "markdown_report", "report_plan_json"}.issubset(artifact_types)

    paper_dir = tmp_path / "artifacts/autosci/runs/shim-paper-draft-native/paper"
    main_tex = paper_dir / "main.tex"
    assert main_tex.exists()
    assert "\\documentclass{article}" in main_tex.read_text(encoding="utf-8")
    assert (paper_dir / "sections").is_dir()
    bundle = json.loads((tmp_path / "artifacts/autosci/runs/shim-paper-draft-native/publication_bundle.json").read_text(encoding="utf-8"))
    bundle_file_types = {item["type"] for item in bundle["outputs"]["bundle"]["files"]}
    assert "latex_source" in bundle_file_types


def test_autosci_skill_shim_paper_draft_includes_verified_compile_pdf_handoff(tmp_path: Path) -> None:
    compiled_dir = tmp_path / "compiled"
    compiled_dir.mkdir()
    pdf = compiled_dir / "main.pdf"
    pdf.write_text("%PDF-1.4\n", encoding="utf-8")
    before = tmp_path / "paper-draft-before.json"
    allowlist = tmp_path / "paper-draft-allowlist.json"
    runtime = tmp_path / "paper-draft-compile-runtime.json"
    before.write_text(json.dumps({"draft": "before"}), encoding="utf-8")
    allowlist.write_text(json.dumps({"approved": True, "scope": "paper-draft-compile-handoff"}), encoding="utf-8")
    runtime.write_text(
        json.dumps(
            {
                "schema": "autosci_runtime_evidence.v1",
                "task_id": "paper-draft-compile-runtime",
                "status": "completed",
                "outputs": {
                    "runtime": {
                        "action": "compile_paper",
                        "status": "completed",
                        "approval_ref": "approval-paper-draft-compile",
                        "exit_code": 0,
                        "command_run": "pdflatex main.tex",
                        "pdf_generated": True,
                        "pdf_path": str(pdf),
                        "evidence_ids": ["runtime:paper-draft-compile"],
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    proc = run_shim(
        tmp_path,
        "$paper-draft",
        "idea-001",
        "--title",
        "Skill Generation for Inference-Time Agents",
        "--approval-ref",
        "approval-paper-draft-compile",
        "--allowlist-evidence",
        str(allowlist),
        "--before-artifact",
        str(before),
        "--runtime-evidence",
        str(runtime),
        "--after-artifact",
        str(pdf),
        "--run-id",
        "shim-paper-draft-compile-handoff",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "paper-draft"
    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    assert action["action"] == "write_report"
    assert action["gate_status"] == "passed"

    report_evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    report = report_evidence["outputs"]["report"]
    assert report["compile_handoff"]["status"] == "completed"
    assert report["compile_handoff"]["verified"] is True
    assert "runtime:paper-draft-compile" in report["compile_handoff"]["evidence_ids"]
    assert any(section["section_id"] == "compiled-paper" for section in report["sections"])
    artifact_types = {artifact["type"] for artifact in report_evidence["artifacts"]}
    assert {"paper_draft_compile_handoff_json", "paper_compile_runtime_evidence_json", "compiled_pdf"} <= artifact_types

    bundle = json.loads(
        (tmp_path / "artifacts/autosci/runs/shim-paper-draft-compile-handoff/publication_bundle.json").read_text(
            encoding="utf-8"
        )
    )
    bundle_file_types = {item["type"] for item in bundle["outputs"]["bundle"]["files"]}
    assert {"compiled_pdf", "paper_draft_compile_handoff_json", "paper_compile_runtime_evidence_json"} <= bundle_file_types


def test_autosci_skill_shim_runs_paper_compile_fix_diagnostics(tmp_path: Path) -> None:
    paper_dir = tmp_path / "paper"
    paper_dir.mkdir()
    paper_dir.joinpath("main.tex").write_text(
        "\\documentclass{article}\n\\begin{document}\nSkillGen draft.\n\\end{document}\n",
        encoding="utf-8",
    )
    proc = run_shim(
        tmp_path,
        "$paper-compile",
        str(paper_dir),
        "--fix",
        "--run-id",
        "shim-paper-compile-fix",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "paper-compile"
    assert summary["execution_status"] == "gated"
    assert summary["action_count"] == 1

    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    assert payload["inputs"]["target"] == str(paper_dir)
    assert payload["inputs"]["native_options"]["fix"] is True
    action = payload["outputs"]["skill_run"]["actions"][0]
    assert action["action"] == "compile_paper"
    bundle = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    assert bundle["schema"] == "publication_bundle.v1"
    assert bundle["status"] == "inconclusive"
    assert any(artifact["type"] == "paper_compile_checklist_json" for artifact in bundle["artifacts"])
    assert any(artifact["type"] == "paper_compile_diagnostics_markdown" for artifact in bundle["artifacts"])


def test_autosci_skill_shim_paper_compile_fix_applies_approved_after_artifact(tmp_path: Path) -> None:
    paper_dir = tmp_path / "paper"
    paper_dir.mkdir()
    tex = paper_dir / "main.tex"
    tex.write_text(
        "\\documentclass{article}\n\\begin{document}\nBroken draft\n\\end{document}\n",
        encoding="utf-8",
    )
    fixed = tmp_path / "main-fixed.tex"
    fixed.write_text(
        "\\documentclass{article}\n\\begin{document}\nApproved fixed draft.\n\\end{document}\n",
        encoding="utf-8",
    )
    before = tmp_path / "main-before.tex"
    before.write_text(tex.read_text(encoding="utf-8"), encoding="utf-8")
    allowlist = tmp_path / "compile-allowlist.json"
    allowlist.write_text('{"allowed": ["source_auto_fix"]}\n', encoding="utf-8")

    proc = run_shim(
        tmp_path,
        "$paper-compile",
        str(paper_dir),
        "--fix",
        "--approval-ref",
        "approval-compile-fix",
        "--allowlist-evidence",
        str(allowlist),
        "--before-artifact",
        str(before),
        "--after-artifact",
        str(fixed),
        "--execute-approved",
        "--run-id",
        "shim-paper-compile-approved-fix",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    bundle = evidence["outputs"]["bundle"]
    assert tex.read_text(encoding="utf-8") == fixed.read_text(encoding="utf-8")
    assert any(artifact["type"] == "paper_compile_fix_writeback_json" for artifact in bundle["files"])
    fix_artifact = next(artifact for artifact in bundle["files"] if artifact["type"] == "paper_compile_fix_writeback_json")
    fix_evidence = json.loads((tmp_path / fix_artifact["path"]).read_text(encoding="utf-8"))
    assert fix_evidence["status"] == "completed"
    checklist_artifact = next(artifact for artifact in bundle["files"] if artifact["type"] == "paper_compile_checklist_json")
    checklist = json.loads((tmp_path / checklist_artifact["path"]).read_text(encoding="utf-8"))
    assert checklist["fix_writeback"]["applied"] is True


def test_autosci_skill_shim_runs_survey_rebuttal_and_poster_native_sidecars(tmp_path: Path) -> None:
    cases = [
        ("$survey", "topic:skillgen", "write_survey", "scientific_report.v1", "partial"),
        ("$rebuttal", "review-comments", "draft_rebuttal", "publication_bundle.v1", "partial"),
        ("$poster", "report-001", "build_poster", "publication_bundle.v1", "gated"),
    ]
    for command, target, expected_action, expected_schema, expected_status in cases:
        run_id = f"shim-{expected_action}"
        proc = run_shim(
            tmp_path,
            command,
            target,
            "--title",
            f"SkillGen {expected_action}",
            "--run-id",
            run_id,
        )
        assert proc.returncode == 0, proc.stderr
        summary = json.loads(proc.stdout)
        assert summary["execution_status"] == expected_status
        assert summary["action_count"] == 1
        assert summary["schema_only_count"] == 1
        payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
        action = payload["outputs"]["skill_run"]["actions"][0]
        assert action["action"] == expected_action
        assert action["schema"] == expected_schema
        evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
        assert evidence["status"] == "inconclusive"
        if expected_schema == "scientific_report.v1":
            assert evidence["outputs"]["report"]["title"] == f"SkillGen {expected_action}"
            assert any(artifact["type"] == "survey_markdown" for artifact in evidence["artifacts"])
        else:
            files = evidence["outputs"]["bundle"]["files"]
            assert files
            assert all((tmp_path / item["path"]).exists() for item in files)


def test_autosci_skill_shim_survey_completes_with_citation_evidence(tmp_path: Path) -> None:
    discovery = tmp_path / "survey-discovery.json"
    discovery.write_text(
        json.dumps(
            {
                "schema": "literature_discovery.v1",
                "task_id": "lit-survey-skillgen",
                "status": "completed",
                "outputs": {
                    "query": "skill generation",
                    "candidates": [
                        {
                            "candidate_id": "arxiv:2601.00002",
                            "title": "Survey Evidence for Skill Generation",
                            "arxiv_id": "2601.00002",
                            "source_ref": "https://arxiv.org/abs/2601.00002",
                            "source_channels": ["references"],
                        }
                    ],
                },
            }
        ),
        encoding="utf-8",
    )
    proc = run_shim(
        tmp_path,
        "$survey",
        "topic:skillgen",
        "--title",
        "SkillGen Survey",
        "--discovery-evidence",
        str(discovery),
        "--run-id",
        "shim-survey-citation-map",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "survey"
    assert summary["action_count"] == 1

    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    assert evidence["status"] == "completed"
    report = evidence["outputs"]["report"]
    prior_work = next(section for section in report["sections"] if section["section_id"] == "prior-work-map")
    assert "Survey Evidence for Skill Generation" in prior_work["body"]
    artifacts = {artifact["type"]: artifact["path"] for artifact in evidence["artifacts"]}
    citation_map = json.loads((tmp_path / artifacts["citation_map_json"]).read_text(encoding="utf-8"))
    assert citation_map["citation_count"] == 1


def test_autosci_skill_shim_rebuttal_maps_review_llm_findings(tmp_path: Path) -> None:
    review = tmp_path / "rebuttal-review.json"
    review.write_text(
        json.dumps(
            {
                "schema": "artifact_review.v1",
                "task_id": "review-rebuttal",
                "status": "completed",
                "outputs": {
                    "review": {
                        "review_available": True,
                        "review_mode": "review_llm",
                        "score": 0.64,
                        "recommendation": "revise",
                        "evidence_ids": ["review:rebuttal"],
                        "findings": [
                            {
                                "criterion": "evidence",
                                "issue": "Clarify which experiment supports the generated-skill claim.",
                                "suggestion": "Cite the runtime evidence and ablation table.",
                            }
                        ],
                        "review_llm": {"status": "completed"},
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    proc = run_shim(
        tmp_path,
        "$rebuttal",
        "review-comments",
        "--title",
        "SkillGen Rebuttal",
        "--review-llm-evidence",
        str(review),
        "--run-id",
        "shim-rebuttal-review-map",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "rebuttal"
    assert summary["action_count"] == 1

    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    assert evidence["status"] == "completed"
    files = evidence["outputs"]["bundle"]["files"]
    map_file = next(item for item in files if item["type"] == "rebuttal_response_map_json")
    response_map = json.loads((tmp_path / map_file["path"]).read_text(encoding="utf-8"))
    assert response_map["mapped_concerns"]
    assert response_map["unmapped_concerns"] == []
    assert "generated-skill claim" in response_map["mapped_concerns"][0]["concern"]


def test_autosci_skill_shim_accepts_survey_format_latex(tmp_path: Path) -> None:
    proc = run_shim(
        tmp_path,
        "$survey",
        "topic:skillgen",
        "--format",
        "latex",
        "--run-id",
        "shim-survey-format-latex",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "survey"
    assert summary["execution_status"] == "partial"
    assert summary["action_count"] == 1

    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    assert payload["inputs"]["native_options"]["format"] == "latex"
    action = payload["outputs"]["skill_run"]["actions"][0]
    assert action["action"] == "write_survey"
    evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    assert evidence["status"] == "inconclusive"
    assert evidence["inputs"]["format"] == "latex"


def test_autosci_skill_shim_runs_wiki_and_control_proposal_actions(tmp_path: Path) -> None:
    cases = [
        ("$prefill", "foundation:skillgen", "prefill_foundations", "research_memory_update.v1", "gated"),
        ("$edit", "wiki/ideas/skillgen.md", "edit_wiki_plan", "research_memory_update.v1", "gated"),
        ("$setup", "autosci", "setup_status", "workflow_evolution.v1", "gated"),
        ("$reset", "autosci", "reset_plan", "workflow_evolution.v1", "gated"),
    ]
    for command, target, expected_action, expected_schema, expected_status in cases:
        run_id = f"shim-{expected_action}"
        proc = run_shim(
            tmp_path,
            command,
            target,
            "--run-id",
            run_id,
        )
        assert proc.returncode == 0, proc.stderr
        summary = json.loads(proc.stdout)
        assert summary["execution_status"] == expected_status
        assert summary["action_count"] == 1
        payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
        action = payload["outputs"]["skill_run"]["actions"][0]
        assert action["action"] == expected_action
        assert action["schema"] == expected_schema
        assert action["status"] == "passed"
        evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
        assert evidence["status"] == "completed"
        if expected_schema == "research_memory_update.v1":
            change = evidence["outputs"]["changes"][0]
            assert change["operation"] == "propose"
            assert change["evidence_ids"]
        else:
            evolution = evidence["outputs"]["evolution"]
            assert evolution["approval_state"] == "proposed"
            assert evolution["review"]["protected_core_edits_applied"] is False
            assert (tmp_path / evolution["recommended_changes_path"]).exists()
            assert (tmp_path / evolution["patch_candidates_path"]).is_dir()


def test_autosci_skill_shim_prefill_applies_approved_wiki_mutation(tmp_path: Path) -> None:
    wiki_root = tmp_path / "artifacts/autosci/workspace/wiki"
    (wiki_root / "topics").mkdir(parents=True)
    (wiki_root / "graph").mkdir(parents=True)
    proc = run_shim(
        tmp_path,
        "$prefill",
        "foundation:skillgen",
        "--wiki-root",
        str(wiki_root),
        "--approval-ref",
        "approval-prefill-skillgen",
        "--execute-approved",
        "--run-id",
        "shim-prefill-approved",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "prefill"
    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    assert evidence["status"] == "completed"
    change = evidence["outputs"]["changes"][0]
    assert change["operation"] == "create"
    assert change["before_sha256"] != change["after_sha256"]
    page = wiki_root / "topics/foundation-foundation-skillgen.md"
    assert page.exists()
    assert "approval-prefill-skillgen" in page.read_text(encoding="utf-8")
    assert (wiki_root / "log.md").exists()
    assert (wiki_root / "index.md").exists()
    assert (wiki_root / "graph/context_brief.md").exists()


def test_autosci_skill_shim_edit_applies_approved_after_artifact(tmp_path: Path) -> None:
    wiki_root = tmp_path / "artifacts/autosci/workspace/wiki"
    (wiki_root / "ideas").mkdir(parents=True)
    (wiki_root / "graph").mkdir(parents=True)
    target = wiki_root / "ideas/skillgen.md"
    target.write_text("# SkillGen\n\nOld content.\n", encoding="utf-8")
    after = tmp_path / "skillgen-after.md"
    after.write_text("# SkillGen\n\nApproved edited content.\n", encoding="utf-8")

    proc = run_shim(
        tmp_path,
        "$edit",
        "wiki/ideas/skillgen.md",
        "--wiki-root",
        str(wiki_root),
        "--approval-ref",
        "approval-edit-skillgen",
        "--after-artifact",
        str(after),
        "--execute-approved",
        "--run-id",
        "shim-edit-approved",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "edit"
    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    assert evidence["status"] == "completed"
    change = evidence["outputs"]["changes"][0]
    assert change["operation"] == "update"
    assert change["before_sha256"] != change["after_sha256"]
    assert target.read_text(encoding="utf-8") == after.read_text(encoding="utf-8")
    artifact_types = {artifact["type"] for artifact in evidence["artifacts"]}
    assert {"wiki_page", "wiki_log", "wiki_rebuild"}.issubset(artifact_types)


def test_autosci_skill_shim_runs_ask_check_and_init_diagnostics(tmp_path: Path) -> None:
    cases = [
        ("$ask", "What supports SkillGen?", "ask_wiki", "research_memory_update.v1", "partial", "schema_only"),
        ("$check", "autosci wiki", "check_wiki_health", "workflow_evolution.v1", "partial", "passed"),
        ("$init", "agent skill learning", "init_sources", "literature_discovery.v1", "partial", "schema_only"),
    ]
    for command, target, expected_action, expected_schema, expected_status, expected_action_status in cases:
        run_id = f"shim-{expected_action}"
        proc = run_shim(
            tmp_path,
            command,
            target,
            "--run-id",
            run_id,
        )
        assert proc.returncode == 0, proc.stderr
        summary = json.loads(proc.stdout)
        assert summary["execution_status"] == expected_status
        assert summary["action_count"] == 1
        payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
        action = payload["outputs"]["skill_run"]["actions"][0]
        assert action["action"] == expected_action
        assert action["schema"] == expected_schema
        assert action["status"] == expected_action_status
        evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
        if expected_action == "ask_wiki":
            assert evidence["status"] == "inconclusive"
            assert evidence["outputs"]["changes"][0]["operation"] == "no_op"
            assert any(artifact["type"] == "ask_answer_markdown" for artifact in evidence["artifacts"])
        elif expected_action == "check_wiki_health":
            assert evidence["outputs"]["evolution"]["approval_state"] == "proposed"
            assert (tmp_path / evidence["outputs"]["evolution"]["recommended_changes_path"]).exists()
        elif expected_action == "init_sources":
            assert evidence["status"] == "inconclusive"
            assert evidence["outputs"]["mode"] == "init_plan"
            assert evidence["outputs"]["candidates"] == []


def test_autosci_skill_shim_init_uses_verified_runtime_source_manifest(tmp_path: Path) -> None:
    allowlist = tmp_path / "allowlist.json"
    before = tmp_path / "before.json"
    after = tmp_path / "after.json"
    runtime = tmp_path / "init-runtime.json"
    allowlist.write_text('{"allowed": ["discover"]}\n', encoding="utf-8")
    before.write_text('{"state": "before"}\n', encoding="utf-8")
    after.write_text('{"state": "after"}\n', encoding="utf-8")
    runtime.write_text(
        json.dumps(
            {
                "schema": "autosci_runtime_evidence.v1",
                "task_id": "init-runtime-skillgen",
                "status": "completed",
                "exit_code": 0,
                "candidates": [
                    {
                        "title": "SkillGen Source Candidate",
                        "url": "https://arxiv.org/abs/2601.00003",
                        "abstract": "Runtime-discovered source candidate.",
                    }
                ],
                "evidence_ids": ["runtime:init-skillgen"],
            }
        ),
        encoding="utf-8",
    )
    proc = run_shim(
        tmp_path,
        "$init",
        "skill generation",
        "--approval-ref",
        "approval-init-runtime",
        "--allowlist-evidence",
        str(allowlist),
        "--before-artifact",
        str(before),
        "--after-artifact",
        str(after),
        "--runtime-evidence",
        str(runtime),
        "--run-id",
        "shim-init-runtime-manifest",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "init"
    assert summary["action_count"] == 1

    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    assert evidence["status"] == "completed"
    assert evidence["outputs"]["mode"] == "init_runtime_verified"
    assert evidence["outputs"]["candidates"][0]["title"] == "SkillGen Source Candidate"
    contract_artifact = next(artifact for artifact in evidence["artifacts"] if artifact["type"] == "approval_contract_json")
    contract = json.loads((tmp_path / contract_artifact["path"]).read_text(encoding="utf-8"))
    assert contract["semantic_runtime"]["verified"] is True


def test_autosci_skill_shim_init_write_fans_runtime_sources_into_wiki(tmp_path: Path) -> None:
    wiki_root = tmp_path / "artifacts/autosci/workspace/wiki"
    (wiki_root / "papers").mkdir(parents=True)
    (wiki_root / "graph").mkdir(parents=True)
    allowlist = tmp_path / "allowlist.json"
    before = tmp_path / "before.json"
    after = tmp_path / "after.json"
    runtime = tmp_path / "init-runtime.json"
    allowlist.write_text('{"allowed": ["discover", "wiki_fan_in"]}\n', encoding="utf-8")
    before.write_text('{"papers": []}\n', encoding="utf-8")
    after.write_text('{"papers": ["skillgen-source"]}\n', encoding="utf-8")
    runtime.write_text(
        json.dumps(
            {
                "schema": "autosci_runtime_evidence.v1",
                "task_id": "init-runtime-skillgen",
                "status": "completed",
                "exit_code": 0,
                "candidates": [
                    {
                        "candidate_id": "skillgen-source",
                        "title": "SkillGen Source Candidate",
                        "url": "https://arxiv.org/abs/2601.00003",
                        "abstract": "Runtime-discovered source candidate.",
                    }
                ],
                "evidence_ids": ["runtime:init-skillgen"],
            }
        ),
        encoding="utf-8",
    )
    proc = run_shim(
        tmp_path,
        "$init",
        "skill generation",
        "--approval-ref",
        "approval-init-runtime",
        "--allowlist-evidence",
        str(allowlist),
        "--before-artifact",
        str(before),
        "--after-artifact",
        str(after),
        "--runtime-evidence",
        str(runtime),
        "--wiki-root",
        str(wiki_root),
        "--write",
        "--run-id",
        "shim-init-runtime-fan-in",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))

    fan_in = evidence["outputs"]["source_fan_in"]
    assert fan_in["status"] == "completed"
    assert fan_in["applied"] is True
    assert fan_in["written_count"] == 1
    fan_in_artifact = next(artifact for artifact in evidence["artifacts"] if artifact["type"] == "source_fan_in_writeback_json")
    fan_in_evidence = json.loads((tmp_path / fan_in_artifact["path"]).read_text(encoding="utf-8"))
    assert fan_in_evidence["status"] == "completed"
    page = wiki_root / "papers/skillgen-source.md"
    assert page.exists()
    assert "SkillGen Source Candidate" in page.read_text(encoding="utf-8")
    assert "Source Candidate Fan-In" in (wiki_root / "log.md").read_text(encoding="utf-8")
    assert "source_candidate_ingested" in (wiki_root / "graph/edges.jsonl").read_text(encoding="utf-8")
    assert (wiki_root / "index.md").exists()
    assert (wiki_root / "graph/context_brief.md").exists()


def test_autosci_skill_shim_daily_arxiv_uses_verified_runtime_digest(tmp_path: Path) -> None:
    allowlist = tmp_path / "daily-allowlist.json"
    before = tmp_path / "daily-before.json"
    after = tmp_path / "daily-after.json"
    runtime = tmp_path / "daily-runtime.json"
    allowlist.write_text('{"allowed": ["daily-arxiv"]}\n', encoding="utf-8")
    before.write_text('{"digest": "before"}\n', encoding="utf-8")
    after.write_text('{"digest": "after"}\n', encoding="utf-8")
    runtime.write_text(
        json.dumps(
            {
                "schema": "autosci_runtime_evidence.v1",
                "task_id": "daily-runtime-skillgen",
                "status": "completed",
                "exit_code": 0,
                "candidates": [
                    {
                        "title": "Daily SkillGen Paper",
                        "url": "https://arxiv.org/abs/2601.00004",
                        "abstract": "Daily arXiv source candidate.",
                    }
                ],
                "evidence_ids": ["runtime:daily-skillgen"],
            }
        ),
        encoding="utf-8",
    )
    proc = run_shim(
        tmp_path,
        "$daily-arxiv",
        "skill generation",
        "--approval-ref",
        "approval-daily-runtime",
        "--allowlist-evidence",
        str(allowlist),
        "--before-artifact",
        str(before),
        "--after-artifact",
        str(after),
        "--runtime-evidence",
        str(runtime),
        "--run-id",
        "shim-daily-runtime-digest",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "daily-arxiv"
    assert summary["execution_status"] == "gated"
    assert summary["action_count"] == 1

    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    assert evidence["status"] == "completed"
    assert evidence["outputs"]["mode"] == "daily_arxiv_runtime_verified"
    assert evidence["outputs"]["candidates"][0]["title"] == "Daily SkillGen Paper"
    contract_artifact = next(artifact for artifact in evidence["artifacts"] if artifact["type"] == "approval_contract_json")
    contract = json.loads((tmp_path / contract_artifact["path"]).read_text(encoding="utf-8"))
    assert contract["semantic_runtime"]["verified"] is True


def test_autosci_skill_shim_daily_arxiv_write_auto_ingests_runtime_digest(tmp_path: Path) -> None:
    wiki_root = tmp_path / "artifacts/autosci/workspace/wiki"
    (wiki_root / "papers").mkdir(parents=True)
    (wiki_root / "graph").mkdir(parents=True)
    allowlist = tmp_path / "daily-allowlist.json"
    before = tmp_path / "daily-before.json"
    after = tmp_path / "daily-after.json"
    runtime = tmp_path / "daily-runtime.json"
    allowlist.write_text('{"allowed": ["daily-arxiv", "auto_ingest"]}\n', encoding="utf-8")
    before.write_text('{"digest": "before"}\n', encoding="utf-8")
    after.write_text('{"digest": "after", "papers": ["daily-skillgen"]}\n', encoding="utf-8")
    runtime.write_text(
        json.dumps(
            {
                "schema": "autosci_runtime_evidence.v1",
                "task_id": "daily-runtime-skillgen",
                "status": "completed",
                "exit_code": 0,
                "candidates": [
                    {
                        "candidate_id": "daily-skillgen",
                        "title": "Daily SkillGen Paper",
                        "url": "https://arxiv.org/abs/2601.00004",
                        "abstract": "Daily arXiv source candidate.",
                    }
                ],
                "evidence_ids": ["runtime:daily-skillgen"],
            }
        ),
        encoding="utf-8",
    )
    proc = run_shim(
        tmp_path,
        "$daily-arxiv",
        "skill generation",
        "--approval-ref",
        "approval-daily-runtime",
        "--allowlist-evidence",
        str(allowlist),
        "--before-artifact",
        str(before),
        "--after-artifact",
        str(after),
        "--runtime-evidence",
        str(runtime),
        "--wiki-root",
        str(wiki_root),
        "--write",
        "--run-id",
        "shim-daily-runtime-auto-ingest",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))

    fan_in = evidence["outputs"]["source_fan_in"]
    assert fan_in["status"] == "completed"
    assert fan_in["applied"] is True
    assert fan_in["written_count"] == 1
    assert any(artifact["type"] == "source_fan_in_writeback_json" for artifact in evidence["artifacts"])
    page = wiki_root / "papers/daily-skillgen.md"
    assert page.exists()
    assert "Daily SkillGen Paper" in page.read_text(encoding="utf-8")
    assert "source_candidate_ingested" in (wiki_root / "graph/edges.jsonl").read_text(encoding="utf-8")


def test_autosci_skill_shim_ask_and_check_read_workspace_wiki(tmp_path: Path) -> None:
    wiki_root = tmp_path / "artifacts/autosci/workspace/wiki"
    (wiki_root / "papers").mkdir(parents=True)
    (wiki_root / "graph").mkdir(parents=True)
    (wiki_root / "papers/skillgen.md").write_text(
        "---\ntitle: SkillGen\n---\n# SkillGen\n\nSkillGen validates generated skills with evidence-linked regression tests.\n",
        encoding="utf-8",
    )
    (wiki_root / "graph/edges.jsonl").write_text(
        json.dumps(
            {
                "source": "paper:skillgen",
                "target": "concept:generated-skills",
                "relation": "supports",
                "operation": "confirm",
                "evidence_ids": ["paper:skillgen"],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    ask = run_shim(
        tmp_path,
        "$ask",
        "What evidence validates SkillGen skills?",
        "--wiki-root",
        str(wiki_root),
        "--run-id",
        "shim-ask-wiki-retrieval",
    )
    assert ask.returncode == 0, ask.stderr
    ask_summary = json.loads(ask.stdout)
    ask_payload = json.loads(Path(ask_summary["evidence_path"]).read_text(encoding="utf-8"))
    ask_action = ask_payload["outputs"]["skill_run"]["actions"][0]
    assert ask_action["status"] == "passed"
    ask_evidence = json.loads(Path(ask_action["evidence_path"]).read_text(encoding="utf-8"))
    assert ask_evidence["status"] == "completed"
    assert ask_evidence["outputs"]["changes"][0]["confidence"] == 0.75
    assert "Source-grounded extractive answer" in ask_evidence["outputs"]["changes"][0]["summary"]
    retrieval_artifact = next(item for item in ask_evidence["artifacts"] if item["type"] == "ask_retrieval_json")
    retrieval = json.loads((tmp_path / retrieval_artifact["path"]).read_text(encoding="utf-8"))
    assert retrieval["status"] == "completed"
    assert retrieval["answer_status"] == "completed"
    assert retrieval["hits"]
    assert retrieval["hits"][0]["path"].endswith("papers/skillgen.md")
    answer_artifact = next(item for item in ask_evidence["artifacts"] if item["type"] == "ask_answer_markdown")
    answer_text = (tmp_path / answer_artifact["path"]).read_text(encoding="utf-8")
    assert "SkillGen validates generated skills" in answer_text
    assert "papers/skillgen.md" in answer_text

    check = run_shim(
        tmp_path,
        "$check",
        "autosci wiki",
        "--wiki-root",
        str(wiki_root),
        "--run-id",
        "shim-check-wiki-health",
    )
    assert check.returncode == 0, check.stderr
    check_summary = json.loads(check.stdout)
    check_payload = json.loads(Path(check_summary["evidence_path"]).read_text(encoding="utf-8"))
    check_action = check_payload["outputs"]["skill_run"]["actions"][0]
    check_evidence = json.loads(Path(check_action["evidence_path"]).read_text(encoding="utf-8"))
    evolution = check_evidence["outputs"]["evolution"]
    markdown = (tmp_path / evolution["recommended_changes_path"]).read_text(encoding="utf-8")
    assert re.search(r"Markdown pages: `[1-9][0-9]*`", markdown)
    assert "Edge errors: `0`" in markdown


def test_autosci_skill_shim_ask_uses_model_command_with_retrieved_sources(tmp_path: Path) -> None:
    wiki_root = tmp_path / "artifacts/autosci/workspace/wiki"
    (wiki_root / "papers").mkdir(parents=True)
    (wiki_root / "papers/skillgen.md").write_text(
        "---\ntitle: SkillGen\n---\n"
        "# SkillGen\n\n"
        "SkillGen is supported by verifier-gated generated skills and runtime evidence.\n",
        encoding="utf-8",
    )
    model_command = tmp_path / "ask_model_command.py"
    model_command.write_text(
        "\n".join(
            [
                "import json",
                "import sys",
                "",
                "request = json.loads(sys.stdin.read())",
                "assert request['schema'] == 'autosci_model_request.v1'",
                "assert request['action'] == 'ask_wiki'",
                "assert request['context']['retrieval_hits']",
                "print(json.dumps({",
                "    'schema': 'autosci_model_response.v1',",
                "    'status': 'completed',",
                "    'outputs': {",
                "        'answer': 'SkillGen is supported by verifier-gated generated skills in the retrieved wiki evidence.',",
                "        'confidence': 0.82,",
                "        'evidence_ids': ['model:skillgen-support'],",
                "        'model': 'test-model',",
                "        'provider': 'command',",
                "    },",
                "}))",
            ]
        ),
        encoding="utf-8",
    )

    proc = run_shim(
        tmp_path,
        "$ask",
        "What supports SkillGen?",
        "--wiki-root",
        str(wiki_root),
        "--model-command",
        f"{shlex.quote(sys.executable)} {shlex.quote(str(model_command))}",
        "--run-id",
        "shim-ask-model-command",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "ask"
    assert summary["action_count"] == 1

    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    assert action["action"] == "ask_wiki"
    assert action["schema"] == "research_memory_update.v1"
    assert action["status"] == "passed"
    evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    assert evidence["status"] == "completed"
    change = evidence["outputs"]["changes"][0]
    assert "model:skillgen-support" in change["evidence_ids"]
    assert change["confidence"] == 0.82
    assert "explicit model evidence" in change["summary"]

    artifact_types = {artifact["type"] for artifact in evidence["artifacts"]}
    assert {"ask_answer_markdown", "ask_retrieval_json", "model_command_stdout_json", "model_command_stderr"} <= artifact_types
    retrieval_artifact = next(item for item in evidence["artifacts"] if item["type"] == "ask_retrieval_json")
    retrieval = json.loads((tmp_path / retrieval_artifact["path"]).read_text(encoding="utf-8"))
    assert retrieval["model_output"]["status"] == "completed"
    assert retrieval["model_output"]["evidence_ids"] == ["model:skillgen-support"]
    answer_artifact = next(item for item in evidence["artifacts"] if item["type"] == "ask_answer_markdown")
    answer_text = (tmp_path / answer_artifact["path"]).read_text(encoding="utf-8")
    assert "## Model Synthesis" in answer_text
    assert "verifier-gated generated skills" in answer_text


def test_autosci_skill_shim_check_uses_model_command_for_quality_review(tmp_path: Path) -> None:
    wiki_root = tmp_path / "artifacts/autosci/workspace/wiki"
    for name in ("papers", "methods", "ideas", "experiments", "outputs", "graph"):
        (wiki_root / name).mkdir(parents=True, exist_ok=True)
    (wiki_root / "papers/skillgen.md").write_text(
        "# SkillGen\n\nSkillGen wiki evidence links claims, methods, ideas, experiments, and outputs.\n",
        encoding="utf-8",
    )
    (wiki_root / "graph/edges.jsonl").write_text(
        json.dumps({"source": "paper:skillgen", "target": "idea:skillgen", "relation": "supports"}) + "\n",
        encoding="utf-8",
    )
    model_command = tmp_path / "check_model_command.py"
    model_command.write_text(
        "\n".join(
            [
                "import json",
                "import sys",
                "",
                "request = json.loads(sys.stdin.read())",
                "assert request['schema'] == 'autosci_model_request.v1'",
                "assert request['action'] == 'check_wiki_health'",
                "assert request['context']['findings']['markdown_page_count'] == 1",
                "print(json.dumps({",
                "    'schema': 'autosci_model_response.v1',",
                "    'status': 'completed',",
                "    'outputs': {",
                "        'answer': 'The wiki has the required structural blocks and a valid source-linked graph edge.',",
                "        'confidence': 0.91,",
                "        'evidence_ids': ['model:wiki-health-review'],",
                "        'findings': [{'criterion': 'source graph', 'verdict': 'pass'}],",
                "        'model': 'test-model',",
                "        'provider': 'command',",
                "    },",
                "}))",
            ]
        ),
        encoding="utf-8",
    )

    proc = run_shim(
        tmp_path,
        "$check",
        "autosci wiki",
        "--wiki-root",
        str(wiki_root),
        "--model-command",
        f"{shlex.quote(sys.executable)} {shlex.quote(str(model_command))}",
        "--run-id",
        "shim-check-model-command",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "check"
    assert summary["action_count"] == 1

    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    assert action["action"] == "check_wiki_health"
    assert action["schema"] == "workflow_evolution.v1"
    assert action["status"] == "passed"
    evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    evolution = evidence["outputs"]["evolution"]
    assert "model:wiki-health-review" in evolution["evidence_ids"]
    assert evolution["collected"]["runtime_errors"] == []
    assert evolution["collected"]["ambiguous_manuals_or_prompts"] == []
    assert evolution["collected"]["gate_rejection_reasons"][0]["status"] == "passed"
    assert "Model/reviewer evidence completed" in evolution["collected"]["gate_rejection_reasons"][0]["reasons"][0]

    artifact_types = {artifact["type"] for artifact in evidence["artifacts"]}
    assert {"recommended_changes_markdown", "patch_candidates_directory", "model_command_stdout_json", "model_command_stderr"} <= artifact_types
    markdown = (tmp_path / evolution["recommended_changes_path"]).read_text(encoding="utf-8")
    assert "## Model Evidence" in markdown
    assert "valid source-linked graph edge" in markdown


def test_autosci_skill_shim_runs_remaining_gated_backend_actions(tmp_path: Path) -> None:
    cases = [
        ("$daily-arxiv", "agents", "daily_arxiv_prepare_finalize", "literature_discovery.v1", "gated", "schema_only"),
        ("$exp-pilot-eval", "pilot-claim-001", "evaluate_pilot_result", "claim_verdict.v1", "partial", "schema_only"),
        ("$exp-pilot-run", "pilot-001", "run_pilot_experiment", "experiment_result.v1", "gated", "schema_only"),
        ("$refine", "report-001", "refine_artifact", "workflow_evolution.v1", "gated", "passed"),
        ("$research", "skillgen lifecycle", "run_research_lifecycle", "workflow_evolution.v1", "gated", "schema_only"),
        ("$visualize", "autosci graph", "visualize_graph", "research_graph_update.v1", "gated", "passed"),
    ]
    for command, target, expected_action, expected_schema, expected_status, expected_action_status in cases:
        run_id = f"shim-{expected_action}"
        proc = run_shim(
            tmp_path,
            command,
            target,
            "--run-id",
            run_id,
        )
        assert proc.returncode == 0, proc.stderr
        summary = json.loads(proc.stdout)
        assert summary["execution_status"] == expected_status
        assert summary["action_count"] == 1
        payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
        action = payload["outputs"]["skill_run"]["actions"][0]
        assert action["action"] == expected_action
        assert action["schema"] == expected_schema
        assert action["status"] == expected_action_status
        evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
        if expected_action in {"daily_arxiv_prepare_finalize", "evaluate_pilot_result", "run_pilot_experiment"}:
            assert evidence["status"] == "inconclusive"
        if expected_action in {"daily_arxiv_prepare_finalize", "run_pilot_experiment", "visualize_graph"}:
            contract_artifact = next(
                artifact for artifact in evidence["artifacts"] if artifact["type"] == "approval_contract_json"
            )
            contract = json.loads((tmp_path / contract_artifact["path"]).read_text(encoding="utf-8"))
            assert contract["approved"] is False
            assert "approval_ref" in contract["missing"]
        if expected_action in {"refine_artifact", "run_research_lifecycle"}:
            assert evidence["outputs"]["evolution"]["review"]["protected_core_edits_applied"] is False
            contract_artifact = next(
                artifact for artifact in evidence["artifacts"] if artifact["type"] == "approval_contract_json"
            )
            contract = json.loads((tmp_path / contract_artifact["path"]).read_text(encoding="utf-8"))
            assert contract["approved"] is False
        if expected_action == "visualize_graph":
            assert evidence["outputs"]["edges"][0]["operation"] == "propose"


def test_autosci_skill_shim_refine_applies_approved_after_artifact(tmp_path: Path) -> None:
    target = tmp_path / "artifacts/autosci/workspace/wiki/outputs/report-001.md"
    target.parent.mkdir(parents=True)
    target.write_text("# Report\n\nOld draft.\n", encoding="utf-8")
    after = tmp_path / "report-001-after.md"
    after.write_text("# Report\n\nApproved refined draft.\n", encoding="utf-8")
    before = tmp_path / "report-001-before.md"
    before.write_text("# Report\n\nOld draft.\n", encoding="utf-8")
    runtime = tmp_path / "refine-runtime.json"
    runtime.write_text('{"status": "completed", "exit_code": 0, "evidence_ids": ["runtime:refine-report"]}\n', encoding="utf-8")
    allowlist = tmp_path / "refine-allowlist.json"
    allowlist.write_text('{"allowed": ["refine_artifact"]}\n', encoding="utf-8")

    proc = run_shim(
        tmp_path,
        "$refine",
        str(target),
        "--approval-ref",
        "approval-refine-report",
        "--allowlist-evidence",
        str(allowlist),
        "--runtime-evidence",
        str(runtime),
        "--before-artifact",
        str(before),
        "--after-artifact",
        str(after),
        "--execute-approved",
        "--run-id",
        "shim-refine-approved-apply",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "refine"
    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    evolution = evidence["outputs"]["evolution"]
    assert evolution["approval_state"] == "applied"
    assert evolution["review"]["protected_core_edits_applied"] is True
    assert evolution["review"]["refine_apply"]["applied"] is True
    assert target.read_text(encoding="utf-8") == after.read_text(encoding="utf-8")
    artifact_types = {artifact["type"] for artifact in evidence["artifacts"]}
    assert {"refine_apply_writeback_json", "refined_artifact"}.issubset(artifact_types)
    apply_artifact = next(artifact for artifact in evidence["artifacts"] if artifact["type"] == "refine_apply_writeback_json")
    apply_evidence = json.loads((tmp_path / apply_artifact["path"]).read_text(encoding="utf-8"))
    assert apply_evidence["status"] == "completed"


def test_autosci_skill_shim_pilot_eval_uses_runtime_evidence(tmp_path: Path) -> None:
    runtime = tmp_path / "pilot-runtime.json"
    runtime.write_text(
        json.dumps(
            {
                "schema": "autosci_runtime_evidence.v1",
                "task_id": "pilot-runtime-skillgen",
                "status": "completed",
                "exit_code": 0,
                "outcome": "supports",
                "metrics": [{"name": "pilot_accuracy", "value": 0.73}],
                "evidence_ids": ["runtime:pilot-skillgen"],
            }
        ),
        encoding="utf-8",
    )
    proc = run_shim(
        tmp_path,
        "$exp-pilot-eval",
        "pilot-claim-001",
        "--runtime-evidence",
        str(runtime),
        "--run-id",
        "shim-pilot-eval-runtime",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "exp-pilot-eval"
    assert summary["action_count"] == 1

    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    assert evidence["status"] == "completed"
    verdict = evidence["outputs"]["verdicts"][0]
    assert verdict["claim_id"] == "pilot-claim-001"
    assert verdict["verdict"] == "supported"
    assert verdict["evidence_outcome"] == "supports"
    assert "runtime:pilot-skillgen" in verdict["evidence_ids"]
    assert any(artifact["type"] == "pilot_runtime_evidence_json" for artifact in evidence["artifacts"])


def test_autosci_skill_shim_pilot_eval_write_updates_wiki_with_approval(tmp_path: Path) -> None:
    claim_id = "pilot-claim-write"
    wiki_root = tmp_path / "artifacts/autosci/workspace/wiki"
    (wiki_root / "ideas").mkdir(parents=True)
    (wiki_root / "graph").mkdir(parents=True)
    idea_path = wiki_root / "ideas" / f"{claim_id}.md"
    idea_path.write_text(
        "---\ntitle: Pilot Claim Write\nstatus: pilot\n---\n# Pilot Claim Write\n",
        encoding="utf-8",
    )
    runtime = tmp_path / "pilot-runtime-write.json"
    runtime.write_text(
        json.dumps(
            {
                "schema": "autosci_runtime_evidence.v1",
                "task_id": "pilot-runtime-write",
                "status": "completed",
                "exit_code": 0,
                "outcome": "supports",
                "metrics": [{"name": "pilot_accuracy", "value": 0.77}],
                "evidence_ids": ["runtime:pilot-write"],
            }
        ),
        encoding="utf-8",
    )

    proc = run_shim(
        tmp_path,
        "$exp-pilot-eval",
        claim_id,
        "--runtime-evidence",
        str(runtime),
        "--wiki-root",
        str(wiki_root),
        "--write",
        "--approval-ref",
        "approval-pilot-write",
        "--run-id",
        "shim-pilot-eval-writeback",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    writeback_artifact = next(artifact for artifact in evidence["artifacts"] if artifact["type"] == "pilot_verdict_writeback_json")
    writeback = json.loads((tmp_path / writeback_artifact["path"]).read_text(encoding="utf-8"))
    assert writeback["status"] == "completed"
    assert writeback["outputs"]["write"]["applied"] is True
    assert "claim_verdict: supported" in idea_path.read_text(encoding="utf-8")
    assert "claim_verdict_written" in (wiki_root / "graph/edges.jsonl").read_text(encoding="utf-8")


def test_autosci_skill_shim_exp_eval_merges_experiment_code_and_review_llm_evidence(tmp_path: Path) -> None:
    claim_id = "claim-skillgen-001"
    claims = tmp_path / "claims.json"
    claims.write_text(
        json.dumps(
            {
                "schema": "research_claims.v1",
                "task_id": "claims-skillgen",
                "status": "completed",
                "outputs": {
                    "claims": [
                        {
                            "claim_id": claim_id,
                            "text": "SkillGen improves generated-skill reliability on held-out repair tasks.",
                            "evidence_ids": ["claim:skillgen"],
                        }
                    ]
                },
            }
        ),
        encoding="utf-8",
    )
    result = tmp_path / "experiment-result.json"
    result.write_text(
        json.dumps(
            {
                "schema": "experiment_result.v1",
                "task_id": "result-skillgen",
                "status": "completed",
                "outputs": {
                    "result": {
                        "experiment_id": "exp-skillgen",
                        "outcome": "supports",
                        "evidence_ids": ["experiment:skillgen"],
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    code = tmp_path / "code-evidence.json"
    code.write_text(
        json.dumps(
            {
                "schema": "code_evidence_map.v1",
                "task_id": "code-skillgen",
                "status": "completed",
                "outputs": {
                    "mappings": [
                        {
                            "mapping_id": "code-map-skillgen",
                            "claim_id": claim_id,
                            "evidence_ids": ["code:skillgen-eval"],
                            "files": ["experiments/skillgen_eval.py"],
                        }
                    ]
                },
            }
        ),
        encoding="utf-8",
    )
    review = tmp_path / "review-llm-exp-eval.json"
    review.write_text(
        json.dumps(
            {
                "schema": "artifact_review.v1",
                "task_id": "review-exp-eval",
                "status": "completed",
                "outputs": {
                    "review": {
                        "artifact_id": "artifact:exp-skillgen",
                        "target": claim_id,
                        "review_mode": "review_llm",
                        "review_available": True,
                        "difficulty": "hard",
                        "focus": "evidence",
                        "score": 0.81,
                        "recommendation": "pass_with_caveats",
                        "evidence_ids": ["review:exp-eval"],
                    },
                    "findings": [
                        {
                            "finding_id": "review.exp-eval.evidence-linked",
                            "severity": "low",
                            "category": "evidence",
                            "evidence": "Experiment and code evidence are linked to the claim.",
                            "suggestion": "Keep the linkage in the paper evidence table.",
                        }
                    ],
                },
            }
        ),
        encoding="utf-8",
    )

    proc = run_shim(
        tmp_path,
        "$exp-eval",
        claim_id,
        "--claims-evidence",
        str(claims),
        "--experiment-result-evidence",
        str(result),
        "--code-evidence",
        str(code),
        "--review-llm-evidence",
        str(review),
        "--run-id",
        "shim-exp-eval-review-llm",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "exp-eval"
    assert summary["action_count"] == 1

    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    assert action["action"] == "verify_claim"
    assert action["schema"] == "claim_verdict.v1"
    assert action["gate_status"] == "passed"
    evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    verdict = evidence["outputs"]["verdicts"][0]
    assert verdict["claim_id"] == claim_id
    assert verdict["verdict"] == "supported"
    assert verdict["experiment_id"] == "exp-skillgen"
    assert verdict["review_llm"]["status"] == "completed"
    assert verdict["review_llm"]["recommendation"] == "pass_with_caveats"
    assert "review-exp-eval" in verdict["evidence_ids"]
    assert "review:exp-eval" in verdict["evidence_ids"]
    assert "code-map-skillgen" in verdict["code_evidence_ids"]
    assert "Review LLM evidence" in verdict["basis"]
    assert any(artifact["type"] == "claim_review_llm_evidence_json" for artifact in evidence["artifacts"])


def test_autosci_skill_shim_exp_eval_write_updates_wiki_with_approval(tmp_path: Path) -> None:
    claim_id = "claim-skillgen-write"
    wiki_root = tmp_path / "artifacts/autosci/workspace/wiki"
    (wiki_root / "ideas").mkdir(parents=True)
    (wiki_root / "graph").mkdir(parents=True)
    idea_path = wiki_root / "ideas" / f"{claim_id}.md"
    idea_path.write_text(
        "---\ntitle: SkillGen Writeback Idea\nstatus: candidate\n---\n# SkillGen Writeback Idea\n",
        encoding="utf-8",
    )
    claims = tmp_path / "claims-write.json"
    claims.write_text(
        json.dumps(
            {
                "schema": "research_claims.v1",
                "task_id": "claims-write",
                "status": "completed",
                "outputs": {"claims": [{"claim_id": claim_id, "text": "Approved claim writeback.", "evidence_ids": ["claim:write"]}]},
            }
        ),
        encoding="utf-8",
    )
    result = tmp_path / "result-write.json"
    result.write_text(
        json.dumps(
            {
                "schema": "experiment_result.v1",
                "task_id": "result-write",
                "status": "completed",
                "outputs": {"result": {"experiment_id": "exp-write", "outcome": "supports", "evidence_ids": ["experiment:write"]}},
            }
        ),
        encoding="utf-8",
    )
    review = tmp_path / "review-write.json"
    review.write_text(
        json.dumps(
            {
                "schema": "artifact_review.v1",
                "task_id": "review-write",
                "status": "completed",
                "outputs": {
                    "review": {
                        "review_mode": "review_llm",
                        "review_available": True,
                        "recommendation": "pass_with_caveats",
                        "evidence_ids": ["review:write"],
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    proc = run_shim(
        tmp_path,
        "$exp-eval",
        claim_id,
        "--wiki-root",
        str(wiki_root),
        "--claims-evidence",
        str(claims),
        "--experiment-result-evidence",
        str(result),
        "--review-llm-evidence",
        str(review),
        "--write",
        "--approval-ref",
        "approval-exp-eval-write",
        "--run-id",
        "shim-exp-eval-writeback",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    writeback_artifact = next(artifact for artifact in evidence["artifacts"] if artifact["type"] == "claim_verdict_writeback_json")
    writeback = json.loads((tmp_path / writeback_artifact["path"]).read_text(encoding="utf-8"))
    assert writeback["status"] == "completed"
    assert writeback["outputs"]["write"]["applied"] is True
    updated = idea_path.read_text(encoding="utf-8")
    assert "claim_verdict: supported" in updated
    assert "claim_verdict_confidence: 0.72" in updated
    assert "claim_verdict_evidence:" in updated
    assert (wiki_root / "log.md").exists()
    assert "Claim Verdict Writeback" in (wiki_root / "log.md").read_text(encoding="utf-8")
    assert "claim_verdict_written" in (wiki_root / "graph/edges.jsonl").read_text(encoding="utf-8")


def test_autosci_web_visualization_compatibility_tools_generate_graph_artifacts(tmp_path: Path) -> None:
    wiki_root = tmp_path / "wiki"
    (wiki_root / "papers").mkdir(parents=True)
    (wiki_root / "ideas").mkdir()
    (wiki_root / "graph").mkdir()
    (wiki_root / "papers/skillgen.md").write_text("# SkillGen\n\nGenerated skill paper.\n", encoding="utf-8")
    (wiki_root / "ideas/idea-001.md").write_text("# Idea 001\n\nEvaluate generated skills.\n", encoding="utf-8")
    (wiki_root / "graph/edges.jsonl").write_text(
        json.dumps(
            {
                "source": "papers/skillgen.md",
                "target": "ideas/idea-001.md",
                "relation": "inspires",
                "operation": "confirm",
                "evidence_ids": ["paper:skillgen"],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    assert (REPO / "tools/visualize.py").exists()
    assert (REPO / "tools/serve.py").exists()
    assert (REPO / "app/index.html").exists()
    assert (REPO / "app/modules/graph.js").exists()

    obsidian = subprocess.run(
        [
            sys.executable,
            str(REPO / "tools/visualize.py"),
            "generate-obsidian-config",
            "--wiki-root",
            str(wiki_root),
        ],
        cwd=REPO,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert obsidian.returncode == 0, obsidian.stderr
    assert (wiki_root / ".obsidian/graph.json").exists()

    canvas = subprocess.run(
        [
            sys.executable,
            str(REPO / "tools/visualize.py"),
            "generate-canvas",
            "--wiki-root",
            str(wiki_root),
            "--graph-out",
            str(tmp_path / "graph.json"),
        ],
        cwd=REPO,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert canvas.returncode == 0, canvas.stderr
    canvas_summary = json.loads(canvas.stdout)
    assert canvas_summary["nodes"] >= 2
    assert canvas_summary["edges"] == 1
    assert (wiki_root / "graph/autosci.canvas").exists()
    graph_data = json.loads((tmp_path / "graph.json").read_text(encoding="utf-8"))
    assert graph_data["schema"] == "autosci_web_graph.v1"
    assert len(graph_data["nodes"]) >= 2
    assert graph_data["edges"][0]["relation"] == "inspires"

    health = subprocess.run(
        [
            sys.executable,
            str(REPO / "tools/serve.py"),
            "--wiki-root",
            str(wiki_root),
            "--health-check",
        ],
        cwd=REPO,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert health.returncode == 0, health.stderr
    health_payload = json.loads(health.stdout)
    assert health_payload["ok"] is True
    assert health_payload["node_count"] >= 2
    assert health_payload["edge_count"] == 1


def test_autosci_skill_shim_records_approval_runtime_contract_for_gated_actions(tmp_path: Path) -> None:
    allowlist = tmp_path / "allowlist.json"
    runtime = tmp_path / "runtime.json"
    before = tmp_path / "before-state.json"
    after = tmp_path / "after-state.json"
    allowlist.write_text(json.dumps({"commands": ["browser-render-poster"]}), encoding="utf-8")
    runtime.write_text(
        json.dumps(
            {
                "exit_code": 0,
                "browser_rendered": True,
                "overflow_probe": "passed",
                "png_exported": True,
                "log": "approved render completed",
            }
        ),
        encoding="utf-8",
    )
    before.write_text(json.dumps({"poster_png": False}), encoding="utf-8")
    after.write_text(json.dumps({"poster_png": True}), encoding="utf-8")

    proc = run_shim(
        tmp_path,
        "$poster",
        "report-001",
        "--approval-ref",
        "approval-123",
        "--allowlist-evidence",
        str(allowlist),
        "--runtime-evidence",
        str(runtime),
        "--before-artifact",
        str(before),
        "--after-artifact",
        str(after),
        "--run-id",
        "shim-poster-approval-contract",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["execution_status"] == "gated"
    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    assert payload["inputs"]["native_options"]["approval_ref"] == "approval-123"
    action = payload["outputs"]["skill_run"]["actions"][0]
    evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    assert evidence["status"] == "inconclusive"
    assert evidence["inputs"]["approval_ref"] == "approval-123"
    contract_artifact = next(
        artifact for artifact in evidence["artifacts"] if artifact["type"] == "approval_contract_json"
    )
    contract = json.loads((tmp_path / contract_artifact["path"]).read_text(encoding="utf-8"))
    assert contract["approval_ref"] == "approval-123"
    assert contract["approved"] is True
    assert contract["ready_for_execution"] is True
    assert contract["execution_verified"] is True
    assert contract["semantic_runtime"]["verified"] is True
    assert contract["missing"] == []
    assert contract["side_effects"] == ["browser_render", "overflow_probe", "png_export"]

    validation_artifact = next(
        artifact for artifact in evidence["artifacts"] if artifact["type"] == "poster_validation_json"
    )
    validation = json.loads((tmp_path / validation_artifact["path"]).read_text(encoding="utf-8"))
    assert validation["approval_contract"]["approval_state"] == "verified"
    assert validation["runtime_semantic"]["verified"] is True
    assert validation["browser_rendered"] is True
    assert validation["png_exported"] is True


def test_autosci_skill_shim_uses_semantic_runtime_evidence_for_gated_results(tmp_path: Path) -> None:
    def contract_files(
        prefix: str,
        action: str,
        runtime_payload: dict[str, object],
        *,
        after_name: str = "after.json",
    ) -> tuple[Path, Path, Path, Path]:
        allowlist = tmp_path / f"{prefix}-allowlist.json"
        runtime = tmp_path / f"{prefix}-runtime.json"
        before = tmp_path / f"{prefix}-before.json"
        after = tmp_path / after_name
        allowlist.write_text(json.dumps({"approved": True, "scope": prefix}), encoding="utf-8")
        runtime_record = {
            "action": action,
            "status": "completed",
            "approval_ref": f"approval-{prefix}",
            "command_run": f"approved-{prefix}-runtime",
            "evidence_ids": [f"runtime:{prefix}"],
            "checks": [{"check": "exit_code", "status": "ok", "detail": "exit_code=0"}],
            **runtime_payload,
        }
        runtime.write_text(
            json.dumps(
                {
                    "schema": "autosci_runtime_evidence.v1",
                    "task_id": f"task-{prefix}",
                    "sprint_id": f"sprint-{prefix}",
                    "node_id": f"node-{prefix}",
                    "status": "completed",
                    "inputs": {"approval_ref": f"approval-{prefix}"},
                    "outputs": {"runtime": runtime_record},
                    "artifacts": [{"type": "runtime_after", "path": str(after)}],
                    "provenance": {
                        "operator_id": "test",
                        "implementation_package": "test",
                        "timestamp": "2026-06-24T00:00:00Z",
                    },
                    "limitations": ["Approved runtime evidence was supplied by the test fixture."],
                }
            ),
            encoding="utf-8",
        )
        before.write_text(json.dumps({"before": prefix}), encoding="utf-8")
        after.write_text(json.dumps({"after": prefix}) if after.suffix != ".pdf" else "%PDF-1.4\n", encoding="utf-8")
        return allowlist, runtime, before, after

    allowlist, runtime, before, after = contract_files(
        "daily",
        "daily_arxiv_prepare_finalize",
        {
            "exit_code": 0,
            "candidates": [
                {
                    "arxiv_id": "2606.12345",
                    "title": "Runtime Verified Agent Discovery",
                    "candidate_id": "2606.12345",
                    "source_channels": ["arxiv"],
                    "ranking_score": 1.0,
                    "ranking_rationale": "Approved arXiv runtime fetch returned this candidate.",
                    "dedup_status": "unknown",
                    "fetch_status": "fetched",
                }
            ],
        },
    )
    daily = run_shim(
        tmp_path,
        "$daily-arxiv",
        "agents",
        "--approval-ref",
        "approval-daily",
        "--allowlist-evidence",
        str(allowlist),
        "--runtime-evidence",
        str(runtime),
        "--before-artifact",
        str(before),
        "--after-artifact",
        str(after),
        "--run-id",
        "shim-daily-runtime-verified",
    )
    assert daily.returncode == 0, daily.stderr
    daily_summary = json.loads(daily.stdout)
    daily_action = json.loads(Path(daily_summary["evidence_path"]).read_text(encoding="utf-8"))["outputs"]["skill_run"]["actions"][0]
    assert daily_action["status"] == "passed"
    daily_evidence = json.loads(Path(daily_action["evidence_path"]).read_text(encoding="utf-8"))
    assert daily_evidence["status"] == "completed"
    assert daily_evidence["outputs"]["candidates"][0]["title"] == "Runtime Verified Agent Discovery"
    daily_contract = json.loads(
        (
            tmp_path
            / next(artifact for artifact in daily_evidence["artifacts"] if artifact["type"] == "approval_contract_json")["path"]
        ).read_text(encoding="utf-8")
    )
    assert daily_contract["semantic_runtime"]["verified"] is True

    allowlist, runtime, before, after = contract_files(
        "pilot",
        "run_pilot_experiment",
        {
            "exit_code": 0,
            "outcome": "supports",
            "result_collected": True,
            "metrics": [{"name": "accuracy", "value": 0.91}],
        },
    )
    pilot = run_shim(
        tmp_path,
        "$exp-pilot-run",
        "pilot-001",
        "--approval-ref",
        "approval-pilot",
        "--allowlist-evidence",
        str(allowlist),
        "--runtime-evidence",
        str(runtime),
        "--before-artifact",
        str(before),
        "--after-artifact",
        str(after),
        "--run-id",
        "shim-pilot-runtime-verified",
    )
    assert pilot.returncode == 0, pilot.stderr
    pilot_summary = json.loads(pilot.stdout)
    pilot_action = json.loads(Path(pilot_summary["evidence_path"]).read_text(encoding="utf-8"))["outputs"]["skill_run"]["actions"][0]
    assert pilot_action["status"] == "passed"
    pilot_evidence = json.loads(Path(pilot_action["evidence_path"]).read_text(encoding="utf-8"))
    assert pilot_evidence["status"] == "completed"
    assert pilot_evidence["outputs"]["result"]["outcome"] == "supports"
    assert pilot_evidence["outputs"]["result"]["metrics"] == [{"name": "accuracy", "value": 0.91}]

    paper_dir = tmp_path / "runtime-paper"
    paper_dir.mkdir()
    (paper_dir / "main.tex").write_text(
        "\\documentclass{article}\n\\begin{document}\nRuntime verified compile.\n\\end{document}\n",
        encoding="utf-8",
    )
    allowlist, runtime, before, after = contract_files(
        "compile",
        "compile_paper",
        {"exit_code": 0, "pdf_generated": True, "pdf_path": str(tmp_path / "compiled-runtime.pdf")},
        after_name="compiled-runtime.pdf",
    )
    compile_proc = run_shim(
        tmp_path,
        "$paper-compile",
        str(paper_dir),
        "--checklist",
        "--approval-ref",
        "approval-compile",
        "--allowlist-evidence",
        str(allowlist),
        "--runtime-evidence",
        str(runtime),
        "--before-artifact",
        str(before),
        "--after-artifact",
        str(after),
        "--run-id",
        "shim-paper-compile-runtime-verified",
    )
    assert compile_proc.returncode == 0, compile_proc.stderr
    compile_summary = json.loads(compile_proc.stdout)
    compile_action = json.loads(Path(compile_summary["evidence_path"]).read_text(encoding="utf-8"))["outputs"]["skill_run"]["actions"][0]
    assert compile_action["status"] == "passed"
    compile_evidence = json.loads(Path(compile_action["evidence_path"]).read_text(encoding="utf-8"))
    assert compile_evidence["status"] == "completed"
    checklist_artifact = next(
        artifact for artifact in compile_evidence["artifacts"] if artifact["type"] == "paper_compile_checklist_json"
    )
    checklist = json.loads((tmp_path / checklist_artifact["path"]).read_text(encoding="utf-8"))
    assert checklist["runtime_semantic"]["verified"] is True
    assert any(row["check"] == "runtime_semantic_verified" and row["status"] == "ok" for row in checklist["checks"])


def test_autosci_skill_shim_executes_approved_paper_compile_executor(tmp_path: Path) -> None:
    paper_dir = tmp_path / "approved-paper"
    paper_dir.mkdir()
    (paper_dir / "main.tex").write_text(
        "\\documentclass{article}\n\\begin{document}\nApproved executor compile.\n\\end{document}\n",
        encoding="utf-8",
    )
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_latexmk = fake_bin / "latexmk"
    fake_latexmk.write_text(
        "#!/usr/bin/env python3\n"
        "from pathlib import Path\n"
        "Path('main.pdf').write_text('%PDF-1.4\\n', encoding='utf-8')\n"
        "print('fake latexmk completed')\n",
        encoding="utf-8",
    )
    fake_latexmk.chmod(0o755)
    allowlist = tmp_path / "compile-allowlist.json"
    before = tmp_path / "compile-before.json"
    allowlist.write_text(json.dumps({"executables": ["latexmk"]}), encoding="utf-8")
    before.write_text(json.dumps({"paper_dir": str(paper_dir), "pdf_exists": False}), encoding="utf-8")

    proc = run_shim(
        tmp_path,
        "$paper-compile",
        str(paper_dir),
        "--checklist",
        "--approval-ref",
        "approval-execute-compile",
        "--allowlist-evidence",
        str(allowlist),
        "--before-artifact",
        str(before),
        "--execute-approved",
        "--run-id",
        "shim-paper-compile-executor",
        extra_env={"PATH": f"{fake_bin}{os.pathsep}{os.environ.get('PATH', '')}"},
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    assert action["status"] == "passed"
    evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    assert evidence["status"] == "completed"
    bundle_files = evidence["outputs"]["bundle"]["files"]
    assert any(item["type"] == "compiled_pdf" and item["path"].endswith("main.pdf") for item in bundle_files)
    assert any(item["type"] == "compile_runtime_evidence_json" for item in bundle_files)
    checklist_artifact = next(item for item in bundle_files if item["type"] == "paper_compile_checklist_json")
    checklist = json.loads((tmp_path / checklist_artifact["path"]).read_text(encoding="utf-8"))
    assert checklist["runtime_semantic"]["verified"] is True
    assert checklist["approval_contract"]["semantic_runtime"]["verified"] is True
    assert "approved side-effect executor" in " ".join(evidence["limitations"])


def test_autosci_skill_shim_executes_approved_paper_compile_with_pdflatex_fallback(tmp_path: Path) -> None:
    paper_dir = tmp_path / "approved-pdflatex-paper"
    paper_dir.mkdir()
    (paper_dir / "main.tex").write_text(
        "\\documentclass{article}\n\\begin{document}\nApproved pdflatex fallback compile.\n\\end{document}\n",
        encoding="utf-8",
    )
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_pdflatex = fake_bin / "pdflatex"
    fake_pdflatex.write_text(
        "#!/usr/bin/env python3\n"
        "from pathlib import Path\n"
        "Path('main.pdf').write_text('%PDF-1.4\\n', encoding='utf-8')\n"
        "print('fake pdflatex completed')\n",
        encoding="utf-8",
    )
    fake_pdflatex.chmod(0o755)
    allowlist = tmp_path / "compile-pdflatex-allowlist.json"
    before = tmp_path / "compile-pdflatex-before.json"
    allowlist.write_text(json.dumps({"executables": ["pdflatex"]}), encoding="utf-8")
    before.write_text(json.dumps({"paper_dir": str(paper_dir), "pdf_exists": False}), encoding="utf-8")

    proc = run_shim(
        tmp_path,
        "$paper-compile",
        str(paper_dir),
        "--checklist",
        "--approval-ref",
        "approval-execute-pdflatex-compile",
        "--allowlist-evidence",
        str(allowlist),
        "--before-artifact",
        str(before),
        "--execute-approved",
        "--run-id",
        "shim-paper-compile-pdflatex-executor",
        extra_env={"PATH": f"{fake_bin}{os.pathsep}{os.environ.get('PATH', '')}"},
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    assert evidence["status"] == "completed"
    checklist_artifact = next(
        item for item in evidence["outputs"]["bundle"]["files"] if item["type"] == "paper_compile_checklist_json"
    )
    checklist = json.loads((tmp_path / checklist_artifact["path"]).read_text(encoding="utf-8"))
    assert checklist["toolchain"]["selected_executor"] == "pdflatex"
    assert checklist["runtime_semantic"]["verified"] is True
    runtime_artifact = next(
        item for item in evidence["outputs"]["bundle"]["files"] if item["type"] == "compile_runtime_evidence_json"
    )
    runtime = json.loads((tmp_path / runtime_artifact["path"]).read_text(encoding="utf-8"))
    assert runtime["outputs"]["runtime"]["tex_executor"] == "pdflatex"
    assert "paper-compile-runtime:pdflatex" in runtime["outputs"]["runtime"]["evidence_ids"]


def test_autosci_skill_shim_executes_approved_poster_executor(tmp_path: Path) -> None:
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_renderer = fake_bin / "poster-renderer"
    fake_renderer.write_text(
        "#!/usr/bin/env python3\n"
        "import json\n"
        "import sys\n"
        "from pathlib import Path\n"
        "html, png, validation = sys.argv[1:4]\n"
        "assert Path(html).exists()\n"
        "Path(png).write_bytes(b'\\x89PNG\\r\\n\\x1a\\n')\n"
        "Path(validation).write_text(json.dumps({\n"
        "  'browser_rendered': True,\n"
        "  'png_exported': True,\n"
        "  'overflow_probe': 'passed'\n"
        "}), encoding='utf-8')\n"
        "print('fake poster renderer completed')\n",
        encoding="utf-8",
    )
    fake_renderer.chmod(0o755)
    allowlist = tmp_path / "poster-allowlist.json"
    before = tmp_path / "poster-before.json"
    allowlist.write_text(
        json.dumps({"poster_render_command": [str(fake_renderer), "{html}", "{png}", "{validation}"]}),
        encoding="utf-8",
    )
    before.write_text(json.dumps({"poster_png": False}), encoding="utf-8")

    proc = run_shim(
        tmp_path,
        "$poster",
        "report-001",
        "--approval-ref",
        "approval-execute-poster",
        "--allowlist-evidence",
        str(allowlist),
        "--before-artifact",
        str(before),
        "--execute-approved",
        "--run-id",
        "shim-poster-executor",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    assert action["action"] == "build_poster"
    evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    assert evidence["status"] == "inconclusive"
    bundle_files = evidence["outputs"]["bundle"]["files"]
    assert any(item["type"] == "poster_runtime_evidence_json" for item in bundle_files)
    assert any(item["type"] == "poster_runtime_after_artifact" and item["path"].endswith("poster.png") for item in bundle_files)
    validation_artifact = next(item for item in bundle_files if item["type"] == "poster_validation_json")
    validation = json.loads((tmp_path / validation_artifact["path"]).read_text(encoding="utf-8"))
    assert validation["runtime_semantic"]["verified"] is True
    assert validation["browser_rendered"] is True
    assert validation["png_exported"] is True
    contract_artifact = next(item for item in bundle_files if item["type"] == "approval_contract_json")
    contract = json.loads((tmp_path / contract_artifact["path"]).read_text(encoding="utf-8"))
    assert contract["semantic_runtime"]["verified"] is True
    assert "approved side-effect executor" in " ".join(evidence["limitations"])


def test_autosci_skill_shim_accepts_paper_compile_checklist_without_bundle_fallback(tmp_path: Path) -> None:
    paper_dir = tmp_path / "paper"
    paper_dir.mkdir()
    (paper_dir / "main.tex").write_text(
        "\\documentclass{article}\n\\begin{document}\nSkillGen paper draft.\n\\end{document}\n",
        encoding="utf-8",
    )
    proc = run_shim(
        tmp_path,
        "$paper-compile",
        str(paper_dir),
        "--checklist",
        "--run-id",
        "shim-paper-compile-native",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "paper-compile"
    assert summary["execution_status"] == "gated"
    assert summary["action_count"] == 1
    assert summary["schema_only_count"] == 1

    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    assert payload["inputs"]["target"] == str(paper_dir)
    assert payload["inputs"]["native_options"]["checklist"] is True
    action = payload["outputs"]["skill_run"]["actions"][0]
    assert action["action"] == "compile_paper"
    assert action["schema"] == "publication_bundle.v1"
    assert action["gate_status"] == "schema_only"
    evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    assert evidence["status"] == "inconclusive"
    bundle = evidence["outputs"]["bundle"]
    assert bundle["publication_type"] == "paper"
    assert any(item["type"] == "paper_compile_checklist_json" for item in bundle["files"])
    assert any(item["type"] == "paper_compile_diagnostics_markdown" for item in bundle["files"])
    assert any(item["type"] == "latex_source" for item in bundle["files"])
    assert not any(item["type"] == "compiled_pdf" for item in bundle["files"])
    checklist_path = tmp_path / "artifacts/autosci/runs/shim-paper-compile-native/paper_compile_checklist.json"
    diagnostics_path = tmp_path / "artifacts/autosci/runs/shim-paper-compile-native/paper_compile_diagnostics.md"
    assert checklist_path.exists()
    assert diagnostics_path.exists()
    checklist = json.loads(checklist_path.read_text(encoding="utf-8"))
    assert checklist["status"] == "inconclusive"
    assert checklist["latex_files"] == ["paper/main.tex"]
    assert "compiled PDF" in diagnostics_path.read_text(encoding="utf-8")


def test_autosci_skill_shim_runs_ideate_from_wiki_and_discovery_sources(tmp_path: Path) -> None:
    wiki_root = tmp_path / "artifacts/autosci/workspace/wiki"
    (wiki_root / "papers").mkdir(parents=True)
    (wiki_root / "methods").mkdir(parents=True)
    (wiki_root / "graph").mkdir(parents=True)
    (wiki_root / "papers/skillgen.md").write_text(
        "---\ntitle: SkillGen Paper\n---\n# SkillGen Paper\n\nSkill generation exposes an inference-time adaptation gap.\n",
        encoding="utf-8",
    )
    (wiki_root / "methods/adaptation.md").write_text(
        "---\ntitle: Inference-Time Adaptation\n---\n# Inference-Time Adaptation\n\nA reusable method with open evaluation questions.\n",
        encoding="utf-8",
    )
    (wiki_root / "graph/open_questions.md").write_text(
        "# Open Questions\n\n- How should generated skills be validated against baseline tools?\n",
        encoding="utf-8",
    )
    discovery_dir = tmp_path / "artifacts/autosci/runs/discover-seed"
    discovery_dir.mkdir(parents=True)
    discovery_path = discovery_dir / "literature_discovery.json"
    discovery_path.write_text(
        json.dumps(
            {
                "schema": "literature_discovery.v1",
                "task_id": "discover-seed",
                "sprint_id": "test",
                "node_id": "discover",
                "status": "completed",
                "inputs": {},
                "outputs": {
                    "candidates": [
                        {
                            "paper_id": "paper-discovery-001",
                            "title": "Recent Agent Skill Adaptation",
                            "summary": "A recent paper about adapting agent skills at inference time.",
                        }
                    ]
                },
                "artifacts": [],
                "provenance": {
                    "operator_id": "test",
                    "implementation_package": "test",
                    "timestamp": "2026-06-24T00:00:00Z",
                },
                "limitations": [],
            }
        ),
        encoding="utf-8",
    )

    proc = run_shim(
        tmp_path,
        "$ideate",
        "agent skill learning",
        "--from-wiki",
        "--discovery-evidence",
        str(discovery_path),
        "--run-id",
        "shim-ideate-real-sources",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "ideate"
    assert summary["execution_status"] == "partial"
    assert summary["action_count"] == 2

    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    assert payload["inputs"]["target"] == "agent skill learning"
    actions = payload["outputs"]["skill_run"]["actions"]
    idea_evidence = json.loads(Path(actions[0]["evidence_path"]).read_text(encoding="utf-8"))
    evaluation_evidence = json.loads(Path(actions[1]["evidence_path"]).read_text(encoding="utf-8"))
    ideas = idea_evidence["outputs"]["ideas"]
    assert ideas
    assert ideas[0]["source_mode"] == "mixed"
    assert all("fixture" not in json.dumps(idea).lower() for idea in ideas)
    evaluation = evaluation_evidence["outputs"]["evaluations"][0]
    assert evaluation["recommendation"] in {"advance", "revise"}
    assert evaluation["review_mode"] == "local_surrogate"
    assert evaluation["review_available"] is False
    assert evaluation["closest_prior_work"]
    assert evaluation["review_score"] != "N/A"


def test_autosci_skill_shim_ideate_uses_model_command_for_brainstorm(tmp_path: Path) -> None:
    wiki_root = tmp_path / "artifacts/autosci/workspace/wiki"
    (wiki_root / "papers").mkdir(parents=True)
    (wiki_root / "papers/skillgen.md").write_text(
        "---\ntitle: SkillGen Paper\n---\n# SkillGen Paper\n\nSkill generation exposes an inference-time adaptation gap.\n",
        encoding="utf-8",
    )
    model_command = tmp_path / "ideate_model_command.py"
    model_command.write_text(
        "\n".join(
            [
                "import json",
                "import sys",
                "request = json.loads(sys.stdin.read())",
                "assert request['action'] == 'generate_ideas'",
                "assert request['context']['topic'] == 'agent skill learning'",
                "payload = {",
                "    'schema': 'autosci_model_response.v1',",
                "    'status': 'completed',",
                "    'outputs': {",
                "        'answer': 'Model brainstorm grounded in SkillGen paper evidence.',",
                "        'confidence': 0.72,",
                "        'provider': 'test-model-provider',",
                "        'model': 'gpt-5.5-test-double',",
                "        'evidence_ids': ['wiki:papers/skillgen'],",
                "        'ideas': [",
                "            {",
                "                'idea_id': 'idea-model-skillgen-001',",
                "                'title': 'Verifier-gated skill transfer benchmark',",
                "                'hypothesis': 'Verifier-gated generated skills transfer more reliably across held-out agent tasks.',",
                "                'approach': 'Build a benchmark that compares generated skills with and without verifier gates across held-out tasks.',",
                "                'novelty_hypothesis': 'The contribution is a source-grounded transfer benchmark for generated agent skills.',",
                "                'origin_evidence_ids': ['wiki:papers/skillgen'],",
                "                'duplicate_status': 'unknown',",
                "            }",
                "        ],",
                "    },",
                "}",
                "print(json.dumps(payload))",
            ]
        ),
        encoding="utf-8",
    )

    proc = run_shim(
        tmp_path,
        "$ideate",
        "agent skill learning",
        "--from-wiki",
        "--model-command",
        f"{shlex.quote(sys.executable)} {shlex.quote(str(model_command))}",
        "--run-id",
        "shim-ideate-model-command",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "ideate"
    assert summary["action_count"] == 2

    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    actions = payload["outputs"]["skill_run"]["actions"]
    idea_evidence = json.loads(Path(actions[0]["evidence_path"]).read_text(encoding="utf-8"))
    assert idea_evidence["status"] == "completed"
    idea = idea_evidence["outputs"]["ideas"][0]
    assert idea["idea_id"] == "idea-model-skillgen-001"
    assert idea["generation_path"] == "model-command"
    assert idea["model"] == "gpt-5.5-test-double"
    assert "wiki:papers/skillgen" in idea["origin_evidence_ids"]
    artifact_types = {artifact["type"] for artifact in idea_evidence["artifacts"]}
    assert {"model_command_stdout_json", "model_command_stderr"} <= artifact_types

    evaluation_evidence = json.loads(Path(actions[1]["evidence_path"]).read_text(encoding="utf-8"))
    evaluation = evaluation_evidence["outputs"]["evaluations"][0]
    assert evaluation["idea_id"] == "idea-model-skillgen-001"
    assert evaluation["review_mode"] == "local_surrogate"


def test_autosci_skill_shim_wiki_state_resolver_parses_entities_and_edges(tmp_path: Path) -> None:
    wiki_root = tmp_path / "artifacts/autosci/workspace/wiki"
    (wiki_root / "ideas").mkdir(parents=True)
    (wiki_root / "experiments").mkdir(parents=True)
    (wiki_root / "outputs/exp-skillgen").mkdir(parents=True)
    (wiki_root / "graph").mkdir(parents=True)
    (wiki_root / "papers").mkdir(parents=True)
    (wiki_root / "papers/skillgen.md").write_text(
        "---\ntitle: SkillGen Prior Work\n---\n# SkillGen Prior Work\n\nPrior work on generated skills.\n",
        encoding="utf-8",
    )
    (wiki_root / "ideas/skillgen.md").write_text(
        "\n".join(
            [
                "---",
                "id: idea-skillgen",
                "slug: skillgen",
                "title: SkillGen Idea",
                "status: proposed",
                "novelty_score: 0.82",
                "linked_experiments: [exp-skillgen]",
                "---",
                "# SkillGen Idea",
                "",
                "Generated skills for inference-time agents.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (wiki_root / "experiments/exp-skillgen.md").write_text(
        "\n".join(
            [
                "---",
                "experiment_id: exp-skillgen",
                "idea_id: idea-skillgen",
                "slug: exp-skillgen",
                "status: collected",
                "run_log: ../outputs/exp-skillgen/run_log.json",
                "---",
                "# SkillGen Experiment",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (wiki_root / "outputs/exp-skillgen/result.md").write_text(
        "---\noutput_id: output-skillgen\nexperiment_id: exp-skillgen\nstatus: ready\n---\n# Result\n",
        encoding="utf-8",
    )
    (wiki_root / "outputs/exp-skillgen/run_log.json").write_text('{"ok": true}\n', encoding="utf-8")
    (wiki_root / "graph/edges.jsonl").write_text(
        "\n".join(
            [
                json.dumps({"source": "idea-skillgen", "target": "exp-skillgen", "relation": "tested_by"}),
                json.dumps({"source": "exp-skillgen", "target": "output-skillgen", "relation": "produced"}),
                "",
            ]
        ),
        encoding="utf-8",
    )

    proc = run_shim(
        tmp_path,
        "$ideate",
        "skillgen",
        "--from-wiki",
        "--wiki-root",
        str(wiki_root),
        "--run-id",
        "shim-wiki-state-resolver",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    actions = payload["outputs"]["skill_run"]["actions"]
    idea_evidence = json.loads(Path(actions[0]["evidence_path"]).read_text(encoding="utf-8"))
    resolver_artifact = next(artifact for artifact in idea_evidence["artifacts"] if artifact["type"] == "wiki_state_resolver_json")
    resolver = json.loads((tmp_path / resolver_artifact["path"]).read_text(encoding="utf-8"))

    assert resolver["schema"] == "autosci_wiki_state_resolver.v1"
    assert resolver["status"] == "completed"
    assert resolver["resolution"]["target_type"] == "idea"
    assert resolver["resolution"]["target_id"] == "idea-skillgen"
    assert resolver["resolution"]["fallback_used"] is False
    assert resolver["ideas"][0]["novelty_score"] == 0.82
    assert resolver["ideas"][0]["linked_experiments"] == ["exp-skillgen"]
    assert resolver["experiments"][0]["run_log_exists"] is True
    assert resolver["experiments"][0]["linked_outputs"] == ["output-skillgen"]
    assert len(resolver["graph_edges"]) == 2
    assert resolver["graph_errors"] == []

    evaluation_evidence = json.loads(Path(actions[1]["evidence_path"]).read_text(encoding="utf-8"))
    assert any(artifact["type"] == "wiki_state_resolver_json" for artifact in evaluation_evidence["artifacts"])


def test_autosci_skill_shim_exp_status_resolves_wiki_experiment_without_default_fallback(tmp_path: Path) -> None:
    wiki_root = tmp_path / "artifacts/autosci/workspace/wiki"
    (wiki_root / "experiments").mkdir(parents=True)
    (wiki_root / "outputs/exp-skillgen").mkdir(parents=True)
    (wiki_root / "graph").mkdir(parents=True)
    (wiki_root / "experiments/exp-skillgen.md").write_text(
        "\n".join(
            [
                "---",
                "experiment_id: exp-skillgen",
                "slug: exp-skillgen",
                "status: running",
                "run_log: ../outputs/exp-skillgen/run_log.json",
                "---",
                "# SkillGen Experiment",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (wiki_root / "outputs/exp-skillgen/run_log.json").write_text('{"status": "running"}\n', encoding="utf-8")

    proc = run_shim(
        tmp_path,
        "$exp-status",
        "exp-skillgen",
        "--wiki-root",
        str(wiki_root),
        "--run-id",
        "shim-exp-status-wiki-state",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    status_evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))

    assert status_evidence["outputs"]["status_report"]["experiment_id"] == "exp-skillgen"
    assert status_evidence["outputs"]["status_report"]["experiment_id"] != "exp-001"
    resolver_artifact = next(artifact for artifact in status_evidence["artifacts"] if artifact["type"] == "wiki_state_resolver_json")
    resolver = json.loads((tmp_path / resolver_artifact["path"]).read_text(encoding="utf-8"))
    assert resolver["resolution"]["target_type"] == "experiment"
    assert resolver["resolution"]["target_id"] == "exp-skillgen"
    assert resolver["experiments"][0]["run_log_exists"] is True


def test_autosci_skill_shim_ideate_without_sources_is_inconclusive_not_fixture(tmp_path: Path) -> None:
    proc = run_shim(
        tmp_path,
        "$ideate",
        "agent skill learning",
        "--run-id",
        "shim-ideate-missing-sources",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "ideate"
    assert summary["execution_status"] == "partial"
    assert summary["action_count"] == 2

    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    actions = payload["outputs"]["skill_run"]["actions"]
    idea_evidence = json.loads(Path(actions[0]["evidence_path"]).read_text(encoding="utf-8"))
    evaluation_evidence = json.loads(Path(actions[1]["evidence_path"]).read_text(encoding="utf-8"))
    idea = idea_evidence["outputs"]["ideas"][0]
    evaluation = evaluation_evidence["outputs"]["evaluations"][0]
    assert idea_evidence["status"] == "inconclusive"
    assert idea["source_mode"] == "missing"
    assert idea["status"] == "blocked"
    assert evaluation["recommendation"] == "inconclusive"
    assert "fixture" not in json.dumps(idea_evidence).lower()


def test_autosci_skill_shim_runs_novelty_target_with_local_sources(tmp_path: Path) -> None:
    wiki_root = tmp_path / "artifacts/autosci/workspace/wiki"
    (wiki_root / "papers").mkdir(parents=True)
    (wiki_root / "ideas").mkdir(parents=True)
    (wiki_root / "papers/skillgen.md").write_text(
        "---\ntitle: SkillGen Prior Work\n---\n# SkillGen Prior Work\n\nPrior work studies generated skills for inference-time agents.\n",
        encoding="utf-8",
    )
    (wiki_root / "ideas/failed-skillgen.md").write_text(
        "---\ntitle: Failed SkillGen Duplicate\nstatus: failed\nfailure_reason: too similar to generated skills prior work\n---\n# Failed SkillGen Duplicate\n",
        encoding="utf-8",
    )

    proc = run_shim(
        tmp_path,
        "$novelty",
        "generated skills for inference-time agents",
        "--from-wiki",
        "--run-id",
        "shim-novelty-local",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "novelty"
    assert summary["execution_status"] == "partial"
    assert summary["action_count"] == 1

    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    evaluation_evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    evaluation = evaluation_evidence["outputs"]["evaluations"][0]
    assert evaluation["source_mode"] == "target"
    assert evaluation["closest_prior_work"]
    assert evaluation["review_mode"] == "local_surrogate"
    assert evaluation["review_llm"]["status"] == "unavailable"
    assert evaluation["external_novelty"]["status"] == "unavailable"
    assert evaluation["recommendation"] in {"revise", "reject", "inconclusive"}
    assert "fixture" not in json.dumps(evaluation_evidence).lower()


def test_autosci_skill_shim_novelty_defaults_to_online_fetch_when_available(tmp_path: Path) -> None:
    semantic_payload = tmp_path / "semantic_scholar_mock.json"
    archive_dir = tmp_path / "novelty-archive"
    archive_dir.mkdir()
    semantic_payload.write_text(
        json.dumps(
            {
                "data": [
                    {
                        "paperId": "s2-123",
                        "title": "Online Prior Work on Generated Skills",
                        "abstract": "Synthetic benchmark for inference-time agents.",
                        "url": "https://example.invalid/s2-123",
                        "authors": [{"name": "Open Researcher"}],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    proc = run_shim(
        tmp_path,
        "$novelty",
        "generated skills for inference-time agents",
        "--from-wiki",
        "--run-id",
        "shim-novelty-default-online",
        extra_env={
            "AUTOSCI_SEMANTIC_SCHOLAR_SEARCH_URL": f"file://{semantic_payload}",
            "AUTOSCI_NOVELTY_PAYLOAD_ARCHIVE_DIR": str(archive_dir),
        },
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    evaluation_evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    evaluation = evaluation_evidence["outputs"]["evaluations"][0]

    assert evaluation["source_mode"] == "target"
    assert evaluation["external_novelty"]["status"] == "completed"
    assert evaluation["external_novelty"]["source_count"] >= 1
    provider_status = next(
        item for item in evaluation["external_novelty"]["provider_statuses"] if item.get("provider") == "semantic_scholar"
    )
    assert provider_status["raw_payload_ref"] == semantic_payload.as_uri()
    assert provider_status["raw_payload_archive_status"] == "completed"
    assert Path(provider_status["raw_payload_archive_path"]).is_file()


def test_autosci_skill_shim_novelty_uses_supplied_external_evidence(tmp_path: Path) -> None:
    external_path = tmp_path / "semantic-scholar-novelty.json"
    external_path.write_text(
        json.dumps(
            {
                "schema": "external_novelty_sources.v1",
                "status": "completed",
                "inputs": {"query": "generated skills for inference-time agents"},
                "outputs": {
                    "sources": [
                        {
                            "id": "s2-001",
                            "provider": "semantic_scholar",
                            "paperId": "s2-001",
                            "title": "Generated Skills for Inference-Time Agents",
                            "summary": "Prior work studies generated skills for inference-time agent adaptation.",
                            "url": "https://example.invalid/s2-001",
                        }
                    ]
                },
                "provenance": {
                    "operator_id": "test",
                    "implementation_package": "test",
                    "timestamp": "2026-06-24T00:00:00Z",
                },
            }
        ),
        encoding="utf-8",
    )

    proc = run_shim(
        tmp_path,
        "$novelty",
        "generated skills for inference-time agents",
        "--novelty-evidence",
        str(external_path),
        "--run-id",
        "shim-novelty-external",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "novelty"
    assert summary["execution_status"] == "partial"
    assert summary["action_count"] == 1

    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    evaluation_evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    evaluation = evaluation_evidence["outputs"]["evaluations"][0]
    assert evaluation["source_mode"] == "target"
    assert evaluation["review_mode"] == "local_surrogate"
    assert evaluation["review_llm"]["status"] == "unavailable"
    assert evaluation["external_novelty"]["status"] == "completed"
    assert evaluation["external_novelty"]["provenance"]["status"] == "passed"
    assert "raw_payload_sha256" in evaluation["external_novelty"]["provenance"]["required_fields"]
    provider_status = evaluation["external_novelty"]["provider_statuses"][0]
    assert re.fullmatch(r"[a-f0-9]{64}", provider_status["raw_payload_sha256"])
    assert provider_status["raw_payload_refs"] == [str(external_path)]
    assert provider_status["raw_payload_archive_status"] == "completed"
    assert Path(provider_status["raw_payload_archive_path"]).exists()
    assert evaluation["external_source_count"] == 1
    assert evaluation["closest_prior_work"][0]["source_id"].startswith("external:semantic_scholar:")
    assert str(external_path) in evaluation["external_novelty"]["checked_paths"]
    artifact_paths = [artifact["path"] for artifact in evaluation_evidence["artifacts"]]
    assert any("external_novelty_payloads" in path for path in artifact_paths)
    assert "fixture" not in json.dumps(evaluation_evidence).lower()


def test_autosci_skill_shim_novelty_requires_provider_specific_semantic_scholar_id(tmp_path: Path) -> None:
    external_path = tmp_path / "semantic-scholar-url-only.json"
    external_path.write_text(
        json.dumps(
            {
                "schema": "external_novelty_sources.v1",
                "status": "completed",
                "inputs": {"query": "generated skills for inference-time agents"},
                "outputs": {
                    "sources": [
                        {
                            "provider": "semantic_scholar",
                            "title": "Generated Skills for Inference-Time Agents",
                            "summary": "Prior work studies generated skills for inference-time agent adaptation.",
                            "url": "https://example.invalid/s2-url-only",
                        }
                    ]
                },
                "provenance": {
                    "operator_id": "test",
                    "implementation_package": "test",
                    "timestamp": "2026-06-24T00:00:00Z",
                },
            }
        ),
        encoding="utf-8",
    )

    proc = run_shim(
        tmp_path,
        "$novelty",
        "generated skills for inference-time agents",
        "--novelty-evidence",
        str(external_path),
        "--run-id",
        "shim-novelty-semantic-url-only",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    evaluation_evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    external = evaluation_evidence["outputs"]["evaluations"][0]["external_novelty"]
    assert external["status"] == "completed"
    assert external["provenance"]["status"] == "failed"
    assert external["provenance"]["provider_schemas"] == ["semantic_scholar"]
    assert any("semantic_scholar requires paperId" in issue for issue in external["provenance"]["issues"])


def test_autosci_skill_shim_novelty_online_fetch_degrades_when_network_disabled(tmp_path: Path) -> None:
    proc = run_shim(
        tmp_path,
        "$novelty",
        "generated skills for inference-time agents",
        "--online",
        "--run-id",
        "shim-novelty-online-disabled",
        extra_env={"AUTOSCI_DISABLE_NETWORK_FETCH": "1"},
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    evaluation_evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    evaluation = evaluation_evidence["outputs"]["evaluations"][0]
    assert evaluation["external_novelty"]["status"] == "unavailable"
    assert "disabled" in evaluation["external_novelty"]["reason"]


def test_autosci_skill_shim_novelty_online_fetch_uses_configured_web_provider(tmp_path: Path) -> None:
    web_payload = tmp_path / "web-novelty.json"
    web_payload.write_text(
        json.dumps(
            {
                "organic": [
                    {
                        "title": "Generated Skills for Inference-Time Agents",
                        "link": "https://example.invalid/generated-skills",
                        "snippet": "A web result about generated skills for inference-time agents.",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    proc = run_shim(
        tmp_path,
        "$novelty",
        "generated skills for inference-time agents",
        "--online",
        "--run-id",
        "shim-novelty-online-web",
        extra_env={
            "AUTOSCI_NOVELTY_PROVIDERS": "web",
            "AUTOSCI_WEB_SEARCH_EVIDENCE_URL": web_payload.as_uri(),
        },
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    evaluation_evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    evaluation = evaluation_evidence["outputs"]["evaluations"][0]
    external = evaluation["external_novelty"]
    assert external["status"] == "completed"
    assert external["source_count"] == 1
    assert external["provider_statuses"][0]["provider"] == "web"
    assert external["provider_statuses"][0]["status"] == "completed"
    assert re.fullmatch(r"[a-f0-9]{64}", external["provider_statuses"][0]["raw_payload_sha256"])
    assert external["provider_statuses"][0]["raw_payload_archive_status"] == "completed"
    assert Path(external["provider_statuses"][0]["raw_payload_archive_path"]).exists()
    assert external["provenance"]["status"] == "passed"
    artifact_paths = [artifact["path"] for artifact in evaluation_evidence["artifacts"]]
    assert any("external_novelty_payloads" in path for path in artifact_paths)
    assert evaluation["closest_prior_work"][0]["source_id"].startswith("external:web:")
    assert "fixture" not in json.dumps(evaluation_evidence).lower()


def test_autosci_skill_shim_novelty_write_skips_without_external_evidence(tmp_path: Path) -> None:
    wiki_root = tmp_path / "artifacts/autosci/workspace/wiki"
    (wiki_root / "papers").mkdir(parents=True)
    (wiki_root / "ideas").mkdir(parents=True)
    (wiki_root / "papers/skillgen.md").write_text(
        "---\ntitle: SkillGen Prior Work\n---\n# SkillGen Prior Work\n\nPrior work studies generated skills for inference-time agents.\n",
        encoding="utf-8",
    )
    idea_path = wiki_root / "ideas/skillgen-writeback.md"
    idea_path.write_text(
        "---\ntitle: SkillGen Writeback\nstatus: proposed\nnovelty_score: 0\n---\n# SkillGen Writeback\n\nGenerated skills for inference-time agents.\n",
        encoding="utf-8",
    )

    proc = run_shim(
        tmp_path,
        "$novelty",
        "skillgen-writeback",
        "--from-wiki",
        "--write",
        "--run-id",
        "shim-novelty-write",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "novelty"
    assert summary["execution_status"] == "partial"
    assert summary["action_count"] == 1

    updated = idea_path.read_text(encoding="utf-8")
    assert "novelty_score: 0" in updated
    assert not (wiki_root / "log.md").exists()

    result_path = tmp_path / "artifacts/autosci/runs/shim-novelty-write/evaluate_ideas.result.json"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    sidecars = result["sidecar_evidence_paths"]
    assert result["novelty_writeback_path"] in sidecars
    writeback = json.loads((tmp_path / result["novelty_writeback_path"]).read_text(encoding="utf-8"))
    assert writeback["schema"] == "novelty_writeback.v1"
    assert writeback["status"] == "inconclusive"
    assert writeback["outputs"]["write"]["applied"] is False
    assert writeback["outputs"]["write"]["external_novelty_status"] == "unavailable"
    assert writeback["outputs"]["write"]["review_llm_status"] == "unavailable"
    assert "completed external novelty evidence is required" in " ".join(writeback["limitations"])


def test_autosci_skill_shim_novelty_write_skips_without_review_llm_evidence(tmp_path: Path) -> None:
    wiki_root = tmp_path / "artifacts/autosci/workspace/wiki"
    (wiki_root / "papers").mkdir(parents=True)
    (wiki_root / "ideas").mkdir(parents=True)
    (wiki_root / "papers/skillgen.md").write_text(
        "---\ntitle: SkillGen Prior Work\n---\n# SkillGen Prior Work\n\nPrior work studies generated skills for inference-time agents.\n",
        encoding="utf-8",
    )
    idea_path = wiki_root / "ideas/skillgen-writeback.md"
    idea_path.write_text(
        "---\ntitle: SkillGen Writeback\nstatus: proposed\nnovelty_score: 0\n---\n# SkillGen Writeback\n\nGenerated skills for inference-time agents.\n",
        encoding="utf-8",
    )
    external_path = tmp_path / "semantic-scholar-writeback.json"
    external_path.write_text(
        json.dumps(
            {
                "schema": "external_novelty_sources.v1",
                "status": "completed",
                "inputs": {"query": "skillgen-writeback"},
                "outputs": {
                    "sources": [
                        {
                            "id": "s2-writeback-001",
                            "provider": "semantic_scholar",
                            "paperId": "s2-writeback-001",
                            "title": "SkillGen Writeback and Generated Skills for Inference-Time Agents",
                            "summary": "External prior work evidence for generated skills.",
                        }
                    ]
                },
                "provenance": {
                    "operator_id": "test",
                    "implementation_package": "test",
                    "timestamp": "2026-06-24T00:00:00Z",
                },
            }
        ),
        encoding="utf-8",
    )

    proc = run_shim(
        tmp_path,
        "$novelty",
        "skillgen-writeback",
        "--from-wiki",
        "--novelty-evidence",
        str(external_path),
        "--write",
        "--run-id",
        "shim-novelty-write-external-no-review",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "novelty"
    assert summary["execution_status"] == "partial"
    assert summary["action_count"] == 1

    updated = idea_path.read_text(encoding="utf-8")
    assert "novelty_score: 0" in updated
    assert not (wiki_root / "log.md").exists()

    result_path = tmp_path / "artifacts/autosci/runs/shim-novelty-write-external-no-review/evaluate_ideas.result.json"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    writeback = json.loads((tmp_path / result["novelty_writeback_path"]).read_text(encoding="utf-8"))
    assert writeback["status"] == "inconclusive"
    assert writeback["outputs"]["write"]["applied"] is False
    assert writeback["outputs"]["write"]["external_novelty_status"] == "completed"
    assert writeback["outputs"]["write"]["external_novelty_provenance_status"] == "passed"
    assert writeback["outputs"]["write"]["review_llm_status"] == "unavailable"
    assert "completed Review LLM evidence is required" in " ".join(writeback["limitations"])


def test_autosci_skill_shim_novelty_write_updates_with_external_and_review_llm_evidence(tmp_path: Path) -> None:
    wiki_root = tmp_path / "artifacts/autosci/workspace/wiki"
    (wiki_root / "papers").mkdir(parents=True)
    (wiki_root / "ideas").mkdir(parents=True)
    (wiki_root / "papers/skillgen.md").write_text(
        "---\ntitle: SkillGen Prior Work\n---\n# SkillGen Prior Work\n\nPrior work studies generated skills for inference-time agents.\n",
        encoding="utf-8",
    )
    idea_path = wiki_root / "ideas/skillgen-writeback.md"
    idea_path.write_text(
        "---\ntitle: SkillGen Writeback\nstatus: proposed\nnovelty_score: 0\n---\n# SkillGen Writeback\n\nGenerated skills for inference-time agents.\n",
        encoding="utf-8",
    )
    external_path = tmp_path / "semantic-scholar-writeback.json"
    external_path.write_text(
        json.dumps(
            {
                "schema": "external_novelty_sources.v1",
                "status": "completed",
                "inputs": {"query": "skillgen-writeback"},
                "outputs": {
                    "sources": [
                        {
                            "id": "s2-writeback-001",
                            "provider": "semantic_scholar",
                            "paperId": "s2-writeback-001",
                            "title": "SkillGen Writeback and Generated Skills for Inference-Time Agents",
                            "summary": "External prior work evidence for generated skills.",
                        }
                    ]
                },
                "provenance": {
                    "operator_id": "test",
                    "implementation_package": "test",
                    "timestamp": "2026-06-24T00:00:00Z",
                },
            }
        ),
        encoding="utf-8",
    )
    review_llm_path = tmp_path / "review-llm-writeback.json"
    review_llm_path.write_text(
        json.dumps(
            {
                "schema": "artifact_review.v1",
                "task_id": "review-llm-writeback",
                "sprint_id": "review-llm-writeback",
                "node_id": "review-llm-writeback",
                "status": "completed",
                "inputs": {"target": "skillgen-writeback"},
                "outputs": {
                    "review": {
                        "artifact_id": "artifact:skillgen-writeback",
                        "target": "skillgen-writeback",
                        "review_mode": "review_llm",
                        "review_available": True,
                        "difficulty": "standard",
                        "focus": "novelty",
                        "score": 0.62,
                        "recommendation": "pass_with_review_required",
                        "evidence_ids": ["review-llm:writeback"],
                    },
                    "findings": [],
                    "artifact": {"artifact_id": "artifact:skillgen-writeback"},
                },
                "artifacts": [],
                "provenance": {
                    "operator_id": "review-llm-test",
                    "implementation_package": "test",
                    "timestamp": "2026-06-24T00:00:00Z",
                },
                "limitations": [],
            }
        ),
        encoding="utf-8",
    )

    proc = run_shim(
        tmp_path,
        "$novelty",
        "skillgen-writeback",
        "--from-wiki",
        "--novelty-evidence",
        str(external_path),
        "--review-llm-evidence",
        str(review_llm_path),
        "--write",
        "--run-id",
        "shim-novelty-write-reviewed",
    )
    assert proc.returncode == 0, proc.stderr

    updated = idea_path.read_text(encoding="utf-8")
    assert "novelty_score: 0" not in updated
    assert re.search(r"^novelty_score: [1-5]$", updated, flags=re.M)
    log_text = (wiki_root / "log.md").read_text(encoding="utf-8")
    assert "novelty | wrote novelty_score=" in log_text
    assert "review-llm:writeback" in log_text
    edges_text = (wiki_root / "graph/edges.jsonl").read_text(encoding="utf-8")
    assert "novelty_evaluated" in edges_text
    assert "review-llm:writeback" in edges_text
    index_text = (wiki_root / "index.md").read_text(encoding="utf-8")
    assert "ideas/skillgen-writeback.md" in index_text
    context_text = (wiki_root / "graph/context_brief.md").read_text(encoding="utf-8")
    assert "Mutation target:" in context_text

    summary = json.loads(proc.stdout)
    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    evaluation_evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    evaluation = evaluation_evidence["outputs"]["evaluations"][0]
    assert evaluation["review_mode"] == "review_llm"
    assert evaluation["review_available"] is True
    assert evaluation["review_llm"]["status"] == "completed"
    assert "review-llm:writeback" in evaluation["evidence_ids"]

    result_path = tmp_path / "artifacts/autosci/runs/shim-novelty-write-reviewed/evaluate_ideas.result.json"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    writeback = json.loads((tmp_path / result["novelty_writeback_path"]).read_text(encoding="utf-8"))
    assert writeback["status"] == "completed"
    assert writeback["outputs"]["write"]["applied"] is True
    assert writeback["outputs"]["write"]["external_novelty_status"] == "completed"
    assert writeback["outputs"]["write"]["external_novelty_provenance_status"] == "passed"
    assert writeback["outputs"]["write"]["review_llm_status"] == "completed"
    assert writeback["outputs"]["write"]["edge_path"].endswith("wiki/graph/edges.jsonl")
    assert any(path.endswith("wiki/index.md") for path in writeback["outputs"]["write"]["rebuilt_paths"])
    artifact_types = {artifact["type"] for artifact in writeback["artifacts"]}
    assert {"wiki_graph_edges", "wiki_rebuild"}.issubset(artifact_types)


def test_autosci_skill_shim_novelty_write_uses_review_llm_command_bridge(tmp_path: Path) -> None:
    wiki_root = tmp_path / "artifacts/autosci/workspace/wiki"
    (wiki_root / "papers").mkdir(parents=True)
    (wiki_root / "ideas").mkdir(parents=True)
    (wiki_root / "papers/skillgen.md").write_text(
        "---\ntitle: SkillGen Prior Work\n---\n# SkillGen Prior Work\n\nPrior work studies generated skills for inference-time agents.\n",
        encoding="utf-8",
    )
    idea_path = wiki_root / "ideas/skillgen-writeback.md"
    idea_path.write_text(
        "---\ntitle: SkillGen Writeback\nstatus: proposed\nnovelty_score: 0\n---\n# SkillGen Writeback\n\nGenerated skills for inference-time agents.\n",
        encoding="utf-8",
    )
    external_path = tmp_path / "semantic-scholar-writeback.json"
    external_path.write_text(
        json.dumps(
            {
                "schema": "external_novelty_sources.v1",
                "status": "completed",
                "inputs": {"query": "skillgen-writeback"},
                "outputs": {
                    "sources": [
                        {
                            "id": "s2-writeback-001",
                            "provider": "semantic_scholar",
                            "paperId": "s2-writeback-001",
                            "title": "SkillGen Writeback and Generated Skills for Inference-Time Agents",
                            "summary": "External prior work evidence for generated skills.",
                        }
                    ]
                },
                "provenance": {
                    "operator_id": "test",
                    "implementation_package": "test",
                    "timestamp": "2026-06-24T00:00:00Z",
                },
            }
        ),
        encoding="utf-8",
    )
    command_path = tmp_path / "review_llm_command.py"
    command_path.write_text(
        """
import json
import sys

request = json.loads(sys.stdin.read())
target = request["inputs"].get("target", "N/A")
print(json.dumps({
    "schema": "artifact_review.v1",
    "status": "completed",
    "outputs": {
        "review": {
            "artifact_id": "artifact:" + target,
            "target": target,
            "review_mode": "review_llm",
            "review_available": True,
            "difficulty": request.get("difficulty", "standard"),
            "focus": request.get("focus", "novelty"),
            "score": 0.61,
            "recommendation": "pass_with_review_required",
            "evidence_ids": ["review-llm:command-writeback"]
        },
        "findings": []
    }
}))
""".lstrip(),
        encoding="utf-8",
    )

    proc = run_shim(
        tmp_path,
        "$novelty",
        "skillgen-writeback",
        "--from-wiki",
        "--novelty-evidence",
        str(external_path),
        "--review-llm-command",
        f"{shlex.quote(sys.executable)} {shlex.quote(str(command_path))}",
        "--write",
        "--run-id",
        "shim-novelty-write-review-command",
    )
    assert proc.returncode == 0, proc.stderr

    updated = idea_path.read_text(encoding="utf-8")
    assert "novelty_score: 0" not in updated
    assert (wiki_root / "graph/edges.jsonl").exists()
    summary = json.loads(proc.stdout)
    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    evaluation_evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    evaluation = evaluation_evidence["outputs"]["evaluations"][0]
    assert evaluation["review_mode"] == "review_llm"
    assert evaluation["review_llm"]["status"] == "completed"
    assert evaluation["review_llm"]["invocation_mode"] == "command"
    assert "review-llm:command-writeback" in evaluation["evidence_ids"]


def test_autosci_skill_shim_novelty_write_skips_external_without_provenance(tmp_path: Path) -> None:
    wiki_root = tmp_path / "artifacts/autosci/workspace/wiki"
    (wiki_root / "papers").mkdir(parents=True)
    (wiki_root / "ideas").mkdir(parents=True)
    (wiki_root / "papers/skillgen.md").write_text(
        "---\ntitle: SkillGen Prior Work\n---\n# SkillGen Prior Work\n\nPrior work studies generated skills for inference-time agents.\n",
        encoding="utf-8",
    )
    idea_path = wiki_root / "ideas/skillgen-writeback.md"
    idea_path.write_text(
        "---\ntitle: SkillGen Writeback\nstatus: proposed\nnovelty_score: 0\n---\n# SkillGen Writeback\n\nGenerated skills for inference-time agents.\n",
        encoding="utf-8",
    )
    external_path = tmp_path / "semantic-scholar-bad-provenance.json"
    external_path.write_text(
        json.dumps(
            {
                "schema": "external_novelty_sources.v1",
                "status": "completed",
                "outputs": {
                    "sources": [
                        {
                            "provider": "semantic_scholar",
                            "title": "SkillGen Writeback Prior Work",
                            "summary": "A source row without durable identifiers or retrieval metadata.",
                        }
                    ]
                },
            }
        ),
        encoding="utf-8",
    )

    proc = run_shim(
        tmp_path,
        "$novelty",
        "skillgen-writeback",
        "--from-wiki",
        "--novelty-evidence",
        str(external_path),
        "--write",
        "--run-id",
        "shim-novelty-write-bad-provenance",
    )
    assert proc.returncode == 0, proc.stderr
    updated = idea_path.read_text(encoding="utf-8")
    assert "novelty_score: 0" in updated
    assert not (wiki_root / "log.md").exists()

    summary = json.loads(proc.stdout)
    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    evaluation_evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    evaluation = evaluation_evidence["outputs"]["evaluations"][0]
    assert evaluation["external_novelty"]["status"] == "completed"
    assert evaluation["external_novelty"]["provenance"]["status"] == "failed"

    result_path = tmp_path / "artifacts/autosci/runs/shim-novelty-write-bad-provenance/evaluate_ideas.result.json"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    writeback = json.loads((tmp_path / result["novelty_writeback_path"]).read_text(encoding="utf-8"))
    assert writeback["status"] == "inconclusive"
    assert writeback["outputs"]["write"]["applied"] is False
    assert writeback["outputs"]["write"]["external_novelty_status"] == "completed"
    assert writeback["outputs"]["write"]["external_novelty_provenance_status"] == "failed"
    assert "provider provenance did not pass" in " ".join(writeback["limitations"])


def test_autosci_skill_shim_runs_review_as_artifact_review(tmp_path: Path) -> None:
    wiki_root = tmp_path / "artifacts/autosci/workspace/wiki"
    (wiki_root / "outputs").mkdir(parents=True)
    review_target = wiki_root / "outputs/skillgen-review.md"
    review_target.write_text(
        "---\ntitle: SkillGen Review Target\n---\n# SkillGen Review Target\n\n"
        "The method uses a dataset, metric, baseline, evidence artifact, and claim-linked result table.\n",
        encoding="utf-8",
    )

    proc = run_shim(
        tmp_path,
        "$review",
        "skillgen-review",
        "--from-wiki",
        "--difficulty",
        "hard",
        "--focus",
        "method",
        "--run-id",
        "shim-review-artifact",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "review"
    assert summary["execution_status"] == "partial"
    assert summary["action_count"] == 1

    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    assert action["action"] == "review_artifact"
    assert action["schema"] == "artifact_review.v1"
    assert action["gate_status"] == "passed"
    review_evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    review = review_evidence["outputs"]["review"]
    assert review["review_mode"] == "local_surrogate"
    assert review["review_available"] is False
    assert review["difficulty"] == "hard"
    assert review["focus"] == "method"
    assert review["review_llm"]["status"] == "unavailable"
    assert review["review_llm"]["tool"] == "mcp__llm-review__chat"
    assert review["recommendation"] in {"pass_with_review_required", "revise", "revise_required"}
    assert "fixture" not in json.dumps(review_evidence).lower()


def test_autosci_skill_shim_review_missing_slug_does_not_use_repo_workspace_fallback(tmp_path: Path) -> None:
    proc = run_shim(
        tmp_path,
        "$review",
        "idea-001",
        "--difficulty",
        "hard",
        "--focus",
        "method",
        "--run-id",
        "shim-review-missing-slug",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "review"
    assert summary["execution_status"] == "partial"
    assert summary["action_count"] == 1
    assert summary["passed_count"] == 0
    assert summary["schema_only_count"] == 1

    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    assert action["action"] == "review_artifact"
    assert action["gate_status"] == "schema_only"
    review_evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    artifact = review_evidence["outputs"]["artifact"]
    assert review_evidence["status"] == "inconclusive"
    assert artifact["path"] == "N/A"
    checked = "\n".join(artifact["checked_paths"])
    assert "harness/artifacts/autosci/workspace/wiki/ideas/idea-001.md" not in checked
    assert any(str(tmp_path) in item for item in artifact["checked_paths"])


def test_autosci_skill_shim_review_resolves_harness_prefixed_workspace_path(tmp_path: Path) -> None:
    wiki_root = tmp_path / "artifacts" / "autosci" / "workspace" / "wiki"
    review_target = wiki_root / "ideas" / "idea-001.md"
    review_target.parent.mkdir(parents=True, exist_ok=True)
    review_target.write_text(
        "---\ntitle: Idea 001\n---\n# Idea 001\n\n"
        "The method uses a dataset, metric, baseline, evidence artifact, and claim-linked result table.\n",
        encoding="utf-8",
    )

    proc = run_shim(
        tmp_path,
        "$review",
        "harness/artifacts/autosci/workspace/wiki/ideas/idea-001.md",
        "--difficulty",
        "hard",
        "--focus",
        "method",
        "--run-id",
        "shim-review-prefixed-workspace-path",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "review"
    assert summary["execution_status"] == "partial"

    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    review_evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    artifact = review_evidence["outputs"]["artifact"]
    assert artifact["path"] != "N/A"
    assert artifact["path"].endswith("artifacts/autosci/workspace/wiki/ideas/idea-001.md")
    assert Path(artifact["path"]).is_absolute() and Path(artifact["path"]).exists()


def test_autosci_skill_shim_review_uses_supplied_review_llm_evidence(tmp_path: Path) -> None:
    wiki_root = tmp_path / "artifacts/autosci/workspace/wiki"
    (wiki_root / "outputs").mkdir(parents=True)
    review_target = wiki_root / "outputs/skillgen-review-llm.md"
    review_target.write_text(
        "---\ntitle: SkillGen Review LLM Target\n---\n# SkillGen Review LLM Target\n\n"
        "The method uses a dataset, metric, baseline, evidence artifact, and claim-linked result table.\n",
        encoding="utf-8",
    )
    llm_evidence = tmp_path / "review-llm-evidence.json"
    llm_evidence.write_text(
        json.dumps(
            {
                "schema": "artifact_review.v1",
                "task_id": "review-llm-task",
                "sprint_id": "review-llm-sprint",
                "node_id": "review-llm-node",
                "status": "completed",
                "inputs": {"target": "skillgen-review-llm"},
                "outputs": {
                    "review": {
                        "artifact_id": "artifact:skillgen-review-llm",
                        "target": "skillgen-review-llm",
                        "review_mode": "review_llm",
                        "review_available": True,
                        "difficulty": "hard",
                        "focus": "method",
                        "score": 0.42,
                        "recommendation": "revise_required",
                        "evidence_ids": ["review-llm:001"],
                    },
                    "findings": [
                        {
                            "finding_id": "review-llm.method-risk",
                            "severity": "high",
                            "category": "method",
                            "evidence": "The independent reviewer found a method risk.",
                            "suggestion": "Add an ablation and failure-mode analysis before promotion.",
                        }
                    ],
                    "artifact": {"artifact_id": "artifact:skillgen-review-llm"},
                },
                "artifacts": [],
                "provenance": {
                    "operator_id": "review-llm-test",
                    "implementation_package": "test",
                    "timestamp": "2026-06-24T00:00:00Z",
                },
                "limitations": [],
            }
        ),
        encoding="utf-8",
    )

    proc = run_shim(
        tmp_path,
        "$review",
        "skillgen-review-llm",
        "--from-wiki",
        "--difficulty",
        "hard",
        "--focus",
        "method",
        "--review-llm-evidence",
        str(llm_evidence),
        "--run-id",
        "shim-review-llm-evidence",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    assert action["schema"] == "artifact_review.v1"
    assert action["gate_status"] == "passed"

    review_evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    review = review_evidence["outputs"]["review"]
    assert review["review_mode"] == "review_llm"
    assert review["review_available"] is True
    assert review["review_llm"]["status"] == "completed"
    assert review["review_llm"]["source_path"] == str(llm_evidence)
    assert review["score"] <= 0.42
    assert review["recommendation"] == "revise_required"
    finding_ids = {finding["finding_id"] for finding in review_evidence["outputs"]["findings"]}
    assert "review-llm.method-risk" in finding_ids


def test_autosci_skill_shim_review_uses_review_llm_command_bridge(tmp_path: Path) -> None:
    wiki_root = tmp_path / "artifacts/autosci/workspace/wiki"
    (wiki_root / "outputs").mkdir(parents=True)
    review_target = wiki_root / "outputs/skillgen-review-command.md"
    review_target.write_text(
        "---\ntitle: SkillGen Review Command Target\n---\n# SkillGen Review Command Target\n\n"
        "The method uses a dataset, metric, baseline, evidence artifact, and claim-linked result table.\n",
        encoding="utf-8",
    )
    command_path = tmp_path / "review_llm_command.py"
    command_path.write_text(
        """
import json
import sys

request = json.loads(sys.stdin.read())
target = request["inputs"].get("target", "N/A")
print(json.dumps({
    "schema": "artifact_review.v1",
    "status": "completed",
    "outputs": {
        "review": {
            "artifact_id": "artifact:" + target,
            "target": target,
            "review_mode": "review_llm",
            "review_available": True,
            "difficulty": request.get("difficulty", "standard"),
            "focus": request.get("focus", "method"),
            "score": 0.52,
            "recommendation": "revise",
            "evidence_ids": ["review-llm:command"]
        },
        "findings": [{
            "finding_id": "review-llm.command-finding",
            "severity": "medium",
            "category": "method",
            "evidence": "Command bridge reviewed the target artifact.",
            "suggestion": "Keep the method evidence attached before promotion."
        }]
    }
}))
""".lstrip(),
        encoding="utf-8",
    )

    proc = run_shim(
        tmp_path,
        "$review",
        "skillgen-review-command",
        "--from-wiki",
        "--difficulty",
        "hard",
        "--focus",
        "method",
        "--review-llm-command",
        f"{shlex.quote(sys.executable)} {shlex.quote(str(command_path))}",
        "--run-id",
        "shim-review-llm-command",
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    review_evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    review = review_evidence["outputs"]["review"]
    assert review["review_mode"] == "review_llm"
    assert review["review_available"] is True
    assert review["review_llm"]["status"] == "completed"
    assert review["review_llm"]["invocation_mode"] == "command"
    assert "review-llm:command" in review["evidence_ids"]


def test_autosci_skill_shim_review_invokes_openai_compatible_provider(tmp_path: Path) -> None:
    wiki_root = tmp_path / "artifacts/autosci/workspace/wiki"
    (wiki_root / "outputs").mkdir(parents=True)
    review_target = wiki_root / "outputs/skillgen-review-provider.md"
    review_target.write_text(
        "---\ntitle: SkillGen Provider Review Target\n---\n# SkillGen Provider Review Target\n\n"
        "The method uses a dataset, metric, baseline, evidence artifact, and claim-linked result table.\n",
        encoding="utf-8",
    )
    captured: dict[str, object] = {}

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:  # noqa: N802
            length = int(self.headers.get("content-length", "0"))
            body = self.rfile.read(length).decode("utf-8")
            captured["authorization"] = self.headers.get("authorization", "")
            captured["payload"] = json.loads(body)
            content = json.dumps(
                {
                    "schema": "artifact_review.v1",
                    "status": "completed",
                    "outputs": {
                        "review": {
                            "artifact_id": "artifact:skillgen-review-provider",
                            "target": "skillgen-review-provider",
                            "review_mode": "review_llm",
                            "review_available": True,
                            "difficulty": "hard",
                            "focus": "method",
                            "score": 0.61,
                            "recommendation": "revise",
                            "evidence_ids": ["review-llm:provider"],
                        },
                        "findings": [
                            {
                                "finding_id": "review-llm.provider-finding",
                                "severity": "medium",
                                "category": "method",
                                "evidence": "Provider review saw method evidence but requested one more ablation.",
                                "suggestion": "Add an ablation result before promotion.",
                            }
                        ],
                    },
                }
            )
            response = json.dumps(
                {
                    "choices": [{"message": {"content": content}}],
                    "usage": {"prompt_tokens": 20, "completion_tokens": 40, "total_tokens": 60},
                }
            ).encode("utf-8")
            self.send_response(200)
            self.send_header("content-type", "application/json")
            self.send_header("content-length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)

        def log_message(self, format: str, *args: object) -> None:
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        endpoint = f"http://127.0.0.1:{server.server_address[1]}/v1/chat/completions"
        proc = run_shim(
            tmp_path,
            "$review",
            "skillgen-review-provider",
            "--from-wiki",
            "--review",
            "--difficulty",
            "hard",
            "--focus",
            "method",
            "--review-llm-provider",
            "openai_compatible",
            "--review-llm-model",
            "gpt-5.5",
            "--review-llm-endpoint",
            endpoint,
            "--run-id",
            "shim-review-llm-provider",
            extra_env={"OPENAI_API_KEY": "test-provider-key", "OPENROUTER_API_KEY": ""},
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    assert proc.returncode == 0, proc.stderr
    assert captured["authorization"] == "Bearer test-provider-key"
    request_payload = captured["payload"]
    assert isinstance(request_payload, dict)
    assert request_payload["model"] == "gpt-5.5"

    summary = json.loads(proc.stdout)
    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    review_evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    review = review_evidence["outputs"]["review"]
    review_llm = review["review_llm"]
    assert review["review_mode"] == "review_llm"
    assert review["review_available"] is True
    assert review_llm["status"] == "completed"
    assert review_llm["invocation_mode"] == "provider"
    assert review_llm["model"] == "gpt-5.5"
    assert review_llm["provider"] == "openai_compatible"
    assert Path(review_llm["source_path"]).exists()
    assert "review-llm:provider" in review["evidence_ids"]


def test_autosci_skill_shim_keeps_setup_gated(tmp_path: Path) -> None:
    proc = run_shim(tmp_path, "skill", "setup", "--run-id", "shim-setup")
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["execution_status"] == "gated"
    assert summary["side_effect_policy"] == "approval_required"
    assert summary["action_count"] == 1
    assert summary["passed_count"] == 1

    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    action = payload["outputs"]["skill_run"]["actions"][0]
    assert action["action"] == "setup_status"
    assert action["schema"] == "workflow_evolution.v1"
    setup_evidence = json.loads(Path(action["evidence_path"]).read_text(encoding="utf-8"))
    assert setup_evidence["outputs"]["evolution"]["approval_state"] == "proposed"
    assert setup_evidence["outputs"]["evolution"]["review"]["protected_core_edits_applied"] is False

    evidence_path = Path(summary["evidence_path"])
    gate = run_gate(evidence_path)
    assert gate.returncode == 0, gate.stdout + gate.stderr
    result = json.loads(gate.stdout)
    assert result["warnings"]
