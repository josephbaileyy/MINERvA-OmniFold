import sys
from pathlib import Path
import time
import numpy as np
import torch
import json
from typing import Callable, Any

b1_path = Path(__file__).resolve().parent.parent / "phase_b" / "scalar"
sys.path.insert(0, str(b1_path))

import run_ibu
import scalar_common as scm
import scalar_omnifold as so
import features
import binned_unfolding as bu

from aussie_scalar import train_classifier, train_unfolder, _capped_ratio
# The OmniFold loop needs the (ratio, n_saturated) form; AUSSIE's _capped_ratio returns the ratio only.
from scalar_omnifold import _capped_ratio as _capped_ratio_with_saturation

def _split(n: int, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    idx = rng.permutation(n)
    n_tr = int(0.8 * n)
    return idx[:n_tr], idx[n_tr:]

def run_scalar_omnifold_patched(*, X_reco_mc: np.ndarray, X_reco_data: np.ndarray, X_gen_mc: np.ndarray,
                        pass_reco_mc: np.ndarray, pass_gen_mc: np.ndarray,
                        w_truth_mc: np.ndarray, w_reco_mc: np.ndarray, w_data: np.ndarray,
                        make_step1, make_step2,
                        iterations: int, seed: int, warm_start: bool = False,
                        callback = None, miss_handling: str = "carry") -> dict:
    s1 = np.asarray(pass_reco_mc, dtype=bool)
    pg = np.asarray(pass_gen_mc, dtype=bool)
    w_t = np.asarray(w_truth_mc, dtype=np.float64).copy()
    w_r = np.asarray(w_reco_mc, dtype=np.float64).copy()
    w_d = np.asarray(w_data, dtype=np.float64).copy()
    c = bu.ENGINE_NORMALIZATION / w_r[s1].sum()
    w_t *= c
    w_r *= c
    w_d *= bu.ENGINE_NORMALIZATION / w_d.sum()

    rng = np.random.default_rng(int(seed))
    n_mc1 = int(s1.sum())
    X1 = np.concatenate([np.asarray(X_reco_mc)[s1], np.asarray(X_reco_data)], axis=0)
    y1 = np.concatenate([np.zeros(n_mc1), np.ones(len(w_d))])
    tr1, va1 = _split(X1.shape[0], rng)
    
    n_pg = int(pg.sum())
    Xg = np.asarray(X_gen_mc)[pg]
    s1_in_pg = s1[pg]
    
    if miss_handling == "eff":
        Xg_train = Xg[s1_in_pg]
        n_train = int(s1_in_pg.sum())
        X2 = np.concatenate([Xg_train, Xg_train], axis=0)
        y2 = np.concatenate([np.zeros(n_train), np.ones(n_train)])
    else:
        X2 = np.concatenate([Xg, Xg], axis=0)
        y2 = np.concatenate([np.zeros(n_pg), np.ones(n_pg)])
        
    tr2, va2 = _split(X2.shape[0], rng)

    push = np.ones(w_t.shape[0], dtype=np.float64)
    pull = push.copy()
    model1 = make_step1(0) if warm_start else None
    model2 = make_step2(0) if warm_start else None
    for k in range(1, iterations + 1):
        m1 = model1 if warm_start else make_step1(k)
        w1 = np.concatenate([(push * w_r)[s1], w_d])
        t0 = time.perf_counter()
        
        # Patch HGB fit to not use X_val if model is HGB
        if hasattr(m1, "model") and type(m1.model).__name__ == "HistGradientBoostingClassifier":
            m1.model.fit(X1[tr1], y1[tr1], sample_weight=w1[tr1])
            info1 = {"model": "hgb", "n_iter": int(m1.model.n_iter_)}
        else:
            info1 = m1.fit(X1[tr1], y1[tr1], w1[tr1], X1[va1], y1[va1], w1[va1])
            
        ratio1, sat1 = _capped_ratio_with_saturation(m1.logit(np.asarray(X_reco_mc)[s1]))
        info1.update({"seconds": time.perf_counter() - t0, "saturated": sat1})
        prev_push = push
        pull = push.copy()
        pull[s1] = push[s1] * ratio1

        m2 = model2 if warm_start else make_step2(k)
        if miss_handling == "eff":
            w2 = np.concatenate([w_t[pg][s1_in_pg], (w_t * pull)[pg][s1_in_pg]])
        else:
            w2 = np.concatenate([w_t[pg], (w_t * pull)[pg]])
            
        t0 = time.perf_counter()
        if hasattr(m2, "model") and type(m2.model).__name__ == "HistGradientBoostingClassifier":
            m2.model.fit(X2[tr2], y2[tr2], sample_weight=w2[tr2])
            info2 = {"model": "hgb", "n_iter": int(m2.model.n_iter_)}
        else:
            info2 = m2.fit(X2[tr2], y2[tr2], w2[tr2], X2[va2], y2[va2], w2[va2])
            
        ratio2, sat2 = _capped_ratio_with_saturation(m2.logit(Xg))
        info2.update({"seconds": time.perf_counter() - t0, "saturated": sat2})
        push = np.ones_like(push)
        push[pg] = ratio2
        if callback is not None:
            callback({"iteration": k, "pull": pull, "push": push, "prev_push": prev_push})
    return {"pull": pull, "push": push}

def transform(x):
    return np.sign(x) * np.log1p(np.abs(x))

def run_all(pop_file: str):
    pop = scm.load_populations(pop_file)
    endpoint = scm.endpoint_from_populations(pop)
    
    pga = pop["a_pass_truth"].astype(bool)
    s1a = pga & pop["a_pass_reco"].astype(bool)
    pgb = pop["b_pass_truth"].astype(bool)
    s1b = pgb & pop["b_pass_reco"].astype(bool)
    w_data = (pop["a_w_reco"] * pop["a_tilt"])[s1a]
    
    inputs = "muon_eavail"
    
    X_reco_mc, fill_mc = features.reco_matrix(pop, "b", inputs, used=s1b)
    X_reco_mc_pass = X_reco_mc[s1b]
    X_reco_data, fill_data = features.reco_matrix(pop, "a", inputs, used=s1a)
    X_reco_data = X_reco_data[s1a]
    X_gen_mc, fill_gen = features.truth_matrix(pop, "b", "truth4", used=pgb)
    X_gen_mc_pass = X_gen_mc[s1b]
    X_gen_mc_miss = X_gen_mc[pgb & ~s1b]
    
    w_truth_mc = pop["b_w_truth"][pgb]
    w_reco_mc = pop["b_w_reco"]
    
    c = bu.ENGINE_NORMALIZATION / w_reco_mc[s1b].sum()
    w_truth_mc *= c
    w_reco_mc *= c
    w_data *= bu.ENGINE_NORMALIZATION / w_data.sum()
    
    w_reco_mc_pass = w_reco_mc[s1b]
    w_truth_mc_pass = w_truth_mc[s1b[pgb]]
    w_truth_mc_miss = w_truth_mc[~s1b[pgb]]
    
    results = []
    
    lambdas = [0, 0.01, 0.1, 1, 10, 100, 1000]
    seeds = [1, 2, 3]
    
    for l in lambdas:
        for seed in seeds:
            t0 = time.perf_counter()
            classifier, c_mean, c_std = train_classifier(X_reco_mc_pass, X_reco_data, w_reco_mc_pass, w_data, epochs=50, lr=1e-3, seed=seed)
            unfolder, z_mean, z_std = train_unfolder(classifier, c_mean, c_std, X_gen_mc_pass, X_reco_mc_pass, w_truth_mc_pass, X_gen_mc_miss, w_truth_mc_miss, lambda_miss=l, epochs=50, lr=1e-3, seed=seed)
            unfolder.eval()
            with torch.no_grad():
                Z_all_t = transform(X_gen_mc)
                Z_all_z = (Z_all_t - z_mean) / z_std
                Z_tensor = torch.tensor(Z_all_z, dtype=torch.float32)
                lw_z = unfolder(Z_tensor).numpy()
                
            ratio2 = _capped_ratio(lw_z)
            push = np.ones_like(w_truth_mc)
            push = ratio2
            t1 = time.perf_counter()
            
            low_acc_mask = (np.asarray(endpoint.region_b) == "low_acceptance")
            passes = s1b[pgb]
            misses = ~s1b[pgb]
            low_acc_passes = low_acc_mask & passes
            low_acc_misses = low_acc_mask & misses
            
            ratio2_valid = ratio2[pgb]
            r_passes = np.mean(ratio2_valid[low_acc_passes]) if low_acc_passes.any() else 0
            r_misses = np.mean(ratio2_valid[low_acc_misses]) if low_acc_misses.any() else 0
            
            rec_score = scm.score_push(endpoint, push, run_ibu.SCOREABLE, run_ibu.INFORMATIONAL)
            top_bin_res = rec_score["aggregate"]["signed_residual_per_bin"][-1]
            
            res_dict = {
                "method": "AUSSIE",
                "miss_handling": f"lambda={l}",
                "seed": seed,
                "k_or_lambda": l,
                "aggregate": rec_score["aggregate"]["recovery"],
                "low": rec_score["regions"]["low_acceptance"]["recovery"],
                "moderate": rec_score["regions"]["moderate"]["recovery"],
                "good": rec_score["regions"]["good"]["recovery"],
                "top_bin_res": top_bin_res,
                "r_miss_low": float(r_misses),
                "r_pass_low": float(r_passes),
                "time": t1-t0
            }
            results.append(res_dict)
            
    def make_factory(seed: int):
        def factory(k: int):
            return so.HGBRatio(seed=seed * 1000 + k)
        return factory

    for miss_handling in ["carry", "eff"]:
        for seed in [1, 2]:
            t0 = time.perf_counter()
            k_records = {}
            def on_iteration(rec):
                k = rec["iteration"]
                push = rec["push"]
                rec_score = scm.score_push(endpoint, push, run_ibu.SCOREABLE, run_ibu.INFORMATIONAL)
                top_bin_res = rec_score["aggregate"]["signed_residual_per_bin"][-1]
                k_records[k] = {
                    "aggregate": rec_score["aggregate"]["recovery"],
                    "low": rec_score["regions"]["low_acceptance"]["recovery"],
                    "moderate": rec_score["regions"]["moderate"]["recovery"],
                    "good": rec_score["regions"]["good"]["recovery"],
                    "top_bin_res": top_bin_res
                }
                
            run_scalar_omnifold_patched(
                X_reco_mc=X_reco_mc, X_reco_data=X_reco_data, X_gen_mc=X_gen_mc,
                pass_reco_mc=s1b, pass_gen_mc=pgb, w_truth_mc=pop["b_w_truth"],
                w_reco_mc=pop["b_w_reco"], w_data=w_data,
                make_step1=make_factory(seed), make_step2=make_factory(seed + 500),
                iterations=50, seed=seed, warm_start=False, callback=on_iteration, miss_handling=miss_handling)
            
            t1 = time.perf_counter()
            for k, scores in k_records.items():
                results.append({
                    "method": "OmniFold",
                    "miss_handling": miss_handling,
                    "seed": seed,
                    "k_or_lambda": k,
                    "aggregate": scores["aggregate"],
                    "low": scores["low"],
                    "moderate": scores["moderate"],
                    "good": scores["good"],
                    "top_bin_res": scores["top_bin_res"],
                    "time": t1-t0 if k==50 else 0
                })
                
    import hashlib, subprocess
    commit = subprocess.run(["git", "-C", str(Path(__file__).parent), "rev-parse", "HEAD"],
                            capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", str(Path(__file__).parent), "status", "--porcelain", "--", "."],
                           capture_output=True, text=True).stdout.strip()
    payload = {"schema": "phase-f-aussie-ablation/2",
               "producer": "phase_f/benchmark_ablation.py",
               "code_commit": commit, "code_dirty": bool(dirty),
               "populations_sha256": hashlib.sha256(Path(pop_file).read_bytes()).hexdigest(),
               "runs": results}
    out_dir = Path("results")
    out_dir.mkdir(exist_ok=True)
    with open(out_dir / "aussie_ablation.json", "w") as f:
        json.dump(payload, f, indent=2)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Phase F miss-handling ablation (scalar, DEV halves).")
    ap.add_argument("--populations", required=True, help="B1 populations.npz of the DEV halves")
    run_all(ap.parse_args().populations)
