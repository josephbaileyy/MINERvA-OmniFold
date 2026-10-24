#!/usr/bin/env python3
"""RE-2 part C copy of stageF/rebuild/scripts/build_q_products.py (050c5b0d...), RE2-DECLARATION-C.md §3.7.

  --arm purity (default)  the original, unchanged: it must reproduce cov2d_Q_205.npz 771e49a5... and budget_Q.json's
                          numbers (K1-roll)
  --arm refined --pins-json FILE --eu-control E_U.root
                          Q_R's products and budget. What changes, and nothing else:
    - the six upstream digests (s5_npz, s5_root, s5_json, playlist_npz, q_npz, combination_json) are read from FILE,
      written by the run script from the previous steps' records (chain of custody; they cannot be declared first);
    - --eu is E_R (part B's ER, a5c13fc3...), the central value: x, the cells, the relative sigmas and hRel2D;
    - the two VL175 controls (budget.json and group_medians.json, BQ-22/BQ-24) are computed with the separately
      pinned E_U (--eu-control, 4f5a1b6d...) as their denominator only, so they are the same controls;
    - every input npz and json must carry arm = refined (CB-G), and s5.json's universe count field is the refined
      rollup's (38 bands, 175 universes).

The original docstring follows.

Stage F rebuild, step A and section 3 (SPEC.md in the parent directory): the adopted-Q products and budget_Q.json.

Q = S5 total + C_PL (DECISION-20261017-joseph-2d-adopt-s5-plus-playlist.md). Every input is read as bytes pinned
by sha256 (SPEC section 1); every check below is a STOP: a raised exception, a [STOP] line and exit code 2.

Writes, into --outdir (which must not exist; its parent must):
  uq_adopted_covariance.root   hCov_Q, hCov_S5total, hCov_universe_total, the 44 hCov_universe_<band>, hCov_stat,
                               hCov_c08, hCov_playlist, hCov_sum_universe_stat, hReportedCells
                               (every matrix in the S5 ROOT's hCov_combined bin layout)
  block_stat.root              hCov2D_reported (stat), hReportedCells, hRel2D = sqrt(diag stat) / E_U (14 x 16 grid)
  block_c08.root               hCov2D_reported (c08), hReportedCells
  block_playlist.root          hCov2D_reported (C_PL), hReportedCells
  cov2d_Q_205.npz / .json      Q, s5_total, universe, stat, c08, C_PL, cells (global ids pt*16 + pz), x = E_U[cells]
  budget_Q.json                the numbers of SPEC section 3, the checks and the controls
  SHA256SUMS                   every file above

Checks (SPEC section 2): A0 pins; A1 cell sets; A1' value-anchored order; A2 storage; A3 combination; A4 read-back;
A5 symmetry and PSD. Controls (SPEC section 3): the metric functions reproduce VL175's budget.json, the grouped
medians reproduce group_medians.json, and the Q, S5 and C_PL rows reproduce combination.json. Also reproduced, as
consistency controls: s5.json's block summaries and ranks, and the rhoFluxMuon value (0.900).

Reused, not reimplemented: reported_cells (read_cells, require_same_cells, reported_indices, grid_hist_to_array,
identity_hist, grid edges); the band-to-category map imported from plot_uncertainty_fig6_7_style; m2np and
lead_mode from rederive_flux_muonE_cross (the rhoFluxMuon producer, route A). The metric definitions follow
c04-repair/scripts/build_repair.py summary() (median, p84, min, max, sqrt_trace) and, for the integral and the 30
projections, playlist-term/scripts/combine_s5.py (S5's functionals F, F[0] = area).

Invocation (SPEC section 1; -I drops the script directory, so the archive's directories are put on sys.path):
  python3 -I -c "import sys, runpy; sys.path[:0] = [A+'/2d-unfolding/uq', A+'/2d-unfolding', A];
                 sys.argv = ['build_q_products.py', '--repo', A, ...]; runpy.run_path(SCRIPT, run_name='__main__')"
See README.md beside this script for the full argument list.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import sys

import numpy as np

# ---------------------------------------------------------------------------------------------------- pins (SPEC §1)
PINS = {
    "s5_npz": "6689d2fc2a795a72e66ee953a32d94c7906dd81a866771979f379c5f163a9ddc",
    "s5_root": "34cf33f96cd688e2c00064f314ff76d294b0d012b0bed5a4560cb1c2e3fc0df8",
    "s5_json": "8c815149517857302af4b3a64b0db4148a13515b8182bd6eebb2f89c57d92510",
    "playlist_npz": "c1723cb5e185ae7a6176fbbe523432ab87877c8cddcfe721eaed71f0a43b9476",
    "q_npz": "8ccb4d723c3dbf737a7fb1d5236e5e25409c41b42b64ac55dccbbc12f595600e",
    "combination_json": "050e256023277ec9da492ffa7b9d129275c3afa2bfc6c47091999d88de5bf18d",
    "eu": "4f5a1b6d44b9e7212b233650bb00bfb626ae65461e3bf8033cd67866dbd7eb2c",
    "ec": "142a45b0efc753d91e95376c28ac3f6a477d582014a919e49d6d71079a127fd5",
    "paper_anc": "6c6dce72050bb8f128fab8e286349b250bc60d1c767e162bf15a0f009f3573e3",
    "vl175_rollup": "da92c5d2567647e8613bb3a6522176dbd9a287970082b45ac9e83e24684b1948",
    "vl175_boot": "71a75821ceeb658710adca30243e39e7184e33f868f58ea56cffe63ba8db0115",
    "vl175_ml": "3b6b48ec89207ae29dc7bb0ddc5a41836c359c4805877d663731694b828d5db9",
    "vl175_blocks": "c2606f9095c61e3b0d56bbb72d4c6948b5662461da51563858ce3c8ae18824f8",
    "vl175_budget": "aab8a24ebd61df54e7277999d49300c3bdaa045710835bfa05adf3bfc71dd8fa",
    "vl175_group_medians": "7927c51ef7549601020517aee397748e10fc7603da7a847f9f833f789200900f",
}
INPUT_HELP = {
    "s5_npz": "S5 production_cov.npz",
    "s5_root": "S5 uq_production_covariance.root",
    "s5_json": "S5 s5.json (committed stageC/production/evidence/production/results/s5.json)",
    "playlist_npz": "playlist_term.npz",
    "q_npz": "s5_plus_playlist.npz (Q)",
    "combination_json": "combination.json (committed playlist-term/outputs/combination/)",
    "eu": "E_U: 2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root",
    "ec": "E_C: 2d_crossSection_omnifold_MEFHC_5iter.root (exact-split denominator only)",
    "paper_anc": "paper ancillary cov_ptpl_minerva_inclusive_6GeV.root",
    "vl175_rollup": "VL175 uq_universe_covariance_c04x01.root",
    "vl175_boot": "VL170 uq_covariance_boot300.root",
    "vl175_ml": "uq_covariance_ml.root",
    "vl175_blocks": "VL175 cov2d_blocks_205.npz",
    "vl175_budget": "VL175 budget.json (c04-repair/products/)",
    "vl175_group_medians": "group_medians.json (stageB/diagnostics/c04-grouped/)",
}

CHAIN = ("s5_npz", "s5_root", "s5_json", "playlist_npz", "q_npz", "combination_json")
E_R_SHA = "a5c13fc38d64242bc9ee459fac87568a2f97fddf7a3ac97cc6f91eb4c2a31cef"
E_U_SHA = PINS["eu"]

N_CELLS_REPORTED = 205
TOL_ID = 1e-12          # A2, A3, A5 symmetry; relative to the matrix max
PSD_TOL = 1e-10         # A5; s5_rollup.py PSD_TOL
RANK_TOLS = (1e-10, 1e-12)
TOL_CONTROL = 1e-12     # relative, every full-precision control value
NORM_BAND = "__Normalization_flat"
RHO_PRINTED = "0.900"   # values.tex \rhoFluxMuon (the VL175 value), printed precision 3 decimals
EXTRA_GROUPS = {"Training seed": "c08", "Run period": "C_PL"}   # SPEC §3 grouped medians, beyond the fig6/7 map


class Stop(RuntimeError):
    """A failed check or control. Never caught except to print it and exit nonzero."""


LOG = []
CHECKS = {}
CREATED = []   # the outdir, once this run has created it (STOPPED.txt is written only there)


def say(line):
    LOG.append(line)
    print(line, flush=True)


def check(name, ok, value=None):
    """Record one check; a failure is a STOP."""
    CHECKS[name] = {"pass": bool(ok), "value": value}
    if not ok:
        raise Stop(f"{name}: {value}")
    say(f"[PASS] {name}" + ("" if value is None else f"  {value}"))


def sha256(path):
    h = hashlib.sha256()
    with open(os.path.realpath(path), "rb") as f:
        for blk in iter(lambda: f.read(1 << 22), b""):
            h.update(blk)
    return h.hexdigest()


def relmax(a, b):
    """max|a - b| / max|b|: the 'to 1e-12 of the matrix max' measure."""
    return float(np.max(np.abs(a - b)) / np.max(np.abs(b)))


def rel(a, b):
    a, b = float(a), float(b)
    if b == 0.0:
        return 0.0 if a == 0.0 else float("inf")
    return abs(a - b) / abs(b)


# ------------------------------------------------------------------------------------------------------ ROOT helpers
def open_root(ROOT, path):
    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        raise Stop(f"cannot open {path}")
    return f


def get(f, name):
    h = f.Get(name)
    if not h:
        raise Stop(f"{name} missing in {f.GetName()}")
    return h


def sq(h):
    """Square TH2D contents as an (n, n) array, [i, j] = bin (i + 1, j + 1)."""
    n = h.GetNbinsX()
    if h.GetNbinsY() != n:
        raise Stop(f"{h.GetName()} is not square")
    return np.array([[h.GetBinContent(i + 1, j + 1) for j in range(n)] for i in range(n)])


def bin_layout(h):
    ax, ay = h.GetXaxis(), h.GetYaxis()
    return (h.GetNbinsX(), ax.GetXmin(), ax.GetXmax(), h.GetNbinsY(), ay.GetXmin(), ay.GetXmax())


def cov_hist(ROOT, name, title, m, layout):
    nx, x0, x1, ny, y0, y1 = layout
    if m.shape != (nx, ny):
        raise Stop(f"{name}: matrix {m.shape} does not fit layout {layout}")
    h = ROOT.TH2D(name, title, nx, x0, x1, ny, y0, y1)
    h.SetDirectory(0)
    for i in range(nx):
        for j in range(ny):
            h.SetBinContent(i + 1, j + 1, float(m[i, j]))
    return h


# ------------------------------------------------------------------------------------------------------------ metrics
def metrics(C, x, F):
    """Per-cell relative sigma (build_repair.py summary()) and the 31 functionals (combine_s5.py summary()).

    Relative sigma is sigma / x in percent, x = E_U on the reported cells. The integral sigma is
    sqrt(F0 C F0) / |F0 . x| with F0 = S5's area row (the note's width-weighted total sigma); the 14 pT and
    16 p_par projections are rows 1-14 and 15-30 of S5's F.
    """
    r = np.sqrt(np.maximum(np.diag(C), 0)) / x
    fs = np.sqrt(np.maximum(np.diag(F @ C @ F.T), 0)) / np.abs(F @ x)
    return {"median_pct": float(100 * np.median(r)), "p84_pct": float(100 * np.percentile(r, 84)),
            "min_pct": float(100 * r.min()), "max_pct": float(100 * r.max()),
            "integral_sigma_pct": float(100 * fs[0]),
            "pt_sigma_pct": [float(v) for v in 100 * fs[1:15]],
            "pz_sigma_pct": [float(v) for v in 100 * fs[15:31]],
            "sqrt_trace": float(np.sqrt(np.trace(C)))}


def median_pct(C, x):
    return float(100 * np.median(np.sqrt(np.maximum(np.diag(C), 0)) / x))


def rank_cond(C):
    ev = np.linalg.eigvalsh(0.5 * (C + C.T))
    out = {"lambda_max": float(ev.max()), "lambda_min_over_max": float(ev.min() / ev.max())}
    for t in RANK_TOLS:
        keep = ev > t * ev.max()
        out[f"rank_{t:.0e}"] = int(keep.sum())
        out[f"cond_{t:.0e}"] = float(ev.max() / ev[keep].min())
    return out


def symmetric_psd(name, C):
    check(f"A5_symmetric_{name}", np.max(np.abs(C - C.T)) <= TOL_ID * np.max(np.abs(C)),
          float(np.max(np.abs(C - C.T)) / np.max(np.abs(C))))
    ev = np.linalg.eigvalsh(0.5 * (C + C.T))
    check(f"A5_psd_{name}", ev.min() >= -PSD_TOL * ev.max(), float(ev.min() / ev.max()))


def json_at(d, path):
    for k in path:
        if not isinstance(d, dict) or k not in d:
            raise Stop(f"s5.json has no field {path}")
        d = d[k]
    return d


# --------------------------------------------------------------------------------------------------------------- main
def parse_args(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", required=True,
                    help="the deployed archive; every imported module must resolve under it")
    for k in PINS:
        ap.add_argument("--" + k.replace("_", "-"), dest=k, required=True, help=INPUT_HELP[k])
    ap.add_argument("--outdir", required=True, help="output directory; must not exist (its parent must)")
    ap.add_argument("--arm", choices=("purity", "refined"), default="purity")
    ap.add_argument("--pins-json", help="refined arm: the recorded digests of the six upstream products")
    ap.add_argument("--eu-control", help="refined arm: E_U, the VL175 controls' denominator only")
    a = ap.parse_args(argv)
    if a.arm == "refined" and not (a.pins_json and a.eu_control):
        ap.error("--arm refined needs --pins-json and --eu-control")
    return a


def run(a):
    repo = os.path.realpath(a.repo)
    outdir = os.path.abspath(a.outdir)
    if os.path.lexists(outdir):
        raise Stop(f"--outdir {outdir} already exists")
    if not os.path.isdir(os.path.dirname(outdir)):
        raise Stop(f"parent of --outdir {outdir} does not exist")

    refined = a.arm == "refined"
    if refined:   # chain of custody: the previous steps' recorded digests; E_R is the central value
        chain = json.load(open(a.pins_json))
        if set(chain) != set(CHAIN):
            raise Stop(f"--pins-json keys {sorted(chain)} != {sorted(CHAIN)}")
        PINS.update(chain)
        PINS["eu"] = E_R_SHA
    # ---- A0: every input digest equals its pin (before anything is written)
    inputs = {}
    for k, want in PINS.items():
        p = getattr(a, k)
        if not os.path.isfile(p):
            raise Stop(f"A0 input {k}: {p} is not a file")
        got = sha256(p)
        inputs[k] = {"path": os.path.abspath(p), "realpath": os.path.realpath(p), "sha256": got}
        check(f"A0_pin_{k}", got == want, got)
    if refined:
        got = sha256(a.eu_control)
        inputs["eu_control"] = {"path": os.path.abspath(a.eu_control), "realpath": os.path.realpath(a.eu_control),
                                "sha256": got}
        check("A0_pin_eu_control", got == E_U_SHA, got)

    os.mkdir(outdir)
    CREATED.append(outdir)
    cache = os.path.join(outdir, "_mplcache")   # matplotlib is imported by the fig6/7 module; keep its cache here
    os.makedirs(cache)
    os.environ["MPLCONFIGDIR"] = cache
    os.environ["XDG_CACHE_HOME"] = cache

    import ROOT
    ROOT.gROOT.SetBatch(True)
    import reported_cells as RC
    import plot_uncertainty_fig6_7_style as F67
    import rederive_flux_muonE_cross as RD
    modules = {}
    for m in (RC, F67, RD, sys.modules["analyze_universes"]):
        p = os.path.realpath(m.__file__)
        check(f"A0_module_{m.__name__}_under_repo", p.startswith(repo + os.sep), p)
        modules[m.__name__] = {"path": p, "sha256": sha256(p)}
    category_for_band, CATEGORY_ORDER = F67.category_for_band, list(F67.CATEGORY_ORDER)

    # ---- inputs
    S = dict(np.load(a.s5_npz))
    P = dict(np.load(a.playlist_npz))
    QZ = dict(np.load(a.q_npz))
    s5j = json.load(open(a.s5_json))
    comb = json.load(open(a.combination_json))
    check("s5_json_S5_PASS", s5j.get("S5") == "PASS", s5j.get("S5"))
    check("combination_json_checks_passed", comb.get("checks_passed") is True, comb.get("checks_passed"))
    if refined:   # CB-G: every input was written by the refined arm
        arms = {"s5_npz": str(S.pop("arm", "")), "playlist_npz": str(P.pop("arm", "")), "q_npz": str(QZ.pop("arm", "")),
                "s5_json": s5j.get("arm"), "combination_json": comb.get("arm")}
        check("arm_refined_on_every_input", all(v == "refined" for v in arms.values()), arms)

    fe = open_root(ROOT, a.eu)
    heu = get(fe, "hXSec2D")
    EU2 = RC.grid_hist_to_array(heu)       # the refined arm: E_R
    area2 = np.array([[heu.GetXaxis().GetBinWidth(ix + 1) * heu.GetYaxis().GetBinWidth(iy + 1)
                       for iy in range(RC.GRID_SHAPE[1])] for ix in range(RC.GRID_SHAPE[0])])
    fe.Close()
    fc = open_root(ROOT, a.ec)
    EC2 = RC.grid_hist_to_array(get(fc, "hXSec2D"))
    fc.Close()

    fs5 = open_root(ROOT, a.s5_root)
    s5_cells, s5_cells_src = RC.read_cells(fs5)
    if s5_cells is None or s5_cells_src != RC.IDENTITY_HIST:
        raise Stop(f"A1 S5 ROOT carries no {RC.IDENTITY_HIST}")
    hcomb = get(fs5, "hCov_combined")
    layout = bin_layout(hcomb)
    root_comb = sq(hcomb)
    root_univ = sq(get(fs5, "hCov_universe_total"))
    root_bands = {}
    for k in fs5.GetListOfKeys():
        nm = k.GetName()
        if nm.startswith("hCov_universe_") and nm != "hCov_universe_total":
            root_bands[nm[len("hCov_universe_"):]] = sq(get(fs5, nm))
    fs5.Close()

    fp = open_root(ROOT, a.paper_anc)
    paper = {nm: RD.m2np(get(fp, nm)) for nm in ("TotalCovariance", "StatOnlyCovariance", "FluxCovariance",
                                                  "MuonEnergyScaleCovariance")}
    fp.Close()

    # ---- A1: cell sets
    cells = RC.reported_indices(EU2 > 0)
    check("A1_E_U_nonzero_205", cells.size == N_CELLS_REPORTED, int(cells.size))
    RC.require_same_cells(s5_cells, cells, f"S5 ROOT {RC.IDENTITY_HIST}", "E_U > 0")
    check("A1_S5_ROOT_hReportedCells_eq_E_U_nonzero", True)
    RC.require_same_cells(np.asarray(P["cells"], dtype=np.int64), cells, "playlist cells", "E_U > 0")
    check("A1_playlist_cells_eq_E_U_nonzero", True)
    paper_stat_cells = np.flatnonzero(np.diag(paper["StatOnlyCovariance"]) > 0)
    RC.require_same_cells(paper_stat_cells, cells, "paper StatOnly diag > 0", "E_U > 0")
    check("A1_paper_StatOnly_positive_diag_eq_E_U_nonzero", True)

    # ---- A1': value-anchored order
    eu_flat = EU2.ravel(order="C")
    x = eu_flat[cells]
    x_ctrl = x                             # the VL175 controls' denominator: E_U in both arms (BQ-22/BQ-24)
    if refined:
        fu = open_root(ROOT, a.eu_control)
        EUc = RC.grid_hist_to_array(get(fu, "hXSec2D"))
        fu.Close()
        RC.require_same_cells(RC.reported_indices(EUc > 0), cells, "E_U > 0", "E_R > 0")
        check("A1_E_R_cells_eq_E_U_cells", True)
        x_ctrl = EUc.ravel(order="C")[cells]
    check("A1p_playlist_cells_strictly_ascending", bool(np.all(np.diff(np.asarray(P["cells"], dtype=np.int64)) > 0)))
    check("A1p_s5_npz_cells_x_EU_eq_E_U_cells_exact", np.array_equal(S["cells_x_EU"], x))
    check("A1p_q_npz_cells_x_EU_eq_E_U_cells_exact", np.array_equal(QZ["cells_x_EU"], x))
    check("A1p_playlist_x_eq_E_U_playlist_cells_exact",
          np.array_equal(P["x"], eu_flat[np.asarray(P["cells"], dtype=np.int64)]))
    F = S["functionals"]
    check("A1p_s5_area_eq_E_U_bin_area_exact", np.array_equal(S["area"], area2.ravel(order="C")[cells]))
    check("A1p_s5_F0_eq_area_exact", np.array_equal(F[0], S["area"]))
    check("A1p_q_npz_functionals_area_eq_s5_exact",
          np.array_equal(QZ["functionals"], F) and np.array_equal(QZ["area"], S["area"]))
    check("A1p_playlist_F_eq_s5_functionals_exact", np.array_equal(P["F"], F))

    # ---- A2: storage
    bands_npz = {k[len("band_"):]: v for k, v in S.items() if k.startswith("band_")}
    check("A2_band_sets_equal_44", set(bands_npz) == set(root_bands) and len(bands_npz) == 44
          and NORM_BAND in bands_npz, [len(bands_npz), len(root_bands)])
    band_order = sorted(b for b in bands_npz if b != NORM_BAND) + [NORM_BAND]   # s5_rollup.py accumulation order
    check("A2_root_hCov_combined_eq_npz_total", relmax(root_comb, S["total"]) <= TOL_ID,
          relmax(root_comb, S["total"]))
    check("A2_root_hCov_universe_total_eq_npz_universe", relmax(root_univ, S["universe"]) <= TOL_ID,
          relmax(root_univ, S["universe"]))
    worst = max(float(np.max(np.abs(root_bands[b] - bands_npz[b]))) / float(np.max(np.abs(bands_npz[b])))
                for b in band_order)
    check("A2_root_each_band_eq_npz_band_worst", worst <= TOL_ID, worst)
    bsum = np.zeros_like(S["universe"])
    for b in band_order:
        bsum += bands_npz[b]
    check("A2_band_sum_eq_universe", relmax(bsum, S["universe"]) <= TOL_ID, relmax(bsum, S["universe"]))
    check("A2_s5_total_eq_universe_stat_c08", relmax(S["universe"] + S["stat"] + S["c08"], S["total"]) <= TOL_ID,
          relmax(S["universe"] + S["stat"] + S["c08"], S["total"]))

    # ---- A3: the combination
    Q = QZ["total_plus_C_PL"]
    C_PL = P["C_PL"]
    T5 = S["total"]
    check("A3_s5_total_plus_C_PL_eq_Q", relmax(T5 + C_PL, Q) <= TOL_ID, relmax(T5 + C_PL, Q))
    check("A3_q_npz_C_PL_eq_playlist_C_PL_exact", np.array_equal(QZ["C_PL"], C_PL))
    check("A3_q_npz_s5_total_eq_s5_npz_total_exact", np.array_equal(QZ["s5_total"], T5))

    U, ST, C8 = S["universe"], S["stat"], S["c08"]
    UPS = U + ST
    mats = {"Q": Q, "S5_total": T5, "universe": U, "stat": ST, "c08": C8, "C_PL": C_PL, "universe_plus_stat": UPS}

    # ---- A5: symmetry and PSD, Q and each block
    for nm in ("Q", "S5_total", "universe", "stat", "c08", "C_PL", "universe_plus_stat"):
        symmetric_psd(nm, mats[nm])

    # ================================================================================== controls (SPEC §3), first
    controls = {}

    # (1) VL175 budget.json: the metric functions on VL175's inputs
    bud = json.load(open(a.vl175_budget))["repaired"]
    fr = open_root(ROOT, a.vl175_rollup)
    vb = {}
    for k in fr.GetListOfKeys():
        nm = k.GetName()
        if nm.startswith("hCov_universe_") and nm != "hCov_universe_total":
            vb[nm[len("hCov_universe_"):]] = sq(get(fr, nm))
    v_tot, v_comb = sq(get(fr, "hCov_universe_total")), sq(get(fr, "hCov_combined"))
    fr.Close()
    fb = open_root(ROOT, a.vl175_boot)
    v_boot = sq(get(fb, "hCov2D_reported"))
    boot_cells, boot_src = RC.read_cells(fb, mean_fallback="hMean2D")
    fb.Close()
    RC.require_same_cells(boot_cells, cells, f"VL170 boot ({boot_src})", "E_U > 0")
    fm = open_root(ROOT, a.vl175_ml)
    v_ml = sq(get(fm, "hCov2D_reported"))
    fm.Close()
    vz = np.load(a.vl175_blocks)
    check("control_vl175_blocks_npz_eq_rollup_and_ml_exact",
          np.array_equal(vz["universe_plus_boot"], v_comb) and np.array_equal(vz["ml"], v_ml))
    VL175 = vz["universe_plus_boot"] + vz["ml"]
    vl_rows = {**{f"per_band/{b}": m for b, m in vb.items()}, "universe_plus_norm": v_tot, "boot": v_boot,
               "ml": v_ml, "universe_plus_boot": v_comb, "block_sum": v_comb + v_ml}
    check("control_budget_json_row_set", set(bud["per_band"]) == set(vb), [len(bud["per_band"]), len(vb)])
    fields = ("median_pct", "p84_pct", "min_pct", "max_pct", "integral_sigma_pct", "sqrt_trace")
    worst, worst_at = 0.0, None
    for row, C in vl_rows.items():
        mine = metrics(C, x_ctrl, F)
        ref = bud["per_band"][row.split("/", 1)[1]] if row.startswith("per_band/") else bud[row]
        for fld in fields:
            r = rel(mine[fld], ref[fld])
            if r > worst or worst_at is None:
                worst, worst_at = r, f"{row}.{fld}"
    controls["vl175_budget_json"] = {"rows": len(vl_rows), "fields": list(fields), "worst_rel": worst,
                                     "worst_at": worst_at, "tolerance": TOL_CONTROL}
    check("control_vl175_budget_json_all_rows_le_1e-12", worst <= TOL_CONTROL, {"worst_rel": worst, "at": worst_at})

    # (2) group_medians.json (repaired): the fig6/7 band-to-category map on VL175's inputs
    gm = json.load(open(a.vl175_group_medians))["repaired"]
    stat_roll = v_comb - v_tot
    g = {c: np.zeros_like(v_tot) for c in CATEGORY_ORDER}
    for b, C in vb.items():
        g[category_for_band(b)] += C
    g["Statistical"] = g["Statistical"] + stat_roll
    gmine = {f"grouped_current/{c}": median_pct(C, x_ctrl) for c, C in g.items()}
    gmine.update({"statistical_vl170_boot300": median_pct(v_boot, x_ctrl),
                  "statistical_rollup_bootstrap": median_pct(stat_roll, x_ctrl),
                  "statistical_rollup_eq_vl170_max_abs_rel":
                      float(np.max(np.abs(stat_roll - v_boot)) / np.max(np.abs(v_boot))),
                  "universe_total": median_pct(v_tot, x_ctrl), "combined": median_pct(v_comb, x_ctrl),
                  "band_sum_eq_total_max_abs_rel": float(np.max(np.abs(sum(vb.values()) - v_tot)) / np.max(np.abs(v_tot)))})
    gmine.update({f"bands/{b}": median_pct(vb["full_" + b], x_ctrl) for b in gm["bands"]})
    check("control_group_medians_n_bands", gm["n_bands"] == len(vb), [gm["n_bands"], len(vb)])
    check("control_group_medians_category_set", set(gm["grouped_current"]) == set(CATEGORY_ORDER),
          sorted(gm["grouped_current"]))
    worst, worst_at = 0.0, None
    for key, v in gmine.items():
        ref = gm[key.split("/")[0]][key.split("/")[1]] if "/" in key else gm[key]
        r = rel(v, ref)
        if r > worst or worst_at is None:
            worst, worst_at = r, key
    controls["group_medians_json"] = {"fields": len(gmine), "worst_rel": worst, "worst_at": worst_at,
                                      "tolerance": TOL_CONTROL,
                                      "not_reproduced": "grouped_legacy (group_medians.py's own legacy map, not the "
                                                        "fig6/7 map); the 'adopted' (VL172) section (its input is not "
                                                        "pinned in SPEC §1)"}
    check("control_group_medians_json_le_1e-12", worst <= TOL_CONTROL, {"worst_rel": worst, "at": worst_at})

    # (3) combination.json: the Q, S5 and C_PL rows (and VL175's), budget and projections
    cb = comb["report"]["budget"]
    crow = {"VL175": VL175, "S5_universe": U, "S5_stat": ST, "S5_c08": C8, "S5_total": T5, "C_PL": C_PL,
            "S5_total_plus_C_PL": Q}
    check("control_combination_row_set", set(cb) == set(crow), sorted(cb))
    sv = np.sqrt(np.diag(VL175))
    worst, worst_at, round_bad = 0.0, None, []
    for row, C in crow.items():
        mine = metrics(C, x, F)
        ref = cb[row]
        pairs = {"median": (mine["median_pct"], ref["cell_rel_sigma_pct"]["median"]),
                 "p84": (mine["p84_pct"], ref["cell_rel_sigma_pct"]["p84"]),
                 "max": (mine["max_pct"], ref["cell_rel_sigma_pct"]["max"]),
                 "integral": (mine["integral_sigma_pct"], ref["integral_rel_sigma_pct"]),
                 "ratio_to_VL175": (float(np.median(np.sqrt(np.maximum(np.diag(C), 0)) / sv)),
                                    ref["median_cell_sigma_ratio_to_VL175"])}
        for fld, (m_, r_) in pairs.items():
            r = rel(m_, r_)
            if r > worst or worst_at is None:
                worst, worst_at = r, f"{row}.{fld}"
        for ax, key in (("pt", "pt_rel_sigma_pct"), ("pz", "pz_rel_sigma_pct")):
            got = np.round(np.array(mine[f"{ax}_sigma_pct"]), 4).tolist()
            if got != ref[key]:
                round_bad.append({"row": row, "axis": ax, "mine_rounded": got, "committed": ref[key]})
    eff = comb["report"]["effect_of_C_PL_on_S5"]
    share_cell = float(np.median(np.diag(C_PL) / np.diag(Q)))
    share_int = float((F[0] @ C_PL @ F[0]) / (F[0] @ Q @ F[0]))
    for fld, (m_, r_) in {"share_cell": (share_cell, eff["block_share_of_cell_variance_median"]),
                          "share_integral": (share_int, eff["block_share_of_integral_variance"])}.items():
        r = rel(m_, r_)
        if r > worst:
            worst, worst_at = r, f"effect_of_C_PL_on_S5.{fld}"
    controls["combination_json"] = {"rows": sorted(crow), "worst_rel_full_precision": worst, "worst_at": worst_at,
                                    "tolerance": TOL_CONTROL,
                                    "projections": "pt/pz stored rounded to 4 decimals; mine rounded to 4 must be "
                                                   "equal (director clarification 2026-10-18)",
                                    "projection_mismatches": round_bad}
    check("control_combination_json_full_precision_le_1e-12", worst <= TOL_CONTROL,
          {"worst_rel": worst, "at": worst_at})
    check("control_combination_json_projections_equal_at_4_decimals", not round_bad, round_bad[:2])
    rk_ref = comb["report"]["ranks_rcond_1e-10"]
    rk_mine = {"S5_total": rank_cond(T5)["rank_1e-10"], "combined": rank_cond(Q)["rank_1e-10"]}
    check("control_combination_json_ranks_1e-10", rk_mine == rk_ref, rk_mine)

    # (4) consistency: s5.json's own block summaries and ranks (s5_rollup.py, BR.summary, PSD_TOL rank)
    worst, worst_at = 0.0, None
    rk_bad = {}
    for nm, C in (("universe", U), ("stat", ST), ("c08", C8), ("total", T5)):
        mine = metrics(C, x, F)
        ref = s5j["numbers"][f"{nm}_summary"]
        for fld in fields:
            r = rel(mine[fld], ref[fld])
            if r > worst or worst_at is None:
                worst, worst_at = r, f"{nm}.{fld}"
        rr = rank_cond(C)["rank_1e-10"]
        if rr != s5j["numbers"][f"{nm}_rank"]:
            rk_bad[nm] = [rr, s5j["numbers"][f"{nm}_rank"]]
    controls["s5_json_summaries"] = {"worst_rel": worst, "worst_at": worst_at, "tolerance": TOL_CONTROL}
    check("control_s5_json_block_summaries_le_1e-12", worst <= TOL_CONTROL, {"worst_rel": worst, "at": worst_at})
    check("control_s5_json_block_ranks_1e-10", not rk_bad, rk_bad)

    # (5) rhoFluxMuon: rederive_flux_muonE_cross.py route A (paper ancillary only), on the paper's own cell set
    rep = np.diag(paper["StatOnlyCovariance"]) > 0
    idx = np.where(rep)[0]
    Tp, Sp, Fp, Ep = (paper[k][np.ix_(idx, idx)] for k in ("TotalCovariance", "StatOnlyCovariance", "FluxCovariance",
                                                          "MuonEnergyScaleCovariance"))
    we, le = np.linalg.eigh(Ep)
    e_hat = le[:, -1]
    e_hat *= np.sign(e_hat[np.argmax(np.abs(e_hat))])
    df_paper, _ = RD.lead_mode(Fp)
    f_hat = df_paper / np.linalg.norm(df_paper)
    rho_cs = float((f_hat @ Tp @ e_hat) / np.sqrt((f_hat @ Tp @ f_hat) * (e_hat @ Tp @ e_hat)))
    rho = min(rho_cs, 1.0)
    check("control_rhoFluxMuon_reproduces_vl175_0.900", f"{rho:.3f}" == RHO_PRINTED, rho)

    # ===================================================================================================== numbers
    budget = {"what": "SPEC §3 (stageF/rebuild/SPEC.md). Relative sigma = sigma / E_U on the 205 reported cells, in "
                      "percent. integral_sigma_pct = sqrt(F0 C F0) / |F0 . E_U| with F0 = S5's area row (also the "
                      "note's width-weighted total sigma); pt_sigma_pct / pz_sigma_pct = S5's functionals rows 1-14 "
                      "and 15-30, full precision.",
              "x": "E_U hXSec2D on cells = flatnonzero(E_U > 0) (global id pt*16 + pz)"}
    for nm in ("Q", "S5_total", "universe", "stat", "c08", "C_PL", "universe_plus_stat"):
        budget[nm] = metrics(mats[nm], x, F)
    budget["bands"] = {b: metrics(bands_npz[b], x, F) for b in band_order}

    x_ec = EC2.ravel(order="C")[cells]
    check("E_C_positive_on_the_205_cells", bool(np.all(x_ec > 0)), int(np.sum(x_ec <= 0)))
    for nm in ("Q", "S5_total", "universe_plus_stat"):
        budget[f"{nm}_vs_EC"] = {"median_pct": median_pct(mats[nm], x_ec),
                                 "denominator": "E_C hXSec2D (exact-split) on the same 205 cells"}

    groups = {c: np.zeros_like(Q) for c in CATEGORY_ORDER}
    for b in band_order:
        groups[category_for_band(b)] += bands_npz[b]
    groups["Statistical"] = groups["Statistical"] + ST
    for gname, src in EXTRA_GROUPS.items():
        groups[gname] = mats[src].copy()
    gsum = sum(groups.values())
    check("groups_sum_eq_Q", relmax(gsum, Q) <= TOL_ID, relmax(gsum, Q))
    budget["groups"] = {
        "map": "plot_uncertainty_fig6_7_style.category_for_band (analyze_universes); Statistical = stat block; "
               "'Training seed' = c08; 'Run period' = C_PL (labels provisional, SPEC §4)",
        "members": {c: [b for b in band_order if category_for_band(b) == c] for c in CATEGORY_ORDER},
        "median_pct": {c: median_pct(C, x) for c, C in groups.items()},
        "metrics": {c: metrics(C, x, F) for c, C in groups.items()}}

    fq = F[0] @ Q @ F[0]
    budget["block_shares"] = {
        "what": "per-cell variance share median = median(diag(B) / diag(Q)); integral share = F0 B F0 / F0 Q F0",
        **{nm: {"cell_variance_share_median": float(np.median(np.diag(mats[nm]) / np.diag(Q))),
                "integral_variance_share": float((F[0] @ mats[nm] @ F[0]) / fq)}
           for nm in ("universe", "stat", "c08", "C_PL")}}

    budget["ranks"] = {
        "what": "eigenvalues of (C + C^T)/2; rank = #{lambda > t lambda_max}; cond = lambda_max / smallest retained "
                "lambda; t = 1e-10 (s5_rollup.py PSD_TOL) and 1e-12 (the note's convention)",
        **{nm: rank_cond(mats[nm]) for nm in ("universe", "universe_plus_stat", "S5_total", "Q")}}

    Tc = paper["TotalCovariance"][np.ix_(cells, cells)]
    Sc = paper["StatOnlyCovariance"][np.ix_(cells, cells)]
    st_tr, so_tr = float(np.sqrt(np.trace(ST))), float(np.sqrt(np.trace(Sc)))
    q_tr, tot_tr = float(np.sqrt(np.trace(Q))), float(np.sqrt(np.trace(Tc)))
    budget["paper_ratios"] = {
        "paper_sqrt_trace_TotalCovariance_205": tot_tr, "paper_sqrt_trace_StatOnly_205": so_tr,
        "sqrt_trace_stat_over_sqrt_trace_StatOnly": st_tr / so_tr,
        "sqrt_trace_Q_over_sqrt_trace_TotalCovariance": q_tr / tot_tr,
        "median_sigma_stat_over_sigma_StatOnly": float(np.median(np.sqrt(np.diag(ST)) / np.sqrt(np.diag(Sc))))}

    budget["flux"] = {
        "band_Flux_median_pct": budget["bands"]["Flux"]["median_pct"],
        "band_Flux_integral_sigma_pct": budget["bands"]["Flux"]["integral_sigma_pct"],
        "leading_mode_variance_share": None,
        "leading_mode_variance_share_status": "NOT COMPUTED: no committed producer of the note's 99.6 % was found "
                                              "(README.md); SPEC §3 asks for it, the work order says implement "
                                              "nothing without a producer",
        "rhoFluxMuon": {"value": rho, "rho_cs_unclipped": rho_cs, "printed": f"{rho:.3f}",
                        "producer": "transcribed from 2d-unfolding/uq/rederive_flux_muonE_cross.py main() L76-90, route A (rho = min(rho_cs, 1)): "
                                    "Cauchy-Schwarz correlation of the paper flux leading mode and the paper "
                                    "muon-energy-scale mode inside the paper TotalCovariance",
                        "inputs": "the paper ancillary only; Q, S5 and every block of ours do not enter, so this "
                                  "value is the VL175 value by construction",
                        "vl175_control": RHO_PRINTED}}

    def copied(path):
        return {"field": path, "value": json_at(s5j, path)}
    po = s5j["inputs"]["production_outputs"]
    budget["s5_copied"] = {
        "source": {"path": inputs["s5_json"]["path"], "sha256": inputs["s5_json"]["sha256"]},
        "stat_centring_offset": copied(["numbers", "centring", "stat"]),
        "mat_agreement": copied(["checks", "mat_universe_block_le_1e-12"]),
        "ensemble": {
            "bands": copied(["checks", "universe_bands_43_plus_norm"]),
            "universes": copied(["checks", "refined_j2_38_bands_175_universes" if refined
                                 else "july_44_bands_187_universes"]),
            "stat_rel_se_of_sigma": copied(["numbers", "stat", "ensemble_rel_se_of_sigma"]),
            "c08_dof": copied(["numbers", "c08", "dof"]),
            "c08_rank": copied(["numbers", "c08", "rank"]),
            "x02_dof": copied(["numbers", "x02", "dof"])},
        "derived_counts_not_copied": {
            "what": "counted here from the keys of inputs.production_outputs; not a field of s5.json",
            "stat_replicas_S1": sum(bool(re.fullmatch(r"2dc_P_S1_\d{3}", k)) for k in po),
            "seed_triplets_S4B_seeds_plus_seed42": len({re.fullmatch(r"2dc_P_S4B_s(\d+)_\d+", k).group(1)
                                                        for k in po if re.fullmatch(r"2dc_P_S4B_s(\d+)_\d+", k)}) + 1,
            "bands_in_npz": len(bands_npz)}}

    # ================================================================================================ products
    title = {"Q": "Q = S5 total + C_PL (adopted), reported bins", "S5total": "S5 total = universe + stat + c08",
             "universe_total": "S5 universe block (43 bands + normalization)", "stat": "S5 statistical block",
             "c08": "S5 training-seed block (C08)", "playlist": "playlist-consistency block C_PL",
             "universe_plus_stat": "S5 universe + stat"}
    adopted = [("hCov_Q", title["Q"], Q), ("hCov_S5total", title["S5total"], T5),
               ("hCov_universe_total", title["universe_total"], U)]
    adopted += [(f"hCov_universe_{b}", f"S5 universe covariance ({b})", bands_npz[b]) for b in band_order]
    adopted += [("hCov_stat", title["stat"], ST), ("hCov_c08", title["c08"], C8),
                ("hCov_playlist", title["playlist"], C_PL),
                ("hCov_sum_universe_stat", title["universe_plus_stat"], UPS)]

    def write_root(path, hists, extra=()):
        f = ROOT.TFile.Open(path, "RECREATE")
        if not f or f.IsZombie():
            raise Stop(f"cannot create {path}")
        for nm, tt, m in hists:
            cov_hist(ROOT, nm, tt, m, layout).Write()
        for h in extra:
            h.Write()
        cells_h = RC.identity_hist(cells)
        cells_h.Write()
        f.Close()

    def readback(path, hists, rel2d=None):
        f = open_root(ROOT, path)
        ok = all(bin_layout(get(f, nm)) == layout and np.array_equal(sq(get(f, nm)), m) for nm, _, m in hists)
        rc, src = RC.read_cells(f)
        ok = ok and src == RC.IDENTITY_HIST and np.array_equal(rc, cells)
        if rel2d is not None:
            ok = ok and np.array_equal(RC.grid_hist_to_array(get(f, "hRel2D")), rel2d)
        keys = sorted(k.GetName() for k in f.GetListOfKeys())
        f.Close()
        want = sorted([nm for nm, _, _ in hists] + [RC.IDENTITY_HIST] + (["hRel2D"] if rel2d is not None else []))
        check(f"A4_readback_{os.path.basename(path)}", ok and keys == want, {"objects": len(keys)})

    p_adopted = os.path.join(outdir, "uq_adopted_covariance.root")
    write_root(p_adopted, adopted)
    readback(p_adopted, adopted)

    rel_flat = np.zeros(RC.N_CELLS)
    rel_flat[cells] = np.sqrt(np.maximum(np.diag(ST), 0)) / x
    rel2d = rel_flat.reshape(RC.GRID_SHAPE, order="C")
    h_rel = ROOT.TH2D("hRel2D", f"sqrt(diag stat) / {'E_R' if refined else 'E_U'} on the pT x p_par grid (fraction; "
                      "0 off the reported cells)",
                      RC.GRID_SHAPE[0], RC.PT_EDGES, RC.GRID_SHAPE[1], RC.PZ_EDGES)
    h_rel.SetDirectory(0)
    for ix in range(RC.GRID_SHAPE[0]):
        for iy in range(RC.GRID_SHAPE[1]):
            h_rel.SetBinContent(ix + 1, iy + 1, float(rel2d[ix, iy]))
    for fn, C, tt, extra in (("block_stat.root", ST, title["stat"], (h_rel,)),
                             ("block_c08.root", C8, title["c08"], ()),
                             ("block_playlist.root", C_PL, title["playlist"], ())):
        hs = [("hCov2D_reported", tt + ", reported bins", C)]
        p = os.path.join(outdir, fn)
        write_root(p, hs, extra)
        readback(p, hs, rel2d if extra else None)

    p_npz = os.path.join(outdir, "cov2d_Q_205.npz")
    arrays = {"Q": Q, "s5_total": T5, "universe": U, "stat": ST, "c08": C8, "C_PL": C_PL,
              "cells": cells.astype(np.int64), "x": x}
    np.savez(p_npz, **arrays)
    back = np.load(p_npz)
    check("A4_readback_cov2d_Q_205.npz", sorted(back.files) == sorted(arrays)
          and all(np.array_equal(back[k], v) for k, v in arrays.items()))
    json.dump({"what": "the adopted Q and its blocks on the 205 reported cells (SPEC §2 item 3)",
               "cells": "flatnonzero(E_U hXSec2D > 0) in C order over (pT, p_par): global id = pt*16 + pz",
               "x": "E_R hXSec2D on cells" if refined else "E_U hXSec2D on cells",
               "arrays": {k: {"shape": list(v.shape), "dtype": str(v.dtype),
                              **({"sqrt_trace": float(np.sqrt(np.trace(v)))} if v.ndim == 2 else {})}
                          for k, v in arrays.items()},
               "sources": {"Q": "s5_plus_playlist.npz total_plus_C_PL", "s5_total": "production_cov.npz total",
                           "universe": "production_cov.npz universe", "stat": "production_cov.npz stat",
                           "c08": "production_cov.npz c08", "C_PL": "playlist_term.npz C_PL"},
               "inputs": {k: inputs[k] for k in ("q_npz", "s5_npz", "playlist_npz", "eu")}},
              open(os.path.join(outdir, "cov2d_Q_205.json"), "w"), indent=1)

    shutil.rmtree(cache)
    budget["checks"] = CHECKS
    budget["controls"] = controls
    budget["provenance"] = {"script": {"path": os.path.realpath(__file__), "sha256": sha256(__file__)},
                            "argv": sys.argv, "sys_path": list(sys.path), "python": sys.version,
                            "numpy": np.__version__, "root": ROOT.gROOT.GetVersion(), "modules": modules,
                            "inputs": inputs}
    if refined:
        budget["arm"] = "refined"
        budget["x"] = "E_R hXSec2D on cells = flatnonzero(E_R > 0), equal to E_U's (global id pt*16 + pz)"
        budget["what"] = budget["what"].replace("sigma / E_U", "sigma / E_R").replace("|F0 . E_U|", "|F0 . E_R|")
        budget["controls_denominator"] = "the VL175 budget.json and group_medians.json controls use E_U (--eu-control)"
    budget["ALL_STOPS_AND_CONTROLS_PASSED"] = True
    json.dump(budget, open(os.path.join(outdir, "budget_Q.json"), "w"), indent=1)

    names = sorted(os.listdir(outdir))
    with open(os.path.join(outdir, "SHA256SUMS"), "w") as fh:
        for n in names:
            fh.write(f"{sha256(os.path.join(outdir, n))}  {n}\n")
    for n in names:
        say(f"[wrote] {n}")

    q, s = budget["Q"], budget["S5_total"]
    say(f"[summary] Q median {q['median_pct']:.6f} %  integral {q['integral_sigma_pct']:.6f} %  "
        f"S5 total median {s['median_pct']:.6f} %  integral {s['integral_sigma_pct']:.6f} %")
    say(f"[summary] ranks 1e-10/1e-12: " + ", ".join(
        f"{nm} {budget['ranks'][nm]['rank_1e-10']}/{budget['ranks'][nm]['rank_1e-12']}"
        for nm in ("universe", "universe_plus_stat", "S5_total", "Q")))
    say(f"[summary] Flux band median {budget['flux']['band_Flux_median_pct']:.6f} %  "
        f"rhoFluxMuon {rho:.6f}  leading-mode share NOT COMPUTED (no producer)")
    say(f"build_q_products: ALL {len(CHECKS)} STOPS AND CONTROLS PASSED; outdir {outdir}")


def main(argv=None):
    a = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        run(a)
    except Exception as e:
        msg = f"[STOP] {type(e).__name__}: {e}"
        print(msg, file=sys.stderr, flush=True)
        if CREATED:
            with open(os.path.join(CREATED[0], "STOPPED.txt"), "w") as fh:
                fh.write("\n".join(LOG + [msg]) + "\n")
        raise SystemExit(2)


if __name__ == "__main__":
    main()
