#!/usr/bin/env python3
"""Emit a structured local AutoSci experiment result for Phase 19 parity proof."""

from __future__ import annotations

import argparse
import json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment-id", required=True)
    args = parser.parse_args()
    print(
        json.dumps(
            {
                "experiment_id": args.experiment_id,
                "outcome": "supports",
                "metrics": [
                    {"name": "local_accuracy", "value": 0.91},
                    {"name": "experiment_exit_code", "value": 0},
                ],
                "evidence_ids": [f"runtime:{args.experiment_id}:local"],
                "logs": [
                    "approved local AutoSci experiment command executed",
                    "remote/provider configuration was not required for local mode",
                ],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
