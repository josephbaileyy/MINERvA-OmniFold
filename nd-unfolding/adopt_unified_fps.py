#!/usr/bin/env python3
"""P6-FPS final unified-throw adoption (Agent C), hardened repair-3. FPS wrapper around
C_final = C_pre - C_vertical + (g g^T) o C_vertical, gated by the publication manifest + receipt chain.
Manifest/receipt/hash gates run BEFORE ROOT (login-safe); ROOT lazy.

Fail-closed (unconditional):
  - publication manifest + manifest PASS receipt (binds this manifest digest);
  - active_adoption transition receipt (predecessor = activelat combined sha; candidate = same);
  - RECOMPUTE the activelat combined sha == active_adoption candidate; reject output aliasing inputs;
  - production CV sha == manifest central_cv_sha256; reported mask (manifest) == canonical, recomputed
    from CV; exact reported order/dim across combined/unified/CV;
  - reject diag(C_blocksum)<=0 < diag(C_unified);
  - hJointMeanShift MANDATORY with expected_dim=n, finite; bind its hash; mean-centered policy (not folded).
Requires the written C_final to satisfy the reconstruction identity + PSD. Emits a unified_adoption
receipt LAST (predecessor = activelat combined sha; candidate = the final uthrow sha).

  python adopt_unified_fps.py --manifest M --pass-receipt R --active-receipt AA \
      --combined COMBINED_activelat.root --uthrow unified_throw_cov_fps.root --prod CV.root \
      --out OUT_uthrow_activelat.root --out-receipt receipt_unified_adoption.json --utc <iso>
"""
import argparse, datetime, hashlib, json, os
import numpy as np

import fps_provenance as fp

VERT_BANDS = ["2p2h", "CCQEPauliSupViaKF", "FrAbs_pi", "FrElas_N", "HighQ2", "LowQ2",
              "MaCCQE", "MaRES", "MFP_N", "MvRES", "Rvn2pi", "Rvp2pi", "Flux"]
PSD_TOL = -1e-12


def _load_root():
    import ROOT
    ROOT.gROOT.SetBatch(True)
    return ROOT


def _th2(h):
    n = h.GetNbinsX()
    return np.array([[h.GetBinContent(i + 1, j + 1) for j in range(n)] for i in range(n)])


def _get(f, key):
    h = f.Get(key)
    if not h:
        raise fp.FpsGateError(f"missing {key}")
    return h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--pass-receipt", required=True)
    ap.add_argument("--active-receipt", required=True)
    ap.add_argument("--combined", required=True, help="active-lateral pre-uthrow combined ROOT")
    ap.add_argument("--uthrow", required=True)
    ap.add_argument("--prod", required=True, help="production CV")
    ap.add_argument("--out", required=True)
    ap.add_argument("--out-receipt", required=True)
    ap.add_argument("--utc", default=None)
    a = ap.parse_args()
    utc = a.utc or datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    # ---- login-safe gates (no ROOT) ----
    manifest = json.load(open(a.manifest))
    fp.require_publication_manifest(manifest)
    manifest_digest = fp.sha256_file(a.manifest)
    fp.require_pass_receipt(json.load(open(a.pass_receipt)), manifest_digest)
    fp.require_recompute_hashes(manifest)
    combined_sha = fp.sha256_file(a.combined)
    aa = json.load(open(a.active_receipt))
    fp.require_transition_receipt(aa, "active_adoption", manifest_digest, predecessor_sha=None)
    if aa.get("candidate_sha256") != combined_sha:
        raise fp.FpsGateError("combined sha != active_adoption candidate (substituted predecessor)")
    fp.require_no_path_alias(a.out, a.combined, a.uthrow, a.prod)
    if fp.sha256_file(a.prod) != manifest["central_cv_sha256"]:
        raise fp.FpsGateError("production CV sha != manifest central_cv_sha256")
    if manifest["reported_mask_hash"] != fp.REPORTED_MASK_FINGERPRINT:
        raise fp.FpsGateError("manifest reported_mask_hash != canonical")

    # ---- ROOT numeric section (lazy) ----
    ROOT = _load_root()
    fpr = ROOT.TFile.Open(a.prod); hx = _get(fpr, "hXSecND_flat")
    xfull = np.array([hx.GetBinContent(i + 1) for i in range(hx.GetNbinsX())]); fpr.Close()
    rep = xfull > 0
    fp.require_reported_mask(rep)                               # recompute == canonical
    n = int(rep.sum())

    fu = ROOT.TFile.Open(a.uthrow)
    C_uni = _th2(_get(fu, "C_unified")); C_block = _th2(_get(fu, "C_blocksum"))
    hms = _get(fu, "hJointMeanShift")
    mean_shift = np.array([hms.GetBinContent(i + 1) for i in range(hms.GetNbinsX())]); fu.Close()
    fp.require_mean_shift(mean_shift, expected_dim=n)           # MANDATORY, dim=n, finite
    mean_shift_sha = hashlib.sha256(mean_shift.astype("<f8").tobytes()).hexdigest()

    fc = ROOT.TFile.Open(a.combined)
    C_comb = _th2(_get(fc, "hCov_combined4d_total"))
    C_vert = None
    for b in VERT_BANDS:
        cb = _th2(_get(fc, f"hCov_universe4d_{b}"))
        C_vert = cb if C_vert is None else C_vert + cb
    fc.Close()
    for tag, C in (("C_unified", C_uni), ("C_blocksum", C_block), ("combined", C_comb), ("C_vertical", C_vert)):
        fp.require_square_finite(C, expected_dim=n, tag=tag)    # exact order/dim across inputs

    vu = np.clip(np.diag(C_uni), 0, None); vb = np.clip(np.diag(C_block), 0, None)
    fp.require_unified_inputs(vb, vu, tag="unified-vs-block")
    g = np.ones(n); m = np.sqrt(vb) > 0
    g[m] = np.sqrt(np.maximum(vu, vb))[m] / np.sqrt(vb)[m]
    C_new = 0.5 * (((C_comb - C_vert) + np.outer(g, g) * C_vert) +
                   ((C_comb - C_vert) + np.outer(g, g) * C_vert).T)
    fp.require_final_identity(C_new, C_comb, C_vert, g, tag="FPS uthrow adoption")
    fp.require_psd(C_new, tol=PSD_TOL, tag="C_final")

    fo = ROOT.TFile.Open(a.out, "RECREATE")

    def wcov(name, mat, title=None):
        h = ROOT.TH2D(name, title or name, n, 0, n, n, 0, n)
        for i in range(n):
            for j in range(n):
                h.SetBinContent(i + 1, j + 1, float(mat[i, j]))
        h.Write()

    wcov("hCov_combined4d_total_uthrow", C_new, "PUBLISHABLE FPS cov (active lateral + stat+ML + uthrow vertical)")
    wcov("hCov_vertical_sweep", C_vert, "C_vertical (13 vertical per-band covs; adoption carrier)")
    hg = ROOT.TH1D("hInflation_g", "per-bin unified/block sigma inflation g>=1", n, 0, n)
    for i in range(n):
        hg.SetBinContent(i + 1, float(g[i]))
    hg.Write()
    hjm = ROOT.TH1D("hJointMeanShift", "joint mean shift (preserved; NOT added: mean-centered policy)", n, 0, n)
    for i in range(n):
        hjm.SetBinContent(i + 1, float(mean_shift[i]))
    hjm.Write()
    ROOT.TNamed("provenance", json.dumps({
        "identity": "C_final = C_pre - C_vertical + (g g^T) o C_vertical",
        "manifest_sha256": manifest_digest, "predecessor_combined_sha256": combined_sha,
        "central_cv_sha256": manifest["central_cv_sha256"], "reported_mask_hash": manifest["reported_mask_hash"],
        "hJointMeanShift_sha256": mean_shift_sha, "hJointMeanShift_dim": int(mean_shift.size),
        "centering": "mean-centered (diag C_unified only); hJointMeanShift preserved separately, NOT added",
        "reported_dim": n})).Write()
    fo.Close()

    cand = fp.sha256_file(a.out)
    receipt = fp.make_transition_receipt(
        "unified_adoption", manifest_digest, predecessor_sha=combined_sha, candidate_sha=cand,
        central_sha=manifest["central_cv_sha256"], reported_mask_hash=manifest["reported_mask_hash"],
        utc=utc, extra={"candidate_path": os.path.abspath(a.out), "hJointMeanShift_sha256": mean_shift_sha})
    fp.require_transition_receipt(receipt, "unified_adoption", manifest_digest, predecessor_sha=combined_sha)
    with open(a.out_receipt, "w") as fh:
        json.dump(receipt, fh, indent=2)
    fpr_ = fp.cov_fingerprint(C_new)
    print(f"[uthrow-fps] wrote {a.out} (cand {cand[:16]}); dim={fpr_['dim']} rank={fpr_['rank']} "
          f"sqrt_tr={fpr_['sqrt_trace']:.4e}  meanshift_sha={mean_shift_sha[:12]}")
    print(f"[uthrow-fps] unified_adoption receipt {a.out_receipt}")


if __name__ == "__main__":
    main()
