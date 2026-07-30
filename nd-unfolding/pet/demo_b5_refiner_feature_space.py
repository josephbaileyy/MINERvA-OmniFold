#!/usr/bin/env python3
"""B-5 demonstrator: Stay-Positive is fit on (pT,p‖) but consumed in cloud space.

THE FINDING (AUDIT-FINDINGS-20260729-B.md:228-274, CONFIRMED). The negweight-refined nominal
learns g(x) = D/(D+B) as a function of the reco muon (pT,p‖) ONLY
(`fullevent_fps_dataloader.py:638-640`, `DEFAULT_EVT_FEATURES = ("pt","pparallel")`), refines the
signed measured inventory to non-negative weights, and then attaches those weights to the
concatenated CLOUDS that PET's step-1 classifier actually discriminates on. The refinement's
guarantee covers the 2D muon manifold it was fit on; the classifier sees the cloud.

THE PRESCRIBED CHECK (:268-274, "login-safe, and it is the decisive one"): a synthetic fixture
where data and background share an IDENTICAL (pT,p‖) distribution but have SEPARABLE recoil
clouds; show the 2D refiner fails to recover the known signed cloud distribution while a
cloud-summary-augmented refiner closes it.

WHY THE MUON PROJECTION PASSING IS NOT LUCK. With data and background drawn from the same
(pT,p‖), the classifier cannot separate them there, so it learns the GLOBAL positive fraction
G = D/(D+B) rather than a per-cell one. Then per cell

    w_ref = (d + b) * (2G - 1) = (d + b) * (D - B)/(D + B),   signed = d - b

and because the data/background ratio is by construction the same in every cell,
(d+b)/(D+B) = (d-b)/(D-B), so the two agree EXACTLY. The Gate-2 muon-grid validation therefore
cannot see this defect -- not because the grid is coarse, but because it is the very space the
refiner was fit on. That is the finding, reproduced as an identity rather than a number.

WHY CLIPPING IS NOT THE EXPLANATION. Stay-Positive clips where the true signed density is
negative, and a demonstrator that disagreed only in negative-density bins would be showing the
clip, not the feature-space mismatch. This fixture is therefore built so the true signed cloud
density is POSITIVE in every compared bin, and it FAILS LOUDLY if that does not hold.

LOGIN-SAFE: numpy + sklearn only. No ROOT (the canonical `u2d.refine_stay_positive` imports it),
no TensorFlow, no GPU, no dump. Uses the algorithm-identical `sklearn_refine` shim that the
Gate-2 tests use, so the refinement is the same procedure as production, not a re-derivation.
"""
import argparse
import json
import os
import sys

import numpy as np

_REPO = os.environ.get("MNV_REPO") or os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for _p in (f"{_REPO}/nd-unfolding", f"{_REPO}/nd-unfolding/tests", f"{_REPO}/nd-unfolding/pet"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import fullevent_fps_dataloader as fed          # noqa: E402


def sklearn_refine(feat, signed):
    """Algorithm-identical login-safe stand-in for u2d.refine_stay_positive.

    Copied deliberately rather than imported from tests/test_fullevent_gate2.py: importing that
    module executes its real-dataloader loader shim and mutates sys.modules, which has already
    once silently changed the suite's expected-failure baseline. Same six lines, no side effects.
    """
    from sklearn.ensemble import GradientBoostingClassifier
    feat = np.asarray(feat, float); signed = np.asarray(signed, float)
    lab = (signed > 0).astype(int); absw = np.abs(signed)
    clf = GradientBoostingClassifier(random_state=0)
    clf.fit(feat, lab, sample_weight=absw)
    g = np.clip(clf.predict_proba(feat)[:, 1], 1e-6, 1.0 - 1e-6)
    fac = 2.0 * g - 1.0
    return absw * np.clip(fac, 0.0, None), g, float((fac < 0).mean())


def make_fixture(n_data, n_bkg, pot_scale, bkg_weight, seed):
    """Data and background with the SAME muon (pT,p‖) law and DIFFERENT recoil clouds."""
    rng = np.random.default_rng(seed)

    def muon(n):
        # One law, sampled twice: any per-cell data/background ratio difference would give the
        # 2D refiner real separating power and destroy the identity the demonstrator rests on.
        return np.column_stack([rng.gamma(2.0, 0.45, n), rng.gamma(3.0, 1.6, n)])

    def cloud(n, shape, scale, n_active):
        """(n, 12, 3) = (E, pos, z). Padded tokens are E==0, the loader's mask sentinel."""
        c = np.zeros((n, 12, 3))
        for i in range(n):
            k = min(12, max(1, int(rng.normal(n_active, 1.2))))
            c[i, :k, 0] = rng.gamma(shape, scale, k)          # token energy
            c[i, :k, 1] = rng.normal(0, 1, k)                 # transverse position
            c[i, :k, 2] = rng.normal(0, 1, k)                 # z
        return c

    mu_d, mu_b = muon(n_data), muon(n_bkg)

    # Background clouds are drawn from the DATA law and then tilted by a BOUNDED factor in total
    # recoil energy, rather than from a different law. Two reasons, one physical and one
    # methodological:
    #   physical      -- real background is not a disjoint process in cloud space, it is a
    #                    differently-weighted version of the same hadronic activity;
    #   methodological -- a bounded tilt bounds B/D per bin. With the tilt clipped to
    #                    [1/TILT_CAP, TILT_CAP] and total background weight f times data,
    #                    B/D <= TILT_CAP * f everywhere, so choosing TILT_CAP*f < 1 makes the
    #                    signed density D-B POSITIVE in every bin BY CONSTRUCTION. A fixture
    #                    drawn from a genuinely different law puts background above data wherever
    #                    background happens to concentrate, and then the two arms differ by the
    #                    Stay-Positive CLIP rather than by feature space -- which would prove
    #                    nothing about B-5. (The first version of this fixture did exactly that;
    #                    the guard below caught it.)
    TILT_CAP = 3.0
    pool = cloud(n_bkg * 6, shape=3.0, scale=0.40, n_active=8)
    e_pool = pool[:, :, 0].sum(1)
    med = np.median(e_pool)
    iqr = max(np.percentile(e_pool, 75) - np.percentile(e_pool, 25), 1e-9)
    tilt = np.clip(np.exp(-1.4 * (e_pool - med) / iqr), 1.0 / TILT_CAP, TILT_CAP)
    pick = rng.choice(len(pool), size=n_bkg, replace=False, p=tilt / tilt.sum())
    cl_d = cloud(n_data, shape=3.0, scale=0.40, n_active=8)
    cl_b = pool[pick]

    w_bkg = np.full(n_bkg, bkg_weight)
    ratio_bound = TILT_CAP * (w_bkg.sum() * pot_scale) / float(n_data)
    print(f"[b5] fixture: bounded tilt cap={TILT_CAP}, background/data weight "
          f"f={w_bkg.sum()*pot_scale/n_data:.4f} -> per-bin B/D <= {ratio_bound:.3f} "
          f"({'positive signed density guaranteed' if ratio_bound < 1 else 'NOT GUARANTEED'})")
    return mu_d, mu_b, cl_d, cl_b, w_bkg, pot_scale


def cloud_summaries(cloud):
    """Independent cloud observables the 2D refiner is blind to (B-5:272-274)."""
    E = cloud[:, :, 0]
    live = E > 0
    n_tok = live.sum(1).astype(float)
    e_tot = E.sum(1)
    z = cloud[:, :, 2]
    z_ext = np.where(n_tok > 1, z.max(1) - np.where(live, z, np.inf).min(1), 0.0)
    return np.column_stack([e_tot, n_tok, np.nan_to_num(z_ext)])


def projection(values, weights, edges):
    h, _ = np.histogram(values, bins=edges, weights=weights)
    return h


def compare(name, obs_d, obs_b, edges, w_data, w_bkg_eff, w_ref, n_data):
    """L1 between the refined projection and the KNOWN signed projection, in one observable."""
    signed = projection(obs_d, w_data, edges) - projection(obs_b, w_bkg_eff, edges)
    refined = (projection(obs_d, w_ref[:n_data], edges)
               + projection(obs_b, w_ref[n_data:], edges))
    scale = np.abs(signed).sum()
    return {"observable": name, "l1": float(np.abs(refined - signed).sum()),
            "l1_frac": float(np.abs(refined - signed).sum() / scale),
            "signed_min_bin": float(signed.min()), "signed_total": float(signed.sum()),
            "refined_total": float(refined.sum())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-data", type=int, default=30000)
    ap.add_argument("--n-bkg", type=int, default=12000)
    ap.add_argument("--pot-scale", type=float, default=0.25)
    ap.add_argument("--bkg-weight", type=float, default=1.0)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--bins", type=int, default=20)
    ap.add_argument("--out", default="products/pet/b5_refiner_feature_space.json")
    a = ap.parse_args()

    mu_d, mu_b, cl_d, cl_b, w_bkg, pot = make_fixture(
        a.n_data, a.n_bkg, a.pot_scale, a.bkg_weight, a.seed)
    sm_d, sm_b = cloud_summaries(cl_d), cloud_summaries(cl_b)

    # Signed measured inventory via the PRODUCTION constructor, so the sign convention and the
    # -w_bkg*pot_scale scaling are the shipped ones rather than my restatement of them.
    feat2, signed, n_d, n_b, n_pos, n_neg = fed.build_signed_measured_inventory(
        mu_d, mu_b, w_bkg, pot)
    print(f"[b5] inventory: {n_d} data (+) / {n_b} bkg (-)  pos={n_pos} neg={n_neg}  "
          f"signed sum={signed.sum():.1f}")

    # Muon-space identity precondition: the two legs must be statistically indistinguishable in
    # (pT,p‖), else the 2D refiner has real separating power and the demonstrator proves nothing.
    for j, nm in enumerate(("pT", "p_parallel")):
        qd = np.percentile(mu_d[:, j], [10, 50, 90]); qb = np.percentile(mu_b[:, j], [10, 50, 90])
        print(f"[b5] muon {nm:11s} data q10/50/90 {np.round(qd,3)}  bkg {np.round(qb,3)}")

    w_data = np.ones(a.n_data)
    w_bkg_eff = w_bkg * pot
    e_edges = np.linspace(0, np.percentile(np.r_[sm_d[:, 0], sm_b[:, 0]], 99.5), a.bins + 1)
    pt_edges = np.linspace(0, np.percentile(np.r_[mu_d[:, 0], mu_b[:, 0]], 99.5), a.bins + 1)

    results = {}
    sm_all = np.vstack([sm_d, sm_b])        # row order matches build_signed_measured_inventory
    for arm, feat in (("2d_muon_only", feat2),
                      ("cloud_augmented", np.column_stack([feat2, sm_all]))):
        w_ref, g, frac_clip = sklearn_refine(feat, signed)
        muon_cmp = compare("muon_pT", mu_d[:, 0], mu_b[:, 0], pt_edges,
                           w_data, w_bkg_eff, w_ref, a.n_data)
        cloud_cmp = compare("recoil_E_total", sm_d[:, 0], sm_b[:, 0], e_edges,
                            w_data, w_bkg_eff, w_ref, a.n_data)
        results[arm] = {"n_features": feat.shape[1], "frac_negative_clipped": frac_clip,
                        "g_spread": float(g.std()), "muon": muon_cmp, "cloud": cloud_cmp}
        print(f"\n[b5] arm={arm}  n_feat={feat.shape[1]}  g std={g.std():.5f}  "
              f"clipped={frac_clip:.4f}")
        print(f"[b5]   muon  pT       L1={muon_cmp['l1']:12.4f}  "
              f"({100*muon_cmp['l1_frac']:7.3f}% of |signed|)")
        print(f"[b5]   cloud recoil_E L1={cloud_cmp['l1']:12.4f}  "
              f"({100*cloud_cmp['l1_frac']:7.3f}% of |signed|)")

    # The clip must not be the explanation: require the true signed cloud density positive in
    # every compared bin. If it is not, the arms differ where Stay-Positive is SUPPOSED to clip
    # and the demonstrator is confounded.
    smin = results["2d_muon_only"]["cloud"]["signed_min_bin"]
    if smin < 0:
        raise SystemExit(f"CONFOUNDED: signed cloud density has a negative bin ({smin:.3f}); "
                         "the arms would differ by clipping, not by feature space. Retune.")
    print(f"\n[b5] clip is not the explanation: min signed cloud bin = {smin:.2f} > 0")

    # Predeclared verdict.
    m2 = results["2d_muon_only"]["muon"]["l1_frac"]
    c2 = results["2d_muon_only"]["cloud"]["l1_frac"]
    ca = results["cloud_augmented"]["cloud"]["l1_frac"]
    muon_agrees = m2 < 0.02                 # the refiner reproduces the space it was fit on
    cloud_fails = c2 > 0.10                 # but not the space the classifier sees
    aug_closes = ca < 0.5 * c2              # cloud summaries recover it
    print(f"\n[b5] muon projection agrees (<2%):           {muon_agrees}  ({100*m2:.3f}%)")
    print(f"[b5] cloud projection FAILS (>10%):          {cloud_fails}  ({100*c2:.3f}%)")
    print(f"[b5] augmented refiner closes it (<0.5x):    {aug_closes}  "
          f"({100*ca:.3f}% vs {100*c2:.3f}%)")
    ok = muon_agrees and cloud_fails and aug_closes
    payload = {"config": vars(a), "arms": results,
               "verdict_muon_agrees": bool(muon_agrees),
               "verdict_cloud_fails": bool(cloud_fails),
               "verdict_augmented_closes": bool(aug_closes),
               "verdict": "B5_DEMONSTRATED" if ok else "INCONCLUSIVE"}
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w") as fh:
        json.dump(payload, fh, indent=2)
    print(f"\n[b5] wrote {a.out}")
    if ok:
        print("B-5 DEMONSTRATED: the 2D refiner reproduces (pT,p‖) while missing cloud space; "
              "cloud summaries close it.")
    else:
        print("B-5 INCONCLUSIVE (inspect the three sub-verdicts above).")
        sys.exit(3)


if __name__ == "__main__":
    main()
