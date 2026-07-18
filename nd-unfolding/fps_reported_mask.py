#!/usr/bin/env python3
"""Blocker 1/4 (Agent C, 2nd repair round): compute + COMMIT the exact 266/285 FPS reported mask
(CV>0 on the 285-bin C-order extended grid) BEFORE any endpoint production, and lock the fingerprint
construction to the orchestrator/verifier canonical value
  TARGET = 23b2a2f4e75f242141c0651052258a930ed38abc4f1740afaa0b349da78bda78
Tries a set of candidate constructions over the CV>0 mask and reports which reproduces TARGET, then
writes a read-only artifact active_universe_5d/fps/covariance/fps_reported_mask.json bound to the CV
sha256. Needs ROOT (26KB CV read) -> runs on a compute node.

  python fps_reported_mask.py --cv <CV.root> --out active_universe_5d/fps/covariance/fps_reported_mask.json
"""
import argparse
import hashlib
import json
import os

import numpy as np
import ROOT

import fps_provenance as fp

ROOT.gROOT.SetBatch(True)
TARGET = "23b2a2f4e75f242141c0651052258a930ed38abc4f1740afaa0b349da78bda78"


def _h(b):
    return hashlib.sha256(b).hexdigest()


def candidates(mask):
    idx = np.where(mask)[0]
    return {
        "bool_tobytes": _h(mask.astype(bool).tobytes()),
        "uint8_tobytes": _h(mask.astype(np.uint8).tobytes()),
        "packbits": _h(np.packbits(mask.astype(bool)).tobytes()),
        "idx_int64": _h(idx.astype("<i8").tobytes()),
        "idx_int32": _h(idx.astype("<i4").tobytes()),
        "idx_csv": _h(",".join(map(str, idx.tolist())).encode()),
        "idx_newline": _h("\n".join(map(str, idx.tolist())).encode()),
        "idx_newline_trail": _h(("\n".join(map(str, idx.tolist())) + "\n").encode()),
        "bitstring01": _h("".join("1" if x else "0" for x in mask).encode()),
        "bitstring01_nl": _h(("".join("1" if x else "0" for x in mask) + "\n").encode()),
        "n_slash_N_idxcsv": _h((f"{int(mask.sum())}/{mask.size}:" +
                                ",".join(map(str, idx.tolist()))).encode()),
        "space_join_idx": _h(" ".join(map(str, idx.tolist())).encode()),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cv", default="uq_fps/universe_sweep/fps2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root")
    ap.add_argument("--out", default="active_universe_5d/fps/covariance/fps_reported_mask.json")
    a = ap.parse_args()

    f = ROOT.TFile.Open(a.cv)
    if not f or f.IsZombie():
        raise SystemExit(f"[FAIL] cannot open CV {a.cv}")
    h = f.Get("hXSecND_flat")
    if not h:
        raise SystemExit(f"[FAIL] no hXSecND_flat in {a.cv}")
    nb = h.GetNbinsX()
    cv = np.array([h.GetBinContent(i + 1) for i in range(nb)])
    f.Close()
    if nb != fp.NBINS_EXT:
        raise SystemExit(f"[FAIL] CV nbins {nb} != {fp.NBINS_EXT}")
    mask = cv > 0
    n = int(mask.sum())
    cv_sha = fp.sha256_file(a.cv)
    print(f"[mask] CV={a.cv} nbins={nb} reported(CV>0)={n}  cv_sha256={cv_sha[:16]}")

    cand = candidates(mask)
    winner = None
    for name, val in cand.items():
        flag = "  <== MATCHES TARGET" if val == TARGET else ""
        print(f"   {name:22s} {val}{flag}")
        if val == TARGET:
            winner = name
    if winner is None:
        print(f"\n[mask] NO candidate construction reproduced TARGET {TARGET}")
        print("[mask] EVIDENCE-BLOCKED: cannot lock the reported-mask fingerprint construction")
        raise SystemExit(4)

    art = {
        "schema": "fps_reported_mask.v1", "readonly": True,
        "n_reported": n, "n_total": nb, "ravel_order": fp.RAVEL_ORDER,
        "reported_indices": np.where(mask)[0].tolist(),
        "fingerprint": TARGET, "fingerprint_construction": winner,
        "central_cv": a.cv, "central_cv_sha256": cv_sha,
        "layout_fingerprint": fp.layout_fingerprint(),
    }
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    if os.path.exists(a.out):
        os.chmod(a.out, 0o644)
    with open(a.out, "w") as fh:
        json.dump(art, fh, indent=2)
    os.chmod(a.out, 0o444)
    print(f"\n[mask] LOCKED construction='{winner}' == TARGET")
    print(f"[mask] wrote read-only {a.out}  (n_reported={n}/{nb})")


if __name__ == "__main__":
    main()
