"""Autopilot dispatches against the sprints directory preflight resolved.

Deriving the sprints directory as ``HARNESS_DIR / "sprints"`` ignores an explicitly
configured sprints directory, so a run whose sprints live elsewhere is dispatched
against a directory that holds no graphs. The monitor, preflight, the scheduler and the
node dispatcher must all agree on one resolved directory.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest


HARNESS = Path(__file__).resolve().parents[3] / "harness"
MONITOR = HARNESS / "tools" / "solar-autopilot-monitor.py"

PATH_PROBE = textwrap.dedent(
    """
    import importlib.util
    import json
    import os
    import sys

    spec = importlib.util.spec_from_file_location("issue9_path_probe", sys.argv[1])
    assert spec and spec.loader
    monitor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(monitor)

    import graph_node_dispatcher
    import graph_scheduler
    import run_preflight

    print(json.dumps({
        "monitor": str(monitor.SPRINTS),
        "preflight": str(run_preflight.sprints_dir()),
        "scheduler": str(graph_scheduler.SPRINTS_DIR),
        "dispatcher": str(graph_node_dispatcher.SPRINTS_DIR),
        "env_sprints": os.environ.get("SPRINTS_DIR", ""),
        "env_harness_sprints": os.environ.get("HARNESS_SPRINTS_DIR", ""),
    }, sort_keys=True))
    """
)

SPRINT_ENV_KEYS = (
    "SPRINTS_DIR",
    "HARNESS_SPRINTS_DIR",
    "SOLAR_HARNESS_SPRINTS_DIR",
    "HARNESS_DIR",
    "SOLAR_HARNESS_DIR",
)


def _subprocess_env(tmp_path: Path, **overrides: str) -> dict[str, str]:
    env = os.environ.copy()
    for key in SPRINT_ENV_KEYS:
        env.pop(key, None)
    home = tmp_path / "home"
    home.mkdir(parents=True, exist_ok=True)
    env.update(
        {
            "HOME": str(home),
            "REAL_HARNESS_DIR": str(HARNESS),
            "PYTHONDONTWRITEBYTECODE": "1",
            "SOLAR_GATE_LEDGER": "0",
            "SOLAR_GRAPH_BUILDER_OPERATOR_POOL": "0",
            "SOLAR_GRAPH_DISPATCH_RESTRICT_SESSION": "1",
            "SOLAR_HARNESS_SESSION": "issue9-no-live-workers",
            "SOLAR_PLAN_VALIDATOR": "1",
            "SOLAR_PRODUCT_MODE": "0",
        }
    )
    env.update(overrides)
    return env


def _run_json(script: str, env: dict[str, str], *args: str) -> dict:
    completed = subprocess.run(
        [sys.executable, "-c", script, str(MONITOR), *args],
        check=False,
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )
    assert completed.returncode == 0, completed.stderr
    return json.loads(completed.stdout)


@pytest.mark.parametrize(
    ("configured", "expected_key"),
    [
        ({"HARNESS_DIR": "runtime-harness"}, "runtime-harness/sprints"),
        (
            {
                "HARNESS_DIR": "runtime-harness",
                "HARNESS_SPRINTS_DIR": "configured-sprints",
            },
            "configured-sprints",
        ),
        (
            {
                "HARNESS_DIR": "runtime-harness",
                "HARNESS_SPRINTS_DIR": "configured-sprints",
                "SPRINTS_DIR": "legacy-sprints",
            },
            "legacy-sprints",
        ),
        ({"SOLAR_HARNESS_DIR": "solar-harness"}, "solar-harness/sprints"),
    ],
)
def test_autopilot_uses_runtime_sprint_directory_precedence(
    tmp_path: Path,
    configured: dict[str, str],
    expected_key: str,
) -> None:
    resolved = {key: str(tmp_path / value) for key, value in configured.items()}
    result = _run_json(PATH_PROBE, _subprocess_env(tmp_path, **resolved))
    expected = str(tmp_path / expected_key)

    assert result == {
        "monitor": expected,
        "preflight": expected,
        "scheduler": expected,
        "dispatcher": expected,
        "env_sprints": expected,
        "env_harness_sprints": expected,
    }


def test_intake_only_alias_does_not_override_runtime_sprints(tmp_path: Path) -> None:
    runtime_harness = tmp_path / "runtime-harness"
    result = _run_json(
        PATH_PROBE,
        _subprocess_env(
            tmp_path,
            HARNESS_DIR=str(runtime_harness),
            SOLAR_HARNESS_SPRINTS_DIR=str(tmp_path / "intake-sprints"),
        ),
    )
    expected = str(runtime_harness / "sprints")
    assert {result[key] for key in ("monitor", "preflight", "scheduler", "dispatcher")} == {
        expected
    }


