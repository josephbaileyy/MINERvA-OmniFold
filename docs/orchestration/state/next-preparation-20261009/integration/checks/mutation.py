"""Integration mutation controls: each mutant must turn its targeted test red; the unmutated clone
must pass the same commands first. Usage: mutation.py WORKTREE HEAD VENV_PYTHON OUT.json"""
import json, os, subprocess, sys, tempfile, time
from pathlib import Path

W, HEAD, PYR, OUT = sys.argv[1:5]
N2 = "2d-unfolding/uq/coverage_fixed_truth/n2"
TOY = "2d-unfolding/uq/coverage_fixed_truth/fixed_truth_toy.py"
EXE = f"{N2}/execution.py"
HAR = f"{N2}/harness.py"
ROOTLIB = subprocess.run(["root-config", "--libdir"], capture_output=True, text=True).stdout.strip()
TESTS = {
    "r1": ([PYR, "-m", "unittest", "discover", "-k", "symlinked", "-s", N2, "-p", "test_producer_prov*.py"], True),
    "r2": (["python3", "-m", "unittest", "discover", "-k", "normalized", "-s", N2, "-p", "test_n2*.py"], False),
    "deps": ([PYR, "-m", "unittest", "discover", "-s", N2, "-p", "test_producer_final*.py"], True),
}
R2_NOW = ("        norm = \"\" if Path(rel).is_absolute() else os.path.normpath(rel).replace(os.sep, \"/\")\n"
          "        if norm.startswith(\"../\") or norm in (\"\", \".\", \"..\") or "
          "(top / norm).resolve() != top / norm:\n"
          "            norm = \"\"\n")
R2_FIRST = ("        try:\n            norm = (top / rel).resolve().relative_to(top).as_posix()\n"
            "        except ValueError:\n            norm = \"\"\n")
MUTANTS = [  # (id, file, old, new, test)
    ("R1-revert", TOY, "        try:\n            rel = path.resolve().relative_to(REPO).as_posix()\n"
     "        except ValueError:\n            raise gx.ProvenanceRefusal(f\"{name}: {path} resolves outside the admitted checkout \"\n"
     "                                       f\"{REPO}\") from None\n",
     "        rel = path.resolve().relative_to(REPO).as_posix()\n", "r1"),
    ("R2-revert", HAR, R2_NOW, "        norm = rel\n", "r2"),
    ("R2-first-version", HAR, R2_NOW, R2_FIRST, "r2"),
    ("no-import-sweep", EXE, '    have = {r["path"] for r in records}\n', "    return []\n", "deps"),
    ("strict-ignores-unstated", EXE, 'if expectations["commit"] is None or missing:',
     'if expectations["commit"] is None:', "deps"),
    ("strict-ignores-head-drift", EXE, '        if ident["mismatched"]:', "        if False:", "deps"),
    ("commit-unchecked", EXE,
     'if expectations["commit"] is not None and ident["commit"] != expectations["commit"]:',
     "if False:", "deps"),
]


def clone(base, tag):
    d = Path(base) / tag
    subprocess.run(["git", "clone", "-q", "--shared", "--no-checkout", W, str(d)], check=True)
    subprocess.run(["git", "-C", str(d), "-c", "advice.detachedHead=false", "checkout", "-q", HEAD], check=True)
    return d


def run(d, test):
    cmd, root = TESTS[test]
    env = dict(os.environ, OMP_NUM_THREADS="1", PYTHONDONTWRITEBYTECODE="1")
    if root:
        env["PYTHONPATH"] = ROOTLIB
    t = time.time()
    cp = subprocess.run(cmd, cwd=d, capture_output=True, text=True, env=env)
    tail = [l for l in cp.stderr.splitlines() if l.startswith(("Ran ", "OK", "FAILED"))]
    return {"rc": cp.returncode, "summary": tail, "wall_s": round(time.time() - t, 1),
            "skipped": "skipped" in cp.stderr}


results = {"head": HEAD, "control": {}, "mutants": []}
with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as base:
    ctl = clone(base, "control")
    for t in TESTS:
        results["control"][t] = run(ctl, t)
    for mid, rel, old, new, test in MUTANTS:
        d = clone(base, mid)
        p = d / rel
        s = p.read_text()
        applied = s.count(old) == 1
        if applied:
            p.write_text(s.replace(old, new))
        r = run(d, test) if applied else {"rc": None}
        r.update(id=mid, file=rel, test=test, applied=applied,
                 caught=bool(applied and r["rc"] not in (0, None)))
        results["mutants"].append(r)
        print(mid, r, flush=True)
results["all_controls_pass"] = all(v["rc"] == 0 and not v["skipped"] for v in results["control"].values())
results["caught"] = sum(m["caught"] for m in results["mutants"])
results["n"] = len(MUTANTS)
Path(OUT).write_text(json.dumps(results, indent=1) + "\n")
print(json.dumps({k: results[k] for k in ("all_controls_pass", "caught", "n")}))
