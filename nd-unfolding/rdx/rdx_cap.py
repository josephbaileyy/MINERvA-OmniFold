"""RDX's charge gate (RDX-DECLARATION.md §5; the director's ruling of 2026-11-12, after COV2D's sacct-lag lesson).

Before every submit the connect runs this on a fresh sacct snapshot and the lane's submissions log:
    spent = the charge of every ended rdx_ job sacct lists;
    held  = the ceiling of every other rdx_ job sacct lists (any state not known terminal), plus the ceiling of every
            submissions.log line whose id sacct does not list (sacct lags sbatch by seconds);
    total = spent + held + the wanted job's ceiling, which must be at most the cap, 2.5 node-h.
Charges: an exclusive job (rdx_s2_merge, rdx_s3_a, rdx_s3_b) is wall time x nodes; a shared event-loop job (rdx_s1_<PL>,
rdx_s2_<PL>) is wall time x 0.0391 node-h per hour, the rate MP-1's S1 1A job was billed for the same request
(phase1/LEDGER.tsv:25: 0.05688 node-h over 5,242 s). A ceiling is the time limit at the same rate.
Runs under the login node's /usr/bin/python3 (3.6). Exit 0 within the cap, 3 over it, 2 on unusable input.

    python3 -I -B rdx_cap.py --sacct <psv> --submissions <log> --name <job name> --limit HH:MM:SS
where <psv> holds sacct -X -n -P -o JobID,JobName,State,ElapsedRaw,NNodes,TimelimitRaw rows.
"""
import argparse
import json
import re
import sys

CAP = 2.5
SHARED_RATE = 0.0391
TERMINAL = {"COMPLETED", "FAILED", "CANCELLED", "TIMEOUT", "OUT_OF_MEMORY", "NODE_FAIL", "PREEMPTED", "BOOT_FAIL",
            "DEADLINE"}
PLAYLISTS = ("1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P")
EXCLUSIVE = ("rdx_s2_merge", "rdx_s3_a", "rdx_s3_b")


class Unusable(Exception):
    pass


def kind(name):
    """'shared', 'exclusive' or None (not an RDX job name)."""
    if name in EXCLUSIVE:
        return "exclusive"
    m = re.match(r"^rdx_s([12])_([0-9][A-Z])$", name)
    if m and m.group(2) in PLAYLISTS and (m.group(1) == "2" or m.group(2) == "1A"):
        return "shared"
    return None


def hms(t):
    h, m, s = (int(x) for x in t.split(":"))
    return 3600 * h + 60 * m + s


def per_hour(name, nodes=1):
    k = kind(name)
    if k is None:
        raise Unusable("not an RDX job name: %r" % name)
    return SHARED_RATE if k == "shared" else max(int(nodes or 1), 1)


def recompute(sacct_lines, submission_lines, want_name, want_limit, cap=CAP):
    listed, spent, held, unlisted = set(), 0.0, 0.0, []
    for ln in sacct_lines:
        if not ln.strip():
            continue
        f = ln.split("|")
        if len(f) < 6:
            raise Unusable("a sacct row without the six columns: %r" % ln)
        jid, name, state, elapsed, nodes, limit_min = f[:6]
        listed.add(jid)
        if not name.startswith("rdx_"):
            continue
        rate = per_hour(name, nodes)
        if state.split()[0] in TERMINAL:
            spent += int(elapsed or 0) / 3600.0 * rate
        else:
            if not limit_min.isdigit():
                raise Unusable("an unfinished rdx_ job without a finite limit: %r" % ln)
            held += int(limit_min) * 60 / 3600.0 * rate
    for ln in submission_lines:
        if not ln.startswith("SUBMIT "):
            continue
        kv = dict(x.split("=", 1) for x in ln.split()[1:] if "=" in x)
        if not kv.get("id") or not kv.get("limit") or not kv.get("name"):
            raise Unusable("a submissions.log line without id, name or limit: %r" % ln)
        if kv["id"] not in listed:
            held += hms(kv["limit"]) / 3600.0 * per_hour(kv["name"])
            unlisted.append(kv["id"])
    want = hms(want_limit) / 3600.0 * per_hour(want_name)
    total = spent + held + want
    return {"spent": spent, "held": held, "unlisted_ids": unlisted, "want": want_name, "want_ceiling": want,
            "total": total, "cap": cap, "pass": total <= cap}


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--sacct", required=True)
    p.add_argument("--submissions", required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--limit", required=True)
    a = p.parse_args(argv)
    try:
        with open(a.sacct) as fs, open(a.submissions) as fl:
            rec = recompute(fs.read().splitlines(), fl.read().splitlines(), a.name, a.limit)
    except (Unusable, ValueError, OSError) as e:
        print(json.dumps({"error": str(e)}))
        return 2
    print(json.dumps(rec))
    return 0 if rec["pass"] else 3


if __name__ == "__main__":
    sys.exit(main())
