"""COV2D's pseudo-data writer (COV2D-DECLARATION.md section 4.3): a file holding one TTree ``data`` in $CV's data
schema and $CV's dataPOTUsed, for ``re2_driver.py --data-file``.

* ``draw_counts``: k = Poisson(lambda+) per row, signal rows first, then background rows, from one generator; the
  clipped mass is recorded (cov2d.lam_plus).
* ``expand``: each reco-passing row with k > 0 becomes k identical rows (measured, measured_pz, measured_pass = 1), in
  row order, signal rows before background rows. The data tree carries no weight, so a count is a repeated row.
* ``write_data_file``: the tree and the parameter, with $CV's leaf types (``LEAVES``), the tree in one cycle: AutoSave
  is off, because on $CV's 4,119,797 rows it left ``data;2`` and ``data;3`` and failed control (2a) (addendum A1).
* ``writer_control`` (control (2), its writer half): $CV's own data tree written through ``write_data_file`` must
  equal $CV's bitwise, by control 1's ``compare_tree`` imported unchanged, and the file's dataPOTUsed must equal
  $CV's.

  python cov2d_writer.py control --out PATH [--cv PATH]

MEASURES: nothing by itself. CANNOT AUTHORIZE: a run.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
CONTROL1 = REPO / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/control1"
for p in (HERE, CONTROL1):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
import cov2d as c  # noqa: E402

CV = "/global/cfs/cdirs/m3246/josephrb/two-d-followup-20261010/xr-input/runEventLoopOmniFold_MEFHC.root"
BRANCHES = ("measured", "measured_pz", "measured_pass")
LEAVES = {"measured": ("d", "D"), "measured_pz": ("d", "D"), "measured_pass": ("B", "b")}


def draw_counts(lam_sig: np.ndarray, lam_bkg: np.ndarray, rng: np.random.Generator):
    """Poisson counts at lambda+ for the signal rows, then the background rows, and each stream's record."""
    ls, rs = c.lam_plus(lam_sig)
    lb, rb = c.lam_plus(lam_bkg)
    return rng.poisson(ls), rng.poisson(lb), {"signal": rs, "background": rb}


def expand(pt: np.ndarray, pz: np.ndarray, passed: np.ndarray, k: np.ndarray) -> dict:
    """Rows that pass, each repeated k times, in row order."""
    keep = np.asarray(passed, bool) & (k > 0)
    n = k[keep]
    return {"measured": np.repeat(np.asarray(pt, np.float64)[keep], n),
            "measured_pz": np.repeat(np.asarray(pz, np.float64)[keep], n),
            "measured_pass": np.ones(int(n.sum()), np.uint8)}


def concat(*parts: dict) -> dict:
    return {b: np.concatenate([p[b] for p in parts]) for b in BRANCHES}


def write_data_file(path: str | Path, cols: dict, data_pot: float) -> None:
    import ROOT
    from array import array
    f = ROOT.TFile.Open(str(path), "RECREATE")
    if not f or f.IsZombie():
        raise c.Refusal(f"could not create {path}")
    t = ROOT.TTree("data", "data")
    t.SetAutoSave(0)  # no intermediate cycles: the final Write is the tree's only key
    bufs = {}
    for b in BRANCHES:
        code, leaf = LEAVES[b]
        bufs[b] = array(code, [0])
        t.Branch(b, bufs[b], f"{b}/{leaf}")
    m, mz, mp = (np.asarray(cols[b]) for b in BRANCHES)
    if not (m.size == mz.size == mp.size):
        raise c.Refusal("the data columns differ in length")
    bm, bz, bp = bufs["measured"], bufs["measured_pz"], bufs["measured_pass"]
    for i in range(m.size):
        bm[0], bz[0], bp[0] = float(m[i]), float(mz[i]), int(mp[i])
        t.Fill()
    t.Write()
    ROOT.TParameter("double")("dataPOTUsed", float(data_pot)).Write()
    f.Close()


def read_cv_data(path: str) -> tuple[dict, float]:
    """$CV's data tree and dataPOTUsed through an O_NOATIME descriptor."""
    import uproot
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOATIME), "rb") as fh:
        f = uproot.open(fh)
        cols = f["data"].arrays(list(BRANCHES), library="np")
        pot = float(f["dataPOTUsed"].member("fVal"))
    return {b: np.asarray(cols[b]) for b in BRANCHES}, pot


def writer_control(cv: str, out: str) -> list[str]:
    """Write $CV's data tree through the writer, then compare it with $CV's by control 1's compare_tree."""
    import uproot
    import control1_content_check as cc
    cols, pot = read_cv_data(cv)
    write_data_file(out, cols, pot)
    failures: list[str] = []
    with cc.open_noatime(cv) as hcv, open(out, "rb") as hw:
        fcv, fw = uproot.open(hcv), uproot.open(hw)
        cc.compare_tree(fcv, fw, "data", cc.STEP, failures)
        if fw["dataPOTUsed"].member("fVal") != fcv["dataPOTUsed"].member("fVal"):
            failures.append("dataPOTUsed differs")
        extra = sorted(set(fw.classnames(recursive=False)) - {"data;1", "dataPOTUsed;1"})
        if extra:
            failures.append(f"unexpected keys {extra}")
    return failures


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    pc = sub.add_parser("control")
    pc.add_argument("--out", required=True)
    pc.add_argument("--cv", default=CV)
    args = ap.parse_args(argv)
    before = int(os.stat(args.cv).st_atime)
    failures = writer_control(args.cv, args.out)
    if int(os.stat(args.cv).st_atime) != before:
        failures.append("CV atime moved")
    for f in failures:
        print(f"FAILURE {f}")
    print(f"WRITER-CONTROL {'FAIL' if failures else 'PASS'} failures={len(failures)}")
    return 3 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
