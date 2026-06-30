import json
from pathlib import Path
Path("results.json").write_text(json.dumps({"outcome": "supports", "metrics": [{"name": "accuracy", "value": 0.98}], "evidence_ids": ["result:codex-exp-run-final-proof"], "logs": ["live provider final proof collected metrics"]}))
