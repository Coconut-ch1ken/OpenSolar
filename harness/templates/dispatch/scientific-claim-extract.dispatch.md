# Dispatch Template: Scientific Claim Extract

Use for logical operators:
- `ScientificClaimExtractor`
- `ScientificMethodExtractor`

## Task envelope

- `task_id`: `<task-id>`
- `sprint_id`: `<sprint-id>`
- `node_id`: `<node-id>`
- `operator_id`: `<physical-operator-id>`
- `task_type`: `scientific_claim_extract`

## Inputs

- Paper evidence: `<research_paper.v1 artifact>`
- Source text or anchors: `<path-or-artifact-id>`
- Extraction focus: `<claims|methods|metrics|assumptions|all>`

## Expected outputs

- Evidence ABI: `research_claims.v1`
- Optional Evidence ABI: `research_method.v1`
- Artifacts: extracted claim list, rejected candidates, method notes, and
  limitations.

## Instructions

1. Extract only claims and methods grounded in supplied evidence.
2. Attach each claim or method to source evidence ids and source anchors.
3. Mark unsupported, duplicate, or ambiguous candidates as rejected or
   inconclusive.
4. Validate emitted `research_claims.v1` and any `research_method.v1` payload.

## Forbidden

- Do not verify claims or assign truth verdicts.
- Do not infer unstated methods.
- Do not replace missing anchors with generic citations.
- Do not update memory.

## Failure and approval gates

- Ask for human approval if external sources are needed or claim boundaries would
  materially change interpretation.
- Emit inconclusive evidence when anchors or claim scope are uncertain.
