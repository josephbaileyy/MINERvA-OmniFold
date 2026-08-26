#!/usr/bin/env python3
"""5D (pt,pz,Eavail,q3,W) unified-throw covariance driver.

Thin wrapper over unified_throw_cov.py (the nd-general rigorous unified throw).
The ONLY 5D-specific change needed is the truth-denom column assembly inside
_xsec_for_weights: the upstream copy stops at td_q3 (`td_cols[:len(edges)]` with
no td_W), so for len(edges)==5 it would feed 4 denom coords to a 5-edge
histogramdd. We monkeypatch a td_W-aware _xsec_for_weights into the base module
(no in-place edit of the shared script); everything else -- do_throws,
do_blockunits, do_combine, the jitter null -- is inherited unchanged.

Usage mirrors unified_throw_cov.py, with --bank bank_uthrow_5d:
  python unified_throw_cov_5d.py --throws 8 --throw-offset 0 --seed 1000 \
      --bank bank_uthrow_5d --iters 5 --out uthrow5d_slab_0.npz
  python unified_throw_cov_5d.py --blockunits --block-knobs all --block-flux 0-99 ...
  python unified_throw_cov_5d.py --combine 'uthrow5d_slab_*.npz' \
      --block-slabs 'block5d_*.npz' --bank bank_uthrow_5d --null \
      --out-root uq_5d/unified_throw_cov_5d.root
"""
import sys
from pathlib import Path

import numpy as np

# OI-136 REPAIR, 2026-08-22, authorized by Joseph's ruling 18 (DECISION-20260822-joseph-b1-lift-and-clause-c.md)
# and required by REVIEW-CONTRACT-20260822-k0-execution-integrity.md B-1. THE IMPORT ROOT IS DERIVED
# FROM THIS FILE, never from the hardcoded cluster root that used to stand here. An absolute
# `insert(0, ...)` executes THAT tree's modules whichever checkout launched this entrypoint, and
# PYTHONPATH cannot outrank position 0 -- so deployment parity can report every pinned file CURRENT
# while the interpreter imports a different file entirely. That is OI-136's measured cause on run
# 57266000_0 (3 h 08 m of A100 against a tree 211 commits behind).
# NO ABSOLUTE FALLBACK, deliberately: a fallback is the hardcode wearing a flag, and it would restore
# the defect silently on the one tree where it matters. Same idiom and the same reason as the OI-136
# pilot repair at `uq_fps/corrected/test_fps_corrected_uq.py`, `tests/test_p4_repair.py:14` and
# `pet/combine_cstat_bkgsub_100rep.py:78`.
# `parents[1]` is the repository root seen from `nd-unfolding/`: the inserts below cover BOTH
# `2d-unfolding/` and `nd-unfolding/` (`omnifold_nn_core`, `xsec_nd`, and `unified_throw_cov`,
# which carries a rooted insert of its own and is repaired in the same commit for that reason).
_REPO = str(Path(__file__).resolve().parents[1])
for _p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import unified_throw_cov as base


def _xsec_for_weights_5d(d, edges, wt_sig, wr_sig, wt_td, iters, seed, flux=None):
    """td_W-aware copy of compare_unified_throw._xsec_for_weights (5D-ready).
    Identical to the upstream function except the truth-denom coordinate stack
    appends td_W when the binning is 5D.

    Being a copy is exactly why J28 had to be fixed here separately: the `flux`
    override must be honoured in this kernel too, or the 5D throws keep dividing
    every Flux universe by the CV integral."""
    from omnifold_nn_core import omnifold_loop
    from xsec_nd import extract_cross_section_nd
    MCgen, MCreco, measured = d["MCgen"], d["MCreco"], d["measured"]
    pass_reco, pass_truth = d["pass_reco"], d["pass_truth"]
    w_pull, w_push = omnifold_loop(
        MCgen, MCreco, measured, pass_reco, pass_truth, np.ones(len(measured), bool),
        iters, kind="lgbm", MCgen_weights=wt_sig, MCreco_weights=wr_sig,
        measured_weights=d["measured_weights"], seed=seed, verbose=False)
    m = pass_truth
    sample = np.column_stack([MCgen[m, a] for a in range(MCgen.shape[1])])
    bins = [np.asarray(e, float) for e in edges]
    unfold_nd, _ = np.histogramdd(sample, bins=bins, weights=w_push * wt_sig[m])
    of_in, _ = np.histogramdd(sample, bins=bins, weights=wt_sig[m])
    # truth-denom coords matched to the binning dimensionality (pt,pz,ea,q3,W)
    td_cols = [d["td_pt"], d["td_pz"]]
    if "td_ea" in d:
        td_cols.append(d["td_ea"])
    if len(edges) >= 4 and "td_q3" in d:
        td_cols.append(d["td_q3"])
    if len(edges) >= 5 and "td_W" in d:
        td_cols.append(d["td_W"])
    denom_nd, _ = np.histogramdd(np.column_stack(td_cols[:len(edges)]),
                                 bins=bins, weights=wt_td)
    completeness = np.zeros_like(of_in)
    nz = denom_nd > 0
    completeness[nz] = of_in[nz] / denom_nd[nz]
    xsec, _ = extract_cross_section_nd(unfold_nd, completeness,
                                       d["flux"] if flux is None else flux,
                                       float(d["data_pot"]), float(d["n_nucleons"]), edges)
    return xsec


# install the 5D-aware kernel into the base module (do_throws/blockunits/combine
# all resolve _xsec_for_weights from base's globals)
base._xsec_for_weights = _xsec_for_weights_5d


if __name__ == "__main__":
    base.main()
