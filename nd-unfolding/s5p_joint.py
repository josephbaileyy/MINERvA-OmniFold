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
FIXED metric W = V + diag Var(mu_G), V the standardized Ledoit-Wolf-shrunk covariance of the frozen development
null ensemble (built by ``build-v`` and committed before any calibration ensemble). p-values (k+1)/(B+1) against
the null's calibration ensemble.

Process sensitivity (review round 1 F3/F4): the pseudo experiments unfold with half the MC, the data with all of
it. A declared per-null shift D (J cells; the measured change of the pseudo-process mean from a quarter to a half
of the MC) enters as VARIANTS of the calibration ensemble, f -> f + c D for the declared coefficients c (0, 1/2,
1: no shift, the 1/n extrapolation to the full MC, a slower decay). Each test's CLAIM p-value is the largest over
the variants (a rejection must hold under every variant); Holm over the family uses the claim p-values. Per
variant c > 0 the implied size of the unshifted test (the null draws shifted by c D against the unshifted
ensemble) is reported. The iid size-validation ensembles of amendment 5 are withdrawn: against an exchangeable
calibration ensemble their rejection rate is alpha by construction and cannot see the data-versus-pseudo
difference.

Power against the MnvTune null's ensemble at the declared levels (0.05 and the Holm first-step level
alpha_family / m), both for the unshifted test and under the claim rule.

MEASURES: the frozen joint statistics, p-values, their process-shift variants and power. CANNOT AUTHORIZE: a rejection outside the frozen
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
    """Ledoit-Wolf shrinkage on STANDARDIZED data (the correlation shrunk toward its diagonal, Schaefer and
    Strimmer 2005 target D, with the Ledoit-Wolf 2004 intensity), rescaled by the sample SDs: every diagonal is
    the sample variance (ddof 1) and V(X S) = S V(X) S for a cell rescaling S. A constant cell keeps variance 0.
    (Until review round 1 F5 the raw cells, whose variances span ~1e5, were shrunk toward (mean variance) x I.)"""
    X = np.asarray(X, float)
    n, p = X.shape
    Xc = X - X.mean(0)
    sd = np.sqrt((Xc ** 2).mean(0))
    Z = Xc / np.where(sd > 0, sd, 1.0)
    S = Z.T @ Z / n
    off = ~np.eye(p, dtype=bool)
    d2 = np.sum(S[off] ** 2)
    b2 = sum(np.sum((np.outer(z, z) - S)[off] ** 2) for z in Z) / n ** 2
    shrink = min(1.0, b2 / d2) if d2 > 0 else 1.0
    R = np.where(off, (1 - shrink) * S, S)
    return R * np.outer(sd, sd) * n / (n - 1), float(shrink)


class Model:
    """The declared additive terms and the metric; one instance per frozen design."""

    def __init__(self, design: dict, U: np.ndarray):
        self.U = U
        lat = design["lateral_endpoints"]
        self.Delta = np.array([(U @ xs(lat[b][1]) - U @ xs(lat[b][0])) / 2.0 for b in sorted(lat)])
        self.lat_bands = sorted(lat)
        J = np.array([U @ xs(p) for p in design["data_jitters"]])
        self.jitters = J
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


def product_files(pattern: str) -> list[str]:
    """The finished products a glob names: a task killed mid-write leaves ``*.partial-<pid>.npz``, never counted
    (review round 2 M6)."""
    return sorted(p for p in glob.glob(pattern) if ".partial" not in Path(p).name)


def ensemble(model: Model, files: list[str]) -> tuple[np.ndarray, np.ndarray]:
    ms = [meta(p) for p in files]
    F = np.array([model.apply(model.U @ xs(p), m, int(m["pseudo_seed"])) for p, m in zip(files, ms)])
    return F, np.array([int(m["pseudo_seed"]) for m in ms], dtype=np.int64)


def statistics(F: np.ndarray, mu: np.ndarray, var_mu: np.ndarray, V: np.ndarray, dom: np.ndarray, seed0: int,
               draw: bool = True, seeds: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray]:
    """The metric is always W = V + diag Var(mu); ``draw`` adds the prediction's MC error to simulated residuals
    (the observed residual carries it already). The draw of experiment i is keyed by (seed0, its pseudo seed),
    so adding or retrying a product never re-assigns another product's draw (review round 2 M6); without
    ``seeds`` the position i stands in (tests)."""
    W = V[np.ix_(dom, dom)] + np.diag(var_mu[dom])
    Winv = np.linalg.inv(W)
    tt, ts = [], []
    keys = seeds if seeds is not None else np.arange(len(F))
    for i, f in enumerate(F):
        eps = np.random.default_rng([int(seed0), int(keys[i]), 0x4A02]).normal(size=mu.size) * np.sqrt(var_mu) if draw else 0.0
        r_mu = mu + eps
        tt.append(si.stat_total(f[dom], r_mu[dom], Winv))
        ts.append(si.stat_shape(f[dom], r_mu[dom], W))
    return np.array(tt), np.array(ts)


def pvals_against(t: np.ndarray, t_null: np.ndarray) -> np.ndarray:
    """(#{null >= t} + 1) / (B + 1) for every t (the rank rule of s5p_inference.mc_pvalue)."""
    s = np.sort(np.asarray(t_null, float))
    return (s.size - np.searchsorted(s, np.asarray(t, float), side="left") + 1) / (s.size + 1)


def load_shift(spec: dict | None, n: int) -> tuple[np.ndarray | None, np.ndarray | None]:
    """The declared process shift of a null: {"none": reason} (explicit), or {"path", "sha256", "mode"} with the
    s5p_pairdiff npz (D_J and its per-pair d_pairs). A null without a declaration is refused (review round 2 M6)."""
    if spec is None:
        raise SystemExit("a null without a process_shift declaration (give {'none': reason} explicitly)")
    if "none" in spec:
        return None, None
    if sha256(spec["path"]) != spec["sha256"]:
        raise SystemExit(f"{spec['path']}: digest differs from the design's")
    z = np.load(spec["path"], allow_pickle=False)
    D = np.asarray(z["D_J"], float)
    if D.size != n:
        raise SystemExit(f"{spec['path']}: {D.size} cells, {n} expected")
    return D, (np.asarray(z["d_pairs"], float) if "d_pairs" in z.files else None)


def shift_vector(spec: dict, D: np.ndarray, d_pairs: np.ndarray | None, F: np.ndarray, mu: np.ndarray,
                 var: np.ndarray, V: np.ndarray, dom: np.ndarray) -> tuple[np.ndarray, dict]:
    """The variant shift S of a null. ``raw``: S = D. ``bias_aligned_upper`` (review round 2 M2): only the component
    of the process difference along the null's own bias direction moves T to first order, so S = m u with
    u = b / |b|_W (b = the calibration ensemble's mean minus mu on the test domain), m = max(a + 2 se, 0), a the
    mean over the F4 pairs of d_j' W^-1 u and se its standard error: the protective (T-increasing) upper bound."""
    mode = spec.get("mode", "raw")
    if mode == "raw":
        return D, {"mode": "raw"}
    if mode != "bias_aligned_upper" or d_pairs is None or len(d_pairs) < 2:
        raise SystemExit(f"shift mode {mode} needs >= 2 F4 pairs")
    W = V[np.ix_(dom, dom)] + np.diag(var[dom])
    Winv = np.linalg.inv(W)
    b = F.mean(0)[dom] - mu[dom]
    nb = float(np.sqrt(b @ Winv @ b))
    u = b / nb if nb > 0 else np.zeros_like(b)
    a_j = np.array([dj[dom] @ Winv @ u for dj in d_pairs])
    a, se = float(a_j.mean()), float(a_j.std(ddof=1) / np.sqrt(len(a_j)))
    m = max(a + 2.0 * se, 0.0)
    S = np.zeros(D.size)
    S[dom] = m * u
    return S, {"mode": mode, "bias_norm_W": nb, "a": a, "se": se, "n_pairs": int(len(a_j)), "magnitude": m}


def test_null(model: Model, design: dict, key: str, V: np.ndarray, names: list, pz_index: np.ndarray, files: list,
              coefs: list) -> dict:
    """One null's observed statistics against its calibration ensemble ``files``, per shift variant, and the
    claim p-values (the largest over the variants)."""
    spec = design["nulls"][key]
    mu, var = prediction(spec["prediction"], model.U)
    dom = np.ones(len(names), bool) if spec.get("domain") != "pz_lt_6" else (pz_index <= 1)
    F, seeds = ensemble(model, files)
    pspec = design.get("process_shift", {}).get(key)
    D, d_pairs = load_shift(pspec, len(names))
    S, sinfo = shift_vector(pspec, D, d_pairs, F, mu, var, V, dom) if D is not None else (None, {"mode": "none", "reason": pspec["none"]})
    tt_o, ts_o = statistics(model.f_data[None, :], mu, var, V, dom, 0, draw=False)
    entry = {"domain_cells": int(dom.sum()), "T_total_obs": float(tt_o[0]), "T_shape_obs": float(ts_o[0]),
             "process_shift": pspec, "shift": sinfo, "variants": {}}
    # the sub-fine-grid residual (confirmation review F5): declared variants F +- kappa delta_M1 (delta_M1 = the
    # fine-minus-merged-x2 asimov difference) enter the CLAIM rule at kappa; kappa_robust is reported only
    m1 = design.get("m1_shift", {}).get(key)
    variant_shifts = [(str(c), (c * S if S is not None else None)) for c in (coefs if S is not None else [0.0])]
    robust_shifts = []
    if m1 is not None and "none" not in m1:
        d1, _ = load_shift({k: v for k, v in m1.items() if k in ("path", "sha256")}, len(names))
        variant_shifts += [(f"m1+{m1['kappa']}", m1["kappa"] * d1), (f"m1-{m1['kappa']}", -m1["kappa"] * d1)]
        robust_shifts = [(f"m1+{m1['kappa_robust']}", m1["kappa_robust"] * d1), (f"m1-{m1['kappa_robust']}", -m1["kappa_robust"] * d1)]
        entry["m1_shift"] = {"kappa": m1["kappa"], "kappa_robust": m1["kappa_robust"], "path": m1["path"]}
    elif m1 is None:
        raise SystemExit(f"{key}: no m1_shift declaration (give {{'none': reason}} explicitly)")
    base = None
    nulls = []
    for name, sv in variant_shifts:
        tt_n, ts_n = statistics(F + (sv if sv is not None else 0.0), mu, var, V, dom, spec["surrogate_seed0"], seeds=seeds)
        nulls.append((tt_n, ts_n))
        if base is None:
            base = (tt_n, ts_n)
        v = {"total": si.mc_pvalue(tt_o[0], tt_n), "shape": si.mc_pvalue(ts_o[0], ts_n),
             "null_T_total_median": float(np.median(tt_n)), "null_T_shape_median": float(np.median(ts_n)),
             "null_T_total_sd": float(np.std(tt_n)), "null_T_shape_sd": float(np.std(ts_n))}
        if name != "0.0":
            v["implied_size_of_unshifted_test"] = {"total": si.power(tt_n, base[0], 0.05), "shape": si.power(ts_n, base[1], 0.05)}
            v["median_shift_in_null_sd"] = {s: float((np.median(x) - np.median(b)) / max(np.std(b), 1e-300))
                                            for s, x, b in (("total", tt_n, base[0]), ("shape", ts_n, base[1]))}
        entry["variants"][name] = v
    entry["robustness_variants"] = {}
    for name, sv in robust_shifts:
        tt_n, ts_n = statistics(F + sv, mu, var, V, dom, spec["surrogate_seed0"], seeds=seeds)
        entry["robustness_variants"][name] = {"total": si.mc_pvalue(tt_o[0], tt_n), "shape": si.mc_pvalue(ts_o[0], ts_n)}
    for s in ("total", "shape"):
        claim = max(entry["variants"].values(), key=lambda v: v[s]["p"])[s]
        entry[s] = dict(claim, rule="the largest p over the declared shift variants")
        robust = max([claim] + [r[s] for r in entry["robustness_variants"].values()], key=lambda v: v["p"])
        entry[s + "_robust"] = dict(robust, rule="the claim p with the kappa_robust M1 variants added (report only)")
    # numerical stability of the observed p (review round 2 L2): the 20 real-data rounding jitters as observations
    k = {"total": 0, "shape": 1}
    tj, sj_ = statistics(model.jitters, mu, var, V, dom, 0, draw=False)
    stab = {}
    for s, tobs in (("total", tj), ("shape", sj_)):
        pj = np.max([pvals_against(tobs, nn[k[s]]) for nn in nulls], axis=0)
        stab[s] = {"min": float(pj.min()), "median": float(np.median(pj)), "max": float(pj.max()), "n": int(pj.size)}
    entry["observed_jitter_p"] = stab
    entry["_nulls"] = nulls  # kept in memory for the power step, removed before writing
    return entry


def calibration_count(spec: dict) -> int:
    """A fixed count, or the final B of a sequential calibration (the controller's last status file)."""
    n = spec["calibration_n"]
    if isinstance(n, int):
        return n
    if not Path(n["sequential_status"]).exists():
        raise SystemExit(f"{n['sequential_status']}: no final status (the sequential calibration has not stopped)")
    st = json.loads(Path(n["sequential_status"]).read_text())
    if not st.get("stop"):
        raise SystemExit(f"{n['sequential_status']}: the sequential calibration has not stopped")
    return int(st["B"])


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
        files = product_files(design["v_ensemble_glob"])
        if len(files) != design["v_ensemble_n"]:
            raise SystemExit(f"{len(files)} V-ensemble products, {design['v_ensemble_n']} declared")
        F, _ = ensemble(model, files)
        V, shrink = ledoit_wolf(F)
        np.savez(a.out, V=V, names=np.array(names), shrinkage=shrink, n=len(files),
                 meta=json.dumps({"files_first_last": [files[0], files[-1]], "shrinkage": shrink,
                                  "lateral_symmetry": model.symmetry(design), "design_sha256": sha256(a.design)}))
        print(json.dumps({"n": len(files), "shrinkage": shrink, "median_rel_sd": float(np.median(np.sqrt(np.diag(V)) / np.abs(F.mean(0))))}))
        return 0
    V = np.asarray(np.load(a.v, allow_pickle=False)["V"], float)
    res = {"schema": "s5p-joint/3", "design_sha256": sha256(a.design), "v_sha256": sha256(a.v), "names": names, "tests": {}}
    coefs = [float(c) for c in design.get("shift_coefficients", [0.0])]
    if coefs[0] != 0.0:
        raise SystemExit("the first shift coefficient must be 0 (the unshifted test)")
    pvals, claims, robust, null_sets = {}, {}, {}, {}
    for key, spec in design["nulls"].items():
        files = product_files(spec["calibration_glob"])
        want = calibration_count(spec)
        if len(files) != want:
            raise SystemExit(f"{key}: {len(files)} calibration products, {want} declared")
        if want == 0:  # a null stopped by the budget before its first batch: no test, no claim (it stays in the family)
            res["tests"][key] = {"not_calibrated": "B = 0 at the stop"}
            for s in ("total", "shape"):
                pvals[f"{key}:{s}"] = 1.0
                claims[f"{key}:{s}"] = robust[f"{key}:{s}"] = {"p": 1.0, "k": 0, "B": 0}
            continue
        entry = test_null(model, design, key, V, names, pz_index, files, coefs)
        null_sets[key] = entry.pop("_nulls")
        res["tests"][key] = entry
        for s in ("total", "shape"):
            pvals[f"{key}:{s}"] = entry[s]["p"]
            claims[f"{key}:{s}"] = {"p": entry[s]["p"], "k": entry[s]["k"], "B": entry[s]["B"]}
            robust[f"{key}:{s}"] = {"p": entry[s + "_robust"]["p"], "k": entry[s + "_robust"]["k"], "B": entry[s + "_robust"]["B"]}
    res["holm_point"] = si.holm(pvals, design["alpha_family"])
    res["decisions"] = si.holm_determined(claims, design["alpha_family"])
    res["decisions_robust_kappa"] = si.holm_determined(robust, design["alpha_family"])
    res["robust_to_the_sub_fine_residual"] = {k: res["decisions"][k]["decision"] == res["decisions_robust_kappa"][k]["decision"]
                                              for k in res["decisions"]}
    levels = [0.05, design["alpha_family"] / len(pvals)]
    res["power"] = {"levels": levels}
    for key, spec in design.get("power", {}).items():
        nk = spec.get("null", "MnvTune_v1")
        nspec = design["nulls"][nk]
        mu0, var0 = prediction(nspec["prediction"], U)
        dom = np.ones(len(names), bool) if nspec.get("domain") != "pz_lt_6" else (pz_index <= 1)
        files = product_files(spec["glob"])
        if nk not in null_sets:
            res["power"][key] = {"n": len(files), "null": nk, "not_evaluated": "its null was not calibrated"}
            continue
        incomplete = "n" in spec and len(files) != int(spec["n"])
        if incomplete and len(files) < 20:  # recorded, never aborting the joint result (confirmation review F3)
            res["power"][key] = {"n": len(files), "declared": int(spec["n"]), "null": nk, "not_evaluated": "fewer than 20 products"}
            continue
        Fa, sa = ensemble(model, files)
        tt_a, ts_a = statistics(Fa, mu0, var0, V, dom, spec["surrogate_seed0"], seeds=sa)
        out = {"n": len(files), "null": nk, "declared": int(spec["n"]) if "n" in spec else None, "incomplete": bool(incomplete)}
        for s, t_alt in (("total", tt_a), ("shape", ts_a)):
            k = 0 if s == "total" else 1
            nn = [x[k] for x in null_sets[nk]]
            p_claim = np.max([pvals_against(t_alt, x) for x in nn], axis=0)
            out[s] = {str(al): {"unshifted": si.power(t_alt, nn[0], al),
                                "claim_rule": {"power": float(np.mean(p_claim <= al)), "n": int(p_claim.size)},
                                "claim_rule_determined": si.power_determined(t_alt, nn, al)} for al in levels}
        res["power"][key] = out
    res["lateral_symmetry"] = model.symmetry(design)
    a.out.write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({k: {kk: (vv if not isinstance(vv, dict) else vv.get("p")) for kk, vv in v.items() if kk in ("total", "shape")}
                      for k, v in res["tests"].items()}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
