#!/usr/bin/env python3
"""Mutation check of RDX's tests (RDX-DECLARATION.md §2, D6), with RSN's harness (rsn_mutation.py).

Each mutation plants one declared defect in a copy of one RDX file and must make the NAMED test fail, not merely some
test. The copy runs in a temporary tree that mirrors the repository: rdx/ holds real copies of the RDX files (the
mutated one among them), and every other entry is a symlink to the real file. Exit 0 only if the unmutated suite
passes with the expected test count and every mutation is killed by its named test. D6's two declared mutants (a
one-row offset of truthx, and the mask applied to truthx alone) are tests that run through the sidecar path
(test_mutant_d6a_*, test_mutant_d6b_*); the mutants below that disable the join's truthx comparison must be killed by
them.

    python3 -B nd-unfolding/rdx/rdx_mutation.py [--only LABEL_SUBSTRING] [--jobs N]
"""
import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ND = HERE.parent
REPO = ND.parent
FILES = ("runEventLoopOmniFold-truthx.patch", "rdx_unfold.py", "rdx_dump.py", "rdx_truthx_npz.py",
         "rdx_truthx_rows.py", "rdx_align.py", "rdx_provenance.py", "rdx_common.py", "test_rdx.py")
P, UF, DP, TN, TR, AL, PV, RC = FILES[:8]
EXPECTED_TESTS = 34
MUTATIONS = [
    # --- C1, the event-loop patch (only '+' lines change, so every mutant still applies)
    ("miss rows keep truthx_enu at 0", P, "+        miss_rdx_enu = tde.rdx_enu; miss_rdx_vtx_x = tde.rdx_vtx_x;",
     "+        miss_rdx_vtx_x = tde.rdx_vtx_x;",
     "test_the_patch_fills_denom_reco_and_miss_rows_and_refuses_both_gates"),
    ("truthx_enu not cached", P, "+        tde.rdx_enu = rdx_enu; tde.rdx_vtx_x = rdx_vtx_x; tde.rdx_vtx_y = rdx_vtx_y;",
     "+        tde.rdx_vtx_x = rdx_vtx_x; tde.rdx_vtx_y = rdx_vtx_y;",
     "test_the_patch_fills_denom_reco_and_miss_rows_and_refuses_both_gates"),
    ("truthx_enu left to the #12 rebind", P, '+        "truthx_enu", "truthx_vtx_x", "truthx_vtx_y", "truthx_vtx_z",',
     '+        "truthx_vtx_x", "truthx_vtx_y", "truthx_vtx_z",',
     "test_the_patch_fills_denom_reco_and_miss_rows_and_refuses_both_gates"),
    ("proton mass 938.0", P, "E[i] - 938.272 > best) best = E[i] - 938.272;", "E[i] - 938.0 > best) best = E[i] - 938.0;",
     "test_the_patch_fills_denom_reco_and_miss_rows_and_refuses_both_gates"),
    ("KE is the total energy", P, "best) best = E[i] - 938.272;", "best) best = E[i];",
     "test_the_patch_fills_denom_reco_and_miss_rows_and_refuses_both_gates"),
    ("denom fill ungated", P, "+    if(dumpTruthx)\n+    {\n+      rdx_enu = truthCV->GetEnuTrue();",
     "+    if(true)\n+    {\n+      rdx_enu = truthCV->GetEnuTrue();", "test_every_added_line_is_gated_or_a_declared_declaration"),
    ("reco fill in reco mode", P, "+        CVUniverse::SetTruth(true);\n+        rdx_enu = recoCV->GetEnuTrue();",
     "+        // reco mode\n+        rdx_enu = recoCV->GetEnuTrue();",
     "test_the_patch_fills_denom_reco_and_miss_rows_and_refuses_both_gates"),
    ("both gates allowed", P, "+    return badCmdLine;", "+    (void)0;",
     "test_the_patch_fills_denom_reco_and_miss_rows_and_refuses_both_gates"),
    ("miss identity zeroed", P, "+        miss_rdx_run = tde.id_run; miss_rdx_subrun = tde.id_subrun;",
     "+        miss_rdx_run = 0; miss_rdx_subrun = tde.id_subrun;",
     "test_the_patch_fills_denom_reco_and_miss_rows_and_refuses_both_gates"),
    # --- C3, the widened regressor
    ("predict not widened", UF, 'return inner_pred(widen(X, tx_pred, "predict") if tx is not None else X)',
     "return inner_pred(X)", "test_the_wide_regressor_sees_truthx_aligned_to_the_loops_fit_and_predict_rows"),
    ("fit widened with the wrong rows", UF, 'Xw = widen(X, tx_fit, "fit") if tx is not None else np.asarray(X)',
     'Xw = widen(X, txm[:len(X)], "fit") if tx is not None else np.asarray(X)',
     "test_the_wide_regressor_sees_truthx_aligned_to_the_loops_fit_and_predict_rows"),
    ("truthx not subset by pass_truth", UF, "            txm = tx[m]\n", "            txm = tx[:int(m.sum())]\n",
     "test_the_wide_regressor_sees_truthx_aligned_to_the_loops_fit_and_predict_rows"),
    ("sidecar row count unchecked", UF, 'if len(tx) != len(d["MCgen"]):', "if False:",
     "test_a_sidecar_with_the_wrong_row_count_refuses"),
    ("permutation not joint", UF, "return tx[np.random.default_rng(seed).permutation(len(tx))]",
     "return np.column_stack([c[np.random.default_rng(seed + i).permutation(len(tx))] for i, c in enumerate(tx.T)])",
     "test_the_permutation_is_joint_seeded_and_deterministic"),
    ("transfer seed RSN's", UF, "TRANSFER_SEED, TRANSFER_FRACTION = 20261112, RSN.TRANSFER_FRACTION",
     "TRANSFER_SEED, TRANSFER_FRACTION = 20261111, RSN.TRANSFER_FRACTION",
     "test_the_transfer_probe_uses_rdx_mask_and_the_widened_rows"),
    ("transfer probe not widened", UF, "probe.fit(Xw[~mk], y_[~mk])", "probe.fit(np.asarray(X)[~mk], y_[~mk])",
     "test_the_transfer_probe_uses_rdx_mask_and_the_widened_rows"),
    ("sidecar npz sha unchecked", UF, 'if meta.get("npz_sha256") != L.sha256_path(npz):', "if False:",
     "test_the_sidecar_refusals"),
    ("sidecar dtype unchecked", UF, "if tx.dtype != np.float64 or tx.ndim != 2", "if tx.ndim != 2",
     "test_the_sidecar_refusals"),
    ("permute allowed with std", UF, "if a.truthx_permute is not None and not wide:", "if False:",
     "test_the_argument_refusals"),
    ("truth without closure", UF, 'if a.truth != "ratio" and "--closure" not in rest:', "if False:",
     "test_the_argument_refusals"),
    # --- C2, the replica kept-row walk and the sidecar
    ("replica keeps bad weights", DP,
     "if not (math.isfinite(wt) and math.isfinite(wr) and 0 <= wt < 1e4 and 0 <= wr < 1e4):", "if False:",
     "test_the_replica_equals_the_collector_row_for_row"),
    ("replica skips the extras' finiteness", DP,
     "if not (math.isfinite(a_pt) and math.isfinite(a_pz) and all(math.isfinite(v) for v in truth_vals)):",
     "if not (math.isfinite(a_pt) and math.isfinite(a_pz)):", "test_the_replica_equals_the_collector_row_for_row"),
    ("replica not POT-scaled", DP, "        wt *= pot_scale\n", "", "test_the_replica_equals_the_collector_row_for_row"),
    ("replica drops reco-only rows", DP, "if not (tru_ok or (passed and rec_ok)):", "if not tru_ok:",
     "test_the_replica_equals_the_collector_row_for_row"),
    ("npz check skipped in the build", DP, "        check_against_npz(arrays, z)\n", "        pass\n",
     "test_the_build_refuses_an_npz_the_replica_does_not_reproduce"),
    ("npz dtype ignored", DP, "if a.shape != b.shape or a.dtype != b.dtype or not np.array_equal(a, b):",
     "if a.shape != b.shape or not np.array_equal(a, b):", "test_a_replica_that_differs_from_the_npz_refuses"),
    ("truthx at the first rows, not the kept ones", DP,
     "tx = np.column_stack([np.asarray(c[nm], np.float64)[ent] for nm in TRUTHX])",
     "tx = np.column_stack([np.asarray(c[nm], np.float64)[:len(ent)] for nm in TRUTHX])",
     "test_the_sidecar_joins_back_to_every_playlist_row"),
    ("truthx cast to float32", DP, "tx = np.column_stack([np.asarray(c[nm], np.float64)[ent] for nm in TRUTHX])",
     "tx = np.column_stack([np.asarray(c[nm], np.float32)[ent] for nm in TRUTHX])",
     "test_the_sidecar_joins_back_to_every_playlist_row"),
    ("a run in two playlists allowed", DP, '                raise DumpError(f"run {r} appears in playlists {owner[r]} and {k}")',
     "                pass", "test_the_playlist_index_and_its_refusals"),
    ("an unknown run allowed", DP, '            raise DumpError(f"row {i}: run {r} is in no per-playlist omnifile")',
     "            out[i] = -1\n            continue", "test_the_playlist_index_and_its_refusals"),
    # --- C-TRUTHX-NPZ, the per-row join (D6)
    ("join ignores truthx (offset)", TN,
     '**{k: int((np.asarray(c[k], np.float64)[jj] != tx[r, i]).sum()) for i, k in enumerate(C.TRUTHX)},', "",
     "test_mutant_d6a_truthx_offset_by_one_row_fails_the_join"),
    ("join ignores truthx (mask)", TN,
     '**{k: int((np.asarray(c[k], np.float64)[jj] != tx[r, i]).sum()) for i, k in enumerate(C.TRUTHX)},', "",
     "test_mutant_d6b_mask_on_truthx_alone_fails_the_join"),
    ("mc_id uniqueness unchecked", TN, "if np.unique(full).size != n:", "if False:",
     "test_a_sidecar_for_another_npz_or_with_duplicate_ids_refuses"),
    ("w_truth not compared", TN, '"w_truth": int((np.asarray(c["w_truth"], np.float64)[jj] * pot != w[r]).sum()),',
     '"w_truth": 0,', "test_a_weight_or_coordinate_mismatch_fails_the_join"),
    ("join npz sha unchecked", TN, 'if meta.get("npz_sha256") != C.sha256(npz):', "if False:",
     "test_a_sidecar_for_another_npz_or_with_duplicate_ids_refuses"),
    ("MC compared uncast", TN, '"MC": int((np.asarray(c["MC"], np.float64)[jj].astype(np.float32) != gen[r, 0]).sum()),',
     '"MC": int((np.asarray(c["MC"], np.float64)[jj] != gen[r, 0]).sum()),',
     "test_the_sidecar_joins_back_to_every_playlist_row"),
    # --- C-TRUTHX, C-ALIGN, provenance, keys
    ("partnerless rows allowed", TR, "    if partnerless:\n", "    if False:\n",
     "test_a_zeroed_miss_row_a_partnerless_row_and_a_bad_enu_fail"),
    ("matched rows not compared", TR, "diff = int((a[ok] != np.asarray(den[k], np.float64)[j[ok]]).sum())", "diff = 0",
     "test_a_zeroed_miss_row_a_partnerless_row_and_a_bad_enu_fail"),
    ("enu positivity unchecked", TR, 'if np.any(~(np.asarray(cols["truthx_enu"], np.float64) > 0)):', "if False:",
     "test_a_zeroed_miss_row_a_partnerless_row_and_a_bad_enu_fail"),
    ("extra branches unchecked", AL, "        if extra != want:\n", "        if False:\n", "test_the_align_refusals"),
    ("values not compared", AL, "            if not same(ca[k], cb[k]):\n", "            if False:\n",
     "test_the_align_refusals"),
    ("missing reference branch allowed", AL, "        if missing:\n", "        if False:\n", "test_the_align_refusals"),
    ("libraries unchecked", PV, "        if so.get(name) != sha:\n", "        if False:\n",
     "test_a_changed_pin_or_library_or_a_missing_library_fails"),
    ("canonical pins unchecked", PV, "        if got != pin:\n", "        if False:\n",
     "test_a_changed_pin_or_library_or_a_missing_library_fails"),
    ("a missing library allowed", PV, "    for name in sorted(set(so) - set(libs)):\n", "    for name in []:\n",
     "test_a_changed_pin_or_library_or_a_missing_library_fails"),
    ("duplicate identities allowed", RC, "if sk.size and np.any(sk[1:] == sk[:-1]):", "if False:",
     "test_packing_and_lookup"),
    ("subrun width unchecked", RC, "or np.any(subrun >= 1 << SUB_BITS)", "or False", "test_packing_and_lookup"),
]


def mirror(root: Path) -> Path:
    """A tree at root/repo mirroring REPO by symlinks, with real copies of the RDX files. Returns its rdx/."""
    repo = root / "repo"
    repo.mkdir()
    for e in REPO.iterdir():
        if e.name != "nd-unfolding":
            (repo / e.name).symlink_to(e)
    nd = repo / "nd-unfolding"
    nd.mkdir()
    for e in ND.iterdir():
        if e.name != "rdx":
            (nd / e.name).symlink_to(e)
    rd = nd / "rdx"
    rd.mkdir()
    for f in FILES:
        (rd / f).write_bytes((HERE / f).read_bytes())
    return rd


def run_suite(rd: Path) -> tuple[int, str]:
    p = subprocess.run([sys.executable, "-B", "-m", "unittest", "nd-unfolding/rdx/test_rdx.py"], cwd=rd.parents[1],
                       capture_output=True, text=True, timeout=3600)
    return p.returncode, p.stdout + p.stderr


def failing(out: str) -> set[str]:
    return set(re.findall(r"^(?:FAIL|ERROR): (\w+)", out, re.M))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None)
    ap.add_argument("--jobs", type=int, default=1, help="mutants run at once (each in its own mirrored tree)")
    a = ap.parse_args(argv)
    with tempfile.TemporaryDirectory() as d:
        rc, out = run_suite(mirror(Path(d)))
    ran = re.search(r"^Ran (\d+) tests?", out, re.M)
    if rc != 0 or not ran or int(ran.group(1)) != EXPECTED_TESTS:
        print(f"UNMUTATED SUITE: rc {rc}, ran {ran.group(1) if ran else '?'} of {EXPECTED_TESTS} expected tests\n" + out[-3000:])
        return 1
    print(f"unmutated suite: {ran.group(1)} tests OK, in the mirrored tree")
    todo = [m for m in MUTATIONS if not a.only or a.only in m[0]]
    ok, n = True, len(todo)

    def one(m):
        label, fname, old, new, test = m
        src = (HERE / fname).read_text()
        if src.count(old) != 1:
            return label, test, None, f"anchor occurs {src.count(old)} times"
        with tempfile.TemporaryDirectory() as d:
            rd = mirror(Path(d))
            (rd / fname).write_text(src.replace(old, new))
            _, out = run_suite(rd)
        return label, test, failing(out), ""

    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for label, test, fails, why in ex.map(one, todo):
            if fails is None:
                print(f"MUTATION NOT APPLIED  {label}: {why}", flush=True)
                ok = False
                continue
            killed = test in fails
            ok &= killed
            print(f"{'KILLED' if killed else 'SURVIVED':8s}  {label:48s} by {test}"
                  + ("" if killed else f"  (failing: {sorted(fails)})"), flush=True)
    print("MUTATION CHECK ::", "PASS" if ok else "FAIL", f"({n} mutations)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
