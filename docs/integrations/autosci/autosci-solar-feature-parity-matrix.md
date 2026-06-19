# AutoSci Solar Feature Parity Matrix

Logged: 2026-06-19
Phase: 19

## Result

Solar now has an explicit route for every native AutoSci English skill found in
the local `AutoSci/i18n/en/skills/*/SKILL.md` checkout. This is route parity,
not a claim that every external side effect has run in this session.

```text
TaskGraph node
  -> Solar logical operator
  -> Solar capability capsule
  -> AutoSci plugin backend action
  -> Evidence ABI
  -> deterministic gate / explicit limitation
```

## Inventory Snapshot

| Metric | Value |
|---|---:|
| Native AutoSci skills scanned | 28 |
| Solar routes configured | 28 |
| Missing routes | 0 |
| Full route coverage | 7 |
| Partial route coverage | 11 |
| Approval-gated route coverage | 10 |
| Blocked routes | 0 |

Evidence:

- Route config: `harness/plugins/autosci/config/feature_parity_routes.v1.json`
- Bridge: `harness/plugins/autosci/bin/autosci_parity_bridge.py`
- Evidence ABI: `harness/schemas/evidence/autosci_feature_parity.v1.schema.json`
- Gate: `harness/evaluators/scientific/autosci_feature_parity_gate.py`
- Local evidence: `harness/artifacts/autosci/phase19/parity_inventory.json`

## Coverage Semantics

| Status | Meaning |
|---|---|
| `full` | Existing Solar route covers the native AutoSci skill's core non-destructive behavior through typed evidence. |
| `partial` | Solar has a native route, but some behavior still depends on model output, source availability, or downstream artifacts. |
| `gated` | Solar has a native route, but live side effects require explicit approval and runtime evidence. |
| `missing` | No Solar route exists; Phase 19 gate fails if this appears. |

## Skill Matrix

| AutoSci skill | Solar capability | Logical operator | Backend action | Evidence ABI | Status | Side effect policy |
|---|---|---|---|---|---|---|
| `/ask` | `cap.research-memory-update` | `ScientificMemoryUpdater` | `ask_wiki` | `research_memory_update.v1` | `partial` | `none` |
| `/check` | `cap.research-workflow-evolve` | `ScientificWorkflowEvolver` | `check_wiki_health` | `workflow_evolution.v1` | `partial` | `none` |
| `/daily-arxiv` | `cap.research-literature-discover` | `ScientificLiteratureDiscoverer` | `daily_arxiv_prepare_finalize` | `literature_discovery.v1` | `gated` | `approval_required` |
| `/discover` | `cap.research-literature-discover` | `ScientificLiteratureDiscoverer` | `discover_literature` | `literature_discovery.v1` | `full` | `none` |
| `/edit` | `cap.research-memory-update` | `ScientificMemoryUpdater` | `edit_wiki_plan` | `research_memory_update.v1` | `gated` | `approval_required` |
| `/exp-design` | `cap.research-experiment-design` | `ScientificExperimentDesigner` | `design_experiment` | `experiment_plan.v1` | `full` | `none` |
| `/exp-eval` | `cap.research-claim-verify` | `ScientificClaimVerifier` | `verify_claim` | `claim_verdict.v1` | `partial` | `dry_run_only` |
| `/exp-pilot-eval` | `cap.research-claim-verify` | `ScientificClaimVerifier` | `evaluate_pilot_result` | `claim_verdict.v1` | `partial` | `dry_run_only` |
| `/exp-pilot-run` | `cap.research-experiment-run` | `ScientificExperimentRunner` | `run_pilot_experiment` | `experiment_result.v1` | `gated` | `approval_required` |
| `/exp-run` | `cap.research-experiment-run` | `ScientificExperimentRunner` | `run_experiment` | `experiment_result.v1` | `gated` | `approval_required` |
| `/exp-status` | `cap.research-experiment-monitor` | `ScientificExperimentMonitor` | `monitor_experiment` | `experiment_status.v1` | `full` | `none` |
| `/ideate` | `cap.research-idea-generate` | `ScientificIdeaGenerator` | `generate_ideas` | `idea_candidate.v1` | `full` | `dry_run_only` |
| `/ingest` | `cap.research-paper-ingest` | `ScientificPaperIngestor` | `ingest_paper` | `research_paper.v1` | `full` | `dry_run_only` |
| `/init` | `cap.research-literature-discover` | `ScientificLiteratureDiscoverer` | `init_sources` | `literature_discovery.v1` | `partial` | `dry_run_only` |
| `/novelty` | `cap.research-idea-evaluate` | `ScientificIdeaEvaluator` | `evaluate_ideas` | `idea_evaluation.v1` | `partial` | `dry_run_only` |
| `/paper-compile` | `cap.research-publication-produce` | `ScientificPublicationProducer` | `compile_paper` | `publication_bundle.v1` | `gated` | `approval_required` |
| `/paper-draft` | `cap.research-report-draft` | `ScientificReportDrafter` | `write_report` | `scientific_report.v1` | `full` | `dry_run_only` |
| `/paper-plan` | `cap.research-report-plan` | `ScientificReportPlanner` | `plan_report` | `scientific_report.v1` | `full` | `dry_run_only` |
| `/poster` | `cap.research-publication-produce` | `ScientificPublicationProducer` | `build_poster` | `publication_bundle.v1` | `gated` | `approval_required` |
| `/prefill` | `cap.research-memory-update` | `ScientificMemoryUpdater` | `prefill_foundations` | `research_memory_update.v1` | `partial` | `dry_run_only` |
| `/rebuttal` | `cap.research-publication-produce` | `ScientificPublicationProducer` | `draft_rebuttal` | `publication_bundle.v1` | `partial` | `dry_run_only` |
| `/refine` | `cap.research-workflow-evolve` | `ScientificWorkflowEvolver` | `refine_artifact` | `workflow_evolution.v1` | `gated` | `approval_required` |
| `/research` | `cap.research-workflow-evolve` | `ScientificWorkflowEvolver` | `run_research_lifecycle` | `workflow_evolution.v1` | `partial` | `approval_required` |
| `/reset` | `cap.research-workflow-evolve` | `ScientificWorkflowEvolver` | `reset_plan` | `workflow_evolution.v1` | `gated` | `approval_required` |
| `/review` | `cap.research-claim-verify` | `ScientificClaimVerifier` | `review_artifact` | `claim_verdict.v1` | `partial` | `dry_run_only` |
| `/setup` | `cap.research-workflow-evolve` | `ScientificWorkflowEvolver` | `setup_status` | `workflow_evolution.v1` | `gated` | `approval_required` |
| `/survey` | `cap.research-report-plan` | `ScientificReportPlanner` | `write_survey` | `scientific_report.v1` | `partial` | `dry_run_only` |
| `/visualize` | `cap.research-graph-update` | `ScientificGraphUpdater` | `visualize_graph` | `research_graph_update.v1` | `gated` | `approval_required` |

## Remaining Non-Full Surfaces

These are no longer missing routes, but they are intentionally not claimed as
fully executed without live evidence:

- External knowledge/API sources: arXiv, Semantic Scholar, DeepXiv, web search.
- Independent Review LLM / MCP review bindings.
- Remote experiment execution through SSH, rsync, and screen sessions.
- Destructive reset and user-owned wiki/raw edits.
- SMTP email delivery and GitHub Actions scheduling.
- Browser-backed poster rendering and local web UI serving.
- LaTeX compile and environment-specific publication checks.

## Verification

```bash
python3 harness/plugins/autosci/bin/autosci_parity_bridge.py inventory \
  --out artifacts/autosci/phase19/parity_inventory.json
python3 harness/evaluators/scientific/autosci_feature_parity_gate.py \
  harness/artifacts/autosci/phase19/parity_inventory.json
env PYTHONPATH=harness harness/bin/python3 -m pytest \
  harness/plugins/autosci/tests/test_phase19_parity_bridge.py \
  harness/tests/evaluators/scientific/test_autosci_feature_parity_gate.py
```

Observed result:

- Bridge inventory: `native_skill_count=28`, `routed_count=28`, `missing_route_count=0`.
- Gate: `passed` with warning that non-full routes must respect limitations.
- Tests: `6 passed`.
