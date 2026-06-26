# Dispatch Template: Scientific Memory Update

Use for logical operators:
- `ScientificMemoryUpdater`

## Task envelope

- `task_id`: `<task-id>`
- `sprint_id`: `<sprint-id>`
- `node_id`: `<node-id>`
- `operator_id`: `<physical-operator-id>`
- `task_type`: `scientific_memory_update`

## Inputs

- Source evidence: `<research_paper.v1|research_claims.v1|claim_verdict.v1|scientific_report.v1 artifact>`
- Write target: `<memory-path-or-record-id>`
- Requested operation: `<create|update|skip|reject>`
- Approval reference: `<approval-id-or-N/A>`

## Expected outputs

- Evidence ABI: `research_memory_update.v1`
- Artifacts: accepted changes, skipped changes, rejected changes, source evidence
  links, rollback notes, and limitations.

## Instructions

1. Apply only the memory changes explicitly requested by the dispatch.
2. Link every accepted change to source evidence ids.
3. Preserve skipped and rejected changes with reasons.
4. Validate `research_memory_update.v1` before completion.

## Forbidden

- Do not mutate memory from model intuition, summaries, or unstated sources.
- Do not overwrite existing records without an explicit target and approval path.
- Do not convert inconclusive evidence into accepted memory.
- Do not hide skipped writes, rejected writes, or partial failures.

## Failure and approval gates

- Ask for human approval before destructive edits, broad rewrites, canonical
  record replacement, or policy-sensitive memory changes.
- Emit failed or inconclusive evidence when targets, approvals, or source
  evidence are missing or ambiguous.
