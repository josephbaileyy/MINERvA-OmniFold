#!/usr/bin/env python3
"""Replay every p-value and decision of the s5p joint tests from the portable sufficient inputs.

Standalone: numpy and scipy only, no repository import. It restates the frozen rules of
``nd-unfolding/s5p_inference.py`` and ``s5p_joint.py`` (statistics, Monte Carlo p-value with its exact
Clopper-Pearson interval, the claim rule over declared variants, Holm with determinacy, the kappa = 3 report
variants, and power under the claim rule). With ``--compare joint-evaluate.json`` it checks every recomputed
field against the frozen evaluator's output and exits non-zero on any difference.

This is a second implementation by design: it is what an outside reader runs. Its agreement with the frozen
output is the release's replay check; ``test_replay_inference.py`` checks it against the frozen functions on
synthetic inputs.

MEASURES: nothing new. CANNOT AUTHORIZE: any decision beyond the frozen evaluator's.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats


def stat_total(f, mu, Winv) -> float:
    r = np.asarray(f, float) - np.asarray(mu, float)
    return float(r @ Winv @ r)


def stat_shape(f, mu, W, drop: int = -1) -> float:
    f = np.asarray(f, float)
    s = f.sum()
    p = f / s
    J = (np.eye(f.size) - np.outer(p, np.ones(f.size))) / s
    Vs = J @ W @ J.T
    q = np.asarray(mu, float) / np.asarray(mu, float).sum()
    keep = np.ones(p.size, bool)
    keep[drop] = False
    r = (p - q)[keep]
    return float(r @ np.linalg.solve(Vs[np.ix_(keep, keep)], r))


def statistics(F, mu, var, V, dom, seed0: int, draw: bool = True, seeds=None):
    W = V[np.ix_(dom, dom)] + np.diag(var[dom])
    Winv = np.linalg.inv(W)
    keys = seeds if seeds is not None else np.arange(len(F))
    tt, ts = [], []
    for i, f in enumerate(F):
        eps = (np.random.default_rng([int(seed0), int(keys[i]), 0x4A02]).normal(size=mu.size) * np.sqrt(var)
               if draw else 0.0)
        r_mu = mu + eps
        tt.append(stat_total(f[dom], r_mu[dom], Winv))
        ts.append(stat_shape(f[dom], r_mu[dom], W))
    return np.array(tt), np.array(ts)


def cp_interval(k: int, B: int, level: float = 0.95):
    a = 1 - level
    lo = 0.0 if k == 0 else float(stats.beta.ppf(a / 2, k, B - k + 1))
    hi = 1.0 if k == B else float(stats.beta.ppf(1 - a / 2, k + 1, B - k))
    return lo, hi


def mc_pvalue(t_obs: float, t_null, level: float = 0.95) -> dict:
    t_null = np.asarray(t_null, float)
    B = t_null.size
    k = int(np.sum(t_null >= t_obs))
    lo, hi = cp_interval(k, B, level)
    return {"p": (k + 1) / (B + 1), "k": k, "B": B, "tail_interval": [lo, hi]}


def holm_determined(entries: dict, alpha: float = 0.05, level: float = 0.95) -> dict:
    order = sorted(entries, key=lambda k: entries[k]["p"])
    m = len(order)
    out, state = {}, None
    for i, key in enumerate(order):
        e = entries[key]
        th = alpha / (m - i)
        lo, hi = cp_interval(int(e["k"]), int(e["B"]), level)
        if state is None:
            if hi < th:
                decision = "rejected"
            elif lo > th:
                state = decision = "not rejected"
            else:
                state = decision = "undetermined"
        else:
            decision = state
        out[key] = {"p": e["p"], "k": int(e["k"]), "B": int(e["B"]), "threshold": th, "interval": [lo, hi],
                    "decision": decision}
    return out


def power_determined(t_alt, t_nulls, alpha: float, level: float = 0.95) -> dict:
    t_alt = np.asarray(t_alt, float)
    ks = []
    for tn in t_nulls:
        s = np.sort(np.asarray(tn, float))
        ks.append(s.size - np.searchsorted(s, t_alt, side="left"))
    k = np.max(np.array(ks), axis=0)
    B = np.asarray(t_nulls[0]).size
    rej = np.array([cp_interval(int(x), B, level)[1] < alpha for x in k])
    return {"power": float(rej.sum() / rej.size), "n": int(rej.size), "B": int(B)}


def replay(z, man: dict) -> dict:
    V, f_data = z["V"], z["f_data"]
    coefs = man["shift_coefficients"]
    alpha = man["alpha_family"]
    res, claims, robust, nulls_by_key = {"tests": {}}, {}, {}, {}
    for key, nm in man["nulls"].items():
        F, seeds = z[f"F__{key}"], z[f"seeds__{key}"]
        mu, var, dom = z[f"mu__{key}"], z[f"var__{key}"], z[f"dom__{key}"].astype(bool)
        S = z[f"S__{key}"] if f"S__{key}" in z.files else None
        tt_o, ts_o = statistics(f_data[None, :], mu, var, V, dom, 0, draw=False)
        variants = [(str(c), (c * S if S is not None else None)) for c in (coefs if S is not None else [0.0])]
        robust_v = []
        if nm["m1"] is not None:
            d1, ka, kr = z[f"d1__{key}"], nm["m1"]["kappa"], nm["m1"]["kappa_robust"]
            variants += [(f"m1+{ka}", ka * d1), (f"m1-{ka}", -ka * d1)]
            robust_v = [(f"m1+{kr}", kr * d1), (f"m1-{kr}", -kr * d1)]
        entry = {"T_total_obs": float(tt_o[0]), "T_shape_obs": float(ts_o[0]), "variants": {}, "robustness_variants": {}}
        nulls = []
        for name, sv in variants:
            tt_n, ts_n = statistics(F + (sv if sv is not None else 0.0), mu, var, V, dom, nm["surrogate_seed0"], seeds=seeds)
            nulls.append((tt_n, ts_n))
            entry["variants"][name] = {"total": mc_pvalue(tt_o[0], tt_n), "shape": mc_pvalue(ts_o[0], ts_n)}
        for name, sv in robust_v:
            tt_n, ts_n = statistics(F + sv, mu, var, V, dom, nm["surrogate_seed0"], seeds=seeds)
            entry["robustness_variants"][name] = {"total": mc_pvalue(tt_o[0], tt_n), "shape": mc_pvalue(ts_o[0], ts_n)}
        for s in ("total", "shape"):
            claim = max(entry["variants"].values(), key=lambda v: v[s]["p"])[s]
            entry[s] = claim
            rob = max([claim] + [r[s] for r in entry["robustness_variants"].values()], key=lambda v: v["p"])
            entry[s + "_robust"] = rob
            claims[f"{key}:{s}"] = {k: claim[k] for k in ("p", "k", "B")}
            robust[f"{key}:{s}"] = {k: rob[k] for k in ("p", "k", "B")}
        res["tests"][key] = entry
        nulls_by_key[key] = nulls
    res["decisions"] = holm_determined(claims, alpha)
    res["decisions_robust_kappa"] = holm_determined(robust, alpha)
    levels = [0.05, alpha / len(claims)]
    res["power"] = {}
    for key, pm in man.get("power", {}).items():
        if f"Fpow__{key}" not in z.files:
            continue
        nk = pm["null"]
        mu0, var0 = z[f"mu__{nk}"], z[f"var__{nk}"]
        dom = z[f"dom__{nk}"].astype(bool)
        tt_a, ts_a = statistics(z[f"Fpow__{key}"], mu0, var0, V, dom, pm["surrogate_seed0"], seeds=z[f"seedspow__{key}"])
        res["power"][key] = {s: {str(al): power_determined(t_alt, [x[i] for x in nulls_by_key[nk]], al) for al in levels}
                             for i, (s, t_alt) in enumerate((("total", tt_a), ("shape", ts_a)))}
    return res


def compare(res: dict, frozen: dict, rtol: float = 1e-12) -> list[str]:
    bad = []

    def close(a, b):
        return np.isclose(float(a), float(b), rtol=rtol, atol=0.0)

    for key, e in res["tests"].items():
        f = frozen["tests"][key]
        for fld in ("T_total_obs", "T_shape_obs"):
            if not close(e[fld], f[fld]):
                bad.append(f"{key}.{fld}: {e[fld]!r} != {f[fld]!r}")
        for grp in ("variants", "robustness_variants"):
            for vn, v in e[grp].items():
                for s in ("total", "shape"):
                    for fld in ("p", "k", "B"):
                        if not close(v[s][fld], f[grp][vn][s][fld]):
                            bad.append(f"{key}.{grp}.{vn}.{s}.{fld}: {v[s][fld]!r} != {f[grp][vn][s][fld]!r}")
        for s in ("total", "shape", "total_robust", "shape_robust"):
            for fld in ("p", "k", "B"):
                if not close(e[s][fld], f[s][fld]):
                    bad.append(f"{key}.{s}.{fld}: {e[s][fld]!r} != {f[s][fld]!r}")
    for grp in ("decisions", "decisions_robust_kappa"):
        for t, d in res[grp].items():
            fd = frozen[grp][t]
            if d["decision"] != fd["decision"] or not close(d["threshold"], fd["threshold"]):
                bad.append(f"{grp}.{t}: {d['decision']}@{d['threshold']} != {fd['decision']}@{fd['threshold']}")
    for key, pw in res["power"].items():
        fp = frozen["power"].get(key, {})
        for s, lv in pw.items():
            for al, v in lv.items():
                want = fp.get(s, {}).get(al, {}).get("claim_rule_determined", {}).get("power")
                if want is None or not close(v["power"], want):
                    bad.append(f"power.{key}.{s}.{al}: {v['power']!r} != {want!r}")
    return bad


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--npz", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, default=None, help="default: <npz>.manifest.json")
    ap.add_argument("--compare", type=Path, default=None, help="frozen joint-evaluate.json to check against")
    ap.add_argument("--out", type=Path, default=None)
    a = ap.parse_args(argv)
    man = json.loads((a.manifest or Path(str(a.npz) + ".manifest.json")).read_text())
    z = np.load(a.npz, allow_pickle=False)
    res = replay(z, man)
    table = {t: {"p": d["p"], "k": d["k"], "B": d["B"], "decision": d["decision"],
                 "robust_kappa3": res["decisions_robust_kappa"][t]["decision"]} for t, d in res["decisions"].items()}
    print(json.dumps(table, indent=1))
    if a.out:
        a.out.write_text(json.dumps(res, indent=1, default=float) + "\n")
    if a.compare:
        bad = compare(res, json.loads(a.compare.read_text()))
        print(f"COMPARE: {'AGREE' if not bad else 'DIFFER'} ({len(bad)} differences)")
        for b in bad[:50]:
            print("  " + b)
        return 0 if not bad else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
