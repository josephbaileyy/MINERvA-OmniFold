#!/usr/bin/env python3
"""T2B (fd/tier2-20261110/T2B-FD-GRADE-VARIANTS-DECLARATION.md, bound by T2-BINDING-1.md): the 16 graded fake-data
records against M1 = (C_e + C_resp)/ff^T, M2 = C_stat/ff^T and M3 = (C_stat + C_resp)/ff^T, with each record's N kept,
beside the existing grade. Controls B0-B3 run first and fail closed (exit 8, the STOP record, no variant formed).

Run under python -I, from outside the fetched directory:
  t2b_grade.py --files <fetch>/files --regrade-nd <worktree at da5f157f>/nd-unfolding --repo <a checkout at the pin>
               --out <t2b.json>
Reads the fetched npz files with allow_pickle=False only. Writes one JSON (t2b.json, or t2b.STOP.json). Nothing it
writes carries f, an absolute cell value or f - X.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

FETCHED = {
    "s1_assembly.npz": "db000707780d4d6da65389be9adedfd9a3ba6552a255f6ce81ccbdd0b8eb72a4",
    "cmodel_5d.npz": "3008d8f6b1f295cdd648f14e1ab2c20d864ce054a19f97e90e1620d22484e882",
    "cresp.npz": "4d8b579732b79cbbb8e6c9a4f6335c4bda4eae6dd4194241a0d8cd6e7ea8a20a",
    "fd_f1_experiments.npz": "997c7dae34ef9703291baece51eed05f3dd7d38a043630cac9667efaad2775bc",
    "fd_f0b_experiments.npz": "7384c6518aa0f59bd4964170fcc9b652f1c31958f422f1e1b597cd3e59219ad9",
}
D = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd"
COMMITTED = {
    f"{D}/readout/fd_f1_readout.json": "cbe411a926a7392e4aa085c7beba6e1bda45aff55d937998c53e49f27e3516c7",
    f"{D}/readout/fd_f0b_readout.json": "b9db935a3187646ba2accaf3865cf4aa26ad72676063c58e7f5e6220224ef17b",
    f"{D}/data-product/fd_data_product.json": "b79556f0538c81942c0ddd3770ae55e5c6fe9ad53df47e470d306f727d7e7072",
}
REGRADE_SHA = "0dfa722c2b74abed09fb255ccb7c0e80e6c55eb922ea1326dd74e6c880697aa2"
FETCHED_FROM = {   # T2B §2: where each fetched file lives (recorded so the receipt names each file by its full path)
    "s1_assembly.npz": "/pscratch/sd/j/josephrb/s1-20261024/s1_assembly.npz",
    "cmodel_5d.npz": "/pscratch/sd/j/josephrb/cmodel5d-20261024/out/cmodel_5d.npz",
    "cresp.npz": "/pscratch/sd/j/josephrb/cresp-20261026/out/cresp.npz",
    "fd_f1_experiments.npz": "/pscratch/sd/j/josephrb/fd-f1-20261027/grade/fd_f1_experiments.npz",
    "fd_f0b_experiments.npz": "/pscratch/sd/j/josephrb/fd-f0b-20261026/fd_f0b_experiments.npz",
}
F0B_TWELVE = ["nominal", "W1", "W2", "W3", "q3", "stage0c_gibuu", "closure_nuwro", "A7_mnvtune", "A7_genie_cv",
              "A7_genie_mec", "A7_nuwro", "A7_gibuu"]
F1_FOUR = ["F1_genie_v3_g18", "F1_closure_genie_v3_g18", "F1_genie_v3_ar23", "F1_closure_genie_v3_ar23"]
REL = 1e-12


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def close(a, b, rel=REL) -> bool:
    """Equal to ``rel`` relative, element by element, with an absolute floor of ``rel`` times the largest |b| (so a
    near-zero element of a vector is judged on the vector's scale; an all-zero b must be matched exactly)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    if a.shape != b.shape or not (np.all(np.isfinite(a)) and np.all(np.isfinite(b))):
        return False
    scale = float(np.max(np.abs(b))) if b.size else 0.0
    return bool(np.allclose(a, b, rtol=rel, atol=rel * scale))


def relmax(a, b) -> float:
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = np.abs(a - b)
    s = np.abs(b)
    return float(np.max(np.where(s > 0, d / np.where(s > 0, s, 1), d))) if a.size else 0.0


def summary(g: dict) -> dict:
    z = np.asarray(g["z"], float)
    k = int(np.argmax(np.abs(z)))
    return {"chi2": g["chi2"], "ndf": g["ndf"], "max_abs_z": float(abs(z[k])), "max_abs_z_cell": g["cells"][k],
            "cells_abs_z_gt_2": list(g["cells_abs_z_gt_2"]), "z": [float(x) for x in z]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", required=True, type=Path)
    ap.add_argument("--regrade-nd", required=True, type=Path)
    ap.add_argument("--repo", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args(argv)
    controls, stop = {}, []

    def control(name, ok, detail=None):
        controls[name] = {"pass": bool(ok), **({"detail": detail} if detail is not None else {})}
        if not ok:
            stop.append(name)

    def finish(rec, rc):
        rec["controls"] = controls
        path = a.out if rc == 0 else a.out.with_name(a.out.stem + ".STOP.json")
        path.write_text(json.dumps(rec, indent=1) + "\n")
        print(f"T2B {'OK' if rc == 0 else 'STOP'} rc={rc} -> {path}; controls failed: {stop}")
        return rc

    rec = {"schema": "t2b/1", "declaration": "T2B-FD-GRADE-VARIANTS-DECLARATION.md", "binding": "T2-BINDING-1.md",
           "inputs_sha256": {}, "inputs_paths": FETCHED_FROM,
           "label": "descriptive only: no criterion, trigger or grade changes; no p-value"}
    # input pins
    for n, s in FETCHED.items():
        got = sha(a.files / n)
        rec["inputs_sha256"][n] = got
        control(f"pin {n}", got == s)
    for p, s in COMMITTED.items():
        got = sha(a.repo / p)
        rec["inputs_sha256"][p] = got
        control(f"pin {p}", got == s)
    got = sha(a.regrade_nd / "fd_f0_regrade.py")
    rec["inputs_sha256"]["fd_f0_regrade.py@da5f157f"] = got
    control("pin fd_f0_regrade.py", got == REGRADE_SHA)
    if stop:
        return finish(rec, 8)
    sys.path.insert(0, str(a.regrade_nd))
    import fd_f0_regrade as fr   # noqa: E402

    with np.load(a.files / "s1_assembly.npz", allow_pickle=False) as z:
        s1m = json.loads(str(z["meta"]))
        f = np.asarray(z["f"], float)
        blocks = {k: np.asarray(z["C_" + k.replace(":", "_")], float) for k in s1m["blocks"]}
        Ce, Ct = np.asarray(z["C_e"], float), np.asarray(z["C_total"], float)
        Cmf, Cma = np.asarray(z["C_model_frac"], float), np.asarray(z["C_model_abs"], float)
    with np.load(a.files / "cmodel_5d.npz", allow_pickle=False) as z:
        S = np.asarray(z["S"], float)
    with np.load(a.files / "cresp.npz", allow_pickle=False) as z:
        Cx = np.asarray(z["C_resp"], float)
    ff = np.outer(f, f)
    scale = np.abs(np.diag(Ct)).max()
    TOL = fr.TOL
    # B0: fd_f0_regrade's control-4 loader checks (fd_f0_regrade.py@da5f157f:667-691)
    Cstat_rel = blocks["stat"] / ff
    ev = np.linalg.eigvalsh(Cstat_rel)
    b0 = {
        "f is positive on every cell": bool(f.shape == (16,) and np.all(f > 0)),
        "C_e is the sum of S1's blocks": bool(np.allclose(sum(blocks.values()), Ce, rtol=TOL, atol=TOL * scale)),
        "C_total = C_e + C_model_abs": bool(np.allclose(Ce + Cma, Ct, rtol=TOL, atol=TOL * scale)),
        "C_model_abs = diag(f) C_model diag(f)": bool(np.allclose(Cmf * ff, Cma, rtol=TOL, atol=TOL * scale)),
        "S is 3 x 16 and C_model = S^T S": bool(S.shape == (3, 16) and np.allclose(S.T @ S, Cmf, rtol=TOL, atol=TOL * np.abs(np.diag(Cmf)).max())),
        "C_stat,rel is full rank": bool(ev.min() > 0 and int(np.sum(ev > TOL * ev.max())) == 16),
        "C_resp is a finite symmetric 16 x 16": bool(Cx.shape == (16, 16) and np.all(np.isfinite(Cx)) and np.allclose(Cx, Cx.T, rtol=TOL, atol=TOL * np.abs(Cx).max())),
    }
    control("B0", all(b0.values()), b0)
    # recorded, not gated (T2B §1 states the seed block is zero; M2 excludes it by construction either way)
    rec["seed_block"] = {"present": "seed" in blocks,
                         "max_abs_relative": float(np.max(np.abs(blocks["seed"] / ff))) if "seed" in blocks else None}
    if stop:
        return finish(rec, 8)
    Ce_rel, Cx_rel = Ce / ff, Cx / ff

    repo = a.repo
    f1 = json.loads((repo / f"{D}/readout/fd_f1_readout.json").read_text())
    dp = json.loads((repo / f"{D}/data-product/fd_data_product.json").read_text())
    truths = {t["name"]: t for t in f1["truths"]}
    names = F0B_TWELVE + F1_FOUR
    control("the 16 records are graded in the F1 readout", all(n in truths and truths[n]["graded"] for n in names))
    if stop:
        return finish(rec, 8)

    # B1: b and sqrt(diag N) from the table reproduce the readout's bias and noise_sigma
    tables = {k: np.load(a.files / k, allow_pickle=False) for k in ("fd_f1_experiments.npz", "fd_f0b_experiments.npz")}

    def estimate(name, table):
        key = "r_" + name.replace(":", "_")
        if key not in table.files:
            return None
        R = np.asarray(table[key], float)
        t = truths[name]
        if t["row"] in (3, 8):
            return R[0], np.zeros((16, 16))
        if t["row"] in (1, 2, 4, 7):
            b, N, _ = fr.unweighted(R)
            return b, N
        return None

    est, b1 = {}, {}
    for n in names:
        t = truths[n]
        used = None
        for tab in ("fd_f1_experiments.npz", "fd_f0b_experiments.npz") if n in F0B_TWELVE else ("fd_f1_experiments.npz",):
            e = estimate(n, tables[tab])
            if e is None:
                continue
            ok = close(e[0], t["bias"]) and close(np.sqrt(np.diag(e[1])), t["noise_sigma"])
            if ok:
                used = tab
                est[n] = e
                break
        b1[n] = {"table": used, "pass": used is not None}
    control("B1", all(v["pass"] for v in b1.values()), b1)
    if stop:
        return finish(rec, 8)

    # B2: the existing grade, M0 = leave_out(C_e/ff, S, own) + C_resp/ff (fd_f0_regrade.py@da5f157f:787)
    M0 = {}
    b2 = {}
    for n in names:
        own = truths[n]["own_vertex"]
        M0[n] = fr.leave_out(Ce_rel, S, own) + Cx_rel
        g = fr.grade(est[n][0], est[n][1], M0[n])
        ok = close(g["chi2"], truths[n]["grade"]["chi2"]) and close(g["z"], truths[n]["grade"]["z"])
        b2[n] = {"pass": bool(ok), "chi2_rel_diff": relmax([g["chi2"]], [truths[n]["grade"]["chi2"]]),
                 "z_max_rel_diff": relmax(g["z"], truths[n]["grade"]["z"])}
    control("B2", all(v["pass"] for v in b2.values()), b2)

    # B3: f, C_e and C_resp equal the committed data product's
    b3 = {"f": close(f, dp["f"]), "C_e": close(Ce, dp["matrices"]["C_e"]), "C_resp": close(Cx, dp["matrices"]["C_resp"])}
    control("B3", all(b3.values()), {k: bool(v) for k, v in b3.items()})
    if stop:
        return finish(rec, 8)

    # the variants (formed only now)
    variants = {"M1": ("(C_e + C_resp)/ff^T", Ce_rel + Cx_rel), "M2": ("C_stat/ff^T", Cstat_rel),
                "M3": ("(C_stat + C_resp)/ff^T", Cstat_rel + Cx_rel)}
    out, counts = {}, {v: {} for v in ["existing"] + list(variants)}
    for n in names:
        t = truths[n]
        b, N = est[n]
        row = {"row": t["row"], "group": t["group"], "own_vertex": t["own_vertex"], "table": b1[n]["table"],
               "existing": summary(t["grade"]) | {"matrix": t.get("grade_matrix", "C_total + C_resp")}}
        for v, (label, M) in variants.items():
            row[v] = summary(fr.grade(b, N, M)) | {"matrix": label}
        out[n] = row
        for v in counts:
            counts[v].setdefault(t["group"], {"cells_abs_z_gt_2": 0, "cells": 0, "records": 0})
            c = counts[v][t["group"]]
            c["cells_abs_z_gt_2"] += len(row[v]["cells_abs_z_gt_2"])
            c["cells"] += 16
            c["records"] += 1
    rec["records"] = out
    rec["abs_z_gt_2_by_group"] = {"label": "descriptive counts only; no threshold is applied", **counts}
    rec["matrices"] = {k: v[0] for k, v in variants.items()} | {"N": "each record's own noise of its mean (0 for rows 3, 8)"}
    return finish(rec, 0)


if __name__ == "__main__":
    sys.exit(main())
