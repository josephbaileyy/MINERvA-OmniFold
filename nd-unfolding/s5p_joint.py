#!/usr/bin/env python3
"""s5p Stage 7: the joint-5D generator tests on the J partition (evaluator; design frozen in contract amendment 5).

The joint cells are the reported cells of partition J (RD1's joint part; 109 cells). A test's domain may be a
declared subset (GiBUU: the cells with p_parallel < 6 GeV/c, KNOWN_ISSUES 82). For every experiment product
(``xsec_flat``) the cell integrals f = U x are formed, then the declared additive terms of the null model that
are not simulated at event level are drawn with the experiment's own recorded z values or seeds:

* lateral bands: + sum_b z_b Delta_b, Delta_b = (f(endpoint 1) - f(endpoint 0)) / 2 from the real-data endpoint
  unfolds (a linear-response surrogate; its symmetry check is reported);
* normalization: x (1 + 0.014 z);
* the data's rounding-scale noise: + N(0, diag s_num^2), s_num from the 20 real-data jitters (the pseudo-data
  are far less chaotic than the data; study N);
* the prediction's finite MC: the residual gets - eps, eps ~ N(0, diag Var(mu_G)) (from the prediction's sumw2).

``T_total = r' W^-1 r`` and ``T_shape`` (s5p_inference.stat_shape) with r = f - mu_G on the test domain and the
FIXED metric W = V + diag Var(mu_G), V the Ledoit-Wolf-shrunk covariance of the frozen development null
ensemble (built by ``build-v`` and committed before any calibration ensemble). p-values (k+1)/(B+1) against the
null's calibration ensemble, Holm over the declared family, power against the MnvTune null's ensemble, size from
independent validation ensembles.

MEASURES: the frozen joint statistics, p-values, power and size. CANNOT AUTHORIZE: a rejection outside the frozen
family, tier and multiplicity rule, or any statement about fine bins.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
from pathlib import Path

import numpy as np

import s5p_inference as si
import s5p_stage1_inspect as s1

NORM = 0.014


def sha256(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def j_matrix(stage1: dict, supported: list[int]) -> tuple[np.ndarray, list[str], np.ndarray]:
    cmap, n = s1.coarse_map(s1.J_EDGES, supported)
    vol = s1.fine_volume()
    rows = np.vstack([np.where(cmap == c, vol, 0.0) for c in range(n)])
    names = [f"J{c}" for c in supported]
    pz_index = np.array([np.unravel_index(c, (3, 3, 3, 3, 3))[1] for c in supported])
    return rows, names, pz_index


def xs(path) -> np.ndarray:
    return np.asarray(np.load(path, allow_pickle=False)["xsec_flat"], float)


def meta(path) -> dict:
    return json.loads(str(np.load(path, allow_pickle=False)["meta"]))


def prediction(path, U) -> tuple[np.ndarray, np.ndarray]:
    z = np.load(path, allow_pickle=True)
    return U @ np.asarray(z["xsec_flat"], float), (U ** 2) @ np.asarray(z["sumw2_flat"], float)


def ledoit_wolf(X: np.ndarray) -> tuple[np.ndarray, float]:
    """Ledoit-Wolf shrinkage towards a scaled identity (Ledoit and Wolf 2004), on standardized data."""
    X = np.asarray(X, float)
    n, p = X.shape
    Xc = X - X.mean(0)
    S = Xc.T @ Xc / n
    mu = np.trace(S) / p
    d2 = np.sum((S - mu * np.eye(p)) ** 2)
    b2 = sum(np.sum((np.outer(x, x) - S) ** 2) for x in Xc) / n ** 2
    shrink = min(1.0, b2 / d2) if d2 > 0 else 1.0
    return shrink * mu * np.eye(p) + (1 - shrink) * S * n / (n - 1), float(shrink)


class Model:
    """The declared additive terms and the metric; one instance per frozen design."""

    def __init__(self, design: dict, U: np.ndarray):
        self.U = U
        lat = design["lateral_endpoints"]
        self.Delta = np.array([(U @ xs(lat[b][1]) - U @ xs(lat[b][0])) / 2.0 for b in sorted(lat)])
        self.lat_bands = sorted(lat)
        J = np.array([U @ xs(p) for p in design["data_jitters"]])
        self.s_num = J.std(0, ddof=1)
        self.f_data = U @ xs(design["data_central"])

    def apply(self, f: np.ndarray, m: dict, seed: int) -> np.ndarray:
        d = m.get("nuisance_draw") or {}
        z = d.get("lateral_z", {})
        out = f + sum(z.get(b, 0.0) * self.Delta[i] for i, b in enumerate(self.lat_bands))
        out = out * (1.0 + NORM * d.get("normalization_z", 0.0))
        rng = np.random.default_rng([seed, 0x4A01])
        return out + rng.normal(size=f.size) * self.s_num

    def symmetry(self, design: dict) -> dict:
        """(f(+1) - f_cv) against -(f(-1) - f_cv) for each lateral band (the surrogate's linearity check)."""
        out = {}
        for b in self.lat_bands:
            e0, e1 = (self.U @ xs(p) for p in design["lateral_endpoints"][b])
            up, dn = e1 - self.f_data, e0 - self.f_data
            ok = np.abs(up) > 0
            out[b] = {"corr_up_vs_minus_down": float(np.corrcoef(up[ok], -dn[ok])[0, 1]),
                      "median_abs_delta_rel": float(np.median(np.abs((e1 - e0) / 2 / self.f_data)))}
        return out


def ensemble(model: Model, files: list[str]) -> np.ndarray:
    return np.array([model.apply(model.U @ xs(p), meta(p), int(meta(p)["pseudo_seed"])) for p in files])


def statistics(F: np.ndarray, mu: np.ndarray, var_mu: np.ndarray, V: np.ndarray, dom: np.ndarray, seed0: int,
               draw: bool = True) -> tuple[np.ndarray, np.ndarray]:
    """The metric is always W = V + diag Var(mu); ``draw`` adds the prediction's MC error to simulated residuals
    (the observed residual carries it already)."""
    W = V[np.ix_(dom, dom)] + np.diag(var_mu[dom])
    Winv = np.linalg.inv(W)
    tt, ts = [], []
    for i, f in enumerate(F):
        eps = np.random.default_rng([seed0 + i, 0x4A02]).normal(size=mu.size) * np.sqrt(var_mu) if draw else 0.0
        r_mu = mu + eps
        tt.append(si.stat_total(f[dom], r_mu[dom], Winv))
        ts.append(si.stat_shape(f[dom], r_mu[dom], W))
    return np.array(tt), np.array(ts)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build-v")
    b.add_argument("--design", type=Path, required=True)
    b.add_argument("--out", type=Path, required=True)
    e = sub.add_parser("evaluate")
    e.add_argument("--design", type=Path, required=True)
    e.add_argument("--v", type=Path, required=True)
    e.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        raise SystemExit(f"refusing to overwrite {a.out}")
    design = json.loads(a.design.read_text())
    stage1 = json.loads(Path(design["stage1"]).read_text())
    supported = json.loads(Path(design["s5c_contract"]).read_text())["measurement"]["partition_J"]["supported_cells"]
    U, names, pz_index = j_matrix(stage1, supported)
    model = Model(design, U)
    if a.cmd == "build-v":
        files = sorted(glob.glob(design["v_ensemble_glob"]))
        if len(files) != design["v_ensemble_n"]:
            raise SystemExit(f"{len(files)} V-ensemble products, {design['v_ensemble_n']} declared")
        F = ensemble(model, files)
        V, shrink = ledoit_wolf(F)
        np.savez(a.out, V=V, names=np.array(names), shrinkage=shrink, n=len(files),
                 meta=json.dumps({"files_first_last": [files[0], files[-1]], "shrinkage": shrink,
                                  "lateral_symmetry": model.symmetry(design), "design_sha256": sha256(a.design)}))
        print(json.dumps({"n": len(files), "shrinkage": shrink, "median_rel_sd": float(np.median(np.sqrt(np.diag(V)) / np.abs(F.mean(0))))}))
        return 0
    V = np.asarray(np.load(a.v, allow_pickle=False)["V"], float)
    res = {"schema": "s5p-joint/1", "design_sha256": sha256(a.design), "v_sha256": sha256(a.v), "names": names, "tests": {}}
    pvals = {}
    mu0, var0 = prediction(design["nulls"]["MnvTune_v1"]["prediction"], U)
    for key, spec in design["nulls"].items():
        mu, var = prediction(spec["prediction"], U)
        dom = np.ones(len(names), bool) if spec.get("domain") != "pz_lt_6" else (pz_index <= 1)
        files = sorted(glob.glob(spec["calibration_glob"]))
        if len(files) != spec["calibration_n"]:
            raise SystemExit(f"{key}: {len(files)} calibration products, {spec['calibration_n']} declared")
        tt_n, ts_n = statistics(ensemble(model, files), mu, var, V, dom, spec["surrogate_seed0"])
        f_obs = model.f_data
        tt_o, ts_o = statistics(f_obs[None, :], mu, var, V, dom, 0, draw=False)
        entry = {"domain_cells": int(dom.sum()), "T_total_obs": float(tt_o[0]), "T_shape_obs": float(ts_o[0]),
                 "total": si.mc_pvalue(tt_o[0], tt_n), "shape": si.mc_pvalue(ts_o[0], ts_n),
                 "null_T_total_median": float(np.median(tt_n)), "null_T_shape_median": float(np.median(ts_n))}
        res["tests"][key] = entry
        pvals[f"{key}:total"], pvals[f"{key}:shape"] = entry["total"]["p"], entry["shape"]["p"]
    res["holm"] = si.holm(pvals, design["alpha_family"])
    base = design["nulls"]["MnvTune_v1"]
    tt_base, ts_base = statistics(ensemble(model, sorted(glob.glob(base["calibration_glob"]))), mu0, var0, V,
                                  np.ones(len(names), bool), base["surrogate_seed0"])
    res["power"] = {}
    for key, spec in design.get("power", {}).items():
        files = sorted(glob.glob(spec["glob"]))
        tt_a, ts_a = statistics(ensemble(model, files), mu0, var0, V, np.ones(len(names), bool), spec["surrogate_seed0"])
        res["power"][key] = {"n": len(files), "total": si.power(tt_a, tt_base, 0.05), "shape": si.power(ts_a, ts_base, 0.05)}
    res["size"] = {}
    for key, spec in design.get("size", {}).items():
        null = design["nulls"][spec["null"]]
        mu, var = prediction(null["prediction"], U)
        dom = np.ones(len(names), bool) if null.get("domain") != "pz_lt_6" else (pz_index <= 1)
        tt_c, ts_c = statistics(ensemble(model, sorted(glob.glob(null["calibration_glob"]))), mu, var, V, dom, null["surrogate_seed0"])
        tt_v, ts_v = statistics(ensemble(model, sorted(glob.glob(spec["glob"]))), mu, var, V, dom, spec["surrogate_seed0"])
        res["size"][key] = {"total": si.size(tt_v, tt_c, 0.05), "shape": si.size(ts_v, ts_c, 0.05)}
    res["lateral_symmetry"] = model.symmetry(design)
    a.out.write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({k: {kk: (vv if not isinstance(vv, dict) else vv.get("p")) for kk, vv in v.items() if kk in ("total", "shape")}
                      for k, v in res["tests"].items()}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
