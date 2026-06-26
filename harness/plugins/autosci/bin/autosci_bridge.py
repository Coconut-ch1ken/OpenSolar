#!/usr/bin/env python3
"""AutoSci backend bridge for Solar Evidence ABI fixture-mode actions."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

PLUGIN_DIR = Path(__file__).resolve().parents[1]
HARNESS_DIR = Path(os.environ.get("HARNESS_DIR", Path(__file__).resolve().parents[3])).resolve()
REPO_HARNESS_DIR = Path(__file__).resolve().parents[3]
if str(PLUGIN_DIR) not in sys.path:
    sys.path.insert(0, str(PLUGIN_DIR))

from adapters.autosci_to_claim_verdict import convert as convert_claim_verdict
from adapters.autosci_to_experiment_plan import convert as convert_experiment_plan
from adapters.autosci_to_experiment_result import convert as convert_experiment_result
from adapters.autosci_to_experiment_status import convert as convert_experiment_status
from adapters.autosci_to_code_evidence_map import convert as convert_code_evidence_map
from adapters.autosci_to_idea_candidate import convert as convert_idea_candidate
from adapters.autosci_to_idea_evaluation import convert as convert_idea_evaluation
from adapters.autosci_to_literature_discovery import convert as convert_literature_discovery
from adapters.autosci_to_research_claims import convert as convert_research_claims
from adapters.autosci_to_research_graph_update import convert as convert_research_graph_update
from adapters.autosci_to_research_memory_update import convert as convert_research_memory_update
from adapters.autosci_to_research_method import convert as convert_research_method
from adapters.autosci_to_research_paper import convert as convert_research_paper
from adapters.autosci_to_workflow_evolution import convert as convert_workflow_evolution
from adapters.autosci_to_publication_bundle import convert as convert_publication_bundle
from adapters.autosci_to_scientific_report import convert as convert_scientific_report
from adapters.solar_envelope_to_autosci import load_envelope, normalize_envelope
from backends.artifact_review import review_artifact
from backends.idea_source import build_idea_candidates
from backends.literature_discover import discover_literature
from backends.novelty_review import evaluate_novelty_and_review
from backends.paper_prepare import read_paper_source

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


def _resolve_harness_path(raw_path: str | Path) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    harness_candidate = HARNESS_DIR / path
    if harness_candidate.exists():
        return harness_candidate
    repo_candidate = REPO_HARNESS_DIR / path
    if repo_candidate.exists():
        return repo_candidate
    return harness_candidate


def _source_type_for(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return "pdf"
    if suffix in {".tex", ".latex"}:
        return "latex"
    if suffix in {".md", ".markdown"}:
        return "markdown"
    if suffix in {".html", ".htm"}:
        return "html"
    return "unknown"


def _markdown_sections(text: str, source_name: str) -> list[dict[str, str]]:
    sections: list[dict[str, str]] = []
    current: dict[str, Any] | None = None
    body: list[str] = []
    for line in text.splitlines():
        if line.startswith("## "):
            if current:
                current["text"] = "\n".join(body).strip()
                sections.append(current)
            title = line[3:].strip()
            section_id = title.lower().replace(" ", "-") or f"section-{len(sections) + 1}"
            current = {
                "section_id": section_id,
                "title": title,
                "source_anchor": f"{source_name}#{section_id}",
            }
            body = []
        elif current:
            body.append(line)
    if current:
        current["text"] = "\n".join(body).strip()
        sections.append(current)
    if not sections:
        sections.append({
            "section_id": "body",
            "title": "Body",
            "text": text.strip(),
            "source_anchor": f"{source_name}#body",
        })
    return sections


def _sentences(text: str) -> list[str]:
    normalized = " ".join(text.split())
    if not normalized:
        return []
    return [
        item.strip()
        for item in re.split(r"(?<=[.!?])\s+", normalized)
        if item.strip()
    ]


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "item"


def _claim_testability(text: str) -> tuple[str, str | None]:
    lowered = text.lower()
    testable_markers = {
        "empirical",
        "evaluate",
        "improve",
        "metric",
        "produce",
        "regression",
        "result",
        "verify",
        "without introducing",
        "write",
    }
    if any(marker in lowered for marker in testable_markers):
        return "testable", None
    return "not_testable", "The sentence is descriptive and does not state a direct test condition."


def _paper_claims_raw(envelope: dict[str, Any]) -> dict[str, Any]:
    paper = _read_sample_paper(envelope)
    sections = list(paper.get("sections") or [])
    paper_id = str(paper.get("paper_id") or "paper-autosci-fixture")
    claims: list[dict[str, Any]] = []
    def section_rank(section: dict[str, Any]) -> int:
        title = str(section.get("title") or section.get("section_id") or "").lower()
        if any(keyword in title for keyword in ("result", "finding", "evidence")):
            return 0
        if "abstract" in title:
            return 1
        return 2

    claim_sections = sorted(
        [section for section in sections if isinstance(section, dict)],
        key=section_rank,
    )
    for section in claim_sections:
        if not isinstance(section, dict):
            continue
        title = str(section.get("title") or section.get("section_id") or "")
        if "method" in title.lower() or "procedure" in title.lower():
            continue
        anchor = str(section.get("source_anchor") or paper.get("source_ref") or paper_id)
        for sentence in _sentences(str(section.get("text") or ""))[:2]:
            testability, reason = _claim_testability(sentence)
            claim: dict[str, Any] = {
                "claim_id": f"claim-{len(claims) + 1:03d}",
                "text": sentence,
                "claim_type": "result" if testability == "testable" else "background",
                "source_anchor": anchor,
                "testability": testability,
                "evidence_ids": [paper_id, anchor],
            }
            if reason:
                claim["non_testable_reason"] = reason
            claims.append(claim)
            if len(claims) >= 3:
                break
        if len(claims) >= 3:
            break
    if not claims:
        anchor = str(paper.get("source_ref") or paper_id)
        claims.append({
            "claim_id": "claim-001",
            "text": "No grounded claim candidate was found in the input paper.",
            "claim_type": "background",
            "source_anchor": anchor,
            "testability": "not_testable",
            "non_testable_reason": "The input paper did not contain a usable claim sentence.",
            "evidence_ids": [paper_id, anchor],
        })
    return {
        "claims": claims,
        "limitations": [
            "Claim extraction is deterministic and section-based; claims remain unverified until a verifier runs.",
        ],
    }


def _method_steps(text: str) -> list[str]:
    sentences = _sentences(text)
    if not sentences:
        return ["No explicit procedure text was found in the input paper."]
    first = sentences[0]
    parts = [
        part.strip(" .")
        for part in re.split(r",\s+and\s+|,\s+|\s+and\s+", first)
        if part.strip(" .")
    ]
    if len(parts) >= 2:
        return [part[0].upper() + part[1:] if len(part) > 1 else part.upper() for part in parts[:5]]
    return sentences[:5]


def _paper_methods_raw(envelope: dict[str, Any]) -> dict[str, Any]:
    paper = _read_sample_paper(envelope)
    sections = [section for section in list(paper.get("sections") or []) if isinstance(section, dict)]
    method_sections = [
        section
        for section in sections
        if any(
            keyword in str(section.get("title") or section.get("section_id") or "").lower()
            for keyword in ("method", "approach", "workflow", "procedure")
        )
    ]
    if not method_sections and sections:
        method_sections = [sections[0]]
    paper_id = str(paper.get("paper_id") or "paper-autosci-fixture")
    methods: list[dict[str, Any]] = []
    for section in method_sections[:2]:
        text = str(section.get("text") or "")
        anchor = str(section.get("source_anchor") or paper.get("source_ref") or paper_id)
        title = str(section.get("title") or "Method")
        summary = (_sentences(text) or ["No explicit method summary was found in the input paper."])[0]
        methods.append({
            "method_id": f"method-{len(methods) + 1:03d}",
            "name": f"{title} protocol",
            "summary": summary,
            "procedure": _method_steps(text),
            "source_papers": [paper_id],
            "evidence_ids": [paper_id, anchor],
            "source_anchor": anchor,
        })
    if not methods:
        anchor = str(paper.get("source_ref") or paper_id)
        methods.append({
            "method_id": "method-001",
            "name": "No explicit method found",
            "summary": "The input paper did not contain a method section.",
            "procedure": ["Mark method extraction as incomplete for this paper."],
            "source_papers": [paper_id],
            "evidence_ids": [paper_id, anchor],
            "source_anchor": anchor,
        })
    return {
        "methods": methods,
        "limitations": [
            "Method extraction is deterministic and section-based; it does not infer hidden procedure steps.",
        ],
    }


def _read_sample_paper(envelope: dict[str, Any] | None = None, *, analyzed: bool = False) -> dict[str, Any]:
    inputs = dict((envelope or {}).get("inputs") or {})
    raw_path = inputs.get("paper_path") or _fixture_path("sample_paper.md")
    raw_path_text = str(raw_path)
    is_remote_source = raw_path_text.startswith(("http://", "https://"))
    paper_path = Path(raw_path_text) if is_remote_source else _resolve_harness_path(raw_path)
    if not is_remote_source and not paper_path.exists():
        return {
            "paper_id": "paper-missing",
            "title": "Missing paper source",
            "source_type": "unknown",
            "source_ref": str(raw_path),
            "identifiers": {"fixture": "autosci-phase9"},
            "abstract": "",
            "parse_status": "failed",
            "sections": [],
            "status": "failed",
            "limitations": [f"Paper source not found: {raw_path}"],
        }
    raw_root_raw = Path(str(inputs.get("raw_root") or "artifacts/autosci/workspace/raw"))
    raw_root = raw_root_raw if raw_root_raw.is_absolute() else HARNESS_DIR / raw_root_raw
    allow_network_fetch = str(inputs.get("allow_network_fetch", "true")).lower() not in {"0", "false", "no"}
    if os.environ.get("AUTOSCI_DISABLE_NETWORK_FETCH", "").lower() in {"1", "true", "yes"}:
        allow_network_fetch = False
    return read_paper_source(
        paper_path,
        raw_root=raw_root,
        workspace_root=HARNESS_DIR,
        repository_root=REPO_HARNESS_DIR,
        paper_id=str(inputs.get("paper_id") or f"paper-{paper_path.stem.replace('_', '-')}"),
        title=str(inputs.get("paper_title") or inputs.get("title") or inputs.get("pdf_title") or ""),
        arxiv_id=str(inputs.get("arxiv_id") or ""),
        allow_network_fetch=allow_network_fetch,
        analyzed=analyzed,
    )


def _rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(HARNESS_DIR.resolve()))
    except ValueError:
        try:
            return str(path.resolve().relative_to(REPO_HARNESS_DIR.resolve()))
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


def _configured_output_path(
    envelope: dict[str, Any],
    key: str,
    default_path: Path,
    *,
    legacy_key: str | None = None,
    legacy_suffix: str | None = None,
) -> Path:
    outputs = envelope.get("outputs") if isinstance(envelope.get("outputs"), dict) else {}
    raw = outputs.get(key) if isinstance(outputs, dict) else None
    if not raw and legacy_key and isinstance(outputs, dict):
        legacy = str(outputs.get(legacy_key) or "")
        if legacy and (legacy_suffix is None or legacy.endswith(legacy_suffix)):
            raw = legacy
    if not raw:
        return default_path
    path = Path(str(raw))
    if not path.is_absolute():
        path = HARNESS_DIR / path
    return path


def _approval_path_entries(raw_values: Any) -> list[dict[str, Any]]:
    values = raw_values if isinstance(raw_values, list) else ([raw_values] if raw_values else [])
    entries: list[dict[str, Any]] = []
    for raw in values:
        raw_text = str(raw or "").strip()
        if not raw_text:
            continue
        if raw_text.startswith(("http://", "https://")):
            entries.append({
                "path": raw_text,
                "artifact_path": raw_text,
                "exists": False,
                "kind": "external_ref",
                "verifiable": False,
            })
            continue
        path = _resolve_harness_path(raw_text)
        entries.append({
            "path": raw_text,
            "artifact_path": _rel(path),
            "exists": path.exists(),
            "kind": "directory" if path.is_dir() else ("file" if path.is_file() else "missing"),
            "verifiable": True,
        })
    return entries


def _all_existing(entries: list[dict[str, Any]]) -> bool:
    return bool(entries) and all(bool(item.get("exists")) for item in entries)


def _missing_contract_items(label: str, entries: list[dict[str, Any]]) -> list[str]:
    if not entries:
        return [label]
    return [
        f"{label}:{item.get('path')}"
        for item in entries
        if not bool(item.get("exists"))
    ]


def _approval_contract(envelope: dict[str, Any], action: str, side_effects: list[str]) -> dict[str, Any]:
    inputs = envelope.get("inputs") if isinstance(envelope.get("inputs"), dict) else {}
    approval_ref = str(inputs.get("approval_ref") or "").strip()
    allowlist_entries = _approval_path_entries(inputs.get("allowlist_evidence"))
    runtime_entries = _approval_path_entries(inputs.get("runtime_evidence"))
    before_entries = _approval_path_entries(inputs.get("before_artifacts"))
    after_entries = _approval_path_entries(inputs.get("after_artifacts"))
    approved = bool(approval_ref and approval_ref.upper() != "N/A")
    allowlist_ready = _all_existing(allowlist_entries)
    before_ready = _all_existing(before_entries)
    runtime_ready = _all_existing(runtime_entries)
    after_ready = _all_existing(after_entries)
    ready_for_execution = approved and allowlist_ready and before_ready
    execution_verified = ready_for_execution and runtime_ready and after_ready
    missing: list[str] = []
    if not approved:
        missing.append("approval_ref")
    missing.extend(_missing_contract_items("allowlist_evidence", allowlist_entries))
    missing.extend(_missing_contract_items("before_artifacts", before_entries))
    missing.extend(_missing_contract_items("runtime_evidence", runtime_entries))
    missing.extend(_missing_contract_items("after_artifacts", after_entries))
    if execution_verified:
        approval_state = "verified"
    elif ready_for_execution:
        approval_state = "approved_pending_runtime"
    elif approved:
        approval_state = "approved_missing_preflight"
    else:
        approval_state = "approval_required"
    return {
        "schema": "autosci_approval_contract.v1",
        "action": action,
        "side_effects": side_effects,
        "approval_ref": approval_ref,
        "approval_state": approval_state,
        "approved": approved,
        "allowlist_ready": allowlist_ready,
        "before_ready": before_ready,
        "ready_for_execution": ready_for_execution,
        "runtime_ready": runtime_ready,
        "after_ready": after_ready,
        "execution_verified": execution_verified,
        "allowlist_evidence": allowlist_entries,
        "runtime_evidence": runtime_entries,
        "before_artifacts": before_entries,
        "after_artifacts": after_entries,
        "missing": missing,
    }


def _approval_contract_limitations(contract: dict[str, Any]) -> list[str]:
    if contract.get("execution_verified") is True:
        return []
    missing = contract.get("missing") if isinstance(contract.get("missing"), list) else []
    suffix = f": {', '.join(str(item) for item in missing)}" if missing else "."
    return [f"Approval/runtime evidence contract is not fully verified{suffix}"]


def _refresh_approval_contract(contract: dict[str, Any]) -> dict[str, Any]:
    allowlist_entries = contract.get("allowlist_evidence") if isinstance(contract.get("allowlist_evidence"), list) else []
    runtime_entries = contract.get("runtime_evidence") if isinstance(contract.get("runtime_evidence"), list) else []
    before_entries = contract.get("before_artifacts") if isinstance(contract.get("before_artifacts"), list) else []
    after_entries = contract.get("after_artifacts") if isinstance(contract.get("after_artifacts"), list) else []
    approved = bool(str(contract.get("approval_ref") or "").strip())
    allowlist_ready = _all_existing(allowlist_entries)
    before_ready = _all_existing(before_entries)
    runtime_ready = _all_existing(runtime_entries)
    after_ready = _all_existing(after_entries)
    ready_for_execution = approved and allowlist_ready and before_ready
    execution_verified = ready_for_execution and runtime_ready and after_ready
    missing: list[str] = []
    if not approved:
        missing.append("approval_ref")
    missing.extend(_missing_contract_items("allowlist_evidence", allowlist_entries))
    missing.extend(_missing_contract_items("before_artifacts", before_entries))
    missing.extend(_missing_contract_items("runtime_evidence", runtime_entries))
    missing.extend(_missing_contract_items("after_artifacts", after_entries))
    contract.update({
        "approved": approved,
        "allowlist_ready": allowlist_ready,
        "before_ready": before_ready,
        "ready_for_execution": ready_for_execution,
        "runtime_ready": runtime_ready,
        "after_ready": after_ready,
        "execution_verified": execution_verified,
        "missing": missing,
        "approval_state": "verified"
        if execution_verified
        else ("approved_pending_runtime" if ready_for_execution else ("approved_missing_preflight" if approved else "approval_required")),
    })
    return contract


def _contract_existing_artifacts(contract: dict[str, Any], key: str, artifact_type: str) -> list[dict[str, str]]:
    entries = contract.get(key) if isinstance(contract.get(key), list) else []
    artifacts: list[dict[str, str]] = []
    for entry in entries:
        if not isinstance(entry, dict) or not entry.get("exists"):
            continue
        path = str(entry.get("artifact_path") or entry.get("path") or "").strip()
        if path:
            artifacts.append({"type": artifact_type, "path": path})
    return artifacts


def _write_approval_contract_sidecar(envelope: dict[str, Any], action: str, contract: dict[str, Any]) -> dict[str, str]:
    output_dir = _output_dir(envelope, action)
    path = _configured_output_path(
        envelope,
        "approval_contract_path",
        output_dir / f"{action}_approval_contract.json",
    )
    return {"type": "approval_contract_json", "path": _write_json_sidecar(path, contract)}


def _runtime_records(contract: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    entries = contract.get("runtime_evidence") if isinstance(contract.get("runtime_evidence"), list) else []
    for entry in entries:
        if not isinstance(entry, dict) or not entry.get("exists"):
            continue
        raw_path = str(entry.get("path") or entry.get("artifact_path") or "").strip()
        if not raw_path:
            continue
        path = _resolve_harness_path(raw_path)
        if path.is_dir():
            errors.append(f"runtime evidence is a directory: {_rel(path)}")
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            errors.append(f"runtime evidence unreadable: {_rel(path)}: {exc}")
            continue
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            records.append({"text": text, "source_path": _rel(path)})
            continue
        if isinstance(payload, dict):
            payload.setdefault("source_path", _rel(path))
            records.append(payload)
        elif isinstance(payload, list):
            for item in payload:
                if isinstance(item, dict):
                    item.setdefault("source_path", _rel(path))
                    records.append(item)
                else:
                    records.append({"value": item, "source_path": _rel(path)})
        else:
            records.append({"value": payload, "source_path": _rel(path)})
    return records, errors


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    return str(value or "").strip().lower() in {"1", "true", "yes", "ok", "pass", "passed", "success", "completed"}


def _status_ok(value: Any) -> bool:
    return str(value or "").strip().lower() in {"ok", "pass", "passed", "success", "completed", "succeeded"}


def _field(record: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in record:
            return record[key]
    outputs = record.get("outputs") if isinstance(record.get("outputs"), dict) else {}
    for key in keys:
        if key in outputs:
            return outputs[key]
    runtime = outputs.get("runtime") if isinstance(outputs.get("runtime"), dict) else {}
    for key in keys:
        if key in runtime:
            return runtime[key]
    result = outputs.get("result") if isinstance(outputs.get("result"), dict) else {}
    for key in keys:
        if key in result:
            return result[key]
    return None


def _runtime_exit_ok(record: dict[str, Any]) -> bool:
    exit_code = _field(record, "exit_code", "returncode", "compile_exit_code")
    if exit_code is not None:
        try:
            return int(exit_code) == 0
        except (TypeError, ValueError):
            return False
    return _truthy(_field(record, "success", "ok", "completed")) or _status_ok(_field(record, "status"))


def _record_path_exists(record: dict[str, Any], *keys: str) -> bool:
    for key in keys:
        raw = _field(record, key)
        values = raw if isinstance(raw, list) else ([raw] if raw else [])
        for value in values:
            if not isinstance(value, str) or not value.strip():
                continue
            if _resolve_harness_path(value).exists():
                return True
    return False


def _candidate_from_runtime(raw: dict[str, Any], index: int) -> dict[str, Any] | None:
    title = str(raw.get("title") or raw.get("paper_title") or "").strip()
    if not title:
        return None
    source_ref = str(raw.get("source_ref") or raw.get("url") or raw.get("pdf_url") or raw.get("arxiv_id") or "").strip()
    channels = raw.get("source_channels") if isinstance(raw.get("source_channels"), list) else []
    if not channels:
        channels = ["arxiv"] if raw.get("arxiv_id") or "arxiv" in source_ref.lower() else ["approved_runtime"]
    try:
        score = float(raw.get("ranking_score", 1.0))
    except (TypeError, ValueError):
        score = 1.0
    candidate = {
        "candidate_id": str(raw.get("candidate_id") or raw.get("paper_id") or raw.get("arxiv_id") or f"runtime-candidate-{index:03d}"),
        "title": title,
        "source_channels": [str(item) for item in channels if str(item).strip()],
        "ranking_score": score,
        "ranking_rationale": str(raw.get("ranking_rationale") or "Approved runtime evidence supplied this discovery candidate."),
        "dedup_status": str(raw.get("dedup_status") or "unknown"),
        "fetch_status": str(raw.get("fetch_status") or "fetched"),
    }
    if source_ref:
        candidate["source_ref"] = source_ref
    if raw.get("abstract"):
        candidate["abstract"] = str(raw["abstract"])
    return candidate


def _runtime_candidates(records: list[dict[str, Any]], *, limit: int) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for record in records:
        raw_candidates = _field(record, "candidates", "papers", "items")
        if isinstance(raw_candidates, dict):
            raw_candidates = [raw_candidates]
        if not isinstance(raw_candidates, list):
            raw_candidates = [record] if record.get("title") else []
        for raw in raw_candidates:
            if not isinstance(raw, dict):
                continue
            candidate = _candidate_from_runtime(raw, len(candidates) + 1)
            if candidate:
                candidates.append(candidate)
            if len(candidates) >= limit:
                return candidates
    return candidates


def _runtime_metrics(record: dict[str, Any]) -> list[dict[str, Any]]:
    raw_metrics = _field(record, "metrics")
    if not isinstance(raw_metrics, list):
        return []
    metrics: list[dict[str, Any]] = []
    for item in raw_metrics:
        if isinstance(item, dict) and str(item.get("name") or "").strip():
            metrics.append(item)
    return metrics


def _runtime_evidence_ids(records: list[dict[str, Any]]) -> list[str]:
    evidence_ids: list[str] = []
    for record in records:
        raw = _field(record, "evidence_ids")
        values = raw if isinstance(raw, list) else ([raw] if raw else [])
        evidence_ids.extend(str(item) for item in values if str(item).strip())
        for key in ("task_id", "node_id", "source_path"):
            value = record.get(key)
            if str(value or "").strip():
                evidence_ids.append(str(value))
    return _unique_strings(evidence_ids)


def _runtime_logs(records: list[dict[str, Any]]) -> list[str]:
    logs: list[str] = []
    for record in records:
        raw = _field(record, "logs", "log", "stdout", "stderr")
        values = raw if isinstance(raw, list) else ([raw] if raw else [])
        for value in values:
            text = str(value).strip()
            if text:
                logs.append(text[:1000])
    return logs


def _approval_semantic_runtime(contract: dict[str, Any], action: str, *, limit: int = 10) -> dict[str, Any]:
    records, errors = _runtime_records(contract)
    checks: list[dict[str, Any]] = [
        {
            "check": "approval_contract_execution_verified",
            "status": "ok" if contract.get("execution_verified") else "error",
            "detail": "Approval, allowlist, runtime, and before/after artifact paths are present."
            if contract.get("execution_verified")
            else "Approval contract path-level verification is incomplete.",
        },
        {
            "check": "runtime_records_loaded",
            "status": "ok" if records else "error",
            "detail": f"{len(records)} runtime record(s) loaded.",
        },
    ]
    if errors:
        checks.append({"check": "runtime_read_errors", "status": "error", "detail": "; ".join(errors)})
    verified = bool(contract.get("execution_verified")) and bool(records) and not errors
    detail: dict[str, Any] = {
        "records_loaded": len(records),
        "errors": errors,
        "evidence_ids": _runtime_evidence_ids(records),
    }

    if action == "build_poster":
        browser_rendered = any(_truthy(_field(record, "browser_rendered", "rendered")) for record in records)
        overflow_passed = any(
            _truthy(_field(record, "overflow_ok", "overflow_passed"))
            or str(_field(record, "overflow_probe") or "").strip().lower() in {"ok", "pass", "passed", "none", "no_overflow"}
            for record in records
        )
        png_exported = any(
            _truthy(_field(record, "png_exported", "image_exported"))
            or _record_path_exists(record, "png_path", "png_artifact", "image_path")
            for record in records
        )
        checks.extend([
            {"check": "browser_rendered", "status": "ok" if browser_rendered else "error", "detail": str(browser_rendered)},
            {"check": "overflow_probe_passed", "status": "ok" if overflow_passed else "error", "detail": str(overflow_passed)},
            {"check": "png_exported", "status": "ok" if png_exported else "error", "detail": str(png_exported)},
        ])
        verified = verified and browser_rendered and overflow_passed and png_exported
        detail.update({
            "browser_rendered": browser_rendered,
            "overflow_probe_passed": overflow_passed,
            "png_exported": png_exported,
        })
    elif action == "compile_paper":
        exit_ok = any(_runtime_exit_ok(record) for record in records)
        pdf_ready = any(
            _truthy(_field(record, "pdf_generated", "compiled_pdf_present"))
            or _record_path_exists(record, "pdf_path", "output_pdf", "compiled_pdf")
            for record in records
        )
        checks.extend([
            {"check": "compile_exit_ok", "status": "ok" if exit_ok else "error", "detail": str(exit_ok)},
            {"check": "compiled_pdf_verified", "status": "ok" if pdf_ready else "error", "detail": str(pdf_ready)},
        ])
        verified = verified and exit_ok and pdf_ready
        detail.update({"compile_exit_ok": exit_ok, "compiled_pdf_verified": pdf_ready})
    elif action == "run_pilot_experiment":
        exit_ok = any(_runtime_exit_ok(record) for record in records)
        metrics = [metric for record in records for metric in _runtime_metrics(record)]
        result_collected = bool(metrics) or any(_truthy(_field(record, "result_collected")) for record in records)
        allowed_outcomes = {"supports", "partially_supports", "refutes", "inconclusive", "failed"}
        outcome = next(
            (
                str(_field(record, "outcome")).strip()
                for record in records
                if str(_field(record, "outcome") or "").strip() in allowed_outcomes
            ),
            "supports" if exit_ok and result_collected else "inconclusive",
        )
        checks.extend([
            {"check": "pilot_exit_ok", "status": "ok" if exit_ok else "error", "detail": str(exit_ok)},
            {"check": "pilot_result_collected", "status": "ok" if result_collected else "error", "detail": str(result_collected)},
        ])
        verified = verified and exit_ok and result_collected
        detail.update({
            "pilot_exit_ok": exit_ok,
            "metrics": metrics,
            "result_collected": result_collected,
            "outcome": outcome,
        })
    elif action == "run_experiment":
        exit_ok = any(_runtime_exit_ok(record) for record in records)
        metrics = [metric for record in records for metric in _runtime_metrics(record)]
        result_collected = bool(metrics) or any(
            _truthy(_field(record, "result_collected", "experiment_result_collected"))
            or _record_path_exists(record, "result_path", "experiment_result_path", "output_json")
            for record in records
        )
        allowed_outcomes = {"supports", "partially_supports", "refutes", "inconclusive", "failed"}
        outcome = next(
            (
                str(_field(record, "outcome", "experiment_outcome")).strip()
                for record in records
                if str(_field(record, "outcome", "experiment_outcome") or "").strip() in allowed_outcomes
            ),
            "supports" if exit_ok and result_collected else "inconclusive",
        )
        command_run = next(
            (
                str(_field(record, "command_run", "command")).strip()
                for record in records
                if str(_field(record, "command_run", "command") or "").strip()
            ),
            "approved-runtime-evidence",
        )
        checks.extend([
            {"check": "experiment_exit_ok", "status": "ok" if exit_ok else "error", "detail": str(exit_ok)},
            {"check": "experiment_result_collected", "status": "ok" if result_collected else "error", "detail": str(result_collected)},
        ])
        verified = verified and exit_ok and result_collected
        detail.update({
            "experiment_exit_ok": exit_ok,
            "metrics": metrics,
            "result_collected": result_collected,
            "outcome": outcome,
            "command_run": command_run,
            "logs": _runtime_logs(records),
        })
    elif action in {"daily_arxiv_prepare_finalize", "init_sources", "discover_literature"}:
        candidates = _runtime_candidates(records, limit=limit)
        fetch_ok = bool(candidates) and any(_runtime_exit_ok(record) for record in records)
        checks.extend([
            {"check": "source_fetch_ok", "status": "ok" if fetch_ok else "error", "detail": str(fetch_ok)},
            {"check": "candidates_present", "status": "ok" if candidates else "error", "detail": str(len(candidates))},
        ])
        verified = verified and fetch_ok and bool(candidates)
        detail.update({"candidates": candidates, "source_fetch_ok": fetch_ok})

    status = "verified" if verified else "incomplete"
    return {
        "schema": "autosci_runtime_semantic_verification.v1",
        "action": action,
        "status": status,
        "verified": verified,
        "checks": checks,
        "detail": detail,
    }


def _write_evidence_payload(path: Path, evidence: dict[str, Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path = _rel(path)
    artifacts = evidence.setdefault("artifacts", [])
    if not any(isinstance(item, dict) and item.get("path") == artifact_path for item in artifacts):
        artifacts.append({"type": "solar_evidence_json", "path": artifact_path})
    path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return artifact_path


def _configured_handoff_path(envelope: dict[str, Any]) -> Path | None:
    outputs = envelope.get("outputs") if isinstance(envelope.get("outputs"), dict) else {}
    raw = envelope.get("handoff_path") or outputs.get("handoff_path") or os.environ.get("HANDOFF")
    if not raw:
        return None
    path = Path(str(raw))
    if not path.is_absolute():
        path = HARNESS_DIR / path
    return path


def _handoff_lines(action: str, evidence: dict[str, Any], result: dict[str, Any]) -> list[str]:
    lines = [
        "# AutoSci Phase 10 Handoff",
        "",
        f"- Action: `{action}`",
        f"- Schema: `{evidence.get('schema')}`",
        f"- Status: `{evidence.get('status')}`",
        f"- Result: `{result.get('result_path')}`",
        f"- Evidence: `{result.get('evidence_path')}`",
        f"- Evidence ledger: `{result.get('evidence_jsonl')}`",
        "",
    ]
    payloads: list[dict[str, Any]] = []
    inputs = evidence.get("inputs") if isinstance(evidence.get("inputs"), dict) else {}
    if inputs.get("paper_path") and not inputs.get("source_evidence"):
        payloads.append({
            "schema": "research_paper.v1",
            "outputs": {"paper": _read_sample_paper({"inputs": inputs})},
        })
    for key in ("source_evidence", "claims_evidence", "method_evidence"):
        related = _load_optional_evidence(inputs.get(key))
        if related and related.get("schema") != evidence.get("schema"):
            payloads.append(related)
    payloads.append(evidence)
    seen_sections: set[str] = set()
    for payload in payloads:
        outputs = payload.get("outputs") if isinstance(payload.get("outputs"), dict) else {}
        paper = outputs.get("paper") if isinstance(outputs, dict) else None
        if isinstance(paper, dict) and "paper" not in seen_sections:
            seen_sections.add("paper")
            lines.extend(["## Paper", ""])
            lines.append(f"- {paper.get('paper_id')}: {paper.get('title')} ({paper.get('source_ref')})")
            lines.append("")
        claims = outputs.get("claims") if isinstance(outputs, dict) else None
        if isinstance(claims, list) and "claims" not in seen_sections:
            seen_sections.add("claims")
            lines.extend(["## Claims", ""])
            for claim in claims:
                if not isinstance(claim, dict):
                    continue
                lines.append(
                    "- "
                    f"{claim.get('claim_id')}: {claim.get('testability')} at "
                    f"{claim.get('source_anchor')} - {claim.get('text')}"
                )
            lines.append("")
        methods = outputs.get("methods") if isinstance(outputs, dict) else None
        if isinstance(methods, list) and "methods" not in seen_sections:
            seen_sections.add("methods")
            lines.extend(["## Methods", ""])
            for method in methods:
                if not isinstance(method, dict):
                    continue
                lines.append(
                    "- "
                    f"{method.get('method_id')}: {method.get('name')} at "
                    f"{method.get('source_anchor', 'N/A')}"
                )
            lines.append("")
        mappings = outputs.get("mappings") if isinstance(outputs, dict) else None
        if isinstance(mappings, list) and "mappings" not in seen_sections:
            seen_sections.add("mappings")
            lines.extend(["## Code Evidence", ""])
            for mapping in mappings:
                if not isinstance(mapping, dict):
                    continue
                files = ", ".join(str(item) for item in mapping.get("files", []))
                lines.append(
                    "- "
                    f"{mapping.get('mapping_id')}: {mapping.get('relevance_label')} "
                    f"for {mapping.get('claim_id')} in {files}"
                )
                if mapping.get("relevance_reason"):
                    lines.append(f"  Reason: {mapping.get('relevance_reason')}")
                if mapping.get("unknown_reason"):
                    lines.append(f"  Unknown: {mapping.get('unknown_reason')}")
            lines.append("")
    limitations = evidence.get("limitations")
    if isinstance(limitations, list) and limitations:
        lines.extend(["## Limitations", ""])
        for limitation in limitations:
            lines.append(f"- {limitation}")
    return lines


def _write_handoff(path: Path, action: str, evidence: dict[str, Any], result: dict[str, Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(_handoff_lines(action, evidence, result)).rstrip() + "\n", encoding="utf-8")
    return _rel(path)


def _write_result(
    action: str,
    envelope: dict[str, Any],
    evidence: dict[str, Any],
    *,
    extra_result_fields: dict[str, Any] | None = None,
) -> dict[str, Any]:
    output_dir = _output_dir(envelope, action)
    output_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = _configured_output_path(
        envelope,
        "evidence_payload_path",
        output_dir / f"{action}.evidence.json",
        legacy_key="evidence_path",
        legacy_suffix=".json",
    )
    result_path = _configured_output_path(envelope, "result_path", output_dir / "result.json")
    ledger_path = _configured_output_path(
        envelope,
        "evidence_jsonl",
        output_dir / "evidence.jsonl",
        legacy_key="evidence_path",
        legacy_suffix=".jsonl",
    )
    handoff_path = _configured_handoff_path(envelope)
    if handoff_path:
        handoff_artifact_path = _rel(handoff_path)
        artifacts = evidence.setdefault("artifacts", [])
        if not any(isinstance(item, dict) and item.get("path") == handoff_artifact_path for item in artifacts):
            artifacts.append({"type": "handoff_markdown", "path": handoff_artifact_path})
    evidence_artifact_path = _write_evidence_payload(evidence_path, evidence)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(evidence, sort_keys=True) + "\n")
    result = {
        "ok": True,
        "action": action,
        "status": evidence["status"],
        "schema": evidence["schema"],
        "result_path": _rel(result_path),
        "evidence_path": evidence_artifact_path,
        "evidence_jsonl": _rel(ledger_path),
        "evidence": evidence,
    }
    if extra_result_fields:
        result.update(extra_result_fields)
    if handoff_path:
        result["handoff_path"] = _write_handoff(handoff_path, action, evidence, result)
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def _action_ingest_paper(envelope: dict[str, Any]) -> dict[str, Any]:
    return convert_research_paper(_read_sample_paper(envelope), envelope)


def _action_analyze_paper(envelope: dict[str, Any]) -> dict[str, Any]:
    return convert_research_paper(_read_sample_paper(envelope, analyzed=True), envelope)


def _paper_update_raw(envelope: dict[str, Any], evidence: dict[str, Any] | None = None) -> dict[str, Any]:
    paper = dict(((evidence or {}).get("outputs") or {}).get("paper") or _read_sample_paper(envelope))
    return {
        "paper_id": str(paper.get("paper_id") or "paper-autosci-fixture"),
        "title": str(paper.get("title") or "AutoSci Fixture Paper"),
        "source_ref": str(paper.get("source_ref") or "plugins/autosci/tests/fixtures/sample_paper.md"),
        "memory_path": f"knowledge/research/papers/{paper.get('paper_id') or 'paper-autosci-fixture'}.md",
        "evidence_ids": [str(paper.get("paper_id") or "paper-autosci-fixture")],
    }


def _action_update_memory(envelope: dict[str, Any]) -> dict[str, Any]:
    return convert_research_memory_update(_paper_update_raw(envelope), envelope)


def _action_update_graph(envelope: dict[str, Any]) -> dict[str, Any]:
    return convert_research_graph_update(_paper_update_raw(envelope), envelope)


def _memory_target(envelope: dict[str, Any], fallback: str) -> str:
    inputs = dict(envelope.get("inputs") or {})
    return str(inputs.get("target") or inputs.get("topic") or inputs.get("title") or fallback)


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _local_mutation_requested(envelope: dict[str, Any]) -> bool:
    inputs = dict(envelope.get("inputs") or {})
    approval_ref = str(inputs.get("approval_ref") or "").strip()
    return bool(approval_ref and inputs.get("execute_approved_side_effect"))


def _wiki_page_rel_for_target(target: str, default_dir: str, default_prefix: str = "") -> Path:
    raw = Path(str(target or "").strip())
    if raw.suffix.lower() in {".md", ".markdown"}:
        if raw.is_absolute():
            return Path(raw.name)
        parts = raw.parts
        if parts and parts[0] == "wiki":
            return Path(*parts[1:])
        return raw
    slug = _slug(target or default_prefix or "page")
    name = f"{default_prefix}-{slug}.md" if default_prefix and not slug.startswith(default_prefix) else f"{slug}.md"
    return Path(default_dir) / name


def _write_generic_wiki_log(root: Path, event: str, target_path: Path, evidence_ids: list[str], summary: str) -> Path:
    log_path = root / "log.md"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    log_path.open("a", encoding="utf-8").write(
        "\n".join(
            [
                "",
                f"## {event}",
                "",
                f"- Timestamp: `{timestamp}`",
                f"- Target: `{_rel(target_path)}`",
                f"- Evidence ids: {', '.join(evidence_ids) if evidence_ids else 'N/A'}",
                f"- Summary: {summary}",
                "",
            ]
        )
    )
    return log_path


def _rebuild_generic_wiki_views(root: Path, run_id: str, target_path: Path, evidence_ids: list[str]) -> list[Path]:
    updated: list[Path] = []
    index_path = root / "index.md"
    lines = [
        "# Solar AutoSci Wiki\n\n",
        "Human-facing research memory projected from Solar-managed evidence and approved wiki mutations.\n\n",
        f"Last mutation run: `{run_id}`\n\n",
    ]
    for subdir in ["papers", "concepts", "methods", "people", "topics", "ideas", "experiments", "outputs"]:
        lines.append(f"## {subdir.title()}\n\n")
        pages = sorted((root / subdir).glob("*.md"))
        if not pages:
            lines.append("- N/A\n\n")
            continue
        for page in pages:
            lines.append(f"- [{page.stem}]({subdir}/{page.name})\n")
        lines.append("\n")
    if _write_text_if_changed_bridge(index_path, "".join(lines)):
        updated.append(index_path)

    context_path = root / "graph" / "context_brief.md"
    context = "\n".join(
        [
            "# Solar AutoSci Context Brief",
            "",
            f"Last mutation run: `{run_id}`",
            f"Updated at: `{datetime.now(UTC).replace(microsecond=0).isoformat().replace('+00:00', 'Z')}`",
            f"Mutation target: `{_rel(target_path)}`",
            f"Evidence ids: {', '.join(evidence_ids) if evidence_ids else 'N/A'}",
            "",
            "Use `wiki/graph/edges.jsonl` for structured mutation edges.",
            "Use `artifacts/autosci/runs/` for Solar-managed execution evidence.",
            "",
        ]
    )
    if _write_text_if_changed_bridge(context_path, context):
        updated.append(context_path)
    return updated


def _action_prefill_foundations(envelope: dict[str, Any]) -> dict[str, Any]:
    inputs = dict(envelope.get("inputs") or {})
    target = _memory_target(envelope, "foundation")
    slug = _slug(target)
    evidence_ids = [f"prefill:{slug}"]
    if _local_mutation_requested(envelope):
        wiki_root = _wiki_roots_for_write(envelope)[0]
        page = wiki_root / "topics" / f"foundation-{slug}.md"
        body = "\n".join(
            [
                "---",
                'entity_type: "foundation"',
                f'entity_id: "foundation-{slug}"',
                f'title: {json.dumps(target)}',
                f'approval_ref: {json.dumps(str(inputs.get("approval_ref") or ""))}',
                'managed_by: "solar-autosci-research-wiki"',
                "---",
                "",
                f"# {target}",
                "",
                "## Scope",
                "",
                "Approved foundation scaffold created for AutoSci research memory.",
                "",
            ]
        )
        before = page.read_text(encoding="utf-8", errors="replace") if page.exists() else ""
        changed = _write_text_if_changed_bridge(page, body)
        after = page.read_text(encoding="utf-8", errors="replace")
        log_path = _write_generic_wiki_log(wiki_root, "Prefill Foundation", page, evidence_ids, "Created or refreshed approved foundation scaffold.")
        rebuilt = _rebuild_generic_wiki_views(wiki_root, str(envelope.get("sprint_id") or "sprint-autosci"), page, evidence_ids)
        return convert_research_memory_update({
            "changes": [
                {
                    "entity_type": "foundation",
                    "entity_id": f"foundation-{slug}",
                    "operation": "update" if before else "create",
                    "path": _rel(page),
                    "evidence_ids": evidence_ids,
                    "confidence": 0.82,
                    "summary": "Approved foundation page scaffold was written to the research wiki.",
                    "changed": changed,
                    "before_sha256": _hash_text(before),
                    "after_sha256": _hash_text(after),
                }
            ],
            "artifacts": [
                {"type": "wiki_foundation_page", "path": _rel(page)},
                {"type": "wiki_log", "path": _rel(log_path)},
                *[{"type": "wiki_rebuild", "path": _rel(path)} for path in rebuilt],
            ],
            "status": "completed",
            "limitations": [
                "Prefill mutation was applied only because approval_ref and execute_approved_side_effect were supplied.",
            ],
        }, envelope)
    return convert_research_memory_update({
        "changes": [
            {
                "entity_type": "foundation",
                "entity_id": f"foundation-{slug}",
                "operation": "propose",
                "path": f"knowledge/research/foundations/{slug}.md",
                "evidence_ids": [f"prefill:{slug}"],
                "confidence": 0.45,
                "summary": "Propose a foundation page scaffold; no wiki mutation is applied.",
            }
        ],
        "limitations": [
            "Prefill creates proposed memory-update evidence only; it does not create or modify wiki files.",
            "Deduplication is limited to the provided target text unless wiki source evidence is supplied.",
        ],
    }, envelope)


def _action_edit_wiki_plan(envelope: dict[str, Any]) -> dict[str, Any]:
    inputs = dict(envelope.get("inputs") or {})
    target = _memory_target(envelope, "wiki-edit")
    slug = _slug(target)
    evidence_ids = [f"edit-plan:{slug}"]
    after_artifacts = inputs.get("after_artifacts") if isinstance(inputs.get("after_artifacts"), list) else []
    if _local_mutation_requested(envelope) and after_artifacts:
        wiki_root = _wiki_roots_for_write(envelope)[0]
        rel_page = _wiki_page_rel_for_target(target, "outputs", "edit")
        page = wiki_root / rel_page
        if not _path_is_under(page, wiki_root):
            return convert_research_memory_update({
                "changes": [
                    {
                        "entity_type": "wiki_page",
                        "entity_id": f"wiki-edit-{slug}",
                        "operation": "blocked",
                        "path": str(rel_page),
                        "evidence_ids": evidence_ids,
                        "confidence": 0.0,
                        "summary": "Approved wiki edit was blocked because the target escapes the wiki root.",
                    }
                ],
                "status": "inconclusive",
                "limitations": ["Approved wiki edit target must resolve inside the configured wiki root."],
            }, envelope)
        after_path = _resolve_harness_path(str(after_artifacts[0]))
        if not after_path.exists() or after_path.is_dir():
            return convert_research_memory_update({
                "changes": [
                    {
                        "entity_type": "wiki_page",
                        "entity_id": f"wiki-edit-{slug}",
                        "operation": "blocked",
                        "path": _rel(page),
                        "evidence_ids": evidence_ids,
                        "confidence": 0.0,
                        "summary": "Approved wiki edit was blocked because after_artifact evidence is missing.",
                    }
                ],
                "status": "inconclusive",
                "limitations": ["Approved wiki edit requires an existing after_artifact file containing the desired page contents."],
            }, envelope)
        before = page.read_text(encoding="utf-8", errors="replace") if page.exists() else ""
        desired = after_path.read_text(encoding="utf-8", errors="replace")
        changed = _write_text_if_changed_bridge(page, desired)
        after = page.read_text(encoding="utf-8", errors="replace")
        log_path = _write_generic_wiki_log(wiki_root, "Approved Wiki Edit", page, evidence_ids, "Applied approved after_artifact contents to wiki page.")
        rebuilt = _rebuild_generic_wiki_views(wiki_root, str(envelope.get("sprint_id") or "sprint-autosci"), page, evidence_ids)
        return convert_research_memory_update({
            "changes": [
                {
                    "entity_type": "wiki_page",
                    "entity_id": f"wiki-edit-{slug}",
                    "operation": "update" if before else "create",
                    "path": _rel(page),
                    "evidence_ids": evidence_ids,
                    "confidence": 0.84,
                    "summary": "Approved wiki edit applied from after_artifact evidence.",
                    "changed": changed,
                    "before_sha256": _hash_text(before),
                    "after_sha256": _hash_text(after),
                    "after_artifact": _rel(after_path),
                }
            ],
            "artifacts": [
                {"type": "wiki_page", "path": _rel(page)},
                {"type": "wiki_log", "path": _rel(log_path)},
                *[{"type": "wiki_rebuild", "path": _rel(path)} for path in rebuilt],
            ],
            "status": "completed",
            "limitations": [
                "Wiki edit mutation was applied only because approval_ref, execute_approved_side_effect, and after_artifact evidence were supplied.",
            ],
        }, envelope)
    return convert_research_memory_update({
        "changes": [
            {
                "entity_type": "wiki_page",
                "entity_id": f"wiki-edit-{slug}",
                "operation": "propose",
                "path": f"knowledge/research/proposed-edits/{slug}.md",
                "evidence_ids": [f"edit-plan:{slug}"],
                "confidence": 0.35,
                "summary": "Propose a bounded wiki edit plan; no set-meta/add-edge mutation is applied.",
            }
        ],
        "limitations": [
            "Wiki edit is proposal-only without explicit approval.",
            "Before/after source mutation evidence is required before applying any wiki or raw-file edit.",
        ],
    }, envelope)


def _wiki_roots_for_read(envelope: dict[str, Any]) -> list[Path]:
    inputs = dict(envelope.get("inputs") or {})
    roots: list[Path] = []
    raw_root = str(inputs.get("wiki_root") or "").strip()
    if raw_root:
        path = Path(raw_root)
        roots.append(path if path.is_absolute() else HARNESS_DIR / path)
    roots.extend(
        [
            HARNESS_DIR / "artifacts" / "autosci" / "workspace" / "wiki",
            HARNESS_DIR / "wiki",
            REPO_HARNESS_DIR / "harness" / "artifacts" / "autosci" / "workspace" / "wiki",
        ]
    )
    seen: set[Path] = set()
    out: list[Path] = []
    for root in roots:
        try:
            resolved = root.resolve()
        except OSError:
            continue
        if resolved in seen:
            continue
        seen.add(resolved)
        out.append(root)
    return out


def _query_terms(query: str) -> list[str]:
    stop = {"a", "an", "and", "are", "for", "how", "in", "is", "of", "on", "or", "the", "to", "what"}
    terms = [term for term in re.findall(r"[a-z0-9][a-z0-9_-]+", query.lower()) if term not in stop]
    return _unique_strings(terms)[:12]


def _wiki_retrieval_hits(envelope: dict[str, Any], query: str, *, limit: int = 5) -> list[dict[str, Any]]:
    terms = _query_terms(query)
    if not terms:
        return []
    hits: list[dict[str, Any]] = []
    for root in _wiki_roots_for_read(envelope):
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.md"), key=lambda item: str(item)):
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            lowered = text.lower()
            score = sum(lowered.count(term) for term in terms)
            if score <= 0:
                continue
            lines = [
                line.strip()
                for line in text.splitlines()
                if line.strip()
                and line.strip() != "---"
                and not re.match(r"^[a-zA-Z_ -]{1,32}:\s", line.strip())
            ]
            ranked_lines = sorted(
                (
                    (sum(line.lower().count(term) for term in terms), line)
                    for line in lines
                    if any(term in line.lower() for term in terms)
                ),
                key=lambda item: (-item[0], len(item[1])),
            )
            snippet = ranked_lines[0][1] if ranked_lines else (lines[0] if lines else "")
            hits.append(
                {
                    "path": _rel(path),
                    "score": score,
                    "matched_terms": [term for term in terms if term in lowered],
                    "snippet": snippet[:300],
                }
            )
    hits.sort(key=lambda item: (-int(item["score"]), str(item["path"])))
    return hits[:limit]


def _wiki_frontmatter_value(raw: str) -> Any:
    value = raw.strip()
    if not value:
        return ""
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_wiki_frontmatter_value(item) for item in inner.split(",")]
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"null", "none"}:
        return None
    try:
        if re.fullmatch(r"-?\d+", value):
            return int(value)
        if re.fullmatch(r"-?\d+\.\d+", value):
            return float(value)
    except ValueError:
        pass
    return value.strip("\"'")


def _wiki_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end < 0:
        return {}, text
    values: dict[str, Any] = {}
    current_list_key = ""
    for raw_line in text[3:end].splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- ") and current_list_key:
            current = values.setdefault(current_list_key, [])
            if not isinstance(current, list):
                current = [current]
                values[current_list_key] = current
            current.append(_wiki_frontmatter_value(stripped[2:]))
            continue
        if ":" not in line:
            current_list_key = ""
            continue
        key, raw_value = line.split(":", 1)
        key = key.strip()
        if not key:
            current_list_key = ""
            continue
        if raw_value.strip():
            values[key] = _wiki_frontmatter_value(raw_value)
            current_list_key = ""
        else:
            values[key] = []
            current_list_key = key
    return values, text[end + len("\n---") :]


def _wiki_title(path: Path, text: str, frontmatter: dict[str, Any]) -> str:
    title = str(frontmatter.get("title") or "").strip()
    if title:
        return title
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem.replace("-", " ").replace("_", " ").title()


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        raw_items = value
    elif isinstance(value, tuple):
        raw_items = list(value)
    elif isinstance(value, str) and "," in value:
        raw_items = value.split(",")
    else:
        raw_items = [value]
    out: list[str] = []
    for item in raw_items:
        text = str(item).strip().strip("\"'")
        if text:
            out.append(text)
    return _unique_strings(out)


def _first_string_list(frontmatter: dict[str, Any], keys: tuple[str, ...]) -> list[str]:
    for key in keys:
        values = _string_list(frontmatter.get(key))
        if values:
            return values
    return []


def _optional_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _resolve_wiki_link(root: Path, source_path: Path, raw_path: str) -> tuple[str, bool]:
    raw_path = raw_path.strip()
    if not raw_path:
        return "", False
    path = Path(raw_path)
    candidates = [path] if path.is_absolute() else [source_path.parent / path, root / path]
    for candidate in candidates:
        if candidate.exists():
            return _rel(candidate), True
    fallback = candidates[0]
    return _rel(fallback), False


def _read_wiki_markdown(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _wiki_entity_common(root: Path, group: str, path: Path, text: str, frontmatter: dict[str, Any]) -> dict[str, Any]:
    raw_slug = str(frontmatter.get("slug") or path.stem).strip()
    slug = _slug(raw_slug)
    entity_id = str(frontmatter.get(f"{group[:-1]}_id") or frontmatter.get("id") or frontmatter.get("slug") or slug)
    return {
        "id": entity_id,
        "slug": slug,
        "title": _wiki_title(path, text, frontmatter),
        "status": str(frontmatter.get("status") or frontmatter.get("state") or "unknown"),
        "path": _rel(path),
        "frontmatter_keys": sorted(str(key) for key in frontmatter),
    }


def _wiki_markdown_entities(root: Path, group: str) -> list[dict[str, Any]]:
    directory = root / group
    if not directory.exists():
        return []
    entities: list[dict[str, Any]] = []
    for path in sorted(directory.rglob("*.md"), key=lambda item: str(item)):
        text = _read_wiki_markdown(path)
        if not text:
            continue
        frontmatter, body = _wiki_frontmatter(text)
        entity = _wiki_entity_common(root, group, path, body or text, frontmatter)
        if group == "ideas":
            entity["idea_id"] = str(frontmatter.get("idea_id") or entity["id"])
            novelty_score = _optional_float(frontmatter.get("novelty_score"))
            entity["novelty_score"] = novelty_score if novelty_score is not None else "N/A"
            entity["has_novelty_score"] = novelty_score is not None
            entity["linked_experiments"] = _first_string_list(
                frontmatter,
                ("linked_experiments", "experiments", "experiment_ids"),
            )
            if frontmatter.get("failure_reason"):
                entity["failure_reason"] = str(frontmatter.get("failure_reason"))
        elif group == "experiments":
            entity["experiment_id"] = str(frontmatter.get("experiment_id") or entity["id"])
            entity["idea_id"] = str(frontmatter.get("idea_id") or "")
            entity["linked_outputs"] = _first_string_list(frontmatter, ("linked_outputs", "outputs", "output_ids"))
            entity["pipeline"] = str(frontmatter.get("pipeline") or frontmatter.get("pipeline_id") or "")
            aliases = _first_string_list(frontmatter, ("aliases", "pipeline_aliases", "pipelines"))
            if entity["pipeline"]:
                aliases.append(str(entity["pipeline"]))
            entity["aliases"] = _unique_strings(aliases)
            entity["outcome"] = str(frontmatter.get("outcome") or frontmatter.get("result") or "")
            entity["evidence_ids"] = _first_string_list(
                frontmatter,
                ("evidence_ids", "result_evidence_ids", "runtime_evidence_ids"),
            )
            run_log = str(frontmatter.get("run_log") or frontmatter.get("run_log_path") or "").strip()
            entity["run_log"] = run_log
            if run_log:
                resolved, exists = _resolve_wiki_link(root, path, run_log)
                entity["run_log_path"] = resolved
                entity["run_log_exists"] = exists
            else:
                entity["run_log_path"] = ""
                entity["run_log_exists"] = False
            if frontmatter.get("env"):
                entity["env"] = str(frontmatter.get("env"))
        elif group == "outputs":
            entity["output_id"] = str(frontmatter.get("output_id") or entity["id"])
            entity["experiment_id"] = str(frontmatter.get("experiment_id") or "")
            entity["idea_id"] = str(frontmatter.get("idea_id") or "")
            entity["artifact_type"] = str(frontmatter.get("artifact_type") or frontmatter.get("type") or "")
        entities.append(entity)
    return entities


def _wiki_graph_edges(root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    edges_path = root / "graph" / "edges.jsonl"
    edges: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    if not edges_path.exists():
        return edges, errors
    try:
        lines = edges_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        return edges, [{"path": _rel(edges_path), "line": 0, "error": str(exc)}]
    for index, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError as exc:
            errors.append({"path": _rel(edges_path), "line": index, "error": str(exc)})
            continue
        if not isinstance(payload, dict):
            errors.append({"path": _rel(edges_path), "line": index, "error": "edge row is not an object"})
            continue
        source = str(payload.get("source") or payload.get("from") or payload.get("src") or "").strip()
        target = str(payload.get("target") or payload.get("to") or payload.get("dst") or "").strip()
        relation = str(payload.get("relation") or payload.get("type") or payload.get("label") or "").strip()
        edges.append(
            {
                "source": source,
                "target": target,
                "relation": relation or "related_to",
                "status": str(payload.get("status") or ""),
                "evidence_ids": _string_list(payload.get("evidence_ids") or payload.get("evidence_id")),
                "path": _rel(edges_path),
                "line": index,
            }
        )
    return edges, errors


def _wiki_entity_aliases(entity: dict[str, Any], id_keys: tuple[str, ...]) -> set[str]:
    aliases: set[str] = set()
    for key in ("id", "slug", "title", "path", "pipeline", *id_keys):
        value = str(entity.get(key) or "").strip()
        if not value:
            continue
        aliases.add(value.lower())
        aliases.add(_slug(value))
        if "/" in value:
            aliases.add(Path(value).stem.lower())
            aliases.add(_slug(Path(value).stem))
    for value in _string_list(entity.get("aliases")):
        aliases.add(value.lower())
        aliases.add(_slug(value))
    return {alias for alias in aliases if alias}


def _target_matches_entity(target: str, entity: dict[str, Any], id_keys: tuple[str, ...]) -> bool:
    if not target:
        return False
    aliases = _wiki_entity_aliases(entity, id_keys)
    return target.lower() in aliases or _slug(target) in aliases


def _edge_links(edge: dict[str, Any], left_aliases: set[str], right_aliases: set[str]) -> bool:
    source = str(edge.get("source") or "").lower()
    target = str(edge.get("target") or "").lower()
    return (source in left_aliases and target in right_aliases) or (source in right_aliases and target in left_aliases)


def _enrich_wiki_entities(
    ideas: list[dict[str, Any]],
    experiments: list[dict[str, Any]],
    outputs: list[dict[str, Any]],
    edges: list[dict[str, Any]],
) -> None:
    experiment_aliases = {
        str(experiment.get("experiment_id") or experiment.get("id")): _wiki_entity_aliases(experiment, ("experiment_id",))
        for experiment in experiments
    }
    output_aliases = {
        str(output.get("output_id") or output.get("id")): _wiki_entity_aliases(output, ("output_id",))
        for output in outputs
    }
    for idea in ideas:
        idea_aliases = _wiki_entity_aliases(idea, ("idea_id",))
        linked = list(idea.get("linked_experiments") or [])
        edge_count = 0
        for edge in edges:
            if str(edge.get("source") or "").lower() in idea_aliases or str(edge.get("target") or "").lower() in idea_aliases:
                edge_count += 1
            for experiment_id, aliases in experiment_aliases.items():
                if _edge_links(edge, idea_aliases, aliases):
                    linked.append(experiment_id)
        idea["linked_experiments"] = _unique_strings(str(item) for item in linked if str(item).strip())
        idea["graph_edge_count"] = edge_count
    for experiment in experiments:
        experiment_aliases_for_entity = _wiki_entity_aliases(experiment, ("experiment_id",))
        linked_outputs = list(experiment.get("linked_outputs") or [])
        edge_count = 0
        for edge in edges:
            if str(edge.get("source") or "").lower() in experiment_aliases_for_entity or str(edge.get("target") or "").lower() in experiment_aliases_for_entity:
                edge_count += 1
            for output_id, aliases in output_aliases.items():
                if _edge_links(edge, experiment_aliases_for_entity, aliases):
                    linked_outputs.append(output_id)
        experiment["linked_outputs"] = _unique_strings(str(item) for item in linked_outputs if str(item).strip())
        experiment["graph_edge_count"] = edge_count


def _resolve_wiki_state_target(
    envelope: dict[str, Any],
    ideas: list[dict[str, Any]],
    experiments: list[dict[str, Any]],
    outputs: list[dict[str, Any]],
    *,
    action: str,
) -> dict[str, Any]:
    inputs = dict(envelope.get("inputs") or {})
    target = str(
        inputs.get("experiment_id")
        or inputs.get("idea_id")
        or inputs.get("target")
        or inputs.get("topic")
        or inputs.get("query")
        or ""
    ).strip()
    preferred = ["idea", "experiment", "output"]
    if action in {"monitor_experiment", "run_experiment"} or inputs.get("experiment_id"):
        preferred = ["experiment", "idea", "output"]
    elif action in {"design_experiment", "generate_ideas", "evaluate_ideas"} or inputs.get("idea_id"):
        preferred = ["idea", "experiment", "output"]
    groups = {
        "idea": (ideas, ("idea_id",)),
        "experiment": (experiments, ("experiment_id",)),
        "output": (outputs, ("output_id",)),
    }
    if target:
        for kind in preferred:
            entities, id_keys = groups[kind]
            for entity in entities:
                if _target_matches_entity(target, entity, id_keys):
                    return {
                        "target": target,
                        "target_type": kind,
                        "target_id": str(entity.get(id_keys[0]) or entity.get("id") or entity.get("slug")),
                        "target_path": str(entity.get("path") or ""),
                        "fallback_used": False,
                        "warnings": [],
                    }
        return {
            "target": target,
            "target_type": "unresolved",
            "target_id": "",
            "target_path": "",
            "fallback_used": False,
            "warnings": [f"Target `{target}` was not found in wiki ideas, experiments, outputs, or graph edges."],
        }
    return {
        "target": "N/A",
        "target_type": "unresolved",
        "target_id": "",
        "target_path": "",
        "fallback_used": False,
        "warnings": ["No explicit target, topic, idea_id, or experiment_id was supplied for wiki state resolution."],
    }


def _wiki_state_resolver(envelope: dict[str, Any], *, action: str) -> dict[str, Any]:
    roots = _wiki_roots_for_read(envelope)
    existing_roots = [root for root in roots if root.exists()]
    ideas: list[dict[str, Any]] = []
    experiments: list[dict[str, Any]] = []
    outputs: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    graph_errors: list[dict[str, Any]] = []
    for root in existing_roots:
        ideas.extend(_wiki_markdown_entities(root, "ideas"))
        experiments.extend(_wiki_markdown_entities(root, "experiments"))
        outputs.extend(_wiki_markdown_entities(root, "outputs"))
        root_edges, root_errors = _wiki_graph_edges(root)
        edges.extend(root_edges)
        graph_errors.extend(root_errors)
    _enrich_wiki_entities(ideas, experiments, outputs, edges)
    resolution = _resolve_wiki_state_target(envelope, ideas, experiments, outputs, action=action)
    status = "completed" if any((ideas, experiments, outputs, edges)) else ("inconclusive" if existing_roots else "missing")
    limitations = [
        "Resolver is read-only; it does not mutate wiki state, add graph edges, or rebuild wiki indexes.",
        "Frontmatter parsing supports scalar values and simple lists only; complex YAML is reported through missing fields.",
    ]
    if not existing_roots:
        limitations.append("No wiki root exists for state resolution.")
    if graph_errors:
        limitations.append("Some graph edge rows could not be parsed.")
    return {
        "schema": "autosci_wiki_state_resolver.v1",
        "status": status,
        "action": action,
        "wiki_roots": [_rel(root) for root in roots],
        "existing_wiki_roots": [_rel(root) for root in existing_roots],
        "selected_root": _rel(existing_roots[0]) if existing_roots else "N/A",
        "ideas": ideas,
        "experiments": experiments,
        "outputs": outputs,
        "graph_edges": edges,
        "graph_errors": graph_errors,
        "indexes": {
            "ideas_by_slug": {str(idea.get("slug")): str(idea.get("idea_id") or idea.get("id")) for idea in ideas},
            "experiments_by_slug": {
                str(experiment.get("slug")): str(experiment.get("experiment_id") or experiment.get("id"))
                for experiment in experiments
            },
            "outputs_by_slug": {str(output.get("slug")): str(output.get("output_id") or output.get("id")) for output in outputs},
        },
        "resolution": resolution,
        "limitations": limitations,
    }


def _should_resolve_wiki_state(envelope: dict[str, Any]) -> bool:
    if _fixture_like_envelope(envelope):
        return False
    inputs = dict(envelope.get("inputs") or {})
    return any(
        bool(inputs.get(key))
        for key in ("wiki_root", "from_wiki", "target", "topic", "query", "idea_id", "experiment_id")
    )


def _wiki_state_resolver_artifact(envelope: dict[str, Any], action: str) -> tuple[dict[str, Any] | None, dict[str, str] | None]:
    if not _should_resolve_wiki_state(envelope):
        return None, None
    resolver = _wiki_state_resolver(envelope, action=action)
    output_dir = _output_dir(envelope, action)
    path = _configured_output_path(envelope, "wiki_state_resolver_path", output_dir / "wiki_state_resolver.json")
    artifact = {"type": "wiki_state_resolver_json", "path": _write_json_sidecar(path, resolver)}
    return resolver, artifact


def _wiki_state_limitations(resolver: dict[str, Any] | None) -> list[str]:
    if not resolver:
        return []
    resolution = resolver.get("resolution") if isinstance(resolver.get("resolution"), dict) else {}
    warnings = [str(item) for item in resolution.get("warnings") or [] if str(item).strip()]
    limitations = [str(item) for item in resolver.get("limitations") or [] if str(item).strip()]
    return [*warnings, *limitations]


def _target_idea_from_wiki_state(resolver: dict[str, Any] | None) -> dict[str, Any] | None:
    if not resolver:
        return None
    resolution = resolver.get("resolution") if isinstance(resolver.get("resolution"), dict) else {}
    if resolution.get("target_type") != "idea":
        return None
    target_id = str(resolution.get("target_id") or "")
    target_path = str(resolution.get("target_path") or "")
    for idea in resolver.get("ideas") or []:
        if not isinstance(idea, dict):
            continue
        if target_id not in {str(idea.get("idea_id") or ""), str(idea.get("id") or ""), str(idea.get("slug") or "")} and target_path != str(idea.get("path") or ""):
            continue
        idea_id = str(idea.get("idea_id") or idea.get("id") or idea.get("slug") or "idea-wiki-target")
        return {
            "idea_id": idea_id,
            "title": str(idea.get("title") or idea_id),
            "hypothesis": f"Wiki idea `{idea_id}` should be evaluated against current source evidence.",
            "approach": "Use the resolved wiki idea state, linked experiments, graph edges, and external novelty evidence before promotion.",
            "origin_evidence_ids": [str(idea.get("path") or idea_id)],
            "novelty_hypothesis": "Novelty must be established from external source evidence and Review LLM evidence.",
            "source_mode": "wiki_state",
            "generation_path": "wiki-state-resolver",
            "duplicate_status": "unknown",
            "status": str(idea.get("status") or "candidate"),
            "wiki_state": {
                "path": str(idea.get("path") or ""),
                "slug": str(idea.get("slug") or ""),
                "novelty_score": idea.get("novelty_score", "N/A"),
                "linked_experiments": list(idea.get("linked_experiments") or []),
            },
        }
    return None


def _resolved_wiki_experiment(resolver: dict[str, Any] | None) -> dict[str, Any] | None:
    if not resolver:
        return None
    resolution = resolver.get("resolution") if isinstance(resolver.get("resolution"), dict) else {}
    if resolution.get("target_type") != "experiment":
        return None
    target_id = str(resolution.get("target_id") or "").strip()
    target_path = str(resolution.get("target_path") or "").strip()
    for experiment in resolver.get("experiments") or []:
        if not isinstance(experiment, dict):
            continue
        ids = {
            str(experiment.get("experiment_id") or ""),
            str(experiment.get("id") or ""),
            str(experiment.get("slug") or ""),
        }
        if target_id and target_id in ids:
            return experiment
        if target_path and target_path == str(experiment.get("path") or ""):
            return experiment
    return None


def _resolved_wiki_experiment_id(resolver: dict[str, Any] | None) -> str:
    experiment = _resolved_wiki_experiment(resolver)
    if not experiment:
        return ""
    return str(experiment.get("experiment_id") or experiment.get("id") or "").strip()


def _experiment_state_from_wiki_status(raw_status: str) -> str:
    normalized = _slug(raw_status)
    if normalized in {"completed", "complete", "done", "passed", "success", "succeeded"}:
        return "completed"
    if normalized in {"failed", "failure", "error", "errored"}:
        return "failed"
    if normalized in {"running", "active", "launched", "queued", "in-progress", "in-progress"}:
        return "running"
    if normalized in {"blocked", "paused", "gated", "waiting", "needs-approval"}:
        return "blocked"
    return "unknown"


def _model_command(inputs: dict[str, Any]) -> list[str]:
    raw = inputs.get("model_command") or os.environ.get("AUTOSCI_MODEL_COMMAND", "")
    if isinstance(raw, list):
        return [str(item) for item in raw if str(item).strip()]
    raw_text = str(raw).strip()
    return shlex.split(raw_text) if raw_text else []


def _normalize_model_response(payload: dict[str, Any], source: str) -> dict[str, Any]:
    outputs = payload.get("outputs") if isinstance(payload.get("outputs"), dict) else {}
    answer = str(outputs.get("answer") or outputs.get("summary") or payload.get("answer") or payload.get("summary") or "").strip()
    ideas_raw = outputs.get("ideas") if isinstance(outputs.get("ideas"), list) else payload.get("ideas")
    ideas = ideas_raw if isinstance(ideas_raw, list) else []
    evidence_ids_raw = outputs.get("evidence_ids") or payload.get("evidence_ids") or []
    evidence_ids = [str(item) for item in (evidence_ids_raw if isinstance(evidence_ids_raw, list) else [evidence_ids_raw]) if str(item).strip()]
    findings_raw = outputs.get("findings") if isinstance(outputs.get("findings"), list) else payload.get("findings")
    findings = findings_raw if isinstance(findings_raw, list) else []
    try:
        confidence = float(outputs.get("confidence", payload.get("confidence", 0.0)))
    except (TypeError, ValueError):
        confidence = 0.0
    confidence = round(max(0.0, min(confidence, 1.0)), 3)
    status = str(payload.get("status") or "completed")
    if status not in {"completed", "inconclusive"}:
        return {"status": "invalid", "source": source, "reason": f"model response status is not completed/inconclusive: {status}"}
    if status == "completed" and ((not answer and not ideas) or not evidence_ids):
        return {
            "status": "invalid",
            "source": source,
            "reason": "completed model response requires answer/summary or ideas plus evidence_ids.",
        }
    return {
        "status": status,
        "source": source,
        "answer": answer,
        "ideas": ideas,
        "confidence": confidence,
        "evidence_ids": evidence_ids,
        "findings": findings,
        "model": str(outputs.get("model") or payload.get("model") or ""),
        "provider": str(outputs.get("provider") or payload.get("provider") or ""),
    }


def _model_output(
    envelope: dict[str, Any],
    *,
    action: str,
    prompt: str,
    context: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, str]]]:
    inputs = dict(envelope.get("inputs") or {})
    artifacts: list[dict[str, str]] = []
    paths = _input_path_values(inputs, "model_evidence", "model_output_evidence")
    checked: list[str] = []
    for raw in paths:
        path = _resolve_harness_path(raw)
        checked.append(_rel(path))
        payload = _load_optional_evidence(raw)
        if not payload:
            continue
        artifacts.append({"type": "model_output_evidence_json", "path": _rel(path)})
        normalized = _normalize_model_response(payload, _rel(path))
        normalized["checked_paths"] = checked
        if normalized.get("status") in {"completed", "inconclusive"}:
            return normalized, artifacts
    command = _model_command(inputs)
    if not command:
        return {
            "status": "unavailable",
            "reason": "No model evidence or model command was supplied.",
            "checked_paths": checked,
        }, artifacts
    request = {
        "schema": "autosci_model_request.v1",
        "action": action,
        "prompt": prompt,
        "context": context,
        "required_response_schema": {
            "schema": "autosci_model_response.v1",
            "status": "completed",
            "outputs": {
                "answer": "source-grounded answer or assessment",
                "confidence": "number between 0 and 1",
                "evidence_ids": ["source id used by the answer"],
                "findings": [],
                "ideas": [],
            },
        },
    }
    timeout = int(os.environ.get("AUTOSCI_MODEL_COMMAND_TIMEOUT", "60"))
    try:
        proc = subprocess.run(
            command,
            input=json.dumps(request, sort_keys=True),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"status": "failed", "reason": f"model command invocation failed: {exc}", "command": command, "checked_paths": checked}, artifacts
    output_dir = _output_dir(envelope, action)
    stdout_path = output_dir / f"{action}_model_stdout.json"
    stderr_path = output_dir / f"{action}_model_stderr.txt"
    stdout_rel = _write_text_sidecar(stdout_path, proc.stdout)
    stderr_rel = _write_text_sidecar(stderr_path, proc.stderr)
    artifacts.extend([
        {"type": "model_command_stdout_json", "path": stdout_rel},
        {"type": "model_command_stderr", "path": stderr_rel},
    ])
    if proc.returncode != 0:
        return {
            "status": "failed",
            "reason": f"model command exited {proc.returncode}: {proc.stderr.strip()[:500]}",
            "command": command,
            "checked_paths": checked,
        }, artifacts
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        return {"status": "invalid", "reason": f"model command returned invalid JSON: {exc}", "command": command, "checked_paths": checked}, artifacts
    if not isinstance(payload, dict):
        return {"status": "invalid", "reason": "model command must return a JSON object.", "command": command, "checked_paths": checked}, artifacts
    normalized = _normalize_model_response(payload, "model-command")
    normalized["invocation_mode"] = "command"
    normalized["command"] = command
    normalized["checked_paths"] = checked
    return normalized, artifacts


def _model_output_requested(envelope: dict[str, Any]) -> bool:
    inputs = dict(envelope.get("inputs") or {})
    return bool(_input_path_values(inputs, "model_evidence", "model_output_evidence") or _model_command(inputs))


def _idea_candidates_from_model_output(
    model: dict[str, Any],
    *,
    source_mode: str,
) -> tuple[list[dict[str, Any]], list[str]]:
    raw_ideas = model.get("ideas") if isinstance(model.get("ideas"), list) else []
    model_evidence_ids = [str(item) for item in model.get("evidence_ids") or [] if str(item).strip()]
    ideas: list[dict[str, Any]] = []
    skipped: list[str] = []
    normalized_source_mode = source_mode if source_mode and source_mode != "missing" else "external"
    for index, item in enumerate(raw_ideas, start=1):
        if not isinstance(item, dict):
            skipped.append(f"ideas[{index}] is not an object")
            continue
        title = str(item.get("title") or "").strip()
        hypothesis = str(item.get("hypothesis") or "").strip()
        approach = str(item.get("approach") or "").strip()
        if not (title and hypothesis and approach):
            skipped.append(f"ideas[{index}] missing title, hypothesis, or approach")
            continue
        origin_evidence_ids = _unique_strings(
            [
                *[str(value) for value in item.get("origin_evidence_ids") or [] if str(value).strip()],
                *model_evidence_ids,
            ]
        )
        if not origin_evidence_ids:
            skipped.append(f"ideas[{index}] missing origin evidence ids")
            continue
        ideas.append(
            {
                "idea_id": str(item.get("idea_id") or f"idea-model-{index:03d}"),
                "title": title,
                "hypothesis": hypothesis,
                "approach": approach,
                "origin_evidence_ids": origin_evidence_ids,
                "novelty_hypothesis": str(
                    item.get("novelty_hypothesis")
                    or item.get("rationale")
                    or "Novelty must be validated by external source evidence and Review LLM evidence."
                ),
                "grounding_summary": str(
                    item.get("grounding_summary")
                    or model.get("answer")
                    or "Model-supplied brainstorm grounded in explicit model evidence."
                )[:600],
                "source_mode": str(item.get("source_mode") or normalized_source_mode),
                "generation_path": str(item.get("generation_path") or f"model-{model.get('invocation_mode') or 'evidence'}"),
                "duplicate_status": str(item.get("duplicate_status") or "unknown"),
                "status": str(item.get("status") or "candidate"),
                "model": str(model.get("model") or ""),
                "provider": str(model.get("provider") or ""),
            }
        )
    return ideas, skipped


def _action_ask_wiki(envelope: dict[str, Any]) -> dict[str, Any]:
    inputs = dict(envelope.get("inputs") or {})
    query = str(inputs.get("query") or inputs.get("target") or inputs.get("topic") or "N/A")
    output_dir = _output_dir(envelope, "ask_wiki")
    answer_path = _configured_output_path(envelope, "answer_markdown_path", output_dir / "ask_wiki_answer.md")
    retrieval_path = _configured_output_path(envelope, "retrieval_json_path", output_dir / "ask_wiki_retrieval.json")
    hits = _wiki_retrieval_hits(envelope, query, limit=int(inputs.get("limit") or 5))
    source_lines = [f"- `{hit['path']}` score={hit['score']}: {hit['snippet']}" for hit in hits] or ["- N/A"]
    answer_lines = [
        f"- {hit['snippet']} Source: `{hit['path']}`."
        for hit in hits
        if str(hit.get("snippet") or "").strip()
    ]
    model_output, model_artifacts = _model_output(
        envelope,
        action="ask_wiki",
        prompt=query,
        context={"query": query, "retrieval_hits": hits},
    )
    model_completed = model_output.get("status") == "completed"
    answer_status = "completed" if answer_lines or model_completed else "inconclusive"
    model_section = [
        "## Model Synthesis",
        "",
        model_output.get("answer", "N/A") if model_completed else f"Model evidence status: `{model_output.get('status')}`.",
        "",
    ]
    body = "\n".join(
        [
            "# AutoSci Ask Wiki",
            "",
            f"Query: `{query}`",
            "",
            "## Retrieval Sources",
            "",
            *source_lines,
            "",
            "## Answer",
            "",
            *(answer_lines or [
                "No source-grounded wiki answer could be generated because no matching wiki sources were retrieved."
            ]),
            "",
            *model_section,
            "## Confidence",
            "",
            f"- Retrieval-backed extractive answer: `{answer_status}`",
            f"- Source count: `{len(hits)}`",
            f"- Model evidence status: `{model_output.get('status')}`",
            "",
        ]
    )
    answer_artifact = _write_text_sidecar(answer_path, body)
    retrieval_artifact = _write_json_sidecar(
        retrieval_path,
        {
            "query": query,
            "status": "completed" if hits else "missing",
            "hits": hits,
            "answer_status": answer_status,
            "answer_lines": answer_lines,
            "model_output": model_output,
            "limitations": [
                "Extractive answer is grounded in retrieved wiki snippets.",
                "Model synthesis is included only when explicit model evidence or a model command was supplied.",
            ],
        },
    )
    slug = _slug(query)
    evidence_ids = _unique_strings([f"ask:{slug}", *[str(hit["path"]) for hit in hits], *[str(item) for item in model_output.get("evidence_ids") or []]])
    return convert_research_memory_update({
        "changes": [
            {
                "entity_type": "ask_query",
                "entity_id": f"ask-{slug}",
                "operation": "no_op",
                "path": f"knowledge/research/queries/{slug}.md",
                "evidence_ids": evidence_ids,
                "confidence": max(0.75 if hits else 0.0, float(model_output.get("confidence") or 0.0) if model_completed else 0.0),
                "summary": (
                    "Source-grounded answer generated from retrieved wiki snippets and explicit model evidence."
                    if model_completed
                    else (
                        "Source-grounded extractive answer generated from retrieved wiki snippets."
                        if hits
                        else "Ask query captured, but no matching wiki evidence was retrieved."
                    )
                ),
            }
        ],
        "artifacts": [
            {"type": "ask_answer_markdown", "path": answer_artifact},
            {"type": "ask_retrieval_json", "path": retrieval_artifact},
            *model_artifacts,
        ],
        "status": "completed" if hits else "inconclusive",
        "limitations": [
            "Ask wiki answer is limited to local retrieved wiki snippets plus explicit model evidence when supplied.",
            "Use human review before treating the answer as final for publication.",
        ],
    }, envelope)


def _source_fan_in_path(envelope: dict[str, Any], action: str) -> Path:
    return _output_dir(envelope, action) / "source_fan_in_writeback.json"


def _source_candidate_page_path(root: Path, candidate: dict[str, Any], index: int, seen_slugs: set[str]) -> Path:
    raw_slug = str(candidate.get("candidate_id") or candidate.get("title") or f"source-candidate-{index:03d}")
    slug = _slug(raw_slug)
    if slug in {"runtime-candidate", "runtime-candidate-001", "candidate", "paper"}:
        slug = _slug(str(candidate.get("title") or raw_slug))
    base = slug or f"source-candidate-{index:03d}"
    suffix = 1
    while slug in seen_slugs:
        suffix += 1
        slug = f"{base}-{suffix}"
    seen_slugs.add(slug)
    return root / "papers" / f"{slug}.md"


def _frontmatter_string(value: Any) -> str:
    return json.dumps(str(value), ensure_ascii=True)


def _source_candidate_page_body(
    candidate: dict[str, Any],
    *,
    action: str,
    query: str,
    evidence_ids: list[str],
) -> str:
    title = str(candidate.get("title") or "Untitled Source Candidate").strip() or "Untitled Source Candidate"
    candidate_id = str(candidate.get("candidate_id") or _slug(title))
    source_ref = str(candidate.get("source_ref") or "N/A")
    channels = [str(item) for item in candidate.get("source_channels") or [] if str(item).strip()]
    abstract = str(candidate.get("abstract") or "N/A").strip() or "N/A"
    rationale = str(candidate.get("ranking_rationale") or "N/A").strip() or "N/A"
    frontmatter = [
        "---",
        f"title: {_frontmatter_string(title)}",
        f"candidate_id: {_frontmatter_string(candidate_id)}",
        f"source_ref: {_frontmatter_string(source_ref)}",
        f"autosci_source_action: {_frontmatter_string(action)}",
        f"query: {_frontmatter_string(query)}",
        f"fetch_status: {_frontmatter_string(candidate.get('fetch_status') or 'unknown')}",
        f"dedup_status: {_frontmatter_string(candidate.get('dedup_status') or 'unknown')}",
        f"ranking_score: {float(candidate.get('ranking_score') or 0.0):.6g}",
        "source_channels:",
        *[f"  - {_frontmatter_string(channel)}" for channel in (channels or ["approved_runtime"])],
        "evidence_ids:",
        *[f"  - {_frontmatter_string(evidence_id)}" for evidence_id in (evidence_ids or [candidate_id])],
        "status: discovered",
        f"discovered_at: {_frontmatter_string(datetime.now(UTC).replace(microsecond=0).isoformat().replace('+00:00', 'Z'))}",
        "---",
        "",
    ]
    return "\n".join(
        [
            *frontmatter,
            f"# {title}",
            "",
            "## Abstract",
            "",
            abstract,
            "",
            "## Source",
            "",
            f"- Reference: `{source_ref}`",
            f"- Channels: {', '.join(channels) if channels else 'approved_runtime'}",
            f"- Ranking rationale: {rationale}",
            "",
        ]
    )


def _append_source_fan_in_edge(
    root: Path,
    page_path: Path,
    candidate: dict[str, Any],
    *,
    action: str,
    evidence_ids: list[str],
) -> Path:
    edges_path = root / "graph" / "edges.jsonl"
    edges_path.parent.mkdir(parents=True, exist_ok=True)
    edge = {
        "edge_type": "source_candidate_ingested",
        "source_type": "runtime_source_manifest",
        "source_id": action,
        "relation": "discovered",
        "target_type": "paper",
        "target_id": str(candidate.get("candidate_id") or page_path.stem),
        "target_path": _rel(page_path),
        "source_ref": str(candidate.get("source_ref") or "N/A"),
        "evidence_ids": evidence_ids,
        "timestamp": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }
    line = json.dumps(edge, sort_keys=True)
    existing = set(edges_path.read_text(encoding="utf-8").splitlines()) if edges_path.exists() else set()
    if line not in existing:
        edges_path.open("a", encoding="utf-8").write(line + "\n")
    return edges_path


def _source_candidate_wiki_fan_in(
    envelope: dict[str, Any],
    *,
    action: str,
    query: str,
    candidates: list[dict[str, Any]],
    semantic: dict[str, Any],
    contract: dict[str, Any],
) -> dict[str, Any]:
    inputs = dict(envelope.get("inputs") or {})
    native_options = inputs.get("native_options") if isinstance(inputs.get("native_options"), dict) else {}
    requested = bool(native_options.get("write"))
    summary: dict[str, Any] = {
        "requested": requested,
        "status": "not_requested",
        "applied": False,
        "candidate_count": len(candidates),
        "written_count": 0,
    }
    if not requested:
        return {"summary": summary, "artifact": None, "limitations": [], "artifacts": []}

    status = "inconclusive"
    artifacts: list[dict[str, Any]] = []
    limitations: list[str] = []
    evidence_ids = _unique_strings(
        [str(item) for item in ((semantic.get("detail") or {}).get("evidence_ids") or []) if str(item).strip()]
    )
    write: dict[str, Any] = {
        **summary,
        "approval_ref": str(contract.get("approval_ref") or "N/A"),
        "approval_state": str(contract.get("approval_state") or "unknown"),
        "semantic_runtime_status": str(semantic.get("status") or "unknown"),
        "written_pages": [],
    }

    if not contract.get("execution_verified"):
        limitations.append("Source fan-in write-back requires verified approval, allowlist, runtime, before, and after artifacts.")
    elif not semantic.get("verified"):
        limitations.append("Source fan-in write-back requires verified runtime source candidates.")
    elif not candidates:
        limitations.append("Source fan-in write-back requires at least one runtime source candidate.")
    else:
        wiki_root = _wiki_roots_for_write(envelope)[0]
        seen_slugs: set[str] = set()
        written_pages: list[str] = []
        edge_paths: list[Path] = []
        for index, candidate in enumerate(candidates, start=1):
            if not isinstance(candidate, dict):
                continue
            candidate_ids = _unique_strings([*evidence_ids, str(candidate.get("candidate_id") or f"candidate-{index:03d}")])
            page_path = _source_candidate_page_path(wiki_root, candidate, index, seen_slugs)
            page_body = _source_candidate_page_body(candidate, action=action, query=query, evidence_ids=candidate_ids)
            _write_text_if_changed_bridge(page_path, page_body)
            edge_paths.append(
                _append_source_fan_in_edge(
                    wiki_root,
                    page_path,
                    candidate,
                    action=action,
                    evidence_ids=candidate_ids,
                )
            )
            written_pages.append(_rel(page_path))
            artifacts.append({"type": "wiki_paper", "path": _rel(page_path)})

        if written_pages:
            log_path = _write_generic_wiki_log(
                wiki_root,
                "Source Candidate Fan-In",
                wiki_root / "papers",
                evidence_ids,
                f"Wrote {len(written_pages)} approved runtime source candidate(s) from {action}.",
            )
            rebuild_paths = _rebuild_generic_wiki_views(
                wiki_root,
                str(envelope.get("run_id") or envelope.get("sprint_id") or "autosci-source-fan-in"),
                wiki_root / "papers",
                evidence_ids,
            )
            status = "completed"
            write.update(
                {
                    "status": status,
                    "applied": True,
                    "wiki_root": _rel(wiki_root),
                    "written_count": len(written_pages),
                    "written_pages": written_pages,
                    "log_path": _rel(log_path),
                    "edge_paths": _unique_strings([_rel(path) for path in edge_paths]),
                    "rebuilt_paths": [_rel(path) for path in rebuild_paths],
                }
            )
            artifacts.extend(
                [
                    {"type": "wiki_log", "path": _rel(log_path)},
                    *[{"type": "wiki_graph_edges", "path": _rel(path)} for path in edge_paths],
                    *[{"type": "wiki_rebuild", "path": _rel(path)} for path in rebuild_paths],
                ]
            )
            limitations.append("Approved source fan-in wrote runtime candidates into wiki papers, graph edges, log, and views.")
        else:
            limitations.append("Source fan-in write-back found no valid candidate dictionaries to write.")

    write["status"] = status
    write["applied"] = status == "completed"
    write["written_count"] = len(write.get("written_pages") or [])
    evidence = {
        "schema": "source_fan_in_writeback.v1",
        "task_id": f"task-{action}:source-fan-in",
        "sprint_id": str(envelope.get("sprint_id") or "sprint-autosci"),
        "node_id": f"node-{action}:source-fan-in",
        "status": status,
        "inputs": inputs,
        "outputs": {
            "write": write,
            "query": query,
            "candidates": candidates,
            "semantic_runtime": semantic,
        },
        "artifacts": artifacts,
        "provenance": {
            "operator_id": "autosci-bridge",
            "implementation_package": "plugins/autosci",
            "timestamp": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        },
        "limitations": limitations,
    }
    sidecar_path = _source_fan_in_path(envelope, action)
    write["sidecar_path"] = _rel(sidecar_path)
    artifact = {"type": "source_fan_in_writeback_json", "path": _write_evidence_payload(sidecar_path, evidence)}
    return {
        "summary": write,
        "artifact": artifact,
        "limitations": limitations,
        "artifacts": artifacts,
    }


def _action_init_sources(envelope: dict[str, Any]) -> dict[str, Any]:
    inputs = dict(envelope.get("inputs") or {})
    query = str(inputs.get("query") or inputs.get("topic") or inputs.get("target") or "AutoSci source initialization")
    contract = _approval_contract(
        envelope,
        "init_sources",
        ["network_source_fetch", "bulk_ingest", "wiki_fan_in"],
    )
    semantic = _approval_semantic_runtime(contract, "init_sources", limit=int(inputs.get("limit") or 10))
    contract["semantic_runtime"] = semantic
    candidates = semantic.get("detail", {}).get("candidates") if isinstance(semantic.get("detail"), dict) else []
    candidates = candidates if isinstance(candidates, list) else []
    contract_artifact = _write_approval_contract_sidecar(envelope, "init_sources", contract)
    fan_in = _source_candidate_wiki_fan_in(
        envelope,
        action="init_sources",
        query=query,
        candidates=candidates,
        semantic=semantic,
        contract=contract,
    )
    artifacts = [contract_artifact]
    if fan_in.get("artifact"):
        artifacts.append(fan_in["artifact"])
    limitations = [
        "Init source preparation did not execute network fetch or fan-in ingest inside this bridge.",
        "Provide topic, anchors, approved network fetch, or source manifests before treating initialization as complete.",
        *_approval_contract_limitations(contract),
    ]
    if semantic.get("verified"):
        limitations = [
            "Init source runtime was verified from supplied approval-gated evidence; this bridge did not execute the fetch.",
        ]
    limitations.extend(str(item) for item in fan_in.get("limitations") or [])
    return convert_literature_discovery({
        "query": query,
        "mode": "init_runtime_verified" if semantic.get("verified") else "init_plan",
        "limit": int(inputs.get("limit") or 10),
        "candidates": candidates,
        "source_fan_in": fan_in.get("summary"),
        "status": "completed" if semantic.get("verified") else "inconclusive",
        "artifacts": artifacts,
        "limitations": limitations,
    }, envelope)


def _action_daily_arxiv_prepare_finalize(envelope: dict[str, Any]) -> dict[str, Any]:
    inputs = dict(envelope.get("inputs") or {})
    query = str(inputs.get("query") or inputs.get("topic") or "daily arXiv digest")
    contract = _approval_contract(
        envelope,
        "daily_arxiv_prepare_finalize",
        ["network_feed_fetch", "digest_email_send", "auto_ingest"],
    )
    semantic = _approval_semantic_runtime(
        contract,
        "daily_arxiv_prepare_finalize",
        limit=int(inputs.get("limit") or 10),
    )
    contract["semantic_runtime"] = semantic
    candidates = semantic.get("detail", {}).get("candidates") if isinstance(semantic.get("detail"), dict) else []
    candidates = candidates if isinstance(candidates, list) else []
    contract_artifact = _write_approval_contract_sidecar(envelope, "daily_arxiv_prepare_finalize", contract)
    fan_in = _source_candidate_wiki_fan_in(
        envelope,
        action="daily_arxiv_prepare_finalize",
        query=query,
        candidates=candidates,
        semantic=semantic,
        contract=contract,
    )
    artifacts = [contract_artifact]
    if fan_in.get("artifact"):
        artifacts.append(fan_in["artifact"])
    limitations = [
        "Daily arXiv prepare/finalize is approval-gated; this bridge did not execute network feed fetch, email, or auto-ingest.",
        "Provide approved feed fetch evidence before treating this digest as complete.",
        *_approval_contract_limitations(contract),
    ]
    if semantic.get("verified"):
        limitations = [
            "Daily arXiv runtime was verified from supplied approval-gated evidence; this bridge did not execute network/email side effects.",
        ]
    limitations.extend(str(item) for item in fan_in.get("limitations") or [])
    return convert_literature_discovery({
        "query": query,
        "mode": "daily_arxiv_runtime_verified" if semantic.get("verified") else "daily_arxiv_plan",
        "limit": int(inputs.get("limit") or 10),
        "candidates": candidates,
        "source_fan_in": fan_in.get("summary"),
        "status": "completed" if semantic.get("verified") else "inconclusive",
        "artifacts": artifacts,
        "limitations": limitations,
    }, envelope)


def _action_discover_literature(envelope: dict[str, Any]) -> dict[str, Any]:
    inputs = dict(envelope.get("inputs") or {})
    wiki_root = _resolve_harness_path(str(inputs.get("wiki_root") or "artifacts/autosci/workspace/wiki"))
    runtime_requested = bool(
        inputs.get("approval_ref")
        or inputs.get("allowlist_evidence")
        or inputs.get("before_artifacts")
        or inputs.get("runtime_evidence")
        or inputs.get("after_artifacts")
    )
    if runtime_requested:
        query = str(inputs.get("query") or inputs.get("topic") or "AutoSci literature discovery")
        limit = int(inputs.get("limit") or 10)
        contract = _approval_contract(
            envelope,
            "discover_literature",
            ["network_source_fetch", "source_manifest_ingest"],
        )
        semantic = _approval_semantic_runtime(contract, "discover_literature", limit=limit)
        contract["semantic_runtime"] = semantic
        candidates = semantic.get("detail", {}).get("candidates") if isinstance(semantic.get("detail"), dict) else []
        candidates = candidates if isinstance(candidates, list) else []
        contract_artifact = _write_approval_contract_sidecar(envelope, "discover_literature", contract)
        runtime_artifacts = _contract_existing_artifacts(
            contract,
            "runtime_evidence",
            "source_runtime_evidence_json",
        )
        limitations = [
            "Literature discovery used supplied approval-gated runtime evidence; the bridge did not execute network fetches.",
            *_approval_contract_limitations(contract),
        ]
        if semantic.get("verified"):
            limitations = [
                "Literature discovery runtime was verified from supplied approval-gated source evidence; this bridge did not execute the fetch.",
            ]
        return convert_literature_discovery({
            "query": query,
            "mode": "discover_literature_runtime_verified" if semantic.get("verified") else "discover_literature_runtime_pending",
            "limit": limit,
            "candidates": candidates,
            "status": "completed" if semantic.get("verified") else "inconclusive",
            "artifacts": [contract_artifact, *runtime_artifacts],
            "limitations": limitations,
        }, envelope)

    allow_network_fetch = str(inputs.get("allow_network_fetch", "true")).lower() not in {"0", "false", "no"}
    if os.environ.get("AUTOSCI_DISABLE_NETWORK_FETCH", "").lower() in {"1", "true", "yes"}:
        allow_network_fetch = False
    fixture_fallback = bool(inputs.get("fixture_fallback")) or (
        str(envelope.get("mode") or "") == "fixture"
        and not any(
            key in inputs
            for key in (
                "discover_mode",
                "from_wiki",
                "anchors",
                "anchor_ids",
                "venue",
                "year",
                "limit",
            )
        )
    )
    discover_mode = str(inputs.get("discover_mode") or "")
    if inputs.get("from_wiki") and not discover_mode:
        discover_mode = "wiki"
    raw = discover_literature(
        query=str(inputs.get("query") or inputs.get("topic") or ""),
        mode=discover_mode,
        anchors=list(inputs.get("anchors") or inputs.get("anchor_ids") or []),
        negative_ids=list(inputs.get("negative_ids") or []),
        venue=str(inputs.get("venue") or ""),
        year=int(inputs["year"]) if inputs.get("year") else None,
        limit=int(inputs.get("limit") or 10),
        wiki_root=wiki_root,
        workspace_root=HARNESS_DIR,
        repository_root=REPO_HARNESS_DIR,
        allow_network_fetch=allow_network_fetch,
        no_citation_expand=bool(inputs.get("no_citation_expand")),
        fixture_fallback=fixture_fallback,
    )
    return convert_literature_discovery(raw, envelope)


def _phase9_sidecar_paths(envelope: dict[str, Any]) -> tuple[Path, Path]:
    output_dir = _output_dir(envelope, "ingest_paper")
    outputs = envelope.get("outputs") if isinstance(envelope.get("outputs"), dict) else {}
    memory_raw = outputs.get("memory_update_path") if isinstance(outputs, dict) else None
    graph_raw = outputs.get("graph_update_path") if isinstance(outputs, dict) else None
    memory_path = Path(str(memory_raw)) if memory_raw else output_dir / "research_memory_update.json"
    graph_path = Path(str(graph_raw)) if graph_raw else output_dir / "research_graph_update.json"
    if not memory_path.is_absolute():
        memory_path = HARNESS_DIR / memory_path
    if not graph_path.is_absolute():
        graph_path = HARNESS_DIR / graph_path
    return memory_path, graph_path


def _write_phase9_foundation_sidecars(envelope: dict[str, Any], paper_evidence: dict[str, Any]) -> list[str]:
    memory_path, graph_path = _phase9_sidecar_paths(envelope)
    memory_evidence = convert_research_memory_update(_paper_update_raw(envelope, paper_evidence), envelope)
    graph_evidence = convert_research_graph_update(_paper_update_raw(envelope, paper_evidence), envelope)
    return [
        _write_evidence_payload(memory_path, memory_evidence),
        _write_evidence_payload(graph_path, graph_evidence),
    ]


def _load_optional_evidence(raw_path: Any) -> dict[str, Any] | None:
    if not raw_path:
        return None
    path = _resolve_harness_path(str(raw_path))
    if not path.exists():
        return None
    try:
        payload = _load_json(path)
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _load_optional_evidence_many(raw_value: Any) -> list[dict[str, Any]]:
    if isinstance(raw_value, list):
        return [payload for item in raw_value if (payload := _load_optional_evidence(item))]
    payload = _load_optional_evidence(raw_value)
    return [payload] if payload else []


def _claim_text_from_evidence(envelope: dict[str, Any], claim_id: str) -> str:
    inputs = dict(envelope.get("inputs") or {})
    for payload in _load_optional_evidence_many(inputs.get("claims_evidence")):
        outputs = payload.get("outputs") if isinstance(payload, dict) else {}
        claims = outputs.get("claims") if isinstance(outputs, dict) else []
        for claim in (claims if isinstance(claims, list) else []):
            if isinstance(claim, dict) and str(claim.get("claim_id") or "") == claim_id:
                return str(claim.get("text") or "")
    return ""


def _claims_from_evidence(envelope: dict[str, Any]) -> list[dict[str, Any]]:
    inputs = dict(envelope.get("inputs") or {})
    out: list[dict[str, Any]] = []
    for payload in _load_optional_evidence_many(inputs.get("claims_evidence")):
        outputs = payload.get("outputs") if isinstance(payload, dict) else {}
        claims = outputs.get("claims") if isinstance(outputs, dict) else []
        if isinstance(claims, list):
            out.extend(claim for claim in claims if isinstance(claim, dict))
    return out


def _methods_from_evidence(envelope: dict[str, Any]) -> list[dict[str, Any]]:
    inputs = dict(envelope.get("inputs") or {})
    payload = _load_optional_evidence(inputs.get("method_evidence"))
    outputs = payload.get("outputs") if isinstance(payload, dict) else {}
    methods = outputs.get("methods") if isinstance(outputs, dict) else []
    return [method for method in methods if isinstance(method, dict)] if isinstance(methods, list) else []


def _ideas_from_evidence(envelope: dict[str, Any]) -> list[dict[str, Any]]:
    inputs = dict(envelope.get("inputs") or {})
    payload = _load_optional_evidence(inputs.get("ideas_evidence"))
    outputs = payload.get("outputs") if isinstance(payload, dict) else {}
    ideas = outputs.get("ideas") if isinstance(outputs, dict) else []
    return [idea for idea in ideas if isinstance(idea, dict)] if isinstance(ideas, list) else []


def _target_idea_from_inputs(envelope: dict[str, Any]) -> dict[str, Any] | None:
    inputs = dict(envelope.get("inputs") or {})
    target = str(inputs.get("target") or inputs.get("topic") or inputs.get("query") or "").strip()
    if not target:
        return None
    safe_id = re.sub(r"[^a-z0-9]+", "-", target.lower()).strip("-")[:48] or "target"
    return {
        "idea_id": f"idea-target-{safe_id}",
        "title": target[:120],
        "hypothesis": f"The proposed target `{target}` may address an evidence-backed research gap.",
        "approach": "Assess novelty against local wiki/discovery evidence before designing an experiment.",
        "origin_evidence_ids": ["target:user-supplied"],
        "novelty_hypothesis": "User-supplied target requires multi-source novelty and review validation.",
        "source_mode": "target",
        "generation_path": "novelty-target",
        "duplicate_status": "unknown",
        "status": "candidate",
    }


def _source_memory_evidence_ids(envelope: dict[str, Any]) -> list[str]:
    inputs = dict(envelope.get("inputs") or {})
    evidence_ids: list[str] = []
    for key in ("paper_evidence", "claims_evidence", "method_evidence", "memory_evidence"):
        payload = _load_optional_evidence(inputs.get(key))
        if not payload:
            continue
        schema = str(payload.get("schema") or "")
        task_id = str(payload.get("task_id") or "")
        if task_id:
            evidence_ids.append(task_id)
        outputs = payload.get("outputs") if isinstance(payload.get("outputs"), dict) else {}
        for collection, id_field in (
            ("claims", "claim_id"),
            ("methods", "method_id"),
            ("changes", "entity_id"),
            ("ideas", "idea_id"),
        ):
            values = outputs.get(collection) if isinstance(outputs, dict) else None
            if isinstance(values, list):
                for item in values:
                    if isinstance(item, dict) and item.get(id_field):
                        evidence_ids.append(str(item[id_field]))
        if schema and not evidence_ids:
            evidence_ids.append(schema)
    seen: set[str] = set()
    unique: list[str] = []
    for item in evidence_ids:
        if item not in seen:
            seen.add(item)
            unique.append(item)
    return unique


def _tokens(value: str) -> set[str]:
    stop_words = {
        "about",
        "after",
        "agent",
        "before",
        "fixture",
        "from",
        "into",
        "markdown",
        "paper",
        "phase",
        "sample",
        "that",
        "the",
        "this",
        "with",
        "without",
    }
    return {
        token
        for token in re.findall(r"[a-z0-9_]+", value.lower())
        if len(token) >= 4 and token not in stop_words
    }


def _code_relevance(claim_text: str, code_text: str) -> tuple[str, str]:
    if not claim_text.strip():
        return "unknown", "No claim text was available to compare with the code file."
    claim_tokens = _tokens(claim_text)
    code_tokens = _tokens(code_text)
    overlap = sorted(claim_tokens & code_tokens)
    if len(overlap) >= 2:
        return "related", f"Claim and code share terms: {', '.join(overlap[:5])}."
    return "unknown", "The file exists, but the script could not prove that it supports the claim."


def _action_extract_claims(envelope: dict[str, Any]) -> dict[str, Any]:
    return convert_research_claims(_paper_claims_raw(envelope), envelope)


def _action_extract_methods(envelope: dict[str, Any]) -> dict[str, Any]:
    return convert_research_method(_paper_methods_raw(envelope), envelope)


def _action_map_code_evidence(envelope: dict[str, Any]) -> dict[str, Any]:
    inputs = dict(envelope.get("inputs") or {})
    raw_repo = inputs.get("repo_path") or "plugins/autosci/tests/fixtures/sample_repo"
    repo_path = _resolve_harness_path(str(raw_repo))
    claim_id = str(inputs.get("claim_id") or "claim-001")
    claim_text = _claim_text_from_evidence(envelope, claim_id)
    if repo_path.exists():
        files = sorted(path for path in repo_path.rglob("*.py") if path.is_file())
        if files:
            primary = files[0]
            code_text = primary.read_text(encoding="utf-8", errors="replace")
            relevance_label, relevance_reason = _code_relevance(claim_text, code_text)
            mapping_status = "mapped" if relevance_label != "unknown" else "unknown"
            mapping: dict[str, Any] = {
                "mapping_id": "map-001",
                "claim_id": claim_id,
                "repo_or_path": _rel(repo_path),
                "files": [_rel(primary)],
                "symbols": ["run_fixture_bridge"],
                "execution_entrypoint": f"python3 {_rel(primary)}",
                "mapping_status": mapping_status,
                "relevance_label": relevance_label,
                "relevance_reason": relevance_reason,
                "evidence_ids": [claim_id],
            }
            if mapping_status == "unknown":
                mapping["unknown_reason"] = relevance_reason
            else:
                mapping["evidence_ids"].append(_rel(primary))
            return convert_code_evidence_map({
                "mappings": [mapping],
                "limitations": ["Code mapping records candidate file relevance; it is not evidence of claim verification."],
            }, envelope)
    return convert_code_evidence_map({
        "mappings": [
            {
                "mapping_id": "map-001",
                "claim_id": claim_id,
                "repo_or_path": str(raw_repo),
                "files": ["N/A"],
                "execution_entrypoint": "fixture-mode",
                "mapping_status": "unknown",
                "relevance_label": "unknown",
                "relevance_reason": f"Repository path not available: {raw_repo}",
                "evidence_ids": [claim_id],
                "unknown_reason": f"Repository path not available: {raw_repo}",
            }
        ],
        "limitations": ["Code evidence mapping is unknown because the repository path was unavailable."],
    }, envelope)


def _action_generate_ideas(envelope: dict[str, Any]) -> dict[str, Any]:
    mode = str(envelope.get("mode") or "")
    inputs = dict(envelope.get("inputs") or {})
    wiki_state, wiki_state_artifact = _wiki_state_resolver_artifact(envelope, "generate_ideas")
    wiki_artifacts = [wiki_state_artifact] if wiki_state_artifact else []
    if mode != "fixture" and not inputs.get("smoke_mode"):
        sourced = build_idea_candidates(envelope, workspace_root=HARNESS_DIR, repository_root=REPO_HARNESS_DIR)
        source_summary = sourced.get("source_summary") if isinstance(sourced.get("source_summary"), dict) else {}
        if _model_output_requested(envelope):
            topic = str(inputs.get("topic") or inputs.get("query") or inputs.get("target") or "research workflow")
            model, model_artifacts = _model_output(
                envelope,
                action="generate_ideas",
                prompt=(
                    "Brainstorm source-grounded AutoSci research ideas. Return JSON with outputs.ideas; each idea "
                    "must include title, hypothesis, approach, novelty_hypothesis, and origin_evidence_ids."
                ),
                context={
                    "topic": topic,
                    "source_summary": source_summary,
                    "wiki_state_resolution": (wiki_state or {}).get("resolution") if isinstance(wiki_state, dict) else {},
                    "local_candidate_count": len(sourced.get("ideas") or []),
                },
            )
            model_ideas, skipped_model_ideas = _idea_candidates_from_model_output(
                model,
                source_mode=str(source_summary.get("source_mode") or "external"),
            )
            if model.get("status") == "completed" and model_ideas:
                return convert_idea_candidate(
                    {
                        "ideas": model_ideas,
                        "artifacts": [*wiki_artifacts, *model_artifacts],
                        "limitations": [
                            "Ideas came from explicit model evidence or a model-command bridge; novelty/review validation remains required.",
                            *(
                                [f"Skipped incomplete model ideas: {'; '.join(skipped_model_ideas)}"]
                                if skipped_model_ideas
                                else []
                            ),
                            *_wiki_state_limitations(wiki_state),
                        ],
                    },
                    envelope,
                    status="completed",
                )
            if model.get("status") in {"failed", "invalid", "inconclusive"}:
                return convert_idea_candidate(
                    {
                        "ideas": sourced["ideas"],
                        "artifacts": [*wiki_artifacts, *model_artifacts],
                        "limitations": [
                            f"Explicit model brainstorm did not complete: {model.get('reason') or model.get('status')}.",
                            "Returned source-grounded local candidates as inconclusive fallback evidence, not as model brainstorm parity.",
                            *list(sourced["limitations"]),
                            *_wiki_state_limitations(wiki_state),
                        ],
                    },
                    envelope,
                    status="inconclusive",
                )
        return convert_idea_candidate(
            {
                "ideas": sourced["ideas"],
                "artifacts": wiki_artifacts,
                "limitations": [*list(sourced["limitations"]), *_wiki_state_limitations(wiki_state)],
            },
            envelope,
            status=str(sourced.get("status") or "completed"),
        )
    claims = _claims_from_evidence(envelope)
    methods = _methods_from_evidence(envelope)
    source_ids = _source_memory_evidence_ids(envelope)
    primary_claim = next(
        (claim for claim in claims if str(claim.get("testability") or "") in {"testable", "partially_testable"}),
        claims[0] if claims else {},
    )
    primary_method = methods[0] if methods else {}
    claim_id = str(primary_claim.get("claim_id") or "claim-001")
    method_id = str(primary_method.get("method_id") or "method-001")
    claim_text = str(primary_claim.get("text") or "Fixture claim evidence needs a follow-up experiment.")
    method_name = str(primary_method.get("name") or "Fixture method")
    origin_ids = [item for item in [claim_id, method_id, *source_ids] if item]
    ideas = [
        {
            "idea_id": "idea-001",
            "title": "Evidence-linked verification coverage experiment",
            "hypothesis": (
                "Pairing source-grounded claims with method and code evidence will expose verification gaps "
                "before claim verdict generation."
            ),
            "approach": (
                f"Use claim `{claim_id}` and method `{method_id}` to compare source-only evidence against "
                "source-plus-code evidence coverage."
            ),
            "origin_evidence_ids": origin_ids or [claim_id],
            "novelty_hypothesis": "Combines claim, method, and code evidence at the same Solar Evidence ABI grain.",
            "grounding_summary": f"Seeded from claim: {claim_text}",
            "source_mode": "fixture",
            "generation_path": "fixture-smoke",
            "duplicate_status": "new",
            "status": "candidate",
        },
        {
            "idea_id": "idea-duplicate-001",
            "title": "Repeat existing fixture bridge smoke",
            "hypothesis": "Repeating the bridge smoke test alone will improve scientific verification.",
            "approach": f"Run the existing {method_name} without adding new evidence dimensions.",
            "origin_evidence_ids": origin_ids or [method_id],
            "novelty_hypothesis": "Low novelty because it duplicates the fixture smoke path.",
            "grounding_summary": "Included to prove duplicate ideas are marked rather than silently promoted.",
            "source_mode": "fixture",
            "generation_path": "fixture-smoke",
            "duplicate_status": "duplicate",
            "duplicate_of": "task-autosci-smoke",
            "status": "filtered",
        },
    ]
    return convert_idea_candidate({
        "ideas": ideas,
        "artifacts": wiki_artifacts,
        "limitations": ["Fixture ideas are generated from supplied local evidence only; external novelty is not proven."],
    }, envelope)


def _novelty_payload_archive_artifacts(evaluations: list[dict[str, Any]]) -> list[dict[str, str]]:
    paths: list[str] = []
    for evaluation in evaluations:
        if not isinstance(evaluation, dict):
            continue
        external = evaluation.get("external_novelty")
        if not isinstance(external, dict):
            continue
        for status in external.get("provider_statuses", []):
            if not isinstance(status, dict):
                continue
            raw_paths = status.get("raw_payload_archive_paths")
            if isinstance(raw_paths, list):
                paths.extend(str(item) for item in raw_paths if str(item).strip())
            raw_path = str(status.get("raw_payload_archive_path") or "").strip()
            if raw_path:
                paths.append(raw_path)
    artifacts: list[dict[str, str]] = []
    seen: set[str] = set()
    for raw_path in paths:
        path = Path(raw_path)
        path_text = _rel(path) if path.is_absolute() else raw_path
        if path_text in seen:
            continue
        seen.add(path_text)
        artifacts.append({"type": "external_novelty_payload_json", "path": path_text})
    return artifacts


def _action_evaluate_ideas(envelope: dict[str, Any]) -> dict[str, Any]:
    mode = str(envelope.get("mode") or "")
    inputs = dict(envelope.get("inputs") or {})
    wiki_state, wiki_state_artifact = _wiki_state_resolver_artifact(envelope, "evaluate_ideas")
    wiki_artifacts = [wiki_state_artifact] if wiki_state_artifact else []
    if mode != "fixture" and not inputs.get("smoke_mode"):
        inputs.setdefault(
            "novelty_payload_archive_dir",
            str(_output_dir(envelope, "evaluate_ideas") / "external_novelty_payloads"),
        )
    ideas = _ideas_from_evidence(envelope)
    if not ideas:
        target_idea = _target_idea_from_wiki_state(wiki_state) or _target_idea_from_inputs(envelope)
        if target_idea and mode != "fixture" and not inputs.get("smoke_mode"):
            ideas = [target_idea]
        else:
            ideas = convert_idea_candidate({}, envelope)["outputs"]["ideas"]
    evaluations: list[dict[str, Any]] = []
    for idea in ideas:
        idea_id = str(idea.get("idea_id") or f"idea-{len(evaluations) + 1:03d}")
        duplicate_status = str(idea.get("duplicate_status") or "unknown")
        source_mode = str(idea.get("source_mode") or "unknown")
        origin_ids = list(idea.get("origin_evidence_ids") or [idea_id])
        if duplicate_status in {"duplicate", "insufficient_source"} or source_mode == "missing":
            evaluations.append({
                "idea_id": idea_id,
                "novelty": 0.15 if duplicate_status == "duplicate" else 0.0,
                "feasibility": 0.8 if duplicate_status == "duplicate" else 0.2,
                "recommendation": "reject" if duplicate_status == "duplicate" else "inconclusive",
                "risks": [
                    "Marked duplicate of an existing fixture smoke path."
                    if duplicate_status == "duplicate"
                    else "No wiki, discovery, or paper source evidence was available."
                ],
                "evidence_ids": [idea_id, *origin_ids],
                "novelty_rationale": (
                    "The idea duplicates known fixture validation rather than adding a new research question."
                    if duplicate_status == "duplicate"
                    else "Novelty cannot be assessed without source evidence."
                ),
                "feasibility_rationale": (
                    "It is easy to run but does not add meaningful evidence."
                    if duplicate_status == "duplicate"
                    else "Feasibility cannot be assessed without a concrete sourced idea."
                ),
                "duplicate_status": duplicate_status,
                "source_mode": source_mode,
            })
        else:
            validation = (
                {}
                if source_mode == "fixture" or mode == "fixture" or inputs.get("smoke_mode")
                else evaluate_novelty_and_review(
                    idea,
                    inputs,
                    workspace_root=HARNESS_DIR,
                    repository_root=REPO_HARNESS_DIR,
                )
            )
            novelty = 0.68 if source_mode == "fixture" else float(validation.get("novelty", 0.62))
            feasibility = 0.76 if source_mode == "fixture" else max(0.25, float(validation.get("review_score", 0.55)))
            recommendation = "advance" if source_mode == "fixture" else str(validation.get("recommendation") or "revise")
            risks = (
                ["External novelty is unverified because fixture mode does not search live literature."]
                if source_mode == "fixture"
                else list(validation.get("risks") or ["Requires /novelty and /review validation before promotion."])
            )
            closest_prior_work = list(validation.get("closest_prior_work") or [])
            validation_review_llm = validation.get("review_llm") if isinstance(validation.get("review_llm"), dict) else {}
            validation_evidence_ids = [
                str(item.get("source_id"))
                for item in closest_prior_work
                if isinstance(item, dict) and str(item.get("source_id") or "").strip()
            ]
            validation_evidence_ids.extend(
                str(item)
                for item in validation_review_llm.get("evidence_ids", [])
                if str(item).strip()
            )
            evidence_ids = list(dict.fromkeys(str(item) for item in [idea_id, *origin_ids, *validation_evidence_ids] if str(item).strip()))
            evaluations.append({
                "idea_id": idea_id,
                "novelty": novelty,
                "feasibility": feasibility,
                "recommendation": recommendation,
                "risks": risks,
                "evidence_ids": evidence_ids,
                "novelty_rationale": (
                    "The idea combines claim, method, and code evidence at a shared artifact grain."
                    if source_mode == "fixture"
                    else str(validation.get("novelty_rationale") or "The idea is grounded in source evidence but still requires validation.")
                ),
                "feasibility_rationale": (
                    "The required inputs already exist as Solar Evidence ABI artifacts."
                    if source_mode == "fixture"
                    else str(validation.get("review_rationale") or "A bounded pilot should be designed before full execution.")
                ),
                "duplicate_status": duplicate_status,
                "source_mode": source_mode,
                "closest_prior_work": closest_prior_work,
                "review_score": validation.get("review_score", "N/A") if validation else "N/A",
                "review_mode": validation.get("review_mode", "N/A") if validation else "N/A",
                "review_available": bool(validation.get("review_available", False)) if validation else False,
                "review_llm": validation_review_llm if validation else {"status": "N/A"},
                "novelty_label": validation.get("novelty_label", "fixture") if validation else "fixture",
                "failed_overlap": validation.get("failed_overlap", "") if validation else "",
                "source_count": validation.get("source_count", "N/A") if validation else "N/A",
                "local_source_count": validation.get("local_source_count", "N/A") if validation else "N/A",
                "external_source_count": validation.get("external_source_count", "N/A") if validation else "N/A",
                "external_novelty": validation.get("external_novelty", {"status": "N/A"}) if validation else {"status": "N/A"},
            })
    limitations = ["Fixture evaluation uses local evidence and does not update idea status directly."]
    if mode != "fixture" and not inputs.get("smoke_mode"):
        limitations = [
            "Novelty/review signals are derived from local wiki/discovery evidence.",
            "Independent Review LLM and live external search are still required before promotion.",
        ]
    return convert_idea_evaluation({
        "evaluations": evaluations,
        "artifacts": [*_novelty_payload_archive_artifacts(evaluations), *wiki_artifacts],
        "limitations": [*limitations, *_wiki_state_limitations(wiki_state)],
    }, envelope)


def _action_review_artifact(envelope: dict[str, Any]) -> dict[str, Any]:
    raw = review_artifact(
        dict(envelope.get("inputs") or {}),
        workspace_root=HARNESS_DIR,
        repository_root=REPO_HARNESS_DIR,
    )
    output_dir = _output_dir(envelope, "review_artifact")
    report_path = output_dir / "artifact_review.md"
    artifacts = []
    artifact = raw.get("artifact") if isinstance(raw.get("artifact"), dict) else {}
    artifact_path = Path(str(artifact.get("path") or ""))
    if artifact_path.is_absolute() and artifact_path.exists():
        artifacts.append({"type": "review_target", "path": _rel(artifact_path)})
    report_markdown = str(raw.get("report_markdown") or "")
    if report_markdown:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report_markdown, encoding="utf-8")
        artifacts.append({"type": "artifact_review_markdown", "path": _rel(report_path)})
    timestamp = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return {
        "schema": "artifact_review.v1",
        "task_id": str(envelope.get("task_id") or "task-review-artifact"),
        "sprint_id": str(envelope.get("sprint_id") or "sprint-autosci-review"),
        "node_id": str(envelope.get("node_id") or "node-review-artifact"),
        "status": str(raw.get("status") or "inconclusive"),
        "inputs": dict(envelope.get("inputs") or {}),
        "outputs": {
            "review": raw.get("review") if isinstance(raw.get("review"), dict) else {},
            "findings": list(raw.get("findings") or []),
            "artifact": artifact,
        },
        "artifacts": artifacts,
        "provenance": {
            "operator_id": "autosci-bridge-review",
            "implementation_package": "plugins/autosci",
            "timestamp": timestamp,
        },
        "limitations": list(raw.get("limitations") or ["Review LLM MCP evidence is unavailable."]),
    }


def _phase11_memory_update_path(envelope: dict[str, Any]) -> Path:
    output_dir = _output_dir(envelope, "evaluate_ideas")
    outputs = envelope.get("outputs") if isinstance(envelope.get("outputs"), dict) else {}
    raw = outputs.get("memory_update_path") if isinstance(outputs, dict) else None
    path = Path(str(raw)) if raw else output_dir / "research_memory_update.ideas.json"
    if not path.is_absolute():
        path = HARNESS_DIR / path
    return path


def _write_phase11_idea_memory_sidecar(envelope: dict[str, Any], evaluation_evidence: dict[str, Any]) -> str:
    path = _phase11_memory_update_path(envelope)
    evaluations = list((evaluation_evidence.get("outputs") or {}).get("evaluations") or [])
    changes = []
    for evaluation in evaluations:
        if not isinstance(evaluation, dict):
            continue
        idea_id = str(evaluation.get("idea_id") or "")
        if not idea_id:
            continue
        changes.append({
            "entity_type": "idea",
            "entity_id": idea_id,
            "operation": "propose",
            "path": f"knowledge/research/ideas/{idea_id}.md",
            "evidence_ids": list(evaluation.get("evidence_ids") or [idea_id]),
            "confidence": float(evaluation.get("feasibility") or 0.5),
            "recommendation": evaluation.get("recommendation"),
        })
    memory_evidence = convert_research_memory_update({
        "changes": changes or [{
            "entity_type": "idea",
            "entity_id": "idea-unknown",
            "operation": "no_op",
            "path": "knowledge/research/ideas/N/A",
            "evidence_ids": [str(evaluation_evidence.get("task_id") or "idea-evaluation")],
            "confidence": 0.0,
        }],
        "limitations": ["Fixture proposes idea memory records; it does not mutate research memory."],
    }, envelope)
    return _write_evidence_payload(path, memory_evidence)


def _novelty_writeback_path(envelope: dict[str, Any]) -> Path:
    output_dir = _output_dir(envelope, "evaluate_ideas")
    return output_dir / "novelty_writeback.json"


def _wiki_roots_for_write(envelope: dict[str, Any]) -> list[Path]:
    inputs = dict(envelope.get("inputs") or {})
    raw_root = str(inputs.get("wiki_root") or "").strip()
    roots: list[Path] = []
    if raw_root:
        path = Path(raw_root)
        roots.append(path if path.is_absolute() else HARNESS_DIR / path)
    roots.extend(
        [
            HARNESS_DIR / "artifacts" / "autosci" / "workspace" / "wiki",
            HARNESS_DIR / "wiki",
            REPO_HARNESS_DIR / "harness" / "artifacts" / "autosci" / "workspace" / "wiki",
        ]
    )
    seen: set[Path] = set()
    out: list[Path] = []
    for root in roots:
        try:
            resolved = root.resolve()
        except OSError:
            continue
        if resolved in seen:
            continue
        seen.add(resolved)
        out.append(root)
    return out


def _path_is_under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _target_idea_path_for_write(envelope: dict[str, Any]) -> tuple[Path | None, str, list[str]]:
    inputs = dict(envelope.get("inputs") or {})
    target = str(inputs.get("target") or inputs.get("topic") or inputs.get("query") or "").strip()
    if not target:
        return None, "", ["No idea target was supplied for novelty write-back."]
    roots = _wiki_roots_for_write(envelope)
    raw_path = Path(target)
    candidates: list[Path] = []
    if raw_path.suffix.lower() in {".md", ".markdown"}:
        if raw_path.is_absolute():
            candidates.append(raw_path)
        else:
            for root in roots:
                candidates.extend([root / raw_path, root / "ideas" / raw_path.name])
    else:
        slug = _slug(raw_path.stem if raw_path.suffix else target)
        for root in roots:
            candidates.append(root / "ideas" / f"{slug}.md")

    checked: list[str] = []
    for candidate in candidates:
        checked.append(str(candidate))
        if not candidate.exists() or not candidate.is_file():
            continue
        if not any(_path_is_under(candidate, root) for root in roots):
            continue
        return candidate, _slug(candidate.stem), checked
    return None, _slug(raw_path.stem if raw_path.suffix else target), checked


def _set_frontmatter_scalar(text: str, key: str, value: str) -> str | None:
    match = re.match(r"^---\s*\n(.*?)\n---\s*(?:\n|$)", text, flags=re.S)
    if not match:
        return None
    body = match.group(1)
    lines = body.splitlines()
    replacement = f"{key}: {value}"
    for idx, line in enumerate(lines):
        if line.split(":", 1)[0].strip() == key:
            lines[idx] = replacement
            break
    else:
        lines.append(replacement)
    return "---\n" + "\n".join(lines).rstrip() + "\n---\n" + text[match.end():]


def _novelty_score_from_evaluation(evaluation: dict[str, Any]) -> int | None:
    try:
        novelty = float(evaluation.get("novelty"))
    except (TypeError, ValueError):
        return None
    if novelty < 0:
        novelty = 0.0
    if novelty > 1:
        novelty = 1.0
    return max(1, min(5, int(novelty * 4 + 1.5)))


def _external_novelty_status(evaluation: dict[str, Any]) -> str:
    external = evaluation.get("external_novelty")
    if not isinstance(external, dict):
        return "missing"
    return str(external.get("status") or "missing")


def _external_novelty_provenance_status(evaluation: dict[str, Any]) -> str:
    external = evaluation.get("external_novelty")
    if not isinstance(external, dict):
        return "missing"
    provenance = external.get("provenance")
    if not isinstance(provenance, dict):
        return "missing"
    return str(provenance.get("status") or "missing")


def _review_llm_status(evaluation: dict[str, Any]) -> str:
    review_llm = evaluation.get("review_llm")
    if not isinstance(review_llm, dict):
        return "missing"
    return str(review_llm.get("status") or "missing")


def _append_novelty_wiki_log(root: Path, idea_path: Path, score: int, evaluation: dict[str, Any]) -> Path:
    log_path = root / "log.md"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    idea_rel = _rel(idea_path)
    evidence_ids = ", ".join(str(item) for item in evaluation.get("evidence_ids") or []) or "N/A"
    entry = (
        "\n## Novelty Writeback\n\n"
        f"- {timestamp} | novelty | wrote novelty_score={score} | idea={idea_rel} | evidence={evidence_ids}\n"
    )
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(entry)
    return log_path


def _append_novelty_wiki_edge(root: Path, idea_path: Path, score: int, evaluation: dict[str, Any]) -> Path:
    edges_path = root / "graph" / "edges.jsonl"
    edges_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    evidence_ids = _unique_strings([str(item) for item in evaluation.get("evidence_ids") or []])
    edge = {
        "edge_type": "novelty_evaluated",
        "source_type": "idea",
        "source_id": str(evaluation.get("idea_id") or idea_path.stem),
        "source_path": _rel(idea_path),
        "relation": "has_novelty_score",
        "target_type": "novelty_evaluation",
        "target_id": str(evaluation.get("idea_id") or idea_path.stem),
        "novelty_score": score,
        "recommendation": str(evaluation.get("recommendation") or "N/A"),
        "evidence_ids": evidence_ids,
        "timestamp": timestamp,
    }
    line = json.dumps(edge, sort_keys=True)
    existing = set(edges_path.read_text(encoding="utf-8").splitlines()) if edges_path.exists() else set()
    if line not in existing:
        with edges_path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
    return edges_path


def _rebuild_wiki_mutation_views(root: Path, run_id: str, idea_path: Path, evaluation: dict[str, Any]) -> list[Path]:
    updated: list[Path] = []
    index_path = root / "index.md"
    lines = [
        "# Solar AutoSci Wiki\n\n",
        "Human-facing research memory projected from Solar-managed evidence and approved wiki mutations.\n\n",
        f"Last mutation run: `{run_id}`\n\n",
    ]
    for subdir in ["papers", "concepts", "methods", "people", "topics", "ideas", "experiments", "outputs"]:
        lines.append(f"## {subdir.title()}\n\n")
        pages = sorted((root / subdir).glob("*.md"))
        if not pages:
            lines.append("- N/A\n\n")
            continue
        for page in pages:
            lines.append(f"- [{page.stem}]({subdir}/{page.name})\n")
        lines.append("\n")
    index_body = "".join(lines)
    if _write_text_if_changed_bridge(index_path, index_body):
        updated.append(index_path)

    context_path = root / "graph" / "context_brief.md"
    evidence_ids = ", ".join(str(item) for item in evaluation.get("evidence_ids") or []) or "N/A"
    context_body = "\n".join(
        [
            "# Solar AutoSci Context Brief",
            "",
            f"Last mutation run: `{run_id}`",
            f"Updated at: `{datetime.now(UTC).replace(microsecond=0).isoformat().replace('+00:00', 'Z')}`",
            f"Mutation target: `{_rel(idea_path)}`",
            f"Evidence ids: {evidence_ids}",
            "",
            "Use `wiki/graph/edges.jsonl` for structured mutation edges.",
            "Use `artifacts/autosci/runs/` for Solar-managed execution evidence.",
            "",
        ]
    )
    if _write_text_if_changed_bridge(context_path, context_body):
        updated.append(context_path)
    return updated


def _write_text_if_changed_bridge(path: Path, content: str) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def _write_novelty_writeback_sidecar(envelope: dict[str, Any], evaluation_evidence: dict[str, Any]) -> str | None:
    inputs = dict(envelope.get("inputs") or {})
    native_options = inputs.get("native_options") if isinstance(inputs.get("native_options"), dict) else {}
    if not native_options.get("write"):
        return None

    path = _novelty_writeback_path(envelope)
    evaluations = list((evaluation_evidence.get("outputs") or {}).get("evaluations") or [])
    evaluation = next((item for item in evaluations if isinstance(item, dict)), {})
    idea_path, idea_slug, checked_paths = _target_idea_path_for_write(envelope)
    status = "inconclusive"
    write: dict[str, Any] = {
        "requested": True,
        "applied": False,
        "approval_ref": "cli --write",
        "idea_slug": idea_slug or "N/A",
        "checked_paths": checked_paths,
        "external_novelty_status": _external_novelty_status(evaluation) if isinstance(evaluation, dict) else "missing",
        "external_novelty_provenance_status": _external_novelty_provenance_status(evaluation) if isinstance(evaluation, dict) else "missing",
        "review_llm_status": _review_llm_status(evaluation) if isinstance(evaluation, dict) else "missing",
    }
    artifacts: list[dict[str, Any]] = []
    limitations: list[str] = []

    if not evaluation:
        limitations.append("No idea evaluation was available for novelty write-back.")
    elif str(evaluation.get("source_mode") or "") == "missing" or str(evaluation.get("recommendation") or "") == "inconclusive":
        limitations.append("Novelty write-back was skipped because evaluation evidence is inconclusive.")
    elif _external_novelty_status(evaluation) != "completed":
        limitations.append(
            "Novelty write-back was skipped because completed external novelty evidence is required before mutating wiki novelty_score."
        )
    elif _external_novelty_provenance_status(evaluation) != "passed":
        limitations.append(
            "Novelty write-back was skipped because external novelty provider provenance did not pass write-grade validation."
        )
    elif _review_llm_status(evaluation) != "completed":
        limitations.append(
            "Novelty write-back was skipped because completed Review LLM evidence is required before promotion-grade wiki mutation."
        )
    elif idea_path is None:
        limitations.append("Novelty write-back was skipped because the target did not resolve to an existing wiki idea file.")
    else:
        score = _novelty_score_from_evaluation(evaluation)
        if score is None:
            limitations.append("Novelty write-back was skipped because the evaluation did not include a numeric novelty score.")
        else:
            original = idea_path.read_text(encoding="utf-8", errors="replace")
            updated = _set_frontmatter_scalar(original, "novelty_score", str(score))
            if updated is None:
                limitations.append("Novelty write-back was skipped because the wiki idea file has no YAML frontmatter.")
            else:
                idea_path.write_text(updated, encoding="utf-8")
                wiki_root = next((root for root in _wiki_roots_for_write(envelope) if _path_is_under(idea_path, root)), idea_path.parent.parent)
                log_path = _append_novelty_wiki_log(wiki_root, idea_path, score, evaluation)
                edge_path = _append_novelty_wiki_edge(wiki_root, idea_path, score, evaluation)
                rebuild_paths = _rebuild_wiki_mutation_views(
                    wiki_root,
                    str(evaluation_evidence.get("sprint_id") or envelope.get("sprint_id") or "sprint-autosci"),
                    idea_path,
                    evaluation,
                )
                status = "completed"
                write.update(
                    {
                        "applied": True,
                        "idea_path": _rel(idea_path),
                        "log_path": _rel(log_path),
                        "edge_path": _rel(edge_path),
                        "rebuilt_paths": [_rel(path) for path in rebuild_paths],
                        "novelty_score": score,
                        "source_review_mode": evaluation.get("review_mode", "N/A"),
                        "source_recommendation": evaluation.get("recommendation", "N/A"),
                    }
                )
                artifacts.extend(
                    [
                        {"type": "wiki_idea", "path": _rel(idea_path)},
                        {"type": "wiki_log", "path": _rel(log_path)},
                        {"type": "wiki_graph_edges", "path": _rel(edge_path)},
                        *[{"type": "wiki_rebuild", "path": _rel(path)} for path in rebuild_paths],
                    ]
                )

    if not limitations:
        limitations.append(
            "Novelty write-back updates the targeted wiki idea frontmatter, appends a wiki log entry, "
            "adds a graph edge, and rebuilds lightweight wiki navigation/context."
        )

    evidence = {
        "schema": "novelty_writeback.v1",
        "task_id": f"{evaluation_evidence.get('task_id', 'task-evaluate-ideas')}:novelty-writeback",
        "sprint_id": str(evaluation_evidence.get("sprint_id") or envelope.get("sprint_id") or "sprint-autosci"),
        "node_id": f"{evaluation_evidence.get('node_id', 'node-evaluate-ideas')}:novelty-writeback",
        "status": status,
        "inputs": inputs,
        "outputs": {
            "write": write,
            "source_evaluation": {
                "idea_id": evaluation.get("idea_id", "N/A") if isinstance(evaluation, dict) else "N/A",
                "evidence_ids": list(evaluation.get("evidence_ids") or []) if isinstance(evaluation, dict) else [],
            },
        },
        "artifacts": artifacts,
        "provenance": {
            "operator_id": "autosci-bridge",
            "implementation_package": "plugins/autosci",
            "timestamp": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        },
        "limitations": limitations,
    }
    return _write_evidence_payload(path, evidence)


SAFE_EXPERIMENT_EXECUTION_MODES = {
    "fixture",
    "dry-run",
    "bounded",
    "bounded-local",
    "benchmark",
    "known-safe-benchmark",
    "human_approved",
    "approved-external",
}
APPROVAL_REQUIRED_EXPERIMENT_MODES = {"human_approved", "approved-external"}


def _fixture_like_envelope(envelope: dict[str, Any]) -> bool:
    inputs = dict(envelope.get("inputs") or {})
    return str(envelope.get("mode") or "") == "fixture" or bool(inputs.get("smoke_mode"))


def _experiment_plan_from_evidence(envelope: dict[str, Any]) -> dict[str, Any]:
    inputs = dict(envelope.get("inputs") or {})
    for key in ("experiment_plan_evidence", "plan_evidence", "experiment_plan"):
        payload = _load_optional_evidence(inputs.get(key))
        if not payload:
            continue
        if payload.get("schema") == "experiment_plan.v1":
            plan = ((payload.get("outputs") or {}).get("experiment_plan") or {})
            return dict(plan) if isinstance(plan, dict) else {}
        if isinstance(payload.get("experiment_plan"), dict):
            return dict(payload["experiment_plan"])
    return {}


def _experiment_result_payload(envelope: dict[str, Any]) -> dict[str, Any] | None:
    inputs = dict(envelope.get("inputs") or {})
    for key in ("experiment_result_evidence", "result_evidence", "experiment_result"):
        for payload in _load_optional_evidence_many(inputs.get(key)):
            return payload
    return None


def _experiment_execution_mode(envelope: dict[str, Any], plan: dict[str, Any] | None = None) -> str:
    inputs = dict(envelope.get("inputs") or {})
    return str(
        inputs.get("execution_mode")
        or (plan or {}).get("execution_mode")
        or envelope.get("mode")
        or "fixture"
    )


def _experiment_approval_satisfied(envelope: dict[str, Any]) -> bool:
    inputs = dict(envelope.get("inputs") or {})
    if inputs.get("approved") is True or inputs.get("human_approval") is True:
        return True
    approval_ref = str(inputs.get("approval_ref") or "").strip()
    return bool(approval_ref and approval_ref.upper() != "N/A")


def _experiment_log_artifact(envelope: dict[str, Any], experiment_id: str, log_lines: list[str]) -> dict[str, str]:
    output_dir = _output_dir(envelope, "run_experiment")
    path = output_dir / f"{_slug(experiment_id)}.log"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(log_lines).rstrip() + "\n", encoding="utf-8")
    return {"type": "experiment_run_log", "path": _rel(path)}


def _write_experiment_state_mutation(
    envelope: dict[str, Any],
    *,
    experiment_id: str,
    outcome: str,
    evidence_ids: list[str],
    metrics: list[dict[str, Any]],
) -> list[dict[str, str]]:
    root = _wiki_roots_for_write(envelope)[0]
    now = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    exp_dir = root / "experiments"
    graph_dir = root / "graph"
    exp_dir.mkdir(parents=True, exist_ok=True)
    graph_dir.mkdir(parents=True, exist_ok=True)
    exp_path = exp_dir / f"{_slug(experiment_id)}.md"
    metric_lines = [
        f"- {metric.get('name')}: {metric.get('value')}"
        for metric in metrics
        if isinstance(metric, dict) and str(metric.get("name") or "").strip()
    ]
    exp_path.write_text(
        "\n".join(
            [
                "---",
                f"experiment_id: {experiment_id}",
                "status: completed",
                f"outcome: {outcome}",
                f"updated_at: {now}",
                "evidence_ids:",
                *[f"  - {item}" for item in evidence_ids],
                "---",
                f"# {experiment_id}",
                "",
                "## Runtime Result",
                "",
                f"- Outcome: `{outcome}`",
                f"- Updated: `{now}`",
                "",
                "## Metrics",
                "",
                *(metric_lines or ["- N/A"]),
                "",
            ]
        ),
        encoding="utf-8",
    )
    log_path = root / "log.md"
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(f"- {now} | experiment | completed `{experiment_id}` outcome `{outcome}` evidence `{', '.join(evidence_ids)}`\n")
    edge_path = graph_dir / "edges.jsonl"
    with edge_path.open("a", encoding="utf-8") as handle:
        handle.write(
            json.dumps(
                {
                    "source": experiment_id,
                    "target": evidence_ids[0] if evidence_ids else f"runtime:{_slug(experiment_id)}",
                    "relation": "produced_result",
                    "operation": "add",
                    "evidence_ids": evidence_ids,
                    "timestamp": now,
                },
                sort_keys=True,
            )
            + "\n"
        )
    return [
        {"type": "wiki_experiment_state", "path": _rel(exp_path)},
        {"type": "wiki_log", "path": _rel(log_path)},
        {"type": "wiki_graph_edges", "path": _rel(edge_path)},
    ]


def _action_design_experiment(envelope: dict[str, Any]) -> dict[str, Any]:
    inputs = dict(envelope.get("inputs") or {})
    execution_mode = _experiment_execution_mode(envelope)
    wiki_state, wiki_state_artifact = _wiki_state_resolver_artifact(envelope, "design_experiment")
    wiki_artifacts = [wiki_state_artifact] if wiki_state_artifact else []
    raw_target = str(inputs.get("claim_or_idea_ref") or inputs.get("target") or "").strip()
    claim_id = str(inputs.get("claim_id") or "").strip()
    idea_id = str(inputs.get("idea_id") or "").strip()
    if not claim_id and raw_target.startswith("claim"):
        claim_id = raw_target
    if not idea_id and raw_target.startswith("idea"):
        idea_id = raw_target
    resolved_idea = _target_idea_from_wiki_state(wiki_state)
    if resolved_idea and not idea_id:
        idea_id = str(resolved_idea.get("idea_id") or "")
        raw_target = raw_target or idea_id
    if _fixture_like_envelope(envelope):
        claim_id = claim_id or "claim-001"
        idea_id = idea_id or "idea-001"
        raw_target = raw_target or claim_id or idea_id
    target_ref = raw_target or claim_id or idea_id
    if not target_ref:
        return convert_experiment_plan({
            "experiment_id": "experiment-unresolved",
            "objective": "No claim, idea, target, or experiment plan evidence was resolved for experiment design.",
            "hypothesis": "N/A",
            "variables": ["N/A"],
            "metrics": ["N/A"],
            "procedure": ["Resolve a concrete wiki idea, claim, or experiment plan before designing an experiment."],
            "approval_required": False,
            "expected_artifacts": [],
            "execution_mode": execution_mode,
            "baseline": "N/A",
            "baseline_absence_reason": "No target evidence was resolved.",
            "success_criteria": ["target evidence resolved"],
            "command_allowlist": [],
            "resource_limits": {"network": "denied", "write_scope": "none"},
            "status": "inconclusive",
            "artifacts": wiki_artifacts,
            "limitations": [
                "Experiment design was skipped because no target evidence was resolved; no default idea-001 fallback was used.",
                *_wiki_state_limitations(wiki_state),
            ],
        }, envelope)
    review_llm, review_evidence_ids, review_artifacts = _claim_review_llm_context(
        envelope,
        target_ref,
        artifact_type="experiment_design_review_llm_evidence_json",
    )
    approval_required = execution_mode in APPROVAL_REQUIRED_EXPERIMENT_MODES
    fixture_plan = execution_mode == "fixture" or _fixture_like_envelope(envelope)
    if fixture_plan:
        objective = f"Validate evidence coverage for `{target_ref}` using a bounded fixture experiment."
        hypothesis = "Fixture execution will emit result evidence, a ledger entry, and a monitorable status without external side effects."
        variables = ["execution_mode", "evidence_payload"]
        metrics = ["result_json_written", "evidence_jsonl_written", "fixture_passed"]
        procedure = [
            "Confirm the experiment plan evidence is present.",
            "Run the AutoSci bridge in fixture mode only.",
            "Record command, metrics, logs, and produced evidence paths.",
            "Validate experiment_result.v1 and experiment_status.v1 gates.",
        ]
        baseline = "previous fixture bridge run writes result.json and evidence.jsonl"
        baseline_absence_reason = ""
        success_criteria = [
            "result_json_written == true",
            "evidence_jsonl_written == true",
            "fixture_passed == true",
        ]
        resource_limits = {"network": "denied", "write_scope": "artifact_dir_only", "timeout_seconds": 30}
        limitations = ["Fixture experiment design is bounded to local bridge artifacts.", *_wiki_state_limitations(wiki_state)]
    else:
        objective = f"Validate evidence coverage for `{target_ref}` using an approval-gated native experiment."
        hypothesis = "A verified approved runtime will produce result artifacts without relying on surrogate outcomes."
        variables = ["execution_mode", "approval_contract", "runtime_evidence"]
        metrics = ["approval_present", "runtime_evidence_verified", "result_artifact_present"]
        procedure = [
            "Resolve the target idea, claim, or experiment plan evidence.",
            "Require explicit approval and allowlisted runtime command evidence before execution.",
            "Collect runtime logs, metrics, and produced result artifacts.",
            "Validate experiment_result.v1 and experiment_status.v1 from supplied runtime evidence.",
        ]
        baseline = "N/A"
        baseline_absence_reason = "No native runtime has executed yet."
        success_criteria = [
            "approval_present == true",
            "runtime_evidence_verified == true",
            "result_artifact_present == true",
        ]
        resource_limits = {"network": "requires_approval", "write_scope": "approved_artifact_dir_only", "timeout_seconds": 0}
        limitations = ["Approval-gated native experiment design; no command is executed by this planning action.", *_wiki_state_limitations(wiki_state)]
    if review_llm.get("status") == "completed":
        procedure.append("Attach completed Review LLM design validation before execution approval.")
        success_criteria.append("review_llm_design_validation == completed")
        limitations.append("Review LLM design validation evidence is attached; execution still requires explicit approval/runtime evidence.")
    elif _input_path_values(inputs, "review_llm_evidence", "review_evidence", "artifact_review_evidence"):
        limitations.append("Supplied Review LLM design validation evidence did not complete.")
    else:
        limitations.append("Review LLM design validation was not supplied.")
    native_experiment_id = _slug(target_ref)
    if not native_experiment_id.startswith(("exp-", "experiment-")):
        native_experiment_id = f"exp-{native_experiment_id}"
    return convert_experiment_plan({
        "experiment_id": "exp-001" if _fixture_like_envelope(envelope) else native_experiment_id,
        "objective": objective,
        "hypothesis": hypothesis,
        "variables": variables,
        "metrics": metrics,
        "procedure": procedure,
        "approval_required": approval_required,
        "expected_artifacts": ["experiment_result.json", "experiment_status.json", "experiment_run.log"],
        "execution_mode": execution_mode,
        "baseline": baseline,
        "baseline_absence_reason": baseline_absence_reason,
        "success_criteria": success_criteria,
        "command_allowlist": [
            "python3 plugins/autosci/bin/autosci_bridge.py run --action run_experiment",
            "python3 plugins/autosci/bin/autosci_bridge.py run --action monitor_experiment",
        ],
        "resource_limits": resource_limits,
        "review_llm": review_llm,
        "evidence_ids": _unique_strings([target_ref, *review_evidence_ids]),
        "artifacts": [*wiki_artifacts, *review_artifacts],
        "limitations": limitations,
    }, envelope)


def _action_run_experiment(envelope: dict[str, Any]) -> dict[str, Any]:
    inputs = dict(envelope.get("inputs") or {})
    plan = _experiment_plan_from_evidence(envelope)
    execution_mode = _experiment_execution_mode(envelope, plan)
    target_ref = str(inputs.get("experiment_id") or inputs.get("target") or "").strip()
    experiment_id = str(
        plan.get("experiment_id")
        or target_ref
        or ("exp-001" if _fixture_like_envelope(envelope) else "experiment-unresolved")
    )
    command_allowlist = list(plan.get("command_allowlist") or [])
    command_run = str(command_allowlist[0] if command_allowlist else "fixture-mode:no-external-command")
    evidence_ids = [experiment_id, str(plan.get("objective") or "experiment-plan")]
    raw = dict(_load_json(_fixture_path("sample_autosci_raw_experiment_result.json")))
    supplied_result = _experiment_result_payload(envelope)
    if supplied_result and supplied_result.get("schema") != "experiment_result.v1":
        raw.update(supplied_result)

    log_lines = [
        f"execution_mode={execution_mode}",
        f"experiment_id={experiment_id}",
        f"command_run={command_run}",
    ]
    if experiment_id == "experiment-unresolved" and not plan and not target_ref:
        log_lines.append("blocked missing experiment plan evidence")
        artifact = _experiment_log_artifact(envelope, experiment_id, log_lines)
        return convert_experiment_result({
            "experiment_id": experiment_id,
            "outcome": "inconclusive",
            "status": "inconclusive",
            "metrics": [{"name": "experiment_plan_resolved", "value": False}],
            "evidence_ids": ["experiment-plan:missing"],
            "execution_mode": execution_mode,
            "command_run": command_run,
            "logs": log_lines,
            "artifacts": [artifact],
            "limitations": ["Experiment execution was skipped because no experiment plan evidence was resolved; no default exp-001 fallback was used."],
        }, envelope)
    if execution_mode not in SAFE_EXPERIMENT_EXECUTION_MODES:
        log_lines.append(f"blocked unsupported execution mode: {execution_mode}")
        artifact = _experiment_log_artifact(envelope, experiment_id, log_lines)
        return convert_experiment_result({
            "experiment_id": experiment_id,
            "outcome": "failed",
            "status": "failed",
            "metrics": [{"name": "execution_allowed", "value": False}],
            "evidence_ids": evidence_ids,
            "execution_mode": execution_mode,
            "command_run": command_run,
            "logs": log_lines,
            "artifacts": [artifact],
            "limitations": [f"Unsupported execution mode: {execution_mode}"],
        }, envelope)

    approval_required = execution_mode in APPROVAL_REQUIRED_EXPERIMENT_MODES or bool(plan.get("approval_required"))
    if approval_required:
        contract = _approval_contract(
            envelope,
            "run_experiment",
            ["local_process_launch", "remote_execution", "result_collection", "wiki_state_mutation"],
        )
        contract_artifact = _write_approval_contract_sidecar(envelope, "run_experiment", contract)
        runtime_artifacts = _contract_existing_artifacts(contract, "runtime_evidence", "experiment_runtime_evidence_json")
        if not _experiment_approval_satisfied(envelope):
            log_lines.append("blocked missing approval for non-fixture execution")
            artifact = _experiment_log_artifact(envelope, experiment_id, log_lines)
            blocked_status = "inconclusive" if execution_mode == "human_approved" else "failed"
            return convert_experiment_result({
                "experiment_id": experiment_id,
                "outcome": blocked_status,
                "status": blocked_status,
                "metrics": [{"name": "approval_present", "value": False}],
                "evidence_ids": evidence_ids,
                "execution_mode": execution_mode,
                "command_run": command_run,
                "logs": log_lines,
                "artifacts": [artifact, contract_artifact, *runtime_artifacts],
                "limitations": [
                    "Experiment execution was blocked because approval is required and absent; no experiment command was executed.",
                    *_approval_contract_limitations(contract),
                ],
            }, envelope)
        contract, executor_result = _execute_experiment_if_approved(envelope, contract, plan)
        semantic = _approval_semantic_runtime(contract, "run_experiment")
        contract["semantic_runtime"] = semantic
        runtime_artifacts = _contract_existing_artifacts(contract, "runtime_evidence", "experiment_runtime_evidence_json")
        detail = semantic.get("detail") if isinstance(semantic.get("detail"), dict) else {}
        if not semantic.get("verified"):
            log_lines.extend([
                f"approval_state={contract.get('approval_state')}",
                f"runtime_semantic_status={semantic.get('status')}",
                "blocked missing verified runtime evidence for approval-gated execution",
            ])
            artifact = _experiment_log_artifact(envelope, experiment_id, log_lines)
            return convert_experiment_result({
                "experiment_id": experiment_id,
                "outcome": "inconclusive",
                "status": "inconclusive",
                "metrics": [
                    {"name": "approval_present", "value": True},
                    {"name": "runtime_evidence_verified", "value": False},
                ],
                "evidence_ids": evidence_ids,
                "execution_mode": execution_mode,
                "command_run": command_run,
                "logs": log_lines,
                "artifacts": [artifact, contract_artifact, *runtime_artifacts],
                "limitations": [
                    "Experiment execution was not marked complete because approval/runtime evidence did not pass semantic verification.",
                    *_approval_contract_limitations(contract),
                ],
            }, envelope)
        if executor_result.get("executed"):
            log_lines.append(f"experiment_executor_result={executor_result.get('result_collected')}")
            log_lines.append(f"executor_exit_code={executor_result.get('exit_code')}")
            if executor_result.get("result_path"):
                log_lines.append(f"executor_result_path={executor_result.get('result_path')}")
        runtime_metrics = detail.get("metrics") if isinstance(detail.get("metrics"), list) else []
        metrics = runtime_metrics or [{"name": "runtime_evidence_verified", "value": True}]
        outcome = str(detail.get("outcome") or "supports")
        runtime_evidence_ids = [str(item) for item in detail.get("evidence_ids") or [] if str(item).strip()]
        completed_evidence_ids = _unique_strings([*evidence_ids, *runtime_evidence_ids])
        command_run = str(detail.get("command_run") or command_run)
        runtime_logs = [str(item) for item in detail.get("logs") or [] if str(item).strip()]
        result_path = executor_result.get("result_path")
        if result_path:
            result_payload = _load_json(_resolve_harness_path(result_path))
            result_logs = (result_payload.get("outputs") or {}).get("result", {}).get("logs")
            if isinstance(result_logs, list):
                for item in result_logs:
                    text = str(item).strip()
                    if text and text not in runtime_logs:
                        runtime_logs.append(text)
        runtime_artifacts.extend(_contract_existing_artifacts(contract, "after_artifacts", "run_experiment_result_json"))
        for key, artifact_type in (
            ("stdout_path", "executor_stdout"),
            ("stderr_path", "executor_stderr"),
        ):
            raw_path = str(executor_result.get(key) or "").strip()
            if raw_path:
                artifact_path = _resolve_harness_path(raw_path)
                if artifact_path.exists():
                    runtime_artifacts.append({"type": artifact_type, "path": _rel(artifact_path)})
        logs = [
            *log_lines,
            f"approval_state={contract.get('approval_state')}",
            "approved runtime evidence verified",
            *runtime_logs,
        ]
        artifact = _experiment_log_artifact(envelope, experiment_id, logs)
        wiki_artifacts = _write_experiment_state_mutation(
            envelope,
            experiment_id=experiment_id,
            outcome=outcome,
            evidence_ids=completed_evidence_ids,
            metrics=metrics,
        )
        return convert_experiment_result({
            "experiment_id": experiment_id,
            "outcome": outcome,
            "status": "completed",
            "metrics": metrics,
            "evidence_ids": completed_evidence_ids,
            "execution_mode": execution_mode,
            "command_run": command_run,
            "logs": logs,
            "artifacts": [artifact, contract_artifact, *runtime_artifacts, *wiki_artifacts],
            "limitations": [
                "Experiment result was completed from approved runtime evidence and mutated wiki state.",
            ],
        }, envelope)

    raw["experiment_id"] = str(raw.get("experiment_id") or experiment_id)
    raw["execution_mode"] = execution_mode
    raw["command_run"] = command_run
    raw["logs"] = [*log_lines, "fixture result collected"]
    raw["evidence_ids"] = list(raw.get("evidence_ids") or evidence_ids)
    raw["artifacts"] = [_experiment_log_artifact(envelope, experiment_id, raw["logs"])]
    raw["limitations"] = list(raw.get("limitations") or ["Fixture result is deterministic and not a real benchmark run."])
    return convert_experiment_result(raw, envelope)


def _action_run_pilot_experiment(envelope: dict[str, Any]) -> dict[str, Any]:
    inputs = dict(envelope.get("inputs") or {})
    target = str(inputs.get("target") or inputs.get("experiment_id") or "pilot-unresolved")
    experiment_id = target if target.startswith("exp") or target.startswith("pilot") else f"pilot-{_slug(target)}"
    contract = _approval_contract(
        envelope,
        "run_pilot_experiment",
        ["local_process_launch", "remote_execution", "result_collection"],
    )
    semantic = _approval_semantic_runtime(contract, "run_pilot_experiment")
    contract["semantic_runtime"] = semantic
    contract_artifact = _write_approval_contract_sidecar(envelope, "run_pilot_experiment", contract)
    semantic_detail = semantic.get("detail") if isinstance(semantic.get("detail"), dict) else {}
    runtime_metrics = semantic_detail.get("metrics") if isinstance(semantic_detail.get("metrics"), list) else []
    metrics = runtime_metrics or [
        {"name": "pilot_execution_started", "value": False},
        {"name": "approval_contract_verified", "value": bool(contract.get("execution_verified"))},
        {"name": "runtime_semantic_verified", "value": bool(semantic.get("verified"))},
    ]
    outcome = str(semantic_detail.get("outcome") or "inconclusive")
    status = "completed" if semantic.get("verified") else "inconclusive"
    limitations = [
        "Pilot run is diagnostics-only unless approved runtime evidence is supplied.",
        "This bridge did not launch local or remote experiment commands.",
    ]
    if semantic.get("verified"):
        limitations = [
            "Pilot runtime was verified from supplied approval-gated evidence; this bridge did not execute the command.",
        ]
    else:
        limitations.extend(_approval_contract_limitations(contract))
    return convert_experiment_result({
        "experiment_id": experiment_id,
        "outcome": outcome,
        "status": status,
        "metrics": metrics,
        "evidence_ids": [f"pilot-run:{_slug(target)}"],
        "execution_mode": str(inputs.get("execution_mode") or "approval_gated_pilot"),
        "command_run": "approval-gated:no-external-command",
        "logs": [
            "Pilot execution was not started by this bridge.",
            "Approved runtime evidence was verified." if semantic.get("verified") else "Code execution, local process launch, remote execution, and result collection require approval.",
            f"approval_state={contract.get('approval_state')}",
            f"runtime_semantic_status={semantic.get('status')}",
        ],
        "artifacts": [contract_artifact],
        "limitations": limitations,
    }, envelope)


def _action_monitor_experiment(envelope: dict[str, Any]) -> dict[str, Any]:
    inputs = dict(envelope.get("inputs") or {})
    plan = _experiment_plan_from_evidence(envelope)
    result_payload = _experiment_result_payload(envelope)
    wiki_state, wiki_state_artifact = _wiki_state_resolver_artifact(envelope, "monitor_experiment")
    wiki_artifacts = [wiki_state_artifact] if wiki_state_artifact else []
    target_ref = str(inputs.get("target") or inputs.get("experiment_id") or "").strip()
    resolved_experiment_id = _resolved_wiki_experiment_id(wiki_state)
    experiment_id = str(
        plan.get("experiment_id")
        or resolved_experiment_id
        or target_ref
        or ("exp-001" if _fixture_like_envelope(envelope) else "experiment-unresolved")
    )
    collect_requested = bool(inputs.get("collect"))
    if result_payload and result_payload.get("schema") == "experiment_result.v1":
        result = ((result_payload.get("outputs") or {}).get("result") or {})
        experiment_id = str(result.get("experiment_id") or experiment_id)
        outcome = str(result.get("outcome") or "inconclusive")
        state = "failed" if outcome == "failed" or result_payload.get("status") == "failed" else "completed"
        evidence_ids = [str(result_payload.get("task_id") or experiment_id), *list(result.get("evidence_ids") or [])]
        return convert_experiment_status({
            "experiment_id": experiment_id,
            "state": state,
            "observations": [f"Observed experiment result outcome: {outcome}."],
            "next_actions": ["Collect result evidence for claim verification." if state == "completed" else "Inspect failed run logs before retry."],
            "evidence_ids": evidence_ids,
            "artifacts": wiki_artifacts,
            "limitations": ["Status is derived from local result evidence only.", *_wiki_state_limitations(wiki_state)],
        }, envelope)
    if result_payload:
        experiment_id = str(result_payload.get("experiment_id") or experiment_id)
        outcome = str(result_payload.get("outcome") or "inconclusive")
        state = "failed" if outcome == "failed" else "completed"
        return convert_experiment_status({
            "experiment_id": experiment_id,
            "state": state,
            "observations": [f"Observed raw fixture result outcome: {outcome}."],
            "next_actions": ["Convert raw result to experiment_result.v1 evidence."],
            "evidence_ids": list(result_payload.get("evidence_ids") or [experiment_id]),
            "artifacts": wiki_artifacts,
            "limitations": [
                "Status was derived from a raw fixture result, not a persisted result evidence artifact.",
                *_wiki_state_limitations(wiki_state),
            ],
        }, envelope)
    wiki_experiment = _resolved_wiki_experiment(wiki_state)
    if wiki_experiment and not collect_requested and not inputs.get("runtime_evidence"):
        experiment_id = str(wiki_experiment.get("experiment_id") or experiment_id)
        raw_status = str(wiki_experiment.get("status") or "")
        state = _experiment_state_from_wiki_status(raw_status)
        outcome = str(wiki_experiment.get("outcome") or "").strip()
        experiment_path = str(wiki_experiment.get("path") or "").strip()
        run_log_path = str(wiki_experiment.get("run_log_path") or "").strip()
        evidence_ids = _unique_strings(
            [
                experiment_id,
                experiment_path,
                run_log_path if wiki_experiment.get("run_log_exists") else "",
                *[str(item) for item in wiki_experiment.get("evidence_ids") or [] if str(item).strip()],
            ]
        )
        experiment_artifacts = list(wiki_artifacts)
        if experiment_path:
            experiment_artifacts.append({"type": "wiki_experiment_markdown", "path": experiment_path})
        if run_log_path and wiki_experiment.get("run_log_exists"):
            experiment_artifacts.append({"type": "wiki_experiment_run_log", "path": run_log_path})
        observations = [f"Resolved wiki experiment `{experiment_id}` with status `{raw_status or 'unknown'}`."]
        if outcome:
            observations.append(f"Wiki experiment outcome: {outcome}.")
        if run_log_path:
            observations.append(
                "Wiki experiment run log exists." if wiki_experiment.get("run_log_exists") else "Wiki experiment run log path is recorded but missing."
            )
        next_actions = (
            ["Use linked run/result evidence for claim verification and reporting."]
            if state == "completed"
            else ["Supply experiment_result.v1 or approved runtime evidence before treating results as collected."]
        )
        status = "completed" if state != "unknown" else "inconclusive"
        limitations = [
            "Experiment status was read from wiki experiment state; no command was executed and no remote results were collected.",
            *_wiki_state_limitations(wiki_state),
        ]
        if not evidence_ids:
            evidence_ids = [experiment_id or "wiki-experiment:missing-evidence"]
        return convert_experiment_status({
            "experiment_id": experiment_id,
            "state": state,
            "observations": observations,
            "next_actions": next_actions,
            "evidence_ids": evidence_ids,
            "status": status,
            "artifacts": experiment_artifacts,
            "limitations": limitations,
        }, envelope)
    if collect_requested or inputs.get("runtime_evidence"):
        contract = _approval_contract(
            envelope,
            "monitor_experiment",
            ["result_collection", "status_mutation", "wiki_state_mutation"],
        )
        semantic = _approval_semantic_runtime(contract, "run_experiment")
        contract["semantic_runtime"] = semantic
        contract_artifact = _write_approval_contract_sidecar(envelope, "monitor_experiment", contract)
        runtime_artifacts = _contract_existing_artifacts(contract, "runtime_evidence", "experiment_runtime_evidence_json")
        detail = semantic.get("detail") if isinstance(semantic.get("detail"), dict) else {}
        runtime_evidence_ids = [str(item) for item in detail.get("evidence_ids") or [] if str(item).strip()]
        evidence_ids = _unique_strings([experiment_id, *runtime_evidence_ids])
        if semantic.get("verified"):
            outcome = str(detail.get("outcome") or "supports")
            state = "failed" if outcome == "failed" else "completed"
            metrics = detail.get("metrics") if isinstance(detail.get("metrics"), list) else []
            wiki_update_artifacts = _write_experiment_state_mutation(
                envelope,
                experiment_id=experiment_id,
                outcome=outcome,
                evidence_ids=evidence_ids,
                metrics=metrics,
            )
            return convert_experiment_status({
                "experiment_id": experiment_id,
                "state": state,
                "observations": [
                    f"Approved runtime evidence verified experiment outcome: {outcome}.",
                    f"approval_state={contract.get('approval_state')}",
                    f"runtime_semantic_status={semantic.get('status')}",
                ],
                "next_actions": ["Use collected result evidence for claim verification and paper reporting."],
                "evidence_ids": evidence_ids,
                "artifacts": [*wiki_artifacts, contract_artifact, *runtime_artifacts, *wiki_update_artifacts],
                "limitations": [
                    "Experiment status was completed from approved runtime evidence; this bridge verified evidence and mutated wiki state but did not pull remote results directly.",
                    *_wiki_state_limitations(wiki_state),
                ],
            }, envelope)
        if inputs.get("runtime_evidence") or inputs.get("approval_ref"):
            return convert_experiment_status({
                "experiment_id": experiment_id,
                "state": "unknown",
                "observations": [
                    "Runtime evidence was supplied but did not pass semantic verification.",
                    f"approval_state={contract.get('approval_state')}",
                    f"runtime_semantic_status={semantic.get('status')}",
                ],
                "next_actions": ["Supply verified runtime evidence with exit_code=0 and collected result metrics."],
                "evidence_ids": evidence_ids or [experiment_id, "runtime-evidence:unverified"],
                "status": "inconclusive",
                "artifacts": [*wiki_artifacts, contract_artifact, *runtime_artifacts],
                "limitations": [
                    "Collect/status remains inconclusive because approved runtime evidence did not pass semantic verification.",
                    *_approval_contract_limitations(contract),
                    *_wiki_state_limitations(wiki_state),
                ],
            }, envelope)
    observations = []
    if target_ref:
        observations.append(f"Status target requested: {target_ref}.")
    if collect_requested:
        observations.append("Collect mode was requested, but no local experiment_result.v1 evidence was supplied.")
    observations.append("No experiment result evidence was available to monitor.")
    next_actions = [
        "Provide experiment_result_evidence from the run artifact directory.",
        "Use an approved remote pull-results path before marking collect as complete.",
    ]
    limitations = ["Experiment status is unknown because result evidence is missing; no default exp-001 fallback was used."]
    if collect_requested:
        limitations.append("Collect mode is diagnostics-only without approved runtime artifact retrieval.")
    limitations.extend(_wiki_state_limitations(wiki_state))
    return convert_experiment_status({
        "experiment_id": experiment_id,
        "state": "unknown",
        "observations": observations,
        "next_actions": next_actions,
        "evidence_ids": [
            experiment_id if experiment_id != "experiment-unresolved" else "experiment-result:missing",
            "experiment-result:missing",
        ],
        "status": "inconclusive",
        "artifacts": wiki_artifacts,
        "limitations": limitations,
    }, envelope)


def _action_evaluate_pilot_result(envelope: dict[str, Any]) -> dict[str, Any]:
    inputs = dict(envelope.get("inputs") or {})
    claim_id = str(inputs.get("claim_id") or inputs.get("target") or "pilot-claim-unresolved")
    result_payload = _experiment_result_payload(envelope)
    artifacts: list[dict[str, str]] = []
    outcome = "inconclusive"
    basis = "Pilot-specific result evidence was not supplied; no wiki idea update was applied."
    evidence_ids = [claim_id, f"pilot-eval:{_slug(claim_id)}"]
    metrics: list[dict[str, Any]] = []

    if result_payload and result_payload.get("schema") == "experiment_result.v1":
        result = ((result_payload.get("outputs") or {}).get("result") or {})
        outcome = str(result.get("outcome") or result_payload.get("status") or "inconclusive")
        evidence_ids = _unique_strings(
            [
                claim_id,
                str(result_payload.get("task_id") or ""),
                *[str(item) for item in result.get("evidence_ids") or [] if str(item).strip()],
            ]
        )
        metrics = result.get("metrics") if isinstance(result.get("metrics"), list) else []
        basis = f"Pilot verdict derived from experiment_result.v1 outcome `{outcome}`."
    elif inputs.get("runtime_evidence"):
        runtime_entries = _approval_path_entries(inputs.get("runtime_evidence"))
        runtime_contract = {"runtime_evidence": runtime_entries}
        records, errors = _runtime_records(runtime_contract)
        artifacts.extend(_contract_existing_artifacts(runtime_contract, "runtime_evidence", "pilot_runtime_evidence_json"))
        if records and not errors:
            record = records[0]
            raw_outcome = str(_field(record, "outcome", "result", "verdict") or "").strip()
            exit_code = _field(record, "exit_code", "returncode")
            if raw_outcome:
                outcome = raw_outcome
            elif str(exit_code).strip() == "0":
                outcome = "supports"
            elif str(exit_code).strip():
                outcome = "failed"
            metrics = _runtime_metrics(record)
            evidence_ids = _unique_strings([claim_id, *_runtime_evidence_ids(records)])
            basis = f"Pilot verdict derived from supplied runtime evidence outcome `{outcome}`."
        else:
            basis = "Pilot runtime evidence was supplied but could not be loaded cleanly."

    verdict = {
        "supports": "supported",
        "supported": "supported",
        "partially_supports": "partially_supported",
        "partial": "partially_supported",
        "refutes": "not_supported",
        "not_supported": "not_supported",
        "failed": "inconclusive",
        "inconclusive": "inconclusive",
    }.get(outcome, "inconclusive")
    status = "completed" if verdict != "inconclusive" else "inconclusive"
    limitations = [
        "Pilot evaluation is lenient and bounded to supplied local result/runtime evidence.",
        "Pilot wiki writes remain proposed-only until explicitly approved.",
    ]
    if status != "completed":
        limitations.append("Pilot evaluation remains inconclusive because result/runtime evidence is missing or non-supportive.")
    verdict_evidence = convert_claim_verdict({
        "claim_id": claim_id,
        "verdict": verdict,
        "confidence": 0.58 if verdict == "supported" else 0.48 if verdict == "partially_supported" else 0.42 if verdict == "not_supported" else 0.2,
        "basis": basis,
        "evidence_ids": evidence_ids,
        "claim_evidence_ids": [claim_id],
        "experiment_evidence_ids": [item for item in evidence_ids if item != claim_id],
        "code_evidence_ids": [],
        "evidence_outcome": outcome,
        "metrics": metrics,
        "status": status,
        "artifacts": artifacts,
        "limitations": limitations,
    }, envelope)
    writeback_path = _write_claim_verdict_writeback_sidecar(envelope, verdict_evidence, require_review_llm=False)
    if writeback_path:
        verdict_evidence.setdefault("artifacts", []).append({"type": "pilot_verdict_writeback_json", "path": writeback_path})
    return verdict_evidence


def _claim_under_verification(envelope: dict[str, Any]) -> dict[str, Any]:
    inputs = dict(envelope.get("inputs") or {})
    claim_id = str(inputs.get("claim_id") or inputs.get("target") or "claim-001")
    for claim in _claims_from_evidence(envelope):
        if str(claim.get("claim_id") or "") == claim_id:
            return dict(claim)
    return {"claim_id": claim_id, "text": "Claim text unavailable in supplied evidence.", "evidence_ids": [claim_id]}


def _claim_verdict_code_evidence_ids(envelope: dict[str, Any], claim_id: str) -> list[str]:
    inputs = dict(envelope.get("inputs") or {})
    ids: list[str] = []
    for key in ("code_evidence", "code_evidence_map", "code_evidence_evidence"):
        for payload in _load_optional_evidence_many(inputs.get(key)):
            if payload.get("task_id"):
                ids.append(str(payload["task_id"]))
            mappings = ((payload.get("outputs") or {}).get("mappings") or [])
            for mapping in mappings if isinstance(mappings, list) else []:
                if not isinstance(mapping, dict):
                    continue
                if str(mapping.get("claim_id") or claim_id) != claim_id:
                    continue
                if mapping.get("mapping_id"):
                    ids.append(str(mapping["mapping_id"]))
                for field in ("files", "evidence_ids"):
                    values = mapping.get(field)
                    if isinstance(values, list):
                        ids.extend(str(item) for item in values if str(item).strip())
    seen: set[str] = set()
    unique: list[str] = []
    for item in ids:
        if item not in seen:
            seen.add(item)
            unique.append(item)
    return unique


def _claim_review_llm_context(
    envelope: dict[str, Any],
    claim_id: str,
    *,
    artifact_type: str = "claim_review_llm_evidence_json",
) -> tuple[dict[str, Any], list[str], list[dict[str, str]]]:
    inputs = dict(envelope.get("inputs") or {})
    paths = _input_path_values(inputs, "review_llm_evidence", "review_evidence", "artifact_review_evidence")
    artifacts: list[dict[str, str]] = []
    checked_paths: list[str] = []
    reasons: list[str] = []
    for raw in paths:
        path = _resolve_harness_path(raw)
        checked_paths.append(_rel(path))
        if not path.exists() or not path.is_file():
            reasons.append(f"missing review evidence: {raw}")
            continue
        artifacts.append({"type": artifact_type, "path": _rel(path)})
        try:
            payload = _load_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            reasons.append(f"invalid review evidence JSON: {_rel(path)}: {exc}")
            continue
        if not isinstance(payload, dict):
            reasons.append(f"review evidence is not a JSON object: {_rel(path)}")
            continue
        outputs = payload.get("outputs") if isinstance(payload.get("outputs"), dict) else {}
        review = outputs.get("review") if isinstance(outputs.get("review"), dict) else payload.get("review")
        if not isinstance(review, dict):
            reasons.append(f"review evidence lacks outputs.review: {_rel(path)}")
            continue
        review_llm = review.get("review_llm") if isinstance(review.get("review_llm"), dict) else {}
        completed = (
            str(payload.get("status") or "") == "completed"
            and str(review.get("review_mode") or "") == "review_llm"
            and review.get("review_available") is True
            and str(review_llm.get("status") or "completed") == "completed"
        )
        evidence_ids = _unique_strings(
            [
                str(payload.get("task_id") or ""),
                *[str(item) for item in review.get("evidence_ids") or []],
            ]
        )
        findings = outputs.get("findings") if isinstance(outputs.get("findings"), list) else []
        if completed:
            return (
                {
                    "status": "completed",
                    "source_path": _rel(path),
                    "claim_id": claim_id,
                    "review_mode": "review_llm",
                    "review_available": True,
                    "score": review.get("score", "N/A"),
                    "recommendation": str(review.get("recommendation") or "N/A"),
                    "difficulty": str(review.get("difficulty") or "N/A"),
                    "focus": str(review.get("focus") or "N/A"),
                    "evidence_ids": evidence_ids,
                    "finding_count": len(findings),
                    "review_llm": review_llm or {"status": "completed"},
                    "checked_paths": checked_paths,
                },
                evidence_ids,
                artifacts,
            )
        reasons.append(f"review evidence was not completed Review LLM evidence: {_rel(path)}")
    return (
        {
            "status": "unavailable" if not paths else "inconclusive",
            "claim_id": claim_id,
            "checked_paths": checked_paths,
            "reasons": reasons or ["No Review LLM evidence was supplied."],
        },
        [],
        artifacts,
    )


def _claim_verdict_experiment_context(envelope: dict[str, Any]) -> tuple[str, list[str], str, str]:
    payload = _experiment_result_payload(envelope)
    if not payload:
        return (
            "inconclusive",
            [],
            "No experiment result evidence was supplied.",
            "missing-experiment-result",
        )
    if payload.get("schema") == "experiment_result.v1":
        result = ((payload.get("outputs") or {}).get("result") or {})
        outcome = str(result.get("outcome") or "inconclusive")
        if payload.get("status") in {"failed", "inconclusive"}:
            outcome = str(payload.get("status"))
        experiment_id = str(result.get("experiment_id") or payload.get("task_id") or "experiment-result")
        evidence_ids = [
            str(payload.get("task_id") or ""),
            experiment_id,
            *[str(item) for item in (result.get("evidence_ids") or []) if str(item).strip()],
        ]
        basis = f"Verdict derived from experiment_result.v1 outcome `{outcome}` for `{experiment_id}`."
        return outcome, [item for item in evidence_ids if item], basis, experiment_id
    outcome = str(payload.get("outcome") or "inconclusive")
    experiment_id = str(payload.get("experiment_id") or "raw-experiment-result")
    evidence_ids = [experiment_id, *[str(item) for item in (payload.get("evidence_ids") or []) if str(item).strip()]]
    basis = f"Verdict derived from raw fixture experiment outcome `{outcome}` for `{experiment_id}`."
    return outcome, evidence_ids, basis, experiment_id


def _verdict_confidence(verdict: str, outcome: str) -> float:
    if verdict == "supported":
        return 0.72
    if verdict == "partially_supported":
        return 0.58
    if verdict == "not_supported":
        return 0.66
    if outcome == "failed":
        return 0.24
    return 0.32


def _action_verify_claim(envelope: dict[str, Any]) -> dict[str, Any]:
    claim = _claim_under_verification(envelope)
    claim_id = str(claim.get("claim_id") or "claim-001")
    outcome, experiment_ids, basis, experiment_id = _claim_verdict_experiment_context(envelope)
    review_llm, review_evidence_ids, review_artifacts = _claim_review_llm_context(envelope, claim_id)
    verdict = {
        "supports": "supported",
        "partially_supports": "partially_supported",
        "refutes": "not_supported",
        "not_supported": "not_supported",
        "inconclusive": "inconclusive",
        "failed": "inconclusive",
    }.get(outcome, "inconclusive")
    claim_evidence_ids = [claim_id, *[str(item) for item in (claim.get("evidence_ids") or []) if str(item).strip()]]
    code_evidence_ids = _claim_verdict_code_evidence_ids(envelope, claim_id)
    evidence_ids = [*claim_evidence_ids, *experiment_ids, *code_evidence_ids, *review_evidence_ids]
    if not experiment_ids:
        verdict = "inconclusive"
    seen: set[str] = set()
    unique_evidence_ids: list[str] = []
    for item in evidence_ids:
        if item and item not in seen:
            seen.add(item)
            unique_evidence_ids.append(item)
    limitations = [
        "Fixture verdict is derived only from supplied local evidence; it is not external scientific validation."
    ]
    if verdict == "inconclusive":
        limitations.append("Supplied experiment evidence is missing, failed, or inconclusive; the claim was not upgraded.")
    if review_llm.get("status") == "completed":
        basis = (
            f"{basis} Review LLM evidence `{review_llm.get('source_path')}` was attached "
            f"with recommendation `{review_llm.get('recommendation')}`."
        )
        limitations.append("Review LLM evidence is attached as an independent second opinion; verdict outcome still follows experiment evidence.")
    else:
        limitations.append("Review LLM second-opinion evidence was not supplied or did not complete.")
    verdict_evidence = convert_claim_verdict({
        "claim_id": claim_id,
        "verdict": verdict,
        "confidence": _verdict_confidence(verdict, outcome),
        "basis": f"{basis} Claim text: {claim.get('text', 'N/A')}",
        "evidence_ids": unique_evidence_ids,
        "claim_evidence_ids": claim_evidence_ids,
        "experiment_evidence_ids": experiment_ids,
        "code_evidence_ids": code_evidence_ids,
        "evidence_outcome": outcome,
        "experiment_id": experiment_id,
        "review_llm": review_llm,
        "artifacts": review_artifacts,
        "limitations": limitations,
    }, envelope)
    writeback_path = _write_claim_verdict_writeback_sidecar(envelope, verdict_evidence)
    if writeback_path:
        verdict_evidence.setdefault("artifacts", []).append({"type": "claim_verdict_writeback_json", "path": writeback_path})
    return verdict_evidence


def _claim_verdict_writeback_path(envelope: dict[str, Any]) -> Path:
    return _output_dir(envelope, "verify_claim") / "claim_verdict_writeback.json"


def _target_claim_verdict_path_for_write(envelope: dict[str, Any], claim_id: str) -> tuple[Path | None, str, list[str]]:
    inputs = dict(envelope.get("inputs") or {})
    target = str(inputs.get("target") or inputs.get("claim_id") or claim_id or "").strip()
    roots = _wiki_roots_for_write(envelope)
    candidates: list[Path] = []
    raw_path = Path(target)
    if raw_path.suffix.lower() in {".md", ".markdown"}:
        if raw_path.is_absolute():
            candidates.append(raw_path)
        else:
            for root in roots:
                candidates.extend([root / raw_path, root / "ideas" / raw_path.name, root / "experiments" / raw_path.name])
    else:
        slug = _slug(target or claim_id)
        for root in roots:
            candidates.extend([root / "ideas" / f"{slug}.md", root / "experiments" / f"{slug}.md"])
    checked: list[str] = []
    for candidate in candidates:
        checked.append(str(candidate))
        if not candidate.exists() or not candidate.is_file():
            continue
        if not any(_path_is_under(candidate, root) for root in roots):
            continue
        return candidate, _slug(candidate.stem), checked
    return None, _slug(target or claim_id), checked


def _append_claim_verdict_wiki_log(root: Path, target_path: Path, verdict: dict[str, Any]) -> Path:
    log_path = root / "log.md"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    evidence_ids = ", ".join(str(item) for item in verdict.get("evidence_ids") or []) or "N/A"
    entry = (
        "\n## Claim Verdict Writeback\n\n"
        f"- {timestamp} | claim-verdict | wrote verdict={verdict.get('verdict')} | "
        f"target={_rel(target_path)} | evidence={evidence_ids}\n"
    )
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(entry)
    return log_path


def _append_claim_verdict_wiki_edge(root: Path, target_path: Path, verdict: dict[str, Any]) -> Path:
    edges_path = root / "graph" / "edges.jsonl"
    edges_path.parent.mkdir(parents=True, exist_ok=True)
    edge = {
        "edge_type": "claim_verdict_written",
        "source_type": "claim",
        "source_id": str(verdict.get("claim_id") or "claim"),
        "relation": "has_claim_verdict",
        "target_type": "wiki_page",
        "target_path": _rel(target_path),
        "verdict": str(verdict.get("verdict") or "inconclusive"),
        "confidence": verdict.get("confidence", "N/A"),
        "evidence_ids": _unique_strings([str(item) for item in verdict.get("evidence_ids") or []]),
        "timestamp": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }
    with edges_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(edge, sort_keys=True) + "\n")
    return edges_path


def _write_claim_verdict_writeback_sidecar(
    envelope: dict[str, Any],
    verdict_evidence: dict[str, Any],
    *,
    require_review_llm: bool = True,
) -> str | None:
    inputs = dict(envelope.get("inputs") or {})
    native_options = inputs.get("native_options") if isinstance(inputs.get("native_options"), dict) else {}
    if not native_options.get("write"):
        return None
    path = _claim_verdict_writeback_path(envelope)
    verdicts = ((verdict_evidence.get("outputs") or {}).get("verdicts") or [])
    verdict = dict(verdicts[0]) if verdicts and isinstance(verdicts[0], dict) else {}
    claim_id = str(verdict.get("claim_id") or inputs.get("claim_id") or "claim")
    approval_ref = str(inputs.get("approval_ref") or native_options.get("approval_ref") or "").strip()
    review_llm = verdict.get("review_llm") if isinstance(verdict.get("review_llm"), dict) else {}
    target_path, target_slug, checked_paths = _target_claim_verdict_path_for_write(envelope, claim_id)
    status = "inconclusive"
    artifacts: list[dict[str, str]] = []
    limitations: list[str] = []
    write = {
        "requested": True,
        "applied": False,
        "approval_ref": approval_ref or "N/A",
        "claim_id": claim_id,
        "target_slug": target_slug,
        "checked_paths": checked_paths,
        "verdict": verdict.get("verdict", "N/A"),
        "review_llm_status": review_llm.get("status", "missing"),
    }

    if not approval_ref:
        limitations.append("Claim verdict write-back requires --approval-ref.")
    elif verdict.get("verdict") == "inconclusive":
        limitations.append("Claim verdict write-back requires a non-inconclusive verdict.")
    elif require_review_llm and review_llm.get("status") != "completed":
        limitations.append("Claim verdict write-back requires completed Review LLM evidence.")
    elif target_path is None:
        limitations.append("Claim verdict write-back target did not resolve to an existing wiki idea or experiment page.")
    else:
        original = target_path.read_text(encoding="utf-8", errors="replace")
        updated = _set_frontmatter_scalar(original, "claim_verdict", str(verdict.get("verdict") or "inconclusive"))
        if updated is not None:
            updated = _set_frontmatter_scalar(updated, "claim_verdict_confidence", str(verdict.get("confidence", "N/A"))) or updated
            updated = _set_frontmatter_scalar(updated, "claim_verdict_evidence", ",".join(str(item) for item in verdict.get("evidence_ids") or [])) or updated
        if updated is None:
            limitations.append("Claim verdict write-back target has no YAML frontmatter.")
        else:
            target_path.write_text(updated, encoding="utf-8")
            wiki_root = next((root for root in _wiki_roots_for_write(envelope) if _path_is_under(target_path, root)), target_path.parent.parent)
            log_path = _append_claim_verdict_wiki_log(wiki_root, target_path, verdict)
            edge_path = _append_claim_verdict_wiki_edge(wiki_root, target_path, verdict)
            rebuild_paths = _rebuild_wiki_mutation_views(wiki_root, str(envelope.get("sprint_id") or "sprint-autosci"), target_path, verdict)
            status = "completed"
            write.update(
                {
                    "applied": True,
                    "target_path": _rel(target_path),
                    "log_path": _rel(log_path),
                    "edge_path": _rel(edge_path),
                    "rebuilt_paths": [_rel(item) for item in rebuild_paths],
                }
            )
            artifacts.extend(
                [
                    {"type": "wiki_claim_verdict_target", "path": _rel(target_path)},
                    {"type": "wiki_log", "path": _rel(log_path)},
                    {"type": "wiki_graph_edges", "path": _rel(edge_path)},
                    *[{"type": "wiki_rebuild", "path": _rel(item)} for item in rebuild_paths],
                ]
            )
    if not limitations:
        limitations.append("Approved claim verdict write-back updated wiki frontmatter, log, graph edge, and lightweight wiki views.")

    evidence = {
        "schema": "claim_verdict_writeback.v1",
        "task_id": f"{verdict_evidence.get('task_id', 'task-verify-claim')}:claim-verdict-writeback",
        "sprint_id": str(verdict_evidence.get("sprint_id") or envelope.get("sprint_id") or "sprint-autosci"),
        "node_id": f"{verdict_evidence.get('node_id', 'node-verify-claim')}:claim-verdict-writeback",
        "status": status,
        "inputs": inputs,
        "outputs": {"write": write, "source_verdict": verdict},
        "artifacts": artifacts,
        "provenance": {
            "operator_id": "autosci-bridge",
            "implementation_package": "plugins/autosci",
            "timestamp": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        },
        "limitations": limitations,
    }
    return _write_evidence_payload(path, evidence)


def _phase14_report_paths(envelope: dict[str, Any]) -> dict[str, Path]:
    output_dir = _output_dir(envelope, "write_report")
    paper_dir = _configured_output_path(envelope, "paper_dir_path", output_dir / "paper")
    return {
        "report_plan": _configured_output_path(envelope, "report_plan_path", output_dir / "report_plan.json"),
        "report_md": _configured_output_path(envelope, "report_markdown_path", output_dir / "report.md"),
        "evidence_index": _configured_output_path(
            envelope,
            "report_evidence_index_path",
            output_dir / "report_evidence_index.json",
        ),
        "poster_html": _configured_output_path(envelope, "poster_html_path", output_dir / "optional_poster.html"),
        "rebuttal_md": _configured_output_path(envelope, "rebuttal_markdown_path", output_dir / "optional_rebuttal.md"),
        "publication_bundle": _configured_output_path(envelope, "publication_bundle_path", output_dir / "publication_bundle.json"),
        "paper_dir": paper_dir,
        "paper_main_tex": _configured_output_path(envelope, "paper_main_tex_path", paper_dir / "main.tex"),
        "paper_sections_dir": _configured_output_path(envelope, "paper_sections_dir_path", paper_dir / "sections"),
    }


def _artifact(kind: str, path: Path) -> dict[str, str]:
    return {"type": kind, "path": _rel(path)}


def _unique_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        value = str(value).strip()
        if value and value not in seen:
            seen.add(value)
            unique.append(value)
    return unique


def _phase14_source_payloads(envelope: dict[str, Any]) -> list[dict[str, Any]]:
    inputs = dict(envelope.get("inputs") or {})
    payloads: list[dict[str, Any]] = []
    for key in (
        "discovery_evidence",
        "novelty_evidence",
        "review_llm_evidence",
        "review_evidence",
        "artifact_review_evidence",
        "claim_verdict_evidence",
        "claim_verdict",
        "verdict_evidence",
        "claims_evidence",
        "experiment_result_evidence",
        "experiment_result",
        "code_evidence",
        "code_evidence_map",
        "ideas_evidence",
        "idea_evaluation_evidence",
        "paper_evidence",
        "method_evidence",
    ):
        payloads.extend(_load_optional_evidence_many(inputs.get(key)))
    return payloads


def _phase14_payload_evidence_ids(payload: dict[str, Any]) -> list[str]:
    ids: list[str] = []
    if payload.get("task_id"):
        ids.append(str(payload["task_id"]))
    outputs = payload.get("outputs") if isinstance(payload.get("outputs"), dict) else {}
    for verdict in outputs.get("verdicts") or []:
        if not isinstance(verdict, dict):
            continue
        if verdict.get("claim_id"):
            ids.append(str(verdict["claim_id"]))
        ids.extend(str(item) for item in verdict.get("evidence_ids") or [] if str(item).strip())
    for claim in outputs.get("claims") or []:
        if isinstance(claim, dict):
            if claim.get("claim_id"):
                ids.append(str(claim["claim_id"]))
            ids.extend(str(item) for item in claim.get("evidence_ids") or [] if str(item).strip())
    for mapping in outputs.get("mappings") or []:
        if isinstance(mapping, dict):
            if mapping.get("mapping_id"):
                ids.append(str(mapping["mapping_id"]))
            ids.extend(str(item) for item in mapping.get("evidence_ids") or [] if str(item).strip())
    result = outputs.get("result")
    if isinstance(result, dict):
        if result.get("experiment_id"):
            ids.append(str(result["experiment_id"]))
        ids.extend(str(item) for item in result.get("evidence_ids") or [] if str(item).strip())
    report = outputs.get("report")
    if isinstance(report, dict):
        if report.get("report_id"):
            ids.append(str(report["report_id"]))
        ids.extend(str(item) for item in report.get("evidence_ids") or [] if str(item).strip())
    for item in outputs.get("evaluations") or []:
        if isinstance(item, dict):
            if item.get("idea_id"):
                ids.append(str(item["idea_id"]))
            ids.extend(str(value) for value in item.get("evidence_ids") or [] if str(value).strip())
    return ids


def _phase14_verdicts(payloads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    verdicts: list[dict[str, Any]] = []
    for payload in payloads:
        outputs = payload.get("outputs") if isinstance(payload.get("outputs"), dict) else {}
        for verdict in outputs.get("verdicts") or []:
            if isinstance(verdict, dict):
                verdicts.append(verdict)
    return verdicts


def _compile_pdf_paths_from_contract(contract: dict[str, Any]) -> list[Path]:
    paths: list[Path] = []
    records, _errors = _runtime_records(contract)
    for record in records:
        for key in ("pdf_path", "output_pdf", "compiled_pdf"):
            raw = _field(record, key)
            if not str(raw or "").strip():
                continue
            path = _resolve_harness_path(str(raw))
            if path.exists() and path.is_file() and path.suffix.lower() == ".pdf":
                paths.append(path)
    after_entries = contract.get("after_artifacts") if isinstance(contract.get("after_artifacts"), list) else []
    for entry in after_entries:
        if not isinstance(entry, dict) or not entry.get("exists"):
            continue
        raw = str(entry.get("artifact_path") or entry.get("path") or "").strip()
        if not raw:
            continue
        path = _resolve_harness_path(raw)
        if path.exists() and path.is_file() and path.suffix.lower() == ".pdf":
            paths.append(path)
    seen: set[str] = set()
    unique: list[Path] = []
    for path in paths:
        key = str(path.resolve())
        if key not in seen:
            seen.add(key)
            unique.append(path)
    return unique


def _phase14_compile_handoff(
    envelope: dict[str, Any],
    *,
    requested: bool | None = None,
) -> tuple[dict[str, Any], list[dict[str, str]], list[str]]:
    inputs = dict(envelope.get("inputs") or {})
    if requested is None:
        requested = bool(inputs.get("paper_draft"))
    if not requested:
        return {"status": "not_requested"}, [], []
    contract = _approval_contract(
        envelope,
        "compile_paper",
        ["tex_executor_execution", "pdf_generation"],
    )
    semantic = _approval_semantic_runtime(contract, "compile_paper")
    contract["semantic_runtime"] = semantic
    pdf_paths = _compile_pdf_paths_from_contract(contract)
    verified = bool(semantic.get("verified")) and bool(pdf_paths)
    output_dir = _output_dir(envelope, "write_report")
    handoff_path = output_dir / "paper_draft_compile_handoff.json"
    runtime_artifacts = _contract_existing_artifacts(contract, "runtime_evidence", "paper_compile_runtime_evidence_json")
    after_artifacts = _contract_existing_artifacts(contract, "after_artifacts", "compile_runtime_after_artifact")
    pdf_artifacts = [_artifact("compiled_pdf", path) for path in pdf_paths]
    handoff = {
        "schema": "paper_draft_compile_handoff.v1",
        "status": "completed" if verified else "inconclusive",
        "verified": verified,
        "approval_state": contract.get("approval_state", "N/A"),
        "semantic_runtime": semantic,
        "pdf_paths": [_rel(path) for path in pdf_paths],
        "evidence_ids": _unique_strings(
            [
                "paper-draft-compile-handoff",
                *[str(item) for item in (semantic.get("detail") or {}).get("evidence_ids", [])],
                *[_rel(path) for path in pdf_paths],
            ]
        ),
        "limitations": (
            ["Paper draft includes verified compile/PDF handoff evidence."]
            if verified
            else [
                "Paper draft compile/PDF handoff is incomplete; supply approved compile runtime evidence and compiled PDF artifacts."
            ]
        ),
    }
    handoff_rel = _write_json_sidecar(handoff_path, handoff)
    artifacts = [
        {"type": "paper_draft_compile_handoff_json", "path": handoff_rel},
        *runtime_artifacts,
        *after_artifacts,
        *pdf_artifacts,
    ]
    limitations = [] if verified else [
        "Paper draft has no verified compile/PDF handoff evidence.",
        *_approval_contract_limitations(contract),
    ]
    return handoff, artifacts, limitations


def _phase14_report_raw(envelope: dict[str, Any]) -> dict[str, Any]:
    inputs = dict(envelope.get("inputs") or {})
    paths = _phase14_report_paths(envelope)
    payloads = _phase14_source_payloads(envelope)
    compile_handoff, compile_artifacts, compile_limitations = _phase14_compile_handoff(envelope)
    evidence_ids = _unique_strings([
        *[str(item) for payload in payloads for item in _phase14_payload_evidence_ids(payload)],
        *[str(item) for item in compile_handoff.get("evidence_ids", [])],
        str(inputs.get("claim_id") or ""),
        str(inputs.get("experiment_id") or ""),
    ])
    if not evidence_ids:
        evidence_ids = ["claim-001", "exp-001"]
    verdicts = _phase14_verdicts(payloads)
    primary_verdict = verdicts[0] if verdicts else {}
    verdict_label = str(primary_verdict.get("verdict") or "inconclusive")
    claim_id = str(primary_verdict.get("claim_id") or inputs.get("claim_id") or "claim-001")
    unsupported_claims = [
        str(verdict.get("claim_id") or claim_id)
        for verdict in verdicts
        if str(verdict.get("verdict") or "") in {"not_supported", "inconclusive"}
    ]
    limitations = [
        "Fixture report is assembled from supplied local Solar evidence only.",
        "Publication files are local artifacts and require human approval before external handoff.",
    ]
    sections = [
        {
            "section_id": "summary",
            "title": "Summary",
            "evidence_ids": evidence_ids,
            "body": f"Claim `{claim_id}` has fixture verdict `{verdict_label}`.",
        },
        {
            "section_id": "findings",
            "title": "Findings",
            "evidence_ids": evidence_ids,
            "body": "Findings are limited to the linked claim, experiment, and code evidence artifacts.",
            "figures": [
                {
                    "figure_id": "fig.optional-poster",
                    "title": "Optional poster artifact",
                    "artifact_path": _rel(paths["poster_html"]),
                    "evidence_ids": evidence_ids,
                }
            ],
        },
        {
            "section_id": "evidence-map",
            "title": "Evidence Map",
            "evidence_ids": evidence_ids,
            "body": "The evidence map lists the concrete ids used to support the report sections.",
            "tables": [
                {
                    "table_id": "table.evidence-map",
                    "title": "Evidence ids",
                    "artifact_path": _rel(paths["evidence_index"]),
                    "evidence_ids": evidence_ids,
                }
            ],
        },
        {
            "section_id": "limitations",
            "title": "Limitations",
            "evidence_ids": evidence_ids,
            "body": "The report is not a substitute for external peer review or real benchmark validation.",
        },
    ]
    if unsupported_claims:
        sections.insert(2, {
            "section_id": "unsupported-claims",
            "title": "Unsupported Claims",
            "evidence_ids": evidence_ids,
            "body": "Unsupported or inconclusive claims are explicitly listed and are not presented as successful.",
        })
    artifacts = [
        _artifact("report_plan_json", paths["report_plan"]),
        _artifact("markdown_report", paths["report_md"]),
        _artifact("report_evidence_index_json", paths["evidence_index"]),
        _artifact("optional_poster_html", paths["poster_html"]),
        _artifact("optional_rebuttal_markdown", paths["rebuttal_md"]),
        *compile_artifacts,
    ]
    if inputs.get("paper_draft"):
        artifacts.extend([
            _artifact("latex_source", paths["paper_main_tex"]),
            _artifact("paper_sections_directory", paths["paper_sections_dir"]),
        ])
        if compile_handoff.get("status") == "completed":
            sections.insert(
                -1,
                {
                    "section_id": "compiled-paper",
                    "title": "Compiled Paper",
                    "evidence_ids": compile_handoff.get("evidence_ids") or evidence_ids,
                    "body": "A compiled PDF handoff is attached from approved compile runtime evidence.",
                },
            )
        else:
            sections[-1]["body"] = (
                str(sections[-1].get("body") or "")
                + " Paper draft compile/PDF handoff is incomplete."
            )
    limitations.extend(compile_limitations)
    return {
        "report_id": str(inputs.get("report_id") or "report-autosci-phase14"),
        "title": str(inputs.get("report_title") or "AutoSci Evidence-Linked Fixture Report"),
        "sections": sections,
        "evidence_ids": evidence_ids,
        "unsupported_claims": _unique_strings(unsupported_claims),
        "figures": sections[1]["figures"],
        "tables": sections[2 if not unsupported_claims else 3]["tables"],
        "publication_bundle_path": _rel(paths["publication_bundle"]),
        "compile_handoff": compile_handoff,
        "artifacts": artifacts,
        "limitations": limitations,
    }


def _render_report_markdown(report: dict[str, Any], limitations_list: list[str]) -> str:
    lines = [f"# {report.get('title', 'Scientific Report')}", ""]
    for section in report.get("sections") or []:
        if not isinstance(section, dict):
            continue
        lines.extend([f"## {section.get('title', 'Section')}", ""])
        body = str(section.get("body") or "")
        if body:
            lines.extend([body, ""])
        evidence_ids = ", ".join(str(item) for item in section.get("evidence_ids") or [])
        lines.extend([f"Evidence ids: {evidence_ids or 'N/A'}", ""])
    if limitations_list:
        lines.extend(["## Evidence Limitations", ""])
        for limitation in limitations_list:
            lines.append(f"- {limitation}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _render_poster_html(report: dict[str, Any]) -> str:
    title = html.escape(str(report.get("title") or "Scientific Report"))
    summary = ""
    sections = report.get("sections") if isinstance(report.get("sections"), list) else []
    if sections and isinstance(sections[0], dict):
        summary = html.escape(str(sections[0].get("body") or ""))
    return (
        "<!doctype html>\n"
        "<html><head><meta charset=\"utf-8\"><title>"
        f"{title}</title></head><body><main><h1>{title}</h1>"
        f"<p>{summary}</p><p>Fixture poster artifact generated from linked Solar evidence.</p>"
        "</main></body></html>\n"
    )


def _render_rebuttal_markdown(report: dict[str, Any], limitations_list: list[str]) -> str:
    unsupported = report.get("unsupported_claims") if isinstance(report.get("unsupported_claims"), list) else []
    lines = [
        f"# Rebuttal Draft: {report.get('title', 'Scientific Report')}",
        "",
        "## Scope",
        "",
        "This local rebuttal draft is generated from the same evidence-linked report payload.",
        "",
        "## Unsupported Or Open Claims",
        "",
    ]
    if unsupported:
        lines.extend(f"- {claim_id}" for claim_id in unsupported)
    else:
        lines.append("- N/A")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {limitation}" for limitation in limitations_list)
    return "\n".join(lines).rstrip() + "\n"


def _latex_escape(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in value)


def _render_latex_paper(report: dict[str, Any], limitations_list: list[str]) -> str:
    title = _latex_escape(str(report.get("title") or "AutoSci Paper Draft"))
    sections = report.get("sections") if isinstance(report.get("sections"), list) else []
    lines = [
        r"\documentclass{article}",
        r"\usepackage[margin=1in]{geometry}",
        r"\usepackage{hyperref}",
        r"\title{" + title + "}",
        r"\author{Solar AutoSci}",
        r"\date{}",
        r"\begin{document}",
        r"\maketitle",
        "",
    ]
    for section in sections:
        if not isinstance(section, dict):
            continue
        heading = _latex_escape(str(section.get("title") or section.get("section_id") or "Section"))
        body = _latex_escape(str(section.get("body") or "N/A"))
        evidence_ids = ", ".join(str(item) for item in section.get("evidence_ids") or []) or "N/A"
        lines.extend([
            r"\section{" + heading + "}",
            body,
            "",
            r"\paragraph{Evidence ids} " + _latex_escape(evidence_ids),
            "",
        ])
    if limitations_list:
        lines.extend([r"\section{Limitations}", ""])
        for limitation in limitations_list:
            lines.append(r"\begin{itemize}\item " + _latex_escape(str(limitation)) + r"\end{itemize}")
    lines.extend(["", r"\end{document}", ""])
    return "\n".join(lines)


def _write_text_sidecar(path: Path, body: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return _rel(path)


def _write_json_sidecar(path: Path, payload: dict[str, Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return _rel(path)


def _write_phase14_publication_sidecars(envelope: dict[str, Any], report_evidence: dict[str, Any]) -> dict[str, Any]:
    inputs = dict(envelope.get("inputs") or {})
    paths = _phase14_report_paths(envelope)
    report = dict(((report_evidence.get("outputs") or {}).get("report") or {}))
    limitations_list = [str(item) for item in report_evidence.get("limitations") or []]
    file_artifacts = [
        _artifact("report_plan_json", paths["report_plan"]),
        _artifact("markdown_report", paths["report_md"]),
        _artifact("report_evidence_index_json", paths["evidence_index"]),
        _artifact("optional_poster_html", paths["poster_html"]),
        _artifact("optional_rebuttal_markdown", paths["rebuttal_md"]),
    ]
    if inputs.get("paper_draft"):
        file_artifacts.extend([
            _artifact("latex_source", paths["paper_main_tex"]),
            _artifact("paper_sections_directory", paths["paper_sections_dir"]),
        ])
    passthrough_types = {
        "paper_draft_compile_handoff_json",
        "paper_compile_runtime_evidence_json",
        "compile_runtime_after_artifact",
        "compiled_pdf",
    }
    seen_file_artifacts = {(artifact["type"], artifact["path"]) for artifact in file_artifacts}
    for artifact in report_evidence.get("artifacts") or []:
        if not isinstance(artifact, dict):
            continue
        artifact_type = str(artifact.get("type") or "")
        artifact_path = str(artifact.get("path") or "")
        if artifact_type not in passthrough_types or not artifact_path:
            continue
        key = (artifact_type, artifact_path)
        if key in seen_file_artifacts:
            continue
        seen_file_artifacts.add(key)
        file_artifacts.append({"type": artifact_type, "path": artifact_path})
    _write_json_sidecar(paths["report_plan"], {
        "report_id": report.get("report_id"),
        "title": report.get("title"),
        "sections": [
            {
                "section_id": section.get("section_id"),
                "title": section.get("title"),
                "evidence_ids": section.get("evidence_ids") or [],
            }
            for section in report.get("sections") or []
            if isinstance(section, dict)
        ],
        "publication_bundle_path": report.get("publication_bundle_path"),
    })
    _write_text_sidecar(paths["report_md"], _render_report_markdown(report, limitations_list))
    _write_text_sidecar(paths["poster_html"], _render_poster_html(report))
    _write_text_sidecar(paths["rebuttal_md"], _render_rebuttal_markdown(report, limitations_list))
    if inputs.get("paper_draft"):
        _write_text_sidecar(paths["paper_main_tex"], _render_latex_paper(report, limitations_list))
        paths["paper_sections_dir"].mkdir(parents=True, exist_ok=True)
        for section in report.get("sections") or []:
            if not isinstance(section, dict):
                continue
            section_id = _slug(str(section.get("section_id") or section.get("title") or "section"))
            section_body = "\n".join(
                [
                    r"\section{" + _latex_escape(str(section.get("title") or section_id)) + "}",
                    _latex_escape(str(section.get("body") or "N/A")),
                    "",
                ]
            )
            _write_text_sidecar(paths["paper_sections_dir"] / f"{section_id}.tex", section_body)
    _write_json_sidecar(paths["evidence_index"], {
        "report_id": report.get("report_id"),
        "evidence_ids": report.get("evidence_ids") or [],
        "sections": [
            {
                "section_id": section.get("section_id"),
                "evidence_ids": section.get("evidence_ids") or [],
            }
            for section in report.get("sections") or []
            if isinstance(section, dict)
        ],
    })
    report_id = str(report.get("report_id") or "report-autosci-phase14")
    bundle_evidence = convert_publication_bundle({
        "bundle_id": f"bundle-{report_id}",
        "publication_type": "mixed",
        "source_report_id": report_id,
        "files": file_artifacts,
        "evidence_ids": _unique_strings([report_id, *[str(item) for item in report.get("evidence_ids") or []]]),
        "artifacts": file_artifacts,
        "limitations": [
            "Fixture publication bundle contains local files only.",
            "Human approval is required before external publication or submission.",
        ],
    }, envelope)
    bundle_path = _write_evidence_payload(paths["publication_bundle"], bundle_evidence)
    return {
        "publication_bundle_path": bundle_path,
        "publication_files": [artifact["path"] for artifact in file_artifacts],
        "sidecar_evidence_paths": [bundle_path],
    }


def _action_write_report(envelope: dict[str, Any]) -> dict[str, Any]:
    return convert_scientific_report(_phase14_report_raw(envelope), envelope)


def _native_publication_title(envelope: dict[str, Any], fallback: str) -> str:
    inputs = dict(envelope.get("inputs") or {})
    return str(
        inputs.get("report_title")
        or inputs.get("title")
        or inputs.get("topic")
        or inputs.get("target")
        or fallback
    )


def _native_publication_target(envelope: dict[str, Any]) -> str:
    inputs = dict(envelope.get("inputs") or {})
    return str(inputs.get("target") or inputs.get("paper_path") or inputs.get("topic") or "N/A")


def _native_publication_evidence_ids(envelope: dict[str, Any], fallback: str) -> list[str]:
    inputs = dict(envelope.get("inputs") or {})
    ids = [
        *[str(item) for payload in _phase14_source_payloads(envelope) for item in _phase14_payload_evidence_ids(payload)],
        str(inputs.get("claim_id") or ""),
        str(inputs.get("experiment_id") or ""),
        str(inputs.get("target") or ""),
    ]
    return _unique_strings(ids) or [fallback]


def _native_publication_has_source_evidence(envelope: dict[str, Any]) -> bool:
    return bool(_phase14_source_payloads(envelope))


def _citation_id_from_entry(entry: dict[str, Any], fallback: str) -> str:
    for key in ("candidate_id", "citation_id", "paper_id", "paperId", "arxiv_id", "source_ref", "url"):
        value = str(entry.get(key) or "").strip()
        if value:
            return value
    return fallback


def _citation_entry(entry: dict[str, Any], *, source: str, evidence_id: str, fallback: str) -> dict[str, Any] | None:
    title = str(entry.get("title") or entry.get("name") or "").strip()
    if not title:
        return None
    source_ref = str(entry.get("source_ref") or entry.get("url") or "").strip()
    arxiv_id = str(entry.get("arxiv_id") or "").strip()
    if not source_ref and arxiv_id:
        source_ref = f"https://arxiv.org/abs/{arxiv_id}"
    citation_id = _citation_id_from_entry(entry, fallback)
    channels = entry.get("source_channels") if isinstance(entry.get("source_channels"), list) else []
    return {
        "citation_id": citation_id,
        "title": title,
        "source_ref": source_ref or "N/A",
        "source": source,
        "evidence_id": evidence_id,
        "source_channels": [str(item) for item in channels if str(item).strip()],
    }


def _citation_entries_from_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    outputs = payload.get("outputs") if isinstance(payload.get("outputs"), dict) else {}
    evidence_id = str(payload.get("task_id") or payload.get("node_id") or payload.get("schema") or "source-evidence")
    entries: list[dict[str, Any]] = []
    for index, candidate in enumerate(outputs.get("candidates") or []):
        if isinstance(candidate, dict):
            entry = _citation_entry(candidate, source="literature_discovery", evidence_id=evidence_id, fallback=f"{evidence_id}:candidate-{index + 1}")
            if entry:
                entries.append(entry)
    paper = outputs.get("paper")
    if isinstance(paper, dict):
        entry = _citation_entry(paper, source="research_paper", evidence_id=evidence_id, fallback=f"{evidence_id}:paper")
        if entry:
            entries.append(entry)
    return entries


def _citation_entries_from_wiki(envelope: dict[str, Any]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for root in _wiki_roots_for_read(envelope):
        papers_dir = root / "papers"
        if not papers_dir.exists():
            continue
        for index, path in enumerate(sorted(papers_dir.glob("*.md")), start=1):
            text = path.read_text(encoding="utf-8", errors="replace")
            title = path.stem.replace("-", " ").title()
            for line in text.splitlines():
                if line.startswith("# "):
                    title = line[2:].strip()
                    break
            arxiv_match = re.search(r"(?:arxiv:|arxiv_id:)\s*([0-9]{4}\.[0-9]{4,5}(?:v\d+)?)", text, re.IGNORECASE)
            source_ref = f"https://arxiv.org/abs/{arxiv_match.group(1)}" if arxiv_match else _rel(path)
            entries.append(
                {
                    "citation_id": f"wiki:{_rel(path)}",
                    "title": title,
                    "source_ref": source_ref,
                    "source": "wiki_paper",
                    "evidence_id": _rel(path),
                    "source_channels": ["wiki"],
                    "path": _rel(path),
                }
            )
            if index >= 50:
                break
    return entries


def _native_publication_citation_map(envelope: dict[str, Any]) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    for payload in _phase14_source_payloads(envelope):
        entries.extend(_citation_entries_from_payload(payload))
    entries.extend(_citation_entries_from_wiki(envelope))
    deduped: dict[str, dict[str, Any]] = {}
    for entry in entries:
        key = str(entry.get("citation_id") or entry.get("title") or "").strip().lower()
        if key and key not in deduped:
            deduped[key] = entry
    citations = list(deduped.values())
    return {
        "schema": "autosci_publication_citation_map.v1",
        "status": "completed" if citations else "inconclusive",
        "citation_count": len(citations),
        "citations": citations,
        "limitations": [] if citations else ["No source-backed citation entries were available."],
    }


def _native_publication_review_completed(envelope: dict[str, Any]) -> bool:
    for payload in _phase14_source_payloads(envelope):
        if payload.get("schema") != "artifact_review.v1" or payload.get("status") != "completed":
            continue
        review = ((payload.get("outputs") or {}).get("review") or {})
        if not isinstance(review, dict):
            continue
        review_llm = review.get("review_llm") if isinstance(review.get("review_llm"), dict) else {}
        if review.get("review_mode") == "review_llm" or review_llm.get("status") == "completed":
            return True
    return False


def _native_report_paths(envelope: dict[str, Any], action: str) -> dict[str, Path]:
    output_dir = _output_dir(envelope, action)
    return {
        "plan_json": _configured_output_path(envelope, "plan_json_path", output_dir / f"{action}_plan.json"),
        "markdown": _configured_output_path(envelope, "markdown_path", output_dir / f"{action}.md"),
        "citation_map": _configured_output_path(envelope, "citation_map_path", output_dir / f"{action}_citation_map.json"),
    }


def _native_report_markdown(title: str, sections: list[dict[str, Any]], limitations_list: list[str]) -> str:
    lines = [f"# {title}", ""]
    for section in sections:
        lines.extend([f"## {section.get('title', 'Section')}", ""])
        body = str(section.get("body") or "")
        if body:
            lines.extend([body, ""])
        evidence_ids = ", ".join(str(item) for item in section.get("evidence_ids") or [])
        lines.extend([f"Evidence ids: {evidence_ids or 'N/A'}", ""])
    if limitations_list:
        lines.extend(["## Limitations", ""])
        lines.extend(f"- {limitation}" for limitation in limitations_list)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _action_plan_report(envelope: dict[str, Any]) -> dict[str, Any]:
    inputs = dict(envelope.get("inputs") or {})
    paths = _native_report_paths(envelope, "plan_report")
    title = _native_publication_title(envelope, "AutoSci Paper Plan")
    target = _native_publication_target(envelope)
    evidence_ids = _native_publication_evidence_ids(envelope, "paper-plan:request")
    has_source_evidence = _native_publication_has_source_evidence(envelope)
    citation_map = _native_publication_citation_map(envelope)
    has_citations = bool(citation_map.get("citations"))
    has_review_llm = _native_publication_review_completed(envelope)
    compile_requested = bool(
        inputs.get("approval_ref")
        or inputs.get("runtime_evidence")
        or inputs.get("after_artifacts")
        or inputs.get("allowlist_evidence")
        or inputs.get("before_artifacts")
    )
    compile_handoff, compile_artifacts, compile_limitations = _phase14_compile_handoff(
        envelope,
        requested=compile_requested,
    )
    if compile_handoff.get("status") == "completed":
        evidence_ids = _unique_strings([*evidence_ids, *[str(item) for item in compile_handoff.get("evidence_ids") or []]])
    limitations = [
        "Paper plan is generated from local Solar evidence, request metadata, and supplied source/review evidence.",
    ]
    if not has_source_evidence:
        limitations.append("No source evidence was supplied; plan remains a scaffold until linked evidence is provided.")
    if not has_citations:
        limitations.append("No source-backed citation map was available; citation slots remain incomplete.")
    if not has_review_llm:
        limitations.append("No completed Review LLM evidence was supplied; plan remains pre-review.")
    limitations.extend(compile_limitations)
    citation_preview = citation_map.get("citations") or []
    citation_body = "\n".join(
        f"- `{item.get('citation_id')}`: {item.get('title')} ({item.get('source_ref')})"
        for item in citation_preview[:8]
    ) or "No source-backed citation entries were available."
    sections = [
        {
            "section_id": "outline",
            "title": "Outline Plan",
            "evidence_ids": evidence_ids,
            "body": f"Plan a paper around target `{target}` with title `{title}`.",
        },
        {
            "section_id": "evidence-map",
            "title": "Evidence Map",
            "evidence_ids": evidence_ids,
            "body": "Every planned claim, figure, and table must be backed by explicit evidence ids before drafting.",
        },
        {
            "section_id": "figure-citation-plan",
            "title": "Figure And Citation Plan",
            "evidence_ids": evidence_ids,
            "body": f"Citation map contains `{citation_map.get('citation_count', 0)}` source-backed entries.\n\n{citation_body}",
        },
        {
            "section_id": "review-gates",
            "title": "Review Gates",
            "evidence_ids": evidence_ids,
            "body": f"Review LLM evidence status: `{'completed' if has_review_llm else 'missing'}`. Novelty/relevance checks remain required before promotion beyond plan status.",
        },
        {
            "section_id": "compile-audit",
            "title": "Compile Audit",
            "evidence_ids": compile_handoff.get("evidence_ids") or evidence_ids,
            "body": f"Compile/PDF handoff status: `{compile_handoff.get('status', 'not_requested')}`.",
        },
        {
            "section_id": "limitations",
            "title": "Limitations",
            "evidence_ids": evidence_ids,
            "body": "This is a bounded planning artifact, not a compiled manuscript or external-review result.",
        },
    ]
    plan_payload = {
        "title": title,
        "target": target,
        "evidence_ids": evidence_ids,
        "sections": [
            {
                "section_id": section["section_id"],
                "title": section["title"],
                "evidence_ids": section["evidence_ids"],
            }
            for section in sections
        ],
        "limitations": limitations,
        "citation_map": citation_map,
        "review_llm_completed": has_review_llm,
        "compile_handoff": compile_handoff,
    }
    plan_path = _write_json_sidecar(paths["plan_json"], plan_payload)
    citation_map_path = _write_json_sidecar(paths["citation_map"], citation_map)
    markdown_path = _write_text_sidecar(paths["markdown"], _native_report_markdown(title, sections, limitations))
    return convert_scientific_report({
        "report_id": f"paper-plan-{_slug(title)}",
        "title": title,
        "sections": sections,
        "evidence_ids": evidence_ids,
        "unsupported_claims": [],
        "compile_handoff": compile_handoff,
        "status": "completed" if has_source_evidence and has_citations and has_review_llm else "inconclusive",
        "artifacts": [
            {"type": "paper_plan_json", "path": plan_path},
            {"type": "paper_plan_markdown", "path": markdown_path},
            {"type": "citation_map_json", "path": citation_map_path},
            *compile_artifacts,
        ],
        "limitations": limitations,
    }, envelope)


def _action_write_survey(envelope: dict[str, Any]) -> dict[str, Any]:
    paths = _native_report_paths(envelope, "write_survey")
    title = _native_publication_title(envelope, "AutoSci Literature Survey")
    target = _native_publication_target(envelope)
    evidence_ids = _native_publication_evidence_ids(envelope, "survey:request")
    has_source_evidence = _native_publication_has_source_evidence(envelope)
    citation_map = _native_publication_citation_map(envelope)
    has_citations = bool(citation_map.get("citations"))
    limitations = [
        "Survey is assembled from local Solar evidence and supplied discovery/paper citation evidence.",
    ]
    if not has_source_evidence:
        limitations.append("No literature/source evidence was supplied; survey remains an evidence scaffold.")
    if not has_citations:
        limitations.append("No source-backed citation map was available; survey coverage remains incomplete.")
    citation_preview = citation_map.get("citations") or []
    citation_body = "\n".join(
        f"- `{item.get('citation_id')}`: {item.get('title')} ({item.get('source_ref')})"
        for item in citation_preview[:12]
    ) or "No source-backed citation entries were available."
    sections = [
        {
            "section_id": "scope",
            "title": "Scope",
            "evidence_ids": evidence_ids,
            "body": f"Survey scope: `{target}`.",
        },
        {
            "section_id": "themes",
            "title": "Themes",
            "evidence_ids": evidence_ids,
            "body": "Themes must be derived from linked paper, discovery, claim, or method evidence.",
        },
        {
            "section_id": "prior-work-map",
            "title": "Prior Work Map",
            "evidence_ids": evidence_ids,
            "body": f"Citation map contains `{citation_map.get('citation_count', 0)}` source-backed entries.\n\n{citation_body}",
        },
        {
            "section_id": "limitations",
            "title": "Limitations",
            "evidence_ids": evidence_ids,
            "body": "This survey scaffold does not claim exhaustive literature coverage.",
        },
    ]
    plan_path = _write_json_sidecar(paths["plan_json"], {
        "title": title,
        "target": target,
        "survey_evidence_ids": evidence_ids,
        "citation_map": citation_map,
        "limitations": limitations,
    })
    citation_map_path = _write_json_sidecar(paths["citation_map"], citation_map)
    markdown_path = _write_text_sidecar(paths["markdown"], _native_report_markdown(title, sections, limitations))
    return convert_scientific_report({
        "report_id": f"survey-{_slug(title)}",
        "title": title,
        "sections": sections,
        "evidence_ids": evidence_ids,
        "unsupported_claims": [],
        "status": "completed" if has_source_evidence and has_citations else "inconclusive",
        "artifacts": [
            {"type": "survey_plan_json", "path": plan_path},
            {"type": "survey_markdown", "path": markdown_path},
            {"type": "citation_map_json", "path": citation_map_path},
        ],
        "limitations": limitations,
    }, envelope)


def _publication_action_paths(envelope: dict[str, Any], action: str) -> dict[str, Path]:
    output_dir = _output_dir(envelope, action)
    return {
        "markdown": _configured_output_path(envelope, "markdown_path", output_dir / f"{action}.md"),
        "html": _configured_output_path(envelope, "html_path", output_dir / f"{action}.html"),
        "map_json": _configured_output_path(envelope, "map_json_path", output_dir / f"{action}_map.json"),
    }


def _rebuttal_concerns_from_review_evidence(envelope: dict[str, Any]) -> list[dict[str, Any]]:
    concerns: list[dict[str, Any]] = []
    for payload in _phase14_source_payloads(envelope):
        if payload.get("schema") != "artifact_review.v1":
            continue
        evidence_id = str(payload.get("task_id") or "artifact-review")
        review = ((payload.get("outputs") or {}).get("review") or {})
        if not isinstance(review, dict):
            continue
        findings = review.get("findings") if isinstance(review.get("findings"), list) else []
        for index, finding in enumerate(findings, start=1):
            if isinstance(finding, dict):
                concern = str(
                    finding.get("issue")
                    or finding.get("finding")
                    or finding.get("evidence")
                    or finding.get("suggestion")
                    or ""
                ).strip()
                focus = str(finding.get("criterion") or finding.get("focus") or "review").strip()
            else:
                concern = str(finding).strip()
                focus = "review"
            if not concern:
                continue
            concerns.append(
                {
                    "concern_id": f"{evidence_id}:concern-{index}",
                    "focus": focus,
                    "concern": concern,
                    "evidence_id": evidence_id,
                }
            )
    return concerns


def _action_draft_rebuttal(envelope: dict[str, Any]) -> dict[str, Any]:
    paths = _publication_action_paths(envelope, "draft_rebuttal")
    title = _native_publication_title(envelope, "AutoSci Rebuttal Draft")
    target = _native_publication_target(envelope)
    evidence_ids = _native_publication_evidence_ids(envelope, "rebuttal:request")
    has_source_evidence = _native_publication_has_source_evidence(envelope)
    concerns = _rebuttal_concerns_from_review_evidence(envelope)
    limitations = [
        "Rebuttal draft is local and evidence-linked; it is not a submitted response.",
        "Review LLM stress-test and reviewer-comment atomization require supplied review evidence.",
    ]
    if not has_source_evidence:
        limitations.append("No review/comment/evidence payload was supplied; all concerns remain unmapped.")
    if has_source_evidence and not concerns:
        limitations.append("Review evidence was supplied but no structured findings/concerns were available to map.")
    mapped_concerns = [
        {
            "concern_id": concern["concern_id"],
            "focus": concern["focus"],
            "concern": concern["concern"],
            "response": "Acknowledge the concern, attach the cited evidence, and revise the manuscript section before final submission.",
            "status": "mapped",
            "evidence_ids": [concern["evidence_id"]],
        }
        for concern in concerns
    ]
    response_map = {
        "title": title,
        "target": target,
        "mapped_concerns": mapped_concerns,
        "unmapped_concerns": [] if mapped_concerns else ["No structured reviewer comments were supplied."],
        "evidence_ids": evidence_ids,
        "limitations": limitations,
    }
    map_path = _write_json_sidecar(paths["map_json"], response_map)
    body = "\n".join(
        [
            f"# {title}",
            "",
            f"Target: `{target}`",
            "",
            "## Response Map",
            "",
            *(
                [
                    f"- `{item['concern_id']}` [{item['focus']}]: {item['concern']}\n  Response: {item['response']}"
                    for item in mapped_concerns
                ]
                or ["- No structured reviewer comments were supplied."]
            ),
            "",
            "## Evidence",
            "",
            *[f"- {item}" for item in evidence_ids],
            "",
            "## Limitations",
            "",
            *[f"- {item}" for item in limitations],
            "",
        ]
    )
    markdown_path = _write_text_sidecar(paths["markdown"], body)
    files = [
        {"type": "rebuttal_markdown", "path": markdown_path},
        {"type": "rebuttal_response_map_json", "path": map_path},
    ]
    return convert_publication_bundle({
        "bundle_id": f"rebuttal-{_slug(title)}",
        "publication_type": "rebuttal",
        "source_report_id": f"rebuttal:{_slug(target)}",
        "files": files,
        "evidence_ids": _unique_strings([f"rebuttal:{_slug(target)}", *evidence_ids]),
        "artifacts": files,
        "status": "completed" if has_source_evidence and mapped_concerns else "inconclusive",
        "limitations": limitations,
    }, envelope)


def _action_build_poster(envelope: dict[str, Any]) -> dict[str, Any]:
    paths = _publication_action_paths(envelope, "build_poster")
    title = _native_publication_title(envelope, "AutoSci Poster")
    target = _native_publication_target(envelope)
    evidence_ids = _native_publication_evidence_ids(envelope, "poster:request")
    has_source_evidence = _native_publication_has_source_evidence(envelope)
    contract = _approval_contract(
        envelope,
        "build_poster",
        ["browser_render", "overflow_probe", "png_export"],
    )
    limitations = [
        "Poster HTML is generated locally; browser rendering, overflow probing, and PNG export are not executed by this bridge.",
        "Poster output requires human/browser validation before publication use.",
        *_approval_contract_limitations(contract),
    ]
    if not has_source_evidence:
        limitations.append("No report/evidence payload was supplied; poster content remains a scaffold.")
    html_body = (
        "<!doctype html>\n"
        "<html><head><meta charset=\"utf-8\"><title>"
        f"{html.escape(title)}</title></head><body><main>"
        f"<h1>{html.escape(title)}</h1>"
        f"<p>Target: {html.escape(target)}</p>"
        "<section><h2>Evidence</h2><ul>"
        + "".join(f"<li>{html.escape(str(item))}</li>" for item in evidence_ids)
        + "</ul></section>"
        "<section><h2>Limitations</h2><ul>"
        + "".join(f"<li>{html.escape(str(item))}</li>" for item in limitations)
        + "</ul></section>"
        "</main></body></html>\n"
    )
    html_path = _write_text_sidecar(paths["html"], html_body)
    contract, executor_result = _execute_poster_if_approved(envelope, contract, paths["html"])
    semantic = _approval_semantic_runtime(contract, "build_poster")
    contract["semantic_runtime"] = semantic
    contract_artifact = _write_approval_contract_sidecar(envelope, "build_poster", contract)
    runtime_evidence_artifacts = _contract_existing_artifacts(contract, "runtime_evidence", "poster_runtime_evidence_json")
    limitations = [
        "Poster HTML is generated locally; browser rendering, overflow probing, and PNG export are not executed by this bridge.",
        "Poster output requires human/browser validation before publication use.",
        *_approval_contract_limitations(contract),
    ]
    if bool(executor_result.get("executed")):
        limitations = [
            "Poster render/export was executed by the approved side-effect executor and verified from runtime evidence."
            if semantic.get("verified")
            else f"Approved poster executor ran but did not verify successfully: {executor_result.get('reason') or 'semantic runtime incomplete'}",
        ]
    elif semantic.get("verified"):
        limitations = [
            "Poster runtime was verified from supplied approval-gated evidence; this bridge did not execute browser rendering.",
        ]
    if not has_source_evidence:
        limitations.append("No report/evidence payload was supplied; poster content remains a scaffold.")
    validation_path = _write_json_sidecar(paths["map_json"], {
        "title": title,
        "target": target,
        "browser_rendered": bool(semantic.get("detail", {}).get("browser_rendered")) if isinstance(semantic.get("detail"), dict) else False,
        "png_exported": bool(semantic.get("detail", {}).get("png_exported")) if isinstance(semantic.get("detail"), dict) else False,
        "overflow_probe": "passed" if semantic.get("detail", {}).get("overflow_probe_passed") else "not_run",
        "approval_contract": contract,
        "runtime_semantic": semantic,
        "evidence_ids": evidence_ids,
        "limitations": limitations,
    })
    files = [
        {"type": "poster_html", "path": html_path},
        {"type": "poster_validation_json", "path": validation_path},
        contract_artifact,
        *runtime_evidence_artifacts,
        *_contract_existing_artifacts(contract, "after_artifacts", "poster_runtime_after_artifact"),
    ]
    return convert_publication_bundle({
        "bundle_id": f"poster-{_slug(title)}",
        "publication_type": "poster",
        "source_report_id": f"poster:{_slug(target)}",
        "files": files,
        "evidence_ids": _unique_strings([f"poster:{_slug(target)}", *evidence_ids]),
        "artifacts": files,
        "status": "completed" if semantic.get("verified") and has_source_evidence else "inconclusive",
        "limitations": limitations,
    }, envelope)


def _paper_compile_paths(envelope: dict[str, Any]) -> dict[str, Path]:
    output_dir = _output_dir(envelope, "compile_paper")
    return {
        "checklist": _configured_output_path(
            envelope,
            "compile_checklist_path",
            output_dir / "paper_compile_checklist.json",
        ),
        "diagnostics": _configured_output_path(
            envelope,
            "compile_diagnostics_path",
            output_dir / "paper_compile_diagnostics.md",
        ),
        "fix_writeback": _configured_output_path(
            envelope,
            "compile_fix_writeback_path",
            output_dir / "paper_compile_fix_writeback.json",
        ),
    }


def _paper_compile_target(envelope: dict[str, Any]) -> tuple[str, Path | None]:
    inputs = envelope.get("inputs") if isinstance(envelope.get("inputs"), dict) else {}
    raw = str(inputs.get("paper_path") or inputs.get("target") or "").strip()
    if not raw:
        return "", None
    return raw, _resolve_harness_path(raw)


def _compile_source_candidates(target_path: Path | None) -> dict[str, list[Path]]:
    suffixes = {
        "latex": {".tex"},
        "pdf": {".pdf"},
        "markdown": {".md", ".markdown"},
        "bibliography": {".bib"},
    }
    candidates: dict[str, list[Path]] = {key: [] for key in suffixes}
    if not target_path or not target_path.exists():
        return candidates

    ignored_parts = {".git", ".hg", ".svn", ".venv", "node_modules", "__pycache__"}

    def add_file(path: Path) -> None:
        if any(part in ignored_parts for part in path.parts):
            return
        suffix = path.suffix.lower()
        for key, key_suffixes in suffixes.items():
            if suffix in key_suffixes and len(candidates[key]) < 25:
                candidates[key].append(path)

    if target_path.is_file():
        add_file(target_path)
        return candidates

    for path in sorted(target_path.rglob("*"), key=lambda item: str(item)):
        if path.is_file():
            add_file(path)
    return candidates


def _paper_compile_fix_target(target_path: Path | None, latex_files: list[Path]) -> Path | None:
    if target_path and target_path.exists() and target_path.is_file() and target_path.suffix.lower() == ".tex":
        return target_path
    return latex_files[0] if latex_files else None


def _paper_compile_fix_if_approved(
    envelope: dict[str, Any],
    contract: dict[str, Any],
    target_path: Path | None,
    latex_files: list[Path],
) -> dict[str, Any]:
    inputs = envelope.get("inputs") if isinstance(envelope.get("inputs"), dict) else {}
    if not bool(inputs.get("fix")):
        return {"requested": False, "applied": False, "artifacts": [], "limitations": [], "status": "not_requested"}

    paths = _paper_compile_paths(envelope)
    after_artifacts = inputs.get("after_artifacts") if isinstance(inputs.get("after_artifacts"), list) else []
    status = "inconclusive"
    artifacts: list[dict[str, Any]] = []
    limitations: list[str] = []
    write: dict[str, Any] = {
        "requested": True,
        "applied": False,
        "approval_ref": str(contract.get("approval_ref") or "N/A"),
        "approval_state": str(contract.get("approval_state") or "unknown"),
    }

    target_tex = _paper_compile_fix_target(target_path, latex_files)
    if not bool(inputs.get("execute_approved_side_effect")):
        limitations.append("Paper compile --fix requires --execute-approved before mutating TeX source.")
    elif not contract.get("ready_for_execution"):
        limitations.append("Paper compile --fix requires approval_ref, allowlist evidence, and before_artifact evidence.")
    elif target_tex is None:
        limitations.append("Paper compile --fix requires an existing .tex target.")
    elif not after_artifacts:
        limitations.append("Paper compile --fix requires an after_artifact containing the approved fixed TeX source.")
    else:
        after_path = _resolve_harness_path(str(after_artifacts[0]))
        allowed_roots = [HARNESS_DIR, REPO_HARNESS_DIR]
        if not any(_path_is_under(target_tex, root) for root in allowed_roots):
            limitations.append("Paper compile --fix target must stay inside the harness or repository root.")
        elif not after_path.exists() or after_path.is_dir():
            limitations.append("Paper compile --fix after_artifact does not resolve to an existing file.")
        else:
            before = target_tex.read_text(encoding="utf-8", errors="replace")
            desired = after_path.read_text(encoding="utf-8", errors="replace")
            changed = _write_text_if_changed_bridge(target_tex, desired)
            after = target_tex.read_text(encoding="utf-8", errors="replace")
            status = "completed"
            write.update(
                {
                    "applied": True,
                    "target_path": _rel(target_tex),
                    "after_artifact": _rel(after_path),
                    "changed": changed,
                    "before_sha256": _hash_text(before),
                    "after_sha256": _hash_text(after),
                }
            )
            artifacts.append({"type": "latex_source", "path": _rel(target_tex)})
            limitations.append("Approved paper compile --fix replaced the TeX source from after_artifact evidence.")

    write["status"] = status
    write["sidecar_path"] = _rel(paths["fix_writeback"])
    evidence = {
        "schema": "paper_compile_fix_writeback.v1",
        "task_id": f"task-compile-fix:{_slug(str(target_path or 'target'))}",
        "sprint_id": str(envelope.get("sprint_id") or "sprint-autosci"),
        "node_id": f"node-compile-fix:{_slug(str(target_path or 'target'))}",
        "status": status,
        "inputs": inputs,
        "outputs": {"write": write},
        "artifacts": artifacts,
        "provenance": {
            "operator_id": "autosci-bridge",
            "implementation_package": "plugins/autosci",
            "timestamp": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        },
        "limitations": limitations,
    }
    artifact = {"type": "paper_compile_fix_writeback_json", "path": _write_evidence_payload(paths["fix_writeback"], evidence)}
    return {
        "requested": True,
        "applied": status == "completed",
        "status": status,
        "artifact": artifact,
        "artifacts": artifacts,
        "limitations": limitations,
        "write": write,
    }


def _allowlist_payloads(contract: dict[str, Any]) -> list[dict[str, Any]]:
    payloads: list[dict[str, Any]] = []
    entries = contract.get("allowlist_evidence") if isinstance(contract.get("allowlist_evidence"), list) else []
    for entry in entries:
        if not isinstance(entry, dict) or not entry.get("exists"):
            continue
        raw_path = str(entry.get("path") or entry.get("artifact_path") or "").strip()
        if not raw_path:
            continue
        path = _resolve_harness_path(raw_path)
        if path.is_dir():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            payload = {"commands": [line.strip() for line in text.splitlines() if line.strip()]}
        if isinstance(payload, dict):
            payloads.append(payload)
    return payloads


def _tokenize_command_text(raw: str) -> list[str]:
    if not raw:
        return []
    try:
        tokens = shlex.split(raw)
    except ValueError:
        return [raw]
    if not tokens:
        return []

    # Some environments place repositories under paths with spaces.
    # If the split broke the executable path, recover by joining prefix tokens
    # until a concrete file path exists.
    first = tokens[0]
    if Path(first).exists() or _resolve_harness_path(first).exists():
        return tokens

    for idx in range(2, min(len(tokens), 8) + 1):
        candidate = " ".join(tokens[:idx])
        if Path(candidate).exists() or _resolve_harness_path(candidate).exists():
            return [candidate] + tokens[idx:]

    return tokens


def _command_allowlisted(command: list[str], contract: dict[str, Any]) -> tuple[bool, str]:
    if not command:
        return False, "empty command"
    command_text = " ".join(command)
    executable = Path(command[0]).name
    for payload in _allowlist_payloads(contract):
        executables = [str(item) for item in payload.get("executables", []) if str(item).strip()]
        if executable in executables or command[0] in executables:
            return True, f"executable allowlisted: {executable}"
        for key in ("commands", "allowed_commands"):
            values = [str(item) for item in payload.get(key, []) if str(item).strip()]
            if command_text in values or command[0] in values or executable in values:
                return True, f"command allowlisted by {key}"
            for value in values:
                template_tokens = _tokenize_command_text(value)
                if not template_tokens:
                    continue
                if len(template_tokens) != len(command):
                    continue
                matched = True
                for command_token, template_token in zip(command, template_tokens):
                    if "{" in template_token and "}" in template_token:
                        continue
                    if command_token != template_token:
                        matched = False
                        break
                if matched:
                    return True, f"command allowlist template matched by {key}"
        prefixes = [str(item) for item in payload.get("allowed_prefixes", []) if str(item).strip()]
        if any(command_text.startswith(prefix) for prefix in prefixes):
            return True, "command allowlisted by prefix"
    return False, f"command is not allowlisted: {command_text}"


def _command_from_template(raw: Any, values: dict[str, str]) -> list[str]:
    if isinstance(raw, list):
        parts = [str(item) for item in raw if str(item).strip()]
    elif isinstance(raw, str):
        parts = _tokenize_command_text(raw)
    else:
        return []
    return [part.format(**values) for part in parts]


def _poster_render_command(contract: dict[str, Any], html_path: Path, png_path: Path, validation_path: Path) -> tuple[list[str], str]:
    values = {
        "html": str(html_path),
        "png": str(png_path),
        "validation": str(validation_path),
    }
    for payload in _allowlist_payloads(contract):
        command = _command_from_template(payload.get("poster_render_command"), values)
        if command:
            return command, "poster_render_command allowlisted"
        renderer = str(payload.get("poster_renderer") or "").strip()
        if renderer:
            return [renderer, values["html"], values["png"], values["validation"]], "poster_renderer allowlisted"
    return [], "No poster_render_command or poster_renderer was found in allowlist evidence."


def _format_command(raw: Any, values: dict[str, str]) -> list[str]:
    if isinstance(raw, list):
        rendered: list[str] = []
        for item in raw:
            text = str(item).strip()
            if not text:
                continue
            try:
                text = text.format(**values)
            except (KeyError, IndexError):
                pass
            rendered.append(text)
        return rendered
    text = str(raw).strip()
    if not text:
        return []
    try:
        text = text.format(**values)
    except (KeyError, IndexError):
        pass
    return _tokenize_command_text(text)


def _iter_experiment_run_commands(
    plan: dict[str, Any],
    contract: dict[str, Any],
    experiment_id: str,
) -> list[tuple[list[str], str]]:
    values = {"experiment_id": experiment_id}
    commands: list[tuple[list[str], str]] = []
    for raw in list(plan.get("command_allowlist") or []):
        parsed = _format_command(raw, values)
        if parsed:
            commands.append((parsed, "plan"))
    for payload in _allowlist_payloads(contract):
        for key in ("commands", "allowed_commands"):
            candidates = payload.get(key, [])
            for raw in candidates if isinstance(candidates, list) else []:
                parsed = _format_command(raw, values)
                if parsed:
                    commands.append((parsed, f"allowlist:{key}"))
    return commands


def _normalize_command(command: list[str]) -> list[str]:
    if not command:
        return []
    resolved = list(command)
    candidate = _resolve_harness_path(resolved[0])
    if candidate.exists():
        resolved[0] = str(candidate)
    return resolved


def _pick_experiment_command(
    plan: dict[str, Any],
    contract: dict[str, Any],
    experiment_id: str,
) -> tuple[list[str], str]:
    for command, source in _iter_experiment_run_commands(plan, contract, experiment_id):
        allowed, reason = _command_allowlisted(command, contract)
        if allowed:
            return command, f"Experiment command selected from {source}: {reason}"
    reason = "No experiment command was selected"
    candidate_commands = [" ".join(item[0]) for item in _iter_experiment_run_commands(plan, contract, experiment_id)]
    if not candidate_commands:
        return [], reason
    return [], f"{reason}; tried: {candidate_commands}"


def _runtime_evidence_payload(
    envelope: dict[str, Any],
    *,
    action: str,
    status: str,
    approval_ref: str,
    command_run: str,
    exit_code: int,
    evidence_ids: list[str],
    checks: list[dict[str, Any]],
    runtime_fields: dict[str, Any],
    artifacts: list[dict[str, str]],
    limitations: list[str],
) -> dict[str, Any]:
    return {
        "schema": "autosci_runtime_evidence.v1",
        "task_id": str(envelope.get("task_id") or f"runtime-{action}"),
        "sprint_id": str(envelope.get("sprint_id") or f"runtime-{action}"),
        "node_id": str(envelope.get("node_id") or f"node-runtime-{action}"),
        "status": status,
        "inputs": {"approval_ref": approval_ref},
        "outputs": {
            "runtime": {
                "action": action,
                "status": status,
                "approval_ref": approval_ref,
                "command_run": command_run,
                "exit_code": exit_code,
                "evidence_ids": evidence_ids,
                "checks": checks,
                **runtime_fields,
            }
        },
        "artifacts": artifacts,
        "provenance": {
            "operator_id": "autosci-approved-side-effect-executor",
            "implementation_package": "plugins/autosci",
            "timestamp": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        },
        "limitations": limitations,
    }


def _latex_tool_paths() -> dict[str, str]:
    return {name: shutil.which(name) or "" for name in ("latexmk", "pdflatex", "xelatex", "lualatex")}


def _paper_compile_command(tool_name: str, tool_path: str, tex_path: Path) -> list[str]:
    if tool_name == "latexmk":
        return [tool_path, "-pdf", "-interaction=nonstopmode", "-halt-on-error", tex_path.name]
    return [tool_path, "-interaction=nonstopmode", "-halt-on-error", tex_path.name]


def _select_paper_compile_command(
    latex_tool_paths: dict[str, str],
    contract: dict[str, Any],
    tex_path: Path,
) -> tuple[str, list[str], str, list[str], list[str]]:
    available = [name for name, path in latex_tool_paths.items() if path]
    rejected: list[str] = []
    for tool_name in ("latexmk", "pdflatex", "xelatex", "lualatex"):
        tool_path = latex_tool_paths.get(tool_name, "")
        if not tool_path:
            continue
        command = _paper_compile_command(tool_name, tool_path, tex_path)
        allowed, allow_reason = _command_allowlisted(command, contract)
        if allowed:
            return tool_name, command, allow_reason, available, rejected
        rejected.append(f"{tool_name}: {allow_reason}")
    if not available:
        return "", [], "No supported TeX executor was found on PATH.", available, rejected
    return "", [], "No available TeX executor was allowlisted: " + "; ".join(rejected), available, rejected


def _execute_paper_compile_if_approved(
    envelope: dict[str, Any],
    contract: dict[str, Any],
    latex_files: list[Path],
    latex_tool_paths: dict[str, str],
) -> tuple[dict[str, Any], dict[str, Any]]:
    inputs = envelope.get("inputs") if isinstance(envelope.get("inputs"), dict) else {}
    if not bool(inputs.get("execute_approved_side_effect")):
        return contract, {"executed": False, "reason": "execute_approved_side_effect=false"}
    output_dir = _output_dir(envelope, "compile_paper")
    runtime_path = _configured_output_path(envelope, "runtime_evidence_path", output_dir / "compile_paper_runtime_evidence.json")
    if not contract.get("ready_for_execution"):
        payload = _runtime_evidence_payload(
            envelope,
            action="compile_paper",
            status="inconclusive",
            approval_ref=str(contract.get("approval_ref") or ""),
            command_run="blocked:approval-contract-incomplete",
            exit_code=1,
            evidence_ids=["paper-compile-runtime:blocked"],
            checks=[{"check": "approval_preflight", "status": "error", "detail": "Approval contract was not ready for execution."}],
            runtime_fields={"pdf_generated": False},
            artifacts=[],
            limitations=["Paper compile executor did not run because approval preflight was incomplete."],
        )
        runtime_rel = _write_json_sidecar(runtime_path, payload)
        contract.setdefault("runtime_evidence", []).append({"path": runtime_rel, "artifact_path": runtime_rel, "exists": True, "kind": "file", "verifiable": True})
        return _refresh_approval_contract(contract), {"executed": False, "reason": "approval_preflight_incomplete", "runtime_path": runtime_rel}
    if not latex_files:
        return contract, {"executed": False, "reason": "no_latex_source"}
    tex_path = latex_files[0]
    executor_name, command, allow_reason, available_tools, rejected_tools = _select_paper_compile_command(
        latex_tool_paths,
        contract,
        tex_path,
    )
    if not command:
        payload = _runtime_evidence_payload(
            envelope,
            action="compile_paper",
            status="inconclusive",
            approval_ref=str(contract.get("approval_ref") or ""),
            command_run="blocked:tex-executor-unavailable-or-not-allowlisted",
            exit_code=1,
            evidence_ids=["paper-compile-runtime:blocked"],
            checks=[
                {
                    "check": "tex_executor_available",
                    "status": "ok" if available_tools else "error",
                    "detail": ", ".join(available_tools) if available_tools else "No supported TeX executor was found on PATH.",
                },
                {"check": "command_allowlisted", "status": "error", "detail": allow_reason},
            ],
            runtime_fields={"pdf_generated": False, "available_tex_executors": available_tools, "rejected_tex_executors": rejected_tools},
            artifacts=[],
            limitations=["Paper compile executor did not run because no available TeX executor was allowlisted."],
        )
        runtime_rel = _write_json_sidecar(runtime_path, payload)
        contract.setdefault("runtime_evidence", []).append({"path": runtime_rel, "artifact_path": runtime_rel, "exists": True, "kind": "file", "verifiable": True})
        reason = "tex_executor_not_found" if not available_tools else "command_not_allowlisted"
        return _refresh_approval_contract(contract), {"executed": False, "reason": reason, "runtime_path": runtime_rel}

    proc = subprocess.run(
        command,
        cwd=tex_path.parent,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=int(inputs.get("executor_timeout_seconds") or 120),
    )
    pdf_path = tex_path.with_suffix(".pdf")
    pdf_generated = proc.returncode == 0 and pdf_path.exists()
    stdout_path = output_dir / "compile_paper_executor_stdout.txt"
    stderr_path = output_dir / "compile_paper_executor_stderr.txt"
    stdout_rel = _write_text_sidecar(stdout_path, proc.stdout)
    stderr_rel = _write_text_sidecar(stderr_path, proc.stderr)
    artifacts = [
        {"type": "executor_stdout", "path": stdout_rel},
        {"type": "executor_stderr", "path": stderr_rel},
    ]
    if pdf_path.exists():
        artifacts.append(_artifact("compiled_pdf", pdf_path))
    payload = _runtime_evidence_payload(
        envelope,
        action="compile_paper",
        status="completed" if pdf_generated else "failed",
        approval_ref=str(contract.get("approval_ref") or ""),
        command_run=" ".join(command),
        exit_code=int(proc.returncode),
        evidence_ids=[f"paper-compile-runtime:{executor_name}", _rel(tex_path)],
        checks=[
            {"check": "command_allowlisted", "status": "ok", "detail": allow_reason},
            {"check": "tex_executor", "status": "ok", "detail": executor_name},
            {"check": "exit_code", "status": "ok" if proc.returncode == 0 else "error", "detail": f"exit_code={proc.returncode}"},
            {"check": "pdf_generated", "status": "ok" if pdf_generated else "error", "detail": _rel(pdf_path) if pdf_path.exists() else "PDF was not found after executor run."},
        ],
        runtime_fields={
            "pdf_generated": pdf_generated,
            "pdf_path": _rel(pdf_path) if pdf_path.exists() else "",
            "tex_executor": executor_name,
            "available_tex_executors": available_tools,
        },
        artifacts=artifacts,
        limitations=[f"Approved paper compile executor ran {executor_name} locally."],
    )
    runtime_rel = _write_json_sidecar(runtime_path, payload)
    contract.setdefault("runtime_evidence", []).append({"path": runtime_rel, "artifact_path": runtime_rel, "exists": True, "kind": "file", "verifiable": True})
    if pdf_path.exists():
        contract.setdefault("after_artifacts", []).append({"path": _rel(pdf_path), "artifact_path": _rel(pdf_path), "exists": True, "kind": "file", "verifiable": True})
    return _refresh_approval_contract(contract), {
        "executed": True,
        "executor": executor_name,
        "exit_code": proc.returncode,
        "pdf_path": pdf_path,
        "runtime_path": runtime_rel,
    }


def _parse_experiment_output_record(stdout_text: str) -> tuple[dict[str, Any] | None, str]:
    text = (stdout_text or "").strip()
    if not text:
        return None, ""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if lines:
        for line in reversed(lines):
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(payload, dict):
                continue
            if payload.get("schema") == "experiment_result.v1":
                result = ((payload.get("outputs") or {}).get("result") or {})
                return result if isinstance(result, dict) else payload, "experiment_result_payload"
            if isinstance(payload.get("result"), dict):
                return payload["result"], "result_key"
            return payload, "experiment_result_key_value"
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return None, ""
    if not isinstance(payload, dict):
        return None, ""
    if payload.get("schema") == "experiment_result.v1":
        result = ((payload.get("outputs") or {}).get("result") or {})
        return result if isinstance(result, dict) else payload, "experiment_result_payload"
    if isinstance(payload.get("result"), dict):
        return payload["result"], "result_key"
    return payload, "experiment_result_key_value"


def _execute_experiment_if_approved(
    envelope: dict[str, Any],
    contract: dict[str, Any],
    plan: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    inputs = envelope.get("inputs") if isinstance(envelope.get("inputs"), dict) else {}
    output_dir = _output_dir(envelope, "run_experiment")
    runtime_path = _configured_output_path(envelope, "runtime_evidence_path", output_dir / "run_experiment_runtime_evidence.json")
    if not bool(inputs.get("execute_approved_side_effect")):
        return contract, {"executed": False, "reason": "execute_approved_side_effect=false"}
    experiment_id = str(inputs.get("experiment_id") or inputs.get("target") or plan.get("experiment_id") or "experiment-unresolved")
    if not contract.get("ready_for_execution"):
        payload = _runtime_evidence_payload(
            envelope,
            action="run_experiment",
            status="inconclusive",
            approval_ref=str(contract.get("approval_ref") or ""),
            command_run="blocked:approval-contract-incomplete",
            exit_code=1,
            evidence_ids=["experiment-runtime:blocked"],
            checks=[{"check": "approval_preflight", "status": "error", "detail": "Approval contract was not ready for execution."}],
            runtime_fields={"result_collected": False},
            artifacts=[],
            limitations=["Experiment executor did not run because approval preflight was incomplete."],
        )
        runtime_rel = _write_json_sidecar(runtime_path, payload)
        contract.setdefault("runtime_evidence", []).append({"path": runtime_rel, "artifact_path": runtime_rel, "exists": True, "kind": "file", "verifiable": True})
        return _refresh_approval_contract(contract), {"executed": False, "reason": "approval_preflight_incomplete", "runtime_path": runtime_rel}

    command, command_reason = _pick_experiment_command(plan, contract, experiment_id)
    if not command:
        payload = _runtime_evidence_payload(
            envelope,
            action="run_experiment",
            status="inconclusive",
            approval_ref=str(contract.get("approval_ref") or ""),
            command_run="blocked:experiment-command-availability",
            exit_code=1,
            evidence_ids=["experiment-runtime:blocked"],
            checks=[{"check": "command_allowlisted", "status": "error", "detail": command_reason}],
            runtime_fields={"result_collected": False},
            artifacts=[],
            limitations=["Experiment executor did not run because no allowlisted command was selected."],
        )
        runtime_rel = _write_json_sidecar(runtime_path, payload)
        contract.setdefault("runtime_evidence", []).append({"path": runtime_rel, "artifact_path": runtime_rel, "exists": True, "kind": "file", "verifiable": True})
        return _refresh_approval_contract(contract), {"executed": False, "reason": "experiment_command_missing", "runtime_path": runtime_rel}

    command = _normalize_command(command)
    proc = subprocess.run(
        command,
        cwd=REPO_HARNESS_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=int(inputs.get("executor_timeout_seconds") or 120),
    )
    stdout_rel = _write_text_sidecar(output_dir / "run_experiment_executor_stdout.txt", proc.stdout)
    stderr_rel = _write_text_sidecar(output_dir / "run_experiment_executor_stderr.txt", proc.stderr)
    artifacts = [
        {"type": "executor_stdout", "path": stdout_rel},
        {"type": "executor_stderr", "path": stderr_rel},
    ]
    result_record, result_source = _parse_experiment_output_record(proc.stdout)
    result_payload: dict[str, Any] = {}
    if result_record:
        result_payload.update({
            "experiment_id": str(result_record.get("experiment_id") or experiment_id),
            "outcome": str(result_record.get("outcome") or "supports"),
            "metrics": list(result_record.get("metrics") or []),
            "evidence_ids": list(result_record.get("evidence_ids") or []),
            "logs": list(result_record.get("logs") or []),
        })
        if not result_payload["evidence_ids"]:
            result_payload["evidence_ids"] = [f"experiment-runtime:{_slug(experiment_id)}"]
        if not result_payload["metrics"]:
            result_payload["metrics"] = [{"name": "experiment_exit_code", "value": int(proc.returncode)}]
    else:
        result_payload = {
            "experiment_id": experiment_id,
            "outcome": "supports" if proc.returncode == 0 else "failed",
            "metrics": [{"name": "experiment_exit_code", "value": int(proc.returncode)}],
            "evidence_ids": [f"experiment-runtime:{_slug(experiment_id)}"],
            "logs": ["Experiment command executed without parseable experiment payload."],
        }
    result_collected = bool(result_record) or bool(proc.stdout.strip())

    runtime_result_path = _configured_output_path(
        envelope,
        "experiment_result_path",
        output_dir / "run_experiment_result.json",
    )
    runtime_result_rel = _rel(runtime_result_path)
    runtime_result_json: dict[str, Any] = {
        "schema": "experiment_result.v1",
        "task_id": str(envelope.get("task_id") or f"runtime-{_slug(experiment_id)}"),
        "sprint_id": str(envelope.get("sprint_id") or "runtime-run-experiment"),
        "node_id": str(envelope.get("node_id") or "node-runtime-run-experiment"),
        "status": "completed" if result_collected else "inconclusive",
        "inputs": dict(envelope.get("inputs") or {}),
        "outputs": {"result": result_payload},
        "artifacts": [{"type": "run_experiment_result_json", "path": runtime_result_rel}],
        "provenance": {
            "operator_id": "autosci-experiment-runner",
            "implementation_package": "plugins/autosci",
            "timestamp": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        },
        "limitations": [f"Experiment result generated from command output source={result_source}."],
    }
    runtime_result_rel = _write_json_sidecar(runtime_result_path, runtime_result_json)
    artifacts.append({"type": "run_experiment_result", "path": runtime_result_rel})
    result_collected = bool(result_record) or bool(proc.stdout.strip())
    payload = _runtime_evidence_payload(
        envelope,
        action="run_experiment",
        status="completed" if proc.returncode == 0 and result_collected else "failed",
        approval_ref=str(contract.get("approval_ref") or ""),
        command_run=" ".join(command),
        exit_code=int(proc.returncode),
        evidence_ids=[str(item) for item in result_payload.get("evidence_ids") or [f"experiment-runtime:{_slug(experiment_id)}"] if str(item).strip()],
        checks=[
            {"check": "command_allowlisted", "status": "ok", "detail": command_reason},
            {"check": "exit_code", "status": "ok" if proc.returncode == 0 else "error", "detail": f"exit_code={proc.returncode}"},
            {"check": "result_collected", "status": "ok" if result_collected else "warn", "detail": str(result_collected)},
            {"check": "result_payload_source", "status": "ok" if result_source else "warn", "detail": result_source or "not-structured"},
        ],
        runtime_fields={
            "result_collected": result_collected,
            "result_path": runtime_result_rel,
            "result": result_payload,
            "result_artifacts": [runtime_result_rel],
            "parsed_record_count": 1 if result_record else 0,
        },
        artifacts=artifacts,
        limitations=["Approved experiment executor ran a real command locally (subject to allowlist and approval contract)."],
    )
    runtime_rel = _write_json_sidecar(runtime_path, payload)
    contract.setdefault("runtime_evidence", []).append({"path": runtime_rel, "artifact_path": runtime_rel, "exists": True, "kind": "file", "verifiable": True})
    contract.setdefault("after_artifacts", []).append({
        "path": runtime_result_rel,
        "artifact_path": runtime_result_rel,
        "exists": True,
        "kind": "file",
        "verifiable": True,
    })
    return _refresh_approval_contract(contract), {
        "executed": True,
        "command": command,
        "exit_code": proc.returncode,
        "runtime_path": runtime_rel,
        "result_path": runtime_result_path,
        "stdout_path": stdout_rel,
        "stderr_path": stderr_rel,
        "result_collected": result_collected,
    }


def _load_runtime_validation(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _execute_poster_if_approved(
    envelope: dict[str, Any],
    contract: dict[str, Any],
    html_path: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    inputs = envelope.get("inputs") if isinstance(envelope.get("inputs"), dict) else {}
    if not bool(inputs.get("execute_approved_side_effect")):
        return contract, {"executed": False, "reason": "execute_approved_side_effect=false"}
    output_dir = _output_dir(envelope, "build_poster")
    runtime_path = _configured_output_path(envelope, "runtime_evidence_path", output_dir / "poster_runtime_evidence.json")
    png_path = _configured_output_path(envelope, "poster_png_path", output_dir / "poster.png")
    executor_validation_path = _configured_output_path(
        envelope,
        "poster_executor_validation_path",
        output_dir / "poster_executor_validation.json",
    )
    if not contract.get("ready_for_execution"):
        payload = _runtime_evidence_payload(
            envelope,
            action="build_poster",
            status="inconclusive",
            approval_ref=str(contract.get("approval_ref") or ""),
            command_run="blocked:approval-contract-incomplete",
            exit_code=1,
            evidence_ids=["poster-runtime:blocked"],
            checks=[{"check": "approval_preflight", "status": "error", "detail": "Approval contract was not ready for execution."}],
            runtime_fields={"browser_rendered": False, "png_exported": False, "overflow_probe": "not_run"},
            artifacts=[],
            limitations=["Poster executor did not run because approval preflight was incomplete."],
        )
        runtime_rel = _write_json_sidecar(runtime_path, payload)
        contract.setdefault("runtime_evidence", []).append({"path": runtime_rel, "artifact_path": runtime_rel, "exists": True, "kind": "file", "verifiable": True})
        return _refresh_approval_contract(contract), {"executed": False, "reason": "approval_preflight_incomplete", "runtime_path": runtime_rel}

    command, allow_reason = _poster_render_command(contract, html_path, png_path, executor_validation_path)
    if not command:
        payload = _runtime_evidence_payload(
            envelope,
            action="build_poster",
            status="inconclusive",
            approval_ref=str(contract.get("approval_ref") or ""),
            command_run="blocked:poster-render-command-missing",
            exit_code=1,
            evidence_ids=["poster-runtime:blocked"],
            checks=[{"check": "poster_render_command", "status": "error", "detail": allow_reason}],
            runtime_fields={"browser_rendered": False, "png_exported": False, "overflow_probe": "not_run"},
            artifacts=[],
            limitations=["Poster executor did not run because no allowlisted render command was supplied."],
        )
        runtime_rel = _write_json_sidecar(runtime_path, payload)
        contract.setdefault("runtime_evidence", []).append({"path": runtime_rel, "artifact_path": runtime_rel, "exists": True, "kind": "file", "verifiable": True})
        return _refresh_approval_contract(contract), {"executed": False, "reason": "poster_render_command_missing", "runtime_path": runtime_rel}

    output_dir.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        command,
        cwd=output_dir,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=int(inputs.get("executor_timeout_seconds") or 120),
    )
    stdout_rel = _write_text_sidecar(output_dir / "poster_executor_stdout.txt", proc.stdout)
    stderr_rel = _write_text_sidecar(output_dir / "poster_executor_stderr.txt", proc.stderr)
    validation = _load_runtime_validation(executor_validation_path)
    browser_rendered = _truthy(validation.get("browser_rendered") if validation else png_path.exists())
    png_exported = _truthy(validation.get("png_exported") if validation else png_path.exists()) or png_path.exists()
    overflow_probe = str(validation.get("overflow_probe") or "not_run")
    overflow_ok = overflow_probe.strip().lower() in {"ok", "pass", "passed", "none", "no_overflow"}
    runtime_ok = proc.returncode == 0 and browser_rendered and png_exported and overflow_ok and png_path.exists()
    artifacts = [
        {"type": "executor_stdout", "path": stdout_rel},
        {"type": "executor_stderr", "path": stderr_rel},
    ]
    if executor_validation_path.exists():
        artifacts.append(_artifact("poster_executor_validation_json", executor_validation_path))
    if png_path.exists():
        artifacts.append(_artifact("poster_png", png_path))
    payload = _runtime_evidence_payload(
        envelope,
        action="build_poster",
        status="completed" if runtime_ok else "failed",
        approval_ref=str(contract.get("approval_ref") or ""),
        command_run=" ".join(command),
        exit_code=int(proc.returncode),
        evidence_ids=["poster-runtime:render", _rel(html_path)],
        checks=[
            {"check": "poster_render_command", "status": "ok", "detail": allow_reason},
            {"check": "exit_code", "status": "ok" if proc.returncode == 0 else "error", "detail": f"exit_code={proc.returncode}"},
            {"check": "browser_rendered", "status": "ok" if browser_rendered else "error", "detail": str(browser_rendered)},
            {"check": "overflow_probe", "status": "ok" if overflow_ok else "error", "detail": overflow_probe},
            {"check": "png_exported", "status": "ok" if png_exported and png_path.exists() else "error", "detail": _rel(png_path) if png_path.exists() else "PNG was not found after executor run."},
        ],
        runtime_fields={
            "browser_rendered": browser_rendered,
            "png_exported": bool(png_exported and png_path.exists()),
            "overflow_probe": overflow_probe,
            "png_path": _rel(png_path) if png_path.exists() else "",
        },
        artifacts=artifacts,
        limitations=["Approved poster executor ran an allowlisted render command locally."],
    )
    runtime_rel = _write_json_sidecar(runtime_path, payload)
    contract.setdefault("runtime_evidence", []).append({"path": runtime_rel, "artifact_path": runtime_rel, "exists": True, "kind": "file", "verifiable": True})
    if png_path.exists():
        contract.setdefault("after_artifacts", []).append({"path": _rel(png_path), "artifact_path": _rel(png_path), "exists": True, "kind": "file", "verifiable": True})
    if executor_validation_path.exists():
        contract.setdefault("after_artifacts", []).append({
            "path": _rel(executor_validation_path),
            "artifact_path": _rel(executor_validation_path),
            "exists": True,
            "kind": "file",
            "verifiable": True,
        })
    return _refresh_approval_contract(contract), {
        "executed": True,
        "exit_code": proc.returncode,
        "png_path": png_path,
        "runtime_path": runtime_rel,
    }


def _check_row(check: str, status: str, detail: str, evidence: list[str] | None = None) -> dict[str, Any]:
    return {
        "check": check,
        "status": status,
        "detail": detail,
        "evidence": evidence or [],
    }


def _render_compile_diagnostics(checklist: dict[str, Any]) -> str:
    lines = [
        "# Paper Compile Checklist Diagnostics",
        "",
        f"Target: {checklist.get('target_raw') or 'N/A'}",
        f"Resolved target: {checklist.get('target_resolved') or 'N/A'}",
        f"Status: {checklist.get('status') or 'N/A'}",
        "",
        "| Check | Status | Detail |",
        "| --- | --- | --- |",
    ]
    for row in checklist.get("checks") or []:
        if not isinstance(row, dict):
            continue
        detail = str(row.get("detail") or "N/A").replace("|", "\\|")
        lines.append(f"| {row.get('check', 'N/A')} | {row.get('status', 'N/A')} | {detail} |")
    lines.extend(["", "## Files", ""])
    for key in ("latex_files", "pdf_files", "markdown_files", "bibliography_files"):
        values = checklist.get(key) if isinstance(checklist.get(key), list) else []
        lines.append(f"- {key}: {', '.join(str(item) for item in values) if values else 'N/A'}")
    limitations_list = checklist.get("limitations") if isinstance(checklist.get("limitations"), list) else []
    if limitations_list:
        lines.extend(["", "## Limitations", ""])
        lines.extend(f"- {limitation}" for limitation in limitations_list)
    return "\n".join(lines).rstrip() + "\n"


def _paper_compile_raw(envelope: dict[str, Any]) -> dict[str, Any]:
    inputs = envelope.get("inputs") if isinstance(envelope.get("inputs"), dict) else {}
    paths = _paper_compile_paths(envelope)
    target_raw, target_path = _paper_compile_target(envelope)
    candidates = _compile_source_candidates(target_path)
    latex_files = candidates["latex"]
    pdf_files = candidates["pdf"]
    markdown_files = candidates["markdown"]
    bibliography_files = candidates["bibliography"]
    latex_tool_paths = _latex_tool_paths()
    available_tex_executors = {name: path for name, path in latex_tool_paths.items() if path}
    latexmk_path = latex_tool_paths.get("latexmk", "")
    checklist_requested = bool(inputs.get("checklist"))
    fix_requested = bool(inputs.get("fix"))
    target_exists = bool(target_path and target_path.exists())
    target_detail = str(target_path) if target_path else "No target or paper_path was provided."
    checklist_paths = [_rel(paths["checklist"]), _rel(paths["diagnostics"])]
    contract = _approval_contract(
        envelope,
        "compile_paper",
        ["tex_executor_execution", "source_auto_fix", "pdf_generation"],
    )
    fix_result = _paper_compile_fix_if_approved(envelope, contract, target_path, latex_files)
    if fix_result.get("applied"):
        candidates = _compile_source_candidates(target_path)
        latex_files = candidates["latex"]
        pdf_files = candidates["pdf"]
        markdown_files = candidates["markdown"]
        bibliography_files = candidates["bibliography"]
    contract, executor_result = _execute_paper_compile_if_approved(envelope, contract, latex_files, latex_tool_paths)
    if executor_result.get("executed"):
        candidates = _compile_source_candidates(target_path)
        latex_files = candidates["latex"]
        pdf_files = candidates["pdf"]
        markdown_files = candidates["markdown"]
        bibliography_files = candidates["bibliography"]
    semantic = _approval_semantic_runtime(contract, "compile_paper")
    contract["semantic_runtime"] = semantic
    contract_artifact = _write_approval_contract_sidecar(envelope, "compile_paper", contract)
    runtime_artifacts = _contract_existing_artifacts(contract, "after_artifacts", "compile_runtime_after_artifact")
    runtime_evidence_artifacts = _contract_existing_artifacts(contract, "runtime_evidence", "compile_runtime_evidence_json")

    checks = [
        _check_row(
            "target_resolved",
            "ok" if target_exists else "error",
            f"Resolved to {target_detail}" if target_exists else target_detail,
            [_rel(target_path)] if target_exists and target_path else [],
        ),
        _check_row(
            "latex_source_present",
            "ok" if latex_files else "warn",
            f"{len(latex_files)} LaTeX source file(s) found." if latex_files else "No .tex source files were found.",
            [_rel(path) for path in latex_files],
        ),
        _check_row(
            "compiled_pdf_present",
            "ok" if pdf_files else "warn",
            f"{len(pdf_files)} PDF file(s) found." if pdf_files else "No compiled PDF was found.",
            [_rel(path) for path in pdf_files],
        ),
        _check_row(
            "bibliography_present",
            "ok" if bibliography_files else "warn",
            f"{len(bibliography_files)} BibTeX file(s) found." if bibliography_files else "No .bib files were found.",
            [_rel(path) for path in bibliography_files],
        ),
        _check_row(
            "latexmk_available",
            "ok" if latexmk_path else "warn",
            latexmk_path or "latexmk was not found on PATH; approved execution may use another allowlisted TeX executor.",
            [latexmk_path] if latexmk_path else [],
        ),
        _check_row(
            "tex_executor_available",
            "ok" if available_tex_executors else "warn",
            ", ".join(f"{name}={path}" for name, path in available_tex_executors.items())
            if available_tex_executors
            else "No supported TeX executor was found on PATH.",
            list(available_tex_executors.values()),
        ),
        _check_row(
            "checklist_requested",
            "ok" if checklist_requested else "warn",
            "Checklist mode was requested." if checklist_requested else "Checklist flag was not set.",
            checklist_paths,
        ),
        _check_row(
            "auto_fix_requested",
            "ok" if bool(fix_result.get("applied")) or not fix_requested else "warn",
            "Approved auto-fix applied from after_artifact evidence."
            if fix_result.get("applied")
            else "Auto-fix was requested but not applied; approval and after_artifact evidence are required."
            if fix_requested
            else "Auto-fix was not requested.",
            [fix_result["artifact"]["path"]] if fix_result.get("artifact") else [],
        ),
        _check_row(
            "compile_execution",
            "ok" if semantic.get("verified") else "warn",
            "Approved executor/runtime evidence verifies LaTeX/PDF compilation."
            if semantic.get("verified")
            else (
                f"Approved executor did not complete: {executor_result.get('reason') or 'semantic runtime incomplete'}"
                if inputs.get("execute_approved_side_effect")
                else "The bridge produced compile diagnostics only; it did not run a TeX executor or mutate sources."
            ),
        ),
        _check_row(
            "approval_contract_verified",
            "ok" if contract.get("execution_verified") else "warn",
            "Approval, allowlist, runtime, and before/after evidence are verified."
            if contract.get("execution_verified")
            else "Approval/runtime contract is incomplete; compile side effects were not executed by this bridge.",
            [contract_artifact["path"]],
        ),
        _check_row(
            "runtime_semantic_verified",
            "ok" if semantic.get("verified") else "warn",
            "Runtime evidence passed compile-specific semantic checks."
            if semantic.get("verified")
            else "Runtime evidence did not pass compile-specific semantic checks.",
            [contract_artifact["path"]],
        ),
    ]
    limitations = [
        "Paper compile currently performs a bounded checklist and diagnostics pass only.",
        "The bridge does not run a TeX executor, mutate source files, or claim PDF compilation without explicit approved execution.",
        *_approval_contract_limitations(contract),
    ]
    if semantic.get("verified"):
        if executor_result.get("executed"):
            limitations = ["Paper compile was executed by the approved side-effect executor and verified from runtime evidence."]
        else:
            limitations = [
                "Paper compile runtime was verified from supplied approval-gated evidence; this bridge did not execute a TeX executor.",
            ]
    if not target_exists:
        limitations.append("Paper compile target was missing or unresolved.")
    if not latex_files:
        limitations.append("No LaTeX source was found for native paper compilation.")
    if not pdf_files:
        limitations.append("No compiled PDF was found in the target path.")
    if fix_requested:
        limitations.extend(str(item) for item in fix_result.get("limitations") or [])
    status = (
        "completed"
        if target_exists and latex_files and (pdf_files or semantic.get("verified")) and (not fix_requested or bool(fix_result.get("applied")))
        else "inconclusive"
    )
    checklist_payload = {
        "schema": "paper_compile_checklist.v1",
        "status": status,
        "target_raw": target_raw,
        "target_resolved": str(target_path) if target_path else "",
        "requested": {
            "checklist": checklist_requested,
            "fix": fix_requested,
            "title": str(inputs.get("title") or ""),
        },
        "toolchain": {
            "latexmk_available": bool(latexmk_path),
            "latexmk_path": latexmk_path,
            "tex_executors": available_tex_executors,
            "selected_executor": str(executor_result.get("executor") or ""),
        },
        "approval_contract": contract,
        "runtime_semantic": semantic,
        "fix_writeback": fix_result.get("write"),
        "checks": checks,
        "latex_files": [_rel(path) for path in latex_files],
        "pdf_files": [_rel(path) for path in pdf_files],
        "markdown_files": [_rel(path) for path in markdown_files],
        "bibliography_files": [_rel(path) for path in bibliography_files],
        "limitations": limitations,
    }
    checklist_path = _write_json_sidecar(paths["checklist"], checklist_payload)
    diagnostics_path = _write_text_sidecar(paths["diagnostics"], _render_compile_diagnostics(checklist_payload))
    file_artifacts = [
        {"type": "paper_compile_checklist_json", "path": checklist_path},
        {"type": "paper_compile_diagnostics_markdown", "path": diagnostics_path},
        contract_artifact,
        *([fix_result["artifact"]] if fix_result.get("artifact") else []),
        *[artifact for artifact in fix_result.get("artifacts") or [] if isinstance(artifact, dict)],
        *runtime_evidence_artifacts,
        *runtime_artifacts,
        *[_artifact("latex_source", path) for path in latex_files],
        *[_artifact("compiled_pdf", path) for path in pdf_files],
        *[_artifact("paper_markdown_source", path) for path in markdown_files[:5]],
        *[_artifact("bibliography_source", path) for path in bibliography_files[:5]],
    ]
    source_report_id = f"paper-compile:{_slug(target_raw or 'target')}"
    return {
        "bundle_id": f"bundle-{_slug(source_report_id)}",
        "publication_type": "paper",
        "source_report_id": source_report_id,
        "files": file_artifacts,
        "evidence_ids": _unique_strings([
            source_report_id,
            "paper-compile-checklist",
            *[_rel(path) for path in latex_files[:5]],
            *[_rel(path) for path in pdf_files[:5]],
        ]),
        "artifacts": file_artifacts,
        "status": status,
        "limitations": limitations,
    }


def _action_compile_paper(envelope: dict[str, Any]) -> dict[str, Any]:
    return convert_publication_bundle(_paper_compile_raw(envelope), envelope)


PHASE16_COLLECTION_KEYS = (
    "failed_nodes",
    "gate_rejection_reasons",
    "ambiguous_manuals_or_prompts",
    "insufficient_schemas",
    "poor_operator_bindings",
    "human_intervention_points",
    "runtime_errors",
)


def _phase16_paths(envelope: dict[str, Any]) -> dict[str, Path]:
    output_dir = _output_dir(envelope, "evolve_workflow")
    return {
        "recommended_changes": _configured_output_path(
            envelope,
            "recommended_changes_path",
            output_dir / "recommended_changes.md",
        ),
        "patch_candidates": _configured_output_path(
            envelope,
            "patch_candidates_path",
            output_dir / "patch_candidates",
        ),
    }


def _phase16_failed_run(envelope: dict[str, Any]) -> dict[str, Any]:
    inputs = dict(envelope.get("inputs") or {})
    inline = inputs.get("failed_run") or inputs.get("workflow_run") or inputs.get("postmortem")
    if isinstance(inline, dict):
        return inline
    for key in ("failed_run_path", "workflow_run_path", "lifecycle_summary_path", "postmortem_path"):
        payload = _load_optional_evidence(inputs.get(key))
        if payload:
            return payload
    return {
        "workflow_id": "unknown-workflow",
        "nodes": [],
        "gate_results": {},
        "runtime_errors": ["No failed run evidence was supplied."],
    }


def _phase16_failed_nodes(run: dict[str, Any]) -> list[dict[str, Any]]:
    explicit = run.get("failed_nodes")
    if isinstance(explicit, list):
        return [item for item in explicit if isinstance(item, dict)]
    failed: list[dict[str, Any]] = []
    node_results = run.get("node_results") if isinstance(run.get("node_results"), dict) else {}
    for node in run.get("nodes") or []:
        if not isinstance(node, dict):
            continue
        node_id = str(node.get("id") or node.get("node_id") or "")
        status = str(node.get("status") or "").lower()
        if node_id and isinstance(node_results.get(node_id), dict):
            status = str(node_results[node_id].get("status") or status).lower()
        if status in {"failed", "error", "inconclusive"}:
            failed.append({
                "node_id": node_id or f"node-{len(failed) + 1:03d}",
                "logical_operator": str(node.get("logical_operator") or "N/A"),
                "status": status,
                "gate": str(node.get("gate") or "N/A"),
            })
    return failed


def _phase16_gate_rejections(run: dict[str, Any]) -> list[dict[str, Any]]:
    explicit = run.get("gate_rejection_reasons")
    if isinstance(explicit, list):
        return [item for item in explicit if isinstance(item, dict)]
    gate_results = run.get("gate_results") if isinstance(run.get("gate_results"), dict) else {}
    rejections: list[dict[str, Any]] = []
    for gate_id, result in gate_results.items():
        if not isinstance(result, dict):
            continue
        status = str(result.get("status") or "").lower()
        if status not in {"failed", "error", "inconclusive"}:
            continue
        reasons = result.get("reasons") if isinstance(result.get("reasons"), list) else []
        if not reasons and result.get("reason"):
            reasons = [str(result["reason"])]
        rejections.append({
            "gate_id": str(gate_id),
            "status": status,
            "reasons": [str(item) for item in reasons if str(item).strip()] or ["Gate failed without a structured reason."],
        })
    return rejections


def _phase16_list_of_dicts(run: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = run.get(key)
    if not isinstance(value, list):
        return []
    items: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if isinstance(item, dict):
            items.append(item)
        elif str(item).strip():
            items.append({"id": f"{key}-{index + 1:03d}", "description": str(item)})
    return items


def _phase16_evidence_ids(collected: dict[str, list[dict[str, Any]]], run: dict[str, Any]) -> list[str]:
    ids: list[str] = []
    for key, items in collected.items():
        for item in items:
            for field in ("evidence_id", "node_id", "gate_id", "id", "artifact", "path"):
                value = item.get(field)
                if isinstance(value, str) and value.strip():
                    ids.append(value)
            values = item.get("evidence_ids")
            if isinstance(values, list):
                ids.extend(str(value) for value in values if str(value).strip())
    for field in ("workflow_id", "sprint_id", "task_id"):
        value = run.get(field)
        if isinstance(value, str) and value.strip():
            ids.append(value)
    return _unique_strings(ids) or ["workflow-run-missing-evidence"]


def _phase16_proposed_changes(collected: dict[str, list[dict[str, Any]]], evidence_ids: list[str]) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    if collected["failed_nodes"]:
        node_ids = ", ".join(str(item.get("node_id") or "N/A") for item in collected["failed_nodes"])
        changes.append({
            "change_id": "change.workflow-template.failed-node-recovery",
            "category": "workflow_template",
            "target": "scientific_research_lifecycle_full_v1",
            "description": f"Add or tighten recovery guidance for failed nodes: {node_ids}.",
            "evidence_ids": evidence_ids,
            "review_required": True,
            "application_state": "proposed_only",
        })
    if collected["gate_rejection_reasons"]:
        changes.append({
            "change_id": "change.gate.rejection-diagnostics",
            "category": "gate",
            "target": "scientific evaluator gates",
            "description": "Expose gate rejection reasons in the dispatch/evidence handoff before retry.",
            "evidence_ids": evidence_ids,
            "review_required": True,
            "application_state": "proposed_only",
        })
    if collected["ambiguous_manuals_or_prompts"]:
        changes.append({
            "change_id": "change.manual.ambiguity-clarification",
            "category": "manual",
            "target": "scientific dispatch manuals",
            "description": "Clarify ambiguous manual or prompt language cited by the failed run.",
            "evidence_ids": evidence_ids,
            "review_required": True,
            "application_state": "proposed_only",
        })
    if collected["insufficient_schemas"]:
        changes.append({
            "change_id": "change.schema.required-field-tightening",
            "category": "schema",
            "target": "scientific Evidence ABI schemas",
            "description": "Review whether missing fields should become schema requirements or deterministic gate checks.",
            "evidence_ids": evidence_ids,
            "review_required": True,
            "application_state": "proposed_only",
        })
    if collected["poor_operator_bindings"]:
        changes.append({
            "change_id": "change.routing.operator-binding",
            "category": "routing",
            "target": "logical-to-physical operator bindings",
            "description": "Review operator binding constraints for the cited poor bindings.",
            "evidence_ids": evidence_ids,
            "review_required": True,
            "application_state": "proposed_only",
        })
    if not changes:
        changes.append({
            "change_id": "change.other.collect-more-evidence",
            "category": "other",
            "target": "workflow postmortem collection",
            "description": "Collect more structured failure evidence before changing workflow behavior.",
            "evidence_ids": evidence_ids,
            "review_required": True,
            "application_state": "proposed_only",
        })
    return changes


def _phase16_markdown(raw: dict[str, Any]) -> str:
    collected = raw["collected"]
    lines = [
        "# Recommended Scientific Workflow Changes",
        "",
        "## Scope",
        "",
        str(raw.get("scope") or "scientific research workflow"),
        "",
        "## Failed Nodes",
        "",
    ]
    for node in collected["failed_nodes"] or [{"node_id": "N/A", "status": "N/A"}]:
        lines.append(f"- `{node.get('node_id', 'N/A')}` status `{node.get('status', 'N/A')}` gate `{node.get('gate', 'N/A')}`")
    lines.extend(["", "## Gate Rejection Reasons", ""])
    for rejection in collected["gate_rejection_reasons"] or [{"gate_id": "N/A", "reasons": ["N/A"]}]:
        reasons = "; ".join(str(item) for item in rejection.get("reasons") or ["N/A"])
        lines.append(f"- `{rejection.get('gate_id', 'N/A')}`: {reasons}")
    lines.extend(["", "## Proposed Changes", ""])
    for change in raw["proposed_changes"]:
        lines.append(
            "- "
            f"`{change.get('change_id', 'N/A')}` [{change.get('category', 'other')}] "
            f"{change.get('target', 'N/A')}: {change.get('description', 'N/A')}"
        )
    lines.extend([
        "",
        "## Patch Candidates",
        "",
        f"- Directory: `{raw.get('patch_candidates_path', 'N/A')}`",
        "- Status: proposed-only; no patch candidate is applied by this action.",
        "",
        "## Review Controls",
        "",
        "- Approval state: proposed",
        "- Protected core runtime edited: false",
        "- Human can accept or reject each proposed change independently.",
    ])
    return "\n".join(lines).rstrip() + "\n"


def _phase16_workflow_evolution_raw(envelope: dict[str, Any]) -> dict[str, Any]:
    run = _phase16_failed_run(envelope)
    collected = {
        "failed_nodes": _phase16_failed_nodes(run),
        "gate_rejection_reasons": _phase16_gate_rejections(run),
        "ambiguous_manuals_or_prompts": _phase16_list_of_dicts(run, "ambiguous_manuals_or_prompts"),
        "insufficient_schemas": _phase16_list_of_dicts(run, "insufficient_schemas"),
        "poor_operator_bindings": _phase16_list_of_dicts(run, "poor_operator_bindings"),
        "human_intervention_points": _phase16_list_of_dicts(run, "human_intervention_points"),
        "runtime_errors": _phase16_list_of_dicts(run, "runtime_errors"),
    }
    evidence_ids = _phase16_evidence_ids(collected, run)
    proposed_changes = _phase16_proposed_changes(collected, evidence_ids)
    paths = _phase16_paths(envelope)
    paths["patch_candidates"].mkdir(parents=True, exist_ok=True)
    scope = str(run.get("workflow_id") or run.get("sprint_id") or "scientific research workflow")
    raw = {
        "proposal_id": f"workflow-evolution-{_slug(scope)}",
        "scope": scope,
        "change_type": "workflow_template",
        "rationale": "A failed scientific workflow run exposed recoverable workflow, gate, manual, schema, or routing gaps.",
        "expected_effect": "Make future failures easier to diagnose and resume without silently changing protected runtime behavior.",
        "approval_state": "proposed",
        "evidence_ids": evidence_ids,
        "collected": collected,
        "proposed_changes": proposed_changes,
        "review": {
            "human_accept_reject_required": True,
            "protected_core_edits_applied": False,
            "application_state": "proposed_only",
            "approval_ref": "N/A",
        },
        "recommended_changes_path": _rel(paths["recommended_changes"]),
        "patch_candidates_path": _rel(paths["patch_candidates"]),
        "artifacts": [
            _artifact("recommended_changes_markdown", paths["recommended_changes"]),
            _artifact("patch_candidates_directory", paths["patch_candidates"]),
        ],
        "limitations": [
            "Workflow evolution output is a proposal only; it does not modify capsules, schemas, gates, routing, or workflows.",
            "Fixture analysis is bounded to supplied failed-run evidence and local deterministic extraction.",
        ],
    }
    _write_text_sidecar(paths["recommended_changes"], _phase16_markdown(raw))
    return raw


def _action_evolve_workflow(envelope: dict[str, Any]) -> dict[str, Any]:
    return convert_workflow_evolution(_phase16_workflow_evolution_raw(envelope), envelope)


def _control_workflow_paths(envelope: dict[str, Any], action: str) -> dict[str, Path]:
    output_dir = _output_dir(envelope, action)
    return {
        "recommended_changes": _configured_output_path(
            envelope,
            "recommended_changes_path",
            output_dir / "recommended_changes.md",
        ),
        "patch_candidates": _configured_output_path(
            envelope,
            "patch_candidates_path",
            output_dir / "patch_candidates",
        ),
    }


def _refine_apply_path(envelope: dict[str, Any]) -> Path:
    return _output_dir(envelope, "refine_artifact") / "refine_apply_writeback.json"


def _refine_target_path_for_write(envelope: dict[str, Any], target: str) -> tuple[Path | None, list[str]]:
    if not target.strip():
        return None, ["Refine apply requires an explicit target artifact path."]
    target_path = _resolve_harness_path(target)
    roots = [HARNESS_DIR, *_wiki_roots_for_write(envelope)]
    if not any(_path_is_under(target_path, root) for root in roots):
        return None, [f"Refine target is outside the allowed harness/wiki roots: {target}"]
    if not target_path.exists() or target_path.is_dir():
        return None, [f"Refine target does not resolve to an existing file: {target}"]
    return target_path, []


def _approved_refine_application(
    envelope: dict[str, Any],
    *,
    target: str,
    contract: dict[str, Any],
    evidence_ids: list[str],
) -> dict[str, Any] | None:
    if not _local_mutation_requested(envelope):
        return None

    inputs = dict(envelope.get("inputs") or {})
    after_artifacts = inputs.get("after_artifacts") if isinstance(inputs.get("after_artifacts"), list) else []
    status = "inconclusive"
    artifacts: list[dict[str, Any]] = []
    limitations: list[str] = []
    write: dict[str, Any] = {
        "requested": True,
        "applied": False,
        "approval_ref": str(contract.get("approval_ref") or "N/A"),
        "approval_state": str(contract.get("approval_state") or "unknown"),
        "target": target,
    }

    target_path: Path | None = None
    if not contract.get("execution_verified"):
        limitations.append("Refine apply requires verified approval, allowlist, runtime, before, and after artifacts.")
    elif not after_artifacts:
        limitations.append("Refine apply requires an after_artifact file containing the approved target contents.")
    else:
        target_path, target_errors = _refine_target_path_for_write(envelope, target)
        limitations.extend(target_errors)
        after_path = _resolve_harness_path(str(after_artifacts[0]))
        if not limitations and (not after_path.exists() or after_path.is_dir()):
            limitations.append("Refine apply after_artifact does not resolve to an existing file.")
        if not limitations and target_path is not None:
            before = target_path.read_text(encoding="utf-8", errors="replace")
            desired = after_path.read_text(encoding="utf-8", errors="replace")
            changed = _write_text_if_changed_bridge(target_path, desired)
            after = target_path.read_text(encoding="utf-8", errors="replace")
            wiki_root = next((root for root in _wiki_roots_for_write(envelope) if _path_is_under(target_path, root)), None)
            wiki_artifacts: list[dict[str, Any]] = []
            if wiki_root is not None:
                log_path = _write_generic_wiki_log(
                    wiki_root,
                    "Approved Artifact Refine",
                    target_path,
                    evidence_ids,
                    "Applied approved after_artifact contents during refine.",
                )
                rebuilt = _rebuild_generic_wiki_views(
                    wiki_root,
                    str(envelope.get("sprint_id") or "sprint-autosci"),
                    target_path,
                    evidence_ids,
                )
                wiki_artifacts.extend(
                    [
                        {"type": "wiki_log", "path": _rel(log_path)},
                        *[{"type": "wiki_rebuild", "path": _rel(path)} for path in rebuilt],
                    ]
                )
            status = "completed"
            write.update(
                {
                    "applied": True,
                    "target_path": _rel(target_path),
                    "after_artifact": _rel(after_path),
                    "changed": changed,
                    "before_sha256": _hash_text(before),
                    "after_sha256": _hash_text(after),
                }
            )
            artifacts.extend(
                [
                    {"type": "refined_artifact", "path": _rel(target_path)},
                    *wiki_artifacts,
                ]
            )
            limitations.append("Approved refine apply replaced the target artifact with the supplied after_artifact contents.")

    write["status"] = status
    sidecar_path = _refine_apply_path(envelope)
    write["sidecar_path"] = _rel(sidecar_path)
    evidence = {
        "schema": "refine_apply_writeback.v1",
        "task_id": f"task-refine-artifact:{_slug(target or 'target')}",
        "sprint_id": str(envelope.get("sprint_id") or "sprint-autosci"),
        "node_id": f"node-refine-artifact:{_slug(target or 'target')}",
        "status": status,
        "inputs": inputs,
        "outputs": {"write": write},
        "artifacts": artifacts,
        "provenance": {
            "operator_id": "autosci-bridge",
            "implementation_package": "plugins/autosci",
            "timestamp": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        },
        "limitations": limitations,
    }
    artifact = {"type": "refine_apply_writeback_json", "path": _write_evidence_payload(sidecar_path, evidence)}
    return {"write": write, "artifact": artifact, "artifacts": artifacts, "limitations": limitations, "status": status}


def _control_workflow_raw(envelope: dict[str, Any], action: str, scope: str) -> dict[str, Any]:
    inputs = dict(envelope.get("inputs") or {})
    target = str(inputs.get("target") or inputs.get("topic") or scope)
    evidence_ids = [f"{action}:{_slug(target)}"]
    paths = _control_workflow_paths(envelope, action)
    paths["patch_candidates"].mkdir(parents=True, exist_ok=True)
    side_effects_by_action = {
        "setup_status": ["credential_probe", "persistent_config_write", "workspace_bootstrap"],
        "reset_plan": ["destructive_reset", "state_archive", "workspace_rebuild"],
        "refine_artifact": ["artifact_mutation", "source_rewrite", "quality_gate_rerun"],
        "run_research_lifecycle": ["multi_step_execution", "network_fetch", "workspace_mutation"],
    }
    contract = _approval_contract(
        envelope,
        action,
        side_effects_by_action.get(action, ["protected_runtime_change"]),
    )
    contract_artifact = _write_approval_contract_sidecar(envelope, action, contract)
    contract_missing = contract.get("missing") if isinstance(contract.get("missing"), list) else []
    refine_application = (
        _approved_refine_application(envelope, target=target, contract=contract, evidence_ids=evidence_ids)
        if action == "refine_artifact"
        else None
    )
    refine_applied = bool((refine_application or {}).get("write", {}).get("applied"))
    approval_state = "applied" if refine_applied else "proposed"
    application_state = "applied" if refine_applied else "proposed_only"
    collected = {
        "failed_nodes": []
        if refine_applied
        else [
            {
                "node_id": f"node-{action.replace('_', '-')}",
                "logical_operator": "ScientificWorkflowEvolver",
                "status": "blocked",
                "gate": "approval_gate",
            }
        ],
        "gate_rejection_reasons": [
            {
                "gate_id": "approval_gate",
                "status": "passed" if refine_applied else "blocked",
                "reasons": [
                    (
                        "Approved refine side effect was applied from verified after_artifact evidence."
                        if refine_applied
                        else "Approval-gated control side effects were not executed."
                    ),
                    f"Approval contract missing: {', '.join(str(item) for item in contract_missing) if contract_missing else 'N/A'}",
                ],
            }
        ],
        "ambiguous_manuals_or_prompts": [
            {
                "id": f"{action}.manual",
                "description": "Document the exact user-approved values and write scope before applying changes.",
            }
        ],
        "insufficient_schemas": [],
        "poor_operator_bindings": [],
        "human_intervention_points": []
        if refine_applied
        else [
            {
                "id": f"{action}.approval",
                "description": "Human approval is required before credentials, destructive reset, or persistent config changes.",
            }
        ],
        "runtime_errors": [],
    }
    proposed_changes = [
        {
            "change_id": f"change.manual.{action}",
            "category": "manual",
            "target": scope,
            "description": f"Record the approved {action.replace('_', ' ')} checklist, requested target, and rollback notes.",
            "evidence_ids": evidence_ids,
            "review_required": True,
            "application_state": application_state,
        },
        {
            "change_id": f"change.gate.{action}",
            "category": "gate",
            "target": "approval gate",
            "description": "Keep side-effect execution blocked until approval evidence and before/after artifact evidence are present.",
            "evidence_ids": evidence_ids,
            "review_required": True,
            "application_state": application_state,
        },
    ]
    markdown = "\n".join(
        [
            f"# {scope.title()} Proposal",
            "",
            f"Target: `{target}`",
            "",
            "## Proposed Changes",
            "",
            *[
                f"- `{item['change_id']}` [{item['category']}]: {item['description']}"
                for item in proposed_changes
            ],
            "",
            "## Controls",
            "",
            f"- Approval state: {approval_state}",
            f"- Protected runtime changed: {str(refine_applied).lower()}",
            f"- Side effects executed: {str(refine_applied).lower()}",
            f"- Approval contract state: {contract.get('approval_state')}",
            "",
        ]
    )
    _write_text_sidecar(paths["recommended_changes"], markdown)
    artifacts = [
        _artifact("recommended_changes_markdown", paths["recommended_changes"]),
        _artifact("patch_candidates_directory", paths["patch_candidates"]),
        contract_artifact,
    ]
    if refine_application:
        artifacts.append(refine_application["artifact"])
        artifacts.extend(refine_application.get("artifacts") or [])
    limitations = [
        (
            "Approved refine side effect was applied from verified before/runtime/after artifact evidence."
            if refine_applied
            else "This action produces proposal evidence only; no secrets, configuration, wiki files, or run artifacts were changed."
        ),
        "Approval and before/after evidence are required before applying setup or reset side effects.",
        *_approval_contract_limitations(contract),
    ]
    if refine_application:
        limitations.extend(str(item) for item in refine_application.get("limitations") or [])
    return {
        "proposal_id": f"{action}-{_slug(target)}",
        "scope": scope,
        "change_type": "workflow_template",
        "rationale": f"{scope} requires explicit approval and auditable before/after evidence.",
        "expected_effect": "Make the requested control action auditable without applying side effects.",
        "approval_state": approval_state,
        "evidence_ids": evidence_ids,
        "collected": collected,
        "proposed_changes": proposed_changes,
        "review": {
            "human_accept_reject_required": not refine_applied,
            "protected_core_edits_applied": refine_applied,
            "application_state": application_state,
            "approval_ref": str(contract.get("approval_ref") or "N/A"),
            "approval_contract_path": contract_artifact["path"],
            "approval_contract_verified": bool(contract.get("execution_verified")),
            "refine_apply": (refine_application or {}).get("write"),
        },
        "recommended_changes_path": _rel(paths["recommended_changes"]),
        "patch_candidates_path": _rel(paths["patch_candidates"]),
        "artifacts": artifacts,
        "limitations": limitations,
    }


RESEARCH_LIFECYCLE_STAGES = (
    ("setup", "Setup and topic initialization"),
    ("ingest", "Source ingest and wiki paper registration"),
    ("discover", "Landscape scan and source evidence fetch"),
    ("ideate", "Gap map and idea generation"),
    ("novelty-review", "Novelty and Review LLM gates"),
    ("experiment-design", "Experiment design"),
    ("experiment-run", "Experiment deployment"),
    ("collect", "Result collection"),
    ("review", "Result and artifact review"),
    ("paper-plan", "Publication plan"),
    ("paper-compile", "LaTeX/PDF compile and checklist"),
)


def _research_stage_from_token(raw_stage: str) -> str:
    token = _slug(raw_stage)
    stage_ids = [stage_id for stage_id, _ in RESEARCH_LIFECYCLE_STAGES]
    if token in stage_ids:
        return token
    aliases = {
        "stage0-setup": "setup",
        "stage1-ingest": "ingest",
        "stage2-discover": "discover",
        "stage2-ideate": "ideate",
        "stage3-collect": "collect",
        "stage3-experiment": "experiment-run",
        "stage4-review": "review",
        "stage5-paper": "paper-plan",
        "stage6-compile": "paper-compile",
    }
    if token in aliases:
        return aliases[token]
    for stage_id in stage_ids:
        if stage_id in token:
            return stage_id
    return "setup"


def _research_lifecycle_paths(envelope: dict[str, Any]) -> dict[str, Path]:
    output_dir = _output_dir(envelope, "run_research_lifecycle")
    wiki_outputs = _wiki_roots_for_write(envelope)[0] / "outputs"
    return {
        "recommended_changes": _configured_output_path(
            envelope,
            "recommended_changes_path",
            output_dir / "research_lifecycle_recommended_changes.md",
        ),
        "patch_candidates": _configured_output_path(
            envelope,
            "patch_candidates_path",
            output_dir / "patch_candidates",
        ),
        "pipeline_progress": _configured_output_path(
            envelope,
            "pipeline_progress_path",
            wiki_outputs / "pipeline-progress.md",
        ),
        "pipeline_report": _configured_output_path(
            envelope,
            "pipeline_report_path",
            wiki_outputs / "PIPELINE_REPORT.md",
        ),
        "pipeline_state": _configured_output_path(
            envelope,
            "pipeline_state_path",
            wiki_outputs / "pipeline-state.json",
        ),
    }


def _research_lifecycle_stage_plan(start_stage: str, skip_paper: bool) -> list[dict[str, Any]]:
    stage_ids = [stage_id for stage_id, _ in RESEARCH_LIFECYCLE_STAGES]
    start_index = stage_ids.index(start_stage) if start_stage in stage_ids else 0
    plan: list[dict[str, Any]] = []
    for index, (stage_id, title) in enumerate(RESEARCH_LIFECYCLE_STAGES):
        if skip_paper and stage_id in {"paper-plan", "paper-compile"}:
            state = "skipped_by_request"
        elif index < start_index:
            state = "skipped_resume_boundary"
        elif index == start_index:
            state = "blocked_approval"
        else:
            state = "pending"
        plan.append({
            "stage_id": stage_id,
            "title": title,
            "state": state,
            "order": index + 1,
        })
    return plan


def _input_path_values(inputs: dict[str, Any], *keys: str) -> list[str]:
    native = inputs.get("native_options") if isinstance(inputs.get("native_options"), dict) else {}
    values: list[str] = []
    for source in (inputs, native):
        for key in keys:
            raw = source.get(key)
            if isinstance(raw, list):
                values.extend(str(item) for item in raw if str(item).strip())
            elif raw:
                values.append(str(raw))
    return _unique_strings(values)


def _load_json_evidence_paths(raw_paths: list[str]) -> tuple[list[dict[str, Any]], list[str], list[dict[str, str]]]:
    payloads: list[dict[str, Any]] = []
    errors: list[str] = []
    artifacts: list[dict[str, str]] = []
    for raw in raw_paths:
        path = _resolve_harness_path(raw)
        if not path.exists() or not path.is_file():
            errors.append(f"missing evidence: {raw}")
            continue
        artifacts.append({"type": "research_lifecycle_stage_evidence_json", "path": _rel(path)})
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid evidence JSON: {_rel(path)}: {exc}")
            continue
        if isinstance(payload, dict):
            payload.setdefault("source_path", _rel(path))
            payloads.append(payload)
        else:
            errors.append(f"evidence JSON is not an object: {_rel(path)}")
    return payloads, errors, artifacts


def _evidence_status_completed(payload: dict[str, Any]) -> bool:
    return str(payload.get("status") or "").strip().lower() == "completed"


def _review_llm_evidence_completed(payloads: list[dict[str, Any]]) -> bool:
    for payload in payloads:
        if not _evidence_status_completed(payload):
            continue
        outputs = payload.get("outputs") if isinstance(payload.get("outputs"), dict) else {}
        review = outputs.get("review") if isinstance(outputs.get("review"), dict) else payload.get("review")
        if not isinstance(review, dict):
            continue
        review_llm = review.get("review_llm") if isinstance(review.get("review_llm"), dict) else {}
        if (
            str(review.get("review_mode") or "") == "review_llm"
            and review.get("review_available") is True
            and str(review_llm.get("status") or "completed") == "completed"
        ):
            return True
    return False


def _external_novelty_evidence_completed(payloads: list[dict[str, Any]]) -> bool:
    for payload in payloads:
        if not _evidence_status_completed(payload):
            continue
        if str(payload.get("schema") or "") in {"external_novelty.v1", "literature_discovery.v1"}:
            return True
        outputs = payload.get("outputs") if isinstance(payload.get("outputs"), dict) else {}
        evaluation = outputs.get("evaluation") if isinstance(outputs.get("evaluation"), dict) else {}
        external = evaluation.get("external_novelty") if isinstance(evaluation.get("external_novelty"), dict) else {}
        if str(external.get("status") or "") == "completed":
            return True
    return False


def _discovery_evidence_completed(payloads: list[dict[str, Any]]) -> bool:
    return any(
        _evidence_status_completed(payload)
        and str(payload.get("schema") or "") == "literature_discovery.v1"
        and bool((payload.get("outputs") if isinstance(payload.get("outputs"), dict) else {}).get("candidates"))
        for payload in payloads
    )


SCHEDULER_FULL_LIFECYCLE_NODE_IDS = {
    "literature_discover",
    "paper_ingest",
    "paper_analyze",
    "memory_update_initial",
    "graph_update",
    "claim_extract",
    "method_extract",
    "code_evidence_map",
    "idea_generate",
    "idea_evaluate",
    "experiment_design",
    "experiment_run",
    "experiment_monitor",
    "claim_verify",
    "report_draft",
    "artifact_review",
    "memory_update_final",
    "workflow_evolve",
    "report_plan",
    "publication_produce",
}


def _scheduler_lifecycle_summary(payloads: list[dict[str, Any]]) -> dict[str, Any]:
    for payload in payloads:
        if str(payload.get("schema") or "") != "scientific_lifecycle.v1":
            continue
        if str(payload.get("lifecycle_status") or "").lower() != "passed":
            continue
        gate = payload.get("lifecycle_gate_result") if isinstance(payload.get("lifecycle_gate_result"), dict) else {}
        if gate.get("ok") is not True:
            continue
        blocked = payload.get("blocked_nodes")
        if isinstance(blocked, dict) and blocked:
            continue
        node_results = payload.get("node_results") if isinstance(payload.get("node_results"), dict) else {}
        present_nodes = {str(node_id) for node_id in node_results}
        missing = sorted(SCHEDULER_FULL_LIFECYCLE_NODE_IDS - present_nodes)
        if missing:
            continue
        if any(
            str((node_results.get(node_id) or {}).get("status") or "").lower() != "passed"
            for node_id in SCHEDULER_FULL_LIFECYCLE_NODE_IDS
        ):
            continue
        return {
            "schema": "scientific_lifecycle.v1",
            "status": "completed",
            "job_id": str(payload.get("job_id") or payload.get("sprint_id") or ""),
            "workflow_id": str(payload.get("workflow_id") or ""),
            "source_path": str(payload.get("source_path") or ""),
            "node_count": len(node_results),
            "required_node_count": len(SCHEDULER_FULL_LIFECYCLE_NODE_IDS),
        }
    return {}


def _wiki_entity_counts(envelope: dict[str, Any]) -> dict[str, int]:
    counts = {"papers": 0, "ideas": 0, "experiments": 0, "outputs": 0, "compiled_pdfs": 0, "latex_sources": 0}
    for root in _wiki_roots_for_read(envelope):
        if not root.exists():
            continue
        for key in ("papers", "ideas", "experiments", "outputs"):
            folder = root / key
            if folder.exists():
                counts[key] += len([path for path in folder.glob("*.md") if path.is_file()])
        parent = root.parent
        paper_dir = parent / "paper"
        if paper_dir.exists():
            counts["compiled_pdfs"] += len([path for path in paper_dir.rglob("*.pdf") if path.is_file()])
            counts["latex_sources"] += len([path for path in paper_dir.rglob("*.tex") if path.is_file()])
    return counts


def _runtime_pdf_paths(contract: dict[str, Any]) -> list[Path]:
    records, _errors = _runtime_records(contract)
    paths: list[Path] = []
    for record in records:
        raw = _field(record, "pdf_path", "output_pdf", "compiled_pdf")
        values = raw if isinstance(raw, list) else ([raw] if raw else [])
        for value in values:
            if not isinstance(value, str) or not value.strip():
                continue
            path = _resolve_harness_path(value)
            if path.exists() and path.is_file():
                paths.append(path)
    return paths


def _runtime_pdf_artifacts(contract: dict[str, Any]) -> list[dict[str, str]]:
    return [{"type": "compiled_pdf", "path": _rel(path)} for path in _runtime_pdf_paths(contract)]


def _materialize_research_pipeline_pdf(
    envelope: dict[str, Any],
    contract: dict[str, Any],
    compile_semantic: dict[str, Any],
) -> dict[str, Any]:
    if not contract.get("execution_verified") or not compile_semantic.get("verified"):
        return {"status": "not_materialized", "reason": "compile runtime or approval contract is not verified"}
    sources = _runtime_pdf_paths(contract)
    if not sources:
        return {"status": "missing", "reason": "no verified runtime PDF path was available"}
    workspace_root = _wiki_roots_for_write(envelope)[0].parent
    target = workspace_root / "paper" / "main.pdf"
    target.parent.mkdir(parents=True, exist_ok=True)
    source = sources[0]
    try:
        if source.resolve() != target.resolve():
            shutil.copyfile(source, target)
    except OSError as exc:
        return {"status": "failed", "reason": str(exc), "source_path": _rel(source), "target_path": _rel(target)}
    return {
        "status": "completed",
        "source_path": _rel(source),
        "target_path": _rel(target),
        "artifact": {"type": "integrated_paper_pdf", "path": _rel(target)},
    }


def _research_lifecycle_evidence_report(envelope: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    inputs = dict(envelope.get("inputs") or {})
    paper_raw = str(inputs.get("paper_path") or "").strip()
    paper_path = _resolve_harness_path(paper_raw) if paper_raw else None
    discovery_payloads, discovery_errors, discovery_artifacts = _load_json_evidence_paths(
        _input_path_values(inputs, "discovery_evidence", "literature_evidence")
    )
    novelty_payloads, novelty_errors, novelty_artifacts = _load_json_evidence_paths(
        _input_path_values(inputs, "novelty_evidence", "external_novelty_evidence")
    )
    review_payloads, review_errors, review_artifacts = _load_json_evidence_paths(
        _input_path_values(inputs, "review_llm_evidence", "review_evidence")
    )
    lifecycle_payloads, lifecycle_errors, lifecycle_artifacts = _load_json_evidence_paths(
        _input_path_values(inputs, "lifecycle_summary", "lifecycle_summary_path", "scientific_lifecycle_evidence")
    )
    scheduler_lifecycle = _scheduler_lifecycle_summary(lifecycle_payloads)
    wiki_counts = _wiki_entity_counts(envelope)
    experiment_semantic = _approval_semantic_runtime(contract, "run_experiment")
    compile_semantic = _approval_semantic_runtime(contract, "compile_paper")
    integrated_pdf = _materialize_research_pipeline_pdf(envelope, contract, compile_semantic)
    paper_exists = bool(paper_path and paper_path.exists())
    report = {
        "paper_path": _rel(paper_path) if paper_path and paper_path.exists() else paper_raw,
        "paper_exists": paper_exists,
        "wiki_counts": wiki_counts,
        "discovery_completed": _discovery_evidence_completed(discovery_payloads),
        "external_novelty_completed": _external_novelty_evidence_completed(novelty_payloads),
        "review_llm_completed": _review_llm_evidence_completed(review_payloads),
        "scheduler_lifecycle_completed": bool(scheduler_lifecycle),
        "scheduler_lifecycle": scheduler_lifecycle,
        "experiment_runtime": experiment_semantic,
        "compile_runtime": compile_semantic,
        "integrated_pdf": integrated_pdf,
        "errors": [*discovery_errors, *novelty_errors, *review_errors, *lifecycle_errors],
        "artifacts": [
            *discovery_artifacts,
            *novelty_artifacts,
            *review_artifacts,
            *lifecycle_artifacts,
            *_contract_existing_artifacts(contract, "runtime_evidence", "research_lifecycle_runtime_evidence_json"),
            *_contract_existing_artifacts(contract, "before_artifacts", "research_lifecycle_before_artifact"),
            *_contract_existing_artifacts(contract, "after_artifacts", "research_lifecycle_after_artifact"),
            *_runtime_pdf_artifacts(contract),
            *([integrated_pdf["artifact"]] if isinstance(integrated_pdf.get("artifact"), dict) else []),
        ],
    }
    report["has_stage_evidence"] = any(
        [
            paper_exists,
            any(wiki_counts.values()),
            report["discovery_completed"],
            report["external_novelty_completed"],
            report["review_llm_completed"],
            report["scheduler_lifecycle_completed"],
            experiment_semantic.get("verified"),
            compile_semantic.get("verified"),
            integrated_pdf.get("status") == "completed",
        ]
    )
    return report


def _research_lifecycle_verified_stage_plan(
    start_stage: str,
    skip_paper: bool,
    evidence: dict[str, Any],
    contract: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    stage_ids = [stage_id for stage_id, _ in RESEARCH_LIFECYCLE_STAGES]
    start_index = stage_ids.index(start_stage) if start_stage in stage_ids else 0
    wiki_counts = evidence.get("wiki_counts") if isinstance(evidence.get("wiki_counts"), dict) else {}
    experiment_runtime = evidence.get("experiment_runtime") if isinstance(evidence.get("experiment_runtime"), dict) else {}
    compile_runtime = evidence.get("compile_runtime") if isinstance(evidence.get("compile_runtime"), dict) else {}
    scheduler_lifecycle_completed = bool(evidence.get("scheduler_lifecycle_completed"))
    checks = {
        "setup": scheduler_lifecycle_completed or bool(contract.get("approved")),
        "ingest": scheduler_lifecycle_completed or bool(evidence.get("paper_exists") or int(wiki_counts.get("papers") or 0) > 0),
        "discover": scheduler_lifecycle_completed or bool(evidence.get("discovery_completed")),
        "ideate": scheduler_lifecycle_completed or int(wiki_counts.get("ideas") or 0) > 0,
        "novelty-review": scheduler_lifecycle_completed
        or bool(evidence.get("external_novelty_completed") and evidence.get("review_llm_completed")),
        "experiment-design": scheduler_lifecycle_completed or int(wiki_counts.get("experiments") or 0) > 0,
        "experiment-run": scheduler_lifecycle_completed or bool(experiment_runtime.get("verified")),
        "collect": scheduler_lifecycle_completed or bool((experiment_runtime.get("detail") or {}).get("result_collected")),
        "review": scheduler_lifecycle_completed or bool(evidence.get("review_llm_completed")),
        "paper-plan": scheduler_lifecycle_completed
        or bool(int(wiki_counts.get("outputs") or 0) > 0 or int(wiki_counts.get("latex_sources") or 0) > 0),
        "paper-compile": scheduler_lifecycle_completed or bool(
            (isinstance(evidence.get("integrated_pdf"), dict) and evidence["integrated_pdf"].get("status") == "completed")
            or compile_runtime.get("verified")
            or int(wiki_counts.get("compiled_pdfs") or 0) > 0
        ),
    }
    missing: list[dict[str, str]] = []
    plan: list[dict[str, Any]] = []
    for index, (stage_id, title) in enumerate(RESEARCH_LIFECYCLE_STAGES):
        if skip_paper and stage_id in {"paper-plan", "paper-compile"}:
            state = "skipped_by_request"
        elif index < start_index:
            state = "skipped_resume_boundary"
        elif checks.get(stage_id):
            state = "completed"
        else:
            state = "pending_evidence"
            missing.append({"stage": stage_id, "reason": f"Required evidence for {stage_id} is missing or incomplete."})
        plan.append({"stage_id": stage_id, "title": title, "state": state, "order": index + 1})
    return plan, missing


def _research_lifecycle_markdown(raw: dict[str, Any], *, report: bool = False) -> str:
    pipeline = raw["pipeline"]
    stage_plan = raw["stage_plan"]
    lines = [
        "# AutoSci Research Pipeline Report" if report else "# AutoSci Research Pipeline Progress",
        "",
        f"Target: `{pipeline['target']}`",
        f"Pipeline: `{pipeline['pipeline_id']}`",
        f"Resume from: `{pipeline['resume_from']}`",
        f"Venue: `{pipeline['venue']}`",
        f"Skip paper: `{pipeline['skip_paper']}`",
        "",
        "## Stage State",
        "",
        "| Order | Stage | State |",
        "| ---: | --- | --- |",
    ]
    for stage in stage_plan:
        lines.append(f"| {stage['order']} | `{stage['stage_id']}` | `{stage['state']}` |")
    lines.extend([
        "",
        "## Gate State",
        "",
        "- Execution state: gated",
        "- Side effects executed: false",
        "- Workspace mutation outside generated pipeline artifacts: false",
        "- Required before full parity: Review LLM evidence, online discovery evidence, experiment runtime evidence, collection evidence, and LaTeX/PDF compile evidence.",
        "",
    ])
    evidence = raw.get("evidence_report") if isinstance(raw.get("evidence_report"), dict) else {}
    if evidence:
        lines.extend([
            "## Evidence Summary",
            "",
            f"- Paper exists: `{evidence.get('paper_exists', 'N/A')}`",
            f"- Discovery completed: `{evidence.get('discovery_completed', 'N/A')}`",
            f"- External novelty completed: `{evidence.get('external_novelty_completed', 'N/A')}`",
            f"- Review LLM completed: `{evidence.get('review_llm_completed', 'N/A')}`",
            f"- Scheduler lifecycle completed: `{evidence.get('scheduler_lifecycle_completed', 'N/A')}`",
            f"- Experiment runtime verified: `{(evidence.get('experiment_runtime') or {}).get('verified', 'N/A')}`",
            f"- Compile runtime verified: `{(evidence.get('compile_runtime') or {}).get('verified', 'N/A')}`",
            f"- Integrated PDF: `{(evidence.get('integrated_pdf') or {}).get('target_path', (evidence.get('integrated_pdf') or {}).get('status', 'N/A'))}`",
            "",
        ])
    if report:
        lines.extend([
            "## Resume Notes",
            "",
            "- The next executable stage is recorded, but no native stage runner was launched.",
            "- This report is intended for parity auditing and resume planning, not as research outcome evidence.",
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def _research_lifecycle_raw(envelope: dict[str, Any]) -> dict[str, Any]:
    inputs = dict(envelope.get("inputs") or {})
    target = str(inputs.get("target") or inputs.get("topic") or "autosci research lifecycle")
    pipeline_id = str(inputs.get("pipeline") or _slug(target))
    start_raw = str(inputs.get("start_from") or "setup")
    start_stage = _research_stage_from_token(start_raw)
    skip_paper = bool(inputs.get("skip_paper"))
    venue = str(inputs.get("venue") or "N/A")
    paths = _research_lifecycle_paths(envelope)
    paths["patch_candidates"].mkdir(parents=True, exist_ok=True)
    contract = _approval_contract(
        envelope,
        "run_research_lifecycle",
        [
            "multi_step_execution",
            "network_fetch",
            "workspace_mutation",
            "experiment_deploy",
            "paper_compile",
        ],
    )
    contract_artifact = _write_approval_contract_sidecar(envelope, "run_research_lifecycle", contract)
    contract_missing = contract.get("missing") if isinstance(contract.get("missing"), list) else []
    evidence_report = _research_lifecycle_evidence_report(envelope, contract)
    evidence_mode = bool(evidence_report.get("has_stage_evidence") or contract.get("approved"))
    if evidence_mode:
        stage_plan, missing_stages = _research_lifecycle_verified_stage_plan(start_stage, skip_paper, evidence_report, contract)
        current = next((stage for stage in stage_plan if stage["state"] == "pending_evidence"), {"stage_id": "completed"})
        if current["stage_id"] == "completed" and evidence_report.get("errors"):
            current = {"stage_id": "evidence-verification"}
    else:
        stage_plan = _research_lifecycle_stage_plan(start_stage, skip_paper)
        missing_stages = [
            {
                "stage": str(next((stage for stage in stage_plan if stage["state"] == "blocked_approval"), stage_plan[0])["stage_id"]),
                "reason": "Native research lifecycle execution was not launched without approval/runtime evidence.",
            }
        ]
        current = next((stage for stage in stage_plan if stage["state"] == "blocked_approval"), stage_plan[0])
    pipeline_completed = evidence_mode and not missing_stages and not evidence_report.get("errors")
    experiment_runtime = evidence_report.get("experiment_runtime") if isinstance(evidence_report.get("experiment_runtime"), dict) else {}
    compile_runtime = evidence_report.get("compile_runtime") if isinstance(evidence_report.get("compile_runtime"), dict) else {}
    runtime_evidence_ids = _unique_strings(
        [
            *[str(item) for item in (experiment_runtime.get("detail") or {}).get("evidence_ids", [])],
            *[str(item) for item in (compile_runtime.get("detail") or {}).get("evidence_ids", [])],
        ]
    )
    pipeline = {
        "pipeline_id": pipeline_id,
        "target": target,
        "resume_from": start_stage,
        "requested_start_from": start_raw,
        "venue": venue,
        "skip_paper": skip_paper,
        "auto": bool(inputs.get("auto")),
        "status": "completed" if pipeline_completed else ("pending_evidence" if evidence_mode else "gated"),
    }
    evidence_ids = [
        f"research-lifecycle:{_slug(pipeline_id)}",
        f"pipeline-progress:{_slug(target)}",
        f"pipeline-report:{_slug(target)}",
        *runtime_evidence_ids,
    ]
    gate_reasons = [
        {
            "gate_id": "research_lifecycle_evidence_gate",
            "status": "passed" if pipeline_completed else "blocked",
            "reasons": ["All required research lifecycle stage evidence was verified."]
            if pipeline_completed
            else [
                "Native research lifecycle execution is incomplete until every required stage has verified evidence.",
                *[f"{item['stage']}: {item['reason']}" for item in missing_stages],
                *[f"evidence_error: {item}" for item in evidence_report.get("errors", [])],
                f"Approval contract missing: {', '.join(str(item) for item in contract_missing) if contract_missing else 'N/A'}",
            ],
        }
    ]
    blocked_nodes = [
        {
            "node_id": f"stage-{item['stage']}",
            "logical_operator": "ScientificWorkflowEvolver",
            "status": "blocked",
            "gate": "research_lifecycle_evidence_gate",
            "stage": item["stage"],
        }
        for item in missing_stages
    ] or [
        {
            "node_id": "research-lifecycle-evidence-errors",
            "logical_operator": "ScientificWorkflowEvolver",
            "status": "blocked",
            "gate": "research_lifecycle_evidence_gate",
            "stage": "evidence-verification",
        }
    ]
    failed_nodes = [
        {
            "node_id": "research-lifecycle-completed",
            "logical_operator": "ScientificWorkflowEvolver",
            "status": "completed",
            "gate": "research_lifecycle_evidence_gate",
            "stage": "completed",
        }
    ] if pipeline_completed else blocked_nodes
    collected = {
        "failed_nodes": failed_nodes,
        "gate_rejection_reasons": gate_reasons,
        "ambiguous_manuals_or_prompts": [
            {
                "id": "research.lifecycle.resume",
                "description": "Record the user-approved resume stage and exact stage runner before executing a native pipeline.",
            }
        ],
        "insufficient_schemas": [],
        "poor_operator_bindings": [],
        "human_intervention_points": [
            {
                "id": "research.lifecycle.approval",
                "description": "Human approval is required before network fetch, experiment deployment, workspace mutation, or paper compilation.",
            }
        ],
        "runtime_errors": [
            *[
                {"id": f"research.lifecycle.evidence-error-{index + 1}", "description": str(error)}
                for index, error in enumerate(evidence_report.get("errors", []))
            ],
            *(
                []
                if evidence_mode
                else [
                    {
                        "id": "native-stage-runner-not-executed",
                        "description": "No native AutoSci stage runner evidence was supplied for this gated lifecycle request.",
                    }
                ]
            ),
        ],
    }
    proposed_changes = [
        {
            "change_id": "change.manual.research-lifecycle-resume",
            "category": "manual",
            "target": "research lifecycle resume protocol",
            "description": "Persist target, resume stage, venue, and skip-paper intent before executing native lifecycle stages.",
            "evidence_ids": evidence_ids,
            "review_required": True,
            "application_state": "proposed_only",
        },
        {
            "change_id": "change.gate.research-lifecycle-required-evidence",
            "category": "gate",
            "target": "research lifecycle gate",
            "description": "Require online evidence, Review LLM, experiment runtime, collection, and compile artifacts before marking the lifecycle complete.",
            "evidence_ids": evidence_ids,
            "review_required": True,
            "application_state": "proposed_only",
        },
        {
            "change_id": "change.workflow.research-lifecycle-stage-artifacts",
            "category": "workflow_template",
            "target": "wiki/outputs pipeline artifacts",
            "description": "Write pipeline progress, state, and report artifacts so resume and audit checks no longer depend on route-only evidence.",
            "evidence_ids": evidence_ids,
            "review_required": True,
            "application_state": "proposed_only",
        },
    ]
    raw = {
        "proposal_id": f"run-research-lifecycle-{_slug(pipeline_id)}",
        "scope": "scientific research lifecycle",
        "change_type": "workflow_template",
        "rationale": "A native research lifecycle request needs stage-resumable wiki-first state before protected side effects can run.",
        "expected_effect": "Expose auditable pipeline progress and required full-parity evidence without pretending the lifecycle executed.",
        "approval_state": "approved" if pipeline_completed else "proposed",
        "approval_ref": str(contract.get("approval_ref") or ""),
        "evidence_ids": evidence_ids,
        "pipeline": pipeline,
        "stage_plan": stage_plan,
        "current_stage": current["stage_id"],
        "resume_from": start_stage,
        "evidence_report": evidence_report,
        "collected": collected,
        "proposed_changes": proposed_changes,
        "review": {
            "human_accept_reject_required": True,
            "protected_core_edits_applied": False,
            "application_state": "not_applied" if pipeline_completed else "proposed_only",
            "approval_ref": str(contract.get("approval_ref") or "N/A"),
            "approval_contract_path": contract_artifact["path"],
            "approval_contract_verified": bool(contract.get("execution_verified")),
        },
        "recommended_changes_path": _rel(paths["recommended_changes"]),
        "patch_candidates_path": _rel(paths["patch_candidates"]),
        "artifacts": [
            _artifact("recommended_changes_markdown", paths["recommended_changes"]),
            _artifact("patch_candidates_directory", paths["patch_candidates"]),
            contract_artifact,
            _artifact("pipeline_progress_markdown", paths["pipeline_progress"]),
            _artifact("pipeline_report_markdown", paths["pipeline_report"]),
            _artifact("pipeline_state_json", paths["pipeline_state"]),
            *list(evidence_report.get("artifacts") or []),
        ],
        "status": "completed" if pipeline_completed else "inconclusive",
        "limitations": (
            [
                "Research lifecycle completion was verified from supplied wiki/source, Review LLM, runtime, and compile evidence.",
                "This action records integrated lifecycle state; protected side effects must still be executed only through approved stage runners.",
            ]
            if pipeline_completed
            else [
                "Pipeline progress/report artifacts were generated, but one or more native research lifecycle stages still lack verified evidence.",
                "Full parity remains blocked until real online evidence, Review LLM evidence, experiment runtime, collection, and paper compile artifacts are attached.",
                *_approval_contract_limitations(contract),
            ]
        ),
    }
    state = {
        "schema": "autosci_research_pipeline_state.v1",
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "pipeline": pipeline,
        "stage_plan": stage_plan,
        "current_stage": current["stage_id"],
        "approval_contract": contract,
        "evidence_report": evidence_report,
    }
    _write_text_sidecar(paths["recommended_changes"], _research_lifecycle_markdown(raw, report=True))
    _write_text_sidecar(paths["pipeline_progress"], _research_lifecycle_markdown(raw))
    _write_text_sidecar(paths["pipeline_report"], _research_lifecycle_markdown(raw, report=True))
    _write_json_sidecar(paths["pipeline_state"], state)
    return raw


def _action_setup_status(envelope: dict[str, Any]) -> dict[str, Any]:
    return convert_workflow_evolution(_control_workflow_raw(envelope, "setup_status", "setup status"), envelope)


def _action_reset_plan(envelope: dict[str, Any]) -> dict[str, Any]:
    return convert_workflow_evolution(_control_workflow_raw(envelope, "reset_plan", "reset plan"), envelope)


def _wiki_health_raw(envelope: dict[str, Any]) -> dict[str, Any]:
    inputs = dict(envelope.get("inputs") or {})
    target = str(inputs.get("target") or inputs.get("wiki_root") or "autosci wiki")
    paths = _control_workflow_paths(envelope, "check_wiki_health")
    paths["patch_candidates"].mkdir(parents=True, exist_ok=True)
    roots = _wiki_roots_for_read(envelope)
    existing_roots = [root for root in roots if root.exists()]
    primary = existing_roots[0] if existing_roots else roots[0]
    expected_dirs = ["papers", "methods", "ideas", "experiments", "outputs", "graph"]
    missing_dirs = [name for name in expected_dirs if not (primary / name).is_dir()]
    markdown_pages = sorted(primary.rglob("*.md")) if primary.exists() else []
    edge_errors: list[dict[str, Any]] = []
    edges_path = primary / "graph" / "edges.jsonl"
    if edges_path.exists():
        for index, line in enumerate(edges_path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                edge_errors.append({"line": index, "error": str(exc)})
                continue
            for field in ("source", "target", "relation"):
                if not str(payload.get(field) or "").strip():
                    edge_errors.append({"line": index, "error": f"missing {field}"})
    elif primary.exists():
        edge_errors.append({"line": 0, "error": "graph/edges.jsonl is missing"})
    evidence_ids = [f"check-wiki:{_slug(target)}", _rel(primary)]
    findings = {
        "target": target,
        "wiki_root": _rel(primary),
        "root_exists": primary.exists(),
        "checked_roots": [_rel(root) for root in roots],
        "markdown_page_count": len(markdown_pages),
        "missing_dirs": missing_dirs,
        "edge_errors": edge_errors,
    }
    model_output, model_artifacts = _model_output(
        envelope,
        action="check_wiki_health",
        prompt=target,
        context={"target": target, "findings": findings},
    )
    model_completed = model_output.get("status") == "completed"
    findings["model_output"] = model_output
    evidence_ids = _unique_strings([
        *evidence_ids,
        *[str(item) for item in model_output.get("evidence_ids") or []],
    ])
    runtime_errors: list[dict[str, Any]] = []
    if not primary.exists():
        runtime_errors.append({"id": "wiki-root-missing", "description": f"Wiki root does not exist: {_rel(primary)}"})
    if not markdown_pages:
        runtime_errors.append({"id": "wiki-pages-missing", "description": "No Markdown wiki pages were found."})
    if missing_dirs:
        runtime_errors.append({"id": "wiki-dirs-missing", "description": f"Missing wiki directories: {', '.join(missing_dirs)}"})
    if edge_errors:
        runtime_errors.append({"id": "wiki-edges-invalid", "description": "Graph edge file is missing or contains invalid rows."})
    if not runtime_errors and not model_completed:
        runtime_errors.append({"id": "wiki-health-review", "description": "Structural checks passed; content quality still requires model/reviewer evidence."})
    quality_reasons = [item["description"] for item in runtime_errors]
    if not quality_reasons:
        quality_reasons = [f"Model/reviewer evidence completed via `{model_output.get('source') or model_output.get('provider') or 'explicit evidence'}`."]
    collected = {
        "failed_nodes": [
            {
                "node_id": "node-check-wiki-health",
                "logical_operator": "ScientificWorkflowEvolver",
                "status": "inconclusive" if runtime_errors else "completed",
                "gate": "wiki_health_check",
            }
        ],
        "gate_rejection_reasons": [
            {
                "gate_id": "wiki_health_check",
                "status": "passed" if not runtime_errors else "inconclusive",
                "reasons": quality_reasons,
            }
        ],
        "ambiguous_manuals_or_prompts": []
        if model_completed
        else [
            {
                "id": "check.content-quality",
                "description": "LLM-assisted content quality checks are not deterministic without model output evidence.",
            }
        ],
        "insufficient_schemas": [],
        "poor_operator_bindings": [],
        "human_intervention_points": [],
        "runtime_errors": runtime_errors,
    }
    proposed_changes = [
        {
            "change_id": "change.manual.wiki-health-evidence",
            "category": "manual",
            "target": "wiki health check",
            "description": "Require source-attributed model/reviewer evidence before marking content quality checks complete.",
            "evidence_ids": evidence_ids,
            "review_required": True,
            "application_state": "proposed_only",
        },
        {
            "change_id": "change.gate.wiki-structure-diagnostics",
            "category": "gate",
            "target": "wiki structural gate",
            "description": "Keep missing wiki directories, missing pages, or invalid graph edges visible as explicit diagnostics.",
            "evidence_ids": evidence_ids,
            "review_required": True,
            "application_state": "proposed_only",
        },
    ]
    markdown = "\n".join(
        [
            "# Wiki Health Check",
            "",
            f"Wiki root: `{_rel(primary)}`",
            f"Markdown pages: `{len(markdown_pages)}`",
            f"Missing dirs: `{', '.join(missing_dirs) if missing_dirs else 'N/A'}`",
            f"Edge errors: `{len(edge_errors)}`",
            "",
            "## Model Evidence",
            "",
            f"Status: `{model_output.get('status')}`",
            f"Source: `{model_output.get('source', 'N/A')}`",
            f"Answer: {model_output.get('answer', 'N/A') if model_completed else 'N/A'}",
            "",
            "## Findings JSON",
            "",
            "```json",
            json.dumps(findings, indent=2, sort_keys=True),
            "```",
            "",
        ]
    )
    _write_text_sidecar(paths["recommended_changes"], markdown)
    return {
        "proposal_id": f"check-wiki-health-{_slug(target)}",
        "scope": "wiki health check",
        "change_type": "gate",
        "rationale": "Local wiki structure and graph diagnostics were checked without mutating wiki state.",
        "expected_effect": "Keep wiki health gaps visible while requiring model evidence for content quality conclusions.",
        "approval_state": "proposed",
        "evidence_ids": evidence_ids,
        "collected": collected,
        "proposed_changes": proposed_changes,
        "review": {
            "human_accept_reject_required": True,
            "protected_core_edits_applied": False,
            "application_state": "proposed_only",
            "approval_ref": "N/A",
        },
        "recommended_changes_path": _rel(paths["recommended_changes"]),
        "patch_candidates_path": _rel(paths["patch_candidates"]),
        "artifacts": [
            _artifact("recommended_changes_markdown", paths["recommended_changes"]),
            _artifact("patch_candidates_directory", paths["patch_candidates"]),
            *model_artifacts,
        ],
        "limitations": [
            "Wiki health check is structural and local only.",
            (
                "LLM-assisted content quality evidence was supplied and archived."
                if model_completed
                else "LLM-assisted content quality checks require supplied model output evidence."
            ),
        ],
    }


def _action_check_wiki_health(envelope: dict[str, Any]) -> dict[str, Any]:
    return convert_workflow_evolution(_wiki_health_raw(envelope), envelope)


def _action_refine_artifact(envelope: dict[str, Any]) -> dict[str, Any]:
    return convert_workflow_evolution(_control_workflow_raw(envelope, "refine_artifact", "artifact refinement"), envelope)


def _action_run_research_lifecycle(envelope: dict[str, Any]) -> dict[str, Any]:
    return convert_workflow_evolution(_research_lifecycle_raw(envelope), envelope)



def _run_visualize_tool(
    tool_path: Path,
    args: list[str],
    *,
    output_dir: Path,
    artifact_prefix: str,
) -> tuple[int, dict[str, Any], list[dict[str, str]]]:
    command = [sys.executable, str(tool_path), *args]
    timeout = int(os.environ.get("AUTOSCI_VISUALIZE_TIMEOUT_SECONDS", "20"))
    try:
        proc = subprocess.run(
            command,
            cwd=REPO_HARNESS_DIR.parent,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        proc_stdout = json.dumps({"status": "error", "detail": str(exc)}, sort_keys=True)
        stdout_path = _write_text_sidecar(output_dir / f"{artifact_prefix}_stdout.json", proc_stdout)
        stderr_path = _write_text_sidecar(output_dir / f"{artifact_prefix}_stderr.txt", str(exc))
        return 1, {"status": "failed"}, [
            {"type": f"{artifact_prefix}_stdout_json", "path": stdout_path},
            {"type": f"{artifact_prefix}_stderr", "path": stderr_path},
        ]

    stdout_path = _write_text_sidecar(
        output_dir / f"{artifact_prefix}_stdout.json",
        proc.stdout,
    )
    stderr_path = _write_text_sidecar(
        output_dir / f"{artifact_prefix}_stderr.txt",
        proc.stderr,
    )
    payload: dict[str, Any] = {}
    if proc.stdout:
        try:
            payload = json.loads(proc.stdout)
        except json.JSONDecodeError:
            payload = {"status": "non_json_stdout", "raw": proc.stdout[:512]}
    if not isinstance(payload, dict):
        payload = {}
    artifacts = [
        {"type": f"{artifact_prefix}_stdout_json", "path": stdout_path},
        {"type": f"{artifact_prefix}_stderr", "path": stderr_path},
    ]
    return proc.returncode, payload, artifacts


def _normalize_visualization_edges(raw_edges: list[dict[str, Any]], fallback: list[str]) -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    for item in raw_edges:
        source = str(item.get("source") or "").strip()
        target = str(item.get("target") or "").strip()
        relation = str(item.get("relation") or "visualizes").strip() or "visualizes"
        if not source or not target:
            continue
        operation = str(item.get("operation") or "confirm").strip() or "confirm"
        if operation not in {"add", "remove", "confirm", "propose", "no_op"}:
            operation = "confirm"
        edge = {
            "source": source,
            "target": target,
            "relation": relation,
            "operation": operation,
            "evidence_ids": list(dict.fromkeys([
                *([str(itemv) for itemv in item.get("evidence_ids") if str(itemv).strip()] if isinstance(item.get("evidence_ids"), list) else []),
                *fallback,
            ])),
            "rendered": bool(item.get("rendered") or "rendered" in item) if isinstance(item.get("rendered"), bool) else False,
        }
        edges.append(edge)
    if not edges:
        edges.append({
            "source": fallback[0] if fallback else "visualize:autosci-graph",
            "target": str(raw_edges[0].get("target") if raw_edges else "autosci-graph"),
            "relation": "proposes_visualization_for",
            "operation": "propose",
            "evidence_ids": fallback,
            "rendered": False,
        })
    return edges


def _visualize_graph_artifacts(envelope: dict[str, Any], target: str, slug: str) -> tuple[dict[str, Any], list[dict[str, str]], list[str], str]:
    inputs = dict(envelope.get("inputs") or {})
    wiki_root = _resolve_harness_path(inputs.get("wiki_root") or "artifacts/autosci/workspace/wiki")
    output_dir = _output_dir(envelope, "visualize_graph")
    output_dir.mkdir(parents=True, exist_ok=True)
    slug_tag = f"visualize-{slug}"
    obsidian_out = wiki_root / ".obsidian" / "graph.json"
    canvas_out = wiki_root / "graph" / "autosci.canvas"
    graph_out = output_dir / "autosci_web_graph.json"
    status_reasons: list[str] = []

    return_code, payload, artifacts = _run_visualize_tool(
        REPO_HARNESS_DIR.parent / "tools" / "visualize.py",
        ["generate-obsidian-config", "--wiki-root", str(wiki_root), "--out", str(obsidian_out)],
        output_dir=output_dir,
        artifact_prefix="visualize_obsidian_config",
    )
    if return_code != 0:
        status_reasons.append("Obsidian graph config generation failed.")

    canvas_payload: dict[str, Any] = {}
    _, canvas_payload, canvas_artifacts = _run_visualize_tool(
        REPO_HARNESS_DIR.parent / "tools" / "visualize.py",
        [
            "generate-canvas",
            "--wiki-root",
            str(wiki_root),
            "--graph-out",
            str(graph_out),
            "--out",
            str(canvas_out),
        ],
        output_dir=output_dir,
        artifact_prefix="visualize_canvas",
    )
    artifacts.extend(canvas_artifacts)
    if not canvas_payload:
        status_reasons.append("AutoSci canvas generation produced no structured output.")

    graph_payload: dict[str, Any] = {}
    code, graph_payload, graph_artifacts = _run_visualize_tool(
        REPO_HARNESS_DIR.parent / "tools" / "visualize.py",
        ["graph-data", "--wiki-root", str(wiki_root), "--out", str(graph_out)],
        output_dir=output_dir,
        artifact_prefix="visualize_graph_data",
    )
    artifacts.extend(graph_artifacts)
    if code != 0:
        status_reasons.append("Graph data extraction failed.")

    graph_edges = graph_payload.get("edges") if isinstance(graph_payload.get("edges"), list) else []
    edges = _normalize_visualization_edges(
        [edge for edge in graph_edges if isinstance(edge, dict)],
        [f"visualize:{slug}", slug_tag, target],
    )

    if not obsidian_out.exists():
        status_reasons.append("Obsidian config artifact was not created.")
    if not canvas_out.exists():
        status_reasons.append("Canvas artifact was not created.")
    if not graph_out.exists():
        status_reasons.append("Graph data artifact was not created.")

    serve_payload: dict[str, Any] = {}
    contract = _approval_contract(envelope, "visualize_graph", ["obsidian_canvas_write", "local_web_server", "graph_read" ])
    if bool(inputs.get("execute_approved_side_effect")) and contract.get("ready_for_execution"):
        code, serve_payload, serve_artifacts = _run_visualize_tool(
            REPO_HARNESS_DIR.parent / "tools" / "serve.py",
            ["--wiki-root", str(wiki_root), "--health-check"],
            output_dir=output_dir,
            artifact_prefix="visualize_web_health",
        )
        artifacts.extend(serve_artifacts)
        if code != 0:
            status_reasons.append("Local web health check execution failed.")
        else:
            status_reasons.append("Local web graph health artifact generated from serve health-check.")
    contract_artifact = _write_approval_contract_sidecar(envelope, "visualize_graph", contract)
    artifacts.append(contract_artifact)
    if graph_out.exists():
        artifacts.append(_artifact("autosci_web_graph_json", graph_out))
    if obsidian_out.exists():
        artifacts.append(_artifact("obsidian_graph_config_json", obsidian_out))
    if canvas_out.exists():
        artifacts.append(_artifact("autosci_canvas_json", canvas_out))
    if serve_payload:
        artifacts.append(_artifact("visualize_web_health_json", _write_json_sidecar(output_dir / "visualize_web_health.json", serve_payload)))

    status = "completed" if not status_reasons else "inconclusive"
    output = {
        "edges": edges,
        "evidence_ids": [f"visualize:{slug}", slug_tag, target],
        "artifacts": artifacts,
        "status": status,
        "reason_count": len(status_reasons),
        "status_reasons": status_reasons,
        "obsidian_config": _rel(obsidian_out),
        "canvas": _rel(canvas_out),
        "graph_data": _rel(graph_out),
    }
    return output, artifacts, status_reasons, contract


def _action_visualize_graph(envelope: dict[str, Any]) -> dict[str, Any]:
    inputs = dict(envelope.get("inputs") or {})
    target = str(inputs.get("target") or inputs.get("topic") or "autosci-graph")
    slug = _slug(target)
    raw_output, artifacts, status_reasons, contract = _visualize_graph_artifacts(
        envelope,
        target,
        slug,
    )
    limitations = [
        "Visualization artifacts are generated from local wiki graph state.",
        "Local web serving, browser opening, and screenshot capture remain approval-gated side effects.",
    ]
    if not status_reasons:
        limitations.append("All requested visualization artifacts were generated from local wiki data.")
    else:
        limitations.extend(status_reasons)
    limitations.extend(_approval_contract_limitations(contract))
    contract_artifact = _write_approval_contract_sidecar(envelope, "visualize_graph", contract)
    if contract_artifact not in artifacts:
        artifacts.append(contract_artifact)
    output = {
        "paper_id": f"visualize-{slug}",
        "source_ref": target,
        "evidence_ids": [f"visualize:{slug}"],
        "edges": raw_output["edges"],
        "artifacts": artifacts,
        "limits": status_reasons,
        "status_reasons": status_reasons,
    }
    return convert_research_graph_update({
        "paper_id": f"visualize-{slug}",
        "source_ref": target,
        "evidence_ids": [f"visualize:{slug}", slug],
        "status": "completed" if not status_reasons else "inconclusive",
        "edges": raw_output["edges"],
        "artifacts": artifacts,
        "limitations": limitations,
    }, envelope)


ACTIONS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "analyze_paper": _action_analyze_paper,
    "ask_wiki": _action_ask_wiki,
    "build_poster": _action_build_poster,
    "check_wiki_health": _action_check_wiki_health,
    "compile_paper": _action_compile_paper,
    "daily_arxiv_prepare_finalize": _action_daily_arxiv_prepare_finalize,
    "discover_literature": _action_discover_literature,
    "draft_rebuttal": _action_draft_rebuttal,
    "edit_wiki_plan": _action_edit_wiki_plan,
    "evaluate_pilot_result": _action_evaluate_pilot_result,
    "evolve_workflow": _action_evolve_workflow,
    "ingest_paper": _action_ingest_paper,
    "init_sources": _action_init_sources,
    "prepare_paper_source": _action_ingest_paper,
    "extract_claims": _action_extract_claims,
    "extract_methods": _action_extract_methods,
    "evaluate_ideas": _action_evaluate_ideas,
    "generate_ideas": _action_generate_ideas,
    "map_code_evidence": _action_map_code_evidence,
    "design_experiment": _action_design_experiment,
    "monitor_experiment": _action_monitor_experiment,
    "plan_report": _action_plan_report,
    "prefill_foundations": _action_prefill_foundations,
    "review_artifact": _action_review_artifact,
    "refine_artifact": _action_refine_artifact,
    "reset_plan": _action_reset_plan,
    "run_pilot_experiment": _action_run_pilot_experiment,
    "run_research_lifecycle": _action_run_research_lifecycle,
    "run_experiment": _action_run_experiment,
    "setup_status": _action_setup_status,
    "update_graph": _action_update_graph,
    "update_memory": _action_update_memory,
    "verify_claim": _action_verify_claim,
    "visualize_graph": _action_visualize_graph,
    "write_report": _action_write_report,
    "write_survey": _action_write_survey,
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
    extra: dict[str, Any] = {}
    if args.action == "ingest_paper":
        extra["sidecar_evidence_paths"] = _write_phase9_foundation_sidecars(envelope, evidence)
    if args.action == "evaluate_ideas":
        sidecar_paths = [_write_phase11_idea_memory_sidecar(envelope, evidence)]
        novelty_writeback_path = _write_novelty_writeback_sidecar(envelope, evidence)
        if novelty_writeback_path:
            sidecar_paths.append(novelty_writeback_path)
            extra["novelty_writeback_path"] = novelty_writeback_path
        extra["sidecar_evidence_paths"] = sidecar_paths
    if args.action == "write_report":
        extra.update(_write_phase14_publication_sidecars(envelope, evidence))
    if args.action == "evolve_workflow":
        artifacts = evidence.get("artifacts") if isinstance(evidence.get("artifacts"), list) else []
        for artifact in artifacts:
            if isinstance(artifact, dict) and artifact.get("type") == "recommended_changes_markdown":
                extra["recommended_changes_path"] = artifact.get("path")
            if isinstance(artifact, dict) and artifact.get("type") == "patch_candidates_directory":
                extra["patch_candidates_path"] = artifact.get("path")
    result = _write_result(args.action, envelope, evidence, extra_result_fields=extra)
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
