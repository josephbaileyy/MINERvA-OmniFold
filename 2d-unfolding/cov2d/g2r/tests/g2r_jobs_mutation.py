"""Mutation check of COV2D-G2R J1's tests (test_g2r_jobs.py): each mutation plants one defect in one job source (the
tables, checks, order, gate and comparison in g2r_jobs.py, or one of the four shell scripts), runs the NAMED test,
which must fail, and restores the file's exact bytes. Exit 0 only if every mutation is killed, every anchor occurs
once, the unmutated suite runs all EXPECTED tests and passes, and every source is byte-identical to HEAD at the end.

    python3 -B 2d-unfolding/cov2d/g2r/tests/g2r_jobs_mutation.py

It mutates in place, so it refuses unless the sources are clean against HEAD (run it in a clean checkout).
"""
from __future__ import annotations

import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
J = REPO / "2d-unfolding/cov2d/g2r/jobs"
PY, ENV, JOB, ENVT, PREP, SUB = (J / "g2r_jobs.py", J / "g2r_env.sh", J / "g2r_job.sbatch", J / "g2r_envtest.sbatch",
                                 J / "g2r_prepare.sbatch", J / "g2r_submit.sh")
TEST = REPO / "2d-unfolding/cov2d/g2r/tests/test_g2r_jobs.py"
EXPECTED = 55

MUTATIONS = [
    # --- the tables
    ("the off reruns carry the map", PY,
     '"cpus": int(r[3]), "args": r[5],\n                    "est_s": int(r[6]), "point": "data", "role": "off"',
     '"cpus": int(r[3]), "args": r[5] + " --miss-map $MAP",\n                    "est_s": int(r[6]), "point": "data", "role": "off"',
     "Tables.test_off_reruns_are_part_bs_rows_exactly_at_the_end_of_d_ud_2"),
    ("the tune rows without the map", PY, '"args": " ".join(r["args"] + MAP_ARGS)', '"args": " ".join(r["args"])',
     "Tables.test_tune_rows_are_cov2ds_universe_rows_plus_the_map"),
    ("the data rows without the map", PY, '"args": r[5] + " " + " ".join(MAP_ARGS)', '"args": r[5]',
     "Tables.test_data_rows_are_part_bs_j2_rows_plus_the_map"),
    ("the envtest priced at part B's per-run estimate", PY, "ENVTEST_EST_S = 2738 ", "ENVTEST_EST_S = 1150 ",
     "Tables.test_limits_and_the_price"),
    ("part B's table not read at its digest", PY,
     "    if hashlib.sha256(data).hexdigest() != PARTB_RUNS[1]:\n", "    if False:\n",
     "Tables.test_part_bs_table_is_read_at_its_digest_and_must_be_the_bank"),
    # --- the check
    ("the map not checked against the committed record", PY,
     "            if got != map_sha:\n", "            if False:\n", "Check.test_the_map_must_be_the_committed_one"),
    ("G8 not compared", PY, "                if got != want[name]:\n", "                if False:\n",
     "Check.test_the_realization_g8"),
    ("$UNI's stat not checked", PY, "        if problem:\n", "        if False:\n", "Check.test_uni_and_pins"),
    # --- the order
    ("each job not once", PY, "    if job in submitted:\n", "    if False:\n", "Order.test_each_job_once_and_records_must_pass"),
    ("the prepare without the envtest's PASS", PY,
     '    if job != "envtest" and (env_rec or {}).get("verdict") != "PASS":\n', "    if False:\n",
     "Order.test_the_sequence"),
    ("the bulk before D_Ua's first --miss-map run", PY, "    if job not in FIRST and not first_run_done:\n",
     "    if False:\n", "Order.test_the_sequence"),
    ("the first run counted whatever its rc", PY, 'if len(f) == 4 and f[3] == "0" and', "if len(f) == 4 and",
     "Order.test_first_run_done"),
    # --- the gate
    ("the gate prices every name", PY, "        if not name.startswith(PREFIX):\n            continue\n",
     "        if False:\n            continue\n", "Gate.test_unknown_names_refuse_and_others_are_ignored"),
    ("the sacct lag ignored", PY, "    for i in lagging:\n        held +=", "    for i in []:\n        held +=",
     "Gate.test_spent_held_lag_and_the_cap"),
    ("the cap opened", PY, "CAP_NODE_H = 110.0 ", "CAP_NODE_H = 1100.0 ", "Gate.test_the_cap_refuses"),
    ("the projection never a STOP", PY,
     '    if want not in ("envtest", "prepare") and projection > CAP_NODE_H:\n', "    if False:\n",
     "Gate.test_the_projection_is_a_stop_for_unfold_jobs_only"),
    # --- the comparison
    ("the envtest's tolerance back to bitwise (the audit's B1)", PY, "ENVTEST_TOL = 1e-8 ", "ENVTEST_TOL = 0.0 ",
     "EnvTest.test_the_measured_rerun_noise_passes"),
    ("the envtest's tolerance opened", PY, "ENVTEST_TOL = 1e-8 ", "ENVTEST_TOL = 1e-1 ",
     "EnvTest.test_each_difference_is_invalid"),
    ("the envtest's tolerance loosened to 3e-8 (the director's condition)", PY, "ENVTEST_TOL = 1e-8 ",
     "ENVTEST_TOL = 3e-8 ", "EnvTest.test_the_tolerance_boundary"),
    ("the envtest's tolerance tightened to 0.4e-8", PY, "ENVTEST_TOL = 1e-8 ", "ENVTEST_TOL = 0.4e-8 ",
     "EnvTest.test_the_tolerance_boundary"),
    ("the histograms' errors not compared", PY, "hist_rel[k] = max(rel_diff(a2, a1), rel_diff(e2, e1))",
     "hist_rel[k] = rel_diff(a2, a1)", "EnvTest.test_each_difference_is_invalid"),
    ("the histograms not held to the tolerance", PY, "        elif not hist_rel[k] <= tol:\n", "        elif False:\n",
     "EnvTest.test_each_difference_is_invalid"),
    ("the TParameters not compared", PY,
     "        if not abs(p1[k] - p2[k]) <= tol * max(abs(p1[k]), abs(p2[k])):\n", "        if False:\n",
     "EnvTest.test_each_difference_is_invalid"),
    ("the JSON records compared bitwise", PY, "        problems += json_problems(ja, jb, k, tol)\n",
     "        problems += json_problems(ja, jb, k, 0.0)\n", "EnvTest.test_the_measured_rerun_noise_passes"),
    ("the JSON integers given the tolerance", PY,
     "    if isinstance(a, int) and isinstance(b, int):\n        return [] if a == b else",
     "    if False:\n        return [] if a == b else", "EnvTest.test_each_difference_is_invalid"),
    ("a flag left on passes", PY, '    if rc2.get("miss_map") is not None:\n', "    if False:\n",
     "EnvTest.test_each_difference_is_invalid"),
    ("the set-aside widened to fluxSource", PY, '"omnifoldHelperFile", "runArgv")',
     '"omnifoldHelperFile", "runArgv", "fluxSource")', "EnvTest.test_each_difference_is_invalid"),
    # --- the shell scripts
    ("the hooks allowed on a NERSC machine", ENV, 'if [ -n "${NERSC_HOST:-}" ] && {', 'if false && {',
     "Shell.test_the_hooks_are_refused_on_a_nersc_machine"),
    ("the job script runs the envtest", JOB, "case \"$JOB\" in envtest|prepare)", "case \"$JOB\" in none)",
     "Shell.test_the_job_script_refuses_the_envtest_and_prepare_and_mixed_points"),
    ("the job script skips its check", JOB, '        || { cat "$O/logs/check-$JOB-$SLURM_JOB_ID.json"; exit 4; }',
     "        || true", "Shell.test_a_real_run_stops_on_a_failed_check_and_the_wrong_limit"),
    ("a product overwritten", JOB,
     '        if [ -e "$O/out/$label" ]; then echo "[g2r] $label exists; not overwritten"; rc=1; continue; fi\n', "",
     "Shell.test_a_real_run_of_g18_ud_against_stubs"),
    ("the envtest's pre deploy unchecked", ENVT,
     'g2r_deploy_ok "$PRE" "$pre_m" || {', 'true || {', "Shell.test_the_envtest_refuses_a_pre_deploy_not_at_pre_m"),
    ("the prepare's rc swallowed", PREP, '--blocks $P5_BLOCKS --out "$O/prepare" || rc=$?',
     '--blocks $P5_BLOCKS --out "$O/prepare" || true', "Shell.test_the_prepare_passes_its_rc_through"),
    ("the submit takes several jobs", SUB, "[ $# = 3 ] ||", "[ $# -ge 3 ] ||", "Shell.test_the_submit_refusals"),
    ("the binding's M_J1 line unchecked", SUB, 'grep -qE "^\\*\\*M_J1 = \\`$M\\`\\*\\*" <<<"$bind" ||', "true ||",
     "Shell.test_the_binding_must_name_m_on_its_m_j1_line"),
    ("the STOP not honoured", SUB, '[ "$grc" = 9 ] && { echo "STOP', '[ "$grc" = 99 ] && { echo "STOP',
     "Shell.test_the_submission_sequence"),
    ("no wait for sacct", SUB, 'echo "$(date -u +%FT%TZ) M=$M job=$JOB id=$id limit=$lim" | tee -a "$LOG"\n',
     'echo "$(date -u +%FT%TZ) M=$M job=$JOB id=$id limit=$lim" | tee -a "$LOG"\nexit 0\n',
     "Shell.test_sacct_never_listing_the_id_is_rc_6"),
]

RUN = "import runpy, sys; sys.argv = [{test!r}] + {names!r}; runpy.run_path({test!r}, run_name='__main__')"


def run(names: list) -> subprocess.CompletedProcess:
    env = dict(os.environ, PYTHONHASHSEED="0", OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1")
    return subprocess.run([sys.executable, "-B", "-c", RUN.format(test=str(TEST), names=names)], capture_output=True,
                          text=True, env=env, cwd=str(REPO))


def head_bytes(path: Path) -> bytes:
    return subprocess.run(["git", "-C", str(REPO), "show", f"HEAD:{path.relative_to(REPO)}"], check=True,
                          capture_output=True).stdout


def main() -> int:
    sources = (PY, ENV, JOB, ENVT, PREP, SUB)
    for p in sources:
        if p.read_bytes() != head_bytes(p):
            print(f"REFUSED: {p.relative_to(REPO)} differs from HEAD; run in a clean checkout")
            return 2
    orig = {p: p.read_bytes() for p in sources}
    for p in sources:
        print(f"{p.relative_to(REPO)} sha256 {hashlib.sha256(orig[p]).hexdigest()}")
    base = run([])
    m = re.search(r"Ran (\d+) tests", base.stderr)
    n = int(m.group(1)) if m else -1
    skipped = "skipped" in base.stderr
    ok = base.returncode == 0 and n == EXPECTED and not skipped
    print(f"UNMUTATED {'PASS' if ok else 'FAIL'} {TEST.name} tests={n} expected={EXPECTED} skipped={skipped} "
          f"rc={base.returncode}")
    try:
        for name, path, old, new, case in MUTATIONS:
            src = orig[path].decode()
            if src.count(old) != 1:
                print(f"MUTATION NOT-APPLICABLE {name}: the anchor occurs {src.count(old)} times")
                ok = False
                continue
            mutated = src.replace(old, new)
            path.write_text(mutated)
            try:
                p = run([case])
            finally:
                path.write_bytes(orig[path])
            killed = p.returncode != 0
            print(f"MUTATION {'KILLED' if killed else 'SURVIVED'} {name} [{case}] "
                  f"sha256={hashlib.sha256(mutated.encode()).hexdigest()[:16]}")
            ok &= killed
    finally:
        for p in sources:
            p.write_bytes(orig[p])
    restored = all(p.read_bytes() == head_bytes(p) for p in sources)
    print(f"SOURCES RESTORED {'OK' if restored else 'FAIL'}")
    ok &= restored
    print("ALL-KILLED" if ok else "MUTATION-CHECK FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
