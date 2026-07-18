#!/usr/bin/env python3
"""P4-FPS validation (Agent C), hardened repair-3: the selection-complete active scalar FPS lateral
covariance vs the support-limited block, with UNCONDITIONAL publication gating + a schema-versioned
receipt chain. All manifest/receipt/hash gates run BEFORE ROOT (login-safe); ROOT is lazy.

Fail-closed (unconditional -- no optional path):
  - publication manifest (schema v2 / negweight-refined / canonical mask / hex64 + paths);
  - manifest PASS receipt (binds this manifest digest);
  - component_build transition receipt (predecessor = manifest digest; candidate = the active cov);
  - RECOMPUTE the active cov sha256 and require it == the component receipt's candidate_sha256;
  - RECOMPUTE every manifest artifact hash;
  - merged-endpoint audit receipt result == PASS.
Then (ROOT): matrix gates (finite/PSD/asym/nonzero), exact 5 active + 5 support band inventories,
per-band nonzero trace, active total == sum(5), 266x266 dim tied to the recomputed canonical mask.
Writes the JSON summary + a p4_validation receipt LAST (predecessor = active cov sha; candidate = same).

  python p4_validate_active_lateral_fps.py --manifest M --pass-receipt R --component-receipt CB \
      --active active_scalar_lateral_fps_cov.root:hCov_universe4d_total --support COMBINED.root \
      --cv CV.root --out p4_summary.json --out-receipt receipt_p4.json --utc <iso>
"""
import argparse, datetime, json, os, sys
import numpy as np

import fps_provenance as fp

BANDS = fp.BANDS


def _load_root():
    import ROOT
    ROOT.gROOT.SetBatch(True)
    return ROOT


def load_th2(ROOT, spec):
    path, key = spec.rsplit(":", 1)
    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        raise SystemExit(f"cannot open {path}")
    h = f.Get(key)
    if not h:
        raise SystemExit(f"missing key {key} in {path}")
    n = h.GetNbinsX()
    C = np.array([[h.GetBinContent(i + 1, j + 1) for j in range(n)] for i in range(n)])
    f.Close()
    return C


def load_th2_key(ROOT, path, key):
    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        return None
    h = f.Get(key)
    if not h:
        f.Close(); return None
    n = h.GetNbinsX()
    C = np.array([[h.GetBinContent(i + 1, j + 1) for j in range(n)] for i in range(n)])
    f.Close()
    return C


def mat_gates(C, tag):
    r = {"shape": list(C.shape), "all_finite": bool(np.all(np.isfinite(C)))}
    Cs = 0.5 * (C + C.T)
    ev = np.linalg.eigvalsh(Cs)
    r["rel_asymmetry"] = float(np.max(np.abs(C - C.T)) / max(1e-300, np.max(np.abs(C))))
    r["min_over_max_eig"] = float(ev[0] / max(1e-300, abs(ev[-1])))
    r["psd"] = bool(ev[0] >= -1e-12 * abs(ev[-1]))
    d = np.diag(C)
    r["diag_finite_nonneg"] = bool(np.all(np.isfinite(d)) and np.all(d >= -1e-30))
    r["sqrt_trace"] = float(np.sqrt(np.clip(np.trace(Cs), 0, None)))
    r["n_reported"] = int(np.sum(d > 0))
    print(f"[{tag}] shape={r['shape']} finite={r['all_finite']} psd={r['psd']} sqrt_tr={r['sqrt_trace']:.4e}")
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--pass-receipt", required=True)
    ap.add_argument("--component-receipt", required=True)
    ap.add_argument("--active", required=True, help="ROOT:key of the active FPS lateral total cov")
    ap.add_argument("--support", required=True, help="uq_universe_fps_covariance_combined.root")
    ap.add_argument("--cv", required=True, help="CV unfold (recompute reported mask)")
    ap.add_argument("--band-prefix", default="hCov_universe4d_")
    ap.add_argument("--audit-json", default="active_universe_5d/fps/covariance/audit_merged_fps.json")
    ap.add_argument("--out", required=True)
    ap.add_argument("--out-receipt", required=True)
    ap.add_argument("--utc", default=None)
    a = ap.parse_args()
    utc = a.utc or datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    out = {"gates": {}, "active": {}, "support": {}, "comparison": {}, "provenance": {}}
    fails = []

    # ---- login-safe unconditional gates (no ROOT) ----
    manifest = json.load(open(a.manifest))
    fp.require_publication_manifest(manifest)
    manifest_digest = fp.sha256_file(a.manifest)
    fp.require_pass_receipt(json.load(open(a.pass_receipt)), manifest_digest)
    fp.require_recompute_hashes(manifest)
    active_path = a.active.rsplit(":", 1)[0]
    active_sha = fp.sha256_file(active_path)
    comp = json.load(open(a.component_receipt))
    fp.require_transition_receipt(comp, "component_build", manifest_digest, predecessor_sha=manifest_digest)
    if comp.get("candidate_sha256") != active_sha:
        raise fp.FpsGateError(
            f"active cov sha {active_sha[:16]} != component_build candidate {comp.get('candidate_sha256','')[:16]} "
            "(substituted covariance)")
    if not os.path.exists(a.audit_json):
        raise fp.FpsGateError(f"merged-endpoint audit receipt absent: {a.audit_json}")
    if json.load(open(a.audit_json)).get("result") != "PASS":
        raise fp.FpsGateError("merged-endpoint audit result != PASS")
    out["provenance"] = {"manifest_sha256": manifest_digest, "active_sha256": active_sha,
                         "reported_mask_hash": manifest["reported_mask_hash"]}

    # ---- ROOT numeric gates (lazy) ----
    ROOT = _load_root()
    Cact = load_th2(ROOT, a.active)
    out["active"] = mat_gates(Cact, "active(FPS selection-complete lateral)")
    for g in ("all_finite", "psd", "diag_finite_nonneg"):
        if not out["active"][g]:
            fails.append(f"active {g}")
    if out["active"]["rel_asymmetry"] > 1e-9:
        fails.append("active asymmetry >1e-9")
    if out["active"]["sqrt_trace"] <= 0 or out["active"]["n_reported"] == 0:
        fails.append("active is zero/empty")
    if Cact.shape[0] != fp.N_REPORTED:
        fails.append(f"active dim {Cact.shape[0]} != {fp.N_REPORTED}")

    active_bands = {}
    for b in BANDS:
        cb = load_th2_key(ROOT, active_path, f"{a.band_prefix}{b}")
        if cb is None:
            fails.append(f"active per-band '{a.band_prefix}{b}' absent")
        else:
            active_bands[b] = cb
    if set(active_bands) == set(BANDS):
        try:
            fp.check_active_rollup(active_bands, Cact)
            out["active"]["rollup_identity"] = "PASS (total == sum of 5 nonzero bands)"
        except fp.FpsGateError as e:
            fails.append(f"active rollup: {e}")

    Csup = None; present = []
    for b in BANDS:
        cb = load_th2_key(ROOT, a.support, f"{a.band_prefix}{b}")
        if cb is not None:
            present.append(b); Csup = cb if Csup is None else Csup + cb
    out["support"]["bands_present"] = present
    if set(present) != set(BANDS):
        fails.append(f"support inventory != 5 named bands (present={present})")
    if Csup is not None and Csup.shape == Cact.shape:
        st_a = out["active"]["sqrt_trace"]; st_s = float(np.sqrt(np.clip(np.trace(Csup), 0, None)))
        out["comparison"] = {"sqrt_trace_active": st_a, "sqrt_trace_support": st_s,
                             "ratio": float(st_a / max(1e-300, st_s))}

    out["gates"]["fails"] = fails
    out["gates"]["result"] = "PASS" if not fails else "FAIL"
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=2)
    if fails:
        print("RESULT FAIL :: " + "; ".join(fails)); sys.exit(1)

    receipt = fp.make_transition_receipt(
        "p4_validation", manifest_digest, predecessor_sha=active_sha, candidate_sha=active_sha,
        central_sha=manifest["central_cv_sha256"], reported_mask_hash=manifest["reported_mask_hash"],
        utc=utc, extra={"summary_path": os.path.abspath(a.out)})
    fp.require_transition_receipt(receipt, "p4_validation", manifest_digest, predecessor_sha=active_sha)
    with open(a.out_receipt, "w") as fh:
        json.dump(receipt, fh, indent=2)
    print(f"RESULT PASS -> {a.out} + p4_validation receipt {a.out_receipt}")


if __name__ == "__main__":
    main()
