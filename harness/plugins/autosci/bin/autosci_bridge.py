#!/usr/bin/env python3
"""AutoSci backend bridge for Solar Evidence ABI fixture-mode actions."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Callable

PLUGIN_DIR = Path(__file__).resolve().parents[1]
HARNESS_DIR = Path(os.environ.get("HARNESS_DIR", Path(__file__).resolve().parents[3]))
if str(PLUGIN_DIR) not in sys.path:
    sys.path.insert(0, str(PLUGIN_DIR))

from adapters.autosci_to_claim_verdict import convert as convert_claim_verdict
from adapters.autosci_to_experiment_plan import convert as convert_experiment_plan
from adapters.autosci_to_experiment_result import convert as convert_experiment_result
from adapters.autosci_to_research_claims import convert as convert_research_claims
from adapters.autosci_to_research_paper import convert as convert_research_paper
from adapters.autosci_to_scientific_report import convert as convert_scientific_report
from adapters.solar_envelope_to_autosci import load_envelope, normalize_envelope

REQUIRED_EVIDENCE_FIELDS = {
    "schema",
    "task_id",
    "sprint_id",
    "node_id",
    "status",
    "inputs",
    "outputs",
    "artifacts",
    "provenance",
    "limitations",
}


def _fixture_path(name: str) -> Path:
    return PLUGIN_DIR / "tests" / "fixtures" / name


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_sample_paper() -> dict[str, Any]:
    paper_path = _fixture_path("sample_paper.md")
    text = paper_path.read_text(encoding="utf-8")
    title = "AutoSci Adapter Fixture Paper"
    for line in text.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break
    return {
        "paper_id": "paper-autosci-fixture",
        "title": title,
        "source_type": "markdown",
        "source_ref": str(paper_path.relative_to(HARNESS_DIR)) if paper_path.is_relative_to(HARNESS_DIR) else str(paper_path),
        "identifiers": {"fixture": "autosci-phase4"},
        "abstract": "A fixture paper used to validate the AutoSci adapter bridge.",
        "parse_status": "parsed",
        "sections": [
            {
                "section_id": "abstract",
                "title": "Abstract",
                "text": "A fixture paper used to validate bridge conversion.",
                "source_anchor": "sample_paper.md#abstract",
            },
            {
                "section_id": "results",
                "title": "Results",
                "text": "The fixture path produces schema-shaped Solar evidence.",
                "source_anchor": "sample_paper.md#results",
            },
        ],
    }


def _rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(HARNESS_DIR.resolve()))
    except ValueError:
        return str(path)


def _output_dir(envelope: dict[str, Any], action: str) -> Path:
    configured = envelope.get("output_dir")
    if configured:
        out = Path(str(configured))
        if not out.is_absolute():
            out = HARNESS_DIR / out
        return out
    return HARNESS_DIR / "artifacts" / "autosci" / action


def _write_result(action: str, envelope: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    output_dir = _output_dir(envelope, action)
    output_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = output_dir / f"{action}.evidence.json"
    result_path = output_dir / "result.json"
    ledger_path = output_dir / "evidence.jsonl"
    evidence.setdefault("artifacts", []).append({"type": "solar_evidence_json", "path": _rel(evidence_path)})
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with ledger_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(evidence, sort_keys=True) + "\n")
    result = {
        "ok": True,
        "action": action,
        "status": evidence["status"],
        "schema": evidence["schema"],
        "result_path": _rel(result_path),
        "evidence_path": _rel(evidence_path),
        "evidence_jsonl": _rel(ledger_path),
        "evidence": evidence,
    }
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def _action_ingest_paper(envelope: dict[str, Any]) -> dict[str, Any]:
    return convert_research_paper(_read_sample_paper(), envelope)


def _action_extract_claims(envelope: dict[str, Any]) -> dict[str, Any]:
    return convert_research_claims(_load_json(_fixture_path("sample_autosci_raw_claims.json")), envelope)


def _action_design_experiment(envelope: dict[str, Any]) -> dict[str, Any]:
    return convert_experiment_plan({
        "experiment_id": "exp-001",
        "objective": "Validate fixture conversion through the AutoSci bridge.",
        "hypothesis": "Bridge fixture mode emits Solar Evidence ABI artifacts.",
        "variables": ["action", "fixture_payload"],
        "metrics": ["result_json_written", "evidence_jsonl_written"],
        "procedure": ["Run bridge", "Write evidence", "Validate required fields"],
        "approval_required": False,
        "expected_artifacts": ["result.json", "evidence.jsonl"],
    }, envelope)


def _action_run_experiment(envelope: dict[str, Any]) -> dict[str, Any]:
    return convert_experiment_result(_load_json(_fixture_path("sample_autosci_raw_experiment_result.json")), envelope)


def _action_verify_claim(envelope: dict[str, Any]) -> dict[str, Any]:
    raw = _load_json(_fixture_path("sample_autosci_raw_experiment_result.json"))
    raw.setdefault("claim_id", "claim-001")
    return convert_claim_verdict(raw, envelope)


def _action_write_report(envelope: dict[str, Any]) -> dict[str, Any]:
    return convert_scientific_report({
        "report_id": "report-001",
        "title": "AutoSci Adapter Fixture Report",
        "sections": [
            {
                "section_id": "summary",
                "title": "Summary",
                "evidence_ids": ["claim-001", "exp-001"],
                "body": "Fixture report generated by the AutoSci bridge.",
            }
        ],
        "evidence_ids": ["claim-001", "exp-001"],
        "unsupported_claims": [],
    }, envelope)


ACTIONS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "ingest_paper": _action_ingest_paper,
    "extract_claims": _action_extract_claims,
    "design_experiment": _action_design_experiment,
    "run_experiment": _action_run_experiment,
    "verify_claim": _action_verify_claim,
    "write_report": _action_write_report,
}


def validate_evidence_payload(payload: dict[str, Any]) -> list[str]:
    errors = []
    missing = sorted(REQUIRED_EVIDENCE_FIELDS - set(payload))
    if missing:
        errors.append(f"missing required fields: {', '.join(missing)}")
    if payload.get("status") not in {"completed", "failed", "inconclusive"}:
        errors.append("status must be completed, failed, or inconclusive")
    provenance = payload.get("provenance")
    if not isinstance(provenance, dict):
        errors.append("provenance must be an object")
    else:
        for field in ("operator_id", "implementation_package", "timestamp"):
            if not provenance.get(field):
                errors.append(f"provenance.{field} is required")
    if not isinstance(payload.get("artifacts"), list):
        errors.append("artifacts must be an array")
    if not isinstance(payload.get("limitations"), list):
        errors.append("limitations must be an array")
    return errors


def cmd_run(args: argparse.Namespace) -> int:
    if args.action not in ACTIONS:
        print(f"ERROR: unsupported action: {args.action}", file=sys.stderr)
        return 2
    envelope = load_envelope(args.envelope)
    evidence = ACTIONS[args.action](envelope)
    result = _write_result(args.action, envelope, evidence)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def cmd_smoke(args: argparse.Namespace) -> int:
    envelope = normalize_envelope({
        "task_id": "task-autosci-smoke",
        "sprint_id": "sprint-autosci-phase4",
        "node_id": "node-autosci-smoke",
        "mode": "fixture",
        "output_dir": "artifacts/autosci/smoke",
        "inputs": {"fixture": "plugins/autosci/tests/fixtures/sample_autosci_raw_claims.json"},
    })
    evidence = _action_extract_claims(envelope)
    result = _write_result("smoke", envelope, evidence)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    path = Path(args.result)
    if not path.is_absolute():
        path = HARNESS_DIR / path
    data = _load_json(path)
    payload = data.get("evidence") if isinstance(data.get("evidence"), dict) else data
    errors = validate_evidence_payload(payload)
    out = {"ok": not errors, "path": _rel(path), "errors": errors}
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0 if not errors else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="autosci_bridge.py",
        epilog="actions: " + ", ".join(sorted(ACTIONS)),
    )
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("smoke", help="Run fixture-mode smoke conversion")
    validate = sub.add_parser("validate", help="Validate a bridge result or evidence payload")
    validate.add_argument("--result", required=True)
    run = sub.add_parser("run", help="Run one fixture-mode backend action")
    run.add_argument("--action", required=True, choices=sorted(ACTIONS))
    run.add_argument("--envelope", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.cmd == "smoke":
        return cmd_smoke(args)
    if args.cmd == "validate":
        return cmd_validate(args)
    if args.cmd == "run":
        return cmd_run(args)
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
