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

THE PREMISE THIS CONSTRAINT RESTS ON IS UNMEASURED, SO THIS IS A CONSERVATIVE CHOICE AND NOT A
CORRECTNESS REQUIREMENT -- and the distinction is the point of this
paragraph rather than a hedge in it. A future lane relaxing this guard needs to know whether it is
trimming a safety margin or breaking a proof, and those are opposite decisions -- so: Lane C recorded it CONSIDERED-AND-DECLINED: *"a shared seed initialises the same RNG state but
consumes draws against different data -- perhaps the perturbations decorrelate. That is an empirical
claim nobody has measured."* If the premise holds, the pairwise form is REQUIRED and the single-value
form was insufficient. If it fails, neither is needed. Imposing it either way is cheap, so it is imposed --
but it is a MARGIN, not a THEOREM. Presenting it as a structural fact would be a claim the campaign has
explicitly declined to make, and the first relay of this constraint did present it that way.

REQUIREMENT (5), and it is enforced in the LAUNCHERS rather than here because that is the only place it
cannot be got wrong: `--draw-seed` stays the literal `1000` for every `k`. ONLY the estimator seed
moves. The natural implementation -- one variable in hand, passed to both flags -- gives every scan
member a DIFFERENT THROW ENSEMBLE, so the measured spread is estimator noise convolved with ensemble
noise, which is `C_syst` re-measured with extra steps and looks entirely normal. AND THE COMBINE GUARD
CANNOT CATCH IT: `unified_throw_cov.py` compares each slab's `draw_seed` against THIS combine's
`--draw-seed`, and each scan member runs its own combine, so `1000/1000` and `1005/1005` both pass.
PER-MEMBER COHERENCE IS NOT ENSEMBLE COHERENCE, and that guard is per-member by construction. Lane D
raised it; the offset hook in the six launchers touches `--estimator-seed` only, and
`assert_draw_seed_is_pinned` below asserts the literal so a later edit cannot parameterise it.
"""
from __future__ import annotations

import itertools
import os


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


def pairs_checked(baselines, offsets):
    """How many (group-pair, offset-pair) comparisons the aliasing check actually performs.

    NON-VACUITY, and it is the hole lane D left in its own power-test specification this evening:
    with one group, or one offset, the check compares NOTHING and returns clean. A guard that
    reports OK over zero comparisons is not a guard, so callers assert this is > 0.
    """
    n_groups = len({int(b) for b in dict(baselines).values()})
    n_off = len({int(k) for k in offsets})
    return (n_groups * (n_groups - 1) // 2) * n_off * n_off


def assert_offset_grid_is_alias_free(baselines, offsets):
    """FAIL CLOSED on any aliasing pair. Call this in the launcher, before submitting anything.

    Deliberately not a warning: the run completes normally and produces a number either way, so the
    only place this can be caught is before submission.
    """
    checked = pairs_checked(baselines, offsets)
    if checked == 0:
        raise SystemExit(
            "[FAIL] the aliasing check compared ZERO pairs and would have reported OK. That needs "
            "at least two distinct baselines and at least one offset; got baselines="
            f"{sorted(set(int(b) for b in dict(baselines).values()))}, offsets={sorted(set(offsets))}. "
            "A clean result over zero comparisons is not evidence -- it is the check not running.")
    bad = check_offset_grid(baselines, offsets)
    if not bad:
        return checked
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


# ---------------------------------------------------------------------------------------------------
# Requirement (5)'s pin. E's `pinned_expected` shape: assert against the CONSTANT, never against the
# run's own argument -- an argument compared to itself is `BEN-423`, which caught three lanes today.
ARCHIVE_DRAW_SEED = 1000

#: leg -> (coherence group, archive estimator-seed baseline). Group membership is what `(ii)` preserves.
LEG_BASELINES = {
    "sweep_bank_5d":     ("g1", 42),
    "bootstrap_nd":      ("g1", 42),
    "seedscan_split":    ("g1", 42),
    "unified_throw_cov": ("g2", 1000),
}


def group_baselines(legs=None):
    """`{group: baseline}` for the aliasing check. Distinct groups are what can alias."""
    src = LEG_BASELINES if legs is None else {k: LEG_BASELINES[k] for k in legs}
    out = {}
    for _leg, (grp, base) in src.items():
        if grp in out and out[grp] != base:
            raise SystemExit(f"[FAIL] group {grp} has two baselines {out[grp]} and {base}; the "
                             "coherence grouping is not well defined")
        out[grp] = base
    return out


def assert_draw_seed_is_pinned(launcher_texts):
    """FAIL CLOSED if any targeted launcher parameterises `--draw-seed`.

    `launcher_texts` maps a path to its source. Only the uthrow leg carries the flag at all; the
    others must not acquire it. Asserted against ARCHIVE_DRAW_SEED, not against whatever the file
    happens to say, so the check cannot be satisfied by the thing it is checking.
    """
    bad = []
    for path, text in launcher_texts.items():
        for ln, line in enumerate(text.split("\n"), 1):
            if "--draw-seed" not in line:
                continue
            if f"--draw-seed {ARCHIVE_DRAW_SEED}" not in line:
                bad.append(f"{path}:{ln}: {line.strip()[:90]}")
    if bad:
        raise SystemExit(
            "[FAIL] --draw-seed is not pinned to the literal " + str(ARCHIVE_DRAW_SEED) + " in:\n  "
            + "\n  ".join(bad)
            + "\n  ONLY the estimator seed may move across scan members. A moving draw seed gives "
              "every member a different throw ensemble, so the measured spread is estimator noise "
              "CONVOLVED with ensemble noise. The combine guard cannot catch it: it compares each "
              "slab against THIS combine's --draw-seed, and every member runs its own combine, so "
              "1000/1000 and 1005/1005 both pass. Per-member coherence is not ensemble coherence.")
    return True


# ---------------------------------------------------------------------------------------------------
OFFSET_ENV = "MNV_EST_SEED_OFFSET"


def declared_offset(environ=None):
    """`(declared, value)` for the offset, for STAMPING ONLY -- never for behaviour.

    WHY THE PRODUCT MUST CARRY THE OFFSET AND NOT JUST THE SEED, which is lane D's finding and is
    unrecoverable once the run is spent: the slabs already stamp `estimator_seed`, so **a leg that
    silently ran UNHOOKED stamps its baseline -- indistinguishable from a member at k = 0.** Only six
    launchers carry the hook; any other launcher of the same module runs at baseline and looks like a
    legitimate anchor member. Stamping the OFFSET separates the two:

        declared = 0            this leg did not go through a hooked launcher. Its seed is its
                                baseline and NOTHING can be concluded about which scan member it is.
        declared = 1, value = 0 this leg ran hooked, at the archive anchor, deliberately.
        declared = 1, value = k this leg ran hooked at offset k.

    TWO KEYS RATHER THAN A SENTINEL, on `unified_throw_cov.py`'s null-as-absent precedent -- a
    sentinel invites `or 0` and collapses "not declared" into "zero", which is the exact conflation
    this exists to prevent. And UNLIKE the `ew_coverage_checked` flag lane D made me drop, `declared`
    genuinely takes both values: it is 0 whenever the env is unset, which is every non-scan run.

    Reading an env var is a hidden input and that is a real cost. It is accepted here because it is
    STAMP-ONLY -- no code path branches on it -- and the alternative is provenance that cannot be
    reconstructed from the artifact at all.
    """
    env = os.environ if environ is None else environ
    raw = env.get(OFFSET_ENV)
    if raw is None or str(raw).strip() == "":
        return 0, 0
    try:
        return 1, int(str(raw).strip())
    except ValueError:
        raise SystemExit(f"[FAIL] {OFFSET_ENV}={raw!r} is not an integer. It is stamped into every "
                         "product of this run, so a malformed value would be recorded as provenance.")


# ---------------------------------------------------------------------------------------------------
# REQUIREMENT (6): THE CLEAN-OFFSET PREDICATE. Lane C's finding, and it is a DIFFERENT confound from
# the pairwise aliasing rule above -- which is why both are needed and why the pairwise rule is
# "necessary and nowhere near sufficient".
#
# Two legs derive their PER-UNIT seeds by adding small integers to the SAME baselines the offset
# moves. So an offset can slide a leg's ESTIMATOR seed into the range of that leg's own DRAW seeds,
# and then, inside a single member, one unit's draw RNG and the estimator RNG are seeded identically.
# The coincidence SITE MOVES WITH k, so it is a per-member structural difference -- the attributability
# confound the pairwise rule exists to prevent, arriving through a door that rule does not cover.
#
# At k = 5: bootstrap replica 47 draws its Poisson weights from seed 47 while the estimator in that
# same unfold is seeded 47. At k = 5 again: unified_throw_cov's estimator seed 1005 IS throw 5's draw
# seed. `k = 958` is dirty for a SECOND independent reason -- so the one value the pairwise rule
# catches, it catches for one of the two reasons it is bad.
#
# DERIVED FROM THE RANGES, NEVER FROM A THRESHOLD. The condition happens to be `k >= 1118` for the
# ranges below, and `1000` and `997` both FAIL (`42+1000 = 1042` and `42+997 = 1039` are both inside
# `[1000,1159]`). A remembered threshold would also silently stop covering the moment an array size
# changes, which is a launcher edit anyone can make.
#
#: leg -> (lo, hi) of the per-unit seeds that leg derives, with where each was measured.
PER_UNIT_SEED_RANGES = {
    # sbatch_bootstrap_5d_gpu.sh:5 `--array=1-100`, :40 `--seed ${SLURM_ARRAY_TASK_ID}`
    "bootstrap replica seed": (1, 100),
    # sbatch_seedscan_split_5d.sh:5 `--array=1-24`, :19 `--split-seed ${SLURM_ARRAY_TASK_ID}`
    "seedscan split seed": (1, 24),
    # unified_throw_cov.py:245 `default_rng(args.draw_seed + gj)` with gj 0..159 at draw_seed 1000
    "uthrow per-throw draw seed": (1000, 1159),
    # NOT INCLUDED AND NAMED SO: lane C reports a PET-family band that makes k = 2000 dirty. This
    # lane has not measured that range, so it is absent rather than guessed -- and its absence is the
    # reason this table is DATA. Adding it is a one-line change here, not a change to the predicate.
}


def forbidden_offsets(lo, hi, baselines=None, ranges=None):
    """Every `k` in `[lo, hi]` that slides a baseline into a per-unit seed range."""
    B = dict(baselines) if baselines is not None else {g: b for g, b in group_baselines().items()}
    R = dict(ranges) if ranges is not None else PER_UNIT_SEED_RANGES
    bad = {}
    for k in range(int(lo), int(hi) + 1):
        for g, b in B.items():
            for nm, (rlo, rhi) in R.items():
                if rlo <= b + k <= rhi:
                    bad.setdefault(k, []).append(f"{g} estimator seed {b + k} lands in {nm} [{rlo},{rhi}]")
    return bad


#: The archive's OWN coincidences, exempt because they ARE the archive. `(group, range name, the
#: estimator seed at which the coincidence occurs)`.
#:
#: WHY AN ALLOWLIST AND NOT `j != 0`, which is lane C's reason and the whole point of wiring this: a
#: MEMBER SKIP passes ANY coincidence at the anchor, including one a later `--array` widening
#: introduces. A two-entry allowlist FAILS the moment a third appears -- and a third appearing at the
#: anchor is exactly the event nobody would otherwise notice, because the anchor is the member
#: everyone has already agreed is special.
#:
#: WHY THE SEED VALUE IS PART OF THE KEY, which is a STRENGTHENING of the two-entry form as specified
#: and is flagged as a deviation rather than assumed. Keyed on `(group, range)` alone, the exemption
#: would also excuse `k = 5`'s coincidence -- bootstrap replica 47 against estimator seed 47 -- because
#: that is the same group against the same range. Pinning the seed exempts ONLY the coincidence the
#: published product actually has, so the allowlist covers `k = 0` and nothing else, without ever
#: naming `k`.
#:
#: AND THE STRUCTURAL REASON THE EXEMPTION IS CORRECT RATHER THAN CONVENIENT, lane C's, better than
#: either option that was on the table: A CLEAN ANCHOR IS NOT AN ANCHOR. The anchor's function is
#: reproducing the published product exactly; the published product HAS these coincidences; so a run
#: without them is not the archive, and a run reproducing the archive has them. THE CONFOUND AND THE
#: ANCHORING ARE THE SAME FACT. Dropping `j = 0` does not cost a member -- it costs the ANCHOR, leaving
#: a 49-member scan with no tie to any published value, which re-imports the defect that refused (i).
COINCIDENCE_ALLOWLIST = {
    # unified_throw_cov.py:245 -- production ran `--seed 1000` for BOTH roles, so throw 0's draw RNG
    # has always been seeded identically to the estimator. Present in every archived slab.
    ("g2", "uthrow per-throw draw seed", 1000),
    # sbatch_bootstrap_5d_gpu.sh:5,40 -- replica 42 has always drawn its Poisson weights from seed 42
    # while its estimator was seeded 42 (bootstrap_nd.py:19 default). Present in every archived replica.
    ("g1", "bootstrap replica seed", 42),
}


def unexempted_coincidences(offsets, baselines=None, ranges=None, allowlist=None):
    """`{k: [reasons]}` for coincidences that are NOT the archive's own."""
    B = dict(baselines) if baselines is not None else {g: b for g, b in group_baselines().items()}
    R = dict(ranges) if ranges is not None else PER_UNIT_SEED_RANGES
    A = set(COINCIDENCE_ALLOWLIST if allowlist is None else allowlist)
    out = {}
    for k in sorted({int(x) for x in offsets}):
        for g, b in B.items():
            for nm, (rlo, rhi) in R.items():
                seed = b + k
                if not (rlo <= seed <= rhi):
                    continue
                if (g, nm, seed) in A:
                    continue
                out.setdefault(k, []).append(
                    f"{g} estimator seed {seed} lands in {nm} [{rlo},{rhi}]")
    return out


def assert_offsets_are_clean(offsets, baselines=None, ranges=None, allowlist=None):
    """FAIL CLOSED on any offset that creates an estimator/draw seed coincidence inside a member.

    Returns the number of (offset, baseline, range) combinations actually examined, so a caller can
    refuse a vacuous pass -- the same non-vacuity requirement as the pairwise check.
    """
    ks = sorted({int(k) for k in offsets})
    if not ks:
        raise SystemExit("[FAIL] no offsets given; a clean-offset check over an empty grid is not a pass")
    B = dict(baselines) if baselines is not None else {g: b for g, b in group_baselines().items()}
    R = dict(ranges) if ranges is not None else PER_UNIT_SEED_RANGES
    checked = len(ks) * len(B) * len(R)
    if checked == 0:
        raise SystemExit("[FAIL] the clean-offset check examined ZERO combinations; that needs at "
                         "least one baseline and one per-unit range. A clean result over nothing "
                         "checked is the check not running.")
    hits = unexempted_coincidences(ks, B, R, allowlist)
    if hits:
        lines = [f"[FAIL] {len(hits)} of {len(ks)} scanned offsets create an estimator/draw seed "
                 f"COINCIDENCE inside a member. The coincidence site moves with k, so each is a "
                 f"per-member structural difference and the spread is not attributable to the "
                 f"estimator seed alone."]
        for k in sorted(hits)[:8]:
            for why in hits[k]:
                lines.append(f"        k={k}: {why}")
        if len(hits) > 8:
            lines.append(f"        ... and {len(hits) - 8} more offsets")
        lines.append("        This is a DIFFERENT constraint from the pairwise aliasing rule: that "
                     "one is about two scan members sharing a seed, this one is about one member's "
                     "estimator and draw seeds coinciding. Both are required.")
        raise SystemExit("\n".join(lines))
    return checked
