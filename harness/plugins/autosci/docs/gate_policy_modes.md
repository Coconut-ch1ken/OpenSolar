# AutoSci Gate Policy Modes

This document defines the policy-driven side-effect gate used by the Solar
AutoSci bridge. The default remains `strict_hitl`.

## Mode Matrix

| Mode | Proof | Auto side effects | Still blocked by default |
|---|---|---|---|
| `strict_hitl` | required | local reads and artifact writes only | wiki mutation, local commands, web serving, network, email, remote, destructive/config/credential mutation |
| `safe` | required | local reads and artifact writes only | wiki mutation, local commands, web serving, network, email, remote, destructive/config/credential mutation |
| `parity_demo` | required | sandbox wiki/artifact writes, allowlisted local commands, TeX compile, browser/server probe, PNG export | email, remote, destructive/config/credential mutation; network unless `SOLAR_AUTOSCI_ALLOW_NETWORK=1` |
| `unsafe_native` | best-effort | local writes, wiki mutation, local commands, web/server probe, network | email, remote, destructive/config/credential mutation unless explicit env opt-in |
| `autosci_native` | best-effort | all side effects are attempted without Solar gate blocking | none at the Solar gate layer |

## Risk Opt-In Environment Variables

| Side effect | Env |
|---|---|
| network fetch | `SOLAR_AUTOSCI_ALLOW_NETWORK=1` |
| email send | `SOLAR_AUTOSCI_ALLOW_EMAIL=1` |
| remote execution | `SOLAR_AUTOSCI_ALLOW_REMOTE=1` |
| destructive mutation | `SOLAR_AUTOSCI_ALLOW_DESTRUCTIVE=1` |
| protected config mutation | `SOLAR_AUTOSCI_ALLOW_PROTECTED_CONFIG=1` |
| credential mutation | `SOLAR_AUTOSCI_ALLOW_CREDENTIAL_MUTATION=1` |

## Mode Resolution

Resolution priority:

1. `envelope.inputs.gate_mode`
2. `envelope.inputs.autosci_mode`
3. `SOLAR_AUTOSCI_GATE_MODE`
4. optional config object passed to the policy layer
5. default `strict_hitl`

## Evidence

Actions that consult the policy should attach the serialized decision to:

- `outputs.policy_decision`
- `provenance.gate_policy`
- an optional `gate_policy_decision_json` sidecar

Auto-approved modes use a synthetic reference of the form:

```text
policy:auto:<mode>:<action>:<utc_timestamp>
```

This is not human approval. It records why the side effect was allowed.

## Current Bridge Coverage

The first integrated action is `visualize_graph` / `$visualize --serve`.

In `strict_hitl`, existing approval/runtime evidence behavior is preserved. In
`parity_demo`, `$visualize --serve` can automatically run a bounded native
server probe through `tools/serve.py --probe-server --port 0`, which starts the
loopback HTTP server, requests `/api/health`, and shuts the server down.

Future slices should connect the same policy helper to compile, poster,
experiment, daily/discover, setup/reset, and other side-effect actions.

## Examples

Strict:

```bash
SOLAR_AUTOSCI_GATE_MODE=strict_hitl python3 harness/plugins/autosci/bin/autosci_bridge.py run --action visualize_graph --envelope artifacts/autosci/demo/visualize.envelope.json
```

Parity demo:

```bash
SOLAR_AUTOSCI_GATE_MODE=parity_demo python3 harness/plugins/autosci/bin/autosci_bridge.py run --action visualize_graph --envelope artifacts/autosci/demo/visualize.envelope.json
```

Native:

```bash
SOLAR_AUTOSCI_GATE_MODE=autosci_native python3 harness/plugins/autosci/bin/autosci_bridge.py run --action visualize_graph --envelope artifacts/autosci/demo/visualize.envelope.json
```

To return to the original behavior, unset `SOLAR_AUTOSCI_GATE_MODE` or set it
to `strict_hitl`.
