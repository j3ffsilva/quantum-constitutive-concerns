"""Structural tests for the backend-adaptation example."""

from __future__ import annotations

import unittest

from qiskit.quantum_info import Statevector

from quantum_constitutive_concerns import (
    analyze_backend_adaptation,
    build_two_qubit_grover_circuit,
)


class BackendAdaptationTests(unittest.TestCase):
    def test_logical_circuit_is_transpiled_to_expected_native_form(self) -> None:
        result = analyze_backend_adaptation()
        self.assertEqual(result["logical"]["size"], 16)
        self.assertEqual(result["native"]["size"], 13)
        self.assertEqual(
            result["native"]["operations"],
            {"sx": 6, "rz": 5, "cz": 2},
        )

    def test_each_target_is_marked_by_the_oracle(self) -> None:
        for target in range(4):
            with self.subTest(target=target):
                probabilities = Statevector.from_instruction(
                    build_two_qubit_grover_circuit(target)
                ).probabilities()
                self.assertAlmostEqual(probabilities[target], 1.0)

    def test_invalid_target_is_rejected(self) -> None:
        for target in (-1, 4, True):
            with self.subTest(target=target):
                with self.assertRaises(ValueError):
                    build_two_qubit_grover_circuit(target)


if __name__ == "__main__":
    unittest.main()
