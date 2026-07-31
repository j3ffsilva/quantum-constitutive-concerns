# Quantum Constitutive Concerns

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/j3ffsilva/quantum-constitutive-concerns/blob/main/notebooks/constitutive_concerns.ipynb)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Research artifact for the WQSE 2026 paper **“Além da Ortogonalidade:
Preocupações Constitutivas em Software Quântico”** (*Beyond Orthogonality:
Constitutive Concerns in Quantum Software*).

The paper distinguishes ordinary crosscutting concerns from **constitutive
concerns**: execution concerns whose absence makes a quantum computation
unexecutable on its target backend or unable to satisfy an operational validity
criterion. This repository provides executable examples for the two initial
categories proposed in the paper:

- **constitutive of executability:** adapting a logical circuit to a target
  backend;
- **constitutive of result validity:** mitigating noise through
  distribution-level zero-noise extrapolation (ZNE).

## What is implemented

The executable code uses Qiskit, Qiskit Aer, the `FakeFez` backend snapshot, and
Mitiq to analyze:

1. a two-qubit Grover circuit whose 16 logical operations are transpiled into
   13 native-basis operations for the selected target and seed;
2. a three-qubit Grover circuit whose classical distribution fidelity changes
   from approximately 0.953 without mitigation to 0.977 after ZNE.

The decorators `@ErrorMitigation`, `@BackendAdapt`, and `@Explore` shown in the
paper are **conceptual notation**, not existing Qiskit APIs and not implemented
by this artifact.

## Run in Google Colab

The quickest path is the
[executable notebook](notebooks/constitutive_concerns.ipynb), which installs the
pinned environment, runs both examples, compares their outputs with the
versioned reference results, and executes the automated tests.

The notebook requires only a standard CPU runtime. No IBM Quantum account or
live quantum hardware is required.

## Local installation

Python 3.12 is required.

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python -m pip install --no-deps -e .
```

## Command-line interface

Backend adaptation:

```sh
.venv/bin/python -m quantum_constitutive_concerns \
  backend-adaptation \
  --output results/backend_adaptation.json
```

ZNE error mitigation:

```sh
.venv/bin/python -m quantum_constitutive_concerns \
  zne-error-mitigation \
  --output results/zne_error_mitigation.json
```

The commands print structured JSON and optionally persist it through
`--output`.

## Expected results

| Example | Observation |
|---|---:|
| Logical circuit size | 16 operations |
| Native circuit size after backend adaptation | 13 operations |
| Fidelity without mitigation | 0.952961 |
| Fidelity after distribution-level ZNE | 0.977236 |
| Direct-fidelity extrapolation, diagnostic only | 0.986777 |
| Native operation counts at nominal scales 1, 2, and 3 | 191, 815, 881 |

For the illustrative operational threshold used in the paper,
$0.952961 < \tau=0.97 \leq 0.977236$.

## Tests

```sh
.venv/bin/python -m unittest discover -s tests -p 'test_*.py'
```

The tests check the ideal Grover distribution and the structural invariant of
the backend-adaptation example. The full integration test reproduces both
examples and compares every reported field with the versioned results. Logical
structure, parameters, versions, gate-accounting invariants, and mitigation
outcomes are checked directly. Physical-circuit depths and sizes produced by
the Qiskit transpiler use a 5% tolerance, and physical gate counts use 10%,
because equivalent decompositions can differ across processor architectures.
Statistical estimates use explicit tolerances:

```sh
RUN_FULL_REPRODUCTION=1 .venv/bin/python -m unittest discover \
  -s tests -p 'test_reference_results.py'
```

The full integration test is mandatory in continuous integration and is also
performed by the notebook.

## Project structure

```text
src/quantum_constitutive_concerns/
  backend_adaptation.py
  zne_error_mitigation.py
  cli.py
tests/
results/
notebooks/
docs/
pyproject.toml
requirements-lock.txt
```

- `src/` contains reusable domain logic and the command-line boundary.
- `tests/` contains fast structural and mathematical checks.
- `results/` contains versioned reference outputs.
- `notebooks/` provides an executable, explanatory interface.
- `docs/reproducibility.md` records parameters, procedures, and limitations.
- `pyproject.toml` defines the package and its direct dependencies.
- `requirements-lock.txt` fixes the complete validated runtime environment.

## Reproducibility and limitations

All direct and transitive package versions, seeds, shots, target state, and
nominal folding factors are fixed. “Native operations” are transpiled
instructions in the backend basis, not a count of physical pulses; for example,
`rz` may be virtual. The experiments use simulation with a calibration snapshot
rather than live hardware, and they illustrate the proposed taxonomy rather
than validate its generality across algorithms and platforms. See
[the reproducibility notes](docs/reproducibility.md) for details.

## Paper template

The bundled `acmart.cls` and `ACM-Reference-Format.bst` files are the adapted
ACM-like versions distributed in the official
[CBSoft 2026 author kit](https://cbsoft.sbc.org.br/2026/Template_para_eventos_do_CBSoft.zip).
The source follows the kit's camera-ready checklist: it omits the ACM reference
block and CCS concepts, so the two corresponding class warnings are expected.

## How to cite

If you use the definition, analysis, or experimental results presented here,
please cite the associated paper. If you also reuse or adapt the source code,
notebook, reference results, or reproducibility workflow, please cite both the
paper and this software artifact.

### Accepted paper

```bibtex
@inproceedings{silva2026constitutive,
  author    = {Jefferson de Oliveira Silva and Bryan Kano Ferreira and
               Murilo Zanini de Carvalho and Fabiana Naomi Iegawa},
  title     = {Além da Ortogonalidade: Preocupações Constitutivas em
               Software Quântico},
  booktitle = {Proceedings of the 1st Brazilian Workshop on Quantum
               Software Engineering (WQSE 2026)},
  year      = {2026},
  address   = {São Paulo, SP, Brazil},
  note      = {Accepted for publication}
}
```

The paper entry will be updated when the proceedings publish its final page
range and persistent identifier.

### Software artifact

```bibtex
@misc{silva2026artifact,
  author       = {Jefferson de Oliveira Silva and Bryan Kano Ferreira and
                  Murilo Zanini de Carvalho and Fabiana Naomi Iegawa},
  title        = {Quantum Constitutive Concerns: Reproducibility Artifact},
  year         = {2026},
  howpublished = {GitHub repository},
  url          = {https://github.com/j3ffsilva/quantum-constitutive-concerns},
  note         = {Version 1.0.0}
}
```

Machine-readable citation metadata are provided in
[`CITATION.cff`](CITATION.cff), which GitHub uses in its **Cite this
repository** interface. The software is distributed under the
[MIT License](LICENSE).
