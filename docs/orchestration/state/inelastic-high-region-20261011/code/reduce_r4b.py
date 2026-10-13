"""R4 (recorded part) and the per-bin profile of amendment 1 (PLAN.md §8).

1. Recorded estimator and background biases, read from committed receipts and aggregated to regions C and M
   with the production data's cell-integrated weights (means are linear, so the aggregate of mean relative
   biases is the data-weighted average):
     s5n Stage-1 C4 (E_avail-shape departure, F2 estimator): regularization residual per EW cell;
     s5n Stage-1 C5 (q3 departure, total (E_avail,W) unchanged): induced (E_avail,W) movement;
     s5n Stage-1 C3 (nominal truth, negweight-refined background): residual nominal bias;
     s5c D1 split_production (purity background, production estimator, nominal truth).
2. Per-W-bin and per-E_avail-bin profile of the R3 decomposition (descriptive presentation of the frozen
   quantities; not an input to the decision rule).

Usage: python3 -I reduce_r4b.py <input_dir> <repo_state_dir> <out_json>
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
import reduce_r3 as R3  # noqa: E402


def ew_index(name):
    return int(name[2:]) if name.startswith("EW") and name[2:].isdigit() else None


def aggregate(names, rel, w_ew, mask_ew):
    v = np.full(42, np.nan)
    for n, x in zip(names, rel):
        i = ew_index(n)
        if i is not None:
            v[i] = x
    v = v.reshape(7, 6)
    m = mask_ew & np.isfinite(v)
    return {"weighted_mean_rel": float((v[m] * w_ew[m]).sum() / w_ew[m].sum()),
            "max_abs_rel_cell": float(np.nanmax(np.abs(np.where(mask_ew, v, np.nan)))),
            "per_cell_rel": np.where(mask_ew, v, np.nan)}


def main(indir, statedir, out):
    names = ["xsec_5d_MEFHC_5iter_lgbm.root"] + list(C.PREDICTIONS.values())
    rnames = ["w2b/w2b_rrzero_b-_j-.npz", "w2b/w2b_rr0_b-_j-.npz", "w2b/w2b_rr1_b-_j-.npz"]
    digests = C.verify(indir, names + rnames)
    preds = {}
    for k, fn in C.PREDICTIONS.items():
        preds[k], _, _, E = C.load_pred(indir, fn)
    dV = C.volume(E)
    D = C.load_data_production(indir) * dV
    corner, mid, overflow = C.region_masks(E)
    w_ew = C.ew(D)

    recs = {}
    s5n = json.load(open(os.path.join(statedir, "s5n/stage1/dev_receipt.json")))
    fn = s5n["functional_names"]
    for key, label in (("C3_nominal", "s5n_C3_nominal_background_residual"),
                       ("C4_eavail_shape", "s5n_C4_eavail_shape_regularization_residual"),
                       ("C5_q3_given_eavail_w", "s5n_C5_q3_departure_induced_movement")):
        rel = s5n["grid"][key]["per_functional"]["mean_rel"]
        recs[label] = {"C": aggregate(fn, rel, w_ew, corner), "M": aggregate(fn, rel, w_ew, mid),
                       "C_no_overflow": aggregate(fn, rel, w_ew, corner & ~overflow),
                       "C_overflow": aggregate(fn, rel, w_ew, corner & overflow)}
    d1 = json.load(open(os.path.join(statedir, "s5c/d1/d1_summary.json")))
    rel = d1["groups"]["split_production"]["mean_rel"]
    recs["s5c_D1_purity_background_production"] = {
        "C": aggregate(d1["functional_names"], rel, w_ew, corner), "M": aggregate(d1["functional_names"], rel, w_ew, mid),
        "C_no_overflow": aggregate(d1["functional_names"], rel, w_ew, corner & ~overflow),
        "C_overflow": aggregate(d1["functional_names"], rel, w_ew, corner & overflow)}
    recs["units_note"] = "mean_rel as stored in each receipt (fractional unless the receipt says percent)"
    recs["receipt_unit_probe"] = {"s5c_EW41": rel[d1["functional_names"].index("EW41")],
                                  "s5n_C4_EW29": s5n["grid"]["C4_eavail_shape"]["per_functional"]["mean_rel"][fn.index("EW29")]}

    # Profiles: each W bin (all E_avail) and each E_avail bin within W >= 1.8
    R = {n: C.load_R(indir, n, dV)[0] for n in rnames}
    prof = {}
    for k, P in preds.items():
        rows = {}
        masks = {}
        for j in range(6):
            m = np.zeros((7, 6), bool)
            m[:, j] = True
            masks[f"W{j}"] = C.broadcast_ew(m)
        for i in range(7):
            m = np.zeros((7, 6), bool)
            m[i, 3:] = True
            masks[f"A{i}_Wge1.8"] = C.broadcast_ew(m)
        nom = R3.decompose(D, P, masks)["inclusive_first"]
        z = R3.decompose(R[rnames[0]], P, masks)["inclusive_first"]
        lo = R3.decompose(R[rnames[1]], P, masks)["inclusive_first"]
        hi = R3.decompose(R[rnames[2]], P, masks)["inclusive_first"]
        for name in masks:
            if nom[name] is None:
                continue
            rows[name] = {"ln_rho": nom[name]["ln_rho"], "steps": nom[name]["steps"],
                          "recoil_minus4_shift_ln_rho": lo[name]["ln_rho"] - z[name]["ln_rho"],
                          "recoil_plus4_shift_ln_rho": hi[name]["ln_rho"] - z[name]["ln_rho"],
                          "data_fraction": float(D[masks[name]].sum() / D.sum())}
        prof[k] = rows
    C.write_json(out, {"schema": "inelastic-r4b/1", "digests": digests, "recorded_biases": recs, "profiles": prof})
    for lab, v in recs.items():
        if isinstance(v, dict) and "C" in v:
            print(f"{lab:48s} C {v['C']['weighted_mean_rel']:+.4f} (max {v['C']['max_abs_rel_cell']:.3f})  "
                  f"M {v['M']['weighted_mean_rel']:+.4f}  C_noovf {v['C_no_overflow']['weighted_mean_rel']:+.4f}  "
                  f"C_ovf {v['C_overflow']['weighted_mean_rel']:+.4f}")
    print("unit probe", recs["receipt_unit_probe"])
    for k in ("TuneV1", "GENIE_CV", "NuWro"):
        print(k)
        for name, r in prof[k].items():
            s = r["steps"]
            print(f"  {name:10s} f={r['data_fraction']:.3f} ln_rho={r['ln_rho']:+.4f} mu={s['muon_shape']:+.4f} "
                  f"t|mu={s['transfer_given_muon']:+.4f} A|t={s['partition_given_transfer']:+.4f} "
                  f"resp(-4,+4)=({r['recoil_minus4_shift_ln_rho']:+.4f},{r['recoil_plus4_shift_ln_rho']:+.4f})")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
