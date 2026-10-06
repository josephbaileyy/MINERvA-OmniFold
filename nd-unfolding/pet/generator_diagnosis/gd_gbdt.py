"""PLAN-20261006 control C-c and the GBDT side of Q2/Q3: re-run the committed PET-vs-GBDT recipe on the D5 and
dev-tilt units to recover its per-iteration (pull, push), then apply the same reductions as for PET.

The fit is the comparison's own (`gbdt_comparison/pgc_run_fb._run_task`): the pinned PET source at `bc356b0c`
activated through `pgc_source`, `pgc_fb.build_problem`, `scalar_estimators.omnifold` with the frozen `h1` config,
efficiency-corrected, `truth4_species`, seed = 1 + FB index, 10 iterations. The only difference is the callback,
which also keeps `pull` (`run_omnifold`'s wrapper passes `push` only). A unit counts only if its E_avail R
reproduces the committed `gbdt_fb_compact.jsonl.gz` value at every k = 1..10 (to <= 1e-12).

    <venv with sklearn 1.8.0>/python gd_gbdt.py --pet-source <checkout at bc356b0c> --raw <run copies> \
        --reco-scalars reco_scalars.npy --row-features row_features.npz --out results/gbdt_reproduction.json
"""
from __future__ import annotations

import argparse
import json
import os
import resource
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

for v in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[v] = "1"
os.environ["OMP_NUM_THREADS"] = "2"            # the comparison's per-task threads

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
PET = HERE.parent
sys.path.insert(0, str(PET / "gbdt_comparison"))
sys.path.insert(0, str(HERE))
CASES = ("dev", "D5_nuwro", "D5p_nuwro", "D5_gibuu")
ITER = 10
TOL = 1e-12


def unit_run(case: str, r: int) -> str:
    return f"s4f/S4F-H2S1T24K5-FB{r}" if case == "dev" else f"s4s/S4S-H2S1T24K5-FB{r}-{case}"


def one(args: tuple) -> dict:
    case, r, paths, committed = args
    import pgc_source
    pgc_source.activate(Path(paths["pet_source"]))
    import matched_design as md
    import scalar_estimators as se
    import selection_data as sdm
    import pgc_fb
    import gd_analyze as gd

    t0, r0 = time.perf_counter(), resource.getrusage(resource.RUSAGE_SELF)
    run_dir = Path(paths["raw"]) / unit_run(case, r)
    cols = pgc_fb.InventoryColumns(paths["reco_scalars"], paths["row_features"])
    prob = pgc_fb.build_problem(run_dir, cols, sdm)
    X_reco_mc, _ = prob.reco_matrix("prior")
    X_reco_data, _ = prob.reco_matrix("pseudo")
    X_gen, _ = prob.truth_matrix("truth4_species")
    params = md.HGB_GRID["h1"]
    seed = 1 + r
    pushes, pulls = {}, {}

    def cb(rec):
        pushes[rec["iteration"]] = np.asarray(rec["push"], float).copy()
        pulls[rec["iteration"]] = np.asarray(rec["pull"], float).copy()

    se.omnifold(X_reco_mc=X_reco_mc, X_reco_data=X_reco_data[prob.s1_pseudo], X_gen_mc=X_gen,
                pass_reco_mc=prob.s1_prior, pass_gen_mc=prob.pg_prior,
                w_truth_mc=prob.prior["w_truth"], w_reco_mc=prob.prior["w_reco"], w_data=prob.w_data,
                make_step1=se.hgb_factory(params, seed), make_step2=se.hgb_factory(params, seed + 500),
                iterations=ITER, seed=seed, miss_rule="efficiency_corrected", callback=cb)
    A = np.load(run_dir / "replicate_arrays.npz")
    # rows of the problem must be the run's prior rows, in order (the weights are indexed by them)
    if not np.array_equal(np.asarray(prob.prior["rows"]), A["prior_rows"]):
        raise SystemExit(f"{case} FB{r}: problem rows differ from the run's prior rows")
    pt_ = A["prior_truth"]
    keep_p = A["prior_pass_truth"].astype(bool) & np.isfinite(pt_[:, 2])
    import score_design as sd
    eb_p, eb_s = sd.eavail_codes(pt_[:, 2]), sd.eavail_codes(A["pseudo_truth"][:, 2])
    eb_p[~keep_p] = -1
    keep_s = A["pseudo_pass_truth"].astype(bool) & np.isfinite(A["pseudo_truth"][:, 2])
    eb_s[~keep_s] = -1
    wt_p = A["prior_w_truth"].astype(float)
    target = sd.hist(eb_s, A["pseudo_w_truth"].astype(float) * A["pseudo_distortion"].astype(float), sd.N_EAV)
    prior = sd.hist(eb_p, wt_p, sd.N_EAV)
    R = {k: gd.rec(prior, sd.hist(eb_p, wt_p * pushes[k], sd.N_EAV), target) for k in range(1, ITER + 1)}
    diffs = {k: abs(R[k] - committed[str(k)]) for k in R}
    out = {"unit": f"{case}|FB{r}", "control_c_c": {"max_abs_diff": max(diffs.values()),
                                                     "pass": max(diffs.values()) <= TOL}, "R_by_k": R}
    if out["control_c_c"]["pass"]:
        rs = np.load(paths["reco_scalars"], mmap_mode="r")
        out.update(gd.reductions(A, pushes, pulls, gd.D5Bins(gd.D5T), ITER, k_op=7,
                                 reco_muon=gd.reco_muon_for(A, rs)))
    r1 = resource.getrusage(resource.RUSAGE_SELF)
    out["cpu_seconds"] = (r1.ru_utime - r0.ru_utime) + (r1.ru_stime - r0.ru_stime)
    out["wall_seconds"] = time.perf_counter() - t0
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for a_ in ("--pet-source", "--raw", "--reco-scalars", "--row-features", "--out"):
        ap.add_argument(a_, type=Path, required=True)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--limit", type=int, default=None)
    a = ap.parse_args(argv)
    import gd_analyze as gd
    g = gd.gbdt_records()
    paths = {k: str(getattr(a, k)) for k in ("pet_source", "raw", "reco_scalars", "row_features")}
    tasks = []
    for case in CASES:
        for r in range(8):
            name = f"GBDT-S4F-FB{r}-dev" if case == "dev" else f"GBDT-S4S-FB{r}-{case}"
            committed = {str(i["k"]): i["hist"]["eavail"]["recovery_raw"] for i in g[name]["iterations"]}
            tasks.append((case, r, paths, committed))
    tasks = tasks[: a.limit] if a.limit else tasks
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        units = list(ex.map(one, tasks))
    for u in units:
        print(u["unit"], "C-c", u["control_c_c"]["pass"], f"{u['control_c_c']['max_abs_diff']:.2e}", flush=True)
    import sklearn
    doc = {"schema": "pet-generator-diagnosis/gbdt-reproduction/1", "plan": "PLAN-20261006.md",
           "recipe": "gbdt_comparison RECIPE (h1, efficiency_corrected, truth4_species, seed 1+FB, 10 iterations)",
           "versions": {"python": sys.version.split()[0], "numpy": np.__version__, "sklearn": sklearn.__version__},
           "units": units, "cost": {"wall_seconds": time.time() - t0,
                                    "cpu_core_hours": sum(u["cpu_seconds"] for u in units) / 3600 * 2}}
    a.out.write_text(json.dumps(doc, indent=1, default=float) + "\n")
    bad = [u["unit"] for u in units if not u["control_c_c"]["pass"]]
    print("C-c failures:", bad, "| charged core-h (2 threads/task):", round(doc["cost"]["cpu_core_hours"], 3))
    return 0 if not bad else 2


if __name__ == "__main__":
    raise SystemExit(main())
