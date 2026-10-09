"""Closeout arithmetic for corrections 1 and 3, read from first operands (standard library only).

Run from the repository root: python3 -I docs/orchestration/state/next-preparation-20261009/closeout/checks/arith.py
"""
import json
import math

KI85 = "docs/orchestration/state/ki85-diag-20261006/ki85_result.json"
BUDGET = "docs/orchestration/state/ki84-adopt-20261006/recompute_2d_budget.json"

realboot = json.load(open(KI85))["median_rel_spread_pct"]["realboot"]  # data-only real-data replicas
vl170_boot = json.load(open(BUDGET))["VL170"]["boot"]["median_pct"]  # both-stream VL170 band
mc_over_data = 4.978e21 / 1.0574e21  # MC / data POT (B DESIGN section 3)
f_data = (realboot / vl170_boot) ** 2

out = {"f_data": f_data, "mc_over_data": mc_over_data, "kappa": {}}
for label, bank in (("N1_half_mc", mc_over_data / 2), ("N2_48pct", 0.48 * mc_over_data)):
    inflation = mc_over_data / bank  # MC-stream variance scales inversely with bank size
    share = f_data / (f_data + (1 - f_data) * inflation)
    out["kappa"][label] = {"bank_mc_over_data": bank, "mc_var_inflation": inflation,
                           "data_share": share, "kappa": math.sqrt(share)}

# Fixed-bank offset (closeout review F1): the bank's MC realization is a per-functional offset
# against T_R of rms sqrt(1 - share) sigma-hat; coverage is the Gaussian average over that offset.
from statistics import NormalDist
_n = NormalDist()
def _mean_i68(offset_rms, noise_sd):
    # E_o[P(|o + noise| < 1)] with o ~ N(0, offset_rms^2): equals P(|N(0, total)| < 1)
    total = math.sqrt(offset_rms ** 2 + noise_sd ** 2)
    return _n.cdf(1 / total) - _n.cdf(-1 / total)
share = out["kappa"]["N1_half_mc"]["data_share"]
o = math.sqrt(1 - share)
out["n1_bank_offset"] = {
    "offset_rms_over_sigma_both_stream": o,
    "pooled_i68_both_stream": _mean_i68(o, math.sqrt(share)),
    "offset_rms_over_sigma_data_only": o / math.sqrt(share),
    "mean_i68_data_only": _mean_i68(o / math.sqrt(share), 1.0),
}

# Fraction of functionals that over-cover with the both-stream bootstrap: a functional with offset d
# over-covers when P(|d + noise| < 1) > 0.682689; that coverage falls in |d|, so solve for the edge d*.
_noise = math.sqrt(share)
_cov = lambda d: _n.cdf((1 - d) / _noise) - _n.cdf((-1 - d) / _noise)
lo, hi = 0.0, 1.0
for _ in range(100):
    mid = (lo + hi) / 2
    lo, hi = (mid, hi) if _cov(mid) > 0.6826894921370859 else (lo, mid)
out["n1_bank_offset"]["over_cover_edge_d"] = lo
out["n1_bank_offset"]["over_cover_fraction"] = 2 * _n.cdf(lo / o) - 1

# Correction 3: P05 under A's and C's conventions; documented walls (not receipts).
packed = 0.68  # A's memory-packed node-h per exact unfold (extrapolated)
ratio = 0.5 / (804 / 3600)  # ~30 min universe task / 13 min 24 s CV, full node
p05_cv_rate = 188 * packed
p05_ratio = 187 * packed * ratio + packed
p09b = 10 * packed
out["p05"] = {"universe_cv_ratio": ratio, "cv_rate": p05_cv_rate, "ratio_convention": p05_ratio}
out["transfer_totals"] = {
    str(p03): {"cv_rate": p03 + p05_cv_rate + p09b, "ratio": p03 + p05_ratio + p09b}
    for p03 in (34, 39, 205, 215)
}
print(json.dumps(out, indent=1))
