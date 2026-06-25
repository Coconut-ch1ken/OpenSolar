# Dispatch Template: Scientific Literature Discover

Use for logical operators:
- `ScientificLiteratureDiscoverer`

## Task envelope

- `task_id`: `<task-id>`
- `sprint_id`: `<sprint-id>`
- `node_id`: `<node-id>`
- `operator_id`: `<physical-operator-id>`
- `task_type`: `scientific_literature_discover`

## Inputs

- Topic query, anchor paper, claim, method, or memory artifact: `<query-or-artifact-id>`
- Allowed source channels: `<source-list>`
- Search filters: `<venue|year|author|citation|keyword-or-N/A>`
- Network policy: `<denied|explicit-targets-only|approved-search>`

## Expected outputs

- Evidence ABI: `literature_discovery.v1`
- Artifacts: candidate shortlist, rejected candidates, channel status, ranking
  rationale, deduplication notes, and limitations.

## Instructions

1. Search only the channels allowed by the dispatch and runtime policy.
2. Rank candidates using explicit relevance criteria and supplied evidence.
3. Preserve rejected, duplicate, inaccessible, and uncertain candidates.
4. Validate `literature_discovery.v1` before completion.

## Forbidden

- Do not auto-ingest discovered papers.
- Do not claim a candidate supports a scientific claim without extraction and
  verification evidence.
- Do not hide failed source channels, rate limits, sparse results, or ambiguity.
- Do not assume a specific backend implementation or source layout.

## Failure and approval gates

- Ask for human approval before using new external sources, paid APIs,
  credentialed access, downloads, or memory mutation.
- Emit failed or inconclusive evidence when allowed channels cannot run or the
  candidate ranking is too weak for downstream use.
