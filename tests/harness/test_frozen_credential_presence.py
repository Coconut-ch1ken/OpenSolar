"""Credential presence is part of candidate truth: observed at freeze, re-observed at dispatch."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
for value in (ROOT / "harness" / "lib", ROOT / "harness" / "tools"):
    if str(value) not in sys.path:
        sys.path.insert(0, str(value))

import apo_plan_compiler as apo  # noqa: E402
import graph_scheduler  # noqa: E402
import research_operator_registry_adapter as registry_adapter  # noqa: E402


def _catalog(tmp_path: Path) -> Path:
    path = tmp_path / "operators.json"
    path.write_text(
        json.dumps(
            {
                "operators": {
                    "provider-builder": {
                        "enabled": True,
                        "available": True,
                        "health_status": "ok",
                        "roles": ["builder"],
                        "provider": "openai",
                        "auth_mode": "subscription",
                    },
                    "local-transform": {
                        "enabled": True,
                        "available": True,
                        "health_status": "ok",
                        "roles": ["builder"],
                        "backend": "research_operator_registry",
                    },
                }
            }
        ),
        encoding="utf-8",
    )
    return path


def _grant_openai(home: Path) -> None:
    (home / ".codex").mkdir(parents=True, exist_ok=True)
    (home / ".codex" / "auth.json").write_text("{}", encoding="utf-8")


def test_frozen_candidates_record_live_credential_presence(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(apo.AUTH_HOME_ENV, str(tmp_path / "home"))
    decisions = apo.enumerate_physical_candidate_decisions(role="builder", operators_path=_catalog(tmp_path))
    by_id = {row["operator_id"]: row for row in decisions["candidates"]}
    assert by_id["provider-builder"]["auth"] == {"provider": "openai", "present": False, "signal": "file:.codex/auth.json"}
    assert "auth" not in by_id["local-transform"]

    _grant_openai(tmp_path / "home")
    decisions = apo.enumerate_physical_candidate_decisions(role="builder", operators_path=_catalog(tmp_path))
    by_id = {row["operator_id"]: row for row in decisions["candidates"]}
    assert by_id["provider-builder"]["auth"]["present"] is True


def test_dispatchable_freeze_excludes_unauthenticated_provider(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(apo.AUTH_HOME_ENV, str(tmp_path / "home"))
    monkeypatch.setattr(apo, "_is_dispatchable_runtime", lambda _op: True)
    decisions = apo.enumerate_physical_candidate_decisions(role="builder", require_dispatchable=True, operators_path=_catalog(tmp_path))
    excluded = {row["operator_id"]: row for row in decisions["excluded"]}
    assert "PROVIDER_UNAUTHENTICATED" in excluded["provider-builder"]["reasons"]
    assert excluded["provider-builder"]["observed"]["auth"]["present"] is False


def test_physical_plan_declares_auth_as_runtime_refreshed() -> None:
    plan = apo.build_physical_plan_ir({"nodes": []})
    assert "auth" in plan["availability_boundary"]["runtime_refresh"]


def test_scheduler_re_observes_credentials_from_the_frozen_record(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(apo.AUTH_HOME_ENV, str(tmp_path / "home"))
    frozen = {"operator_id": "provider-builder", "auth": {"provider": "openai", "present": True, "signal": "file:.codex/auth.json"}}
    assert graph_scheduler._frozen_candidate_unauthenticated(frozen) is True
    _grant_openai(tmp_path / "home")
    assert graph_scheduler._frozen_candidate_unauthenticated(frozen) is False


def test_scheduler_re_observes_credentials_from_the_catalog_when_the_row_is_bare(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(apo.AUTH_HOME_ENV, str(tmp_path / "home"))
    specs = json.loads(_catalog(tmp_path).read_text(encoding="utf-8"))["operators"]
    monkeypatch.setattr(graph_scheduler, "_operator_spec", lambda operator_id: dict(specs.get(operator_id) or {}))
    assert graph_scheduler._frozen_candidate_unauthenticated({"operator_id": "provider-builder", "rank": 1}) is True
    assert graph_scheduler._frozen_candidate_unauthenticated({"operator_id": "local-transform", "rank": 1}) is False
    assert graph_scheduler._frozen_candidate_unauthenticated({"operator_id": "unknown", "rank": 1}) is False
    _grant_openai(tmp_path / "home")
    assert graph_scheduler._frozen_candidate_unauthenticated({"operator_id": "provider-builder", "rank": 1}) is False


def test_adapter_copies_planner_budget_and_never_widens_it() -> None:
    assert registry_adapter._frozen_timeout_retry_policy({}) == registry_adapter.DEFAULT_TIMEOUT_RETRY_POLICY
    narrowed = registry_adapter._frozen_timeout_retry_policy(
        {"timeout_retry_policy": {"timeout_seconds": 120, "max_attempts": 2, "retry_on": ["provider_timeout"]}}
    )
    assert narrowed == {"timeout_seconds": 120, "max_attempts": 2, "retry_on": ["provider_timeout"]}
    widened = registry_adapter._frozen_timeout_retry_policy({"timeout_retry_policy": {"timeout_seconds": 99999}})
    assert widened["timeout_seconds"] == registry_adapter.DEFAULT_TIMEOUT_RETRY_POLICY["timeout_seconds"]
