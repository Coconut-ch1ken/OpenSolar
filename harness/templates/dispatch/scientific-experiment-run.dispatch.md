# Dispatch Template: Scientific Experiment Run

Use for logical operators:
- `ScientificExperimentRunner`
- `ScientificExperimentMonitor`

## Task envelope

- `task_id`: `<task-id>`
- `sprint_id`: `<sprint-id>`
- `node_id`: `<node-id>`
- `operator_id`: `<physical-operator-id>`
- `task_type`: `scientific_experiment_run`

## Inputs

- Experiment plan: `<experiment_plan.v1 artifact>`
- Approval reference: `<approval-id-or-N/A>`
- Timeout and resource limits: `<limits>`
- Output directory: `<artifact-dir>`

## Expected outputs

- Evidence ABI: `experiment_result.v1`
- Optional Evidence ABI: `experiment_status.v1`
- Artifacts: logs, metrics, command outputs, generated files, and limitations.

## Instructions

1. Execute only commands listed in the approved `experiment_plan.v1`.
2. Capture exit code, stdout/stderr tail, metrics, artifacts, environment notes,
   and limitations.
3. Stop on missing approval, denied commands, timeout, or missing prerequisites.
4. Validate `experiment_result.v1` or `experiment_status.v1` before completion.

## Forbidden

- Do not redesign the experiment.
- Do not install dependencies without explicit approval.
- Do not expand network or filesystem permissions.
- Do not produce `claim_verdict.v1`.

## Failure and approval gates

- Ask for human approval before credentialed, destructive, paid, networked, or
  long-running execution.
- Emit failed or inconclusive evidence when execution cannot safely complete.
