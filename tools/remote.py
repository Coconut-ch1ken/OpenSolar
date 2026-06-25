#!/usr/bin/env python3
"""Approval-gated remote/local experiment helper for AutoSci parity routes."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
import json
import os
import shlex
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]


def emit(command: str, status: str, payload: dict[str, Any], *, ok: bool = False) -> int:
    out = {"schema": "autosci_remote_cli.v1", "command": command, "status": status, "ok": ok, **payload}
    print(json.dumps(out, indent=2, sort_keys=True))
    return 1 if status == "failed" else 0


def load_allowlists(paths: list[str]) -> list[dict[str, Any]]:
    payloads: list[dict[str, Any]] = []
    for raw in paths:
        if not raw:
            continue
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


def result_paths(run_dir: Path) -> list[Path]:
    names = ("results.json", "result.json", "metrics.json", "status.json", "run_log.json")
    return [run_dir / name for name in names if (run_dir / name).exists()]


def load_result_summary(paths: list[Path]) -> dict[str, Any]:
    summary: dict[str, Any] = {"metrics": [], "outcome": "", "logs": []}
    for path in paths:
        try:
            payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(payload, dict):
            continue
        result = payload.get("result") if isinstance(payload.get("result"), dict) else {}
        outcome = payload.get("outcome") or result.get("outcome") or payload.get("status")
        if outcome and not summary["outcome"]:
            summary["outcome"] = str(outcome)
        metrics = payload.get("metrics") if isinstance(payload.get("metrics"), list) else result.get("metrics")
        if isinstance(metrics, list):
            summary["metrics"].extend(item for item in metrics if isinstance(item, dict))
        logs = payload.get("logs") if isinstance(payload.get("logs"), list) else []
        summary["logs"].extend(str(item) for item in logs if str(item).strip())
    return summary


def write_runtime_evidence(
    *,
    args: argparse.Namespace,
    command_run: str,
    exit_code: int,
    status: str,
    checks: list[dict[str, Any]],
    artifacts: list[dict[str, str]],
    runtime_fields: dict[str, Any],
    limitations: list[str],
) -> Path | None:
    out = Path(args.runtime_evidence_out).expanduser() if args.runtime_evidence_out else None
    if out is None:
        return None
    out.parent.mkdir(parents=True, exist_ok=True)
    experiment = args.experiment or "experiment"
    payload = {
        "schema": "autosci_runtime_evidence.v1",
        "task_id": f"remote-launch-{experiment}",
        "sprint_id": "remote-launch",
        "node_id": f"node-remote-launch-{experiment}",
        "status": status,
        "inputs": {"approval_ref": args.approval_ref, "experiment": experiment},
        "outputs": {
            "runtime": {
                "action": "run_experiment",
                "status": status,
                "approval_ref": args.approval_ref,
                "command_run": command_run,
                "exit_code": exit_code,
                "evidence_ids": [f"remote-runtime:{experiment}"],
                "checks": checks,
                **runtime_fields,
            }
        },
        "artifacts": artifacts,
        "provenance": {
            "operator_id": "autosci-remote-cli",
            "implementation_package": "tools.remote",
            "timestamp": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        },
        "limitations": limitations,
    }
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out


def cmd_launch(args: argparse.Namespace) -> int:
    if not args.approval_ref:
        return emit("launch", "approval_required", {"limitations": ["Remote/local launch requires --approval-ref and external runtime configuration."]})
    if not args.execute_approved:
        return emit("launch", "inconclusive", {"approval_ref": args.approval_ref, "limitations": ["Launch executor requires --execute-approved before running an allowlisted command."]})
    if not args.command_run:
        return emit("launch", "inconclusive", {"approval_ref": args.approval_ref, "limitations": ["Launch executor requires --command."]})

    command = shlex.split(args.command_run)
    allowlists = load_allowlists(args.allowlist_evidence or [])
    allowed, allow_reason = command_allowlisted(command, allowlists)
    run_dir = Path(args.run_dir or ".").expanduser().resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    if not allowed:
        runtime_path = write_runtime_evidence(
            args=args,
            command_run=" ".join(command),
            exit_code=1,
            status="inconclusive",
            checks=[{"check": "command_allowlisted", "status": "error", "detail": allow_reason}],
            artifacts=[],
            runtime_fields={"result_collected": False, "run_dir": str(run_dir)},
            limitations=["Remote/local launch did not run because command allowlist validation failed."],
        )
        return emit(
            "launch",
            "inconclusive",
            {
                "approval_ref": args.approval_ref,
                "runtime_evidence_path": str(runtime_path) if runtime_path else "",
                "limitations": ["Remote/local launch did not run because command allowlist validation failed."],
            },
        )

    proc = subprocess.run(
        command,
        cwd=run_dir,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=int(args.timeout_seconds),
    )
    stdout_path = run_dir / "remote_stdout.txt"
    stderr_path = run_dir / "remote_stderr.txt"
    stdout_path.write_text(proc.stdout, encoding="utf-8")
    stderr_path.write_text(proc.stderr, encoding="utf-8")
    paths = result_paths(run_dir)
    summary = load_result_summary(paths)
    result_collected = bool(paths)
    metrics = summary["metrics"]
    outcome = summary["outcome"] or ("supports" if proc.returncode == 0 and result_collected else "inconclusive")
    runtime_status = "completed" if proc.returncode == 0 and result_collected else ("failed" if proc.returncode else "inconclusive")
    artifacts = [
        {"type": "remote_stdout", "path": str(stdout_path)},
        {"type": "remote_stderr", "path": str(stderr_path)},
        *[{"type": "remote_result", "path": str(path)} for path in paths],
    ]
    runtime_path = write_runtime_evidence(
        args=args,
        command_run=" ".join(command),
        exit_code=int(proc.returncode),
        status=runtime_status,
        checks=[
            {"check": "command_allowlisted", "status": "ok", "detail": allow_reason},
            {"check": "exit_code", "status": "ok" if proc.returncode == 0 else "error", "detail": f"exit_code={proc.returncode}"},
            {"check": "result_collected", "status": "ok" if result_collected else "error", "detail": ", ".join(str(path) for path in paths) if paths else "No result artifact found."},
        ],
        artifacts=artifacts,
        runtime_fields={
            "outcome": outcome,
            "result_collected": result_collected,
            "metrics": metrics,
            "logs": summary["logs"],
            "run_dir": str(run_dir),
            "result_paths": [str(path) for path in paths],
        },
        limitations=["Remote/local launch ran an explicitly approved and allowlisted command."],
    )
    return emit(
        "launch",
        runtime_status,
        {
            "approval_ref": args.approval_ref,
            "run_dir": str(run_dir),
            "exit_code": int(proc.returncode),
            "result_collected": result_collected,
            "runtime_evidence_path": str(runtime_path) if runtime_path else "",
            "artifacts": artifacts,
        },
        ok=runtime_status == "completed",
    )


def cmd_pull_results(args: argparse.Namespace) -> int:
    result_dir = Path(args.result_dir).expanduser() if args.result_dir else None
    if result_dir and result_dir.exists():
        files = [str(path) for path in sorted(result_dir.rglob("*")) if path.is_file()]
        return emit("pull-results", "completed", {"result_dir": str(result_dir.resolve()), "files": files, "count": len(files)}, ok=True)
    return emit("pull-results", "inconclusive", {"result_dir": str(result_dir) if result_dir else "", "limitations": ["No local result directory was available to collect."]})


def cmd_check(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir).expanduser() if args.run_dir else None
    candidates = []
    if run_dir:
        candidates.extend([run_dir / "status.json", run_dir / "run_log.json", run_dir / "results.json"])
    existing = [path for path in candidates if path.exists()]
    payload: dict[str, Any] = {"experiment": args.experiment, "checked_paths": [str(path) for path in candidates]}
    if existing:
        payload["evidence_paths"] = [str(path.resolve()) for path in existing]
        return emit("check", "completed", payload, ok=True)
    payload["limitations"] = ["No runtime status artifact was found; remote status remains inconclusive."]
    return emit("check", "inconclusive", payload)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    command = sub.add_parser("launch")
    command.add_argument("--approval-ref", default="")
    command.add_argument("--experiment", default="")
    command.add_argument("--allowlist-evidence", action="append", default=[])
    command.add_argument("--command", dest="command_run", default="")
    command.add_argument("--run-dir", default="")
    command.add_argument("--runtime-evidence-out", default="")
    command.add_argument("--timeout-seconds", type=int, default=120)
    command.add_argument("--execute-approved", action="store_true")
    command.set_defaults(func=cmd_launch)

    command = sub.add_parser("pull-results")
    command.add_argument("--result-dir", default="")
    command.set_defaults(func=cmd_pull_results)

    command = sub.add_parser("check")
    command.add_argument("--experiment", default="")
    command.add_argument("--run-dir", default=os.environ.get("AUTOSCI_RUN_DIR", ""))
    command.set_defaults(func=cmd_check)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
