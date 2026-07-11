#!/usr/bin/env python
"""LightGBM signed-weight background-subtraction toy (Phase 1b).

Pure numpy + lightgbm, no ROOT, no SLURM. Validates the estimator memo in
bkg_negweight_state.md: that the OmniFold step-1 classifier trained with the
negative-weight-injection construction recovers the density ratio (D-B)/S where
it is positive, and probes stability where the injected background locally
exceeds the data.

Ground-truth 1D setup (analytic densities in expected-event-count units):
  signal MC (class 0, "MCreco"):   N_Smc * phi(x; 0.0, 1.0),      weight +1
  data signal:                     N_Dsig * phi(x; muD, sdD)
  true background (in data):       N_B   * phi(x; muB, sdB)
  pseudo-data D = data signal + background  (drawn samples, weight +1)
  injected bkg MC:                 N_Binj* phi(x; muB, sdB),      weight -N_Binj/n_Bmc

With N_Dsig = N_Smc and matched background (N_Binj = N_B), the target reweight is
  r*(x) = (D - B)/S = phi(x; muD, sdD) / phi(x; 0, 1)     (analytic, closed form)
which is a nontrivial (!=1) smooth positive function everywhere here.

Modes compared, each learning r(x) = p/(1-p) from an LGBM classifier:
  none      : measured = data only, +1        -> should recover D/S (contaminated)
  purity    : measured = data only, weighted by per-bin max(0,(D-B)/D) (current)
  negweight : measured = data(+1) + bkgMC(-w)  (proposed, matched background)
  oversub   : negweight but N_Binj = 1.3 * N_B -> forces a B>D region (stress)
"""
import numpy as np
import lightgbm as lgb
import warnings
warnings.filterwarnings("ignore")

# ---- ground-truth parameters ----
N_SMC  = 40000      # signal MC events (class 0)
N_DSIG = 40000      # signal events in pseudo-data (== N_SMC so r* = phi_D/phi_S)
N_B    = 8000       # true background events in pseudo-data (~17% contamination)
N_BMC  = 40000      # injected background-MC events (POT-scaled, small per-event w)
MU_D, SD_D = 0.30, 1.10     # data-signal Gaussian (reweighted vs MC signal)
MU_B, SD_B = 2.00, 0.70     # background Gaussian
LGBM = dict(n_estimators=200, num_leaves=31, learning_rate=0.05,
            min_child_samples=50, subsample=1.0, verbose=-1, n_jobs=4)


def phi(x, mu, sd):
    return np.exp(-0.5 * ((x - mu) / sd) ** 2) / (sd * np.sqrt(2 * np.pi))


def make_samples(seed, n_binj, mu_b=MU_B, sd_b=SD_B):
    rng = np.random.RandomState(seed)
    mcreco = rng.normal(0.0, 1.0, N_SMC)                         # class 0
    data_sig = rng.normal(MU_D, SD_D, N_DSIG)
    data_bkg = rng.normal(mu_b, sd_b, N_B)                       # true bkg in data
    data = np.concatenate([data_sig, data_bkg])                 # pseudo-data
    bkg_mc = rng.normal(mu_b, sd_b, N_BMC)                       # injected bkg MC
    w_inj = -float(n_binj) / N_BMC                              # signed per-event weight
    return mcreco, data, bkg_mc, w_inj


def fit_reweight(mcreco, meas_x, meas_w, grid, seed):
    """Train class0=mcreco(+1) vs class1=meas(meas_w); return r=p/(1-p) on grid."""
    X = np.concatenate([mcreco, meas_x]).reshape(-1, 1)
    y = np.concatenate([np.zeros(len(mcreco)), np.ones(len(meas_x))])
    w = np.concatenate([np.ones(len(mcreco)), meas_w])
    clf = lgb.LGBMClassifier(random_state=seed, **LGBM)
    clf.fit(X, y, sample_weight=w)
    p = np.clip(clf.predict_proba(grid.reshape(-1, 1))[:, 1], 1e-6, 1 - 1e-6)
    return p / (1.0 - p)


def purity_weights(data, n_bins=40, lo=-4.0, hi=6.0):
    """Per-bin max(0,(D-B)/D) applied to each data event (current binned method)."""
    edges = np.linspace(lo, hi, n_bins + 1)
    # POT-scaled background histogram in the SAME binning (analytic expectation
    # -> use the true background density * bin width * N_B for a clean, low-noise
    #  purity map; the binning discretization is what we are illustrating).
    centers = 0.5 * (edges[:-1] + edges[1:])
    width = edges[1] - edges[0]
    Dhist, _ = np.histogram(data, bins=edges)
    Bhist = N_B * phi(centers, MU_B, SD_B) * width
    wpur_bin = np.where(Dhist > 0, np.maximum(0.0, (Dhist - Bhist) / np.maximum(Dhist, 1e-9)), 0.0)
    idx = np.clip(np.digitize(data, edges) - 1, 0, n_bins - 1)
    return wpur_bin[idx]


def rel_err(learned, truth, mask):
    e = np.abs(learned[mask] / truth[mask] - 1.0)
    return np.median(e), np.percentile(e, 90)


def main():
    grid = np.linspace(-4.0, 6.0, 400)
    S = N_SMC * phi(grid, 0.0, 1.0)
    Dsig = N_DSIG * phi(grid, MU_D, SD_D)
    Bden = N_B * phi(grid, MU_B, SD_B)
    D = Dsig + Bden
    r_target = Dsig / S                      # analytic (D-B)/S with matched bkg
    r_contam = D / S                         # what 'none' should recover

    # validation region: signal well-supported, background-subtracted mass clearly
    # positive (data-signal dominated), decent MC-signal statistics.
    pos = (grid > -3.0) & (grid < 3.0) & (Dsig > 0.05 * D) & (S > 0.02 * S.max())

    print("=" * 78)
    print("LightGBM signed-weight background-subtraction toy")
    print(f"  N_Smc={N_SMC} N_Dsig={N_DSIG} N_B={N_B} (contamination "
          f"{N_B/(N_DSIG+N_B)*100:.1f}%) N_Bmc={N_BMC}")
    print(f"  signal MC ~N(0,1), data signal ~N({MU_D},{SD_D}), bkg ~N({MU_B},{SD_B})")
    print("=" * 78)

    seeds = [0, 1, 2]

    # --- mode: none (no subtraction) ---
    mc, data, _, _ = make_samples(seeds[0], N_B)
    r_none = fit_reweight(mc, data, np.ones(len(data)), grid, seeds[0])
    med_n, p90_n = rel_err(r_none, r_contam, pos)      # vs contaminated D/S
    med_nt, _ = rel_err(r_none, r_target, pos)         # vs clean target (bias)
    print(f"\n[none ] learns D/S (contaminated). "
          f"rel-err vs D/S: med={med_n:.3f} p90={p90_n:.3f}; "
          f"vs clean (D-B)/S: med={med_nt:.3f}  <- contamination bias")

    # --- mode: purity (current binned) ---
    mc, data, _, _ = make_samples(seeds[0], N_B)
    wpur = purity_weights(data)
    r_pur = fit_reweight(mc, data, wpur, grid, seeds[0])
    med_p, p90_p = rel_err(r_pur, r_target, pos)
    print(f"[pur  ] binned max(0,(D-B)/D). "
          f"rel-err vs (D-B)/S: med={med_p:.3f} p90={p90_p:.3f}")

    # --- mode: negweight (proposed, matched bkg), 3 seeds ---
    negw_med, negw_p90 = [], []
    for s in seeds:
        mc, data, bkg_mc, w_inj = make_samples(s, N_B)
        meas_x = np.concatenate([data, bkg_mc])
        meas_w = np.concatenate([np.ones(len(data)), np.full(len(bkg_mc), w_inj)])
        r_neg = fit_reweight(mc, meas_x, meas_w, grid, s)
        m, p = rel_err(r_neg, r_target, pos)
        negw_med.append(m); negw_p90.append(p)
    print(f"[neg  ] negative-weight injection (matched bkg). "
          f"rel-err vs (D-B)/S over seeds {seeds}: "
          f"med={np.mean(negw_med):.3f}+/-{np.std(negw_med):.3f} "
          f"p90={np.mean(negw_p90):.3f}")

    # --- purity vs negweight agreement (same estimand check) ---
    med_pn, p90_pn = rel_err(r_neg, r_pur, pos)
    print(f"[pur~neg] negweight/purity ratio in pos region: "
          f"med={med_pn:.3f} p90={p90_pn:.3f}  (should be small: same estimand)")

    # --- mode: oversub -> forces a genuine B>D region ---
    # A tail background (well outside the signal core) makes even MATCHED
    # subtraction locally over-subtract once statistics thin out; a 1.3x
    # over-injection guarantees a broad D-B<0 region. This is the realistic
    # analogue of the current max(0,.) floor.
    MU_BS, SD_BS = 3.8, 0.5          # tail background for the stress test
    FACTOR = 1.3
    n_binj = int(FACTOR * N_B)
    mc, data, bkg_mc, w_inj = make_samples(seeds[0], n_binj, mu_b=MU_BS, sd_b=SD_BS)
    meas_x = np.concatenate([data, bkg_mc])
    meas_w = np.concatenate([np.ones(len(data)), np.full(len(bkg_mc), w_inj)])
    r_over = fit_reweight(mc, meas_x, meas_w, grid, seeds[0])
    Bden_s = N_B * phi(grid, MU_BS, SD_BS)
    D_s = Dsig + Bden_s
    r_over_true = (D_s - FACTOR * Bden_s) / S      # negative where FACTOR*B > D
    neg_region = (r_over_true < 0) & (grid < 5.0)
    frac_neg = neg_region.mean()
    max_learn_negreg = r_over[neg_region].max() if neg_region.any() else float("nan")
    finite_ok = np.isfinite(r_over).all()
    posO = pos & (r_over_true > 0.05)
    med_o, p90_o = rel_err(r_over, r_over_true, posO)
    print(f"\n[over ] over-subtraction stress: tail bkg ~N({MU_BS},{SD_BS}), "
          f"N_Binj={FACTOR}*N_B. true-negative grid fraction={frac_neg:.2f}")
    print(f"        signal-core region rel-err vs true (D-{FACTOR}B)/S: "
          f"med={med_o:.3f} p90={p90_o:.3f}")
    print(f"        learned reweight max over the true B>D region = "
          f"{max_learn_negreg:.3g}  (>=0: probabilistic classifier structurally "
          f"floors at 0; a post-hoc clip is exact, matching max(0,.))")
    print(f"        all learned reweights finite (no NaN/inf): {finite_ok}; "
          f"no crash -> LGBM tolerates negative sample weights.")
    print(f"        NOTE: floor is structural, not a well-posed fit in B>D; that "
          f"region is where Stay-Positive (negweight-refined) would refine.")
    print("\nDONE")


if __name__ == "__main__":
    main()
