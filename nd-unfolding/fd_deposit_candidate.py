#!/usr/bin/env python3
"""The 5D result's deposit candidate (state/measurement-paper/5d-community-20261024/fd/deposit-candidate/README.md;
DECISION-20261028-joseph-result-table-and-deposit-package.md item 2): the sixteen-cell result's cell definitions,
measured vector, reported covariance C_total + C_resp and its correlation matrix, as CSV and one JSON, written from
the committed data product (fd/data-product/fd_data_product.json) and nothing else; and, apart from the measurement,
predictions-reference.json: the five predictions' g and V_g (V_g recomputed from the sigma_Vg_over_f that Stage G's
readout, fd/readout/fd_g_readout.json, prints), with which the paper's chi2 is reproduced. Whether that file goes into a deposit is Joseph's call at release.

``build`` writes the package; ``check`` re-reads it from disk and refuses (exit 1) unless every control holds:
* P0  the data product and Stage G's readout are the pinned bytes, every file exists, and the CSVs' digests in
      deposit.json hold (the files' bytes, not newline-translated text);
* P1  the cells, their boxes and H2 boxes are the data product's; each cell's box is exactly the union of its H2
      boxes (the boxes inside it are exactly its listed ones, and their bounding box is it); no two cells share an H2
      box; the unreported boxes are exactly the H2 boxes in no cell;
* P2  f, the covariance and the correlation, from every CSV and from the JSON, are the data product's bit for bit;
* P3  the covariance is symmetric to 1e-12 of its largest entry and positive definite; sigma is sqrt(diag); the correlation is the covariance's;
* P4  GiBUU's subset is exactly the eight cells with p_parallel's upper edge at 4.5 GeV/c, and Stage G's eight;
* P5  every Stage G chi2 in fd_g_readout.json (five predictions, total and shape-only) is recomputed by Stage G's own
      compare() from the package files alone (cells.csv's f, covariance.csv, predictions-reference.json's g and V_g),
      to 1e-10 relative; the readout's f is the package's;
* P6  predictions-reference.json is Stage G's readout: the same five predictions in order, each with fd_g_compare's
      source path, sha256 and label, its cells (GiBUU's eight), g and sigma_Vg_over_f bit for bit, V_g =
      (sigma_Vg_over_f f)^2 bit for bit, and Stage G's chi2 and ndf;
* P7  every file is what ``build`` writes from the pinned inputs: the CSVs byte for byte, and every field of
      deposit.json and predictions-reference.json (labels, units, status, domains included), value and JSON type,
      but code_sha256.

A ``Variant`` names the reported matrix the package carries (its data-product key, its name in Stage G's compare(),
the labels, the pins and the source paths). The default is C_total + C_resp, the CLI's only variant; another is passed
in-process to ``run`` (fd_cpl_addition.py's chain), with its pins, and changes nothing else.

``check --measurement-only`` checks the measurement without predictions-reference.json or Stage G's readout:
P0-P3, P4's p_parallel rule and P7 on the four measurement files.

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
from dataclasses import dataclass
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
FILES = ("cells.csv", "covariance.csv", "correlation.csv", "deposit.json")      # the measurement
REFERENCE = "predictions-reference.json"                                       # apart from it
REFERENCE_LABEL = "reference predictions used for the paper's chi2; not part of the measurement"
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
                  "finite-MC variance, ndf n; its shape-only chi2 adds 100 f f^T (f on c, absolute units) to "
                  "C + V_g, ndf n - 1; g and V_g are the prediction's, not part of the measurement",
    "gibuu": "GiBUU is compared on the eight cells with p_parallel < 4.5 GeV/c only (gibuu_subset = 1)",
    "unreported": "the sixteen cells cover 28 of the 32 H2 boxes; the four unreported boxes are listed with their "
                  "bounds and are in no cell",
    "not_citable_for": "coverage; any reading, claim or release text",
}


@dataclass(frozen=True)
class Variant:
    """The reported matrix a package carries: ``key`` in the data product's matrices, ``name`` as Stage G's compare()
    names it, the labels, the pins of the data product and Stage G's readout, and their source paths."""
    key: str
    name: str
    labels: dict
    pins: dict
    sources: dict


DEFAULT = Variant(key="C_total_plus_C_resp", name="C_total + C_resp", labels=LABELS, pins=PINS,
                  sources={"data_product": "fd/data-product/fd_data_product.json",
                           "g_readout": "fd/readout/fd_g_readout.json"})


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


def load_pinned(path: Path, key: str, v: Variant = DEFAULT) -> dict:
    report("P0", f"{key} sha256 is the pin", sha256(path) == v.pins[key], f"{sha256(path)} != {v.pins[key]}")
    return json.loads(path.read_text())


def package(dp: dict, v: Variant = DEFAULT) -> dict[str, str]:
    """The package's files, from the data product alone."""
    f = np.array(dp["f"], float)
    C = np.array(dp["matrices"][v.key], float)
    rho = np.array(dp["correlation"], float)
    sigma = np.sqrt(np.diag(C))
    head = ["cell", "h2_boxes", *[f"{ax}_{e}" for ax in AXES for e in ("lo", "hi")], "gibuu_subset",
            "f_cm2_per_nucleon", "sigma_cm2_per_nucleon"]
    rows = [[c["cell"], " ".join(map(str, c["h2_boxes"])), *[float(v) for ax in AXES for v in c["box"][ax]],
             gibuu_flag(c), float(f[i]), float(sigma[i])] for i, c in enumerate(dp["cells"])]
    files = {"cells.csv": csv_text(head, rows), "covariance.csv": matrix_csv(C), "correlation.csv": matrix_csv(rho)}
    unreported = sorted(b for box in dp["h2"]["unreported_boxes"] for b in box)
    js = {"schema": "fd-deposit-candidate/1", "labels": v.labels,
          "axes": [{"name": ax, "unit": UNITS[ax], "h2_edges": H2_EDGES[ax]} for ax in AXES],
          "cells": [{**c, "gibuu_subset": gibuu_flag(c)} for c in dp["cells"]],
          "unreported_h2_boxes": [{"h2_box": b, "box": h2_box(b)} for b in unreported],
          "gibuu_subset": [c["cell"] for c in dp["cells"] if gibuu_flag(c)],
          "f": f.tolist(), "covariance": C.tolist(), "correlation": rho.tolist(), "sigma": sigma.tolist(),
          "covariance_of": v.key,
          "files_sha256": {n: hashlib.sha256(t.encode()).hexdigest() for n, t in files.items()},
          "source": {"data_product": v.sources["data_product"], "sha256": v.pins["data_product"]},
          "code_sha256": {"fd_deposit_candidate.py": sha256(Path(__file__).resolve())}}
    files["deposit.json"] = json.dumps(js, indent=1, allow_nan=False) + "\n"
    return files


def reference(gr: dict, f: np.ndarray, v: Variant = DEFAULT) -> str:
    """predictions-reference.json, from Stage G's readout: g, sigma_Vg_over_f and V_g = (sigma_Vg_over_f f)^2 on each
    prediction's own cells, with its source and Stage G's chi2."""
    preds = []
    for p in gr["predictions"]:
        idx = [CELLS.index(c) for c in p["cells"]]
        Vg = (np.array(p["sigma_Vg_over_f"], float) * f[idx]) ** 2
        preds.append({"name": p["name"], "label": p["label"], "source": p["file"], "source_sha256": p["sha256"],
                      "cells": p["cells"], "domain": "GiBUU's eight cells, p_parallel < 4.5 GeV/c" if p["name"]
                      == "gibuu" else "all sixteen cells", "g_cm2_per_nucleon": p["g"],
                      "sigma_Vg_over_f": p["sigma_Vg_over_f"], "V_g_cm4_per_nucleon2": Vg.tolist(),
                      "stage_g": {k: {"chi2": p[k]["chi2"], "ndf": p[k]["ndf"], "matrix": p[k]["matrix"]}
                                  for k in ("total", "shape_only")}})
    js = {"schema": "fd-deposit-candidate-predictions/1", "label": REFERENCE_LABEL, "status": STATUS,
          "release": "whether this file goes into a deposit is Joseph's call at release, separately from the "
                     "measurement",
          "use": "chi2 = d^T (C[c,c] + diag(V_g))^-1 d, d = f - g on the prediction's cells c (fd_g_compare.compare); "
                 "shape-only adds 100 f f^T on c, ndf n - 1; V_g = (sigma_Vg_over_f f)^2, recomputed from the "
                 "sigma_Vg_over_f that Stage G's readout prints, with which every Stage G chi2 is reproduced",
          "predictions": preds,
          "source": {"g_readout": v.sources["g_readout"], "sha256": v.pins["g_readout"]},
          "code_sha256": {"fd_deposit_candidate.py": sha256(Path(__file__).resolve())}}
    return json.dumps(js, indent=1, allow_nan=False) + "\n"


def bounding_box(boxes: list) -> dict:
    return {ax: [min(h2_box(b)[ax][0] for b in boxes), max(h2_box(b)[ax][1] for b in boxes)] for ax in AXES}


def without_code(text: str) -> str:
    """The JSON without code_sha256, canonically serialized: types are kept (1, 1.0 and true differ)."""
    js = json.loads(text)
    js.pop("code_sha256", None)
    return json.dumps(js, sort_keys=True, allow_nan=False)


def check(pkg: Path, dp_path: Path, g_path: Path | None, v: Variant = DEFAULT) -> dict:
    """Every control; with ``g_path`` None (``--measurement-only``), the measurement's alone."""
    dp = load_pinned(dp_path, "data_product", v)
    gr = None if g_path is None else load_pinned(g_path, "g_readout", v)
    names = FILES if gr is None else (*FILES, REFERENCE)
    for n in names:
        report("P0", f"{n} exists", (pkg / n).is_file())
    text = {n: (pkg / n).read_bytes().decode() for n in names}   # the bytes: read_text() would translate newlines
    js = json.loads(text["deposit.json"])
    for n in FILES[:-1]:
        report("P0", f"{n}'s sha256 is deposit.json's", hashlib.sha256(text[n].encode()).hexdigest()
               == js["files_sha256"].get(n))
    report("P0", "deposit.json names the pinned data product", js["source"]["sha256"] == v.pins["data_product"])

    # P1: the cells and their boxes
    rows = list(csv.DictReader(io.StringIO(text["cells.csv"])))
    report("P1", "cells.csv and deposit.json list R00-R15 in order", [r["cell"] for r in rows] == CELLS
           and [c["cell"] for c in js["cells"]] == CELLS and [c["cell"] for c in dp["cells"]] == CELLS)
    for i, (r, c, d) in enumerate(zip(rows, js["cells"], dp["cells"])):
        box = {ax: [float(r[f"{ax}_lo"]), float(r[f"{ax}_hi"])] for ax in AXES}
        report("P1", f"{CELLS[i]}'s box and H2 boxes are the data product's", box == d["box"] == c["box"]
               and [int(x) for x in r["h2_boxes"].split()] == d["h2_boxes"] == c["h2_boxes"])
        report("P1", f"{CELLS[i]}'s box is exactly the union of its H2 boxes", boxes_inside(box) == set(d["h2_boxes"])
               and bounding_box(d["h2_boxes"]) == box)
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
    C_dp = np.array(dp["matrices"][v.key], float)
    rho_dp = np.array(dp["correlation"], float)
    f_csv = np.array([float(r["f_cm2_per_nucleon"]) for r in rows])
    C_csv, rho_csv = read_matrix_csv(text["covariance.csv"]), read_matrix_csv(text["correlation.csv"])
    report("P2", "f from cells.csv and deposit.json is the data product's, bit for bit",
           np.array_equal(f_csv, f_dp) and np.array_equal(np.array(js["f"]), f_dp))
    report("P2", f"the covariance from covariance.csv and deposit.json is the data product's {v.key}, "
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
    sub = [r["cell"] for r in rows if r["gibuu_subset"] == "1"]
    report("P4", "GiBUU's subset is the eight cells with p_parallel's upper edge 4.5 GeV/c", len(sub) == 8
           and sub == js["gibuu_subset"] == [CELLS[i] for i, d in enumerate(dp["cells"]) if d["box"]["pz"][1] <= 4.5])
    summary = {"controls_passed": ["P0", "P1", "P2", "P3", "P4", "P7"], "correlation_worst_abs_diff": rho_worst,
           "covariance_asymmetry_over_max": asym, "covariance_eigen_min_max": [float(ev.min()), float(ev.max())]}
    if gr is None:
        check_as_built(text, package(dp, v), FILES)
        return {**summary, "mode": "measurement only: predictions-reference.json and Stage G's readout not read"}
    gib = [p for p in gr["predictions"] if p["name"] == "gibuu"]
    report("P4", "GiBUU's subset is Stage G's eight cells", len(gib) == 1 and sub == gib[0]["cells"])

    # P6: the reference predictions are Stage G's
    ref = json.loads(text[REFERENCE])
    rp = ref["predictions"]
    spec = {s["name"]: s for s in G.PREDICTIONS}
    report("P6", "predictions-reference.json is labelled apart from the measurement and names the pinned readout",
           ref["label"] == REFERENCE_LABEL and ref["source"]["sha256"] == v.pins["g_readout"])
    report("P6", "it holds Stage G's five predictions, in order", [p["name"] for p in rp]
           == [p["name"] for p in gr["predictions"]] == [s["name"] for s in G.PREDICTIONS])
    for r, p in zip(rp, gr["predictions"]):
        idx = [CELLS.index(c) for c in p["cells"]]
        report("P6", f"{r['name']}: source, sha256 and label are fd_g_compare's and the readout's",
               (r["source"], r["source_sha256"], r["label"]) == (p["file"], p["sha256"], p["label"])
               == (spec[r["name"]]["path"], spec[r["name"]]["sha256"], p["label"]))
        report("P6", f"{r['name']}: cells, g and sigma_Vg_over_f are the readout's, bit for bit",
               r["cells"] == p["cells"] and np.array_equal(np.array(r["g_cm2_per_nucleon"]), np.array(p["g"]))
               and np.array_equal(np.array(r["sigma_Vg_over_f"]), np.array(p["sigma_Vg_over_f"])))
        report("P6", f"{r['name']}: V_g is (sigma_Vg_over_f f)^2 with the package's f, bit for bit", np.array_equal(
            np.array(r["V_g_cm4_per_nucleon2"]), (np.array(p["sigma_Vg_over_f"]) * f_csv[idx]) ** 2))
        report("P6", f"{r['name']}: Stage G's chi2 and ndf are the readout's", all(
            r["stage_g"][k]["chi2"] == p[k]["chi2"] and r["stage_g"][k]["ndf"] == p[k]["ndf"]
            for k in ("total", "shape_only")))
    report("P6", "GiBUU's domain is the package's GiBUU subset", next(r for r in rp if r["name"] == "gibuu")["cells"]
           == sub)

    # P5: Stage G's chi2, by Stage G's own compare(), from the package files alone
    report("P5", "Stage G's f is the package's, bit for bit", gr["cells"] == CELLS and all(
        np.array_equal(np.array(p["f"]), f_csv[[CELLS.index(c) for c in p["cells"]]]) for p in gr["predictions"]))
    worst, rec = 0.0, []
    for r, p in zip(rp, gr["predictions"]):
        idx = [CELLS.index(c) for c in r["cells"]]
        g, Vg = np.zeros(N), np.zeros(N)
        g[idx] = r["g_cm2_per_nucleon"]
        Vg[idx] = r["V_g_cm4_per_nucleon2"]
        out = G.compare(f_csv, g, Vg, C, idx, v.name)
        for key in ("total", "shape_only"):
            got, want = out[key]["chi2"], p[key]["chi2"]
            rel = abs(got - want) / want
            worst = max(worst, rel)
            rec.append({"prediction": p["name"], "kind": key, "n_cells": len(idx), "ndf": out[key]["ndf"],
                        "chi2_package": got, "chi2_stage_g": want, "rel_diff": rel})
            report("P5", f"{p['name']} {key} chi2 from the package is Stage G's to {CHI2_TOL} relative",
                   rel <= CHI2_TOL and out[key]["ndf"] == p[key]["ndf"], f"{got} vs {want} ({rel})")
    built = package(dp, v)
    built[REFERENCE] = reference(gr, f_dp, v)
    check_as_built(text, built, names)
    return {**summary, "controls_passed": ["P0", "P1", "P2", "P3", "P4", "P6", "P5", "P7"], "chi2": rec,
            "chi2_worst_rel_diff": worst}


def check_as_built(text: dict, built: dict, names) -> None:
    """P7: each file is what build writes from the pinned inputs; the JSONs field by field, but code_sha256."""
    for n in names:
        if n.endswith(".csv"):
            report("P7", f"{n} is what build writes, byte for byte", text[n] == built[n])
        else:
            report("P7", f"every field of {n} (but code_sha256) is what build writes",
                   without_code(text[n]) == without_code(built[n]))


def build_args(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--data-product", type=Path, required=True)
    b.add_argument("--g-readout", type=Path, required=True)
    b.add_argument("--out-dir", type=Path, required=True)
    c = sub.add_parser("check")
    c.add_argument("--package", type=Path, required=True)
    c.add_argument("--data-product", type=Path, required=True)
    g = c.add_mutually_exclusive_group(required=True)
    g.add_argument("--g-readout", type=Path)
    g.add_argument("--measurement-only", action="store_true",
                   help="check the measurement alone, without predictions-reference.json or Stage G's readout")
    return ap.parse_args(argv)


def run(a, pins=None, variant: Variant | None = None) -> int:
    """``build`` or ``check``; ``variant`` (with its own pins) is passed in-process only, ``pins`` replaces its pins."""
    v = DEFAULT if variant is None else variant
    if pins is not None:
        v = Variant(key=v.key, name=v.name, labels=v.labels, pins=pins, sources=v.sources)
    try:
        if a.cmd == "build":
            dp = load_pinned(a.data_product, "data_product", v)
            gr = load_pinned(a.g_readout, "g_readout", v)
            report("P0", "no package file exists (no overwrite)", not any((a.out_dir / n).exists()
                                                                          for n in (*FILES, REFERENCE)))
            a.out_dir.mkdir(parents=True, exist_ok=True)
            files = package(dp, v)
            files[REFERENCE] = reference(gr, np.array(dp["f"], float), v)
            for n, t in files.items():
                out = a.out_dir / n
                tmp = out.with_name(out.name + ".partial")
                tmp.write_text(t)
                os.replace(tmp, out)
                print(json.dumps({"wrote": str(out), "sha256": sha256(out)}), flush=True)
        else:
            print(json.dumps(check(a.package, a.data_product, a.g_readout, v), indent=1), flush=True)
    except Stop as e:
        print(f"[STOP] {e}", file=sys.stderr)
        return 1
    return 0


def main(argv=None) -> int:
    return run(build_args(argv))


if __name__ == "__main__":
    sys.exit(main())
