"""CENTER2D: how far the nominal-centred 2D covariance sits from the mean-centred one (tier3-design, 2026-11-28; local,
0 node-h; CENTER2D-DECLARATION.md beside this file, merged in #1446, is the authority for every rule below).

usage:
  python3 -I -B center2d.py expected                         # the 16 fetched files' digests, from committed records
  python3 -I -B center2d.py rehearsal --out RECORD.json      # part R: the committed pre-G2R blocks, no label
  python3 -I -B center2d.py main FETCH_DIR --out RECORD.json [--er E_R_XSEC_ROOT]   # parts T and D

For each universe band b (the 38 weight bands and the 5 laterals; Muon_Energy_MINOS through its X01 rescale), with
universes X_i, weights w (the 100 constraint weights for Flux, 1 otherwise) and the nominal unfold X0:
  V_mean = wcov(X, w) (MAT, the reported convention), V_nom = sum_i w_i (X_i - X0)(X_i - X0)^T / sum_i w_i,
  V_nom - V_mean = b b^T with b = mu - X0 exactly, and M = sum_b b b^T.
Readings R1-R6 and the labels are the declaration's section 5; the controls are its section 6 (any failure is a STOP
recorded unrepaired). The training-noise term is "not separable, disclosed" (section 4): no noise column is computed.

It prints statuses only; the numbers are in the record, read by the director first.
"""
import argparse
import gzip
import hashlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.environ.get("CENTER2D_REPO") or os.path.abspath(os.path.join(HERE, *[".."] * 7))
FD = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd"
G2R = FD + "/receipts-cov2d/g2r/readout"
RE2 = "docs/orchestration/state/2d-closeout/stageF/methods/re2/run"
PINS = {  # name -> (path at origin/main, sha256 of the file's bytes)
    "blocks_AR23": (FD + "/receipts-cov2d/readout/AR23/blocks_AR23.npz",
                    "abaebaeae6c9cb075dcb974a420dbf148809d01b2cabc8deda31f318bf6715ee"),
    "blocks_G18": (FD + "/receipts-cov2d/readout/G18/blocks_G18.npz",
                   "7eb657b82ae953bdf0584eda27264c52a64bcb48baea52dfc194f5efe440ea3d"),
    "data_g2r_json": (G2R + "/data/data_g2r.json", "cd975b64402325da489ae608277faf5f6d7a7cbebe4974465f90b07c336e083f"),
    "data_connect_log": (G2R + "/data/connect.log.txt",
                         "957750e57a6bc43ac62b629d6d140cd0b9479c2db93744937b29a1555a3e21c3"),
    "score_AR23": (G2R + "/AR23/score_g2r_AR23.json", "fb6d1f7fddfa18124bf097087a2f895582ef0991f9888c5ab1ce16cefbbe3079"),
    "score_G18": (G2R + "/G18/score_g2r_G18.json", "27374aab74793444ee20561ced1066247b225a40067092d7d181e186128b9ec2"),
    "partc_sums": (RE2 + "/partc_r2/partc-r2/SHA256SUMS",
                   "bf259be46ef1c4ddf8e6a18bfd49e1626b04f9a284e42a4024403e66ed60e25b"),
    "s5r_json_gz": (RE2 + "/partc_r2/partc-r2/s5/s5.json.gz",
                    "5c489837f999ea4bf8ea416be7d67fa5ba9e3107acf32cfc18f74545a1ee705e"),
    "cov2d_py": ("2d-unfolding/cov2d/cov2d.py", "76cbceba395bc6bbf8fc5cce9cf44fc0f21354dff8591cbdee578e0fddcaf8ed"),
}
PARTB_SUMS_DIR = RE2 + "/partb_readout/sums"
PARTB_SUMS_N, PARTB_SUMS_CAT = 35, "d3e89361695bd95735bd918008a741377782bf7f3635f146e76b567e1cac77d9"
ER_LOCAL = "/Users/josephbailey/c2eff-data/c2eff-run1/files/inputs/001_xsec.root"
ER_SHA = "a5c13fc38d64242bc9ee459fac87568a2f97fddf7a3ac97cc6f91eb4c2a31cef"
TUNES = ("AR23", "G18")
MINOS = "Muon_Energy_MINOS"
NORM_KEY = "__Normalization_flat"
S3_LABELS = ("BeamAngleX", "BeamAngleY", "MuonResolution", "MuonEnergyMINERvA", "MuonEnergyMINOS")
S3_BAND = dict(zip(S3_LABELS, ("BeamAngleX", "BeamAngleY", "MuonResolution", "Muon_Energy_MINERvA", MINOS)))
NS_G2R = "/pscratch/sd/j/josephrb/cov2d-g2r-20261112/readout"
NS_RE2 = "/pscratch/sd/j/josephrb/2d-closeout-re2-20261023"
NS_C04 = "/pscratch/sd/j/josephrb/2d-closeout-c04repair-20261012/build"
FETCH = (  # tar label -> pscratch path; center2d_fetch_remote.py carries the same list (a test checks it)
    ("g2r/data_g2r.npz", NS_G2R + "/data/data_g2r.npz"),
    ("g2r/blocks_g2r_AR23.npz", NS_G2R + "/AR23/blocks_g2r_AR23.npz"),
    ("g2r/blocks_g2r_G18.npz", NS_G2R + "/G18/blocks_g2r_G18.npz"),
    ("partc/cov2d_Q_205.npz", NS_RE2 + "/partc-r2/outA/cov2d_Q_205.npz"),
    ("partc/production_cov.npz", NS_RE2 + "/partc-r2/s5/production_cov.npz"),
    *((f"partb/S3_{L}{u}.root", f"{NS_RE2}/partb/out/S3_{L}{u}/xsec.root") for L in S3_LABELS for u in (0, 1)),
    ("c04/minos_rescaled.npz", NS_C04 + "/minos_rescaled.npz"),
)
N_FETCH = len(FETCH)
DATA_FILES = ("g2r/data_g2r.npz", "partc/cov2d_Q_205.npz", "partc/production_cov.npz", "c04/minos_rescaled.npz",
              *(f"partb/S3_{L}{u}.root" for L in S3_LABELS for u in (0, 1)))
NPT, NPZ, NCELL = 14, 16, 205
PT_EDGES = np.array([0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55, 0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50])
PZ_EDGES = np.array([1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0])
TOL = 1e-12          # every C-RECON, C-ID, C-PSD and C-ADD tolerance (declaration section 6)
RANK_TOL = 1e-12     # the retained ranks: eigenvalues above 1e-12 of the largest (COV2D's and G2R's rule)
RANK_BANDS = ((1, 73), (74, 139), (140, None))   # T2A's bands; the last ends at ndf
S_TR_CUT, RANK_CUT = 0.01, 0.10
NOISE_TERM = "not separable, disclosed"
NOISE_STATEMENT = (
    "E_R, all 175 universes and all 10 laterals share estimator seed 42 (declaration section 4), so the training-noise "
    "term is not separable from these records. With b = b_bar + n (b_bar the seed average, E[n] = 0), E_seed[b b^T] = "
    "b_bar b_bar^T + Cov_seed(b), so the raw M is, in expectation over training seeds, at least the seed-averaged term. "
    "Any one realization (this one, at seed 42) can fall on either side. D11's X03 (seed SD of six Stage C universes' "
    "shifts, median 1.24-1.33 sigma_ML) is the only measurement of this noise; it is cited, not used.")
LABEL_READS = {
    "NEGLIGIBLE": ("Nominal centring would add under 1% of the trace and under 10% on average in every rank band; the "
                   "seed-averaged term is, in expectation, no larger. Any one realization (this one, at seed 42) can "
                   "fall on either side."),
    "APPRECIABLE": ("As built (one training seed), M adds at least 10% on average in some rank band; how much of it is "
                    "asymmetric response and how much is training noise is not separable from these records."),
    "INTERMEDIATE": "Visible in the trace, but under 10% on average in every rank band.",
}


class Stop(Exception):
    pass


# ---------------------------------------------------------------- committed inputs
def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha_file(p: str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_blob(path: str) -> bytes:
    r = subprocess.run(["git", "-C", REPO, "cat-file", "blob", f"origin/main:{path}"], capture_output=True)
    if r.returncode != 0:
        raise Stop(f"C-PIN: origin/main:{path} is not readable")
    return r.stdout


def pinned(name: str) -> bytes:
    path, want = PINS[name]
    b = git_blob(path)
    if sha(b) != want:
        raise Stop(f"C-PIN: origin/main:{path} has sha256 {sha(b)}, not {want}")
    return b


def partb_sums() -> dict:
    r = subprocess.run(["git", "-C", REPO, "ls-tree", "--name-only", "origin/main", PARTB_SUMS_DIR + "/"],
                       capture_output=True, text=True)
    names = sorted(p for p in r.stdout.split() if os.path.basename(p).startswith("SHA256SUMS.J"))
    if r.returncode != 0 or len(names) != PARTB_SUMS_N:
        raise Stop(f"C-PIN: part B sums: {len(names)} files, not {PARTB_SUMS_N}")
    blobs = [git_blob(p) for p in names]
    if sha(b"".join(blobs)) != PARTB_SUMS_CAT:
        raise Stop(f"C-PIN: part B sums concatenate to {sha(b''.join(blobs))}, not {PARTB_SUMS_CAT}")
    out = {}
    for b in blobs:
        for ln in b.decode().splitlines():
            d, rel = ln.split()
            out[rel] = d
    return out


def load_cov2d():
    """cov2d.py (numpy only) at its pinned sha, imported unchanged, for BANDS, ORDER and LATERAL_BANDS."""
    b = pinned("cov2d_py")
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "cov2d.py")
        with open(p, "wb") as f:
            f.write(b)
        spec = importlib.util.spec_from_file_location("cov2d_pinned", p)
        m = importlib.util.module_from_spec(spec)
        sys.modules["cov2d_pinned"] = m
        spec.loader.exec_module(m)
    return m


def band_sets():
    c = load_cov2d()
    weight, lateral = list(c.ORDER), list(c.LATERAL_BANDS)
    nu = dict(c.BANDS)
    nu.update({L: 2 for L in lateral})
    if len(weight) != 38 or sum(c.BANDS.values()) != 175 or len(lateral) != 5 or MINOS not in lateral:
        raise Stop("C-PIN: cov2d.py's bands are not 38 weight bands of 175 universes and 5 laterals")
    if sorted(S3_BAND.values()) != sorted(lateral):
        raise Stop("C-PIN: the S3 labels do not map onto cov2d.py's laterals")
    return weight, lateral, nu, c.FLUX


def logged_flux() -> tuple:
    for ln in pinned("data_connect_log").decode().splitlines():
        if ln.startswith("[PASS] weights_equal_vl175_build_json"):
            d = json.loads(ln.split(None, 2)[2].replace("'", '"'))
            return float(d["sum"]), float(d["n_eff"])
    raise Stop("C-FLUX: the data connect log has no weights_equal_vl175_build_json line")


def expected_digests() -> dict:
    """label -> sha256 for the 16 fetched files, every one from a committed record (never typed)."""
    d = json.loads(pinned("data_g2r_json"))
    if d.get("verdict") != "PASS" or d.get("controls_failed") != []:
        raise Stop("C-PIN: data_g2r.json is not a PASS with no failed control")
    out = {"g2r/data_g2r.npz": d["npz_sha256"]}
    for T in TUNES:
        s = json.loads(pinned(f"score_{T}"))
        if s.get("controls_failed") != [] or s.get("stop") != []:
            raise Stop(f"C-PIN: score_g2r_{T}.json has a failed control or a stop")
        out[f"g2r/blocks_g2r_{T}.npz"] = s["blocks_npz_sha256"]
    sums = {ln.split()[1]: ln.split()[0] for ln in pinned("partc_sums").decode().splitlines() if ln.strip()}
    out["partc/cov2d_Q_205.npz"] = sums["./outA/cov2d_Q_205.npz"]
    out["partc/production_cov.npz"] = sums["./s5/production_cov.npz"]
    s5 = json.loads(gzip.decompress(pinned("s5r_json_gz")))
    if s5.get("S5") != "PASS" or s5.get("arm") != "refined":
        raise Stop("C-PIN: S5_R's s5.json is not the refined arm's PASS")
    for k in ("s3_x01_scale_equals_vl175", "pin_vl175_minos_npz", "s3_minos_outputs_divided_by_phi_cv"):
        if s5["checks"].get(k, {}).get("ok") is not True:
            raise Stop(f"C-PIN: S5_R's check {k} is not True")
    if s5["inputs"]["E_R"]["sha256"] != ER_SHA:
        raise Stop("C-PIN: S5_R's E_R is not a5c13fc3")
    if s5["products"]["production_cov.npz"] != out["partc/production_cov.npz"]:
        raise Stop("C-PIN: S5_R's production_cov.npz digest differs from partc-r2's SHA256SUMS")
    pb = partb_sums()
    if pb.get("ER/xsec.root") != ER_SHA:
        raise Stop("C-PIN: part B's ER/xsec.root digest is not a5c13fc3")
    po = s5["inputs"]["production_outputs"]
    for L in S3_LABELS:
        for u in (0, 1):
            a, b = pb[f"S3_{L}{u}/xsec.root"], po[f"2dc_P_S3_{L}{u}"]
            if a != b:
                raise Stop(f"C-PIN: S3_{L}{u}: part B's digest differs from S5_R's")
            out[f"partb/S3_{L}{u}.root"] = a
    mr = s5["inputs"]["vl175_minos_npz"]
    if mr["path"] != dict(FETCH)["c04/minos_rescaled.npz"]:
        raise Stop("C-PIN: S5_R's X01 file is not the path fetched")
    out["c04/minos_rescaled.npz"] = mr["sha256"]
    if sorted(out) != sorted(dict(FETCH)) or any(len(v) != 64 for v in out.values()):
        raise Stop("C-PIN: the expected digests do not cover exactly the 16 fetched files")
    return out


# ---------------------------------------------------------------- reading files
def npz(b: bytes) -> dict:
    with np.load(io.BytesIO(b), allow_pickle=False) as z:
        return {k: np.asarray(z[k]) for k in z.files}


def th2_values(path: str, name: str = "hXSec2D") -> np.ndarray:
    import uproot
    with uproot.open(path) as f:
        h = f[name]
        ex, ey = h.axis(0).edges(), h.axis(1).edges()
        if len(ex) != NPT + 1 or len(ey) != NPZ + 1 or not (np.allclose(ex, PT_EDGES, rtol=0, atol=1e-9)
                                                           and np.allclose(ey, PZ_EDGES, rtol=0, atol=1e-9)):
            raise Stop(f"C-FINITE: {os.path.basename(path)}:{name} is not the (pt 14, p|| 16) grid")
        v = np.asarray(h.values(flow=False), np.float64)
    if v.shape != (NPT, NPZ):
        raise Stop(f"C-FINITE: {os.path.basename(path)}:{name} has shape {v.shape}")
    return v


def need(arrs: dict, key: str, shape: tuple, what: str) -> np.ndarray:
    if key not in arrs:
        raise Stop(f"C-FINITE: {what} has no {key!r}")
    a = np.asarray(arrs[key], np.float64)
    if a.shape != shape or not np.all(np.isfinite(a)):
        raise Stop(f"C-FINITE: {what}[{key!r}] has shape {a.shape} (want {shape}) or non-finite values")
    return a


# ---------------------------------------------------------------- the algebra
def wcov(X: np.ndarray, w: np.ndarray) -> np.ndarray:
    """build_repair.wcov (MAT CalcCovMx with universe weights), reimplemented: build_repair imports ROOT."""
    w = np.asarray(w, float)
    mu = (w[:, None] * X).sum(axis=0) / w.sum()
    Z = X - mu
    return (Z.T * w) @ Z / w.sum()


def centre(X: np.ndarray, w: np.ndarray) -> np.ndarray:
    w = np.asarray(w, float)
    return (w[:, None] * X).sum(axis=0) / w.sum()


def v_nom(X: np.ndarray, w: np.ndarray, x0: np.ndarray) -> np.ndarray:
    w = np.asarray(w, float)
    Z = X - x0
    return (Z.T * w) @ Z / w.sum()


def amax(A) -> float:
    return float(np.max(np.abs(A)))


def scaled(resid: float, own: float, total: float) -> float:
    """A residual at the block's own scale, or at the total's when the block is null (below 1e-12 of it), as S5's
    control reads null bands."""
    s = own if own >= TOL * total else total
    return resid / s if s > 0 else (0.0 if resid == 0 else float("inf"))


def check(ctl: dict, name: str, ok: bool, **info) -> None:
    ctl[name] = {"pass": bool(ok), **info}
    if not ok:
        raise Stop(f"{name.split(':')[0]}: {name} failed ({json.dumps(info, default=str)[:300]})")


def psd(ctl: dict, name: str, A: np.ndarray) -> None:
    sym = amax(A - A.T) / amax(A) if amax(A) > 0 else 0.0
    lam = np.linalg.eigvalsh((A + A.T) / 2)
    low = float(lam.min() / lam.max()) if lam.max() > 0 else 0.0
    check(ctl, f"C-PSD:{name}", sym <= TOL and low >= -TOL, symmetry=sym, min_over_max_eig=low)


def eig_desc(C: np.ndarray):
    lam, U = np.linalg.eigh(C)
    o = np.argsort(-lam, kind="stable")
    return lam[o], U[:, o]


def rank_slices(ndf: int) -> list:
    out = []
    for lo, hi in RANK_BANDS:
        hi = ndf if hi is None else min(hi, ndf)
        out.append((lo, hi, None if lo > hi else slice(lo - 1, hi)))
    return out


def label(s_tr: float, means: list) -> str:
    vals = [m for m in means if m is not None]
    if any(m >= RANK_CUT for m in vals):
        return "APPRECIABLE"
    if s_tr < S_TR_CUT and all(m < RANK_CUT for m in vals):
        return "NEGLIGIBLE"
    return "INTERMEDIATE"


def readings(offsets: dict, vmean_diag: dict, x0: np.ndarray, C: np.ndarray, C_sys: np.ndarray, cells: np.ndarray,
             ctl: dict, tag: str) -> dict:
    """R1-R6 for M = sum_b b b^T against C (declaration section 5); C-PSD and C-ADD on the way."""
    bands = sorted(offsets)
    M = np.zeros_like(C)
    for b in bands:
        M += np.outer(offsets[b], offsets[b])
    psd(ctl, f"C:{tag}", C)
    psd(ctl, f"M:{tag}", M)
    lam, U = eig_desc(C)
    ndf = int(np.sum(lam > RANK_TOL * lam[0]))
    Ur, lr = U[:, :ndf], lam[:ndf]
    sl = rank_slices(ndf)
    trC = float(np.trace(C))
    # R1, R2
    s_tr = float(np.trace(M)) / trC
    d = np.diag(M) / np.diag(C)
    i_max = int(np.argmax(d))
    # R3 from M and per band (C-ADD)
    r = np.einsum("ik,ij,jk->k", Ur, M, Ur) / lr
    per = {}
    for b in bands:
        p = (Ur.T @ offsets[b]) ** 2 / lr
        per[b] = {"trace_share": float(offsets[b] @ offsets[b]) / trC,
                  "rank_band_means": [None if s is None else float(p[s].mean()) for _, _, s in sl]}
    means = [None if s is None else float(r[s].mean()) for _, _, s in sl]
    add_tr = abs(sum(per[b]["trace_share"] for b in bands) - s_tr) / max(abs(s_tr), np.finfo(float).tiny)
    add_r = [0.0 if m is None else abs(sum(per[b]["rank_band_means"][k] for b in bands) - m) / max(abs(m), np.finfo(float).tiny)
             for k, m in enumerate(means)]
    check(ctl, f"C-ADD:{tag}", add_tr <= TOL and all(a <= TOL for a in add_r), trace_rel=add_tr, rank_band_rel=add_r)
    # R4
    sq = np.sqrt(lr)
    W = (Ur.T @ M @ Ur) / sq[:, None] / sq[None, :]
    eps = float(np.linalg.eigvalsh((W + W.T) / 2).max())
    P_perp = np.eye(C.shape[0]) - Ur @ Ur.T
    coupling = float(np.linalg.norm(P_perp @ M @ Ur / sq[None, :], 2))
    # R5: top five by each decision quantity, and leave-one-band-out
    top = {"trace_share": sorted(bands, key=lambda b: -per[b]["trace_share"])[:5]}
    for k, (lo, hi, s) in enumerate(sl):
        top[f"ranks_{lo}_{hi}"] = None if s is None else sorted(bands, key=lambda b: -per[b]["rank_band_means"][k])[:5]
    loo = {}
    for b in bands:
        s2 = s_tr - per[b]["trace_share"]
        m2 = [None if m is None else m - per[b]["rank_band_means"][k] for k, m in enumerate(means)]
        loo[b] = {"trace_share": s2, "rank_band_means": m2, "label": label(s2, m2)}
    loo_range = {"trace_share": [min(v["trace_share"] for v in loo.values()), max(v["trace_share"] for v in loo.values())],
                 "rank_band_means": [None if means[k] is None else
                                     [min(v["rank_band_means"][k] for v in loo.values()),
                                      max(v["rank_band_means"][k] for v in loo.values())] for k in range(len(sl))],
                 "labels": sorted({v["label"] for v in loo.values()})}
    # R6
    r6 = {}
    for b in bands:
        ab = np.abs(offsets[b])
        pos = vmean_diag[b] > 0
        r6[b] = {"median_abs_b_over_x0": float(np.median(ab / np.abs(x0))),
                 "median_abs_b_over_sigma_band": float(np.median(ab[pos] / np.sqrt(vmean_diag[b][pos]))) if pos.any()
                 else None,
                 "cells_with_positive_band_variance": int(pos.sum())}
    lab = label(s_tr, means)
    return {
        "ndf": ndf,
        "rank_bands": [[lo, hi] if s is not None else [lo, None] for lo, hi, s in sl],
        "R1": {"trace_share": s_tr, "trace_share_of_C_sys": float(np.trace(M)) / float(np.trace(C_sys))},
        "R2": {"median": float(np.median(d)), "p84": float(np.percentile(d, 84)), "max": float(d[i_max]),
               "max_cell_globalid": int(cells[i_max])},
        "R3": {"rank_band_means": means, "overall_mean": float(r.mean()),
               "overall_mean_via_pinv": float(np.trace(Ur @ np.diag(1 / lr) @ Ur.T @ M)) / ndf,
               "max_r": float(r.max()), "max_r_rank": int(np.argmax(r)) + 1},
        "R4": {"epsilon": eps, "coupling_to_discarded": coupling},
        "R5": {"per_band": per, "top5": top, "leave_one_band_out": loo, "leave_one_band_out_range": loo_range},
        "R6": r6,
        "label_if_decided": lab,
        "label_reads": LABEL_READS[lab],
    }


def bands_and_checks(bands: dict, minos_x: np.ndarray, w_flux: np.ndarray, x0: np.ndarray, weight: list, lateral: list,
                     nu: dict, flux: str, ctl: dict, tag: str) -> tuple:
    """Per band: the universes used (MINOS replaced by minos_x), V_mean, b; C-ID per band."""
    if sorted(bands) != sorted(weight + lateral):
        raise Stop(f"C-FINITE: {tag}: the bands are not cov2d.py's 38 + 5")
    use, vm, off = {}, {}, {}
    worst = 0.0
    total = 0.0
    for b in sorted(bands):
        X = minos_x if b == MINOS else bands[b]
        if X.shape != (nu[b], NCELL) or not np.all(np.isfinite(X)):
            raise Stop(f"C-FINITE: {tag}: band {b} has shape {X.shape}, not ({nu[b]}, {NCELL})")
        w = w_flux if b == flux else np.ones(X.shape[0])
        use[b] = (X, w)
        vm[b] = wcov(X, w)
        off[b] = centre(X, w) - x0
        total = max(total, amax(v_nom(X, w, x0)))
    per = {}
    for b in sorted(bands):
        X, w = use[b]
        Vn = v_nom(X, w, x0)
        resid = amax(Vn - vm[b] - np.outer(off[b], off[b]))
        per[b] = scaled(resid, amax(Vn), total)
        worst = max(worst, per[b])
    check(ctl, f"C-ID:{tag}", worst <= TOL, worst_rel=worst, tol=TOL)
    return use, vm, off


def recon(ctl: dict, name: str, got: np.ndarray, want: np.ndarray, scale: float = None) -> None:
    s = amax(want) if scale is None else scale
    rel = amax(got - want) / s if s > 0 else (0.0 if amax(got - want) == 0 else float("inf"))
    check(ctl, f"C-RECON:{name}", rel <= TOL, rel=rel, tol=TOL)


def flux_check(ctl: dict, name: str, w: np.ndarray) -> None:
    lsum, lneff = logged_flux()
    s, neff = float(w.sum()), float(w.sum() ** 2 / (w ** 2).sum())
    check(ctl, f"C-FLUX:{name}", w.shape == (100,) and s == lsum and neff == lneff, sum=s, n_eff=neff,
          logged_sum=lsum, logged_n_eff=lneff)


# ---------------------------------------------------------------- the parts
BLOCK_KEYS = ("C_T", "C_univ", "C_lat", "C_norm", "C_stat", "C08", "C_model_abs")


def tune_controls(B: dict, sets: tuple, ctl: dict, tag: str) -> tuple:
    """Every tune control before any reading: C-FINITE, C-X0 (mask), C-FLUX, C-ID and C-RECON."""
    weight, lateral, nu, flux = sets
    mats = {k: need(B, k, (NCELL, NCELL), tag) for k in BLOCK_KEYS}
    x0 = need(B, "x_T", (NCELL,), tag)
    rep = np.asarray(B["rep"])
    check(ctl, f"C-X0:{tag}:mask", rep.shape == (NPT * NPZ,) and int(rep.astype(bool).sum()) == NCELL,
          cells=int(rep.astype(bool).sum()))
    w = need(B, "w_flux", (100,), tag)
    minos_x = need(B, "minos_x", (2, NCELL), tag)
    bands = {k[len("band__"):]: np.asarray(B[k], np.float64) for k in B if k.startswith("band__")}
    check(ctl, f"C-FINITE:{tag}", all(np.all(np.isfinite(v)) for v in bands.values()), bands=len(bands))
    flux_check(ctl, tag, w)
    use, vm, off = bands_and_checks(bands, minos_x, w, x0, weight, lateral, nu, flux, ctl, tag)
    recon(ctl, f"{tag}:C_univ", sum(vm[b] for b in sorted(weight)), mats["C_univ"])
    recon(ctl, f"{tag}:C_lat", sum(vm[b] for b in sorted(lateral)), mats["C_lat"])
    recon(ctl, f"{tag}:C_T_sum_of_blocks", sum(mats[k] for k in BLOCK_KEYS[1:]), mats["C_T"])
    return off, vm, mats, x0, np.flatnonzero(rep.astype(bool))


def tune_core(B: dict, sets: tuple, ctl: dict, tag: str) -> dict:
    off, vm, mats, x0, cells = tune_controls(B, sets, ctl, tag)
    return readings(off, {b: np.diag(vm[b]) for b in vm}, x0, mats["C_T"], mats["C_univ"] + mats["C_lat"], cells,
                    ctl, tag)


def part_rehearsal(sets: tuple) -> dict:
    out = {}
    for T in TUNES:
        ctl = {}
        tag = f"R:{T}"
        try:
            B = npz(pinned(f"blocks_{T}"))
            ctl[f"C-PIN:{tag}"] = {"pass": True}
            rd = tune_core(B, sets, ctl, tag)
            rd.pop("label_if_decided")
            rd.pop("label_reads")
            out[tag] = {"status": "OK", "label": None, "controls": ctl, "readings": rd}
        except Stop as e:
            out[tag] = {"status": "STOP", "stop": str(e), "controls": ctl}
    return out


def fetched(fetch_dir: str, expected: dict) -> tuple:
    """C-FETCH: the verifier's success line, SHA256SUMS, and each file's digest against the committed one."""
    status = {}
    v = os.path.join(fetch_dir, "verify.out")
    with open(v) as f:
        last = f.read().splitlines()[-1:]
    if last != [f"VERIFY OK {N_FETCH}"]:
        raise Stop(f"C-FETCH: verify.out does not end 'VERIFY OK {N_FETCH}' ({last})")
    with open(os.path.join(fetch_dir, "SHA256SUMS")) as f:
        rows = dict((rel[len("files/"):], d) for d, rel in (ln.split() for ln in f if ln.strip()))
    if sorted(rows) != sorted(expected):
        raise Stop("C-FETCH: SHA256SUMS does not list exactly the 16 fetched files")
    paths = {}
    for lab, want in expected.items():
        p = os.path.join(fetch_dir, "files", lab)
        got = sha_file(p) if os.path.isfile(p) and not os.path.islink(p) else None
        status[lab] = {"pass": got == want == rows[lab], "sha256": got, "want": want}
        paths[lab] = p
    return status, paths


def part_tune(T: str, sets: tuple, fst: dict, paths: dict) -> dict:
    ctl = {}
    tag = f"T:{T}"
    lab = f"g2r/blocks_g2r_{T}.npz"
    try:
        check(ctl, f"C-FETCH:{tag}", fst[lab]["pass"], **fst[lab])
        with open(paths[lab], "rb") as f:
            G = npz(f.read())
        B = npz(pinned(f"blocks_{T}"))
        ctl[f"C-PIN:{tag}"] = {"pass": True}
        for k in ("x_T", "rep", "w_flux", "minos_x"):
            if k not in G or k not in B:
                raise Stop(f"C-FINITE: {tag}: {k} missing")
        check(ctl, f"C-X0:{tag}", np.array_equal(G["x_T"], B["x_T"]) and np.array_equal(G["rep"], B["rep"]),
              note="blocks_g2r x_T and rep equal the committed blocks' bit for bit")
        check(ctl, f"C-FLUX:{tag}:equal", np.array_equal(G["w_flux"], B["w_flux"]))
        _, lateral, _, _ = sets
        check(ctl, f"C-RECON:{tag}:laterals_kept",
              all(np.array_equal(G[f"band__{L}"], B[f"band__{L}"]) for L in lateral)
              and np.array_equal(G["minos_x"], B["minos_x"]),
              note="c_t_prime keeps the committed lateral bands and minos_x")
        rd = tune_core(G, sets, ctl, tag)
        lab_ = rd.pop("label_if_decided")
        reads = rd.pop("label_reads")
        return {"status": "OK", "label": None, "descriptive_label": lab_, "descriptive_label_reads": reads,
                "note": "a tune result does not carry over to the data's matrix (COV2D-DECLARATION.md:226-227)",
                "controls": ctl, "readings": rd}
    except Stop as e:
        return {"status": "STOP", "stop": str(e), "controls": ctl}


def part_data(sets: tuple, fst: dict, paths: dict, er_path: str) -> dict:
    weight, lateral, nu, flux = sets
    ctl = {}
    tag = "D"
    try:
        bad = [k for k in DATA_FILES if not fst[k]["pass"]]
        check(ctl, "C-FETCH:D", not bad, failed=bad)
        def rd(k):
            with open(paths[k], "rb") as f:
                return f.read()
        Z, Q, S5, MR = (npz(rd(k)) for k in ("g2r/data_g2r.npz", "partc/cov2d_Q_205.npz", "partc/production_cov.npz",
                                              "c04/minos_rescaled.npz"))
        B = npz(pinned("blocks_AR23"))
        if sha_file(er_path) != ER_SHA:
            raise Stop(f"C-PIN: {er_path} is not E_R ({ER_SHA})")
        ctl["C-PIN:D"] = {"pass": True}
        # C-X0
        er = th2_values(er_path).ravel(order="C")
        rep = er > 0
        x0 = need(Q, "x", (NCELL,), "cov2d_Q_205.npz")
        check(ctl, "C-X0:D", int(rep.sum()) == NCELL and np.array_equal(er[rep], x0)
              and np.array_equal(rep, np.asarray(B["rep"]).astype(bool)),
              note="cov2d_Q_205.npz x equals E_R's hXSec2D on its 205 positive cells, the tunes' mask")
        # C-FLUX
        w = need(B, "w_flux", (100,), "blocks_AR23")
        check(ctl, "C-FLUX:D:equal_tunes", np.array_equal(w, npz(pinned("blocks_G18"))["w_flux"]))
        flux_check(ctl, "D", w)
        # the bands
        bands = {b: need(Z, f"band__{b}", (nu[b], NCELL), "data_g2r.npz") for b in weight}
        if sorted(k for k in Z if k.startswith("band__")) != sorted(f"band__{b}" for b in weight):
            raise Stop("C-FINITE: data_g2r.npz's bands are not the 38 weight bands")
        H = {}
        for L in S3_LABELS:
            H[L] = [th2_values(paths[f"partb/S3_{L}{u}.root"]) for u in (0, 1)]
            bands[S3_BAND[L]] = np.stack([h.ravel(order="C")[rep] for h in H[L]])
        scale = need(MR, "scale", (2, NPT), "minos_rescaled.npz")
        minos_x = np.stack([(H["MuonEnergyMINOS"][u] * scale[u][:, None]).ravel(order="C")[rep] for u in (0, 1)])
        use, vm, off = bands_and_checks(bands, minos_x, w, x0, weight, lateral, nu, flux, ctl, tag)
        # C-RECON
        C_new = need(Z, "C_new", (NCELL, NCELL), "data_g2r.npz")
        C_un = need(Z, "C_univ_new", (NCELL, NCELL), "data_g2r.npz")
        C_uo = need(Z, "C_univ_old", (NCELL, NCELL), "data_g2r.npz")
        Qm = need(Q, "Q", (NCELL, NCELL), "cov2d_Q_205.npz")
        Qu = need(Q, "universe", (NCELL, NCELL), "cov2d_Q_205.npz")
        s5b = {b: need(S5, f"band_{b}", (NCELL, NCELL), "S5_R") for b in weight + lateral + [NORM_KEY]}
        recon(ctl, "D:C_univ_new", sum(vm[b] for b in sorted(weight)), C_un)
        tot = amax(sum(s5b.values()))
        for L in sorted(lateral):
            recon(ctl, f"D:lateral:{L}", vm[L], s5b[L], scale=amax(s5b[L]) if amax(s5b[L]) >= TOL * tot else tot)
        old = sum(s5b[b] for b in sorted(weight))
        recon(ctl, "D:C_univ_old", old, C_uo)
        recon(ctl, "D:S5R_bands_sum_to_Q_universe", sum(s5b[b] for b in sorted(s5b)), Qu)
        recon(ctl, "D:C_new", Qm - old + C_un, C_new)
        C_sys = C_un + sum(s5b[L] for L in sorted(lateral))
        rdg = readings(off, {b: np.diag(vm[b]) for b in vm}, x0, C_new, C_sys, np.flatnonzero(rep), ctl, tag)
        lab = rdg.pop("label_if_decided")
        reads = rdg.pop("label_reads")
        return {"status": "OK", "label": lab, "label_reads": reads, "controls": ctl, "readings": rdg}
    except (Stop, OSError, KeyError, ValueError) as e:
        return {"status": "STOP", "stop": f"{type(e).__name__}: {e}", "controls": ctl}


# ---------------------------------------------------------------- record and main
def head(mode: str) -> dict:
    return {"schema": "center2d/1", "mode": mode, "declaration": "CENTER2D-DECLARATION.md (#1446)",
            "noise_term": NOISE_TERM, "noise_statement": NOISE_STATEMENT,
            "code_sha256": sha_file(os.path.abspath(__file__)),
            "pins": {k: v[1] for k, v in PINS.items()}, "partb_sums_concat_sha256": PARTB_SUMS_CAT}


def write(rec: dict, out: str) -> None:
    with open(out, "x") as f:
        json.dump(rec, f, indent=1, sort_keys=True, allow_nan=False)
        f.write("\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="mode", required=True)
    sub.add_parser("expected")
    r = sub.add_parser("rehearsal")
    r.add_argument("--out", required=True)
    m = sub.add_parser("main")
    m.add_argument("fetch_dir")
    m.add_argument("--out", required=True)
    m.add_argument("--er", default=ER_LOCAL)
    a = ap.parse_args(argv)
    if a.mode == "expected":
        try:
            exp = expected_digests()
        except (Stop, KeyError, ValueError) as e:
            print(f"CENTER2D EXPECTED REFUSED: {type(e).__name__}: {e}")
            return 3
        for lab, path in FETCH:
            print(f"{lab}\t{exp[lab]}\t{path}")
        return 0
    if os.path.lexists(a.out):
        print(f"refusing: {a.out} exists")
        return 2
    rec = head(a.mode)
    try:
        sets = band_sets()
        if a.mode == "rehearsal":
            rec["parts"] = part_rehearsal(sets)
        else:
            exp = expected_digests()
            rec["expected_digests"] = exp
            fst, paths = fetched(a.fetch_dir, exp)
            rec["fetch"] = fst
            rec["parts"] = {f"T:{T}": part_tune(T, sets, fst, paths) for T in TUNES}
            rec["parts"]["D"] = part_data(sets, fst, paths, a.er)
    except (Stop, OSError, KeyError, ValueError) as e:
        rec.update(status="STOP", stop=f"{type(e).__name__}: {e}")
        write(rec, a.out)
        print(f"CENTER2D STOP: {rec['stop']}")
        return 3
    bad = sorted(k for k, v in rec["parts"].items() if v["status"] != "OK")
    rec["status"] = "OK" if not bad else "STOP"
    rec["stopped_parts"] = bad
    write(rec, a.out)
    for k in sorted(rec["parts"]):
        print(f"{k}: {rec['parts'][k]['status']}")
    print("CENTER2D OK" if not bad else f"CENTER2D STOP in {bad}")
    return 0 if not bad else 3


if __name__ == "__main__":
    sys.exit(main())
