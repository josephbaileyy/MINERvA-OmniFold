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
        no family is unusable, so it fails closed. The slim job asks for 32G (sized for the largest playlist block,
        1M's 5,917,406 rows), twice the 16G request, so it is charged SLIM_RATE = 2 x SHARED_RATE (amendment 3).
        Exit 0 within, 3 over, 2 unusable.
    geanttw_sacct.py completed --sacct PSV --submissions LOG NAME...
        each NAME has exactly one submissions.log line, and sacct lists that id, under that name, as COMPLETED.
        Downstream steps use it, so an output left by a job that exited nonzero (for example 20, a failed
        after-stamp) is never consumed. Exit 0 all COMPLETED, 3 refuse, 2 unusable.
    geanttw_sacct.py pilot --sacct PSV --submissions LOG
        P2's pilot gate (AMENDMENT-P2P3.md A2): the read-traced pilot geanttw_p2_pilot_1B and its untraced reference
        geanttw_p2_pilotref_1B, each the id its submissions.log line names, are both COMPLETED in sacct, and
        ElapsedRaw(pilot) / ElapsedRaw(pilotref) <= PILOT_RATIO = 3, the factor P2's limits assume (the director's
        ruling, 2026-11-27). The measured extra cost is recorded. Exit 0 pass, 3 refuse (a STOP to the director), 2
        unusable.
PSV rows are `sacct -X -n -P -o JobID,JobName,State,ElapsedRaw,NNodes,TimelimitRaw[,AllocTRES]`. The fences read
the first six columns. The cap gate also reads AllocTRES when present (the director's ruling, 2026-11-27): a job's
billed rate is billing / BILLING_PER_NODE node-h per hour, where a Perlmutter CPU node bills 256
(stageC/production/jobs.tsv: 128 CPUs bill 0.5). Each job is charged at the larger of its family's rate and its
billed rate, and both totals are reported. SHARED_RATE 0.0391 is 10/256: P0's two jobs had AllocCPUS 10.
"""
import argparse
import json
import re
import sys

CAP = 8.0
SHARED_RATE = 0.0391
UNFOLD_RATE = 0.5
SLIM_RATE = 2 * SHARED_RATE
PILOT_RATIO = 3.0
BILLING_PER_NODE = 256.0
PILOT_PAIR = ("geanttw_p2_pilot_1B", "geanttw_p2_pilotref_1B")
TERMINAL = {"COMPLETED", "FAILED", "CANCELLED", "TIMEOUT", "OUT_OF_MEMORY", "NODE_FAIL", "PREEMPTED", "BOOT_FAIL",
            "DEADLINE"}
P2_PL = "(1A|1B|1C|1D|1E|1F|1G|1M|1N|1O|1P)"   # P2 reuses P0's 1L output
FAMILIES = (
    (re.compile(r"^geanttw_p0_(pin|pat)_1L$"), SHARED_RATE),
    (re.compile(r"^geanttw_p2_" + P2_PL + r"$"), SHARED_RATE),
    (re.compile(r"^geanttw_p2_(pilot|pilotref)_1B$"), SHARED_RATE),   # the pilot playlist is 1B only
    (re.compile(r"^geanttw_(p2_c2pre|p3_extract_(pin|all))$"), SHARED_RATE),
    (re.compile(r"^geanttw_p3_slim$"), SLIM_RATE),
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
        out.append(f[:6] + [f[6] if len(f) > 6 else ""])
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


def billed_rate(tres):
    """node-h per hour from an AllocTRES field's billing=N, or None when sacct gave none (a pending job)."""
    m = re.search(r"(?:^|,)billing=(\d+)(?:,|$)", tres or "")
    return int(m.group(1)) / BILLING_PER_NODE if m else None


def cap(sacct_lines, submission_lines, want_name, want_limit, cap_=CAP):
    want_rate = rate(want_name)
    listed, spent, held, unlisted = set(), 0.0, 0.0, []
    spent_family, spent_billed = 0.0, 0.0
    for jid, name, state, elapsed, _nodes, limit_min, tres in rows(sacct_lines):
        listed.add(jid)
        if not name.startswith("geanttw_"):
            continue
        fam, bill = rate(name), billed_rate(tres)
        r = max(fam, bill or 0.0)
        if not live(state):
            if not elapsed.strip().isdigit():
                raise Unusable("an ended geanttw_ job without ElapsedRaw: %r" % jid)
            h = int(elapsed) / 3600.0
            spent += h * r
            spent_family += h * fam
            spent_billed += h * (bill if bill is not None else fam)
        else:
            if not limit_min.isdigit():
                raise Unusable("a live geanttw_ job without a finite limit: %r" % jid)
            held += int(limit_min) / 60.0 * r
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
    return {"spent": spent, "spent_at_family_rates": spent_family, "spent_at_billed_rates": spent_billed,
            "held": held, "unlisted_ids": unlisted, "want": want_name, "want_ceiling": want,
            "total": total, "cap": cap_, "pass": total <= cap_}


def submissions(lines):
    out = {}
    for ln in lines:
        if ln.startswith("SUBMIT "):
            kv = dict(x.split("=", 1) for x in ln.split()[1:] if "=" in x)
            if not kv.get("id") or not kv.get("name"):
                raise Unusable("a submissions.log line without id or name: %r" % ln)
            out.setdefault(kv["name"], []).append(kv["id"])
    return out


def completed(sacct_lines, submission_lines, names):
    """{name: {id, state, elapsed}} and the refusals: each name submitted once and COMPLETED in sacct."""
    subs = submissions(submission_lines)
    by_id = {f[0]: f for f in rows(sacct_lines)}
    rec, why = {}, []
    for name in names:
        ids = subs.get(name, [])
        if len(ids) != 1:
            raise Unusable("%s has %d submissions.log lines, not 1" % (name, len(ids)))
        row = by_id.get(ids[0])
        if row is None or row[1] != name:
            why.append("%s (id %s) is not in sacct under that name" % (name, ids[0]))
            continue
        if not row[3].strip().isdigit():
            raise Unusable("%s (id %s) has no ElapsedRaw: %r" % (name, ids[0], row[3]))
        rec[name] = {"id": ids[0], "state": row[2], "elapsed": int(row[3])}
        if (row[2].split() or [""])[0] != "COMPLETED":
            why.append("%s is %s, not COMPLETED" % (name, row[2]))
    return rec, why


def pilot(sacct_lines, submission_lines):
    rec, why = completed(sacct_lines, submission_lines, PILOT_PAIR)
    if not why:
        e_pil, e_ref = rec[PILOT_PAIR[0]]["elapsed"], rec[PILOT_PAIR[1]]["elapsed"]
        rec["extra_node_h"] = max(e_pil - e_ref, 0) / 3600.0 * SHARED_RATE
        if e_ref <= 0:
            why.append("the untraced reference has ElapsedRaw %d: no ratio" % e_ref)
        else:
            rec["ratio"] = e_pil / float(e_ref)
            if rec["ratio"] > PILOT_RATIO:
                why.append("the traced pilot took %.2fx the untraced reference, over %.0fx: STOP to the director"
                           % (rec["ratio"], PILOT_RATIO))
    rec["refusals"] = why
    rec["pass"] = not why
    return rec


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
    q = sub.add_parser("pilot")
    q.add_argument("--sacct", required=True)
    q.add_argument("--submissions", required=True)
    d = sub.add_parser("completed")
    d.add_argument("--sacct", required=True)
    d.add_argument("--submissions", required=True)
    d.add_argument("names", nargs="+")
    a = p.parse_args(argv)
    try:
        with open(a.sacct) as fh:
            lines = fh.read().splitlines()
        if a.cmd == "fence":
            hits = fence(lines, a.regex)
            for h in hits:
                print("LIVE %s" % "|".join(h[:3]))
            return 3 if hits else 0
        try:
            with open(a.submissions) as fl:
                subs = fl.read().splitlines()
        except FileNotFoundError:
            subs = []
        if a.cmd == "completed":
            got, why = completed(lines, subs, a.names)
            rec = {"jobs": got, "refusals": why, "pass": not why}
        else:
            rec = pilot(lines, subs) if a.cmd == "pilot" else cap(lines, subs, a.name, a.limit)
        print(json.dumps(rec, sort_keys=True))
        return 0 if rec["pass"] else 3
    except (Unusable, ValueError, OSError) as e:
        print(json.dumps({"error": str(e)}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
