#!/usr/bin/env python3
"""Project Solar-managed AutoSci run evidence into a human-facing workspace.

The workspace is intentionally a projection of validated run artifacts.  It is
not the execution ledger: logs, envelopes, retry metadata, and operator status
stay under artifacts/autosci/runs and harness/run.
"""
from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

WORKSPACE_REL = "artifacts/autosci/workspace"
WIKI_SUBDIRS = [
    "papers",
    "foundations",
    "concepts",
    "methods",
    "people",
    "topics",
    "ideas",
    "experiments",
    "outputs",
    "graph",
]


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def load_json_if_exists(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return load_json(path)


def write_text_if_changed(path: Path, content: str) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def slugify(value: str, *, fallback: str = "item") -> str:
    raw = value.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", raw).strip("-")
    return slug or fallback


def as_posix(path: Path) -> str:
    return path.as_posix()


def rel_to_output(path: Path, output_harness: Path) -> str:
    try:
        return as_posix(path.resolve().relative_to(output_harness.resolve()))
    except ValueError:
        return str(path.resolve())


def artifact_path(path: Path) -> str:
    return str(path.resolve())


def value_as_text(value: Any, default: str = "N/A") -> str:
    if value is None:
        return default
    if isinstance(value, str):
        return value.strip() or default
    return str(value)


def list_lines(items: list[Any]) -> str:
    if not items:
        return "- N/A\n"
    return "".join(f"- {value_as_text(item)}\n" for item in items)


def evidence_link(path: Path, output_harness: Path) -> str:
    return rel_to_output(path, output_harness)


def frontmatter(entity_type: str, entity_id: str, title: str, run_id: str, source_evidence: str) -> str:
    return "\n".join(
        [
            "---",
            f"entity_type: {json.dumps(entity_type)}",
            f"entity_id: {json.dumps(entity_id)}",
            f"title: {json.dumps(title)}",
            f"run_id: {json.dumps(run_id)}",
            f"source_evidence: {json.dumps(source_evidence)}",
            "managed_by: \"solar-autosci-workspace-projector\"",
            "---",
            "",
        ]
    )


def bootstrap_workspace(workspace: Path) -> list[Path]:
    wiki = workspace / "wiki"
    updated: list[Path] = []
    for subdir in WIKI_SUBDIRS:
        (wiki / subdir).mkdir(parents=True, exist_ok=True)
    (workspace / "raw" / "papers").mkdir(parents=True, exist_ok=True)

    readme = """# Solar AutoSci Workspace

This is the human-facing research workspace projected from Solar AutoSci run evidence.

- Read and edit research-facing pages under `wiki/`.
- Keep execution logs, envelopes, gate results, and operator state under Solar-managed `artifacts/autosci/runs/` and `harness/run/`.
- Treat this workspace as a durable research memory view, not as the source of execution truth.
"""
    if write_text_if_changed(workspace / "README.md", readme):
        updated.append(workspace / "README.md")

    raw_readme = """# Raw Sources

This directory is reserved for explicit human-facing source references. Solar-managed run inputs and parser traces remain in `artifacts/autosci/runs/<run-id>/`.
"""
    if write_text_if_changed(workspace / "raw" / "README.md", raw_readme):
        updated.append(workspace / "raw" / "README.md")
    return updated


def project_paper(run_dir: Path, wiki: Path, output_harness: Path, run_id: str) -> list[Path]:
    evidence_path = run_dir / "research_paper.analyzed.json"
    payload = load_json_if_exists(evidence_path)
    if payload is None:
        evidence_path = run_dir / "research_paper.json"
        payload = load_json_if_exists(evidence_path)
    if payload is None:
        return []

    paper = payload.get("outputs", {}).get("paper")
    if not isinstance(paper, dict):
        return []

    paper_id = value_as_text(paper.get("paper_id"), "paper-unknown")
    title = value_as_text(paper.get("title"), paper_id)
    page = wiki / "papers" / f"{slugify(paper_id)}.md"
    analysis = paper.get("analysis") if isinstance(paper.get("analysis"), dict) else {}
    sections = paper.get("sections") if isinstance(paper.get("sections"), list) else []

    body = [
        frontmatter("paper", paper_id, title, run_id, evidence_link(evidence_path, output_harness)),
        f"# {title}\n\n",
        "## Source\n\n",
        f"- Paper id: `{paper_id}`\n",
        f"- Source ref: `{value_as_text(paper.get('source_ref'))}`\n",
        f"- Source type: `{value_as_text(paper.get('source_type'))}`\n",
        f"- Parse status: `{value_as_text(paper.get('parse_status'))}`\n",
        f"- Evidence: `{evidence_link(evidence_path, output_harness)}`\n\n",
        "## Abstract\n\n",
        f"{value_as_text(paper.get('abstract'))}\n\n",
    ]
    if analysis:
        body.extend(
            [
                "## Analysis\n\n",
                f"{value_as_text(analysis.get('summary'))}\n\n",
                "### Key Concepts\n\n",
                list_lines([str(item) for item in analysis.get("key_concepts", []) if str(item).strip()]),
                "\n",
            ]
        )
    if sections:
        body.append("## Sections\n\n")
        for section in sections:
            if not isinstance(section, dict):
                continue
            heading = value_as_text(section.get("title"), value_as_text(section.get("section_id"), "Section"))
            anchor = value_as_text(section.get("source_anchor"))
            text = value_as_text(section.get("text"))
            body.extend([f"### {heading}\n\n", f"Source anchor: `{anchor}`\n\n", f"{text}\n\n"])

    if write_text_if_changed(page, "".join(body)):
        return [page]
    return []


def project_methods(run_dir: Path, wiki: Path, output_harness: Path, run_id: str) -> list[Path]:
    evidence_path = run_dir / "research_method.json"
    payload = load_json_if_exists(evidence_path)
    methods = payload.get("outputs", {}).get("methods") if payload else None
    if not isinstance(methods, list):
        return []

    updated: list[Path] = []
    for method in methods:
        if not isinstance(method, dict):
            continue
        method_id = value_as_text(method.get("method_id"), "method-unknown")
        title = value_as_text(method.get("name"), method_id)
        page = wiki / "methods" / f"{slugify(method_id)}.md"
        content = "".join(
            [
                frontmatter("method", method_id, title, run_id, evidence_link(evidence_path, output_harness)),
                f"# {title}\n\n",
                f"- Method id: `{method_id}`\n",
                f"- Source anchor: `{value_as_text(method.get('source_anchor'))}`\n",
                f"- Evidence: `{evidence_link(evidence_path, output_harness)}`\n\n",
                "## Summary\n\n",
                f"{value_as_text(method.get('summary'))}\n\n",
                "## Procedure\n\n",
                list_lines([str(item) for item in method.get("procedure", []) if str(item).strip()]),
                "\n## Source Papers\n\n",
                list_lines([str(item) for item in method.get("source_papers", []) if str(item).strip()]),
            ]
        )
        if write_text_if_changed(page, content):
            updated.append(page)
    return updated


def project_claims_output(run_dir: Path, wiki: Path, output_harness: Path, run_id: str) -> list[Path]:
    evidence_path = run_dir / "research_claims.json"
    payload = load_json_if_exists(evidence_path)
    claims = payload.get("outputs", {}).get("claims") if payload else None
    if not isinstance(claims, list):
        return []

    page = wiki / "outputs" / f"claims-{slugify(run_id)}.md"
    body = [
        frontmatter("claim_set", f"claims-{run_id}", f"Claims from {run_id}", run_id, evidence_link(evidence_path, output_harness)),
        f"# Claims from `{run_id}`\n\n",
        f"Evidence: `{evidence_link(evidence_path, output_harness)}`\n\n",
    ]
    for claim in claims:
        if not isinstance(claim, dict):
            continue
        claim_id = value_as_text(claim.get("claim_id"), "claim")
        body.extend(
            [
                f"## {claim_id}\n\n",
                f"{value_as_text(claim.get('text'))}\n\n",
                f"- Type: `{value_as_text(claim.get('claim_type'))}`\n",
                f"- Testability: `{value_as_text(claim.get('testability'))}`\n",
                f"- Verification: `{value_as_text(claim.get('verification_status'))}`\n",
                f"- Source anchor: `{value_as_text(claim.get('source_anchor'))}`\n\n",
            ]
        )
    if write_text_if_changed(page, "".join(body)):
        return [page]
    return []


def project_ideas(run_dir: Path, wiki: Path, output_harness: Path, run_id: str) -> list[Path]:
    evidence_path = run_dir / "idea_candidate.json"
    payload = load_json_if_exists(evidence_path)
    ideas = payload.get("outputs", {}).get("ideas") if payload else None
    if not isinstance(ideas, list):
        return []

    updated: list[Path] = []
    for idea in ideas:
        if not isinstance(idea, dict):
            continue
        idea_id = value_as_text(idea.get("idea_id"), "idea-unknown")
        title = value_as_text(idea.get("title"), idea_id)
        page = wiki / "ideas" / f"{slugify(idea_id)}.md"
        content = "".join(
            [
                frontmatter("idea", idea_id, title, run_id, evidence_link(evidence_path, output_harness)),
                f"# {title}\n\n",
                f"- Idea id: `{idea_id}`\n",
                f"- Status: `{value_as_text(idea.get('status'))}`\n",
                f"- Duplicate status: `{value_as_text(idea.get('duplicate_status'))}`\n",
                f"- Evidence: `{evidence_link(evidence_path, output_harness)}`\n\n",
                "## Hypothesis\n\n",
                f"{value_as_text(idea.get('hypothesis'))}\n\n",
                "## Approach\n\n",
                f"{value_as_text(idea.get('approach'))}\n\n",
                "## Grounding\n\n",
                f"{value_as_text(idea.get('grounding_summary'))}\n",
            ]
        )
        if write_text_if_changed(page, content):
            updated.append(page)
    return updated


def project_experiment(run_dir: Path, wiki: Path, output_harness: Path, run_id: str) -> list[Path]:
    evidence_path = run_dir / "experiment_plan.json"
    payload = load_json_if_exists(evidence_path)
    plan = payload.get("outputs", {}).get("experiment_plan") if payload else None
    result_evidence_path = run_dir / "experiment_result.json"
    result_payload = load_json_if_exists(result_evidence_path)
    result = result_payload.get("outputs", {}).get("result") if result_payload else None
    if not isinstance(plan, dict) and not isinstance(result, dict):
        return []

    plan = plan if isinstance(plan, dict) else {}
    result = result if isinstance(result, dict) else {}
    experiment_id = value_as_text(result.get("experiment_id") or plan.get("experiment_id"), "experiment-unknown")
    title = value_as_text(plan.get("objective"), experiment_id)
    status = "completed" if result_payload and result_payload.get("status") == "completed" else value_as_text(plan.get("status"), "planned")
    outcome = value_as_text(result.get("outcome"), "N/A")
    source_path = result_evidence_path if result_payload and result_evidence_path.exists() else evidence_path
    page = wiki / "experiments" / f"{slugify(experiment_id)}.md"
    metric_lines = [
        f"- {value_as_text(metric.get('name'))}: `{value_as_text(metric.get('value'))}`\n"
        for metric in result.get("metrics", [])
        if isinstance(metric, dict)
    ]
    evidence_id_lines = [
        f"- `{value_as_text(evidence_id)}`\n"
        for evidence_id in result.get("evidence_ids", [])
        if str(evidence_id).strip()
    ]
    frontmatter_lines = [
        "---",
        f"entity_type: {json.dumps('experiment')}",
        f"entity_id: {json.dumps(experiment_id)}",
        f"title: {json.dumps(title)}",
        f"run_id: {json.dumps(run_id)}",
        f"source_evidence: {json.dumps(evidence_link(source_path, output_harness))}",
        f"status: {status}",
        f"outcome: {outcome}",
        "managed_by: \"solar-autosci-workspace-projector\"",
        "---",
        "",
    ]
    content = "".join(
        [
            "\n".join(frontmatter_lines),
            f"# {title}\n\n",
            f"- Experiment id: `{experiment_id}`\n",
            f"- Status: `{status}`\n",
            f"- Outcome: `{outcome}`\n",
            f"- Execution mode: `{value_as_text(plan.get('execution_mode'))}`\n",
            f"- Approval required: `{value_as_text(plan.get('approval_required'))}`\n",
            f"- Plan evidence: `{evidence_link(evidence_path, output_harness) if evidence_path.exists() else 'N/A'}`\n",
            f"- Result evidence: `{evidence_link(result_evidence_path, output_harness) if result_evidence_path.exists() else 'N/A'}`\n\n",
            "## Hypothesis\n\n",
            f"{value_as_text(plan.get('hypothesis'))}\n\n",
            "## Procedure\n\n",
            list_lines([str(item) for item in plan.get("procedure", []) if str(item).strip()]),
            "\n## Success Criteria\n\n",
            list_lines([str(item) for item in plan.get("success_criteria", []) if str(item).strip()]),
            "\n## Result Metrics\n\n",
            "".join(metric_lines) if metric_lines else "- N/A\n",
            "\n## Result Evidence IDs\n\n",
            "".join(evidence_id_lines) if evidence_id_lines else "- N/A\n",
        ]
    )
    if write_text_if_changed(page, content):
        return [page]
    return []


def project_report(run_dir: Path, wiki: Path, output_harness: Path, run_id: str) -> list[Path]:
    evidence_path = run_dir / "scientific_report.json"
    payload = load_json_if_exists(evidence_path)
    report = payload.get("outputs", {}).get("report") if payload else None
    report_id = "report-" + slugify(run_id)
    title = f"Report from {run_id}"
    if isinstance(report, dict):
        report_id = value_as_text(report.get("report_id"), report_id)
        title = value_as_text(payload.get("inputs", {}).get("report_title"), title)

    source_report = run_dir / "report.md"
    if not source_report.exists() and payload is None:
        return []

    page = wiki / "outputs" / f"{slugify(report_id)}.md"
    source_body = source_report.read_text(encoding="utf-8") if source_report.exists() else ""
    body = [
        frontmatter("output", report_id, title, run_id, evidence_link(evidence_path if evidence_path.exists() else source_report, output_harness)),
        f"# {title}\n\n",
        f"- Report id: `{report_id}`\n",
        f"- Run artifact: `{evidence_link(source_report, output_harness) if source_report.exists() else 'N/A'}`\n",
        f"- Evidence: `{evidence_link(evidence_path, output_harness) if evidence_path.exists() else 'N/A'}`\n\n",
    ]
    if source_body.strip():
        body.extend(["## Report Body\n\n", source_body.strip(), "\n"])
    elif isinstance(report, dict):
        body.append("## Sections\n\n")
        for section in report.get("sections", []):
            if not isinstance(section, dict):
                continue
            body.extend([f"### {value_as_text(section.get('title'), 'Section')}\n\n", f"{value_as_text(section.get('body'))}\n\n"])

    if write_text_if_changed(page, "".join(body)):
        return [page]
    return []


def project_graph(run_dir: Path, wiki: Path, output_harness: Path, run_id: str) -> list[Path]:
    updated: list[Path] = []
    graph_dir = wiki / "graph"
    edges_path = graph_dir / "edges.jsonl"
    existing: set[str] = set()
    if edges_path.exists():
        existing = {line.strip() for line in edges_path.read_text(encoding="utf-8").splitlines() if line.strip()}

    new_lines: list[str] = []
    for name in ("research_graph_update.json", "research_graph_update.direct.json"):
        payload = load_json_if_exists(run_dir / name)
        edges = payload.get("outputs", {}).get("edges") if payload else None
        if not isinstance(edges, list):
            continue
        for edge in edges:
            if not isinstance(edge, dict):
                continue
            enriched = {**edge, "run_id": run_id, "source_evidence": rel_to_output(run_dir / name, output_harness)}
            line = json.dumps(enriched, sort_keys=True)
            if line not in existing:
                existing.add(line)
                new_lines.append(line)
    if new_lines:
        edges_path.parent.mkdir(parents=True, exist_ok=True)
        with edges_path.open("a", encoding="utf-8") as handle:
            for line in new_lines:
                handle.write(line + "\n")
        updated.append(edges_path)

    citations_path = graph_dir / "citations.jsonl"
    if write_text_if_changed(citations_path, citations_path.read_text(encoding="utf-8") if citations_path.exists() else ""):
        updated.append(citations_path)

    mutation_payload = load_json_if_exists(run_dir / "novelty_writeback.json")
    mutation_write = {}
    if mutation_payload:
        candidate = mutation_payload.get("outputs", {}).get("write")
        if isinstance(candidate, dict) and candidate.get("applied"):
            mutation_write = candidate

    context_brief = "\n".join(
        [
            "# Solar AutoSci Context Brief",
            "",
            f"Last projected run: `{run_id}`",
            f"Updated at: `{datetime.now(UTC).isoformat().replace('+00:00', 'Z')}`",
            *(
                [
                    f"Mutation target: `{value_as_text(mutation_write.get('idea_path'))}`",
                    f"Mutation edge: `{value_as_text(mutation_write.get('edge_path'))}`",
                    f"Mutation log: `{value_as_text(mutation_write.get('log_path'))}`",
                ]
                if mutation_write
                else []
            ),
            "",
            "Use `wiki/papers/`, `wiki/methods/`, `wiki/ideas/`, and `wiki/experiments/` for human research navigation.",
            "Use `wiki/graph/edges.jsonl` for structured graph edges from approved mutations and projected graph evidence.",
            "Use `artifacts/autosci/runs/` for Solar-managed execution evidence.",
            "",
        ]
    )
    if write_text_if_changed(graph_dir / "context_brief.md", context_brief):
        updated.append(graph_dir / "context_brief.md")

    open_questions = "# Open Questions\n\n- Pending explicit research questions from future Solar AutoSci runs.\n"
    if write_text_if_changed(graph_dir / "open_questions.md", open_questions):
        updated.append(graph_dir / "open_questions.md")
    return updated


def rebuild_index(workspace: Path, run_id: str) -> list[Path]:
    wiki = workspace / "wiki"
    lines = [
        "# Solar AutoSci Wiki\n\n",
        "Human-facing research memory projected from Solar-managed evidence.\n\n",
        f"Last projected run: `{run_id}`\n\n",
    ]
    for subdir in ["papers", "foundations", "concepts", "methods", "people", "topics", "ideas", "experiments", "outputs"]:
        lines.append(f"## {subdir.title()}\n\n")
        pages = sorted((wiki / subdir).glob("*.md"))
        if not pages:
            lines.append("- N/A\n\n")
            continue
        for page in pages:
            lines.append(f"- [{page.stem}]({subdir}/{page.name})\n")
        lines.append("\n")

    updated: list[Path] = []
    if write_text_if_changed(wiki / "index.md", "".join(lines)):
        updated.append(wiki / "index.md")
    return updated


def project_run_to_workspace(
    skill_run_path: Path,
    *,
    output_harness: Path,
    workspace_rel: str = WORKSPACE_REL,
) -> dict[str, Any]:
    payload = load_json(skill_run_path)
    inputs = payload.get("inputs", {})
    run_id = value_as_text(inputs.get("run_id"), value_as_text(payload.get("sprint_id"), "autosci-run"))
    work_dir = value_as_text(inputs.get("work_dir"), "")
    run_dir = output_harness / work_dir
    workspace = output_harness / workspace_rel
    wiki = workspace / "wiki"

    updated = bootstrap_workspace(workspace)
    updated.extend(project_paper(run_dir, wiki, output_harness, run_id))
    updated.extend(project_methods(run_dir, wiki, output_harness, run_id))
    updated.extend(project_claims_output(run_dir, wiki, output_harness, run_id))
    updated.extend(project_ideas(run_dir, wiki, output_harness, run_id))
    updated.extend(project_experiment(run_dir, wiki, output_harness, run_id))
    updated.extend(project_report(run_dir, wiki, output_harness, run_id))
    updated.extend(project_graph(run_dir, wiki, output_harness, run_id))
    updated.extend(rebuild_index(workspace, run_id))

    updated_unique = []
    seen: set[Path] = set()
    for path in updated:
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            updated_unique.append(path)

    return {
        "workspace_root": artifact_path(workspace),
        "wiki_root": artifact_path(wiki),
        "solar_managed_run_dir": artifact_path(run_dir),
        "updated_count": len(updated_unique),
        "updated_paths": [artifact_path(path) for path in updated_unique],
        "index_path": artifact_path(wiki / "index.md"),
        "policy": "human-facing workspace projection; execution logs remain Solar-managed",
    }
