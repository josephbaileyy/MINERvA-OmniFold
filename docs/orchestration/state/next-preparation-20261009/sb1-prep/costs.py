#!/usr/bin/env python3
"""Price the frozen SB1 plan (``launch/launch-spec.json``) against its 2.0 node-h ceiling.

    python3 costs.py > results/costs.json

Charge rule (``operands/sacct_reference_and_billing.psv``): ``node_h = billing_cpus / 256 *
elapsed_s / 3600``. A regular full node bills 256 whatever ``--cpus-per-task`` says (55677843_166:
``billing=256`` with ``--cpus-per-task=128``); a shared job bills its cpus (59410433_1:
``billing=64``). A job's charge cannot exceed ``billing / 256 * time_limit``, its CEILING.

EXPECTED charges are forecasts, each with its source. The only Perlmutter operand for the
prototype-1 arm is speed's Amdahl estimate from a measured ``f_io`` and a laptop ``s_io``.
Selected bytes come from the real branch inventory (``operands/universe_branches.json``, the
zipped bytes of exactly the branches each loader reads in each pattern).
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = json.loads((HERE / "launch" / "launch-spec.json").read_text())
INV = json.loads((HERE / "operands" / "universe_branches.json").read_text())
BILLING_PER_NODE = 256
CEILING = SPEC["cluster"]["ceiling_node_h"]

# Historical operands (speed REPORT §3 and operands/; sacct read 2026-10-10).
U_REF_TASK_S = 2617          # 55677843_166, Muon_Energy_MINOS:0, July driver, 128 threads
U_SWEEP_S = (2350, 2547, 2751)   # 374 universe tasks min / median / max (speed §3)
F_IO, S_IO_LOCAL, S_IO_ANALYTIC = 0.695, 14.6, 68.0     # speed §3-§4
CV_REPLICA_S = (544, 840, 1900)  # 59410433, 300 shared-64 replicas, min / median / max
#: Loader-only all-branch read time, apportioned from the universe-file excess (2,547 - 778 s for
#: 171.29 GB) by each tree's zipped bytes, plus 100 s of per-row work: an ESTIMATE.
EXCESS_S_PER_GB = (2547 - 778) / 171.29
HASH_GB_PER_S = 0.5          # assumed single-stream sha256 over Lustre (not measured)


def seconds(hms):
    h, m, s = (int(x) for x in hms.split(":"))
    return 3600 * h + 60 * m + s


def billing(job):
    return BILLING_PER_NODE * job["nodes"] if job["qos"] == "regular" else job["cpus_per_task"]


def node_h(bill, secs):
    return bill / BILLING_PER_NODE * secs / 3600.0


def tree_bytes(file_key, tree, names=None):
    t = INV["files"][file_key]["trees"][tree]
    return sum(b[2] for b in t["branches"] if names is None or b[0] in names)


def selected(file_key, universe):
    """Zipped bytes of the branches each loader reads in one pattern (the rules of branch_select)."""
    sys.path.insert(0, str(HERE))
    import importlib.util
    spec = importlib.util.spec_from_file_location("bsel", HERE / "branch_select.py")
    bsel = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bsel)
    ub = None
    if universe:
        band, _, idx = universe.partition(":")
        ub = (band, int(idx))
    out = {}
    for loader, tree in bsel.LOADER_TREES.items():
        present = {b[0] for b in INV["files"][file_key]["trees"][tree]["branches"]}
        settings = {"use_weights": True, "universe_branch": ub, "alt_universe_branch": None}
        names = bsel.expected_branches(loader, settings, present)
        out[tree] = {"branches": names, "zip_bytes": tree_bytes(file_key, tree, set(names)),
                     "tree_zip_bytes": tree_bytes(file_key, tree)}
    return out


def main():
    uni = next(k for k in INV["files"] if k.endswith("universes_full.root"))
    cv = next(k for k in INV["files"] if k.endswith("MEFHC.root"))
    patterns = {"lateral " + SPEC["universes"]["lateral"]: selected(uni, SPEC["universes"]["lateral"]),
                "vertical " + SPEC["universes"]["vertical"]: selected(uni, SPEC["universes"]["vertical"]),
                "CV (CV file)": selected(cv, None)}
    for p in patterns.values():
        p["total_selected_zip_bytes"] = sum(t["zip_bytes"] for t in p.values() if isinstance(t, dict))
        p["total_file_tree_zip_bytes"] = sum(t["tree_zip_bytes"] for t in p.values()
                                             if isinstance(t, dict))

    amdahl = lambda s: 1.0 / ((1.0 - F_IO) + F_IO / s)        # noqa: E731
    sig_gb = tree_bytes(uni, "mc_signal_reco") / 1e9
    tru_gb = tree_bytes(uni, "mc_truth_denom") / 1e9
    bkg_gb = (tree_bytes(uni, "mc_background") + tree_bytes(uni, "data")) / 1e9
    j1_all_s = max(sig_gb, tru_gb, bkg_gb) * EXCESS_S_PER_GB + 100.0   # parallel processes
    j1_sel_s = 3 * 120.0                                             # cached small reads, assumed
    uni_bytes = 171117087867
    cv_bytes = 2144008221
    hash_s = (uni_bytes + cv_bytes) / 1e9 / HASH_GB_PER_S + 30.0
    expected_s = {
        "H0": (hash_s, f"{HASH_GB_PER_S} GB/s assumed sha256 rate over 173.3 GB, +30 s start"),
        "UL": (U_REF_TASK_S, "55677843_166 elapsed (same universe, argv and node shape; July driver)"),
        "SL": (U_REF_TASK_S / amdahl(S_IO_LOCAL),
               f"Amdahl, f_io={F_IO} (Perlmutter), s_io={S_IO_LOCAL} (laptop): "
               f"S={amdahl(S_IO_LOCAL):.3f}; analytic s={S_IO_ANALYTIC} gives "
               f"{U_REF_TASK_S / amdahl(S_IO_ANALYTIC):.0f} s"),
        "J1": (j1_all_s + j1_sel_s + 60.0,
               f"signal tree {sig_gb:.1f} GB x {EXCESS_S_PER_GB:.2f} s/GB + 100 s (parallel with "
               f"truth and background), + 3 x 120 s selective, + 60 s controls: an estimate"),
        "C": (CV_REPLICA_S[1] + 2 * 130.0,
              "59410433 median 840 s + two CV-file loader passes of ~130 s (speed §3 per-row cost)"),
        "H1": (hash_s + 120.0, "as H0, + 120 s for sb1_verify.py"),
    }
    jobs, tot_ceiling, tot_expected = [], 0.0, 0.0
    for job in SPEC["jobs"]:
        b = billing(job)
        lim = seconds(job["time"])
        e_s, src = expected_s[job["id"]]
        e_s = min(e_s, lim)
        rec = {"id": job["id"], "qos": job["qos"], "cpus_per_task": job["cpus_per_task"],
               "billing_cpus": b, "time_limit_s": lim, "ceiling_node_h": node_h(b, lim),
               "expected_elapsed_s": round(e_s, 1), "expected_node_h": node_h(b, e_s),
               "expected_source": src}
        tot_ceiling += rec["ceiling_node_h"]
        tot_expected += rec["expected_node_h"]
        jobs.append(rec)
    slack = CEILING - tot_ceiling
    retry = {j["id"]: {"ceiling_node_h": j["ceiling_node_h"],
                       "admissible_from_ceiling_slack_alone": j["ceiling_node_h"] <= slack}
             for j in jobs}
    out = {
        "schema": "sb1-costs/1",
        "charge_rule": SPEC["cluster"]["charge_rule"],
        "ceiling_node_h": CEILING,
        "jobs": jobs,
        "total_ceiling_node_h": tot_ceiling,
        "total_expected_node_h": tot_expected,
        "ceiling_slack_node_h": slack,
        "retry_admissibility": retry,
        "worst_case_sl_reaches_its_limit": {
            "note": "SL at its 1,800 s limit means elapsed >= 0.69 x UL's reference: the elapsed "
                    "criterion (<= 0.5 x UL) has failed, so SL needs no retry for a verdict",
            "sl_limit_over_ul_reference": seconds("00:30:00") / U_REF_TASK_S},
        "selected_bytes": patterns,
        "universe_file_reads_by_sb1_gb": {
            "UL": uni_bytes / 1e9, "SL": patterns["lateral " + SPEC["universes"]["lateral"]]
            ["total_selected_zip_bytes"] / 1e9,
            "J1_all": (tree_bytes(uni, "mc_signal_reco") + tree_bytes(uni, "mc_truth_denom") +
                       tree_bytes(uni, "mc_background") + tree_bytes(uni, "data")) / 1e9,
            "J1_selective": patterns["vertical " + SPEC["universes"]["vertical"]]
            ["total_selected_zip_bytes"] / 1e9,
            "H0": uni_bytes / 1e9, "H1": uni_bytes / 1e9},
        "peak_memory_per_job": {
            "UL": "64.5-186.6 GB observed on 374 universe tasks (55677843_166: 69,191,672 KiB = "
                  "70.85 GB); full node 487,802 MiB",
            "SL": "success bound 30 GB; local evidence only",
            "J1": "estimate ~70 GB for three parallel all-branch loader processes (0.26-0.31 x "
                  "bytes read, speed §4, plus Python lists); allocation 121,920 MiB = 127.8 GB",
            "C": "59410433_1: 16,296,360 KiB = 16.7 GB; allocation 127.8 GB",
            "H0/H1": "< 1 GB"},
        "simultaneous": "jobs are serialized by afterok/afterany, so peak simultaneous memory "
                        "across SB1 is one job's",
    }
    json.dump(out, sys.stdout, indent=1, sort_keys=True)
    print()


if __name__ == "__main__":
    main()
