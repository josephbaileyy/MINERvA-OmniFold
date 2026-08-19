#!/usr/bin/env python3
"""Stage 0: does the estimator-seed offset CHANGE THE NUMBERS? C_stat only, ~0.013 GPU-h.

THE ARGUMENT FOR STAGE 0 EXISTING AT ALL, which the mediator accepted: the argv probe established
that the offset REACHES the seed. It cannot establish that the seed CHANGES ANYTHING. Those are
different claims and only the second makes `M(ii)` measurable, so it is worth 0.013 GPU-h to separate
them before spending 39 A100-h on stage 1.

=====================================================================================================
THIS CHECKER'S POLARITY IS INVERTED FROM EVERY OTHER GATE IN THE CAMPAIGN, AND THAT IS THE WHOLE
DESIGN PROBLEM.

Everywhere else, PASS means "these agree". Here PASS means "THESE DIFFER". So the usual failure modes
land on the wrong side: a missing file, an unreadable file, an empty directory, a comparison of a file
against itself -- each of which produces NO OBSERVED DIFFERENCE, which under a naive implementation
reads as... a pass? no: as a FAIL, which is the safe direction, but a FAIL THAT MEANS "the offset does
nothing" when the truth is "nothing was compared". THAT MISREADING WOULD ABORT `M(ii)` FOR THE WRONG
REASON, and it would look like a physics result.

So this module reports THREE outcomes and never two:
    DISTINCT     the products differ, AND the difference is attributable to the estimator seed
    IDENTICAL    the products were genuinely compared and are the same -- a real negative result
    INCOMPARABLE nothing was established; the reason is named

`IDENTICAL` and `INCOMPARABLE` are both non-passes and they mean opposite things about the campaign.
Collapsing them is the defect this docstring exists to prevent.
=====================================================================================================

AND A DIFFERENCE IS NOT ENOUGH: IT MUST BE ATTRIBUTABLE. Two member trees can differ because their
estimator seeds differ (what we want to measure) or because they bootstrapped different DATA draws
(which would make the comparison meaningless and the difference large and spurious). So every pair is
checked on BOTH sides before its difference is believed:
    same `seed`            -- the replica id / data draw is IDENTICAL, so the draw is not the cause
    estimator_seed delta   -- equals the offset delta EXACTLY, so the estimator seed IS the cause
    both declared          -- an absent stamp is not a weak yes, it is a no
That is `my-recurring-failure-is-asymmetric-comparison` wired in rather than remembered: name both
sides before believing a delta.
"""
import argparse
import glob
import hashlib
import os
import re
import sys

import numpy as np

#: Keys `bootstrap_nd.py:49` writes. Presence of ALL of them is this module's completeness definition
#: for a replica -- validated here rather than assumed, because `rg_valid_npz` checks only that the
#: names requested are present and that every array MATERIALIZES, and the launcher requests none.
REPLICA_KEYS = ("seed", "xsec_flat", "shape", "total_xsec",
                "estimator_seed", "est_seed_offset_declared", "est_seed_offset")

REPLICA_RE = re.compile(r"res_boot_(\d+)\.npz$")

DISTINCT, IDENTICAL, INCOMPARABLE = "DISTINCT", "IDENTICAL", "INCOMPARABLE"


class Incomparable(Exception):
    """Raised for every reason that is NOT a physics answer. Never caught into a boolean."""


def validate_replica(path):
    """COMPLETE per REPLICA_KEYS, with every array materialized. Raises `Incomparable`.

    A truncated `.npz` is the same hazard as a `kRecovered` ROOT (`BEN-481`/B4) and a *compressed* npz
    is worse: the header can list every key while a member's deflate stream is truncated, so a
    key-presence check passes and `d[k]` raises. Hence every array is touched.
    """
    if not os.path.exists(path):
        raise Incomparable(f"absent: {path}")
    if os.path.getsize(path) < 1024:
        raise Incomparable(f"tiny ({os.path.getsize(path)} B): {path}")
    try:
        with np.load(path, allow_pickle=False) as d:
            names = list(d.files)
            missing = [k for k in REPLICA_KEYS if k not in names]
            if missing:
                raise Incomparable(f"missing keys {missing}: {path}")
            out = {k: d[k] for k in names}          # materialize: catches a truncated deflate stream
    except Incomparable:
        raise
    except Exception as exc:                        # zlib.error, EOFError, BadZipFile, ValueError...
        raise Incomparable(f"unreadable ({exc.__class__.__name__}: {exc}): {path}")
    x = np.asarray(out["xsec_flat"], float)
    if x.size == 0:
        raise Incomparable(f"empty xsec_flat: {path}")
    if not np.all(np.isfinite(x)):
        raise Incomparable(f"non-finite xsec_flat ({int((~np.isfinite(x)).sum())} bins): {path}")
    if not int(out["est_seed_offset_declared"]):
        raise Incomparable(
            f"est_seed_offset_declared == 0: {path}\n"
            "  This product may have come from an UNHOOKED launcher stamping its baseline, which is "
            "indistinguishable from a deliberate k=0 member. An absent positive declaration is a NO.")
    return out


def _replicas(member_root):
    """Replica id -> path under a member root. Raises `Incomparable` on an empty or absent tree."""
    if not os.path.isdir(member_root):
        raise Incomparable(f"member root is not a directory: {member_root}")
    found = {}
    for p in sorted(glob.glob(os.path.join(member_root, "boot_nd_5d", "res_boot_*.npz"))):
        m = REPLICA_RE.search(os.path.basename(p))
        if m:
            found[int(m.group(1))] = p
    if not found:
        raise Incomparable(
            f"no replicas matched {member_root}/boot_nd_5d/res_boot_*.npz\n"
            "  AN EMPTY GLOB IS EVIDENCE ABOUT THE SEARCH, NOT ABOUT THE WORLD. Stage 0 cannot report "
            "'the offset changes nothing' from a directory it found nothing in.")
    return found


def compare_member_pair(root_a, root_b, offset_a, offset_b):
    """The stage-0 measurement. Returns (verdict, report) and NEVER raises on a data condition.

    `report` carries the INGREDIENTS, not just the verdict -- per `CONVENTION-receipt-ingredients.md`
    every derived quantity ships enough that the reported numbers can contradict each other. Here that
    means per-replica max|delta|, the CV scale it is relative to, and the changed-bin count: a verdict
    of DISTINCT whose max|delta| is 0 would be self-contradicting and visibly so.
    """
    rep = {"root_a": root_a, "root_b": root_b, "offset_a": offset_a, "offset_b": offset_b,
           "replicas": [], "why": ""}

    # SELF-COMPARISON IS THE FAILURE C NAMED AT STAGE 1 AND IT APPLIES HERE FIRST: at stage 1 a
    # bit-exact pass and "you compared the archive to itself" are the same observation. Two equal
    # offsets, or two paths resolving to one directory, produce IDENTICAL for a reason that says
    # nothing about the estimator seed -- so it is INCOMPARABLE, not IDENTICAL.
    if offset_a == offset_b:
        rep["why"] = (f"both offsets are {offset_a} -- comparing a member to itself. A null here is "
                      "about the comparison, not about the seed.")
        return INCOMPARABLE, rep
    try:
        if os.path.realpath(root_a) == os.path.realpath(root_b):
            rep["why"] = (f"both roots resolve to {os.path.realpath(root_a)} -- one directory, two "
                          "names. Distinct offsets MUST have distinct member roots by construction, "
                          "so this means the member axis did not apply.")
            return INCOMPARABLE, rep
        a_paths, b_paths = _replicas(root_a), _replicas(root_b)
    except Incomparable as exc:
        rep["why"] = str(exc)
        return INCOMPARABLE, rep

    shared = sorted(set(a_paths) & set(b_paths))
    only_a, only_b = sorted(set(a_paths) - set(b_paths)), sorted(set(b_paths) - set(a_paths))
    rep.update(n_a=len(a_paths), n_b=len(b_paths), n_shared=len(shared),
               only_a=only_a, only_b=only_b)
    if not shared:
        rep["why"] = (f"no replica id is present in BOTH members (a has {sorted(a_paths)[:5]}..., "
                      f"b has {sorted(b_paths)[:5]}...). Nothing was compared.")
        return INCOMPARABLE, rep
    if only_a or only_b:
        # NOT fatal -- the shared set is still a valid comparison -- but it must be REPORTED, because a
        # silently reduced denominator is how "all replicas differ" gets said about three of them.
        rep["partial"] = (f"asymmetric population: {len(only_a)} only in a, {len(only_b)} only in b; "
                          f"comparing the {len(shared)} shared")

    n_diff = 0
    for rid in shared:
        try:
            A, B = validate_replica(a_paths[rid]), validate_replica(b_paths[rid])
        except Incomparable as exc:
            rep["why"] = f"replica {rid}: {exc}"
            return INCOMPARABLE, rep

        # BOTH SIDES NAMED BEFORE THE DELTA IS BELIEVED ----------------------------------------------
        if int(A["seed"]) != int(B["seed"]):
            rep["why"] = (f"replica {rid}: DATA DRAW DIFFERS -- seed {int(A['seed'])} vs "
                          f"{int(B['seed'])}. Any difference in xsec_flat would be attributable to the "
                          "draw, not the estimator seed, so this is not the measurement stage 0 makes.")
            return INCOMPARABLE, rep
        d_est = int(B["estimator_seed"]) - int(A["estimator_seed"])
        if d_est != offset_b - offset_a:
            rep["why"] = (f"replica {rid}: estimator_seed delta {d_est} != offset delta "
                          f"{offset_b - offset_a}. The products may differ, but not demonstrably "
                          "BECAUSE of the estimator seed.")
            return INCOMPARABLE, rep
        for side, S, k in (("a", A, offset_a), ("b", B, offset_b)):
            if int(S["est_seed_offset"]) != k:
                rep["why"] = (f"replica {rid} side {side}: stamped offset {int(S['est_seed_offset'])} "
                              f"!= the offset this tree is declared to be, {k}")
                return INCOMPARABLE, rep

        xa = np.asarray(A["xsec_flat"], float)
        xb = np.asarray(B["xsec_flat"], float)
        if xa.shape != xb.shape:
            rep["why"] = f"replica {rid}: shape {xa.shape} vs {xb.shape}"
            return INCOMPARABLE, rep
        delta = np.abs(xb - xa)
        scale = float(np.abs(xa).max()) or 1.0
        changed = int((delta > 0).sum())
        # THE DENOMINATOR THAT MATTERS IS THE SUPPORT, NOT THE GRID -- and my first version shipped only
        # the grid, which made the headline number wrong by construction.
        #
        # `changed/nbins` reads as "the seed moved 16% of bins". But ~84% of the 65,856-bin 5D grid is
        # EMPTY (the analysis reports on the `cv > 0` mask, 10,694 bins -- analyze_universes_5d.py:160,
        # and "the same 10694 support" at p4_evidence.py:137). A bin that is zero in both members cannot
        # change, so it is not evidence of anything. Against the support the same measurement reads
        # "the seed moved ~98% of the bins that CAN move", which is a far stronger statement and the
        # correct one. SHIPPING ONLY THE GRID SIZE MADE A STRONG RESULT LOOK WEAK.
        #
        # This is BEN-077 against my own report: a derived quantity must ship its ingredients, and the
        # ingredient of "changed bins" is HOW MANY BINS WERE EVER IN PLAY.
        nz_a = int(np.count_nonzero(xa))
        nz_either = int(np.count_nonzero(np.abs(xa) + np.abs(xb)))
        row = {"replica": rid, "nbins": int(xa.size), "changed_bins": changed,
               "support_a": nz_a, "support_either": nz_either,
               "changed_frac_of_support": (changed / nz_either) if nz_either else None,
               "max_abs_delta": float(delta.max()), "scale_max_abs_a": float(np.abs(xa).max()),
               # NAMED PRECISELY BECAUSE THE SHORT NAME MISLED A READER: this is max|delta| divided by
               # the PEAK bin value of side a, i.e. the largest absolute change expressed as a fraction
               # of the largest bin. It is NOT a per-bin relative error and NOT a typical bin's change.
               # A report saying "0.6-1.2% relative" invites exactly that second reading, so the median
               # per-bin relative change over the support is shipped beside it.
               "max_delta_over_peak": float(delta.max() / scale),
               "median_rel_delta_on_support": float(np.median(
                   (delta[np.abs(xa) > 0] / np.abs(xa)[np.abs(xa) > 0]))) if nz_a else None,
               "max_rel_delta": float(delta.max() / scale),   # retained: existing readers
               "digest_a": hashlib.sha256(xa.tobytes()).hexdigest()[:16],
               "digest_b": hashlib.sha256(xb.tobytes()).hexdigest()[:16],
               "estimator_seed_a": int(A["estimator_seed"]),
               "estimator_seed_b": int(B["estimator_seed"])}
        row["identical"] = row["digest_a"] == row["digest_b"]
        if not row["identical"]:
            n_diff += 1
        rep["replicas"].append(row)

    rep["n_differing"] = n_diff
    if n_diff == 0:
        rep["why"] = (f"all {len(shared)} shared replicas are BIT-IDENTICAL across offsets "
                      f"{offset_a} and {offset_b}, with the data draw held fixed and the estimator "
                      "seeds confirmed to differ by the offset delta. THIS IS A REAL NEGATIVE RESULT: "
                      "the estimator seed does not move C_stat, so M(ii) is not measurable this way.")
        return IDENTICAL, rep
    if n_diff != len(shared):
        # Partial distinctness is not a pass. If the seed matters it should matter everywhere; some
        # replicas identical and some not means something other than the seed is in play.
        rep["why"] = (f"only {n_diff} of {len(shared)} shared replicas differ. Partial distinctness is "
                      "not a result -- if the estimator seed moves the estimate it should move every "
                      "replica, so an identical subset means something else is varying.")
        return INCOMPARABLE, rep
    return DISTINCT, rep


def format_report(verdict, rep):
    L = [f"[stage0] VERDICT: {verdict}",
         f"[stage0]   a: offset {rep['offset_a']:>7}  {rep['root_a']}",
         f"[stage0]   b: offset {rep['offset_b']:>7}  {rep['root_b']}"]
    if "n_shared" in rep:
        L.append(f"[stage0]   replicas: {rep.get('n_a')} / {rep.get('n_b')} found, "
                 f"{rep['n_shared']} shared, {rep.get('n_differing', '-')} differing")
    if rep.get("partial"):
        L.append(f"[stage0]   NOTE {rep['partial']}")
    for r in rep["replicas"]:
        frac = r.get("changed_frac_of_support")
        med = r.get("median_rel_delta_on_support")
        L.append(f"[stage0]   r{r['replica']:<4} est {r['estimator_seed_a']}->{r['estimator_seed_b']} "
                 f"{'IDENTICAL' if r['identical'] else 'differs'} "
                 f"changed {r['changed_bins']}/{r.get('support_either', '?')} of support "
                 f"({'--' if frac is None else format(100*frac, '.2f')}%) "
                 f"[grid {r['nbins']}] "
                 f"max|d| {r['max_abs_delta']:.6e} = {r['max_delta_over_peak']:.3e} of peak "
                 f"median rel on support {'--' if med is None else format(med, '.3e')} "
                 f"{r['digest_a']}->{r['digest_b']}")
    if rep.get("why"):
        L.append(f"[stage0]   WHY: {rep['why']}")
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root-a", required=True, help="member root for offset a (e.g. mii/member_k000000)")
    ap.add_argument("--root-b", required=True)
    ap.add_argument("--offset-a", type=int, required=True)
    ap.add_argument("--offset-b", type=int, required=True)
    a = ap.parse_args(argv)
    verdict, rep = compare_member_pair(a.root_a, a.root_b, a.offset_a, a.offset_b)
    print(format_report(verdict, rep))
    # THREE EXIT CODES, MATCHING THE THREE VERDICTS. A caller that only checks `!= 0` still behaves
    # correctly; a caller that wants to distinguish a negative RESULT from a broken COMPARISON can.
    return {DISTINCT: 0, IDENTICAL: 1, INCOMPARABLE: 2}[verdict]


if __name__ == "__main__":
    sys.exit(main())
