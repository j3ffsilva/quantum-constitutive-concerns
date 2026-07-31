"""Command-line interface for the reproducibility artifact."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence

from quantum_constitutive_concerns.backend_adaptation import (
    analyze_backend_adaptation,
)
from quantum_constitutive_concerns.zne_error_mitigation import (
    DEFAULT_SEED_TRANSPILER,
    DEFAULT_SHOTS,
    DEFAULT_TARGET,
    analyze_zne_error_mitigation,
)


def _write_result(result: dict[str, Any], output: Path | None) -> None:
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


def build_parser() -> argparse.ArgumentParser:
    """Build the artifact command-line parser."""
    parser = argparse.ArgumentParser(
        prog="quantum-constitutive-concerns",
        description="Run the executable examples associated with the paper.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    backend = subparsers.add_parser(
        "backend-adaptation",
        help="analyze logical-to-native backend adaptation",
    )
    backend.add_argument("--target", type=int, default=0)
    backend.add_argument("--optimization-level", type=int, default=3)
    backend.add_argument(
        "--seed-transpiler",
        type=int,
        default=DEFAULT_SEED_TRANSPILER,
    )
    backend.add_argument("--output", type=Path)

    zne = subparsers.add_parser(
        "zne-error-mitigation",
        help="run the distribution-level ZNE example",
    )
    zne.add_argument("--target", default=DEFAULT_TARGET)
    zne.add_argument("--shots", type=int, default=DEFAULT_SHOTS)
    zne.add_argument(
        "--seed-transpiler",
        type=int,
        default=DEFAULT_SEED_TRANSPILER,
    )
    zne.add_argument("--output", type=Path)

    return parser


def main(argv: Sequence[str] | None = None) -> None:
    """Dispatch an artifact command."""
    args = build_parser().parse_args(argv)
    if args.command == "backend-adaptation":
        result = analyze_backend_adaptation(
            target=args.target,
            optimization_level=args.optimization_level,
            seed_transpiler=args.seed_transpiler,
        )
    else:
        result = analyze_zne_error_mitigation(
            target=args.target,
            shots=args.shots,
            seed_transpiler=args.seed_transpiler,
        )
    _write_result(result, args.output)
