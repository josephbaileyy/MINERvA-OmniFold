#!/usr/bin/env python3
"""Omitted-variable (muon) stress closure for the full-event PET estimator (P5A step D).

Decisive test of KNOWN_ISSUES #19: build pseudo-data by applying a KNOWN muon-kinematic
reweight WITHIN narrow recoil strata, normalized per stratum so the recoil MARGINAL is
unchanged and ONLY the conditional muon distribution p(m | recoil) is tilted. Then:

  * a RECOIL-ONLY estimator (classifier sees only the recoil cloud) cannot distinguish
    data from MC (identical recoil marginal) -> learned weight ~ 1 -> the conditional muon
    distribution stays at the MC prior -> it FAILS to recover the injected tilt;
  * the FULL-EVENT estimator (recoil cloud + continuous muon event feature) sees m ->
    learns the per-stratum tilt -> RECOVERS the data conditional muon distribution.

Runs under the TF module. Prints a PASS/FAIL verdict and the per-stratum residuals for
both models on the same stress sample (this is the FE-D + FE-E ablation core).
"""
import sys

import numpy as np

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
for _p in (f"{_REPO}/omnifold_nn", f"{_REPO}/nd-unfolding"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import tensorflow as tf
from omnifold import PET, MultiFold
from omnifold.dataloader import DataLoader

SEED = 0
np.random.seed(SEED)
rng = np.random.default_rng(SEED)

# ------------------------------------------------------------------ synthetic full event
# Recoil "cloud": P tokens with (E, x, z). A summary R = total recoil energy defines strata.
# Muon feature m correlated with R (m ~ N(g(R), s)), so a naive muon-marginal reweight would
# also move R; we normalize the tilt PER R-STRATUM to leave the recoil marginal fixed.
N, P = 20000, 5
tokE = rng.gamma(2.0, 0.4, size=(N, P)).astype(np.float32)       # >0 so no accidental pad
tokx = rng.normal(0, 1, size=(N, P)).astype(np.float32)
tokz = rng.normal(0, 1, size=(N, P)).astype(np.float32)
cloud = np.stack([tokE, tokx, tokz], axis=-1).astype(np.float32)  # (N,P,3) E,x,z
R = tokE.sum(1)                                                   # recoil-energy summary
m = (0.5 * R + rng.normal(0, 0.5, N)).astype(np.float32)          # muon feat, correlated w/ R
m_evt = ((m - m.mean()) / (m.std() + 1e-6)).astype(np.float32).reshape(-1, 1)  # continuous

# strata in R (deciles): normalize the tilt within each so the recoil marginal is unchanged
edges = np.quantile(R, np.linspace(0, 1, 11))
edges[0] -= 1e-6; edges[-1] += 1e-6
strata = np.clip(np.digitize(R, edges) - 1, 0, 9)
ALPHA = 1.2                                                       # injected muon tilt strength
f = np.exp(ALPHA * m_evt[:, 0]).astype(np.float64)               # muon-only tilt
w_data = np.empty(N, np.float64)
for s in range(10):
    sel = strata == s
    w_data[sel] = f[sel] / f[sel].mean()                          # per-stratum normalized => recoil marginal fixed
w_data = w_data.astype(np.float32)


def run(full_event):
    """Unfold with recoil-only (full_event=False) or full-event (True); return the pushed
    MC gen weights (likelihood-ratio estimate per event)."""
    tf.keras.utils.set_random_seed(SEED)
    data = DataLoader(reco=cloud, weight=w_data, normalize=True,
                      reco_evt=(m_evt if full_event else None))
    mc = DataLoader(reco=cloud, gen=cloud, pass_reco=np.ones(N, bool), pass_gen=np.ones(N, bool),
                    weight=np.ones(N, np.float32), normalize=True,
                    reco_evt=(m_evt if full_event else None),
                    gen_evt=(m_evt if full_event else None))
    m1 = PET(3, num_evt=(1 if full_event else 0), num_part=P, num_transformer=2, num_heads=2,
             projection_dim=32, local=True, K=3, coord_idx=(1, 2))
    m2 = PET(3, num_evt=(1 if full_event else 0), num_part=P, num_transformer=2, num_heads=2,
             projection_dim=32, local=True, K=3, coord_idx=(1, 2))
    of = MultiFold(f"stress_{'full' if full_event else 'recoil'}", m1, m2, data, mc,
                   niter=3, epochs=8, batch_size=512,
                   weights_folder=f"/tmp/stress_{'full' if full_event else 'recoil'}",
                   verbose=False)
    of.Unfold()
    return of.weights_push.astype(np.float64)


def residual(push):
    """Per-stratum L1 residual between the unfolded conditional muon histogram and the data
    target. Truth here = MC (reco=gen), so 'unfolded' p(m|stratum) = push-weighted MC; the
    data target = w_data-weighted MC. Returns (median, max) over strata of the L1 distance."""
    mbins = np.linspace(m_evt.min(), m_evt.max(), 21)
    res = []
    for s in range(10):
        sel = strata == s
        hu, _ = np.histogram(m_evt[sel, 0], mbins, weights=push[sel], density=True)
        hd, _ = np.histogram(m_evt[sel, 0], mbins, weights=w_data[sel], density=True)
        hp, _ = np.histogram(m_evt[sel, 0], mbins, weights=np.ones(sel.sum()), density=True)
        res.append((np.abs(hu - hd).sum() * np.diff(mbins)[0],
                    np.abs(hp - hd).sum() * np.diff(mbins)[0]))
    res = np.array(res)
    return res[:, 0], res[:, 1]   # (unfolded-vs-data, prior-vs-data)


print("[stress] injected per-stratum muon tilt alpha=%.2f; recoil marginal held fixed" % ALPHA)
push_r = run(full_event=False)
push_f = run(full_event=True)
res_r, prior = residual(push_r)
res_f, _ = residual(push_f)
print(f"[stress] PRIOR      vs data  L1/stratum: median={np.median(prior):.4f} max={prior.max():.4f}")
print(f"[stress] RECOIL-ONLY vs data L1/stratum: median={np.median(res_r):.4f} max={res_r.max():.4f}")
print(f"[stress] FULL-EVENT  vs data L1/stratum: median={np.median(res_f):.4f} max={res_f.max():.4f}")
# recoil-only should stay near the prior residual (cannot move m|R); full-event should
# recover data (residual much smaller than prior). Predeclared verdict:
recoil_fails = np.median(res_r) > 0.5 * np.median(prior)         # stays >= half the prior gap
full_recovers = np.median(res_f) < 0.5 * np.median(res_r)        # closes >= 2x better than recoil
print(f"[stress] recoil-only FAILS to recover (>=0.5*prior): {recoil_fails}")
print(f"[stress] full-event RECOVERS (<0.5*recoil-only):      {full_recovers}")
if recoil_fails and full_recovers:
    print("STRESS CLOSURE PASS: full-event recovers the omitted muon variable; recoil-only cannot.")
else:
    print("STRESS CLOSURE INCONCLUSIVE (inspect residuals/tuning).")
    sys.exit(3)
