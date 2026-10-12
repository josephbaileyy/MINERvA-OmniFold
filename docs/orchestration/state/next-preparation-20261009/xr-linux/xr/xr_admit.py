#!/usr/bin/env python3
"""XR admission: the package manifest, the authorization binding, the admission record and the ledger.

    xr_admit.py manifest [--check]                   write (or verify) manifest/expected-code.json
    xr_admit.py check  --authorization A --package-commit C --manifest-sha S
    xr_admit.py draft  --authorization A --package-commit C --manifest-sha S --setup F
    xr_admit.py verify --admission ADM                re-run check against the admission's values
    xr_admit.py jobcheck --admission ADM --run R [--record F]   inside a job: its allocation within the caps
    xr_admit.py next-attempt --admission ADM --run R --sacct PSV [--now ISO] [--diagnosis TEXT]
                                                      prints: ATTEMPT DEADLINE
    xr_admit.py ledger --admission ADM --sacct PSV    cumulative charge, attempts and the stop; exit 6 if over

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

The amendment (``runs.json`` ``amendment`` and ``prior``):
* the allocation is read from the named ``scontrol -o`` fields, each required exactly once, and the
  billing from ``AllocTRES`` (absent, ``(null)``, malformed or over the cap refuses);
* this amendment's jobs are named ``<prefix>_<RUN>_a<N>`` and its attempt caps count only them
  (attempt directories, the submissions record, and ``sacct`` since ``cumulative_since``);
* every earlier grant's jobs (``prior.grants``: the 2026-10-10 ``xr_*`` five and the 2026-10-11
  ``xrr_PF_a1``) must all be in ``sacct``, and no other job with their prefixes may be. Their
  charge stays in the cumulative ledger and in every submission's planned ceiling against
  ``cap_node_h``. A new package, outroot or date does not reset it;
* release order: no run before the preflight has passed, and nothing but the preflight and the
  first run (L0) before that run has a complete, comparable receipt. A passed preflight is the PF
  job's own receipt (bound to its submission and its recorded allocation line), with its fixture
  stage and controls met, no launch in its no-launch window, and a clean OI-136 inventory;
* a second attempt of any run (the spare attempts) needs a stated ``--diagnosis``, recorded with
  the submission: the spares are for diagnosed infrastructure failures only.
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
#: Executed files outside this package: the driver, the helper, ``n2``, X0p's execution-only record of
#: the ``d1bc8813`` driver (in the frozen two-d-followup package) and the preflight's fixture writer
#: (in the frozen SB1 package). Both frozen packages are read, never edited.
EXECUTED = ("2d-unfolding/unfold_2d_omnifold_unbinned.py", "unbinned_unfolding/python/omnifold.py",
            "2d-unfolding/uq/coverage_fixed_truth/n2/__init__.py",
            "2d-unfolding/uq/coverage_fixed_truth/n2/execution.py",
            "docs/orchestration/state/next-preparation-20261009/two-d-followup/xr/record/unfold_2d_omnifold_unbinned_d1bc8813.py.record",
            "docs/orchestration/state/next-preparation-20261009/sb1-prep/tests/make_fixture_omnifile.py")
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
    if any(os.path.normpath(g["outroot"]) == os.path.normpath(str(outroot)) for g in runs["prior"]["grants"]):
        raise Refusal("the outroot {} is a prior grant's".format(outroot))
    try:
        outroot.mkdir(parents=False)
    except FileExistsError:
        raise Refusal("outroot {} already exists: one admission per grant".format(outroot)) from None
    man = json.loads(MANIFEST.read_text())["files"]
    common = [PKG + "/xr_run.py", "unbinned_unfolding/python/omnifold.py",
              "2d-unfolding/uq/coverage_fixed_truth/n2/__init__.py",
              "2d-unfolding/uq/coverage_fixed_truth/n2/execution.py"]
    inputs = {k: v["sha256"] for k, v in runs["inputs"].items()}
    def modules(r):
        """A run's driver; for the preflight, every driver of the runs it stands in front of, the
        fixture writer and the comparator."""
        if "preflight_of" not in r:
            return [r["driver"]]
        return sorted({runs["runs"][o]["driver"] for o in r["preflight_of"]}) + [
            runs["preflight"]["fixture"]["maker"], PKG + "/xr_compare.py"]
    expect = {name: {"commit": bound["head"], "modules": {m: man[m] for m in common + modules(r)},
                     "inputs": inputs} for name, r in runs["runs"].items()}
    adm = {"schema": "xr-admission/3", "status": "ADMITTED", "head": bound["head"],
           "authorization": bound["authorization"], "package_commit": args.package_commit,
           "manifest_sha256": args.manifest_sha, "checkout": str(REPO), "outroot": str(outroot),
           "runs_sha256": sha(RUNS), "references_sha256": sha(HERE / "manifest" / "references.json"),
           "setup": setup_record(args.setup, runs["environment"]["nested_setup"]), "expect": expect,
           "kinds": runs["kinds"], "cap_node_h": runs["cap_node_h"],
           "stop_after_hours": runs["stop_after_hours_from_first_submission"],
           "cumulative_since": runs["amendment"]["cumulative_since"],
           "job_name_prefix": runs["amendment"]["job_name_prefix"], "prior": runs["prior"], "release": runs["release"],
           "window": runs["window"],
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
    """The ``billing`` count of a TRES value (``scontrol`` AllocTRES or ``sacct`` AllocTRES).

    None for an absent, empty or ``(null)`` value, an item that is not ``key=value``, or a billing
    that is missing, repeated or not a whole number. The callers refuse on None."""
    if not tres or tres == "(null)":
        return None
    pairs = [item.split("=", 1) for item in tres.split(",")]
    if any(len(kv) != 2 or not kv[0] or not kv[1] for kv in pairs):
        return None
    vals = [v for k, v in pairs if k == "billing"]
    if len(vals) != 1 or not re.fullmatch(r"[0-9]+", vals[0]):
        return None
    return int(vals[0])


def scontrol_field(text, key):
    """The value of ``key`` in one ``scontrol show job <id> -o`` line, which must hold it exactly once.

    The line is ``Key=Value`` tokens, but ``Command=``, ``SubmitLine=`` and ``Comment=`` carry free
    text (the sbatch argv, spaces included) after the scheduler's own fields, so splitting the
    whole line into a dict lets a later token stand in for a field. A key that is absent or appears
    twice refuses. Perlmutter prints ``ReqTRES=`` and ``AllocTRES=``, never ``TRES=``
    (``tests/scheduler/``)."""
    hits = re.findall(r"(?:^|\s){}=(\S*)".format(re.escape(key)), text)
    if len(hits) != 1:
        raise Refusal("scontrol field {} appears {} times".format(key, len(hits)))
    return hits[0]


def check_allocation(text, kind, job_id):
    """Refuse an allocation outside the kind's caps; billing is the allocation actually granted."""
    vals, errors = {}, []
    for key in ("JobId", "QOS", "NumCPUs", "TimeLimit", "AllocTRES"):
        try:
            vals[key] = scontrol_field(text, key)
        except Refusal as exc:
            errors.append(str(exc))
    if errors:
        raise Refusal("unreadable allocation: {}".format("; ".join(errors)))
    billing = parse_billing(vals["AllocTRES"])
    try:
        limit = seconds(vals["TimeLimit"])
    except ValueError:
        limit = None
    checks = {"JobId": vals["JobId"] == str(job_id), "QOS": vals["QOS"] == kind["qos"],
              "NumCPUs": vals["NumCPUs"] == str(kind["cpus_per_task"]),
              "billing": billing is not None and billing <= kind["billing_max"],
              "TimeLimit": limit is not None and limit <= kind["time_limit_s_max"]}
    if not all(checks.values()):
        raise Refusal("allocation outside the frozen caps: {} ({})".format(checks, vals))
    return dict(vals, billing=billing)


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
    """Refuse a job whose actual allocation exceeds its kind's frozen caps; print its thread count.

    With ``--record`` the raw ``scontrol`` line is first written there (created exclusively), so a
    refused allocation is still on record."""
    kind_name, runs = kind_of(args.run)
    kind = runs["kinds"][kind_name]
    job = os.environ.get("SLURM_JOB_ID")
    if not job:
        raise Refusal("not inside a Slurm job")
    text = run(["scontrol", "show", "job", job, "-o"])
    if args.record:
        with open(args.record, "x") as fh:
            fh.write(text)
    try:
        check_allocation(text, kind, job)
    except Refusal as exc:
        raise Refusal("{} ({})".format(exc, kind_name)) from None
    print(kind["omp_threads"])
    return 0


def submissions(outroot):
    p = Path(outroot) / "submissions.jsonl"
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def sacct_jobs(psv, prefix):
    """``JobID|JobName|State`` rows (header optional) of the jobs named ``<prefix>_<RUN>_a<N>``, steps excluded."""
    out = []
    pat = re.compile(r"{}_([A-Za-z0-9]+)_a(\d+)".format(re.escape(prefix)))
    for line in Path(psv).read_text().splitlines():
        parts = line.split("|")
        if len(parts) < 3 or parts[0] == "JobID" or "." in parts[0]:
            continue
        m = pat.fullmatch(parts[1])
        if m:
            out.append({"job_id": parts[0], "name": parts[1], "run": m.group(1),
                        "state": parts[2].split()[0] if parts[2] else ""})
    return out


def check_prior(runs, psv):
    """Every earlier grant's jobs must all be listed, and no other job with its name prefix."""
    for grant in runs["prior"]["grants"]:
        seen = {j["job_id"]: j for j in sacct_jobs(psv, grant["job_name_prefix"])}
        missing = sorted(set(grant["jobs"]) - set(seen))
        extra = sorted(set(seen) - set(grant["jobs"]))
        if missing or extra:
            raise Refusal("sacct does not show exactly the {}_* jobs of {}: missing {} unexpected {}".format(
                grant["job_name_prefix"], grant["authorization"], missing, extra))
        wrong = sorted(j for j, r in grant["jobs"].items() if seen[j]["run"] != r)
        if wrong:
            raise Refusal("prior jobs {} carry another run name than recorded".format(wrong))


def attempts_by_kind(adm, runs, psv):
    """This amendment's attempts per kind: the largest of three independent records."""
    dirs = {k: 0 for k in runs["kinds"]}
    subs = {k: 0 for k in runs["kinds"]}
    sac = {k: 0 for k in runs["kinds"]}
    for r, spec in runs["runs"].items():
        dirs[spec["kind"]] += len(list(Path(adm["outroot"], r).glob("a*")))
    for s in submissions(adm["outroot"]):
        subs[s["kind"]] += 1
    for j in sacct_jobs(psv, runs["amendment"]["job_name_prefix"]):
        if j["run"] in runs["runs"]:
            sac[runs["runs"][j["run"]]["kind"]] += 1
    return {k: max(dirs[k], subs[k], sac[k]) for k in runs["kinds"]}, {"dirs": dirs, "submissions": subs, "sacct": sac}


def admission_matches(adm, rec):
    adm_path = Path(adm["outroot"]) / "admission.json"
    a = rec.get("admission") or {}
    return a.get("sha256") == sha(adm_path) and Path(a.get("path", "")) == adm_path.resolve()


def inventory_clean(path, label):
    """The OI-136 guard's inventory of a guarded run: present, every record of this run's label, no
    refusal or violation, and no module from outside the expected root."""
    p = Path(path)
    if not p.is_file():
        return False
    recs = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    return bool(recs) and all(r.get("label") == label and r.get("verdict") == "REPOSITORY-ORIGINS-INSPECTED"
                              and r.get("violation") is None and r.get("repo_origins_outside_expect_root") == 0
                              and r.get("guard_installed") is True for r in recs)


def preflight_passed(adm, runs):
    """A passing preflight receipt of this admission that the submitted PF job itself produced.

    Besides schema, status, run and this admission, it requires exit 0, strict provenance, the
    fixture stage's verdict PASS with every configuration complete and every control met, the job
    script's controls met, no launch recorded in the no-launch window, the job's own
    ``SLURM_JOB_ID`` equal to the PF job in ``submissions.jsonl`` for that attempt, that job's
    recorded ``scontrol`` line (``scontrol-job.txt``, at its recorded digest) passing the preflight
    kind's allocation check, and the attempt's guard inventory clean. A preflight run by hand
    outside the job releases nothing."""
    pf = runs["release"]["preflight"]
    kind = runs["kinds"][runs["runs"][pf]["kind"]]
    subs = {(s["run"], s["attempt"]): str(s["job_id"]) for s in submissions(adm["outroot"])}
    for d in sorted(Path(adm["outroot"], pf).glob("a*")):
        p = d / "preflight-receipt.json"
        if not (p.is_file() and p.stat().st_size):
            continue
        r = json.loads(p.read_text())
        if not (r.get("schema") == "xr-preflight-receipt/2" and r.get("status") == "preflight-pass"
                and r.get("run") == pf and r.get("fits") == [] and admission_matches(adm, r)
                and d.name == "a{}".format(r.get("attempt"))):
            continue
        if r.get("exit_code") != 0 or (r.get("identity") or {}).get("strict") is not True:
            continue
        fx = r.get("fixture") or {}
        fx_runs = fx.get("runs") or {}
        if not (fx.get("verdict") == "PASS" and set(runs["runs"][pf]["preflight_of"]) <= set(fx_runs)
                and all(v.get("status") == "complete" for v in fx_runs.values())
                and fx.get("checks") and all(v is True for v in fx["checks"].values())
                and fx.get("controls") and all(c.get("met") is True for c in fx["controls"].values())):
            continue
        ctl = r.get("controls") or {}
        if not (ctl and all(c.get("met") is True for c in ctl.values()) and r.get("launches") == []):
            continue
        if not inventory_clean(d / "inventory.jsonl", "XR-{}-{}".format(pf, d.name)):
            continue
        job = ((r.get("environment") or {}).get("slurm") or {}).get("SLURM_JOB_ID")
        if not job or job != subs.get((pf, r.get("attempt"))):
            continue
        rec = r.get("allocation_record") or {}
        line, f = rec.get("line"), d / "scontrol-job.txt"
        if not line or not f.is_file() or f.read_text() != line or sha(f) != rec.get("sha256"):
            continue
        try:
            check_allocation(line, kind, job)
        except Refusal:
            continue
        return True
    return False


def comparable(adm, run_name):
    """The run's newest complete receipt: this admission, strict provenance, output at its digest."""
    best = None
    for d in sorted(Path(adm["outroot"], run_name).glob("a*"),
                    key=lambda d: int(d.name[1:]) if d.name[1:].isdigit() else -1):
        p = d / "receipt.json"
        if p.is_file() and p.stat().st_size:
            r = json.loads(p.read_text())
            if r.get("status") == "complete":
                best = r
    if best is None or best.get("schema") != "xr-receipt/2" or best.get("run") != run_name:
        return False
    out = (best.get("output") or {}).get("path")
    return (admission_matches(adm, best) and (best.get("identity") or {}).get("strict") is True
            and bool(out) and Path(out).is_file() and sha(out) == best["output"].get("sha256"))


def planned_ceiling(adm, runs, extra):
    """Prior charge (every earlier grant) plus the ceiling of every submitted attempt of this
    amendment, plus ``extra``."""
    return runs["prior"]["charged_node_h_recorded"] + extra + sum(
        runs["kinds"][s["kind"]]["ceiling_node_h_per_attempt"] for s in submissions(adm["outroot"]))


def next_attempt(args):
    """Refuse a submission over a kind's cap, out of release order, over the cumulative ceiling,
    a rerun of a completed run, or one that could run past the stop."""
    adm = json.loads(Path(args.admission).read_text())
    kind_name, runs = kind_of(args.run)
    kind = runs["kinds"][kind_name]
    check_prior(runs, args.sacct)
    total, parts = attempts_by_kind(adm, runs, args.sacct)
    if kind_name == "preflight" and preflight_passed(adm, runs):
        raise Refusal("the preflight has already passed; no rerun")
    cap = kind["max_attempts_total"]
    if total[kind_name] + 1 > cap:
        raise Refusal("{} {} attempts already used of {} in this amendment ({})".format(total[kind_name], kind_name, cap, parts))
    earlier = sorted(Path(adm["outroot"], args.run).glob("a*"))
    for d in earlier:
        rec = d / "receipt.json"
        if rec.is_file() and rec.stat().st_size and json.loads(rec.read_text()).get("status") == "complete":
            raise Refusal("{} already has a complete attempt ({}); no rerun".format(args.run, d.name))
    if earlier and not (args.diagnosis or "").strip():
        raise Refusal("{} already has {} attempt(s): a spare attempt needs a stated --diagnosis of an "
                      "infrastructure failure".format(args.run, len(earlier)))
    release = runs["release"]
    if kind_name == "preflight":
        pass
    elif not preflight_passed(adm, runs):
        raise Refusal("no passed preflight for this admission: {} is not released".format(args.run))
    elif args.run != release["first"] and not comparable(adm, release["first"]):
        raise Refusal("{} has no complete, comparable receipt: {} is not released".format(release["first"], args.run))
    planned = planned_ceiling(adm, runs, kind["ceiling_node_h_per_attempt"])
    if planned > runs["cap_node_h"]:
        raise Refusal("planned cumulative ceiling {:.6f} node-h > {}".format(planned, runs["cap_node_h"]))
    now = parse_utc(args.now) if args.now else utcnow()
    subs = submissions(adm["outroot"])
    starts = [parse_utc(s["submitted_utc"]) for s in subs]
    if (runs.get("window") or {}).get("first_submission_utc"):
        starts.append(parse_utc(runs["window"]["first_submission_utc"]))
    first = min(starts, default=now)
    stop = first + datetime.timedelta(hours=adm["stop_after_hours"])
    limit = datetime.timedelta(seconds=kind["time_limit_s_max"])
    if now > stop:
        raise Refusal("past the stop: {} hours after the first submission {}".format(adm["stop_after_hours"], first))
    if now + limit > stop:
        raise Refusal("a {} job submitted now could run past the stop at {}".format(kind_name, stop))
    attempt = len(list(Path(adm["outroot"], args.run).glob("a*"))) + 1
    # Slurm reads --deadline in the cluster's local time zone
    local = datetime.datetime.fromtimestamp(stop.timestamp()).strftime("%Y-%m-%dT%H:%M:%S")
    print(attempt, local)
    return 0


def charge(row):
    billing = parse_billing(row.get("AllocTRES")) if row else None
    elapsed = int(row["ElapsedRaw"]) if row and row.get("ElapsedRaw") else 0
    return (billing or 0) / 256 * elapsed / 3600, billing, elapsed


def ledger(args):
    """Cumulative charged node-h (the prior grant's jobs and this amendment's), plus the ceilings of
    unfinished jobs; this amendment's attempts; the stop."""
    adm = json.loads(Path(args.admission).read_text())
    runs = load_runs()
    rows = {}
    lines = Path(args.sacct).read_text().splitlines()
    head = lines[0].split("|") if lines else []
    over, report = [], []
    lacking = [c for c in ("JobID", "JobName", "State", "ElapsedRaw", "AllocTRES") if c not in head]
    if lacking:
        print(json.dumps({"over": ["the sacct header lacks {}: no row was read".format(lacking)],
                          "header": head}, indent=1))
        return OVER
    for line in lines[1:]:
        r = dict(zip(head, line.split("|")))
        if "." not in r.get("JobID", "."):
            rows[r["JobID"]] = r
    prior = runs["prior"]
    prior_charged = 0.0
    for grant in prior["grants"]:
        for jid, run_name in sorted(grant["jobs"].items()):
            r = rows.get(jid)
            if r is None:
                over.append("prior job {} ({}) is not in sacct".format(jid, run_name))
                continue
            c, billing, elapsed = charge(r)
            prior_charged += c
            if elapsed > 0 and billing is None:
                over.append("prior job {} ran {} s with unreadable billing".format(jid, elapsed))
            report.append("prior {}_{} job {} {} billing={} elapsed={}s charged={:.10f}".format(
                grant["job_name_prefix"], run_name, jid, r["State"].split()[0], billing, elapsed, c))
        pre = re.compile(r"{}_[A-Za-z0-9]+_a\d+".format(re.escape(grant["job_name_prefix"])))
        for jid, r in rows.items():
            if pre.fullmatch(r.get("JobName", "")) and jid not in grant["jobs"]:
                over.append("job {} {} carries a prior prefix but is not a prior job".format(jid, r["JobName"]))
    if abs(prior_charged - prior["charged_node_h_recorded"]) > 1e-12:
        over.append("prior charge {:.13f} differs from the recorded {}".format(prior_charged, prior["charged_node_h_recorded"]))
    charged, pending, flagged = 0.0, 0.0, []
    subs = submissions(adm["outroot"])
    known = {str(s["job_id"]) for s in subs}
    new = re.compile(r"{}_[A-Za-z0-9]+_a\d+".format(re.escape(runs["amendment"]["job_name_prefix"])))
    for jid, r in rows.items():
        if new.fullmatch(r.get("JobName", "")) and jid not in known:
            flagged.append("job {} {} is not in the submissions record".format(jid, r["JobName"]))
    for s in subs:
        kind = adm["kinds"][s["kind"]]
        r = rows.get(str(s["job_id"]))
        state = r["State"].split()[0] if r else "UNKNOWN"
        c, billing, elapsed = charge(r)
        charged += c
        if elapsed > 0 and billing is None:
            flagged.append("job {} ran {} s with unreadable billing".format(s["job_id"], elapsed))
        if state not in FINISHED:
            pending += kind["ceiling_node_h_per_attempt"]
        if billing is not None and billing > kind["billing_max"]:
            flagged.append("{} billing {} > {}".format(s["job_id"], billing, kind["billing_max"]))
        report.append("{} a{} job {} {} billing={} elapsed={}s charged={:.10f}".format(
            s["run"], s["attempt"], s["job_id"], state, billing, elapsed, c))
    counts = {k: sum(1 for s in subs if s["kind"] == k) for k in runs["kinds"]}
    over += flagged
    for k, n in counts.items():
        if n > runs["kinds"][k]["max_attempts_total"]:
            over.append("{} {} attempts > {}".format(n, k, runs["kinds"][k]["max_attempts_total"]))
    cumulative = prior_charged + charged
    if cumulative + pending > adm["cap_node_h"]:
        over.append("cumulative charged {:.6f} + unfinished ceilings {:.6f} > {}".format(cumulative, pending, adm["cap_node_h"]))
    hours = None
    starts = [parse_utc(s["submitted_utc"]) for s in subs]
    if (runs.get("window") or {}).get("first_submission_utc"):
        starts.append(parse_utc(runs["window"]["first_submission_utc"]))
    if starts:
        first = min(starts)
        now = parse_utc(args.now) if args.now else utcnow()
        hours = (now - first).total_seconds() / 3600
        if hours > adm["stop_after_hours"] and pending:
            over.append("{:.1f} h after the first submission with unfinished jobs: cancel them".format(hours))
    out = {"prior_charged_node_h": prior_charged, "amendment_charged_node_h": charged,
           "cumulative_charged_node_h": cumulative, "unfinished_ceiling_node_h": pending,
           "cap_node_h": adm["cap_node_h"], "attempts": counts, "hours_since_first_submission": hours,
           "jobs": report, "over": over}
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
            p.add_argument("--diagnosis")
        else:
            p.add_argument("--record")
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
