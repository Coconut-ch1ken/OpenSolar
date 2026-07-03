#!/usr/bin/env python3
from __future__ import annotations

import json
import sys


request = json.loads(sys.stdin.read())
assert request["schema"] == "autosci_model_request.v1"
assert request["action"] == "check_wiki_health"

findings = request["context"]["findings"]
assert findings["root_exists"] is True
assert findings["markdown_page_count"] >= 1
assert findings["missing_dirs"] == []
assert findings["edge_errors"] == []
assert findings["lint_report"]["issue_counts"]["error"] == 0

print(
    json.dumps(
        {
            "schema": "autosci_model_response.v1",
            "status": "completed",
            "outputs": {
                "answer": (
                    "The local proof wiki has the required AutoSci wiki directories, "
                    "at least one source page, a parseable graph edge file, and zero "
                    "native lint errors."
                ),
                "confidence": 0.92,
                "evidence_ids": ["model:check-local-quality-proof-20260702"],
                "findings": [
                    {
                        "criterion": "local structure",
                        "verdict": "pass",
                        "evidence_id": "model:check-local-quality-proof-20260702",
                    },
                    {
                        "criterion": "native lint",
                        "verdict": "pass",
                        "evidence_id": "model:check-local-quality-proof-20260702",
                    },
                ],
                "model": "local-model-command",
                "provider": "codex-local-proof",
            },
        }
    )
)
