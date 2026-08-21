import math
import unittest

from app import simulation_payload, twin_simulation_payload
from drug_discovery import rank_candidates, rank_twin_profiles
from simulator import simulate


class SimulatorTests(unittest.TestCase):
    def test_hadamard_creates_equal_superposition(self):
        result = simulate(1, [{"gate": "H", "qubit": 0}])
        self.assertAlmostEqual(result.probabilities[0], 0.5)
        self.assertAlmostEqual(result.probabilities[1], 0.5)

    def test_bell_state_is_entangled(self):
        result = simulate(
            2,
            [
                {"gate": "H", "qubit": 0},
                {"gate": "CX", "control": 0, "target": 1},
            ],
        )
        self.assertAlmostEqual(result.probabilities[0], 0.5)
        self.assertAlmostEqual(result.probabilities[3], 0.5)
        self.assertAlmostEqual(result.probabilities[1], 0)
        self.assertAlmostEqual(result.probabilities[2], 0)

    def test_ry_pi_flips_zero_to_one(self):
        result = simulate(1, [{"gate": "RY", "qubit": 0, "angle": math.pi}])
        self.assertAlmostEqual(result.probabilities[1], 1)

    def test_invalid_gate_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unsupported gate"):
            simulate(1, [{"gate": "NOPE", "qubit": 0}])

    def test_api_payload_contains_measurements(self):
        payload = simulation_payload(
            {"num_qubits": 1, "gates": [{"gate": "X", "qubit": 0}], "shots": 20}
        )
        self.assertEqual(payload["counts"], {"1": 20})
        self.assertEqual(payload["states"][1]["probability"], 1.0)

    def test_twin_engine_compares_two_circuits(self):
        payload = twin_simulation_payload(
            {
                "left": {
                    "num_qubits": 1,
                    "gates": [{"gate": "H", "qubit": 0}],
                    "shots": 20,
                },
                "right": {
                    "num_qubits": 1,
                    "gates": [{"gate": "X", "qubit": 0}],
                    "shots": 20,
                },
            }
        )
        self.assertAlmostEqual(payload["comparison"]["similarity"], 0.5)
        self.assertAlmostEqual(
            payload["comparison"]["total_variation_distance"], 0.5
        )

    def test_twin_engine_requires_matching_qubits(self):
        with self.assertRaisesRegex(ValueError, "same number of qubits"):
            twin_simulation_payload(
                {
                    "left": {"num_qubits": 1, "gates": []},
                    "right": {"num_qubits": 2, "gates": []},
                }
            )

    def test_drug_discovery_ranks_fictional_candidates(self):
        payload = rank_candidates(
            {
                "desired_profile": {
                    "D2": 0.7,
                    "5-HT2A": 0.8,
                    "NMDA": 0.5,
                    "M1": 0.5,
                },
                "safety_weight": 0.35,
            }
        )
        self.assertEqual(len(payload["candidates"]), 5)
        self.assertEqual(payload["candidates"][0]["rank"], 1)
        self.assertGreaterEqual(
            payload["candidates"][0]["score"], payload["candidates"][-1]["score"]
        )
        self.assertIn("fictional compounds", payload["disclaimer"])

    def test_drug_discovery_rejects_invalid_weight(self):
        with self.assertRaisesRegex(ValueError, "between 0 and 1"):
            rank_candidates({"safety_weight": 1.5})

    def test_drug_twin_compares_two_rankings(self):
        payload = rank_twin_profiles(
            {
                "left": {
                    "desired_profile": {"D2": 0.8, "5-HT2A": 0.8},
                    "safety_weight": 0.2,
                },
                "right": {
                    "desired_profile": {"NMDA": 0.8, "M1": 0.8},
                    "safety_weight": 0.7,
                },
            }
        )
        self.assertEqual(len(payload["comparison"]["candidates"]), 5)
        self.assertGreaterEqual(payload["comparison"]["rank_correlation"], -1)
        self.assertLessEqual(payload["comparison"]["rank_correlation"], 1)

    def test_drug_twin_requires_both_profiles(self):
        with self.assertRaisesRegex(ValueError, "left and right"):
            rank_twin_profiles({"left": {}})


if __name__ == "__main__":
    unittest.main()
