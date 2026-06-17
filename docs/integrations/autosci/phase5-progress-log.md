# AutoSci Phase 5 Progress Log

Logged: 2026-06-17 14:51:59 EDT
Branch: `feature/autosci-solar-native`

## Scope

Phase 5 registered AutoSci backend workers as Solar physical operators and bound
the Phase 3 `Scientific*` logical operators to those workers.

This phase does not add TaskGraph templates, evaluator gates, memory mutation,
ideation logic, or any AutoSci-owned end-to-end workflow runner. Solar remains
the workflow authority and only dispatches bounded backend actions through the
Phase 4 bridge.

## Files Changed

| Path or artifact | Operation | Commit | Note |
|---|---|---|---|
| `harness/config/physical-operators.json` | Modified | this phase commit | Added 8 AutoSci command-backend physical operators. |
| `harness/config/logical-operators.json` | Modified | this phase commit | Added 11 `Scientific*` logical-to-physical bindings. |
| `harness/artifacts/autosci/smoke/envelope.claim_extract.json` | Added | this phase commit | Human-testable submit envelope for claim extraction dispatch. |
| `docs/integrations/autosci/phase5-progress-log.md` | Added | this phase commit | This audit log for Phase 5. |

## Physical Operators

| Physical operator | Bridge action | Status | Logical coverage |
|---|---|---|---|
| `autosci-paper-ingest-worker` | `ingest_paper` | ok | `ScientificPaperIngestor` |
| `autosci-claim-extract-worker` | `extract_claims` | ok | `ScientificClaimExtractor` |
| `autosci-memory-update-worker` | `update_memory` | pending | `ScientificMemoryUpdater` |
| `autosci-idea-worker` | `generate_ideas` | pending | `ScientificIdeaGenerator`, `ScientificIdeaEvaluator` |
| `autosci-experiment-design-worker` | `design_experiment` | ok | `ScientificExperimentDesigner` |
| `autosci-experiment-run-worker` | `run_experiment` | ok | `ScientificExperimentRunner` |
| `autosci-claim-verify-worker` | `verify_claim` | ok | `ScientificClaimVerifier` |
| `autosci-report-worker` | `write_report` | ok | `ScientificReportPlanner`, `ScientificReportDrafter`, `ScientificPublicationProducer` |

## Binding Policy

| Area | Policy |
|---|---|
| Enabled backends | Use command backend through `plugins/autosci/bin/autosci_bridge.py run --action ... --envelope "$SOLAR_OPERATOR_ENVELOPE_JSON"`. |
| Pending backends | Memory update and idea generation/evaluation are registered but disabled until their later planned phases. |
| Capability names | Physical preferences use `cap.research-*`; no `cap.scientific-*` tokens were added. |
| Workflow ownership | No `AutoSciRunner` logical operator or binding was added. |
| Network | AutoSci physical operators are configured with `network: denied`. |
| Writes | Operator policy limits writes to artifact output scope. |

## Checks Run

| Check | Status | Note |
|---|---|---|
| Solar context injection | ok with warning | Used repo-local `HARNESS_DIR=<OpenSolar>/harness bash solar-harness.sh context inject`; Mirage source was degraded. |
| Physical operator JSON parse | ok | `python3 -m json.tool harness/config/physical-operators.json` passed. |
| Logical operator JSON parse | ok | `python3 -m json.tool harness/config/logical-operators.json` passed. |
| Smoke envelope JSON parse | ok | `python3 -m json.tool harness/artifacts/autosci/smoke/envelope.claim_extract.json` passed. |
| Operator registry verification | ok | Script confirmed all 8 AutoSci physical operators, command backend wiring, disabled pending workers, network policy, and `cap.research-*` preferences. |
| Logical binding verification | ok | Script confirmed 11 expected `Scientific*` bindings and no `AutoSciRunner` binding. |
| Dispatch smoke | ok | `operator_runtime.submit()` dispatched `autosci-claim-extract-worker`; operatord completed with exit code 0. |
| Bridge result validation | ok | `python3 plugins/autosci/bin/autosci_bridge.py validate --result artifacts/autosci/smoke/claim_extract_dispatch/result.json` returned `ok: true`. |

## Dispatch Smoke Evidence

| Field | Value |
|---|---|
| Envelope | `harness/artifacts/autosci/smoke/envelope.claim_extract.json` |
| Operator | `autosci-claim-extract-worker` |
| Task | `task-autosci-phase5-claim-extract-smoke` |
| Result status | `completed` |
| Bridge result | `harness/artifacts/autosci/smoke/claim_extract_dispatch/result.json` |

## Notes

- Generated smoke outputs under
  `harness/artifacts/autosci/smoke/claim_extract_dispatch/*` were produced for
  local verification and are not intended as part of the Phase 5 commit.
- `autosci-memory-update-worker` is intentionally disabled because the bridge
  action is planned for Phase 9; enabling it now would create a fake memory path.
- `autosci-idea-worker` is intentionally disabled because idea generation and
  evaluation are planned for Phase 11; enabling it now would create fake
  ideation.
- Existing unrelated dirty files were left untouched.

## Done State

Phase 5 is complete when Solar can map native `Scientific*` logical operators to
bounded AutoSci physical workers, submit at least one fixture-backed worker
through the normal operator runtime, validate the resulting Evidence ABI output,
and still has no hidden AutoSci-owned full workflow runner.
