#!/usr/bin/env python3
"""RSN regrade (RSN-DECLARATION.md §3.2): the 22 fake-data records of the committed F1 readout (F0b's 18 truths and
the four held-out GENIE v3 records), graded against the reported covariance with C_model replaced by each arm's C^V.
Numpy only; runs on a login node.

    rsn_regrade.py --table fd_f1_experiments.npz --s1-npz s1_assembly.npz --extra-block cpl_block.npz
                   --flux-constraint <NuE constraint file> --rsn-cmodel <OUT>/cmodel/rsn_cmodel.npz --out <OUT>/regrade.json

Each record's bias b and the noise N of its mean are rebuilt from the committed per-experiment table, exactly as
fd_f0_regrade.py builds them (its own functions: unweighted, weighted, the row-4 offsets and control 7). The matrices
are fd_f0_regrade's, with S replaced: C^(T) = C_e/(f f^T) + sum_{j != own(T)} s_j^V s_j^V^T + C_x/(f f^T), and the
same for the in-sample, sensitivity, eight-cell and model-only matrices. Nothing else changes: the truths, the
estimators, the noise, the triggers (|z| > 2 per cell, p < 0.01 per truth) and the groups.

Refuses, writing nothing, unless:
  every input matches its pinned sha256;
  NC-R: with cmodel_5d.json's own S, every record's bias and every grade field (z, chi2, p, the flagged cells, the
      p < 0.01 flag, graded, listed), control 7's verdict and the per-group counts reproduce the committed F1 readout;
  the arm file's nominal S is cmodel_5d.json's S bitwise;
  C-INV: under G6, which changes only GiBUU's row, every record whose own vertex is GiBUU grades bitwise as nominal.
Every output passes fd_f0_regrade.LeakGuard first.

MEASURES: arithmetic on committed records and pinned matrices. CANNOT AUTHORIZE: any claim, or a change to a grade,
a criterion or C_model.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ND = _HERE.parent
_ROOT = _ND.parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import fd_f0_regrade as R  # noqa: E402

FD = _ROOT / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd"
F1_READOUT = FD / "with-cpl/readout/fd_f1_readout.json"
F1_PREP_SUMS = FD / "receipts-f1/run/cluster/f1b3/prep/f1-prep-SHA256SUMS"
CMODEL_JSON = _ND / "pv-ladder/readouts/cmodel_5d.json"
PINS = {
    "table": "997c7dae34ef9703291baece51eed05f3dd7d38a043630cac9667efaad2775bc",
    "f1_readout": "5ccc89e58096a14ab8dc0e3e6f508ca4b2b546b629077560a09a4596cde40395",
    "f1_prep_sums": "981b188b03a7e75b904489fa1bf15bd818ef4b72f93a8beba4a906eb3122a480",
    "s1_npz": R.PINS["s1_npz"],
    "extra_block": "d9aa32fdb64357760348c9ccbc32fbea81d517f0f0786eedf17ab4946eaca59f",
    "cmodel_json": R.PINS["cmodel_json"],
}
EXTRA_KEY = "C_resp_plus_C_PL5D"
SUBGRADES = ("grade", "model_only", "in_sample", "sensitivity", "p_parallel_lt_4p5")
RTOL = 1e-10


class Refuse(SystemExit):
    def __init__(self, why):
        super().__init__(f"[FAIL] {why}")


def require(path: Path, want: str, what: str) -> None:
    got = R.sa.sha256(Path(path))
    if got != want:
        raise Refuse(f"{what} {path}: sha256 {got} != {want}")


def truths(f1_prep_sums: Path) -> tuple:
    return R.TRUTHS + R.f1_truths(R.sa.load_manifest(f1_prep_sums))


def estimates(TR: tuple, table: dict, w_all: np.ndarray) -> tuple[dict, bool]:
    """(b, N, B, how[, b uncorrected]) per record and control 7's verdict, as fd_f0_regrade.run builds them."""
    def r(name):
        return np.asarray(table[f"r_{name.replace(':', '_')}"], float)

    def flux(name):
        return np.asarray(table[f"flux_{name.replace(':', '_')}"], int)

    est, offsets = {}, {}
    for t in TR:
        Rr = r(t["name"])
        if t["row"] in (3, 8):
            est[t["name"]] = (Rr[0], np.zeros((R.N_CELLS, R.N_CELLS)), None, "noise-free closure (N = 0)")
        elif t["row"] in (1, 2, 4, 7):
            b, N, B = R.unweighted(Rr)
            est[t["name"]] = (b, N, B, "unweighted mean")
        if t["row"] == 4:
            bw, Nw, Beff = R.weighted(r("cal:" + t["name"]), w_all[flux("cal:" + t["name"])])
            b4, N4, _ = est[t["name"]][:3]
            offsets[t["name"]] = {"O": bw - b4, "N_O": Nw + N4}
    x, y = R.OFFSET_PAIR
    g = R.grade(offsets[x]["O"] - offsets[y]["O"], offsets[x]["N_O"] + offsets[y]["N_O"],
                np.zeros((R.N_CELLS, R.N_CELLS)))
    offset_pass = bool(g["p"] >= 0.01)
    for t in R.TRUTHS:
        if t["row"] != 6:
            continue
        bw, Nw, Beff = R.weighted(r(t["name"]), w_all[flux(t["name"])])
        o = offsets[t["ref"]]
        est[t["name"]] = (bw - o["O"], Nw + o["N_O"], Beff, "offset-corrected", bw)
    return est, offset_pass


def grade_all(TR: tuple, est: dict, offset_pass: bool, S: np.ndarray, Ce_rel, Cstat_rel, Cx_rel) -> dict:
    mats = {"C_total": R.leave_out(Ce_rel, S, None)}
    mats.update({f"minus_{v}": R.leave_out(Ce_rel, S, v) for v in R.VERTICES})
    recs, by = [], {}
    for t in TR:
        b, N = est[t["name"]][:2]
        graded = t["row"] != 6 or offset_pass
        C = (mats["C_total"] if t["own"] is None else mats[f"minus_{t['own']}"]) + Cx_rel
        rec = {"name": t["name"], "row": t["row"], "group": t["group"], "own_vertex": t["own"], "graded": graded,
               "bias": np.asarray(b).tolist(), "grade": R.grade(b, N, C),
               "model_only": R.grade(b, N, R.leave_out(Cstat_rel, S, t["own"]))}
        if t["own"] is not None:
            rec["in_sample"] = R.grade(b, N, mats["C_total"] + Cx_rel)
        if t.get("sens"):
            rec["sensitivity"] = R.grade(b, N, mats[f"minus_{t['sens']}"] + Cx_rel)
        if t["own"] == "gibuu":
            rec["p_parallel_lt_4p5"] = R.grade(b, N, C, R.GIBUU_CELLS)
        rec["listed"] = bool(graded and (rec["grade"]["cells_abs_z_gt_2"] or rec["grade"]["p_lt_0.01"]))
        recs.append(rec)
        if graded:
            gr = by.setdefault(t["group"], {"truths": 0, "cells": 0, "cells_abs_z_gt_2": 0, "truths_p_lt_0.01": 0})
            gr["truths"] += 1
            gr["cells"] += R.N_CELLS
            gr["cells_abs_z_gt_2"] += len(rec["grade"]["cells_abs_z_gt_2"])
            gr["truths_p_lt_0.01"] += int(rec["grade"]["p_lt_0.01"])
    sigma = np.sqrt(np.diag(mats["C_total"] + Cx_rel))
    return {"records": recs, "by_group": by, "listed": [r["name"] for r in recs if r["listed"]],
            "reported_relative_sigma": sigma.tolist()}


def same_grade(a: dict, b: dict) -> bool:
    return (np.allclose(a["z"], b["z"], rtol=RTOL, atol=1e-12) and np.isclose(a["chi2"], b["chi2"], rtol=RTOL, atol=0)
            and np.isclose(a["p"], b["p"], rtol=1e-8, atol=1e-14) and a["cells_abs_z_gt_2"] == b["cells_abs_z_gt_2"]
            and a["p_lt_0.01"] == b["p_lt_0.01"])


def reproduce(nom: dict, offset_pass: bool, readout: dict) -> None:
    """NC-R: the nominal regrade is the committed F1 readout, record for record."""
    old = {r["name"]: r for r in readout["truths"]}
    if [r["name"] for r in nom["records"]] != [r["name"] for r in readout["truths"]]:
        raise Refuse("NC-R: the records are not the committed readout's, in its order")
    if offset_pass != bool(readout["controls"]["offset_control_7"]["pass"]):
        raise Refuse("NC-R: control 7's verdict differs from the committed one")
    for rec in nom["records"]:
        o = old[rec["name"]]
        if not np.allclose(rec["bias"], o["bias"], rtol=1e-12, atol=1e-15):
            raise Refuse(f"NC-R: {rec['name']}'s bias differs from the committed one")
        if rec["graded"] != o["graded"] or rec["listed"] != o["listed"]:
            raise Refuse(f"NC-R: {rec['name']}'s graded or listed flag differs")
        for k in SUBGRADES:
            if (k in rec) != (k in o) or (k in rec and not same_grade(rec[k], o[k])):
                raise Refuse(f"NC-R: {rec['name']}'s {k} differs from the committed one")
    for gname, g in readout["triggers"]["by_group"].items():
        mine = nom["by_group"].get(gname, {})
        if any(mine.get(k) != g[k] for k in ("truths", "cells", "cells_abs_z_gt_2", "truths_p_lt_0.01")):
            raise Refuse(f"NC-R: group {gname}'s counts differ from the committed ones")


def invariant_g6(nom: dict, g6: dict) -> None:
    """C-INV: G6 changes GiBUU's row only, so a record graded without GiBUU's shift cannot move."""
    for a, b in zip(nom["records"], g6["records"]):
        if a["own_vertex"] == "gibuu" and a["grade"] != b["grade"]:
            raise Refuse(f"C-INV: {a['name']} (own vertex GiBUU) moved under G6")


def run(a) -> dict:
    if a.out.exists():
        raise Refuse(f"refusing to overwrite {a.out}")
    for key, path in (("table", a.table), ("f1_readout", a.f1_readout), ("f1_prep_sums", a.f1_prep_sums),
                      ("s1_npz", a.s1_npz), ("extra_block", a.extra_block), ("cmodel_json", a.cmodel_json)):
        require(path, PINS[key], key)
    TR = truths(a.f1_prep_sums)
    with np.load(a.table, allow_pickle=False) as z:
        table = {k: z[k] for k in z.files}
    if [str(x) for x in table["names"]] != [t["name"] for t in TR]:
        raise Refuse("the table's records are not fd_f0_regrade's F1 records")
    w_all = R.sa.flux_weights(a.flux_constraint)
    with np.load(a.s1_npz, allow_pickle=False) as z:
        meta = json.loads(str(z["meta"]))
        f = np.asarray(z["f"], float)
        Ce = np.asarray(z["C_e"], float)
        if "stat" not in meta["blocks"]:
            raise Refuse("S1's assembly has no stat block")
        Cstat = np.asarray(z["C_stat"], float)
    with np.load(a.extra_block, allow_pickle=False) as z:
        Cx = np.asarray(z[EXTRA_KEY], float)
    ff = np.outer(f, f)
    Ce_rel, Cstat_rel, Cx_rel = Ce / ff, Cstat / ff, Cx / ff
    S0 = np.asarray(json.loads(Path(a.cmodel_json).read_text())["S"], float)
    with np.load(a.rsn_cmodel, allow_pickle=False) as z:
        arms = {k[2:]: np.asarray(z[k], float) for k in z.files if k.startswith("S_")}
    if "nominal" not in arms or not np.array_equal(arms["nominal"], S0):
        raise Refuse("the arm file's nominal S is not cmodel_5d.json's")
    est, offset_pass = estimates(TR, table, w_all)
    out = {name: grade_all(TR, est, offset_pass, S, Ce_rel, Cstat_rel, Cx_rel) for name, S in arms.items()}
    reproduce(out["nominal"], offset_pass, json.loads(Path(a.f1_readout).read_text()))
    if "G6" in out:
        invariant_g6(out["nominal"], out["G6"])
    readout = {"schema": "rsn-regrade/1", "offset_control_7_pass": offset_pass, "arms": out,
               "controls": ["NC-R", "nominal S", "C-INV" if "G6" in out else None],
               "inputs_sha256": {**PINS, "rsn_cmodel": R.sa.sha256(Path(a.rsn_cmodel))},
               "code_sha256": {"rsn_regrade.py": R.sa.sha256(Path(__file__).resolve()),
                               "fd_f0_regrade.py": R.sa.sha256(Path(R.__file__).resolve())}}
    R.LeakGuard(f, []).check("the regrade JSON", readout)
    a.out.write_text(json.dumps(readout, indent=1) + "\n")
    for name, g in out.items():
        print(f"[rsn] {name}: listed {g['listed']}; " + "; ".join(
            f"{k} {v['cells_abs_z_gt_2']}/{v['cells']} cells, {v['truths_p_lt_0.01']}/{v['truths']} truths"
            for k, v in sorted(g["by_group"].items())))
    return readout


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--table", type=Path, required=True)
    ap.add_argument("--f1-readout", type=Path, default=F1_READOUT)
    ap.add_argument("--f1-prep-sums", type=Path, default=F1_PREP_SUMS)
    ap.add_argument("--s1-npz", type=Path, required=True)
    ap.add_argument("--extra-block", type=Path, required=True)
    ap.add_argument("--flux-constraint", type=Path, required=True)
    ap.add_argument("--cmodel-json", type=Path, default=CMODEL_JSON)
    ap.add_argument("--rsn-cmodel", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    run(ap.parse_args(argv))
    return 0


if __name__ == "__main__":
    sys.exit(main())
