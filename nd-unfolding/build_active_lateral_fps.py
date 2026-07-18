#!/usr/bin/env python3
"""Blocker 2 (Agent C): fail-closed active five-band selection-complete FPS lateral rollup. Replaces
the ad-hoc `analyze_universes_nd.py --glob` invocation with a hardened, manifest-gated builder.

REQUIRES a PUBLICATION manifest (fps_provenance.require_publication_manifest -> exactly 10 entries,
exact band/index inventory, common layout/mask/central hashes, and bkg_mode=negweight-refined for
ALL ten). It then, on the 266-bin reported mask (CV>0, hash bound to the manifest):
  - reads each endpoint's hXSecND_flat, subtracts the central CV,
  - forms each band's MAT biased-1/N mean-centered covariance C_b = (1/N) Z Z^T  (N=2 endpoints),
  - requires EXACTLY the five named bands, each with a finite nonzero trace,
  - requires active_total == sum(5 bands) within tol,
and writes hCov_universe4d_total + per-band hCov_universe4d_<band> + provenance to
active_scalar_lateral_fps_cov.root. A zero or incomplete active result fails closed.

NOT RUN in the 2026-07-18 repair round (no negweight-refined inputs, no holder); this is the gated
producer for the later, verifier-approved C turn.

  python build_active_lateral_fps.py --manifest <publication_manifest.json> \
      --cv uq_fps/universe_sweep/..._CV.root \
      --out active_universe_5d/fps/covariance/active_scalar_lateral_fps_cov.root
"""
import argparse
import json
import os

import numpy as np
import ROOT

import fps_provenance as fp

ROOT.gROOT.SetBatch(True)


def load_flat(path):
    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        raise fp.FpsGateError(f"cannot open {path}")
    h = f.Get("hXSecND_flat")
    if not h:
        f.Close(); raise fp.FpsGateError(f"no hXSecND_flat in {path}")
    a = np.array([h.GetBinContent(i + 1) for i in range(h.GetNbinsX())])
    f.Close()
    if a.size != fp.NBINS_EXT:
        raise fp.FpsGateError(f"{path}: {a.size} bins != {fp.NBINS_EXT}")
    return a


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True, help="PUBLICATION (negweight-refined) endpoint manifest")
    ap.add_argument("--cv", required=True, help="central CV unfold (defines the 285->266 reported mask)")
    ap.add_argument("--out", default="active_universe_5d/fps/covariance/active_scalar_lateral_fps_cov.root")
    ap.add_argument("--tol", type=float, default=1e-10)
    a = ap.parse_args()

    manifest = json.load(open(a.manifest))
    fp.require_publication_manifest(manifest)          # inventory + fingerprints + negweight-refined
    fp.require_no_path_alias(a.out, a.cv, *[e["unfold_root"] for e in manifest["endpoints"]])

    # central + reported mask (CV>0), bound to the manifest's declared mask hash
    if fp.sha256_file(a.cv) != manifest["central_cv_sha256"]:
        raise fp.FpsGateError("CV sha256 != manifest central_cv_sha256")
    cv = load_flat(a.cv)
    rep = cv > 0
    mh = fp.mask_hash(rep)
    if manifest["reported_mask_hash"] != mh:
        raise fp.FpsGateError(
            f"reported-mask hash {mh} != manifest {manifest['reported_mask_hash']} "
            "(central changed; covariance would be built against the wrong reporting mask)")
    cv_rep = cv[rep]
    n_rep = int(rep.sum())

    by = {e["band"]: {} for e in manifest["endpoints"]}
    for e in manifest["endpoints"]:
        by[e["band"]][e["endpoint"]] = load_flat(e["unfold_root"])[rep] - cv_rep

    per_band, total = {}, np.zeros((n_rep, n_rep))
    for b in fp.BANDS:
        if set(by[b]) != {0, 1}:
            raise fp.FpsGateError(f"band {b}: endpoints != {{0,1}} (got {sorted(by[b])})")
        D = np.stack([by[b][0], by[b][1]], axis=0)
        Z = D - D.mean(axis=0, keepdims=True)
        cov = (Z.T @ Z) / D.shape[0]              # MAT biased 1/N, mean-centered
        per_band[b] = cov
        total += cov

    fp.check_active_rollup(per_band, total, tol=a.tol)   # 5 nonzero bands + total==sum
    fp.require_reported_cov(total, n_rep, manifest["reported_mask_hash"], mh)

    fo = ROOT.TFile.Open(a.out, "RECREATE")

    def wcov(name, mat, title=None):
        h = ROOT.TH2D(name, title or name, n_rep, 0, n_rep, n_rep, 0, n_rep)
        for i in range(n_rep):
            for j in range(n_rep):
                h.SetBinContent(i + 1, j + 1, float(mat[i, j]))
        h.Write()

    wcov("hCov_universe4d_total", total, "active selection-complete FPS lateral (sum of 5 bands)")
    for b in fp.BANDS:
        wcov(f"hCov_universe4d_{b}", per_band[b])
    ROOT.TNamed("provenance", json.dumps({
        "manifest": os.path.abspath(a.manifest),
        "manifest_class": fp.classify_manifest(manifest),
        "reported_mask_hash": mh, "layout_fingerprint": fp.layout_fingerprint(),
        "central_cv_sha256": manifest["central_cv_sha256"],
        "n_reported": n_rep, "centering": "MAT biased 1/N, mean-centered", "bands": fp.BANDS,
    })).Write()
    fo.Close()
    print(f"[rollup] wrote {a.out}  n_reported={n_rep}  "
          f"sqrt_tr={np.sqrt(max(np.trace(total),0)):.4e}  mask={mh[:24]}")
    for b in fp.BANDS:
        print(f"   {b:22s} sqrt_tr={np.sqrt(max(np.trace(per_band[b]),0)):.4e}")


if __name__ == "__main__":
    main()
