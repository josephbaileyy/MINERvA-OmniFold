#!/usr/bin/env python3
"""P4-FPS validation (Agent C): the selection-complete active scalar FPS lateral covariance
vs the support-limited (dump-all-bank) FPS lateral block. Self-contained FPS sibling of
p4_validate_active_lateral.py -- same matrix gates + active-vs-support sqrt-trace/per-bin
comparison, but reads the FPS `hCov_universe4d_<band>` block naming (analyze_universes_nd.py
writes 4d-tagged names for every ND build, FPS included) and does NOT re-do the migration
census (audit_merged_fps.py already gates the hadd-summed census on the merged endpoints).

  p4_validate_active_lateral_fps.py \
    --active active_universe_5d/fps/covariance/active_scalar_lateral_fps_cov.root:hCov_universe4d_total \
    --support uq_fps/corrected/universe_stage2_fps/uq_universe_fps_covariance_combined.root \
    --band-prefix hCov_universe4d_ \
    --out active_universe_5d/fps/covariance/p4_active_lateral_fps_summary.json
"""
import argparse, json, os, sys
import numpy as np
import ROOT

import fps_provenance as fp

ROOT.gROOT.SetBatch(True)
# the 5 selection-complete lateral bands (muon angle / resolution / energy scales); the
# support-limited comparator is the sum of these per-band blocks in the FPS combined ROOT.
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
    if not f or f.IsZombie():
        return None
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
    ap.add_argument("--active", required=True, help="ROOT:key of the active FPS lateral total cov")
    ap.add_argument("--support", required=True, help="uq_universe_fps_covariance_combined.root")
    ap.add_argument("--band-prefix", default="hCov_universe4d_",
                    help="per-band block key prefix in BOTH the support and active ROOTs")
    ap.add_argument("--manifest", default=None,
                    help="PUBLICATION endpoint manifest; if given, require negweight-refined + mask binding")
    ap.add_argument("--audit-json", default="active_universe_5d/fps/covariance/audit_merged_fps.json",
                    help="merged-endpoint audit receipt to fingerprint into the summary")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    out = {"gates": {}, "active": {}, "support": {}, "comparison": {}, "provenance": {}}
    fails = []

    # ---- fail-closed publication manifest gate (blocker 3): negweight-refined + mask/central binding
    manifest = None
    if a.manifest:
        try:
            manifest = json.load(open(a.manifest))
            fp.require_publication_manifest(manifest)
            out["provenance"]["manifest_class"] = fp.classify_manifest(manifest)
            out["provenance"]["reported_mask_hash"] = manifest["reported_mask_hash"]
        except fp.FpsGateError as e:
            fails.append(f"manifest gate: {e}")
    else:
        out["provenance"]["manifest"] = "ABSENT (publication run must pass --manifest)"

    # ---- merged-endpoint audit fingerprint (blocker 3)
    if os.path.exists(a.audit_json):
        out["provenance"]["audit_json_sha256"] = fp.sha256_file(a.audit_json)
        try:
            audit = json.load(open(a.audit_json))
            if audit.get("result") != "PASS":
                fails.append(f"merged-endpoint audit not PASS (result={audit.get('result')})")
        except Exception as e:
            fails.append(f"audit json unreadable: {e}")
    else:
        fails.append(f"merged-endpoint audit receipt absent: {a.audit_json}")

    Cact = load_th2(a.active)
    out["active"] = mat_gates(Cact, "active(FPS selection-complete lateral)")

    # ---- exact 5-band active inventory + nonzero per-band traces + total identity (blocker 3)
    a_root = a.active.rsplit(":", 1)[0]
    active_bands = {}
    for b in fp.BANDS:
        cb = load_th2_key(a_root, f"{a.band_prefix}{b}")
        if cb is None:
            fails.append(f"active per-band block '{a.band_prefix}{b}' absent")
        else:
            active_bands[b] = cb
    if set(active_bands) == set(fp.BANDS):
        try:
            fp.check_active_rollup(active_bands, Cact)   # 5 nonzero bands + total==sum(5)
            out["active"]["rollup_identity"] = "PASS (total == sum of 5 nonzero bands)"
        except fp.FpsGateError as e:
            fails.append(f"active rollup: {e}")

    # hard gates on the active P4-FPS product
    for g in ("all_finite", "psd", "diag_finite_nonneg"):
        if not out["active"][g]:
            fails.append(f"active {g}")
    if out["active"]["rel_asymmetry"] > 1e-9:
        fails.append("active asymmetry >1e-9")
    if out["active"]["sqrt_trace"] <= 0 or out["active"]["n_reported"] == 0:
        fails.append("active is zero/empty (nothing migrated into the covariance)")

    # support-limited block = sum of the 5 kinematic per-band covs in the FPS combined ROOT
    Csup = None; present = []
    for b in BANDS:
        cb = load_th2_key(a.support, f"{a.band_prefix}{b}")
        if cb is None:
            print(f"[support] band {b} key '{a.band_prefix}{b}' absent"); continue
        present.append(b)
        Csup = cb if Csup is None else Csup + cb
    out["support"]["bands_present"] = present
    if set(present) != set(BANDS):
        fails.append(f"support inventory != 5 named bands (present={present}); check --band-prefix")
    if Csup is None:
        fails.append("no support-limited lateral bands found (check --band-prefix)")
    else:
        out["support"].update(mat_gates(Csup, "support(sum of 5 FPS bands)"))
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
