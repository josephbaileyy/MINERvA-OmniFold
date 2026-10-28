"""Reviewer probe: how B2 (head tool's path) responds to a rebuild that differs from C0 in the last bits."""
import sys, tempfile, io, contextlib
from pathlib import Path
from unittest import mock
ROOT = Path(sys.argv[1]) / "head" / "nd-unfolding"
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import numpy as np
import fd_flux_boot as FB, fd_g_diag as D, s1_assemble as sa, test_fd_flux_boot as T
tree = T.BootTree(Path(tempfile.mkdtemp(dir=sys.argv[2])) / "t").write()
with contextlib.redirect_stdout(io.StringIO()):
    x = D.load(FB.build_args(tree.bargv), tree.bpins, tree.predictions)
    w = FB.weights(FB.build_args(tree.bargv).flux_constraint, x.s1j, tree.bpins) if False else tree.w
_, carries = x.comps[0][1]
C0 = x.blocks_abs["band:Flux"]
C1 = FB.replicate_block(tree.X, tree.w, np.arange(100))
print("C1 == C0 bitwise:", np.array_equal(C1, C0), "max|C1-C0|/max|C0|", np.abs(C1 - C0).max() / np.abs(C0).max())
Cg = x.Ct + (x.Cx if carries else 0)
rng = np.random.default_rng(7)
def worst(delta):
    out = 0.0
    for spec in tree.predictions:
        cells, g, Vg = x.integ[spec["name"]]
        got = FB.chi2s(x.f, g, Vg, Cg + delta, cells)
        ref = x.grp[spec["name"]]
        want = (ref["total"]["chi2"], ref["shape_only"]["chi2"])
        out = max(out, max(abs(a - b) / abs(b) for a, b in zip(got, want)))
    return out
print("TOL", FB.TOL, "REPRO", FB.REPRO)
for eps in (1.1e-16, 2.2e-16, 1e-15, 1e-14, 1e-13, 1e-12):
    ws = []
    for trial in range(50):
        E = rng.normal(size=(16, 16)); E = (E + E.T) / 2
        C1p = C0 * (1 + eps * E)
        ws.append(worst(C1p - C0))
    ws = np.array(ws)
    print(f"eps {eps:.1e}: B2 worst over 50 draws: median {np.median(ws):.2e}, max {ws.max():.2e}, frac>0 {np.mean(ws>0):.2f}")
# a rebuild one TOL off at max entry (B1's edge): uniform relative shift of entire block
for eps in (FB.TOL,):
    E = rng.normal(size=(16, 16)); E = (E + E.T) / 2; E /= np.abs(E).max()
    d = eps * np.abs(C0).max() * E
    print(f"B1-edge perturbation (|C1-C0|max = TOL*max|C0|): B2 worst {worst(d):.2e}")
