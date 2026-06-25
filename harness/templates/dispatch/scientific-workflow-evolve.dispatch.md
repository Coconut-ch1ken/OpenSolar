# Dispatch Template: Scientific Workflow Evolve

Use for logical operators:
- `ScientificWorkflowEvolver`

## Task envelope

- `task_id`: `<task-id>`
- `sprint_id`: `<sprint-id>`
- `node_id`: `<node-id>`
- `operator_id`: `<physical-operator-id>`
- `task_type`: `scientific_workflow_evolve`

## Inputs

- Failed, blocked, or inconclusive run evidence: `<evidence-artifact-id>`
- Current capsule, manual, dispatch, gate, or routing definition: `<artifact-id-or-path>`
- Change scope: `<proposal-only|approved-patch|requires-human>`
- Approval reference: `<approval-id-or-N/A>`

## Expected outputs

- Evidence ABI: `workflow_evolution.v1`
- Artifacts: proposed changes, rejected changes, risk notes, compatibility notes,
  and limitations.

## Instructions

1. Propose workflow changes only from explicit failed, blocked, or inconclusive
   evidence.
2. Separate capsule, manual, dispatch, gate, routing, and evaluator changes.
3. Mark proposals requiring human review before runtime policy or routing
   changes are applied.
4. Validate `workflow_evolution.v1` before completion.

## Forbidden

- Do not silently change scheduler behavior, routing, quotas, leases, scoring, or
  model selection.
- Do not treat one failed run as proof that a workflow rule is globally wrong.
- Do not hide compatibility risks, rejected changes, or missing evidence.
- Do not apply policy or routing changes unless explicitly approved.

## Failure and approval gates

- Ask for human approval before applying workflow, gate, routing, or policy
  changes.
- Emit failed or inconclusive evidence when the causal link from run evidence to
  workflow change is weak or unsupported.
