#!/usr/bin/env python3
"""Zenodo change B (Joseph, 2026-11-27): re-export the sixteen-cell products from the V_F data product.

usage: python3 -I -B export_sixteen_vf.py REPO PACKAGE
  REPO     a checkout of this repository; committed files are read at origin/main through `git show`.
  PACKAGE  the package being built (~/codex-reports/note-measurement/zenodo-draft/package-rc10). Its sixteen-cell/ is
           rewritten; nothing else is touched.

The RC9 export (zenodo-draft/tools/export_products.py, G2) read the pre-V_F product (with-cpl, d6752d2c). This reads
fd/with-vf/data-product/fd_data_product_vf.json (1a37b082, the product make_values_fived16.py pins) and writes:
  - C_rep.csv: the reported covariance C_rep^(5D) = C_e^infl + C_model + C_resp + C_PL,5D
    (fd_data_product_vf_C_total_plus_C_resp_plus_C_PL5D_plus_DeltaC_e.csv);
  - its components C_e_infl.csv (new), C_e.csv, C_model.csv, C_resp.csv, C_PL5D.csv;
  - cells.csv (each cell's box, integral and sqrt(C_rep)_ii) and sixteen_cell.npz (the same arrays, and C_e_infl).
Checks, each a failure on disagreement (exit 1):
  - the inputs' sha256 pins; C_rep = C_e_infl + C_model + C_resp + C_PL5D (1e-12 of max); C_rep symmetric to 1e-12 and
    positive definite;
  - every per-cell percent sigma the note prints (values_fived16.tex at origin/main: sig-reported, sig-C_e,
    sig-C_e_infl, sig-C_model, sig-C_resp) and the 120 printed correlations, and f-R00..R15;
  - f equals RC9's exported f bit for bit (f does not change with V_F);
  - each matrix CSV written is byte-identical to the committed CSV of the same matrix in fd/with-vf/data-product/.
"""
import csv, hashlib, io, json, re, subprocess, sys
from pathlib import Path
import numpy as np

REPO, PKG = Path(sys.argv[1]), Path(sys.argv[2])
VF = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/with-vf/data-product"
PIN = {"dp": "1a37b082", "C_rep_csv": "6d48cb98", "C_e_infl_csv": "763f14c6"}
COMMITTED = {"C_rep": "fd_data_product_vf_C_total_plus_C_resp_plus_C_PL5D_plus_DeltaC_e.csv",
             "C_e_infl": "fd_data_product_vf_C_e_infl.csv", "C_e": "fd_data_product_vf_C_e.csv",
             "C_model": "fd_data_product_vf_C_model_abs.csv", "C_resp": "fd_data_product_vf_C_resp.csv",
             "C_PL5D": "fd_data_product_vf_C_PL5D.csv"}
fails = []


def blob(path):
    return subprocess.run(["git", "-C", str(REPO), "show", f"origin/main:{path}"], check=True, capture_output=True).stdout


def sha(b):
    return hashlib.sha256(b).hexdigest()


def check(ok, what):
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        fails.append(what)


raw = blob(f"{VF}/fd_data_product_vf.json")
check(sha(raw).startswith(PIN["dp"]), f"product sha256 starts {PIN['dp']}")
check(sha(blob(f"{VF}/{COMMITTED['C_rep']}")).startswith(PIN["C_rep_csv"]), f"committed C_rep CSV starts {PIN['C_rep_csv']}")
check(sha(blob(f"{VF}/{COMMITTED['C_e_infl']}")).startswith(PIN["C_e_infl_csv"]), f"committed C_e_infl CSV starts {PIN['C_e_infl_csv']}")
dp = json.loads(raw)
fv = dict(re.findall(r"\\@namedef\{fv@([^}]*)\}\{([^}]*)\}", blob("docs/analysis-note/values_fived16.tex").decode()))
cells = [c["cell"] for c in dp["cells"]]
check(cells == [f"R{i:02d}" for i in range(16)], "cells are R00-R15 in order")
f = np.array(dp["f"], float)
M = {k: np.array(v, float) for k, v in dp["matrices"].items()}
C_rep = M["C_total_plus_C_resp_plus_C_PL5D_plus_DeltaC_e"]
recon = M["C_e_infl"] + M["C_model_abs"] + M["C_resp"] + M["C_PL5D"]
check(np.max(np.abs(recon - C_rep)) <= 1e-12 * np.max(np.abs(C_rep)), "C_rep = C_e_infl + C_model + C_resp + C_PL5D")
asym = float(np.max(np.abs(C_rep - C_rep.T)) / np.max(np.abs(C_rep)))
check(asym < 1e-12, f"C_rep symmetric to max|C-C^T|/max|C| = {asym:.2e}")
check(np.min(np.linalg.eigvalsh(C_rep)) > 0, "C_rep positive definite")
for i, c in enumerate(cells):
    check(f"{f[i] / 1e-40:#.3g}".rstrip(".") == fv[f"f-{c}"], f"f-{c}: {f[i]:.6e} prints {fv[f'f-{c}']}")
old = np.load(PKG / "sixteen-cell/sixteen_cell.npz", allow_pickle=False)
check(np.array_equal(old["f"], f), "f equals RC9's exported f bit for bit")


def pct(x):
    return f"{100 * x:.2f}"


SIG = {"reported": C_rep, "C_e": M["C_e"], "C_e_infl": M["C_e_infl"], "C_model": M["C_model_abs"], "C_resp": M["C_resp"]}
for key, mat in SIG.items():
    rel = np.sqrt(np.diag(mat)) / f
    bad = [c for i, c in enumerate(cells) if pct(rel[i]) != fv[f"sig-{key}-{c}"]]
    check(not bad, f"sig-{key}: 16 cells agree with the note's printed percent" + (f" (differ: {bad})" if bad else ""))
sd = np.sqrt(np.diag(C_rep))
corr = C_rep / np.outer(sd, sd)
bad = []
for i in range(16):
    for j in range(i):
        x = f"{corr[i, j]:.2f}"
        x = ("$-$" + x[1:]) if x.startswith("-") else x
        if x != fv[f"corr-{cells[i]}-{cells[j]}"]:
            bad.append((cells[i], cells[j], x, fv[f"corr-{cells[i]}-{cells[j]}"]))
check(not bad, "corr: 120 lower-triangle entries agree with the note" + (f" (differ: {bad[:5]})" if bad else ""))

o2 = PKG / "sixteen-cell"
AX = ["pt", "pz", "eavail", "q3", "W"]
UNIT = {"pt": "GeV/c", "pz": "GeV/c", "eavail": "GeV", "q3": "GeV/c", "W": "GeV"}
with open(o2 / "cells.csv", "w", newline="") as fh:
    w = csv.writer(fh, lineterminator="\n")
    w.writerow(["cell"] + [f"{a}_lo_{UNIT[a]}" for a in AX] + [f"{a}_hi_{UNIT[a]}" for a in AX]
               + ["integral_cm2_per_nucleon", "sigma_rep_cm2_per_nucleon"])
    for i, c in enumerate(dp["cells"]):
        b = c["box"]
        w.writerow([c["cell"]] + [repr(float(b[a][0])) for a in AX] + [repr(float(b[a][1])) for a in AX]
                   + [repr(f[i]), repr(float(sd[i]))])
NAMES = {"C_rep": C_rep, "C_e_infl": M["C_e_infl"], "C_e": M["C_e"], "C_model": M["C_model_abs"], "C_resp": M["C_resp"],
         "C_PL5D": M["C_PL5D"]}
for name, mat in NAMES.items():
    with open(o2 / f"{name}.csv", "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["cell"] + cells)
        for i, c in enumerate(cells):
            w.writerow([c] + [repr(float(x)) for x in mat[i]])
    check((o2 / f"{name}.csv").read_bytes() == blob(f"{VF}/{COMMITTED[name]}"),
          f"{name}.csv is byte-identical to the committed {COMMITTED[name]}")
np.savez(o2 / "sixteen_cell.npz", cells=np.array(cells), f=f, **NAMES,
         box_lo=np.array([[c["box"][a][0] for a in AX] for c in dp["cells"]], float),
         box_hi=np.array([[c["box"][a][1] for a in AX] for c in dp["cells"]], float), axes=np.array(AX))
z = np.load(o2 / "sixteen_cell.npz", allow_pickle=False)
check(all(np.array_equal(z[k], v) for k, v in NAMES.items()) and np.array_equal(z["f"], f), "sixteen_cell.npz reloads equal")
for n in sorted(p.name for p in o2.iterdir()):
    print("wrote", n, sha((o2 / n).read_bytes()))
print("EXPORT B:", "PASS" if not fails else f"FAIL ({len(fails)})")
sys.exit(1 if fails else 0)
