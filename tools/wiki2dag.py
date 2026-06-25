#!/usr/bin/env python3
"""Build a lightweight DAG JSON artifact from an AutoSci wiki."""

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


def rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def build_dag(wiki_root: Path) -> dict[str, Any]:
    nodes = [{"id": rel(path, wiki_root), "group": path.parent.name} for path in sorted(wiki_root.rglob("*.md"))] if wiki_root.exists() else []
    edges = []
    edges_path = wiki_root / "graph" / "edges.jsonl"
    if edges_path.exists():
        for line in edges_path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                edge = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(edge, dict):
                edges.append(edge)
    return {"schema": "autosci_wiki_dag.v1", "wiki_root": str(wiki_root.resolve()), "nodes": nodes, "edges": edges}


def cmd_build(args: argparse.Namespace) -> int:
    wiki_root = Path(args.wiki_root).expanduser()
    dag = build_dag(wiki_root)
    if args.out:
        out = Path(args.out).expanduser()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(dag, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        dag["path"] = str(out.resolve())
    dag.update({"ok": True, "status": "completed"})
    print(json.dumps(dag, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command")
    command = sub.add_parser("build")
    command.add_argument("--wiki-root", default=str(default_wiki_root()))
    command.add_argument("--out", default="")
    command.set_defaults(func=cmd_build)
    parser.set_defaults(func=cmd_build, command="build", wiki_root=str(default_wiki_root()), out="")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
