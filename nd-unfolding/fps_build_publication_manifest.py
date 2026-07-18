#!/usr/bin/env python3
"""Blockers 1/2/3 (Agent C): build the hash-bound PUBLICATION (negweight-refined) endpoint manifest +
its schema-versioned PASS receipt -- the single producer every covariance-chain gate consumes.

Each of the exact ten (band,endpoint) entries carries CANONICAL PATHS (unfold_root, input_merged_root,
config_path, source_path, launcher_path [the launcher ACTUALLY used, from the endpoint's config],
central_path, audit_path) plus strict lowercase-64-hex SHA256 for each, the fixed footing (lgbm/seed42/
5iter/weights/fps/negweight-refined), and the canonical 266/285 reported-mask fingerprint. All worker/
inventory failures are AGGREGATED (never first-failure exit) before ROOT is touched. ROOT is imported
lazily only to recompute the reported mask from CV.

NOT RUN in the repair round (no negweight-refined endpoints). Login-safe up to the mask recompute.

  python fps_build_publication_manifest.py --negweight-dir active_universe_5d/fps/unfolds_negweight_refined \
      --cv CV.root --utc <iso> --out-manifest M.json --out-receipt R.json
"""
import argparse
import json
import os
import subprocess
import sys

import fps_provenance as fp
import fps_verify_merged_receipt as fvm

UNFOLD_NAME = "fps2d_xsec_MEFHC_5iter_lgbm_uni_full_{b}_{ep}.root"
MERGE_NAME = "runEventLoopOmniFold_5D_FPS_active_{b}_{ep}_universes_full.root"
KNOWN_LAUNCHERS = {"sbatch_unfold_active_fps.sh", "run_active_fps_unfolds_interactive.sh"}


def _load_root():
    import ROOT
    ROOT.gROOT.SetBatch(True)
    return ROOT


def _complete(path):
    r = subprocess.run([sys.executable, "fps_unfold_complete.py", path],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    return r.returncode == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--negweight-dir", default="active_universe_5d/fps/unfolds_negweight_refined")
    ap.add_argument("--merged-dir", default="active_universe_5d/fps/merged")
    ap.add_argument("--cv", default="uq_fps/universe_sweep/fps2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root")
    ap.add_argument("--source", default="unfold_nd_omnifold_unbinned.py")
    ap.add_argument("--audit-json", default="active_universe_5d/fps/covariance/audit_merged_fps.json")
    ap.add_argument("--mask-artifact", default="active_universe_5d/fps/covariance/fps_reported_mask.json")
    ap.add_argument("--out-manifest", default="active_universe_5d/fps/covariance/fps_publication_manifest.json")
    ap.add_argument("--out-receipt", default="active_universe_5d/fps/covariance/fps_publication_pass_receipt.json")
    ap.add_argument("--utc", required=True)
    a = ap.parse_args()

    receipt = fvm.verify()                                     # validated full input hashes (no re-hash)
    input_hashes = receipt["verified_input_sha256"]
    lay = fp.layout_fingerprint()

    # ---- PASS 1: aggregate ALL endpoint/inventory failures FIRST (login-safe; before any header hash) ----
    valid, failures = [], []
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
                failures.append(f"{tag}: config bkg_mode={conf.get('bkg_mode')} != {fp.PUBLICATION_BKG_MODE}"); continue
            for k, v in fp.REQUIRED_FOOTING.items():
                if conf.get(k) != v:
                    failures.append(f"{tag}: config {k}={conf.get(k)} != {v}")
            launcher = conf.get("launcher")                    # attribute the ACTUAL launcher used
            if launcher not in KNOWN_LAUNCHERS or not os.path.exists(launcher):
                failures.append(f"{tag}: config launcher '{launcher}' unknown/absent"); continue
            abs_mp = os.path.abspath(mp)
            if abs_mp not in input_hashes:
                failures.append(f"{tag}: merged input not in validated receipt"); continue
            if not _complete(out):
                failures.append(f"{tag}: output not COMPLETE"); continue
            valid.append((b, ep, out, cfg, mp, abs_mp, launcher))
    if failures:
        print("[pub-manifest] FAIL -- aggregate worker/inventory failures:")
        for m in failures:
            print("   " + m)
        sys.exit(2)

    # ---- all ten valid: NOW compute header hashes + build entries ----
    cv_sha = fp.sha256_file(a.cv)
    src_sha = fp.sha256_file(a.source)
    audit_sha = fp.sha256_file(a.audit_json)
    mask_art = json.load(open(a.mask_artifact))
    if mask_art.get("fingerprint") != fp.REPORTED_MASK_FINGERPRINT:
        raise fp.FpsGateError("mask artifact fingerprint != canonical")
    endpoints = []
    for b, ep, out, cfg, mp, abs_mp, launcher in valid:
        foot = dict(fp.REQUIRED_FOOTING); foot["bkg_mode"] = fp.PUBLICATION_BKG_MODE
        endpoints.append({
            "band": b, "endpoint": ep,
            "unfold_root": out, "unfold_sha256": fp.sha256_file(out),
            "input_merged_root": mp, "input_merged_sha256": input_hashes[abs_mp],
            "config_path": cfg, "config_sha256": fp.sha256_file(cfg),
            "source_path": a.source, "source_sha256": src_sha,
            "launcher_path": launcher, "launcher_sha256": fp.sha256_file(launcher),
            "central_path": a.cv, "central_sha256": cv_sha,
            "audit_path": a.audit_json, "audit_sha256": audit_sha,
            "layout_fingerprint": lay, "reported_mask_hash": fp.REPORTED_MASK_FINGERPRINT,
            "central_hash": cv_sha, "footing": foot,
        })

    # ---- ROOT: recompute mask from CV == canonical ----
    ROOT = _load_root()
    f = ROOT.TFile.Open(a.cv); h = f.Get("hXSecND_flat")
    if not h:
        raise fp.FpsGateError(f"no hXSecND_flat in CV {a.cv}")
    import numpy as np
    cv = np.array([h.GetBinContent(i + 1) for i in range(h.GetNbinsX())]); f.Close()
    mask_fp = fp.require_reported_mask(cv > 0)

    manifest = {
        "schema": fp.PUBLICATION_SCHEMA, "label": fp.PUBLICATION_LABEL, "built_utc": a.utc,
        "nbins_extended": fp.NBINS_EXT, "n_reported": fp.N_REPORTED,
        "pt_edges": fp.PT_EDGES, "pz_edges": fp.PZ_EDGES, "ravel_order": fp.RAVEL_ORDER,
        "layout_fingerprint": lay, "reported_mask_hash": mask_fp, "central_hash": cv_sha,
        "central_cv_sha256": cv_sha, "reported_mask_artifact_sha256": fp.sha256_file(a.mask_artifact),
        "merged_input_receipt_run_id": receipt["run_id"],
        "merged_input_fps_hash_list_sha256": receipt["fps_hash_list_sha256"],
        "footing": {**fp.REQUIRED_FOOTING, "bkg_mode": fp.PUBLICATION_BKG_MODE},
        "endpoints": endpoints,
    }
    fp.require_publication_manifest(manifest)
    fp.require_recompute_hashes(manifest)                      # self-check: recompute all bound hashes
    with open(a.out_manifest, "w") as fh:
        json.dump(manifest, fh, indent=2)
    mdig = fp.sha256_file(a.out_manifest)
    pr = {"schema": "fps_publication_pass_receipt.v1", "result": "PASS",
          "manifest": os.path.abspath(a.out_manifest), "manifest_sha256": mdig, "validated_utc": a.utc}
    fp.require_pass_receipt(pr, mdig)
    with open(a.out_receipt, "w") as fh:
        json.dump(pr, fh, indent=2)
    print(f"[pub-manifest] wrote {a.out_manifest} (sha {mdig[:16]}) + PASS receipt; mask {mask_fp[:16]}")


if __name__ == "__main__":
    main()
