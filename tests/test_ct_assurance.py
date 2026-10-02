import unittest

from aquaflow.api import AquaFlowService
from aquaflow.treatment.chlorine_ct import REFERENCE_TEMPERATURE_C, Segment, effective_ct, segment_ct, temperature_factor
from aquaflow.workflow_service import WorkflowService


def payload(temperature_c, required, mg_l=1.0, minutes=20.0, residual=1.0, baffling=0.8):
    return {
        "segments": [{
            "minutes": minutes,
            "residual": residual,
            "baffling": baffling,
            "temperature_c": temperature_c,
        }],
        "dose": {"mg_l": mg_l, "low_limit": 0.5, "high_limit": 2.0},
        "required": required,
    }


class TemperatureFactorTest(unittest.TestCase):
    def test_reference_is_unity(self):
        self.assertEqual(temperature_factor(REFERENCE_TEMPERATURE_C), 1.0)

    def test_doubles_every_ten_degrees(self):
        self.assertAlmostEqual(temperature_factor(30.0), 2.0)
        self.assertAlmostEqual(temperature_factor(10.0), 0.5)
        self.assertAlmostEqual(temperature_factor(0.0), 0.25)


class EffectiveCtTest(unittest.TestCase):
    def test_reference_temperature_behavior_unchanged(self):
        # 20 * 1.0 * 0.8 * 1.0 = 16, exactly as before compensation
        self.assertAlmostEqual(effective_ct([Segment(20, 1.0, 0.8, 20.0)]), 16.0)
        self.assertTrue(AquaFlowService().ct([Segment(20, 1, 0.8, 20)], 10))

    def test_cold_segment_earns_less_credit(self):
        self.assertAlmostEqual(segment_ct(Segment(20, 1.0, 0.8, 5.0)), 16.0 * 2 ** (-1.5))

    def test_warm_segment_earns_more_credit(self):
        self.assertAlmostEqual(segment_ct(Segment(20, 1.0, 0.8, 25.0)), 16.0 * 2 ** 0.5)

    def test_segments_keep_their_own_temperatures(self):
        rows = [Segment(10, 1.0, 1.0, 10.0), Segment(10, 1.0, 1.0, 30.0)]
        # 10 * 0.5 + 10 * 2.0 = 25
        self.assertAlmostEqual(effective_ct(rows), 25.0)

    def test_illegal_segment_rejected(self):
        for bad in (
            Segment(0, 1.0, 0.8, 20.0),       # non-positive contact time
            Segment(20, -0.1, 0.8, 20.0),     # negative residual
            Segment(20, 1.0, 0.0, 20.0),      # baffling out of range
            Segment(20, 1.0, 1.1, 20.0),
            Segment(20, 1.0, 0.8, 0.0),       # water freezing / boiling
            Segment(20, 1.0, 0.8, 100.0),
        ):
            with self.assertRaises(ValueError):
                effective_ct([bad])


class CtAssuranceWorkflowTest(unittest.TestCase):
    def setUp(self):
        self.service = WorkflowService()

    def test_normalization_preserves_temperature(self):
        result = self.service.run("ct_assurance", payload(5.0, 10))
        self.assertEqual(result["audit"]["contract"], "v1")
        self.assertNotIn("_temperature_override", result["audit"]["input_snapshot"])
        self.assertEqual(result["evidence"]["segments"][0]["temperature_c"], 5.0)
        self.assertAlmostEqual(
            result["evidence"]["segments"][0]["temperature_factor"], 2 ** (-1.5)
        )

    def test_cold_segment_holds_at_boundary(self):
        # Reference-temperature CT is 16; cold (5 C) CT is ~5.66. Only
        # temperature compensation distinguishes release (required 10) from hold.
        result = self.service.run("ct_assurance", payload(5.0, 10))
        self.assertEqual(result["decision"], "hold")
        self.assertFalse(result["evidence"]["ct_ok"])
        self.assertTrue(result["evidence"]["residual_ok"])
        self.assertAlmostEqual(result["value"], 16.0 * 2 ** (-1.5))

    def test_warm_segment_releases_at_boundary(self):
        # At 25 C the CT is ~22.6; required 20 fails at reference but passes warm.
        result = self.service.run("ct_assurance", payload(25.0, 20))
        self.assertEqual(result["decision"], "release")
        self.assertTrue(result["evidence"]["ct_ok"])
        self.assertGreater(result["value"], 20.0)

    def test_reference_temperature_boundary_still_releases(self):
        result = self.service.run("ct_assurance", payload(20.0, 16.0))
        self.assertEqual(result["decision"], "release")
        self.assertEqual(result["evidence"]["segments"][0]["temperature_factor"], 1.0)

    def test_reference_temperature_just_below_still_holds(self):
        result = self.service.run("ct_assurance", payload(20.0, 16.0001))
        self.assertEqual(result["decision"], "hold")

    def test_low_residual_independent_of_temperature(self):
        result = self.service.run("ct_assurance", payload(20.0, 1, mg_l=0.4))
        self.assertEqual(result["decision"], "hold")
        self.assertTrue(result["evidence"]["residual_low"])
        self.assertFalse(result["evidence"]["residual_high"])
        self.assertFalse(result["evidence"]["residual_ok"])
        # CT itself is fine; the dose range is what holds the water.
        self.assertTrue(result["evidence"]["ct_ok"])

    def test_high_residual_independent_of_temperature(self):
        result = self.service.run("ct_assurance", payload(20.0, 1, mg_l=2.5))
        self.assertEqual(result["decision"], "hold")
        self.assertTrue(result["evidence"]["residual_high"])
        self.assertFalse(result["evidence"]["residual_low"])

    def test_warm_ct_cannot_cure_out_of_range_dose(self):
        result = self.service.run("ct_assurance", payload(30.0, 1, mg_l=3.0))
        self.assertEqual(result["decision"], "hold")
        self.assertFalse(result["evidence"]["residual_ok"])
        self.assertTrue(result["evidence"]["ct_ok"])

    def test_mixed_temperature_segments_release(self):
        p = {
            "segments": [
                {"minutes": 10, "residual": 1.0, "baffling": 1.0, "temperature_c": 10.0},
                {"minutes": 10, "residual": 1.0, "baffling": 1.0, "temperature_c": 30.0},
            ],
            "dose": {"mg_l": 1.0, "low_limit": 0.5, "high_limit": 2.0},
            "required": 25.0,
        }
        result = self.service.run("ct_assurance", p)
        self.assertEqual(result["decision"], "release")
        self.assertAlmostEqual(result["value"], 25.0)

    def test_illegal_contact_segment_rejected(self):
        p = payload(20.0, 1)
        p["segments"][0]["baffling"] = 1.5
        with self.assertRaises(ValueError):
            self.service.run("ct_assurance", p)

    def test_segment_missing_temperature_rejected(self):
        p = payload(20.0, 1)
        del p["segments"][0]["temperature_c"]
        with self.assertRaises(ValueError):
            self.service.run("ct_assurance", p)

    def test_illegal_temperature_rejected(self):
        with self.assertRaises(ValueError):
            self.service.run("ct_assurance", payload(-5.0, 1))

    def test_illegal_dose_envelope_rejected(self):
        p = payload(20.0, 1)
        p["dose"]["low_limit"] = 2.0
        with self.assertRaises(ValueError):
            self.service.run("ct_assurance", p)

    def test_audit_evidence_records_temperature_and_decision(self):
        result = self.service.run("ct_assurance", payload(5.0, 10))
        audit = result["audit"]
        self.assertEqual(audit["input_snapshot"]["segments"][0]["temperature_c"], 5.0)
        self.assertIn("segments", audit["evidence_keys"])
        self.assertIn("ct_ok", audit["evidence_keys"])
        self.assertEqual(result["evidence"]["reference_temperature_c"], REFERENCE_TEMPERATURE_C)


if __name__ == "__main__":
    unittest.main()
