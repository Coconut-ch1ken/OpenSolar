#!/usr/bin/env python3
"""AutoSci-compatible local research wiki tool.

This tool provides the native wiki ABI expected by the AutoSci skill wrappers:
read-only retrieval commands plus explicit local mutation commands.  It only
touches files inside the selected wiki root and returns structured evidence for
each write.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
WIKI_SUBDIRS = ["papers", "concepts", "methods", "people", "topics", "ideas", "experiments", "outputs", "graph"]


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def default_wiki_root() -> Path:
    raw = os.environ.get("AUTOSCI_WIKI_ROOT") or os.environ.get("WIKI_ROOT")
    if raw:
        return Path(raw).expanduser()
    harness_dir = Path(os.environ.get("HARNESS_DIR", REPO_ROOT / "harness"))
    return harness_dir / "artifacts" / "autosci" / "workspace" / "wiki"


def slug(value: str) -> str:
    out = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return out or "node"


def rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def ensure_under_root(path: Path, root: Path) -> Path:
    resolved = path.resolve()
    root_resolved = root.resolve()
    try:
        resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise ValueError(f"path escapes wiki root: {path}") from exc
    return resolved


def atomic_write_text(path: Path, content: str) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8", errors="replace") == content:
        return False
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=str(path.parent), delete=False) as handle:
        handle.write(content)
        tmp_name = handle.name
    Path(tmp_name).replace(path)
    return True


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def print_payload(payload: dict[str, Any], as_json: bool = True) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(payload.get("summary") or json.dumps(payload, sort_keys=True))


def markdown_pages(wiki_root: Path) -> list[Path]:
    if not wiki_root.exists():
        return []
    return [
        path
        for path in sorted(wiki_root.rglob("*.md"))
        if ".obsidian" not in path.parts and path.is_file()
    ]


def first_heading(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            if title:
                return title
    return fallback


def read_edges(wiki_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    edges_path = wiki_root / "graph" / "edges.jsonl"
    edges: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    if not edges_path.exists():
        return edges, errors
    for line_no, line in enumerate(edges_path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append({"line": line_no, "error": str(exc)})
            continue
        if not isinstance(payload, dict):
            errors.append({"line": line_no, "error": "edge must be a JSON object"})
            continue
        source = edge_source(payload)
        target = edge_target(payload)
        relation = str(payload.get("relation") or payload.get("edge_type") or "").strip()
        if not source or not target or not relation:
            errors.append({"line": line_no, "error": "edge missing source, target, or relation"})
            continue
        edges.append(payload)
    return edges, errors


def edge_source(edge: dict[str, Any]) -> str:
    for key in ("source", "source_path", "source_id"):
        value = str(edge.get(key) or "").strip()
        if value:
            return value
    return ""


def edge_target(edge: dict[str, Any]) -> str:
    for key in ("target", "target_path", "target_id"):
        value = str(edge.get(key) or "").strip()
        if value:
            return value
    return ""


def resolve_existing_page(raw: str, wiki_root: Path) -> Path:
    candidate = Path(raw).expanduser()
    candidates: list[Path] = []
    if candidate.is_absolute():
        candidates.append(candidate)
    else:
        candidates.append(wiki_root / candidate)
        if candidate.suffix.lower() not in {".md", ".markdown"}:
            candidates.extend(wiki_root / subdir / f"{slug(raw)}.md" for subdir in WIKI_SUBDIRS if subdir != "graph")
        elif len(candidate.parts) == 1:
            candidates.extend(wiki_root / subdir / candidate.name for subdir in WIKI_SUBDIRS if subdir != "graph")
    checked: list[str] = []
    for item in candidates:
        checked.append(str(item))
        try:
            resolved = ensure_under_root(item, wiki_root)
        except ValueError:
            continue
        if resolved.exists() and resolved.is_file():
            return resolved
    raise FileNotFoundError(f"wiki page not found for {raw}; checked: {checked}")


def render_scalar(raw: str) -> str:
    value = raw.strip()
    if value == "":
        return '""'
    lowered = value.lower()
    if lowered in {"true", "false", "null"}:
        return lowered
    if re.fullmatch(r"-?\d+(?:\.\d+)?", value):
        return value
    if (value.startswith("[") and value.endswith("]")) or (value.startswith("{") and value.endswith("}")):
        try:
            json.loads(value)
            return value
        except json.JSONDecodeError:
            pass
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value
    return json.dumps(value)


def split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    match = re.match(r"^---\s*\n(.*?)\n---\s*(?:\n|$)", text, flags=re.S)
    if not match:
        return {}, text
    items: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line.strip() or ":" not in line:
            continue
        key, value = line.split(":", 1)
        items[key.strip()] = value.strip()
    return items, text[match.end():]


def render_frontmatter(items: dict[str, str], body: str) -> str:
    lines = ["---"]
    for key in sorted(items):
        lines.append(f"{key}: {items[key]}")
    lines.append("---")
    lines.append("")
    return "\n".join(lines) + body.lstrip("\n")


def parse_key_values(items: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"metadata argument must be KEY=VALUE: {item}")
        key, value = item.split("=", 1)
        key = key.strip()
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]*", key):
            raise ValueError(f"invalid metadata key: {key}")
        out[key] = render_scalar(value)
    return out


def cmd_set_meta(args: argparse.Namespace) -> int:
    wiki_root = Path(args.wiki_root).expanduser()
    page = resolve_existing_page(args.page, wiki_root)
    original = page.read_text(encoding="utf-8", errors="replace")
    metadata = parse_key_values(args.metadata)
    frontmatter, body = split_frontmatter(original)
    frontmatter.update(metadata)
    updated = render_frontmatter(frontmatter, body)
    changed = atomic_write_text(page, updated)
    print_payload(
        {
            "ok": True,
            "command": "set-meta",
            "wiki_root": str(wiki_root.resolve()),
            "path": rel(page, wiki_root),
            "changed": changed,
            "updated_keys": sorted(metadata),
            "before_sha256": sha256_text(original),
            "after_sha256": sha256_text(updated),
            "timestamp": utc_now(),
        },
        args.json,
    )
    return 0


def normalize_node_ref(raw: str, wiki_root: Path) -> str:
    try:
        page = resolve_existing_page(raw, wiki_root)
        return rel(page, wiki_root)
    except (FileNotFoundError, ValueError):
        value = raw.strip()
        return value or slug(raw)


def cmd_add_edge(args: argparse.Namespace) -> int:
    wiki_root = Path(args.wiki_root).expanduser()
    edges_path = ensure_under_root(wiki_root / "graph" / "edges.jsonl", wiki_root)
    source = normalize_node_ref(args.source, wiki_root)
    target = normalize_node_ref(args.target, wiki_root)
    evidence_ids = [item for item in args.evidence_id if item.strip()]
    edge = {
        "source": source,
        "target": target,
        "relation": args.relation.strip() or "related",
        "operation": args.operation,
        "evidence_ids": evidence_ids,
        "timestamp": utc_now(),
    }
    if args.edge_type:
        edge["edge_type"] = args.edge_type
    line = json.dumps(edge, sort_keys=True)
    existing_lines = edges_path.read_text(encoding="utf-8", errors="replace").splitlines() if edges_path.exists() else []
    comparable_existing: set[str] = set()
    for item in existing_lines:
        if not item.strip().startswith("{"):
            continue
        try:
            payload = json.loads(item)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            comparable_existing.add(
                json.dumps({key: value for key, value in payload.items() if key != "timestamp"}, sort_keys=True)
            )
    comparable_new = json.dumps({key: value for key, value in edge.items() if key != "timestamp"}, sort_keys=True)
    changed = False
    if comparable_new not in comparable_existing:
        edges_path.parent.mkdir(parents=True, exist_ok=True)
        with edges_path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
        changed = True
    print_payload(
        {
            "ok": True,
            "command": "add-edge",
            "wiki_root": str(wiki_root.resolve()),
            "path": rel(edges_path, wiki_root),
            "changed": changed,
            "edge": edge,
            "timestamp": utc_now(),
        },
        args.json,
    )
    return 0


def cmd_log(args: argparse.Namespace) -> int:
    wiki_root = Path(args.wiki_root).expanduser()
    log_path = ensure_under_root(wiki_root / "log.md", wiki_root)
    evidence = ", ".join(args.evidence_id) if args.evidence_id else "N/A"
    entry = (
        f"\n## {utc_now()} {args.event}\n\n"
        f"- Message: {args.message}\n"
        f"- Evidence: {evidence}\n"
    )
    before = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(entry)
    print_payload(
        {
            "ok": True,
            "command": "log",
            "wiki_root": str(wiki_root.resolve()),
            "path": rel(log_path, wiki_root),
            "changed": True,
            "event": args.event,
            "before_sha256": sha256_text(before),
            "after_sha256": sha256_text(log_path.read_text(encoding="utf-8", errors="replace")),
            "timestamp": utc_now(),
        },
        args.json,
    )
    return 0


def query_pages(wiki_root: Path, query: str, limit: int) -> list[dict[str, Any]]:
    terms = [term.lower() for term in re.findall(r"[A-Za-z0-9_+-]+", query) if term.strip()]
    hits: list[dict[str, Any]] = []
    for page in markdown_pages(wiki_root):
        text = page.read_text(encoding="utf-8", errors="replace")
        haystack = text.lower()
        score = sum(haystack.count(term) for term in terms) if terms else 0
        if query.lower() in haystack:
            score += 5
        if score <= 0:
            continue
        snippet = ""
        for line in text.splitlines():
            if any(term in line.lower() for term in terms):
                snippet = line.strip()
                break
        hits.append(
            {
                "path": rel(page, wiki_root),
                "title": first_heading(text, page.stem),
                "group": page.parent.name,
                "score": score,
                "snippet": snippet[:240],
            }
        )
    hits.sort(key=lambda item: (-int(item["score"]), str(item["path"])))
    return hits[: max(1, limit)]


def cmd_query(args: argparse.Namespace) -> int:
    wiki_root = Path(args.wiki_root).expanduser()
    hits = query_pages(wiki_root, args.query, args.limit)
    print_payload(
        {
            "ok": True,
            "command": "query",
            "wiki_root": str(wiki_root.resolve()),
            "query": args.query,
            "count": len(hits),
            "hits": hits,
        },
        args.json,
    )
    return 0


def cmd_neighbors(args: argparse.Namespace) -> int:
    wiki_root = Path(args.wiki_root).expanduser()
    node = normalize_node_ref(args.node, wiki_root)
    edges, errors = read_edges(wiki_root)
    neighbors = []
    for edge in edges:
        source = edge_source(edge)
        target = edge_target(edge)
        if node not in {source, target, str(edge.get("source_id") or ""), str(edge.get("target_id") or "")}:
            continue
        neighbors.append(
            {
                "source": source,
                "target": target,
                "relation": str(edge.get("relation") or edge.get("edge_type") or "related"),
                "direction": "out" if node == source else "in",
                "evidence_ids": [str(item) for item in edge.get("evidence_ids") or []],
            }
        )
    print_payload(
        {
            "ok": True,
            "command": "neighbors",
            "wiki_root": str(wiki_root.resolve()),
            "node": node,
            "count": len(neighbors),
            "neighbors": neighbors,
            "edge_errors": errors,
        },
        args.json,
    )
    return 0


def wiki_stats(wiki_root: Path) -> dict[str, Any]:
    pages = markdown_pages(wiki_root)
    by_group: dict[str, int] = {}
    for page in pages:
        by_group[page.parent.name] = by_group.get(page.parent.name, 0) + 1
    edges, errors = read_edges(wiki_root)
    return {
        "page_count": len(pages),
        "groups": dict(sorted(by_group.items())),
        "edge_count": len(edges),
        "edge_error_count": len(errors),
        "edge_errors": errors,
        "has_log": (wiki_root / "log.md").exists(),
        "has_index": (wiki_root / "index.md").exists(),
    }


def cmd_stats(args: argparse.Namespace) -> int:
    wiki_root = Path(args.wiki_root).expanduser()
    print_payload({"ok": True, "command": "stats", "wiki_root": str(wiki_root.resolve()), "stats": wiki_stats(wiki_root)}, args.json)
    return 0


def rebuild_index(wiki_root: Path) -> Path:
    lines = [
        "# Solar AutoSci Wiki",
        "",
        "Human-facing research memory from approved local wiki state.",
        "",
        f"Last rebuilt: `{utc_now()}`",
        "",
    ]
    for subdir in [item for item in WIKI_SUBDIRS if item != "graph"]:
        lines.extend([f"## {subdir.title()}", ""])
        pages = sorted((wiki_root / subdir).glob("*.md"))
        if not pages:
            lines.extend(["- N/A", ""])
            continue
        for page in pages:
            lines.append(f"- [{page.stem}]({subdir}/{page.name})")
        lines.append("")
    index_path = ensure_under_root(wiki_root / "index.md", wiki_root)
    atomic_write_text(index_path, "\n".join(lines) + "\n")
    return index_path


def rebuild_context(wiki_root: Path) -> Path:
    stats = wiki_stats(wiki_root)
    context_path = ensure_under_root(wiki_root / "graph" / "context_brief.md", wiki_root)
    group_lines = [f"- {group}: {count}" for group, count in stats["groups"].items()] or ["- N/A"]
    lines = [
        "# Solar AutoSci Context Brief",
        "",
        f"Last rebuilt: `{utc_now()}`",
        f"Pages: `{stats['page_count']}`",
        f"Edges: `{stats['edge_count']}`",
        f"Edge errors: `{stats['edge_error_count']}`",
        "",
        "## Groups",
        "",
        *group_lines,
        "",
        "Use `wiki/graph/edges.jsonl` for structured graph edges from approved mutations.",
        "Use `artifacts/autosci/runs/` for Solar-managed execution evidence.",
        "",
    ]
    atomic_write_text(context_path, "\n".join(lines))
    return context_path


def cmd_rebuild(args: argparse.Namespace) -> int:
    wiki_root = Path(args.wiki_root).expanduser()
    for subdir in WIKI_SUBDIRS:
        (wiki_root / subdir).mkdir(parents=True, exist_ok=True)
    index_path = rebuild_index(wiki_root)
    context_path = rebuild_context(wiki_root)
    print_payload(
        {
            "ok": True,
            "command": "rebuild",
            "wiki_root": str(wiki_root.resolve()),
            "rebuilt_paths": [rel(index_path, wiki_root), rel(context_path, wiki_root)],
            "stats": wiki_stats(wiki_root),
            "timestamp": utc_now(),
        },
        args.json,
    )
    return 0


def add_common(command: argparse.ArgumentParser) -> None:
    command.add_argument("--wiki-root", default=str(default_wiki_root()))
    command.add_argument("--json", action="store_true", help="Emit JSON output.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    command = sub.add_parser("query")
    command.add_argument("query")
    command.add_argument("--limit", type=int, default=10)
    add_common(command)
    command.set_defaults(func=cmd_query)

    command = sub.add_parser("neighbors")
    command.add_argument("node")
    add_common(command)
    command.set_defaults(func=cmd_neighbors)

    command = sub.add_parser("stats")
    add_common(command)
    command.set_defaults(func=cmd_stats)

    command = sub.add_parser("set-meta")
    command.add_argument("page")
    command.add_argument("metadata", nargs="+")
    add_common(command)
    command.set_defaults(func=cmd_set_meta)

    command = sub.add_parser("add-edge")
    command.add_argument("source")
    command.add_argument("target")
    command.add_argument("--relation", required=True)
    command.add_argument("--edge-type")
    command.add_argument("--operation", choices=["confirm", "propose", "reject"], default="confirm")
    command.add_argument("--evidence-id", action="append", default=[])
    add_common(command)
    command.set_defaults(func=cmd_add_edge)

    command = sub.add_parser("log")
    command.add_argument("message")
    command.add_argument("--event", default="wiki")
    command.add_argument("--evidence-id", action="append", default=[])
    add_common(command)
    command.set_defaults(func=cmd_log)

    command = sub.add_parser("rebuild")
    add_common(command)
    command.set_defaults(func=cmd_rebuild)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return int(args.func(args))
    except Exception as exc:  # noqa: BLE001 - CLI should return structured errors.
        print(json.dumps({"ok": False, "error": str(exc), "command": getattr(args, "command", "unknown")}, indent=2, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
