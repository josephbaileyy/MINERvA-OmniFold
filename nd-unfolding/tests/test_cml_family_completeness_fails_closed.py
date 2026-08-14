#!/usr/bin/env python3
"""`combine_cml_bkgsub.py` must REFUSE an incomplete `C_ML` family, not warn about it.

WHY THIS BATTERY EXISTS, and it is a live hazard rather than a hypothetical.
`state/gate6-member-trajectories-result-56847059.json:109-118` records
`family_verdict BLOCK_GATE6_ML_ENSEMBLE`, `passing_members [1]`, `failing_members [2,3,4,5]`, and
five prohibitions including `do_not_select_passing_subset`. Before this file existed, that
prohibition was enforced **on people only**: `combine_cml_bkgsub.py` treated a member-count mismatch
as a `WARN`, built the covariance from whatever it found, and printed *"NOT final until complete"* --
into a log that this filesystem block-buffers for hours at a time (`BEN-028`). So the single passing
member could have become `C_ML`, with the warning as the only trace. `BEN-244`.

WHAT AXIS THIS COVERS, named because a battery that does not name its axis gets mistaken for coverage
it does not have (`BEN-119`). Three axes, and the third is the one that makes the first two mean
something:

  1. REFUSAL. An incomplete family is a non-zero exit AND no output file. Exercised at the exact live
     case -- one member against `--expect 12` -- and at zero members, and at 11 of 12.
  2. THE OPT-IN IS REAL AND IT COSTS SOMETHING. A diagnostic may still build from an incomplete
     family via `--allow-incomplete-family`, and when it does the output is marked non-quotable BY
     NAME and BY FIELD, following the `NONQUOTABLE-DIAGNOSTIC.` convention that closure `56552326`
     already uses. A guard that cannot be opted out of gets deleted; one that is free to opt out of
     is not a guard.
  3. THE POSITIVE CONTROL. A COMPLETE family must still build, exit 0, and be marked quotable. This
     axis exists because of `test_cannot_fail_auditor.py`'s inverse: a check that always fires is as
     useless as one that never does, and "refuses everything" would pass axes 1 and 2 alone.

HOW THIS AVOIDS `assert_no_truth_leakage`'s DEFECT -- the guard whose producer and checker were
line-for-line identical, so it could never fire. **Every test here runs the real script as a
subprocess and observes its exit code and its files.** Nothing re-implements the completeness rule,
so the test cannot agree with the code by construction; if the rule is deleted from the script, no
edit to this file is needed for the suite to go red.

STATED GAPS, at the foot of the file rather than left to be discovered.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "nd-unfolding/pet/combine_cml_bkgsub.py"

NBINS = 6
# The live case, transcribed from the receipt rather than chosen: one member passed, four failed.
LIVE_PASSING_MEMBERS = 1
CML_EXPECT_DEFAULT = 12


def _write_cv(d):
    """A `cv` with two zero bins, so `cv > 0` is a real mask and not the identity."""
    cv = np.array([3.0, 0.0, 5.0, 7.0, 0.0, 11.0])
    assert cv.shape[0] == NBINS
    p = d / "pet_nominal_bkgsub_5d_xsec.npz"
    np.savez(p, xsec_flat=cv)
    return p


def _write_members(d, pairs, seed=0):
    """One npz per (sub_seed, est_seed), named exactly as the script's regex requires."""
    rng = np.random.default_rng(seed)
    md = d / "cml"
    md.mkdir(exist_ok=True)
    for (s, e) in pairs:
        x = np.array([3.0, 0.0, 5.0, 7.0, 0.0, 11.0]) * (1.0 + 0.01 * rng.standard_normal(NBINS))
        np.savez(md / f"pet_s{s}_e{e}_bkgsub_5d_xsec.npz", xsec_flat=x)
    return md


def _run(tmp_path, pairs, expect, extra=(), seed=0):
    cv = _write_cv(tmp_path)
    md = _write_members(tmp_path, pairs, seed=seed)
    out = tmp_path / "pet_cml_bkgsub_5d.npz"
    cmd = [sys.executable, str(SCRIPT),
           "--glob", str(md / "pet_s*_e*_bkgsub_5d_xsec.npz"),
           "--cv", str(cv),
           "--floor", str(tmp_path / "absent_floor.json"),
           "--out", str(out),
           "--expect", str(expect), *extra]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc, out


def _balanced(ns, ne):
    return [(s, e) for s in range(ns) for e in range(ne)]


def _summary(p):
    """Mirror the script's own `os.path.splitext(out)[0] + '.summary.json'`. NOT `Path.with_suffix`:
    the non-quotable name `NONQUOTABLE-DIAGNOSTIC.pet_cml_bkgsub_5d.npz` has two dots, and
    `with_suffix('')` strips the wrong one -- which this test hit before it was written this way."""
    return Path(str(p)[: -len(p.suffix)] + ".summary.json") if p.suffix else Path(str(p) + ".summary.json")


# --- AXIS 1: REFUSAL -----------------------------------------------------------------------------

@pytest.mark.needs_tmpdir
def test_the_live_case_one_passing_member_against_expect_12_is_refused(tmp_path):
    """THE case this file exists for. Gate 6 has exactly one passing member; the crossed design is
    12. Building from the one is `do_not_select_passing_subset` violated by the builder itself."""
    proc, out = _run(tmp_path, [(0, 0)], CML_EXPECT_DEFAULT)
    combined = proc.stdout + proc.stderr
    assert proc.returncode != 0, (
        "combine_cml_bkgsub.py built C_ML from 1 of 12 members and exited 0. "
        f"do_not_select_passing_subset is not enforced by the builder.\n{combined}")
    assert not out.exists(), (
        "refused with a non-zero exit but WROTE THE OUTPUT ANYWAY -- a downstream consumer globbing "
        "for the file finds a subset-derived C_ML and never sees the exit code")
    assert not _summary(out).exists()
    assert "1" in combined and "12" in combined, (
        f"the refusal must name both counts so the log says what is missing:\n{combined}")


@pytest.mark.needs_tmpdir
def test_zero_members_is_refused_and_not_a_traceback(tmp_path):
    """Zero members must be the same refusal, not an unhandled `vstack([])`. A traceback is a defect
    report; this is a predeclared condition and must read as one."""
    proc, out = _run(tmp_path, [], CML_EXPECT_DEFAULT)
    combined = proc.stdout + proc.stderr
    assert proc.returncode != 0
    assert not out.exists()
    assert "Traceback" not in combined, f"refused by crashing rather than by rule:\n{combined}"


@pytest.mark.needs_tmpdir
def test_eleven_of_twelve_is_refused_because_nearly_complete_is_not_complete(tmp_path):
    """The dangerous size. One missing member barely moves any published number, which is exactly
    why a warning gets read past. `BEN-023`: validate completeness, not existence."""
    pairs = _balanced(3, 4)[:11]
    assert len(pairs) == 11
    proc, out = _run(tmp_path, pairs, CML_EXPECT_DEFAULT)
    assert proc.returncode != 0, "11 of 12 built silently"
    assert not out.exists()


# --- AXIS 2: THE OPT-IN IS REAL AND IT COSTS SOMETHING -------------------------------------------

@pytest.mark.needs_tmpdir
def test_explicit_opt_in_builds_but_the_product_is_marked_non_quotable(tmp_path):
    """A legitimate intermediate/diagnostic path must survive this change -- silently breaking a
    working diagnostic to fix a publication hazard trades one defect for another. The price of the
    opt-in is that its output cannot be mistaken for the publication object."""
    proc, out = _run(tmp_path, [(0, 0), (0, 1)], CML_EXPECT_DEFAULT,
                     extra=("--allow-incomplete-family",))
    combined = proc.stdout + proc.stderr
    assert proc.returncode == 0, f"the explicit opt-in must still build:\n{combined}"
    assert not out.exists(), (
        "the opt-in wrote to the PUBLICATION path. A non-quotable product at a quotable filename is "
        "how a diagnostic becomes a result (56552326's convention exists for this).")
    nq = out.with_name("NONQUOTABLE-DIAGNOSTIC." + out.name)
    assert nq.exists(), f"expected the non-quotable product at {nq.name}:\n{combined}"
    summary = json.loads(_summary(nq).read_text())
    assert summary["quotable"] is False
    assert summary["family_complete"] is False
    assert summary["n_members"] == 2 and summary["expected"] == CML_EXPECT_DEFAULT


# --- AXIS 3: THE POSITIVE CONTROL ----------------------------------------------------------------

@pytest.mark.needs_tmpdir
def test_a_complete_family_still_builds_and_is_marked_quotable(tmp_path):
    """Without this, 'refuse everything' passes axes 1 and 2. Also pins the real contract: on a
    complete BALANCED grid the two-way decomposition must actually run."""
    pairs = _balanced(2, 2)
    proc, out = _run(tmp_path, pairs, len(pairs))
    combined = proc.stdout + proc.stderr
    assert proc.returncode == 0, f"a COMPLETE family was refused:\n{combined}"
    assert out.exists(), combined
    assert not out.with_name("NONQUOTABLE-DIAGNOSTIC." + out.name).exists()
    summary = json.loads(_summary(out).read_text())
    assert summary["quotable"] is True
    assert summary["family_complete"] is True
    assert summary["variance_decomposition"]["balanced"] is True
    assert summary["variance_decomposition"]["grid"] == [2, 2]
    # cv has two zero bins; the reported mask must exclude them, or the covariance is built over
    # bins the central does not report.
    assert summary["n_reported_bins"] == 4

    with np.load(out) as z:
        C = z["C_ml"]
        assert C.shape == (4, 4)
        assert bool(z["reported_mask"].sum() == 4)
    # rank <= n-1 by Gram construction; 4 members over 4 bins must NOT be full rank.
    assert np.linalg.matrix_rank(C, tol=1e-10 * max(np.linalg.eigvalsh(C).max(), 1e-300)) <= 3


# --- STATED GAPS ---------------------------------------------------------------------------------
# 1. `--expect` REMAINS A DECLARED NUMBER, so `--expect 1` still builds from one member. That is an
#    explicit declaration recorded in the summary rather than a silent path, and closing it needs the
#    crossed design's size to live somewhere the builder can read -- which is a predeclaration
#    question, not a builder question. Named because "the guard can be bypassed by declaring a
#    smaller family" is the first thing an adversarial reader should ask.
# 2. NOT COVERED: whether the members are the RIGHT members. A complete count of 12 wrong files
#    passes every test here. Member identity is `combine_cov_nd`'s seed-manifest problem and the
#    script's own docstring says that manifest cannot distinguish these files (they all carry
#    extractor seed 0), so this battery deliberately does not claim it.
# 3. NOT COVERED: balance. `--expect 12` with 12 members on an unbalanced (1,12) grid builds, and the
#    decomposition self-reports `balanced: False`. Left as-is: it is reported, not hidden.
# 4. These tests write files, so they carry `needs_tmpdir` and SKIP rather than ERROR under the
#    read-only audit sandbox (`conftest.py`).
