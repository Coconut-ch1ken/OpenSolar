#!/usr/bin/env python3
"""Poster build/validate/render helper for AutoSci routes."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
import html
import json
import shlex
import subprocess
from pathlib import Path
from typing import Any


def emit(command: str, status: str, payload: dict[str, Any], *, ok: bool = False) -> int:
    out = {"schema": "autosci_poster_cli.v1", "command": command, "status": status, "ok": ok, **payload}
    print(json.dumps(out, indent=2, sort_keys=True))
    return 1 if status == "failed" else 0


def cmd_build(args: argparse.Namespace) -> int:
    out = Path(args.out).expanduser()
    title = args.title or "AutoSci Poster"
    body = f"<!doctype html><html><head><meta charset=\"utf-8\"><title>{html.escape(title)}</title></head><body><h1>{html.escape(title)}</h1><p>{html.escape(args.summary or 'Poster scaffold generated from local evidence.')}</p></body></html>\n"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(body, encoding="utf-8")
    return emit("build", "completed", {"path": str(out.resolve()), "title": title}, ok=True)


def cmd_validate(args: argparse.Namespace) -> int:
    path = Path(args.path).expanduser()
    if not path.exists():
        return emit("validate", "failed", {"path": str(path), "limitations": ["Poster HTML does not exist."]})
    text = path.read_text(encoding="utf-8", errors="replace")
    missing = [token for token in ("<html", "<body", "</html>") if token not in text.lower()]
    if missing:
        return emit("validate", "failed", {"path": str(path.resolve()), "missing": missing})
    return emit("validate", "completed", {"path": str(path.resolve()), "bytes": path.stat().st_size}, ok=True)


def load_allowlists(paths: list[str]) -> list[dict[str, Any]]:
    payloads: list[dict[str, Any]] = []
    for raw in paths:
        path = Path(raw).expanduser()
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            payload = {"commands": [line.strip() for line in text.splitlines() if line.strip()]}
        if isinstance(payload, dict):
            payloads.append(payload)
    return payloads


def command_from_template(raw: Any, values: dict[str, str]) -> list[str]:
    if isinstance(raw, list):
        parts = [str(item) for item in raw if str(item).strip()]
    elif isinstance(raw, str):
        parts = shlex.split(raw)
    else:
        return []
    return [part.format(**values) for part in parts]


def command_allowlisted(command: list[str], allowlists: list[dict[str, Any]]) -> tuple[bool, str]:
    if not command:
        return False, "empty command"
    command_text = " ".join(command)
    executable = Path(command[0]).name
    for payload in allowlists:
        executables = [str(item) for item in payload.get("executables", []) if str(item).strip()]
        if command[0] in executables or executable in executables:
            return True, f"executable allowlisted: {executable}"
        for key in ("commands", "allowed_commands"):
            values = [str(item) for item in payload.get(key, []) if str(item).strip()]
            if command_text in values:
                return True, f"command allowlisted by {key}"
        prefixes = [str(item) for item in payload.get("allowed_prefixes", []) if str(item).strip()]
        if any(command_text.startswith(prefix) for prefix in prefixes):
            return True, "command allowlisted by prefix"
    return False, f"command is not allowlisted: {command_text}"


def resolve_render_command(args: argparse.Namespace, values: dict[str, str], allowlists: list[dict[str, Any]]) -> tuple[list[str], str]:
    if args.render_command:
        return command_from_template(args.render_command, values), "--render-command"
    for payload in allowlists:
        command = command_from_template(payload.get("poster_render_command"), values)
        if command:
            return command, "poster_render_command allowlisted"
        renderer = str(payload.get("poster_renderer") or "").strip()
        if renderer:
            return [renderer, values["html"], values["png"], values["validation"]], "poster_renderer allowlisted"
    return [], "No render command was supplied."


def write_runtime_evidence(
    args: argparse.Namespace,
    *,
    status: str,
    command_run: str,
    exit_code: int,
    checks: list[dict[str, Any]],
    runtime_fields: dict[str, Any],
    artifacts: list[dict[str, str]],
    limitations: list[str],
) -> str:
    if not args.runtime_evidence_out:
        return ""
    payload = {
        "schema": "autosci_runtime_evidence.v1",
        "task_id": "poster-render-runtime",
        "sprint_id": "poster-render",
        "node_id": "node-poster-render",
        "status": status,
        "inputs": {"approval_ref": args.approval_ref, "poster_html": args.path},
        "outputs": {
            "runtime": {
                "action": "build_poster",
                "status": status,
                "approval_ref": args.approval_ref,
                "command_run": command_run,
                "exit_code": exit_code,
                "evidence_ids": [f"poster-render:{Path(args.path or 'poster').stem}"],
                "checks": checks,
                **runtime_fields,
            }
        },
        "artifacts": artifacts,
        "provenance": {
            "operator_id": "autosci-poster-cli",
            "implementation_package": "tools.poster",
            "timestamp": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        },
        "limitations": limitations,
    }
    out = Path(args.runtime_evidence_out).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return str(out)


def cmd_render(args: argparse.Namespace) -> int:
    if not args.approval_ref:
        return emit("render", "approval_required", {"limitations": ["Browser/PNG rendering requires --approval-ref and a configured renderer."]})
    if not args.execute_approved:
        return emit("render", "inconclusive", {"approval_ref": args.approval_ref, "limitations": ["Browser/PNG rendering requires --execute-approved before running a renderer."]})
    html_path = Path(args.path or "").expanduser()
    if not html_path.exists():
        return emit("render", "failed", {"approval_ref": args.approval_ref, "limitations": ["Poster HTML does not exist."]})
    png_path = Path(args.png_out or html_path.with_suffix(".png")).expanduser()
    validation_path = Path(args.validation_out or (str(png_path) + ".validation.json")).expanduser()
    png_path.parent.mkdir(parents=True, exist_ok=True)
    validation_path.parent.mkdir(parents=True, exist_ok=True)
    values = {"html": str(html_path.resolve()), "png": str(png_path.resolve()), "validation": str(validation_path.resolve())}
    allowlists = load_allowlists(args.allowlist_evidence or [])
    command, source = resolve_render_command(args, values, allowlists)
    allowed, allow_reason = command_allowlisted(command, allowlists)
    if not command or not allowed:
        runtime_path = write_runtime_evidence(
            args,
            status="inconclusive",
            command_run=" ".join(command) if command else "blocked:render-command-missing",
            exit_code=1,
            checks=[{"check": "poster_render_command", "status": "error", "detail": allow_reason if command else source}],
            runtime_fields={"browser_rendered": False, "png_exported": False, "overflow_probe": "not_run"},
            artifacts=[],
            limitations=["Poster render executor did not run because no render command was allowlisted."],
        )
        return emit("render", "inconclusive", {"approval_ref": args.approval_ref, "runtime_evidence_path": runtime_path, "limitations": ["Renderer command is not allowlisted."]})

    proc = subprocess.run(
        command,
        cwd=png_path.parent,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=int(args.timeout_seconds),
    )
    stdout_path = png_path.with_suffix(".stdout.txt")
    stderr_path = png_path.with_suffix(".stderr.txt")
    stdout_path.write_text(proc.stdout, encoding="utf-8")
    stderr_path.write_text(proc.stderr, encoding="utf-8")
    validation: dict[str, Any] = {}
    if validation_path.exists():
        try:
            loaded = json.loads(validation_path.read_text(encoding="utf-8", errors="replace"))
            validation = loaded if isinstance(loaded, dict) else {}
        except json.JSONDecodeError:
            validation = {}
    browser_rendered = bool(validation.get("browser_rendered", png_path.exists()))
    png_exported = bool(validation.get("png_exported", png_path.exists())) and png_path.exists()
    overflow_probe = str(validation.get("overflow_probe") or "not_run")
    overflow_ok = overflow_probe.strip().lower() in {"ok", "pass", "passed", "none", "no_overflow"}
    runtime_ok = proc.returncode == 0 and browser_rendered and png_exported and overflow_ok
    artifacts = [
        {"type": "poster_render_stdout", "path": str(stdout_path)},
        {"type": "poster_render_stderr", "path": str(stderr_path)},
    ]
    if png_path.exists():
        artifacts.append({"type": "poster_png", "path": str(png_path)})
    if validation_path.exists():
        artifacts.append({"type": "poster_render_validation_json", "path": str(validation_path)})
    runtime_path = write_runtime_evidence(
        args,
        status="completed" if runtime_ok else "failed",
        command_run=" ".join(command),
        exit_code=int(proc.returncode),
        checks=[
            {"check": "poster_render_command", "status": "ok", "detail": f"{source}; {allow_reason}"},
            {"check": "exit_code", "status": "ok" if proc.returncode == 0 else "error", "detail": f"exit_code={proc.returncode}"},
            {"check": "browser_rendered", "status": "ok" if browser_rendered else "error", "detail": str(browser_rendered)},
            {"check": "overflow_probe", "status": "ok" if overflow_ok else "error", "detail": overflow_probe},
            {"check": "png_exported", "status": "ok" if png_exported else "error", "detail": str(png_path) if png_path.exists() else "PNG was not found."},
        ],
        runtime_fields={
            "browser_rendered": browser_rendered,
            "png_exported": png_exported,
            "overflow_probe": overflow_probe,
            "png_path": str(png_path) if png_path.exists() else "",
        },
        artifacts=artifacts,
        limitations=["Poster render/export ran only because explicit approval and an allowlisted renderer were supplied."],
    )
    return emit(
        "render",
        "completed" if runtime_ok else "failed",
        {"approval_ref": args.approval_ref, "runtime_evidence_path": runtime_path, "png_path": str(png_path) if png_path.exists() else ""},
        ok=runtime_ok,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    command = sub.add_parser("build")
    command.add_argument("--out", default="artifacts/autosci/workspace/poster/poster.html")
    command.add_argument("--title", default="")
    command.add_argument("--summary", default="")
    command.set_defaults(func=cmd_build)
    command = sub.add_parser("validate")
    command.add_argument("path")
    command.set_defaults(func=cmd_validate)
    command = sub.add_parser("render")
    command.add_argument("path", nargs="?")
    command.add_argument("--approval-ref", default="")
    command.add_argument("--allowlist-evidence", action="append", default=[])
    command.add_argument("--render-command", default="")
    command.add_argument("--png-out", default="")
    command.add_argument("--validation-out", default="")
    command.add_argument("--runtime-evidence-out", default="")
    command.add_argument("--timeout-seconds", type=int, default=120)
    command.add_argument("--execute-approved", action="store_true")
    command.set_defaults(func=cmd_render)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
