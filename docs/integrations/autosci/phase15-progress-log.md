# AutoSci Phase 15 Progress Log

Logged: 2026-06-25 EDT
Branch: `feature/autosci-solar-native`

## Scope

Phase 15 is the scheduler-native full lifecycle and resume/recovery phase. The
current continuation begins from a partial migration: scientific workflow files
exist and pass structural architecture validation, but `$research` has not yet
been proven through the real TaskGraph scheduler and operator runtime chain.

## Current Status

| Item | Status | Evidence |
|---|---|---|
| Full lifecycle workflow file | ok | `harness/workflows/scientific_research_lifecycle_full_v1.json` exists and passes architecture guard. |
| Resume workflow file | ok | `harness/workflows/scientific_research_resume_v1.json` exists and passes architecture guard. |
| Runtime scheduler execution proof | warn | Sixteen bounded core nodes now dispatch through `operator_runtime.submit` and `operatord`; full `$research` graph is not yet proven. |
| Empty runtime-result rejection | ok | `lifecycle_runtime_gate.py` rejects missing `job_id`, `node_results`, `gate_results`, missing artifacts, hash mismatch, bridge-owned lifecycle, and black-box runner summaries. |
| Durable human gates | pending | Not yet implemented as scheduler state. |
| External wait/resume | pending | Not yet implemented as recoverable scheduler state. |

## Phase 15 Acceptance Target

```text
TaskGraph submission
  -> graph scheduler
  -> logical-to-physical resolution
  -> registered host/worker dispatch
  -> bounded backend action
  -> Evidence ABI artifact
  -> runtime gate
  -> persisted node/gate state
  -> parent closure advances or remains blocked correctly
```

## Step 0 Verification

| Command | Result |
|---|---|
| `python3 harness/lib/architecture_guard.py validate --graph harness/workflows/scientific_research_lifecycle_full_v1.json --strict` | ok |
| `python3 harness/lib/architecture_guard.py validate --graph harness/workflows/scientific_research_resume_v1.json --strict` | ok |
| `.venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-baseline.json` | ok: 0 full, 17 partial, 11 gated. |

## Remaining Phase 15 Blockers

| Blocker | Status | Required next proof |
|---|---|---|
| `$research` bypasses scheduler-native execution | error | A run whose nodes are submitted and dispatched through scheduler/operator runtime. |
| Lifecycle gate accepts structure as lifecycle evidence | ok | Contract and runtime gates are split; runtime summaries require concrete node/gate maps and artifact hashes. |
| Physical/local host chain is not audited | ok | `audit_scientific_runtime_bindings.py --strict --json` checks workflow -> logical -> physical -> host -> bridge action -> schema -> gate with 0 issues. |
| Human and external wait states are missing | pending | Durable gate/wait artifacts and resume CLI in later slice. |

## Step 4 Verification

| Command | Result |
|---|---|
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_scientific_node_runtime_smoke.py -q` | ok: 1 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 66 passed |
| `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json` | ok: 27 nodes, 0 issues |

## Step 5 Verification

| Command | Result |
|---|---|
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_scientific_node_runtime_smoke.py harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py harness/tests/evaluators/scientific/test_lifecycle_runtime_gate.py -q` | ok: 11 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 67 passed |
| `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json` | ok: 27 nodes, 0 issues |

## Step 6 Verification

| Command | Result |
|---|---|
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_scientific_node_runtime_smoke.py harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py harness/tests/evaluators/scientific/test_lifecycle_runtime_gate.py -q` | ok: 11 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 67 passed |
| `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json` | ok: 27 nodes, 0 issues |

## Step 7 Verification

| Command | Result |
|---|---|
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_scientific_node_runtime_smoke.py harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py harness/tests/evaluators/scientific/test_lifecycle_runtime_gate.py -q` | ok: 11 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 67 passed |
| `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json` | ok: 27 nodes, 0 issues |

## Step 8 Verification

| Command | Result |
|---|---|
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_scientific_runtime_binding_audit.py harness/tests/evaluators/scientific/test_scientific_node_runtime_smoke.py harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py -q` | ok: 5 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 68 passed |
| `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json` | ok: 27 nodes, 0 issues |

## Step 9 Verification

| Command | Result |
|---|---|
| `python3 -m json.tool harness/config/physical-operators.json` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py -q` | ok: 1 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_scientific_runtime_binding_audit.py harness/tests/evaluators/scientific/test_scientific_node_runtime_smoke.py harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py -q` | ok: 5 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 68 passed |
| `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json` | ok: 27 nodes, 0 issues |

## Step 10 Verification

| Command | Result |
|---|---|
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py -q` | ok: 1 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_scientific_runtime_binding_audit.py harness/tests/evaluators/scientific/test_scientific_node_runtime_smoke.py harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py -q` | ok: 5 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 68 passed |
| `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json` | ok: 27 nodes, 0 issues |

## Step 11 Verification

| Command | Result |
|---|---|
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_lifecycle_runtime_gate.py harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py -q` | ok: 13 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 71 passed |
| `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json` | ok: 27 nodes, 0 issues |

## Next Phase 15 Slice

| Field | Value |
|---|---|
| Planned files | `harness/config/physical-operators.json`, `harness/tools/run_scientific_node_smoke.py`, `harness/tools/run_scientific_lifecycle_smoke.py`, `harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Goal | Add durable blocked/waiting runtime states for report planning and publication production when required external evidence is unavailable. |
| Non-goal | Do not advertise full `$research` parity until the complete graph, wait/resume gates, and publication path are scheduler-native. |

## Current Remaining Blockers

| Blocker | Status | Required next proof |
|---|---|---|
| Report planning Review LLM | blocked | Completed Review LLM-backed `artifact_review.v1`, then scheduler-dispatched `report_plan` passes. |
| Publication compile/PDF | blocked | `compile_paper` emits passed `publication_bundle.v1` with existing compile/PDF artifacts or approved runtime evidence. |
| Online source evidence | warn | Run discovery/source fetching with network-enabled, multi-source evidence instead of fixture/local fallback. |
| Resume after blocked state | pending | CLI/scheduler path that resumes blocked `report_plan` or `publication_produce` after evidence appears. |

## Step 12 Planned Files

| Field | Value |
|---|---|
| Planned files | `harness/tools/run_scientific_lifecycle_smoke.py`, `harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Goal | Add scheduler-native resume mode for blocked `report_plan` and `publication_produce` after caller-supplied Review LLM and compile/PDF evidence appears. |
| Non-goal | Do not synthesize Review LLM or PDF evidence inside production runtime; supplied evidence must be explicit input. |

## Step 12 Verification

| Command | Result |
|---|---|
| `env PYTHONPATH=harness .venv/bin/python -m py_compile harness/tools/run_scientific_lifecycle_smoke.py harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py -q` | ok: 3 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_lifecycle_runtime_gate.py harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py -q` | ok: 14 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 72 passed |
| `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json` | ok: 27 nodes, 2 workflows, 0 issues |

## Current Remaining Blockers After Step 12

| Blocker | Status | Required next proof |
|---|---|---|
| Report planning Review LLM wait/resume | ok | Blocked state resumes through scheduler after explicit completed Review LLM evidence is supplied. |
| Publication compile/PDF wait/resume | ok | Blocked state resumes through scheduler after explicit compile target with LaTeX/PDF evidence is supplied. |
| Online source evidence | warn | Run discovery/source fetching with network-enabled, multi-source evidence instead of fixture/local fallback. |
| Full `$research` parity claim | pending | Complete non-fixture source evidence proof plus end-to-end full graph evidence without remaining warnings. |

## Step 13 Planned Files

| Field | Value |
|---|---|
| Planned files | `harness/tools/run_scientific_lifecycle_smoke.py`, `harness/evaluators/scientific/literature_discovery_gate.py`, `harness/tests/evaluators/scientific/test_literature_discovery_gate.py`, `harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Goal | Expose strict online/non-fixture discovery proof for lifecycle smoke and prevent fixture candidates from satisfying full-parity source evidence. |
| Non-goal | Do not make default offline smoke depend on network availability. |

## Step 13 Verification

| Command | Result |
|---|---|
| `env PYTHONPATH=harness .venv/bin/python -m py_compile harness/tools/run_scientific_lifecycle_smoke.py harness/evaluators/scientific/literature_discovery_gate.py harness/tests/evaluators/scientific/test_literature_discovery_gate.py harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_literature_discovery_gate.py harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py -q` | ok: 7 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 76 passed |
| `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json` | ok: 27 nodes, 2 workflows, 0 issues |

## Current Remaining Blockers After Step 13

| Blocker | Status | Required next proof |
|---|---|---|
| Strict online discovery path | ok | CLI and gate now reject fixture evidence for full-parity source claims. |
| Real online source run | blocked | Needs network-enabled execution that returns completed non-fixture online candidates. |
| Full `$research` parity claim | pending | Needs real online source run plus end-to-end full graph evidence using supplied Review LLM and compile/PDF artifacts. |

## Step 14 Planned Files

| Field | Value |
|---|---|
| Planned files | `harness/plugins/autosci/bin/autosci_bridge.py`, `harness/evaluators/scientific/autosci_runtime_evidence_gate.py`, `harness/tools/run_scientific_lifecycle_smoke.py`, `harness/tests/evaluators/scientific/test_autosci_runtime_evidence_gate.py`, `harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Goal | Let strict discovery use supplied approval-gated online source runtime evidence without executing network fetches in the bridge. |
| Non-goal | Do not fabricate live source candidates or weaken runtime evidence validation. |

### Step 14 Scope Correction

| Field | Value |
|---|---|
| Additional file | `harness/schemas/evidence/autosci_runtime_evidence.v1.schema.json` |
| Reason | `discover_literature` must be added to the runtime Evidence ABI action enum for source-fetch runtime evidence to validate. |

## Step 14 Verification

| Command | Result |
|---|---|
| `env PYTHONPATH=harness .venv/bin/python -m py_compile harness/plugins/autosci/bin/autosci_bridge.py harness/evaluators/scientific/autosci_runtime_evidence_gate.py harness/tools/run_scientific_lifecycle_smoke.py harness/tests/evaluators/scientific/test_autosci_runtime_evidence_gate.py harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py` | ok |
| `python3 -m json.tool harness/schemas/evidence/autosci_runtime_evidence.v1.schema.json` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_autosci_runtime_evidence_gate.py harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py -q` | ok: 9 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 77 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_init_uses_verified_runtime_source_manifest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_daily_arxiv_uses_verified_runtime_digest -q` | ok: 2 passed |
| `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json` | ok: 27 nodes, 2 workflows, 0 issues |

## Current Remaining Blockers After Step 14

| Blocker | Status | Required next proof |
|---|---|---|
| Online/source evidence parity path | ok | Strict discovery can use validated supplied runtime source evidence without fixture fallback. |
| End-to-end full lifecycle proof | pending | Need one combined run with strict source evidence, completed Review LLM evidence, compile/PDF target, and no blocked nodes. |
| Full `$research` parity claim | pending | Needs end-to-end full graph evidence plus remaining route truthfulness/audit updates if any coverage status still overclaims. |

## Step 15 Planned Files

| Field | Value |
|---|---|
| Planned files | `harness/tools/run_scientific_lifecycle_smoke.py`, `harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Goal | Prove one scheduler lifecycle run can include strict source runtime evidence, Review LLM-backed report planning, and compile/PDF publication production. |
| Non-goal | Do not auto-pass external nodes when their evidence is absent. |

## Step 15 Verification

| Command | Result |
|---|---|
| `env PYTHONPATH=harness .venv/bin/python -m py_compile harness/tools/run_scientific_lifecycle_smoke.py harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py -q` | ok: 5 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 77 passed |
| `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json` | ok: 27 nodes, 2 workflows, 0 issues |

## Current Remaining Blockers After Step 15

| Blocker | Status | Required next proof |
|---|---|---|
| Single-run full external lifecycle | ok | Strict source runtime, Review LLM, and compile/PDF nodes can pass in one scheduler lifecycle run. |
| Route truthfulness metadata | pending | Recheck AutoSci route coverage statuses so no route claims `full` when it still requires supplied external evidence or runtime approvals. |
| Full `$research` parity claim | warn | Bounded parity proof exists for supplied evidence; full native AutoSci parity still depends on route metadata and real operational evidence availability. |

## Step 16 Verification

| Command | Result |
|---|---|
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py -q` | ok: 4 passed |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step16.json` | ok: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |
| Route config status count | ok: `Counter({'partial': 17, 'gated': 11})` |

## Current Remaining Blockers After Step 16

| Blocker | Status | Required next proof |
|---|---|---|
| Route truthfulness metadata | ok | No route currently overclaims `full`. |
| Capability completion | pending | Partial/gated routes still need real provider/runtime evidence, approved side-effect execution, or route-specific full-parity implementation before statuses can be upgraded. |
| Full `$research` parity claim | warn | Do not claim full parity until the remaining partial/gated route capabilities have operational evidence, not only bounded harness proofs. |

## Step 17 Planned Files

| Field | Value |
|---|---|
| Planned files | `harness/plugins/autosci/bin/autosci_bridge.py`, `harness/plugins/autosci/bin/autosci_skill_shim.py`, `harness/plugins/autosci/tests/test_autosci_skill_shim.py`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Goal | Connect `/research` to scheduler-native `scientific_lifecycle.v1` runtime summaries. |
| Non-goal | Do not accept blocked/inconclusive lifecycle summaries as completed research lifecycle evidence. |

## Step 17 Verification

| Command | Result |
|---|---|
| `env PYTHONPATH=harness .venv/bin/python -m py_compile harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_research_lifecycle_completes_from_scheduler_summary harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_research_lifecycle_completes_from_verified_stage_evidence -q` | ok: 2 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 77 passed |
| `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json` | ok: 27 nodes, 2 workflows, 0 issues |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step17.json` | ok: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |

## Current Remaining Blockers After Step 17

| Blocker | Status | Required next proof |
|---|---|---|
| `/research` consumes scheduler proof | ok | Passed scheduler lifecycle summary can complete `/research` route evidence. |
| Operational full parity | pending | Partial/gated route statuses remain until live providers, approved side effects, and durable external evidence are available per route. |
| Full parity claim | warn | The bounded supplied-evidence path is strong, but full native parity still cannot be honestly claimed for routes that remain provider/approval-gated. |

## Step 18 Planned Files

| Field | Value |
|---|---|
| Planned files | `harness/plugins/autosci/config/feature_parity_routes.v1.json`, `harness/evaluators/scientific/autosci_feature_parity_gate.py`, `harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Goal | Keep route primary tool metadata aligned with configured bridge actions. |
| Non-goal | Do not change coverage statuses in this metadata-only truthfulness fix. |

## Step 18 Verification

| Command | Result |
|---|---|
| `python3 -m json.tool harness/plugins/autosci/config/feature_parity_routes.v1.json` | ok |
| Route primary tool drift scan | ok: no mismatches |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py -q` | ok: 5 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 78 passed |
| `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json` | ok: 27 nodes, 2 workflows, 0 issues |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step18.json` | ok: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |

## Current Remaining Blockers After Step 18

| Blocker | Status | Required next proof |
|---|---|---|
| Route primary tool truthfulness | ok | Gate now prevents configured bridge action drift. |
| Operational/provider parity | pending | Provider/network/approval-gated routes still need real approved runtime evidence before any `full` status claim. |
| Final full parity claim | warn | Not yet honest: route inventory intentionally remains 17 partial and 11 gated. |

## Step 19 Planned Files

| Field | Value |
|---|---|
| Planned files | `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Goal | Recheck whether `$survey --format latex` still fails before touching parser code. |
| Non-goal | Do not change survey generation semantics or claim full survey parity. |

## Step 19 Verification

| Command | Result |
|---|---|
| `env HARNESS_DIR=/tmp/autosci-step19-survey .venv/bin/python harness/plugins/autosci/bin/autosci_skill_shim.py text '$survey --format latex --topic skillgen --run-id step19-survey-format-latex'` | ok: `skill=survey`, `action_count=1`, `execution_status=partial` |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_accepts_survey_format_latex -q` | ok: 1 passed |

## Current Remaining Blockers After Step 19

| Blocker | Status | Required next proof |
|---|---|---|
| `$survey --format latex` parser acceptance | ok | Current shim accepts and propagates the format flag. |
| Citation-backed survey parity | pending | Need real literature/source evidence and citation map coverage before route can move beyond `partial`. |
| Full parity claim | warn | Still blocked by provider/network/approval-gated routes and real publication/experiment evidence. |

## Step 20 Planned Files

| Field | Value |
|---|---|
| Planned files | `harness/plugins/autosci/bin/autosci_bridge.py`, `harness/plugins/autosci/tests/test_autosci_skill_shim.py`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Goal | Improve `$exp-status --pipeline` from unknown schema-only output to read-only status evidence when wiki experiment state exists. |
| Non-goal | No experiment execution, remote collection, or wiki mutation. |

## Step 20 Verification

| Command | Result |
|---|---|
| `env PYTHONPATH=harness .venv/bin/python -m py_compile harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_exp_status_pipeline_runs_monitor_action harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_exp_status_pipeline_reads_wiki_experiment_state -q` | ok: 2 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_experiment_status_gate.py harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py -q` | ok: 7 passed |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step20.json` | ok: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |

## Current Remaining Blockers After Step 20

| Blocker | Status | Required next proof |
|---|---|---|
| `$exp-status --pipeline` action route | ok | Route now runs monitor action. |
| Wiki-backed status read | ok | Existing wiki experiment state can produce passed `experiment_status.v1` evidence without execution or mutation. |
| Runtime collect parity | pending | `--collect` still requires `experiment_result.v1` or approved runtime evidence. |

## Step 21 Planned Files

| Field | Value |
|---|---|
| Planned files | `harness/plugins/autosci/bin/autosci_skill_shim.py`, `harness/plugins/autosci/backends/novelty_review.py`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Goal | Treat absent novelty Review LLM evidence as `unavailable`, not `failed`, by only requesting provider Review LLM for novelty when the user supplies `--review` or explicit Review LLM provider/command/evidence inputs. |
| Non-goal | No synthetic Review LLM verdict and no promotion-grade write-back without completed Review LLM evidence. |

## Step 21 Verification

| Command | Result |
|---|---|
| `env PYTHONPATH=harness .venv/bin/python -m py_compile harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/backends/novelty_review.py` | ok |
| Novelty Review LLM absence/write-back targeted group | ok: 4 formerly failing semantic checks pass inside the 5-test group after Step 22 assertion repair |

## Step 22 Verification

| Command | Result |
|---|---|
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_runs_novelty_target_with_local_sources harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_novelty_defaults_to_online_fetch_when_available harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_novelty_uses_supplied_external_evidence harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_novelty_write_skips_without_external_evidence harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_novelty_write_skips_without_review_llm_evidence -q` | ok: 5 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q` | ok: 80 passed outside sandbox; local provider test requires binding `127.0.0.1` |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 78 passed |
| `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json` | ok: 27 nodes, 2 workflows, 0 issues |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step22.json` | ok: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |

## Current Remaining Blockers After Step 22

| Blocker | Status | Required next proof |
|---|---|---|
| Novelty missing Review LLM semantics | ok | Missing Review LLM is `unavailable`; explicit provider failures can still be `failed`. |
| Novelty write-back promotion gate | ok | Still blocks without completed external novelty provenance and completed Review LLM evidence. |
| Full parity claim | warn | Not yet honest: route inventory remains 17 partial and 11 gated. |

## Step 23 Planned Files

| Field | Value |
|---|---|
| Planned files | `harness/plugins/autosci/bin/autosci_bridge.py`, `harness/plugins/autosci/tests/test_autosci_skill_shim.py`, `harness/plugins/autosci/config/feature_parity_routes.v1.json`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Goal | Add explicit model-command/model-evidence brainstorm support to `/ideate` candidate generation. |
| Non-goal | No implicit provider calls, no deterministic replacement for missing model output, and no `full` route status upgrade. |

## Step 22 Planned Files

| Field | Value |
|---|---|
| Planned files | `harness/plugins/autosci/tests/test_autosci_skill_shim.py`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Goal | Fix the novelty online-fetch test to assert the provider payload URI/archive fields instead of checking a local directory path for `file://`. |
| Non-goal | No product behavior change. |
