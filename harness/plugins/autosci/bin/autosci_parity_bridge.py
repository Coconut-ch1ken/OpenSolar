#!/usr/bin/env python3
"""AutoSci native-skill parity inventory for Solar-native routes."""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_HARNESS = Path(__file__).resolve().parents[3]
REPO_ROOT = REPO_HARNESS.parent
OUTPUT_HARNESS = Path(os.environ.get("HARNESS_DIR", REPO_HARNESS)).resolve()
CONFIG_PATH = REPO_HARNESS / "plugins" / "autosci" / "config" / "feature_parity_routes.v1.json"
DEFAULT_AUTOSCI_REPO = REPO_ROOT.parent / "AutoSci"
SCHEMA = "autosci_feature_parity.v1"


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def resolve_output(path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return OUTPUT_HARNESS / path


def default_output(skill: str | None = None) -> Path:
    name = f"autosci_feature_parity.{skill}.json" if skill else "autosci_feature_parity.json"
    return OUTPUT_HARNESS / "artifacts" / "autosci" / "phase19" / name


def discover_native_skills(autosci_repo: Path) -> tuple[list[str], list[str]]:
    skills_root = autosci_repo / "i18n" / "en" / "skills"
    if not skills_root.exists():
        return [], [f"AutoSci skills root not found: {skills_root}"]
    skills = sorted(path.parent.name for path in skills_root.glob("*/SKILL.md"))
    if not skills:
        return [], [f"AutoSci skills root contains no SKILL.md files: {skills_root}"]
    return skills, []


def route_items(routes: list[dict[str, Any]], native_skills: list[str]) -> list[dict[str, Any]]:
    native_set = set(native_skills)
    items: list[dict[str, Any]] = []
    for route in sorted(routes, key=lambda item: str(item.get("native_skill") or "")):
        skill = str(route.get("native_skill") or "")
        item = dict(route)
        item["autosci_feature"] = route.get("autosci_command") or f"/{skill}"
        item["evidence_ids"] = [
            f"route:{skill}",
            f"native:{skill}" if skill in native_set else f"config-only:{skill}",
        ]
        items.append(item)
    return items


def add_missing_items(items: list[dict[str, Any]], native_skills: list[str]) -> list[dict[str, Any]]:
    routed = {str(item.get("native_skill") or "") for item in items}
    missing = sorted(set(native_skills) - routed)
    for skill in missing:
        items.append(
            {
                "autosci_feature": f"/{skill}",
                "native_skill": skill,
                "feature_kind": "skill",
                "native_paths": [f"i18n/en/skills/{skill}/SKILL.md"],
                "solar_capability": "N/A",
                "solar_logical_operator": "N/A",
                "solar_backend_action": "N/A",
                "coverage_status": "missing",
                "backend_mode": "route_plan",
                "side_effect_policy": "unavailable",
                "evidence_schema": SCHEMA,
                "primary_tools": ["N/A"],
                "required_capabilities": ["Solar route definition"],
                "limitations": ["No Solar route is configured for this discovered AutoSci native skill."],
                "evidence_ids": [f"missing:{skill}"],
            }
        )
    return sorted(items, key=lambda item: str(item.get("native_skill") or ""))


def count(items: list[dict[str, Any]], status: str) -> int:
    return sum(1 for item in items if item.get("coverage_status") == status)


def build_evidence(
    *,
    autosci_repo: Path,
    requested_skill: str | None = None,
) -> dict[str, Any]:
    config = load_json(CONFIG_PATH)
    routes = config.get("routes")
    if not isinstance(routes, list):
        raise ValueError(f"{CONFIG_PATH} routes must be a list")

    native_skills, discovery_warnings = discover_native_skills(autosci_repo)
    configured_items = route_items([route for route in routes if isinstance(route, dict)], native_skills)
    if requested_skill:
        configured_items = [
            item for item in configured_items if item.get("native_skill") == requested_skill
        ]
        native_skills = [skill for skill in native_skills if skill == requested_skill]
        if not configured_items:
            native_skills = sorted(set(native_skills + [requested_skill]))
    items = add_missing_items(configured_items, native_skills)

    missing_count = count(items, "missing")
    status = "completed"
    if discovery_warnings:
        status = "inconclusive"
    if missing_count:
        status = "failed"

    limitations = [
        "Phase 19 parity evidence verifies Solar-native route coverage, not live execution of external services.",
        "Side effects such as secrets, remote execution, SMTP, browser rendering, GitHub Actions, and destructive reset remain approval-gated.",
    ]
    limitations.extend(discovery_warnings)
    return {
        "schema": SCHEMA,
        "task_id": "phase19-autosci-feature-parity",
        "sprint_id": "phase19",
        "node_id": "autosci-feature-parity-inventory" if not requested_skill else f"autosci-feature-parity-{requested_skill}",
        "status": status,
        "inputs": {
            "autosci_repo": str(autosci_repo),
            "route_config": str(CONFIG_PATH),
            "requested_skill": requested_skill or "N/A",
        },
        "outputs": {
            "parity": {
                "config_version": str(config.get("version") or "unknown"),
                "autosci_repo": str(autosci_repo),
                "native_skill_count": len(native_skills),
                "configured_route_count": len(items),
                "routed_count": len(items) - missing_count,
                "missing_route_count": missing_count,
                "full_count": count(items, "full"),
                "partial_count": count(items, "partial"),
                "gated_count": count(items, "gated"),
                "blocked_count": count(items, "blocked"),
                "native_skills": native_skills,
                "items": items,
            }
        },
        "artifacts": [
            {
                "type": "route_config",
                "path": str(CONFIG_PATH),
            }
        ],
        "provenance": {
            "operator_id": "AutoSciFeatureParityBridge",
            "implementation_package": "harness.plugins.autosci",
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        },
        "limitations": limitations,
    }


def write_evidence(payload: dict[str, Any], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_inventory(args: argparse.Namespace) -> int:
    autosci_repo = Path(args.autosci_repo).expanduser().resolve()
    payload = build_evidence(autosci_repo=autosci_repo)
    out_path = resolve_output(args.out) if args.out else default_output()
    write_evidence(payload, out_path)
    parity = payload["outputs"]["parity"]
    print(
        json.dumps(
            {
                "ok": payload["status"] == "completed",
                "schema": SCHEMA,
                "evidence_path": str(out_path),
                "native_skill_count": parity["native_skill_count"],
                "routed_count": parity["routed_count"],
                "missing_route_count": parity["missing_route_count"],
                "full_count": parity["full_count"],
                "partial_count": parity["partial_count"],
                "gated_count": parity["gated_count"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if payload["status"] == "completed" else 2


def run_route(args: argparse.Namespace) -> int:
    autosci_repo = Path(args.autosci_repo).expanduser().resolve()
    payload = build_evidence(autosci_repo=autosci_repo, requested_skill=args.skill)
    out_path = resolve_output(args.out) if args.out else default_output(args.skill)
    write_evidence(payload, out_path)
    parity = payload["outputs"]["parity"]
    print(
        json.dumps(
            {
                "ok": payload["status"] == "completed",
                "schema": SCHEMA,
                "evidence_path": str(out_path),
                "skill": args.skill,
                "routed_count": parity["routed_count"],
                "missing_route_count": parity["missing_route_count"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if payload["status"] == "completed" else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--autosci-repo",
        default=os.environ.get("AUTOSCI_REPO", str(DEFAULT_AUTOSCI_REPO)),
        help="Path to the AutoSci checkout. Defaults to AUTOSCI_REPO or a sibling checkout.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    inventory = subparsers.add_parser("inventory", help="Write full native-skill route parity evidence")
    inventory.add_argument("--out", help="Output JSON path, relative to HARNESS_DIR when not absolute")
    inventory.set_defaults(func=run_inventory)

    route = subparsers.add_parser("route", help="Write parity evidence for one native AutoSci skill")
    route.add_argument("--skill", required=True, help="Native AutoSci skill name, for example daily-arxiv")
    route.add_argument("--out", help="Output JSON path, relative to HARNESS_DIR when not absolute")
    route.set_defaults(func=run_route)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
