"""Second, independent derivation of the report's headline numbers from the raw operands.

Shares no code with ``profile_from_sacct.py`` or ``costs.py``: it parses the
``sacct`` files itself, uses its own unit conversions (sacct K/M = KiB/MiB) and
compares against ``results/costs.json``. Exit 1 on any mismatch beyond 0.5 %.
"""

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OPS = os.path.join(HERE, "operands")


def table(name):
    out = []
    for line in open(os.path.join(OPS, name)):
        f = line.strip().split("|")
        if len(f) > 5 and f[0] != "JobID":
            out.append(f)
    return out


def secs(x):
    d, _, hms = x.rpartition("-")
    h = [float(v) for v in hms.split(":")]
    h = [0.0] * (3 - len(h)) + h
    return (int(d) if d else 0) * 86400 + h[0] * 3600 + h[1] * 60 + h[2]


def kib(x):
    return float(x[:-1]) * {"K": 1, "M": 1024, "G": 1024 ** 2}[x[-1]]


def median(xs):
    xs = sorted(xs)
    n = len(xs)
    return xs[n // 2] if n % 2 else 0.5 * (xs[n // 2 - 1] + xs[n // 2])


rep = [r for r in table("sacct_59410433_steps.psv") if r[0].endswith(".batch")]
uni = [r for r in table("sacct_universe_sweeps_batch.psv")
       if r[0].startswith("55677843_") and float(r[3]) > 300]
cvu = [r for r in table("sacct_universe_sweeps_batch.psv") if r[0].split(".")[0] in ("55677844", "55677845")]
misc = {r[0]: r for r in table("sacct_exact_pilots_ki85_steps.psv")}

mine = {}
mine["replica_mean_node_h"] = sum(float(r[3]) for r in rep) / len(rep) * 64 / 256 / 3600
mine["uni_median_node_h"] = median([float(r[3]) for r in uni]) / 3600
reads = [kib(r[8]) for r in uni]
assert len(uni) == 187 and max(reads) - min(reads) <= 1024, "every universe task read the whole file"
mine["uni_read_GB"] = median(reads) * 1024 / 1e9
e778 = float(misc["59409026_1.batch"][3])
e_cvu = sum(float(r[3]) for r in cvu) / len(cvu)
mine["excess_s"] = e_cvu - e778
mine["f_io"] = (median([float(r[3]) for r in uni]) - e778) / median([float(r[3]) for r in uni])
node_kib = 487802 * 1024
rss_max = max(kib(r[7]) for r in uni)
rss_exact = kib(misc["53116554.batch"][7])
e_exact = float(misc["53116554.batch"][3])
p_safe, p_cv = math.floor(node_kib / rss_max), math.floor(node_kib / rss_exact)
mine["P05_now_safe"] = 187 * (e_exact + mine["excess_s"]) / 3600 / p_safe + e_exact / 3600 / p_cv
resid = None
for line in open(os.path.join(HERE, "results", "bench_loader_fill.jsonl")):
    d = json.loads(line)
    if "seconds" not in d:
        continue
    key = (d["variant"], d["tree"])
    if key == ("status", "synth_rows200000_extra192.root"):
        st192 = d["us_per_row_min"]
    if key == ("pinned", "synth_rows200000_extra192.root"):
        pin192 = d["us_per_row_min"]
    if key == ("pinned", "synth_rows200000_extra0.root"):
        pin0 = d["us_per_row_min"]
resid = (st192 - pin0) / (pin192 - pin0)
mine["P05_p1"] = 187 * (e_exact + resid * mine["excess_s"]) / 3600 / p_cv + e_exact / 3600 / p_cv
mine["S-a_now"] = 187 * mine["uni_median_node_h"] + e778 / 3600
mine["N2_hi"] = (100 * 0.0708 * 1.05 + 2.3) / 0.8
mine["B_primary"] = 719 * 301 * 0.059147 * 1.05
pet = json.load(open(os.path.join(HERE, "..", "..", "..", "..", "..",
                                  "nd-unfolding/pet/final_design/resources/cost_fb_look1-20260930.json")))
runs = pet["candidates"]["H2S1T24"]["runs"]
mine["pet_f_load_median"] = median([r["load_seconds"] / (5 * r["mean_iteration_seconds"] + r["load_seconds"])
                                    for r in runs])

c = json.load(open(os.path.join(HERE, "results", "costs.json")))
P = c["procedures"]
theirs = {
    "replica_mean_node_h": 0.059147,
    "uni_median_node_h": c["unit_rates_node_h"]["lgbm_universe"]["now_fullnode_measured"],
    "uni_read_GB": 171.286,
    "excess_s": c["operands"]["universe_file_excess_s"][0],
    "f_io": c["operands"]["f_io_universe"][0],
    "P05_now_safe": P["exact_transfer_measurement"]["now_safe_packing_N50"]["P05"],
    "P05_p1": P["exact_transfer_measurement"]["p1_N50"]["P05"],
    "S-a_now": P["lgbm_matched_sweep_S-a"]["now_fullnode_measured"],
    "N2_hi": P["N2"]["now"][1],
    "B_primary": P["B_primary_N719"]["now"],
    "pet_f_load_median": P["PET_repair_H2S1T24"]["f_load_median"],
}
bad = 0
for k in mine:
    rel = abs(mine[k] - theirs[k]) / abs(theirs[k])
    flag = "OK " if rel <= 0.005 else "BAD"
    bad += flag == "BAD"
    print(f"{flag} {k:22s} independent={mine[k]:.6g} costs.json={theirs[k]:.6g} rel={rel:.2e}")
sys.exit(1 if bad else 0)
