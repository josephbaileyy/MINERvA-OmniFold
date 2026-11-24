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
    ('no-minute-rounding', 'return nodes * math.ceil(time_limit_s / 60) * 60', 'return nodes * time_limit_s'),
    ('bool-nodes-ok', 'type(nodes) is int and nodes >= 1', 'isinstance(nodes, int) and nodes >= 1'),
    ('hhmmss-hmm', 'return f"{seconds // 3600:02d}:{seconds % 3600 // 60:02d}:{seconds % 60:02d}"', 'return f"{seconds // 3600}:{seconds % 3600 // 60:02d}"'),
    ('slurm-days-dropped', '((d * 24 + h) * 60 + mi) * 60 + s', '(h * 60 + mi) * 60 + s'),
    ('state-first-word', 'return raw.split()[0] if raw.split() else ""', 'return raw'),
    ('cap-infinite-ok', 'math.isfinite(cap) and cap > 0', 'cap > 0'),
    ('cap-fraction-ok', ' or (cap * 3600) != int(cap * 3600)', ''),
    ('policy-reopen-ok', ' or {k: es[0].get(k) for k in self.policy} != \\\n                json.loads(json.dumps(self.policy)):', ':'),
    ('init-overwrite', 'os.O_WRONLY | os.O_CREAT | os.O_EXCL', 'os.O_WRONLY | os.O_CREAT | os.O_TRUNC'),
    ('init-no-dir-fsync', '            try:\n                os.fsync(dfd)', '            try:\n                pass'),
    ('no-fsync', '            os.fsync(fh.fileno())\n', ''),
    ('dup-intent-ok', '            if k == "intent" and e.get("intent") not in intents and e.get("phase") in self.groups \\', '            if k == "intent" and e.get("phase") in self.groups \\'),
    ('double-submit-replay-ok', 'elif k == "submitted" and it is not None and it["job"] is None and JOBID', 'elif k == "submitted" and it is not None and JOBID'),
    ('double-charge-replay-ok', '\n                    and it["charge"] is None and type(e.get("charge")) is int', '\n                    and type(e.get("charge")) is int'),
    ('dup-accept-replay-ok', 'elif k == "accepted" and (e.get("phase"), e.get("arm"), e.get("toy")) not in toys \\', 'elif k == "accepted" and True \\'),
    ('unknown-kind-ok', '                raise Refusal(f"an invalid ledger transition ({k!r})")', '                pass'),
    ('unrecorded-allowed', '            if unrecorded:\n', '            if False:\n'),
    ('ceiling-unchecked', 'if gate["total_ns"] > self.ceiling or gate["group_total_ns"] > st["caps"][group]:', 'if gate["group_total_ns"] > st["caps"][group]:'),
    ('cap-unchecked', 'if gate["total_ns"] > self.ceiling or gate["group_total_ns"] > st["caps"][group]:', 'if gate["total_ns"] > self.ceiling:'),
    ('held-not-counted', '                held += it["reservation"]', '                pass'),
    ('group-filter-off', '            if group is not None and self.groups[it["phase"]] != group:', '            if False:'),
    ('phase-unvalidated', '        if not PHASE.fullmatch(phase) or phase not in self.groups:\n            raise Refusal(f"unknown phase', '        if not PHASE.fullmatch(phase):\n            raise Refusal(f"unknown phase'),
    ('job-nonnumeric-ok', '    if not JOBID.fullmatch(str(job)):\n        raise Refusal("a job ID is numeric")', '    if False:\n        raise Refusal("a job ID is numeric")'),
    ('double-submit-ok', '            if st["intents"][intent]["job"] is not None:', '            if False:'),
    ('job-reuse-ok', '            if any(it["job"] == str(job) for it in st["intents"].values()):', '            if False:'),
    ('whole-minute-unchecked', '        if it["time_limit_s"] % 60:', '        if False:'),
    ('no-requeue-dropped', '"--no-requeue", *extra, script]', '*extra, script]'),
    ('time-not-hhmmss', 'f"--time={hhmmss(it[\'time_limit_s\'])}"', 'f"--time={it[\'time_limit_s\'] // 60}"'),
    ('jobid-suffix-rejected', 'm = re.fullmatch(r"([0-9]+)(;\\S+)?", r.stdout.strip())', 'm = re.fullmatch(r"([0-9]+)", r.stdout.strip())'),
    ('sbatch-rc-ignored', 'ok = r.returncode == 0 and m', 'ok = m'),
    ('timelimit-unchecked', '        if slurm_seconds(fields.get("TimeLimit", "")) != it["time_limit_s"]:', '        if False:'),
    ('jobname-unchecked', '        if fields.get("JobName") != job_name:', '        if False:'),
    ('qos-unchecked', '        if not re.fullmatch(qos_pattern, fields.get("QOS", "")):', '        if False:'),
    ('no-scancel', '            subprocess.run([scancel, job], capture_output=True', '            (lambda *a, **k: None)([scancel, job], capture_output=True'),
    ('no-stop-on-sbatch-failure', 'self._append({"kind": "stop", "intent": intent, "reason": "sbatch returned no job ID; held"})', 'pass'),
    ('no-stop-on-mismatch', 'self._append({"kind": "stop", "intent": intent, "job": job,', 'None and self._append({"kind": "stop", "intent": intent, "job": job,'),
    ('lost-id-phase-ignored', '                    cands = by_name.get((it["phase"], iid), set())', '                    cands = set().union(set(), *[v for (p, i), v in by_name.items() if i == iid])'),
    ('ambiguous-matched', 'if len(cands) == 1 and next(iter(cands)) not in used:', 'if len(cands) >= 1 and next(iter(cands)) not in used:'),
    ('used-job-matched', ' and next(iter(cands)) not in used:', ':'),
    ('step-rows-matched', '                if not JOBID.fullmatch(str(r.get("JobID", ""))):\n                    continue', '                if False:\n                    continue'),
    ('conflicting-rows-ok', '                    if len(sigs) != 1:', '                    if len(sigs) < 1:'),
    ('running-charged', '                    if state in TERMINAL and', '                    if state != "" and'),
    ('negative-ok', 'UINT.fullmatch(nn) and UINT.fullmatch(el) and int(nn) >= 1', 'UINT.fullmatch(nn) and int(nn) >= 1'),
    ('nnodes-zero-ok', 'and int(nn) >= 1 and zero_ok', 'and int(nn) >= 0 and zero_ok'),
    ('recorded-name-unchecked', '                            and name == f"covfix_{it[\'phase\']}_{iid}":', '                            :'),
    ('charge-twice', '                if it["charge"] is None:\n                    rs = by_job', '                if True:\n                    rs = by_job'),
    ('charge-nodes-ignored', 'charge = int(nn) * int(el)', 'charge = int(el)'),
    ('unexpected-toy-ok', '        if toy not in self.toys.get(phase, {}).get(arm, []):', '        if False:'),
    ('bad-sha-ok', '        if not re.fullmatch(r"[0-9a-f]{64}", sha256):\n', '        if False:\n'),
    ('accept-job-unchecked', '            if not any(it["job"] == job and it["phase"] == phase for it in st["intents"].values()):', '            if False:'),
    ('duplicate-toy-ok', '            if (phase, arm, toy) in st["toys"]:', '            if False:'),
    ('lock-noop', '            fcntl.flock(fh, fcntl.LOCK_EX)\n', ''),
    ('claim-skipped', 'self._append({"kind": "claimed", "intent": intent})', 'pass'),
    ('claim-unchecked', 'if it["claimed"] or it["job"] is not None or it["stop"] is not None:', 'if it["job"] is not None:'),
    ('extra-unrestricted', 'bad = [x for x in extra if not EXTRA_OK.fullmatch(x)]', 'bad = []'),
    ('numnodes-unchecked', '        if fields.get("NumNodes") != str(it["nodes"]):', '        if False:'),
    ('requeue-unchecked', '        if fields.get("Requeue") != "0":', '        if False:'),
    ('zero-uncorroborated', 'zero_ok = not (UINT.fullmatch(el) and int(el) == 0) or start in NOT_STARTED', 'zero_ok = True'),
    ('job-not-canonical', 'return str(int(str(job)))', 'return str(job)'),
    ('row-job-not-canonical', 'jid = canon_job(r["JobID"])', 'jid = str(r["JobID"])'),
    ('negative-replay-ok', 'and type(e.get("charge")) is int and e["charge"] >= 0:', 'and type(e.get("charge")) is int:'),
    ('reconciled-without-job-ok', 'elif k == "reconciled" and it is not None and it["job"] is not None and it["job"] == e.get("job") \\', 'elif k == "reconciled" and it is not None \\'),
    ('init-parent-unsynced', '        for d in reversed(created):', '        for d in []:'),
    ('fixed-not-held', '                held += self.fixed[n]["ns"]', '                pass'),
    ('fixed-credit-zero', 'credit = self.fixed[fixed]["ns"]', 'credit = 0'),
    ('fixed-reuse-ok', 'if fixed not in st["fixed_open"] or', 'if fixed not in self.fixed or'),
    ('fixed-size-unchecked', ' or res > self.fixed[fixed]["ns"]:', ':'),
    ('amendment-sha-unchecked', 'if group not in self.caps or not re.fullmatch(r"[0-9a-f]{40}", str(director_sha)):', 'if group not in self.caps:'),
    ('amendment-ignored', '                caps[e["group"]] = e["cap_ns"]', '                pass'),
    ('complete-without-policy', 'expected = set(self.toys.get(phase, {}).get(arm, []))', 'expected = set()'),
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
