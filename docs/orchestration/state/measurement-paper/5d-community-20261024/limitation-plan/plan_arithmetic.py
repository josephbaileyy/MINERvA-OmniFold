#!/usr/bin/env python3
"""The arithmetic behind LIMITATION-PLAN.md, from three committed readouts. Login-node or laptop, numpy, 0 node-h.

1. The kappa -> infinity bound (section 2(b)). With M the grade matrix (C_total + C_resp without the GiBUU vertex, plus
   the noise of the mean) and the GiBUU vertex s added at scale kappa, Sherman-Morrison gives
   chi2(kappa) = chi2_out - kappa u^2 / (1 + kappa q), u = s'M^-1 b, q = s'M^-1 s. From chi2(0) = grade and
   chi2(1) = in-sample, chi2(inf) = chi2_in - (chi2_out - chi2_in) / q, which increases with q; q >= s_c^2 / M_cc for
   every cell c (M positive definite), so the largest s_c^2 / M_cc gives a lower bound on chi2(inf).
   1b. The rank-3 limit (diagonal noise; the readout records only N_T's diagonal), every C_model vertex scaled by kappa -> inf: min_a (b - S'a)' M0^-1 (b - S'a), with
   M0 = C_e + C_resp + noise, from the data product's matrices (each checked against F0b's readout first).
   1c. The coverage of the total intervals at zero bias if the pseudo-data spread reproduces only C_e (or C_e + C_resp).
2. The direction of the bias against each C_model vertex: unweighted cosine and the residual after a least-squares fit
   of b onto s.
3. The per-cell 1-sigma coverage that F0b's biases imply IF the reported sigma were the true spread:
   P(|z_c + e| <= 1), e ~ N(0, 1), z_c the bias over sigma of the in-sample matrix (the grade matrix for a truth with
   no own vertex). An assumption, not a test.
4. Option (a)'s size: the per-cell relative sigma with the N1 quadrature sum of declared biases added, for
   illustrative truth sets (the set is Joseph's to declare).
5. The binomial resolution and cost of the coverage designs in section 1.

MEASURES: nothing; arithmetic on committed readouts. CANNOT AUTHORIZE: anything.
"""
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[6]
F0B = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/readout/fd_f0b_readout.json"
CMODEL = "nd-unfolding/pv-ladder/readouts/cmodel_5d.json"
DP = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/data-product/fd_data_product.json"
CHI2_16_P01 = 31.9999  # chi2 with 16 ndf at p = 0.01


def Phi(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def main():
    for p in (F0B, CMODEL, DP):
        print(f"input {p} sha256 {hashlib.sha256((REPO / p).read_bytes()).hexdigest()}")
    d = json.loads((REPO / F0B).read_text())
    c = json.loads((REPO / CMODEL).read_text())
    S = dict(zip(c["vertices"], c["S"]))
    T = {t["name"]: t for t in d["truths"]}
    cells = d["cells"] if isinstance(d["cells"], list) else [f"R{i:02d}" for i in range(16)]

    print("\n1. kappa -> infinity bound, GiBUU vertex (F0b: + C_resp)")
    s = S["gibuu"]
    rs = d["relative_sigma_plus_C_resp"]["minus_gibuu"]
    for name in ("A7_gibuu", "stage0c_gibuu"):
        t = T[name]
        N = t["noise_sigma"]
        ratio = [s[i] ** 2 / (rs[i] ** 2 + N[i] ** 2) for i in range(16)]
        i = max(range(16), key=ratio.__getitem__)
        out, ins = t["grade"]["chi2"], t["in_sample"]["chi2"]
        print(f"  {name}: grade {out:.2f}, in-sample {ins:.2f}; q >= {ratio[i]:.3f} ({cells[i]}: s {s[i]:+.4f}, "
              f"sigma {math.sqrt(rs[i] ** 2 + N[i] ** 2):.4f}); chi2(kappa -> inf) >= {ins - (out - ins) / ratio[i]:.2f}"
              f" (p = 0.01 at {CHI2_16_P01:.2f})")

    t = T["A7_gibuu"]
    rs0 = d["relative_sigma"]["minus_gibuu"]
    q0 = max(s[i] ** 2 / (rs0[i] ** 2 + t["noise_sigma"][i] ** 2) for i in range(16))
    print(f"  A7_gibuu, F0 (no C_resp; FD-F0-REPORT.md: grade 246.75, in-sample 180.99): q >= {q0:.3f}; "
          f"chi2(kappa -> inf) >= {180.99 - (246.75 - 180.99) / q0:.2f}")

    print("\n1b. all of C_model scaled, kappa -> inf (rank-3), from the data product's matrices. The readout records only")
    print("    the diagonal of the noise N_T = Cov_i(r)/B_T (FD-PLAN.md:237), so N_T is diagonal here: the readout's")
    print("    chi2 is reproduced to about 0.1 %, and the limits below carry that approximation")
    dp = json.loads((REPO / DP).read_text())
    f = np.array(dp["f"])
    rel = {k: np.array(v) / np.outer(f, f) for k, v in dp["matrices"].items()}
    Sm = np.array([S[v] for v in c["vertices"]])
    print(f"  check: C_model_abs / ff' = S'S to {np.abs(rel['C_model_abs'] - Sm.T @ Sm).max():.2e} "
          f"(max entry {np.abs(rel['C_model_abs']).max():.2e})")
    full = rel["C_e"] + rel["C_model_abs"] + rel["C_resp"]
    print(f"  check: sqrt(diag) vs F0b relative_sigma_plus_C_resp.C_total: max diff "
          f"{np.abs(np.sqrt(np.diag(full)) - np.array(d['relative_sigma_plus_C_resp']['C_total'])).max():.2e}")
    for name in ("A7_gibuu", "stage0c_gibuu", "q3", "A7_nuwro"):
        t = T[name]
        b = np.array(t["bias"])
        N2 = np.diag(np.array(t["noise_sigma"]) ** 2)
        own = t["own_vertex"]
        chi = lambda M, r: float(r @ np.linalg.solve(M, r))
        M_in = full + N2
        msg = f"  {name}: in-sample/full chi2 {chi(M_in, b):.2f} (readout {(t.get('in_sample') or t['grade'])['chi2']:.2f})"
        if own:
            so = np.array(S[own])
            msg += f"; grade {chi(M_in - np.outer(so, so), b):.2f} (readout {t['grade']['chi2']:.2f})"
        M0 = rel["C_e"] + rel["C_resp"] + N2
        for lab, rows in (("all three vertices", list(c["vertices"])),
                          ("own vertex left out", [v for v in c["vertices"] if v != own]) if own else (None, None)):
            if lab is None:
                continue
            A = np.array([S[v] for v in rows]).T
            Wi = np.linalg.solve(M0, A)
            a = np.linalg.solve(A.T @ Wi, Wi.T @ b)
            msg += f"; kappa -> inf, {lab}: {chi(M0, b - A @ a):.2f}"
        print(msg)
    print(f"  (p = 0.01 at chi2_16 = {CHI2_16_P01:.2f})")

    print("\n1c. expected coverage of the reported (total) intervals at zero bias, if the pseudo-data spread is only part")
    rs_dp = {k: np.array(v) for k, v in dp["relative_sigma"].items()}
    tot = rs_dp["C_total_plus_C_resp"]
    for lab, spr in (("C_e", rs_dp["C_e"]), ("C_e + C_resp", np.hypot(rs_dp["C_e"], rs_dp["C_resp"]))):
        c1 = np.array([2 * Phi(x) - 1 for x in tot / spr])
        c2 = np.array([2 * Phi(2 * x) - 1 for x in tot / spr])
        print(f"  spread {lab}: 1 sigma mean {c1.mean():.3f} (min {c1.min():.3f}); 2 sigma mean {c2.mean():.3f} "
              f"(min {c2.min():.3f}); nominal 0.683 / 0.954")

    print("\n2. bias direction against each C_model vertex (unweighted, Euclidean: a heuristic; section 1 is the bound)")
    for name in ("A7_gibuu", "stage0c_gibuu", "q3", "A7_nuwro"):
        b = T[name]["bias"]
        nb = math.sqrt(sum(x * x for x in b))
        print(f"  {name}: |b| {nb:.4f}, max |b_c| {max(abs(x) for x in b):.4f} ({cells[max(range(16), key=lambda k: abs(b[k]))]})")
        for v, sv in S.items():
            ns2 = sum(y * y for y in sv)
            dot = sum(x * y for x, y in zip(b, sv))
            lam = dot / ns2
            res = math.sqrt(sum((x - lam * y) ** 2 for x, y in zip(b, sv)))
            print(f"    vs {v}: cos {dot / (nb * math.sqrt(ns2)):+.3f}, residual {res / nb:.3f} of |b|")

    print("\n3. per-cell 1-sigma coverage implied by F0b's bias, if sigma were the true spread (nominal 0.683)")
    for t in d["truths"]:
        if not t["graded"]:
            continue
        src, lab = (t["in_sample"], "in-sample") if t.get("in_sample") else (t["grade"], "grade")
        cov = [Phi(1 - z) - Phi(-1 - z) for z in src["z"]]
        low = [cells[k] for k in range(16) if cov[k] < 0.5]
        out1 = [cells[k] for k in range(16) if abs(src["z"][k]) > 1]
        print(f"  {t['name']:14s} ({lab:9s}) mean {sum(cov) / 16:.3f}, min {min(cov):.3f}, "
              f"cells below 0.5: {', '.join(low) or 'none'}; |z| > 1 (coverage <= 0.5 for ANY symmetric spread): "
              f"{', '.join(out1) or 'none'}")

    print("\n4. option (a), N1 quadrature: per-cell relative sigma of C_total + C_resp + sum_T b_T b_T' (illustrative sets)")
    full = d["relative_sigma_plus_C_resp"]["C_total"]
    med = lambda v: sorted(v)[7:9]
    for label, names in (("A7 GiBUU only", ("A7_gibuu",)), ("q3 only", ("q3",)),
                         ("A7 GENIE+MEC, A7 NuWro, A7 GiBUU, q3", ("A7_genie_mec", "A7_nuwro", "A7_gibuu", "q3"))):
        new = [math.sqrt(full[k] ** 2 + sum(T[n]["bias"][k] ** 2 for n in names)) for k in range(16)]
        m0, m1 = sum(med(full)) / 2, sum(med(new)) / 2
        k = max(range(16), key=lambda j: new[j] / full[j])
        print(f"  {label}: median {100 * m0:.2f} % -> {100 * m1:.2f} %; largest {cells[k]} {100 * full[k]:.2f} % -> "
              f"{100 * new[k]:.2f} %; trace x {sum(x * x for x in new) / sum(x * x for x in full):.2f}")

    print("\n5. coverage-design resolution and cost")
    for n in (100, 300, 544):
        print(f"  N = {n}: per-cell binomial SE at 0.683 = {math.sqrt(0.683 * 0.317 / n):.4f}; "
              f"16 independent cells pooled {math.sqrt(0.683 * 0.317 / (16 * n)):.4f}")
    unit = 0.025  # node-h per nuisance-drawn experiment, FD-PLAN.md section 5.1
    for truths, n in ((3, 300), (3, 100)):
        e = truths * n * unit
        print(f"  {truths} truths x {n}: {truths * n} unfolds x {unit} = {e:.2f} node-h; x 1.5625 reserve = {e * 1.5625:.2f}")
    s1 = 6.04167  # node-h, S1's whole covariance production (S1-REPORT.md; s1/LEDGER.tsv)
    print(f"  nested (C_e rebuilt per experiment, one S1 each): {s1} node-h per experiment; per arm N = 100: "
          f"{100 * s1:.0f}, N = 300: {300 * s1:.0f}; three arms x 300: {900 * s1:.0f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
