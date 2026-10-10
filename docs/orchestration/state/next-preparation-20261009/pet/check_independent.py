"""Independent re-implementation of the consequential numbers in `results/saved_reductions.json`.

Pure standard-library Python: no numpy or scipy, its own file discovery (directory glob, not the
completeness records), its own Student-t quantile (Simpson integration of the density plus
bisection), and explicit loops. It recomputes, for the aggregate E_avail and the low-acceptance
region at k = 5:

* W, V, V1, s_D^2 = V - W/6, s_T^2 = V1 - s_D^2 (per bin);
* the section-9 coverage at 68 % and 95 %, pooled over bins, against the replicate's own truth;
* the member-mean bias per bin and the single-fit E0 recovery mean;
* the S-N2 pooled seed variance.

and compares each with the reduction's value (relative tolerance 1e-9 on moments, exact on coverage
counts). Exit 0 only if every comparison agrees.

    python check_independent.py results/saved_reductions.json [results/design_cost.json]
"""
from __future__ import annotations

import glob
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FD = os.path.normpath(os.path.join(HERE, "../../../../../nd-unfolding/pet/final_design"))
B = 6


def t_pdf(x: float, nu: int) -> float:
    c = math.exp(math.lgamma((nu + 1) / 2) - math.lgamma(nu / 2)) / math.sqrt(nu * math.pi)
    return c * (1 + x * x / nu) ** (-(nu + 1) / 2)


def t_cdf(x: float, nu: int, n: int = 4000) -> float:
    """P(T <= x) for x >= 0 by composite Simpson on [0, x]."""
    h = x / n
    s = t_pdf(0, nu) + t_pdf(x, nu)
    for i in range(1, n):
        s += (4 if i % 2 else 2) * t_pdf(i * h, nu)
    return 0.5 + s * h / 3


def t_quantile(level: float, nu: int) -> float:
    target = 0.5 + level / 2
    lo, hi = 0.0, 50.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if t_cdf(mid, nu) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def phi(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def phi_inv(p: float) -> float:
    lo, hi = -10.0, 10.0
    for _ in range(100):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if phi(mid) < p else (lo, mid)
    return (lo + hi) / 2


def check_design(dc: dict, close) -> None:
    """Re-derive the consequential arithmetic of `results/design_cost.json` by hand."""
    # bias tolerance: coverage of N(b, 1) inside +-z at the reported b equals the proposed bound
    for level, lb in (("0.68", 0.63), ("0.95", 0.92)):
        z = phi_inv(0.5 + float(level) / 2)
        b = dc["bias_tolerance"][level]["max_abs_bias_over_sd"]
        close(f"bias tolerance {level}", phi(z - b) - phi(-z - b), lb, rel=1e-6)
    # prices: units x 1.05 failures x u / 0.8 reserve (not x 1.2)
    for key, units in (("dispatch_192_pilot", 192), ("E1_look1", 60), ("E1_through_look2", 108)):
        c = dc["costs"][key]
        close(f"{key} units", c["study_scale"]["units"], units, rel=0)
        close(f"{key} study A100-h", c["study_scale"]["a100h_total_with_reserve"], units * 1.05 * 1.768 / 0.8)
        close(f"{key} 2M A100-h", c["data_2M_forecast"]["value"]["a100h_total_with_reserve"], units * 1.05 * 7.3 / 0.8)
        close(f"{key} 10M A100-h", c["data_10M_forecast"]["value"]["a100h_total_with_reserve"], units * 1.05 * 29 / 0.8)
    nv = dc["validation_replicates_per_case_used"]
    full = 108 + 60 * 6 * 3 + 2 * 6 * 51 + nv * 6 * 4 + 121
    nvj = dc["validation_replicates_per_case_used_joint"]
    fullj = 108 + 60 * 6 * 3 + 4 * 6 * 51 + nvj * 6 * 4 + 308
    close("full procedure joint high units", dc["costs"]["full_procedure_strategyB_joint_high"]["study_scale"]["units"],
          fullj, rel=0)
    close("full procedure joint high 2M A100-h",
          dc["costs"]["full_procedure_strategyB_joint_high"]["data_2M_forecast"]["value"]["a100h_total_with_reserve"],
          fullj * 1.05 * 7.3 / 0.8)
    close("full procedure low units", dc["costs"]["full_procedure_strategyB_low"]["study_scale"]["units"], full, rel=0)
    close("full procedure low 2M A100-h",
          dc["costs"]["full_procedure_strategyB_low"]["data_2M_forecast"]["value"]["a100h_total_with_reserve"],
          full * 1.05 * 7.3 / 0.8)
    close("full procedure allocation share",
          dc["costs"]["full_procedure_strategyB_low"]["data_2M_forecast"]["value"]["share_of_recorded_allocation"],
          full * 1.05 * 7.3 / 0.8 / 4 / 56132)
    # events
    ev = dc["events"]
    close("disjoint experiments in DEV", ev["disjoint_data_size_experiments_in_DEV"], 45087969 // 11600000, rel=0)
    close("never drawn / experiment", ev["never_drawn_rows_over_one_experiment"], 4061737 / 11.6e6)
    close("500 experiments / inventory", ev["inventory_multiples_for_independent_validation"]["500"],
          500 * 11.6e6 / 49152885)
    # validation sizing: re-implement the Wilson-bound assurance and confirm the reported N is minimal
    deff = dc["validation_sizing"]["design_effect"]
    for row in dc["validation_sizing"]["rows"]:
        def ass(n):
            ne = n * 7 / deff
            z = phi_inv(1 - 0.05 / row["m"])
            lo, hi = 0.0, 1.0
            for _ in range(80):
                ph = (lo + hi) / 2
                c = ph + z * z / (2 * ne)
                w = (c - z * math.sqrt(ph * (1 - ph) / ne + z * z / (4 * ne * ne))) / (1 + z * z / ne)
                lo, hi = (lo, ph) if w >= row["lower_bound"] else (ph, hi)
            return 1 - phi((hi - row["level"]) / math.sqrt(row["level"] * (1 - row["level"]) / ne))
        n = row["replicates_per_case"]
        if not (ass(n) >= 0.9 > ass(n - 1)):
            close(f"N minimal m={row['m']} {row['level']} {row['tolerances']}", ass(n), 0.9, rel=0)
        nj, tj = row["replicates_per_case_joint"], 0.9 ** (1 / row["m"])
        if not (ass(nj) >= tj > ass(nj - 1)):
            close(f"joint N minimal m={row['m']} {row['level']} {row['tolerances']}", ass(nj), tj, rel=0)
    print("design arithmetic: checked")


def mean(xs):
    return sum(xs) / len(xs)


def var(xs):
    m = mean(xs)
    return sum((x - m) ** 2 for x in xs) / (len(xs) - 1)


def k5(doc, hist):
    for it in doc["iterations"]:
        if it["k"] == 5:
            return it["histograms"][hist]
    raise SystemExit(f"{doc['run_name']}: no k=5")


def load(path):
    with open(path) as fh:
        return json.load(fh)


def main(path: str) -> int:
    ref = load(path)
    tq = {L: t_quantile(L, B - 1) for L in (0.68, 0.95)}
    problems = []

    def close(label, a, b, rel=1e-9, absol=1e-15):
        if not (abs(a - b) <= max(rel * max(abs(a), abs(b)), absol)):
            problems.append(f"{label}: independent {a!r} vs reduction {b!r}")

    for L in (0.68, 0.95):
        close(f"t({L},5)", tq[L], ref["t_factors"][f"{L:.2f}"], rel=1e-7)

    s5 = sorted(glob.glob(os.path.join(FD, "results/final/scored_s5c/S5-H2S1T24K5-FB*-b*.design_scores.json")))
    reps = {}
    for f in s5:
        base = os.path.basename(f).split(".")[0]          # S5-H2S1T24K5-FB<r>-b<m>
        r = int(base.split("-FB")[1].split("-b")[0])
        reps.setdefault(r, []).append(f)
    if len(reps) != 120 or any(len(v) != B for v in reps.values()):
        problems.append(f"S5 discovery: {len(reps)} replicates, sizes {sorted({len(v) for v in reps.values()})}")
    s4f = [os.path.join(FD, f"results/final/scored_fb/S4F-H2S1T24K5-FB{r}.design_scores.json") for r in range(60)]
    sn2 = {d: [os.path.join(FD, f"results/s3n/S3P-H2S1T24K5-DEV{d}{s}.design_scores.json")
               for s in ("", "-s1", "-s2", "-s3")] for d in (0, 1)}

    for hist in ("eavail", "eavail@low_acceptance"):
        R = ref["histograms"][hist]
        mem, tgt = [], []
        for r in sorted(reps):
            hs = [k5(load(f), hist) for f in sorted(reps[r])]
            mem.append([h["unfolded_norm"] for h in hs])
            tgt.append(hs[0]["target_norm"])
        sing, tgt1, pri1 = [], [], []
        for f in s4f:
            h = k5(load(f), hist)
            sing.append(h["unfolded_norm"])
            tgt1.append(h["target_norm"])
            pri1.append(h["prior_norm"])
        nb = len(tgt[0])
        hits = {0.68: 0, 0.95: 0}
        for j in range(nb):
            within = [var([m[b][j] for b in range(B)]) for m in mem]
            W = mean(within)
            ests = [mean([m[b][j] for b in range(B)]) for m in mem]
            V = var(ests)
            V1 = var([s[j] for s in sing])
            sD2 = V - W / B
            sT2 = V1 - sD2
            c = R["components"]
            close(f"{hist} W[{j}]", W, c["W"][j])
            close(f"{hist} V[{j}]", V, c["V"][j])
            close(f"{hist} V1[{j}]", V1, c["V1"][j])
            close(f"{hist} sD2[{j}]", sD2, c["sD2"][j], rel=1e-7)
            close(f"{hist} sT2[{j}]", sT2, c["sT2"][j], rel=1e-7)
            bias = mean([ests[i] - tgt[i][j] for i in range(len(mem))])
            close(f"{hist} bias_own[{j}]", bias, R["member_mean"]["bias_own"][j], rel=1e-7)
            for L in (0.68, 0.95):
                for i in range(len(mem)):
                    hw = tq[L] * math.sqrt(within[i]) * math.sqrt(1 + 1 / B)
                    hits[L] += abs(ests[i] - tgt[i][j]) <= hw
            seedv = mean([var([k5(load(f), hist)["unfolded_norm"][j] for f in sn2[d]]) for d in (0, 1)])
            close(f"{hist} sT2_sn2[{j}]", seedv, R["sT2_sn2_dev"][j])
        for L in (0.68, 0.95):
            pooled = hits[L] / (len(mem) * nb)
            close(f"{hist} pooled coverage {L}", pooled, R["coverage_section9_own"][f"{L:.2f}"]["pooled"], rel=0)
        rr = []
        for s, t, p in zip(sing, tgt1, pri1):
            rr.append(1 - sum(abs(a - b) for a, b in zip(s, t)) / sum(abs(a - b) for a, b in zip(p, t)))
        close(f"{hist} single-fit R mean", mean(rr), R["recovery"]["single_fit_R"]["mean"])
        print(f"{hist}: pooled 68 % {hits[0.68] / (len(mem) * nb):.4f}, 95 % {hits[0.95] / (len(mem) * nb):.4f}; "
              f"single-fit R {mean(rr):.4f}")
    if len(sys.argv) > 2:
        check_design(load(sys.argv[2]), close)
    if problems:
        print("DISAGREE:\n  " + "\n  ".join(problems))
        return 1
    print("independent check: all comparisons agree")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
