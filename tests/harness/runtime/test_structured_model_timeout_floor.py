"""An unconstrained-generation transport gets enough time to finish the document.

A native constrained decode returns in tens of seconds because the provider enforces the
schema while emitting. A prompt_json transport must generate the whole document first and
is validated locally afterwards, which takes minutes for a large IR. Holding both to the
same ceiling times out every prompt_json stage on a large request, and the failure looks
like a transport fault rather than a budget that was never adequate.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "harness" / "lib"))

from structured_model import PROMPT_JSON_MIN_TIMEOUT_SEC, StructuredJsonModel  # noqa: E402


def _model(schema_mode: str, timeout_seconds: int) -> StructuredJsonModel:
    return StructuredJsonModel(
        model="test-model",
        provider="anthropic",
        transport="claude_cli",
        schema_mode=schema_mode,
        timeout_seconds=timeout_seconds,
    )


def test_prompt_json_is_raised_to_the_floor():
    assert _model("prompt_json", 240).timeout_seconds == PROMPT_JSON_MIN_TIMEOUT_SEC


def test_native_keeps_its_configured_budget():
    # A constrained decode does not need the larger budget and must not silently inherit it.
    model = StructuredJsonModel(
        model="test-model",
        provider="openai",
        transport="codex_cli",
        schema_mode="native",
        timeout_seconds=240,
    )
    assert model.timeout_seconds == 240


def test_an_explicit_larger_budget_is_preserved():
    generous = PROMPT_JSON_MIN_TIMEOUT_SEC + 600
    assert _model("prompt_json", generous).timeout_seconds == generous


def test_the_floor_covers_every_non_native_mode():
    # json_object is likewise unconstrained at the wire level for our adapters.
    assert _model("json_object", 60).timeout_seconds == PROMPT_JSON_MIN_TIMEOUT_SEC
