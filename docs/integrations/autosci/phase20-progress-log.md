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

## Agent B First-Class Native Execution Parity Audit: Ingest

Logged: 2026-07-03 EDT

Intent: audit whether any first-class command execution path still bypassed a
native AutoSci root tool after the `$visualize`, `$poster`, `$daily-arxiv`,
`$init`, and `$discover` native-path fixes.

| Item | Status | Evidence |
|---|---|---|
| `$ingest` native source prepare | ok | `$ingest` now invokes `tools/prepare_paper_source.py` before bridge parsing; native payload/stdout artifacts are archived and preparation records `native_prepare_paper_source`. |
| Parser compatibility | ok | Existing `read_paper_source` parser remains responsible for the Solar `research_paper.v1` body/sections so parse quality and ABI output do not regress. |
| Remaining first-class audit | ok | Explicit root-tool commands now have native invocation or remain approval-gated remote/provider paths: visualize, poster, daily-arxiv, init, discover, ingest, check, reset, and remote execution. |

### Issues Encountered And Guardrails

| Issue | Status | Guardrail |
|---|---|---|
| `$ingest` source normalization used only the OpenSolar backend. | fixed | Route now runs native `prepare_paper_source.py` and archives native payload/stdout. |
| Replacing the parser wholesale could alter `research_paper.v1` ABI and parse quality. | guarded | Native CLI is the source-normalization authority; existing parser still emits paper body/sections. |
| `research_wiki.py` calls appear in many native skills. | deferred | Treat as command-internal wiki mutation/UX parity unless the slash route has an explicit native root tool that is bypassed. |

### Verification Commands

| Command | Result |
|---|---|
| `python3 -m py_compile harness/plugins/autosci/bin/autosci_bridge.py` | ok |
| `pytest -q test_autosci_skill_shim.py::test_autosci_skill_shim_maps_positional_ingest_source test_autosci_skill_shim.py::test_autosci_skill_shim_ingests_pdf_with_extracted_text_and_no_fixture_leakage` | ok: 2 passed |
| `pytest -q harness/plugins/autosci/tests/test_autosci_skill_shim.py -k ingest` | ok: 8 passed, 146 deselected |
| `pytest -q harness/plugins/autosci/tests/test_source_cli_tools.py harness/plugins/autosci/tests/test_paper_prepare.py` | ok: 11 passed |
| `git diff --check -- harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/tests/test_autosci_skill_shim.py docs/integrations/autosci/phase20-progress-log.md` | ok |

## Agent B Problem 3 Side-Effect Parity: Visualize Serve Policy Gate

Logged: 2026-07-03 EDT

Intent: begin solving the side-effect parity class from the updated prompt:
allow the same bounded side effects in AutoSci parity modes instead of only
emitting health/proposal evidence. This slice covers `$visualize --serve`.

| Item | Status | Evidence |
|---|---|---|
| Central gate policy | ok | Added `harness/plugins/autosci/policy/gate_policy.py` with `strict_hitl`, `safe`, `parity_demo`, `unsafe_native`, and `autosci_native` modes. |
| Strict default | ok | Default mode remains `strict_hitl`; existing `$visualize --serve` without approval still does not execute the server path. |
| Visualize side effect | ok | In `parity_demo`, `$visualize --serve` auto-generates a synthetic policy approval and runs native `tools/serve.py --probe-server --port 0`. |
| Native server lifecycle | ok | `tools/serve.py --probe-server` binds a loopback HTTP server, probes `/api/health`, records `server_started=true`, and shuts down. |
| Evidence attachment | ok | Action evidence includes `outputs.policy_decision`, `provenance.gate_policy`, `gate_policy_decision_json`, and synthetic approval contract evidence. |
| Scope | partial | Only `$visualize --serve` is connected to the new policy gate in this slice; compile/poster/experiment/daily/reset remain follow-up action integrations. |

### Issues Encountered And Guardrails

| Issue | Status | Guardrail |
|---|---|---|
| The prompt's full policy request spans many side-effect routes. | scoped | Implemented the shared policy layer plus one representative route first; did not broad-edit all side-effect actions in one pass. |
| `serve.py --health-check` did not actually bind a server. | fixed | Added bounded `--probe-server`, which starts the HTTP server, probes it, then shuts it down. |
| System `python3` lacked PyYAML for native visualize/serve dependencies in a manual demo. | documented | Use the repo `.venv/bin/python` or harness Python for native tools requiring project dependencies. |
| Sandbox loopback restrictions can block the server probe. | documented | Focused pytest passed; manual demo needed an elevated loopback run to prove `server_started=true`. |
| Synthetic policy approval could be mistaken for human approval. | guarded | Synthetic refs use `policy:auto:<mode>:<action>:<timestamp>` and evidence warnings state no human approval was requested. |

### Verification Commands

| Command | Result |
|---|---|
| `python3 -m py_compile harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/policy/gate_policy.py tools/serve.py` | ok |
| `pytest -q harness/plugins/autosci/tests/test_gate_policy_modes.py` | ok: 9 passed |
| `pytest -q harness/plugins/autosci/tests/test_root_tool_abi.py::test_side_effect_root_tools_emit_truthful_non_mutating_evidence` | ok: 1 passed |
| `pytest -q test_autosci_skill_shim.py::test_autosci_skill_shim_accepts_visualize_serve_flag_without_server_execution test_autosci_skill_shim.py::test_autosci_skill_shim_visualize_parity_demo_auto_runs_server_probe test_autosci_skill_shim.py::test_autosci_skill_shim_visualize_serve_emits_approved_runtime_proofs` | ok: 3 passed |
| `pytest -q harness/plugins/autosci/tests/test_gate_policy_modes.py harness/plugins/autosci/tests/test_root_tool_abi.py::test_side_effect_root_tools_emit_truthful_non_mutating_evidence ...visualize serve tests` | ok: 13 passed |
| `env HARNESS_DIR=/private/tmp/opensolar_autosci_policy_smoke SOLAR_AUTOSCI_OUTPUT_HARNESS=/private/tmp/opensolar_autosci_policy_smoke python3 harness/plugins/autosci/bin/autosci_bridge.py smoke` | ok |
| `env HARNESS_DIR=/private/tmp/opensolar_autosci_policy_smoke SOLAR_AUTOSCI_OUTPUT_HARNESS=/private/tmp/opensolar_autosci_policy_smoke python3 harness/plugins/autosci/bin/autosci_bridge.py validate --result /private/tmp/opensolar_autosci_policy_smoke/artifacts/autosci/smoke/result.json` | ok |
| elevated demo: `.venv/bin/python harness/plugins/autosci/bin/autosci_skill_shim.py skill visualize "autosci graph" --serve --gate-mode parity_demo --run-id policy-demo-visualize-serve` | ok: `passed_count=1`; `visualize_web_health.json` has `server_started=true`, `server_stopped=true`; approval contract has `execution_verified=true`. |
| `git diff --check -- <changed AutoSci policy/visualize files>` | ok |

## Agent B Problem 3 Side-Effect Parity: Compile, Poster, And Local Experiment Run

Logged: 2026-07-03 EDT

Intent: continue solving the side-effect parity class after `$visualize --serve`
by letting policy-approved parity modes execute bounded local side effects for
publication compile, poster render/export, and local experiment run paths while
preserving runtime semantic verification.

| Item | Status | Evidence |
|---|---|---|
| Shared policy helper | ok | Added `_policy_prepare_auto_contract()` and `autosci_gate_policy_allowlist.v1` sidecars so side-effect actions can attach gate decisions and synthetic allowlist evidence consistently. |
| `$paper-compile` | ok | In `parity_demo`, discovered supported TeX executors are converted into a synthetic policy allowlist; actual completion still requires executor exit success and structurally valid PDF proof. |
| `$poster` | ok | In `parity_demo`, policy approval can trigger the existing approved renderer path, but only when concrete `poster_render_command` or `poster_renderer` allowlist evidence is supplied. |
| `$exp-run --env local` | ok | In `parity_demo`, policy approval can trigger a supplied concrete local command allowlist, then the existing runtime semantic and wiki mutation checks decide completion. |
| Evidence attachment | ok | Compile/poster/experiment evidence now includes `outputs.policy_decision`, `provenance.gate_policy`, `gate_policy_decision_json`, and relevant policy/allowlist sidecars. |

### Issues Encountered And Guardrails

| Issue | Status | Guardrail |
|---|---|---|
| The initial `$exp-run` policy allowlist treated exp-design's generic handoff command (`autosci_bridge.py run --action run_experiment`) as executable allowlist evidence. | fixed | `run_experiment` policy sidecars now record `declared_plan_commands` for audit only; executable selection still requires concrete command allowlist evidence or supplied verified runtime evidence. |
| Synthetic policy approval can look similar to user approval in downstream contracts. | guarded | Synthetic refs keep the `policy:auto:<mode>:<action>:<timestamp>` prefix and sidecars state that they are not human approval artifacts. |
| `$poster` cannot safely infer a browser renderer from policy mode alone. | guarded | The policy gate can approve execution, but the renderer still must come from concrete allowlist evidence. Missing renderer remains inconclusive. |
| TeX availability differs by machine. | guarded | `$paper-compile` auto-execution only allowlists supported executors discovered on `PATH`; missing executor or invalid PDF output remains inconclusive. |

### Verification Commands

| Command | Result |
|---|---|
| `python3 -m py_compile harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/policy/gate_policy.py tools/serve.py` | ok |
| `pytest -q test_autosci_skill_shim.py::test_autosci_skill_shim_exp_run_parity_demo_auto_executes_local_command test_autosci_skill_shim.py::test_autosci_skill_shim_paper_compile_parity_demo_auto_executes_executor test_autosci_skill_shim.py::test_autosci_skill_shim_poster_parity_demo_auto_executes_renderer` | ok: 3 passed |
| `pytest -q harness/plugins/autosci/tests/test_autosci_skill_shim.py -k 'paper_compile or poster or exp_run'` | ok: 28 passed, 130 deselected |
| `pytest -q harness/plugins/autosci/tests/test_gate_policy_modes.py` | ok: 9 passed |
| `git diff --check -- <changed AutoSci problem3 files>` | ok |

## Agent B Problem 3 Side-Effect Parity: Init Source Fan-In

Logged: 2026-07-03 EDT

Intent: continue solving the side-effect parity class for remaining commands by
connecting `$init --write` to the policy-approved local wiki fan-in path without
auto-running provider/network fetch, email, remote execution, or bulk ingest.

| Item | Status | Evidence |
|---|---|---|
| `$init --write` policy approval | ok | In `parity_demo`, `$init --write` can generate synthetic policy approval/allowlist evidence for the local `wiki_fan_in` side effect. |
| Runtime source boundary | ok | Fan-in still requires supplied runtime source candidates with completed provider-source boundary evidence; policy mode does not fabricate source/provider proof. |
| Two-stage contract | ok | Before fan-in, the contract can be ready with runtime candidates but missing after artifacts; after real page/log/graph/rebuild files are written, those files are appended as after artifacts and the contract is refreshed. |
| Final readiness | ok | `init_sources_final_fan_in_boundary` reaches `init_sources_final_fan_in_ready` only after provider candidates, semantic runtime verification, wiki mutation, log, graph edge, index, and context brief evidence are present. |
| Scope preservation | ok | `$daily-arxiv` still emits ingest handoff for daily candidates and does not directly write paper pages or auto-send email/auto-ingest. |

### Issues Encountered And Guardrails

| Issue | Status | Guardrail |
|---|---|---|
| The original generic approval semantic check required after artifacts before fan-in, but fan-in itself produces the after artifacts. | fixed | `$init` now uses a two-stage source-runtime check for policy fan-in, then re-runs semantic verification after real fan-in files exist. |
| Runtime candidates could be replaced by the local init plan when semantic verification was incomplete only because after artifacts were missing. | fixed | If runtime candidate records are loaded, `$init` keeps them and does not fall back to the local plan candidate list. |
| Synthetic policy approval could be mistaken for live provider/network execution. | guarded | Policy allowlist text and handoff docs state that `$init` policy approval covers local wiki fan-in only. Provider/network, email, remote, and bulk ingest remain gated. |

### Verification Commands

| Command | Result |
|---|---|
| `python3 -m py_compile harness/plugins/autosci/bin/autosci_bridge.py` | ok |
| `pytest -q test_autosci_skill_shim.py::test_autosci_skill_shim_init_parity_demo_auto_fans_runtime_sources_into_wiki` | ok: 1 passed |
| `pytest -q test_autosci_skill_shim.py::test_autosci_skill_shim_init_uses_verified_runtime_source_manifest test_autosci_skill_shim.py::test_autosci_skill_shim_init_write_fans_runtime_sources_into_wiki test_autosci_skill_shim.py::test_autosci_skill_shim_init_parity_demo_auto_fans_runtime_sources_into_wiki` | ok: 3 passed |
| `pytest -q harness/plugins/autosci/tests/test_gate_policy_modes.py` | ok: 9 passed |
| `pytest -q harness/plugins/autosci/tests/test_autosci_skill_shim.py -k 'init or daily_arxiv or discover or source_fan_in or ingest'` | ok: 22 passed, 137 deselected |
| `python3 -m py_compile harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/policy/gate_policy.py` | ok |
