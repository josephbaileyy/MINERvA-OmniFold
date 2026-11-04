# COV2D amendment 1: the toy, truth, block, null, scorer and readout code, the job scripts and the pilot

**By** the `cov2d` session, 2026-11-04, for **binding 2** (COV2D-DECLARATION.md §10 item 4). It is written under:
- [`COV2D-DECLARATION.md`](COV2D-DECLARATION.md) (the declaration);
- [`COV2D-BINDING-1.md`](COV2D-BINDING-1.md);
- [`COV2D-BINDING-1-A1.md`](COV2D-BINDING-1-A1.md);
- the director's rulings of 2026-11-03 and 2026-11-04, restated below where each applies.

**MEASURES:** nothing; it states code and rules. **CANNOT AUTHORIZE:** any job before binding 2. Then the G18 pseudo-data
job (sha first), then the pilot (sha first, after that job's PASS), then the bulk (after the pilot's readout).

**The STOP count is one**: CONTROL-2A FAIL, 2026-11-03, under COV2D-DECLARATION.md:358-359 via §2 :89. A second STOP
ends (c) unless Joseph rules otherwise.

## 1. What is bound at binding 2

The code is on branch `code/cov2d-amendment-20261104`; its blobs are listed in §9. **Imports, not copies**
(declaration :596-597). Every imported module is used unchanged, at the blob shown.

| imported | blob | used for |
|---|---|---|
| `cov2d.py` (binding 1) | `7dafdd3f` | the bank, draws, `compose`, `lam_plus`, seeds, `weakened_cells`, `OUTLIER_CELL` |
| `cov2d_writer.py` (A1) | `bb3892e5` | `draw_counts`, `expand`, `concat`, `write_data_file` (one tree cycle) |
| `cov2d_receipt.py` (binding 1) | `d5718bf4` | `open_noatime`, `read_noatime`, `universe_columns`, `truth_cell`, `driver_phase_space` |
| `re2_driver.py` (binding 1) | `97f26a1d` | `extract_cross_section_2d`, `load_flux_bins`, `load_flux_universe_bins`, `make_th2d`, the edges, the nucleon count; every unfold |
| `fd_1b_null.py` (binding 1) | `1810161d` | the null: `Discrete`, `null_contents`, `thresholds`, `size`, `chi2_nonnull` |
| `fd_1b_mc.py` (1B) | `74aa8dac` | `grade`: section 5.1-5.2 exactly as 1B grades |
| `re2c_rollup.py` (part C) | `e41940cb` | `universe_block`, `x01`, `flux_weights`, `partb_sums`, `Cells` (S5's own block functions) |
| `build_cmodel.py` (part C) | `7a987e25` | `cmodel`, `matrix_sha256` (C_model and C_model⁻) |
| `re2_k1.py` (RE-2) | `62a1dc33` | `compare`, `xsec`, `TOL` (RE-2's equality rule for (2b) and §9.12) |
| `fd_rpd_inputs.py` (RPD) | `7c2e018f` | `run_check_mat_setup`, `mat_environment` (the pinned MAT environment) |
| `s5e_deform.py`, `pvl_lib.py` (F1) | `2c11f9f6`, `81d509ba` | `ratio_weight`, `FINE`, `AXES5` (r_T) |
| `clip_probe.py` (C1, committed) | `f5683876` | `reco_cell` (the reco-kept rows of section 6 (ii), as C2 took them) |

**The rollup's exact imports** (declaration :218): `re2c_rollup.universe_block(cells, bands, w, minos_x)`, `x01`,
`flux_weights` and `partb_sums`. `band_cov` enters through `universe_block`.

## 2. The rulings this amendment carries (the director, 2026-11-03 and 2026-11-04)

1. **Control (2a) runs as three processes:** read (omnifold_py310), write (root_6_28), check (omnifold_py310, the module
   global `write_data_file` stubbed).
   - This changes how the control is run, not what it compares.
   - Its conditions: patch reach, the digest chain, npz exactness, threads, and the usual clone, porcelain, blob and
     removal rules.
   - Result: FAIL (extra `data;2`/`data;3`, the first STOP), then A1 (`SetAutoSave(0)`), then **PASS** on the rerun
     (`fd/receipts-cov2d/control2a/`).
2. **(2a)'s file is kept** at `/pscratch/sd/j/josephrb/cov2d-2a/writer_control.root`, sha256 `7eb39088…`.
   - The pilot re-checks it before use (`cov2d_jobs.py check`, `$K2A`).
   - A purge or change stops the pilot. A (2a) rerun is a new connect.
3. **A1's test counts:** a cluster test receipt expects `test_cov2d_writer` at 12 tests, 3 ok, 9 skipped where ROOT is
   absent.
4. **Staging.**
   - The pilot and the bulk re-hash each staged copy against `inputs.stat` (sha256 `3614ebad…`,
     `fd/receipts-cov2d/staging/`) before reading it.
   - A mismatch or purge stops the run, with no silent re-stage.
   - **$UNI is not staged.** It is stat-checked (size, mtime, inode) against part B's DTN record and refused on any
     difference: **a weaker pin than sha256, by the same convention as 1B's bank** (171 GB per job is too much to
     re-read).
5. **The MAT environment is pinned** wherever a MINERvA ROOT file is read: the §9.5 control, the pseudo-data job's step
   B, and every unfold job.
   - It uses RPD's binding-2-A1 standard, through RPD's own code: `fd_rpd_inputs.run_check_mat_setup` before sourcing,
     `mat_environment` after.
   - That checks six setup scripts and three MAT files at their digests, libMATDict.so resolving to libMAT.so, the
     files mapped from MINERvA101/opt exactly {libMAT.so}, the two environment variables, and the MnvH1D dictionary.
   - **MAT is not required for step B's MEFHC flux read.** A login check read `pTmu_reweightedflux_integrated` from the
     real `runEventLoopMC_MEFHC.root` (sha256 `d40aea69…`) with `re2_driver.load_flux_bins` in plain root_6_28 and in
     the pinned MAT environment. It is a TH1D, both reads succeeded, and the 14 bins were equal
     (`fd/receipts-cov2d/amendment/flux_check/FLUX-CHECK.md`). Step B still runs under the pinned MAT environment, as
     the director ruled.
6. **The E3 template for LightGBM runs:**
   - sbatch on one node, pinned by Slurm's allocation;
   - TMPDIR and threads reset in the job, because the submitting shell's TMPDIR leaked through sbatch.
7. **R1, the §9.4 reference:** `extract_cross_section_2d(hTruth2D, hOFCompleteness2D, …)` from E_R's own file, with two
   cross-checks: hTruth2D equals hOFInputTruth2D, and hOFTruthDenom2D at completeness 1 equals the reference.
   - At the CV the pseudo-data job counts three things:
     - (a) truth rows with w ≥ 1e4;
     - (b) in-box rows outside `in_truth_phase_space`;
     - (c) non-finite rows.
   - If all three are 0, §9.4 runs as declared at 1e-12.
   - If any is nonzero, the job stops before any count is written and the counts go to the director. **The truth
     definition is the director's**, not the code's.
8. **R2:** §9.4 and §9.6 run inside each pseudo-data job before any data file is written. §9.5 is a login connect
   before the pilot (done: **PASS**, `fd/receipts-cov2d/control95/`). §9.8–9.10 are asserts.
9. **R3:** C08_R is part C's `outA/cov2d_Q_205.npz` key `c08`, sha256 `7153b194…` (RE2-PARTC-REPORT.md:134,
   :364-365).
   - **C_model⁻ is "constructed from the committed shift matrix, not a named part-C product"**: `build_cmodel.cmodel`
     over the `nuwro` and `gibuu` rows of `pv2d/cmodel/cmodel_2d.json` (sha256 `aabc66d1…`).
   - Its control: the same construction over all three vertices must reproduce C_model's matrix sha256 `11fe6818…`,
     or the C_T⁻ readout is INVALID.
   - It is descriptive only and changes no verdict.
10. **R4:** the surrogates apply in the table's order, the lateral first, then the normalization. A test fixes it, and
    the non-commuting term is reported in σ_c, descriptively.
11. **R5, the seeds, verbatim:**
    - toys: G18 **5,720,000–5,720,299**, AR23 **5,730,000–5,730,299**;
    - realizations: 5,721,000 and 5,731,000;
    - null: **5,742,000**.
    The code passes `cov2d.NULL_SEED` and 205 cells explicitly; fd_1b_null's defaults are 1B's.
12. **R6, the blocks:** `universe_block` is called with a cells object holding E_R's 205-cell mask and x = x̂_T. Two
    tests guard the layout:
    - the per-band dict must hold exactly 38 universe bands, 5 lateral bands (X01 for Muon_Energy_MINOS) and the
      normalization entry;
    - the blocks must sum to the function's total.
    C_univ and C_lat come from the dict, and the normalization is counted once.
13. **§9.11's "within 5 Poisson σ of Σλ⁺"** compares d̃_T's written total with Σλ⁺ over the rows the writer keeps (the
    passing rows). Both sums are recorded.
14. **The pilot (ruling (A)):** the G18 pseudo-data job is its own submission at binding 2, with its sha sent first. Its
    PASS (step A's counts and digests, step B's §9.11 read-back, §9.4 and §9.6) is read before the pilot. A pseudo-data
    failure stops before any unfold. The reserves stay as declared.
15. **A declared departure (ruling (b)):** the full CFS-read lateral of §8 :432-433 and §10 :549 is **replaced** by one
    timed O_NOATIME read of the first 4 GB of the CFS lateral beside its staged copy, inside the pilot.
    - The reason: staging is complete (STAGE PASS), so §4.4's CFS fallback cannot arise.
    - If staging were ever lost before the bulk, the run stops (rule 4), and a CFS route would need its own amendment.

## 3. The pseudo-data job (§4.1–4.4, §6 (ii), §9.4, §9.6, §9.11)

`cov2d_pseudo.py`, step A, in omnifold_py310, reads $UNI once through O_NOATIME. For one truth's 300 toys and d̃_T it:
- composes each nature with `cov2d.compose` in draw order;
- applies r_T from one `ratio_weight` call on the concatenation of the truth rows and the signal rows (signal weight 0);
- draws the counts with `cov2d_writer.draw_counts` from `default_rng([seed, DRAW_SALT, 1])`;
- clips the truth row by row;
- records λ⁺'s records, the per-cell sums behind R_c (S_c, m_seen, N_c, m_all), the per-reco-cell negative mass and
  signed signal λ, the non-finite weights zeroed, and the outlier cell's negative rows.

Section 9.6 and the R1 counts stop it before any count is written. Chunking is invariant: a test shows chunked Poisson
draws equal one call. It refuses if $UNI's signal tree lacks the 5D truth.

`cov2d_pseudo_write.py`, step B, runs in root_6_28 under the pinned MAT environment:
- §9.4 first;
- then each data file through the bound writer (with $CV's dataPOTUsed), read back for §9.11, its sha256 recorded;
- then each nature's truth cross section with the drawn Flux universe's integral at completeness 1.

## 4. Blocks, null, scorer, readouts (§4.4, §5, §6, §9.5, §9.8)

- **`cov2d_blocks.py`:** C_T = C_univ + C_lat + C_norm + C_stat (ddof 1) + C08 (carried) + C_model_abs, with C_model⁻.
  §9.8 checks symmetry and PSD at 1e-12 and records the ndf.
  - The §9.5 control (`control95`) carries the director's **open audit**. builtins.open, io.open, os.open and
    ROOT.TFile.Open are wrapped before the rollup is imported. Any open under /global/cfs or /pscratch that is not a
    sanctioned O_NOATIME read is refused.
  - A bypass scan lists subprocess calls, TFile constructors and copied constants.
  - **Measured limit:** a `ROOT.TFile(path)` constructor call skips `TFile.Open`, and opens inside ROOT's C++ are not
    visible to Python wrappers; the scan covers the first.
- **`cov2d_null.py`:** one `Discrete` law per drawn band, from the same unfold outputs as the blocks, plus the Gaussian
  C_stat + C_norm + C08 + C_model_abs. fd_1b_null runs at seed 5,742,000 with 205 cells.
  - C_T⁻'s null is built in the same step, before any toy error is read, with C_model⁻ in place of C_model in the
    Gaussian and the same seed, as 1B builds both of its nulls in its null step (fd_1b_mc.py:740).
  - A test drives the real path, `assemble` → `re2c_rollup.universe_block` → `build_repair.wcov` → `null_at_T`, and
    requires check_matched ≤ 1e-12 for both nulls in four regimes.
- **`cov2d_score.py`:** the R4 surrogates, then e on E_R's 205 cells, then `fd_1b_mc.grade` unchanged.
  - It refuses unless E has exactly the truth's 300 declared toys (§5.2's rule is Bin(300, …)) and the outlier cell
    is among the 205.
  - The cross term is reported in σ_c = √diag C_T.
  - It adds the weakened-pass labels from `cov2d.weakened_cells` of C2's record (a flagged cell is never labelled), the
    share beside the joint reading, the outlier cell, and INVALID when a §9 control fails, keeping the graded verdict
    beside it.
- **`cov2d_readouts.py`:** §6's readouts:
  - the spread alone, the bias and the predicted offset (over the 38 drawn universe bands; the lateral surrogate is
    centred);
  - C_T⁻ against its own null (built in the null step), read with 1B's three texts verbatim (fd_1b_mc.py:803–808):
    "covers without the GENIE + MEC shift", "its coverage in cells […] (and jointly) rests on the GENIE + MEC
    shift", and "printed; no reading (the tune under-covers under C_T)". A cell is named by its flat index where 1B
    writes R⟨cc⟩;
  - the realization check;
  - (ii) R_c with the fixed 0.5 σ_c reading and C2's prediction (0.043/0.042 σ_Q). A missing R_c is counted, and
    enters the coherent offset as 0. Since a 0 can only shrink the offset, it is also reported over the toys with no
    missing cell. It refuses unless the rows it reads are the truth's toys in seed order (step A's `seeds`) and the
    outlier cell is among the 205;
  - (i) a login-node cross-terms CLI over the 600 draws. Its "product composition" is C2's definition:
    a_CV ∏ (a_uj/a_CV) where a_CV > 0 and every drawn a_uj > 0, else 0 (`clip_probe2.py:19-20, 273-292`). C2 applied
    it to the truth tree; here it is applied to the reco histogram. The unit is √F, F being that draw's first-order
    expected count in the reco cell. (Cell, draw) pairs with F ≤ 0 are excluded and counted. F and P are saved per draw.
  - Every readout record says whether its pins were checked (`pins_checked`), as do steps A and B.

## 5. Job scripts, packing and price (§8, §10)

- **`jobs/cov2d_jobs.py`:**
  - **Tables:** each truth's 786 runs, with part B's argv per class plus `--data-file`: J1 for the central run and the
    toys, J2 for the universes, J3 for the laterals, J4 for the replicas.
  - **Packing**, as declared: 4 universe jobs (2 × 128), 1 lateral-and-central job (2 × 128), and 3 replica and 3 toy
    jobs (4 × 64).
  - **Limits:** ceil-to-the-minute of 1.25 × (longest lane + 300 s), the rule that reproduces part B's limits. All are
    under 12 h.
  - **Check:** rule 4's input checks, plus the flux pins, through O_NOATIME.
  - **Gate:** ended attempts at elapsed time, plus unfinished ones at their limit, plus this job's limit, at most
    **165.8 node-h**. It prices every cov2d job of the user, the pilot and the pseudo-data jobs included, and refuses
    a cov2d job name it cannot price.
  - **Order** (COV2D-DECLARATION.md:40, §10 steps 5–6; ruling (A); audit J1): `cov2d_jobs.order`, called by
    `cov2d_submit.sh` before the gate, reads PASS records committed on origin/main that name the deploy's commit M:
    1. the G18 pseudo-data job first;
    2. the pilot after G18's pseudo-data PASS (`fd/receipts-cov2d/pseudo/G18/pseudo_b.json`);
    3. AR23's pseudo-data job and every unfold job after the pilot readout's PASS
       (`fd/receipts-cov2d/pilot/pilot_readout.json`);
    4. the eight universe jobs (the $UNI readers) after both pseudo-data PASSes;
    5. the rest after all eight universe jobs are submitted.
  - **Waves under the gate** (audit J6). The limits: 8 universe jobs at 08:54:00, 6 replica jobs at 08:06:00, 6 toy
    jobs at 07:38:00, 2 lateral-and-central jobs at 03:20:00, 2 pseudo-data jobs at 03:00:00 and the pilot at
    01:41:00. They sum to **179.95 node-h**, above the 165.8 cap; the projected wall is **144.95 node-h** (the 24 unfold
    jobs at part B's per-run estimates, the pilot at its estimate, the pseudo-data jobs at their limits).
    - Steps 1–4 (two pseudo-data jobs, the pilot, the eight universe jobs) hold **78.88 node-h** of limits. The other 14
      jobs hold **101.07**. So while steps 1–4 are all unfinished, some of the 14 must wait: the gate refuses a
      submission, which is a wait, not a STOP, and the job goes in once earlier jobs end and are charged at their
      elapsed time.
    - **The gate's at-limit accounting keeps the campaign's total ≤ 165.8 node-h.** At each submission it requires
      (elapsed of ended attempts) + (limit of unfinished ones) + (the new job's limit) ≤ 165.8. After a submission, the
      sum can only fall: an unfinished job ends at or before its limit, so its limit is replaced by an elapsed time no
      larger. Every attempt, a failed one or a retry included, goes through the gate. So the final charge is at most
      the sum at the last submission, which is at most 165.8. This holds provided no job runs past its limit, which
      Slurm enforces.
- **The scripts:** `cov2d_job.sbatch` (part B's lanes and OI-136 guard, a digest per finished run, each run's own rc
  and wall for REPRICE), `cov2d_pseudo.sbatch` (QOS and TimeLimit checked, threads and TMPDIR reset, $UNI stat-checked,
  then step A, then step B), `cov2d_env.sh`, `cov2d_submit.sh`. The submit script refuses unless COV2D-BINDING-2.md
  names the deploy's commit. It regenerates the tables at each submission and compares them with the deployed ones.
- **The pilot** (`cov2d_pilot.py`): eight runs in three lanes on one node, limit **01:41:00** (1.68 node-h, within
  the 2.0 reserve and the 02:00:00 ruling). Each control runs on its part B reference's CPU count, since RE-2 states
  equality only like for like (RE2-DECLARATION.md:234):
  - lane 1, 128 CPUs: §9.12's lateral (P912_L, as S3_BeamAngleX0), the G18 lateral, §9.12's universe (P912_U_MaRES_0,
    as U_MaRES_0 in J2b);
  - lane 2, 64 CPUs: (2b) (P2b_ER, as ER), x̂_T, one toy;
  - lane 3, 64 CPUs: one replica, one G18 universe (a route test at 64 CPUs, not a REPRICE measurement).
  - **The pass rule** for (2b) and §9.12: max relative difference ≤ `re2_k1.TOL` on E_R's 205 cells, and the same
    reported-cell set, each reference copied through O_NOATIME at its pin. This is `re2_k1.check_row`'s rule for
    hXSec2D (re2_k1.py:268) restated: there `(same_cell_set or hist != "hXSec2D")` reduces to `same_cell_set`, and
    the reference pin plays the role of `ref_sha256_ok`. The pilot reads its own new products without O_NOATIME:
    they are lane outputs, not §7 inputs.
  - **INVALID** (§9.13): any of the eight runs without rc 0 and a digest, any REPRICE class without a wall, or a
    missing part B product. A (2b) or §9.12 failure is the second STOP.
  - **REPRICE, like for like:** a class reprices when the pilot's run-only wall per run exceeds 1.25 × part B's
    run-only wall per run. Part B's is (elapsed − the declared 300 s preflight) × min(lanes, runs) / runs, from its
    committed ledger and `partb_jobs.tsv`. **The effective triggers:**

    | class | part B's run-only wall per run | trigger (1.25 ×) | the bulk's per-run estimate |
    |---|---:|---:|---:|
    | central, toy | 610.0 s (J1) | 762.5 s | 866 s |
    | universe (128 CPUs) | 864.9 s (J2a–d) | 1,081.1 s | 1,150 s |
    | lateral | 1,174.8 s (J3) | 1,468.5 s | 1,678 s |
    | replica | 691.7 s (J4a–c) | 864.6 s | 920 s |

    Two differences remain, and both make the trigger slightly looser on pure run time. J1's three runs each had a
    lane, so its figure is the longest of the three. Part B's multi-run lanes include the gaps between srun steps,
    which the pilot's step walls exclude. Every trigger lies below the per-run estimate the bulk's limits are built
    on, so REPRICE fires before a limit is at risk.
  - **The DVS read** (ruling (b)): a timed O_NOATIME read of the first 4 GiB of the CFS lateral beside its staged copy,
    run before `check` re-hashes the staged copy. The CFS figure is cold. The record notes that the staged figure may
    still be a page-cache read left by another process on that node.

## 6. Controls: where each runs

| § | control | where | status |
|---|---|---|---|
| 9.3 | (2a) the writer | login, three processes | PASS (rerun) |
| 9.3 | (2b) E_R reproduced | the pilot | pending |
| 9.4 | the truth computation | each pseudo-data job, step B first | pending |
| 9.5 | the blocks reproduce S5_R | login connect | **PASS**, 4.59e-16 |
| 9.6 | single-universe compose | each pseudo-data job, step A, every chunk | pending |
| 9.7 | check_matched before any toy is read | the null | asserted |
| 9.8 | C_T symmetric, PSD, ndf | the blocks | asserted |
| 9.9 | one code, one input set; declared seeds | tables, runs, records | asserted |
| 9.10 | truth pins | step A (`committed_ratio_sha256`) | asserted |
| 9.11 | pseudo-data content | each pseudo-data job, step B | pending |
| 9.12 | universe and lateral routes | the pilot | pending; its references' cell sets equal E_R's 205 (login check, **PASS**, `fd/receipts-cov2d/amendment/cell_check/`) |
| 9.13 | no run dropped or re-seeded; a failure is INVALID | every job | rule |

## 7. Statements the declaration asks the amendment to make

- **Imports:** §1.
- **Seeds:** rule 11.
- **Rules unimplementable as written:** none found. Two readings are made explicit and were ruled:
  - §9.4's reference (rule 7): E_R carries no `hTruthXSec2D`;
  - §9.11's population (rule 13).
- **Declared departure:** rule 15.
- **REPRICE:** decided after the pilot, at the effective triggers in §5.
- **The waves:** §5.

## 8. Tests and mutants

At `0d43c9a3`, in one environment holding PyROOT, uproot and numpy (ROOT 6.28/12, uproot 5.6.9): **112 tests, 0
skipped, all pass** (`fd/receipts-cov2d/amendment/suites_0d43c9a3.txt`). This was a local run. The table names the
environment each module runs in on the cluster, which is not the environment of this test run.

| module | tests | runs in |
|---|---:|---|
| step A | 16 | omnifold_py310 (no ROOT) |
| step B | 10 | root_6_28 + the pinned MAT environment |
| blocks | 25 | root_6_28 (the real-path null test included) |
| null | 5 | numpy |
| scorer | 12 | numpy |
| readouts | 12 | numpy + uproot (the cross-terms CLI) |
| jobs | 22 | every generated line through `re2_driver`'s real parser (needs PyROOT): 786 per truth and 8 for the pilot |
| pilot | 10 | PyROOT |

**Mutants:** `fd/receipts-cov2d/amendment/mutation_amendment.py`, 51 mutants over the eight modules, one guard or
declared rule each; **51 killed** (`mutation_amendment.txt`). The first run of the 51 left one survivor ("a missing
class is not INVALID", `mutation_amendment.run1.txt`); the test that reaches that check alone was added before the
commit. The rolling audit's findings and the answers are in `fd/receipts-cov2d/amendment/` (`AUDIT-PART*.md`,
`ANSWERS.md`), with the flux check in `flux_check/`.

## 9. The code's blobs at the binding commit

The code commit is `0d43c9a300fa02cea8e25557f431e65ce33c8ebc`. Binding 2 names the commit that carries this amendment.
These blobs are unchanged there, since it changes no code. The imported modules are in §1.

| file | blob |
|---|---|
| `2d-unfolding/cov2d/cov2d.py` | `7dafdd3ff827378554931bd1b3d1f19aeeabe11d` |
| `2d-unfolding/cov2d/cov2d_blocks.py` | `b9e63a3827e44c31a529f8d92482b7d7969d8223` |
| `2d-unfolding/cov2d/cov2d_null.py` | `59d9721cefbcd1276348e7ee183007160954e49d` |
| `2d-unfolding/cov2d/cov2d_pilot.py` | `cfbe69a787ffcd2aa8ba7c787ccd956249592c26` |
| `2d-unfolding/cov2d/cov2d_pseudo.py` | `47ecfd8c26b35ed1f476d7568467d3b472402523` |
| `2d-unfolding/cov2d/cov2d_pseudo_write.py` | `e6124ab0819fcd0803a5e3269f610d8c592321c0` |
| `2d-unfolding/cov2d/cov2d_readouts.py` | `7e6407c4308500e1f622dfe870b8f8f314e1a7fc` |
| `2d-unfolding/cov2d/cov2d_receipt.py` | `d5718bf44c2084c20c30a8b8614e9c40e6fbeee3` |
| `2d-unfolding/cov2d/cov2d_score.py` | `282fd27ec07c84b4f9a0f287004eca0133858c15` |
| `2d-unfolding/cov2d/cov2d_writer.py` | `bb3892e5447d37ee524c720c5ab623baa7184f30` |
| `2d-unfolding/cov2d/jobs/cov2d_env.sh` | `822696007afa8816e982984cc8ca0b39951ef2a3` |
| `2d-unfolding/cov2d/jobs/cov2d_job.sbatch` | `0e64f14a2c15728b0274bda30ad2cd1fe83a562a` |
| `2d-unfolding/cov2d/jobs/cov2d_jobs.py` | `7cc8ec846f48ff278d4ad0774876701cc0164855` |
| `2d-unfolding/cov2d/jobs/cov2d_pseudo.sbatch` | `0299633fed74300f9efb66add7b05bf77b00c424` |
| `2d-unfolding/cov2d/jobs/cov2d_submit.sh` | `03ad296e3a39be50d654e15b8819e6fa6e910ae6` |

Their tests:

| file | blob |
|---|---|
| `2d-unfolding/cov2d/tests/test_cov2d_blocks.py` | `7e8da5b37ac170d0f7eb2803afd17036523b0da6` |
| `2d-unfolding/cov2d/tests/test_cov2d_jobs.py` | `ca030e6d6d0ed5f00dd817609e78db2f1a03316c` |
| `2d-unfolding/cov2d/tests/test_cov2d_null.py` | `3002455578509d6d4be06a08e4fa17105f06492d` |
| `2d-unfolding/cov2d/tests/test_cov2d_pilot.py` | `2424ff270509f18580f265705241928c55944493` |
| `2d-unfolding/cov2d/tests/test_cov2d_pseudo.py` | `452f4f7e738108c664d7b8b9d13dc82cd7d3bb41` |
| `2d-unfolding/cov2d/tests/test_cov2d_pseudo_write.py` | `eccb43a4c7235942b0fe110312438c64d29d2973` |
| `2d-unfolding/cov2d/tests/test_cov2d_readouts.py` | `1b2be505bb839e889eb968c07e4708a9a2bcd5b9` |
| `2d-unfolding/cov2d/tests/test_cov2d_score.py` | `25aa147442296ef4b22ed0ac43c712f604a73ec4` |
