VERDICT: GO WITH CHANGES

I read all of it but ran nothing. I could not hash the files against `tests.txt` or check commit 02e9518c2. `unfold_2d_omnifold_unbinned.py` and `s5e_deform.py` are not in the supplied tree. For §4 I relied on `refine_stay_positive` taking no edges argument (`s5e_trace.py:417`).

**BLOCKING**

1. **A float32 `w_truth` would fail C-FILE on the real run.** Nothing in the supplied material shows the real npz's `w_truth` dtype. `nn_dump_inputs.py:97` passes `sig["w_truth"]` through, and every test uses float64 (`test_evw5d.py:75`).
   - `build_table` saves `w_prior` at the input's own dtype (`evw5d.py:159`).
   - `check_file` requires all three weight columns to be float64 (`evw5d.py:241`).
   - If the real dtype is float32, `weights_float64` goes false, C-FILE fails, and 0.25 node-h buys a FAIL marker.
   - Nothing wrong would be published, and this is moot if the dtype is float64, but the gate would fail when it should pass.
   - Fix: write `w_prior` as `.astype(np.float64)` (exact widening), and compare the widened `indep["w_truth"][e]` at `evw5d.py:238`. Alternatively, have the connect pre-check print `np.load(npz)["w_truth"].dtype` at zero node-h.
   - Add a float32-`w_truth` end-to-end test.

2. **The launcher can fetch a FAIL or unverified product without complaint.** `evw5d_launch.sh:24-31` (`fetch-products`) checks only `shasum -a 256 -c SHA256SUMS`, and that file comes from the same directory it checks.
   - It never reads the done marker, so a FAIL run (all files are written on FAIL) fetches with "shasum -c rc=0".
   - It never compares `SHA256SUMS` to a bound digest, and never runs `accepted()`. §6 says the fetch is "by sha".
   - `evw5d_hpss.sh:13` has the same weakness, though less so: it only greps `"verdict": "PASS"`. That grep is safe, because `"controls_verdict"` does not match it.
   - Fix: give `fetch-products` a required `EXPECT_SUMS_SHA256` argument. Fail unless it equals `shasum` of the fetched `SHA256SUMS`. Then run `python3 -c 'import evw5d,sys; sys.exit(0 if evw5d.accepted(sys.argv[1], sys.argv[2]) else 1)'` on the fetched directory.
   - Do the same bound-digest check in the HPSS script.

**NON-BLOCKING**

3. **`set -o noclobber` is new in this revision and is set before `source setup_salloc_env.sh`** (`sbatch_evw5d.sh:21,50`). The setting persists into the sourced script, and ESS never ran that way.
   - Any `> existing-file` inside the setup would fail. The connect pre-check (`evw5d_connect.sh:96`) sources without noclobber, so it cannot predict this.
   - The likely outcome is `src_rc≠0` and a refusal, which fails closed but wastes the slot. Retrying needs a new `$OUT`, because `evw5d_connect.sh:36` demands that `$OUT` be absent.
   - Fix: `set +o noclobber; source …; set -o noclobber`.
   - The tests only fake a setup that does `return 1`, and the script's tail (lines 49-65: srun, DONE) never runs under test.

4. **`accepted()` accepts any self-consistent PASS bundle when `expect_sums_sha256` is omitted** (`evw5d.py:393-423`). That includes a synthetic `--fixture` bundle, because it never checks `input_npz_sha256`, `result_sha256`, `code_pin`, `tool_digest` or the absence of `--fixture` in `argv`.
   - Fix: make the bound digest a required argument, and check the production pins in `run.json`.

5. **Mislabelled unit key in published constants.** `evw5d.py:592` calls the flux `flux_m2_per_POT_by_pt_bin`. `xsec_nd.py:60` says m⁻²/POT, and the formula divides by it.
   - The values and the formula are right, but the label reads as m²/POT. Rename it to `flux_per_m2_per_POT_by_pt_bin`.
   - The axis units are also not recorded in `constants.json`.

6. **§4's limit omits the flux.** It is stored only per fine pT bin. Splitting a pT bin needs the flux for the sub-bin as well as the event-level completeness.
   - The §4 limit on completeness is otherwise right: `denom_nd` is `histnd` on the fine edges (`nn_dump_inputs.py:90`), and the 0.07/0.33/0.47 edges do not match the paper's 0.075/0.325/0.475.

7. **§6 says the script carries `#SBATCH -t 00:30:00`; it does not** (`sbatch_evw5d.sh:2-8`). The limit comes from `--time` in the connect (`evw5d_connect.sh:113`), and the job refuses unless it reads 30:00 (line 34), so this is safe. Fix the text.

8. **Mutant gaps.** None of these can change the weights, because C-BIND, C-F and C-SELF overlap them.
   - No mutant exists for `grid["pass"]` (`evw5d.py:570`), C-PINS (`:621`), the pre-run HEAD and `code_sha` checks (`:478-483`), `captured_equals_remade` (`:527`) or `weights_float64` (`:241`).
   - No mutant exists for the sbatch checks at lines 26, 32-34, 47-48 and 54.
   - No test makes C-PINS or C-GRID fail, or a wrong deploy refuse.
   - Fix: add those tests and mutants, and pull C-PINS and C-GRID into the kill set.

9. **HPSS script.** `evw5d_hpss.sh:33-38` runs `htar -xf` inside `while read … < list`, so htar could consume the list from stdin and silently verify fewer files. Add `< /dev/null` and check that the retrieved count equals the file count. The `hashcreate` and `hashverify` return codes (lines 28-29) do not set `bad`.

10. **Two job-script refusals.**
    - A dangling symlink at `$OUT/evw5d` passes `[ ! -e ]` (`sbatch_evw5d.sh:47`). Python's `mkdir` then fails closed. Add `-L`.
    - The `pwd -P` equality check (line 26) refuses with no DONE file if the pscratch path is not canonical. Check it in the connect before submitting.

**Answers to the questions**

- **Q1 (key, alignment).**
  - `build_data` passes `MCgen`, `pass_truth` and `w_truth` through unchanged (`s5n_pseudo.py:197-199`).
  - `unf_inputs` copies the references (`s5e_trace.py:438-442`), and the central pair has no permute, bootstrap or jitter (`s5p_numerics.py:181-185`).
  - `omnifold_loop` filters by `pass_truth` in order (`omnifold_nn_core.py:210-213`). `w_push` is the second return value, and `do_split` is false.
  - C-KEY proves input identity bit for bit, dtypes included, and tests each field. It proves wpush alignment only by length.
  - The per-row pairing rests on that code plus C-GRID's bit-exact re-histogram. The re-histogram would almost surely catch a reorder even within a cell, because summation order changes the rounding.
- **Q3 (gates).**
  - `contributions` mirrors ESS's (B) line for line (`evw5d.py:128-141` against `ess_capture.py:371-384`). The ESS margins were 3.8e-15 for rows against the result and 3.3e-16 for the result against the published f, so about 4e-15 against the 1e-14 limit.
  - The summation is deterministic given a byte-equal result, and the meta strip is ESS's, which passed with no differing keys.
  - I found no spurious-fail path other than item 1.
- **Q4 (read-back).**
  - C-FILE, C-SELF and C-FLOW parse the same bytes that are hashed (`read_npz`), and the inputs are compared to an independent read. The `good` array, `xsec_flat`, 1e4 and the volumes are now checked independently.
  - The other constants (`fine_to_cell`, `completeness`, `ofin`, `denom_nd`, flux, POT, N, edges) are all present and checked.
  - The constants.json formula is right. It matches `xsec_nd.py:77-83`, with `isfinite` being the only omission.
- **Q5 (binning independence).**
  - The claim holds for this driver path. The loop gets continuous coordinates, and the interior edges are used only after training (`s5c_unfold.py:135-145`).
  - C-COL is a valid bit-for-bit test of what it states. It is synthetic, uses 2 threads, and the two grids differ only in edges, denominator and flux (the RNG draws are identical).
- **Q6 (completeness).** The measurement matches the driver (`nz = dn > 0`). It is not a gate, so it cannot touch the weights. A cell with a denominator and no signal gives c=0, which correctly sets the 1e-5 flag false.
- **Q9 (r1 fixes).** All six r1 findings are fixed, each with a test.
  - Tests: `test_accepted_*`, `test_fail_on_f`, `test_check_self_saved_constants_from_the_builder`, the `test_job_*` tests and `test_check_self_f_file_alone`.
  - The only new defects are items 3 and 4.
- **Q10 (launch scripts).** Apart from item 2:
  - Every script is sha-gated through placeholders that refuse until filled.
  - There is one sbatch, and the connect bails if `$OUT` exists or an evw5d job is queued.
  - The limit is 30:00 (0.5 node-h at the observed charge factor of 1) and `--no-requeue` is set.
  - Writes go to `$OUT`, `/dev/shm` and HPSS home, never CFS. The job script uses `/global/homes` only as HOME.

**Checked and fine**
- The `wpush` dtype: LightGBM returns float64, and a float32 push would widen exactly (tested).
- `w_unfolded` is the same expression as `s5c_unfold.py:138`.
- `entry`: uint32 holds 32.8M, with a guard.
- Unmasked row-ordering: the `flat_index` last-edge rule matches `histogramdd`, and flow rows are counted.
- `load_indep` never touches the object-dtype `axes` array.
- Output paths: `--out` is checked under `--out-root` before and after `mkdir`, and `--fixture` is refused in Slurm.
- The staged inputs are hashed during the copy and re-hashed after the run.
- The ESS tool is executed from hashed bytes.
- The product set is exact, and nothing else is written.
