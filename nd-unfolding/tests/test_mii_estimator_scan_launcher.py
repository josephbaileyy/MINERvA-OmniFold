"""Contract tests for the background-aware 5D estimator-seed scan launcher."""

import re
from pathlib import Path

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
LAUNCHER_PATH = (
    REPOSITORY_ROOT / "nd-unfolding/sbatch_mii_estimator_scan_5d_bkgaware_gpu.sh"
)
LAUNCHER_TEXT = LAUNCHER_PATH.read_text(encoding="utf-8")


def executable_text(source: str) -> str:
    """Return launcher lines that are not comments."""
    return "\n".join(
        line for line in source.splitlines() if not line.lstrip().startswith("#")
    )


def assert_candidate_footing(source: str) -> None:
    """Assert that the CV unfold reads the declared background-aware ROOT footing."""
    code = executable_text(source)
    assert (
        'OMNIFILE="${ND}/runEventLoopOmniFold_5D_MEFHC_universes_full_bkgaware.root"'
        in code
    )
    assert (
        'FLUX_MC="${DATA_ROOT}/2d-unfolding/baseline_flux/'
        'runEventLoopMC_MEFHC.root"' in code
    )
    assert '--omnifile "${OMNIFILE}"' in code
    assert '--mcfile "${FLUX_MC}"' in code
    assert "--npz" not in code


def test_launcher_uses_candidate_background_aware_footing() -> None:
    assert_candidate_footing(LAUNCHER_TEXT)


def test_estimator_seed_is_the_array_task_id() -> None:
    code = executable_text(LAUNCHER_TEXT)
    assert '--seed "${SLURM_ARRAY_TASK_ID}"' in code
    assert re.search(r'^#SBATCH --array=1-12(?:%\d+)?$', LAUNCHER_TEXT, re.MULTILINE)


def test_unfold_configuration_is_fixed() -> None:
    code = executable_text(LAUNCHER_TEXT)
    assert "--axes eavail,q3,W" in code
    assert "--iters 5" in code
    assert "--estimator lgbm" in code
    assert "--use-weights" in code
    assert "--closure-slack 5000" in code


def test_scheduler_shape_is_the_predeclared_array() -> None:
    assert re.search(r'^#SBATCH --time=01:30:00$', LAUNCHER_TEXT, re.MULTILINE)
    assert re.search(r'^#SBATCH --array=1-12(?:%\d+)?$', LAUNCHER_TEXT, re.MULTILINE)


def test_every_python_invocation_is_guarded() -> None:
    python_lines = [
        line for line in executable_text(LAUNCHER_TEXT).splitlines() if "python3" in line
    ]
    assert python_lines
    assert all('python3 "$GUARD" --expect-root "$CODE_ROOT"' in line for line in python_lines)


def test_wrong_footing_mutant_is_rejected() -> None:
    """Power arm: replacing the ROOT input flag with the legacy packed flag must fail."""
    original = '--omnifile "${OMNIFILE}"'
    mutant = LAUNCHER_TEXT.replace(original, '--npz "${OMNIFILE}"', 1)
    assert mutant != LAUNCHER_TEXT, "fixture mutation did not apply"
    with pytest.raises(AssertionError):
        assert_candidate_footing(mutant)
