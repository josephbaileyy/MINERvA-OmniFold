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
import re


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
#: AND THE COINCIDENCE HAS NO OBSERVED BUILDER-SIDE CONSEQUENCE, measured by lane E on the one product
#: where a consequence would have shown: `replica_42` was the family's only non-zero Slurm exit, which
#: is the first place anyone would look for a seed-coincidence effect at index 42. E found the products
#: COMPLETE AND SOUND -- PASS line with the target digest, both artifacts and both `.done` markers
#: written, npy byte-for-byte the size of replicas 41 and 43, receipt in family range -- and exit 129 a
#: SIGHUP during interpreter TEARDOWN, after the writes, with the same crash present but exit-masked in
#: none of the other 49. NOTHING IN THE BUILDER FAILED AT INDEX 42, so there is no builder-side event
#: for the coincidence to explain. That CLOSES the question from the other side rather than weakening
#: the exemption: the coincidence is real in the seeds and so far invisible in the products, which is
#: precisely why lane C's displacement/leverage read is the test that decides materiality.
#:
#: E's transferable line, recorded because it generalises past this file: A SLURM EXIT STATUS DESCRIBES
#: THE PROCESS, NOT THE PRODUCT -- a task can fail with its output complete and correct. It is `BEN-023`
#: mirrored: that was a resume guard ACCEPTING an incomplete product because it existed; this is a
#: scheduler verdict REJECTING a complete one because the process died after making it. A guard
#: validating completeness rather than existence would accept `_42`, and would be right.
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


# ---------------------------------------------------------------------------------------------------
# C's ITEM 2: THE TARGET SET IS DERIVED, NOT LISTED.
#
# The lateral leg was missed because the plan enumerated HOOKED LAUNCHERS while a coherence group is
# defined by the SHARED SEED VALUE. A hand list was wrong by one leg in seven, so the list is retired.
#
# BUT THE DERIVED PREDICATE RETURNS A BIGGER ANSWER THAN SEVEN, AND THE EXTRA MEMBERS ARE A SECOND
# HAZARD RATHER THAN NOISE -- measured 2026-08-18 over 48 5D-scoped shell files: the seventh leg C
# named, PLUS NINE UNHOOKED VARIANTS OF THE SAME MODULES (`_fast`/non-`_fast`, `bkgaware`/plain,
# packed-loop, adopt). Those nine are not launchers the plan invokes; they are launchers someone could
# invoke INSTEAD of a hooked one and get baseline silently. So the predicate reports two classes and
# does not collapse them:
#
#   TARGETED and unhooked          -> HARD FAILURE. The plan invokes it; the offset would not reach it.
#   SAME-MODULE VARIANT, unhooked  -> SUBSTITUTION HAZARD. Naming it is the point; whether it must be
#                                     hooked or explicitly fenced is a specification call, not mine.
#
# SCOPE IS DERIVED TOO, from 5D artifact references rather than filenames, because "is this a 5D
# launcher" answered by name is the same defect one level up.
_FIVE_D = re.compile(r'(of_inputs_5d\.npz|uq_5d/|bank_uthrow_5d|bank_sweep_5d|_5d\.py|boot_nd_5d'
                     r'|seedscan_split_5d)')
_SEED_LITERAL = re.compile(r'--(?:estimator-)?seed\s+(42|1000)\b')
#: module basename -> the coherence group it belongs to, so a VARIANT is recognised by what it RUNS.
_LEG_MODULES = {
    "sweep_bank_5d.py": "g1",
    "bootstrap_nd.py": "g1",
    "seedscan_split.py": "g1",
    "unfold_nd_omnifold_unbinned.py": "g1",     # the lateral leg, item 7 ruling (a)
    "unified_throw_cov_5d.py": "g2",
    "unified_throw_cov.py": "g2",
}


def derive_seed_literal_sites(repo_root, targeted):
    """Every 5D-scoped shell file carrying an unhooked `42`/`1000` seed literal, split into the two
    classes above. `targeted` is the set of launchers the plan actually invokes.

    Returns `(hard_failures, substitution_hazards, n_scoped)`; the third is the denominator, so a
    caller can refuse a pass computed over nothing.
    """
    import subprocess
    listed = subprocess.run(["git", "-C", repo_root, "ls-files", "*.sh", "**/*.sh"],
                            capture_output=True, text=True).stdout.split()
    hard, haz, scoped = [], [], 0
    for rel in sorted(set(listed)):
        full = os.path.join(repo_root, rel)
        if not os.path.exists(full):
            continue
        with open(full, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        body = "\n".join(l for l in text.split("\n") if not l.lstrip().startswith("#"))
        if not _FIVE_D.search(body):
            continue
        scoped += 1
        lits = [(i, l.strip()) for i, l in enumerate(body.split("\n"), 1) if _SEED_LITERAL.search(l)]
        if not lits or OFFSET_ENV in text:
            continue
        base = os.path.basename(rel)
        groups = sorted({g for m, g in _LEG_MODULES.items() if m in body})
        row = {"file": rel, "sites": lits, "groups": groups}
        (hard if base in targeted else haz).append(row)
    return hard, haz, scoped


def assert_target_set_is_complete(repo_root, targeted):
    """FAIL CLOSED if any TARGETED launcher carries an unhooked seed literal. Hazards are returned,
    not raised -- they are a specification question and raising on them would make this module
    unusable until someone else's decision lands, which is how a check gets switched off."""
    hard, haz, scoped = derive_seed_literal_sites(repo_root, set(targeted))
    if scoped == 0:
        raise SystemExit("[FAIL] no 5D-scoped shell files found; the derived target set was computed "
                         "over ZERO files and a clean result means the walk did not run")
    if hard:
        lines = [f"[FAIL] {len(hard)} TARGETED launcher(s) carry an unhooked 42/1000 seed literal, so "
                 f"the offset would not reach them and those legs would run at baseline for every k:"]
        for r in hard:
            lines.append(f"        {r['file']}  groups={r['groups'] or ['?']}")
            for ln, txt in r["sites"][:3]:
                lines.append(f"            :{ln}  {txt[:88]}")
        raise SystemExit("\n".join(lines))
    return {"scoped_files": scoped, "targeted_clean": len(targeted),
            "substitution_hazards": [r["file"] for r in haz]}


# ---------------------------------------------------------------------------------------------------
#: The substitution hazards, FROZEN AS A CLOSED ENUMERATION. C's item 4: not raising on these leaves
#: the list decorative unless its test asserts EXACT EQUALITY. `len(hazards) > 0` and
#: `FROZEN <= hazards` both pass forever and discover nothing; equality fails the moment a tenth
#: appears. The nine block nobody; a tenth stops the build. Same device as the anchor allowlist.
FROZEN_SUBSTITUTION_HAZARDS = frozenset({
    # LOUD -- g2, backstopped by the F2 guard at unified_throw_cov.py:453, CONFIRMED BY RUN in both
    # directions rather than by reading it: slabs at 1000 vs a combine at 1000+k raises, and slabs at
    # 1000+k vs a combine at 1000 raises, while the matching pair is ACCEPTED.
    "nd-unfolding/sbatch_uthrow_run_5d.sh",
    "nd-unfolding/sbatch_uthrow_combine_5d.sh",
    "nd-unfolding/sbatch_j28_adopt_5d.sh",
    # SILENT -- g1, the sweep path, which has NO such guard: analyze_universes globs and
    # combine_cov_nd checks ids but not offset metadata. Remedy differs BY ROW, not by group.
    "nd-unfolding/sbatch_sweep_bank_5d_run.sh",
    "nd-unfolding/sbatch_unfold_5d_detector.sh",
    "nd-unfolding/sweep_run_bkgaware_packed_loop.sh",
    # OUT OF REACH rather than out of scope -- their outputs are products/pet/fps_envelope_5d*,
    # disjoint from all six canonical namespaces and from every member root, so they cannot
    # contaminate a member or a combine whatever their seeds. C's route, better than the
    # module-name one this lane used: "a different measurement" is a claim about INTENT; a disjoint
    # output tree is a fact about REACH.
    "nd-unfolding/sbatch_fps_reunfold_5d.sh",
    "nd-unfolding/sbatch_fps_reunfold_5d_xps.sh",
    "nd-unfolding/sbatch_fps_reunfold_5d_xps2.sh",
})

#: `%06d` in the member directory name widens rather than truncates, so nothing is lost -- but MIXED
#: widths break lexicographic ordering above 999999. C checked the headroom rather than asserting a
#: footgun: max offset is 58,800 at n=50 and 118,800 at n=100, so sort-safety holds to n <= 833. The
#: assertion exists anyway, in the direction the padding acts, so a later lane widening the STEP
#: rather than the count cannot walk into it.
MEMBER_DIR_SORT_SAFE_LIMIT = 1_000_000


def assert_offsets_are_sort_safe(offsets):
    """FAIL CLOSED if any offset would break lexicographic ordering of the member directories."""
    ks = [abs(int(k)) for k in offsets]
    if not ks:
        raise SystemExit("[FAIL] no offsets; a sort-safety check over an empty grid is not a pass")
    worst = max(ks)
    if worst >= MEMBER_DIR_SORT_SAFE_LIMIT:
        raise SystemExit(
            f"[FAIL] offset magnitude {worst} >= {MEMBER_DIR_SORT_SAFE_LIMIT}: the member directory "
            f"name is zero-padded to 6 digits, so this one widens and MIXED widths no longer sort "
            f"lexicographically. Widen the padding in lib_member_resume.sh:mr_member_dir and this "
            f"limit together, or the directory listing silently stops being ordered.")
    return worst
