# AutoSci Research Pipeline Report

Target: `skillgen`
Pipeline: `skillgen`
Resume from: `ideate`
Venue: `ICLR`
Skip paper: `False`

## Stage State

| Order | Stage | State |
| ---: | --- | --- |
| 1 | `setup` | `skipped_resume_boundary` |
| 2 | `ingest` | `skipped_resume_boundary` |
| 3 | `discover` | `skipped_resume_boundary` |
| 4 | `ideate` | `completed` |
| 5 | `novelty-review` | `pending_evidence` |
| 6 | `experiment-design` | `completed` |
| 7 | `experiment-run` | `pending_evidence` |
| 8 | `collect` | `pending_evidence` |
| 9 | `review` | `pending_evidence` |
| 10 | `paper-plan` | `completed` |
| 11 | `paper-compile` | `pending_evidence` |

## Gate State

- Execution state: gated
- Side effects executed: false
- Workspace mutation outside generated pipeline artifacts: false
- Required before full parity: Review LLM evidence, online discovery evidence, experiment runtime evidence, collection evidence, and LaTeX/PDF compile evidence.

## Evidence Summary

- Paper exists: `False`
- Discovery completed: `False`
- External novelty completed: `False`
- Review LLM completed: `False`
- Scheduler lifecycle completed: `False`
- Experiment runtime verified: `False`
- Compile runtime verified: `False`
- Integrated PDF: `not_materialized`

## Resume Notes

- The next executable stage is recorded, but no native stage runner was launched.
- This report is intended for parity auditing and resume planning, not as research outcome evidence.
