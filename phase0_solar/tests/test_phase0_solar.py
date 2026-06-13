from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from phase0_solar import (
    BenchmarkClaim,
    BenchmarkContract,
    ClaimComparison,
    ObservedMetric,
    Phase0VerificationRequest,
    build_phase0_solar_plan,
    compare_contract_to_observed,
    to_dict,
)
from phase0_solar.artifact_adapter import load_phase0_matrix
from phase0_solar.report_runner import write_report


ROOT = Path(__file__).resolve().parents[2]
REQUEST_SCHEMA = ROOT / "phase0_solar" / "config" / "schemas" / "phase0-verification-request.schema.json"
A4_MATRIX = Path(
    "/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B/"
    "phase_0/runs/20260604/artifacts/all_claim_verification_matrix.json"
)


class Phase0SolarTest(unittest.TestCase):
    def test_request_schema_round_trip(self) -> None:
        request = Phase0VerificationRequest(
            request_id="req-skillgen",
            paper_source="docs/SkillGen.pdf",
            repo_source="code/official",
            objective="Verify benchmark claims with evidence.",
            source_metadata={"source": "codex_app"},
        )
        payload = to_dict(request)
        self.assertEqual(payload["schema_version"], "solar.phase0.claim_verification.v0")

        try:
            import jsonschema
        except Exception:  # pragma: no cover - local minimal env fallback
            return
        schema = json.loads(REQUEST_SCHEMA.read_text(encoding="utf-8"))
        jsonschema.validate(instance=payload, schema=schema)

    def test_readiness_cannot_upgrade_claim_verdict(self) -> None:
        with self.assertRaisesRegex(ValueError, "require observed metrics"):
            ClaimComparison(
                claim_id="claim_ready_only",
                contract_id="contract_ready_only",
                observed_metric_ids=(),
                claim_verdict_status="partially_reproduced",
                execution_readiness_status="ready",
                evidence_ids=("artifact:plan",),
                mismatch_summary="Ready is not evidence.",
                limitations=(),
                comparison_basis="readiness_only",
            )

    def test_reconstructed_positive_caps_at_partial(self) -> None:
        claim = BenchmarkClaim(
            claim_id="claim_reconstructed",
            paper_location="Table 1",
            metric_name="accuracy_delta",
            dataset="mcp_bench_single",
            split="test",
            config="local_reconstructed",
            expected_value=0.0,
            expected_direction_or_tolerance="delta_positive",
            extraction_evidence_ids=("paper:table1",),
        )
        contract = BenchmarkContract(
            contract_id="contract_reconstructed",
            claim_id=claim.claim_id,
            runnable_target="reconstructed_path",
            metric_definition="Delta accuracy",
            aggregation_rule="single smoke",
            tolerance=0.0,
            comparison_logic="delta_positive",
            required_artifacts=("eval_results.json",),
            human_approval_state="approved",
            reconstructed_path=True,
            deviation_notes=("Reconstructed smoke only.",),
        )
        metric = ObservedMetric(
            observed_metric_id="metric_positive",
            run_id="run",
            metric_name="accuracy_delta",
            observed_value=0.2,
            dataset=claim.dataset,
            split=claim.split,
            config=claim.config,
            source_artifact_ids=("artifact:eval_results",),
            parser_confidence=1.0,
        )

        comparison = compare_contract_to_observed(
            claim,
            contract,
            (metric,),
            readiness_status="ready",
            evidence_ids=("artifact:eval_results", "metric_positive"),
        )

        self.assertEqual(comparison.claim_verdict_status, "partially_reproduced")
        self.assertEqual(comparison.comparison_basis, "executed_reconstructed_smoke")

    def test_phase0_solar_plan_uses_local_fragments(self) -> None:
        request = Phase0VerificationRequest(
            request_id="req-solar",
            paper_source="paper.pdf",
            repo_source="repo",
            objective="Verify paper claims through Solar.",
        )
        plan = build_phase0_solar_plan(request)

        self.assertEqual(plan.task_envelope["capability_capsule_id"], "cap.phase0-claim-verification")
        self.assertEqual(plan.task_envelope["logical_operator"], "ResearchClaimVerifier")
        self.assertEqual(plan.capsule_validation_errors, ())
        self.assertIn("mini-codex-gpt55-medium-evaluator-1", plan.operator_candidates)
        self.assertEqual(plan.selected_actor, "mini-codex-gpt55-medium-evaluator-1")
        self.assertTrue(plan.submission_ready)

    def test_artifact_replay_report_generation(self) -> None:
        if not A4_MATRIX.exists():
            self.skipTest("a4 Phase 0 matrix not available")

        bundle = load_phase0_matrix(A4_MATRIX)
        self.assertEqual(len(bundle.claims), 12)
        self.assertIn("blocked", bundle.claim_status_counts)

        with tempfile.TemporaryDirectory() as td:
            result = write_report(matrix_path=A4_MATRIX, output_dir=td, run_id="unit-replay")
            report = Path(result["report_path"])
            summary = Path(result["summary_path"])
            self.assertTrue(report.exists())
            self.assertTrue(summary.exists())
            self.assertIn("artifact_replay", report.read_text(encoding="utf-8"))
            payload = json.loads(summary.read_text(encoding="utf-8"))
            self.assertEqual(payload["mode"], "artifact_replay")
            self.assertEqual(payload["claim_count"], 12)


if __name__ == "__main__":
    unittest.main()
