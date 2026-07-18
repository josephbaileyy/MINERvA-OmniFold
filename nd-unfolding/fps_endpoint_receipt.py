#!/usr/bin/env python3
"""Blocker 3 (Agent C, repair-3): ONE strict resume/completion validator behind BOTH FPS endpoint
launchers (batch + interactive). Writes / checks a schema-versioned per-endpoint receipt with LIVE
output/input/config/source/launcher/central/audit hashes + the canonical reported-mask fingerprint,
attributing the launcher ACTUALLY used (passed by the caller). ROOT-facing (completeness + mask
recompute) -> runs on the compute node during production, not the login node.

  # after an atomic ROOT publish, mint the receipt LAST (validates completeness first):
  fps_endpoint_receipt.py write --out OUT.root --band B --endpoint E --bkg-mode negweight-refined \
      --merged M.root --source unfold_...py --launcher <the launcher used> --central CV.root \
      --audit audit_merged_fps.json --receipt OUT.root.config.json

  # skip only when the ROOT recomputes complete AND the receipt's live output hash matches:
  fps_endpoint_receipt.py check --out OUT.root --receipt OUT.root.config.json   # rc 0 = skip-safe
"""
import argparse
import datetime
import json
import os
import subprocess
import sys

import fps_provenance as fp

SCHEMA = "fps_endpoint_receipt.v1"


def _complete(path):
    r = subprocess.run([sys.executable, "fps_unfold_complete.py", path],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    return r.returncode == 0


def _load_root():
    import ROOT
    ROOT.gROOT.SetBatch(True)
    return ROOT


def _recompute_mask(central):
    ROOT = _load_root()
    f = ROOT.TFile.Open(central); h = f.Get("hXSecND_flat")
    if not h:
        raise fp.FpsGateError(f"no hXSecND_flat in {central}")
    import numpy as np
    cv = np.array([h.GetBinContent(i + 1) for i in range(h.GetNbinsX())]); f.Close()
    return fp.require_reported_mask(cv > 0)     # == canonical or raises


def cmd_write(a):
    if not _complete(a.out):
        raise fp.FpsGateError(f"endpoint output not COMPLETE, refusing receipt: {a.out}")
    if a.bkg_mode != fp.PUBLICATION_BKG_MODE:
        raise fp.FpsGateError(f"bkg_mode {a.bkg_mode} != {fp.PUBLICATION_BKG_MODE}")
    mask = _recompute_mask(a.central)
    receipt = {
        "schema": SCHEMA, "result": "PASS", "band": a.band, "endpoint": int(a.endpoint),
        "bkg_mode": a.bkg_mode, "footing": {**fp.REQUIRED_FOOTING, "bkg_mode": a.bkg_mode},
        "reported_mask_hash": mask,
        "output_sha256": fp.sha256_file(a.out),
        "input_merged_sha256": fp.sha256_file(a.merged),
        "source_sha256": fp.sha256_file(a.source),
        "launcher": os.path.basename(a.launcher), "launcher_sha256": fp.sha256_file(a.launcher),
        "central_sha256": fp.sha256_file(a.central), "audit_sha256": fp.sha256_file(a.audit),
        "completed_utc": a.utc or datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    tmp = a.receipt + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(receipt, fh, indent=2)
    os.replace(tmp, a.receipt)                  # atomic receipt publish, LAST
    print(f"[endpoint-receipt] wrote {a.receipt} (output {receipt['output_sha256'][:12]}, "
          f"launcher {receipt['launcher']})")


def cmd_check(a):
    """rc 0 iff the ROOT recomputes COMPLETE and the receipt's live output hash still matches (skip)."""
    if not (os.path.exists(a.out) and os.path.exists(a.receipt)):
        sys.exit(1)
    try:
        rec = json.load(open(a.receipt))
        if rec.get("schema") != SCHEMA or rec.get("result") != "PASS":
            sys.exit(1)
        if not _complete(a.out):
            sys.exit(1)
        if fp.sha256_file(a.out) != rec.get("output_sha256"):
            sys.exit(1)
    except Exception:
        sys.exit(1)
    sys.exit(0)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("write")
    for f in ("out", "band", "endpoint", "bkg-mode", "merged", "source", "launcher", "central", "audit", "receipt"):
        w.add_argument("--" + f, required=True)
    w.add_argument("--utc", default=None)
    c = sub.add_parser("check")
    c.add_argument("--out", required=True)
    c.add_argument("--receipt", required=True)
    a = ap.parse_args()
    if a.cmd == "write":
        a.bkg_mode = getattr(a, "bkg_mode")
        cmd_write(a)
    else:
        cmd_check(a)


if __name__ == "__main__":
    main()
