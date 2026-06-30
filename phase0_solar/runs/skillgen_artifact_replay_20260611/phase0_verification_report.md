# Solar Phase 0 Verification Report

Generated: `2026-06-11T14:27:40+00:00`
Run id: `skillgen-artifact-replay-20260611`
Mode: `artifact_replay`
Source matrix: `/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B/phase_0/runs/20260604/artifacts/all_claim_verification_matrix.json`

## Verdict

| Field | Value |
| --- | --- |
| Paper-level status | `not_reproduced` |
| Full-paper claim status | `blocked` |
| Claims | 12 |
| Executable targets in source matrix | 7 |

## Claim Status Counts

| Status | Count |
| --- | ---: |
| `blocked` | 7 |
| `not_reproduced` | 2 |
| `partially_reproduced` | 3 |

## Readiness Summary

| Status | Count |
| --- | ---: |
| `blocked` | 1 |
| `partially_ready` | 2 |
| `ready` | 9 |

## Claim Matrix

| Claim | Verdict | Readiness | Evidence | Blockers |
| --- | --- | --- | ---: | ---: |
| `claim_method_paired_intervention` | `partially_reproduced` | `ready_for_full_matrix_execution_after_dependencies` | 1 | 0 |
| `claim_table1_average_gains_all_models` | `blocked` | `partially_ready_full_matrix` | 0 | 3 |
| `claim_table1_entry_counts` | `blocked` | `partially_ready_full_matrix` | 0 | 3 |
| `claim_table1_alfworld_scienceworld_patterns` | `blocked` | `ready_for_reconstructed_alfworld_implementation` | 0 | 1 |
| `claim_baseline_generator_comparison` | `blocked` | `ready_for_reconstructed_baseline_comparison` | 0 | 1 |
| `claim_ablation_full_wins` | `blocked` | `ready_for_reconstructed_ablation_human_review` | 0 | 1 |
| `claim_cross_model_transfer` | `blocked` | `blocked_by_alfworld_ood_execution` | 0 | 1 |
| `claim_tau_bench_gate_activated` | `not_reproduced` | `ready_for_execution` | 2 | 1 |
| `claim_chemllmbench_useful_gains` | `not_reproduced` | `ready_for_execution` | 2 | 1 |
| `claim_refinement_best_of_k` | `blocked` | `ready_for_trace_generation_after_full_runs` | 0 | 2 |
| `claim_token_cost` | `partially_reproduced` | `ready_for_full_token_cost_execution` | 9 | 1 |
| `claim_auditable_skill_artifact` | `partially_reproduced` | `ready_for_full_scope_artifact_check` | 1 | 0 |

## Issue Notes

### `claim_method_paired_intervention`

Next step: Promote from smoke evidence to full-paper evidence only if the matching full contract is executed.

### `claim_table1_average_gains_all_models`

Blockers:
- Full Table 1 requires 80 benchmark-split-model entries, not only the AIME smoke target.
- Rows not yet Table 1 execution-ready: alfworld_iod (ready_for_reconstructed_execution), alfworld_ood (ready_for_reconstructed_execution).
- ALFWorld reconstructed rows still require canonical data download, adapter implementation, generated train/test JSON, smoke logs, and human approval before Table 1 execution.

Next step: Resolve structurally non-ready Table 1 rows (alfworld_iod, alfworld_ood), then aggregate the full Table 1 matrix.

### `claim_table1_entry_counts`

Blockers:
- Full Table 1 requires 80 benchmark-split-model entries, not only the AIME smoke target.
- Rows not yet Table 1 execution-ready: alfworld_iod (ready_for_reconstructed_execution), alfworld_ood (ready_for_reconstructed_execution).
- ALFWorld reconstructed rows still require canonical data download, adapter implementation, generated train/test JSON, smoke logs, and human approval before Table 1 execution.

Next step: Resolve structurally non-ready Table 1 rows (alfworld_iod, alfworld_ood), then aggregate the full Table 1 matrix.

### `claim_table1_alfworld_scienceworld_patterns`

Blockers:
- ALFWorld IOD/OOD still need canonical data download, adapter implementation, generated split files, smoke logs, and human approval before result comparison.

Next step: Resolve the remaining structural missing contract or artifact, then execute the relevant benchmark plan.

### `claim_baseline_generator_comparison`

Blockers:
- Reconstructed Figure 2 baseline comparison has not been executed yet.

Next step: Execute baseline_single_skill_adapter_contract.json with the shared paired rollout harness, then aggregate Figure 2 deltas.

### `claim_ablation_full_wins`

Blockers:
- Reconstructed ablation smoke execution has not been run or parsed yet.

Next step: Human-review reconstructed_ablation_contract.json, ablation_config_matrix.json, and ablation_deviation_note.md, then execute ablation_smoke_plan.json before any paper-target Figure 3 matrix.

### `claim_cross_model_transfer`

Blockers:
- Full 120-comparison transfer claim still requires executing the ALFWorld OOD reconstructed contract, including data download, adapter implementation, generated split files, and retained per-round traces.

Next step: Execute the approved ALFWorld OOD reconstructed contract first (data download, adapter implementation, split JSONs, trace retention), then run transfer_runner_plan.json.

### `claim_tau_bench_gate_activated`

Blockers:
- Executed tau-Bench smoke did not support the paper claim: the generated skill failed the internal verification gate or produced no positive held-out skill delta.

Next step: Inspect the raw execution logs and rerun at full paper scale only if the smoke scope is considered insufficient; the current executed smoke evidence does not support the claim.

### `claim_chemllmbench_useful_gains`

Blockers:
- Executed ChemLLMBench smoke targets did not show positive skill gains for all prepared subtasks.

Next step: Inspect the raw execution logs and rerun at full paper scale only if the smoke scope is considered insufficient; the current executed smoke evidence does not support the claim.

### `claim_refinement_best_of_k`

Blockers:
- Official pipeline records refinement outputs for executed runs, but the paper's aggregate Figure 7 traces are not bundled.
- Needs full per-round run logs across representative benchmark-model entries.

Next step: Resolve the remaining structural missing contract or artifact, then execute the relevant benchmark plan.

### `claim_token_cost`

Blockers:
- The run uses reduced POC-scale configs, so token-log mechanics are reproduced but the paper's full-scale token totals are not.

Next step: Promote the reduced POC token-log executions to full paper-scale Table 4 runs only if exact numeric token-cost reproduction is required.

### `claim_auditable_skill_artifact`

Next step: Promote from smoke evidence to full-paper evidence only if the matching full contract is executed.

## Solar Interpretation

- Claim verdicts and execution readiness remain separate.
- Readiness/planning evidence does not upgrade a claim verdict.
- Negative executed evidence remains `not_reproduced`.
- This run produced a report from recorded artifacts and did not execute live benchmark jobs.
- Machine-readable summary: `phase0_solar/runs/skillgen_artifact_replay_20260611/phase0_verification_summary.json`
