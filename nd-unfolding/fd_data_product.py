#!/usr/bin/env python3
"""The 5D data product (state/measurement-paper/5d-community-20261024/FD-DATA-PRODUCT-DECLARATION.md): the 5D
result's reported covariance on R00-R15, written to git as a JSON readout and one CSV per matrix, for the 5D
integration (DECISION-20261027-joseph-5d-integration-then-second-scope-review.md item 2).

From S1's assembly (s1_assembly.npz) and C_resp's (cresp.npz), both pinned by digest:
* the cells R00-R15 and their boxes, from the H2 definition;
* f, S1's cell integrals;
* C_e, C_model_abs and C_resp, and the reported C_total + C_resp = C_e + C_model_abs + C_resp
  (DECISION-20261026-joseph-adopt-cresp.md), in S1's absolute units;
* the correlation matrix of C_total + C_resp;
* the per-cell relative sigma, sqrt(diag)/f, of each of the four.

Controls Q0-Q6 each refuse (exit 1, nothing written): the digests and their chain (Q0); the shapes (Q1); the sum
C_total + C_resp = C_e + C_model_abs + C_resp, and cresp.npz's C_total_resp (Q2); every
relative sigma against S1's, C_resp's and Stage G's committed readouts (Q3); symmetry, positive definiteness of the
reported matrix and semidefiniteness of its parts (Q4); the correlation (Q5); and every written number read back from
its CSV (Q6).

MEASURES: nothing; a copy of committed results' inputs into git, with sqrt(diag)/f and the correlation for display.
CANNOT AUTHORIZE: a release, supplemental material, a reading, a claim or paper text. NOT CITABLE FOR coverage.
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
import fd_g_compare as G  # noqa: E402  (Stop, report)
import s1_assemble as sa  # noqa: E402  (sha256, s1.AXES)

N = 16
TOL = 1e-12
INPUTS = ("s1_npz", "s1_json", "cresp_npz", "cresp_json", "cresp_report", "g_readout", "definition", "stage1")
PINS = {
    "s1_npz": "db000707780d4d6da65389be9adedfd9a3ba6552a255f6ce81ccbdd0b8eb72a4",
    "s1_json": "81e5ef3fe8e7b055360dc43b8a8240c9b5c39c8aa6e7c507b3211d305b326b21",
    "cresp_npz": "4d8b579732b79cbbb8e6c9a4f6335c4bda4eae6dd4194241a0d8cd6e7ea8a20a",
    "cresp_json": "19bb2ee12827207fa346242ac901af48f6c80785eff5a14ff54133dff1ea01f0",
    "cresp_report": "f41e5f0c607ecf1499b576d89688249a6bc025ca3ed29803b29a1a9dcd95d5a2",
    "g_readout": "75a9ddee19a7affe7e3bc10bf0cba8e5ebaa71132686e5ae116f1454d7bafcee",
    "definition": "b67907615fe2e903e60ae6caa1c141fa007676c0a1b3ae9f42490d331bfdda89",
    "stage1": "def4c67cfb59f5ae917f86d2745416b172be6aca3764eba11f3d116db4621d9d",
}
SCHEMAS = {"s1_json": "s1-readout/1", "cresp_json": "cresp-readout/1", "g_readout": "fd-g-readout/2",
           "definition": "h2-definition/1", "stage1": "s5p-stage1-inspect/1"}
N_H2 = 32
REPORTED = "C_total_plus_C_resp"
# each matrix written, and where its committed relative sigma is (Q3)
MATRICES = (("C_e", (("s1_json", "C_e"),)),
            ("C_model_abs", (("s1_json", "C_model"),)),
            ("C_resp", (("cresp_json", "C_resp"),)),
            (REPORTED, (("cresp_json", "C_total_resp"), ("g_readout", "sigma_total_over_f"))))
STEM = "fd_data_product"
LABELS = {
    "what": "data product: the 5D result's reported covariance",
    "covariance": "C_total + C_resp = C_e + C_model_abs + C_resp, the data's reported covariance (Stage G's "
                  "reported_covariance; DECISION-20261026-joseph-adopt-cresp.md), from S1's assembly and C_resp's, in "
                  "S1's absolute units. Stage G's chi2 is against C_total + C_resp + V_g, which adds each prediction's "
                  "own finite-MC variance V_g (Stage G's sigma_Vg_over_f); V_g is not in this product",
    "units": "f: each cell's integral sum_f xsec_flat_f * vol_f in cm^2/nucleon (S1's meta.integral); each matrix in "
             "(cm^2/nucleon)^2; relative sigma: sqrt(diag)/f; box edges as in the H2 definition, whose largest edges "
             "(4.5 for p_T, 60 for p_parallel, 100 for E_avail, q3 and W) are the analysis grid's outer edges",
    "not_citable_for": "coverage",
    "limitation": "the fake-data study of this estimator, graded against C_total + C_resp, is "
                  "state/measurement-paper/5d-community-20261024/FD-F0b-REPORT.md, whose grades travel with this "
                  "product; the limitation's wording is Joseph's (state/2d-closeout/stageF/methods/5d-fd-presentation/"
                  "DRAFT.md)",
    "not": "no reading, claim or release text; whether it ships as supplemental material is Joseph's",
}


def report(control, name, ok, why="differs"):
    G.report(control, name, ok, why)


def worst(a, b) -> float:
    a, b = np.asarray(a, float), np.asarray(b, float)
    if a.shape != b.shape or not (np.all(np.isfinite(a)) and np.all(np.isfinite(b))):
        return float("inf")
    den = np.maximum(np.abs(a), np.abs(b))
    return float(np.max(np.where(a == b, 0.0, np.abs(a - b) / np.where(den > 0, den, 1.0)), initial=0.0))


def load(a, pins: dict) -> dict:
    """Q0: the digests, the schemas and the chain between the products and their readouts."""
    for k in INPUTS:
        got = sa.sha256(getattr(a, k))
        report("Q0", f"{k} sha256 is the pin", got == pins[k], f"{got} != {pins[k]}")
    r = {k: json.loads(getattr(a, k).read_text()) for k in INPUTS if not k.endswith(("_npz", "_report"))}
    r["cresp_report"] = report_table(a.cresp_report.read_text())
    for k, s in SCHEMAS.items():
        report("Q0", f"{k} schema is {s}", r[k].get("schema") == s, repr(r[k].get("schema")))
    report("Q0", "S1's readout names this S1 assembly, of schema s1-assembly/1",
           r["s1_json"]["assembly_sha256"] == pins["s1_npz"] and r["s1_json"]["meta"]["schema"] == "s1-assembly/1")
    cm = r["cresp_json"]["meta"]["inputs_sha256"]
    report("Q0", "C_resp's readout names this C_resp, built on this S1 assembly and definition",
           r["cresp_json"]["assembly_sha256"] == pins["cresp_npz"] and cm["s1_assembly"] == pins["s1_npz"]
           and cm["definition"] == pins["definition"])
    g = r["g_readout"]
    report("Q0", "the definition was checked against this Stage-1 receipt",
           r["definition"]["inputs"]["stage1_inspect_sha256"] == pins["stage1"])
    report("Q0", "Stage G ran on this S1 assembly, definition and C_resp, adopted",
           g["inputs_sha256"]["s1_npz"] == pins["s1_npz"] and g["inputs_sha256"]["definition"] == pins["definition"]
           and g["extra_block"]["sha256"] == pins["cresp_npz"] and g["extra_block"]["role"] == "adopted")
    with np.load(a.s1_npz, allow_pickle=False) as z:
        r["s1"] = {k: np.asarray(z[k], float) for k in ("f", "C_e", "C_model_abs", "C_total")}
    with np.load(a.cresp_npz, allow_pickle=False) as z:
        r["cresp"] = {k: np.asarray(z[k], float) for k in ("C_resp", "C_total_resp")}
    return r


def build(r: dict) -> dict:
    s1, cr, defn = r["s1"], r["cresp"], r["definition"]
    f = s1["f"]
    shapes = {k: v.shape for k, v in {**s1, **cr}.items()}
    report("Q1", "f is 16 cells and every matrix 16 x 16, finite", shapes == {
        "f": (N,), "C_e": (N, N), "C_model_abs": (N, N), "C_total": (N, N), "C_resp": (N, N), "C_total_resp": (N, N)}
        and all(np.all(np.isfinite(v)) for v in {**s1, **cr}.values()), f"{shapes}")
    report("Q1", "f is positive on every cell", bool(np.all(f > 0)))
    cells = [c for c in defn["reporting_cells"] if c.get("reported", True)]
    report("Q1", "the definition reports R00-R15, in order", [c["id"] for c in cells] == list(range(N))
           and r["s1_json"]["cells"] == r["cresp_json"]["cells"] == r["g_readout"]["cells"]
           == [f"R{i:02d}" for i in range(N)])
    h2 = h2_relation(defn, r["stage1"]["mc"]["H2"])
    report("Q1", "the H2 boxes: Stage 1's supported boxes, the definition's cells and its unreported boxes agree",
           h2["consistent"])
    Ce, Cm, Ct, Cx = s1["C_e"], s1["C_model_abs"], s1["C_total"], cr["C_resp"]
    M = Ct + Cx
    scale = float(np.abs(np.diag(M)).max())
    report("Q2", "C_total + C_resp is the sum of its parts, C_e + C_model_abs + C_resp",
           float(np.abs(Ce + Cm + Cx - M).max()) <= TOL * scale)
    report("Q2", "C_total + C_resp is cresp.npz's C_total_resp", float(np.abs(cr["C_total_resp"] - M).max())
           <= TOL * scale)
    mats = {"C_e": Ce, "C_model_abs": Cm, "C_resp": Cx, REPORTED: M}
    sig = {k: np.sqrt(np.clip(np.diag(v), 0, None)) / f for k, v in mats.items()}
    gp = r["g_readout"]["predictions"][0]
    committed = {"s1_json": r["s1_json"]["relative_sigma"], "cresp_json": r["cresp_json"]["relative_sigma"],
                 "g_readout": {"sigma_total_over_f": gp["sigma_total_over_f"]}}
    for name, refs in MATRICES:
        for src, key in refs:
            report("Q3", f"{name}'s relative sigma is {src}'s {key}", worst(sig[name], committed[src][key]) <= TOL)
    report("Q3", "C_total's relative sigma is S1's and C_resp's readouts'", worst(
        np.sqrt(np.diag(Ct)) / f, r["s1_json"]["relative_sigma"]["C_total"]) <= TOL and worst(
        np.sqrt(np.diag(Ct)) / f, r["cresp_json"]["relative_sigma"]["C_total"]) <= TOL)
    report("Q3", "f is Stage G's", gp["cells"] == r["g_readout"]["cells"] and worst(f, gp["f"]) <= TOL)
    rt = r["cresp_report"]
    ours = {"C_resp": sig["C_resp"], "C_total": np.sqrt(np.diag(Ct)) / f, "C_total_resp": sig[REPORTED]}
    report("Q3", "C_resp's, C_total's and C_total + C_resp's relative sigma are CRESP-REPORT.md's table, to its 2 dp",
           bool(rt) and rt["cells"] == [f"R{i:02d}" for i in range(N)] and all(
               float(np.abs(100 * ours[c] - np.array(rt[c])).max()) <= 0.005 + 1e-9 for c in REPORT_COLUMNS))
    spec = {k: np.linalg.eigvalsh(v) for k, v in (("C_e", Ce), ("C_total", Ct), ("C_resp", Cx),
                                                               ("C_total_resp", M))}
    se, ce = r["s1_json"]["eigen"], r["cresp_json"]["eigen"]
    report("Q3", "the spectra's extremes are S1's and C_resp's committed ones (off the diagonal too), to 1e-9", all(
        worst(got, want) <= 1e-9 for got, want in (
            ([spec["C_e"].min(), spec["C_e"].max()], [se["C_e"]["min"], se["C_e"]["max"]]),
            ([spec["C_total"].min(), spec["C_total"].max()], [se["C_total"]["min"], se["C_total"]["max"]]),
            ([spec["C_total"].min(), spec["C_total"].max()], [ce["C_total"]["min"], ce["C_total"]["max"]]),
            ([spec["C_total_resp"].min(), spec["C_total_resp"].max()],
             [ce["C_total_resp"]["min"], ce["C_total_resp"]["max"]]),
            ([spec["C_resp"].max()], [ce["C_resp"]["max"]]))))
    for name, C in mats.items():
        report("Q4", f"{name} is symmetric", float(np.abs(C - C.T).max()) <= TOL * scale)
    rel = {k: v / np.outer(f, f) for k, v in mats.items()}
    ev = {k: np.linalg.eigvalsh((v + v.T) / 2) for k, v in rel.items()}
    report("Q4", "C_total + C_resp is positive definite", bool(ev[REPORTED].min() > 0))
    for name in ("C_e", "C_model_abs", "C_resp"):
        report("Q4", f"{name} is positive semidefinite", bool(ev[name].min() >= -TOL * np.abs(ev[name]).max()))
    rho = correlation(M)
    d = np.sqrt(np.diag(M))
    report("Q5", "the correlation is C_total + C_resp's (rho_ij sqrt(M_ii M_jj) = M_ij), symmetric, within [-1, 1], "
                 "with a unit diagonal", float(np.abs(rho * np.outer(d, d) - M).max()) <= TOL * scale
           and float(np.abs(rho - rho.T).max()) <= TOL and float(np.abs(rho).max()) <= 1 + TOL
           and float(np.abs(np.diag(rho) - 1).max()) <= TOL)
    boxes = [{"cell": f"R{c['id']:02d}", "h2_boxes": list(c["h2_cells"]), "box": c["box"]} for c in cells]
    return {"cells": boxes, "h2": h2, "f": f, "matrices": mats, "correlation": rho, "relative_sigma": sig}


REPORT_COLUMNS = ("C_resp", "C_total", "C_total_resp")


def report_table(text: str) -> dict:
    """CRESP-REPORT.md's per-cell table (section 2): each cell's relative sigma in %, to 2 dp, by column name."""
    rows = [ln.split("|")[1:-1] for ln in text.splitlines() if ln.startswith("| R") and ln[3:5].isdigit()]
    head = next((ln.split("|")[1:-1] for ln in text.splitlines() if ln.startswith("| cell |")), [])
    head = [h.strip() for h in head]
    if len(rows) != N or not all(c in head for c in REPORT_COLUMNS):
        return {}
    return {"cells": [r[0].strip() for r in rows], **{c: [float(r[head.index(c)]) for r in rows]
                                                       for c in REPORT_COLUMNS}}


def h2_relation(defn: dict, st1: dict) -> dict:
    """How the 32 H2 boxes, Stage 1's supported ones (the note's 27 H2 cells) and the 16 reporting cells relate."""
    m = defn["h2_to_reporting_cell"]
    unsupported = [i for i, x in enumerate(st1["reported"]) if not x]
    in_cells = [i for i, x in enumerate(m) if x >= 0]
    unreported = sorted(b for box in defn["unreported_boxes"] for b in box)
    absorbed = {i: f"R{m[i]:02d}" for i in unsupported if m[i] >= 0}
    by_cell = {f"R{c['id']:02d}": sorted(c["h2_cells"]) for c in defn["reporting_cells"]}
    consistent = (len(m) == st1["n_cells"] == N_H2 and st1["n_reported"] == N_H2 - len(unsupported)
                  and sorted(set(range(N_H2)) - set(in_cells)) == unreported and set(unreported) <= set(unsupported)
                  and sorted(b for bs in by_cell.values() for b in bs) == in_cells
                  and all(m[b] == int(c[1:]) for c, bs in by_cell.items() for b in bs))
    text = (f"R00-R15 are the definition's {len(by_cell)} reporting cells: the {N_H2} H2 boxes "
            f"(s5p_stage1_inspect.H2_EDGES) after its purity merges (steps, tau {defn['tau']:g}). Stage 1 "
            f"(state/s5p/stage1/stage1_inspect.json mc.H2) supports {st1['n_reported']} of the {N_H2} boxes before "
            f"merging (the note's {st1['n_reported']} supported H2 cells); its unsupported boxes are "
            f"{', '.join(map(str, unsupported))}. {len(in_cells)} boxes enter the {len(by_cell)} cells; the "
            f"definition's unreported boxes are {', '.join(map(str, unreported))}"
            + "".join(f"; box {b}, unsupported alone, enters {c} ({', '.join(map(str, by_cell[c]))}) by the merges"
                      for b, c in absorbed.items()))
    return {"consistent": bool(consistent), "unsupported_stage1": unsupported, "in_cells": in_cells,
            "unreported_boxes": defn["unreported_boxes"], "absorbed": absorbed,
            "h2_to_reporting_cell": m, "label": text}


def correlation(M: np.ndarray) -> np.ndarray:
    d = np.sqrt(np.diag(M))
    return M / np.outer(d, d)


def csv_text(header: list, rows: list) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    for row in rows:
        w.writerow([repr(float(x)) if isinstance(x, (float, np.floating)) else x for x in row])
    return buf.getvalue()


def matrix_csv(C: np.ndarray) -> str:
    names = [f"R{i:02d}" for i in range(N)]
    return csv_text(["cell", *names], [[names[i], *C[i]] for i in range(N)])


def cells_csv(p: dict) -> str:
    axes = sa.s1.AXES
    head = ["cell", *[f"{ax}_{e}" for ax in axes for e in ("lo", "hi")], "f",
            *[f"rel_sigma_{name}" for name, _ in MATRICES]]
    rows = [[c["cell"], *[float(v) for ax in axes for v in c["box"][ax]], float(p["f"][i]),
             *[float(p["relative_sigma"][name][i]) for name, _ in MATRICES]] for i, c in enumerate(p["cells"])]
    return csv_text(head, rows)


def read_matrix_csv(text: str) -> np.ndarray:
    rows = list(csv.reader(io.StringIO(text)))
    names = [f"R{i:02d}" for i in range(N)]
    if rows[0] != ["cell", *names] or [r[0] for r in rows[1:]] != names:
        return np.full((N, N), np.nan)
    return np.array([[float(x) for x in r[1:]] for r in rows[1:]])


def outputs(p: dict) -> dict[str, str]:
    files = {f"{STEM}_cells.csv": cells_csv(p)}
    for name in p["matrices"]:
        files[f"{STEM}_{name}.csv"] = matrix_csv(p["matrices"][name])
    files[f"{STEM}_corr_{REPORTED}.csv"] = matrix_csv(p["correlation"])
    return files


def check_readback(p: dict, files: dict, readout: dict) -> None:
    """Q6: every number written reads back, from its CSV and from the JSON, bit for bit."""
    for name, C in [*p["matrices"].items(), (f"corr_{REPORTED}", p["correlation"])]:
        back = read_matrix_csv(files[f"{STEM}_{name}.csv"])
        js = np.array(readout["matrices"][name] if not name.startswith("corr_") else readout["correlation"], float)
        report("Q6", f"{name}: the CSV and the JSON read back bit for bit", np.array_equal(back, C)
               and np.array_equal(js, C))
    rows = list(csv.reader(io.StringIO(files[f"{STEM}_cells.csv"])))
    back_f = np.array([float(r[11]) for r in rows[1:]])
    back_s = {name: np.array([float(r[12 + j]) for r in rows[1:]]) for j, (name, _) in enumerate(MATRICES)}
    report("Q6", "the cells CSV reads back f and every relative sigma bit for bit", np.array_equal(back_f, p["f"])
           and all(np.array_equal(back_s[k], p["relative_sigma"][k]) for k in back_s)
           and np.array_equal(np.array(readout["f"]), p["f"]))


def build_args(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    for k in INPUTS:
        ap.add_argument("--" + k.replace("_", "-"), dest=k, type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    return ap.parse_args(argv)


def run(a, pins=None) -> int:
    pins = PINS if pins is None else pins
    names = [f"{STEM}.json", f"{STEM}_cells.csv", *[f"{STEM}_{n}.csv" for n, _ in MATRICES],
             f"{STEM}_corr_{REPORTED}.csv"]
    report("Q0", "no output exists (no overwrite)", not any((a.out_dir / n).exists() for n in names))
    r = load(a, pins)
    p = build(r)
    files = outputs(p)
    code = {k: sa.sha256(v) for k, v in (("fd_data_product.py", Path(__file__).resolve()),
                                         ("fd_g_compare.py", Path(G.__file__).resolve()),
                                         ("s1_assemble.py", Path(sa.__file__).resolve()),
                                         ("s5p_stage1_inspect.py", Path(sa.s1.__file__).resolve()))}
    readout = {"schema": "fd-data-product/1", "labels": {**LABELS, "cells": p["h2"]["label"]},
               "controls_passed": ["Q0", "Q1", "Q2", "Q3", "Q4", "Q5", "Q6"],
               "cells": p["cells"], "h2": {k: v for k, v in p["h2"].items() if k not in ("label", "consistent")},
               "f": p["f"].tolist(),
               "matrices": {k: v.tolist() for k, v in p["matrices"].items()},
               "correlation": p["correlation"].tolist(), "correlation_of": REPORTED,
               "relative_sigma": {k: v.tolist() for k, v in p["relative_sigma"].items()},
               "files_sha256": {n: hashlib.sha256(t.encode()).hexdigest() for n, t in files.items()},
               "inputs_sha256": {k: pins[k] for k in INPUTS}, "code_sha256": code, "argv": list(sys.argv)}
    check_readback(p, files, json.loads(json.dumps(readout, allow_nan=False)))
    a.out_dir.mkdir(parents=True, exist_ok=True)
    files[f"{STEM}.json"] = json.dumps(readout, indent=1, allow_nan=False) + "\n"
    for n, text in files.items():
        out = a.out_dir / n
        tmp = out.with_name(out.name + ".partial")
        tmp.write_text(text)
        os.replace(tmp, out)
        print(json.dumps({"wrote": str(out), "sha256": sa.sha256(out)}), flush=True)
    return 0


def main(argv=None) -> int:
    return run(build_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
