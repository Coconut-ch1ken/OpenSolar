# AutoSci Phase 19 Progress Log

Logged: 2026-06-19 00:14 EDT
Branch: `feature/autosci-solar-native`

## Scope

Phase 19 is the follow-up parity phase after Phase 18 acceptance. The goal is
to move from fixture-mode scientific lifecycle acceptance toward practical
feature parity with the local AutoSci `main` checkout, while preserving the
Solar-native architecture:

```text
TaskGraph node
  -> Logical operator
  -> Capability capsule
  -> Physical operator
  -> plugins/autosci backend action
  -> Evidence ABI / sidecar artifact
  -> deterministic gate or explicit warning
```

This phase must not introduce a monolithic `AutoSciRunner`, must not make
AutoSci the owner of workflow semantics, and must not silently replace
model-driven or evidence-driven paths with unsupported deterministic guesses.

## Work Completed Tonight

| Item | Status | Evidence |
|---|---|---|
| Phase 18 closeout | ok | Added `docs/integrations/autosci/phase18-progress-log.md`. |
| Phase 18 commit | ok | Commit `6dda794f docs: record autosci phase 18 acceptance`. |
| Phase 18 push | ok | Pushed `feature/autosci-solar-native` to GitHub. |
| Solar context injection | warn | Re-ran as `bash harness/solar-harness.sh context inject ...`; Mirage source returned `mirage:nonzero`. |
| AutoSci capability scan | ok | Inspected local `/Users/jamesyuan/Developer/Github Repos (On Git)/AutoSci` README, skills, tools, runtime schema, remote/daily/poster docs. |
| Solar coverage scan | ok | Inspected Solar AutoSci bridge actions, capsules, schemas, evaluators, workflows, personas, templates. |
| Parity finding | warn | Solar covers the scientific lifecycle governance/core, but not all AutoSci `main` concrete product features yet. |
| Phase 19 route parity config | ok | Added `harness/plugins/autosci/config/feature_parity_routes.v1.json` covering all 28 native AutoSci English skills. |
| Phase 19 parity bridge | ok | Added `harness/plugins/autosci/bin/autosci_parity_bridge.py` to scan native skills and emit `autosci_feature_parity.v1` evidence. |
| Phase 19 parity ABI/gate | ok | Added `harness/schemas/evidence/autosci_feature_parity.v1.schema.json` and `harness/evaluators/scientific/autosci_feature_parity_gate.py`. |
| Phase 19 real operator binding | ok | Added `harness/plugins/autosci/config/feature_operator_bindings.v1.json` mapping every native skill to a physical operator binding. |
| Phase 19 skillgen operator smoke | ok | Added `harness/plugins/autosci/bin/autosci_operator_smoke.py`, `autosci_operator_smoke.v1`, and smoke gate/tests. |
| Phase 19 tests | ok | Added bridge and gate tests; targeted suite passes `6 passed`. |
| Phase 19 matrix | ok | Added `docs/integrations/autosci/autosci-solar-feature-parity-matrix.md`. |

## Current Solar Coverage Baseline

| Capability group | Status | Solar surface |
|---|---|---|
| Literature discovery | ok | `discover_literature`, `literature_discovery.v1` |
| Paper ingest/analyze | ok | `ingest_paper`, `analyze_paper`, `research_paper.v1` |
| Memory and graph update | ok | `update_memory`, `update_graph`, memory/graph evidence |
| Claim/method/code extraction | ok | `extract_claims`, `extract_methods`, `map_code_evidence` |
| Idea generation/evaluation | ok | `generate_ideas`, `evaluate_ideas` |
| Experiment design/run/status | ok | `design_experiment`, `run_experiment`, `monitor_experiment` |
| Claim verdict | ok | `verify_claim`, `claim_verdict.v1` |
| Report/publication bundle | ok | `write_report`, report and publication gates |
| Workflow evolution | ok | `evolve_workflow`, `workflow_evolution.v1` |

## AutoSci Features Requiring Phase 19 Parity Work

| AutoSci feature | Current Solar status | Required Phase 19 direction |
|---|---|---|
| `/setup` | missing | Add config/status evidence action without mutating secrets. |
| `/reset` | missing | Add dry-run reset plan evidence; destructive execution must require explicit approval. |
| `/prefill` | missing | Add foundation/background evidence and memory-update path. |
| `/init` | partial | Add prepare/discovery/fan-in parity actions and source manifest evidence. |
| `/ingest` | partial | Move beyond sample markdown fixture toward local file/arXiv source preparation. |
| `/discover` live/topic/venue | partial | Add source-mode evidence for anchor/topic/wiki/venue discovery. |
| `/edit` | missing | Add bounded wiki edit plan/evidence action. |
| `/ask` | missing | Add retrieve/synthesize/crystallize evidence action with explicit confidence. |
| `/check` | missing | Add wiki health check evidence and gate. |
| `/daily-arxiv` | missing | Add prepare/finalize/digest evidence; live feeds/email/GitHub Actions as gated side effects. |
| `/novelty` | partial | Add multi-source novelty evidence and Review LLM warning path. |
| `/review` | partial | Add review report evidence and optional MCP-backed review binding. |
| `/refine` | partial | Add iterative review/fix loop evidence without silent edits. |
| `/exp-pilot-run` | partial | Add pilot-specific execution/result evidence. |
| `/exp-pilot-eval` | partial | Add lenient pilot verdict evidence. |
| `/exp-run --env remote` | partial | Add remote plan/status evidence; real SSH/rsync/screen must be approval-gated. |
| `/exp-status --collect-ready` | partial | Add collect-ready status and collection evidence. |
| `/exp-eval` | partial | Add Review LLM verdict mode and idea status update evidence. |
| `/survey` | missing | Add related-work/survey evidence and report artifact. |
| `/paper-plan` | partial | Add native paper outline/figure/citation plan evidence. |
| `/paper-draft` | partial | Add LaTeX draft bundle evidence. |
| `/paper-compile` | missing | Add compile/checklist evidence; real `latexmk` gated by availability. |
| `/rebuttal` | partial | Add rebuttal response evidence and review-comment mapping. |
| `/poster` | partial | Add full poster tool parity for build/title/header/figures/validate/render/overflow. |
| `/visualize` | missing | Add graph visualization artifacts for Obsidian config, Canvas, and web graph summary. |
| `tools/serve.py` web UI | missing | Add optional local server/runbook surface; not a core evidence ABI yet. |
| `mcp-servers/llm-review` | missing | Add optional physical operator binding and unavailable-state evidence. |

## Proposed Phase 19 Slices

| Slice | Status | Intended output |
|---|---|---|
| 19A parity matrix | ok | `docs/integrations/autosci/autosci-solar-feature-parity-matrix.md` |
| 19B generic parity evidence | ok | `autosci_feature_parity.v1` evidence ABI plus deterministic gate. |
| 19C bridge route expansion | ok | Added route-level bridge actions for setup/reset/prefill/init/check/ask/daily/review/poster/visualize and all other native skills. |
| 19D operator/config binding | ok | Added plugin route config mapping each native skill to Solar capability, logical operator, backend action, and Evidence ABI. |
| 19E gates/tests | ok | Added deterministic checks for route completeness, truthful partial/gated status, and missing-route failure. |
| 19F acceptance | ok | Local AutoSci scan produced 28 native skills, 28 routed, 0 missing. |

## Phase 19 Implementation Details

| File | Status | Purpose |
|---|---|---|
| `harness/plugins/autosci/config/feature_parity_routes.v1.json` | ok | Declarative Solar route map for every native AutoSci English skill. |
| `harness/plugins/autosci/config/feature_operator_bindings.v1.json` | ok | Physical operator binding map for every native AutoSci English skill. |
| `harness/plugins/autosci/bin/autosci_parity_bridge.py` | ok | Discovers AutoSci native skills and emits route parity evidence. |
| `harness/plugins/autosci/bin/autosci_operator_smoke.py` | ok | Runs real AutoSci bridge actions against the SkillGen smoke paper and summarizes route/operator status. |
| `harness/schemas/evidence/autosci_feature_parity.v1.schema.json` | ok | Evidence ABI for route parity inventory. |
| `harness/schemas/evidence/autosci_operator_smoke.v1.schema.json` | ok | Evidence ABI for SkillGen-backed operator smoke results. |
| `harness/evaluators/scientific/autosci_feature_parity_gate.py` | ok | Gate that fails on missing routes, bad counts, or false full-coverage claims. |
| `harness/evaluators/scientific/autosci_operator_smoke_gate.py` | ok | Gate that fails on unbound/failed operator routes and enforces gated side-effect honesty. |
| `harness/plugins/autosci/tests/fixtures/skillgen_operator_smoke_paper.md` | ok | Committed SkillGen smoke paper fixture. |
| `harness/plugins/autosci/tests/test_phase19_parity_bridge.py` | ok | Tests full inventory, single-skill route output, and unmapped future-skill failure. |
| `harness/plugins/autosci/tests/test_phase19_operator_smoke.py` | ok | Tests SkillGen smoke execution, all operator bindings, and generated smoke gate acceptance. |
| `harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py` | ok | Tests honest mixed coverage, missing route rejection, and full+approval misreport rejection. |
| `harness/tests/evaluators/scientific/test_autosci_operator_smoke_gate.py` | ok | Tests mixed completed/partial/gated smoke acceptance and unbound rejection. |
| `docs/integrations/autosci/autosci-solar-feature-parity-matrix.md` | ok | Human-readable matrix and verification record. |

## Phase 19 Verification

| Command | Result |
|---|---|
| `python3 -m json.tool harness/plugins/autosci/config/feature_parity_routes.v1.json` | ok |
| `python3 -m json.tool harness/schemas/evidence/autosci_feature_parity.v1.schema.json` | ok |
| `python3 harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out artifacts/autosci/phase19/parity_inventory.json` | ok: 28 native, 28 routed, 0 missing, 7 full, 11 partial, 10 gated |
| `python3 harness/evaluators/scientific/autosci_feature_parity_gate.py harness/artifacts/autosci/phase19/parity_inventory.json` | ok: passed with non-full route warning |
| `harness/bin/python3 harness/plugins/autosci/bin/autosci_operator_smoke.py skillgen --out artifacts/autosci/operator-smoke/skillgen/autosci_operator_smoke.json` | ok: 28 bound, 0 failed, 0 unbound, 16 core actions |
| `python3 harness/evaluators/scientific/autosci_operator_smoke_gate.py harness/artifacts/autosci/operator-smoke/skillgen/autosci_operator_smoke.json` | ok: passed with approval-gated warning |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_phase19_parity_bridge.py harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py` | ok: 6 passed before operator-smoke expansion |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_phase19_operator_smoke.py harness/tests/evaluators/scientific/test_autosci_operator_smoke_gate.py` | ok: 4 passed |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests harness/tests/evaluators/scientific` | ok: 63 passed |

## Phase 19 Acceptance State

| Criterion | Status | Evidence |
|---|---|---|
| Every discovered AutoSci native English skill has a Solar route | ok | `missing_route_count=0` in `harness/artifacts/autosci/phase19/parity_inventory.json`. |
| Every discovered AutoSci native English skill has a physical operator binding | ok | `bound_count=28`, `unbound_count=0` in `harness/artifacts/autosci/operator-smoke/skillgen/autosci_operator_smoke.json`. |
| SkillGen paper runs through real core bridge operators | ok | 16 core actions executed; 14 gate-passed and 2 schema-only where no deterministic gate exists. |
| Route status is truthful, not overclaimed | ok | Gate rejects `full` routes that still require approval and warns on partial/gated routes. |
| Side effects remain governed | ok | Config marks reset/edit/setup/remote/email/browser/GitHub Actions/compile paths as approval-gated. |
| Future AutoSci skill drift is detectable | ok | Bridge test adds `new-native-skill` and verifies missing-route failure. |
| No AutoSci black-box owner introduced | ok | Bridge emits route parity evidence; it does not execute or own the research workflow. |

## Guardrails

- Do not call a single AutoSci end-to-end owner.
- Do not mutate user-owned AutoSci `raw/` inputs from Solar parity tests.
- Do not execute remote SSH, SMTP email, browser open, GitHub Actions mutation,
  or destructive reset without explicit approval.
- If live APIs or external tools are unavailable, emit `warn` or `inconclusive`
  evidence instead of a fake success.
- Keep AutoSci-specific mechanics in `harness/plugins/autosci`; keep Solar
  workflow meaning in operators, capsules, workflows, schemas, gates, and docs.

## Current Worktree Note

The OpenSolar worktree already contains substantial modified and untracked
AutoSci integration files from earlier phases. Phase 19 commits should stage
only files intentionally changed for the current slice.
