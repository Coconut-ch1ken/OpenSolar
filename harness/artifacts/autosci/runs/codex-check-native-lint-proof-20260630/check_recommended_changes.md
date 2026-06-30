# Wiki Health Check

Wiki root: `artifacts/autosci/phase19/check-native-lint-proof-inputs/wiki`
Markdown pages: `1`
Missing dirs: `N/A`
Edge errors: `0`
Native lint errors: `0`
Native lint warnings: `0`
Native lint info: `1`

## Model Evidence

Status: `completed`
Source: `model-command`
Answer: Native lint is clean and the wiki quality review has source-attributed evidence.

## Final Quality Boundary

Status: `final_quality_ready`
Final quality ready: `True`

## Findings JSON

```json
{
  "checked_roots": [
    "artifacts/autosci/phase19/check-native-lint-proof-inputs/wiki",
    "artifacts/autosci/workspace/wiki",
    "wiki",
    "harness/artifacts/autosci/workspace/wiki"
  ],
  "edge_errors": [],
  "lint_report": {
    "edge_count": 0,
    "issue_counts": {
      "error": 0,
      "info": 1,
      "warn": 0
    },
    "ok": true,
    "page_count": 1,
    "returncode": 0,
    "schema": "autosci_wiki_lint_cli.v1",
    "status": "completed",
    "wiki_root": "/Users/jamesyuan/Developer/Github Repos (On Git)/OpenSolar/harness/artifacts/autosci/phase19/check-native-lint-proof-inputs/wiki"
  },
  "markdown_page_count": 1,
  "missing_dirs": [],
  "model_output": {
    "answer": "Native lint is clean and the wiki quality review has source-attributed evidence.",
    "checked_paths": [],
    "command": [
      "/Users/jamesyuan/Developer/Github Repos (On Git)/OpenSolar/.venv/bin/python",
      "/Users/jamesyuan/Developer/Github Repos (On Git)/OpenSolar/harness/artifacts/autosci/phase19/check-native-lint-proof-inputs/bin/check-model-command-20260630.py"
    ],
    "confidence": 0.93,
    "evidence_ids": [
      "model:check-native-lint-proof-20260630"
    ],
    "findings": [
      {
        "criterion": "native lint",
        "evidence_id": "model:check-native-lint-proof-20260630",
        "verdict": "pass"
      }
    ],
    "ideas": [],
    "invocation_mode": "command",
    "model": "gpt-5.5",
    "provider": "codex",
    "request_path": "artifacts/autosci/runs/codex-check-native-lint-proof-20260630/check_wiki_health_model_request.json",
    "request_sha256": "f51ad891b793f6bc4fe9a2ebae18db2e8f059c6a680cdabb50aca7694836d3f9",
    "response_path": "artifacts/autosci/runs/codex-check-native-lint-proof-20260630/check_wiki_health_model_stdout.json",
    "response_sha256": "b814e31950737db9df04d1f68027ff13c54333d0e364e3c64620f4af00324018",
    "source": "model-command",
    "status": "completed"
  },
  "root_exists": true,
  "target": "autosci wiki",
  "wiki_root": "artifacts/autosci/phase19/check-native-lint-proof-inputs/wiki"
}
```
