"""Mutation check of addendum A1's tests (RS1-BINDING-2 addendum A1; the director's rulings: REQUIRED mutants for the
teardown guard's three directions, plus one per staging rule and refusal).

Each mutation plants one defect in a temporary copy of rs1_a1_plan.py or sbatch_rs1_a1.sh and runs the suite with
that copy first on sys.path and named through RS1_A1_PLAN / RS1_A1_SBATCH. The mutation must make its NAMED test
fail. Exit 0 only if every mutation is killed and the unmutated suite runs all EXPECTED_TESTS and passes.

    python3 -B nd-unfolding/tests/rs1_a1_mutation.py
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ND = Path(__file__).resolve().parents[1]
TEST = ND / "tests" / "test_rs1_a1.py"
P, S = "rs1_a1_plan.py", "sbatch_rs1_a1.sh"
EXPECTED_TESTS = 17

MUTATIONS = [
    # --- REQUIRED: the teardown guard
    ("REQ teardown crash read as a failure", S, 'if [ "$all" -ne 1 ]; then echo "rc=$rc before',
     'if true; then echo "rc=$rc before', "test_a_teardown_crash_is_recomputed_once_and_compared"),
    ("REQ pre-write failure read as a teardown", S, 'for f in "${files[@]}"; do [ -e "$f" ] || all=0; done', "true",
     "test_a_failure_before_writing_is_a_failure_and_the_queue_continues"),
    ("REQ a second crash accepted", S, 'if [ "$rc" -ne 0 ]; then echo "rc=$rc on the re-run',
     'if false; then echo "rc=$rc on the re-run', "test_a_second_crash_is_a_failure"),
    ("REQ xargs aborts on a failure", S, 'before every product was written" > "$L/$id.failed"; exit 1; fi',
     'before every product was written" > "$L/$id.failed"; exit 255; fi',
     "test_a_failure_before_writing_is_a_failure_and_the_queue_continues"),
    ("REQ crashed files kept, not recomputed", S, 'for f in "${files[@]}"; do mv "$f" "$T/" ||',
     'for f in; do mv "$f" "$T/" ||', "test_a_teardown_crash_is_recomputed_once_and_compared"),
    # --- the wrapper
    ("done tasks re-run", S, '!/^#/ && $2 == "todo" {print $1}', '!/^#/ {print $1}',
     "test_only_todo_tasks_run_and_done_is_written"),
    ("a failed task still writes DONE", S, '[ -z "$failed" ] && [ "$rc" -eq 0 ] || {', "true || {",
     "test_a_failure_before_writing_is_a_failure_and_the_queue_continues"),
    ("deploy pin unchecked", S, 'if [ "$head_sha" != "$PIN" ] || [ "$dirty" -ne 0 ]; then', "if false; then",
     "test_refusals_before_anything_is_written"),
    ("a1 tools unchecked", S, 'if [ "$a1_sha" != "$A1PIN" ] || [ "$a1_dirty" -ne 0 ] ||', "if false ||",
     "test_refusals_before_anything_is_written"),
    ("dry pin unchecked", S, '[ "$dry_pin" = "$PIN" ] ||', "true ||", "test_refusals_before_anything_is_written"),
    ("plan/queue count unchecked", S, '[ "$n_q" -eq "$n_p" ] ||', "true ||", "test_refusals_before_anything_is_written"),
    ("staged files unverified", S, '    || { echo "[rs1-a1] refusing: a staged file no longer verifies" >&2; exit 2; }',
     "    || true", "test_refusals_before_anything_is_written"),
    ("existing log reused", S, '[ ! -e "$L" ] || {', "true || {", "test_refusals_before_anything_is_written"),
    ("environment unchecked", S, '|| { echo "[rs1-a1] refusing: the environment lacks lightgbm/scipy" >&2; exit 7; }',
     "|| true", "test_an_environment_without_lightgbm_is_refused"),
    # --- staging and the plan
    ("done without the digest", P, 'and sha256_path(old / r) == sums[kind][str(r)]', "",
     "test_an_ended_task_whose_file_does_not_verify_is_todo_and_not_copied"),
    ("done without having ended", P, "ok = ended and all(", "ok = all(",
     "test_an_unended_tasks_files_go_to_runs_attempt1_never_to_runs"),
    ("sidecars not expected", P, 'files += [p, p.with_name(p.name[:-4] + ".trace.json.gz")]', "files += [p]",
     "test_each_pair_names_its_product_and_sidecar"),
    ("todo files copied into runs", P, 'copy_noatime(old / r, new / "runs-attempt1" / tid / r.name)',
     "copy_noatime(old / r, new / r)", "test_an_unended_tasks_files_go_to_runs_attempt1_never_to_runs"),
    ("staging twice", P, '            raise Refusal(f"{new / x} exists: staging is once only")', "            pass",
     "test_log_dry_is_copied_verbatim_and_staging_is_once_only"),
    ("a failed dry run staged", P, '        raise Refusal("attempt 1\'s dry run left FAILED or STOP")', "        pass",
     "test_a_dry_run_that_left_failed_is_refused"),
    ("verify passes a changed copy", P, "        if not p.is_file() or sha256_path(p) != h:", "        if not p.is_file():",
     "test_verify_finds_a_changed_copy"),
    ("two --tag accepted", P, "        if rest.count(name) != 1:", "        if rest.count(name) < 1:",
     "test_a_line_without_one_pairs_or_tag_is_refused"),
]


def run_suite(first: Path | None, plan: Path | None, script: Path | None) -> tuple[int, str]:
    boot = ("import sys, runpy; sys.argv = ['t']; " + (f"sys.path.insert(0, {str(first)!r}); " if first else "")
            + f"runpy.run_path({str(TEST)!r}, run_name='__main__')")
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    for k, v in (("RS1_A1_PLAN", plan), ("RS1_A1_SBATCH", script)):
        env.pop(k, None)
        if v is not None:
            env[k] = str(v)
    p = subprocess.run([sys.executable, "-B", "-c", boot], capture_output=True, text=True, cwd=str(ND.parent), env=env)
    return p.returncode, p.stdout + p.stderr


def failing(out: str) -> set[str]:
    return set(re.findall(r"^(?:FAIL|ERROR): (\w+)", out, re.M))


def main() -> int:
    rc, out = run_suite(None, None, None)
    ran = re.search(r"^Ran (\d+) tests?", out, re.M)
    if rc != 0 or not ran or int(ran.group(1)) != EXPECTED_TESTS:
        print(f"UNMUTATED SUITE: rc {rc}, ran {ran.group(1) if ran else '?'} of {EXPECTED_TESTS} expected tests\n" + out[-2000:])
        return 1
    print(f"UNMUTATED SUITE: {EXPECTED_TESTS} tests, rc 0")
    ok = True
    for label, fname, old, new, test in MUTATIONS:
        src = (ND / fname).read_text()
        if src.count(old) != 1:
            print(f"MUTATION NOT APPLIED  {label}: anchor occurs {src.count(old)} times")
            ok = False
            continue
        with tempfile.TemporaryDirectory() as d:
            for f in (P, S):
                shutil.copy(ND / f, Path(d) / f)
            (Path(d) / fname).write_text(src.replace(old, new))
            rc, out = run_suite(Path(d), Path(d) / P, Path(d) / S)
        fails = failing(out)
        killed = test in fails
        ok &= killed
        print(f"{'KILLED' if killed else 'SURVIVED':8s}  {label:42s} by {test}" + ("" if killed else f"  (failing: {sorted(fails)})"),
              flush=True)
    print("MUTATION CHECK ::", "PASS" if ok else "FAIL", f"({len(MUTATIONS)} mutations)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
