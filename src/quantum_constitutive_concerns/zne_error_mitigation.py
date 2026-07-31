"""Zero-noise extrapolation example for a constitutive quantum concern.

The module reports both success probability and classical distribution
fidelity, keeping these distinct quantities explicit in the artifact.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

os.environ.setdefault("MPLCONFIGDIR", str(Path(".cache/matplotlib").resolve()))

import numpy as np
from mitiq.zne.scaling import fold_global
from qiskit import ClassicalRegister, QuantumCircuit, transpile
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime.fake_provider import FakeFez


DEFAULT_SHOTS = 32_768
DEFAULT_SEED_TRANSPILER = 6
SEED_SIMULATOR = 54_321
SCALE_FACTORS = (1.0, 2.0, 3.0)
DEFAULT_TARGET = "000"


def grover_three_qubits(
    target: str = DEFAULT_TARGET,
    iterations: int = 2,
) -> QuantumCircuit:
    """Return a three-qubit Grover search circuit for a marked basis state."""
    if len(target) != 3 or set(target) - {"0", "1"}:
        raise ValueError("target must be a three-character binary string")

    circuit = QuantumCircuit(3)
    circuit.h(range(3))
    # Qiskit labels bit strings in q_2 q_1 q_0 order.
    target_by_qubit = target[::-1]

    for _ in range(iterations):
        # Map the marked state to |111>, apply a CCZ, then uncompute.
        for qubit, bit in enumerate(target_by_qubit):
            if bit == "0":
                circuit.x(qubit)
        circuit.h(2)
        circuit.ccx(0, 1, 2)
        circuit.h(2)
        for qubit, bit in enumerate(target_by_qubit):
            if bit == "0":
                circuit.x(qubit)

        # Grover diffuser.
        circuit.h(range(3))
        circuit.x(range(3))
        circuit.h(2)
        circuit.ccx(0, 1, 2)
        circuit.h(2)
        circuit.x(range(3))
        circuit.h(range(3))

    return circuit


def probabilities_from_counts(counts: dict[str, int], shots: int) -> np.ndarray:
    """Return a dense probability vector ordered by integer bit-string value."""
    probabilities = np.zeros(8, dtype=float)
    for bit_string, count in counts.items():
        probabilities[int(bit_string.replace(" ", ""), 2)] = count / shots
    return probabilities


def classical_fidelity(left: np.ndarray, right: np.ndarray) -> float:
    """Squared Bhattacharyya coefficient, matching common fidelity convention."""
    return float(np.square(np.sum(np.sqrt(left * right))))


def measure(
    circuit: QuantumCircuit,
    logical_output_qubits: list[int],
) -> QuantumCircuit:
    measured = circuit.copy()
    classical = ClassicalRegister(3, "result")
    measured.add_register(classical)
    for logical_index, physical_index in enumerate(logical_output_qubits):
        measured.measure(physical_index, classical[logical_index])
    return measured


def run_distribution(
    simulator: AerSimulator,
    circuit: QuantumCircuit,
    *,
    seed: int,
    logical_output_qubits: list[int],
    shots: int,
) -> np.ndarray:
    job = simulator.run(
        measure(circuit, logical_output_qubits),
        shots=shots,
        seed_simulator=seed,
    )
    return probabilities_from_counts(job.result().get_counts(), shots)


def serializable_distribution(values: np.ndarray) -> dict[str, float]:
    return {format(index, "03b"): float(value) for index, value in enumerate(values)}


def analyze_zne_error_mitigation(
    *,
    target: str = DEFAULT_TARGET,
    shots: int = DEFAULT_SHOTS,
    seed_transpiler: int = DEFAULT_SEED_TRANSPILER,
) -> dict[str, Any]:
    """Run distribution-level ZNE and return parameters, circuits, and metrics."""
    backend = FakeFez()
    logical = grover_three_qubits(target)
    ideal = np.abs(Statevector.from_instruction(logical).data) ** 2

    native = transpile(
        logical,
        backend=backend,
        optimization_level=3,
        seed_transpiler=seed_transpiler,
    )
    logical_output_qubits = native.layout.final_index_layout(
        filter_ancillas=True
    )
    # FakeFez has 156 qubits even though this experiment activates only a
    # small connected subset. Matrix-product-state simulation avoids allocating
    # a dense 2**156 statevector for the inactive wires.
    simulator = AerSimulator.from_backend(
        backend,
        method="matrix_product_state",
        enable_truncation=True,
    )

    folded_circuits = [
        native if scale == 1.0 else fold_global(native, scale_factor=scale)
        for scale in SCALE_FACTORS
    ]
    # Folding native gates introduces their inverse representations (for
    # example, ``sxdg``). Translate those back to the backend basis without
    # optimization, which could otherwise cancel the noise-amplifying folds.
    scaled_circuits = [
        transpile(
            circuit,
            basis_gates=["cz", "rz", "sx", "x"],
            optimization_level=0,
        )
        for circuit in folded_circuits
    ]
    noisy_distributions = [
        run_distribution(
            simulator,
            circuit,
            seed=SEED_SIMULATOR + index,
            logical_output_qubits=logical_output_qubits,
            shots=shots,
        )
        for index, circuit in enumerate(scaled_circuits)
    ]

    # Linear ZNE independently extrapolates every outcome probability to zero
    # noise. This makes the bridge from scalar extrapolation to a distribution
    # explicit. Clipping and normalization are reported because unconstrained
    # linear fits need not produce a valid probability distribution.
    raw_zne = np.array(
        [
            np.polyfit(SCALE_FACTORS, outcome_values, deg=1)[1]
            for outcome_values in np.asarray(noisy_distributions).T
        ]
    )
    clipped_zne = np.clip(raw_zne, 0.0, None)
    normalized_zne = clipped_zne / clipped_zne.sum()
    fidelity_by_scale = [
        classical_fidelity(distribution, ideal)
        for distribution in noisy_distributions
    ]
    # This reproduces a plausible origin of the paper's 0.988 value, but is
    # only a diagnostic: computing F at every scale requires access to the
    # ideal target distribution and does not itself reconstruct a mitigated
    # output distribution.
    direct_fidelity_intercept = float(
        np.polyfit(SCALE_FACTORS, fidelity_by_scale, deg=1)[1]
    )

    target_index = int(target, 2)
    result: dict[str, Any] = {
        "versions": {
            "qiskit": __import__("qiskit").__version__,
            "qiskit_aer": __import__("qiskit_aer").__version__,
            "qiskit_ibm_runtime": __import__("qiskit_ibm_runtime").__version__,
            "mitiq": __import__("mitiq").__version__,
        },
        "parameters": {
            "shots": shots,
            "seed_transpiler": seed_transpiler,
            "seed_simulator_base": SEED_SIMULATOR,
            "scale_factors": SCALE_FACTORS,
            "target": target,
        },
        "circuits": {
            "logical_operations": logical.count_ops(),
            "native_operations": native.count_ops(),
            "native_size": native.size(),
            "native_depth": native.depth(),
            "logical_output_qubits": logical_output_qubits,
            "scaled_sizes": [circuit.size() for circuit in scaled_circuits],
            "scaled_depths": [circuit.depth() for circuit in scaled_circuits],
            "scaled_operations": [
                circuit.count_ops() for circuit in scaled_circuits
            ],
        },
        "distributions": {
            "ideal": serializable_distribution(ideal),
            "noisy_by_scale": [
                serializable_distribution(distribution)
                for distribution in noisy_distributions
            ],
            "zne_raw_linear_intercepts": serializable_distribution(raw_zne),
            "zne_clipped_normalized": serializable_distribution(normalized_zne),
        },
        "metrics": {
            "ideal_success_probability": float(ideal[target_index]),
            "noisy_success_probability": float(
                noisy_distributions[0][target_index]
            ),
            "zne_success_probability": float(normalized_zne[target_index]),
            "noisy_distribution_fidelity": classical_fidelity(
                noisy_distributions[0], ideal
            ),
            "zne_distribution_fidelity": classical_fidelity(
                normalized_zne, ideal
            ),
            "distribution_fidelity_by_scale": fidelity_by_scale,
            "direct_linear_extrapolation_of_fidelity_diagnostic": (
                direct_fidelity_intercept
            ),
            "raw_zne_sum": float(raw_zne.sum()),
            "raw_zne_minimum": float(raw_zne.min()),
        },
    }
    return result
