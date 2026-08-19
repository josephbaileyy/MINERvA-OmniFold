#!/usr/bin/env python3
"""ISSUE-54 regression: `cstat_data_only_readback.assert_member_logs` must fire on what the data-only
producers ACTUALLY emit, and must not fire on a healthy run. The defect ran in BOTH directions out of one
constant family, so every test here comes in a pair.

  FALSE ALARM (loud):  :425/:429 wanted `[gate5-train] index=...` / `[gate5-train] DONE ...`, a token the
                       data-only launcher NEVER writes -- so a genuinely successful member scored 0.
  FALSE PASS (silent): FATAL_LOG_TOKENS omitted every token a real failure emits. `raise SystemExit(msg)`
                       prints ONLY msg -- no traceback, no literal "SystemExit:" -- so the launcher's 12
                       `die` sites and the shared driver's 53 guard rejections tripped NOTHING.

WHY THE FIXTURES ARE BUILT THE WAY THEY ARE (BEN-476): a fixture derived from the rule under test cannot
disagree with it. So the launcher's start/DONE/FAIL lines are produced by EXECUTING the launcher's own
`echo`/`die` source lines under bash, and the driver's guard message is produced by RAISING a SystemExit
string literal lifted out of the driver and capturing real stderr from a real interpreter. Nothing in the
fatal/needle fixtures is copied from `cstat_data_only_readback.py`.

Login-safe: no ROOT, no TensorFlow, no cluster, no Slurm. Run: python3 test_cstat_data_only_readback_log_tokens.py
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cstat_data_only_readback as R  # noqa: E402

HERE = Path(__file__).resolve().parent
LAUNCHER = HERE / "sbatch_gate5_data_only_train_array.sh"
REPLICA_LAUNCHER = HERE / "sbatch_gate5_replica_train_array.sh"
DRIVER = HERE / "train_fullevent_replica.py"

IDX, JOB = 7, "57235710"
SEED = 50000 + IDX          # launcher :48  SEED=$((50000 + INDEX))
WHERE = "test_issue54"

# The token list as it stood at the defect, for the mutation runs. Quoted here ONLY so the power tests can
# demonstrate what it failed to match; it is not an input to any correctness assertion.
OLD_FATAL_TOKENS = ["Traceback (most recent call last)", "[gate5-train][FAIL]", "SystemExit:"]
OLD_LAUNCHER_PREFIX_IN_READBACK = "[gate5-train]"

P, F = 0, []


def ok(name, cond, detail=""):
    global P
    if cond:
        P += 1
        print(f"  PASS  {name}")
    else:
        F.append(f"{name}: {detail}")
        print(f"  FAIL  {name}: {detail}")


# ----------------------------------------------------------------------------------------------------
# PRODUCER-DERIVED FIXTURES
# ----------------------------------------------------------------------------------------------------
def _launcher_src_line(lineno):
    return LAUNCHER.read_text().splitlines()[lineno - 1]


def launcher_echo(lineno):
    """Run the launcher's own `echo` at `lineno` under bash and return its stdout verbatim."""
    line = _launcher_src_line(lineno)
    assert line.lstrip().startswith("echo "), f"{lineno} is not an echo: {line!r}"
    script = (
        f'INDEX={IDX}\nSEED={SEED}\nSLURM_ARRAY_JOB_ID={JOB}\n'
        'EXPECTED_HEAD=377c713d0000000000000000000000000000beef\n'
        f'{line}\n'
    )
    r = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
    assert r.returncode == 0, f"launcher echo {lineno} failed rc={r.returncode}: {r.stderr!r}"
    return r.stdout


def launcher_die(msg="loader hash drift"):
    """Run the launcher's own die() at :57 and return the STDERR it writes."""
    line = _launcher_src_line(57)
    assert line.startswith("die()"), f":57 is not die(): {line!r}"
    r = subprocess.run(["bash", "-c", f'{line}\ndie "{msg}"\n'], capture_output=True, text=True)
    assert r.returncode != 0, "die() must exit non-zero"
    assert r.stdout == "", f"die() must write to stderr, not stdout: {r.stdout!r}"
    return r.stderr


def driver_guard_stderr(which=0):
    """Lift a real `SystemExit("[gate5-...] ...")` literal out of the driver, raise it in a child
    interpreter, and return the stderr a real failure actually produces."""
    lits = re.findall(r'SystemExit\((?:f?)"(\[gate5-[a-z-]+\][^"\\]*)"\)', DRIVER.read_text())
    assert lits, "no single-line SystemExit literal found in the driver"
    msg = lits[which]
    r = subprocess.run([sys.executable, "-c", f'raise SystemExit({msg!r})'],
                       capture_output=True, text=True)
    assert r.returncode == 1, f"expected rc=1, got {r.returncode}"
    return msg, r.stdout, r.stderr


def write_logs(tmp, out_text, err_text):
    d = Path(tmp)
    (d / f"train_{JOB}_{IDX}.out").write_text(out_text)
    (d / f"train_{JOB}_{IDX}.err").write_text(err_text)
    return d


def healthy_stdout():
    """A stdout containing all five things a successful member emits, each from its own producer:
    launcher :111 parity, :113 start, :124 DONE; nominal :350's config-gate JSON; the driver's PASS
    receipt (:696/:756) and the LR-anneal proof line."""
    return "".join([
        launcher_echo(111),
        launcher_echo(113),
        # train_fullevent_nominal.py:350 -- json.dumps({"config_gate": "PASS", ...})
        json.dumps({"config_gate": "PASS", "tag": "data-only-v1"}) + "\n",
        R.optimizer_proof_line() + "\n",
        # train_fullevent_replica.py:696 -- the PASS receipt block, same serializer
        json.dumps({"status": "PASS", "replica_index": IDX}) + "\n",
        launcher_echo(124),
    ])


class old_fatal_config:
    """Restore the pre-fix fatal detection COMPLETELY: the three-token both-streams list AND an empty
    stderr-only list, which did not exist. Reverting one of the two would leave the other live and the
    mutation would silently not be a mutation."""

    def __enter__(self):
        self.saved = (R.FATAL_LOG_TOKENS, R.FATAL_STDERR_TOKENS)
        R.FATAL_LOG_TOKENS, R.FATAL_STDERR_TOKENS = OLD_FATAL_TOKENS, []
        return self

    def __exit__(self, *exc):
        R.FATAL_LOG_TOKENS, R.FATAL_STDERR_TOKENS = self.saved
        return False


def call(logs_dir, prefix=None):
    """Invoke the real predicate. Returns (raised, message)."""
    try:
        res = R.assert_member_logs(logs_dir, array_job_id=JOB, replica_index=IDX,
                                   bootstrap_seed=SEED, where=WHERE,
                                   launcher_log_prefix=prefix)
        return False, res
    except SystemExit as e:
        return True, str(e)


# ----------------------------------------------------------------------------------------------------
def main():
    print("== 0. the measurement the whole repair rests on ==")
    msg, so, se = driver_guard_stderr()
    ok("systemexit_prints_bare_message", se.strip() == msg, f"stderr={se!r} msg={msg!r}")
    ok("systemexit_emits_no_traceback", "Traceback" not in se + so, f"stderr={se!r}")
    ok("systemexit_emits_no_SystemExit_token", "SystemExit:" not in se + so, f"stderr={se!r}")
    ok("so_only_one_old_token_could_ever_match",
       [t for t in OLD_FATAL_TOKENS if t in se or t in so] == [],
       "an old token matched a real driver guard, contradicting the premise")

    print("== 1. producers really do disagree, and the constants name them correctly ==")
    lsrc, dsrc = LAUNCHER.read_text(), DRIVER.read_text()
    ok("launcher_emits_declared_prefix", R.LAUNCHER_LOG_PREFIX in lsrc)
    ok("launcher_never_emits_old_prefix", OLD_LAUNCHER_PREFIX_IN_READBACK not in lsrc,
       "the launcher does emit [gate5-train]; ISSUE-54's premise would be wrong")
    ok("driver_emits_declared_fatal_prefixes",
       all(p in dsrc for p in R.DRIVER_FATAL_PREFIXES))
    # SOUNDNESS CONDITION for using bare driver prefixes as fatal tokens: the launcher must not print them
    # on its healthy path, or the fatal arm becomes a false alarm. This is the g1 caveat, made executable.
    ok("healthy_stdout_carries_no_driver_prefix",
       not any(p in healthy_stdout() for p in R.DRIVER_FATAL_PREFIXES),
       "a driver fatal prefix appears in healthy output -> the fatal arm would false-alarm")

    print("== 2. FALSE ALARM direction: a healthy member must PASS ==")
    with tempfile.TemporaryDirectory() as tmp:
        d = write_logs(tmp, healthy_stdout(), "")
        raised, info = call(d)
        ok("healthy_run_does_not_raise", not raised, f"raised: {info}")
        ok("healthy_run_reports_checked_8", (not raised) and info.get("checked") == 8, f"{info}")

        # POWER / MUTATION: put the pre-fix prefix back -- now THROUGH THE PARAMETER, which is also a
        # test that the parameter is actually consulted rather than shadowed by the module default.
        raised_old, msg_old = call(d, prefix=OLD_LAUNCHER_PREFIX_IN_READBACK)
        ok("MUTANT_old_prefix_fails_a_healthy_run", raised_old and "appears 0 times" in msg_old,
           f"raised={raised_old} msg={msg_old}")
        ok("MUTANT_old_prefix_blames_the_start_line", raised_old and "log_start_line" in msg_old,
           f"msg={msg_old}")

        # Tolerance spot-check: the producer's extra head=/product= fields and the DONE timestamp are
        # already tolerated by substring counting -- confirmed against the real echoes, not asserted.
        so_text = healthy_stdout()
        ok("start_line_really_carries_extra_fields",
           "head=" in so_text and "product=" in so_text, so_text)
        ok("done_line_really_carries_a_trailing_timestamp",
           re.search(r"DONE index=%d seed=%d \d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ" % (IDX, SEED), so_text)
           is not None, so_text)

    print("== 3. FALSE PASS direction A: the launcher's die() must fire ==")
    with tempfile.TemporaryDirectory() as tmp:
        d = write_logs(tmp, healthy_stdout(), launcher_die())
        raised, msg = call(d)
        ok("launcher_die_raises", raised, f"info={msg}")
        ok("launcher_die_names_fatal_tokens", raised and "fatal tokens present" in msg, msg)

        with old_fatal_config():
            raised_old, msg_old = call(d)
        ok("MUTANT_old_tokens_MISS_launcher_die", not raised_old,
           f"old tokens caught it; the silent half would not have been silent: {msg_old}")

    print("== 4. FALSE PASS direction B: a driver guard rejection must fire ==")
    # Isolating the fatal-token arm: all five needles present, so the ONLY thing that can raise is the
    # token scan. Under `set -eo pipefail` (launcher :15) a real driver failure also loses the DONE line,
    # which case is covered separately in section 5 -- but that would mask this arm.
    for i in (0, 1):
        gmsg, _, gse = driver_guard_stderr(i)
        with tempfile.TemporaryDirectory() as tmp:
            d = write_logs(tmp, healthy_stdout(), gse)
            raised, msg = call(d)
            ok(f"driver_guard[{i}]_raises", raised, f"guard={gmsg!r} info={msg}")
            ok(f"driver_guard[{i}]_names_fatal_tokens", raised and "fatal tokens present" in msg, msg)

            with old_fatal_config():
                raised_old, msg_old = call(d)
            ok(f"MUTANT_old_tokens_MISS_driver_guard[{i}]", not raised_old,
               f"old tokens caught {gmsg!r}: {msg_old}")

    print("== 5. the second, independent detector: set -e loses the DONE line ==")
    with tempfile.TemporaryDirectory() as tmp:
        # What the real filesystem holds after a driver guard rejection: parity + start line on stdout,
        # the guard message on stderr, and NO DONE line because :124 never runs.
        _, _, gse = driver_guard_stderr()
        partial = launcher_echo(111) + launcher_echo(113)
        d = write_logs(tmp, partial, gse)
        raised, msg = call(d)
        ok("aborted_member_raises", raised, f"info={msg}")
        # It raises at the FIRST failing check, which is an exact_one needle, not the token scan.
        ok("aborted_member_reports_a_missing_needle", raised and "appears 0 times" in msg, msg)

        with old_fatal_config():
            raised_old, _ = call(d)
        ok("aborted_member_caught_even_with_old_tokens", raised_old,
           "with the prefix fixed, log_done alone catches an aborted member")

    print("== 6. the != 1 double-run detector is PRESERVED ==")
    with tempfile.TemporaryDirectory() as tmp:
        d = write_logs(tmp, healthy_stdout() + launcher_echo(124), "")
        raised, msg = call(d)
        ok("two_done_lines_raise", raised and "appears 2 times" in msg, f"{raised} {msg}")
        ok("double_run_message_kept", raised and "ran twice" in msg, msg)

    print("== 7. g1 benefit, without changing g1's producers ==")
    # The repair's fatal arm is prefix-independent for the FAIL marker, so g1's own die token still
    # matches. Stated as a fact about this list, not as a change to any g1 script.
    ok("g1_fail_token_still_matched",
       any(t in "[gate5-train][FAIL] code HEAD drift" for t in R.FATAL_LOG_TOKENS))
    ok("data_only_fail_token_matched",
       any(t in launcher_die() for t in R.FATAL_LOG_TOKENS))

    print("== 7b. the stderr-only arm is a NARROWING, so test that it does NOT fire ==")
    # Same bytes, other stream. In STDERR this is a guard rejection; in STDOUT the identical prefix is
    # what a healthy replica-family launcher prints. If this fired, section 8 could not pass.
    gmsg, _, gse = driver_guard_stderr()
    with tempfile.TemporaryDirectory() as tmp:
        d = write_logs(tmp, healthy_stdout() + gse, "")
        raised, msg = call(d)
        ok("driver_prefix_in_STDOUT_does_not_trip_the_stderr_arm",
           not (raised and "[gate5-train]" in str(msg)), f"raised={raised} {msg}")
    with tempfile.TemporaryDirectory() as tmp:
        d = write_logs(tmp, healthy_stdout(), gse)
        raised, msg = call(d)
        ok("the_same_bytes_in_STDERR_DO_trip_it", raised and "[gate5-train]" in msg, f"{raised} {msg}")

    print("== 8. lane C's ruling: ONE reader, BOTH families, via the parameter ==")
    # The REPLICA launcher is the sole producer of the "[gate5-train]" needle form (:62/:72). Its lines are
    # executed here the same way, so this fixture is the replica family's real output -- not a re-spelling
    # of the data-only one.
    rsrc = REPLICA_LAUNCHER.read_text().splitlines()
    r_start, r_done = rsrc[61], rsrc[71]
    ok("replica_launcher_lines_are_the_echoes",
       r_start.lstrip().startswith("echo ") and r_done.lstrip().startswith("echo "),
       f"{r_start!r} / {r_done!r}")
    script = (f'INDEX={IDX}\nSEED={SEED}\nSLURM_ARRAY_JOB_ID={JOB}\n'
              'EXPECTED_HEAD=377c713d0000000000000000000000000000beef\n'
              f'{r_start}\n{r_done}\n')
    rp = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
    ok("replica_launcher_echoes_run", rp.returncode == 0, rp.stderr)
    ok("replica_prefix_really_differs", "[gate5-train]" in rp.stdout
       and R.LAUNCHER_LOG_PREFIX not in rp.stdout, rp.stdout)
    r_out = (rp.stdout.splitlines()[0] + "\n"
             + json.dumps({"config_gate": "PASS", "tag": "replica"}) + "\n"
             + R.optimizer_proof_line() + "\n"
             + json.dumps({"status": "PASS", "replica_index": IDX}) + "\n"
             + rp.stdout.splitlines()[1] + "\n")
    with tempfile.TemporaryDirectory() as tmp:
        d = write_logs(tmp, r_out, "")
        raised, info = call(d, prefix="[gate5-train]")
        ok("replica_family_log_passes_with_its_own_prefix", not raised, f"raised: {info}")
        # And the default must NOT accept a replica log -- otherwise the parameter is decorative.
        raised_def, msg_def = call(d)
        ok("replica_log_REJECTED_under_the_data_only_default", raised_def
           and "appears 0 times" in msg_def, f"raised={raised_def} {msg_def}")

    print(f"\n{P} passed, {len(F)} failed")
    for f in F:
        print(f"  - {f}")
    return 1 if F else 0


if __name__ == "__main__":
    sys.exit(main())
