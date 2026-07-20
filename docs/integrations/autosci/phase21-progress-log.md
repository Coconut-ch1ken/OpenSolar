# AutoSci Solar Phase 21 Progress Log

Phase21 starts after the Phase20 native-execution, installer-closure, and
cross-repo E2E artifact snapshot work. Use this file for follow-up work on
AutoSci runtime integration, generated artifact UX parity, live graph rendering,
and subsequent command-level fixes.

## Cross-Repo AutoSci OmegaWiki Graph UX Follow-Up

Logged: 2026-07-08 EDT

Intent: record the follow-up fixes made in the BetterSolar artifact generator
after the first native-style OmegaWiki parity pass, specifically the repeated
blank/broken graph reports, overloaded labels, stale serving confusion, and the
need for an Obsidian-style dynamic idea graph rather than a static lane list.

| Item | Status | Evidence |
|---|---|---|
| Graph data integrity | ok | Regenerated `autosci_native_final/omegawiki_ui/graph-data.json` from source run artifacts; current generated data contains 514 nodes, 702 edges, 39 selected ideas, and 5 normalized generation paths. |
| Workflow graph default | ok | Graph view now defaults to `Selected Workflow` and displays the bounded selected workflow graph instead of the overloaded all-node graph. Generated `run-status.json` records 119 workflow nodes and 117 workflow edges. |
| Blank graph fallback | ok | Graph filtering now treats both boolean/string selected markers and `selected_for_experiment` as selected ideas, and falls back from an unexpectedly empty selected workflow view to the idea view instead of rendering a blank canvas. |
| Idea Graph layout | ok | Replaced the brittle row/rail layout with a force-directed, Obsidian-style cloud layout using paper, idea, experiment, claim, method, code, document, and verdict nodes. |
| Label overlap control | ok | Default idea-graph labels are off; when labels are enabled, both Graph and Idea Graph use simple collision avoidance and priority-based label selection to reduce overlap. |
| Native-style route behavior | ok | Reader, Graph, Idea Graph, and Dashboard remain hash-routed views backed by the same generated `index.html`, `graph-data.json`, and `run-status.json` deliverable. |
| Serving diagnosis | ok | Visual checks showed the regenerated UI had nodes when served from the correct `omegawiki_ui` directory; remaining blank reports were traced to stale/stopped local server or stale browser tab/cache risk rather than empty graph data. |

### Issues Encountered And Guardrails

| Issue | Status | Guardrail |
|---|---|---|
| The first follow-up graph layout could still look like a table of rails rather than an Obsidian-style graph. | fixed | `computeIdeaLayout()` now runs a bounded force simulation with repulsion, link attraction, and weak path/type centers before drawing the SVG. |
| Labels could overwhelm the graph and make nodes appear broken even when data existed. | fixed | Idea Graph labels are opt-in by default, and label rendering uses priority/collision filtering. |
| Selected workflow could compute zero visible nodes if selected flags were serialized differently. | fixed | Selection checks now accept multiple selected markers and fall back to ideas when a selected workflow view is empty. |
| A stale HTTP server or stale browser tab could make the UI appear blank after files were regenerated. | guarded | The validation procedure now includes checking the served URL/port, regenerating the artifact, restarting the local server against the exact `omegawiki_ui` directory, and performing a browser visual check. |
| Raw generation paths such as repeated `A:` prefixes made idea naming and grouping noisy. | fixed | Generator preserves `raw_generation_path` for provenance while normalizing `generation_path` into five reader-facing lanes. |

### Verification Commands

| Command | Result |
|---|---|
| `.venv/bin/python harness/artifacts/autosci/runs/e2e-doc-literature-20260707-idea-chain/tools/generate_autosci_native_final_outputs.py` in BetterSolar | ok: regenerated final report artifacts, graph data, run status, and OmegaWiki UI. |
| `node -e '<extract generated index.html script and compile with new Function(...)>'` in BetterSolar | ok: generated SPA script parsed successfully. |
| `jq '.nodes | length' .../omegawiki_ui/graph-data.json` | ok: 514 nodes. |
| `jq '.edges | length' .../omegawiki_ui/graph-data.json` | ok: 702 edges. |
| `jq '.selected_idea_count, .workflow_graph_node_count, .workflow_graph_edge_count' .../omegawiki_ui/run-status.json` | ok: 39 selected ideas, 119 workflow nodes, 117 workflow edges. |
| Browser visual check on `http://127.0.0.1:8766/#/graph` | ok: selected workflow graph rendered nodes/edges, not a blank canvas. |
| Browser visual check on `http://127.0.0.1:8766/#/idea-graph` | ok: Obsidian-style dynamic idea graph rendered nodes/edges on light background with labels hidden by default. |

## AutoSci Normal Intake Orchestration Contract

Logged: 2026-07-08 EDT

Intent: close the normal-intake orchestration gap where AutoSci components were
registered and callable, but ordinary Solar intake could still route a full
AutoSci research request through generic planning paths instead of binding it to
the AutoSci scientific lifecycle by construction.

| Item | Status | Evidence |
|---|---|---|
| Deterministic intake contract | ok | Added `research.autosci.v1` detection/materialization in `BetterSolar/harness/lib/autosci_intake_contract.py`; explicit AutoSci research workflow requests instantiate `scientific_research_lifecycle_full_v1`. |
| RawIntent / PM compiler routing | ok | `BetterSolar/harness/tools/codex_pm_router.py` now routes matching normal intake text into a Scientific* task graph instead of a generic `ResearchScout` graph. |
| Long / epic intake routing | ok | `BetterSolar/harness/lib/epic_decomposer.py` now detects long AutoSci workflow requests and creates an AutoSci-bound child sprint rather than the generic requirements-slice epic. |
| Graph-ready compiled package | ok | `BetterSolar/harness/tools/pm_dispatch.py` now marks AutoSci contract-bound compiled packages as `active`, `planning_complete`, and `builder_main` so the graph scheduler can pick them up. |
| Exact physical worker selection | ok | `BetterSolar/harness/lib/apo_plan_compiler.py` maps Scientific logical operators to exact `autosci-*` workers, avoiding same-role or alphabetical fallback selection. |
| Regression coverage | ok | `BetterSolar/harness/tests/test_autosci_intake_contract.py` covers explicit detection, task-graph materialization, RawIntent consumer routing, epic intake routing, capsule binding, and physical worker selection. |

### Issues Encountered And Guardrails

| Issue | Status | Guardrail |
|---|---|---|
| AutoSci was installed/registered but ordinary runtime intake did not deterministically choose it. | fixed | Requests that explicitly name AutoSci or native AutoSci workflow skills plus research/workflow intent now bind to `research.autosci.v1`. |
| Generic planner routing could turn a full AutoSci request into a non-AutoSci research task graph. | fixed | Contract-bound intake builds the existing full Scientific* lifecycle graph directly. |
| Epic decomposition could hide AutoSci inside generic child requirements slices. | fixed | Long AutoSci requests now get an AutoSci-bound child sprint and parent graph metadata. |
| Compiled AutoSci sprint packages could be emitted in a planner-oriented status. | fixed | Contract-bound packages are emitted as graph-ready builder handoffs. |
| Physical selection could choose same-role siblings by fallback ordering. | fixed | Scientific logical operators now have explicit `autosci-*` physical worker mappings. |
| Contract detection should not hijack unrelated engineering tasks. | guarded | Detection requires both an AutoSci/native-skill signal and a research/workflow action signal; a generic dashboard/README request remains non-AutoSci. |

### Verification Commands

| Command | Result |
|---|---|
| `env PYTHONPATH=harness .venv/bin/python -m pytest -q harness/tests/test_autosci_intake_contract.py` in BetterSolar | ok: 4 passed. |

## AutoSci Evaluator Gate Integration Fixes

Logged: 2026-07-08 EDT

Intent: close the remaining orchestration-level blocker after normal intake
routing was made contract-bound. AutoSci could be selected and run as component
operators, but the runtime still needed an evaluator-seam integration so a
completed Scientific* node would be verified by AutoSci evidence gates and
converted into a Solar gate-consumable verdict automatically.

| Item | Status | Evidence |
|---|---|---|
| AutoSci evaluator adapter | ok | Added `BetterSolar/harness/plugins/autosci/bin/autosci_eval_adapter.py`; it discovers node evidence, runs the matching scientific evidence gate, and writes canonical `solar.eval.v1` `eval.json` plus `eval.md`. |
| Runtime evaluator registration | ok | Added `autosci-evaluator-worker` in `BetterSolar/harness/config/physical-operators.json` with `role: evaluator`, `persona: evaluator`, and an envelope-driven command that calls the AutoSci eval adapter. |
| Eval dispatch wiring | ok | Updated `BetterSolar/harness/lib/graph_node_dispatcher.py`; `research.autosci.v1` Scientific/cap.research nodes now route through `operator:autosci-evaluator-worker` during `dispatch_node_evals`, then call `node_verdict` with the adapter verdict. |
| Gate-consumable verdict contract | ok | Adapter output includes `schema_version: solar.eval.v1`, `verdict`, `failed_conditions`, `generated_by`, `generation_mode`, `proof_level`, `independent_author`, evidence paths, gate result, and provenance fields consumed by the runtime gate path. |
| Red/green acceptance coverage | ok | Added `BetterSolar/harness/tests/graph/test_autosci_eval_dispatch.py`; covers adapter PASS/FAIL, command-envelope mode, normal intake graph to AutoSci evaluator dispatch, and failing verification blocking the stage as `failed_review`. |

### Issues Encountered And Guardrails

| Issue | Status | Guardrail |
|---|---|---|
| AutoSci operators were producer-shaped; no runtime evaluator automatically consumed node artifacts. | fixed | Contract-bound AutoSci nodes now use a dedicated evaluator adapter at the graph eval dispatch seam. |
| AutoSci evidence spoke scientific evidence schemas, while the graph gate consumes `solar.eval.v1`. | fixed | Adapter translates typed evidence plus scientific gate result into canonical Solar eval sidecars. |
| A smart pane could call AutoSci manually, but that did not prove official intake orchestration. | guarded | Tests distinguish pane/manual behavior from normal intake -> RawIntent -> task graph -> `dispatch_node_evals` routing. |
| A failing AutoSci verification could be missed if only happy-path component tests were run. | fixed | Red-path test asserts failed evidence produces FAIL eval output and blocks the node as `failed_review`, without passing the node gate. |
| Test isolation initially risked mutating the root physical operator registry runtime state. | fixed | Eval dispatch tests copy `config/` into an isolated harness fixture instead of symlinking it. |

### Verification Commands

| Command | Result |
|---|---|
| `env PYTHONPATH=harness harness/bin/python3 -m py_compile harness/plugins/autosci/bin/autosci_eval_adapter.py harness/lib/graph_node_dispatcher.py` in BetterSolar | ok. |
| `harness/bin/python3 -c 'import json; json.load(open("harness/config/physical-operators.json", encoding="utf-8")); print("physical-operators json ok")'` in BetterSolar | ok: `physical-operators json ok`. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest -q harness/tests/graph/test_autosci_eval_dispatch.py harness/tests/test_autosci_intake_contract.py` in BetterSolar | ok: 8 passed. |
| `env PYTHONPATH=harness AUTOSCI_DISABLE_NETWORK_FETCH=1 harness/bin/python3 -m pytest -q harness/tests/evaluators/scientific/test_scientific_node_runtime_smoke.py` in BetterSolar | ok: 1 passed. |
| `env PYTHONPATH=harness AUTOSCI_DISABLE_NETWORK_FETCH=1 harness/bin/python3 -m pytest -q harness/tests/integration/test_autosci_routes_list.py harness/tests/integration/test_autosci_cli_dispatch.py harness/tests/integration/test_autosci_ingest_demo.py harness/tests/integration/test_autosci_review_demo.py harness/tests/integration/test_autosci_research_scheduler_demo.py harness/tests/integration/test_autosci_artifact_root.py` in BetterSolar | ok: 6 passed. |
| `env PYTHONPATH=harness AUTOSCI_DISABLE_NETWORK_FETCH=1 harness/bin/python3 -m pytest -q harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_research_scheduler_run_attaches_blocked_summary harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_research_scheduler_demo_uses_multi_node_preset` in BetterSolar | ok: 2 passed. |



## AutoSci Producer Dispatch Integration Fix

Logged: 2026-07-08 EDT

Intent: close the producer-side dispatch blocker found during official Solar intake testing. The generated `research.autosci.v1` DAG was structurally correct and compiled to the right `autosci-*` physical operators, but `dispatch-ready` still stopped at `no_matching_worker` because graph worker discovery only saw tmux/generic operator-pool workers and not the local AutoSci command operators.

| Item | Status | Evidence |
|---|---|---|
| Exact AutoSci command-worker discovery | ok | Updated `BetterSolar/harness/lib/graph_node_dispatcher.py`; `dispatch_ready()` now enriches the graph, detects current ready `research.autosci.v1` Scientific nodes, and exposes only their exact `operator:<autosci-worker>` virtual worker. |
| Direct operator runtime submit path | ok | Added `autosci_operator_direct` dispatch handling in `graph_node_dispatcher.py`; `operator:<autosci-worker>` assignments now build a Solar operator envelope and call `operator_runtime.submit()` instead of falling through to tmux pane existence checks. |
| DAG-to-action envelope contract | ok | Direct dispatch envelopes include `runner_contract: research.autosci.v1`, `expected_action`, `expected_schema`, declared evidence output path, handoff path, dependency evidence paths, capsule plan IR, and physical plan IR. |
| Wrong-worker prevention | ok | AutoSci virtual workers are generated only for the graph scheduler current ready nodes, preventing unrelated AutoSci workers from winning assignment by alphabetical or generic role fallback. |
| Regression coverage | ok | Added producer-dispatch coverage in `BetterSolar/harness/tests/graph/test_autosci_eval_dispatch.py`; it proves normal intake dry-run dispatch selects `operator:autosci-literature-discover-worker` with `expected_action: discover_literature`, and the queue-item drain path submits the envelope through `operator_runtime.submit()`. |

### Issues Encountered And Guardrails

| Issue | Status | Guardrail |
|---|---|---|
| The DAG was correct, but `dispatch-ready --dry-run` reported `no_matching_worker` for `literature_discover`. | fixed | Contract-bound AutoSci ready nodes now advertise exact local command workers to the scheduler. |
| Generic `operator-pool:builder` would not guarantee the Scientific node used the intended `autosci-*` worker. | fixed | AutoSci producer nodes now dispatch through `operator:<exact-autosci-worker>` and `operator_runtime.submit()`. |
| If all AutoSci workers were advertised at once, a node with weak/empty hard capabilities could choose the wrong AutoSci worker. | fixed | Worker augmentation is limited to scheduler-ready nodes for the current batch. |
| A failed operator submit could leave a node stuck as assigned. | guarded | Direct-submit failure clears the assignment and returns the node to `pending` for retry. |

### Verification Commands

| Command | Result |
|---|---|
| `env PYTHONPATH=harness harness/bin/python3 -m py_compile harness/lib/graph_node_dispatcher.py harness/tests/graph/test_autosci_eval_dispatch.py` in BetterSolar | ok. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest -q harness/tests/graph/test_autosci_eval_dispatch.py` in BetterSolar | ok: 6 passed. |
| `env PYTHONPATH=harness HARNESS_DIR="$PWD/harness" SOLAR_HARNESS_DIR="$PWD/harness" harness/bin/python3 -c ... dispatch-ready dry-run summary ...` in BetterSolar | ok: actual intake graph enqueued `literature_discover` to `operator:autosci-literature-discover-worker`, `dispatch_mode: autosci_operator_direct`, `expected_action: discover_literature`, with no queued or worker-blocked nodes. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest -q harness/tests/graph/test_autosci_eval_dispatch.py harness/tests/test_autosci_intake_contract.py` in BetterSolar | ok: 10 passed. |
| `env PYTHONPATH=harness AUTOSCI_DISABLE_NETWORK_FETCH=1 harness/bin/python3 -m pytest -q harness/tests/evaluators/scientific/test_scientific_node_runtime_smoke.py` in BetterSolar | ok: 1 passed. |
