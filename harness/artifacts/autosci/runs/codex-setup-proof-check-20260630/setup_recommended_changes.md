# Setup Status Proposal

Target: `autosci`

## Proposed Changes

- `change.manual.setup_status` [manual]: Record the approved setup status checklist, requested target, and rollback notes.
- `change.gate.setup_status` [gate]: Keep side-effect execution blocked until approval evidence and before/after artifact evidence are present.

## Controls

- Approval state: proposed
- Protected runtime changed: false
- Side effects executed: false
- Approval contract state: verified
