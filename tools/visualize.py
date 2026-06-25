#!/usr/bin/env python3
"""AutoSci-compatible graph visualization artifact generator."""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]


def slug(value: str) -> str:
    out = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return out or "node"


def default_wiki_root() -> Path:
    raw = os.environ.get("AUTOSCI_WIKI_ROOT") or os.environ.get("WIKI_ROOT")
    if raw:
        return Path(raw).expanduser()
    harness_dir = Path(os.environ.get("HARNESS_DIR", REPO_ROOT / "harness"))
    return harness_dir / "artifacts" / "autosci" / "workspace" / "wiki"


def rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def read_edges(wiki_root: Path) -> list[dict[str, Any]]:
    edges_path = wiki_root / "graph" / "edges.jsonl"
    edges: list[dict[str, Any]] = []
    if not edges_path.exists():
        return edges
    for line_no, line in enumerate(edges_path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            edges.append({"source": f"invalid:{line_no}", "target": "graph-errors", "relation": "invalid_json", "operation": "warn"})
            continue
        if isinstance(payload, dict):
            edges.append(payload)
    return edges


def read_markdown_nodes(wiki_root: Path) -> list[dict[str, Any]]:
    nodes: list[dict[str, Any]] = []
    for path in sorted(wiki_root.rglob("*.md")) if wiki_root.exists() else []:
        if "/.obsidian/" in path.as_posix():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        title = path.stem
        for line in text.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
        node_id = rel(path, wiki_root)
        group = path.parent.name
        nodes.append({"id": node_id, "label": title, "group": group, "path": node_id})
    return nodes


def graph_data(wiki_root: Path) -> dict[str, Any]:
    nodes = read_markdown_nodes(wiki_root)
    node_ids = {node["id"] for node in nodes}
    edges = []
    for edge in read_edges(wiki_root):
        source = str(edge.get("source") or "").strip()
        target = str(edge.get("target") or "").strip()
        relation = str(edge.get("relation") or "related").strip()
        if not source or not target:
            continue
        for node_id in (source, target):
            if node_id not in node_ids:
                node_ids.add(node_id)
                nodes.append({"id": node_id, "label": node_id, "group": "graph", "path": ""})
        edges.append({
            "source": source,
            "target": target,
            "relation": relation,
            "operation": str(edge.get("operation") or "confirm"),
            "evidence_ids": [str(item) for item in edge.get("evidence_ids") or [] if str(item).strip()],
        })
    return {
        "schema": "autosci_web_graph.v1",
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "wiki_root": str(wiki_root.resolve()),
        "nodes": nodes,
        "edges": edges,
    }


def write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def cmd_obsidian(args: argparse.Namespace) -> int:
    wiki_root = Path(args.wiki_root).expanduser()
    path = Path(args.out).expanduser() if args.out else wiki_root / ".obsidian" / "graph.json"
    payload = {
        "schema": "autosci_obsidian_graph_config.v1",
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "collapse-filter": False,
        "search": "",
        "showTags": True,
        "showAttachments": True,
        "hideUnresolved": False,
        "showOrphans": True,
        "colorGroups": [
            {"query": "path:ideas", "color": {"a": 1, "rgb": 3381759}},
            {"query": "path:experiments", "color": {"a": 1, "rgb": 13369344}},
            {"query": "path:papers", "color": {"a": 1, "rgb": 26367}},
        ],
    }
    write_json(path, payload)
    print(json.dumps({"ok": True, "path": str(path), "schema": payload["schema"]}, sort_keys=True))
    return 0


def cmd_canvas(args: argparse.Namespace) -> int:
    wiki_root = Path(args.wiki_root).expanduser()
    data = graph_data(wiki_root)
    path = Path(args.out).expanduser() if args.out else wiki_root / "graph" / "autosci.canvas"
    nodes = []
    for index, node in enumerate(data["nodes"]):
        nodes.append({
            "id": node["id"],
            "type": "text",
            "text": node["label"],
            "x": (index % 6) * 260,
            "y": (index // 6) * 180,
            "width": 220,
            "height": 100,
        })
    canvas = {
        "nodes": nodes,
        "edges": [
            {
                "id": f"edge-{index}",
                "fromNode": edge["source"],
                "toNode": edge["target"],
                "label": edge["relation"],
            }
            for index, edge in enumerate(data["edges"], start=1)
        ],
    }
    write_json(path, canvas)
    graph_out = Path(args.graph_out).expanduser() if args.graph_out else REPO_ROOT / "app" / "data" / "graph.json"
    write_json(graph_out, data)
    print(json.dumps({"ok": True, "path": str(path), "graph_data": str(graph_out), "nodes": len(data["nodes"]), "edges": len(data["edges"])}, sort_keys=True))
    return 0


def cmd_graph_data(args: argparse.Namespace) -> int:
    wiki_root = Path(args.wiki_root).expanduser()
    data = graph_data(wiki_root)
    path = Path(args.out).expanduser()
    write_json(path, data)
    print(json.dumps({"ok": True, "path": str(path), "nodes": len(data["nodes"]), "edges": len(data["edges"])}, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name, func in (
        ("generate-obsidian-config", cmd_obsidian),
        ("generate-canvas", cmd_canvas),
        ("graph-data", cmd_graph_data),
    ):
        command = sub.add_parser(name)
        command.add_argument("--wiki-root", default=str(default_wiki_root()))
        command.add_argument("--out")
        if name == "generate-canvas":
            command.add_argument("--graph-out")
        command.set_defaults(func=func)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
