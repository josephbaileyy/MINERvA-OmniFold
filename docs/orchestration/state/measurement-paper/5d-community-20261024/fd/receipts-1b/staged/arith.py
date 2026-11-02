"""Arithmetic of the staged 1B declaration (FD-1B-STAGED-DECLARATION.md sections 5, 7 and 8), revision 2: the
flag rule's thresholds, size and power through ``nd-unfolding/fd_1b_null.py`` (the rule's one implementation, checked
here against scipy's Clopper-Pearson); the draw-matched null's content at the data's point, from committed readouts
only, as a check of its size before any truth's blocks exist; the item counts and the price; and the seed ranges'
absence from the repository.

The data-point check (``null_at_data``) builds each cell's laws from S1's committed per-band shares
(``fd/receipts-1b/diag/diag.json`` ``share_s1``, times the drawn matrix's relative variance from
``s1/readout/s1_assembly.json``, which reproduce its group sigmas to 2e-16). It is a proxy, labelled as such:
* interaction pair bands, detector bands and the lateral bands are two-point, at their exact variances;
* 2p2h is taken as two-point (its three-point shape needs the shifts themselves), and flux as Gaussian (its 100
  weighted universes need them too);
* the per-lateral-band split is not in a committed readout, so it is bracketed: 5 equal bands, or one band carrying
  the whole lateral variance;
* stat, normalization and C_model are Gaussian. Cells are simulated independently, so only per-cell contents are
  read; the joint content needs the remade blocks' correlations and is computed at each truth by the scorer.

No product is read and nothing runs on the cluster. Run from the repository root:

    python3 -I docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b/staged/arith.py

and the output is ``arith.out`` beside this file.
"""
from __future__ import annotations

import json
import math
import re
import subprocess
import sys

from pathlib import Path

import numpy as np
from scipy.stats import beta, binom

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[7]
sys.path.insert(0, str(REPO / "nd-unfolding"))
import fd_1b_null as fn  # noqa: E402

DIAG = HERE.parent / "diag" / "diag.json"
S1 = HERE.parents[2] / "s1" / "readout" / "s1_assembly.json"
I2 = HERE.parent / "inv" / "i2" / "i2.json"
N_LATERAL = 5
PROXY_SEED = fn.NULL_SEED

P0 = math.erf(1 / math.sqrt(2))          # 0.682689..., the 1-sigma two-sided content
N_TOYS = 300
N_CELLS = 16
CELL_CONF = 1 - fn.ALPHA_CELLS / N_CELLS  # one-sided, Bonferroni over the 16 cells
JOINT_CONF = 1 - fn.ALPHA_JOINT          # one-sided
REV0 = {"cell_conf": 1 - 0.05 / N_CELLS, "joint_conf": 0.95}  # revision 0's rule, for the record

# measured costs (sources in the declaration's section 7)
I2_MAX_S, I2_MEDIAN_S = 849.6, 725.1     # fd/receipts-1b/inv/i2/connect24-post-bulk.out
UNIT_S = 1.25 * I2_MAX_S                 # 1,062 s, mode D's unit
S1_PER_UNIVERSE = 2.00889 / 88           # S1-REPORT.md section 3, job P1
S1_PER_SEED = 1.82500 / 80               # S1-REPORT.md section 3, the seed job
LANES = 8
PER_LANE = 22
LIMIT_S = 8 * 3600
BALANCE = 2069.4                         # iris, 2026-11-01T19:27Z (mode D declaration section 7)
STAGE0_CAP = 5.5

REBUILD = {"CV": 1, "seed_check": 1, "flux": 100, "interaction": 67, "detector": 8, "stat": 50}
TOYS = 300
CONTROLS = 4                              # set-A b1, MaRES_0, Flux_0, GEANT_Pion_0 on the data
CAPTURE = 1                               # the plug-in's data CV unfold with the weights exposed
PILOT = 8                                 # one per lane; with the plug-in, the capture is one of them

SEEDS = {"g18_toys": range(3_620_000, 3_620_300), "g18_stat": [3_621_000],
         "ar23_toys": range(3_630_000, 3_630_300), "ar23_stat": [3_631_000],
         "plugin_toys": range(3_640_000, 3_640_300), "plugin_stat": [3_641_000], "null": [fn.NULL_SEED]}


def cp_upper(k: int, n: int, conf: float) -> float:
    return 1.0 if k >= n else float(beta.ppf(conf, k + 1, n - k))


def cp_lower(k: int, n: int, conf: float) -> float:
    return 0.0 if k <= 0 else float(beta.ppf(1 - conf, k, n - k + 1))


def flag_below(n: int, conf: float) -> int:
    """The largest count k whose one-sided upper bound is below P0 (k <= this flags under-coverage)."""
    return max(k for k in range(n + 1) if cp_upper(k, n, conf) < P0)


def flag_above(n: int, conf: float) -> int:
    """The smallest count k whose one-sided lower bound is above P0 (descriptive over-coverage)."""
    return min(k for k in range(n + 1) if cp_lower(k, n, conf) > P0)


def power(k_flag: int, n: int, p: float) -> float:
    return float(binom.cdf(k_flag, n, p))


def seeds_in_repo() -> list[int]:
    out = subprocess.run(["git", "grep", "-h", "-o", "-E", r"(^|[^0-9a-fA-F_])36[2-4][0-9]{4}([^0-9a-fA-F_]|$)",
                          "--", "*.tsv", "*.py", "*.sh", "*.json", "*.md"], capture_output=True, text=True)
    if out.returncode not in (0, 1):
        raise SystemExit(f"git grep failed: {out.stderr}")
    found = {int(m) for m in re.findall(r"36[2-4][0-9]{4}", out.stdout)}
    declared = {s for r in SEEDS.values() for s in r}
    return sorted(found & declared)


def jobs(items: int) -> dict:
    nodes = math.ceil(items / (LANES * PER_LANE))
    return {"items": items, "nodes": nodes, "per_lane_max": math.ceil(items / (nodes * LANES)),
            "limit_s": LIMIT_S, "fullest_lane_s": math.ceil(items / (nodes * LANES)) * UNIT_S,
            "fill": math.ceil(items / (nodes * LANES)) * UNIT_S / LIMIT_S, "reserved_node_h": nodes * LIMIT_S / 3600}


def null_at_data(lateral_split: str) -> dict:
    """The per-cell draw-matched content at the data's point (the proxy of this module's docstring)."""
    diag, s1 = json.loads(DIAG.read_text()), json.loads(S1.read_text())
    rs = {k: np.asarray(v, float) for k, v in s1["relative_sigma"].items()}
    drawn = sum(rs[k] ** 2 for k in ("stat", "interaction", "flux", "detector", "lateral", "normalization", "seed"))
    pb = diag["per_band"]
    cells, out = s1["cells"], {}
    for c, cell in enumerate(cells):
        laws, gauss = [], rs["stat"][c] ** 2 + rs["normalization"][c] ** 2 + rs["C_model"][c] ** 2
        for b, rec in pb.items():
            var = rec["share_s1"][c] * drawn[c]
            if rec["group"] == "flux":
                gauss += var
            else:
                laws.append(fn.Discrete.two_point(np.array([2 * math.sqrt(var)])))
        lat = rs["lateral"][c] ** 2
        parts = [lat / N_LATERAL] * N_LATERAL if lateral_split == "equal" else [lat]
        laws += [fn.Discrete.two_point(np.array([2 * math.sqrt(v)])) for v in parts]
        C = np.array([[gauss + sum(law.cov()[0, 0] for law in laws)]])
        if abs(C[0, 0] / rs["C_total"][c] ** 2 - 1) > 1e-12:
            raise SystemExit(f"{cell}: the proxy's variance misses C_total by {C[0, 0] / rs['C_total'][c] ** 2 - 1:.2e}")
        null = fn.null_contents(laws, np.array([[gauss]]), C, n_mc=fn.N_MC, seed=PROXY_SEED + c)
        out[cell] = {"p": float(null["p_cell"][0]), "se": float(null["se_cell"][0]),
                     "lateral_share_of_C_total": float(lat / rs["C_total"][c] ** 2),
                     "C_model_share_of_C_total": float(rs["C_model"][c] ** 2 / rs["C_total"][c] ** 2)}
    p = np.array([v["p"] for v in out.values()])
    se = np.array([v["se"] for v in out.values()])
    null = {"p_cell": p, "se_cell": se, "q_joint": fn.P0, "se_joint": 0.0}
    thr = fn.thresholds(null)
    sz = fn.size(null, thr)
    for cell, k, s in zip(out, thr["k_cell"], sz["cell"]):
        out[cell].update({"k_flag": k, "false_flag": s})
    return {"cells": out, "min_p": float(p.min()), "median_p": float(np.median(p)), "max_se": float(se.max()),
            "cells_union_bound": sz["cells_union_bound"],
            "per_truth_with_joint_at_its_alpha": sz["cells_union_bound"] + fn.ALPHA_JOINT}


def main() -> int:
    k_cell, k_joint = flag_below(N_TOYS, CELL_CONF), flag_below(N_TOYS, JOINT_CONF)
    if (k_cell, k_joint) != (fn.flag_count(P0, N_TOYS, fn.ALPHA_CELLS / N_CELLS), fn.flag_count(P0, N_TOYS, fn.ALPHA_JOINT)):
        raise SystemExit("fd_1b_null's binomial duality disagrees with scipy's Clopper-Pearson")
    grading = {
        "p0": P0, "n_toys": N_TOYS,
        "cell": {"confidence": CELL_CONF, "flag_if_count_at_most": k_cell, "fraction": k_cell / N_TOYS,
                 "false_flag_at_p0_per_cell": power(k_cell, N_TOYS, P0),
                 "false_flag_at_p0_any_of_16_if_independent": 1 - (1 - power(k_cell, N_TOYS, P0)) ** N_CELLS,
                 "over_if_count_at_least": flag_above(N_TOYS, CELL_CONF),
                 "power": {f"{p:.2f}": power(k_cell, N_TOYS, p) for p in (0.62, 0.60, 0.58, 0.55, 0.50)}},
        "joint": {"confidence": JOINT_CONF, "flag_if_count_at_most": k_joint, "fraction": k_joint / N_TOYS,
                  "false_flag_at_p0": power(k_joint, N_TOYS, P0),
                  "power": {f"{p:.2f}": power(k_joint, N_TOYS, p) for p in (0.64, 0.62, 0.60, 0.58, 0.55)}},
        "binomial_sd_at_p0": math.sqrt(P0 * (1 - P0) / N_TOYS),
        "chi2_mean_over_ndf_se_at_ndf16": math.sqrt(2 * 16 / N_TOYS) / 16,
        "revision_0_flags": {"cell": flag_below(N_TOYS, REV0["cell_conf"]), "joint": flag_below(N_TOYS, REV0["joint_conf"])},
        "size_bound_per_truth": fn.ALPHA_CELLS + fn.ALPHA_JOINT,
        "size_bound_across": {"two_tunes": 2 * (fn.ALPHA_CELLS + fn.ALPHA_JOINT),
                              "with_plugin": 3 * (fn.ALPHA_CELLS + fn.ALPHA_JOINT)},
        "null_mc": {"n_mc": fn.N_MC, "se_at_p0": math.sqrt(P0 * (1 - P0) / fn.N_MC), "margin_se": fn.SE_MARGIN},
    }
    i2 = np.asarray(json.loads(I2.read_text())["prior_share_C_over_A"], float)
    prior = {"median": float(np.median(i2)), "min": float(i2.min()), "max": float(i2.max())}
    at_data = {split: null_at_data(split) for split in ("equal", "one_band")}
    per_truth = sum(REBUILD.values()) + TOYS
    base = 2 * per_truth + CONTROLS
    plug = per_truth + CAPTURE
    price = {
        "unit_s": UNIT_S, "s1_per_universe_node_h": S1_PER_UNIVERSE, "s1_per_seed_node_h": S1_PER_SEED,
        "per_truth": {"rebuild": REBUILD, "rebuild_total": sum(REBUILD.values()), "toys": TOYS, "total": per_truth},
        "stage1_base_items": base, "plugin_items": plug,
        "pilot": {"items": PILOT, "nodes": 1, "limit_s": 3600, "fullest_lane_s": UNIT_S, "reserved_node_h": 1.0},
        # without the plug-in the pilot's 8 items are stage 1's; with it, 7 are and the capture is the 8th
        "bulk_base": jobs(base - PILOT), "bulk_base_when_plugin": jobs(base - (PILOT - CAPTURE)),
        "bulk_plugin": jobs(plug - CAPTURE),
    }
    price["cap_base_node_h"] = 1.0 + price["bulk_base"]["reserved_node_h"]
    price["cap_with_plugin_node_h"] = 1.0 + price["bulk_base_when_plugin"]["reserved_node_h"] + price["bulk_plugin"]["reserved_node_h"]
    price["expected_base_node_h_s1_rate"] = base * S1_PER_UNIVERSE
    price["expected_with_plugin_node_h_s1_rate"] = (base + plug) * S1_PER_UNIVERSE
    price["expected_base_node_h_i2_median_8_lanes"] = base * I2_MEDIAN_S / LANES / 3600
    price["expected_with_plugin_node_h_i2_median_8_lanes"] = (base + plug) * I2_MEDIAN_S / LANES / 3600
    price["campaign_cap_with_stage0"] = {"base": STAGE0_CAP + price["cap_base_node_h"],
                                         "with_plugin": STAGE0_CAP + price["cap_with_plugin_node_h"]}
    price["half_balance"] = BALANCE / 2
    price["above_half_balance"] = price["campaign_cap_with_stage0"]["with_plugin"] > BALANCE / 2
    out = {"schema": "fd-1b-staged-arith/2", "grading": grading, "null_at_data_proxy": at_data,
           "i2_prior_share_C_over_A": prior, "price": price,
           "declared_seeds_found_in_repo": seeds_in_repo()}
    text = json.dumps(out, indent=1) + "\n"
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
