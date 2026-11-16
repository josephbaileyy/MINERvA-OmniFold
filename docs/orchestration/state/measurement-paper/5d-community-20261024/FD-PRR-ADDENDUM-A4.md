# FD-PRR ADDENDUM A4: route 2 reads nothing outside REF-G1's guard roots; the fine-ratio rho arrays are staged (2026-11-09, for coverage-5b-audit and the director's binding; nothing runs)

**By:** the valid-region lane (session director-helper-2), at the director's rulings of 2026-11-09 on the prr_ibu
attempt-2 STOP and on the A4 trace.

**Amends:** `FD-PRR-DECLARATION.md` rev 2, as amended by addendums A1, A2 and A3. The code is at M_A3 =
`06657cff7a6ed6c9832fe27957899125e6cac4ad`. This addendum changes `prr_ibu.py`, with its tests and mutants. It adds one
staging step on the cluster, made with the bound `prr_probe.py stage`, unchanged. No bound limit, price, cap, reading,
licence, queue or other FD-PRR file changes.

**CITABLE FOR:**
- the two cluster-only defects on route 2's run path and their cause;
- the change to `prr_ibu.py`;
- the staging step's design;
- its tests, its required mutants and the new digests;
- the static and dynamic trace of the run path, and the search of the completed jobs' runner path.

**NOT CITABLE FOR:**
- anything the declaration does not license;
- any route-2 or prior-retention result;
- the §10.4 deviation in the four completed jobs. That is
  [`OUTCOME-20261109-fd-prr-104-plain-reads.md`](../../../OUTCOME-20261109-fd-prr-104-plain-reads.md), recorded
  separately.

## 1. The defect that refused attempt 2

- **What happened.** prr_ibu, job 61043652, ran from M_A3. It passed the job script's checks, A3's TimeLimit check
  among them. It then started `prr_ibu.py`, which refused 1 min 12 s later, before any unfold
  (`fd/receipts-prr/ibu/attempt2/README.md`). `log-ibu/ibu.log` reads: "refusing: a plain read of
  /pscratch/sd/j/josephrb/fd-prr-20261108/stage.json: files under ['/pscratch', '/global/cfs'] are read only through
  O_NOATIME".
- **The cause** (`prr_ibu.py` @ 06657cff):
  - `main()` enters `ref_g1.read_guards(PROTECTED, (REPO, a.out, stage_dir, a.queue_dir), root=False)` at :339. The
    allowed roots are the repository, `$OUT/route2`, the stage dest `$OUT/stage` and `$OUT/queues`.
  - `run()` then re-read `$OUT/stage.json` plainly at :274. That file is under /pscratch and under none of the four
    roots.

## 2. The next defect, found by the trace the director required

- **What the trace was.** With the first defect fixed, `prr_ibu.main` was run end to end on synthetic rows with
  `ref_g1.PROTECTED` patched over the test's temp root, so every path was protected as on the cluster (§7).
- **What it found.** The run refused at "a plain read of
  /pscratch/sd/j/josephrb/s5p-20260926/ratios/nullsF/rho-genie_cv-F.npz".
- **The cause.**
  - The four fine-ratio hypotheses, `docs/orchestration/state/s5p/ratios/nullsF/null-{genie_cv,genie_mec,gibuu_cv,
    nuwro_cv}-F.json`, name their rho arrays by an absolute shared path in `rho_npz.path`.
  - `s5p_truths.load_fine_rho` (`nd-unfolding/s5p_truths.py:238-242` @ 06657cff) hashes and loads that path plainly.
    The runner reaches it at `s5p_nullexp.py:298-299`.
  - None of the four files is in `prr_probe.SOURCES`, so none was staged.
  - Route 2 reads them in 8 of its 20 experiments: A7_genie_cv, A7_genie_mec and A7_nuwro once each, and A7_gibuu at
    its five splits.
- **On the cluster, attempt 3 would have stopped here.**
- **The same reads in the four completed jobs** happened without a guard, in 72 of their 181 tasks. That §10.4
  deviation is recorded in its own record, cited above, under the director's ruling: the products stand and are not
  rerun.

## 3. Why no test caught either

- **Route2Run's only run test** wrote stage.json in a tempfile directory (`test_prr.py:790-809` @ 06657cff). That
  directory is under neither PROTECTED root, so the guard protected none of its paths.
- **No test ran a fine-ratio truth through the capture.** Route2Capture and Route2Unfold use W1, nominal and
  closure_nuwro, whose hypothesis is the coarse `null-mnvtune_v1-J.json`.
  Search: git grep -n 'R.capture(' 06657cff -- nd-unfolding/prior_retention/test_prr.py gives 7 calls, at W1 (4), nominal (2) and closure_nuwro (1) @ 06657cff
- **The lane's machine has no /pscratch,** so a fine-ratio capture there without the guard would have failed with
  FileNotFoundError, a different error from the guard's.
  <!-- absence-ok: a statement about the test machine's filesystem, not about a result -->
- **The connect** reads stage.json with sha256sum and does not run `prr_ibu.py`.

## 4. The change (`prr_ibu.py`)

- **Both stage records are read once, in `main()`, before the guard** (:390-399), and passed to `run()`:
  - `stage.json`, as before;
  - `stage-a4.json`, the new record beside it (`STAGE_A4`). Without it the run is refused: "no stage-a4.json beside
    …: the rho arrays are not staged".
  - `run()` reads neither file.
- **`rho_manifest()`** (:76-87) builds the staging manifest, in `prr_probe.py stage`'s {role, src, sha256, name}
  format. It lists every rho array a route-2 truth's hypothesis names, read from the committed json's own `rho_npz`.
  So the json is the only source of the four paths and digests. `prr_ibu.py stage-a4-manifest` prints it.
- **`rho_copies()`** (:90-101) refuses unless the stage-A4 record stages exactly that manifest: the same sha256 set,
  each `src` as named, and each copy under `$OUT/stage/s5p-nullsF` (`STAGE_A4_DEST`). It returns the copies keyed by
  sha256.
- **`capture()`** (:146-210) takes them as `rho`. While the B0 line runs, it replaces `s5p_truths.load_fine_rho` with a
  wrapper (:186-190, :198). The wrapper picks the staged copy by the json's `rho_npz.sha256`, and refuses if there is
  none. It then calls the real loader on the copy, so `load_fine_rho`'s own sha256 check still runs.
- **`run()`** re-verifies the stage-A4 copies with `prr_probe.verify_stage` (:324), as it does stage.json's.
- **What does not change:**
  - `s5p_truths.py` and the four json files;
  - `sbatch_prr.sh`, `prr_probe.py`, `prr_read.py`, the queues and `stage.json`;
  - every declared limit and the 27.0 cap;
  - the guard's four allowed roots, which the director ruled not to widen.

## 5. The staging step (after the binding; its script goes to the director for its sha256 first)

- **What it does.** A login-node connect, launched as every connect is: one ssh session, a /dev/shm copy, its sha256
  checked or exit 91, then nohup.
  - It runs from a fresh clone at A4's merge commit (`$OUT/deploy-stage-a4`).
  - It runs the deploy's `prr_ibu.py stage-a4-manifest`, then the bound `prr_probe.py stage --manifest … --dest
    $OUT/stage/s5p-nullsF --out $OUT/stage-a4.json`.
  - `prr_probe.stage` copies each file once through O_NOATIME, with `ref_g1.copy_noatime`. It takes the digest in the
    same pass, refuses unless that digest is the pin, records each source's stat before and after, and refuses if any
    of them moved. `stage.json` is not touched.
- **Its own pins and refusals** (the draft is `fd/receipts-prr/a4/prr_stage_a4.sh.template`; the commit and digests
  are filled in after the binding):
  - the four rho sha256, checked against the deploy's committed json and against the manifest;
  - `$OUT/stage-a4.json` and `$OUT/stage/s5p-nullsF` must be absent;
  - no prr_* job may be queued or running;
  - no process on the node may name s5p-20260926;
  - after the copy, each copy's sha256 is checked again and porcelain must be 0.
- **When.** Only while no other lane is copying from s5p-20260926, per the director's ruling.

## 6. The tests and the required mutants

New tests:
- **`test_the_run_path_end_to_end_with_every_path_protected`** (REQUIRED, `Route2Run`):
  - `prr_ibu.main` runs end to end on `route2_fixture`, the cluster layout on synthetic rows, with `ref_g1.PROTECTED`
    over the temp root;
  - all 20 experiments complete, C-IBU runs, and both products are written;
  - the eight rho loads all come from the staged copies;
  - only content pins are substituted, as listed in the test's docstring; no read is.
- **`test_unpinned_inputs_are_refused_before_any_unfold`** (existing): now on the same fixture.
- **`test_without_the_stage_a4_record_the_run_is_refused`** and **`test_a_changed_rho_copy_is_refused_inside_the_run`**
  (`Route2Run`).
- **`Route2StageA4`**, three tests:
  - the manifest is exactly the committed fine hypotheses' `rho_npz`, all four under /pscratch, and the CLI prints it;
  - the stage-A4 record must stage exactly the manifest under its directory;
  - the capture refuses a fine hypothesis with no staged copy and reads the staged copy when it has one.

**Against the earlier `prr_ibu.py`** (`fd/receipts-prr/a4/probe-earlier-mains.txt`): the same fixture and
substitutions run each version's own `main`:

| prr_ibu.py | rc | outcome |
|---|---|---|
| M_A3 06657cff | 2 | refuses at `stage.json`, attempt 2's refusal |
| 0d6656be (the stage.json fix alone) | 2 | refuses at the rho array's shared path |
| A4 | 1 | completes (C-IBU fails on synthetic rows) |

New mutants, each killed by its named test:

| mutant | change | killed by |
|---|---|---|
| the stage record re-read inside the guard (REQUIRED) | `run(…, stage_rec, …)` → `run(…, json.loads(a.stage.read_text()), …)` | the end-to-end test |
| the rho arrays read at their shared path (REQUIRED) | the wrapper's installation removed | the end-to-end test |
| the stage-A4 record re-read inside the guard (REQUIRED) | `a4_rec` → `json.loads(a4_path.read_text())` | the end-to-end test |
| the run hands the capture no staged rho | `capture(…, rho)` → `capture(…)` | the end-to-end test |
| a staged rho copy not re-verified in the run | `P.verify_stage(a4_rec)` removed | the changed-copy test |
| no stage-A4 record needed | the `is_file()` refusal removed | the no-record test |
| the stage-A4 record not checked against the manifest | the set check removed | the stage-exactly test |
| a rho copy outside the stage directory accepted | the directory check removed | the stage-exactly test |
| a fine hypothesis left out of the manifest | A7_nuwro skipped | the manifest test |
| a missing staged copy read in place | the refusal replaced by the real loader on the shared path | the capture test |

**The counts.** 116 tests (110 + 6) and 81 mutants (71 + 10). `prr_mutation.py`'s EXPECTED_TESTS is 116.

## 7. The trace and the search (receipts in `fd/receipts-prr/a4/`)

- **The dynamic trace** (`trace-run-path.txt`, from `trace_run_path.py`). The REQUIRED fixture is run with REF-G1's
  guard test logged as well as applied. Inside the guard it records every open and filesystem event, grouped by root
  and by the innermost repository frame (file:line), and every import attempted.
  - **At A4:** 0 reads the guard would refuse.
  - **Reads:**
    - the repository: modules, pins, configs, the contract, `h2_definition.json`, the REF-G1 readout and the
      hypotheses;
    - the stage dest: the inputs, the nuwro ratio and the four rho copies;
    - the queues;
    - the python environment, which is not protected (`/global/homes` on the cluster).
  - **Writes and events:** `$OUT/route2`'s `scratch` mkdir, listdir and rmdir, and its two products.
  - **What is absent:** no subprocess, no tempfile and no ROOT import. The fixture's hypothesis copies under
    `stage/hyp/` stand in for the repository's json.
- **Cluster-only conditions, checked statically:**
  - The guard compares abspath with resolve()d roots. `realpath` showed no symlink on `$OUT`, `stage`, `queues`, the
    deploy or `nullsF` (login30, 2026-11-09T18:34:37Z).
  - `setup_salloc_env.sh:24` sets `TMPDIR=$SCRATCH/tmp`, under /pscratch. Nothing on the run path uses `tempfile`.
  - `2d-unfolding/unfold_2d_omnifold_unbinned.py` imports ROOT at its top. It is only hashed by `check_pins`
    (`prr_probe.py:99`) and is not imported inside the guard.
- **The search of the completed jobs' runner path** (`search-closure.txt`, `search-json.txt`, from `search_closure.py`
  and `search_json.py`):
  - **The AST import closure** of `prr_probe.py`, `prr_ibu.py`, `prr_read.py` and `s5p_nullexp.py` has 32 modules.
    Eight lines carry a `/pscratch` or `/global` literal:
    - six are prr_probe's SOURCES and FD_STAB_OUT, the staged inputs;
    - one is ref_g1's PROTECTED;
    - one is unfold_2d's `_OF_PY`, inside `main()` (:1352-2400), which the runner never calls. It calls only
      `refine_stay_positive` and `_make_bkg_classifier`, which do no file I/O;
    - `unfold_nd_omnifold_unbinned.py:73-74` are argparse defaults, used only by its `main()`.
  - **Every absolute path in the 181 queue lines** is under `$OUT` (stage and runs).
  - **The 15 committed json files the runner names** were searched for absolute path values. The only field the
    runner path opens is `rho_npz.path`. The hypotheses' `numerator`, `denominator` and `control` paths are written by
    their builders (`s5p_truths.py:320`, `s5e_deform.py:141`) and read by nothing on the path. The ibu1 and REF-G1
    configs' input, comparator and product paths are read only by `ibu1.main` and `ref_g1.Run`, which route 2 does not
    call.
  - Search: python3 -I search_closure.py; python3 -I search_json.py over the queues, the 32 modules and 15 json gives one opened absolute path field, rho_npz.path @ ef9411a3
- **A slip, recorded as the director ruled.** In the realpath session on login30 at 2026-11-09T18:34:37Z, the lane
  also ran `ls -la /pscratch/sd/j/josephrb/s5p-20260926/ratios/nullsF/`. It listed a shared directory outside the
  study, which can move that directory's atime (§10.4 cites the same effect from ENS1, #940). It opened no file
  (`fd/receipts-prr/a4/ls-slip.txt`).

## 8. The new digests (sha256)

| file | at M_A3 | after A4 |
|---|---|---|
| `prr_ibu.py` | `17acad82…` | `fa91394507c0e6a32486af25fa52f7e162135cf6483519ccf15510e1c9473cb0` |
| `test_prr.py` | `c600e4b1…` | `fad928d85c9183ac525ffabcd809d6968afab6aead4a2ad2aa13202b788eef40` |
| `prr_mutation.py` | `dfa99466…` | `e088406cd47ef88c8e47b988e7f684f8c29b74a620fa65d101ac790ca7892d5f` |
| `prr_probe.py`, `prr_read.py`, `sbatch_prr.sh` | unchanged | `f87ee90c…`, `d7c7c2c0…`, `4493aad5…` |

## 9. Receipts (`fd/receipts-prr/a4/`)

- **Where they are made.** In a clean clone at this addendum's code commit, which the receipt README names. A following
  commit adds only the receipt files.
- **How.** Each run is one serial process under `nice -n 19`, with every thread cap at 1. The runs are:
  - every class but `JobScript`;
  - the `JobScript` class;
  - the earlier mains' probe;
  - the trace;
  - the two searches;
  - the 81-mutant run.

## 10. After the binding (the director's ruling; not part of this addendum's code)

1. **The move.** One ssh session moves attempt 2's `$OUT/log-ibu` and `$OUT/route2` into `$OUT/ibu-attempt2/`, with a
   listing and every moved file's sha256 before and after. It is recorded as a short addendum to the attempt-2 record.
2. **The staging step** of §5, its sha256 to the director first.
3. **Attempt 3.**
   - It runs from A4's merge commit, with TAG=ibu-3 on the connect side.
   - It pins both earlier attempts in sacct: `61035510|prr_ibu|FAILED|41|1` and `61043652|prr_ibu|FAILED|132|1`.
   - It checks `stage-a4.json` and the four copies.
   - The job keeps the name prr_ibu and writes `$OUT/log-ibu` and `$OUT/route2` fresh, so `prr_read.py` is unchanged.
   - Its post reads `logs/ibu-3.jobid`.
   - The charge is bounded: 7.4267 + 0.5 = 7.9267 of 27.0.
