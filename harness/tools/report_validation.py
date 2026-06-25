"""Deterministic verifier and quality scoring helpers for chapterized reports."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


FORBIDDEN_PUBLIC_FIELD_RE = re.compile(
    r"\b(video_id|chapter_id|evidence_pack_id|transcript_status|backend|token_count)\b",
    re.I,
)
CLAIM_SPLIT_RE = re.compile(r"[。！？!?]\s*|\n+-\s+")
VIDEO_REF_RE = re.compile(r"\bV\d{3}\b")
ACTION_INSIGHT_RE = re.compile(r"(建议|应当|可以|下一步|观察|优先|风险)")
SAFETY_DOWNGRADE_RE = re.compile(r"(证据不足|待验证|暂不作为结论|不确定)")
DEEP_PROOF_FILENAMES = ("deep-research-state.json",)
DEEP_REQUEST_FILENAMES = ("report-operator-request.json", "request.json")


def _text(value: Any) -> str:
    return str(value or "").strip()


def _evidence_refs(evidence_pack: dict[str, Any]) -> list[str]:
    refs: list[str] = []
    for key in ("must_use_evidence_ids", "optional_evidence_ids"):
        refs.extend(_text(item) for item in evidence_pack.get(key) or [] if _text(item))
    for key in ("core_evidence", "support_evidence", "selected_videos"):
        for item in evidence_pack.get(key) or []:
            if not isinstance(item, dict):
                continue
            refs.extend(
                _text(item.get(ref_key))
                for ref_key in ("evidence_id", "video_ref", "ref")
                if _text(item.get(ref_key))
            )
    seen: set[str] = set()
    return [ref for ref in refs if not (ref in seen or seen.add(ref))]


def _claim_sentences(markdown: str) -> list[str]:
    claims: list[str] = []
    for part in CLAIM_SPLIT_RE.split(markdown):
        sentence = part.strip()
        if len(sentence) < 18:
            continue
        if sentence.startswith("#"):
            continue
        if SAFETY_DOWNGRADE_RE.search(sentence):
            continue
        claims.append(sentence)
    return claims


def _read_json_path(path: str | Path) -> dict[str, Any] | None:
    try:
        candidate = Path(path).expanduser()
    except TypeError:
        return None
    if not candidate.exists() or not candidate.is_file():
        return None
    try:
        data = json.loads(candidate.read_text(encoding="utf-8"))
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def _path_text(value: Any) -> str:
    return str(value or "").strip()


def _deep_request_sidecar_for(proof_path: Path, proof_bundle: dict[str, Any]) -> dict[str, Any] | None:
    explicit = _path_text(
        proof_bundle.get("deep_request_path")
        or proof_bundle.get("deep_research_request_path")
        or proof_bundle.get("report_operator_request_path")
    )
    if explicit:
        loaded = _read_json_path(explicit)
        if loaded is not None:
            return loaded
    for name in DEEP_REQUEST_FILENAMES:
        loaded = _read_json_path(proof_path.parent / name)
        if loaded is not None:
            return loaded
    return None


def _request_confirms_deep_writer(request: dict[str, Any] | None, proof_bundle: dict[str, Any]) -> bool:
    merged: dict[str, Any] = {}
    if isinstance(request, dict):
        merged.update(request)
    merged.update({k: v for k, v in proof_bundle.items() if k in {"operator_kind", "model_mode", "reasoning_effort", "tool_mode"}})
    operator_kind = _text(merged.get("operator_kind")).lower()
    model_mode = _text(merged.get("model_mode")).lower()
    reasoning_effort = _text(merged.get("reasoning_effort")).lower()
    tool_mode = _text(merged.get("tool_mode")).lower()
    return (
        operator_kind == "deep_writer"
        and model_mode == "pro"
        and reasoning_effort == "deep_research"
        and tool_mode == "deep_research"
    )


def validate_deep_proof_bundle(proof_bundle: dict[str, Any] | None, *, chapter_id: str = "") -> dict[str, Any]:
    """Validate that Deep Research proof is a real deep-writer sidecar."""
    proof = proof_bundle or {}
    paths = [
        _path_text(proof.get("deep_proof_path")),
        _path_text(proof.get("deep_research_state_proof")),
        _path_text(proof.get("deep_writer_proof")),
    ]
    request_dir = _path_text(proof.get("request_dir"))
    if request_dir:
        for name in DEEP_PROOF_FILENAMES:
            paths.append(str(Path(request_dir).expanduser() / name))

    checked_paths: list[str] = []
    errors: list[str] = []
    for raw_path in [p for p in paths if p]:
        proof_path = Path(raw_path).expanduser()
        checked_paths.append(str(proof_path))
        state = _read_json_path(proof_path)
        if state is None:
            errors.append(f"missing_or_invalid_deep_proof:{proof_path}")
            continue
        request = _deep_request_sidecar_for(proof_path, proof)
        if not state.get("ok"):
            errors.append(f"deep_proof_not_ok:{proof_path}")
            continue
        if not _request_confirms_deep_writer(request, proof):
            errors.append(f"deep_request_not_confirmed:{proof_path}")
            continue
        return {
            "ok": True,
            "chapter_id": chapter_id,
            "deep_proof_path": str(proof_path),
            "deep_request_path": str(proof_path.parent / "report-operator-request.json")
            if (proof_path.parent / "report-operator-request.json").exists()
            else str(proof_path.parent / "request.json")
            if (proof_path.parent / "request.json").exists()
            else "",
            "checked_paths": checked_paths,
        }

    embedded_state = proof.get("deep_research_state")
    if isinstance(embedded_state, dict) and embedded_state.get("ok") and _request_confirms_deep_writer(None, proof):
        return {
            "ok": True,
            "chapter_id": chapter_id,
            "deep_proof_path": _path_text(proof.get("deep_proof_path")),
            "deep_request_path": _path_text(proof.get("deep_request_path")),
            "checked_paths": checked_paths,
        }
    return {
        "ok": False,
        "chapter_id": chapter_id,
        "deep_proof_path": "",
        "deep_request_path": "",
        "checked_paths": checked_paths,
        "errors": errors or ["deep_proof_missing"],
    }


def chapter_requires_deep_proof(chapter_job: dict[str, Any], evidence_pack: dict[str, Any]) -> bool:
    chapter = evidence_pack.get("chapter") if isinstance(evidence_pack.get("chapter"), dict) else {}
    priority = _text(chapter_job.get("priority") or chapter.get("priority")).upper()
    explicit = bool(chapter_job.get("deep_writer_required") or chapter.get("deep_writer_required"))
    return explicit or priority in {"P0", "P1"}


def run_chapter_verifier(
    chapter_job: dict[str, Any],
    markdown: str,
    evidence_pack: dict[str, Any],
    proof_bundle: dict[str, Any] | None = None,
    *,
    grounded_claim_target: float = 0.9,
) -> dict[str, Any]:
    """Verify one chapter without inventing evidence or replacing model review."""
    text = _text(markdown)
    chapter_id = _text(chapter_job.get("chapter_id") or evidence_pack.get("chapter_id") or "chapter")
    refs = _evidence_refs(evidence_pack)
    claims = _claim_sentences(text)
    referenced = [ref for ref in refs if ref and ref in text]
    claims_with_refs = []
    for claim in claims:
        if any(ref in claim for ref in refs) or VIDEO_REF_RE.search(claim):
            claims_with_refs.append(claim)
            continue
        # Actionable follow-ups can inherit the chapter's cited evidence context,
        # but only after the chapter has cited at least one supplied reference.
        if referenced and ACTION_INSIGHT_RE.search(claim):
            claims_with_refs.append(claim)
    grounded_claim_ratio = 1.0 if not claims else len(claims_with_refs) / len(claims)
    proof = proof_bundle or {}
    deep_required = chapter_requires_deep_proof(chapter_job, evidence_pack)
    deep_proof = validate_deep_proof_bundle(proof, chapter_id=chapter_id) if deep_required else {"ok": True}
    checks = {
        "has_clear_thesis": bool(re.search(r"(判断|结论|认为|说明|显示|意味着)", text)) and len(text) >= 80,
        "uses_required_evidence": bool(referenced),
        "grounded_claim_ratio": round(grounded_claim_ratio, 4),
        "has_counter_evidence": bool(evidence_pack.get("counter_evidence")) or "证据不足" in text or "不确定" in text,
        "has_actionable_insight": bool(re.search(r"(建议|应当|可以|下一步|观察|优先|风险)", text)),
        "no_internal_field_leak": not FORBIDDEN_PUBLIC_FIELD_RE.search(text),
        "no_unsupported_claim": grounded_claim_ratio >= grounded_claim_target,
        "not_video_by_video_summary": len(re.findall(r"(^|\n)\s*[-*]?\s*V\d{3}", text)) <= max(2, len(claims) // 2),
        "deep_proof_present_if_required": (not deep_required) or bool(deep_proof.get("ok")),
    }
    repair_reasons = [key for key, value in checks.items() if value is False]
    if checks["grounded_claim_ratio"] < grounded_claim_target:
        repair_reasons.append("grounded_claim_ratio_below_target")
    status = "passed" if not repair_reasons else "repair_needed"
    if not checks["no_internal_field_leak"] or not checks["deep_proof_present_if_required"]:
        status = "failed"
    return {
        "schema_version": "chapter_verification.v1",
        "chapter_id": chapter_id,
        "status": status,
        "checks": checks,
        "claim_count": len(claims),
        "grounded_claim_count": len(claims_with_refs),
        "referenced_evidence": referenced,
        "repair_reasons": repair_reasons,
        "grounded_claim_target": grounded_claim_target,
        "deep_writer_required": deep_required,
        "deep_proof": deep_proof,
    }


def _claim_is_grounded_or_safe(sentence: str, refs: list[str], referenced: list[str]) -> bool:
    if len(sentence.strip()) < 18:
        return True
    if sentence.lstrip().startswith("#"):
        return True
    if SAFETY_DOWNGRADE_RE.search(sentence):
        return True
    if any(ref in sentence for ref in refs) or VIDEO_REF_RE.search(sentence):
        return True
    return bool(referenced and ACTION_INSIGHT_RE.search(sentence))


def _repair_markdown_once(markdown: str, evidence_pack: dict[str, Any]) -> tuple[str, list[str]]:
    refs = _evidence_refs(evidence_pack)
    referenced = [ref for ref in refs if ref and ref in markdown]
    removed: list[str] = []
    repaired_lines: list[str] = []
    for line in str(markdown or "").splitlines():
        if FORBIDDEN_PUBLIC_FIELD_RE.search(line):
            line = FORBIDDEN_PUBLIC_FIELD_RE.sub("[内部字段已过滤]", line)
        if not line.strip() or line.lstrip().startswith("#"):
            repaired_lines.append(line)
            continue
        pieces = re.split(r"([。！？!?])", line)
        kept: list[str] = []
        for idx in range(0, len(pieces), 2):
            sentence = pieces[idx].strip()
            punct = pieces[idx + 1] if idx + 1 < len(pieces) else ""
            if not sentence:
                continue
            if _claim_is_grounded_or_safe(sentence, refs, referenced):
                kept.append(sentence + punct)
            else:
                removed.append(sentence[:180])
        if kept:
            repaired_lines.append("".join(kept))
        elif removed:
            repaired_lines.append("证据不足：上一段判断缺少章节证据支撑，暂不作为结论。")
    return "\n".join(repaired_lines).strip(), removed


def run_chapter_repair_loop(
    chapter_job: dict[str, Any],
    markdown: str,
    evidence_pack: dict[str, Any],
    proof_bundle: dict[str, Any] | None = None,
    *,
    max_attempts: int = 3,
    grounded_claim_target: float = 0.9,
) -> dict[str, Any]:
    """Run a bounded deterministic safety repair after model writing.

    This does not invent replacement analysis; it only removes unsafe leaks and
    unsupported claims, then re-runs the verifier. Missing Deep Research proof
    remains non-repairable and blocks publication.
    """
    current = _text(markdown)
    attempts: list[dict[str, Any]] = []
    initial = run_chapter_verifier(
        chapter_job,
        current,
        evidence_pack,
        proof_bundle,
        grounded_claim_target=grounded_claim_target,
    )
    verification = initial
    if verification.get("status") == "passed":
        return {
            "schema_version": "chapter_repair_loop.v1",
            "status": "passed",
            "publish_decision": "publish",
            "attempt_count": 0,
            "attempts": attempts,
            "markdown": current,
            "initial_verification": initial,
            "final_verification": verification,
        }
    if "deep_proof_present_if_required" in verification.get("repair_reasons", []):
        return {
            "schema_version": "chapter_repair_loop.v1",
            "status": "blocked",
            "publish_decision": "blocked",
            "attempt_count": 0,
            "attempts": attempts,
            "markdown": current,
            "initial_verification": initial,
            "final_verification": verification,
            "blocked_reasons": ["deep_proof_missing_or_unconfirmed"],
        }

    for attempt in range(1, max_attempts + 1):
        repaired, removed = _repair_markdown_once(current, evidence_pack)
        attempts.append(
            {
                "attempt": attempt,
                "removed_unsupported_claims": removed,
                "changed": repaired != current,
            }
        )
        if repaired == current:
            break
        current = repaired
        verification = run_chapter_verifier(
            chapter_job,
            current,
            evidence_pack,
            proof_bundle,
            grounded_claim_target=grounded_claim_target,
        )
        attempts[-1]["status_after"] = verification.get("status")
        attempts[-1]["repair_reasons_after"] = verification.get("repair_reasons", [])
        if verification.get("status") == "passed":
            break

    publish_decision = "publish" if verification.get("status") == "passed" else "internal_only"
    return {
        "schema_version": "chapter_repair_loop.v1",
        "status": "passed" if publish_decision == "publish" else "internal_only",
        "publish_decision": publish_decision,
        "attempt_count": len(attempts),
        "attempts": attempts,
        "markdown": current,
        "initial_verification": initial,
        "final_verification": verification,
        "blocked_reasons": [] if publish_decision == "publish" else list(verification.get("repair_reasons") or []),
    }


def build_quality_score(report_ir: dict[str, Any], chapter_verifications: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate chapter verification into the PRD A/B/C/D publish decision."""
    verifications = [item for item in chapter_verifications if isinstance(item, dict)]
    total = max(1, len(verifications))
    passed = sum(1 for item in verifications if item.get("status") == "passed")
    failed = sum(1 for item in verifications if item.get("status") == "failed")
    avg_grounding = sum(float((item.get("checks") or {}).get("grounded_claim_ratio") or 0) for item in verifications) / total
    evidence_grounding_score = avg_grounding * 100
    structure_completeness_score = (passed / total) * 100
    counterargument_score = (
        sum(1 for item in verifications if (item.get("checks") or {}).get("has_counter_evidence")) / total
    ) * 100
    safety_score = 0 if failed else 100
    weighted = (
        0.20 * evidence_grounding_score
        + 0.15 * structure_completeness_score
        + 0.15 * structure_completeness_score
        + 0.15 * evidence_grounding_score
        + 0.10 * safety_score
        + 0.10 * structure_completeness_score
        + 0.05 * counterargument_score
        + 0.05 * safety_score
        + 0.05 * structure_completeness_score
    )
    grade = "A" if weighted >= 85 else "B" if weighted >= 75 else "C" if weighted >= 60 else "D"
    publish_decision = "publish" if grade in {"A", "B"} and failed == 0 else "internal_only" if grade == "C" else "blocked"
    return {
        "schema_version": "report_quality_score.v1",
        "report_id": report_ir.get("report_id") or "N/A",
        "score": round(weighted, 2),
        "grade": grade,
        "publish_decision": publish_decision,
        "chapter_count": total,
        "passed_chapter_count": passed,
        "failed_chapter_count": failed,
        "scores": {
            "evidence_grounding_score": round(evidence_grounding_score, 2),
            "structure_completeness_score": round(structure_completeness_score, 2),
            "counterargument_score": round(counterargument_score, 2),
            "safety_score": round(safety_score, 2),
        },
    }


def write_validation_sidecars(report_dir: Path, report_ir: dict[str, Any], chapter_verifications: list[dict[str, Any]]) -> dict[str, Any]:
    validation_dir = Path(report_dir) / "validation"
    validation_dir.mkdir(parents=True, exist_ok=True)
    quality = build_quality_score(report_ir, chapter_verifications)
    (validation_dir / "chapter-validation-summary.json").write_text(
        json.dumps({"chapters": chapter_verifications}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (validation_dir / "claim-verification.json").write_text(
        json.dumps({"chapters": chapter_verifications}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (validation_dir / "quality-score.json").write_text(
        json.dumps(quality, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return quality
