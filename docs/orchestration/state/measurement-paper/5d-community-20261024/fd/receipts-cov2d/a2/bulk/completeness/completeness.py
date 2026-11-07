"""COV2D stage 4's PASS record (COV2D-BINDING-2.md, addendum A3, ruling 6): the per-label completeness table.

For every bulk label of runs_G18.tsv and runs_AR23.tsv (1,572), it lists the walls rows and the SHA256SUMS lines that
jobs at M wrote for it, and requires exactly one rc-0 walls row and exactly one digest, both from one job that
submissions.log lists at M with exactly one id. For the five labels of runs_G18C.tsv that job must be G18_C (A3 rulings
2-4), and their planned bulk jobs must hold no walls row or digest for them. With --disk it also hashes each
$O/out/<label>/xsec.root with O_NOATIME (cov2d_jobs.noatime_sha256) and requires it to equal the digest.

Read-only: it opens files for reading and runs sacct; it writes only to stdout. Run on a login node under $PY310:
    $PY310 -I -B - [--disk] < completeness.py
Exit 0 when every label passes, 1 when any fails, 2 on unusable input.
"""
import glob
import os
import subprocess
import sys

M = "a60547692df5f963e428cdfe4661fc51ab785b7b"
O = "/pscratch/sd/j/josephrb/cov2d-run-20261104"
C = "/pscratch/sd/j/josephrb/cov2d-deploy-a6054769"
COMPLETION_JOB, COMPLETION_TABLE = "G18_C", "G18C"
LEDGER = O + "/renames-pilot-60857636.tsv"
N_LABELS = 1572


class Unusable(Exception):
    pass


def table(truth):
    with open("%s/tables/runs_%s.tsv" % (O, truth)) as f:
        rows = [ln.rstrip("\n").split("\t") for ln in f]
    head = rows[0]
    return [dict(zip(head, r)) for r in rows[1:] if r != [""]]


def main(disk):
    plan = {}
    for truth in ("G18", "AR23"):
        for r in table(truth):
            if r["label"] in plan:
                raise Unusable("label %s twice in the bulk tables" % r["label"])
            plan[r["label"]] = (truth, r["job"])
    if len(plan) != N_LABELS:
        raise Unusable("%d bulk labels, not %d" % (len(plan), N_LABELS))
    completion = {r["label"]: r["job"] for r in table(COMPLETION_TABLE)}
    if set(completion.values()) != {COMPLETION_JOB} or not set(completion) <= set(plan):
        raise Unusable("runs_%s.tsv is not %s rows over bulk labels" % (COMPLETION_TABLE, COMPLETION_JOB))
    jobs = {j for _, j in plan.values()} | {COMPLETION_JOB}

    ids = {}
    with open(O + "/submissions.log") as f:
        for ln in f:
            kv = dict(x.split("=", 1) for x in ln.split()[1:] if "=" in x)
            if kv.get("M") == M and kv.get("job") in jobs:
                ids.setdefault(kv["job"], []).append(kv["id"])
    out = subprocess.run(["sacct", "-X", "-n", "-P", "-j", ",".join(i for v in ids.values() for i in v),
                          "-o", "JobID,State,ExitCode"], capture_output=True, text=True, check=True).stdout
    state = {f[0]: "%s %s" % (f[1], f[2]) for f in (ln.split("|") for ln in out.splitlines() if ln)}

    walls, sums = {}, {}
    for job in sorted(jobs):
        for p in sorted(glob.glob("%s/walls.%s.*.tsv" % (O, job))):
            lane = p.rsplit(".", 2)[1]
            with open(p) as f:
                for ln in f:
                    lab, t0, t1, rc = ln.rstrip("\n").split("\t")
                    walls.setdefault(lab, []).append((job, lane, rc))
        for p in sorted(glob.glob("%s/SHA256SUMS.%s.*" % (O, job))):
            with open(p) as f:
                for ln in f:
                    sha, path = ln.split()
                    sums.setdefault(path.split("/")[0], []).append((job, sha))

    noatime = None
    if disk:
        sys.path.insert(0, C + "/2d-unfolding/cov2d/jobs")
        from cov2d_jobs import noatime_sha256 as noatime

    cols = ["truth", "label", "plan_job", "job", "job_id", "sacct", "lane", "walls_rc0", "walls_other", "digests",
            "sha256", "disk", "basis", "verdict"]
    print("\t".join(cols))
    bad = 0
    for lab in sorted(plan, key=lambda x: (plan[x][0], plan[x][1], x)):
        truth, plan_job = plan[lab]
        want_job = completion.get(lab, plan_job)
        w = walls.get(lab, [])
        rc0 = [x for x in w if x[2] == "0"]
        d = sums.get(lab, [])
        why = []
        if len(rc0) != 1:
            why.append("%d rc-0 walls rows" % len(rc0))
        if len(w) != len(rc0):
            why.append("walls rows with rc != 0: %s" % [x for x in w if x[2] != "0"])
        if len(d) != 1:
            why.append("%d digests" % len(d))
        job = rc0[0][0] if len(rc0) == 1 else ""
        if job and job != want_job:
            why.append("walls row from %s, expected %s" % (job, want_job))
        if job and d and any(j != job for j, _ in d):
            why.append("digest from %s" % ",".join(j for j, _ in d))
        jid = ids.get(job, [])
        if job and len(jid) != 1:
            why.append("%s has %d ids at M" % (job, len(jid)))
        sha = d[0][1] if len(d) == 1 else ""
        on_disk = ""
        if noatime and sha:
            try:
                on_disk = "match" if noatime("%s/out/%s/xsec.root" % (O, lab)) == sha else "DIFFERS"
            except OSError as e:
                on_disk = "unreadable: %s" % e.strerror
            if on_disk != "match":
                why.append("disk " + on_disk)
        basis = ("A3 rulings 2-4; ledger %s" % os.path.basename(LEDGER)) if lab in completion else "A2 ruling 3"
        verdict = "PASS" if not why else "FAIL: " + "; ".join(why)
        bad += bool(why)
        print("\t".join([truth, lab, plan_job, job, jid[0] if len(jid) == 1 else ",".join(jid),
                         state.get(jid[0], "") if len(jid) == 1 else "", rc0[0][1] if len(rc0) == 1 else "",
                         str(len(rc0)), str(len(w) - len(rc0)), str(len(d)), sha, on_disk or "-", basis, verdict]))
    print("# labels=%d pass=%d fail=%d disk=%s M=%s" % (len(plan), len(plan) - bad, bad, "checked" if disk else "not checked",
                                                       M), file=sys.stderr)
    return 1 if bad else 0


if __name__ == "__main__":
    try:
        sys.exit(main("--disk" in sys.argv[1:]))
    except (Unusable, OSError, ValueError, KeyError, subprocess.CalledProcessError) as e:
        print("unusable: %r" % e, file=sys.stderr)
        sys.exit(2)
