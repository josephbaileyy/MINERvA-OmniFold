#!/usr/bin/env python3
"""Phase 2: extract the corrected NOMINAL 5D PET cross section (no bootstrap).

The corrected nominal PET model is trained (unbootstrapped) on the bkgsub 5D
target; this bins its push weights into the 5D cross section via PETxsec5D
(the same estimator the C_stat/C_ml/systematic blocks will reference). Unlike
extract_bootstrap_replica.py this does NOT require the coherent-Poisson
bootstrap fields -- the nominal has none -- but it enforces full ordered MC
coverage (the strict-manifest contract) before extracting.

Run under root_6_28 (self-reexecs there if launched from the TF-module python):
  python3 pet/extract_nominal_bkgsub.py --weights <w.npz> --out <xsec.npz>
"""
import argparse
import json
import os
import sys

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
_ROOT_PREFIX = os.environ.get("ROOT628_PREFIX",
                              "/global/homes/j/josephrb/.conda/envs/root_6_28")


def _ensure_pyroot():
    """PETxsec5D needs PyROOT; the GPU launcher runs under the TF-module python
    which has none. Re-exec through the activated analysis env (bare root_6_28
    python segfaults in cling; PATH after activation is not trustworthy under a
    loaded TF module, so the interpreter is absolute). Mirrors
    extract_bootstrap_replica.py."""
    try:
        import ROOT  # noqa: F401
        return
    except ImportError:
        pass
    if os.environ.get("PET_EXTRACT_REEXEC") == "1":
        raise SystemExit(f"[FAIL] PyROOT still unavailable after re-exec through "
                         f"{_ROOT_PREFIX}")
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

from pet_bootstrap import write_xsec_replica  # noqa: E402


def validate_nominal_weights(weights_npz, n_events):
    """Full ordered MC coverage for a non-bootstrap nominal: w_push finite,
    mc_indices == arange(N). (No coherent-Poisson fields required.)"""
    w = np.load(weights_npz)
    if "w_push" not in w.files or "mc_indices" not in w.files:
        raise SystemExit(f"[FAIL] {weights_npz} missing w_push/mc_indices")
    wp = np.asarray(w["w_push"]); idx = np.asarray(w["mc_indices"])
    problems = []
    if wp.ndim != 1 or idx.ndim != 1:
        problems.append("w_push/mc_indices not 1D")
    if not (wp.size == idx.size == int(n_events)):
        problems.append(f"coverage {wp.size}/{idx.size} != n_events {n_events}")
    if not np.array_equal(idx, np.arange(int(n_events), dtype=idx.dtype)):
        problems.append("mc_indices not the ordered full-sample range (need --reweight-all)")
    if not np.all(np.isfinite(wp)):
        problems.append("w_push has non-finite values")
    if "mc_bootstrap_factor" in w.files:
        problems.append("nominal must NOT carry a bootstrap factor (this is a replica)")
    return {"n_events": int(n_events), "w_push_min": float(wp.min()),
            "w_push_max": float(wp.max()), "w_push_mean": float(wp.mean()),
            "problems": problems}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pc", default=os.path.join(_ND, "of_inputs_pc_fullcloud_bkgsub_5d.npz"))
    ap.add_argument("--w-source", default=os.path.join(_ND, "of_inputs_5d.npz"))
    ap.add_argument("--weights", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--summary", default=None)
    ap.add_argument("--mcfile", default=f"{_REPO}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root")
    ap.add_argument("--flux-hist", default="pTmu_reweightedflux_integrated")
    ap.add_argument("--comp-ref", default=os.path.join(_ND, "products/5d/xsec_5d_MEFHC_5iter_lgbm.root"))
    args = ap.parse_args()

    n_events = int(np.load(args.pc)["w_truth"].shape[0])
    wchk = validate_nominal_weights(args.weights, n_events)
    print(f"[nominal] weight coverage: n={wchk['n_events']} "
          f"w_push[min={wchk['w_push_min']:.4f} max={wchk['w_push_max']:.4f} "
          f"mean={wchk['w_push_mean']:.4f}] problems={wchk['problems']}", flush=True)
    if wchk["problems"]:
        raise SystemExit(f"[FAIL] nominal weight coverage: {wchk['problems']}")

    from pet_systematics_5d import PETxsec5D, total_xsec
    comp_ref = args.comp_ref if os.path.exists(args.comp_ref) else None
    pet = PETxsec5D(args.pc, args.weights, args.mcfile, args.flux_hist, args.w_source, comp_ref)
    x5 = pet.xsec(None).reshape(pet.shape, order="C")
    finite = bool(np.isfinite(x5).all())
    nonneg = bool((x5 >= 0).all())
    total = float(total_xsec(x5, pet.edges))
    n_reported = int((x5 > 0).sum())

    if not (finite and nonneg and total > 0):
        raise SystemExit(f"[FAIL] nominal xsec invalid: finite={finite} nonneg={nonneg} total={total}")

    write_xsec_replica(args.out, 0, x5, pet.edges)   # seed=0 = nominal marker

    summary = {
        "campaign": "PET bkgsub 5D corrected NOMINAL (Phase 2)",
        "pc": args.pc, "w_source": args.w_source, "weights": args.weights,
        "comp_ref": comp_ref, "out": os.path.abspath(args.out),
        "shape": list(pet.shape), "n_bins": int(np.prod(pet.shape)),
        "n_bins_populated": n_reported,
        "n_pass_truth": int(pet.pt.sum()), "n_pass_truth_reco": int(pet.ptr.sum()),
        "finite": finite, "nonneg": nonneg,
        "total_sigma_cm2_per_nucleon": total,
        "weight_coverage": wchk,
    }
    spath = args.summary or (os.path.splitext(args.out)[0] + ".summary.json")
    with open(spath, "w") as fh:
        json.dump(summary, fh, indent=2)
    print(f"[nominal] 5D xsec shape={pet.shape} nbins={summary['n_bins']} "
          f"populated={n_reported} finite={finite} nonneg={nonneg} "
          f"total_sigma={total:.6e} cm^2/nucleon", flush=True)
    print(f"[nominal] wrote {os.path.abspath(args.out)}", flush=True)
    print(f"[nominal] wrote {spath}", flush=True)
    print("[nominal] PASS: corrected nominal 5D PET cross section extracted.", flush=True)


if __name__ == "__main__":
    main()
