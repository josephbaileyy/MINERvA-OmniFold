# EVW5D declaration: configuration (e)'s central per-event weights for the sixteen-cell result (2026-11-25, revision 2)

**By** ibu-chi, at the director's request. **Status: a draft for the reads and the director's binding. Nothing has run
on NERSC.** It runs only under a binding and the director's GO. Publication, and where a 1.7 GB file is hosted, are
Joseph's.

**Authority.** Joseph, 2026-11-25: the central-value per-event weights are saved and published with the result
(`DECISION-20261125-joseph-v1-scope-option-i-weights-hydrogen.md` §1, §3). The director's rulings of 2026-11-25 on
this lane's scoping report:
1. weights for configuration (e), the sixteen-cell result's estimator, only. The five-axis purity result is not in v1:
   a later control did not reproduce its product (`docs/orchestration/RESULT-20260923-issue26-issue5.md:89`), so no
   exactness gate can be passed against it;
2. the writer is ESS's capture plus a save, a read-back, a done marker and acceptance, in a new module that imports
   the pinned driver unchanged; both of ESS's gates are kept; a C-COL test; completeness measured and reported;
3. the key, columns and constants as scoped; weights in float64; truth columns at the input's own precision;
4. nothing on CFS: the output stays on $SCRATCH with its manifest, gets an HPSS copy, and is fetched by sha;
5. reads by codex-school `gpt-6.2-sol` and claude-personal Sonnet 5.5, blocking only on what could change the
   published weights, constants or gates; price 0.25 node-h, cap 0.5, one CPU node.

**Revision 2 (2026-11-25)** takes codex-school `gpt-6.2-sol`'s first read (`receipts/reads/r1/`): NO-GO, four
BLOCKING and two other findings, all taken (§8). It also takes the director's rulings on revision 1: no production
C-COL arm, and the 1e-5 completeness statement (§3).

The code is in [`nd-unfolding/evw5d/`](../../../../../../../nd-unfolding/evw5d/): `evw5d.py`, `sbatch_evw5d.sh`,
`test_evw5d.py` and `evw5d_mutation.py`.

## 1. What runs

**One run of configuration (e)'s central data unfold, unchanged**, exactly as the ESS run made it
(`fd/receipts-ess/README.md`, job 61082774, which reproduced the product's `xsec_flat` byte for byte):
- **the driver:** `nd-unfolding/s5p_numerics.py` `main`, in a clean clone at the producer's code commit
  `abdc88c52b909cfc1eb658ae97bd9defc8f640e7`, with the eleven module digests of `ess_capture.py:63-75`;
- **the argv** (`ess_capture.py:280-284`; the producer's, `state/s5p/s2-num-tasks.tsv:2`): `--config R --iters 5
  --construction data --pairs=-:- --tag data --threads 32`, on the staged copies of `of_inputs_5d.npz` (`07fccc1a…`)
  and `bkg_dump.npz` (`2addac8f…`);
- **the reference:** `s5p-20260926/runs/s2/num/data/data_b-_j-.npz` (`fb5cc679…`), the sixteen-cell result's central
  product (`RE1-REPORT.md:21-31`; `S1-DECLARATION.md:181`);
- **the capture:** two pass-through wrappers, on `omnifold_nn_core.omnifold_loop` and `s5c_unfold.unfold`, which
  return the very objects the real calls return and keep the push weights and the unfold's inputs (ESS's, at
  `ess_capture.py:265-279`). The run refuses unless each is called once;
- **the machinery:** `evw5d.py` executes `nd-unfolding/ess_e/ess_capture.py` from the bytes whose sha256 it checks
  (`4755681f…`, the ESS run's tool) and uses its pins, O_NOATIME staging into `/dev/shm`, read guard and helpers.

The truth-selected MC rows reach the unfold in the npz's own order: the data build passes them through
(`s5n_pseudo.py:189-204` @ abdc88c5), nothing permutes them for the central pair (no bootstrap, no jitter, no permute
seed), and `s5e_trace.unf_inputs` copies the references (`:438-442`). C-KEY checks this rather than assuming it.

## 2. What is written

All under `--out` (new), on $SCRATCH:

**`weights.npz`**, one row per truth-selected MC row (`pass_truth`), in the npz's order: 32,849,103 rows on the ESS
run's count (`fd/receipts-ess/README.md:111`), about 1.74 GB at 53 bytes a row, plain `np.savez`.

| column | dtype | meaning |
|---|---|---|
| `entry` | uint32 | the row's index in the npz's `MCgen`: **the key is (input npz sha256 `07fccc1a…`, `entry`)** |
| `truth_pt`, `truth_pz`, `truth_eavail`, `truth_q3`, `truth_W` | float32 | the truth coordinates as the driver binned them (the npz's own precision) |
| `w_prior` | float64 | `w_truth`, the prior weight (fills the driver's `ofin`) |
| `wpush` | float64 | the step-2 push weight (`omnifold_loop`'s second result) |
| `w_unfolded` | float64 | `wpush * w_truth`, the very expression the driver histograms (`s5c_unfold.py:138`) |
| `fine_index` | int32 | the row's fine cell, C order, −1 outside the grid (`s5e_trace.flat_index`, last edge inclusive) |
| `reco_partner` | bool | `pass_reco`: false where step 1's weight came from the regressor |

The key identifies a row of one content-addressed file. It is not a physical event id (run, subrun, gate), which the
director ruled out of this item, as in 2D.

**`constants.npz`** and **`constants.json`**: the extraction's operands, taken from the run, not recomputed: the five
axes' edges, the 14 per-pT flux values, `data_pot`, `n_nucleons`, the 1e4 m²→cm² factor, `denom_nd`, the driver's
`ofin` and completeness, the `good` mask, the cell volumes, the fine-to-sixteen-cell map (`930326a3…`) and the result's
`xsec_flat`. `constants.json` also gives the formula and the sixteen f values:

d⁵σ_f = 1e4 · Σ_{rows in f} w_unfolded / (c_f · Φ(pT bin of f) · N · POT · vol_f), zero where that denominator is
not positive; f_R = Σ_{f ∈ R} d⁵σ_f · vol_f.

Also: `product/data_b-_j-.npz` (the driver's own output), `run.json` (every control, the findings and their sizes,
timings, peak RSS, digests), `SHA256SUMS`, and **`evw5d.done`, published last by write-then-rename**, holding the
verdict, the failed controls, the findings, the acceptance checks and the digest of `SHA256SUMS`. A product without a
PASS `evw5d.done` is not a result; a consumer checks it with `evw5d.accepted()`.

## 3. Controls

| control | what it checks | gate |
|---|---|---|
| **C-BIND** (gate 1) | the re-made `xsec_flat` equals fb5cc679's byte for byte, the in-memory result equals the file, and the meta equals the reference's but for the per-run fields (`ess_capture.py:PER_RUN`) | otherwise STOP: `STOP.json`, no weights, exit 8 |
| **C-KEY** | the arrays the unfold received (MCgen, MCreco, both pass flags, both weights, `denom_nd`, flux, POT, N, edges) equal an independent `allow_pickle=False` read of the staged npz bit for bit, `pass_truth` is bool, and the push weights align with its rows | otherwise no weights, exit 6 |
| **C-ENTRY** | the key is unique: uint32 entries, strictly increasing | all |
| **C-GRID** | ESS's mapping checks: the driver's maps recomputed from the table reproduce its result bit for bit; edges equal the fine grid; the fine map's digest; the volumes | all |
| **C-F** (gate 2) | the sixteen f, from the result (Σ xs·vol) and from the per-row contributions (ESS's (B)), against the data product `fd_data_product_cpl.json` (`d6752d2c…`) | ≤ 1e-14 relative |
| **C-FILE** | the products read back from the bytes hashed: exactly the declared columns and constants, each column equal to its source in the independent read (entry, truth, `w_prior`, `reco_partner`) or to the captured push weights, `w_unfolded` equal to their product, `fine_index` recomputed, the constants equal to the run's, the input constants (edges, flux, POT, N, `denom_nd`) also equal to the independent read itself, the meta and `constants.json` as written | all, bit for bit |
| **C-SELF** | from the read-back files alone: the result re-histogrammed and extracted bit for bit equal to fb5cc679's; the saved `ofin`, completeness and `good` mask bit for bit against the ones recomputed from the saved rows; the saved `xsec_flat` bit for bit against fb5cc679's; the saved 1e4 exactly; the saved volumes against the products of the saved edges' widths to 1e-13; an independently written formula to 1e-13; the sixteen f from the file and from its rows to 1e-14 | as stated |
| **C-FLOW** | every truth-selected row is in the file; the in-grid rows, by `bincount` over `fine_index`, give the driver's per-cell `unf` and `ofin`; the rows outside the grid are counted with their weight | ≤ 1e-12 relative |
| **C-PINS** | after the run, the eleven pinned modules and the staged copies equal their pins | all |
| **C-COMPLETE** | a **measurement**: c_f = ofin_f / denom_f over the fine cells; max \|c − 1\|, its quantiles, cells beyond 1e-12, cells with signal and no denominator | a departure beyond 1e-12 is a **FINDING**, printed and recorded with its size; not a failure. Under the director's ruling, the record states "completeness is 1 to 1e-5" only if every fine cell with a denominator is within 1e-5 of 1 and no cell has signal without one (`c_one_to_1e-5_in_every_fine_cell`); otherwise the lane prices an event-level denominator for the director and builds nothing |

The verdict is PASS only when every gated control passes and the acceptance holds: the products are exactly the
declared set, `SHA256SUMS` parses to exactly their digest map, every product re-hashes equal, and nothing is a link.
A FAIL still writes the files, for diagnosis, under a FAIL done marker; an interrupted run leaves no marker, and a
retry needs a new `--out`.

**The consumer's check, `accepted(out, expect_sums_sha256)`.** It refuses a linked marker or manifest, reads
`SHA256SUMS` as bytes (LF-only, the exact form written), re-runs the acceptance, and requires the marker to agree with
the hashed `run.json`: the verdict and controls verdict PASS, no failed control, the products' digests equal to the
manifest's, and in `run.json` every gated control passing with the same findings. A product set replaced as a whole
can only be told from the real one by the manifest's digest recorded in the release binding, passed as
`expect_sums_sha256`; the receipt records it.

## 4. Binning independence, and its limit

The training sees no interior edge: the OmniFold loop takes the continuous coordinates
(`s5c_unfold.py:124-128` @ abdc88c5); the data build and the refinement use only the outer fiducial window
(`s5n_pseudo.py:105-110`, `:189-196`); the edges enter after the loop, in the histograms and the binned completeness
(`s5c_unfold.py:135-145`). **C-COL** (a test, `test_col_weights_do_not_depend_on_interior_edges`) runs the pinned
driver on two grids with the same outer edges and every interior edge moved or dropped. It requires the push weights
bit for bit equal, and grid B's result equal to grid A's saved weights re-histogrammed on grid B with B's denominator.

So one set of push weights serves every binning inside the fiducial box (pT < 4.5, 1.5 ≤ p∥ < 60, E_avail, q3,
W < 100 GeV). What else a rebinning needs depends on the binning:
- **a union of fine cells** (the sixteen cells are): the result is the sum of the fine cells' integrals, each with its
  own saved completeness and flux. That reproduces the released estimator exactly. A fresh extraction that pools one
  completeness and one flux per coarse cell is a different estimator and can differ;
- **a binning that splits fine cells:** the denominator is stored only binned on the fine grid
  (`nn_dump_inputs.py:88-98`), so it needs c at event level, from the denominator rows in the 5D omnifile. A fine
  cell's c can be 1 while its parts are not, so C-COMPLETE's measurement does not license splits, whatever it finds.
  One case in point: the fine grid's pT edges are 0.07 / 0.33 / 0.47, so the paper's 0.075 / 0.325 / 0.475 split
  fine cells. The director has ruled that the 5D result is not compared on those edges in v1.

C-COL shows that the pushes do not change, and that grid B's result is recovered given grid B's own denominator and
flux. It does not supply that denominator.

## 5. Tests and mutants

`test_evw5d.py` (pytest, 79 tests) builds a deploy at the code pin and synthetic inputs on the real fine grid, with
truth rows on the top edges and outside the grid, and a denominator 1.15 times the signal (so C-COMPLETE's finding
fires). It reuses `test_ess_capture.py`'s helpers. Four kinds of test:
- **end to end** through the real driver: PASS; a STOP on a one-ulp reference and on a meta difference; a FAIL on f
  1e-13 away (C-F and C-SELF fail, the files are written, `accepted()` refuses); a wrong pin; an existing `--out`;
  `--out` outside `--out-root` (nothing created); `--fixture` inside Slurm;
- **C-COL** (§4);
- **each control with one fault injected**, each one the exactness gates alone would miss: a shifted key, two weights
  swapped within one cell, a truth value one ulp inside its cell, a flow row's weight, wrong dtypes, a missing or
  extra column or constant, a row moved to another reported cell, the factor read only by the independent formula;
- **the consumer's acceptance:** a changed byte, an extra or missing file, a link (product or marker), a FAIL or
  foreign done marker, a FAIL run whose marker is edited to PASS, a `run.json` recording a failure with the manifest
  and marker re-made to match, a short or CRLF `SHA256SUMS`, a bound digest that differs;
- **the job script's refusals**, run with a fake `squeue` and two small git repositories: a linked log directory or
  log file (nothing is written through it), a writer digest that is not the bound one, a tool clone whose `git
  status` fails, and a setup that returns non-zero.

`evw5d_mutation.py` applies each of its mutants (one exact span of `evw5d.py` or `sbatch_evw5d.sh`) to a copy of the directory and requires
the full suite to fail with a named test; a control must pass. Its result is committed as
`receipts/mutation.json`.

Local environment: Python 3.11.18, numpy 1.26.4, lightgbm 4.6.0 (the cluster's numpy and lightgbm; its Python is
3.11.14). A stub ROOT module stands in off the cluster, as in ESS's test.

## 6. Placement and price

- One `regular` CPU node, exclusive, one srun step of 32 CPUs at 160 G, `#SBATCH -t 00:30:00` (`sbatch_evw5d.sh`).
  Before its first write, the job requires `$OUT` and `$OUT/logs` to be real directories reached through no link and
  each per-job file to be absent; it then creates them exclusively (`noclobber`). It refuses unless:
  - its name is `evw5d` and its limit 30:00;
  - the deploy is a clean clone at the code pin and the tool clone a clean clone at the tool pin, with each git
    command itself succeeding;
  - `evw5d.py`'s bytes equal the bound sha256, checked before Python starts;
  - `setup_salloc_env.sh` returns 0 (it did in both ESS records);
  - `$OUT/evw5d` is absent.
- **Expected about 0.28 node-h; price 0.25 node-h, cap 0.5.** The unfold is ESS's 794 s (`fd/receipts-ess/README.md:37-42`).
  The added steps took 11.4 s on 8.2 M synthetic rows on the laptop (table, maps, write, read-back, C-SELF, C-FLOW),
  so roughly 1–2 min at full size, plus the independent read of the npz.
- The output stays on $SCRATCH with `SHA256SUMS`, is copied to HPSS, and is fetched to the laptop by sha for a
  deposit. **Nothing is written to CFS.** The scripts are in [`launch/`](launch/), adapted from ESS's:
  `evw5d_connect.sh` (preconditions, iris bound, the two clean clones and their pinned bytes, the environment
  pre-check including `os.O_NOATIME`, one sbatch, the TimeLimit check), `evw5d_post.sh` (sacct, the charge, the
  products re-checked against `SHA256SUMS` in place, the small products tarred for the fetch), `evw5d_hpss.sh` (after
  a PASS only: htar with CRC verify, hsi hashcreate/hashverify, every file retrieved and compared by sha256) and
  `evw5d_launch.sh` (the Mac side: each script staged in `/dev/shm` and refused unless its sha256 is the approved one;
  `fetch` and `fetch-products`, the latter checked with `shasum -c`). The tool commit and the approved digests are
  filled in at the binding; until then each script refuses.

## 7. What this is not

- It is not the five-axis purity result's weights (ruling 1), and not physical event ids.
- It changes no result, covariance, uncertainty or note number. It reruns the central unfold only to keep its
  weights.
- The weights are the central value, validated only through the reported result (gates 1 and 2) and for binnings
  within §4's limit.

## 8. Revision 2: codex-school r1's findings and what changed

| # | finding (r1) | change |
|---|---|---|
| 1 | BLOCKING: `accepted()` took a FAIL run whose marker's verdict was edited; a linked marker and a CRLF manifest passed | `accepted()` as in §3: links refused, bytes, the marker cross-checked with the hashed `run.json`, the optional bound digest; tests for each |
| 2 | BLOCKING: the saved `good` and `xsec_flat` were compared only with the builder's own output | C-SELF compares them with the recomputed mask and fb5cc679's result, and the 1e4 and the volumes independently; C-FILE compares the input constants with the independent read; builder-side mutants |
| 3 | BLOCKING: a failing `git status` passed as clean; the writer's digest was not enforced; the setup's rc was ignored | `clean_at` checks each git call; the bound sha256 of `evw5d.py` is checked before Python; setup must return 0; tests |
| 4 | BLOCKING: a linked log directory or log file could redirect a write outside `$OUT` | physical `$OUT` and logs, absent per-job files, `noclobber`; tests |
| 5 | §4 overstated what fine-grid completeness establishes | §4 rewritten |
| 6 | `SELF_F_FILE` is killable (volumes 5e-14 high) | the test added; the mutant moved back into the kill set |

**CITABLE FOR:** what will run, what it writes and what each control checks. **NOT CITABLE FOR:** any number from the
run, which comes from its receipt.
