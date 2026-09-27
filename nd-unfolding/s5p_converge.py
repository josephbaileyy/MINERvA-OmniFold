#!/usr/bin/env python3
"""s5p Stage 2: the fixed convergence study -- one traced noise-free unfold to many iterations.

Contract ``stages.2_construction_questions.items.convergence_observability`` of
``docs/orchestration/state/s5p/contract.json`` (frozen design in contract amendment 2). This is
``s5e_trace.main`` (the s5e diagnosis instrumentation: the production loop observed through the
estimator factory, every per-iteration weight rebuild checked bitwise, the final unfold recomputed) with
three declared additions and nothing else:

* the reported functionals are the s5c set (42 (E_avail,W) cells, EW_all_ones, the 109 supported cells of
  partition J, the total) FOLLOWED BY the 32 cells of the s5p reporting partition H2 (contract amendment
  1, RD2), each a cell integral with the fine-bin volumes, as the J rows are built;
* the 5D reco-level fold snapshots add iterations 50, 75, 100, 125, 150, 175 and 200 to s5e's list;
* the multi-dimensional truth ``ratio_nd`` (``s5e_deform``) is available, so W3-type 3D ratios can be run.

Per iteration it therefore records the truth functionals of ``w_push`` and ``w_pull`` (EW, J and H2),
the (E_avail,W) reco-level folds and, at the snapshots, the 5D folds beside the measured side, the folded
truth and the prior: the inputs of the detector-level checks (fold agreement, explained fraction,
residual visibility at the analysis exposure).

MEASURES: the noise-free response of one estimator to one declared truth as a function of iteration.
CANNOT AUTHORIZE: an optimality claim from a finite scan, a stopping rule by itself, a coverage verdict.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import project_cov_nd as pc  # noqa: E402
import s5c_coverage  # noqa: E402
import s5e_deform  # noqa: E402
import s5e_trace  # noqa: E402
import s5n_pseudo  # noqa: E402
import s5p_truths  # noqa: E402

H2_EDGES = {"pt": [0.0, 0.7, 4.5], "pz": [1.5, 4.5, 60.0], "eavail": [0.0, 0.8, 100.0],
            "q3": [0.0, 2.0, 100.0], "W": [0.0, 1.8, 100.0]}
EXTRA_SNAPSHOTS = (50, 75, 100, 125, 150, 175, 200)


def h2_rows() -> tuple[np.ndarray, list[str]]:
    """One row per H2 cell over the full fine grid: the fine-bin volume where the fine cell's centre
    lies in the coarse cell (the construction of s5c_coverage.reported_functionals' J rows)."""
    axes = s5c_coverage.AXES
    shape = tuple(len(pc.AXIS_EDGES[a]) - 1 for a in axes)
    n = int(np.prod(shape))
    idx = np.unravel_index(np.arange(n), shape)
    vol = np.ones(n)
    cidx = []
    for k, ax in enumerate(axes):
        fine = np.asarray(pc.AXIS_EDGES[ax], float)
        vol *= np.diff(fine)[idx[k]]
        ce = np.asarray(H2_EDGES[ax], float)
        if not all(np.any(np.isclose(fine, x)) for x in ce):
            raise ValueError(f"H2 edge of {ax} is not a fine edge")
        centres = 0.5 * (fine[:-1] + fine[1:])[idx[k]]
        cidx.append(np.clip(np.searchsorted(ce, centres, side="right") - 1, 0, len(ce) - 2))
    cshape = tuple(len(H2_EDGES[a]) - 1 for a in axes)
    cell = np.ravel_multi_index(cidx, cshape)
    ncell = int(np.prod(cshape))
    return np.vstack([np.where(cell == c, vol, 0.0) for c in range(ncell)]), [f"H2_{c}" for c in range(ncell)]


def install() -> None:
    """The three declared additions (idempotent)."""
    if getattr(s5c_coverage.reported_functionals, "_s5p_h2", False):
        return
    s5e_deform.install_ratio_truth(s5n_pseudo)
    s5p_truths.install(s5n_pseudo)
    original = s5c_coverage.reported_functionals

    def with_h2(contract):
        U, names = original(contract)
        H, hn = h2_rows()
        return np.vstack([U, H]), list(names) + hn

    with_h2._s5p_h2 = True
    s5c_coverage.reported_functionals = with_h2
    snaps = tuple(sorted(set(s5e_trace.SNAPSHOTS) | set(EXTRA_SNAPSHOTS)))
    init = s5e_trace.Recorder.__init__
    defaults = list(init.__defaults__)
    defaults[-1] = snaps
    init.__defaults__ = tuple(defaults)
    base_digests = s5n_pseudo.code_digests

    def code_digests():
        return {**base_digests(), "s5p_converge.py": s5n_pseudo.sha256_path(Path(__file__).resolve()),
                "s5e_deform.py": s5n_pseudo.sha256_path(_ND / "s5e_deform.py")}

    s5n_pseudo.code_digests = code_digests


def install_checkpoints(out: Path, every: tuple[int, ...]) -> None:
    """Write the recorder's per-iteration truth functionals so far to ``<out>.partial.npz`` at the declared
    iterations (a DIAGNOSTIC checkpoint: the trace's bitwise checks and the final product are unchanged; a
    run that dies at its time limit keeps the iterations it completed)."""
    orig = s5e_trace.Recorder.on_iteration
    if getattr(orig, "_s5p_ckpt", False):
        return

    def on_iteration(self, k, w_pull, w_push, new_w):
        orig(self, k, w_pull, w_push, new_w)
        if k in every:
            o = self.out
            tmp = out.with_name(out.name + ".partial.tmp.npz")
            np.savez(tmp, k=np.array(k), fn_push=o["fn_push"][:k], fn_pull=o["fn_pull"][:k], fn_true_A=o["fn_true_A"],
                     reco_ew_push=o["reco_ew_push"][:k], reco_ew_true=o["reco_ew_true"], reco_ew_prior=o["reco_ew_prior"],
                     reco5d_true=o["reco5d_true"], reco5d_prior=o["reco5d_prior"])
            tmp.replace(out.with_name(out.name + ".partial.npz"))

    on_iteration._s5p_ckpt = True
    s5e_trace.Recorder.on_iteration = on_iteration


def main(argv=None) -> int:
    install()
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--out" in argv:
        install_checkpoints(Path(argv[argv.index("--out") + 1]), (10, 20, 30, 40, 50, 75, 100, 125, 150, 175))
    return s5e_trace.main(argv)


if __name__ == "__main__":
    sys.exit(main())
