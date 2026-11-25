import csv, json, numpy as np
ST = "/Users/josephbailey/local-research/wt-ibu-chi2/docs/orchestration/state/ibu-chi2-20261123"
W = "/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/8f21a498-e586-4293-aaeb-c5560401abaa/scratchpad/resp/work"
P = np.load(ST + "/evloop/results/ibuchi_products.npz"); M, T = P["BASE_M"], P["T"]
ipt, ipz = np.divmod(np.arange(224), 16)
def mig(axis_idx, n):
    out = np.zeros((n, n))
    for i in range(n):
        for j in range(n): out[i, j] = M[np.ix_(axis_idx == j, axis_idx == i)].sum()
    return out / out.sum(1, keepdims=True)
P3, P4 = mig(ipz, 16), mig(ipt, 14)
def load(fn, a, b):
    V = np.zeros((a, b)); Sg = np.zeros((a, b))
    for r in csv.DictReader(open(f"{W}/{fn}")):
        k = (int(r["true_bin"]), int(r["reco_bin"])) if "true_bin" in r else (int(r["ipt"]), int(r["ipz"]))
        V[k] = float(r["value"]); Sg[k] = float(r["sigma"])
    return V, Sg
F3, S3 = load("fig3.csv", 16, 16); F4, S4 = load("fig4.csv", 14, 14); F5, S5 = load("fig5.csv", 14, 16)
eps = np.divide(M.sum(0), T, out=np.zeros(224), where=T > 0).reshape(14, 16)
Tw = T.reshape(14, 16)
c = Tw[:, 15] > 0
eps40_o = float((eps[c, 15] * Tw[c, 15]).sum() / Tw[c, 15].sum()); eps40_t = float((F5[c, 15] * Tw[c, 15]).sum() / Tw[c, 15].sum())
sx = 0.0025
q = dict(P_ii=(float(P3[15, 15]), float(F3[15, 15])), P_bi=(float(P3[15, 14]), float(F3[15, 14])), P_fi=(float(P3[14, 15]), float(F3[14, 15])))
mig_diff = any(abs(o - t) >= 0.03 and abs(o - t) > 3 * sx for k, (o, t) in q.items() if k in ("P_ii", "P_fi"))
eff_rel = eps40_o / eps40_t - 1; eff_diff = abs(eff_rel) >= 0.05 and abs(eps40_o - eps40_t) > 3 * sx
unres = 3 * sx >= 0.03
reading = "UNRESOLVED" if unres else ("+".join([x for x, f in (("MIGRATION-DIFF", mig_diff), ("EFF-DIFF", eff_diff)) if f]) or "NEITHER")
out = dict(quantities_ours_theirs=q, eps40_ours=eps40_o, eps40_theirs=eps40_t, eps40_rel=eff_rel, reading=reading,
           desc=dict(eps_col15_by_pt_ours=np.round(eps[:, 15], 3).tolist(), eps_col15_by_pt_theirs=np.round(F5[:, 15], 3).tolist(),
                     eps_col14_ours=np.round(eps[:, 14], 3).tolist(), eps_col14_theirs=np.round(F5[:, 14], 3).tolist(),
                     fig3_maxabs_diff=float(np.abs(P3 - F3).max()), fig3_row15_ours=np.round(P3[15], 3).tolist(), fig3_row15_theirs=np.round(F3[15], 3).tolist(),
                     fig3_row14_ours=np.round(P3[14], 3).tolist(), fig3_row14_theirs=np.round(F3[14], 3).tolist(),
                     fig4_diag_ours=np.round(np.diag(P4), 3).tolist(), fig4_diag_theirs=np.round(np.diag(F4), 3).tolist(),
                     fig4_rows01_ours=np.round(P4[:2, :4], 3).tolist(), fig4_rows01_theirs=np.round(F4[:2, :4], 3).tolist()))
print(json.dumps(out, indent=1))
