import runpy, sys, io, contextlib, numpy as np
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    g = runpy.run_path(sys.argv[1])
P, MB, BB, stats = g["P"], g["MB"], g["BB"], g["stats"]
d = P["scan_d"]; H = P["scanC"]
S0 = abs(stats(MB, P["BASE_N"], BB)["COL"]) if "BASE_N" in P else None
for i in range(len(d)):
    s = stats(MB, H[i], BB)
    print(f"{d[i]:+.3f} COL={s['COL']:+.4f} ROW={s['ROW']:+.4f} chi2={s['chi2']:.1f}")
