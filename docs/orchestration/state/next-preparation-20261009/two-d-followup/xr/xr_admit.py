#!/usr/bin/env python3
"""XR admission: the package manifest, the authorization binding, the admission record and the ledger.

    xr_admit.py manifest [--check]                   write (or verify) manifest/expected-code.json
    xr_admit.py check  --authorization A --package-commit C --manifest-sha S
    xr_admit.py draft  --authorization A --package-commit C --manifest-sha S --setup F
    xr_admit.py verify --admission ADM                re-run check against the admission's values
    xr_admit.py jobcheck --admission ADM --run R      inside a job: its allocation within the caps
    xr_admit.py next-attempt --admission ADM --run R --sacct PSV [--now ISO]   prints: ATTEMPT DEADLINE
    xr_admit.py ledger --admission ADM --sacct PSV    charge, attempts and the stop; exit 6 if over

Standard library only, and Python 3.6-compatible: the launch scripts run it with the cluster's
``/usr/bin/python3`` (3.6.15), before the analysis environment is sourced.

The binding (``check``), every clause a refusal (exit 3):
* the authorization is a repository-relative path under ``docs/orchestration/``, not a symlink,
  committed at HEAD with the same bytes, and its text names the package commit (40 hex) and the
  manifest sha256 (64 hex) in full;
* the package commit is an ancestor of HEAD, and nothing under the package, an executed module or
  the guard differs between it and HEAD;
* ``manifest/expected-code.json`` hashes to the stated sha256 and every file it lists has that
  digest on disk and at HEAD;
* the work tree is clean.

One admission per grant: the outroot is frozen in ``runs.json`` (independent of HEAD), ``draft``
creates it exclusively and writes ``<outroot>/admission.json``, so a second ``draft`` is refused.
Attempt caps and the stop rule are counted over the whole grant: attempt directories, the
submissions record, and every ``xr_*`` job ``sacct`` lists for the user since the grant date.
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[5]
PKG = HERE.relative_to(REPO).as_posix()
MANIFEST = HERE / "manifest" / "expected-code.json"
RUNS = HERE / "manifest" / "runs.json"
EXECUTED = ("2d-unfolding/unfold_2d_omnifold_unbinned.py", "unbinned_unfolding/python/omnifold.py",
            "2d-unfolding/uq/coverage_fixed_truth/n2/__init__.py",
            "2d-unfolding/uq/coverage_fixed_truth/n2/execution.py")
GUARD = ("nd-unfolding/mnv_guarded_run.py",)
GUARD_DIR = "nd-unfolding/mnv_guard_shim"
REFUSE, OVER = 3, 6
FINISHED = ("COMPLETED", "FAILED", "CANCELLED", "TIMEOUT", "OUT_OF_MEMORY", "NODE_FAIL", "PREEMPTED",
            "BOOT_FAIL", "DEADLINE")


class Refusal(RuntimeError):
    pass


def run(cmd, env=None):
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True,
                          check=True, env=env).stdout


def git(*args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return run(["git", "-C", str(REPO)] + list(args), env=env)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc)


def parse_utc(text):
    return datetime.datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)


def load_runs():
    return json.loads(RUNS.read_text())


def package_files():
    tracked = git("ls-files", "-z", "--", PKG, GUARD_DIR).split("\0")
    files = sorted(f for f in tracked if f and "__pycache__" not in f and not f.endswith(".pyc")
                   and f != MANIFEST.relative_to(REPO).as_posix() and "/tests/" not in f)
    return sorted(set(files) | set(EXECUTED) | set(GUARD))


def build_manifest():
    return {"schema": "xr-expected-code/1", "package": PKG,
            "files": {rel: sha(REPO / rel) for rel in package_files()}}


def manifest_cmd(check_only):
    want = json.dumps(build_manifest(), indent=1, sort_keys=True) + "\n"
    if check_only:
        if not MANIFEST.exists() or MANIFEST.read_text() != want:
            print("[xr-admit] manifest/expected-code.json is OUT OF DATE", file=sys.stderr)
            return REFUSE
        print("[xr-admit] manifest current")
        return 0
    MANIFEST.write_text(want)
    print("[xr-admit] wrote {} sha256 {}".format(MANIFEST.relative_to(REPO), sha(MANIFEST)))
    return 0


def check(authorization, package_commit, manifest_sha):
    if not re.fullmatch(r"[0-9a-f]{40}", package_commit or ""):
        raise Refusal("the package commit must be 40 lower-case hex characters")
    if not re.fullmatch(r"[0-9a-f]{64}", manifest_sha or ""):
        raise Refusal("the manifest sha256 must be 64 lower-case hex characters")
    rel = os.path.normpath(authorization)
    if os.path.isabs(authorization) or rel.startswith("..") or not rel.startswith("docs/orchestration/"):
        raise Refusal("authorization {!r} must be repository-relative under docs/orchestration/".format(authorization))
    if not re.fullmatch(r"docs/orchestration/AUTHORIZATION-\d{8}-[a-z0-9-]+\.md", rel):
        raise Refusal("authorization {} is not an AUTHORIZATION-<date>-<name>.md record".format(rel))
    path = REPO / rel
    if path.is_symlink() or not path.is_file():
        raise Refusal("authorization {} is missing or a symlink".format(rel))
    head = git("rev-parse", "HEAD").strip()
    try:
        blob = git("rev-parse", "HEAD:" + rel).strip()
    except subprocess.CalledProcessError:
        raise Refusal("authorization {} is not committed at HEAD".format(rel)) from None
    if git("hash-object", "--", rel).strip() != blob:
        raise Refusal("authorization {} differs from its committed bytes".format(rel))
    text = path.read_text()
    if package_commit not in text or manifest_sha not in text:
        raise Refusal("the authorization does not name the package commit and the manifest sha256 in full")
    anc = subprocess.run(["git", "-C", str(REPO), "merge-base", "--is-ancestor", package_commit, head],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if anc.returncode:
        raise Refusal("package commit {} is not an ancestor of HEAD {}".format(package_commit, head))
    changed = git("diff", "--name-only", package_commit, head, "--", PKG, *EXECUTED, *GUARD, GUARD_DIR).split()
    if changed:
        raise Refusal("the package changed after {}: {}".format(package_commit, changed))
    if sha(MANIFEST) != manifest_sha:
        raise Refusal("manifest/expected-code.json has sha256 {}, not {}".format(sha(MANIFEST), manifest_sha))
    man = json.loads(MANIFEST.read_text())
    if man != build_manifest():
        raise Refusal("manifest/expected-code.json does not describe the files on disk")
    for f in man["files"]:
        if git("hash-object", "--", f).strip() != git("rev-parse", "HEAD:" + f).strip():
            raise Refusal("{} differs from HEAD".format(f))
    if git("status", "--porcelain", "--untracked-files=no").strip():
        raise Refusal("the work tree has uncommitted changes to tracked files")
    return {"head": head, "authorization": {"path": rel, "sha256": sha(path)}}


def setup_record(setup, nested):
    setup = Path(setup).resolve()
    rec = {"path": str(setup), "sha256": sha(setup), "nested": {}}
    for rel in nested:
        p = (setup.parent / rel).resolve()
        if not p.is_file():
            raise Refusal("nested setup script {} is missing".format(p))
        rec["nested"][str(p)] = sha(p)
    return rec


def draft(args):
    bound = check(args.authorization, args.package_commit, args.manifest_sha)
    runs = load_runs()
    outroot = Path(runs["outroot"])
    if not outroot.is_absolute() or os.path.realpath(str(outroot)) != os.path.normpath(str(outroot)):
        raise Refusal("the frozen outroot {} must be absolute and free of symlinks".format(outroot))
    try:
        outroot.mkdir(parents=False)
    except FileExistsError:
        raise Refusal("outroot {} already exists: one admission per grant".format(outroot)) from None
    man = json.loads(MANIFEST.read_text())["files"]
    common = [PKG + "/xr_run.py", "unbinned_unfolding/python/omnifold.py",
              "2d-unfolding/uq/coverage_fixed_truth/n2/__init__.py",
              "2d-unfolding/uq/coverage_fixed_truth/n2/execution.py"]
    inputs = {k: v["sha256"] for k, v in runs["inputs"].items()}
    expect = {name: {"commit": bound["head"], "modules": {m: man[m] for m in common + [r["driver"]]},
                     "inputs": inputs} for name, r in runs["runs"].items()}
    adm = {"schema": "xr-admission/2", "status": "ADMITTED", "head": bound["head"],
           "authorization": bound["authorization"], "package_commit": args.package_commit,
           "manifest_sha256": args.manifest_sha, "checkout": str(REPO), "outroot": str(outroot),
           "runs_sha256": sha(RUNS), "references_sha256": sha(HERE / "manifest" / "references.json"),
           "setup": setup_record(args.setup, runs["environment"]["nested_setup"]), "expect": expect,
           "kinds": runs["kinds"], "cap_node_h": runs["cap_node_h"],
           "stop_after_hours": runs["stop_after_hours_from_first_submission"], "grant_date": runs["grant_date"],
           "drafted_utc": utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")}
    path = outroot / "admission.json"
    with open(str(path), "x") as fh:
        fh.write(json.dumps(adm, indent=1, sort_keys=True) + "\n")
    print("[xr-admit] ADMITTED -> {}".format(path))
    return 0


def verify(args):
    adm = json.loads(Path(args.admission).read_text())
    if adm.get("status") != "ADMITTED":
        raise Refusal("admission status {!r}".format(adm.get("status")))
    if Path(args.admission).resolve() != Path(adm["outroot"]) / "admission.json":
        raise Refusal("the admission is not the outroot's own admission.json")
    bound = check(adm["authorization"]["path"], adm["package_commit"], adm["manifest_sha256"])
    if bound["head"] != adm["head"] or Path(adm["checkout"]).resolve() != REPO:
        raise Refusal("the checkout or HEAD differs from the admission")
    now = setup_record(adm["setup"]["path"], load_runs()["environment"]["nested_setup"])
    if now != adm["setup"]:
        raise Refusal("the environment setup (or a script it sources) changed since admission")
    print("[xr-admit] admission verified")
    return 0


def parse_billing(tres):
    m = re.search(r"billing=(\d+)", tres or "")
    return int(m.group(1)) if m else None


def seconds(limit):
    """Slurm TimeLimit [D-]HH:MM:SS (or MM:SS) in seconds."""
    days, _, hms = limit.rpartition("-")
    parts = [int(p) for p in hms.split(":")]
    while len(parts) < 3:
        parts.insert(0, 0)
    return (int(days) if days else 0) * 86400 + parts[0] * 3600 + parts[1] * 60 + parts[2]


def kind_of(run_name):
    runs = load_runs()
    if run_name not in runs["runs"]:
        raise Refusal("unknown run {!r}".format(run_name))
    return runs["runs"][run_name]["kind"], runs


def jobcheck(args):
    """Refuse a job whose actual allocation exceeds its kind's frozen caps; print its thread count."""
    kind_name, runs = kind_of(args.run)
    kind = runs["kinds"][kind_name]
    job = os.environ.get("SLURM_JOB_ID")
    if not job:
        raise Refusal("not inside a Slurm job")
    text = run(["scontrol", "show", "job", job, "-o"])
    f = dict(t.split("=", 1) for t in text.split() if "=" in t)
    billing = parse_billing(f.get("TRES", ""))
    checks = {"QOS": f.get("QOS") == kind["qos"], "NumCPUs": f.get("NumCPUs") == str(kind["cpus_per_task"]),
              "billing": billing is not None and billing <= kind["billing_max"],
              "TimeLimit": seconds(f.get("TimeLimit", "99-00:00:00")) <= kind["time_limit_s_max"]}
    if not all(checks.values()):
        raise Refusal("allocation outside the frozen caps for {}: {} (QOS={} NumCPUs={} TRES={} TimeLimit={})".format(
            kind_name, checks, f.get("QOS"), f.get("NumCPUs"), f.get("TRES"), f.get("TimeLimit")))
    print(kind["omp_threads"])
    return 0


def submissions(outroot):
    p = Path(outroot) / "submissions.jsonl"
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def sacct_jobs(psv):
    """``JobID|JobName|State`` rows (header optional) of every ``xr_*`` job, steps excluded."""
    out = []
    for line in Path(psv).read_text().splitlines():
        parts = line.split("|")
        if len(parts) < 3 or parts[0] == "JobID" or "." in parts[0]:
            continue
        if re.fullmatch(r"xr_[A-Za-z0-9]+_a\d+", parts[1]):
            out.append({"job_id": parts[0], "name": parts[1], "state": parts[2].split()[0] if parts[2] else ""})
    return out


def attempts_by_kind(adm, runs, psv):
    """Attempts per kind over the grant: the largest of three independent records."""
    dirs = {k: 0 for k in runs["kinds"]}
    subs = {k: 0 for k in runs["kinds"]}
    sac = {k: 0 for k in runs["kinds"]}
    for r, spec in runs["runs"].items():
        dirs[spec["kind"]] += len(list(Path(adm["outroot"], r).glob("a*")))
    for s in submissions(adm["outroot"]):
        subs[s["kind"]] += 1
    for j in sacct_jobs(psv):
        r = j["name"][3:].rsplit("_a", 1)[0]
        if r in runs["runs"]:
            sac[runs["runs"][r]["kind"]] += 1
    return {k: max(dirs[k], subs[k], sac[k]) for k in runs["kinds"]}, {"dirs": dirs, "submissions": subs, "sacct": sac}


def next_attempt(args):
    """Refuse a submission over a kind's total, a rerun of a completed run, or one past the stop."""
    adm = json.loads(Path(args.admission).read_text())
    kind_name, runs = kind_of(args.run)
    total, parts = attempts_by_kind(adm, runs, args.sacct)
    cap = runs["kinds"][kind_name]["max_attempts_total"]
    if total[kind_name] + 1 > cap:
        raise Refusal("{} {} attempts already used of {} over the grant ({})".format(total[kind_name], kind_name, cap, parts))
    for d in sorted(Path(adm["outroot"], args.run).glob("a*")):
        rec = d / "receipt.json"
        if rec.is_file() and rec.stat().st_size and json.loads(rec.read_text()).get("status") == "complete":
            raise Refusal("{} already has a complete attempt ({}); no rerun".format(args.run, d.name))
    now = parse_utc(args.now) if args.now else utcnow()
    subs = submissions(adm["outroot"])
    first = min((parse_utc(s["submitted_utc"]) for s in subs), default=now)
    stop = first + datetime.timedelta(hours=adm["stop_after_hours"])
    limit = datetime.timedelta(seconds=runs["kinds"][kind_name]["time_limit_s_max"])
    if now > stop:
        raise Refusal("past the stop: {} hours after the first submission {}".format(adm["stop_after_hours"], first))
    if now + limit > stop:
        raise Refusal("a {} job submitted now could run past the stop at {}".format(kind_name, stop))
    attempt = len(list(Path(adm["outroot"], args.run).glob("a*"))) + 1
    # Slurm reads --deadline in the cluster's local time zone
    local = datetime.datetime.fromtimestamp(stop.timestamp()).strftime("%Y-%m-%dT%H:%M:%S")
    print(attempt, local)
    return 0


def ledger(args):
    """Charged node-h of every XR job, plus the ceilings of unfinished ones; attempts; the stop."""
    adm = json.loads(Path(args.admission).read_text())
    runs = load_runs()
    rows = {}
    lines = Path(args.sacct).read_text().splitlines()
    head = lines[0].split("|")
    for line in lines[1:]:
        r = dict(zip(head, line.split("|")))
        if "." not in r["JobID"]:
            rows[r["JobID"]] = r
    charged, pending, report, flagged = 0.0, 0.0, [], []
    subs = submissions(adm["outroot"])
    for s in subs:
        kind = adm["kinds"][s["kind"]]
        r = rows.get(str(s["job_id"]))
        state = r["State"].split()[0] if r else "UNKNOWN"
        billing = parse_billing(r.get("AllocTRES")) if r else None
        elapsed = int(r["ElapsedRaw"]) if r and r.get("ElapsedRaw") else 0
        c = (billing or 0) / 256 * elapsed / 3600
        charged += c
        if state not in FINISHED:
            pending += kind["ceiling_node_h_per_attempt"]
        if billing is not None and billing > kind["billing_max"]:
            flagged.append("{} billing {} > {}".format(s["job_id"], billing, kind["billing_max"]))
        report.append("{} a{} job {} {} billing={} elapsed={}s charged={:.4f}".format(
            s["run"], s["attempt"], s["job_id"], state, billing, elapsed, c))
    counts = {k: sum(1 for s in subs if s["kind"] == k) for k in runs["kinds"]}
    over = list(flagged)
    for k, n in counts.items():
        if n > runs["kinds"][k]["max_attempts_total"]:
            over.append("{} {} attempts > {}".format(n, k, runs["kinds"][k]["max_attempts_total"]))
    if charged + pending > adm["cap_node_h"]:
        over.append("charged {:.4f} + unfinished ceilings {:.4f} > {}".format(charged, pending, adm["cap_node_h"]))
    hours = None
    if subs:
        first = min(parse_utc(s["submitted_utc"]) for s in subs)
        now = parse_utc(args.now) if args.now else utcnow()
        hours = (now - first).total_seconds() / 3600
        if hours > adm["stop_after_hours"] and pending:
            over.append("{:.1f} h after the first submission with unfinished jobs: cancel them".format(hours))
    out = {"charged_node_h": charged, "unfinished_ceiling_node_h": pending, "attempts": counts,
           "hours_since_first_submission": hours, "jobs": report, "over": over}
    print(json.dumps(out, indent=1))
    return OVER if over else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    m = sub.add_parser("manifest")
    m.add_argument("--check", action="store_true")
    for name in ("check", "draft"):
        p = sub.add_parser(name)
        p.add_argument("--authorization", required=True)
        p.add_argument("--package-commit", required=True)
        p.add_argument("--manifest-sha", required=True)
        if name == "draft":
            p.add_argument("--setup", required=True)
    v = sub.add_parser("verify")
    v.add_argument("--admission", required=True)
    for name in ("jobcheck", "next-attempt"):
        p = sub.add_parser(name)
        p.add_argument("--admission", required=True)
        p.add_argument("--run", required=True)
        if name == "next-attempt":
            p.add_argument("--sacct", required=True)
            p.add_argument("--now")
    led = sub.add_parser("ledger")
    led.add_argument("--admission", required=True)
    led.add_argument("--sacct", required=True)
    led.add_argument("--now")
    a = ap.parse_args(argv)
    if not a.cmd:
        ap.error("a command is required")
    try:
        if a.cmd == "manifest":
            return manifest_cmd(a.check)
        if a.cmd == "check":
            check(a.authorization, a.package_commit, a.manifest_sha)
            print("[xr-admit] binding holds")
            return 0
        if a.cmd == "draft":
            return draft(a)
        if a.cmd == "verify":
            return verify(a)
        if a.cmd == "jobcheck":
            return jobcheck(a)
        if a.cmd == "next-attempt":
            return next_attempt(a)
        return ledger(a)
    except Refusal as exc:
        print("[REFUSED] {}".format(exc), file=sys.stderr)
        return REFUSE


if __name__ == "__main__":
    sys.exit(main())
