"""Print xk's readout beside the control's (K as it ran), as recorded, with no reading added:
  route, route_reasons, primary and Q_R_alone (as stored) and the raw operands of the printed x-chi2-hi, x-p-min and
  x-zmax (and each variant's chi2/p/|z|); the paired and bounded band sets from "crosses" and "bounded"
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
def ends(d, name):
    R = d.get(name) or {}
    if not all(r in R for r in ("r0", "r1")):
        return None
    zmax = max(abs(z) for r in ("r0", "r1") for z in R[r]["z"])
    return {"chi2_4 r0": R["r0"]["chi2_4"], "chi2_4 r1": R["r1"]["chi2_4"], "p r0": R["r0"]["p"], "p r1": R["r1"]["p"],
            "p min": min(R["r0"]["p"], R["r1"]["p"]), "|z| max": zmax, "outcome": R.get("outcome"), "r_star": R.get("r_star")}
# the printed x- values' raw operands (make_values_fived16.py:551-578: x-chi2-hi from the primary's r1 chi2_4, x-p-min from
# its smaller p, x-zmax from its largest |z|; and per variant chi2/p at r0 and r1 and |z| max); no rounding here
for name in ("primary", "Q_R_alone", "C_PL_pair_zero"):
    print(f"{name} operands: control {ends(C, name)}")
    print(f"{name} operands: g2r     {ends(G, name)}")
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
