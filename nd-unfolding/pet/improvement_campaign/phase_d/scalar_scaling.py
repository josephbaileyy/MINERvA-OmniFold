import sys
import os
from pathlib import Path
import time
import numpy as np
import torch
import json
import hashlib
from joblib import Parallel, delayed

# Fix paths
d_path = Path(__file__).resolve().parent
b1_path = d_path.parent / "phase_b" / "scalar"
f_path = d_path.parent / "phase_f"
sys.path.insert(0, str(b1_path))
sys.path.insert(0, str(f_path))

import run_ibu
import scalar_common as scm
import scalar_omnifold as so
import features
import binned_unfolding as bu
from aussie_scalar import train_classifier, train_unfolder

DATA_PATH = "/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/b160e1e8-d9e0-44fe-ab81-24d89902eec7/scratchpad/pet/f1_data/populations.npz"

POP_GLOBAL = None

def get_subset(pop, a_size=None, b_size=None, seed=0):
    rng = np.random.default_rng(seed)
    new_pop = dict(pop)
    
    idx_a = np.arange(len(pop['a_rows']))
    if a_size is not None and a_size < len(idx_a):
        idx_a = rng.permutation(len(idx_a))[:a_size]
        
    idx_b = np.arange(len(pop['b_rows']))
    if b_size is not None and b_size < len(idx_b):
        idx_b = rng.permutation(len(idx_b))[:b_size]
        
    for k, v in pop.items():
        if isinstance(v, np.ndarray) and len(v.shape) > 0:
            if k.startswith('a_') or k in ['hist_push_ours127', 'hist_push_theirs127', 'ep_prior_selector']:
                if len(v) == len(pop['a_rows']) and k.startswith('a_'):
                    new_pop[k] = v[idx_a]
                elif len(v) == len(pop['b_rows']) and (k.startswith('b_') or k in ['hist_push_ours127', 'hist_push_theirs127', 'ep_prior_selector']):
                    new_pop[k] = v[idx_b]
            elif k.startswith('b_'):
                if len(v) == len(pop['b_rows']):
                    new_pop[k] = v[idx_b]
                    
    # Handle ep_..._a
    map_a_to_ep = np.full(len(pop['a_rows']), -1)
    a_pt = pop['a_pass_truth'].astype(bool)
    map_a_to_ep[a_pt] = np.arange(a_pt.sum())
    idx_a_truth = idx_a[pop['a_pass_truth'][idx_a].astype(bool)]
    ep_idx_a = map_a_to_ep[idx_a_truth]
    
    for k in ['ep_eavail_a', 'ep_w_truth_a', 'ep_tilt_a', 'ep_region_a']:
        if k in pop:
            new_pop[k] = pop[k][ep_idx_a]
            
    # Handle ep_..._b
    map_b_to_ep = np.full(len(pop['b_rows']), -1)
    b_pt = pop['b_pass_truth'].astype(bool)
    map_b_to_ep[b_pt] = np.arange(b_pt.sum())
    idx_b_truth = idx_b[pop['b_pass_truth'][idx_b].astype(bool)]
    ep_idx_b = map_b_to_ep[idx_b_truth]
    
    for k in ['ep_eavail_b', 'ep_w_truth_b', 'ep_region_b']:
        if k in pop:
            new_pop[k] = pop[k][ep_idx_b]
            
    return new_pop


def _split(n: int, rng):
    idx = rng.permutation(n)
    n_tr = int(0.8 * n)
    return idx[:n_tr], idx[n_tr:]

def run_scalar_omnifold_patched(*, X_reco_mc, X_reco_data, X_gen_mc,
                        pass_reco_mc, pass_gen_mc,
                        w_truth_mc, w_reco_mc, w_data,
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
    
    if miss_handling == "efficiency_corrected" or miss_handling == "eff":
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
        
        if hasattr(m1, "model") and type(m1.model).__name__ == "HistGradientBoostingClassifier":
            m1.model.fit(X1[tr1], y1[tr1], sample_weight=w1[tr1])
            info1 = {"model": "hgb", "n_iter": int(m1.model.n_iter_)}
        else:
            info1 = m1.fit(X1[tr1], y1[tr1], w1[tr1], X1[va1], y1[va1], w1[va1])
            
        ratio1, sat1 = so._capped_ratio(m1.logit(np.asarray(X_reco_mc)[s1]))
        info1.update({"seconds": time.perf_counter() - t0, "saturated": sat1})
        prev_push = push
        pull = push.copy()
        pull[s1] = push[s1] * ratio1

        m2 = model2 if warm_start else make_step2(k)
        if miss_handling == "efficiency_corrected" or miss_handling == "eff":
            w2 = np.concatenate([w_t[pg][s1_in_pg], (w_t * pull)[pg][s1_in_pg]])
        else:
            w2 = np.concatenate([w_t[pg], (w_t * pull)[pg]])
            
        t0 = time.perf_counter()
        if hasattr(m2, "model") and type(m2.model).__name__ == "HistGradientBoostingClassifier":
            m2.model.fit(X2[tr2], y2[tr2], sample_weight=w2[tr2])
            info2 = {"model": "hgb", "n_iter": int(m2.model.n_iter_)}
        else:
            info2 = m2.fit(X2[tr2], y2[tr2], w2[tr2], X2[va2], y2[va2], w2[va2])
            
        ratio2, sat2 = so._capped_ratio(m2.logit(Xg))
        info2.update({"seconds": time.perf_counter() - t0, "saturated": sat2})
        push = np.ones_like(push)
        push[pg] = ratio2
        if callback is not None:
            callback({"iteration": k, "pull": pull, "push": push, "prev_push": prev_push})
    return {"pull": pull, "push": push}

def transform(x):
    return np.sign(x) * np.log1p(np.abs(x))

def tilt_spec_of_full_population():
    """The tilt function as injected, from the FULL half A, so every subset is scored against it."""
    mods = scm.historical_modules()
    cp, fd = mods["cp"], mods["fd"]
    pop = scm.load_populations(DATA_PATH)
    pga = pop["a_pass_truth"].astype(bool)
    _, spec = cp.clipped_exponential_tilt(pop["a_truth"][:, 2][pga],
                                          amplitude=float(fd.ENDPOINT["amplitude"]),
                                          clip_z=float(fd.ENDPOINT["clip"]))
    return {k: float(v) for k, v in spec.items() if isinstance(v, (int, float))}


def evaluate_tilt(x, spec):
    z = np.clip((x - spec["pt_p50"]) / spec["pt_iqr"], -spec["clip_z"], spec["clip_z"])
    return np.exp(spec["amplitude"] * z) / spec["pre_normalization_mean"]


def oracle_anchor(pop, endpoint, spec):
    """What the EXACT injected tilt scores on this evaluation subset: its finite-sample ceiling."""
    pgb = pop["b_pass_truth"].astype(bool)
    push = np.ones(pgb.size)
    push[pgb] = evaluate_tilt(pop["b_truth"][:, 2][pgb], spec)
    return scm.score_push(endpoint, push, run_ibu.SCOREABLE, run_ibu.INFORMATIONAL)


def worker(task):
    global POP_GLOBAL
    if POP_GLOBAL is None:
        POP_GLOBAL = scm.load_populations(DATA_PATH)
    pop_subset = get_subset(POP_GLOBAL, a_size=task["a_size"], b_size=task["b_size"], seed=task["subset_seed"])
    
    if task["method"] == "AUSSIE":
        from aussie_scalar import _capped_ratio as aussie_capped_ratio
        t0 = time.perf_counter()
        pop = pop_subset
        endpoint = scm.endpoint_from_populations(pop)
        pga = pop["a_pass_truth"].astype(bool)
        s1a = pga & pop["a_pass_reco"].astype(bool)
        pgb = pop["b_pass_truth"].astype(bool)
        s1b = pgb & pop["b_pass_reco"].astype(bool)
        w_data = (pop["a_w_reco"] * pop["a_tilt"])[s1a]
        
        X_reco_mc, _ = features.reco_matrix(pop, "b", "muon_eavail", used=s1b)
        X_reco_mc_pass = X_reco_mc[s1b]
        X_reco_data, _ = features.reco_matrix(pop, "a", "muon_eavail", used=s1a)
        X_reco_data = X_reco_data[s1a]
        X_gen_mc, _ = features.truth_matrix(pop, "b", "truth4", used=pgb)
        X_gen_mc_pass = X_gen_mc[s1b]
        X_gen_mc_miss = X_gen_mc[pgb & ~s1b]
        
        w_truth_mc = pop["b_w_truth"][pgb]
        w_reco_mc = pop["b_w_reco"]
        
        c = bu.ENGINE_NORMALIZATION / w_reco_mc[s1b].sum()
        w_truth_mc = w_truth_mc * c
        w_reco_mc = w_reco_mc * c
        w_data = w_data * (bu.ENGINE_NORMALIZATION / w_data.sum())
        
        w_reco_mc_pass = w_reco_mc[s1b]
        w_truth_mc_pass = w_truth_mc[s1b[pgb]]
        w_truth_mc_miss = w_truth_mc[~s1b[pgb]]
        
        classifier, c_mean, c_std = train_classifier(X_reco_mc_pass, X_reco_data, w_reco_mc_pass, w_data, epochs=task["epochs"], lr=1e-3, seed=task["seed"])
        unfolder, z_mean, z_std = train_unfolder(classifier, c_mean, c_std, X_gen_mc_pass, X_reco_mc_pass, w_truth_mc_pass, X_gen_mc_miss, w_truth_mc_miss, lambda_miss=task["l_miss"], epochs=task["epochs"], lr=1e-3, seed=task["seed"])
        unfolder.eval()
        with torch.no_grad():
            Z_all_t = transform(X_gen_mc)
            Z_all_z = (Z_all_t - z_mean) / z_std
            Z_tensor = torch.tensor(Z_all_z, dtype=torch.float32)
            lw_z = unfolder(Z_tensor).numpy()
            
        ratio2 = aussie_capped_ratio(lw_z)
        push = ratio2
        
        rec_score = scm.score_push(endpoint, push, run_ibu.SCOREABLE, run_ibu.INFORMATIONAL)
        t1 = time.perf_counter()
        
        res = {
            "run_id": task["run_id"], "method": "AUSSIE", "miss_handling": f"lambda={task['l_miss']}",
            "k_or_lambda": task['l_miss'], "epochs": task["epochs"],
            "aggregate": rec_score["aggregate"]["recovery"],
            "low": rec_score["regions"]["low_acceptance"]["recovery"],
            "moderate": rec_score["regions"]["moderate"]["recovery"],
            "good": rec_score["regions"]["good"]["recovery"],
            "time": t1-t0
        }
        anc = oracle_anchor(pop, endpoint, task["tilt_spec"])
        res["anchor_aggregate"] = anc["aggregate"]["recovery"]
        res["anchor_low"] = anc["regions"]["low_acceptance"]["recovery"]
    else:
        t0 = time.perf_counter()
        pop = pop_subset
        endpoint = scm.endpoint_from_populations(pop)
        pga = pop["a_pass_truth"].astype(bool)
        s1a = pga & pop["a_pass_reco"].astype(bool)
        pgb = pop["b_pass_truth"].astype(bool)
        s1b = pgb & pop["b_pass_reco"].astype(bool)
        w_data = (pop["a_w_reco"] * pop["a_tilt"])[s1a]
        
        X_reco_mc, _ = features.reco_matrix(pop, "b", "muon_eavail", used=s1b)
        X_reco_data, _ = features.reco_matrix(pop, "a", "muon_eavail", used=s1a)
        X_reco_data = X_reco_data[s1a]
        X_gen_mc, _ = features.truth_matrix(pop, "b", "truth4", used=pgb)
        
        def make_factory(seed_base):
            def factory(k: int):
                return so.HGBRatio(seed=seed_base * 1000 + k, max_iter=task["max_iter"], early_stopping=task["early_stopping"])
            return factory

        final_k_score = None
        def on_iteration(rec):
            nonlocal final_k_score
            if rec["iteration"] == task["k_target"]:
                push = rec["push"]
                final_k_score = scm.score_push(endpoint, push, run_ibu.SCOREABLE, run_ibu.INFORMATIONAL)

        run_scalar_omnifold_patched(
            X_reco_mc=X_reco_mc, X_reco_data=X_reco_data, X_gen_mc=X_gen_mc,
            pass_reco_mc=s1b, pass_gen_mc=pgb, w_truth_mc=pop["b_w_truth"],
            w_reco_mc=pop["b_w_reco"], w_data=w_data,
            make_step1=make_factory(task["seed"]), make_step2=make_factory(task["seed"] + 500),
            iterations=task["k_target"], seed=task["seed"], warm_start=False, callback=on_iteration, miss_handling=task["miss_handling"])
        
        t1 = time.perf_counter()
        res = {
            "run_id": task["run_id"], "method": "OmniFold", "miss_handling": task["miss_handling"],
            "k_or_lambda": task["k_target"], "max_iter": task["max_iter"], "early_stopping": task["early_stopping"],
            "aggregate": final_k_score["aggregate"]["recovery"],
            "low": final_k_score["regions"]["low_acceptance"]["recovery"],
            "moderate": final_k_score["regions"]["moderate"]["recovery"],
            "good": final_k_score["regions"]["good"]["recovery"],
            "time": t1-t0
        }
        anc = oracle_anchor(pop, endpoint, task["tilt_spec"])
        res["anchor_aggregate"] = anc["aggregate"]["recovery"]
        res["anchor_low"] = anc["regions"]["low_acceptance"]["recovery"]
        
    res.update({
        "exp": task["exp"],
        "prior_size": task["b_size"],
        "data_size": task["a_size"],
        "draw_seed": task["subset_seed"]
    })
    print(f"Finished task {res['run_id']} (exp={res['exp']} method={res['method']}) in {res['time']:.2f}s, aggregate={res['aggregate']:.4f}")
    return res

def main():
    data_sha = hashlib.sha256(open(DATA_PATH, 'rb').read()).hexdigest()
    
    spec = tilt_spec_of_full_population()
    tasks = []
    sizes = [75000, 150000, 300000, 600143]
    draws = [1, 2, 3] # 3 draws!
    
    run_id = 0
    # 1. Vary Prior Size
    for size in sizes:
        for draw in draws:
            base = {"exp": "vary_prior", "a_size": 600143, "b_size": size, "subset_seed": draw*100, "seed": draw}
            tasks.append({**base, "run_id": run_id, "method": "OmniFold", "miss_handling": "carry", "k_target": 3, "max_iter": 400, "early_stopping": True}); run_id += 1
            tasks.append({**base, "run_id": run_id, "method": "OmniFold", "miss_handling": "carry", "k_target": 20, "max_iter": 400, "early_stopping": True}); run_id += 1
            tasks.append({**base, "run_id": run_id, "method": "OmniFold", "miss_handling": "efficiency_corrected", "k_target": 3, "max_iter": 400, "early_stopping": True}); run_id += 1
            tasks.append({**base, "run_id": run_id, "method": "OmniFold", "miss_handling": "efficiency_corrected", "k_target": 20, "max_iter": 400, "early_stopping": True}); run_id += 1
            tasks.append({**base, "run_id": run_id, "method": "AUSSIE", "l_miss": 0, "epochs": 25}); run_id += 1
            tasks.append({**base, "run_id": run_id, "method": "AUSSIE", "l_miss": 1000, "epochs": 25}); run_id += 1

    # 2. Vary Data Size
    for size in sizes:
        if size == 600143: continue
        for draw in draws:
            base = {"exp": "vary_data", "a_size": size, "b_size": 600143, "subset_seed": draw*100, "seed": draw}
            tasks.append({**base, "run_id": run_id, "method": "OmniFold", "miss_handling": "carry", "k_target": 3, "max_iter": 400, "early_stopping": True}); run_id += 1
            tasks.append({**base, "run_id": run_id, "method": "OmniFold", "miss_handling": "carry", "k_target": 20, "max_iter": 400, "early_stopping": True}); run_id += 1
            tasks.append({**base, "run_id": run_id, "method": "OmniFold", "miss_handling": "efficiency_corrected", "k_target": 3, "max_iter": 400, "early_stopping": True}); run_id += 1
            tasks.append({**base, "run_id": run_id, "method": "OmniFold", "miss_handling": "efficiency_corrected", "k_target": 20, "max_iter": 400, "early_stopping": True}); run_id += 1
            tasks.append({**base, "run_id": run_id, "method": "AUSSIE", "l_miss": 0, "epochs": 25}); run_id += 1
            tasks.append({**base, "run_id": run_id, "method": "AUSSIE", "l_miss": 1000, "epochs": 25}); run_id += 1

    # 3. Vary Effort
    efforts_gbdt = [10, 25, 50, 100]
    efforts_aussie = [10, 25, 50, 100]
    for size in [75000, 600143]:
        for draw in draws: # 3 draws for effort ablation too!
            base = {"exp": "vary_effort", "a_size": size, "b_size": size, "subset_seed": draw*100, "seed": draw}
            for e in efforts_gbdt:
                tasks.append({**base, "run_id": run_id, "method": "OmniFold", "miss_handling": "carry", "k_target": 20, "max_iter": e, "early_stopping": False}); run_id += 1
                tasks.append({**base, "run_id": run_id, "method": "OmniFold", "miss_handling": "efficiency_corrected", "k_target": 20, "max_iter": e, "early_stopping": False}); run_id += 1
            for e in efforts_aussie:
                tasks.append({**base, "run_id": run_id, "method": "AUSSIE", "l_miss": 0, "epochs": e}); run_id += 1
                tasks.append({**base, "run_id": run_id, "method": "AUSSIE", "l_miss": 1000, "epochs": e}); run_id += 1

    for task in tasks:
        task["tilt_spec"] = spec
    print(f"Total tasks: {len(tasks)}")
    
    workers = min(5, os.cpu_count() or 1)
    results = Parallel(n_jobs=workers, backend='loky')(delayed(worker)(t) for t in tasks)
            
    out_dir = Path("results")
    out_dir.mkdir(exist_ok=True)
    with open(out_dir / "scalar_scaling.json", "w") as f:
        json.dump({"data_sha256": data_sha, "runs": results}, f, indent=2)

if __name__ == "__main__":
    main()
