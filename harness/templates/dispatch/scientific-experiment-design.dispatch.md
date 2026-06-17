# Dispatch Template: Scientific Experiment Design

Use for logical operators:
- `ScientificIdeaGenerator`
- `ScientificIdeaEvaluator`
- `ScientificExperimentDesigner`

## Task envelope

- `task_id`: `<task-id>`
- `sprint_id`: `<sprint-id>`
- `node_id`: `<node-id>`
- `operator_id`: `<physical-operator-id>`
- `task_type`: `scientific_experiment_design`

## Inputs

- Claim evidence: `<research_claims.v1 artifact>`
- Method or code evidence: `<research_method.v1|code_evidence_map.v1 artifact>`
- Optional idea evidence: `<idea_candidate.v1|idea_evaluation.v1 artifact>`
- Runtime policy: `<fixture-only|approved-local|requires-human>`

## Expected outputs

- Evidence ABI: `experiment_plan.v1`
- Optional Evidence ABI: `idea_candidate.v1` or `idea_evaluation.v1`
- Artifacts: commands, metrics, expected outputs, assumptions, risk notes, and
  approval gates.

## Instructions

1. Ground every idea or experiment in supplied evidence ids.
2. Define hypothesis, commands, data, metrics, expected artifacts, and limits.
3. Mark plans as requiring approval when execution is non-fixture, destructive,
   networked, expensive, or long running.
4. Validate `experiment_plan.v1` before completion.

## Forbidden

- Do not run the experiment.
- Do not invent unsupported ideas.
- Do not hide missing datasets, credentials, or compute requirements.
- Do not produce `claim_verdict.v1`.

## Failure and approval gates

- Ask for human approval before non-fixture execution can be scheduled.
- Emit inconclusive evidence when a plausible plan lacks required data, code, or
  permissions.
