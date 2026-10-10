"""Re-review recompute of numbers the repair moved (own code; imports nothing from the lane)."""
import json, math, sys, statistics as S
R = sys.argv[1]; Q = R + "/docs/orchestration/state/next-preparation-20261009/speed"
U = {"K": 1024, "M": 1024**2, "G": 1024**3}
L = [l.rstrip("\n").split("|") for l in open(Q + "/operands/sacct_universe_sweeps_batch.psv")]
h = L[0]; rows = [dict(zip(h, x)) for x in L[1:]]
node = 487802 * 2**20 / 1e9
rss = {}
for m in ("55677843", "55677842"):
    rss[m] = sorted(float(r["MaxRSS"][:-1]) * U[r["MaxRSS"][-1]] / 1e9 for r in rows
                    if r["JobID"].startswith(m + "_") and int(r["ElapsedRaw"]) > 300)
    v = rss[m]; n = len(v)
    print(m, "n", n, "<=72.5 GB:", sum(x <= 72.5 for x in v), f"({sum(x <= 72.5 for x in v)/n:.3f})",
          "median", round(S.median(v), 2), "p90 idx(9n//10)", round(v[(9*n)//10], 2), "max", round(v[-1], 2))
pack = lambda r: max(1, min(128, math.floor(node / r)))
e_exact, excess = 69523.0, 1801.0
rss_exact = 16786760 * 1024 / 1e9
cvp = e_exact / 3600 / pack(rss_exact)
pur = rss["55677843"]
for lab, r in (("median", S.median(pur)), ("p90", pur[(9*len(pur))//10]), ("worst", pur[-1])):
    p = pack(r); unit = (e_exact + excess) / 3600 / p
    p05 = 187 * unit + cvp; tot = p05 + 50 * cvp + 10 * cvp
    print(f"{lab:6s} rss {r:7.2f} pack {p} unit {unit:.4f} P05 {p05:8.1f} sum {tot:8.1f} admitted {tot*1.15/0.8:7.1f} "
          f"= {tot*1.15/0.8/3040.6:.2f} x remaining; waves {math.ceil(188/(30*p))}; saving vs p1/unf {unit - (e_exact + 0.0683*excess)/3600/29:.2f}")
# conservative C, prototypes 1+2 with the smaller loop fraction
B = {}
for ln in open(Q + "/results/bench_loader_fill.jsonl"):
    d = json.loads(ln)
    if "seconds" in d: B[(d["variant"], d["tree"].replace(".root", ""))] = min(d["seconds"]) / d["rows"] * 1e6
t = "synth_rows1000000_extra0"; N = dict(sig=32849103, truth=32849103, data=4119797, bkg=658227)
loops = (N["sig"]*B[("pinned", t)] + (N["truth"]+N["data"]+N["bkg"])*B[("truth", t)] + 6*N["sig"]*B[("fill_loop", t)]) / 1e6
after = (sum(N.values())*B[("columnar", t)] + 6*N["sig"]*B[("fill_n", t)]) / 1e6
s = loops/after; f_lo = loops/840.0
resid = (B[("status", "synth_rows200000_extra192")] - B[("pinned", "synth_rows200000_extra0")]) / \
        (B[("pinned", "synth_rows200000_extra192")] - B[("pinned", "synth_rows200000_extra0")])
a_lo = (1 - f_lo) + f_lo / s
C = json.load(open(R + "/docs/orchestration/state/uncertainty-preparation-20261008/c/costs.json"))["scenarios"]["conservative"]
g = lambda k: C[k]["value"]
cv0, ovh, ext, retry, verif = g("c_cv_unfold"), g("nuisance_pseudodata_overhead"), g("c_extraction_per_experiment"), g("retry_rate"), g("verification_fraction")
def adm(proc, cv, uni, ni):
    setup = sum(round(x, 4) for x in [12*24*24/256, 187*uni+cv, 120*5*8/256 + 10*uni, 20.0, 300*cv, 200*cv, 3*202*cv*ovh])
    pe = {"P1": cv*ovh + ni*cv + 10*cv + 187*uni + ext, "P2": cv*ovh + ext, "P3": cv*ovh + ni*cv + ext}[proc]
    prod = 5000 * round(pe, 6); sub = setup + 6 + prod + verif*(prod+setup) + retry*(prod+setup+6)
    return sub / 0.8
cv, uni = cv0 * a_lo, (778.0 * a_lo + resid * excess) / 3600
print(f"a_lo {a_lo:.4f}; cons p1+p2: P1 {adm('P1',cv,uni,300):.1f} P2 {adm('P2',cv,uni,50):.1f} P3 {adm('P3',cv,uni,50):.1f}")
lane = json.load(open(Q + "/results/costs.json"))["procedures"]["C_total_uncertainty_4x1250"]["conservative"]["p1_p2_fullnode"]
print("lane", {k: round(v, 1) for k, v in lane.items()})
