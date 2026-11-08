#!/usr/bin/env python3
"""Valid-region scoping (SCOPING.md section 2): resolved size of within-quadrant contrasts, covariance-only.

Reads no data central value. It never touches f in any input. From I4 it reads only the absolute matrix
C_total_plus_C_resp_plus_C_PL5D; from I3 only mnvtune_v1's g; from s1_assembly only relative_sigma.stat; from
stage1_inspect only mc/H2 and sigma_boot_data_R/H2 (data-bootstrap widths, no central values). It forms no
data-versus-prior quantity. Usage: python3 -I power_sim.py <repo>
"""
import itertools, json, math, sys
from pathlib import Path
import numpy as np

R = Path(sys.argv[1])
P = {"I3": "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/gencmp-e/rerun1/chain/chdefs/with/readout/fd_g_readout.json",
     "I4": "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/with-cpl/data-product/fd_data_product_cpl.json",
     "I5": "nd-unfolding/pv-ladder/readouts/h2_definition.json",
     "I6": "docs/orchestration/state/measurement-paper/5d-community-20261024/s1/readout/s1_assembly.json",
     "S1I": "docs/orchestration/state/s5p/stage1/stage1_inspect.json"}
J = {k: json.loads((R / v).read_text()) for k, v in P.items()}
AX = ("eavail", "q3", "W")
POS = 3.0
RQ = {"Q1": 0.099, "Q2": 0.046, "Q3": 0.170, "Q4": 0.212}  # OUTCOME-20261107-valid-region.md:107-110 (published yardstick)

# --- 16 cells: covariance in g-relative units, R = C / (g g^T); no f, V_P omitted
cells = [c["cell"] for c in J["I4"]["cells"]]
box = {c["cell"]: c["box"] for c in J["I4"]["cells"]}
C = np.asarray(J["I4"]["matrices"]["C_total_plus_C_resp_plus_C_PL5D"], float)
tune = [p for p in J["I3"]["predictions"] if p["name"] == "mnvtune_v1"][0]
g = dict(zip(tune["cells"], map(float, tune["g"])))
gv = np.asarray([g[c] for c in cells])
Rm = C / np.outer(gv, gv)
s_stat16 = dict(zip([c if isinstance(c, str) else "R%02d" % c for c in J["I6"]["meta"]["cells"]],
                    map(float, J["I6"]["relative_sigma"]["stat"])))
def quad(b):
    return {(True, True): "Q1", (True, False): "Q2", (False, True): "Q3", (False, False): "Q4"}[(b["pt"][1] <= 0.7, b["pz"][1] <= 4.5)]
print("== 16-cell within-quadrant contrasts: sigma(r_i - r_j) from the reported covariance (g-relative), and stat-only")
ratios = {q: [] for q in RQ}
for q in RQ:
    qc = [c for c in cells if quad(box[c]) == q]
    for a, b in itertools.combinations(qc, 2):
        i, j = cells.index(a), cells.index(b)
        st = math.sqrt(Rm[i, i] + Rm[j, j] - 2 * Rm[i, j])
        ss = math.hypot(s_stat16[a], s_stat16[b])
        ratios[q].append(st / ss)
        axes = [x for x in AX if list(box[a][x]) != list(box[b][x])]
        print(f"{q} {a}-{b} axes={','.join(axes):14s} 3sigma_tot={POS*st:.4f} 3sigma_stat={POS*ss:.4f} tot/stat={st/ss:.1f} "
              f"resolves r_Q={RQ[q]:.3f}: {'yes' if POS*st < RQ[q] else 'no'}")
k = {q: float(np.median(v)) for q, v in ratios.items()}
print("median tot/stat ratio per quadrant:", {q: round(v, 1) for q, v in k.items()})

# --- H2-32 boxes: stat floor from sigma_boot_data_R, single-axis edges inside a quadrant
m = J["S1I"]["mc"]["H2"]; sd = J["S1I"]["sigma_boot_data_R"]["H2"]; nrep = J["S1I"]["sigma_boot_data_R"]["n"]
h2map = J["I5"]["h2_to_reporting_cell"]
used = [b for b in range(32) if h2map[b] >= 0]
print(f"\n== H2 boxes used: {len(used)} (unreported {[b for b in range(32) if h2map[b] < 0]}); sigma_boot_data_R n={nrep}")
bits = lambda b: np.unravel_index(b, (2,) * 5)
QN = {(0, 0): "Q1", (0, 1): "Q2", (1, 0): "Q3", (1, 1): "Q4"}
edges = []
for a, b in itertools.combinations(used, 2):
    ba, bb = bits(a), bits(b)
    if ba[:2] != bb[:2]:
        continue
    diff = [AX[t - 2] for t in range(2, 5) if ba[t] != bb[t]]
    if len(diff) != 1:
        continue
    q = QN[(int(ba[0]), int(ba[1]))]
    within = h2map[a] == h2map[b]
    fl = math.hypot(sd[a], sd[b])
    edges.append((q, a, b, diff[0], within, fl))
for q, a, b, ax, within, fl in edges:
    est = fl * k[q]
    print(f"{q} box{a:02d}-box{b:02d} axis={ax:6s} {'NEW (inside R%02d)' % h2map[a] if within else 'across R%02d/R%02d' % (h2map[a], h2map[b]):22s} "
          f"purity {m['purity'][a]:.3f}/{m['purity'][b]:.3f} 3sigma_stat_floor={POS*fl:.4f} "
          f"3sigma_est(x{k[q]:.1f})={POS*est:.4f} r_Q={RQ[q]:.3f} resolvable_est={'yes' if POS*est < RQ[q] else 'no'}")
n_all = len(edges); n_new = sum(e[4] for e in edges)
lowp = sum(1 for e in edges if min(m['purity'][e[1]], m['purity'][e[2]]) < 0.1)
print(f"\nedges: {n_all} single-axis within-quadrant, {n_new} inside a merged cell (new); {lowp} touch a box with purity < 0.1")
for n in (n_new, n_all):
    p1 = 1 - (1 - math.erfc(3 / math.sqrt(2))) ** n
    # Bonferroni |z| for family-wise 0.05, two-sided
    lo, hi = 2.0, 6.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if n * math.erfc(mid / math.sqrt(2)) > 0.05: lo = mid
        else: hi = mid
    print(f"n={n}: P(any |z|>=3 | null, independent) = {p1:.3f}; Bonferroni two-sided 0.05 -> |z| >= {hi:.2f}")
