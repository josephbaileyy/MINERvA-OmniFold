#!/usr/bin/env python3
"""MP3-C option (b): the POST-HOC DESCRIPTIVE bias check declared in DECLARATION-b.json (its sha256 is checked
against --declaration-sha256 before anything is computed). B3 stays FAILED whatever this finds.

Computes the declared linear within-point keep-probability correction s_e on the H events, the H product under the
frozen weight w r and under w r s (mp3c_build.build), and Delta_c = (1/13) U (x_H,alt - x_H,frozen) over GiBUU's 72
domain cells in units of sigma_c (readings a/b/c as MP3-B). PASS iff max |Delta/sigma(a)| <= 0.1. On PASS it also
writes the two fine products (frozen r: the primary; alternative: beside it) in the keys mp3c_eval.py reads, with
the C12 part rebuilt (as B2) for the eval's control.
Usage (root_6_28): python3 mp3c_bcheck.py --declaration D --declaration-sha256 H --h-glob G --inputs IN --out OUT
Exit 0 PASS (products written); 7 FAIL (effect size only); 2 a control failed.
"""
import argparse
import glob
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np  # noqa: E402

import mp3c_build as b  # noqa: E402
import s5p_joint as sj  # noqa: E402

KEY = "GiBUU_2019"
N_SUB = 5


def slopes(enu_every, g_edges, fcut):
    Et = enu_every[np.isfinite(enu_every)]
    out = {}
    xj = (np.arange(N_SUB) + 0.5) / N_SUB
    A = np.vstack([np.ones(N_SUB), xj - 0.5]).T
    for k in np.where((g_edges[:-1] >= 1.5 - 1e-9) & (fcut > 0))[0]:
        a0, w = g_edges[k], g_edges[k + 1] - g_edges[k]
        x = (Et[(Et >= a0) & (Et < a0 + w)] - a0) / w
        n = np.histogram(x, N_SUB, (0.0, 1.0))[0].astype(float)
        (alpha, beta), *_ = np.linalg.lstsq(A, n, rcond=None)
        bk = beta / alpha
        ck = x.size / np.sum(1.0 / (1.0 + bk * (x - 0.5)))
        out[int(k)] = {"E_lo": float(a0), "width": float(w), "N": int(x.size), "b": float(bk), "c": float(ck),
                       "sub_counts": n.astype(int).tolist()}
    return out


def s_weight(enu, g_edges, fit):
    s = np.ones(enu.size)
    k = np.searchsorted(g_edges, enu, side="right") - 1
    for kk, f in fit.items():
        m = k == kk
        x = (enu[m] - f["E_lo"]) / f["width"]
        s[m] = f["c"] / (1.0 + f["b"] * (x - 0.5))
    return s


def main():
    ap = argparse.ArgumentParser()
    for k in ("declaration", "declaration-sha256", "h-glob", "inputs", "out"):
        ap.add_argument(f"--{k}", required=True)
    ap.add_argument("--nproc", type=int, default=96)
    a = ap.parse_args()
    if b.sha256(a.declaration) != a.declaration_sha256:
        raise SystemExit("STOP: DECLARATION-b.json differs from the declared sha256")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=False)
    b.gfr.import_root()
    g5 = b.gfr.load_g5(b.gfr.DEFAULTS["gen5d_tree"])
    b.G5 = g5
    inp = Path(a.inputs)
    res = {"schema": "mp3c-bcheck/1", "label": "POST-HOC DESCRIPTIVE; B3 stays FAILED",
           "declaration": {"path": a.declaration, "sha256": a.declaration_sha256}, "argv": sys.argv}
    files = sorted(glob.glob(a.h_glob))
    ah, Mh, nev, enu_every, al = b.events(files, a.nproc)
    ptz, _, _ = b.gfr.load_phi_t(b.sup.OUT)
    g_edges, fcut, phi_g, cut, step = b.gibuu_density(b.gfr.DEFAULTS["gibuu_jobcard"])
    r, zero = b.weights(ah, g_edges, phi_g, ptz["edges"], ptz["phi_t_density"], float(ptz["Phi_t"]))
    fit = slopes(enu_every, g_edges, fcut)
    s = s_weight(ah["enu"], g_edges, fit)
    xf, vf, nf = b.build(g5, ah, Mh, r)
    xa, va, _ = b.build(g5, ah, Mh, r * s)
    design = json.loads((inp / "design.json").read_text())
    sj.check_v(design, f"{b.gfr.S5P}/stage3/V/V-s3v.npz")
    V = np.asarray(np.load(f"{b.gfr.S5P}/stage3/V/V-s3v.npz", allow_pickle=False)["V"], float)
    supported = json.loads((inp / "s5c_contract.json").read_text())["measurement"]["partition_J"]["supported_cells"]
    U, names, pz_index = sj.j_matrix({}, supported)
    dom = pz_index <= 1
    spec = design["nulls"][KEY]
    mu_C, var_C = sj.prediction(spec["prediction"], U)
    model = sj.Model(design, U)
    cal = sj.product_files(spec["calibration_glob"])
    if len(cal) != sj.calibration_count(spec):
        raise SystemExit("calibration count mismatch")
    F, seeds = sj.ensemble(model, cal)
    sd_a = F.std(0, ddof=1)
    W = V + np.diag(var_C)
    sd_b = np.sqrt(np.diag(W))
    eps = np.array([np.random.default_rng([int(spec["surrogate_seed0"]), int(q), 0x4A02]).normal(size=mu_C.size)
                    for q in seeds]) * np.sqrt(var_C)
    sd_c = (F - (mu_C + eps)).std(0, ddof=1)
    h_f, h_a = b.F_H * (U @ xf), b.F_H * (U @ xa)
    delta = h_a - h_f
    mu_CH = b.F_C * mu_C + h_f
    z = {"a_sd_null_result": delta / sd_a, "b_sqrt_diag_W": delta / sd_b, "c_sd_null_residual": delta / sd_c}
    q = lambda v: {"min": float(v[dom].min()), "median": float(np.median(v[dom])), "max": float(v[dom].max()),  # noqa: E731
                   "max_abs": float(np.abs(v[dom]).max())}
    Wd = W[np.ix_(dom, dom)]
    worst = int(np.where(dom)[0][np.argmax(np.abs(z["a_sd_null_result"][dom]))])
    passed = bool(np.abs(z["a_sd_null_result"][dom]).max() <= 0.1)
    res.update({
        "n_H_files": len(files), "M_H": Mh, "alignment": al, "zero_flux_event": zero,
        "fit_per_point": fit, "slope_b": {"min": min(f["b"] for f in fit.values()), "max": max(f["b"] for f in fit.values())},
        "s_in_grid_quantiles_1_50_99": np.percentile(s, [1, 50, 99]).tolist(),
        "n_cells": int(dom.sum()), "delta_over_sigma": {k: q(v) for k, v in z.items()},
        "worst_cell": names[worst], "worst_delta_over_sigma_a": float(z["a_sd_null_result"][worst]),
        "delta_rel_H_contribution": q(np.where(h_f != 0, delta / h_f, 0.0)),
        "delta_rel_mu_CH": q(delta / mu_CH),
        "integrated_H_in_domain_alt_over_frozen": float(h_a[dom].sum() / h_f[dom].sum()),
        "DeltaT_Winv_Delta_frozen_W": float(delta[dom] @ np.linalg.solve(Wd, delta[dom])),
        "acceptance": "max |Delta_c / sigma_c(a)| <= 0.1 over the 72 domain cells",
        "VERDICT": "PASS" if passed else "FAIL",
        "cells": {"names": names, "in_domain": dom.tolist(), "delta": delta.tolist(),
                  **{f"z_{k}": v.tolist() for k, v in z.items()}}})
    print("BCHECK", json.dumps({k: res[k] for k in ("slope_b", "delta_over_sigma", "worst_cell", "worst_delta_over_sigma_a",
                                                    "delta_rel_mu_CH", "DeltaT_Winv_Delta_frozen_W", "VERDICT")}), flush=True)
    if not passed:
        (out / "mp3c_bcheck.json").write_text(json.dumps(res, indent=1) + "\n")
        return 7
    # PASS: the two fine products, C12 part rebuilt as B2 for the eval control
    c12 = sorted(glob.glob(b.C12_GLOB))
    ac, Mc, _, _, alc = b.events(c12, a.nproc)
    rc, _ = b.weights(ac, g_edges, phi_g, ptz["edges"], ptz["phi_t_density"], float(ptz["Phi_t"]))
    xc, vc, _ = b.build(g5, ac, Mc, rc)
    fz = np.load(b.FROZEN, allow_pickle=True)
    ctrl = {"C12_rebuild_bitwise_xsec": bool(np.array_equal(xc, fz["xsec_flat"])),
            "C12_rebuild_bitwise_sumw2": bool(np.array_equal(vc, fz["sumw2_flat"])), "alignment_C12": alc}
    res["controls"] = ctrl
    if not all(ctrl.values()):
        (out / "mp3c_bcheck.json").write_text(json.dumps(res, indent=1) + "\n")
        return 2
    for tag, xh, vh in (("frozen", xf, vf), ("alt", xa, va)):
        np.savez_compressed(out / f"mp3c_fine_gibuu_{tag}.npz", xsec_C12_frozen=np.asarray(fz["xsec_flat"]),
                            sumw2_C12_frozen=np.asarray(fz["sumw2_flat"]), nevt_C12_frozen=np.asarray(fz["nevt_flat"]),
                            xsec_C12_rebuilt=xc, sumw2_C12_rebuilt=vc, xsec_H=xh, sumw2_H=vh, nevt_H=nf,
                            xsec_CH=b.F_C * np.asarray(fz["xsec_flat"]) + b.F_H * xh,
                            sumw2_CH=b.F_C ** 2 * np.asarray(fz["sumw2_flat"]) + b.F_H ** 2 * vh,
                            nevt_CH=np.asarray(fz["nevt_flat"]) + nf)
    (out / "mp3c_bcheck.json").write_text(json.dumps(res, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
