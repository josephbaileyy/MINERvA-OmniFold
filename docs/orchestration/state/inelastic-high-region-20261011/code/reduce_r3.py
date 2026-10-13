"""R3/R4: hierarchical decomposition of the corner and intermediate-W contrasts (PLAN.md §4, §5).

sigma(m, a, t) = sigma(m) P(t|m) P(a|m,t), with m = (p_T, p_par), t = (q3, W), a = E_avail. Substituting the
data's factors into a prediction one at a time splits ln R_X into steps: rate, muon shape, transfer given
muon (inclusive response), E_avail given transfer (final-state partition). Two orders are reported.

R4 applies the same decomposition with the data replaced by the estimator-R unfolds (delta = 0, -4%, +4%
recoil; numerical jitters; frozen central), so each step's sensitivity to the response and estimator is
measured on identical predictions.

Usage: python3 -I reduce_r3.py <input_dir> <out_json>
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

N_REP = 200
SEED = 20261011


def sm(x):
    return x.sum(axis=(2, 3, 4))


def smt(x):
    return x.sum(axis=2)


def cond_a(x):
    """P(a | m, t), falling back to P(a | t) and then P(a) where the (m, t) cell is empty."""
    den = smt(x)[:, :, None, :, :]
    pa_t = x.sum(axis=(0, 1))
    den_t = pa_t.sum(axis=0, keepdims=True)
    pa = x.sum(axis=(0, 1, 3, 4))
    pa = pa / pa.sum()
    fb_t = np.where(den_t > 0, pa_t / np.where(den_t > 0, den_t, 1), pa[:, None, None])
    out = np.where(den > 0, x / np.where(den > 0, den, 1), fb_t[None, None])
    return out, (den[:, :, 0] == 0)


def cond_t(x):
    den = sm(x)[:, :, None, None]
    pt = smt(x).sum(axis=(0, 1))
    pt = pt / pt.sum()
    out = np.where(den > 0, smt(x) / np.where(den > 0, den, 1), pt[None, None])
    return out, (den[:, :, 0, 0] == 0)


def decompose(D, P, masks):
    """Return per-region step log-ratios in both orders, plus fallback diagnostics."""
    k = D.sum() / P.sum()
    pa, empty_mt = cond_a(P)
    pt, empty_m = cond_t(P)
    da, d_empty_mt = cond_a(D)
    X = {
        "inclusive_first": [P, P * k,
                            sm(D)[:, :, None, None, None] * pt[:, :, None, :, :] * pa,
                            smt(D)[:, :, None, :, :] * pa,
                            D],
        "partition_first": [P, P * k,
                            (smt(P) * k)[:, :, None, :, :] * da,
                            sm(D)[:, :, None, None, None] * pt[:, :, None, :, :] * da,
                            D],
    }
    labels = {"inclusive_first": ["rate", "muon_shape", "transfer_given_muon", "partition_given_transfer"],
              "partition_first": ["rate", "partition_given_transfer", "muon_shape", "transfer_given_muon"]}
    out = {}
    for order, seq in X.items():
        reg = {}
        for name, m5 in masks.items():
            s = [float(x[m5].sum()) for x in seq]
            if min(s) <= 0:
                reg[name] = None
                continue
            steps = {lab: float(np.log(s[i + 1] / s[i])) for i, lab in enumerate(labels[order])}
            reg[name] = {"lnR": float(np.log(s[-1] / s[0])), "steps": steps,
                         "ln_rho": float(np.log(s[-1] / s[0]) - steps["rate"])}
        out[order] = reg
    smtD = smt(D)
    out["fallback"] = {
        "data_fraction_in_pred_empty_mt": float(smtD[empty_mt].sum() / D.sum()),
        "data_fraction_in_pred_empty_m": float(sm(D)[empty_m].sum() / D.sum()),
        "pred_fraction_in_data_empty_mt": float(smt(P)[d_empty_mt].sum() / P.sum()),
    }
    return out


def summarize_reps(reps, nominal):
    """Standard deviation over MC replicas of every step, same nesting as ``nominal``."""
    out = {}
    for order in ("inclusive_first", "partition_first"):
        out[order] = {}
        for reg, v in nominal[order].items():
            if v is None:
                continue
            out[order][reg] = {"lnR_sd": float(np.std([r[order][reg]["lnR"] for r in reps], ddof=1)),
                               "ln_rho_sd": float(np.std([r[order][reg]["ln_rho"] for r in reps], ddof=1)),
                               "steps_sd": {s: float(np.std([r[order][reg]["steps"][s] for r in reps], ddof=1))
                                            for s in v["steps"]}}
    return out


def main(indir, out):
    names = ["xsec_5d_MEFHC_5iter_lgbm.root"] + list(C.PREDICTIONS.values())
    rnames = ["w2b/w2b_rrzero_b-_j-.npz", "w2b/w2b_rr0_b-_j-.npz", "w2b/w2b_rr1_b-_j-.npz",
              "s5pdata/data_b-_j-.npz", "s5pdata/data_b-_j1.npz", "s5pdata/data_b-_j2.npz", "s5pdata/data_b-_j3.npz"]
    digests = C.verify(indir, names + rnames)
    preds, var = {}, {}
    for kname, fn in C.PREDICTIONS.items():
        preds[kname], var[kname], _, E = C.load_pred(indir, fn)
    dV = C.volume(E)
    D = C.load_data_production(indir) * dV
    corner, mid, overflow = C.region_masks(E)
    S20 = C.enu_upper_bound(E) < 20.0
    masks = {"C": C.broadcast_ew(corner), "M": C.broadcast_ew(mid),
             "C_no_overflow": C.broadcast_ew(corner & ~overflow), "C_overflow": C.broadcast_ew(corner & overflow)}
    rng = np.random.default_rng(SEED)

    res = {"production": {}, "production_S20": {}}
    for kname, P in preds.items():
        nom = decompose(D, P, masks)
        reps = []
        sd = np.sqrt(var[kname])
        for _ in range(N_REP):
            Pr = np.clip(P + rng.standard_normal(P.shape) * sd, 0, None)
            reps.append(decompose(D, Pr, masks))
        nom["mc_sd"] = summarize_reps(reps, nom)
        res["production"][kname] = nom
        res["production_S20"][kname] = decompose(D * S20, P * S20, masks)
        c = nom["inclusive_first"]["C"]
        print(f"{kname:10s} C ln_rho={c['ln_rho']:+.4f} steps={ {s: round(v, 4) for s, v in c['steps'].items()} } "
              f"sd={nom['mc_sd']['inclusive_first']['C']['ln_rho_sd']:.4f}")

    # ---- R4: estimator-R data variants ---------------------------------------------------------
    R = {}
    for n in rnames:
        R[n], _ = C.load_R(indir, n, dV)
    res["estimator_R"] = {}
    for kname, P in preds.items():
        v = {}
        for n in rnames:
            v[n] = decompose(R[n], P, masks)
        res["estimator_R"][kname] = v
        z, m4, p4 = (v[n]["inclusive_first"]["C"] for n in rnames[:3])
        print(f"  R {kname:10s} C ln_rho d0={z['ln_rho']:+.4f} -4%={m4['ln_rho']:+.4f} +4%={p4['ln_rho']:+.4f}")
    # direct totals for R variants
    res["estimator_R_totals"] = {n: {"total": float(R[n].sum()),
                                     "corner": float(R[n][masks["C"]].sum()),
                                     "mid": float(R[n][masks["M"]].sum())} for n in rnames}
    res["production_totals"] = {"total": float(D.sum()), "corner": float(D[masks["C"]].sum()),
                                "mid": float(D[masks["M"]].sum())}
    C.write_json(out, {"schema": "inelastic-r3/1", "digests": digests, "n_rep": N_REP, "seed": SEED,
                       "results": res})


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
