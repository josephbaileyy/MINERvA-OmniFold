#!/usr/bin/env python3
"""W1 (PACKET-20261005 §6; DECISION-20261006 item 3): the frozen joint tests restricted to matched 3x3 coarse
projections of the same J cells.

For each null G and statistic t (total or shape), it projects the frozen 109-cell quantities onto
P_ptpl = (p_T, p_par) and P_eW = (E_avail, W) by summing the cell-integrated J values over the dropped axes, and
recomputes t with:
- the projected metric P V P' + diag(P Var(mu));
- the same per-draw prediction-error draw (seeded as the frozen evaluator, then projected);
- the projected variant vectors (each 109-dimensional variant S(c), c in {0, 1/2, 1}, and +-kappa delta_M1 is
  projected; nothing is rebuilt in the projected metric);
- the claim rule (largest p over the variants).

The criterion (fixed in the packet before any W1 run) is applied by ``--criterion``: (G, t) shows discrimination
beyond the matched coarse projections iff its recorded 5D t-test is rejected and BOTH projected t-tests have
claim p >= 0.05, under every supplied reading of the missing-seed resolution.

Inputs: the npz files written by ``publication/release/extract_inference_sufficient.py``, one per D2 reading:
(a) the union with S recomputed, and (b) the recovered draws with the frozen S. Report-only: no Holm family,
no frozen decision changed.

MEASURES: projected-test p-values. CANNOT AUTHORIZE: any change to a frozen decision; any comparison other than
the two matched coarse projections; a claim about published lower-dimensional results.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent / "release"))
import replay_inference as rp  # noqa: E402

GRID = (3, 3, 3, 3, 3)  # (pt, pz, eavail, q3, W): nd-unfolding/s5p_stage1_inspect.py J_EDGES, C order
PROJECTIONS = {"ptpl": (0, 1), "eW": (2, 4)}


def projection_matrix(supported: np.ndarray, dom: np.ndarray, keep_axes: tuple[int, int]) -> np.ndarray:
    """Rows: the 9 cells of the kept axes that receive at least one in-domain J cell; columns: the in-domain J
    cells. Entries 1 (cell-integrated values are additive)."""
    idx = np.unravel_index(np.asarray(supported)[dom], GRID)
    tgt = idx[keep_axes[0]] * GRID[keep_axes[1]] + idx[keep_axes[1]]
    rows = np.unique(tgt)
    P = (tgt[None, :] == rows[:, None]).astype(float)
    return P


def projected_statistics(F, mu, var, V, dom, P, seed0, draw=True, seeds=None):
    Vd = V[np.ix_(dom, dom)]
    Wp = P @ Vd @ P.T + np.diag(P @ var[dom])
    Winv = np.linalg.inv(Wp)
    keys = seeds if seeds is not None else np.arange(len(F))
    tt, ts = [], []
    for i, f in enumerate(F):
        eps = (np.random.default_rng([int(seed0), int(keys[i]), 0x4A02]).normal(size=mu.size) * np.sqrt(var)
               if draw else 0.0)
        r_mu = mu + eps
        fp, mp = P @ f[dom], P @ r_mu[dom]
        tt.append(rp.stat_total(fp, mp, Winv))
        ts.append(rp.stat_shape(fp, mp, Wp))
    return np.array(tt), np.array(ts)


def run(npz: Path, manifest: Path) -> dict:
    z = np.load(npz, allow_pickle=False)
    man = json.loads(manifest.read_text())
    V, f_data, supported = z["V"], z["f_data"], z["supported_cells"]
    coefs = man["shift_coefficients"]
    out = {"npz": str(npz), "npz_sha256": man.get("npz_sha256"), "group": man.get("group"), "tests": {}}
    for key, nm in man["nulls"].items():
        F, seeds = z[f"F__{key}"], z[f"seeds__{key}"]
        mu, var, dom = z[f"mu__{key}"], z[f"var__{key}"], z[f"dom__{key}"].astype(bool)
        S = z[f"S__{key}"] if f"S__{key}" in z.files else None
        variants = [(str(c), (c * S if S is not None else None)) for c in (coefs if S is not None else [0.0])]
        if nm["m1"] is not None:
            d1, ka = z[f"d1__{key}"], nm["m1"]["kappa"]
            variants += [(f"m1+{ka}", ka * d1), (f"m1-{ka}", -ka * d1)]
        for proj, axes in PROJECTIONS.items():
            P = projection_matrix(supported, dom, axes)
            tt_o, ts_o = projected_statistics(f_data[None, :], mu, var, V, dom, P, 0, draw=False)
            per = {}
            for name, sv in variants:
                tt_n, ts_n = projected_statistics(F + (sv if sv is not None else 0.0), mu, var, V, dom, P,
                                                  nm["surrogate_seed0"], seeds=seeds)
                per[name] = {"total": rp.mc_pvalue(tt_o[0], tt_n), "shape": rp.mc_pvalue(ts_o[0], ts_n)}
            for s in ("total", "shape"):
                claim = max(per.values(), key=lambda v: v[s]["p"])[s]
                out["tests"][f"{key}:{s}:{proj}"] = {"cells": int(P.shape[0]), "claim": claim,
                                                     "variants": {n: v[s]["p"] for n, v in per.items()}}
    return out


def criterion(readings: list[dict], recorded: dict) -> dict:
    """Apply the fixed W1 criterion. ``recorded`` maps 'G:t' to the recorded 5D decision string."""
    res = {}
    for gt, dec in recorded.items():
        ok = dec == "rejected"
        detail = []
        for r in readings:
            for proj in PROJECTIONS:
                p = r["tests"][f"{gt}:{proj}"]["claim"]["p"]
                detail.append({"reading": r["group"], "projection": proj, "claim_p": p})
                ok = ok and p >= 0.05
        res[gt] = {"recorded_5d": dec, "joint_beyond_matched_coarse_projections": bool(ok), "detail": detail}
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--npz", type=Path, action="append", required=True, help="one per D2 reading")
    ap.add_argument("--recorded", type=Path, required=True, help="frozen joint-evaluate.json (recorded decisions)")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        raise SystemExit(f"refusing to overwrite {a.out}")
    readings = [run(p, Path(str(p) + ".manifest.json")) for p in a.npz]
    frozen = json.loads(a.recorded.read_text())
    recorded = {k: v["decision"] for k, v in frozen["decisions"].items()}
    result = {"schema": "w1-projected-tests/1", "readings": readings, "criterion": criterion(readings, recorded),
              "report_only": True}
    a.out.write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v["joint_beyond_matched_coarse_projections"] for k, v in result["criterion"].items()}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
