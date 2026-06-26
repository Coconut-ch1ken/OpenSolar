# AutoSci Native Lifecycle Continuation Log

Logged: 2026-06-25 EDT
Branch: `feature/autosci-solar-native`

## Operating Rule

Before each fix, this log records the intended files in scope. After each fix,
it records verification results. A step is not marked complete unless the named
check ran and the remaining limitation is explicit.

## Step 0 - Baseline And Scope Capture

| Field | Value |
|---|---|
| Planned files | `docs/integrations/autosci/continuation-baseline-2026-06-25.md`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Intent | Record baseline and create the dedicated continuation/Phase 15 logs before runtime changes. |
| Out of scope | No Python, JSON config, workflow, gate, or shim behavior changes in this step. |
| Risk | Documentation-only; should not affect runtime behavior. |

### Step 0 Result

| Check | Status | Evidence |
|---|---|---|
| Baseline commands recorded | ok | See `continuation-baseline-2026-06-25.md`. |
| Runtime code changed | ok | None. |
| Full parity claimed | ok | No. |

## Next Planned Step - Lifecycle Gate Split

| Field | Value |
|---|---|
| Planned files | `harness/evaluators/scientific/lifecycle_contract_gate.py`, `harness/evaluators/scientific/lifecycle_runtime_gate.py`, `harness/evaluators/scientific/lifecycle_gate.py`, `harness/tests/evaluators/scientific/test_lifecycle_runtime_gate.py`, `docs/integrations/autosci/native-lifecycle-continuation-log.md` |
| Intent | Split graph contract validation from runtime lifecycle acceptance and add negative tests for empty/missing result maps. |
| Out of scope | No route/config/operator mutation until the runtime gate contract is in place. |
| Risk | Gate behavior may expose existing false-positive lifecycle tests; retain compatibility wrapper where needed. |

### Step 1 Result

| Check | Status | Evidence |
|---|---|---|
| Contract/runtime gate split | ok | Added `lifecycle_contract_gate.py`; `lifecycle_gate.py` dispatches runtime summaries to `lifecycle_runtime_gate.py`. |
| Runtime empty-map rejection | ok | `lifecycle_runtime_gate.py harness/tests/evaluators/scientific/fixtures/pass/lifecycle.json` exits nonzero and rejects missing `job_id`, `node_results`, and `gate_results`. |
| Existing contract workflow validation | ok | `lifecycle_contract_gate.py harness/workflows/scientific_research_lifecycle_full_v1.json` passes. |
| Targeted lifecycle tests | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_lifecycle_gate.py harness/tests/evaluators/scientific/test_lifecycle_runtime_gate.py -q`: 15 passed. |
| Scientific evaluator suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q`: 63 passed. |

## Next Planned Step - Registry Binding Audit

| Field | Value |
|---|---|
| Planned files | `harness/tools/audit_scientific_runtime_bindings.py`, `harness/tests/evaluators/scientific/test_scientific_runtime_binding_audit.py`, `docs/integrations/autosci/native-lifecycle-continuation-log.md` |
| Intent | Add deterministic audit coverage for workflow node -> logical operator -> binding -> physical operator -> host -> command/action -> schema -> gate. |
| Out of scope | Do not mutate operator registries until the audit reports the actual failure set. |
| Risk | Audit may expose stale `backend_action_pending`, placeholder hosts, or missing manifest capabilities. |

### Step 2 Result

| Check | Status | Evidence |
|---|---|---|
| Audit tool added | ok | Added `harness/tools/audit_scientific_runtime_bindings.py`. |
| Synthetic complete-chain test | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_scientific_runtime_binding_audit.py -q`: 2 passed. |
| Current repository audit | error | `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json`: 40 issues, exit 1. |

### Step 2 Current Audit Findings

| Finding | Count/Scope | Next action |
|---|---|---|
| Missing logical bindings | `ScientificLiteratureDiscoverer`, `ScientificPaperAnalyzer`, `ScientificGraphUpdater`, `ScientificMethodExtractor`, `ScientificCodeEvidenceMapper`, `ScientificWorkflowEvolver` | Add bindings to existing AutoSci worker actors. |
| Missing manifest capabilities | `cap.research-literature-discover`, `cap.research-memory-update`, `cap.research-graph-update`, `cap.research-paper-analyze`, `cap.research-idea-evaluate` | Reconcile plugin manifest to all 18 target capabilities. |
| Stale binding condition | `backend_action_pending` on memory and idea bindings | Replace with truthful availability conditions for already registered actions. |
| Missing registered host | AutoSci physical workers point to `solar@example-host` | Add a local command host and point AutoSci workers at it. |

## Next Planned Step - Repair Registry Chain

| Field | Value |
|---|---|
| Planned files | `harness/config/actor-hosts.json`, `harness/config/logical-operators.json`, `harness/config/physical-operators.json`, `harness/plugins/autosci/manifest.yaml`, `docs/integrations/autosci/native-lifecycle-continuation-log.md` |
| Intent | Repair only the failures exposed by the audit: local host registration, missing scientific logical bindings, stale pending conditions, manifest capability omissions, and placeholder AutoSci worker metadata. |
| Out of scope | Do not change bridge action behavior or `$research` execution semantics in this step. |
| Risk | Physical operator metadata changes can affect dispatch selection; keep actor IDs and command strings stable. |

### Step 3 Result

| Check | Status | Evidence |
|---|---|---|
| Local AutoSci host registered | ok | Added `local-autosci-backend` as `local_command_worker` in `actor-hosts.json`. |
| Scientific logical bindings repaired | ok | Added missing bindings and removed `backend_action_pending` from current AutoSci-backed scientific bindings. |
| Manifest reconciled | ok | Added the five missing target capabilities to `plugins/autosci/manifest.yaml`. |
| AutoSci physical metadata repaired | ok | AutoSci workers now point to `local-autosci-backend` and use bounded-local metadata. |
| Strict runtime binding audit | ok | `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json`: 27 nodes, 0 issues. |
| Scientific evaluator suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q`: 65 passed. |
| AutoSci manifest/parity targeted tests | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_manifest_capabilities.py harness/plugins/autosci/tests/test_phase19_parity_bridge.py harness/plugins/autosci/tests/test_phase19_operator_smoke.py -q`: 11 passed. |

## Next Planned Step - Scheduler-Dispatched Bounded Node Proof

| Field | Value |
|---|---|
| Planned files | `harness/tools/run_scientific_node_smoke.py`, `harness/tests/evaluators/scientific/test_scientific_node_runtime_smoke.py`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Intent | Prove one safe `ScientificPaperIngestor` node dispatches through `operator_runtime.submit`, local host/operator metadata, bounded bridge action, evidence artifact, and deterministic gate. |
| Out of scope | Do not claim full `$research` lifecycle execution yet; this is one vertical node slice. |
| Risk | `operator_runtime.submit` may write runtime inbox/lease state under harness runtime directories; generated runtime artifacts must remain under explicit artifact paths. |

### Step 4 Result

| Check | Status | Evidence |
|---|---|---|
| Scheduler node smoke tool added | ok | Added `harness/tools/run_scientific_node_smoke.py`; it submits a `ScientificPaperIngestor` task through `operator_runtime.submit` and waits for `operatord` result artifacts. |
| Isolated dispatch smoke test | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_scientific_node_runtime_smoke.py -q`: 1 passed. |
| End-to-end node chain verified | ok | Test asserts operator result, materialized envelope, bridge result, `research_paper.v1` evidence, output log action, and `paper_gate.py` pass. |
| Scientific evaluator suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q`: 66 passed. |
| Strict runtime binding audit | ok | `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json`: 27 nodes, 0 issues. |
| Full `$research` claimed | ok | No. This proves only one scheduler-dispatched bounded node. |

## Next Planned Step - Scheduler Runtime Lifecycle Summary

| Field | Value |
|---|---|
| Planned files | `harness/config/physical-operators.json`, `harness/tools/run_scientific_node_smoke.py`, `harness/tools/run_scientific_lifecycle_smoke.py`, `harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Intent | Compose multiple scheduler-dispatched bounded nodes into a runtime lifecycle summary accepted by `lifecycle_runtime_gate.py`, starting from paper ingest and paper analyze. |
| Out of scope | Do not mark `$research` full parity until the complete graph, waits, gates, and resume semantics are proven. |
| Risk | Multi-node smoke may reveal missing dependency handoff paths or stale fixture assumptions between node artifacts. |

### Step 5 Result

| Check | Status | Evidence |
|---|---|---|
| Node smoke generalized | ok | `run_scientific_node_smoke.py` now keeps paper ingest as default but supports explicit action/operator/node/logical operator/evidence name parameters. |
| Two-node lifecycle smoke added | ok | Added `harness/tools/run_scientific_lifecycle_smoke.py` for scheduler-dispatched `paper_ingest` and `paper_analyze`. |
| Runtime lifecycle summary accepted | ok | `test_scientific_lifecycle_runtime_smoke.py` verifies `lifecycle_runtime_gate.py` accepts the generated `scientific_lifecycle.v1` summary. |
| Targeted runtime tests | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_scientific_node_runtime_smoke.py harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py harness/tests/evaluators/scientific/test_lifecycle_runtime_gate.py -q`: 11 passed. |
| Scientific evaluator suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q`: 67 passed. |
| Strict runtime binding audit | ok | `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json`: 27 nodes, 0 issues. |
| Full `$research` claimed | ok | No. This proves a two-node scheduler runtime summary, not the complete lifecycle graph. |

## Next Planned Step - Generic Scheduler Node Runtime For Core Actions

| Field | Value |
|---|---|
| Planned files | `harness/tools/run_scientific_node_smoke.py`, `harness/tools/run_scientific_lifecycle_smoke.py`, `harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Intent | Replace paper-only gate wiring with action/schema/gate metadata so the lifecycle smoke can dispatch more bounded core nodes without bespoke code per node. |
| Out of scope | Do not introduce deterministic substitutes for missing model/evidence intelligence; each node must still surface failed/incomplete states through its real gate. |
| Risk | Some existing bridge actions may still depend on earlier fixture paths; generic dispatch may expose missing source-evidence handoff. |

### Step 6 Result

| Check | Status | Evidence |
|---|---|---|
| Schema-driven node gates | ok | `run_scientific_node_smoke.py` now maps action -> expected schema and schema -> deterministic gate CLI. |
| Upstream evidence handoff inputs | ok | `run_scientific_lifecycle_smoke.py` passes prior node artifact paths into memory, graph, method, code, and idea nodes. |
| Core scheduler chain expanded | ok | Lifecycle smoke now dispatches 9 nodes: paper ingest/analyze, memory, graph, claims, methods, code evidence, idea generation, idea evaluation. |
| Runtime lifecycle summary accepted | ok | `test_scientific_lifecycle_runtime_smoke.py` verifies `lifecycle_runtime_gate.py` accepts all 9 node results and artifact hashes. |
| Targeted runtime tests | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_scientific_node_runtime_smoke.py harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py harness/tests/evaluators/scientific/test_lifecycle_runtime_gate.py -q`: 11 passed. |
| Scientific evaluator suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q`: 67 passed. |
| Strict runtime binding audit | ok | `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json`: 27 nodes, 0 issues. |
| Full `$research` claimed | ok | No. Experiment, verification, report/publication, wait/resume, and final memory/workflow evolution are still not complete. |

## Next Planned Step - Experiment Verification And Report Runtime Nodes

| Field | Value |
|---|---|
| Planned files | `harness/tools/run_scientific_lifecycle_smoke.py`, `harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Intent | Extend scheduler lifecycle smoke through experiment design/run/monitor, claim verification, report draft, publication bundle, final memory update, and workflow evolution where current gates allow bounded execution. |
| Out of scope | Do not bypass human approval semantics for real experiment deployment; bounded fixture/local runs must remain labeled as smoke/runtime proof. |
| Risk | Publication and workflow evolution gates may expose missing sidecar output configuration or incomplete source evidence handoff. |

### Step 7 Result

| Check | Status | Evidence |
|---|---|---|
| Experiment and verification nodes added | ok | Lifecycle smoke now dispatches experiment design/run/monitor and claim verification through operator runtime. |
| Report/final memory/workflow nodes added | ok | Lifecycle smoke now dispatches report draft, final memory update, and workflow evolution. |
| Workflow evolution gate fixed by input contract | ok | Synthetic failed-run input now uses `failed` status plus ambiguous manual evidence, so `workflow_evolution_gate.py` passes without weakening the gate. |
| Scheduler runtime coverage | warn | 16 nodes pass; missing nodes are `literature_discover`, `report_plan`, and `publication_produce`. |
| Targeted runtime tests | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_scientific_node_runtime_smoke.py harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py harness/tests/evaluators/scientific/test_lifecycle_runtime_gate.py -q`: 11 passed. |
| Scientific evaluator suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q`: 67 passed. |
| Strict runtime binding audit | ok | `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json`: 27 nodes, 0 issues. |
| Full `$research` claimed | ok | No. Literature discovery, report-plan action binding, publication bundle action binding, durable waits, and resume execution remain open. |

## Next Planned Step - Report And Publication Action Binding Accuracy

| Field | Value |
|---|---|
| Planned files | `harness/tools/audit_scientific_runtime_bindings.py`, `harness/tests/evaluators/scientific/test_scientific_runtime_binding_audit.py`, `harness/config/logical-operators.json`, `harness/config/physical-operators.json`, `harness/tools/run_scientific_node_smoke.py`, `harness/tools/run_scientific_lifecycle_smoke.py`, `harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Intent | Make the audit catch logical node/action/schema mismatches and bind report planning to `plan_report` and publication production to `compile_paper` instead of treating `write_report` as all publication stages. |
| Out of scope | Do not claim external LaTeX/PDF parity unless compile evidence and PDFs are actually produced and gated. |
| Risk | Tightening the audit may reveal additional route truthfulness issues that require registry repair. |

### Step 8 Result

| Check | Status | Evidence |
|---|---|---|
| Action mismatch audit added | ok | `audit_scientific_runtime_bindings.py` now checks node id -> expected bridge action. |
| Audit negative test added | ok | `test_scientific_runtime_binding_audit.py` rejects an otherwise registered but wrong bridge action. |
| Report plan binding repaired | ok | `ScientificReportPlanner` now binds to `autosci-report-plan-worker` running `plan_report`. |
| Publication producer binding repaired | ok | `ScientificPublicationProducer` now binds to `autosci-publication-compile-worker` running `compile_paper`. |
| Node smoke metadata updated | ok | `run_scientific_node_smoke.py` knows `plan_report` and `compile_paper` schemas/actions. |
| Targeted tests | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_scientific_runtime_binding_audit.py harness/tests/evaluators/scientific/test_scientific_node_runtime_smoke.py harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py -q`: 5 passed. |
| Scientific evaluator suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q`: 68 passed. |
| Strict runtime binding audit | ok | `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json`: 27 nodes, 0 issues. |
| Full `$research` claimed | ok | No. `report_plan` still needs independent review evidence; `publication_produce` still needs real compile/PDF or approved runtime evidence to pass. |

## Next Planned Step - Review Evidence For Report Planning

| Field | Value |
|---|---|
| Planned files | `harness/tools/run_scientific_node_smoke.py`, `harness/tools/run_scientific_lifecycle_smoke.py`, `harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Intent | Add scheduler-dispatched artifact review evidence so `plan_report` can run with an explicit Review LLM-equivalent block instead of remaining inconclusive. |
| Out of scope | Do not fabricate a model review; if the local bounded `review_artifact` action marks review unavailable/incomplete, preserve that state. |
| Risk | The report-plan gate may remain inconclusive until review evidence satisfies the bridge's `artifact_review.v1` contract. |

### Step 9 Scope Correction

| Field | Value |
|---|---|
| Actual additional file | `harness/config/physical-operators.json` |
| Reason | A scheduler-dispatched review block required registering `autosci-artifact-review-worker`; no existing physical operator ran `review_artifact`. |

### Step 9 Result

| Check | Status | Evidence |
|---|---|---|
| Review worker registered | ok | Added `autosci-artifact-review-worker` running bounded `review_artifact`. |
| Node smoke review metadata added | ok | `run_scientific_node_smoke.py` maps `review_artifact` to `artifact_review.v1` and `artifact_review_gate.py`. |
| Lifecycle auxiliary review block added | ok | `run_scientific_lifecycle_smoke.py` reviews the generated report draft as `artifact_review`. |
| Review truthfulness preserved | warn | The passing review block is `local_surrogate`; it does not satisfy `plan_report`'s mandatory completed Review LLM condition. |
| Targeted tests | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_scientific_runtime_binding_audit.py harness/tests/evaluators/scientific/test_scientific_node_runtime_smoke.py harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py -q`: 5 passed. |
| Scientific evaluator suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q`: 68 passed. |
| Strict runtime binding audit | ok | `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json`: 27 nodes, 0 issues. |
| Full `$research` claimed | ok | No. Completed Review LLM evidence, report planning, and publication compile/PDF remain open. |

## Next Planned Step - Literature Discovery Runtime Node

| Field | Value |
|---|---|
| Planned files | `harness/tools/run_scientific_lifecycle_smoke.py`, `harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Intent | Add the remaining `literature_discover` workflow node to the scheduler-dispatched lifecycle smoke using the existing bounded discovery action and gate. |
| Out of scope | Do not claim online discovery/full source evidence parity; network fetch remains bounded/off unless explicitly configured. |
| Risk | The discovery gate may expose that current smoke discovery is fixture/local-only. |

### Step 10 Result

| Check | Status | Evidence |
|---|---|---|
| Literature discovery node added | ok | `run_scientific_lifecycle_smoke.py` now dispatches `literature_discover` through `autosci-literature-discover-worker`. |
| Discovery truthfulness preserved | warn | Smoke inputs set `allow_network_fetch=false` and `fixture_fallback=true`; this is scheduler proof, not online evidence parity. |
| Lifecycle smoke accepted | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py -q`: 1 passed. |
| Targeted tests | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_scientific_runtime_binding_audit.py harness/tests/evaluators/scientific/test_scientific_node_runtime_smoke.py harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py -q`: 5 passed. |
| Scientific evaluator suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q`: 68 passed. |
| Strict runtime binding audit | ok | `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json`: 27 nodes, 0 issues. |
| Full `$research` claimed | ok | No. Full workflow still needs `report_plan` with completed Review LLM evidence and `publication_produce` with compile/PDF evidence. |

## Next Planned Step - Durable Blocked States For External Evidence

| Field | Value |
|---|---|
| Planned files | `harness/evaluators/scientific/lifecycle_runtime_gate.py`, `harness/tests/evaluators/scientific/test_lifecycle_runtime_gate.py`, `harness/tools/run_scientific_lifecycle_smoke.py`, `harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Intent | Represent `report_plan` and `publication_produce` as explicit blocked/waiting nodes when Review LLM or compile/PDF evidence is unavailable, instead of omitting them or marking them passed. |
| Out of scope | Do not weaken passed lifecycle acceptance; passed nodes must still have valid artifacts, hashes, schemas, and gates. |
| Risk | Runtime gate status semantics must distinguish partial/blocked lifecycle proof from completed lifecycle proof. |

### Step 11 Result

| Check | Status | Evidence |
|---|---|---|
| Runtime gate blocked-node support | ok | `lifecycle_runtime_gate.py` accepts structured `blocked_nodes` only as `inconclusive`, not `passed`. |
| Blocked-node negative tests | ok | `test_lifecycle_runtime_gate.py` rejects blocked nodes without reason, required evidence, and unblock condition. |
| Blocked lifecycle smoke mode | ok | `run_scientific_lifecycle_smoke.py --include-blocked-external` records `report_plan` and `publication_produce` as blocked external-evidence waits. |
| Passed lifecycle strictness preserved | ok | Default lifecycle smoke still requires passed nodes with artifacts, hashes, schemas, and gate results. |
| Targeted tests | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_lifecycle_runtime_gate.py harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py -q`: 13 passed. |
| Scientific evaluator suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q`: 71 passed. |
| Strict runtime binding audit | ok | `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json`: 27 nodes, 0 issues. |
| Full `$research` claimed | ok | No. The blocked nodes now surface the remaining external evidence requirements truthfully. |

## Remaining Full-Parity Blockers After Step 11

| Blocker | Status | Required evidence/path |
|---|---|---|
| `report_plan` | blocked | Completed `artifact_review.v1` with `review_mode=review_llm` or `review_llm.status=completed`. |
| `publication_produce` | blocked | `publication_bundle.v1` from `compile_paper` with existing source/PDF files or approved compile runtime evidence. |
| Online literature/source parity | warn | Current lifecycle smoke uses bounded local discovery with network disabled. |
| Resume/human wait orchestration | pending | Blocked nodes are represented in runtime evidence; scheduler resume CLI/dispatch for unblocking is still not complete. |

## Next Planned Step - Resume Blocked External Evidence Nodes

| Field | Value |
|---|---|
| Planned files | `harness/tools/run_scientific_lifecycle_smoke.py`, `harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Intent | Add a resume mode that reads a blocked lifecycle summary and dispatches only `report_plan` and `publication_produce` after Review LLM and compile/PDF evidence are supplied. |
| Out of scope | Do not synthesize Review LLM or PDF evidence inside production runtime; tests may create explicit local fixtures as supplied evidence. |
| Risk | Resume must preserve original job id and artifact hashes so lifecycle runtime gate can verify the resumed summary. |

### Step 12 Result

| Check | Status | Evidence |
|---|---|---|
| Blocked lifecycle resume CLI | ok | `run_scientific_lifecycle_smoke.py --resume-summary ...` now resumes only blocked `report_plan` and `publication_produce`. |
| Review/PDF truthfulness preserved | ok | Production resume requires caller-supplied `--review-llm-evidence` and `--compile-target`; it does not synthesize Review LLM or PDF evidence. |
| Runtime gate closure | ok | Resumed nodes dispatch through `operator_runtime.submit`, write artifacts with hashes, and convert blocked lifecycle summaries to passed only after gates pass. |
| Syntax check | ok | `env PYTHONPATH=harness .venv/bin/python -m py_compile harness/tools/run_scientific_lifecycle_smoke.py harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py` passed. |
| Resume lifecycle smoke test | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py -q`: 3 passed. |
| Targeted runtime tests | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_lifecycle_runtime_gate.py harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py -q`: 14 passed. |
| Scientific evaluator suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q`: 72 passed. |
| Strict runtime binding audit | ok | `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json`: 27 nodes, 2 workflows, 0 issues. |
| Full `$research` claimed | ok | No. Online/multi-source evidence fetching still needs a non-fixture parity path and proof. |

## Next Planned Step - Online Source Evidence Strict Mode

| Field | Value |
|---|---|
| Planned files | `harness/tools/run_scientific_lifecycle_smoke.py`, `harness/evaluators/scientific/literature_discovery_gate.py`, `harness/tests/evaluators/scientific/test_literature_discovery_gate.py`, `harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Intent | Add an explicit non-fixture/online discovery mode and gate checks so fixture discovery cannot satisfy full-parity source evidence claims. |
| Out of scope | Do not require network during default smoke; network-restricted runs must surface inconclusive/blocked state instead of fabricating candidates. |
| Risk | Strict online mode may fail in offline CI, so default smoke must remain bounded while full-parity proof requires explicit opt-in. |

### Step 13 Result

| Check | Status | Evidence |
|---|---|---|
| Strict online discovery gate | ok | `literature_discovery_gate.py` now rejects fixture/local candidates when `inputs.require_online_source_evidence=true`. |
| Source fan-in control | ok | Gate enforces `inputs.min_online_source_channels` for online source channel fan-in. |
| Lifecycle strict-mode inputs | ok | `run_scientific_lifecycle_smoke.py` now exposes `--allow-network-fetch`, `--disable-fixture-fallback`, `--require-online-source-evidence`, discovery query/mode/limit, and minimum online source channels. |
| Default smoke preserved | ok | Default lifecycle smoke still uses offline fixture mode unless strict online evidence is explicitly requested. |
| Offline strict-mode truthfulness | ok | Strict online lifecycle test fails without network/online candidates instead of accepting fixture discovery. |
| Syntax check | ok | `env PYTHONPATH=harness .venv/bin/python -m py_compile harness/tools/run_scientific_lifecycle_smoke.py harness/evaluators/scientific/literature_discovery_gate.py harness/tests/evaluators/scientific/test_literature_discovery_gate.py harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py` passed. |
| Related tests | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_literature_discovery_gate.py harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py -q`: 7 passed. |
| Scientific evaluator suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q`: 76 passed. |
| Strict runtime binding audit | ok | `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json`: 27 nodes, 2 workflows, 0 issues. |
| Full `$research` claimed | ok | No. The strict path exists, but a real network-enabled source evidence run still needs to be executed/proven in an environment with online access. |

## Next Planned Step - Approved Runtime Source Evidence For Discovery

| Field | Value |
|---|---|
| Planned files | `harness/plugins/autosci/bin/autosci_bridge.py`, `harness/evaluators/scientific/autosci_runtime_evidence_gate.py`, `harness/tools/run_scientific_lifecycle_smoke.py`, `harness/tests/evaluators/scientific/test_autosci_runtime_evidence_gate.py`, `harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Intent | Allow `discover_literature` to consume approval-gated runtime source-fetch evidence so strict online discovery can be proven from supplied external evidence in offline environments. |
| Out of scope | Do not execute network fetches or invent source candidates inside the bridge. |
| Risk | Runtime evidence must be validated as source-fetch evidence before it can satisfy strict discovery gates. |

### Step 14 Scope Correction

| Field | Value |
|---|---|
| Additional file | `harness/schemas/evidence/autosci_runtime_evidence.v1.schema.json` |
| Reason | Adding `discover_literature` as a validated source-fetch runtime action requires the Evidence ABI schema enum to accept that action. |

### Step 14 Result

| Check | Status | Evidence |
|---|---|---|
| Discovery runtime evidence bridge | ok | `discover_literature` now consumes approval-gated `runtime_evidence` and emits `discover_literature_runtime_verified` only when the contract and runtime semantic checks pass. |
| Runtime evidence validation | ok | `autosci_runtime_evidence_gate.py` and `autosci_runtime_evidence.v1.schema.json` now recognize `discover_literature` as a source-fetch runtime action. |
| Lifecycle strict online unblocked by supplied evidence | ok | Strict lifecycle smoke can pass with supplied approved source runtime evidence and no fixture fallback. |
| Network truthfulness preserved | ok | The bridge does not execute network fetches or invent candidates; incomplete runtime contracts remain inconclusive. |
| Schema check | ok | `python3 -m json.tool harness/schemas/evidence/autosci_runtime_evidence.v1.schema.json` passed. |
| Related tests | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_autosci_runtime_evidence_gate.py harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py -q`: 9 passed. |
| Scientific evaluator suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q`: 77 passed. |
| AutoSci shim source runtime tests | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_init_uses_verified_runtime_source_manifest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_daily_arxiv_uses_verified_runtime_digest -q`: 2 passed. |
| Strict runtime binding audit | ok | `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json`: 27 nodes, 2 workflows, 0 issues. |
| Full `$research` claimed | ok | No. The runtime evidence path is now proven, but a full end-to-end parity run still needs combined source runtime, Review LLM, compile/PDF evidence, and no remaining lifecycle warnings. |

## Next Planned Step - Combined Full External Evidence Lifecycle

| Field | Value |
|---|---|
| Planned files | `harness/tools/run_scientific_lifecycle_smoke.py`, `harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Intent | Add a single lifecycle run mode that dispatches `report_plan` and `publication_produce` when source runtime, Review LLM, and compile/PDF evidence are supplied. |
| Out of scope | Do not treat missing Review LLM or compile/PDF evidence as passed; missing evidence should remain blocked or failed depending on requested mode. |
| Risk | Full run status must remain strict: required external nodes need artifacts, hashes, schemas, and gates like every other scheduler node. |

### Step 15 Result

| Check | Status | Evidence |
|---|---|---|
| Single-run external dispatch | ok | `run_scientific_lifecycle_smoke.py --dispatch-external-evidence` dispatches `report_plan` and `publication_produce` in the same lifecycle run when required evidence is supplied. |
| Missing evidence strictness | ok | Requested external dispatch records missing Review LLM/compile evidence as error/blocked instead of passing. |
| Combined full evidence proof | ok | Lifecycle smoke test passes with strict source runtime evidence, completed Review LLM evidence, compile/PDF target, and no blocked nodes. |
| Syntax check | ok | `env PYTHONPATH=harness .venv/bin/python -m py_compile harness/tools/run_scientific_lifecycle_smoke.py harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py` passed. |
| Lifecycle smoke tests | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py -q`: 5 passed. |
| Scientific evaluator suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q`: 77 passed. |
| Strict runtime binding audit | ok | `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json`: 27 nodes, 2 workflows, 0 issues. |
| Full `$research` claimed | warn | Bounded lifecycle proof is now single-run complete when evidence is supplied, but route truthfulness/coverage metadata still needs review before claiming full AutoSci parity. |

## Step 16 Route Truthfulness Verification

| Check | Status | Evidence |
|---|---|---|
| Planned files | ok | No code/config change planned; this was an audit-only verification of route coverage metadata. |
| Full overclaim scan | ok | `feature_parity_routes.v1.json` has 0 routes with `coverage_status: full`. |
| Route status distribution | ok | Current route config distribution: 17 partial, 11 gated, 0 full. |
| Feature parity gate | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py -q`: 4 passed. |
| Inventory proof | ok | `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step16.json`: 28 native skills, 28 routed, 0 missing, 0 full, 17 partial, 11 gated. |
| Full `$research` claimed | ok | No. Route metadata is now truthful; remaining parity work is capability completion, not route overclaim repair. |

## Next Planned Step - Research Route Consumes Scheduler Lifecycle Evidence

| Field | Value |
|---|---|
| Planned files | `harness/plugins/autosci/bin/autosci_bridge.py`, `harness/plugins/autosci/bin/autosci_skill_shim.py`, `harness/plugins/autosci/tests/test_autosci_skill_shim.py`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Intent | Let `/research` accept a passed `scientific_lifecycle.v1` scheduler runtime summary as route evidence, so the skill route can cite scheduler-native lifecycle proof. |
| Out of scope | Do not mark incomplete or blocked lifecycle summaries as completed research lifecycle evidence. |
| Risk | The bridge must require passed lifecycle gate status, no blocked nodes, and the key full-lifecycle node results before treating the summary as complete. |

### Step 17 Result

| Check | Status | Evidence |
|---|---|---|
| `/research` scheduler summary input | ok | `autosci_skill_shim.py` now accepts `--lifecycle-summary` and forwards it into bridge inputs/native options. |
| Scheduler lifecycle completion guard | ok | `autosci_bridge.py` accepts only `scientific_lifecycle.v1` summaries with `lifecycle_status=passed`, `lifecycle_gate_result.ok=true`, no blocked nodes, and passed key full-lifecycle node results. |
| Stage-plan integration | ok | A valid scheduler lifecycle summary marks all `/research` lifecycle stages completed without requiring duplicate route-plan inference. |
| Targeted tests | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_research_lifecycle_completes_from_scheduler_summary harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_research_lifecycle_completes_from_verified_stage_evidence -q`: 2 passed. |
| Scientific evaluator suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q`: 77 passed. |
| Strict runtime binding audit | ok | `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json`: 27 nodes, 2 workflows, 0 issues. |
| Feature parity inventory | ok | `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step17.json`: 28 routed, 0 missing, 0 full, 17 partial, 11 gated. |
| Full `$research` claimed | warn | `/research` can now consume scheduler-native completed lifecycle evidence, but route status remains partial until real operational/provider evidence policy is satisfied. |

## Next Planned Step - Route Primary Tool Action Truthfulness

| Field | Value |
|---|---|
| Planned files | `harness/plugins/autosci/config/feature_parity_routes.v1.json`, `harness/evaluators/scientific/autosci_feature_parity_gate.py`, `harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Intent | Repair route metadata where `primary_tools` still names old generic bridge actions instead of the configured `solar_backend_action`, and add a gate guard against future drift. |
| Out of scope | Do not upgrade route `coverage_status`; this step only fixes metadata truthfulness. |
| Risk | Some primary tools are non-bridge helper tools; the guard must only enforce action matches when a primary tool explicitly invokes `autosci_bridge.py run --action ...`. |

### Step 18 Result

| Check | Status | Evidence |
|---|---|---|
| Route primary tool metadata repaired | ok | Updated stale bridge action references for exp-eval, exp-pilot-eval, exp-pilot-run, paper-draft, paper-plan, rebuttal, refine, and survey where needed. |
| Drift guard added | ok | `autosci_feature_parity_gate.py` now rejects `primary_tools` bridge action drift when `autosci_bridge.py run --action ...` omits the configured `solar_backend_action`. |
| Negative test added | ok | `test_autosci_feature_parity_gate.py` rejects paper-plan primary tool drift from `plan_report` to `write_report`. |
| JSON validation | ok | `python3 -m json.tool harness/plugins/autosci/config/feature_parity_routes.v1.json` passed. |
| Drift scan | ok | Local scan found no route where bridge primary tool action omits the configured backend action. |
| Feature parity gate tests | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py -q`: 5 passed. |
| Scientific evaluator suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q`: 78 passed. |
| Strict runtime binding audit | ok | `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json`: 27 nodes, 2 workflows, 0 issues. |
| Feature parity inventory | ok | `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step18.json`: 28 routed, 0 missing, 0 full, 17 partial, 11 gated. |

## Step 19 Survey CLI Format Recheck

| Field | Value |
|---|---|
| Planned files | `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Intent | Recheck the audit blocker that reported `$survey --format latex` as rejected before making further parser changes. |
| Out of scope | Do not change survey report semantics or upgrade route coverage; this is a parser/route truthfulness verification only. |

### Step 19 Result

| Check | Status | Evidence |
|---|---|---|
| `$survey --format latex` direct text command | ok | `env HARNESS_DIR=/tmp/autosci-step19-survey .venv/bin/python harness/plugins/autosci/bin/autosci_skill_shim.py text '$survey --format latex --topic skillgen --run-id step19-survey-format-latex'`: `ok=true`, `action_count=1`, `skill=survey`, `execution_status=partial`. |
| Native option propagation | ok | Existing shim test confirms `inputs.native_options.format == latex` and bridge evidence `inputs.format == latex`. |
| Targeted test | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_accepts_survey_format_latex -q`: 1 passed. |
| Code changes | ok | None needed; current parser already accepts the original `--format latex` shape. |
| Remaining parity status | warn | Survey CLI rejection is closed, but `write_survey` remains `partial` until citation-backed survey completeness is proven with real source evidence. |

## Next Planned Step - Wiki-Backed Experiment Status Read

| Field | Value |
|---|---|
| Planned files | `harness/plugins/autosci/bin/autosci_bridge.py`, `harness/plugins/autosci/tests/test_autosci_skill_shim.py`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Intent | Let `$exp-status --pipeline` / `monitor_experiment` answer from resolved wiki experiment state when no fresh runtime/result evidence is supplied. |
| Out of scope | Do not execute experiment commands, collect remote results, or mutate wiki state in status-only mode. |
| Risk | A read-only wiki state must not be overstated as runtime collection; limitations and evidence ids need to make the source explicit. |

### Step 20 Result

| Check | Status | Evidence |
|---|---|---|
| Wiki experiment state fields | ok | `autosci_bridge.py` now preserves experiment `pipeline`, `aliases`, `outcome`, `evidence_ids`, and run-log metadata from wiki frontmatter. |
| Pipeline alias resolution | ok | Wiki resolver aliases now include `pipeline` and explicit alias lists, so `$exp-status --pipeline <slug>` can resolve matching experiments. |
| Read-only status output | ok | `monitor_experiment` emits `experiment_status.v1` from resolved wiki experiment state only when no `--collect` or runtime evidence path is active. |
| Targeted tests | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest ...test_autosci_skill_shim_exp_status_pipeline_runs_monitor_action ...test_autosci_skill_shim_exp_status_pipeline_reads_wiki_experiment_state -q`: 2 passed. |

## Step 21 Result - Novelty Review LLM Absence Semantics

| Check | Status | Evidence |
|---|---|---|
| Implicit Review LLM provider disabled for novelty | ok | `autosci_skill_shim.py` now sets `review_llm_requested` for idea/novelty evaluation only when `--review` or explicit Review LLM evidence/command/provider/endpoint inputs are supplied. |
| Missing Review LLM state | ok | Local novelty paths now report Review LLM evidence as `unavailable`, not provider `failed`, when no Review LLM source was supplied. |
| Write-back strictness | ok | Novelty write-back still requires completed external novelty provenance and completed Review LLM evidence before mutating wiki novelty score. |
| Targeted tests | ok | Novelty Review LLM absence/write-back group: 4 previously failing semantic cases now pass as part of the 5-test novelty group. |

## Step 22 Result - Novelty Online Archive Test Assertion

| Check | Status | Evidence |
|---|---|---|
| Test assertion repaired | ok | `test_autosci_skill_shim_novelty_defaults_to_online_fetch_when_available` now checks provider `raw_payload_ref`, `raw_payload_archive_status`, and archive file existence instead of checking a local directory string for `file://`. |
| Novelty targeted group | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest ...novelty... -q`: 5 passed. |
| Full shim suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q`: 80 passed when rerun outside the sandbox because one provider test binds `127.0.0.1`. |
| Scientific evaluator suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q`: 78 passed. |
| Strict runtime binding audit | ok | `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json`: 27 nodes, 2 workflows, 0 issues. |
| Feature parity inventory | ok | `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step22.json`: 28 routed, 0 missing, 0 full, 17 partial, 11 gated. |
| Full parity claim | warn | Still not honest to claim full parity; remaining routes depend on real provider/network/approval-gated execution evidence. |

## Next Planned Step - Ideate Model Brainstorm Evidence Path

| Field | Value |
|---|---|
| Planned files | `harness/plugins/autosci/bin/autosci_bridge.py`, `harness/plugins/autosci/tests/test_autosci_skill_shim.py`, `harness/plugins/autosci/config/feature_parity_routes.v1.json`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Intent | Let `/ideate` consume explicit model evidence or a model-command bridge to produce source-grounded candidate ideas instead of only deterministic local candidates. |
| Out of scope | Do not silently call a provider, invent model output, or mark dual-model parity complete without supplied model evidence. |
| Risk | Invalid model output must not be treated as a passed brainstorm; generated ideas still need origin evidence ids and novelty/review gates. |

## Next Planned Step - Novelty Review LLM Absence Semantics

| Field | Value |
|---|---|
| Planned files | `harness/plugins/autosci/bin/autosci_skill_shim.py`, `harness/plugins/autosci/backends/novelty_review.py`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Intent | Preserve the distinction between missing Review LLM evidence (`unavailable`) and real Review LLM/provider failures (`failed`) in novelty evaluation/write-back by disabling implicit provider invocation unless explicitly requested. |
| Out of scope | Do not replace Review LLM with a deterministic pass; local surrogate remains non-promotional. |
| Risk | Write-back gates must still require completed external novelty evidence and completed Review LLM evidence. |

## Next Planned Step - Novelty Online Archive Test Assertion

| Field | Value |
|---|---|
| Planned files | `harness/plugins/autosci/tests/test_autosci_skill_shim.py`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Intent | Replace an impossible local-path assertion with checks against the actual provider file URI and archived payload evidence. |
| Out of scope | Do not change novelty fetching/product behavior. |
| Risk | The test should still prove online/file-backed Semantic Scholar evidence and payload archiving, not merely remove coverage. |
