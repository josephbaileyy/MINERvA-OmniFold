"""R1/R2: rate, shape and coverage of the high-E_avail / high-W region (PLAN.md §5).

Usage: python3 -I reduce_r1.py <input_dir> <out_json>
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402


def rel(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    m = b != 0
    return float(np.max(np.abs(a[m] / b[m] - 1))) if m.any() else 0.0


def main(indir, out):
    names = ["xsec_5d_MEFHC_5iter_lgbm.root", "fig_arrays.npz"] + list(C.PREDICTIONS.values())
    digests = C.verify(indir, names)
    preds, var, nevt = {}, {}, {}
    for k, fn in C.PREDICTIONS.items():
        preds[k], var[k], nevt[k], E = C.load_pred(indir, fn)
    dV = C.volume(E)
    D = C.load_data_production(indir) * dV
    corner, mid, overflow = C.region_masks(E)
    fig = np.load(os.path.join(indir, "fig_arrays.npz"), allow_pickle=False)
    wA, wW = np.diff(E["eavail"]), np.diff(E["W"])
    area = wA[:, None] * wW[None, :]

    D_ew = C.ew(D)
    P_ew = {k: C.ew(v) for k, v in preds.items()}

    # ---- controls ------------------------------------------------------------------------------
    ctrl = {"data_vs_fig_hData2D_density_maxrel": rel(D_ew / area, fig["hData2D"]),
            "data_vs_fig_hData2D_integrated_maxrel": rel(D_ew, fig["hData2D"])}
    for k, fk in (("GENIE_CV", "gen_GENIE-CV"), ("GENIE_MEC", "gen_GENIE+MEC"), ("NuWro", "gen_NuWro"),
                  ("GiBUU", "gen_GiBUU"), ("TuneV1", "hGenCV2D")):
        ctrl[f"{k}_vs_fig_{fk}_density_maxrel"] = rel(P_ew[k] / area, fig[fk])
    vl156 = {"GENIE_CV": 1.142, "GENIE_MEC": 1.139, "NuWro": 1.160, "GiBUU": 1.607}
    vl157 = {"GENIE_CV": 1.110, "GENIE_MEC": 1.068, "NuWro": 1.153, "GiBUU": 1.386}
    ctrl["data_total"] = D.sum()
    ctrl["data_corner"] = D_ew[corner].sum()
    # Tune v1 descriptive-map shares (paper: 67.215%, 83.172%, 21.947%)
    diff_t = D_ew - P_ew["TuneV1"]
    pos = np.clip(diff_t, 0, None)
    hiA = (E["eavail"][:-1] >= 0.8 - 1e-9)[:, None] & np.ones((1, 6), bool)
    ctrl["tune_share_pos_diff_A_ge_0.8"] = pos[hiA].sum() / pos.sum()
    ctrl["tune_share_of_that_W_ge_1.8"] = pos[corner].sum() / pos[hiA].sum()
    ctrl["tune_share_catch_cell_max"] = pos.max() / pos.sum()
    ctrl["tune_share_catch_cell_index"] = int(np.argmax(pos))

    # ---- per-prediction rate / shape / coverage -------------------------------------------------
    S20 = C.enu_upper_bound(E) < 20.0
    S20_ew_frac_data = C.ew(D * S20)
    res = {}
    for k, P in preds.items():
        Pe = P_ew[k]
        r = {}
        r["sigma_total"] = P.sum()
        r["R_total"] = D.sum() / P.sum()
        r["R_C"] = D_ew[corner].sum() / Pe[corner].sum()
        r["R_notC"] = D_ew[~corner].sum() / Pe[~corner].sum()
        r["R_M"] = D_ew[mid].sum() / Pe[mid].sum()
        r["rho_C"] = r["R_C"] / r["R_total"]
        r["rho_M"] = r["R_M"] / r["R_total"]
        r["C_over_notC"] = r["R_C"] / r["R_notC"]
        r["f_C_pred"] = Pe[corner].sum() / P.sum()
        r["f_M_pred"] = Pe[mid].sum() / P.sum()
        r["overflow_share_of_C_pred"] = Pe[corner & overflow].sum() / Pe[corner].sum()
        r["R_C_without_overflow"] = D_ew[corner & ~overflow].sum() / Pe[corner & ~overflow].sum()
        r["R_C_overflow_only"] = D_ew[corner & overflow].sum() / Pe[corner & overflow].sum()
        # Cell-integrated differences on the 42-cell grid, raw and with the prediction normalized to data
        raw = D_ew - Pe
        shp = D_ew - Pe * (D.sum() / P.sum())
        r["diff_raw_ew"] = raw
        r["diff_shape_ew"] = shp
        r["ratio_ew"] = np.where(Pe > 0, D_ew / np.where(Pe > 0, Pe, 1), np.nan)
        r["rho_ew"] = r["ratio_ew"] / r["R_total"]
        r["diff_raw_C"] = raw[corner].sum()
        r["diff_raw_C_overflow"] = raw[corner & overflow].sum()
        r["diff_shape_C"] = shp[corner].sum()
        r["diff_shape_C_overflow"] = shp[corner & overflow].sum()
        r["diff_shape_M"] = shp[mid].sum()
        r["diff_raw_total"] = raw.sum()
        # MC statistical relative error of the corner and total (sumw2)
        r["mc_relerr_C"] = np.sqrt(C.ew(var[k])[corner].sum()) / Pe[corner].sum()
        r["mc_relerr_total"] = np.sqrt(var[k].sum()) / P.sum()
        r["n_mc_events_C"] = C.ew(nevt[k])[corner].sum()
        # Conditional shapes
        r["P_W_given_A_data"] = D_ew / D_ew.sum(axis=1, keepdims=True)
        r["P_W_given_A_pred"] = Pe / np.where(Pe.sum(axis=1, keepdims=True) > 0, Pe.sum(axis=1, keepdims=True), 1)
        r["P_A_given_W_data"] = D_ew / D_ew.sum(axis=0, keepdims=True)
        r["P_A_given_W_pred"] = Pe / np.where(Pe.sum(axis=0, keepdims=True) > 0, Pe.sum(axis=0, keepdims=True), 1)
        r["cond_ratio_W_given_A"] = r["P_W_given_A_data"] / np.where(r["P_W_given_A_pred"] > 0, r["P_W_given_A_pred"], np.nan)
        r["cond_ratio_A_given_W"] = r["P_A_given_W_data"] / np.where(r["P_A_given_W_pred"] > 0, r["P_A_given_W_pred"], np.nan)
        # Fraction with W >= 1.8 at fixed A >= 0.8 band; fraction with A >= 0.8 at fixed W >= 1.8 band
        hiW = E["W"][:-1] >= 1.8 - 1e-9
        hiAa = E["eavail"][:-1] >= 0.8 - 1e-9
        r["frac_Wge1.8_given_Age0.8"] = {"data": D_ew[hiAa][:, hiW].sum() / D_ew[hiAa].sum(),
                                         "pred": Pe[hiAa][:, hiW].sum() / Pe[hiAa].sum()}
        r["frac_Age0.8_given_Wge1.8"] = {"data": D_ew[:, hiW][hiAa].sum() / D_ew[:, hiW].sum(),
                                         "pred": Pe[:, hiW][hiAa].sum() / Pe[:, hiW].sum()}
        r["frac_Age0.8"] = {"data": D_ew[hiAa].sum() / D.sum(), "pred": Pe[hiAa].sum() / P.sum()}
        r["frac_Wge1.8"] = {"data": D_ew[:, hiW].sum() / D.sum(), "pred": Pe[:, hiW].sum() / P.sum()}
        # Support-complete domain S20
        P20 = C.ew(P * S20)
        r["S20"] = {"R_total": D[S20].sum() / P[S20].sum(),
                    "R_C": S20_ew_frac_data[corner].sum() / P20[corner].sum(),
                    "R_M": S20_ew_frac_data[mid].sum() / P20[mid].sum()}
        r["S20"]["rho_C"] = r["S20"]["R_C"] / r["S20"]["R_total"]
        r["S20"]["rho_M"] = r["S20"]["R_M"] / r["S20"]["R_total"]
        if k in vl156:
            r["control_VL156_R_C"] = {"expected": vl156[k], "got": round(r["R_C"], 3)}
            r["control_VL157_R_total"] = {"expected": vl157[k], "got": round(r["R_total"], 3)}
        res[k] = r
    s20 = {"data_fraction_total_in_S20": D[S20].sum() / D.sum(),
           "data_fraction_C_in_S20": S20_ew_frac_data[corner].sum() / D_ew[corner].sum(),
           "data_fraction_M_in_S20": S20_ew_frac_data[mid].sum() / D_ew[mid].sum(),
           "n_cells_S20": int(S20.sum()), "n_cells": int(S20.size)}
    C.write_json(out, {"schema": "inelastic-r1/1", "digests": digests, "edges": E, "controls": ctrl,
                       "S20": s20, "data_ew": D_ew, "pred_ew": P_ew, "area_ew": area,
                       "corner_mask_ew": corner, "mid_mask_ew": mid, "overflow_mask_ew": overflow,
                       "predictions": res})
    print("controls:", {k: v for k, v in ctrl.items()})
    for k, r in res.items():
        print(f"{k:10s} Rtot={r['R_total']:.4f} RC={r['R_C']:.4f} rhoC={r['rho_C']:.4f} RM={r['R_M']:.4f} "
              f"rhoM={r['rho_M']:.4f} C/notC={r['C_over_notC']:.4f} fC={r['f_C_pred']:.4f} "
              f"S20 rhoC={r['S20']['rho_C']:.4f} S20 RC={r['S20']['R_C']:.4f} mcC={r['mc_relerr_C']:.4f}")
    print("S20:", s20)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
