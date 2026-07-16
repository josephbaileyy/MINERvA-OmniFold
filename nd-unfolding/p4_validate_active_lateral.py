#!/usr/bin/env python3
"""P4 validation: the selection-complete active scalar lateral covariance vs the
support-limited dump-all-bank block. Matrix gates (symmetry / PSD / finite diag),
sqrt-trace + per-bin comparison, and migration accounting from the active endpoints'
census. Writes a compact JSON summary. Exit 0 iff all hard gates pass.

Usage:
  p4_validate_active_lateral.py \
    --active uq_5d/active_lateral_stage2/active_scalar_lateral_5d_cov.root:hCov_universe5d_total \
    --support uq_5d/universe_stage2_5d/uq_universe_5d_covariance_combined.root \
    --merged-dir active_universe_5d/standard/merged \
    --out uq_5d/active_lateral_stage2/p4_active_lateral_summary.json
"""
import argparse, json, os, sys
import numpy as np
import ROOT

BANDS = ["BeamAngleX", "BeamAngleY", "MuonResolution",
         "Muon_Energy_MINERvA", "Muon_Energy_MINOS"]

def load_th2(spec):
    path, key = spec.rsplit(":", 1)
    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        raise SystemExit(f"cannot open {path}")
    h = f.Get(key)
    if not h:
        raise SystemExit(f"missing key {key} in {path}")
    n = h.GetNbinsX()
    C = np.empty((n, n))
    for i in range(n):
        for j in range(n):
            C[i, j] = h.GetBinContent(i + 1, j + 1)
    f.Close()
    return C

def load_th2_key(path, key):
    f = ROOT.TFile.Open(path)
    h = f.Get(key)
    if not h:
        f.Close(); return None
    n = h.GetNbinsX()
    C = np.empty((n, n))
    for i in range(n):
        for j in range(n):
            C[i, j] = h.GetBinContent(i + 1, j + 1)
    f.Close()
    return C

def mat_gates(C, tag):
    r = {}
    r["shape"] = list(C.shape)
    r["all_finite"] = bool(np.all(np.isfinite(C)))
    asym = np.max(np.abs(C - C.T)) / max(1e-300, np.max(np.abs(C)))
    r["rel_asymmetry"] = float(asym)
    Cs = 0.5 * (C + C.T)
    ev = np.linalg.eigvalsh(Cs)
    r["min_eig"] = float(ev[0]); r["max_eig"] = float(ev[-1])
    r["min_over_max_eig"] = float(ev[0] / max(1e-300, ev[-1]))
    r["psd"] = bool(ev[0] >= -1e-12 * abs(ev[-1]))
    d = np.diag(C)
    r["diag_finite_nonneg"] = bool(np.all(np.isfinite(d)) and np.all(d >= -1e-30))
    r["sqrt_trace"] = float(np.sqrt(np.clip(np.trace(Cs), 0, None)))
    r["n_reported"] = int(np.sum(d > 0))
    print(f"[{tag}] shape={r['shape']} finite={r['all_finite']} "
          f"asym={asym:.2e} min/max_eig={r['min_over_max_eig']:.2e} PSD={r['psd']} "
          f"sqrt_tr={r['sqrt_trace']:.4e}")
    return r

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--active", required=True, help="ROOT:key of the active lateral total cov")
    ap.add_argument("--support", required=True, help="uq_universe_5d_covariance_combined.root")
    ap.add_argument("--merged-dir", default=None)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    out = {"gates": {}, "active": {}, "support": {}, "comparison": {}, "migration": {}}
    fails = []

    Cact = load_th2(a.active)
    out["active"] = mat_gates(Cact, "active")

    # hard gates on the active (P4 product)
    for g in ("all_finite", "psd", "diag_finite_nonneg"):
        if not out["active"][g]:
            fails.append(f"active {g}")
    if out["active"]["rel_asymmetry"] > 1e-9:
        fails.append("active asymmetry >1e-9")

    # support-limited block = sum of the 5 kinematic per-band covs in the old combined ROOT
    Csup = None; present = []
    for b in BANDS:
        cb = load_th2_key(a.support, f"hCov_universe5d_{b}")
        if cb is None:
            print(f"[support] band {b} key absent"); continue
        present.append(b)
        Csup = cb if Csup is None else Csup + cb
    out["support"]["bands_present"] = present
    if Csup is not None:
        out["support"].update(mat_gates(Csup, "support(sum of 5 bands)"))
        if Csup.shape == Cact.shape:
            st_a = out["active"]["sqrt_trace"]; st_s = out["support"]["sqrt_trace"]
            da = np.sqrt(np.clip(np.diag(Cact), 0, None))
            ds = np.sqrt(np.clip(np.diag(Csup), 0, None))
            m = ds > 0
            ratio = np.divide(da, ds, out=np.zeros_like(da), where=m)
            out["comparison"] = {
                "sqrt_trace_active": st_a,
                "sqrt_trace_support": st_s,
                "sqrt_trace_ratio_active_over_support": float(st_a / max(1e-300, st_s)),
                "per_bin_sigma_ratio_median": float(np.median(ratio[m])),
                "per_bin_sigma_ratio_p16": float(np.percentile(ratio[m], 16)),
                "per_bin_sigma_ratio_p84": float(np.percentile(ratio[m], 84)),
                "n_bins_active_gt_support": int(np.sum(da > ds)),
                "n_bins_common": int(np.sum(m)),
            }
            print(f"[compare] sqrt_tr active={st_a:.4e} support={st_s:.4e} "
                  f"ratio={st_a/max(1e-300,st_s):.3f}; per-bin median ratio "
                  f"{out['comparison']['per_bin_sigma_ratio_median']:.3f}")
        else:
            fails.append(f"active/support shape mismatch {Cact.shape} vs {Csup.shape}")

    # migration accounting from the merged endpoint census (hadd sums TParameter<long>)
    if a.merged_dir:
        for b in BANDS:
            per = {}
            for ep in (0, 1):
                p = os.path.join(a.merged_dir,
                                 f"runEventLoopOmniFold_5D_MEFHC_active_{b}_{ep}.root")
                if not os.path.exists(p):
                    continue
                f = ROOT.TFile.Open(p)
                d = {}
                for k in ("activeUniverseTruthEntrants", "activeUniverseTruthExits",
                          "activeUniverseRecoEntrants", "activeUniverseRecoExits"):
                    o = f.Get(k); d[k] = int(o.GetVal()) if o else None
                f.Close()
                per[f"idx{ep}"] = d
            out["migration"][b] = per
        # sanity: lateral bands should show nonzero total migration
        tot = 0
        for b, per in out["migration"].items():
            for ep, d in per.items():
                tot += sum(abs(v) for v in d.values() if isinstance(v, int))
        out["migration"]["_total_abs"] = tot
        print(f"[migration] total |entrants|+|exits| across bands/endpoints = {tot}")
        if out["migration"] and tot == 0:
            print("[migration] WARN: zero total migration (unexpected for lateral bands)")

    out["gates"]["fails"] = fails
    out["gates"]["result"] = "PASS" if not fails else "FAIL"
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"\nRESULT {out['gates']['result']}" + ("" if not fails else " :: " + "; ".join(fails)))
    print(f"summary -> {a.out}")
    sys.exit(0 if not fails else 1)

if __name__ == "__main__":
    main()
