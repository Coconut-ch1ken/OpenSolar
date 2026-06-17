# Dispatch Template: Scientific Code Evidence Map

Use for logical operators:
- `ScientificCodeEvidenceMapper`

## Task envelope

- `task_id`: `<task-id>`
- `sprint_id`: `<sprint-id>`
- `node_id`: `<node-id>`
- `operator_id`: `<physical-operator-id>`
- `task_type`: `scientific_code_evidence_map`

## Inputs

- Claim or method evidence: `<research_claims.v1|research_method.v1 artifact>`
- Code artifact or repository path: `<path-or-artifact-id>`
- Allowed inspection commands: `<none|list>`

## Expected outputs

- Evidence ABI: `code_evidence_map.v1`
- Artifacts: mapping table, unmapped targets, inspection notes, and limitations.

## Instructions

1. Link claim or method ids to concrete files, symbols, commands, and datasets
   only when they are present in supplied code artifacts.
2. Separate static mapping from execution.
3. Preserve unmapped and ambiguous targets.
4. Validate `code_evidence_map.v1` before completion.

## Forbidden

- Do not fabricate paths, symbols, commands, or datasets.
- Do not run experiments.
- Do not install dependencies or expand network access.
- Do not produce `claim_verdict.v1`.

## Failure and approval gates

- Ask for human approval before running commands or modifying code.
- Emit failed or inconclusive evidence when the repository or mapping target is
  missing or ambiguous.
