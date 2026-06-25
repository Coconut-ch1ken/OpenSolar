#!/usr/bin/env python3
"""CLI wrapper for Solar AutoSci literature discovery."""

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

from plugins.autosci.backends.literature_discover import discover_literature  # noqa: E402


def default_workspace_root() -> Path:
    return Path(os.environ.get("HARNESS_DIR", HARNESS)).expanduser()


def default_wiki_root() -> Path:
    raw = os.environ.get("AUTOSCI_WIKI_ROOT") or os.environ.get("WIKI_ROOT")
    if raw:
        return Path(raw).expanduser()
    return default_workspace_root() / "artifacts" / "autosci" / "workspace" / "wiki"


def allow_network(args: argparse.Namespace) -> bool:
    enabled = not args.no_network_fetch
    if os.environ.get("AUTOSCI_DISABLE_NETWORK_FETCH", "").lower() in {"1", "true", "yes"}:
        enabled = False
    return enabled


def emit(payload: dict[str, Any]) -> int:
    payload = dict(payload)
    payload.update({"schema": "autosci_discover_cli.v1", "ok": payload.get("status") == "completed"})
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 1 if payload.get("status") == "failed" else 0


def run_discovery(args: argparse.Namespace, *, mode: str, query: str = "", anchors: list[str] | None = None) -> int:
    payload = discover_literature(
        query=query,
        mode=mode,
        anchors=anchors or [],
        negative_ids=args.negative_id,
        venue=args.venue,
        year=args.year,
        limit=args.limit,
        wiki_root=Path(args.wiki_root).expanduser(),
        workspace_root=Path(args.workspace_root).expanduser(),
        repository_root=Path(args.repository_root).expanduser(),
        allow_network_fetch=allow_network(args),
        no_citation_expand=args.no_citation_expand,
        fixture_fallback=False,
    )
    payload["allow_network_fetch"] = allow_network(args)
    return emit(payload)


def cmd_from_topic(args: argparse.Namespace) -> int:
    return run_discovery(args, mode="topic", query=args.topic)


def cmd_from_anchors(args: argparse.Namespace) -> int:
    return run_discovery(args, mode="anchors", query=args.query or " ".join(args.anchor), anchors=args.anchor)


def cmd_from_wiki(args: argparse.Namespace) -> int:
    return run_discovery(args, mode="wiki", query=args.query)


def cmd_from_venue(args: argparse.Namespace) -> int:
    return run_discovery(args, mode="venue", query=args.query or f"{args.venue} {args.year or ''}".strip())


def add_common(command: argparse.ArgumentParser) -> None:
    command.add_argument("--limit", type=int, default=10)
    command.add_argument("--wiki-root", default=str(default_wiki_root()))
    command.add_argument("--workspace-root", default=str(default_workspace_root()))
    command.add_argument("--repository-root", default=str(REPO_ROOT))
    command.add_argument("--negative-id", action="append", default=[])
    command.add_argument("--no-citation-expand", action="store_true")
    command.add_argument("--no-network-fetch", action="store_true")
    command.add_argument("--venue", default="")
    command.add_argument("--year", type=int)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    command = sub.add_parser("from-topic")
    command.add_argument("topic")
    add_common(command)
    command.set_defaults(func=cmd_from_topic)

    command = sub.add_parser("from-anchors")
    command.add_argument("anchor", nargs="+")
    command.add_argument("--query", default="")
    add_common(command)
    command.set_defaults(func=cmd_from_anchors)

    command = sub.add_parser("from-wiki")
    command.add_argument("--query", default="")
    add_common(command)
    command.set_defaults(func=cmd_from_wiki)

    command = sub.add_parser("from-venue")
    command.add_argument("venue_arg", nargs="?")
    command.add_argument("year_arg", nargs="?")
    add_common(command)
    command.set_defaults(func=cmd_from_venue)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if getattr(args, "venue_arg", None) and not args.venue:
        args.venue = args.venue_arg
    if getattr(args, "year_arg", None) and not args.year:
        args.year = int(args.year_arg)
    try:
        return int(args.func(args))
    except Exception as exc:  # noqa: BLE001 - command-line evidence should be structured.
        print(json.dumps({"ok": False, "schema": "autosci_discover_cli.v1", "status": "failed", "error": str(exc)}, indent=2, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
