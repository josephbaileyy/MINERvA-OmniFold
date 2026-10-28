import sys, json
from pathlib import Path
S = Path(sys.argv[1]); WT = Path(sys.argv[2]); sys.path[:0] = [str(S / "head/nd-unfolding")]
import numpy as np, s1_assemble as sa
F = WT / "docs/orchestration/state/measurement-paper/5d-community-20261024"
U = sa.functional_matrix(sa.fine_map(WT / "nd-unfolding/pv-ladder/readouts/h2_definition.json"))
X = np.array([U @ sa.xs(F / f"s1/readout/s1_assembly/S1_Flux_{u}.npz") for u in range(100)])
w = sa.flux_weights(S / "fetched/sorted_NuEConstraint_FHC_RHC_IMD.txt")
z = np.load(S / "fetched/s1_assembly.npz"); f = np.asarray(z["f"], float)
rs = np.asarray(json.loads((F / "s1/readout/s1_assembly.json").read_text())["relative_sigma"]["flux"], float)
s = np.sqrt(np.diag(sa.mat_cov(X, w))) / f
print("max |sigma - readout|", np.abs(s - rs).max(), "max rel", (np.abs(s - rs) / rs).max())
