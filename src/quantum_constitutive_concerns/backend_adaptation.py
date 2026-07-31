"""Backend-adaptation example for a constitutive quantum concern."""

from __future__ import annotations

from typing import Any

from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime.fake_provider import FakeFez


def build_two_qubit_grover_circuit(target: int = 0) -> QuantumCircuit:
    """Build the executable Qiskit circuit represented by Listing 1."""
    if not isinstance(target, int) or isinstance(target, bool) or not 0 <= target <= 3:
        raise ValueError("target must be an integer between 0 and 3")

    circuit = QuantumCircuit(2)
    circuit.h(range(2))

    # Qiskit labels two-qubit basis states in q_1 q_0 order. Map the
    # requested state to |11>, apply the phase oracle, then uncompute.
    target_by_qubit = f"{target:02b}"[::-1]
    for qubit, bit in enumerate(target_by_qubit):
        if bit == "0":
            circuit.x(qubit)
    circuit.cz(0, 1)
    for qubit, bit in enumerate(target_by_qubit):
        if bit == "0":
            circuit.x(qubit)

    # Grover diffuser.
    circuit.h(range(2))
    circuit.x(range(2))
    circuit.cz(0, 1)
    circuit.x(range(2))
    circuit.h(range(2))
    return circuit


def analyze_backend_adaptation(
    *,
    target: int = 0,
    optimization_level: int = 3,
    seed_transpiler: int = 6,
) -> dict[str, Any]:
    """Transpile the logical circuit and report its logical and native forms."""
    backend = FakeFez()
    logical = build_two_qubit_grover_circuit(target)
    native = transpile(
        logical,
        backend=backend,
        optimization_level=optimization_level,
        seed_transpiler=seed_transpiler,
    )
    return {
        "versions": {
            "qiskit": __import__("qiskit").__version__,
            "qiskit_ibm_runtime": __import__(
                "qiskit_ibm_runtime"
            ).__version__,
        },
        "parameters": {
            "backend": backend.name,
            "backend_version": backend.backend_version,
            "target": target,
            "optimization_level": optimization_level,
            "seed_transpiler": seed_transpiler,
        },
        "logical": {
            "size": logical.size(),
            "depth": logical.depth(),
            "operations": logical.count_ops(),
        },
        "native": {
            "size": native.size(),
            "depth": native.depth(),
            "operations": native.count_ops(),
            "logical_output_qubits": native.layout.final_index_layout(
                filter_ancillas=True
            ),
        },
    }
