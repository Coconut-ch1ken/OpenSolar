#!/usr/bin/env python3
"""LaTeX/PDF diagnostics and optional rasterization helper."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


def emit(command: str, status: str, payload: dict[str, Any], *, ok: bool = False) -> int:
    out = {"schema": "autosci_rasterize_latex_cli.v1", "command": command, "status": status, "ok": ok, **payload}
    print(json.dumps(out, indent=2, sort_keys=True))
    return 1 if status == "failed" else 0


def cmd_diagnose(args: argparse.Namespace) -> int:
    tools = {name: shutil.which(name) for name in ("latexmk", "pdflatex", "pdftoppm", "gs")}
    return emit("diagnose", "completed", {"tools": tools}, ok=True)


def cmd_check_pdf(args: argparse.Namespace) -> int:
    pdf = Path(args.pdf).expanduser()
    if not pdf.exists():
        return emit("check-pdf", "failed", {"pdf": str(pdf), "limitations": ["PDF file does not exist."]})
    return emit("check-pdf", "completed", {"pdf": str(pdf.resolve()), "bytes": pdf.stat().st_size}, ok=True)


def cmd_rasterize(args: argparse.Namespace) -> int:
    pdf = Path(args.pdf).expanduser()
    out_dir = Path(args.out_dir).expanduser()
    pdftoppm = shutil.which("pdftoppm")
    if not pdf.exists():
        return emit("rasterize", "failed", {"pdf": str(pdf), "limitations": ["PDF file does not exist."]})
    if not pdftoppm:
        return emit("rasterize", "inconclusive", {"pdf": str(pdf.resolve()), "limitations": ["pdftoppm is unavailable."]})
    out_dir.mkdir(parents=True, exist_ok=True)
    prefix = out_dir / pdf.stem
    proc = subprocess.run([pdftoppm, "-png", str(pdf), str(prefix)], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if proc.returncode != 0:
        return emit("rasterize", "failed", {"stderr": proc.stderr, "stdout": proc.stdout})
    files = [str(path.resolve()) for path in sorted(out_dir.glob(f"{pdf.stem}-*.png"))]
    return emit("rasterize", "completed", {"files": files, "count": len(files)}, ok=bool(files))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command")
    command = sub.add_parser("diagnose")
    command.set_defaults(func=cmd_diagnose)
    command = sub.add_parser("check-pdf")
    command.add_argument("pdf")
    command.set_defaults(func=cmd_check_pdf)
    command = sub.add_parser("rasterize")
    command.add_argument("pdf")
    command.add_argument("--out-dir", default="artifacts/autosci/workspace/paper/rasterized")
    command.set_defaults(func=cmd_rasterize)
    parser.set_defaults(func=cmd_diagnose, command="diagnose")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
