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
    ('double-submit-replay-ok', 'elif k in ("submitted", "recovered") and it is not None and it["claimed"] and it["job"] is None \\', 'elif k in ("submitted", "recovered") and it is not None and it["claimed"] \\'),
    ('double-charge-replay-ok', '\n                    and it["charge"] is None and type(e.get("charge")) is int', '\n                    and type(e.get("charge")) is int'),
    ('dup-accept-replay-ok', 'elif k == "accepted" and (e.get("phase"), e.get("arm"), e.get("toy")) not in toys \\', 'elif k == "accepted" and True \\'),
    ('unknown-kind-ok', '                raise Refusal(f"an invalid ledger transition ({k!r})")', '                pass'),
    ('unrecorded-allowed', '            if unrecorded:\n', '            if False:\n'),
    ('fixed-held-in-every-group', '            if group is None or self.fixed[n]["group"] == group:', '            if True:'),
    ('ceiling-unchecked', '        return tot["spent_ns"] + tot["held_ns"] + res - credit <= self.ceiling \\\n            and', '        return True \\\n            and'),
    ('cap-unchecked', '            and gt["spent_ns"] + gt["held_ns"] + res - credit <= st["caps"][group]', '            and True'),
    ('held-not-counted', '                held += it["reservation"]', '                pass'),
    ('group-filter-off', '            if group is not None and self.groups[it["phase"]] != group:', '            if False:'),
    ('phase-unvalidated', '        if not PHASE.fullmatch(phase) or phase not in self.groups:\n            raise Refusal(f"unknown phase', '        if not PHASE.fullmatch(phase):\n            raise Refusal(f"unknown phase'),
    ('job-nonnumeric-ok', '    if not JOBID.fullmatch(str(job)):\n        raise Refusal("a job ID is numeric")', '    if False:\n        raise Refusal("a job ID is numeric")'),
    ('double-submit-ok', '                raise Refusal("the intent already has another job ID")', '                pass'),
    ('job-reuse-ok', '            if any(x["job"] == job for x in st["intents"].values()):', '            if False:'),
    ('whole-minute-unchecked', '        if it["time_limit_s"] % 60:', '        if False:'),
    ('no-requeue-dropped', '"--no-requeue", *extra]', '*extra]'),
    ('time-not-hhmmss', 'f"--time={hhmmss(it[\'time_limit_s\'])}"', 'f"--time={it[\'time_limit_s\'] // 60}"'),
    ('jobid-suffix-rejected', 'm = re.fullmatch(r"([0-9]+)(;\\S+)?", r.stdout.decode', 'm = re.fullmatch(r"([0-9]+)", r.stdout.decode'),
    ('sbatch-rc-ignored', 'ok = r.returncode == 0 and m', 'ok = m'),
    ('timelimit-unchecked', '        if slurm_seconds(fields.get("TimeLimit", "")) != it["time_limit_s"]:', '        if False:'),
    ('jobname-unchecked', '        if fields.get("JobName") != job_name:', '        if False:'),
    ('qos-unchecked', '        if not re.fullmatch(qos_pattern, fields.get("QOS", "")):', '        if False:'),
    ('no-scancel', '                cancelled = subprocess.run([scancel, job]', '                cancelled = (lambda *a, **k: subprocess.CompletedProcess(a, 0))([scancel, job]'),
    ('no-stop-on-sbatch-failure', 'self._append({"kind": "stop", "intent": intent, "reason": "sbatch returned no job ID; held"})', 'pass'),
    ('no-stop-on-mismatch', 'self._append({"kind": "stop", "intent": intent, "job": job,', 'None and self._append({"kind": "stop", "intent": intent, "job": job,'),
    ('lost-id-phase-ignored', '                    cands = by_name.get((it["phase"], iid), set())', '                    cands = set().union(set(), *[v for (p, i), v in by_name.items() if i == iid])'),
    ('ambiguous-matched', 'if it["claimed"] and len(cands) == 1 and next(iter(cands)) not in used:', 'if it["claimed"] and len(cands) >= 1 and next(iter(cands)) not in used:'),
    ('used-job-matched', ' and next(iter(cands)) not in used:', ':'),
    ('step-rows-matched', '                if not JOBID.fullmatch(str(r.get("JobID", ""))):\n                    continue', '                if False:\n                    continue'),
    ('conflicting-rows-ok', '                    if len(sigs) != 1:', '                    if len(sigs) < 1:'),
    ('running-charged', '    if state not in TERMINAL or not', '    if state == "" or not'),
    ('negative-ok', 'not (UINT.fullmatch(nn) and UINT.fullmatch(el)) or int(nn) < 1', 'not UINT.fullmatch(nn) or int(nn) < 1'),
    ('nnodes-zero-ok', 'UINT.fullmatch(el)) or int(nn) < 1:', 'UINT.fullmatch(el)) or int(nn) < 0:'),
    ('recorded-name-unchecked', ' or row.get("JobName") != f"covfix_{it[\'phase\']}_{intent}":', ':'),
    ('charge-twice', '                if it["charge"] is None:\n                    rs = by_job', '                if True:\n                    rs = by_job'),
    ('charge-nodes-ignored', 'charge = int(nn) * int(el)', 'charge = int(el)'),
    ('unexpected-toy-ok', '        if toy not in self.toys.get(phase, {}).get(arm, []):', '        if False:'),
    ('bad-sha-ok', '        if not _hex(HEX64, sha256):\n', '        if False:\n'),
    ('accept-job-unchecked', '            if not any(it["job"] == job and it["phase"] == phase and it["verified"] for it in st["intents"].values()):', '            if False:'),
    ('duplicate-toy-ok', '            if (phase, arm, toy) in st["toys"]:', '            if False:'),
    ('lock-noop', '            fcntl.flock(fh, fcntl.LOCK_EX)\n', ''),
    ('claim-skipped', 'self._append({"kind": "claimed", "intent": intent})', 'pass'),
    ('claim-unchecked', 'if it["claimed"] or it["job"] is not None or it["stop"] is not None:', 'if it["job"] is not None:'),
    ('extra-unrestricted', 'bad = [x for x in extra if not EXTRA_OK.fullmatch(x)]', 'bad = []'),
    ('numnodes-unchecked', '        if fields.get("NumNodes") != str(it["nodes"]):', '        if False:'),
    ('requeue-unchecked', '        if fields.get("Requeue") != "0":', '        if False:'),
    ('zero-uncorroborated', '    return it["reservation"] if charge == 0 and not _released(row) else charge', '    return charge'),
    ('job-not-canonical', 'return str(int(str(job)))', 'return str(job)'),
    ('row-job-not-canonical', 'jid = canon_job(r["JobID"])', 'jid = str(r["JobID"])'),
    ('negative-replay-ok', '                    and e["charge"] == _charge(e.get("evidence"), it, e["intent"]):', '                    and (e["charge"] == _charge(e.get("evidence"), it, e["intent"]) or e["charge"] < 0):'),
    ('reconciled-without-job-ok', 'elif k == "reconciled" and it is not None and it["job"] is not None and it["job"] == e.get("job") \\', 'elif k == "reconciled" and it is not None \\'),
    ('init-parent-unsynced', '        for d in reversed(created):', '        for d in []:'),
    ('fixed-not-held', '                held += self.fixed[n]["ns"]', '                pass'),
    ('fixed-credit-zero', '                credit = self.fixed[fixed]["ns"]           # the line', '                credit = 0           # the line'),
    ('fixed-reuse-ok', 'if fixed not in st["fixed_open"] or', 'if fixed not in self.fixed or'),
    ('fixed-size-unchecked', ' or res > self.fixed[fixed]["ns"]:', ':'),
    ('amendment-sha-unchecked', 'if group not in self.caps or not _hex(HEX40, director_sha):', 'if group not in self.caps:'),
    ('amendment-ignored', '                caps[e["group"]] = e["cap_ns"]', '                pass'),
    ('complete-without-policy', 'expected = set(self.toys.get(phase, {}).get(arm, []))', 'expected = set()'),
    ('amend-below-held-ok', '            if cap < sum(self.totals(st, group).values()):', '            if False:'),
    ('replay-amend-below-held-ok', '                    and e["cap_ns"] >= sum(self.totals(st, e["group"]).values()):', '                    :'),
    ('replay-intent-gate-off', '                    and self._fits(st, e["phase"], e["reservation"], fx):', '                    :'),
    ('claim-gate-off', '            if not self._claim_fits(st, it["phase"]):\n                raise Refusal', '            if False:\n                raise Refusal'),
    ('claim-ceiling-off', '        return sum(self.totals(st).values()) <= self.ceiling \\\n            and', '        return True \\\n            and'),
    ('directive-unchecked', '                if not STRICT_DIRECTIVE.fullmatch(line) or not all(', '                if False and not all('),
    ('directive-bare-ok', 'STRICT_DIRECTIVE = re.compile(r"#SBATCH( \\S+)+")', 'STRICT_DIRECTIVE = re.compile(r"#SBATCH( \\S+)*")'),
    ('r5-directive-splitlines', '.split("\\n"):    # Slurm', '.splitlines():    # Slurm'),   # round 6: \\v, \\r ... split a line
    ('script-by-path', 'r = subprocess.run(argv, capture_output=True, input=body, env=env, timeout=300)', 'r = subprocess.run(argv + [script], capture_output=True, input=b"", env=env, timeout=300)'),
    ('env-not-scrubbed', 'env = {k: v for k, v in os.environ.items() if not k.startswith(SCRUB)}', 'env = dict(os.environ)'),
    ('env-slurm-kept', 'SCRUB = ("SBATCH_", "SLURM_")', 'SCRUB = ("SBATCH_",)'),
    ('array-unchecked', '        if "ArrayJobId" in fields or "ArrayTaskId" in fields:', '        if False:'),
    ('record-not-idempotent', '            if it["job"] == job:\n                return\n', ''),
    ('record-without-claim', '            if not it["claimed"]:\n                raise Refusal("the intent was never claimed")', '            if False:\n                pass'),
    ('scancel-rc-ignored', 'timeout=120).returncode == 0', 'timeout=120) is not None'),
    ('verified-not-recorded', '            self._append({"kind": "verified", "intent": intent, "job": job})', '            pass'),
    ('replay-verified-unchecked', '                    and any(x["job"] == e["job"] and x["phase"] == e["phase"] and x["verified"]', '                    and any(x["job"] == e["job"] and x["phase"] == e["phase"]'),
    ('replay-job-type-loose', '    return type(job) is str and JOBID.fullmatch(job) is not None and job == str(int(job))', '    return JOBID.fullmatch(str(job)) is not None and str(job) == str(int(job))'),
    ('replay-sha-unchecked', '                    and _hex(HEX64, e.get("sha256")) and _canon_str(e.get("job")) \\', '                    and _canon_str(e.get("job")) \\'),
    ('replay-unclaimed-submit-ok', 'elif k in ("submitted", "recovered") and it is not None and it["claimed"] and it["job"] is None \\', 'elif k in ("submitted", "recovered") and it is not None and it["job"] is None \\'),
    ('replay-zero-unevidenced', '    return it["reservation"] if charge == 0 and not _released(row) else charge', '    return charge if charge > 0 or _released(row) or True else charge'),
    ('release-start-unknown-ok', '        and str(ev.get("Start", "")) == "None" and str(ev.get("ElapsedRaw", "")) == "0"', '        and str(ev.get("Start", "")) in ("None", "Unknown") and str(ev.get("ElapsedRaw", "")) == "0"'),
    ('release-any-state', '    return isinstance(ev, dict) and sacct_state(str(ev.get("State", ""))) == "CANCELLED" \\', '    return isinstance(ev, dict) \\'),
    ('evidence-dropped', '"charge": charge,\n                                      "evidence": dict(rs[0])})', '"charge": charge})'),
    ('recover-unclaimed', 'if it["claimed"] and len(cands) == 1', 'if len(cands) == 1'),
    ('recovered-as-submitted', 'self._append({"kind": "recovered", "intent": iid', 'self._append({"kind": "submitted", "intent": iid'),
    ('accept-unverified-ok', 'if not any(it["job"] == job and it["phase"] == phase and it["verified"] for it', 'if not any(it["job"] == job and it["phase"] == phase for it'),
    ('script-unreadable-crashes', '        except OSError as e:\n            raise Refusal("the job script cannot be read") from e', '        except KeyError as e:\n            raise Refusal("the job script cannot be read") from e'),
    ('scontrol-launch-crashes', '        except (OSError, subprocess.SubprocessError):\n            fields = {}', '        except KeyError:\n            fields = {}'),
    ('scancel-launch-ok', '            except (OSError, subprocess.SubprocessError):\n                cancelled = False', '            except (OSError, subprocess.SubprocessError):\n                cancelled = True'),
    ('r4-directive-case-sensitive', 'DIRECTIVE_WORD = re.compile(r"sbatch|slurm", re.IGNORECASE)', 'DIRECTIVE_WORD = re.compile(r"SBATCH")'),
    ('r4-directive-loose-form', 'STRICT_DIRECTIVE = re.compile(r"#SBATCH( \\S+)+")', 'STRICT_DIRECTIVE = re.compile(r"\\s*#\\s*SBATCH(\\s*\\S+)+\\s*")'),
    ('r4-directive-comment-scope', '            if line.strip().startswith("#") and DIRECTIVE_WORD.search(line):', '            if line.startswith("#SBATCH") and DIRECTIVE_WORD.search(line):'),
    ('r4-flag-value-any', '=[A-Za-z0-9_.,:%/@+-]+"', '=\\S+"'),
    ('r4-hex-type-dropped', '    return type(v) is str and rx.fullmatch(v) is not None', '    return rx.fullmatch(str(v)) is not None'),
    ('r4-replay-sha-type-dropped', '_hex(HEX64, e.get("sha256"))', 'HEX64.fullmatch(str(e.get("sha256", "")))'),
    ('r4-replay-amend-sha-type-dropped', '_hex(HEX40, e.get("director_sha"))', 'HEX40.fullmatch(str(e.get("director_sha", "")))'),
    ('r4-live-amend-sha-type-dropped', 'if group not in self.caps or not _hex(HEX40, director_sha):', 'if group not in self.caps or not HEX40.fullmatch(str(director_sha)):'),
    ('r4-live-accept-sha-type-dropped', '        if not _hex(HEX64, sha256):\n', '        if not HEX64.fullmatch(str(sha256)):\n'),
    ('r4-replay-intent-while-unrecorded', '                    and all(x["job"] is not None for x in intents.values()) \\\n', ''),
    ('r4-replay-claim-unchecked', ' \\\n                    and self._claim_fits(st, it["phase"]):', ':'),
    ('r4-evidence-other-job', ' \\\n            or str(int(str(row["JobID"]))) != it["job"] or row.get("JobName")', ' \\\n            or row.get("JobName")'),
    ('r4-replay-charge-unchecked', '                    and e["charge"] == _charge(e.get("evidence"), it, e["intent"]):', '                    and (e["charge"] > 0 or _charge(e.get("evidence"), it, e["intent"]) == 0):'),
    ('r4-format-unchecked', 'es[0].get("format") != FORMAT:', 'False:'),
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
