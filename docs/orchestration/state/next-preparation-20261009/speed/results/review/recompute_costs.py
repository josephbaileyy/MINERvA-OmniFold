"""Reviewer's independent cost arithmetic (does not import the lane's costs.py)."""
import json, math, sys, statistics as S
R = sys.argv[1]  # worktree root
Q = R + "/docs/orchestration/state/next-preparation-20261009/speed"
lane = json.load(open(Q + "/results/costs.json"))
Cpub = json.load(open(R + "/docs/orchestration/state/uncertainty-preparation-20261008/c/costs.json"))
# ---- my implementation of lane C's admitted total -----------------------------------
def admitted(proc, cv, uni, ovh, ext, retry, verif, cons_setup, n_inner, n_exp=5000, dev=6.0):
    setup = [12 * (24.0 if cons_setup else 2.5) * 24 / 256,   # S-r
             187 * uni + cv,                                   # S-a (pairing not established)
             (120 * 5 * 8 / 256 if cons_setup else 0.0) + 10 * uni,  # S-b
             20.0 if cons_setup else 2.0,                      # S-d
             300 * cv if cons_setup else 0.0,                  # S-e
             200 * cv,                                         # S-f
             3 * 202 * cv * ovh]                               # S-j
    setup = sum(round(x, 4) for x in setup)
    if proc == "P1": pe = cv*ovh + n_inner*cv + 10*cv + 187*uni + ext
    elif proc == "P2": pe = cv*ovh + ext
    else: pe = cv*ovh + n_inner*cv + ext
    prod = n_exp * round(pe, 6)
    sub = setup + dev + prod + verif*(prod+setup) + retry*(prod+setup+dev)
    return sub / 0.8
SC = {}
for name in ("optimistic", "conservative"):
    s = Cpub["scenarios"][name]
    SC[name] = dict(cv=s["c_cv_unfold"]["value"], uni=s["c_universe_unfold"]["value"],
                    ovh=s["nuisance_pseudodata_overhead"]["value"], ext=s["c_extraction_per_experiment"]["value"],
                    retry=s["retry_rate"]["value"], verif=s["verification_fraction"]["value"])
NI = {"P1": 300, "P2": 50, "P3": 50}
PK = {"P1": "P1_reconstructed_full", "P2": "P2_fixed_band", "P3": "P3_shortcut_S1_S2"}
print("== C reproduction (mine vs C published)")
for name, s in SC.items():
    for p in ("P1", "P2", "P3"):
        a = admitted(p, s["cv"], s["uni"], s["ovh"], s["ext"], s["retry"], s["verif"], name == "conservative", NI[p])
        print(f"  {name:12s} {p}: mine {a:12.3f}  C {Cpub['totals'][name][PK[p]]['admitted_total_node_h']:12.3f}")
# ---- operands from raw sacct (from my recompute_operands numbers) -------------------
e_cv_shared, e_cv_full, e_uni, excess, e_exact = 840.0, 778.0, 2547.0, 1801.0, 69523.0
rss_exact, rss_uni_med, rss_uni_max = 16786760*1024/1e9, 71.16, 186.64  # pooled max over both sweeps
node_mem = 487802 * 2**20 / 1e9
# local per-row costs (min of repeats) taken from results/bench_loader_fill.jsonl records
B = {}
for ln in open(Q + "/results/bench_loader_fill.jsonl"):
    d = json.loads(ln)
    if "seconds" in d: B[(d["variant"], d["tree"].replace(".root", ""))] = min(d["seconds"]) / d["rows"] * 1e6
t = "synth_rows1000000_extra0"
rows = dict(sig=32849103, truth=32849103, data=4119797, bkg=658227)
reads = (rows["sig"] * B[("pinned", t)] + (rows["truth"] + rows["data"] + rows["bkg"]) * B[("truth", t)]) / 1e6
fills = 6 * rows["sig"] * B[("fill_loop", t)] / 1e6
after = (sum(rows.values()) * B[("columnar", t)] + 6 * rows["sig"] * B[("fill_n", t)]) / 1e6
s_loop = (reads + fills) / after
f_lo = (reads + fills) / e_cv_shared
f_hi = 0.5259545  # my serial-bound median (recompute_operands.out)
resid = (B[("status", "synth_rows200000_extra192")] - B[("pinned", "synth_rows200000_extra0")]) / \
        (B[("pinned", "synth_rows200000_extra192")] - B[("pinned", "synth_rows200000_extra0")])
s_io = 1 / resid
f_io = (e_uni - e_cv_full) / e_uni
print(f"\nreads {reads:.1f} s fills {fills:.1f} s loops {reads+fills:.1f} s after {after:.1f} s s_loop {s_loop:.3f}")
print(f"f_loop [{f_lo:.4f}, {f_hi:.4f}]  resid {resid:.4f} s_io {s_io:.2f}  bytes ratio {171.117087867/2.53:.1f}  f_io {f_io:.4f}")
A = lambda f, s: (1 - f) + f / s
for lab, f, s in (("io", f_io, s_io), ("loop_lo", f_lo, s_loop), ("loop_hi", f_hi, s_loop)):
    print(f"  S[{lab}] measured {1/A(f,s):.3f}  2/5/10/100 " + " ".join(f"{1/A(f,x):.3f}" for x in (2,5,10,100)) + f"  ceil {1/(1-f):.3f}")
print(f"  exact loops f {f_lo*e_cv_shared/e_exact:.4f}-{f_hi*e_cv_shared/e_exact:.4f}; exact io f {excess/(e_exact+excess):.4f} ceil {(e_exact+excess)/e_exact:.4f}")
# ---- exact backend pricing ----------------------------------------------------------
pack = lambda r: max(1, min(128, math.floor(node_mem / r)))
cvp = e_exact / 3600 / pack(rss_exact)
def P05(rate): return 187 * rate + cvp
rate_safe = (e_exact + excess) / 3600 / pack(rss_uni_max)
rate_med = (e_exact + excess) / 3600 / pack(rss_uni_med)
rate_p1 = (e_exact + resid * excess) / 3600 / pack(rss_exact)
lists, arrays = 11 * rows["sig"] * 32 / 1e9, 11 * rows["sig"] * 8 / 1e9
rss_p2 = rss_exact - lists + arrays
cvp2 = e_exact / 3600 / pack(rss_p2); rate_p12 = (e_exact + resid * excess) / 3600 / pack(rss_p2)
print(f"\npack exact {pack(rss_exact)} (rss {rss_exact:.2f}), uni max {pack(rss_uni_max)}, uni med {pack(rss_uni_med)}, p2 rss {rss_p2:.2f} -> {pack(rss_p2)}")
for lab, cv_, uni_ in (("A 0.68", 0.68, 0.68), ("C ratio", 0.68, 0.68*0.5/(804/3600)), ("safe", cvp, rate_safe),
                       ("median", cvp, rate_med), ("p1", cvp, rate_p1), ("p1+p2", cvp2, rate_p12)):
    p03, p05, p09 = 50*cv_, 187*uni_ + cv_, 10*cv_
    tot = p03+p05+p09
    print(f"  {lab:8s} unit {uni_:.4f} P05 {p05:9.2f} sum {tot:9.2f} admitted {tot*1.15/0.8:9.1f}  N300 sum {tot+250*cv_:9.2f} adm {(tot+250*cv_)*1.15/0.8:8.1f}")
print(f"  billing ratio safe/p1 {rate_safe/rate_p1:.2f}; waves at 30 nodes: safe {math.ceil(188/60)}, p1 {math.ceil(188/(30*29))}")
# what packing would the CV-file exact RSS spread allow, and a 3rd option: pack by p99-ish
# ---- LightGBM universe rates ---------------------------------------------------------
p1_full = (e_cv_full + resid*excess)/3600; p1_sh = (e_cv_shared + resid*excess)*64/256/3600
print(f"\nuni rate now {e_uni/3600:.4f} p1 full {p1_full:.4f} p1 shared {p1_sh:.4f}; billing gain {e_uni/3600/p1_full:.2f} / {e_uni/3600/p1_sh:.2f}")
cv_sh = e_cv_shared*64/256/3600
print(f"S-a now {187*e_uni/3600 + e_cv_full/3600:.2f}  p1 full {187*p1_full + e_cv_full/3600:.2f}  p1 sh {187*p1_sh + cv_sh:.2f}")
a_hi, a_lo = A(f_hi, s_loop), A(f_lo, s_loop)
p12 = [(e_cv_shared*a + resid*excess)*64/256/3600 for a in (a_hi, a_lo)]
print(f"S-a p1+p2 shared {[round(187*r+cv_sh,2) for r in p12]}")
# ---- accelerated C rows -------------------------------------------------------------
print("\n== accelerated C rows (mine; cons_setup explicit | C's own coupling uni==0.5)")
o, c = SC["optimistic"], SC["conservative"]
rows_ = {
 "cons measured_universe_rate": (c, c["cv"], e_uni/3600, True),
 "cons p1_fullnode": (c, c["cv"], p1_full, True),
 "cons p1_p2_fullnode": (c, c["cv"]*a_hi, (e_cv_full*a_hi + resid*excess)/3600, True),
 "opt p1_shared64": (o, o["cv"], p1_sh, False),
 "opt p1_p2_shared64": (o, o["cv"]*a_hi, p12[0], False),
}
for k, (s, cv_, uni_, cons) in rows_.items():
    for p in ("P1", "P2", "P3"):
        mine = admitted(p, cv_, uni_, s["ovh"], s["ext"], s["retry"], s["verif"], cons, NI[p])
        coupled = admitted(p, cv_, uni_, s["ovh"], s["ext"], s["retry"], s["verif"], uni_ == 0.5, NI[p])
        key = k.split(" ", 1)
        nm = "conservative" if key[0] == "cons" else "optimistic"
        ln = lane["procedures"]["C_total_uncertainty_4x1250"][nm][key[1]][PK[p]]
        print(f"  {k:28s} {p}: mine {mine:12.1f}  C-coupled {coupled:12.1f}  lane {ln:12.1f}")
for nm, s in SC.items():
    for x in (100,):
        print(f"  all unfolds x{x} {nm}: " + " ".join(f"{p} {admitted(p, s['cv']/x, s['uni']/x, s['ovh'], s['ext'], s['retry'], s['verif'], nm=='conservative', NI[p]):.0f}" for p in ("P1","P2","P3")))
# ---- N2 / B ---------------------------------------------------------------------------
n2 = 100*0.0708*1.05
print(f"\nN2 now {(n2+0.4)/0.8:.2f}-{(n2+2.3)/0.8:.2f}; p2 {(n2*a_hi+0.4)/0.8:.2f}-{(n2*a_lo+2.3)/0.8:.2f}; saving {n2*(1-a_hi)/0.8:.2f}")
b = 719*301*0.059147*1.05
print(f"B primary {b:.1f}; p2 {b*a_hi:.0f}-{b*a_lo:.0f}; zero loops {b*(1-f_hi):.0f}-{b*(1-f_lo):.0f} = {b*(1-f_hi)/3040.6:.2f}-{b*(1-f_lo)/3040.6:.2f} x remaining")
b2 = 1116*301*0.059147*1.05; print(f"B N1116 {b2:.1f}; p2 {b2*a_hi:.0f}-{b2*a_lo:.0f}")
# payback
p1_ver = 2*cv_sh + 3*p1_full
print(f"\nP1 verif {p1_ver:.3f} saving/uni-full {e_uni/3600-p1_full:.3f} shared {e_uni/3600-p1_sh:.3f} exact {rate_safe-rate_p1:.2f}; payback {p1_ver/(e_uni/3600-p1_full):.2f} unfolds")
p2_ver = 6*cv_sh; sav = [cv_sh*(1-a) for a in (a_hi, a_lo)]
print(f"P2 verif {p2_ver:.3f} savings {sav} payback {[p2_ver/x for x in sav]}")
