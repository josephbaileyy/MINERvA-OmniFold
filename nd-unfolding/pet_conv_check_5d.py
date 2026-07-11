#!/usr/bin/env python3
"""Step 4 (Tier-2 retraining-response, b-lite / convergence-curve check) evaluation.

CPU-only. Loads the 6 seed-replica PET weight npz's produced by
sbatch_pet_conv_fps_xps2.sh (4 at 10M events, 2 at 5M events, same NITER/EPOCHS recipe as
the xps2 headline train), pushes each through PETxsec5D on the SAME xps2 inputs used for
the headline/envelope, and takes the per-bin spread ACROSS seed replicas at fixed event
count as the ML-retraining noise floor sigma_retrain. Compares sigma_retrain/x_pet by
completeness tier (comp_reco, reused from the already-landed
products/pet/fps_envelope_5d_xps2/fps_gbdt_prior_xsec_5d.npz -- no re-derivation) against
the 3-prior model-dependence envelope median, and checks the 5M->10M trend shrinks.

  python pet_conv_check_5d.py
"""
import numpy as np

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
MCFILE = f"{_REPO}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root"
FLUX_HIST = "pTmu_reweightedflux_integrated"
PC_NPZ = "of_inputs_pc_fps_xps2.npz"
WSOURCE = "of_inputs_5d_fps_xps2_wsource.npz"
ENVELOPE_NPZ = "products/pet/fps_envelope_5d_xps2/fps_gbdt_prior_xsec_5d.npz"

REPLICAS_10M = [f"products/pet/pet_weights_fps_xps2_conv_10M_s{s}.npz" for s in (101, 102, 103, 104)]
REPLICAS_5M = [f"products/pet/pet_weights_fps_xps2_conv_5M_s{s}.npz" for s in (201, 202)]


def main():
    from pet_systematics_5d import PETxsec5D

    def xsec_for(weights_npz):
        pet = PETxsec5D(PC_NPZ, weights_npz, MCFILE, FLUX_HIST, WSOURCE, None)
        return pet.xsec(None)

    print("[conv] evaluating 10M replicas...")
    x10 = np.stack([xsec_for(f) for f in REPLICAS_10M])
    print("[conv] evaluating 5M replicas...")
    x5 = np.stack([xsec_for(f) for f in REPLICAS_5M])

    env = np.load(ENVELOPE_NPZ)
    comp_reco = env["comp_reco"].astype(np.float64)
    rep_envelope = env["rep"].astype(bool)

    # a bin is "reported" for this check if all replicas at that event count populate it
    # (x_pet>0) AND the envelope's own rep mask agrees (consistency with the headline)
    rep10 = np.all(x10 > 0, axis=0) & rep_envelope
    rep5 = np.all(x5 > 0, axis=0) & rep_envelope

    mean10 = x10.mean(axis=0)
    sig10 = x10.std(axis=0, ddof=1)
    frac10 = np.where(mean10 > 0, sig10 / mean10, np.nan)

    mean5 = x5.mean(axis=0)
    sig5 = x5.std(axis=0, ddof=1)
    frac5 = np.where(mean5 > 0, sig5 / mean5, np.nan)

    tier1 = comp_reco >= 0.5
    tier2 = comp_reco < 0.5

    def report(name, frac, rep, mask):
        m = rep & mask & np.isfinite(frac)
        if not m.any():
            print(f"[conv] {name:28s} n=0"); return None
        d = frac[m]
        med, p90 = float(np.median(d)), float(np.percentile(d, 90))
        print(f"[conv] {name:28s} n={m.sum():5d}  sigma_retrain/x: median={100*med:.2f}%  "
              f"p90={100*p90:.2f}%")
        return {"n": int(m.sum()), "median": med, "p90": p90}

    print("\n=== sigma_retrain/x_pet by tier ===")
    r10_t1 = report("10M Tier-1 (comp>=0.5)", frac10, rep10, tier1)
    r10_t2 = report("10M Tier-2 (comp<0.5)", frac10, rep10, tier2)
    r5_t1 = report("5M  Tier-1 (comp>=0.5)", frac5, rep5, tier1)
    r5_t2 = report("5M  Tier-2 (comp<0.5)", frac5, rep5, tier2)

    print("\n=== acceptance check vs 3-prior envelope ===")
    summary_env_t2_median = 0.1628  # Stage-2 extrapolated(comp<0.5) median, for reference
    if r10_t2:
        ratio = r10_t2["median"] / summary_env_t2_median
        print(f"[conv] 10M Tier-2 median {100*r10_t2['median']:.2f}% vs envelope Tier-2 "
              f"median {100*summary_env_t2_median:.2f}% -> ratio={ratio:.3f} "
              f"(target <= 0.33)")
    if r5_t2 and r10_t2:
        trend_ok = r5_t2["median"] > r10_t2["median"]
        print(f"[conv] 5M->10M Tier-2 trend: {100*r5_t2['median']:.2f}% -> "
              f"{100*r10_t2['median']:.2f}% (shrinking={trend_ok})")

    np.savez_compressed("products/pet/pet_conv_check_5d_xps2.npz",
                        x10=x10, x5=x5, frac10=frac10, frac5=frac5,
                        rep10=rep10, rep5=rep5, comp_reco=comp_reco)
    print("\n[conv] wrote products/pet/pet_conv_check_5d_xps2.npz")


if __name__ == "__main__":
    main()
