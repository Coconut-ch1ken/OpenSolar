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
