#!/usr/bin/env python3
"""Methods-paper M2 archive checks (read-only on CFS; numpy/scipy only).

CHECK 1: per-experiment J-cell truth x_true (half-B realization) against the null's G on the test domain.
CHECK 2: the production null covariance of the T_total residual against the frozen metric W = V + diag Var(mu_G).

Every product is hashed from the bytes that were parsed and the hash is compared with the archive's SHA256SUMS.
The production code (s5p_joint.py, s5p_inference.py, s5p_stage1_inspect.py at origin/main 19b46af9, byte-identical
to the frozen 4f5a613f) is imported, not retyped: j_matrix, Model.apply (laterals, normalization, rounding noise),
the eps draw of statistics(), stat_total/stat_shape and ledoit_wolf.

Usage: python -I m2_archive_checks.py CODE_DIR OUT_DIR
"""
import hashlib
import io
import json
import sys
import time
from pathlib import Path

CODE, OUT = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
sys.path.insert(0, str(CODE))
import numpy as np  # noqa: E402

import s5p_inference as si  # noqa: E402
import s5p_joint as sj  # noqa: E402

ARCH = Path("/global/cfs/cdirs/m3246/josephrb/s5p-archive-20261006")
NS = "/pscratch/sd/j/josephrb/s5p-20260926/"
MANIFEST = {}
for line in (ARCH / "SHA256SUMS").read_text().splitlines():
    h, p = line.split(None, 1)
    MANIFEST[p.strip().lstrip("./") if p.startswith("./") else p.strip()] = h
READ = []  # (path, sha256, bytes, manifest verdict)


def to_archive(p: str) -> Path:
    return ARCH / p[len(NS):] if p.startswith(NS) else Path(p)


def load(path: Path):
    b = Path(path).read_bytes()
    h = hashlib.sha256(b).hexdigest()
    rel = str(path)[len(str(ARCH)) + 1:] if str(path).startswith(str(ARCH)) else None
    verdict = "not-in-archive" if rel is None else ("match" if MANIFEST.get(rel) == h else
                                                    ("MISMATCH" if rel in MANIFEST else "ABSENT-from-SHA256SUMS"))
    READ.append((str(path), h, len(b), verdict))
    return np.load(io.BytesIO(b), allow_pickle=False)


def file_sha(path) -> str:
    h = sj.sha256(path)
    rel = str(path)[len(str(ARCH)) + 1:] if str(path).startswith(str(ARCH)) else None
    verdict = "not-in-archive" if rel is None else ("match" if MANIFEST.get(rel) == h else "MISMATCH/ABSENT")
    READ.append((str(path), h, Path(path).stat().st_size, verdict))
    return h


def q(x, qs=(50, 90, 100)):
    x = np.asarray(x, float)
    return {f"p{k}": float(np.percentile(x, k)) for k in qs}


def whitened(C, W):
    """eigenvalues of W^-1/2 C W^-1/2 (symmetric generalized eigenproblem)."""
    L = np.linalg.cholesky(W)
    Li = np.linalg.inv(L)
    return np.sort(np.linalg.eigvalsh(Li @ C @ Li.T))[::-1]


def eig_summary(lam):
    lam = np.asarray(lam, float)
    return {"trace": float(lam.sum()), "max": float(lam.max()), "min": float(lam.min()),
            "median": float(np.median(lam)), "top5": [float(v) for v in lam[:5]],
            "n_eff_tr2_over_sum_sq": float(lam.sum() ** 2 / (lam ** 2).sum()),
            "n_above_1": int((lam > 1).sum()), "n_below_0p1": int((lam < 0.1).sum())}


def main() -> int:
    t0 = time.time()
    design = json.loads((CODE / "design.json").read_text())
    if sj.sha256(CODE / "design.json") != "404446eb2a770dc4412012c5e182e57a77afa2edd332c75de399a9281f536285":
        raise SystemExit("design sha differs")
    supported = json.loads((CODE / "s5c_contract.json").read_text())["measurement"]["partition_J"]["supported_cells"]
    U, names, pz_index = sj.j_matrix({}, supported)
    # Model inputs (lateral endpoints, jitters, data central) are read from pscratch exactly as the evaluation did
    for b in sorted(design["lateral_endpoints"]):
        for p in design["lateral_endpoints"][b]:
            file_sha(p)
    for p in design["data_jitters"] + [design["data_central"]]:
        file_sha(p)
    file_sha(to_archive(design["data_central"]))
    model = sj.Model(design, U)
    vpath = ARCH / "stage3/V/V-s3v.npz"
    if file_sha(vpath) != design["v_sha256"]:
        raise SystemExit("V sha differs from the design's")
    V = np.asarray(np.load(vpath, allow_pickle=False)["V"], float)
    ref = json.loads((CODE / "joint-evaluate.json").read_text())["tests"]
    res = {"n_J": len(names), "nulls": {}}
    keep_arrays = {}

    for key, spec in design["nulls"].items():
        glob_arch = str(to_archive(spec["calibration_glob"]))
        files = sj.product_files(glob_arch)
        ppath = to_archive(spec["prediction"])
        file_sha(ppath)
        mu, var = sj.prediction(ppath, U)
        dom = np.ones(len(names), bool) if spec.get("domain") != "pz_lt_6" else (pz_index <= 1)
        Fraw, F, XT, seeds, wt, codes, detsets = [], [], [], [], {}, {}, {}
        for p in files:
            z = load(Path(p))
            m = json.loads(str(z["meta"]))
            fr = U @ np.asarray(z["xsec_flat"], float)
            Fraw.append(fr)
            F.append(model.apply(fr, m, int(m["pseudo_seed"])))
            XT.append(U @ np.asarray(z["xtrue_flat"], float))
            seeds.append(int(m["pseudo_seed"]))
            k = json.dumps((m.get("nuisance_draw") or {}).get("weight_treatment"), sort_keys=True)[:200]
            wt[k] = wt.get(k, 0) + 1
            c = m["code_sha256"].get("s5p_nullexp.py", "?")
            codes[c] = codes.get(c, 0) + 1
            d = ",".join(m.get("detector_bands") or [])
            detsets[d] = detsets.get(d, 0) + 1
        Fraw, F, XT, seeds = map(np.asarray, (Fraw, F, XT, seeds))
        n = len(files)
        eps = np.array([np.random.default_rng([int(spec["surrogate_seed0"]), int(s), 0x4A02]).normal(size=mu.size)
                        * np.sqrt(var) for s in seeds])
        # reproduce the recorded unshifted null (variant 0.0) with the production statistics()
        tt, ts = sj.statistics(F, mu, var, V, dom, spec["surrogate_seed0"], seeds=seeds)
        rv = ref[key]["variants"]["0.0"]
        repro = {"B": n, "T_total_median": float(np.median(tt)), "T_total_sd": float(np.std(tt)),
                 "T_total_mean": float(tt.mean()), "T_shape_median": float(np.median(ts)),
                 "T_shape_sd": float(np.std(ts)),
                 "recorded": {k2: rv[k2] for k2 in ("null_T_total_median", "null_T_total_sd", "null_T_shape_median",
                                                     "null_T_shape_sd")},
                 "recorded_B": ref[key]["total"].get("B")}
        d = np.where(dom)[0]
        Wd = V[np.ix_(d, d)] + np.diag(var[d])
        Winv = np.linalg.inv(Wd)
        R = F[:, d] - (mu[d] + eps[:, d])          # the residual T_total is the W^-1 norm of
        Craw = np.cov(Fraw[:, d].T)                  # unfolded only
        CF = np.cov(F[:, d].T)                       # + laterals, normalization, rounding noise
        CR = np.cov(R.T)                             # + prediction MC error (the statistic's residual)
        Cxt = np.cov(XT[:, d].T)
        b = R.mean(0)
        lamR = whitened(CR, Wd)
        lam_FV = whitened(CF, V[np.ix_(d, d)])
        bWb = float(b @ Winv @ b)
        pred_mean = float(np.trace(Winv @ CR) * (n - 1) / n + bWb)
        pred_sd = float(np.sqrt(2 * np.sum(lamR ** 2) + 4 * b @ Winv @ CR @ Winv @ b))
        # shape analog: linearize p = f / sum f about mu; Vs = J W J', drop the last cell as stat_shape does
        s = mu[d].sum()
        Jm = (np.eye(d.size) - np.outer(mu[d] / s, np.ones(d.size))) / s
        Vs = (Jm @ Wd @ Jm.T)[:-1, :-1]
        Cs = (Jm @ CR @ Jm.T)[:-1, :-1]
        bs = (Jm @ b)[:-1]
        shape_lin = {"trace_Vs^-1_Cs": float(np.trace(np.linalg.solve(Vs, Cs))),
                     "bias_term": float(bs @ np.linalg.solve(Vs, bs)), "n_cells": int(d.size - 1),
                     "eig": eig_summary(whitened(Cs, Vs))}
        # CHECK 1
        rel = XT[:, d] / mu[d] - 1.0
        sd_rel = rel.std(0, ddof=1)
        mean_rel = rel.mean(0)
        se_mean = sd_rel / np.sqrt(n)
        sd_xt, sd_raw, sd_R = XT[:, d].std(0, ddof=1), Fraw[:, d].std(0, ddof=1), R.std(0, ddof=1)
        corr = np.array([np.corrcoef(XT[:, d][:, j], Fraw[:, d][:, j])[0, 1] for j in range(d.size)])
        xt_off_sd = (XT[:, d].mean(0) - mu[d]) / sd_R
        res["nulls"][key] = {
            "B": n, "domain_cells": int(d.size), "files_first_last": [files[0], files[-1]],
            "seeds_min_max": [int(seeds.min()), int(seeds.max())],
            "nullexp_code_sha_counts": codes, "detector_band_sets": detsets, "weight_treatment_counts": wt,
            "reproduction_of_recorded_null": repro,
            "check1": {
                "rel_sd_xtrue_over_G_minus_1": q(sd_rel),
                "mean_xtrue_over_G_minus_1": {"median": float(np.median(mean_rel)), "max_abs": float(np.abs(mean_rel).max()),
                                              "median_abs_in_SE": float(np.median(np.abs(mean_rel / se_mean))),
                                              "max_abs_in_SE": float(np.abs(mean_rel / se_mean).max()),
                                              "cell_average": float(mean_rel.mean()),
                                              "rate_weighted": float(XT[:, d].sum(1).mean() / mu[d].sum() - 1)},
                "xtrue_mean_minus_G_in_null_SD": {"median_abs": float(np.median(np.abs(xt_off_sd))),
                                                  "max_abs": float(np.abs(xt_off_sd).max())},
                "ratio_SD_xtrue_over_SD_unfolded_raw": {**q(sd_xt / sd_raw), "median": float(np.median(sd_xt / sd_raw))},
                "ratio_SD_xtrue_over_SD_T_residual": {**q(sd_xt / sd_R), "median": float(np.median(sd_xt / sd_R))},
                "corr_xtrue_vs_unfolded_raw_per_cell": q(corr, (10, 50, 90)),
                "trace_Winv_C_xtrue": float(np.trace(Winv @ Cxt)),
                "rel_sd_unfolded_raw": q(Fraw[:, d].std(0, ddof=1) / mu[d]),
                "rel_sd_T_residual": q(sd_R / mu[d]),
            },
            "check2": {
                "trace_Winv_C_raw_unfolded": float(np.trace(Winv @ Craw)),
                "trace_Winv_C_with_additive_terms": float(np.trace(Winv @ CF)),
                "trace_Winv_diag_var_mu": float(np.sum(np.diag(Winv) * var[d])),
                "trace_Winv_C_prod_residual": float(np.trace(Winv @ CR)),
                "bias_term_bWb": bWb,
                "predicted_mean_T_total": pred_mean, "predicted_sd_T_total_gaussian": pred_sd,
                "eig_Winv_C_prod": eig_summary(lamR),
                "trace_Vinv_C_F_(V-construction_analog)": float(lam_FV.sum()),
                "eig_Vinv_C_F": eig_summary(lam_FV),
                "diag_ratio_C_F_over_V": q(np.diag(CF) / np.diag(V)[d], (10, 50, 90)),
                "diag_ratio_var_mu_over_W": q(var[d] / np.diag(Wd), (10, 50, 90)),
                "shape_linearized": shape_lin,
            },
        }
        keep_arrays[key] = {"Fraw": Fraw, "F": F, "XT": XT, "mu": mu, "var": var, "dom": dom}
        print(key, n, "done", round(time.time() - t0, 1), flush=True)

    # The V pilot: rebuild V from its 194 products (pscratch) with the production ensemble() and ledoit_wolf()
    pfiles = sj.product_files(design["v_ensemble_glob"])
    Fp_raw, Fp, XTp, pseeds, pcodes, pwt, pdet = [], [], [], [], {}, {}, {}
    for p in pfiles:
        z = load(Path(p))
        m = json.loads(str(z["meta"]))
        fr = U @ np.asarray(z["xsec_flat"], float)
        Fp_raw.append(fr)
        Fp.append(model.apply(fr, m, int(m["pseudo_seed"])))
        XTp.append(U @ np.asarray(z["xtrue_flat"], float))
        c = m["code_sha256"].get("s5p_nullexp.py", "?")
        pcodes[c] = pcodes.get(c, 0) + 1
        k = json.dumps((m.get("nuisance_draw") or {}).get("weight_treatment"), sort_keys=True)[:200]
        pwt[k] = pwt.get(k, 0) + 1
        dd = ",".join(m.get("detector_bands") or [])
        pdet[dd] = pdet.get(dd, 0) + 1
    Fp_raw, Fp, XTp = map(np.asarray, (Fp_raw, Fp, XTp))
    Vre, shrink = sj.ledoit_wolf(Fp)
    mt = keep_arrays["MnvTune_v1"]
    Cprod_F = np.cov(mt["F"].T)
    Cpil_F = np.cov(Fp.T)
    W109 = V + np.diag(mt["var"])
    Winv109 = np.linalg.inv(W109)
    # robust (MAD) per-cell SDs, to see whether a few pilot draws carry the excess
    mad = lambda X: 1.4826 * np.median(np.abs(X - np.median(X, 0)), 0)  # noqa: E731
    sdP, sdQ = Fp.std(0, ddof=1), mt["F"].std(0, ddof=1)
    # leave-out-top: drop the pilot draws with the largest whitened norm and recompute the trace
    Cp_c = Fp - Fp.mean(0)
    Li = np.linalg.inv(np.linalg.cholesky(V))
    wn = np.sum((Cp_c @ Li.T) ** 2, 1)
    order = np.argsort(wn)[::-1]
    Cq_c = mt["F"] - mt["F"].mean(0)
    wnq = np.sum((Cq_c @ Li.T) ** 2, 1)
    drop = {}
    for kdrop in (0, 1, 2, 5, 10):
        keep = np.ones(len(Fp), bool)
        keep[order[:kdrop]] = False
        drop[str(kdrop)] = float(np.trace(np.linalg.solve(V, np.cov(Fp[keep].T))))
    res["V_pilot"] = {
        "n": len(pfiles), "files_first_last": [pfiles[0], pfiles[-1]], "nullexp_code_sha_counts": pcodes,
        "weight_treatment_counts": pwt, "detector_band_sets": pdet,
        "rebuilt_V_max_abs_rel_diff": float(np.max(np.abs(Vre - V)) / np.max(np.abs(V))),
        "rebuilt_shrinkage": shrink,
        "trace_Vinv_C_pilot_F": float(np.trace(np.linalg.solve(V, Cpil_F))),
        "trace_Vinv_C_prod_F_MnvTune": float(np.trace(np.linalg.solve(V, Cprod_F))),
        "trace_Winv_(C_pilot_F+diag var_mu)": float(np.trace(Winv109 @ (Cpil_F + np.diag(mt["var"])))),
        "per_cell_SD_ratio_pilot_over_prod": q(sdP / sdQ, (10, 50, 90, 100)),
        "per_cell_MAD_ratio_pilot_over_prod": q(mad(Fp) / mad(mt["F"]), (10, 50, 90, 100)),
        "per_cell_SD_ratio_pilot_over_prod_raw_unfolded": q(Fp_raw.std(0, ddof=1) / mt["Fraw"].std(0, ddof=1), (10, 50, 90, 100)),
        "per_cell_SD_ratio_pilot_over_prod_xtrue": q(XTp.std(0, ddof=1) / mt["XT"].std(0, ddof=1), (10, 50, 90, 100)),
        "pilot_whitened_norm_sq_in_V": q(wn, (50, 90, 99, 100)),
        "prod_whitened_norm_sq_in_V": q(wnq, (50, 90, 99, 100)),
        "trace_Vinv_C_pilot_after_dropping_top_k_pilot_draws": drop,
        "pilot_mean_minus_prod_mean_in_prod_SD": q(np.abs(Fp.mean(0) - mt["F"].mean(0)) / sdQ, (50, 90, 100)),
    }
    # which production draws carry the 100th-percentile whitened norm, for the outlier picture
    res["seconds"] = round(time.time() - t0, 1)
    (OUT / "m2_archive_results.json").write_text(json.dumps(res, indent=1))
    with open(OUT / "inputs_sha256.tsv", "w") as fh:
        fh.write("path\tsha256\tbytes\tarchive_SHA256SUMS\n")
        for r in READ:
            fh.write("\t".join(map(str, r)) + "\n")
    verdicts = {}
    for r in READ:
        verdicts[r[3]] = verdicts.get(r[3], 0) + 1
    print(json.dumps({"inputs": len(READ), "verdicts": verdicts, "seconds": res["seconds"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
