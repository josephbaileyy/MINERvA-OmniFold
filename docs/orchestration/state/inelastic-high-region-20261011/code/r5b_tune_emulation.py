"""A1-d: first-order emulation of the GENIE G18_02a_02_11b inelastic parameters on GENIE 2.12.10 CV events.

Reweights existing events only (PLAN.md §8, amendment 2): RES x 0.84; DIS x 1.062/1.032; nonresonant DIS events
(generator W < 1.7 GeV) with primary hadronic multiplicity ni = 2 or 3 x R_new/R_old by struck nucleon. W_cut and
RES-Ma changes are omitted. Writes a 5D cell-integrated array of the emulated prediction and of the nominal
rebuild (control), both on the committed grid, to OUTDIR.

Usage: python3 r5b_tune_emulation.py OUTDIR
"""
import json
import os
import resource
import sys

sys.dont_write_bytecode = True
import numpy as np  # noqa: E402

CODE = "/pscratch/sd/j/josephrb/s5p-20260926/gen5d_fluxfix/code"
sys.path.insert(0, CODE)
import gen5d_flux_reweight as gfr  # noqa: E402
import gen5d_flux_supplement as sup  # noqa: E402

OUTDIR = sys.argv[1]
ROOT = gfr.import_root()
g5 = gfr.load_g5(gfr.DEFAULTS["gen5d_tree"])
AX, E5 = g5.AXES, g5.EDGES
shape = tuple(g5.SHAPE)
dV = g5.widths(*AX)
G = gfr.DEFAULTS["genie_dir"]
S_RES, S_DIS = 0.84 / 1.0, 1.062 / 1.032
R = {(2212, 2): 0.008 / 0.10, (2212, 3): 0.94 / 1.00, (2112, 2): 0.03 / 0.30, (2112, 3): 2.3 / 1.00}
COLS = ["cc", "Ev", "pxv", "pyv", "pzv", "El", "pxl", "pyl", "pzl", "res", "dis", "Ws", "hitnuc", "ni",
        "nipip", "nipim", "nipi0", "eav5d"]


def read(gst):
    return ROOT.RDataFrame("gst", gst).Define("eav5d", g5.EAVAIL_CPP).AsNumpy(COLS)


def in_ps(d):
    pt = np.hypot(d["pxl"], d["pyl"])
    f = g5.u3d.u2d.in_truth_phase_space
    PT, PZ = E5["pt"], E5["pz"]
    return np.fromiter((c and f(float(a), float(b), PT[0], PT[-1], PZ[0], PZ[-1])
                        for c, a, b in zip(d["cc"].astype(bool).tolist(), pt.tolist(), d["pzl"].tolist())),
                       dtype=bool, count=pt.size)


def kin(d, sel):
    Ev, pxv, pyv, pzv = (d[k][sel] for k in ("Ev", "pxv", "pyv", "pzv"))
    El, pxl, pyl, pzl = (d[k][sel] for k in ("El", "pxl", "pyl", "pzl"))
    W = np.fromiter((g5.gew.w_true((a, b, c, e), (f, g, h, i)) for a, b, c, e, f, g, h, i in
                     zip(Ev.tolist(), pxv.tolist(), pyv.tolist(), pzv.tolist(),
                         El.tolist(), pxl.tolist(), pyl.tolist(), pzl.tolist())), dtype=float, count=sel.size)
    _, q3 = g5.q3_true(Ev, pxv, pyv, pzv, El, pxl, pyl, pzl)
    return {"pt": np.hypot(pxl, pyl), "pz": pzl, "eavail": d["eav5d"][sel], "q3": q3, "W": W}


def factor(d, sel):
    res, dis = d["res"][sel].astype(bool), d["dis"][sel].astype(bool)
    f = np.ones(sel.size)
    f[res] *= S_RES
    f[dis] *= S_DIS
    nrb = dis & (d["Ws"][sel] < 1.7)
    ni, hn = d["ni"][sel], d["hitnuc"][sel]
    npi = d["nipip"][sel] + d["nipim"][sel] + d["nipi0"][sel]
    for (nuc, m), r in R.items():
        f[nrb & (hn == nuc) & (ni == m)] *= r
    diag = {"nrb_frac_events": float(nrb.mean()),
            "nrb_ni2_with_one_pion": float(((ni == 2) & (npi == 1) & nrb).sum() / max(((ni == 2) & nrb).sum(), 1)),
            "nrb_ni3_with_two_pions": float(((ni == 3) & (npi == 2) & nrb).sum() / max(((ni == 3) & nrb).sum(), 1))}
    return f, diag


def main():
    edges, phi_t, Phi_t, _, _ = sup.phi_t_arrays()
    _, meta = sup.load5(os.path.join(sup.OUT, "genie_cv_xsec5d.npz"), shape)
    full_np, fmeta = sup.load5(os.path.join(sup.OUT, "genie_cv_xsec5d_full.npz"), shape)
    A = meta["normalisation"]["sigma_CC_t_lt50_per_nucleon_cm2"]
    B = meta["normalisation"]["sum_r_normalising_population"]
    pe = fmeta["supplement"]["normalisation"]["per_event_xsec_cm2"]
    mev = sup.main_genie_events(ROOT, g5, "genie_cv", edges, phi_t, Phi_t)
    dm = read(os.path.join(G, "genie_mefhc_cv_ALL.gst.root"))
    sm = np.where(in_ps(dm))[0]
    km = kin(dm, sm)
    ds = read(sup.SUPP_FILES["genie_cv"])
    ss = np.where(in_ps(ds))[0]
    ks = kin(ds, ss)
    fm, diag_m = factor(dm, sm)
    fs, diag_s = factor(ds, ss)
    w = np.concatenate([A * mev["r_ps"] / B, np.full(ss.size, pe)])
    f = np.concatenate([fm, fs])
    cols = [np.concatenate([km[a], ks[a]]) for a in AX]
    e5 = [E5[a] for a in AX]
    x_nom = g5.hist(cols, w, e5)
    x_emu = g5.hist(cols, w * f, e5)
    rec = gfr.compare_arrays((np.asarray(x_nom) / dV).reshape(-1), full_np["xsec_flat"])
    os.makedirs(OUTDIR, exist_ok=True)
    np.savez(os.path.join(OUTDIR, "r5b_tune_emulation.npz"), nominal_cell_sigma=np.asarray(x_nom),
             emulated_cell_sigma=np.asarray(x_emu))
    info = {"schema": "inelastic-r5b/1", "aligned_main": bool(np.array_equal(km["pz"], mev["pz_ps"])),
            "reconstruction_vs_full_product": rec, "factors": {"S_RES": S_RES, "S_DIS": S_DIS,
            "R_ratio": {f"{k[0]}_m{k[1]}": v for k, v in R.items()}}, "diag_main": diag_m, "diag_supp": diag_s,
            "total_ratio_emulated_over_nominal": float(np.sum(x_emu) / np.sum(x_nom))}
    json.dump(info, open(os.path.join(OUTDIR, "r5b_tune_emulation.json"), "w"), indent=1)
    print(json.dumps(info, default=str))
    ru, rc = resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN)
    print(f"BUDGET_REMOTE_CPU_S={ru.ru_utime + ru.ru_stime + rc.ru_utime + rc.ru_stime:.3f}")


main()
