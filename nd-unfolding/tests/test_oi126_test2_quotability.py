"""Tests for the §5 quotability accounting added to the OI-126 Test 2 probe.

Governing ruling: `RULING-20260819-lanec-reconstructed-cell-assignment-admissible.md` §5 --
a Test 2 number is quotable ONLY alongside the `-1` count AND its weight share, PER ARM, and
"a count alone is insufficient: the comparison is over weighted mass, so a small count carrying
large weight is the case that matters".

THESE TESTS ARE WRITTEN IN THE DIRECTION THE FIX ACTS. The defect was not "a field was missing"
in the abstract -- it was that the field the probe DID report (a pooled count) is arm-invariant by
construction, so it cannot distinguish two arms that differ. `test_counts_are_arm_invariant_but_shares_are_not`
is therefore the load-bearing test: it FAILS if someone reverts to count-only reporting, and it
would PASS vacuously if it only checked that the keys exist. The others pin arithmetic and the
two ways a share can mislead (sign cancellation, and a zero denominator reported as 0.0).
"""
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

PET = Path(__file__).resolve().parents[1] / "pet"


def _load_probe():
    """Import the probe by path. It is a script, not a package member, and its module body
    imports the PINNED loader -- so a failure here is a real signal, not a harness detail."""
    sys.path.insert(0, str(PET))
    spec = importlib.util.spec_from_file_location(
        "probe_oi126", PET / "probe_oi126_test2_target_level_spatial.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


probe = _load_probe()


# Five events. Event 0,1 in grid; event 2 out of grid proper; event 3 an FPS miss; event 4 in grid.
INSIDE = np.array([True, True, False, False, True])
MISS = np.array([False, False, False, True, False])


def test_counts_and_arithmetic_are_exact():
    w = np.array([1.0, 2.0, 4.0, 8.0, 3.0])
    s = probe.out_of_grid_stats(w, INSIDE, MISS)

    assert s["n_dropped_total"] == 2          # events 2 and 3
    assert s["n_out_of_grid_proper"] == 1     # event 2 only
    assert s["n_fps_miss_SENTINEL"] == 1      # event 3 only

    assert s["weight_abs_total"] == pytest.approx(18.0)
    assert s["weight_abs_dropped"] == pytest.approx(12.0)              # 4 + 8
    assert s["weight_abs_out_of_grid_proper"] == pytest.approx(4.0)
    assert s["share_abs_dropped"] == pytest.approx(12.0 / 18.0)
    assert s["share_abs_out_of_grid_proper"] == pytest.approx(4.0 / 18.0)


def test_counts_are_arm_invariant_but_shares_are_not():
    """THE LOAD-BEARING TEST, and the reason §5 demands shares rather than counts.

    Two arms over the SAME events with the SAME assignment: every count is identical, because the
    cell assignment is reconstructed from shared reco kinematics. The weight shares differ by an
    order of magnitude. A count-only report -- what the probe emitted before 2026-08-20 -- is
    therefore blind to a difference that §5.2 says can make the target-level gap a confound.
    """
    arm_a = np.array([1.0, 1.0, 0.01, 0.01, 1.0])   # almost no weight outside
    arm_b = np.array([1.0, 1.0, 50.0, 50.0, 1.0])   # most of the weight outside

    a = probe.out_of_grid_stats(arm_a, INSIDE, MISS)
    b = probe.out_of_grid_stats(arm_b, INSIDE, MISS)

    # Counts cannot tell the arms apart -- this is the defect, asserted rather than described.
    for k in ("n_dropped_total", "n_out_of_grid_proper", "n_fps_miss_SENTINEL"):
        assert a[k] == b[k], f"{k} should be arm-invariant by construction"

    # The shares can, and by a wide margin.
    assert a["share_abs_dropped"] < 0.01
    assert b["share_abs_dropped"] > 0.9
    assert b["share_abs_dropped"] > 50 * a["share_abs_dropped"]


def test_signed_share_can_cancel_while_absolute_share_cannot():
    """Why BOTH shares are reported. These are signed refined weights, so a signed share can sit
    at ~0 through cancellation while a large amount of weight is actually off the grid. Reporting
    only the signed share would look reassuring in exactly the case that matters."""
    w = np.array([1.0, 1.0, +40.0, -40.0, 1.0])     # dropped weight cancels to zero, signed
    s = probe.out_of_grid_stats(w, INSIDE, MISS)

    assert s["weight_signed_dropped"] == pytest.approx(0.0)
    assert s["share_signed_dropped"] == pytest.approx(0.0)
    # ... while 80 of 83 units of absolute weight are outside the grid.
    assert s["weight_abs_dropped"] == pytest.approx(80.0)
    assert s["share_abs_dropped"] > 0.9


def test_zero_denominator_is_None_not_zero():
    """A share of 0.0 reads as "nothing outside the grid"; an all-zero arm has no share at all.
    Collapsing the second onto the first would report the reassuring fact for the uninformative case."""
    s = probe.out_of_grid_stats(np.zeros(5), INSIDE, MISS)
    assert s["share_abs_dropped"] is None
    assert s["share_signed_dropped"] is None
    assert s["weight_abs_total"] == 0.0


def test_all_inside_reports_zero_share_not_None():
    """The complement of the test above: a real arm with genuinely nothing outside must report 0.0,
    so that None keeps meaning "no denominator" and never means "clean"."""
    inside = np.ones(5, dtype=bool)
    miss = np.zeros(5, dtype=bool)
    s = probe.out_of_grid_stats(np.array([1.0, 2.0, 3.0, 4.0, 5.0]), inside, miss)
    assert s["n_dropped_total"] == 0
    assert s["share_abs_dropped"] == pytest.approx(0.0)
