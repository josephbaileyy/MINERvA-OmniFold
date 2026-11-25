#!/usr/bin/env python3
"""Per-p_par-strip ours/paper ratio receipt for KNOWN_ISSUES #5 (the low-p_par sum-ratio gradient).

WHAT IS MEASURED. For each of the 16 paper p_par strips j, the strip integral
    S_j = sum_{i in strip j, i in mask} xs_i * dpT_i
(i.e. dsigma/dp_par over the strip, a cross section) is formed for ours and for the paper on the
SAME mask, and R_j = S_j(ours) / S_j(paper) is reported with the paper-TotalCovariance standard
error of S_j(paper) propagated as sigma_j = sqrt(a_j^T C a_j), a_j the area vector of strip j.
The bare content-sum ratio (no dpT Jacobian) is also emitted, because the historical 2026-04-25
"strip sum-ratio" (0.60 at p_par 1.5-2 GeV/c rising to 1.00 above 20 GeV/c) does not record which
one it was; both conventions are printed so neither can be silently assumed.

Two masks: the 205 REPORTED bins (positive StatOnlyCovariance diagonal, asserted == 205) and the
185-bin STRICT INTERIOR used by the historical measurement (reported AND pt_hi/pz_lo <= tan 20 deg).

POWER CONTROL (built in, not optional). The instrument is also run on a SYNTHETIC input: ours
multiplied strip-by-strip by the recorded historical post-MINOS-fix gradient (Phase 11 table,
evidence tag prepublication-2026-08-20-0b329e8a:2d-unfolding/2D_OMNIFOLD_RUN_LOG_ARCHIVE.md:222-230,
interpolated in log p_par between the recorded strips). The receipt must report that gradient back.
If it does not, the instrument is blind and the production verdict is void (exit 4).

VERDICT RULE (predeclared in docs/orchestration/PLAN-20260923-issue26-issue5-studies.md §2):
GRADIENT ABSENT iff, on the 185-bin interior, (a) the low-strip mean R over p_par 1.5-2.5 GeV/c and
the high-strip mean R over p_par 20-60 GeV/c differ by less than 2 sigma of their paper-TotalCov
difference, AND (b) |R_j - 1| <= 2 sigma_j/S_j(paper) + 0.05 for both p_par < 2.5 strips. Otherwise
GRADIENT PRESENT. The verdict speaks only to the ours/paper cross-section ratio of the named file.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys

import numpy as np
import ROOT

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compare_to_paper_fullcov import (  # noqa: E402
    N, N_PT, N_PZ, tmatrix_to_numpy, flatten_th2d, flatten_ours, ANC_DIR, DEFAULT_OURS,
)
from agreement_windows_receipt import bin_areas  # noqa: E402
from reported_cells import th2d_edges  # noqa: E402  (uq/, which compare_to_paper_fullcov puts on sys.path)

PT_EDGES = [0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55, 0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50]
PZ_EDGES = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0]
TAN20 = math.tan(math.radians(20.0))

# Historical post-MINOS-fix strip ratios (Phase 11, 2026-04-25): (p_par lo, hi, ratio).
HISTORICAL_GRADIENT = [(1.5, 2.0, 0.60), (2.0, 2.5, 0.61), (5.0, 6.0, 0.85),
                       (10.0, 15.0, 0.90), (20.0, 40.0, 1.00)]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def strip_index():
    """GlobalID -> (ipt, ipz) zero-based, paper convention gid = ipt*16 + ipz."""
    ipt = np.repeat(np.arange(N_PT), N_PZ)
    ipz = np.tile(np.arange(N_PZ), N_PT)
    return ipt, ipz


def interior_mask(pt_edges=PT_EDGES, pz_edges=PZ_EDGES):
    ipt, ipz = strip_index()
    pt_hi = np.asarray(pt_edges)[1:][ipt]
    pz_lo = np.asarray(pz_edges)[:-1][ipz]
    return pt_hi / pz_lo <= TAN20


def historical_factor(pz_edges=PZ_EDGES):
    """Per-strip multiplicative gradient, log-p_par interpolation of the recorded strips."""
    c = np.array([math.sqrt(lo * hi) for lo, hi, _ in HISTORICAL_GRADIENT])
    r = np.array([x for _, _, x in HISTORICAL_GRADIENT])
    pzc = np.sqrt(np.asarray(pz_edges)[:-1] * np.asarray(pz_edges)[1:])
    return np.interp(np.log(pzc), np.log(c), r)  # flat extrapolation beyond the ends


def strips(ours_v, paper_v, area, cov, mask, area_ours=None, pz_edges=PZ_EDGES):
    """`area` is the paper's bin-area vector, `area_ours` ours (default `area`), and `pz_edges`
    the paper's p_par edges."""
    area_ours = area if area_ours is None else area_ours
    _, ipz = strip_index()
    rows = []
    for j in range(N_PZ):
        sel = mask & (ipz == j)
        if not sel.any():
            rows.append(None)
            continue
        a = np.where(sel, area, 0.0)
        s_o, s_p = float(np.where(sel, area_ours, 0.0) @ ours_v), float(a @ paper_v)
        sig = float(math.sqrt(max(a @ cov @ a, 0.0)))
        bo, bp = float(ours_v[sel].sum()), float(paper_v[sel].sum())
        rows.append(dict(pz_lo=float(pz_edges[j]), pz_hi=float(pz_edges[j + 1]), n_bins=int(sel.sum()),
                         S_ours=s_o, S_paper=s_p, sigma_paper_total=sig,
                         R=s_o / s_p, R_sigma=sig / s_p,
                         R_bare=bo / bp))
    return rows


def contrast(ours_v, paper_v, area, cov, mask, lo=(1.5, 2.5), hi=(20.0, 60.0), area_ours=None,
             pz_edges=PZ_EDGES):
    """Low-strip over high-strip integral ratio, with the paper-cov error of the difference of
    the fractional deviations propagated linearly (delta method). `area` is the paper's bin-area
    vector, `area_ours` ours (default `area`), and `pz_edges` the paper's p_par edges."""
    area_ours = area if area_ours is None else area_ours
    _, ipz = strip_index()
    pz_lo = np.asarray(pz_edges)[:-1][ipz]
    pz_hi = np.asarray(pz_edges)[1:][ipz]
    sl = mask & (pz_lo >= lo[0]) & (pz_hi <= lo[1])
    sh = mask & (pz_lo >= hi[0]) & (pz_hi <= hi[1])
    al, ah = np.where(sl, area, 0.0), np.where(sh, area, 0.0)
    Rl = float(np.where(sl, area_ours, 0.0) @ ours_v) / float(al @ paper_v)
    Rh = float(np.where(sh, area_ours, 0.0) @ ours_v) / float(ah @ paper_v)
    # d = R_l - R_h as a function of the paper vector p: grad_p = -R_l a_l/S_l + R_h a_h/S_h
    g = -Rl * al / float(al @ paper_v) + Rh * ah / float(ah @ paper_v)
    sig_d = float(math.sqrt(max(g @ cov @ g, 0.0)))
    return dict(R_low=Rl, R_high=Rh, diff=Rl - Rh, sigma_diff_paper_total=sig_d,
                n_sigma=(Rl - Rh) / sig_d if sig_d > 0 else float("nan"))


def verdict(rows, con):
    a = abs(con["diff"]) < 2.0 * con["sigma_diff_paper_total"]
    low = [r for r in rows if r is not None and r["pz_hi"] <= 2.5]
    b = all(abs(r["R"] - 1.0) <= 2.0 * r["R_sigma"] + 0.05 for r in low)
    return ("GRADIENT ABSENT" if (a and b) else "GRADIENT PRESENT"), dict(contrast_ok=a,
                                                                       low_strips_ok=b)


def measure(ours_v, paper_v, area, cov, mask, area_ours=None, pz_edges=PZ_EDGES):
    rows = strips(ours_v, paper_v, area, cov, mask, area_ours, pz_edges)
    con = contrast(ours_v, paper_v, area, cov, mask, area_ours=area_ours, pz_edges=pz_edges)
    v, parts = verdict(rows, con)
    return dict(strips=rows, contrast=con, verdict=v, verdict_parts=parts)


def positive_areas(h):
    """bin_areas(h), refusing a non-positive area rather than dividing by it later."""
    a = bin_areas(h)
    if not np.all(a > 0):
        raise ValueError(f"{h.GetName()}: non-positive bin area at GlobalID {np.flatnonzero(~(a > 0)).tolist()}")
    return a


def same_cells(ours_edges, paper_edges):
    """Our TH2D bins the paper's cells: p_par edges equal the release axis's, and pT edges equal
    either our analysis grid (PT_EDGES, bin_mapping.txt's printed edges) or the release axis's."""
    (o_pt, o_pz), (p_pt, p_pz) = ours_edges, paper_edges

    def equal(a, b):
        a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
        return a.shape == b.shape and bool(np.all(np.abs(a - b) <= 1e-12))
    return equal(o_pz, p_pz) and (equal(o_pt, PT_EDGES) or equal(o_pt, p_pt))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--anc-dir", default=ANC_DIR)
    ap.add_argument("--ours", action="append", default=None,
                    help="LABEL=ROOT[:HIST] (repeatable). Default: frozen 2D production")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    specs = a.ours or [f"2d_production={DEFAULT_OURS}:hXSec2D"]

    paper_path = os.path.join(a.anc_dir, "cov_ptpl_minerva_inclusive_6GeV.root")
    fp = ROOT.TFile.Open(paper_path)
    h_paper = fp.Get("pt_pl_cross_section")
    paper_v = flatten_th2d(h_paper)
    cov = tmatrix_to_numpy(fp.Get("TotalCovariance"))
    cov_stat = tmatrix_to_numpy(fp.Get("StatOnlyCovariance"))
    reported = np.diag(cov_stat) > 0
    if int(reported.sum()) != 205:
        print(f"[FAIL] reported bins = {int(reported.sum())}, expected 205", file=sys.stderr)
        return 3
    paper_edges = th2d_edges(h_paper)
    paper_pz = paper_edges[1]
    interior = reported & interior_mask(*paper_edges)
    # Paper areas from the release TH2D's own axes; ours, below, from our TH2D's axes.
    try:
        area = positive_areas(h_paper)
    except ValueError as e:
        print(f"[FAIL] {e}", file=sys.stderr)
        return 3
    # Recorded: the release axis's areas against those of bin_mapping.txt's printed edges
    # (PT_EDGES/PZ_EDGES).
    ipt, ipz = strip_index()
    printed_area = (np.diff(PT_EDGES)[ipt] * np.diff(PZ_EDGES)[ipz]).astype(float)
    out_paper_axis_area_maxreldev = float(np.max(np.abs(area / printed_area - 1.0)))

    out = dict(produced_by="2d-unfolding/strip_ratio_receipt.py",
               issue="KNOWN_ISSUES #5", hostname=os.uname().nodename,
               paper=dict(path=paper_path, sha256=sha256(paper_path)),
               n_reported=int(reported.sum()), n_interior=int(interior.sum()),
               paper_th2d_axis_area_max_reldev_vs_authoritative=out_paper_axis_area_maxreldev,
               inputs={}, results={})
    for spec in specs:
        label, _, rest = spec.partition("=")
        path, _, hist = rest.partition(":")
        hist = hist or "hXSec2D"
        fo = ROOT.TFile.Open(path)
        ho = fo.Get(hist)
        ours_v = flatten_ours(ho)
        # Our TH2D must bin the paper's cells (same_cells), so a binning mismatch cannot pass
        # silently.
        if not same_cells(th2d_edges(ho), paper_edges):
            print(f"[FAIL] {label}: bin edges differ from the paper grid", file=sys.stderr)
            return 3
        try:
            a_o = positive_areas(ho)
        except ValueError as e:
            print(f"[FAIL] {label}: {e}", file=sys.stderr)
            return 3
        out["inputs"][label] = dict(path=path, hist=hist, sha256=sha256(path))
        reldev = float(np.max(np.abs(a_o / area - 1.0)))
        if reldev > 0:  # recorded only when our cells' areas differ from the release axis's
            out["inputs"][label]["area_max_reldev_vs_paper_axis"] = reldev
        res = {"reported_205": measure(ours_v, paper_v, area, cov, reported, a_o, paper_pz),
               "interior_185": measure(ours_v, paper_v, area, cov, interior, a_o, paper_pz)}
        fac = historical_factor(paper_pz)[strip_index()[1]]
        ctrl = {"interior_185": measure(ours_v * fac, paper_v, area, cov, interior, a_o, paper_pz)}
        res["power_control_historical_gradient_injected"] = ctrl
        out["results"][label] = res
        for mname in ("reported_205", "interior_185"):
            m = res[mname]
            print(f"\n[{label}] mask={mname}  verdict={m['verdict']}  {m['verdict_parts']}")
            print(f"  {'p_par strip':>12s} {'n':>3s} {'R(int)':>8s} {'+-paper':>8s} {'R(bare)':>8s}")
            for r in m["strips"]:
                if r is None:
                    continue
                print(f"  {r['pz_lo']:5.1f}-{r['pz_hi']:<6.1f} {r['n_bins']:3d} {r['R']:8.4f} "
                      f"{r['R_sigma']:8.4f} {r['R_bare']:8.4f}")
            c = m["contrast"]
            print(f"  contrast R(1.5-2.5)={c['R_low']:.4f} R(20-60)={c['R_high']:.4f} "
                  f"diff={c['diff']:+.4f} +- {c['sigma_diff_paper_total']:.4f} "
                  f"({c['n_sigma']:+.2f} sigma)")
        pc = ctrl["interior_185"]
        print(f"[{label}] POWER CONTROL (historical gradient injected): verdict={pc['verdict']} "
              f"contrast diff={pc['contrast']['diff']:+.4f} ({pc['contrast']['n_sigma']:+.2f} sigma)")
        if pc["verdict"] != "GRADIENT PRESENT":
            print("[FAIL] the instrument did not detect the injected historical gradient",
                  file=sys.stderr)
            with open(a.out, "w") as f:
                json.dump(out, f, indent=1)
            return 4
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1)
    print(f"\n[receipt] wrote {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
