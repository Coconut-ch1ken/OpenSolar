#!/usr/bin/env python3
"""Email draft/send helper with approval-gated delivery."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
from email.message import EmailMessage
import json
import smtplib
from typing import Any


def emit(command: str, status: str, payload: dict[str, Any], *, ok: bool = False) -> int:
    out = {"schema": "autosci_send_email_cli.v1", "command": command, "status": status, "ok": ok, **payload}
    print(json.dumps(out, indent=2, sort_keys=True))
    return 1 if status == "failed" else 0


def cmd_draft(args: argparse.Namespace) -> int:
    return emit("draft", "completed", {"to": args.to, "subject": args.subject, "body": args.body}, ok=True)


def write_runtime_evidence(
    args: argparse.Namespace,
    *,
    status: str,
    exit_code: int,
    checks: list[dict[str, Any]],
    runtime_fields: dict[str, Any],
    limitations: list[str],
) -> str:
    if not args.runtime_evidence_out:
        return ""
    from_addr = args.from_addr or args.smtp_user or "autosci@localhost"
    receipt_path = None
    artifacts: list[dict[str, str]] = []
    if status == "completed":
        receipt_path = args.runtime_evidence_out + ".receipt.json"
        with open(receipt_path, "w", encoding="utf-8") as handle:
            handle.write(
                json.dumps(
                    {
                        "schema": "autosci_email_delivery_receipt.v1",
                        "status": status,
                        "approval_ref": args.approval_ref,
                        "to": args.to,
                        "from": from_addr,
                        "subject": args.subject,
                        "provider": runtime_fields.get("provider", "smtp"),
                        "delivered": runtime_fields.get("delivered") is True,
                    },
                    indent=2,
                    sort_keys=True,
                )
                + "\n"
            )
        artifacts.append({"type": "email_delivery_receipt_json", "path": receipt_path})
    payload = {
        "schema": "autosci_runtime_evidence.v1",
        "task_id": "send-email-runtime",
        "sprint_id": "send-email",
        "node_id": "node-send-email",
        "status": status,
        "inputs": {"approval_ref": args.approval_ref, "to": args.to, "subject": args.subject},
        "outputs": {
            "runtime": {
                "action": "send_email",
                "status": status,
                "approval_ref": args.approval_ref,
                "command_run": f"smtp://{args.smtp_host}:{args.smtp_port} send {from_addr} -> {args.to}",
                "exit_code": exit_code,
                "evidence_ids": [f"email:{args.approval_ref}", f"recipient:{args.to}"],
                "checks": checks,
                **runtime_fields,
            }
        },
        "artifacts": artifacts,
        "provenance": {
            "operator_id": "autosci-send-email-cli",
            "implementation_package": "tools.send_email",
            "timestamp": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        },
        "limitations": limitations,
    }
    with open(args.runtime_evidence_out, "w", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return str(args.runtime_evidence_out)


def cmd_send(args: argparse.Namespace) -> int:
    if not args.approval_ref:
        return emit("send", "approval_required", {"to": args.to, "subject": args.subject, "limitations": ["Email delivery requires --approval-ref and configured SMTP/provider credentials."]})
    if not args.execute_approved:
        return emit("send", "inconclusive", {"approval_ref": args.approval_ref, "limitations": ["Email delivery requires --execute-approved before contacting SMTP/provider endpoints."]})
    if not args.smtp_host:
        runtime_path = write_runtime_evidence(
            args,
            status="inconclusive",
            exit_code=1,
            checks=[{"check": "smtp_configured", "status": "error", "detail": "Missing --smtp-host."}],
            runtime_fields={"delivered": False},
            limitations=["SMTP/provider delivery did not run because no SMTP host was configured."],
        )
        return emit("send", "inconclusive", {"approval_ref": args.approval_ref, "runtime_evidence_path": runtime_path, "limitations": ["SMTP/provider delivery is not configured."]})

    from_addr = args.from_addr or args.smtp_user or "autosci@localhost"
    message = EmailMessage()
    message["From"] = from_addr
    message["To"] = args.to
    message["Subject"] = args.subject
    message.set_content(args.body or "")
    try:
        with smtplib.SMTP(args.smtp_host, int(args.smtp_port), timeout=int(args.timeout_seconds)) as smtp:
            if args.tls:
                smtp.starttls()
            if args.smtp_user or args.smtp_password:
                smtp.login(args.smtp_user, args.smtp_password)
            refused = smtp.send_message(message)
    except Exception as exc:  # noqa: BLE001 - CLI must surface provider failures as evidence.
        runtime_path = write_runtime_evidence(
            args,
            status="failed",
            exit_code=1,
            checks=[
                {"check": "smtp_configured", "status": "ok", "detail": f"{args.smtp_host}:{args.smtp_port}"},
                {"check": "smtp_send", "status": "error", "detail": str(exc)[:500]},
            ],
            runtime_fields={"delivered": False, "provider": "smtp", "smtp_host": args.smtp_host, "smtp_port": int(args.smtp_port)},
            limitations=["SMTP/provider delivery failed; no successful delivery is claimed."],
        )
        return emit("send", "failed", {"approval_ref": args.approval_ref, "runtime_evidence_path": runtime_path, "error": str(exc)[:500]})

    delivered = not refused
    status = "completed" if delivered else "failed"
    runtime_path = write_runtime_evidence(
        args,
        status=status,
        exit_code=0 if delivered else 1,
        checks=[
            {"check": "smtp_configured", "status": "ok", "detail": f"{args.smtp_host}:{args.smtp_port}"},
            {"check": "smtp_send", "status": "ok" if delivered else "error", "detail": "accepted" if delivered else json.dumps(refused, sort_keys=True, default=str)},
        ],
        runtime_fields={
            "delivered": delivered,
            "provider": "smtp",
            "smtp_host": args.smtp_host,
            "smtp_port": int(args.smtp_port),
            "to": args.to,
            "from": from_addr,
            "subject": args.subject,
        },
        limitations=["Email was sent only because explicit approval and SMTP execution flags were supplied."],
    )
    return emit("send", status, {"approval_ref": args.approval_ref, "runtime_evidence_path": runtime_path, "delivered": delivered}, ok=delivered)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command")
    for name, func in (("draft", cmd_draft), ("send", cmd_send)):
        command = sub.add_parser(name)
        command.add_argument("--to", default="")
        command.add_argument("--from", dest="from_addr", default="")
        command.add_argument("--subject", default="")
        command.add_argument("--body", default="")
        command.add_argument("--approval-ref", default="")
        command.add_argument("--execute-approved", action="store_true")
        command.add_argument("--smtp-host", default="")
        command.add_argument("--smtp-port", type=int, default=25)
        command.add_argument("--smtp-user", default="")
        command.add_argument("--smtp-password", default="")
        command.add_argument("--tls", action="store_true")
        command.add_argument("--timeout-seconds", type=int, default=30)
        command.add_argument("--runtime-evidence-out", default="")
        command.set_defaults(func=func)
    parser.set_defaults(func=cmd_draft, command="draft")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
