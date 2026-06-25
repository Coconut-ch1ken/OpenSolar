#!/usr/bin/env python3
"""DeepXiv fetch helper for AutoSci-compatible source evidence.

The repository does not bundle a DeepXiv provider implementation.  This CLI
therefore only performs a live request when DEEPXIV_API_URL is configured and
otherwise emits explicit unavailable evidence.
"""

from __future__ import annotations

import argparse
import json
import os
import urllib.parse
import urllib.request
from typing import Any


def emit(command: str, status: str, payload: dict[str, Any], *, ok: bool = False) -> int:
    out = {"schema": "autosci_fetch_deepxiv_cli.v1", "command": command, "status": status, "ok": ok, **payload}
    print(json.dumps(out, indent=2, sort_keys=True))
    return 1 if status == "failed" else 0


def provider_url() -> str:
    return os.environ.get("DEEPXIV_API_URL", "").strip()


def network_allowed(args: argparse.Namespace) -> bool:
    if args.no_network_fetch:
        return False
    return os.environ.get("AUTOSCI_DISABLE_NETWORK_FETCH", "").lower() not in {"1", "true", "yes"}


def normalize_item(item: dict[str, Any]) -> dict[str, Any]:
    title = str(item.get("title") or item.get("name") or "").strip()
    if not title:
        return {}
    return {
        "candidate_id": str(item.get("id") or item.get("paper_id") or item.get("url") or title),
        "title": title,
        "abstract": str(item.get("abstract") or item.get("summary") or ""),
        "url": str(item.get("url") or item.get("source_ref") or ""),
        "source_channels": ["deepxiv"],
        "source_ref": str(item.get("url") or item.get("source_ref") or ""),
        "fetch_status": "fetched",
    }


def cmd_search(args: argparse.Namespace) -> int:
    if not network_allowed(args):
        return emit("search", "inconclusive", {"items": [], "limitations": ["Network fetch disabled; no DeepXiv request was made."]})
    base_url = provider_url()
    if not base_url:
        return emit(
            "search",
            "inconclusive",
            {"items": [], "limitations": ["DEEPXIV_API_URL is not configured; DeepXiv live evidence is unavailable."]},
        )
    query = urllib.parse.urlencode({"q": args.query, "limit": args.limit})
    separator = "&" if "?" in base_url else "?"
    url = f"{base_url}{separator}{query}"
    try:
        with urllib.request.urlopen(url, timeout=args.timeout) as response:  # noqa: S310
            payload = json.loads(response.read().decode("utf-8"))
    except Exception as exc:  # noqa: BLE001 - provider failures are explicit evidence.
        return emit("search", "inconclusive", {"items": [], "limitations": [f"DeepXiv request failed: {exc}"]})
    raw_items = payload.get("data") if isinstance(payload, dict) else payload
    if not isinstance(raw_items, list):
        return emit("search", "failed", {"items": [], "limitations": ["DeepXiv response must be a JSON list or object with data list."]})
    items = [item for item in (normalize_item(raw) for raw in raw_items if isinstance(raw, dict)) if item]
    return emit("search", "completed" if items else "inconclusive", {"items": items, "count": len(items), "limitations": []}, ok=bool(items))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    command = sub.add_parser("search")
    command.add_argument("query")
    command.add_argument("--limit", type=int, default=10)
    command.add_argument("--timeout", type=int, default=30)
    command.add_argument("--no-network-fetch", action="store_true")
    command.set_defaults(func=cmd_search)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
