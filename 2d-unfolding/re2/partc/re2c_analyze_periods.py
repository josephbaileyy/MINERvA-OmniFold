#!/usr/bin/env python3
"""RE-2 part C copy of period-unfold-20261014/scripts/analyze_periods.py (912af1dd...), RE2-DECLARATION-C.md §3.4.

    python3 -I re2c_analyze_periods.py [--arm refined --work-cov PATH SHA256 --ns DIR] <mode> ...   (modes below)

  --arm purity (default)  the original, unchanged: it must reproduce analysis.json 05edff61... (K1-roll)
  --arm refined           pins from re2c_periods.set_arm("refined"); every run's driver and background mode is
                          checked (PA-02, PT-G); the control compares pu_CTRL_s42 with E_R and J0's refined D_cv and,
                          unlike the original (PA-05c), exits nonzero unless it passes

The metric stays VL175 + ML of work_cov with only x moving to E_R (the director's ruling Q2). The noise reference
resamples data and MC, not the background stream, in both arms: J8's period replicas ran --bootstrap-streams both,
as the purity chain's did (a disclosure, RE2-DECLARATION-C.md §3.4).

The original docstring follows.

Phase-2 analysis of the period-unfold test (cluster, root_6_28; reads small ROOT products only).

    python3 -I analyze_periods.py control  OUTDIR RESULT.json        # pu_CTRL_s42 vs XR-L0 and E_U (frozen 1e-8)
    python3 -I analyze_periods.py roles    OUTDIR ROLES.json         # role map from the job outputs
    python3 -I analyze_periods.py analyze  ROLES.json RESULT.json RESULT.txt
    python3 -I analyze_periods.py selftest RESULT.json               # identity + injection tests (no job output needed)

ROLES.json: {"POOL": path, "PA": {"s42": path, "s43": path, "boot": [paths]}, "PB": {...}, "PC": {...}}.

Quantities (205 reported cells of VL175, C-order flat index ipt*16+ipz of the 14 x 16 grid):
  x_X   unfolded hXSec2D of period X (its own POT scale and flux), X in PA, PB, PC; x_POOL the control.
  t_X   the MC-truth cross section of X: hTruth2D through the producer's formula (extract_cross_section_2d,
        unfold_2d_omnifold_unbinned.py:1207-1270) with X's completeness, flux, POT and nucleons.
  r_X   = x_X / t_X, the data/MC double ratio; the unfolded analogue of the reco proxy R of the spread record.
  e_X   exposure share per p_T row, POT_X Phi_X(pT) / sum_Y POT_Y Phi_Y(pT). With it sum_X e_X x_X is the
        cross section of the summed unfolded yields (it equals x_POOL if the unfold were additive).
Comparisons (fractional shift f per cell):
  raw  B/A, C/A, C/B, X/POOL, POOL/A    : x_num / x_den - 1
  dr   the same on r (cells); marginals and the step as data/MC of integrated yields: the unfolded shape of the
       playlist-spread R
  mc   B/A, C/A on t                      : what the MC alone predicts for the period difference
  bias_B, bias_C  = e_X (x_X/x_A - 1)     : coverage/REPORT.md (b) analogue, the shift of the combined result
                                            if period X alone is off against P_A
  J36  = sum_X e_X x_X / x_POOL - 1 (and the data-POT-weighted variant J36_potw): the per-period POT fix
Each f is assessed exactly as coverage/scripts/coverage.py:assess: b = f * E_U, chi2 against VL175 + ML
(hCov_combined + ML of work_cov.npz) by common.mahalanobis2 (pinv, rcond 1e-12) over 205 cells and over the
covariance-exact p_par (16) and p_T (14) marginals, cell and marginal z, integral shift. The step statistic is
I_hi/I_lo of the p_par-marginal ratio (I = sum over p_par bins of the marginal x bin width; lo [1.5, 8),
hi [8, 15) GeV/c, common.STEP_LO/HI) minus 1.
Noise reference (same statistics on noise): per period, bootstrap draws d_k = x_b,k / x_s42 - 1 (seed 42,
Poisson(1) data+MC, a distinct bootstrap seed per period) and one seed draw s = x_s43 / x_s42 - 1. A comparison's
noise is a linear combination sum_X a_X * delta_X of the periods' fractional fluctuations (B/A: a_B = 1,
a_A = -1; X/POOL: pooled ~ sum_Y e_Y x_Y, so a_X = 1 - e_X, a_Y = -e_Y; bias_X: e_X (1, -1)), plus the pooled
seed covariance C_ML (VL175's ML block) where the pooled result enters; J36 carries seed noise only (its
statistical part is common to both sides, so this is a lower bound). Noise covariance
N = sum_X (a_X a_X^T) o (mean_k d_k d_k^T + s s^T / 2); expected noise chi2 = tr(C^+ (x x^T o N)) with the same
pinv; plus the chi2 of each paired noise draw and the step's noise sigma.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import re2c_periods as PD  # noqa: E402

sys.path.insert(0, PD.COVERAGE_SCRIPTS)
import common as C  # noqa: E402  (pinned copy, main c67dbdda)

XR_DIR = f"{PD.CODE}/docs/orchestration/state/next-preparation-20261009/xr-linux/xr"
REF_SHAPE = f"{PD.CODE}/docs/orchestration/state/2d-closeout/playlist-spread-20261014/outputs/ref_shape.json"
PER = ("PA", "PB", "PC")


# ------------------------------------------------------------------------------------------------ inputs
def th2(h):
    return np.array([[h.GetBinContent(i + 1, j + 1) for j in range(h.GetNbinsY())] for i in range(h.GetNbinsX())])


def load(path, cells):
    import ROOT
    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        raise SystemExit(f"cannot open {path}")
    hx = f.Get("hXSec2D")
    ex = np.array([hx.GetXaxis().GetBinLowEdge(i) for i in range(1, hx.GetNbinsX() + 2)])
    ey = np.array([hx.GetYaxis().GetBinLowEdge(i) for i in range(1, hx.GetNbinsY() + 2)])
    if not (np.allclose(ex, C.PT_A) and np.allclose(ey, C.PZ_A)):
        raise SystemExit(f"{path}: axes differ from the analysis grid")
    x = th2(hx)
    T = th2(f.Get("hTruth2D"))
    c = th2(f.Get("hOFCompleteness2D"))
    hf = f.Get("hFlux_pt")
    phi = np.array([hf.GetBinContent(i) for i in range(1, hf.GetNbinsX() + 1)])
    pot = float(f.Get("dataPOT").GetVal())
    nn = float(f.Get("nNucleons").GetVal())
    rc = f.Get("runConfig")
    run = json.loads(rc.GetTitle()) if rc else {}
    dsha = f.Get("driverSha256")
    f.Close()
    dpt, dpz = np.diff(C.PT_A), np.diff(C.PZ_A)
    denom = c * phi[:, None] * nn * pot * dpt[:, None] * dpz[None, :]
    with np.errstate(divide="ignore", invalid="ignore"):
        t = np.where((c > 0) & (phi[:, None] > 0), T / denom * 1.0e4, 0.0)
    return {"path": path, "sha256": PD.sha256(path), "x": x.ravel(order="C")[cells], "t": t.ravel(order="C")[cells],
            "phi": phi, "pot": pot, "seed": run.get("seed"), "bootstrap_seed": run.get("bootstrap_seed"),
            "omnifile": run.get("omnifile"), "mcfile": run.get("mcfile"),
            "driverSha256": dsha.GetTitle() if dsha else None,
            "n_reported_own": int((x > 0).sum()),
            **{k: run.get(k) for k in ("bkg_mode", "refine_n_estimators", "refine_num_leaves")}}


# ------------------------------------------------------------------------------------------------ metric
class Metric:
    """coverage.py's assessment against the quoted covariance (VL175 total = hCov_combined + ML)."""

    def __init__(self, W, keep):
        cells = W["cells"]
        self.keep = keep
        self.cells = cells[keep]
        self.x = W["EU"].ravel(order="C")[cells][keep]
        Ct = (W["cov__hCov_combined"] + W["cov__ML"])[np.ix_(keep, keep)]
        self.C = Ct
        self.Cml_frac = W["cov__ML"][np.ix_(keep, keep)] / np.outer(self.x, self.x)
        self.A = C.area(self.cells)
        self.P = {"pz": C.proj_matrix("pz", self.cells), "pt": C.proj_matrix("pt", self.cells)}
        self.m = {k: P @ self.x for k, P in self.P.items()}
        self.sig_cell = np.sqrt(np.diag(Ct)) / self.x
        self.sig_m = {k: np.sqrt(np.diag(P @ Ct @ P.T)) / self.m[k] for k, P in self.P.items()}
        self.Ci = {"205": self._pinv(Ct)}
        for k, P in self.P.items():
            self.Ci[k] = self._pinv(P @ Ct @ P.T)

    @staticmethod
    def _pinv(M, rcond=1e-12):  # the truncation of common.mahalanobis2
        lam, V = np.linalg.eigh(0.5 * (M + M.T))
        k = lam > rcond * lam.max()
        return (V[:, k] / lam[k]) @ V[:, k].T

    def chi2(self, f):
        b = f * self.x
        o = {"205": C.mahalanobis2(b, self.C)[0]}
        for k, P in self.P.items():
            o[k] = C.mahalanobis2(P @ b, P @ self.C @ P.T)[0]
        return o

    def expected_chi2(self, Nf):
        """tr(C^+ (x x^T o N)) for a fractional noise covariance N, in each projection."""
        Na = Nf * np.outer(self.x, self.x)
        o = {"205": float(np.trace(self.Ci["205"] @ Na))}
        for k, P in self.P.items():
            o[k] = float(np.trace(self.Ci[k] @ (P @ Na @ P.T)))
        return o

    def assess(self, f):
        b = f * self.x
        mz, mt = self.P["pz"] @ b / self.m["pz"], self.P["pt"] @ b / self.m["pt"]
        c2 = self.chi2(f)
        return {"integral_shift_pct": 100 * float(self.A @ b / (self.A @ self.x)),
                "cell_shift_pct": {"median": 100 * float(np.median(f)), "min": 100 * float(f.min()),
                                   "max": 100 * float(f.max())},
                "pz_marginal_shift_pct": (100 * mz).round(4).tolist(),
                "pt_marginal_shift_pct": (100 * mt).round(4).tolist(),
                "cell_z_max": float(np.max(np.abs(f) / self.sig_cell)),
                "pz_marg_z_max": float(np.max(np.abs(mz) / self.sig_m["pz"])),
                "pt_marg_z_max": float(np.max(np.abs(mt) / self.sig_m["pt"])),
                "chi2_205_pinv": c2["205"], "chi2_pz_marginal": c2["pz"], "chi2_pt_marginal": c2["pt"]}


def step_stat(num, den, met, tn=None, td=None):
    """q_hi/q_lo - 1, q(range) = I(num)/I(den), I = integral of the p_par marginal (covariance-exact projection)
    over the range. With MC truths tn, td (double ratio) q(range) = [I(num)/I(tn)] / [I(den)/I(td)], i.e. data/MC
    of the integrated yields, as the reco proxy R is built from summed yields."""
    e = C.PZ_A
    w = np.diff(e)
    lo = (e[:-1] >= C.STEP_LO[0]) & (e[1:] <= C.STEP_LO[1])
    hi = (e[:-1] >= C.STEP_HI[0]) & (e[1:] <= C.STEP_HI[1])
    P = met.P["pz"]
    I = lambda v, s: float(np.sum((P @ v)[s] * w[s]))  # noqa: E731
    q = (lambda s: I(num, s) / I(den, s)) if tn is None else (lambda s: (I(num, s) / I(tn, s)) / (I(den, s) / I(td, s)))
    return q(hi) / q(lo) - 1.0


def marg_ratio(num, den, met, tn=None, td=None):
    if tn is None:
        return {k: (P @ num / (P @ den) - 1).round(6).tolist() for k, P in met.P.items()}
    return {k: ((P @ num / (P @ tn)) / (P @ den / (P @ td)) - 1).round(6).tolist() for k, P in met.P.items()}


# ------------------------------------------------------------------------------------------------ analysis
def analyze(roles, W, out_json, out_txt, guard=True):
    cells_all = W["cells"]
    R = {"POOL": load(roles["POOL"], cells_all)}
    for X in PER:
        R[X] = {"s42": load(roles[X]["s42"], cells_all), "s43": load(roles[X]["s43"], cells_all) if roles[X].get("s43") else None,
                "boot": [load(p, cells_all) for p in roles[X].get("boot", [])]}
    runs = [R["POOL"]] + [r for X in PER for r in [R[X]["s42"], R[X]["s43"]] + R[X]["boot"] if r is not None]
    if guard:   # PA-02 / PT-G: the period runs' driver and mode; the selftest's synthetic roles are E_U copies
        for r in runs:
            PD.check_mode(r)
    keep = np.ones(cells_all.size, bool)
    for r in runs:
        keep &= (r["x"] > 0) & (r["t"] > 0)
    met = Metric(W, keep)
    k = keep

    def X_(X, kind="s42", q="x"):
        return R[X][kind][q][k]

    x = {X: X_(X) for X in PER}
    x["POOL"] = R["POOL"]["x"][k]
    t = {X: X_(X, q="t") for X in PER}
    t["POOL"] = R["POOL"]["t"][k]
    ipt, _ = C.cell_ipt_ipz(met.cells)
    expo = np.stack([R[X]["s42"]["pot"] * R[X]["s42"]["phi"] for X in PER])            # (3, 14)
    e = {X: (expo[i] / expo.sum(0))[ipt] for i, X in enumerate(PER)}
    potw = {X: R[X]["s42"]["pot"] / sum(R[Y]["s42"]["pot"] for Y in PER) for X in PER}

    # per-period fractional fluctuation draws, for x and for r
    def draws(X, q):
        val = (lambda run: run["x"][k] / run["t"][k]) if q == "r" else (lambda run: run["x"][k])
        b0 = val(R[X]["s42"])
        bd = [val(b) / b0 - 1 for b in R[X]["boot"]]
        sd = val(R[X]["s43"]) / b0 - 1 if R[X]["s43"] is not None else np.zeros_like(b0)
        return bd, sd

    D = {q: {X: draws(X, q) for X in PER} for q in ("x", "r")}
    Kmin = min(len(D["x"][X][0]) for X in PER)

    def noise(coef, q, pooled_seed):
        """coef: {X: per-cell coefficient}. Returns (N_frac, boot draw vectors, seed draw vector)."""
        N = np.zeros((met.cells.size, met.cells.size))
        for X, a in coef.items():
            bd, sd = D[q][X]
            Nb = np.mean([np.outer(d, d) for d in bd], axis=0) if bd else 0.0
            N = N + np.outer(a, a) * (Nb + 0.5 * np.outer(sd, sd))
        bdraws = [sum(a * D[q][X][0][i] for X, a in coef.items()) for i in range(Kmin)]
        sdraw = sum(a * D[q][X][1] for X, a in coef.items()) / np.sqrt(2)
        return N, bdraws, sdraw

    one = np.ones(met.cells.size)
    comps = {}
    # value: (num, den, MC truths (tn, td) or None, noise coefficients, draw quantity, pooled seed enters)
    for q in ("raw", "dr"):
        qq = "x" if q == "raw" else "r"
        tt = (lambda a, b: (t[a], t[b])) if q == "dr" else (lambda a, b: None)  # noqa: E731
        for num, den in (("PB", "PA"), ("PC", "PA"), ("PC", "PB")):
            comps[f"{q}_{num}/{den}"] = (x[num], x[den], tt(num, den), {num: one, den: -one}, qq, False)
        for X in PER:
            coef = {Y: (1 - e[Y]) * one if Y == X else -e[Y] for Y in PER}
            comps[f"{q}_{X}/POOL"] = (x[X], x["POOL"], tt(X, "POOL"), coef, qq, True)
        coef = {Y: (e[Y] - 1) * one if Y == "PA" else e[Y] for Y in PER}
        comps[f"{q}_POOL/PA"] = (x["POOL"], x["PA"], tt("POOL", "PA"), coef, qq, True)
    for X in ("PB", "PC"):
        comps[f"bias_{X}"] = (None, None, None, {X: e[X], "PA": -e[X]}, "x", False)
    out = {"_roles": roles,
           "_inputs": {"work_cov": PD.check_pin("work_cov")},
           "_runs": {rr["path"]:
                     {kk: rr[kk] for kk in ("path", "sha256", "seed", "bootstrap_seed", "omnifile", "mcfile",
                                            "driverSha256", "pot", "n_reported_own")} for rr in runs},
           "cells_used": int(k.sum()), "cells_dropped_nonpositive": int((~k).sum()),
           "n_boot_pairs": Kmin, "exposure_share_by_pt_row": {X: (expo[i] / expo.sum(0)).tolist() for i, X in enumerate(PER)},
           "data_pot_share": potw, "comparisons": {}}
    for name, (num, den, tnd, coef, qq, pooled_seed) in comps.items():
        tn, td = tnd if tnd is not None else (None, None)
        if name.startswith("bias_"):
            X = name[5:]
            f = e[X] * (x[X] / x["PA"] - 1)
        elif tn is None:
            f = num / den - 1
        else:
            f = (num / tn) / (den / td) - 1
        o = met.assess(f)
        Np, bdr, sdr = noise(coef, qq, pooled_seed)
        N = Np + met.Cml_frac if pooled_seed else Np
        o["noise"] = {"expected_chi2": met.expected_chi2(N),
                      "expected_chi2_periods_only": met.expected_chi2(Np),
                      "boot_draw_chi2": [met.chi2(d) for d in bdr],
                      "seed_draw_chi2": met.chi2(sdr),
                      "sigma_cell_pct_median": 100 * float(np.median(np.sqrt(np.diag(N)))),
                      "sigma_pz_marginal_pct": (100 * np.sqrt(np.maximum(np.diag(met.P["pz"] @ (N * np.outer(met.x, met.x)) @ met.P["pz"].T), 0)) / met.m["pz"]).round(4).tolist(),
                      "sigma_pt_marginal_pct": (100 * np.sqrt(np.maximum(np.diag(met.P["pt"] @ (N * np.outer(met.x, met.x)) @ met.P["pt"].T), 0)) / met.m["pt"]).round(4).tolist(),
                      "includes_pooled_seed_C_ML": pooled_seed}
        if num is not None:
            o["marginal_ratio_minus_1"] = marg_ratio(num, den, met, tn, td)
            s0 = step_stat(num, den, met, tn, td)
            sb = [step_stat(num * (1 + d), den, met, tn, td) - s0 for d in bdr]
            ss = step_stat(num * (1 + sdr), den, met, tn, td) - s0
            var = (np.mean(np.square(sb)) if sb else 0.0) + ss ** 2
            o["step"] = {"value": s0, "noise_sigma": float(np.sqrt(var)),
                         "z": float(s0 / np.sqrt(var)) if var > 0 else None,
                         "boot_draws": sb, "seed_draw": ss}
        out["comparisons"][name] = o
    # MC-truth expectation of the period difference, and J36
    for num, den in (("PB", "PA"), ("PC", "PA")):
        f = t[num] / t[den] - 1
        o = met.assess(f)
        o["marginal_ratio_minus_1"] = marg_ratio(t[num], t[den], met)
        o["step"] = {"value": step_stat(t[num], t[den], met)}
        out["comparisons"][f"mc_{num}/{den}"] = o
    for nm, wts in (("J36", e), ("J36_potw", {X: potw[X] * one for X in PER})):
        synth = sum(wts[X] * x[X] for X in PER)
        f = synth / x["POOL"] - 1
        o = met.assess(f)
        Np = sum(np.outer(wts[X], wts[X]) * 0.5 * np.outer(D["x"][X][1], D["x"][X][1]) for X in PER)
        N = Np + met.Cml_frac
        o["noise"] = {"expected_chi2": met.expected_chi2(N), "expected_chi2_periods_only": met.expected_chi2(Np),
                      "what": "seed noise only (periods' s43-s42, pooled C_ML)",
                      "sigma_integral_pct": 100 * float(np.sqrt(met.A @ (N * np.outer(met.x, met.x)) @ met.A) / (met.A @ met.x))}
        o["marginal_ratio_minus_1"] = marg_ratio(synth, x["POOL"], met)
        out["comparisons"][nm] = o
    try:
        rs = json.load(open(REF_SHAPE))
        out["reco_reference_1G-1M_vs_1A-1E"] = {"by_pz": rs["1G-1M_vs_1A-1E"]["by_pz"], "pz_edges": list(C.PZ_P),
                                                "step_pct": 6.10, "source": PD.sha256(REF_SHAPE)}
    except (OSError, KeyError):
        pass
    json.dump(out, open(out_json, "w"), indent=1, default=float)
    lines = [f"period-unfold analysis: {k.sum()} cells used ({(~k).sum()} dropped), {Kmin} bootstrap pairs",
             "comparison            integral%  chi2_205  chi2_pz16  chi2_pT14 | noise E[chi2] 205/pz/pT | step%  sigma%  z"]
    for name, o in out["comparisons"].items():
        n = o.get("noise", {}).get("expected_chi2", {"205": float("nan"), "pz": float("nan"), "pt": float("nan")})
        st = o.get("step", {})
        lines.append(f"{name:22s} {o['integral_shift_pct']:+8.3f} {o['chi2_205_pinv']:9.2f} {o['chi2_pz_marginal']:9.2f} "
                     f"{o['chi2_pt_marginal']:9.2f} | {n.get('205', float('nan')):7.2f} {n.get('pz', float('nan')):6.2f} "
                     f"{n.get('pt', float('nan')):6.2f} | "
                     + (f"{100 * st['value']:+6.2f}" if 'value' in st else "      ")
                     + (f" {100 * st['noise_sigma']:6.2f} {st['z'] if st.get('z') is None else round(st['z'], 2)}"
                        if 'noise_sigma' in st else ""))
    open(out_txt, "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return out


# ------------------------------------------------------------------------------------------------ modes
def roles_from_outdir(outdir):
    p = lambda n: os.path.join(outdir, n, "xsec.root")  # noqa: E731
    ro = {"POOL": p("pu_CTRL_s42")}
    for X in PER:
        ro[X] = {"s42": p(f"pu_{X}_s42"), "s43": p(f"pu_{X}_s43"),
                 "boot": [p(f"pu_{X}_b{i:02d}") for i in range(1, 11) if os.path.isfile(p(f"pu_{X}_b{i:02d}"))]}
    return ro


def control(outdir, out_json):
    sys.path.insert(0, XR_DIR)
    import xr_compare as XR
    refs = json.load(open(f"{XR_DIR}/manifest/references.json"))["references"]
    cells = refs["E_C"]["reported_globalid"]
    new = os.path.join(outdir, "pu_CTRL_s42", "xsec.root")
    res = {"new": {"path": new, "sha256": PD.sha256(new)}, "tolerance": XR.TOL, "comparisons": {}}
    for nm in ("XR_L0", "E_U"):
        ref = PD.check_pin(nm)
        c = XR.compare(new, ref["path"], cells)
        c["ref"] = ref
        res["comparisons"][f"CTRL_vs_{nm}"] = c
    res["verdict"] = "PASS" if all(c["verdict"] == "PASS" for c in res["comparisons"].values()) else "NOT PASS"
    if PD.ARM == "refined":
        res["arm"] = "refined"
    json.dump(res, open(out_json, "w"), indent=1)
    print(json.dumps({kk: {k2: v.get(k2) for k2 in ("verdict", "max_rel_diff_cells", "integral_rel_diff")}
                      for kk, v in res["comparisons"].items()}, indent=1), res["verdict"])
    if PD.ARM == "refined" and res["verdict"] != "PASS":   # PA-05c: the refined control stops
        sys.exit(2)


def selftest(out_json):
    import tempfile
    import ROOT
    W = np.load(PD.PINS["work_cov"][0])
    PD.check_pin("work_cov")
    EU = PD.check_pin("E_U")["path"]
    tests = {}
    # 1. identity: every role is the production CV E_U -> every shift, chi2 and noise is exactly zero
    ro = {"POOL": EU}
    for X in PER:
        ro[X] = {"s42": EU, "s43": EU, "boot": [EU, EU]}
    tmp = tempfile.mkdtemp(dir=f"{PD.NS}/tmp")
    o1 = analyze(ro, W, f"{tmp}/id.json", f"{tmp}/id.txt", guard=False)
    vals = []
    for nm, o in o1["comparisons"].items():
        vals += [o["chi2_205_pinv"], o["chi2_pz_marginal"], o["chi2_pt_marginal"], o["integral_shift_pct"]]
        vals += [o.get("step", {}).get("value", 0.0)]
        vals += list(o.get("noise", {}).get("expected_chi2_periods_only", {}).values())   # C_ML is not from the roles
    chis = [o[kk] for o in o1["comparisons"].values() for kk in ("chi2_205_pinv", "chi2_pz_marginal", "chi2_pt_marginal")]
    # every shift, chi2, step and period-derived noise is exactly 0 except J36, whose sum_X e_X x with e_X = 1/3 can
    # differ from x in the last bit; the pooled-seed C_ML term is not built from the roles and is excluded
    tests["identity_all_zero"] = {"max_abs_any": float(np.max(np.abs(vals))), "max_chi2": float(np.max(chis)),
                                  "n_values": len(vals), "n_exactly_zero": int(np.sum(np.array(vals) == 0.0)),
                                  "nonzero": {nm: o["chi2_205_pinv"] for nm, o in o1["comparisons"].items()
                                              if o["chi2_205_pinv"] != 0.0},
                                  "pass": bool(np.max(np.abs(vals)) <= 1e-12), "cells_used": o1["cells_used"]}
    # 2. injection: P_B = E_U x (1 + g), g = -2% on p_par [1.5, 8), +4% on [8, 15), 0 elsewhere; everything else E_U.
    f = ROOT.TFile.Open(EU)
    hx = f.Get("hXSec2D")
    keys = [kk.GetName() for kk in f.GetListOfKeys()]
    inj = f"{tmp}/inj.root"
    g = ROOT.TFile.Open(inj, "RECREATE")
    for kk in keys:
        obj = f.Get(kk)
        if kk == "hXSec2D":
            obj = hx.Clone("hXSec2D")
            for j in range(1, obj.GetNbinsY() + 1):
                lo, hi = obj.GetYaxis().GetBinLowEdge(j), obj.GetYaxis().GetBinUpEdge(j)
                fac = 0.98 if hi <= 8.0 else (1.04 if (lo >= 8.0 and hi <= 15.0) else 1.0)
                for i in range(1, obj.GetNbinsX() + 1):
                    obj.SetBinContent(i, j, obj.GetBinContent(i, j) * fac)
        g.cd()
        obj.Write(kk)
    g.Close()
    f.Close()
    ro2 = {"POOL": EU, "PA": {"s42": EU, "s43": EU, "boot": [EU]}, "PB": {"s42": inj, "s43": inj, "boot": [inj]},
           "PC": {"s42": EU, "s43": EU, "boot": [EU]}}
    o2 = analyze(ro2, W, f"{tmp}/inj.json", f"{tmp}/inj.txt", guard=False)
    c = o2["comparisons"]["raw_PB/PA"]
    want_step = 1.04 / 0.98 - 1
    cells = W["cells"]
    ipz = cells % C.NPZ
    gv = np.where(C.PZ_A[ipz + 1] <= 8.0, -0.02, np.where((C.PZ_A[ipz] >= 8.0) & (C.PZ_A[ipz + 1] <= 15.0), 0.04, 0.0))
    x = W["EU"].ravel(order="C")[cells]
    Ct = W["cov__hCov_combined"] + W["cov__ML"]
    direct = C.mahalanobis2(gv * x, Ct)[0]
    Pz = C.proj_matrix("pz", cells)
    direct_pz = C.mahalanobis2(Pz @ (gv * x), Pz @ Ct @ Pz.T)[0]
    mr = np.array(c["marginal_ratio_minus_1"]["pz"])
    want_mr = np.array([-0.02 if b <= 8.0 else (0.04 if (a >= 8.0 and b <= 15.0) else 0.0)
                        for a, b in zip(C.PZ_A[:-1], C.PZ_A[1:])])
    tests["injection"] = {"step": c["step"]["value"], "want_step": want_step,
                          "chi2_205": c["chi2_205_pinv"], "direct_chi2_205": direct,
                          "chi2_pz": c["chi2_pz_marginal"], "direct_chi2_pz": direct_pz,
                          "pz_marginal_ratio_maxdiff": float(np.max(np.abs(mr - want_mr))),
                          "noise_zero": o2["comparisons"]["raw_PB/PA"]["noise"]["expected_chi2_periods_only"]["205"] == 0.0,
                          "pass": bool(abs(c["step"]["value"] - want_step) < 1e-12 and abs(c["chi2_205_pinv"] - direct) < 1e-9 * direct
                                       and abs(c["chi2_pz_marginal"] - direct_pz) < 1e-9 * direct_pz
                                       and np.max(np.abs(mr - want_mr)) < 1e-12)}
    tests["verdict"] = "PASS" if all(v["pass"] for v in tests.values() if isinstance(v, dict)) else "FAIL"
    json.dump(tests, open(out_json, "w"), indent=1)
    print(json.dumps(tests, indent=1))
    return tests


def parse_arm(argv):
    """Strip [--arm refined --work-cov PATH SHA256] [--ns DIR] from argv and set the pins; returns the rest."""
    argv = list(argv)
    arm, wc, ns = "purity", None, None
    if "--arm" in argv:
        i = argv.index("--arm")
        arm = argv[i + 1]
        del argv[i:i + 2]
    if "--work-cov" in argv:
        i = argv.index("--work-cov")
        wc = (argv[i + 1], argv[i + 2])
        del argv[i:i + 3]
    if "--ns" in argv:
        i = argv.index("--ns")
        ns = argv[i + 1]
        del argv[i:i + 2]
    PD.set_arm(arm, work_cov=wc, ns=ns)
    return argv


if __name__ == "__main__":
    sys.argv[1:] = parse_arm(sys.argv[1:])
    mode = sys.argv[1]
    if mode == "control":
        control(sys.argv[2], sys.argv[3])
    elif mode == "roles":
        json.dump(roles_from_outdir(sys.argv[2]), open(sys.argv[3], "w"), indent=1)
    elif mode == "analyze":
        PD.check_pin("work_cov")
        analyze(json.load(open(sys.argv[2])), np.load(PD.PINS["work_cov"][0]), sys.argv[3], sys.argv[4])
    elif mode == "selftest":
        sys.exit(0 if selftest(sys.argv[2])["verdict"] == "PASS" else 1)
    else:
        sys.exit(__doc__)
