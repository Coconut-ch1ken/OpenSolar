"""Every artifact that carries a repair generation must accept the configured budget.

The planner (SOLAR_PLANNER_MAX_REPAIRS) and the intent compiler
(SOLAR_INTENT_MAX_REPAIRS) both cap repairs at 4. A schema that still caps
``generation`` at 1 rejects a valid second repair after the pipeline already
spent the model calls to produce it.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
LIB = ROOT / "harness" / "lib"
if str(LIB) not in sys.path:
    sys.path.insert(0, str(LIB))

import intent_compiler  # noqa: E402

SCHEMAS = ROOT / "harness" / "schemas"
BUDGET_CAP = 4


def _prop(schema: dict, *path: str) -> dict:
    node = schema
    for key in path:
        node = node[key]
    return node


@pytest.mark.parametrize(
    ("relative", "path"),
    [
        ("planning/plan-ir.v2.schema.json", ("properties", "generation")),
        ("planning/planning-decision.v1.schema.json", ("properties", "generation")),
        ("planning/direct-response.v1.schema.json", ("properties", "generation")),
        ("planning/capsule-selection.v1.schema.json", ("properties", "generation")),
        ("planning/composition-selection.v1.schema.json", ("properties", "generation")),
        ("planning/plan-validation.v2.schema.json", ("properties", "plan_ir_ref", "properties", "generation")),
        ("planning/plan-validation.v2.schema.json", ("properties", "repair_count")),
        ("planning/plan-acceptance.v1.schema.json", ("properties", "repair", "properties", "maximum_attempts")),
        ("compiler/intent-ir.v3.schema.json", ("properties", "generation")),
        ("compiler/intent-validation.v1.schema.json", ("properties", "repair_count")),
        ("compiler/intent-validation.v1.schema.json", ("$defs", "intent_ref", "properties", "generation")),
        ("compiler/intent-fidelity.v1.schema.json", ("properties", "intent_ir_ref", "properties", "generation")),
        ("compiler/intent-acceptance.v1.schema.json", ("properties", "final_generation")),
        ("compiler/intent-acceptance.v1.schema.json", ("properties", "repair", "properties", "maximum_attempts")),
    ],
)
def test_generation_counters_accept_the_full_repair_budget(relative: str, path: tuple[str, ...]) -> None:
    schema = json.loads((SCHEMAS / relative).read_text(encoding="utf-8"))
    node = _prop(schema, *path)
    assert node.get("maximum") == BUDGET_CAP, (relative, path, node)
    assert "const" not in node, (relative, path, node)


def test_intent_repair_budget_follows_environment_and_stays_bounded(monkeypatch) -> None:
    monkeypatch.delenv("SOLAR_INTENT_MAX_REPAIRS", raising=False)
    assert intent_compiler._configured_intent_max_repairs() == 1
    monkeypatch.setenv("SOLAR_INTENT_MAX_REPAIRS", "3")
    assert intent_compiler._configured_intent_max_repairs() == 3
    monkeypatch.setenv("SOLAR_INTENT_MAX_REPAIRS", "9")
    assert intent_compiler._configured_intent_max_repairs() == BUDGET_CAP
    monkeypatch.setenv("SOLAR_INTENT_MAX_REPAIRS", "not-a-number")
    assert intent_compiler._configured_intent_max_repairs() == 1
    monkeypatch.setenv("SOLAR_INTENT_MAX_REPAIRS", "-2")
    assert intent_compiler._configured_intent_max_repairs() == 0
