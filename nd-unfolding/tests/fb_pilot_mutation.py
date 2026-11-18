#!/usr/bin/env python3
"""Mutation check of PILOT-FB's tests (tests/test_fb_pilot.py; PILOT-FB-DECLARATION.md rev 3 §8).

Each mutation plants one defect in a copy of one PILOT-FB module and must make the NAMED test fail. Exit 0 only if the
unmutated suite passes with the expected test count (none skipped: run it with LightGBM 4.6.0) and every mutation is
killed by its named test. Harmless changes are tests that must pass (test_harmless_changes_...), not mutants.

    <python with LightGBM 4.6.0> -B nd-unfolding/tests/fb_pilot_mutation.py [--only LABEL] [--jobs N]
"""
import argparse
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ND = HERE.parent
REPO = ND.parent
FILES = ("fb_pilot_edges.py", "fb_pilot_gates.py", "fb_pilot_probe.py", "fb_pilot_analyze.py", "sbatch_pfb.sh",
         "pfb_smoke_prep.sh")
ED, GA, PR, AN, SB, SM = FILES
EXPECTED_TESTS = 45
T = "test_fb_pilot"
MUTATIONS = [
    # §3: the edges
    ("signed spacing (no |u|)", ED, "np.spacing(np.abs(np.asarray(u, np.float32)))", "np.spacing(np.asarray(u, np.float32))",
     "test_signed_spacing_counterexamples_are_refused"),
    ("half the envelope", ED, "    return 0.5 * np.spacing(", "    return 0.25 * np.spacing(",
     "test_no_jitter_crosses_an_admissible_edge"),
    ("a gap that touches is admissible", ED, "    ok = lo < hi\n    e = (lo + hi) / 2.0\n    ok &= (lo < e) & (e < hi) & (np.abs(e) > EDGE_MIN_ABS)\n",
     "    ok = lo <= hi\n    e = (lo + hi) / 2.0\n    ok &= (np.abs(e) > EDGE_MIN_ABS)\n", "test_signed_spacing_counterexamples_are_refused"),
    ("an edge may sit in the zero band", ED, " & (np.abs(e) > EDGE_MIN_ABS)", "",
     "test_no_edge_sits_in_the_zero_band"),
    ("the zero band unchecked", ED, "    if np.any((a > ZERO_BAND[0]) & (a < ZERO_BAND[1])):\n", "    if False:\n",
     "test_the_zero_band_and_finiteness_refuse"),
    ("non-finite values allowed", ED, "    if not np.all(np.isfinite(U)):\n", "    if False:\n",
     "test_the_zero_band_and_finiteness_refuse"),
    ("K is the decimal 1e-35", ED, "K = float(np.float32(1e-35))", "K = 1e-35",
     "test_k_is_lightgbms_float32_constant"),
    ("z from the pool, not the fit column", ED, "    zb = zero_bounds(F)\n", "    zb = zero_bounds(np.asarray(U, np.float64))\n",
     "test_z_comes_from_the_fit_column"),
    ("too few gaps not refused", ED, "    if lower.size < n:\n", "    if False:\n", "test_too_few_gaps_is_infeasible"),
    ("no walk above the previous edge", ED, "        if k <= prev:\n            k = prev + 1\n", "",
     "test_ties_collide_and_walk_up"),
    ("E2 offset ignored", ED, "        t = (i + offset) / (n + 1) * N\n", "        t = i / (n + 1) * N\n",
     "test_one_pool_gives_one_edge_set"),
    ("edges written at 6 digits", ED, '    return format(float(e), ".17g")', '    return format(float(e), ".6g")',
     "test_edges_are_written_at_17_digits_and_round_trip"),
    ("an existing edges dir overwritten", ED, "    out_dir.mkdir(parents=True, exist_ok=False)", "    out_dir.mkdir(parents=True, exist_ok=True)",
     "test_build_edges_writes_twelve_files_and_refuses_an_existing_dir"),
    # code rev 2: the audits' findings
    ("placement: right end of a plateau (code 1)", ED, "        k = int(np.argmin(np.abs(B - t)))  # the lowest k among tied distances (numpy.argmin returns the first)\n",
     "        j = int(np.searchsorted(B, t, side=\"left\"))\n        cands = [c for c in (j - 1, j) if 0 <= c < B.size]\n        k = min(cands, key=lambda c: (abs(B[c] - t), c))\n",
     "test_placement_takes_the_lowest_gap_on_a_plateau"),
    ("G0 stops at the first failure", ED, "                    failed.append(what)\n", "                    raise\n",
     "test_g0_records_every_role_and_feature"),
    ("the time limit allows an hour", AN, "TIME_LIMIT_S = 3000", "TIME_LIMIT_S = 3600", "test_the_slurm_limit_and_the_scripts_cap"),
    ("no #SBATCH --time", SB, "#SBATCH --time=0:50:00\n", "", "test_the_slurm_limit_and_the_scripts_cap"),
    ("any job name accepted", SB, '    case "$SLURM_JOB_NAME" in pfb_*) ;; *) refuse "the job name \'$SLURM_JOB_NAME\' is not in the pfb_ family" ;; esac\n', "",
     "test_the_job_refuses_a_stale_root_a_bad_stage_and_a_foreign_name"),
    ("a stale root accepted", SB, '[ ! -e "$OUT" ] || refuse "the root is not fresh: $OUT exists"\n', "",
     "test_the_job_refuses_a_stale_root_a_bad_stage_and_a_foreign_name"),
    ("any root accepted", SB, '    [ "$OUT" = "$ROOT_DECLARED" ] || refuse "the root $OUT is not the declared $ROOT_DECLARED"\n', "",
     "test_the_job_refuses_a_stale_root_a_bad_stage_and_a_foreign_name"),
    ("exits 4 and 5 not distinguished", SB, '4) bad4="$bad4 $id" ;; 5) bad5="$bad5 $id" ;; ', "",
     "test_exits_4_and_5_and_operational_failures_keep_their_place"),
    ("the smoke runs inside a job", SM, '[ -z "$SLURM_JOB_ID" ] || { echo "[pfb-smoke] refusing: this is a login-node step and runs outside any Slurm job" >&2; exit 2; }\n', "",
     "test_the_smoke_is_a_login_node_step"),
    ("G4 skips the inputs", AN, "    if check_inputs:\n", "    if False:\n", "test_g4_rechecks_the_inputs_the_deploy_and_the_sigma_copy"),
    ("G4 skips the deploy", AN, "    if dp:\n        g4.append(dp)\n", "", "test_g4_rechecks_the_inputs_the_deploy_and_the_sigma_copy"),
    ("G4 skips the sigma copy", AN, '        g4.append("the sigma receipt copy")\n', "        pass\n",
     "test_g4_rechecks_the_inputs_the_deploy_and_the_sigma_copy"),
    ("identity from the first fit only", PR, "    for i, r in enumerate(records):\n", "    for i, r in enumerate(records[:1]):\n",
     "test_identity_is_every_fit_with_the_file_digest"),
    ("identity ignores the file digest", PR, ' \\\n                or r.get("forcedbins_sha256") != want_sha:', ":",
     "test_identity_is_every_fit_with_the_file_digest"),
    ("a sidecar not bound to its product", AN, '        if rec.get("product") != p.name or rec.get("product_sha256") != sha256_path(p):\n', "        if False:\n",
     "test_a_sidecar_is_bound_to_its_product"),
    ("a sidecar's set/seed unchecked against the meta", AN, '        elif (rec.get("set"), rec.get("jitter_seed")) != (s, j) or (blk.get("set"), blk.get("jitter_seed")) != (s, j):\n',
     "        elif False:\n", "test_a_sidecar_is_bound_to_its_product"),
    ("a sidecar's INDEX unchecked", AN, '        elif index_sha is not None and (rec.get("edges_index_sha256") != index_sha or blk.get("edges_index_sha256") != index_sha):\n',
     "        elif False:\n", "test_a_sidecar_is_bound_to_its_product"),
    ("a sidecar's code unchecked", AN, '        elif code is not None and (rec.get("code_sha256") != code or blk.get("code_sha256") != code):\n',
     "        elif False:\n", "test_a_sidecar_is_bound_to_its_product"),
    ("exit 4 not INPUTS CHANGED", AN, '    if g["G4_failing"] or status.get("inputs_changed"):\n', '    if g["G4_failing"]:\n',
     "test_exits_4_and_5_and_operational_failures_keep_their_place"),
    ("crashed tasks below the gates", AN, '    if status.get("task_failures"):\n        return "INCOMPLETE", f"tasks failed: {status[\'task_failures\']}"\n', "",
     "test_exits_4_and_5_and_operational_failures_keep_their_place"),
    ("S1 INVALID looked up as a band", AN, '    if r.get("invalid") or r.get("reading") == "INVALID":\n        return "INVALID"\n', "",
     "test_s1_invalid_reads_invalid_and_non_finite_values_write_as_null"),
    ("non-finite kept in the record", AN, "    if isinstance(obj, float) and not math.isfinite(obj):\n", "    if False:\n",
     "test_s1_invalid_reads_invalid_and_non_finite_values_write_as_null"),
    ("S3 waits for the jitters", AN, "    if bases_ok:\n", "    if bases_ok and jit_ok:\n", "test_base_only_statistics_survive_a_round1_stop"),
    ("the status not bound to the job", AN, '    if str(status.get("job")) != str(job):\n', "    if False:\n",
     "test_the_analysis_is_bound_to_one_job"),
    # §5.1: the gates
    ("G3 (a) reads nothing", GA, '    return {"pass": not any(bad), "mismatched_rows": bad,', '    return {"pass": True, "mismatched_rows": bad,',
     "test_a_middle_edge_removed_changes_the_partition"),
    ("G3 (b) ignores thresholds", GA, "    off = [(f, t) for f, t, _ in splits if f >= len(sets) or t not in sets[f]]\n", "    off = []\n",
     "test_an_edge_moved_in_a_used_gap_fails_b"),
    ("G3 (c) ignores missing types", GA, "    missing = [(f, d) for f, _, d in splits if (d >> 2) & 3 != 0 or d & 1]\n", "    missing = []\n",
     "test_a_nan_in_a_split_feature_fails_c"),
    ("ValueToBin read as strict", GA, '[:, f], side="left") for f, b in enumerate(intended)])',
     '[:, f], side="right") for f, b in enumerate(intended)])', "test_intended_index_is_lightgbms_value_to_bin"),
    ("J compares bases bytewise", GA, "    if base:\n        if not np.array_equal(a.astype(np.float64), b.astype(np.float64)):",
     "    if False:\n        if not np.array_equal(a.astype(np.float64), b.astype(np.float64)):",
     "test_unapplied_wrong_seed_and_edge_moves_are_caught"),
    ("J2 by value for a jitter", GA, "    elif a.dtype != b.dtype or a.tobytes() != b.tobytes():\n",
     "    elif not np.array_equal(a.astype(np.float64), b.astype(np.float64)):\n", "test_unapplied_wrong_seed_and_edge_moves_are_caught"),
    ("J3 counts edge moves as off-edge", GA, '    return {"moved_off_edge": int((moved & ~on_edge).sum()), "moved_on_edge": int((moved & on_edge).sum())}',
     '    return {"moved_off_edge": int(moved.sum()), "moved_on_edge": 0}', "test_unapplied_wrong_seed_and_edge_moves_are_caught"),
    # the probe: the bound selection and J2's rebuild
    ("ref from the observed rows only", PR, '    return {"ref": (feat, None),', '    return {"ref": (np.asarray(exp["obs"]), None),',
     "test_role_matrices_follow_the_bound_selection"),
    ("clf1 without the measured rows", PR, '            "clf1": (np.concatenate([mcreco[pr], measured]), mcreco[pr]),', '            "clf1": (mcreco[pr], mcreco[pr]),',
     "test_role_matrices_follow_the_bound_selection"),
    ("reg scores the passing rows", PR, '            "reg": (mcgen[pr], mcgen[~pr]),', '            "reg": (mcgen[pr], mcgen[pr]),',
     "test_role_matrices_follow_the_bound_selection"),
    ("J2 rebuild at amplitude 0", PR, "            base_exp = s5n_pseudo.build_pseudo(st[\"inputs\"], st[\"bkg\"], a.truth, a.amplitude, split_key,",
     "            base_exp = s5n_pseudo.build_pseudo(st[\"inputs\"], st[\"bkg\"], a.truth, 0.0, split_key,",
     "test_j2_rebuilds_with_the_runs_own_build_inputs"),
    # §5, §5.2: the analysis
    ("rows 1 and 2 swapped", AN, '    (1, lambda s1, s2, s3: s1 == "NOT REMOVED", "NOT A REMEDY"),\n    (2, lambda s1, s2, s3: s2 == "STAB_FAIL", "NOT AN OPTION AS DECLARED"),',
     '    (2, lambda s1, s2, s3: s2 == "STAB_FAIL", "NOT AN OPTION AS DECLARED"),\n    (1, lambda s1, s2, s3: s1 == "NOT REMOVED", "NOT A REMEDY"),',
     "test_every_combination_reaches_exactly_one_row"),
    ("row 6 lost", AN, '    (6, lambda s1, s2, s3: s1 == "REDUCED" and s3 == "POLICY-STABLE", "OPTION C"),\n', "",
     "test_every_combination_reaches_exactly_one_row"),
    ("a NaN endpoint read as the band", AN, "    if not (math.isfinite(lo) and math.isfinite(hi)):\n", "    if False:\n",
     "test_a_nonfinite_bootstrap_endpoint_is_inconclusive"),
    ("rows 5/7 name both numbers", AN, '    crossed = [w for w, v, bar in (("median", s3["median"], BARS[0]), ("maximum", s3["max"], BARS[1])) if v > bar]',
     '    crossed = ["median", "maximum"]', "test_the_bars_include_equality_and_rows_5_7_name_what_crossed"),
    ("INCOMPLETE before the gates", AN, '    if g["G1"] is False:\n        return "NOT REPRODUCED"',
     '    if g["missing"]:\n        return "INCOMPLETE", "x"\n    if g["G1"] is False:\n        return "NOT REPRODUCED"',
     "test_gate_precedence_and_a_deliberate_round1_stop"),
    ("RUN REFUSED before INPUTS CHANGED", AN, '    if g["G4_failing"] or status.get("inputs_changed"):\n        return "INPUTS CHANGED", status.get("inputs_changed") or f"not at their pins: {g[\'G4_failing\']}"\n    if status.get("refused"):\n        return "RUN REFUSED", status["refused"]',
     '    if status.get("refused"):\n        return "RUN REFUSED", status["refused"]\n    if g["G4_failing"] or status.get("inputs_changed"):\n        return "INPUTS CHANGED", status.get("inputs_changed") or f"not at their pins: {g[\'G4_failing\']}"',
     "test_gate_precedence_and_a_deliberate_round1_stop"),
    ("a zero S1 mean allowed", AN, '    if "E1_jit" in Fs and np.any(Fs["E1_jit"].mean(axis=0) == 0):\n', "    if False:\n",
     "test_invalid_branches"),
    ("a zero base allowed", AN, "        if k in Fs and np.any(Fs[k] == 0):\n", "        if False:\n", "test_invalid_branches"),
    ("S2 pairs averaged, not maxed", AN, "    pairs = [np.maximum(z[2 * p], z[2 * p + 1]) for p in range(len(SEEDS) // 2)]",
     "    pairs = [(z[2 * p] + z[2 * p + 1]) / 2 for p in range(len(SEEDS) // 2)]", "test_s2_and_s3_follow_their_definitions"),
    ("S3 place uses E3", AN, '            "place": {"median": float(np.median(d["E1-E2"])), "max": float(np.max(d["E1-E2"]))},',
     '            "place": {"median": float(np.median(d["E1-E3"])), "max": float(np.max(d["E1-E3"]))},',
     "test_s2_and_s3_follow_their_definitions"),
]


def mirror(root: Path) -> Path:
    repo = root / "repo"
    repo.mkdir()
    for e in REPO.iterdir():
        if e.name != "nd-unfolding":
            (repo / e.name).symlink_to(e)
    nd = repo / "nd-unfolding"
    nd.mkdir()
    for e in ND.iterdir():
        if e.name not in FILES and e.name != "tests":
            (nd / e.name).symlink_to(e)
    for f in FILES:
        (nd / f).write_bytes((ND / f).read_bytes())
    tests = nd / "tests"
    tests.mkdir()
    for e in HERE.iterdir():
        if e.name == f"{T}.py":
            (tests / e.name).write_bytes(e.read_bytes())  # a copy: a symlink would resolve back to the real modules
        else:
            (tests / e.name).symlink_to(e)
    return nd


def run_suite(nd: Path) -> tuple[int, str]:
    p = subprocess.run([sys.executable, "-B", "-W", "ignore", "-m", "unittest", f"nd-unfolding/tests/{T}.py"],
                       cwd=nd.parent, capture_output=True, text=True, timeout=3600,
                       env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin"})
    return p.returncode, p.stdout + p.stderr


def failing(out: str) -> set:
    return set(re.findall(r"^(?:FAIL|ERROR): (\w+)", out, re.M))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None)
    ap.add_argument("--jobs", type=int, default=1)
    a = ap.parse_args(argv)
    with tempfile.TemporaryDirectory() as d:
        rc, out = run_suite(mirror(Path(d)))
    ran = re.search(r"^Ran (\d+) tests?", out, re.M)
    if rc != 0 or not ran or int(ran.group(1)) != EXPECTED_TESTS or "skipped" in out:
        print(f"UNMUTATED SUITE: rc {rc}, ran {ran.group(1) if ran else '?'} of {EXPECTED_TESTS} expected tests\n" + out[-3000:])
        return 1
    print(f"unmutated suite: {ran.group(1)} tests OK, none skipped, in the mirrored tree")
    todo = [m for m in MUTATIONS if not a.only or a.only in m[0]]
    ok = True

    def one(m):
        label, fname, old, new, test = m
        src = (ND / fname).read_text()
        if src.count(old) != 1:
            return label, test, None, f"anchor occurs {src.count(old)} times"
        with tempfile.TemporaryDirectory() as d:
            nd = mirror(Path(d))
            (nd / fname).write_text(src.replace(old, new))
            _, out = run_suite(nd)
        return label, test, failing(out), ""

    with ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for label, test, fails, why in ex.map(one, todo):
            if fails is None:
                print(f"MUTATION NOT APPLIED  {label}: {why}", flush=True)
                ok = False
                continue
            killed = test in fails
            ok &= killed
            print(f"{'KILLED' if killed else 'SURVIVED':8s}  {label:44s} by {test}"
                  + ("" if killed else f"  (failing: {sorted(fails)})"), flush=True)
    print("MUTATION CHECK ::", "PASS" if ok else "FAIL", f"({len(todo)} mutations)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
