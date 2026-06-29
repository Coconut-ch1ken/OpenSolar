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

## Phase 19 Shim Follow-up

| Item | Status | Evidence |
|---|---|---|
| Solar AutoSci skill shim | ok | Added `harness/plugins/autosci/bin/autosci_skill_shim.py` and `solar-harness.sh autosci ...` dispatch. |
| Skill-run Evidence ABI | ok | Added `harness/schemas/evidence/autosci_skill_run.v1.schema.json`. |
| Skill-run gate | ok | Added `harness/evaluators/scientific/autosci_skill_run_gate.py`. |
| Runtime artifact resolver | ok | Scientific gate artifact checks now also resolve paths under runtime `HARNESS_DIR` while schemas remain repo-local. |
| Shim tests | ok | Added `harness/plugins/autosci/tests/test_autosci_skill_shim.py`. |

## Phase 19 Dollar Skill Compatibility Follow-up

Logged: 2026-06-22 EDT

| Item | Status | Evidence |
|---|---|---|
| `$skills` list alias | ok | `autosci_skill_shim.py` normalizes `$skills` to `skills list`. |
| `$skill <name>` alias | ok | `autosci_skill_shim.py` normalizes `$skill ingest ...` to `skill ingest ...`. |
| `$<skill-name>` direct aliases | ok | Any configured native skill name can be invoked as `$ingest`, `$research`, `$exp-design`, etc.; unknown routes still emit failed route evidence instead of silent success. |
| Codex/PM intake routing | ok | `scripts/solar-codex-intake.sh` detects AutoSci `$...` messages and sends them directly to the deterministic shim instead of natural-language intent compilation. |
| Repo-local chat trace behavior | ok | `scripts/solar-chat.sh --trace` treats direct `$...` commands as direct shim runs and does not require a sprint DAG trace. |
| Harness top-level dispatch | ok | `harness/solar-harness.sh` dispatches literal `$skills`, `$skill`, and `$<skill>` arguments to the AutoSci shim. |

### Shim Commands

| Command | Result |
|---|---|
| `bash harness/solar-harness.sh autosci skills list` | ok: lists 28 configured native AutoSci skills. |
| `bash harness/solar-harness.sh '$skills'` | ok: lists 28 configured native AutoSci skills through the AutoSci-compatible command surface. |
| `bash harness/solar-harness.sh '$ingest' --paper "$PWD/harness/plugins/autosci/tests/fixtures/skillgen_operator_smoke_paper.md" --run-id solar-dollar-ingest-smoke` | ok: routes through the deterministic shim and generates `autosci_skill_run.v1` evidence. |
| `python3 harness/evaluators/scientific/autosci_skill_run_gate.py harness/artifacts/autosci/runs/solar-dollar-ingest-smoke/autosci_skill_run.json` | ok: passed. |
| `bash scripts/solar-codex-intake.sh --dry-run '$ingest --paper harness/plugins/autosci/tests/fixtures/skillgen_operator_smoke_paper.md --run-id codex-dollar-dryrun'` | ok: resolves to direct `autosci_skill_shim.py text ...`, not `intake`. |
| `bash scripts/solar-chat.sh --trace '$skills'` | ok: lists 28 skills and reports direct AutoSci command without sprint DAG trace. |
| `~/.solar/bin/solar-harness '$skills'` | ok: active installed harness returns `ok=True`, `count=28`. |
| `bash harness/solar-harness.sh autosci skill ingest --paper "$PWD/harness/plugins/autosci/tests/fixtures/skillgen_operator_smoke_paper.md" --run-id solar-shim-ingest-smoke` | ok: generated `autosci_skill_run.v1`, `research_paper.json`, and `research_paper.analyzed.json`. |
| `bash harness/solar-harness.sh autosci skill research --paper "$PWD/harness/plugins/autosci/tests/fixtures/skillgen_operator_smoke_paper.md" --topic "agent skill learning" --run-id solar-shim-research-smoke` | ok: ran 16 bounded bridge actions; 14 gate-passed, 2 schema-only; route honestly marked `gated`. |
| `bash harness/solar-harness.sh autosci skill setup --run-id solar-shim-setup-smoke` | ok: generated gated route evidence without writing secrets or executing setup side effects. |
| `python3 harness/evaluators/scientific/autosci_skill_run_gate.py harness/artifacts/autosci/runs/solar-shim-research-smoke/autosci_skill_run.json` | ok: passed with gated-route warning. |
| `python3 harness/evaluators/scientific/autosci_skill_run_gate.py harness/artifacts/autosci/runs/solar-shim-setup-smoke/autosci_skill_run.json` | ok: passed with gated-route warning. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok: 4 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok: 8 passed after dollar-command compatibility tests. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests harness/tests/evaluators/scientific` | ok: 71 passed after dollar-command compatibility tests. |

## Phase 19 Solar Skill Projection and Workspace Follow-up

Logged: 2026-06-22 EDT

| Item | Status | Evidence |
|---|---|---|
| Codex-native Solar AutoSci skill projection | ok | Generated 28 wrapper skills under `.agents/skills/*/SKILL.md`; wrappers preserve `$skill_name` UX and require routing through Solar. |
| Projection generator | ok | Added `harness/plugins/autosci/bin/project_autosci_codex_skills.py` to regenerate wrappers from Solar route config. |
| Human-facing workspace projector | ok | Added `harness/plugins/autosci/bin/autosci_workspace_projector.py`; it projects run evidence into `harness/artifacts/autosci/workspace/wiki/`. |
| Solar-managed logs boundary | ok | Workspace pages include research entities and outputs only; envelopes, logs, gate results, and operator state remain under Solar-managed run/runtime paths. |
| Shim workspace handoff | ok | `autosci_skill_shim.py` writes run evidence first, projects workspace pages, then records workspace paths in `outputs.skill_run.workspace`. |
| Skill projection tests | ok | Added `harness/plugins/autosci/tests/test_autosci_skill_projection.py`. |
| Workspace projection tests | ok | Extended `harness/plugins/autosci/tests/test_autosci_skill_shim.py` to assert paper, idea, experiment, and report workspace pages. |

### Projection Output Shape

| Path | Owner | Purpose |
|---|---|---|
| `harness/artifacts/autosci/runs/<run-id>/` | Solar | Execution evidence, envelopes, result JSON, gates, and reproducibility records. |
| `harness/artifacts/autosci/workspace/README.md` | Human/Solar projection | Explains human-facing workspace policy. |
| `harness/artifacts/autosci/workspace/wiki/index.md` | Human/Solar projection | Research navigation index. |
| `harness/artifacts/autosci/workspace/wiki/papers/` | Human/Solar projection | Durable paper pages projected from `research_paper.v1`. |
| `harness/artifacts/autosci/workspace/wiki/methods/` | Human/Solar projection | Method pages projected from `research_method.v1`. |
| `harness/artifacts/autosci/workspace/wiki/ideas/` | Human/Solar projection | Idea pages projected from `idea_candidate.v1`. |
| `harness/artifacts/autosci/workspace/wiki/experiments/` | Human/Solar projection | Experiment pages projected from `experiment_plan.v1`. |
| `harness/artifacts/autosci/workspace/wiki/outputs/` | Human/Solar projection | Claims/report pages intended for direct reading. |
| `harness/artifacts/autosci/workspace/wiki/graph/` | Human/Solar projection | Explicit graph edges and brief/open-question summaries. |

### Projection Commands

| Command | Result |
|---|---|
| `python3 harness/plugins/autosci/bin/project_autosci_codex_skills.py --source-skills "/Users/jamesyuan/Developer/Github Repos (On Git)/AutoSci/.agents/skills"` | ok: generated 28 OpenSolar wrapper skills. |
| `python3 -m py_compile harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/bin/autosci_workspace_projector.py harness/plugins/autosci/bin/project_autosci_codex_skills.py` | ok |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py harness/plugins/autosci/tests/test_autosci_skill_projection.py` | ok: 9 passed. |
| `bash harness/solar-harness.sh '$ingest' --paper "$PWD/harness/plugins/autosci/tests/fixtures/skillgen_operator_smoke_paper.md" --run-id solar-projection-ingest-smoke` | ok: generated Solar run evidence and `workspace/wiki/papers/paper-skillgen-operator-smoke-paper.md`. |
| `python3 harness/evaluators/scientific/autosci_skill_run_gate.py harness/artifacts/autosci/runs/solar-projection-ingest-smoke/autosci_skill_run.json` | ok: passed. |
| `bash harness/solar-harness.sh '$research' --paper "$PWD/harness/plugins/autosci/tests/fixtures/skillgen_operator_smoke_paper.md" --topic "agent skill learning" --run-id solar-projection-research-smoke` | ok: generated gated Solar research run and workspace pages for paper, method, ideas, experiment, claims, and report. |
| `python3 harness/evaluators/scientific/autosci_skill_run_gate.py harness/artifacts/autosci/runs/solar-projection-research-smoke/autosci_skill_run.json` | ok: passed with gated-route warning. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests harness/tests/evaluators/scientific` | ok: 72 passed. |
| `find .agents/skills -maxdepth 2 -name SKILL.md -print \| sort \| xargs -n1 dirname \| xargs -n1 harness/bin/python3 /Users/jamesyuan/.codex/skills/.system/skill-creator/scripts/quick_validate.py` | ok: 28 valid skills. |

## Phase 19 Lab Worktree Skill Discovery Follow-up

Logged: 2026-06-22 EDT

| Item | Status | Evidence |
|---|---|---|
| Root cause | ok | Solar lab Codex panes launch with `--cd .worktrees/lab-builder-*`; those worktrees had 0 `.agents/skills` while the main worktree had 28. |
| Merge decision | ok | No Git branch merge was needed: all four active lab worktrees were clean and based on the same HEAD as the main branch. The missing skills were untracked generated projection files. |
| Startup sync | ok | `harness/pane-launcher.sh` now projects Solar AutoSci wrapper skills into the actual pane `WORK_DIR/.agents/skills` before launching Codex. |
| Runtime route fix | ok | Generated wrapper skills now call `"${HARNESS_DIR:-$HOME/.solar/harness}/solar-harness.sh" '$skill' ...` so lab worktrees do not need uncommitted shim/intake files locally. |
| Active worktree sync | ok | Synced 28 wrapper skills into `.worktrees/lab-builder-{1,2,3,4}/.agents/skills`. |

### Worktree Skill Discovery Commands

| Command | Result |
|---|---|
| `git worktree list --porcelain` | ok: active Solar lab worktrees are `.worktrees/lab-builder-1..4` on `harness-lab-builder-*` branches. |
| `find .agents/skills -maxdepth 2 -name SKILL.md \| wc -l` | ok: main worktree has 28 wrapper skills. |
| `find .worktrees/lab-builder-*/.agents/skills -maxdepth 2 -name SKILL.md` before sync | warn: active lab worktrees had 0 wrapper skills. |
| `python3 harness/plugins/autosci/bin/project_autosci_codex_skills.py --output-dir ".worktrees/lab-builder-N/.agents/skills"` | ok: generated 28 wrapper skills per active lab worktree. |
| `bash -n harness/pane-launcher.sh` | ok |
| `env HARNESS_DIR="$PWD/harness" "$PWD/harness/solar-harness.sh" '$skills'` from `.worktrees/lab-builder-1` | ok: `True 28 True`, including `ingest`. |
| `env HARNESS_DIR="$PWD/harness" "$PWD/harness/solar-harness.sh" '$ingest' --paper ... --run-id worktree-wrapper-ingest-smoke` from `.worktrees/lab-builder-1` | ok: generated completed Solar run evidence and workspace paths. |
| `python3 harness/evaluators/scientific/autosci_skill_run_gate.py harness/artifacts/autosci/runs/worktree-wrapper-ingest-smoke/autosci_skill_run.json` | ok: passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py harness/plugins/autosci/tests/test_autosci_skill_projection.py` | ok: 9 passed. |

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

## Phase 19 Codex Pane Worktree Default Follow-up

Logged: 2026-06-22 EDT

| Item | Status | Evidence |
|---|---|---|
| Root cause | ok | Codex discovers skills from its `--cd` directory; lab panes in `.worktrees/lab-builder-*` missed main `.agents/skills` unless wrappers were copied. |
| Default behavior | ok | `SOLAR_BUILDER_WORKTREES` now defaults off; `pane-launcher.sh` and `start-incarnation.sh` keep builder/lab-builder `WORK_DIR` as the original OpenSolar checkout unless `SOLAR_BUILDER_WORKTREES=1` is set. |
| Opt-in isolation | ok | `harness/lib/worktree.sh` exposes `solar_builder_worktrees_enabled`; existing worktree creation remains available only when explicitly enabled. |
| Skill projection | ok | `pane-launcher.sh` still projects Solar AutoSci wrapper skills into the actual `WORK_DIR/.agents/skills`; with worktrees disabled this is the main OpenSolar `.agents/skills`. |
| Live lab refresh | ok | `bash harness/solar-harness.sh models apply-lab` respawned four lab panes; tmux pane cwd values are now the original OpenSolar directory, not `.worktrees/lab-builder-*`. |

### Worktree Default Verification Commands

| Command | Result |
|---|---|
| `bash -n harness/lib/worktree.sh harness/pane-launcher.sh harness/start-incarnation.sh` | ok |
| `bash harness/tests/test-d3-builder-worktree-consistency.sh` | ok: `PASS: 8 FAIL: 0`; verifies default-off and `SOLAR_BUILDER_WORKTREES=1` opt-in semantics. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_autosci_skill_projection.py` | ok: 1 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py harness/plugins/autosci/tests/test_autosci_skill_projection.py` | ok: 9 passed. |
| `bash harness/solar-harness.sh models apply-lab` | ok: respawned active lab panes after the default-off change. |
| `tmux list-panes -a -F '#{session_name}:#{window_name}.#{pane_index} #{pane_id} cwd=#{pane_current_path} title=#{pane_title}'` | ok: four `solar-harness-lab` panes use `/Users/jamesyuan/Developer/Github Repos (On Git)/OpenSolar` as cwd. |
| `find .agents/skills -mindepth 1 -maxdepth 1 -type d \| wc -l` | ok: 28 wrapper skill directories in the active Codex `--cd` project directory. |
| `rg -n "solar-harness\|do not execute native AutoSci" .agents/skills -g 'SKILL.md'` | ok: wrappers route through Solar Harness and forbid native AutoSci tool execution. |

### Worktree Cleanup Audit

| Worktree group | Status | Recommendation |
|---|---|---|
| `.worktrees/lab-builder-1..4` | not live after respawn; contain `.DS_Store`, generated `.agents/`, and in lab-builder-1 `library/.DS_Store` | Candidate cleanup after user approval if no hidden needed changes are found. |
| `.worktrees/builder` | not live; contains real modified AI influence/report validation code and tests plus untracked nested `.worktrees/` and caches | Do not delete. Review, merge, or explicitly discard these changes first. |
| nested `.worktrees/builder/.worktrees/builder*` | not live; mostly `.DS_Store` / nested worktree metadata | Candidate cleanup only after resolving parent `.worktrees/builder` and explicit approval. |
| `/Users/jamesyuan/.codex/worktrees/05ae/OpenSolar` | not live in current tmux audit; contains real modified core/harness and routing files | Do not delete without review. |
| `/Users/jamesyuan/.codex/worktrees/a0ad/OpenSolar` | not live in current tmux audit; has `codex-recovery/` untracked | Do not delete until recovery contents are reviewed. |
| `/Users/jamesyuan/.codex/worktrees/a0ad/OpenSolar/.worktrees/lab-builder-1..4` | not live in current tmux audit; clean by `git status --short --branch` | Candidate cleanup after user approval. |

No worktrees were deleted during this follow-up.

## Phase 19 Worktree Sync and Cleanup Follow-up

Logged: 2026-06-22 EDT

| Item | Status | Evidence |
|---|---|---|
| User approval | ok | User explicitly requested syncing progress to the original directory and deleting all worktrees. |
| Live pane audit | ok | Active Solar lab panes were already running from `/Users/jamesyuan/Developer/Github Repos (On Git)/OpenSolar`; no live pane cwd referenced `.worktrees`. |
| Preservation bundle | ok | Tracked diffs, clean-apply subsets, untracked tarballs, and status inventory were saved under `harness/artifacts/worktree-sync/20260622-worktree-cleanup/`. |
| Clean tracked sync | ok | Non-conflicting tracked changes from `/Users/jamesyuan/.codex/worktrees/05ae/OpenSolar` and `.worktrees/builder` were applied into the original checkout with `git apply --3way`. |
| Conflict handling | warn | Conflicting tracked changes were not overwritten; full patches are preserved in `codex-05ae-tracked.diff` and `local-builder-tracked.diff`. |
| Untracked sync | ok | Meaningful missing untracked files were copied into the original checkout: `codex-recovery/AI4Research-B-threads.md` and `harness/tests/test_report_deep_verifier_repair.py`. |
| Newer original files | ok | Original-checkout versions of `core/harness/harness-client.ts` and `scripts/solar-codex-intake.sh` were kept because they already contained newer Solar routing behavior than the worktree copies. |
| Worktree deletion | ok | All registered non-main worktrees were removed with `git worktree remove --force`; local `.worktrees/` leftovers were removed after confirming they contained only disposable residue. |
| Final worktree state | ok | `git worktree list --porcelain` reports only the original OpenSolar checkout. |

### Preserved Cleanup Artifacts

| Artifact | Purpose |
|---|---|
| `codex-05ae-tracked.diff` | Full tracked diff from `/Users/jamesyuan/.codex/worktrees/05ae/OpenSolar`, including conflicts that were not applied. |
| `codex-05ae-clean-apply.diff` | Clean subset applied into the original checkout. |
| `codex-05ae-untracked.tar.gz` | Untracked file backup from the 05ae Codex worktree. |
| `codex-a0ad-tracked.diff` | Empty tracked diff record for the a0ad Codex worktree. |
| `codex-a0ad-untracked.tar.gz` | Untracked recovery backup from the a0ad Codex worktree. |
| `local-builder-tracked.diff` | Full tracked diff from `.worktrees/builder`, including any paths excluded from clean apply. |
| `local-builder-clean-apply.diff` | Clean subset applied into the original checkout. |
| `local-builder-untracked.tar.gz` | Untracked backup from `.worktrees/builder`. |
| `worktree-status-summary.json` | Inventory of audited worktrees, tracked status, and untracked files before deletion. |

### Sync and Cleanup Verification Commands

| Command | Result |
|---|---|
| `lsof +D .worktrees` and `lsof +D /Users/jamesyuan/.codex/worktrees` | ok: no open file handles were reported before deletion. |
| `git apply --3way --check codex-05ae-clean-apply.diff` | ok: clean subset was applicable. |
| `git apply --3way --check local-builder-clean-apply.diff` | ok: clean subset was applicable. |
| `git worktree remove --force <path>` for every non-main registered worktree | ok: all non-main registered worktrees removed. |
| `git worktree list --porcelain` | ok: only `/Users/jamesyuan/Developer/Github Repos (On Git)/OpenSolar` remains. |
| `find .worktrees -maxdepth 2 -print` | ok: no local `.worktrees` directory remains. |
| `find /Users/jamesyuan/.codex/worktrees -maxdepth 2 -print` | ok: only the Codex worktree root and `.metadata_never_index` remain. |
| `bash -n harness/lib/worktree.sh harness/pane-launcher.sh harness/start-incarnation.sh` | ok |
| `bash harness/tests/test-d3-builder-worktree-consistency.sh` | ok: `PASS: 8 FAIL: 0`. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py harness/plugins/autosci/tests/test_autosci_skill_projection.py` | ok: 9 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/tests/test_ai_influence_youtube_report_pane_surface.py harness/tests/test_ai_influence_youtube_report_status_surface.py harness/tests/test_report_validation.py harness/tests/test_report_deep_verifier_repair.py harness/tests/test_unified_selector_binding_policy.py harness/tests/test_pm_dispatch.py harness/tests/test_physical_operator_logical_selector.py` | ok: 33 passed after updating the synced selector test to expect `gpt-5.5`. |
| `bash harness/tests/test-model-registry-guard.sh` | ok: `PASS=23 FAIL=0`. |
| `bash harness/tests/test-model-config-single-source.sh` | ok: `PASS=19 FAIL=0`. |

### Preserved Conflict Notes

| Path | Status | Reason |
|---|---|---|
| `AGENTS.md` | preserved in patch only | Worktree changes conflicted with the current original-checkout file. |
| `harness/config/physical-operators.json` | preserved in patch only | Worktree changes conflicted with the current original-checkout file. |
| `harness/lib/multi_task_runner.py` | preserved in patch only | Worktree changes conflicted with the current original-checkout file. |
| `core/harness/harness-client.ts` | original kept | Original checkout had newer repo-harness resolution behavior. |
| `scripts/solar-codex-intake.sh` | original kept | Original checkout had newer direct AutoSci dollar-command routing. |

## Phase 19 PDF / arXiv Source Preparation Gap Closure

Logged: 2026-06-22 EDT

| Item | Status | Evidence |
|---|---|---|
| Native AutoSci gap | ok | Confirmed original AutoSci `/ingest` and `/init` prepare local PDFs through `tools/prepare_paper_source.py`, recover arXiv IDs, fetch `https://arxiv.org/e-print/<id>`, and fall back to synthetic `.tex`. |
| Solar backend implementation | ok | Added `harness/plugins/autosci/backends/paper_prepare.py` and routed bridge paper reads through it. |
| Supported inputs | ok | Local `.pdf`, `.tex`, markdown, source directories, source archives, and arXiv URLs now share the same Solar AutoSci preparation path. |
| PDF extraction | ok | PyMuPDF-backed PDF text extraction writes explicit `extracted_pdf_text` artifacts under `artifacts/autosci/workspace/raw/tmp/papers/`. |
| arXiv source recovery | ok | Preparation recovers arXiv IDs from explicit inputs, arXiv URLs, filename/path/text, and optional title-based Semantic Scholar lookup, then prefers arXiv source before synthetic fallback. |
| Evidence preservation | ok | `research_paper.v1` now preserves `outputs.paper.preparation` and preparation artifacts. |
| Offline behavior | ok | `inputs.allow_network_fetch=false` or `AUTOSCI_DISABLE_NETWORK_FETCH=1` disables source retrieval and forces synthetic `.tex` fallback when possible. |
| Harness Python entry | ok | Updated `harness/solar-harness.sh` AutoSci skill entries to prefer `harness/bin/python3`, ensuring PyMuPDF and AutoSci dependencies are available during `$ingest`. |
| Skill UX | ok | Updated the `$ingest` Solar wrapper description to show `prepare_paper_source -> ingest_paper`. |

### PDF / arXiv Verification Commands

| Command | Result |
|---|---|
| `harness/bin/python3 -m py_compile harness/plugins/autosci/backends/paper_prepare.py harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/adapters/autosci_to_research_paper.py` | ok |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_paper_prepare.py -q` | ok: 2 passed. |
| `bash -n harness/solar-harness.sh` | ok |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests -q` | ok: 38 passed. |
| `env AUTOSCI_DISABLE_NETWORK_FETCH=1 bash harness/solar-harness.sh '$ingest' --paper /private/tmp/solar-autosci-pdf-smoke-2401.00003.pdf --run-id solar-pdf-ingest-smoke-2` | ok: `execution_status=completed`; `research_paper.v1` has `source_type=latex`, `arxiv=2401.00003`, `source_fetch_status=skipped_network_disabled`, `extracted_pdf_text`, and `synthetic_latex`. |
| `harness/bin/python3 harness/evaluators/scientific/paper_gate.py harness/artifacts/autosci/runs/solar-pdf-ingest-smoke-2/research_paper.json` | ok: `status=passed`. |

## Phase 19 Discover Command Compatibility Gap Closure

Logged: 2026-06-22 EDT

| Item | Status | Evidence |
|---|---|---|
| Native AutoSci reference | ok | Upstream `/discover` supports `--anchor`, `--negative`, `--topic`, `--from-wiki`, `--venue`, `--year`, and `--limit`, implemented by `tools/discover.py`. |
| Shim argument compatibility | ok | `harness/plugins/autosci/bin/autosci_skill_shim.py` now accepts native discovery arguments, including `$discover --from-wiki --limit 10`. |
| Real discovery backend | ok | Added `harness/plugins/autosci/backends/literature_discover.py` for `wiki`, `topic`, `anchors`, and `venue` modes. |
| Fixture fallback policy | ok | Fixture candidates are retained only for explicit smoke fixture mode; real discovery modes emit live candidates or inconclusive evidence. |
| Discovery gate | ok | Added `harness/evaluators/scientific/literature_discovery_gate.py` and registered it in operator smoke. |
| Limit handling | ok | Backend applies `outputs.limit` and fails gate if completed candidate count exceeds limit. |
| Converter regression guard | ok | Updated converter tests so `literature_discovery.v1` only emits a fixture candidate when raw input explicitly sets `mode=fixture`; normal discovery conversion keeps empty candidates empty. |
| Solar Harness smoke | ok | `$discover --from-wiki --limit 10` now parses through the Solar shim, records `mode=wiki`, `from_wiki=true`, `limit=10`, and emits inconclusive evidence without `local_fixture` when network discovery is disabled. |

### Discover Compatibility Verification Commands

| Command | Result |
|---|---|
| `harness/bin/python3 -m py_compile harness/plugins/autosci/backends/literature_discover.py harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/adapters/autosci_to_literature_discovery.py harness/evaluators/scientific/literature_discovery_gate.py harness/plugins/autosci/bin/autosci_operator_smoke.py` | ok |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_literature_discover.py harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_accepts_discover_from_wiki_limit -q` | ok: 3 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py harness/plugins/autosci/tests/test_phase19_operator_smoke.py harness/plugins/autosci/tests/test_bridge_smoke.py harness/plugins/autosci/tests/test_literature_discover.py -q` | ok: 27 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests -q` | ok: 42 passed. |
| `bash -n harness/solar-harness.sh` | ok |
| `git diff --check -- <discover compatibility files>` | ok |
| `env AUTOSCI_DISABLE_NETWORK_FETCH=1 bash harness/solar-harness.sh '$discover' --from-wiki --limit 10 --run-id solar-discover-from-wiki-smoke` | ok: command parsed and wrote `harness/artifacts/autosci/runs/solar-discover-from-wiki-smoke/literature_discovery.json`; evidence status is `inconclusive`, `outputs.mode=wiki`, `outputs.limit=10`, and no `local_fixture` candidate is present. |

## Phase 19 Native Command Contract and Smoke Boundary Follow-up

Logged: 2026-06-24 EDT

| Item | Status | Evidence |
|---|---|---|
| Pane-output diagnosis | ok | User-provided pane output showed missing native flags, implicit fixture fallbacks, fixture-grade ideas, missing novelty/review gates, unsupported collect/title/checklist paths, and publication compile overclaiming. |
| Native CLI contract | ok | `autosci_skill_shim.py` now accepts native compatibility flags for experiment, ideation, novelty/review, paper planning, and paper compile routes. |
| Explicit smoke boundary | ok | Source-dependent bridge actions no longer run on implicit default fixture input; fixture bridge execution now requires `--smoke` or an explicit `--paper`. |
| Target resolver | ok | Positional native targets such as `exp-001`, `idea-001`, and `paper/` are recorded as `inputs.target` when `--target` is not supplied. |
| Native option evidence | ok | Skill-run evidence records `inputs.native_options` for flags such as `--env`, `--collect`, `--title`, and `--checklist`. |
| Route truthfulness | ok | `exp-status`, `ideate`, `paper-draft`, and `paper-plan` were downgraded from `full`/`executable` to `partial` until wiki state, multi-source evidence, Review LLM, and publication artifacts are fully wired. |
| Bundle fallback guard | ok | `$paper-compile paper/ --checklist` is accepted and recorded, but no longer silently produces a fixture publication bundle without explicit smoke/source context. |
| Experiment fallback guard | ok | `$exp-run exp-001 --env local --collect` is accepted and recorded, but no longer silently runs fixture experiment evidence without explicit smoke/source context. |

### Native Contract Verification Commands

| Command | Result |
|---|---|
| `harness/bin/python3 -m py_compile harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/bin/autosci_operator_smoke.py harness/plugins/autosci/bin/autosci_parity_bridge.py` | ok |
| `python3 -m json.tool harness/plugins/autosci/config/feature_parity_routes.v1.json` | ok |
| `python3 -m json.tool harness/plugins/autosci/config/feature_operator_bindings.v1.json` | ok |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py harness/plugins/autosci/tests/test_phase19_parity_bridge.py harness/plugins/autosci/tests/test_phase19_operator_smoke.py -q` | ok: 18 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests -q` | ok: 46 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py harness/tests/evaluators/scientific/test_autosci_operator_smoke_gate.py -q` | ok: 5 passed. |
| `git diff --check -- <native contract files>` | ok |
| `harness/plugins/autosci/bin/autosci_skill_shim.py '$exp-run' exp-001 --env local --collect --run-id contract-exp-run` | ok: accepted native flags, recorded `target=exp-001`, `env=local`, `collect=true`, `execution_status=gated`, `action_count=0`. |
| `harness/plugins/autosci/bin/autosci_skill_shim.py '$paper-plan' idea-001 --venue ICLR --title "Skill Generation for Inference-Time Agents" --run-id contract-paper-plan` | ok: accepted `--title`, recorded `target=idea-001`, `execution_status=partial`, `action_count=0`. |
| `harness/plugins/autosci/bin/autosci_skill_shim.py '$paper-compile' paper/ --checklist --run-id contract-paper-compile` | ok: accepted `--checklist`, recorded `target=paper/`, `execution_status=gated`, `action_count=0`. |

### Remaining Native Parity Blocks

| Block | Status | Required follow-up |
|---|---|---|
| Full `/ideate` | pending | Wiki maturity scan, failed-idea banlist, external discovery evidence, dual-model brainstorm, novelty/review validation, and wiki writes. |
| Full `/exp-run` | pending | Code generation, dataset/GPU/config inspection, approval loop, local/remote deploy, status mutation, and collect mode. |
| Full `/paper-plan` | pending | Idea-graph evidence map, section/figure/citation plan, `--title` as first-class plan input, and mandatory Review LLM assessment. |
| Full `/paper-compile` | pending | `latexmk`, PDF output, page/font/anonymity/[UNCONFIRMED] checks, and checklist report. |

## Phase 19 Real Ideate Sourcing Follow-up

Logged: 2026-06-24 EDT

| Item | Status | Evidence |
|---|---|---|
| Wiki/discovery sourcing backend | ok | Added `harness/plugins/autosci/backends/idea_source.py` to read Solar workspace wiki pages, graph briefs/open questions, failed ideas, and latest/explicit `literature_discovery.v1` evidence. |
| Non-fixture `/ideate` path | ok | `$ideate <direction>` can now run `generate_ideas -> evaluate_ideas` without a paper fixture when topic/wiki/discovery sources are available. |
| Missing-source behavior | ok | `/ideate` without wiki/discovery/paper evidence now emits inconclusive `idea-source-missing` diagnostics instead of silently generating fixture ideas. |
| Fixture-only guard | ok | `idea_gate.py` rejects fixture-only idea candidates/evaluations unless the evidence is explicit fixture/smoke evidence. |
| Source metadata | ok | Generated ideas include `source_mode`, `generation_path`, `origin_evidence_ids`, `grounding_summary`, and failed-idea overlap status. |
| Evaluation behavior | ok | Real sourced ideas are marked `revise` pending `/novelty` and `/review`; missing-source ideas are marked `inconclusive`; fixture ideas remain allowed only in smoke fixtures. |
| Shim contract | ok | `autosci_skill_shim.py` passes `--from-wiki`, `--wiki-root`, `--discovery-evidence`, `--max-ideas`, `--skip-validation`, and `--skip-pilot` into idea envelopes. |

### Real Ideate Verification Commands

| Command | Result |
|---|---|
| `harness/bin/python3 -m py_compile harness/plugins/autosci/backends/idea_source.py harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/adapters/autosci_to_idea_candidate.py harness/evaluators/scientific/idea_gate.py` | ok |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py harness/plugins/autosci/tests/test_bridge_smoke.py::test_phase11_generate_and_evaluate_ideas_write_native_evidence harness/tests/evaluators/scientific/test_idea_gate.py -q` | ok: 18 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests -q` | ok: 48 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/tests/evaluators/scientific/test_idea_gate.py harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py harness/tests/evaluators/scientific/test_autosci_operator_smoke_gate.py -q` | ok: 8 passed. |

### Remaining Ideate Blocks

| Block | Status | Required follow-up |
|---|---|---|
| External search | pending | WebSearch, Semantic Scholar, and DeepXiv source collection still need live/degraded evidence paths. |
| Dual-model brainstorming | pending | Codex/Review LLM independent generation and merge/dedup are not wired yet. |
| Deep validation | pending | `/novelty --write` and `/review --difficulty hard --focus method` still need first-class integration into `/ideate`. |
| Wiki mutation | pending | Writing proposed/failed ideas plus graph edges and context rebuild remains approval-gated follow-up work. |
| Pilot loop | pending | Pilot spec generation, `/exp-pilot-run`, and `/exp-pilot-eval` remain separate route work. |

## Phase 19 Local Novelty / Review Signal Follow-up

Logged: 2026-06-24 EDT

| Item | Status | Evidence |
|---|---|---|
| Local novelty backend | ok | Added `harness/plugins/autosci/backends/novelty_review.py` to score idea novelty against local wiki/discovery sources and failed-idea memory. |
| Direct `/novelty` route | ok | `$novelty <target> --from-wiki` now maps to evaluate-only evidence without expanding fixture paper/claim/method dependencies. |
| Ideate deep-validation signal | ok | Non-smoke `/ideate` evaluations now include `closest_prior_work`, `review_score`, `review_mode`, `review_available`, `novelty_label`, and conservative recommendations. |
| Review honesty | ok | Review signal is marked `review_mode=local_surrogate` and `review_available=false`; it does not claim Review LLM MCP was used. |
| Gate hardening | ok | `idea_gate.py` requires sourced `advance`/`revise` evaluations to include closest-prior and review-score fields, and still rejects non-smoke fixture evaluations. |
| Missing source behavior | ok | Missing-source evaluations remain `inconclusive`, not promoted. |

### Novelty / Review Verification Commands

| Command | Result |
|---|---|
| `harness/bin/python3 -m py_compile harness/plugins/autosci/backends/novelty_review.py harness/plugins/autosci/backends/idea_source.py harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/evaluators/scientific/idea_gate.py` | ok |
| `python3 -m json.tool harness/plugins/autosci/config/feature_parity_routes.v1.json` | ok |
| `python3 -m json.tool harness/plugins/autosci/config/feature_operator_bindings.v1.json` | ok |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py harness/plugins/autosci/tests/test_bridge_smoke.py::test_phase11_generate_and_evaluate_ideas_write_native_evidence harness/tests/evaluators/scientific/test_idea_gate.py -q` | ok: 20 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests -q` | ok: 49 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/tests/evaluators/scientific/test_idea_gate.py harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py harness/tests/evaluators/scientific/test_autosci_operator_smoke_gate.py -q` | ok: 9 passed. |

### Remaining Deep Validation Blocks

| Block | Status | Required follow-up |
|---|---|---|
| Live external novelty | pending | Connect WebSearch, Semantic Scholar, and DeepXiv results as explicit source evidence. |
| Review LLM MCP | pending | Replace or augment `local_surrogate` with independent Review LLM evidence when MCP is available. |
| `/novelty --write` | pending | Approval-gated update of `wiki/ideas/{slug}.md` frontmatter `novelty_score`. |
| `/review` standalone | pending | General artifact review report with difficulty/focus and wiki entity mapping remains separate from idea evaluation. |

## Phase 19 Novelty Writeback Follow-up

Logged: 2026-06-24 EDT

| Item | Status | Evidence |
|---|---|---|
| Explicit write gate | ok | `/novelty <idea-slug> --write` is the only path that attempts wiki mutation; normal novelty evaluation remains read-only. |
| Wiki idea resolver | ok | Write-back resolves an existing `wiki/ideas/{slug}.md` file from explicit `--wiki-root`, workspace wiki, or repo workspace wiki roots and refuses unresolved free-text targets. |
| Frontmatter mutation | ok | `autosci_bridge.py` updates the target idea YAML `novelty_score` from the numeric evaluation score and leaves missing-frontmatter targets inconclusive instead of fabricating state. |
| Wiki audit log | ok | Successful writes append a `Novelty Writeback` entry to `wiki/log.md` with idea path, score, and source evidence ids. |
| Sidecar evidence | ok | `evaluate_ideas.result.json` now includes `novelty_writeback_path` and sidecar evidence with `schema=novelty_writeback.v1`, `approval_ref=cli --write`, and applied/skipped status. |

### Novelty Writeback Verification Commands

| Command | Result |
|---|---|
| `harness/bin/python3 -m py_compile harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py harness/tests/evaluators/scientific/test_idea_gate.py -q` | ok: 20 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests -q` | ok: 50 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/tests/evaluators/scientific/test_idea_gate.py harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py harness/tests/evaluators/scientific/test_autosci_operator_smoke_gate.py -q` | ok: 9 passed. |
| `git diff --check -- harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |

### Remaining Validation Blocks

| Block | Status | Required follow-up |
|---|---|---|
| Live external novelty | pending | Connect WebSearch, Semantic Scholar, and DeepXiv result evidence before using write-back as a final acceptance gate. |
| Review LLM MCP | pending | Replace or augment local surrogate review with independent Review LLM evidence. |
| `/review` standalone | pending | Add first-class artifact review reports with difficulty/focus routing and wiki entity mapping. |

## Phase 19 Standalone Review Follow-up

Logged: 2026-06-24 EDT

| Item | Status | Evidence |
|---|---|---|
| Standalone `/review` action | ok | Non-smoke `$review <target>` now runs `review_artifact` instead of claim-verification fixture steps. |
| Local artifact resolver | ok | Added `harness/plugins/autosci/backends/artifact_review.py` to resolve explicit artifact paths, paper paths, workspace wiki entities, and explicit `--wiki-root` targets. |
| Evidence schema | ok | Added `artifact_review.v1` schema with review mode, difficulty, focus, score, recommendation, findings, artifacts, and limitations. |
| Review honesty | ok | Evidence declares `review_mode=local_surrogate` and `review_available=false`; limitations explicitly state that independent Review LLM evidence is still required. |
| Gate coverage | ok | Added `artifact_review_gate.py` and registered it in the AutoSci operator smoke gate map. |
| Route truthfulness | ok | `/review` route now advertises `artifact_review.v1` and `review_artifact`, while binding limitations keep fixture smoke and Review LLM gaps explicit. |

### Standalone Review Verification Commands

| Command | Result |
|---|---|
| `harness/bin/python3 -m py_compile harness/plugins/autosci/backends/artifact_review.py harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/bin/autosci_operator_smoke.py harness/evaluators/scientific/artifact_review_gate.py harness/plugins/autosci/tests/test_autosci_skill_shim.py harness/tests/evaluators/scientific/test_artifact_review_gate.py` | ok |
| `python3 -m json.tool harness/plugins/autosci/config/feature_parity_routes.v1.json` | ok |
| `python3 -m json.tool harness/plugins/autosci/config/feature_operator_bindings.v1.json` | ok |
| `python3 -m json.tool harness/schemas/evidence/artifact_review.v1.schema.json` | ok |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py harness/tests/evaluators/scientific/test_artifact_review_gate.py harness/tests/evaluators/scientific/test_idea_gate.py -q` | ok: 23 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests -q` | ok: 51 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/tests/evaluators/scientific/test_artifact_review_gate.py harness/tests/evaluators/scientific/test_idea_gate.py harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py harness/tests/evaluators/scientific/test_autosci_operator_smoke_gate.py -q` | ok: 11 passed. |
| `git diff --check -- <standalone review and novelty writeback files>` | ok |

### Remaining Review Blocks

| Block | Status | Required follow-up |
|---|---|---|
| Review LLM MCP | pending | Add real `mcp__llm-review__chat` execution or explicit unavailable evidence when the server is absent. |
| Entity write-back | pending | Add approval-gated wiki metadata updates for review status/review score after independent review evidence exists. |
| Deep rubric | pending | Replace coarse deterministic findings with native AutoSci rubric sections for method, evidence, novelty, clarity, and reproducibility. |

## Phase 19 Review LLM Evidence State Follow-up

Logged: 2026-06-24 EDT

| Item | Status | Evidence |
|---|---|---|
| Unavailable-state evidence | ok | Standalone `/review` now includes `outputs.review.review_llm.status=unavailable` when no MCP bridge or Review LLM evidence path is supplied. |
| Supplied Review LLM evidence path | ok | Added `--review-llm-evidence <json>` support; valid external `artifact_review.v1` evidence promotes output to `review_mode=review_llm` and `review_available=true`. |
| Conservative merge | ok | Local deterministic findings and Review LLM findings are merged; score/recommendation remain conservative when the external reviewer raises a stricter concern. |
| Gate hardening | ok | `artifact_review_gate.py` now requires local surrogate reviews to carry unavailable/invalid Review LLM state, and Review LLM mode to carry completed Review LLM state. |
| Honesty boundary | ok | The bridge records supplied Review LLM evidence as external evidence; it still does not claim direct MCP invocation. |

### Review LLM Evidence Verification Commands

| Command | Result |
|---|---|
| `harness/bin/python3 -m py_compile harness/plugins/autosci/backends/artifact_review.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/evaluators/scientific/artifact_review_gate.py harness/plugins/autosci/tests/test_autosci_skill_shim.py harness/tests/evaluators/scientific/test_artifact_review_gate.py` | ok |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py harness/tests/evaluators/scientific/test_artifact_review_gate.py -q` | ok: 20 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests -q` | ok: 52 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/tests/evaluators/scientific/test_artifact_review_gate.py harness/tests/evaluators/scientific/test_idea_gate.py harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py harness/tests/evaluators/scientific/test_autosci_operator_smoke_gate.py -q` | ok: 11 passed. |
| `python3 -m json.tool harness/schemas/evidence/artifact_review.v1.schema.json` | ok |
| `git diff --check -- <Review LLM evidence-state files>` | ok |

### Remaining Review LLM Blocks

| Block | Status | Required follow-up |
|---|---|---|
| Direct MCP invocation | pending | Add a safe bridge to call `mcp__llm-review__chat` when the server is actually available in the runtime. |
| MCP response normalization | pending | Validate and normalize live Review LLM response bodies into `artifact_review.v1` before merging. |
| Review write-back | pending | Update wiki review status only after trusted independent review evidence and explicit write approval. |

## Phase 19 External Novelty Evidence Follow-up

Logged: 2026-06-24 EDT

| Item | Status | Evidence |
|---|---|---|
| External novelty unavailable state | ok | Non-smoke `/novelty` now emits `external_novelty.status=unavailable` when no Web/Semantic Scholar/DeepXiv evidence path is supplied. |
| Supplied external evidence | ok | Added `--novelty-evidence <json>` support for external source evidence files containing `sources`, `candidates`, `results`, `papers`, or `items`. |
| Evidence normalization | ok | External sources are normalized into closest-prior rows with provider, title, summary, source id, path, and optional URL. |
| Conservative scoring | ok | External sources are included in overlap scoring; unavailable or invalid external evidence is surfaced as a risk rather than replaced by synthetic sources. |
| Gate hardening | ok | `idea_gate.py` now requires sourced `advance`/`revise` evaluations to carry explicit `external_novelty.status`. |

### External Novelty Verification Commands

| Command | Result |
|---|---|
| `harness/bin/python3 -m py_compile harness/plugins/autosci/backends/novelty_review.py harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/evaluators/scientific/idea_gate.py harness/plugins/autosci/tests/test_autosci_skill_shim.py harness/tests/evaluators/scientific/test_idea_gate.py` | ok |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py harness/tests/evaluators/scientific/test_idea_gate.py -q` | ok: 23 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests -q` | ok: 53 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/tests/evaluators/scientific/test_idea_gate.py harness/tests/evaluators/scientific/test_artifact_review_gate.py harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py harness/tests/evaluators/scientific/test_autosci_operator_smoke_gate.py -q` | ok: 11 passed. |
| `git diff --check -- <external novelty evidence files>` | ok |

### Remaining External Novelty Blocks

| Block | Status | Required follow-up |
|---|---|---|
| Live source fetch | pending | Add actual Web/Semantic Scholar/DeepXiv fetch operators with degraded-source evidence instead of only supplied JSON imports. |
| Source provenance gate | pending | Validate provider-specific ids, URLs, timestamps, and query metadata before allowing promotion. |
| Novelty write trust | pending | Require completed external novelty evidence, not merely local/wiki evidence, before high-confidence write-back. |

## Phase 19 Novelty Write Trust Follow-up

Logged: 2026-06-24 EDT

| Item | Status | Evidence |
|---|---|---|
| Write trust boundary | ok | `/novelty --write` now requires `external_novelty.status=completed` before mutating `wiki/ideas/{slug}.md`. |
| Local-only write behavior | ok | Local/wiki-only novelty evaluation still runs, but write-back emits an inconclusive skipped sidecar and leaves frontmatter unchanged. |
| Completed external write behavior | ok | Supplied completed external novelty evidence allows the existing approval-gated frontmatter update and wiki log append. |
| Sidecar audit | ok | `novelty_writeback.v1` records `external_novelty_status`, checked target paths, applied/skipped state, and skip reason. |

### Novelty Write Trust Verification Commands

| Command | Result |
|---|---|
| `harness/bin/python3 -m py_compile harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py harness/tests/evaluators/scientific/test_idea_gate.py -q` | ok: 24 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests -q` | ok: 54 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/tests/evaluators/scientific/test_idea_gate.py harness/tests/evaluators/scientific/test_artifact_review_gate.py harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py harness/tests/evaluators/scientific/test_autosci_operator_smoke_gate.py -q` | ok: 11 passed. |
| `git diff --check -- harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |

### Remaining Novelty Write Blocks

| Block | Status | Required follow-up |
|---|---|---|
| Provider provenance | pending | Require provider/query/timestamp metadata for external novelty evidence before treating it as high-confidence. |
| Live fetch | pending | Add degraded live Web/S2/DeepXiv operators so users do not need to hand-supply novelty evidence JSON. |
| Review-coupled write | pending | Optionally require completed Review LLM evidence for promotion-grade novelty writes. |

## Phase 19 Online Novelty Fetch Follow-up

Logged: 2026-06-24 EDT

| Item | Status | Evidence |
|---|---|---|
| `/novelty --online` | ok | Added online novelty fetch request path through the shim and `native_options.online`. |
| Semantic Scholar path | ok | Online provider can query Semantic Scholar search API, with API-key header when `SEMANTIC_SCHOLAR_API_KEY` is present. |
| Web path | ok | Online provider can use Serper when `SERPER_API_KEY` is present or a configured `AUTOSCI_WEB_SEARCH_EVIDENCE_URL` endpoint. |
| DeepXiv path | ok | Online provider can use configured `AUTOSCI_DEEPXIV_SEARCH_URL`; missing endpoint is explicit provider-level unavailable state. |
| Degraded evidence | ok | Network disabled, missing credentials, unavailable endpoints, HTTP errors, and empty results produce provider statuses instead of synthetic candidates. |
| Provider audit fields | ok | `external_novelty` now carries provider statuses, query, source count, checked paths, and reason. |

### Online Novelty Verification Commands

| Command | Result |
|---|---|
| `harness/bin/python3 -m py_compile harness/plugins/autosci/backends/novelty_review.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py harness/tests/evaluators/scientific/test_idea_gate.py -q` | ok: 26 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests -q` | ok: 56 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/tests/evaluators/scientific/test_idea_gate.py harness/tests/evaluators/scientific/test_artifact_review_gate.py harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py harness/tests/evaluators/scientific/test_autosci_operator_smoke_gate.py -q` | ok: 11 passed. |
| `git diff --check -- harness/plugins/autosci/backends/novelty_review.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |

### Remaining Online Novelty Blocks

| Block | Status | Required follow-up |
|---|---|---|
| Provider provenance gate | pending | Enforce provider ids, URLs/DOIs/arXiv ids, query metadata, and fetch timestamp before write-grade trust. |
| Live source smoke | pending | Run real online smoke only when network/API keys are approved in the runtime environment. |
| Review-coupled promotion | pending | Require Review LLM evidence in addition to completed external novelty evidence before final promotion. |

## Phase 19 External Novelty Provenance Gate Follow-up

Logged: 2026-06-24 EDT

| Item | Status | Evidence |
|---|---|---|
| Source identifier normalization | ok | External novelty sources now retain URL, DOI, arXiv id, Semantic Scholar id, provider, and source id metadata where supplied. |
| Provider metadata validation | ok | `external_novelty.provenance` validates provider status query metadata, fetch timestamp, and stable source identifiers. |
| Gate hardening | ok | `idea_gate.py` rejects completed external novelty evidence that lacks a provenance status. |
| Write-grade trust | ok | `/novelty --write` now requires both `external_novelty.status=completed` and `external_novelty.provenance.status=passed`. |
| Skipped write audit | ok | Missing provenance produces an inconclusive writeback sidecar and leaves wiki frontmatter/log unchanged. |

### External Novelty Provenance Verification Commands

| Command | Result |
|---|---|
| `harness/bin/python3 -m py_compile harness/plugins/autosci/backends/novelty_review.py harness/plugins/autosci/bin/autosci_bridge.py harness/evaluators/scientific/idea_gate.py harness/plugins/autosci/tests/test_autosci_skill_shim.py harness/tests/evaluators/scientific/test_idea_gate.py` | ok |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py harness/tests/evaluators/scientific/test_idea_gate.py -q` | ok: 28 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests -q` | ok: 57 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/tests/evaluators/scientific/test_idea_gate.py harness/tests/evaluators/scientific/test_artifact_review_gate.py harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py harness/tests/evaluators/scientific/test_autosci_operator_smoke_gate.py -q` | ok: 12 passed. |
| `git diff --check -- <external novelty provenance files>` | ok |

### Remaining Provenance Blocks

| Block | Status | Required follow-up |
|---|---|---|
| Provider-specific schemas | pending | Add stricter schemas per provider, including S2 paperId/externalIds, DeepXiv ids, web URL/domain, and query hash. |
| Live smoke approval | pending | Run a real online smoke with approved API keys/network and archive provider raw evidence. |
| Review-coupled promotion | pending | Require completed Review LLM evidence in addition to write-grade novelty provenance before promoting an idea. |

## Phase 19 Review-Coupled Novelty Write Follow-up

Logged: 2026-06-24 EDT

| Item | Status | Evidence |
|---|---|---|
| Review evidence propagation | ok | `/novelty` now forwards `--review-llm-evidence` into `evaluate_ideas` instead of limiting it to `/review`. |
| Novelty review normalization | ok | Novelty evaluation now reads the existing `artifact_review.v1` Review LLM evidence shape and emits `review_llm`, `review_mode`, and `review_available`. |
| Promotion gate | ok | `/novelty --write` now requires completed external novelty evidence, passed external provenance, and completed Review LLM evidence before mutating wiki idea frontmatter. |
| Gate hardening | ok | `idea_gate.py` rejects sourced evaluations that claim `review_mode=review_llm` without `review_available=true` and completed `review_llm` evidence. |
| Audit trail | ok | `novelty_writeback.v1` records `review_llm_status` alongside external novelty and provenance status. |

### Review-Coupled Novelty Verification Commands

| Command | Result |
|---|---|
| `harness/bin/python3 -m py_compile harness/plugins/autosci/backends/novelty_review.py harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/evaluators/scientific/idea_gate.py harness/plugins/autosci/tests/test_autosci_skill_shim.py harness/tests/evaluators/scientific/test_idea_gate.py` | ok |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py harness/tests/evaluators/scientific/test_idea_gate.py -q` | ok: 30 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests -q` | ok: 58 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/tests/evaluators/scientific/test_idea_gate.py harness/tests/evaluators/scientific/test_artifact_review_gate.py harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py harness/tests/evaluators/scientific/test_autosci_operator_smoke_gate.py -q` | ok: 13 passed. |
| `git diff --check -- harness/plugins/autosci/backends/novelty_review.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/bin/autosci_bridge.py harness/evaluators/scientific/idea_gate.py harness/plugins/autosci/tests/test_autosci_skill_shim.py harness/tests/evaluators/scientific/test_idea_gate.py` | ok |

### Remaining Review-Coupled Blocks

| Block | Status | Required follow-up |
|---|---|---|
| Direct Review LLM MCP invocation | pending | Current path accepts supplied Review LLM evidence; direct MCP execution remains unavailable in this bridge. |
| Provider-specific schemas | pending | External novelty provenance still needs stricter per-provider schemas before final parity. |
| Live smoke approval | pending | Run real online novelty and Review LLM smoke only when runtime network/API access is approved. |

## Phase 19 Provider-Specific Novelty Provenance Follow-up

Logged: 2026-06-24 EDT

| Item | Status | Evidence |
|---|---|---|
| Provider canonicalization | ok | Novelty sources now normalize provider aliases such as `s2`, `semantic scholar`, `web_search`, and `deep_xiv`. |
| Semantic Scholar schema | ok | Write-grade Semantic Scholar evidence now requires `paperId`, `externalIds.DOI`, or `externalIds.ArXiv`; URL-only S2 rows fail provenance. |
| Web schema | ok | Web evidence now requires an absolute `http(s)` URL and records URL domain metadata. |
| DeepXiv schema | ok | DeepXiv evidence now requires a DeepXiv id, DOI, arXiv id, or absolute `http(s)` URL. |
| Provenance report | ok | `external_novelty.provenance` now reports provider schemas, required provider fields, and provider-specific identifier issues. |

### Provider-Specific Novelty Verification Commands

| Command | Result |
|---|---|
| `harness/bin/python3 -m py_compile harness/plugins/autosci/backends/novelty_review.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q` | ok: 25 passed. |

### Remaining Provider-Specific Blocks

| Block | Status | Required follow-up |
|---|---|---|
| Live source smoke | pending | Run real online S2/Web/DeepXiv smoke with approved API keys/network and archive raw provider payloads. |
| Direct Review LLM MCP invocation | pending | Current novelty promotion accepts supplied Review LLM evidence; direct MCP execution remains unavailable in this bridge. |
| Provider payload archives | pending | Persist raw provider payload digests alongside normalized source rows for stronger replay/audit parity. |

## Phase 19 Novelty Provider Payload Digest Follow-up

Logged: 2026-06-24 EDT

| Item | Status | Evidence |
|---|---|---|
| Supplied payload digest | ok | Supplied `--novelty-evidence` JSON now records `raw_payload_ref`, `raw_payload_sha256`, `raw_payload_refs`, and `raw_payload_sha256s` in provider status. |
| Online payload digest | ok | Online Semantic Scholar, Web, and DeepXiv fetch paths now hash raw provider payload JSON before normalization. |
| Source provenance digest | ok | Normalized external sources now carry `raw_payload_sha256` and `raw_payload_status` in source provenance. |
| Write-grade provenance | ok | `external_novelty.provenance.required_fields` now includes `raw_payload_sha256`; missing digests fail provenance. |
| Test coverage | ok | Added assertions that supplied evidence and configured web provider paths emit 64-character SHA-256 digests. |

### Provider Payload Digest Verification Commands

| Command | Result |
|---|---|
| `harness/bin/python3 -m py_compile harness/plugins/autosci/backends/novelty_review.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q` | ok: 25 passed. |

### Remaining Provider Payload Blocks

| Block | Status | Required follow-up |
|---|---|---|
| Raw payload archive files | pending | Current fix records digests and refs; it does not yet persist copied raw payload archives into run artifacts. |
| Live smoke approval | pending | Run real online provider smoke only when network/API access is approved. |
| Direct Review LLM MCP invocation | pending | Current novelty promotion still consumes supplied Review LLM evidence rather than invoking MCP directly. |

## Phase 19 Novelty Provider Payload Archive Follow-up

Logged: 2026-06-24 EDT

| Item | Status | Evidence |
|---|---|---|
| Run-local archive dir | ok | `evaluate_ideas` now configures `external_novelty_payloads/` under the run's evaluate output directory. |
| Supplied payload archive | ok | Supplied external novelty JSON is copied into the run-local archive and linked from provider status. |
| Online payload archive | ok | Online S2/Web/DeepXiv JSON payloads are written into the same archive before source normalization. |
| Source provenance archive | ok | Normalized external source provenance now carries `raw_payload_archive_path` and `raw_payload_archive_status`. |
| Write-grade provenance | ok | Missing completed payload archive now fails `external_novelty.provenance`. |

### Provider Payload Archive Verification Commands

| Command | Result |
|---|---|
| `harness/bin/python3 -m py_compile harness/plugins/autosci/backends/novelty_review.py harness/plugins/autosci/bin/autosci_bridge.py` | ok |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q` | ok: 25 passed. |

### Remaining Provider Payload Archive Blocks

| Block | Status | Required follow-up |
|---|---|---|
| Live smoke approval | pending | Archive behavior is covered with supplied JSON and file-backed web provider tests; real network/API smoke still needs approval. |
| Direct Review LLM MCP invocation | pending | Current novelty promotion still consumes supplied Review LLM evidence rather than invoking MCP directly. |

## Phase 19 Novelty Payload Artifact Visibility Follow-up

Logged: 2026-06-24 EDT

| Item | Status | Evidence |
|---|---|---|
| Idea evaluation artifacts | ok | `idea_evaluation.v1` now includes `external_novelty_payload_json` artifacts for archived provider payload files. |
| Adapter passthrough | ok | `autosci_to_idea_evaluation.py` now passes raw artifacts into the Solar Evidence ABI envelope. |
| Artifact de-duplication | ok | Archive artifact paths are de-duplicated before evidence emission. |
| Test coverage | ok | Shim tests assert supplied and file-backed web novelty payload archives appear in `evaluation_evidence.artifacts`. |

### Novelty Payload Artifact Visibility Verification Commands

| Command | Result |
|---|---|
| `harness/bin/python3 -m py_compile harness/plugins/autosci/adapters/autosci_to_idea_evaluation.py harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q` | ok: 25 passed. |

### Remaining Novelty Artifact Blocks

| Block | Status | Required follow-up |
|---|---|---|
| Live smoke approval | pending | Artifact visibility is covered with local payloads; real provider payload archives still need approved network/API smoke. |
| Direct Review LLM MCP invocation | pending | Current novelty promotion still consumes supplied Review LLM evidence rather than invoking MCP directly. |

## Phase 19 Review LLM Command Bridge Follow-up

Logged: 2026-06-24 EDT

| Item | Status | Evidence |
|---|---|---|
| Explicit command bridge | ok | `/review` and `/novelty` now support `--review-llm-command` and `AUTOSCI_REVIEW_LLM_COMMAND` for direct configured Review LLM invocation. |
| Request contract | ok | The command bridge sends `review_llm_request.v1` JSON on stdin, including difficulty, focus, inputs, and review target metadata. |
| Existing output contract | ok | The command bridge must return the existing `artifact_review.v1` Review LLM JSON shape on stdout; no new review schema was introduced. |
| Failure truthfulness | ok | Missing command remains `unavailable`; non-zero exit, timeout, invalid JSON, and invalid review shape are surfaced as `failed` or `invalid`. |
| Novelty promotion | ok | `/novelty --write` can now satisfy the completed Review LLM requirement through the command bridge, not only supplied evidence files. |

### Review LLM Command Bridge Verification Commands

| Command | Result |
|---|---|
| `harness/bin/python3 -m py_compile harness/plugins/autosci/backends/artifact_review.py harness/plugins/autosci/backends/novelty_review.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q` | ok: 27 passed. |

### Remaining Review LLM Blocks

| Block | Status | Required follow-up |
|---|---|---|
| Native MCP tool exposure | pending | Current session does not expose `mcp__llm-review__chat`; the command bridge is the direct configurable invocation path until the MCP tool is available. |
| Live Review LLM smoke | pending | Needs an approved real Review LLM command/tool in the runtime environment. |

## Phase 19 Route Truthfulness Follow-up

Logged: 2026-06-24 EDT

| Item | Status | Evidence |
|---|---|---|
| Exp-design overclaim fixed | ok | `/exp-design` route is now `partial`/`route_plan`/`dry_run_only` instead of `full` while native wiki/runtime/review-backed design validation remains incomplete. |
| Operator binding aligned | ok | `exp-design` physical operator status is now `partial`; limitation no longer claims executable full parity. |
| Gate hardening | ok | `autosci_feature_parity_gate.py` now rejects `full` routes whose limitations describe fixture, smoke-only, local-surrogate, or unimplemented behavior. |
| Regression coverage | ok | Tests now assert `exp-design` is partial and full routes with fixture limitations fail parity evaluation. |

### Route Truthfulness Verification Commands

| Command | Result |
|---|---|
| `harness/bin/python3 -m py_compile harness/evaluators/scientific/autosci_feature_parity_gate.py harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py harness/plugins/autosci/tests/test_phase19_parity_bridge.py` | ok |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py -q` | ok: 4 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_phase19_parity_bridge.py -q` | ok: 4 passed. |

### Remaining Route Truthfulness Blocks

| Block | Status | Required follow-up |
|---|---|---|
| Full-route live evidence | pending | Remaining full routes still need periodic live evidence audits, especially discovery and ingest under real source conditions. |
| Operator binding audit | pending | Other partial/gated bindings should stay aligned as native capabilities become executable. |

## Phase 19 Wiki State Resolver Fallback Follow-up

Logged: 2026-06-24 EDT

| Item | Status | Evidence |
|---|---|---|
| Design target fallback | ok | Non-smoke experiment design without a resolved claim/idea/target now returns `inconclusive` with `experiment-unresolved` instead of defaulting to `idea-001`. |
| Run plan fallback | ok | Non-smoke experiment execution without experiment plan evidence now returns `inconclusive` with `experiment-unresolved` instead of defaulting to `exp-001`. |
| Monitor fallback | ok | Non-smoke experiment monitoring without plan/result evidence reports unknown state against `experiment-unresolved`. |
| Fixture compatibility | ok | Explicit fixture/smoke paths still keep deterministic `claim-001`, `idea-001`, and `exp-001` fixtures for bounded smoke tests. |
| Test coverage | ok | Bridge tests cover missing-target design and missing-plan run boundaries. |

### Wiki State Resolver Fallback Verification Commands

| Command | Result |
|---|---|
| `harness/bin/python3 -m py_compile harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/adapters/autosci_to_experiment_plan.py harness/plugins/autosci/tests/test_bridge_smoke.py` | ok |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_bridge_smoke.py -q` | ok: 16 passed. |

### Remaining Wiki Resolver Blocks

| Block | Status | Required follow-up |
|---|---|---|
| Full wiki entity resolver | pending | Experiment and paper routes still need richer lookup across wiki experiments, ideas, graph edges, and run artifacts. |
| Approved wiki mutation | pending | set-meta/add-edge/log/rebuild mutations remain approval-gated and not fully implemented. |

## Phase 19 Paper Compile Checklist Follow-up

Logged: 2026-06-24 EDT

| Item | Status | Evidence |
|---|---|---|
| Native checklist action | ok | `$paper-compile --checklist` now maps to `compile_paper` instead of route-only fallback evidence. |
| Compile diagnostics | ok | The bridge writes `paper_compile_checklist.json` and `paper_compile_diagnostics.md` with target, source, PDF, bibliography, and latexmk checks. |
| Truthful publication evidence | ok | `compile_paper` emits `publication_bundle.v1` using only files that actually exist; missing PDF/source/toolchain state remains explicit. |
| No fake compilation | ok | The path does not run latexmk, mutate sources, or claim a PDF was produced by Solar. Missing compile readiness yields `inconclusive` / schema-only action status. |
| Gate path resolution | ok | `publication_gate.py` now resolves bundle `files[].path` against the active `HARNESS_DIR` artifact root as well as the repo harness root. |

### Paper Compile Checklist Verification Commands

| Command | Result |
|---|---|
| `harness/bin/python3 -m py_compile harness/evaluators/scientific/publication_gate.py harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/bin/autosci_operator_smoke.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_accepts_paper_compile_checklist_without_bundle_fallback -q` | ok: 1 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests -q` | ok: 63 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/tests/evaluators/scientific/test_idea_gate.py harness/tests/evaluators/scientific/test_artifact_review_gate.py harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py harness/tests/evaluators/scientific/test_autosci_operator_smoke_gate.py harness/tests/evaluators/scientific/test_report_gate.py -q` | ok: 18 passed. |

### Remaining Paper Compile Blocks

| Block | Status | Required follow-up |
|---|---|---|
| Real LaTeX execution | pending | Running latexmk and producing a new PDF still needs an approval-gated toolchain execution path. |
| Auto-fix mode | pending | `--fix` is recorded but not executed; source mutation should remain gated until implemented. |

## Phase 19 Wiki Mutation Layer Follow-up

Logged: 2026-06-24 EDT

| Item | Status | Evidence |
|---|---|---|
| Set-meta path | ok | Promotion-grade `/novelty --write` already updates the targeted idea frontmatter `novelty_score` only after completed external novelty evidence, passed provenance, and completed Review LLM evidence. |
| Structured add-edge | ok | Successful novelty write-back now appends a structured `novelty_evaluated` edge into `wiki/graph/edges.jsonl`. |
| Mutation log | ok | Successful write-back continues to append `wiki/log.md` with timestamp, score, idea path, and evidence ids. |
| Lightweight rebuild | ok | Successful write-back rebuilds `wiki/index.md` and `wiki/graph/context_brief.md`; the workspace projector now preserves mutation target/edge/log context after projection. |
| Truthful skip behavior | ok | Evidence gaps, failed provenance, missing Review LLM, unresolved targets, or missing YAML frontmatter still produce `novelty_writeback.v1` as `inconclusive` without mutating wiki files. |

### Wiki Mutation Layer Verification Commands

| Command | Result |
|---|---|
| `harness/bin/python3 -m py_compile harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/bin/autosci_workspace_projector.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_novelty_write_updates_with_external_and_review_llm_evidence harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_novelty_write_uses_review_llm_command_bridge harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_novelty_write_skips_without_external_evidence harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_novelty_write_skips_without_review_llm_evidence -q` | ok: 4 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_autosci_skill_projection.py -q` | ok: 1 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests -q` | ok: 63 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/tests/evaluators/scientific/test_idea_gate.py harness/tests/evaluators/scientific/test_artifact_review_gate.py harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py harness/tests/evaluators/scientific/test_autosci_operator_smoke_gate.py harness/tests/evaluators/scientific/test_report_gate.py -q` | ok: 18 passed. |

### Remaining Wiki Mutation Blocks

| Block | Status | Required follow-up |
|---|---|---|
| General wiki edit route | pending | `/edit`, `/prefill`, `/reset`, and broad wiki/raw mutations remain approval-gated and route-scoped; this follow-up only completes the novelty promotion write path. |
| Destructive mutations | pending | Delete/reset/rebuild actions still need explicit confirmation and before/after evidence before implementation. |

## Phase 19 Experiment Lifecycle Collect Follow-up

Logged: 2026-06-24 EDT

| Item | Status | Evidence |
|---|---|---|
| Collect option routing | ok | `$exp-run --collect` now maps to a bounded `monitor_experiment` diagnostics action instead of emitting route-only evidence. |
| No fake execution | ok | Collect mode does not deploy, run code, SSH, rsync, or pull remote files; missing runtime artifacts remain `unknown` / `inconclusive`. |
| Target preservation | ok | Non-smoke collect diagnostics preserve the explicit experiment target instead of falling back to `exp-001` unless the user supplied that target. |
| Gate truthfulness | ok | Missing result evidence now produces `experiment_status.v1` with top-level `status: inconclusive`, yielding schema-only action status rather than a false pass. |
| Native options surfaced | ok | `env` and `collect` remain visible in native options and monitor inputs for follow-up approved collection. |

### Experiment Lifecycle Collect Verification Commands

| Command | Result |
|---|---|
| `harness/bin/python3 -m py_compile harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_accepts_exp_run_native_options_without_fixture_fallback harness/plugins/autosci/tests/test_bridge_smoke.py::test_phase12_design_run_and_monitor_experiment_write_native_evidence harness/plugins/autosci/tests/test_bridge_smoke.py::test_phase12_run_without_plan_does_not_default_to_exp_001 -q` | ok: 3 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/tests/evaluators/scientific/test_experiment_status_gate.py -q` | ok: 2 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests -q` | ok: 63 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/tests/evaluators/scientific/test_idea_gate.py harness/tests/evaluators/scientific/test_artifact_review_gate.py harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py harness/tests/evaluators/scientific/test_autosci_operator_smoke_gate.py harness/tests/evaluators/scientific/test_report_gate.py harness/tests/evaluators/scientific/test_experiment_status_gate.py -q` | ok: 20 passed. |

### Remaining Experiment Lifecycle Blocks

| Block | Status | Required follow-up |
|---|---|---|
| Approved run execution | pending | Actual local/remote experiment execution remains approval-gated and requires concrete command allowlists, resource limits, and runtime artifacts. |
| Approved result retrieval | pending | Remote collect/pull-results still needs an approved tool path plus before/after artifact evidence. |

## Phase 19 Publication And Report Native Sidecar Follow-up

Logged: 2026-06-24 EDT

| Item | Status | Evidence |
|---|---|---|
| Paper plan action | ok | `$paper-plan` now runs `plan_report` and emits `scientific_report.v1` plus paper plan JSON/Markdown sidecars. |
| Survey action | ok | `$survey` now runs `write_survey` and emits `scientific_report.v1` plus survey plan/Markdown sidecars. |
| Rebuttal action | ok | `$rebuttal` now runs `draft_rebuttal` and emits `publication_bundle.v1` with rebuttal Markdown and response-map JSON. |
| Poster action | ok | `$poster` now runs `build_poster` and emits `publication_bundle.v1` with local poster HTML and validation JSON. |
| Truthful status | ok | Request-only targets remain `inconclusive` / schema-only; only real source evidence payloads can promote report sidecar status beyond scaffold. |

### Publication And Report Sidecar Verification Commands

| Command | Result |
|---|---|
| `harness/bin/python3 -m py_compile harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/bin/autosci_operator_smoke.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_accepts_paper_plan_title_without_topic_fallback harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_runs_survey_rebuttal_and_poster_native_sidecars -q` | ok: 2 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests -q` | ok: 64 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/tests/evaluators/scientific/test_report_gate.py harness/tests/evaluators/scientific/test_autosci_operator_smoke_gate.py harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py -q` | ok: 10 passed. |

### Remaining Publication And Report Blocks

| Block | Status | Required follow-up |
|---|---|---|
| Browser/poster rendering | pending | Poster HTML is generated, but browser overflow probe and PNG export remain approval/environment-gated. |
| Citation expansion | pending | Survey and paper plan sidecars do not imply live citation expansion or exhaustive literature coverage. |
| Review stress-test | pending | Rebuttal stress-test still needs Review LLM evidence or an approved Review LLM command/tool. |

## Phase 19 Wiki And Control Proposal Follow-up

Logged: 2026-06-24 EDT

| Item | Status | Evidence |
|---|---|---|
| Prefill proposal action | ok | `$prefill` now runs `prefill_foundations` and emits `research_memory_update.v1` proposed foundation-page evidence without mutating wiki files. |
| Edit proposal action | ok | `$edit` now runs `edit_wiki_plan` and emits `research_memory_update.v1` bounded edit-plan evidence without set-meta/add-edge side effects. |
| Setup status action | ok | `$setup` now runs `setup_status` and emits `workflow_evolution.v1` setup checklist/proposal evidence without writing secrets or config. |
| Reset plan action | ok | `$reset` now runs `reset_plan` and emits `workflow_evolution.v1` reset checklist/proposal evidence without destructive deletes. |
| Approval controls | ok | Setup/reset proposal evidence includes manual and gate changes, human approval controls, recommended-changes Markdown, and patch-candidates directory. |

### Wiki And Control Proposal Verification Commands

| Command | Result |
|---|---|
| `harness/bin/python3 -m py_compile harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/bin/autosci_operator_smoke.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_runs_wiki_and_control_proposal_actions harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_keeps_setup_gated -q` | ok: 2 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests -q` | ok: 65 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/tests/evaluators/scientific/test_idea_gate.py harness/tests/evaluators/scientific/test_artifact_review_gate.py harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py harness/tests/evaluators/scientific/test_autosci_operator_smoke_gate.py harness/tests/evaluators/scientific/test_report_gate.py harness/tests/evaluators/scientific/test_experiment_status_gate.py harness/tests/evaluators/scientific/test_workflow_evolution_gate.py -q` | ok: 22 passed. |

### Remaining Wiki And Control Blocks

| Block | Status | Required follow-up |
|---|---|---|
| Approved wiki apply | pending | Proposed edit/prefill evidence still needs explicit approval and before/after evidence before mutating wiki/raw files. |
| Secret/config writes | pending | Setup remains proposal-only until the user supplies exact values and approves the write scope. |
| Destructive reset | pending | Reset remains proposal-only until explicit destructive confirmation and rollback evidence are available. |

## Phase 19 Ask Check Init Diagnostic Follow-up

Logged: 2026-06-24 EDT

| Item | Status | Evidence |
|---|---|---|
| Ask diagnostic action | ok | `$ask` now runs `ask_wiki`, writes an answer Markdown artifact, and emits `research_memory_update.v1` no-op evidence marked `inconclusive` until retrieval/model evidence exists. |
| Check diagnostic action | ok | `$check` now runs `check_wiki_health` and emits `workflow_evolution.v1` wiki-health proposal evidence with approval controls. |
| Init diagnostic action | ok | `$init` now runs `init_sources` and emits `literature_discovery.v1` init-plan evidence marked `inconclusive` when no candidates/source manifests are available. |
| Adapter truthfulness | ok | `research_memory_update.v1` adapter now preserves raw `status` and `artifacts`, allowing diagnostics to stay schema-only instead of defaulting to completed. |

### Ask Check Init Verification Commands

| Command | Result |
|---|---|
| `harness/bin/python3 -m py_compile harness/plugins/autosci/adapters/autosci_to_research_memory_update.py harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/bin/autosci_operator_smoke.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_runs_ask_check_and_init_diagnostics -q` | ok: 1 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests -q` | ok: 66 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/tests/evaluators/scientific/test_idea_gate.py harness/tests/evaluators/scientific/test_artifact_review_gate.py harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py harness/tests/evaluators/scientific/test_autosci_operator_smoke_gate.py harness/tests/evaluators/scientific/test_report_gate.py harness/tests/evaluators/scientific/test_experiment_status_gate.py harness/tests/evaluators/scientific/test_workflow_evolution_gate.py -q` | ok: 22 passed. |

### Remaining Ask Check Init Blocks

| Block | Status | Required follow-up |
|---|---|---|
| Ask model synthesis | pending | `$ask` still needs retrieval-backed model synthesis and confidence calibration before completed answer evidence. |
| Check content quality | pending | `$check` structural proposal does not imply LLM quality review without supplied model output evidence. |
| Init bulk fetch | pending | `$init` still needs approved network/source fetch and fan-in ingest before completed discovery evidence. |

## Phase 19 Remaining Backend Action Mapping Follow-up

Logged: 2026-06-24 EDT

| Item | Status | Evidence |
|---|---|---|
| Daily arXiv action | ok | `$daily-arxiv` now runs `daily_arxiv_prepare_finalize` and emits `literature_discovery.v1` plan evidence without network/email/auto-ingest side effects. |
| Pilot eval action | ok | `$exp-pilot-eval` now runs `evaluate_pilot_result` and emits `claim_verdict.v1` inconclusive evidence until pilot result evidence is supplied. |
| Pilot run action | ok | `$exp-pilot-run` now runs `run_pilot_experiment` and emits `experiment_result.v1` inconclusive diagnostics without local/remote execution. |
| Refine action | ok | `$refine` now runs `refine_artifact` and emits `workflow_evolution.v1` proposed-only refinement evidence. |
| Research lifecycle action | ok | `$research` now runs `run_research_lifecycle` and emits `workflow_evolution.v1` lifecycle proposal evidence instead of route-only fallback. |
| Visualize action | ok | `$visualize` now runs `visualize_graph` and emits `research_graph_update.v1` visualization proposal evidence without serving/opening UI. |
| Backend action coverage | ok | All configured `solar_backend_action` values in `feature_parity_routes.v1.json` now have bridge action handlers. |

### Remaining Backend Action Verification Commands

| Command | Result |
|---|---|
| `harness/bin/python3 -m py_compile harness/plugins/autosci/adapters/autosci_to_research_memory_update.py harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/bin/autosci_operator_smoke.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_runs_remaining_gated_backend_actions -q` | ok: 1 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests -q` | ok: 67 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/tests/evaluators/scientific/test_idea_gate.py harness/tests/evaluators/scientific/test_artifact_review_gate.py harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py harness/tests/evaluators/scientific/test_autosci_operator_smoke_gate.py harness/tests/evaluators/scientific/test_report_gate.py harness/tests/evaluators/scientific/test_experiment_status_gate.py harness/tests/evaluators/scientific/test_workflow_evolution_gate.py -q` | ok: 22 passed. |
| `backend action coverage script` | ok: `missing_count: 0`. |

### Remaining Full-Parity Blocks

| Block | Status | Required follow-up |
|---|---|---|
| External side effects | pending | Network fetch, SMTP, browser/UI serving, local/remote experiment execution, and destructive reset still require explicit approval and runtime evidence. |
| Completed intelligence outputs | pending | Ask synthesis, check quality review, citation expansion, Review LLM stress-test, and full lifecycle orchestration need actual model/source evidence before completed status. |

## Phase 19 Wiki Retrieval And Graph Gate Follow-up

Logged: 2026-06-24 EDT

| Item | Status | Evidence |
|---|---|---|
| Ask wiki retrieval | ok | `$ask` now performs local lexical retrieval over workspace wiki Markdown and writes `ask_wiki_retrieval.json` plus answer Markdown with source snippets. |
| Ask truthfulness | ok | `$ask` remains `inconclusive` until model synthesis/confidence evidence is supplied; retrieval is not presented as a completed answer. |
| Wiki health diagnostics | ok | `$check` now inspects wiki root existence, expected subdirectories, Markdown page count, and `graph/edges.jsonl` JSON/field validity. |
| Wiki-root routing | ok | `--wiki-root` now propagates into ask/check/init diagnostic actions. |
| Graph update gate | ok | Added deterministic `research_graph_update.v1` gate and registered it in operator smoke; graph update and visualize proposal evidence are now gate-checked. |

### Wiki Retrieval And Graph Gate Verification Commands

| Command | Result |
|---|---|
| `harness/bin/python3 -m py_compile harness/evaluators/scientific/graph_update_gate.py harness/plugins/autosci/adapters/autosci_to_research_memory_update.py harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/bin/autosci_operator_smoke.py harness/plugins/autosci/tests/test_autosci_skill_shim.py harness/plugins/autosci/tests/test_phase19_operator_smoke.py harness/tests/evaluators/scientific/test_graph_update_gate.py` | ok |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_runs_ask_check_and_init_diagnostics harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_ask_and_check_read_workspace_wiki -q` | ok: 2 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/tests/evaluators/scientific/test_graph_update_gate.py harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_runs_remaining_gated_backend_actions -q` | ok: 3 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests -q` | ok: 68 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/tests/evaluators/scientific/test_idea_gate.py harness/tests/evaluators/scientific/test_artifact_review_gate.py harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py harness/tests/evaluators/scientific/test_autosci_operator_smoke_gate.py harness/tests/evaluators/scientific/test_report_gate.py harness/tests/evaluators/scientific/test_experiment_status_gate.py harness/tests/evaluators/scientific/test_workflow_evolution_gate.py harness/tests/evaluators/scientific/test_graph_update_gate.py -q` | ok: 24 passed. |

### Remaining Wiki Retrieval And Graph Blocks

| Block | Status | Required follow-up |
|---|---|---|
| Ask synthesis | pending | Lexical retrieval still needs model synthesis and confidence/review evidence before completed answer status. |
| Check content review | pending | Structural wiki health does not replace LLM-assisted content quality checks. |
| Visualization rendering | pending | Graph update proposals are gate-checked, but Canvas/browser rendering remains approval-gated. |

## Phase 19 Approval Runtime Contract Follow-up

Logged: 2026-06-24 EDT

| Item | Status | Evidence |
|---|---|---|
| CLI approval inputs | ok | `autosci_skill_shim.py` now accepts `--approval-ref`, `--allowlist-evidence`, `--runtime-evidence`, `--before-artifact`, and `--after-artifact`, and forwards them into bridge envelopes plus `native_options`. |
| Approval contract sidecar | ok | `autosci_bridge.py` now writes `autosci_approval_contract.v1` JSON sidecars with action, side effects, approval ref, allowlist/runtime/before/after artifact paths, readiness flags, and explicit missing fields. |
| Gated source fetch paths | ok | `$init` and `$daily-arxiv` now attach approval contract artifacts instead of only prose limitations for network fetch, digest send, auto-ingest, and wiki fan-in paths. |
| Gated execution paths | ok | `$exp-pilot-run`, `$paper-compile`, `$poster`, `$setup`, `$reset`, `$refine`, `$research`, and `$visualize` now attach approval contract evidence for their protected runtime, browser, compile, mutation, or lifecycle side effects. |
| Truthfulness guard | ok | Approval evidence does not mark these actions as completed; poster/browser rendering, pilot execution, compile execution, and lifecycle mutation remain inconclusive or proposed-only unless real runtime artifacts are supplied and separately interpreted. |
| Graph artifact preservation | ok | `research_graph_update.v1` adapter now preserves raw `artifacts` and `status`, allowing visualization approval contracts to remain visible to gates and smoke tests. |

### Approval Runtime Contract Verification Commands

| Command | Result |
|---|---|
| `harness/bin/python3 -m py_compile harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/adapters/autosci_to_research_graph_update.py` | ok |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q` | ok: 33 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests -q` | ok: 69 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/tests/evaluators/scientific/test_artifact_review_gate.py harness/tests/evaluators/scientific/test_claim_verdict_gate.py harness/tests/evaluators/scientific/test_claims_gate.py harness/tests/evaluators/scientific/test_code_evidence_gate.py harness/tests/evaluators/scientific/test_experiment_plan_gate.py harness/tests/evaluators/scientific/test_experiment_result_gate.py harness/tests/evaluators/scientific/test_experiment_status_gate.py harness/tests/evaluators/scientific/test_graph_update_gate.py harness/tests/evaluators/scientific/test_idea_gate.py harness/tests/evaluators/scientific/test_lifecycle_gate.py harness/tests/evaluators/scientific/test_report_gate.py harness/tests/evaluators/scientific/test_workflow_evolution_gate.py -q` | ok: 38 passed. |
| `env PYTHONPATH=harness HARNESS_DIR=/tmp/autosci-operator-smoke harness/bin/python3 harness/plugins/autosci/bin/autosci_operator_smoke.py skillgen --out /tmp/autosci-operator-smoke/operator_smoke.json` | ok: 28 routes, 28 bound, 0 failed, 10 gated. |
| `git diff --check -- harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/adapters/autosci_to_research_graph_update.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |

### Remaining Approval Runtime Blocks

| Block | Status | Required follow-up |
|---|---|---|
| Semantic runtime verification | ok | Implemented in the Semantic Runtime Verification follow-up below; remaining work is schema hardening and real executors. |
| Real side-effect executors | pending | Network fetch, SMTP, browser render/export, latexmk compile, local/remote pilot execution, and destructive reset remain blocked unless a separate approved executor is implemented. |
| Full lifecycle orchestration | pending | `$research` still emits a workflow proposal; it does not yet orchestrate every native AutoSci stage into one real multi-step run. |

## Phase 19 Semantic Runtime Verification Follow-up

Logged: 2026-06-24 EDT

| Item | Status | Evidence |
|---|---|---|
| Runtime parser layer | ok | `autosci_bridge.py` now loads supplied runtime evidence JSON/text and writes `autosci_runtime_semantic_verification.v1` results into approval contract sidecars. |
| Daily arXiv semantic verification | ok | `$daily-arxiv` can now promote to completed `literature_discovery.v1` only when approved runtime evidence has successful fetch status and non-empty candidate papers. |
| Init source semantic verification | ok | `$init` shares the same candidate parser for approved runtime source manifests while remaining inconclusive without semantic candidate evidence. |
| Pilot runtime verification | ok | `$exp-pilot-run` can now map approved runtime `exit_code`, `outcome`, and `metrics` into completed `experiment_result.v1`; otherwise it remains inconclusive. |
| Poster runtime verification | ok | `$poster` now checks approved runtime evidence for browser render, overflow pass, and PNG export, and records the semantic result in `poster_validation.json`. |
| Paper compile runtime verification | ok | `$paper-compile` now checks approved runtime evidence for compile exit success and generated/existing PDF evidence before marking compile runtime semantics as verified. |
| Truthfulness guard | ok | Verified runtime evidence still does not mean the bridge itself executed the side effect; limitations explicitly state the bridge verified supplied evidence and did not launch network/browser/latex/experiment commands. |

### Semantic Runtime Verification Commands

| Command | Result |
|---|---|
| `harness/bin/python3 -m py_compile harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_records_approval_runtime_contract_for_gated_actions harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_uses_semantic_runtime_evidence_for_gated_results harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_runs_remaining_gated_backend_actions harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_accepts_paper_compile_checklist_without_bundle_fallback -q` | ok: 4 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests -q` | ok: 70 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/tests/evaluators/scientific -q` | ok: 47 passed. |
| `env PYTHONPATH=harness HARNESS_DIR=/tmp/autosci-operator-smoke harness/bin/python3 harness/plugins/autosci/bin/autosci_operator_smoke.py skillgen --out /tmp/autosci-operator-smoke/operator_smoke_semantic.json` | ok: 28 routes, 28 bound, 0 failed, 10 gated. |
| `git diff --check -- docs/integrations/autosci/phase19-progress-log.md harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |

### Remaining Semantic Runtime Blocks

| Block | Status | Required follow-up |
|---|---|---|
| Real side-effect executors | warn | Paper compile now has an approved latexmk executor; network fetch, SMTP, browser render/export, remote execution, and destructive reset executors remain pending. |
| Runtime schema hardening | ok | Implemented in the Runtime Schema And Compile Executor follow-up below. |
| Full lifecycle orchestration | pending | `$research` still needs orchestration across discovery, ideation, novelty/review, experiment, report, and publication stages. |

## Phase 19 Runtime Schema And Compile Executor Follow-up

Logged: 2026-06-24 EDT

| Item | Status | Evidence |
|---|---|---|
| Runtime evidence ABI | ok | Added `autosci_runtime_evidence.v1` schema for approval-gated runtime outputs with action, approval ref, command, exit code, checks, candidates, metrics, poster render fields, and compile PDF fields. |
| Runtime evidence gate | ok | Added `autosci_runtime_evidence_gate.py` with action-specific completed checks for source fetch, pilot run, poster render/export, and paper compile. |
| Bridge ABI consumption | ok | `autosci_bridge.py` now reads formal runtime evidence from `outputs.runtime` while retaining compatibility with simpler JSON runtime files. |
| Paper compile executor | ok | `$paper-compile --execute-approved` can now run an implemented local latexmk executor only when approval, allowlist evidence, and before artifact preflight are present. |
| Compile executor provenance | ok | The executor writes `autosci_runtime_evidence.v1`, stdout/stderr sidecars, compiled PDF artifact entries, and routes the result back through the approval contract and semantic runtime verifier. |
| Default safety | ok | `$paper-compile` default behavior is unchanged; no latexmk command runs unless the user passes `--execute-approved` and satisfies preflight. |

### Runtime Schema And Compile Executor Verification Commands

| Command | Result |
|---|---|
| `python3 -m json.tool harness/schemas/evidence/autosci_runtime_evidence.v1.schema.json` | ok |
| `harness/bin/python3 -m py_compile harness/evaluators/scientific/autosci_runtime_evidence_gate.py harness/tests/evaluators/scientific/test_autosci_runtime_evidence_gate.py harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/tests/evaluators/scientific/test_autosci_runtime_evidence_gate.py harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_uses_semantic_runtime_evidence_for_gated_results harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_records_approval_runtime_contract_for_gated_actions -q` | ok: 6 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_executes_approved_paper_compile_executor harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_uses_semantic_runtime_evidence_for_gated_results harness/tests/evaluators/scientific/test_autosci_runtime_evidence_gate.py -q` | ok: 6 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests -q` | ok: 71 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/tests/evaluators/scientific -q` | ok: 51 passed. |
| `env PYTHONPATH=harness HARNESS_DIR=/tmp/autosci-operator-smoke harness/bin/python3 harness/plugins/autosci/bin/autosci_operator_smoke.py skillgen --out /tmp/autosci-operator-smoke/operator_smoke_compile_executor.json` | ok: 28 routes, 28 bound, 0 failed, 10 gated. |
| `git diff --check -- docs/integrations/autosci/phase19-progress-log.md harness/schemas/evidence/autosci_runtime_evidence.v1.schema.json harness/evaluators/scientific/autosci_runtime_evidence_gate.py harness/tests/evaluators/scientific/test_autosci_runtime_evidence_gate.py harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |

### Remaining Runtime Executor Blocks

| Block | Status | Required follow-up |
|---|---|---|
| Browser/poster executor | ok | Implemented in the Poster Approved Executor follow-up below. |
| Source fetch/email executors | pending | Daily arXiv/source initialization can verify supplied runtime evidence, but network fetch and email send executors are not implemented. |
| Pilot executor | pending | Pilot runtime verification exists, but local/remote process execution and result collection executor are not implemented. |
| Destructive/control executors | pending | Setup/reset/refine/research lifecycle mutation executors remain proposal-only and approval-gated. |
| Full lifecycle orchestration | pending | `$research` still needs orchestration across discovery, ideation, novelty/review, experiment, report, and publication stages. |

## Phase 19 Wiki State Resolver Follow-up

Logged: 2026-06-24 EDT

| Item | Status | Evidence |
|---|---|---|
| Wiki-first resolver ABI | ok | Added a read-only `autosci_wiki_state_resolver.v1` sidecar from `autosci_bridge.py` for `ideas`, `experiments`, `outputs`, and `graph/edges.jsonl`. |
| Frontmatter/entity parsing | ok | Resolver now records slug/id/title/status, idea `novelty_score`, `linked_experiments`, experiment `run_log`, `run_log_exists`, and output links. |
| Graph edge parsing | ok | Resolver parses JSONL graph edges with source/target/relation/evidence ids, records invalid rows separately, and enriches linked experiments/outputs from graph edges. |
| Target truthfulness | ok | Resolver records `resolution.target_type`, `target_id`, `target_path`, and `fallback_used=false`; unresolved targets stay `unresolved` rather than silently becoming `idea-001` or `exp-001`. |
| Action integration | ok | `generate_ideas`, `evaluate_ideas`, `design_experiment`, and `monitor_experiment` now attach the resolver sidecar when wiki/target inputs are present. |
| Novelty target sourcing | ok | `$novelty` can now create the evaluated idea from a resolved wiki idea when no upstream `idea_candidate.v1` evidence exists. |
| Experiment status sourcing | ok | `$exp-status` can now resolve the experiment id from wiki experiment state before falling back to unresolved status. |
| Adapter propagation | ok | `idea_candidate.v1` and `experiment_plan.v1` adapters now preserve action artifacts so resolver evidence is visible to gates and pane output. |
| Gate hardening | ok | `idea_gate.py` now treats `source_mode=wiki_state` as sourced evidence, so wiki-resolved novelty evaluations must still carry closest-prior, review score/mode, and external novelty status. |

### Wiki State Resolver Verification Commands

| Command | Result |
|---|---|
| `python3 -m py_compile harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/adapters/autosci_to_idea_candidate.py harness/plugins/autosci/adapters/autosci_to_experiment_plan.py` | ok |
| `.venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_wiki_state_resolver_parses_entities_and_edges harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_exp_status_resolves_wiki_experiment_without_default_fallback -q` | ok: 2 passed. |
| `.venv/bin/python -m pytest harness/plugins/autosci/tests -q` | ok: 74 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 51 passed. |
| `.venv/bin/python harness/plugins/autosci/bin/autosci_operator_smoke.py skillgen` | ok: 28 routes, 28 bound, 0 failed, 10 gated. |
| `.venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci_feature_parity_wiki_state.json` | ok: 28 routed, 0 missing, 2 full, 16 partial, 10 gated. |
| `env PYTHONPATH=harness .venv/bin/python harness/evaluators/scientific/autosci_feature_parity_gate.py /tmp/autosci_feature_parity_wiki_state.json` | ok: passed with non-full route warning. |
| `env PYTHONPATH=harness .venv/bin/python harness/evaluators/scientific/autosci_operator_smoke_gate.py harness/artifacts/autosci/operator-smoke/skillgen/autosci_operator_smoke.json` | ok: passed with approval-gated warning. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_idea_gate.py -q` | ok: 7 passed after wiki-state gate hardening. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 52 passed after wiki-state gate hardening. |

### Remaining Wiki/State Blocks

| Block | Status | Required follow-up |
|---|---|---|
| Mutation layer | pending | Real set-meta/add-edge/log/rebuild operations still only exist in bounded novelty writeback paths; generic wiki mutation remains proposal/approval gated. |
| Strict lifecycle state machine | pending | Resolver reads state, but `$research` still does not orchestrate native state transitions across discovery, ideation, novelty/review, experiment, report, and publication. |
| Rich YAML parsing | warn | Resolver intentionally supports scalar and simple list frontmatter only; complex YAML/nested metadata needs a structured parser or schema-backed wiki writer. |
| Quality gates | pending | Resolver improves state truthfulness but does not replace idea quality, novelty, review, experiment validity, or publication compile gates. |

## Phase 19 Poster Approved Executor Follow-up

Logged: 2026-06-24 EDT

| Item | Status | Evidence |
|---|---|---|
| Poster executor | ok | `$poster --execute-approved` can now run an allowlisted poster renderer only after approval ref, allowlist evidence, and before artifact preflight are present. |
| Renderer command contract | ok | Allowlist evidence can provide `poster_render_command` with `{html}`, `{png}`, and `{validation}` placeholders, or `poster_renderer` as an executable receiving those three paths. |
| Runtime ABI output | ok | The poster executor writes `autosci_runtime_evidence.v1`, stdout/stderr sidecars, PNG artifact, and executor validation JSON. |
| Semantic verification loop | ok | Executor output is fed back through the approval contract and existing poster semantic verifier for browser render, overflow probe, and PNG export checks. |
| Default safety | ok | `$poster` default behavior is unchanged; no renderer command runs unless `--execute-approved` is supplied and preflight passes. |
| Truthfulness guard | ok | Without source report/evidence payload, poster evidence remains `inconclusive` even when render/export runtime is verified. |

### Poster Approved Executor Verification Commands

| Command | Result |
|---|---|
| `harness/bin/python3 -m py_compile harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_executes_approved_poster_executor harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_records_approval_runtime_contract_for_gated_actions harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_runs_survey_rebuttal_and_poster_native_sidecars -q` | ok: 3 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/plugins/autosci/tests -q` | ok: 72 passed. |
| `env PYTHONPATH=harness harness/bin/python3 -m pytest harness/tests/evaluators/scientific -q` | ok: 51 passed. |
| `env PYTHONPATH=harness HARNESS_DIR=/tmp/autosci-operator-smoke harness/bin/python3 harness/plugins/autosci/bin/autosci_operator_smoke.py skillgen --out /tmp/autosci-operator-smoke/operator_smoke_poster_executor.json` | ok: 28 routes, 28 bound, 0 failed, 10 gated. |
| `git diff --check -- docs/integrations/autosci/phase19-progress-log.md harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |

### Remaining Executor Blocks After Poster

| Block | Status | Required follow-up |
|---|---|---|
| Source fetch/email executors | pending | Daily arXiv/source initialization can verify supplied runtime evidence, but network fetch and email send executors are not implemented. |
| Pilot executor | pending | Pilot runtime verification exists, but local/remote process execution and result collection executor are not implemented. |
| Destructive/control executors | pending | Setup/reset/refine/research lifecycle mutation executors remain proposal-only and approval-gated. |
| Full lifecycle orchestration | pending | `$research` still needs orchestration across discovery, ideation, novelty/review, experiment, report, and publication stages. |

## Phase 19 Parity Log Coverage Audit

Logged: 2026-06-25 EDT

This audit cross-checked the current AutoSci/Solar parity-related dirty paths against the Phase 19 log. The goal was not to add new behavior, but to confirm that prior parity work is recorded in the log with its verification evidence and remaining limitations.

| Change group | Status | Log coverage |
|---|---|---|
| Codex entry, model, and worktree default behavior | ok | Covered by Dollar Skill Compatibility, Solar Skill Projection, Lab Worktree Skill Discovery, Codex Pane Worktree Default, and Worktree Sync/Cleanup follow-ups. These sections record direct AutoSci `$...` intake routing, 28 projected skills, main-checkout pane defaults, worktree cleanup, and model config guard checks including `gpt-5.5`. |
| Native command protocol and fixture boundary | ok | Covered by Native Command Contract and Smoke Boundary. The log records native flags such as `--env`, `--collect`, `--title`, `--checklist`, `--max-ideas`, `--skip-validation`, `--skip-pilot`, approval/runtime flags, and the explicit-smoke rule for fixture fallback. |
| Source preparation and discovery | ok | Covered by PDF/arXiv Source Preparation and Discover Command Compatibility. The log records PDF/local/remote source preparation, raw archive evidence, wiki discovery mode, citation expansion limitations, and literature discovery gate coverage. |
| Ideate, novelty, review, and Review LLM paths | ok | Covered by Real Ideate Sourcing, Local Novelty/Review Signal, Novelty Writeback, Standalone Review, Review LLM Evidence State, External Novelty Evidence, Novelty Write Trust, Online Novelty Fetch, External Novelty Provenance, Review-Coupled Novelty Write, Provider-Specific Novelty Provenance, Provider Payload Digest/Archive, Novelty Payload Artifact Visibility, and Review LLM Command Bridge follow-ups. |
| Wiki resolver, mutation, retrieval, and graph gates | ok | Covered by Wiki State Resolver Fallback, Wiki Mutation Layer, Wiki Retrieval And Graph Gate, and Wiki State Resolver follow-ups. The log records no-default `idea-001`/`exp-001` fallback, read-only resolver sidecars, graph edge parsing, wiki writeback boundaries, and remaining mutation/state-machine gaps. |
| Experiment lifecycle and runtime approval | ok | Covered by Experiment Lifecycle Collect, Approval Runtime Contract, Semantic Runtime Verification, Runtime Schema And Compile Executor, and Poster Approved Executor follow-ups. The log records collect diagnostics, approval contracts, semantic runtime verification, formal runtime evidence ABI/gate, approved compile executor, and approved poster executor. |
| Paper/report/publication pipeline | ok | Covered by Paper Compile Checklist, Publication And Report Native Sidecar, Runtime Schema And Compile Executor, and Poster Approved Executor follow-ups. The log records checklist diagnostics, report plan/markdown/evidence-index sidecars, publication bundle truthfulness, latexmk gating, and no-PDF/no-submission limitations when runtime evidence is absent. |
| Route truthfulness and backend mapping | ok | Covered by Route Truthfulness and Remaining Backend Action Mapping. The log records coverage-status downgrades, full-route guardrails, all configured `solar_backend_action` handlers, and remaining non-full parity blocks. |
| Evidence schemas, gates, adapters, fixtures, and tests | ok | Covered throughout each follow-up's implementation and verification command tables. The changed schema/gate/adapter/test groups are recorded by file or by functional group, including `autosci_skill_run`, `artifact_review`, `experiment_status`, `graph_update`, `literature_discovery`, `publication_bundle`, `workflow_evolution`, `autosci_runtime_evidence`, and the AutoSci bridge/shim tests. |

### Coverage Audit Commands

| Command | Result |
|---|---|
| `bash harness/solar-harness.sh context inject --query "AutoSci parity progress log completeness audit changed files phase19 log coverage" --format markdown` | ok: Solar unified context loaded; source degraded to local Mirage/QMD/DB context. |
| `git status --short -- docs/integrations/autosci/phase19-progress-log.md harness/plugins/autosci harness/evaluators/scientific harness/schemas/evidence harness/tests/evaluators/scientific` | ok: enumerated current AutoSci parity-related tracked and untracked dirty paths for coverage checking. |
| `rg -n "^## Phase 19|^### Remaining|autosci_runtime_evidence|autosci_skill_shim|autosci_bridge|idea_gate|test_idea_gate|test_autosci_skill_shim|autosci_to_idea_candidate|autosci_to_experiment_plan|Wiki State Resolver|Runtime Schema|Poster Approved|Compile Executor|approval|semantic|novelty|review|collect|paper compile|checklist|route truthfulness|model|gpt-5.5|worktree" docs/integrations/autosci/phase19-progress-log.md` | ok: found matching log coverage across all parity workstreams. |
| `git diff --name-only -- docs/integrations/autosci/phase19-progress-log.md harness/plugins/autosci harness/evaluators/scientific harness/schemas/evidence harness/tests/evaluators/scientific` | ok: tracked AutoSci parity diffs are covered by existing Phase 19 sections or by this audit section. |

### Coverage Audit Exclusions

| Path group | Status | Reason |
|---|---|---|
| `.DS_Store`, watchdog pid/session files, pane logs, generated run artifacts | excluded | Local/runtime noise, not parity implementation. |
| AI Influence, Tech Hotspot Radar, report validation, PM dispatch, and unrelated selector/report files outside the AutoSci parity path | excluded | Present in the dirty worktree but not part of the AutoSci parity workstream being audited here. |
| Untracked generated `harness/artifacts/autosci/` run outputs | excluded | Execution artifacts used for verification; not implementation changes. |

### Coverage Audit Result

| Finding | Status | Notes |
|---|---|---|
| Unlogged AutoSci parity implementation group | ok | No unlogged AutoSci parity implementation group was found in the audited path set. |
| Remaining parity gaps | ok | Remaining gaps are already logged as pending/warn blocks: full lifecycle orchestration, real source/email/pilot/control executors, generic wiki mutation, richer YAML/wiki schemas, Review LLM stress coverage, and completed ask/check intelligence outputs. |
| Commit readiness | warn | The repository still contains many unrelated dirty/untracked files; do not treat this audit as a safe commit boundary without a separate staging review. |

## Phase 19 Audit-Adjusted Parity Completion

Logged: 2026-06-25 EDT

This update incorporates the migrated runtime audit at
`docs/integrations/autosci/audit/migrated-autosci-parity-audit-2026-06-25.md`
and the current route/operator smoke inventory. The audit shows that the
migrated AutoSci runtime is not full parity yet, so route completion is now
reported as bound-but-partial/gated rather than completed.

| Completion measure | Status | Current value | Evidence |
|---|---|---:|---|
| Native skills/routes bound | ok | 28 / 28 | Current parity inventory and operator smoke both bind all native AutoSci skills to Solar routes. |
| Missing routes | ok | 0 | No native skill is missing from `feature_parity_routes.v1.json`. |
| Full route coverage | warn | 0 | The audit invalidated `full` claims for migrated runtime parity because source-grounded end-to-end runs still fail or remain fixture/schema-only. |
| Partial route coverage | warn | 18 | Non-gated routes are now classified as partial until source evidence, wiki state, review, experiment, and publication blocks run natively. |
| Approval-gated routes | pending | 10 | Side-effecting routes remain gated until approved runtime executors are supplied and verified. |
| Native full runtime stages | error | 0 / 23 | Audit YAML summary reports no fully native completed runtime stage. |
| Runtime final verdict | error | failed | End-to-end `$research` did not complete; SkillGen ingest, experiment deploy, paper compile, and resume/status behavior failed or were incomplete. |

### Audit-Driven Route Truthfulness Changes

| Route | Status | Change |
|---|---|---|
| `/discover` | warn | Downgraded from `full` to `partial` because the audit observed `/discover --from-wiki --limit 10` as schema-only/inconclusive rather than live/wiki-grounded shortlist evidence. |
| `/ingest` | warn | Downgraded from `full` to `partial` because SkillGen PDF semantic ingestion failed and fixture abstract leakage was observed. |
| `/exp-design`, `/exp-status`, `/ideate`, `/paper-plan`, `/paper-draft` | warn | Remain partial in the current route config; they are useful bridge paths but not full native AutoSci parity. |
| `/review` | warn | Bound to the artifact review operator/schema, but still partial until independent Review LLM evidence is present. |

### Audit-Adjusted Remaining Blocks

| Block | Status | Required follow-up |
|---|---|---|
| Native CLI protocol | error | Finish native command options for original AutoSci syntax, including resume/status and route-specific flags. |
| Source-grounded ingest/discovery | error | Replace fixture/schema-only success with verified PDF/arXiv/wiki evidence propagation. |
| Ideate and novelty gates | warn | Keep improving real ideation, novelty provenance, and Review LLM coupling until quality gates prove research value, not just schema shape. |
| Experiment lifecycle | error | Implement deploy/monitor/collect lifecycle without fixture result artifacts for non-smoke runs. |
| Publication compile | error | Produce and verify LaTeX/PDF/checklist artifacts through approved executors. |
| Web UI and visualization | error | Restore native visualization/web surfaces and validate route flags against real runtime behavior. |

### Audit-Adjusted Verification Commands

| Command | Result |
|---|---|
| `.venv/bin/python -m json.tool harness/plugins/autosci/config/feature_parity_routes.v1.json /tmp/feature_parity_routes_after_audit_update.json` | ok |
| `.venv/bin/python -m json.tool harness/plugins/autosci/config/feature_operator_bindings.v1.json /tmp/feature_operator_bindings_after_audit_update.json` | ok |
| `.venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci_feature_parity_after_audit_update_20260625.json` | ok: `full_count=0`, `partial_count=18`, `gated_count=10`, `missing_route_count=0`. |
| `env PYTHONPATH=harness .venv/bin/python harness/evaluators/scientific/autosci_feature_parity_gate.py /tmp/autosci_feature_parity_after_audit_update_20260625.json` | ok: gate passed with non-full route warning. |
| `.venv/bin/python harness/plugins/autosci/bin/autosci_operator_smoke.py skillgen --out /tmp/autosci_operator_smoke_after_audit_update_20260625.json` | ok: `bound_count=28`, `completed_count=0`, `partial_count=18`, `gated_count=10`, `failed_count=0`. |
| `env PYTHONPATH=harness .venv/bin/python harness/evaluators/scientific/autosci_operator_smoke_gate.py /tmp/autosci_operator_smoke_after_audit_update_20260625.json` | ok: gate passed with approval-gated runtime warning. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 52 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests -q` | ok: 74 passed. |

## Phase 19 P0 SkillGen PDF Ingest Repair

Logged: 2026-06-25 EDT

This follow-up addresses the rerun audit blocker `F-001 PDF ingestion`. The
failure mode was environment-sensitive: the project `.venv` had PyMuPDF, but
the strict audit's system `python3` had `pypdf` and no `fitz`, so SkillGen PDF
ingest returned failed parse evidence. Full parity is still not claimed here;
this repair only removes the PDF extraction/semantic-fidelity blocker.

| Item | Status | Evidence |
|---|---|---|
| System Python PDF fallback | ok | `paper_prepare.py` now falls back from PyMuPDF to `pypdf` or `PyPDF2` before declaring PDF decode failure. |
| Wrapped title recovery | ok | PDF title lines such as `SKILLGEN: Verified Inference-Time Agent Skill` + `Synthesis` are combined into the full title. |
| Semantic evidence retention | ok | Parsed LaTeX/recovered-text sections now retain enough source text for appendix facts such as seed, temperature, model, split, and refinement rounds. |
| Fixture leakage guard | ok | Failed paper parses use explicit parse-failure sections; they do not synthesize `Fixture abstract` or `sample_paper.md#abstract`. |
| Workspace isolation | ok | Default raw paper preparation paths resolve under the active `HARNESS_DIR`, not the main repository artifact directory. |

### SkillGen PDF Ingest Verification Commands

| Command | Result |
|---|---|
| `python3 - <<'PY' ... import fitz/pypdf/PyPDF2/pdfplumber ... PY` | ok: system `python3` has `pypdf` and no `fitz`; this reproduces the audit environment. |
| `env HARNESS_DIR=/tmp/autosci-system-pypdf-ingest2 AUTOSCI_DISABLE_NETWORK_FETCH=1 python3 harness/plugins/autosci/bin/autosci_skill_shim.py text '$ingest /Users/jamesyuan/Downloads/SkillGen(1).pdf --run-id system-pypdf-ingest2'` | ok: `action_count=2`, `failed_count=0`, `execution_status=partial`. |
| Semantic oracle over `/tmp/autosci-system-pypdf-ingest2/.../research_paper.json` | ok: title, three stages, analysis object, skill tuple, repairs/regressions/net gain, Best-of-K/verification gate, +3.27/+10.08 pp, seed 42, temperature 0, GPT-5.4-Mini, 70/30 split, and eight rounds are present in evidence. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_paper_prepare.py -q` | ok: 4 passed. |
| `.venv/bin/python -m py_compile harness/plugins/autosci/backends/paper_prepare.py` | ok |

### Remaining After PDF Repair

| Block | Status | Notes |
|---|---|---|
| Full native ingest parity | pending | Source extraction is fixed, but full parity still requires original AutoSci-equivalent wiki mutation, graph rebuild, source citation expansion, and downstream ask/research lifecycle verification. |
| Review LLM gate | error | Independent Review LLM evidence is still required before novelty/review stages can be considered full parity. |
| Experiment and paper lifecycle | error | Real approved runtime execution, collect/eval mutation, LaTeX draft, and PDF compile remain mandatory blockers. |

## Phase 19 CLI No-op And Research Pipeline Artifact Repair

Logged: 2026-06-25 EDT

This follow-up addresses audit blockers `F-005 CLI parity` and part of
`F-006 Integrated pipeline`. It does not claim full parity. The goal is to stop
native AutoSci commands from being accepted as route-only no-ops, while keeping
unexecuted lifecycle work explicitly gated/inconclusive.

| Item | Status | Evidence |
|---|---|---|
| Native CLI flag parsing | ok | The shim accepts original-style flags including `--format`, `--pipeline`, `--start-from`, `--skip-paper`, `--collect-ready`, `--discover`, and `--visualize` with `allow_abbrev=False`. |
| Positional ingest source | ok | `$ingest <path>` now maps the positional source to `paper_path`; it no longer requires a separate `--paper` to avoid route-only evidence. |
| Compile/survey/status no-op repair | ok | `$paper-compile ... --fix`, `$survey ... --format latex`, and `$exp-status --pipeline ...` each run a bounded bridge action and preserve native options in evidence. |
| Non-smoke experiment truthfulness | ok | Non-smoke `$exp-run --env/--review` uses approval-gated native semantics and no longer emits fixture result support when approval evidence is absent. |
| Research lifecycle artifacts | ok | `$research --start-from ...` now writes `wiki/outputs/pipeline-progress.md`, `wiki/outputs/PIPELINE_REPORT.md`, and `wiki/outputs/pipeline-state.json`. |
| Research lifecycle status | warn | Lifecycle evidence is intentionally `inconclusive`/`schema_only`; no online discovery, experiment deployment, collection, Review LLM, or PDF compile stage was executed. |

### Research Pipeline Artifact Details

| Artifact | Status | Path |
|---|---|---|
| Pipeline progress | ok | `artifacts/autosci/workspace/wiki/outputs/pipeline-progress.md` |
| Pipeline report | ok | `artifacts/autosci/workspace/wiki/outputs/PIPELINE_REPORT.md` |
| Pipeline state | ok | `artifacts/autosci/workspace/wiki/outputs/pipeline-state.json` |
| Workflow evidence | warn | `workflow_evolution.v1` records `current_stage`, `resume_from`, `pipeline`, and `stage_plan`, but remains `inconclusive`. |

### CLI And Pipeline Verification Commands

| Command | Result |
|---|---|
| `env HARNESS_DIR=/tmp/autosci-paper-compile-fix-current python3 harness/plugins/autosci/bin/autosci_skill_shim.py text '$paper-compile paper/ --fix --run-id paper-compile-fix-current'` | ok: `action_count=1`, `schema_only_count=1`, `execution_status=gated`. |
| `env HARNESS_DIR=/tmp/autosci-survey-format-fixed python3 harness/plugins/autosci/bin/autosci_skill_shim.py text '$survey topic:skillgen --format latex --run-id survey-format-fixed'` | ok: `action_count=1`, `schema_only_count=1`, `execution_status=partial`. |
| `env HARNESS_DIR=/tmp/autosci-exp-status-pipeline-fixed python3 harness/plugins/autosci/bin/autosci_skill_shim.py text '$exp-status --pipeline skillgen-main --run-id exp-status-pipeline-fixed'` | ok: `action_count=1`, `schema_only_count=1`, `execution_status=partial`. |
| `env HARNESS_DIR=/tmp/autosci-research-start-from-current python3 harness/plugins/autosci/bin/autosci_skill_shim.py text '$research skillgen-main --venue ICLR --start-from stage3-collect --skip-paper --run-id research-start-from-current'` | ok: `action_count=1`, `schema_only_count=1`, `execution_status=gated`, `workspace_updated_count=6`. |
| `env HARNESS_DIR=/private/tmp/autosci-research-start-from-current PYTHONPATH=harness .venv/bin/python harness/evaluators/scientific/workflow_evolution_gate.py /private/tmp/autosci-research-start-from-current/artifacts/autosci/runs/research-start-from-current/workflow_evolution.research.json` | ok: gate returned `inconclusive` with no structural reasons, matching the non-executed lifecycle state. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_research_start_from_writes_pipeline_artifacts -q` | ok: 1 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_runs_remaining_gated_backend_actions harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_research_start_from_writes_pipeline_artifacts -q` | ok: 2 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_paper_prepare.py harness/plugins/autosci/tests/test_autosci_skill_shim.py harness/plugins/autosci/tests/test_conversion_to_solar_evidence.py -q` | ok: 55 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests -q` | ok: 84 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 52 passed. |
| `.venv/bin/python harness/plugins/autosci/bin/autosci_operator_smoke.py skillgen --out /tmp/autosci_operator_smoke_after_cli_pipeline_repair_20260625.json` | ok: `bound_count=28`, `completed_count=0`, `partial_count=18`, `gated_count=10`, `failed_count=0`. |
| `.venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci_feature_parity_after_cli_pipeline_repair_20260625.json` | ok: `full_count=0`, `partial_count=18`, `gated_count=10`, `missing_route_count=0`. |
| `env PYTHONPATH=harness .venv/bin/python harness/evaluators/scientific/autosci_operator_smoke_gate.py /tmp/autosci_operator_smoke_after_cli_pipeline_repair_20260625.json` | ok: gate passed with approval-gated warning. |
| `env PYTHONPATH=harness .venv/bin/python harness/evaluators/scientific/autosci_feature_parity_gate.py /tmp/autosci_feature_parity_after_cli_pipeline_repair_20260625.json` | ok: gate passed with non-full route warning. |
| `git diff --check -- harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/adapters/autosci_to_workflow_evolution.py harness/plugins/autosci/tests/test_autosci_skill_shim.py harness/plugins/autosci/backends/paper_prepare.py harness/plugins/autosci/adapters/autosci_to_research_paper.py harness/plugins/autosci/tests/test_paper_prepare.py harness/plugins/autosci/tests/test_conversion_to_solar_evidence.py docs/integrations/autosci/phase19-progress-log.md` | ok |

### Remaining After CLI/Pipeline Repair

| Block | Status | Notes |
|---|---|---|
| Full integrated research pipeline | error | The lifecycle now has resume/report artifacts, but still lacks real stage execution and cross-stage native AutoSci artifacts. |
| Review LLM gate | error | Novelty/review/paper-plan still require independent Review LLM evidence before full parity can be claimed. |
| Experiment deploy/monitor/collect | error | Approval-gated diagnostics exist, but deploy/session/status mutation/result collection are not native full parity. |
| Publication compile | error | Compile diagnostics exist, but verified LaTeX/PDF/checklist output through approved executors remains incomplete. |
| Web UI and visualization | error | Native AutoSci visualization/web UI parity remains pending. |

## Phase 19 Runtime, Review, Draft, And Ask Parity Repair

Logged: 2026-06-25 EDT

This follow-up addresses additional parts of `F-002 Review gate`,
`F-003 Experiment lifecycle`, `F-004 Paper pipeline`, and `F-008 Ask/wiki QA`.
It still does not claim full parity. The main change is that approved runtime
evidence and source-grounded wiki evidence now produce concrete state/artifacts
instead of fixture fallback, stale repository fallback, or route-only output.

| Item | Status | Evidence |
|---|---|---|
| Review resolver isolation | ok | `$review <slug>` no longer falls back from an isolated `HARNESS_DIR` to stale repo-level `harness/artifacts/autosci/workspace/wiki` pages. Missing targets remain `inconclusive/schema_only`. |
| Review LLM evidence path | warn | Supplied `artifact_review.v1` evidence and command bridge still work; absent Review LLM evidence remains disclosed as unavailable and not promotion-grade. |
| Approved experiment run | ok | `run_experiment` no longer returns fixture results after approval. It requires approval contract + runtime evidence + semantic verification before producing completed `experiment_result.v1`. |
| Experiment state mutation | ok | Verified runtime evidence writes `wiki/experiments/<experiment>.md`, appends `wiki/log.md`, and adds `produced_result` graph edges. |
| Experiment collect/status | ok | `$exp-run <slug> --collect` can now derive completed `experiment_status.v1` from verified approved runtime evidence and update wiki state. |
| Paper draft | ok | `$paper-draft ...` now runs `write_report` and writes `paper/main.tex` plus `paper/sections/*.tex`; it no longer returns action_count=0. |
| Ask/wiki QA | ok | `$ask` now returns a source-grounded extractive answer when wiki retrieval hits exist, with answer markdown, retrieval JSON, source paths, and passed memory-update gate. |

### Runtime/Draft/Ask Verification Commands

| Command | Result |
|---|---|
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_review_missing_slug_does_not_use_repo_workspace_fallback harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_runs_review_as_artifact_review harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_review_uses_supplied_review_llm_evidence -q` | ok: 3 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_exp_run_uses_verified_runtime_evidence_and_mutates_wiki harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_exp_collect_uses_verified_runtime_evidence harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_blocks_unapproved_exp_run_deploy_without_fixture_support harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_accepts_exp_run_native_options_without_fixture_fallback -q` | ok: 4 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_paper_draft_writes_latex_source harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_runs_paper_compile_fix_diagnostics harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_accepts_paper_plan_title_without_topic_fallback -q` | ok: 3 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_runs_ask_check_and_init_diagnostics harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_ask_and_check_read_workspace_wiki -q` | ok: 2 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests -q` | ok: 88 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 52 passed. |
| `.venv/bin/python harness/plugins/autosci/bin/autosci_operator_smoke.py skillgen --out /tmp/autosci_operator_smoke_after_runtime_draft_ask_repair_20260625.json` | ok: `bound_count=28`, `completed_count=0`, `partial_count=18`, `gated_count=10`, `failed_count=0`. |
| `.venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci_feature_parity_after_runtime_draft_ask_repair_20260625.json` | ok: `full_count=0`, `partial_count=18`, `gated_count=10`, `missing_route_count=0`. |
| `env PYTHONPATH=harness .venv/bin/python harness/evaluators/scientific/autosci_operator_smoke_gate.py /tmp/autosci_operator_smoke_after_runtime_draft_ask_repair_20260625.json` | ok: gate passed with approval-gated warning. |
| `env PYTHONPATH=harness .venv/bin/python harness/evaluators/scientific/autosci_feature_parity_gate.py /tmp/autosci_feature_parity_after_runtime_draft_ask_repair_20260625.json` | ok: gate passed with non-full route warning. |
| `git diff --check -- harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/bin/autosci_workspace_projector.py harness/plugins/autosci/backends/artifact_review.py harness/plugins/autosci/tests/test_autosci_skill_shim.py docs/integrations/autosci/phase19-progress-log.md` | ok |

### Remaining After Runtime/Draft/Ask Repair

| Block | Status | Notes |
|---|---|---|
| Full Review LLM parity | error | The bridge can consume Review LLM evidence/commands, but there is still no built-in native Review LLM provider execution proven in strict audit. |
| End-to-end research completion | error | Individual approved runtime and draft/ask paths work, but `$research` still does not execute every native stage to completion automatically. |
| Paper compile full parity | warn | Draft LaTeX and approved compile executor paths exist, but strict full parity still requires verified `paper/main.pdf` in the integrated pipeline. |
| Web UI and visualization | error | Native AutoSci web/graph UI parity remains pending. |

## Phase 19 Web UI Compatibility Repair

Logged: 2026-06-25 EDT

This follow-up addresses `F-007 Web UI`. The strict audit found that the
original AutoSci-compatible `tools/serve.py`, `tools/visualize.py`,
`app/index.html`, and `app/modules/graph.js` paths were missing. These paths
now exist as Solar AutoSci compatibility entrypoints over the local
`wiki/graph/edges.jsonl` and Markdown wiki workspace.

| Item | Status | Evidence |
|---|---|---|
| `tools/visualize.py` | ok | Provides `generate-obsidian-config`, `generate-canvas`, and `graph-data` commands over a supplied `--wiki-root`. |
| `tools/serve.py` | ok | Provides `--health-check` plus a local static server that generates `app/data/graph.json` from the active wiki before serving. |
| `app/index.html` | ok | Static graph reader shell exists and loads `app/modules/graph.js`. |
| `app/modules/graph.js` | ok | Renders local graph JSON with search and selection details. |
| Runtime data handling | ok | `app/data/graph.json` is generated at serve/health-check time and is not treated as a source file. |

### Web UI Verification Commands

| Command | Result |
|---|---|
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_web_visualization_compatibility_tools_generate_graph_artifacts harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_runs_remaining_gated_backend_actions -q` | ok: 2 passed. |
| `.venv/bin/python -m py_compile tools/visualize.py tools/serve.py harness/plugins/autosci/bin/autosci_bridge.py` | ok |
| `.venv/bin/python tools/visualize.py generate-obsidian-config --wiki-root /tmp/autosci-web-current/wiki` | ok: generated `.obsidian/graph.json`. |
| `.venv/bin/python tools/visualize.py generate-canvas --wiki-root /tmp/autosci-web-current/wiki --graph-out /tmp/autosci-web-current/graph.json` | ok: generated Canvas and graph JSON with 2 nodes / 1 edge in the smoke wiki. |
| `.venv/bin/python tools/serve.py --wiki-root /tmp/autosci-web-current/wiki --health-check` | ok: `node_count=2`, `edge_count=1`, app files present. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests -q` | ok: 89 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 52 passed. |
| `.venv/bin/python harness/plugins/autosci/bin/autosci_operator_smoke.py skillgen --out /tmp/autosci_operator_smoke_after_web_repair_20260625.json` | ok: `bound_count=28`, `completed_count=0`, `partial_count=18`, `gated_count=10`, `failed_count=0`. |
| `.venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci_feature_parity_after_web_repair_20260625.json` | ok: `full_count=0`, `partial_count=18`, `gated_count=10`, `missing_route_count=0`. |
| `env PYTHONPATH=harness .venv/bin/python harness/evaluators/scientific/autosci_operator_smoke_gate.py /tmp/autosci_operator_smoke_after_web_repair_20260625.json` | ok: gate passed with approval-gated warning. |
| `env PYTHONPATH=harness .venv/bin/python harness/evaluators/scientific/autosci_feature_parity_gate.py /tmp/autosci_feature_parity_after_web_repair_20260625.json` | ok: gate passed with non-full route warning. |

### Remaining After Web UI Repair

| Block | Status | Notes |
|---|---|---|
| Full end-to-end `$research` parity | error | Compatibility pieces exist, but the integrated research command still needs to orchestrate all repaired stages into one completed pipeline. |
| Built-in Review LLM provider | error | Evidence/command bridge exists; automatic Codex/Review LLM execution has not been proven by strict audit. |
| Integrated paper PDF | warn | Draft/compile pieces exist; the integrated research run still must produce verified `paper/main.pdf`. |

## Phase 19 Review LLM Provider Repair

Logged: 2026-06-25 EDT

This follow-up addresses the remaining built-in Review LLM provider blocker
from the Web UI repair section. It does not claim full parity because the
integrated `$research` lifecycle and integrated paper PDF proof remain open.

| Item | Status | Evidence |
|---|---|---|
| OpenAI-compatible provider path | ok | `artifact_review.py` now invokes a configured Review LLM provider when Review LLM is explicitly requested or provider env/config is present. |
| Default model | ok | Provider mode defaults to `gpt-5.5`; shim also exposes `--review-llm-model` for explicit auditability. |
| Provider controls | ok | Shim exposes `--review-llm-provider`, `--review-llm-model`, and `--review-llm-endpoint`; env fallbacks are `AUTOSCI_REVIEW_LLM_PROVIDER`, `AUTOSCI_REVIEW_LLM_MODEL`, and `AUTOSCI_REVIEW_LLM_ENDPOINT`. |
| Provenance | ok | Provider responses are normalized into `artifact_review.v1`, archived under `artifacts/autosci/review-llm`, and include invocation mode, provider, model, endpoint, request hash, response hash, usage, and Review LLM evidence ids. |
| Failure truthfulness | ok | Missing key, transport failure, invalid transport JSON, or invalid model JSON stay unavailable/failed/invalid; the bridge does not convert failed provider calls into passed surrogate review. |
| Novelty coupling | ok | Novelty/review output now distinguishes provider-produced, command-bridge, and externally supplied Review LLM evidence instead of always saying the bridge did not invoke a reviewer. |

### Review LLM Provider Verification Commands

| Command | Result |
|---|---|
| `.venv/bin/python -m py_compile harness/plugins/autosci/backends/artifact_review.py harness/plugins/autosci/backends/novelty_review.py harness/plugins/autosci/bin/autosci_skill_shim.py` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_runs_review_as_artifact_review harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_review_uses_review_llm_command_bridge harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_review_invokes_openai_compatible_provider harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_novelty_write_uses_review_llm_command_bridge -q` | ok: 4 passed. |

### Remaining After Review LLM Provider Repair

| Block | Status | Notes |
|---|---|---|
| Full end-to-end `$research` parity | error | Compatibility pieces and individual repaired routes exist, but `$research` still must orchestrate all repaired stages into one completed lifecycle. |
| Integrated paper PDF | warn | Draft/compile pieces exist; the integrated research run still must produce verified `paper/main.pdf`. |

## Phase 19 Research Lifecycle And Integrated PDF Repair

Logged: 2026-06-25 EDT

This follow-up addresses the `$research` integration blocker and the integrated
PDF proof blocker. It still does not claim full parity because real long-running
stage runners, network fetches, and human gates remain approval/evidence driven.
The fix prevents `$research` from being only a blocked route plan when strict
stage evidence is available.

| Item | Status | Evidence |
|---|---|---|
| Evidence-aware `$research` lifecycle | ok | `run_research_lifecycle` now reads active wiki state plus discovery, novelty, Review LLM, experiment runtime, collection, and compile evidence to mark each native lifecycle stage `completed` or `pending_evidence`. |
| Verified completed pipeline state | ok | When every required stage has evidence, `$research` emits completed `workflow_evolution.v1`, writes `pipeline-state.json`, and records `pipeline.status=completed` instead of a blocked plan. |
| Missing-evidence truthfulness | ok | If any required stage evidence is missing or invalid, the lifecycle remains `inconclusive` and names the pending stage rather than synthesizing success. |
| Integrated PDF materialization | ok | With verified approval contract plus compile runtime/PDF evidence, `$research` materializes the verified PDF to `artifacts/autosci/workspace/paper/main.pdf` and records an `integrated_paper_pdf` artifact. |
| Config truthfulness | ok | Route/operator configs now describe `$research` as external-evidence-orchestrated partial coverage and `/review` as supporting configured Review LLM provider/command/supplied evidence. Coverage status remains non-full and uses existing parity schema enums. |

### Research Lifecycle Verification Commands

| Command | Result |
|---|---|
| `.venv/bin/python -m py_compile harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/adapters/autosci_to_workflow_evolution.py` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_research_start_from_writes_pipeline_artifacts harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_research_lifecycle_completes_from_verified_stage_evidence harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_runs_research_pipeline -q` | ok: 3 passed. |
| `python3 -m json.tool harness/plugins/autosci/config/feature_parity_routes.v1.json >/dev/null && python3 -m json.tool harness/plugins/autosci/config/feature_operator_bindings.v1.json >/dev/null` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests -q` | ok: 91 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 52 passed. |
| `.venv/bin/python harness/plugins/autosci/bin/autosci_operator_smoke.py skillgen --out /tmp/autosci_operator_smoke_after_research_lifecycle_repair_20260625.json` | ok: `bound_count=28`, `completed_count=0`, `partial_count=18`, `gated_count=10`, `failed_count=0`. |
| `.venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci_feature_parity_after_research_lifecycle_repair_20260625.json` | ok: `full_count=0`, `partial_count=18`, `gated_count=10`, `missing_route_count=0`. |
| `env PYTHONPATH=harness .venv/bin/python harness/evaluators/scientific/autosci_operator_smoke_gate.py /tmp/autosci_operator_smoke_after_research_lifecycle_repair_20260625.json` | ok: gate passed with approval-gated warning. |
| `env PYTHONPATH=harness .venv/bin/python harness/evaluators/scientific/autosci_feature_parity_gate.py /tmp/autosci_feature_parity_after_research_lifecycle_repair_20260625.json` | ok: gate passed with non-full route warning. |
| `git diff --check -- harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/adapters/autosci_to_workflow_evolution.py harness/plugins/autosci/backends/artifact_review.py harness/plugins/autosci/backends/novelty_review.py harness/plugins/autosci/config/feature_parity_routes.v1.json harness/plugins/autosci/config/feature_operator_bindings.v1.json harness/plugins/autosci/tests/test_autosci_skill_shim.py docs/integrations/autosci/phase19-progress-log.md tools/visualize.py tools/serve.py app/index.html app/styles.css app/modules/graph.js` | ok |

### Remaining After Research Lifecycle Repair

| Block | Status | Notes |
|---|---|---|
| Real stage runner full parity | error | The integrated lifecycle can verify completed stage evidence, but it still does not launch every native long-running runner by itself without approval/runtime evidence. |
| Live external source full parity | warn | Online discovery/novelty fetch paths exist, but full parity still needs repeated live source audits under real provider conditions. |

## Phase 19 PDF Ingest Gate Hardening Follow-up

Logged: 2026-06-25 EDT

This follow-up tightens the already repaired PDF ingest path so the strict
audit cannot pass a completed PDF ingest that lacks extracted text evidence.
It also removes stale route text that still described the old SkillGen PDF
semantic failure as current behavior.

| Item | Status | Evidence |
|---|---|---|
| PDF ingest gate | ok | `paper_gate.py` now requires completed PDF-prepared evidence to carry `preparation.extracted_text_path`, an `extracted_pdf_text` artifact, and a parsed/partial parse status. |
| `$ingest <pdf>` regression | ok | Shim test now generates a real PDF, runs non-smoke `$ingest <pdf>` with network disabled, and verifies `original_format=pdf`, `extracted_pdf_text`, `synthetic_latex`, parsed title text, and no fixture abstract leakage. |
| Config truthfulness | ok | Ingest route/operator limitations now say PDF extraction and fixture-leakage guards are covered; the route remains partial only for approved wiki mutation, graph rebuild, citation expansion, and downstream lifecycle audits. |

### PDF Ingest Gate Verification Commands

| Command | Result |
|---|---|
| `.venv/bin/python -m py_compile harness/evaluators/scientific/paper_gate.py harness/plugins/autosci/tests/test_autosci_skill_shim.py harness/tests/evaluators/scientific/test_paper_gate.py` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_ingests_pdf_with_extracted_text_and_no_fixture_leakage harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_maps_positional_ingest_source harness/tests/evaluators/scientific/test_paper_gate.py -q` | ok: 4 passed. |

### Remaining After PDF Gate Hardening

| Block | Status | Notes |
|---|---|---|
| Approved wiki mutation and graph rebuild | warn | Ingest can parse and prepare sources, but original-style approved wiki mutation/rebuild still needs explicit mutation evidence. |
| Live external source full parity | warn | Discovery and novelty online paths still need live provider audit evidence. |

## Phase 19 Research Wiki Tool ABI Repair

Logged: 2026-06-25 EDT

This follow-up closes the generic `tools/research_wiki.py` command-layer gap
referenced by the migrated AutoSci routes. It does not mark full parity by
itself because citation expansion and downstream lifecycle audits still need
completed evidence, but the missing wiki mutation/retrieval ABI is now present
as a local, bounded, auditable tool.

| Item | Status | Evidence |
|---|---|---|
| Wiki retrieval ABI | ok | Added `tools/research_wiki.py query`, `neighbors`, and `stats` with JSON evidence output over the local Markdown wiki and `wiki/graph/edges.jsonl`. |
| Wiki mutation ABI | ok | Added `set-meta`, `add-edge`, `log`, and `rebuild` commands with wiki-root containment checks, before/after hashes, edge evidence ids, and rebuilt `index.md` / `graph/context_brief.md`. |
| Route truthfulness | ok | Ingest route/operator limitations now state that generic local wiki mutation/rebuild tooling is covered; the route remains partial for citation expansion and downstream lifecycle audits. |

### Research Wiki Tool Verification Commands

| Command | Result |
|---|---|
| `python3 -m py_compile tools/research_wiki.py harness/plugins/autosci/tests/test_research_wiki_tool.py` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_research_wiki_tool.py -q` | ok: 1 passed. |
| `python3 tools/research_wiki.py set-meta ideas/skillgen.md status=reviewed --wiki-root <tmp>/wiki --json && python3 tools/research_wiki.py query SkillGen --wiki-root <tmp>/wiki --json` | ok: CLI smoke emitted consumable JSON. |

### Remaining After Research Wiki Tool ABI Repair

| Block | Status | Notes |
|---|---|---|
| Citation expansion | warn | Source preparation and wiki mutation are covered, but survey/paper planning still needs stronger citation expansion evidence before full parity. |
| Live external source full parity | warn | Discovery and novelty online paths still need live provider audit evidence under real source conditions. |
| Real stage runner full parity | error | Long-running experiment/deploy/collect stages still require approved runtime evidence and cannot be truthfully collapsed into deterministic smoke output. |

## Phase 19 Source Discovery CLI ABI Repair

Logged: 2026-06-25 EDT

This follow-up closes the root `tools/` command ABI gap for source preparation,
literature discovery, and novelty source helpers. The commands reuse existing
Solar AutoSci backends where available and report unavailable providers as
`inconclusive` evidence instead of synthetic candidates.

| Item | Status | Evidence |
|---|---|---|
| Paper source CLI | ok | Added `tools/prepare_paper_source.py` as a root wrapper over the source preparation backend for local/PDF/arXiv source normalization. |
| Discover CLI | ok | Added `tools/discover.py from-topic/from-anchors/from-wiki/from-venue` over the literature discovery backend, preserving no-network inconclusive behavior. |
| Novelty source CLIs | ok | Added `tools/fetch_s2.py search/references/citations` and `tools/fetch_deepxiv.py search`; unavailable providers return explicit inconclusive evidence. |
| Route truthfulness | ok | Discover and novelty route/operator limitations now state that source CLIs exist while provider-backed completion still requires real source evidence. |

### Source Discovery CLI Verification Commands

| Command | Result |
|---|---|
| `python3 -m py_compile tools/prepare_paper_source.py tools/discover.py tools/fetch_s2.py tools/fetch_deepxiv.py harness/plugins/autosci/tests/test_source_cli_tools.py` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_source_cli_tools.py -q` | ok: 3 passed. |

### Remaining After Source Discovery CLI ABI Repair

| Block | Status | Notes |
|---|---|---|
| Root side-effect/toolchain CLIs | warn | `tools/lint.py`, `daily_arxiv.py`, `send_email.py`, `remote.py`, `init_discovery.py`, `rasterize_latex.py`, `poster.py`, `wiki2dag.py`, and `reset_wiki.py` are still missing root ABI coverage. |
| Live provider completion | warn | Discovery/novelty commands are truthful, but full parity still needs live provider success evidence rather than only disabled/unavailable evidence. |

## Phase 19 Root Tool ABI Completion Repair

Logged: 2026-06-25 EDT

This follow-up closes the remaining root `tools/*.py` existence gap in the
feature parity route config. Side-effectful commands remain approval-gated and
truthful: launch, email send, reset, and browser/PNG render paths report
`approval_required` or `inconclusive` unless real runtime evidence is supplied.

| Item | Status | Evidence |
|---|---|---|
| Wiki/check tool ABI | ok | Added `tools/lint.py` and covered route config references to `tools/research_wiki.py stats/query/neighbors`. |
| Init/source tool ABI | ok | Added `tools/init_discovery.py prepare/plan/fetch` and verified all source/discovery route tool paths now exist. |
| Side-effect tool ABI | ok | Added `tools/daily_arxiv.py`, `tools/send_email.py`, `tools/remote.py`, and `tools/reset_wiki.py` with approval-required evidence for external/destructive effects. |
| Publication/visual tool ABI | ok | Added `tools/rasterize_latex.py`, `tools/wiki2dag.py`, and `tools/poster.py` for diagnostics/build/validate paths without claiming unavailable rendering success. |
| Route tool inventory | ok | Route config root tool reference audit now returns `{}` for missing `tools/*.py` paths. |

### Root Tool ABI Verification Commands

| Command | Result |
|---|---|
| `python3 -m py_compile tools/lint.py tools/init_discovery.py tools/remote.py tools/daily_arxiv.py tools/send_email.py tools/rasterize_latex.py tools/wiki2dag.py tools/poster.py tools/reset_wiki.py` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_root_tool_abi.py harness/plugins/autosci/tests/test_source_cli_tools.py harness/plugins/autosci/tests/test_research_wiki_tool.py -q` | ok: 6 passed. |
| `python3 -m json.tool harness/plugins/autosci/config/feature_parity_routes.v1.json >/dev/null && python3 -m json.tool harness/plugins/autosci/config/feature_operator_bindings.v1.json >/dev/null` | ok |
| Root `tools/*.py` route inventory script | ok: `{}` missing root tools. |

### Remaining After Root Tool ABI Completion Repair

| Block | Status | Notes |
|---|---|---|
| Full route completion evidence | error | `full_count` remains zero until route statuses are backed by live/provider/runtime evidence and not merely by ABI coverage. |
| Live provider completion | warn | Discovery/novelty paths now have CLIs, but still need real provider success evidence for completed source-backed routes. |
| Long-running execution parity | error | Remote/local experiment launch, collect, reset, email, and render side effects still require approved runtime implementations and evidence. |

## Phase 19 Primary Tool ABI Gate Repair

Logged: 2026-06-25 EDT

This follow-up makes the parity inventory gate enforce local primary tool and
config-file existence. It also adds the missing setup documentation artifacts
referenced by the setup route.

| Item | Status | Evidence |
|---|---|---|
| Setup config ABI | ok | Added `harness/plugins/autosci/config/setup-guide.md` and `harness/plugins/autosci/config/.env.example` without writing secrets. |
| Inventory tool ABI sidecar | ok | `autosci_parity_bridge.py` now records `tool_abi_status`, `primary_tool_statuses`, and `missing_primary_tools` for each route. |
| Gate enforcement | ok | `autosci_feature_parity_gate.py` now fails if any local primary tool/config reference is missing. External executables/providers remain explicit external requirements. |

### Primary Tool ABI Gate Verification Commands

| Command | Result |
|---|---|
| `python3 -m py_compile harness/plugins/autosci/bin/autosci_parity_bridge.py harness/evaluators/scientific/autosci_feature_parity_gate.py` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_phase19_parity_bridge.py harness/plugins/autosci/tests/test_root_tool_abi.py -q` | ok: 6 passed. |
| `.venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci_feature_parity_after_tool_abi_gate_20260625.json` | ok: `full_count=0`, `partial_count=18`, `gated_count=10`, `missing_route_count=0`. |
| `env PYTHONPATH=harness .venv/bin/python harness/evaluators/scientific/autosci_feature_parity_gate.py /tmp/autosci_feature_parity_after_tool_abi_gate_20260625.json` | ok: gate passed with non-full warning. |

### Remaining After Primary Tool ABI Gate Repair

| Block | Status | Notes |
|---|---|---|
| Route completion | error | ABI completeness is enforced, but routes remain non-full until each route has source/model/runtime evidence matching native behavior. |
| External executable/provider proof | warn | `latexmk`, Review LLM MCP/provider, live S2/DeepXiv, SMTP, browser rendering, and remote execution remain external evidence requirements. |

## Phase 19 Publication Citation Map Repair

Logged: 2026-06-25 EDT

This follow-up fixes the paper-plan/survey citation expansion blocker for
supplied source evidence. The routes no longer only emit placeholder citation
language: they build an explicit `autosci_publication_citation_map.v1` sidecar
from discovery, paper, and wiki paper evidence.

| Item | Status | Evidence |
|---|---|---|
| Citation map sidecar | ok | `plan_report` and `write_survey` now write `*_citation_map.json` artifacts with source-backed citation ids, titles, source refs, source channels, and evidence ids. |
| Survey completion gate | ok | `$survey` remains inconclusive without source citations, but becomes completed when supplied discovery/paper/wiki evidence yields citation entries. |
| Paper-plan review gate | ok | `$paper-plan` now requires both citation-map entries and completed Review LLM evidence before returning completed status. |
| Config truthfulness | ok | Ingest, paper-plan, paper-draft, and survey route/operator limitations now describe citation-map handoff as covered while preserving remaining live/provider/compile audit blockers. |

### Publication Citation Map Verification Commands

| Command | Result |
|---|---|
| `python3 -m py_compile harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_accepts_paper_plan_title_without_topic_fallback harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_paper_plan_completes_with_citations_and_review_llm harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_runs_survey_rebuttal_and_poster_native_sidecars harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_survey_completes_with_citation_evidence harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_accepts_survey_format_latex -q` | ok: 5 passed. |

### Remaining After Publication Citation Map Repair

| Block | Status | Notes |
|---|---|---|
| Live/exhaustive literature audit | warn | Citation-map generation works for supplied evidence, but live provider coverage still needs real S2/DeepXiv/Paper Copilot success evidence. |
| End-to-end publication compile audit | warn | Planning/survey citation evidence is fixed; compile/PDF/toolchain evidence still gates full publication parity. |

## Phase 19 Pilot Evaluation Runtime Evidence Repair

Logged: 2026-06-25 EDT

This follow-up replaces the fixed inconclusive `$exp-pilot-eval` behavior with
evidence-driven pilot verdict generation. Missing evidence still remains
inconclusive; supplied runtime or `experiment_result.v1` evidence can now
produce completed `claim_verdict.v1` evidence.

| Item | Status | Evidence |
|---|---|---|
| Runtime-backed pilot verdict | ok | `evaluate_pilot_result` now reads supplied runtime evidence, maps outcome/exit code to a lenient pilot verdict, and attaches `pilot_runtime_evidence_json` artifacts. |
| Missing-evidence truthfulness | ok | Existing no-evidence `$exp-pilot-eval` path remains inconclusive; no default support verdict is synthesized. |
| Config truthfulness | ok | `exp-pilot-eval` and `exp-status` route/operator limitations now reflect runtime/wiki evidence support while preserving approved wiki-write/remote-provider blockers. |

### Pilot Evaluation Verification Commands

| Command | Result |
|---|---|
| `python3 -m py_compile harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_runs_remaining_gated_backend_actions harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_pilot_eval_uses_runtime_evidence -q` | ok: 2 passed. |

### Remaining After Pilot Evaluation Runtime Evidence Repair

| Block | Status | Notes |
|---|---|---|
| Approved pilot wiki writeback | warn | Completed pilot verdicts do not mutate wiki status unless an explicit approved write path is implemented/audited. |
| Remote provider audit | warn | Runtime evidence can be consumed, but real remote launch/check/pull-results provider evidence remains approval-gated. |

## Phase 19 Rebuttal Review Mapping Repair

Logged: 2026-06-25 EDT

This follow-up replaces fixed empty rebuttal maps with evidence-backed response
plans when supplied Review LLM / `artifact_review.v1` findings are available.

| Item | Status | Evidence |
|---|---|---|
| Review finding extraction | ok | `draft_rebuttal` now reads supplied `artifact_review.v1` findings and atomizes them into mapped concerns. |
| Response map completion | ok | Rebuttal bundle status becomes completed only when source review evidence yields mapped concerns; no-evidence runs remain inconclusive. |
| Config truthfulness | ok | Rebuttal route/operator limitations now describe completed mapped response plans from supplied Review LLM evidence while preserving reviewer-thread/submission audit blockers. |

### Rebuttal Mapping Verification Commands

| Command | Result |
|---|---|
| `python3 -m py_compile harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_runs_survey_rebuttal_and_poster_native_sidecars harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_rebuttal_maps_review_llm_findings -q` | ok: 2 passed. |

### Remaining After Rebuttal Mapping Repair

| Block | Status | Notes |
|---|---|---|
| Reviewer-thread ingestion | warn | Mapped responses work for supplied Review LLM findings, but full native reviewer-thread ingestion/submission workflow is still not audited. |

## Phase 19 Init Runtime Source Manifest Coverage

Logged: 2026-06-25 EDT

This follow-up verifies the completed `$init` path for approved runtime source
manifests. The bridge still does not execute network fetch or fan-in ingest by
itself, but it can consume approved source-manifest runtime evidence and emit
completed `literature_discovery.v1` evidence.

| Item | Status | Evidence |
|---|---|---|
| Init runtime manifest path | ok | Added regression coverage for `$init` with approval, allowlist, before/after artifacts, and runtime candidates. |
| Semantic verification | ok | `init_sources` returns `mode=init_runtime_verified` only when the approval contract and runtime candidate evidence pass semantic verification. |
| Config truthfulness | ok | Init route/operator limitations now distinguish completed approved runtime source manifests from still-gated native network fetch/bulk ingest/wiki fan-in execution. |

### Init Runtime Verification Commands

| Command | Result |
|---|---|
| `python3 -m py_compile harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_runs_ask_check_and_init_diagnostics harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_init_uses_verified_runtime_source_manifest -q` | ok: 2 passed. |

### Remaining After Init Runtime Source Manifest Coverage

| Block | Status | Notes |
|---|---|---|
| Native network/fan-in executor | warn | `$init` can consume verified runtime evidence, but direct feed/source fetching and wiki fan-in remain approval/provider-gated. |

## Phase 19 Daily arXiv Runtime Digest Coverage

Logged: 2026-06-25 EDT

This follow-up verifies the completed `$daily-arxiv` path for approved runtime
digest/feed evidence. The route remains gated for direct network fetch, email,
scheduling, and auto-ingest side effects.

| Item | Status | Evidence |
|---|---|---|
| Daily runtime digest path | ok | Added regression coverage for `$daily-arxiv` with approval, allowlist, before/after artifacts, and runtime candidates. |
| Semantic verification | ok | `daily_arxiv_prepare_finalize` returns `mode=daily_arxiv_runtime_verified` only when the approval contract and runtime candidate evidence pass semantic verification. |
| Config truthfulness | ok | Daily arXiv route/operator limitations now distinguish completed approved runtime digest evidence from still-gated fetch/email/scheduling/auto-ingest execution. |

### Daily arXiv Runtime Verification Commands

| Command | Result |
|---|---|
| `python3 -m py_compile harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_runs_remaining_gated_backend_actions harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_daily_arxiv_uses_verified_runtime_digest -q` | ok: 2 passed. |

### Remaining After Daily arXiv Runtime Digest Coverage

| Block | Status | Notes |
|---|---|---|
| Direct daily executor | warn | The route can consume verified runtime evidence, but feed fetch/email/scheduling/auto-ingest execution remains approval/provider-gated. |

## Phase 19 ABI Publication Runtime Verification Rollup

Logged: 2026-06-25 EDT

This rollup records the verification pass after the research wiki tool ABI,
source/discovery CLI ABI, root tool ABI, primary-tool gate, publication
citation map, pilot runtime evaluation, rebuttal mapping, init runtime manifest,
and daily runtime digest repairs.

| Item | Status | Evidence |
|---|---|---|
| AutoSci plugin tests | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests -q` passed: 104 tests. |
| Scientific evaluator tests | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` passed: 54 tests. |
| Operator smoke gate | ok | `bound_count=28`, `completed_count=0`, `partial_count=18`, `gated_count=10`, `failed_count=0`; gate passed with approval-gated warning. |
| Feature parity gate | warn | `full_count=0`, `partial_count=18`, `gated_count=10`, `missing_route_count=0`; gate passed with non-full warning. |
| Config and whitespace checks | ok | Route/operator JSON validation passed; `git diff --check` passed over changed AutoSci/code/log files. |
| Generated artifact cleanup | ok | Removed generated `app/data/graph.json` after visualization tests. |

### Current Full Parity Status

| Area | Status | Notes |
|---|---|---|
| Route coverage | ok | All 28 native skills have Solar routes and local primary tool/config ABI references resolve. |
| Functional parity | partial | Many routes now have completed paths when supplied source/model/runtime evidence exists, but static inventory remains non-full. |
| External/provider parity | blocked | Full parity still needs real provider/executor evidence for live S2/DeepXiv/Paper Copilot, Review LLM, latexmk/PDF compile, SMTP/email, browser render, and remote launch/check/pull-results. |

## Phase 19 Approved Wiki Mutation and Status Sync Repair

Logged: 2026-06-25 EDT

This follow-up closes the local wiki mutation gap for approved `/prefill` and
`/edit` executions, while preserving no-approval proposal behavior.

| Item | Status | Evidence |
|---|---|---|
| Approved prefill mutation | ok | `$prefill foundation:... --approval-ref ... --execute-approved` now writes a foundation page under the configured wiki root, appends `wiki/log.md`, and rebuilds `wiki/index.md` plus `wiki/graph/context_brief.md`. |
| Approved edit mutation | ok | `$edit wiki/... --approval-ref ... --after-artifact ... --execute-approved` now applies the approved after-artifact to the target wiki page with before/after hashes and rebuild evidence. |
| No-approval safety | ok | Existing `/prefill` and `/edit` runs without explicit approval still emit proposed `research_memory_update.v1` evidence and do not mutate wiki files. |
| Route/operator truthfulness | ok | `/prefill` is synchronized as approval-gated for approved wiki mutation; `/exp-design` and `/exp-pilot-eval` remain synchronized as partial evidence/evaluation routes rather than side-effect executors. |
| Drift guard | ok | Added a route-vs-operator status consistency regression so future parity reports cannot silently disagree with operator smoke status. |

### Approved Wiki Mutation Verification Commands

| Command | Result |
|---|---|
| `python3 -m py_compile harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `python3 -m json.tool harness/plugins/autosci/config/feature_parity_routes.v1.json` | ok |
| `python3 -m json.tool harness/plugins/autosci/config/feature_operator_bindings.v1.json` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_runs_wiki_and_control_proposal_actions harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_prefill_applies_approved_wiki_mutation harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_edit_applies_approved_after_artifact -q` | ok: 3 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_phase19_operator_smoke.py -q` | ok: 3 passed. |
| `.venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci_feature_parity_after_executor_repairs_20260625.json` | ok: `full_count=0`, `partial_count=17`, `gated_count=11`, `missing_route_count=0`. |
| `.venv/bin/python harness/plugins/autosci/bin/autosci_operator_smoke.py skillgen --out /tmp/autosci_operator_smoke_after_executor_repairs_20260625.json` | ok: `bound_count=28`, `completed_count=0`, `partial_count=17`, `gated_count=11`, `failed_count=0`. |

### Remaining After Approved Wiki Mutation Repair

| Block | Status | Notes |
|---|---|---|
| Full parity | blocked | Inventory remains non-full because live provider/executor evidence is still required for S2/DeepXiv/Paper Copilot, Review LLM, latexmk/PDF compile, SMTP/email, browser render, and remote launch/check/pull-results. |

## Phase 19 TeX Executor Fallback Repair

Logged: 2026-06-25 EDT

This follow-up improves the approved paper compile executor so a machine without
`latexmk` can still produce verified PDF evidence through an explicitly
allowlisted TeX engine.

| Item | Status | Evidence |
|---|---|---|
| TeX executor selection | ok | `$paper-compile --execute-approved` now chooses the first installed and allowlisted executor from `latexmk`, `pdflatex`, `xelatex`, and `lualatex`. |
| Approval boundary | ok | The executor still requires `approval_ref`, allowlist evidence, before-artifact evidence, and `--execute-approved`; no-approval runs remain diagnostics-only. |
| Runtime provenance | ok | `autosci_runtime_evidence.v1` now records `tex_executor`, available TeX executors, command, stdout/stderr sidecars, PDF path, and executor-specific evidence ids such as `paper-compile-runtime:pdflatex`. |
| Checklist truthfulness | ok | `paper_compile_checklist.v1` preserves `latexmk_available` while adding `tex_executors` and `selected_executor`, so missing latexmk no longer hides usable approved engines. |
| Route truthfulness | ok | `/paper-compile` route text now describes approval-gated TeX executor behavior instead of latexmk-only behavior. |

### TeX Executor Fallback Verification Commands

| Command | Result |
|---|---|
| `python3 -m py_compile harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_executes_approved_paper_compile_executor harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_executes_approved_paper_compile_with_pdflatex_fallback harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_uses_semantic_runtime_evidence_for_gated_results harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_accepts_paper_compile_checklist_without_bundle_fallback -q` | ok: 4 passed. |
| `python3 -m json.tool harness/plugins/autosci/config/feature_parity_routes.v1.json` | ok |
| `.venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci_feature_parity_after_executor_repairs_20260625.json` | ok: `full_count=0`, `partial_count=17`, `gated_count=11`, `missing_route_count=0`. |

### Remaining After TeX Executor Fallback Repair

| Block | Status | Notes |
|---|---|---|
| End-to-end publication parity | warn | Approved TeX executor can now produce verified PDF evidence, but final full parity still depends on real paper content, citation/review gates, and environment-specific toolchain smoke. |
| Non-publication executors | blocked | Live S2/DeepXiv/Paper Copilot, SMTP/email, browser render, and remote launch/check/pull-results still need approved runtime smoke evidence. |

## Phase 19 Remote Runtime Executor Repair

Logged: 2026-06-25 EDT

This follow-up adds a real approval-gated launch path to `tools/remote.py` and
fixes the runtime evidence schema/gate mismatch for experiment execution.

| Item | Status | Evidence |
|---|---|---|
| Approved remote/local launch | ok | `tools/remote.py launch --execute-approved` can run an explicit allowlisted command only when `--approval-ref`, `--allowlist-evidence`, `--command`, and a run directory are supplied. |
| Runtime evidence output | ok | The launch path writes `autosci_runtime_evidence.v1` with `action=run_experiment`, command, exit code, result paths, metrics, outcome, stdout/stderr artifacts, and approval ref. |
| Schema/gate consistency | ok | `autosci_runtime_evidence.v1` now permits `run_experiment`, and the runtime gate requires completed experiment evidence to include metrics, outcome, and `result_collected=true`. |
| Bridge consumption | ok | Existing `$exp-run` and collect paths continue to consume verified runtime evidence and mutate wiki experiment state only after semantic verification. |
| Default safety | ok | Without `--execute-approved`, `tools/remote.py launch` remains approval/inconclusive evidence and does not run commands. |

### Remote Runtime Verification Commands

| Command | Result |
|---|---|
| `python3 -m json.tool harness/schemas/evidence/autosci_runtime_evidence.v1.schema.json` | ok |
| `python3 -m py_compile tools/remote.py harness/evaluators/scientific/autosci_runtime_evidence_gate.py harness/tests/evaluators/scientific/test_autosci_runtime_evidence_gate.py harness/plugins/autosci/tests/test_root_tool_abi.py` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_autosci_runtime_evidence_gate.py harness/plugins/autosci/tests/test_root_tool_abi.py -q` | ok: 7 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_blocks_unapproved_exp_run_deploy_without_fixture_support harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_exp_run_uses_verified_runtime_evidence_and_mutates_wiki harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_exp_collect_uses_verified_runtime_evidence -q` | ok: 3 passed. |

### Remaining After Remote Runtime Executor Repair

| Block | Status | Notes |
|---|---|---|
| Provider-specific remote parity | warn | The local approved executor can launch allowlisted commands and produce verifier-ready runtime evidence; SSH/rsync/screen provider profiles and real remote connectivity smoke remain environment-dependent. |
| External source/provider parity | blocked | Live S2/DeepXiv/Paper Copilot, SMTP/email, and browser render/export still need approved runtime smoke evidence. |

## Phase 19 SMTP Email Executor Repair

Logged: 2026-06-25 EDT

This follow-up converts `tools/send_email.py` from an approval-only stub into
an approval-gated SMTP executor with runtime evidence.

| Item | Status | Evidence |
|---|---|---|
| Approved SMTP send | ok | `tools/send_email.py send --execute-approved` sends only when `--approval-ref`, SMTP host/port, sender/recipient, and explicit execution are supplied. |
| Runtime evidence | ok | The send path writes `autosci_runtime_evidence.v1` with `action=send_email`, provider, SMTP endpoint metadata, delivery status, approval ref, and an email delivery receipt sidecar. |
| Gate hardening | ok | Runtime schema/gate now accepts `send_email` and requires completed email runtime evidence to declare `delivered=true` plus a provider. |
| Local smoke | ok | Added a local SMTP server test so delivery is verified without external email services or credentials. |
| Default safety | ok | Without approval or `--execute-approved`, email send remains approval-required/inconclusive and does not contact SMTP endpoints. |

### SMTP Executor Verification Commands

| Command | Result |
|---|---|
| `python3 -m json.tool harness/schemas/evidence/autosci_runtime_evidence.v1.schema.json` | ok |
| `python3 -m py_compile tools/send_email.py harness/evaluators/scientific/autosci_runtime_evidence_gate.py harness/tests/evaluators/scientific/test_autosci_runtime_evidence_gate.py harness/plugins/autosci/tests/test_root_tool_abi.py` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_autosci_runtime_evidence_gate.py harness/plugins/autosci/tests/test_root_tool_abi.py -q` | ok: 8 passed. |

### Remaining After SMTP Executor Repair

| Block | Status | Notes |
|---|---|---|
| Live/provider SMTP | warn | Local SMTP smoke passes; real SMTP/provider credentials and deliverability remain environment-specific and must be approved before use. |
| External source/render parity | blocked | Live S2/DeepXiv/Paper Copilot and browser render/export still need approved runtime smoke evidence. |

## Phase 19 Root Poster Render Executor Repair

Logged: 2026-06-25 EDT

This follow-up closes the root CLI render/export gap for poster/browser parity.
The bridge already had an approved renderer path; `tools/poster.py render` now
has the same approval-gated runtime evidence behavior.

| Item | Status | Evidence |
|---|---|---|
| Approved root render | ok | `tools/poster.py render --execute-approved` runs only with `--approval-ref`, allowlist evidence, and an explicit renderer command or allowlisted renderer config. |
| PNG/export evidence | ok | The root render path writes PNG, renderer validation, stdout/stderr sidecars, and `autosci_runtime_evidence.v1` with `action=build_poster`. |
| Runtime gate | ok | Generated evidence satisfies existing poster checks: `browser_rendered=true`, `png_exported=true`, and passing overflow probe. |
| Config truthfulness | ok | Poster route/operator limitations now state root and bridge render paths are approval-gated and unavailable renderers remain inconclusive. |

### Root Poster Render Verification Commands

| Command | Result |
|---|---|
| `python3 -m py_compile tools/poster.py harness/plugins/autosci/tests/test_root_tool_abi.py` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_root_tool_abi.py harness/tests/evaluators/scientific/test_autosci_runtime_evidence_gate.py -q` | ok: 9 passed. |

### Remaining After Root Poster Render Repair

| Block | Status | Notes |
|---|---|---|
| Browser/provider render smoke | warn | Local approved renderer smoke passes; real browser/Playwright or screenshot providers still require environment-specific approval. |
| External source parity | blocked | Live S2/DeepXiv/Paper Copilot provider smoke remains the main external evidence blocker. |

## Phase 19 Paper Copilot Source CLI Repair

Logged: 2026-06-25 EDT

This follow-up adds an auditable root Paper Copilot provider CLI so venue-based
Paper Copilot source evidence is visible outside the internal discovery backend.

| Item | Status | Evidence |
|---|---|---|
| Root provider CLI | ok | Added `tools/fetch_paper_copilot.py venue <venue> <year>` for Paper Copilot venue lists. |
| Truthful network behavior | ok | With network disabled, the CLI emits inconclusive evidence and no synthesized papers. |
| Local provider smoke | ok | `file://` provider evidence can be read in offline tests, normalized to paper candidates, and marked completed. |
| Route visibility | ok | `/discover` primary tools now include `tools/fetch_paper_copilot.py venue` so provider ABI is covered by parity inventory. |

### Paper Copilot Verification Commands

| Command | Result |
|---|---|
| `python3 -m py_compile tools/fetch_paper_copilot.py harness/plugins/autosci/tests/test_source_cli_tools.py` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_source_cli_tools.py -q` | ok: 4 passed. |
| `python3 -m json.tool harness/plugins/autosci/config/feature_parity_routes.v1.json` | ok |
| `.venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci_feature_parity_after_executor_repairs_20260625.json` | ok: `full_count=0`, `partial_count=17`, `gated_count=11`, `missing_route_count=0`. |

### Remaining After Paper Copilot CLI Repair

| Block | Status | Notes |
|---|---|---|
| Live provider smoke | warn | S2, DeepXiv, and Paper Copilot have auditable provider paths; real internet/API success evidence remains environment/date dependent and must be captured under approved smoke. |
| Static full parity | blocked | Inventory remains non-full because routes still correctly distinguish partial/gated execution from always-on full native parity. |

## Phase 19 Executor And Source Provider Repair Rollup

Logged: 2026-06-25 EDT

This rollup records the verification pass after approved wiki mutation,
approval-gated TeX fallback, remote/local launch runtime evidence, SMTP send,
root poster render/export, Paper Copilot source CLI, and runtime schema/gate
repairs.

| Item | Status | Evidence |
|---|---|---|
| AutoSci plugin tests | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests -q` passed: 112 tests. |
| Scientific evaluator tests | ok | `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` passed: 54 tests. |
| Operator smoke gate | ok | `bound_count=28`, `completed_count=0`, `partial_count=17`, `gated_count=11`, `failed_count=0`; generated evidence passed with approval-gated warning. |
| Feature parity gate | warn | `full_count=0`, `partial_count=17`, `gated_count=11`, `missing_route_count=0`; generated inventory passed with non-full warning. |
| Config/whitespace checks | ok | Route/operator/runtime schema JSON validation passed; `git diff --check` passed for changed AutoSci/tool/log files. |
| Generated artifact cleanup | ok | Removed untracked `app/data/graph.json` generated by visualization tests. |

### Current Full Parity Status After Executor Repairs

| Area | Status | Notes |
|---|---|---|
| Native route coverage | ok | All 28 AutoSci native skills remain routed and bound. |
| Approved side-effect executors | partial | Local approved executors now exist for wiki mutation, TeX/PDF compile fallback, remote/local launch evidence, SMTP send, and poster render/export. |
| Source/provider evidence | partial | S2, DeepXiv, Web, and Paper Copilot have auditable provider paths; live success evidence still depends on network/API availability and approved smoke. |
| Static full parity | blocked | The inventory still has `full_count=0` because routes intentionally remain partial/gated until real provider, model, remote, and publication runs are captured end to end. |

## Phase 19 Ask/Check Model Evidence Repair

Logged: 2026-06-25 EDT

This follow-up closes the immediate ask/check model-evidence gap without
pretending that missing provider output is a completed intelligence result.
Both paths now accept explicit `autosci_model_response.v1` evidence files or a
model command bridge that receives an `autosci_model_request.v1` payload on
stdin and returns normalized model evidence on stdout.

| Item | Status | Evidence |
|---|---|---|
| `$ask` model synthesis | ok | Added `--model-evidence` and `--model-command`; `ask_wiki` archives model stdout/stderr, records `model_output`, writes a `Model Synthesis` section, and carries model evidence ids into `research_memory_update.v1`. |
| `$check` quality review | ok | `check_wiki_health` now archives supplied model/reviewer evidence, includes it in findings/recommended changes, clears the prior “content quality still requires model evidence” runtime error only when model evidence is completed, and keeps missing evidence visible otherwise. |
| Truthfulness guard | ok | No model command/evidence still produces `unavailable` model status and the route remains partial; no deterministic substitute is used for LLM content quality or synthesis. |
| Route/binding docs | ok | Ask/check limitations now state that explicit model evidence/commands are supported while missing evidence remains inconclusive. |

### Ask/Check Model Evidence Verification Commands

| Command | Result |
|---|---|
| `python3 -m py_compile harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_runs_ask_check_and_init_diagnostics harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_ask_and_check_read_workspace_wiki harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_ask_uses_model_command_with_retrieved_sources harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_check_uses_model_command_for_quality_review -q` | ok: 4 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_workflow_evolution_gate.py harness/tests/evaluators/scientific/test_lifecycle_gate.py -q` | ok: 8 passed. |
| `python3 -m json.tool harness/plugins/autosci/config/feature_parity_routes.v1.json` and `feature_operator_bindings.v1.json` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests -q` | ok: 114 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 54 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_autosci_operator_smoke_gate.py harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py -q` | ok: 6 passed. |
| `.venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci_feature_parity_after_ask_check_model_20260625.json` | ok: `full_count=0`, `partial_count=17`, `gated_count=11`, `missing_route_count=0`. |
| `git diff --check -- harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/config/feature_parity_routes.v1.json harness/plugins/autosci/config/feature_operator_bindings.v1.json harness/plugins/autosci/tests/test_autosci_skill_shim.py docs/integrations/autosci/phase19-progress-log.md` | ok |

### Remaining After Ask/Check Model Evidence Repair

| Block | Status | Notes |
|---|---|---|
| Live model provider smoke | warn | Local command-bridge evidence is verified; real provider/API execution still needs approved credentials and runtime smoke evidence. |
| Static full parity | blocked | Ask/check are stronger but still correctly remain partial until a full end-to-end AutoSci run captures real retrieval, model, source, runtime, review, and publication evidence. |

## Phase 19 Exp-Eval Review Evidence Repair

Logged: 2026-06-25 EDT

This follow-up closes the formal `/exp-eval` evidence handoff gap. The shim now
exposes explicit claim, experiment result, code evidence, and Review LLM evidence
inputs for review-backed claim verdicts, and the bridge keeps Review LLM output
as an independent second opinion instead of using it to override experiment
outcomes.

| Item | Status | Evidence |
|---|---|---|
| Native CLI evidence inputs | ok | Added `--experiment-result-evidence`, `--claims-evidence`, and `--code-evidence` to the AutoSci skill shim and native options. |
| Evidence list loading | ok | `experiment_result`, `claims`, and `code_evidence` loaders now accept append/list inputs rather than only scalar paths. |
| Claim id routing | ok | `$exp-eval <claim>` now maps the positional target into `claim_id`, avoiding fallback to `claim-001`. |
| Review LLM binding | ok | `verify_claim` now reads completed `artifact_review.v1` Review LLM evidence, archives it as `claim_review_llm_evidence_json`, appends review evidence ids, and stores a `review_llm` audit block in `claim_verdict.v1`. |
| Approved wiki writeback | ok | `$exp-eval --write --approval-ref ... --wiki-root ...` can update linked wiki idea/experiment frontmatter, append wiki log/graph evidence, and emit `claim_verdict_writeback.v1`; unapproved or incomplete evidence remains inconclusive. |
| Truthfulness guard | ok | Review LLM evidence does not upgrade missing/failed/inconclusive experiment evidence; verdict outcome remains derived from supplied experiment result evidence. |

### Exp-Eval Review Evidence Verification Commands

| Command | Result |
|---|---|
| `python3 -m py_compile harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/adapters/autosci_to_claim_verdict.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_exp_eval_merges_experiment_code_and_review_llm_evidence harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_pilot_eval_uses_runtime_evidence harness/tests/evaluators/scientific/test_claim_verdict_gate.py -q` | ok: 6 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_exp_eval_merges_experiment_code_and_review_llm_evidence harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_exp_eval_write_updates_wiki_with_approval harness/tests/evaluators/scientific/test_claim_verdict_gate.py -q` | ok: 6 passed. |
| `python3 -m json.tool harness/plugins/autosci/config/feature_parity_routes.v1.json` and `feature_operator_bindings.v1.json` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests -q` | ok: 116 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 54 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_autosci_operator_smoke_gate.py harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py -q` | ok: 6 passed. |
| `.venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci_feature_parity_after_exp_eval_20260625.json` | ok: `full_count=0`, `partial_count=17`, `gated_count=11`, `missing_route_count=0`. |
| `git diff --check -- harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/adapters/autosci_to_claim_verdict.py harness/plugins/autosci/config/feature_parity_routes.v1.json harness/plugins/autosci/config/feature_operator_bindings.v1.json harness/plugins/autosci/tests/test_autosci_skill_shim.py docs/integrations/autosci/phase19-progress-log.md` | ok |

### Remaining After Exp-Eval Review Evidence Repair

| Block | Status | Notes |
|---|---|---|
| Idea status mutation | ok | Approved write-back now updates linked wiki idea/experiment pages with verdict frontmatter, log, graph edge, and lightweight wiki rebuild artifacts. |
| Static full parity | blocked | `/exp-eval` is stronger but remains partial until end-to-end provider/runtime/review audits are captured under real project conditions. |

## Phase 19 Exp-Design Review Evidence Repair

Logged: 2026-06-25 EDT

This follow-up closes the `/exp-design` review-backed design validation gap
without executing an experiment or treating missing Review LLM output as a pass.
The design route can now attach completed Review LLM evidence directly to
`experiment_plan.v1`.

| Item | Status | Evidence |
|---|---|---|
| Native route override | ok | Non-smoke `$exp-design <target>` now runs `design_experiment` directly instead of being blocked by source-required fixture dependencies. |
| Review LLM validation | ok | `design_experiment` reads completed `artifact_review.v1` Review LLM evidence, archives it as `experiment_design_review_llm_evidence_json`, and stores `review_llm` plus evidence ids in `experiment_plan.v1`. |
| Plan gate compatibility | ok | Review validation adds a success criterion while preserving required experiment-plan fields, approval semantics, and safe execution modes. |
| Truthfulness guard | ok | Missing or incomplete Review LLM evidence remains a limitation; it does not mark the plan reviewed. |

### Exp-Design Review Evidence Verification Commands

| Command | Result |
|---|---|
| `python3 -m py_compile harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/adapters/autosci_to_experiment_plan.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_exp_design_attaches_review_llm_validation harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_blocks_unapproved_exp_run_deploy_without_fixture_support harness/tests/evaluators/scientific/test_experiment_plan_gate.py -q` | ok: 4 passed. |
| `python3 -m json.tool harness/plugins/autosci/config/feature_parity_routes.v1.json` and `feature_operator_bindings.v1.json` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests -q` | ok: 117 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 54 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_autosci_operator_smoke_gate.py harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py -q` | ok: 6 passed. |
| `.venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci_feature_parity_after_exp_design_20260625.json` | ok: `full_count=0`, `partial_count=17`, `gated_count=11`, `missing_route_count=0`. |
| `git diff --check -- harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/adapters/autosci_to_claim_verdict.py harness/plugins/autosci/adapters/autosci_to_experiment_plan.py harness/plugins/autosci/config/feature_parity_routes.v1.json harness/plugins/autosci/config/feature_operator_bindings.v1.json harness/plugins/autosci/tests/test_autosci_skill_shim.py docs/integrations/autosci/phase19-progress-log.md` | ok |

### Remaining After Exp-Design Review Evidence Repair

| Block | Status | Notes |
|---|---|---|
| Runtime artifact discovery | warn | Design validation is attached, but real execution artifacts still depend on approved runtime/remote paths. |
| Static full parity | blocked | `/exp-design` remains partial until reviewed design, approved execution, collection, and downstream verdict/writeback are audited end to end. |

## Phase 19 Pilot Eval Approved Writeback Repair

Logged: 2026-06-25 EDT

This follow-up closes the `/exp-pilot-eval` wiki mutation gap for lenient pilot
verdicts. The route still requires explicit approval before mutating wiki state.

| Item | Status | Evidence |
|---|---|---|
| Runtime verdict path | ok | Existing pilot runtime evidence continues to produce completed lenient `claim_verdict.v1` when the runtime outcome supports the pilot claim. |
| Approved wiki writeback | ok | `$exp-pilot-eval --write --approval-ref ... --wiki-root ...` now updates linked wiki idea/experiment frontmatter, appends wiki log/graph evidence, and emits a `pilot_verdict_writeback_json` artifact. |
| Approval boundary | ok | Without `--write` and `--approval-ref`, pilot verdicts do not mutate wiki state. |

### Pilot Eval Writeback Verification Commands

| Command | Result |
|---|---|
| `python3 -m py_compile harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_pilot_eval_uses_runtime_evidence harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_pilot_eval_write_updates_wiki_with_approval harness/tests/evaluators/scientific/test_claim_verdict_gate.py -q` | ok: 6 passed. |
| `python3 -m json.tool harness/plugins/autosci/config/feature_parity_routes.v1.json` and `feature_operator_bindings.v1.json` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests -q` | ok: 118 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 54 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_autosci_operator_smoke_gate.py harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py -q` | ok: 6 passed. |
| `.venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci_feature_parity_after_pilot_writeback_20260625.json` | ok: `full_count=0`, `partial_count=17`, `gated_count=11`, `missing_route_count=0`. |
| `git diff --check -- harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/adapters/autosci_to_claim_verdict.py harness/plugins/autosci/adapters/autosci_to_experiment_plan.py harness/plugins/autosci/config/feature_parity_routes.v1.json harness/plugins/autosci/config/feature_operator_bindings.v1.json harness/plugins/autosci/tests/test_autosci_skill_shim.py docs/integrations/autosci/phase19-progress-log.md` | ok |

### Remaining After Pilot Eval Writeback Repair

| Block | Status | Notes |
|---|---|---|
| Remote/runtime provider audit | warn | Pilot verdict and writeback paths are local-evidence verified; real remote runtime evidence still depends on approved execution providers. |
| Static full parity | blocked | `/exp-pilot-eval` remains partial until pilot execution, collection, verdict, and wiki mutation are audited in one approved run. |

## Phase 19 Paper Draft Compile Handoff Repair

Logged: 2026-06-25 EDT

This follow-up closes the immediate `/paper-draft` compile/PDF handoff gap. The
draft route still does not execute TeX itself; it consumes verified
approval-gated compile runtime evidence from the existing paper compile path and
threads the compiled PDF into report and publication-bundle artifacts.

| Item | Status | Evidence |
|---|---|---|
| Compile handoff verifier | ok | `write_report` now builds `paper_draft_compile_handoff.v1` from `compile_paper` approval/runtime/after evidence and only marks it completed when compile semantic runtime verifies the PDF. |
| Scientific report output | ok | `scientific_report.v1` now preserves `compile_handoff`, adds a compiled-paper section when verified, and includes `paper_draft_compile_handoff_json`, runtime evidence, and `compiled_pdf` artifacts. |
| Publication bundle handoff | ok | The publication bundle sidecar now carries verified compile/PDF handoff artifacts instead of only Markdown/LaTeX sidecars. |
| Truthfulness guard | ok | Missing or incomplete approval/runtime/PDF evidence remains an explicit limitation and does not become a compiled publication claim. |

### Paper Draft Compile Handoff Verification Commands

| Command | Result |
|---|---|
| `python3 -m py_compile harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/adapters/autosci_to_scientific_report.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_paper_draft_writes_latex_source harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_paper_draft_includes_verified_compile_pdf_handoff harness/tests/evaluators/scientific/test_report_gate.py harness/tests/evaluators/scientific/test_paper_gate.py -q` | ok: 8 passed. |
| `python3 -m json.tool harness/plugins/autosci/config/feature_parity_routes.v1.json` and `feature_operator_bindings.v1.json` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests -q` | ok: 119 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 54 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_autosci_operator_smoke_gate.py harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py -q` | ok: 6 passed. |
| `.venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci_feature_parity_after_paper_draft_compile_handoff_20260625.json` | ok: `full_count=0`, `partial_count=17`, `gated_count=11`, `missing_route_count=0`. |
| `git diff --check -- harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/adapters/autosci_to_claim_verdict.py harness/plugins/autosci/adapters/autosci_to_experiment_plan.py harness/plugins/autosci/adapters/autosci_to_scientific_report.py harness/plugins/autosci/config/feature_parity_routes.v1.json harness/plugins/autosci/config/feature_operator_bindings.v1.json harness/plugins/autosci/tests/test_autosci_skill_shim.py docs/integrations/autosci/phase19-progress-log.md` | ok |

### Remaining After Paper Draft Compile Handoff Repair

| Block | Status | Notes |
|---|---|---|
| Real manuscript synthesis | warn | Draft and compile handoff are evidence-linked; full route parity still needs a real wiki-output manuscript synthesis audit under project evidence. |
| Static full parity | blocked | `/paper-draft` remains partial until live/source/review/compile evidence is captured in an end-to-end publication run. |

## Phase 19 Paper Plan Compile Audit Repair

Logged: 2026-06-25 EDT

This follow-up wires the same verified compile/PDF handoff into `/paper-plan`.
The plan route remains a planning artifact, but it can now carry downstream
compile audit evidence when that evidence has already been produced and
approved.

| Item | Status | Evidence |
|---|---|---|
| Compile audit section | ok | `plan_report` now adds a compile-audit section and `compile_handoff` output when approved compile runtime/PDF evidence is supplied. |
| Artifact propagation | ok | `paper_plan_json`, `scientific_report.v1`, and report artifacts now include the verified compile handoff JSON, runtime evidence, and compiled PDF. |
| Compatibility | ok | Existing citation-map + Review LLM completion behavior remains unchanged when compile evidence is not supplied. |
| Truthfulness guard | ok | Missing/incomplete compile evidence remains `not_requested` or `inconclusive`; the paper plan is not treated as a compiled publication. |

### Paper Plan Compile Audit Verification Commands

| Command | Result |
|---|---|
| `python3 -m py_compile harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_paper_plan_completes_with_citations_and_review_llm harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_paper_plan_attaches_verified_compile_handoff harness/tests/evaluators/scientific/test_report_gate.py -q` | ok: 6 passed. |
| `python3 -m json.tool harness/plugins/autosci/config/feature_parity_routes.v1.json` and `feature_operator_bindings.v1.json` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests -q` | ok: 120 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 54 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_autosci_operator_smoke_gate.py harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py -q` | ok: 6 passed. |
| `.venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci_feature_parity_after_paper_plan_compile_audit_20260625.json` | ok: `full_count=0`, `partial_count=17`, `gated_count=11`, `missing_route_count=0`. |
| `git diff --check -- harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/adapters/autosci_to_claim_verdict.py harness/plugins/autosci/adapters/autosci_to_experiment_plan.py harness/plugins/autosci/adapters/autosci_to_scientific_report.py harness/plugins/autosci/config/feature_parity_routes.v1.json harness/plugins/autosci/config/feature_operator_bindings.v1.json harness/plugins/autosci/tests/test_autosci_skill_shim.py docs/integrations/autosci/phase19-progress-log.md` | ok |

### Remaining After Paper Plan Compile Audit Repair

| Block | Status | Notes |
|---|---|---|
| Live idea-graph/figure/table plan | warn | Citation/review/compile audit evidence can be attached, but full parity still needs real idea-graph-derived figure/table planning under project evidence. |
| Static full parity | blocked | `/paper-plan` remains partial until the full publication lifecycle is captured with real source, review, compile, and submission evidence. |

## Phase 19 Source Fan-In Writeback Repair

Logged: 2026-06-25 EDT

This follow-up closes the approved wiki fan-in gap for `/init` and
`/daily-arxiv`. The bridge still does not execute live network fetches, feed
scheduling, or SMTP delivery itself; it now consumes verified runtime source
candidate manifests and, when `--write` is explicit, writes those approved
candidates into the Solar AutoSci wiki state layer.

| Item | Status | Evidence |
|---|---|---|
| Runtime candidate fan-in | ok | `init_sources` and `daily_arxiv_prepare_finalize` now emit `source_fan_in_writeback.v1` when `--write` is requested with a verified approval/runtime contract. |
| Wiki mutation layer | ok | Approved candidates are written to `wiki/papers/*.md`, `wiki/log.md`, `wiki/graph/edges.jsonl`, `wiki/index.md`, and `wiki/graph/context_brief.md`. |
| Evidence propagation | ok | `literature_discovery.v1` now preserves `outputs.source_fan_in` and carries a `source_fan_in_writeback_json` artifact. |
| Truthfulness guard | ok | Without `--write`, verified candidates remain output-only; without a complete approval/runtime contract, fan-in side effects stay inconclusive. |

### Source Fan-In Verification Commands

| Command | Result |
|---|---|
| `python3 -m py_compile harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/adapters/autosci_to_literature_discovery.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_init_write_fans_runtime_sources_into_wiki harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_daily_arxiv_write_auto_ingests_runtime_digest -q` | ok: 2 passed. |
| `python3 -m json.tool harness/plugins/autosci/config/feature_parity_routes.v1.json` and `feature_operator_bindings.v1.json` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_init_uses_verified_runtime_source_manifest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_daily_arxiv_uses_verified_runtime_digest -q` | ok: 2 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py -q` | ok: 4 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests -q` | ok: 122 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 54 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_autosci_operator_smoke_gate.py harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py -q` | ok: 6 passed. |
| `.venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci_feature_parity_after_source_fan_in_20260625.json` | ok: `full_count=0`, `partial_count=17`, `gated_count=11`, `missing_route_count=0`. |
| `git diff --check -- harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/adapters/autosci_to_literature_discovery.py harness/plugins/autosci/config/feature_parity_routes.v1.json harness/plugins/autosci/config/feature_operator_bindings.v1.json harness/plugins/autosci/tests/test_autosci_skill_shim.py docs/integrations/autosci/phase19-progress-log.md` | ok |

### Remaining After Source Fan-In Writeback Repair

| Block | Status | Notes |
|---|---|---|
| Live source providers | warn | Approved manifests can now fan into wiki state, but real arXiv/S2 fetch execution, scheduling, and SMTP delivery remain provider/approval-gated. |
| Static full parity | blocked | `/init` and `/daily-arxiv` remain partial/gated until live source provider runs are captured and audited end to end. |

## Phase 19 Refine Approved Apply Repair

Logged: 2026-06-25 EDT

This follow-up closes the immediate `/refine` proposal-only gap for approved
artifact replacement. The route still does not rerun downstream quality gates by
itself; it now supports a narrowly scoped, auditable apply path when the user
supplies a verified approval contract plus an approved `after_artifact`.

| Item | Status | Evidence |
|---|---|---|
| Approved refine apply | ok | `refine_artifact` can now replace an existing target artifact from `after_artifact` only when `--execute-approved`, `--approval-ref`, allowlist, runtime, before, and after artifacts are present. |
| Writeback evidence | ok | Applied refine runs emit `refine_apply_writeback.v1`, `refine_apply_writeback_json`, `refined_artifact`, and optional wiki log/rebuild artifacts. |
| Workflow ABI gate | ok | `workflow_evolution.v1` schema/gate now permits `application_state=applied` only for verified refine apply evidence with an approval contract and writeback artifact; general workflow evolution remains proposal-only. |
| Truthfulness guard | ok | Unapproved refine, setup, reset, and lifecycle control routes still emit proposed-only evidence and keep protected edits blocked. |

### Refine Apply Verification Commands

| Command | Result |
|---|---|
| `python3 -m py_compile harness/evaluators/scientific/workflow_evolution_gate.py harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `python3 -m json.tool harness/schemas/evidence/workflow_evolution.v1.schema.json` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_workflow_evolution_gate.py harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_refine_applies_approved_after_artifact harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_runs_remaining_gated_backend_actions -q` | ok: 4 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests -q` | ok: 123 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 54 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_autosci_operator_smoke_gate.py harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py -q` | ok: 6 passed. |
| `.venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci_feature_parity_after_refine_apply_20260625.json` | ok: `full_count=0`, `partial_count=17`, `gated_count=11`, `missing_route_count=0`. |
| `git diff --check -- harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/adapters/autosci_to_literature_discovery.py harness/plugins/autosci/config/feature_parity_routes.v1.json harness/plugins/autosci/config/feature_operator_bindings.v1.json harness/plugins/autosci/tests/test_autosci_skill_shim.py harness/evaluators/scientific/workflow_evolution_gate.py harness/schemas/evidence/workflow_evolution.v1.schema.json docs/integrations/autosci/phase19-progress-log.md` | ok |

### Remaining After Refine Apply Repair

| Block | Status | Notes |
|---|---|---|
| Quality gate rerun | warn | Approved artifact replacement is covered, but automated post-refine lint/review/test reruns still depend on approved runtime evidence. |
| Static full parity | blocked | `/refine` remains gated until apply + post-refine quality gates are audited in one approved run. |

## Phase 19 Paper Compile Fix Writeback Repair

Logged: 2026-06-25 EDT

This follow-up closes the immediate `/paper-compile --fix` proposal-only gap.
The compile route still does not claim publication success without a compiled
PDF or verified compile runtime evidence; it can now apply an approved fixed TeX
source before diagnostics or approved TeX executor execution.

| Item | Status | Evidence |
|---|---|---|
| Approved TeX source fix | ok | `compile_paper` now replaces the target `.tex` source from `after_artifact` only when `--fix`, `--execute-approved`, approval, allowlist, and before evidence are supplied. |
| Fix writeback evidence | ok | Applied fixes emit `paper_compile_fix_writeback.v1`, `paper_compile_fix_writeback_json`, source hashes, and the updated `latex_source` artifact. |
| Compile status guard | ok | A fixed source alone does not mark publication complete; completion still requires a discovered PDF or verified compile runtime evidence. |
| Diagnostics integration | ok | The compile checklist records `fix_writeback` and marks auto-fix checks `ok` only when the approved writeback applies. |

### Paper Compile Fix Verification Commands

| Command | Result |
|---|---|
| `python3 -m py_compile harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_runs_paper_compile_fix_diagnostics harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_paper_compile_fix_applies_approved_after_artifact harness/tests/evaluators/scientific/test_paper_gate.py -q` | ok: 4 passed. |
| `python3 -m json.tool harness/plugins/autosci/config/feature_parity_routes.v1.json` and `feature_operator_bindings.v1.json` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests -q` | ok: 124 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 54 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific/test_autosci_operator_smoke_gate.py harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py -q` | ok: 6 passed. |
| `.venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci_feature_parity_after_paper_compile_fix_20260625.json` | ok: `full_count=0`, `partial_count=17`, `gated_count=11`, `missing_route_count=0`. |
| `git diff --check -- harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/adapters/autosci_to_literature_discovery.py harness/plugins/autosci/config/feature_parity_routes.v1.json harness/plugins/autosci/config/feature_operator_bindings.v1.json harness/plugins/autosci/tests/test_autosci_skill_shim.py harness/evaluators/scientific/workflow_evolution_gate.py harness/schemas/evidence/workflow_evolution.v1.schema.json docs/integrations/autosci/phase19-progress-log.md` | ok |

### Remaining After Paper Compile Fix Repair

| Block | Status | Notes |
|---|---|---|
| End-to-end compile fix rerun | warn | Source fix writeback is covered, but full compile-fix parity still needs approved fix + TeX execution + PDF checklist in one audited run. |
| Static full parity | blocked | `/paper-compile` remains gated until approved toolchain execution and PDF validation are audited across the native workflow. |

## Phase 19 Autosci Dollar Command Repair

Logged: 2026-06-25 EDT

Planned file changes (pre-fix):
- `harness/plugins/autosci/bin/autosci_skill_shim.py`
- `harness/plugins/autosci/tests/test_autosci_skill_shim.py`
- `docs/integrations/autosci/phase19-progress-log.md`

This fixes single-token `$` command parsing so one-shot invocations such as
`"$survey --format latex --topic test"` no longer get interpreted as an
invalid skill name.

| Command | Result |
|---|---|
| `python3 -m py_compile harness/plugins/autosci/bin/autosci_skill_shim.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_runs_single_token_dollar_command_with_flags -q` | ok: 1 passed. |

### Remaining After Dollar Command Repair

| Block | Status | Notes |
|---|---|---|
| Dollar-command passthrough | ok | Single-token `$skill --flag ...` now resolves to a normalized `skill` command. |
| Static full parity | blocked | Remaining blockers remain in core execution paths (`review`, `exp-run` lifecycle, `paper-compile` toolchain, online evidence fetch). |

## Phase 19 Exp-Run Native Execution Repair

Logged: 2026-06-25 EDT

Planned file changes (pre-fix):
- `harness/plugins/autosci/bin/autosci_bridge.py`
- `harness/plugins/autosci/tests/test_autosci_skill_shim.py`
- `docs/integrations/autosci/phase19-progress-log.md`

### Exp-Run Execution Fix

This repair step enables genuine approved command execution for `run_experiment`
instead of report-only completion:
- command selection now normalizes executable paths from allowlisted plans/commands.
- runtime output parser now attempts to recover JSON payloads from command stdout lines.
- `run_experiment` now computes result-collection status before writing result artifacts (fixing an untested path bug).
- `--execute-approved` runtime path now records `run_experiment_result.json` and `run_experiment_runtime_evidence.json` as part of completed outcomes.

Added regression test:
- `test_autosci_skill_shim_exp_run_executes_approved_native_command` validates that
  `--execute-approved` with allowlist/before-artifact evidence executes the command,
  writes command marker output, and mutates wiki/experiment state from real output.

### Verification commands

| Command | Result |
|---|---|
| `python3 -m py_compile harness/plugins/autosci/bin/autosci_bridge.py harness/plugins/autosci/tests/test_autosci_skill_shim.py` | ok |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_exp_run_executes_approved_native_command -q` | ok: 1 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_exp_run_uses_verified_runtime_evidence_and_mutates_wiki -q` | ok: 1 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q` | ok: 76 passed. |

### Remaining After Exp-Run Execution Repair

| Block | Status | Notes |
|---|---|---|
| Experiment execution lifecycle | partial | Real command execution is now reachable behind approval, but approval/collect/eval chain coverage still needs a full approved deploy→collect→verify path and state transitions across workflow evidence. |
| Static full parity | blocked | `review`, `paper-compile` runtime execution, novelty gate, and online evidence fetch remain incomplete. |

## Phase 19 Exp-Run Artifact Return Repair

Logged: 2026-06-25 EDT

Planned file changes (pre-fix):
- `harness/plugins/autosci/bin/autosci_bridge.py`
- `docs/integrations/autosci/phase19-progress-log.md`

Fix summary:
- `run_experiment` now adds runtime artifacts from `contract.after_artifacts` (`run_experiment_result_json`) to its returned artifact list.
- `run_experiment` now adds missing executor artifacts (`executor_stdout`, `executor_stderr`) by consuming explicit paths returned by executor.
- `_execute_experiment_if_approved` now returns `stdout_path` and `stderr_path` explicitly so action-level artifacts can reference the captured process streams.

### Exp-Run Artifact Return Verification

| Command | Result |
|---|---|
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_exp_run_executes_approved_native_command -q` | ok: 1 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_exp_run_uses_verified_runtime_evidence_and_mutates_wiki harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_exp_collect_uses_verified_runtime_evidence -q` | ok: 2 passed. |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_exp_run_executes_approved_native_command` | ok: 1 passed. |

### Remaining After Exp-Run Artifact Return Repair

| Block | Status | Notes |
|---|---|---|
| Exp-run artifact completeness | ok | Native run branch now returns `run_experiment_result_json` + executor stream artifacts when `--execute-approved` path is used. |
| Lifecycle parity | partial | `collect`/`eval`/resume chains and full experiment state transitions still need one approved end-to-end lifecycle run. |

## Phase 19 Review Artifact Resolver Repair

Logged: 2026-06-25 EDT

Planned file changes (pre-fix):
- `harness/plugins/autosci/backends/artifact_review.py`
- `docs/integrations/autosci/phase19-progress-log.md`

### Review Artifact Resolver Fix Plan

- `artifact_review._path_candidates` / `_resolve_artifact` now treats relative targets that already include `harness/` by adding a normalized candidate without the `harness/` prefix.
- This addresses false misses where `_resolve_artifact` only checked `.../harness/harness/...` paths and could not resolve a workspace artifact passed as `harness/artifacts/...`.

### Review Artifact Resolver Fix Verification

| Command | Result |
|---|---|
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py::test_autosci_skill_shim_review_resolves_harness_prefixed_workspace_path -q` | ok: 1 passed. |
| `python3 harness/plugins/autosci/bin/autosci_skill_shim.py text "\$review --paper harness/artifacts/autosci/workspace/wiki/ideas/idea-001.md --difficulty hard --focus method --run-id harness-review-test-review-fixed"` | ok: resolved to `harness/artifacts/autosci/workspace/wiki/ideas/idea-001.md` with `status=completed`, `passed_count=1`, `schema_only_count=0`. |

## Phase 19 Route Truthfulness Sync For Steps 45-48

Logged: 2026-06-26 EDT

Planned file changes (pre-fix):
- `docs/integrations/autosci/phase19-progress-log.md`

### Route Sync Scope

This documentation-only sync records route-parity changes already made during
the scheduler/native lifecycle continuation:

- Step 45: `$research` route limitations now say default scheduler runs block
  at `report_plan` / `publication_produce` unless explicit Review LLM and
  compile/PDF evidence are supplied with external-evidence dispatch.
- Step 45: `$research.primary_tools` now points at the real
  `harness/tools/run_scientific_lifecycle_smoke.py` path instead of the missing
  `tools/run_scientific_lifecycle_smoke.py`.
- Step 47: `/exp-status` route limitations now distinguish approved
  `tools/remote.py check` execution from registry-only status and keep live
  SSH/provider polling partial.
- Step 48: `/ask`, `/check`, and `/ideate` route limitations now describe
  persisted model-command request/response provenance without claiming hosted
  provider parity.

### Remaining After Route Truthfulness Sync

| Block | Status | Notes |
|---|---|---|
| Route truthfulness for continuation steps | ok | Phase 19 now references the route config truthfulness updates made in Steps 45, 47, and 48. |
| Full parity | blocked | Route inventory remains 0 full, 17 partial, 11 gated until live providers, generic scheduler dispatch, remote polling, and publication parity are proven. |

### Route Truthfulness Sync Verification

| Command | Result |
|---|---|
| `git diff --check -- docs/integrations/autosci/phase19-progress-log.md` | ok |
| `rg -n "Phase 19 Route Truthfulness Sync|Step 45|Step 47|Step 48" docs/integrations/autosci/phase19-progress-log.md` | ok: sync section and referenced continuation steps are present. |

## Phase 19 Publication Review Boundary Sync

Logged: 2026-06-26 EDT

Planned file changes (pre-fix):
- `harness/plugins/autosci/bin/autosci_bridge.py`
- `harness/plugins/autosci/bin/autosci_skill_shim.py`
- `harness/plugins/autosci/tests/test_autosci_skill_shim.py`
- `harness/plugins/autosci/config/feature_parity_routes.v1.json`
- `docs/integrations/autosci/native-lifecycle-continuation-log.md`
- `docs/integrations/autosci/phase15-progress-log.md`
- `docs/integrations/autosci/phase19-progress-log.md`

Intent: tighten `$paper-plan` route truthfulness by recording an explicit
Review LLM boundary object instead of only a permissive boolean completion flag.

### Publication Review Boundary Result

| Check | Status | Evidence |
|---|---|---|
| `$paper-plan` boundary object | ok | `paper_plan_json` now includes `autosci_publication_review_boundary.v1`. |
| Boundary completion rules | ok | Completion requires `artifact_review.v1`, completed payload status, LLM review mode, `review_available=true`, and non-empty evidence ids. |
| Weak Review LLM evidence | ok | Weak Review LLM-shaped JSON is recorded as invalid/inconclusive and does not complete the plan. |
| Route limitation | ok | `/paper-plan` limitation now states explicit Review LLM boundary requirements. |

### Publication Review Boundary Verification

| Command | Result |
|---|---|
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -k 'paper_plan_completes_with_citations_and_review_llm or paper_plan_rejects_weak_review_llm_boundary or paper_plan_attaches_verified_compile_handoff' -q` | ok: 3 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -k 'paper_plan or paper_draft or paper_compile or research_scheduler_executes_approved_publication_compile' -q` | ok: 13 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q` | ok: 101 passed with elevated local bind permission |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step49.json` | warn: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |
| `git diff --check` over Step 49 files | ok before log write |

## Phase 19 Scheduler Production Boundary Sync

Logged: 2026-06-26 EDT

Planned file changes (pre-fix):
- `harness/tools/run_scientific_lifecycle_smoke.py`
- `harness/plugins/autosci/bin/autosci_skill_shim.py`
- `harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py`
- `harness/plugins/autosci/tests/test_autosci_skill_shim.py`
- `harness/plugins/autosci/config/feature_parity_routes.v1.json`
- `docs/integrations/autosci/native-lifecycle-continuation-log.md`
- `docs/integrations/autosci/phase15-progress-log.md`
- `docs/integrations/autosci/phase19-progress-log.md`

Intent: tighten `$research` route truthfulness by adding a scheduler
production-dispatch boundary and strict failure flag for smoke/fixture-backed
lifecycle runs.

### Scheduler Production Boundary Result

| Check | Status | Evidence |
|---|---|---|
| `$research` dispatch boundary | ok | Scheduler lifecycle summaries now include `autosci_scheduler_dispatch_boundary.v1`. |
| Strict production dispatch | ok | `--scheduler-require-production-dispatch` fails while bounded smoke runner or fixture/smoke input markers remain. |
| Route limitation | ok | `/research` now documents the production-dispatch boundary failure condition without changing `coverage_status`. |

### Scheduler Production Boundary Verification

| Command | Result |
|---|---|
| Runner + shim targeted tests | ok: 2 passed |
| Lifecycle smoke + runtime gate subset | ok: 25 passed |
| `$research` scheduler shim subset | ok: 8 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 87 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q` | ok: 102 passed with elevated local bind permission |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step50.json` | warn: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |
| `git diff --check` over Step 50 files | ok before log write |

## Phase 19 Source Provider Boundary Sync

Logged: 2026-06-26 EDT

Planned file changes (pre-fix):
- `harness/plugins/autosci/bin/autosci_bridge.py`
- `harness/plugins/autosci/adapters/autosci_to_literature_discovery.py`
- `harness/plugins/autosci/tests/test_autosci_skill_shim.py`
- `harness/plugins/autosci/config/feature_parity_routes.v1.json`
- `docs/integrations/autosci/native-lifecycle-continuation-log.md`
- `docs/integrations/autosci/phase15-progress-log.md`
- `docs/integrations/autosci/phase19-progress-log.md`

Intent: tighten source/discover route truthfulness by requiring non-fixture
provider channels before source runtime evidence is treated as completed.

### Source Provider Boundary Result

| Check | Status | Evidence |
|---|---|---|
| Source provider boundary | ok | `literature_discovery.v1.outputs.source_provider_boundary` records `autosci_source_provider_boundary.v1`. |
| Generic runtime candidates | ok | Generic `approved_runtime` candidates no longer complete source runtime evidence without provider channels. |
| Provider-backed candidates | ok | `search_s2` channel runtime evidence completes and records provider boundary proof. |
| Route limitation | ok | `/discover`, `/init`, and `$research --online` limitations now describe provider boundary requirements. |

### Source Provider Boundary Verification

| Command | Result |
|---|---|
| Source-boundary targeted tests | ok: 2 passed |
| Literature backend/source CLI subset | ok: 6 passed |
| Source-related shim subset | ok: 6 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 87 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q` | ok: 103 passed with elevated local bind permission |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step51.json` | warn: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |
| `git diff --check` over Step 51 files | ok before log write |

## Phase 19 Remote Poll Boundary Sync

Logged: 2026-06-26 EDT

Planned file changes (pre-fix):
- `harness/plugins/autosci/bin/autosci_bridge.py`
- `harness/plugins/autosci/tests/test_autosci_skill_shim.py`
- `harness/plugins/autosci/config/feature_parity_routes.v1.json`
- `docs/integrations/autosci/native-lifecycle-continuation-log.md`
- `docs/integrations/autosci/phase15-progress-log.md`
- `docs/integrations/autosci/phase19-progress-log.md`

Intent: tighten `$exp-status` route truthfulness by emitting an explicit
remote poll boundary that separates local run-dir status-file checks from live
SSH/provider polling.

### Remote Poll Boundary Result

| Check | Status | Evidence |
|---|---|---|
| Runtime boundary | ok | Approved `$exp-status` remote-check evidence includes `autosci_remote_poll_boundary.v1`. |
| Local status check classification | ok | `tools/remote.py check` against local `run_dir/status.json` now reports boundary status `local_run_dir_check`, not live provider polling. |
| Route limitation | ok | `/exp-status` documents that local run-dir status-file checks do not count as live SSH/provider polling. |

### Remote Poll Boundary Verification

| Command | Result |
|---|---|
| `py_compile` bridge/tests | ok |
| route config `json.tool` | ok |
| `$exp-status` approved remote-check boundary test | ok: 1 passed |
| exp-status/run/collect remote subset | ok: 12 passed |
| runtime binding audit | ok: 28 nodes, 2 workflows, 0 issues |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q` | ok: 103 passed with elevated local bind permission |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step52.json` | warn: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |
| `git diff --check` over Step 52 files | ok before log write |

## Phase 19 Approved Live Remote Status Command Sync

Logged: 2026-06-26 EDT

Planned file changes (pre-fix):
- `tools/remote.py`
- `harness/plugins/autosci/bin/autosci_bridge.py`
- `harness/plugins/autosci/tests/test_autosci_skill_shim.py`
- `harness/plugins/autosci/config/feature_parity_routes.v1.json`
- `docs/integrations/autosci/native-lifecycle-continuation-log.md`
- `docs/integrations/autosci/phase15-progress-log.md`
- `docs/integrations/autosci/phase19-progress-log.md`

Intent: add an approved live/provider status command path that can satisfy the
remote poll boundary without weakening allowlist or approval requirements.

### Approved Live Remote Status Command Result

| Check | Status | Evidence |
|---|---|---|
| `tools/remote.py check --status-command` | ok | Live/provider status command path is approval-gated and allowlisted. |
| Remote poll boundary | ok | Approved status command payload can satisfy `autosci_remote_poll_boundary.v1` with transport/session metadata and `remote_state`. |
| Local check preservation | ok | Plain run-dir checks still report `local_run_dir_check`, not live polling. |
| Route limitation | ok | `/exp-status` now names approved live/provider status command execution while keeping real external connectivity smoke pending. |

### Approved Live Remote Status Command Verification

| Command | Result |
|---|---|
| `py_compile` tools/bridge/tests | ok |
| route config `json.tool` | ok |
| local + live `$exp-status` targeted tests | ok: 2 passed |
| exp-status/run/collect remote subset | ok: 13 passed |
| runtime binding audit | ok: 28 nodes, 2 workflows, 0 issues |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q` | ok: 104 passed with elevated local bind permission |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step53.json` | warn: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |
| `git diff --check` over Step 53 files | ok before log write |

## Phase 19 Remote Pull Results Boundary Sync

Logged: 2026-06-26 EDT

Planned file changes (pre-fix):
- `tools/remote.py`
- `harness/plugins/autosci/bin/autosci_bridge.py`
- `harness/plugins/autosci/tests/test_autosci_skill_shim.py`
- `harness/plugins/autosci/config/feature_parity_routes.v1.json`
- `docs/integrations/autosci/native-lifecycle-continuation-log.md`
- `docs/integrations/autosci/phase15-progress-log.md`
- `docs/integrations/autosci/phase19-progress-log.md`

Intent: add an approved remote/provider pull-results path and collection
boundary so local result-dir reads are not counted as live provider collection.

### Remote Pull Results Boundary Result

| Check | Status | Evidence |
|---|---|---|
| `tools/remote.py pull-results --pull-command` | ok | Live/provider pull-results command path is approval-gated and allowlisted. |
| Remote collection boundary | ok | Collect runtime evidence includes `autosci_remote_collection_boundary.v1`. |
| Local collection preservation | ok | Plain result-dir reads report `local_result_dir_collection`, not live provider collection. |
| Route limitation | ok | `/exp-run` names approved live/provider pull-results boundary and keeps distributed exactly-once/external smoke pending. |

### Remote Pull Results Boundary Verification

| Command | Result |
|---|---|
| `py_compile` tools/bridge/tests | ok |
| route config `json.tool` | ok |
| local + live pull-results targeted tests | ok: 2 passed |
| exp-status/run/collect remote subset | ok: 15 passed |
| runtime binding audit | ok: 28 nodes, 2 workflows, 0 issues |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q` | ok: 105 passed with elevated local bind permission |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step54.json` | warn: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |
| `git diff --check` over Step 54 files | ok before log write |

## Phase 19 Scheduler Replay Resume Boundary Sync

Logged: 2026-06-26 EDT

Planned file changes (pre-fix):
- `harness/tools/run_scientific_lifecycle_smoke.py`
- `harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py`
- `harness/plugins/autosci/tests/test_autosci_skill_shim.py`
- `harness/plugins/autosci/config/feature_parity_routes.v1.json`
- `docs/integrations/autosci/native-lifecycle-continuation-log.md`
- `docs/integrations/autosci/phase15-progress-log.md`
- `docs/integrations/autosci/phase19-progress-log.md`

Intent: add scheduler replay/resume evidence so lifecycle dispatch cannot be
mistaken for production parity without durable node state and no-rerun proof.

### Scheduler Replay Resume Boundary Result

| Check | Status | Evidence |
|---|---|---|
| Resume boundary | ok | Resume summaries emit `autosci_scheduler_resume_boundary.v1`. |
| No-rerun proof | ok | Boundary records reused-node fingerprints, changed reused nodes, dispatched nodes, and `no_rerun_verified`. |
| Route limitation | ok | `/research` now names resume boundary while keeping non-smoke dispatcher and lease/runtime audit pending. |

### Scheduler Replay Resume Boundary Verification

| Command | Result |
|---|---|
| `py_compile` runner/test | ok |
| route config `json.tool` | ok |
| human-gate resume targeted test | ok: 1 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 87 passed |
| `$research` scheduler shim subset | ok: 8 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q` | ok: 105 passed with elevated local bind permission |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step55.json` | warn: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |
| `git diff --check` over Step 55 files | ok before log write |

## Phase 19 Scheduler Lease Boundary Sync

Logged: 2026-06-26 EDT

Planned file changes (pre-fix):
- `harness/tools/run_scientific_lifecycle_smoke.py`
- `harness/tests/evaluators/scientific/test_scientific_lifecycle_runtime_smoke.py`
- `harness/plugins/autosci/config/feature_parity_routes.v1.json`
- `docs/integrations/autosci/native-lifecycle-continuation-log.md`
- `docs/integrations/autosci/phase15-progress-log.md`
- `docs/integrations/autosci/phase19-progress-log.md`

Intent: add scheduler lease evidence and boundary fields so local smoke-run
lease ownership is visible and not confused with distributed production leases.

### Scheduler Lease Boundary Result

| Check | Status | Evidence |
|---|---|---|
| Lease sidecar | ok | Lifecycle run/resume writes `autosci_scheduler_lease.v1` sidecar evidence. |
| Lease boundary | ok | Lifecycle summaries include `autosci_scheduler_lease_boundary.v1`. |
| Route limitation | ok | `/research` now names local lease boundary while keeping distributed lease/quota/runtime audit pending. |

### Scheduler Lease Boundary Verification

| Command | Result |
|---|---|
| `py_compile` runner/test | ok |
| route config `json.tool` | ok |
| blocked lifecycle + resume targeted tests | ok: 2 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/tests/evaluators/scientific -q` | ok: 87 passed |
| `$research` scheduler shim subset | ok: 8 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q` | ok: 105 passed with elevated local bind permission |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step56.json` | warn: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |
| `git diff --check` over Step 56 files | ok before log write |

## Phase 19 Publication Submission Checklist Boundary Sync

Logged: 2026-06-26 EDT

Planned file changes (pre-fix):
- `harness/plugins/autosci/bin/autosci_bridge.py`
- `harness/plugins/autosci/tests/test_autosci_skill_shim.py`
- `harness/plugins/autosci/config/feature_parity_routes.v1.json`
- `docs/integrations/autosci/native-lifecycle-continuation-log.md`
- `docs/integrations/autosci/phase15-progress-log.md`
- `docs/integrations/autosci/phase19-progress-log.md`

Intent: add publication submission checklist boundary so compile/PDF success is
not confused with submission/anonymity/page/font readiness.

### Publication Submission Checklist Boundary Result

| Check | Status | Evidence |
|---|---|---|
| Submission boundary | ok | Paper compile writes `autosci_publication_submission_boundary.v1` sidecar evidence. |
| Checklist/diagnostics | ok | Checklist embeds boundary and diagnostics render a Submission Boundary section. |
| Bundle artifact | ok | Publication bundle includes `publication_submission_boundary_json`. |
| Route limitation | ok | `/paper-compile` now separates compile/PDF evidence from submission readiness. |

### Publication Submission Checklist Boundary Verification

| Command | Result |
|---|---|
| `py_compile` bridge/tests | ok |
| route config `json.tool` | ok |
| submission checklist boundary targeted test | ok: 1 passed |
| paper-compile/paper-plan/paper-draft publication subset | ok: 10 passed |
| `env PYTHONPATH=harness .venv/bin/python -m pytest harness/plugins/autosci/tests/test_autosci_skill_shim.py -q` | ok: 105 passed with elevated local bind permission |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step57.json` | warn: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |
| `git diff --check` over Step 57 files | ok before log write |

## Phase 19 Paper Compile Submission Evidence Flags Sync

Logged: 2026-06-26 EDT

Planned file changes (pre-fix):
- `harness/plugins/autosci/bin/autosci_skill_shim.py`
- `harness/plugins/autosci/tests/test_autosci_skill_shim.py`
- `harness/plugins/autosci/config/feature_parity_routes.v1.json`
- `docs/integrations/autosci/native-lifecycle-continuation-log.md`
- `docs/integrations/autosci/phase15-progress-log.md`
- `docs/integrations/autosci/phase19-progress-log.md`

Intent: expose paper-compile submission evidence flags for anonymous mode,
page-count/page-limit, and minimum font-size proof.

### Paper Compile Submission Evidence Flags Result

| Check | Status | Evidence |
|---|---|---|
| CLI flags | ok | `$paper-compile` now forwards anonymity, page, and font-size evidence flags into compile inputs. |
| Submission boundary | ok | Explicit evidence can make `autosci_publication_submission_boundary.v1` report `submission_ready`. |
| Route limitation | ok | `/paper-compile` now records that CLI flags satisfy readiness only with explicit proof. |

### Paper Compile Submission Evidence Flags Verification

| Command | Result |
|---|---|
| `py_compile` shim/tests | ok |
| route config JSON load | ok |
| submission incomplete + submission-ready targeted tests | ok: 2 passed |
| paper-compile/paper-plan/paper-draft publication subset | ok: 11 passed |
| full shim suite with elevated local bind permission | ok: 106 passed |
| default sandbox full shim suite | warn: local `127.0.0.1` bind was denied before elevated rerun |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step58.json` | warn: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |
| `git diff --check` over Step 58 files | ok before log write |

## Phase 19 Paper Compile Venue Submission Profile Boundary Sync

Logged: 2026-06-26 EDT

Planned file changes (pre-fix):
- `harness/plugins/autosci/bin/autosci_bridge.py`
- `harness/plugins/autosci/bin/autosci_skill_shim.py`
- `harness/plugins/autosci/tests/test_autosci_skill_shim.py`
- `harness/plugins/autosci/config/feature_parity_routes.v1.json`
- `docs/integrations/autosci/native-lifecycle-continuation-log.md`
- `docs/integrations/autosci/phase15-progress-log.md`
- `docs/integrations/autosci/phase19-progress-log.md`

Intent: add source-backed venue submission profile input so compile readiness
uses explicit venue requirements rather than loose CLI-only claims.

### Paper Compile Venue Submission Profile Boundary Result

| Check | Status | Evidence |
|---|---|---|
| Profile input | ok | `$paper-compile --submission-profile` forwards source-backed venue requirements into compile inputs. |
| Venue boundary | ok | Publication boundary now includes `venue_submission_ready`, `venue_status`, `venue_blocking_checks`, and embedded profile evidence. |
| Diagnostics/artifacts | ok | Diagnostics and bundle artifacts expose the loaded profile and SHA-256. |
| Route limitation | ok | `/paper-compile` now requires source-backed profile evidence for venue-specific readiness. |

### Paper Compile Venue Submission Profile Boundary Verification

| Command | Result |
|---|---|
| `py_compile` bridge/shim/tests | ok |
| route config JSON load | ok |
| missing evidence + CLI evidence + venue profile targeted tests | ok: 3 passed |
| paper-compile/paper-plan/paper-draft publication subset | ok: 12 passed |
| full shim suite with elevated local bind permission | ok: 107 passed |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step59.json` | warn: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |
| `git diff --check` over Step 59 files | ok before log write |

## Phase 19 Paper Compile PDF Inspection Evidence Ingestion Sync

Logged: 2026-06-26 EDT

Planned file changes (pre-fix):
- `harness/plugins/autosci/bin/autosci_bridge.py`
- `harness/plugins/autosci/bin/autosci_skill_shim.py`
- `harness/plugins/autosci/tests/test_autosci_skill_shim.py`
- `harness/plugins/autosci/config/feature_parity_routes.v1.json`
- `docs/integrations/autosci/native-lifecycle-continuation-log.md`
- `docs/integrations/autosci/phase15-progress-log.md`
- `docs/integrations/autosci/phase19-progress-log.md`

Intent: ingest explicit PDF inspection evidence for verified page count and
minimum font size instead of relying only on loose numeric CLI flags.

### Paper Compile PDF Inspection Evidence Ingestion Result

| Check | Status | Evidence |
|---|---|---|
| PDF inspection input | ok | `$paper-compile --pdf-inspection` forwards PDF inspection evidence to compile inputs. |
| PDF evidence boundary | ok | Bridge validates inspection sidecars against discovered PDFs by path or SHA-256. |
| Venue readiness | ok | `venue_submission_ready` now requires profile plus PDF inspection evidence. |
| Diagnostics/artifacts | ok | Diagnostics and bundle artifacts expose PDF inspection status and SHA-256. |
| Route limitation | ok | `/paper-compile` now distinguishes generic CLI checks from source-backed venue readiness. |

### Paper Compile PDF Inspection Evidence Ingestion Verification

| Command | Result |
|---|---|
| `py_compile` bridge/shim/tests | ok |
| route config JSON load | ok |
| missing evidence + CLI evidence + profile-only + profile/PDF-inspection targeted tests | ok: 4 passed |
| paper-compile/paper-plan/paper-draft publication subset | ok: 13 passed |
| full shim suite with elevated local bind permission | ok: 108 passed |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step60.json` | warn: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |
| `git diff --check` over Step 60 files | ok before log write |

## Phase 19 Publication Submission Audit Evidence Boundary Sync

Logged: 2026-06-26 EDT

Planned file changes (pre-fix):
- `harness/plugins/autosci/bin/autosci_bridge.py`
- `harness/plugins/autosci/bin/autosci_skill_shim.py`
- `harness/plugins/autosci/tests/test_autosci_skill_shim.py`
- `harness/plugins/autosci/config/feature_parity_routes.v1.json`
- `docs/integrations/autosci/native-lifecycle-continuation-log.md`
- `docs/integrations/autosci/phase15-progress-log.md`
- `docs/integrations/autosci/phase19-progress-log.md`

Intent: add explicit publication submission audit evidence so venue readiness
and final submission audit readiness are separate source-backed states.

### Publication Submission Audit Evidence Boundary Result

| Check | Status | Evidence |
|---|---|---|
| Submission audit input | ok | `$paper-compile --submission-audit` forwards explicit audit evidence into compile inputs. |
| Audit boundary | ok | Publication boundary now includes audit readiness, audit blocking checks, and portal completion as separate fields. |
| Portal truthfulness | ok | Portal completion is not implied by audit readiness. |
| Diagnostics/artifacts | ok | Diagnostics and bundle artifacts expose submission audit status and SHA-256. |
| Route limitation | ok | `/paper-compile` now names explicit submission audit evidence as required for audit readiness. |

### Publication Submission Audit Evidence Boundary Verification

| Command | Result |
|---|---|
| `py_compile` bridge/shim/tests | ok |
| route config JSON load | ok |
| paper-compile submission/profile/PDF/audit targeted tests | ok: 5 passed |
| paper-compile/paper-plan/paper-draft publication subset | ok: 14 passed |
| full shim suite with elevated local bind permission | ok: 109 passed |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step61.json` | warn: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |
| `git diff --check` over Step 61 files | ok before log write |

## Phase 19 Review LLM Final Acceptance Boundary Sync

Logged: 2026-06-26 EDT

Planned file changes (pre-fix):
- `harness/plugins/autosci/bin/autosci_bridge.py`
- `harness/plugins/autosci/bin/autosci_skill_shim.py`
- `harness/plugins/autosci/tests/test_autosci_skill_shim.py`
- `harness/plugins/autosci/config/feature_parity_routes.v1.json`
- `docs/integrations/autosci/native-lifecycle-continuation-log.md`
- `docs/integrations/autosci/phase15-progress-log.md`
- `docs/integrations/autosci/phase19-progress-log.md`

Intent: add explicit Review LLM final acceptance evidence so local surrogate
review is not confused with provider/command/evidence-backed final review.

### Review LLM Final Acceptance Boundary Result

| Check | Status | Evidence |
|---|---|---|
| Requirement flag | ok | `$review --require-review-llm` records that local surrogate review is insufficient for final acceptance. |
| Final boundary | ok | Review evidence includes `autosci_review_final_acceptance_boundary.v1`. |
| Local surrogate separation | ok | Local surrogate review now reports `review_llm_incomplete` rather than final acceptance. |
| Provider/evidence readiness | ok | Supplied Review LLM evidence, command bridge, and OpenAI-compatible provider mode can report `final_acceptance_ready`. |
| Route limitation | ok | `/review` now names the final acceptance boundary and local surrogate insufficiency. |

### Review LLM Final Acceptance Boundary Verification

| Command | Result |
|---|---|
| `py_compile` bridge/shim/tests | ok |
| route config JSON load | ok |
| local/evidence/command/provider review boundary targeted tests | ok: 4 passed |
| `-k review` subset | ok: 15 passed with elevated local bind permission |
| full shim suite with elevated local bind permission | ok: 109 passed |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step62.json` | warn: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |
| `git diff --check` over Step 62 files | ok before log write |

## Phase 19 Novelty Final Acceptance Boundary Sync

Logged: 2026-06-28 EDT

Planned file changes (pre-fix):
- `harness/plugins/autosci/bin/autosci_bridge.py`
- `harness/plugins/autosci/tests/test_autosci_skill_shim.py`
- `harness/plugins/autosci/config/feature_parity_routes.v1.json`
- `docs/integrations/autosci/native-lifecycle-continuation-log.md`
- `docs/integrations/autosci/phase15-progress-log.md`
- `docs/integrations/autosci/phase19-progress-log.md`

Intent: add explicit novelty final acceptance boundary requiring external
novelty evidence plus Review LLM proof, while keeping local/source-only checks
incomplete for final acceptance.

### Novelty Final Acceptance Boundary Result

| Check | Status | Evidence |
|---|---|---|
| Evaluation boundary | ok | Novelty evaluations embed `autosci_novelty_final_acceptance_boundary.v1`. |
| Boundary sidecar | ok | Evaluate-ideas writes `novelty_final_acceptance_boundary.json`. |
| Source/review requirements | ok | Final acceptance requires external novelty completion, provider provenance pass, Review LLM completion, and numeric novelty score. |
| Writeback linkage | ok | Novelty writeback records final acceptance status without changing existing writeback gating order. |
| Route limitation | ok | `/novelty` now names the final acceptance boundary and required evidence. |

### Novelty Final Acceptance Boundary Verification

| Command | Result |
|---|---|
| `py_compile` bridge/tests | ok |
| route config JSON load | ok |
| local/external-only/external+Review LLM/missing-review novelty targeted tests | ok: 4 passed |
| `-k novelty` subset | ok: 11 passed |
| full shim suite with elevated local bind permission | ok: 109 passed |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step63.json` | warn: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |
| `git diff --check` over Step 63 files | ok before log write |

## Phase 19 Ask Final Answer Boundary Sync

Logged: 2026-06-28 EDT

Planned file changes (pre-fix):
- `harness/plugins/autosci/bin/autosci_bridge.py`
- `harness/plugins/autosci/tests/test_autosci_skill_shim.py`
- `harness/plugins/autosci/config/feature_parity_routes.v1.json`
- `docs/integrations/autosci/native-lifecycle-continuation-log.md`
- `docs/integrations/autosci/phase15-progress-log.md`
- `docs/integrations/autosci/phase19-progress-log.md`

Intent: add explicit final answer boundary for `/ask` requiring retrieval/source
evidence plus model-backed synthesis, without treating retrieval-only local
summaries as final.

### Ask Final Answer Boundary Result

| Check | Status | Evidence |
|---|---|---|
| Final answer boundary | ok | `/ask` retrieval JSON embeds `autosci_ask_final_answer_boundary.v1`. |
| Boundary sidecar | ok | Ask runs write `ask_final_answer_boundary.json`. |
| Retrieval/model separation | ok | Retrieval-only answers report `ask_final_answer_incomplete`. |
| Model-backed readiness | ok | Retrieval plus completed model synthesis reports `final_answer_ready`. |
| Route limitation | ok | `/ask` now names the boundary and source/model requirements. |

### Ask Final Answer Boundary Verification

| Command | Result |
|---|---|
| `py_compile` bridge/tests | ok |
| route config JSON load | ok |
| retrieval-only and model-command ask targeted tests | ok: 2 passed |
| full shim suite with elevated local bind permission | ok: 109 passed |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step64.json` | warn: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |
| `git diff --check` over Step 64 files | ok before log write |

## Phase 19 Check Final Quality Boundary Sync

Logged: 2026-06-28 EDT

Planned file changes (pre-fix):
- `harness/plugins/autosci/bin/autosci_bridge.py`
- `harness/plugins/autosci/tests/test_autosci_skill_shim.py`
- `harness/plugins/autosci/config/feature_parity_routes.v1.json`
- `docs/integrations/autosci/native-lifecycle-continuation-log.md`
- `docs/integrations/autosci/phase15-progress-log.md`
- `docs/integrations/autosci/phase19-progress-log.md`

Intent: add explicit final quality boundary for `/check` requiring local wiki
checks plus model-backed recommendation evidence, without treating lint-only
output as final review.

### Check Final Quality Boundary Result

| Check | Status | Evidence |
|---|---|---|
| Final quality boundary | ok | `/check` embeds `autosci_check_final_quality_boundary.v1` in workflow evolution review metadata. |
| Boundary sidecar | ok | Check runs write `check_final_quality_boundary.json`. |
| Local/model separation | ok | Local structural checks alone remain incomplete for final quality. |
| Model-backed readiness | ok | Completed model evidence plus passing local checks can report `final_quality_ready`. |
| Route limitation | ok | `/check` now names the final quality boundary and local/model requirements. |

### Check Final Quality Boundary Verification

| Command | Result |
|---|---|
| `py_compile` bridge/tests | ok |
| route config JSON load | ok |
| retrieval/check local and model-command check targeted tests | ok: 2 passed |
| `-k 'ask or check'` subset | ok: 8 passed |
| full shim suite with elevated local bind permission | ok: 109 passed |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step65.json` | warn: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |
| `git diff --check` over Step 65 files | ok before log write |

## Phase 19 Discover Final Shortlist Boundary Sync

Logged: 2026-06-28 EDT

Planned file changes (pre-fix):
- `harness/plugins/autosci/bin/autosci_bridge.py`
- `harness/plugins/autosci/tests/test_autosci_skill_shim.py`
- `harness/plugins/autosci/config/feature_parity_routes.v1.json`
- `docs/integrations/autosci/native-lifecycle-continuation-log.md`
- `docs/integrations/autosci/phase15-progress-log.md`
- `docs/integrations/autosci/phase19-progress-log.md`

Intent: add explicit discovery final shortlist boundary requiring source-backed
provider evidence, without treating local fallback/fixture candidates as final
discovery.

### Discover Final Shortlist Boundary Result

| Check | Status | Evidence |
|---|---|---|
| Final shortlist boundary | ok | Discover source provider boundary embeds `autosci_discover_final_shortlist_boundary.v1`. |
| Boundary sidecar | ok | Discover writes `discover_final_shortlist_boundary.json`. |
| Local/provider separation | ok | Empty/local/generic runtime candidates remain incomplete for final shortlist readiness. |
| Provider-backed readiness | ok | Provider-backed candidates can report `final_shortlist_ready`. |
| Route limitation | ok | `/discover` now names the final shortlist boundary and provider-channel requirements. |

### Discover Final Shortlist Boundary Verification

| Command | Result |
|---|---|
| `py_compile` bridge/tests | ok |
| route config JSON load | ok |
| wiki/local, generic runtime, and provider-backed runtime discovery targeted tests | ok |
| `-k 'discover or source_runtime_evidence'` subset | ok: 4 passed |
| full shim suite with elevated local bind permission | ok: 109 passed |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step66.json` | warn: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |
| `git diff --check` over Step 66 files | ok before log write |

## Phase 19 Survey Final Coverage Boundary Sync

Logged: 2026-06-28 EDT

Planned file changes (pre-fix):
- `harness/plugins/autosci/bin/autosci_bridge.py`
- `harness/plugins/autosci/tests/test_autosci_skill_shim.py`
- `harness/plugins/autosci/config/feature_parity_routes.v1.json`
- `docs/integrations/autosci/native-lifecycle-continuation-log.md`
- `docs/integrations/autosci/phase15-progress-log.md`
- `docs/integrations/autosci/phase19-progress-log.md`

Intent: add explicit survey final coverage boundary requiring source-backed
citation coverage, without treating partial/local citation maps as exhaustive
survey evidence.

### Survey Final Coverage Boundary Result

| Check | Status | Evidence |
|---|---|---|
| Final coverage boundary | ok | `/survey` writes `autosci_survey_final_coverage_boundary.v1`. |
| Boundary sidecar | ok | Survey artifacts include `survey_final_coverage_boundary_json`. |
| Bounded/exhaustive separation | ok | Bounded source-backed coverage can pass while exhaustive coverage remains false without provider audit. |
| Scaffold separation | ok | Survey scaffolds without citations remain incomplete. |
| Route limitation | ok | `/survey` now names bounded coverage and keeps exhaustive live coverage pending. |

### Survey Final Coverage Boundary Verification

| Command | Result |
|---|---|
| `py_compile` bridge/tests | ok |
| route config JSON load | ok |
| survey scaffold and citation-map completion targeted tests | ok: 2 passed |
| `-k 'survey or paper_plan or paper_compile or paper_draft'` subset | ok: 19 passed |
| full shim suite with elevated local bind permission | ok: 109 passed |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step67.json` | warn: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |
| `git diff --check` over Step 67 files | ok before log write |

## Phase 19 Paper Draft Final Manuscript Boundary Sync

Logged: 2026-06-28 EDT

Planned file changes (pre-fix):
- `harness/plugins/autosci/bin/autosci_bridge.py`
- `harness/plugins/autosci/tests/test_autosci_skill_shim.py`
- `harness/plugins/autosci/config/feature_parity_routes.v1.json`
- `docs/integrations/autosci/native-lifecycle-continuation-log.md`
- `docs/integrations/autosci/phase15-progress-log.md`
- `docs/integrations/autosci/phase19-progress-log.md`

Intent: add explicit paper-draft final manuscript boundary requiring source
evidence, citation map, Review LLM proof, and compile/PDF handoff before
treating a draft as publication-ready.

### Paper Draft Final Manuscript Boundary Result

| Check | Status | Evidence |
|---|---|---|
| Final manuscript boundary | ok | `/paper-draft` writes `autosci_paper_draft_final_manuscript_boundary.v1`. |
| Boundary sidecar | ok | Draft artifacts include `paper_draft_final_manuscript_boundary_json`; publication bundle passthrough includes it. |
| Citation map sidecar | ok | Draft artifacts include `citation_map_json` from `paper_draft_citation_map.json`. |
| Publication-ready separation | ok | Plain LaTeX drafts stay incomplete for final manuscript readiness. |
| Final-ready path | ok | Source citation evidence, completed Review LLM proof, and verified compile/PDF handoff can satisfy `final_manuscript_ready`. |
| Route limitation | ok | `/paper-draft` now names final manuscript boundary requirements. |

### Paper Draft Final Manuscript Boundary Verification

| Command | Result |
|---|---|
| `py_compile` bridge/tests | ok |
| route config JSON load | ok |
| paper-draft incomplete and final-ready boundary targeted tests | ok: 2 passed |
| `-k 'survey or paper_plan or paper_compile or paper_draft'` subset | ok: 19 passed |
| full shim suite with elevated local bind permission | ok: 109 passed |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step68.json` | warn: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |
| `git diff --check` over Step 68 files | ok before log write |

## Phase 19 Paper Plan Final Acceptance Boundary Sync

Logged: 2026-06-28 EDT

Planned file changes (pre-fix):
- `harness/plugins/autosci/bin/autosci_bridge.py`
- `harness/plugins/autosci/tests/test_autosci_skill_shim.py`
- `harness/plugins/autosci/config/feature_parity_routes.v1.json`
- `docs/integrations/autosci/native-lifecycle-continuation-log.md`
- `docs/integrations/autosci/phase15-progress-log.md`
- `docs/integrations/autosci/phase19-progress-log.md`

Intent: add explicit paper-plan final acceptance boundary requiring source-backed
citation plan, Review LLM proof, and downstream compile/PDF handoff before
treating a plan as draft/compile-ready.

Scope amendment before fix:
- `harness/tools/run_scientific_lifecycle_smoke.py`

Reason: full shim verification showed scheduler `report_plan` did not receive
compile/PDF handoff inputs, so the new paper-plan final acceptance boundary
could not pass in the approved publication compile lifecycle. Propagate existing
approved compile evidence only; do not loosen the boundary.

### Paper Plan Final Acceptance Boundary Result

| Check | Status | Evidence |
|---|---|---|
| Final plan acceptance boundary | ok | `/paper-plan` writes `autosci_paper_plan_final_acceptance_boundary.v1`. |
| Boundary sidecar | ok | Plan artifacts include `paper_plan_final_acceptance_boundary_json`. |
| Draft/compile readiness separation | ok | Citation plus Review LLM without compile/PDF stays incomplete for final acceptance. |
| Final-ready path | ok | Source citation plan, Review LLM proof, and verified compile/PDF handoff can satisfy `final_plan_accepted`. |
| Scheduler handoff | ok | Scheduler `report_plan` receives approved compile contract fields; approved compile execution can generate plan-boundary runtime/PDF handoff. |
| Route limitation | ok | `/paper-plan` now names final acceptance boundary requirements. |

### Paper Plan Final Acceptance Boundary Verification

| Command | Result |
|---|---|
| `py_compile` bridge/scheduler/tests | ok |
| route config JSON load | ok |
| paper-plan final acceptance boundary targeted tests | ok: 3 passed |
| approved publication compile scheduler regression | ok: 1 passed |
| `-k 'survey or paper_plan or paper_compile or paper_draft or research_scheduler_executes_approved_publication_compile'` subset | ok: 20 passed |
| full shim suite with elevated local bind permission | ok: 109 passed |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step69.json` | warn: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |
| `git diff --check` over Step 69 files | ok before log write |

## Phase 19 Ideate Final Promotion Boundary Sync

Logged: 2026-06-28 EDT

Planned file changes (pre-fix):
- `harness/plugins/autosci/bin/autosci_bridge.py`
- `harness/plugins/autosci/tests/test_autosci_skill_shim.py`
- `harness/plugins/autosci/config/feature_parity_routes.v1.json`
- `docs/integrations/autosci/native-lifecycle-continuation-log.md`
- `docs/integrations/autosci/phase15-progress-log.md`
- `docs/integrations/autosci/phase19-progress-log.md`

Intent: add explicit `/ideate` final promotion boundary requiring wiki maturity
scan, failed-idea banlist check, source-backed evidence, model brainstorm
provenance, and novelty/review gate references before generated ideas are
promotable.

### Ideate Final Promotion Boundary Result

| Check | Status | Evidence |
|---|---|---|
| Final promotion boundary | ok | `/ideate` writes `autosci_ideate_final_promotion_boundary.v1`. |
| Per-idea boundary | ok | Generated ideas include `autosci_ideate_idea_promotion_boundary.v1` and `promotion_ready`. |
| Boundary sidecar | ok | Generate-ideas artifacts include `ideate_final_promotion_boundary_json`. |
| Source/model/gate separation | ok | Source-grounded and model-command ideas remain non-promotable until novelty/review gate references are supplied. |
| Missing-source separation | ok | Missing-source ideation remains inconclusive and boundary records missing source evidence. |
| Route limitation | ok | `/ideate` now names final promotion boundary requirements. |

### Ideate Final Promotion Boundary Verification

| Command | Result |
|---|---|
| `py_compile` bridge/tests | ok |
| route config JSON load | ok |
| ideate source/model/missing-source boundary targeted tests | ok: 3 passed |
| `-k 'ideate or novelty'` subset | ok: 14 passed |
| full shim suite with elevated local bind permission | ok: 109 passed |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step70.json` | warn: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |
| `git diff --check` over Step 70 files | ok before log write |

## Phase 19 Experiment Design Final Execution Boundary Sync

Logged: 2026-06-28 EDT

Planned file changes (pre-fix):
- `harness/plugins/autosci/bin/autosci_bridge.py`
- `harness/plugins/autosci/tests/test_autosci_skill_shim.py`
- `harness/plugins/autosci/config/feature_parity_routes.v1.json`
- `docs/integrations/autosci/native-lifecycle-continuation-log.md`
- `docs/integrations/autosci/phase15-progress-log.md`
- `docs/integrations/autosci/phase19-progress-log.md`

Intent: add explicit `/exp-design` final execution-readiness boundary requiring
resolved idea/evaluation evidence, completed Review LLM design validation, and
declared runtime/artifact handoff requirements before an experiment plan is
executable.

### Experiment Design Final Execution Boundary Result

| Check | Status | Evidence |
|---|---|---|
| Final execution boundary | ok | `/exp-design` writes `autosci_experiment_design_final_execution_boundary.v1`. |
| Boundary sidecar | ok | Experiment-plan artifacts include `experiment_design_final_execution_boundary_json`. |
| Plan embedding | ok | `source_context.final_execution_boundary` records target, Review LLM, approval preflight, command handoff, and artifact handoff state. |
| Review-only separation | ok | Review-only designs remain incomplete for execution readiness. |
| Execution-ready path | ok | Review LLM plus approval/allowlist/before preflight can satisfy `execution_ready`. |
| Network isolation | ok | Local novelty test disables network fetch so live S2 availability cannot alter local-source expectations. |
| Route limitation | ok | `/exp-design` now names final execution boundary requirements. |

### Experiment Design Final Execution Boundary Verification

| Command | Result |
|---|---|
| `py_compile` bridge/tests | ok |
| route config JSON load | ok |
| exp-design final execution boundary targeted tests | ok: 2 passed |
| failed full-suite cases after isolation fix | ok: 2 passed |
| `-k 'exp_design or exp_run or exp_status or exp_pilot or novelty'` subset | ok: 28 passed |
| full shim suite with elevated local bind permission | ok: 110 passed |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step71.json` | warn: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |
| `git diff --check` over Step 71 files | ok before log write |

## Phase 19 Experiment Evaluation Final Verdict Boundary Sync

Logged: 2026-06-28 EDT

Planned file changes (pre-fix):
- `harness/plugins/autosci/bin/autosci_bridge.py`
- `harness/plugins/autosci/tests/test_autosci_skill_shim.py`
- `harness/plugins/autosci/config/feature_parity_routes.v1.json`
- `docs/integrations/autosci/native-lifecycle-continuation-log.md`
- `docs/integrations/autosci/phase15-progress-log.md`
- `docs/integrations/autosci/phase19-progress-log.md`

Intent: add explicit `/exp-eval` final verdict boundary requiring experiment
result evidence, linked claim/code evidence, completed Review LLM proof, and
explicit writeback status before verdicts are treated as final.

### Experiment Evaluation Final Verdict Boundary Result

| Check | Status | Evidence |
|---|---|---|
| Final verdict boundary | ok | `/exp-eval` writes `autosci_experiment_evaluation_final_verdict_boundary.v1`. |
| Boundary sidecar | ok | Claim-verdict artifacts include `experiment_evaluation_final_verdict_boundary_json`. |
| Verdict embedding | ok | Verdict payloads include `final_verdict_boundary` and `final_verdict_ready`. |
| Non-final separation | ok | Evidence-backed verdicts without approved wiki writeback remain `final_verdict_incomplete`. |
| Final-ready path | ok | Experiment result, claim/code evidence, Review LLM proof, and completed approved writeback satisfy `final_verdict_ready`. |
| Route limitation | ok | `/exp-eval` now records approval-required writeback policy and final verdict boundary requirements. |

### Experiment Evaluation Final Verdict Boundary Verification

| Command | Result |
|---|---|
| `py_compile` bridge/tests | ok |
| route config JSON load | ok |
| exp-eval final verdict boundary targeted tests | ok: 2 passed |
| `-k 'exp_eval or exp_pilot_eval or exp_design or exp_run or exp_status or exp_pilot'` subset | ok: 19 passed |
| full shim suite with elevated local bind permission | ok: 110 passed |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step72.json` | warn: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |
| `git diff --check` over Step 72 files | ok before log write |

## Phase 19 Experiment Run Final Runtime Audit Boundary Sync

Logged: 2026-06-28 EDT

Planned file changes (pre-fix):
- `harness/plugins/autosci/bin/autosci_bridge.py`
- `harness/plugins/autosci/tests/test_autosci_skill_shim.py`
- `harness/plugins/autosci/config/feature_parity_routes.v1.json`
- `docs/integrations/autosci/native-lifecycle-continuation-log.md`
- `docs/integrations/autosci/phase15-progress-log.md`
- `docs/integrations/autosci/phase19-progress-log.md`

Intent: add explicit `/exp-run` final runtime audit boundary requiring approved
deploy/run evidence, monitor/collect evidence, collection ledger, and wiki state
mutation proof before a run is treated as fully executed/collected.

### Experiment Run Final Runtime Audit Boundary Result

| Check | Status | Evidence |
|---|---|---|
| Final runtime audit boundary | ok | `/exp-run` run/collect paths write `autosci_experiment_run_final_runtime_audit_boundary.v1`. |
| Boundary sidecar | ok | Run/status artifacts include `experiment_run_final_runtime_audit_boundary_json`. |
| Run-only separation | ok | Approved run plus wiki mutation is `stage_runtime_audit_ready`, not final lifecycle ready. |
| Local collect separation | ok | Local result-dir collection records ledger evidence but remains non-final without live provider/SSH proof. |
| Live collect final path | ok | Approved live/provider pull-results with ledger and wiki mutation satisfies `final_runtime_audit_ready`. |
| Route limitation | ok | `/exp-run` now names final runtime audit boundary requirements. |

### Experiment Run Final Runtime Audit Boundary Verification

| Command | Result |
|---|---|
| `py_compile` bridge/tests | ok |
| route config JSON load | ok |
| exp-run runtime/local collect/live collect boundary targeted tests | ok: 3 passed |
| `-k 'exp_eval or exp_pilot_eval or exp_design or exp_run or exp_status or exp_pilot or exp_collect'` subset | ok: 24 passed |
| full shim suite with elevated local bind permission | ok: 110 passed |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step73.json` | warn: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |
| `git diff --check` over Step 73 files | ok before log write |

## Phase 19 Pilot Experiment Final Acceptance Boundary Sync

Logged: 2026-06-28 EDT

Planned file changes (pre-fix):
- `harness/plugins/autosci/bin/autosci_bridge.py`
- `harness/plugins/autosci/tests/test_autosci_skill_shim.py`
- `harness/plugins/autosci/config/feature_parity_routes.v1.json`
- `docs/integrations/autosci/native-lifecycle-continuation-log.md`
- `docs/integrations/autosci/phase15-progress-log.md`
- `docs/integrations/autosci/phase19-progress-log.md`

Intent: add explicit `/exp-pilot-run` and `/exp-pilot-eval` final pilot
acceptance boundaries requiring approved pilot runtime evidence, collected pilot
result evidence, verdict linkage, and approved wiki writeback status before pilot
success/evaluation is treated as final.

### Pilot Experiment Final Acceptance Boundary Result

| Check | Status | Evidence |
|---|---|---|
| Pilot run boundary | ok | `/exp-pilot-run` writes `autosci_pilot_experiment_final_acceptance_boundary.v1` with `stage=pilot_run`. |
| Pilot eval boundary | ok | `/exp-pilot-eval` writes `autosci_pilot_experiment_final_acceptance_boundary.v1` with `stage=pilot_eval`. |
| Runtime/final separation | ok | Pilot runtime readiness is separate from final pilot acceptance. |
| Final-ready path | ok | Runtime-linked verdict plus approved wiki writeback satisfies `final_pilot_acceptance_ready`. |
| Route limitation | ok | Pilot run/eval limitations now name final acceptance boundary requirements. |

### Pilot Experiment Final Acceptance Boundary Verification

| Command | Result |
|---|---|
| `py_compile` bridge/tests | ok |
| route config JSON load | ok |
| pilot runtime/eval/writeback boundary targeted tests | ok: 3 passed |
| `-k 'exp_pilot or pilot_eval or pilot_run or exp_eval or exp_run or exp_status or exp_design'` subset | ok: 21 passed |
| full shim suite with elevated local bind permission | ok: 110 passed |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step74.json` | warn: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |
| `git diff --check` over Step 74 files | ok before log write |

## Phase 19 Daily Arxiv Final Provider Delivery Boundary Sync

Logged: 2026-06-28 EDT

Planned file changes (pre-fix):
- `harness/plugins/autosci/bin/autosci_bridge.py`
- `harness/plugins/autosci/tests/test_autosci_skill_shim.py`
- `harness/plugins/autosci/config/feature_parity_routes.v1.json`
- `docs/integrations/autosci/native-lifecycle-continuation-log.md`
- `docs/integrations/autosci/phase15-progress-log.md`
- `docs/integrations/autosci/phase19-progress-log.md`

Intent: add explicit `/daily-arxiv` final provider/delivery boundary requiring
approved live provider runtime, source-channel candidate evidence,
ranking/finalize evidence, and explicit delivery or ingest status before a daily
digest is treated as final.

### Daily Arxiv Final Provider Delivery Boundary Result

| Check | Status | Evidence |
|---|---|---|
| Final provider/delivery boundary | ok | `/daily-arxiv` writes `autosci_daily_arxiv_final_provider_delivery_boundary.v1`. |
| Boundary sidecar | ok | Daily artifacts include `daily_arxiv_final_provider_delivery_boundary_json`. |
| Runtime/final separation | ok | Runtime provider/ranking evidence is stage-ready but non-final without delivery/ingest. |
| Final-ready path | ok | Approved wiki fan-in/ingest after provider candidates satisfies `daily_final_delivery_ready`. |
| Route limitation | ok | `/daily-arxiv` now names provider, ranking, delivery/ingest boundary requirements. |

### Daily Arxiv Final Provider Delivery Boundary Verification

| Command | Result |
|---|---|
| `py_compile` bridge/tests | ok |
| route config JSON load | ok |
| daily runtime digest and auto-ingest boundary targeted tests | ok: 2 passed |
| `-k 'daily_arxiv or discover or init_sources or source_fan_in or ingest'` subset | ok: 10 passed |
| full shim suite with elevated local bind permission | ok: 110 passed |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step75.json` | warn: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |
| `git diff --check` over Step 75 files | ok before log write |

## Phase 19 Init Sources Final Fan-In Boundary Sync

Logged: 2026-06-28 EDT

Planned file changes (pre-fix):
- `harness/plugins/autosci/bin/autosci_bridge.py`
- `harness/plugins/autosci/tests/test_autosci_skill_shim.py`
- `harness/plugins/autosci/config/feature_parity_routes.v1.json`
- `docs/integrations/autosci/native-lifecycle-continuation-log.md`
- `docs/integrations/autosci/phase15-progress-log.md`
- `docs/integrations/autosci/phase19-progress-log.md`

Intent: add explicit `/init` source initialization final fan-in boundary
requiring approved provider runtime, provider-backed candidates, approved wiki
fan-in, graph/log/index rebuild evidence, and visible incomplete status when any
piece is missing.

### Init Sources Final Fan-In Boundary Result

| Check | Status | Evidence |
|---|---|---|
| Init final fan-in boundary | ok | `/init` writes `autosci_init_sources_final_fan_in_boundary.v1`. |
| Boundary sidecar | ok | Init artifacts include `init_sources_final_fan_in_boundary_json`. |
| Runtime/final separation | ok | Provider runtime source evidence is provider-ready but non-final without approved fan-in. |
| Final-ready path | ok | Approved wiki fan-in plus log/edge/index/context rebuild satisfies `init_sources_final_fan_in_ready`. |
| Route limitation | ok | `/init` now names final fan-in boundary requirements and approval-required side effects. |

### Init Sources Final Fan-In Boundary Verification

| Command | Result |
|---|---|
| `py_compile` bridge/tests | ok |
| route config JSON load | ok |
| init diagnostics/runtime-only/approved fan-in targeted tests | ok: 3 passed |
| `-k 'init or daily_arxiv or discover or source_fan_in or ingest'` subset | ok: 13 passed |
| full shim suite with elevated local bind permission | ok: 110 passed |
| `env PYTHONPATH=harness .venv/bin/python harness/plugins/autosci/bin/autosci_parity_bridge.py inventory --out /tmp/autosci-parity-step76.json` | warn: 28 routed, 0 missing, 0 full, 17 partial, 11 gated |
| `git diff --check` over Step 76 files | ok before log write |

## Phase 19 Ingest Final Source Registration Boundary Sync

Logged: 2026-06-28 EDT

Planned file changes (pre-fix):
- `harness/plugins/autosci/bin/autosci_bridge.py`
- `harness/plugins/autosci/tests/test_autosci_skill_shim.py`
- `harness/plugins/autosci/config/feature_parity_routes.v1.json`
- `docs/integrations/autosci/native-lifecycle-continuation-log.md`
- `docs/integrations/autosci/phase15-progress-log.md`
- `docs/integrations/autosci/phase19-progress-log.md`

Intent: add explicit `/ingest` final source registration boundary requiring
verified source preparation, parsed paper metadata/text, raw artifact provenance,
wiki paper registration/log/graph evidence, and downstream discovery handoff
before an ingest is treated as final.

Plan refinement: include `autosci_skill_shim.py` so `/ingest --wiki-root`
propagates into bridge inputs and the boundary checks the intended wiki root.

### Ingest Final Source Registration Boundary Result

| Check | Status | Evidence |
|---|---|---|
| Final source registration boundary | ok | `/ingest` writes `autosci_ingest_final_source_registration_boundary.v1`. |
| Boundary sidecar | ok | Ingest artifacts include final boundary plus phase9 memory/graph sidecars. |
| Custom wiki root | ok | `/ingest --wiki-root` propagates into bridge inputs. |
| Runtime/final separation | ok | Parsed source without wiki paper/log/graph/index/context registration remains non-final. |
| Final-ready path | ok | Pre-registered wiki evidence satisfies `ingest_source_registration_ready`. |
| Targeted/subset tests | ok | Targeted ingest tests: 2 passed; source/ingest subset: 14 passed. |
| Full suite | warn | Full shim suite: 105 passed, 6 failed because scheduler AutoSci worker entries are missing from `physical-operators.json`. |

## Phase 19 Scheduler AutoSci Worker Registry Restore Sync

Logged: 2026-06-28 EDT

Planned file changes (pre-fix):
- `harness/config/physical-operators.json`
- `docs/integrations/autosci/native-lifecycle-continuation-log.md`
- `docs/integrations/autosci/phase15-progress-log.md`
- `docs/integrations/autosci/phase19-progress-log.md`

Intent: restore bounded AutoSci worker entries required by scheduler lifecycle
smoke so `$research --scheduler-run` can dispatch configured AutoSci bridge
actions through `operator_runtime`.

### Scheduler AutoSci Worker Registry Restore Result

| Check | Status | Evidence |
|---|---|---|
| Physical workers | ok | `physical-operators.json` now has scheduler-referenced `autosci-*` bounded command workers. |
| Scheduler regression group | ok | `$research --scheduler-run` group: 6 passed. |
| Full shim suite | ok | Full AutoSci shim suite: 111 passed. |
| Static binding audit | warn | Next blocker is missing Scientific* logical operators/bindings in `logical-operators.json`. |

## Phase 19 Scientific Logical Operator Binding Restore Sync

Logged: 2026-06-28 EDT

Planned file changes (pre-fix):
- `harness/config/logical-operators.json`
- `docs/integrations/autosci/native-lifecycle-continuation-log.md`
- `docs/integrations/autosci/phase15-progress-log.md`
- `docs/integrations/autosci/phase19-progress-log.md`

Intent: restore Scientific* logical operators and bindings to the bounded
AutoSci workers so static runtime binding audit can validate workflow
node-to-operator-to-bridge coverage.

### Scientific Logical Operator Binding Restore Result

| Check | Status | Evidence |
|---|---|---|
| Logical operators/bindings | ok | Scientific* definitions and bounded worker bindings restored. |
| Static runtime binding audit | ok | 28 workflow nodes across 2 workflows, 0 issues. |
| Scheduler/full shim regression | ok | Scheduler group: 6 passed; full shim suite: 111 passed. |
| Inventory | warn | Route inventory remains 17 partial and 11 gated. |

## Phase 19 Two-Axis Parity Status Model Sync

Logged: 2026-06-28 EDT

Planned file changes (pre-fix):
- `harness/plugins/autosci/bin/autosci_parity_bridge.py`
- `harness/evaluators/scientific/autosci_feature_parity_gate.py`
- `harness/plugins/autosci/tests/test_phase19_parity_bridge.py`
- `harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py`
- `docs/integrations/autosci/native-lifecycle-continuation-log.md`
- `docs/integrations/autosci/phase15-progress-log.md`
- `docs/integrations/autosci/phase19-progress-log.md`

Intent: add authoritative two-axis parity/proof fields to generated inventory
and gate validation without upgrading any route to semantic full absent E3/E4
evidence.

### Two-Axis Parity Status Model Result

| Check | Status | Evidence |
|---|---|---|
| Inventory fields | ok | Parity inventory route items now expose `semantic_parity`, `execution_policy`, `proof_level`, `proof_refs`, and `remaining_requirements`. |
| Gate enforcement | ok | `autosci_feature_parity_gate.py` validates semantic/execution/proof values and rejects semantic-full claims without enough proof. |
| Truthfulness guard | ok | No route was promoted to semantic full; Step 80 inventory remains semantic partial for all 28 routes. |
| Tests | ok | Parity bridge/gate targeted tests: 10 passed; full AutoSci plugin suite: 161 passed. |
| Inventory | warn | `/tmp/autosci-parity-step80.json`: route coverage 0 full / 17 partial / 11 gated; semantic 0 full / 28 partial / 0 missing. |

## Phase 19 Skill Run Terminal Status Truthfulness Gate Sync

Logged: 2026-06-29 EDT

Planned file changes (pre-fix):
- `harness/evaluators/scientific/autosci_skill_run_gate.py`
- `harness/tests/evaluators/scientific/test_autosci_skill_run_gate.py`
- `docs/integrations/autosci/native-lifecycle-continuation-log.md`
- `docs/integrations/autosci/phase15-progress-log.md`
- `docs/integrations/autosci/phase19-progress-log.md`

Intent: make the skill-run gate reject evidence that claims top-level
`status: completed` while `outputs.skill_run.execution_status` is `partial` or
`gated`.

Non-goal: do not change route execution, side-effect policy, schema enums, or
the shim's existing `inconclusive` status for partial/gated runs.

### Skill Run Terminal Status Truthfulness Gate Result

| Check | Status | Evidence |
|---|---|---|
| Gate guard | ok | `autosci_skill_run_gate.py` rejects top-level `completed` for `partial`/`gated` execution status. |
| Tests | ok | New skill-run gate tests: 3 passed; gated/partial shim subsets and operator smoke gate remain green. |
| Full plugin suite | ok | Elevated local-bind AutoSci plugin suite: 161 passed. |
| Inventory | warn | Step 81 parity inventory remains 17 partial and 11 gated; semantic inventory remains 28 partial. |
| Broad evaluator suite | warn | Scientific evaluator suite exposed next blocker: full lifecycle external/resume tails drift from the 20-node workflow config. |

## Phase 19 Scheduler Full Lifecycle Tail Alignment Sync

Logged: 2026-06-29 EDT

Planned file changes (pre-fix):
- `harness/plugins/autosci/bin/autosci_bridge.py`
- `harness/tools/run_scientific_lifecycle_smoke.py`
- `docs/integrations/autosci/native-lifecycle-continuation-log.md`
- `docs/integrations/autosci/phase15-progress-log.md`
- `docs/integrations/autosci/phase19-progress-log.md`

Intent: make full external/resume lifecycle smoke paths dispatch the configured
publication/finalization tail and treat an explicitly supplied compile-target
PDF as handoff evidence without claiming approved executor runtime.

Non-goal: do not make bounded smoke dispatch production-ready, execute
unapproved TeX/remote effects, or relax lifecycle runtime gate requirements.

### Scheduler Tail Alignment Adjustment Plan

Logged: 2026-06-29 EDT

Planned file changes (pre-fix):
- `harness/plugins/autosci/bin/autosci_bridge.py`
- `harness/tools/run_scientific_lifecycle_smoke.py`
- `docs/integrations/autosci/native-lifecycle-continuation-log.md`
- `docs/integrations/autosci/phase15-progress-log.md`
- `docs/integrations/autosci/phase19-progress-log.md`

Intent: keep the Step 82 boundary and wire supplied compile-target evidence
into paper-plan handoff readiness so configured tail dispatch can proceed only
after verified handoff.

Non-goal: do not change test expectations, production readiness claims, TeX
execution policy, or unrelated scheduler nodes.

### Scheduler Resume Blocker Adjustment Plan

Logged: 2026-06-29 EDT

Planned file changes (pre-fix):
- `harness/tools/run_scientific_lifecycle_smoke.py`
- `docs/integrations/autosci/native-lifecycle-continuation-log.md`
- `docs/integrations/autosci/phase15-progress-log.md`
- `docs/integrations/autosci/phase19-progress-log.md`

Intent: preserve all unresolved external unblock points during resume when
earlier external evidence is missing, without dispatching downstream configured
tail nodes.

Non-goal: do not change human-gate behavior, node execution order, or
publication/finalization dispatch semantics.

### Scheduler Full Lifecycle Tail Alignment Result

| Check | Status | Evidence |
|---|---|---|
| Supplied compile handoff | ok | `plan_report` now treats `supplied_compile_target_evidence` as a compile handoff request and verifies existing PDF targets without claiming TeX execution. |
| Full external tail | ok | Full external lifecycle dispatch reaches all configured tail nodes when Review LLM and compile-target evidence are supplied. |
| Resume tail | ok | Resume dispatch reaches configured tail nodes after supplied external evidence and preserves no-rerun fingerprints. |
| Resume blocked externals | ok | Human-gate resume with no external evidence records both `report_plan` and `publication_produce` blockers. |
| Focused lifecycle tests | ok | 3 targeted lifecycle regressions passed. |
| Broad evaluator suite | ok | Scientific evaluator suite: 91 passed. |
| Full plugin suite | ok | AutoSci plugin suite with elevated local bind permission: 161 passed. |
| Inventory/gate | warn | Step 82 inventory still reports 17 partial and 11 gated route statuses; semantic parity remains 28 partial. |

## Phase 19 External Runtime Proof Registry Sync

Logged: 2026-06-29 EDT

Planned file changes (pre-fix):
- `harness/plugins/autosci/bin/autosci_parity_bridge.py`
- `harness/evaluators/scientific/autosci_feature_parity_gate.py`
- `harness/plugins/autosci/tests/test_phase19_parity_bridge.py`
- `harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py`
- `docs/integrations/autosci/native-lifecycle-continuation-log.md`
- `docs/integrations/autosci/phase15-progress-log.md`
- `docs/integrations/autosci/phase19-progress-log.md`

Intent: add explicit external runtime proof references and required proof
categories to parity inventory/gate output so remaining non-full routes are
auditable.

Non-goal: do not mark any route full, fabricate provider/runtime evidence, or
execute external side effects.

### External Runtime Proof Registry Result

| Check | Status | Evidence |
|---|---|---|
| Inventory fields | ok | Route items now include `runtime_proof_status`, `runtime_proof_refs`, and `proof_requirements`. |
| Gate enforcement | ok | Gate validates requirement shape/status, runtime proof status/counts, and approval/provider proof-category presence. |
| Tests | ok | Parity bridge tests: 4 passed; feature parity gate tests: 8 passed; scientific evaluator suite: 93 passed. |
| Full plugin suite | ok | AutoSci plugin suite with elevated local bind permission: 161 passed. |
| Inventory | warn | Step 83 inventory reports 25 pending runtime proof slots and 0 supplied/verified runtime proofs. |

## Phase 19 Runtime Proof Manifest Ingestion Sync

Logged: 2026-06-29 EDT

Planned file changes (pre-fix):
- `harness/plugins/autosci/bin/autosci_parity_bridge.py`
- `harness/evaluators/scientific/autosci_feature_parity_gate.py`
- `harness/plugins/autosci/tests/test_phase19_parity_bridge.py`
- `harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py`
- `docs/integrations/autosci/native-lifecycle-continuation-log.md`
- `docs/integrations/autosci/phase15-progress-log.md`
- `docs/integrations/autosci/phase19-progress-log.md`

Intent: allow parity inventory to ingest explicit runtime proof manifests and
mark matching route proof slots as supplied without promoting route/semantic
full status.

Non-goal: do not trust arbitrary manifests as verified runtime, mark routes
full, execute providers, or execute side effects.

### Runtime Proof Manifest Strictness Adjustment Plan

Logged: 2026-06-29 EDT

Planned file changes (pre-fix):
- `harness/evaluators/scientific/autosci_feature_parity_gate.py`
- `harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py`
- `docs/integrations/autosci/native-lifecycle-continuation-log.md`
- `docs/integrations/autosci/phase15-progress-log.md`
- `docs/integrations/autosci/phase19-progress-log.md`

Intent: require supplied runtime proof source categories to match declared proof
requirements and actually satisfy at least one requirement.

Non-goal: do not change manifest ingestion semantics, route statuses, or proof
verification level.

### Runtime Proof Manifest Ingestion Result

| Check | Status | Evidence |
|---|---|---|
| CLI ingestion | ok | `inventory` and `route` accept repeated `--runtime-proof-manifest` paths. |
| Proof attachment | ok | Manifest proofs attach to matching native skills as `runtime_proof_sources` and supplied proof requirements. |
| Gate strictness | ok | Gate rejects skill mismatch, unknown categories, supplied-without-supplied-requirement, and count drift. |
| Tests | ok | Targeted bridge/gate group: 15 passed; scientific evaluator suite: 95 passed. |
| Full plugin suite | ok | AutoSci plugin suite with elevated local bind permission: 162 passed. |
| Inventory | warn | No-manifest Step 84 inventory still has 25 pending runtime proof slots and no supplied/verified proof. |

## Phase 19 Runtime Proof Evidence Ref Audit Sync

Logged: 2026-06-29 EDT

Planned file changes (pre-fix):
- `harness/plugins/autosci/bin/autosci_parity_bridge.py`
- `harness/evaluators/scientific/autosci_feature_parity_gate.py`
- `harness/plugins/autosci/tests/test_phase19_parity_bridge.py`
- `harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py`
- `docs/integrations/autosci/native-lifecycle-continuation-log.md`
- `docs/integrations/autosci/phase15-progress-log.md`
- `docs/integrations/autosci/phase19-progress-log.md`

Intent: audit runtime proof evidence refs so path-like local refs must resolve
and missing local refs cannot satisfy supplied proof requirements.

Non-goal: do not verify external provider ids as live, promote supplied proof
to verified, or execute external side effects.

### Runtime Proof Evidence Ref Audit Result

| Check | Status | Evidence |
|---|---|---|
| Ref audit | ok | Manifest proof sources now include `evidence_ref_statuses`; local path refs must resolve. |
| Blocked proof handling | ok | Missing local proof refs produce blocked proof sources and do not satisfy supplied requirements. |
| Gate enforcement | ok | Gate rejects blocked sources and unresolved local refs. |
| Tests | ok | Phase19 bridge tests: 6 passed; feature parity gate tests: 10 passed; scientific evaluator suite: 95 passed. |
| Full plugin suite | ok | AutoSci plugin suite with elevated local bind permission: 163 passed. |
| Inventory | warn | Step 85 inventory remains non-full and has no verified live runtime proof. |

## Phase 19 Runtime Proof CLI Summary Visibility Sync

Logged: 2026-06-29 EDT

Planned file changes (pre-fix):
- `harness/plugins/autosci/bin/autosci_parity_bridge.py`
- `harness/plugins/autosci/tests/test_phase19_parity_bridge.py`
- `docs/integrations/autosci/native-lifecycle-continuation-log.md`
- `docs/integrations/autosci/phase15-progress-log.md`
- `docs/integrations/autosci/phase19-progress-log.md`

Intent: include runtime proof status counts in parity bridge CLI summaries so
pending/supplied/verified proof state is visible without opening the JSON
artifact.

Non-goal: do not change inventory payload semantics, gate rules, route status,
or proof verification.

### Runtime Proof CLI Summary Visibility Result

| Check | Status | Evidence |
|---|---|---|
| CLI summary | ok | Inventory/route stdout summaries now include `runtime_proof_status_counts`. |
| Tests | ok | Phase19 bridge tests: 6 passed. |
| Inventory/gate | ok | Step 86 inventory gates successfully and stdout reports 25 pending / 3 not_required / 0 supplied / 0 verified runtime proof states. |
| Full parity claim | warn | Remaining work requires real runtime proof manifests or approved live provider execution. |
