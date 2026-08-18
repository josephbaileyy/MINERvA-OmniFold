#!/usr/bin/env python3
"""Offset-scan policy for the four-leg estimator-seed variation (spec (B), option (ii)).

WHY THIS EXISTS AND WHY IT IS A MODULE RATHER THAN A LINE IN A LAUNCHER. Under spec (B) `M(ii)` is a
JOINT measurement, and lane C ruled option **(ii) OFFSET**: vary each leg from its OWN baseline by a
common `k`, rather than moving every leg to one common value. The reason is structural -- estimator
noise is correlated between legs that share a seed and independent between legs that do not, so
"coherent" names a co-variation STRUCTURE, not a seed value, and a common value would make all four
legs correlated and therefore measure a different product.

The baselines are NOT shared. Measured 2026-08-18:

    group 1 (baseline 42)    sweep_bank_5d.py, bootstrap_nd.py, seedscan_split.py
    group 2 (baseline 1000)  unified_throw_cov.py

An offset preserves that grouping -- 42+k stays equal across group 1 and unequal to 1000+k -- but it
can make one group's seed at offset `k` COLLIDE WITH THE OTHER GROUP'S SEED AT A DIFFERENT OFFSET
`k'`, which aliases two members of the scan ensemble to the same estimator state.

THE CONSTRAINT IS PAIRWISE OVER THE GRID, NOT A FORBIDDEN OFFSET VALUE. This is the whole reason the
check is here rather than left to whoever picks the grid:

    g1@k collides with g2@k'   <=>   b1 + k == b2 + k'   <=>   k - k' == b2 - b1

An "exclude k in {+-958}" form is only the special case k' == 0 -- the baseline member -- and it
PASSES grids that alias. Counterexample, verified in the tests beside this file:

    grid [0, 100, 500, 958, 1058, 1500]  aliases at (0, 958) AND at (100, 1058)
    the single-value form flags the first and ships the second

A guard that certifies a grid it has not checked is worse than no guard, so the check is over PAIRS.

WHAT THE FAILURE ACTUALLY IS, stated because the first description of it was wrong and a wrong message
sends the next reader after the wrong bug: at k = 958 the WITHIN-RUN structure is intact (group 1 ->
1000, group 2 -> 1958, distinct). What collides is group 1 at k=958 against group 2 at k=0. So the
defect is SPURIOUS ALIASING BETWEEN TWO MEMBERS OF THE SCAN ENSEMBLE, not destruction of the
co-variation structure.

THE PREMISE THIS WHOLE CONSTRAINT RESTS ON IS UNMEASURED, and this module asserts a policy rather than
a fact. Lane C recorded it CONSIDERED-AND-DECLINED: *"a shared seed initialises the same RNG state but
consumes draws against different data -- perhaps the perturbations decorrelate. That is an empirical
claim nobody has measured."* If the premise holds, the pairwise form is REQUIRED and the single-value
form was insufficient. If it fails, neither is needed. Imposing it either way is conservative and
cheap; presenting it as structural would be a claim the campaign has explicitly declined to make.
"""
from __future__ import annotations

import itertools


def forbidden_differences(baselines):
    """The offset DIFFERENCES that alias, `{b_i - b_j : i != j}`.

    Diagnostic only -- a grid is validated by `check_offset_grid`, not by avoiding these. Two
    offsets whose difference lands here alias; a single offset cannot be judged on its own.
    """
    vals = sorted({int(b) for b in baselines})
    return sorted({a - b for a, b in itertools.permutations(vals, 2)})


def check_offset_grid(baselines, offsets):
    """Return the aliasing `(group_a, k_a, group_b, k_b, seed)` tuples for this grid; `[]` if clean.

    `baselines` maps a group name to its baseline estimator seed. `offsets` is the full scan grid.
    Every distinct-group pair is checked against every offset pair, including k == k'.
    """
    items = [(str(g), int(b)) for g, b in dict(baselines).items()]
    ks = [int(k) for k in offsets]
    out = []
    for (ga, ba), (gb, bb) in itertools.combinations(items, 2):
        for ka in ks:
            for kb in ks:
                if ba + ka == bb + kb:
                    out.append((ga, ka, gb, kb, ba + ka))
    return sorted(out)


def assert_offset_grid_is_alias_free(baselines, offsets):
    """FAIL CLOSED on any aliasing pair. Call this in the launcher, before submitting anything.

    Deliberately not a warning: the run completes normally and produces a number either way, so the
    only place this can be caught is before submission.
    """
    bad = check_offset_grid(baselines, offsets)
    if not bad:
        return True
    lines = [f"[FAIL] estimator-seed offset grid ALIASES {len(bad)} ensemble member pair(s). "
             f"Two scan points would run at the SAME estimator seed in different legs, so their "
             f"noise is not independent and the joint variation is not what (B) specifies."]
    for ga, ka, gb, kb, seed in bad[:12]:
        lines.append(f"        {ga} @ k={ka} -> seed {seed}   ==   {gb} @ k={kb} -> seed {seed}")
    if len(bad) > 12:
        lines.append(f"        ... and {len(bad) - 12} more")
    lines.append(f"        aliasing offset differences for these baselines: "
                 f"{forbidden_differences(baselines.values())}")
    lines.append("        This is PAIRWISE over the grid: excluding a single offset value is the "
                 "special case k'=0 and passes grids that alias (see this module's docstring).")
    raise SystemExit("\n".join(lines))
