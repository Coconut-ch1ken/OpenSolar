#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evaluators.scientific.common import (  # noqa: E402
    check_artifact_paths,
    finish,
    has_any_evidence_ids,
    limitations,
    outputs,
    require_non_empty_list,
    require_non_empty_string,
    run_cli,
    validate_schema,
)

SCHEMA = "autosci_feature_parity.v1"


def _count(items: list[dict[str, Any]], status: str) -> int:
    return sum(1 for item in items if item.get("coverage_status") == status)


def evaluate(payload: dict[str, Any], path: str | Path | None = None):
    reasons, warnings = validate_schema(payload, SCHEMA)
    parity = outputs(payload).get("parity")
    if not isinstance(parity, dict):
        reasons.append("outputs.parity must be an object")
        return finish(payload, reasons, warnings, path=path)

    items_raw = require_non_empty_list(parity.get("items"), "outputs.parity.items", reasons)
    items: list[dict[str, Any]] = []
    for index, item in enumerate(items_raw):
        if not isinstance(item, dict):
            reasons.append(f"items[{index}] must be an object")
            continue
        items.append(item)

    native_skills_raw = require_non_empty_list(parity.get("native_skills"), "outputs.parity.native_skills", reasons)
    native_skills = [str(skill) for skill in native_skills_raw if isinstance(skill, str) and skill.strip()]
    item_skills: set[str] = set()
    for index, item in enumerate(items):
        skill = require_non_empty_string(item.get("native_skill"), f"items[{index}].native_skill", reasons)
        if skill in item_skills:
            reasons.append(f"items[{index}].native_skill duplicates route for {skill}")
        if skill:
            item_skills.add(skill)
        for field in (
            "autosci_feature",
            "feature_kind",
            "solar_capability",
            "solar_logical_operator",
            "solar_backend_action",
            "coverage_status",
            "backend_mode",
            "side_effect_policy",
            "evidence_schema",
        ):
            require_non_empty_string(item.get(field), f"items[{index}].{field}", reasons)
        require_non_empty_list(item.get("native_paths"), f"items[{index}].native_paths", reasons)
        require_non_empty_list(item.get("primary_tools"), f"items[{index}].primary_tools", reasons)
        require_non_empty_list(item.get("required_capabilities"), f"items[{index}].required_capabilities", reasons)
        item_limits = require_non_empty_list(item.get("limitations"), f"items[{index}].limitations", reasons)
        if not has_any_evidence_ids(item.get("evidence_ids")):
            reasons.append(f"items[{index}].evidence_ids must contain at least one id")
        tool_abi_status = str(item.get("tool_abi_status") or "")
        missing_primary_tools = item.get("missing_primary_tools")
        if tool_abi_status:
            if tool_abi_status not in {"ok", "missing"}:
                reasons.append(f"items[{index}].tool_abi_status must be ok or missing")
            if tool_abi_status == "missing":
                reasons.append(f"items[{index}] has missing primary tool/config references")
        if isinstance(missing_primary_tools, list) and missing_primary_tools:
            missing_refs = ", ".join(str(entry.get("ref") or entry) for entry in missing_primary_tools if isinstance(entry, dict))
            reasons.append(f"items[{index}].missing_primary_tools must be empty: {missing_refs}")

        coverage = item.get("coverage_status")
        side_effect_policy = item.get("side_effect_policy")
        if coverage == "full" and side_effect_policy not in {"none", "dry_run_only"}:
            reasons.append(
                f"items[{index}] cannot claim full coverage while side_effect_policy={side_effect_policy}"
            )
        if coverage == "full":
            limitation_text = " ".join(str(item).lower() for item in item_limits)
            overclaim_markers = (
                "fixture",
                "smoke only",
                "smoke evidence only",
                "not yet implemented",
                "not fully implemented",
                "local surrogate",
            )
            if any(marker in limitation_text for marker in overclaim_markers):
                reasons.append(f"items[{index}] full coverage cannot describe fixture/smoke-only or unimplemented behavior")
        if coverage in {"partial", "gated", "blocked", "missing"} and not item_limits:
            reasons.append(f"items[{index}] must explain limitations for {coverage} coverage")
        if coverage == "gated" and side_effect_policy != "approval_required":
            reasons.append(f"items[{index}] gated coverage requires approval_required side effect policy")
        if coverage == "missing" and side_effect_policy != "unavailable":
            reasons.append(f"items[{index}] missing coverage requires unavailable side effect policy")

    missing_native = sorted(set(native_skills) - item_skills)
    extra_routes = sorted(item_skills - set(native_skills))
    if missing_native:
        reasons.append(f"native skills without route: {', '.join(missing_native)}")
    if extra_routes:
        warnings.append(f"routes without discovered native skill: {', '.join(extra_routes)}")

    expected_native_count = int(parity.get("native_skill_count") or 0)
    if expected_native_count != len(native_skills):
        reasons.append(
            f"native_skill_count={expected_native_count} does not match native_skills length={len(native_skills)}"
        )
    expected_configured_count = int(parity.get("configured_route_count") or 0)
    if expected_configured_count != len(items):
        reasons.append(
            f"configured_route_count={expected_configured_count} does not match items length={len(items)}"
        )
    routed_count = int(parity.get("routed_count") or 0)
    missing_route_count = int(parity.get("missing_route_count") or 0)
    actual_missing = _count(items, "missing") + len(missing_native)
    actual_routed = len(items) - _count(items, "missing")
    if routed_count != actual_routed:
        reasons.append(f"routed_count={routed_count} does not match actual routed count={actual_routed}")
    if missing_route_count != actual_missing:
        reasons.append(
            f"missing_route_count={missing_route_count} does not match actual missing count={actual_missing}"
        )
    if missing_route_count:
        reasons.append("all discovered AutoSci native skills must have a Solar route")

    count_fields = {
        "full_count": _count(items, "full"),
        "partial_count": _count(items, "partial"),
        "gated_count": _count(items, "gated"),
        "blocked_count": _count(items, "blocked"),
    }
    for field, actual in count_fields.items():
        expected = int(parity.get(field) or 0)
        if expected != actual:
            reasons.append(f"{field}={expected} does not match actual {actual}")
    if count_fields["partial_count"] or count_fields["gated_count"] or count_fields["blocked_count"]:
        warnings.append("parity inventory includes non-full routes; downstream execution must respect limitations")

    if not limitations(payload):
        reasons.append("top-level limitations must describe parity scope")
    check_artifact_paths(payload, path, reasons)
    return finish(payload, reasons, warnings, path=path)


if __name__ == "__main__":
    raise SystemExit(run_cli(evaluate, SCHEMA))
