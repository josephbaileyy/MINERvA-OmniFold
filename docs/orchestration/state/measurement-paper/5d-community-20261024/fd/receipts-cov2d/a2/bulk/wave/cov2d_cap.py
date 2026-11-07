"""COV2D's connect-side charge recompute (the director's ruling on the gate's sacct lag, 2026-11-06). Not A2's code.

The gate (cov2d_jobs.gate) prices unfinished attempts only from the sacct snapshot it reads. sacct lags sbatch by
seconds, so a job submitted just before can be missing, and held undercounted. This recompute is independent of the
gate's code and tables:
    spent = ElapsedRaw x NNodes of every ended cov2d-* attempt sacct lists;
    held  = TimelimitRaw x NNodes of every other cov2d-* attempt sacct lists (any state not known terminal), plus
            the limit of every submissions.log line at M whose id sacct does not list (one node: each cov2d sbatch
            asks for one);
    total = spent + held + the wanted job's limit, which must be at most the cap.
Runs under the login node's /usr/bin/python3 (3.6). Exit 0 when within the cap, 3 when over it, 2 on unusable input.

    python3 -I -B cov2d_cap.py --sacct <psv> --submissions <submissions.log> --M <M> --limit HH:MM:SS
where <psv> holds sacct -X -n -P -o JobID,JobName,State,ElapsedRaw,NNodes,TimelimitRaw rows.
"""
import argparse
import json
import sys

CAP = 165.8
TERMINAL = {"COMPLETED", "FAILED", "CANCELLED", "TIMEOUT", "OUT_OF_MEMORY", "NODE_FAIL", "PREEMPTED", "BOOT_FAIL",
            "DEADLINE"}


class Unusable(Exception):
    pass


def hms(t):
    h, m, s = (int(x) for x in t.split(":"))
    return 3600 * h + 60 * m + s


def recompute(sacct_lines, submission_lines, M, want_limit, cap=CAP):
    listed, spent, held, unlisted = set(), 0.0, 0.0, []
    for ln in sacct_lines:
        if not ln.strip():
            continue
        f = ln.split("|")
        if len(f) < 6:
            raise Unusable("a sacct row without the six columns: %r" % ln)
        jid, name, state, elapsed, nodes, limit_min = f[:6]
        listed.add(jid)
        if not name.startswith("cov2d-"):
            continue
        n = max(int(nodes or 1), 1)
        if state.split()[0] in TERMINAL:
            spent += int(elapsed or 0) / 3600 * n
        else:
            if not limit_min.isdigit():
                raise Unusable("an unfinished cov2d attempt without a finite limit: %r" % ln)
            held += int(limit_min) * 60 / 3600 * n
    for ln in submission_lines:
        kv = dict(x.split("=", 1) for x in ln.split()[1:] if "=" in x)
        if kv.get("M") != M:
            continue
        if not kv.get("id") or not kv.get("limit"):
            raise Unusable("a submissions.log line at M without id or limit: %r" % ln)
        if kv["id"] not in listed:
            held += hms(kv["limit"]) / 3600
            unlisted.append(kv["id"])
    want = hms(want_limit) / 3600
    total = spent + held + want
    return {"spent": spent, "held": held, "unlisted_ids": unlisted, "want_node_h": want, "total": total, "cap": cap,
            "pass": total <= cap}


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--sacct", required=True)
    p.add_argument("--submissions", required=True)
    p.add_argument("--M", required=True)
    p.add_argument("--limit", required=True)
    a = p.parse_args(argv)
    try:
        with open(a.sacct) as fs, open(a.submissions) as fl:
            rec = recompute(fs.read().splitlines(), fl.read().splitlines(), a.M, a.limit)
    except (Unusable, ValueError, OSError) as e:
        print(json.dumps({"error": str(e)}))
        return 2
    print(json.dumps(rec))
    return 0 if rec["pass"] else 3


if __name__ == "__main__":
    sys.exit(main())
