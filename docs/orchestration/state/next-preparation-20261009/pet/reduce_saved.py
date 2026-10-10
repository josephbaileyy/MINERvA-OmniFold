"""Variance components, bias and coverage of the PET H2S1T24 K5 procedure from saved scores only.

Reads committed per-run score files of the PET final-design study (no training, no new runs, no
FB/RB row access beyond the already-scored, already-unblinded histograms):

* S5 coverage members  ``results/final/scored_s5c/S5-H2S1T24K5-FB<r>-b<m>``: 120 replicates x B = 6
  Poisson(1)-bootstrap members, each with its own estimator seeds (PROTOCOL section 9, Amendment 2c);
* S4F FINAL single fits ``results/final/scored_fb/S4F-H2S1T24K5-FB<r>``: 60 replicates, one
  unbootstrapped fit each, its own estimator seed, identical estimator configuration otherwise;
* S-N2 seed repeats   ``results/s3n/S3P-H2S1T24K5-DEV<d>[-s<i>]``: two DEV draws x four seeds at
  fixed events and nominal weights;
* S4S library single fits (eight FB draws per case) for the bias of the generator/stress cases.

Model per histogram bin (unit-normalized, k = 5), for replicate r and bootstrap member b:

    member_rb = mu + D_r + P_rb + T_rb,        single_r = mu1 + D_r + T_r

D_r is the replicate's event-sample effect (pseudodata and prior draw), P_rb the Poisson-reweighting
effect, T_rb the training/validation-split randomness. Then

    W  = E[within-replicate member variance]      = s_P^2 + s_T^2
    V  = Var_r(member mean)                         = s_D^2 + W / B
    V1 = Var_r(single fit)                          = s_D^2 + s_T^2

so s_D^2 = V - W/B, s_T^2 = V1 - s_D^2 and s_P^2 = W - s_T^2 are identified from the saved design
(s_T^2 also directly, on DEV, from the S-N2 seed repeats). These are study-scale quantities
conditional on the frozen banks (PROTOCOL section 3).

    python reduce_saved.py --out results/saved_reductions.json
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import re
import sys
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import numpy as np  # noqa: E402
from scipy import stats  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
FD = REPO / "nd-unfolding/pet/final_design"
CAND = "H2S1T24K5"
K = 5
B = 6
HISTS = ("eavail", "eavail@low_acceptance", "eavail@moderate", "eavail@good")
LEVELS = (0.68, 0.95)
N_BOOT = 2000
BOOT_SEED = 20261009
LIBRARY_CASES = ("null", "D1_p0.175", "D1_p0.350", "D1_m0.700", "D1_p0.350XD4c_p_up", "D2_bump_c0.3",
                 "D2_bump_c1.0", "D3_p0.35", "D3_m0.35", "D4a_pipm_up", "D4b_pi0_up", "D4c_p_up", "D4c_p_down",
                 "D4d_n_up", "D4d_n_down", "D5_nuwro", "D5p_nuwro", "D5_gibuu", "R1_x1.05_D1_p0.350",
                 "R1_x0.95_D1_p0.350", "R2_x1.01_D1_p0.350")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def completeness(tsv: Path) -> dict[str, str]:
    """run name -> receipt sha256 from a committed completeness record."""
    out = {}
    with tsv.open() as fh:
        lines = list(csv.reader(fh, delimiter="\t"))
    if lines[0] != ["# manifest", "row", "status", "receipt_sha256"]:
        raise SystemExit(f"{tsv.name}: unexpected header {lines[0]}")
    for r in lines[1:]:
        if not r or r[0].startswith("#"):
            continue
        if r[2] != "COMPLETE":
            raise SystemExit(f"{tsv.name}: {r[1]} is {r[2]}")
        if r[1] in out:
            raise SystemExit(f"{tsv.name}: duplicate row {r[1]}")
        out[r[1]] = r[3]
    return out


def iteration(doc: dict, k: int) -> dict:
    for it in doc["iterations"]:
        if it["k"] == k and it.get("histograms") is not None:
            return it
    raise SystemExit(f"{doc['run_name']}: k={k} not scored")


class Ledger:
    """Every operand file read, with its digest, so the reduction is bound to its inputs."""

    def __init__(self) -> None:
        self.files: dict[str, str] = {}

    def load(self, path: Path) -> dict:
        self.files[str(path.relative_to(REPO))] = sha256(path)
        return json.loads(path.read_text())

    def digest(self) -> str:
        h = hashlib.sha256()
        for k in sorted(self.files):
            h.update(f"{k}\t{self.files[k]}\n".encode())
        return h.hexdigest()


def load_s5(led: Ledger) -> dict:
    receipts = completeness(FD / "freeze/COMPLETENESS-s5c_a5_H2S1T24.tsv")
    led.files[str((FD / "freeze/COMPLETENESS-s5c_a5_H2S1T24.tsv").relative_to(REPO))] = sha256(
        FD / "freeze/COMPLETENESS-s5c_a5_H2S1T24.tsv")
    pat = re.compile(rf"^S5-{CAND}-FB(\d+)-b(\d)$")
    reps: dict[int, dict[int, str]] = {}
    for name in receipts:
        m = pat.match(name)
        if not m:
            raise SystemExit(f"unexpected completeness row {name}")
        reps.setdefault(int(m[1]), {})[int(m[2])] = name
    out = {h: {"members": [], "target": [], "pop": [], "prior": []} for h in HISTS}
    seeds = []
    for r in sorted(reps):
        if sorted(reps[r]) != list(range(1, B + 1)):
            raise SystemExit(f"FB{r}: members {sorted(reps[r])}")
        docs = []
        for b in range(1, B + 1):
            name = reps[r][b]
            d = led.load(FD / f"results/final/scored_s5c/{name}.design_scores.json")
            if d["provenance"]["receipt_sha256"] != receipts[name]:
                raise SystemExit(f"{name}: receipt digest differs from completeness record")
            if d["case"]["case"] != "D1_p0.350":
                raise SystemExit(f"{name}: case {d['case']['case']}")
            docs.append(d)
        idn = [d["identity"] for d in docs]
        if len({i["pseudo_rows_sha256"] for i in idn}) != 1 or len({i["prior_rows_sha256"] for i in idn}) != 1:
            raise SystemExit(f"FB{r}: members differ in rows")
        bs = [i["bootstrap"]["seed"] for i in idn]
        if len(set(bs)) != 1 or len({i["bootstrap"]["member"] for i in idn}) != B:
            raise SystemExit(f"FB{r}: bootstrap seed/member structure unexpected")
        seeds.append(bs[0])
        for h in HISTS:
            its = [iteration(d, K)["histograms"][h] for d in docs]
            t = np.array([x["target_norm"] for x in its])
            if np.abs(t - t[0]).max() > 1e-12:
                raise SystemExit(f"FB{r} {h}: member targets differ")
            pops = [iteration(d, K)["vs_population"][h]["target_norm"] for d in docs]
            out[h]["members"].append([x["unfolded_norm"] for x in its])
            out[h]["prior"].append([x["prior_norm"] for x in its])
            out[h]["target"].append(t[0])
            out[h]["pop"].append(pops[0])
    if len(set(seeds)) != len(seeds):
        raise SystemExit("bootstrap seeds repeat across replicates")
    return {h: {k: np.asarray(v, np.float64) for k, v in out[h].items()} for h in HISTS} | {
        "_replicates": sorted(reps)}


def load_single(led: Ledger, stem: str, reps: list[int], subdir: str) -> dict:
    out = {h: {"single": [], "target": [], "pop": [], "prior": [], "R_committed": []} for h in HISTS}
    seeds = []
    for r in reps:
        d = led.load(FD / f"results/final/{subdir}/{stem.format(r=r)}.design_scores.json")
        if d["identity"].get("bootstrap") is not None:
            raise SystemExit(f"{d['run_name']}: unexpectedly bootstrapped")
        it = iteration(d, K)
        seeds.append(d["identity"]["config_hash"])
        for h in HISTS:
            x = it["histograms"][h]
            out[h]["single"].append(x["unfolded_norm"])
            out[h]["prior"].append(x["prior_norm"])
            out[h]["R_committed"].append(x["recovery_raw"])
            out[h]["target"].append(x["target_norm"])
            vp = it.get("vs_population", {}).get(h)
            out[h]["pop"].append(vp["target_norm"] if vp else [np.nan] * len(x["target_norm"]))
    if len(set(seeds)) != len(seeds):
        raise SystemExit(f"{stem}: config hashes (seeds) repeat")
    return {h: {k: np.asarray(v, np.float64) for k, v in out[h].items()} for h in HISTS}


def check_s4f_receipts(reps: list[int], look1: dict[str, str]) -> None:
    for r in reps:
        p = FD / f"results/final/scored_fb/S4F-{CAND}-FB{r}.design_scores.json"
        if json.loads(p.read_text())["provenance"]["receipt_sha256"] != look1[f"S4F-{CAND}-FB{r}"]:
            raise SystemExit(f"S4F FB{r}: receipt digest differs from completeness record")


def load_sn2(led: Ledger) -> dict:
    """Two DEV draws x four seeds (nominal + s1..s3) at fixed events: (2, 4, nbins)."""
    out = {h: [] for h in HISTS}
    for dv in (0, 1):
        per = {h: [] for h in HISTS}
        rows = set()
        for sfx in ("", "-s1", "-s2", "-s3"):
            d = led.load(FD / f"results/s3n/S3P-{CAND}-DEV{dv}{sfx}.design_scores.json")
            rows.add((d["identity"]["prior_rows_sha256"], d["identity"]["pseudo_rows_sha256"]))
            it = iteration(d, K)
            for h in HISTS:
                per[h].append(it["histograms"][h]["unfolded_norm"])
        if len(rows) != 1:
            raise SystemExit(f"S-N2 DEV{dv}: seed runs differ in events")
        for h in HISTS:
            out[h].append(per[h])
    return {h: np.asarray(v, np.float64) for h, v in out.items()}


# ------------------------------------------------------------------------------------------- #
def components(mem: np.ndarray, single: np.ndarray) -> dict[str, np.ndarray]:
    """Per-bin moment estimators of the model in the module docstring."""
    W = mem.var(axis=1, ddof=1).mean(axis=0)
    V = mem.mean(axis=1).var(axis=0, ddof=1)
    V1 = single.var(axis=0, ddof=1)
    sD2 = V - W / B
    sT2 = V1 - sD2
    sP2 = W - sT2
    return {"W": W, "V": V, "V1": V1, "sD2": sD2, "sT2": sT2, "sP2": sP2}


def boot_components(mem: np.ndarray, single: np.ndarray, rng: np.random.Generator) -> dict:
    """Replicate-cluster bootstrap (S5 and S4F resampled independently): 16/50/84 and 2.5/97.5 %."""
    R, R1 = mem.shape[0], single.shape[0]
    draws = {k: [] for k in ("W", "V", "V1", "sD2", "sT2", "sP2", "sT2_over_W", "sP2_over_sD2", "V1_over_W",
                             "g_sD2_over_W_per_B")}
    for _ in range(N_BOOT):
        c = components(mem[rng.integers(0, R, R)], single[rng.integers(0, R1, R1)])
        for k in ("W", "V", "V1", "sD2", "sT2", "sP2"):
            draws[k].append(c[k])
        with np.errstate(divide="ignore", invalid="ignore"):
            draws["sT2_over_W"].append(c["sT2"] / c["W"])
            draws["sP2_over_sD2"].append(c["sP2"] / c["sD2"])
            draws["V1_over_W"].append(c["V1"] / c["W"])
            draws["g_sD2_over_W_per_B"].append(c["sD2"] / (c["W"] / B))
    q = (2.5, 16, 50, 84, 97.5)
    return {k: {f"p{p}": np.nanpercentile(np.asarray(v), p, axis=0).tolist() for p in q}
            for k, v in draws.items()}


def tq(level: float, dof: int) -> float:
    return float(stats.t.ppf(0.5 + level / 2.0, dof))


def coverage(mem: np.ndarray, target: np.ndarray, var_override: np.ndarray | None = None) -> dict:
    """Section-9 interval (mean +- t(B-1) sd sqrt(1+1/B)); or, if `var_override` (R, nbins) is given,
    mean +- t(B-1) sqrt(var_override). Per bin and pooled; misses split by side."""
    est = mem.mean(axis=1)
    sd = mem.std(axis=1, ddof=1)
    dev = est - target
    out = {}
    for L in LEVELS:
        if var_override is None:
            hw = tq(L, B - 1) * sd * math.sqrt(1 + 1 / B)
        else:
            hw = tq(L, B - 1) * np.sqrt(np.clip(var_override, 0, None))
        hit = np.abs(dev) <= hw
        # design effect of pooling the bins of one replicate: variance of the replicate means of
        # the hit indicators relative to independent Bernoulli cells
        p, nb = float(hit.mean()), hit.shape[1]
        deff = float(hit.mean(axis=1).var(ddof=1) / (p * (1 - p) / nb)) if 0 < p < 1 else None
        out[f"{L:.2f}"] = {"per_bin": hit.mean(axis=0).tolist(), "pooled": p, "design_effect": deff,
                           "miss_high_pooled": float((dev > hw).mean()),
                           "miss_low_pooled": float((dev < -hw).mean()),
                           "mean_half_width": hw.mean(axis=0).tolist()}
    return out


def recovery(u: np.ndarray, t: np.ndarray, p: np.ndarray) -> np.ndarray:
    """Historical R = 1 - L1(u - t) / L1(p - t) per replicate (unit-normalized rows)."""
    return 1.0 - np.abs(u - t).sum(axis=1) / np.abs(p - t).sum(axis=1)


def recovery_summary(est, t, p, single, t1, p1, r_committed) -> dict:
    """R of the six-member mean (S5) against R of the single fit (S4F), with the S4F recomputation
    checked against the committed `recovery_raw`."""
    r5, r4 = recovery(est, t, p), recovery(single, t1, p1)
    rc = np.asarray(r_committed, np.float64)
    return {"member_mean_R": {"mean": float(r5.mean()), "sd": float(r5.std(ddof=1)), "n": int(r5.size)},
            "single_fit_R": {"mean": float(r4.mean()), "sd": float(r4.std(ddof=1)), "n": int(r4.size)},
            "single_fit_R_recomputed_max_abs_diff_vs_committed": float(np.abs(r4 - rc).max())}


def skew(x: np.ndarray, axis: int = 0) -> np.ndarray:
    return stats.skew(x, axis=axis, bias=False)


def reduce_hist(h: str, s5: dict, s4f: dict, sn2: np.ndarray, rng: np.random.Generator) -> dict:
    mem, t, pop = s5[h]["members"], s5[h]["target"], s5[h]["pop"]
    single, t1, pop1 = s4f[h]["single"], s4f[h]["target"], s4f[h]["pop"]
    est = mem.mean(axis=1)
    sd = mem.std(axis=1, ddof=1)
    e_own, e_pop = est - t, est - pop
    e1_own, e1_pop = single - t1, single - pop1
    comp = components(mem, single)
    # S-N2: pooled within-draw seed variance at fixed events (2 draws x 3 dof)
    sT2_sn2 = sn2.var(axis=1, ddof=1).mean(axis=0)
    # truth tracking: does the estimate follow the replicate's own truth fluctuation?
    dt = t - pop
    with np.errstate(divide="ignore", invalid="ignore"):
        slope = ((e_pop - e_pop.mean(0)) * (dt - dt.mean(0))).mean(0) / dt.var(0)
    pull = e_own / (sd * math.sqrt(1 + 1 / B))
    res = {
        "n_replicates_s5": int(mem.shape[0]), "n_replicates_s4f": int(single.shape[0]),
        "components": {k: v.tolist() for k, v in comp.items()},
        "components_bootstrap": boot_components(mem, single, rng),
        "sT2_sn2_dev": sT2_sn2.tolist(), "sT2_sn2_dof": int(sn2.shape[0] * (sn2.shape[1] - 1)),
        "member_mean": {
            "bias_own": e_own.mean(0).tolist(), "bias_own_se": (e_own.std(0, ddof=1) / math.sqrt(len(e_own))).tolist(),
            "bias_pop": e_pop.mean(0).tolist(), "bias_pop_se": (e_pop.std(0, ddof=1) / math.sqrt(len(e_pop))).tolist(),
            "rms_own": np.sqrt((e_own ** 2).mean(0)).tolist(), "sd_own": e_own.std(0, ddof=1).tolist(),
            "rms_pop": np.sqrt((e_pop ** 2).mean(0)).tolist(), "sd_pop": e_pop.std(0, ddof=1).tolist(),
            "bias2_over_mse_own": (e_own.mean(0) ** 2 / (e_own ** 2).mean(0)).tolist(),
            "abs_bias_over_sd_own": (np.abs(e_own.mean(0)) / e_own.std(0, ddof=1)).tolist(),
            "member_sd_rms": np.sqrt((sd ** 2).mean(0)).tolist(),
            "member_sd_over_rms_own": (np.sqrt((sd ** 2).mean(0)) / np.sqrt((e_own ** 2).mean(0))).tolist(),
            "skew_error_own": skew(e_own).tolist(),
            "skew_within_members_mean": skew(mem, axis=1).mean(0).tolist(),
            "pull_mean": pull.mean(0).tolist(), "pull_sd": pull.std(0, ddof=1).tolist(),
        },
        "single_fit": {
            "bias_own": e1_own.mean(0).tolist(), "bias_own_se": (e1_own.std(0, ddof=1) / math.sqrt(len(e1_own))).tolist(),
            "rms_own": np.sqrt((e1_own ** 2).mean(0)).tolist(), "sd_own": e1_own.std(0, ddof=1).tolist(),
            "bias_pop": (e1_pop.mean(0).tolist() if np.isfinite(e1_pop).all() else None),
        },
        "recovery": recovery_summary(est, t, s5[h]["prior"].mean(axis=1), single, t1, s4f[h]["prior"],
                                     s4f[h]["R_committed"]),
        "member_mean_minus_single_fit_bias": {
            "diff": (e_own.mean(0) - e1_own.mean(0)).tolist(),
            "se": np.sqrt(e_own.var(0, ddof=1) / len(e_own) + e1_own.var(0, ddof=1) / len(e1_own)).tolist(),
            "note": "E[member mean] - E[single fit], both against own truth, from different FB draws of the same "
                    "bank; a bootstrap bias correction 2 x single - mean(members) moves the bias by -diff"},
        "own_truth_vs_population": {
            "sd_target_minus_pop": dt.std(0, ddof=1).tolist(),
            "slope_est_minus_pop_on_target_minus_pop": slope.tolist(),
        },
        "coverage_section9_own": coverage(mem, t),
        "coverage_section9_pop": coverage(mem, pop),
    }
    # diagnostic (in-sample, NOT a validated interval): the section-9 variance with the training term
    # replaced by its member-mean share, using an EXTERNAL s_T^2 (S4F-derived, or S-N2 on DEV).
    W_r = sd ** 2
    for label, sT2 in (("s4f_derived", comp["sT2"]), ("sn2_dev", sT2_sn2)):
        var = W_r * (1 + 1 / B) - np.clip(sT2, 0, None)[None, :]
        res[f"coverage_diag_minus_sT2_{label}_own"] = coverage(mem, t, var)
    # diagnostic (in-sample: the sampling term is estimated from these same replicates): the error variance
    # the components model predicts, W_r / B + s_De^2, with s_De^2 = Var(estimate - own truth) - W/B (the
    # ERROR's event-sample term, not the estimate's), and no bias term.
    sDe2 = e_own.var(axis=0, ddof=1) - comp["W"] / B
    res["sD2_error_own"] = sDe2.tolist()
    res["coverage_diag_components_insample_own"] = coverage(mem, t, W_r / B + np.clip(sDe2, 0, None)[None, :])
    return res


def library_bias(led: Ledger, s5_eav: dict) -> dict:
    """Mean signed residual (SINGLE fit - own truth) of every S4S case over FB draws 0-7, on the aggregate
    E_avail histogram (not each case's natural histogram), against the dev-tilt section-9 68 % half-width
    of the six-member mean (mean over S5 replicates). Single-fit bias is not member-mean bias."""
    mem = s5_eav["members"]
    hw68 = (tq(0.68, B - 1) * mem.std(axis=1, ddof=1) * math.sqrt(1 + 1 / B)).mean(axis=0)
    out = {"dev_tilt_section9_mean_half_width_68": hw68.tolist(), "cases": {}}
    for case in LIBRARY_CASES:
        res = []
        for r in range(8):
            d = led.load(FD / f"results/final/scored_fb/S4S-{CAND}-FB{r}-{case}.design_scores.json")
            x = iteration(d, K)["histograms"]["eavail"]
            res.append(np.asarray(x["signed_residual_per_bin"], np.float64))
        res = np.asarray(res)
        m, s = res.mean(0), res.std(0, ddof=1)
        out["cases"][case] = {"n": 8, "bias": m.tolist(), "sd": s.tolist(),
                              "abs_bias_over_hw68": (np.abs(m) / hw68).tolist(),
                              "max_abs_bias_over_hw68": float((np.abs(m) / hw68).max())}
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    led = Ledger()
    rng = np.random.default_rng(BOOT_SEED)
    s5 = load_s5(led)
    look1 = completeness(FD / "freeze/COMPLETENESS-look1.tsv")
    led.files[str((FD / "freeze/COMPLETENESS-look1.tsv").relative_to(REPO))] = sha256(FD / "freeze/COMPLETENESS-look1.tsv")
    s4f_reps = sorted(int(m[1]) for n in look1 if (m := re.match(rf"^S4F-{CAND}-FB(\d+)$", n)))
    if s4f_reps != list(range(60)):
        raise SystemExit(f"S4F replicates {s4f_reps[:5]}... ({len(s4f_reps)})")
    check_s4f_receipts(s4f_reps, look1)
    s4f = load_single(led, f"S4F-{CAND}-FB{{r}}", s4f_reps, "scored_fb")
    sn2 = load_sn2(led)
    out = {"schema": "next-prep-pet/saved-reductions/1", "candidate": CAND, "k": K, "B": B,
           "n_boot": N_BOOT, "boot_seed": BOOT_SEED,
           "t_factors": {f"{L:.2f}": tq(L, B - 1) for L in LEVELS},
           "s5_replicates": s5["_replicates"], "s4f_replicates": s4f_reps,
           "histograms": {h: reduce_hist(h, s5, s4f, sn2[h], rng) for h in HISTS},
           "library_bias_eavail": library_bias(led, s5["eavail"])}
    out["operands"] = {"n_files": len(led.files), "digest_of_file_list": led.digest()}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=1, allow_nan=True) + "\n")
    (a.out.parent / "operands.tsv").write_text(
        "path\tsha256\n" + "".join(f"{k}\t{v}\n" for k, v in sorted(led.files.items())))
    print(f"{len(led.files)} operand files; digest {led.digest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
