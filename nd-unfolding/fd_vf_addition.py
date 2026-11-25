#!/usr/bin/env python3
"""V_F's adoption into the 16-cell reported covariance (state/measurement-paper/5d-community-20261024/
FD-VF-ADDITION-DECLARATION.md; DECISION-20261125 section 3): dF = V_F - C_e added to every matrix that carries C_e,
so the reported covariance becomes C_rep,F = V_F + C_model_abs + C_resp + C_PL5D = C_rep + dF, and the arm without
the run-period block C_total + C_resp + DeltaC_e.

V_F = L C_e L^T is B5D's fluctuation block (blocks5d-20261124/record/V_F.csv), built on the with-block data product's
C_e. The bound tools take one extra block under any key and name; this module writes the blocks and drives them.

Subcommands:
* ``block``    vf_block.npz and vf_block.json from committed files only: dF, the three extra blocks dF (F0, graded
               against C_total), C_resp + DeltaC_e (without C_PL5D) and C_resp + C_PL5D + DeltaC_e (reported), and the two revised
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
import io
import json
import math
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
    "DeltaC_e": "DeltaC_e",
    "C_resp_plus_DeltaC_e": "C_resp + DeltaC_e",
    "C_resp_plus_C_PL5D_plus_DeltaC_e": "C_resp + C_PL5D + DeltaC_e",
}
SIDE_KEY = {"with": "C_resp_plus_C_PL5D_plus_DeltaC_e", "nopl": "C_resp_plus_DeltaC_e"}
REPORTED_F = "C_total_plus_C_resp_plus_C_PL5D_plus_DeltaC_e"
WITHOUT_F = "C_total_plus_C_resp_plus_DeltaC_e"
VF_BLOCK_NPZ = "cef8460a1dcc0db64f536af0099db1e1523ed2601d5c8ecc682afc0f9440c99b"   # vf_block.npz (no code digest in it)
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
    "block": "DeltaC_e = C_e^infl - C_e, the covariance increment; C_e^infl = L C_e L^T is C_e with its eigenvalue "
             "ranks 1-4, 5-8 and 9-16 rescaled by the applied variance multipliers phi_j (B5D's fluctuation block, "
             "V_F in its build records: blocks5d-20261124/RECEIPT.md), adopted into the reported covariance "
             "C_rep = C_e^infl + C_model + C_resp + C_PL,5D by DECISION-20261125 section 3, with A1 section 4's caveat: "
             "the multiplier measures the toy spread relative to LL5D's rebuilt reference block",
    "not_citable_for": ["a validated size for C_e^infl", "a coverage or calibration statement"],
}
report, Stop = A.report, A.Stop


def load_npz_bytes(raw: bytes) -> dict:
    """An npz decoded from the bytes whose digest was checked (never reopened by path)."""
    with np.load(io.BytesIO(raw), allow_pickle=False) as z:
        return {k: np.asarray(z[k], float) for k in z.files}


def same_bits(a, b) -> bool:
    """Literal identity: the same dtype, shape and bytes (np.array_equal reads -0.0 as 0.0 and coerces dtypes)."""
    a, b = np.asarray(a), np.asarray(b)
    return a.dtype == b.dtype and a.shape == b.shape and a.tobytes() == b.tobytes()


def symmetric(M: np.ndarray, tol: float = TOL) -> bool:
    return float(np.abs(M - M.T).max()) <= tol * float(np.abs(M).max())


# ---------------------------------------------------------------- block

def build_block(VF: np.ndarray, L: np.ndarray, Ce: np.ndarray, dp: dict, cpl: dict) -> dict:
    """V1-V3 on the inputs, then dF and the blocks; returns the npz arrays in their written order."""
    f = np.array(dp["f"], float)
    mats = {k: np.array(dp["matrices"][k], float) for k in
            ("C_e", "C_model_abs", "C_resp", "C_PL5D", "C_total_plus_C_resp", "C_total_plus_C_resp_plus_C_PL5D")}
    report("V1", "V_F (C_e^infl), L and C_e are finite 16 x 16 matrices; f is 16 positive cells",
           all(M.shape == (N, N) and bool(np.all(np.isfinite(M))) for M in (VF, L, Ce))
           and f.shape == (N,) and bool(np.all(f > 0)))
    report("V1", "the C_e CSV is the with-block data product's C_e, bit for bit", same_bits(Ce, mats["C_e"]))
    report("V1", "the cpl block's f, C_resp and C_PL5D are the data product's, bit for bit",
           same_bits(cpl["f"], f) and same_bits(cpl["C_resp"], mats["C_resp"])
           and same_bits(cpl["C_PL5D"], mats["C_PL5D"]))
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
    blocks = {"DeltaC_e": dF, "C_resp_plus_DeltaC_e": mats["C_resp"] + dF, "C_resp_plus_C_PL5D_plus_DeltaC_e": cpl[X_PL] + dF}
    wo_f = mats["C_total_plus_C_resp"] + dF
    rep_f = mats["C_total_plus_C_resp_plus_C_PL5D"] + dF
    report("V3", "the reported matrix is V_F + C_model_abs + C_resp + C_PL5D, to 1e-12", float(np.abs(
        rep_f - (VF + mats["C_model_abs"] + mats["C_resp"] + mats["C_PL5D"])).max()) <= TOL * scale)
    report("V3", "the matrix without C_PL5D is V_F + C_model_abs + C_resp, to 1e-12", float(np.abs(
        wo_f - (VF + mats["C_model_abs"] + mats["C_resp"])).max()) <= TOL * scale)
    for k, M in (("reported", rep_f), ("without C_PL5D", wo_f)):
        report("V3", f"the revised matrix {k} is positive definite",
               bool(np.linalg.eigvalsh((M + M.T) / 2 / np.outer(f, f)).min() > 0))
    return {"f": f, "C_e": Ce, "C_e_infl": VF, **blocks, WITHOUT_F: wo_f, REPORTED_F: rep_f}


def block_inputs(repo: Path) -> tuple:
    """V0: every input read once and checked against its pin; returns (V_F, L, C_e, the data product, the cpl block)."""
    raw = {k: A.pinned(repo / SOURCES[k], PINS[k], k, "V0") for k in PINS}
    VF = F.read_matrix_csv(raw["v_f_csv"].decode())
    Ce = F.read_matrix_csv(raw["c_e_csv"].decode())
    rec = json.loads(raw["blocks5d_json"])
    report("V0", "the B5D record names this V_F", rec["matrices_sha256"]["V_F.csv"] == PINS["v_f_csv"])
    VFj, L = (np.array(rec["fluctuation"][k], float) for k in ("V_F", "L"))
    report("V0", "the record's V_F is the CSV's, bit for bit", same_bits(VFj, VF))
    return VF, L, Ce, json.loads(raw["data_product_cpl"]), load_npz_bytes(raw["cpl_block_npz"])


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
                                  for k in ("C_e", "C_e_infl", *BLOCKS, WITHOUT_F, REPORTED_F)},
               "inputs_sha256": dict(PINS), "inputs": dict(SOURCES),
               "code_sha256": {"fd_vf_addition.py": A.sha256(Path(__file__).resolve()),
                               "fd_cpl_addition.py": A.sha256(Path(A.__file__).resolve())}}
    A.write_atomic(out_json, (json.dumps(readout, indent=1, allow_nan=False) + "\n").encode())
    print(json.dumps({"wrote": str(out_npz), "sha256": h}), flush=True)
    print(json.dumps({"wrote": str(out_json), "sha256": A.sha256(out_json)}), flush=True)
    return 0


# ---------------------------------------------------------------- product

PRODUCT_STEM = "fd_data_product_vf"
PRODUCT_MATRICES = ("C_e", "C_e_infl", "DeltaC_e", "C_model_abs", "C_resp", "C_PL5D", WITHOUT_F, REPORTED_F)
PRODUCT_INPUTS = ("data_product", "block_npz", "block_json", "g_readout")
REPORTED_NAME = f"C_total + {BLOCKS[SIDE_KEY['with']]}"         # C_total + C_resp + C_PL5D + DeltaC_e


def product_labels(dp: dict) -> dict:
    return {"what": "data product with C_e^infl adopted: the 5D result's reported covariance, with and without C_PL5D",
            "covariance": f"{REPORTED_NAME} = C_e^infl + C_model_abs + C_resp + C_PL5D = C_rep, the reported covariance "
                          f"(FD-VF-ADDITION-DECLARATION.md section 1 and amendment A2), DeltaC_e = C_e^infl - C_e; C_total "
                          f"stays the baseline subtotal C_e + C_model_abs; {WITHOUT_F} is the "
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
    report("K2", "the block's f and C_e are the data product's, bit for bit", same_bits(blk["f"], f)
           and same_bits(blk["C_e"], old["C_e"]))
    dF = blk["DeltaC_e"]
    scale = float(np.abs(np.diag(blk[REPORTED_F])).max())
    report("K2", "DeltaC_e is the block's C_e_infl - C_e, bit for bit", same_bits(dF, blk["C_e_infl"] - blk["C_e"]))
    report("K2", "the revised matrices are the committed ones + dF, to 1e-12",
           float(np.abs(blk[REPORTED_F] - (old[A.REPORTED] + dF)).max()) <= TOL * scale
           and float(np.abs(blk[WITHOUT_F] - (old["C_total_plus_C_resp"] + dF)).max()) <= TOL * scale)
    sig = np.sqrt(np.diag(blk[REPORTED_F])) / f
    report("K3", "Stage G's predictions are its declared five, in order, on their declared cells",
           [(p["name"], p["cells"]) for p in gr["predictions"]] == declared_cells()
           and all(len(p["sigma_total_over_f"]) == len(p["cells"]) for p in gr["predictions"]))
    for p in gr["predictions"]:
        idx = [CELLS.index(c) for c in p["cells"]]
        report("K3", f"{p['name']}: Stage G's sigma_total_over_f is sqrt(diag(C_rep,F))/f to 1e-12 and its covariance "
                     f"is {REPORTED_NAME}", F.worst(np.array(p["sigma_total_over_f"]), sig[idx]) <= TOL
               and p["reported_covariance"] == REPORTED_NAME)
    mats = {"C_e": old["C_e"], "C_e_infl": blk["C_e_infl"], "DeltaC_e": dF, "C_model_abs": old["C_model_abs"],
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
    p = build_product(dp, load_npz_bytes(raw["block_npz"]), bj, gr, pins)
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
    files[f"{PRODUCT_STEM}.json"] = json.dumps(readout, indent=1, allow_nan=False) + "\n"
    out = Path(a.out_dir).resolve()
    stage = out.with_name(out.name + ".staging")
    report("K0", "neither the output directory (unless empty) nor its staging directory exists",
           not stage.exists() and (not out.exists() or not any(out.iterdir())))
    stage.mkdir(parents=True)
    for n, text in files.items():
        A.write_atomic(stage / n, text.encode())
    check_written(stage, files, p, dp)                 # a refusal leaves only the staging directory, never the outputs
    if out.exists():
        out.rmdir()
    os.rename(stage, out)
    for n in files:
        print(json.dumps({"wrote": str(out / n), "sha256": A.sha256(out / n)}), flush=True)
    return 0


def check_written(out: Path, files: dict, p: dict, dp: dict) -> None:
    """K6 on the files as written: each is its text's bytes and the JSON's files_sha256; the JSON's f, matrices,
    correlation and relative sigma, and the cells CSV's f and sigma columns, read back bit for bit."""
    for n, text in files.items():
        report("K6", f"{n}: the file on disk is the bytes written", (out / n).read_bytes() == text.encode())
    js = json.loads((out / f"{PRODUCT_STEM}.json").read_bytes())
    report("K6", "every CSV's sha256 is the JSON's files_sha256", js["files_sha256"] == {
        n: A.sha256(out / n) for n in files if n.endswith(".csv")})
    report("K6", "the JSON's f, matrices, correlation and relative sigma read back bit for bit",
           np.array_equal(np.array(js["f"]), p["f"]) and np.array_equal(np.array(js["correlation"]), p["correlation"])
           and all(np.array_equal(np.array(js["matrices"][k]), p["matrices"][k]) for k in PRODUCT_MATRICES)
           and all(np.array_equal(np.array(js["relative_sigma"][k]), p["relative_sigma"][k]) for k in PRODUCT_MATRICES))
    import csv as _csv
    rows = list(_csv.DictReader(io.StringIO((out / f"{PRODUCT_STEM}_cells.csv").read_text())))
    report("K6", "the cells CSV lists R00-R15 with f and every relative sigma, bit for bit",
           [r["cell"] for r in rows] == CELLS and same_bits(np.array([float(r["f"]) for r in rows]), p["f"])
           and all(same_bits(np.array([float(r[f"rel_sigma_{k}"]) for r in rows]), p["relative_sigma"][k])
                   for k in PRODUCT_MATRICES))
    report("K6", "the cells CSV's box edges are the committed product's cells", all(
        [float(r[f"{ax}_{e}"]) for e in ("lo", "hi")] == [float(v) for v in c["box"][ax]]
        for r, c in zip(rows, dp["cells"]) for ax in c["box"]))


def deposit_variant(pins: dict) -> DC.Variant:
    """The deposit candidate's variant for the reported matrix with V_F, with the chain's pins of the V_F data product
    and Stage G readout."""
    labels = {**DC.LABELS,
              "what": "the 5D result on its sixteen reporting cells R00-R15: cell definitions, the measured vector f, "
                      f"the reported covariance C_rep = {REPORTED_NAME}, and its correlation matrix",
              "covariance": f"{REPORTED_NAME} = C_e^infl + C_model_abs + C_resp + C_PL5D, DeltaC_e = C_e^infl - C_e (the data "
                            f"product's {REPORTED_F}). The paper's chi2 for a prediction g on its cells c is "
                            "d^T (C + V_g)^-1 d with d = f - g, C this covariance on c, and V_g = diag of g's own "
                            "finite-MC variance, ndf n; its shape-only chi2 adds 100 f f^T (f on c, absolute units) to "
                            "C + V_g, ndf n - 1; g and V_g are the prediction's, not part of the measurement",
              "block": LABELS["block"],
              "not_citable_for": f"{DC.LABELS['not_citable_for']}; {'; '.join(LABELS['not_citable_for'])}"}
    return DC.Variant(key=REPORTED_F, name=REPORTED_NAME, labels=labels,
                      pins={"data_product": pins["data_product"], "g_readout": pins["g_readout"]},
                      sources={"data_product": f"fd/with-vf/data-product/{PRODUCT_STEM}.json",
                               "g_readout": "fd/with-vf/readout/S/vf-with/fd_g_readout.json"})


# ---------------------------------------------------------------- strict reading and comparison

def _reject_constant(name: str):
    raise Stop("R", f"a readout holds the non-finite constant {name}")


def load_strict(raw: bytes) -> dict:
    """A readout decoded with NaN and Infinity refused (the writers use allow_nan=False)."""
    return json.loads(raw, parse_constant=_reject_constant)


def finite_mismatch(old, new) -> list:
    """Every numeric leaf at the same path whose finiteness or infinite sign differs (fd_cpl_addition.same_number
    reads inf against a finite number as equal)."""
    lo = dict(A.numeric_leaves(old))
    bad = []
    for p, y in A.numeric_leaves(new):
        x = lo.get(p)
        if isinstance(x, float) or isinstance(y, float):
            fx = x is None or isinstance(x, bool) or math.isfinite(x)
            fy = y is None or isinstance(y, bool) or math.isfinite(y)
            if fx != fy or (not fx and x != y):
                bad.append(f"finite {p}: {x!r} vs {y!r}")
    return bad


def compare(old: dict, new: dict, exclude, strings: bool) -> list:
    return (A.compare_numbers(old, new, exclude) + finite_mismatch(old, new)
            + (A.compare_strings(old, new, exclude) if strings else []))


# ---------------------------------------------------------------- table

def rename_vf(key: str) -> str:
    """A V_F readout's key, as the OLD readout spells it: keys built from the block's name lose its " + DeltaC_e"."""
    return key.replace(" + DeltaC_e", "")


def paired(old, new, path="", unpaired=None):
    """(path, OLD, V_F) for every numeric leaf at the same place in both readouts, keys renamed; every leaf or
    container that has no partner (a missing key, a list of another length) is appended to ``unpaired``."""
    unpaired = [] if unpaired is None else unpaired
    if isinstance(old, dict) and isinstance(new, dict):
        nk = {rename_vf(k): k for k in new}
        for k in sorted(set(old) | set(nk)):
            if k in old and k in nk:
                yield from paired(old[k], new[nk[k]], f"{path}/{k}", unpaired)
            else:
                unpaired.append(f"{path}/{k} ({'OLD' if k in old else 'V_F'} only)")
    elif isinstance(old, list) and isinstance(new, list):
        if len(old) != len(new):
            unpaired.append(f"{path} (lengths {len(old)} and {len(new)})")
            return
        for i, (x, y) in enumerate(zip(old, new)):
            yield from paired(x, y, f"{path}/{i}", unpaired)
    elif not isinstance(old, (dict, list, str)) and not isinstance(new, (dict, list, str)):
        yield path, old, new
    elif isinstance(old, str) != isinstance(new, str) or isinstance(old, (dict, list)) != isinstance(new, (dict, list)):
        unpaired.append(f"{path} (types {type(old).__name__} and {type(new).__name__})")


def identities(o: dict, n: dict, k: str) -> None:
    """T before any pairing: every list of named records (predictions, truths, comparisons, modes, ...) holds the
    same names, in the same order, on the same cells, on both sides."""
    def walk(a, b, path):
        if isinstance(a, dict) and isinstance(b, dict):
            for key in a:
                if rename_vf(key) == key and key in b:
                    walk(a[key], b[key], f"{path}/{key}")
        elif isinstance(a, list) and isinstance(b, list) and a and all(isinstance(x, dict) and "name" in x for x in a):
            ida = [(x.get("name"), x.get("cells")) for x in a]
            idb = [(rename_vf(x["name"]) if isinstance(x.get("name"), str) else x.get("name"), x.get("cells"))
                   if isinstance(x, dict) else None for x in b]
            report("T", f"{k}{path}: the named records are the same, in the same order, on the same cells",
                   ida == idb, f"{ida[:3]} / {idb[:3]}")
            for x, y in zip(a, b):
                walk(x, y, f"{path}/{x.get('name')}")
    walk(o, n, "")


def listed(r: dict) -> list:
    return sorted(x["truth"] for x in r["triggers"]["listed"])


def vf_matrix(old_name: str, stage_g: bool) -> str:
    """The matrix a V_F readout names, from its OLD readout's: dF added to the block (Stage G: before V_g)."""
    return old_name.replace(" + V_g", " + DeltaC_e + V_g", 1) if stage_g else old_name + " + DeltaC_e"


def block_label(r: dict) -> dict:
    a = r.get("argv") or []
    return {f: (a[a.index(f) + 1] if f in a else None) for f in ("--extra-block-key", "--extra-block-name")}


def curated(old: dict, new: dict) -> dict:
    """The named rows: each readout's block, each F readout's listing and per-truth grades (F0's sigma, base OLD and
    revised V_F, paired by name), each Stage G prediction's chi2 and p on the same cells; each side names its matrix
    (the V_F side the OLD side's with dF added)."""
    out = {"blocks": {}, "listings": {}, "truths": {}, "stage_g": {}, "f0_sigma": None}
    for k in old:
        o, n = old[k], new[k]
        identities(o, n, k)
        out["blocks"][k] = {"old": block_label(o), "vf": block_label(n),
                            "sens_unchanged": [(o.get("sens") or {}).get("unchanged"), (n.get("sens") or {}).get("unchanged")]}
        if "triggers" in o:
            report("T", f"{k}: the truths are the same, in the same order, on both sides",
                   bool(o["truths"]) and [t["name"] for t in o["truths"]] == [t["name"] for t in n["truths"]])
            for to, tn in zip(o["truths"], n["truths"]):
                report("T", f"{k} {to['name']}: the V_F grade matrix is the OLD one with dF added, on the same cells",
                       tn["grade_matrix"] == vf_matrix(to["grade_matrix"], False)
                       and tn["grade"]["cells"] == to["grade"]["cells"],
                       f"{to['grade_matrix']!r} / {tn['grade_matrix']!r}")
            out["listings"][k] = {"old": listed(o), "vf": listed(n), "newly_listed": sorted(set(listed(n)) - set(listed(o))),
                                  "cleared": sorted(set(listed(o)) - set(listed(n)))}
            out["truths"][k] = [{"truth": to["name"], "graded": to["graded"],
                                 "old": {**{q: to["grade"][q] for q in ("chi2", "p")},
                                         "cells_abs_z_gt_2": to["grade"]["cells_abs_z_gt_2"]},
                                 "vf": {**{q: tn["grade"][q] for q in ("chi2", "p")},
                                        "cells_abs_z_gt_2": tn["grade"]["cells_abs_z_gt_2"]},
                                 "grade_matrix": {"old": to["grade_matrix"], "vf": tn["grade_matrix"]}}
                                for to, tn in zip(o["truths"], n["truths"])]
            if k == "F0":
                out["f0_sigma"] = {"old": o["relative_sigma"], "vf": n.get(f"relative_sigma_plus_{BLOCKS['DeltaC_e']}")}
                report("T", "F0: the V_F readout carries its revised sigma (relative_sigma_plus_DeltaC_e)",
                       out["f0_sigma"]["vf"] is not None)
        elif k.endswith("/g"):
            report("T", f"{k}: the predictions are the same, in the same order, on the same cells, on both sides",
                   bool(o["predictions"]) and [(p["name"], p["cells"]) for p in o["predictions"]]
                   == [(p["name"], p["cells"]) for p in n["predictions"]])
            for po, pn in zip(o["predictions"], n["predictions"]):
                for kind in ("total", "shape_only"):
                    report("T", f"{k} {po['name']} {kind}: the OLD matrix is C_total + its block + V_g, and the V_F "
                                "matrix is it with dF added",
                           po[kind]["matrix"].startswith("C_total + ") and " + V_g" in po[kind]["matrix"]
                           and pn[kind]["matrix"] == vf_matrix(po[kind]["matrix"], True),
                           f"{po[kind]['matrix']!r} / {pn[kind]['matrix']!r}")
            out["stage_g"][k] = [{"prediction": po["name"], "kind": kind, "ndf": po[kind]["ndf"],
                                  "old": {q: po[kind][q] for q in ("chi2", "p", "matrix")},
                                  "vf": {q: pn[kind][q] for q in ("chi2", "p", "matrix")}}
                                 for po, pn in zip(o["predictions"], n["predictions"]) for kind in ("total", "shape_only")]
    return out


def table_md(c: dict, counts: dict, unpaired: dict) -> str:
    L = ["# V_F's adoption: every Phase 1 readout, OLD and V_F", "", LABELS["block"] + ".", "",
         "## Listings (p < 0.01 or any |z| > 2)", "", "| readout | OLD | V_F | newly listed | cleared |",
         "|---|---|---|---|---|"]
    L += [f"| {k} | {', '.join(v['old']) or 'none'} | {', '.join(v['vf']) or 'none'} | "
          f"{', '.join(v['newly_listed']) or '-'} | {', '.join(v['cleared']) or '-'} |" for k, v in c["listings"].items()]
    L += ["", "## Each readout's block (argv)", "", "| readout | OLD key | V_F key |", "|---|---|---|"]
    L += [f"| {k} | {v['old']['--extra-block-key'] or 'none'} | {v['vf']['--extra-block-key'] or 'none'} |"
          for k, v in c["blocks"].items()]
    for k, rows in c["stage_g"].items():
        L += ["", f"## Stage G, {k}", "", "| prediction | kind | ndf | chi2 OLD | p OLD | chi2 V_F | p V_F |",
              "|---|---|---:|---:|---:|---:|---:|"]
        L += [f"| {r['prediction']} | {r['kind']} | {r['ndf']} | {r['old']['chi2']:.3f} | {r['old']['p']:.3g} | "
              f"{r['vf']['chi2']:.3f} | {r['vf']['p']:.3g} |" for r in rows]
        L += ["", "Matrices: " + "; ".join(sorted({f"OLD {r['old']['matrix']} / C_e^infl {r['vf']['matrix']}" for r in rows}))]
    for k, rows in c["truths"].items():
        L += ["", f"## {k}: each truth", "", "| truth | graded | chi2 OLD | p OLD | cells OLD | chi2 V_F | p V_F | "
              "cells V_F |", "|---|---|---:|---:|---|---:|---:|---|"]
        L += [f"| {t['truth']} | {t['graded']} | {t['old']['chi2']:.4g} | {t['old']['p']:.3g} | "
              f"{' '.join(t['old']['cells_abs_z_gt_2']) or '-'} | {t['vf']['chi2']:.4g} | {t['vf']['p']:.3g} | "
              f"{' '.join(t['vf']['cells_abs_z_gt_2']) or '-'} |" for t in rows]
        L += ["", "Grade matrices: " + "; ".join(sorted({f"OLD {t['grade_matrix']['old']} / C_e^infl {t['grade_matrix']['vf']}"
                                                         for t in rows}))]
    L += ["", "## Every other number", "", "`fd_vf_table.json` `leaves` pairs every numeric leaf of each readout:", ""]
    L += [f"- {k}: {n} paired leaves, {len(unpaired[k])} without a partner" for k, n in counts.items()]
    L += ["", f"NOT CITABLE FOR: {'; '.join(LABELS['not_citable_for'])}. Readings go to the director first.", ""]
    return "\n".join(L)


def cmd_table(a, pins: dict | None) -> int:
    """``pairs``: a JSON list of [label, OLD path, OLD pin, V_F path, V_F pin], the OLD pins the declared ones and the
    V_F pins the digests the chain recorded when each file was written; ``pins`` must be the same map."""
    if pins is None:
        raise Stop("T", "table runs in the chain only: the readouts' pins are the declared and recorded ones")
    out_json, out_md = a.out_dir / "fd_vf_table.json", a.out_dir / "fd_vf_table.md"
    report("T", "no output exists (no overwrite)", not out_json.exists() and not out_md.exists())
    pairs = json.loads(a.pairs.read_bytes())
    report("T", "every pair's pins are the chain's", bool(pairs) and all(
        pins.get(po) == ho and pins.get(pn) == hn for _, po, ho, pn, hn in pairs))
    old, new = {}, {}
    for label, po, ho, pn, hn in pairs:
        old[label] = load_strict(A.pinned(Path(po), ho, f"{label} OLD", "T"))
        new[label] = load_strict(A.pinned(Path(pn), hn, f"{label} V_F", "T"))
    c = curated(old, new)
    leaves, unpaired = {}, {}
    for k in old:
        unpaired[k] = []
        leaves[k] = [[p, x, y] for p, x, y in paired(old[k], new[k], "", unpaired[k])]
    counts = {k: len(v) for k, v in leaves.items()}
    table = {"schema": "fd-vf-table/1", "labels": {"what": "every Phase 1 readout's numbers, OLD and with V_F",
                                                   **LABELS}, "controls_passed": ["T"], "curated": c,
             "leaves": leaves, "leaf_counts": counts, "unpaired": unpaired, "inputs_sha256": dict(pins),
             "code_sha256": {"fd_vf_addition.py": A.sha256(Path(__file__).resolve())}, "argv": list(sys.argv)}
    a.out_dir.mkdir(parents=True, exist_ok=True)
    A.write_atomic(out_json, (json.dumps(table, indent=1, allow_nan=False) + "\n").encode())
    A.write_atomic(out_md, table_md(c, counts, unpaired).encode())
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
_CE = f"{FD}/fd/gencmp-e/rerun1/chain"
OLD_E = {
    "with": {"g": (f"{_CE}/chdefs/with/readout/fd_g_readout.json",
                   "a19009e0bd83b9bb8f9ad65fb65804e6f62c8953310103fbfe6fce5f84995875"),
             "g_diag": (f"{_CE}/chdefs/with/readout/fd_g_diag_readout.json",
                        "522bfafa3016fadbd62c72f9f34153e17cd514a3b06acf282030d550f5dc1855"),
             "g_followup": (f"{_CE}/chdefs/with/readout/fd_g_followup_readout.json",
                            "586cd74105d0837c69290d0370f6327cda75a92ee31f2d437658c626b4ab1e8f"),
             "g_sens2": (f"{_CE}/chdefs/with/readout/fd_g_sens2_readout.json",
                         "4bc21dfda9c49762227fc4c486ee9decc349863aaea095f94347ad4b963d4513"),
             "flux_boot": (f"{_CE}/chdefs/with/readout/fd_flux_boot_readout.json",
                           "5bb475eada29d270f93bf124251b98152a437280fa684429fe20e15d940f2e5d")},
    "nopl": {"g": (f"{_CE}/chdefs/nopl/readout/fd_g_readout.json",
                   "d9a1ce38040b8cd3c2a6deb787f8a7dc90aca5c4d3a5a8d25a60b7f8ab582ed9"),
             "g_diag": (f"{_CE}/chdefs/nopl/readout/fd_g_diag_readout.json",
                        "4e77966e93bd21d53ae777f2af02f00963d9eec45372997fc7af5fd45d2a099f"),
             "g_followup": (f"{_CE}/chdefs/nopl/readout/fd_g_followup_readout.json",
                            "748f3af6e7fa54f916d73295b078e5b8a768a8abe024e848a55d9b90f9a806ac"),
             "g_sens2": (f"{_CE}/chdefs/nopl/readout/fd_g_sens2_readout.json",
                         "6626cb7347793b50a4431307244d50e3e863202c6ac920d659d10ec691e7f7e9"),
             "flux_boot": (f"{_CE}/chdefs/nopl/readout/fd_flux_boot_readout.json",
                           "24ff27f90067864292ef93bd018f5040548f90118368b3cf03fc3760377661ed")},
}
# the figures the note shows: E-A2's redraw of the with arm at the current fd_g_figures.py (5d2916cb). The nopl arm's
# committed figures predate E-A1/E-A2's legends and are drawn by no current tool; the note shows none of them, so the
# chain draws figures in the with arms only.
OLD_E_FIG = f"{_CE}/chdefs/with/figures-a2"
OLD_E_FIG_SUMS = f"{FD}/fd/gencmp-e/a2/run/receipts/figures-a2.sha256"
CHDEFS_SPEC = f"{_CE}/pins/predictions-chdefs.json"
CHDEFS_SUMS = "a45438fa06565d647bf496b4c2a8333a2e0dc011dd71afd4bb63f377732c9aa0"     # rerun1/pred/SHA256SUMS
OLD_DEP = f"{FD}/fd/with-cpl/deposit-candidate"
CPL_BLOCK_JSON = "4023746e3a819e8cc8348c457d7dc1ee55df66eaa5f5f68082824b9df27cabd6"
R_EXCLUDE = ("/argv", "/code_sha256", "/code", "/versions", "/extra_block/file")
FIG_EXCLUDE = A.FIG_EXCLUDE
F_TOOLS = ("fd_f0_regrade",)                       # the tools that take no --extra-block-role

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
CLI_ONLY = "fd_g_figures_check"


class Chain(A.Chain):
    """fd_cpl_addition's Chain, with one BOOT for the pins, the prediction set and either deposit variant; the
    figures check (main() only) runs as its CLI, as fd_gencmp_e's chain runs it."""

    def __init__(self, paths, receipt: Path, steps: list, preds_file: Path | None = None):
        super().__init__(paths, receipt)
        self.steps, self.preds_file = steps, preds_file

    def run(self, name, arm, tool, argv, outputs, timeout, pins=None, variant=""):
        log = self.p.BA / "logs" / f"{arm}-{name}"
        preds = "-" if self.preds_file is None or tool == CLI_ONLY else str(self.preds_file)
        if pins is None or tool == CLI_ONLY:
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


REQUIRED_REFS = {"g_sens2": ("g_followup_readout",)}       # duplicate upstream references a readout must carry


def check_c(c: Chain, label: str, path: Path, vf_sha: str, key: str, upstream: dict, role: bool,
            required: tuple = ()) -> None:
    """C, right after a V_F step: its recorded argv names vf_block.npz's sha256, this member's key and name (and role
    adopted, or none for the F tools); every digest field it records for the block is that sha256 (at least one); and
    every upstream readout's sha256, where it is recorded (inputs_sha256, referenced), is the one the chain wrote."""
    r = load_strict(path.read_bytes())
    a = r.get("argv") or []

    def fl(f):
        return a[a.index(f) + 1] if a.count(f) == 1 else None
    xbr, ins, ref = r.get("extra_block") or {}, r.get("inputs_sha256") or {}, r.get("referenced") or {}
    digests = [d.get(k) for d, k in ((xbr, "sha256"), (ins, "extra_block")) if k in d]
    ok = (fl("--extra-block-sha256") == vf_sha and fl("--extra-block-key") == key and fl("--extra-block-name") == BLOCKS[key]
          and (fl("--extra-block-role") == "adopted" if role else "--extra-block-role" not in a)
          and bool(digests) and all(v == vf_sha for v in digests)
          and xbr.get("key", key) == key and xbr.get("name", BLOCKS[key]) == BLOCKS[key]
          and (xbr.get("role", "adopted") == "adopted" if role else "role" not in xbr)
          and all(f in ref for f in required)
          and all(ins.get(f) == h for f, h in upstream.items())
          and all(ref.get(f, h) == h for f, h in upstream.items()))
    c.check(f"C {label}: argv, the block's digests, key, name and role, and each upstream digest are as written", ok,
            {"argv_block": [fl(f) for f in ("--extra-block-sha256", "--extra-block-key", "--extra-block-name",
                                            "--extra-block-role")], "digests": digests,
             "upstream": {f: [ins.get(f), ref.get(f)] for f in upstream}})


def check_table(c: Chain, label: str, readout: Path, npz: Path, want: str) -> None:
    """The experiment table: the npz the step wrote is the one its readout names, and the table it must be."""
    r = load_strict(readout.read_bytes())
    h = A.sha256(npz)
    c.check(f"R {label}: the experiment table is the readout's table_sha256 and the declared table",
            r.get("table_sha256") == h == want, {"npz": h, "readout": r.get("table_sha256"), "want": want})


def run_f0(c: Chain, arm: str, vf: dict) -> tuple[Path, Path]:
    p = c.p
    W = p.BA / "S" / arm
    (W / "readout").mkdir(parents=True)
    out, npz = W / "readout" / "fd_f0_readout.json", W / "fd_f0_experiments.npz"
    xb0 = [] if arm == "old-f0" else A.extra(vf["npz"], vf["sha"], "DeltaC_e", BLOCKS["DeltaC_e"], role=False)
    c.run("f0", arm, "fd_f0_regrade", [*p.f0(), *xb0, "--out-json", str(out), "--out-npz", str(npz)], [out, npz],
          A.TIMEOUT["f0b"])
    if arm != "old-f0":
        check_c(c, f"{arm} f0", out, vf["sha"], "DeltaC_e", {}, role=False)
    return out, npz


def run_s(c: Chain, arm: str, vf: dict, f0b_old: tuple[Path, str] | None) -> dict:
    """F0b, F1 and Stage G on the original predictions for one arm. F1 reads ``f0b_old`` (an OLD arm: the committed
    F0b, as its pinned readout was made) or this arm's F0b. A V_F step's C runs as soon as it returns."""
    p = c.p
    xb, xb0 = arm_flags(p, arm, vf), arm_flags(p, arm, vf, role=False)
    vfarm = arm.startswith("vf-")
    key = SIDE_KEY[arm.split("-")[1]]
    W = p.BA / "S" / arm
    (W / "readout").mkdir(parents=True)
    out = {k: W / "readout" / Path(A.COMMITTED[k][0]).name for k in S_STEPS}
    out["f0b_npz"], out["f1_npz"] = W / "fd_f0b_experiments.npz", W / "fd_f1_experiments.npz"
    c.run("f0b", arm, "fd_f0_regrade", A.step_argv(p, "f0b", xb, xb0, {}, out["f0b"], "with"),
          [out["f0b"], out["f0b_npz"]], A.TIMEOUT["f0b"])
    if vfarm:
        check_c(c, f"{arm} f0b", out["f0b"], vf["sha"], key, {}, role=False)
    up = ({"f0b": f0b_old[0], "f0b_sha256": f0b_old[1]} if f0b_old else
          {"f0b": out["f0b"], "f0b_sha256": A.sha256(out["f0b"])})
    c.run("f1", arm, "fd_f0_regrade", A.step_argv(p, "f1", xb, xb0, up, out["f1"], "with"), [out["f1"], out["f1_npz"]],
          A.TIMEOUT["f1"])
    if vfarm:
        check_c(c, f"{arm} f1", out["f1"], vf["sha"], key, {"f0b_readout": up["f0b_sha256"]}, role=False)
    c.run("g", arm, "fd_g_compare", A.step_argv(p, "g", xb, xb0, up, out["g"], "with"), [out["g"]], A.TIMEOUT["g"])
    if vfarm:
        check_c(c, f"{arm} g", out["g"], vf["sha"], key, {}, role=True)
    return out


def run_e(c: Chain, arm: str, vf: dict, f0b: tuple[Path, str]) -> dict:
    """The chdefs set for one arm: Stage G, G-DIAG, G-FOLLOWUP, G-SENS2 and the flux bootstrap. In an OLD arm each
    downstream step reads the COMMITTED upstream readouts, pinned by their declared digests (fd_gencmp_e's old set:
    each readout records its upstream's digest, so R can hold only on the committed upstream); in a V_F arm each reads,
    and is pinned to, the readout the step before wrote, and its C runs as soon as it returns. Then, in the with arms
    only, the three figures (with ``f0b``) and their check."""
    import fd_g_figures as FG
    import fd_gencmp_e as E
    p = c.p
    kind, side = arm.split("-")
    xb = arm_flags(p, arm, vf)
    base = {"s5p_sums": CHDEFS_SUMS}                      # the recorded digest, checked once before any step
    W = p.BA / "E" / arm
    (W / "readout").mkdir(parents=True)
    out = {k: W / "readout" / Path(A.COMMITTED[k][0]).name for k in E_STEPS}
    H, up = {}, {}
    if kind == "old":
        src = {k: p.D / OLD_E[side][k][0] for k in E_STEPS}
        hsrc = {k: OLD_E[side][k][1] for k in E_STEPS}
    else:
        src, hsrc = up, H
    for k in E_STEPS:
        c.run(k, f"E-{arm}", A.TOOLS[k], A.step_argv(p, k, xb, xb, src, out[k], "with"), [out[k]], A.TIMEOUT[k],
              pins=E.step_pins(k, hsrc, base))
        H[k], up[k] = A.sha256(out[k]), out[k]
        if kind == "vf":
            check_c(c, f"E {arm} {k}", out[k], vf["sha"], SIDE_KEY[side],
                    {f: H[u] for f, u in A.UPSTREAM.get(k, {}).items()}, role=True, required=REQUIRED_REFS.get(k, ()))
    res = {"out": out, "H": H, "fig": None}
    if side != "with":
        return res
    fsrc, fh = {**src, "f0b": f0b[0]}, hsrc
    fig = W / "figures"
    name = A.NAME if kind == "old" else BLOCKS[SIDE_KEY["with"]]
    fargv = [*A.step_argv(p, "figures", xb, xb, fsrc, fig, "without"), "--reported-block-name", name,
             "--prediction-set", "gencmp-chdefs"]
    c.run("figures", f"E-{arm}", "fd_g_figures", fargv, [fig / f"{n}{e}" for n in A.FIG_NAMES for e in (".pdf", ".json")],
          75, pins={**FG.PINS, "g_readout": fh["g"], "g_diag_readout": fh["g_diag"], "g_followup_readout": fh["g_followup"],
                    "g_sens2_readout": fh["g_sens2"], "f0b_readout": f0b[1]})
    c.run("figures_check", f"E-{arm}", CLI_ONLY,
          [*A.step_argv(p, "figures_check", xb, xb, fsrc, fig, "with"), "--prediction-set", "gencmp-chdefs"], [], 75,
          pins={})
    res["fig"] = fig
    return res


def check_r(c: Chain, label: str, D: Path, rel: str, pin: str, new: Path, strings: bool) -> None:
    raw = (D / rel).read_bytes()
    c.check(f"R {label}: the committed readout is the pinned bytes", hashlib.sha256(raw).hexdigest() == pin, rel)
    bad = compare(load_strict(raw), load_strict(new.read_bytes()), R_EXCLUDE, strings)
    c.check(f"R {label}: structure, numbers and finiteness{' and strings' if strings else ''} are the committed "
            "readout's", not bad, bad[:20])


def check_r_figures(c: Chain, label: str, D: Path, fig: Path) -> None:
    """Each figure against E-A2's committed redraw: the committed files are E-A2's receipt bytes; the sidecar is
    the committed one but argv, code and versions; the PDF the same bytes."""
    sums = {ln.split()[1]: ln.split()[0] for ln in (D / OLD_E_FIG_SUMS).read_text().splitlines() if ln.strip()}
    for n in A.FIG_NAMES:
        for e in (".pdf", ".json"):
            c.check(f"R {label} figure {n}{e}: the committed file is E-A2's receipt bytes",
                    A.sha256(D / OLD_E_FIG / f"{n}{e}") == sums.get(f"{n}{e}"), f"{n}{e}")
        old = load_strict((D / OLD_E_FIG / f"{n}.json").read_bytes())
        new = load_strict((fig / f"{n}.json").read_bytes())
        bad = compare(old, new, FIG_EXCLUDE, True)
        c.check(f"R {label} figure {n}: the sidecar is the committed one but argv, code and versions; the PDF the same "
                "bytes", not bad and (fig / f"{n}.pdf").read_bytes() == (D / OLD_E_FIG / f"{n}.pdf").read_bytes(),
                bad[:20])


def declared_cells() -> list:
    """Stage G's five predictions, in order, each with its declared cells (fd_g_compare.PREDICTIONS; "gibuu" is
    GIBUU_CELLS), as a readout spells them."""
    import fd_g_compare as G
    return [(q["name"], CELLS if q["cells"] == "all" else [CELLS[i] for i in G.GIBUU_CELLS]) for q in G.PREDICTIONS]


def check_renderer(c: Chain, D: Path) -> None:
    """The figures' environment is E-A2's (figures-a2's sidecars), so control R's PDF comparison can hold."""
    import matplotlib
    want = load_strict((D / OLD_E_FIG / "fd_g_fig_modes.json").read_bytes())["versions"]
    have = {"python": sys.version.split()[0], "numpy": np.__version__, "matplotlib": matplotlib.__version__}
    c.check("C the renderer: python, numpy and matplotlib are E-A2's (figures-a2), so the PDFs can match byte for byte",
            bool(want) and all(have.get(k) == v for k, v in want.items()), {"have": have, "want": want})


def check_s(c: Chain, label: str, g: Path, f0b: Path | None, blk: dict, side: str) -> None:
    """S: the arm's reported sigma is sqrt(diag) of its own revised matrix, on Stage G's declared predictions and
    cells, and in F0b's revised sigma."""
    M = blk[REPORTED_F] if side == "with" else blk[WITHOUT_F]
    sig = np.sqrt(np.diag(M)) / blk["f"]
    gr = load_strict(g.read_bytes())
    have = [(q["name"], q["cells"]) for q in gr["predictions"]]
    c.check(f"S {label} g: Stage G's predictions are its declared five, in order, on their declared cells",
            have == declared_cells() and all(len(q["sigma_total_over_f"]) == len(q["cells"]) for q in gr["predictions"]),
            have)
    c.check(f"S {label} g: every prediction's sigma_total_over_f is sqrt(diag(C_rep,F))/f", all(
        F.worst(np.array(q["sigma_total_over_f"]), sig[[CELLS.index(x) for x in q["cells"]]]) <= TOL
        for q in gr["predictions"]), None)
    if f0b is not None:
        b = load_strict(f0b.read_bytes())
        c.check(f"S {label} f0b: its sqrt(diag(C_total + X_F))/f is sqrt(diag(C_rep,F))/f",
                F.worst(np.array(b[f"relative_sigma_plus_{BLOCKS[SIDE_KEY[side]]}"]["C_total"]), sig) <= TOL, None)


def old_product_deposit(cS: Chain, D: Path, pS, BA: Path) -> None:
    """The with-block data product and deposit candidate as committed, by their own tools, compared with the
    committed files (control R): the product's CSVs byte for byte and its JSON but argv; the deposit built and
    checked as recorded, its CSVs byte for byte and its JSON files but code_sha256."""
    pdir = BA / "S" / "old-with" / "data-product"
    cS.run("data_product", "old-with", "fd_cpl_addition",
           ["product", "--data-product", str(pS.committed["data_product"]), "--block-npz",
            str(pS.T / "fd/with-cpl/block/cpl_block.npz"), "--block-json", str(pS.T / "fd/with-cpl/block/cpl_block.json"),
            "--g-readout", str(D / OLD_S["with"]["g"][0]), "--audit-json", str(pS.audit), "--out-dir", str(pdir)],
           [pdir / n for n in A_PRODUCT_NAMES], 75,
           pins={"data_product": A.PINS["data_product"], "block_npz": PINS["cpl_block_npz"],
                 "block_json": CPL_BLOCK_JSON, "g_readout": OLD_S["with"]["g"][1], "audit_json": A.PINS["audit"]})
    cdp = D / FD / "fd/with-cpl/data-product"
    csvs = sorted(q.name for q in cdp.glob("*.csv"))
    cS.check("R data_product: every CSV is the committed with-block product's, byte for byte", bool(csvs) and all(
        (pdir / n).read_bytes() == (cdp / n).read_bytes() for n in csvs)
        and sorted(q.name for q in pdir.glob("*.csv")) == csvs, csvs)
    raw = (D / SOURCES["data_product_cpl"]).read_bytes()
    cS.check("R data_product: the committed product is the pinned bytes",
             hashlib.sha256(raw).hexdigest() == PINS["data_product_cpl"], None)
    bad = compare(load_strict(raw), load_strict((pdir / f"{A.PRODUCT_STEM}.json").read_bytes()), A.DP_EXCLUDE, True)
    cS.check("R data_product: its JSON is the committed one but argv", not bad, bad[:20])
    dep = BA / "S" / "old-with" / "deposit-candidate"
    dpins = {"data_product": PINS["data_product_cpl"], "g_readout": OLD_S["with"]["g"][1]}
    cS.run("deposit_build", "old-with", "fd_deposit_candidate",
           ["build", "--data-product", str(D / SOURCES["data_product_cpl"]), "--g-readout",
            str(D / OLD_S["with"]["g"][0]), "--out-dir", str(dep)],
           [dep / n for n in (*DC.FILES, DC.REFERENCE)], 75, pins=dpins, variant="with-cpl")
    cS.run("deposit_check", "old-with", "fd_deposit_candidate",
           ["check", "--package", str(dep), "--data-product", str(D / SOURCES["data_product_cpl"]), "--g-readout",
            str(D / OLD_S["with"]["g"][0])], [dep / "deposit.json"], 75, pins=dpins, variant="with-cpl")
    rec5b = load_strict((D / FD / "fd/receipts-ct/5b/addition/run/chain.json").read_bytes())
    built = [s for s in rec5b["steps"] if s.get("step") == "deposit_build" and s.get("arm") == "with"]
    sums = {Path(q).name: h for q, h in (built[0]["outputs"] if len(built) == 1 else {}).items()}
    for n in (*DC.FILES, DC.REFERENCE):
        cS.check(f"R deposit {n}: the committed file is the 5B receipt's bytes", A.sha256(D / OLD_DEP / n) == sums.get(n), n)
    for n in (*DC.FILES, DC.REFERENCE):
        a_, b_ = (D / OLD_DEP / n).read_bytes().decode(), (dep / n).read_bytes().decode()
        ok = a_ == b_ if n.endswith(".csv") else DC.without_code(a_) == DC.without_code(b_)
        cS.check(f"R deposit {n}: the committed with-block file{'' if n.endswith('.csv') else ' but code_sha256'}", ok, n)


A_PRODUCT_NAMES = (f"{A.PRODUCT_STEM}.json", f"{A.PRODUCT_STEM}_cells.csv",
                   *[f"{A.PRODUCT_STEM}_{k}.csv" for k in A.PRODUCT_MATRICES], f"{A.PRODUCT_STEM}_corr_{A.REPORTED}.csv")


def vf_arms(cS: Chain, cE: Chain, D: Path, BA: Path, vf: dict, blk: dict, tables: dict) -> None:
    """The V_F arms (F0, then each side's set S and chdefs set, each step's C as it returns, then S), the V_F data
    product, the deposit candidate and the table. Called only after every OLD-arm control has passed. ``tables``: the
    experiment tables' declared digests (the OLD readouts'), which a V_F arm must write unchanged."""
    vnpz = vf["npz"]
    f0, f0npz = run_f0(cS, "vf-f0", vf)
    check_table(cS, "vf-f0 f0", f0, f0npz, tables["f0"])
    res_s, res_e = {}, {}
    for side in ("with", "nopl"):
        arm = f"vf-{side}"
        out = run_s(cS, arm, vf, None)
        res_s[side] = out
        check_table(cS, f"{arm} f0b", out["f0b"], out["f0b_npz"], tables[f"{side}/f0b"])
        check_table(cS, f"{arm} f1", out["f1"], out["f1_npz"], tables[f"{side}/f1"])
        check_s(cS, arm, out["g"], out["f0b"], blk, side)
        res = run_e(cE, arm, vf, (out["f0b"], A.sha256(out["f0b"])))
        res_e[side] = res
        check_s(cE, f"E {arm}", res["out"]["g"], None, blk, side)
    vdir = BA / "vf" / "data-product"
    gS = res_s["with"]["g"]
    bj = D / FD / "fd/with-vf/block/vf_block.json"
    cS.run("data_product", "vf-with", "fd_vf_addition",
           ["product", "--data-product", str(D / SOURCES["data_product_cpl"]), "--block-npz", str(vnpz),
            "--block-json", str(bj), "--g-readout", str(gS), "--out-dir", str(vdir)],
           [vdir / n for n in product_names()], 75,
           pins={"data_product": PINS["data_product_cpl"], "block_npz": vf["sha"], "block_json": vf["json_sha"],
                 "g_readout": A.sha256(gS)})
    vdep = BA / "vf" / "deposit-candidate"
    vpins = {"data_product": A.sha256(vdir / f"{PRODUCT_STEM}.json"), "g_readout": A.sha256(gS)}
    cS.run("deposit_build", "vf-with", "fd_deposit_candidate",
           ["build", "--data-product", str(vdir / f"{PRODUCT_STEM}.json"), "--g-readout", str(gS), "--out-dir",
            str(vdep)], [vdep / n for n in (*DC.FILES, DC.REFERENCE)], 75, pins=vpins, variant="with-vf")
    cS.run("deposit_check", "vf-with", "fd_deposit_candidate",
           ["check", "--package", str(vdep), "--data-product", str(vdir / f"{PRODUCT_STEM}.json"), "--g-readout",
            str(gS)], [vdep / "deposit.json"], 75, pins=vpins, variant="with-vf")

    # the table: every V_F readout beside its OLD one; OLD pins declared, V_F pins as recorded when written
    written = {q: h for s in cS.steps if "outputs" in s for q, h in s["outputs"].items()}
    pairs = [["F0", str(D / OLD_F0[0]), OLD_F0[1], str(f0), written[str(f0)]]]
    for side in ("with", "nopl"):
        pairs += [[f"S {side}/{k}", str(D / OLD_S[side][k][0]), OLD_S[side][k][1], str(res_s[side][k]),
                   written[str(res_s[side][k])]] for k in S_STEPS]
        pairs += [[f"E {side}/{k}", str(D / OLD_E[side][k][0]), OLD_E[side][k][1], str(res_e[side]["out"][k]),
                   written[str(res_e[side]["out"][k])]] for k in E_STEPS]
    pf2 = BA / "pins" / "table-pairs.json"
    A.write_atomic(pf2, (json.dumps(pairs, indent=1) + "\n").encode())
    tab = BA / "table"
    cS.run("table", "vf", "fd_vf_addition", ["table", "--pairs", str(pf2), "--out-dir", str(tab)],
           [tab / "fd_vf_table.json", tab / "fd_vf_table.md"], 75,
           pins={q: h for _, po, ho, pn, hn in pairs for q, h in ((po, ho), (pn, hn))})


def cmd_chain(a) -> int:
    D = DEPLOY
    BA = a.run_dir.resolve()
    for d in ("S", "E", "vf", "table", "logs", "pins", "mpl", "tmp", "chain.json"):
        report("C", f"{d} does not exist (no overwrite)", not (BA / d).exists() and not (BA / d).is_symlink())
    for d in ("logs", "pins", "mpl", "tmp"):
        (BA / d).mkdir(parents=True)
    os.environ["MPLCONFIGDIR"] = str(BA / "mpl")          # before any figure import, here and in every subprocess
    os.environ["TMPDIR"] = str(BA / "tmp")
    import fd_gencmp_e as E
    steps: list = []
    receipt = BA / "chain.json"
    pS = A.Paths(D, a.scratch.resolve(), BA)
    run_e_dir = a.run_e.resolve()
    pE = E.Paths(D, BA, run_e_dir, "chdefs")
    try:
        cS = Chain(pS, receipt, steps)
        # the block: the committed npz is the pinned bytes, decoded from those bytes; the deploy rebuilds the npz and
        # its readout as the same bytes as the committed ones
        vnpz, vjson = D / FD / "fd/with-vf/block/vf_block.npz", D / FD / "fd/with-vf/block/vf_block.json"
        raw = vnpz.read_bytes()
        cS.check("C vf_block.npz: the committed block is the pinned bytes",
                 hashlib.sha256(raw).hexdigest() == VF_BLOCK_NPZ, str(vnpz))
        blk = load_npz_bytes(raw)
        cS.run("block", "vf", "fd_vf_addition", ["block", "--repo", str(D), "--out-dir", str(BA / "vf" / "block")],
               [BA / "vf" / "block" / "vf_block.npz", BA / "vf" / "block" / "vf_block.json"], 75)
        cS.check("C vf_block: rebuilt in the deploy, the npz and its readout are the committed bytes",
                 (BA / "vf" / "block" / "vf_block.npz").read_bytes() == raw
                 and (BA / "vf" / "block" / "vf_block.json").read_bytes() == vjson.read_bytes(), None)
        vf = {"npz": vnpz, "sha": VF_BLOCK_NPZ, "json_sha": A.sha256(vjson)}
        # the chdefs set: its manifest is the recorded one, and its specification the committed one
        check_renderer(cS, D)
        cS.check("C chdefs: the staged predictions' manifest is the recorded one", A.sha256(pE.s5p_sums) == CHDEFS_SUMS,
                 str(pE.s5p_sums))
        specs = E.load_chdefs(run_e_dir / "pred")
        cS.check("C chdefs: the predictions' specification is the committed one",
                 specs == json.loads((D / CHDEFS_SPEC).read_bytes()), CHDEFS_SPEC)
        pf = BA / "pins" / "predictions-chdefs.json"
        A.write_atomic(pf, (json.dumps(specs, indent=1) + "\n").encode())
        cE = Chain(pE, receipt, steps, pf)
        for rel, pin in [OLD_F0, *[v for s in (OLD_S, OLD_E) for arm in s.values() for v in arm.values()]]:
            cS.check(f"R {rel}: the committed file is the pinned bytes", A.sha256(D / rel) == pin, rel)
        tables = {"f0": load_strict((D / OLD_F0[0]).read_bytes())["table_sha256"],
                  **{f"{side}/{k}": load_strict((D / OLD_S[side][k][0]).read_bytes())["table_sha256"]
                     for side in ("with", "nopl") for k in ("f0b", "f1")}}

        # ---- the OLD arms: every output against its pinned file before any V_F number
        f0, f0npz = run_f0(cS, "old-f0", vf)
        check_r(cS, "F0", D, *OLD_F0, f0, strings=False)
        check_table(cS, "old-f0 f0", f0, f0npz, tables["f0"])
        for side in ("with", "nopl"):
            arm = f"old-{side}"
            f0b_old = (D / OLD_S[side]["f0b"][0], OLD_S[side]["f0b"][1])
            out = run_s(cS, arm, vf, f0b_old)
            for k in S_STEPS:
                check_r(cS, f"S {arm} {k}", D, *OLD_S[side][k], out[k], strings=False)
            check_table(cS, f"{arm} f0b", out["f0b"], out["f0b_npz"], tables[f"{side}/f0b"])
            check_table(cS, f"{arm} f1", out["f1"], out["f1_npz"], tables[f"{side}/f1"])
            res = run_e(cE, arm, vf, f0b_old)
            for k in E_STEPS:
                check_r(cE, f"E {arm} {k}", D, *OLD_E[side][k], res["out"][k], strings=(side == "with"))
            if side == "with":
                check_r_figures(cE, f"E {arm}", D, res["fig"])
        old_product_deposit(cS, D, pS, BA)
        vf_arms(cS, cE, D, BA, vf, blk, tables)
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
