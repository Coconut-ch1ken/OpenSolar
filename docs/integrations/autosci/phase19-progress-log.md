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
| Solar context injection | warn | `bash solar-harness.sh context inject ...` worked; Mirage source returned `mirage:nonzero`. |
| AutoSci capability scan | ok | Inspected local `/Users/jamesyuan/Developer/Github Repos (On Git)/AutoSci` README, skills, tools, runtime schema, remote/daily/poster docs. |
| Solar coverage scan | ok | Inspected Solar AutoSci bridge actions, capsules, schemas, evaluators, workflows, personas, templates. |
| Parity finding | warn | Solar covers the scientific lifecycle governance/core, but not all AutoSci `main` concrete product features yet. |
| Phase 19 implementation | pending | User interrupted before implementation edits beyond this log. |

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
| 19A parity matrix | pending | `docs/integrations/autosci/autosci-solar-feature-parity-matrix.md` |
| 19B generic AutoSci command evidence | pending | New `autosci_command_result.v1` or equivalent sidecar schema. |
| 19C bridge action expansion | pending | Add non-black-box actions for setup/reset/prefill/init/check/ask/daily/review/poster/visualize. |
| 19D operator/config binding | pending | Add Solar-native logical/physical operator bindings for concrete feature families. |
| 19E gates/tests | pending | Deterministic checks for command result, generated artifacts, unavailable side effects, and approval-gated execution. |
| 19F acceptance | pending | Run parity tests proving every AutoSci `main` skill has a Solar-native route. |

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
