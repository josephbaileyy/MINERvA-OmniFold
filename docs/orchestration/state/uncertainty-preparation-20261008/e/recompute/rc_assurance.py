#!/usr/bin/env python3
"""Reviewer's independent assurance arithmetic (lane B / lane C claims).

Own implementation: exact binomial tails via scipy.stats.binom, exact Student-t for sigma-hat
noise (B uses Simpson quadrature over chi^2), noncentral t for an offset. Does not import B or C.
python3 -I rc_assurance.py > rc_assurance.json
"""
import json
import math

import numpy as np
from scipy import stats

Z95 = stats.norm.ppf(0.975)
LEV = {"I68": 1.0, "I95": Z95}
NOM = {k: 2 * stats.norm.cdf(z) - 1 for k, z in LEV.items()}
DF = 299  # sigma-hat from 300 replicas, ddof=1


def cov(z, kappa, df=DF, delta=0.0):
    """P(|X| <= z*s), X ~ N(delta, kappa^2), s^2 ~ chi2_df/df (df=None: s=1)."""
    if df is None:
        return stats.norm.cdf((z - delta) / kappa) - stats.norm.cdf((-z - delta) / kappa)
    if delta == 0.0:
        return 2 * stats.t.cdf(z / kappa, df) - 1
    nc = delta / kappa
    return stats.nct.cdf(z / kappa, df, nc) - stats.nct.cdf(-z / kappa, df, nc)


def accept(n, p0, alpha):
    """Largest tails each with prob <= alpha/2 under Binomial(n,p0). Return [a,b]."""
    h = alpha / 2
    # lower: reject H <= a-1 ; need P(H <= a-1) <= h, a maximal
    a = int(stats.binom.ppf(h, n, p0))  # smallest k with cdf(k) >= h
    # adjust: want max a with cdf(a-1) <= h
    while stats.binom.cdf(a, n, p0) <= h:
        a += 1
    while a > 0 and stats.binom.cdf(a - 1, n, p0) > h:
        a -= 1
    b = int(stats.binom.isf(h, n, p0))
    while stats.binom.sf(b - 1, n, p0) <= h:  # P(H >= b) <= h -> can lower b
        b -= 1
    while stats.binom.sf(b, n, p0) > h:      # need P(H >= b+1) <= h
        b += 1
    return a, b


def pin(n, p, a, b):
    return float(stats.binom.cdf(b, n, p) - stats.binom.cdf(a - 1, n, p))


def ok_at(n, levels, edges, alpha, beta):
    for k in levels:
        a, b = accept(n, NOM[k], alpha)
        if pin(n, edges[k][0], a, b) > beta or pin(n, edges[k][1], a, b) > beta:
            return False
    return True


def req_n(levels, edges, alpha, beta, win=100, start=20, nmax=6000):
    run = None
    for n in range(start, nmax + 1):
        if ok_at(n, levels, edges, alpha, beta):
            run = n if run is None else run
            if n - run >= win:
                return run
        else:
            run = None
    return None


def edges_for(tol, levels, df=DF):
    lo, hi = tol
    return {k: (cov(LEV[k], hi, df), cov(LEV[k], lo, df)) for k in levels}


out = {}
out["nominal"] = NOM
out["z95"] = Z95
out["cov_k1_b300"] = {k: cov(z, 1.0) for k, z in LEV.items()}
out["edges_b300"] = {k: [cov(z, 1.25), cov(z, 0.80)] for k, z in LEV.items()}
out["edges_exact_sigma"] = {k: [cov(z, 1.25, None), cov(z, 0.80, None)] for k, z in LEV.items()}

# deterministic edge cases
ec = {}
ec["binom_n1_p0.5_accept_alpha0.5"] = accept(1, 0.5, 0.5)  # each tail 0.25 < 0.5: P(H=0)=0.5>0.25 -> [0,1]
ec["binom_n10_p0.5_alpha0.05"] = accept(10, 0.5, 0.05)  # textbook [2,8]
ec["t_df_inf_limit"] = cov(1.0, 1.0, 10**7) - NOM["I68"]
ec["2sigma_vs_95"] = [2 * stats.norm.cdf(2) - 1, 0.95]
ec["p_in_full_range"] = pin(50, 0.3, 0, 50)
out["edge_cases"] = ec

FUN = 206
ALPHA_COV = 0.04 / (FUN * 2)
out["per_test_alpha"] = ALPHA_COV
BETA = 0.10
lv = ["I68", "I95"]
E = edges_for((0.80, 1.25), lv)
N = req_n(lv, E, ALPHA_COV, BETA)
out["N_required"] = N
det = {}
for k in lv:
    a, b = accept(N, NOM[k], ALPHA_COV)
    det[k] = dict(accept=[a, b], pass_at_k1p25=pin(N, E[k][0], a, b), pass_at_k0p8=pin(N, E[k][1], a, b),
                  fail_nominal=1 - pin(N, NOM[k], a, b), fail_k1_b300=1 - pin(N, cov(LEV[k], 1.0), a, b))
out["at_N"] = det
# first N (without stability window) and whether the condition is non-monotone
first = next(n for n in range(20, 3000) if ok_at(n, lv, E, ALPHA_COV, BETA))
out["first_N_ok_no_window"] = first
out["fw_nominal_union"] = 1 - FUN * sum(det[k]["fail_nominal"] for k in lv)
out["fw_k1b300_union"] = 1 - FUN * sum(det[k]["fail_k1_b300"] for k in lv)

# bias test
za = stats.norm.ppf(1 - 0.01 / (2 * FUN)); zb = stats.norm.ppf(0.9)
out["bias_zcrit"] = za
out["bias_N_k1"] = math.ceil(((za + zb) * 1.0 / 0.2) ** 2)
out["bias_N_k1p25"] = math.ceil(((za + zb) * 1.25 / 0.2) ** 2)
def bpow(n, k):
    m = 0.2 * math.sqrt(n) / k
    return stats.norm.sf(za - m) + stats.norm.cdf(-za - m)
out["bias_power_719"] = [bpow(N, 1.0), bpow(N, 1.25)]
# exact-t version of bias power (pull sd includes t inflation; test uses s_j, so z approx ok)
ND = max(N, out["bias_N_k1p25"])
out["N_design"] = ND
out["at_N_design"] = {k: dict(accept=list(accept(ND, NOM[k], ALPHA_COV))) for k in lv}
out["fw_nominal_union_N_design"] = 1 - FUN * sum(1 - pin(ND, NOM[k], *accept(ND, NOM[k], ALPHA_COV)) for k in lv)
out["coverage_at_bias_0.2"] = {k: cov(LEV[k], 1.0, None, 0.2) for k in lv}

# sensitivity table
sens = []
for tol in ([0.87, 1.15], [0.83, 1.20], [0.80, 1.25], [0.75, 1.33], [0.667, 1.50]):
    e = edges_for(tol, lv)
    nb = req_n(lv, e, ALPHA_COV, BETA)
    n68 = req_n(["I68"], {"I68": e["I68"]}, 0.04 / FUN, BETA)
    sens.append(dict(tol=tol, both=nb, i68=n68))
out["sens"] = sens
# exact reciprocal tolerances 1/x..x as the doc's header claims
sens2 = []
for x in (1.15, 1.20, 1.25, 1.33, 1.5):
    e = edges_for((1 / x, x), lv)
    sens2.append(dict(x=x, both=req_n(lv, e, ALPHA_COV, BETA), i68=req_n(["I68"], {"I68": e["I68"]}, 0.04 / FUN, BETA)))
out["sens_exact_reciprocal"] = sens2

# C's 4-case family: 824 functionals
FUN4 = 824
a4 = 0.04 / (FUN4 * 2)
N4 = req_n(lv, E, a4, BETA)
za4 = stats.norm.ppf(1 - 0.01 / (2 * FUN4))
out["C_4case_N"] = N4
out["C_4case_bias_N_k1p25"] = math.ceil(((za4 + zb) * 1.25 / 0.2) ** 2)
out["C_4case_accept"] = {k: list(accept(N4, NOM[k], a4)) for k in lv}

# finite reference offset (B s7): fraction failing at exact calibration
r_mc = 4.978198462880827e21 / 1.057394261158926e21
f_data = (0.4869623637052485 / 0.6738150183177408) ** 2
out["r_mc"] = r_mc; out["f_data"] = f_data
rows = []
gh_x = np.linspace(-9, 9, 3601)  # dense grid (Gauss-Hermite with 80 nodes was too coarse: integrand steps on a 1/(tau*sqrt(N)) scale)
gh_w = np.exp(-0.5 * gh_x ** 2); gh_w = gh_w / gh_w.sum()
acc = {k: accept(N, NOM[k], ALPHA_COV) for k in lv}
for rho in (0.3, 0.5, 0.7):
    for s in (0.25, 0.5, 1.0):
        tau = math.sqrt(s * f_data / (rho * r_mc))
        cf = 0.0
        for k in lv:
            a, b = acc[k]
            pc = cov(LEV[k], 1.0, None, tau * gh_x)
            cf += float(np.sum(gh_w * (1 - (stats.binom.cdf(b, N, pc) - stats.binom.cdf(a - 1, N, pc)))))
        # bias: t ~ N(delta*sqrt(N), 1) approx (kappa=1)
        bf = float(np.sum(gh_w * (stats.norm.sf(za - tau * gh_x * math.sqrt(N)) + stats.norm.cdf(-za - tau * gh_x * math.sqrt(N)))))
        bf_closed = 2 * stats.norm.sf(za / math.sqrt(N * tau ** 2 + 1))
        # coverage-only, with exact-t sigma-hat noise in the per-experiment hit
        rows.append(dict(rho=rho, s=s, tau=tau, exp_cov_fail=FUN * cf, exp_bias_fail=FUN * bf, exp_bias_fail_closed_form=FUN * bf_closed))
out["finite_ref"] = rows
# what reservoir exposure would make the reference offset negligible for the 0.2 sigma bias test?
# need tau <= ~0.05 (1/4 of the bias tolerance): rho*r_mc >= s*f_data/0.0025
out["reservoir_exposure_over_D_for_tau_0p05_s0p5"] = 0.5 * f_data / 0.05 ** 2

# costs from B's operands (own arithmetic)
per = 17.744 / 300
out["per_run_shared"] = per
out["P_719"] = 719 * 301 * per * 1.05
out["P_1116"] = 1116 * 301 * per * 1.05
out["P_floor_172"] = 172 * 301 * per * 1.05
out["N2"] = 100 * 7.076 / 100 * 1.05
print(json.dumps(out, indent=1, default=float))
