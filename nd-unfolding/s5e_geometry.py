#!/usr/bin/env python3
"""s5e diagnosis D6(i): the input geometry that bounds what the reco data can say about the truth axes.

On a fixed 2M-row subsample of reco- and truth-passing MC rows inside the 5D grid at both levels
(seed 20260925, 50/50 train/test), a fixed LightGBM regressor (200 trees, 63 leaves, learning rate 0.1,
deterministic) reports the held-out fraction of variance explained (R^2) for:

* reco q3 and reco W from reco (pT, p_parallel, E_avail) -- how far the reco space is three-dimensional;
* truth q3 and truth W from truth (pT, p_parallel, E_avail) -- how far the truth space is;
* reco E_avail from truth (pT, p_parallel, E_avail) and from all five truth axes -- whether the
  detector's E_avail responds to truth W and q3 beyond truth E_avail (a gain means a truth-level W/q3
  change moves reco E_avail, so a truth E_avail change and a truth W/q3 change can look alike at reco);
* reco W from truth (pT, p_parallel, E_avail) and from all five truth axes.

MEASURES: regression-explained variance on the analysis MC. CANNOT AUTHORIZE: a cause by itself; it is
the geometric context for the observability items D6(ii)-(iii).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import s5c_unfold  # noqa: E402
import s5n_pseudo  # noqa: E402

AX = {"pt": 0, "pz": 1, "eavail": 2, "q3": 3, "W": 4}
TASKS = [
    ("reco_q3 | reco(pt,pz,eavail)", "reco", ["pt", "pz", "eavail"], "reco", "q3"),
    ("reco_W | reco(pt,pz,eavail)", "reco", ["pt", "pz", "eavail"], "reco", "W"),
    ("truth_q3 | truth(pt,pz,eavail)", "gen", ["pt", "pz", "eavail"], "gen", "q3"),
    ("truth_W | truth(pt,pz,eavail)", "gen", ["pt", "pz", "eavail"], "gen", "W"),
    ("reco_eavail | truth(pt,pz,eavail)", "gen", ["pt", "pz", "eavail"], "reco", "eavail"),
    ("reco_eavail | truth(all five)", "gen", ["pt", "pz", "eavail", "q3", "W"], "reco", "eavail"),
    ("reco_W | truth(pt,pz,eavail)", "gen", ["pt", "pz", "eavail"], "reco", "W"),
    ("reco_W | truth(all five)", "gen", ["pt", "pz", "eavail", "q3", "W"], "reco", "W"),
]


def in_grid(x: np.ndarray, edges: list) -> np.ndarray:
    ok = np.ones(x.shape[0], bool)
    for k, e in enumerate(edges):
        ok &= (x[:, k] >= e[0]) & (x[:, k] < e[-1])
    return ok


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--npz", type=Path, required=True)
    ap.add_argument("--expect-npz-sha256", required=True)
    ap.add_argument("--rows", type=int, default=2_000_000)
    ap.add_argument("--threads", type=int, default=int(os.environ.get("SLURM_CPUS_PER_TASK", "32")))
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        print(f"refusing to overwrite {a.out}", file=sys.stderr)
        return 3
    sha = s5n_pseudo.sha256_path(a.npz)
    if sha != a.expect_npz_sha256:
        print(f"npz sha256 {sha} differs", file=sys.stderr)
        return 4
    from lightgbm import LGBMRegressor

    d = s5c_unfold.load_inputs(a.npz)
    edges = d["edges"]
    sel = d["pass_reco"] & d["pass_truth"] & in_grid(d["MCgen"], edges) & in_grid(d["MCreco"], edges)
    rows = np.flatnonzero(sel)
    rng = np.random.default_rng(20260925)
    rows = np.sort(rng.choice(rows, size=min(a.rows, rows.size), replace=False))
    train = rng.uniform(size=rows.size) < 0.5
    level = {"gen": d["MCgen"][rows].astype(float), "reco": d["MCreco"][rows].astype(float)}
    out = {"schema": "s5e-geometry/1", "input_npz_sha256": sha, "rows_eligible": int(sel.sum()),
           "rows_used": int(rows.size), "train_fraction": float(train.mean()), "r2_test": {},
           "code_sha256": s5n_pseudo.sha256_path(Path(__file__).resolve())}
    corr = np.corrcoef(np.column_stack([level["reco"][:, AX["eavail"]], level["gen"][:, AX["eavail"]],
                                        level["gen"][:, AX["W"]], level["gen"][:, AX["q3"]]]), rowvar=False)
    out["pearson_reco_eavail_with"] = {"truth_eavail": float(corr[0, 1]), "truth_W": float(corr[0, 2]),
                                       "truth_q3": float(corr[0, 3])}
    for label, xl, xs, yl, y in TASKS:
        X = level[xl][:, [AX[v] for v in xs]]
        t = level[yl][:, AX[y]]
        m = LGBMRegressor(n_estimators=200, num_leaves=63, learning_rate=0.1, deterministic=True,
                          force_row_wise=True, num_threads=a.threads, random_state=7, verbose=-1)
        m.fit(X[train], t[train])
        p = m.predict(X[~train])
        resid = t[~train] - p
        out["r2_test"][label] = float(1.0 - resid.var() / t[~train].var())
        print(json.dumps({label: out["r2_test"][label]}), flush=True)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
