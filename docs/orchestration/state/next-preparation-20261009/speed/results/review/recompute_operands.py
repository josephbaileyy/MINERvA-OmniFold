"""Reviewer's own reduction of the speed lane's sacct operands (independent of profile_from_sacct.py)."""
import sys, statistics as S
Q = sys.argv[1]
KIB, MIB = 1024, 1024**2
def mem_bytes(v):
    if not v: return None
    if v[-1].isdigit(): return float(v)
    u = v[-1]; x = float(v[:-1])
    return x * {"K": KIB, "M": MIB, "G": 1024**3}[u]
def hms(v):
    d = 0
    if "-" in v: d, v = v.split("-"); d = int(d)
    p = [float(t) for t in v.split(":")]
    while len(p) < 3: p = [0.0] + p
    return d*86400 + p[0]*3600 + p[1]*60 + p[2]
def load(fn):
    L = [l.rstrip("\n").split("|") for l in open(f"{Q}/operands/{fn}")]
    h = L[0]; return [dict(zip(h, r)) for r in L[1:]]
def stats(xs):
    xs = sorted(xs); return dict(n=len(xs), min=xs[0], med=S.median(xs), mean=S.mean(xs), max=xs[-1])
# replica 59410433
rep = load("sacct_59410433_steps.psv")
alloc = [r for r in rep if "." not in r["JobID"]]
bat = {r["JobID"].split(".")[0]: r for r in rep if r["JobID"].endswith(".batch")}
bill = {r["JobID"]: int(dict(kv.split("=") for kv in r["AllocTRES"].split(","))["billing"]) for r in alloc}
el = [int(r["ElapsedRaw"]) for r in alloc]
print("replica n", len(alloc), "states", {r["State"] for r in alloc}, "billing", set(bill.values()))
print("replica elapsed", stats(el))
nh = [int(r["ElapsedRaw"]) * bill[r["JobID"]] / 256 / 3600 for r in alloc]
print("replica node-h", stats(nh))
cpu = {k: hms(b["TotalCPU"]) for k, b in bat.items()}
busy = [cpu[r["JobID"]] / int(r["ElapsedRaw"]) for r in alloc]
print("replica busy CPUs", stats(busy))
k = 64
ser = [(k*int(r["ElapsedRaw"]) - cpu[r["JobID"]]) / (k-1) / int(r["ElapsedRaw"]) for r in alloc]
print("replica serial-bound fraction", stats(ser))
rss = [mem_bytes(b["MaxRSS"])/1e9 for b in bat.values()]
print("replica MaxRSS GB(dec)", stats(rss), "read GB", stats([mem_bytes(b["MaxDiskRead"])/1e9 for b in bat.values()]))
# universe sweeps
uni = load("sacct_universe_sweeps_batch.psv")
thr = 121920 * MIB
for m in ("55677843", "55677842"):
    b = [r for r in uni if r["JobID"].startswith(m + "_")]
    longs = [r for r in b if int(r["ElapsedRaw"]) > 300]
    shorts = [int(r["ElapsedRaw"]) for r in b if int(r["ElapsedRaw"]) <= 300]
    e = [int(r["ElapsedRaw"]) for r in longs]
    print(f"\n{m}: total {len(b)}, >300s {len(longs)}, <=300s {len(shorts)} (max short {max(shorts) if shorts else None})")
    # check gap in elapsed distribution
    allE = sorted(int(r["ElapsedRaw"]) for r in b)
    gaps = max((allE[i+1]-allE[i], allE[i], allE[i+1]) for i in range(len(allE)-1))
    print("  largest elapsed gap", gaps)
    print("  elapsed", stats(e), "node-h median", S.median(e)/3600)
    r_ = [mem_bytes(r["MaxRSS"]) for r in longs]
    print("  MaxRSS GB(dec)", {k: round(v/1e9, 2) if k != 'n' else v for k, v in stats(r_).items()})
    print("  count RSS > 121,920 MiB:", sum(x > thr for x in r_), " > 121.92e9 B:", sum(x > 121.92e9 for x in r_))
    d = [mem_bytes(r["MaxDiskRead"])/1e9 for r in longs]
    print("  MaxDiskRead GB(dec)", stats(d))
    dshort = [mem_bytes(r["MaxDiskRead"])/1e9 for r in b if int(r["ElapsedRaw"]) <= 300]
    print("  short tasks MaxDiskRead GB", stats(dshort) if dshort else None)
    bc = [hms(r["TotalCPU"])/int(r["ElapsedRaw"]) for r in longs]
    print("  busy CPUs", stats(bc))
    k = 128
    print("  serial frac", stats([(k*int(r["ElapsedRaw"]) - hms(r["TotalCPU"]))/(k-1)/int(r["ElapsedRaw"]) for r in longs]))
cvu = {r["JobID"]: r for r in uni if r["JobID"].startswith(("55677844", "55677845"))}
for kk, r in cvu.items():
    print(kk, r["ElapsedRaw"], round(hms(r["TotalCPU"])/int(r["ElapsedRaw"]), 2), round(mem_bytes(r["MaxRSS"])/1e9, 1))
misc = load("sacct_exact_pilots_ki85_steps.psv")
mb = {r["JobID"].split(".")[0]: r for r in misc if r["JobID"].endswith(".batch")}
e_cv = int(mb["59409026_1"]["ElapsedRaw"]); c_cv = hms(mb["59409026_1"]["TotalCPU"])
e_cu = [int(r["ElapsedRaw"]) for r in cvu.values()]; c_cu = [hms(r["TotalCPU"]) for r in cvu.values()]
e_u = S.median(int(r["ElapsedRaw"]) for r in uni if r["JobID"].startswith("55677843_") and int(r["ElapsedRaw"]) > 300)
exc = S.mean(e_cu) - e_cv
print("\nexcess s", exc, "excess cpu / wall", (S.mean(c_cu) - c_cv)/exc)
print("f_io (median uni task - 778)/median", (e_u - e_cv)/e_u, " 1801/2547", exc/e_u, " excess/mean(cv on uni)", exc/S.mean(e_cu))
print("exact 53116554", mb["53116554"]["ElapsedRaw"], hms(mb["53116554"]["TotalCPU"])/int(mb["53116554"]["ElapsedRaw"]), mem_bytes(mb["53116554"]["MaxRSS"])/1e9)
print("full-node replica busy", c_cv/e_cv, "serial", (128*e_cv - c_cv)/127/e_cv, "RSS", mem_bytes(mb["59409026_1"]["MaxRSS"])/1e9)
ki = [r for k_, r in mb.items() if k_.startswith(("59466329", "59466330", "59469539"))]
print("KI85 n", len(ki), stats([int(r["ElapsedRaw"]) for r in ki]), "busy med", S.median(hms(r["TotalCPU"])/int(r["ElapsedRaw"]) for r in ki))
print("KI85 serial med", S.median((64*int(r["ElapsedRaw"]) - hms(r["TotalCPU"]))/63/int(r["ElapsedRaw"]) for r in ki), "nodeh med", S.median(int(r["ElapsedRaw"])*64/256/3600 for r in ki))
print("node mem GB", 487802*MIB/1e9, "121920MiB in GB", thr/1e9, "GiB", thr/1024**3)
