#!/usr/bin/env python3
"""Coupled-phi sweep: turn the unread-variable UPPER BOUND into a curve.

WHAT THIS FIXES. `closure_unread_variable_phi.py` (Delta job 20600383, 2026-07-30) measured
base +0.0003 / extended +0.8755 / control +0.9643 with phi drawn INDEPENDENT of the muon block.
Independence maximizes the baseline's blindness, so +0.8755 is an UPPER BOUND on the capability
gain, not an estimate of it. Real muon phi is not independent of (pT, p‖): MINOS matching and the
detector's non-azimuthally-symmetric acceptance couple them. This script sweeps that coupling and
reports gain = extended - leak as a FUNCTION of it, so that when /pscratch returns (2026-08-03
22:00 PT) the real coupling can be measured and the gain READ OFF the curve instead of guessed.

HOW THE COUPLING IS INDUCED, and why not a correlation knob. The mechanism named in the caveat is
ACCEPTANCE, so acceptance is what is simulated: candidates are drawn exactly as in the independent
fixture, then THINNED with

    P(accept) = exp( lambda * cos(phi) * s_pT  -  lambda ),      s_pT = 2F(pT) - 1 in [-1,1]

which is bounded in (0,1] and favours the (cos phi, s_pT) diagonal. The surviving sample therefore
carries a real phi-muon correlation produced the way the detector produces one, and it also
distorts the phi and pT marginals the way real acceptance does. Sweeping `lambda` and REPORTING
the achieved correlation is honest in a way that dialling a correlation coefficient directly is
not -- a copula would give the same corr with none of the marginal distortion, and the marginal
distortion is part of what the estimator has to cope with.

N IS HELD FIXED ACROSS SWEEP POINTS. Thinning at lambda=1.5 keeps ~25% of candidates. If each
point simply used whatever survived, the high-coupling points would train on less data and "gain
shrinks with coupling" would be confounded with "gain shrinks with statistics" -- the exact class
of confound that voided CLM-006. Candidates are drawn in chunks until n accepted, then TRUNCATED
to exactly n.

EVERY POINT RUNS ITS OWN POSITIVE CONTROL. Validity is per-fixture, not per-sweep: thinning
changes the sample at every lambda, and an arm that is merely under-trained at high lambda would
masquerade as "the gain vanished". A point whose control fails is reported INVALID and excluded
from the curve rather than plotted as a low-gain point.

THE LEAK STATISTIC IS corr(cos phi, .), NOT corr(phi, .). The linear correlation of a raw azimuth
with anything is close to meaningless -- it is aliased by the 0/2pi wrap. What the base arm can
exploit is the SHAPE COORDINATE the tilt is built from, cos(phi), so that is what is reported and
gated on. (The independent fixture checked corr(phi, pT); its conclusion is unaffected, because
there phi was built from R + noise and pT was drawn from a separate generator, so independence was
guaranteed by CONSTRUCTION and the check was merely weaker than the construction. Here nothing is
independent by construction, so the statistic has to be the right one.)

STILL A CLOSURE. Pseudo-data is a reweighted MC half. This bounds a CAPABILITY, and says nothing
about whether the real data contains an azimuthal mismatch.
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

from closure_unread_variable_phi import (  # noqa: E402  (path set above)
    per_stratum_tilt,
    residual_per_stratum,
    run,
    shape_coord_circular,
    shape_coord_rank,
    zscore,
)


def draw_candidates(m, p_tokens, rng):
    """The independent fixture's generator, verbatim in law: cloud, R, muon block, azimuth.

    Imported by value rather than by reference from closure_unread_variable_phi.build_event
    because that function draws exactly n events; here the draw has to be oversampled and thinned,
    and silently reusing it would give a different number of events per sweep point.
    """
    tokE = rng.gamma(2.0, 0.4, size=(m, p_tokens))
    tokx = rng.normal(0, 1, size=(m, p_tokens))
    tokz = rng.normal(0, 1, size=(m, p_tokens))
    cloud = np.stack([tokE, tokx, tokz], axis=-1).astype(np.float32)
    R = tokE.sum(1)
    pt = rng.gamma(2.0, 0.45, m)
    ppar = rng.gamma(3.0, 1.6, m)
    phi = np.mod(0.6 * R + rng.normal(0, 1.0, m), 2 * np.pi)
    return cloud, R, pt, ppar, phi


def build_event_coupled(n, p_tokens, rng, coupling, max_chunks=40):
    """Draw n events whose azimuth is coupled to the muon block by acceptance thinning."""
    parts, kept = [], 0
    for _ in range(max_chunks):
        m = 4 * n
        cl, R, pt, ppar, phi = draw_candidates(m, p_tokens, rng)
        if coupling == 0.0:
            acc = np.ones(m, bool)
        else:
            # s_pT ranked within the candidate pool, so the exponent is bounded by +-lambda and
            # the acceptance never needs a clip that would itself distort the coupling.
            log_p = coupling * np.cos(phi) * shape_coord_rank(pt) - coupling
            acc = rng.random(m) < np.exp(log_p)
        parts.append((cl[acc], R[acc], pt[acc], ppar[acc], phi[acc]))
        kept += int(acc.sum())
        if kept >= n:
            break
    if kept < n:
        # Raised to 40 chunks (from 12) for the high-lambda extension: lambda=6.0 accepts ~3.1%,
        # so 60000 events needs ~8 chunks of 4n and the old cap aborted the whole job. This is a
        # runaway guard, not a budget -- candidate generation is seconds against ~17 min of
        # training per point. Points that still hit it are genuinely unreachable at this n.
        raise SystemExit(f"acceptance too tight at coupling={coupling}: only {kept}/{n} events "
                         f"after {max_chunks} chunks of {4*n} candidates "
                         f"({100.0*kept/(max_chunks*4*n):.2f}% accepted). Lower --coupling or "
                         f"raise --n-events.")
    out = [np.concatenate([p[i] for p in parts], axis=0)[:n] for i in range(5)]
    return (*out, float(kept) / (len(parts) * 4 * n))   # accepted fraction of drawn candidates


def sweep_point(coupling, cfg, rng):
    """One fixture + its three arms. Returns the record for the curve."""
    cloud, R, pt, ppar, phi, acc_frac = build_event_coupled(
        cfg.n_events, cfg.tokens, rng, coupling)
    evt_block = np.column_stack([zscore(pt), zscore(ppar), zscore(phi)]).astype(np.float32)
    BASE, EXTENDED = [0, 1], [0, 1, 2]

    edges = np.quantile(R, np.linspace(0, 1, cfg.strata + 1))
    edges[0] -= 1e-6
    edges[-1] += 1e-6
    strata = np.clip(np.digitize(R, edges) - 1, 0, cfg.strata - 1)

    c_phi = shape_coord_circular(phi)
    corr = {"cosphi_pt": float(np.corrcoef(c_phi, pt)[0, 1]),
            "cosphi_ppar": float(np.corrcoef(c_phi, ppar)[0, 1]),
            "cosphi_R": float(np.corrcoef(c_phi, R)[0, 1]),
            "phi_pt_raw": float(np.corrcoef(phi, pt)[0, 1])}
    print(f"\n=== coupling lambda={coupling:.2f}  accepted={100*acc_frac:.1f}%  n={len(phi)} ===")
    print(f"[sweep] corr(cos phi, pT)={corr['cosphi_pt']:+.4f}  "
          f"corr(cos phi, p‖)={corr['cosphi_ppar']:+.4f}  "
          f"corr(cos phi, R)={corr['cosphi_R']:+.4f}  "
          f"[raw corr(phi,pT)={corr['phi_pt_raw']:+.4f}, the WRONG statistic, shown for "
          f"continuity with job 20600383]", flush=True)

    if cfg.calibrate_only:
        return {"coupling": coupling, "corr": corr, "accepted_fraction": acc_frac,
                "n": int(len(phi))}

    phi_bins = np.linspace(0, 2 * np.pi, 21)
    pt_bins = np.linspace(pt.min(), np.percentile(pt, 99.5), 21)
    w_phi = per_stratum_tilt(c_phi, strata, cfg.strata, cfg.amplitude)
    w_pt = per_stratum_tilt(shape_coord_rank(pt), strata, cfg.strata, cfg.amplitude)
    ess = {}
    for nm, w in (("phi", w_phi), ("pT", w_pt)):
        ess[nm] = float(w.sum() ** 2 / (w ** 2).sum()) / len(w)
    print(f"[sweep] ESS phi={100*ess['phi']:.1f}%  pT={100*ess['pT']:.1f}%", flush=True)

    rec = {}
    # Per-point checkpoint dir. `run()` names its weights folder from (features, seed) only, which
    # is unique within one fixture but COLLIDES across sweep points. Nothing loads those files at
    # start=0 so today the collision is only an overwrite, but a later run with MultiFold(start>0)
    # would silently warm-start one coupling from another's checkpoint. Separate them now.
    pcfg = argparse.Namespace(**vars(cfg))
    pcfg.workdir = os.path.join(cfg.workdir, f"lam{coupling:.2f}")
    os.makedirs(pcfg.workdir, exist_ok=True)

    def arm(name, feats, w_data, target_vals, bins):
        push = run(feats, w_data, cloud, evt_block, cfg.seed, pcfg)
        res, prior = residual_per_stratum(target_vals, strata, cfg.strata, push, w_data, bins)
        r = 1.0 - float(np.median(res)) / float(np.median(prior))
        rec[name] = r
        print(f"[sweep]   {name:22s} feats={feats} median L1={np.median(res):.4f} "
              f"(prior {np.median(prior):.4f}) recovered={r:+.4f}", flush=True)
        return r

    leak = arm("base_phi_tilt", BASE, w_phi, phi, phi_bins)
    ext = arm("extended_phi_tilt", EXTENDED, w_phi, phi, phi_bins)
    ctrl = arm("base_pt_tilt_control", BASE, w_pt, pt, pt_bins)

    control_ok = ctrl > 0.5
    gain = ext - leak
    print(f"[sweep]   gain = extended - leak = {gain:+.4f}   control {'OK' if control_ok else 'FAILED'}"
          f" ({ctrl:+.4f})", flush=True)
    return {"coupling": coupling, "corr": corr, "accepted_fraction": acc_frac,
            "n": int(len(phi)), "ess": ess, "leak": leak, "extended": ext, "control": ctrl,
            "gain": gain, "control_ok": bool(control_ok),
            "valid": bool(control_ok)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--couplings", default="0.0,0.3,0.6,1.0,1.5",
                    help="lambda grid for the acceptance thinning")
    ap.add_argument("--n-events", type=int, default=60000)
    ap.add_argument("--tokens", type=int, default=5)
    ap.add_argument("--strata", type=int, default=10)
    ap.add_argument("--amplitude", type=float, default=1.2)
    ap.add_argument("--niter", type=int, default=3)
    ap.add_argument("--epochs", type=int, default=8)
    ap.add_argument("--batch-size", type=int, default=512)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--workdir", default="/tmp/coupled_phi")
    ap.add_argument("--out", default="products/pet/closure_coupled_phi_sweep.json")
    ap.add_argument("--calibrate-only", action="store_true",
                    help="draw the fixtures and report achieved correlations, no training "
                         "(numpy only -- login-safe, use this to pick the lambda grid)")
    cfg = ap.parse_args()

    couplings = [float(x) for x in cfg.couplings.split(",")]
    os.makedirs(cfg.workdir, exist_ok=True)
    rng = np.random.default_rng(cfg.seed)
    np.random.seed(cfg.seed)

    points = [sweep_point(c, cfg, rng) for c in couplings]

    out = {"config": vars(cfg), "points": points}
    if not cfg.calibrate_only:
        print(f"\n{'lambda':>7s} {'corr(cosphi,pT)':>16s} {'leak':>8s} {'extended':>9s} "
              f"{'gain':>8s} {'control':>8s}  valid")
        for p in points:
            print(f"{p['coupling']:7.2f} {p['corr']['cosphi_pt']:+16.4f} {p['leak']:+8.4f} "
                  f"{p['extended']:+9.4f} {p['gain']:+8.4f} {p['control']:+8.4f}  "
                  f"{'yes' if p['valid'] else 'NO (control failed)'}")

        valid = [p for p in points if p["valid"]]
        if len(valid) < 2:
            out["verdict"] = "INVALID_TOO_FEW_VALID_POINTS"
            print("\nINVALID: fewer than two points have a passing positive control, so there is "
                  "no curve. Raise --epochs.")
        else:
            # The actionable number: the coupling at which the gain stops clearing the +0.25
            # clearance the independent fixture used as its verdict threshold. Linear interpolation
            # between the bracketing points -- crude, and labelled crude, but it is what turns the
            # curve into a comparison the 08-03 real-data measurement can be run against.
            xs = [p["corr"]["cosphi_pt"] for p in valid]
            gs = [p["gain"] for p in valid]
            cross = None
            for i in range(len(valid) - 1):
                if (gs[i] - 0.25) * (gs[i + 1] - 0.25) <= 0 and gs[i] != gs[i + 1]:
                    t = (gs[i] - 0.25) / (gs[i] - gs[i + 1])
                    cross = xs[i] + t * (xs[i + 1] - xs[i])
                    break
            out["gain_at_zero_coupling"] = gs[0]
            out["crossing_corr_cosphi_pt"] = cross
            if cross is None and min(gs) > 0.25:
                out["verdict"] = "GAIN_SURVIVES_ALL_TESTED_COUPLINGS"
                print(f"\nThe gain clears +0.25 at EVERY tested coupling, out to "
                      f"corr(cos phi,pT)={max(xs):+.3f}. The independent-fixture number "
                      f"{gs[0]:+.4f} is an upper bound, but the capability claim does not depend "
                      f"on independence over this range.")
            elif cross is None:
                out["verdict"] = "GAIN_BELOW_THRESHOLD_THROUGHOUT"
                print("\nThe gain never clears +0.25 on this grid -- including at zero coupling, "
                      "which contradicts job 20600383. Suspect the fixture, not the physics.")
            else:
                out["verdict"] = "GAIN_DEGRADES_WITH_COUPLING"
                print(f"\nThe gain falls below the +0.25 clearance at corr(cos phi, pT) ~ "
                      f"{cross:+.3f} (linear interpolation between bracketing points, crude). "
                      f"THE 08-03 TEST: measure corr(cos phi, pT) in the real FPS sample; if it "
                      f"is below {cross:+.3f} the extension's phi channel still buys something, "
                      f"if above, it does not.")
            print("\nCLOSURE, not data: pseudo-data is a reweighted MC half. This bounds a "
                  "CAPABILITY and is not evidence that the real data carries an azimuthal "
                  "mismatch.")

    os.makedirs(os.path.dirname(cfg.out) or ".", exist_ok=True)
    with open(cfg.out, "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"\n[sweep] wrote {cfg.out}")


if __name__ == "__main__":
    main()
