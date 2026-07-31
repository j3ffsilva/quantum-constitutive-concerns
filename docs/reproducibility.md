# Reproducibility Notes

This document describes the environment, parameters, procedures, expected
outputs, and limitations of the executable examples associated with the paper
“Beyond Orthogonality: Constitutive Concerns in Quantum Software”.

## Environment

The project targets Python 3.12. Direct dependency constraints are declared in
`pyproject.toml`, while `requirements-lock.txt` fixes the complete validated
runtime environment, including transitive dependencies. The isolated
`setuptools` build backend is also fixed in `pyproject.toml`. The principal
runtime packages are:

- Qiskit 2.4.2;
- Qiskit Aer 0.17.2;
- Qiskit IBM Runtime 0.47.0;
- Mitiq 1.0.0;
- PLY 3.11.

Install the package and its dependencies with:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python -m pip install --no-deps -e .
```

## Backend adaptation

The backend-adaptation example builds the two-qubit Grover circuit represented
by Listing 1 of the paper with `target=0`. It transpiles the circuit against
`FakeFez` with:

- optimization level: 3;
- transpiler seed: 6.

Run:

```sh
.venv/bin/python -m quantum_constitutive_concerns \
  backend-adaptation \
  --output results/backend_adaptation.json
```

The selected configuration produces 16 logical operations and 13 native-basis
operations (`sx`: 6, `rz`: 5, `cz`: 2). This is a result for the declared
target, optimization level, and seed; it is not a claim that backend adaptation
always reduces operation count. These are transpiled instructions, not physical
pulses; in particular, `rz` may be implemented virtually.

## ZNE error mitigation

The ZNE example uses a three-qubit Grover search with two iterations and the
marked state `000`. Its fixed parameters are:

- backend snapshot: `FakeFez`;
- shots: 32,768;
- transpiler seed: 6;
- simulator seeds: 54,321, 54,322, and 54,323;
- nominal folding factors: 1, 2, and 3;
- extrapolation: linear, independently for every outcome probability;
- fidelity:
  $(\sum_i \sqrt{p_iq_i})^2$.

Run:

```sh
.venv/bin/python -m quantum_constitutive_concerns \
  zne-error-mitigation \
  --output results/zne_error_mitigation.json
```

For each nominal scale, the experiment samples a complete output distribution.
It linearly extrapolates every outcome probability to zero noise, clips possible
negative values, and normalizes the resulting vector. The classical fidelity of
that mitigated distribution is then computed against the ideal distribution.

The expected point estimates are:

- fidelity without mitigation: 0.952961;
- fidelity after distribution-level ZNE: 0.977236;
- ideal-distribution fidelity: 1;
- direct extrapolation of the fidelity scalar: 0.986777.

The last quantity is retained as a diagnostic only. It requires access to the
ideal distribution and does not reconstruct a mitigated output distribution.

## Nominal folding and native-basis size

Mitiq applies global folding at nominal factors 1, 2, and 3; the scale-1 circuit
is unchanged, while larger factors insert inverse pairs globally and, when
needed, partially. Inverse gates are then translated back to the Fez native
basis. In particular, the inverse of `sx` requires a multi-instruction native
decomposition. The resulting native operation counts are 191, 815, and 881
rather than exact multiples of 1, 2, and 3. The fit therefore uses nominal
folding scales, not measured physical-noise multipliers.

## Verification

Fast tests:

```sh
.venv/bin/python -m unittest discover -s tests -p 'test_*.py'
```

Full command-line verification:

```sh
RUN_FULL_REPRODUCTION=1 .venv/bin/python -m unittest discover \
  -s tests -p 'test_reference_results.py'
```

This integration test reproduces both examples and recursively compares every
reported field with the versioned JSON files under `results/`. Logical
structure, parameters, versions, gate-accounting invariants, and mitigation
outcomes are checked directly. Physical-circuit depths and sizes produced by
the Qiskit transpiler use a 5% tolerance, and physical gate counts use 10%:
with the same versions and seed, equivalent decompositions can vary slightly
across processor architectures. Floating-point distributions use an absolute
tolerance of 0.01, and derived metrics use 0.005. The test also verifies the entangling-gate
counts, consistency between gate counts and circuit sizes, monotonic growth
under folding, and the inequalities around the operational threshold
$\tau=0.97$. It is mandatory in continuous integration. The same full
verification is also provided by `notebooks/constitutive_concerns.ipynb`.

## Limitations

- `FakeFez` is a calibration-derived simulator snapshot, not live hardware.
- Point estimates depend on the declared model, package versions, seeds, and
  number of shots.
- The operational threshold $\tau=0.97$ is specific to the illustrative
  example, not universal.
- The ideal distribution is available because this is a benchmark. It is not
  generally available for production problems, so a real validity criterion
  may require partial properties, analytical bounds, calibration, or dynamic
  evidence.
- The examples cover one superconducting backend model and one mitigation
  strategy.
- The artifact illustrates the proposed categories; it does not empirically
  validate their prevalence or generality.
