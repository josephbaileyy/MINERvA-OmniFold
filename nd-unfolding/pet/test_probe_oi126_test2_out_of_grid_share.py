#!/usr/bin/env python3
"""Regression: OI-126 Test 2's out-of-grid reporting must satisfy the quotability condition in
`RULING-20260819-lanec-reconstructed-cell-assignment-admissible.md` §5 -- the `-1` COUNT **and its
WEIGHT SHARE**, PER ARM, not pooled.

WHAT THIS PINS, and why it is not a restatement of the rule. An earlier revision of the probe reported
only `n_events_out_of_grid_REPORTED_NOT_CLIPPED = int((~inside).sum())` -- a pooled event count. Because
the cell assignment is built from the SHARED reco kinematics, that count is IDENTICAL across all 51 arms
by construction: it is the one quantity that cannot differ. The quantity that can differ is the weight
share, since each arm is a different set of weights and the comparison is over weighted mass. So the probe
reported the arm-INVARIANT half and omitted the arm-DEPENDENT half -- precisely the confound §5 exists to
exclude. The decisive test below constructs two arms with IDENTICAL kinematics (hence identical count) and
shows the share differs, which is the property a pooled count cannot express.

Exercises the probe's OWN `arm_weight_mass` and `cell_index`, never a copy of them (BEN-476). Login-safe:
no ROOT, no TensorFlow, no cluster, and NO real campaign input -- the probe has still never been executed
against real arrays.

Run: python3 test_probe_oi126_test2_out_of_grid_share.py   (exit 0 = all pass)
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fullevent_fps_dataloader as fe                        # noqa: E402
import probe_oi126_test2_target_level_spatial as P           # noqa: E402

P_, F = 0, []


def ok(name, cond, detail=""):
    global P_
    if cond:
        P_ += 1
        print(f"  PASS  {name}")
    else:
        F.append(f"{name}: {detail}")
        print(f"  FAIL  {name}: {detail}")


def masks():
    """Kinematics with a known partition, built from the PINNED loader's own edges and SENTINEL:
    one row per p_parallel column (in-grid), one out-of-grid row, one FPS miss."""
    epp = np.asarray(fe.CANONICAL_PPARALLEL_EDGES, float)
    ctr = 0.5 * (epp[:-1] + epp[1:])
    pt = np.concatenate([np.full(ctr.size, 0.5), [0.5], [fe.SENTINEL]])
    pp = np.concatenate([ctr, [1e6], [fe.SENTINEL]])
    cell, n_cells, inside = P.cell_index(pt, pp)
    miss = (pt <= fe.SENTINEL + 1.0) | (pp <= fe.SENTINEL + 1.0)
    return pt, pp, cell, n_cells, inside & ~miss, miss


def main():
    pt, pp, cell, n_cells, inside, miss = masks()

    print("== 0. the fixture partitions as intended, from the loader's own grid ==")
    n_out = int(((~inside) & (~miss)).sum())
    ok("in_grid_is_one_per_pparallel_column", int(inside.sum()) == 19, int(inside.sum()))
    ok("exactly_one_out_of_grid_row", n_out == 1, n_out)
    ok("exactly_one_fps_miss_row", int(miss.sum()) == 1, int(miss.sum()))
    ok("out_of_grid_cell_is_minus_one_not_clipped", cell[-2] == -1, cell[-2])

    print("== 1. THE DECISIVE ONE: identical kinematics, identical COUNT, different SHARE ==")
    a = np.ones(pt.size)
    b = np.ones(pt.size); b[-2] = 100.0        # same row out of grid, 100x the weight
    ma = P.arm_weight_mass(a, "armA", inside=inside, miss=miss)
    mb = P.arm_weight_mass(b, "armB", inside=inside, miss=miss)
    ok("count_is_arm_INVARIANT", n_out == 1,
       "the count cannot distinguish these arms -- that is the defect this test pins")
    ok("share_is_arm_DEPENDENT",
       ma["share_of_gridable_signed"] != mb["share_of_gridable_signed"],
       f"{ma['share_of_gridable_signed']} vs {mb['share_of_gridable_signed']}")
    ok("share_moves_in_the_right_direction",
       mb["share_of_gridable_signed"] > ma["share_of_gridable_signed"],
       f"{ma['share_of_gridable_signed']} -> {mb['share_of_gridable_signed']}")

    print("== 2. the denominators are the ones the key names claim ==")
    for nm, m in (("A", ma), ("B", mb)):
        g = m["sum_w_out_of_grid"] + m["sum_w_in_grid"]
        ok(f"{nm}_gridable_shares_sum_to_one",
           abs(m["sum_w_out_of_grid"] / g + m["sum_w_in_grid"] / g - 1.0) < 1e-12)
        ok(f"{nm}_all_rows_denominator_includes_the_miss_mass",
           m["share_of_all_rows_signed"] < m["share_of_gridable_signed"],
           f"{m['share_of_all_rows_signed']} vs {m['share_of_gridable_signed']}")
        ok(f"{nm}_three_way_partition_is_exact",
           abs(m["sum_w_all_rows"]
               - (m["sum_w_fps_miss"] + m["sum_w_in_grid"] + m["sum_w_out_of_grid"])) < 1e-12)

    print("== 3. a NARROWING needs a test that it does not fire: all-in-grid gives share 0 ==")
    c = np.ones(pt.size); c[-2] = 0.0          # out-of-grid row carries no mass
    mc = P.arm_weight_mass(c, "armC", inside=inside, miss=miss)
    ok("zero_mass_out_of_grid_gives_share_zero", mc["share_of_gridable_signed"] == 0.0,
       mc["share_of_gridable_signed"])
    ok("but_the_COUNT_is_still_one", n_out == 1,
       "count and share disagree here by design -- a count of 1 with share 0.0 is exactly the case "
       "§5's 'a small count carrying large weight' distinction is about, inverted")

    print("== 4. mixed signs are REFUSED rather than shared ==")
    d = np.ones(pt.size); d[3] = -0.5
    try:
        P.arm_weight_mass(d, "armD", inside=inside, miss=miss)
        ok("negative_weights_refused", False, "no SystemExit raised")
    except SystemExit as e:
        ok("negative_weights_refused", "negative weights" in str(e), str(e)[:80])
        ok("refusal_explains_why_a_share_would_be_meaningless",
           "not interpretable" in str(e) or "cancel" in str(e), str(e)[:120])

    print("== 5. the probe still declares the §5 contract in its payload keys ==")
    src = Path(P.__file__).read_text()
    for key in ("out_of_grid_weight_share", "per_arm", "share_of_gridable_signed",
                "WHY_COUNT_IS_NOT_PER_ARM", "QUOTABILITY"):
        ok(f"payload_declares_{key}", key in src)
    ok("pooled_count_is_RETAINED_too",
       "n_events_out_of_grid_REPORTED_NOT_CLIPPED" in src,
       "§5 requires count AND share; dropping the count would trade one omission for another")
    ok("probe_still_records_it_has_never_run",
       "nothing here has been executed against real" in src)

    print(f"\n{P_} passed, {len(F)} failed")
    for f in F:
        print(f"  - {f}")
    return 1 if F else 0


if __name__ == "__main__":
    sys.exit(main())
