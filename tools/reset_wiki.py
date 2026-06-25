#!/usr/bin/env python3
"""Approval-gated wiki reset helper."""

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


def emit(status: str, payload: dict[str, Any], *, ok: bool = False) -> int:
    out = {"schema": "autosci_reset_wiki_cli.v1", "status": status, "ok": ok, **payload}
    print(json.dumps(out, indent=2, sort_keys=True))
    return 1 if status == "failed" else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wiki-root", default=str(default_wiki_root()))
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--approval-ref", default="")
    args = parser.parse_args()
    root = Path(args.wiki_root).expanduser()
    pages = [str(path) for path in sorted(root.rglob("*")) if path.is_file()] if root.exists() else []
    if not args.apply:
        return emit("dry_run", {"wiki_root": str(root.resolve()), "file_count": len(pages), "would_remove": pages[:200]}, ok=True)
    if not args.approval_ref:
        return emit("approval_required", {"wiki_root": str(root.resolve()), "file_count": len(pages), "limitations": ["Destructive reset requires --approval-ref."]})
    return emit("inconclusive", {"approval_ref": args.approval_ref, "limitations": ["Destructive reset execution is intentionally not implemented in this local parity harness."]})


if __name__ == "__main__":
    raise SystemExit(main())
