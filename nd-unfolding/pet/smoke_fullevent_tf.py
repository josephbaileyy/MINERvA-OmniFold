#!/usr/bin/env python3
"""TF smoke for the full-event PET interface repair (KNOWN_ISSUES #19, P5A step B/C).

Runs under the TF module (GPU or CPU). Proves, on tiny synthetic data:
  t1  event features ACTUALLY change the classifier output (the num_evt dead-wire is fixed)
  t1b recoil-only (num_evt=0) still builds a single-input model (backward compat)
  t2  explicit coord_idx changes the k-NN neighborhood (geometry is not accidental)
  t3  paired (cloud, evt) MultiFold runs end-to-end through cache/train/reweight both steps
  t4  save/reload weights -> identical prediction
Exit non-zero on any failure.
"""
import os
import sys

import numpy as np

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
for _p in (f"{_REPO}/omnifold_nn", f"{_REPO}/nd-unfolding"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import tensorflow as tf
from omnifold import PET, MultiFold
from omnifold.dataloader import DataLoader

tf.keras.utils.set_random_seed(0)
np.random.seed(0)

N, P, F, EV = 96, 6, 3, 2
rng = np.random.default_rng(0)
cloud = rng.random((N, P, F)).astype(np.float32)
cloud[:, 4:, 0] = 0.0                       # last 2 tokens padded (energy col 0 == 0)
evt = rng.random((N, EV)).astype(np.float32)

# ---- t1: event features change output --------------------------------------------------
m = PET(F, num_evt=EV, num_part=P, num_transformer=1, num_heads=1, projection_dim=16,
        local=True, K=3, coord_idx=(1, 2))
o1 = m.model.predict([cloud, evt], verbose=0)
o2 = m.model.predict([cloud, evt + 1.0], verbose=0)      # change ONLY event features
d = float(np.abs(o1 - o2).max())
assert o1.shape == (N, 1) and d > 1e-6, f"[t1 FAIL] event features are a no-op (max|d|={d:.3g})"
print(f"[t1] event features change output: PASS (max|delta|={d:.4g})")

# ---- t1b: recoil-only single-input model still works -----------------------------------
m0 = PET(F, num_evt=0, num_part=P, num_transformer=1, num_heads=1, projection_dim=16,
         local=True, K=3, coord_idx=(1, 2))
o0 = m0.model.predict(cloud, verbose=0)
assert o0.shape == (N, 1), "[t1b FAIL] recoil-only model broken"
assert len(m0.model.inputs) == 1 and len(m.model.inputs) == 2, "[t1b FAIL] input arity wrong"
print("[t1b] recoil-only num_evt=0 single-input model: PASS")

# ---- t2: explicit coord_idx changes the neighborhood -----------------------------------
tf.keras.utils.set_random_seed(1)
ma = PET(F, num_evt=0, num_part=P, num_transformer=1, num_heads=1, projection_dim=16,
         local=True, K=3, coord_idx=(0, 1))
tf.keras.utils.set_random_seed(1)
mb = PET(F, num_evt=0, num_part=P, num_transformer=1, num_heads=1, projection_dim=16,
         local=True, K=3, coord_idx=(1, 2))
# copy weights so ONLY coord_idx differs, then compare
mb.model.set_weights(ma.model.get_weights())
da = float(np.abs(ma.model.predict(cloud, verbose=0) - mb.model.predict(cloud, verbose=0)).max())
assert da > 1e-6, f"[t2 FAIL] coord_idx had no effect (max|d|={da:.3g})"
print(f"[t2] coord_idx changes k-NN neighborhood: PASS (max|delta|={da:.4g})")

# ---- t3: paired MultiFold end-to-end ---------------------------------------------------
tf.keras.utils.set_random_seed(0)
nmc, nda = 200, 180
mc_reco = rng.random((nmc, P, F)).astype(np.float32); mc_reco[:, 4:, 0] = 0
mc_gen = rng.random((nmc, P, F)).astype(np.float32); mc_gen[:, 4:, 0] = 0
da_reco = rng.random((nda, P, F)).astype(np.float32); da_reco[:, 4:, 0] = 0
mc_evt_r = rng.random((nmc, EV)).astype(np.float32)
mc_evt_g = rng.random((nmc, EV)).astype(np.float32)
da_evt = rng.random((nda, EV)).astype(np.float32)
pr = (rng.random(nmc) > 0.2); pg = (rng.random(nmc) > 0.1)
data = DataLoader(reco=da_reco, weight=np.ones(nda, np.float32), normalize=True, reco_evt=da_evt)
mc = DataLoader(reco=mc_reco, gen=mc_gen, pass_reco=pr, pass_gen=pg,
                weight=np.ones(nmc, np.float32), normalize=True,
                reco_evt=mc_evt_r, gen_evt=mc_evt_g)
m1 = PET(F, num_evt=EV, num_part=P, num_transformer=1, num_heads=1, projection_dim=16,
         local=True, K=3, coord_idx=(1, 2))
m2 = PET(F, num_evt=EV, num_part=P, num_transformer=1, num_heads=1, projection_dim=16,
         local=True, K=3, coord_idx=(1, 2))
of = MultiFold("smoke_fe", m1, m2, data, mc, niter=1, epochs=2, batch_size=32,
               weights_folder="/tmp/smoke_fe_w", verbose=False)
of.Unfold()
w = of.reweight((mc.gen, mc.gen_evt), of.model2, batch_size=64)
assert w.shape == (nmc,) and np.all(np.isfinite(w)), "[t3 FAIL] paired push weights bad"
print(f"[t3] paired MultiFold e2e: PASS (w mean={w.mean():.4f} std={w.std():.4f})")

# ---- t4: save / reload -----------------------------------------------------------------
p = "/tmp/smoke_fe_w/reload_test.weights.h5"
of.model2.model.save_weights(p)
m2b = PET(F, num_evt=EV, num_part=P, num_transformer=1, num_heads=1, projection_dim=16,
          local=True, K=3, coord_idx=(1, 2))
_ = m2b.model.predict([mc_gen[:8], mc_evt_g[:8]], verbose=0)   # build
m2b.model.load_weights(p)
oa = of.model2.model.predict([mc_gen[:16], mc_evt_g[:16]], verbose=0)
ob = m2b.model.predict([mc_gen[:16], mc_evt_g[:16]], verbose=0)
assert np.allclose(oa, ob, atol=1e-5), "[t4 FAIL] reload prediction differs"
print("[t4] save/reload identical prediction: PASS")

print("ALL FULL-EVENT TF SMOKE TESTS PASS")
