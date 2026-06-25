from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[4]


def run_tool(tool: str, *args: str, extra_env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [sys.executable, str(REPO / "tools" / tool), *args],
        cwd=REPO,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def payload(proc: subprocess.CompletedProcess[str]) -> dict:
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return json.loads(proc.stdout)


def test_prepare_paper_source_cli_prepares_local_markdown(tmp_path: Path) -> None:
    paper = tmp_path / "SkillGen.md"
    paper.write_text("# SkillGen\n\n## Abstract\n\nGenerated skill agents.\n", encoding="utf-8")
    result = payload(
        run_tool(
            "prepare_paper_source.py",
            str(paper),
            "--workspace-root",
            str(tmp_path),
            "--raw-root",
            str(tmp_path / "raw"),
            "--no-network-fetch",
        )
    )
    assert result["schema"] == "autosci_prepare_paper_source_cli.v1"
    assert result["ok"] is True
    assert result["status"] == "completed"
    assert result["canonical_ingest_path"].endswith("SkillGen.md")


def test_discover_cli_reports_inconclusive_when_network_disabled(tmp_path: Path) -> None:
    wiki = tmp_path / "wiki"
    (wiki / "papers").mkdir(parents=True)
    (wiki / "papers/skillgen.md").write_text(
        "# SkillGen\n\narXiv: 2601.00001\n\nGenerated skill agents.\n",
        encoding="utf-8",
    )
    result = payload(
        run_tool(
            "discover.py",
            "from-wiki",
            "--wiki-root",
            str(wiki),
            "--workspace-root",
            str(tmp_path),
            "--no-network-fetch",
        )
    )
    assert result["schema"] == "autosci_discover_cli.v1"
    assert result["ok"] is False
    assert result["status"] == "inconclusive"
    assert result["anchors"] == ["2601.00001"]
    assert result["candidates"] == []
    assert "Network discovery disabled" in result["limitations"][0]


def test_source_fetch_helpers_do_not_synthesize_when_network_disabled() -> None:
    s2 = payload(run_tool("fetch_s2.py", "search", "skill generation", "--no-network-fetch"))
    assert s2["schema"] == "autosci_fetch_s2_cli.v1"
    assert s2["status"] == "inconclusive"
    assert s2["items"] == []

    deepxiv = payload(run_tool("fetch_deepxiv.py", "search", "skill generation", "--no-network-fetch"))
    assert deepxiv["schema"] == "autosci_fetch_deepxiv_cli.v1"
    assert deepxiv["status"] == "inconclusive"
    assert deepxiv["items"] == []

    paper_copilot = payload(run_tool("fetch_paper_copilot.py", "venue", "iclr", "2026", "--no-network-fetch"))
    assert paper_copilot["schema"] == "autosci_fetch_paper_copilot_cli.v1"
    assert paper_copilot["status"] == "inconclusive"
    assert paper_copilot["items"] == []


def test_paper_copilot_cli_reads_file_provider_evidence(tmp_path: Path) -> None:
    provider = tmp_path / "iclr2026.json"
    provider.write_text(
        json.dumps(
            [
                {
                    "id": "paper-copilot-001",
                    "title": "SkillGen Agents with Verified Tool Use",
                    "abstract": "A provider-backed paper list entry.",
                    "url": "https://example.org/skillgen",
                }
            ]
        ),
        encoding="utf-8",
    )
    result = payload(
        run_tool(
            "fetch_paper_copilot.py",
            "venue",
            "iclr",
            "2026",
            "--url",
            provider.as_uri(),
            "--limit",
            "5",
            "--no-network-fetch",
        )
    )
    assert result["schema"] == "autosci_fetch_paper_copilot_cli.v1"
    assert result["status"] == "completed"
    assert result["ok"] is True
    assert result["provider_status"]["provider"] == "paper_copilot"
    assert result["items"][0]["provider"] == "paper_copilot"
    assert result["items"][0]["title"] == "SkillGen Agents with Verified Tool Use"
