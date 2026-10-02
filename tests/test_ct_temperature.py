import math
import unittest
from datetime import datetime, timezone

from aquaflow.api import AquaFlowService
from aquaflow.treatment.chlorine_ct import (
    REFERENCE_TEMPERATURE_C,
    Segment,
    compliant,
    effective_ct,
    temperature_factor,
)
from aquaflow.workflow_models import normalize


def payload(segments, mg_l=1.0, low=0.2, high=4.0, required=20.0):
    return {
        "segments": [
            {"minutes": m, "residual": r, "baffling": b, "temperature_c": t}
            for m, r, b, t in segments
        ],
        "dose": {"mg_l": mg_l, "low_limit": low, "high_limit": high},
        "required": required,
    }


class TemperatureFactor(unittest.TestCase):
    def test_reference_temperature_is_neutral(self):
        self.assertEqual(temperature_factor(20.0), 1.0)
        self.assertEqual(REFERENCE_TEMPERATURE_C, 20.0)

    def test_warm_water_earns_more_credit(self):
        self.assertEqual(temperature_factor(30.0), 2.0)

    def test_cold_water_earns_less_credit(self):
        self.assertEqual(temperature_factor(10.0), 0.5)

    def test_effective_ct_applies_factor_per_segment(self):
        warm = [Segment(20, 1.0, 0.8, 30.0)]
        cold = [Segment(20, 1.0, 0.8, 10.0)]
        ref = [Segment(20, 1.0, 0.8, 20.0)]
        self.assertAlmostEqual(effective_ct(warm), 32.0)
        self.assertAlmostEqual(effective_ct(cold), 8.0)
        self.assertAlmostEqual(effective_ct(ref), 16.0)

    def test_mixed_segments_sum_individual_factors(self):
        rows = [Segment(10, 1.0, 1.0, 30.0), Segment(10, 1.0, 1.0, 10.0)]
        self.assertAlmostEqual(effective_ct(rows), 25.0)


class InvalidSegments(unittest.TestCase):
    def test_nonpositive_minutes_rejected(self):
        with self.assertRaises(ValueError):
            effective_ct([Segment(0, 1.0, 0.8, 20.0)])

    def test_negative_residual_rejected(self):
        with self.assertRaises(ValueError):
            effective_ct([Segment(20, -0.1, 0.8, 20.0)])

    def test_baffling_out_of_range_rejected(self):
        with self.assertRaises(ValueError):
            effective_ct([Segment(20, 1.0, 0.0, 20.0)])
        with self.assertRaises(ValueError):
            effective_ct([Segment(20, 1.0, 1.5, 20.0)])

    def test_non_finite_temperature_rejected(self):
        with self.assertRaises(ValueError):
            effective_ct([Segment(20, 1.0, 0.8, math.nan)])
        with self.assertRaises(ValueError):
            effective_ct([Segment(20, 1.0, 0.8, math.inf)])

    def test_workflow_rejects_invalid_segment(self):
        service = AquaFlowService()
        with self.assertRaises(ValueError):
            service.run_workflow("ct_assurance", payload([(0, 1.0, 0.8, 20.0)]))


class Normalization(unittest.TestCase):
    def test_temperature_survives_normalization(self):
        envelope = normalize("ct_assurance", payload([(20, 1.0, 0.8, 30.0)]))
        self.assertNotIn("_temperature_override", envelope.payload)
        self.assertEqual(envelope.payload["segments"][0]["temperature_c"], 30.0)

    def test_contract_is_current(self):
        envelope = normalize("ct_assurance", payload([(20, 1.0, 0.8, 30.0)]))
        self.assertEqual(envelope.payload["_contract"], "v1")

    def test_input_payload_not_mutated(self):
        original = payload([(20, 1.0, 0.8, 7.5)])
        normalize("ct_assurance", original)
        self.assertEqual(original["segments"][0]["temperature_c"], 7.5)
        self.assertNotIn("_temperature_override", original)


class ReleaseDecision(unittest.TestCase):
    def setUp(self):
        self.service = AquaFlowService()

    def test_high_temperature_boundary_releases(self):
        # raw CT 16.0 < required 20.0: legacy (forced 20C) would hold;
        # at 30C the compensated CT is 32.0 and must release.
        result = self.service.run_workflow("ct_assurance", payload([(20, 1.0, 0.8, 30.0)]))
        self.assertEqual(result["decision"], "release")
        self.assertAlmostEqual(result["value"], 32.0)

    def test_low_temperature_boundary_holds(self):
        # raw CT 24.0 >= required 20.0: legacy (forced 20C) would release;
        # at 10C the compensated CT is 12.0 and must hold.
        result = self.service.run_workflow(
            "ct_assurance", payload([(30, 1.0, 0.8, 10.0)], required=20.0)
        )
        self.assertEqual(result["decision"], "hold")
        self.assertAlmostEqual(result["value"], 12.0)

    def test_reference_temperature_behavior_unchanged(self):
        released = self.service.run_workflow(
            "ct_assurance", payload([(20, 1.0, 0.8, 20.0)], required=16.0)
        )
        self.assertEqual(released["decision"], "release")
        self.assertAlmostEqual(released["value"], 16.0)
        held = self.service.run_workflow(
            "ct_assurance", payload([(20, 1.0, 0.8, 20.0)], required=16.1)
        )
        self.assertEqual(held["decision"], "hold")

    def test_low_dose_holds_even_with_ample_ct(self):
        result = self.service.run_workflow(
            "ct_assurance", payload([(60, 2.0, 1.0, 30.0)], mg_l=0.1, low=0.2)
        )
        self.assertEqual(result["decision"], "hold")
        self.assertFalse(result["evidence"]["residual_ok"])

    def test_high_dose_holds_even_with_ample_ct(self):
        result = self.service.run_workflow(
            "ct_assurance", payload([(60, 2.0, 1.0, 30.0)], mg_l=4.5, high=4.0)
        )
        self.assertEqual(result["decision"], "hold")
        self.assertFalse(result["evidence"]["residual_ok"])

    def test_dose_at_limits_still_releases(self):
        for mg_l in (0.2, 4.0):
            result = self.service.run_workflow(
                "ct_assurance", payload([(20, 1.0, 0.8, 30.0)], mg_l=mg_l)
            )
            self.assertEqual(result["decision"], "release")

    def test_compliant_api_uses_compensation(self):
        self.assertTrue(compliant([Segment(20, 1.0, 0.8, 30.0)], 20.0))
        self.assertFalse(compliant([Segment(30, 1.0, 0.8, 10.0)], 20.0))
        self.assertTrue(compliant([Segment(20, 1.0, 0.8, 20.0)], 16.0))


class AuditEvidence(unittest.TestCase):
    def test_evidence_records_temperature_compensation(self):
        result = AquaFlowService().run_workflow(
            "ct_assurance", payload([(20, 1.0, 0.8, 30.0), (10, 1.0, 1.0, 10.0)])
        )
        evidence = result["evidence"]
        self.assertEqual(evidence["temperatures_c"], [30.0, 10.0])
        self.assertEqual(evidence["temperature_factors"], [2.0, 0.5])
        self.assertEqual(evidence["reference_temperature_c"], 20.0)
        self.assertAlmostEqual(evidence["ct"], 37.0)
        self.assertTrue(evidence["residual_ok"])

    def test_audit_metadata_present(self):
        received = datetime(2026, 10, 2, tzinfo=timezone.utc)
        result = AquaFlowService().run_workflow(
            "ct_assurance", payload([(20, 1.0, 0.8, 30.0)]), received_at=received
        )
        self.assertEqual(result["workflow"], "ct_assurance")
        self.assertEqual(result["audit"]["contract"], "v1")
        self.assertEqual(result["audit"]["received_at"], received.isoformat())


if __name__ == "__main__":
    unittest.main()
