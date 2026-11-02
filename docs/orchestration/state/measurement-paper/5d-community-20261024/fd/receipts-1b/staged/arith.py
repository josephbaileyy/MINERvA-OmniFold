"""Arithmetic of the staged 1B declaration (FD-1B-STAGED-DECLARATION.md sections 5, 7 and 8): the grading
thresholds and their power, the item counts and the price, and the seed ranges' absence from the repository.

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

from scipy.stats import beta, binom

P0 = math.erf(1 / math.sqrt(2))          # 0.682689..., the 1-sigma two-sided content
N_TOYS = 300
N_CELLS = 16
ALPHA = 0.05
CELL_CONF = 1 - ALPHA / N_CELLS          # one-sided, Bonferroni over the 16 cells
JOINT_CONF = 1 - ALPHA                   # one-sided

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
         "plugin_toys": range(3_640_000, 3_640_300), "plugin_stat": [3_641_000]}


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


def main() -> int:
    k_cell, k_joint = flag_below(N_TOYS, CELL_CONF), flag_below(N_TOYS, JOINT_CONF)
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
    }
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
    out = {"schema": "fd-1b-staged-arith/1", "grading": grading, "price": price,
           "declared_seeds_found_in_repo": seeds_in_repo()}
    text = json.dumps(out, indent=1) + "\n"
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
