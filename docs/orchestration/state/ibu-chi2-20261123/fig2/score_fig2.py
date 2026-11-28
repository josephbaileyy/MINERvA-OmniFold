import csv, json, numpy as np
SC = "/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/8f21a498-e586-4293-aaeb-c5560401abaa/scratchpad"
P = np.load("/Users/josephbailey/local-research/wt-ibu-chi2/docs/orchestration/state/ibu-chi2-20261123/evloop/results/ibuchi_products.npz")
N = P["BASE_N"]; Pm = P["BASE_M"].sum(1) + P["BASE_B"]
pts = list(csv.DictReader(open(SC + "/fig2/work/fig2_points.csv")))
val = {}; qnt = {}
for p in pts:
    k = (p["blk"], p["kind"], int(p["g"])); val[k] = float(p["count"]); qnt[k] = float(p["quantum_count"])
kinds = sorted({p["kind"] for p in pts})
dk, mk = ("data" if "data" in kinds else kinds[0]), "mc"
def vec(kind, mode):
    v = np.full(224, np.nan)
    for g in range(224):
        t, b = (("top", kind, g)), (("bot", kind, g))
        if mode == "top": v[g] = val.get(t, np.nan)
        elif mode == "bot": v[g] = val.get(b, np.nan)
        else:
            c = [k for k in (t, b) if k in val]
            v[g] = val[min(c, key=lambda k: qnt[k])] if c else np.nan
    return v
ipt, ipz = np.arange(224)//16, np.arange(224)%16
def score(mode):
    D, Q = vec(dk, mode), vec(mk, mode)
    ok = np.isfinite(D) & np.isfinite(Q)
    reg = {"COL": ok & (ipz == 15), "ROW": ok & (ipt == 0), "ALL": ok}
    rd = lambda w: N[w].sum()/D[w].sum(); rm = lambda w: Pm[w].sum()/Q[w].sum()
    out = {"n_cells": int(ok.sum()), "abs_data_N_over_D": rd(reg["ALL"]), "abs_MC_P_over_Q": rm(reg["ALL"])}
    for r in ("COL", "ROW"):
        w = reg[r]
        out[r] = dict(rho_data=rd(w)/rd(reg["ALL"]) - 1, rho_MC=rm(w)/rm(reg["ALL"]) - 1,
                      ours_data_over_MC=N[w].sum()/Pm[w].sum(), theirs_data_over_MC=D[w].sum()/Q[w].sum(),
                      sumN=N[w].sum(), sumD=D[w].sum(), sumP=Pm[w].sum(), sumQ=Q[w].sum())
    return out
res = {m: score(m) for m in ("best", "top", "bot")}
# delta from top/bottom region sums
Dt, Db, Qt, Qb = vec(dk, "top"), vec(dk, "bot"), vec(mk, "top"), vec(mk, "bot")
ok = np.isfinite(Dt) & np.isfinite(Db) & np.isfinite(Qt) & np.isfinite(Qb)
delta = {}
for r, w in {"COL": ok & (ipz == 15), "ROW": ok & (ipt == 0)}.items():
    delta[r] = max(abs(Dt[w].sum()/Db[w].sum() - 1), abs(Qt[w].sum()/Qb[w].sum() - 1))
tau = {"COL": 0.05, "ROW": 0.032}
reading = {}
for r in ("COL", "ROW"):
    x = res["best"][r]
    if 3*delta[r] >= tau[r]: reading[r] = "UNRESOLVED"
    elif abs(x["rho_data"]) >= tau[r]: reading[r] = "DATA"
    elif abs(x["rho_MC"]) >= tau[r]: reading[r] = "MC"
    else: reading[r] = "NEITHER"
print(json.dumps(dict(kinds=kinds, delta=delta, tau=tau, reading=reading, results=res), indent=1))
