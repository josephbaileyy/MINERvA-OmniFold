#!/usr/bin/env python3
"""SB1 operator wrapper (sb1-run): submit once, identify this attempt's jobs, clean up orphans.

Runs on a Perlmutter login node, outside the pinned package (which it never edits):

    sb1_operate.py submit   --admission ADM --record DIR
    sb1_operate.py identify --record DIR
    sb1_operate.py cleanup  --record DIR [--reason TEXT]
    sb1_operate.py status   --record DIR

``submit`` records the UTC window around one call of the package's ``launch/sb1_submit.sh``, its
exit status, stdout and stderr, then runs ``identify``. On a non-zero or ambiguous exit (exit 0 but
the jobs found differ from ``submission.json``) it runs ``cleanup``. It never resubmits.

``identify`` finds this attempt's jobs WITHOUT trusting returned ids: every job of ``$USER`` in
``sacct`` and ``squeue`` whose submit time lies in the recorded window (padded 120 s) AND whose
WorkDir is the attempt's unique outroot or whose StdOut/StdErr lies under it. The launcher sets
``--chdir``, ``--output`` and ``--error`` to the outroot, so these bind a job to this attempt.
Jobs matched by only one of the two keys are reported as AMBIGUOUS and not acted on.

``cleanup`` cancels only identified jobs still pending or running, by id, one ``scancel`` per id,
then polls until none is active (at most 10 min) and records the final states. It never cancels by
name. Every action is appended to ``DIR/operator-log.jsonl``.
"""

import argparse
import datetime
import json
import os
import subprocess
import sys
import time
from pathlib import Path

PKG = "docs/orchestration/state/next-preparation-20261009/sb1-prep"
ACTIVE = {"PENDING", "RUNNING", "CONFIGURING", "REQUEUED", "RESIZING", "SUSPENDED", "COMPLETING"}
PAD_S = 120


def now():
    return datetime.datetime.now(datetime.timezone.utc)


def iso(t):
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def log(rec_dir, event, **kw):
    entry = {"utc": iso(now()), "event": event, **kw}
    with open(Path(rec_dir) / "operator-log.jsonl", "a") as fh:
        fh.write(json.dumps(entry, sort_keys=True) + "\n")
    print(json.dumps(entry, sort_keys=True), flush=True)


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def load_window(rec_dir):
    return json.loads((Path(rec_dir) / "attempt.json").read_text())


def parse_slurm_time(text):
    # sacct/squeue print local time without zone; this login node's TZ is used consistently
    return datetime.datetime.strptime(text, "%Y-%m-%dT%H:%M:%S").astimezone(datetime.timezone.utc)


def identify(rec_dir):
    att = load_window(rec_dir)
    out = att["outroot"].rstrip("/")
    t0 = datetime.datetime.fromisoformat(att["t0_utc"].replace("Z", "+00:00")) - \
        datetime.timedelta(seconds=PAD_S)
    t1 = datetime.datetime.fromisoformat(att["t1_utc"].replace("Z", "+00:00")) + \
        datetime.timedelta(seconds=PAD_S)
    user = os.environ["USER"]
    start = (t0.astimezone()).strftime("%Y-%m-%dT%H:%M:%S")
    sa = run(["sacct", "-u", user, "-X", "-P", "-S", start, "--duplicates",
              "-o", "JobID,JobName,User,Submit,State,WorkDir,StdOut,StdErr,ElapsedRaw,AllocTRES"])
    sq = run(["squeue", "-u", user, "-h", "-o", "%i|%j|%V|%T|%Z"])
    if sa.returncode != 0 or sq.returncode != 0:
        log(rec_dir, "identify-failed", sacct_rc=sa.returncode, squeue_rc=sq.returncode,
            stderr=(sa.stderr + sq.stderr)[-2000:])
        return None
    rows = {}
    lines = sa.stdout.strip().splitlines()
    head = lines[0].split("|") if lines else []
    for line in lines[1:]:
        r = dict(zip(head, line.split("|")))
        rows[r["JobID"]] = r
    for line in sq.stdout.strip().splitlines():
        jid, name, submit, state, wd = line.split("|")
        rows.setdefault(jid, {"JobID": jid, "JobName": name, "Submit": submit, "WorkDir": wd,
                              "StdOut": "", "StdErr": "", "ElapsedRaw": "", "AllocTRES": ""})
        rows[jid]["State_squeue"] = state
    matched, ambiguous = {}, {}
    for jid, r in rows.items():
        try:
            in_window = t0 <= parse_slurm_time(r["Submit"]) <= t1
        except (ValueError, KeyError):
            in_window = False
        under = r.get("WorkDir", "").rstrip("/") == out or \
            r.get("StdOut", "").startswith(out + "/") or r.get("StdErr", "").startswith(out + "/")
        if in_window and under:
            matched[jid] = r
        elif under or (in_window and r.get("JobName", "").startswith("sb1_")):
            ambiguous[jid] = r
    sub = Path(out) / "submission.json"
    returned = json.loads(sub.read_text())["jobs"] if sub.exists() else None
    found = {
        "utc": iso(now()), "window_utc": [iso(t0), iso(t1)], "outroot": out,
        "matched": matched, "ambiguous": ambiguous,
        "submission_json": returned,
        "submission_json_agrees": (returned is not None and
                                   sorted(returned.values()) == sorted(matched)),
    }
    (Path(rec_dir) / "attempt-jobs.json").write_text(json.dumps(found, indent=1, sort_keys=True))
    log(rec_dir, "identify", matched=sorted(matched), ambiguous=sorted(ambiguous),
        submission_json=returned, agrees=found["submission_json_agrees"])
    return found


def state_of(r):
    return (r.get("State_squeue") or r.get("State") or "").split()[0]


def cleanup(rec_dir, reason):
    found = identify(rec_dir)
    if found is None:
        log(rec_dir, "cleanup-blocked", reason="job identity could not be established")
        return 2
    targets = sorted(j for j, r in found["matched"].items() if state_of(r) in ACTIVE)
    log(rec_dir, "cleanup-start", reason=reason, targets=targets,
        ambiguous_not_touched=sorted(found["ambiguous"]))
    for jid in targets:
        r = run(["scancel", jid])
        log(rec_dir, "scancel", jobid=jid, rc=r.returncode, stderr=r.stderr[-500:])
    deadline = time.time() + 600
    while time.time() < deadline:
        found = identify(rec_dir)
        if found is None:
            return 2
        active = sorted(j for j, r in found["matched"].items() if state_of(r) in ACTIVE)
        if not active:
            break
        time.sleep(15)
    final = {j: state_of(r) for j, r in found["matched"].items()}
    log(rec_dir, "cleanup-done", final_states=final,
        still_active=sorted(j for j, s in final.items() if s in ACTIVE),
        ambiguous=sorted(found["ambiguous"]))
    return 0 if not any(s in ACTIVE for s in final.values()) and not found["ambiguous"] else 3


def submit(args):
    rec_dir = Path(args.record)
    rec_dir.mkdir(parents=True, exist_ok=False)
    adm = json.loads(Path(args.admission).read_text())
    code, out = adm["checkout"], adm["outroot"]
    if Path(out).exists():
        raise SystemExit(f"[operator] REFUSED: outroot {out} exists")
    t0 = now()
    (rec_dir / "attempt.json").write_text(json.dumps(
        {"t0_utc": iso(t0), "t1_utc": None, "outroot": out, "checkout": code,
         "admission": str(Path(args.admission).resolve()), "user": os.environ["USER"]}, indent=1))
    log(rec_dir, "submit-start", outroot=out, checkout=code)
    r = run(["bash", f"{code}/{PKG}/launch/sb1_submit.sh", args.admission])
    t1 = now()
    (rec_dir / "submit.stdout").write_text(r.stdout)
    (rec_dir / "submit.stderr").write_text(r.stderr)
    att = load_window(rec_dir)
    att.update(t1_utc=iso(t1), submit_rc=r.returncode)
    (rec_dir / "attempt.json").write_text(json.dumps(att, indent=1))
    log(rec_dir, "submit-end", rc=r.returncode)
    time.sleep(5)
    found = identify(rec_dir)
    if r.returncode != 0 or found is None or not found["submission_json_agrees"] \
            or found["ambiguous"]:
        log(rec_dir, "submission-failed-or-ambiguous", rc=r.returncode)
        return cleanup(rec_dir, reason=f"submit rc={r.returncode}") or 1
    return 0


def status(args):
    found = identify(args.record)
    if found is None:
        return 2
    for jid, r in sorted(found["matched"].items()):
        print(jid, r.get("JobName"), state_of(r), r.get("ElapsedRaw"), r.get("AllocTRES"))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("submit")
    s.add_argument("--admission", required=True)
    s.add_argument("--record", required=True)
    for name in ("identify", "cleanup", "status"):
        p = sp.add_parser(name)
        p.add_argument("--record", required=True)
        if name == "cleanup":
            p.add_argument("--reason", default="operator")
    a = ap.parse_args(argv)
    if a.cmd == "submit":
        return submit(a)
    if a.cmd == "identify":
        return 0 if identify(a.record) is not None else 2
    if a.cmd == "cleanup":
        return cleanup(a.record, a.reason)
    return status(a)


if __name__ == "__main__":
    sys.exit(main())
