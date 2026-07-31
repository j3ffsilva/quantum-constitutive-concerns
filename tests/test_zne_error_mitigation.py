"""Fast mathematical tests for the ZNE example."""

from __future__ import annotations

import unittest

import numpy as np
from qiskit.quantum_info import Statevector

from quantum_constitutive_concerns import (
    classical_fidelity,
    grover_three_qubits,
)


class ZneErrorMitigationTests(unittest.TestCase):
    def test_ideal_grover_distribution_and_fidelity(self) -> None:
        circuit = grover_three_qubits("000")
        distribution = np.abs(Statevector.from_instruction(circuit).data) ** 2
        self.assertAlmostEqual(distribution[0], 0.9453125)
        self.assertAlmostEqual(
            classical_fidelity(distribution, distribution),
            1.0,
        )


if __name__ == "__main__":
    unittest.main()
