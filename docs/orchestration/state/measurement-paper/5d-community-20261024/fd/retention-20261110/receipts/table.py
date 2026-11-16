"""AT-RISK.md's table, from the GROUP lines of receipts/session.txt (raw epoch atimes, UTC). Exposure is the oldest
atime + 8 weeks (FD-CT-RETENTION.md §1). Usage: python3 -I table.py session.txt"""
import datetime as d
import sys
NEED = {"univ2d_per_playlist": "RPL (i) band size", "anatuple_data_1A": "RPL (ii-a) join", "anatuple_mc_1A": "RPL (ii-a) join",
        "anatuple_data_1B-1P": "RPL (ii-a) join", "anatuple_mc_1B-1P": "RPL (ii-a) join", "zero_loops": "RPL (ii-a)",
        "cpl": "V-HALF-R §3 (C_PL,5D)", "s1_cmodel_cresp_tables": "V-HALF-R §3; Tier 2 (done)", "f0b": "V-HALF-R steps 2-4",
        "rpd_dumps": "RPD-RECO; RPL (i), (ii-b)", "central": "E96D A-D0/A-D1; V-HALF-R", "cstat": "V-HALF-R §3 (C_stat)",
        "tier3_inputs": "Tier 3 (FD-PRR's staged inputs, rho arrays)", "shared_inputs": "E96D; Tier 3; V-HALF-R",
        "prr": "Tier 3 (C-PAIR, C-P); V-HALF-R step 3"}
rows = []
for l in open(sys.argv[1]):
    if not l.startswith("GROUP "):
        continue
    p = l.split()
    f = dict(x.split("=") for x in p[2:])
    o = d.datetime.fromtimestamp(int(f["oldest_atime"]), d.timezone.utc)
    rows.append((o + d.timedelta(weeks=8), p[1], int(f["found"]), int(f["missing"]), int(f["bytes"]), o, f["oldest_atime"]))
print("| exposed from | group | needed by | files (missing) | bytes | oldest atime (UTC; epoch) |")
print("|---|---|---|---:|---:|---|")
for e, g, n, m, b, o, raw in sorted(rows):
    print(f"| **{e:%Y-%m-%d}** | `{g}` | {NEED[g]} | {n:,} ({m}) | {b:,} | {o:%Y-%m-%d %H:%M}; {raw} |")
