#!/usr/bin/env python3
"""AutoSci-compatible local web UI server for the Solar AutoSci workspace."""

from __future__ import annotations

import argparse
import functools
import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from visualize import default_wiki_root, graph_data, write_json


REPO_ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = REPO_ROOT / "app"


def prepare_graph(wiki_root: Path, app_root: Path = APP_ROOT) -> Path:
    graph_path = app_root / "data" / "graph.json"
    write_json(graph_path, graph_data(wiki_root))
    return graph_path


def cmd_health(args: argparse.Namespace) -> int:
    wiki_root = Path(args.wiki_root).expanduser()
    graph_path = prepare_graph(wiki_root)
    data = json.loads(graph_path.read_text(encoding="utf-8"))
    payload = {
        "ok": (APP_ROOT / "index.html").exists() and (APP_ROOT / "modules" / "graph.js").exists(),
        "app_root": str(APP_ROOT),
        "wiki_root": str(wiki_root.resolve()),
        "graph_path": str(graph_path),
        "node_count": len(data.get("nodes") or []),
        "edge_count": len(data.get("edges") or []),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["ok"] else 2


def cmd_serve(args: argparse.Namespace) -> int:
    wiki_root = Path(args.wiki_root).expanduser()
    prepare_graph(wiki_root)
    handler = functools.partial(SimpleHTTPRequestHandler, directory=str(APP_ROOT))
    server = ThreadingHTTPServer((args.host, args.port), handler)
    print(json.dumps({"ok": True, "url": f"http://{args.host}:{server.server_port}/", "wiki_root": str(wiki_root.resolve())}, sort_keys=True))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wiki-root", default=str(default_wiki_root()))
    parser.add_argument("--host", default=os.environ.get("HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8765")))
    parser.add_argument("--health-check", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.health_check:
        return cmd_health(args)
    return cmd_serve(args)


if __name__ == "__main__":
    raise SystemExit(main())
