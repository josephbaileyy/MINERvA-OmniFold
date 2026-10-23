#!/usr/bin/env python3
"""RE-1 F: package a configuration-(e) product (P3 or P4) in the container its figure producers read.

    re1_to_root.py --dim 3 --product P3.npz --expect-product-sha256 S --current CUR3D.root \
        --expect-current-sha256 S --out P3.root --json receipt.json
    re1_to_root.py --dim 4 --product P4.npz ... (the same)

Container conversion only, by the production writers (``RE1-AMENDMENT-DECLARATION.md`` section 5.3; the
first pass's ``p5_to_root.py`` is the precedent):

* 3D: the 3D driver's own output block (``unfold_3d_omnifold_unbinned.py:704-740``): ``numpy_to_th3d`` for
  ``hXSec3D``; ``xsec_3d.project_eavail_marginal`` for ``hXSec2D``; ``xsec_3d.project_axis`` and
  ``numpy_to_th1d`` for ``hXSec_pt``, ``hXSec_pz`` and ``hXSec_eavail``.
* 4D: the ND driver's ``write_thnd`` for ``hXSecND_flat`` (the only object ``redraw_central_only.py`` reads).

The product carries no per-bin errors, so the histograms carry none (``err=None``, as the driver's
marginal-free objects do). CONTROL, before anything is written: the same projection is applied to the
CURRENT product's stored ``hXSec3D`` and must reproduce its stored ``hXSec2D`` and 1D projections bit for
bit (3D), or its ``hXSecND_flat`` must round-trip bit for bit (4D). The written file is read back and must
equal the product bit for bit. Either failure refuses and writes nothing to ``--out``.

MEASURES: nothing new. CANNOT AUTHORIZE: a figure, a number or a claim.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

_REPO = Path(__file__).resolve().parents[2]
for p in (_REPO / "3d-unfolding", _REPO / "2d-unfolding", _REPO / "nd-unfolding"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

SHAPES = {3: (14, 16, 7), 4: (14, 16, 7, 7)}


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def modules():
    import ROOT
    ROOT.gROOT.SetBatch(True)
    import xsec_3d  # before the 3D driver, so its `from xsec_3d import` reuses this checkout's module
    import unfold_3d_omnifold_unbinned as u3d
    import unfold_nd_omnifold_unbinned as und
    for m in (xsec_3d, u3d, und, und.u2d):
        if _REPO not in Path(m.__file__).resolve().parents:
            raise SystemExit(f"{m.__name__} imported from {m.__file__}, outside {_REPO}")
    return ROOT, xsec_3d, u3d, und


def th_array(h, dims: int) -> np.ndarray:
    if dims == 1:
        return np.array([h.GetBinContent(i) for i in range(1, h.GetNbinsX() + 1)])
    if dims == 2:
        return np.array([[h.GetBinContent(i, j) for j in range(1, h.GetNbinsY() + 1)]
                         for i in range(1, h.GetNbinsX() + 1)])
    return np.array([[[h.GetBinContent(i, j, k) for k in range(1, h.GetNbinsZ() + 1)]
                      for j in range(1, h.GetNbinsY() + 1)] for i in range(1, h.GetNbinsX() + 1)])


def projections_3d(x3, xsec_3d, u3d) -> dict:
    pt_e, pz_e, ea_e = u3d.PT_EDGES, u3d.PZ_EDGES, u3d.EAVAIL_EDGES
    out = {"hXSec2D": xsec_3d.project_eavail_marginal(x3, ea_e)}
    for ax in ("pt", "pz", "eavail"):
        _, out[f"hXSec_{ax}"] = xsec_3d.project_axis(x3, pt_e, pz_e, ea_e, ax)
    return out


def write_3d(ROOT, xsec_3d, u3d, x3: np.ndarray, out: Path, title: str) -> None:
    """The 3D driver's write block (:704-740) for the central objects, with err=None."""
    pt_e, pz_e, ea_e = u3d.PT_EDGES, u3d.PZ_EDGES, u3d.EAVAIL_EDGES
    pr = projections_3d(x3, xsec_3d, u3d)
    edges = {}
    for ax in ("pt", "pz", "eavail"):
        edges[ax], _ = xsec_3d.project_axis(x3, pt_e, pz_e, ea_e, ax)
    f = ROOT.TFile.Open(str(out), "RECREATE")
    f.cd()
    u3d.numpy_to_th3d(x3, None, "hXSec3D", "d^{3}#sigma/(dp_{T}dp_{||}dE_{avail}) " + title + ";"
                      "p_{T} (GeV/c);p_{||} (GeV/c);E_{avail} (GeV)", pt_e, pz_e, ea_e).Write()
    u3d.numpy_to_th2d(pr["hXSec2D"], None, "hXSec2D", "Eavail-marginal d^{2}#sigma/(dp_{T}dp_{||});"
                      "p_{T} (GeV/c);p_{||} (GeV/c)", pt_e, pz_e).Write()
    labels = {"pt": "d#sigma/dp_{T};p_{T} (GeV/c);d#sigma/dp_{T}",
              "pz": "d#sigma/dp_{||};p_{||} (GeV/c);d#sigma/dp_{||}",
              "eavail": "d#sigma/dE_{avail};E_{avail} (GeV);d#sigma/dE_{avail}"}
    for ax in ("pt", "pz", "eavail"):
        u3d.numpy_to_th1d(edges[ax], pr[f"hXSec_{ax}"], f"hXSec_{ax}", labels[ax]).Write()
    f.Close()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--dim", type=int, choices=sorted(SHAPES), required=True)
    ap.add_argument("--product", type=Path, required=True)
    ap.add_argument("--expect-product-sha256", required=True)
    ap.add_argument("--current", type=Path, required=True)
    ap.add_argument("--expect-current-sha256", required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--json", type=Path, required=True)
    a = ap.parse_args(argv)
    for p in (a.out, a.json):
        if p.exists():
            print(f"refusing to overwrite {p}", file=sys.stderr)
            return 3
    got = (sha256_path(a.product), sha256_path(a.current))
    if got != (a.expect_product_sha256, a.expect_current_sha256):
        print(f"input digests {got} differ from the expected ones", file=sys.stderr)
        return 4
    ROOT, xsec_3d, u3d, und = modules()
    shape = SHAPES[a.dim]
    z = np.load(a.product, allow_pickle=False)
    meta = json.loads(str(z["meta"]))
    if tuple(int(s) for s in z["shape"]) != shape or meta.get("bkg_mode") != "negweight-refined" \
            or meta.get("code_sha256", {}).get("candidate") != "R":
        print(f"{a.product} is not a {a.dim}D configuration-(e) product", file=sys.stderr)
        return 5
    x = np.asarray(z["xsec_flat"], np.float64)
    rec = {"dim": a.dim, "product": str(a.product), "product_sha256": got[0], "current": str(a.current),
           "current_sha256": got[1], "code_sha256": sha256_path(Path(__file__).resolve())}
    fc = ROOT.TFile.Open(str(a.current), "READ")
    if a.dim == 3:
        cur3 = th_array(fc.Get("hXSec3D"), 3)
        stored = {"hXSec2D": th_array(fc.Get("hXSec2D"), 2),
                  **{f"hXSec_{ax}": th_array(fc.Get(f"hXSec_{ax}"), 1) for ax in ("pt", "pz", "eavail")}}
        fc.Close()
        mine = projections_3d(cur3, xsec_3d, u3d)
        rec["control"] = {k: bool(np.array_equal(mine[k], stored[k])) for k in stored}
        if not all(rec["control"].values()):
            a.json.write_text(json.dumps(rec, indent=1) + "\n")
            print("control failed: the projections do not reproduce the current product's", file=sys.stderr)
            return 6
        write_3d(ROOT, xsec_3d, u3d, x.reshape(shape), a.out, "(RE-1 P3, configuration (e))")
        fb = ROOT.TFile.Open(str(a.out), "READ")
        back = th_array(fb.Get("hXSec3D"), 3).ravel(order="C")
        fb.Close()
    else:
        cur = th_array(fc.Get("hXSecND_flat"), 1)
        fc.Close()
        edges = [und.u2d.PT_EDGES, und.u2d.PZ_EDGES, und.EXTRA_AXES["eavail"]["edges"], und.EXTRA_AXES["q3"]["edges"]]
        tmp = a.out.with_name(a.out.name + ".control.root")
        f = ROOT.TFile.Open(str(tmp), "RECREATE")
        und.write_thnd(f, cur.reshape(shape), None, "hXSecND", "control", edges, None)
        f.Close()
        f = ROOT.TFile.Open(str(tmp), "READ")
        rec["control"] = {"hXSecND_flat": bool(np.array_equal(th_array(f.Get("hXSecND_flat"), 1), cur))}
        f.Close()
        tmp.unlink()
        if not rec["control"]["hXSecND_flat"]:
            a.json.write_text(json.dumps(rec, indent=1) + "\n")
            print("control failed: write_thnd does not round-trip the current product", file=sys.stderr)
            return 6
        f = ROOT.TFile.Open(str(a.out), "RECREATE")
        und.write_thnd(f, x.reshape(shape), None, "hXSecND", "RE-1 P4, configuration (e)", edges, None)
        f.Close()
        fb = ROOT.TFile.Open(str(a.out), "READ")
        back = th_array(fb.Get("hXSecND_flat"), 1)
        fb.Close()
    rec["readback_bitwise"] = bool(np.array_equal(back, x))
    if not rec["readback_bitwise"]:
        a.out.unlink()
        a.json.write_text(json.dumps(rec, indent=1) + "\n")
        print("readback differs from the product; nothing kept", file=sys.stderr)
        return 7
    rec["out_sha256"] = sha256_path(a.out)
    a.json.write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"out": str(a.out), "sha256": rec["out_sha256"], "control": rec["control"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
