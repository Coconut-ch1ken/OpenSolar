# Reset Plan Proposal

Target: `autosci`

## Proposed Changes

- `change.manual.reset_plan` [manual]: Record the approved reset plan checklist, requested target, and rollback notes.
- `change.gate.reset_plan` [gate]: Keep side-effect execution blocked until approval evidence and before/after artifact evidence are present.

## Controls

- Approval state: proposed
- Protected runtime changed: false
- Side effects executed: false
- Approval contract state: verified
