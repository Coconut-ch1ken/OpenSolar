# Dispatch Template: Scientific Graph Update

Use for logical operators:
- `ScientificGraphUpdater`

## Task envelope

- `task_id`: `<task-id>`
- `sprint_id`: `<sprint-id>`
- `node_id`: `<node-id>`
- `operator_id`: `<physical-operator-id>`
- `task_type`: `scientific_graph_update`

## Inputs

- Source evidence: `<research_paper.v1|research_claims.v1|claim_verdict.v1|scientific_report.v1 artifact>`
- Target graph or edge set: `<graph-id-or-path>`
- Requested edge changes: `<create|update|delete|skip|reject>`
- Approval reference: `<approval-id-or-N/A>`

## Expected outputs

- Evidence ABI: `research_graph_update.v1`
- Artifacts: proposed edge changes, accepted edges, skipped edges, rejected
  edges, rollback notes, and limitations.

## Instructions

1. Change only graph nodes or edges explicitly listed by the dispatch.
2. Link every accepted graph change to source evidence ids.
3. Preserve conflicting, missing, and ambiguous graph relationships separately.
4. Validate `research_graph_update.v1` before completion.

## Forbidden

- Do not infer graph edges from unstated sources or model intuition.
- Do not rewrite broad graph regions without explicit approval.
- Do not convert inconclusive evidence into accepted graph relationships.
- Do not hide failed, skipped, or rejected graph updates.

## Failure and approval gates

- Ask for human approval before destructive deletes, broad rewrites, canonical
  identity merges, or policy-sensitive graph changes.
- Emit failed or inconclusive evidence when graph targets, approvals, or source
  evidence are missing or ambiguous.
