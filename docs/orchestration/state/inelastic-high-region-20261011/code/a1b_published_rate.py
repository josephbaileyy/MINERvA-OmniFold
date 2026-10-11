"""Amendment A1-b: the published 2D (p_T, p_par) comparison as a rate check independent of the hadronic axes.

Uses the released arrays: paper_v (published data, Ruterbories et al.), tune_v1_v (the published Tune v1
prediction), ours_v (this analysis's 2D central value), with area_paper / area_ours and mask_reported.
Flat index = i_pT * 16 + i_pz (p_par varies fastest), as the area pattern shows.

Usage: python3 -I a1b_published_rate.py <input_dir> <out_json>
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402


def main(indir, out):
    dig = C.verify(indir, ["fig_arrays.npz"])
    z = np.load(os.path.join(indir, "fig_arrays.npz"), allow_pickle=False)
    m = z["mask_reported"].astype(bool)
    a = z["area_paper"]
    ao = z["area_ours"]
    pt = z["pt_edges"]
    npz = len(z["pz_edges"]) - 1
    ipt = np.arange(m.size) // npz
    paper, tune, ours = z["paper_v"] * a, z["tune_v1_v"] * a, z["ours_v"] * ao
    res = {"digests": dig, "area_check_max_rel": float(np.max(np.abs(ao[m] / a[m] - 1))),
           "total": {"paper_over_tune": paper[m].sum() / tune[m].sum(),
                     "ours_over_tune": ours[m].sum() / tune[m].sum(),
                     "ours_over_paper": ours[m].sum() / paper[m].sum()},
           "by_pt": []}
    for i in range(len(pt) - 1):
        s = m & (ipt == i)
        if not s.any():
            continue
        res["by_pt"].append({"pt_lo": pt[i], "pt_hi": pt[i + 1],
                             "paper_over_tune": paper[s].sum() / tune[s].sum(),
                             "ours_over_tune": ours[s].sum() / tune[s].sum(),
                             "rho_paper": paper[s].sum() / tune[s].sum() / (paper[m].sum() / tune[m].sum()),
                             "paper_fraction": paper[s].sum() / paper[m].sum()})
    hi = m & (pt[ipt + 1] > 0.85 + 1e-9)
    res["pt_gt_0.85"] = {"paper_over_tune": paper[hi].sum() / tune[hi].sum(),
                         "rho_paper": paper[hi].sum() / tune[hi].sum() / (paper[m].sum() / tune[m].sum()),
                         "paper_fraction": paper[hi].sum() / paper[m].sum()}
    C.write_json(out, res)
    print({k: v for k, v in res.items() if k not in ("by_pt", "digests")})
    for r in res["by_pt"]:
        print(f"pT [{r['pt_lo']:.2f},{r['pt_hi']:.2f}) paper/tune={r['paper_over_tune']:.4f} "
              f"ours/tune={r['ours_over_tune']:.4f} rho={r['rho_paper']:.4f} frac={r['paper_fraction']:.4f}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
