"""Independent reproduction of the W1 projected tests (own projection + variant code; stats from s5p_inference)."""
import hashlib, json, sys
import numpy as np
sys.path.insert(0, "/Users/josephbailey/local-research/MINERvA-OmniFold-publication-20261005/nd-unfolding")
import s5p_inference as si

IN = "/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/d19e9212-9147-403d-b61c-1ebf054fb7d1/scratchpad/w1/"
OUT = "/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/d19e9212-9147-403d-b61c-1ebf054fb7d1/scratchpad/w1-repro/"
READINGS = {"a": "reading_a_union.npz", "b": "reading_b_frozenS.npz"}
AXES = ("pt", "pz", "eavail", "q3", "W")
PROJ = {"P_ptpl": ("pt", "pz"), "P_eW": ("eavail", "W")}


def proj_matrix(cells, dom, keep_axes):
    """Rows: the 3x3 grid of keep_axes (C order), restricted to rows hit by an in-domain J cell; columns: in-domain J cells."""
    coords = np.array([np.unravel_index(int(c), (3,) * 5) for c in cells])  # (109, 5)
    ia, ib = (AXES.index(a) for a in keep_axes)
    target = coords[dom, ia] * 3 + coords[dom, ib]
    P = np.zeros((9, int(dom.sum())))
    P[target, np.arange(target.size)] = 1.0
    rows = P.sum(1) > 0
    return P[rows], np.flatnonzero(rows)


def run_one(z, man, key, P, dom):
    F, seeds, mu, var = (np.asarray(z[f"{n}__{key}"], float) for n in ("F", "seeds", "mu", "var"))
    seeds = np.asarray(z[f"seeds__{key}"]).astype(np.int64)
    V = np.asarray(z["V"], float)
    f_data = np.asarray(z["f_data"], float)
    spec = man["nulls"][key]
    seed0 = int(spec["surrogate_seed0"])
    Vdd = V[np.ix_(dom, dom)]
    Wp = P @ Vdd @ P.T + np.diag(P @ var[dom])
    Wpinv = np.linalg.inv(Wp)
    tt_o = si.stat_total(P @ f_data[dom], P @ mu[dom], Wpinv)
    ts_o = si.stat_shape(P @ f_data[dom], P @ mu[dom], Wp)
    # variants
    variants = []
    S = np.asarray(z[f"S__{key}"], float) if f"S__{key}" in z.files else None
    coefs = man["shift_coefficients"]
    if S is not None:
        variants += [(str(float(c)), float(c) * S) for c in coefs]
    else:
        variants += [("0.0", np.zeros(mu.size))]
    m1 = spec.get("m1")
    if f"d1__{key}" in z.files and m1 is not None and "none" not in m1:
        d1 = np.asarray(z[f"d1__{key}"], float)
        kap = m1["kappa"]
        variants += [(f"m1+{kap}", kap * d1), (f"m1-{kap}", -kap * d1)]
    # per-draw MC error of the prediction, full 109 vector
    B = F.shape[0]
    r_mu = np.empty_like(F)
    for i in range(B):
        eps = np.random.default_rng([seed0, int(seeds[i]), 0x4A02]).normal(size=mu.size) * np.sqrt(var)
        r_mu[i] = mu + eps
    Pr_mu = (P @ r_mu[:, dom].T).T
    out = {"cells": int(P.shape[0]), "B": B, "T_total_obs": tt_o, "T_shape_obs": ts_o, "variants": {}}
    for name, v in variants:
        Fv = F + v
        Pf = (P @ Fv[:, dom].T).T
        tt = np.array([si.stat_total(Pf[i], Pr_mu[i], Wpinv) for i in range(B)])
        ts = np.array([si.stat_shape(Pf[i], Pr_mu[i], Wp) for i in range(B)])
        vt, vs = si.mc_pvalue(tt_o, tt), si.mc_pvalue(ts_o, ts)
        out["variants"][name] = {"total": {"k": vt["k"], "B": vt["B"], "p": vt["p"]},
                                 "shape": {"k": vs["k"], "B": vs["B"], "p": vs["p"]}}
    for s in ("total", "shape"):
        nm, best = max(out["variants"].items(), key=lambda kv: kv[1][s]["p"])
        out[s] = dict(best[s], variant=nm)
    return out


def main():
    res = {}
    for rd, fn in READINGS.items():
        raw = open(IN + fn, "rb").read()
        man = json.load(open(IN + fn + ".manifest.json"))
        sha = hashlib.sha256(raw).hexdigest()
        assert sha == man["npz_sha256"], (fn, sha)
        z = np.load(IN + fn, allow_pickle=False)
        cells = np.asarray(z["supported_cells"]).astype(int)
        res[rd] = {"npz_sha256": sha, "tests": {}}
        for key in man["nulls"]:
            dom = np.asarray(z[f"dom__{key}"]).astype(bool)
            # consistency with the frozen domain rule
            pzi = np.asarray(z["pz_index"])
            want = (pzi <= 1) if man["nulls"][key]["domain"] == "pz_lt_6" else np.ones(cells.size, bool)
            assert np.array_equal(dom, want), key
            assert z[f"F__{key}"].shape[0] == man["nulls"][key]["B"], key
            res[rd]["tests"][key] = {"domain_cells": int(dom.sum())}
            for pn, ax in PROJ.items():
                P, rows = proj_matrix(cells, dom, ax)
                r = run_one(z, man, key, P, dom)
                r["rows"] = rows.tolist()
                res[rd]["tests"][key][pn] = r
                print(rd, key, pn, r["cells"], "total", r["total"], "shape", r["shape"], flush=True)
    json.dump(res, open(OUT + "repro-result.json", "w"), indent=1)


if __name__ == "__main__":
    main()
