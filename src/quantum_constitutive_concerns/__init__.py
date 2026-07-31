"""Executable examples for constitutive concerns in quantum software."""

from quantum_constitutive_concerns.backend_adaptation import (
    analyze_backend_adaptation,
    build_two_qubit_grover_circuit,
)
from quantum_constitutive_concerns.zne_error_mitigation import (
    analyze_zne_error_mitigation,
    classical_fidelity,
    grover_three_qubits,
)

__all__ = [
    "analyze_backend_adaptation",
    "analyze_zne_error_mitigation",
    "build_two_qubit_grover_circuit",
    "classical_fidelity",
    "grover_three_qubits",
]

__version__ = "1.0.0"
