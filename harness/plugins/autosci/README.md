# AutoSci Backend Adapter

This package is a Solar backend implementation package for AutoSci-derived
research actions. It must not own the research workflow.

Solar-native ownership stays in:

- TaskGraph templates
- `Scientific*` logical operators
- `cap.research-*` capability capsules
- Evidence ABI schemas under `schemas/evidence/`
- deterministic evaluator gates

The adapter converts bounded fixture or backend outputs into Solar Evidence ABI
documents and writes them under declared plugin artifact scopes.

## Commands

```bash
python3 plugins/autosci/bin/autosci_bridge.py --help
python3 plugins/autosci/bin/autosci_bridge.py smoke
python3 plugins/autosci/bin/autosci_bridge.py validate --result artifacts/autosci/smoke/result.json
python3 plugins/autosci/bin/autosci_bridge.py run --action ingest_paper --envelope plugins/autosci/tests/fixtures/envelope.ingest_paper.json
```

Supported Phase 4 actions:

- `ingest_paper`
- `extract_claims`
- `design_experiment`
- `run_experiment`
- `verify_claim`
- `write_report`

Additional adapter modules are present for method, code evidence, and idea
conversion so later phases can bind native nodes without introducing a monolithic
AutoSci runner.
