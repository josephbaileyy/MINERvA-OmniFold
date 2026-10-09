"""Agent C audit checks from the RC4 release arrays (read-only).
J13: observed-p stability over the 20 jitters (frozen npz) vs joint-evaluate observed_jitter_p.
J28: with complete batches (union npz, seed offsets < 1200), does the frozen sequential rule stop
     MnvTune, GENIE CV, GENIE MEC, GiBUU at B = 1200 (and not at B = 1000), with k = 0 claim?
J02/J21/J04: shape counts.
Sequential rule restated from nd-unfolding/s5p_inference.py:89-111 and s5p_seqstop.py:67-70 (fec438db)."""
import json, sys
from pathlib import Path
import numpy as np
rc = Path(sys.argv[1]); sys.path.insert(0, str(rc / "code"))
sys.dont_write_bytecode = True
import replay_inference as rp

def seqdec(k, B, ths, look=0.995):
    lo, hi = rp.cp_interval(k, B, look)
    p = (k + 1) / (B + 1)
    straddle = [t for t in ths if lo < t <= hi]
    half = (hi - lo) / 2
    if hi < min(ths): precise = True
    elif p >= 0.05: precise = half <= 0.05
    elif p >= 0.01: precise = half <= 0.5 * p
    else: precise = False
    return precise and not straddle, (lo, hi)

def nulls_for(z, man, key, sel=None):
    F, seeds = z[f"F__{key}"], z[f"seeds__{key}"]
    if sel is not None: F, seeds = F[sel], seeds[sel]
    nm = man["nulls"][key]
    mu, var, dom = z[f"mu__{key}"], z[f"var__{key}"], z[f"dom__{key}"].astype(bool)
    S = z[f"S__{key}"] if f"S__{key}" in z.files else None
    coefs = man["shift_coefficients"]
    vs = [(str(c), (c * S if S is not None else None)) for c in (coefs if S is not None else [0.0])]
    if nm["m1"] is not None:
        d1, ka = z[f"d1__{key}"], nm["m1"]["kappa"]
        vs += [(f"m1+{ka}", ka * d1), (f"m1-{ka}", -ka * d1)]
    out = []
    for name, sv in vs:
        out.append(rp.statistics(F + (sv if sv is not None else 0.0), mu, var, z["V"], dom, nm["surrogate_seed0"], seeds=seeds))
    return out, mu, var, dom

def pvals_against(t, tn):
    s = np.sort(np.asarray(tn, float))
    return (s.size - np.searchsorted(s, np.asarray(t, float), side="left") + 1) / (s.size + 1)

res = {}
zf = np.load(rc / "data/frozen/inference_sufficient.npz")
manf = json.loads((rc / "data/frozen/inference_sufficient.npz.manifest.json").read_text())
ev = json.loads((rc / "expected/joint-evaluate.json").read_text())
res["J02"] = {"supported": int(zf["supported_cells"].size), "dom": {k: int(zf[f"dom__{k}"].sum()) for k in manf["nulls"]}}
res["J04_jitters_shape"] = list(zf["jitters"].shape)
# J13
j13 = {}
for key in manf["nulls"]:
    nulls, mu, var, dom = nulls_for(zf, manf, key)
    tj, sj = rp.statistics(zf["jitters"], mu, var, zf["V"], dom, 0, draw=False)
    row = {}
    for i, (s, tobs) in enumerate((("total", tj), ("shape", sj))):
        pj = np.max([pvals_against(tobs, nn[i]) for nn in nulls], axis=0)
        B = len(zf[f"seeds__{key}"])
        mine = {"min": float(pj.min()), "max": float(pj.max()), "kmin": int(round(pj.min() * (B + 1))) - 1,
                "kmax": int(round(pj.max() * (B + 1))) - 1, "B": B}
        want = ev["tests"][key]["observed_jitter_p"][s]
        mine["match_expected"] = bool(np.isclose(mine["min"], want["min"], rtol=1e-12) and np.isclose(mine["max"], want["max"], rtol=1e-12))
        row[s] = mine
    j13[key] = row
res["J13"] = j13
# J28 / J21
zu = np.load(rc / "data/recovery-union/inference_sufficient.npz")
manu = json.loads((rc / "data/recovery-union/inference_sufficient.npz.manifest.json").read_text())
m = 10
ths = sorted(set([0.05 / (m - i) for i in range(m)]) | {0.01, 0.05})
j28 = {}
for key in manu["nulls"]:
    seeds = zu[f"seeds__{key}"]; off = seeds - seeds.min()
    full = {}
    for Bcut in (1000, 1200, 1400):
        sel = off < Bcut
        nulls, mu, var, dom = nulls_for(zu, manu, key, sel)
        tt_o, ts_o = rp.statistics(zu["f_data"][None, :], mu, var, zu["V"], dom, 0, draw=False)
        ks = {}
        for i, (s, to) in enumerate((("total", tt_o[0]), ("shape", ts_o[0]))):
            k = max(int(np.sum(nn[i] >= to)) for nn in nulls)
            stop, iv = seqdec(k, int(sel.sum()), ths)
            ks[s] = {"k": k, "B": int(sel.sum()), "stop": stop, "look_hi": iv[1]}
        full[Bcut] = ks
    j28[key] = full
res["J28"] = j28
res["J21_union_B"] = {k: int(zu[f"seeds__{k}"].size) for k in manu["nulls"]}
res["thresholds"] = ths
print(json.dumps(res, indent=1, default=float))
