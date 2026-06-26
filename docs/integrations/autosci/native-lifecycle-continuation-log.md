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

### Step 23 Result

| Check | Status | Evidence |
|---|---|---|
| Model response shape | ok | `autosci_model_response.v1` normalization now accepts `outputs.ideas` with required evidence ids, while preserving answer/summary support for ask/check. |
| `/ideate` model-command path | ok | `generate_ideas` uses explicit model evidence/command output when it returns valid ideas; invalid/failed model output is marked inconclusive and does not count as model brainstorm parity. |
| Route metadata | ok | `feature_parity_routes.v1.json` now states explicit model-command/model-evidence brainstorming is wired, without upgrading `coverage_status`. |
| Targeted test | ok | `test_autosci_skill_shim_ideate_uses_model_command_for_brainstorm`: passed. |
| Related tests | ok | Ideate/novelty targeted group: 4 passed; idea gate + feature parity gate: 12 passed. |
| Inventory | ok | `/tmp/autosci-parity-step23.json`: 28 routed, 0 missing, 0 full, 17 partial, 11 gated. |

## Next Planned Step - Novelty Write Test Network Isolation

| Field | Value |
|---|---|
| Planned files | `harness/plugins/autosci/tests/test_autosci_skill_shim.py`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Intent | Make the `without external evidence` novelty write-back test deterministic by disabling network fetch for that test. |
| Out of scope | Do not change default online novelty behavior. |
| Risk | The test should still prove write-back blocks when external novelty evidence is unavailable. |

### Step 24 Result

| Check | Status | Evidence |
|---|---|---|
| Test isolation | ok | The missing-external-evidence novelty write-back test now sets `AUTOSCI_DISABLE_NETWORK_FETCH=1`, so it validates the unavailable evidence branch even when live network/provider access exists. |
| Targeted test | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest ...test_autosci_skill_shim_novelty_write_skips_without_external_evidence -q`: 1 passed. |
| Full shim suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q`: 81 passed outside sandbox because one provider test binds `127.0.0.1`. |
| Scientific evaluator suite | ok | Latest post-Step 23 run: 78 passed. |
| Full parity claim | warn | Still not honest: explicit model-command ideation improves parity, but audited provider-backed dual-model ideation and provider/runtime execution remain partial/gated. |

## Next Planned Step - Wiki Experiment Status State Mapping

| Field | Value |
|---|---|
| Planned files | `harness/plugins/autosci/bin/autosci_bridge.py`, `harness/plugins/autosci/tests/test_autosci_skill_shim.py`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Intent | Map common AutoSci wiki experiment statuses such as `collected`, `collect-ready`, and `ready` into the constrained `experiment_status.v1` state enum. |
| Out of scope | Do not execute collect/deploy or mutate experiment state. |
| Risk | `collect-ready` must not be overstated as completed results; only `collected` should map to completed. |

### Step 25 Result

| Check | Status | Evidence |
|---|---|---|
| Status mapping | ok | `collected` now maps to `completed`; `collect-ready` and `ready` map to `running`; planned/failed/abandoned variants map into valid ABI states. |
| No execution/mutation | ok | Mapping is used only by wiki-backed `monitor_experiment` read mode. |
| Targeted tests | ok | `test_autosci_skill_shim_exp_status_pipeline_reads_wiki_experiment_state`, `test_autosci_skill_shim_exp_status_normalizes_native_wiki_states`, and experiment status gate tests: 6 passed. |
| Full shim suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q`: 84 passed outside sandbox because one provider test binds `127.0.0.1`. |
| Scientific evaluator suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q`: 78 passed. |
| Strict runtime binding audit | ok | `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json`: 27 nodes, 2 workflows, 0 issues. |
| Feature parity inventory | ok | `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step25.json`: 28 routed, 0 missing, 0 full, 17 partial, 11 gated. |
| Full parity claim | warn | Still not honest: this closes a status-read gap, but provider/approval-gated execution evidence is still required for full native parity. |

## Next Planned Step - Research Scheduler Lifecycle Entry

| Field | Value |
|---|---|
| Planned files | `harness/plugins/autosci/bin/autosci_skill_shim.py`, `harness/plugins/autosci/config/feature_parity_routes.v1.json`, `harness/plugins/autosci/tests/test_autosci_skill_shim.py`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Intent | Add an explicit `$research` scheduler lifecycle run path that dispatches the existing scientific lifecycle smoke through `operator_runtime` and feeds its `scientific_lifecycle.v1` summary back into the research bridge. |
| Out of scope | Do not make fixture-mode scheduler execution implicit, do not claim full parity, and do not bypass approval/provider requirements for external source, experiment, Review LLM, or compile evidence. |
| Risk | The new path must remain opt-in and must preserve failure/blocking state rather than converting a failed scheduler run into a successful pipeline projection. |

### Step 26 Result

| Check | Status | Evidence |
|---|---|---|
| Explicit scheduler entry | ok | `$research --scheduler-run` now invokes `tools/run_scientific_lifecycle_smoke.py` with the active `HARNESS_DIR`, prepares isolated harness resource links when needed, and attaches the generated `scientific_lifecycle.v1` summary to the research bridge as `lifecycle_summary`. |
| Blocked external nodes preserved | ok | `$research --scheduler-run --scheduler-include-blocked-external` records `report_plan` and `publication_produce` as blocked scheduler nodes instead of marking the pipeline complete. |
| Route truthfulness | ok | `feature_parity_routes.v1.json` documents the explicit scheduler-run path while keeping `/research` at `coverage_status: partial`. |
| Targeted tests | ok | `$research` supplied-summary, scheduler-run blocked-summary, and lifecycle blocked-node smoke tests: 3 passed. |
| Full shim suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q`: 85 passed outside sandbox because one provider test binds `127.0.0.1`. |
| Scientific evaluator suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q`: 78 passed. |
| Strict runtime binding audit | ok | `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json`: 27 nodes, 2 workflows, 0 issues. |
| Feature parity inventory | ok | `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step26.json`: 28 routed, 0 missing, 0 full, 17 partial, 11 gated. |
| Full parity claim | warn | Still not honest: this closes an explicit scheduler-entry gap, but full native parity still requires non-fixture provider/source evidence, durable human gates, and approved long-running experiment/publication stage runners. |

## Next Planned Step - Scheduler Durable Human Gates

| Field | Value |
|---|---|
| Planned files | `harness/tools/run_scientific_lifecycle_smoke.py`, `harness/plugins/autosci/bin/autosci_skill_shim.py`, `harness/plugins/autosci/bin/autosci_bridge.py`, `harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py`, `harness/plugins/autosci/tests/test_autosci_skill_shim.py`, `harness/plugins/autosci/config/feature_parity_routes.v1.json`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Intent | Represent AutoSci idea/results human approval pauses as scheduler-visible blocked nodes for explicit lifecycle runs. |
| Out of scope | Do not auto-approve human gates, do not change default lifecycle smoke behavior, and do not mark `/research` full parity. |
| Risk | Missing approvals must stop downstream stages instead of allowing experiment or publication stages to run past an unapproved human gate. |

### Step 27 Result

| Check | Status | Evidence |
|---|---|---|
| Human gate nodes | ok | `run_scientific_lifecycle_smoke.py` now models `idea_acceptance_gate` and `results_acceptance_gate` as scheduler-visible lifecycle nodes. |
| Durable approval evidence | ok | Supplying `--idea-approval-ref` or `--results-approval-ref` writes completed `workflow_evolution.v1` gate evidence with approval refs, artifact hashes, and gate results. |
| Missing approval behavior | ok | With human gates enabled, the lifecycle stops at the missing gate and records a blocked node with required evidence/unblock condition; downstream experiment/publication stages do not run past the gate. |
| `$research` shim passthrough | ok | `$research --scheduler-run --scheduler-include-human-gates` passes human gate options to the scheduler lifecycle runner and records the blocked/passed gate state in the skill payload. |
| Targeted tests | ok | Human gate lifecycle smoke and `$research` shim human-gate regression: 2 passed; broader research scheduler group: 3 passed. |
| Lifecycle smoke suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py -q`: 6 passed. |
| Full shim suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q`: 86 passed outside sandbox because one provider test binds `127.0.0.1`. |
| Scientific evaluator suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q`: 79 passed. |
| Strict runtime binding audit | ok | `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json`: 27 nodes, 2 workflows, 0 issues. |
| Feature parity inventory | ok | `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step27.json`: 28 routed, 0 missing, 0 full, 17 partial, 11 gated. |
| Full parity claim | warn | Still not honest: durable gate state is now represented, but non-fixture source/provider evidence and approved long-running experiment/publication execution are still required. |

## Next Planned Step - Human Gate Resume

| Field | Value |
|---|---|
| Planned files | `harness/tools/run_scientific_lifecycle_smoke.py`, `harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Intent | Let scheduler lifecycle resume from blocked idea/results human gates using durable approval refs, without rerunning already passed nodes. |
| Out of scope | Do not add external provider execution or publication compile execution in this step. |
| Risk | Resume must not skip the second human gate or rerun completed upstream nodes. |

### Step 28 Result

| Check | Status | Evidence |
|---|---|---|
| Idea gate resume | ok | `run_scientific_lifecycle_smoke.py --resume-summary ... --idea-approval-ref ...` now records approval evidence, removes the blocked idea gate, and resumes at experiment design without rerunning upstream nodes. |
| Results gate resume | ok | A second resume with `--results-approval-ref ...` records results approval evidence and continues through report draft/artifact review/memory final/workflow evolve before blocking on external report plan/compile evidence. |
| No upstream rerun | ok | Resume regression asserts the original `literature_discover` artifact path is unchanged after both human-gate resumes. |
| Targeted test | ok | `test_scientific_lifecycle_smoke_resumes_human_gate_pauses`: passed. |
| Lifecycle smoke suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py -q`: 7 passed. |
| Scientific evaluator suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q`: 80 passed. |
| Strict runtime binding audit | ok | `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json`: 27 nodes, 2 workflows, 0 issues. |
| Feature parity inventory | ok | `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step28.json`: 28 routed, 0 missing, 0 full, 17 partial, 11 gated. |
| Full parity claim | warn | Still not honest: human gate resume is now covered, but non-fixture source/provider, real experiment deploy/collect, and full publication execution remain partial/gated. |

## Next Planned Step - Research Scheduler Strict Source Evidence Passthrough

| Field | Value |
|---|---|
| Planned files | `harness/plugins/autosci/bin/autosci_skill_shim.py`, `harness/plugins/autosci/tests/test_autosci_skill_shim.py`, `harness/plugins/autosci/config/feature_parity_routes.v1.json`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Intent | Pass `$research --scheduler-run --online` approval/runtime source evidence from the shim into scheduler strict online source flags. |
| Out of scope | Do not execute live network by default, and do not reuse source runtime evidence as experiment or compile evidence. |
| Risk | Missing or invalid source runtime evidence must fail/blocked strict online mode rather than falling back to fixtures. |

### Step 29 Result

| Check | Status | Evidence |
|---|---|---|
| Strict source passthrough | ok | `$research --scheduler-run --online` now maps shim `--approval-ref`, `--allowlist-evidence`, `--runtime-evidence`, `--before-artifact`, and `--after-artifact` into scheduler `--source-*` evidence flags. |
| No fixture fallback | ok | The regression verifies `literature_discover` emits `discover_literature_runtime_verified` with supplied `search_s2` runtime candidates and no fixture candidate id. |
| Route truthfulness | ok | `/research` route limitations now mention strict scheduler source evidence passthrough without changing `coverage_status`. |
| Targeted test | ok | `test_autosci_skill_shim_research_scheduler_online_uses_source_runtime_evidence`: passed. |
| Research scheduler group | ok | `$research` blocked-summary, human-gate, and strict-source scheduler regressions: 3 passed. |
| Full shim suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q`: 87 passed outside sandbox because one provider test binds `127.0.0.1`. |
| Scientific evaluator suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q`: 80 passed. |
| Strict runtime binding audit | ok | `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json`: 27 nodes, 2 workflows, 0 issues. |
| Feature parity inventory | ok | `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step29.json`: 28 routed, 0 missing, 0 full, 17 partial, 11 gated. |
| Full parity claim | warn | Still not honest: source runtime passthrough is wired, but real provider execution plus experiment/publication stage runners remain gated/partial. |

## Next Planned Step - Scheduler Experiment Runtime Evidence Passthrough

| Field | Value |
|---|---|
| Planned files | `harness/tools/run_scientific_lifecycle_smoke.py`, `harness/plugins/autosci/bin/autosci_skill_shim.py`, `harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py`, `harness/plugins/autosci/tests/test_autosci_skill_shim.py`, `harness/plugins/autosci/config/feature_parity_routes.v1.json`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Intent | Let scheduler lifecycle experiment run/monitor consume explicit approved experiment runtime evidence instead of fixture-only experiment output. |
| Out of scope | Do not execute arbitrary experiment commands by default, and do not claim remote/long-running parity without approved executor evidence. |
| Risk | Source runtime evidence and experiment runtime evidence must remain separate so source-fetch approval cannot satisfy experiment execution. |

### Step 30 Result

| Check | Status | Evidence |
|---|---|---|
| Scheduler experiment runtime contract | ok | `run_scientific_lifecycle_smoke.py` now accepts `--experiment-approval-ref`, `--experiment-runtime-evidence`, `--experiment-allowlist-evidence`, `--experiment-before-artifact`, and `--experiment-after-artifact`. |
| Experiment run/monitor passthrough | ok | When experiment runtime evidence is supplied, scheduler `experiment_run` and `experiment_monitor` use `execution_mode: human_approved` plus experiment-specific approval/runtime artifacts instead of fixture experiment output. |
| `$research` shim passthrough | ok | `$research --scheduler-run` forwards `--experiment-*` arguments to the scheduler lifecycle runner without reusing source `--runtime-evidence` paths. |
| Route truthfulness | ok | `/research` limitations document experiment runtime passthrough while keeping `coverage_status: partial`. |
| Targeted tests | ok | `test_scientific_lifecycle_smoke_uses_experiment_runtime_evidence` and `test_autosci_skill_shim_research_scheduler_uses_experiment_runtime_evidence`: 2 passed. |
| Syntax/config checks | ok | `py_compile` for modified Python files and `json.tool` for `feature_parity_routes.v1.json`: passed. |
| Lifecycle smoke suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py -q`: 8 passed. |
| Scientific evaluator suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q`: 81 passed. |
| Full shim suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q`: 88 passed outside sandbox because the provider test binds `127.0.0.1`; the sandboxed run had the same single localhost-bind permission failure. |
| Strict runtime binding audit | ok | `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json`: 27 nodes, 2 workflows, 0 issues. |
| Feature parity inventory | ok | `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step30.json`: 28 routed, 0 missing, 0 full, 17 partial, 11 gated. |
| Full parity claim | warn | Still not honest: scheduler experiment runtime evidence can now be supplied and verified, but live provider execution, long-running deploy/status/collect runners, and publication execution remain partial/gated. |

## Next Planned Step - Scheduler Approved Experiment Executor

| Field | Value |
|---|---|
| Planned files | `harness/tools/run_scientific_lifecycle_smoke.py`, `harness/plugins/autosci/bin/autosci_skill_shim.py`, `harness/plugins/autosci/bin/autosci_bridge.py`, `harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py`, `harness/plugins/autosci/tests/test_autosci_skill_shim.py`, `harness/plugins/autosci/config/feature_parity_routes.v1.json`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Intent | Let explicit scheduler experiment runs execute an allowlisted approved command and feed generated runtime/result evidence into downstream monitor/claim/report stages. |
| Out of scope | Do not execute by default, do not allow unapproved commands, and do not claim remote/session parity until remote runners are separately audited. |
| Risk | The execute-approved path must require approval, allowlist, before/after evidence, and an explicit scheduler/shim flag. |

### Step 31 Result

| Check | Status | Evidence |
|---|---|---|
| Approved scheduler executor flag | ok | `run_scientific_lifecycle_smoke.py` accepts `--experiment-execute-approved` and `--experiment-executor-timeout-seconds`; default scheduler runs still do not execute experiment commands. |
| Shim passthrough | ok | `$research --scheduler-run` forwards `--experiment-execute-approved` and timeout settings to the scheduler lifecycle runner. |
| Runtime ABI mapping | ok | `autosci_bridge.py` now lifts executor-generated `metrics`, `outcome`, and `logs` into `autosci_runtime_evidence.v1` fields consumed by `_approval_semantic_runtime`. |
| Downstream monitor collection | ok | When the executor generates result evidence, scheduler `experiment_monitor` consumes the generated `experiment_result.v1` and reports completed state. |
| Route truthfulness | ok | `/research` limitations document the approved local executor path while keeping `coverage_status: partial`. |
| Targeted tests | ok | `test_scientific_lifecycle_smoke_executes_approved_experiment_command` and `test_autosci_skill_shim_research_scheduler_executes_approved_experiment_command`: 2 passed after the runtime ABI fix. |
| Syntax/config checks | ok | `py_compile` for modified Python files and `json.tool` for `feature_parity_routes.v1.json`: passed. |
| Lifecycle smoke suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py -q`: 9 passed. |
| Scientific evaluator suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q`: 82 passed. |
| Full shim suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q`: 89 passed outside sandbox; sandboxed run still cannot bind the local provider test to `127.0.0.1`. |
| Strict runtime binding audit | ok | `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json`: 27 nodes, 2 workflows, 0 issues. |
| Feature parity inventory | ok | `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step31.json`: 28 routed, 0 missing, 0 full, 17 partial, 11 gated. |
| Full parity claim | warn | Still not honest: approved local experiment execution is now scheduler-visible, but remote/session runners, live provider evidence, and publication execution remain partial/gated. |

## Next Planned Step - Scheduler Approved Publication Compile

| Field | Value |
|---|---|
| Planned files | `harness/tools/run_scientific_lifecycle_smoke.py`, `harness/plugins/autosci/bin/autosci_skill_shim.py`, `harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py`, `harness/plugins/autosci/tests/test_autosci_skill_shim.py`, `harness/plugins/autosci/config/feature_parity_routes.v1.json`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Intent | Let scheduler `publication_produce` consume compile-specific approval/runtime evidence or execute an approved allowlisted TeX command, producing verified PDF/runtime evidence. |
| Out of scope | Do not execute compile by default, do not reuse source/experiment approval evidence, and do not claim submission/anonymity parity yet. |
| Risk | Compile approval evidence must stay separate from source and experiment evidence. |

### Step 32 Result

| Check | Status | Evidence |
|---|---|---|
| Compile-specific scheduler flags | ok | `run_scientific_lifecycle_smoke.py` accepts `--compile-approval-ref`, `--compile-runtime-evidence`, `--compile-allowlist-evidence`, `--compile-before-artifact`, `--compile-after-artifact`, `--compile-execute-approved`, and timeout flags for `publication_produce`. |
| Shim passthrough | ok | `$research --scheduler-run --scheduler-dispatch-external-evidence` forwards compile-specific evidence/execution flags without reusing source or experiment contracts. |
| Approved compile execution | ok | Scheduler publication compile can run an allowlisted fake `latexmk`, generate `main.pdf`, emit `compile_runtime_evidence_json`, and pass runtime semantic verification. |
| Route truthfulness | ok | `/research` limitations document compile-specific runtime evidence/execution while keeping `coverage_status: partial`. |
| Targeted tests | ok | `test_scientific_lifecycle_smoke_executes_approved_publication_compile` and `test_autosci_skill_shim_research_scheduler_executes_approved_publication_compile`: 2 passed. |
| Syntax/config checks | ok | `py_compile` for modified Python files and `json.tool` for `feature_parity_routes.v1.json`: passed. |
| Lifecycle smoke suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py -q`: 10 passed. |
| Scientific evaluator suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q`: 83 passed. |
| Full shim suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q`: 90 passed outside sandbox; sandboxed run still cannot bind the local provider test to `127.0.0.1`. |
| Strict runtime binding audit | ok | `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json`: 27 nodes, 2 workflows, 0 issues. |
| Feature parity inventory | ok | `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step32.json`: 28 routed, 0 missing, 0 full, 17 partial, 11 gated. |
| Full parity claim | warn | Still not honest: scheduler publication compile can now execute approved local TeX commands, but submission/anonymity checks, live provider evidence, and remote/session experiment runners remain partial/gated. |

## Next Planned Step - Publication Submission Checklist Truthfulness

| Field | Value |
|---|---|
| Planned files | `harness/plugins/autosci/bin/autosci_bridge.py`, `harness/plugins/autosci/tests/test_autosci_skill_shim.py`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Intent | Add explicit paper compile checklist rows for anonymity, page limit, font size, and `[UNCONFIRMED]` markers without pretending unavailable checks passed. |
| Out of scope | Do not add PDF font parsing or venue-specific submission rules unless verified evidence is supplied. |
| Risk | Missing page/font evidence must be `warn`/unconfirmed, not a deterministic pass. |

### Step 33 Result

| Check | Status | Evidence |
|---|---|---|
| Submission checklist rows | ok | `paper_compile_checklist.json` now includes `submission_checks` for `unconfirmed_marker_scan`, `anonymity_check`, `page_limit_check`, and `font_size_check`. |
| Truthful unconfirmed handling | ok | Missing page/font evidence is reported as `warn`; `[UNCONFIRMED]` source markers and non-anonymous author blocks are surfaced as warnings rather than silently passing. |
| Diagnostics rendering | ok | `paper_compile_diagnostics.md` renders a dedicated `Submission Checks` section. |
| Targeted test | ok | `test_autosci_skill_shim_paper_compile_checklist_records_submission_checks`: passed. |
| Full shim suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q`: 91 passed outside sandbox; sandboxed run cannot bind the local provider test to `127.0.0.1`. |
| Strict runtime binding audit | ok | `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json`: 27 nodes, 2 workflows, 0 issues. |
| Feature parity inventory | ok | `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step33.json`: 28 routed, 0 missing, 0 full, 17 partial, 11 gated. |
| Full parity claim | warn | Still not honest: checklist truthfulness improved, but live provider evidence and remote/session experiment lifecycle remain partial/gated. |

## Next Planned Step - Remote Helper Runtime Evidence Assimilation

| Field | Value |
|---|---|
| Planned files | `harness/plugins/autosci/bin/autosci_bridge.py`, `harness/plugins/autosci/tests/test_autosci_skill_shim.py`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Intent | Let approved experiment commands that invoke `tools/remote.py launch` feed its generated `runtime_evidence_path` into the experiment approval contract. |
| Out of scope | Do not add real SSH/session execution; this only assimilates approved helper evidence produced by an allowlisted command. |
| Risk | Remote helper evidence must be an existing runtime evidence file; stdout alone must not be treated as completed experiment evidence. |

### Step 34 Result

| Check | Status | Evidence |
|---|---|---|
| Remote helper stdout parsing | ok | `autosci_bridge.py` now recognizes `autosci_remote_cli.v1` as a pointer/control payload, not as experiment result evidence. |
| Runtime evidence assimilation | ok | Existing `runtime_evidence_path` files emitted by `tools/remote.py launch` are appended to the approval contract and consumed by `_approval_semantic_runtime`. |
| False-success guard | ok | Remote helper stdout alone leaves the local bridge runtime result uncollected; completion still requires a readable runtime evidence file with collected results/metrics. |
| Targeted tests | ok | `test_autosci_skill_shim_exp_run_assimilates_remote_helper_runtime_evidence` and `test_autosci_skill_shim_exp_run_rejects_remote_helper_stdout_without_runtime_evidence`: 2 passed. |
| Syntax checks | ok | `env PYTHONPATH=harness .venv/bin/python -m py_compile harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/tests/test_autosci_skill_shim.py`: passed. |
| Full shim suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q`: 93 passed outside sandbox; local provider test still requires binding `127.0.0.1`. |
| Strict runtime binding audit | ok | `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json`: 27 nodes, 2 workflows, 0 issues. |
| Feature parity inventory | ok | `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step34.json`: 28 routed, 0 missing, 0 full, 17 partial, 11 gated. |
| Full parity claim | warn | Still not honest: remote helper evidence is assimilated, but true SSH/session lifecycle, live provider runs, and remaining publication parity proof are still partial/gated. |

## Next Planned Step - Approved Remote Collect Execution

| Field | Value |
|---|---|
| Planned files | `harness/plugins/autosci/bin/autosci_bridge.py`, `harness/plugins/autosci/tests/test_autosci_skill_shim.py`, `harness/plugins/autosci/config/feature_parity_routes.v1.json`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Intent | Let `$exp-run --collect --execute-approved` run an approved `tools/remote.py pull-results` style command, convert collected result files into runtime evidence, and reuse semantic verification/wiki mutation. |
| Out of scope | Do not add SSH/session transport or exactly-once collection ledger in this step. |
| Risk | Collection must require approval, allowlist, before artifact, collected files, and semantic runtime verification; empty stdout or empty result directories must not pass. |

### Step 35 Result

| Check | Status | Evidence |
|---|---|---|
| Approved collect execution | ok | `monitor_experiment` can execute an approved/allowlisted collect command when `$exp-run --collect --execute-approved` is used. |
| Pull-results assimilation | ok | Collected files from `tools/remote.py pull-results` stdout are converted into `autosci_runtime_evidence.v1` and verified by `_approval_semantic_runtime`. |
| Empty collection guard | ok | Empty result directories generate runtime evidence but remain `inconclusive`; they do not pass semantic verification or mutate wiki as completed. |
| Route truthfulness | ok | `exp-run` and `exp-status` limitations now mention approved pull-results collection while keeping remote/session and exactly-once parity as partial. |
| Targeted tests | ok | `test_autosci_skill_shim_exp_collect_uses_verified_runtime_evidence`, `test_autosci_skill_shim_exp_collect_executes_approved_remote_pull_results`, and `test_autosci_skill_shim_exp_collect_rejects_empty_remote_pull_results`: 3 passed. |
| Syntax/config checks | ok | `py_compile` for modified Python files and `json.tool` for `feature_parity_routes.v1.json`: passed. |
| Full shim suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q`: 95 passed outside sandbox; local provider test still requires binding `127.0.0.1`. |
| Strict runtime binding audit | ok | `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json`: 27 nodes, 2 workflows, 0 issues. |
| Feature parity inventory | ok | `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step35.json`: 28 routed, 0 missing, 0 full, 17 partial, 11 gated. |
| Full parity claim | warn | Still not honest: approved local pull-results collection is wired, but true SSH/session status, exactly-once collection ledger, live provider runs, and remaining publication proof are still partial/gated. |

## Next Planned Step - Exactly-Once Collection Ledger

| Field | Value |
|---|---|
| Planned files | `harness/plugins/autosci/bin/autosci_bridge.py`, `harness/plugins/autosci/tests/test_autosci_skill_shim.py`, `harness/plugins/autosci/config/feature_parity_routes.v1.json`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Intent | Add a durable local collection identity/hash ledger so repeated approved collect runs reuse existing accepted evidence instead of duplicating collection state. |
| Out of scope | Do not add distributed locks or remote scheduler resume semantics in this step. |
| Risk | Duplicate collection must still return completed status from existing evidence, but must not append duplicate wiki log/graph mutations. |

### Step 36 Result

| Check | Status | Evidence |
|---|---|---|
| Collection identity ledger | ok | Approved collect runs now write `wiki/collections/collection-ledger.json` with experiment id, collected file hashes, evidence ids, and collection identity. |
| Duplicate collection reuse | ok | Repeated approved collect runs with the same experiment/file hashes return completed status with `collection_duplicate=True` and skip duplicate wiki log/graph mutation. |
| Runtime evidence fields | ok | Collect runtime evidence now includes `collection_identity`, `collection_duplicate`, and `collection_ledger_path`. |
| Route truthfulness | ok | `exp-run`/`exp-status` limitations now distinguish local collection ledger support from distributed remote/session exactly-once parity. |
| Targeted tests | ok | Collect runtime, pull-results execution, empty collection rejection, and exactly-once ledger reuse tests: 4 passed. |
| Syntax/config checks | ok | `py_compile` for modified Python files and `json.tool` for `feature_parity_routes.v1.json`: passed. |
| Full shim suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q`: 96 passed outside sandbox; local provider test still requires binding `127.0.0.1`. |
| Strict runtime binding audit | ok | `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json`: 27 nodes, 2 workflows, 0 issues. |
| Feature parity inventory | ok | `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step36.json`: 28 routed, 0 missing, 0 full, 17 partial, 11 gated. |
| Full parity claim | warn | Still not honest: local exactly-once collection is covered, but true remote/session status polling, live provider runs, scheduler resume, and remaining publication proof are still partial/gated. |

## Next Planned Step - Persistent Experiment Session Registry

| Field | Value |
|---|---|
| Planned files | `harness/plugins/autosci/bin/autosci_bridge.py`, `harness/plugins/autosci/tests/test_autosci_skill_shim.py`, `harness/plugins/autosci/config/feature_parity_routes.v1.json`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Intent | Persist approved launch/session records and let `$exp-status` read them when no completed wiki experiment state exists. |
| Out of scope | Do not implement SSH/screen polling or scheduler resume replay yet. |
| Risk | Registry status must not be overstated as collected results; waiting/running sessions should remain non-completed until runtime/collect evidence verifies results. |

### Step 37 Result

| Check | Status | Evidence |
|---|---|---|
| Session registry write | ok | Approved remote-launch style stdout now records `wiki/experiments/session-registry.json` with experiment id, run dir, runtime evidence path, remote CLI status, and session state. |
| Status read from registry | ok | `$exp-status <experiment>` can report `running` from the session registry when wiki state is only planned/running/non-completed. |
| Truthful non-collection status | ok | Registry status limitations state that no remote process was polled and no results were collected in the status call. |
| Route truthfulness | ok | `exp-status` limitations now distinguish local session registry status from missing live remote process polling. |
| Targeted test | ok | `test_autosci_skill_shim_exp_status_reads_persistent_session_registry`: passed. |
| Syntax/config checks | ok | `py_compile` for modified Python files and `json.tool` for `feature_parity_routes.v1.json`: passed. |
| Full shim suite | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q`: 97 passed outside sandbox; local provider test still requires binding `127.0.0.1`. |
| Strict runtime binding audit | ok | `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json`: 27 nodes, 2 workflows, 0 issues. |
| Feature parity inventory | ok | `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step37.json`: 28 routed, 0 missing, 0 full, 17 partial, 11 gated. |
| Full parity claim | warn | Still not honest: persistent local session status is covered, but live remote polling, scheduler resume replay, live provider runs, and remaining publication proof are still partial/gated. |
