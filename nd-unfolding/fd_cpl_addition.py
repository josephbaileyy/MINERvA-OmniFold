#!/usr/bin/env python3
"""The 5B run-period block's addition (state/measurement-paper/5d-community-20261024/FD-CT-5B-ADDITION-DECLARATION.md):
C_rep,PL = C_e + C_model_abs + C_resp + C_PL,5D,abs on R00-R15, with every product recomputed with it and, at the same
code, reproduced without it. Under DECISION-20261030-joseph-4b-not-now-5b-audit-then-add.md item 2, after the audit's
stop condition did not fire (FD-CT-5B-AUDIT-REPORT.md).

Subcommands:
* ``block``   C_PL,5D,abs = diag(f) P diag(f), P the 5B readout's C_PL5D_rel read from its floats (not rebuilt), and
              the combined extra block X = C_resp + C_PL,5D,abs that every tool takes, written byte-reproducibly to
              cpl_block.npz with cpl_block.json (controls A, B0-B3);
* ``product`` the data product with the block, from the committed data product and cpl_block.npz (controls K0-K6);
* ``table``   every matrix-dependent number of the with-block readouts beside the committed one (control T);
* ``chain``   the without arm (each bound tool on its committed inputs, reproduced by control R), then the block,
              the with arm (each downstream step's pins the sha256 of the file the step before wrote) and the table.

``product`` and ``table`` take the pins of the files the chain wrote, in-process (``run(a, pins)``); their CLI refuses
without them. MEASURES: nothing but the arithmetic above. CANNOT AUTHORIZE: a write over a committed product, the
paper or the note, a reading or a claim. NOT CITABLE FOR a validated size of C_PL,5D, a cause of a period difference,
or a coverage statement.
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
import zipfile
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import fd_data_product as F  # noqa: E402  (correlation, csv_text, matrix_csv, read_matrix_csv, worst)
import fd_deposit_candidate as DC  # noqa: E402  (Variant, LABELS, without_code)
import fd_g_compare as G  # noqa: E402  (Stop, report)

N = 16
CELLS = [f"R{i:02d}" for i in range(N)]
TOL = 1e-12
FD = "docs/orchestration/state/measurement-paper/5d-community-20261024"
NAME = "C_resp + C_PL5D"                       # the combined extra block's name in every tool's readout
XKEY = "C_resp_plus_C_PL5D"                    # its key in cpl_block.npz
BLOCK = "C_PL5D"
REPORTED = "C_total_plus_C_resp_plus_C_PL5D"
WITHOUT = "C_total_plus_C_resp"
PINS = {
    "audit": "6d34d7f8034ea956cf22c092fb31d608f330daabdd721285302868806d50692c",
    "periods": "a5b17895b1189543d773e94717e14cd9b1409535e366c96788f94bf6f40759db",
    "s1_npz": "db000707780d4d6da65389be9adedfd9a3ba6552a255f6ce81ccbdd0b8eb72a4",
    "cresp_npz": "4d8b579732b79cbbb8e6c9a4f6335c4bda4eae6dd4194241a0d8cd6e7ea8a20a",
    "data_product": "b79556f0538c81942c0ddd3770ae55e5c6fe9ad53df47e470d306f727d7e7072",
}
# the committed readouts: the "without" products, reproduced by the chain's without arm (control R)
COMMITTED = {
    "f0b": (f"{FD}/fd/readout/fd_f0b_readout.json", "b9db935a3187646ba2accaf3865cf4aa26ad72676063c58e7f5e6220224ef17b"),
    "f1": (f"{FD}/fd/readout/fd_f1_readout.json", "cbe411a926a7392e4aa085c7beba6e1bda45aff55d937998c53e49f27e3516c7"),
    "g": (f"{FD}/fd/readout/fd_g_readout.json", "75a9ddee19a7affe7e3bc10bf0cba8e5ebaa71132686e5ae116f1454d7bafcee"),
    "g_diag": (f"{FD}/fd/readout/fd_g_diag_readout.json",
               "680dc5ef9c40b1ab006657ce020c6acac7e891c68ce36850cf7a7dd2df278d88"),
    "g_followup": (f"{FD}/fd/readout/fd_g_followup_readout.json",
                   "cd82517afdfb1dc8383580c8a4c57e82d9b87864e75d28528cb35c4455f6e379"),
    "g_sens2": (f"{FD}/fd/readout/fd_g_sens2_readout.json",
                "0f6568aba032e5d9a85f945048494d8fccde3525bb45a1762d6f5d5aaf15b77f"),
    "flux_boot": (f"{FD}/fd/readout/fd_flux_boot_readout.json",
                  "b7b5652cbd163b6830655250c18bbcfd65f87bb199821c97c7abdbd671e70001"),
    "data_product": (f"{FD}/fd/data-product/fd_data_product.json", PINS["data_product"]),
}
READOUTS = ("f0b", "f1", "g", "g_diag", "g_followup", "g_sens2", "flux_boot")
LABELS = {
    "block": "C_PL,5D: the 5B run-period block (FD-CT-5B-REPORT.md), audited (FD-CT-5B-AUDIT-REPORT.md); added after "
             "the data were seen; published with and without. Its sigma rests on three periods: the 68% interval on "
             "sigma_true/sigma_hat is [0.73, 2.56]. Noise-dominated cells: R00, R08. Rank 2; undebiased",
    "decision": "added under DECISION-20261030 item 2 after the audit's stop condition did not fire "
                "(FD-CT-5B-AUDIT-REPORT.md); the decision followed the data; published with and without",
    "context_dr_pair": "descriptive; not a reason for the addition: the best detector-response pair (GEANT_Pion#1 "
                       "with C_resp:meson#1) explains 0.853, 0.560 and 0.617 of PA's, PB's and PC's noise-weighted "
                       "offset patterns at |a| <= 1.51, reproducing PA's to within noise and not PB's or PC's; pairs "
                       "have no stop role (FD-CT-5B-AUDIT-REPORT.md section 4)",
    "context_5a_5b": "descriptive; not a reason for the addition: 5A's and 5B's mean period offsets agree, PB -2.724% "
                     "against -2.699% and PC +4.671% against +4.806%, while their patterns about the mean differ "
                     "beyond the combined noise, with sum (Delta/sigma)^2 of 81.6 and 192.8 over 16 cells "
                     "(FD-CT-5B-AUDIT-REPORT.md section 6)",
    "not_citable_for": ["a validated size for C_PL,5D: a block built from the observed differences contains them by "
                        "construction", "the cause of a period difference, or which period is right",
                        "a coverage or calibration statement"],
}


class Stop(Exception):
    def __init__(self, control: str, msg: str):
        super().__init__(f"{control}: {msg}")
        self.control = control


def report(control: str, name: str, ok: bool, why: str = "differs") -> None:
    print(f"{'PASS' if ok else 'FAIL'} control {control} {name}", flush=True)
    if not ok:
        raise Stop(control, f"{name}: {why}")


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pinned(path: Path, pin: str, what: str, control: str) -> bytes:
    raw = Path(path).read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    report(control, f"{what} sha256 is the pin", got == pin, f"{got} != {pin}")
    return raw


def write_atomic(path: Path, data: bytes) -> None:
    tmp = path.with_name(path.name + ".partial")
    tmp.write_bytes(data)
    os.replace(tmp, path)


# ---------------------------------------------------------------- the npz, byte-reproducibly

def npz_bytes(arrays: dict) -> bytes:
    """A stored zip of .npy members in insertion order, fixed timestamps and attributes, float64 little-endian: the
    same arrays give the same bytes, which np.load reads as an npz."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_STORED) as z:
        for k, v in arrays.items():
            b = io.BytesIO()
            np.lib.format.write_array(b, np.ascontiguousarray(np.asarray(v, dtype="<f8")), version=(1, 0),
                                      allow_pickle=False)
            zi = zipfile.ZipInfo(f"{k}.npy", date_time=(1980, 1, 1, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_STORED
            zi.create_system = 3
            zi.external_attr = 0o644 << 16
            z.writestr(zi, b.getvalue())
    return buf.getvalue()


# ---------------------------------------------------------------- block

def context_numbers(au: dict) -> dict:
    """The numbers the two context strings quote, from the audit readout, as they are printed there."""
    bp = au["item1_overlap"]["identification"]["best_pair_in_DR"]
    i3 = au["item3_5a_vs_5b"]["periods"]
    return {"context_dr_pair": [c.split(":", 1)[1] for c in bp["candidates"]]
            + [f"{bp[X]['E']:.3f}" for X in ("PA", "PB", "PC")]
            + [f"{max(abs(a) for X in ('PA', 'PB', 'PC') for a in bp[X]['a']):.2f}"],
            "context_5a_5b": [f"{100 * i3[X]['mean_offset'][k]:+.3f}%"
                              for X in ("PB", "PC") for k in ("5B", "5A")]
            + [f"{i3[X]['difference_chi2_combined_diagonal']:.1f}" for X in ("PB", "PC")]}


def check_labels(labels: dict, au: dict) -> None:
    """L: the decision, block and context strings are present, and each context number is the audit readout's."""
    report("L", "the block, decision and both context labels are present, the contexts marked descriptive", all(
        labels.get(k) == LABELS[k] for k in ("block", "decision", "context_dr_pair", "context_5a_5b"))
           and all(LABELS[k].startswith("descriptive; not a reason for the addition")
                   for k in ("context_dr_pair", "context_5a_5b")))
    for k, nums in context_numbers(au).items():
        txt, at_, missing = LABELS[k], 0, []
        for n in nums:                       # each in the label, in the readout's order
            i = txt.find(n.lstrip("+"), at_)
            if i < 0:
                missing.append(n)
            else:
                at_ = i + len(n.lstrip("+"))
        report("L", f"{k}: every number it quotes is the audit readout's, in order ({', '.join(nums)})", not missing,
               f"missing or out of order {missing}")


def build_block(s1: dict, cr: dict, per: dict, au: dict) -> dict:
    report("A", "the audit's stop condition is false", au["stop_condition"]["stop"] is False
           and au["stop_condition"]["which"] == [])
    ins = au["inputs_sha256"]
    report("A", "the audit ran on this 5B readout, S1 assembly and C_resp", ins["readout_5b"] == PINS["periods"]
           and ins["s1_npz"] == PINS["s1_npz"] and ins["cresp"] == PINS["cresp_npz"])
    report("A", "the 5B readout names this S1 assembly and C_resp", per["inputs_sha256"]["s1_npz"] == PINS["s1_npz"]
           and per["inputs_sha256"]["cresp"] == PINS["cresp_npz"] and per["cells"] == CELLS)
    check_labels(LABELS, au)
    f = s1["f"]
    P = np.array(per["C_PL5D"]["C_PL5D_rel"], dtype=float)
    report("B1", "f is 16 positive cells; P is a finite 16 x 16 matrix", f.shape == (N,) and bool(np.all(f > 0))
           and P.shape == (N, N) and bool(np.all(np.isfinite(P))))
    report("B1", "P is symmetric", float(np.abs(P - P.T).max()) <= TOL * float(np.abs(P).max()))
    lam = np.linalg.eigvalsh((P + P.T) / 2)
    rank = int(np.sum(lam > TOL * lam.max()))
    report("B1", "P is positive semidefinite and of rank 2", bool(lam.min() >= -TOL * lam.max()) and rank == 2,
           f"min {lam.min():.3e}, rank {rank}")
    report("B1", "sqrt(diag P) is the 5B readout's sigma_rel to 1e-12", F.worst(np.sqrt(np.diag(P)),
           per["C_PL5D"]["sigma_rel"]) <= TOL)
    ff = np.outer(f, f)
    M = cr["C_total_resp"] / ff
    share = float(np.trace(P) / np.trace(M + P))
    report("B1", "its trace share of M + P is the 5B readout's to 1e-10", abs(share - per["C_PL5D"]["trace_share"])
           <= 1e-10 * per["C_PL5D"]["trace_share"], f"{share} vs {per['C_PL5D']['trace_share']}")
    Cpl = ff * P
    X = cr["C_resp"] + Cpl
    rep = s1["C_e"] + s1["C_model_abs"] + cr["C_resp"] + Cpl
    scale = float(np.abs(np.diag(rep)).max())
    report("B2", "C_e + C_model_abs + C_resp + C_PL5D is C_total + X and cresp.npz's C_total_resp + C_PL5D, to 1e-12",
           float(np.abs(rep - (s1["C_total"] + X)).max()) <= TOL * scale
           and float(np.abs(rep - (cr["C_total_resp"] + Cpl)).max()) <= TOL * scale)
    report("B2", "S1's C_total is C_e + C_model_abs", float(np.abs(s1["C_total"] - s1["C_e"] - s1["C_model_abs"]).max())
           <= TOL * scale)
    report("B2", "the revised matrix is positive definite", bool(np.linalg.eigvalsh((rep + rep.T) / 2).min() > 0))
    arrays = {"f": f, "P_rel": P, BLOCK: Cpl, "C_resp": cr["C_resp"], XKEY: X, REPORTED: rep}
    sig = {k: (np.sqrt(np.diag(v)) / f).tolist() for k, v in (("C_total_plus_C_resp", cr["C_total_resp"]),
                                                               (BLOCK, Cpl), (REPORTED, rep))}
    return {"arrays": arrays, "rank": rank, "trace_share": share, "relative_sigma": sig}


def load_npz(path: Path) -> dict:
    with np.load(path, allow_pickle=False) as z:
        return {k: np.asarray(z[k], float) for k in z.files}


def cmd_block(a) -> int:
    out_npz, out_json = a.out_dir / "cpl_block.npz", a.out_dir / "cpl_block.json"
    report("B0", "no output exists (no overwrite)", not out_npz.exists() and not out_json.exists())
    au = json.loads(pinned(a.audit_json, PINS["audit"], "the audit readout", "B0"))
    per = json.loads(pinned(a.periods_json, PINS["periods"], "the 5B readout", "B0"))
    pinned(a.s1_npz, PINS["s1_npz"], "S1's assembly", "B0")
    pinned(a.cresp_npz, PINS["cresp_npz"], "cresp.npz", "B0")
    with np.load(a.s1_npz, allow_pickle=False) as z:
        s1 = {k: np.asarray(z[k], float) for k in ("f", "C_e", "C_model_abs", "C_total")}
    with np.load(a.cresp_npz, allow_pickle=False) as z:
        cr = {k: np.asarray(z[k], float) for k in ("C_resp", "C_total_resp")}
    b = build_block(s1, cr, per, au)
    data = npz_bytes(b["arrays"])
    report("B3", "the npz is the same bytes when written twice", data == npz_bytes(b["arrays"]))
    a.out_dir.mkdir(parents=True, exist_ok=True)
    write_atomic(out_npz, data)
    back = load_npz(out_npz)
    report("B3", "the npz reads back key by key, bit for bit", list(back) == list(b["arrays"])
           and all(np.array_equal(back[k], b["arrays"][k]) for k in back))
    h = sha256(out_npz)
    readout = {"schema": "fd-cpl-block/1", "labels": LABELS, "controls_passed": ["A", "L", "B0", "B1", "B2", "B3"],
               "cells": CELLS, "npz": {"file": out_npz.name, "sha256": h, "keys": list(b["arrays"]),
                                       "extra_block": {"key": XKEY, "name": NAME}},
               "rank": b["rank"], "trace_share_of_M_plus_P": b["trace_share"], "relative_sigma": b["relative_sigma"],
               "inputs_sha256": {k: PINS[k] for k in ("audit", "periods", "s1_npz", "cresp_npz")},
               "code_sha256": {"fd_cpl_addition.py": sha256(Path(__file__).resolve())}, "argv": list(sys.argv)}
    write_atomic(out_json, (json.dumps(readout, indent=1, allow_nan=False) + "\n").encode())
    print(json.dumps({"wrote": str(out_npz), "sha256": h}), flush=True)
    print(json.dumps({"wrote": str(out_json), "sha256": sha256(out_json)}), flush=True)
    return 0


# ---------------------------------------------------------------- product

PRODUCT_STEM = "fd_data_product_cpl"
PRODUCT_MATRICES = ("C_e", "C_model_abs", "C_resp", BLOCK, WITHOUT, REPORTED)
PRODUCT_INPUTS = ("data_product", "block_npz", "block_json", "g_readout", "audit_json")


def product_labels(dp: dict) -> dict:
    return {"what": "data product with the 5B run-period block: the 5D result's revised covariance",
            "covariance": "C_total + C_resp + C_PL5D = C_e + C_model_abs + C_resp + C_PL5D, the revised reported "
                          "covariance (FD-CT-5B-ADDITION-DECLARATION.md section 1), with C_PL5D = diag(f) P diag(f); "
                          "C_total_plus_C_resp is the committed product's matrix, written beside it as the variant "
                          "without the block. Stage G's chi2 is against C_total + C_resp + C_PL5D + V_g",
            "units": dp["labels"]["units"], **{k: LABELS[k] for k in ("block", "decision", "context_dr_pair",
                                                                       "context_5a_5b")},
            "not_citable_for": ["coverage", *LABELS["not_citable_for"]],
            "not": "no reading, claim or release text; whether it ships is Joseph's"}


def build_product(dp: dict, blk: dict, bj: dict, gr: dict, pins: dict) -> dict:
    report("K1", "the committed data product is Q0-Q6 on this S1 assembly and C_resp", dp["controls_passed"] ==
           ["Q0", "Q1", "Q2", "Q3", "Q4", "Q5", "Q6"] and dp["inputs_sha256"]["s1_npz"] == PINS["s1_npz"]
           and dp["inputs_sha256"]["cresp_npz"] == PINS["cresp_npz"] and [c["cell"] for c in dp["cells"]] == CELLS)
    report("K1", "the block readout names this npz, built on the same S1 assembly and C_resp",
           bj["npz"]["sha256"] == pins["block_npz"] and bj["inputs_sha256"]["s1_npz"] == PINS["s1_npz"]
           and bj["inputs_sha256"]["cresp_npz"] == PINS["cresp_npz"])
    xb = gr["extra_block"]
    report("K1", "Stage G's reported comparison adopted this block", xb["sha256"] == pins["block_npz"]
           and xb["name"] == NAME and xb["key"] == XKEY and xb["role"] == "adopted"
           and gr["inputs_sha256"]["s1_npz"] == PINS["s1_npz"])
    f = np.array(dp["f"], float)
    mats = {k: np.array(dp["matrices"][k], float) for k in ("C_e", "C_model_abs", "C_resp", WITHOUT)}
    report("K2", "the block's f and C_resp are the data product's, bit for bit", np.array_equal(blk["f"], f)
           and np.array_equal(blk["C_resp"], mats["C_resp"]))
    Cpl, rep = blk[BLOCK], blk[REPORTED]
    scale = float(np.abs(np.diag(rep)).max())
    report("K2", "the revised matrix is the data product's C_total_plus_C_resp + C_PL5D, to 1e-12",
           float(np.abs(rep - (mats[WITHOUT] + Cpl)).max()) <= TOL * scale)
    report("K2", "the revised matrix is C_e + C_model_abs + C_resp + C_PL5D, to 1e-12", float(np.abs(
        rep - (mats["C_e"] + mats["C_model_abs"] + mats["C_resp"] + Cpl)).max()) <= TOL * scale)
    sig = np.sqrt(np.diag(rep)) / f
    for p in gr["predictions"]:
        idx = [CELLS.index(c) for c in p["cells"]]
        report("K3", f"{p['name']}: Stage G's sigma_total_over_f is sqrt(diag(C_rep))/f to 1e-12 and its covariance "
                     f"is C_total + {NAME}", F.worst(np.array(p["sigma_total_over_f"]), sig[idx]) <= TOL
               and p["reported_covariance"] == f"C_total + {NAME}")
    mats = {"C_e": mats["C_e"], "C_model_abs": mats["C_model_abs"], "C_resp": mats["C_resp"], BLOCK: Cpl,
            WITHOUT: mats[WITHOUT], REPORTED: rep}
    for k, C in mats.items():
        report("K4", f"{k} is symmetric", float(np.abs(C - C.T).max()) <= TOL * scale)
    ev = {k: np.linalg.eigvalsh((v + v.T) / 2 / np.outer(f, f)) for k, v in mats.items()}
    report("K4", "the revised matrix is positive definite", bool(ev[REPORTED].min() > 0))
    lam = ev[BLOCK]
    report("K4", "C_PL5D is positive semidefinite and of rank 2", bool(lam.min() >= -TOL * lam.max())
           and int(np.sum(lam > TOL * lam.max())) == 2)
    rho = F.correlation(rep)
    d = np.sqrt(np.diag(rep))
    report("K5", "the correlation is the revised matrix's, symmetric, within [-1, 1], with a unit diagonal",
           float(np.abs(rho * np.outer(d, d) - rep).max()) <= TOL * scale and float(np.abs(rho - rho.T).max()) <= TOL
           and float(np.abs(rho).max()) <= 1 + TOL and float(np.abs(np.diag(rho) - 1).max()) <= TOL)
    rel = {k: np.sqrt(np.diag(v)) / f for k, v in mats.items()}
    report("K5", "the without matrix's relative sigma is the committed product's", F.worst(
        rel[WITHOUT], dp["relative_sigma"][WITHOUT]) <= TOL)
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
    files[f"{PRODUCT_STEM}_corr_{REPORTED}.csv"] = F.matrix_csv(p["correlation"])
    return files


def cmd_product(a, pins: dict | None) -> int:
    if pins is None:
        raise Stop("K0", "product runs in the chain only: the block's and Stage G's pins are the files it just wrote")
    names = [f"{PRODUCT_STEM}.json", f"{PRODUCT_STEM}_cells.csv", *[f"{PRODUCT_STEM}_{k}.csv" for k in
                                                                      PRODUCT_MATRICES],
             f"{PRODUCT_STEM}_corr_{REPORTED}.csv"]
    report("K0", "no output exists (no overwrite)", not any((a.out_dir / n).exists() for n in names))
    report("K0", "the committed data product's and the audit's pins are the declared ones",
           pins["data_product"] == PINS["data_product"] and pins["audit_json"] == PINS["audit"])
    raw = {k: pinned(getattr(a, k), pins[k], k, "K0") for k in PRODUCT_INPUTS}
    dp, bj, gr = (json.loads(raw[k]) for k in ("data_product", "block_json", "g_readout"))
    p = build_product(dp, load_npz(a.block_npz), bj, gr, pins)
    files = product_files(p, dp)
    readout = {"schema": "fd-data-product-cpl/1", "labels": {**product_labels(dp), "cells": dp["labels"]["cells"]},
               "controls_passed": ["K0", "K1", "K2", "K3", "K4", "K5", "K6"], "cells": dp["cells"], "h2": dp["h2"],
               "f": p["f"].tolist(), "matrices": {k: v.tolist() for k, v in p["matrices"].items()},
               "correlation": p["correlation"].tolist(), "correlation_of": REPORTED,
               "relative_sigma": {k: v.tolist() for k, v in p["relative_sigma"].items()},
               "files_sha256": {n: hashlib.sha256(t.encode()).hexdigest() for n, t in files.items()},
               "inputs_sha256": {k: pins[k] for k in PRODUCT_INPUTS},
               "code_sha256": {"fd_cpl_addition.py": sha256(Path(__file__).resolve()),
                               "fd_data_product.py": sha256(Path(F.__file__).resolve())}, "argv": list(sys.argv)}
    js = json.loads(json.dumps(readout, allow_nan=False))
    for k in PRODUCT_MATRICES:
        back = F.read_matrix_csv(files[f"{PRODUCT_STEM}_{k}.csv"])
        report("K6", f"{k}: the CSV and the JSON read back bit for bit", np.array_equal(back, p["matrices"][k])
               and np.array_equal(np.array(js["matrices"][k]), p["matrices"][k]))
    report("K6", "the correlation's CSV and JSON read back bit for bit", np.array_equal(
        F.read_matrix_csv(files[f"{PRODUCT_STEM}_corr_{REPORTED}.csv"]), p["correlation"])
           and np.array_equal(np.array(js["correlation"]), p["correlation"]))
    check_labels(readout["labels"], json.loads(raw["audit_json"]))
    a.out_dir.mkdir(parents=True, exist_ok=True)
    files[f"{PRODUCT_STEM}.json"] = json.dumps(readout, indent=1, allow_nan=False) + "\n"
    for n, text in files.items():
        write_atomic(a.out_dir / n, text.encode())
        print(json.dumps({"wrote": str(a.out_dir / n), "sha256": sha256(a.out_dir / n)}), flush=True)
    return 0


def deposit_variant(pins: dict) -> DC.Variant:
    """The deposit candidate's variant for the revised matrix, with the chain's pins of the with-block data product
    and Stage G readout."""
    labels = {**DC.LABELS,
              "what": "the 5D result on its sixteen reporting cells R00-R15: cell definitions, the measured vector f, "
                      "the revised covariance C_total + C_resp + C_PL5D and its correlation matrix",
              "covariance": "C_total + C_resp + C_PL5D = C_e + C_model_abs + C_resp + C_PL5D, the revised reported "
                            "covariance (the with-block data product's C_total_plus_C_resp_plus_C_PL5D). The paper's "
                            "chi2 for a prediction g on its cells c is d^T (C + V_g)^-1 d with d = f - g, C this "
                            "covariance on c, and V_g = diag of g's own finite-MC variance, ndf n; its shape-only chi2 "
                            "adds 100 f f^T (f on c, absolute units) to C + V_g, ndf n - 1; g and V_g are the "
                            "prediction's, not part of the measurement",
              **{k: LABELS[k] for k in ("block", "decision", "context_dr_pair", "context_5a_5b")}}
    return DC.Variant(key=REPORTED, name="C_total + C_resp + C_PL5D", labels=labels,
                      pins={"data_product": pins["data_product"], "g_readout": pins["g_readout"]},
                      sources={"data_product": f"fd/with-cpl/data-product/{PRODUCT_STEM}.json",
                               "g_readout": "fd/with-cpl/readout/fd_g_readout.json"})


# ---------------------------------------------------------------- comparisons (R) and the table (T)

def numeric_leaves(o, path=""):
    """(path, value) for every int, float, bool and None leaf; dict keys sorted, lists by index."""
    if isinstance(o, dict):
        for k in sorted(o):
            yield from numeric_leaves(o[k], f"{path}/{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from numeric_leaves(v, f"{path}/{i}")
    elif o is None or isinstance(o, (bool, int, float)):
        yield path, o


def structure(o, path=""):
    """Every container path with its keys (dicts) or length (lists): the shape R requires to be equal."""
    if isinstance(o, dict):
        yield path, ("dict", tuple(sorted(o)))
        for k in sorted(o):
            yield from structure(o[k], f"{path}/{k}")
    elif isinstance(o, list):
        yield path, ("list", len(o))
        for i, v in enumerate(o):
            yield from structure(v, f"{path}/{i}")


def same_number(x, y, tol: float = TOL) -> bool:
    if isinstance(x, bool) or isinstance(y, bool) or x is None or y is None:
        return x is y or (x == y and type(x) is type(y))
    if math.isnan(x) or math.isnan(y):
        return False
    return x == y or abs(x - y) <= tol * max(abs(x), abs(y))


def skipped(path: str, exclude) -> bool:
    return any(path == e or path.startswith(e + "/") for e in exclude)


def compare_numbers(old: dict, new: dict, exclude=("/argv", "/code_sha256", "/code", "/versions")) -> list:
    """R on a readout: the same structure, and every number, bool and null equal to 1e-12 relative, outside the
    excluded subtrees. Returns the differences (empty when it holds)."""
    bad = []
    so = {p: s for p, s in structure(old) if not skipped(p, exclude)}
    sn = {p: s for p, s in structure(new) if not skipped(p, exclude)}
    bad += [f"structure {p}" for p in sorted(set(so) | set(sn)) if so.get(p) != sn.get(p)]
    lo = {p: v for p, v in numeric_leaves(old) if not skipped(p, exclude)}
    ln = {p: v for p, v in numeric_leaves(new) if not skipped(p, exclude)}
    bad += [f"number {p}: {lo.get(p)!r} vs {ln.get(p)!r}" for p in sorted(set(lo) | set(ln))
            if p not in lo or p not in ln or not same_number(lo[p], ln[p])]
    return bad


def string_leaves(o, path=""):
    if isinstance(o, dict):
        for k in sorted(o):
            yield from string_leaves(o[k], f"{path}/{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from string_leaves(v, f"{path}/{i}")
    elif isinstance(o, str):
        yield path, o


def compare_strings(old: dict, new: dict, exclude) -> list:
    so = {p: v for p, v in string_leaves(old) if not skipped(p, exclude)}
    sn = {p: v for p, v in string_leaves(new) if not skipped(p, exclude)}
    return [f"string {p}" for p in sorted(set(so) | set(sn)) if so.get(p) != sn.get(p)]


def rename(key: str) -> str:
    """A with-block readout's key, as the committed readout spells it (keys built from the block's name)."""
    return key.replace(NAME, "C_resp")


def paired(old, new, path=""):
    """(path, without, with) for every numeric leaf at the same place in both readouts, keys renamed."""
    if isinstance(old, dict) and isinstance(new, dict):
        nk = {rename(k): k for k in new}
        for k in sorted(old):
            if k in nk:
                yield from paired(old[k], new[nk[k]], f"{path}/{k}")
    elif isinstance(old, list) and isinstance(new, list) and len(old) == len(new):
        for i, (x, y) in enumerate(zip(old, new)):
            yield from paired(x, y, f"{path}/{i}")
    elif not isinstance(old, (dict, list, str)) and not isinstance(new, (dict, list, str)):
        yield path, old, new


def at(o, path: str):
    for k in path.strip("/").split("/"):
        o = o[int(k)] if isinstance(o, list) else o[k]
    return o


def curated(old: dict, new: dict, dp_old: dict, dp_new: dict) -> dict:
    """The table's named rows (FD-CT-5B-ADDITION-DECLARATION.md section 3.1), each without and with."""
    sig = {"cells": CELLS, "without": dp_old["relative_sigma"][WITHOUT], "C_PL5D": dp_new["relative_sigma"][BLOCK],
           "with": dp_new["relative_sigma"][REPORTED],
           "ratio": (np.array(dp_new["relative_sigma"][REPORTED]) / np.array(dp_old["relative_sigma"][WITHOUT])).tolist(),
           "matrices": {"without": "C_total + C_resp", "with": "C_total + C_resp + C_PL5D"}}
    report("T", "Stage G's predictions are the same, in the same order, on both sides",
           [p["name"] for p in old["g"]["predictions"]] == [p["name"] for p in new["g"]["predictions"]])
    for r in ("f0b", "f1"):
        report("T", f"{r}'s truths are the same, in the same order, on both sides",
               [t["name"] for t in old[r]["truths"]] == [t["name"] for t in new[r]["truths"]])
    g = []
    for po, pn in zip(old["g"]["predictions"], new["g"]["predictions"]):
        for kind in ("total", "shape_only"):
            g.append({"prediction": po["name"], "kind": kind, "ndf": po[kind]["ndf"],
                      "without": {k: po[kind][k] for k in ("chi2", "p", "matrix")},
                      "with": {k: pn[kind][k] for k in ("chi2", "p", "matrix")}})
    truths = {}
    for r in ("f0b", "f1"):
        truths[r] = [{"truth": to["name"], "graded": to["graded"],
                      "without": {k: to["grade"].get(k) for k in ("chi2", "p")} | {
                          "cells_abs_z_gt_2": len(to["grade"].get("cells_abs_z_gt_2", []))},
                      "with": {k: tn["grade"].get(k) for k in ("chi2", "p")} | {
                          "cells_abs_z_gt_2": len(tn["grade"].get("cells_abs_z_gt_2", []))},
                      "grade_matrix": {"without": to["grade_matrix"], "with": tn["grade_matrix"]}}
                     for to, tn in zip(old[r]["truths"], new[r]["truths"]) if to["graded"]]
    trig = {r: {grp: {k: {"without": old[r]["triggers"]["by_group"][grp][k], "with": new[r]["triggers"]["by_group"][grp][k]}
                      for k in ("cells_abs_z_gt_2", "truths_p_lt_0.01")}
                for grp in old[r]["triggers"]["by_group"]} for r in ("f0b", "f1")}
    fb = [{"variant": v, "prediction": n, "without": {q: old["flux_boot"]["bands"][v][n]["total"]["percentiles"][q]
                                                       for q in ("16", "50", "84")},
           "with": {q: new["flux_boot"]["bands"][v][n]["total"]["percentiles"][q] for q in ("16", "50", "84")}}
          for v in old["flux_boot"]["bands"] for n in old["flux_boot"]["bands"][v]]
    return {"sigma_over_f": sig, "stage_g": g, "truths": truths, "triggers": trig, "flux_boot_total_band": fb}


def table_md(c: dict, counts: dict) -> str:
    L = ["# The 5B block's addition: every matrix-dependent number, without and with C_PL5D", "",
         f"Without: C_total + C_resp (the committed readouts). With: C_total + C_resp + C_PL5D. {LABELS['decision']}.",
         "", "## sigma/f per cell", "", "| cell | without | C_PL5D | with | with / without |", "|---|---:|---:|---:|---:|"]
    s = c["sigma_over_f"]
    L += [f"| {cell} | {100 * a:.3f}% | {100 * b:.3f}% | {100 * w:.3f}% | {r:.4f} |"
          for cell, a, b, w, r in zip(s["cells"], s["without"], s["C_PL5D"], s["with"], s["ratio"])]
    L += ["", "## Stage G", "", "| prediction | kind | ndf | chi2 without | p without | chi2 with | p with |",
          "|---|---|---:|---:|---:|---:|---:|"]
    L += [f"| {r['prediction']} | {r['kind']} | {r['ndf']} | {r['without']['chi2']:.3f} | {r['without']['p']:.3g} | "
          f"{r['with']['chi2']:.3f} | {r['with']['p']:.3g} |" for r in c["stage_g"]]
    for k in ("f0b", "f1"):
        L += ["", f"## {k.upper()}: each graded truth", "",
              "| truth | chi2 without | p without | cells abs(z) > 2 | chi2 with | p with | cells abs(z) > 2 |",
              "|---|---:|---:|---:|---:|---:|---:|"]
        L += [f"| {t['truth']} | {t['without']['chi2']:.4g} | {t['without']['p']:.3g} | {t['without']['cells_abs_z_gt_2']} | "
              f"{t['with']['chi2']:.4g} | {t['with']['p']:.3g} | {t['with']['cells_abs_z_gt_2']} |" for t in c["truths"][k]]
    L += ["", "## The flux bootstrap: each total chi2's replicate percentiles 16 / 50 / 84", "",
          "| variant | prediction | without | with |", "|---|---|---|---|"]
    L += [f"| {r['variant']} | {r['prediction']} | " + " / ".join(f"{r['without'][q]:.2f}" for q in ("16", "50", "84"))
          + " | " + " / ".join(f"{r['with'][q]:.2f}" for q in ("16", "50", "84")) + " |" for r in c["flux_boot_total_band"]]
    L += ["", "## Every other number", "", "`fd_cpl_table.json` `leaves` pairs every numeric leaf of each readout:", ""]
    L += [f"- {k}: {n} paired leaves" for k, n in counts.items()]
    L += ["", f"NOT CITABLE FOR: {'; '.join(LABELS['not_citable_for'])}.", ""]
    return "\n".join(L)


TABLE_INPUTS = tuple(f"{k}_{arm}" for k in (*READOUTS, "data_product") for arm in ("without", "with"))


def cmd_table(a, pins: dict | None) -> int:
    if pins is None:
        raise Stop("T", "table runs in the chain only: the with-block readouts' pins are the files it wrote")
    out_json, out_md = a.out_dir / "fd_cpl_table.json", a.out_dir / "fd_cpl_table.md"
    report("T", "no output exists (no overwrite)", not out_json.exists() and not out_md.exists())
    for k in (*READOUTS, "data_product"):
        report("T", f"{k}: the without readout's pin is the committed one", pins[f"{k}_without"] == COMMITTED[k][1])
    r = {k: json.loads(pinned(getattr(a, k), pins[k], k, "T")) for k in TABLE_INPUTS}
    old = {k: r[f"{k}_without"] for k in READOUTS}
    new = {k: r[f"{k}_with"] for k in READOUTS}
    c = curated(old, new, r["data_product_without"], r["data_product_with"])
    for p in c["stage_g"]:
        want = p["without"]["matrix"].replace("C_total + C_resp", f"C_total + {NAME}", 1)
        report("T", f"Stage G {p['prediction']} {p['kind']}: each side names its matrix (the with side the without's, "
                    f"with C_resp read as {NAME})", p["without"]["matrix"].startswith("C_total + C_resp + V_g")
               and p["with"]["matrix"] == want, f"{p['without']['matrix']!r} / {p['with']['matrix']!r}")
    leaves = {k: [[p, x, y] for p, x, y in paired(old[k], new[k])] for k in READOUTS}
    counts = {k: len(v) for k, v in leaves.items()}
    unpaired = {k: sorted({p for p, _ in numeric_leaves(old[k])} - {q[0] for q in leaves[k]}) for k in READOUTS}
    table = {"schema": "fd-cpl-table/1", "labels": {"what": "every matrix-dependent number, without and with C_PL5D",
                                                     "without": "C_total + C_resp: the committed readouts",
                                                     "with": "C_total + C_resp + C_PL5D: the with-block readouts",
                                                     **{k: LABELS[k] for k in ("block", "decision", "context_dr_pair",
                                                                               "context_5a_5b", "not_citable_for")}},
             "controls_passed": ["T", "L"], "curated": c, "leaves": leaves, "leaf_counts": counts,
             "unpaired_without_leaves": unpaired,
             "inputs_sha256": {k: pins[k] for k in TABLE_INPUTS},
             "code_sha256": {"fd_cpl_addition.py": sha256(Path(__file__).resolve())}, "argv": list(sys.argv)}
    check_labels(table["labels"], json.loads(pinned(a.audit_json, PINS["audit"], "the audit readout", "L")))
    a.out_dir.mkdir(parents=True, exist_ok=True)
    write_atomic(out_json, (json.dumps(table, indent=1, allow_nan=False) + "\n").encode())
    write_atomic(out_md, table_md(c, counts).encode())
    for p in (out_json, out_md):
        print(json.dumps({"wrote": str(p), "sha256": sha256(p)}), flush=True)
    return 0


# ---------------------------------------------------------------- chain

BOOT = """import json, sys
nd, mod, pins_file, variant, argv = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], json.loads(sys.argv[5])
sys.path.insert(0, nd)
import importlib
T = importlib.import_module(mod)
pins = json.load(open(pins_file))
sys.argv = [T.__file__, *argv]
kw = {}
if variant == "with-cpl":
    import fd_cpl_addition as A
    kw["variant"] = A.deposit_variant(pins)
    pins = None
sys.exit(T.run(T.build_args(argv), pins=pins, **kw))
"""


class Paths:
    """Every path the chain reads, from the deploy D, the scratch root P and the run directory BA."""

    def __init__(self, D: Path, P: Path, BA: Path):
        self.D, self.P, self.BA = D, P, BA
        self.T = D / FD
        self.nd = D / "nd-unfolding"
        self.definition = self.nd / "pv-ladder/readouts/h2_definition.json"
        self.s1_npz = P / "s1-20261024/s1_assembly.npz"
        self.s1_json = self.T / "s1/readout/s1_assembly.json"
        self.cmodel_json = self.nd / "pv-ladder/readouts/cmodel_5d.json"
        self.cmodel_npz = P / "cmodel5d-20261024/out/cmodel_5d.npz"
        self.s5p_sums = D / "docs/orchestration/state/s5p/archive/SHA256SUMS-s5p-archive-20261006.txt"
        self.s5p_root = P / "s5p-20260926"
        self.cresp = P / "cresp-20261026/out/cresp.npz"
        self.cresp_json = D / "docs/orchestration/state/measurement-scoping/assigned-uncertainties/cresp/cresp.json"
        self.cresp_report = D / "docs/orchestration/state/measurement-scoping/assigned-uncertainties/cresp/CRESP-REPORT.md"
        self.stage1 = D / "docs/orchestration/state/s5p/stage1/stage1_inspect.json"
        self.constraint = P / ("MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/"
                               "sorted_NuEConstraint_FHC_RHC_IMD.txt")
        self.audit = self.T / "fd/readout/fd_ct_5b_audit.json"
        self.periods = self.T / "fd/readout/fd_ct_5b_periods.json"
        self.committed = {k: D / rel for k, (rel, _) in COMMITTED.items()}

    def common(self) -> list[str]:
        return ["--definition", str(self.definition), "--s1-npz", str(self.s1_npz), "--s1-json", str(self.s1_json),
                "--cmodel-json", str(self.cmodel_json), "--s5p-sums", str(self.s5p_sums),
                "--s5p-root", str(self.s5p_root)]

    def f0(self) -> list[str]:
        d5 = self.D / "docs/orchestration/state/measurement-paper/5d-design-20261023/stage0"
        return ["--definition", str(self.definition), "--s1-npz", str(self.s1_npz), "--s1-json", str(self.s1_json),
                "--cmodel-npz", str(self.cmodel_npz), "--cmodel-json", str(self.cmodel_json),
                "--flux-constraint", str(self.constraint),
                "--d16-dir", str(self.D / "docs/orchestration/state/s5p/stage3/f4"),
                "--f4-root", str(self.P / "s5p-20260926/runs/s3r/f4"),
                "--stage0-inventory", str(d5 / "INVENTORY.sha256"),
                "--s5e-assess", str(self.P / "s5e-20260925/runs/cand/assess"),
                "--stage0c-sums", str(d5 / "receipts-A/products.sha256"),
                "--stage0c-root", str(self.P / "5d-stage0-20261023"),
                "--pvl-products", str(self.P / "pv-ladder-20261024/products"),
                "--s5p-sums", str(self.s5p_sums), "--s5p-root", str(self.s5p_root)]

    def f1(self, f0b: Path, f0b_sha: str) -> list[str]:
        rc = self.T / "fd/receipts-f1/run/cluster"
        return ["--f1-prep-sums", str(rc / "f1b3/prep/f1-prep-SHA256SUMS"),
                "--f1-prep-sums-sha256", "981b188b03a7e75b904489fa1bf15bd818ef4b72f93a8beba4a906eb3122a480",
                "--f1-products-sums", str(rc / "manifest/f1-products-SHA256SUMS"),
                "--f1-products-sums-sha256", "fdb0274053e9946177376913f6145c024c24582f94607d1f5fd05271642fec09",
                "--f1-root", str(self.P / "fd-f1-20261027/f1c"), "--f0b-readout", str(f0b),
                "--f0b-readout-sha256", f0b_sha]


def extra(npz: Path, sha: str, key: str, name: str, role: bool = True) -> list[str]:
    out = ["--extra-block", str(npz), "--extra-block-sha256", sha, "--extra-block-key", key, "--extra-block-name", name]
    return out + (["--extra-block-role", "adopted"] if role else [])


class Chain:
    """Runs each step as a subprocess of the deploy's own tool and records it; stops at the first failure."""

    def __init__(self, paths: Paths, receipt: Path):
        self.p, self.receipt, self.steps = paths, receipt, []

    def save(self) -> None:
        write_atomic(self.receipt, (json.dumps({"schema": "fd-cpl-chain/1", "steps": self.steps}, indent=1,
                                               allow_nan=False) + "\n").encode())

    def run(self, name: str, arm: str, tool: str, argv: list, outputs: list, timeout: int, pins: dict | None = None,
            variant: str = "") -> dict:
        log = self.p.BA / "logs" / f"{arm}-{name}"
        if pins is None:
            cmd = [sys.executable, "-I", "-B", str(self.p.nd / f"{tool}.py"), *argv]
        else:
            pf = self.p.BA / "pins" / f"{arm}-{name}.json"
            write_atomic(pf, (json.dumps(pins, indent=1) + "\n").encode())
            cmd = [sys.executable, "-I", "-B", "-c", BOOT, str(self.p.nd), tool, str(pf), variant, json.dumps(argv)]
        t0 = time.time()
        with open(f"{log}.out", "w") as o, open(f"{log}.err", "w") as e:
            try:
                rc = subprocess.run(cmd, stdout=o, stderr=e, timeout=timeout, cwd=self.p.BA,
                                    env={k: v for k, v in os.environ.items() if k != "PYTHONPATH"}).returncode
            except subprocess.TimeoutExpired:
                rc = 124
        rec = {"step": name, "arm": arm, "tool": tool, "argv": argv, "pins": pins, "variant": variant or None,
               "rc": rc, "wall_s": round(time.time() - t0, 1), "start_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                                                                      time.gmtime(t0)),
               "outputs": {str(q): (sha256(q) if Path(q).exists() else None) for q in outputs}}
        self.steps.append(rec)
        self.save()
        print(f"[chain] {arm} {name}: rc {rc}, {rec['wall_s']} s", flush=True)
        if rc != 0 or any(v is None for v in rec["outputs"].values()):
            raise Stop("C", f"{arm} {name} exited {rc} or wrote no {[k for k, v in rec['outputs'].items() if v is None]}")
        return rec

    def check(self, name: str, ok: bool, detail) -> None:
        self.steps.append({"step": name, "check": True, "ok": bool(ok), "detail": detail})
        self.save()
        report(name.split(" ")[0], name, ok, f"{detail if not ok else ''}"[:2000])


def step_argv(p: Paths, step: str, xb: list, xb0: list, up: dict, out: Path, arm: str) -> list:
    """Each step's argv, as its last bound run's (FD-CT-5B-ADDITION-DECLARATION.md section 3): ``xb`` the extra
    block's flags (``xb0`` without the role, for fd_f0_regrade), ``up`` the upstream files, ``out`` the output."""
    if step == "f0b":
        return [*p.f0(), *xb0, "--out-json", str(out), "--out-npz", str(out.parent.parent / "fd_f0b_experiments.npz")]
    if step == "f1":
        return [*p.f0(), *xb0, *p.f1(up["f0b"], up["f0b_sha256"]), "--out-json", str(out),
                "--out-npz", str(out.parent.parent / "fd_f1_experiments.npz")]
    if step == "g":
        return [*p.common(), *xb, "--out-json", str(out)]
    if step == "g_diag":
        return [*p.common(), "--g-readout", str(up["g"]), *xb, "--out-json", str(out)]
    if step == "g_followup":
        return [*p.common(), "--g-readout", str(up["g"]), "--g-diag-readout", str(up["g_diag"]), *xb,
                "--out-json", str(out)]
    if step == "g_sens2":
        return ["--part", "sens2", *p.common(), "--g-readout", str(up["g"]), "--g-followup-readout",
                str(up["g_followup"]), *xb, "--out-json", str(out)]
    if step == "flux_boot":
        return [*p.common(), "--g-readout", str(up["g"]), *xb, "--flux-dir", str(p.T / "s1/readout/s1_assembly"),
                "--flux-constraint", str(p.constraint), "--out-json", str(out)]
    if step == "data_product" and arm == "without":
        return ["--s1-npz", str(p.s1_npz), "--s1-json", str(p.s1_json), "--cresp-npz", str(p.cresp),
                "--cresp-json", str(p.cresp_json), "--cresp-report", str(p.cresp_report), "--g-readout",
                str(up["g"]), "--definition", str(p.definition), "--stage1", str(p.stage1), "--out-dir", str(out)]
    if step == "data_product":
        return ["product", "--data-product", str(p.committed["data_product"]), "--block-npz", str(up["block_npz"]),
                "--block-json", str(up["block_json"]), "--g-readout", str(up["g"]), "--audit-json", str(p.audit),
                "--out-dir", str(out)]
    if step == "deposit_build":
        return ["build", "--data-product", str(up["data_product"]), "--g-readout", str(up["g"]), "--out-dir", str(out)]
    if step == "deposit_check":
        return ["check", "--package", str(out), "--data-product", str(up["data_product"]), "--g-readout",
                str(up["g"])]
    fargs = ["--g-readout", str(up["g"]), "--g-diag-readout", str(up["g_diag"]), "--g-followup-readout",
             str(up["g_followup"]), "--g-sens2-readout", str(up["g_sens2"]), "--f0b-readout", str(up["f0b"]),
             "--definition", str(p.definition)]
    if step == "figures":
        return [*fargs, "--figures", "ratio", "modes", "sens", "--ratio-form", "data-over-prediction",
                "--gibuu-axis", "separate", *(["--reported-block-name", NAME] if arm == "with" else []),
                "--out-dir", str(out)]
    if step == "figures_check":
        return [*fargs, "--figures-dir", str(out)]
    raise ValueError(step)


TOOLS = {"f0b": "fd_f0_regrade", "f1": "fd_f0_regrade", "g": "fd_g_compare", "g_diag": "fd_g_diag",
         "g_followup": "fd_g_followup", "g_sens2": "fd_g_followup", "flux_boot": "fd_flux_boot",
         "deposit_build": "fd_deposit_candidate", "deposit_check": "fd_deposit_candidate",
         "figures": "fd_g_figures", "figures_check": "fd_g_figures_check"}
TIMEOUT = {"f0b": 375, "f1": 900, "g": 375, "g_diag": 375, "g_followup": 375, "g_sens2": 375, "flux_boot": 375}
FIG_NAMES = ("fd_g_fig_ratio", "fd_g_fig_modes", "fd_g_fig_sens")
FIG_EXCLUDE = ("/argv", "/code", "/versions")           # the sidecar's fields that name the run, not the figure
DP_EXCLUDE = ("/argv",)


def readout_paths(base: Path) -> dict:
    return {k: base / "readout" / Path(COMMITTED[k][0]).name for k in READOUTS}


def without_arm(c: Chain) -> dict:
    """Each bound tool on its committed inputs and C_resp, as its last bound run; R compares each output with the
    committed one."""
    p, W = c.p, c.p.BA / "without"
    xb, xb0 = extra(p.cresp, PINS["cresp_npz"], "C_resp", "C_resp"), extra(p.cresp, PINS["cresp_npz"], "C_resp",
                                                                            "C_resp", role=False)
    out = readout_paths(W)
    (W / "readout").mkdir(parents=True, exist_ok=True)
    cm = p.committed
    up = {**cm, "f0b_sha256": COMMITTED["f0b"][1]}
    for k in READOUTS:
        c.run(k, "without", TOOLS[k], step_argv(p, k, xb, xb0, up, out[k], "without"), [out[k]], TIMEOUT[k])
    for k in READOUTS:
        bad = compare_numbers(json.loads(cm[k].read_bytes()), json.loads(out[k].read_bytes()))
        c.check(f"R {k}: every number and the structure are the committed readout's", not bad, bad[:20])
    dpd = W / "data-product"
    c.run("data_product", "without", "fd_data_product", step_argv(p, "data_product", xb, xb0, up, dpd, "without"),
          [dpd / "fd_data_product.json"], 75)
    cdp = cm["data_product"].parent
    csvs = sorted(q.name for q in cdp.glob("fd_data_product*.csv"))
    c.check("R data_product: every CSV is the committed product's, byte for byte", bool(csvs) and all(
        (dpd / n).read_bytes() == (cdp / n).read_bytes() for n in csvs) and sorted(
        q.name for q in dpd.glob("*.csv")) == csvs, csvs)
    old, new = json.loads(cm["data_product"].read_bytes()), json.loads((dpd / "fd_data_product.json").read_bytes())
    bad = compare_numbers(old, new, DP_EXCLUDE) + compare_strings(old, new, DP_EXCLUDE)
    c.check("R data_product: its JSON is the committed one but argv", not bad, bad[:20])
    dep = W / "deposit-candidate"
    c.run("deposit_build", "without", "fd_deposit_candidate", step_argv(p, "deposit_build", xb, xb0, up, dep,
                                                                       "without"),
          [dep / n for n in (*DC.FILES, DC.REFERENCE)], 75)
    cdep = p.T / "fd/deposit-candidate"
    for n in (*DC.FILES, DC.REFERENCE):
        a_, b_ = (cdep / n).read_bytes().decode(), (dep / n).read_bytes().decode()
        ok = a_ == b_ if n.endswith(".csv") else DC.without_code(a_) == DC.without_code(b_)
        c.check(f"R deposit {n}: the committed file{'' if n.endswith('.csv') else ' but code_sha256 (without_code)'}",
                ok, n)
    fig = W / "figures"
    c.run("figures", "without", "fd_g_figures", step_argv(p, "figures", xb, xb0, up, fig, "without"),
          [fig / f"{n}{e}" for n in FIG_NAMES for e in (".pdf", ".json")], 75)
    cfig = p.T / "fd/figures"
    for n in FIG_NAMES:
        old, new = json.loads((cfig / f"{n}.json").read_bytes()), json.loads((fig / f"{n}.json").read_bytes())
        bad = compare_numbers(old, new, FIG_EXCLUDE) + compare_strings(old, new, FIG_EXCLUDE)
        c.check(f"R figure {n}: its sidecar is the committed one but argv, code and versions; the PDF the same bytes",
                not bad and (fig / f"{n}.pdf").read_bytes() == (cfig / f"{n}.pdf").read_bytes(), bad[:20])
    return out


UPSTREAM = {"g_diag": {"g_readout": "g"}, "g_followup": {"g_readout": "g", "g_diag_readout": "g_diag"},
            "g_sens2": {"g_readout": "g", "g_followup_readout": "g_followup"}, "flux_boot": {"g_readout": "g"}}
STEP_PINS = {"g_diag": ("fd_g_diag", "PINS"), "g_followup": ("fd_g_followup", "PINS"),
             "g_sens2": ("fd_g_followup", "SENS2_PINS"), "flux_boot": ("fd_flux_boot", "PINS")}


def with_arm(c: Chain, pins_of) -> dict:
    """The block, then each consumer on it; each downstream step's pins are its defaults with only the upstream
    readouts' sha256 replaced, by the sha256 of the files the steps before wrote."""
    p, Wd = c.p, c.p.BA / "with"
    blk = Wd / "block"
    c.run("block", "with", "fd_cpl_addition", ["block", "--audit-json", str(p.audit), "--periods-json",
                                               str(p.periods), "--s1-npz", str(p.s1_npz), "--cresp-npz", str(p.cresp),
                                               "--out-dir", str(blk)], [blk / "cpl_block.npz", blk / "cpl_block.json"],
          75)
    npz, h = blk / "cpl_block.npz", sha256(blk / "cpl_block.npz")
    bj = json.loads((blk / "cpl_block.json").read_bytes())
    c.check("C block: its readout names the npz it wrote", bj["npz"]["sha256"] == h, h)
    xb, xb0 = extra(npz, h, XKEY, NAME), extra(npz, h, XKEY, NAME, role=False)
    out = readout_paths(Wd)
    (Wd / "readout").mkdir(parents=True, exist_ok=True)
    H, up = {}, {"block_npz": npz, "block_json": blk / "cpl_block.json"}
    for k in READOUTS:
        pins = None
        if k in STEP_PINS:
            pins = {**pins_of(*STEP_PINS[k]), **{f: H[u] for f, u in UPSTREAM[k].items()}}
        c.run(k, "with", TOOLS[k], step_argv(p, k, xb, xb0, up, out[k], "with"), [out[k]], TIMEOUT[k], pins=pins)
        H[k], up[k] = sha256(out[k]), out[k]
        if k == "f0b":
            up["f0b_sha256"] = H[k]
    for k in READOUTS:
        r = json.loads(out[k].read_bytes())
        xbr, ins = r.get("extra_block") or {}, r.get("inputs_sha256", {})
        named = [v for v in (xbr.get("sha256"), ins.get("extra_block")) if v is not None]
        c.check(f"C {k}: the readout names the combined block's sha256, and each upstream readout's as written",
                bool(named) and all(v == h for v in named)
                and all(ins.get(f) == H[u] for f, u in UPSTREAM.get(k, {}).items()),
                {"named": named, "upstream": {f: ins.get(f) for f in UPSTREAM.get(k, {})}})
    blkz = load_npz(npz)
    rep = np.sqrt(np.diag(blkz[REPORTED])) / blkz["f"]
    g = json.loads(out["g"].read_bytes())
    c.check("S g: every prediction's sigma_total_over_f is sqrt(diag(C_rep))/f", all(
        F.worst(np.array(q["sigma_total_over_f"]), rep[[CELLS.index(x) for x in q["cells"]]]) <= TOL
        for q in g["predictions"]), None)
    b = json.loads(out["f0b"].read_bytes())
    c.check("S f0b: its sqrt(diag(C_total + X))/f is sqrt(diag(C_rep))/f",
            F.worst(np.array(b[f"relative_sigma_plus_{NAME}"]["C_total"]), rep) <= TOL, None)
    dpd = Wd / "data-product"
    c.run("data_product", "with", "fd_cpl_addition", step_argv(p, "data_product", xb, xb0, up, dpd, "with"),
          [dpd / f"{PRODUCT_STEM}.json"], 75,
          pins={"data_product": PINS["data_product"], "block_npz": h, "block_json": sha256(blk / "cpl_block.json"),
                "g_readout": H["g"], "audit_json": PINS["audit"]})
    up["data_product"] = dpd / f"{PRODUCT_STEM}.json"
    H["data_product"] = sha256(up["data_product"])
    dep = Wd / "deposit-candidate"
    dpins = {"data_product": H["data_product"], "g_readout": H["g"]}
    c.run("deposit_build", "with", "fd_deposit_candidate", step_argv(p, "deposit_build", xb, xb0, up, dep, "with"),
          [dep / n for n in (*DC.FILES, DC.REFERENCE)], 75, pins=dpins, variant="with-cpl")
    c.run("deposit_check", "with", "fd_deposit_candidate", step_argv(p, "deposit_check", xb, xb0, up, dep, "with"),
          [dep / "deposit.json"], 75, pins=dpins, variant="with-cpl")
    fig = Wd / "figures"
    c.run("figures", "with", "fd_g_figures", step_argv(p, "figures", xb, xb0, up, fig, "with"),
          [fig / f"{n}{e}" for n in FIG_NAMES for e in (".pdf", ".json")], 75,
          pins={**pins_of("fd_g_figures", "PINS"), "g_readout": H["g"], "g_diag_readout": H["g_diag"],
                "g_followup_readout": H["g_followup"], "g_sens2_readout": H["g_sens2"], "f0b_readout": H["f0b"]})
    c.run("figures_check", "with", "fd_g_figures_check", step_argv(p, "figures_check", xb, xb0, up, fig, "with"),
          [], 75)
    tab = Wd / "table"
    targs = ["table"]
    for k in (*READOUTS, "data_product"):
        targs += [f"--{k.replace('_', '-')}-without", str(p.committed[k]), f"--{k.replace('_', '-')}-with", str(up[k])]
    c.run("table", "with", "fd_cpl_addition", [*targs, "--audit-json", str(p.audit), "--out-dir", str(tab)],
          [tab / "fd_cpl_table.json", tab / "fd_cpl_table.md"], 75,
          pins={**{f"{k}_without": COMMITTED[k][1] for k in (*READOUTS, "data_product")},
                **{f"{k}_with": H[k] for k in (*READOUTS, "data_product")}})
    return H


def cmd_chain(a) -> int:
    D = Path(__file__).resolve().parents[1]
    BA = a.run_dir
    for d in ("without", "with"):
        report("C", f"{d}/ does not exist (no overwrite)", not (BA / d).exists())
    (BA / "logs").mkdir(parents=True, exist_ok=True)
    (BA / "pins").mkdir(parents=True, exist_ok=True)
    c = Chain(Paths(D, a.scratch, BA), BA / "chain.json")

    def pins_of(mod: str, attr: str) -> dict:
        import importlib
        return dict(getattr(importlib.import_module(mod), attr))

    try:
        for k, (rel, pin) in COMMITTED.items():
            c.check(f"R {k}: the committed readout is the pinned bytes", sha256(D / rel) == pin, rel)
        without_arm(c)
        with_arm(c, pins_of)
    except Stop as e:
        print(f"[STOP] {e}", file=sys.stderr, flush=True)
        return 1
    print(f"[chain] done: {len(c.steps)} records in {c.receipt}", flush=True)
    return 0


# ---------------------------------------------------------------- CLI

def build_args(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("block")
    for k in ("audit_json", "periods_json", "s1_npz", "cresp_npz", "out_dir"):
        b.add_argument("--" + k.replace("_", "-"), dest=k, type=Path, required=True)
    p = sub.add_parser("product")
    for k in (*PRODUCT_INPUTS, "out_dir"):
        p.add_argument("--" + k.replace("_", "-"), dest=k, type=Path, required=True)
    t = sub.add_parser("table")
    for k in (*TABLE_INPUTS, "audit_json", "out_dir"):
        t.add_argument("--" + k.replace("_", "-"), dest=k, type=Path, required=True)
    c = sub.add_parser("chain")
    c.add_argument("--scratch", type=Path, required=True, help="$P, the pscratch root the inputs are under")
    c.add_argument("--run-dir", type=Path, required=True, help="$BA, where without/, with/, logs/ and pins/ go")
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
    except (Stop, G.Stop) as e:
        print(f"[STOP] {e}", file=sys.stderr, flush=True)
        return 1


def main(argv=None) -> int:
    return run(build_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
