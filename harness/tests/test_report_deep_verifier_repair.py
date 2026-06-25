from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from report_validation import run_chapter_repair_loop, run_chapter_verifier  # noqa: E402


def _pack() -> dict:
    return {
        "chapter_id": "ch_01",
        "chapter": {"priority": "P1", "deep_writer_required": True},
        "must_use_evidence_ids": ["V001"],
        "core_evidence": [{"video_ref": "V001", "evidence_id": "V001"}],
        "counter_evidence": [{"id": "ce1"}],
    }


def _deep_proof(tmp_path: Path) -> dict:
    request_dir = tmp_path / "deep-request"
    request_dir.mkdir()
    (request_dir / "deep-research-state.json").write_text('{"ok": true}\n', encoding="utf-8")
    (request_dir / "report-operator-request.json").write_text(
        '{"operator_kind":"deep_writer","model_mode":"pro","reasoning_effort":"deep_research","tool_mode":"deep_research"}\n',
        encoding="utf-8",
    )
    return {"request_dir": str(request_dir)}


def test_p1_chapter_cannot_pass_with_ordinary_chatgpt_proof(tmp_path: Path) -> None:
    request_dir = tmp_path / "ordinary-chatgpt"
    request_dir.mkdir()
    (request_dir / "chatgpt-mode-state.json").write_text('{"ok": true}\n', encoding="utf-8")
    markdown = (
        "## 运行时变化\n\n"
        "判断：V001 显示开发者工具链正在向可执行 agent workflow 迁移。"
        "这意味着团队下一步应优先观察权限、调度和失败恢复。"
    )

    result = run_chapter_verifier({"chapter_id": "ch_01", "priority": "P1"}, markdown, _pack(), {"request_dir": str(request_dir)})

    assert result["status"] == "failed"
    assert "deep_proof_present_if_required" in result["repair_reasons"]
    assert result["deep_proof"]["ok"] is False


def test_verifier_repair_loop_removes_unsupported_claim(tmp_path: Path) -> None:
    markdown = (
        "## 运行时变化\n\n"
        "判断：V001 显示开发者工具链正在向可执行 agent workflow 迁移，并暴露出调度、权限和失败恢复的新要求。"
        "这意味着团队下一步应优先观察权限、调度和失败恢复。"
        "这个方向已经彻底改变所有企业软件市场，并证明所有团队都会立刻迁移。"
    )

    result = run_chapter_repair_loop(
        {"chapter_id": "ch_01", "priority": "P1"},
        markdown,
        _pack(),
        _deep_proof(tmp_path),
        max_attempts=3,
    )

    assert result["publish_decision"] == "publish"
    assert result["final_verification"]["status"] == "passed"
    assert result["attempt_count"] >= 1
    assert "彻底改变所有企业软件市场" not in result["markdown"]
