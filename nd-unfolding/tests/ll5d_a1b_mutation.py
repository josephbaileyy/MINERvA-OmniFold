"""Mutation check of LL5D amendment A1b's tests (LL5D-DECLARATION.md section 12; the director's rulings on A1b,
2026-11-08: the weakened label's mutants (<=, 0.85, 0.95, a wrong evaluation's r_c), the allowlist, the sealed
consumer). Each mutation plants one defect in a temporary copy of ll5d_b.py, placed first on sys.path, and runs the NAMED
test, which must fail. Exit 0 only if every mutation is killed and the unmutated suite runs all EXPECTED_TESTS and passes.

    python3 -B nd-unfolding/tests/ll5d_a1b_mutation.py
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
TEST = TESTS / "test_ll5d_b.py"
SRC = ND / "ll5d_b.py"
EXPECTED_TESTS = 29

MUTATIONS = [
    # --- the weakened label (the director's REQUIRED mutants)
    ("WK <= in place of <", "float(ratio[c]) < WEAK_RATIO]", "float(ratio[c]) <= WEAK_RATIO]", "Weakened.test_strictly_below_0_9"),
    ("WK 0.85", "WEAK_RATIO = 0.9 ", "WEAK_RATIO = 0.85 ", "Weakened.test_strictly_below_0_9"),
    ("WK 0.95", "WEAK_RATIO = 0.9 ", "WEAK_RATIO = 0.95 ", "Weakened.test_strictly_below_0_9"),
    ("WK a wrong evaluation's r_c", "minus, ratios[e], clip, X_true", "minus, ratios[f\"{a.truth}/all\"], clip, X_true",
     "Pipeline.test_each_reading_takes_its_own_ratio_for_the_weakened_label"),
    ("WK the label moves the verdict", "        \"grade\": g, \"verdict\": g[\"verdict\"],",
     "        \"grade\": g, \"verdict\": \"UNDER-COVERS\" if weakened(g[\"cell_flag\"], ratio).get(\"weakened_cells\") else g[\"verdict\"],",
     "Pipeline.test_the_weakened_label_moves_no_verdict"),
    ("WK another gate key read", "    seen = {k: g[k] for k in GATE_KEYS if k in g}\n",
     "    seen = {k: g[k] for k in GATE_KEYS if k in g}\n    _ = g.get(\"receipt\")\n",
     "Pipeline.test_the_gate_record_is_read_only_through_its_allowlist"),
    # --- the nature (sections 3.3-3.4, 10)
    ("NA the reference dropped", "                acc[q] += a - refs[q]\n", "                acc[q] += a\n",
     "Nature.test_compose_order_and_each_tree_clipped_on_its_own_composite"),
    ("NA a detector's tdw not tdw_ref", "\"tdw\": np.asarray(zero[\"tdw\"], float) if \"tdw\" in zero else refs[\"tdw\"]}",
     "\"tdw\": np.asarray(zero[\"tdw\"], float) if \"tdw\" in zero else np.ones_like(refs[\"tdw\"])}",
     "Nature.test_k1_gives_universe_inputs_arrays_bitwise"),
    ("NA the truth tree unclipped", "    wtp, tdp = np.maximum(acc[\"wt\"], 0.0), np.maximum(acc[\"tdw\"], 0.0)",
     "    wtp, tdp = acc[\"wt\"], np.maximum(acc[\"tdw\"], 0.0)",
     "Nature.test_compose_order_and_each_tree_clipped_on_its_own_composite"),
    ("NA the truth takes Phi_CV", "flux=phis[0] if phis else np.asarray(inputs[\"flux\"], float))",
     "flux=np.asarray(inputs[\"flux\"], float))", "Nature.test_the_toys_truth_is_the_receipts_and_takes_phi_u"),
    ("NA a toy ignores its reading", "        tags = ll5d.reading_draws([mc.draw_universes(d)], reading)[0]\n",
     "        tags = mc.draw_universes(d)\n", "Unfold.test_each_role_writes_its_arrays"),
    ("NA the stat seed is 1B's", "exp = mc.stat_experiment(inputs, bkg, r, ll5d.STAT_SEED[t], b)",
     "exp = mc.stat_experiment(inputs, bkg, r, mc.STAT_SEED[t], b)", "Unfold.test_each_role_writes_its_arrays"),
    ("NA r_T unchecked", "    if not ctl[t][\"passes\"]:\n", "    if False:\n", "Unfold.test_r_t_must_be_positive_everywhere"),
    # --- section 5.3, the sealed consumer
    ("CM the mean is a sum", "    sig = np.asarray(cp[f\"signal_negative_lambda_sum_{reading}\"], float) / N_DECLARED",
     "    sig = np.asarray(cp[f\"signal_negative_lambda_sum_{reading}\"], float)",
     "Unfold.test_the_clipmean_adds_the_mean_clipped_mass_and_reads_only_the_sealed_digest"),
    ("CM the seal's digest unchecked", "    if hashlib.sha256(raw).hexdigest() != want_sha256:\n        raise Refusal(f\"{path}: the clip-prep",
     "    if False:\n        raise Refusal(f\"{path}: the clip-prep",
     "Unfold.test_the_clipmean_adds_the_mean_clipped_mass_and_reads_only_the_sealed_digest"),
    ("CM the seal read plainly", "def read_clip_prep(path: Path, want_sha256: str) -> dict:\n    \"\"\"The gate's sealed clip-prep products (A1a section 5j), read once through O_NOATIME by the digest the gate record\n    gives; a mismatch refuses. Only section 5.3's consumers (clipmean, clipcheck) call this.\"\"\"\n    with inv.open_noatime(path) as fh:",
     "def read_clip_prep(path: Path, want_sha256: str) -> dict:\n    \"\"\"The gate's sealed clip-prep products (A1a section 5j), read once through O_NOATIME by the digest the gate record\n    gives; a mismatch refuses. Only section 5.3's consumers (clipmean, clipcheck) call this.\"\"\"\n    with open(path, \"rb\") as fh:",
     "NoAtime.test_the_clip_prep_the_gate_and_the_products_are_read_with_o_noatime_only"),
    ("CC tau added", "    o = unfold_shift / sigma - tau\n", "    o = unfold_shift / sigma + tau\n",
     "ClipOffset.test_the_offset_is_the_unfolds_shift_less_the_truths"),
    ("CC delta* strict", "if abs(o[c]) >= CLIP_DELTA_STAR]", "if abs(o[c]) > CLIP_DELTA_STAR]", "ClipOffset.test_delta_star_is_at_or_above"),
    # --- walls, the blocks, the null, the grade
    ("WA the unit strict", "    ok = s_max <= UNIT_SECONDS and r_max <= RSS_LIMIT_KIB",
     "    ok = s_max < UNIT_SECONDS and r_max <= RSS_LIMIT_KIB", "Walls.test_the_unit_and_the_limit_both_ways"),
    ("BL minus2 keeps every band", "    return [b for b in sa.EXPECT if b in bands]", "    return list(sa.EXPECT)",
     "Pipeline.test_minus2_rebuilds_without_the_two_bands_and_the_removal_is_exact"),
    ("BL the removal tolerance loosened", "REMOVAL_TOL = 1e-12 ", "REMOVAL_TOL = 1e-6 ",
     "Pipeline.test_minus2_rebuilds_without_the_two_bands_and_the_removal_is_exact"),
    ("NU 1B's null seed", "                                    seed=ll5d.NULL_SEED[e])",
     "                                    seed=fn.NULL_SEED)", "Pipeline.test_the_null_is_per_reading_at_the_declared_seeds"),
    ("GR the reading rule's bound doubled", "    ok = fin(k) and fin(tol) and fin(mrd) and mrd <= tol and cmp.get(\"tol\") == tol",
     "    ok = fin(k) and fin(tol) and fin(mrd) and mrd <= 2 * tol and cmp.get(\"tol\") == tol",
     "CholeskyRule.test_the_rule_both_ways"),
    ("GR the grade's own tol unchecked", "    ok = fin(k) and fin(tol) and fin(mrd) and mrd <= tol and cmp.get(\"tol\") == tol",
     "    ok = fin(k) and fin(tol) and fin(mrd) and mrd <= tol", "CholeskyRule.test_the_rule_both_ways"),
    ("EX a refusal is not INVALID", "    except (Refusal, ll5d.Refusal, mc.Refusal, inv.Refusal, toys.Refusal) as exc:",
     "    except (KeyError,) as exc:", "ExitCodes.test_a_refusal_is_invalid_with_its_record"),
    ("A1a.1 run_unfold installs no candidate", "    s5e_candidate.install(toys.CONFIG)\n", "",
     "RealUnfold.test_run_unfold_runs_every_role_over_the_real_chain"),
    ("GR A5's tolerance without its factor 10", "\"tol\": max(1e-9, 10 * kappa * eps)}",
     "\"tol\": max(1e-9, kappa * eps)}", "CholeskyRule.test_the_tolerance_is_a5s"),
]

RUN = ("import runpy, sys; sys.path.insert(0, {tmp!r}); sys.argv = ['test_ll5d_b.py'] + {names!r}; "
       "runpy.run_path({test!r}, run_name='__main__')")


def run(tmp: str, names: list) -> subprocess.CompletedProcess:
    env = dict(os.environ, PYTHONHASHSEED="0", OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
               NUMEXPR_NUM_THREADS="1")
    return subprocess.run([sys.executable, "-B", "-c", RUN.format(tmp=tmp, names=names, test=str(TEST))],
                          capture_output=True, text=True, env=env, cwd=str(TESTS))


def main() -> int:
    src = SRC.read_text()
    print(f"ll5d_b.py sha256 {hashlib.sha256(src.encode()).hexdigest()}")
    print(f"test_ll5d_b.py sha256 {hashlib.sha256(TEST.read_bytes()).hexdigest()}")
    ok = True
    with tempfile.TemporaryDirectory(prefix="ll5d-b-mut-") as tmp:
        shutil.copy(SRC, Path(tmp) / "ll5d_b.py")
        base = run(tmp, [])
        m = re.search(r"Ran (\d+) tests", base.stderr)
        n = int(m.group(1)) if m else -1
        skipped = "skipped" in base.stderr
        base_ok = base.returncode == 0 and n == EXPECTED_TESTS and not skipped
        print(f"UNMUTATED {'PASS' if base_ok else 'FAIL'} tests={n} expected={EXPECTED_TESTS} skipped={skipped} "
              f"rc={base.returncode}")
        ok &= base_ok
        for name, old, new, test in MUTATIONS:
            if src.count(old) != 1:
                print(f"MUTATION NOT-APPLICABLE {name}: the anchor occurs {src.count(old)} times")
                ok = False
                continue
            mutated = src.replace(old, new)
            (Path(tmp) / "ll5d_b.py").write_text(mutated)
            p = run(tmp, [test])
            killed = p.returncode != 0
            print(f"MUTATION {'KILLED' if killed else 'SURVIVED'} {name} [{test}] "
                  f"sha256={hashlib.sha256(mutated.encode()).hexdigest()[:16]}")
            ok &= killed
    print("ALL-KILLED" if ok else "MUTATION-CHECK FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
