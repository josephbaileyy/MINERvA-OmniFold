#!/usr/bin/env python3
"""Ordinary self-consistency closure for the full-event FPS estimator (P5A).

Pseudo-data = MC reco of the pass_reco events (weighted by the prior). A correct unfold then
pushes the truth back onto the MC truth: push weights stay ~1 and the reweighted-gen (pT,p‖)
spectrum reproduces the MC-truth spectrum. Complements the omitted-muon stress closure (which
proves the estimator MOVES when it should); this proves it does NOT move when it should not,
and checks the lower-dimensional (pT,p‖) marginal + normalization. Runs under the TF module."""
import sys
import zipfile

import numpy as np
import numpy.lib.format as npf

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
_ND = f"{_REPO}/nd-unfolding"
for _p in (f"{_REPO}/omnifold_nn", _ND, f"{_ND}/pet"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import tensorflow as tf
from omnifold import PET, MultiFold
from omnifold.dataloader import DataLoader
import fullevent_fps_dataloader as fe

NPZ = f"{_ND}/of_inputs_pc_fps_xps2.npz"
DATA_SCALARS = f"{_ND}/of_inputs_5d_fps_xps2.npz"   # CLM-007: explicit data muon scalars
MAXEV = 12000
tf.keras.utils.set_random_seed(0)

data, mc, imc, coord_reco, coord_gen, meta = fe.build_fullevent_loaders(
    NPZ, max_events=MAXEV, seed=0, data_scalars_npz=DATA_SCALARS)

# truth (pT,p‖) for the SAME subsample (for the marginal closure check)
z = zipfile.ZipFile(NPZ)
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
of = MultiFold("fe_closure", m1, m2, pdata, mc, niter=2, epochs=6, batch_size=512,
               weights_folder="/tmp/fe_closure_w", verbose=False)
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
ok = (l1 < 0.10) and (abs(np.median(push) - 1.0) < 0.15) and np.all(np.isfinite(push))
print("ORDINARY CLOSURE PASS" if ok else "ORDINARY CLOSURE CHECK (inspect L1/push/norm)")
sys.exit(0 if ok else 3)
