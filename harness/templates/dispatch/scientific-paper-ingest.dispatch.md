# Dispatch Template: Scientific Paper Ingest

Use for logical operators:
- `ScientificPaperIngestor`
- `ScientificPaperAnalyzer`

## Task envelope

- `task_id`: `<task-id>`
- `sprint_id`: `<sprint-id>`
- `node_id`: `<node-id>`
- `operator_id`: `<physical-operator-id>`
- `task_type`: `scientific_paper_ingest`

## Inputs

- Paper source: `<path-or-artifact-id>`
- Metadata hints: `<title/authors/doi/arxiv-id-or-N/A>`
- Extraction scope: `<sections-or-N/A>`
- Network policy: `<denied|explicit-targets-only>`

## Expected outputs

- Evidence ABI: `research_paper.v1`
- Artifacts: normalized text, metadata, extraction diagnostics, and limitations.

## Instructions

1. Read only the supplied source and metadata hints.
2. Extract paper identity, source anchors, claims, method summary, and
   limitations when present.
3. Preserve missing fields as limitations or inconclusive status.
4. Validate the emitted `research_paper.v1` payload before completion.

## Forbidden

- Do not verify claims.
- Do not fetch new papers unless explicitly authorized.
- Do not mutate memory or graph state.
- Do not assume a specific backend implementation.

## Failure and approval gates

- Ask for human approval before credentialed access, paid access, external
  retrieval, or overwriting a canonical paper record.
- Emit failed or inconclusive evidence when source identity or source anchors
  cannot be established.
