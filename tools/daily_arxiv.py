#!/usr/bin/env python3
"""Approval-gated daily arXiv helper."""

from __future__ import annotations

import argparse
import json
import os
from datetime import UTC, datetime
from typing import Any


def emit(command: str, status: str, payload: dict[str, Any], *, ok: bool = False) -> int:
    out = {"schema": "autosci_daily_arxiv_cli.v1", "command": command, "status": status, "ok": ok, **payload}
    print(json.dumps(out, indent=2, sort_keys=True))
    return 1 if status == "failed" else 0


def cmd_prepare(args: argparse.Namespace) -> int:
    return emit(
        "prepare",
        "completed",
        {
            "topic": args.topic,
            "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "requires_network": True,
            "limitations": ["Feed fetch and email delivery are not executed by prepare."],
        },
        ok=True,
    )


def cmd_finalize(args: argparse.Namespace) -> int:
    if not args.approval_ref:
        return emit("finalize", "approval_required", {"limitations": ["Finalize requires --approval-ref before feed delivery or auto-ingest side effects."]})
    return emit("finalize", "inconclusive", {"approval_ref": args.approval_ref, "limitations": ["No feed result manifest was supplied for finalization."]})


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    command = sub.add_parser("prepare")
    command.add_argument("--topic", default="")
    command.set_defaults(func=cmd_prepare)
    command = sub.add_parser("finalize")
    command.add_argument("--approval-ref", default="")
    command.set_defaults(func=cmd_finalize)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
