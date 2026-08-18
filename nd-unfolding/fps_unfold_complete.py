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


def check(path, expect_nbins=None, min_complete=None, require_completeness=True):
    """COMPLETE per the definition at the top of this file. Reusable, not FPS-only.

    PARAMETERISED 2026-08-18 so the M(ii) member-axis work can REUSE this instead of adding a third
    copy of a kRecovered check. `BEN-481` measured that this file already carries the right COMPLETE
    definition and that only three hardcoded constants blocked reuse; `expect_nbins=None` skips the
    grid-size assertion for callers on a different binning, and `require_completeness=False` skips the
    globalCompleteness gate ENTIRELY -- both its presence/NaN half and its threshold half. Defaults
    preserve the FPS behaviour exactly, so every existing caller is unaffected.

    DO NOT REACH FOR `require_completeness=False` TO RELAX A THRESHOLD; pass `min_complete` instead.
    I wrote its first use with the justification "for products that do not write it" and that was
    false of the family I applied it to -- measured 2026-08-18, both writers of the 5D universe family
    emit the key unconditionally (`sweep_bank_5d.py:289`, `unfold_nd_omnifold_unbinned.py:1014`). The
    flag's coarseness is what made the mistake cheap to make: it bundles "the key may be absent" with
    "the floor does not transfer", and only the second was ever true. NaN is a reachable value with a
    known cause (`denom_nd.sum() <= 0`), so skipping the presence half admits a meaningless product.
    `analyze_universes_5d.py:load_flat` now passes `min_complete=0.0, require_completeness=True`.

    THE POINT OF REUSE HERE IS NOT TIDINESS. Two copies of a completeness rule drift, and the drift is
    invisible: each copy passes its own tests. The mediator's instruction was explicit -- if there is a
    shared helper, use it -- and this is the helper.
    """
    if expect_nbins is None:
        expect_nbins = EXPECT_NBINS
    if min_complete is None:
        min_complete = MIN_COMPLETE
    r = {"path": os.path.basename(path), "ok": False, "why": ""}
    if not os.path.exists(path):
        r["why"] = "missing"; return r
    if os.path.getsize(path) < 1024:
        r["why"] = f"tiny ({os.path.getsize(path)}B)"; return r
    # THE `if not f` DISJUNCT WAS DEAD CODE AND THAT MADE THIS GUARD LOOK REDUNDANT WHILE IT WAS BARE.
    # Under PyROOT 6.28 `TFile.Open` is PYTHONIZED TO RAISE OSError rather than return a null pointer
    # (_pythonization/_tfile.py:103), so on the dominant real failure mode -- an unopenable file --
    # control never reached this return and `why="zombie/unopenable"` could never be produced. Measured
    # by the mediator on truncated copies of a real 5D product at 99/97/95/90/80/60 %: every one raised
    # OSError out of `check()` instead of being classified, so the caller's clean SystemExit with its
    # diagnostic never appeared and a bare ROOT traceback appeared instead.
    #
    # The DIRECTION was always fail-closed -- nothing unsafe got through -- but a guard that cannot
    # report its own reason is a guard whose failures a future reader has to re-diagnose. And the
    # `not f or IsZombie()` idiom reads as belt-and-braces while being single-ply: the audit lane
    # measured 90 occurrences of it across 70 files, so this is one instance of a repo-wide shape.
    #
    # BOTH BRANCHES ARE KEPT. The except handles pythonized PyROOT; `not f` is still correct for a
    # build or call path that returns null, and IsZombie() for a file that opens degraded. What changed
    # is that the first is now REACHABLE.
    try:
        f = ROOT.TFile.Open(path)
    except OSError as exc:
        r["why"] = f"zombie/unopenable ({exc.__class__.__name__}: {exc})"; return r
    if not f or f.IsZombie():
        r["why"] = "zombie/unopenable"; return r
    if f.TestBit(ROOT.TFile.kRecovered):
        f.Close(); r["why"] = "kRecovered (truncated/uncleanly-closed write)"; return r
    h = f.Get("hXSecND_flat")
    if not h:
        f.Close(); r["why"] = "no hXSecND_flat"; return r
    nb = h.GetNbinsX()
    if expect_nbins and nb != expect_nbins:
        f.Close(); r["why"] = f"nbins {nb} != {expect_nbins}"; return r
    vals = np.array([h.GetBinContent(i + 1) for i in range(nb)])
    if not np.all(np.isfinite(vals)):
        f.Close(); r["why"] = "non-finite bins in hXSecND_flat"; return r
    s = float(vals.sum())
    if s <= 0:
        f.Close(); r["why"] = f"sum<=0 ({s:.3e})"; return r
    gc = f.Get("globalCompleteness")
    gcv = float(gc.GetVal()) if gc else None
    f.Close()
    if require_completeness:
        if gcv is None or not np.isfinite(gcv):
            r["why"] = "no/NaN globalCompleteness"; return r
        if gcv < min_complete:
            r["why"] = f"globalCompleteness {gcv:.4f} < {min_complete}"; return r
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
