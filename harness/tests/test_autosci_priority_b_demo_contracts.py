from __future__ import annotations

import json
import os
import subprocess
import uuid
from pathlib import Path


HARNESS = Path(__file__).resolve().parents[1]
REPO = HARNESS.parent
SOLAR_HARNESS = HARNESS / "solar-harness.sh"


def _prepare_isolated_harness(tmp_path: Path) -> Path:
    harness_dir = tmp_path / "harness"
    harness_dir.mkdir()
    for name in ("bin", "config", "personas", "tools", "plugins", "evaluators", "schemas", "lib", "templates"):
        target = HARNESS / name
        link = harness_dir / name
        if not link.exists():
            link.symlink_to(target, target_is_directory=target.is_dir())
    (harness_dir / "run").mkdir(exist_ok=True)
    (harness_dir / "artifacts").mkdir(exist_ok=True)
    return harness_dir


def _env_for(harness_dir: Path) -> dict[str, str]:
    env = dict(os.environ)
    env["HARNESS_DIR"] = str(harness_dir)
    env["SOLAR_OPERATORD_ONCE_MAX_WAIT_SECONDS"] = "20"
    env.pop("AUTOSCI_ARTIFACT_ROOT", None)
    env.pop("SCIENTIFIC_ARTIFACT_ROOT", None)
    env.pop("SOLAR_AUTOSCI_OUTPUT_HARNESS", None)
    return env


def test_research_scheduler_run_projects_human_lifecycle_summary(tmp_path: Path) -> None:
    harness_dir = _prepare_isolated_harness(tmp_path)
    run_id = f"priority-b-lifecycle-workspace-{uuid.uuid4().hex}"
    paper = harness_dir / "raw" / "priority-b-paper.md"
    paper.parent.mkdir()
    paper.write_text(
        "# Priority B Lifecycle Workspace\n\n"
        "## Abstract\n"
        "This paper verifies a human-facing lifecycle summary projection.\n\n"
        "## Results\n"
        "The scheduler run should produce node, gate, and evidence summary output.\n",
        encoding="utf-8",
    )

    proc = subprocess.run(
        [
            "bash",
            str(SOLAR_HARNESS),
            "autosci",
            f"$research priority-b lifecycle --paper {paper} --scheduler-run --scheduler-timeout 20 --run-id {run_id}",
        ],
        cwd=REPO,
        env=_env_for(harness_dir),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert proc.returncode == 0, proc.stdout + proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["scheduler_dispatch_boundary_status"] == "generic_workflow_runner"
    assert summary["scheduler_lifecycle_status"] == "passed"

    wiki_root = harness_dir / "artifacts" / "autosci" / "workspace" / "wiki"
    lifecycle_page = wiki_root / "outputs" / "lifecycle_summary.md"
    assert lifecycle_page.exists()
    page = lifecycle_page.read_text(encoding="utf-8")
    assert f"Lifecycle Summary: `{run_id}`" in page
    assert "Lifecycle status: `passed`" in page
    assert "Dispatch boundary: `generic_workflow_runner`" in page
    assert "Runtime manifest:" in page
    assert "## Node Results" in page
    assert "paper_ingest" in page
    assert "## Blocked Nodes" in page
    assert "Missing provider, model, approval, or runtime evidence remains visible" in page

    index_text = (wiki_root / "index.md").read_text(encoding="utf-8")
    assert "outputs/lifecycle_summary.md" in index_text
    assert not (HARNESS / "artifacts" / "autosci" / "runs" / run_id).exists()


def test_review_projects_human_diagnostics_summary(tmp_path: Path) -> None:
    harness_dir = _prepare_isolated_harness(tmp_path)
    run_id = f"priority-b-review-workspace-{uuid.uuid4().hex}"
    wiki_root = harness_dir / "artifacts" / "autosci" / "workspace" / "wiki"
    review_target = wiki_root / "outputs" / "priority-b-review.md"
    review_target.parent.mkdir(parents=True)
    review_target.write_text(
        "---\ntitle: Priority B Review Target\n---\n# Priority B Review Target\n\n"
        "The method describes a dataset, metric, baseline, evidence artifact, and reproducible result table.\n",
        encoding="utf-8",
    )

    proc = subprocess.run(
        [
            "bash",
            str(SOLAR_HARNESS),
            "autosci",
            f"$review priority-b-review --from-wiki --difficulty hard --focus method --run-id {run_id}",
        ],
        cwd=REPO,
        env=_env_for(harness_dir),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert proc.returncode == 0, proc.stdout + proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "review"
    assert summary["execution_status"] == "partial"
    assert summary["action_count"] == 1

    review_page = wiki_root / "outputs" / "review.md"
    assert review_page.exists()
    page = review_page.read_text(encoding="utf-8")
    assert f"Review Diagnostics: `{run_id}`" in page
    assert "- Review mode: `local_surrogate`" in page
    assert "- Review available: `False`" in page
    assert "- Final acceptance ready: `False`" in page
    assert "Review LLM" in page
    assert "review_llm_incomplete" in page
    assert "Review LLM evidence from supplied evidence, command bridge, or provider mode" in page

    index_text = (wiki_root / "index.md").read_text(encoding="utf-8")
    assert "outputs/review.md" in index_text
    assert not (HARNESS / "artifacts" / "autosci" / "runs" / run_id).exists()


def test_discover_projects_human_shortlist_summary(tmp_path: Path) -> None:
    harness_dir = _prepare_isolated_harness(tmp_path)
    run_id = f"priority-b-discover-workspace-{uuid.uuid4().hex}"
    wiki_root = harness_dir / "artifacts" / "autosci" / "workspace" / "wiki"
    (wiki_root / "papers").mkdir(parents=True)
    (wiki_root / "papers" / "skillgen-seed.md").write_text(
        "---\ntitle: SkillGen Seed\narxiv: 2401.00001\n---\n# SkillGen Seed\n\n"
        "Skill generation and agent adaptation need provider-backed literature discovery before promotion.\n",
        encoding="utf-8",
    )
    env = _env_for(harness_dir)
    env["AUTOSCI_DISABLE_NETWORK_FETCH"] = "1"

    proc = subprocess.run(
        [
            "bash",
            str(SOLAR_HARNESS),
            "autosci",
            f"$discover agent skill learning --from-wiki --limit 3 --run-id {run_id}",
        ],
        cwd=REPO,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert proc.returncode == 0, proc.stdout + proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "discover"
    assert summary["execution_status"] == "partial"
    assert summary["action_count"] == 1
    assert summary["workspace_updated_count"] > 0

    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    actions = payload["outputs"]["skill_run"]["actions"]
    assert [action["action"] for action in actions] == ["discover_literature"]
    discovery = json.loads(Path(actions[0]["evidence_path"]).read_text(encoding="utf-8"))
    assert discovery["schema"] == "literature_discovery.v1"
    assert discovery["status"] == "inconclusive"
    assert discovery["outputs"]["mode"] == "wiki"
    assert discovery["outputs"]["limit"] == 3
    boundary = discovery["outputs"]["source_provider_boundary"]["final_shortlist_boundary"]
    assert boundary["final_shortlist_ready"] is False
    assert "discovery shortlist is empty" in boundary["blocking_reasons"]
    assert "provider-backed source channel is missing" in boundary["blocking_reasons"]

    discovery_page = wiki_root / "outputs" / "discovery.md"
    assert discovery_page.exists()
    page = discovery_page.read_text(encoding="utf-8")
    assert f"Discovery Summary: `{run_id}`" in page
    assert "- Evidence status: `inconclusive`" in page
    assert "- Mode: `wiki`" in page
    assert "- Limit: `3`" in page
    assert "- Final shortlist ready: `False`" in page
    assert "literature_discovery.json" in page
    assert "discovery shortlist is empty" in page
    assert "provider-backed source channel is missing" in page
    assert "Final discovery shortlist requires non-empty candidates" in page

    index_text = (wiki_root / "index.md").read_text(encoding="utf-8")
    assert "outputs/discovery.md" in index_text
    assert not (HARNESS / "artifacts" / "autosci" / "runs" / run_id).exists()


def test_ideate_projects_human_candidate_and_evaluation_summary(tmp_path: Path) -> None:
    harness_dir = _prepare_isolated_harness(tmp_path)
    run_id = f"priority-b-ideate-workspace-{uuid.uuid4().hex}"
    wiki_root = harness_dir / "artifacts" / "autosci" / "workspace" / "wiki"
    (wiki_root / "papers").mkdir(parents=True)
    (wiki_root / "methods").mkdir(parents=True)
    (wiki_root / "graph").mkdir(parents=True)
    (wiki_root / "papers" / "skillgen.md").write_text(
        "---\ntitle: SkillGen Paper\n---\n# SkillGen Paper\n\n"
        "Skill generation exposes an inference-time adaptation gap with measurable validation needs.\n",
        encoding="utf-8",
    )
    (wiki_root / "methods" / "adaptation.md").write_text(
        "---\ntitle: Inference-Time Adaptation\n---\n# Inference-Time Adaptation\n\n"
        "A reusable method with open evaluation and robustness questions.\n",
        encoding="utf-8",
    )
    (wiki_root / "graph" / "open_questions.md").write_text(
        "# Open Questions\n\n- How should generated skills be validated against baseline tools?\n",
        encoding="utf-8",
    )
    discovery_dir = harness_dir / "artifacts" / "autosci" / "runs" / "priority-b-discover-seed"
    discovery_dir.mkdir(parents=True)
    discovery_path = discovery_dir / "literature_discovery.json"
    discovery_path.write_text(
        json.dumps(
            {
                "schema": "literature_discovery.v1",
                "task_id": "priority-b-discover-seed",
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

    proc = subprocess.run(
        [
            "bash",
            str(SOLAR_HARNESS),
            "autosci",
            (
                "$ideate agent skill learning --from-wiki "
                f"--wiki-root {wiki_root} --discovery-evidence {discovery_path} "
                f"--max-ideas 2 --run-id {run_id}"
            ),
        ],
        cwd=REPO,
        env=_env_for(harness_dir),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert proc.returncode == 0, proc.stdout + proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "ideate"
    assert summary["execution_status"] == "partial"
    assert summary["action_count"] == 2

    ideas_page = wiki_root / "outputs" / "ideas.md"
    assert ideas_page.exists()
    page = ideas_page.read_text(encoding="utf-8")
    assert f"Idea Summary: `{run_id}`" in page
    assert "- Candidate evidence status: `completed`" in page
    assert "- Evaluation evidence status: `completed`" in page
    assert "idea_promotion_incomplete" in page or "novelty_acceptance_incomplete" in page
    assert "external_novelty status is" in page
    assert "review_llm status is" in page
    assert "Independent Review LLM and live external search are still required before promotion." in page
    assert "N/A" not in page.split("## Ideas", maxsplit=1)[0]

    index_text = (wiki_root / "index.md").read_text(encoding="utf-8")
    assert "outputs/ideas.md" in index_text
    assert not (HARNESS / "artifacts" / "autosci" / "runs" / run_id).exists()


def test_ingest_projects_human_paper_workspace_page(tmp_path: Path) -> None:
    harness_dir = _prepare_isolated_harness(tmp_path)
    run_id = f"priority-b-ingest-workspace-{uuid.uuid4().hex}"
    paper = harness_dir / "raw" / "priority-b-ingest-paper.md"
    paper.parent.mkdir()
    paper.write_text(
        "# Priority B Product Ingest\n\n"
        "## Abstract\n"
        "This source verifies direct product entry for AutoSci paper ingestion.\n\n"
        "## Method\n"
        "The ingest route should emit research_paper.v1 evidence and a human-facing workspace paper page.\n",
        encoding="utf-8",
    )

    proc = subprocess.run(
        [
            "bash",
            str(SOLAR_HARNESS),
            "autosci",
            f"$ingest --paper {paper} --run-id {run_id}",
        ],
        cwd=REPO,
        env=_env_for(harness_dir),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert proc.returncode == 0, proc.stdout + proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["skill"] == "ingest"
    assert summary["execution_status"] == "partial"
    assert summary["action_count"] == 2
    assert summary["workspace_updated_count"] > 0

    payload = json.loads(Path(summary["evidence_path"]).read_text(encoding="utf-8"))
    actions = payload["outputs"]["skill_run"]["actions"]
    assert [action["action"] for action in actions] == ["ingest_paper", "analyze_paper"]
    ingest_evidence = json.loads(Path(actions[0]["evidence_path"]).read_text(encoding="utf-8"))
    assert ingest_evidence["schema"] == "research_paper.v1"
    assert ingest_evidence["status"] == "completed"
    paper_output = ingest_evidence["outputs"]["paper"]
    assert paper_output["parse_status"] == "parsed"
    assert "Priority B Product Ingest" in paper_output["title"]
    boundary = paper_output["final_source_registration_boundary"]
    assert boundary["source_preparation_verified"] is True
    assert boundary["raw_artifact_provenance_ready"] is True

    wiki_root = harness_dir / "artifacts" / "autosci" / "workspace" / "wiki"
    paper_pages = sorted((wiki_root / "papers").glob("*.md"))
    assert len(paper_pages) == 1
    page = paper_pages[0].read_text(encoding="utf-8")
    assert "# Priority B Product Ingest" in page
    assert "Evidence:" in page
    assert "research_paper.analyzed.json" in page or "research_paper.json" in page

    index_text = (wiki_root / "index.md").read_text(encoding="utf-8")
    assert f"papers/{paper_pages[0].name}" in index_text
    assert not (HARNESS / "artifacts" / "autosci" / "runs" / run_id).exists()
