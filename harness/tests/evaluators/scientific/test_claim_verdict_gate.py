from pathlib import Path

from evaluators.scientific import claim_verdict_gate
from evaluators.scientific.common import load_json

FIXTURES = Path(__file__).parent / "fixtures"


def test_claim_verdict_gate_accepts_evidence_linked_verdict():
    path = FIXTURES / "pass/claim_verdict.json"
    result = claim_verdict_gate.evaluate(load_json(path), path)

    assert result.ok is True
    assert result.status == "passed"
    assert result.reasons == []


def test_claim_verdict_gate_rejects_source_free_verdict():
    path = FIXTURES / "fail/claim_verdict.json"
    result = claim_verdict_gate.evaluate(load_json(path), path)

    assert result.ok is False
    assert result.status == "failed"
    joined = " ".join(result.reasons)
    assert "evidence_ids" in joined
    assert "limitations" in joined
    assert "artifacts" in joined
