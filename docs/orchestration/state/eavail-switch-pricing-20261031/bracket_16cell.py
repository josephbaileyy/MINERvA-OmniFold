"""Per-charged-pion first-order estimate of the 139.57 MeV switch on the 16 H2 cells, from committed arrays only.

Assumptions (stated in the record): (1) the unfolded fine-grid density is uniform inside the fine E_avail bin
[0.8, 1.5) GeV; (2) every event there carries exactly one charged pion (results scale linearly with the mean
multiplicity at E_avail ~ 0.8 GeV, which no committed record gives); (3) the unfolded result moves as the truth
coordinate does (no change in the unfolding itself). Operand: the mean of the 20 committed seed-42 replicas.
Usage: python3 -I -B bracket_16cell.py <repo>
"""
import glob, hashlib, json, sys
from pathlib import Path
import numpy as np
R = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(R / "nd-unfolding"))
import s1_assemble as sa, s5p_stage1_inspect as s1
D = R / "nd-unfolding/pv-ladder/readouts/h2_definition.json"
fm = sa.fine_map(D)                                   # fine flat -> reporting cell (-1 unreported)
shape = s1.fine_shape(); vol = s1.fine_volume()
files = sorted(glob.glob(str(R / "docs/orchestration/state/measurement-paper/5d-community-20261024/s1/readout/s1_assembly/data_b*_j*.npz")))
X = np.mean([np.load(f)["xsec_flat"] for f in files], axis=0) * vol   # fine-cell integrals
idx = np.unravel_index(np.arange(X.size), shape)
E = np.asarray(s1.FINE["eavail"]); k08 = int(np.where(np.isclose(E, 0.8))[0][0])   # first fine bin above 0.8
up = idx[2] == k08
flat = np.ravel_multi_index
lo = flat((idx[0][up], idx[1][up], np.full(up.sum(), k08 - 1), idx[3][up], idx[4][up]), shape)
frac = 4.57 / ((E[k08 + 1] - E[k08]) * 1000.0)        # per pion, uniform density
f = np.zeros(16); np.add.at(f, fm[fm >= 0], X[fm >= 0])
# second variant: the density at 0.8 linearly interpolated between the two adjacent bins' mean densities (centres)
wl, wu = E[k08] - E[k08 - 1], E[k08 + 1] - E[k08]
cl_, cu_ = 0.5 * (E[k08 - 1] + E[k08]), 0.5 * (E[k08] + E[k08 + 1])
def moves(variant):
    d = np.zeros(16)
    for i_up, i_lo in zip(np.where(up)[0], lo):
        cu, cl = fm[i_up], fm[i_lo]
        if cu < 0 and cl < 0 or cu == cl:
            continue
        if variant == "uniform":
            m = frac * X[i_up]
        else:
            rl, ru = X[i_lo] / wl, X[i_up] / wu                      # integral per GeV of E_avail
            rho = rl + (ru - rl) * (E[k08] - cl_) / (cu_ - cl_)
            m = max(rho, 0.0) * 4.57e-3
        if cu >= 0: d[cu] -= m
        if cl >= 0: d[cl] += m
    return d
d = moves("uniform"); d2 = moves("interp")
print("files", len(files), "per-pion fraction of the [0.8,1.5) bin", round(frac, 6))
print("defn sha256", hashlib.sha256(D.read_bytes()).hexdigest()[:16])
dp = json.loads((R / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/data-product/fd_data_product.json").read_text())
rs = np.asarray(dp["relative_sigma"]["C_total_plus_C_resp"])
print("cell uniform interp sigma_rel(C_total+C_resp) uniform/sigma interp/sigma")
for c in range(16):
    print(f"R{c:02d} {100 * d[c] / f[c]:+.3f}% {100 * d2[c] / f[c]:+.3f}% {100 * rs[c]:.2f}% {d[c] / f[c] / rs[c]:+.3f} {d2[c] / f[c] / rs[c]:+.3f}")
print("max |rel| interp", f"{100 * np.max(np.abs(d2 / f)):.3f}%")
print("max |rel|", f"{100 * np.max(np.abs(d / f)):.3f}%", "sum of moves / total", f"{100 * np.abs(d).sum() / 2 / f.sum():.4f}%")
# the fine E_avail marginal (all reported fine cells, i.e. fm >= 0): per pion, uniform density in each upper bin
M = np.array([X[(idx[2] == k) & (fm >= 0)].sum() for k in range(len(E) - 1)])
mv = np.array([4.57 / ((E[k + 1] - E[k]) * 1000.0) * M[k] for k in range(len(E) - 1)])   # out of bin k, downward
mv[0] = 0.0                                                                               # bin 0 has no lower bin
net = -mv + np.append(mv[1:], 0.0)
print("fine E_avail bin, integral share, net change per pion (uniform)")
for k in range(len(E) - 1):
    print(f"[{E[k]:g},{E[k+1]:g}) {100 * M[k] / M.sum():.2f}% {100 * net[k] / M[k]:+.3f}%")
