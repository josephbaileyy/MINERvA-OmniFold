"""Reviewer: the real flux block's regime from the committed universes, the constraint weights and S1's npz."""
import sys, json
from pathlib import Path
S = Path(sys.argv[1]); ROOT = S / "head/nd-unfolding"; WT = Path(sys.argv[2])
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import numpy as np
import s1_assemble as sa, fd_flux_boot as FB
F = WT / "docs/orchestration/state/measurement-paper/5d-community-20261024"
fm = sa.fine_map(WT / "nd-unfolding/pv-ladder/readouts/h2_definition.json")
U = sa.functional_matrix(fm)
X = np.array([U @ sa.xs(F / f"s1/readout/s1_assembly/S1_Flux_{u}.npz") for u in range(100)])
w = sa.flux_weights(S / "fetched/sorted_NuEConstraint_FHC_RHC_IMD.txt")
z = np.load(S / "fetched/s1_assembly.npz", allow_pickle=False)
print("npz keys sample", [k for k in z.files if "Flux" in k or k in ("f", "U")][:6])
C0 = np.asarray(z["C_band_Flux"], float)
C1 = sa.mat_cov(X, w)
print("n_eff", FB.n_eff(w), "sum", w.sum())
print("real B1: bitwise", np.array_equal(C1, C0), "max|C1-C0|/max|C0|", np.abs(C1 - C0).max() / np.abs(C0).max(),
      "max ulps", np.max(np.abs(C1 - C0) / np.spacing(np.abs(C0))))
fkey = [k for k in z.files if k in ("f", "x", "f_cells")]
s1j = json.loads((F / "s1/readout/s1_assembly.json").read_text())
cmodel = json.loads((WT / "nd-unfolding/pv-ladder/readouts/cmodel_5d.json").read_text())
f = np.asarray(cmodel["x"], float) if "x" in cmodel else None
print("f from cmodel", None if f is None else f.shape)
def regime(C, f, label):
    Cr = C / np.outer(f, f)
    r = Cr / np.sqrt(np.outer(np.diag(Cr), np.diag(Cr)))
    off = r[np.triu_indices(16, 1)]
    e = np.linalg.eigvalsh(Cr)
    q = np.percentile(off, [0, 5, 25, 50, 75, 95, 100])
    print(f"{label}: corr quantiles 0/5/25/50/75/95/100 % {np.round(q, 4).tolist()}; frac>=0.97 {np.mean(off >= 0.97):.3f}; "
          f"lmin {e[0]:.3e} lmax {e[-1]:.3e}; sigma/f range {np.sqrt(np.diag(Cr)).min():.4f}-{np.sqrt(np.diag(Cr)).max():.4f}")
    return off
regime(C1, f, "real rebuild")
rs = np.asarray(s1j["relative_sigma"].get("band:Flux", s1j["relative_sigma"].get("C_band_Flux", [np.nan]*16)), float) if isinstance(s1j["relative_sigma"], dict) else None
print("relative_sigma keys", list(s1j["relative_sigma"].keys())[:8] if isinstance(s1j["relative_sigma"], dict) else type(s1j["relative_sigma"]))
if rs is not None and np.all(np.isfinite(rs)):
    print("sigma vs readout max rel diff", np.max(np.abs(np.sqrt(np.diag(C1)) / f - rs) / rs))
import test_fd_flux_boot as T, tempfile
tree = T.BootTree(Path(tempfile.mkdtemp(dir=sys.argv[3])) / "t")
regime(tree.blocks["band:Flux"], tree.f, "amended fixture")
