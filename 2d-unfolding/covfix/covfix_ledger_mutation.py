"""Hand mutants for covfix_ledger.py: each must be killed by test_covfix_ledger.py.

  python3 -B covfix_ledger_mutation.py        one line per mutant; exit 0 only if all are killed

Each mutant runs in a fresh temp dir with copies of the module and its test. A failure that names no test, or an
import or discovery failure, is a HARNESS FAILURE, not a kill.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILES = ("covfix_ledger.py", "test_covfix_ledger.py")
L = "covfix_ledger.py"
MUTANTS = [
    ("no-minute-rounding", "return nodes * math.ceil(time_limit_s / 60) / 60.0", "return nodes * time_limit_s / 3600.0"),
    ("float-nodes-ok", "isinstance(nodes, int) and nodes >= 1", "nodes >= 1"),
    ("state-first-word", "return raw.split()[0] if raw.split() else \"\"", "return raw"),
    ("cap-group-unchecked", "        if set(self.groups.values()) - set(self.caps):\n", "        if False:\n"),
    ("no-fsync", "            os.fsync(fh.fileno())\n", ""),
    ("unrecorded-allowed", "            if unrecorded:\n", "            if False:\n"),
    ("ceiling-unchecked", "if gate[\"total\"] > self.ceiling + EPS or ", "if "),
    ("cap-unchecked", " or gate[\"group_total\"] > self.caps[group] + EPS:", ":"),
    ("held-not-counted", "                held += it[\"reservation\"]", "                pass"),
    ("group-filter-off", "            if group is not None and self.groups[it[\"phase\"]] != group:", "            if False:"),
    ("phase-unvalidated", "        if not PHASE.fullmatch(phase) or phase not in self.groups:", "        if not PHASE.fullmatch(phase):"),
    ("job-nonnumeric-ok", "        if not re.fullmatch(r\"[0-9]+\", str(job)):\n            raise", "        if False:\n            raise"),
    ("double-submit-ok", "            if st[\"intents\"][intent][\"job\"] is not None:", "            if False:"),
    ("job-reuse-ok", "            if any(it[\"job\"] == str(job) for it in st[\"intents\"].values()):", "            if False:"),
    ("ambiguous-matched", "if len(cands) == 1 and", "if len(cands) >= 1 and"),
    ("used-job-matched", " and str(cands[0][\"JobID\"]) not in {x[\"job\"] for x in st[\"intents\"].values()}:", ":"),
    ("step-rows-matched", "if m and re.fullmatch(r\"[0-9]+\", str(r.get(\"JobID\", \"\"))):", "if m:"),
    ("running-charged", "sacct_state(r.get(\"State\", \"\")) in TERMINAL:", "sacct_state(r.get(\"State\", \"\")) != \"\":"),
    ("charge-twice", "                if it[\"charge\"] is None:\n                    r = by_job", "                if True:\n                    r = by_job"),
    ("charge-nodes-ignored", "charge = int(r[\"NNodes\"]) * int(r[\"ElapsedRaw\"]) / 3600.0", "charge = int(r[\"ElapsedRaw\"]) / 3600.0"),
    ("unexpected-toy-ok", "        if toy not in expected:\n", "        if False:\n"),
    ("bad-sha-ok", "        if not re.fullmatch(r\"[0-9a-f]{64}\", sha256):\n", "        if False:\n"),
    ("duplicate-toy-ok", "            if (phase, arm, toy) in self.state()[\"toys\"]:", "            if False:"),
    ("unknown-kind-ok", "                raise Refusal(f\"unknown ledger entry kind {k!r}\")", "                pass"),
    ("lock-noop", "            fcntl.flock(fh, fcntl.LOCK_EX)\n", ""),
]


def run_tests(d: Path) -> tuple[int, str]:
    r = subprocess.run([sys.executable, "-B", "-m", "unittest", "test_covfix_ledger.py"], cwd=d,
                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL, timeout=300,
                       text=True, env=dict(os.environ))
    lines = r.stderr.splitlines()
    named = [ln for ln in lines if ln.startswith(("FAIL: ", "ERROR: "))]
    if r.returncode != 0 and (not named or any("_FailedTest" in ln for ln in named)):
        return -1, "HARNESS: " + (lines[-1] if lines else "no stderr")
    return r.returncode, (named[0] if named else (lines[-1] if lines else ""))


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        for f in FILES:
            shutil.copy2(HERE / f, Path(td) / f)
        base, why = run_tests(Path(td))
    print(f"baseline rc {base} {why}")
    if base != 0:
        return 2
    bad = []
    for mid, old, new in MUTANTS:
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            for f in FILES:
                shutil.copy2(HERE / f, d / f)
            src = (d / L).read_text()
            if src.count(old) != 1:
                print(f"{mid}: NOT APPLIED (pattern occurs {src.count(old)} times)")
                bad.append(mid)
                continue
            (d / L).write_text(src.replace(old, new))
            rc, why = run_tests(d)
        status = "killed" if rc > 0 else ("HARNESS FAILURE" if rc < 0 else "SURVIVED")
        if rc <= 0:
            bad.append(mid)
        print(f"{mid}: {status} {why}")
    print(f"{len(MUTANTS) - len(bad)}/{len(MUTANTS)} killed; survived, harness or not applied: {bad}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
