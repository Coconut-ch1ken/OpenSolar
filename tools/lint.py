#!/usr/bin/env python3
"""Local AutoSci wiki lint helper."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]


def default_wiki_root() -> Path:
    raw = os.environ.get("AUTOSCI_WIKI_ROOT") or os.environ.get("WIKI_ROOT")
    if raw:
        return Path(raw).expanduser()
    return Path(os.environ.get("HARNESS_DIR", REPO_ROOT / "harness")) / "artifacts" / "autosci" / "workspace" / "wiki"


def markdown_pages(root: Path) -> list[Path]:
    return [path for path in sorted(root.rglob("*.md")) if ".obsidian" not in path.parts] if root.exists() else []


def read_edges(root: Path) -> tuple[int, list[dict[str, Any]]]:
    path = root / "graph" / "edges.jsonl"
    if not path.exists():
        return 0, [{"severity": "warn", "message": "graph/edges.jsonl is missing"}]
    count = 0
    issues: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            edge = json.loads(line)
        except json.JSONDecodeError as exc:
            issues.append({"severity": "error", "line": line_no, "message": str(exc)})
            continue
        if not isinstance(edge, dict):
            issues.append({"severity": "error", "line": line_no, "message": "edge must be a JSON object"})
            continue
        if not (edge.get("source") or edge.get("source_id") or edge.get("source_path")):
            issues.append({"severity": "error", "line": line_no, "message": "edge missing source"})
        if not (edge.get("target") or edge.get("target_id") or edge.get("target_path")):
            issues.append({"severity": "error", "line": line_no, "message": "edge missing target"})
        if not (edge.get("relation") or edge.get("edge_type")):
            issues.append({"severity": "error", "line": line_no, "message": "edge missing relation"})
        count += 1
    return count, issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wiki-root", default=str(default_wiki_root()))
    args = parser.parse_args()
    root = Path(args.wiki_root).expanduser()
    pages = markdown_pages(root)
    edge_count, issues = read_edges(root)
    error_count = sum(1 for issue in issues if issue["severity"] == "error")
    payload = {
        "schema": "autosci_wiki_lint_cli.v1",
        "ok": error_count == 0,
        "status": "completed" if error_count == 0 else "failed",
        "wiki_root": str(root.resolve()),
        "page_count": len(pages),
        "edge_count": edge_count,
        "issues": issues,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 1 if error_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
