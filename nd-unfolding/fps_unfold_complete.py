#!/usr/bin/env python3
"""Completeness gate for FPS active-endpoint unfolds (Agent C). A wall-killed unfold leaves a
present-but-TRUNCATED .root (ROOT auto-recovered on reopen, or the final hXSecND_flat/histograms
never written) -- the exact failure that makes a naive `-s`/existence skip consume a bad file. This
validates each output is COMPLETE so the driver never skips (and the P4 chain never ingests) a
truncated unfold. Exit 0 iff EVERY requested file is complete.

  fps_unfold_complete.py f1.root [f2 ...]   # explicit files
  fps_unfold_complete.py --all              # the 10 canonical endpoints (relative to CWD=nd-unfolding)

COMPLETE := TFile opens & not zombie; NOT TFile::kRecovered (recovery => truncated write);
hXSecND_flat present with nbins==285 (FPS 15pt x 19pz extended grid), all bins finite, sum>0;
globalCompleteness TParameter present, finite, > MIN_COMPLETE (the unfold's '[CHECK] c=' value).
"""
import argparse, os, sys
import numpy as np
import ROOT

ROOT.gROOT.SetBatch(True)
BANDS = ["BeamAngleX", "BeamAngleY", "MuonResolution",
         "Muon_Energy_MINERvA", "Muon_Energy_MINOS"]
OUTDIR = "active_universe_5d/fps/unfolds"
NAME = "fps2d_xsec_MEFHC_5iter_lgbm_uni_full_{b}_{ep}.root"
EXPECT_NBINS = 285          # 15 (pt) x 19 (pz) FPS extended grid
MIN_COMPLETE = 0.50         # sanity floor; healthy unfolds report c=1.0000


def check(path):
    r = {"path": os.path.basename(path), "ok": False, "why": ""}
    if not os.path.exists(path):
        r["why"] = "missing"; return r
    if os.path.getsize(path) < 1024:
        r["why"] = f"tiny ({os.path.getsize(path)}B)"; return r
    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        r["why"] = "zombie/unopenable"; return r
    if f.TestBit(ROOT.TFile.kRecovered):
        f.Close(); r["why"] = "kRecovered (truncated/uncleanly-closed write)"; return r
    h = f.Get("hXSecND_flat")
    if not h:
        f.Close(); r["why"] = "no hXSecND_flat"; return r
    nb = h.GetNbinsX()
    if nb != EXPECT_NBINS:
        f.Close(); r["why"] = f"nbins {nb} != {EXPECT_NBINS}"; return r
    vals = np.array([h.GetBinContent(i + 1) for i in range(nb)])
    if not np.all(np.isfinite(vals)):
        f.Close(); r["why"] = "non-finite bins in hXSecND_flat"; return r
    s = float(vals.sum())
    if s <= 0:
        f.Close(); r["why"] = f"sum<=0 ({s:.3e})"; return r
    gc = f.Get("globalCompleteness")
    gcv = float(gc.GetVal()) if gc else None
    f.Close()
    if gcv is None or not np.isfinite(gcv):
        r["why"] = "no/NaN globalCompleteness"; return r
    if gcv < MIN_COMPLETE:
        r["why"] = f"globalCompleteness {gcv:.4f} < {MIN_COMPLETE}"; return r
    r.update(ok=True, sum=s, gc=gcv, nbins=nb); return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    files = list(a.files)
    if a.all:
        files = [os.path.join(OUTDIR, NAME.format(b=b, ep=ep)) for b in BANDS for ep in (0, 1)]
    if not files:
        sys.exit("no files given")
    nbad = 0
    for p in files:
        r = check(p)
        if r["ok"]:
            print(f"[OK]   {r['path']} nbins={r['nbins']} sum={r['sum']:.4e} gc={r['gc']:.4f}")
        else:
            nbad += 1; print(f"[BAD]  {r['path']} :: {r['why']}")
    print(f"\n{len(files) - nbad}/{len(files)} complete")
    sys.exit(0 if nbad == 0 else 1)


if __name__ == "__main__":
    main()
