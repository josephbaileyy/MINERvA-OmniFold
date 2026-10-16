#!/usr/bin/env python3
"""Stage C production launcher, regular-QOS packed path: the grant's charge gate, then sbatch of single-node packs
of frozen jobs.tsv rows (DESIGN §14; AUTHORIZATION-20261016-2d-closeout-stageC-regular-packing.md).

  python launch.py gate   <batch>                                 print the packs and the gate arithmetic; submit nothing
  python launch.py submit <batch>                                 gate, preconditions, then sbatch each pack of the
                                                                  rows owed a first submission (compose())
  python launch.py submit <batch> --retry A[,B..] --time HH:MM:SS one walltime-retry pack of members whose only
                                                                  attempt is a TIMEOUT
  python launch.py redo   <batch>                                 resubmit deadline-cancelled retry packs (owed_retries())
  python launch.py pack   A,B,C,D                                 one pack of the named owed rows (the smoke pack)
  python launch.py migrate [--only A,B..] [--execute]             list (and with --execute, scancel --state=PENDING) the
                                                                  never-started shared-QOS 2dc_P_* jobs, from squeue now
  python launch.py members <jobid>                                a pack's members, their rc, step state and status
  python launch.py simulate {mean,p84,cap}                        the worked example of DESIGN §6 (no Slurm)

Runs on a NERSC login node from the deployed package ($NS/repo_k/docs/orchestration/state/2d-closeout/stageC/production).
The shared-QOS launcher of the binding (4139548b) is the base: same gate, same namespace, same order and
preconditions, same retry rules. What changes is the unit of submission (DESIGN §14):

PACKS. A pack is one regular-QOS node (billing 256) running up to 256/cpus members of one class (cpus, mem, cap) as
`srun --exact` steps (sbatch_pack.sh). A full pack's enforced charge, 256 x cap / 256, equals the sum of its members'
row caps (4 x 0.2125 = 0.85 for CV rows; 2 x 0.25 = 0.5 for S4U rows). compose() chunks, per class and in the frozen
order, every row owed a first submission; a partial chunk waits for the next batch unless the batch is the class's
last. Pack names: 2dc_P_K<n>_<first member without 2dc_P_>. Before sbatch, the members are written to
$NS/packs/<pack name>.members (the dispatcher refuses arguments that differ); after it, to $NS/packs/<job id>.members,
which is how the ledger maps a pack job to its members. A pack job with no such record is refused (fail closed).

GATE (AUTHORIZATION-20261015-2d-closeout-stageC-production.md §3, unchanged): before each submission,
    charges of terminal 2dc_P_* jobs (rows and packs) from sacct (ElapsedRaw x billing / 256 / 3600)
  + the FULL enforced worst case of every 2dc_P_* job still PENDING or RUNNING (billing x TimeLimit / 256)
  + the submission's enforced worst case (256 x pack cap / 256 per pack)
  <= 100.0 charged node-h, otherwise REFUSE. `gate` only prints; a refusal by `submit` is a stop-and-report.

ATTEMPTS ARE MEMBER-LEVEL. A job that never started (DEADLINE, or CANCELLED, with ElapsedRaw 0 and no Start) is not
an attempt. Otherwise every member of a pack has one attempt, whose state is derived (member_states()):
COMPLETED only with rc 0 in $NS/packs/<job id>.status AND out/<member>/xsec.root present ("validated output");
TIMEOUT when the pack timed out and the member had no rc line or ended within 120 s of Start + TimeLimit (killed at
the limit); OUT_OF_MEMORY when the pack did; FAILED otherwise. A walltime retry needs exactly one TIMEOUT attempt
(grant §3); any other state refuses, and a FAILED member needs the director (no command here acts on it). A pack
that ran without launching its members is a STOP. sacct is read with TZ=UTC.

MAINTENANCE: maintenance_20261021 runs 2026-10-21 13:00Z to 2026-10-28 06:00Z (TZ=UTC scontrol; the regular-packing
record §2 corrects the binding's 06:00Z). Every job keeps --deadline=2026-10-20T23:00:00 PDT (06:00Z), 7 h before the
window, as that record rules; Slurm never starts a job that could not end by then. Nothing is submitted from 06:00Z.
"""
import argparse
import csv
import datetime as dt
import json
import os
import re
import subprocess
import sys
from collections import namedtuple
from pathlib import Path

if sys.version_info < (3, 9):
    raise SystemExit("REFUSE: launch.py needs Python >= 3.9; source setup_salloc_env.sh first (root_6_28 has 3.11)")
HERE = Path(__file__).resolve().parent
CEILING = 100.0
PREFIX = "2dc_P_"
PACK_PREFIX = "2dc_P_K"
PACK_QOS = "regular"
PACK_BILLING = 256
NODE_CPUS = 256
NODE_MEM_MB = 515100          # RealMemory of a regular_milan_ss11 node (scontrol show node)
KILL_MARGIN_S = 120           # a member ending within this of Start + TimeLimit was killed by the limit (KillWait 30 s)
WINDOW_START = "2026-10-15T00:00:00"
NS = "/pscratch/sd/j/josephrb/2d-closeout-stageC-production-20261015"
SBATCH = f"{NS}/repo_k/docs/orchestration/state/2d-closeout/stageC/production/sbatch_pack.sh"
DEADLINE = dt.datetime(2026, 10, 21, 6, 0, tzinfo=dt.timezone.utc)      # = 2026-10-20T23:00 PDT
MAINT_END = dt.datetime(2026, 10, 28, 6, 0, tzinfo=dt.timezone.utc)
IN_FLIGHT = ("PENDING", "RUNNING", "REQUEUED", "RESIZING", "SUSPENDED", "CONFIGURING", "COMPLETING")
ORDER = ["G0", "G1", "G2", "S1a", "S1b", "S1c", "S1d", "S1e", "S1f", "S2a", "S2b", "S4a", "S4b"]
Row = namedtuple("Row", "jid name st el kind amount start end tl", defaults=("",))


def hours(t):
    d = 0
    if "-" in t:
        dd, t = t.split("-")
        d = int(dd)
    p = [int(x) for x in t.split(":")]
    while len(p) < 3:
        p.insert(0, 0)
    return d * 24 + p[0] + p[1] / 60 + p[2] / 3600


def table():
    with open(HERE / "jobs.tsv") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def mem_mb(m):
    if not re.fullmatch(r"\d+M", m):
        raise SystemExit(f"REFUSE: memory '{m}' is not <int>M")
    return int(m[:-1])


def enforced(row, time=None):
    return int(row["billing"]) * hours(time or row["time"]) / 256


def pack_enforced(time):
    return PACK_BILLING * hours(time) / 256


def per_node(row):
    return NODE_CPUS // int(row["cpus"])


def klass(row):
    return (row["cpus"], row["mem"], row["time"])


def fit(members):
    """The identity and node-fit rules of a pack (record §4.2, §4.3). Refuses (SystemExit) or returns None."""
    names = [r["name"] for r in members]
    if not members:
        raise SystemExit("REFUSE: an empty pack")
    if len(set(names)) != len(names):
        raise SystemExit(f"REFUSE: a member repeats in {names}")
    tbl = {r["name"]: r for r in table()}
    for r in members:
        if tbl.get(r["name"]) != r:
            raise SystemExit(f"REFUSE: {r['name']} is not its jobs.tsv row")
    if len({(r["cpus"], r["mem"]) for r in members}) != 1:
        raise SystemExit(f"REFUSE: members of {names} differ in CPUs or memory")
    if len(members) > per_node(members[0]):
        raise SystemExit(f"REFUSE: {len(members)} members of {members[0]['cpus']} CPUs exceed one {NODE_CPUS}-CPU node")
    if sum(mem_mb(r["mem"]) for r in members) > NODE_MEM_MB:
        raise SystemExit(f"REFUSE: summed member memory of {names} exceeds RealMemory {NODE_MEM_MB}M")


def check_pack(members, time):
    """A first-submission pack: fit(), and the pack cap is its members' common row cap (record §4.1)."""
    fit(members)
    if {r["time"] for r in members} != {time}:
        raise SystemExit(f"REFUSE: pack cap {time} is not the common cap of {[r['name'] for r in members]}")


def check_pack_retry(members, time):
    """A walltime-retry pack: fit(); its cap is the re-projected --time every member's retry record will carry."""
    fit(members)
    if hours(time) >= 12:
        raise SystemExit("REFUSE: a retry cap must be under 12 h")


def pack_name(members):
    return f"{PACK_PREFIX}{len(members)}_{members[0]['name'][len(PREFIX):]}"


def is_pack(name):
    return name.startswith(PACK_PREFIX)


def never_started(st, el, start):
    return (st == "DEADLINE" and el == 0) or (st == "CANCELLED" and el == 0 and start in ("Unknown", "None", ""))


def ledger():
    """Every 2dc_P_* job (rows and packs) since the window start: (completed charge, in-flight enforced, Rows).

    An in-flight job's liability uses the larger of its expected billing (jobs.tsv, or 256 for a pack) and any billing
    Slurm reports (AllocTRES, else ReqTRES); the dispatcher refuses at start a pack whose billing is not 256."""
    tbl = {r["name"]: int(r["billing"]) for r in table()}
    cmd = ["sacct", "-X", "-P", "-S", WINDOW_START, "-E", "now", "-u", os.environ.get("USER", "josephrb"),
           "-o", "JobID,JobName,State,ElapsedRaw,AllocTRES,Timelimit,ReqTRES,Start,End"]
    r = subprocess.run(cmd, capture_output=True, text=True, env=dict(os.environ, TZ="UTC"))   # times in UTC
    lines = r.stdout.strip().splitlines()
    if r.returncode != 0 or not lines or not lines[0].startswith("JobID|"):
        raise SystemExit(f"REFUSE: sacct unreadable (rc {r.returncode}); the gate does not treat that as zero")
    done = fly = 0.0
    rows = []
    for ln in lines[1:]:
        jid, name, state, el, alloc, tl, req, start, end = ln.split("|")
        if not name.startswith(PREFIX):
            continue
        tres = alloc if "billing=" in alloc else req
        bill = int(tres.split("billing=")[1].split(",")[0]) if "billing=" in tres else None
        want = PACK_BILLING if is_pack(name) else tbl.get(name)
        st = state.split()[0]
        if st in IN_FLIGHT:
            cands = [x for x in (bill, want) if x is not None]
            if not cands:
                raise SystemExit(f"REFUSE: no billing for in-flight job {jid}")
            liab = max(cands) * hours(tl) / 256
            fly += liab
            rows.append(Row(jid, name, st, int(el), "in-flight at cap", round(liab, 4), start, end, tl))
        else:
            if is_pack(name) and int(el) > 0:   # a pack that ran holds a whole node: never charge it below 256
                bill = max(bill or 0, PACK_BILLING)
            ch = int(el) * (bill or 0) / 256 / 3600
            done += ch
            rows.append(Row(jid, name, st, int(el), "charged", round(ch, 4), start, end, tl))
    return done, fly, rows


def members_of(jid):
    """A pack job's members from $NS/packs/<jid>.members (launcher record: name, cap, comma-separated members)."""
    p = Path(NS, "packs", f"{jid}.members")
    if not p.is_file():
        raise SystemExit(f"REFUSE: pack job {jid} has no member record {p}; fail closed (DESIGN §14)")
    f = p.read_text().strip().split("\t")
    if len(f) != 3 or not f[2]:
        raise SystemExit(f"REFUSE: malformed member record {p}")
    return f[2].split(",")


def status_of(jid):
    """member -> (rc, end epoch) from $NS/packs/<jid>.status, written by the dispatcher as each member ends."""
    p = Path(NS, "packs", f"{jid}.status")
    out = {}
    if p.is_file():
        for ln in p.read_text().splitlines():
            f = ln.split("\t")
            if len(f) == 3 and f[0].startswith(PREFIX) and f[1].lstrip("-").isdigit():
                out[f[0]] = (int(f[1]), int(f[2]))
    return out


def epoch(t):
    """A sacct timestamp, read with TZ=UTC (ledger()) -> epoch; None if absent."""
    try:
        return dt.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=dt.timezone.utc).timestamp()
    except (ValueError, TypeError):
        return None


def validated(name):
    return Path(NS, "out", name, "xsec.root").is_file()


def started_steps(jid):
    """True when the dispatcher passed its refusals and launched the members (its '#pack' status line)."""
    p = Path(NS, "packs", f"{jid}.status")
    return p.is_file() and any(ln.startswith("#pack\t") for ln in p.read_text().splitlines())


def member_states(row):
    """member -> derived attempt state of one terminal pack job that ran (module docstring, ATTEMPTS). A pack that
    ran but never launched its members (no '#pack' status line: a dispatcher refusal or a node failure before the
    steps) is a pack-level STOP for the director, not an attempt by its members."""
    ms, rc = members_of(row.jid), status_of(row.jid)
    if not started_steps(row.jid):
        raise SystemExit(f"STOP: pack {row.jid} ({row.name}, {row.st}) ran but never launched its members; report to "
                         "the director (DESIGN §14.3). Nothing is submitted until it rules")
    start = epoch(row.start)
    limit = start + hours(row.tl) * 3600 if start is not None and row.tl else None
    out = {}
    for m in ms:
        if m in rc and rc[m][0] == 0 and validated(m):
            out[m] = "COMPLETED"
        elif row.st == "OUT_OF_MEMORY":
            out[m] = "OUT_OF_MEMORY"
        elif row.st == "TIMEOUT" and limit is not None and (m not in rc or rc[m][1] >= limit - KILL_MARGIN_S):
            out[m] = "TIMEOUT"
        else:
            out[m] = "FAILED"
    return out


def attempts(rows):
    """jobs.tsv name -> list of its attempts' states (member-level for packs). Never-started jobs are not attempts."""
    out = {}
    for x in rows:
        if never_started(x.st, x.el, x.start):
            continue
        if is_pack(x.name):
            if x.st in IN_FLIGHT:
                for m in members_of(x.jid):
                    out.setdefault(m, []).append(x.st)
            else:
                for m, s in member_states(x).items():
                    out.setdefault(m, []).append(s)
        else:
            out.setdefault(x.name, []).append(x.st)
    return out


def queued():
    """Row names in the Slurm queue now, a queued pack contributing its members (squeue sees a job before sacct)."""
    r = subprocess.run(["squeue", "-h", "-u", os.environ.get("USER", "josephrb"), "-o", "%i|%j"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"REFUSE: squeue unreadable (rc {r.returncode})")
    out = set()
    for ln in r.stdout.splitlines():
        if "|" not in ln:
            continue
        jid, name = ln.strip().split("|", 1)
        if is_pack(name):
            out.update(members_of(jid.split("_")[0]))
        elif name.startswith(PREFIX):
            out.add(name)
    return out


def owed_first(rows_l, inq):
    """Rows with no attempt, not queued and with nothing in out/<name>/ (owed a first submission)."""
    att = attempts(rows_l)
    return [r for r in table() if r["name"] not in att and r["name"] not in inq
            and not any(Path(NS, "out", r["name"]).glob("*"))]


def compose(batch, rows_l, inq):
    """Packs for `submit <batch>`: per class, in the frozen order, chunks of the batch's owed rows led by the owed rows
    of earlier batches; a partial chunk is held for the next batch unless this is the class's last batch. Earlier
    rows may lead only as a held remainder (fewer than a node's worth per class): more than that means an earlier
    batch is owed a submission first (frozen order), and compose() refuses."""
    i = ORDER.index(batch)
    owed = [r for r in owed_first(rows_l, inq) if ORDER.index(r["batch"]) <= i]
    owed.sort(key=lambda r: ORDER.index(r["batch"]))   # stable: jobs.tsv order within a batch
    last = {}
    for r in table():
        last[klass(r)] = max(last.get(klass(r), -1), ORDER.index(r["batch"]))
    for k in dict.fromkeys(klass(r) for r in owed):
        early = [r for r in owed if klass(r) == k and ORDER.index(r["batch"]) < i]
        if early and len(early) >= per_node(early[0]):
            first = min((r["batch"] for r in early), key=ORDER.index)
            raise SystemExit(f"REFUSE: {len(early)} rows of earlier batches ({first} first) are owed a submission; "
                             f"submit {first} before {batch} (frozen order)")
    packs = []
    for k in dict.fromkeys(klass(r) for r in owed):
        rs = [r for r in owed if klass(r) == k]
        n = per_node(rs[0])
        for j in range(0, len(rs), n):
            ch = rs[j:j + n]
            if len(ch) == n or i >= last[k]:
                packs.append((ch, k[2]))
    return packs


def owed_retries(batch, rows_l, inq):
    """redo: members of <batch> whose walltime-retry pack was removed by the deadline before it started (records: one
    TIMEOUT attempt, retries/<name>.time, nothing queued, nothing in out/<name>/), packed by class and recorded cap."""
    att = attempts(rows_l)
    owed = []
    for r in table():
        n = r["name"]
        if r["batch"] != batch or n in inq or any(Path(NS, "out", n).glob("*")):
            continue
        rec = Path(NS, "retries", f"{n}.time")
        if att.get(n) == ["TIMEOUT"] and rec.is_file():
            owed.append((r, rec.read_text().strip()))
    packs = []
    for k in dict.fromkeys((klass(r), t) for r, t in owed):
        rs = [r for r, t in owed if (klass(r), t) == k]
        n = per_node(rs[0])
        packs += [(rs[j:j + n], k[1]) for j in range(0, len(rs), n)]
    return packs


def gate(packs, rows=None, verbose=True):
    done, fly, rl = rows if rows is not None else ledger()
    b = sum(pack_enforced(t) for _, t in packs)
    total = done + fly + b
    if verbose:
        for x in rl:
            print("  ", x.jid, x.name, x.st, x.el, x.kind, x.amount)
        for ms, t in packs:
            print(f"   + pack {pack_name(ms)} cap {t} enforced {pack_enforced(t):.4f} "
                  f"(members' caps {sum(enforced(r, t) for r in ms):.4f}): {','.join(r['name'] for r in ms)}")
        print(f"GATE completed {done:.4f} + in-flight at cap {fly:.4f} + packs {b:.4f} = {total:.4f} "
              f"vs ceiling {CEILING}")
    return total <= CEILING + 1e-12, total, fly


def load_result(f):
    p = Path(NS, "results", f)
    if not p.is_file():
        raise SystemExit(f"REFUSE: precondition {p} missing")
    return json.load(open(p))


def preconditions(batch, rows_l, inq, members):
    """Order rules (DESIGN §6). Rows of earlier batches must be attempted, queued, or members of this submission."""
    if batch == "G0":
        return
    c0 = load_result("c0.json")
    if c0.get("out_root") != f"{NS}/out":
        raise SystemExit("REFUSE: c0.json was not computed from the production outputs ($NS/out)")
    if c0.get("C0") != "PASS":
        raise SystemExit("REFUSE: the controls (C0) did not PASS; production stops (grant §3)")
    if (batch == "G2" or any(m.startswith("2dc_P_S4U_") for m in members)) and \
            not Path(NS, "preflight", "uomni.stat").is_file():
        raise SystemExit("REFUSE: the universe-omnifile preflight (preflight_uomni.sh) is not recorded")
    i = ORDER.index(batch)
    names = {r["name"] for r in table() if r["batch"] in ORDER[:i]}
    seen = set(attempts(rows_l)) | inq | set(members)
    if not names <= seen:
        raise SystemExit(f"REFUSE: {batch} follows {ORDER[:i]}; {len(names - seen)} earlier rows not yet submitted")


def deadline_arg(now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    if DEADLINE <= now < MAINT_END:
        raise SystemExit("REFUSE: past the deadline and before the maintenance window ends; nothing is submitted")
    if now < DEADLINE:   # Slurm reads --deadline in the cluster's local time; pass an explicit UTC-derived value
        local = DEADLINE.astimezone()   # the login node's local zone
        return [f"--deadline={local.strftime('%Y-%m-%dT%H:%M:%S')}"]
    return []


def sbatch_pack(members, time, dl):
    """Write the pre-sbatch record, sbatch one pack, write the job-id record (scancel the job if that fails)."""
    pname = pack_name(members)
    names = ",".join(r["name"] for r in members)
    Path(NS, "packs").mkdir(parents=True, exist_ok=True)
    Path(NS, "packs", f"{pname}.members").write_text(f"{pname}\t{time}\t{names}\n")
    memsum = sum(mem_mb(r["mem"]) for r in members)
    cmd = ["sbatch", "--parsable", f"--job-name={pname}", f"--qos={PACK_QOS}", "--nodes=1", "--exclusive",
           f"--mem={memsum}M", f"--time={time}", "--no-requeue", *dl, SBATCH, *[r["name"] for r in members]]
    print("+", " ".join(cmd))
    s = subprocess.run(cmd, capture_output=True, text=True)
    print(s.stdout.strip(), s.stderr.strip())
    if s.returncode != 0:
        return None
    jid = s.stdout.strip().split(";")[0]
    try:
        if not jid.isdigit():
            raise OSError(f"unparsable job id '{s.stdout.strip()}'")
        Path(NS, "packs", f"{jid}.members").write_text(f"{pname}\t{time}\t{names}\n")
    except OSError as e:
        subprocess.run(["scancel", jid])
        raise SystemExit(f"REFUSE: could not record pack {pname} ({e}); scancel {jid} issued; nothing further submitted")
    return jid


def migrate(only, execute):
    """Record §4.5: the never-started PENDING shared-QOS 2dc_P_* jobs, measured from squeue NOW; scancel only in state
    PENDING, so a job that starts between the listing and the cancel is left alone."""
    r = subprocess.run(["squeue", "-h", "-u", os.environ.get("USER", "josephrb"), "-t", "PENDING", "-o", "%i|%j|%q"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"REFUSE: squeue unreadable (rc {r.returncode})")
    rows = [ln.strip().split("|") for ln in r.stdout.splitlines() if "|" in ln]
    tbl = {x["name"] for x in table()}
    cand = [(j, n) for j, n, q in rows if n in tbl and not is_pack(n) and q == "shared"]
    if only is not None:
        missing = set(only) - {n for _, n in cand}
        if missing:
            raise SystemExit(f"REFUSE: not PENDING shared-QOS jobs now: {sorted(missing)}")
        cand = [(j, n) for j, n in cand if n in set(only)]
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    for j, n in cand:
        print(f"  cancel {j} {n}")
    print(f"MIGRATE {len(cand)} never-started PENDING shared-QOS jobs ({'execute' if execute else 'dry run'})")
    if execute and cand:
        Path(NS, "gatelog").mkdir(parents=True, exist_ok=True)
        Path(NS, "gatelog", f"migrate_{stamp}.tsv").write_text("".join(f"{j}\t{n}\n" for j, n in cand))
        s = subprocess.run(["scancel", "--state=PENDING", *[j for j, _ in cand]], capture_output=True, text=True)
        print(s.stdout.strip(), s.stderr.strip())
        if s.returncode != 0:
            raise SystemExit(f"scancel failed (rc {s.returncode}); re-measure before anything else")
    return 0


def show_members(jid):
    done, fly, rl = ledger()
    row = next((x for x in rl if x.jid == jid), None)
    if row is None or not is_pack(row.name):
        raise SystemExit(f"REFUSE: {jid} is not a 2dc_P_K pack job in the ledger")
    st = (member_states(row) if row.st not in IN_FLIGHT and not never_started(row.st, row.el, row.start)
          else {m: row.st for m in members_of(jid)})
    rc = status_of(jid)
    steps = subprocess.run(["sacct", "-j", jid, "-n", "-P", "-o", "JobID,JobName,State,ExitCode,ElapsedRaw"],
                           capture_output=True, text=True).stdout
    print(f"pack {jid} {row.name} {row.st} elapsed {row.el} {row.kind} {row.amount}")
    for m in members_of(jid):
        stp = [ln for ln in steps.splitlines() if ln.split("|")[1:2] == [m]]
        print(f"  {m} derived={st[m]} rc={rc.get(m, ('-',))[0]} step={stp[0] if stp else '-'}")
    return 0


def simulate(mode):
    """Worked example of the shared-QOS design (DESIGN §6), at ROW caps and per-row units; it does not model packs.
    The packed path's expected charge is measured from the smoke pack (DESIGN §14.5). Batches in the frozen order, each admitted against the charges of every earlier
    batch, with no overlap (the floor of the gate's totals) and costs per job at the pilot's measured mean, p84
    (u_CV) / max (u_U,sel, u_A), or the cap."""
    unit = {"mean": {"cv": 0.0754, "u": 0.1418, "a": 0.3293},
            "p84": {"cv": 0.0933, "u": 0.2232, "a": 0.3889}}
    rows = table()
    spent = 0.0
    print(f"mode={mode}  ceiling={CEILING}")
    for b in ORDER:
        br = [r for r in rows if r["batch"] == b]
        cap = sum(enforced(r) for r in br)
        ok = spent + cap <= CEILING + 1e-12
        if mode == "cap":
            cost = cap
        else:
            k = lambda r: "a" if r["item"] == "S3" else "u" if r["name"].startswith("2dc_P_S4U_") else "cv"
            cost = sum(unit[mode][k(r)] for r in br)
        print(f"  {b:4s}: {len(br):3d} jobs  gate {spent:.4f} + {cap:.4f} = {spent + cap:.4f}  "
              f"{'OK' if ok else 'REFUSE'}  then charged {cost:.4f}")
        if not ok:
            print(f"  first refusal at {b}")
            return
        spent += cost
    print(f"  all batches admitted; total charged {spent:.4f}; unused at the ceiling {CEILING - spent:.4f}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=["gate", "submit", "redo", "pack", "migrate", "members", "simulate"])
    ap.add_argument("arg", nargs="?")
    ap.add_argument("--retry")
    ap.add_argument("--time")
    ap.add_argument("--only")
    ap.add_argument("--execute", action="store_true")
    a = ap.parse_args()
    if a.action == "simulate":
        return simulate(a.arg)
    if a.action == "migrate":
        return migrate(a.only.split(",") if a.only else None, a.execute)
    if a.action == "members":
        return show_members(a.arg)
    if not a.arg:
        raise SystemExit(f"REFUSE: {a.action} needs an argument")
    tbl = {r["name"]: r for r in table()}
    for d in ("logs", "results", "retries", "out", "tmp", "gatelog", "packs"):
        Path(NS, d).mkdir(parents=True, exist_ok=True)
    led = ledger()
    rows_l = led[2]
    inq = queued()
    att = attempts(rows_l)
    rec_write = []
    if a.retry:
        if a.action not in ("gate", "submit"):
            raise SystemExit("REFUSE: --retry goes with gate or submit")
        names = a.retry.split(",")
        if not all(n in tbl for n in names) or not a.time or not re.fullmatch(r"\d{2}:\d{2}:\d{2}", a.time) \
                or hours(a.time) >= 12:
            raise SystemExit("REFUSE: --retry needs jobs.tsv names and a re-projected --time HH:MM:SS under 12 h")
        members = [tbl[n] for n in names]
        if {r["batch"] for r in members} != {a.arg}:
            raise SystemExit(f"REFUSE: --retry members must all belong to batch {a.arg}")
        for r in members:
            n = r["name"]
            if n in inq:
                raise SystemExit(f"REFUSE: {n} is in the Slurm queue now; no double submission")
            if att.get(n) != ["TIMEOUT"]:
                raise SystemExit(f"REFUSE: {n} has attempts {att.get(n, [])}; a walltime retry needs exactly one "
                                 "TIMEOUT attempt (grant §3). Out of memory is a stop; any other failure needs a "
                                 "diagnosed infrastructure cause and the director")
            if Path(NS, "retries", f"{n}.time").exists():
                raise SystemExit(f"REFUSE: {n} already has a retry record")
            if validated(n):
                raise SystemExit(f"REFUSE: out/{n}/xsec.root exists; a member with output is never re-run without "
                                 "the director")
            if any(Path(NS, "out", n).glob("*")):
                raise SystemExit(f"REFUSE: move out/{n} aside (sha-verified) before the retry")
        packs = [(members, a.time)]
        rec_write = names
    elif a.action == "pack":
        names = a.arg.split(",")
        if not all(n in tbl for n in names):
            raise SystemExit(f"REFUSE: not jobs.tsv names: {[n for n in names if n not in tbl]}")
        owed = {r["name"] for r in owed_first(rows_l, inq)}
        bad = [n for n in names if n not in owed]
        if bad:
            raise SystemExit(f"REFUSE: not owed a first submission (attempted, queued or with output): {bad}")
        members = [tbl[n] for n in names]
        packs = [(members, members[0]["time"])]
    elif a.action == "redo":
        packs = owed_retries(a.arg, rows_l, inq)
        if not packs:
            raise SystemExit(f"REFUSE: batch {a.arg} has no deadline-cancelled retry owed (owed_retries())")
    else:
        if a.arg not in ORDER:
            raise SystemExit(f"REFUSE: no batch {a.arg}")
        packs = compose(a.arg, rows_l, inq)
        if not packs:
            raise SystemExit(f"REFUSE: batch {a.arg} has no rows owed a first submission (or only a held partial pack)")
    for ms, t in packs:
        if rec_write:
            check_pack_retry(ms, t)
        elif a.action == "redo":   # each member's recorded retry cap is the pack cap
            check_pack_retry(ms, t)
            if any(Path(NS, "retries", f"{r['name']}.time").read_text().strip() != t for r in ms):
                raise SystemExit(f"REFUSE: retry pack {pack_name(ms)} cap {t} differs from a member's retry record")
        else:
            check_pack(ms, t)
    batch = a.arg if a.action != "pack" else max((r["batch"] for r in packs[0][0]), key=ORDER.index)
    dl = deadline_arg()
    ok, total, fly = gate(packs, led)
    if not ok:
        if a.action == "gate" and fly > 0:
            print("NOT ADMITTED: the packs would exceed the ceiling with jobs still in flight. Wait and re-check.")
        else:   # a submit refusal, or a pre-check refusal with nothing in flight (waiting cannot help): a stop
            print("REFUSE: the packs would exceed the ceiling. Stop and report to the director (grant §3).")
        return 3
    if a.action == "gate":
        return 0
    preconditions(batch, rows_l, inq, [r["name"] for ms, _ in packs for r in ms])
    for n in rec_write:   # written before sbatch (the dispatcher and member read them at start)
        Path(NS, "retries", f"{n}.time").write_text(a.time + "\n")
    for ms, t in packs:
        try:
            jid = sbatch_pack(ms, t, dl)
        except SystemExit:   # the job-id record could not be written; sbatch_pack() cancelled the job
            for n in rec_write:
                Path(NS, "retries", f"{n}.time").unlink(missing_ok=True)
            raise
        if jid is None:
            for n in rec_write:
                Path(NS, "retries", f"{n}.time").unlink()
            raise SystemExit(f"sbatch failed for {pack_name(ms)}; nothing further submitted")
    return 0


if __name__ == "__main__":
    sys.exit(main())
