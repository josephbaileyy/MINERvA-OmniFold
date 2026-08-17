#!/usr/bin/env python3
"""Quarantine cause 1 for X: the per-band endpoint census (P leg) and the one-sided magnitude (M leg).

Predeclaration: docs/orchestration/PREDECLARE-20260817-cause1-endpoint-census-and-magnitude.md

WHAT IS OPEN AND WHY THIS CLOSES IT BY READING RATHER THAN REBUILDING.
`CRITERIA-20260811` section 2 cause 1 asks for two things this repo does not have:

  P: "X's receipt records ... both +/- endpoints present for every band and an exact contiguous
      100-universe flux bank."                      -> no per-band endpoint census exists for X
  M: "sqrt-Tr and per-bin median of X built both ways on X's OWN bank -- one-sided CV-centered vs
      mean-centered -- reported as a distribution, not a max (BEN-064).
      *This number does not exist anywhere.*"

X's band covariances are built by `analyze_universes_5d.py:91-104` out of per-universe flat vectors
that are already on disk. So both legs are one read pass. Nothing is re-unfolded and no covariance
product is rebuilt or replaced.

FIDELITY: this module IMPORTS `load_flat`, `UNI_RE` and `category_for_band` FROM
`analyze_universes_5d` rather than reimplementing them. If this reconstruction disagrees with the
committed summary, the disagreement cannot be my parsing or my band grouping -- it is the same code
production ran. That is the point of the positive control below and it is why the import is not a
convenience.

DIAGONAL-ONLY, BY SUFFICIENCY AND NOT AS A SHORTCUT. The criterion is phrased over sqrt-trace and
per-bin median sigma. Both depend only on the diagonal:

    as-built (mean-centered, biased 1/N, analyze_universes_5d:96-97):
        Z = D - D.mean(axis=0);  diag_b = (Z**2).sum(axis=0) / N
    one-sided CV-centered (the defect, outer(x_{+1sigma} - CV)):
        diag_b = d_ep ** 2

so no 10694x10694 matrix is ever materialised. **This therefore says NOTHING about off-diagonal
structure**, and no claim about correlation structure is made anywhere in the output.

THE COUNTERFACTUAL IS APPLIED ONLY TO N==2 PAIR BANDS. The defect is defined for a +/-pair. `Flux`
(N=100) has no "the +1sigma endpoint"; `__Normalization_flat` is a documented rank-1 band and not a
one-sided construction; `2p2h` has N=3 and is NOT a pair (declared unknown, predeclaration section 4).
All three are carried UNCHANGED in both totals, so the difference between the totals is attributable
to the pair bands alone. Their exclusion is reported, not silent.

WHICH INDEX IS +1sigma IS NOT ASSUMED. `unified_throw_cov.py:52-53` says idx 0 = -1sigma, idx 1 =
+1sigma, but that is a comment in a different module, so the one-sided form is computed BOTH ways and
both are reported.

ADOPTS NOTHING. Every ROOT is opened READ; the only write is the output JSON. values.tex untouched.

Usage (on Perlmutter, inside the ROOT env):
    source setup_salloc_env.sh
    python3 receipt_cause1_endpoint_census_5d.py --out uq_5d/receipt_cause1_endpoint_census_5d.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from collections import defaultdict

import numpy as np

# Production's own loader, regex and category map -- imported, never reimplemented.
from analyze_universes_5d import UNI_RE, category_for_band, load_flat

CV_PATH = "products/5d/xsec_5d_MEFHC_5iter_lgbm.root"
SWEEP_GLOB = "uq_5d/universe_sweep_bkgaware/5d_xsec_*_uni_full_*.root"
ADD_NORM = 0.014          # sbatch_finalize_5d_bkgaware_gpu.sh:26

# Committed reproduction targets: uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_summary.txt
TARGETS = {
    "reported_bins": 10694,
    "total_bins": 65856,
    "total_syst_sqrt_trace": 4.3515e-38,
    "total_syst_median_rel_pct": 13.235,
    "category_sum_sqrt_trace": {
        "Flux": 3.993e-39,
        "Models": 8.964e-38,
        "Normalization": 4.507e-39,
        "Hadronic response": 4.017e-38,
        "Muon reconstruction": 2.789e-38,
    },
}
# The summary prints 4 significant figures, so equality is asserted at that precision and the
# tolerance is stated rather than left to a reader to infer.
REPRO_RTOL = 5e-4
REPRO_RTOL_NOTE = ("uq_universe_5d_summary.txt prints 4 significant figures; 5e-4 is half a unit in "
                   "the last printed place. Not a fitted tolerance.")


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(16 * 1024**2), b""):
            h.update(chunk)
    return h.hexdigest()


def git_rev(repo: str) -> dict:
    def run(argv):
        try:
            return subprocess.run(argv, cwd=repo, capture_output=True, text=True,
                                  check=False).stdout.strip()
        except Exception:  # noqa: BLE001
            return None
    return {"head": run(["git", "rev-parse", "HEAD"]),
            "dirty": bool(run(["git", "status", "--porcelain"]))}


def main() -> int:
    import glob as globmod

    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="/pscratch/sd/j/josephrb/MINERvA-OmniFold")
    ap.add_argument("--out", default="uq_5d/receipt_cause1_endpoint_census_5d.json")
    args = ap.parse_args()
    nd = os.path.join(args.repo, "nd-unfolding")
    os.chdir(nd)

    receipt = {
        "schema": "cause1-endpoint-census-and-magnitude/1",
        "written_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "predeclaration": "docs/orchestration/PREDECLARE-20260817-cause1-endpoint-census-and-magnitude.md",
        "criteria": "docs/orchestration/CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md",
        "purpose": ("Cause 1's P leg (per-band endpoint census) and M leg (one-sided CV-centered vs "
                    "mean-centered sqrt-trace and per-bin median on X's own bank). Reads existing "
                    "universe vectors; adopts nothing, rebuilds nothing, makes no value quotable."),
        "adopts_nothing": True,
        "values_tex_untouched": True,
        "reader_sha256": sha256_file(os.path.abspath(__file__)),
        "production_module_sha256": sha256_file(os.path.join(nd, "analyze_universes_5d.py")),
        "git": git_rev(args.repo),
        "inputs": {"cv": CV_PATH, "glob": SWEEP_GLOB, "add_norm": ADD_NORM},
        "method": {
            "diagonal_only": True,
            "why_sufficient": ("The criterion is phrased over sqrt-trace and per-bin median sigma; "
                               "both depend only on the diagonal. No 10694^2 matrix is formed. This "
                               "says NOTHING about off-diagonal structure and no such claim is made."),
            "as_built": "Z = D - D.mean(axis=0); diag = (Z**2).sum(axis=0)/N   [analyze_universes_5d:96-97]",
            "one_sided": "diag = d_ep**2, i.e. diag(outer(x_ep - CV)); computed for BOTH ep in {0,1}",
            "counterfactual_scope": ("N==2 pair bands only. Flux (N=100), 2p2h (N=3) and "
                                     "__Normalization_flat are carried UNCHANGED in both totals."),
        },
        "reproduction_tolerance": {"rtol": REPRO_RTOL, "note": REPRO_RTOL_NOTE},
    }

    cv = load_flat(CV_PATH)
    paths = sorted(globmod.glob(SWEEP_GLOB))
    rep = cv > 0
    n_rep = int(rep.sum())
    cv_rep = cv[rep]
    print(f"[c1] CV bins={cv.size} reported={n_rep}  files={len(paths)}", flush=True)

    # ---- census: group exactly as production does, and record what it SKIPS ------------------
    by_band: dict[str, list] = defaultdict(list)
    skipped = []
    for p in paths:
        m = UNI_RE.match(os.path.basename(p))
        if not m:
            skipped.append(os.path.basename(p))
            continue
        by_band[m.group("band")].append((int(m.group("idx")), p))

    census = {}
    for band, entries in sorted(by_band.items()):
        idxs = sorted(i for i, _ in entries)
        census[band] = {
            "n_universes": len(idxs),
            "indices": idxs,
            "category": category_for_band(band),
            "is_pm_pair": len(idxs) == 2 and idxs == [0, 1],
            "contiguous_from_zero": idxs == list(range(len(idxs))),
            "both_endpoints_present": (0 in idxs and 1 in idxs),
        }
    receipt["census"] = {
        "n_files_matched_glob": len(paths),
        "n_files_grouped": len(paths) - len(skipped),
        "n_bands": len(census),
        "skipped_files_not_matching_UNI_RE": skipped,
        "skipped_note": ("Production's UNI_RE requires a trailing _<digits>; these are skipped by "
                         "analyze_universes_5d too and contribute to no band."),
        "per_band": census,
    }

    pair_bands = [b for b, c in census.items() if c["is_pm_pair"]]
    non_pair = {b: c["n_universes"] for b, c in census.items() if not c["is_pm_pair"]}
    flux = census.get("Flux", {})
    flux_ok = flux.get("n_universes") == 100 and flux.get("contiguous_from_zero") is True
    missing_ep = [b for b, c in census.items()
                  if c["n_universes"] == 2 and not c["both_endpoints_present"]]
    receipt["census"]["summary"] = {
        "n_pm_pair_bands": len(pair_bands),
        "non_pair_bands": non_pair,
        "flux_exactly_100_contiguous": flux_ok,
        "pair_bands_missing_an_endpoint": missing_ep,
    }
    print(f"[c1] census: {len(census)} bands, {len(pair_bands)} +/- pairs, "
          f"non-pair {non_pair}, flux_ok={flux_ok}", flush=True)

    # ---- load once, compute both forms -------------------------------------------------------
    as_built_diag = np.zeros(n_rep)
    one_sided_diag = {0: np.zeros(n_rep), 1: np.zeros(n_rep)}
    per_band = {}

    for band, entries in sorted(by_band.items()):
        D = np.stack([load_flat(p)[rep] - cv_rep for _, p in sorted(entries)], axis=0)
        if D.shape[0] < 2:
            print(f"[c1]   [skip] {band}: {D.shape[0]} universe(s)", flush=True)
            continue
        Z = D - D.mean(axis=0, keepdims=True)
        d_ab = (Z ** 2).sum(axis=0) / D.shape[0]
        as_built_diag += d_ab
        entry = {"n": int(D.shape[0]), "category": category_for_band(band),
                 "trace_as_built": float(d_ab.sum()),
                 "sqrt_trace_as_built": float(np.sqrt(max(d_ab.sum(), 0.0)))}

        if census[band]["is_pm_pair"]:
            order = [i for i, _ in sorted(entries)]
            for ep in (0, 1):
                d_os = D[order.index(ep)] ** 2
                one_sided_diag[ep] += d_os
                entry[f"trace_one_sided_ep{ep}"] = float(d_os.sum())
                entry[f"ratio_one_sided_ep{ep}_over_as_built"] = (
                    float(d_os.sum() / d_ab.sum()) if d_ab.sum() > 0 else None)
            entry["counterfactual_applied"] = True
        else:
            # carried UNCHANGED into both totals; recorded so the exclusion is visible
            for ep in (0, 1):
                one_sided_diag[ep] += d_ab
            entry["counterfactual_applied"] = False
            entry["excluded_reason"] = (
                "N != 2, so there is no '+1 sigma endpoint'; carried unchanged in both totals")
        per_band[band] = entry
        print(f"[c1]   {band:24s} N={entry['n']:3d} sqrtTr={entry['sqrt_trace_as_built']:.3e}"
              + (f"  ratios ep0={entry.get('ratio_one_sided_ep0_over_as_built'):.4f}"
                 f" ep1={entry.get('ratio_one_sided_ep1_over_as_built'):.4f}"
                 if entry["counterfactual_applied"] else "   [carried unchanged]"), flush=True)

    # normalization band: rank-1 by design, identical in both totals
    v = ADD_NORM * cv_rep
    d_norm = v ** 2
    as_built_diag += d_norm
    for ep in (0, 1):
        one_sided_diag[ep] += d_norm
    per_band["__Normalization_flat"] = {
        "n": None, "category": "Normalization",
        "trace_as_built": float(d_norm.sum()),
        "sqrt_trace_as_built": float(np.sqrt(d_norm.sum())),
        "counterfactual_applied": False,
        "excluded_reason": ("documented rank-1 outer(sigma*CV) norm band, not a one-sided "
                            "construction (CRITERIA section 2 cause 1); identical in both totals"),
    }
    receipt["per_band"] = per_band

    def summarise(diag):
        tr = float(diag.sum())
        relsig = np.sqrt(np.maximum(diag, 0)) / cv_rep
        return {"sqrt_trace": float(np.sqrt(max(tr, 0.0))),
                "median_rel_pct": float(100 * np.median(relsig))}

    ab = summarise(as_built_diag)
    os_res = {ep: summarise(one_sided_diag[ep]) for ep in (0, 1)}

    cat_sums = defaultdict(float)
    for band, e in per_band.items():
        cat_sums[e["category"]] += e["sqrt_trace_as_built"]

    # ---- positive control: reproduce the committed summary -----------------------------------
    checks, repro_ok = [], True

    def chk(label, got, want):
        nonlocal repro_ok
        ok = abs(got - want) <= REPRO_RTOL * abs(want)
        checks.append({"quantity": label, "reconstructed": got, "committed": want,
                       "rel_diff": abs(got - want) / abs(want), "match": ok})
        repro_ok = repro_ok and ok
        print(f"[c1] REPRO {label:34s} got={got:.6e} committed={want:.6e} "
              f"{'OK' if ok else 'MISMATCH'}", flush=True)

    bins_ok = (n_rep == TARGETS["reported_bins"] and cv.size == TARGETS["total_bins"])
    checks.append({"quantity": "reported_bins", "reconstructed": [n_rep, int(cv.size)],
                   "committed": [TARGETS["reported_bins"], TARGETS["total_bins"]],
                   "match": bins_ok})
    repro_ok = repro_ok and bins_ok
    chk("total syst sqrt-trace", ab["sqrt_trace"], TARGETS["total_syst_sqrt_trace"])
    chk("total syst median rel %", ab["median_rel_pct"], TARGETS["total_syst_median_rel_pct"])
    for cat, want in TARGETS["category_sum_sqrt_trace"].items():
        chk(f"category sum sqrt-tr {cat}", cat_sums[cat], want)

    receipt["positive_control"] = {
        "all_targets_reproduced": bool(repro_ok),
        "checks": checks,
        "why": ("An instrument that cannot rebuild the committed number is not measuring X, so a "
                "failure here VOIDS the one-sided comparison whatever it says (branch C2)."),
    }

    # ---- the M leg: distribution across pair bands, not a max (BEN-064) ----------------------
    ratios = {ep: sorted(per_band[b][f"ratio_one_sided_ep{ep}_over_as_built"]
                         for b in pair_bands) for ep in (0, 1)}
    def dist(xs):
        a = np.array(xs, dtype=float)
        return {"n_bands": int(a.size), "min": float(a.min()), "p25": float(np.percentile(a, 25)),
                "median": float(np.median(a)), "p90": float(np.percentile(a, 90)),
                "max": float(a.max()), "n_above_1": int((a > 1.0).sum()),
                "n_below_1": int((a < 1.0).sum())}

    receipt["magnitude_M"] = {
        "as_built": ab,
        "one_sided_ep0": os_res[0],
        "one_sided_ep1": os_res[1],
        "total_ratio_ep0": os_res[0]["sqrt_trace"] / ab["sqrt_trace"],
        "total_ratio_ep1": os_res[1]["sqrt_trace"] / ab["sqrt_trace"],
        "per_band_trace_ratio_distribution_ep0": dist(ratios[0]),
        "per_band_trace_ratio_distribution_ep1": dist(ratios[1]),
        "per_band_ratios_ep0_sorted": ratios[0],
        "per_band_ratios_ep1_sorted": ratios[1],
        "reported_as": "distribution across pair bands, not a max (BEN-064)",
        "scope_note": ("Totals differ ONLY through the pair bands; Flux, 2p2h and the norm band are "
                       "byte-identical contributions in both."),
    }

    # ---- branch selection, dominators first --------------------------------------------------
    degenerate = (
        abs(os_res[0]["sqrt_trace"] - ab["sqrt_trace"]) <= 1e-12 * ab["sqrt_trace"]
        and abs(os_res[1]["sqrt_trace"] - ab["sqrt_trace"]) <= 1e-12 * ab["sqrt_trace"]
    )
    census_bad = bool(missing_ep) or not flux_ok
    if not repro_ok:
        branch, why = "C2", ("reconstruction did not reproduce the committed summary; the one-sided "
                             "comparison is VOID")
    elif degenerate:
        branch, why = "C5", ("one-sided total equals as-built total; the counterfactual is not "
                             "implementing the defect and the measurement is VOID")
    elif census_bad:
        branch, why = "C3", (f"census incomplete: missing_endpoints={missing_ep}, "
                             f"flux_exactly_100_contiguous={flux_ok}")
    else:
        branch, why = "C1", ("all committed targets reproduced; census complete; one-sided total "
                             "differs from as-built and is reported as a per-band distribution")
    receipt["verdict"] = {
        "branch": branch,
        "why": why,
        "P_leg": ("MET -- per-band census committed, both endpoints present for every pair band, "
                  "Flux exactly 100 contiguous" if branch == "C1" else f"NOT ESTABLISHED ({branch})"),
        "M_leg": ("MEASURED -- the number CRITERIA says 'does not exist anywhere' now exists"
                  if branch == "C1" else f"NOT ESTABLISHED ({branch})"),
        "does_not_discharge": ("M MEASURED is not M ACCEPTABLE. Whether this magnitude leaves X's "
                               "published numbers standing is a physics-presentation judgement and "
                               "is NOT taken here."),
    }
    print(f"\n[c1] BRANCH {branch}: {why}", flush=True)
    print(f"[c1] as-built  sqrtTr={ab['sqrt_trace']:.6e} median={ab['median_rel_pct']:.4f}%",
          flush=True)
    for ep in (0, 1):
        print(f"[c1] one-sided ep{ep} sqrtTr={os_res[ep]['sqrt_trace']:.6e} "
              f"median={os_res[ep]['median_rel_pct']:.4f}%  "
              f"total ratio={os_res[ep]['sqrt_trace']/ab['sqrt_trace']:.6f}", flush=True)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    tmp = args.out + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(receipt, fh, indent=2, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, args.out)   # write-to-temp + rename (BEN-023)
    print(f"[c1] wrote {args.out}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
