#!/usr/bin/env python3
"""Blocker 1/2 (Agent C): fail-closed active five-band FPS lateral rollup, mutually executable with the
publication-manifest builder. All manifest/receipt/hash gates run BEFORE ROOT is imported (login-safe
CLI negatives); ROOT is imported lazily only for the numeric rollup.

Gates (fail-closed):
  - publication manifest (schema v2 / negweight-refined / canonical 266/285 mask / hex64 hashes + paths);
  - manifest PASS receipt (schema-versioned, binds this manifest digest);
  - RECOMPUTE every referenced artifact hash in the manifest (never trust a string);
Then (ROOT): validate each endpoint TH2 (pt,pz) edges == canonical AND hXSecND_flat == TH2 C-order ravel;
per-band MAT biased-1/N mean-centered cov; EXACTLY five nonzero bands; total == sum(5); reported mask
recomputed from CV == canonical. Writes the cov ROOT then a schema-versioned component_build receipt LAST
(candidate = the written cov sha256; predecessor = manifest digest).

NOT RUN in the repair round (no negweight-refined inputs). Login-safe up to the ROOT section.

  python build_active_lateral_fps.py --manifest M.json --pass-receipt R.json --cv CV.root \
      --out active_universe_5d/fps/covariance/active_scalar_lateral_fps_cov.root \
      --out-receipt active_universe_5d/fps/covariance/receipt_component_build.json --utc <iso>
"""
import argparse
import datetime
import json
import os

import numpy as np

import fps_provenance as fp


def _load_root():
    import ROOT
    ROOT.gROOT.SetBatch(True)
    return ROOT


def _flat_and_th2(ROOT, path):
    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        raise fp.FpsGateError(f"cannot open {path}")
    h1 = f.Get("hXSecND_flat"); h2 = f.Get("hXSecND")
    if not h1 or not h2:
        f.Close(); raise fp.FpsGateError(f"{path}: missing hXSecND_flat/hXSecND")
    flat = np.array([h1.GetBinContent(i + 1) for i in range(h1.GetNbinsX())])
    nx, ny = h2.GetNbinsX(), h2.GetNbinsY()
    th2 = np.array([[h2.GetBinContent(i + 1, j + 1) for j in range(ny)] for i in range(nx)])
    xed = [h2.GetXaxis().GetBinLowEdge(i + 1) for i in range(nx)] + [h2.GetXaxis().GetBinUpEdge(nx)]
    yed = [h2.GetYaxis().GetBinLowEdge(j + 1) for j in range(ny)] + [h2.GetYaxis().GetBinUpEdge(ny)]
    f.Close()
    # TH2 edges == canonical
    if not (np.allclose(xed, fp.PT_EDGES) and np.allclose(yed, fp.PZ_EDGES)):
        raise fp.FpsGateError(f"{os.path.basename(path)}: TH2 edges != canonical 15x19 grid")
    # flat == TH2 raveled C-order
    if flat.size != fp.NBINS_EXT or th2.shape != (fp.NPT, fp.NPZ):
        raise fp.FpsGateError(f"{os.path.basename(path)}: shape {flat.size}/{th2.shape} != 285/(15,19)")
    if not np.allclose(flat, th2.ravel(order="C")):
        raise fp.FpsGateError(f"{os.path.basename(path)}: hXSecND_flat != TH2 C-order ravel")
    return flat


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--pass-receipt", required=True)
    ap.add_argument("--cv", required=True)
    ap.add_argument("--out", default="active_universe_5d/fps/covariance/active_scalar_lateral_fps_cov.root")
    ap.add_argument("--out-receipt", default="active_universe_5d/fps/covariance/receipt_component_build.json")
    ap.add_argument("--utc", default=None)
    ap.add_argument("--tol", type=float, default=1e-10)
    a = ap.parse_args()
    utc = a.utc or datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    # ---- login-safe gates (no ROOT) ----
    manifest = json.load(open(a.manifest))
    fp.require_publication_manifest(manifest)
    manifest_digest = fp.sha256_file(a.manifest)
    fp.require_pass_receipt(json.load(open(a.pass_receipt)), manifest_digest)
    fp.require_recompute_hashes(manifest)                       # recompute EVERY referenced hash
    fp.require_no_path_alias(a.out, a.cv, *[e["unfold_root"] for e in manifest["endpoints"]])
    if fp.sha256_file(a.cv) != manifest["central_cv_sha256"]:
        raise fp.FpsGateError("CV sha256 != manifest central_cv_sha256")

    # ---- ROOT numeric section (lazy import) ----
    ROOT = _load_root()
    cvflat = _flat_and_th2(ROOT, a.cv)
    rep = cvflat > 0
    mh = fp.require_reported_mask(rep)                          # recompute == canonical 266/285
    if manifest["reported_mask_hash"] != mh:
        raise fp.FpsGateError("manifest reported_mask_hash != recomputed canonical")
    cv_rep = cvflat[rep]; n_rep = int(rep.sum())

    by = {b: {} for b in fp.BANDS}
    for e in manifest["endpoints"]:
        by[e["band"]][e["endpoint"]] = _flat_and_th2(ROOT, e["unfold_root"])[rep] - cv_rep
    per_band, total = {}, np.zeros((n_rep, n_rep))
    for b in fp.BANDS:
        if set(by[b]) != {0, 1}:
            raise fp.FpsGateError(f"band {b}: endpoints != {{0,1}}")
        D = np.stack([by[b][0], by[b][1]], axis=0)
        Z = D - D.mean(axis=0, keepdims=True)
        per_band[b] = (Z.T @ Z) / D.shape[0]                   # MAT biased 1/N, mean-centered
        total += per_band[b]
    fp.check_active_rollup(per_band, total, tol=a.tol)
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
        "manifest_sha256": manifest_digest, "reported_mask_hash": mh,
        "central_cv_sha256": manifest["central_cv_sha256"], "n_reported": n_rep,
        "centering": "MAT biased 1/N, mean-centered", "bands": fp.BANDS})).Write()
    fo.Close()

    cand = fp.sha256_file(a.out)
    receipt = fp.make_transition_receipt(
        "component_build", manifest_digest, predecessor_sha=manifest_digest, candidate_sha=cand,
        central_sha=manifest["central_cv_sha256"], reported_mask_hash=mh, utc=utc,
        extra={"candidate_path": os.path.abspath(a.out), "n_reported": n_rep})
    fp.require_transition_receipt(receipt, "component_build", manifest_digest, predecessor_sha=manifest_digest)
    with open(a.out_receipt, "w") as fh:
        json.dump(receipt, fh, indent=2)
    print(f"[rollup] wrote {a.out} (cand {cand[:16]}) + component_build receipt {a.out_receipt}")
    for b in fp.BANDS:
        print(f"   {b:22s} sqrt_tr={np.sqrt(max(np.trace(per_band[b]),0)):.4e}")


if __name__ == "__main__":
    main()
