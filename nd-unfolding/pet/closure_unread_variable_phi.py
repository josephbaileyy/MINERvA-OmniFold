#!/usr/bin/env python3
"""Unread-variable closure: is the event-feature channel blind to a feature it does not read?

THE QUESTION THIS ANSWERS (B-3). `FULL_EVENT_FEATURE_CONTRACT.md:19-21` declares the
publication estimator `pet-fullevent-fps-v1` needs the full muon object (px,py,pz,E,phi,charge,
MINOS) + vertex + view/timing, while what P5A actually validated is the reduced {pT,p‖} set
(`:96`, `:116-123`). Extending the block to match the label costs new C++ branches plus an
FPS-CV regeneration (G2). Nothing currently measures whether that buys anything.

WHAT THE B-6 STRESS CLOSURE COULD NOT SETTLE. `stress_closure_muon.py` (first recorded PASS
2026-07-30) injected a tilt in the muon feature the loader ALREADY reads, and showed recoil-only
cannot recover it while full-event closes it 13.6x. That proves the event-feature CHANNEL works.
It cannot separate "PET uses muon information" from "PET needs the full muon object", because
the injected tilt was a function of a feature already consumed. This closure changes exactly one
thing: the injected variable is one the baseline does NOT read.

WHY phi AND NOT view/timing. view and timing are detector-only: they have no truth counterpart
(`FULL_EVENT_FEATURE_CONTRACT.md:102`, `:148`), so a tilt in them is recoverable at step 1 but
has no truth image, and letting step 1 absorb what may be a SIMULATION error propagates a fake
shift into truth. "Can see it" is not "should see it" for reco-only features. Muon phi is
unread today, is in the proposed extension, and HAS a truth counterpart -- so recovery is
meaningful at the truth level, which is where the measurement lives.

THREE ARMS, because a two-arm version is not falsifiable:
  1. BASE + phi-tilt        -- reads {pT,p‖}; must FAIL. Its residual is the LEAK FLOOR.
  2. EXTENDED + phi-tilt    -- reads {pT,p‖,phi}; must RECOVER, and must clear arm 1.
  3. BASE + pT-tilt         -- POSITIVE CONTROL. Without it, "arm 1 did not move" is
                               unfalsifiable: it could just mean the base arm is under-trained
                               at this stratum resolution rather than blind.

THE NULL IS HARDER HERE THAN IN B-6. B-6 only had to hold a 1-D marginal fixed. Here the tilt
must leave everything the BASE arm reads unchanged -- the whole cloud plus {pT,p‖}. phi is drawn
independent of {pT,p‖} so the muon block carries no phi information, and the tilt is normalized
WITHIN strata of the cloud summary R so the recoil marginal is held. Any residual correlation
between phi and the cloud beyond R leaks into arm 1, which is why arm 1's residual is reported
as a floor rather than assumed to be zero.

Synthetic on purpose: none of the eight extension arrays exist in any dump (the loader
references `reco_muon`, `reco_vertex`, `reco_view`, `reco_time` and their four `data_*` twins
ZERO times, verified 2026-07-30), so a real-data version is impossible before G2. What this can
license is the ASK, not the schema.
"""
import argparse
import json
import os
import sys

import numpy as np

_REPO = os.environ.get("MNV_REPO") or os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for _p in (f"{_REPO}/omnifold_nn", f"{_REPO}/nd-unfolding"):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def build_event(n, p_tokens, rng):
    """Synthetic full event: recoil cloud + muon block (pT, p‖) + an UNREAD azimuth phi.

    phi is correlated with the cloud summary R (as a real azimuth would be, through the hadronic
    system) but INDEPENDENT of (pT, p‖) -- so the baseline's muon block carries no phi
    information and the only route to phi is the cloud, which the per-stratum normalization
    closes off.
    """
    tokE = rng.gamma(2.0, 0.4, size=(n, p_tokens))
    tokx = rng.normal(0, 1, size=(n, p_tokens))
    tokz = rng.normal(0, 1, size=(n, p_tokens))
    cloud = np.stack([tokE, tokx, tokz], axis=-1).astype(np.float32)
    R = tokE.sum(1)                                              # recoil-energy summary
    pt = rng.gamma(2.0, 0.45, n)                                 # muon block: independent of phi
    ppar = rng.gamma(3.0, 1.6, n)
    phi = np.mod(0.6 * R + rng.normal(0, 1.0, n), 2 * np.pi)      # unread, cloud-correlated
    return cloud, R, pt, ppar, phi


def zscore(a):
    a = np.asarray(a, np.float64)
    return ((a - a.mean()) / (a.std() + 1e-9)).astype(np.float32)


def shape_coord_circular(phi, phi0=0.0):
    """Bounded shape coordinate for an AZIMUTH: cos(phi - phi0) in [-1, 1].

    A z-score tilt is WRONG for a circular variable: exp(a*z(phi)) is discontinuous across the
    0/2pi wrap, so the injected 'conditional distribution' jumps and the estimator is asked to
    learn a discontinuity that no physical azimuthal modulation has. cos() is the smooth periodic
    analogue (a von Mises tilt), which is also what an azimuthal asymmetry actually looks like.
    """
    return np.cos(np.asarray(phi, np.float64) - phi0)


def shape_coord_rank(values):
    """Bounded shape coordinate for a POSITIVE variable: 2*F(x) - 1 in [-1, 1], F = empirical CDF.

    Used so the positive control is AMPLITUDE-MATCHED to the phi arm. A z-score tilt on a gamma
    variable reaches exp(a*z) ~ 400 in the tail against ~3 for the bounded circular tilt, and a
    control with a 100x larger dynamic range is not a control -- it would be an easier problem,
    so 'base recovers pT but not phi' would confound difficulty with blindness.
    """
    v = np.asarray(values, np.float64)
    r = np.empty(len(v))
    r[np.argsort(v, kind="stable")] = np.arange(len(v))
    return 2.0 * (r + 0.5) / len(v) - 1.0


def per_stratum_tilt(shape_coord, strata, n_strata, amplitude):
    """exp(amplitude * s) for s in [-1,1], renormalized to mean 1 WITHIN each stratum.

    The renormalization holds the stratifying variable's marginal fixed: every stratum keeps its
    total weight, so only the CONDITIONAL distribution inside it moves. Because s is bounded, the
    tilt range is exactly [exp(-amplitude), exp(+amplitude)] for EVERY variable -- which is what
    makes the test arm and the control arm comparable.
    """
    f = np.exp(amplitude * np.asarray(shape_coord, np.float64))
    w = np.empty_like(f)
    for s in range(n_strata):
        sel = strata == s
        w[sel] = f[sel] / f[sel].mean()
    return w


def residual_per_stratum(target_vals, strata, n_strata, w_unfolded, w_data, bins):
    """L1 per stratum between the unfolded and data conditional distributions of target_vals."""
    res, prior = [], []
    for s in range(n_strata):
        sel = strata == s
        hu, _ = np.histogram(target_vals[sel], bins, weights=w_unfolded[sel], density=True)
        hd, _ = np.histogram(target_vals[sel], bins, weights=w_data[sel], density=True)
        hp, _ = np.histogram(target_vals[sel], bins, weights=np.ones(sel.sum()), density=True)
        dx = np.diff(bins)[0]
        res.append(np.abs(hu - hd).sum() * dx)
        prior.append(np.abs(hp - hd).sum() * dx)
    return np.array(res), np.array(prior)


def run(arm_features, w_data, cloud, evt_block, seed, cfg):
    """Unfold with the given event-feature block; return pushed gen weights."""
    import tensorflow as tf
    from omnifold import PET, MultiFold
    from omnifold.dataloader import DataLoader

    n = cloud.shape[0]
    evt = evt_block[:, arm_features].astype(np.float32)
    n_evt = evt.shape[1]
    tf.keras.utils.set_random_seed(seed)
    data = DataLoader(reco=cloud, weight=w_data.astype(np.float32), normalize=True, reco_evt=evt)
    mc = DataLoader(reco=cloud, gen=cloud, pass_reco=np.ones(n, bool), pass_gen=np.ones(n, bool),
                    weight=np.ones(n, np.float32), normalize=True,
                    reco_evt=evt, gen_evt=evt)
    m1 = PET(cloud.shape[-1], num_evt=n_evt, num_part=cloud.shape[1], num_transformer=2,
             num_heads=2, projection_dim=32, local=True, K=3, coord_idx=(1, 2))
    m2 = PET(cloud.shape[-1], num_evt=n_evt, num_part=cloud.shape[1], num_transformer=2,
             num_heads=2, projection_dim=32, local=True, K=3, coord_idx=(1, 2))
    tag = f"unread_{'_'.join(map(str, arm_features))}_s{seed}"
    of = MultiFold(tag, m1, m2, data, mc, niter=cfg.niter, epochs=cfg.epochs,
                   batch_size=cfg.batch_size, weights_folder=os.path.join(cfg.workdir, tag),
                   verbose=False)
    of.Unfold()
    return np.asarray(of.weights_push, np.float64)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-events", type=int, default=60000)
    ap.add_argument("--tokens", type=int, default=5)
    ap.add_argument("--strata", type=int, default=10)
    ap.add_argument("--amplitude", type=float, default=1.2, help="tilt strength (B-6 used 1.2)")
    ap.add_argument("--niter", type=int, default=3)
    ap.add_argument("--epochs", type=int, default=8)
    ap.add_argument("--batch-size", type=int, default=512)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--workdir", default="/tmp/unread_phi")
    ap.add_argument("--out", default="products/pet/closure_unread_variable_phi.json")
    cfg = ap.parse_args()

    os.makedirs(cfg.workdir, exist_ok=True)
    rng = np.random.default_rng(cfg.seed)
    np.random.seed(cfg.seed)
    cloud, R, pt, ppar, phi = build_event(cfg.n_events, cfg.tokens, rng)

    # Event-feature matrix. Columns 0,1 = the ADOPTED reduced schema; column 2 = the unread phi.
    # Azimuth enters as its own z-scored column here (the production truth cloud encodes azimuth
    # as cos/sin for KNN periodicity, CLM-008 F10; that is a neighbourhood-metric concern, not a
    # FiLM event-feature one, and using one column keeps the arms differing by exactly one dim).
    evt_block = np.column_stack([zscore(pt), zscore(ppar), zscore(phi)]).astype(np.float32)
    BASE, EXTENDED = [0, 1], [0, 1, 2]

    edges = np.quantile(R, np.linspace(0, 1, cfg.strata + 1))
    edges[0] -= 1e-6; edges[-1] += 1e-6
    strata = np.clip(np.digitize(R, edges) - 1, 0, cfg.strata - 1)

    # Independence precondition: if phi were correlated with the muon block, the base arm would
    # have a legitimate route to the tilt and a null would be meaningless.
    c_pt = float(np.corrcoef(phi, pt)[0, 1]); c_pp = float(np.corrcoef(phi, ppar)[0, 1])
    c_R = float(np.corrcoef(phi, R)[0, 1])
    print(f"[unread] corr(phi,pT)={c_pt:+.4f} corr(phi,p‖)={c_pp:+.4f} "
          f"corr(phi,R)={c_R:+.4f}  (muon-block corrs must be ~0; R corr is intended)")
    if abs(c_pt) > 0.05 or abs(c_pp) > 0.05:
        raise SystemExit("phi is correlated with the muon block -- the base arm is not blind")

    phi_bins = np.linspace(0, 2 * np.pi, 21)
    pt_bins = np.linspace(pt.min(), np.percentile(pt, 99.5), 21)

    # ---- tilt in phi (UNREAD by base), held per-R-stratum so the recoil marginal is fixed
    w_phi = per_stratum_tilt(shape_coord_circular(phi), strata, cfg.strata, cfg.amplitude)
    # ---- tilt in pT (READ by base) at MATCHED amplitude and matched dynamic range
    w_pt = per_stratum_tilt(shape_coord_rank(pt), strata, cfg.strata, cfg.amplitude)
    # Ranges are POST per-stratum renormalization, so they can exceed the raw exp(+-a) bound: a
    # stratum whose mean tilt is below 1 gets scaled up. What the bounded shape coordinate buys is
    # that the two arms stay within ~2x of each other instead of ~100x, which is what makes the
    # control a control. ESS is reported because a wide tilt costs effective statistics.
    for nm, w in (("phi", w_phi), ("pT ", w_pt)):
        ess = float(w.sum() ** 2 / (w ** 2).sum()) / len(w)
        print(f"[unread] {nm}-tilt range [{w.min():.3f},{w.max():.3f}] (post-stratum-renorm; "
              f"raw bound [{np.exp(-cfg.amplitude):.3f},{np.exp(cfg.amplitude):.3f}])  "
              f"ESS={100*ess:.1f}%", flush=True)

    out = {"config": vars(cfg), "corr": {"phi_pt": c_pt, "phi_ppar": c_pp, "phi_R": c_R}}

    def arm(name, feats, w_data, target_vals, bins):
        push = run(feats, w_data, cloud, evt_block, cfg.seed, cfg)
        res, prior = residual_per_stratum(target_vals, strata, cfg.strata, push, w_data, bins)
        rec = 1.0 - float(np.median(res)) / float(np.median(prior))
        out[name] = {"features": feats, "median_residual": float(np.median(res)),
                     "max_residual": float(res.max()),
                     "median_prior": float(np.median(prior)),
                     "recovered_fraction": rec,
                     "push_mean": float(push.mean()), "push_max": float(push.max())}
        print(f"[unread] {name:26s} feats={feats} median L1={np.median(res):.4f} "
              f"(prior {np.median(prior):.4f}) recovered={rec:+.4f}", flush=True)
        return rec

    leak = arm("base_phi_tilt", BASE, w_phi, phi, phi_bins)        # arm 1: the leak floor
    ext = arm("extended_phi_tilt", EXTENDED, w_phi, phi, phi_bins)  # arm 2: the test
    ctrl = arm("base_pt_tilt_control", BASE, w_pt, pt, pt_bins)     # arm 3: positive control

    # Predeclared verdict. The control gates the whole thing: a base arm that cannot recover a
    # tilt in a feature it DOES read is under-trained, and then arm 1's null says nothing.
    control_ok = ctrl > 0.5
    ext_clears_leak = ext > leak + 0.25
    print(f"\n[unread] positive control recovers (>0.50):        {control_ok}  ({ctrl:+.4f})")
    print(f"[unread] leak floor (base on unread phi):           {leak:+.4f}")
    print(f"[unread] extended clears the leak floor (+0.25):    {ext_clears_leak}  "
          f"({ext:+.4f} vs {leak:+.4f})")
    if not control_ok:
        verdict = "INVALID_CONTROL_FAILED"
        msg = ("INVALID: the base arm could not recover a tilt in a feature it DOES read, so its "
               "null on phi is uninterpretable (under-trained, not blind). Raise --epochs.")
    elif ext_clears_leak:
        verdict = "EXTENSION_ADDS_CAPABILITY"
        msg = ("UNREAD-VARIABLE CLOSURE: the extension recovers a mismatch class the reduced "
               "schema reports as null -> the event-feature channel has HEADROOM. This licenses "
               "the C++ ask as a sensitivity argument; it does NOT show the real data contains "
               "such a mismatch.")
    else:
        verdict = "EXTENSION_ADDS_NOTHING_MEASURABLE"
        msg = ("UNREAD-VARIABLE CLOSURE: the extension does NOT clear the leak floor -> no "
               "measurable capability gain from adding phi at this amplitude. Evidence AGAINST "
               "spending the C++ dump + FPS-CV regeneration on the extension.")
    out["verdict"] = verdict
    out["control_ok"] = bool(control_ok)
    print(f"\n{msg}")
    os.makedirs(os.path.dirname(cfg.out) or ".", exist_ok=True)
    with open(cfg.out, "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"[unread] wrote {cfg.out}")
    if not control_ok:
        sys.exit(3)


if __name__ == "__main__":
    main()
