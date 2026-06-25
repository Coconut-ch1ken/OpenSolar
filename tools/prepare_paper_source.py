#!/usr/bin/env python3
"""CLI wrapper for Solar AutoSci paper source preparation."""

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

from plugins.autosci.backends.paper_prepare import prepare_paper_source  # noqa: E402


def default_workspace_root() -> Path:
    return Path(os.environ.get("HARNESS_DIR", HARNESS)).expanduser()


def default_raw_root() -> Path:
    return default_workspace_root() / "artifacts" / "autosci" / "workspace" / "raw"


def print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def cmd_prepare(args: argparse.Namespace) -> int:
    workspace_root = Path(args.workspace_root).expanduser()
    raw_root = Path(args.raw_root).expanduser()
    allow_network_fetch = not args.no_network_fetch
    if os.environ.get("AUTOSCI_DISABLE_NETWORK_FETCH", "").lower() in {"1", "true", "yes"}:
        allow_network_fetch = False
    payload = prepare_paper_source(
        args.source,
        raw_root=raw_root,
        workspace_root=workspace_root,
        repository_root=Path(args.repository_root).expanduser() if args.repository_root else REPO_ROOT,
        title=args.title or "",
        arxiv_id=args.arxiv_id or "",
        allow_network_fetch=allow_network_fetch,
    )
    payload.update(
        {
            "schema": "autosci_prepare_paper_source_cli.v1",
            "ok": payload.get("status") == "completed",
            "allow_network_fetch": allow_network_fetch,
            "workspace_root": str(workspace_root.resolve()),
            "raw_root": str(raw_root.resolve()),
        }
    )
    print_json(payload)
    return 0 if payload.get("status") == "completed" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source")
    parser.add_argument("--raw-root", default=str(default_raw_root()))
    parser.add_argument("--workspace-root", default=str(default_workspace_root()))
    parser.add_argument("--repository-root", default=str(REPO_ROOT))
    parser.add_argument("--title", default="")
    parser.add_argument("--arxiv-id", default="")
    parser.add_argument("--no-network-fetch", action="store_true")
    parser.set_defaults(func=cmd_prepare)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return int(args.func(args))
    except Exception as exc:  # noqa: BLE001 - command-line evidence should be structured.
        print_json({"ok": False, "schema": "autosci_prepare_paper_source_cli.v1", "status": "failed", "error": str(exc)})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
