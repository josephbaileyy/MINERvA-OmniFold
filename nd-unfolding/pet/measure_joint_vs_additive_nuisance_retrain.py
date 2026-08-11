#!/usr/bin/env python3
"""Cause 5's construction defect, MEASURED: the joint nuisance/retraining shift vs the additive blocks.

WHAT THIS SETTLES. The 2026-07-12 quarantine's cause 5 is "frozen PET weights", and
`VALIDATION_LEDGER.md:83-84` says the recoil-PET budget is quarantined pending *a joint
nuisance--retraining construction* and *selection-complete detector samples*. The note states the
requirement algebraically (`sec_pet.tex:117-127`): for a nuisance endpoint `u` the physical shift and
the induced retraining response form ONE joint shift

    delta_u = x_u^{varied+retrained} - x_CV,

and *"writing this as a frozen-map piece plus a retraining increment is an algebraic decomposition, but
adding the two separate covariances omits Cov(delta_frozen, delta_retrain) and its transpose. Positive
semidefiniteness of that sum does not restore the missing cross term."*

The historical recoil-PET assembly does exactly the thing that sentence rules out. `C_syst` is built
from `s_u = x_frozen - CV` and `C_retrain` from `Delta_u = x_retrain - x_frozen`, and the assembler's
own no-double-count note (`PET_UQ_PRODUCTION_STATUS.md:244-250`) argues they "sum DISJOINT quantities".
That argument is correct about the SHIFTS and silent about the COVARIANCE: with `delta = s + Delta`,

    outer(delta,delta) = outer(s,s) + outer(Delta,Delta) + outer(s,Delta) + outer(Delta,s)

and the assembly keeps only the first two terms. So the question "how wrong is the additive
construction, and in which direction" is not a matter of opinion -- every operand is stored per bin.

WHY IT IS WORTH MEASURING RATHER THAN ASSERTING. The Phase-7 record already reports
`corr(Delta,s) = -0.71` for MaRES:+1 and, at the integral level, that retraining *halves* the frozen
shift (frozen +1.83% -> retrain +0.89%). A negative cross term means the additive sum does not merely
omit something -- it **overstates** the joint covariance. If that holds across the material universes,
then the cause-5 repair is not only a correctness fix: the quarantined budget is inflated by its own
construction, and the direction of the correction is knowable before the full-event build exists.

SCOPE, AND IT IS NARROW. These are RECOIL-representation products. Per the 2026-08-01 full-event schema
landing, every pre-08-01 PET number is a DIFFERENT ESTIMATOR, so nothing here is a full-event
magnitude and no number here becomes quotable. What transfers is the STRUCTURE: the sign and rough size
of the cross term the additive construction drops, which is a design input for the full-event
construction that cause 5 actually requires. Stated because a per-band ratio computed on real arrays
reads as more portable than it is.

Also narrow in band coverage: the comparison is possible only on the universes where BOTH operands were
stored, i.e. the 6 Phase-7 material endpoint-universes. `C_syst` sums 13 bands over both endpoints, so
the aggregate below is NOT a restatement of the published C_total, and is labelled per-universe
throughout. Two points give a difference, not a spread (BEN-025) -- with 6 universes the spread is
reported as a realized range, never as a fitted interval.

THE IDENTITY IS CHECKED, NOT ASSUMED. `delta == s + Delta` should hold to machine precision because all
three come from the same three stored vectors. It is verified per universe and reported as a residual,
because if it fails the stored arrays are not what their names say and every ratio below is void. That
check is the whole reason to recompute `delta` from `x_retrain - cv` rather than from `s + Delta`.

SELF-TEST (--self-test) is a power test in BOTH directions on synthetic vectors with analytically known
answers: orthogonal operands must give ratio 1 (additive == joint), anti-correlated operands must give
ratio > 1 (additive OVERSTATES), positively-correlated operands must give ratio < 1 (additive
understates). A tool that cannot produce all three readings cannot be trusted to have found the middle
one in real data.

Usage:
  python3 measure_joint_vs_additive_nuisance_retrain.py --self-test
  python3 measure_joint_vs_additive_nuisance_retrain.py --p7-dir <dir> --json OUT.json
"""
import argparse
import glob
import json
import os
import sys

import numpy as np


def norms(s, d, delta):
    """All the ingredients for one universe. No verdict, just operands and derived quantities."""
    ns, nd, ndelta = float(np.linalg.norm(s)), float(np.linalg.norm(d)), float(np.linalg.norm(delta))
    dot = float(np.dot(s, d))
    additive = float(np.sqrt(ns * ns + nd * nd))
    # cosine similarity is the quantity that actually governs the cross term; Pearson is reported too
    # because the Phase-7 record quotes a "corr" whose definition it does not state, and the two are
    # NOT the same number unless both vectors are mean-zero across bins.
    cos = dot / (ns * nd) if ns > 0 and nd > 0 else float("nan")
    sc, dc = s - s.mean(), d - d.mean()
    denom = np.linalg.norm(sc) * np.linalg.norm(dc)
    pearson = float(np.dot(sc, dc) / denom) if denom > 0 else float("nan")
    return {
        "norm_s_frozen_shift": ns,
        "norm_delta_retrain_increment": nd,
        "norm_joint_shift": ndelta,
        "dot_s_delta": dot,
        "cross_term_2sdot": 2.0 * dot,
        "cosine_similarity_s_delta": cos,
        "pearson_corr_s_delta": pearson,
        "additive_block_norm_sqrt_ss_plus_dd": additive,
        "additive_over_joint": (additive / ndelta) if ndelta > 0 else float("nan"),
        # identity: ||delta||^2 == ||s||^2 + ||d||^2 + 2 s.d exactly
        "identity_norm_residual_rel": abs(ndelta ** 2 - (ns * ns + nd * nd + 2 * dot))
        / (ndelta ** 2) if ndelta > 0 else float("nan"),
    }


def self_test():
    """Both directions, analytically known. Returns 0 on success, 1 on failure."""
    rng = np.random.default_rng(0)
    n = 4096
    a = rng.normal(size=n)
    # build a second vector with a controlled cosine to `a`
    b0 = rng.normal(size=n)
    b0 -= a * (np.dot(a, b0) / np.dot(a, a))          # orthogonalize
    b0 /= np.linalg.norm(b0)
    au = a / np.linalg.norm(a)
    fails = []

    def case(name, cosine, expect):
        b = (cosine * au + np.sqrt(max(0.0, 1 - cosine ** 2)) * b0) * np.linalg.norm(a)
        r = norms(a, b, a + b)
        got = r["additive_over_joint"]
        ok = {"eq1": abs(got - 1.0) < 1e-9, "gt1": got > 1.0 + 1e-6, "lt1": got < 1.0 - 1e-6}[expect]
        print(f"  [self-test] {name:<28} cos={cosine:+.2f}  additive/joint={got:.6f}  "
              f"expect {expect:<4} {'PASS' if ok else 'FAIL'}")
        if r["identity_norm_residual_rel"] > 1e-12:
            fails.append(f"{name}: identity residual {r['identity_norm_residual_rel']:.3e}")
        if not ok:
            fails.append(f"{name}: additive/joint {got} did not satisfy {expect}")

    print("[self-test] power test in BOTH directions -- a tool that can only return one reading")
    print("[self-test] cannot be trusted to have measured the other:")
    case("orthogonal -> no effect", 0.0, "eq1")
    case("anti-correlated -> OVERSTATES", -0.71, "gt1")
    case("positively corr -> understates", +0.71, "lt1")
    # and the degenerate direction: an exactly cancelling pair must blow the ratio up, not silently pass
    r = norms(a, -a, a + (-a))
    print(f"  [self-test] exact cancellation         additive/joint="
          f"{r['additive_over_joint']:.3e}  expect huge/inf  "
          f"{'PASS' if not np.isfinite(r['additive_over_joint']) or r['additive_over_joint'] > 1e6 else 'FAIL'}")
    if fails:
        print("[self-test] FAILURES:")
        for f in fails:
            print("   ", f)
        return 1
    print("[self-test] PASS (all directions)")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--p7-dir", default=None,
                    help="directory holding pet_p7_<tag>_response.npz")
    ap.add_argument("--json", default=None)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--identity-tol", type=float, default=1e-10,
                    help="max relative residual on ||delta||^2 == ||s||^2+||d||^2+2s.d")
    a = ap.parse_args(argv)

    if a.self_test:
        return self_test()
    if not a.p7_dir:
        raise SystemExit("[joint] --p7-dir is required unless --self-test")

    files = sorted(glob.glob(os.path.join(a.p7_dir, "pet_p7_*_response.npz")))
    if not files:
        raise SystemExit(f"[joint] no response npz under {a.p7_dir} (fail closed)")

    per, skipped = {}, {}
    for f in files:
        base = os.path.basename(f)
        tag = base[len("pet_p7_"):-len("_response.npz")]
        with np.load(f, allow_pickle=True) as d:
            need = ("cv", "x_frozen", "x_retrain", "reported_mask", "s_reported", "delta_reported")
            missing = [k for k in need if k not in d.files]
            if missing:
                skipped[tag] = f"missing keys {missing}"
                continue
            m = np.asarray(d["reported_mask"]).astype(bool)
            cv = np.asarray(d["cv"], np.float64)[m]
            xf = np.asarray(d["x_frozen"], np.float64)[m]
            xr = np.asarray(d["x_retrain"], np.float64)[m]
            s_stored = np.asarray(d["s_reported"], np.float64)
            d_stored = np.asarray(d["delta_reported"], np.float64)
            universe = str(d["universe"]) if "universe" in d.files else tag

        # recompute from the primitives; the STORED s/delta are used only to cross-check
        s = xf - cv
        dd = xr - xf
        delta = xr - cv                      # the JOINT shift, the thing cause 5 requires

        rec = norms(s, dd, delta)
        rec["universe"] = universe
        rec["n_reported_bins"] = int(m.sum())
        # cross-checks against the stored vectors: if these disagree, the recomputation is not
        # measuring the same objects the published blocks were built from.
        rec["stored_vs_recomputed_s_max_absdev"] = float(np.max(np.abs(s - s_stored))) \
            if s_stored.shape == s.shape else None
        rec["stored_vs_recomputed_delta_max_absdev"] = float(np.max(np.abs(dd - d_stored))) \
            if d_stored.shape == dd.shape else None
        rec["integral"] = {"cv": float(cv.sum()), "frozen": float(xf.sum()),
                           "retrain": float(xr.sum())}
        rec["integral_frozen_rel"] = float(xf.sum() / cv.sum() - 1.0)
        rec["integral_retrain_rel"] = float(xr.sum() / cv.sum() - 1.0)
        per[tag] = rec

    # ---- aggregates, GROUPED, because one pooled number would be wrong twice --------------------
    # trace(outer(v,v)) == ||v||^2, so sqrt-trace of a sum of rank-1 blocks is the quadrature sum.
    #
    # (1) `null` is the identity retrain -- a training-noise control with s == 0. It is not a band, it
    #     is not in C_retrain's contributing set, and pooling it into a "construction" aggregate
    #     describes a construction nobody built. Excluded, and named so the exclusion is auditable.
    # (2) flux is NOT summed the way the knob bands are. C_syst's flux block is built over 100 PPFX
    #     universes, so a SINGLE flux universe's ||s|| is not a term in it -- and measurably so:
    #     flux:55 alone has ||s|| larger than the whole flux block's published sqrt-trace
    #     (1.0604e-38, pet_csyst_prelim summary). Pooling it with the knob bands would silently
    #     assert a rule the published assembly does not use, so it gets its own group.
    # The KNOB group is therefore the like-for-like number, and it is reported first.
    all_tags = sorted(per)
    noise_tags = [t for t in all_tags if t == "null"]
    flux_tags = [t for t in all_tags if t.startswith("flux")]
    knob_tags = [t for t in all_tags if t not in noise_tags and t not in flux_tags]

    def agg(tags_):
        ss_ = sum(per[t]["norm_s_frozen_shift"] ** 2 for t in tags_)
        dd2 = sum(per[t]["norm_delta_retrain_increment"] ** 2 for t in tags_)
        jj_ = sum(per[t]["norm_joint_shift"] ** 2 for t in tags_)
        a_ = float(np.sqrt(ss_ + dd2))
        j_ = float(np.sqrt(jj_))
        return {"universes": tags_, "n": len(tags_),
                "sum_sq_norm_s": ss_, "sum_sq_norm_delta_increment": dd2, "sum_sq_norm_joint": jj_,
                "additive_sqrt_trace": a_, "joint_sqrt_trace": j_,
                "additive_over_joint": (a_ / j_) if j_ > 0 else float("nan")}

    groups = {
        "knob_bands_LIKE_FOR_LIKE": agg(knob_tags),
        "flux_single_universe_NOT_COMPARABLE_TO_CSYST_FLUX_BLOCK": agg(flux_tags),
        "training_noise_control_EXCLUDED_FROM_CONSTRUCTION": agg(noise_tags),
        "all_pooled_DO_NOT_QUOTE": agg(all_tags),
    }
    tags = knob_tags
    ss = groups["knob_bands_LIKE_FOR_LIKE"]["sum_sq_norm_s"]
    dd_ = groups["knob_bands_LIKE_FOR_LIKE"]["sum_sq_norm_delta_increment"]
    jj = groups["knob_bands_LIKE_FOR_LIKE"]["sum_sq_norm_joint"]
    additive = groups["knob_bands_LIKE_FOR_LIKE"]["additive_sqrt_trace"]
    joint = groups["knob_bands_LIKE_FOR_LIKE"]["joint_sqrt_trace"]
    ratios = [per[t]["additive_over_joint"] for t in tags]
    idmax = max(per[t]["identity_norm_residual_rel"] for t in all_tags)

    payload = {
        "schema": "pet-joint-vs-additive-nuisance-retrain-v1",
        "question": ("cause 5 requires delta_u = x^{varied+retrained} - x_CV as ONE joint shift; the "
                     "historical assembly sums outer(s,s) + outer(Delta,Delta) and drops the cross "
                     "terms. This measures the size and SIGN of what is dropped."),
        "scope": ("RECOIL-representation products. Pre-2026-08-01 PET numbers are a DIFFERENT "
                  "ESTIMATOR than the full-event one cause 5's replacement belongs to, so no "
                  "magnitude here is quotable and none transfers. What transfers is the sign and "
                  "rough size of the omitted cross term, as a design input."),
        "band_coverage_caveat": ("only the Phase-7 material endpoint-universes store both operands. "
                                 "C_syst sums 13 bands over both endpoints, so the aggregate here is "
                                 "NOT a restatement of the published C_total."),
        "n_universes_measured": len(all_tags),
        "universes_measured": all_tags,
        "headline_group": "knob_bands_LIKE_FOR_LIKE",
        "grouping_rationale": (
            "null is the identity-retrain training-noise control (s == 0) and is not a band in "
            "C_retrain's contributing set. flux is built over 100 PPFX universes in C_syst, so one "
            "flux universe's ||s|| is not a term in that block -- flux:55's ||s|| alone exceeds the "
            "published whole-flux sqrt-trace 1.0604e-38. Pooling either into one number would assert "
            "a construction rule the published assembly does not use."),
        "aggregates_by_group": groups,
        "skipped": skipped,
        "identity_check": {
            "claim": "||delta||^2 == ||s||^2 + ||Delta||^2 + 2 s.Delta, exactly",
            "max_relative_residual": idmax,
            "tolerance": a.identity_tol,
            "pass": bool(idmax <= a.identity_tol),
        },
        "headline_knob_aggregate": {
            "sum_sq_norm_s": ss,
            "sum_sq_norm_delta_increment": dd_,
            "sum_sq_norm_joint": jj,
            "additive_sqrt_trace": additive,
            "joint_sqrt_trace": joint,
            "additive_over_joint": additive / joint if joint > 0 else float("nan"),
            "note": "trace(outer(v,v)) == ||v||^2, so these are quadrature sums of rank-1 blocks",
        },
        "per_universe_additive_over_joint": {
            "values": {t: per[t]["additive_over_joint"] for t in tags},
            "realized_min": min(ratios), "realized_max": max(ratios),
            "note": ("realized range over 6 universes, NOT a fitted interval -- with 6 points a "
                     "gaussian spread would be the BEN-025 error"),
        },
        "per_universe": per,
    }

    print(f"[joint] universes: {len(tags)}  identity max rel residual {idmax:.3e} "
          f"({'PASS' if idmax <= a.identity_tol else 'FAIL'})")
    print(f"{'universe':<24} {'||s||':>12} {'||Delta||':>12} {'||joint||':>12} "
          f"{'additive':>12} {'add/joint':>10} {'cos':>7} {'pearson':>8}")
    for t in tags:
        r = per[t]
        print(f"{r['universe']:<24} {r['norm_s_frozen_shift']:12.5e} "
              f"{r['norm_delta_retrain_increment']:12.5e} {r['norm_joint_shift']:12.5e} "
              f"{r['additive_block_norm_sqrt_ss_plus_dd']:12.5e} "
              f"{r['additive_over_joint']:10.4f} {r['cosine_similarity_s_delta']:+7.3f} "
              f"{r['pearson_corr_s_delta']:+8.3f}")
    print("\n[joint] AGGREGATES BY GROUP -- the knob group is the like-for-like one:")
    for gname, g in payload["aggregates_by_group"].items():
        if not g["n"]:
            continue
        print(f"  {gname}")
        print(f"    n={g['n']}  additive {g['additive_sqrt_trace']:.6e}  "
              f"joint {g['joint_sqrt_trace']:.6e}  additive/joint {g['additive_over_joint']:.6f}")
    print("  >1 means the additive construction OVERSTATES the joint covariance.")

    if not payload["identity_check"]["pass"]:
        print("[joint] *** IDENTITY FAILED -- the stored arrays are not what their names say and "
              "every ratio above is void. Reporting the failure rather than the ratios. ***")

    if a.json:
        with open(a.json, "w") as fh:
            json.dump(payload, fh, indent=2)
        print(f"[joint] receipt -> {a.json}")
    return 0 if payload["identity_check"]["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
