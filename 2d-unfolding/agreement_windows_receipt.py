#!/usr/bin/env python3
"""Produce the 2D per-bin agreement receipt: median ratio and the 5/10/20 % windows.

WHY THIS EXISTS. `docs/analysis-note/values.tex` carried four macros -- \\medianBinRatio,
\\binsFive, \\binsTen and \\binsTwenty -- with NO committed producing script (OI-130). They were
printing in all three deliverables, including the external paper, and were suppressed on
2026-08-21. This script is the authorized producer whose committed output is the only sanctioned
route to restoring them.

WHAT IT IS NOT. It is NOT a re-derivation of the suppressed values and it makes no attempt to
land on them. It states a mask, states a denominator rule, and reports what it measures. If the
numbers differ from the suppressed ones, THAT IS A FINDING, not an error in this script -- the
suppressed values have no recoverable provenance to disagree with.

WHY NOT `compare_to_paper_interior.py`. That script masks to the STRICT INTERIOR
(`interior_mask()`, pt_hi/pz_lo <= tan(20 deg)) intersected with the paper-reported mask, so its
denominators are SMALLER than the 205 the note prints. `git log --follow` puts that interior mask
in the initial commit, so no committed version of it ever produced a 205-bin window.

THE MASK, derived not assumed. The paper's ancillary carries a 224-bin global grid
(GlobalID = (Ptbin-1)*16 + (P||bin-1), 14 x 16). A bin is REPORTED iff its StatOnlyCovariance
diagonal is positive -- the same predicate `compare_to_paper_fullcov.py:96-99` uses for its
chi^2 ndf. That count is ASSERTED to be 205; a different count is a hard failure, because every
number this script emits is denominated in it.

THE DENOMINATOR RULE, stated because it is the one real choice here. A per-bin ratio needs a
positive paper value. Reported bins whose paper central value is non-positive are EXCLUDED from
the ratio statistics and COUNTED SEPARATELY in the receipt -- never silently dropped, because a
denominator that shrinks without saying so is how the 205-vs-185 discrepancy arose in the first
place. `n_reported`, `n_ratio_used` and `n_excluded_nonpositive_paper` are all emitted, and
`n_ratio_used + n_excluded_nonpositive_paper == n_reported` is asserted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys

import numpy as np
import ROOT

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------------------------
# THE FLATTENERS AND THE GRID ARE IMPORTED, NOT COPIED. My first draft reimplemented them and got
# BOTH wrong in the same invisible way: I hardcoded `GetBinContent(ipz, ipt)` for the paper, where
# the canonical `flatten_th2d` DETECTS which axis is pt (`x_is_pt = (nx == N_PT)`) and handles
# either order; and for ours I wrote the same (ipz, ipt) when the canonical `flatten_ours` is
# (ipt, ipz) with `gid = (ix-1)*N_PZ + (iy-1)` -- a TRANSPOSE. A transposed comparison still
# produces a median and three percentages that look entirely plausible, which is exactly the
# failure this receipt exists to make impossible. One implementation, imported.
from compare_to_paper_fullcov import (            # noqa: E402
    N, N_PT, N_PZ, tmatrix_to_numpy, flatten_th2d, flatten_ours,
    ANC_DIR as FULLCOV_ANC_DIR, DEFAULT_OURS as FULLCOV_DEFAULT_OURS,
)

N_REPORTED_EXPECTED = 205
DEFAULT_ANC = FULLCOV_ANC_DIR
DEFAULT_OURS = FULLCOV_DEFAULT_OURS


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--anc-dir", default=DEFAULT_ANC)
    ap.add_argument("--ours", default=DEFAULT_OURS)
    ap.add_argument("--ours-hist", default="hXSec2D")
    ap.add_argument("--paper-hist", default="pt_pl_cross_section")
    ap.add_argument("--mask-object", default="StatOnlyCovariance",
                    help="the object whose positive diagonal DEFINES the reported mask")
    ap.add_argument("--out", required=True, help="receipt JSON to write")
    a = ap.parse_args()

    paper_path = os.path.join(a.anc_dir, "cov_ptpl_minerva_inclusive_6GeV.root")
    for p in (paper_path, a.ours):
        if not os.path.exists(p):
            print(f"[FAIL] missing input: {p}", file=sys.stderr)
            return 2

    fp = ROOT.TFile.Open(paper_path)
    if not fp or fp.IsZombie():
        print(f"[FAIL] cannot open {paper_path}", file=sys.stderr)
        return 2
    h_paper = fp.Get(a.paper_hist)
    cov_stat = tmatrix_to_numpy(fp.Get(a.mask_object))
    if cov_stat.shape != (N, N):
        print(f"[FAIL] {a.mask_object} is {cov_stat.shape}, expected ({N},{N})", file=sys.stderr)
        return 2
    paper_v = flatten_th2d(h_paper)

    fo = ROOT.TFile.Open(a.ours)
    if not fo or fo.IsZombie():
        print(f"[FAIL] cannot open {a.ours}", file=sys.stderr)
        return 2
    ours_v = flatten_ours(fo.Get(a.ours_hist))

    # ---- the mask, DERIVED ----------------------------------------------------------------
    mask = np.diag(cov_stat) > 0
    n_reported = int(mask.sum())
    print(f"[mask] reported bins = {n_reported} / {N}  (positive {a.mask_object} diagonal)")
    if n_reported != N_REPORTED_EXPECTED:
        print(f"[FAIL] reported-bin count is {n_reported}, not the asserted "
              f"{N_REPORTED_EXPECTED}. Every number below is denominated in this count, so a "
              f"mismatch is a hard failure and NOT something to normalise away.", file=sys.stderr)
        return 3

    # ---- the ratio statistics, with the denominator stated --------------------------------
    pv, ov = paper_v[mask], ours_v[mask]
    usable = pv > 0
    n_used = int(usable.sum())
    n_excl = n_reported - n_used
    assert n_used + n_excl == n_reported
    ratio = ov[usable] / pv[usable]
    median = float(np.median(ratio))
    dev = np.abs(ratio - 1.0)
    frac = {w: 100.0 * float((dev <= w / 100.0).sum()) / n_used for w in (5, 10, 20)}
    cnt = {w: int((dev <= w / 100.0).sum()) for w in (5, 10, 20)}

    print(f"[ratio] denominator: {n_used} of {n_reported} reported bins "
          f"({n_excl} excluded for non-positive paper value)")
    print(f"[ratio] median per-bin ratio (ours/paper) = {median:.4f}")
    for w in (5, 10, 20):
        print(f"[ratio] within {w:2d} % : {cnt[w]:3d}/{n_used} = {frac[w]:.1f} %")

    # ---- OI-130: the three headline macros name NO backing artifact, so attest them here -------
    # \sigTwoD, \sigTwoDpaper and \ratioTot are the 2D demonstrator's headline numbers and the
    # OI-130 enumeration found them to be the hard core: they cite no path even under the generous
    # bound, so no hash-binding, freeze gate or receipt check can fire on them. They come from the
    # two artifacts this producer already opens and pins by sha256, so attesting them costs nothing
    # extra and closes that hole.
    # BOTH SUMMATION CONVENTIONS ARE EMITTED, NOT ONE. `compare_to_paper_fullcov.py` prints the
    # paper total over REPORTED bins and ours over ALL bins, and that asymmetry is exactly how a
    # ratio goes quietly wrong. Reporting both makes the choice visible instead of assumed.
    totals = {
        "ours_all_bins": float(ours_v.sum()),
        "ours_reported_bins": float(ov.sum()),
        "paper_all_bins": float(paper_v.sum()),
        "paper_reported_bins": float(pv.sum()),
    }
    totals["ratio_ours_all_over_paper_reported"] = totals["ours_all_bins"] / totals["paper_reported_bins"]
    totals["ratio_both_reported"] = totals["ours_reported_bins"] / totals["paper_reported_bins"]
    print(f"[totals] ours  all={totals['ours_all_bins']:.4e}  reported={totals['ours_reported_bins']:.4e}")
    print(f"[totals] paper all={totals['paper_all_bins']:.4e}  reported={totals['paper_reported_bins']:.4e}")
    print(f"[totals] ratio ours_all/paper_reported = {totals['ratio_ours_all_over_paper_reported']:.4f}")
    print(f"[totals] ratio both_reported           = {totals['ratio_both_reported']:.4f}")

    rev = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                         cwd=os.path.dirname(os.path.abspath(__file__))).stdout.strip() or None
    receipt = {
        "produced_by": "2d-unfolding/agreement_windows_receipt.py",
        "authorization": "Joseph's 6b ruling, 2026-08-21; OI-130",
        "git_head_at_run": rev,
        "hostname": os.uname().nodename,
        "root_version": ROOT.gROOT.GetVersion(),
        "sources": {
            "paper": {"path": os.path.abspath(paper_path), "sha256": sha256(paper_path),
                      "central_value_object": a.paper_hist, "mask_object": a.mask_object},
            "ours": {"path": os.path.abspath(a.ours), "sha256": sha256(a.ours),
                     "central_value_object": a.ours_hist},
        },
        "mask": {"rule": f"positive diagonal of {a.mask_object} on the paper's 224-bin global grid",
                 "n_global": N, "n_reported": n_reported,
                 "n_reported_asserted": N_REPORTED_EXPECTED},
        "denominator": {"rule": "reported bins with a positive paper central value",
                        "n_ratio_used": n_used,
                        "n_excluded_nonpositive_paper": n_excl},
        "results": {"median_bin_ratio": round(median, 4),
                    "within_5_percent": {"count": cnt[5], "percent": round(frac[5], 1)},
                    "within_10_percent": {"count": cnt[10], "percent": round(frac[10], 1)},
                    "within_20_percent": {"count": cnt[20], "percent": round(frac[20], 1)}},
        "headline_totals_oi130": {
            "why": ("\\sigTwoD, \\sigTwoDpaper and \\ratioTot cite no backing artifact anywhere in "
                    "values.tex, which is OI-130's hard core: nothing can bind them. They derive from "
                    "the two artifacts pinned under `sources` above, so this receipt attests them."),
            "convention_note": ("BOTH summation conventions are given because compare_to_paper_fullcov.py "
                                "mixes them -- paper over REPORTED bins, ours over ALL bins. Which one "
                                "reproduces the quoted macro is a FINDING to read off, not an input."),
            "values": totals,
        },
        "caveat": ("These are a NEW measurement under a STATED mask and denominator. They are not "
                   "a reproduction of the suppressed \\medianBinRatio / \\binsFive / \\binsTen / "
                   "\\binsTwenty, which have no recoverable provenance. A difference is a finding, "
                   "not an error."),
    }
    with open(a.out, "w") as f:
        json.dump(receipt, f, indent=2, sort_keys=True)
        f.write("\n")
    print(f"[receipt] wrote {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
