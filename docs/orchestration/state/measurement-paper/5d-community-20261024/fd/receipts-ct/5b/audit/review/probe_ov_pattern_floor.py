"""Probe: does OV_pattern for the (uniform) normalization group produce a nonzero number below LEAK_FLOOR=1e-30?
Uses the committed 5B readout's g and e, and S1's own normalization construction outer(NF f, NF f) / outer(f, f)
on random f of order 1e-39 (f itself is not read)."""
import json, sys
from pathlib import Path
import numpy as np
W = Path(sys.argv[1])
sys.path.insert(0, str(W / "nd-unfolding"))
import fd_ct_5b_audit as au
import fd_f0_regrade as f0
ro = json.loads((W / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/readout/fd_ct_5b_periods.json").read_text())
e = ro["constants"]["exposure_share"]
g = {X: np.asarray(ro["g_vs_5A"]["periods"][X]["g_5b"]) for X in au.PER}
k = au.kfac(e)
pat = {X: g[X] - g[X].mean() for X in au.PER}
Ppat = k * sum(e[X] * np.outer(pat[X], pat[X]) for X in au.PER)
NF = 0.014
hits = 0
vals = []
for s in range(200):
    rng = np.random.default_rng(s)
    f = rng.uniform(0.2, 5.0, 16) * 1e-39
    B = np.outer(NF * f, NF * f) / np.outer(f, f)
    o = au.ov(Ppat, B)
    small = [v for v in [o["OV"], *o["b"]] if v != 0 and abs(v) < f0.LEAK_FLOOR]
    vals.append((o["OV"], *o["b"]))
    hits += bool(small)
# exact-uniform case (B_rel built as NF^2 * ones)
o = au.ov(Ppat, np.full((16, 16), NF ** 2))
print("S1 construction over 200 random f: draws with a nonzero |value| < 1e-30 in OV_pattern[normalization]:", hits)
print("  median |b_1|, |b_2|, OV:", np.median(np.abs(np.array(vals)), axis=0)[[1, 2, 0]])
print("exactly uniform B: OV_pattern", o["OV"], "b", o["b"], "-> guard refuses:",
      any(v != 0 and abs(v) < f0.LEAK_FLOOR for v in [o["OV"], *o["b"]]))
