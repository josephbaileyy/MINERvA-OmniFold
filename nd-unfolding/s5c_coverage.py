#!/usr/bin/env python3
"""Tier-S coverage evaluation of the s5c contract (frozen with it; run only after validation completes).

For every reported functional f of the contract (43 M1 functionals, the supported cells of the joint
partition J, the integrated total) and every grid point g, it counts the validation experiments whose
68% interval ``f_hat +- sigma_f`` and 95% interval ``f_hat +- 1.96 sigma_f`` contain the experiment's
own true value ``f_true``, where ``sigma_f = sqrt(u_f' C u_f)`` and ``C`` is the contract's fixed
statistical covariance (the sample covariance, ddof=1, of the declared bootstrap replicas).

Gate (contract ``coverage.gate``): the one-sided Clopper-Pearson lower bound at level
``0.05 / (F * G)`` must exceed 0.66 (68%) for every (f, g), and separately 0.94 (95%) -- two
families, each simultaneous at 95%. The experiment population is exactly the contract's declared
seed range per grid point; a missing experiment is reported, never silently dropped, and the
gate refuses to evaluate unless every declared experiment is present.

MEASURES: interval coverage of the frozen construction over the declared grid. CANNOT AUTHORIZE:
coverage outside the grid, at other nuisance settings, or of any other interval construction.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

import project_cov_nd as pc
import s5c_samplesize as ss

AXES = ["pt", "pz", "eavail", "q3", "W"]


def reported_functionals(contract: dict) -> tuple[np.ndarray, list[str]]:
    """Rows over the full 65,856-cell grid (cells outside support carry zero)."""
    shape = tuple(len(pc.AXIS_EDGES[a]) - 1 for a in AXES)
    n = int(np.prod(shape))
    cells = np.arange(n)
    idx = np.unravel_index(cells, shape)
    dst_shape = (shape[2], shape[4])
    hit = np.unique(np.ravel_multi_index((idx[2], idx[4]), dst_shape))
    dst_index_of = -np.ones(int(np.prod(dst_shape)), dtype=int)
    dst_index_of[hit] = np.arange(hit.size)
    M, _ = pc.build_projection(AXES, ["eavail", "W"], cells, shape, dst_shape, dst_index_of)
    rows = [M, np.ones((1, n))]
    names = [f"EW{i}" for i in range(M.shape[0])] + ["EW_all_ones"]
    vol = np.ones(n)
    coarse_idx = []
    J = contract["measurement"]["partition_J"]
    for k, ax in enumerate(AXES):
        fine = np.asarray(pc.AXIS_EDGES[ax], float)
        vol *= np.diff(fine)[idx[k]]
        centers = 0.5 * (fine[:-1] + fine[1:])[idx[k]]
        ce = np.asarray(J["edges"][ax], float)
        coarse_idx.append(np.clip(np.searchsorted(ce, centers, side="right") - 1, 0, len(ce) - 2))
    cshape = tuple(len(J["edges"][ax]) - 1 for ax in AXES)
    cell = np.ravel_multi_index(coarse_idx, cshape)
    for c in J["supported_cells"]:
        rows.append(np.where(cell == c, vol, 0.0)[None, :])
        names.append(f"J{c}")
    rows.append(vol[None, :])
    names.append("total_integrated")
    return np.vstack(rows), names


def stat_covariance(U: np.ndarray, boot_dir: Path, first: int, last: int) -> np.ndarray:
    reps = []
    for b in range(first, last + 1):
        f = boot_dir / f"boot_b{b}.npz"
        if not f.exists():
            raise SystemExit(f"missing bootstrap replica {f}")
        reps.append(U @ np.load(f, allow_pickle=False)["xsec_flat"])
    R = np.array(reps)
    return np.cov(R, rowvar=False, ddof=1)


def evaluate(U, sigma, exp_dir: Path, truth_tag: str, first: int, last: int, b_rel=None) -> dict:
    """b_rel (contract amendment 3, F2 revision 1): per-functional relative closure-bias allowance,
    added LINEARLY to each half-width as b_rel * |f_hat|; None reproduces the frozen construction."""
    hits68 = np.zeros(U.shape[0], int)
    hits95 = np.zeros(U.shape[0], int)
    missing = []
    for s in range(first, last + 1):
        f = exp_dir / f"{truth_tag}_s{s}.npz"
        if not f.exists():
            missing.append(s)
            continue
        z = np.load(f, allow_pickle=False)
        fh = U @ z["xsec_flat"]
        d = np.abs(fh - U @ z["xtrue_flat"])
        allow = 0.0 if b_rel is None else b_rel * np.abs(fh)
        hits68 += d <= allow + sigma
        hits95 += d <= allow + 1.96 * sigma
    return {"n_declared": last - first + 1, "n_present": last - first + 1 - len(missing),
            "missing": missing[:50], "hits68": hits68.tolist(), "hits95": hits95.tolist()}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--contract", type=Path, required=True)
    ap.add_argument("--experiments", type=Path, required=True, help="directory of validation products")
    ap.add_argument("--bootstrap", type=Path, required=True, help="directory of the declared replicas")
    ap.add_argument("--bias-allowance", type=Path, default=None,
                    help="contract amendment 3: state/s5c/d1/bias_allowance.json (F2 revision 1)")
    ap.add_argument("--interim", type=int, default=None,
                    help="contract amendment 3 futility look: evaluate only the first N declared seeds of "
                         "each grid point; verdict FUTILITY-FAIL if any one-sided CP UPPER bound at "
                         "0.05/(F*G) is below its threshold, else CONTINUE (never PASS)")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    contract = json.loads(a.contract.read_text())
    cov = contract["coverage"]
    U, names = reported_functionals(contract)
    b0, b1 = cov["sigma"]["bootstrap_seeds"]
    C = stat_covariance(U, a.bootstrap, b0, b1)
    sigma = np.sqrt(np.diag(C))
    b_rel = None
    if a.bias_allowance is not None:
        ba = json.loads(a.bias_allowance.read_text())
        if ba["functional_names"] != names:
            raise SystemExit("bias allowance functional order differs from the contract's")
        b_rel = np.asarray(ba["b_rel"], float)
    G = len(cov["grid"])
    m = U.shape[0] * G
    alpha = 0.05 / m
    out = {"schema": "s5c-coverage/1", "n_functionals": int(U.shape[0]), "grid_points": G,
           "bias_allowance": None if a.bias_allowance is None else str(a.bias_allowance),
           "per_comparison_alpha": alpha, "functional_names": names, "sigma": sigma.tolist(), "grid": []}
    complete, passed = True, True
    for g in cov["grid"]:
        s0, s1 = g["validation_seeds"]
        if a.interim is not None:
            s1 = min(s1, s0 + a.interim - 1)
        tag = f"{g['truth']}_a{g['amplitude']:g}"
        res = evaluate(U, sigma, a.experiments, tag, s0, s1, b_rel)
        n = res["n_present"]
        complete &= n == res["n_declared"]
        lcb68 = [ss.cp_lower(int(k), n, alpha) if n else 0.0 for k in res["hits68"]]
        lcb95 = [ss.cp_lower(int(k), n, alpha) if n else 0.0 for k in res["hits95"]]
        ucb68 = [ss.cp_upper(int(k), n, alpha) if n else 1.0 for k in res["hits68"]]
        ucb95 = [ss.cp_upper(int(k), n, alpha) if n else 1.0 for k in res["hits95"]]
        futile = min(ucb68) < cov["gate"]["lcb68_threshold"] or min(ucb95) < cov["gate"]["lcb95_threshold"]
        ok = min(lcb68) > cov["gate"]["lcb68_threshold"] and min(lcb95) > cov["gate"]["lcb95_threshold"]
        passed &= ok
        out["grid"].append({**g, **res, "lcb68": lcb68, "lcb95": lcb95, "min_lcb68": min(lcb68),
                            "min_lcb95": min(lcb95), "argmin68": names[int(np.argmin(lcb68))],
                            "argmin95": names[int(np.argmin(lcb95))],
                            "coverage68_min": min(h / n for h in res["hits68"]) if n else None,
                            "coverage95_min": min(h / n for h in res["hits95"]) if n else None, "pass": ok,
                            "min_ucb68": min(ucb68), "min_ucb95": min(ucb95), "futile": futile})
    out["complete"] = complete
    if a.interim is not None:
        out["interim_n"] = a.interim
        out["verdict"] = ("INCOMPLETE" if not complete else
                          ("FUTILITY-FAIL" if any(gg["futile"] for gg in out["grid"]) else "CONTINUE"))
    else:
        out["verdict"] = ("INCOMPLETE" if not complete else ("PASS" if passed else "FAIL"))
    a.out.write_text(json.dumps(out, indent=1))
    print(json.dumps({"verdict": out["verdict"], **{f"g{i}": {k: gg[k] for k in ("truth", "n_present", "min_lcb68", "min_lcb95", "argmin68", "argmin95")}
                                                    for i, gg in enumerate(out["grid"])}}, indent=1))
    return {"PASS": 0, "FAIL": 1, "INCOMPLETE": 4, "FUTILITY-FAIL": 1, "CONTINUE": 5}[out["verdict"]]


if __name__ == "__main__":
    raise SystemExit(main())
