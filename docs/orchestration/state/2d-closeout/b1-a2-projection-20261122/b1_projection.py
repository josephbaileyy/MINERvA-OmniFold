#!/usr/bin/env python3
"""b1: IBUKT A2's mean residual pattern projected onto Delta = E_R - published in V_pub's modes.

Implements DECLARATION.md in this directory (committed at c75612a7 before any projection). Local, 0 node-h.

  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  <rootmpl3108 python> b1_projection.py --er <xsec.root> --pub <cov_ptpl_minerva_inclusive_6GeV.root> \
      --readout docs/orchestration/state/2d-closeout/ibukt-a2/readout.json --out <dir> [--controls-only]

--controls-only runs the controls that use no residual pattern (C-OPS, C-CELLS, C-PUB, C-SUM, C-K, C-M on Delta,
C-A2) and writes controls.json. Nothing involving beta is computed in that mode.
Exit 0 = PASS (readout written), 3 = a control STOPped (controls.json written, no readings).
"""

import argparse
import hashlib
import json
import math
import os
import sys
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
TD = REPO / "2d-unfolding"

# ------------------------------------------------------------------ declared constants (DECLARATION.md section)
SHA = {  # section 1
    "er": "a5c13fc38d64242bc9ee459fac87568a2f97fddf7a3ac97cc6f91eb4c2a31cef",
    "pub": "6c6dce72050bb8f128fab8e286349b250bc60d1c767e162bf15a0f009f3573e3",
    "readout": "dfae50f595ac37b5179722a6a9d264f758cce91c163ca6cc1ab3b03462da8da6",
}
CHI2_ER = 465.4152721915331          # section 4 C-PUB
K73 = 73                             # section 2, C-K
RCOND_K = 1e-4
S73_PER205 = 0.662
M_RANKS = (23, 9, 118, 2, 79, 121)   # section 2
M_EXPECT = {23: ("3.549e-09", 4.75), 9: ("4.314e-10", 3.78), 118: ("5.613e-05", 3.65),
            2: ("6.590e-11", 3.64), 79: ("4.460e-06", 3.61), 121: ("6.048e-05", 3.50)}
T_MULT = 2.7764451051977987          # section 2, A2's guard multiplier
N_TRIALS = 5
PRIMARY = ("nominal", "genie_mec", "nuwro")
SECONDARY = ("bump", "tilt", "within_plus", "within_minus")
READ_METHOD = "omnifold"
PRINT_METHODS = ("ibu5", "ibu10")
PREC_MODE_REL = 0.01                 # N-PREC: per-mode component, relative
PREC_G_ABS = 0.01                    # N-PREC: g_K between drivers, absolute
BANDS = ("opposite", "minor", "partial", "candidate")
SENT = {
    "candidate": "At truth {t}, the E_R estimator's A2 mean residual pattern supplies at least half of Delta's component "
                 "along Delta in {K}. Estimator bias of this pattern is a candidate contributor to the difference in "
                 "these directions. It is not shown to be the cause.",
    "partial": "At truth {t}, the E_R estimator's A2 mean residual pattern supplies between a fifth and a half of "
               "Delta's component in {K}: a partial contributor at most.",
    "minor": "At truth {t}, the E_R estimator's A2 mean residual pattern supplies at most a fifth of Delta's component "
             "in {K}, either way. This weakens this bias pattern as a main contributor in these directions.",
    "opposite": "At truth {t}, the E_R estimator's A2 mean residual pattern points away from Delta in {K}. Removing it "
                "would increase the distance.",
}
KNAME = {"K73": "the 73 best-determined directions of the published covariance",
         "Kbar": "the 132 poorly determined directions of the published covariance"}


# ------------------------------------------------------------------ pure functions (tested)
def band_of(x):
    """Section 3: an edge belongs to the band nearer zero, except 0.5, which belongs to candidate."""
    if x < -0.2:
        return "opposite"
    if x <= 0.2:
        return "minor"
    if x < 0.5:
        return "partial"
    return "candidate"


def label(f, h):
    """Read a band only if [f-h, f+h] lies inside one band; else 'unresolved between A and B'."""
    if not (math.isfinite(f) and math.isfinite(h)):
        return "unresolved (non-finite)"
    lo, hi = band_of(f - h), band_of(f + h)
    if lo == hi:
        return lo
    touched = BANDS[BANDS.index(lo):BANDS.index(hi) + 1]
    return "unresolved between " + " and ".join(touched)


def guard(fs):
    fs = np.asarray(fs, dtype=float)
    return float(T_MULT * np.std(fs, ddof=1) / math.sqrt(len(fs)))


def basis(V, driver):
    """Ascending eigen-decomposition (rank 0 = smallest)."""
    if driver == "numpy":
        lam, U = np.linalg.eigh(V)
    elif driver == "evr":
        import scipy.linalg
        lam, U = scipy.linalg.eigh(V, driver="evr")
    else:
        raise ValueError(driver)
    return lam, U


def signed_basis(lam, U, d):
    """Fix each u_i's sign so z_Delta,i > 0 (section 2). A zero component keeps its sign."""
    c = U.T @ d
    s = np.where(c < 0, -1.0, 1.0)
    return lam, U * s


def whiten(lam, U, v):
    return (U.T @ v) / np.sqrt(lam)


def g_share(zb, zd, idx):
    return float(np.sum(zb[idx] * zd[idx]) / np.sum(zd[idx] ** 2))


def quad(z, idx):
    return float(np.sum(z[idx] ** 2))


def mode_sets(lam):
    order = np.argsort(lam)[::-1]
    k73 = np.sort(order[:K73])
    kbar = np.setdiff1d(np.arange(len(lam)), k73)
    return {"K73": k73, "Kbar": kbar, "K205": np.arange(len(lam))}


def project(lam, U, d, betas):
    """All statistics for one pattern (betas: trials x n). Returns a dict per set and per M mode."""
    zd = whiten(lam, U, d)
    zt = np.array([whiten(lam, U, b) for b in betas])
    zb = zt.mean(axis=0)
    out = {"sets": {}, "modes": {}}
    for name, idx in mode_sets(lam).items():
        g = g_share(zb, zd, idx)
        gs = [g_share(z, zd, idx) for z in zt]
        sb, sd_ = quad(zb, idx), quad(zd, idx)
        noise = sum(quad(z - zb, idx) for z in zt) / (N_TRIALS - 1) / N_TRIALS
        rem = quad(zd - zb, idx) / sd_
        cos = float(np.sum(zb[idx] * zd[idx]) / math.sqrt(sb * sd_)) if sb > 0 else float("nan")
        out["sets"][name] = {"g": g, "g_trials": gs, "h": guard(gs), "g_mean_of_trials": float(np.mean(gs)),
                             "cos": cos, "q_raw": sb / sd_, "q_debiased": (sb - noise) / sd_,
                             "remainder_unit_amplitude": rem, "S_delta": sd_, "n_modes": int(len(idx))}
    for r in M_RANKS:
        rho = float(zb[r] / zd[r])
        rs = [float(z[r] / zd[r]) for z in zt]
        out["modes"][str(r)] = {"rho": rho, "rho_trials": rs, "h": guard(rs), "rho_mean_of_trials": float(np.mean(rs)),
                                "z_delta": float(zd[r]), "z_beta": float(zb[r])}
    return out, zd, zb


def combined(labels):
    vals = set(labels)
    if vals == {"candidate"}:
        return "candidate at every tested truth"
    if vals == {"minor"}:
        return "weakened at every tested truth"
    if vals == {"opposite"}:
        return "opposite at every tested truth"
    return "truth-dependent"


# ------------------------------------------------------------------ I/O and controls
def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def import_cpf():
    if str(TD) not in sys.path:
        sys.path.insert(0, str(TD))
    import compare_to_paper_fullcov as cpf  # noqa: E402
    f = os.path.realpath(cpf.__file__)
    if not f.startswith(os.path.realpath(REPO) + os.sep):
        raise SystemExit(f"compare_to_paper_fullcov resolved outside the repo: {f}")
    return cpf


def load_root(cpf, er_path, pub_path):
    import ROOT  # noqa: E402
    f = ROOT.TFile.Open(str(er_path))
    er = cpf.flatten_ours(f.Get("hXSec2D"))
    f.Close()
    fp = ROOT.TFile.Open(str(pub_path))
    p = cpf.flatten_th2d(fp.Get("pt_pl_cross_section"))
    total = cpf.tmatrix_to_numpy(fp.Get("TotalCovariance"))
    stat = cpf.tmatrix_to_numpy(fp.Get("StatOnlyCovariance"))
    fp.Close()
    return er, p, total, stat


def ctl(cid, ok, **vals):
    return {"id": cid, "ok": bool(ok), **vals}


def c_modes(lam, U, d, prec_unresolved):
    lam_max = lam.max()
    rows, ok_all, hard_fail = [], True, False
    for r, (lam_txt, zabs) in M_EXPECT.items():
        got_l = lam[r] / lam_max
        want_l = float(lam_txt)
        half = 0.5 * 10 ** (math.floor(math.log10(want_l)) - 3)
        got_z = abs(float(U[:, r] @ d) / math.sqrt(lam[r]))
        good = abs(got_l - want_l) <= half * (1 + 1e-9) and abs(got_z - zabs) <= 0.005 * (1 + 1e-9)
        ok_all &= good
        if not good and r not in prec_unresolved:
            hard_fail = True
        rows.append({"rank": r, "lam_rel": got_l, "lam_rel_declared": lam_txt, "abs_z": got_z,
                     "abs_z_declared": zabs, "ok": bool(good), "n_prec_unresolved": r in prec_unresolved})
    return ctl("C-M", not hard_fail, all_within=bool(ok_all), modes=rows)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--er", required=True)
    ap.add_argument("--pub", required=True)
    ap.add_argument("--readout", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--controls-only", action="store_true")
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    controls = []

    got = {"er": sha256(a.er), "pub": sha256(a.pub), "readout": sha256(a.readout)}
    controls.append(ctl("C-OPS", got == SHA, measured=got, declared=SHA))
    if not controls[-1]["ok"]:
        return stop(out, controls)

    cpf = import_cpf()
    er, p, total, stat = load_root(cpf, a.er, a.pub)
    rd = json.load(open(a.readout))

    mask_stat = np.flatnonzero(np.diag(stat) > 0)
    mask_tot = np.flatnonzero(np.diag(total) > 0)
    cells_ok = {t: rd["truths"][t]["cells"] == mask_stat.tolist() for t in rd["truths"]}
    controls.append(ctl("C-CELLS", len(mask_stat) == 205 and np.array_equal(mask_stat, mask_tot)
                        and all(cells_ok.values()), n_stat=int(len(mask_stat)), n_total=int(len(mask_tot)),
                        same_sets=bool(np.array_equal(mask_stat, mask_tot)), truths=cells_ok))
    if not controls[-1]["ok"]:
        return stop(out, controls)
    cells = mask_stat
    d = (er - p)[cells]
    V = total[np.ix_(cells, cells)]
    kappa = float(np.linalg.cond(V))
    eps = float(np.finfo(float).eps)

    chi2, ndf, _ = cpf.chi2_with_cov(er - p, total, "E_R vs published", report=False)
    bar_pub = max(1e-8, 10 * kappa * eps)
    rel_pub = abs(chi2 - CHI2_ER) / CHI2_ER
    controls.append(ctl("C-PUB", rel_pub <= bar_pub, chi2=chi2, declared=CHI2_ER, rel=rel_pub, bar=bar_pub,
                        kappa2=kappa, ndf=int(ndf)))

    bases = {}
    for drv in ("numpy", "evr"):
        lam, U = basis(V, drv)
        bases[drv] = signed_basis(lam, U, d)
    lam, U = bases["numpy"]
    zd = whiten(lam, U, d)
    s_all = float(np.sum(zd ** 2))
    bar_sum = max(1e-6, 10 * kappa * eps)
    controls.append(ctl("C-SUM", abs(s_all - chi2) / chi2 <= bar_sum, s205=s_all, chi2=chi2,
                        rel=abs(s_all - chi2) / chi2, bar=bar_sum))
    k = int(np.sum(lam > RCOND_K * lam.max()))
    s73 = quad(zd, mode_sets(lam)["K73"])
    controls.append(ctl("C-K", k == K73 and abs(s73 / 205 - S73_PER205) <= 5e-4, k=k, s73_per205=s73 / 205))

    zd_e = whiten(*bases["evr"], d)
    mode_rel_delta = np.abs(zd - zd_e) / np.abs(zd)
    unres_delta = {r for r in M_RANKS if mode_rel_delta[r] > PREC_MODE_REL}

    # C-A2: the committed means and guards
    worst = 0.0
    for t, tv in rd["truths"].items():
        for m in ("omnifold", "ibu5", "ibu10"):
            res = np.array(tv[m]["residuals"], dtype=float)
            mean = res.mean(axis=0)
            h = T_MULT * res.std(axis=0, ddof=1) / math.sqrt(N_TRIALS)
            worst = max(worst, float(np.max(np.abs(mean - np.array(tv[m]["mean"])))),
                        float(np.max(np.abs(h - np.array(tv[m]["noise_guard"])))))
    controls.append(ctl("C-A2", worst <= 1e-15, worst_abs=worst, bar=1e-15))

    if a.controls_only:
        controls.append(c_modes(lam, U, d, unres_delta))
        rec = {"mode": "controls-only", "controls": controls, "all_ok": all(c["ok"] for c in controls),
               "mode_rel_delta_driver_diff": mode_rel_delta.tolist()}
        (out / "controls.json").write_text(json.dumps(rec, indent=1) + "\n")
        print(json.dumps({c["id"]: c["ok"] for c in controls}))
        return 0 if rec["all_ok"] else 3

    # ---------------- projections (both drivers)
    res = {}
    for drv in ("numpy", "evr"):
        lam_d, U_d = bases[drv]
        res[drv] = {}
        for t, tv in rd["truths"].items():
            res[drv][t] = {}
            for m in ("omnifold", "ibu5", "ibu10"):
                e = np.array(tv[m]["residuals"], dtype=float)
                pr, _, _ = project(lam_d, U_d, d, e * er[cells])
                sens, _, _ = project(lam_d, U_d, d, e * p[cells])
                res[drv][t][m] = {"beta_E_R": pr, "beta_p_sensitivity": sens}

    # N-PREC on beta components (primary truths, read method)
    unres_beta = set()
    for t in PRIMARY:
        for r in M_RANKS:
            a1 = res["numpy"][t][READ_METHOD]["beta_E_R"]["modes"][str(r)]["z_beta"]
            a2 = res["evr"][t][READ_METHOD]["beta_E_R"]["modes"][str(r)]["z_beta"]
            if abs(a1 - a2) > PREC_MODE_REL * abs(a1):
                unres_beta.add(r)
    unresolved_modes = sorted(unres_delta | unres_beta)
    controls.append(c_modes(lam, U, d, set(unresolved_modes)))

    # C-LIN
    lin = 0.0
    for t in rd["truths"]:
        for m in ("omnifold", "ibu5", "ibu10"):
            pr = res["numpy"][t][m]["beta_E_R"]
            for s in pr["sets"].values():
                lin = max(lin, abs(s["g"] - s["g_mean_of_trials"]) / max(abs(s["g"]), 1e-300))
            for s in pr["modes"].values():
                lin = max(lin, abs(s["rho"] - s["rho_mean_of_trials"]) / max(abs(s["rho"]), 1e-300))
    controls.append(ctl("C-LIN", lin <= 1e-10, worst_rel=lin, bar=1e-10))

    if not all(c["ok"] for c in controls):
        return stop(out, controls)

    # ---------------- readings (section 3)
    readings = {"R1": {}, "R2": {}, "R3": {}}
    for t in PRIMARY + SECONDARY:
        role = "primary" if t in PRIMARY else "secondary"
        for rid, K in (("R1", "K73"), ("R2", "Kbar")):
            s1 = res["numpy"][t][READ_METHOD]["beta_E_R"]["sets"][K]
            s2 = res["evr"][t][READ_METHOD]["beta_E_R"]["sets"][K]
            l1, l2 = label(s1["g"], s1["h"]), label(s2["g"], s2["h"])
            if abs(s1["g"] - s2["g"]) > PREC_G_ABS or l1 != l2:
                lab = "numerically unresolved"
            else:
                lab = l1
            sent = SENT[lab].format(t=t, K=KNAME[K]) if lab in SENT else None
            readings[rid][t] = {"role": role, "g": s1["g"], "h": s1["h"], "g_evr": s2["g"], "h_evr": s2["h"],
                                "label": lab, "sentence": sent}
        readings["R3"][t] = {"role": role}
        for r in M_RANKS:
            s1 = res["numpy"][t][READ_METHOD]["beta_E_R"]["modes"][str(r)]
            if r in unresolved_modes:
                lab = "numerically unresolved"
            else:
                lab = label(s1["rho"], s1["h"])
            readings["R3"][t][str(r)] = {"rho": s1["rho"], "h": s1["h"], "label": lab,
                                         "reproduces_mode": lab == "candidate"}
    comb = {rid: combined([readings[rid][t]["label"] for t in PRIMARY]) for rid in ("R1", "R2")}

    rec = {"schema": "b1-a2-projection/1", "declaration": "DECLARATION.md @ c75612a7",
           "controls": controls, "all_ok": True, "kappa2": kappa,
           "n_prec": {"mode_rel_delta_driver_diff": mode_rel_delta.tolist(),
                      "unresolved_modes_in_M": unresolved_modes},
           "readings": readings, "combined": comb, "projections": res,
           "limits": "descriptive only; no cause; Delta fixed; A2 bias at 7 development truths, 5 draws, one bank"}
    (out / "readout.json").write_text(json.dumps(rec, indent=1) + "\n")
    (out / "readout.txt").write_text(render(rec))
    print(render(rec))
    return 0


def render(rec):
    L = ["b1: A2 mean residual pattern on Delta = E_R - published, V_pub modes", ""]
    L.append("controls: " + ", ".join(f"{c['id']} {'PASS' if c['ok'] else 'FAIL'}" for c in rec["controls"]))
    L.append(f"N-PREC unresolved M modes: {rec['n_prec']['unresolved_modes_in_M']}")
    L.append("")
    for rid, K in (("R1", "K73"), ("R2", "Kbar")):
        L.append(f"{rid} ({K}): g +/- h [evr g]  label")
        for t, v in rec["readings"][rid].items():
            L.append(f"  {t:13s} {v['role']:9s} {v['g']:+.4f} +/- {v['h']:.4f} [{v['g_evr']:+.4f}]  {v['label']}")
        L.append(f"  combined (primary): {rec['combined'][rid]}")
        L.append("")
    L.append("R3 (M modes): rho +/- h  label")
    for t, v in rec["readings"]["R3"].items():
        cells = "  ".join(f"{r}:{v[str(r)]['rho']:+.3f}+/-{v[str(r)]['h']:.3f} {v[str(r)]['label']}" for r in M_RANKS)
        L.append(f"  {t:13s} {v['role']:9s} {cells}")
    L.append("")
    L.append("printed, read by nothing (numpy driver): per method/truth/set g, h, cos, q_raw, q_debiased, remainder")
    for t, tv in rec["projections"]["numpy"].items():
        for m, mv in tv.items():
            for K in ("K73", "Kbar", "K205"):
                s = mv["beta_E_R"]["sets"][K]
                sp = mv["beta_p_sensitivity"]["sets"][K]
                L.append(f"  {t:13s} {m:8s} {K:5s} g {s['g']:+.4f} h {s['h']:.4f} cos {s['cos']:+.4f} "
                         f"q {s['q_raw']:.4g} q~ {s['q_debiased']:.4g} rem {s['remainder_unit_amplitude']:.4g} "
                         f"| e*p g {sp['g']:+.4f}")
    return "\n".join(L) + "\n"


def stop(out, controls):
    (out / "controls.json").write_text(json.dumps({"mode": "STOP", "controls": controls}, indent=1, default=str) + "\n")
    print("STOP: " + ", ".join(f"{c['id']} {'PASS' if c['ok'] else 'FAIL'}" for c in controls))
    return 3


if __name__ == "__main__":
    sys.exit(main())
