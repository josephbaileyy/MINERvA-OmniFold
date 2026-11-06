#!/usr/bin/env python3
"""Mutation check of REF-G1's tests (REF-G1-DECLARATION.md §7; REF-G1-BINDING-1.md ruling 2).

Each mutation plants one declared defect in ``ref_g1.py`` or ``ref_g1_read.py`` and must make its NAMED test fail or
error. The modules locate the repository from their own path, so a mutation is written in place and the original
restored after it; the harness refuses to finish unless every file's sha256 is back to what it was.

The expected survivors (§7, "recorded as equivalent, with its proof"; the director added the jitter-seed one) are each
run once against the WHOLE suite and must survive: the harness fails if one is killed, which would refute its proof,
or if either is missing from the list.

    python3 -B nd-unfolding/ref_g1/ref_g1_mutation.py
"""
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEST = HERE / "test_ref_g1.py"
D, R = "ref_g1.py", "ref_g1_read.py"
EXPECTED_TESTS = 38  # a run that stops early exits 0 with fewer: refuse it
NULL_CALL = 't = null_t(c_stat, c_flux, wflux, c_fixed, n_rep, b["draws"], b["seed"], b["batch"], rd["norm_fraction"])'
MUTATIONS = [
    # §7's required mutants
    ("chi2_16 quantiles in place of the bootstrap's", R,
     '"bars": [float(np.quantile(t, q)) for q in b["quantiles"]],',
     '"bars": [26.29622760486434, 35.88680724686915],',
     "Readings.test_the_bars_are_ts_simulated_null_not_chi2"),
    ("C*_norm from the realized Delta", R, NULL_CALL,
     'x_c, _ = ibu_cells(run, "central", cfg)\n'
     '    d_real = rd["norm_fraction"] * (x_c - e_cells(staged(cfg["e_products"]["central"]), U))\n'
     '    t = null_t(c_stat, c_flux, wflux, c_fixed + np.outer(d_real, d_real), n_rep, b["draws"], b["seed"], '
     'b["batch"], 0.0)',
     "Readings.test_the_bars_never_read_the_central_difference"),
    ("the flux block held fixed", R, NULL_CALL, NULL_CALL[:-1] + ", resample_flux=False)",
     "Readings.test_the_flux_block_is_resampled"),
    ("the self-check skipped", R, '    if not sc["pass"]:\n', "    if False:\n",
     "Readings.test_a_failed_self_check_writes_no_bars"),
    ("the order guard removed", R, '    if (out.parent / "readout.json").exists():\n', "    if False:\n",
     "Readings.test_the_order_guard_and_the_bars_identity"),
    ("the membership refusal removed from g1's builder", D, "    if any(moved.values()):\n", "    if False:\n",
     "Replicas.test_a_jitter_that_moves_membership_is_refused_before_any_replica"),
    # per reading bar
    ("R1's agree bar strict", R, 'return "agree" if t <= bar_lo else', 'return "agree" if t < bar_lo else',
     "Readings.test_the_reading_words_at_their_bars"),
    ("R1's differ bar strict", R, '("marginal" if t <= bar_hi else "differ")', '("marginal" if t < bar_hi else "differ")',
     "Readings.test_the_reading_words_at_their_bars"),
    ("R2's band open", R, 'return "within" if lo <= ratio <= hi else', 'return "within" if lo < ratio < hi else',
     "Readings.test_the_reading_words_at_their_bars"),
    ("R1 formed on a singular covariance", R, "ok = bool(lam.min() > 0 and lam.max() / lam.min() < cond_max)",
     "ok = bool(lam.min() > 0)", "Readings.test_r1_is_not_formed_on_a_singular_covariance"),
    # per control
    ("G-CV reads one variant", R, 'same = all(np.array_equal(a[k], b[k]) for k in ("ks", "F_fold", "F_sub"))',
     'same = all(np.array_equal(a[k], b[k]) for k in ("ks", "F_fold"))', "Controls.test_g_cv_fires_on_either_variant"),
    ("G-IBU1 reads one variant", R, '    keys = ("ks", "F_fold", "F_sub")\n', '    keys = ("ks", "F_fold")\n',
     "Controls.test_g_ibu1_fires_on_either_variant_and_on_the_pin"),
    ("G-IBU1's pin unchecked", R, '    if staged.sha[ref["path"]] != ref["sha256"]:\n', "    if False:\n",
     "Controls.test_g_ibu1_fires_on_either_variant_and_on_the_pin"),
    ("G-cells' tolerance loosened", R, 'rel <= cfg["readings"]["gcells_rtol"]', "rel <= 1e-6",
     "Controls.test_g_cells_holds_at_its_tolerance"),
    ("G-pair's pins unchecked", R, "        if pins.get(str(p)) is None or paired.e_sha(p) != pins[str(p)]:\n",
     "        if False:\n", "Controls.test_g_pair_fires_on_a_pin_a_swapped_replica_and_a_universe_from_other_weights"),
    ("G-draw passes anything", D, '"pass": bool(all(checks.values()))}', '"pass": True}',
     "Replicas.test_g_draw_fires_on_a_replica_that_is_not_es"),
    ("the reader ignores G-draw", R,
     'controls["G-draw"] = {"pass": all(m.get("g_draw", {}).get("pass") is True for m in rep_meta),',
     'controls["G-draw"] = {"pass": True,', "Controls.test_g_draw_fires_on_one_failed_replica"),
    ("the bars' sha256 unchecked", R, "    if G.sha256(bars_path) != bars_sha:\n", "    if False:\n",
     "Readings.test_the_order_guard_and_the_bars_identity"),
    ("the bars' products unchecked", R, '    if paired.digest() != bars_rec["products_digest"]:\n', "    if False:\n",
     "Readings.test_the_order_guard_and_the_bars_identity"),
    # the audit's C1-C3 (the director, 2026-11-05)
    ("a failed control flagged and the run continued", R, "    if failed:  # §3.3", "    if False:  # §3.3",
     "Controls.test_a_failed_control_stops_the_run_with_no_readings"),
    ("the bars' reader and config unchecked", R,
     '    if (bars_rec.get("reader_sha256"), bars_rec.get("config_sha256")) != (G.sha256(Path(__file__).resolve()),',
     '    if False and (bars_rec.get("reader_sha256"), bars_rec.get("config_sha256")) != (G.sha256(Path(__file__).resolve()),',
     "Readings.test_bars_from_another_reader_or_config_are_refused"),
    ("a unit skipped whatever its verdict", D, '        if verdict == "PASS":\n            return 0',
     "        if True:\n            return 0", "Units.test_a_unit_that_failed_g_draw_is_never_done"),
    ("the batch covariance centred unweighted", R,
     "    Z = Y - (w[None, :, None] * Y).sum(axis=1, keepdims=True) / w.sum()",
     "    Z = Y - Y.mean(axis=1, keepdims=True)", "Readings.test_the_batch_weighted_covariance_is_s1s_mat_cov"),
    ("gibu1 run outside IBU-1's environment", D, "        if not ok:\n            print(f\"refusing: gibu1",
     "        if False:\n            print(f\"refusing: gibu1", "Units.test_gibu1_runs_only_in_ibu1s_environment"),
    # per pairing key
    ("replica b paired with (e)'s b+1", R, 'Path(ep["replica"].format(b=b, j=self.offset + b))',
     'Path(ep["replica"].format(b=b % 50 + 1, j=self.offset + b % 50 + 1))',
     "Readings.test_r1_reads_agree_on_no_difference_and_differ_on_a_large_one"),
    ("a universe paired with another index", R, 'Path(ep["universe"].format(tag=t.replace(":", "_")))',
     'Path(ep["universe"].format(tag=t.replace(":", "_").replace("_1", "_0")))',
     "Readings.test_r1_reads_agree_on_no_difference_and_differ_on_a_large_one"),
    # REF-G1-ADDENDUM-A1 (the director, 2026-11-05): REQUIRED
    ("gibu1 run in another thread environment", D, '    same = same and env["thread_env"] == want["thread_env"]',
     "    same = same", "Units.test_gibu1_runs_only_in_ibu1s_environment"),
    ("gibu1 run at another CPU count", D, '    same = same and env["cpus"] == int(want["cpus"])', "    same = same",
     "Units.test_gibu1_runs_only_in_ibu1s_environment"),
    ("a plain read where O_NOATIME is absent", D, '    flag = getattr(os, "O_NOATIME", None)',
     '    flag = getattr(os, "O_NOATIME", 0)', "Reads.test_o_noatime_absent_is_refused"),
    ("the audit hook on Python opens disabled", D, '    if event != "open" or not _READS["active"]:', "    if True:",
     "Reads.test_the_audit_guard_fires_on_a_plain_read_and_is_silent_otherwise"),
    ("the TFile guard admitting opens outside its roots", D, "        if not any(under(path, r) for r in roots):",
     "        if False:", "Reads.test_the_tfile_guard_refuses_root_reads_outside_the_roots"),
    ("a staging directory reused", D, "            self.root.mkdir(parents=True)",
     "            self.root.mkdir(parents=True, exist_ok=True)", "Reads.test_a_staging_directory_is_new"),
    ("D1: the bank's cv.npz read in place", D,
     'np.load(self.staged(Path(self.cfg["inputs"]["bank"]) / "cv.npz"), allow_pickle=True)',
     'np.load(Path(self.cfg["inputs"]["bank"]) / "cv.npz", allow_pickle=True)',
     "Units.test_a_detector_universe_through_the_bank_parsers"),
    ("D2: a universe's weights read in place", D, "            w = self.lib.uni.weights(sdir, tag)",
     "            w = self.lib.uni.weights(wdir, tag)", "Units.test_a_detector_universe_through_the_bank_parsers"),
    ("D3: the flux constraint read in place", R,
     '    wflux = lib.s1a.flux_weights(staged(cfg["inputs"]["flux_constraint"]))',
     '    wflux = lib.s1a.flux_weights(Path(cfg["inputs"]["flux_constraint"]))', "Reads.test_the_constraint_is_read_as_a_copy"),
    ("D5: the units load the original inputs", D,
     '        npz, bkg_path = staged(cfg["inputs"]["of_inputs_5d"]), staged(cfg["inputs"]["bkg_dump"])',
     '        npz, bkg_path = Path(cfg["inputs"]["of_inputs_5d"]), Path(cfg["inputs"]["bkg_dump"])',
     "Reads.test_the_units_load_the_staged_inputs"),
    ("D6: a ratio read in place", D, "    ratio = json.loads(p.read_text())", "    ratio = json.loads(src.read_text())",
     "Units.test_vertex_and_closure_read_the_pinned_ratio"),
    ("D8: the (e) central read in place", R, '    x_e = e_cells(staged(ep["central"]), U)',
     '    x_e = e_cells(Path(ep["central"]), U)', "Reads.test_the_reader_stages_its_declared_set_and_the_digest_is_unchanged"),
    ("D8: IBU-1's D_N read in place", R, "    b, _ = load(b_path)", '    b, _ = load(Path(ref["path"]))',
     "Reads.test_the_reader_stages_its_declared_set_and_the_digest_is_unchanged"),
    ("the gibu1 product's pin unchecked", R, '    if staged.sha[own["path"]] != own["sha256"]:', "    if False:",
     "Controls.test_g_ibu1_fires_on_either_variant_and_on_the_pin"),
    ("the read without the gibu1 product pinned", R,
     '    if not (cfg["gibu1_product"]["path"] and cfg["gibu1_product"]["sha256"]):', "    if False:",
     "Reads.test_the_read_refuses_until_the_gibu1_product_is_pinned"),
]
# Equivalent mutants: each runs once against the whole suite and must survive, so the label is measured, not only
# declared (REF-G1 §7; the director, 2026-11-05). A kill refutes its proof.
#
# Jitter skipped (coverage-5b-audit's proof, recorded in §7): (e)'s loop refuses any jitter that changes fine-grid
# membership (s5p_numerics.py:174, 186-191), and g1's builder applies the same refusal. On every admitted input the
# jitter therefore changes no reco- or truth-cell assignment, so nothing G-draw compares (the keep masks, obs_counts,
# the MC Poisson factors, tmpl_w) and nothing IBU returns can change.
#
# The jitter seed not (e)'s (offset + b + 1 for offset + b): the same proof, for any seed. Membership is invariant
# under every admitted jitter, so which admitted jitter is drawn cannot change a cell; and the Poisson draws depend
# on the bootstrap seed b alone (s5n_pseudo.bootstrap_replica). The pairing that matters, the bootstrap seed b, is
# killed: "replica b paired with (e)'s b+1" above, via G-pair's seed check.
EXPECTED_SURVIVORS = [
    ("the jitter step skipped in g1's builder", D, "    ji, jb = lib.num.jittered(inputs, bkg, offset + b)\n    moved",
     "    ji, jb = lib.num.jittered(inputs, bkg, None)\n    moved"),
    ("the IBU replica's jitter seed not (e)'s", D, "    ji, jb = lib.num.jittered(inputs, bkg, offset + b)\n    moved",
     "    ji, jb = lib.num.jittered(inputs, bkg, offset + b + 1)\n    moved"),
]

REQUIRED_SURVIVORS = {"the jitter step skipped in g1's builder", "the IBU replica's jitter seed not (e)'s"}


def digest(name: str) -> str:
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()


def run(tests: list[str]) -> tuple[int, str]:
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    p = subprocess.run([sys.executable, "-B", str(TEST), *tests], capture_output=True, text=True, cwd=str(HERE.parent),
                       env=env)
    return p.returncode, p.stdout + p.stderr


def failing(out: str) -> set[str]:
    return {f"{c}.{t}" for t, c in re.findall(r"^(?:FAIL|ERROR): (\w+) \(\w+\.(\w+)\.\w+\)", out, re.M)}


def mutate(fname: str, old: str, new: str, tests: list[str]) -> tuple[int, str] | None:
    path = HERE / fname
    src = path.read_text()
    if src.count(old) != 1:
        return None
    try:
        path.write_text(src.replace(old, new))
        return run(tests)
    finally:
        path.write_text(src)


def main() -> int:
    before = {f: digest(f) for f in (D, R)}
    rc, out = run([])
    ran = re.search(r"^Ran (\d+) tests?", out, re.M)
    if rc != 0 or not ran or int(ran.group(1)) != EXPECTED_TESTS:
        print(f"UNMUTATED SUITE: rc {rc}, ran {ran.group(1) if ran else '?'} of {EXPECTED_TESTS} expected tests\n" + out[-2000:])
        return 1
    ok = True
    for label, fname, old, new, test in MUTATIONS:
        res = mutate(fname, old, new, [test])
        if res is None:
            print(f"MUTATION NOT APPLIED  {label}: anchor does not occur exactly once")
            ok = False
            continue
        killed = test in failing(res[1])
        ok &= killed
        print(f"{'KILLED' if killed else 'SURVIVED':8s}  {label:48s} by {test}")
    missing = REQUIRED_SURVIVORS - {label for label, *_ in EXPECTED_SURVIVORS}
    if missing:
        print(f"EXPECTED SURVIVOR missing from the list: {sorted(missing)}")
        ok = False
    for label, fname, old, new in EXPECTED_SURVIVORS:
        res = mutate(fname, old, new, [])
        if res is None:
            print(f"EXPECTED SURVIVOR NOT APPLIED  {label}")
            ok = False
            continue
        ran = re.search(r"^Ran (\d+) tests?", res[1], re.M)
        survived = res[0] == 0 and ran is not None and int(ran.group(1)) == EXPECTED_TESTS
        ok &= survived
        print(f"{'SURVIVED (expected; equivalent)' if survived else 'KILLED (refutes the equivalence proof)':40s}  {label}"
              + ("" if survived else f"  (failing: {sorted(failing(res[1]))})"))
    after = {f: digest(f) for f in (D, R)}
    if after != before:
        print("MODULES NOT RESTORED:", {f for f in before if before[f] != after[f]})
        return 1
    print("MUTATION CHECK ::", "PASS" if ok else "FAIL",
          f"({len(MUTATIONS)} mutations, {len(EXPECTED_SURVIVORS)} expected survivors)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
