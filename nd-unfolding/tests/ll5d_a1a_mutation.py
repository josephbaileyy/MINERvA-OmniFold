"""Mutation check of LL5D amendment A1a's tests (LL5D-DECLARATION.md section 12, "each with a mutant that a test must
kill"; the director's rulings on A1, 2026-11-08: m2-a to m2-f, the RSS low and the all-path equality, REQUIRED).

Each mutation plants one defect in a temporary copy of ll5d.py, placed first on sys.path, and runs the NAMED test. The
mutation must make that test fail. Exit 0 only if every mutation is killed and the unmutated suite runs all
EXPECTED_TESTS and passes; the receipt line per mutation is printed, with the copy's sha256.

    python3 -B nd-unfolding/tests/ll5d_a1a_mutation.py
"""
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ND = Path(__file__).resolve().parents[1]
TESTS = ND / "tests"
TEST = TESTS / "test_ll5d.py"
SRC = ND / "ll5d.py"
EXPECTED_TESTS = 69

MUTATIONS = [
    # --- section 12's REQUIRED list (A1a's part)
    ("REQ per-row first order drops the reference", "        acc += Vq[c, sel] - r\n", "        acc += Vq[c, sel]\n",
     "Composition.test_first_order_in_draw_order"),
    ("REQ k = 1 aliases the universe", "    acc = Vq[cols[0], sel].copy()\n", "    acc = Vq[cols[0], sel]\n",
     "Composition.test_k1_is_the_universe_bitwise"),
    ("REQ the tdw reference is not tdw_ref",
     '            rows["tdw"][i] = zero["tdw"] if "tdw" in zero else world["tdw_ref"]',
     '            rows["tdw"][i] = zero["tdw"] if "tdw" in zero else np.ones_like(world["tdw_ref"])',
     "Builders.test_detector_rows_carry_tdw_ref_and_enter_with_zero_departure"),
    ("REQ the denominator tree is not clipped", "    wtp, tdp = np.maximum(wt, 0.0), np.maximum(tdw, 0.0)",
     "    wtp, tdp = np.maximum(wt, 0.0), tdw", "Clip.test_each_tree_is_clipped_on_its_own_composite_and_nowhere_else"),
    ("REQ the denominator can go negative", "    wtp, tdp = np.maximum(wt, 0.0), np.maximum(tdw, 0.0)",
     "    wtp, tdp = np.maximum(wt, 0.0), tdw - 0.0",
     "Clip.test_the_denominator_is_never_negative_under_adversarial_composites"),
    ("REQ D1 tolerates one ULP", "        elif not np.array_equal(arr, ref):", "        elif not np.allclose(arr, ref):",
     "Denominator.test_d1_fires_on_one_ulp"),
    ("REQ D2 total edge widened", "tot <= DENOM_TOTAL_TOL", "tot <= 10 * DENOM_TOTAL_TOL",
     "Denominator.test_d2_at_its_total_edge"),
    ("REQ D2 cell edge widened", "dev <= DENOM_CELL_TOL", "dev <= 2 * DENOM_CELL_TOL",
     "Denominator.test_d2_at_its_cell_edge"),
    ("REQ D2 ignores the support", '"passes": bool(same_support and tot', '"passes": bool(True and tot',
     "Denominator.test_d2_fails_on_the_support_alone"),
    ("REQ D3 tolerates one ULP", "        elif not np.array_equal(np.asarray(w[\"denom_nd\"], float), ref):",
     "        elif not np.allclose(np.asarray(w[\"denom_nd\"], float), ref):", "Denominator.test_d3_fires_on_one_ulp"),
    ("REQ T <= 0 misses T = 0", "                bad = np.flatnonzero(~np.isfinite(T16) | (T16 <= 0))",
     "                bad = np.flatnonzero(~np.isfinite(T16) | (T16 < 0))", "Receipt.test_t_le_0_stops_and_halts_at_the_first"),
    ("REQ T <= 0 keeps BLAS's clip sign near zero", "ZERO_REL = 1e-9 ", "ZERO_REL = 0.0 ",
     "Receipt.test_t_le_0_takes_composes_clip_sign_on_near_zero_rows"),
    ("REQ the N1 screen hides a pair past the bound", "        np.maximum(L, lo, out=L)\n",
     "        np.maximum(L, 1e3 * lo, out=L)\n", "Receipt.test_n1_stops"),
    ("REQ the receipt runs on after a STOP", "                    stop = {\"reading\": reading, \"draw\": d, \"seed\": int(seeds[d]), \"reasons\": reasons}\n                    break",
     "                    stop = {\"reading\": reading, \"draw\": d, \"seed\": int(seeds[d]), \"reasons\": reasons}",
     "Receipt.test_t_le_0_stops_and_halts_at_the_first"),
    ("REQ N1 bound loosened", "above, mx = int(np.sum(rr > N1_BOUND)), float(rr.max())", "above, mx = int(np.sum(rr > 100.0)), float(rr.max())",
     "Receipt.test_n1_stops"),
    ("REQ the truth takes the CV's flux", "                phi = phi_u[flux_cols_map[flux_tags[0]]]",
     "                phi = phi_u[0]", "Receipt.test_each_reading_composes_its_own_draw_and_the_truth_takes_phi_u"),
    ("REQ the rule's union is not joint", "        return float(np.mean(np.any([stops[e] for e in EVALUATIONS], axis=0)))",
     "        return float(max(np.mean(stops[e]) for e in EVALUATIONS))",
     "Rule.test_the_union_is_measured_jointly_per_replicate"),
    ("REQ the rule takes any evaluation set", "    if set(R) != set(EVALUATIONS):\n        raise Refusal(f\"the rule is over",
     "    if False:\n        raise Refusal(f\"the rule is over", "Rule.test_the_rule_is_over_exactly_the_four_paired_evaluations"),
    ("REQ a toy seed moved", "TOY_SEEDS = {\"g18\": range(4_751_000, 4_751_300)",
     "TOY_SEEDS = {\"g18\": range(4_751_001, 4_751_301)", "Seeds.test_the_declared_seeds"),
    ("REQ the gate sample skips the toys", "    first = TOY_SEEDS[truth][0]\n", "    first = TOY_SEEDS[truth][0] + 300\n",
     "Seeds.test_the_gate_sample_extends_the_toys_and_cannot_overlap"),
    ("REQ a pinned array read plainly", "def read_pinned_npy(path: Path, want: str) -> np.ndarray:\n    \"\"\"One .npy read once through O_NOATIME, its digest taken over the very bytes loaded.\"\"\"\n    with inv.open_noatime(path) as fh:",
     "def read_pinned_npy(path: Path, want: str) -> np.ndarray:\n    \"\"\"One .npy read once through O_NOATIME, its digest taken over the very bytes loaded.\"\"\"\n    with open(path, \"rb\") as fh:",
     "NoAtime.test_tdw_ref_the_manifest_and_the_universes_are_read_with_o_noatime_only"),
    ("REQ the calibration read plainly", "    with inv.open_noatime(a.calibration) as fh:\n        cal = json.loads",
     "    with open(a.calibration, \"rb\") as fh:\n        cal = json.loads",
     "NoAtime.test_the_calibration_record_is_read_with_o_noatime_only"),
    ("REQ an atime move does not set 8", "    return code | (ATIME_RC if moved else 0)", "    return code",
     "ExitCodes.test_an_atime_move_sets_8"),
    ("REQ more than one BLAS thread accepted", "    if bad:\n        raise Refusal(f\"one BLAS thread",
     "    if False:\n        raise Refusal(f\"one BLAS thread", "ExitCodes.test_one_blas_thread_is_required"),
    # --- m2-a to m2-g (936-C1, the audit's lows, the RSS low)
    ("m2-a minus2 keeps the removed tags", "            [t for t in tags if t.rpartition(\"_\")[0] not in REMOVED])",
     "            list(tags))", "Layouts.test_m2a_minus2_is_s1s_layout_less_exactly_two_bands"),
    ("m2-a removes GEANT_Pion instead", "REMOVED = (\"GEANT_Neutron\", \"GEANT_Proton\")",
     "REMOVED = (\"GEANT_Neutron\", \"GEANT_Pion\")", "Layouts.test_m2a_minus2_is_s1s_layout_less_exactly_two_bands"),
    ("m2-b drop2 keeps one band", "    return [t for t in tags if t.rpartition(\"_\")[0] not in REMOVED]\n",
     "    return [t for t in tags if t.rpartition(\"_\")[0] != REMOVED[0]]\n",
     "Selection.test_m2b_selection_accepts_drop2_and_refuses_a_kept_band"),
    ("m2-c the receipt composes minus2 from the all draw",
     "        dtags = reading_draws(draws_all, reading)\n", "        dtags = [list(x) for x in draws_all]\n",
     "Receipt.test_each_reading_composes_its_own_draw_and_the_truth_takes_phi_u"),
    ("m2-d the minus2 reference over every band", "            v = restrict(P, reading)\n",
     "            v = restrict(P, \"all\")\n", "Builders.test_m2d_the_minus2_reference_is_all_less_the_two_bands_variances"),
    ("m2-e an independent minus2 stream", "        S = selection(draws, reading, v[\"col\"])",
     "        S = selection(calibration_draws(t, s + (reading == \"minus2\"), st[\"flux_p\"], st[\"groups\"], st[\"n\"]), reading, v[\"col\"])",
     "Calibration.test_m2e_each_minus2_replicate_is_the_all_replicates_draws_less_two"),
    ("m2-f the product composition on the nature path", "    nf = int(np.prod(geo[\"shape\"]))\n    wt, tdw = comp[\"wt\"], comp[\"tdw\"]",
     "    toys.source_factors({}, {}, {}, None, None, None, None)\n    nf = int(np.prod(geo[\"shape\"]))\n    wt, tdw = comp[\"wt\"], comp[\"tdw\"]",
     "SourceFactors.test_m2f_the_product_composition_is_off_the_nature_path"),
    ("m2-g restrict copies the row arrays", "            \"phi_single\": P[\"phi_single\"][idx],",
     "            \"phi_single\": P[\"phi_single\"][idx], \"rows\": {k: v.copy() for k, v in (P[\"rows\"] or {}).items()},",
     "Builders.test_m2g_restrict_copies_no_row_array_and_the_zero_columns_are_the_selected_form"),
    # --- the cross terms (REQUIRED, the director's condition 2 on option (B))
    ("XT the product drops the reference", "        prod *= inv_ref\n", "", "CrossTerms.test_the_streamed_product_equals_a21s_crossterm"),
    ("XT a_CV = 0 not first order", "    return np.where(nz, prod, additive)", "    return prod",
     "CrossTerms.test_the_streamed_product_equals_a21s_crossterm"),
    # --- the all-path equality (REQUIRED, the director's ruling on A1)
    ("EQ a Flux universe's Phi_u misplaced", "    phi_single[flux_cols] = phi\n", "    phi_single[flux_cols] = phi[::-1]\n",
     "A21Equality.test_the_all_path_equals_a21s_bitwise"),
    ("EQ reco cells without the reco pass", "    geo = {\"gen\": P[\"cells\"], \"reco\": np.where(prec, flat_cells(np.asarray(inputs[\"MCreco\"], float), edges), -1),",
     "    geo = {\"gen\": P[\"cells\"], \"reco\": flat_cells(np.asarray(inputs[\"MCreco\"], float), edges),",
     "A21Equality.test_the_all_path_equals_a21s_bitwise"),
    # --- the gate's own rules
    ("a failed r_T control read on", "    if not (controls[\"passes\"] and r_ctl[t][\"passes\"]):",
     "    if not controls[\"passes\"]:", "Jobs.test_a_failed_control_is_invalid_before_anything_is_read"),
    ("an incomplete calibration accepted", "        raise Refusal(\"the calibration carries no threshold or backstop SD for every evaluation\")",
     "        pass", "Jobs.test_the_gate_refuses_an_uncalibrated_or_foreign_calibration"),
    ("a failing reading passes", "    ok = all(v == \"option (1)\" for v in rec[\"reads\"].values()) and all(b[\"passes\"] for b in back.values())",
     "    ok = True", "Jobs.test_a_failing_gate_reading_is_a_stop"),
    ("the receipt's projection never reprices", "            if proj > line:\n                raise Reprice(f\"the receipt alone",
     "            if False:\n                raise Reprice(f\"the receipt alone", "Jobs.test_the_receipt_reprices_past_its_line"),
    ("the gate's projection never reprices", "            if proj > line:\n                raise Reprice(f\"the gate projects",
     "            if False:\n                raise Reprice(f\"the gate projects", "Jobs.test_the_gate_reprices_past_its_line"),
    ("the first-300 check skipped", "            if not np.array_equal(qn[k][:, :v.shape[1]], v):",
     "            if False:", "Jobs.test_a_gate_sample_whose_first_300_differ_is_refused"),
    ("N1 stops at exactly the bound", "above, mx = int(np.sum(rr > N1_BOUND)), float(rr.max())",
     "above, mx = int(np.sum(rr >= N1_BOUND)), float(rr.max())", "Receipt.test_n1_at_exactly_the_bound_does_not_stop"),
    ("a reading takes the other reading's thresholds", "        thr = cal[\"rule\"][\"thresholds\"][e]\n",
     "        thr = cal[\"rule\"][\"thresholds\"][f\"{t}/all\"]\n", "Jobs.test_each_evaluation_reads_its_own_thresholds"),
    ("CP the clipmean sums lambda+", "                sig_neg[reco] += np.maximum(-lam, 0.0)",
     "                sig_neg[reco] += np.maximum(lam, 0.0)", "Receipt.test_the_clip_prep_products_equal_a_direct_computation"),
    ("CP the unclipped truth is the clipped one", "                t_unclip.append(U_full @ unclipped_truth(comp, r, geo, phi, const_full))",
     "                t_unclip.append(T16)", "Receipt.test_the_clip_prep_products_equal_a_direct_computation"),
    ("the merge passes on one truth", "    verdict = (\"PASS\" if all(v == \"PASS\" for v in verdicts.values()) else",
     "    verdict = (\"PASS\" if any(v == \"PASS\" for v in verdicts.values()) else", "Merge.test_pass_needs_both"),
]

RUN = ("import runpy, sys; sys.path.insert(0, {tmp!r}); sys.argv = ['test_ll5d.py'] + {names!r}; "
       "runpy.run_path({test!r}, run_name='__main__')")


def run(tmp: str, names: list[str]) -> subprocess.CompletedProcess:
    env = dict(os.environ, PYTHONHASHSEED="0", OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
               NUMEXPR_NUM_THREADS="1")
    return subprocess.run([sys.executable, "-B", "-c", RUN.format(tmp=tmp, names=names, test=str(TEST))],
                          capture_output=True, text=True, env=env, cwd=str(TESTS))


def main() -> int:
    src = SRC.read_text()
    print(f"ll5d.py sha256 {hashlib.sha256(src.encode()).hexdigest()}")
    print(f"test_ll5d.py sha256 {hashlib.sha256(TEST.read_bytes()).hexdigest()}")
    ok = True
    with tempfile.TemporaryDirectory(prefix="ll5d-mut-") as tmp:
        shutil.copy(SRC, Path(tmp) / "ll5d.py")
        base = run(tmp, [])
        m = re.search(r"Ran (\d+) tests", base.stderr)
        n = int(m.group(1)) if m else -1
        base_ok = base.returncode == 0 and n == EXPECTED_TESTS
        print(f"UNMUTATED {'PASS' if base_ok else 'FAIL'} tests={n} expected={EXPECTED_TESTS} rc={base.returncode}")
        ok &= base_ok
        for name, old, new, test in MUTATIONS:
            if src.count(old) != 1:
                print(f"MUTATION NOT-APPLICABLE {name}: the anchor occurs {src.count(old)} times")
                ok = False
                continue
            mutated = src.replace(old, new)
            (Path(tmp) / "ll5d.py").write_text(mutated)
            p = run(tmp, [test])
            killed = p.returncode != 0
            print(f"MUTATION {'KILLED' if killed else 'SURVIVED'} {name} [{test}] "
                  f"sha256={hashlib.sha256(mutated.encode()).hexdigest()[:16]}")
            ok &= killed
        (Path(tmp) / "ll5d.py").write_text(src)
    print("ALL-KILLED" if ok else "MUTATION-CHECK FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
