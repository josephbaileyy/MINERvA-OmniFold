#!/usr/bin/env python3
"""5D PET FPS 3-prior envelope (step 3, the DOMINANT extrapolation systematic).

The 5D point-cloud analogue of fps_prior_envelope.py, driven through the FROZEN
PET reweighter (PETxsec5D.xsec(rho)): the full-stats FPS push weights w_push are
held FIXED, and each prior enters ONLY as a per-event truth reweight rho -- so all
three priors are re-binned from the SAME trained network, no re-inference.

  priors:  MnvTune (headline)   rho = 1
           bare-GENIE           rho = fps_prior_genie_ratio_5d.npz  (unweighted/tuned shape)
           NuWro-shaped         rho = fps_prior_nuwro_ratio_5d.npz  (NuWro/tuned shape)
  rho per event = 4D bin lookup on (pT, p||, Eavail, W) in the prior's PT_EXT grid
                  (the per-event LOOKUP grid; the xsec is REPORTED on the 65856 grid).

Model dependence = per-bin spread across the three unfolded xsecs. It is ~0 where
data constrains the answer (high completeness) and blooms where the result is
prior-driven (low completeness = the extrapolation region the FPS headline exposes),
so we report two-tier stratified by PET completeness.

Everything is expressed at the PER-EVENT-WEIGHT level: the per-event rho arrays are
saved, so any downstream observable re-binned from w_push*w_truth*rho inherits the
same 3-prior band without re-running OmniFold.

  python fps_3prior_envelope_5d.py     # -> products/pet/fps_envelope_5d/
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


def _rho_lookup(truth, ratio_npz):
    """Per-event rho = 4D (pT,p||,Eavail,W) bin lookup; rho=1 outside the grid."""
    d = np.load(ratio_npz)
    R = d["ratio"]
    ept, epz, eea, eW = d["edges_pt"], d["edges_pz"], d["edges_eav"], d["edges_W"]
    pt, pz, ea, W = truth[:, 0], truth[:, 1], truth[:, 2], truth[:, 4]
    ip = np.digitize(pt, ept) - 1
    iz = np.digitize(pz, epz) - 1
    ie = np.digitize(ea, eea) - 1
    iw = np.digitize(W, eW) - 1
    inb = ((ip >= 0) & (ip < R.shape[0]) & (iz >= 0) & (iz < R.shape[1])
           & (ie >= 0) & (ie < R.shape[2]) & (iw >= 0) & (iw < R.shape[3]))
    rho = np.ones(truth.shape[0], np.float64)
    ipc, izc, iec, iwc = (np.clip(ip, 0, R.shape[0] - 1), np.clip(iz, 0, R.shape[1] - 1),
                          np.clip(ie, 0, R.shape[2] - 1), np.clip(iw, 0, R.shape[3] - 1))
    vals = R[ipc, izc, iec, iwc]
    rho[inb] = vals[inb]
    rho[~np.isfinite(rho)] = 1.0
    return rho, int(inb.sum())


def main():
    from pet_systematics_5d import PETxsec5D
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pc", default="of_inputs_pc_fps.npz")
    ap.add_argument("--weights", default="products/pet/pet_weights_fps.npz")
    ap.add_argument("--w-source", default="of_inputs_5d_fps.npz")
    ap.add_argument("--nuwro", default="products/5d/fps_prior_nuwro_ratio_5d.npz")
    ap.add_argument("--genie", default="products/5d/fps_prior_genie_ratio_5d.npz")
    ap.add_argument("--mcfile", default=f"{_REPO}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root")
    ap.add_argument("--flux-hist", default="pTmu_reweightedflux_integrated")
    ap.add_argument("--comp-split", type=float, default=0.5,
                    help="completeness threshold: >= is 'measured', < is 'prior-extrapolated'")
    ap.add_argument("--outdir", default="products/pet/fps_envelope_5d")
    ap.add_argument("--save-weights", action="store_true",
                    help="also save per-event rho arrays (per-event-weight-level band)")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    # frozen FPS reweighter; comp_ref=None -> no GBDT anchor (the fractional envelope
    # is invariant to the fixed per-bin completeness rescale, which cancels in the ratio).
    pet = PETxsec5D(args.pc, args.weights, args.mcfile, args.flux_hist, args.w_source, None)
    truth = pet.truth

    rho_g, ng = _rho_lookup(truth, args.genie)
    rho_n, nn = _rho_lookup(truth, args.nuwro)
    print(f"[env5d] rho lookup: genie in-grid {ng}/{truth.shape[0]}  nuwro in-grid {nn}")

    x_tune = pet.xsec(None)
    x_gen = pet.xsec(rho_g)
    x_nu = pet.xsec(rho_n)
    comp = (pet._comp(pet.w_truth) * pet.comp_rescale).ravel(order="C")

    stack = np.stack([x_tune, x_gen, x_nu])
    ok = np.all(stack > 0, axis=0)
    mean = stack[:, ok].mean(axis=0)
    half = 0.5 * (stack[:, ok].max(axis=0) - stack[:, ok].min(axis=0))
    env = half / mean
    comp_ok = comp[ok]

    def _tier(name, m):
        d = env[m]
        if d.size == 0:
            print(f"[env5d] {name:22s} n=0"); return {}
        s = {"n": int(m.sum()), "median": float(np.median(d)),
             "p90": float(np.percentile(d, 90)), "max": float(d.max())}
        print(f"[env5d] {name:22s} n={s['n']:5d}  half-spread/mean: "
              f"median={100*s['median']:.2f}%  p90={100*s['p90']:.2f}%  max={100*s['max']:.1f}%")
        return s

    from xsec_nd import total_xsec
    integ = lambda x: total_xsec(x.reshape(pet.shape, order="C"), pet.edges)
    print(f"[env5d] total sigma  tune={integ(x_tune):.4e}  "
          f"genie={integ(x_gen):.4e}  nuwro={integ(x_nu):.4e}")
    summary = {
        "n_reported_all3pos": int(ok.sum()),
        "comp_split": args.comp_split,
        "priors": ["MnvTune(headline,rho=1)", "bareGENIE(unweighted/tuned)", "NuWro(shape/tuned)"],
        "mechanism": "frozen PET reweighter (w_push fixed); prior = per-event truth rho; "
                     "reported on 65856 grid, rho looked up on PT_EXT grid",
        "all": _tier("all reported cells", np.ones(env.size, bool)),
        "measured (comp>=%.2f)" % args.comp_split: _tier(f"measured comp>={args.comp_split}",
                                                          comp_ok >= args.comp_split),
        "extrapolated (comp<%.2f)" % args.comp_split: _tier(f"extrapolated comp<{args.comp_split}",
                                                            comp_ok < args.comp_split),
    }
    # completeness-stratified profile (shows the model-dependence blooming as data thins)
    prof = []
    for lo, hi in [(0.0, 0.1), (0.1, 0.3), (0.3, 0.5), (0.5, 0.7), (0.7, 1.01)]:
        m = (comp_ok >= lo) & (comp_ok < hi)
        if m.any():
            prof.append({"comp": f"[{lo},{hi})", "n": int(m.sum()),
                         "median_env_pct": float(100 * np.median(env[m]))})
    summary["completeness_profile"] = prof

    # ---- save (per-bin envelope + optional per-event rho for observable projection) ----
    grid_idx = np.where(ok)[0]
    np.savez_compressed(os.path.join(args.outdir, "fps_envelope_5d.npz"),
                        env=env, comp=comp_ok, grid_idx=grid_idx,
                        x_tune=x_tune[ok], x_genie=x_gen[ok], x_nuwro=x_nu[ok],
                        comp_split=args.comp_split)
    if args.save_weights:
        np.savez_compressed(os.path.join(args.outdir, "fps_envelope_5d_rho.npz"),
                            rho_genie=rho_g.astype(np.float32), rho_nuwro=rho_n.astype(np.float32),
                            note="per-event truth reweights; effective weight = w_push*w_truth*rho")
    with open(os.path.join(args.outdir, "fps_envelope_5d_summary.json"), "w") as fh:
        json.dump(summary, fh, indent=2)
    print(f"[env5d] wrote {args.outdir}/fps_envelope_5d.npz + summary.json"
          + (" + rho.npz" if args.save_weights else ""))

    # ---- figure: envelope vs completeness + per-axis mean-envelope projection ----
    try:
        import pathlib
        for _a in pathlib.Path(__file__).resolve().parents:
            if (_a / "technote_style.py").exists():
                sys.path.insert(0, str(_a)); break
        import technote_style  # noqa: F401
    except Exception:
        pass
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    GRID = (14, 16, 7, 7, 6)
    AXL = [r"$p_T$", r"$p_\parallel$", r"$E_{avail}$", r"$q_3$", r"$W$"]
    fig, axes = plt.subplots(2, 3, figsize=(13, 7))
    ax = axes[0, 0]
    cb = np.linspace(0, 1, 11)
    cc = 0.5 * (cb[1:] + cb[:-1])
    med = [100 * np.median(env[(comp_ok >= cb[i]) & (comp_ok < cb[i + 1])])
           if ((comp_ok >= cb[i]) & (comp_ok < cb[i + 1])).any() else np.nan for i in range(len(cb) - 1)]
    ax.plot(cc, med, "o-")
    ax.axvline(args.comp_split, color="C3", ls="--", lw=1)
    ax.set_xlabel("PET completeness"); ax.set_ylabel("median 3-prior spread/mean (%)")
    ax.set_title("model dependence vs data constraint")
    # per-axis mean-envelope projections
    full = np.unravel_index(grid_idx, GRID, order="C")
    for a in range(5):
        r, c = divmod(a + 1, 3)
        axx = axes[r, c]
        na = GRID[a]
        m = np.array([np.median(env[full[a] == b]) * 100 if (full[a] == b).any() else np.nan
                      for b in range(na)])
        axx.plot(range(na), m, "s-")
        axx.set_xlabel(f"{AXL[a]} bin"); axx.set_ylabel("median spread (%)")
    fig.tight_layout()
    p = os.path.join(args.outdir, "fps_envelope_5d.png")
    fig.savefig(p, dpi=130, bbox_inches="tight"); plt.close(fig)
    print(f"[env5d] wrote {p}")


if __name__ == "__main__":
    main()
