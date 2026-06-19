from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from evaluators.scientific import autosci_feature_parity_gate

HARNESS = Path(__file__).resolve().parents[3]
ROUTE_CONFIG = HARNESS / "plugins" / "autosci" / "config" / "feature_parity_routes.v1.json"


def payload_with_items(items: list[dict]) -> dict:
    native_skills = [item["native_skill"] for item in items]
    return {
        "schema": "autosci_feature_parity.v1",
        "task_id": "test-autosci-feature-parity",
        "sprint_id": "phase19-test",
        "node_id": "node-autosci-feature-parity",
        "status": "completed",
        "inputs": {
            "autosci_repo": "/tmp/AutoSci",
            "route_config": str(ROUTE_CONFIG),
            "requested_skill": "N/A",
        },
        "outputs": {
            "parity": {
                "config_version": "phase19.v1",
                "autosci_repo": "/tmp/AutoSci",
                "native_skill_count": len(native_skills),
                "configured_route_count": len(items),
                "routed_count": len([item for item in items if item["coverage_status"] != "missing"]),
                "missing_route_count": len([item for item in items if item["coverage_status"] == "missing"]),
                "full_count": len([item for item in items if item["coverage_status"] == "full"]),
                "partial_count": len([item for item in items if item["coverage_status"] == "partial"]),
                "gated_count": len([item for item in items if item["coverage_status"] == "gated"]),
                "blocked_count": len([item for item in items if item["coverage_status"] == "blocked"]),
                "native_skills": native_skills,
                "items": items,
            }
        },
        "artifacts": [{"type": "route_config", "path": str(ROUTE_CONFIG)}],
        "provenance": {
            "operator_id": "AutoSciFeatureParityBridge",
            "implementation_package": "harness.plugins.autosci",
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        },
        "limitations": ["Gate test parity scope limitation."],
    }


def base_item(skill: str, *, coverage_status: str = "full", side_effect_policy: str = "none") -> dict:
    return {
        "autosci_feature": f"/{skill}",
        "native_skill": skill,
        "feature_kind": "skill",
        "native_paths": [f"i18n/en/skills/{skill}/SKILL.md"],
        "solar_capability": "cap.research-literature-discover",
        "solar_logical_operator": "ScientificLiteratureDiscoverer",
        "solar_backend_action": "discover_literature",
        "coverage_status": coverage_status,
        "backend_mode": "solar_native" if coverage_status == "full" else "route_plan",
        "side_effect_policy": side_effect_policy,
        "evidence_schema": "literature_discovery.v1",
        "primary_tools": ["plugins/autosci/bin/autosci_bridge.py"],
        "required_capabilities": ["route coverage"],
        "limitations": ["Non-full route requires downstream evidence."] if coverage_status != "full" else ["N/A"],
        "evidence_ids": [f"route:{skill}", f"native:{skill}"],
    }


def test_autosci_feature_parity_gate_accepts_honest_mixed_route_inventory() -> None:
    payload = payload_with_items(
        [
            base_item("discover"),
            base_item("daily-arxiv", coverage_status="gated", side_effect_policy="approval_required"),
            base_item("novelty", coverage_status="partial", side_effect_policy="dry_run_only"),
        ]
    )

    result = autosci_feature_parity_gate.evaluate(payload)

    assert result.ok is True
    assert result.status == "passed"
    assert result.reasons == []
    assert result.warnings


def test_autosci_feature_parity_gate_rejects_missing_route() -> None:
    missing = base_item("future-skill", coverage_status="missing", side_effect_policy="unavailable")
    missing["solar_capability"] = "N/A"
    missing["solar_logical_operator"] = "N/A"
    missing["solar_backend_action"] = "N/A"
    payload = payload_with_items([base_item("discover"), missing])

    result = autosci_feature_parity_gate.evaluate(payload)

    assert result.ok is False
    assert result.status == "failed"
    assert "all discovered AutoSci native skills must have a Solar route" in " ".join(result.reasons)


def test_autosci_feature_parity_gate_rejects_full_route_with_approval_gate() -> None:
    payload = payload_with_items([base_item("poster", coverage_status="full", side_effect_policy="approval_required")])

    result = autosci_feature_parity_gate.evaluate(payload)

    assert result.ok is False
    assert result.status == "failed"
    assert "cannot claim full coverage" in " ".join(result.reasons)
