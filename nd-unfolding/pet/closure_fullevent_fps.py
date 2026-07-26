#!/usr/bin/env python3
"""Ordinary self-consistency closure for the full-event FPS estimator (P5A).

Pseudo-data = MC reco of the pass_reco events (weighted by the prior). A correct unfold then
pushes the truth back onto the MC truth: push weights stay ~1 and the reweighted-gen (pT,p‖)
spectrum reproduces the MC-truth spectrum. Complements the omitted-muon stress closure (which
proves the estimator MOVES when it should); this proves it does NOT move when it should not,
and checks the lower-dimensional (pT,p‖) marginal + normalization. Runs under the TF module.

2026-07-25 REPAIR. As committed at 9d7a4c6 (2026-07-18) this script passed the recoil-only
`of_inputs_pc_fps_xps2.npz` with bkg_mode="purity". The `g2-fullevent-v1` schema gate landed
the next day (01d324a, dataloader ~L497) and fail-closes on exactly that input, so the script
had been dead ever since -- verified 2026-07-25 by replaying the staged xps2 member set
(18 members, no `petSchemaVersion`) through `build_fullevent_loaders`, which raises
"[G2] input is not a g2-fullevent-v1 schema NPZ". The recorded PASS at 36ab84d was therefore
obtained against the PRE-GATE dataloader and does not certify the current code path.

Changes made in the repair (physics untouched):
  * repo root derived from __file__ (was hardcoded /pscratch/...), so it runs on Delta too
  * --inputs / --data-scalars / --bkg-mode / --niter / --epochs / --max-events are CLI args
  * default input is the real G2 full-event dump; default bkg_mode is the negweight-refined
    nominal. "purity" remains selectable as a LABELED CONTROL, never the nominal.
  * a synthetic fixture (synthetic_fixture=1) is detected and loudly banner-ed, and the
    verdict line is tagged so a plumbing run can never be mistaken for a physics closure.

Re-running this against the real G2 dump is required to restore the P5A closure receipt;
that is blocked until the Perlmutter restore (2026-08-03).
"""
import argparse
import os
import sys
import zipfile

import numpy as np
import numpy.lib.format as npf

# Repo root from this file's location: <repo>/nd-unfolding/pet/closure_fullevent_fps.py
_HERE = os.path.dirname(os.path.abspath(__file__))
_ND = os.path.dirname(_HERE)
_REPO = os.environ.get("MNV_REPO") or os.path.dirname(_ND)
for _p in (os.path.join(_REPO, "omnifold_nn"), _ND, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

_DEFAULT_NPZ = os.path.join(_ND, "g2_fullevent", "input", "G2_FPS_MEFHC_P12.npz")


def parse_args():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--inputs", default=_DEFAULT_NPZ,
                   help="g2-fullevent-v1 NPZ (default: the real G2 dump)")
    p.add_argument("--data-scalars", default=None,
                   help="explicit data muon scalars (CLM-007); unnecessary when the input "
                        "carries measured_scalars, as the G2 dump does")
    p.add_argument("--bkg-mode", default="negweight-refined",
                   choices=("negweight-refined", "purity"),
                   help="negweight-refined = locked nominal; purity = labeled control only")
    p.add_argument("--max-events", type=int, default=12000)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--niter", type=int, default=2)
    p.add_argument("--epochs", type=int, default=6)
    p.add_argument("--batch-size", type=int, default=512)
    p.add_argument("--weights-folder", default="/tmp/fe_closure_w")
    p.add_argument("--l1-max", type=float, default=0.10, help="marginal L1 pass threshold")
    p.add_argument("--push-med-tol", type=float, default=0.15,
                   help="|median(push) - 1| pass threshold")
    return p.parse_args()


def main():
    a = parse_args()
    if not os.path.exists(a.inputs):
        print(f"[closure] MISSING input {a.inputs}\n"
              f"[closure] the real G2 dump lives on Perlmutter /pscratch and is unreachable "
              f"during the 2026-07-22..08-03 maintenance; pass --inputs with a "
              f"g2-fullevent-v1 fixture to exercise the code path.", file=sys.stderr)
        return 2

    import tensorflow as tf
    from omnifold import PET, MultiFold
    from omnifold.dataloader import DataLoader
    import fullevent_fps_dataloader as fe

    # Synthetic-fixture detection BEFORE anything expensive, so the banner leads the log.
    with zipfile.ZipFile(a.inputs) as _z:
        _members = {n[:-4] for n in _z.namelist()}
    is_synth = "synthetic_fixture" in _members
    if is_synth:
        print("=" * 78)
        print("SYNTHETIC FIXTURE -- RANDOM DATA. This is a PLUMBING check of the full-event")
        print("code path, NOT a physics closure. The verdict below is tagged accordingly and")
        print("must never be recorded as the P5A closure receipt.")
        print("=" * 78)
    if a.bkg_mode == "purity":
        print("[closure] bkg_mode=purity -- LABELED CONTROL, not the publication nominal.")

    tf.keras.utils.set_random_seed(a.seed)

    data, mc, imc, coord_reco, coord_gen, meta = fe.build_fullevent_loaders(
        a.inputs, max_events=a.max_events, seed=a.seed,
        data_scalars_npz=a.data_scalars, bkg_mode=a.bkg_mode)

    # truth (pT,p‖) for the SAME subsample (for the marginal closure check)
    z = zipfile.ZipFile(a.inputs)
    with z.open("truth_scalars.npy") as fh:
        ts_full = npf.read_array(fh, allow_pickle=False)
    ts = ts_full[imc]                                  # (n, 4) pt,pz,eavail,q3
    del ts_full

    reco = np.asarray(mc.reco); reco_evt = np.asarray(mc.reco_evt)
    pr = np.asarray(mc.pass_reco); pg = np.asarray(mc.pass_gen)
    # pseudo-data = MC reco (pass_reco), weighted by the (normalized) prior; carry reco_evt
    pdata = DataLoader(reco=reco[pr], weight=np.asarray(mc.weight)[pr], normalize=True,
                       reco_evt=reco_evt[pr])
    P = reco.shape[1]; ev = meta["n_evt"]
    m1 = PET(reco.shape[-1], num_evt=ev, num_part=P, num_transformer=2, num_heads=2,
             projection_dim=32, local=True, K=3, coord_idx=coord_reco)
    m2 = PET(np.asarray(mc.gen).shape[-1], num_evt=ev, num_part=P, num_transformer=2, num_heads=2,
             projection_dim=32, local=True, K=3, coord_idx=coord_gen)
    of = MultiFold("fe_closure", m1, m2, pdata, mc, niter=a.niter, epochs=a.epochs,
                   batch_size=a.batch_size, weights_folder=a.weights_folder, verbose=False)
    of.Unfold()
    push = of.weights_push.astype(np.float64)
    print(f"[closure] push weights: mean={push.mean():.4f} median={np.median(push):.4f} "
          f"std={push.std():.4f} finite={np.all(np.isfinite(push))}")

    # (pT,p‖) marginal closure among pass_gen: truth vs reweighted-gen
    wt = np.asarray(mc.weight).astype(np.float64)
    sel = pg
    edges_pt, edges_pz = fe.CANONICAL_PT_EDGES, fe.CANONICAL_PPARALLEL_EDGES
    H_truth, _, _ = np.histogram2d(ts[sel, 0], ts[sel, 1], [edges_pt, edges_pz], weights=wt[sel])
    H_rw, _, _ = np.histogram2d(ts[sel, 0], ts[sel, 1], [edges_pt, edges_pz],
                                weights=(wt * push)[sel])
    H_truth /= H_truth.sum(); H_rw /= H_rw.sum()
    l1 = float(np.abs(H_truth - H_rw).sum())
    print(f"[closure] (pT,p||) marginal L1(truth, reweighted-gen) = {l1:.4f} "
          f"(closure: pseudo-data=MC -> should be small)")
    norm_ok = abs((wt * push)[sel].sum() / wt[sel].sum() - 1.0)
    print(f"[closure] normalization |sum(w*push)/sum(w) - 1| = {norm_ok:.4f}")
    ok = (l1 < a.l1_max) and (abs(np.median(push) - 1.0) < a.push_med_tol) \
        and np.all(np.isfinite(push))

    tag = " [SYNTHETIC FIXTURE - PLUMBING ONLY, NOT THE P5A RECEIPT]" if is_synth else ""
    if a.bkg_mode == "purity":
        tag += " [purity control]"
    print(("ORDINARY CLOSURE PASS" if ok else
           "ORDINARY CLOSURE CHECK (inspect L1/push/norm)") + tag)
    return 0 if ok else 3


if __name__ == "__main__":
    sys.exit(main())
