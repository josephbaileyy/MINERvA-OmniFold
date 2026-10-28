"""Reviewer: B2 (head path) on the amended fixture when C1 - C0 carries the real block's laptop-vs-S1 difference
pattern (elementwise relative), plus its transpose/sign variants."""
import sys, io, contextlib, tempfile, json
from pathlib import Path
S = Path(sys.argv[1]); ROOT = S / "head/nd-unfolding"; WT = Path(sys.argv[2])
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import numpy as np
import s1_assemble as sa, fd_flux_boot as FB, fd_g_diag as D, test_fd_flux_boot as T
F = WT / "docs/orchestration/state/measurement-paper/5d-community-20261024"
U = sa.functional_matrix(sa.fine_map(WT / "nd-unfolding/pv-ladder/readouts/h2_definition.json"))
X = np.array([U @ sa.xs(F / f"s1/readout/s1_assembly/S1_Flux_{u}.npz") for u in range(100)])
w = sa.flux_weights(S / "fetched/sorted_NuEConstraint_FHC_RHC_IMD.txt")
C0r = np.asarray(np.load(S / "fetched/s1_assembly.npz")["C_band_Flux"], float)
R = (sa.mat_cov(X, w) - C0r) / C0r
tree = T.BootTree(Path(tempfile.mkdtemp(dir=sys.argv[3])) / "t").write()
with contextlib.redirect_stdout(io.StringIO()):
    x = D.load(FB.build_args(tree.bargv), tree.bpins, tree.predictions)
_, carries = x.comps[0][1]
C0 = x.blocks_abs["band:Flux"]; Cg = x.Ct + (x.Cx if carries else 0)
def worst(delta):
    res = {}
    for spec in tree.predictions:
        cells, g, Vg = x.integ[spec["name"]]
        t, s = FB.chi2s(x.f, g, Vg, Cg + delta, cells)
        ref = x.grp[spec["name"]]
        res[spec["name"]] = (abs(t - ref["total"]["chi2"]) / ref["total"]["chi2"], abs(s - ref["shape_only"]["chi2"]) / ref["shape_only"]["chi2"])
    return res
for k in (1, -1, 10, 100):
    r = worst(k * R * C0)
    print(f"x{k}: worst total {max(v[0] for v in r.values()):.2e}, shape-only {max(v[1] for v in r.values()):.2e}")
