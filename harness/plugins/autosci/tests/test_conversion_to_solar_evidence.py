from __future__ import annotations

import json
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
if str(PLUGIN) not in sys.path:
    sys.path.insert(0, str(PLUGIN))

from adapters.autosci_to_claim_verdict import convert as convert_verdict
from adapters.autosci_to_experiment_plan import convert as convert_plan
from adapters.autosci_to_experiment_result import convert as convert_result
from adapters.autosci_to_research_claims import convert as convert_claims
from adapters.autosci_to_research_paper import convert as convert_paper
from adapters.autosci_to_scientific_report import convert as convert_report


def assert_evidence_shape(payload: dict, schema: str) -> None:
    assert payload["schema"] == schema
    for field in ["task_id", "sprint_id", "node_id", "status", "inputs", "outputs", "artifacts", "provenance", "limitations"]:
        assert field in payload
    assert payload["provenance"]["implementation_package"] == "plugins/autosci"


def test_raw_claims_convert_to_unverified_solar_claims() -> None:
    raw = json.loads((PLUGIN / "tests" / "fixtures" / "sample_autosci_raw_claims.json").read_text(encoding="utf-8"))
    payload = convert_claims(raw, {"task_id": "t", "sprint_id": "s", "node_id": "n", "inputs": {}})
    assert_evidence_shape(payload, "research_claims.v1")
    assert payload["outputs"]["claims"]
    assert all(claim["verification_status"] == "unverified" for claim in payload["outputs"]["claims"])
    assert all(claim["source_anchor"] for claim in payload["outputs"]["claims"])


def test_core_phase4_converters_emit_expected_schema_names() -> None:
    envelope = {"task_id": "t", "sprint_id": "s", "node_id": "n", "inputs": {}}
    paper = convert_paper({"paper_id": "p", "title": "T", "source_type": "markdown", "source_ref": "sample.md"}, envelope)
    plan = convert_plan({}, envelope)
    result = convert_result({}, envelope)
    verdict = convert_verdict({}, envelope)
    report = convert_report({}, envelope)
    assert_evidence_shape(paper, "research_paper.v1")
    assert_evidence_shape(plan, "experiment_plan.v1")
    assert_evidence_shape(result, "experiment_result.v1")
    assert_evidence_shape(verdict, "claim_verdict.v1")
    assert_evidence_shape(report, "scientific_report.v1")
