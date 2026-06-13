"""Generate a Solar-style Phase 0 verification report from recorded artifacts."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .artifact_adapter import Phase0ArtifactReportBundle, load_phase0_matrix


def _jsonable(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return value


def _status_counts_table(counts: dict[str, int]) -> str:
    lines = [
        "| Status | Count |",
        "| --- | ---: |",
    ]
    for status, count in sorted(counts.items()):
        lines.append(f"| `{status}` | {count} |")
    return "\n".join(lines)


def _claim_table(bundle: Phase0ArtifactReportBundle) -> str:
    lines = [
        "| Claim | Verdict | Readiness | Evidence | Blockers |",
        "| --- | --- | --- | ---: | ---: |",
    ]
    for claim in bundle.claims:
        evidence_count = len(claim.validation_evidence)
        blocker_count = len(claim.blockers)
        lines.append(
            f"| `{claim.claim_id}` | `{claim.claim_verdict_status}` | "
            f"`{claim.execution_readiness_status}` | {evidence_count} | {blocker_count} |"
        )
    return "\n".join(lines)


def _issue_notes(bundle: Phase0ArtifactReportBundle) -> str:
    lines: list[str] = []
    for claim in bundle.claims:
        if not claim.blockers and not claim.next_step:
            continue
        lines.append(f"### `{claim.claim_id}`")
        if claim.blockers:
            lines.append("")
            lines.append("Blockers:")
            for blocker in claim.blockers[:5]:
                lines.append(f"- {blocker}")
        if claim.next_step:
            lines.append("")
            lines.append(f"Next step: {claim.next_step}")
        lines.append("")
    return "\n".join(lines).strip()


def build_summary_payload(
    bundle: Phase0ArtifactReportBundle,
    *,
    report_path: str,
    run_id: str,
    generated_at: str,
) -> dict[str, Any]:
    return {
        "schema_version": "solar.phase0.verification_report.v0",
        "run_id": run_id,
        "generated_at": generated_at,
        "mode": "artifact_replay",
        "source_matrix_path": bundle.source_matrix_path,
        "paper_level_status": bundle.paper_level_status,
        "full_paper_claim_status": bundle.full_paper_claim_status,
        "claim_status_counts": dict(bundle.claim_status_counts),
        "execution_readiness_summary": dict(bundle.execution_readiness_summary),
        "detailed_readiness_counts": dict(bundle.detailed_readiness_counts),
        "claim_count": len(bundle.claims),
        "executable_target_count": bundle.executable_target_count,
        "report_path": report_path,
        "limitations": [
            "This report replays recorded Phase 0 artifacts; it does not execute new benchmark commands.",
            "Planning evidence and execution readiness are not treated as claim reproduction evidence.",
            "Detailed readiness labels are preserved separately from broad Solar readiness categories.",
        ],
    }


def render_markdown_report(
    bundle: Phase0ArtifactReportBundle,
    *,
    run_id: str,
    generated_at: str,
    summary_path: str,
) -> str:
    issue_notes = _issue_notes(bundle)
    if not issue_notes:
        issue_notes = "No claim-level blockers or next steps were recorded in the source matrix."

    return f"""# Solar Phase 0 Verification Report

Generated: `{generated_at}`
Run id: `{run_id}`
Mode: `artifact_replay`
Source matrix: `{bundle.source_matrix_path}`

## Verdict

| Field | Value |
| --- | --- |
| Paper-level status | `{bundle.paper_level_status}` |
| Full-paper claim status | `{bundle.full_paper_claim_status}` |
| Claims | {len(bundle.claims)} |
| Executable targets in source matrix | {bundle.executable_target_count} |

## Claim Status Counts

{_status_counts_table(bundle.claim_status_counts)}

## Readiness Summary

{_status_counts_table(bundle.execution_readiness_summary)}

## Claim Matrix

{_claim_table(bundle)}

## Issue Notes

{issue_notes}

## Solar Interpretation

- Claim verdicts and execution readiness remain separate.
- Readiness/planning evidence does not upgrade a claim verdict.
- Negative executed evidence remains `not_reproduced`.
- This run produced a report from recorded artifacts and did not execute live benchmark jobs.
- Machine-readable summary: `{summary_path}`
"""


def write_report(
    *,
    matrix_path: str | Path,
    output_dir: str | Path,
    run_id: str | None = None,
) -> dict[str, str]:
    bundle = load_phase0_matrix(matrix_path)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    actual_run_id = run_id or f"phase0-artifact-replay-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    report_path = out / "phase0_verification_report.md"
    summary_path = out / "phase0_verification_summary.json"

    summary = build_summary_payload(
        bundle,
        report_path=str(report_path),
        run_id=actual_run_id,
        generated_at=generated_at,
    )
    report = render_markdown_report(
        bundle,
        run_id=actual_run_id,
        generated_at=generated_at,
        summary_path=str(summary_path),
    )

    summary_path.write_text(json.dumps(_jsonable(summary), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(report, encoding="utf-8")
    return {
        "report_path": str(report_path),
        "summary_path": str(summary_path),
        "run_id": actual_run_id,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a Solar Phase 0 verification report from artifacts.")
    parser.add_argument("--matrix", required=True, type=Path, help="Path to an all_claim_verification_matrix.json artifact.")
    parser.add_argument("--output-dir", required=True, type=Path, help="Directory for report outputs.")
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()
    result = write_report(matrix_path=args.matrix, output_dir=args.output_dir, run_id=args.run_id)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
