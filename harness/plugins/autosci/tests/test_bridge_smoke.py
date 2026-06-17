from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

HARNESS = Path(__file__).resolve().parents[3]
BRIDGE = HARNESS / "plugins" / "autosci" / "bin" / "autosci_bridge.py"


def run_bridge(args: list[str], tmp_path: Path) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["HARNESS_DIR"] = str(tmp_path)
    return subprocess.run(
        [sys.executable, str(BRIDGE), *args],
        cwd=HARNESS,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_help_lists_required_actions(tmp_path: Path) -> None:
    proc = run_bridge(["run", "--help"], tmp_path)
    assert proc.returncode == 0, proc.stderr
    for action in ["ingest_paper", "extract_claims", "design_experiment", "run_experiment", "verify_claim", "write_report"]:
        assert action in proc.stdout


def test_smoke_writes_result_and_evidence_jsonl(tmp_path: Path) -> None:
    proc = run_bridge(["smoke"], tmp_path)
    assert proc.returncode == 0, proc.stderr
    out = json.loads(proc.stdout)
    assert out["ok"] is True
    result_path = tmp_path / out["result_path"]
    ledger_path = tmp_path / out["evidence_jsonl"]
    assert result_path.exists()
    assert ledger_path.exists()
    result = json.loads(result_path.read_text(encoding="utf-8"))
    assert result["schema"] == "research_claims.v1"
    assert "AutoSciRunner" not in json.dumps(result)


def test_validate_accepts_smoke_result(tmp_path: Path) -> None:
    smoke = run_bridge(["smoke"], tmp_path)
    assert smoke.returncode == 0, smoke.stderr
    out = json.loads(smoke.stdout)
    validate = run_bridge(["validate", "--result", out["result_path"]], tmp_path)
    assert validate.returncode == 0, validate.stderr
    assert json.loads(validate.stdout)["ok"] is True
