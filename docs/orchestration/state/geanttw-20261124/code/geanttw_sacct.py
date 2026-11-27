#!/usr/bin/env python3
"""geanttw's sacct readers (DECLARATION.md §3, §7): the fence and the cap gate. sacct only, never squeue (the
standing rule, cov2d_fence.sh:3). Runs under the login node's /usr/bin/python3 (3.6) and inside jobs.

    geanttw_sacct.py fence --sacct PSV --regex REGEX
        exit 0 clear; 3 if any row whose JobName matches REGEX is in a state not known terminal (fail-closed:
        unknown states count as live); 2 on unusable input (a row without the columns).
    geanttw_sacct.py cap --sacct PSV --submissions LOG --name NAME --limit HH:MM:SS
        spent = the charge of every ended geanttw_ job; held = the ceiling of every other geanttw_ job sacct lists,
        plus every submissions.log line whose id sacct does not list (sacct lags sbatch); total = spent + held + the
        wanted job's ceiling, which must be at most CAP. Each job is charged at its family's rate (FAMILIES) in node-h
        per hour of wall (ceiling: of time limit). The 2-CPU, 16 GB shared jobs (P0, P2, the C2 checks and the slim
        build) use SHARED_RATE, RDX's measured rate for that request (nd-unfolding/rdx/rdx_cap.py SHARED_RATE, from
        MP-1's phase1/LEDGER.tsv:25). P3's universe unfolds use Stage C's request (128 CPUs, 243840M, shared), billed
        128 of 256, so UNFOLD_RATE = 0.5 (stageC/production/jobs.tsv: 0.2500 node-h at 00:30:00). A geanttw_ name in
        no family is unusable, so it fails closed. Exit 0 within, 3 over, 2 unusable.
PSV rows are `sacct -X -n -P -o JobID,JobName,State,ElapsedRaw,NNodes,TimelimitRaw`.
"""
import argparse
import json
import re
import sys

CAP = 8.0
SHARED_RATE = 0.0391
UNFOLD_RATE = 0.5
TERMINAL = {"COMPLETED", "FAILED", "CANCELLED", "TIMEOUT", "OUT_OF_MEMORY", "NODE_FAIL", "PREEMPTED", "BOOT_FAIL",
            "DEADLINE"}
P2_PL = "(1A|1B|1C|1D|1E|1F|1G|1M|1N|1O|1P)"   # P2 reuses P0's 1L output
FAMILIES = (
    (re.compile(r"^geanttw_p0_(pin|pat)_1L$"), SHARED_RATE),
    (re.compile(r"^geanttw_p2_(pilot_|pilotref_)?" + P2_PL + r"$"), SHARED_RATE),
    (re.compile(r"^geanttw_(p2_c2pre|p3_c2|p3_slim|p3_extract_(pin|all))$"), SHARED_RATE),
    (re.compile(r"^geanttw_p3_unf_(pin|pinov|patov)_GEANT_(Neutron|Pion|Proton)_[01]$"), UNFOLD_RATE),
)


def rate(name):
    """The node-h per hour of wall of a geanttw job name's family; unusable if the name is in none."""
    for rx, r in FAMILIES:
        if rx.match(name):
            return r
    raise Unusable("not a geanttw job name: %r" % name)


class Unusable(Exception):
    pass


def rows(lines):
    out = []
    for ln in lines:
        if not ln.strip():
            continue
        f = ln.split("|")
        if len(f) < 6 or not f[0].strip():
            raise Unusable("a sacct row without the six columns: %r" % ln)
        out.append(f[:6])
    return out


def live(state):
    return state.split()[0] not in TERMINAL if state.strip() else True


def fence(lines, regex):
    r = re.compile(regex)
    return [f for f in rows(lines) if r.search(f[1]) and live(f[2])]


def hms(t):
    m = re.match(r"^(\d+):([0-5]\d):([0-5]\d)$", t)
    if not m:
        raise Unusable("not HH:MM:SS: %r" % t)
    return 3600 * int(m.group(1)) + 60 * int(m.group(2)) + int(m.group(3))


def cap(sacct_lines, submission_lines, want_name, want_limit, cap_=CAP):
    want_rate = rate(want_name)
    listed, spent, held, unlisted = set(), 0.0, 0.0, []
    for jid, name, state, elapsed, _nodes, limit_min in rows(sacct_lines):
        listed.add(jid)
        if not name.startswith("geanttw_"):
            continue
        if not live(state):
            spent += int(elapsed or 0) / 3600.0 * rate(name)
        else:
            if not limit_min.isdigit():
                raise Unusable("a live geanttw_ job without a finite limit: %r" % jid)
            held += int(limit_min) / 60.0 * rate(name)
    for ln in submission_lines:
        if not ln.startswith("SUBMIT "):
            continue
        kv = dict(x.split("=", 1) for x in ln.split()[1:] if "=" in x)
        if not kv.get("id") or not kv.get("limit") or not kv.get("name"):
            raise Unusable("a submissions.log line without id, name or limit: %r" % ln)
        if kv["id"] not in listed:
            held += hms(kv["limit"]) / 3600.0 * rate(kv["name"])
            unlisted.append(kv["id"])
    want = hms(want_limit) / 3600.0 * want_rate
    total = spent + held + want
    return {"spent": spent, "held": held, "unlisted_ids": unlisted, "want": want_name, "want_ceiling": want,
            "total": total, "cap": cap_, "pass": total <= cap_}


def main(argv=None):
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd")
    sub.required = True   # argparse then exits 2 with usage when no subcommand is given
    f = sub.add_parser("fence")
    f.add_argument("--sacct", required=True)
    f.add_argument("--regex", required=True)
    c = sub.add_parser("cap")
    c.add_argument("--sacct", required=True)
    c.add_argument("--submissions", required=True)
    c.add_argument("--name", required=True)
    c.add_argument("--limit", required=True)
    a = p.parse_args(argv)
    try:
        with open(a.sacct) as fh:
            lines = fh.read().splitlines()
        if a.cmd == "fence":
            hits = fence(lines, a.regex)
            for h in hits:
                print("LIVE %s" % "|".join(h[:3]))
            return 3 if hits else 0
        try:   # cap: the only other subcommand argparse admits
            with open(a.submissions) as fl:
                subs = fl.read().splitlines()
        except FileNotFoundError:
            subs = []
        rec = cap(lines, subs, a.name, a.limit)
        print(json.dumps(rec, sort_keys=True))
        return 0 if rec["pass"] else 3
    except (Unusable, ValueError, OSError) as e:
        print(json.dumps({"error": str(e)}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
