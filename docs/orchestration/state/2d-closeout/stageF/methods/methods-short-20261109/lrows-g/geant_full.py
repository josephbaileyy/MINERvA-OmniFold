"""D2 (DECISION-20261112-joseph-consult-d1-d7.md item 2): the GEANT_Neutron + GEANT_Proton effect with FULL
covariance matrices, not per-cell diagonal shares. Read-only, committed files only. Run from the repository root:
python3 -I <this file>.

G is the two bands' full 16 x 16 block on R00-R15, off-diagonals included: each band's s1_assemble.mat_cov over its
two committed S1 universe unfolds through the float64 U of the committed H2 definition, as G2 (geant_share.py) built
it. Control: the four detector bands rebuilt this way reproduce S1's committed detector relative sigma.

For a covariance M, the largest share of M's variance that G carries along ANY direction a is
mu_max = max_a (a^T G a) / (a^T M a), the largest generalized eigenvalue of (G, M). It bounds every linear
combination, including M's smallest-eigenvalue directions, and it bounds every chi2 change from dropping G:
chi2(M - G) / chi2(M) lies in [1, 1 / (1 - mu_max)] for every bias vector. The readout also gives, for each of M's
eigenmodes v_k (variance lambda_k), the share v_k^T G v_k / lambda_k, smallest lambda first.

The matrices M, each fractional (divided by f f^T):
- C_total = C_e + C_model_abs at the data, the form LL5D grades against (C_T = C_e(T) + C_model_abs(T),
  LL5D-DECLARATION.md:306), here with S1's blocks at the data rather than LL5D's blocks rebuilt at G18 and AR23;
- the reported covariance C_total + C_resp + C_PL5D (fd_data_product_cpl.json);
- F0b's twelve graded truths' grade matrices C^(T) + C_x + N_T, with N_T diagonal (only its diagonal is committed;
  geant_share.py reproduces the committed chi2 to 0.76 % this way), and the full-matrix chi2 change per truth."""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, "nd-unfolding")
import s1_assemble as sa  # noqa: E402

FD = Path("docs/orchestration/state/measurement-paper/5d-community-20261024")
S1D = FD / "s1/readout/s1_assembly"
FILES = {"s1_json": FD / "s1/readout/s1_assembly.json", "dp_cpl": FD / "fd/with-cpl/data-product/fd_data_product_cpl.json",
         "cmodel": Path("nd-unfolding/pv-ladder/readouts/cmodel_5d.json"),
         "f0b": FD / "fd/with-cpl/readout/fd_f0b_readout.json",
         "definition": Path("nd-unfolding/pv-ladder/readouts/h2_definition.json")}
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()  # noqa: E731


def gen_eig(G, M):
    """Generalized eigenvalues and M-normalized directions of (G, M), largest first."""
    L = np.linalg.cholesky(M)
    Li = np.linalg.inv(L)
    w, V = np.linalg.eigh(Li @ G @ Li.T)
    order = np.argsort(w)[::-1]
    return w[order], (Li.T @ V)[:, order]


def mode_shares(G, M):
    lam, V = np.linalg.eigh(M)
    return [{"k": int(k), "lambda": float(lam[k]), "share": float(V[:, k] @ G @ V[:, k] / lam[k])} for k in range(len(lam))]


def summarize(G, M, cells):
    mu, A = gen_eig(G, M)
    a = A[:, 0] / np.max(np.abs(A[:, 0]))
    ms = mode_shares(G, M)
    return {"mu_max": float(mu[0]), "mu_top3": [float(x) for x in mu[:3]],
            "chi2_ratio_bound": float(1 / (1 - mu[0])),
            "mu_max_direction_cells": {cells[i]: round(float(a[i]), 4) for i in np.argsort(-np.abs(a))[:5]},
            "eigenmode_shares_smallest_first": ms,
            "max_eigenmode_share": max(m["share"] for m in ms),
            "smallest4_eigenmode_shares": [m["share"] for m in ms[:4]]}


def main():
    U = sa.functional_matrix(sa.fine_map(FILES["definition"]))
    blk, usha = {}, {}
    for b in ("GEANT_Neutron", "GEANT_Pion", "GEANT_Proton", "MinosEfficiency"):
        ps = [S1D / f"S1_{b}_{i}.npz" for i in (0, 1)]
        usha.update({str(p): sha(p) for p in ps})
        blk[b] = sa.mat_cov(np.array([U @ sa.xs(p) for p in ps]))
    dp = json.loads(FILES["dp_cpl"].read_text())
    Mx = {k: np.array(v) for k, v in dp["matrices"].items()}
    f = np.array(dp["f"]); ff = np.outer(f, f)
    s1j = json.loads(FILES["s1_json"].read_text())
    c = float(np.max(np.abs(np.sqrt(np.diag(sum(blk.values()))) / f / np.array(s1j["relative_sigma"]["detector"]) - 1)))
    assert c < 1e-10, c
    cells = s1j["cells"]
    G = (blk["GEANT_Neutron"] + blk["GEANT_Proton"]) / ff
    offdiag_share = float(np.sum(np.abs(G - np.diag(np.diag(G)))) / np.sum(np.abs(G)))
    out = {"schema": "lrows-d2-geant-full/1", "cells": cells,
           "controls": {"detector_relative_sigma_max_rel_diff": c},
           "G_offdiagonal_abs_share": offdiag_share,
           "matrices": {}}
    out["matrices"]["C_total (C_e + C_model_abs, at the data)"] = summarize(G, (Mx["C_e"] + Mx["C_model_abs"]) / ff, cells)
    out["matrices"]["reported (C_total + C_resp + C_PL5D)"] = summarize(G, Mx["C_total_plus_C_resp_plus_C_PL5D"] / ff, cells)
    cm = json.loads(FILES["cmodel"].read_text())
    Sk = dict(zip(cm["vertices"], np.array(cm["S"])))
    Cx = (Mx["C_resp"] + Mx["C_PL5D"]) / ff
    truths = []
    for t in json.loads(FILES["f0b"].read_text())["truths"]:
        if not t["graded"]:
            continue
        b = np.array(t["bias"])
        M = Mx["C_e"] / ff + sum(np.outer(s, s) for k, s in Sk.items() if k != t["own_vertex"]) + Cx \
            + np.diag(np.array(t["noise_sigma"]) ** 2)
        c2, c2g = float(b @ np.linalg.solve(M, b)), float(b @ np.linalg.solve(M - G, b))
        s = summarize(G, M, cells)
        assert c2 <= c2g <= c2 * s["chi2_ratio_bound"] * (1 + 1e-9) + 1e-12
        truths.append({"truth": t["name"], "chi2": c2, "chi2_without": c2g, "delta_chi2": c2g - c2,
                       "delta_rel": (c2g - c2) / c2, "mu_max": s["mu_max"], "chi2_ratio_bound": s["chi2_ratio_bound"],
                       "max_eigenmode_share": s["max_eigenmode_share"], "smallest4_eigenmode_shares": s["smallest4_eigenmode_shares"]})
    out["f0b_graded_truths"] = truths
    out["scope"] = {"covered": "S1's GEANT blocks at the data, against C_total (LL5D's matrix form), the reported covariance, "
                              "and F0b's 12 grade matrices (N_T diagonal), on R00-R15",
                    "not_covered": "LL5D's own C_T at G18 and AR23, whose GEANT blocks are rebuilt from 8 detector-universe "
                                   "unfolds per truth (LL5D-DECLARATION.md:291-296) and exist only once LL5D runs"}
    out["inputs_sha256"] = {**{k: sha(p) for k, p in FILES.items()}, **usha}
    Path(__file__).with_name("geant_full.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"control {c:.1e}; G off-diagonal |.| share {offdiag_share:.3f}")
    for k, v in out["matrices"].items():
        print(f"{k}: mu_max {v['mu_max']:.3e} (chi2 ratio <= {v['chi2_ratio_bound']:.5f}); max eigenmode share "
              f"{v['max_eigenmode_share']:.3e}; smallest-4 modes {[f'{x:.2e}' for x in v['smallest4_eigenmode_shares']]}; "
              f"direction {v['mu_max_direction_cells']}")
    for t in truths:
        print(f"  {t['truth']:14s} chi2 {t['chi2']:8.3f} -> {t['chi2_without']:8.3f} ({100 * t['delta_rel']:+.2f} %); "
              f"mu_max {t['mu_max']:.3e}, bound {100 * (t['chi2_ratio_bound'] - 1):.2f} %")


if __name__ == "__main__":
    main()
