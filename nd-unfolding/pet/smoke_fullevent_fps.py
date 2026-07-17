#!/usr/bin/env python3
"""Small FPS smoke: full-event interface on the REAL extended-FPS tensors (P5A).

Builds paired full-event loaders from the xps2 scaffolding npz (subsample), then runs a
tiny MultiFold to prove the whole full-event chain flows on genuine FPS data: the extended
edge guard fires, the recoil/truth clouds + continuous event features + explicit KNN coords
assemble, the no-truth-leakage assertion holds on real scalars, and the paired PET MultiFold
trains + reweights to finite push weights. NOT a physics/coverage claim (that is P5B)."""
import sys

import numpy as np

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
_ND = f"{_REPO}/nd-unfolding"
for _p in (f"{_REPO}/omnifold_nn", _ND, f"{_ND}/pet"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import tensorflow as tf
from omnifold import PET, MultiFold
import fullevent_fps_dataloader as fe

NPZ = f"{_ND}/of_inputs_pc_fps_xps2.npz"
DATA_SCALARS = f"{_ND}/of_inputs_5d_fps_xps2.npz"   # data muon pT,p‖ (CLM-007: no silent MC fallback)
tf.keras.utils.set_random_seed(0)

data, mc, imc, coord_reco, coord_gen, meta = fe.build_fullevent_loaders(
    NPZ, max_events=8000, seed=0, data_scalars_npz=DATA_SCALARS)
print(f"[fps-smoke] data_scalar_source = {meta.get('data_scalar_source')}")
reco = np.asarray(mc.reco); gen = np.asarray(mc.gen)
print(f"[fps-smoke] reco cloud {reco.shape} coord_reco={coord_reco} "
      f"reco_evt {np.asarray(mc.reco_evt).shape}")
print(f"[fps-smoke] gen  cloud {gen.shape} coord_gen={coord_gen} "
      f"gen_evt {np.asarray(mc.gen_evt).shape}")
print(f"[fps-smoke] data cloud {np.asarray(data.reco).shape} data_evt "
      f"{np.asarray(data.reco_evt).shape}")
print(f"[fps-smoke] meta={meta}")
assert reco.shape[-1] == 3 and gen.shape[-1] == 7, "unexpected cloud feature dims"
assert coord_reco == (1, 2) and coord_gen == (5, 6), "unexpected KNN coord indices"
assert np.all(np.isfinite(reco)) and np.all(np.isfinite(gen)), "non-finite cloud"
assert np.all(np.isfinite(mc.reco_evt)) and np.all(np.isfinite(mc.gen_evt)), "non-finite evt"

P = reco.shape[1]
ev = meta["n_evt"]
m1 = PET(reco.shape[-1], num_evt=ev, num_part=P, num_transformer=1, num_heads=1,
         projection_dim=16, local=True, K=3, coord_idx=coord_reco)
m2 = PET(gen.shape[-1], num_evt=ev, num_part=P, num_transformer=1, num_heads=1,
         projection_dim=16, local=True, K=3, coord_idx=coord_gen)
of = MultiFold("fps_smoke", m1, m2, data, mc, niter=1, epochs=2, batch_size=256,
               weights_folder="/tmp/fps_smoke_w", verbose=False)
of.Unfold()
w = of.reweight((mc.gen, mc.gen_evt), of.model2, batch_size=256)
assert w.shape[0] == gen.shape[0] and np.all(np.isfinite(w)), "bad push weights"
print(f"[fps-smoke] paired MultiFold on real FPS data: PASS "
      f"(push mean={w.mean():.4f} std={w.std():.4f})")
print("FPS FULL-EVENT SMOKE PASS")
