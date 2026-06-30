#!/usr/bin/env python3
from __future__ import annotations

import json
import sys


request = json.loads(sys.stdin.read())
assert request["schema"] == "autosci_model_request.v1"
assert request["action"] == "check_wiki_health"
findings = request["context"]["findings"]
assert findings["lint_report"]["issue_counts"]["error"] == 0

print(
    json.dumps(
        {
            "schema": "autosci_model_response.v1",
            "status": "completed",
            "outputs": {
                "answer": "Native lint is clean and the wiki quality review has source-attributed evidence.",
                "confidence": 0.93,
                "evidence_ids": ["model:check-native-lint-proof-20260630"],
                "findings": [
                    {
                        "criterion": "native lint",
                        "verdict": "pass",
                        "evidence_id": "model:check-native-lint-proof-20260630",
                    }
                ],
                "model": "gpt-5.5",
                "provider": "codex",
            },
        }
    )
)
