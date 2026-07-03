import argparse
import json
from pathlib import Path


parser = argparse.ArgumentParser()
parser.add_argument("--experiment-id", required=True)
parser.add_argument("--marker", required=True)
args = parser.parse_args()

marker = Path(args.marker)
marker.parent.mkdir(parents=True, exist_ok=True)
marker.write_text("pilot approved command executed\n", encoding="utf-8")

payload = {
    "schema": "experiment_result.v1",
    "task_id": "task-exp-pilot-run-approved-command-proof",
    "sprint_id": "phase19-exp-pilot-run",
    "node_id": "node-exp-pilot-run-approved-command",
    "status": "completed",
    "inputs": {"experiment_id": args.experiment_id},
    "outputs": {
        "result": {
            "experiment_id": args.experiment_id,
            "outcome": "supports",
            "metrics": [{"name": "accuracy", "value": 0.94}],
            "evidence_ids": ["runtime:exp-pilot-run-approved-command"],
            "logs": ["phase19 approved pilot command executed"],
        }
    },
    "artifacts": [
        {
            "type": "pilot_marker",
            "path": str(marker),
            "label": "approved command marker",
        }
    ],
    "provenance": {
        "operator_id": "phase19-pilot-command",
        "implementation_package": "plugins/autosci",
        "timestamp": "2026-07-02T00:00:00Z",
    },
    "limitations": [],
}
print(json.dumps(payload))
