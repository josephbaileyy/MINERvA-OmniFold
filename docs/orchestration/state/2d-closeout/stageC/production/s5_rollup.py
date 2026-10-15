#!/usr/bin/env python3
"""Stage C production S5: the matrices of the recipe (Stage B REPORT §4 R1-R9), from the production unfolds and the
July sweep, with the C04 / X01 / KI-92 repairs. Login node, no Slurm. Frozen in DESIGN.md §8 before any job.

  python s5_rollup.py --out <dir>                      production rollup (after every unfold it reads is terminal)
  python s5_rollup.py --out <dir> --control-only       the May control alone (packaging smoke test; no products read)

Blocks (205 reported cells, E_U hXSec2D > 0, C order over (pT, p_par)):
  universe  R1-R4, R6. The July purity_newomni sweep (sweeps.json "pn/", each file sha-checked), except:
            - Flux (C04): MAT CalcCovMx with the nu-e+IMD constraint weights (GetUnivWgts; = the constraint file);
            - the 5 lateral bands (C05a, R4): replaced by the 10 production active-file unfolds (S3);
            - Muon_Energy_MINOS (X01): each S3 output x Phi_CV(pT) / Phi_MINOS,u(pT) (POT-combined, 12 playlists);
            - Rvp1pi (KI-92, R3): dropped (counted once as Rvn1pi);
            - every other band: MAT mean-centred, 1/N; plus the 1.4 % rank-1 normalization scaled to E_U (R6).
  stat      R5. Sample covariance (ddof 1, the VL170 convention) of the 300 three-stream replicas (S1).
  c08       R7. Seed main effect: sample covariance (ddof 1) over the 5 seed triplets of the per-triplet mean of
            the 20 bootstrap replicas (S4(i); the seed-42 column is S1_001-020). Rank <= 4, PSD.
  total     universe + stat + c08.
Reported, not added: the bkg-only separable term (S2), the bootstrap x seed interaction X02 (S4(i)) and the
universe x retraining interaction X03 (S4(ii)).

Control (frozen, runs first): the same universe-block code on the MAY sweep with no lateral swap and Rvp1pi kept must
reproduce every block and the total of the adopted VL175 rollup (uq_universe_covariance_c04x01.root, da92c5d2...) to
max|diff|/max|C| <= 1e-12; the weights must equal VL175's build.json numbers and the constraint file; the X01 factors
must equal VL175's minos_rescaled.npz to 1e-15. Any failed check is a stop (grant §3): products are written only
when every check passes, and s5.json records which failed otherwise.

Reused (pinned in manifest.json): build_repair.py (c04-repair) for wcov, mat_cov, th2, sq, summary and write_rollup;
the pilot's analyze_pilot.py for the reference pins. Run in root_6_28 (setup_salloc_env.sh; MAT on the path).
"""
import argparse
import hashlib
import importlib.util
import json
import os
import sys
from collections import OrderedDict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ST = HERE.parents[1]                       # docs/orchestration/state/2d-closeout


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


BR = _load("build_repair", ST / "c04-repair" / "scripts" / "build_repair.py")
import ROOT  # noqa: E402  (build_repair has set batch mode)

NS = "/pscratch/sd/j/josephrb/2d-closeout-stageC-production-20261015"
D2 = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding"
BF = f"{D2}/baseline_flux"
C04 = "/pscratch/sd/j/josephrb/2d-closeout-c04repair-20261012/build"
PIN = {
    "E_U": (f"{D2}/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root",
            "4f5a1b6d44b9e7212b233650bb00bfb626ae65461e3bf8033cd67866dbd7eb2c"),
    "sweeps_json": (ST / "stageB" / "evidence" / "b-genie-truth" / "sweeps.json",
                    "15b57de9124f204bf3cdf8cd0660c467783bf633bf0d45bfbd4e2506b19be2e4"),
    "vl175_rollup": (f"{C04}/uq_universe_covariance_c04x01.root",
                     "da92c5d2567647e8613bb3a6522176dbd9a287970082b45ac9e83e24684b1948"),
    "vl175_build_json": (f"{C04}/build.json", "dcc1331e8e510cc21a2abd95675cfc69acf92bae7ae3dfa43a3a94b9fdbe34dd"),
    "vl175_minos_npz": (f"{C04}/minos_rescaled.npz",
                        "8912376ef2a6cfce8bed515cc945d9d5778cf5c838154a685435c3c7ce25416d"),
    "vl175_budget": (f"{C04}/budget.json", "aab8a24ebd61df54e7277999d49300c3bdaa045710835bfa05adf3bfc71dd8fa"),
    "ml": (f"{D2}/uq/seedscan_lgbm_ml/uq_covariance_ml.root",
           "3b6b48ec89207ae29dc7bb0ddc5a41836c359c4805877d663731694b828d5db9"),
    "constraint": (BR.INPUTS["constraint"], BR.PINNED["constraint"]),
    "flux_mefhc": (f"{BF}/runEventLoopMC_MEFHC.root",
                   "d40aea69235cdc98644e1bb3e622e579d6b81904c004c83fe50465079989f316"),
}
LATERAL_BANDS = ["BeamAngleX", "BeamAngleY", "MuonResolution", "Muon_Energy_MINERvA", "Muon_Energy_MINOS"]
LATERALS = [f"{b}_{i}" for b in LATERAL_BANDS for i in (0, 1)]
FLUX, MINOS, DROP = "Flux", "Muon_Energy_MINOS", "Rvp1pi"
NORM = 0.014
SEEDS = [42, 45, 48, 51, 54]
PANEL_U = ["NormDISCC:0", "Flux:23", "MaRES:0", "MaCCQE:0", "2p2h:0", "MinosEfficiency:0", "Muon_Energy_MINOS:0"]
REL_TOL, X01_TOL, SYM_TOL, PSD_TOL, VEC_TOL = 1e-12, 1e-15, 1e-12, 1e-10, 1e-10
CHECKS = OrderedDict()


def sha(p):
    h = hashlib.sha256()
    with open(os.path.realpath(p), "rb") as f:
        for blk in iter(lambda: f.read(1 << 22), b""):
            h.update(blk)
    return h.hexdigest()


def check(name, ok, value=None):
    CHECKS[name] = {"ok": bool(ok), "value": value}
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  {value}" if value is not None else ""))
    return bool(ok)


def rel(a, b):
    return float(np.abs(a - b).max() / np.abs(b).max())


class Cells:
    """The 205 reported cells from E_U, read once."""
    def __init__(self):
        cv, self.area2 = BR.th2(PIN["E_U"][0])
        self.NX, self.NY = cv.shape
        self.rep = (cv > 0).ravel(order="C")
        self.x = cv.ravel(order="C")[self.rep]
        self.area = self.area2.ravel(order="C")[self.rep]

    def vec(self, path):
        a, _ = BR.th2(str(path))
        return a.ravel(order="C")[self.rep]

    def full(self, path):
        a, _ = BR.th2(str(path))
        return a


def sweep(cells, tag):
    """{band: {idx: {"path", "x"}}} from sweeps.json entries '<tag>/<Band>_<idx>', every file sha-checked."""
    recs = json.loads(Path(PIN["sweeps_json"][0]).read_text())
    out = {}
    bad = []
    for k, r in recs.items():
        if not k.startswith(tag + "/") or k.endswith("/CV"):
            continue
        band, idx = k[len(tag) + 1:].rsplit("_", 1)
        if sha(r["path"]) != r["sha256"]:
            bad.append(k)
            continue
        out.setdefault(band, {})[int(idx)] = {"path": r["path"], "x": cells.vec(r["path"])}
    check(f"{tag}_sweep_files_match_sweeps_json", not bad, bad[:5])
    return out


def band_cov(X, w=None):
    return BR.wcov(X, np.ones(X.shape[0]) if w is None else w)


def flux_weights():
    """Per-universe Flux weights from every playlist's flux MnvH1D (GetUnivWgts), and the X01 fluxes."""
    wl, phi_cv_l, phi_minos_l, pot = [], [], [], []
    for pl in BR.PLAYLISTS:
        f = ROOT.TFile.Open(f"{BF}/runEventLoopMC_{pl}.root")
        h = f.Get(BR.FLUX_HIST)
        n = h.GetNbinsX()
        wl.append(np.array(list(h.GetVertErrorBand("Flux").GetUnivWgts())))
        phi_cv_l.append(np.array([h.GetBinContent(i) for i in range(1, n + 1)]))
        mb = h.GetVertErrorBand(MINOS)
        phi_minos_l.append(np.array([[mb.GetHist(u).GetBinContent(i) for i in range(1, n + 1)] for u in range(2)]))
        f.Close()
        fd = ROOT.TFile.Open(f"{BF}/runEventLoopData_{pl}.root")
        pot.append(float(fd.Get("POTUsed").GetVal()))
        fd.Close()
    w = wl[0]
    check("weights_identical_across_playlists", all(np.array_equal(w, x) for x in wl))
    cons = {}
    for line in open(PIN["constraint"][0]):
        t = line.split()
        if len(t) == 3 and t[0] == "Flux":
            cons[int(t[1])] = float(t[2])
    cv = np.array([cons[i] for i in range(100)])
    check("weights_equal_constraint_file", w.size == 100 and np.array_equal(cv, w))
    bj = json.loads(Path(PIN["vl175_build_json"][0]).read_text())["numbers"]["weights"]
    mine = {"sum": float(w.sum()), "n_eff": float(w.sum() ** 2 / (w ** 2).sum())}
    check("weights_equal_vl175_build_json", mine["sum"] == bj["sum"] and mine["n_eff"] == bj["n_eff"], mine)
    pot = np.array(pot)
    phi_minos = np.tensordot(pot, np.stack(phi_minos_l), axes=([0], [0])) / pot.sum()
    return w, phi_minos


def x01(cells, paths, phi_minos, tag):
    """Rescale the two MINOS outputs by Phi_CV / Phi_MINOS,u per pT; 'used' is each output's own hFlux_pt."""
    fM = ROOT.TFile.Open(PIN["flux_mefhc"][0])
    hM = fM.Get(BR.FLUX_HIST)
    phi_cv = np.array([hM.GetBinContent(i) for i in range(1, hM.GetNbinsX() + 1)])
    fM.Close()
    used = []
    for p in paths:
        f = ROOT.TFile.Open(str(p))
        h = f.Get("hFlux_pt")
        used.append(np.array([h.GetBinContent(i) for i in range(1, h.GetNbinsX() + 1)]))
        f.Close()
    used = np.stack(used)
    check(f"{tag}_minos_outputs_divided_by_phi_cv", rel(used, np.stack([phi_cv, phi_cv])) <= X01_TOL,
          rel(used, np.stack([phi_cv, phi_cv])))
    scale = used / phi_minos
    ref = np.load(PIN["vl175_minos_npz"][0])["scale"]
    check(f"{tag}_x01_scale_equals_vl175", rel(scale, ref) <= X01_TOL, rel(scale, ref))
    return np.stack([(cells.full(p) * scale[u][:, None]).ravel(order="C")[cells.rep] for u, p in enumerate(paths)])


def universe_block(cells, bands, w, minos_x):
    """bands: {band: (n_u, 205) array}. Flux weighted, MINOS replaced by minos_x, sorted order, then the norm."""
    blocks = OrderedDict()
    for b in sorted(bands):
        X = minos_x if b == MINOS else bands[b]
        blocks[b] = band_cov(X, w if b == FLUX else None)
    v = NORM * cells.x
    blocks["__Normalization_flat"] = np.outer(v, v)
    tot = np.zeros((cells.rep.sum(),) * 2)
    for b in blocks:
        tot += blocks[b]
    return blocks, tot


def may_control(cells, w, phi_minos):
    may = sweep(cells, "may")
    check("may_44_bands_187_universes", len(may) == 44 and sum(len(v) for v in may.values()) == 187)
    bands = {b: np.stack([may[b][i]["x"] for i in sorted(may[b])]) for b in may}
    mx = x01(cells, [may[MINOS][u]["path"] for u in (0, 1)], phi_minos, "may")
    blocks, tot = universe_block(cells, bands, w, mx)
    f = ROOT.TFile.Open(PIN["vl175_rollup"][0])
    worst, missing, per_block = 0.0, [], {}
    for b, C in blocks.items():   # VL175 names the May bands after their files, "uni_full_<band>"
        S = BR.sq(f, f"hCov_universe_{b}" if b.startswith("__") else f"hCov_universe_full_{b}")
        if S is None:
            missing.append(b)
            continue
        worst = max(worst, rel(C, S))
        per_block[b] = {"rel_own": rel(C, S), "absmax_diff": float(np.abs(C - S).max()), "absmax": float(np.abs(S).max())}
    check("control_vl175_all_45_blocks_found", not missing and len(blocks) == 45, missing)
    CHECKS["control_vl175_per_block"] = {"ok": True, "value": sorted(per_block.items(), key=lambda kv: -kv[1]["rel_own"])[:6]}
    St = BR.sq(f, "hCov_universe_total")
    f.Close()
    # A block is compared at the total's scale; a non-null block also at its own scale. A null band (every entry
    # below 1e-12 of the total's scale: the NC knobs in this CC sample) is rounding-dominated, so its own-scale ratio
    # is not a meaningful test (DESIGN §11).
    scale = float(np.abs(St).max())
    null = sorted(b for b, v in per_block.items() if v["absmax"] < REL_TOL * scale)
    at_total = max(v["absmax_diff"] for v in per_block.values()) / scale
    own = max((v["rel_own"] for b, v in per_block.items() if b not in null), default=0.0)
    check("control_vl175_every_block_at_total_scale_le_1e-12", at_total <= REL_TOL, at_total)
    check("control_vl175_nonnull_blocks_own_scale_le_1e-12", own <= REL_TOL, {"max": own, "null_bands": null})
    worst = own
    check("control_vl175_total_le_1e-12", rel(tot, St) <= REL_TOL, rel(tot, St))
    return worst


def vec_identity(name, X, C, w=None):
    """aT C a from the matrix vs the (weighted, 1/N) variance of the integrals a.x of the same vectors."""
    a = cells_area
    s = X @ a
    ww = np.ones(len(s)) if w is None else np.asarray(w, float)
    mu = (ww * s).sum() / ww.sum()
    v = (ww * (s - mu) ** 2).sum() / ww.sum()
    q = float(a @ C @ a)
    r = abs(q - v) / max(abs(v), 1e-300)
    check(f"integral_from_vectors_{name}", r <= VEC_TOL, r)


def main():
    global cells_area
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--out-root", default=f"{NS}/out")
    ap.add_argument("--results", default=f"{NS}/results")
    ap.add_argument("--control-only", action="store_true")
    a = ap.parse_args()
    Path(a.out).mkdir(parents=True, exist_ok=True)
    rep = {"s5_rollup_sha256": sha(__file__), "build_repair_sha256": sha(BR.__file__), "out_root": a.out_root,
           "inputs": {}, "checks": CHECKS, "numbers": {}}
    for k, (p, want) in PIN.items():
        got = sha(p)
        rep["inputs"][k] = {"path": str(p), "sha256": got}
        check(f"pin_{k}", got == want, got[:16])
    cells = Cells()
    cells_area = cells.area
    check("reported_cells_205", int(cells.rep.sum()) == 205)
    w, phi_minos = flux_weights()
    rep["numbers"]["control_worst_block_rel"] = may_control(cells, w, phi_minos)
    if a.control_only:
        rep["S5"] = "CONTROL ONLY: " + ("PASS" if all(c["ok"] for c in CHECKS.values()) else "FAIL")
        Path(a.out, "s5_control.json").write_text(json.dumps(rep, indent=1, default=str) + "\n")
        print(rep["S5"])
        return 0 if rep["S5"].endswith("PASS") else 2

    try:
        ok = production(a, rep, cells, w, phi_minos)
    except Exception as e:   # a missing or unreadable input is a FAIL with a record, never a silent crash
        import traceback
        check("production_ran_without_exception", False, f"{type(e).__name__}: {e}")
        rep["traceback"] = traceback.format_exc()
        ok = False
    rep["S5"] = "PASS" if ok and all(c["ok"] for c in CHECKS.values()) else "FAIL"
    Path(a.out, "s5.json").write_text(json.dumps(rep, indent=1, default=str) + "\n")
    print("S5", rep["S5"])
    return 0 if rep["S5"] == "PASS" else 2


def functionals(cells):
    """F (31 x 205): the area-weighted integral, the 14 pT projections (sum over p_par of x * dp_par) and the 16 p_par
    projections (sum over pT of x * dpT), each over the reported cells (plan Stage C: 236 functionals = 205 + 1 + 30)."""
    ix, iy = np.divmod(np.flatnonzero(cells.rep), cells.NY)
    f = ROOT.TFile.Open(PIN["E_U"][0])
    h = f.Get("hXSec2D")
    wpt = np.array([h.GetXaxis().GetBinWidth(i) for i in range(1, cells.NX + 1)])
    wpz = np.array([h.GetYaxis().GetBinWidth(j) for j in range(1, cells.NY + 1)])
    f.Close()
    F = np.zeros((1 + cells.NX + cells.NY, ix.size))
    F[0] = cells.area
    for k in range(cells.NX):
        F[1 + k, ix == k] = wpz[iy[ix == k]]
    for k in range(cells.NY):
        F[1 + cells.NX + k, iy == k] = wpt[ix[iy == k]]
    return F


def fcov(Z, w=None):
    """Covariance of the rows of Z (n x m): weighted 1/sum(w) about the weighted mean, or 1/N."""
    return BR.wcov(Z, np.ones(Z.shape[0]) if w is None else w)


def func_identity(name, F, X, C, w=None, ddof_scale=1.0):
    """F C F^T from the matrix vs the covariance of the functionals F x of the same vectors (same convention).
    Returns (max|diff|, max|F C F^T|): the caller compares at the total's scale and, for a non-null block, at its own."""
    A = F @ C @ F.T
    V = fcov(X @ F.T, w) * ddof_scale
    return float(np.abs(A - V).max()), float(np.abs(A).max())


def func_check(name, diffs, scale):
    """The control's two-part rule (DESIGN §8): every block at the total's scale; a non-null block (max|F C F^T| at least
    1e-12 of that scale) also at its own scale. A null block's own-scale ratio is rounding."""
    at_total = max(d for d, _ in diffs.values()) / scale
    null = sorted(k for k, (_, m) in diffs.items() if m < REL_TOL * scale)
    own = max((d / m for k, (d, m) in diffs.items() if k not in null), default=0.0)
    check(f"functionals_from_vectors_{name}_at_total_scale_le_1e-10", at_total <= VEC_TOL, at_total)
    check(f"functionals_from_vectors_{name}_nonnull_own_scale_le_1e-10", own <= VEC_TOL,
          {"max": own, "null": null, "worst": sorted(((k, d / m if m else None) for k, (d, m) in diffs.items()
                                                      if k not in null), key=lambda kv: -(kv[1] or 0))[:3]})


def jack_rel_se(X, v):
    """Leave-one-out jackknife relative SE of the sample variance (ddof 1) of the projections X @ v."""
    s = X @ v
    n = s.size
    full = s.var(ddof=1)
    loo = np.array([np.delete(s, k).var(ddof=1) for k in range(n)])
    return float(np.sqrt((n - 1) / n * ((loo - loo.mean()) ** 2).sum()) / full)


def production(a, rep, cells, w, phi_minos):
    # ---- every unfold S5 reads passed its frozen analysis (DESIGN §7), on these outputs
    for f, key in (("c0.json", "C0"), ("s3.json", "S3"), ("s4ii.json", "S4ii"), ("s1.json", "S1"),
                   ("s2.json", "S2"), ("s4i.json", "S4i")):
        p = Path(a.results, f)
        r = json.loads(p.read_text()) if p.is_file() else {}
        check(f"analysis_{key}_PASS", r.get(key) == "PASS", r.get(key))
        check(f"analysis_{key}_out_root_matches", r.get("out_root") == a.out_root, r.get("out_root"))
        rep["inputs"][f] = {"path": str(p), "sha256": sha(p) if p.is_file() else None}
    # ---- the per-playlist flux and POT files, against VL175's recorded digests (build.json, pinned)
    bi = json.loads(Path(PIN["vl175_build_json"][0]).read_text())["inputs"]
    badf = [k for k in bi if k.startswith(("flux_MC_", "flux_Data_")) and sha(bi[k]["path"]) != bi[k]["sha256"]]
    check("flux_pot_24_files_match_vl175_build_json",
          not badf and sum(k.startswith(("flux_MC_", "flux_Data_")) for k in bi) == 24, badf)
    produced = {}

    def O(n):
        p = Path(a.out_root, n, "xsec.root")
        produced[n] = sha(p)
        return p

    # ---- universe block (R1-R4, R6)
    pn = sweep(cells, "pn")
    check("july_44_bands_187_universes", len(pn) == 44 and sum(len(v) for v in pn.values()) == 187)
    bands = {b: np.stack([pn[b][i]["x"] for i in sorted(pn[b])]) for b in pn if b not in LATERAL_BANDS + [DROP]}
    lat = {L: O(f"2dc_P_S3_{L.replace('_', '')}") for L in LATERALS}
    for b in LATERAL_BANDS:
        bands[b] = np.stack([cells.vec(lat[f"{b}_{i}"]) for i in (0, 1)])
    mx = x01(cells, [lat["Muon_Energy_MINOS_0"], lat["Muon_Energy_MINOS_1"]], phi_minos, "s3")
    ublocks, C_univ = universe_block(cells, bands, w, mx)
    check("universe_bands_43_plus_norm", len(ublocks) == 44, sorted(ublocks)[:3])
    M = BR.mat_cov(cells.x, {b: (mx if b == MINOS else bands[b]) for b in bands}, {FLUX: w})
    Cu_nonorm = C_univ - ublocks["__Normalization_flat"]
    check("mat_universe_block_le_1e-12", rel(M, Cu_nonorm) <= REL_TOL, rel(M, Cu_nonorm))
    vec_identity("flux_weighted", bands[FLUX], ublocks[FLUX], w)
    vec_identity("minos_x01", mx, ublocks[MINOS])

    # ---- stat (R5), bkg-only separable term (reported)
    X1 = np.stack([cells.vec(O(f"2dc_P_S1_{n:03d}")) for n in range(1, 301)])
    X2 = np.stack([cells.vec(O(f"2dc_P_S2_{n:03d}")) for n in range(1, 101)])
    C_stat = np.cov(X1, rowvar=False)
    C_bkg = np.cov(X2, rowvar=False)
    vec_identity("stat_ddof1", X1, C_stat * (299 / 300))
    s1 = np.sqrt(np.diag(C_stat))
    rep["numbers"]["stat"] = {"median_rel_pct": float(100 * np.median(s1 / cells.x)),
                              "ensemble_rel_se_of_sigma": float(1 / np.sqrt(2 * 299)),
                              "nested_150_vs_300_sigma_ratio_median":
                                  float(np.median(np.sqrt(np.diag(np.cov(X1[:150], rowvar=False))) / s1))}
    rep["numbers"]["bkg_separable"] = {"sigma_bkg_over_sigma_stat_median":
                                       float(np.median(np.sqrt(np.diag(C_bkg)) / s1))}

    # ---- C08 and X02 from the S4(i) panel (R7)
    Y = np.stack([np.stack([cells.vec(O(f"2dc_P_S1_{n:03d}") if s == 42 else O(f"2dc_P_S4B_s{s}_{n:02d}"))
                            for n in range(1, 21)]) for s in SEEDS])           # (T=5, B=20, 205)
    T, B = Y.shape[:2]
    mt = Y.mean(axis=1)
    C08 = np.cov(mt, rowvar=False)

    def interaction(Yb):
        t_, b_ = Yb.shape[:2]
        Rr = Yb - Yb.mean(axis=1)[:, None, :] - Yb.mean(axis=0)[None, :, :] + Yb.mean(axis=(0, 1))[None, None, :]
        Rf = Rr.reshape(t_ * b_, -1)
        return Rf.T @ Rf / ((t_ - 1) * (b_ - 1))
    C_int = interaction(Y)
    fml = ROOT.TFile.Open(PIN["ml"][0])
    sml = np.sqrt(np.diag(BR.sq(fml, "hCov2D_reported")))
    fml.Close()
    x02_med = float(np.median(np.diag(C_int) / np.diag(C_stat)))
    x02_loo = np.array([np.median(np.diag(interaction(np.delete(Y, k, axis=1))) / np.diag(C_stat)) for k in range(B)])
    rep["numbers"]["c08"] = {
        "rank": int(np.linalg.matrix_rank(C08)), "median_rel_pct": float(100 * np.median(np.sqrt(np.diag(C08)) / cells.x)),
        "dof": T - 1, "gaussian_rel_se_of_variance": float(np.sqrt(2 / (T - 1))),
        "sigma_c08_over_sigma_ml_median": float(np.median(np.sqrt(np.diag(C08)) / sml)),
        "random_effects_seed_var_clipped_median_rel_pct":
            float(100 * np.median(np.sqrt(np.maximum(np.diag(C08) - np.diag(C_int) / B, 0)) / cells.x))}
    rep["numbers"]["x02"] = {
        "interaction_var_over_stat_var_median": x02_med,
        "jackknife_se_over_bootstrap_seeds": float(np.sqrt((B - 1) / B * ((x02_loo - x02_loo.mean()) ** 2).sum())),
        "dof": (T - 1) * (B - 1), "gaussian_rel_se_of_variance": float(np.sqrt(2 / ((T - 1) * (B - 1)))),
        "interaction_over_B_over_c08_diag_median": float(np.median(np.diag(C_int) / B / np.diag(C08)))}

    # ---- X03 from the S4(ii) panel (reported, with uncertainties)
    cvs = {s: cells.vec(O("2dc_P_C0_cv" if s == 42 else f"2dc_P_S4CV_s{s}")) for s in SEEDS}
    x03 = {}
    for u in PANEL_U:
        d = np.stack([cells.vec(O(f"2dc_P_S4U_{u.replace(':', '')}_s{s}")) - cvs[s] for s in SEEDS])
        dm = np.abs(d.mean(axis=0))
        sd = d.std(axis=0, ddof=1)
        med = float(np.median(sd / sml))
        loo = np.array([np.median(np.delete(d, k, axis=0).std(axis=0, ddof=1) / sml) for k in range(len(SEEDS))])
        n = len(SEEDS)
        x03[u] = {"shift_median_rel_pct": float(100 * np.median(dm / cells.x)),
                  "seed_sd_of_shift_median_rel_pct": float(100 * np.median(sd / cells.x)),
                  "seed_sd_over_sigma_ml_median": med,
                  "seed_sd_over_sigma_ml_jackknife_se": float(np.sqrt((n - 1) / n * ((loo - loo.mean()) ** 2).sum())),
                  "dof": n - 1, "gaussian_rel_se_of_sd": float(1 / np.sqrt(2 * (n - 1)))}
    rep["numbers"]["x03"] = x03

    # ---- the 31 functionals from vectors vs matrix, per block (plan Stage C)
    F = functionals(cells)
    scale = float(np.abs(F @ (C_univ + C_stat + C08) @ F.T).max())     # the total's functional scale
    diffs = {b: func_identity(b, F, (mx if b == MINOS else bands[b]), ublocks[b], w if b == FLUX else None)
             for b in bands}
    diffs["stat"] = func_identity("stat", F, X1, C_stat, None, 300 / 299)
    diffs["c08"] = func_identity("c08", F, mt, C08, None, T / (T - 1))
    func_check("blocks", diffs, scale)
    vn = F @ (NORM * cells.x)
    rn = rel(F @ ublocks["__Normalization_flat"] @ F.T, np.outer(vn, vn))
    check("functionals_normalization_rank1_le_1e-10", rn <= VEC_TOL, rn)

    # ---- centring conventions (R9): offset of each band's centre and of the stat ensemble mean from E_U
    cen = {}
    for b in bands:
        X = mx if b == MINOS else bands[b]
        ww = w if b == FLUX else np.ones(X.shape[0])
        c = (ww[:, None] * X).sum(axis=0) / ww.sum()
        sb = np.sqrt(np.maximum(np.diag(ublocks[b]), 0))
        cen[b] = {"centre": "weighted mean" if b == FLUX else "mean",
                  "median_abs_offset_rel_pct": float(100 * np.median(np.abs(c - cells.x) / cells.x)),
                  "median_abs_offset_over_sigma_band": float(np.median(np.abs(c - cells.x)[sb > 0] / sb[sb > 0]))
                  if np.any(sb > 0) else None}
    cen["stat"] = {"centre": "replica mean (ddof 1 covariance)",
                   "median_abs_offset_over_sigma_mean": float(np.median(np.abs(X1.mean(axis=0) - cells.x) / (s1 / np.sqrt(300))))}
    rep["numbers"]["centring"] = cen

    # ---- total and its checks (plan Stage C)
    C_tot = C_univ + C_stat + C08
    for n, C in (("universe", C_univ), ("stat", C_stat), ("c08", C08), ("total", C_tot)):
        check(f"symmetric_{n}", np.abs(C - C.T).max() <= SYM_TOL * np.abs(C).max())
        ev = np.linalg.eigvalsh((C + C.T) / 2)
        check(f"psd_{n}", ev.min() >= -PSD_TOL * ev.max(), float(ev.min() / ev.max()))
        rep["numbers"][f"{n}_rank"] = int(np.sum(ev > PSD_TOL * ev.max()))
        rep["numbers"][f"{n}_summary"] = BR.summary(C, cells.x, cells.area)
    # ---- ensemble error in the modes used for inference: the 10 leading eigenmodes of the total and the 31 functionals
    ev, V = np.linalg.eigh(C_tot)
    lead = V[:, np.argsort(ev)[::-1][:10]]
    rep["numbers"]["ensemble_error"] = {
        "stat_jackknife_rel_se_of_variance_leading10_modes": [jack_rel_se(X1, lead[:, k]) for k in range(10)],
        "stat_jackknife_rel_se_of_variance_31_functionals": [jack_rel_se(X1, F[k]) for k in range(F.shape[0])],
        "stat_share_of_total_variance_leading10_modes": [float(lead[:, k] @ C_stat @ lead[:, k] / (lead[:, k] @ C_tot @ lead[:, k]))
                                                         for k in range(10)],
        "c08_gaussian_rel_se_of_variance": float(np.sqrt(2 / (T - 1)))}
    proj = F @ C_tot @ F.T
    rep["numbers"]["functionals_total_sigma_rel_pct"] = (100 * np.sqrt(np.diag(proj)) / np.abs(F @ cells.x)).tolist()
    vl = json.loads(Path(PIN["vl175_budget"][0]).read_text())
    rep["numbers"]["vl175_block_sum"] = vl.get("repaired", {}).get("block_sum")
    rep["inputs"]["production_outputs"] = produced
    ok = all(c["ok"] for c in CHECKS.values())
    if ok:
        np.savez(Path(a.out, "production_cov.npz"), cells_x_EU=cells.x, area=cells.area, functionals=F, universe=C_univ,
                 stat=C_stat, c08=C08, total=C_tot, bkg_separable=C_bkg, x02_interaction=C_int,
                 **{f"band_{b}": m for b, m in ublocks.items()})
        f = ROOT.TFile.Open(PIN["E_U"][0])
        h = f.Get("hXSec2D")
        pt = np.array([h.GetXaxis().GetBinLowEdge(i) for i in range(1, cells.NX + 2)])
        pz = np.array([h.GetYaxis().GetBinLowEdge(i) for i in range(1, cells.NY + 2)])
        cells_hist = ROOT.TH2D("hReportedCells", "reported cells (E_U hXSec2D > 0)", cells.NX, pt, cells.NY, pz)
        cells_hist.SetDirectory(0)
        for ix in range(cells.NX):
            for iy in range(cells.NY):
                cells_hist.SetBinContent(ix + 1, iy + 1, 1.0 if h.GetBinContent(ix + 1, iy + 1) > 0 else 0.0)
        f.Close()
        BR.write_rollup(str(Path(a.out, "uq_production_covariance.root")), ublocks, C_univ, C_tot,
                        cells_hist, cells.NX, cells.NY, np.flatnonzero(cells.rep), pt, pz)
        rep["products"] = {n: sha(Path(a.out, n)) for n in ("production_cov.npz", "uq_production_covariance.root")}
    return ok


if __name__ == "__main__":
    sys.exit(main())
