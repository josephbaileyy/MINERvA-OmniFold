#!/usr/bin/env python3
"""s5p Stage 2: the frozen analysis of studies K, N and C (contract amendment 2).

Reads the Stage-2 products under ``--runs`` (``s2/conv``, ``s2/num``) and the committed s5e development
products under ``--s5e-runs``; applies exactly the metrics and decision rules of amendment 2 and writes one
receipt. Reporting cells and their support flags come from the Stage-1 receipt (amendment 1): EW (42 cells,
39 reported), J (109) and H2 (32, 27 reported).

* study K (noise-free convergence): per iteration and reporting definition, residual quantiles over reported
  cells, the T2 proxy (median over cells with a departure > 1% of |bias| / |departure|; the departure is the
  alternative's truth over the nominal run's truth), M_P(k) = the maximum over the four alternatives, and the
  detector-level fold agreement (EW every iteration, 5D at the snapshots) with the analysis-exposure Poisson
  variance of the folded truth, the explained fraction and S_dep;
* study N (numerical/bootstrap overlap): sigma_num_base, sigma_boot, sigma_num_rep, the covariance
  decomposition, absorption and consistency ratios per functional, and the amendment's absorption rule;
* study C (the six calibration failures): pull SDs with the single-experiment sigma and with the mean of the
  per-experiment sigmas, the sigma CV over experiments, the fixed- versus varying-split spread, departure
  sigmas and mean pulls, and the ADDRESSED / UNRESOLVED rule;
* R verification from product metadata and measured unfold costs.

MEASURES: the amendment-2 quantities. CANNOT AUTHORIZE: an interval, a component definition, a configuration
choice by itself (applied by the next amendment) or any coverage, stability or adoption verdict.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

import s5p_stage1_inspect as s1

SIX = ("EW41", "J85", "J162", "J206", "J215", "J232")
ALTS = ("gibuu", "q3", "w1", "w3")
KGRID = (1, 5, 10, 15, 20, 30, 40, 50, 75, 100, 125, 150, 175, 200)
T5_BAND = (0.80, 1.25)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def load(path: Path) -> dict:
    z = np.load(path, allow_pickle=False)
    out = {k: np.asarray(z[k]) for k in z.files if k != "meta"}
    out["meta"] = json.loads(str(z["meta"]))
    return out


class Cells:
    """Fine-grid cross sections -> reporting-cell integrals, the Stage-1 maps and support flags."""

    def __init__(self, stage1: dict, s5c_contract: dict):
        supported = s5c_contract["measurement"]["partition_J"]["supported_cells"]
        self.maps = {"EW": s1.ew_map(), "J": s1.coarse_map(s1.J_EDGES, supported), "H2": s1.coarse_map(s1.H2_EDGES)}
        self.vol = s1.fine_volume()
        self.reported = {P: np.asarray(stage1["mc"][P]["reported"], bool) for P in self.maps}
        self.names = {"EW": [f"EW{i}" for i in range(42)], "J": [f"J{c}" for c in supported],
                      "H2": [f"H2_{c}" for c in range(32)]}

    def of(self, flat: np.ndarray) -> dict:
        return {P: s1.cell_xsec(np.asarray(flat, float), cm, n, self.vol) for P, (cm, n) in self.maps.items()}

    def stack(self, flats: list) -> dict:
        per = [self.of(f) for f in flats]
        return {P: np.array([p[P] for p in per]) for P in self.maps}


def med_rep(values: np.ndarray, mask: np.ndarray) -> float:
    return float(np.median(np.asarray(values)[mask]))


# ------------------------------------------------------------------------------------------ study K


def trace_functionals(p: dict) -> dict:
    names = p["meta"]["functional_names"]
    rows = {"EW": [names.index(f"EW{i}") for i in range(42)],
            "J": [i for i, n in enumerate(names) if n.startswith("J")],
            "H2": [names.index(f"H2_{c}") for c in range(32)]}
    return rows


def study_k(conv: Path, cells: Cells) -> dict:
    out = {}
    for family, kmax in (("b0", 200), ("cap", 100)):
        runs = {}
        for f in sorted(conv.glob(f"k_{family}_*.npz")):
            runs[f.stem.split("_", 2)[2]] = load(f)
        if not runs:
            out[family] = {"missing": True}
            continue
        nominal = runs.get("nominal")
        ref = nominal if nominal is not None else load(conv / "k_b0_nominal.npz") if (conv / "k_b0_nominal.npz").exists() else None
        fam = {"runs": {}, "M": {}}
        for truth, p in runs.items():
            rows = trace_functionals(p)
            K = p["fn_push"].shape[0]
            ft = p["fn_true"]
            shape = tuple(len(e) - 1 for e in s1.FINE.values())
            var5 = p["reco5d_true"]
            varew = var5.reshape(shape).sum(axis=(0, 1, 3)).ravel()
            s_dep_ew = chi2(p["reco_ew_prior"], p["reco_ew_true"], varew)
            s_dep_5d = chi2(p["reco5d_prior"], p["reco5d_true"], var5)
            series = {}
            for k in [k for k in KGRID if k <= K]:
                row = {}
                for P, idx in rows.items():
                    rel = p["fn_push"][k - 1][idx] / ft[idx] - 1.0
                    m = cells.reported[P]
                    a = np.abs(rel[m])
                    row[P] = {"median_abs_pct": 100 * float(np.median(a)), "p90_abs_pct": 100 * float(np.percentile(a, 90)),
                              "max_abs_pct": 100 * float(a.max())}
                    if ref is not None and truth != "nominal":
                        dep = ft[idx] / ref["fn_true"][idx] - 1.0
                        ok = m & (np.abs(dep) > 0.01)
                        ratio = np.abs(rel[ok]) / np.abs(dep[ok])
                        row[P]["T2_proxy"] = float(np.median(ratio)) if ratio.size else None
                        row[P]["recovered_median"] = float(np.median(1 - ratio)) if ratio.size else None
                        row[P]["n_departure_cells"] = int(ok.sum())
                c_ew = chi2(p["reco_ew_push"][k - 1], p["reco_ew_true"], varew)
                row["ew_chi2_push_vs_true"] = c_ew
                row["ew_explained_fraction"] = 1 - c_ew / s_dep_ew if s_dep_ew > 0 else None
                key = f"reco5d_push_it{k}"
                if key in p:
                    c5 = chi2(p[key], p["reco5d_true"], var5)
                    row["reco5d_chi2_push_vs_true"] = c5
                    row["reco5d_explained_fraction"] = 1 - c5 / s_dep_5d if s_dep_5d > 0 else None
                series[k] = row
            best = {}
            for P, idx in rows.items():
                med = [float(np.median(np.abs(p["fn_push"][k][idx] / ft[idx] - 1.0)[cells.reported[P]])) for k in range(K)]
                best[P] = {"k_min_median": int(np.argmin(med)) + 1, "median_at_min_pct": 100 * min(med),
                           "median_k5_pct": 100 * med[4] if K >= 5 else None, "median_kmax_pct": 100 * med[-1]}
            fam["runs"][truth] = {"K": K, "S_dep_ew": s_dep_ew, "S_dep_reco5d": s_dep_5d, "series": series, "best": best,
                                  "seconds_unfold": p["meta"].get("seconds_unfold"), "capacity": p["meta"].get("capacity"),
                                  "trace_checks": p["meta"].get("trace_checks")}
        for P in ("J", "H2"):
            fam["M"][P] = {}
            for k in KGRID:
                vals = [fam["runs"][t]["series"].get(k, {}).get(P, {}).get("T2_proxy") for t in ALTS if t in fam["runs"]]
                if vals and all(v is not None for v in vals) and len(vals) == len([t for t in ALTS if t in fam["runs"]]):
                    fam["M"][P][k] = {"M": max(vals), "alternatives": [t for t in ALTS if t in fam["runs"]]}
        out[family] = fam
    return out


def chi2(a, b, var) -> float:
    a, b, var = (np.asarray(x, float) for x in (a, b, var))
    ok = var > 0
    return float(np.sum((a[ok] - b[ok]) ** 2 / var[ok]))


# ------------------------------------------------------------------------------------------ study N


def num_products(d: Path, tag: str) -> dict:
    return {f.name: f for f in d.glob(f"{tag}_b*_j*.npz")}


def overlap(base_flats: dict, jit: list, rep0: list, repj: list, cells: Cells) -> dict:
    """Per functional sigma_num_base, sigma_boot, sigma_num_rep, the covariance decomposition."""
    B = cells.of(base_flats)
    J = cells.stack(jit)
    R0, RJ = cells.stack(rep0), cells.stack(repj)
    out = {"n_jitters": len(jit), "n_replicas": len(rep0)}
    for P in cells.maps:
        m = cells.reported[P]
        mean = np.where(B[P] > 0, B[P], 1.0)
        s_num = J[P].std(0, ddof=1) / mean
        s_boot = R0[P].std(0, ddof=1) / mean
        d = (RJ[P] - R0[P]) / np.sqrt(2.0)
        s_num_rep = d.std(0, ddof=1) / mean
        cov = np.array([np.cov(R0[P][:, i], RJ[P][:, i])[0, 1] for i in range(R0[P].shape[1])]) / mean ** 2
        absorption = np.where(s_boot > 0, s_num_rep ** 2 / np.where(s_boot > 0, s_boot ** 2, 1), 0.0)
        consistency = np.where(s_num > 0, s_num_rep / np.where(s_num > 0, s_num, 1), 0.0)
        out[P] = {"sigma_num_base_rel": s_num.tolist(), "sigma_boot_rel": s_boot.tolist(),
                  "sigma_num_rep_rel": s_num_rep.tolist(), "sigma_smooth_sq_rel": cov.tolist(),
                  "absorption_ratio": absorption.tolist(), "consistency_ratio": consistency.tolist(),
                  "median_sigma_num_base_pct": 100 * med_rep(s_num, m), "max_sigma_num_base_pct": 100 * float(s_num[m].max()),
                  "median_sigma_boot_pct": 100 * med_rep(s_boot, m),
                  "median_sigma_num_over_boot": med_rep(np.where(s_boot > 0, s_num / np.where(s_boot > 0, s_boot, 1), 0), m),
                  "median_absorption": med_rep(absorption, m), "median_consistency": med_rep(consistency, m),
                  "fraction_boot_var_ge_num_rep_var": float(np.mean((s_boot ** 2 >= s_num_rep ** 2)[m])),
                  "absorbed": bool(0.7 <= med_rep(consistency, m) <= 1.4 and np.mean((s_boot ** 2 >= s_num_rep ** 2)[m]) >= 0.95)}
    return out


def study_n(num: Path, s5e: Path, cells: Cells) -> dict:
    res = {}
    d = num / "data"
    ctrl = {}
    base = d / "data_b-_j-.npz"
    if base.exists():
        ref = s5e / "cand/assess/data/data_R.npz"
        ctrl["data_base_equals_s5e_data_R"] = bool(np.array_equal(load(base)["xsec_flat"], load(ref)["xsec_flat"]))
        for b in (1, 2):
            f = d / f"data_b{b}_j-.npz"
            if f.exists():
                ctrl[f"data_b{b}_equals_s5e_boot_b{b}"] = bool(np.array_equal(
                    load(f)["xsec_flat"], load(s5e / f"cand/assess/data/boot/boot_b{b}.npz")["xsec_flat"]))
        jit = [load(d / f"data_b-_j{j}.npz")["xsec_flat"] for j in range(1, 21) if (d / f"data_b-_j{j}.npz").exists()]
        pairs = [b for b in range(1, 51) if (d / f"data_b{b}_j{100 + b}.npz").exists()]
        rep0 = [load(s5e / f"cand/assess/data/boot/boot_b{b}.npz")["xsec_flat"] for b in pairs]
        repj = [load(d / f"data_b{b}_j{100 + b}.npz")["xsec_flat"] for b in pairs]
        if len(jit) >= 2 and len(pairs) >= 3:
            res["N1_data"] = overlap(load(base)["xsec_flat"], jit, rep0, repj, cells)
    res["controls"] = ctrl
    for tag, grp in (("nom", "N2_nominal_930000"), ("gibuu", "N3_gibuu_931000")):
        g = num / tag
        base = g / f"{tag}_b-_j-.npz"
        if not base.exists():
            continue
        jit = [load(g / f"{tag}_b-_j{j}.npz")["xsec_flat"] for j in range(1, 21) if (g / f"{tag}_b-_j{j}.npz").exists()]
        pairs = [b for b in range(5001, 5041) if (g / f"{tag}_b{b}_j-.npz").exists() and (g / f"{tag}_b{b}_j{100 + b - 5000}.npz").exists()]
        rep0 = [load(g / f"{tag}_b{b}_j-.npz")["xsec_flat"] for b in pairs]
        repj = [load(g / f"{tag}_b{b}_j{100 + b - 5000}.npz")["xsec_flat"] for b in pairs]
        if len(jit) >= 2 and len(pairs) >= 3:
            res[grp] = overlap(load(base)["xsec_flat"], jit, rep0, repj, cells)
    return res


# ------------------------------------------------------------------------------------------ study C


def rel_sigma(flats: list, cells: Cells) -> dict:
    S = cells.stack(flats)
    return {P: S[P].std(0, ddof=1) / np.where(S[P].mean(0) > 0, S[P].mean(0), 1.0) for P in S}


def ensemble(files: list[Path], cells: Cells) -> tuple[dict, dict, int]:
    """Relative residuals per experiment (f_hat / f_true - 1) and the mean truth, per definition."""
    xs, xt = [], []
    for f in files:
        z = np.load(f, allow_pickle=False)
        xs.append(z["xsec_flat"])
        xt.append(z["xtrue_flat"])
    A, T = cells.stack(xs), cells.stack(xt)
    rel = {P: np.where(T[P] > 0, A[P] / np.where(T[P] > 0, T[P], 1) - 1.0, 0.0) for P in A}
    return rel, {P: T[P].mean(0) for P in T}, len(files)


def study_c(num: Path, s5e: Path, cells: Cells) -> dict:
    nom_files = (sorted((s5e / "cand/dev/k1_R").glob("nominal_a0_s*.npz")) + sorted((s5e / "cand/assess/nominal").glob("nominal_a0_s*.npz"))
                 + sorted((num / "c2").glob("nominal_a0_s*.npz")))
    rel, _, n = ensemble(nom_files, cells)
    sigmas = {"700000": rel_sigma([load(f)["xsec_flat"] for f in sorted((s5e / "cand/dev/sigma").glob("boot_b*.npz"))], cells)}
    nomrep = sorted((num / "nom").glob("nom_b50[0-9][0-9]_j-.npz"))
    if nomrep:
        sigmas["930000"] = rel_sigma([load(f)["xsec_flat"] for f in nomrep], cells)
    for s in range(930001, 930005):
        fs = sorted((num / "c1").glob(f"c1_s{s}_b*_j-.npz"))
        if len(fs) >= 3:
            sigmas[str(s)] = rel_sigma([load(f)["xsec_flat"] for f in fs], cells)
    out = {"n_nominal_experiments": n, "nominal_files_first_last": [str(nom_files[0]), str(nom_files[-1])] if nom_files else [],
           "sigma_experiments": sorted(sigmas), "per_definition": {}}
    fixed = sorted((num / "c3").glob("c3_s*_b-_j-.npz"))
    rel_fixed = ensemble(fixed, cells)[0] if len(fixed) >= 3 else None
    dep = {}
    for tag, sub, pat in (("gibuu", "gibuu", "gibuu_b50[0-9][0-9]_j-.npz"), ("w3", "c4", "w3_b50[0-9][0-9]_j-.npz")):
        fs = sorted((num / sub).glob(pat))
        if len(fs) >= 3:
            dep[tag] = rel_sigma([load(f)["xsec_flat"] for f in fs], cells)
    dep_ens = {"gibuu": sorted((s5e / "cand/dev/k2").glob("*.npz")) + sorted((s5e / "cand/assess/eavail_gibuu").glob("*.npz")),
               "w3": sorted((s5e / "cand/assess/W3").glob("*.npz"))}
    for P in cells.maps:
        m = cells.reported[P]
        r = rel[P]
        ens_sd = r.std(0, ddof=1)
        s_single = sigmas["700000"][P]
        s_mean = np.mean([sigmas[k][P] for k in sigmas], axis=0)
        s_cv = np.std([sigmas[k][P] for k in sigmas], axis=0, ddof=1) / np.where(s_mean > 0, s_mean, 1) if len(sigmas) > 1 else None
        psd_single = ens_sd / np.where(s_single > 0, s_single, 1)
        psd_mean = ens_sd / np.where(s_mean > 0, s_mean, 1)
        mean_pull = r.mean(0) / np.where(s_mean > 0, s_mean, 1)
        se_mean_pull = psd_mean / np.sqrt(n)
        block = {"ensemble_rel_sd": ens_sd.tolist(), "sigma_single_700000": s_single.tolist(), "sigma_mean": s_mean.tolist(),
                 "sigma_cv_over_experiments": None if s_cv is None else s_cv.tolist(),
                 "pull_sd_single_sigma": psd_single.tolist(), "pull_sd_mean_sigma": psd_mean.tolist(),
                 "mean_pull_mean_sigma": mean_pull.tolist(), "se_mean_pull": se_mean_pull.tolist(),
                 "se_pull_sd": 1 / np.sqrt(2 * (n - 1)),
                 "fraction_pull_sd_mean_sigma_in_T5_band": float(np.mean(((psd_mean >= T5_BAND[0]) & (psd_mean <= T5_BAND[1]))[m])),
                 "median_pull_sd_mean_sigma": med_rep(psd_mean, m), "median_sigma_cv": None if s_cv is None else med_rep(s_cv, m)}
        if rel_fixed is not None:
            fsd = rel_fixed[P].std(0, ddof=1)
            block["fixed_over_varying_split_sd"] = (fsd / np.where(ens_sd > 0, ens_sd, 1)).tolist()
            block["median_fixed_over_varying_split_sd"] = med_rep(fsd / np.where(ens_sd > 0, ens_sd, 1), m)
        for tag, sg in dep.items():
            block[f"departure_{tag}_sigma_over_nominal_mean_sigma"] = med_rep(sg[P] / np.where(s_mean > 0, s_mean, 1), m)
            if dep_ens[tag]:
                rr = ensemble(dep_ens[tag], cells)[0][P]
                block[f"departure_{tag}_ensemble_sd_over_departure_sigma"] = med_rep(rr.std(0, ddof=1) / np.where(sg[P] > 0, sg[P], 1), m)
        out["per_definition"][P] = block
    six = {}
    for name in SIX:
        P = "EW" if name.startswith("EW") else "J"
        i = cells.names[P].index(name)
        b = out["per_definition"][P]
        entry = {"pull_sd_single_sigma": b["pull_sd_single_sigma"][i], "pull_sd_mean_sigma": b["pull_sd_mean_sigma"][i],
                 "se_pull_sd": b["se_pull_sd"], "mean_pull": b["mean_pull_mean_sigma"][i], "se_mean_pull": b["se_mean_pull"][i],
                 "sigma_cv": None if b["sigma_cv_over_experiments"] is None else b["sigma_cv_over_experiments"][i]}
        if "fixed_over_varying_split_sd" in b:
            entry["fixed_over_varying_split_sd"] = b["fixed_over_varying_split_sd"][i]
        entry["disposition"] = ("ADDRESSED (mean-sigma construction)" if T5_BAND[0] <= entry["pull_sd_mean_sigma"] <= T5_BAND[1]
                                else "UNRESOLVED")
        six[name] = entry
    out["six"] = six
    return out


# ------------------------------------------------------------------------------------------ study P


def study_p(runs: Path, s5e: Path, cells: Cells) -> dict:
    """Amendment 3: data shift under a prior change to vertex k against minus the estimator's bias there."""
    pdir = runs / "s2/prior"
    cv_path = pdir / "prior_R5_CV.npz"
    if not cv_path.exists():
        return {"missing": True}
    cv = load(cv_path)["xsec_flat"]
    out = {"controls": {}}
    base = runs / "s2/num/data/data_b-_j-.npz"
    d0 = pdir / "prior_R5_prior_d0.npz"
    if base.exists():
        out["controls"]["CV_path_equals_N1_base"] = bool(np.array_equal(cv, load(base)["xsec_flat"]))
    if d0.exists():
        out["controls"]["nominal_prior_equals_CV_path"] = bool(np.array_equal(load(d0)["xsec_flat"], cv))
    C0 = cells.of(cv)
    conv = runs / "s2/conv"
    bias_src = {"d1": ("asimov", conv / "k_b0_gibuu.npz"), "d2": ("asimov", conv / "k_b0_w1.npz"),
                "d4": ("asimov", conv / "k_b0_w3.npz"), "d3": ("pseudo", s5e / "cand/assess/W2")}
    out["vertices"] = {}
    for k in ("d1", "d2", "d3", "d4", "d5"):
        f = pdir / f"prior_R5_prior_{k}.npz"
        if not f.exists():
            continue
        Ck = cells.of(load(f)["xsec_flat"])
        entry = {}
        bias = None
        kind, src = bias_src.get(k, (None, None))
        if kind == "asimov" and src.exists():
            p = load(src)
            rows = trace_functionals(p)
            bias = {P: p["fn_push"][4][idx] / p["fn_true"][idx] - 1.0 for P, idx in rows.items()}
        elif kind == "pseudo" and src.exists():
            rel, _, _ = ensemble(sorted(src.glob("*.npz")), cells)
            bias = {P: rel[P].mean(0) for P in rel}
        for P in cells.maps:
            m = cells.reported[P]
            shift = np.where(C0[P] > 0, Ck[P] / np.where(C0[P] > 0, C0[P], 1) - 1.0, 0.0)
            e = {"median_abs_shift_pct": 100 * med_rep(np.abs(shift), m), "max_abs_shift_pct": 100 * float(np.abs(shift[m]).max())}
            if bias is not None:
                b = bias[P]
                x, y = -b[m], shift[m]
                e["corr_shift_vs_minus_bias"] = float(np.corrcoef(x, y)[0, 1])
                e["slope_shift_on_minus_bias"] = float(np.dot(x, y) / np.dot(x, x))
                big = np.abs(b[m]) > 0.01
                e["median_rel_mismatch"] = float(np.median(np.abs(y[big] - x[big]) / np.abs(x[big]))) if big.any() else None
                e["median_abs_bias_pct"] = 100 * float(np.median(np.abs(b[m])))
            entry[P] = e
        entry["bias_source"] = None if bias is None else kind
        out["vertices"][k] = entry
    return out


# ------------------------------------------------------------------------------------------ R metadata


R_REFINE = {"n_estimators": 400, "num_leaves": 31, "learning_rate": 0.1, "random_state": 45}
F2 = {"n_estimators": 100, "num_leaves": 8, "learning_rate": 0.1, "deterministic": True, "force_row_wise": True}


def verify_r(paths: list[Path]) -> dict:
    bad, n, refined = [], 0, 0
    for f in paths:
        m = json.loads(str(np.load(f, allow_pickle=False)["meta"]))
        n += 1
        ref = m.get("refinement", {})
        if ref.get("ran"):
            refined += 1
            cp = ref.get("classifier_params", {})
            if any(cp.get(k) != v for k, v in R_REFINE.items()):
                bad.append((f.name, "refinement", {k: cp.get(k) for k in R_REFINE}))
        for p in m.get("estimator_params", []):
            cap = m.get("capacity")
            want = dict(F2, **({"n_estimators": cap[0], "num_leaves": cap[1]} if cap else {}))
            if any(p.get(k) != v for k, v in want.items()):
                bad.append((f.name, "estimator", {k: p.get(k) for k in want}))
                break
    return {"n_products": n, "n_refined": refined, "violations": bad[:20], "n_violations": len(bad)}


def costs(paths: list[Path]) -> dict:
    rows = {}
    for f in paths:
        m = json.loads(str(np.load(f, allow_pickle=False)["meta"]))
        key = (m.get("construction", "pseudo" if "pseudo_seed" in m else "?"), m.get("iters"), str(m.get("capacity")), m.get("coords", "float32"))
        rows.setdefault(str(key), []).append(float(m.get("seconds_unfold", np.nan)))
    return {k: {"n": len(v), "median_seconds_unfold": float(np.nanmedian(v)), "max": float(np.nanmax(v))} for k, v in rows.items()}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--runs", type=Path, required=True, help="the s5p namespace runs/ directory")
    ap.add_argument("--s5e-runs", type=Path, required=True)
    ap.add_argument("--stage1", type=Path, required=True)
    ap.add_argument("--s5c-contract", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        raise SystemExit(f"refusing to overwrite {a.out}")
    stage1 = json.loads(a.stage1.read_text())
    cells = Cells(stage1, json.loads(a.s5c_contract.read_text()))
    num, conv = a.runs / "s2/num", a.runs / "s2/conv"
    new_products = sorted(num.rglob("*.npz")) + sorted((a.runs / "s2/prior").glob("*.npz"))
    receipt = {"schema": "s5p-stage2-receipt/1", "stage1_sha256": sha256(a.stage1),
               "code_sha256": {"s5p_stage2_analyze.py": sha256(Path(__file__).resolve()),
                               "s5p_stage1_inspect.py": sha256(Path(s1.__file__).resolve())},
               "runs_dir": str(a.runs), "s5e_runs_dir": str(a.s5e_runs),
               "study_K": study_k(conv, cells), "study_N": study_n(num, a.s5e_runs, cells),
               "study_C": study_c(num, a.s5e_runs, cells),
               "study_P": study_p(a.runs, a.s5e_runs, cells),
               "R_verification": verify_r(new_products + sorted(conv.glob("k_*.npz"))),
               "costs": costs(new_products + sorted(conv.glob("k_*.npz")))}
    a.out.write_text(json.dumps(receipt) + "\n")
    print(json.dumps({"K_M": {f: receipt["study_K"].get(f, {}).get("M") for f in ("b0", "cap")},
                      "N": {g: {P: {k: v[P][k] for k in ("median_sigma_num_base_pct", "median_sigma_boot_pct", "median_absorption",
                                                           "median_consistency", "absorbed")} for P in ("J", "H2")}
                            for g, v in receipt["study_N"].items() if g != "controls"},
                      "controls": receipt["study_N"]["controls"],
                      "six": receipt["study_C"]["six"], "R": receipt["R_verification"]}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
