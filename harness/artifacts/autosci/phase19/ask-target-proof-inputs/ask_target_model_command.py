import json
import sys


request = json.loads(sys.stdin.read())
assert request["schema"] == "autosci_model_request.v1"
assert request["action"] == "ask_wiki"
assert request["prompt"] != "concept:skillgen-support"
assert request["context"]["retrieval_hits"]

print(json.dumps({
    "schema": "autosci_model_response.v1",
    "status": "completed",
    "outputs": {
        "answer": "SkillGen support is grounded in retrieved wiki evidence about verifier-gated generated skills and paper-derived runtime checks.",
        "confidence": 0.87,
        "evidence_ids": ["model:ask-target-skillgen-20260630"],
        "model": "gpt-5.5",
        "provider": "codex-model-command"
    }
}))
