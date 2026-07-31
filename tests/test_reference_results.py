"""Full integration test against the versioned reference results."""

from __future__ import annotations

import json
import math
import os
from pathlib import Path
from typing import Any
import unittest

from quantum_constitutive_concerns import (
    analyze_backend_adaptation,
    analyze_zne_error_mitigation,
)


RUN_FULL_REPRODUCTION = os.environ.get("RUN_FULL_REPRODUCTION") == "1"
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(
    RUN_FULL_REPRODUCTION,
    "set RUN_FULL_REPRODUCTION=1 to execute the full simulation",
)
class ReferenceResultTests(unittest.TestCase):
    """Reproduce both examples and compare every reported field."""

    @staticmethod
    def float_tolerance(path: str) -> float:
        """Return a platform-independent tolerance for numerical estimates."""
        if ".distributions." in path:
            return 1e-2
        if ".metrics." in path:
            return 5e-3
        return 1e-12

    @staticmethod
    def transpiler_count_tolerance(path: str, expected: int) -> int | None:
        """Return the tolerance for platform-dependent physical counts."""
        operation_prefixes = (
            "zne_error_mitigation.circuits.native_operations",
            "zne_error_mitigation.circuits.scaled_operations",
        )
        size_and_depth_prefixes = (
            "zne_error_mitigation.circuits.native_depth",
            "zne_error_mitigation.circuits.native_size",
            "zne_error_mitigation.circuits.scaled_depths",
            "zne_error_mitigation.circuits.scaled_sizes",
        )
        if path.startswith(operation_prefixes):
            return max(1, math.ceil(abs(expected) * 0.10))
        if path.startswith(size_and_depth_prefixes):
            return max(1, math.ceil(abs(expected) * 0.05))
        return None

    def assert_result_equal(
        self,
        actual: Any,
        expected: Any,
        path: str = "result",
    ) -> None:
        transpiler_tolerance = (
            self.transpiler_count_tolerance(path, expected)
            if isinstance(expected, int) and not isinstance(expected, bool)
            else None
        )
        if (
            isinstance(expected, int)
            and not isinstance(expected, bool)
            and transpiler_tolerance is not None
        ):
            self.assertIsInstance(actual, int, path)
            self.assertAlmostEqual(
                actual,
                expected,
                delta=transpiler_tolerance,
                msg=path,
            )
        elif isinstance(expected, float):
            self.assertIsInstance(actual, (int, float), path)
            self.assertAlmostEqual(
                actual,
                expected,
                delta=self.float_tolerance(path),
                msg=path,
            )
        elif isinstance(expected, dict):
            self.assertEqual(set(actual), set(expected), path)
            for key, expected_value in expected.items():
                self.assert_result_equal(
                    actual[key],
                    expected_value,
                    f"{path}.{key}",
                )
        elif isinstance(expected, list):
            self.assertEqual(len(actual), len(expected), path)
            for index, expected_value in enumerate(expected):
                self.assert_result_equal(
                    actual[index],
                    expected_value,
                    f"{path}[{index}]",
                )
        else:
            self.assertEqual(actual, expected, path)

    def load_reference(self, filename: str) -> dict[str, Any]:
        path = REPOSITORY_ROOT / "results" / filename
        return json.loads(path.read_text(encoding="utf-8"))

    def test_examples_match_reference_results(self) -> None:
        backend_actual = analyze_backend_adaptation()
        backend_expected = self.load_reference("backend_adaptation.json")
        self.assert_result_equal(
            backend_actual,
            backend_expected,
            "backend_adaptation",
        )

        zne_actual = analyze_zne_error_mitigation()
        zne_expected = self.load_reference("zne_error_mitigation.json")
        self.assert_result_equal(
            zne_actual,
            zne_expected,
            "zne_error_mitigation",
        )

        self.assertEqual(backend_actual["logical"]["size"], 16)
        self.assertEqual(backend_actual["native"]["size"], 13)

        circuits = zne_actual["circuits"]
        self.assertEqual(
            circuits["native_operations"]["cz"],
            39,
        )
        self.assertEqual(
            [operations["cz"] for operations in circuits["scaled_operations"]],
            [39, 113, 117],
        )
        self.assertEqual(circuits["scaled_sizes"][0], circuits["native_size"])
        self.assertEqual(
            sum(circuits["native_operations"].values()),
            circuits["native_size"],
        )
        for operations, size in zip(
            circuits["scaled_operations"],
            circuits["scaled_sizes"],
            strict=True,
        ):
            self.assertEqual(sum(operations.values()), size)
        self.assertTrue(
            all(
                earlier < later
                for earlier, later in zip(
                    circuits["scaled_sizes"],
                    circuits["scaled_sizes"][1:],
                )
            )
        )
        self.assertTrue(
            all(
                depth <= size
                for depth, size in zip(
                    circuits["scaled_depths"],
                    circuits["scaled_sizes"],
                    strict=True,
                )
            )
        )
        self.assertLess(
            zne_actual["metrics"]["noisy_distribution_fidelity"],
            0.97,
        )
        self.assertGreaterEqual(
            zne_actual["metrics"]["zne_distribution_fidelity"],
            0.97,
        )


if __name__ == "__main__":
    unittest.main()
