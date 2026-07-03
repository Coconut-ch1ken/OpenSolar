# AutoSci Solar Phase 20 Progress Log

Phase20 starts after phase19 full-parity runtime proof closure. Use this file
for AutoSci parity continuation work going forward, including first-class
native execution parity, non-runtime local parity, generated artifact UX parity,
and subsequent command-level fixes.

## Agent B First-Class Native Execution Parity Tightening

Logged: 2026-07-03 EDT

Intent: tighten slash-command paths where OpenSolar compatibility output could be
mistaken for native AutoSci execution. This keeps Solar approval/evidence gates,
but prevents scaffold or bridge-only output from presenting as native command
completion.

| Item | Status | Evidence |
|---|---|---|
| `$poster` native precondition | ok | `$poster report-001` no longer emits scaffold `poster_html`; the regular route records `paper_source_missing` until a paper directory containing `main.tex` is supplied. |
| Poster compatibility scaffold | ok | `tools/poster.py build --out` now requires explicit `--compat-scaffold`; the native template/outline/output path remains unchanged. |
| Poster approved renderer | ok | Approved renderer execution now requires actual poster HTML; no-paper route writes inconclusive runtime evidence instead of launching the renderer. |
| `$daily-arxiv` local native path | ok | Shim accepts `--feed`, `--decisions`, and `--no-external`; bridge runs native `tools/daily_arxiv.py prepare/finalize` against local inputs and attaches context/digest artifacts. |
| Side effects | ok | Daily local path defaults to `--no-external`; network, email, scheduler, and auto-ingest side effects remain gated. |

### Issues Encountered And Guardrails

| Issue | Status | Guardrail |
|---|---|---|
| `$poster` could silently produce scaffold HTML without native paper source. | fixed | Scaffold output is only allowed in explicit smoke/compat mode; regular command records the missing native precondition. |
| `tools/poster.py build --out` looked like a native poster build. | fixed | `--compat-scaffold` is now required for scaffold output. |
| Approved poster renderer could be invoked before native poster HTML existed. | fixed | Renderer is blocked with `poster_html_exists=error` runtime evidence if HTML is missing. |
| `$daily-arxiv` with local feed/decisions did not execute native `daily_arxiv.py`. | fixed | Local feed path now invokes native prepare/finalize and maps candidates to Solar evidence schema. |
| Native daily candidates lacked Solar `literature_discovery.v1` required fields. | fixed | Added normalization through `_candidate_from_runtime`. |

### Verification Commands

| Command | Result |
|---|---|
| `python3 -m py_compile harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/bin/autosci_skill_shim.py tools/poster.py` | ok |
| `pytest -q harness/plugins/autosci/tests/test_root_tool_abi.py harness/plugins/autosci/tests/test_autosci_skill_shim.py -k 'poster or daily_arxiv or research_start_from'` | ok: 14 passed, 148 deselected |

## Agent B Remaining First-Class Native Execution Parity

Logged: 2026-07-03 EDT

Intent: continue closing first-class slash-command parity gaps where an
OpenSolar route could produce bridge-native output without invoking the native
AutoSci tool that owns the command semantics.

| Item | Status | Evidence |
|---|---|---|
| `$discover` default path | ok | Non-runtime `$discover` now invokes native `tools/discover.py` for `from-wiki`, `from-anchors`, `from-topic`, and `from-venue` modes, then adapts the native shortlist to Solar `literature_discovery.v1`. |
| `$discover` no-network path | ok | `AUTOSCI_DISABLE_NETWORK_FETCH=1` now reaches native `tools/discover.py --no-network-fetch`; native stdout/payload artifacts are archived. |
| `$init` local plan path | ok | Non-runtime `$init` now invokes native `tools/init_discovery.py prepare` and `tools/init_discovery.py plan --no-network-fetch`; prepare manifest and plan JSON are archived. |
| `$check` review | ok | No route change needed: `/check` already invokes native `tools/lint.py` and stores the lint report. |
| `$reset` review | ok | No route change needed: `/reset` already invokes native `tools/reset_wiki.py` for dry-run and approved execution. |

### Issues Encountered And Guardrails

| Issue | Status | Guardrail |
|---|---|---|
| `$discover` used the OpenSolar backend directly instead of the native discovery CLI. | fixed | Bridge now dispatches to `tools/discover.py`; explicit fixture fallback remains limited to fixture/smoke mode. |
| `$init` produced a plan-only bridge result without native init planner artifacts. | fixed | Bridge now runs native `init_discovery.py prepare` and no-network `plan`, then records native artifacts. |
| Network/provider behavior could be conflated with local native parity. | guarded | `$init` uses native no-network local planning by default; provider fetch and bulk ingest still require approved runtime/source evidence. |
| `$check` and `$reset` looked suspicious during audit because their bridge actions contain Solar gates. | reviewed | Confirmed they already call `tools/lint.py` and `tools/reset_wiki.py`; no additional first-class fix was needed. |

### Verification Commands

| Command | Result |
|---|---|
| `python3 -m py_compile harness/plugins/autosci/bin/autosci_bridge.py` | ok |
| `pytest -q harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_accepts_discover_from_wiki_limit harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_runs_ask_check_and_init_diagnostics` | ok: 2 passed |
| `pytest -q harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_discover_runtime_requires_provider_boundary harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_discover_runtime_attaches_provider_runtime_proof harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_discover_wiki_runtime_proof_is_not_live_provider harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_init_uses_verified_runtime_source_manifest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_init_write_fans_runtime_sources_into_wiki` | ok: 5 passed |
| `pytest -q harness/plugins/autosci/tests/test_source_cli_tools.py harness/plugins/autosci/tests/test_root_tool_abi.py::test_side_effect_root_tools_emit_truthful_non_mutating_evidence` | ok: 8 passed |
| `pytest -q harness/plugins/autosci/tests/test_literature_discover.py` | ok: 2 passed |
