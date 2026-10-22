#!/usr/bin/env python3
"""KI 98 W-bias confirming test: the reader of DECLARATION.md (read-only; no unfold).

    existing  per-functional means and SDs of the 400 existing Tier-S tilt products (seeds 204000-204399) and,
              beside them, the 400 nominal ones (200000-200399): raw relative bias e = f_hat/f_true - 1 and the
              corrected residual rho = (f_hat/(1+beta) - f_true)/sigma, for the 153 reported functionals and the
              declared band aggregates
    analyze   the new arms (b) tilt without background, (b0) nominal without background, (c) tilt with the
              background x0.9, against arm (a) = the existing tilt products on the same five seeds; the control
              (arm (a) seed 204000 re-run, bitwise); product checks; the declared decision rule
Run with the s5c deploy's nd-unfolding importable (s5c_coverage, project_cov_nd).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

import project_cov_nd as pc
import s5c_coverage as cov

AXES = ["pt", "pz", "eavail", "q3", "W"]
SEEDS = list(range(204000, 204005))
K_T4 = 2.776          # two-sided 95% Student t, 4 degrees of freedom (five seeds)
PRIMARY = "band_EW_W_ge_3"
SECONDARY = "band_EW_W_2.2_3"
NAMED = ["EW9", "EW10", "EW16", "EW17", "J116", "J224", "total_integrated", "EW_all_ones"]
CODE = {"s5c_pseudo.py": "e423aaaeef1f0c938e9ac53c955eb0e58bb6b29f1680eac4ba33d4d73e7e4820",
        "s5c_unfold.py": "510d749a2e82fa448de6172753ae2adc9ebd81a89d4f18bf76beb5faa8bb3968"}


def sha256(p) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def split_key_for(seed: int) -> int:
    return (seed * 0x9E3779B1 + 0x5C5C) % (2**61 - 1)   # s5c_pseudo.split_key_for, 4bdfa75e


def bands(contract: dict, names: list[str]) -> dict[str, list[int]]:
    """Declared band aggregates: EW cells by truth-W bin (EW index k = 6 * e + w, W edges of project_cov_nd);
    J cells whose coarse W lower edge is >= 2.2 GeV."""
    we = pc.AXIS_EDGES["W"]
    ew = {k: k % 6 for k in range(42)}
    out = {"band_EW_W_lt_1.4": [k for k, w in ew.items() if we[w + 1] <= 1.4],
           "band_EW_W_1.4_2.2": [k for k, w in ew.items() if we[w] >= 1.4 and we[w + 1] <= 2.2],
           SECONDARY: [k for k, w in ew.items() if we[w] == 2.2 and we[w + 1] == 3.0],
           PRIMARY: [k for k, w in ew.items() if we[w] >= 3.0]}
    J = contract["measurement"]["partition_J"]
    cshape = tuple(len(J["edges"][ax]) - 1 for ax in AXES)
    jw = np.asarray(J["edges"]["W"], float)
    out["band_J_W_ge_2.2"] = [names.index(f"J{c}") for c in J["supported_cells"]
                              if jw[np.unravel_index(c, cshape)[4]] >= 2.2]
    return out


class Setup:
    def __init__(self, a):
        self.contract = json.loads(a.contract.read_text())
        U, names = cov.reported_functionals(self.contract)
        self.names = names
        self.bands = bands(self.contract, names)
        rows = [U] + [U[idx].sum(0, keepdims=True) for idx in self.bands.values()]
        Uall = np.vstack(rows)
        self.U = U
        C = cov.stat_covariance(Uall, a.bootstrap, 1, 200)
        self.sigma_all = np.sqrt(np.diag(C))
        rec = json.loads(a.interim.read_text())
        if rec["functional_names"] != names:
            raise SystemExit("interim functional order differs")
        s0 = np.asarray(rec["sigma"], float)
        self.sigma_check = float(np.max(np.abs(self.sigma_all[: len(names)] - s0) / s0))
        if self.sigma_check > 1e-9:
            raise SystemExit(f"recomputed sigma differs from interim_400.json by {self.sigma_check:.3g} (relative)")
        bc = json.loads(a.bias_correction.read_text())
        if bc["functional_names"] != names:
            raise SystemExit("bias correction functional order differs")
        self.beta = np.asarray(bc["beta"], float)
        self.se = np.asarray(bc["se"], float)
        self.digests = {"contract": sha256(a.contract), "interim": sha256(a.interim),
                        "bias_correction": sha256(a.bias_correction)}
        self.all_names = names + list(self.bands)

    def residuals(self, fh: np.ndarray, ft: np.ndarray, beta: np.ndarray) -> np.ndarray:
        """rho over the 153 functionals and the band aggregates (corrected per cell, then summed)."""
        fc = fh / (1.0 + beta)
        num = list(fc - ft) + [fc[idx].sum() - ft[idx].sum() for idx in self.bands.values()]
        return np.asarray(num) / self.sigma_all

    def raw(self, fh, ft) -> np.ndarray:
        num = list(fh) + [fh[idx].sum() for idx in self.bands.values()]
        den = list(ft) + [ft[idx].sum() for idx in self.bands.values()]
        num, den = np.asarray(num), np.asarray(den)
        return np.where(den != 0, num / np.where(den != 0, den, 1.0) - 1.0, np.nan)

    def beta_se_term(self, ft_mean: np.ndarray) -> np.ndarray:
        """The correction's own SE in sigma units, fully correlated within a band (conservative)."""
        t = self.se * np.abs(ft_mean) / (1.0 + self.beta)
        return np.asarray(list(t) + [t[idx].sum() for idx in self.bands.values()]) / self.sigma_all

    def load(self, p: Path):
        z = np.load(p, allow_pickle=False)
        return self.U @ z["xsec_flat"], self.U @ z["xtrue_flat"], json.loads(str(z["meta"])), z


def summarize(x: np.ndarray) -> dict:
    n = x.shape[0]
    sd = x.std(0, ddof=1)
    return {"n": n, "mean": x.mean(0), "sd": sd, "se": sd / np.sqrt(n)}


def table(names, **cols) -> dict:
    return {nm: {k: (None if not np.isfinite(v[i]) else float(v[i])) for k, v in cols.items()}
            for i, nm in enumerate(names)}


def cmd_existing(a) -> int:
    S = Setup(a)
    out = {"schema": "ki98-existing/1", "digests": S.digests, "sigma_recompute_max_rel_diff": S.sigma_check,
           "bands": {k: [S.names[i] for i in v] for k, v in S.bands.items()}, "grid": {}}
    for tag, first in (("eavail_tilt_a0.2", 204000), ("nominal_a0", 200000)):
        rho, e = [], []
        for s in range(first, first + 400):
            fh, ft, _, _ = S.load(a.valid / f"{tag}_s{s}.npz")
            rho.append(S.residuals(fh, ft, S.beta))
            e.append(S.raw(fh, ft))
        R, E = summarize(np.array(rho)), summarize(np.array(e))
        out["grid"][tag] = {"seeds": [first, first + 399],
                            "functionals": table(S.all_names, rho_mean=R["mean"], rho_se=R["se"], rho_sd=R["sd"],
                                                 e_mean=E["mean"], e_sd=E["sd"])}
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    for nm in NAMED + list(S.bands):
        t, n = out["grid"]["eavail_tilt_a0.2"]["functionals"][nm], out["grid"]["nominal_a0"]["functionals"][nm]
        print(f"{nm:20s} tilt rho {t['rho_mean']:+.3f} ({t['rho_se']:.3f}) sd {t['rho_sd']:.2f} e {t['e_mean']:+.4%}"
              f" | nominal rho {n['rho_mean']:+.3f} ({n['rho_se']:.3f}) sd {n['rho_sd']:.2f} e {n['e_mean']:+.4%}")
    return 0


def check_product(meta, arm, seed, bkg_sha):
    want = {"a": ("eavail_tilt", 0.2, False), "b": ("eavail_tilt", 0.2, True),
            "b0": ("nominal", 0.0, True), "c": ("eavail_tilt", 0.2, False)}[arm]
    bad = []
    if (meta["truth"], float(meta["amplitude"]), bool(meta["no_background"])) != want:
        bad.append("truth/amplitude/no_background")
    if meta["pseudo_seed"] != seed or meta["split_key"] != split_key_for(seed):
        bad.append("seed/split_key")
    if meta["config"] != "deterministic" or meta["estimator_seed"] != 42 or meta["iters"] != 5 or meta["threads"] != 32:
        bad.append("config")
    if meta["code_sha256"] != CODE:
        bad.append("code_sha256")
    if meta["bkg_dump_sha256"] != bkg_sha:
        bad.append("bkg_dump_sha256")
    return bad


def cmd_analyze(a) -> int:
    S = Setup(a)
    bkg09 = sha256(a.bkg09)
    res = {"schema": "ki98-analyze/1", "digests": {**S.digests, "bkg09": bkg09}, "failures": [], "products": {}}
    fail = res["failures"]
    arms = {}
    for arm, prefix, bkg_sha in (("b", "ki98_b_tilt_nobkg", a.bkg_sha256), ("b0", "ki98_b0_nom_nobkg", a.bkg_sha256),
                                 ("c", "ki98_c_tilt_bkg09", bkg09)):
        fhs, fts = [], []
        for s in SEEDS:
            p = a.unf / f"{prefix}_s{s}.npz"
            if not p.is_file():
                fail.append(f"{p.name} missing")
                continue
            fh, ft, meta, z = S.load(p)
            bad = check_product(meta, arm, s, bkg_sha)
            if not (np.isfinite(z["xsec_flat"]).all() and np.isfinite(z["xtrue_flat"]).all()):
                bad.append("non-finite")
            if bad:
                fail.append(f"{p.name}: {bad}")
            res["products"][p.name] = {"sha256": sha256(p), "experiment": meta["experiment"], "slurm_job": meta["slurm_job"]}
            fhs.append(fh)
            fts.append(ft)
        arms[arm] = (np.array(fhs), np.array(fts))
    fha, fta = [], []
    for s in SEEDS:
        fh, ft, meta, _ = S.load(a.valid / f"eavail_tilt_a0.2_s{s}.npz")
        if check_product(meta, "a", s, a.bkg_sha256):
            fail.append(f"existing s{s}: {check_product(meta, 'a', s, a.bkg_sha256)}")
        fha.append(fh)
        fta.append(ft)
    arms["a"] = (np.array(fha), np.array(fta))
    # control: arm (a) seed 204000 re-run in single-experiment mode, bitwise against the existing product
    zc = np.load(a.unf / "ki98_ctl_a_s204000.npz", allow_pickle=False)
    ze = np.load(a.valid / "eavail_tilt_a0.2_s204000.npz", allow_pickle=False)
    ctl = {k: bool(np.array_equal(zc[k], ze[k])) for k in ("xsec_flat", "xtrue_flat", "shape")}
    ctl["meta_checks"] = check_product(json.loads(str(zc["meta"])), "a", 204000, a.bkg_sha256)
    res["control"] = {**ctl, "pass": all(ctl[k] for k in ("xsec_flat", "xtrue_flat", "shape")) and not ctl["meta_checks"]}
    if not res["control"]["pass"]:
        fail.append("control")
    if fail:
        res["verdict"] = "INCOMPLETE"
        a.out.write_text(json.dumps(res, indent=1, default=str) + "\n")
        print(json.dumps({"verdict": res["verdict"], "failures": fail}, indent=1))
        return 1
    # truths: (a), (b) and (c) share each seed's truth exactly (same split key, same reweight)
    res["truth_shared"] = {arm: bool(np.array_equal(arms[arm][1], arms["a"][1])) for arm in ("b", "c")}
    # beta references: d1 (nominal, with background) for (a) and (c); the five-seed nominal no-background mean for (b)
    e_b0 = np.array([S.raw(fh, ft)[: len(S.names)] for fh, ft in zip(*arms["b0"])])
    beta_nb = np.nan_to_num(e_b0.mean(0), nan=0.0)
    rho = {"a": np.array([S.residuals(fh, ft, S.beta) for fh, ft in zip(*arms["a"])]),
           "c": np.array([S.residuals(fh, ft, S.beta) for fh, ft in zip(*arms["c"])]),
           "b": np.array([S.residuals(fh, ft, beta_nb) for fh, ft in zip(*arms["b"])]),
           "b0": np.array([S.residuals(fh, ft, beta_nb) for fh, ft in zip(*arms["b0"])])}
    sb = S.beta_se_term(arms["a"][1].mean(0))
    n = len(SEEDS)
    v = {k: x.var(0, ddof=1) / n for k, x in rho.items()}
    stat = {
        "R_a": rho["a"].mean(0), "SE_a": np.sqrt(v["a"] + sb ** 2),
        "R_c": rho["c"].mean(0), "SE_c": np.sqrt(v["c"] + sb ** 2),
        "R_b": rho["b"].mean(0), "SE_b": np.sqrt(v["b"] + v["b0"]),
        "D_c": (rho["a"] - rho["c"]).mean(0), "SE_Dc": np.sqrt((rho["a"] - rho["c"]).var(0, ddof=1) / n),
        "D_b": (rho["a"] - rho["b"]).mean(0), "SE_Db": np.sqrt((rho["a"] - rho["b"]).var(0, ddof=1) / n + v["b0"]),
        "beta_se_term": sb,
    }
    res["functionals"] = table(S.all_names, **stat)
    res["k"] = K_T4

    def rule(i: int) -> dict:
        g = {x: float(stat[x][i]) for x in stat}
        present = g["R_a"] > K_T4 * g["SE_a"]
        c_bs = abs(g["R_c"]) <= K_T4 * g["SE_c"] and g["D_c"] > K_T4 * g["SE_Dc"]
        c_est = abs(g["D_c"]) <= K_T4 * g["SE_Dc"] and g["R_c"] > K_T4 * g["SE_c"]
        b_bs = abs(g["R_b"]) <= K_T4 * g["SE_b"] and g["D_b"] > K_T4 * g["SE_Db"]
        b_est = abs(g["D_b"]) <= K_T4 * g["SE_Db"] and g["R_b"] > K_T4 * g["SE_b"]
        if not present:
            verdict = "UNDETERMINED (the residual is not resolved in arm (a) on these five seeds)"
        elif c_bs and not b_est:
            verdict = "B/S CHANGE"
        elif c_est and not b_bs:
            verdict = "ESTIMATOR"
        else:
            verdict = "UNDETERMINED"
        return {"present_in_a": present, "c_BS_pattern": c_bs, "c_estimator_pattern": c_est,
                "b_BS_pattern": b_bs, "b_estimator_pattern": b_est, "verdict": verdict, **g}

    res["decision"] = {"primary": {"functional": PRIMARY, **rule(S.all_names.index(PRIMARY))},
                       "secondary": {"functional": SECONDARY, **rule(S.all_names.index(SECONDARY))}}
    res["verdict"] = res["decision"]["primary"]["verdict"]
    a.out.write_text(json.dumps(res, indent=1, default=str) + "\n")
    print(json.dumps({"verdict": res["verdict"], "control": res["control"], "truth_shared": res["truth_shared"],
                      "primary": res["decision"]["primary"], "secondary": res["decision"]["secondary"]}, indent=1))
    for nm in NAMED + list(S.bands):
        r = res["functionals"][nm]
        print(f"{nm:20s} R_a {r['R_a']:+.2f}({r['SE_a']:.2f}) R_c {r['R_c']:+.2f}({r['SE_c']:.2f}) "
              f"R_b {r['R_b']:+.2f}({r['SE_b']:.2f}) D_c {r['D_c']:+.2f}({r['SE_Dc']:.2f}) D_b {r['D_b']:+.2f}({r['SE_Db']:.2f})")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("cmd", choices=("existing", "analyze"))
    ap.add_argument("--contract", type=Path, required=True)
    ap.add_argument("--interim", type=Path, required=True)
    ap.add_argument("--bias-correction", type=Path, required=True)
    ap.add_argument("--bootstrap", type=Path, required=True)
    ap.add_argument("--valid", type=Path, required=True, help="the Tier-S validation products")
    ap.add_argument("--unf", type=Path, help="analyze: the new products")
    ap.add_argument("--bkg-sha256", help="analyze: the original background dump's sha256")
    ap.add_argument("--bkg09", type=Path, help="analyze: the scaled background dump")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    return cmd_existing(a) if a.cmd == "existing" else cmd_analyze(a)


if __name__ == "__main__":
    sys.exit(main())
