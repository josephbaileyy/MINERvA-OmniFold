#!/usr/bin/env python3
"""Per-period 2D benchmark: each run-period group of E_R's refined period products against the published result.

The design is DECLARATION.md in this directory. This script implements it and nothing else:
  copy    O_NOATIME copies of the 39 operands in INPUTS.sha256 into a new directory (no hashing in this step)
  verify  sha256 of every copy compared with INPUTS.sha256, in a separate step; writes verify.json
  read    re-hashes the copies, runs the controls of DECLARATION.md section 3, and only if every control passes
          computes the readings R1-R5 of section 4 and their classes of section 5; writes readout.json/.txt

Reused, never re-implemented (DECLARATION.md section 9):
  compare_to_paper_fullcov.py   tmatrix_to_numpy, flatten_th2d, flatten_ours, chi2_with_cov
  coverage/scripts/common.py    proj_matrix, area, STEP_LO, STEP_HI
  period-unfold analyze_periods step_stat
S_K, the eigen-sum over a mode set K, is tied to chi2_with_cov by control C-SUM.

Exit codes: 0 readings written; 3 a control STOPped (STOP.json, no readings); 4 an operand was refused
(digest, missing, environment). 1 is left to Python's own crash exit.
"""
import argparse
import hashlib
import json
import math
import os
import shutil
import sys
import types
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
TD = REPO / "2d-unfolding"
COV_SCRIPTS = REPO / "docs/orchestration/state/2d-closeout/playlist-spread-20261014/coverage/scripts"
PU_SCRIPTS = REPO / "docs/orchestration/state/2d-closeout/period-unfold-20261014/scripts"
PARTC_ANALYSIS = REPO / "docs/orchestration/state/2d-closeout/stageF/methods/re2/run/partc_r2/partc-r2/periods/analysis.json"
INPUTS = HERE / "INPUTS.sha256"

EXIT_STOP, EXIT_REFUSE = 3, 4

# ---------------------------------------------------------------------------------------- declared constants
# Each value is DECLARATION.md's; the comment names its source on main.
PARTC_ANALYSIS_SHA = "2ce5d5dab3e566590504ba0f186a90b0334e7e691dbda011403fc99a8c8d92cd"
STEP_PBPA = 0.10235291689162862          # analysis.json comparisons["raw_PB/PA"].step.value
EXPOSURE = {"PA": 0.533379, "PB": 0.294541, "PC": 0.172079}   # analysis.json exposure_share_by_pt_row, to 6 decimals;
# a CHECK only (C-PARTC). The readings use analysis.json's full-precision shares, which sum to 1 per row.
CHI2_ER = 465.4152721915331              # OUTCOME-20261106-ref-c2c1-read.md:16 (C-PUB, full precision)
K73 = 73                                 # tension_report.txt:56 (rcond 1e-4 keeps 73), fixed by number
RCOND_K = 1e-4
S73_PER205 = 0.662                       # tension_report.txt:56, printed to 3 decimals
SENS_K = (139, 176)                      # tension_report.txt:55, 54
# M: E_R's six largest contributors, eigh rank (0 = smallest) -> (lam/lam_max as printed, |c/sqrt(lam)| as printed)
M_EXPECT = {23: ("3.549e-09", 4.75), 9: ("4.314e-10", 3.78), 118: ("5.613e-05", 3.65),
            2: ("6.590e-11", 3.64), 79: ("4.460e-06", 3.61), 121: ("6.048e-05", 3.50)}
M_RANKS = (23, 9, 118, 2, 79, 121)       # tension_report.txt:18-23, in that order
N_REPLICAS = 10
POS, NULL = 3.0, 2.0                     # positive class |z| >= 3, null class |z| <= 2
TOL = {"C-PUB": 1e-8, "C-SUM": 1e-6, "C-CTRL-cells": 1e-8, "C-CTRL-S73": 1e-6, "C-CTRL-S205": 1e-4,
       "C-STEP": 1e-10, "C-COMB": 5e-3, "C-GRAD": 1e-12, "C-W": 1e-6}
GROUPS = ("PA", "PB", "PC")
PAIRS = (("PB", "PA"), ("PB", "PC"), ("PC", "PA"))


class Refused(Exception):
    """An operand or the environment is not what the declaration binds."""


# ---------------------------------------------------------------------------------------- reused modules
def import_reused():
    """Import the reused modules from THIS repository and prove where each came from.

    analyze_periods.py inserts a cluster path (periods.COVERAGE_SCRIPTS) at sys.path[0] before `import common`
    (analyze_periods.py:46-50), the OI-136 shape. `common` is therefore imported first from the repo, so the cached
    module is the one analyze_periods binds; then every module's file must resolve inside REPO.
    """
    for p in (str(COV_SCRIPTS),):
        if p not in sys.path:
            sys.path.insert(0, p)
    import common  # noqa: E402
    if str(PU_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(PU_SCRIPTS))
    import analyze_periods  # noqa: E402
    import periods  # noqa: E402
    # drop the cluster path analyze_periods inserted, so no later import can resolve through it
    sys.path[:] = [p for p in sys.path if p != periods.COVERAGE_SCRIPTS]
    if str(TD) not in sys.path:
        sys.path.insert(0, str(TD))
    import compare_to_paper_fullcov  # noqa: E402
    import reported_cells  # noqa: E402
    mods = {"common": common, "analyze_periods": analyze_periods, "periods": periods,
            "compare_to_paper_fullcov": compare_to_paper_fullcov, "reported_cells": reported_cells}
    check_provenance(mods, analyze_periods)
    return types.SimpleNamespace(**{k: v for k, v in mods.items()})


def check_provenance(mods, analyze_periods):
    root = os.path.realpath(REPO)
    for name, m in mods.items():
        f = os.path.realpath(getattr(m, "__file__", "") or "")
        if not f.startswith(root + os.sep):
            raise Refused(f"module {name} resolved outside the repo: {f!r}")
    if analyze_periods.C is not mods["common"]:
        raise Refused("analyze_periods bound a different `common` module than the repo's")


# ---------------------------------------------------------------------------------------- digests and copies
def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 22), b""):
            h.update(blk)
    return h.hexdigest()


def read_inputs(path=INPUTS):
    rows = []
    for line in Path(path).read_text().splitlines():
        if line.strip():
            digest, src = line.split(None, 1)
            if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
                raise Refused(f"malformed digest in {path}: {digest!r}")
            rows.append((digest, src.strip()))
    if len(rows) != 39 or len({s for _, s in rows}) != 39:
        raise Refused(f"{path}: expected 39 distinct operands, found {len(rows)}")
    return rows


def copy_name(src):
    """Unique local name: 'pu_PB_b03__xsec.root', 'ER__xsec.root', 'cov_ptpl_minerva_inclusive_6GeV.root'."""
    p = Path(src)
    return p.name if p.name.startswith("cov_ptpl_") else f"{p.parent.name}__{p.name}"


def noatime_copy(src, dst):
    flag = getattr(os, "O_NOATIME", None)
    if flag is None:
        raise Refused("os.O_NOATIME is unavailable on this platform; the copy step runs on the cluster only")
    fd = os.open(src, os.O_RDONLY | flag)
    try:
        with os.fdopen(fd, "rb", closefd=False) as fin, open(dst, "xb") as fout:
            shutil.copyfileobj(fin, fout, 1 << 22)
    finally:
        os.close(fd)


def do_copy(dest):
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=False)
    rows = read_inputs()
    log = []
    for _, src in rows:
        if not os.path.isfile(src):
            raise Refused(f"operand missing: {src} (HPSS retrieval needs its own binding)")
        dst = dest / copy_name(src)
        noatime_copy(src, dst)
        log.append({"src": src, "dst": str(dst)})
    (dest / "copies.json").write_text(json.dumps(log, indent=1) + "\n")
    return log


def verify_copies(dest, rows=None):
    """Compare every copy's sha256 with the declared one. Returns the record; raises Refused on any mismatch."""
    dest = Path(dest)
    rows = rows if rows is not None else read_inputs()
    rec = {"inputs_sha256": sha256(INPUTS), "files": []}
    bad = []
    for want, src in rows:
        dst = dest / copy_name(src)
        got = sha256(dst) if dst.is_file() else None
        rec["files"].append({"src": src, "copy": str(dst), "declared": want, "measured": got, "equal": got == want})
        if got != want:
            bad.append(src)
    rec["verdict"] = "PASS" if not bad else "REFUSE"
    if bad:
        rec["refused"] = bad
    return rec


# ---------------------------------------------------------------------------------------- the algebra
def eig_basis(V):
    """V = sum lam_i u_i u_i^T, ascending (eigh rank 0 = smallest), as diagnose_tension.py:138."""
    lam, U = np.linalg.eigh(V)
    return lam, U


def top_modes(lam, k):
    """Indices of the k largest-lambda modes."""
    return np.argsort(lam)[::-1][:k]


def complement(n, idx):
    return np.setdiff1d(np.arange(n), idx)


def quad(d, lam, U, idx):
    """S_K(d) = sum_{i in K} (u_i . d)^2 / lambda_i."""
    c = U[:, idx].T @ d
    return float(np.sum(c * c / lam[idx]))


NOISE_MODELS = ("replica", "replica+seed")


def noise_var(fr, f0, fs, model):
    """Unbiased variance of one fit's statistic f under a noise model (DECLARATION.md section 4, revision 3).

    fr: f on the N replicas (training seed 42, resampled data); f0 = f(x), fs = f(x') at seed 43.
      "replica":       var_r(f_r), ddof 1, centred on the replicas' own mean. Unbiased for one fit's variance
                       when the seed's effect re-randomizes with the data (seed noise is inside the replica spread).
      "replica+seed":  the same plus (f(x') - f(x))^2 / 2. x' - x = s_43 - s_42 has variance 2 V_seed for
                       exchangeable seeds, so / 2 is unbiased for V_seed; for when the seed's effect does not
                       re-randomize. (coverage-5b-audit N1: the undivided term over-subtracts.)
    """
    fr = np.asarray(fr, dtype=float)
    v = float(np.var(fr, ddof=1))
    if model == "replica+seed":
        v += (fs - f0) ** 2 / 2.0
    elif model != "replica":
        raise ValueError(model)
    return v


def noise_sigma(f, x0, reps, xs, model):
    return math.sqrt(noise_var([f(r) for r in reps], f(x0), f(xs), model))


def zscore(delta, sigma):
    """delta / sigma; sigma = 0 reads z = 0 when delta = 0 and +-inf otherwise (DECLARATION.md section 5)."""
    if sigma > 0:
        return delta / sigma
    return 0.0 if delta == 0 else math.copysign(math.inf, delta)


def noise_term(g, basis, idx, model):
    """n_K = tr(A_K N) / |K|, N the model's unbiased noise covariance of one fit (noise_var's two models):
    replicas centred on their own mean with ddof 1, plus delta' delta'^T / 2 under "replica+seed"."""
    lam, U = basis
    reps = np.asarray(g["reps"])
    c = reps - reps.mean(axis=0)
    n = sum(quad(r, lam, U, idx) for r in c) / (len(reps) - 1)
    if model == "replica+seed":
        n += quad(g["seed"] - g["x"], lam, U, idx) / 2.0
    elif model != "replica":
        raise ValueError(model)
    return n / len(idx)


def distance(g, p, basis, idx, model):
    """T_K, its noise term n_K, the debiased T~_K and sigma, for one result g = {x, reps, seed}."""
    lam, U = basis
    k = len(idx)
    T = quad(g["x"] - p, lam, U, idx) / k
    out = {"k": k, "T": T}
    if g.get("reps") is None:
        return out
    n = noise_term(g, basis, idx, model)
    out.update({"n": n, "T_debiased": T - n,
                "sigma": noise_sigma(lambda x: quad(x - p, lam, U, idx) / k, g["x"], g["reps"], g["seed"], model)})
    return out


def combine(groups, weights):
    """sum_X w_X g_X for x, every replica index and the seed draw. weights: {X: per-cell vector}."""
    names = list(weights)
    n = {len(groups[X]["reps"]) for X in names}
    if len(n) != 1:
        raise Refused(f"groups have unequal replica counts {sorted(n)}")
    out = {"x": sum(weights[X] * groups[X]["x"] for X in names),
           "seed": sum(weights[X] * groups[X]["seed"] for X in names),
           "reps": [sum(weights[X] * groups[X]["reps"][r] for X in names) for r in range(n.pop())]}
    return out


def exposure_weights(shares_by_row, cells, npz, subset):
    """Per-cell weights from per-p_T-row shares, renormalized over `subset` (ABC: all three; AC: A and C)."""
    ipt = cells // npz
    tot = sum(np.asarray(shares_by_row[X])[ipt] for X in subset)
    return {X: np.asarray(shares_by_row[X])[ipt] / tot for X in subset}


# ---------------------------------------------------------------------------------------- the p_par step
def step_ops(m, cells, p):
    """met for analyze_periods.step_stat, and the range weight vectors w_lo, w_hi with I_range(v) = w_range . v."""
    P = m.common.proj_matrix("pz", cells)
    e = m.common.PZ_A
    w = np.diff(e)
    lo = (e[:-1] >= m.common.STEP_LO[0]) & (e[1:] <= m.common.STEP_LO[1])
    hi = (e[:-1] >= m.common.STEP_HI[0]) & (e[1:] <= m.common.STEP_HI[1])
    met = types.SimpleNamespace(P={"pz": P})
    return met, (w * lo) @ P, (w * hi) @ P


def step_value(m, met, x, p):
    return float(m.analyze_periods.step_stat(x, p, met))


def step_sigma_pub(st, w_lo, w_hi, p, V):
    """Linear propagation of V through st = (I_hi(x)/I_hi(p)) / (I_lo(x)/I_lo(p)) - 1, exact gradient in p."""
    grad = -(1.0 + st) * (w_hi / float(w_hi @ p) - w_lo / float(w_lo @ p))
    return math.sqrt(max(float(grad @ V @ grad), 0.0))


# ---------------------------------------------------------------------------------------- classes (section 5)
def cls_r5(z):
    if z >= POS:
        return "closer without 1G-1M"
    if z <= -POS:
        return "farther without 1G-1M"
    if abs(z) <= NULL:
        return "no change"
    return "unresolved"


def cls_r2(z2):
    """z2: {(g, h): z of T~_g - T~_h}. 'g farther' / 'no group separates' / 'other pattern'."""
    def z(g, h):
        return z2[(g, h)] if (g, h) in z2 else -z2[(h, g)]
    farther = []
    for g in GROUPS:
        o = [h for h in GROUPS if h != g]
        if all(z(g, h) >= POS for h in o) and abs(z(o[0], o[1])) <= NULL:
            farther.append(g)
    if len(farther) == 1:
        return f"{farther[0]} farther"
    if all(abs(v) <= NULL for v in z2.values()):
        return "no group separates"
    return "other pattern"


def cls_r3(deltas, unresolved_by_groups):
    if unresolved_by_groups:
        return "not resolved by the period groups"
    if any(abs(v) >= POS for v in deltas.values()):
        return "group-dependent"
    if all(abs(v) <= NULL for v in deltas.values()):
        return "group-independent at this resolution"
    return "unresolved"


def cls_r4(z):
    if abs(z) <= NULL:
        return "matches the published p_par high/low ratio"
    if abs(z) >= POS:
        return "differs"
    return "unresolved"


SENTENCE_CLOSER = ("In the best-determined directions of the published covariance, the combination of the two "
                   "run-period groups without 1G-1M is closer to the published result than the three-group "
                   "combination.")
CLAUSE_R4_SEPARATES = ("The published p_par high/low ratio matches those two groups and not the group with the step.")
CLAUSE_R4_WIDE = ("At its own uncertainty, the published p_par high/low ratio does not distinguish the groups.")
SENTENCE_NOCHANGE = ("The run-period step does not account for the distance in the best-determined directions, at the "
                     "resolved size.")
R4_MATCH = "matches the published p_par high/low ratio"


def combined_statement(r5_class, r4_classes):
    """DECLARATION.md section 5 (revision 3). R4's clause is conditional: the published covariance gives the step
    ratio sigma_pub of about 4.3% (r4_power_txt.txt), so 'differs' needs |st| >~ 12.8% and may be unreachable."""
    if r5_class == "closer without 1G-1M":
        if r4_classes["PA"] == R4_MATCH and r4_classes["PC"] == R4_MATCH and r4_classes["PB"] == "differs":
            return SENTENCE_CLOSER + " " + CLAUSE_R4_SEPARATES
        if all(r4_classes[g] == R4_MATCH for g in GROUPS):
            return SENTENCE_CLOSER + " " + CLAUSE_R4_WIDE
        return SENTENCE_CLOSER
    if r5_class == "no change":
        return SENTENCE_NOCHANGE
    return None


# ---------------------------------------------------------------------------------------- controls (section 3)
def _ctl(cid, ok, **values):
    return {"id": cid, "verdict": "PASS" if ok else "FAIL", **values}


def rel(a, b):
    return abs(a - b) / abs(b) if b != 0 else (0.0 if a == 0 else math.inf)


def ctl_cells(rc, mask_idx, products):
    """C-IN (cells): each product's positive cells equal the published StatOnly set, index by index.

    E_R's driver stores no reported-cell histogram, so the product side is its own x > 0 set; the comparison is
    reported_cells.require_same_cells, as compare_to_paper_fullcov.py:156 uses it."""
    bad = {}
    for name, x224 in products.items():
        try:
            rc.require_same_cells(mask_idx, np.flatnonzero(x224 > 0), "published StatOnly", name)
        except rc.CellIdentityError as e:
            bad[name] = str(e)
    return _ctl("C-IN-cells", not bad and mask_idx.size == 205, n_published=int(mask_idx.size), mismatches=bad)


def ctl_pub(chi2_er, want=CHI2_ER):
    r = rel(chi2_er, want)
    return _ctl("C-PUB", r <= TOL["C-PUB"], measured=chi2_er, declared=want, rel=r, tol=TOL["C-PUB"])


def ctl_sum(s_all, chi2_er):
    r = rel(s_all, chi2_er)
    return _ctl("C-SUM", r <= TOL["C-SUM"], eigen_sum=s_all, chi2_with_cov=chi2_er, rel=r, tol=TOL["C-SUM"])


def ctl_k(lam, s73, n_cells, want_k=K73, want_per205=S73_PER205):
    k = int(np.sum(lam > RCOND_K * lam.max()))
    per205 = s73 / n_cells
    ok = k == want_k and abs(per205 - want_per205) <= 5e-4
    return _ctl("C-K", ok, k_measured=k, k_declared=want_k, s73_per205=per205, declared=want_per205, half_unit=5e-4)


def ctl_modes(lam, U, d_er, expect=M_EXPECT):
    lam_max = lam.max()
    rows, ok = [], True
    for r, (lam_txt, zabs) in expect.items():
        got_l = lam[r] / lam_max
        want_l = float(lam_txt)
        half = 0.5 * 10 ** (math.floor(math.log10(want_l)) - 3)
        got_z = abs(float(U[:, r] @ d_er) / math.sqrt(lam[r]))
        good = abs(got_l - want_l) <= half * (1 + 1e-9) and abs(got_z - zabs) <= 0.005 * (1 + 1e-9)
        ok &= good
        rows.append({"rank": r, "lam_rel": got_l, "lam_rel_declared": lam_txt, "abs_z": got_z,
                     "abs_z_declared": zabs, "ok": bool(good)})
    return _ctl("C-M", ok, modes=rows)


def ctl_ctrl(x_ctrl, x_er, p, basis, idx73, idx_all):
    lam, U = basis
    cells = float(np.max(np.abs(x_ctrl - x_er) / np.abs(x_er)))
    s73 = rel(quad(x_ctrl - p, lam, U, idx73), quad(x_er - p, lam, U, idx73))
    s205 = rel(quad(x_ctrl - p, lam, U, idx_all), quad(x_er - p, lam, U, idx_all))
    ok = cells <= TOL["C-CTRL-cells"] and s73 <= TOL["C-CTRL-S73"] and s205 <= TOL["C-CTRL-S205"]
    return _ctl("C-CTRL", ok, max_rel_cells=cells, rel_S73=s73, rel_S205=s205,
                tol={k: TOL[k] for k in ("C-CTRL-cells", "C-CTRL-S73", "C-CTRL-S205")})


def ctl_step(step_ba, want=STEP_PBPA):
    r = rel(step_ba, want)
    return _ctl("C-STEP", r <= TOL["C-STEP"], measured=step_ba, declared=want, rel=r, tol=TOL["C-STEP"])


def ctl_grad(m, met, w_lo, w_hi, x, p):
    """My range weights reproduce step_stat on the same operands, so sigma_pub differentiates the right function."""
    mine = (float(w_hi @ x) / float(w_hi @ p)) / (float(w_lo @ x) / float(w_lo @ p)) - 1.0
    theirs = step_value(m, met, x, p)
    d = abs(mine - theirs) / max(abs(theirs), 1e-300) if theirs != 0 else abs(mine)
    return _ctl("C-GRAD", d <= TOL["C-GRAD"], weights_form=mine, step_stat=theirs, rel=d, tol=TOL["C-GRAD"])


def ctl_comb(weights, x_abc, x_ctrl, area):
    wsum = sum(weights.values())
    wdev = float(np.max(np.abs(wsum - 1.0)))
    i_abc, i_ctrl = float(area @ x_abc), float(area @ x_ctrl)
    r = (i_abc - i_ctrl) / i_ctrl
    ok = wdev <= 1e-12 and abs(r) <= TOL["C-COMB"]
    return _ctl("C-COMB", ok, weights_max_dev_from_1=wdev, integral_abc=i_abc, integral_ctrl=i_ctrl, rel=r,
                tol=TOL["C-COMB"])


def ctl_partc(rec, shares_declared=EXPOSURE, step_declared=STEP_PBPA):
    """The two values read from part C's analysis.json equal the declared ones."""
    sh = {X: rec["exposure_share_by_pt_row"][X] for X in GROUPS}
    const = all(len(set(v)) == 1 for v in sh.values())
    dev = max(abs(sh[X][0] - shares_declared[X]) for X in GROUPS)
    rowsum = max(abs(sum(sh[X][r] for X in GROUPS) - 1.0) for r in range(len(sh[GROUPS[0]])))
    st = rec["comparisons"]["raw_PB/PA"]["step"]["value"]
    ok = (const and dev <= TOL["C-W"] and rowsum <= 1e-12 and st == step_declared
          and int(rec["n_boot_pairs"]) == N_REPLICAS)
    return _ctl("C-PARTC", ok, shares_constant_over_rows=const, max_share_dev=dev, max_row_sum_dev=rowsum, step=st,
                n_boot_pairs=int(rec["n_boot_pairs"]))


# ---------------------------------------------------------------------------------------- readings (section 4)
def merge_class(a, b):
    """A class is read only where both noise models give it (DECLARATION.md section 4, revision 3)."""
    return a if a == b else "unresolved (noise model)"


def readings_one(m, groups, x_er, p, V, cells, shares_by_row, model):
    """Every reading of section 4 under one noise model."""
    basis = eig_basis(V)
    lam, U = basis
    n = len(p)
    idx73 = top_modes(lam, K73)
    idxbar = complement(n, idx73)
    idx_all = np.arange(n)
    npz = len(m.common.PZ_A) - 1
    abc = combine(groups, exposure_weights(shares_by_row, cells, npz, GROUPS))
    ac = combine(groups, exposure_weights(shares_by_row, cells, npz, ("PA", "PC")))
    er = {"x": x_er}
    allres = dict(groups, ABC=abc, AC=ac)
    out = {"model": model}

    # R1, printed and read by nothing
    out["R1"] = {name: distance(g, p, basis, idx_all, model) for name, g in dict(allres, E_R=er).items()}

    # R2 and R2-bar
    def r2(idx):
        d = {g: distance(groups[g], p, basis, idx, model) for g in GROUPS}
        z2 = {f"{g}-{h}": zscore(d[g]["T_debiased"] - d[h]["T_debiased"], math.hypot(d[g]["sigma"], d[h]["sigma"]))
              for g, h in PAIRS}
        resolved = {f"{g}-{h}": POS * math.hypot(d[g]["sigma"], d[h]["sigma"]) for g, h in PAIRS}
        return {"per_group": d, "z": z2, "class": cls_r2({(g, h): z2[f"{g}-{h}"] for g, h in PAIRS}),
                "resolved_3sigma": resolved, "E_R": distance(er, p, basis, idx, model)}
    out["R2"], out["R2bar"] = r2(idx73), r2(idxbar)

    # R3, the mode set M, signs fixed so E_R's component is positive
    r3 = {}
    for i in M_RANKS:
        u = U[:, i] * (1.0 if float(U[:, i] @ (x_er - p)) >= 0 else -1.0)
        sl = math.sqrt(lam[i])
        zf = lambda x, u=u, sl=sl: float(u @ (x - p)) / sl  # noqa: E731
        z_all = zf(x_er)
        per = {g: {"z": zf(groups[g]["x"]),
                   "sigma": noise_sigma(zf, groups[g]["x"], groups[g]["reps"], groups[g]["seed"], model)}
               for g in GROUPS}
        dl = {f"{g}-{h}": zscore(per[g]["z"] - per[h]["z"], math.hypot(per[g]["sigma"], per[h]["sigma"]))
              for g, h in PAIRS}
        unres = any(per[g]["sigma"] > abs(z_all) for g in GROUPS)
        r3[str(i)] = {"lam_rel": float(lam[i] / lam.max()), "z_E_R": z_all, "per_group": per, "delta": dl,
                      "printed": {"ABC": zf(abc["x"]), "AC": zf(ac["x"])}, "class": cls_r3(dl, unres)}
    out["R3"] = r3

    # R4, the p_par step against the published ratio
    met, w_lo, w_hi = step_ops(m, cells, p)
    r4 = {}
    for name, g in dict(allres, E_R=er).items():
        st = step_value(m, met, g["x"], p)
        sp = step_sigma_pub(st, w_lo, w_hi, p, V)
        row = {"st": st, "sigma_pub": sp}
        if g.get("reps") is not None:
            sg = noise_sigma(lambda x: step_value(m, met, x, p), g["x"], g["reps"], g["seed"], model)
            row.update({"sigma": sg, "z": zscore(st, math.hypot(sg, sp))})
            if name in GROUPS:
                row["class"] = cls_r4(row["z"])
        r4[name] = row
    r4["pairwise"] = {f"{g}-{h}": zscore(r4[g]["st"] - r4[h]["st"], math.hypot(r4[g]["sigma"], r4[h]["sigma"]))
                      for g, h in PAIRS}
    Pz = met.P["pz"]
    r4["marginal_ratio_printed"] = {g: ((Pz @ groups[g]["x"]) / (Pz @ p) - 1).tolist() for g in GROUPS}
    out["R4"] = r4

    # R5 and R5-bar, the primary connection reading; sigma_5 from the paired difference (ABC and AC share A, C)
    def r5(idx):
        a, c = distance(abc, p, basis, idx, model), distance(ac, p, basis, idx, model)
        k = len(idx)
        f = lambda xa, xc: quad(xa - p, lam, U, idx) / k - quad(xc - p, lam, U, idx) / k  # noqa: E731
        s5 = math.sqrt(noise_var([f(ra, rc) for ra, rc in zip(abc["reps"], ac["reps"])], f(abc["x"], ac["x"]),
                                 f(abc["seed"], ac["seed"]), model))
        d5 = a["T_debiased"] - c["T_debiased"]
        z5 = zscore(d5, s5)
        return {"ABC": a, "AC": c, "delta": d5, "sigma": s5, "z": z5, "class": cls_r5(z5),
                "fraction": d5 / a["T_debiased"] if a["T_debiased"] != 0 else None, "resolved_3sigma": POS * s5}
    out["R5"], out["R5bar"] = r5(idx73), r5(idxbar)

    out["sensitivity_printed"] = {str(k): {"R2": r2(top_modes(lam, k)), "R5": r5(top_modes(lam, k))} for k in SENS_K}
    return out


def readings(m, groups, x_er, p, V, cells, shares_by_row):
    """Both noise models, and the merged classes that the outcome reads."""
    by = {md: readings_one(m, groups, x_er, p, V, cells, shares_by_row, md) for md in NOISE_MODELS}
    a, b = (by[md] for md in NOISE_MODELS)
    cls = {"R5": merge_class(a["R5"]["class"], b["R5"]["class"]),
           "R5bar": merge_class(a["R5bar"]["class"], b["R5bar"]["class"]),
           "R2": merge_class(a["R2"]["class"], b["R2"]["class"]),
           "R2bar": merge_class(a["R2bar"]["class"], b["R2bar"]["class"]),
           "R3": {i: merge_class(a["R3"][i]["class"], b["R3"][i]["class"]) for i in a["R3"]},
           "R4": {g: merge_class(a["R4"][g]["class"], b["R4"][g]["class"]) for g in GROUPS}}
    return {"n_cells": len(p), "n_replicas": N_REPLICAS, "noise_models": list(NOISE_MODELS),
            "noise_note": ("every sigma, and the noise behind every null class, comes from 10 bootstrap draws plus one "
                           "seed draw per group (accepted by the director on 2026-11-06); a sigma is uncertain by "
                           "about +-24%"),
            "by_model": by, "classes": cls,
            "combined_statement": combined_statement(cls["R5"], cls["R4"])}


# ---------------------------------------------------------------------------------------- the read
def roles_of(rows, dest):
    """Map declared operands to roles. Raises Refused if the set is not exactly the declared one."""
    roles = {"published": None, "E_R": None, "CTRL": None, "groups": {g: {"s42": None, "s43": None, "boot": {}} for g in GROUPS}}
    for _, src in rows:
        dst = str(Path(dest) / copy_name(src))
        tag = Path(src).parent.name
        if Path(src).name.startswith("cov_ptpl_"):
            roles["published"] = dst
        elif tag == "ER":
            roles["E_R"] = dst
        elif tag == "pu_CTRL_s42":
            roles["CTRL"] = dst
        else:
            _, g, kind = tag.split("_")
            if g not in GROUPS:
                raise Refused(f"unexpected operand {src}")
            if kind in ("s42", "s43"):
                roles["groups"][g][kind] = dst
            else:
                roles["groups"][g]["boot"][int(kind[1:])] = dst
    for g in GROUPS:
        if sorted(roles["groups"][g]["boot"]) != list(range(1, N_REPLICAS + 1)):
            raise Refused(f"group {g}: replicas {sorted(roles['groups'][g]['boot'])}")
    if None in (roles["published"], roles["E_R"], roles["CTRL"]):
        raise Refused("published, E_R or control operand missing from INPUTS.sha256")
    return roles


def load_all(m, roles):
    import ROOT  # noqa: E402
    cpf = m.compare_to_paper_fullcov

    def ours(path):
        f = ROOT.TFile.Open(path)
        if not f or f.IsZombie():
            raise Refused(f"cannot open {path}")
        h = f.Get("hXSec2D")
        if not h:
            raise Refused(f"{path}: no hXSec2D")
        v = cpf.flatten_ours(h)
        f.Close()
        return v

    fp = ROOT.TFile.Open(roles["published"])
    pub = {"p": cpf.flatten_th2d(fp.Get("pt_pl_cross_section")),
           "total": cpf.tmatrix_to_numpy(fp.Get("TotalCovariance")),
           "stat": cpf.tmatrix_to_numpy(fp.Get("StatOnlyCovariance"))}
    fp.Close()
    prods = {"E_R": ours(roles["E_R"]), "CTRL": ours(roles["CTRL"])}
    for g in GROUPS:
        prods[f"{g}_s42"] = ours(roles["groups"][g]["s42"])
        prods[f"{g}_s43"] = ours(roles["groups"][g]["s43"])
        for r in range(1, N_REPLICAS + 1):
            prods[f"{g}_b{r:02d}"] = ours(roles["groups"][g]["boot"][r])
    return pub, prods


def run_controls(m, pub, prods, partc):
    mask = np.diag(pub["stat"]) > 0
    mask_idx = np.flatnonzero(mask)
    cells = mask_idx
    p = pub["p"][mask]
    V = pub["total"][np.ix_(mask, mask)]
    red = {k: v[mask] for k, v in prods.items()}
    lam, U = eig_basis(V)
    idx_all = np.arange(mask_idx.size)
    idx73 = top_modes(lam, K73)
    chi2_er = m.compare_to_paper_fullcov.chi2_with_cov(prods["E_R"] - pub["p"], pub["total"], "E_R", report=False)[0]
    met, w_lo, w_hi = step_ops(m, cells, p)
    w_abc = exposure_weights(partc["exposure_share_by_pt_row"], cells, len(m.common.PZ_A) - 1, GROUPS)
    x_abc = sum(w_abc[g] * red[f"{g}_s42"] for g in GROUPS)
    ctl = [
        ctl_partc(partc),
        ctl_cells(m.reported_cells, mask_idx, prods),
        ctl_pub(chi2_er),
        ctl_sum(quad(red["E_R"] - p, lam, U, idx_all), chi2_er),
        ctl_k(lam, quad(red["E_R"] - p, lam, U, idx73), mask_idx.size),
        ctl_modes(lam, U, red["E_R"] - p),
        ctl_ctrl(red["CTRL"], red["E_R"], p, (lam, U), idx73, idx_all),
        ctl_step(step_value(m, met, red["PB_s42"], red["PA_s42"])),
        ctl_grad(m, met, w_lo, w_hi, red["E_R"], p),
        ctl_comb(w_abc, x_abc, red["CTRL"], m.common.area(cells)),
    ]
    ctx = {"cells": cells, "p": p, "V": V, "red": red}
    return ctl, ctx


def groups_from(red):
    return {g: {"x": red[f"{g}_s42"], "seed": red[f"{g}_s43"],
                "reps": [red[f"{g}_b{r:02d}"] for r in range(1, N_REPLICAS + 1)]} for g in GROUPS}


def load_partc():
    got = sha256(PARTC_ANALYSIS)
    if got != PARTC_ANALYSIS_SHA:
        raise Refused(f"{PARTC_ANALYSIS}: sha256 {got} != {PARTC_ANALYSIS_SHA}")
    return json.loads(PARTC_ANALYSIS.read_text())


def _json(o):
    if isinstance(o, dict):
        return {str(k): _json(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_json(v) for v in o]
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, float) and not math.isfinite(o):
        return str(o)
    return o


def do_read(dest, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    m = import_reused()
    rows = read_inputs()
    ver = verify_copies(dest, rows)
    if ver["verdict"] != "PASS":
        (out / "REFUSE.json").write_text(json.dumps(ver, indent=1) + "\n")
        raise Refused(f"{len(ver['refused'])} copies differ from INPUTS.sha256")
    partc = load_partc()
    pub, prods = load_all(m, roles_of(rows, dest))
    ctl, ctx = run_controls(m, pub, prods, partc)
    head = {"script_sha256": sha256(__file__), "inputs_sha256": ver["inputs_sha256"],
            "partc_analysis_sha256": PARTC_ANALYSIS_SHA, "modules": {k: sha256(getattr(m, k).__file__)
                                                                     for k in vars(m)}, "controls": ctl}
    if any(c["verdict"] != "PASS" for c in ctl):
        head["verdict"] = "STOP"
        (out / "STOP.json").write_text(json.dumps(_json(head), indent=1) + "\n")
        return EXIT_STOP
    head["verdict"] = "READ"
    head["readings"] = readings(m, groups_from(ctx["red"]), ctx["red"]["E_R"], ctx["p"], ctx["V"], ctx["cells"],
                                partc["exposure_share_by_pt_row"])
    (out / "readout.json").write_text(json.dumps(_json(head), indent=1) + "\n")
    (out / "readout.txt").write_text(summary(head["readings"]) + "\n")
    return 0


def summary(r):
    L = [f"per-period 2D benchmark readout; {r['noise_note']}",
         f"classes (read only where both noise models agree): {json.dumps(r['classes'])}"]
    for md, x in r["by_model"].items():
        L.append(f"--- noise model {md}")
        for key in ("R5", "R5bar"):
            y = x[key]
            L.append(f"{key}: delta {y['delta']:+.4f}  sigma {y['sigma']:.4f}  z {y['z']:+.2f}  -> {y['class']}")
        for key in ("R2", "R2bar"):
            y = x[key]
            L.append(f"{key}: " + "  ".join(f"{g} T~ {y['per_group'][g]['T_debiased']:.4f}+-{y['per_group'][g]['sigma']:.4f}"
                                            for g in GROUPS) + f"  z {y['z']}  -> {y['class']}")
        for i, y in x["R3"].items():
            L.append(f"R3 mode {i}: z_E_R {y['z_E_R']:+.2f}  delta {y['delta']}  -> {y['class']}")
        for g in GROUPS:
            y = x["R4"][g]
            L.append(f"R4 {g}: st {y['st']:+.5f}  sigma_pub {y['sigma_pub']:.5f}  z {y['z']:+.2f}  -> {y['class']}")
    L.append(f"combined statement: {r['combined_statement']}")
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("copy")
    c.add_argument("--dest", required=True)
    v = sub.add_parser("verify")
    v.add_argument("--dest", required=True)
    r = sub.add_parser("read")
    r.add_argument("--dest", required=True)
    r.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    try:
        if a.cmd == "copy":
            do_copy(a.dest)
            return 0
        if a.cmd == "verify":
            rec = verify_copies(a.dest)
            Path(a.dest, "verify.json").write_text(json.dumps(rec, indent=1) + "\n")
            return 0 if rec["verdict"] == "PASS" else EXIT_REFUSE
        return do_read(a.dest, a.out)
    except Refused as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return EXIT_REFUSE


if __name__ == "__main__":
    sys.exit(main())
