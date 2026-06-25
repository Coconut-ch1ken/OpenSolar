from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

HARNESS = Path(__file__).resolve().parents[3]
BRIDGE = HARNESS / "plugins" / "autosci" / "bin" / "autosci_parity_bridge.py"
GATE = HARNESS / "evaluators" / "scientific" / "autosci_feature_parity_gate.py"
ROUTE_CONFIG = HARNESS / "plugins" / "autosci" / "config" / "feature_parity_routes.v1.json"


def route_skills() -> list[str]:
    config = json.loads(ROUTE_CONFIG.read_text(encoding="utf-8"))
    return sorted(route["native_skill"] for route in config["routes"])


def make_autosci_fixture(tmp_path: Path, *, extra_skill: str | None = None) -> Path:
    repo = tmp_path / "AutoSci"
    skills_root = repo / "i18n" / "en" / "skills"
    for skill in route_skills() + ([extra_skill] if extra_skill else []):
        skill_dir = skills_root / skill
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_dir.joinpath("SKILL.md").write_text(
            f"---\ndescription: fixture for {skill}\n---\n\n# /{skill}\n",
            encoding="utf-8",
        )
    return repo


def run_bridge(args: list[str], tmp_path: Path, autosci_repo: Path) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["HARNESS_DIR"] = str(tmp_path)
    env["AUTOSCI_REPO"] = str(autosci_repo)
    return subprocess.run(
        [sys.executable, str(BRIDGE), *args],
        cwd=HARNESS,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_inventory_routes_every_native_autosci_skill(tmp_path: Path) -> None:
    autosci_repo = make_autosci_fixture(tmp_path)
    out = "artifacts/autosci/phase19/parity.json"
    proc = run_bridge(["inventory", "--out", out], tmp_path, autosci_repo)
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["missing_route_count"] == 0
    assert summary["native_skill_count"] == len(route_skills())
    payload = json.loads((tmp_path / out).read_text(encoding="utf-8"))
    parity = payload["outputs"]["parity"]
    assert parity["configured_route_count"] == len(route_skills())
    assert parity["routed_count"] == len(route_skills())
    assert {item["native_skill"] for item in parity["items"]} == set(route_skills())
    assert all(item["evidence_ids"] for item in parity["items"])

    gate = subprocess.run(
        [sys.executable, str(GATE), str(tmp_path / out)],
        cwd=HARNESS,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert gate.returncode == 0, gate.stdout + gate.stderr


def test_route_writes_single_skill_parity_evidence(tmp_path: Path) -> None:
    autosci_repo = make_autosci_fixture(tmp_path)
    out = "artifacts/autosci/phase19/daily_arxiv_route.json"
    proc = run_bridge(["route", "--skill", "daily-arxiv", "--out", out], tmp_path, autosci_repo)
    assert proc.returncode == 0, proc.stderr
    payload = json.loads((tmp_path / out).read_text(encoding="utf-8"))
    items = payload["outputs"]["parity"]["items"]
    assert [item["native_skill"] for item in items] == ["daily-arxiv"]
    assert items[0]["coverage_status"] == "gated"
    assert items[0]["side_effect_policy"] == "approval_required"


def test_overclaimed_smoke_routes_are_marked_partial() -> None:
    config = json.loads(ROUTE_CONFIG.read_text(encoding="utf-8"))
    routes = {item["native_skill"]: item for item in config["routes"]}
    for skill in ["exp-design", "exp-status", "ideate", "paper-draft", "paper-plan"]:
        assert routes[skill]["coverage_status"] == "partial"
        assert routes[skill]["backend_mode"] == "route_plan"
        assert routes[skill]["limitations"]


def test_inventory_fails_when_autosci_adds_unmapped_native_skill(tmp_path: Path) -> None:
    autosci_repo = make_autosci_fixture(tmp_path, extra_skill="new-native-skill")
    out = "artifacts/autosci/phase19/parity_missing.json"
    proc = run_bridge(["inventory", "--out", out], tmp_path, autosci_repo)
    assert proc.returncode == 2
    payload = json.loads((tmp_path / out).read_text(encoding="utf-8"))
    parity = payload["outputs"]["parity"]
    assert payload["status"] == "failed"
    assert parity["missing_route_count"] == 1
    missing = [item for item in parity["items"] if item["coverage_status"] == "missing"]
    assert missing[0]["native_skill"] == "new-native-skill"
