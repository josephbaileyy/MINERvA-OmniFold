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
EXPECTED_TESTS = 30

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
    # --- coverage-5b-audit's A1 sites (#902 comment 6712619323), its anchors verbatim
    ("W01 copy not re-hashed", P, "                if h != sums[kind][str(r)]:\n                    raise Refusal", "                if False:\n                    raise Refusal", "test_a_bad_copy_is_refused"),
    ("W02 log-dry copy not verified", P, 'raise Refusal(f"log-dry copy of {f.name} differs")', "pass", "test_a_bad_log_dry_copy_is_refused"),
    ("W03 dry tasks judged against log-full", P, 'kind = "dry" if tid in dry_ids else "full"', 'kind = "full"', "test_a_dry_task_is_judged_against_log_dry"),
    ("W04 empty expect list read as all present", S, '[ "${#files[@]}" -gt 0 ] || all=0', "true", "test_a_task_whose_expect_fails_is_a_failure_not_a_teardown"),
    ("W05 not every task done-or-ended still DONE", S, '[ $((n_done + n_ran)) -eq "$n_q" ] ||', "true ||", "test_every_task_must_be_done_or_ended"),
    ("W06 xargs rc ignored", S, '[ -z "$failed" ] && [ "$rc" -eq 0 ] ||', '[ -z "$failed" ] ||', "test_xargs_rc_alone_stops_the_run"),
    ("W07 old log-dry DONE not required", P, 'for need in (old / "log-dry" / "DONE", ', "for need in (", "test_attempt_ones_dry_done_is_required"),
    ("W08 a1 plan file not required", S, ' || [ ! -f "$A1/nd-unfolding/rs1_a1_plan.py" ]', "", "test_the_a1_clone_must_hold_the_plan_module"),
    ("W09 mv failure ignored", S, 'mv "$f" "$T/" || { echo "could not move $f aside" > "$L/$id.failed"; exit 1; }', 'mv "$f" "$T/" || true', "test_a_failed_move_aside_is_a_failure_and_the_crashed_files_are_not_used"),
    ("W10 attempt-1 STOP in log-dry accepted", P, 'if (old / "log-dry" / "FAILED").exists() or (old / "log-dry" / "STOP").exists():', 'if (old / "log-dry" / "FAILED").exists():', "test_a_dry_run_that_left_stop_is_refused"),
    ("W11 a file missing from sums still done", P, "ok = ended and all(str(r) in sums[kind] and (old / r).is_file() and sha256_path(old / r) == sums[kind][str(r)]", "ok = ended and all((old / r).is_file() and sha256_path(old / r) == sums[kind].get(str(r), sha256_path(old / r))", "test_a_file_missing_from_sha256sums_makes_a_task_todo"),
    # --- A1 connect 1's stop (Python 3.6 on the cluster; the director's rulings, items 1-3)
    ("REQ verify above the source", S, 'source "$D/setup_salloc_env.sh" > "$ENVLOG" 2>&1\npython3 "$PLANPY" verify --root "$OUT" > /dev/null \\\n    || { echo "[rs1-a1] refusing: a staged file no longer verifies" >&2; exit 2; }', 'python3 "$PLANPY" verify --root "$OUT" > /dev/null \\\n    || { echo "[rs1-a1] refusing: a staged file no longer verifies" >&2; exit 2; }\nsource "$D/setup_salloc_env.sh" > "$ENVLOG" 2>&1', "test_every_planner_call_runs_under_the_sourced_environment"),
    ("REQ the future import back", P, "import argparse\nimport hashlib", "from __future__ import annotations\n\nimport argparse\nimport hashlib", "test_the_planner_is_python36_compatible"),
    ("REQ a PEP 585 annotation back", P, "def verify(root: Path) -> List[str]:", "def verify(root: Path) -> list[str]:", "test_the_planner_is_python36_compatible"),
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
