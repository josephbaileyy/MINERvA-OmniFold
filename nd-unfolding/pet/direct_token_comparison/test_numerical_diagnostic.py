"""Check saved numerical failures, reference arithmetic and artifact integrity."""

from pathlib import Path

import numpy as np
from numerical_diagnostic import prepare_testing_import

prepare_testing_import()
import pytest  # noqa: E402

from numerical_diagnostic import reference_operation, save_errors, seal, verify_seal


def test_failure_saved_before_return(tmp_path: Path) -> None:
    """Near-zero errors fail the fixed threshold and retain their exact index."""
    left = np.array([0, 4, np.nan], dtype=np.float32)
    right = np.array([0.000489235, 4, np.nan], dtype=np.float32)
    result = save_errors(tmp_path / "errors.npz", left, right)
    assert not result["passes"]
    assert result["failing_elements"] == 2
    assert result["maximum_absolute_error"] is None
    with np.load(tmp_path / "errors.npz") as saved:
        np.testing.assert_array_equal(saved["failing_indices"], [[0], [2]])
        np.testing.assert_array_equal(saved["left"], left)
        np.testing.assert_array_equal(saved["right"], right)
        assert saved["normalized_error"][0] > 1


def test_relative_threshold_retained(tmp_path: Path) -> None:
    result = save_errors(
        tmp_path / "relative.npz", np.array([100.005]), np.array([100.0])
    )
    assert result["passes"]
    assert result["unequal_elements"] == 1


def test_shape_mismatch_is_saved(tmp_path: Path) -> None:
    result = save_errors(tmp_path / "shape.npz", np.zeros(2), np.zeros(3))
    assert result["shape_mismatch"]
    assert not result["passes"]
    assert (tmp_path / "shape.npz").exists()


@pytest.mark.parametrize("change", ["modify", "remove", "extra"])
def test_seal_rejects_changed_inventory(tmp_path: Path, change: str) -> None:
    artifact = tmp_path / "values.bin"
    artifact.write_bytes(b"original")
    seal(tmp_path)
    verify_seal(tmp_path)
    if change == "modify":
        artifact.write_bytes(b"changed")
    elif change == "remove":
        artifact.unlink()
    else:
        (tmp_path / "extra.bin").write_bytes(b"extra")
    with pytest.raises(ValueError, match="Artifact inventory mismatch"):
        verify_seal(tmp_path)


def test_float64_matmul_recovers_cancellation() -> None:
    a = np.array([[2**24, 1, -(2**24)]], dtype=np.float32)
    reference, bound = reference_operation("matmul", a, np.ones((3, 1), np.float32))
    np.testing.assert_array_equal(reference, [[1]])
    assert reference.dtype == np.float64
    assert bound[0, 0] > 0


def test_pool_preserves_empty_rows_and_signed_cancellation() -> None:
    values = np.array([[2, -1], [-2, 3], [4, 5]], np.float32)
    reference, bound = reference_operation("pool", values, np.array([1, 1, 3]))
    np.testing.assert_array_equal(reference, [[0, 0], [0, 2], [0, 0], [4, 5]])
    assert bound[1, 0] > 0
    np.testing.assert_array_equal(bound[[0, 2, 3]], np.zeros((3, 2)))


def test_mask_reference_removes_disabled_values() -> None:
    reference, bound = reference_operation("mask", [[2, 3], [4, 5]], [True, False])
    np.testing.assert_array_equal(reference, [[2, 3], [0, 0]])
    np.testing.assert_array_equal(bound, np.zeros((2, 2)))


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
