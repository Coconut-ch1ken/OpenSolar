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
    assert sum(summary["runtime_proof_status_counts"].values()) == len(route_skills())
    payload = json.loads((tmp_path / out).read_text(encoding="utf-8"))
    parity = payload["outputs"]["parity"]
    assert parity["configured_route_count"] == len(route_skills())
    assert parity["routed_count"] == len(route_skills())
    assert {item["native_skill"] for item in parity["items"]} == set(route_skills())
    assert all(item["evidence_ids"] for item in parity["items"])
    assert all(item["semantic_parity"] in {"full", "partial", "missing"} for item in parity["items"])
    assert all(item["execution_policy"] in {"pure", "bounded_local", "approval_required", "provider_required"} for item in parity["items"])
    assert all(item["proof_level"] in {"E0", "E1", "E2", "E3", "E4", "E5"} for item in parity["items"])
    assert all(item["proof_refs"] for item in parity["items"])
    assert all(isinstance(item["remaining_requirements"], list) for item in parity["items"])
    assert all(item["runtime_proof_status"] in {"not_required", "pending", "supplied", "verified"} for item in parity["items"])
    assert all(isinstance(item["runtime_proof_refs"], list) for item in parity["items"])
    assert all(isinstance(item["proof_requirements"], list) and item["proof_requirements"] for item in parity["items"])
    assert any(item["runtime_proof_status"] == "pending" for item in parity["items"])
    assert any(
        any(requirement["category"] == "external_runtime_evidence" for requirement in item["proof_requirements"])
        for item in parity["items"]
    )
    assert parity["semantic_full_count"] == 0
    assert parity["semantic_partial_count"] == len(route_skills())
    assert parity["semantic_missing_count"] == 0
    assert sum(parity["execution_policy_counts"].values()) == len(route_skills())
    assert sum(parity["proof_level_counts"].values()) == len(route_skills())
    assert sum(parity["runtime_proof_status_counts"].values()) == len(route_skills())
    assert sum(parity["proof_requirement_status_counts"].values()) >= len(route_skills())

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
    summary = json.loads(proc.stdout)
    assert summary["runtime_proof_status_counts"]["pending"] == 1
    payload = json.loads((tmp_path / out).read_text(encoding="utf-8"))
    items = payload["outputs"]["parity"]["items"]
    assert [item["native_skill"] for item in items] == ["daily-arxiv"]
    assert items[0]["coverage_status"] == "gated"
    assert items[0]["side_effect_policy"] == "approval_required"
    assert items[0]["semantic_parity"] == "partial"
    assert items[0]["execution_policy"] == "approval_required"
    assert items[0]["proof_level"] == "E2"
    assert items[0]["remaining_requirements"]
    assert items[0]["runtime_proof_status"] == "pending"
    assert any(requirement["category"] == "external_runtime_evidence" for requirement in items[0]["proof_requirements"])


def test_inventory_attaches_runtime_proof_manifest_without_promoting_full(tmp_path: Path) -> None:
    autosci_repo = make_autosci_fixture(tmp_path)
    runtime_artifact = tmp_path / "artifacts/runtime/daily-arxiv/result.json"
    runtime_artifact.parent.mkdir(parents=True)
    runtime_artifact.write_text('{"status": "completed"}\n', encoding="utf-8")
    manifest = tmp_path / "runtime-proof-manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "schema": "autosci_runtime_proof_manifest.v1",
                "proofs": [
                    {
                        "native_skill": "daily-arxiv",
                        "proof_id": "runtime:daily-arxiv:test",
                        "categories": [
                            "external_runtime_evidence",
                            "approval_boundary_evidence",
                            "provider_source_evidence",
                        ],
                        "evidence_refs": ["artifacts/runtime/daily-arxiv/result.json"],
                        "description": "Fixture manifest represents supplied runtime proof metadata only.",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    out = "artifacts/autosci/phase19/parity_with_runtime.json"
    proc = run_bridge(["inventory", "--runtime-proof-manifest", str(manifest), "--out", out], tmp_path, autosci_repo)
    assert proc.returncode == 0, proc.stderr
    payload = json.loads((tmp_path / out).read_text(encoding="utf-8"))
    daily = next(item for item in payload["outputs"]["parity"]["items"] if item["native_skill"] == "daily-arxiv")
    assert daily["coverage_status"] == "gated"
    assert daily["semantic_parity"] == "partial"
    assert daily["runtime_proof_status"] == "supplied"
    assert daily["runtime_proof_sources"][0]["proof_id"] == "runtime:daily-arxiv:test"
    assert daily["runtime_proof_sources"][0]["evidence_ref_statuses"][0]["status"] == "ok"
    assert "runtime:daily-arxiv:test" in daily["runtime_proof_refs"]
    supplied_categories = {
        requirement["category"]
        for requirement in daily["proof_requirements"]
        if requirement["status"] == "supplied"
    }
    assert "external_runtime_evidence" in supplied_categories
    assert payload["outputs"]["parity"]["full_count"] == 0
    assert payload["outputs"]["parity"]["semantic_full_count"] == 0
    gate = subprocess.run(
        [sys.executable, str(GATE), str(tmp_path / out)],
        cwd=HARNESS,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert gate.returncode == 0, gate.stdout + gate.stderr


def test_inventory_blocks_runtime_proof_manifest_with_missing_local_ref(tmp_path: Path) -> None:
    autosci_repo = make_autosci_fixture(tmp_path)
    manifest = tmp_path / "runtime-proof-manifest-missing-ref.json"
    manifest.write_text(
        json.dumps(
            {
                "schema": "autosci_runtime_proof_manifest.v1",
                "proofs": [
                    {
                        "native_skill": "daily-arxiv",
                        "proof_id": "runtime:daily-arxiv:missing-ref",
                        "categories": ["external_runtime_evidence"],
                        "evidence_refs": ["artifacts/runtime/daily-arxiv/missing-result.json"],
                        "description": "Missing local evidence should block supplied proof.",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    out = "artifacts/autosci/phase19/parity_with_missing_runtime_ref.json"
    proc = run_bridge(["inventory", "--runtime-proof-manifest", str(manifest), "--out", out], tmp_path, autosci_repo)
    assert proc.returncode == 0, proc.stderr
    payload = json.loads((tmp_path / out).read_text(encoding="utf-8"))
    daily = next(item for item in payload["outputs"]["parity"]["items"] if item["native_skill"] == "daily-arxiv")
    assert daily["runtime_proof_status"] == "pending"
    assert daily["runtime_proof_sources"][0]["status"] == "blocked"
    assert daily["runtime_proof_sources"][0]["evidence_ref_statuses"][0]["status"] == "missing"
    assert "runtime:daily-arxiv:missing-ref" not in daily["runtime_proof_refs"]
    gate = subprocess.run(
        [sys.executable, str(GATE), str(tmp_path / out)],
        cwd=HARNESS,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert gate.returncode == 2, gate.stdout + gate.stderr
    assert "blocked by unresolved evidence refs" in gate.stdout


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
    assert missing[0]["semantic_parity"] == "missing"
    assert missing[0]["proof_level"] == "E0"
    assert missing[0]["remaining_requirements"]
    assert missing[0]["runtime_proof_status"] == "pending"
    assert any(requirement["status"] == "missing" for requirement in missing[0]["proof_requirements"])
