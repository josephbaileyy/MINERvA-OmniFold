"""X report (read-only diagnostic, the director's approval of 2026-11-02; outside the bound steps, changes no reading):
why K2 failed for the statistical block. From $R/deploy-a2 at M''' (b2e2d232), its own functions imported, inputs read
through Inputs (O_NOATIME, pin-checked) and the paired replicas through committed_sha, as k_compute reads them.
Prints dimensionless magnitudes only (eigenvalue ratios, correlations, sigma ratios); no covariance value."""
import json, sys
from pathlib import Path
R = Path("/pscratch/sd/j/josephrb/gencmp-x-20261102")
sys.path.insert(0, str(R / "deploy-a2/nd-unfolding"))
import numpy as np, fd_xcov as X, fd_xcov_steps as XS
gc, sa = XS.gc, XS.sa
inp = X.Inputs()
defn = json.loads(XS.DEFINITION.read_text())
U = gc.cell_matrix()
qz, pl, s5 = inp.npz(XS.Q_R), inp.npz(XS.CPL_R), inp.npz(XS.S5_R)
cells2d, area = np.asarray(pl["cells"], int), np.asarray(qz["area"], float)
_, (e_pt, e_pz) = gc.root_hist(inp.bytes(XS.RE2 / "partb/out/ER/xsec.root"), "hXSec2D")
A, B = X.quadrant_vectors(defn, cells2d, area, np.asarray(e_pt, float), np.asarray(e_pz, float))
s1 = inp.npz(XS.S1_NPZ)
S16, S2 = A @ np.asarray(s1["C_stat"], float) @ A.T, B @ np.asarray(s5["stat"], float) @ B.T
sig16, sig2 = np.sqrt(np.diag(S16)), np.sqrt(np.diag(S2))
prods = {}
for p in sorted((R / "boot" / "xcov").glob("lane_*.json")):
    prods.update(json.loads(p.read_text())["products"])
want = [f"xcov_b{b}_j{100 + b}.npz" for b in X.STAT_REPLICAS]
for n in want:
    XS.committed_sha(R / "boot" / "xcov" / n, prods[n], "paired replica")
S16r = np.array([A @ (U @ sa.xs(R / "boot" / "xcov" / n)) for n in want])
S2r = np.array([B @ XS.hist2d_cells(inp.bytes(XS.RE2 / f"partb/out/S1_{b:03d}/xsec.root"), cells2d)
                for b in X.STAT_REPLICAS])
st = X.stat_cross(S16r, S2r, sig16, sig2)
kj = json.loads((R / "k" / "k.json").read_text())
Rk = np.asarray(kj["stat"]["R"], float)
corr = lambda M: M / np.sqrt(np.outer(np.diag(M), np.diag(M)))  # noqa: E731
J = np.block([[S16, st["K"]], [st["K"].T, S2]])
lam = np.linalg.eigvalsh((J + J.T) / 2)
C16, C2 = corr(S16), corr(S2)
iw = lambda M: np.linalg.inv(np.linalg.cholesky(M))  # noqa: E731
L16, L2 = iw(C16), iw(C2)
tstar = 1.0 / np.linalg.svd(L16 @ st["R"] @ L2.T, compute_uv=False).max()   # [[C16, tR], [tR^T, C2]] PSD iff t <= t*
Zr = np.corrcoef(np.hstack([S16r, S2r]), rowvar=False)
Jn = np.block([[C16, st["R"]], [st["R"].T, C2]])
w, v = np.linalg.eigh(Jn)
off = ~np.eye(X.N_Q, dtype=bool)
out = {
    "control_R_equals_k_json_R": bool(np.array_equal(st["R"], Rk)),
    "control_joint_psd_false_as_K_found": not X.joint_psd(S16, S2, st["K"]),
    "joint_lambda_min_over_max": float(lam.min() / lam.max()), "PD_REL_tolerance": X.PD_REL,
    "joint_correlation_form_lambda_min": float(w.min()),
    "joint_correlation_form_min_eigvec_weight_16_vs_2d": [float((v[:4, 0] ** 2).sum()), float((v[4:, 0] ** 2).sum())],
    "rho_hat_diag": {q: float(st["R"][i, i]) for i, q in enumerate(X.QNAMES)},
    "rho_max_for_each_2x2_psd_given_stated_sigma": 1.0,
    "rho_hat_offdiag_max_abs": float(np.abs(st["R"][off]).max()),
    "t_star_largest_scale_on_cross_block_keeping_joint_psd": float(tstar),
    "own_stat_corr_lambda_min": {"16": float(np.linalg.eigvalsh(C16).min()), "2D": float(np.linalg.eigvalsh(C2).min())},
    "stated_vs_replica_within_side": {
        "16": {"max_abs_offdiag_corr_diff": float(np.abs((corr(S16) - Zr[:4, :4])[off]).max()),
               "replica_sigma_over_stated": (S16r.std(axis=0, ddof=1) / sig16).tolist()},
        "2D": {"max_abs_offdiag_corr_diff": float(np.abs((corr(S2) - Zr[4:, 4:])[off]).max()),
               "replica_sigma_over_stated": (S2r.std(axis=0, ddof=1) / sig2).tolist()}},
    "replica_sample_joint_correlation_lambda_min": float(np.linalg.eigvalsh(Zr).min()),
    "n_replicas": len(want), "atime_deviations": inp.atime_deviations()}
print(json.dumps(out, indent=1))
