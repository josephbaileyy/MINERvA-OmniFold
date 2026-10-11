"""A1-d reduction: data/prediction contrasts for the nominal GENIE CV rebuild and the 02_11b-parameter emulation.

Usage: python3 -I reduce_a1d.py <input_dir> <emulation_npz> <out_json>
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
import reduce_r3 as R3  # noqa: E402


def main(indir, emu, out):
    dig = C.verify(indir, ["xsec_5d_MEFHC_5iter_lgbm.root", "genie_cv_xsec5d_full.npz"])
    dig[C.PS + "/inelastic-high-region-20261011/out/r5b_tune_emulation.npz"] = C.sha256(emu)
    P, _, _, E = C.load_pred(indir, "genie_cv_xsec5d_full.npz")
    D = C.load_data_production(indir) * C.volume(E)
    z = np.load(emu)
    nom, emul = z["nominal_cell_sigma"].reshape(C.SHAPE), z["emulated_cell_sigma"].reshape(C.SHAPE)
    corner, mid, overflow = C.region_masks(E)
    masks = {"C": C.broadcast_ew(corner), "M": C.broadcast_ew(mid),
             "C_no_overflow": C.broadcast_ew(corner & ~overflow), "C_overflow": C.broadcast_ew(corner & overflow)}
    for j in range(6):
        m = np.zeros((7, 6), bool)
        m[:, j] = True
        masks[f"W{j}"] = C.broadcast_ew(m)
    res = {"digests": dig, "control_nominal_vs_product_maxrel": float(np.max(np.abs(nom[P > 0] / P[P > 0] - 1))),
           "total_emulated_over_nominal": float(emul.sum() / nom.sum()),
           "R_total": {"nominal": float(D.sum() / nom.sum()), "emulated": float(D.sum() / emul.sum())}, "regions": {}}
    dn = R3.decompose(D, nom, masks)["inclusive_first"]
    de = R3.decompose(D, emul, masks)["inclusive_first"]
    for k in masks:
        res["regions"][k] = {"pred_change_emulated_over_nominal": float(emul[masks[k]].sum() / nom[masks[k]].sum()),
                             "ln_rho_nominal": dn[k]["ln_rho"], "ln_rho_emulated": de[k]["ln_rho"],
                             "steps_nominal": dn[k]["steps"], "steps_emulated": de[k]["steps"]}
    C.write_json(out, res)
    print({k: v for k, v in res.items() if k != "regions"})
    for k, r in res["regions"].items():
        print(f"{k:14s} pred x{r['pred_change_emulated_over_nominal']:.4f}  ln_rho {r['ln_rho_nominal']:+.4f} -> "
              f"{r['ln_rho_emulated']:+.4f}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
