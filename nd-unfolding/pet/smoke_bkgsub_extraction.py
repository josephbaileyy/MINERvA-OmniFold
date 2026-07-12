#!/usr/bin/env python3
"""Phase-1 end-to-end fixture: drive the corrected bkgsub 5D point-cloud input
all the way to PET cross-section extraction, under the ROOT environment.

The corrected input differs from the unsubtracted one ONLY in
`measured_weights` (the training target); the extraction (`PETxsec5D`) bins the
MC side (`truth_scalars`, `w_truth`, `pass_*`, W spliced row-aligned from
`of_inputs_5d`) with the trained `w_push`. So this fixture proves the corrected
npz is structurally consumable by the extraction machinery -- it must pass the
W-source alignment gate, anchor completeness, load flux, and bin a finite, full
5D cross section. It uses SYNTHETIC unit push-weights (no GPU training): with
w_push == 1 the result is the prior (MC) cross section, a valid finite plumbing
check. The real trained nominal is Phase 2.

Modes:
  --tiny   self-contained synthetic mini-input (fast; proves PETxsec5D mechanics)
  (default) the real corrected npz + of_inputs_5d W-source (a few minutes)

Run under root_6_28 (PyROOT required):
  python3 pet/smoke_bkgsub_extraction.py --tiny
  python3 pet/smoke_bkgsub_extraction.py
"""
import argparse
import os
import sys
import tempfile

import numpy as np

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
_ND = os.path.join(_REPO, "nd-unfolding")
if _ND not in sys.path:
    sys.path.insert(0, _ND)


def _synth_weights(n, path, seed=0):
    """A minimal push-weights npz (unit weights, full-coverage indices)."""
    np.savez(path, w_push=np.ones(n, dtype=np.float64),
             mc_indices=np.arange(n, dtype=np.int64),
             pass_truth=np.ones(n, dtype=bool), model="synthetic_unit")


def _build_tiny(tmp):
    """A tiny synthetic PET pc + row-aligned W-source that PETxsec5D accepts."""
    rng = np.random.default_rng(0)
    n = 4000
    edges = [np.array([0.0, 0.5, 4.5]), np.array([1.5, 3.0, 60.0]),
             np.array([0.0, 1.0, 100.0]), np.array([0.0, 1.0, 100.0]),
             np.array([0.0, 2.0, 100.0])]
    truth4 = np.column_stack([rng.uniform(0.05, 4.4, n), rng.uniform(1.6, 59, n),
                              rng.uniform(0.05, 90, n), rng.uniform(0.05, 90, n)])
    W = rng.uniform(0.05, 90, n)
    w_truth = rng.uniform(0.5, 2.0, n)
    pass_truth = rng.uniform(size=n) > 0.2
    pass_reco = pass_truth & (rng.uniform(size=n) > 0.3)
    pc = os.path.join(tmp, "pc_tiny.npz")
    np.savez(pc, truth_scalars=truth4.astype(np.float32), w_truth=w_truth,
             pass_truth=pass_truth, pass_reco=pass_reco,
             edges_0=edges[0], edges_1=edges[1], edges_2=edges[2], edges_3=edges[3],
             data_pot=np.asarray(1.057e21))
    wsrc = os.path.join(tmp, "wsrc_tiny.npz")
    np.savez(wsrc, MCgen=np.column_stack([truth4, W]).astype(np.float64),
             w_truth=w_truth, edges_4=edges[4])
    wts = os.path.join(tmp, "w_tiny.npz")
    _synth_weights(n, wts)
    return pc, wsrc, wts


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pc", default=os.path.join(_ND, "of_inputs_pc_fullcloud_bkgsub_5d.npz"))
    ap.add_argument("--w-source", default=os.path.join(_ND, "of_inputs_5d.npz"))
    ap.add_argument("--weights", default=None,
                    help="push-weights npz; default = synthetic unit weights")
    ap.add_argument("--mcfile", default=f"{_REPO}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root")
    ap.add_argument("--flux-hist", default="pTmu_reweightedflux_integrated")
    ap.add_argument("--comp-ref", default=os.path.join(_ND, "products/5d/xsec_5d_MEFHC_5iter_lgbm.root"))
    ap.add_argument("--tiny", action="store_true")
    args = ap.parse_args()

    import ROOT  # noqa: F401  (fail fast if PyROOT missing)
    from pet_systematics_5d import PETxsec5D, total_xsec

    tmp = tempfile.mkdtemp(prefix="pet_bkgsub_smoke_")
    if args.tiny:
        pc, wsrc, wts = _build_tiny(tmp)
        comp_ref = None
        print("[smoke] TINY synthetic mode")
    else:
        pc, wsrc = args.pc, args.w_source
        wts = args.weights
        if wts is None:
            n = int(np.load(pc)["w_truth"].shape[0])
            wts = os.path.join(tmp, "w_unit.npz")
            _synth_weights(n, wts)
            print(f"[smoke] REAL corrected input; synthetic unit push-weights (n={n})")
        comp_ref = args.comp_ref if os.path.exists(args.comp_ref) else None
        print(f"[smoke] pc={os.path.basename(pc)} w_source={os.path.basename(wsrc)} "
              f"comp_ref={'yes' if comp_ref else 'none'}")

    pet = PETxsec5D(pc, wts, args.mcfile, args.flux_hist, wsrc, comp_ref)
    xs = pet.xsec(None)
    x5 = xs.reshape(pet.shape, order="C")
    total = total_xsec(x5, pet.edges)

    finite = bool(np.isfinite(xs).all())
    nonneg = bool((xs >= 0).all())
    print(f"[smoke] xsec shape={pet.shape} nbins={xs.size} finite={finite} "
          f"nonneg={nonneg} total_sigma={total:.4e} cm^2/nucleon "
          f"(unit-push = prior/MC xsec)")
    ok = finite and nonneg and xs.size == int(np.prod(pet.shape)) and total > 0.0
    print(f"[smoke] {'PASS' if ok else 'FAIL'}: corrected bkgsub 5D input reaches "
          f"PET cross-section extraction end-to-end under ROOT.")
    sys.exit(0 if ok else 5)


if __name__ == "__main__":
    main()
