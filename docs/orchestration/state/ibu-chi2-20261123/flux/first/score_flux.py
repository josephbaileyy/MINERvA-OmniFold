import json, csv, numpy as np, sys
D = sys.argv[1]
d = json.load(open(D + "/flux_dump.json"))
w = np.array(d["w"]); ctl = {"C-W": bool(len(w) == 100 and np.all(np.isfinite(w)) and np.all(w >= 0) and w.sum() > 0)}
V = np.array([[float(x) for x in r] for r in list(csv.reader(open(D + "/MINERvA_Flux_pdg14_500MeVBins.csv")))[1:]])
vlo, vhi, vf = V[:, 0], V[:, 1], V[:, 2]; nb = len(vf)
T = np.array([[float(x) for x in r] for r in list(csv.reader(open(D + "/MINERvA_Flux_covariance_pdg14_500MeVBins.csv")))[1:] if r])
M = np.zeros((nb + 2, nb + 2)); M[T[:, 0].astype(int), T[:, 1].astype(int)] = T[:, 2]; Cv = M[1:nb + 1, 1:nb + 1]
ours_e = np.array(d["1M"]["edges"])
common = np.unique(np.round(np.concatenate([np.arange(0, 20.001, 0.5), ours_e[ours_e >= 20]]), 6))
def onto(edges, y):            # y = integrated content per source bin; sum source bins inside each common bin
    out = np.zeros(len(common) - 1)
    for k, (a, b) in enumerate(zip(common[:-1], common[1:])):
        m = (edges[:-1] >= a - 1e-6) & (edges[1:] <= b + 1e-6); out[k] = y[m].sum()
    return out
vint = onto(np.append(vlo, vhi[-1]), vf * (vhi - vlo))
regs = {"LOW": (2, 6), "MID": (6, 11), "HIGH": (11, 20), "VHIGH": (20, 50)}
R = lambda y, a, b: y[(common[:-1] >= a - 1e-6) & (common[1:] <= b + 1e-6)].sum()
def vsig(a, b):
    g = ((vlo >= a - 1e-6) & (vhi <= b + 1e-6)) * (vhi - vlo); return float(np.sqrt(g @ Cv @ g))
out = {"controls": ctl, "valencia_cov_note": "diag sqrt / flux per bin, bins 1,10,40: " + ", ".join(
    f"{np.sqrt(Cv[k, k]) / vf[k]:.3g}" for k in (1, 10, 40))}
for per in ("1D", "1M", "1N"):
    x = d[per]; e = np.array(x["edges"]); wid = np.diff(e)
    cv = np.array(x["cv"]); U = np.array(x["univ"][:100]); con = (w[:, None] * U).sum(0) / w.sum()
    rr = {}
    for mode, f in (("density", wid), ("content", np.ones_like(wid))):
        c_cv, c_con = onto(e, cv * f), onto(e, con * f)
        rr[mode + "_cv_over_val_0_100"] = float(c_cv.sum() / vint.sum())
    mode = "density" if 0.7 <= rr["density_cv_over_val_0_100"] <= 1.3 else "content"
    f = wid if mode == "density" else np.ones_like(wid)
    c_cv, c_con = onto(e, cv * f), onto(e, con * f)
    rr["unit_mode"] = mode; rr["C-UNIT"] = bool(0.7 <= rr[mode + "_cv_over_val_0_100"] <= 1.3)
    n = lambda y: y / R(y, 2, 20)
    reg = {}
    for k, (a, b) in regs.items():
        reg[k] = dict(rho_con=R(n(c_con), a, b) / R(n(vint), a, b), rho_cv=R(n(c_cv), a, b) / R(n(vint), a, b),
                      con_over_cv=R(c_con, a, b) / R(c_cv, a, b), val_cov_rel=vsig(a, b) / R(vint, a, b))
    rr["regions"] = reg
    rr["fine_rho_con_above20"] = [[float(a), float(b), float(n(c_con)[i] / n(vint)[i])] for i, (a, b) in enumerate(zip(common[:-1], common[1:])) if a >= 20 and b <= 60]
    vh = reg["VHIGH"]
    rr["reading_ignoring_sigma"] = "HIGH-LOW" if vh["rho_con"] <= 0.95 else "HIGH-HIGH" if vh["rho_con"] >= 1.05 else "SAME"
    out[per] = rr
print(json.dumps(out, indent=1))
