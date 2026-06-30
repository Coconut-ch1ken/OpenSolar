# Artifact Refinement Proposal

Target: `artifacts/autosci/workspace/wiki/outputs/refine-loop-proof.md`

## Proposed Changes

- `change.manual.refine_artifact` [manual]: Record the approved refine artifact checklist, requested target, and rollback notes.
- `change.gate.refine_artifact` [gate]: Keep side-effect execution blocked until approval evidence and before/after artifact evidence are present.

## Controls

- Approval state: applied
- Protected runtime changed: true
- Side effects executed: true
- Approval contract state: verified
