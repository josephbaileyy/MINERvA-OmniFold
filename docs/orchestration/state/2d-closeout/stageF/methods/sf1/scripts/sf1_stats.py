"""SF-1 statistics and evaluation (SF1-SPEC.md sections 2-4), through the production code path.

Run from the production tree (clean clone at 4f5a613f) with PYTHONPATH=nd-unfolding:
    cd $D && PYTHONPATH=nd-unfolding python3 $S/scripts/sf1_stats.py --out $S/results/sf1-results.json

1. Production reproduction: for each SF-1 null, ``s5p_joint.test_null`` over the production claim ensemble (the
   frozen design's calibration_glob, B as reached) with the frozen V; every recorded field of
   stage7/joint/joint-evaluate.json for that null must be reproduced exactly (else exit 3).
2. Pairs: T_tot and T_shape of the quarter products by ``s5p_joint.ensemble`` + ``s5p_joint.statistics`` (frozen V,
   the null's surrogate_seed0 and pseudo-seed keys, the null's domain, variant c = 0), and the production T of
   the same seeds at c = 0 (taken from the step-1 ensemble, and recomputed on the subset as a check).
3. Section 3: median shift, scale ratio, P95/P99 ratios, paired differences; paired bootstrap over seeds
   (10,000 resamples, numpy default_rng(20261019), one index matrix per null shared by both statistics), 95%
   percentile intervals.
4. Section 4: the adjusted claim ensemble of each SF-1 shape test (every claim variant: T -> median_h +
   (T - median_h)/s_lo - Delta_lo SD_h with the 200-pair half median/SD and the lower 95% ends), its claim p
   (largest over the variants), and the Holm/Clopper-Pearson decision by ``s5p_inference.holm_determined`` over
   the ten-test family (the other tests' claims as produced in step 1 or recorded in joint-evaluate.json).
"""
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

import numpy as np

import s5p_inference as si
import s5p_joint as sj

S = Path("/pscratch/sd/j/josephrb/methods-paper/sf1-20261019")
NS = Path("/pscratch/sd/j/josephrb/s5p-20260926")
DESIGN = Path("docs/orchestration/state/s5p/prod/design.json")
DESIGN_SHA = "404446eb2a770dc4412012c5e182e57a77afa2edd332c75de399a9281f536285"
EVAL = NS / "stage7/joint/joint-evaluate.json"
EVAL_SHA = "b9604502b1aa263508ba46f0be91846d7a2106f6f2fd0ba5c172b87ee256dd11"
V_PATH = NS / "stage3/V/V-s3v.npz"
NULLS = ["NuWro_21_09", "GENIE_2_12_10_CV", "GENIE_2_12_10_MEC"]
NBOOT, BOOT_SEED = 10_000, 20261019


def seed_of(p) -> int:
    return int(Path(p).stem.rsplit("_s", 1)[1])


def same(a, b, tol=0.0) -> bool:
    """Exact equality of recorded JSON values (floats compared exactly unless tol)."""
    if isinstance(a, dict):
        return isinstance(b, dict) and set(a) == set(b) and all(same(a[k], b[k], tol) for k in a)
    if isinstance(a, list):
        return isinstance(b, list) and len(a) == len(b) and all(same(x, y, tol) for x, y in zip(a, b))
    if isinstance(a, float) or isinstance(b, float):
        return abs(float(a) - float(b)) <= tol * max(1.0, abs(float(b)))
    return a == b


def describe(tq: np.ndarray, th: np.ndarray, idx: np.ndarray) -> dict:
    def point(q, h):
        mh, sh = np.median(h, -1), np.std(h, -1)
        return {"delta": (np.median(q, -1) - mh) / sh, "s": np.std(q, -1) / sh,
                "r95": np.percentile(q, 95, axis=-1) / np.percentile(h, 95, axis=-1),
                "r99": np.percentile(q, 99, axis=-1) / np.percentile(h, 99, axis=-1),
                "d_mean_over_sd_h": np.mean(q - h, -1) / sh, "d_median_over_sd_h": np.median(q - h, -1) / sh}
    pt = point(tq, th)
    bs = point(tq[idx], th[idx])
    d = tq - th
    out = {k: {"estimate": float(pt[k]), "ci95": [float(np.percentile(bs[k], 2.5)), float(np.percentile(bs[k], 97.5))]}
           for k in pt}
    out["half"] = {"median": float(np.median(th)), "sd": float(np.std(th)), "p95": float(np.percentile(th, 95)),
                   "p99": float(np.percentile(th, 99)), "min": float(th.min()), "max": float(th.max())}
    out["quarter"] = {"median": float(np.median(tq)), "sd": float(np.std(tq)), "p95": float(np.percentile(tq, 95)),
                      "p99": float(np.percentile(tq, 99)), "min": float(tq.min()), "max": float(tq.max())}
    out["paired_difference"] = {"mean": float(d.mean()), "sd": float(np.std(d, ddof=1)), "median": float(np.median(d)),
                                "quantiles_5_25_75_95": [float(x) for x in np.percentile(d, [5, 25, 75, 95])],
                                "min": float(d.min()), "max": float(d.max()), "fraction_negative": float(np.mean(d < 0)),
                                "corr_q_h": float(np.corrcoef(tq, th)[0, 1]), "n": int(d.size)}
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--nulls", default=",".join(NULLS), help="a subset for a preliminary check run (the final run uses all three)")
    a = ap.parse_args()
    nulls_run = a.nulls.split(",")
    if a.out.exists():
        raise SystemExit(f"refusing to overwrite {a.out}")
    assert sj.sha256(DESIGN) == DESIGN_SHA, "design sha256"
    assert sj.sha256(EVAL) == EVAL_SHA, "joint-evaluate sha256"
    design = json.loads(DESIGN.read_text())
    recorded = json.loads(EVAL.read_text())
    stage1 = json.loads(Path(design["stage1"]).read_text())
    supported = json.loads(Path(design["s5c_contract"]).read_text())["measurement"]["partition_J"]["supported_cells"]
    U, names, pz_index = sj.j_matrix(stage1, supported)
    model = sj.Model(design, U)
    sj.check_v(design, V_PATH)
    V = np.asarray(np.load(V_PATH, allow_pickle=False)["V"], float)
    coefs = [float(c) for c in design["shift_coefficients"]]
    res = {"schema": "sf1-results/1", "design_sha256": DESIGN_SHA, "v_sha256": sj.sha256(V_PATH),
           "joint_evaluate_sha256": EVAL_SHA, "bootstrap": {"n": NBOOT, "seed": BOOT_SEED, "interval": "percentile 2.5/97.5"},
           "nulls": {}}
    claims = {k: {"p": v["p"], "k": v["k"], "B": v["B"]} for k, v in recorded["decisions"].items()}
    adjusted_claims = dict(claims)
    sens_claims = dict(claims)
    pairs_rows = []
    for key in nulls_run:
        spec = design["nulls"][key]
        files = sj.product_files(spec["calibration_glob"])
        B = sj.calibration_count(spec)
        assert len(files) == B, (key, len(files), B)
        entry = sj.test_null(model, design, key, V, names, pz_index, files, coefs)
        nulls = entry.pop("_nulls")
        rec = recorded["tests"][key]
        got = json.loads(json.dumps(entry))
        repro = {f: same(got[f], rec[f]) for f in rec}
        repro_tol = {f: same(got[f], rec[f], 1e-9) for f in rec}
        res_n = {"B": B, "reproduces_joint_evaluate_exactly": repro, "reproduces_joint_evaluate_rel_1e-9": repro_tol}
        if not all(repro_tol.values()):
            print(json.dumps({key: repro_tol}))
            raise SystemExit(3)
        variant_names = list(entry["variants"])  # the claim variants, in test_null's order
        assert len(variant_names) == len(nulls)
        prod_seeds = np.array([seed_of(p) for p in files])
        # the 200 selected seeds and their quarter products
        sel = [int(x) for x in (S / "tables" / f"seeds-{key}.txt").read_text().split()]
        qfiles = sj.product_files(str(S / "runs/quarter" / key / f"sf1q_{key}_s*.npz"))
        qseeds = np.array([seed_of(p) for p in qfiles])
        assert set(qseeds) <= set(sel), "a quarter product outside the selection"
        Fq, sq = sj.ensemble(model, qfiles)
        assert np.array_equal(sq, qseeds)
        mu, var = sj.prediction(spec["prediction"], U)
        dom = np.ones(len(names), bool) if spec.get("domain") != "pz_lt_6" else (pz_index <= 1)
        tq_tot, tq_shp = sj.statistics(Fq, mu, var, V, dom, spec["surrogate_seed0"], seeds=sq)
        pos = {int(s): i for i, s in enumerate(prod_seeds)}
        hi = np.array([pos[int(s)] for s in sq])
        th_tot, th_shp = nulls[0][0][hi], nulls[0][1][hi]
        # check: the half T of the subset recomputed alone equals the ensemble's (draws keyed by seed)
        Fh_sub, sh_sub = sj.ensemble(model, [files[i] for i in hi])
        c_tot, c_shp = sj.statistics(Fh_sub, mu, var, V, dom, spec["surrogate_seed0"], seeds=sh_sub)
        res_n["half_subset_recomputed_equal"] = bool(np.array_equal(c_tot, th_tot) and np.array_equal(c_shp, th_shp))
        res_n["n_selected"], res_n["n_pairs"] = len(sel), int(sq.size)
        res_n["missing_quarter_seeds"] = sorted(set(sel) - set(int(s) for s in sq))
        res_n["shortfall_fraction"] = 1 - sq.size / len(sel)
        res_n["shortfall_over_10pct"] = bool(res_n["shortfall_fraction"] > 0.10)
        rng = np.random.default_rng(BOOT_SEED)
        idx = rng.integers(0, sq.size, size=(NBOOT, sq.size))
        res_n["total"] = describe(tq_tot, th_tot, idx)
        res_n["shape"] = describe(tq_shp, th_shp, idx)
        res_n["T_obs"] = {"total": entry["T_total_obs"], "shape": entry["T_shape_obs"]}
        for i, sd in enumerate(sq):
            pairs_rows.append((key, int(sd), float(th_tot[i]), float(tq_tot[i]), float(th_shp[i]), float(tq_shp[i])))
        # section 4: the adjusted claim ensemble of the shape test
        k_stat = 1
        d = res_n["shape"]
        med_h, sd_h = d["half"]["median"], d["half"]["sd"]
        s_lo, delta_lo = d["s"]["ci95"][0], d["delta"]["ci95"][0]
        t_obs = entry["T_shape_obs"]
        per_variant, per_variant_sens = {}, {}
        for vn, nn in zip(variant_names, nulls):
            t = nn[k_stat]
            adj = med_h + (t - med_h) / s_lo - delta_lo * sd_h
            pv = si.mc_pvalue(t_obs, adj)
            per_variant[vn] = dict(pv, median=float(np.median(adj)), sd=float(np.std(adj)),
                                   margin_in_sd=float((t_obs - np.median(adj)) / np.std(adj)),
                                   unadjusted=si.mc_pvalue(t_obs, t))
            # sensitivity (not the frozen rule): centre and scale at the variant's own production median and SD
            m_v, s_v = float(np.median(t)), float(np.std(t))
            adj2 = m_v + (t - m_v) / s_lo - delta_lo * s_v
            per_variant_sens[vn] = si.mc_pvalue(t_obs, adj2)
        claim = max(per_variant.values(), key=lambda v: v["p"])
        claim_sens = max(per_variant_sens.values(), key=lambda v: v["p"])
        prod_claim = recorded["tests"][key]["shape"]
        res_n["adjusted_shape"] = {"median_h": med_h, "sd_h": sd_h, "s_lo": s_lo, "delta_lo": delta_lo,
                                   "transform": "T' = median_h + (T - median_h)/s_lo - delta_lo*sd_h",
                                   "variants": per_variant, "claim": {k: claim[k] for k in ("p", "k", "B", "tail_interval")},
                                   "production_claim": {k: prod_claim[k] for k in ("p", "k", "B")},
                                   "sensitivity_own_variant_centre": {"variants": per_variant_sens,
                                                                      "claim": {k: claim_sens[k] for k in ("p", "k", "B")}}}
        adjusted_claims[f"{key}:shape"] = {"p": claim["p"], "k": claim["k"], "B": claim["B"]}
        sens_claims[f"{key}:shape"] = {"p": claim_sens["p"], "k": claim_sens["k"], "B": claim_sens["B"]}
        res["nulls"][key] = res_n
    res["holm_production_recomputed"] = si.holm_determined(claims, design["alpha_family"])
    res["holm_production_recomputed_equals_record"] = same(res["holm_production_recomputed"], recorded["decisions"])
    res["holm_adjusted_all_three"] = si.holm_determined(adjusted_claims, design["alpha_family"])
    res["holm_adjusted_one_at_a_time"] = {}
    for key in nulls_run:
        c = dict(claims)
        c[f"{key}:shape"] = adjusted_claims[f"{key}:shape"]
        res["holm_adjusted_one_at_a_time"][key] = si.holm_determined(c, design["alpha_family"])[f"{key}:shape"]
    res["holm_sensitivity_own_variant_centre"] = si.holm_determined(sens_claims, design["alpha_family"])
    res["outcome"] = {}
    res["nulls_run"] = nulls_run
    for key in nulls_run:
        dec = res["holm_adjusted_all_three"][f"{key}:shape"]["decision"]
        alone = res["holm_adjusted_one_at_a_time"][key]["decision"]
        res["outcome"][f"{key}:shape"] = {"decision_adjusted": dec, "decision_adjusted_alone": alone,
                                          "production_decision": recorded["decisions"][f"{key}:shape"]["decision"],
                                          "alone_agrees": dec == alone,
                                          "result": "PASS" if dec == "rejected" else "FAIL"}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(res, indent=1) + "\n")
    with open(a.out.with_name("sf1-pairs.csv"), "w") as fh:
        fh.write("null,seed,T_total_half,T_total_quarter,T_shape_half,T_shape_quarter\n")
        for r in pairs_rows:
            fh.write(",".join([r[0], str(r[1])] + [repr(x) for x in r[2:]]) + "\n")
    print(json.dumps(res["outcome"], indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
