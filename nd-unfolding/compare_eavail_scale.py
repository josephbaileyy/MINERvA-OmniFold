#!/usr/bin/env python3
"""Compare E_avail-scale variants against their matched control (KNOWN_ISSUES #26 / OI-31).

    python compare_eavail_scale.py --control C.root --repeat C2.root \
        --variant LABEL=V.root [...] --hists hXSec3D,hXSec_eavail,hXSec2D --out receipt.json

For each histogram and each input, the per-bin ratio to the control is taken over the control's
positive support. Reported: median / 95th-percentile / max of |ratio - 1|, the signed ratio of
the full integral (bin contents times bin volume), and, for 1D histograms, the per-bin ratios.
The REPEAT (an identical-configuration rerun of the control) gives the run-to-run floor; every
variant is reported against it. The verdict rule is the predeclared one in
docs/orchestration/PLAN-20260923-issue26-issue5-studies.md §1.5 and is applied here, not by hand.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

import numpy as np
import ROOT


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def contents(h):
    """(values, volumes) over all in-range bins, any dimension."""
    nd = h.GetDimension()
    axes = [h.GetXaxis(), h.GetYaxis(), h.GetZaxis()][:nd]
    ns = [ax.GetNbins() for ax in axes]
    vals, vols = [], []
    for ix in range(1, ns[0] + 1):
        for iy in range(1, (ns[1] if nd > 1 else 1) + 1):
            for iz in range(1, (ns[2] if nd > 2 else 1) + 1):
                b = h.GetBin(ix, iy if nd > 1 else 0, iz if nd > 2 else 0)
                vals.append(h.GetBinContent(b))
                v = axes[0].GetBinWidth(ix)
                if nd > 1:
                    v *= axes[1].GetBinWidth(iy)
                if nd > 2:
                    v *= axes[2].GetBinWidth(iz)
                vols.append(v)
    return np.asarray(vals), np.asarray(vols)


def load(path, name):
    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        raise SystemExit(f"[FAIL] cannot open {path}")
    h = f.Get(name)
    if not h:
        raise SystemExit(f"[FAIL] {name} missing in {path}")
    v, w = contents(h)
    f.Close()
    return v, w


def compare(ctrl, other):
    (cv, vol), (ov, vol2) = ctrl, other
    if cv.shape != ov.shape or not np.allclose(vol, vol2):
        raise SystemExit("[FAIL] binning mismatch")
    sup = cv > 0
    r = ov[sup] / cv[sup]
    d = np.abs(r - 1.0)
    out = dict(n_support=int(sup.sum()),
               median_abs_dev=float(np.median(d)), p95_abs_dev=float(np.percentile(d, 95)),
               max_abs_dev=float(d.max()),
               integral_ratio=float((ov * vol).sum() / (cv * vol).sum()),
               bitwise_identical=bool(np.array_equal(ov, cv)))
    if cv.size <= 40:
        out["per_bin_ratio"] = [float(x) if c > 0 else None for x, c in
                                zip(np.divide(ov, cv, out=np.full_like(ov, np.nan), where=cv > 0), cv)]
    return out


def verdict(var, floor, ml_ref):
    """§1.5: INERT iff for every histogram the variant's median and p95 |dev| are each no larger
    than max(2 x the repeat floor's, 0.1 x ml_ref) and |integral_ratio - 1| <= max(2 x floor's,
    1e-4). ml_ref is the per-bin median ML-seed band of the product (fraction)."""
    ok = True
    for h, m in var.items():
        f = floor[h]
        tol_med = max(2 * f["median_abs_dev"], 0.1 * ml_ref)
        tol_p95 = max(2 * f["p95_abs_dev"], 0.1 * ml_ref)
        tol_int = max(2 * abs(f["integral_ratio"] - 1.0), 1e-4)
        m["tolerances"] = dict(median=tol_med, p95=tol_p95, integral=tol_int)
        m["within"] = bool(m["median_abs_dev"] <= tol_med and m["p95_abs_dev"] <= tol_p95
                           and abs(m["integral_ratio"] - 1.0) <= tol_int)
        ok &= m["within"]
    return "INERT" if ok else "SENSITIVE"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--control", required=True)
    ap.add_argument("--repeat", required=True)
    ap.add_argument("--variant", action="append", required=True, help="LABEL=ROOT")
    ap.add_argument("--power", action="append", default=[], help="LABEL=ROOT (power control)")
    ap.add_argument("--reference", default=None, help="frozen production ROOT (informational)")
    ap.add_argument("--hists", required=True)
    ap.add_argument("--ml-ref", type=float, required=True,
                    help="per-bin median ML-seed band of this product, as a fraction")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    hists = [h.strip() for h in a.hists.split(",") if h.strip()]

    files = {"control": a.control, "repeat": a.repeat}
    for s in a.variant + a.power:
        lab, _, p = s.partition("=")
        files[lab] = p
    if a.reference:
        files["frozen_reference"] = a.reference
    rec = dict(produced_by="nd-unfolding/compare_eavail_scale.py", hostname=os.uname().nodename,
               files={k: dict(path=v, sha256=sha256(v)) for k, v in files.items()},
               hists=hists, ml_ref=a.ml_ref, results={})
    ctrl = {h: load(a.control, h) for h in hists}
    floor = {h: compare(ctrl[h], load(a.repeat, h)) for h in hists}
    rec["results"]["repeat_floor"] = floor
    if a.reference:
        rec["results"]["frozen_reference_vs_control"] = {
            h: compare(ctrl[h], load(a.reference, h)) for h in hists}
    for s in a.variant:
        lab, _, p = s.partition("=")
        m = {h: compare(ctrl[h], load(p, h)) for h in hists}
        rec["results"][lab] = dict(metrics=m, verdict=verdict(m, floor, a.ml_ref))
    for s in a.power:
        lab, _, p = s.partition("=")
        m = {h: compare(ctrl[h], load(p, h)) for h in hists}
        v = verdict(m, floor, a.ml_ref)
        rec["results"][lab] = dict(metrics=m, verdict=v,
                                   power_control_detected=(v == "SENSITIVE"))
    with open(a.out, "w") as f:
        json.dump(rec, f, indent=1)
    for lab, r in rec["results"].items():
        if lab in ("repeat_floor", "frozen_reference_vs_control"):
            mm, v = r, "-"
        else:
            mm, v = r["metrics"], r["verdict"]
        print(f"[{lab}] verdict={v}")
        for h, m in mm.items():
            print(f"   {h:16s} n={m['n_support']:6d} med|d|={m['median_abs_dev']:.3e} "
                  f"p95|d|={m['p95_abs_dev']:.3e} max|d|={m['max_abs_dev']:.3e} "
                  f"int={m['integral_ratio']:.6f} identical={m['bitwise_identical']}")
    bad_power = [lab for lab, r in rec["results"].items()
                 if isinstance(r, dict) and r.get("power_control_detected") is False]
    if bad_power:
        print(f"[FAIL] power control(s) not detected: {bad_power} -- the null is uninformative",
              file=sys.stderr)
        return 4
    return 0


if __name__ == "__main__":
    sys.exit(main())
