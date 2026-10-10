#!/usr/bin/env python3
"""XR admission: the package manifest, the authorization binding, the admission record and the ledger.

    xr_admit.py manifest [--check]                     write (or verify) manifest/expected-code.json
    xr_admit.py check  --authorization A --package-commit C --manifest-sha S
    xr_admit.py draft  --authorization A --package-commit C --manifest-sha S --setup F --out ADM
                       [--outroot-base DIR]   (default /pscratch/sd/j/josephrb; tests use a temp dir)
    xr_admit.py verify --admission ADM                  re-run check against the admission's values
    xr_admit.py ledger --admission ADM --sacct PSV      charge and attempt accounting; exit 6 if over
    xr_admit.py jobcheck --admission ADM --run R        inside a job: its allocation within the caps
    xr_admit.py next-attempt --admission ADM --run R    the attempt number a new submission may use

Standard library only (it runs before the analysis environment is sourced).

The binding (``check``), every clause a refusal (exit 3):
* the authorization is a repository-relative path under ``docs/orchestration/``, not a symlink,
  committed at HEAD with the same bytes, and its text names the package commit (40 hex) and the
  manifest sha256 (64 hex) in full;
* the package commit is an ancestor of HEAD, and nothing under the package, an executed module or
  the guard differs between it and HEAD;
* ``manifest/expected-code.json`` hashes to the stated sha256 and every file it lists has that
  digest on disk and at HEAD;
* the work tree is clean.
"""

import argparse
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
EXECUTED = ("2d-unfolding/unfold_2d_omnifold_unbinned.py", "unbinned_unfolding/python/omnifold.py",
            "2d-unfolding/uq/coverage_fixed_truth/n2/__init__.py",
            "2d-unfolding/uq/coverage_fixed_truth/n2/execution.py")
GUARD = ("nd-unfolding/mnv_guarded_run.py",)
GUARD_DIR = "nd-unfolding/mnv_guard_shim"
REFUSE, OVER = 3, 6
OUTROOT_BASE = "/pscratch/sd/j/josephrb"


class Refusal(RuntimeError):
    pass


def git(*args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True, check=True,
                          env=env).stdout


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def package_files():
    tracked = git("ls-files", "-z", "--", PKG, GUARD_DIR).split("\0")
    files = sorted(f for f in tracked if f and "__pycache__" not in f and not f.endswith(".pyc")
                   and f != MANIFEST.relative_to(REPO).as_posix() and "/tests/" not in f)
    return sorted(set(files) | set(EXECUTED) | set(GUARD))


def build_manifest():
    files = {rel: sha(REPO / rel) for rel in package_files()}
    return {"schema": "xr-expected-code/1", "package": PKG, "files": files}


def manifest_cmd(check):
    want = json.dumps(build_manifest(), indent=1, sort_keys=True) + "\n"
    if check:
        have = MANIFEST.read_text() if MANIFEST.exists() else ""
        if have != want:
            print("[xr-admit] manifest/expected-code.json is OUT OF DATE", file=sys.stderr)
            return REFUSE
        print("[xr-admit] manifest current")
        return 0
    MANIFEST.write_text(want)
    print(f"[xr-admit] wrote {MANIFEST.relative_to(REPO)} sha256 {sha(MANIFEST)}")
    return 0


def check(authorization, package_commit, manifest_sha):
    if not re.fullmatch(r"[0-9a-f]{40}", package_commit or ""):
        raise Refusal("the package commit must be 40 lower-case hex characters")
    if not re.fullmatch(r"[0-9a-f]{64}", manifest_sha or ""):
        raise Refusal("the manifest sha256 must be 64 lower-case hex characters")
    rel = os.path.normpath(authorization)
    if os.path.isabs(authorization) or rel.startswith("..") or not rel.startswith("docs/orchestration/"):
        raise Refusal(f"authorization {authorization!r} must be repository-relative under docs/orchestration/")
    if not re.fullmatch(r"docs/orchestration/AUTHORIZATION-\d{8}-[a-z0-9-]+\.md", rel):
        raise Refusal(f"authorization {rel} is not an AUTHORIZATION-<date>-<name>.md record")
    path = REPO / rel
    if path.is_symlink() or not path.is_file():
        raise Refusal(f"authorization {rel} is missing or a symlink")
    head = git("rev-parse", "HEAD").strip()
    try:
        blob = git("rev-parse", f"HEAD:{rel}").strip()
    except subprocess.CalledProcessError:
        raise Refusal(f"authorization {rel} is not committed at HEAD") from None
    if git("hash-object", "--", rel).strip() != blob:
        raise Refusal(f"authorization {rel} differs from its committed bytes")
    text = path.read_text()
    if package_commit not in text or manifest_sha not in text:
        raise Refusal("the authorization does not name the package commit and the manifest sha256 in full")
    if subprocess.run(["git", "-C", str(REPO), "merge-base", "--is-ancestor", package_commit, head]).returncode:
        raise Refusal(f"package commit {package_commit} is not an ancestor of HEAD {head}")
    changed = git("diff", "--name-only", package_commit, head, "--", PKG, *EXECUTED, *GUARD, GUARD_DIR).split()
    if changed:
        raise Refusal(f"the package changed after {package_commit}: {changed}")
    if sha(MANIFEST) != manifest_sha:
        raise Refusal(f"manifest/expected-code.json has sha256 {sha(MANIFEST)}, not {manifest_sha}")
    man = json.loads(MANIFEST.read_text())
    if man != build_manifest():
        raise Refusal("manifest/expected-code.json does not describe the files on disk")
    for f, digest in man["files"].items():
        if git("hash-object", "--", f).strip() != git("rev-parse", f"HEAD:{f}").strip():
            raise Refusal(f"{f} differs from HEAD")
    if git("status", "--porcelain", "--untracked-files=no").strip():
        raise Refusal("the work tree has uncommitted changes to tracked files")
    return {"head": head, "authorization": {"path": rel, "sha256": sha(path)}}


def draft(args):
    bound = check(args.authorization, args.package_commit, args.manifest_sha)
    runs = json.loads((HERE / "manifest" / "runs.json").read_text())
    man = json.loads(MANIFEST.read_text())["files"]
    common = [f"{PKG}/xr_run.py", "unbinned_unfolding/python/omnifold.py",
              "2d-unfolding/uq/coverage_fixed_truth/n2/__init__.py",
              "2d-unfolding/uq/coverage_fixed_truth/n2/execution.py"]
    inputs = {k: v["sha256"] for k, v in runs["inputs"].items()}
    expect = {name: {"commit": bound["head"], "modules": {m: man[m] for m in common + [r["driver"]]},
                     "inputs": inputs} for name, r in runs["runs"].items()}
    setup = Path(args.setup).resolve()
    adm = {"schema": "xr-admission/1", "status": "ADMITTED", **bound,
           "package_commit": args.package_commit, "manifest_sha256": args.manifest_sha,
           "checkout": str(REPO), "outroot": f"{args.outroot_base}/xr-{bound['head'][:8]}",
           "runs_sha256": sha(HERE / "manifest" / "runs.json"),
           "references_sha256": sha(HERE / "manifest" / "references.json"),
           "setup": {"path": str(setup), "sha256": sha(setup)}, "expect": expect,
           "kinds": runs["kinds"], "cap_node_h": runs["cap_node_h"]}
    out = Path(args.out)
    if out.exists():
        raise Refusal(f"admission {out} already exists")
    out.write_text(json.dumps(adm, indent=1, sort_keys=True) + "\n")
    print(f"[xr-admit] ADMITTED -> {out} (outroot {adm['outroot']})")
    return 0


def verify(args):
    adm = json.loads(Path(args.admission).read_text())
    if adm.get("status") != "ADMITTED":
        raise Refusal(f"admission status {adm.get('status')!r}")
    bound = check(adm["authorization"]["path"], adm["package_commit"], adm["manifest_sha256"])
    if bound["head"] != adm["head"] or Path(adm["checkout"]).resolve() != REPO:
        raise Refusal("the checkout or HEAD differs from the admission")
    if sha(adm["setup"]["path"]) != adm["setup"]["sha256"]:
        raise Refusal("the environment setup changed since admission")
    print("[xr-admit] admission verified")
    return 0


def parse_billing(tres):
    m = re.search(r"billing=(\d+)", tres or "")
    return int(m.group(1)) if m else None


def ledger(args):
    """Charged node-h of every XR job this outroot submitted, plus the ceilings of unfinished ones."""
    adm = json.loads(Path(args.admission).read_text())
    subs = [json.loads(l) for l in Path(adm["outroot"], "submissions.jsonl").read_text().splitlines() if l.strip()]
    rows = {}
    lines = Path(args.sacct).read_text().splitlines()
    head = lines[0].split("|")
    for line in lines[1:]:
        r = dict(zip(head, line.split("|")))
        if "." not in r["JobID"]:
            rows[r["JobID"]] = r
    charged, pending, attempts, report = 0.0, 0.0, {"exact": 0, "lgbm": 0}, []
    for s in subs:
        kind = adm["kinds"][s["kind"]]
        attempts[s["kind"]] += 1
        r = rows.get(str(s["job_id"]))
        state = r["State"].split()[0] if r else "UNKNOWN"
        billing = parse_billing(r.get("AllocTRES")) if r else None
        elapsed = int(r["ElapsedRaw"]) if r and r["ElapsedRaw"] else 0
        done = state in ("COMPLETED", "FAILED", "CANCELLED", "TIMEOUT", "OUT_OF_MEMORY", "NODE_FAIL", "PREEMPTED")
        c = (billing or 0) / 256 * elapsed / 3600
        charged += c
        if not done:
            pending += kind["ceiling_node_h_per_attempt"]
        if billing is not None and billing > kind["billing_max"]:
            report.append(f"{s['job_id']} billing {billing} > {kind['billing_max']}")
        report.append(f"{s['run']} a{s['attempt']} job {s['job_id']} {state} billing={billing} elapsed={elapsed}s charged={c:.4f}")
    over = []
    for k, n in attempts.items():
        if n > adm["kinds"][k]["max_attempts_total"]:
            over.append(f"{n} {k} attempts > {adm['kinds'][k]['max_attempts_total']}")
    if charged + pending > adm["cap_node_h"]:
        over.append(f"charged {charged:.4f} + unfinished ceilings {pending:.4f} > {adm['cap_node_h']}")
    out = {"charged_node_h": charged, "unfinished_ceiling_node_h": pending, "attempts": attempts,
           "jobs": report, "over": over}
    print(json.dumps(out, indent=1))
    return OVER if over or any("billing" in r and ">" in r for r in report) else 0


def kind_of(adm, run):
    runs = json.loads((HERE / "manifest" / "runs.json").read_text())
    if run not in runs["runs"]:
        raise Refusal(f"unknown run {run!r}")
    return runs["runs"][run]["kind"], runs


def seconds(limit):
    """Slurm TimeLimit [D-]HH:MM:SS (or MM:SS) in seconds."""
    days, _, hms = limit.rpartition("-")
    parts = [int(p) for p in hms.split(":")]
    while len(parts) < 3:
        parts.insert(0, 0)
    return (int(days) if days else 0) * 86400 + parts[0] * 3600 + parts[1] * 60 + parts[2]


def jobcheck(args):
    """Refuse a job whose actual allocation exceeds its kind's frozen caps; print its thread count."""
    adm = json.loads(Path(args.admission).read_text())
    kind_name, runs = kind_of(adm, args.run)
    kind = runs["kinds"][kind_name]
    job = os.environ.get("SLURM_JOB_ID")
    if not job:
        raise Refusal("not inside a Slurm job")
    text = subprocess.run(["scontrol", "show", "job", job, "-o"], capture_output=True, text=True, check=True).stdout
    f = dict(t.split("=", 1) for t in text.split() if "=" in t)
    billing = parse_billing(f.get("TRES", ""))
    checks = {"QOS": f.get("QOS") == kind["qos"], "NumCPUs": f.get("NumCPUs") == str(kind["cpus_per_task"]),
              "billing": billing is not None and billing <= kind["billing_max"],
              "TimeLimit": seconds(f.get("TimeLimit", "99-00:00:00")) <= kind["time_limit_s_max"]}
    if not all(checks.values()):
        raise Refusal(f"allocation outside the frozen caps for {kind_name}: {checks} "
                      f"(QOS={f.get('QOS')} NumCPUs={f.get('NumCPUs')} TRES={f.get('TRES')} TimeLimit={f.get('TimeLimit')})")
    print(kind["omp_threads"])
    return 0


def attempts_of(outroot, runs, kind_name):
    return sum(len(list(Path(outroot, r).glob("a*"))) for r, spec in runs["runs"].items() if spec["kind"] == kind_name)


def next_attempt(args):
    """Refuse a submission that would exceed the kind's total attempts or rerun a completed run."""
    adm = json.loads(Path(args.admission).read_text())
    kind_name, runs = kind_of(adm, args.run)
    used = attempts_of(adm["outroot"], runs, kind_name)
    if used + 1 > runs["kinds"][kind_name]["max_attempts_total"]:
        raise Refusal(f"{used} {kind_name} attempts already used of {runs['kinds'][kind_name]['max_attempts_total']}")
    mine = sorted(Path(adm["outroot"], args.run).glob("a*"))
    for d in mine:
        rec = d / "receipt.json"
        if rec.is_file() and rec.stat().st_size and json.loads(rec.read_text()).get("status") == "complete":
            raise Refusal(f"{args.run} already has a complete attempt ({d.name}); no rerun")
    print(len(mine) + 1)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("manifest")
    m.add_argument("--check", action="store_true")
    for name in ("check", "draft"):
        p = sub.add_parser(name)
        p.add_argument("--authorization", required=True)
        p.add_argument("--package-commit", required=True)
        p.add_argument("--manifest-sha", required=True)
        if name == "draft":
            p.add_argument("--setup", required=True)
            p.add_argument("--out", required=True)
            p.add_argument("--outroot-base", default=OUTROOT_BASE)
    v = sub.add_parser("verify")
    v.add_argument("--admission", required=True)
    led = sub.add_parser("ledger")
    led.add_argument("--admission", required=True)
    led.add_argument("--sacct", required=True)
    for name in ("jobcheck", "next-attempt"):
        p = sub.add_parser(name)
        p.add_argument("--admission", required=True)
        p.add_argument("--run", required=True)
    a = ap.parse_args(argv)
    try:
        if a.cmd == "jobcheck":
            return jobcheck(a)
        if a.cmd == "next-attempt":
            return next_attempt(a)
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
        return ledger(a)
    except Refusal as exc:
        print(f"[REFUSED] {exc}", file=sys.stderr)
        return REFUSE


if __name__ == "__main__":
    sys.exit(main())
