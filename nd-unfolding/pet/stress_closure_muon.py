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

LOGIN-SAFE BY CONSTRUCTION: synthetic event set, no ROOT, no /pscratch, no dump, identity
response (`reco=gen=cloud`) with all-pass masks. It does import TensorFlow and train, so budget
CPU minutes, not seconds.

2026-07-31 (Gate-4 re-issue, RESTORE-2026-08-03.md Step 2b / AUDIT-FINDINGS-20260729-B.md B-6).
Two changes, physics untouched:
  * `--json` writes a machine-readable report. This closure is named inside Gate-4's own frozen
    contract (`validate_pet_nominal_gate4.py FROZEN["closure_scripts"]["omitted_muon_stress"]`) and
    supplies two of its three `closure=` verdicts, which the validator had no way to read -- so
    `closure:stress_recoil_blind` and `closure:stress_fullevent_recovers` never executed.
  * the run is behind `main()` / `__name__ == "__main__"`. It used to train at IMPORT time, so
    nothing could inspect the predeclared verdict thresholds without paying for two trainings.
    The synthetic sample is still built at module scope: it is cheap and deterministic.
"""
import argparse
import json
import sys

import numpy as np

import os

# Repo root from this file location (<repo>/nd-unfolding/pet/); MNV_REPO overrides.
_REPO = os.environ.get("MNV_REPO") or os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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


REPORT_SCHEMA = "pet-fullevent-omitted-muon-stress-v1"
# Predeclared verdict thresholds (unchanged from the 2026-07-19 original; named so the report can
# state them and Gate-4 can see they were not loosened for the run it is reading).
RECOIL_BLIND_FRAC = 0.5      # recoil-only residual must stay >= this * the prior gap
FULLEVENT_GAIN_FRAC = 0.5    # full-event residual must fall below this * the recoil-only residual


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", default=None,
                    help="write the machine-readable stress-closure report here (Gate-4 consumes "
                         "it as --stress-report)")
    a = ap.parse_args(argv)

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
    recoil_fails = bool(np.median(res_r) > RECOIL_BLIND_FRAC * np.median(prior))
    full_recovers = bool(np.median(res_f) < FULLEVENT_GAIN_FRAC * np.median(res_r))
    print(f"[stress] recoil-only FAILS to recover (>=0.5*prior): {recoil_fails}")
    print(f"[stress] full-event RECOVERS (<0.5*recoil-only):      {full_recovers}")
    ok = recoil_fails and full_recovers
    if ok:
        print("STRESS CLOSURE PASS: full-event recovers the omitted muon variable; recoil-only cannot.")
    else:
        print("STRESS CLOSURE INCONCLUSIVE (inspect residuals/tuning).")

    if a.json:
        report = {
            "report_schema": REPORT_SCHEMA,
            "verdict": "PASS" if ok else "INCONCLUSIVE",
            "pass": ok,
            "recoil_only_fails_to_recover": recoil_fails,
            "fullevent_recovers": full_recovers,
            "alpha": float(ALPHA), "seed": int(SEED),
            "n_events": int(N), "n_tokens": int(P), "n_strata": 10,
            "niter": 3, "epochs": 8,
            "recoil_blind_frac": float(RECOIL_BLIND_FRAC),
            "fullevent_gain_frac": float(FULLEVENT_GAIN_FRAC),
            "residual_median": {"prior": float(np.median(prior)),
                                "recoil_only": float(np.median(res_r)),
                                "fullevent": float(np.median(res_f))},
            "residual_max": {"prior": float(prior.max()),
                             "recoil_only": float(res_r.max()),
                             "fullevent": float(res_f.max())},
            "residual_per_stratum": {"prior": [float(x) for x in prior],
                                     "recoil_only": [float(x) for x in res_r],
                                     "fullevent": [float(x) for x in res_f]},
            "synthetic_event_set": True,
            "note": "synthetic full-event stress sample by construction (identity response, "
                    "all-pass masks); this is the omitted-variable ABLATION, not the ordinary "
                    "physics closure of the G2 dump.",
        }
        with open(a.json, "w") as fh:
            json.dump(report, fh, indent=2)
            fh.write("\n")
        print(f"[stress] wrote report {a.json}")
    return 0 if ok else 3


if __name__ == "__main__":
    sys.exit(main())
