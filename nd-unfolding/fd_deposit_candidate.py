#!/usr/bin/env python3
"""The 5D result's deposit candidate (state/measurement-paper/5d-community-20261024/fd/deposit-candidate/README.md;
DECISION-20261028-joseph-result-table-and-deposit-package.md item 2): the sixteen-cell result's cell definitions,
measured vector, reported covariance C_total + C_resp and its correlation matrix, as CSV and one JSON, written from
the committed data product (fd/data-product/fd_data_product.json) and nothing else.

``build`` writes the package; ``check`` re-reads it from disk and refuses (exit 1) unless every control holds:
* P0  the data product and Stage G's readout are the pinned bytes, and the package's own file digests hold;
* P1  the cells, their boxes and H2 boxes are the data product's; each cell's box is exactly the union of its H2
      boxes; no two cells share an H2 box; the unreported boxes are exactly the H2 boxes in no cell;
* P2  f, the covariance and the correlation, from every CSV and from the JSON, are the data product's bit for bit;
* P3  the covariance is symmetric to 1e-12 of its largest entry and positive definite; sigma is sqrt(diag); the correlation is the covariance's;
* P4  GiBUU's subset is Stage G's eight cells and is exactly the cells with p_parallel's upper edge at 4.5 GeV/c;
* P5  every Stage G chi2 in fd_g_readout.json (five predictions, total and shape-only) is recomputed by Stage G's own
      compare() from the package's f and covariance and the readout's g and V_g = (sigma_Vg_over_f f)^2, to 1e-10
      relative; the readout's f is the package's.

MEASURES: nothing; a copy of the committed data product in a deposit layout, with its checks.
CANNOT AUTHORIZE: an upload, a deposit, a DOI, a release, supplemental material, a claim or paper text.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import sys
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import fd_g_compare as G  # noqa: E402  (compare, Stop, report)

N = 16
CELLS = [f"R{i:02d}" for i in range(N)]
AXES = ("pt", "pz", "eavail", "q3", "W")
UNITS = {"pt": "GeV/c", "pz": "GeV/c", "eavail": "GeV", "q3": "GeV", "W": "GeV"}
H2_EDGES = {"pt": [0.0, 0.7, 4.5], "pz": [1.5, 4.5, 60.0], "eavail": [0.0, 0.8, 100.0],
            "q3": [0.0, 2.0, 100.0], "W": [0.0, 1.8, 100.0]}   # s5p_stage1_inspect.H2_EDGES, checked in P1
GIBUU_PZ_HI = 4.5
CHI2_TOL = 1e-10
PINS = {"data_product": "b79556f0538c81942c0ddd3770ae55e5c6fe9ad53df47e470d306f727d7e7072",
        "g_readout": "75a9ddee19a7affe7e3bc10bf0cba8e5ebaa71132686e5ae116f1454d7bafcee"}
FILES = ("cells.csv", "covariance.csv", "correlation.csv", "deposit.json")
STATUS = "candidate, not deposited: nothing is uploaded and no DOI is minted until Joseph releases it"
LABELS = {
    "what": "the 5D result on its sixteen reporting cells R00-R15: cell definitions, the measured vector f, the "
            "reported covariance C_total + C_resp and its correlation matrix",
    "status": STATUS,
    "order": "every vector and matrix is in the cell order R00, R01, ..., R15 (cells.csv's row order)",
    "units": "f: each cell's integrated cross section, cm^2/nucleon (a cell integral, not a differential density); "
             "covariance: (cm^2/nucleon)^2; sigma = sqrt(diag(covariance)), cm^2/nucleon; box edges: p_T and "
             "p_parallel in GeV/c, E_avail, q3 and W in GeV",
    "edges": "the upper edge 100 GeV on E_avail, q3 and W is the analysis grid's last edge: the last bin on those "
             "axes is a catch bin to 100 GeV; 4.5 GeV/c on p_T and 60 GeV/c on p_parallel are the grid's outer "
             "edges too. A cell's integral covers only its box inside the grid; no edge is infinity",
    "covariance": "C_total + C_resp = C_e + C_model_abs + C_resp, the data's reported covariance (the data "
                  "product's C_total_plus_C_resp). The paper's chi2 for a prediction g on its cells c is "
                  "d^T (C + V_g)^-1 d with d = f - g, C this covariance on c, and V_g = diag of g's own "
                  "finite-MC variance; V_g and g are the prediction's, not in this package",
    "gibuu": "GiBUU is compared on the eight cells with p_parallel < 4.5 GeV/c only (gibuu_subset = 1)",
    "unreported": "the sixteen cells cover 28 of the 32 H2 boxes; the four unreported boxes are listed with their "
                  "bounds and are in no cell",
    "not_citable_for": "coverage; any reading, claim or release text",
}


class Stop(Exception):
    pass


def report(control: str, name: str, ok: bool, why: str = "differs") -> None:
    print(json.dumps({"control": control, "check": name, "ok": bool(ok)}), flush=True)
    if not ok:
        raise Stop(f"{control}: {name}: {why}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csv_text(head: list, rows: list) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(head)
    for r in rows:
        w.writerow([repr(x) if isinstance(x, float) else x for x in r])
    return buf.getvalue()


def matrix_csv(C: np.ndarray) -> str:
    return csv_text(["cell", *CELLS], [[CELLS[i], *[float(x) for x in C[i]]] for i in range(N)])


def read_matrix_csv(text: str) -> np.ndarray:
    rows = list(csv.reader(io.StringIO(text)))
    if rows[0] != ["cell", *CELLS] or [r[0] for r in rows[1:]] != CELLS:
        raise Stop("a matrix CSV's header or cell order is not R00-R15")
    return np.array([[float(x) for x in r[1:]] for r in rows[1:]])


def h2_box(index: int) -> dict:
    """The bounds of H2 box ``index``: C order over AXES, two bins per axis (s5p_stage1_inspect.coarse_map)."""
    bits = [(index >> (len(AXES) - 1 - k)) & 1 for k in range(len(AXES))]
    return {ax: [H2_EDGES[ax][b], H2_EDGES[ax][b + 1]] for ax, b in zip(AXES, bits)}


def boxes_inside(box: dict) -> set:
    return {i for i in range(2 ** len(AXES))
            if all(box[ax][0] <= h2_box(i)[ax][0] and h2_box(i)[ax][1] <= box[ax][1] for ax in AXES)}


def gibuu_flag(cell: dict) -> int:
    return int(cell["box"]["pz"][1] <= GIBUU_PZ_HI)


def load_pinned(path: Path, key: str) -> dict:
    report("P0", f"{key} sha256 is the pin", sha256(path) == PINS[key], f"{sha256(path)} != {PINS[key]}")
    return json.loads(path.read_text())


def package(dp: dict) -> dict[str, str]:
    """The package's files, from the data product alone."""
    f = np.array(dp["f"], float)
    C = np.array(dp["matrices"]["C_total_plus_C_resp"], float)
    rho = np.array(dp["correlation"], float)
    sigma = np.sqrt(np.diag(C))
    head = ["cell", "h2_boxes", *[f"{ax}_{e}" for ax in AXES for e in ("lo", "hi")], "gibuu_subset",
            "f_cm2_per_nucleon", "sigma_cm2_per_nucleon"]
    rows = [[c["cell"], " ".join(map(str, c["h2_boxes"])), *[float(v) for ax in AXES for v in c["box"][ax]],
             gibuu_flag(c), float(f[i]), float(sigma[i])] for i, c in enumerate(dp["cells"])]
    files = {"cells.csv": csv_text(head, rows), "covariance.csv": matrix_csv(C), "correlation.csv": matrix_csv(rho)}
    unreported = sorted(b for box in dp["h2"]["unreported_boxes"] for b in box)
    js = {"schema": "fd-deposit-candidate/1", "labels": LABELS,
          "axes": [{"name": ax, "unit": UNITS[ax], "h2_edges": H2_EDGES[ax]} for ax in AXES],
          "cells": [{**c, "gibuu_subset": gibuu_flag(c)} for c in dp["cells"]],
          "unreported_h2_boxes": [{"h2_box": b, "box": h2_box(b)} for b in unreported],
          "gibuu_subset": [c["cell"] for c in dp["cells"] if gibuu_flag(c)],
          "f": f.tolist(), "covariance": C.tolist(), "correlation": rho.tolist(), "sigma": sigma.tolist(),
          "covariance_of": "C_total_plus_C_resp",
          "files_sha256": {n: hashlib.sha256(t.encode()).hexdigest() for n, t in files.items()},
          "source": {"data_product": "fd/data-product/fd_data_product.json", "sha256": PINS["data_product"]},
          "code_sha256": {"fd_deposit_candidate.py": sha256(Path(__file__).resolve())}}
    files["deposit.json"] = json.dumps(js, indent=1, allow_nan=False) + "\n"
    return files


def check(pkg: Path, dp_path: Path, g_path: Path) -> dict:
    dp = load_pinned(dp_path, "data_product")
    gr = load_pinned(g_path, "g_readout")
    text = {n: (pkg / n).read_text() for n in FILES}
    js = json.loads(text["deposit.json"])
    for n in FILES[:-1]:
        report("P0", f"{n}'s sha256 is deposit.json's", hashlib.sha256(text[n].encode()).hexdigest()
               == js["files_sha256"].get(n))
    report("P0", "deposit.json names the pinned data product", js["source"]["sha256"] == PINS["data_product"])

    # P1: the cells and their boxes
    rows = list(csv.DictReader(io.StringIO(text["cells.csv"])))
    report("P1", "cells.csv and deposit.json list R00-R15 in order", [r["cell"] for r in rows] == CELLS
           and [c["cell"] for c in js["cells"]] == CELLS and [c["cell"] for c in dp["cells"]] == CELLS)
    for i, (r, c, d) in enumerate(zip(rows, js["cells"], dp["cells"])):
        box = {ax: [float(r[f"{ax}_lo"]), float(r[f"{ax}_hi"])] for ax in AXES}
        report("P1", f"{CELLS[i]}'s box and H2 boxes are the data product's", box == d["box"] == c["box"]
               and [int(x) for x in r["h2_boxes"].split()] == d["h2_boxes"] == c["h2_boxes"])
        report("P1", f"{CELLS[i]}'s box is exactly the union of its H2 boxes", boxes_inside(box) == set(d["h2_boxes"]))
    used = [b for d in dp["cells"] for b in d["h2_boxes"]]
    report("P1", "no two cells share an H2 box", len(used) == len(set(used)))
    unrep = [u["h2_box"] for u in js["unreported_h2_boxes"]]
    report("P1", "the unreported boxes are exactly the H2 boxes in no cell, with their bounds",
           sorted(unrep) == sorted(set(range(32)) - set(used))
           == sorted(b for box in dp["h2"]["unreported_boxes"] for b in box)
           and all(u["box"] == h2_box(u["h2_box"]) for u in js["unreported_h2_boxes"]))
    report("P1", "the H2 edges are s5p_stage1_inspect's", H2_EDGES == G.sa.s1.H2_EDGES)

    # P2: every number, bit for bit
    f_dp = np.array(dp["f"], float)
    C_dp = np.array(dp["matrices"]["C_total_plus_C_resp"], float)
    rho_dp = np.array(dp["correlation"], float)
    f_csv = np.array([float(r["f_cm2_per_nucleon"]) for r in rows])
    C_csv, rho_csv = read_matrix_csv(text["covariance.csv"]), read_matrix_csv(text["correlation.csv"])
    report("P2", "f from cells.csv and deposit.json is the data product's, bit for bit",
           np.array_equal(f_csv, f_dp) and np.array_equal(np.array(js["f"]), f_dp))
    report("P2", "the covariance from covariance.csv and deposit.json is the data product's C_total_plus_C_resp, "
           "bit for bit", np.array_equal(C_csv, C_dp) and np.array_equal(np.array(js["covariance"]), C_dp))
    report("P2", "the correlation from correlation.csv and deposit.json is the data product's, bit for bit",
           np.array_equal(rho_csv, rho_dp) and np.array_equal(np.array(js["correlation"]), rho_dp))

    # P3: the covariance and what is derived from it
    C = C_csv
    asym = float(np.abs(C - C.T).max() / np.abs(C).max())   # S1's C_e is symmetric to the last bit only
    report("P3", "the covariance is symmetric to 1e-12 of its largest entry (the data product's Q4 rule)",
           asym <= 1e-12, f"{asym}")
    ev = np.linalg.eigvalsh(C)
    report("P3", "the covariance is positive definite", bool(ev.min() > 0))
    sig = np.sqrt(np.diag(C))
    report("P3", "sigma in cells.csv and deposit.json is sqrt(diag), bit for bit", np.array_equal(
        np.array([float(r["sigma_cm2_per_nucleon"]) for r in rows]), sig) and np.array_equal(np.array(js["sigma"]), sig))
    rho_worst = float(np.abs(C / np.outer(sig, sig) - rho_csv).max())
    report("P3", "the correlation is the covariance's, to 1e-15", rho_worst <= 1e-15, f"{rho_worst}")

    # P4: GiBUU's subset
    gib = [p for p in gr["predictions"] if p["name"] == "gibuu"]
    sub = [r["cell"] for r in rows if r["gibuu_subset"] == "1"]
    report("P4", "GiBUU's subset is Stage G's eight cells and the cells with p_parallel's upper edge 4.5 GeV/c",
           len(gib) == 1 and sub == gib[0]["cells"] == js["gibuu_subset"] == [CELLS[i] for i, d in
                                                                              enumerate(dp["cells"]) if d["box"]["pz"][1] <= 4.5]
           and len(sub) == 8)

    # P5: Stage G's chi2, by Stage G's own compare()
    report("P5", "Stage G's f is the package's, bit for bit", gr["cells"] == CELLS and all(
        np.array_equal(np.array(p["f"]), f_csv[[CELLS.index(c) for c in p["cells"]]]) for p in gr["predictions"]))
    worst, rec = 0.0, []
    for p in gr["predictions"]:
        idx = [CELLS.index(c) for c in p["cells"]]
        g, Vg = np.zeros(N), np.zeros(N)
        g[idx] = p["g"]
        Vg[idx] = (np.array(p["sigma_Vg_over_f"]) * f_csv[idx]) ** 2
        out = G.compare(f_csv, g, Vg, C, idx, "C_total + C_resp")
        for key in ("total", "shape_only"):
            got, want = out[key]["chi2"], p[key]["chi2"]
            rel = abs(got - want) / want
            worst = max(worst, rel)
            rec.append({"prediction": p["name"], "kind": key, "n_cells": len(idx), "ndf": out[key]["ndf"],
                        "chi2_package": got, "chi2_stage_g": want, "rel_diff": rel})
            report("P5", f"{p['name']} {key} chi2 from the package is Stage G's to {CHI2_TOL} relative",
                   rel <= CHI2_TOL and out[key]["ndf"] == p[key]["ndf"], f"{got} vs {want} ({rel})")
    return {"controls_passed": ["P0", "P1", "P2", "P3", "P4", "P5"], "chi2": rec, "chi2_worst_rel_diff": worst,
            "correlation_worst_abs_diff": rho_worst, "covariance_asymmetry_over_max": asym,
            "covariance_eigen_min_max": [float(ev.min()), float(ev.max())]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--data-product", type=Path, required=True)
    b.add_argument("--out-dir", type=Path, required=True)
    c = sub.add_parser("check")
    c.add_argument("--package", type=Path, required=True)
    c.add_argument("--data-product", type=Path, required=True)
    c.add_argument("--g-readout", type=Path, required=True)
    a = ap.parse_args(argv)
    try:
        if a.cmd == "build":
            dp = load_pinned(a.data_product, "data_product")
            report("P0", "no package file exists (no overwrite)", not any((a.out_dir / n).exists() for n in FILES))
            a.out_dir.mkdir(parents=True, exist_ok=True)
            for n, t in package(dp).items():
                out = a.out_dir / n
                tmp = out.with_name(out.name + ".partial")
                tmp.write_text(t)
                os.replace(tmp, out)
                print(json.dumps({"wrote": str(out), "sha256": sha256(out)}), flush=True)
        else:
            print(json.dumps(check(a.package, a.data_product, a.g_readout), indent=1), flush=True)
    except Stop as e:
        print(f"[STOP] {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
