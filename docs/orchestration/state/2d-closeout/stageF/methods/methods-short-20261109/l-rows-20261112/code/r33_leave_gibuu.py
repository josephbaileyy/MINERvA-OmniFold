#!/usr/bin/env python3
"""Row 3.3: which fake-data grades depend on the GiBUU component of C_model (leave-one-out). Descriptive, as T2B.

Usage (repo root, python -I):
  r33_leave_gibuu.py --files <dir with T2B's five fetched files> --regrade-nd <dir with fd_f0_regrade.py@da5f157f>
                     --out <r33.json>

Reuses T2B's (fd/tier2-20261110/t2b/code/t2b_grade.py) pins, loaders and records unchanged: it imports that module
and runs its own B0-B3 path by calling main() into a scratch output first, refusing unless T2B's rc is 0. Then for
each of T2B's 16 records it forms the existing grade matrix M0 = leave_out(C_e/ff, S, own) + C_resp/ff and the
variant M0-G = C_e/ff + sum_{j not in {own, gibuu}} s_j s_j^T + C_resp/ff (identical to M0 when own is gibuu), and
grades each record's b, N against both with fd_f0_regrade.grade. Control: M0's grade must reproduce the F1 readout's
chi2 and z (T2B's B2, re-run here). No criterion, trigger or grade changes; no p-value is written.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

import numpy as np

REPO = Path.cwd()
T2B = REPO / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/tier2-20261110/t2b/code/t2b_grade.py"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", required=True, type=Path)
    ap.add_argument("--regrade-nd", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args()
    spec = importlib.util.spec_from_file_location("t2b_grade", T2B)
    tg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tg)
    with tempfile.TemporaryDirectory() as td:
        rc = tg.main(["--files", str(a.files), "--regrade-nd", str(a.regrade_nd), "--repo", str(REPO),
                      "--out", str(Path(td) / "t2b.json")])
        if rc != 0:
            print("STOP: T2B's controls did not pass on these inputs"); return 8
        t2b = json.loads((Path(td) / "t2b.json").read_text())
    sys.path.insert(0, str(a.regrade_nd))
    import fd_f0_regrade as fr  # noqa: E402

    with np.load(a.files / "s1_assembly.npz", allow_pickle=False) as z:
        f, Ce = np.asarray(z["f"], float), np.asarray(z["C_e"], float)
    with np.load(a.files / "cmodel_5d.npz", allow_pickle=False) as z:
        S = np.asarray(z["S"], float)
    with np.load(a.files / "cresp.npz", allow_pickle=False) as z:
        Cx = np.asarray(z["C_resp"], float)
    ff = np.outer(f, f)
    Ce_rel, Cx_rel = Ce / ff, Cx / ff
    D = tg.D
    f1 = json.loads((REPO / f"{D}/readout/fd_f1_readout.json").read_text())
    truths = {t["name"]: t for t in f1["truths"]}
    tables = {k: np.load(a.files / k, allow_pickle=False) for k in ("fd_f1_experiments.npz", "fd_f0b_experiments.npz")}
    gi = fr.VERTICES.index("gibuu")
    out, ctl = {}, {}
    for n, row in t2b["records"].items():
        t = truths[n]
        R = np.asarray(tables[row["table"]]["r_" + n.replace(":", "_")], float)
        if t["row"] in (3, 8):
            b, N = R[0], np.zeros((16, 16))
        else:
            b, N, _ = fr.unweighted(R)
        own = t["own_vertex"]
        M0 = fr.leave_out(Ce_rel, S, own) + Cx_rel
        keep = [j for j, v in enumerate(fr.VERTICES) if v != own and j != gi]
        MG = Ce_rel + S[keep].T @ S[keep] + Cx_rel
        g0, gG = fr.grade(b, N, M0), fr.grade(b, N, MG)
        ok = tg.close(g0["chi2"], t["grade"]["chi2"]) and tg.close(g0["z"], t["grade"]["z"])
        ctl[n] = bool(ok)
        out[n] = {"row": t["row"], "group": t["group"], "own_vertex": own, "same_matrix": own == "gibuu",
                  "existing": tg.summary(g0), "leave_gibuu": tg.summary(gG),
                  "chi2_change": gG["chi2"] - g0["chi2"],
                  "cells_abs_z_gt_2_added": sorted(set(gG["cells_abs_z_gt_2"]) - set(g0["cells_abs_z_gt_2"])),
                  "cells_abs_z_gt_2_removed": sorted(set(g0["cells_abs_z_gt_2"]) - set(gG["cells_abs_z_gt_2"]))}
    for r in out.values():
        for k in ("existing", "leave_gibuu"):
            r[k].pop("p", None)
    rec = {"schema": "r33-leave-gibuu/1", "label": "descriptive only: no criterion, trigger or grade changes; no p-value",
           "t2b_code_path": str(T2B.relative_to(REPO)), "t2b_code_bytes_digest_sha256": hashlib.sha256(T2B.read_bytes()).hexdigest(),
           "t2b_inputs_paths": tg.FETCHED_FROM,   # the fetched files by full path (T2B section 2), as T2B records them
           "t2b_controls_rerun": {k: v["pass"] for k, v in t2b["controls"].items()},
           "control_M0_reproduces_readout": ctl, "vertices": list(fr.VERTICES),
           "S_row_norms": {v: float(np.linalg.norm(S[j])) for j, v in enumerate(fr.VERTICES)},
           "records": out}
    a.out.write_text(json.dumps(rec, indent=1) + "\n")
    ok = all(ctl.values())
    for n, r in out.items():
        print(f"{n:28s} own={r['own_vertex'] or '-':9s} chi2 {r['existing']['chi2']:9.2f} -> {r['leave_gibuu']['chi2']:9.2f}"
              f"  |z|>2 {len(r['existing']['cells_abs_z_gt_2'])} -> {len(r['leave_gibuu']['cells_abs_z_gt_2'])}"
              f"  max|z| {r['existing']['max_abs_z']:.2f} -> {r['leave_gibuu']['max_abs_z']:.2f}")
    print("R33 " + ("OK" if ok else "CONTROL FAILED"))
    return 0 if ok else 5


if __name__ == "__main__":
    sys.exit(main())
