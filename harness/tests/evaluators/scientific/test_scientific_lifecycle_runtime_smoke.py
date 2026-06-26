from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


HARNESS = Path(__file__).resolve().parents[3]
SMOKE = HARNESS / "tools" / "run_scientific_lifecycle_smoke.py"
LIFECYCLE_GATE = HARNESS / "evaluators" / "scientific" / "lifecycle_runtime_gate.py"


def _prepare_isolated_harness(tmp_path: Path) -> Path:
    for name in ("config", "personas", "tools", "plugins", "evaluators", "schemas", "lib", "templates"):
        target = HARNESS / name
        link = tmp_path / name
        if not link.exists():
            link.symlink_to(target, target_is_directory=True)
    (tmp_path / "run").mkdir(exist_ok=True)
    (tmp_path / "artifacts").mkdir(exist_ok=True)
    return tmp_path


def test_scientific_lifecycle_smoke_emits_runtime_gate_accepted_summary(tmp_path: Path) -> None:
    harness_dir = _prepare_isolated_harness(tmp_path)
    env = os.environ.copy()
    env["HARNESS_DIR"] = str(harness_dir)
    proc = subprocess.run(
        [
            sys.executable,
            str(SMOKE),
            "--harness-dir",
            str(harness_dir),
            "--job-id",
            "job-scientific-lifecycle-smoke-test",
            "--timeout-seconds",
            "20",
        ],
        cwd=HARNESS,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert proc.returncode == 0, proc.stdout + proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["schema"] == "scientific_lifecycle.v1"
    assert summary["workflow_id"] == "scientific_research_lifecycle_full_v1"
    assert summary["lifecycle_status"] == "passed"
    expected_actions = {
        "literature_discover": ("discover_literature", "literature_discovery.v1"),
        "paper_ingest": ("ingest_paper", "research_paper.v1"),
        "paper_analyze": ("analyze_paper", "research_paper.v1"),
        "memory_update_initial": ("update_memory", "research_memory_update.v1"),
        "graph_update": ("update_graph", "research_graph_update.v1"),
        "claim_extract": ("extract_claims", "research_claims.v1"),
        "method_extract": ("extract_methods", "research_method.v1"),
        "code_evidence_map": ("map_code_evidence", "code_evidence_map.v1"),
        "idea_generate": ("generate_ideas", "idea_candidate.v1"),
        "idea_evaluate": ("evaluate_ideas", "idea_evaluation.v1"),
        "experiment_design": ("design_experiment", "experiment_plan.v1"),
        "experiment_run": ("run_experiment", "experiment_result.v1"),
        "experiment_monitor": ("monitor_experiment", "experiment_status.v1"),
        "claim_verify": ("verify_claim", "claim_verdict.v1"),
        "report_draft": ("write_report", "scientific_report.v1"),
        "artifact_review": ("review_artifact", "artifact_review.v1"),
        "memory_update_final": ("update_memory", "research_memory_update.v1"),
        "workflow_evolve": ("evolve_workflow", "workflow_evolution.v1"),
    }
    assert summary["required_nodes"] == list(expected_actions)
    assert set(summary["node_results"]) == set(expected_actions)
    assert set(summary["gate_results"]) == set(expected_actions)
    assert summary["lifecycle_gate_result"]["ok"] is True
    assert {item["status"] for item in summary["checks"]} == {"ok"}

    for node_id, (action, schema) in expected_actions.items():
        result = summary["node_results"][node_id]
        assert result["status"] == "passed"
        assert result["action"] == action
        assert result["expected_schema"] == schema
        assert len(result["artifact_sha256"]) == 64
        assert (harness_dir / result["artifact_path"]).exists()
        assert (harness_dir / result["operator_result_path"]).exists()
        assert (harness_dir / result["bridge_result_path"]).exists()

    gate = subprocess.run(
        [
            sys.executable,
            str(LIFECYCLE_GATE),
            str(harness_dir / summary["summary_path"]),
        ],
        cwd=HARNESS,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert gate.returncode == 0, gate.stdout + gate.stderr
    gate_payload = json.loads(gate.stdout)
    assert gate_payload["ok"] is True


def test_scientific_lifecycle_smoke_can_record_external_blocked_nodes(tmp_path: Path) -> None:
    harness_dir = _prepare_isolated_harness(tmp_path)
    env = os.environ.copy()
    env["HARNESS_DIR"] = str(harness_dir)
    proc = subprocess.run(
        [
            sys.executable,
            str(SMOKE),
            "--harness-dir",
            str(harness_dir),
            "--job-id",
            "job-scientific-lifecycle-blocked-test",
            "--timeout-seconds",
            "20",
            "--include-blocked-external",
        ],
        cwd=HARNESS,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert proc.returncode == 3, proc.stdout + proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["lifecycle_status"] == "blocked"
    assert summary["lifecycle_gate_result"]["status"] == "inconclusive"
    assert set(summary["blocked_nodes"]) == {"report_plan", "publication_produce"}
    assert "report_plan" in summary["required_nodes"]
    assert "publication_produce" in summary["required_nodes"]
    assert summary["blocked_nodes"]["report_plan"]["required_evidence"]
    assert summary["blocked_nodes"]["publication_produce"]["unblock_condition"]


def test_scientific_lifecycle_smoke_records_human_gate_pause(tmp_path: Path) -> None:
    harness_dir = _prepare_isolated_harness(tmp_path)
    env = os.environ.copy()
    env["HARNESS_DIR"] = str(harness_dir)
    proc = subprocess.run(
        [
            sys.executable,
            str(SMOKE),
            "--harness-dir",
            str(harness_dir),
            "--job-id",
            "job-scientific-lifecycle-human-gate-test",
            "--timeout-seconds",
            "20",
            "--include-human-gates",
            "--idea-approval-ref",
            "approval-idea-human-gate-test",
        ],
        cwd=HARNESS,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert proc.returncode == 3, proc.stdout + proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["lifecycle_status"] == "blocked"
    assert summary["lifecycle_gate_result"]["status"] == "inconclusive"
    assert "idea_acceptance_gate" in summary["node_results"]
    assert summary["node_results"]["idea_acceptance_gate"]["approval_ref"] == "approval-idea-human-gate-test"
    assert "results_acceptance_gate" in summary["blocked_nodes"]
    assert summary["blocked_nodes"]["results_acceptance_gate"]["required_evidence"]
    assert "claim_verify" in summary["node_results"]
    assert "report_draft" not in summary["required_nodes"]
    approval_path = harness_dir / summary["node_results"]["idea_acceptance_gate"]["artifact_path"]
    approval_evidence = json.loads(approval_path.read_text(encoding="utf-8"))
    assert approval_evidence["schema"] == "workflow_evolution.v1"
    assert approval_evidence["outputs"]["evolution"]["approval_state"] == "approved"


def test_scientific_lifecycle_smoke_resumes_human_gate_pauses(tmp_path: Path) -> None:
    harness_dir = _prepare_isolated_harness(tmp_path)
    env = os.environ.copy()
    env["HARNESS_DIR"] = str(harness_dir)

    blocked_proc = subprocess.run(
        [
            sys.executable,
            str(SMOKE),
            "--harness-dir",
            str(harness_dir),
            "--job-id",
            "job-scientific-lifecycle-human-gate-resume-test",
            "--timeout-seconds",
            "20",
            "--include-human-gates",
        ],
        cwd=HARNESS,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert blocked_proc.returncode == 3, blocked_proc.stdout + blocked_proc.stderr
    blocked = json.loads(blocked_proc.stdout)
    assert set(blocked["blocked_nodes"]) == {"idea_acceptance_gate"}
    original_literature_artifact = blocked["node_results"]["literature_discover"]["artifact_path"]

    first_resume_proc = subprocess.run(
        [
            sys.executable,
            str(SMOKE),
            "--harness-dir",
            str(harness_dir),
            "--resume-summary",
            str(harness_dir / blocked["summary_path"]),
            "--idea-approval-ref",
            "approval-resume-idea-gate",
            "--timeout-seconds",
            "20",
        ],
        cwd=HARNESS,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert first_resume_proc.returncode == 3, first_resume_proc.stdout + first_resume_proc.stderr
    first_resumed = json.loads(first_resume_proc.stdout)
    assert "idea_acceptance_gate" in first_resumed["node_results"]
    assert first_resumed["node_results"]["idea_acceptance_gate"]["approval_ref"] == "approval-resume-idea-gate"
    assert set(first_resumed["blocked_nodes"]) == {"results_acceptance_gate"}
    assert "claim_verify" in first_resumed["node_results"]
    assert "report_draft" not in first_resumed["required_nodes"]
    assert first_resumed["node_results"]["literature_discover"]["artifact_path"] == original_literature_artifact

    second_resume_proc = subprocess.run(
        [
            sys.executable,
            str(SMOKE),
            "--harness-dir",
            str(harness_dir),
            "--resume-summary",
            str(harness_dir / first_resumed["summary_path"]),
            "--results-approval-ref",
            "approval-resume-results-gate",
            "--timeout-seconds",
            "20",
        ],
        cwd=HARNESS,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert second_resume_proc.returncode == 3, second_resume_proc.stdout + second_resume_proc.stderr
    second_resumed = json.loads(second_resume_proc.stdout)
    assert "results_acceptance_gate" in second_resumed["node_results"]
    assert second_resumed["node_results"]["results_acceptance_gate"]["approval_ref"] == "approval-resume-results-gate"
    assert "report_draft" in second_resumed["node_results"]
    assert "workflow_evolve" in second_resumed["node_results"]
    assert set(second_resumed["blocked_nodes"]) == {"report_plan", "publication_produce"}
    assert second_resumed["node_results"]["literature_discover"]["artifact_path"] == original_literature_artifact


def test_scientific_lifecycle_smoke_strict_online_mode_rejects_offline_fixture(tmp_path: Path) -> None:
    harness_dir = _prepare_isolated_harness(tmp_path)
    env = os.environ.copy()
    env["HARNESS_DIR"] = str(harness_dir)
    proc = subprocess.run(
        [
            sys.executable,
            str(SMOKE),
            "--harness-dir",
            str(harness_dir),
            "--job-id",
            "job-scientific-lifecycle-online-strict-test",
            "--timeout-seconds",
            "20",
            "--require-online-source-evidence",
            "--disable-fixture-fallback",
            "--discovery-query",
            "skill generation",
        ],
        cwd=HARNESS,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert proc.returncode == 1, proc.stdout + proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["lifecycle_status"] == "failed"
    assert set(summary["node_results"]) == set()
    literature_summary = summary["node_summaries"]["literature_discover"]
    assert literature_summary["status"] == "failed"
    joined_reasons = " ".join(literature_summary["gate_result"]["reasons"])
    assert "online source evidence requires completed literature discovery" in joined_reasons
    assert "online source evidence requires at least one non-fixture online source channel" in joined_reasons


def test_scientific_lifecycle_smoke_accepts_combined_full_external_evidence(tmp_path: Path) -> None:
    harness_dir = _prepare_isolated_harness(tmp_path)
    env = os.environ.copy()
    env["HARNESS_DIR"] = str(harness_dir)

    external_dir = harness_dir / "artifacts/scientific/external/source-runtime-test"
    external_dir.mkdir(parents=True)
    allowlist = external_dir / "allowlist.json"
    before = external_dir / "before.json"
    after = external_dir / "after.json"
    runtime = external_dir / "source-runtime.json"
    source_manifest = external_dir / "source-manifest.json"
    allowlist.write_text('{"allowed": ["semantic_scholar", "arxiv"]}\n', encoding="utf-8")
    before.write_text('{"state": "before-source-fetch"}\n', encoding="utf-8")
    after.write_text('{"state": "after-source-fetch", "candidates": ["runtime-source-001"]}\n', encoding="utf-8")
    source_manifest.write_text('{"candidate_ids": ["runtime-source-001"]}\n', encoding="utf-8")
    runtime.write_text(
        json.dumps(
            {
                "schema": "autosci_runtime_evidence.v1",
                "task_id": "task-source-runtime-test",
                "sprint_id": "sprint-source-runtime-test",
                "node_id": "source_runtime",
                "status": "completed",
                "inputs": {"approval_ref": "approval-source-runtime-test"},
                "outputs": {
                    "runtime": {
                        "action": "discover_literature",
                        "status": "completed",
                        "approval_ref": "approval-source-runtime-test",
                        "command_run": "approved-semantic-scholar-fetch",
                        "exit_code": 0,
                        "evidence_ids": ["runtime:source-fetch:test"],
                        "checks": [{"check": "source_fetch", "status": "ok", "detail": "one candidate"}],
                        "candidates": [
                            {
                                "candidate_id": "runtime-source-001",
                                "title": "Runtime Verified Skill Generation Source",
                                "url": "https://arxiv.org/abs/2601.00005",
                                "source_channels": ["search_s2"],
                                "ranking_score": 0.93,
                                "ranking_rationale": "Approved Semantic Scholar runtime returned this source.",
                                "dedup_status": "new",
                                "fetch_status": "fetched",
                            }
                        ],
                    }
                },
                "artifacts": [{"type": "source_manifest", "path": str(source_manifest)}],
                "provenance": {
                    "operator_id": "external-source-runtime-test",
                    "implementation_package": "harness.tests",
                    "timestamp": "2026-06-26T00:00:00Z",
                },
                "limitations": ["Runtime source evidence was supplied by the test harness."],
            }
        ),
        encoding="utf-8",
    )
    review_llm_path = external_dir / "review_llm_artifact_review.json"
    review_llm_path.write_text(
        json.dumps(
            {
                "schema": "artifact_review.v1",
                "task_id": "task-review-llm-full-external-test",
                "sprint_id": "external-review-llm-full-external-test",
                "node_id": "external_artifact_review",
                "status": "completed",
                "inputs": {"target": "scheduler-lifecycle-full-external"},
                "outputs": {
                    "review": {
                        "artifact_id": "artifact:scheduler-lifecycle-full-external",
                        "target": "scheduler-lifecycle-full-external",
                        "review_mode": "review_llm",
                        "review_available": True,
                        "difficulty": "standard",
                        "focus": "completeness",
                        "score": 0.88,
                        "recommendation": "inconclusive",
                        "evidence_ids": ["review-llm:full-external-test"],
                        "review_llm": {
                            "status": "completed",
                            "invocation_mode": "supplied_evidence",
                            "source_path": str(review_llm_path),
                        },
                    },
                    "findings": [
                        {
                            "finding_id": "review-llm.full-external.coverage",
                            "severity": "low",
                            "category": "coverage",
                            "evidence": "External Review LLM evidence was supplied for full lifecycle dispatch.",
                            "suggestion": "Proceed with paper planning while preserving evidence ids.",
                        }
                    ],
                    "artifact": {"artifact_id": "artifact:scheduler-lifecycle-full-external"},
                },
                "artifacts": [],
                "provenance": {
                    "operator_id": "external-review-llm-full-external-test",
                    "implementation_package": "harness.tests",
                    "timestamp": "2026-06-26T00:00:00Z",
                },
                "limitations": ["Test fixture supplied as explicit external Review LLM evidence."],
            }
        ),
        encoding="utf-8",
    )
    compile_target = external_dir / "compile_target"
    compile_target.mkdir()
    (compile_target / "main.tex").write_text(
        "\\documentclass{article}\\begin{document}Full external lifecycle compile target.\\end{document}\n",
        encoding="utf-8",
    )
    (compile_target / "main.pdf").write_bytes(b"%PDF-1.4\n% full external lifecycle test\n")

    proc = subprocess.run(
        [
            sys.executable,
            str(SMOKE),
            "--harness-dir",
            str(harness_dir),
            "--job-id",
            "job-scientific-lifecycle-source-runtime-test",
            "--timeout-seconds",
            "20",
            "--require-online-source-evidence",
            "--disable-fixture-fallback",
            "--discovery-query",
            "skill generation",
            "--source-approval-ref",
            "approval-source-runtime-test",
            "--source-allowlist-evidence",
            str(allowlist),
            "--source-before-artifact",
            str(before),
            "--source-after-artifact",
            str(after),
            "--source-runtime-evidence",
            str(runtime),
            "--review-llm-evidence",
            str(review_llm_path),
            "--compile-target",
            str(compile_target),
            "--dispatch-external-evidence",
        ],
        cwd=HARNESS,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert proc.returncode == 0, proc.stdout + proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["lifecycle_status"] == "passed"
    assert summary["blocked_nodes"] == {}
    literature = json.loads((harness_dir / summary["node_results"]["literature_discover"]["artifact_path"]).read_text(encoding="utf-8"))
    assert literature["status"] == "completed"
    assert literature["outputs"]["mode"] == "discover_literature_runtime_verified"
    assert literature["outputs"]["candidates"][0]["source_channels"] == ["search_s2"]
    assert "report_plan" in summary["node_results"]
    assert "publication_produce" in summary["node_results"]
    assert summary["node_results"]["report_plan"]["action"] == "plan_report"
    assert summary["node_results"]["publication_produce"]["action"] == "compile_paper"


def test_scientific_lifecycle_smoke_executes_approved_publication_compile(tmp_path: Path) -> None:
    harness_dir = _prepare_isolated_harness(tmp_path)
    env = os.environ.copy()
    env["HARNESS_DIR"] = str(harness_dir)

    external_dir = harness_dir / "artifacts/scientific/external/publication-compile-test"
    external_dir.mkdir(parents=True)
    review_llm_path = external_dir / "review_llm_artifact_review.json"
    review_llm_path.write_text(
        json.dumps(
            {
                "schema": "artifact_review.v1",
                "task_id": "task-review-llm-publication-compile-test",
                "sprint_id": "external-review-llm-publication-compile-test",
                "node_id": "external_artifact_review",
                "status": "completed",
                "inputs": {"target": "scheduler-lifecycle-publication-compile"},
                "outputs": {
                    "review": {
                        "artifact_id": "artifact:scheduler-lifecycle-publication-compile",
                        "target": "scheduler-lifecycle-publication-compile",
                        "review_mode": "review_llm",
                        "review_available": True,
                        "difficulty": "standard",
                        "focus": "completeness",
                        "score": 0.87,
                        "recommendation": "inconclusive",
                        "evidence_ids": ["review-llm:publication-compile-test"],
                    },
                    "findings": [],
                    "artifact": {"artifact_id": "artifact:scheduler-lifecycle-publication-compile"},
                },
                "artifacts": [],
                "provenance": {
                    "operator_id": "external-review-llm-publication-compile-test",
                    "implementation_package": "harness.tests",
                    "timestamp": "2026-06-26T00:00:00Z",
                },
                "limitations": ["Test fixture supplied as explicit external Review LLM evidence."],
            }
        ),
        encoding="utf-8",
    )
    compile_target = external_dir / "compile_target"
    compile_target.mkdir()
    (compile_target / "main.tex").write_text(
        "\\documentclass{article}\n\\begin{document}\nApproved scheduler publication compile.\n\\end{document}\n",
        encoding="utf-8",
    )
    fake_bin = external_dir / "bin"
    fake_bin.mkdir()
    fake_latexmk = fake_bin / "latexmk"
    fake_latexmk.write_text(
        "#!/usr/bin/env python3\n"
        "from pathlib import Path\n"
        "Path('main.pdf').write_text('%PDF-1.4\\n', encoding='utf-8')\n"
        "print('fake scheduler latexmk completed')\n",
        encoding="utf-8",
    )
    fake_latexmk.chmod(0o755)
    env["PATH"] = f"{fake_bin}{os.pathsep}{env.get('PATH', '')}"
    allowlist = external_dir / "compile-allowlist.json"
    before = external_dir / "compile-before.json"
    allowlist.write_text(json.dumps({"executables": ["latexmk"]}) + "\n", encoding="utf-8")
    before.write_text(json.dumps({"paper_dir": str(compile_target), "pdf_exists": False}) + "\n", encoding="utf-8")

    proc = subprocess.run(
        [
            sys.executable,
            str(SMOKE),
            "--harness-dir",
            str(harness_dir),
            "--job-id",
            "job-scientific-lifecycle-publication-compile-test",
            "--timeout-seconds",
            "20",
            "--review-llm-evidence",
            str(review_llm_path),
            "--compile-target",
            str(compile_target),
            "--compile-approval-ref",
            "approval-publication-compile-test",
            "--compile-allowlist-evidence",
            str(allowlist),
            "--compile-before-artifact",
            str(before),
            "--compile-execute-approved",
            "--compile-executor-timeout-seconds",
            "20",
            "--dispatch-external-evidence",
        ],
        cwd=HARNESS,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert proc.returncode == 0, proc.stdout + proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["lifecycle_status"] == "passed"
    assert "publication_produce" in summary["node_results"]
    compile_evidence = json.loads((harness_dir / summary["node_results"]["publication_produce"]["artifact_path"]).read_text(encoding="utf-8"))
    assert compile_evidence["status"] == "completed"
    bundle_files = compile_evidence["outputs"]["bundle"]["files"]
    assert any(item["type"] == "compiled_pdf" and item["path"].endswith("main.pdf") for item in bundle_files)
    assert any(item["type"] == "compile_runtime_evidence_json" for item in bundle_files)
    checklist_path = next(item["path"] for item in bundle_files if item["type"] == "paper_compile_checklist_json")
    checklist = json.loads((harness_dir / checklist_path).read_text(encoding="utf-8"))
    assert checklist["runtime_semantic"]["verified"] is True
    assert checklist["approval_contract"]["semantic_runtime"]["verified"] is True


def test_scientific_lifecycle_smoke_uses_experiment_runtime_evidence(tmp_path: Path) -> None:
    harness_dir = _prepare_isolated_harness(tmp_path)
    env = os.environ.copy()
    env["HARNESS_DIR"] = str(harness_dir)

    external_dir = harness_dir / "artifacts/scientific/external/experiment-runtime-test"
    external_dir.mkdir(parents=True)
    allowlist = external_dir / "experiment-allowlist.json"
    before = external_dir / "experiment-before.json"
    after = external_dir / "experiment-after.json"
    runtime = external_dir / "experiment-runtime.json"
    allowlist.write_text('{"allowed": ["approved-local-experiment"]}\n', encoding="utf-8")
    before.write_text('{"state": "planned"}\n', encoding="utf-8")
    after.write_text('{"state": "completed", "metrics": ["accuracy"]}\n', encoding="utf-8")
    runtime.write_text(
        json.dumps(
            {
                "schema": "autosci_runtime_evidence.v1",
                "task_id": "task-experiment-runtime-test",
                "sprint_id": "sprint-experiment-runtime-test",
                "node_id": "experiment_runtime",
                "status": "completed",
                "exit_code": 0,
                "inputs": {"approval_ref": "approval-experiment-runtime-test"},
                "outputs": {
                    "runtime": {
                        "action": "run_experiment",
                        "status": "completed",
                        "approval_ref": "approval-experiment-runtime-test",
                        "command_run": "approved-local-experiment",
                        "exit_code": 0,
                        "result_collected": True,
                        "outcome": "supports",
                        "metrics": [{"name": "accuracy", "value": 0.77}],
                        "evidence_ids": ["runtime:experiment:scheduler"],
                        "logs": ["approved experiment runtime completed"],
                    }
                },
                "artifacts": [{"type": "experiment_after", "path": str(after)}],
                "provenance": {
                    "operator_id": "external-experiment-runtime-test",
                    "implementation_package": "harness.tests",
                    "timestamp": "2026-06-26T00:00:00Z",
                },
                "limitations": ["Runtime experiment evidence was supplied by the test harness."],
            }
        ),
        encoding="utf-8",
    )

    proc = subprocess.run(
        [
            sys.executable,
            str(SMOKE),
            "--harness-dir",
            str(harness_dir),
            "--job-id",
            "job-scientific-lifecycle-experiment-runtime-test",
            "--timeout-seconds",
            "20",
            "--experiment-approval-ref",
            "approval-experiment-runtime-test",
            "--experiment-allowlist-evidence",
            str(allowlist),
            "--experiment-before-artifact",
            str(before),
            "--experiment-after-artifact",
            str(after),
            "--experiment-runtime-evidence",
            str(runtime),
        ],
        cwd=HARNESS,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert proc.returncode == 0, proc.stdout + proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["lifecycle_status"] == "passed"
    run_evidence = json.loads((harness_dir / summary["node_results"]["experiment_run"]["artifact_path"]).read_text(encoding="utf-8"))
    result = run_evidence["outputs"]["result"]
    assert result["execution_mode"] == "human_approved"
    assert result["outcome"] == "supports"
    assert result["metrics"] == [{"name": "accuracy", "value": 0.77}]
    assert result["command_run"] == "approved-local-experiment"
    assert "runtime:experiment:scheduler" in result["evidence_ids"]
    assert "fixture result collected" not in "\n".join(result["logs"]).lower()
    assert any(artifact["type"] == "experiment_runtime_evidence_json" for artifact in run_evidence["artifacts"])

    monitor_evidence = json.loads((harness_dir / summary["node_results"]["experiment_monitor"]["artifact_path"]).read_text(encoding="utf-8"))
    report = monitor_evidence["outputs"]["status_report"]
    assert report["state"] == "completed"
    assert "runtime:experiment:scheduler" in report["evidence_ids"]
    assert any(artifact["type"] == "experiment_runtime_evidence_json" for artifact in monitor_evidence["artifacts"])


def test_scientific_lifecycle_smoke_executes_approved_experiment_command(tmp_path: Path) -> None:
    harness_dir = _prepare_isolated_harness(tmp_path)
    env = os.environ.copy()
    env["HARNESS_DIR"] = str(harness_dir)

    external_dir = harness_dir / "artifacts/scientific/external/experiment-executor-test"
    external_dir.mkdir(parents=True)
    runner = external_dir / "approved_experiment_runner.py"
    runner.write_text(
        "\n".join(
            [
                "import argparse",
                "import json",
                "",
                "parser = argparse.ArgumentParser()",
                "parser.add_argument('--experiment-id', required=True)",
                "args = parser.parse_args()",
                "print(json.dumps({",
                "    'experiment_id': args.experiment_id,",
                "    'outcome': 'supports',",
                "    'metrics': [{'name': 'accuracy', 'value': 0.84}],",
                "    'evidence_ids': ['runtime:experiment:executor'],",
                "    'logs': ['approved executor produced experiment result'],",
                "}))",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    command_template = f"{sys.executable} {runner} --experiment-id {{experiment_id}}"
    allowlist = external_dir / "experiment-allowlist.json"
    before = external_dir / "experiment-before.json"
    after = external_dir / "experiment-after.json"
    allowlist.write_text(json.dumps({"commands": [command_template]}) + "\n", encoding="utf-8")
    before.write_text('{"state": "planned"}\n', encoding="utf-8")
    after.write_text('{"state": "completed"}\n', encoding="utf-8")

    proc = subprocess.run(
        [
            sys.executable,
            str(SMOKE),
            "--harness-dir",
            str(harness_dir),
            "--job-id",
            "job-scientific-lifecycle-experiment-executor-test",
            "--timeout-seconds",
            "20",
            "--experiment-approval-ref",
            "approval-experiment-executor-test",
            "--experiment-allowlist-evidence",
            str(allowlist),
            "--experiment-before-artifact",
            str(before),
            "--experiment-after-artifact",
            str(after),
            "--experiment-execute-approved",
            "--experiment-executor-timeout-seconds",
            "20",
        ],
        cwd=HARNESS,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert proc.returncode == 0, proc.stdout + proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["lifecycle_status"] == "passed"
    run_evidence = json.loads((harness_dir / summary["node_results"]["experiment_run"]["artifact_path"]).read_text(encoding="utf-8"))
    result = run_evidence["outputs"]["result"]
    assert result["execution_mode"] == "human_approved"
    assert result["metrics"] == [{"name": "accuracy", "value": 0.84}]
    assert "runtime:experiment:executor" in result["evidence_ids"]
    assert "approved executor produced experiment result" in "\n".join(result["logs"])
    artifact_types = {artifact["type"] for artifact in run_evidence["artifacts"]}
    assert {"experiment_runtime_evidence_json", "executor_stdout", "executor_stderr", "run_experiment_result_json"}.issubset(artifact_types)
    assert "fixture result collected" not in "\n".join(result["logs"]).lower()

    monitor_evidence = json.loads((harness_dir / summary["node_results"]["experiment_monitor"]["artifact_path"]).read_text(encoding="utf-8"))
    status_report = monitor_evidence["outputs"]["status_report"]
    assert status_report["state"] == "completed"
    assert "runtime:experiment:executor" in status_report["evidence_ids"]


def test_scientific_lifecycle_smoke_can_resume_external_blocked_nodes(tmp_path: Path) -> None:
    harness_dir = _prepare_isolated_harness(tmp_path)
    env = os.environ.copy()
    env["HARNESS_DIR"] = str(harness_dir)

    blocked_proc = subprocess.run(
        [
            sys.executable,
            str(SMOKE),
            "--harness-dir",
            str(harness_dir),
            "--job-id",
            "job-scientific-lifecycle-resume-test",
            "--timeout-seconds",
            "20",
            "--include-blocked-external",
        ],
        cwd=HARNESS,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert blocked_proc.returncode == 3, blocked_proc.stdout + blocked_proc.stderr
    blocked_summary = json.loads(blocked_proc.stdout)
    blocked_summary_path = harness_dir / blocked_summary["summary_path"]

    external_dir = harness_dir / "artifacts/scientific/external/resume-test"
    external_dir.mkdir(parents=True)
    review_llm_path = external_dir / "review_llm_artifact_review.json"
    review_llm_path.write_text(
        json.dumps(
            {
                "schema": "artifact_review.v1",
                "task_id": "task-review-llm-resume-test",
                "sprint_id": "external-review-llm-resume-test",
                "node_id": "external_artifact_review",
                "status": "completed",
                "inputs": {"target": "scheduler-lifecycle-resume"},
                "outputs": {
                    "review": {
                        "artifact_id": "artifact:scheduler-lifecycle-resume",
                        "target": "scheduler-lifecycle-resume",
                        "review_mode": "review_llm",
                        "review_available": True,
                        "difficulty": "standard",
                        "focus": "completeness",
                        "score": 0.86,
                        "recommendation": "inconclusive",
                        "evidence_ids": ["review-llm:resume-test"],
                        "review_llm": {
                            "status": "completed",
                            "invocation_mode": "supplied_evidence",
                            "source_path": str(review_llm_path),
                        },
                    },
                    "findings": [
                        {
                            "finding_id": "review-llm.resume-test.coverage",
                            "severity": "low",
                            "category": "coverage",
                            "evidence": "Supplied external Review LLM evidence exists for the scheduler resume path.",
                            "suggestion": "Proceed with paper planning while retaining source evidence links.",
                        }
                    ],
                    "artifact": {"artifact_id": "artifact:scheduler-lifecycle-resume"},
                },
                "artifacts": [],
                "provenance": {
                    "operator_id": "external-review-llm-test-fixture",
                    "implementation_package": "harness.tests",
                    "timestamp": "2026-06-26T00:00:00Z",
                },
                "limitations": ["Test fixture supplied as explicit external Review LLM evidence."],
            }
        ),
        encoding="utf-8",
    )

    compile_target = external_dir / "compile_target"
    compile_target.mkdir()
    (compile_target / "main.tex").write_text(
        "\\documentclass{article}\\begin{document}Scheduler resume compile target.\\end{document}\n",
        encoding="utf-8",
    )
    (compile_target / "main.pdf").write_bytes(b"%PDF-1.4\n% scheduler resume test\n")

    resume_proc = subprocess.run(
        [
            sys.executable,
            str(SMOKE),
            "--harness-dir",
            str(harness_dir),
            "--resume-summary",
            str(blocked_summary_path),
            "--review-llm-evidence",
            str(review_llm_path),
            "--compile-target",
            str(compile_target),
            "--timeout-seconds",
            "20",
        ],
        cwd=HARNESS,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert resume_proc.returncode == 0, resume_proc.stdout + resume_proc.stderr
    resumed = json.loads(resume_proc.stdout)
    assert resumed["lifecycle_status"] == "passed"
    assert resumed["blocked_nodes"] == {}
    assert resumed["lifecycle_gate_result"]["ok"] is True
    assert "report_plan" in resumed["node_results"]
    assert "publication_produce" in resumed["node_results"]
    assert resumed["node_results"]["report_plan"]["action"] == "plan_report"
    assert resumed["node_results"]["publication_produce"]["action"] == "compile_paper"
    assert resumed["node_results"]["publication_produce"]["expected_schema"] == "publication_bundle.v1"
    assert (harness_dir / resumed["node_results"]["report_plan"]["artifact_path"]).exists()
    assert (harness_dir / resumed["node_results"]["publication_produce"]["artifact_path"]).exists()

    gate = subprocess.run(
        [
            sys.executable,
            str(LIFECYCLE_GATE),
            str(harness_dir / resumed["summary_path"]),
        ],
        cwd=HARNESS,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert gate.returncode == 0, gate.stdout + gate.stderr
    gate_payload = json.loads(gate.stdout)
    assert gate_payload["ok"] is True
