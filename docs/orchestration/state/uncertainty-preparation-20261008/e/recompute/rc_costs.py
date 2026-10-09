#!/usr/bin/env python3
"""Reviewer's independent cost arithmetic from committed sacct receipts. Own code.
python3 -I rc_costs.py REPO_ROOT > rc_costs.json
"""
import json
import os
import re
import sys

ROOT = sys.argv[1]
S = os.path.join(ROOT, "docs/orchestration/state")
out = {}


def parse(path, layout):
    rows = []
    for line in open(path):
        f = line.strip().split("|")
        if len(f) < 4:
            continue
        if layout == "ki84":
            jid, qos, st, el, tres = f[0], f[1], f[2], int(f[3]), f[4]
        else:
            jid, st, el, tres, qos = f[0], f[1], int(f[2]), f[3], f[4]
        bill = int(re.search(r"billing=(\d+)", tres).group(1))
        cpu = int(re.search(r"cpu=(\d+)", tres).group(1))
        rows.append(dict(job=jid.split("_")[0], task=jid, qos=qos, state=st, el=el, bill=bill, cpu=cpu))
    return rows


k84 = parse(os.path.join(S, "ki84-rebuild-20261006/sacct_all.txt"), "ki84")
k85 = parse(os.path.join(S, "ki85-diag-20261006/sacct_ki85.txt"), "ki85")
def nh(rows, conv):
    if conv == "billing/256":
        return sum(r["el"] / 3600 * r["bill"] / 256 for r in rows)
    if conv == "cpu/128":
        return sum(r["el"] / 3600 * r["cpu"] / 128 for r in rows)
    if conv == "whole_node":
        return sum(r["el"] / 3600 for r in rows)
by = {}
for r in k84:
    by.setdefault(r["job"], []).append(r)
out["ki84_jobs"] = {j: dict(n=len(v), states=sorted({x["state"] for x in v}), node_h=nh(v, "billing/256"),
                            node_h_cpu128=nh(v, "cpu/128"), mean_el_s=sum(x["el"] for x in v) / len(v))
                    for j, v in by.items()}
out["ki84_total_billing256"] = nh(k84, "billing/256")
out["ki85_n"] = len(k85)
out["ki85_states"] = sorted({r["state"] for r in k85})
out["ki85_total_billing256"] = nh(k85, "billing/256")
out["ki85_total_cpu128"] = nh(k85, "cpu/128")
out["iris_delta_ki84_user"] = 2024.5 - 2006.6
out["iris_delta_ki85_user"] = 2034.3 - 2027.9

per = out["ki84_jobs"]["59410433"]["node_h"] / 300
out["per_replica_shared"] = per
out["per_ki85_run"] = out["ki85_total_billing256"] / 100
# ki85 'toy' runs only (exclude pilots?) -- C says 0.0700 over 98
toy = [r for r in k85 if not r["job"].startswith("5946632") and not r["job"].startswith("5946633")]
out["ki85_excluding_pilot_jobs_n"] = len(toy)
out["ki85_excluding_pilot_per_run"] = nh(toy, "billing/256") / max(len(toy), 1)

# B totals
retry = 1.05
out["B_P_719"] = 719 * 301 * per * retry
out["B_P_1116"] = 1116 * 301 * per * retry
out["B_N2"] = 100 * out["per_ki85_run"] * retry
out["B_P_B50_719"] = 719 * 51 * per * retry
out["B_S_719"] = 719 * 1 * per * retry
out["B_N1_719_half"] = 719 * 301 * per * 0.5 * retry

# C E_C branch: one exact unfold per experiment, admitted P2 = (setup + N*(per_exp) ...)/0.8 -> re-derive from costs.json definitions
exact_s = 69523
out["exact_unfold_unpacked_node_h"] = exact_s / 3600 * 256 / 256
# packed by memory: 16.8 GB MaxRSS on a 512 GB node (487,802 MB allocatable): how many fit?
out["exact_pack_by_mem_jobs_per_node"] = 487802 / (16786760 / 1024)
out["exact_packed_node_h"] = exact_s / 3600 / (487802 // (16786760 / 1024))
print(json.dumps(out, indent=1))
