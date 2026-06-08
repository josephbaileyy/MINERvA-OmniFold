#!/usr/bin/env python3
"""Rigorous many-throw unified systematic covariance vs the block-sum (prepub #1).

The block-sum cov assumes the unfolding responds LINEARLY to each band, so
C_total = sum_b C_b. The decisive test is a TRUE unified throw: shift ALL bands
together per universe, re-unfold, and build the covariance directly. In the linear
regime C_unified == C_blocksum exactly; the difference is the unfolding's nonlinear
cross-band term.

The 2026-06-04 ratio-product proxy was artifact-prone because it multiplied BINNED
spectrum ratios (low-w_cv tail events compounded -> 25x inflation). This driver
avoids that by composing weights at the PER-EVENT level and RE-UNFOLDING each throw
(the proper construction a multi-band event-loop universe would produce, for the
reweight/vertical systematics):

    throw j:  g_b ~ N(0,1) per +-1sigma knob band b;  u ~ U{0..Nflux-1}
    w_truth^(j) = w_truth * prod_b (wt_b/w_truth)^{g_b} * (wt_flux_u/w_truth)
    (same for w_reco and the truth-denom weights), clipped per event for positivity
    x_j = OmniFold-reunfold(w^(j))   [compare_unified_throw._xsec_for_weights]

Reads the per-event bank produced for the superposition probe (bank_uthrow/): cv.npz
(MCgen/MCreco/measured/pass_*/w_*/td_*/edges/flux/...) + per-band absolute universe
weights sig_<band>_{t,r}_<idx>.npy, td_<band>_<idx>.npy, flux as 100 universes.

Two phases (throws array-parallelise; combine aggregates):
  # one array task -> a slab of throws
  python unified_throw_cov.py --throws 8 --throw-offset 0 --seed 1000 \
      --bank bank_uthrow --iters 5 --out uthrow_slab_0.npz
  # after all slabs land
  python unified_throw_cov.py --combine 'uthrow_slab_*.npz' --bank bank_uthrow \
      --iters 5 --out-root uq_4d/unified_throw_cov.root
"""
import argparse
import glob
import os
import sys

import numpy as np

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
for _p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from compare_unified_throw import _xsec_for_weights

# +-1sigma reweight knobs (each has idx 0 and 1 in the bank; idx 1 = +1sigma).
# Flux is handled separately as a 100-universe set.
KNOB_BANDS = ["2p2h", "CCQEPauliSupViaKF", "FrAbs_pi", "FrElas_N", "HighQ2",
              "LowQ2", "MaCCQE", "MaRES", "MFP_N", "MvRES", "Rvn2pi", "Rvp2pi"]
RHO_CLIP = (1e-2, 1e2)     # per-event ratio clip (positivity / tail guard)


def _opt(bank, name):
    p = os.path.join(bank, name)
    return np.load(p).astype(np.float64) if os.path.exists(p) else None


def _load_bank(bank):
    """Return (d, bands, n_flux) WITHOUT loading any weight arrays into memory.
    d is the cv dict for _xsec_for_weights; bands = available knob names; n_flux =
    number of available flux universes. Weight arrays are loaded lazily (the full
    set is ~80 GB in float64 -- never hold them all)."""
    cv = np.load(os.path.join(bank, "cv.npz"))
    d = {k: cv[k] for k in cv.files}
    nedges = sum(1 for k in cv.files if k.startswith("edges_"))
    d["edges"] = [cv[f"edges_{i}"] for i in range(nedges)]
    bands = [b for b in KNOB_BANDS
             if all(os.path.exists(os.path.join(bank, f"{p}.npy"))
                    for p in (f"sig_{b}_t_1", f"sig_{b}_r_1", f"td_{b}_1"))]
    n_flux = 0
    while all(os.path.exists(os.path.join(bank, f"{p}.npy"))
              for p in (f"sig_flux_t_{n_flux}", f"sig_flux_r_{n_flux}", f"td_flux_{n_flux}")):
        n_flux += 1
    print(f"[bank] {len(bands)} knob bands, {n_flux} flux universes, "
          f"{d['MCgen'].shape[0]} events, edges {[len(e)-1 for e in d['edges']]}")
    return d, bands, n_flux


def _clip(rho):
    """The bank stores per-event universe/CV RATIOS (verified: sig_*_t_1 median=1).
    Clip positive for log/exp composition (and guard NaN/inf -> 1)."""
    rho = np.where(np.isfinite(rho) & (rho > 0), rho, 1.0)
    return np.clip(rho, *RHO_CLIP)


def _knob_logs(bank, bands, w_truth, w_reco, td_cv):
    """Per-band float32 log-RATIOS for the +1sigma knobs (bank values ARE ratios);
    raw arrays freed after each band (peak mem = one band's three arrays)."""
    log_t, log_r, log_td = {}, {}, {}
    for b in bands:
        log_t[b] = np.log(_clip(_opt(bank, f"sig_{b}_t_1.npy"))).astype(np.float32)
        log_r[b] = np.log(_clip(_opt(bank, f"sig_{b}_r_1.npy"))).astype(np.float32)
        log_td[b] = np.log(_clip(_opt(bank, f"td_{b}_1.npy"))).astype(np.float32)
    return log_t, log_r, log_td


def _flux_universe(bank, u):
    """Lazy-load the three weight arrays for flux universe u."""
    return (_opt(bank, f"sig_flux_t_{u}.npy"),
            _opt(bank, f"sig_flux_r_{u}.npy"),
            _opt(bank, f"td_flux_{u}.npy"))


def do_throws(args):
    d, bands, n_flux = _load_bank(args.bank)
    edges = d["edges"]
    w_truth, w_reco, td_cv = d["w_truth"], d["w_reco"], d["td_w"]
    # precompute per-band float32 log-ratios for the knobs (g-exponentiated per throw)
    log_t, log_r, log_td = _knob_logs(args.bank, bands, w_truth, w_reco, td_cv)

    xs = []
    metas = []
    for j in range(args.throws):
        gj = args.throw_offset + j
        rng = np.random.default_rng(args.seed + gj)
        g = {b: float(rng.standard_normal()) for b in bands}
        lt = np.zeros_like(w_truth); lr = np.zeros_like(w_reco); ltd = np.zeros_like(td_cv)
        for b in bands:
            lt += g[b] * log_t[b]; lr += g[b] * log_r[b]; ltd += g[b] * log_td[b]
        wt_j = w_truth * np.exp(lt); wr_j = w_reco * np.exp(lr); wtd_j = td_cv * np.exp(ltd)
        if n_flux:
            u = int(rng.integers(n_flux))
            fwt, fwr, fwtd = _flux_universe(args.bank, u)
            wt_j *= _clip(fwt); wr_j *= _clip(fwr); wtd_j *= _clip(fwtd)
        else:
            u = -1
        x = _xsec_for_weights(d, edges, wt_j, wr_j, wtd_j, args.iters, args.seed + 1000 + gj)
        xs.append(x.ravel(order="C"))
        metas.append((gj, u))
        print(f"[throw {gj}] flux_u={u} sum(x)={x.sum():.4e}", flush=True)
        # save incrementally so a killed job (e.g. interactive alloc expiry) keeps
        # every completed throw rather than losing the whole slab.
        np.savez_compressed(args.out, xs=np.array(xs),
                            throws=np.array([m[0] for m in metas]),
                            flux_u=np.array([m[1] for m in metas]),
                            bands=np.array(bands, dtype=object))
    print(f"[throws] wrote {args.out}: xs{np.array(xs).shape}")


def do_blockunits(args):
    """Producer for the block-sum: compute the xsec vector for each assigned
    block universe (knob +1sigma and/or flux index) and save them. Parallelises
    the otherwise-serial 112-unfold block-sum exactly like the throws. Combine
    aggregates these. --block-knobs all|csv ; --block-flux LO-HI (inclusive)."""
    d, bands, n_flux = _load_bank(args.bank)
    edges = d["edges"]
    w_truth, w_reco, td_cv = d["w_truth"], d["w_reco"], d["td_w"]
    xs, labels, kinds = [], [], []

    knob_list = bands if args.block_knobs == "all" else [b for b in args.block_knobs.split(",") if b in bands]
    for b in knob_list:
        wt = w_truth * _clip(_opt(args.bank, f"sig_{b}_t_1.npy"))
        wr = w_reco * _clip(_opt(args.bank, f"sig_{b}_r_1.npy"))
        wtd = td_cv * _clip(_opt(args.bank, f"td_{b}_1.npy"))
        x = _xsec_for_weights(d, edges, wt, wr, wtd, args.iters, args.seed).ravel(order="C")
        xs.append(x); labels.append(b); kinds.append("knob")
        print(f"[blockunit] knob {b} done", flush=True)
        np.savez_compressed(args.out, xs=np.array(xs), labels=np.array(labels, dtype=object),
                            kinds=np.array(kinds, dtype=object))
    if args.block_flux:
        lo, hi = (int(x) for x in args.block_flux.split("-"))
        for u in range(lo, min(hi, n_flux - 1) + 1):
            fwt, fwr, fwtd = _flux_universe(args.bank, u)
            x = _xsec_for_weights(d, edges, w_truth * _clip(fwt), w_reco * _clip(fwr),
                                  td_cv * _clip(fwtd), args.iters, args.seed).ravel(order="C")
            xs.append(x); labels.append(f"flux{u}"); kinds.append("flux")
            print(f"[blockunit] flux {u} done", flush=True)
            np.savez_compressed(args.out, xs=np.array(xs), labels=np.array(labels, dtype=object),
                                kinds=np.array(kinds, dtype=object))
    print(f"[blockunit] wrote {args.out}: {len(xs)} units")


def do_combine(args):
    d, bands, n_flux = _load_bank(args.bank)
    edges = d["edges"]
    w_truth, w_reco, td_cv = d["w_truth"], d["w_reco"], d["td_w"]

    # CV xsec (reported-bin mask)
    x_cv = _xsec_for_weights(d, edges, w_truth, w_reco, td_cv, args.iters, args.seed).ravel(order="C")
    rep = x_cv > 0
    base = x_cv[rep]
    nrep = int(rep.sum())
    print(f"[combine] reported bins = {nrep}")

    # unified covariance over all throws
    slabs = sorted(glob.glob(args.combine))
    if not slabs:
        raise SystemExit(f"no slabs match {args.combine}")
    X = np.concatenate([np.load(s, allow_pickle=True)["xs"] for s in slabs], axis=0)[:, rep]
    T = X.shape[0]
    dX = X - base[None, :]
    C_uni = (dX.T @ dX) / T
    print(f"[combine] {T} throws from {len(slabs)} slabs")

    # block-sum covariance from precomputed block-unit slabs (knobs summed as
    # outer(delta); flux averaged then added). Falls back to inline if no slabs.
    C_block = np.zeros((nrep, nrep))
    bslabs = sorted(glob.glob(args.block_slabs)) if args.block_slabs else []
    if not bslabs:
        raise SystemExit(f"no block-unit slabs match {args.block_slabs}; run --blockunits first")
    fX = []
    n_knob = 0
    for s in bslabs:
        z = np.load(s, allow_pickle=True)
        for x, kind in zip(z["xs"], z["kinds"]):
            delta = x[rep] - base
            if str(kind) == "knob":
                C_block += np.outer(delta, delta); n_knob += 1
            else:
                fX.append(delta)
    if fX:
        fX = np.array(fX)
        C_flux = (fX.T @ fX) / len(fX)
        C_block += C_flux
        print(f"[block] {n_knob} knobs + flux ({len(fX)} univ, sqrt-tr={np.sqrt(np.trace(C_flux)):.3e})")
    else:
        print(f"[block] {n_knob} knobs (no flux units)")

    st_uni = float(np.sqrt(np.trace(C_uni)))
    st_block = float(np.sqrt(np.trace(C_block)))
    tr_uni = float(np.trace(C_uni))

    # JITTER CORRECTION. The throws each re-unfold at a DIFFERENT seed, so their
    # OmniFold run-to-run jitter does NOT cancel against x_cv; the block units +
    # x_cv all share one seed, so their jitter cancels in (x_b - x_cv). That makes
    # the raw unified trace jitter-inflated relative to the block sum. With two CV
    # unfolds at different seeds, E||x_cv2 - x_cv1||^2 = 2*sum_bin sigma_jit^2, and
    # each throw's d_t = x_t - x_cv carries +2*sum sigma_jit^2 in expectation, so
    # the jitter-free systematic trace is  tr(C_uni) - ||Dcv||^2.
    jit_trace = None
    if args.null:
        x_cv2 = _xsec_for_weights(d, edges, w_truth, w_reco, td_cv, args.iters,
                                  args.seed + 7).ravel(order="C")[rep]
        jit_trace = float(np.sum((x_cv2 - base) ** 2))
        tr_uni_corr = max(tr_uni - jit_trace, 0.0)
        st_uni_corr = float(np.sqrt(tr_uni_corr))
        print(f"\n[null] jitter floor ||x_cv(s+7)-x_cv||^2 = {jit_trace:.3e}  "
              f"(= 2*sum sigma_jit^2); sqrt = {np.sqrt(jit_trace):.3e}")

    # cross term = unified - block (the nonlinear piece block-sum drops)
    C_cross = C_uni - C_block
    st_cross = float(np.sqrt(abs(np.trace(C_cross))))
    du = np.sqrt(np.clip(np.diag(C_uni), 0, None))
    db = np.sqrt(np.clip(np.diag(C_block), 0, None))
    med_ratio = float(np.median(du[db > 0] / db[db > 0]))
    print("\n===== Unified-throw vs block-sum =====")
    print(f"  sqrt-trace  unified={st_uni:.4e}  block={st_block:.4e}  "
          f"raw ratio={st_uni/st_block:.3f}")
    if jit_trace is not None:
        print(f"  jitter-corrected unified sqrt-trace={st_uni_corr:.4e}  "
              f"corrected ratio={st_uni_corr/st_block:.3f}")
    print(f"  sqrt-trace cross-term (unified-block) = {st_cross:.4e}  "
          f"({100*st_cross/st_block:.1f}% of block)")
    print(f"  per-bin sigma ratio unified/block: median={med_ratio:.3f}")
    print("  (the jitter-corrected ratio is the block-sum-vs-unified test: throws re-unfold "
          "at independent seeds while block units share the CV seed, so subtract the jitter "
          "floor before comparing. ratio>>1 => the unfolding combines bands NONLINEARLY and "
          "the block-sum underestimates; ratio~1 => block-sum is a good approximation.)")

    if args.out_root:
        import ROOT
        os.makedirs(os.path.dirname(args.out_root) or ".", exist_ok=True)
        fo = ROOT.TFile.Open(args.out_root, "RECREATE")
        for name, M in [("C_unified", C_uni), ("C_blocksum", C_block), ("C_cross", C_cross)]:
            h = ROOT.TH2D(name, name, nrep, 0, nrep, nrep, 0, nrep)
            for i in range(nrep):
                for k in range(nrep):
                    h.SetBinContent(i + 1, k + 1, float(M[i, k]))
            h.Write()
        ROOT.TParameter("double")("sqrt_tr_unified", st_uni).Write()
        ROOT.TParameter("double")("sqrt_tr_block", st_block).Write()
        ROOT.TParameter("int")("n_throws", T).Write()
        fo.Close()
        print(f"[combine] wrote {args.out_root}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bank", default="bank_uthrow")
    ap.add_argument("--throws", type=int, default=0, help="number of throws this task")
    ap.add_argument("--throw-offset", type=int, default=0)
    ap.add_argument("--seed", type=int, default=1000)
    ap.add_argument("--iters", type=int, default=5)
    ap.add_argument("--out", default="uthrow_slab.npz")
    ap.add_argument("--combine", default=None, help="glob of throw slab npzs to aggregate")
    ap.add_argument("--block-slabs", default=None, help="glob of block-unit slabs (combine)")
    ap.add_argument("--blockunits", action="store_true", help="producer for block-sum units")
    ap.add_argument("--block-knobs", default="all", help="all|csv of knob bands")
    ap.add_argument("--block-flux", default=None, help="flux index range LO-HI (inclusive)")
    ap.add_argument("--null", action="store_true",
                    help="(combine) also unfold a 2nd CV at seed+7 to measure + subtract "
                         "the OmniFold jitter floor from the unified trace")
    ap.add_argument("--out-root", default=None)
    args = ap.parse_args()
    if args.combine:
        do_combine(args)
    elif args.blockunits:
        do_blockunits(args)
    elif args.throws > 0:
        do_throws(args)
    else:
        ap.error("pass --throws N, --blockunits, or --combine GLOB")


if __name__ == "__main__":
    main()
