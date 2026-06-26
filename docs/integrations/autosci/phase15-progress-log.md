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

## Step 23 Verification

| Command | Result |
|---|---|
| `env PYTHONPATH=harness .venv/bin/python -m py_compile harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `python3 -m json.tool harness/plugins/autosci/config/feature_parity_routes.v1.json` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_ideate_uses_model_command_for_brainstorm -q` | ok: 1 passed |
| Ideate/novelty targeted group | ok: 4 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_idea_gate.py harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py -q` | ok: 12 passed |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step23.json` | ok: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |
| `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json` | ok: 27 nodes, 2 workflows, 0 issues |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 78 passed |

## Current Remaining Blockers After Step 23

| Blocker | Status | Required next proof |
|---|---|---|
| Explicit model brainstorm for `/ideate` | ok | `--model-command`/model evidence can produce idea candidates with source evidence ids. |
| Dual-model native brainstorm parity | pending | Need audited provider-backed Codex/Review LLM runs or supplied evidence for both brainstorm/review roles. |
| Full parity claim | warn | Route inventory remains 17 partial and 11 gated. |

## Step 24 Planned Files

| Field | Value |
|---|---|
| Planned files | `harness/plugins/autosci/tests/test_autosci_skill_shim.py`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Goal | Isolate the novelty write-back missing-external-evidence test from live network/provider availability. |
| Non-goal | No product behavior change; default online novelty fetch remains enabled when available. |

## Step 24 Verification

| Command | Result |
|---|---|
| `env PYTHONPATH=harness .venv/bin/python -m py_compile harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_novelty_write_skips_without_external_evidence -q` | ok: 1 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q` | ok: 81 passed outside sandbox; local provider test requires binding `127.0.0.1` |

## Current Remaining Blockers After Step 24

| Blocker | Status | Required next proof |
|---|---|---|
| Novelty missing-evidence test determinism | ok | Test now disables network for the missing external evidence branch. |
| Operational/provider parity | pending | Live provider/network paths still require real audited evidence before `full` claims. |
| Full parity claim | warn | Still not honest: route inventory remains partial/gated. |

## Step 25 Planned Files

| Field | Value |
|---|---|
| Planned files | `harness/plugins/autosci/bin/autosci_bridge.py`, `harness/plugins/autosci/tests/test_autosci_skill_shim.py`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Goal | Normalize wiki experiment statuses used by native AutoSci into valid `experiment_status.v1` states. |
| Non-goal | No new execution, collection, or mutation behavior. |

## Step 25 Verification

| Command | Result |
|---|---|
| `env PYTHONPATH=harness .venv/bin/python -m py_compile harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_exp_status_pipeline_reads_wiki_experiment_state harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_exp_status_normalizes_native_wiki_states harness/tests/evaluators/scientific/test_experiment_status_gate.py -q` | ok: 6 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q` | ok: 84 passed outside sandbox; local provider test requires binding `127.0.0.1` |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 78 passed |
| `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json` | ok: 27 nodes, 2 workflows, 0 issues |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step25.json` | ok: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |

## Current Remaining Blockers After Step 25

| Blocker | Status | Required next proof |
|---|---|---|
| Wiki experiment status normalization | ok | Native wiki statuses now map into valid status ABI states. |
| Experiment lifecycle full parity | pending | Still needs approved deploy/monitor/collect execution evidence under real local/remote conditions. |
| Full parity claim | warn | Route inventory remains 17 partial and 11 gated. |

## Step 26 Planned Files

| Field | Value |
|---|---|
| Planned files | `harness/plugins/autosci/bin/autosci_skill_shim.py`, `harness/plugins/autosci/config/feature_parity_routes.v1.json`, `harness/plugins/autosci/tests/test_autosci_skill_shim.py`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Goal | Wire an explicit `$research` scheduler lifecycle run into the compatibility shim and attach the resulting `scientific_lifecycle.v1` evidence to the research bridge. |
| Non-goal | No implicit scheduler execution, no provider/network side-effect bypass, and no `full` route status upgrade. |

## Step 26 Verification

| Command | Result |
|---|---|
| `env PYTHONPATH=harness .venv/bin/python -m py_compile harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `python3 -m json.tool harness/plugins/autosci/config/feature_parity_routes.v1.json` | ok |
| `$research --scheduler-run --scheduler-include-blocked-external` targeted shim regression | ok: scheduler summary attached, 18 dispatched nodes recorded, `report_plan`/`publication_produce` blocked |
| `$research` supplied-summary + scheduler blocked-node group | ok: 3 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q` | ok: 85 passed outside sandbox; local provider test requires binding `127.0.0.1` |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 78 passed |
| `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json` | ok: 27 nodes, 2 workflows, 0 issues |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step26.json` | ok: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |

## Current Remaining Blockers After Step 26

| Blocker | Status | Required next proof |
|---|---|---|
| Explicit scheduler entry for `$research` | ok | `$research --scheduler-run` now dispatches the existing lifecycle through `operator_runtime` and feeds the summary to the bridge. |
| Durable human gates | pending | Need scheduler-observed approval states for idea acceptance and results acceptance, not only CLI flags or supplied summaries. |
| Non-fixture full lifecycle | pending | Need online/source provider evidence, Review LLM evidence, real experiment deploy/collect evidence, and compile/PDF evidence in one audited scheduler run. |
| Full parity claim | warn | Route inventory remains 17 partial and 11 gated. |

## Step 27 Planned Files

| Field | Value |
|---|---|
| Planned files | `harness/tools/run_scientific_lifecycle_smoke.py`, `harness/plugins/autosci/bin/autosci_skill_shim.py`, `harness/plugins/autosci/bin/autosci_bridge.py`, `harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py`, `harness/plugins/autosci/tests/test_autosci_skill_shim.py`, `harness/plugins/autosci/config/feature_parity_routes.v1.json`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Goal | Add scheduler-visible blocked nodes for the native AutoSci idea acceptance and results acceptance human gates. |
| Non-goal | No implicit approvals, no default behavior change, and no full-parity status upgrade. |

## Step 27 Verification

| Command | Result |
|---|---|
| `env PYTHONPATH=harness .venv/bin/python -m py_compile harness/tools/run_scientific_lifecycle_smoke.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `python3 -m json.tool harness/plugins/autosci/config/feature_parity_routes.v1.json` | ok |
| Human gate targeted tests | ok: 2 passed |
| `$research` scheduler regression group | ok: 3 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py -q` | ok: 6 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q` | ok: 86 passed outside sandbox; local provider test requires binding `127.0.0.1` |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 79 passed |
| `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json` | ok: 27 nodes, 2 workflows, 0 issues |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step27.json` | ok: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |

## Current Remaining Blockers After Step 27

| Blocker | Status | Required next proof |
|---|---|---|
| Durable human gates | ok | Idea/results approval pauses can now be represented as scheduler-visible blocked or approved nodes. |
| Non-fixture source/provider lifecycle | pending | Need real online/source provider evidence in the scheduler-run path without fixture fallback. |
| Long-running experiment lifecycle | pending | Need approved deploy/status/collect/evaluate state across resume, not only fixture/local runtime evidence. |
| Publication lifecycle | pending | Need full paper plan/draft/review/compile loop with real PDF/submission checks in scheduler state. |
| Full parity claim | warn | Route inventory remains 17 partial and 11 gated. |

## Step 28 Planned Files

| Field | Value |
|---|---|
| Planned files | `harness/tools/run_scientific_lifecycle_smoke.py`, `harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Goal | Add resume support for blocked idea/results human approval gates in the scheduler lifecycle smoke. |
| Non-goal | No external source/provider or publication compile expansion in this step. |

## Step 28 Verification

| Command | Result |
|---|---|
| `env PYTHONPATH=harness .venv/bin/python -m py_compile harness/tools/run_scientific_lifecycle_smoke.py harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py::test_scientific_lifecycle_smoke_resumes_human_gate_pauses -q` | ok: 1 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py -q` | ok: 7 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 80 passed |
| `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json` | ok: 27 nodes, 2 workflows, 0 issues |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step28.json` | ok: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |

## Current Remaining Blockers After Step 28

| Blocker | Status | Required next proof |
|---|---|---|
| Human gate resume | ok | Idea/results gates can block and resume from durable scheduler state without rerunning upstream nodes. |
| Non-fixture source/provider lifecycle | pending | Need strict online/source provider evidence under scheduler-run without fixture fallback. |
| Long-running experiment lifecycle | pending | Need approved deploy/status/collect/evaluate state across resume. |
| Publication lifecycle | pending | Need full paper plan/draft/review/compile loop with real PDF/submission checks. |
| Full parity claim | warn | Route inventory remains 17 partial and 11 gated. |

## Step 29 Planned Files

| Field | Value |
|---|---|
| Planned files | `harness/plugins/autosci/bin/autosci_skill_shim.py`, `harness/plugins/autosci/tests/test_autosci_skill_shim.py`, `harness/plugins/autosci/config/feature_parity_routes.v1.json`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Goal | Let `$research --scheduler-run --online` carry source approval/runtime evidence into the scheduler lifecycle runner's strict source-evidence mode. |
| Non-goal | No live network execution by default and no full-parity status upgrade. |

## Step 29 Verification

| Command | Result |
|---|---|
| `env PYTHONPATH=harness .venv/bin/python -m py_compile harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `python3 -m json.tool harness/plugins/autosci/config/feature_parity_routes.v1.json` | ok |
| `test_autosci_skill_shim_research_scheduler_online_uses_source_runtime_evidence` | ok: 1 passed |
| `$research` scheduler regression group | ok: 3 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q` | ok: 87 passed outside sandbox; local provider test requires binding `127.0.0.1` |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 80 passed |
| `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json` | ok: 27 nodes, 2 workflows, 0 issues |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step29.json` | ok: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |

## Current Remaining Blockers After Step 29

| Blocker | Status | Required next proof |
|---|---|---|
| `$research` strict source passthrough | ok | Scheduler source node can consume supplied approval/runtime evidence under `--online` without fixture fallback. |
| Live provider execution | pending | Need approved provider run evidence rather than only supplied runtime evidence. |
| Long-running experiment lifecycle | pending | Need approved deploy/status/collect/evaluate state across resume. |
| Publication lifecycle | pending | Need full paper plan/draft/review/compile loop with real PDF/submission checks. |
| Full parity claim | warn | Route inventory remains 17 partial and 11 gated. |

## Step 30 Planned Files

| Field | Value |
|---|---|
| Planned files | `harness/tools/run_scientific_lifecycle_smoke.py`, `harness/plugins/autosci/bin/autosci_skill_shim.py`, `harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py`, `harness/plugins/autosci/tests/test_autosci_skill_shim.py`, `harness/plugins/autosci/config/feature_parity_routes.v1.json`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Goal | Pass explicit experiment approval/runtime evidence into scheduler lifecycle experiment run and monitor nodes. |
| Non-goal | No arbitrary command execution by default and no full-parity route upgrade. |

## Step 30 Verification

| Command | Result |
|---|---|
| `env PYTHONPATH=harness .venv/bin/python -m py_compile harness/tools/run_scientific_lifecycle_smoke.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `python3 -m json.tool harness/plugins/autosci/config/feature_parity_routes.v1.json` | ok |
| `test_scientific_lifecycle_smoke_uses_experiment_runtime_evidence` | ok: 1 passed |
| `test_autosci_skill_shim_research_scheduler_uses_experiment_runtime_evidence` | ok: 1 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py -q` | ok: 8 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 81 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q` | ok: 88 passed outside sandbox; local provider test requires binding `127.0.0.1` |
| `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json` | ok: 27 nodes, 2 workflows, 0 issues |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step30.json` | ok: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |

## Current Remaining Blockers After Step 30

| Blocker | Status | Required next proof |
|---|---|---|
| Scheduler experiment runtime passthrough | ok | Experiment run/monitor nodes consume supplied `--experiment-*` evidence without fixture result fallback. |
| Live provider execution | pending | Need approved provider/source runs that produce durable runtime evidence instead of test-supplied runtime JSON. |
| Long-running experiment lifecycle | pending | Need approved deploy/status/collect/evaluate runners across resume, including remote/session state. |
| Publication lifecycle | pending | Need full paper plan/draft/review/compile loop with real PDF/submission checks. |
| Full parity claim | warn | Route inventory remains 17 partial and 11 gated. |

## Step 31 Planned Files

| Field | Value |
|---|---|
| Planned files | `harness/tools/run_scientific_lifecycle_smoke.py`, `harness/plugins/autosci/bin/autosci_skill_shim.py`, `harness/plugins/autosci/bin/autosci_bridge.py`, `harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py`, `harness/plugins/autosci/tests/test_autosci_skill_shim.py`, `harness/plugins/autosci/config/feature_parity_routes.v1.json`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Goal | Add an explicit approved experiment executor path to scheduler-run and verify generated runtime/result evidence feeds downstream monitor state. |
| Non-goal | No default execution and no remote/session parity claim. |

## Step 31 Verification

| Command | Result |
|---|---|
| `env PYTHONPATH=harness .venv/bin/python -m py_compile harness/plugins/autosci/bin/autosci_bridge.py harness/tools/run_scientific_lifecycle_smoke.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `python3 -m json.tool harness/plugins/autosci/config/feature_parity_routes.v1.json` | ok |
| `test_scientific_lifecycle_smoke_executes_approved_experiment_command` | ok: 1 passed |
| `test_autosci_skill_shim_research_scheduler_executes_approved_experiment_command` | ok: 1 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py -q` | ok: 9 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 82 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q` | ok: 89 passed outside sandbox; local provider test requires binding `127.0.0.1` |
| `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json` | ok: 27 nodes, 2 workflows, 0 issues |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step31.json` | ok: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |

## Current Remaining Blockers After Step 31

| Blocker | Status | Required next proof |
|---|---|---|
| Approved local experiment executor | ok | Scheduler can run an allowlisted approved local experiment command and feed generated runtime/result evidence into monitor state. |
| Live provider execution | pending | Need approved provider/source runs that produce durable runtime evidence under real provider conditions. |
| Remote/session experiment lifecycle | pending | Need approved deploy/status/collect/evaluate runners with remote/session state, not only local command execution. |
| Publication lifecycle | pending | Need full paper plan/draft/review/compile loop with real PDF/submission checks. |
| Full parity claim | warn | Route inventory remains 17 partial and 11 gated. |

## Step 32 Planned Files

| Field | Value |
|---|---|
| Planned files | `harness/tools/run_scientific_lifecycle_smoke.py`, `harness/plugins/autosci/bin/autosci_skill_shim.py`, `harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py`, `harness/plugins/autosci/tests/test_autosci_skill_shim.py`, `harness/plugins/autosci/config/feature_parity_routes.v1.json`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Goal | Add compile-specific scheduler/shim flags for approved publication compile evidence/execution and verify generated PDF/runtime evidence. |
| Non-goal | No default compile execution and no submission/anonymity parity claim. |

## Step 32 Verification

| Command | Result |
|---|---|
| `env PYTHONPATH=harness .venv/bin/python -m py_compile harness/tools/run_scientific_lifecycle_smoke.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `python3 -m json.tool harness/plugins/autosci/config/feature_parity_routes.v1.json` | ok |
| `test_scientific_lifecycle_smoke_executes_approved_publication_compile` | ok: 1 passed |
| `test_autosci_skill_shim_research_scheduler_executes_approved_publication_compile` | ok: 1 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py -q` | ok: 10 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 83 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q` | ok: 90 passed outside sandbox; local provider test requires binding `127.0.0.1` |
| `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json` | ok: 27 nodes, 2 workflows, 0 issues |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step32.json` | ok: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |

## Current Remaining Blockers After Step 32

| Blocker | Status | Required next proof |
|---|---|---|
| Approved publication compile | ok | Scheduler can run an allowlisted approved local TeX command and verify generated PDF/runtime evidence. |
| Live provider execution | pending | Need approved provider/source runs that produce durable runtime evidence under real provider conditions. |
| Remote/session experiment lifecycle | pending | Need approved deploy/status/collect/evaluate runners with remote/session state, not only local command execution. |
| Submission/anonymity publication checks | pending | Need final checklist coverage for anonymity, page/font limits, and submission package expectations. |
| Full parity claim | warn | Route inventory remains 17 partial and 11 gated. |

## Step 33 Planned Files

| Field | Value |
|---|---|
| Planned files | `harness/plugins/autosci/bin/autosci_bridge.py`, `harness/plugins/autosci/tests/test_autosci_skill_shim.py`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Goal | Add truthful submission checklist diagnostics for anonymity, page/font evidence, and `[UNCONFIRMED]` markers. |
| Non-goal | No fake PDF font parser and no venue-specific submission rule expansion without evidence. |

## Step 33 Verification

| Command | Result |
|---|---|
| `env PYTHONPATH=harness .venv/bin/python -m py_compile harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `test_autosci_skill_shim_paper_compile_checklist_records_submission_checks` | ok: 1 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q` | ok: 91 passed outside sandbox; local provider test requires binding `127.0.0.1` |
| `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json` | ok: 27 nodes, 2 workflows, 0 issues |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step33.json` | ok: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |

## Current Remaining Blockers After Step 33

| Blocker | Status | Required next proof |
|---|---|---|
| Submission checklist truthfulness | ok | Compile checklist surfaces anonymity, page/font, and `[UNCONFIRMED]` diagnostics without false pass claims. |
| Live provider execution | pending | Need approved provider/source runs that produce durable runtime evidence under real provider conditions. |
| Remote/session experiment lifecycle | pending | Need approved deploy/status/collect/evaluate runners with remote/session state, not only local command execution. |
| Venue-specific submission rules | pending | Need verified venue rules for exact page/font/anonymity thresholds before marking final publication parity. |
| Full parity claim | warn | Route inventory remains 17 partial and 11 gated. |

## Step 34 Planned Files

| Field | Value |
|---|---|
| Planned files | `harness/plugins/autosci/bin/autosci_bridge.py`, `harness/plugins/autosci/tests/test_autosci_skill_shim.py`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Goal | Assimilate `tools/remote.py launch` runtime evidence paths from approved experiment executor stdout into semantic experiment verification. |
| Non-goal | No real SSH/session runner expansion in this step. |

## Step 34 Verification

| Command | Result |
|---|---|
| `env PYTHONPATH=harness .venv/bin/python -m py_compile harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `test_autosci_skill_shim_exp_run_assimilates_remote_helper_runtime_evidence` + `test_autosci_skill_shim_exp_run_rejects_remote_helper_stdout_without_runtime_evidence` | ok: 2 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q` | ok: 93 passed outside sandbox; local provider test requires binding `127.0.0.1` |
| `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json` | ok: 27 nodes, 2 workflows, 0 issues |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step34.json` | ok: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |

## Current Remaining Blockers After Step 34

| Blocker | Status | Required next proof |
|---|---|---|
| Remote helper runtime assimilation | ok | Approved `tools/remote.py launch` can provide runtime evidence consumed by experiment semantic verification and wiki mutation. |
| True remote/session lifecycle | pending | Need approved deploy/status/collect/evaluate runners with durable remote/session state, not only helper-produced local runtime evidence. |
| Live provider execution | pending | Need approved provider/source/model runs that produce durable runtime evidence under real provider conditions. |
| Publication full parity | pending | Need remaining paper plan/draft/review/compile/submission evidence loop with verified venue-specific checks. |
| Full parity claim | warn | Route inventory remains 17 partial and 11 gated. |

## Step 35 Planned Files

| Field | Value |
|---|---|
| Planned files | `harness/plugins/autosci/bin/autosci_bridge.py`, `harness/plugins/autosci/tests/test_autosci_skill_shim.py`, `harness/plugins/autosci/config/feature_parity_routes.v1.json`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Goal | Execute approved collect commands such as `tools/remote.py pull-results`, convert collected files into runtime evidence, and verify them through existing monitor semantics. |
| Non-goal | No SSH/session transport and no exactly-once collection ledger yet. |

## Step 35 Verification

| Command | Result |
|---|---|
| `env PYTHONPATH=harness .venv/bin/python -m py_compile harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `python3 -m json.tool harness/plugins/autosci/config/feature_parity_routes.v1.json` | ok |
| `test_autosci_skill_shim_exp_collect_uses_verified_runtime_evidence` + `test_autosci_skill_shim_exp_collect_executes_approved_remote_pull_results` + `test_autosci_skill_shim_exp_collect_rejects_empty_remote_pull_results` | ok: 3 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q` | ok: 95 passed outside sandbox; local provider test requires binding `127.0.0.1` |
| `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json` | ok: 27 nodes, 2 workflows, 0 issues |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step35.json` | ok: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |

## Current Remaining Blockers After Step 35

| Blocker | Status | Required next proof |
|---|---|---|
| Approved pull-results collection | ok | `$exp-run --collect --execute-approved` can run an approved collect command, verify collected files, and mutate wiki state. |
| Exactly-once collection | pending | Need durable collection identity/hash ledger so repeated collection returns existing accepted evidence instead of duplicating artifacts. |
| True remote/session status | pending | Need persistent process/session registry and status polling, not only local helper output. |
| Live provider execution | pending | Need approved provider/source/model runs that produce durable runtime evidence under real provider conditions. |
| Full parity claim | warn | Route inventory remains 17 partial and 11 gated. |

## Step 36 Planned Files

| Field | Value |
|---|---|
| Planned files | `harness/plugins/autosci/bin/autosci_bridge.py`, `harness/plugins/autosci/tests/test_autosci_skill_shim.py`, `harness/plugins/autosci/config/feature_parity_routes.v1.json`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Goal | Add local collection identity/hash ledger and reuse behavior for repeated approved collect runs. |
| Non-goal | No distributed lock, remote scheduler resume, or provider-specific session polling yet. |

## Step 36 Verification

| Command | Result |
|---|---|
| `env PYTHONPATH=harness .venv/bin/python -m py_compile harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `python3 -m json.tool harness/plugins/autosci/config/feature_parity_routes.v1.json` | ok |
| collect runtime + pull-results + empty collection + exactly-once ledger tests | ok: 4 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q` | ok: 96 passed outside sandbox; local provider test requires binding `127.0.0.1` |
| `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json` | ok: 27 nodes, 2 workflows, 0 issues |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step36.json` | ok: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |

## Current Remaining Blockers After Step 36

| Blocker | Status | Required next proof |
|---|---|---|
| Local exactly-once collection | ok | Repeated approved collect runs reuse a collection identity/hash ledger and avoid duplicate wiki mutation. |
| True remote/session status | pending | Need persistent process/session registry and live status polling, not only local helper output. |
| Scheduler resume | pending | Need resume proof that deployed/waiting/collected nodes are not rerun after restart. |
| Live provider execution | pending | Need approved provider/source/model runs that produce durable runtime evidence under real provider conditions. |
| Full parity claim | warn | Route inventory remains 17 partial and 11 gated. |

## Step 37 Planned Files

| Field | Value |
|---|---|
| Planned files | `harness/plugins/autosci/bin/autosci_bridge.py`, `harness/plugins/autosci/tests/test_autosci_skill_shim.py`, `harness/plugins/autosci/config/feature_parity_routes.v1.json`, `docs/integrations/autosci/native-lifecycle-continuation-log.md`, `docs/integrations/autosci/phase15-progress-log.md` |
| Goal | Persist approved launch/session records and let `$exp-status` report non-completed waiting/running state from that registry. |
| Non-goal | No SSH/screen polling, remote process management, or scheduler replay yet. |

## Step 37 Verification

| Command | Result |
|---|---|
| `env PYTHONPATH=harness .venv/bin/python -m py_compile harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `python3 -m json.tool harness/plugins/autosci/config/feature_parity_routes.v1.json` | ok |
| `test_autosci_skill_shim_exp_status_reads_persistent_session_registry` | ok: 1 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q` | ok: 97 passed outside sandbox; local provider test requires binding `127.0.0.1` |
| `env PYTHONPATH=harness .venv/bin/python harness/tools/audit_scientific_runtime_bindings.py --strict --json` | ok: 27 nodes, 2 workflows, 0 issues |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step37.json` | ok: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |

## Current Remaining Blockers After Step 37

| Blocker | Status | Required next proof |
|---|---|---|
| Local session registry status | ok | Approved launch/session records persist and `$exp-status` can report running state from the registry. |
| Live remote polling | pending | Need approved `tools/remote.py check` or provider-specific status polling against a durable session/run directory. |
| Scheduler resume | pending | Need resume proof that deployed/waiting/collected nodes are not rerun after restart. |
| Live provider execution | pending | Need approved provider/source/model runs that produce durable runtime evidence under real provider conditions. |
| Full parity claim | warn | Route inventory remains 17 partial and 11 gated. |
