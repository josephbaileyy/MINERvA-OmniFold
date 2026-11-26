import csv, json, numpy as np, sys
E = sys.argv[1]
ST = "/Users/josephbailey/local-research/wt-ibu-chi2/docs/orchestration/state/ibu-chi2-20261123"
H = json.load(open(E + "/hists.json")); No, NE = np.array(H["ours"]), np.array(H["E"])
BN = np.load(ST + "/evloop/results/ibuchi_products.npz")["BASE_N"]
PZ = np.array([1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8, 9, 10, 15, 20, 40, 60])
PTo = np.array([0, .07, .15, .25, .33, .40, .47, .55, .70, .85, 1.00, 1.25, 1.50, 2.50, 4.50])
PTe = np.array([0, .075, .15, .25, .325, .40, .475, .55, .70, .85, 1.00, 1.25, 1.50, 2.50, 4.50])
ctl = {"C-REP": bool(np.array_equal(No, BN))}
pts = [p for p in csv.DictReader(open(ST + "/fig2/fig2_points.csv")) if p["blk"] == "bot" and p["kind"] == "data"]
dens = np.full(224, np.nan); qd = np.full(224, np.nan)
for p in pts:
    g = int(p["g"]); dens[g] = float(p["ydisp"]) / float(p["factor"]) * 1e5; qd[g] = float(p["quantum_count"]) / float(p["area"])
ipt, ipz = np.divmod(np.arange(224), 16)
def theirs(PT):
    area = np.array([(PT[i+1]-PT[i]) * (PZ[j+1]-PZ[j]) for i in range(14) for j in range(16)]); return dens * area, qd * area
def score(N, PT):
    D, Q = theirs(PT); X = 0.0; num = np.zeros(7); den = np.zeros(7)
    for s in range(16):
        sl = (ipz == s) & np.isfinite(D); Ns, Ds = N[sl].sum(), np.nansum(D[sl])
        for i in range(7):
            g = i * 16 + s
            if not np.isfinite(D[g]) or N[g] <= 0 or D[g] <= 0: continue
            fo, ft = N[g] / Ns, D[g] / Ds
            X += (fo - ft)**2 / (fo**2 * (1/N[g] + 1/Ns) + ft**2 * (1/D[g] + 1/Ds) + (Q[g] / np.sqrt(12) / Ds)**2)
            num[i] += fo * Ds; den[i] += ft * Ds
    return float(X), (num / den).tolist()
Xo, ro = score(No, PTo); Xe, re_ = score(NE, PTe)
conf = all(abs(re_[i] - 1) <= .015 for i in (0, 1, 3, 4, 5, 6)) and Xe <= .5 * Xo
part = Xe < Xo and abs(re_[0] - 1) <= .5 * abs(ro[0] - 1)
print(json.dumps(dict(controls=ctl, X_ours=Xo, rho_ours=ro, X_E=Xe, rho_E=re_,
    reading=("STOP" if not ctl["C-REP"] else "EDGES-CONFIRMED" if conf else "EDGES-PARTIAL" if part else "EDGES-NO")), indent=1))
