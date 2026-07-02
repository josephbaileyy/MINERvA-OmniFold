#!/usr/bin/env python3
"""PET 5D frozen-reweighter unified throw + matched block-sum.

The GBDT unified throw (unified_throw_cov_5d.py) RE-UNFOLDS each throw, so it
captures the estimator's nonlinear response to the combined systematic shift --
the term that drives the 4D block->unified inflation (x2.01). PET CANNOT reproduce
that term without retraining the network per throw (~160 GPU trainings; infeasible).
This driver therefore measures PET's unified/block factor UNDER THE FROZEN
REWEIGHTER: per throw it composes ONE combined per-event truth reweight (1 Flux
PPFX universe x prod_b knob^{g_b}) and re-bins the frozen PET cloud (PETxsec5D),
exactly as the block-sum bands do -- so the only difference between unified and
block here is the cross-band composition + completeness nonlinearity, NOT a
retraining response.

DOCUMENTED LIMITATION (publication caveat): because the PET reweighter is frozen,
this PET unified/block factor is a LOWER BOUND on the true PET nonlinearity -- it
omits the retraining-response term that dominates the GBDT factor. A symmetric
PET-vs-GBDT unified comparison would require per-throw PET retraining. Read the
GBDT factor (unified_throw_cov_5d.root) alongside this one and disclose the
asymmetry.

Computes, on the new bank_uthrow_5d ratios (matched to the GBDT throw):
  C_block_pet = sum_b outer(x_b - x_cv) + (1/Nflux) sum_u outer(x_u - x_cv)
  C_uni_pet   = (1/T) sum_t outer(x_t - x_cv)        [x_t = combined throw]
Headline PET unified covariance = C_uni_pet + C_stat + C_ML + C_lateral
(stat/ML/lateral copied unchanged from the Phase B pet_5d_covariance_combined_wlat
file -- they do not depend on the vertical reweight construction). Writes
products/pet/pet_5d_covariance_combined_unified_wlat.root + a json summary.

  python pet_unified_throw_5d.py --bank bank_uthrow_5d --throws 160   # compute node, cheap
"""
import argparse
import json
import os
import sys

import numpy as np

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
for _p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from pet_systematics_5d import PETxsec5D

KNOB_BANDS = ["2p2h", "CCQEPauliSupViaKF", "FrAbs_pi", "FrElas_N", "HighQ2",
              "LowQ2", "MaCCQE", "MaRES", "MFP_N", "MvRES", "Rvn2pi", "Rvp2pi"]
RHO_CLIP = (1e-2, 1e2)


def _opt(bank, name):
    p = os.path.join(bank, name)
    return np.load(p).astype(np.float64) if os.path.exists(p) else None


def _clip(rho):
    rho = np.where(np.isfinite(rho) & (rho > 0), rho, 1.0)
    return np.clip(rho, *RHO_CLIP)


def _th2(h):
    import numpy as np
    n = h.GetNbinsX()
    a = np.empty((n, n))
    for i in range(n):
        for k in range(n):
            a[i, k] = h.GetBinContent(i + 1, k + 1)
    return a


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pc", default="of_inputs_pc.npz")
    ap.add_argument("--w-source", default="of_inputs_5d.npz")
    ap.add_argument("--weights", default="products/pet/pet_weights_full.npz")
    ap.add_argument("--bank", default="bank_uthrow_5d")
    ap.add_argument("--mcfile", default=f"{_REPO}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root")
    ap.add_argument("--flux-hist", default="pTmu_reweightedflux_integrated")
    ap.add_argument("--comp-ref", default="products/5d/xsec_5d_MEFHC_5iter_lgbm.root")
    ap.add_argument("--phaseB", default="products/pet/pet_5d_covariance_combined_wlat.root",
                    help="Phase B PET combined cov: source of C_stat/C_ML/C_lateral")
    ap.add_argument("--throws", type=int, default=160)
    ap.add_argument("--seed", type=int, default=1000)
    ap.add_argument("--out-root", default="products/pet/pet_5d_covariance_combined_unified_wlat.root")
    args = ap.parse_args()

    pet = PETxsec5D(args.pc, args.weights, args.mcfile, args.flux_hist, args.w_source, args.comp_ref)
    x_cv = pet.xsec(None)
    rep = x_cv > 0
    base = x_cv[rep]
    nrep = int(rep.sum())
    print(f"[petuni] CV reported bins = {nrep}")

    # bank: truth-side knob ratios (PET uses the truth reweight only) + flux universes
    bands = [b for b in KNOB_BANDS if os.path.exists(os.path.join(args.bank, f"sig_{b}_t_1.npy"))]
    log_t = {b: np.log(_clip(_opt(args.bank, f"sig_{b}_t_1.npy"))) for b in bands}
    nflux = 0
    while os.path.exists(os.path.join(args.bank, f"sig_flux_t_{nflux}.npy")):
        nflux += 1
    print(f"[petuni] bank: {len(bands)} knob bands, {nflux} flux universes")
    if len(bands) < len(KNOB_BANDS) or nflux == 0:
        raise SystemExit(f"[FAIL] incomplete bank: {len(bands)}/{len(KNOB_BANDS)} knobs, {nflux} flux")

    # ---- matched block-sum (same frozen reweighter) ----
    C_block = np.zeros((nrep, nrep))
    for b in bands:
        delta = pet.xsec(_clip(_opt(args.bank, f"sig_{b}_t_1.npy")))[rep] - base
        C_block += np.outer(delta, delta)
        print(f"[block] {b}: ||d||={np.linalg.norm(delta):.3e}", flush=True)
    fX = np.array([pet.xsec(_clip(_opt(args.bank, f"sig_flux_t_{u}.npy")))[rep] - base
                   for u in range(nflux)])
    C_block += (fX.T @ fX) / nflux
    print(f"[block] flux ({nflux}) added")

    # ---- unified throw (combined per-event reweight per throw) ----
    xs = []
    for j in range(args.throws):
        rng = np.random.default_rng(args.seed + j)
        lt = np.zeros_like(base, shape=log_t[bands[0]].shape)
        for b in bands:
            lt = lt + rng.standard_normal() * log_t[b]
        rho = np.exp(lt)
        u = int(rng.integers(nflux))
        rho = rho * _clip(_opt(args.bank, f"sig_flux_t_{u}.npy"))
        xs.append(pet.xsec(_clip(rho))[rep])
        if j % 20 == 0:
            print(f"[throw {j}] flux_u={u}", flush=True)
    X = np.array(xs)
    dX = X - base[None, :]
    C_uni = (dX.T @ dX) / args.throws

    st_uni = float(np.sqrt(np.trace(C_uni)))
    st_block = float(np.sqrt(np.trace(C_block)))
    du = np.sqrt(np.clip(np.diag(C_uni), 0, None))
    db = np.sqrt(np.clip(np.diag(C_block), 0, None))
    med_ratio = float(np.median(du[db > 0] / db[db > 0]))
    print("\n===== PET unified-throw vs block-sum (frozen reweighter) =====")
    print(f"  sqrt-trace unified={st_uni:.4e}  block={st_block:.4e}  ratio={st_uni/st_block:.3f}")
    print(f"  per-bin sigma ratio unified/block: median={med_ratio:.3f}")
    print("  (frozen reweighter -> LOWER BOUND on PET nonlinearity; omits retraining response)")

    # ---- assemble headline: C_uni + Phase B stat/ML/lateral ----
    import ROOT
    fb = ROOT.TFile.Open(args.phaseB)
    blk = {nm: _th2(fb.Get(nm)) for nm in ("C_stat", "C_ML", "C_lateral")}
    cvflat = np.array([fb.Get("hXSec_cv_flat").GetBinContent(i + 1) for i in range(nrep)])
    fb.Close()
    rel = np.abs(base - cvflat) / np.where(cvflat != 0, np.abs(cvflat), 1)
    if rel.max() > 1e-4:
        raise SystemExit(f"[FAIL] Phase B CV mismatch (max rel {rel.max():.2e}) -- mask/order differ")
    C_total = C_uni + blk["C_stat"] + blk["C_ML"] + blk["C_lateral"]
    for nm, C in [("syst_unified", C_uni), ("syst_block", C_block), ("stat", blk["C_stat"]),
                  ("ML", blk["C_ML"]), ("lateral", blk["C_lateral"]), ("total", C_total)]:
        med = float(np.median(np.sqrt(np.clip(np.diag(C), 0, None))[base > 0] / base[base > 0]))
        print(f"[cov] {nm:13s} sqrt-trace={np.sqrt(max(np.trace(C),0)):.4e}  median frac={100*med:.1f}%")

    os.makedirs(os.path.dirname(args.out_root) or ".", exist_ok=True)
    fo = ROOT.TFile.Open(args.out_root, "RECREATE")
    for nm, C in [("C_syst", C_uni), ("C_syst_block", C_block), ("C_stat", blk["C_stat"]),
                  ("C_ML", blk["C_ML"]), ("C_lateral", blk["C_lateral"]), ("C_total", C_total)]:
        h = ROOT.TH2D(nm, nm, nrep, 0, nrep, nrep, 0, nrep)
        for i in range(nrep):
            for k in range(nrep):
                h.SetBinContent(i + 1, k + 1, float(C[i, k]))
        h.Write()
    hcv = ROOT.TH1D("hXSec_cv_flat", "PET CV xsec (reported bins)", nrep, 0, nrep)
    for i in range(nrep):
        hcv.SetBinContent(i + 1, float(base[i]))
    hcv.Write()
    ROOT.TParameter("int")("n_reported", nrep).Write()
    ROOT.TParameter("double")("pet_unified_block_ratio", st_uni / st_block).Write()
    fo.Close()
    summary = {
        "n_reported": nrep, "throws": args.throws,
        "pet_sqrt_tr_unified": st_uni, "pet_sqrt_tr_block": st_block,
        "pet_unified_block_ratio": st_uni / st_block, "pet_unified_block_median_sigma_ratio": med_ratio,
        "limitation": "frozen reweighter: PET unified/block omits the retraining-response nonlinearity "
                      "(lower bound); GBDT factor in uq_5d/unified_throw_cov_5d.root is the re-unfolded one.",
        "out_root": args.out_root,
    }
    with open(os.path.splitext(args.out_root)[0] + "_summary.json", "w") as fh:
        json.dump(summary, fh, indent=2)
    print(f"[petuni] wrote {args.out_root}")


if __name__ == "__main__":
    main()
