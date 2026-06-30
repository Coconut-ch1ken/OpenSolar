# Wiki Health Check

Wiki root: `artifacts/autosci/workspace/wiki`
Markdown pages: `41`
Missing dirs: `N/A`
Edge errors: `0`

## Model Evidence

Status: `completed`
Source: `model-command`
Answer: The wiki has sufficient structure for this smoke review.

## Final Quality Boundary

Status: `final_quality_ready`
Final quality ready: `True`

## Findings JSON

```json
{
  "checked_roots": [
    "artifacts/autosci/workspace/wiki",
    "wiki",
    "harness/artifacts/autosci/workspace/wiki"
  ],
  "edge_errors": [],
  "markdown_page_count": 41,
  "missing_dirs": [],
  "model_output": {
    "answer": "The wiki has sufficient structure for this smoke review.",
    "checked_paths": [],
    "command": [
      "/Users/jamesyuan/Developer/Github Repos (On Git)/OpenSolar/.venv/bin/python",
      "-c",
      "import json, sys; req=json.loads(sys.stdin.read()); print(json.dumps({\"schema\":\"autosci_model_response.v1\",\"status\":\"completed\",\"outputs\":{\"answer\":\"The wiki has sufficient structure for this smoke review.\",\"confidence\":0.88,\"evidence_ids\":[\"model:check-smoke\"],\"findings\":[],\"model\":\"smoke-model\",\"provider\":\"command\"}}))"
    ],
    "confidence": 0.88,
    "evidence_ids": [
      "model:check-smoke"
    ],
    "findings": [],
    "ideas": [],
    "invocation_mode": "command",
    "model": "smoke-model",
    "provider": "command",
    "request_path": "artifacts/autosci/runs/codex-check-model-proof-check/check_wiki_health_model_request.json",
    "request_sha256": "440765725594fe1c3acf5486e9c5f7d977a82bc68ed5ad07f120276a35ca3e17",
    "response_path": "artifacts/autosci/runs/codex-check-model-proof-check/check_wiki_health_model_stdout.json",
    "response_sha256": "c8d1d635f75328ab513f0c06cc99a294bfe1d32ec5a4285e17095f51dc8b39bd",
    "source": "model-command",
    "status": "completed"
  },
  "root_exists": true,
  "target": "autosci wiki",
  "wiki_root": "artifacts/autosci/workspace/wiki"
}
```
