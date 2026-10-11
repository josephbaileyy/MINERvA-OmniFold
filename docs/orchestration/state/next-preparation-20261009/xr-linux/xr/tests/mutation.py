"""Mutation controls for the XR package (xr-linux): each mutant must turn its targeted test red.

Each mutant edits one package file in place, runs the named tests, and restores the file, whose
sha256 is verified after every mutant. Run from this directory with the same interpreter and
PYTHONPATH as the suite:

    PYTHONPATH=$(root-config --libdir) python3.13 mutation.py --out mutation-results.json
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parent

MUTANTS = [
    ('overwrite-allowed', 'xr_run.py', '            gx.reserve_output(str(out))\n', '            pass\n', ['test_xr.XR.test_an_existing_output_is_never_overwritten']),
    ('symlink-allowed', 'xr_run.py', '    if str(real) != os.path.normpath(str(p)):\n', '    if False:\n', ['test_xr.XR.test_a_symlinked_attempt_directory_is_refused']),
    ('frozen-path-allowed', 'xr_run.py', '    if str(real) in frozen_paths(refs):\n', '    if False:\n', ['test_xr.XR.test_an_output_that_is_a_frozen_reference_path_is_refused']),
    ('checkout-outroot-allowed', 'xr_run.py', '    for root in (Path(repo).resolve(), Path(CANONICAL), *map(Path, extra_forbidden)):\n', '    for root in ():\n', ['test_xr.XR.test_an_outroot_inside_the_checkout_is_refused']),
    ('seed-unchecked', 'xr_run.py', '                if seed != want:\n', '                if False:\n', ['test_xr.XR.test_a_wrong_seed_stops_before_training']),
    ('class-unchecked', 'xr_run.py', '                if _name not in self.want:\n', '                if False:\n', ['test_xr.XR.test_a_backend_other_than_the_frozen_one_stops_before_training']),
    ('normalization-unchecked', 'xr_run.py', '    if bad:\n        raise BackendRefusal(f"normalization', '    if False:\n        raise BackendRefusal(f"normalization', ['test_xr.XR.test_a_normalization_differing_from_the_reference_is_refused']),
    ('driver-pin-unchecked', 'xr_run.py', '        if rec["sha256"] != digest:\n', '        if False:\n', ['test_xr.XR.test_a_changed_driver_or_helper_is_refused']),
    ('input-digest-unchecked', 'xr_run.py', '            if digest != spec["sha256"] or st["size"] != spec["size"]:\n', '            if False:\n', ['test_xr.XR.test_an_input_with_other_bytes_is_refused']),
    ('cwd-unchecked', 'xr_run.py', '        if Path.cwd().resolve() != REPO / "2d-unfolding":\n', '        if False:\n', ['test_xr.XR.test_the_wrong_working_directory_is_refused']),
    ('environment-unchecked', 'xr_run.py', '    if bad:\n        raise BackendRefusal(f"environment differs', '    if False:\n        raise BackendRefusal(f"environment differs', ['test_xr.XR.test_an_environment_other_than_the_frozen_one_stops_before_training']),
    ('outroot-unchecked', 'xr_run.py', '        if adm["outroot"] != runs["outroot"]:\n', '        if False:\n', ['test_xr.XR.test_an_admission_that_is_not_admitted_or_has_other_runs_is_refused']),
    ('regressor-count-loose', 'xr_run.py', '        if n_c != 2 * it or n_r != it:\n', '        if n_c != 2 * it or n_r not in (0, it):\n', ['test_xr.Units.test_the_regressor_must_fit_every_iteration']),
    ('abbreviated-commit-accepted', 'xr_admit.py', '    if not re.fullmatch(r"[0-9a-f]{40}", package_commit or ""):\n', '    if False:\n', ['test_xr.XR.test_the_authorization_binding']),
    ('package-drift-accepted', 'xr_admit.py', '    if changed:\n        raise Refusal("the package changed after', '    if False:\n        raise Refusal("the package changed after', ['test_xr.XR.test_a_package_change_after_the_package_commit_is_refused']),
    ('outroot-reuse-allowed', 'xr_admit.py', '        outroot.mkdir(parents=False)\n', '        outroot.mkdir(parents=False, exist_ok=True)\n', ['test_xr.XR.test_a_second_draft_for_the_same_package_is_refused']),
    ('nested-setup-unbound', 'xr_admit.py', '        rec["nested"][str(p)] = sha(p)\n', '        rec["nested"][str(p)] = None\n', ['test_xr.XR.test_verify_refuses_a_changed_nested_setup_or_a_copied_admission']),
    ('attempt-cap-off-by-one', 'xr_admit.py', '    if total[kind_name] + 1 > cap:\n', '    if total[kind_name] + 1 > cap + 1:\n', ['test_xr.Launch.test_submit_releases_in_order_counts_attempts_records_diagnoses_and_cancels_on_a_failed_sbatch']),
    ('billing-unchecked', 'xr_admit.py', '              "billing": billing is not None and billing <= kind["billing_max"],\n', '              "billing": True,\n', ['test_xr.Launch.test_jobcheck_on_real_format_allocations']),
    ('ledger-billing-unflagged', 'xr_admit.py', '    over += flagged\n', '    pass\n', ['test_xr.Launch.test_ledger_is_cumulative_over_every_prior_grant_and_flags']),
    ('sacct-uncounted', 'xr_admit.py', '    return {k: max(dirs[k], subs[k], sac[k])', '    return {k: max(dirs[k], subs[k])', ['test_xr.Launch.test_next_attempt_counts_only_this_amendment_and_enforces_order_spares_and_the_stop']),
    ('stop-unchecked', 'xr_admit.py', '    if now + limit > stop:\n', '    if False:\n', ['test_xr.Launch.test_next_attempt_counts_only_this_amendment_and_enforces_order_spares_and_the_stop']),
    ('tres-field-restored', 'xr_admit.py', '    billing = parse_billing(vals["AllocTRES"])\n', '    billing = parse_billing(dict(t.split("=", 1) for t in text.split() if "=" in t).get("TRES", ""))\n', ['test_xr.Scheduler.test_billing_is_read_from_AllocTRES_explicitly']),
    ('dict-parse-restored', 'xr_admit.py', '    hits = re.findall(r"(?:^|\\s){}=(\\S*)".format(re.escape(key)), text)\n', '    hits = [dict(t.split("=", 1) for t in text.split() if "=" in t)[key]] if key + "=" in text else []\n', ['test_xr.Scheduler.test_billing_is_read_from_AllocTRES_explicitly']),
    ('null-allocation-accepted', 'xr_admit.py', '              "billing": billing is not None and billing <= kind["billing_max"],\n', '              "billing": billing is None or billing <= kind["billing_max"],\n', ['test_xr.Scheduler.test_billing_is_read_from_AllocTRES_explicitly']),
    ('jobid-unchecked', 'xr_admit.py', '    checks = {"JobId": vals["JobId"] == str(job_id), "QOS": vals["QOS"] == kind["qos"],\n', '    checks = {"JobId": True, "QOS": vals["QOS"] == kind["qos"],\n', ['test_xr.Scheduler.test_the_captured_running_line_is_the_preflight_kind_and_no_other']),
    ('record-skipped', 'xr_admit.py', '    if args.record:\n', '    if False:\n', ['test_xr.Launch.test_jobcheck_on_real_format_allocations']),
    ('prior-unchecked', 'xr_admit.py', '    check_prior(runs, args.sacct)\n', '    pass\n', ['test_xr.Launch.test_next_attempt_counts_only_this_amendment_and_enforces_order_spares_and_the_stop']),
    ('preflight-gate-off', 'xr_admit.py', '    elif not preflight_passed(adm, runs):\n', '    elif False:\n', ['test_xr.Launch.test_next_attempt_counts_only_this_amendment_and_enforces_order_spares_and_the_stop']),
    ('l0-gate-off', 'xr_admit.py', '    elif args.run != release["first"] and not comparable(adm, release["first"]):\n', '    elif False:\n', ['test_xr.Launch.test_next_attempt_counts_only_this_amendment_and_enforces_order_spares_and_the_stop']),
    ('preflight-receipt-comparable', 'xr_admit.py', '    if best is None or best.get("schema") != "xr-receipt/2" or best.get("run") != run_name:\n', '    if best is None or best.get("run") != run_name:\n', ['test_xr.Launch.test_next_attempt_counts_only_this_amendment_and_enforces_order_spares_and_the_stop']),
    ('ceiling-unchecked', 'xr_admit.py', '    if planned > runs["cap_node_h"]:\n', '    if False:\n', ['test_xr.Launch.test_the_planned_cumulative_ceiling_includes_every_prior_charge']),
    ('prior-charge-dropped', 'xr_admit.py', '    cumulative = prior_charged + charged\n', '    cumulative = charged\n', ['test_xr.Launch.test_ledger_is_cumulative_over_every_prior_grant_and_flags']),
    ('prior-charge-unverified', 'xr_admit.py', '    if abs(prior_charged - prior["charged_node_h_recorded"]) > 1e-12:\n', '    if False:\n', ['test_xr.Launch.test_ledger_is_cumulative_over_every_prior_grant_and_flags']),
    ('foreign-prior-job-ignored', 'xr_admit.py', '            if pre.fullmatch(r.get("JobName", "")) and jid not in grant["jobs"]:\n', '            if False:\n', ['test_xr.Launch.test_ledger_is_cumulative_over_every_prior_grant_and_flags']),
    ('gate-job-unbound', 'xr_admit.py', '        if not job or job != subs.get((pf, r.get("attempt"))):\n', '        if False:\n', ['test_xr.Launch.test_the_preflight_gate_requires_the_pf_jobs_own_bound_and_complete_receipt']),
    ('gate-record-unchecked', 'xr_admit.py', '        if not line or not f.is_file() or f.read_text() != line or sha(f) != rec.get("sha256"):\n', '        if not line:\n', ['test_xr.Launch.test_the_preflight_gate_requires_the_pf_jobs_own_bound_and_complete_receipt']),
    ('gate-allocation-unchecked', 'xr_admit.py', '            check_allocation(line, kind, job)\n        except', '            pass\n        except', ['test_xr.Launch.test_the_preflight_gate_requires_the_pf_jobs_own_bound_and_complete_receipt']),
    ('gate-strict-exit-unchecked', 'xr_admit.py', '        if r.get("exit_code") != 0 or (r.get("identity") or {}).get("strict") is not True:\n', '        if False:\n', ['test_xr.Launch.test_the_preflight_gate_requires_the_pf_jobs_own_bound_and_complete_receipt']),
    ('ledger-unreadable-billing-uncharged', 'xr_admit.py', '            flagged.append("job {} ran {} s with unreadable billing".format(s["job_id"], elapsed))\n', '            pass\n', ['test_xr.Launch.test_ledger_is_cumulative_over_every_prior_grant_and_flags']),
    ('prior-unreadable-billing-uncharged', 'xr_admit.py', '                over.append("prior job {} ran {} s with unreadable billing".format(jid, elapsed))\n', '                pass\n', ['test_xr.Launch.test_ledger_is_cumulative_over_every_prior_grant_and_flags']),
    ('loose-tolerance', 'xr_compare.py', 'TOL = 1e-8\n', 'TOL = 1e-7\n', ['test_xr.Comparator.test_tolerance_cells_and_digests']),
    ('cell-identity-unchecked', 'xr_compare.py', '    if gid(xn) != cells or gid(xr) != cells:\n', '    if False:\n', ['test_xr.Comparator.test_tolerance_cells_and_digests']),
    ('receipt-admission-unchecked', 'xr_compare.py', '        return None, f"{run}: the receipt names another run or admission than {adm_path}"\n', '        pass\n', ['test_xr.Comparator.test_receipts_must_name_their_run_and_admission']),
    ('axes-unchecked', 'xr_compare.py', '    if xn.shape != xr.shape or en != er:\n', '    if xn.shape != xr.shape:\n', ['test_xr.Comparator.test_tolerance_cells_and_digests']),
    ('comparator-preflight-accepted', 'xr_compare.py', '    if r.get("schema") != "xr-receipt/2" or r.get("kind") == "preflight":\n', '    if False:\n', ['test_xr.Comparator.test_receipts_must_name_their_run_and_admission']),
    ('no-slurm-deadline', 'launch/xr_submit.sh', ' --deadline="$DEADLINE"', '', ['test_xr.Launch.test_submit_releases_in_order_counts_attempts_records_diagnoses_and_cancels_on_a_failed_sbatch']),
    ('submit-no-cancel', 'launch/xr_submit.sh', 'on_error() { for j in "${QUEUED[@]}"; do scancel "$j" || true; done;', 'on_error() { for j in; do scancel "$j" || true; done;', ['test_xr.Launch.test_submit_releases_in_order_counts_attempts_records_diagnoses_and_cancels_on_a_failed_sbatch']),
    ('submit-old-prefix', 'launch/xr_submit.sh', '--job-name="${PREFIX}_${RUN}_a${ATT}"', '--job-name="xrr_${RUN}_a${ATT}"', ['test_xr.Launch.test_submit_releases_in_order_counts_attempts_records_diagnoses_and_cancels_on_a_failed_sbatch']),
    ('submit-window-reset', 'launch/xr_submit.sh', '-S "$SINCE"', '-S "2026-10-11"', ['test_xr.Launch.test_submit_releases_in_order_counts_attempts_records_diagnoses_and_cancels_on_a_failed_sbatch']),
    ('job-record-dropped', 'launch/xr_job.sbatch', ' --record "$DIR/scontrol-job.txt"', '', ['test_xr.Launch.test_the_preflight_through_the_job_script_passes_with_its_fixture_stage']),
    ('threadpool-info-restored', 'xr_run.py', '    have["runtime"] = runtime_record()\n', '    have["runtime"] = runtime_record()\n    have["threadpools"] = __import__("threadpoolctl").threadpool_info()\n', ['test_xr.Units.test_the_run_path_has_no_child_launching_inspection']),
    ('loky-cache-seeded', 'xr_run.py', '    import joblib\n    want = kind["cpus_per_task"]\n', '    import joblib\n    from joblib.externals.loky.backend import context as _c\n    _c.physical_cores_cache = kind["cpus_per_task"]\n    want = kind["cpus_per_task"]\n', ['test_xr.Units.test_the_run_path_has_no_child_launching_inspection']),
    ('launch-window-open', 'xr_run.py', '            setattr(mod, attr, self._refuser(f"{mod_name}.{attr}"))\n', '            pass\n', ['test_xr.Units.test_the_launch_window_refuses_and_records_then_restores']),
    ('launch-window-not-restored', 'xr_run.py', '        for mod, attr, orig in reversed(self._saved):\n            setattr(mod, attr, orig)\n', '        for mod, attr, orig in reversed(self._saved):\n            pass\n', ['test_xr.Units.test_the_launch_window_refuses_and_records_then_restores']),
    ('swallowed-launch-ignored', 'xr_run.py', '    if spy.calls:\n        raise LaunchRefusal(', '    if False:\n        raise LaunchRefusal(', ['test_xr.Units.test_a_launch_a_library_swallows_is_still_recorded']),
    ('run-path-launch-unchecked', 'xr_run.py', '            output.update(path=str(out), sha256=sha256_file(out), bytes=os.path.getsize(out))\n        require_no_launch(spy)\n', '            output.update(path=str(out), sha256=sha256_file(out), bytes=os.path.getsize(out))\n', ['test_xr.Units.test_both_paths_refuse_on_a_recorded_launch']),
    ('thread-plan-full-node-accepted', 'xr_run.py', '        if not rec["affinity"] < rec["os_cpu_count"]:\n', '        if False:\n', ['test_xr.Units.test_the_linux_thread_plan']),
    ('thread-plan-affinity-unchecked', 'xr_run.py', '        if rec["affinity"] != want:\n', '        if False:\n', ['test_xr.Units.test_the_linux_thread_plan']),
    ('thread-plan-loky-env-accepted', 'xr_run.py', '        if rec["LOKY_MAX_CPU_COUNT"] is not None:\n', '        if False:\n', ['test_xr.Units.test_the_linux_thread_plan']),
    ('thread-plan-joblib-unchecked', 'xr_run.py', '    if rec["joblib_cpu_count_physical"] != want:\n', '    if False:\n', ['test_xr.Units.test_the_linux_thread_plan']),
    ('thread-plan-omp-unchecked', 'xr_run.py', '    if rec["OMP_NUM_THREADS"] != str(kind["omp_threads"]):\n', '    if False:\n', ['test_xr.XR.test_a_thread_count_other_than_the_kinds_stops_before_training']),
    ('lgbm-fit-threads-unchecked', 'xr_run.py', '                    if planned != self.threads:\n', '                    if False:\n', ['test_xr.Units.test_the_lightgbm_thread_count_is_checked_at_fit_after_fit_and_at_predict']),
    ('lgbm-booster-threads-unchecked', 'xr_run.py', '                    if used != planned:\n', '                    if False:\n', ['test_xr.Units.test_the_lightgbm_thread_count_is_checked_at_fit_after_fit_and_at_predict']),
    ('lgbm-predict-threads-unchecked', 'xr_run.py', '            if n != self.threads:\n', '            if False:\n', ['test_xr.Units.test_the_lightgbm_thread_count_is_checked_at_fit_after_fit_and_at_predict']),
    ('lgbm-predicts-unrequired', 'xr_run.py', '        if self.backend["estimator"] == "lgbm" and (not self.predicts["calls"]', '        if False and (not self.predicts["calls"]', ['test_xr.Units.test_lightgbm_runs_must_have_predicted_on_the_plan']),
    ('recorder-not-uninstalled', 'xr_run.py', '            if had:\n                setattr(cls, attr, orig)\n            else:\n                delattr(cls, attr)\n', '            pass\n', ['test_xr.Units.test_uninstall_restores_every_class_so_runs_can_follow_in_one_process']),
    ('launch-control-vacuous', 'xr_run.py', '    res["met"] = all(p["launches"] for p in res["probes"].values())\n', '    res["met"] = True\n', ['test_xr.Units.test_launch_controls_are_unmet_when_a_probe_launches_nothing']),
    ('job-controls-ignored', 'xr_run.py', '        if not all(c["met"] for c in receipt["controls"].values()):\n', '        if False:\n', ['test_xr.Launch.test_the_preflight_fails_when_a_job_control_is_not_met']),
    ('job-control-rc-unchecked', 'xr_run.py', '        met = (rc == want_rc if want_rc else rc not in ("", "0")) and want_text in err\n', '        met = want_text in err or True\n', ['test_xr.Launch.test_the_preflight_fails_when_a_job_control_is_not_met']),
    ('job-script-controls-skipped', 'launch/xr_job.sbatch', 'if [ "$KIND" = preflight ]; then\n', 'if false; then\n', ['test_xr.Launch.test_the_preflight_through_the_job_script_passes_with_its_fixture_stage']),
    ('gate-fixture-unchecked', 'xr_admit.py', '        if not (fx.get("verdict") == "PASS" and set(runs["runs"][pf]["preflight_of"]) <= set(fx_runs)\n', '        if False and (fx.get("verdict") == "PASS" and set(runs["runs"][pf]["preflight_of"]) <= set(fx_runs)\n', ['test_xr.Launch.test_the_preflight_gate_requires_the_pf_jobs_own_bound_and_complete_receipt']),
    ('gate-controls-unchecked', 'xr_admit.py', '        if not (ctl and all(c.get("met") is True for c in ctl.values()) and r.get("launches") == []):\n', '        if False:\n', ['test_xr.Launch.test_the_preflight_gate_requires_the_pf_jobs_own_bound_and_complete_receipt']),
    ('gate-inventory-unchecked', 'xr_admit.py', '        if not inventory_clean(d / "inventory.jsonl", "XR-{}-{}".format(pf, d.name)):\n', '        if False:\n', ['test_xr.Launch.test_the_preflight_gate_requires_the_pf_jobs_own_bound_and_complete_receipt']),
    ('gate-old-schema-accepted', 'xr_admit.py', '        if not (r.get("schema") == "xr-preflight-receipt/2" and r.get("status") == "preflight-pass"\n', '        if not (r.get("status") == "preflight-pass"\n', ['test_xr.Launch.test_the_preflight_gate_requires_the_pf_jobs_own_bound_and_complete_receipt']),
    ('prior-grant-dropped', 'xr_admit.py', '    for grant in runs["prior"]["grants"]:\n        seen', '    for grant in runs["prior"]["grants"][:1]:\n        seen', ['test_xr.Launch.test_next_attempt_counts_only_this_amendment_and_enforces_order_spares_and_the_stop']),
    ('prior-grant-dropped-in-ledger', 'xr_admit.py', '    for grant in prior["grants"]:\n', '    for grant in prior["grants"][:1]:\n', ['test_xr.Launch.test_ledger_is_cumulative_over_every_prior_grant_and_flags']),
    ('draft-prior-outroot-allowed', 'xr_admit.py', '    if any(os.path.normpath(g["outroot"]) == os.path.normpath(str(outroot)) for g in runs["prior"]["grants"]):\n', '    if False:\n', ['test_xr.Launch.test_draft_refuses_every_prior_grants_outroot']),
    ('spare-without-diagnosis', 'xr_admit.py', '    if earlier and not (args.diagnosis or "").strip():\n', '    if False:\n', ['test_xr.Launch.test_next_attempt_counts_only_this_amendment_and_enforces_order_spares_and_the_stop']),
    ('submit-diagnosis-dropped', 'launch/xr_submit.sh', '                               --diagnosis "${XR_DIAGNOSIS:-}")', '                               --diagnosis "")', ['test_xr.Launch.test_submit_releases_in_order_counts_attempts_records_diagnoses_and_cancels_on_a_failed_sbatch']),
    ('window-start-ignored', 'xr_admit.py', '    if (runs.get("window") or {}).get("first_submission_utc"):\n        starts.append(parse_utc(runs["window"]["first_submission_utc"]))\n    first = min(starts, default=now)\n', '    first = min(starts, default=now)\n', ['test_xr.Launch.test_a_window_start_carried_by_a_repaired_package_is_honoured']),
    ('ledger-header-reads-rows-anyway', 'xr_admit.py', '        print(json.dumps({"over": ["the sacct header lacks {}: no row was read".format(lacking)],\n                          "header": head}, indent=1))\n        return OVER\n', '        over.append("the sacct header lacks {}".format(lacking))\n', ['test_xr.Launch.test_ledger_refuses_a_header_lacking_a_column_before_reading_any_row']),
    ('executed-outside-package-unbound', 'xr_admit.py', '            "docs/orchestration/state/next-preparation-20261009/sb1-prep/tests/make_fixture_omnifile.py")', ')', ['test_xr.XR.test_a_change_to_an_executed_file_outside_the_package_is_refused']),
    ('maker-pin-unchecked', 'xr_run.py', '        if rec["sha256"] != fx["maker_digest"]:\n', '        if False:\n', ['test_xr.Launch.test_the_preflight_pins_the_fixture_writer']),
]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


#: Not listed, equivalent on any passing fixture (every check and control is true there, so forcing
#: one true changes nothing a test can see): forcing ``repeat_reproduces_to_the_criterion``, the
#: fixture verdict's control term, or a completed control's ``met`` to True. The release gate reads
#: each check and each control's ``met`` itself (``gate-fixture-unchecked``, ``gate-controls-unchecked``).


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", nargs="*", help="run only these mutants")
    a = ap.parse_args()
    results = []
    for name, rel, old, new, tests in MUTANTS:
        if a.only and name not in a.only:
            continue
        path = PKG / rel
        before = path.read_bytes()
        digest = sha(path)
        text = before.decode()
        if text.count(old) != 1:
            results.append({"mutant": name, "status": "ANCHOR-NOT-UNIQUE", "count": text.count(old)})
            continue
        try:
            path.write_text(text.replace(old, new))
            r = subprocess.run([sys.executable, "-m", "unittest", *tests], cwd=HERE, capture_output=True, text=True,
                               env=dict(os.environ, OMP_NUM_THREADS="1"))
            caught = r.returncode != 0
            results.append({"mutant": name, "file": rel, "tests": tests, "caught": caught,
                            "tail": r.stderr.strip().splitlines()[-1] if r.stderr.strip() else ""})
        finally:
            path.write_bytes(before)
            assert sha(path) == digest, f"restore failed for {rel}"
        print(f"{name}: {'caught' if caught else 'NOT CAUGHT'}", flush=True)
    out = {"n": len(results), "caught": sum(1 for r in results if r.get("caught")), "results": results}
    Path(a.out).write_text(json.dumps(out, indent=1) + "\n")
    print(f"{out['caught']} of {out['n']} caught")
    return 0 if out["caught"] == out["n"] else 1


if __name__ == "__main__":
    sys.exit(main())
