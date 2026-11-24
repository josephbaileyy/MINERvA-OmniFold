import csv, json, numpy as np
ST = "/Users/josephbailey/local-research/wt-ibu-chi2/docs/orchestration/state/ibu-chi2-20261123"
P = np.load(ST + "/evloop/results/ibuchi_products.npz"); a = P["scan_a"]; SA = P["scanA"]
pts = [p for p in csv.DictReader(open(ST + "/fig2/fig2_points.csv")) if p["blk"] == "bot" and p["kind"] == "data"]
D = np.full(224, np.nan); Q = np.full(224, np.nan)
for p in pts: D[int(p["g"])] = float(p["count"]); Q[int(p["g"])] = float(p["quantum_count"])
ipt, ipz = np.divmod(np.arange(224), 16)
rows = range(5)
def X_and_rho(N):
    X = 0.0; num = np.zeros(3); den = np.zeros(3)
    for s in range(16):
        sl = (ipz == s) & np.isfinite(D)
        Ns, Ds = N[sl].sum(), np.nansum(D[sl])
        if Ns <= 0 or Ds <= 0: continue
        for i in rows:
            g = i * 16 + s
            if not np.isfinite(D[g]) or N[g] <= 0 or D[g] <= 0: continue
            fo, ft = N[g] / Ns, D[g] / Ds
            var = fo**2 * (1/N[g] + 1/Ns) + ft**2 * (1/D[g] + 1/Ds) + (Q[g] / np.sqrt(12) / Ds)**2
            X += (fo - ft)**2 / var
            if i < 3: num[i] += fo * Ds; den[i] += ft * Ds   # pooled with their slice weights
    return X, num / den
i0 = int(np.argmin(np.abs(a)))
X0, rho0 = X_and_rho(SA[i0, i0])
grid = np.array([[X_and_rho(SA[i, j])[0] for j in range(len(a))] for i in range(len(a))])
bi, bj = np.unravel_index(np.argmin(grid), grid.shape); Xb, rhob = X_and_rho(SA[bi, bj])
edge = bi in (0, len(a) - 1) or bj in (0, len(a) - 1)
explains = (not edge) and abs(rhob[0] - 1) <= .02 and abs(rhob[1] - 1) <= .02 and Xb <= .5 * X0
partial = abs(rhob[0] - 1) <= .5 * abs(rho0[0] - 1)
reading = "AXIS-EXPLAINS" if explains else ("EDGE: " if edge else "") + ("AXIS-PARTIAL" if partial else "AXIS-NO")
# descriptive: rho by slice at (0,0) and best, rows 0-1
def by_slice(N):
    out = []
    for s in range(16):
        sl = (ipz == s) & np.isfinite(D); Ns, Ds = N[sl].sum(), np.nansum(D[sl])
        out.append([round(float((N[i*16+s]/Ns)/(D[i*16+s]/Ds)), 3) if D[i*16+s] > 0 else None for i in (0, 1, 2)])
    return out
print(json.dumps(dict(n_cells_rows0to4=int(sum(np.isfinite(D[i*16+s]) for i in rows for s in range(16))),
    X0=X0, rho0=rho0.tolist(), best_dx_mrad=float(a[bi]*1e3), best_dy_mrad=float(a[bj]*1e3), Xbest=float(Xb), rho_best=rhob.tolist(),
    edge=bool(edge), reading=reading, X_dx0_dy_profile=[round(float(x), 1) for x in grid[i0]],
    X_dy0_dx_profile=[round(float(x), 1) for x in grid[:, i0]], rows012_by_slice_at0=by_slice(SA[i0, i0]),
    rows012_by_slice_best=by_slice(SA[bi, bj])), indent=1))
