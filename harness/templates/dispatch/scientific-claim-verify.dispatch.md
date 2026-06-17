# Dispatch Template: Scientific Claim Verify

Use for logical operators:
- `ScientificClaimVerifier`

## Task envelope

- `task_id`: `<task-id>`
- `sprint_id`: `<sprint-id>`
- `node_id`: `<node-id>`
- `operator_id`: `<physical-operator-id>`
- `task_type`: `scientific_claim_verify`

## Inputs

- Claims: `<research_claims.v1 artifact>`
- Optional methods: `<research_method.v1 artifact>`
- Optional code mapping: `<code_evidence_map.v1 artifact>`
- Optional experiment results: `<experiment_result.v1 artifact>`
- Verdict criteria: `<criteria>`

## Expected outputs

- Evidence ABI: `claim_verdict.v1`
- Artifacts: per-claim evidence table, rationale, opposing evidence, and
  limitations.

## Instructions

1. Evaluate each claim only against supplied evidence ids.
2. Preserve supporting, opposing, missing, and inconclusive evidence separately.
3. Assign calibrated verdicts without hiding failed experiments or weak sources.
4. Validate `claim_verdict.v1` before completion.

## Forbidden

- Do not use unstated sources or model memory as evidence.
- Do not rerun experiments.
- Do not mutate research memory.
- Do not write a publication report unless separately dispatched.

## Failure and approval gates

- Ask for human approval when verdict criteria are ambiguous or domain-sensitive.
- Emit inconclusive evidence when supplied evidence cannot support a clear
  verdict.
