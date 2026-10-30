# DECLARATION 5B: the per-period 5D unfolds, with a pooled control fixed before they run (2026-10-30)

**By** the measurement session `coverage-5b` (ListAgents), for the director to bind.

**Under:**
- [`DECISION-20261028-joseph-d2-approved-and-cheap-tier.md`](../../../DECISION-20261028-joseph-d2-approved-and-cheap-tier.md)
  item 2: the cheap tier runs "under the standing approval for jobs under 12 h, declared and bound as usual";
- the director's ruling of 2026-10-29 that 5B goes to a fresh session, and its condition that any fallback CV event
  loop is CPU only, declared and bound separately, and priced from MP-1's measured per-variant cost
  ([`HANDOFF-20261029-coverage-session.md`](HANDOFF-20261029-coverage-session.md) §3 item 2);
- the director's rulings of 2026-10-30, given in messages, on five design choices (§7 items 1–5) and on C2's
  bit-reproducibility (§3, K2).

**After:**
- [`LIMITATION-PLAN-ADDENDUM-20261028.md`](LIMITATION-PLAN-ADDENDUM-20261028.md) §5.2, design 5B, and §5.3–5.4;
- [`FD-CT-5B-INPUTS.md`](FD-CT-5B-INPUTS.md): the inputs are MP-1's zero per-playlist loops, and the pooled control
  decides whether they reproduce S1.

**Declares:**
- a new input driver, `nd-unfolding/fd_ct_period_inputs.py` (`stage-flux`, `merge`, `check`, `unfold`);
- a new reader, `nd-unfolding/fd_ct_periods.py` (`precheck`, `control`, `gate`, `periods`);
- the step and lane tables of two jobs, written by `make_5b_tables.py`;
- two submit stages, `5b-inputs` and `5b-periods`, in `nd-unfolding/submit_fd_ct.sh`;
- the period flux files, committed as copies;
- their tests, the argv, the controls and tolerance, the readout and the stop rule.

**MEASURES:** nothing. The code has run only on synthetic fixtures. The design read real data once: the per-cell
scatter of MP-1's 25 committed jittered data unfolds about their own variant means, which fixes K3's tolerance (§3).
It read no f, made no comparison with f and read nothing from any period. The other cluster commands were `ls` and
`sha256sum` of the inputs (§1), a copy of the four flux files, and the unit tests in a scratch clone (§11).
<!-- absence-ok: a scoping statement about this session's own reads, listed in full in sections 1, 3 and 11 -->

**CANNOT AUTHORIZE:**
- running either job, which needs the director's binding. Job A also needs the precheck's PASS (§2.2), and the
  period job the control's (§2.5);
- a consistency verdict. No threshold is declared, and the words "consistent" and "inconsistent" are not used of any
  5B number (§5; the director's ruling 5);
- a covariance component, a change to the reported matrix or to κ, a claim or printed wording. A C_PL,5D is printed
  beside the matrix, never in it (addendum §5.4);
- any fallback event loop (§7 item 8).

**CITABLE FOR:** what 5B will compute, from which inputs, at what cost, what its control decides and what makes it stop.

**NOT CITABLE FOR:** any result. Once run:
- not the cause of a period difference, or which period is right;
- not a validated size: a block built from the observed differences contains them by construction
  (`2d-closeout/playlist-term/REPORT.md:20`);
- not a coverage or calibration statement.

**Paths:** as in LIMITATION-PLAN.md. A bare `.md` or `.tsv` name is in this directory. Paths beginning `docs/`,
`nd-unfolding/`, `2d-unfolding/` or `publication/` are from the repository root, as is `KNOWN_ISSUES.md`. Every other path
is relative to `docs/orchestration/state/`. `$P` = `/pscratch/sd/j/josephrb`.

## 0. Summary

### The question

Do the three run-period groups of the 2D result, 1A–1F, 1G/1L/1M and 1N–1P, give the same 5D cross section on the
16 reporting cells R00–R15, within the noise? If not, how large is the difference by 2D's construction? Addendum §5.3
states the question. This declaration answers it only with numbers beside their references (§5).

### The chain

The 2D period unfold's design (`2d-closeout/period-unfold-20261014/`) is applied to the 5D inputs, period by period:

| step | tool | what it makes |
|---|---|---|
| flux | `fd_ct_period_inputs.py stage-flux` (login) | the 2D period unfold's four data-POT-weighted flux files, committed, copied into `$B/flux` |
| merge | `fd_ct_period_inputs.py merge` → `2d-unfolding/uq/hadd_universes_full.py` | the period's MP-1 zero loops, in production order, as MP-1 merged them |
| dump | `nn_dump_inputs.py --axes eavail,q3,W --mcfile <period flux>` | the period's npz |
| lateral form | `s5p_input_dumps.py lateral --cv-npz <that npz> --mcfile <period flux>` | the same npz again, and its background dump in MP-1's float64 form |
| check | `fd_ct_period_inputs.py check` → `s5p_mc_truth_pred.py` | a receipt that the pieces hang together, and the period's MC truth |
| unfold | `fd_ct_period_inputs.py unfold` → `s5p_numerics.py` | (e): config R, 5 iterations, real data, seed 42 |

**ALL is all twelve playlists through the same chain,** so it is MP-1's own zero chain rebuilt by 5B's tools.

### The control (fixed here, before anything runs)

**Before any job,** the reader's `precheck` decides K3 below on MP-1's own zero unfold: if K2 holds, that unfold is
X_ALL. So a K3 failure is known at 0 node-h, before job A is submitted.

The control job builds the inputs of all four periods and unfolds ALL only. The reader's `control` then decides:
- **K1:** the ALL npz and background arrays are bitwise MP-1's `lat_zero.npz` and `lat_zero_bkg.npz`, key by key;
- **K2:** the ALL unfold's `xsec_flat` is bitwise MP-1's `mp1s1_zero_b-_j-.npz` (`f1d5178a…`);
- **K3:** |X_ALL,R / f_R − 1| ≤ τ_R on all 16 cells. τ_R = 5√2 σ_R, where σ_R is the pooled per-cell SD of MP-1's 25
  jittered data unfolds (§3). τ runs from 0.43% to 1.99%. K3 is written as one flag per cell. A written
  |X_ALL/f − 1|, or its ratio to τ, would give f back with the committed `mp1s1_zero` (§3, review H2).

**Each job is submitted only after its gate.** The submit stages call `fd_ct_periods.py gate`, which refuses job A
unless this deploy's precheck says PASS. It refuses job B unless this deploy's control says PASS on the ALL unfold now
on disk, with the three period receipts this deploy's.

### The period unfolds and the readout

- **34 unfolds:** ALL at seed 42, then for each period the seed-42 unfold and ten bootstrap replicas.
  - Each period has its own seed block: PA 1001–1010, PB 2001–2010, PC 3001–3010, as 2D's.
  - Shared seeds would give the periods' rows common Poisson draws and correlate their noise (§4, review M1).
  - This is the addendum's 37 less the three seed-43 unfolds, which are zero by construction for (e) (§7 item 1).
- **The readout** (`periods`, login node), on R00–R15:
  - the double ratios r_X = X_X / T_X of the periods against each other, with the raw and MC-truth ratios beside them;
  - nothing relative to ALL: once K2 holds, X_ALL is the committed `mp1s1_zero`, so a ratio to it would give an
    absolute period integral back (§4, review H2);
  - per comparison, its χ² in the metric of M = (C_total + C_resp)/(f fᵀ), beside the bootstrap-noise expectation
    and the ten paired noise draws;
  - a p_∥ contrast across the 4.5 GeV/c cell boundary, with its noise σ;
  - C_PL,5D by 2D's DESIGN §2, beside M and beside its own noise floor;
  - 5B's period offsets g_X against 5A's projection of the 2D offsets: the test of 5A's assumption.
- **Every output is relative,** through F0's leak guard (§3).

### Cost

| job | geometry | measured units | projected | limit, so at most |
|---|---|---|---|---|
| A, `5b-inputs` | one exclusive CPU node, 4 lanes of 32 CPUs and 56 GB, MP-1's geometry | dump 340–359 s, unfold 688–711 s (`measurement-paper/phase1/mp1/S1-REPORT.md:143-148`) | ALL's lane about 33 min **(estimate: merge and check unpriced)**, so about 0.55 node-h | 1:00:00, so 1.0 node-h |
| B, `5b-periods` | one exclusive CPU node, 8 lanes of 32 CPUs and 56 GB | the same unfold unit | about 20 min if the unfold time scales with the period's bytes, so about 0.33 node-h **(estimate)** | 1:30:00, so 1.5 node-h |

**About 0.9 node-h expected, at most 2.5.** That is inside the addendum's 1.0–1.9 and its cap of about 3.0, and each
job is under 12 h. The readers run on a login node at 0 node-h.

**Stop rule:** any refusal, any non-zero exit, a lane that ends without its products, or a job past its limit is
reported unrepaired. **There is no resume:** every step refuses to overwrite, and the submit stages refuse an existing
run directory. A rerun needs the director and recommitted tables under a new `$B`. A control FAIL is a STOP: the period
job is not submitted, and the next step is the director's (§7 item 8).

## 1. Inputs

Every pin is in the code, not the argv.

| input | where | pin |
|---|---|---|
| MP-1's 12 zero loops | `$P/measurement-paper/phase1/mp1/s1/evloop/zero/runEventLoopOmniFold_5D_<PL>_zero.root` (4.84 GB in all) | `fd_ct_period_inputs.ZERO_LOOPS`, measured by `sha256sum` on login37, 2026-10-30. G1 ties each to W2b's rrzero pass (`measurement-paper/phase1/mp1/S1-REPORT.md:122-125`) |
| the period flux | `fd/receipts-ct/5b/flux/runEventLoopMC_{ALL,PA,PB,PC}.root`, **force-added** (`*.root` is ignored, as for the repository's four other evidence `.root` files) at 5,657, 5,537, 5,484 and 5,484 bytes | `FLUX`: `e3dc9e63…`, `927f5af2…`, `c64637d5…`, `95c45a5f…`, equal to the 2D record's `2d-closeout/period-unfold-20261014/outputs/SHA256SUMS.inputs` and to the files at `$P/2d-closeout-period-unfold-20261014/flux/` (2026-10-30) |
| MP-1's zero chain | `$P/measurement-paper/phase1/mp1/s1/lateral/lat_zero{,_bkg}.npz`; `mp1s1_zero_b-_j-.npz` committed at `measurement-paper/phase1/mp1/jitter-receipts/` | `MP1_ZERO` = `build_cresp.PRODUCTS["zero"]`: `f1d5178a…`, `6ca02c3d…`, `f09727d0…` |
| MP-1's 25 jittered data unfolds | `measurement-paper/phase1/mp1/jitter-receipts/mp1nj_{zero,em_m1,em_p1,other_m1,other_p1}_b-_j{1..5}.npz` (committed) | `fd_ct_periods.JITTER`. Each digest is in that directory's `verify_nj.json` and `jitter.json` |
| S1 and C_resp | as the readers' declaration | `db000707…`, `4d8b5797…` |
| 5A's readout | `fd/readout/fd_ct_period.json` (committed) | `d7d518ac…` (`READOUT_5A_SHA256`) |

**The flux files:**
- 2D's `build_flux.py` made them with the pinned production combiner, and 2D's `verify_inputs.py` required ALL to equal
  the production flux `d40aea69…` bin for bin, with errors and POTs as well. That passed
  (`2d-closeout/period-unfold-20261014/outputs/inputs_verify.json`).
- They depend only on `2d-unfolding/baseline_flux/`, not on the event loops.
- `stage-flux` refuses any source or copy not at its pin.
- `check` refuses unless each merge's `dataPOTUsed` equals its flux file's `DataPOTUsedForFluxWeighting`, and the dump's
  `data_pot`, to 10⁻¹². `merge` makes the first of these checks before any dump reads the merge (review L2).

**The merges:**
- They run in production order, 1A…1P (PA = 1A–1F, PB = 1G/1L/1M, PC = 1N–1P, ALL = all twelve). `PERIODS` is
  tested against 2D's `periods.py`, and ALL's order against MP-1's `mp1_s1_pipeline.sh` `PLS`.
- `merge` refuses any loop not at its pin, before merging.

## 2. Exact commands

`B=$P/fd-ct-5b-20261030` (which must not exist beforehand); `D=$B/deploy/<pin8>`;
`PY=env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I -B`.

### 2.1 Deploy and tests (login node)

As the readers' declaration §2.1, with:
- the digest list: `fd_ct_period_inputs.py`, `fd_ct_periods.py`, `test_fd_ct_periods.py`, `submit_fd_ct.sh`,
  `fd_ct_readers.py`, `fd_f0_regrade.py`, `s1_assemble.py`, `s5p_numerics.py`, `s5p_input_dumps.py`,
  `nn_dump_inputs.py`, `s5p_mc_truth_pred.py`, `hadd_universes_full.py`, `fd_f1_lane.py`, `s5c_array.sh`,
  `sbatch_timing_packed.sh`, the four tables, the four flux copies and this declaration;
- the test modules `test_fd_ct_periods test_fd_ct_readers test_fd_ct_closure test_fd_f0_regrade test_s1_assemble`;
- the committed tables regenerated by `make_5b_tables.py` into `$B/tables`, then compared with `cmp`;
- **the tests run with root_6_28 activated by prefix,** not by the bare interpreter that the readers' recipe used:
  `eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"; conda activate $HOME/.conda/envs/root_6_28`,
  with no `set -u`, then `python3 -B -m unittest …`. `test_fd_ct_periods.RootReaders` imports ROOT, and the bare
  interpreter segfaults on that (§11). The steps are unaffected: `s5c_array.sh` sources `setup_salloc_env.sh`.
  `stage-flux` and the readers import no ROOT, so they keep `$PY`.

**It must show:** HEAD equal to the pin; 0 porcelain lines before and after; the §8 digests; `tests rc=0` with
**"Ran 243 tests … OK" and no skip**, so that the two ROOT tests and 3b's real-unfold test run; the four tables
identical.

### 2.2 The precheck (login node, after §2.1, before job A)

```bash
mkdir $B/control && cd $B && TMPDIR=$B/tmp timeout 600 $PY $D/nd-unfolding/fd_ct_periods.py precheck \
  --definition $D/nd-unfolding/pv-ladder/readouts/h2_definition.json \
  --s1-npz $P/s1-20261024/s1_assembly.npz --cresp $P/cresp-20261026/out/cresp.npz --b $B \
  --mp1-zero $D/docs/orchestration/state/measurement-paper/phase1/mp1/jitter-receipts/mp1s1_zero_b-_j-.npz \
  --out-json $B/control/fd_ct_5b_precheck.json > $B/logs/precheck.out 2> $B/logs/precheck.err; echo "rc=$?" >> $B/logs/precheck.out
```

It decides K3 on MP-1's zero unfold, with the tolerance below, and writes a flag per cell. A FAIL is a STOP at
0 node-h, reported to the director; job A's gate then refuses. Exit codes are as in §2.4.

### 2.3 Job A, the inputs and the ALL unfold (login node submits; one compute node)

```bash
bash $D/nd-unfolding/submit_fd_ct.sh 5b-inputs $D <pin> $B > $B/logs/submit-inputs.out 2>&1; echo "rc=$?" >> $B/logs/submit-inputs.out
```

- `submit_fd_ct.sh` refuses unless `$D` is at the pin, and none of `$B/{flux,merged,dumps,truth,inputs,unf,lanes-inputs}`
  exists. It also refuses unless all 17 steps write under `$B/`, and unless the gate passes on the precheck.
- After those refusals, it creates the steps' output folders `$B/{dumps,truth,inputs}` (review H1). It then stages the flux (`stage-flux --out-dir $B/flux`, logged to `$B/logs/stage-flux.out`) and submits one job:
  account m3246, QOS regular, constraint cpu, one exclusive node, `--no-requeue`, `--time=01:00:00`, no GPU. The
  four lanes have 32 CPUs and 56 GB each, as MP-1's dumps and unfolds did, so the ALL unfold runs as `mp1s1_zero` did
  (review M3). Four lanes fit the node's 487,802M allocation (review M4).
- **Lanes,** each running under `s5c_array.sh`, which refuses a deploy not at the pin and wraps every interpreter in
  `mnv_guarded_run.py`:
  - lane 0: ALL, merge → nn_dump → lateral → check → the ALL unfold;
  - lanes 1–3: PA, PB and PC, merge → nn_dump → lateral → check.

**After the job:** `sacct -j <job> -X -o JobID,State,ExitCode,Elapsed,NNodes,AllocTRES`, and every lane's `[f1-lane]`
lines, are recorded. The job must be COMPLETED 0:0, and all four lanes must end `done`. Anything else is a STOP.

### 2.4 The pooled control (login node, after §2.3)

```bash
cd $B && TMPDIR=$B/tmp timeout 600 $PY $D/nd-unfolding/fd_ct_periods.py control \
  --definition $D/nd-unfolding/pv-ladder/readouts/h2_definition.json \
  --s1-npz $P/s1-20261024/s1_assembly.npz --cresp $P/cresp-20261026/out/cresp.npz --b $B \
  --mp1-zero $D/docs/orchestration/state/measurement-paper/phase1/mp1/jitter-receipts/mp1s1_zero_b-_j-.npz \
  --out-json $B/control/fd_ct_5b_control.json > $B/logs/control.out 2> $B/logs/control.err; echo "rc=$?" >> $B/logs/control.out
```

- It reads the ALL receipt and the ALL unfold, and nothing of PA, PB or PC (`test_reads_no_period_product`). It
  refuses while any period unfold directory exists.
- Exit codes: 0 PASS (written); 1 FAIL (written, with the verdict) or a refusal (nothing written); 2 argparse; 3 leak
  guard; 124 timeout.
- **The control record is reported to the director before job B is submitted.**

### 2.5 Job B, the period unfolds (login node submits; one compute node; only after a PASS)

```bash
bash $D/nd-unfolding/submit_fd_ct.sh 5b-periods $D <pin> $B > $B/logs/submit-periods.out 2>&1; echo "rc=$?" >> $B/logs/submit-periods.out
```

- It refuses unless none of `$B/unf/{PA,PB,PC}` or `$B/lanes-periods` exists, all 33 steps write under `$B/`, and the
  gate passes. The gate requires this deploy's control record to say PASS on the ALL unfold now on disk, with the
  three period receipts this deploy's.
- One job: QOS regular, constraint cpu, one exclusive node, `--no-requeue`, `--time=01:30:00`, no GPU. It runs eight
  lanes of 32 CPUs and 56 GB, the 33 unfolds packed longest first.

The `sacct` and lane checks are as in §2.3.

### 2.6 The readout (login node, after §2.5)

```bash
cd $B && TMPDIR=$B/tmp timeout 600 $PY $D/nd-unfolding/fd_ct_periods.py periods \
  --definition $D/nd-unfolding/pv-ladder/readouts/h2_definition.json \
  --s1-npz $P/s1-20261024/s1_assembly.npz --cresp $P/cresp-20261026/out/cresp.npz --b $B \
  --control-json $B/control/fd_ct_5b_control.json \
  --readout-5a $D/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/readout/fd_ct_period.json \
  --out-json $B/fd_ct_5b_periods.json > $B/logs/periods.out 2> $B/logs/periods.err; echo "rc=$?" >> $B/logs/periods.out
```

Exit codes are as in §2.4; there is no FAIL verdict here.

### 2.7 Preservation (login node, after §2.6)

These go to HPSS by the committed `stage0_preserve.sh`, as 3b's inputs did, into
`/home/j/josephrb/mnv-5d-ct-5b-<date>`, with their inventory:
- the 34 unfolds, the four MC truths, the four check receipts, the four merge receipts and the two control records, about 5 MB **(estimate:
  34 × 96 kB, plus the truths)**;
- the ALL npz and background dump (1.55 GB), so that K1 can be re-measured.

**The period merges and dumps,** about 14 GB **(estimate: the loops' 4.84 GB merged twice, plus the dumps)**, stay on
pscratch only. They are rebuilt from the pinned loops by job A.

**Committed in the report's PR:** the three readouts as `fd/readout/fd_ct_5b_{precheck,control,periods}.json`;
the logs, `sacct` lines, step scripts, receipts and the products' sha256 list under `fd/receipts-ct/5b/run/`; ledger
rows.

## 3. Controls

### The pooled control (`fd_ct_periods.py control`)

**K0, refusals** (exit 1, nothing written):
- no period unfold directory may exist yet (`test_refuses_while_a_period_unfold_exists`);
- the ALL check receipt must be this deploy's `fd_ct_period_inputs.py`'s, with its files at their recorded digests;
- its comparison with MP-1 must name MP-1's pinned dumps, and cover every declared key of both files;
- MP-1's `mp1s1_zero_b-_j-.npz` must be at its pin;
- the ALL unfold must have been made by (e): config R, 5 iterations, seed 42 with the refinement at 45, real data,
  no bootstrap, no jitter, float32 coordinates, on the receipt's two dumps, by this deploy's `s5p_numerics.py`;
- every ALL cell integral must be positive.

Tests: `test_refuses_a_comparison_missing_a_key`, `test_refuses_a_receipt_of_other_code_or_a_moved_dump`,
`test_refuses_an_all_unfold_not_made_as_declared` (four defects), `test_refuses_another_mp1_zero`,
`test_refuses_a_non_positive_all_integral`.

**K1, the inputs bitwise.** The ALL check compares `lat_ALL.npz` with `lat_zero.npz` over all 19 keys, and
`lat_ALL_bkg.npz` with `lat_zero_bkg.npz` over `bkg_reco`, `bkg_w` and `bkg_nd`. Each comparison is of shape, dtype and
values; the key sets are compared too. The background's `meta` holds paths and run times and is not compared.
- **Why expected:** the dump code and the collectors it calls are MP-1's (§4), and the merge is MP-1's tool on MP-1's
  inputs in MP-1's order.
- **Decides:** `test_k1_fails_on_one_recorded_key` (three keys) and `test_all_records_each_key_against_mp1_and_does_not_decide`.

**K2, the unfold bitwise.** The ALL unfold's `xsec_flat` must be array-equal to `mp1s1_zero`'s.
- **Expected bitwise, because (e) is bit-reproducible run to run on the records.** (e) runs `deterministic=True`,
  `force_row_wise=True`, `num_threads=32` and `bin_construct_sample_cnt = ALL_ROWS`, with no bagging and no feature
  subsampling (`nd-unfolding/s5c_unfold.py:54-60`). On that configuration:
  - **S1's G4:** a fresh run on 2026-10-24, by another entrypoint (`s5p_universe.py`), reproduced s5p's
    `data_b-_j-.npz` of 2026-09-26 bitwise on the same inputs (`S1-DECLARATION.md:183`; `S1-REPORT.md:105`;
    `s1/receipts-S1/logs/G4.log`);
  - **S1's seed block:** 80 products are bitwise equal to set A's from job 58904837, a separate job a month earlier
    (`S1-REPORT.md:317-318`, `:456`);
  - **s5c P1:** with `deterministic` on, two estimator seeds give bitwise-equal 5D fits, while LightGBM's defaults
    repeat at 2.1 × 10⁻¹³ (`S1-REPORT.md:438-442`, from `s5c/p1/p1_summary.json:70,79`).
- **OI-160's run-to-run floor does not apply to (e).** That floor, 1.43 × 10⁻¹² (`oi160-tolerance-20261029/REPORT.md:39`),
  was measured on `bootstrap_nd.py`, which builds its estimators at LightGBM's defaults (`omnifold_nn_core.py:145`) and
  sets none of `deterministic`, `force_row_wise`, `num_threads` or `bin_construct_sample_cnt`. It is the regime of s5c
  P1's 2.1 × 10⁻¹³, not of (e).
- **The code:** every file the unfold executes is byte-identical to MP-1's unfold deploy `4e4b4f56`, except
  `unfold_2d_omnifold_unbinned.py` and `s5p_truths.py`. Those differ only in top-level code the data construction never
  calls: `main`, plus added functions, and `fine_weight` (§4; `fd/receipts-ct/5b/probe/p1_chain_code.out`).
- **What a mismatch means, declared now:** on these records the run-to-run floor of (e) is zero, so **any** K2 mismatch
  is a STOP, reported unrepaired. The record carries the fine-cell maximum relative difference for the report only;
  it is not a tolerance.
- **Decides:** `test_k2_fails_on_one_fine_cell`, a one-ulp change in one fine cell.

**K3, within tolerance of f.** |X_ALL,R / f_R − 1| ≤ τ_R on every cell, τ_R = 5√2 σ_R. It is decided twice, on the
same tolerance: first by `precheck`, on MP-1's zero unfold, before job A (review M2); then by `control`, on X_ALL.
If K2 holds, the two are the same integrals.
- **σ_R:** the pooled relative SD, per cell, of MP-1's 25 jittered data unfolds, each about its own variant's mean.
  There are five variants (zero, em ±1σ, other ±1σ), five edge-safe jitter seeds each, and 20 dof
  (`jitter_sigma`).
- **The one read of real data behind this design.** It reads only that scatter: no f, no comparison with f, and
  nothing from any period. The director accepted it on 2026-10-30.
- **Fixed in code:** `SIGMA_JITTER`, required equal to `jitter_sigma`'s recomputation to 10⁻¹² before K3 is
  evaluated. That is, in %:

  | R00 | R01 | R02 | R03 | R04 | R05 | R06 | R07 | R08 | R09 | R10 | R11 | R12 | R13 | R14 | R15 |
  |---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
  | σ 0.129 | 0.123 | 0.253 | 0.189 | 0.061 | 0.229 | 0.164 | 0.282 | 0.121 | 0.114 | 0.153 | 0.165 | 0.104 | 0.132 | 0.083 | 0.075 |
  | τ 0.911 | 0.871 | 1.792 | 1.339 | 0.434 | 1.616 | 1.158 | 1.993 | 0.857 | 0.809 | 1.082 | 1.168 | 0.738 | 0.934 | 0.584 | 0.531 |

- **Why 5√2:** f and X_ALL come from two chains that differ in their dump paths, as recorded:
  - the 2,801 −9999 sentinel rows that the production npz keeps (`KNOWN_ISSUES.md:69`);
  - the background coordinates' dtype (`FD-CT-5B-INPUTS.md` §1–2).

  If each chain's result is one draw from the estimator's rounding-scale scatter, as MP-1 found for its unjittered
  product (`measurement-paper/phase1/mp1/S1-REPORT.md:326-331`), their difference has SD √2 σ_R. Five SD over 16
  cells, with σ estimated on 20 dof, gives a false STOP of order 10⁻³ under that model **(arithmetic, t₂₀)**. A larger
  difference means the chains differ by more than rounding.
- **Written:** one flag per cell, `within_by_cell`, with the failing cells and τ. **Not written:** |X_ALL/f − 1| or
  its ratio q to τ, in the record or on stdout.
  - Once K2 holds, X_ALL is the committed `mp1s1_zero`, so q τ would give f back cell by cell. That is a leak by
    combination, which F0's guard, judging one number at a time, cannot see (review H2, `review/probe_leak.py`).
  - `test_the_record_does_not_give_f_back_with_the_public_x_all` requires that no written number be either.
  - A flag still bounds f to X_ALL (1 ± τ_R). That is the content of any such control, and it is far from the guard's
    10⁻¹³.
- **Decides in both directions:** `test_k3_decides_in_both_directions` plants R05 at 0.99 τ (PASS) and 1.01 τ (FAIL).
  `test_decides_k3_on_mp1s_zero_in_both_directions_and_writes_flags_only` does the same for the precheck, on R11.
  `test_refuses_a_tolerance_not_the_declared_one` changes one σ by 10⁻⁹. `test_the_declared_sigma_is_the_committed_receipts`
  recomputes σ by a second route.

**The verdict** is PASS only if K1, K2 and K3 all hold (`test_passes_when_bitwise_and_within_tolerance`). A FAIL is
written with all three parts and exits 1.

**The gate** (`fd_ct_periods.py gate`, called by both submit stages; review M5):
- job A: the precheck record exists, has the precheck schema, says PASS and was made by this deploy's
  `fd_ct_periods.py`;
- job B: the same for the control record, whose ALL-unfold digest must equal the file now on disk, and the three
  period receipts must be this deploy's with their files at their digests.

Tests: `Gate.test_inputs_gate` (three defects), `Gate.test_periods_gate` (a missing receipt, a changed ALL unfold).

### The inputs (`fd_ct_period_inputs.py`; each refusal writes nothing)

| step | refuses (exit) | tests |
|---|---|---|
| `stage-flux` | an existing directory (3); a source or copy not at its pin, before anything is created (4) | `StageFlux` (3) |
| `merge` | an existing output, receipt or partial (3); any loop or the flux file not at its pin, before merging (4); a failed merge, with the partial removed (6); a merge whose `dataPOTUsed` is not the flux file's `DataPOTUsedForFluxWeighting` to 10⁻¹², before any dump reads it, with the merge removed (5) | `Merge` (5): the production order and MP-1's tool, and the POT check in both directions |
| `check` | creates its output folders; refuses an existing receipt or truth (3); a flux file not at the period's pin (4); for ALL, MP-1's dumps not at their pins (4); the lateral npz differing from the nn_dump npz in any key, shape or dtype; a background dump naming another npz or merge; a merge its receipt does not name; a data POT the flux was not weighted with (5); `--mp1-*` given for a period or missing for ALL (2) | `Check` (11): each of the 19 keys by a one-entry change, a dtype change alone, and the real ALL flux's last-digit spread |
| `unfold` | an existing product, since `s5p_numerics` would skip it and exit 0 (3); another period's receipt, or a dump changed since its check (4); an exit 0 without the product (6) | `Unfold` (4), including the declared argv |

**ALL against MP-1 is recorded, not decided,** by `check`; the control decides on it.

**The flux's p_T constancy is to rounding:** the real ALL flux's bins differ in the last digit (`…851218`, `…851219`,
`inputs_verify.json`). So `check` records the spread and calls it constant at ≤ 10⁻¹⁴, and the reader refuses a
period whose flux is not (`test_the_real_alls_last_digit_flux_spread_is_constant_and_a_larger_one_is_not`).

### The readout (`fd_ct_periods.py periods`; exit 1 and nothing written)

- **S:** as the readers' declaration, plus the definition's p_∥ cell sets, which must be {R00–R03, R08–R11} below
  4.5 GeV/c and {R04–R07, R12–R15} above it.
- **Q0:** the control record is this deploy's and says PASS, and the ALL unfold is the one it read
  (`test_refuses_without_a_passing_control`, `test_refuses_an_all_unfold_changed_after_the_control`).
  `test_refuses_another_cell_definition` covers S's cell sets.
- **Q1:** the four receipts as K0. Each period's directory holds exactly its 11 declared unfolds, each made by (e) on
  its own period's dumps with its declared bootstrap seed (`test_refuses_a_missing_or_extra_replica`,
  `test_refuses_a_replica_not_made_as_declared`).
- **Q2:**
  - each MC truth is `s5p_mc_truth_pred.py`'s, made by this deploy, of its own period's npz;
  - each flux is constant over p_T;
  - the periods' exposure sums to ALL's, to 10⁻⁹. Σ_X POT_X Φ_X = POT_ALL Φ_ALL holds by the flux's construction.
- **Q3:** every unfold and MC-truth integral is positive on all 16 cells (`test_refuses_a_non_positive_integral`;
  `test_refuses_a_truth_of_other_code` covers Q2).
- **Q4:** 5A's readout matches its pin.
- **Q5, an assertion:** Σ_X e_X g_X = 0 and C_PL,5D is PSD of rank ≤ 2. A relative variance below 10⁻²⁴ counts as zero.

**The leak guard** (exit 3, nothing written) receives f, every unfold integral and every MC-truth integral. Following
amendment 1, an integral within LEAK_REL of f is dropped from the guard's table, since it IS f:
`test_an_integral_within_leak_rel_of_f_is_dropped_from_the_guard` plants one. A string with "1"s then passes, and the
unfiltered guard refuses it, which is the mode amendment 1 repaired.
- **A ratio against such an integral is X/f − 1 to LEAK_REL, so the guard refuses it.** The run then stops, by
  design, rather than write it (`test_a_ratio_against_a_near_f_integral_is_refused_as_relative_to_f`).
- **Expected not to arise:** K3 places X_ALL at the jitter scale from f, of order 10⁻³, not 10⁻¹³, and the periods
  differ from f by their exposure.
- **The control:** an X_ALL within LEAK_REL of f passes (`test_an_all_integral_within_leak_rel_of_f_is_not_falsely_refused`),
  since it writes only q.
- **Planted leaks are refused:** an absolute value, a period's ratio to f, an MC truth's ratio to f, and a ratio
  X_ALL/f − 1 in the control.
- **Combinations:** nothing is written relative to ALL. With the committed `mp1s1_zero` standing for X_ALL, an
  X/ALL ratio, or J36 (Σ e_X X_X / X_ALL − 1), would give absolute period integrals back, so neither is written
  (review H2). `test_the_readout_recomputed_by_hand` requires no comparison against ALL or J36.

**The readout recomputed by hand** (`test_the_readout_recomputed_by_hand`):
- the dr, raw and MC ratios, χ²_M, the noise expectation and the ten paired draws, the p_∥ contrast, the exposure
  share and C_PL,5D, from the planted cell integrals by explicit loops;
- three planted cases: periods agreeing to 10⁻⁹, a 7% step above 4.5 GeV/c in PB, read where it was planted, and a
  planted 5A offset.

**The tables** are regenerated and compared byte for byte (`test_the_committed_tables_are_the_generators`).
- Job A: four lanes of the declared steps and arguments.
- Job B: each declared (period, replica) exactly once, on eight lanes, at seed 42, with a seed block per period
  whose three Poisson streams overlap no other replica's (`test_each_period_has_its_own_seed_block`).

**The submit stages,** in a throwaway git repo with a stub `sbatch` and a stub login interpreter (`FD_CT_PY`, set only
by the tests):
- the committed arguments: exactly one `--qos=regular` and one time limit, cpu, one exclusive node, `--no-requeue`,
  the lane geometry, no GPU, and the flux staging;
- each refusal: a deploy not at the pin, an existing run directory (four), a `$B` the tables do not write under, a
  gate that does not pass (both stages), and existing period unfolds;
- that the steps' output folders exist before job A, and that the lanes of each job fit one node's 256 CPUs and
  487,802M (`test_the_lanes_fit_one_node`).

## 4. Statistics and choices, as built

- **Why MP-1's lateral form, and not `s5c_dump_bkg.py`.**
  - `s5c_dump_bkg.py` writes `bkg_reco` as float32. `s5p_input_dumps.py lateral` writes it in float64, which is how
    MP-1's `lat_zero_bkg.npz` holds it.
  - The refinement trains on these coordinates in float64 (`s5n_pseudo.signed_sample`), so the float32 chain cannot
    be bitwise mp1s1_zero.
  - `lateral` needs a CV npz for its data-row and flux checks (`s5p_input_dumps.py:165-166`). So it is given the
    period's own nn_dump npz, which it must reproduce, and `check` requires the two npz to agree key by key.
  - Given its own period's npz, lateral's checks cannot fail on its own data (review L1). It runs for the background
    dump's form, at one dump's extra cost per lane. `FD-CT-5B-INPUTS.md` §5's "cannot be used" is about the full CV
    npz as `--cv-npz`, which is not used here.
  - The director accepted this on 2026-10-30.
- **The code is MP-1's** (`fd/receipts-ct/5b/probe/p1_chain_code.{py,out}`, at `ba440b19`):
  - `nn_dump_inputs.py`, `unfold_nd_omnifold_unbinned.py`, `hadd_universes_full.py` and every unfold module are
    byte-identical to MP-1's deploys;
  - `s5p_input_dumps.py` differs only in `detector`;
  - `unfold_2d_omnifold_unbinned.py` differs only in `main`, plus 23 added top-level definitions;
  - `s5p_truths.py` differs only in `fine_weight` and `main`, plus two additions. `fine_weight` serves the pseudo
    truths, which `--construction data` never builds;
  - nine of the ten code digests recorded in `mp1s1_zero`'s meta equal main's files; the tenth is
    `unfold_2d_omnifold_unbinned.py`.
- **The MC truth T_X** is `s5p_mc_truth_pred.py` on the period's own npz: its own flux, POT, completeness and nucleons.
  r_X = X_X / T_X is 2D's double ratio (`2d-closeout/playlist-term/DESIGN.md` §2).
- **The exposure share** is e_X = POT_X Φ_X / Σ_Y POT_Y Φ_Y, with Φ the mean of the flux's p_T bins. It is 2D's
  (`2d-closeout/period-unfold-20261014/scripts/analyze_periods.py:194-195`); the data-POT share sits beside it.
- **The noise reference:**
  - d_X,k = X_X,b=k / X_X,s42 − 1 over the ten bootstrap replicas (`s5n_pseudo.bootstrap_replica`: Poisson on data,
    MC and template rows, refit per replica);
  - N = Σ_X (a_X a_Xᵀ) ∘ mean_k d_X,k d_X,kᵀ, and the paired draws are Σ_X a_X d_X,k, as 2D's `analyze_periods.noise`;
  - a_X = (1, −1) for X/Y;
  - each period's replicas come from its own seed block (PA 1001–1010, PB 2001–2010, PC 3001–3010, 2D's). A seed
    shared across periods gives row i the same Poisson weight in both, since `bootstrap_replica` seeds its streams
    from the seed alone. That correlates the periods' noise positively, and so biases low the paired draws, g's
    noise σ and C_PL,5D's noise floor (review M1, `review/probe_shared_seeds.py`);
  - the replica leaves `denom_nd`, and so T_X, unchanged, so d is the same for X and for r;
  - **no seed term:** zero for (e) (§7 item 1). 2D's pooled C_ML has no 5D counterpart, for the same reason.
- **The metric** is the reported M = (C_total + C_resp)/(f fᵀ). χ² values are distances in it, beside their noise,
  not tests. 2D's 205-cell χ² was unusable (`2d-closeout/period-unfold-20261014/REPORT.md` §4). On 16 cells the
  matrix is full rank, but the same caution applies to reading the numbers.
- **The p_∥ contrast** is [I_hi(num)/I_hi(den)] / [I_lo(num)/I_lo(den)] − 1, over the cells above and below
  4.5 GeV/c; for dr, each I is over its MC truth. **It is not 2D's step.** That step was at 8 GeV/c, inside the cells'
  [4.5, 60) range. Its noise σ comes from the paired draws, as 2D's step's did.
- **C_PL,5D** is DESIGN §2 on the cells: m = Σ e_X r_X, g_X = r_X/m − 1, k = V2/(1 − V2), C = k Σ e_X g_X g_Xᵀ.
  - Its **noise floor** is the same construction on pure noise around agreeing periods: g_X,k = d_X,k − Σ_Y e_Y d_Y,k,
    averaged over k. DESIGN §3 discloses that the term does not subtract the noise.
  - The readout prints each σ's ratio to the floor.
- **5B against 5A:** Δ_X = g_X,5B − g_X,5A, against g_X,5B's noise σ (the floor's per period) and in M's metric.
  - 5A's g is 2D's projected under the assumption that the offset does not depend on E_avail, q3 or W inside a 2D bin.
  - Δ is where that assumption and the 5D unfold differ. 5A's own noise has no reference here, and the label says so.
- **Not written: X/ALL and J36.** 2D compared each period with the pooled result and wrote J36. Here the pooled
  result, once K2 holds, is the committed `mp1s1_zero`, so either would give absolute period integrals back
  (review H2). The period comparisons among themselves, C_PL,5D and 5A's test are unaffected.

## 5. The readouts

**`fd-ct-5b-precheck/1`:**
```text
labels{what}, verdict, controls_passed[S, K0], cells, K3_within_tolerance_of_f{as below},
inputs_sha256{mp1_zero, jitter, s1_npz, cresp, definition}, code_sha256, argv
```

**`fd-ct-5b-control/1`:**
```text
labels{what}, verdict, controls_passed[S, K0], cells,
K1_inputs_bitwise_mp1_zero{pass, failed_keys, lat_npz_bytes_equal}, K2_unfold_bitwise_mp1_zero{pass, max_rel_diff_fine_cells},
K3_within_tolerance_of_f{pass, within_by_cell, cells_over, tau_rel, tau_k, sigma_jitter_rel, written},
inputs_sha256{all_receipt, all_unfold, mp1_zero, jitter, s1_npz, cresp, definition}, code_sha256, argv
```

**`fd-ct-5b-periods/1`:**
```text
labels{what, cpl, vs_5a, contrast, no_threshold, not_citable_for}, controls_passed[S, Q0-Q4], assertions_passed{Q5},
cells, cell_sets, constants{periods, exposure_share, k, n_boot, bootstrap_seeds, metric, noise},
comparisons{raw_X/Y, dr_X/Y, mc_X/Y for X/Y in PB/PA, PC/PA, PC/PB:
            {shift, integral_shift, chi2_M, pz_contrast,
             noise{expected_chi2_M, draw_chi2_M, exceeds_every_draw, sigma_rel, abs_shift_over_sigma(_summary),
                   pz_contrast_sigma, pz_contrast_z}}},
C_PL5D{C_PL5D_rel, rank, sigma_rel(_summary), sigma_ratio_to_M(_summary), trace_share, noise_floor_sigma_rel,
       sigma_ratio_to_noise_floor},
g_vs_5A{periods{X: {g_5b, g_5a, difference, g_5b_noise_sigma, abs_difference_over_noise(_summary), difference_chi2_M}}},
sigma_rel_M, inputs_sha256{control, readout_5a, receipts, unfolds, s1_npz, cresp, definition}, code_sha256, argv
```

**stdout:** the PASS lines; one `[5B precheck]` line, one `[5B control]` line, or three `[5B] dr_…` lines with the
C_PL,5D line; and the `wrote` line.

**How the report reads them.** No 5B number is called consistent or inconsistent; that reading is Joseph's. The report
prints each comparison's χ²_M beside its noise expectation and its ten draws, and its contrast with its z. It quotes
addendum §5.3's words only as the question asked.

## 6. Code and tests

- **`nd-unfolding/fd_ct_period_inputs.py`** (new): `run_stage_flux`, `run_merge`, `run_check`, `run_unfold`.
- **`nd-unfolding/fd_ct_periods.py`** (new): `receipt`, `unfold`, `jitter_sigma`, `guarded`, `k3`, `run_precheck`,
  `run_control`, `run_gate`, `assess`, `contrast` and `run_periods`. It imports `fd_ct_readers` (`common`, `near_f`, `write`), which is unchanged.
- **`nd-unfolding/submit_fd_ct.sh`:** adds `5b-inputs` and `5b-periods`. The `3b` stage is unchanged, and 3b's own
  tests pass on it.
- **`fd/receipts-ct/5b/make_5b_tables.py`**, its four tables, and the four flux copies.
- **Tests:** `nd-unfolding/tests/test_fd_ct_periods.py` (new). Its classes: `Definitions`, `StageFlux`, `Merge`,
  `Check`, `Unfold`, `RootReaders` (2, ROOT only), `Jitter`, `Control`, `Precheck`, `Gate`, `Periods`, `Tables` and
  `Submit`.
- **Probe:** `fd/receipts-ct/5b/probe/p1_chain_code.{py,out}`.
- **Review:** `fd/receipts-ct/5b/review/` (§11).
- **Mutation receipt:** `fd/receipts-ct/5b/mutants_5b.{py,log}` (§11).

## 7. For the director

1. **Seed 43 is dropped, so 34 unfolds, not 37.** (e)'s estimator-seed effect is zero by construction: the S1 seed
   block, ruled a measurement in `S1-DIRECTOR-RULINGS.md` §2 (`:47-88`, choice 9 at `:67`), which discharged choice 9. Accepted
   2026-10-30.
2. **MP-1's lateral dump form,** for the float64 reason in §4, which is what makes K2 possible. Accepted 2026-10-30.
3. **The 2D period flux files,** force-added as copies with their digests, plus the data-POT refusal per period.
   Accepted 2026-10-30.
4. **The pooled control:** K1 and K3 as proposed, and K2 on the bit-reproducibility records of §3. Accepted
   2026-10-30, with K2's records cited and its mismatch declared a STOP.
5. **No classification rule.** The report prints the numbers beside their references and does not call them
   consistent or inconsistent. Accepted 2026-10-30.
6. **Two jobs, not one, and a precheck before them,** so that no period unfold exists until the control has passed
   and the director has its record (§2.4). The precheck spends nothing (review M2).
7. **A ratio against a near-f integral stops the run** (§3). Under the guard it is relative to f; K3's tolerance makes
   it improbable.
8. **The fallback, not declared here.**
   - If K1 or K2 fails, the INPUTS record names a new CPU-only CV event loop over the 12 playlists
     (`FD-CT-5B-INPUTS.md` §3). Priced from MP-1's measured per-variant cost, 3.913 node-h for 11 variants, that is
     about 0.36 node-h for the loops **(arithmetic, `measurement-paper/phase1/mp1/S1-REPORT.md:102`)**, before
     packing overheads. It would need its own declaration and binding.
   - A K1 or K2 failure would more likely point at the dump or the environment than at the loops. G1 already ties the
     zero loops to W2b's rrzero. So the report would bring the director the failing keys first.
   - A K3 failure, which the precheck finds before job A, is a difference between MP-1's zero chain and production.
     No new event loop would change it, and the director decides what follows.
9. **Storage:** `$B` and `$P/fd-ct-5b-dev-20261030/` (§11) join the pscratch retention list. The small products and
   the ALL dumps go to HPSS (§2.7). Nothing goes to CFS.
10. **X/ALL and J36 stay dropped,** ruled by the director by message on 2026-10-30. 2D wrote them; here they would
    give absolute period integrals back through the committed `mp1s1_zero` (review H2). The ruling, quoted: "keep
    X/ALL and J36 dropped. Ruling 6's leak guard stands. No absolute period integral, and no form that returns f, is
    written. The period result is reported only in the f-free forms the 2D design uses: the double ratios and offsets
    g_X, C_PL,5D relative to f, and the χ² against the reference. K3 stays a per-cell flag. If a reviewer of the
    readout later needs an absolute scale, that is a new declared reader, not an amendment of this one."

## 8. Pinned bytes

At this declaration's commit:

| file | sha256 |
|---|---|
| `nd-unfolding/fd_ct_period_inputs.py` | `4d005f265ea6abf4ee7cfec988fe7c06553556ca7984387929f77409dfc244b1` |
| `nd-unfolding/fd_ct_periods.py` | `ec6bc7f5b292195c7b3488ad9903c2ad7a5dc22746349e7c3fbb9737e283ed3e` |
| `nd-unfolding/tests/test_fd_ct_periods.py` | `933c740d93f03e524906f161d2c4ee8e11a69bdd114cedd210832cbd1eb78d60` |
| `nd-unfolding/submit_fd_ct.sh` | `d16f52bc241357dbf51be5139cd172c601e206979a273cdbcc91227d0f14c705` |
| `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ct/5b/make_5b_tables.py` | `4cc9ed7857a82b61078a355f3e5ed812e0913a8b0c803004cbac1ebc8e0b6c5c` |
| `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ct/5b/5b-inputs-steps.tsv` | `fc08be826620364ebbe62ab6f29d79aeac9133ac3031a7664b82f7cb79181eb4` |
| `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ct/5b/tasks-5b-inputs.tsv` | `e72c65313478b5aa8cdea0b02346d4624d4c84c6ba33df52a457040c5011fe18` |
| `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ct/5b/5b-periods-steps.tsv` | `74dba155b13821b082a67e927fbfd56bf2f55d09dabf5e1172a4f62399a22e4e` |
| `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ct/5b/tasks-5b-periods.tsv` | `bf3d23cf2afa2f55409535a071d03aa48048502122aced42d6e84f9b1dd542e4` |
| `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ct/5b/flux/runEventLoopMC_ALL.root` | `e3dc9e63bc8db07ab545cee6d8b227cdaa7f8249c657cc1a60119020dd6a86de` |
| `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ct/5b/flux/runEventLoopMC_PA.root` | `927f5af214b15935c1093b83c7e703730b8a5993b5e8f43f60a56eb8f07963fe` |
| `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ct/5b/flux/runEventLoopMC_PB.root` | `c64637d58961c4681f83611ab79f057f741329398cde00df175fac28dad15f0d` |
| `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ct/5b/flux/runEventLoopMC_PC.root` | `95c45a5f91f1fc356bfde74b463e1a24a70d698d8693a766773a6a37c3bdfafc` |
| `nd-unfolding/fd_ct_readers.py` | `f4cc51c8fdba141b4ae3e289ee983d755c0cd5b90a82d40fe71d2e56a4447464` (unchanged from main) |
| `nd-unfolding/fd_f0_regrade.py` | `0dfa722c2b74abed09fb255ccb7c0e80e6c55eb922ea1326dd74e6c880697aa2` (unchanged from main) |
| `nd-unfolding/s1_assemble.py` | `b157250af21a2ef74e4164db6009a40ac596e225f33ac655475798ef49f613f7` (unchanged from main) |
| `nd-unfolding/s5p_stage1_inspect.py` | `26569afc0da46f21167e0908014712cd800c1e14ac63a4b245a0b493c76d3d71` (unchanged from main) |
| `nd-unfolding/s5p_numerics.py` | `7ad8ca0f73989128b783b59d55670687c293d186b2643ea799a3e67c047bf185` (unchanged from main) |
| `nd-unfolding/s5p_input_dumps.py` | `7e925087b45b99dd94b75e45a09b5ef6dca826f594c86307c6c7d09f15058807` (unchanged from main) |
| `nd-unfolding/nn_dump_inputs.py` | `6e8061f836e9ac941f24ca518907c1c94efe772e9d92cf29eeeb940062c8b685` (unchanged from main) |
| `nd-unfolding/s5p_mc_truth_pred.py` | `e4518d0a75c82c7c232ec079e715d47a64111222e15fa60ac9d1ecec9265ddb5` (unchanged from main) |
| `2d-unfolding/uq/hadd_universes_full.py` | `cfa457cb8e979db4df3e6c088c2b89a6e7a107b25763cdc2b05200d6fe720da0` (unchanged from main) |
| `nd-unfolding/fd_f1_lane.py` | `fbcb786923cabd8ab9177525a4b95afaec60486b2a0670ca598d048ebe835a7c` (unchanged from main) |
| `nd-unfolding/s5c_array.sh` | `dd95db5de1a801eb6b47c8d60bc7da43532ed2ad38e10597ae2db94c0a12526f` (unchanged from main) |
| `docs/orchestration/state/gpu-timing-20261023/tools/sbatch_timing_packed.sh` | `b72aaa627d12e6953ad6b1f40a4ae35ffd9b5439db3c0114defe93742f14c6d3` (unchanged from main) |
| `nd-unfolding/pv-ladder/readouts/h2_definition.json` | `b67907615fe2e903e60ae6caa1c141fa007676c0a1b3ae9f42490d331bfdda89` (unchanged from main) |

## 9. Ledger, storage and stops

- **Ledger:** one row each for the deploy and tests, job A (with its `sacct` charge), the control, job B, the readout
  and the preservation.
- **Storage:** as §7 item 9.
- **Stops:** §0's stop rule.

## 10. Not changed

C_resp, every covariance, cell, readout and κ; 3a's, 4C's, 5A's and 3b's readers and readouts; `fd_ct_readers.py`;
`docs/analysis-note/**` by hand. The merge of main regenerated `docs/analysis-note/records_estimators.tex`, as
`merge_main.sh` does: its three CATALOG line pointers moved from `:688`, which main's copy cited although main's
CATALOG holds that line at `:716`, to `:717`. The standalone note's sync is the director's. Claims and publication
are Joseph's.

## 11. Review dispositions

**An independent read-only review** of `ba440b19`, by a Claude Opus 5.5 subagent of this session, in its own
detached worktree, which it left clean (`git status --porcelain` empty). Its report is kept verbatim as
`fd/receipts-ct/5b/review/REVIEW.txt` (`1cbbf4dc3ce5e453…`), with its three probes and their logs.

**It confirmed:**
- that the ALL chain is MP-1's zero chain: the periods, the order, the merge tool, the dump and unfold code since
  MP-1's pins, the `--cv-npz` choice, the flux bins and the unfold argv;
- the pins;
- the control's isolation;
- σ_R;
- the statistics, against 2D's `analyze_periods.py` and DESIGN §2–4;
- the leak guard number by number, near-f handling included;
- the submit stages' QOS, CPU, `--no-requeue`, pin and B checks, job B's memory and both time limits.

**Its findings, and what was done:**
- **H1. Job A could not finish:** nothing created `$B/{dumps,truth,inputs}` (`review/probe_dirs.py`). **Done:** the
  submit stage creates them after its refusals, and `check` creates its own output folders. Tests cover both.
- **H2. The control record gave f back,** because q τ = |X_ALL/f − 1| and X_ALL is the committed `mp1s1_zero` once K2
  holds (`review/probe_leak.py`: f recovered to 2.2 × 10⁻¹⁶). The X/ALL ratios and J36 gave absolute period integrals
  back the same way. **Done:**
  - K3 is written as a flag per cell;
  - X/ALL and J36 are not written (§4; §7 item 10);
  - a test requires that no written number be |X/f − 1| or q.
- **M1. Shared bootstrap seeds across periods** correlated their noise (`review/probe_shared_seeds.py`). **Done:** a
  seed block per period, 2D's, with a test that no replica's three streams overlap another's.
- **M2. K3 is fixed once K2 holds.** **Done:** `precheck` decides it before job A at 0 node-h, and job A's gate
  requires its PASS.
- **M3. The ALL unfold ran in a 64-CPU step,** where `mp1s1_zero`'s ran in 32. **Done:** job A's lanes are MP-1's
  32 CPUs.
- **M4. Four 120G lanes exceeded the node's 487,802M allocation.** **Done:** 56G lanes, with a test of both jobs'
  geometry against one node.
- **M5. The period gate accepted any JSON saying PASS.** **Done:** `gate` checks the schema, this deploy's code, the
  ALL unfold's digest and the three period receipts; both submit stages call it, and it has its own tests.
- **L1. Lateral's checks cannot fail on the period's own npz.** **Kept,** for the background dump's form, and stated
  in §4, with the INPUTS record's "cannot be used" scoped.
- **L2. Cheap checks after expensive steps.** **Done:** `merge` checks the data POT before any dump reads the merge.
  Tracebacks in place of the tools' exit codes are left; any non-zero exit is a STOP.
- **L3. Test gaps.** **Done:** fixtures that start without the output folders; independent seed blocks; refusal-
  direction tests for Q2, Q3, K0 and the cell sets; the submit tests of the gate; the lanes against one node; the
  combination leak.
- **L4. The p_∥ contrast dilutes a 2D-like step.** **Done:** its label says so.
- **L5. The declaration was missing.** It is this file. Its departures from the addendum are §7 items 1, 2, 6 and 10.
- **L6. Nits.** **Done:** the control refuses while a period unfold exists; J36 is gone. Q1's glob counts a
  `s5p_numerics` partial file as an extra file, which refuses; that is kept as correct. The inputs stage does not
  refuse an existing `$B/control`, because the precheck lives there by design.

**Mutation receipt** (`fd/receipts-ct/5b/mutants_5b.log`, on `fd_ct_period_inputs.py` `4d005f26…`, `fd_ct_periods.py`
`ec6bc7f5…` and `submit_fd_ct.sh` `d16f52bc…`): **66 of 66 killed**, none unapplied, with every file restored.
- The mutants cover:
  - the inputs driver's pins, order, grouping, refusals, POT and flatness checks and folder creation;
  - the control's K0–K3, its flag-only K3, its verdict and exit;
  - the precheck and the gate;
  - the seed blocks;
  - the readout's statistics: the dr direction, the noise pairing and coefficients, the metric, the contrast's
    cells, C_PL's k and mean, and 5A's sign and pin;
  - both guards' tables;
  - the submit stages' pin, refusals, gate, QOS, limits, geometry, folders and flux staging.
- A first pass, before the final tests, left four mutants alive and a second left one. Each was a test gap, and each
  was closed with a test in the direction the check acts (a torn flux copy, a value-preserving dtype change,
  per-period fluxes, a relative truth leak, a pin refusal reached past the gate).

**On the cluster** (login37, under `$P/fd-ct-5b-dev-20261030/`, 1.1 GB, mostly the clone; the director's go-ahead
of 2026-10-30; receipts in `fd/receipts-ct/5b/cluster/`):
- **Run 1, at `2635a99c`:** HEAD equal to the pin and 0 porcelain lines before and after, but the suite **crashed**
  with rc 139 (`cling::CIFactory::createCI(): cannot extract standard library include paths`; `dev.log`,
  `dev-tests.log`).
  - The run called root_6_28's interpreter bare, as the readers' recipe does, and `RootReaders` imports ROOT, which
    segfaults without the env active.
  - No test result came from it.
- **Run 2, the one rerun the director approved,** in the same clone moved to `4514c010`, which adds the
  `BareInterpreter` tests:
  - the env was activated by prefix: the conda hook, then `conda activate`, with no `set -u` (`run2_devtest.sh`);
  - Python 3.11.14, ROOT 6.28/12, LightGBM 4.6.0;
  - the five declared modules **Ran 243 tests, OK, with none skipped** (`dev2.log`, `dev2-tests.log`). The two ROOT
    tests ran: the committed ALL flux reads `DataPOTUsedForFluxWeighting` = 1.057394261158926 × 10²¹, the 2D record's
    value. 3b's real-unfold test also ran;
  - 0 porcelain lines before and after.
- **So that the recipe is exercised and not assumed,** `BareInterpreter` runs `stage-flux`, `precheck`, `control`,
  both gates and `periods` with ROOT made unimportable, and shows that a path that does import ROOT fails there.
- **Locally,** `test_fd_ct_periods` ran 85 tests, OK, with the two ROOT tests skipped. With `test_fd_ct_closure`,
  `test_fd_ct_readers` and `test_oi136_rooted_insert_ratchet`, all passed.
