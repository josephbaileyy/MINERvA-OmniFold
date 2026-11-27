#!/usr/bin/env python3
"""Zenodo change E(a) (Joseph, 2026-11-27): the 2D central values on MINERvA's published p_T edges, as a new item.

usage: python3 -I -B export_published_edges.py REPO PACKAGE RC9_DIR
  REPO     a checkout of this repository; committed files are read at origin/main through `git show`.
  PACKAGE  the package being built (package-rc10); writes PACKAGE/result-products-2d-published-edges/ only.
  RC9_DIR  RC9's unpacked tree, for data/figs/fig_arrays.npz (the published values and covariance it redistributes).

The central values are regenA's input E (ibu-chi2-20261123/regenA, #1322): E_R's histogram hXSec2D on the published
p_T edges, docs/orchestration/state/ibu-chi2-20261123/tier1/units/e/er.root (sha256 5171c7b8). The same 224 values are
2d-unfolding/evw2d/references.npz's `paper` vector (1b214582), which records that source. Central values only: the note
gives our uncertainties only on our grid, so no OmniFold covariance on these edges exists or is invented; a comparison
uses the published covariance.
Checks (exit 1 on any failure): the pins; er.root's hXSec2D equals references.npz `paper` bit for bit, and its axes equal
`paper_pt_edges`/`paper_pz_edges`; the reported cells equal the package's 2D result's 205 cells and the published
covariance's reported bins; regenA's P1a and P7 numbers are reproduced: chi2/ndf against the published total
covariance 434.89/205, pull mean 0.133 and RMS 0.513, 175/205 within 5 %.
"""
import csv, hashlib, io, json, subprocess, sys, tempfile
from pathlib import Path
import numpy as np
import uproot

REPO, PKG, RC9 = (Path(a) for a in sys.argv[1:4])
ER = "docs/orchestration/state/ibu-chi2-20261123/tier1/units/e/er.root"
REFS = "2d-unfolding/evw2d/references.npz"
PIN = {"er": "5171c7b8ecacda6090e242349dd622218c1c38885c60ef8b91027033a8c4b780",
       "refs": "1b21458283c06531c9791efdc1e15f9d685d0733e398288a715768d61b612a03"}
fails = []


def blob(path):
    return subprocess.run(["git", "-C", str(REPO), "show", f"origin/main:{path}"], check=True, capture_output=True).stdout


def sha(b):
    return hashlib.sha256(b).hexdigest()


def check(ok, what):
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        fails.append(what)


er_b, refs_b = blob(ER), blob(REFS)
check(sha(er_b) == PIN["er"], f"er.root sha256 {PIN['er'][:8]}")
check(sha(refs_b) == PIN["refs"], f"references.npz sha256 {PIN['refs'][:8]}")
refs = np.load(io.BytesIO(refs_b), allow_pickle=False)
meta = json.loads(str(refs["meta"]))
check(meta["paper"]["sha256"] == PIN["er"], "references.npz records er.root 5171c7b8 as its `paper` source")
with tempfile.TemporaryDirectory() as td:
    (Path(td) / "er.root").write_bytes(er_b)
    h = uproot.open(Path(td) / "er.root")["hXSec2D"]
    vals, xe, ye = h.to_numpy()
# find the axis orientation that matches the published edges exactly (shapes 15 and 17)
pt_e, pz_e = np.asarray(refs["paper_pt_edges"]), np.asarray(refs["paper_pz_edges"])
same = lambda a, b: a.shape == b.shape and bool(np.array_equal(a, b))
if same(xe, pz_e) and same(ye, pt_e):
    grid = vals.T  # (pT, p_par)
elif same(xe, pt_e) and same(ye, pz_e):
    grid = vals
else:
    grid = None
check(grid is not None, "er.root's hXSec2D axes equal the published p_T and p_par edges")
flat = np.asarray(grid, dtype=float).reshape(-1) if grid is not None else None
check(flat is not None and np.array_equal(flat, np.asarray(refs["paper"])),
      "er.root hXSec2D (pT x 16 + p_par order) equals references.npz `paper` bit for bit")
r2 = np.load(PKG / "result-products-2d/result_2d.npz", allow_pickle=False)
cells = r2["cells"]
fig = np.load(RC9 / "data/figs/fig_arrays.npz", allow_pickle=False)
reported = np.flatnonzero(np.diag(fig["cov_total"]) > 0)
check(np.array_equal(reported, cells), "the 205 reported cells equal the published covariance's reported bins")
x = flat[cells]
pv, Cp, ap = fig["paper_v"][cells], fig["cov_total"][np.ix_(cells, cells)], fig["area_paper"][cells]
d = x - pv
chi2 = float(d @ np.linalg.pinv(Cp) @ d)
pull = d / np.sqrt(np.diag(Cp))
within5 = int(np.sum(np.abs(x / pv - 1) < 0.05))
check(abs(chi2 - 434.89) < 0.005, f"chi2 vs the published total covariance {chi2:.4f} (regenA P1a 434.89/205)")
check(abs(chi2 / 205 - 2.121436) < 5e-6, f"chi2/ndf {chi2 / 205:.6f} (A3's D_E_R 2.121436)")
check(f"{pull.mean():.3f}" == "0.133" and f"{pull.std():.3f}" == "0.513",
      f"pull mean {pull.mean():.4f} and RMS {pull.std():.4f} (P1a 0.133 / 0.513)")
check(within5 == 175, f"{within5}/205 within 5 % (P7 175/205)")
o = PKG / "result-products-2d-published-edges"
o.mkdir(parents=True, exist_ok=True)
with open(o / "cells.csv", "w", newline="") as fh:
    w = csv.writer(fh, lineterminator="\n")
    w.writerow(["cell_id", "pt_index", "ppar_index", "pt_lo_GeV/c", "pt_hi_GeV/c", "ppar_lo_GeV/c", "ppar_hi_GeV/c",
                "d2sigma_dpt_dppar_cm2_per_(GeV/c)2_per_nucleon"])
    for c, v in zip(cells, x):
        i, j = int(c) // 16, int(c) % 16
        w.writerow([int(c), i, j, repr(float(pt_e[i])), repr(float(pt_e[i + 1])), repr(float(pz_e[j])),
                    repr(float(pz_e[j + 1])), repr(float(v))])
np.savez(o / "result_2d_published_edges.npz", cells=cells, x=x, pt_edges=pt_e, ppar_edges=pz_e)
z = np.load(o / "result_2d_published_edges.npz", allow_pickle=False)
check(np.array_equal(z["x"], x) and np.array_equal(z["cells"], cells), "result_2d_published_edges.npz reloads equal")
for n in sorted(p.name for p in o.iterdir()):
    print("wrote", n, sha((o / n).read_bytes()))
print("EXPORT E(a):", "PASS" if not fails else f"FAIL ({len(fails)})")
sys.exit(1 if fails else 0)
