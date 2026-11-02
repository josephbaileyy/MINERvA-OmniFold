"""Re-derive each new printed number from the GENCMP readouts, independently of make_values_fived16.py, and give the
readout file:line of its source value; compare with values_fived16.tex."""
import json, math, re, sys
from pathlib import Path
WT = Path(sys.argv[1]); R = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/gencmp"
FG = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/with-cpl/readout/fd_g_readout.json"
FGN = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/readout/fd_g_readout.json"
vals = dict(re.findall(r"\\@namedef\{fv@([^}]*)\}\{(.*)\}", (WT / "docs/analysis-note/values_fived16.tex").read_text()))
def J(rel): return json.loads((WT / rel).read_text())
def line(rel, keys):
    """line of the last key of a key path in a pretty-printed JSON file (each key searched after the previous)"""
    L = (WT / rel).read_text().splitlines(); i = 0
    for k in keys:
        pat = f'"{k}":' if isinstance(k, str) else None
        if isinstance(k, int):          # list index: the k-th element line after the list opens
            i += 1 + k; continue
        while pat not in L[i]: i += 1
    return f"{rel.split('/')[-1]}:{i + 1}"
rows = []
def row(key, got, where):
    pr = vals.get(key, "MISSING"); rows.append((key, pr, got, where, "ok" if pr == got else "DIFF"))
defs, ch, nat, ov = (J(f"{R}/readout/{f}.json") for f in ("defs", "ch", "native", "overlap"))
P = {"genie_cv": "gcv", "genie_mec": "gmec", "nuwro": "nuwro", "gibuu": "gibuu"}
for n, k in P.items():
    for mat, suf in (("reported", ""), ("without_C_PL5D", "-nopl")):
        for part in ("total", "shape_only"):
            x = defs["table_2x2"][n]["CH"]["analysis_definitions"][mat][part]
            w = line(f"{R}/readout/defs.json", ["table_2x2", n, "CH", "analysis_definitions", mat, part])
            row(f"g-{k}-{part}-chi2int{suf}", f"{x:.0f}", w); row(f"g-{k}-{part}-chi2{suf}", f"{x:.2f}", w)
for n in ("nuwro", "gibuu"):
    for mat, suf in (("reported", ""), ("without_C_PL5D", "-nopl")):
        for part in ("total", "shape_only"):
            x = defs["table_2x2"][n]["carbon"]["analysis_definitions"][mat][part]
            w = line(f"{R}/readout/defs.json", ["table_2x2", n, "carbon", "analysis_definitions", mat, part])
            row(f"g-{P[n]}-carbon-{part}-chi2int{suf}", f"{x:.0f}", w); row(f"g-{P[n]}-carbon-{part}-chi2{suf}", f"{x:.2f}", w)
t2 = defs["table_2x2"]["gibuu"]
row("g-gibuu-chrise", f"{t2['CH']['analysis_definitions']['reported']['total'] - t2['carbon']['analysis_definitions']['reported']['total']:.1f}", "defs.json table_2x2 gibuu CH - carbon")
for t, tag in (("carbon", "gen-carbon"), ("CH", "gen-ch"), ("CH_genie_hydrogen", "genieh")):
    for n in ("nuwro", "gibuu"):
        x = ch["generators"][n][t]["chi2"]["reported"]["total"]["chi2"]
        row(f"g-{P[n]}-{tag}-total-chi2r1", f"{x:.1f}", line(f"{R}/readout/ch.json", ["generators", n, t, "chi2", "reported", "total", "chi2"]))
for route, tag in (("generator_definitions", "gen"), ("analysis_definitions", "ana")):
    r = nat[route]["rule"]
    row(f"gnat-{tag}-sumz2", f"{r['sum_z2']:.1f}", line(f"{R}/readout/native.json", [route, "rule", "sum_z2"]))
    row(f"gnat-{tag}-zmax", f"{r['max_abs_z']:.1f}", line(f"{R}/readout/native.json", [route, "rule", "max_abs_z"]))
    row(f"g-nuwro-native-{tag}-total-chi2", f"{nat[route]['native_chi2']['reported']['total']['chi2']:.2f}", line(f"{R}/readout/native.json", [route, "native_chi2", "reported", "total"]))
m = re.search(r"Σz² < ([\d.]+)|sum z\^2 over the cells < ([\d.]+)", nat["generator_definitions"]["rule"]["rule"])
row("gnat-rule-sumz2", m.group(2), line(f"{R}/readout/native.json", ["generator_definitions", "rule", "rule"]))
best = max(((abs(x), n, i) for n in P for i, x in enumerate(defs["generators"][n]["CH"]["delta_over_sigma"])))
row("gdef-dmax", f"{best[0]:.3f}", line(f"{R}/readout/defs.json", ["generators", best[1], "CH", "delta_over_sigma", best[2]]) + f" ({best[1]}, R{best[2]:02d})")
row("gdef-dmax-bound", f"{math.ceil(100 * best[0]) / 100:.2f}", "ceil of gdef-dmax")
best = max(((x, n, i) for n in P for i, x in enumerate(defs["generators"][n]["CH"]["seed_spread_over_sigma"])))
row("gdef-seedmax", f"{best[0]:.3f}", line(f"{R}/readout/defs.json", ["generators", best[1], "CH", "seed_spread_over_sigma", best[2]]) + f" ({best[1]}, cell {defs['generators'][best[1]]['CH']['cells'][best[2]]})")
txt = (WT / f"{R}/receipts/d_projection.txt").read_text().splitlines()
ln = next(i for i, l in enumerate(txt) if "+2.1%" in l)
row("gnat-probe-pct", re.search(r"\+([\d.]+)%", txt[ln]).group(1), f"d_projection.txt:{ln + 1}")
q = ov["quadrants"]
d = {k: q[k]["3D"]["d_pct"] for k in q}; z = {k: abs(q[k]["3D"]["d_over_sigma16"]) for k in q}
lo = min(d, key=lambda k: -d[k]); hi = max(d, key=lambda k: -d[k]); zk = max(z, key=z.get)
row("g3d-pct-lo", f"{-d[lo]:.1f}", line(f"{R}/readout/overlap.json", ["quadrants", lo, "3D", "d_pct"]) + f" ({lo})")
row("g3d-pct-hi", f"{-d[hi]:.1f}", line(f"{R}/readout/overlap.json", ["quadrants", hi, "3D", "d_pct"]) + f" ({hi})")
row("g3d-zmax", f"{z[zk]:.2f}", line(f"{R}/readout/overlap.json", ["quadrants", zk, "3D", "d_over_sigma16"]) + f" ({zk})")
row("g3d-qa-unrep", r"1.1\times10^{-7}" if f"{q['QA']['unreported_share_P5']:.1e}" == "1.1e-07" else "?", line(f"{R}/readout/overlap.json", ["quadrants", "QA", "unreported_share_P5"]))
lab = defs["generators"]["gibuu"]["CH"]["label"]
row("g-gibuu-hlab-sigc", re.search(r"<= ([\d.]+) sigma_c", lab).group(1), line(f"{R}/readout/defs.json", ["generators", "gibuu", "CH", "label"]))
row("g-gibuu-hlab-dis", re.search(r"(\d+)% of the hydrogen", lab).group(1), line(f"{R}/readout/defs.json", ["generators", "gibuu", "CH", "label"]))
row("g-ch-hweight", "1/13" if "12:1 per nucleon" in defs["generators"]["nuwro"]["CH"]["label"] else "?", line(f"{R}/readout/defs.json", ["generators", "nuwro", "CH", "label"]))
# abstracts and the falls, from the table and Stage G's Tune v1
g, gn = J(FG), J(FGN)
tune = {"with": next(p for p in g["predictions"] if p["name"] == "mnvtune_v1"), "without": next(p for p in gn["predictions"] if p["name"] == "mnvtune_v1")}
ext = [defs["table_2x2"][n]["CH"]["analysis_definitions"]["reported"]["total"] for n in ("genie_cv", "genie_mec", "nuwro")]
extn = [defs["table_2x2"][n]["CH"]["analysis_definitions"]["without_C_PL5D"]["total"] for n in ("genie_cv", "genie_mec", "nuwro")]
row("g-ext-chi2int-min16", f"{min(ext):.0f}", "min of g-{gcv,gmec,nuwro}-total"); row("g-ext-chi2int-max16", f"{max(ext):.0f}", "max of the same")
row("g-ext-chi2int-min16-nopl", f"{min(extn):.0f}", "without C_PL"); row("g-ext-chi2int-max16-nopl", f"{max(extn):.0f}", "without C_PL")
for part in ("total", "shape_only"):
    fall = [1 - defs["table_2x2"][n]["CH"]["analysis_definitions"]["reported"][part] / defs["table_2x2"][n]["CH"]["analysis_definitions"]["without_C_PL5D"][part] for n in P]
    fall.append(1 - tune["with"][part]["chi2"] / tune["without"][part]["chi2"])
    row(f"pl-chi2fall-{part}-lo", f"{100 * min(fall):.1f}", "Table IV with / without C_PL"); row(f"pl-chi2fall-{part}-hi", f"{100 * max(fall):.1f}", "same")
for r in rows: print(" | ".join(r))
print("DIFFS:", sum(r[-1] != "ok" for r in rows), "of", len(rows))
