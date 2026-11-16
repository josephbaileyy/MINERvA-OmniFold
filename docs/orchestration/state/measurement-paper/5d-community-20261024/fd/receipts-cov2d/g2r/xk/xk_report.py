"""Print xk's readout beside the control's (K as it ran), as recorded, with no reading added:
  route, route_reasons, primary and Q_R_alone (as stored); the paired and bounded band sets from "crosses" and "bounded"
  (x-nbands-paired, x-nbands-bounded and their total, x-nbands), per band; K1's null-band list; and every band's K1 ratios
  from each run's "[K1 ratios]" log lines.
    python3 xk_report.py <control k.json> <control k.log> <g2r k.json> <g2r k.log>"""
import json, re, sys
ck, cl, gk, gl = sys.argv[1:5]
C, G = json.load(open(ck)), json.load(open(gk))
for f in ("route", "route_reasons", "v1_source", "boot"):
    print(f"{f}: control {C.get(f)!r} | g2r {G.get(f)!r}")
for f in ("primary", "Q_R_alone"):
    print(f"{f}: control {json.dumps(C.get(f), sort_keys=True)}")
    print(f"{f}: g2r     {json.dumps(G.get(f), sort_keys=True)}")
bands = lambda d, k: sorted(x for x in d.get(k, {}) if x.startswith("band:"))
for name, k in (("paired (crosses)", "crosses"), ("bounded", "bounded")):
    c, g = bands(C, k), bands(G, k)
    print(f"x-nbands {name}: control {len(c)} | g2r {len(g)}; only control {sorted(set(c) - set(g))}; only g2r {sorted(set(g) - set(c))}")
print(f"x-nbands (paired + bounded): control {len(bands(C, 'crosses')) + len(bands(C, 'bounded'))} | g2r {len(bands(G, 'crosses')) + len(bands(G, 'bounded'))}")
print(f"K1 null bands: control {C.get('k1_null_bands')} | g2r {G.get('k1_null_bands')}")
rx = re.compile(r"^\[K1 ratios\] (.+?): kind (\S+); ratio16 (\S+) ratio2 (\S+)$")
def ratios(path):
    out = {}
    for ln in open(path).read().splitlines():
        m = rx.match(ln)
        if m:
            out[m.group(1)] = (m.group(2), m.group(3), m.group(4))
    return out
rc, rg = ratios(cl), ratios(gl)
for lab in sorted(set(rc) | set(rg)):
    print(f"K1 {lab}: control {rc.get(lab)} | g2r {rg.get(lab)}")
print(f"K1 ratio lines: control {len(rc)} | g2r {len(rg)}")
