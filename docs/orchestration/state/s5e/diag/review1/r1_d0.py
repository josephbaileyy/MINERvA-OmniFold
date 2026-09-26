"""D0 and instrumentation meta checks."""
import glob, os
import numpy as np
from common import *
out = []
def cmp(name, prod, ref, key):
    p, r = L(prod), L(ref)
    xe = np.array_equal(p[key], r["xsec_flat"])
    te = np.array_equal(p["xtrue_flat"], r["xtrue_flat"]) if "xtrue_flat" in r else "REF-HAS-NO-XTRUE"
    out.append((name, xe, te, key, p[key].dtype, r["xsec_flat"].dtype, os.path.basename(ref)))
T = {"nominal": ("nominal_a0", 300000), "eavail": ("eavail_shape_a1", 301000), "q3": ("q3_given_eavail_w_a0.3", 302000)}
for t, (tn, b) in T.items():
    for i in range(4):
        s = b + i
        cmp(f"trace_{t}_bkg_s{s}", f"{RUNS}/trace/trace_{t}_bkg_s{s}.npz", f"{S5N}/dev/{tn}_s{s}.npz", "xsec_it5_flat")
for t in ("eavail", "q3"):
    tn, b = T[t]
    for i in range(4):
        s = b + i
        cmp(f"trace_{t}_sig_s{s}", f"{RUNS}/trace/trace_{t}_sig_s{s}.npz", f"{S5N}/diag/diag_sigonly_{tn}_s{s}.npz", "xsec_it5_flat")
for s in range(300004, 300012):
    cmp(f"bkg_b0_s{s}", f"{RUNS}/bkg/bkg_b0_s{s}.npz", f"{S5N}/dev/nominal_a0_s{s}.npz", "xsec_flat")
    # also: xsec_it5_flat == xsec_flat inside a K=5 product
for row in out: print(*row)
print("N bitwise xsec&xtrue equal:", sum(1 for r in out if r[1] and r[2] is True), "of", len(out))
p, r = L(f"{RUNS}/drv/data_b0.npz"), L(f"{S5N}/c7/data_negweight.npz")
print("data_b0 vs c7 xsec equal:", np.array_equal(p["xsec_flat"], r["xsec_flat"]), "keys ref:", [k for k in r if k != 'meta'])
# trace_checks of every traced product
bad = []; n = 0
for f in sorted(glob.glob(f"{RUNS}/*/*.npz")):
    m = L(f)["meta"]
    if "trace_checks" in m:
        n += 1
        tc = m["trace_checks"]; K = m["iters"]
        if not (tc["step1_mc_weights"] == K and tc["step2_pull_weights"] == K):
            bad.append((f, tc, K))
print("traced products:", n, "with checks != iters:", bad)
# the K=5 products: is xsec_it5_flat == xsec_flat?
for f in sorted(glob.glob(f"{RUNS}/bkg/*.npz")):
    d = L(f)
    if not np.array_equal(d["xsec_it5_flat"], d["xsec_flat"]): print("it5 != final", f)
# code digest used by the traced runs vs the reviewed file
m = L(f"{RUNS}/trace/trace_eavail_bkg_s301000.npz")["meta"]
print("trace code sha (meta):", m["code_sha256"].get("s5e_trace.py"), " deploy file:", sha(DEP + "/nd-unfolding/s5e_trace.py"))
for sub in ("asimov", "bkg", "drv", "rep"):
    shas = set()
    for f in glob.glob(f"{RUNS}/{sub}/*.npz"):
        mm = L(f)["meta"]; shas.add(str(mm.get("code_sha256", {}).get("s5e_trace.py") or mm.get("code_sha256", {}).get("s5e_driver_departure.py")))
    print(sub, "code sha set:", shas)
