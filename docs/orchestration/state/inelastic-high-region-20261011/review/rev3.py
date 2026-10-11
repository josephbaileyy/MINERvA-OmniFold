import sys, json, numpy as np
IN, RES = sys.argv[1], sys.argv[2]
SH = (14, 16, 7, 7, 6)
def load(fn):
    z = np.load(f"{IN}/{fn}", allow_pickle=False)
    e = [np.asarray(z["edges_" + k], float) for k in ("pt", "pz", "eavail", "q3", "W")]
    dv = np.einsum("a,b,c,d,e->abcde", *[np.diff(x) for x in e])
    return np.asarray(z["xsec_flat"], float).reshape(SH) * dv
cv, mec = load("genie_cv_xsec5d_full.npz"), load("genie_mec_xsec5d_full.npz")
d = (mec - cv).sum(axis=(0, 1, 3, 4))
print("MEC-CV by A bin (frac of added):", np.round(d / d.sum(), 3), "added/CV total", round(d.sum() / cv.sum(), 4))
dw = (mec - cv).sum(axis=(0, 1, 2, 3)); print("MEC-CV by W bin:", np.round(dw / d.sum(), 3))
r = json.load(open(f"{RES}/R3R4_decomposition.json"))["results"]["production"]
mx = 0; where = None; sdmax = 0
for k, v in r.items():
    for reg in ("C", "M", "C_no_overflow", "C_overflow"):
        a, b = v["inclusive_first"][reg]["steps"], v["partition_first"][reg]["steps"]
        for s in a:
            if abs(a[s] - b[s]) > mx: mx, where = abs(a[s] - b[s]), (k, reg, s)
        sd = v["mc_sd"]["inclusive_first"][reg]["steps_sd"]
        sdmax = max(sdmax, max(sd.values()))
    print(k, "fallback", {a: round(b, 5) for a, b in v["fallback"].items()})
print("max order disagreement", round(mx, 4), where, "max MC sd per step", round(sdmax, 4))
