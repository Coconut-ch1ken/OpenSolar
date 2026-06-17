# Dispatch Template: Scientific Report Write

Use for logical operators:
- `ScientificReportPlanner`
- `ScientificReportDrafter`
- `ScientificPublicationProducer`

## Task envelope

- `task_id`: `<task-id>`
- `sprint_id`: `<sprint-id>`
- `node_id`: `<node-id>`
- `operator_id`: `<physical-operator-id>`
- `task_type`: `scientific_report_write`

## Inputs

- Paper evidence: `<research_paper.v1 artifact>`
- Claims and methods: `<research_claims.v1|research_method.v1 artifact>`
- Experiment results: `<experiment_result.v1 artifact>`
- Claim verdicts: `<claim_verdict.v1 artifact>`
- Audience and format: `<report-spec>`

## Expected outputs

- Evidence ABI: `scientific_report.v1`
- Optional Evidence ABI: `publication_bundle.v1`
- Artifacts: report draft, evidence table, unresolved questions, limitations,
  and packaging notes.

## Instructions

1. Build report sections from supplied evidence only.
2. Link every substantive claim to evidence ids and verdict ids.
3. Preserve failed experiments, inconclusive verdicts, and limitations.
4. Validate `scientific_report.v1` and any `publication_bundle.v1` payload before
   completion.

## Forbidden

- Do not fabricate citations, experiment results, or verdicts.
- Do not hide limitations or failed evidence.
- Do not publish, post, email, or commit externally without approval.
- Do not verify new claims during report writing.

## Failure and approval gates

- Ask for human approval before publication or external handoff.
- Emit inconclusive evidence when the requested conclusion is stronger than the
  available evidence.
