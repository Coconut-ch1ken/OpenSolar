# Phase 0 Solar Overlay

This folder is a non-invasive Solar overlay for Phase 0 paper claim
verification.

It keeps new migration files together and does not modify `harness/config`,
`harness/lib`, or scheduler/runtime behavior. The overlay can later be promoted
into formal Solar runtime locations after review.

## Scope

Current scope:

- Define Phase 0 request, claim, contract, metric, comparison, evidence-map,
  run-manifest, and summary schemas.
- Preserve `claim_verdict_status` and `execution_readiness_status` as separate
  fields.
- Compare observed metrics against benchmark contracts.
- Cap reconstructed-path positive evidence at `partially_reproduced`.
- Provide a local capability capsule fragment.
- Provide a local `ResearchClaimVerifier` logical operator fragment.
- Build a Solar task envelope and local admission/routing plan.

Out of scope for this pass:

- Golden fixture replay.
- Golden conclusion enforcement.
- Installing fragments into `harness/config`.
- Calling `operator_runtime.submit()`.
- Running paper-scale benchmark jobs.

## Layout

| Path | Purpose |
| --- | --- |
| `schemas.py` | Phase 0 dataclass contracts and invariants. |
| `comparator.py` | Claim/contract/metric comparison policy. |
| `solar_bridge.py` | Solar envelope, capsule validation, and local operator routing. |
| `config/capability-capsules/cap.phase0-claim-verification.yaml` | Local capsule fragment. |
| `config/logical-operators.fragment.json` | Local logical operator and actor binding fragment. |
| `config/schemas/phase0-verification-request.schema.json` | Intake request schema. |
| `tests/test_phase0_solar.py` | Non-golden unit tests. |

## Promotion Path

1. Review overlay files.
2. Validate the local capsule fragment.
3. Validate local routing with existing actor ids.
4. Add formal harness tests.
5. Merge config fragments into Solar config.
6. Add operator-runtime dry-run admission.
7. Add golden fixture regression later.
