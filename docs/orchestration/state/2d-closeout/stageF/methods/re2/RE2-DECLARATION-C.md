# RE-2 declaration, part C: post-processing of the refined 2D rebuild (2026-10-24, re-1 lane)

**Status.** A declaration, for the director to bind. **No refined post-processing has run.** The purity arm of
every copy has run once, as the K1-roll the director allowed before binding (ruling Q1, conditions (a)–(d)). It
reproduced every committed purity product: 36 of 36 comparisons, and Fig. 1's PDF byte for byte. The run touched no
refined product (§4.1).

**What part C produces, from part B's 644 refined unfolds (RE2-PARTB-REPORT.md):**
- `E_R`'s covariance `Q_R` = S5_R total + C_PL_R. Each block is built as S5, C_PL and the combination were; only
  the estimator changes.
- Its products and budget (`budget_Q.json`).
- The comparison with MINERvA's published result, recomputed on `E_R` and `Q_R`:
  - the "~1 %" total ratio;
  - the agreement windows and the median bin ratio;
  - the pulls;
  - χ² against the published covariance and against the combined covariance;
  - the tension and Tune v1 numbers.
- The figures that read `E_R` or `Q_R`.
- RO-FPS.
- The secondary users' total `Q_R + C_model` beside `Q_R` (DECISION-20261024).
- **A values table:** every printed number that derives from `E_U` or Q (251 rows), each with its regenerated
  value. A number is regenerated only after its current printed value has been reproduced from its committed
  source.

**MEASURES:**
- the refined 2D result's covariance blocks and their budget;
- the published comparison on `E_R` and `Q_R`;
- the C_model term beside `Q_R`.

**CANNOT AUTHORIZE:**
- adopting `E_R` and `Q_R`, which is Joseph's decision, from part C's report;
- folding C_model into `Q_R` (DECISION-20261024 item 1: `Q_R` stays the headline);
- any printed wording, which is Joseph's (DECISION-20261024 item 3);
- an edit to `docs/analysis-note/*.tex`, which is the integration step's (§6.4);
- a coverage statement about `Q_R` (RE2-PLAN §7).

**Based on** `origin/main` `39312fcc`. The code is on branch `re2/partc-declaration`. The director's preliminary
rulings on the design (Q1–Q4, gaps 1–5) are recorded in §11.

---

## 1. What part C covers

It is RE2-DECLARATION-B §6's list, with every gap the survey found added. The chain is Stage C, then Stage F, in
order:

| step | original (sha256) | copy, or how it runs | product |
|---|---|---|---|
| C1 analyze | `stageC/production/analyze_prod.py` (`f9e0d8f2…`) | `re2c_analyze.py` | item records c0, s3, s4ii, s1, s4i |
| C2 rollup | `stageC/production/s5_rollup.py` (`6c437004…`) | `re2c_rollup.py` | S5_R: `production_cov.npz`, `s5.json`, ROOT |
| C3 work_cov | `playlist-spread-20261014/coverage/scripts/export_cov.py` (`d3b9c5cb…`) | `re2c_export_cov.py` | `work_cov.npz` with `E_R` |
| C4 periods | `period-unfold-20261014/scripts/periods.py` (`d37c1a8f…`), `analyze_periods.py` (`912af1dd…`) | `re2c_periods.py`, `re2c_analyze_periods.py` | selftest, control, roles, `analysis.json` |
| C5 C_PL | `playlist-term/scripts/playlist_term.py` (`b21d03ce…`) | `re2c_playlist_term.py` | C_PL_R: `playlist_term.npz/.json` |
| C6 Q_R | `playlist-term/scripts/combine_s5.py` (`0c6ac3a0…`) | `re2c_combine.py` | `s5_plus_playlist.npz`, `combination.json` |
| C7 budget | `stageF/rebuild/scripts/build_q_products.py` (`050c5b0d…`) | `re2c_build_q.py` | `budget_Q.json`, `cov2d_Q_205.npz`, the block ROOT files |
| C8 χ² and figures | `run_rebuild.sh` steps C and D (`1f4d16d4…`) | `re2c_run.sh`, the same producers with `--ours E_R` | `chi2_Q_*.txt`, `ours_only_*.txt`, Figs. 6/7, the stat figures |
| C8b same-run checks | `stageF/rebuild/scripts/check_rebuild.py` steps C and D (CR-02, CR-03) | `re2c_check_rebuild.py`; step B (CR-01) compared two purity archives and has no counterpart | `checks.json` |
| C9 published comparison | P12: `agreement_windows_receipt.py`, `compare_to_paper_fullcov.py`, `receipt_model_chi2_2d.py`, `compare_to_models.py`, `diagnose_tension.py`, and `make_figures.sh:35-42`'s plots | `re2c_run.sh`, the producers unchanged, `--ours E_R` | the receipts and figures |
| C10 Fig. 1 | `stageF/rebuild/scripts/make_fig1_q.py` (`7710d601…`), with `remote_reduce.json` | `re2c_fig1.py`, run by `re2c_fig1_local.sh`; new `re2c_reduce.py` | Fig. 1 (laptop, recorded environment) |
| C11 numbers | RE-1's `re1_f_numbers.py`, `re1_report2_extras.py` (imported); `lgbm_central_metrics.py`'s learner definition | new `re2c_numbers.py` | 3D-vs-2D, learner, `E_R − E_U` in `Q_R`'s σ |
| C12 C_model | `2d-unfolding/pv2d/cmodel/build_cmodel.py` (imported) | new `re2c_cmodel.py` | `Q_R + C_model`, secondary |
| C13 values | — | new `re2c_values.py` with `re2c_values_spec.tsv` | `values_table.tsv/.json` |
| C14 HPSS | `run/launch/re2_hpss.sh` | its parameterized version | part C's bundle (§9) |

**Two corrections to RE2-PLAN:**
- **P13** said Fig. 1's reducer had no committed producer. `next-preparation-20261009/two-d-path/remote_reduce.py`
  is committed with its JSON (`ebcba79c`). It names `E_U` as "CV42_universe_file", so part C writes a reduction that
  names `E_R` explicitly (`re2c_reduce.py`, §3.8).
- **P12's producers** were not in RE2-DECLARATION-B §6's list. They need no copy: each takes `--ours`, so part C
  runs them unchanged, with `--ours E_R` and its argv committed (`re2c_run.sh`), after a purity K1 with `--ours E_U`.
  - The original runs' argv was never committed.
  - The K1 reproduces their committed printouts and receipts line for line (§4.1). That establishes the argv.

## 2. Code

### 2.1 The copies

Each copy has an `--arm purity|refined` switch.
- **The purity arm is the original code path,** and it must reproduce the original's committed products (§4.1).
- **The refined arm changes only** pins, a mode guard, and the identities `run/partb_identities.tsv` marks X. Each
  is named in the copy's docstring and in §3.
- **The diff of each copy against its original** is committed in `2d-unfolding/re2/partc/diffs/` (`make_diffs.sh`).
  `test_re2c.py` fails if a diff is stale.
- **A purity path cannot lose code unseen.** Every line a copy removes from its original must reappear in the
  copy, or be one of the reviewed lines in `diffs/removed_lines.json`. Those are 65 lines: docstring heads, pins and
  paths the refined arm generalizes, and calls that gained an argument. The test requires that set exactly, both
  ways.
- **The purity arm's changes, all shown harmless by the K1-roll:**
  - the C_PL and combination copies import the period copies (`re2c_analyze_periods.py`, `re2c_periods.py`, each
    pinned by sha256, PT-01/CB-01), not the 10-14 cluster record copies;
  - the period mode guard also runs in the purity arm. It requires each period run's driver `74a4ed69…` and
    `bkg_mode` purity or absent, and every purity run passes;
  - some records gain an `arm` field: the analyze items, `cov_controls.json`, and the refined arm's npz and json.

### 2.2 New code

| file | does |
|---|---|
| `re2c_run.sh` | runs either arm on a login node, in order; records each step's argv, status and time; stops on any failure and at 15 minutes (`timeout 900`); in the refined arm, each product's sha256 is the next step's pin (`chain.json`) |
| `re2c_check_rebuild.py` | `check_rebuild.py`'s same-run checks: CR-02, the cell-identity pass lines; CR-03, the Fig. 6/7 projections equal to `budget_Q`'s to 1e-12 |
| `re2c_fig1_local.sh` | C10 on the laptop: fetches the inputs by their digests (the purity ones from `RUN-fig1.txt`, the refined ones from `chain.json`), refuses another environment, writes the inset's `\uqMedian` from the same arm's `budget_Q.json`, runs `re2c_fig1.py`, writes `RUN-fig1.txt` (environment, commit, script digest, argv, digests), and copies the refined outputs into `$B/partc/fig1/` |
| `re2c_dryrun.sh` | the purity dry run under `strace`, with a 15-minute stop, then the audit |
| `re2c_audit.py` | from `strace -f -y -e trace=%file`: fails if any refined product (part B's or J0's outputs, or their HPSS bundle) was touched by any file call, `stat` included, or if any write fell outside the dry-run directory; it resolves relative paths through descriptors and each process's chdirs |
| `re2c_k1roll.py` | compares the purity outputs with their committed originals (§4.1) |
| `re2c_reduce.py` | Fig. 1's central values, with `E_C`, `E_U` and `E_R` each under its own name; stops unless `E_C` and `E_U` equal the committed reduction exactly |
| `re2c_numbers.py` | the printed numbers that compare another product with the 2D central value (RE-1's definitions, imported), and RE2-PLAN §5.3's descriptive readouts: `E_R − E_U` in `Q_R`'s σ, and per block (Q, S5, universe, stat, C08, C_PL) the per-cell ratio of the refined relative σ to the purity one, with percentiles |
| `re2c_cmodel.py` | C_model beside `Q_R` (§5) |
| `re2c_values.py`, `re2c_values_spec.tsv` | the values table (§6) |
| `pin_siblings.py`, `make_diffs.sh` | maintenance: the sibling pins and the copy diffs |

### 2.3 Tests

`python3 -m unittest test_re2c -v` (numpy only) passes 15 of 15:
- the sibling pins are current;
- the copy diffs are current, and the removed lines are exactly the reviewed set;
- the values engine's three gates (anchor, positive control, refined source) each fire on a bad row and stay
  silent on a good one;
  - a declared failure is listed without being fatal, and a declared failure that starts passing is flagged;
  - a purity-only run writes no regenerated value;
- the values spec resolves in the refined layout: a stand-in refined tree built from the purity sources, and every
  row must regenerate (the review's B1);
- the period mode guard, in both arms and both directions;
- the K1-roll comparator's helpers;
- C_model's arithmetic beside Q (`Q` unmodified; diag = diag Q + Σ s² x²; rank 3).

**Not exercised before binding: the refined arm on real inputs.** Running it would be the post-processing run
itself. Every refined step stops on a failed check (§4.3). A failure in part C's own code, as opposed to the data, is
reported to the director and repaired only by an amendment.

## 3. What each refined step changes

### 3.1 C1, `re2c_analyze.py` (AP rows)

**Inputs.**
- Part B's outputs are read under their own labels: the name map drops `2dc_P_` (gap 3).
- **A disclosure (AP-03):** the refined arm still re-hashes the purity reference pins. A purged purity reference
  would therefore make an item INCONCLUSIVE, which is a stop, not a silent pass.
- Each output must equal its committed `SHA256SUMS` digest (`run/partb_readout/sums/`); otherwise it counts as
  missing.

**Provenance.**
- The driver must be `re2_driver.py` `38ff3705…`, for both the unfolds and the replicas.
- The mode guard is `negweight-refined` with 400/31.
- The input paths are the staged ones the runs recorded (gap 2). The staged CV and laterals were deleted under B9,
  so they are not re-read. `preflight/inputs.stat` (`89595b3e…`, pinned) ties each staged path to its CFS
  original's digest:
  - the CV's digest must be `43f8cc16…`;
  - each of the 10 laterals' recorded digests must equal its row of the CFS lateral `SHA256SUMS`, whose own digest
    is pinned (`73775251…`).
  - This gates both c0 and s3.
- **The refinement record** (AP-22, DRV-02, AP-17). Part B's readout checked every run's refinement health and
  parameters (`k1_core.json`'s 605 and `k1_j7.json`'s 39 health rows, pinned and required to PASS). C2 re-reads them
  for every input: 400 trees, 31 leaves, and `random_state` = the run's seed + 3.

**The replaced identities** (AP-09/10/13/15/18), read from part B's pinned readouts (`k1_core.json` `7c407e95…`,
`k1_j7.json` `faa4656d…`):

| item | refined readout rows |
|---|---|
| c0 | PB-unit, PB-unit-J0; PB-ER-rep, PB-ER-D2, PB-ER-J0, PB-ER-eff |
| s3 | PB-J0-S3_BeamAngleX0 (the MINOS0 pilot check has no refined reference) |
| s4ii | PB-panel-* for six of the seven panel universes |
| s1 | PB-J0-S1_001–008 and PB-stream-S1_*, 300 |
| s4i | PB-stream-S4B_*, 80 |

**What is unchanged:**
- s3's closure check (completeness = 1 on the 205 cells);
- s4ii's null-universe identity against the CV at each seed;
- every provenance check.

**What has no refined reference.** `Muon_Energy_MINOS:0` has no J2 partner (gap 4). It is recorded as "NO REFINED
REFERENCE", and S4ii's verdict is over the other six. The S3 MINOS0 pilot check is recorded the same way.

**s2 does not run:** J5 was not bound.

### 3.2 C2, `re2c_rollup.py` (S5 rows)

**The central value.** The reported cells, the R6 normalization, the centring offsets and the functionals' grid
come from `E_R` (part B's `ER`, `a5c13fc3…`). Its reported set must equal `E_U`'s.

**The May control** still runs on the purity May sweep against VL175, with a separately pinned `E_U` as its own
denominator (gap 1, S5-08). So it is the same control.

**The universe block** is part B's J2: 38 bands and 175 universes (S5-09/10).
- Its band set must equal the July set less the 5 laterals and Rvp1pi.
- Every input must equal its committed digest and record the refined mode (S5-G).

**The analysis gate** reads C1's refined items (each must carry `arm` = refined) and part B's readouts, which must
PASS.

**S5-22: there is no S2.** The bkg-only separable term is not computed, and the npz has no `bkg_separable` key. The
npz carries `arm` = refined (CB-G). <!-- absence-ok: J5 was not bound (RE2-BINDING-B, R10); the refined rollup's code skips the S2 block by design, which re2c_rollup.py's refined branch implements -->

### 3.3 C3, `re2c_export_cov.py` (EX rows)

- **The central value:** the npz key `EU` holds `E_R` (EX-07). The key keeps its name, because three consumers read
  it by name. The npz's arm is recorded in its controls JSON.
- **The mode guard** on `E_R` (EX-G).
- **The block-sum control** (VL175's 6.0898 %) uses `E_U` as its denominator, and in the refined arm it stops
  (EX-04).
- **The metric is unchanged.** The VL175 and ML blocks and the May universes stay as they are (ruling Q2).
- **The E_R-relative median** of the same block sum is reported beside the control, with no threshold (EX-04's second
  half).

### 3.4 C4, the periods (PD, PA rows)

**Pins.** `set_arm("refined", work_cov=…)` repoints only these, under the same keys:

| key | refined pin |
|---|---|
| `E_U` | `E_R`, in the central value's role |
| `XR_L0` | J0's refined `D_cv`, `0835a328…` (PA-05b) |
| `work_cov` | C3's product, by the digest C3 recorded |
| `producer` | `re2_driver.py` |

**The mode guard.** Every period run's driver and mode is checked (PA-02, PT-G). In the refined arm, each run's
sha256 must also equal its committed part-B digest. The selftest's synthetic roles are `E_U` copies with no driver
record, so the guard runs on the period runs, not inside `load()`.

**The control** compares `pu_CTRL_s42` with `E_R` and `D_cv` at 1e-8. Unlike the original, it exits nonzero unless
it passes (PA-05c).

**The χ² metric stays VL175 + ML, like for like, with only x moving to `E_R`** (ruling Q2).
- C_PL itself never uses that metric. It enters only the controls and the reported χ² rows.
- So those rows keep their meaning.

**Disclosure (gap 5).** The noise reference resamples data and MC, not the background stream, in both arms.
- J8's period replicas ran `--bootstrap-streams both`, as the purity chain's did.
- So the construction is like for like, and the refined background's own resampling variance is not in C_PL's noise
  reference.

### 3.5 C5, `re2c_playlist_term.py` (PT rows)

The construction is unchanged, with x = `E_R`.
- The `analysis.json` and `work_cov` digests are the ones C3 and C4 recorded (PT-02/04).
- Every run is mode-checked (PT-G).
- The npz and json carry `arm` = refined.

### 3.6 C6, `re2c_combine.py` (CB rows)

`Q_R` = S5_R total + C_PL_R, with every check of the original.
- The three input digests come from the previous steps (CB-02/03/04).
- Check 5's control values are read from the refined `playlist_term.json`, which is pinned and must carry
  `arm` = refined (CB-18). The purity literals cannot be declared for a product that does not exist yet. <!-- absence-ok: a rule about the refined product, which part C has not made: CB-18's literals are read at run time from it -->
- Both npz must carry `arm` = refined (CB-G).

### 3.7 C7, `re2c_build_q.py` (BQ rows)

- **Upstream digests:** the six come from `pins_q.json`, written by the run from the previous steps' records.
- **The central value:** `--eu` is `E_R`. It sets x, the cells, every relative σ and `hRel2D`.
- **The VL175 controls** (`budget.json` and `group_medians.json`, BQ-22/24) use the separately pinned
  `--eu-control` `E_U` as their denominator only.
- **The arm record:** every input must carry `arm` = refined.
- **s5.json's universe count** is the refined rollup's: 38 bands, 175 universes.
- **The same-run checks** (C8b) run after the χ² and Fig. 6/7 steps, in both arms: CR-02's cell-identity pass lines,
  and CR-03's Fig. 6/7 projections against this run's `budget_Q.json`, to 1e-12.
- **A disclosure (labels):** the copy keeps the original's check names. For example, `A1_E_U_nonzero_205` counts
  `E_R`'s cells in the refined arm, and the record's `arm` and `x` fields say which estimator it holds.

### 3.8 C10, Fig. 1 (`re2c_reduce.py`, `re2c_fig1.py`)

- **The central value** is drawn from `re2c_reduce.py`'s field `"E_R"`, named explicitly (P13).
- **Check 1** requires `cov2d_Q_205.npz`'s x to equal that `E_R`.
- **The inset** prints `Q_R`'s `\uqMedian` from `budget_Q.json`, as before.
- **Where it runs:** the laptop, in the recorded environment (python 3.12.2, matplotlib 3.11.2, numpy 2.5.4; uv
  venv), as the purity Fig. 1 was.
- **The procedure:** `bash re2c_fig1_local.sh refined <workdir> <venv python> $B/partc`. It reads the reduction,
  S5_R, C_PL_R, combination and `budget_Q` digests from `chain.json`, and copies the outputs and their
  `RUN-fig1.txt` into `$B/partc/fig1/`, which part C's HPSS bundle includes.
- **Before integration** Joseph reviews Fig. 1 visually (ruling Q3).

## 4. Runs

### 4.1 C0, the K1-roll: run before binding, as a control (ruling Q1)

The run (`bash re2c_dryrun.sh <deploy> try4`) was:
- on login12, 2026-10-24T14:07:31–14:10:40Z, 189 s of steps;
- from a clean deploy of this branch at `8c2b626d`, the code bound here, under `$B/review/partc-dryrun/`.

Its records are in [`run/partc_dryrun/`](run/partc_dryrun/).

**Condition (a), where it wrote.** Only under the dry-run directory. The first try also wrote 63 entries of the conda
environment's fontconfig cache and bytecode, outside it; tries 2–4 wrote none.

**Condition (b), what it touched.** `re2c_audit.py` over the `strace -f -y -e trace=%file` record
(`try4.strace.log.gz` `0edc09be…`, 307,468 successful file calls, `stat` included) found:
- **0** calls touching part B's or J0's products or their HPSS bundle;
- **no** write outside the dry-run directory, with every relative path resolved through its descriptor or the
  process's chdirs (`try4.audit.json`).

**Condition (c), the outcomes.** **36 of 36 comparisons PASS** (`try4/k1roll.json`):

| kind | what reproduced |
|---|---|
| analyze_prod item records (6) | every field but the copy's own digest and arm, each verdict PASS (c0, s3, s4ii, s1, s2, s4i) |
| bytes (9) | `production_cov.npz` `6689d2fc…`; `work_cov.npz` `70c4daf2…`; `analysis.json` `05edff61…`; `playlist_term.npz` `c1723cb5…`; `s5_plus_playlist.npz` `8ccb4d72…`; `cov2d_Q_205.npz` `771e49a5…`; and the period control, roles and selftest records |
| JSON (8) | `s5.json`'s numbers and checks; `cov_controls.json`; `playlist_term.json` and `combination.json` (checks, report); `budget_Q.json` (all but provenance and paths); the Fig. 6/7 projections; the agreement receipt; CR-02/CR-03's five entries of `checks.json` |
| printouts (10) | `chi2_Q_{std,lognormal,substat}.txt`, the three `ours_only_*.txt`, the published-covariance χ² and pulls, `tune.log`, the model and tension reports, line for line |
| values (3) | RE-1's 3D numbers exactly; the learner 0.983 % / 12.18 %; the values table's 242 controls |

**Fig. 1 reproduced byte for byte.** On the laptop, `bash re2c_fig1_local.sh purity` reproduced
`fig1_validation.pdf` `82665808…`, from the inputs that `stageF/rebuild/outputs/fig1/RUN-fig1.txt` names.
- Its own record, `run/partc_dryrun/fig1/RUN-fig1.txt`, gives the environment, commit, script digest, argv and every
  digest.

**Condition (d), failures, reported here and to the director.**
- **Try 1** (`deploy-1d095e1b`) stopped at C11 on a wrong import path in `re2c_numbers.py`, after 30 steps had
  passed (`try1.out`). The comparator's normalization also needed two fixes: dropping ROOT's rootmap warnings, and
  not comparing the deploy path that build_q's module checks record.
- **Try 2** (`3654be55`) passed 35 of 35.
- **The review then found the defects in §Review record.** Try 3 (`dbadf053`) ran their fixes. Try 4 (`8c2b626d`)
  added only the audit's chdir resolution.
- **None of these changed a purity product.** Every try that reached a product reproduced it.
- The review notes that patching and re-running may not be what the ruling's "reported, not patched" intended. That
  reading is the director's (§11).

**The P12 argv.** Running the five producers with `--ours E_U` and their defaults reproduces their committed
printouts and receipts. That establishes the argv the 2026-10-11 runs never committed.

### 4.2 The refined chain

**The order** is C1 to C13 (`bash re2c_run.sh refined <deploy> $B/partc`), on a login node, from a clean deploy of
the bound commit. Then C10 runs on the laptop, and C14 follows.

**Chain of custody.** Each product's sha256 becomes the next step's pin. All are recorded in `chain.json`:
- `work_cov`;
- `analysis.json`;
- `playlist_term.npz/.json`;
- `production_cov.npz`;
- `cov2d_Q_205.npz`;
- `s5_plus_playlist.npz`.

### 4.3 Stops

**A step's failure:** any nonzero exit stops the run (`re2c_run.sh`). It is reported to the director and not
resubmitted or patched without them. That covers:
- a failed pin or mode guard;
- a structural check of S5, C_PL or `Q_R` (symmetry, PSD to S5's tolerance, the 205 cells equal to `E_U`'s);
- a control (the May control, the block-sum control, the period control, CB-18, the VL175 budget and group
  medians, C_model's two controls);
- an upstream record without `arm` = refined.

**No threshold selects the result** (RE2-PLAN §5.3). The run reports every value, and adoption is Joseph's
decision.

## 5. C_model,2D beside `Q_R` (DECISION-20261024)

**What it is.** `C_model` = Σ_k s_k s_kᵀ: M2, κ = 1, fractional, from the committed factor S (`cmodel_2d.json`,
3 × 205).
- It does not depend on the central value, so RE-2 leaves it unchanged. Its matrix sha256 must be `11fe6818…`.
- `re2c_cmodel.py` writes C_abs_R = diag(`E_R`) C_model diag(`E_R`), the rescaling the C_model report names.
- It also writes the users' total, `Q_R + C_abs_R`, as a separate product. `Q_R` is read and never modified, and
  nothing written here is named Q.

**Reported:**
- the per-cell relative σ of `Q_R`, of C_model and of `Q_R + C_model` (median, p84, p90, max);
- the integral σ of each. This is new, so a secondary total can sit beside `\uqIntegral`.

**Positive controls, before the refined numbers:**
1. C_model's matrix sha256 equals `11fe6818…`.
2. With the purity Q (`771e49a5…`), C_abs's matrix sha256 equals `b11b10a0…`, and the per-cell Q + C_model summary
   equals `cmodel_2d.json`'s, whose median is 7.95 %.

**Label:** "generator-shape model dependence; not a calibrated bound". The output carries `cmodel_2d.json`'s caveat
and its post-hoc tail classification verbatim (`caveat`, `tail_caveat_post_hoc`).

**In the values table:** five "new product" rows. Nothing printed today corresponds to them, so they have no control.

**What C_model contradicts.** The integration step must reword the text it makes false:
- `paper_body.tex:415-418`, `sec_systematics.tex:379-382` and `primer_body.tex:294-296` say the covariance omits the
  unfolding-model dependence;
- PV-2D measured it, and C_model reports it beside Q.

## 6. Every printed number from `E_U` or Q

### 6.1 The values table (`re2c_values.py`, `re2c_values_spec.tsv`, 251 rows)

**The three gates.** Each row names a printed site, the characters printed there, the committed purity source, a
path, a transform and a format. Three gates run in order:
1. **anchor:** the characters are on the cited line. A macro must be defined once, with that value.
2. **positive control:** the formatted purity value equals the printed characters.
3. **regenerated value:** the same path, transform and format, on part C's refined output.

A row whose anchor or control fails gets no regenerated value.

**Paths that differ by arm.** Where the two arms' records differ in layout, a row names both, as "A || B". Ranges and
bounds reduce over every entry, by `min()`, `max()` or `maxabs()` with a required count. They never pin today's
extreme index.

**The dry run's table:** 251 rows; **242 controls PASS**, 8 new products, 1 declared failure, and 0 unexpected.

| group | rows | from |
|---|---|---|
| Q blocks tables (tab:uq, tab:combine, tab:band-medians, the worked example) | 46 | `budget_Q.json` |
| Q budget (`\uqMedian`, `\uqIntegral`, `\uqSFiveMedian`, `\fluxBand`, S1 0.684, 6.410 vs `E_C`, C_PL 2.0 %, …) | 36 | `budget_Q.json` |
| S5 prose (S1, C08, X02, X03, centring) | 34 | `s5.json` |
| published comparison | 32 | the agreement receipt; the published-covariance and combined χ² printouts (§6.2) |
| ranks and conditioning | 22 | `budget_Q.json`, `ours_only_*.txt` |
| C_PL prose | 17 | `playlist_term.json`, `combination.json` |
| tension | 15 | the tension report |
| published-side, unchanged (kept as controls) | 14 | `budget_Q.json`'s paper ratios |
| run periods (+6.94 ± 0.41 %, "about 7 %", pooled vs period) | 12 | `analysis.json` |
| 3D against 2D (0.001 %, 1.0000, ~3.5 %) | 8 | RE-1's numbers, then `re2c_numbers.py` |
| learner, against `E_C` (0.98 %, 12.2 %) | 6 | `lgbm_central_metrics.out`, then `re2c_numbers.py` |
| new: C_model (5), `E_R − E_U` in `Q_R`'s σ and the integral change (3) | 8 | `re2c_cmodel.py`, `re2c_numbers.py` |
| RO-FPS | 1 | the agreement receipt's `Integral("width")` |

**Macros.** Each is regenerated once, at its `values.tex` definition, which covers all 183 of its uses (RE2-DECLARATION-B §7.1).

**The declared failure is `\fpsAbove` (46).** It has no producer. 4.502/3.0730 − 1 = 46.50 %, which rounds to 47,
not the printed 46. Its definition is not established, so it is listed and not regenerated.

**The 21 sites the table cannot regenerate** are in `re2c_values_unmatched.tsv`, each with its reason. The
integration step handles them by hand:
- numbers printed as words or bounds: "eightfold", "about 4–5", 4×10⁻⁹, "two", "about three times", "one
  percent";
- numbers with no source field: `sec_method.tex:113-128`'s seed comparisons, C_PL's "1.8 effective degrees of
  freedom" and "order of 100 %";
- D2's movement against `E_U` (0.44 %, 1.13 %). Under adoption, that becomes `E_R`'s against `E_U`, which the new
  readout rows give;
- four published-side numbers.

### 6.2 The published comparison on `E_R` and `Q_R`

These are recomputed by the same producers on `E_R`, and `Q_R` where they use it.

| printed | now | producer (part C output) |
|---|---|---|
| the "~1 %": `\ratioTot` 1.011, "1.1 %", `\sigTwoD` 3.073e-38 | | `agreement_windows_receipt.py` (`receipts/RECEIPT-agreement-windows.json`) |
| `\medianBinRatio`, `\binsFive/Ten/Twenty` | 1.008; 82.9 / 95.6 / 99.0 | same |
| pulls `\pullMean`, `\pullRMS`, `\pullRMSr` | 0.074 / 0.564 / 0.56 | `compare_to_paper_fullcov.py`, paper-only (`receipts/chi2_paperonly.txt`) |
| `\chiPaper`, against the published covariance | 2.65 | same |
| `\chiCombined`, `\chiCombinedLog`, `\chiCombinedSubStat` (published + `Q_R`) | 0.964 / 0.987 / 6.01 | the same producer with `--omnifold-cov … hCov_Q` (`chi2/chi2_Q_*.txt`) |
| tension: 9.5 %, 0.81 over 73 modes, 15 %, χ²_norm and shape, diagonal-only | | `diagnose_tension.py` (`receipts/figs/tension_report.txt`) |
| Tune v1 ours-vs-tune 29.8 (data-vs-tune 33.0 stays) | | `compare_to_models.py` (`receipts/figs/model_comp_report.txt`) |

**Unchanged:**
- the published-side values (`\sigTwoDpaper`, `\uqPaper`, `\uqPaperIntegral`);
- the exact-split comparators (`\chiPaperExact` 3.66, `\chiPaperExactSeeded`, the 26.5);
- the purity coverage history (`\covTwoD*`, `\pull*Frac`);
- the negative-weight study (`\nw*`);
- the 5D and joint-test numbers.

The text comparing `\chiPaper` with the exact-split values is reworded at integration.

### 6.3 RO-FPS (RE2-DECLARATION-B §7.4)

- **The readout:** `E_R`'s `hXSec2D.Integral("width")` at 4 significant figures, against 3.073e-38.
- **It is printed either way:** "reproduces", or the two values and their difference.
- **Its source** is printed as "`VALIDATION_LEDGER.md:1614-1615`, no committed digest".
- **The positive control** is `E_U`'s 3.073e-38, which passes in the dry run (row `ro-fps`).

### 6.4 What part C does not do

- **No edit to `docs/analysis-note/`.** The values table, the figures and the reword list (RE2-PLAN §2.5;
  `paper_body` and the others for C_model; the `sec_fps.tex:47-52` control sentence) are the integration step's
  inputs.
- **`check_sec4_receipts.py`** is repointed at `Q_R`'s `budget_Q.json` at integration.
- **The printed wording is Joseph's.**

## 7. Figures

| figure | producer | numeric K1 (purity, in the dry run) |
|---|---|---|
| `MEFHC_fig6_7_uncertainty_pt/_pz` | `plot_uncertainty_fig6_7_style.py` | `fig67_projections.json` equal |
| `uq_spread_2d`, `uq_corr_2d` | `plot_bootstrap_figs.py` | from `block_stat.root`, whose npz twin is byte-identical |
| `MEFHC_5iter_pull_full` | `compare_to_paper_fullcov.py` | the pull mean and RMS in its printout |
| `MEFHC_5iter_fig13`, `_xsec_proj_pt/_pz`, `_xsec_paper_pt/_pz_slices` | `make_figures.sh:35-38`'s plots, `--infile E_R` | the run's input is the K1-checked central value |
| `model_comp_*`, `tension_*` | `compare_to_models.py`, `diagnose_tension.py` | their reports, line for line |
| `paper_fig1_validation` | `re2c_fig1.py` (laptop) | the PDF byte for byte, `82665808…` |
| `MEFHC_5iter_xsec_eff_heatmap` | `plot_2d_cross_section.py` | part B's PB-ER-eff shows `hEff2D` is bit-identical under both estimators |

**Byte checks.** PDFs drawn on the cluster carry timestamps, so they are not byte-compared (ruling Q3). Fig. 1's
environment is byte-stable.

**Joseph's visual review.** He reviews Fig. 1, and the director may extend this to any figure, before integration.

**The efficiency heatmap.** The committed `MEFHC_5iter_xsec_eff_heatmap.pdf` (`f33071e2…`, 2026-07-05) predates
`E_U` (the survey). Its integration redraws it from `E_R`, whose `hEff2D` equals `E_U`'s.

## 8. Compute

**Where:** a login node, no Slurm, 0 node-h, as every purity step was:
- s5_rollup: 8 s;
- the C_PL and combination steps: 0 node-h on login04;
- export_cov: 24 s and 386 MB.

**Measured:** the purity dry run took **189 s** in all (try 4). Its longest steps were the two `E_R`-figure
plots at 12 s each (`xsec_proj`, `paper_slices`), the period analysis at 11 s and the rollup at 10 s.

**Projected for the refined arm:** under 10 minutes. It reads 644 small files (44 MB) and the same purity
references.

**Cap:** login only. `re2c_run.sh` stops itself at 15 minutes (`timeout 900`), and a step that needs more memory
than a login node allows stops the run. Either way it comes back to the director. No QOS is requested. Fig. 1 runs on the laptop.

**Grant:** RE-2's room stays 36.8162 node-h. Part C charges none of it.

## 9. HPSS, part C's bundle (ruling Q4)

**What is copied:** `run/launch/re2_hpss.sh`, now parameterized, copies `$B/partc/` (every product and record of
the refined chain), with Fig. 1's outputs added to it, as one bundle `re2-2d-rebuild-partc-<date>`. The procedure is
RE2-DECLARATION-B §8's.

**The receipt's caveat is fixed.** `verify_tree` now writes its path sets per call (`6-got.<tag>.set`), so the
negative controls can no longer overwrite the real recovery's. That was the J0 and part B receipt's second caveat.

**The quota check.** The run re-reads `hpssquota` against the J0 and part B bundle's 0.056 GiB, closing that
receipt's first caveat if the quota has updated.

**Every step's output** is committed with part C's report.

## 10. Not in part C

- **A coverage or calibration test of `Q_R`** (RE2-PLAN §7).
- **Folding C_model into `Q_R`.**
- **The extended-fiducial central value, and a refined 5D covariance** (R8).
- **A new release candidate** (P14).
- **The note, paper and primer edits:** these are the integration step, after Joseph's adoption decision.

## 11. Rulings and decisions

**The director's preliminary rulings, 2026-10-24, to be confirmed by the binding:**

| # | ruling |
|---|---|
| Q1 | the purity-arm K1-roll may run before binding: it writes only to `$B/review/partc-dryrun`; it provably opens no refined product, with the opened-file list recorded; its outcomes go into the declaration; a failure is reported, not patched. **Done, §4.1.** |
| Q2 | the period and C_PL χ² keep VL175 + ML, like for like, with only x moving to `E_R` (§3.4) |
| Q3 | figures get a numeric K1, plus Joseph's visual review of Fig. 1 before integration (§7) |
| Q4 | part C's own HPSS step uses the same script, with per-call set files (§9) |
| gap 1 | S5-08: a separately pinned `E_U` as the May control's denominator (§3.2) |
| gap 2 | the provenance check verifies the staged paths through `preflight/inputs.stat`'s recorded digests, not by reading the deleted copies (§3.1) |
| gap 3 | the name map (§3.1) |
| gap 4 | `Muon_Energy_MINOS:0`: "no refined reference", with S4ii over the other six (§3.1) |
| gap 5 | the period and C_PL noise reference's data+MC-only bootstrap, as a disclosure (§3.4) |
| compute | login only; stop and return past about 15 min or on memory (§8) |

**For the binding:**
1. Bind part C at this branch's final commit, for the refined chain C1–C13 and C14 (HPSS).
2. **The values table's rule:** a number is regenerated only when its positive control passes, and
   `re2c_values_unmatched.tsv`'s 21 sites go to integration by hand. The alternative, writing definitions for
   them, would be choosing a specification after measuring (the `\fpsAbove` case).
3. **Joseph's review of Fig. 1** before integration, and of the C_model wording before anything prints.

## Review record

**The reviewer:** a fresh agent, read-only, given the declaration, the code, the records and the requirements, but
not the author's reasoning. It reviewed the working tree at `3654be55` in two directions: declaration to evidence,
and requirements to declaration. It ran the unit tests, spot-checked digests, and read nine refined outputs' records
on the cluster.

**What it verified:**
- all 17 digests;
- the dry-run counts;
- part B's committed sums against the cluster's;
- every name the copies build;
- the run script's argument counts against its parsers;
- the refined-arm data checks that already pass on part B's products: the period control at 7.5e-12 against `E_R`
  and 5.2e-12 against `D_cv`; the null universe at ≤ 5.6e-12 at all five seeds; the lateral closure at ≤ 2e-14; and
  both C_model controls exactly.

**It found 1 blocker, 3 major findings, 10 minor findings and 6 nits.** Their dispositions:

| finding | disposition |
|---|---|
| B1: four values rows read RE-1's numbers with no refined source, so the refined run would stop at C13 | fixed: the rows read `re2c_numbers.py`'s 3D numbers in the refined arm; RE-1's sources are purity-only; a new test builds a stand-in refined tree and requires every row to regenerate |
| M1: CR-02 and CR-03 (`check_rebuild.py`) implemented nowhere | fixed: `re2c_check_rebuild.py` (C8b), in both arms; the K1 compares it with the committed `checks.json` |
| M2: RE2-PLAN §5.3's per-block σ ratio to the purity block missing | fixed: `re2c_numbers.py` reports it for Q, S5, universe, stat, C08 and C_PL |
| M3: the refined Fig. 1 had no declared procedure | fixed: `re2c_fig1_local.sh` (§3.8), with the chain keys it needs; it writes its own `RUN-fig1.txt` |
| m1: refinement-record checks partial | fixed: C2 re-reads 400/31 and seed + 3 per input; part B's pinned health rows are cited (§3.1) |
| m2: the period outputs were not checked against part B's digests | fixed: the refined mode guard checks each run's committed digest |
| m3: the laterals were only counted, and S3 was not gated | fixed: each lateral's digest equals its CFS `SHA256SUMS` row (pinned), and the check gates c0 and s3 |
| m4: the audit missed relative paths, `stat`, and the HPSS bundle | fixed: `strace -y -e trace=%file`, chdir tracking, and the HPSS root added; try 4 resolves every path |
| m5: §8 named the wrong longest step | fixed from try 4's record |
| m6: the 15-minute stop applied only in the dry-run wrapper | fixed: `re2c_run.sh` runs itself under `timeout 900` |
| m7: try 1's failure was patched and re-run, while the ruling says "reported, not patched" | reported here and to the director (§4.1); the ruling's reading is the director's (§11) |
| m8: C_model's caveat was not carried in its output | fixed: `caveat` and `tail_caveat_post_hoc` are written verbatim |
| m9: AP-03, the refined arm still re-hashes the purity pins | disclosed (§3.1): it stops on a purged reference rather than passing |
| m10: the purity arm has more changes than the one named | listed (§2.1) |
| n1–n6 | n1 disclosed (§3.7), and the E_R-relative block-sum median added (§3.3); n2 docstring fixed; n3 pointer fixed; n4 committed, with `re2_hpss.sh`'s digest in §12; n5 group renamed `published_side`; n6 `app_statmethods.tex:910-911,957` classified as exact-split history in the unmatched list |

## 12. File digests

These are the code at `8c2b626d`, the commit try 4 ran. The declaration and the records were committed after it and
change no code. `test_re2c.py` checks the copy diffs.

| file | sha256 |
|---|---|
| `2d-unfolding/re2/partc/make_diffs.sh` | `9a3cb6839111b9988042a357b52dda6c64f273b0915682c02950515655f65a6b` |
| `2d-unfolding/re2/partc/pin_siblings.py` | `9679d4db21365b63210a27f95022be5031a6efa3ef83b6a6ca05c3bcf3f7f68b` |
| `2d-unfolding/re2/partc/re2c_analyze.py` | `4789b36d9c6d1d9979e272544f0a6d4bd46e675779b699983f59d1ba88c587f0` |
| `2d-unfolding/re2/partc/re2c_analyze_periods.py` | `708cfc2fec29b80019bebbf84cc3a354aff02031f1669904fae680ede21c8a59` |
| `2d-unfolding/re2/partc/re2c_audit.py` | `280ee00742e7b89912e6cb2b1e01558f94ffe675762081c3abe37bdbdddc5605` |
| `2d-unfolding/re2/partc/re2c_build_q.py` | `45fafddb6e44e88386d6b10b605b635315ef09e3d31ef1da5e8a71a913d1fe97` |
| `2d-unfolding/re2/partc/re2c_check_rebuild.py` | `f7feca72a17ce43ba740162e380320a6e62eae57926116e85e1476eb4b1c9246` |
| `2d-unfolding/re2/partc/re2c_cmodel.py` | `cd8fbf09635c2854d2e68f6f1274add500d722aa21552e9fd665403f836b3072` |
| `2d-unfolding/re2/partc/re2c_combine.py` | `2f5d2ea3161d7f5c3a389fb697e5aa5a745b6565334e2bba1a10d0f5ceb15301` |
| `2d-unfolding/re2/partc/re2c_dryrun.sh` | `3c6084c5c64d7f9fd79b780da059dcfa2602506753e8157e21e37ec078a917e0` |
| `2d-unfolding/re2/partc/re2c_export_cov.py` | `524ef62e79947dbc16c5a59e860e166a05a03f27cc60ad80ac07709e1d947a3f` |
| `2d-unfolding/re2/partc/re2c_fig1.py` | `9d7eb17700d33fd77696c3d7af49e22dd943d4bb8495eda974d7bba119873b99` |
| `2d-unfolding/re2/partc/re2c_fig1_local.sh` | `02c3090f22790ca50f9d762b2d766bd07918dd2e7cdec12cc33099b9adc20e9a` |
| `2d-unfolding/re2/partc/re2c_k1roll.py` | `166d5c09da3c95e8e949dacb5a3f78832c5366ed2ad18e99048e25eb6c2d186c` |
| `2d-unfolding/re2/partc/re2c_numbers.py` | `8d5f06a86ee25e087ffa46745cf2c24d568c9cb43a937c2f23cc14b058123787` |
| `2d-unfolding/re2/partc/re2c_periods.py` | `19f2c3934f93a34cc7d20202f83152421bdb0db044380bd8601216bcdb95dd9f` |
| `2d-unfolding/re2/partc/re2c_playlist_term.py` | `24ac48d86a76cc00c9dbf175f460baa1239947941fffdf57cad8c98b804383e8` |
| `2d-unfolding/re2/partc/re2c_reduce.py` | `e03df3f88a7e609d8787bd0ee8e22fbe319d2afa7dcaf97f67b006073c05e381` |
| `2d-unfolding/re2/partc/re2c_rollup.py` | `53840b0bc687511995466b74bef185412f0b4db3244f170e6204629b516b74d8` |
| `2d-unfolding/re2/partc/re2c_run.sh` | `ff66c7a9faa3529f1a84582fc3df2cfaea43a20016c01523077bbb7880fcf589` |
| `2d-unfolding/re2/partc/re2c_values.py` | `b5d645021e3d876c852794a5d1a14d12aed1375f75c08ad0be0c80350a8c0e3e` |
| `2d-unfolding/re2/partc/re2c_values_spec.tsv` | `5ff566fd13c6fe689c539da58062a09720562bf564cf5ac9770ddd1cd922d1fe` |
| `2d-unfolding/re2/partc/re2c_values_unmatched.tsv` | `4c2e7eb956d232fb67fdd6cbfc692a9fe11ccd651271b28dc44157d4bd533d00` |
| `2d-unfolding/re2/partc/test_re2c.py` | `ae3334610e15f0673cd69aef2ce7451aeba198c5fd61f859c8d746d1a32dc6e8` |
| `docs/orchestration/state/2d-closeout/stageF/methods/re2/run/launch/re2_hpss.sh` | `3db768d559958ef02984fdd1096fee3270705f70be912f91cde2c4be9404b0ce` |
