#!/usr/bin/env python3
"""V_F's adoption into the 16-cell reported covariance (state/measurement-paper/5d-community-20261024/
FD-VF-ADDITION-DECLARATION.md; DECISION-20261125 section 3): dF = V_F - C_e added to every matrix that carries C_e,
so the reported covariance becomes C_rep,F = V_F + C_model_abs + C_resp + C_PL5D = C_rep + dF, and the arm without
the run-period block C_total + C_resp + dF.

V_F = L C_e L^T is B5D's fluctuation block (blocks5d-20261124/record/V_F.csv), built on the with-block data product's
C_e. The bound tools take one extra block under any key and name; this module writes the blocks and drives them.

Subcommands:
* ``block``    vf_block.npz and vf_block.json from committed files only: dF, the three extra blocks dF (F0, graded
               against C_total), C_resp + dF (without C_PL5D) and C_resp + C_PL5D + dF (reported), and the two revised
               matrices (controls V0-V4);
* ``product``  the V_F data product, from the committed with-block data product and vf_block.npz (controls K0-K6);
* ``table``    every numeric leaf of each V_F readout beside its OLD one (control T);
* ``chain``    Phase 1 (the declaration's section 3): the OLD arms, each output compared with its pinned file
               (control R), and only then the V_F arms, the product, the deposit candidate and the table.

``product`` and ``table`` take the chain's pins in-process (``run(a, pins)``); their CLI refuses without them.
MEASURES: nothing but the arithmetic above. CANNOT AUTHORIZE: a write over a committed product, the paper or the
note, a reading or a claim. NOT CITABLE FOR a validated size of V_F (A1 section 4: the factor measures the toy spread
relative to LL5D's rebuilt reference block) or a coverage statement.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import fd_cpl_addition as A  # noqa: E402  (npz_bytes, load_npz, write_atomic, compare_*, Chain, Paths, step_argv, extra)
import fd_data_product as F  # noqa: E402  (read_matrix_csv, csv_text, matrix_csv, correlation, worst)
import fd_deposit_candidate as DC  # noqa: E402  (Variant, LABELS, FILES, REFERENCE, without_code)

N, CELLS, TOL = A.N, A.CELLS, A.TOL
FD = A.FD
B5D = "docs/orchestration/state/ben-b-20261124/blocks5d-20261124"
SCRATCH = Path("/pscratch/sd/j/josephrb")
DEPLOY = _ND.parent                                     # the deploy the chain runs from (its committed files)
RUN_E = SCRATCH / "gencmp-e-20261101/rerun1"            # amendment E's run: its staged inputs/ and the chdefs pred/
X_PL = A.XKEY                                           # C_resp_plus_C_PL5D, the block the committed readouts adopted
BLOCKS = {                                              # key in vf_block.npz: the name each bound tool writes
    "dF": "dF",
    "C_resp_plus_dF": "C_resp + dF",
    "C_resp_plus_C_PL5D_plus_dF": "C_resp + C_PL5D + dF",
}
SIDE_KEY = {"with": "C_resp_plus_C_PL5D_plus_dF", "nopl": "C_resp_plus_dF"}
REPORTED_F = "C_total_plus_C_resp_plus_C_PL5D_plus_dF"
WITHOUT_F = "C_total_plus_C_resp_plus_dF"
VF_BLOCK_NPZ = "e1057f88f5d77b2dba7617982201e3a520940c32f369a938df064a8e8b7508ce"   # vf_block.npz (no code digest in it)
PINS = {
    "v_f_csv": "763f14c6ace6e69109fc11ded75d8654615fe55d5e53281e9911bc5318a03e93",
    "blocks5d_json": "c465768b490acc96515c5340585b8ff1f14735254f269af605ffaf182ae521f9",
    "c_e_csv": "222c4dd4efef0780c408b82caa8d360723bc8b73b784885789f374a624e6c715",
    "data_product_cpl": "d6752d2c64aad4426375c03a3171a7015f031e2027928cf89aea6cd3bbb84d50",
    "cpl_block_npz": "d9aa32fdb64357760348c9ccbc32fbea81d517f0f0786eedf17ab4946eaca59f",
}
SOURCES = {
    "v_f_csv": f"{B5D}/record/V_F.csv",
    "blocks5d_json": f"{B5D}/record/blocks5d.json",
    "c_e_csv": f"{FD}/fd/with-cpl/data-product/fd_data_product_cpl_C_e.csv",
    "data_product_cpl": f"{FD}/fd/with-cpl/data-product/fd_data_product_cpl.json",
    "cpl_block_npz": f"{FD}/fd/with-cpl/block/cpl_block.npz",
}
LABELS = {
    "block": "dF = V_F - C_e, V_F = L C_e L^T the 5D fluctuation block (blocks5d-20261124/RECEIPT.md), adopted into "
             "the reported covariance by DECISION-20261125 section 3, with A1 section 4's caveat: the factor measures "
             "the toy spread relative to LL5D's rebuilt reference block",
    "not_citable_for": ["a validated size for V_F", "a coverage or calibration statement"],
}
report, Stop = A.report, A.Stop


def symmetric(M: np.ndarray, tol: float = TOL) -> bool:
    return float(np.abs(M - M.T).max()) <= tol * float(np.abs(M).max())


# ---------------------------------------------------------------- block

def build_block(VF: np.ndarray, L: np.ndarray, Ce: np.ndarray, dp: dict, cpl: dict) -> dict:
    """V1-V3 on the inputs, then dF and the blocks; returns the npz arrays in their written order."""
    f = np.array(dp["f"], float)
    mats = {k: np.array(dp["matrices"][k], float) for k in
            ("C_e", "C_model_abs", "C_resp", "C_PL5D", "C_total_plus_C_resp", "C_total_plus_C_resp_plus_C_PL5D")}
    report("V1", "V_F, L and C_e are finite 16 x 16 matrices; f is 16 positive cells",
           all(M.shape == (N, N) and bool(np.all(np.isfinite(M))) for M in (VF, L, Ce))
           and f.shape == (N,) and bool(np.all(f > 0)))
    report("V1", "the C_e CSV is the with-block data product's C_e, bit for bit", np.array_equal(Ce, mats["C_e"]))
    report("V1", "the cpl block's f, C_resp and C_PL5D are the data product's, bit for bit",
           np.array_equal(cpl["f"], f) and np.array_equal(cpl["C_resp"], mats["C_resp"])
           and np.array_equal(cpl["C_PL5D"], mats["C_PL5D"]))
    scale = float(np.abs(np.diag(mats["C_total_plus_C_resp_plus_C_PL5D"])).max())
    report("V1", "the cpl block's C_resp + C_PL5D and reported matrix are the data product's, to 1e-12",
           float(np.abs(cpl[X_PL] - (mats["C_resp"] + mats["C_PL5D"])).max()) <= TOL * scale
           and float(np.abs(cpl[A.REPORTED] - mats["C_total_plus_C_resp_plus_C_PL5D"]).max()) <= TOL * scale)
    report("V2", "L is symmetric", symmetric(L))
    report("V2", "V_F is L C_e L^T, to 1e-12", float(np.abs(L @ Ce @ L.T - VF).max())
           <= TOL * float(np.abs(VF).max()))
    report("V2", "L commutes with C_e, to 1e-12", float(np.abs(L @ Ce - Ce @ L).max())
           <= TOL * float(np.abs(L @ Ce).max()))
    dF = VF - Ce
    report("V3", "dF is symmetric, to 1e-12", symmetric(dF))
    lam = np.linalg.eigvalsh((dF + dF.T) / 2 / np.outer(f, f))
    report("V3", "dF is positive semidefinite", bool(lam.min() >= -TOL * lam.max()), f"min {lam.min():.3e}")
    blocks = {"dF": dF, "C_resp_plus_dF": mats["C_resp"] + dF, "C_resp_plus_C_PL5D_plus_dF": cpl[X_PL] + dF}
    wo_f = mats["C_total_plus_C_resp"] + dF
    rep_f = mats["C_total_plus_C_resp_plus_C_PL5D"] + dF
    report("V3", "the reported matrix is V_F + C_model_abs + C_resp + C_PL5D, to 1e-12", float(np.abs(
        rep_f - (VF + mats["C_model_abs"] + mats["C_resp"] + mats["C_PL5D"])).max()) <= TOL * scale)
    report("V3", "the matrix without C_PL5D is V_F + C_model_abs + C_resp, to 1e-12", float(np.abs(
        wo_f - (VF + mats["C_model_abs"] + mats["C_resp"])).max()) <= TOL * scale)
    for k, M in (("reported", rep_f), ("without C_PL5D", wo_f)):
        report("V3", f"the revised matrix {k} is positive definite",
               bool(np.linalg.eigvalsh((M + M.T) / 2 / np.outer(f, f)).min() > 0))
    return {"f": f, "C_e": Ce, "V_F": VF, **blocks, WITHOUT_F: wo_f, REPORTED_F: rep_f}


def block_inputs(repo: Path) -> tuple:
    """V0: every input read once and checked against its pin; returns (V_F, L, C_e, the data product, the cpl block)."""
    raw = {k: A.pinned(repo / SOURCES[k], PINS[k], k, "V0") for k in PINS}
    VF = F.read_matrix_csv(raw["v_f_csv"].decode())
    Ce = F.read_matrix_csv(raw["c_e_csv"].decode())
    rec = json.loads(raw["blocks5d_json"])
    report("V0", "the B5D record names this V_F", rec["matrices_sha256"]["V_F.csv"] == PINS["v_f_csv"])
    VFj, L = (np.array(rec["fluctuation"][k], float) for k in ("V_F", "L"))
    report("V0", "the record's V_F is the CSV's, bit for bit", np.array_equal(VFj, VF))
    return VF, L, Ce, json.loads(raw["data_product_cpl"]), A.load_npz(repo / SOURCES["cpl_block_npz"])


def cmd_block(a) -> int:
    out_npz, out_json = a.out_dir / "vf_block.npz", a.out_dir / "vf_block.json"
    report("V0", "no output exists (no overwrite)", not out_npz.exists() and not out_json.exists())
    arrays = build_block(*block_inputs(a.repo))
    data = A.npz_bytes(arrays)
    report("V4", "the npz is the same bytes when written twice", data == A.npz_bytes(arrays))
    a.out_dir.mkdir(parents=True, exist_ok=True)
    A.write_atomic(out_npz, data)
    back = A.load_npz(out_npz)
    report("V4", "the npz reads back key by key, bit for bit", list(back) == list(arrays)
           and all(np.array_equal(back[k], arrays[k]) for k in back))
    h = A.sha256(out_npz)
    f = arrays["f"]
    readout = {"schema": "fd-vf-block/1", "labels": LABELS, "controls_passed": ["V0", "V1", "V2", "V3", "V4"],
               "cells": CELLS, "npz": {"file": out_npz.name, "sha256": h, "keys": list(arrays),
                                       "extra_blocks": [{"key": k, "name": n} for k, n in BLOCKS.items()]},
               "relative_sigma": {k: (np.sqrt(np.diag(arrays[k])) / f).tolist()
                                  for k in ("C_e", "V_F", *BLOCKS, WITHOUT_F, REPORTED_F)},
               "inputs_sha256": dict(PINS), "inputs": dict(SOURCES),
               "code_sha256": {"fd_vf_addition.py": A.sha256(Path(__file__).resolve()),
                               "fd_cpl_addition.py": A.sha256(Path(A.__file__).resolve())}}
    A.write_atomic(out_json, (json.dumps(readout, indent=1, allow_nan=False) + "\n").encode())
    print(json.dumps({"wrote": str(out_npz), "sha256": h}), flush=True)
    print(json.dumps({"wrote": str(out_json), "sha256": A.sha256(out_json)}), flush=True)
    return 0


# ---------------------------------------------------------------- product

PRODUCT_STEM = "fd_data_product_vf"
PRODUCT_MATRICES = ("C_e", "V_F", "dF", "C_model_abs", "C_resp", "C_PL5D", WITHOUT_F, REPORTED_F)
PRODUCT_INPUTS = ("data_product", "block_npz", "block_json", "g_readout")
REPORTED_NAME = f"C_total + {BLOCKS[SIDE_KEY['with']]}"         # C_total + C_resp + C_PL5D + dF


def product_labels(dp: dict) -> dict:
    return {"what": "data product with V_F adopted: the 5D result's revised covariance, with and without C_PL5D",
            "covariance": f"{REPORTED_NAME} = V_F + C_model_abs + C_resp + C_PL5D, the reported covariance with V_F "
                          f"adopted (FD-VF-ADDITION-DECLARATION.md section 1), dF = V_F - C_e; {WITHOUT_F} is the "
                          "same without the run-period block. Stage G's chi2 is against the reported matrix + V_g",
            "units": dp["labels"]["units"], "block": LABELS["block"],
            "not_citable_for": ["coverage", *LABELS["not_citable_for"]],
            "not": "no reading, claim or release text; whether it ships is Joseph's"}


def build_product(dp: dict, blk: dict, bj: dict, gr: dict, pins: dict) -> dict:
    report("K1", "the committed data product is the with-block product (its pin)",
           pins["data_product"] == PINS["data_product_cpl"] and [c["cell"] for c in dp["cells"]] == CELLS)
    report("K1", "the block readout names this npz and the pinned inputs", bj["npz"]["sha256"] == pins["block_npz"]
           and bj["inputs_sha256"] == PINS)
    xb = gr["extra_block"]
    report("K1", "Stage G's reported comparison adopted this block", xb["sha256"] == pins["block_npz"]
           and xb["key"] == SIDE_KEY["with"] and xb["name"] == BLOCKS[SIDE_KEY["with"]] and xb["role"] == "adopted")
    f = np.array(dp["f"], float)
    old = {k: np.array(dp["matrices"][k], float) for k in
           ("C_e", "C_model_abs", "C_resp", "C_PL5D", "C_total_plus_C_resp", A.REPORTED)}
    report("K2", "the block's f and C_e are the data product's, bit for bit", np.array_equal(blk["f"], f)
           and np.array_equal(blk["C_e"], old["C_e"]))
    dF = blk["dF"]
    scale = float(np.abs(np.diag(blk[REPORTED_F])).max())
    report("K2", "dF is the block's V_F - C_e, bit for bit", np.array_equal(dF, blk["V_F"] - blk["C_e"]))
    report("K2", "the revised matrices are the committed ones + dF, to 1e-12",
           float(np.abs(blk[REPORTED_F] - (old[A.REPORTED] + dF)).max()) <= TOL * scale
           and float(np.abs(blk[WITHOUT_F] - (old["C_total_plus_C_resp"] + dF)).max()) <= TOL * scale)
    sig = np.sqrt(np.diag(blk[REPORTED_F])) / f
    for p in gr["predictions"]:
        idx = [CELLS.index(c) for c in p["cells"]]
        report("K3", f"{p['name']}: Stage G's sigma_total_over_f is sqrt(diag(C_rep,F))/f to 1e-12 and its covariance "
                     f"is {REPORTED_NAME}", F.worst(np.array(p["sigma_total_over_f"]), sig[idx]) <= TOL
               and p["reported_covariance"] == REPORTED_NAME)
    mats = {"C_e": old["C_e"], "V_F": blk["V_F"], "dF": dF, "C_model_abs": old["C_model_abs"],
            "C_resp": old["C_resp"], "C_PL5D": old["C_PL5D"], WITHOUT_F: blk[WITHOUT_F], REPORTED_F: blk[REPORTED_F]}
    for k, C in mats.items():
        report("K4", f"{k} is symmetric", symmetric(C) if float(np.abs(C).max()) > 0 else True)
    for k in (WITHOUT_F, REPORTED_F):
        report("K4", f"{k} is positive definite",
               bool(np.linalg.eigvalsh((mats[k] + mats[k].T) / 2 / np.outer(f, f)).min() > 0))
    rho = F.correlation(mats[REPORTED_F])
    d = np.sqrt(np.diag(mats[REPORTED_F]))
    report("K5", "the correlation is the reported matrix's, symmetric, within [-1, 1], with a unit diagonal",
           float(np.abs(rho * np.outer(d, d) - mats[REPORTED_F]).max()) <= TOL * scale
           and float(np.abs(rho - rho.T).max()) <= TOL and float(np.abs(rho).max()) <= 1 + TOL
           and float(np.abs(np.diag(rho) - 1).max()) <= TOL)
    rel = {k: np.sqrt(np.diag(v)) / f for k, v in mats.items()}
    return {"f": f, "matrices": mats, "correlation": rho, "relative_sigma": rel}


def product_files(p: dict, dp: dict) -> dict[str, str]:
    axes = [ax for ax in dp["cells"][0]["box"]]
    head = ["cell", *[f"{ax}_{e}" for ax in axes for e in ("lo", "hi")], "f",
            *[f"rel_sigma_{k}" for k in PRODUCT_MATRICES]]
    rows = [[c["cell"], *[float(v) for ax in axes for v in c["box"][ax]], float(p["f"][i]),
             *[float(p["relative_sigma"][k][i]) for k in PRODUCT_MATRICES]] for i, c in enumerate(dp["cells"])]
    files = {f"{PRODUCT_STEM}_cells.csv": F.csv_text(head, rows)}
    for k in PRODUCT_MATRICES:
        files[f"{PRODUCT_STEM}_{k}.csv"] = F.matrix_csv(p["matrices"][k])
    files[f"{PRODUCT_STEM}_corr_{REPORTED_F}.csv"] = F.matrix_csv(p["correlation"])
    return files


def product_names() -> list[str]:
    return [f"{PRODUCT_STEM}.json", f"{PRODUCT_STEM}_cells.csv",
            *[f"{PRODUCT_STEM}_{k}.csv" for k in PRODUCT_MATRICES], f"{PRODUCT_STEM}_corr_{REPORTED_F}.csv"]


def cmd_product(a, pins: dict | None) -> int:
    if pins is None:
        raise Stop("K0", "product runs in the chain only: the block's and Stage G's pins are the files it just wrote")
    report("K0", "no output exists (no overwrite)", not any((a.out_dir / n).exists() for n in product_names()))
    report("K0", "the committed data product's pin is the declared one", pins["data_product"] == PINS["data_product_cpl"])
    raw = {k: A.pinned(getattr(a, k), pins[k], k, "K0") for k in PRODUCT_INPUTS}
    dp, bj, gr = (json.loads(raw[k]) for k in ("data_product", "block_json", "g_readout"))
    p = build_product(dp, A.load_npz(a.block_npz), bj, gr, pins)
    files = product_files(p, dp)
    readout = {"schema": "fd-data-product-vf/1", "labels": {**product_labels(dp), "cells": dp["labels"]["cells"]},
               "controls_passed": ["K0", "K1", "K2", "K3", "K4", "K5", "K6"], "cells": dp["cells"], "h2": dp["h2"],
               "f": p["f"].tolist(), "matrices": {k: v.tolist() for k, v in p["matrices"].items()},
               "correlation": p["correlation"].tolist(), "correlation_of": REPORTED_F,
               "relative_sigma": {k: v.tolist() for k, v in p["relative_sigma"].items()},
               "files_sha256": {n: hashlib.sha256(t.encode()).hexdigest() for n, t in files.items()},
               "inputs_sha256": {k: pins[k] for k in PRODUCT_INPUTS},
               "code_sha256": {"fd_vf_addition.py": A.sha256(Path(__file__).resolve()),
                               "fd_data_product.py": A.sha256(Path(F.__file__).resolve())}, "argv": list(sys.argv)}
    js = json.loads(json.dumps(readout, allow_nan=False))
    for k in PRODUCT_MATRICES:
        back = F.read_matrix_csv(files[f"{PRODUCT_STEM}_{k}.csv"])
        report("K6", f"{k}: the CSV and the JSON read back bit for bit", np.array_equal(back, p["matrices"][k])
               and np.array_equal(np.array(js["matrices"][k]), p["matrices"][k]))
    report("K6", "the correlation's CSV and JSON read back bit for bit", np.array_equal(
        F.read_matrix_csv(files[f"{PRODUCT_STEM}_corr_{REPORTED_F}.csv"]), p["correlation"])
           and np.array_equal(np.array(js["correlation"]), p["correlation"]))
    a.out_dir.mkdir(parents=True, exist_ok=True)
    files[f"{PRODUCT_STEM}.json"] = json.dumps(readout, indent=1, allow_nan=False) + "\n"
    for n, text in files.items():
        A.write_atomic(a.out_dir / n, text.encode())
        print(json.dumps({"wrote": str(a.out_dir / n), "sha256": A.sha256(a.out_dir / n)}), flush=True)
    return 0


def deposit_variant(pins: dict) -> DC.Variant:
    """The deposit candidate's variant for the reported matrix with V_F, with the chain's pins of the V_F data product
    and Stage G readout."""
    labels = {**DC.LABELS,
              "what": "the 5D result on its sixteen reporting cells R00-R15: cell definitions, the measured vector f, "
                      f"the reported covariance with V_F adopted, {REPORTED_NAME}, and its correlation matrix",
              "covariance": f"{REPORTED_NAME} = V_F + C_model_abs + C_resp + C_PL5D, dF = V_F - C_e (the V_F data "
                            f"product's {REPORTED_F}). The paper's chi2 for a prediction g on its cells c is "
                            "d^T (C + V_g)^-1 d with d = f - g, C this covariance on c, and V_g = diag of g's own "
                            "finite-MC variance, ndf n; its shape-only chi2 adds 100 f f^T (f on c, absolute units) to "
                            "C + V_g, ndf n - 1; g and V_g are the prediction's, not part of the measurement",
              "block": LABELS["block"]}
    return DC.Variant(key=REPORTED_F, name=REPORTED_NAME, labels=labels,
                      pins={"data_product": pins["data_product"], "g_readout": pins["g_readout"]},
                      sources={"data_product": f"fd/with-vf/data-product/{PRODUCT_STEM}.json",
                               "g_readout": "fd/with-vf/readout/S/vf-with/fd_g_readout.json"})


# ---------------------------------------------------------------- table

def rename_vf(key: str) -> str:
    """A V_F readout's key, as the OLD readout spells it (keys built from the block's name)."""
    for k in ("C_resp_plus_C_PL5D_plus_dF", "C_resp_plus_dF"):
        key = key.replace(BLOCKS[k], BLOCKS[k][:-len(" + dF")])
    return key.replace(" + dF", "")


def paired(old, new, path=""):
    """(path, OLD, V_F) for every numeric leaf at the same place in both readouts, keys renamed."""
    if isinstance(old, dict) and isinstance(new, dict):
        nk = {rename_vf(k): k for k in new}
        for k in sorted(old):
            if k in nk:
                yield from paired(old[k], new[nk[k]], f"{path}/{k}")
    elif isinstance(old, list) and isinstance(new, list) and len(old) == len(new):
        for i, (x, y) in enumerate(zip(old, new)):
            yield from paired(x, y, f"{path}/{i}")
    elif not isinstance(old, (dict, list, str)) and not isinstance(new, (dict, list, str)):
        yield path, old, new


def listed(r: dict) -> list:
    return sorted(x["truth"] for x in r["triggers"]["listed"])


def curated(old: dict, new: dict) -> dict:
    """The named rows: each F readout's listing and per-truth grades, each Stage G prediction's chi2 and p."""
    out = {"listings": {}, "truths": {}, "stage_g": {}}
    for k in old:
        o, n = old[k], new[k]
        if "triggers" in o:
            report("T", f"{k}: the truths are the same, in the same order, on both sides",
                   [t["name"] for t in o["truths"]] == [t["name"] for t in n["truths"]])
            out["listings"][k] = {"old": listed(o), "vf": listed(n), "newly_listed": sorted(set(listed(n)) - set(listed(o))),
                                  "cleared": sorted(set(listed(o)) - set(listed(n)))}
            out["truths"][k] = [{"truth": to["name"], "graded": to["graded"],
                                 "old": {**{q: to["grade"][q] for q in ("chi2", "p")},
                                         "cells_abs_z_gt_2": to["grade"]["cells_abs_z_gt_2"]},
                                 "vf": {**{q: tn["grade"][q] for q in ("chi2", "p")},
                                        "cells_abs_z_gt_2": tn["grade"]["cells_abs_z_gt_2"]},
                                 "grade_matrix": {"old": to["grade_matrix"], "vf": tn["grade_matrix"]}}
                                for to, tn in zip(o["truths"], n["truths"])]
        elif k.endswith("/g"):
            report("T", f"{k}: the predictions are the same, in the same order, on both sides",
                   [p["name"] for p in o["predictions"]] == [p["name"] for p in n["predictions"]])
            out["stage_g"][k] = [{"prediction": po["name"], "kind": kind, "ndf": po[kind]["ndf"],
                                  "old": {q: po[kind][q] for q in ("chi2", "p", "matrix")},
                                  "vf": {q: pn[kind][q] for q in ("chi2", "p", "matrix")}}
                                 for po, pn in zip(o["predictions"], n["predictions"]) for kind in ("total", "shape_only")]
    return out


def table_md(c: dict, counts: dict) -> str:
    L = ["# V_F's adoption: every Phase 1 readout, OLD and V_F", "", LABELS["block"] + ".", "",
         "## Listings (p < 0.01 or any |z| > 2)", "", "| readout | OLD | V_F | newly listed | cleared |",
         "|---|---|---|---|---|"]
    L += [f"| {k} | {', '.join(v['old']) or 'none'} | {', '.join(v['vf']) or 'none'} | "
          f"{', '.join(v['newly_listed']) or '-'} | {', '.join(v['cleared']) or '-'} |" for k, v in c["listings"].items()]
    for k, rows in c["stage_g"].items():
        L += ["", f"## Stage G, {k}", "", "| prediction | kind | ndf | chi2 OLD | p OLD | chi2 V_F | p V_F |",
              "|---|---|---:|---:|---:|---:|---:|"]
        L += [f"| {r['prediction']} | {r['kind']} | {r['ndf']} | {r['old']['chi2']:.3f} | {r['old']['p']:.3g} | "
              f"{r['vf']['chi2']:.3f} | {r['vf']['p']:.3g} |" for r in rows]
    for k, rows in c["truths"].items():
        L += ["", f"## {k}: each truth", "", "| truth | graded | chi2 OLD | p OLD | cells OLD | chi2 V_F | p V_F | "
              "cells V_F |", "|---|---|---:|---:|---|---:|---:|---|"]
        L += [f"| {t['truth']} | {t['graded']} | {t['old']['chi2']:.4g} | {t['old']['p']:.3g} | "
              f"{' '.join(t['old']['cells_abs_z_gt_2']) or '-'} | {t['vf']['chi2']:.4g} | {t['vf']['p']:.3g} | "
              f"{' '.join(t['vf']['cells_abs_z_gt_2']) or '-'} |" for t in rows]
    L += ["", "## Every other number", "", "`fd_vf_table.json` `leaves` pairs every numeric leaf of each readout:", ""]
    L += [f"- {k}: {n} paired leaves" for k, n in counts.items()]
    L += ["", f"NOT CITABLE FOR: {'; '.join(LABELS['not_citable_for'])}. Readings go to the director first.", ""]
    return "\n".join(L)


def cmd_table(a, pins: dict | None) -> int:
    """``pairs``: a JSON list of [label, OLD path, V_F path]; ``pins`` the sha256 of each path, from the chain."""
    if pins is None:
        raise Stop("T", "table runs in the chain only: the readouts' pins are the files the chain read and wrote")
    out_json, out_md = a.out_dir / "fd_vf_table.json", a.out_dir / "fd_vf_table.md"
    report("T", "no output exists (no overwrite)", not out_json.exists() and not out_md.exists())
    pairs = json.loads(a.pairs.read_bytes())
    old, new = {}, {}
    for label, po, pn in pairs:
        old[label] = json.loads(A.pinned(Path(po), pins[po], f"{label} OLD", "T"))
        new[label] = json.loads(A.pinned(Path(pn), pins[pn], f"{label} V_F", "T"))
    c = curated(old, new)
    leaves = {k: [[p, x, y] for p, x, y in paired(old[k], new[k])] for k in old}
    counts = {k: len(v) for k, v in leaves.items()}
    table = {"schema": "fd-vf-table/1", "labels": {"what": "every Phase 1 readout's numbers, OLD and with V_F",
                                                   **LABELS}, "controls_passed": ["T"], "curated": c,
             "leaves": leaves, "leaf_counts": counts, "inputs_sha256": dict(pins),
             "code_sha256": {"fd_vf_addition.py": A.sha256(Path(__file__).resolve())}, "argv": list(sys.argv)}
    a.out_dir.mkdir(parents=True, exist_ok=True)
    A.write_atomic(out_json, (json.dumps(table, indent=1, allow_nan=False) + "\n").encode())
    A.write_atomic(out_md, table_md(c, counts).encode())
    for p in (out_json, out_md):
        print(json.dumps({"wrote": str(p), "sha256": A.sha256(p)}), flush=True)
    return 0


# ---------------------------------------------------------------- chain

E_STEPS = ("g", "g_diag", "g_followup", "g_sens2", "flux_boot")
S_STEPS = ("f0b", "f1", "g")
OLD_F0 = (f"{FD}/fd/readout/fd_f0_readout.json", "6e7d718bd393dd0600e974d0ce9b5c389486890cb7112550b22289008d6d312b")
OLD_S = {
    "with": {"f0b": (f"{FD}/fd/with-cpl/readout/fd_f0b_readout.json",
                     "5f542830561731b567f2b97d78e5e9677a9802a35ef9c21855828bf184e6f3d6"),
             "f1": (f"{FD}/fd/with-cpl/readout/fd_f1_readout.json",
                    "5ccc89e58096a14ab8dc0e3e6f508ca4b2b546b629077560a09a4596cde40395"),
             "g": (f"{FD}/fd/with-cpl/readout/fd_g_readout.json",
                   "b55366b3fd2d35a5426351531a9aa002a4d6be4b1048bd27339491e8c400a6fd")},
    "nopl": {k: A.COMMITTED[k] for k in S_STEPS},
}
_CE = f"{FD}/fd/gencmp-e/rerun1/chain/chdefs"
OLD_E = {
    "with": {"g": (f"{_CE}/with/readout/fd_g_readout.json",
                   "a19009e0bd83b9bb8f9ad65fb65804e6f62c8953310103fbfe6fce5f84995875"),
             "g_diag": (f"{_CE}/with/readout/fd_g_diag_readout.json",
                        "522bfafa3016fadbd62c72f9f34153e17cd514a3b06acf282030d550f5dc1855"),
             "g_followup": (f"{_CE}/with/readout/fd_g_followup_readout.json",
                            "586cd74105d0837c69290d0370f6327cda75a92ee31f2d437658c626b4ab1e8f"),
             "g_sens2": (f"{_CE}/with/readout/fd_g_sens2_readout.json",
                         "4bc21dfda9c49762227fc4c486ee9decc349863aaea095f94347ad4b963d4513"),
             "flux_boot": (f"{_CE}/with/readout/fd_flux_boot_readout.json",
                           "5bb475eada29d270f93bf124251b98152a437280fa684429fe20e15d940f2e5d")},
    "nopl": {"g": (f"{_CE}/nopl/readout/fd_g_readout.json",
                   "d9a1ce38040b8cd3c2a6deb787f8a7dc90aca5c4d3a5a8d25a60b7f8ab582ed9"),
             "g_diag": (f"{_CE}/nopl/readout/fd_g_diag_readout.json",
                        "4e77966e93bd21d53ae777f2af02f00963d9eec45372997fc7af5fd45d2a099f"),
             "g_followup": (f"{_CE}/nopl/readout/fd_g_followup_readout.json",
                            "748f3af6e7fa54f916d73295b078e5b8a768a8abe024e848a55d9b90f9a806ac"),
             "g_sens2": (f"{_CE}/nopl/readout/fd_g_sens2_readout.json",
                         "6626cb7347793b50a4431307244d50e3e863202c6ac920d659d10ec691e7f7e9"),
             "flux_boot": (f"{_CE}/nopl/readout/fd_flux_boot_readout.json",
                           "24ff27f90067864292ef93bd018f5040548f90118368b3cf03fc3760377661ed")},
}
OLD_E_FIG = {"with": f"{_CE}/with/figures", "nopl": f"{_CE}/nopl/figures"}
OLD_DEP = f"{FD}/fd/with-cpl/deposit-candidate"
CPL_BLOCK_JSON = "4023746e3a819e8cc8348c457d7dc1ee55df66eaa5f5f68082824b9df27cabd6"
R_EXCLUDE = ("/argv", "/code_sha256", "/code", "/versions", "/extra_block/file")
FIG_EXCLUDE = A.FIG_EXCLUDE
DP_EXCLUDE = ("/argv", "/code_sha256")

BOOT = """import json, sys
nd, mod, pins_file, variant, preds_file, argv = (sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5],
                                                 json.loads(sys.argv[6]))
sys.path.insert(0, nd)
import importlib
T = importlib.import_module(mod)
pins = json.load(open(pins_file))
sys.argv = [T.__file__, *argv]
kw = {}
if preds_file != "-":
    kw["predictions"] = json.load(open(preds_file))
if variant in ("with-cpl", "with-vf"):
    import fd_cpl_addition as A, fd_vf_addition as V
    kw["variant"] = (A if variant == "with-cpl" else V).deposit_variant(pins)
    pins = None
sys.exit(T.run(T.build_args(argv), pins=pins, **kw))
"""


class Chain(A.Chain):
    """fd_cpl_addition's Chain, with one BOOT for the pins, the prediction set and either deposit variant."""

    def __init__(self, paths, receipt: Path, steps: list, preds_file: Path | None = None):
        super().__init__(paths, receipt)
        self.steps, self.preds_file = steps, preds_file

    def run(self, name, arm, tool, argv, outputs, timeout, pins=None, variant=""):
        log = self.p.BA / "logs" / f"{arm}-{name}"
        preds = "-" if self.preds_file is None or tool == "fd_g_figures_check" else str(self.preds_file)
        if pins is None:
            cmd = [sys.executable, "-I", "-B", str(self.p.nd / f"{tool}.py"), *argv]
        else:
            pf = self.p.BA / "pins" / f"{arm}-{name}.json"
            A.write_atomic(pf, (json.dumps(pins, indent=1) + "\n").encode())
            cmd = [sys.executable, "-I", "-B", "-c", BOOT, str(self.p.nd), tool, str(pf), variant or "-", preds,
                   json.dumps(argv)]
        t0 = time.time()
        with open(f"{log}.out", "w") as o, open(f"{log}.err", "w") as e:
            try:
                rc = subprocess.run(cmd, stdout=o, stderr=e, timeout=timeout, cwd=self.p.BA,
                                    env={k: v for k, v in os.environ.items() if k != "PYTHONPATH"}).returncode
            except subprocess.TimeoutExpired:
                rc = 124
        rec = {"step": name, "arm": arm, "tool": tool, "argv": argv, "pins": pins, "variant": variant or None,
               "predictions": None if preds == "-" else preds, "rc": rc, "wall_s": round(time.time() - t0, 1),
               "start_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t0)),
               "outputs": {str(q): (A.sha256(q) if Path(q).exists() else None) for q in outputs}}
        self.steps.append(rec)
        self.save()
        print(f"[chain] {arm} {name}: rc {rc}, {rec['wall_s']} s", flush=True)
        if rc != 0 or any(v is None for v in rec["outputs"].values()):
            raise Stop("C", f"{arm} {name} exited {rc} or wrote no {[k for k, v in rec['outputs'].items() if v is None]}")
        return rec


def arm_flags(p, arm: str, vf: dict, role: bool = True) -> list:
    """The extra block's flags for an arm: OLD with the block its pinned files used, V_F with vf_block.npz."""
    kind, side = arm.split("-")
    if kind == "old" and side == "with":
        return A.extra(p.T / "fd/with-cpl/block/cpl_block.npz", PINS["cpl_block_npz"], A.XKEY, A.NAME, role)
    if kind == "old":
        return A.extra(p.cresp, A.PINS["cresp_npz"], "C_resp", "C_resp", role)
    return A.extra(vf["npz"], vf["sha"], SIDE_KEY[side], BLOCKS[SIDE_KEY[side]], role)


def arm_name(arm: str) -> str | None:
    """The reported block's name a figure is drawn with; None for OLD without, whose figures use the default."""
    kind, side = arm.split("-")
    if kind == "old":
        return A.NAME if side == "with" else None
    return BLOCKS[SIDE_KEY[side]]


def run_f0(c: Chain, arm: str, vf: dict) -> Path:
    p = c.p
    W = p.BA / "S" / arm
    (W / "readout").mkdir(parents=True, exist_ok=True)
    out = W / "readout" / "fd_f0_readout.json"
    xb0 = [] if arm == "old-f0" else A.extra(vf["npz"], vf["sha"], "dF", BLOCKS["dF"], role=False)
    c.run("f0", arm, "fd_f0_regrade", [*p.f0(), *xb0, "--out-json", str(out), "--out-npz",
                                       str(W / "fd_f0_experiments.npz")], [out], A.TIMEOUT["f0b"])
    return out


def run_s(c: Chain, arm: str, vf: dict, f0b_old: tuple[Path, str] | None) -> dict:
    """F0b, F1 and Stage G on the original predictions for one arm. F1 reads ``f0b_old`` (an OLD arm: the committed
    F0b, as its pinned readout was made) or this arm's F0b."""
    p = c.p
    xb, xb0 = arm_flags(p, arm, vf), arm_flags(p, arm, vf, role=False)
    W = p.BA / "S" / arm
    (W / "readout").mkdir(parents=True, exist_ok=True)
    out = {k: W / "readout" / Path(A.COMMITTED[k][0]).name for k in S_STEPS}
    c.run("f0b", arm, "fd_f0_regrade", A.step_argv(p, "f0b", xb, xb0, {}, out["f0b"], "with"), [out["f0b"]],
          A.TIMEOUT["f0b"])
    up = ({"f0b": f0b_old[0], "f0b_sha256": f0b_old[1]} if f0b_old else
          {"f0b": out["f0b"], "f0b_sha256": A.sha256(out["f0b"])})
    c.run("f1", arm, "fd_f0_regrade", A.step_argv(p, "f1", xb, xb0, up, out["f1"], "with"), [out["f1"]],
          A.TIMEOUT["f1"])
    c.run("g", arm, "fd_g_compare", A.step_argv(p, "g", xb, xb0, up, out["g"], "with"), [out["g"]], A.TIMEOUT["g"])
    return out


def run_e(c: Chain, arm: str, vf: dict, f0b: tuple[Path, str]) -> dict:
    """The chdefs set for one arm: Stage G, G-DIAG, G-FOLLOWUP, G-SENS2 and the flux bootstrap, each pinned to the
    readouts the steps before wrote (fd_gencmp_e.run_set), then the three figures (with ``f0b``) and their check."""
    import fd_g_figures as FG
    import fd_gencmp_e as E
    p = c.p
    xb = arm_flags(p, arm, vf)
    base = {"s5p_sums": A.sha256(p.s5p_sums)}
    W = p.BA / "E" / arm
    (W / "readout").mkdir(parents=True, exist_ok=True)
    out = {k: W / "readout" / Path(A.COMMITTED[k][0]).name for k in E_STEPS}
    up, H = {}, {}
    for k in E_STEPS:
        c.run(k, f"E-{arm}", A.TOOLS[k], A.step_argv(p, k, xb, xb, up, out[k], "with"), [out[k]], A.TIMEOUT[k],
              pins=E.step_pins(k, H, base))
        H[k], up[k] = A.sha256(out[k]), out[k]
    src = {**up, "f0b": f0b[0]}
    fig = W / "figures"
    name = arm_name(arm)
    fargv = [*A.step_argv(p, "figures", xb, xb, src, fig, "without"),
             *(["--reported-block-name", name] if name else []), "--prediction-set", "gencmp-chdefs"]
    c.run("figures", f"E-{arm}", "fd_g_figures", fargv, [fig / f"{n}{e}" for n in A.FIG_NAMES for e in (".pdf", ".json")],
          75, pins={**FG.PINS, "g_readout": H["g"], "g_diag_readout": H["g_diag"], "g_followup_readout": H["g_followup"],
                    "g_sens2_readout": H["g_sens2"], "f0b_readout": f0b[1]})
    c.run("figures_check", f"E-{arm}", "fd_g_figures_check",
          [*A.step_argv(p, "figures_check", xb, xb, src, fig, "with"), "--prediction-set", "gencmp-chdefs"], [], 75,
          pins={})
    return {"out": out, "H": H, "fig": fig}


def check_r(c: Chain, label: str, D: Path, rel: str, pin: str, new: Path, strings: bool) -> None:
    c.check(f"R {label}: the committed readout is the pinned bytes", A.sha256(D / rel) == pin, rel)
    old, nw = json.loads((D / rel).read_bytes()), json.loads(new.read_bytes())
    bad = A.compare_numbers(old, nw, R_EXCLUDE) + (A.compare_strings(old, nw, R_EXCLUDE) if strings else [])
    c.check(f"R {label}: structure and numbers{' and strings' if strings else ''} are the committed readout's",
            not bad, bad[:20])


def check_r_figures(c: Chain, label: str, D: Path, rel: str, fig: Path) -> None:
    for n in A.FIG_NAMES:
        old = json.loads((D / rel / f"{n}.json").read_bytes())
        new = json.loads((fig / f"{n}.json").read_bytes())
        bad = A.compare_numbers(old, new, FIG_EXCLUDE) + A.compare_strings(old, new, FIG_EXCLUDE)
        c.check(f"R {label} figure {n}: the sidecar is the committed one but argv, code and versions; the PDF the same "
                "bytes", not bad and (fig / f"{n}.pdf").read_bytes() == (D / rel / f"{n}.pdf").read_bytes(), bad[:20])


def check_s(c: Chain, label: str, g: Path, f0b: Path | None, blk: dict, side: str) -> None:
    M = blk[REPORTED_F] if side == "with" else blk[WITHOUT_F]
    sig = np.sqrt(np.diag(M)) / blk["f"]
    gr = json.loads(g.read_bytes())
    c.check(f"S {label} g: every prediction's sigma_total_over_f is sqrt(diag(C_rep,F))/f", all(
        F.worst(np.array(q["sigma_total_over_f"]), sig[[CELLS.index(x) for x in q["cells"]]]) <= TOL
        for q in gr["predictions"]), None)
    if f0b is not None:
        b = json.loads(f0b.read_bytes())
        c.check(f"S {label} f0b: its sqrt(diag(C_total + X_F))/f is sqrt(diag(C_rep,F))/f",
                F.worst(np.array(b[f"relative_sigma_plus_{BLOCKS[SIDE_KEY[side]]}"]["C_total"]), sig) <= TOL, None)


def check_c(c: Chain, label: str, path: Path, vf_sha: str, upstream: dict) -> None:
    r = json.loads(path.read_bytes())
    xbr, ins = r.get("extra_block") or {}, r.get("inputs_sha256", {})
    named = [v for v in (xbr.get("sha256"), ins.get("extra_block")) if v is not None]
    c.check(f"C {label}: the readout names vf_block.npz's sha256, and each upstream readout's as written",
            bool(named) and all(v == vf_sha for v in named) and all(ins.get(f) == h for f, h in upstream.items()),
            {"named": named, "upstream": {f: ins.get(f) for f in upstream}})


def cmd_chain(a) -> int:
    import fd_gencmp_e as E
    D = DEPLOY
    BA = a.run_dir
    for d in ("S", "E", "vf", "table", "chain.json"):
        report("C", f"{d} does not exist (no overwrite)", not (BA / d).exists())
    for d in ("logs", "pins"):
        (BA / d).mkdir(parents=True, exist_ok=True)
    steps: list = []
    receipt = BA / "chain.json"
    pS = A.Paths(D, a.scratch, BA)
    pE = E.Paths(D, BA, a.run_e, "chdefs")
    try:
        cS = Chain(pS, receipt, steps)
        # the block: the committed npz is the pinned bytes, and rebuilding it here gives the same bytes
        vnpz = D / FD / "fd/with-vf/block/vf_block.npz"
        cS.check("C vf_block.npz: the committed block is the pinned bytes", A.sha256(vnpz) == VF_BLOCK_NPZ, str(vnpz))
        cS.run("block", "vf", "fd_vf_addition", ["block", "--repo", str(D), "--out-dir", str(BA / "vf" / "block")],
               [BA / "vf" / "block" / "vf_block.npz", BA / "vf" / "block" / "vf_block.json"], 75)
        cS.check("C vf_block.npz: rebuilt in the deploy, the same bytes",
                 A.sha256(BA / "vf" / "block" / "vf_block.npz") == VF_BLOCK_NPZ, None)
        vf = {"npz": vnpz, "sha": VF_BLOCK_NPZ}
        blk = A.load_npz(vnpz)
        specs = E.load_chdefs(a.run_e / "pred")
        pf = BA / "pins" / "predictions-chdefs.json"
        A.write_atomic(pf, (json.dumps(specs, indent=1) + "\n").encode())
        cE = Chain(pE, receipt, steps, pf)
        for rel, pin in [OLD_F0, *[v for s in (OLD_S, OLD_E) for arm in s.values() for v in arm.values()]]:
            cS.check(f"R {rel}: the committed file is the pinned bytes", A.sha256(D / rel) == pin, rel)

        # ---- the OLD arms: every output against its pinned file before any V_F number
        check_r(cS, "F0", D, *OLD_F0, run_f0(cS, "old-f0", vf), strings=False)
        for side in ("with", "nopl"):
            arm = f"old-{side}"
            f0b_old = (D / OLD_S[side]["f0b"][0], OLD_S[side]["f0b"][1])
            out = run_s(cS, arm, vf, f0b_old)
            for k in S_STEPS:
                check_r(cS, f"S {arm} {k}", D, *OLD_S[side][k], out[k], strings=False)
            res = run_e(cE, arm, vf, f0b_old)
            for k in E_STEPS:
                check_r(cE, f"E {arm} {k}", D, *OLD_E[side][k], res["out"][k], strings=(side == "with"))
            check_r_figures(cE, f"E {arm}", D, OLD_E_FIG[side], res["fig"])
        # the product and the deposit candidate as committed, by their own tools
        pdir = BA / "S" / "old-with" / "data-product"
        cS.run("data_product", "old-with", "fd_cpl_addition",
               ["product", "--data-product", str(pS.committed["data_product"]), "--block-npz",
                str(pS.T / "fd/with-cpl/block/cpl_block.npz"), "--block-json", str(pS.T / "fd/with-cpl/block/cpl_block.json"),
                "--g-readout", str(D / OLD_S["with"]["g"][0]), "--audit-json", str(pS.audit), "--out-dir", str(pdir)],
               [pdir / f"{A.PRODUCT_STEM}.json"], 75,
               pins={"data_product": A.PINS["data_product"], "block_npz": PINS["cpl_block_npz"],
                     "block_json": CPL_BLOCK_JSON, "g_readout": OLD_S["with"]["g"][1], "audit_json": A.PINS["audit"]})
        cdp = D / FD / "fd/with-cpl/data-product"
        csvs = sorted(q.name for q in cdp.glob("*.csv"))
        cS.check("R data_product: every CSV is the committed with-block product's, byte for byte", bool(csvs) and all(
            (pdir / n).read_bytes() == (cdp / n).read_bytes() for n in csvs)
            and sorted(q.name for q in pdir.glob("*.csv")) == csvs, csvs)
        old = json.loads(Path(D / SOURCES["data_product_cpl"]).read_bytes())
        new = json.loads((pdir / f"{A.PRODUCT_STEM}.json").read_bytes())
        bad = A.compare_numbers(old, new, DP_EXCLUDE) + A.compare_strings(old, new, DP_EXCLUDE)
        cS.check("R data_product: its JSON is the committed one but argv and code_sha256", not bad, bad[:20])
        dep = BA / "S" / "old-with" / "deposit-candidate"
        dpins = {"data_product": PINS["data_product_cpl"], "g_readout": OLD_S["with"]["g"][1]}
        dargv = ["build", "--data-product", str(D / SOURCES["data_product_cpl"]), "--g-readout",
                 str(D / OLD_S["with"]["g"][0]), "--out-dir", str(dep)]
        cS.run("deposit_build", "old-with", "fd_deposit_candidate", dargv,
               [dep / n for n in (*DC.FILES, DC.REFERENCE)], 75, pins=dpins, variant="with-cpl")
        for n in (*DC.FILES, DC.REFERENCE):
            a_, b_ = (D / OLD_DEP / n).read_bytes().decode(), (dep / n).read_bytes().decode()
            ok = a_ == b_ if n.endswith(".csv") else DC.without_code(a_) == DC.without_code(b_)
            cS.check(f"R deposit {n}: the committed with-block file{'' if n.endswith('.csv') else ' but code_sha256'}",
                     ok, n)

        # ---- the V_F arms
        f0 = run_f0(cS, "vf-f0", vf)
        check_c(cS, "vf-f0 f0", f0, vf["sha"], {})
        res_s, res_e = {}, {}
        for side in ("with", "nopl"):
            arm = f"vf-{side}"
            out = run_s(cS, arm, vf, None)
            res_s[side] = out
            check_c(cS, f"{arm} f0b", out["f0b"], vf["sha"], {})
            check_c(cS, f"{arm} f1", out["f1"], vf["sha"], {"f0b_readout": A.sha256(out["f0b"])})
            check_c(cS, f"{arm} g", out["g"], vf["sha"], {})
            check_s(cS, arm, out["g"], out["f0b"], blk, side)
            res = run_e(cE, arm, vf, (out["f0b"], A.sha256(out["f0b"])))
            res_e[side] = res
            H = res["H"]
            for k in E_STEPS:
                check_c(cE, f"E {arm} {k}", res["out"][k], vf["sha"],
                        {f: H[u] for f, u in A.UPSTREAM.get(k, {}).items()})
            check_s(cE, f"E {arm}", res["out"]["g"], None, blk, side)
        vdir = BA / "vf" / "data-product"
        gS = res_s["with"]["g"]
        cS.run("data_product", "vf-with", "fd_vf_addition",
               ["product", "--data-product", str(D / SOURCES["data_product_cpl"]), "--block-npz", str(vnpz),
                "--block-json", str(D / FD / "fd/with-vf/block/vf_block.json"), "--g-readout", str(gS),
                "--out-dir", str(vdir)], [vdir / f"{PRODUCT_STEM}.json"], 75,
               pins={"data_product": PINS["data_product_cpl"], "block_npz": vf["sha"],
                     "block_json": A.sha256(D / FD / "fd/with-vf/block/vf_block.json"), "g_readout": A.sha256(gS)})
        vdep = BA / "vf" / "deposit-candidate"
        vpins = {"data_product": A.sha256(vdir / f"{PRODUCT_STEM}.json"), "g_readout": A.sha256(gS)}
        cS.run("deposit_build", "vf-with", "fd_deposit_candidate",
               ["build", "--data-product", str(vdir / f"{PRODUCT_STEM}.json"), "--g-readout", str(gS), "--out-dir",
                str(vdep)], [vdep / n for n in (*DC.FILES, DC.REFERENCE)], 75, pins=vpins, variant="with-vf")
        cS.run("deposit_check", "vf-with", "fd_deposit_candidate",
               ["check", "--package", str(vdep), "--data-product", str(vdir / f"{PRODUCT_STEM}.json"), "--g-readout",
                str(gS)], [vdep / "deposit.json"], 75, pins=vpins, variant="with-vf")

        # ---- the table: every V_F readout beside its OLD one
        pairs = [["F0", str(D / OLD_F0[0]), str(f0)]]
        for side in ("with", "nopl"):
            pairs += [[f"S {side}/{k}", str(D / OLD_S[side][k][0]), str(res_s[side][k])] for k in S_STEPS]
            pairs += [[f"E {side}/{k}", str(D / OLD_E[side][k][0]), str(res_e[side]["out"][k])] for k in E_STEPS]
        pf2 = BA / "pins" / "table-pairs.json"
        A.write_atomic(pf2, (json.dumps(pairs, indent=1) + "\n").encode())
        tab = BA / "table"
        cS.run("table", "vf", "fd_vf_addition", ["table", "--pairs", str(pf2), "--out-dir", str(tab)],
               [tab / "fd_vf_table.json", tab / "fd_vf_table.md"], 75,
               pins={q: A.sha256(Path(q)) for _, po, pn in pairs for q in (po, pn)})
    except Stop as e:
        print(f"[STOP] {e}", file=sys.stderr, flush=True)
        return 1
    print(f"[chain] done: {len(steps)} records in {receipt}", flush=True)
    return 0


# ---------------------------------------------------------------- CLI

def build_args(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("block")
    b.add_argument("--repo", type=Path, required=True, help="the checkout the committed inputs are read from")
    b.add_argument("--out-dir", type=Path, required=True)
    p = sub.add_parser("product")
    for k in (*PRODUCT_INPUTS, "out_dir"):
        p.add_argument("--" + k.replace("_", "-"), dest=k, type=Path, required=True)
    t = sub.add_parser("table")
    t.add_argument("--pairs", type=Path, required=True)
    t.add_argument("--out-dir", type=Path, required=True)
    c = sub.add_parser("chain")
    c.add_argument("--scratch", type=Path, default=SCRATCH, help="$P, the pscratch root the inputs are under")
    c.add_argument("--run-e", type=Path, default=RUN_E, help="amendment E's run directory (inputs/, pred/)")
    c.add_argument("--run-dir", type=Path, required=True, help="$BA, where S/, E/, vf/, table/, logs/ and pins/ go")
    return ap.parse_args(argv)


def run(a, pins=None) -> int:
    try:
        if a.cmd == "block":
            return cmd_block(a)
        if a.cmd == "product":
            return cmd_product(a, pins)
        if a.cmd == "table":
            return cmd_table(a, pins)
        return cmd_chain(a)
    except Stop as e:
        print(f"[STOP] {e}", file=sys.stderr, flush=True)
        return 1


def main(argv=None) -> int:
    return run(build_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
