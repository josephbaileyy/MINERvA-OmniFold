#!/usr/bin/env python3
"""The cause of the 3D STOP (FD-FLUX-BOOT-DECLARATION-AMENDMENT-1.md section 1), measured on synthetic fixtures only.

For each prediction of the pre-amendment fixture (the declaration's BootTree universes: common 0.035, tilt 0.01, noise
0.004) and of the amended one, it prints:
* total and shape-only chi2 as the pre-amendment tool computed them (M relative to f, then + 100 * 11^T, Cholesky),
  against Stage G's own readout value (absolute units, M + 100 f f^T);
* the condition numbers of M and of the shape-only matrix;
* the exact chi2 (rational arithmetic) of the float problem in each representation, and Stage G's float value against
  its own exact one;
* the shape-only and total chi2's change when M is perturbed by 1e-16 relative per entry (the problem's own
  conditioning);
* the amended tool's B2 reproduction.

    python3 -B diagnose.py <repo>    (run from anywhere; TMPDIR is used for the fixtures)
"""
import sys
import tempfile
from fractions import Fraction as Fr
from pathlib import Path
from unittest import mock

REPO = Path(sys.argv[1]).resolve()
sys.path[:0] = [str(REPO / "nd-unfolding"), str(REPO / "nd-unfolding/tests")]
import numpy as np  # noqa: E402
import fd_flux_boot as FB  # noqa: E402
import fd_g_compare as G  # noqa: E402
import fd_g_diag as D  # noqa: E402
import fd_g_followup as F  # noqa: E402
import s1_assemble as sa  # noqa: E402
import test_fd_flux_boot as T  # noqa: E402


class OldTree(T.BootTree):
    """The declaration's fixture before amendment 1: the same construction with its original universe widths."""

    def __init__(self, root, seed=0, scale=1e-39):
        T.DiagTree.__init__(self, root, seed=seed, scale=scale)
        rng = np.random.default_rng(seed + 200)
        common, tilt = rng.normal(0, 0.035, 100), rng.normal(0, 0.01, 100)
        rel = common[:, None] + tilt[:, None] * np.linspace(-1, 1, 16)[None, :] + rng.normal(0, 0.004, (100, 16))
        self.Xint = self.f * (1 + rel)
        self.w = T.heavy_weights()
        self.universe_fine = [self.fine_of(x) for x in self.Xint]
        self.X = np.array([self.U @ v for v in self.universe_fine])
        self.blocks["band:Flux"] = sa.mat_cov(self.X, self.w)
        self.Ce = sum(self.blocks[k] for k in sorted(self.blocks))
        self.Ct = self.Ce + self.Cma


def exact_quad(M, d):
    n = len(d)
    A = [[Fr(float(M[i][j])) for j in range(n)] + [Fr(float(d[i]))] for i in range(n)]
    for c in range(n):
        p = next(r for r in range(c, n) if A[r][c] != 0)
        A[c], A[p] = A[p], A[c]
        for r in range(c + 1, n):
            k = A[r][c] / A[c][c]
            if k:
                A[r] = [a - k * b for a, b in zip(A[r], A[c])]
    y = [Fr(0)] * n
    for i in range(n - 1, -1, -1):
        y[i] = (A[i][n] - sum(A[i][j] * y[j] for j in range(i + 1, n))) / A[i][i]
    return float(sum(Fr(float(d[i])) * y[i] for i in range(n)))


def relative_chi2s(d, M):
    """The pre-amendment tool's arithmetic: M relative to f, then + 100 * 11^T."""
    out = []
    for mat in (M, M + G.SHAPE_LAMBDA * np.ones_like(M)):
        y = np.linalg.solve(np.linalg.cholesky(mat), d)
        out.append(float(y @ y))
    return out


def flux_regime(tree):
    C = tree.blocks["band:Flux"] / np.outer(tree.f, tree.f)
    r = C / np.sqrt(np.outer(np.diag(C), np.diag(C)))
    off = r[~np.eye(16, dtype=bool)]
    e = np.linalg.eigvalsh(C)
    return f"correlations {off.min():.3f}-{off.max():.4f}, lambda_min {e[0]:.3e}, lambda_max {e[-1]:.3e}, n_eff {FB.n_eff(tree.w):.2f}"


def main():
    print(f"numpy {np.__version__}")
    rng = np.random.default_rng(0)
    for label, cls in (("pre-amendment fixture", OldTree), ("amended fixture", T.BootTree)):
        tree = cls(Path(tempfile.mkdtemp(prefix="diag3d-")) / "t").write()
        print(f"\n== {label}: {flux_regime(tree)}")
        with mock.patch("sys.stdout"):
            x = D.load(FB.build_args(tree.bargv), tree.bpins, tree.predictions)
        _, carries = x.comps[0][1]
        for spec in tree.predictions:
            names, d, B0, _ = F.prediction_blocks(x, spec, carries)
            cells, g, Vg = x.integ[spec["name"]]
            i = np.asarray(cells)
            ref = x.grp[spec["name"]]
            Mrel = sum(B0.values())
            t_rel, s_rel = relative_chi2s(d, Mrel)
            Mabs = (x.Ct + x.Cx)[np.ix_(i, i)] + np.diag(Vg[i])
            fs = x.f[i]
            ex_abs = exact_quad(Mabs + G.SHAPE_LAMBDA * np.outer(fs, fs), (x.f - g)[i])
            ex_rel = exact_quad(Mrel + G.SHAPE_LAMBDA * np.ones_like(Mrel), d)
            E = rng.normal(size=Mrel.shape)
            E = (E + E.T) / 2
            pt, ps = relative_chi2s(d, Mrel * (1 + 1e-16 * E))
            k = lambda M: (lambda e: e[-1] / e[0])(np.linalg.eigvalsh(M))
            e = lambda a, b: abs(a - b) / abs(b)
            print(f"{spec['name']:10s} pre-amendment vs Stage G: total {e(t_rel, ref['total']['chi2']):.1e}, shape-only "
                  f"{e(s_rel, ref['shape_only']['chi2']):.1e} | cond M {k(Mrel):.1e}, shape-only matrix "
                  f"{k(Mrel + 100 * np.ones_like(Mrel)):.1e} | exact relative vs exact absolute {e(ex_rel, ex_abs):.1e}; "
                  f"Stage G vs its exact {e(ref['shape_only']['chi2'], ex_abs):.1e} | M x (1 + 1e-16 E): total "
                  f"{e(pt, t_rel):.1e}, shape-only {e(ps, s_rel):.1e}")
        with mock.patch.object(sa, "CONSTRAINT_SHA256", tree.bpins["constraint"]), mock.patch("sys.stdout"):
            FB.run(FB.build_args(tree.bargv), tree.bpins, tree.predictions)
        import json
        out = json.loads((tree.out / "boot.json").read_text())
        print("amended tool, B2 relative_difference:", {k_: v["relative_difference"] for k_, v in out["identity"].items()})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
