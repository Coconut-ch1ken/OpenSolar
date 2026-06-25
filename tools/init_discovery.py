#!/usr/bin/env python3
"""Init-time discovery planning helper for AutoSci-compatible workflows."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
HARNESS = REPO_ROOT / "harness"
sys.path.insert(0, str(HARNESS))

from plugins.autosci.backends.literature_discover import discover_literature, scan_wiki_papers  # noqa: E402


def default_workspace_root() -> Path:
    return Path(os.environ.get("HARNESS_DIR", HARNESS)).expanduser()


def default_wiki_root() -> Path:
    raw = os.environ.get("AUTOSCI_WIKI_ROOT") or os.environ.get("WIKI_ROOT")
    if raw:
        return Path(raw).expanduser()
    return default_workspace_root() / "artifacts" / "autosci" / "workspace" / "wiki"


def emit(command: str, status: str, payload: dict[str, Any], *, ok: bool = False) -> int:
    out = {"schema": "autosci_init_discovery_cli.v1", "command": command, "status": status, "ok": ok, **payload}
    print(json.dumps(out, indent=2, sort_keys=True))
    return 1 if status == "failed" else 0


def network_allowed(args: argparse.Namespace) -> bool:
    if args.no_network_fetch:
        return False
    return os.environ.get("AUTOSCI_DISABLE_NETWORK_FETCH", "").lower() not in {"1", "true", "yes"}


def cmd_prepare(args: argparse.Namespace) -> int:
    wiki_root = Path(args.wiki_root).expanduser()
    seeds = scan_wiki_papers(wiki_root, limit=args.limit)
    items = [{"title": item["title"], "arxiv_id": item["arxiv_id"], "path": str(item["path"])} for item in seeds]
    return emit("prepare", "completed", {"topic": args.topic, "wiki_root": str(wiki_root.resolve()), "seed_count": len(items), "seeds": items}, ok=True)


def cmd_plan(args: argparse.Namespace) -> int:
    steps = [
        "scan wiki seed papers",
        "run topic or anchor discovery",
        "deduplicate against wiki",
        "write source manifest evidence",
        "hand candidates to ingest after review",
    ]
    return emit("plan", "completed", {"topic": args.topic, "steps": steps, "requires_network": not args.no_network_fetch}, ok=True)


def cmd_fetch(args: argparse.Namespace) -> int:
    payload = discover_literature(
        query=args.topic,
        mode="wiki" if args.from_wiki else "topic",
        limit=args.limit,
        wiki_root=Path(args.wiki_root).expanduser(),
        workspace_root=Path(args.workspace_root).expanduser(),
        repository_root=REPO_ROOT,
        allow_network_fetch=network_allowed(args),
        no_citation_expand=args.no_citation_expand,
    )
    return emit("fetch", str(payload.get("status") or "inconclusive"), payload, ok=payload.get("status") == "completed")


def add_common(command: argparse.ArgumentParser) -> None:
    command.add_argument("topic", nargs="?", default="")
    command.add_argument("--wiki-root", default=str(default_wiki_root()))
    command.add_argument("--workspace-root", default=str(default_workspace_root()))
    command.add_argument("--limit", type=int, default=10)
    command.add_argument("--from-wiki", action="store_true")
    command.add_argument("--no-network-fetch", action="store_true")
    command.add_argument("--no-citation-expand", action="store_true")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name, func in (("prepare", cmd_prepare), ("plan", cmd_plan), ("fetch", cmd_fetch)):
        command = sub.add_parser(name)
        add_common(command)
        command.set_defaults(func=func)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
