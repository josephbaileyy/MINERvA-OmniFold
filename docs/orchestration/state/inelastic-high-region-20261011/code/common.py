"""Shared loaders and projections for the inelastic high-region study (PLAN.md §3–§4).

All arrays are cell-integrated cross sections on the committed 5D grid, shape (14, 16, 7, 7, 6) with axes
(p_T, p_par, E_avail, q3, W), in cm^2/nucleon. Inputs are read from a directory given on the command line and
are checked against the digests frozen in PLAN.md before use.
"""
import hashlib
import json
import os

import numpy as np

SHAPE = (14, 16, 7, 7, 6)
AX_PT, AX_PZ, AX_A, AX_Q3, AX_W = range(5)
M_N = 0.939565
M_MU = 0.1056584

DIGESTS = {
    "xsec_5d_MEFHC_5iter_lgbm.root": "630306e20e4e175bde8b459174842a58e4f4b5a694b8a5018e730a952820aec8",
    "mnvtune_v1_xsec5d.npz": "bf7bd27873427d4b1ff9864403b895529931f113440acec3daa28479f958466c",
    "genie_cv_xsec5d_full.npz": "cfa42210dfe9cadc8e9460333316a639bd719c9ae52ab1144be900372a9adcc2",
    "genie_mec_xsec5d_full.npz": "c179855df6e42a5b8bab1f839aae675c53a5150f132649c855356ad75f26790f",
    "nuwro_cv_xsec5d_full.npz": "475a2871304db23efedbd5ab42a32d91c7f1d295b6dd0c907c46aa6d81c48070",
    "gibuu_cv_xsec5d_fluxfix.npz": "48917692ee1295902db3bec34d6c80e368f020ae7924dabbda7e996c461cca18",
    "fig_arrays.npz": "72394a2b4eff9f14b01903ff97525bcb690c2adee58ccaf573a8d95139b415b8",
    # W2B manifests (publication/w2/w2b-results/*/manifest.json)
    "w2b/w2b_rrzero_b-_j-.npz": "ec5dc97d8554f008902a17428724e8482544d6e6de7db5ae1155d96d51dc4c4e",
    "w2b/w2b_rr0_b-_j-.npz": "df11bfd8e879a051d3d0bf2aa5fc4e0131efa9065bcbd89d29a859ddb9f8639b",
    "w2b/w2b_rr1_b-_j-.npz": "36313201ecffa85183fa83d642c9b0b71dc67f9ed1743dba7184eb22c41356a8",
    # frozen estimator-R data central (W2B report section 4: fb5cc679...)
    "s5pdata/data_b-_j-.npz": "fb5cc6798b97b5902ad8f0fecbc49990271f7772f98d3063c1dc8596340e680c",
    # numerical jitters: no external reference digest; pinned as recorded on first read, 2026-10-11
    "s5pdata/data_b-_j1.npz": "1167923a18a60f5f42332b7c1d0a0778c32af24bed73054bb97e330da5b2399c",
    "s5pdata/data_b-_j2.npz": "015093815820df594a81e7775817f2dbc999f645b555d5601d5b899038e5a0dc",
    "s5pdata/data_b-_j3.npz": "d77f58eeffd0a5c4bffbe02a0c21d27dd3a784bf3d471ca15e73fa2a222a64b1",
}
PREDICTIONS = {
    "TuneV1": "mnvtune_v1_xsec5d.npz",
    "GENIE_CV": "genie_cv_xsec5d_full.npz",
    "GENIE_MEC": "genie_mec_xsec5d_full.npz",
    "NuWro": "nuwro_cv_xsec5d_full.npz",
    "GiBUU": "gibuu_cv_xsec5d_fluxfix.npz",
}
EXTERNAL_COMPLETE = ("GENIE_CV", "GENIE_MEC", "NuWro")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


PS = "/pscratch/sd/j/josephrb"
CANONICAL = {
    "xsec_5d_MEFHC_5iter_lgbm.root": f"{PS}/MINERvA-OmniFold/nd-unfolding/products/5d/xsec_5d_MEFHC_5iter_lgbm.root",
    "mnvtune_v1_xsec5d.npz": f"{PS}/s5p-20260926/gen5d/mnvtune_v1_xsec5d.npz",
    "genie_cv_xsec5d_full.npz": f"{PS}/s5p-20260926/gen5d_fluxfix/genie_cv_xsec5d_full.npz",
    "genie_mec_xsec5d_full.npz": f"{PS}/s5p-20260926/gen5d_fluxfix/genie_mec_xsec5d_full.npz",
    "nuwro_cv_xsec5d_full.npz": f"{PS}/s5p-20260926/gen5d_fluxfix/nuwro_cv_xsec5d_full.npz",
    "gibuu_cv_xsec5d_fluxfix.npz": f"{PS}/s5p-20260926/gen5d_fluxfix/gibuu_cv_xsec5d_fluxfix.npz",
    "fig_arrays.npz": f"{PS}/pub-release-20261006/figs/fig_arrays.npz",
    "w2b/w2b_rrzero_b-_j-.npz": f"{PS}/w2-recoil-20261006/w2b/unf/w2b_rrzero_b-_j-.npz",
    "w2b/w2b_rr0_b-_j-.npz": f"{PS}/w2-recoil-20261006/w2b/unf/w2b_rr0_b-_j-.npz",
    "w2b/w2b_rr1_b-_j-.npz": f"{PS}/w2-recoil-20261006/w2b/unf/w2b_rr1_b-_j-.npz",
    "s5pdata/data_b-_j-.npz": f"{PS}/s5p-20260926/runs/s2/num/data/data_b-_j-.npz",
    "s5pdata/data_b-_j1.npz": f"{PS}/s5p-20260926/runs/s2/num/data/data_b-_j1.npz",
    "s5pdata/data_b-_j2.npz": f"{PS}/s5p-20260926/runs/s2/num/data/data_b-_j2.npz",
    "s5pdata/data_b-_j3.npz": f"{PS}/s5p-20260926/runs/s2/num/data/data_b-_j3.npz",
}


def verify(indir, names):
    """Return {canonical source path: sha256} for local copies; raise if a frozen digest does not match."""
    out = {}
    for n in names:
        d = sha256(os.path.join(indir, n))
        want = DIGESTS.get(n)
        if want is not None and d != want:
            raise SystemExit(f"DIGEST MISMATCH {n}: {d} != {want}")
        out[CANONICAL[n]] = d
    return out


def edges_from(z):
    return {k: np.asarray(z["edges_" + k], float) for k in ("pt", "pz", "eavail", "q3", "W")}


def volume(E):
    w = [np.diff(E[k]) for k in ("pt", "pz", "eavail", "q3", "W")]
    return np.einsum("a,b,c,d,e->abcde", *w)


def load_pred(indir, name):
    z = np.load(os.path.join(indir, name), allow_pickle=False)
    E = edges_from(z)
    dV = volume(E)
    x = np.asarray(z["xsec_flat"], float).reshape(SHAPE) * dV
    var = np.asarray(z["sumw2_flat"], float).reshape(SHAPE) * dV * dV
    nevt = np.asarray(z["nevt_flat"], float).reshape(SHAPE)
    return x, var, nevt, E


def load_data_production(indir):
    import uproot
    f = uproot.open(os.path.join(indir, "xsec_5d_MEFHC_5iter_lgbm.root"))
    dens = np.asarray(f["hXSecND_flat"].values(), float)
    if dens.size != int(np.prod(SHAPE)):
        raise SystemExit(f"unexpected hXSecND_flat size {dens.size}")
    return dens.reshape(SHAPE)


def load_R(indir, name, dV):
    z = np.load(os.path.join(indir, name), allow_pickle=False)
    meta = json.loads(str(z["meta"]))
    return np.asarray(z["xsec_flat"], float).reshape(SHAPE) * dV, meta


def ew(x):
    """Project a 5D cell-integrated array to the 7x6 (E_avail, W) grid."""
    return x.sum(axis=(AX_PT, AX_PZ, AX_Q3))


def region_masks(E):
    a_lo = E["eavail"][:-1]
    w_lo = E["W"][:-1]
    a_hi = E["eavail"][1:]
    w_hi = E["W"][1:]
    corner_ew = (a_lo[:, None] >= 0.8 - 1e-9) & (w_lo[None, :] >= 1.8 - 1e-9)
    mid_ew = np.ones_like(corner_ew) & (w_lo[None, :] >= 1.4 - 1e-9) & (w_hi[None, :] <= 1.8 + 1e-9)
    overflow_ew = (a_lo[:, None] >= 3.0 - 1e-9) | (w_lo[None, :] >= 3.0 - 1e-9)
    return corner_ew, mid_ew, overflow_ew


def broadcast_ew(mask_ew):
    """Broadcast a (7, 6) (E_avail, W) mask to the 5D shape."""
    return np.broadcast_to(mask_ew[None, None, :, None, :], SHAPE)


def enu_upper_bound(E):
    """Kinematic upper bound on E_nu per 5D cell from the q3 and W definitions (PLAN.md §4).

    (M + omega)^2 = W^2 + q3^2 - (Q^2 - Qexp^2) and Q^2 - Qexp^2 >= -m_mu^2, so
    omega <= sqrt(W_hi^2 + q3_hi^2 + m_mu^2) - M; E_mu <= sqrt(pT_hi^2 + pz_hi^2 + m_mu^2).
    The W = 0 clamp (W^2 <= 0) only lowers omega's bound, so it is covered.
    """
    pt_hi, pz_hi = E["pt"][1:], E["pz"][1:]
    q3_hi, w_hi = E["q3"][1:], E["W"][1:]
    emu = np.sqrt(pt_hi[:, None] ** 2 + pz_hi[None, :] ** 2 + M_MU ** 2)
    om = np.sqrt(q3_hi[:, None] ** 2 + w_hi[None, :] ** 2 + M_MU ** 2) - M_N
    b = emu[:, :, None, None, None] + om[None, None, None, :, :]
    return np.broadcast_to(b, SHAPE)


def write_json(path, obj):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

    def conv(o):
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, (np.bool_,)):
            return bool(o)
        raise TypeError(type(o))

    with open(path, "w") as f:
        json.dump(obj, f, indent=1, default=conv, sort_keys=False)
