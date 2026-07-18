#!/usr/bin/env python3
"""Blockers 1/2/3 (Agent C): build the hash-bound PUBLICATION (negweight-refined) endpoint manifest
and its hash-bound PASS receipt -- the single producer the covariance chain's gates consume.

Aggregates ALL worker failures (never first-failure exit): for each of the exact ten (band,endpoint)
tags it requires the negweight output ROOT + its mode-stamped .config.json, config bkg_mode ==
negweight-refined and the fixed footing, and a COMPLETE ROOT (fps_unfold_complete). It binds full
output/input/config/source/launcher/central/audit SHA256 (input from the validated orchestrator
merged-input receipt -- no re-hash), RECOMPUTES the 266/285 reported mask from CV and requires it to
equal the canonical fingerprint, then emits the v2 manifest, self-checks require_publication_manifest,
and writes a PASS receipt bound to the manifest digest.

NOT RUN in the 2026-07-18 repair round (no negweight-refined endpoints exist; production gated on the
fps-adopt-verifier PASS). ROOT-facing (validates the endpoint ROOTs).

  python fps_build_publication_manifest.py --negweight-dir active_universe_5d/fps/unfolds_negweight_refined \
      --cv uq_fps/universe_sweep/fps2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root \
      --out-manifest active_universe_5d/fps/covariance/fps_publication_manifest.json \
      --out-receipt  active_universe_5d/fps/covariance/fps_publication_pass_receipt.json
"""
import argparse
import datetime
import json
import os
import subprocess
import sys

import numpy as np
import ROOT

import fps_provenance as fp
import fps_verify_merged_receipt as fvm

ROOT.gROOT.SetBatch(True)
UNFOLD_NAME = "fps2d_xsec_MEFHC_5iter_lgbm_uni_full_{b}_{ep}.root"
MERGE_NAME = "runEventLoopOmniFold_5D_FPS_active_{b}_{ep}_universes_full.root"


def _complete(path):
    r = subprocess.run([sys.executable, "fps_unfold_complete.py", path],
                       capture_output=True, text=True)
    return r.returncode == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--negweight-dir", default="active_universe_5d/fps/unfolds_negweight_refined")
    ap.add_argument("--merged-dir", default="active_universe_5d/fps/merged")
    ap.add_argument("--cv", default="uq_fps/universe_sweep/fps2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root")
    ap.add_argument("--source", default="unfold_nd_omnifold_unbinned.py")
    ap.add_argument("--launcher", default="sbatch_unfold_active_fps.sh")
    ap.add_argument("--audit-json", default="active_universe_5d/fps/covariance/audit_merged_fps.json")
    ap.add_argument("--mask-artifact", default="active_universe_5d/fps/covariance/fps_reported_mask.json")
    ap.add_argument("--out-manifest", default="active_universe_5d/fps/covariance/fps_publication_manifest.json")
    ap.add_argument("--out-receipt", default="active_universe_5d/fps/covariance/fps_publication_pass_receipt.json")
    ap.add_argument("--utc", required=True, help="timestamp string (caller-supplied for reproducibility)")
    a = ap.parse_args()

    # full input hashes from the validated orchestrator receipt (reuse; no 748GB re-hash)
    receipt = fvm.verify()
    input_hashes = receipt["verified_input_sha256"]

    # canonical mask (recompute from CV, compare) + committed artifact binding
    f = ROOT.TFile.Open(a.cv)
    h = f.Get("hXSecND_flat")
    if not h:
        raise fp.FpsGateError(f"no hXSecND_flat in CV {a.cv}")
    cv = np.array([h.GetBinContent(i + 1) for i in range(h.GetNbinsX())])
    f.Close()
    mask_fp = fp.require_reported_mask(cv > 0)          # == canonical or raises
    mask_art = json.load(open(a.mask_artifact))
    if mask_art.get("fingerprint") != mask_fp:
        raise fp.FpsGateError("mask artifact fingerprint != recomputed canonical")

    cv_sha = fp.sha256_file(a.cv)
    src_sha = fp.sha256_file(a.source)
    launcher_sha = fp.sha256_file(a.launcher)
    audit_sha = fp.sha256_file(a.audit_json)
    lay = fp.layout_fingerprint()

    endpoints, failures = [], []
    for b in fp.BANDS:
        for ep in fp.ENDPOINTS:
            tag = f"{b}_{ep}"
            out = os.path.join(a.negweight_dir, UNFOLD_NAME.format(b=b, ep=ep))
            cfg = out + ".config.json"
            mp = os.path.join(a.merged_dir, MERGE_NAME.format(b=b, ep=ep))
            if not os.path.exists(out):
                failures.append(f"{tag}: negweight output missing"); continue
            if not os.path.exists(cfg):
                failures.append(f"{tag}: config receipt missing"); continue
            conf = json.load(open(cfg))
            if conf.get("bkg_mode") != fp.PUBLICATION_BKG_MODE:
                failures.append(f"{tag}: config bkg_mode={conf.get('bkg_mode')} != {fp.PUBLICATION_BKG_MODE}")
                continue
            for k, v in fp.REQUIRED_FOOTING.items():
                if conf.get(k) != v:
                    failures.append(f"{tag}: config {k}={conf.get(k)} != {v}")
            if not _complete(out):
                failures.append(f"{tag}: output not COMPLETE (fps_unfold_complete)"); continue
            abs_mp = os.path.abspath(mp)
            if abs_mp not in input_hashes:
                failures.append(f"{tag}: merged input not in validated receipt"); continue
            foot = dict(fp.REQUIRED_FOOTING); foot["bkg_mode"] = fp.PUBLICATION_BKG_MODE
            endpoints.append({
                "band": b, "endpoint": ep,
                "unfold_sha256": fp.sha256_file(out),
                "input_merged_sha256": input_hashes[abs_mp],
                "config_sha256": fp.sha256_file(cfg),
                "source_sha256": src_sha, "launcher_sha256": launcher_sha,
                "central_sha256": cv_sha, "audit_sha256": audit_sha,
                "layout_fingerprint": lay, "reported_mask_hash": mask_fp, "central_hash": cv_sha,
                "footing": foot,
            })
    if failures:
        print("[pub-manifest] FAIL -- aggregate worker/inventory failures:")
        for m in failures:
            print("   " + m)
        sys.exit(2)

    manifest = {
        "schema": fp.PUBLICATION_SCHEMA, "label": fp.PUBLICATION_LABEL,
        "built_utc": a.utc,
        "nbins_extended": fp.NBINS_EXT, "n_reported": fp.N_REPORTED,
        "pt_edges": fp.PT_EDGES, "pz_edges": fp.PZ_EDGES, "ravel_order": fp.RAVEL_ORDER,
        "layout_fingerprint": lay, "reported_mask_hash": mask_fp, "central_hash": cv_sha,
        "central_cv_sha256": cv_sha, "reported_mask_artifact_sha256": fp.sha256_file(a.mask_artifact),
        "merged_input_receipt_run_id": receipt["run_id"],
        "merged_input_fps_hash_list_sha256": receipt["fps_hash_list_sha256"],
        "footing": {**fp.REQUIRED_FOOTING, "bkg_mode": fp.PUBLICATION_BKG_MODE},
        "endpoints": endpoints,
    }
    fp.require_publication_manifest(manifest)          # self-check: schema/label/inventory/mask/hashes
    with open(a.out_manifest, "w") as fh:
        json.dump(manifest, fh, indent=2)
    mdig = fp.sha256_file(a.out_manifest)
    pass_receipt = {"schema": "fps_publication_pass_receipt.v1", "result": "PASS",
                    "manifest": os.path.abspath(a.out_manifest), "manifest_sha256": mdig,
                    "validated_utc": a.utc}
    fp.require_pass_receipt(pass_receipt, mdig)
    with open(a.out_receipt, "w") as fh:
        json.dump(pass_receipt, fh, indent=2)
    print(f"[pub-manifest] wrote {a.out_manifest} (sha256 {mdig[:16]}) + PASS receipt {a.out_receipt}")
    print(f"[pub-manifest] 10/10 negweight-refined endpoints bound; mask={mask_fp[:16]}")


if __name__ == "__main__":
    main()
