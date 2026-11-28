"""Verify the replay against generated-normalized IBU and reproduce its two outputs."""

import argparse
import io
import re
import subprocess
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import numpy as np

import compare

FROZEN = "0a6e3f4e84e4286021795c8ba652a1f010b98af4"
FOLDER = "docs/orchestration/state/precharge-20261125/ibu-convention"


def reference_selected(
    migration: np.ndarray, target: np.ndarray, generated: np.ndarray
) -> np.ndarray:
    """Implement inputs/replay/replay.py's update in generated-event units."""
    response = np.zeros_like(migration, dtype=float)
    np.divide(migration, generated, out=response, where=generated > 0)
    efficiency = response.sum(axis=0)
    truth = generated.copy()
    for _ in range(10):
        predicted = response @ truth
        ratios = np.zeros_like(predicted)
        np.divide(target, predicted, out=ratios, where=predicted > 0)
        updated = truth * (response.T @ ratios)
        truth = np.zeros_like(updated)
        np.divide(updated, efficiency, out=truth, where=efficiency > 0)
    return truth * efficiency


def check(checkout: Path) -> None:
    """Check the toy, all real iteration inputs, and all six diagnostic rows."""
    unfold = compare.unfold_selected
    toy = np.array([[8.0, 8.0], [2.0, 2.0]])
    target = np.array([16.0, 4.0])
    generated = np.array([20.0, 0.0])
    np.testing.assert_allclose(unfold(toy, target, generated), [20.0, 0.0])
    print(
        "PASS: toy with positive migration in an empty truth column assigns all 20 events to supported truth."
    )

    affected_bins = []

    def checked(migration: np.ndarray, data: np.ndarray, gen: np.ndarray) -> np.ndarray:
        result = unfold(migration, data, gen)
        expected = reference_selected(migration, data, gen)
        np.testing.assert_allclose(result, expected, rtol=1e-10, atol=1e-7)
        np.testing.assert_array_equal(result[gen == 0], 0.0)
        affected_bins.append(
            np.flatnonzero((gen == 0) & (migration.sum(0) > 0)).tolist()
        )
        printout.append(
            f"224 bins compared; maximum absolute selected-count difference {np.max(np.abs(result-expected)):.3g}"
        )
        return result

    printout = []
    capture = io.StringIO()
    with patch.object(compare, "unfold_selected", side_effect=checked), redirect_stdout(
        capture
    ):
        compare.compare(checkout)
    names = [
        "baseline control",
        "unchanged",
        "true40_60_only",
        "all_in_grid_true_muons",
    ]
    assert len(printout) == len(names)
    for name, bins, line in zip(names, affected_bins, printout):
        print(
            f"PASS: {name}: {line}; unsupported columns with selected entries: {bins}"
        )
    assert affected_bins[:3] == [[], [], []] and len(affected_bins[3]) == 2

    old = subprocess.check_output(
        ["git", "-C", str(checkout), "show", f"{FROZEN}:{FOLDER}/replay.txt"], text=True
    )
    new = capture.getvalue()
    previous, current = old.splitlines(), new.splitlines()
    assert len(current) == len(previous) == 7
    for line_before, line_after in zip(previous[:4], current[:4]):
        assert line_before == line_after.replace("partial (saved scan) ", "")
    assert previous[-1] == current[-1]
    print(
        "PASS: four control rows and the efficiency count summary reproduce the frozen output."
    )

    reviewed = {
        "in_grid": (0.34925865, 1.09367341),
        "anywhere": (0.37259493, 1.02573016),
    }
    for line in current[4:6]:
        match = re.fullmatch(
            r"all_in_grid_true_muons (\w+) partial \(saved scan\) chi2/205 (\S+) column ratio (\S+) cell range .+",
            line,
        )
        assert match
        convention, distance, ratio = match.groups()
        np.testing.assert_allclose(
            [float(distance), float(ratio)], reviewed.pop(convention), atol=5e-9, rtol=0
        )
    assert not reviewed
    print("PASS: both changed rows agree with the review to eight decimal places.")
    Path(__file__).with_name("replay.txt").write_text(new)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkout", type=Path)
    check(parser.parse_args().checkout)
