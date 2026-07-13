#!/usr/bin/env python3
"""Extract one fully retrained PET bootstrap into a strict cross-section NPZ."""

import argparse
import os
import sys

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
_ROOT_PREFIX = os.environ.get("ROOT628_PREFIX",
                              "/global/homes/j/josephrb/.conda/envs/root_6_28")


def _ensure_pyroot():
    """PETxsec needs PyROOT, but the GPU launcher runs this under the TF-module
    python, which has none. Re-exec through the activated analysis env instead
    of dying after an hours-long training has already saved the weights. The
    activation (setup_salloc_env.sh) is required: a bare root_6_28 python
    without it segfaults in cling, and PATH order after activation is not
    trustworthy under a loaded TF module, so the interpreter is absolute."""
    try:
        import ROOT  # noqa: F401
        return
    except ImportError:
        pass
    if os.environ.get("PET_EXTRACT_REEXEC") == "1":
        raise SystemExit(f"[FAIL] PyROOT still unavailable after re-exec through "
                         f"{_ROOT_PREFIX}; run extraction in the root_6_28 env")
    os.environ["PET_EXTRACT_REEXEC"] = "1"
    os.environ["ROOT628_PREFIX"] = _ROOT_PREFIX
    cmd = (f'source "{_REPO}/setup_salloc_env.sh" >/dev/null; '
           'exec "${ROOT628_PREFIX}/bin/python3" "$@"')
    os.execv("/bin/bash", ["/bin/bash", "-c", cmd, "bash",
                           os.path.abspath(__file__)] + sys.argv[1:])


_ensure_pyroot()

import numpy as np

_ND = f"{_REPO}/nd-unfolding"
if _ND not in sys.path:
    sys.path.insert(0, _ND)

from pet_bootstrap import validate_full_replica_weights, write_xsec_replica


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dimension", type=int, choices=(4, 5), required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--weights", required=True,
                    help="retrained PET weights made with the same --bootstrap-seed")
    ap.add_argument("--out", required=True)
    ap.add_argument("--pc", default="of_inputs_pc.npz")
    ap.add_argument("--w-source", default="of_inputs_5d.npz")
    ap.add_argument("--mcfile", default=f"{_REPO}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root")
    ap.add_argument("--flux-hist", default="pTmu_reweightedflux_integrated")
    ap.add_argument("--comp-ref", default=None,
                    help="fixed nominal GBDT completeness anchor; dimension-specific default if omitted")
    args = ap.parse_args()

    with np.load(args.pc, allow_pickle=False) as pc, np.load(args.weights, allow_pickle=False) as w:
        n_events = int(pc["w_truth"].shape[0])
        validate_full_replica_weights(w, n_events, args.seed)

    if args.dimension == 4:
        from pet_systematics import PETxsec
        comp_ref = args.comp_ref or "products/4d/xsec_4d_MEFHC_5iter_lgbm.root"
        pet = PETxsec(args.pc, args.weights, args.mcfile, args.flux_hist, comp_ref)
    else:
        from pet_systematics_5d import PETxsec5D
        comp_ref = args.comp_ref or "products/5d/xsec_5d_MEFHC_5iter_lgbm.root"
        pet = PETxsec5D(args.pc, args.weights, args.mcfile, args.flux_hist,
                        args.w_source, comp_ref)

    xsec = pet.xsec(None).reshape(pet.shape, order="C")
    total = write_xsec_replica(args.out, args.seed, xsec, pet.edges)
    print(f"[pet-bootstrap] wrote seed={args.seed} shape={pet.shape} "
          f"total_xsec={total:.8e} -> {os.path.abspath(args.out)}")


if __name__ == "__main__":
    main()
