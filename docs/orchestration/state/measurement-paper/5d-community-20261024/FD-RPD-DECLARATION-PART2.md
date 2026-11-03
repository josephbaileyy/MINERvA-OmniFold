# DECLARATION RPD, part 2 (code): the run-period diagnosis's code, tests, exact commands and pinned bytes (2026-11-02)

**By** the `limitation-resolver` lane, for the director's binding 2 after a fresh Sonnet audit.

**Under:**
- [`FD-RPD-BINDING-1.md`](FD-RPD-BINDING-1.md) (#703), which binds part 1's design
  ([`FD-RPD-DECLARATION.md`](FD-RPD-DECLARATION.md), revision 4, sha256 `b3413ffc…`) and requires for part 2 blob
  digests, tests, a mutation receipt and its own audit before anything runs, stage 0 and stage D included;
- `DECISION-20261102-joseph-quadrant-sentence-sec4-and-validations.md` item 3(b) (#690).

**Declares:**
- the code that implements part 1: `nd-unfolding/fd_rpd_inputs.py`, `nd-unfolding/fd_rpd.py`, the `rpd-a` and `rpd-b`
  stages of `nd-unfolding/submit_fd_ct.sh`, and the tables written by `fd/receipts-rpd/make_rpd_tables.py`;
- the tests (`nd-unfolding/tests/test_fd_rpd.py`) and the mutation receipt (`fd/receipts-rpd/mutants_rpd.py` and
  `.log`);
- the exact commands, in order, and the pins;
- **§6: what part 2 settles that part 1 left to it, and two deviations from part 1's text.** Each deviation is for the
  director's acceptance in binding 2.

**Part 1's rules are unchanged.** Every section number below that is not part 2's own refers to part 1.

**MEASURES:** nothing. The code has run only on synthetic fixtures and the committed H2 definition, locally (no cluster
contact for part 2).

**CANNOT AUTHORIZE:** any run before binding 2; anything part 1 cannot authorize.

**Paths** are as in part 1. `$R` = `/pscratch/sd/j/josephrb/fd-rpd-20261103` (the tables' run directory; it must not
exist beforehand). `$D` = `$R/deploy`, a fresh clone at the bound commit.
`PY` = `env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I -B`, run with root_6_28 activated by prefix and no
`set -u`, as in 5B (§2.1 there).

## 1. The code

### 1.1 `fd_rpd_inputs.py`: stage S, job A's checks, N0's split and the unfolds

| subcommand | where | what | part 1 |
|---|---|---|---|
| `stage --r $R` | login | copies every input of `stage_sources()` into `$R/staged/` through an O_NOATIME descriptor while hashing. Each copy must equal its pin, or it is deleted and the step refuses. Records each source's atime before and after in `staged/STAGED.json` | §1 |
| `flux --r $R` | login | builds X's flux file from the staged baseline files with the pinned combiner's `read_playlist`, its module global `BASE` set to the staged copies, and the combiner's own arithmetic (`combine`). Decides **F1** and computes e. Writes `flux/F1.json` | §1, §4 F1, §5 |
| `check --r $R --playlist X` | job A | X's receipt and MC truth, after the dump and lateral steps (refusals below) | §2, §4 C1 |
| `n0-split --r $R --partition p` | job A | one N0 partition, its 12 pseudo-npz files, background dumps, assignment vectors, receipt and MC truths | §4 N0 |
| `unfold --r $R --what playlist\|n0\|k2 …` | jobs A and B | `s5p_numerics.py` unchanged: config R, 5 iterations, real data, estimator seed 42, with the expected input digests | §2 |

**The pins** (`stage_sources()`, 79 files):

| what | count | pin source |
|---|---|---|
| the zero loops | 12 | `fd_ct_period_inputs.ZERO_LOOPS` |
| the baseline flux and data-POT files | 24 | `BASELINE`, equal to Stage B's `2d-closeout/stageB/evidence/verify-c04/verify_c04.json` (tested) |
| the production flux | 1 | `d40aea69…` (`2d-closeout/period-unfold-20261014/scripts/periods.py`) |
| 5B's period unfolds | 33 | `fd/receipts-ct/5b/run/preserve/INVENTORY.sha256`, read at run time from the deploy |
| 5B's period MC truths | 3 | the same inventory |
| 5B's PC lateral npz and background dump | 2 | `fd/receipts-ct/5b/run/inputs/check_PC.json` |
| MP-1's `lat_zero.npz` and `lat_zero_bkg.npz` | 2 | `fd_ct_period_inputs.MP1_ZERO` |
| S1's assembly | 1 | `db000707…` (`fd_ct_readers.PINS`) |
| C_resp | 1 | `4d8b5797…` (the same) |

**`check` refuses (exit 5, nothing written) unless:**
- the staged loop is X's pinned zero loop;
- the flux file is the one F1 recorded for X;
- the lateral npz is the nn_dump npz key by key;
- the background dump names the lateral npz and the staged loop;
- the npz `flux` key equals X's flux bin contents as F1 recorded them, to 10⁻¹²;
- the npz data POT, the loop's `dataPOTUsed` and the flux file's `DataPOTUsedForFluxWeighting` agree to 10⁻¹².

It records the loop's `mcPOTUsed`, so C1's s_X uses it.

### 1.2 `fd_rpd.py`: the readers

| reader | where | what | part 1 |
|---|---|---|---|
| `stage0` | login | s₀, σ₀ and the branch, from the staged 5B PA and PB products, each meta-checked against 5B's committed check receipts | §3 |
| `staged` | login | stage D: R1's operating-characteristics table, both R1 rules, and R2's reachability with its rule | §5 |
| `controls` | login | C1, K2′ and N0-P, with one verdict | §4 |
| `gate --stage a\|b` | login (the submit stages call it) | job A only after F1's PASS and the stage 0 and stage D records; job B only after this deploy's controls PASSed on the receipts now on disk | §4 Gates |
| `readout` | login | N0's reading, R1, R2 (with p_era) and R3 | §4 N0, §5 |

Every reader writes through `fd_ct_readers.write`, so each output passes F0's `LeakGuard` first. Every reader refuses to
overwrite.

### 1.3 The submit stages and the tables

- `submit_fd_ct.sh rpd-a $D <pin> $R` and `rpd-b`.
  - Each refuses before creating anything unless `$D` is at the pin and its product directories are absent.
  - `rpd-a` also needs `staged/`, `flux/` and `control/`.
  - Each refuses unless every step names `$R`, and every dump step passes `--mcfile` under `$R/flux/`.
  - Then the gate runs. On a pass the stage makes the step folders and submits one job: one exclusive CPU node, QOS
    regular, `--no-requeue`, account m3246, 8 lanes of 32 CPUs and 56 GB, through `sbatch_timing_packed.sh` →
    `s5c_array.sh` → `fd_f1_lane.py`.
- **Job A** (`rpd-a`, 1:00:00, 48 steps):
  - per playlist: `nn_dump_inputs.py` → `s5p_input_dumps.py lateral` → `check`, on its staged loop with `--mcfile` its
    flux file;
  - K2′'s two unfolds;
  - N0's ten splits.

  The fullest lane is estimated at 869 s (`fd/receipts-rpd/packing.json`).
- **Job B** (`rpd-b`, 2:00:00, 492 steps): the 372 playlist unfolds and 120 N0 unfolds, packed longest first by
  780 s × e + 10 s. The fullest lane is estimated at 4,622 s.

**5B's merge step is bypassed.** Each dump reads its playlist's staged zero loop directly. `check` ties the dump to the
pinned loop, and the background dump's meta must name that loop's staged path.

## 2. Exact commands, in order

```bash
# deploy and tests (login)
git clone -q <repo> $D && git -C $D checkout -q <pin> && git -C $D status --porcelain --ignored | wc -l   # 0
# tests with root_6_28 activated by prefix: test_fd_rpd test_fd_ct_periods test_fd_ct_readers test_fd_gencmp_e
cd $D/nd-unfolding/tests && python3 -B -m unittest test_fd_rpd test_fd_ct_periods test_fd_ct_readers
# stage S (login)
$PY $D/nd-unfolding/fd_rpd_inputs.py stage --r $R > $R/logs/stage.out 2>&1      # (mkdir -p $R/logs first)
$PY $D/nd-unfolding/fd_rpd_inputs.py flux  --r $R > $R/logs/flux.out 2>&1
# stage 0 and stage D (login); both records go to the director before job A
$PY $D/nd-unfolding/fd_rpd.py stage0 --r $R --definition $D/nd-unfolding/pv-ladder/readouts/h2_definition.json --deploy $D \
    --out-json $R/control/stage0.json > $R/logs/stage0.out 2>&1
nice -n 19 $PY $D/nd-unfolding/fd_rpd.py staged --r $R --definition $D/nd-unfolding/pv-ladder/readouts/h2_definition.json \
    --deploy $D --out-json $R/control/stageD.json > $R/logs/stageD.out 2>&1
# job A (login submits; one node)
bash $D/nd-unfolding/submit_fd_ct.sh rpd-a $D <pin> $R > $R/logs/submit-a.out 2>&1
# controls (login, after job A)
$PY $D/nd-unfolding/fd_rpd.py controls --r $R --definition … --deploy $D --out-json $R/control/controls.json > $R/logs/controls.out 2>&1
# job B (login submits; one node; only after the controls PASS)
bash $D/nd-unfolding/submit_fd_ct.sh rpd-b $D <pin> $R > $R/logs/submit-b.out 2>&1
# readout (login, after job B)
nice -n 19 $PY $D/nd-unfolding/fd_rpd.py readout --r $R --definition … --deploy $D --out-json $R/readout/fd_rpd.json > $R/logs/readout.out 2>&1
```

- **After each job:** `sacct -j <job> -X -o JobID,State,ExitCode,Elapsed,NNodes,AllocTRES` and each lane's `[f1-lane]`
  lines are recorded. The job must be COMPLETED 0:0 with every lane `done`; anything else is a stop.
- **Exit codes:** 0 written and PASS; 1 FAIL (written) or a refusal (nothing written); 2 argparse; 3 the leak guard.
- **Each run** is from a fresh clone at the bound commit (binding 1 ruling 6).

## 3. Tests

**`tests/test_fd_rpd.py`, 83 tests** (one is skipped locally: it needs ROOT; on the cluster all must run). Locally,
all pass in about 60 s. The suite covers:
- **definitions:**
  - the replica seeds: 360, disjoint, and none of 5B's;
  - the baseline pins equal Stage B's record;
  - the 79 staged sources and their pins;
  - the groupings;
  - N0's t₂₉ thresholds against SciPy;
  - ν and the interval reproduce the 5D label's 1.824 and 0.73–2.56;
  - the calibration gate is 0.0646;
- **stage S:** copies at their pins with atime recorded; refuses a wrong digest (no copy kept), an existing staging
  directory or a missing source; a staged copy changed afterwards refuses; the copy opens with O_NOATIME where the
  platform has it;
- **F1 and the flux:** the combiner's arithmetic; F1 in both directions (a 10⁻¹¹ defect fails in a period, in ALL and
  in a POT; 5 × 10⁻¹³ passes); e is POT × flux;
- **check:** a consistent playlist passes and records mc_pot; each refusal on its one-entry defect;
- **N0:** a partition reassembles bitwise, weights unchanged, POT and histograms sum, completeness equal per cell, the
  draw fixed by the seed; a scaled denominator would break the completeness;
- **unfold:** the declared argv; refuses an existing product, another receipt, or a missing product; each `--what`
  takes exactly its arguments;
- **arithmetic:**
  - the L/H regions;
  - the step and the reference;
  - **all 262,144 class assignments give exactly one pattern** (PERIOD-WIDE 252, SUBSET 756, as audit 2 counted);
  - the pattern semantics;
  - FREE and CARRIES disjoint over 20,000 random resolved cases;
  - classes in both directions, including a single carrier as CARRIES;
  - **the partitions: 9,240 and 83,160, unique**;
  - F against explicit loops;
  - the p tie rule;
  - Σ_δ unbiased;
  - R2's outcome order;
  - stage 0's branches, including a negative step;
  - the OC model reproduces σ₀, and its truths have group mean s₀;
  - the OC table finds each pattern at low noise;
  - R2 reaches EC on exchangeable offsets and CLUSTERED on clustered ones;
- **the readers on a synthetic run directory:**
  - stage 0 SEES a planted 7% step, writes nothing absolute, is ABSENT on a flat ratio, refuses a 5B unfold made from
    other dumps or a changed staged copy, and the guard refuses a planted f;
  - stage D writes both rules, gives no verdict under 200 outer datasets, and honours its budget;
  - C1 passes a correct split and fails each one-entry defect;
  - C1's weight predicate tests hadd's mcPOTUsed additivity;
  - the vectorized measured-weight rule equals the dump's loop;
  - N0-P passes a true partition and fails a completeness defect;
  - K2′ is bitwise;
  - the gates;
  - the readout end to end: PERIOD-WIDE and CLUSTERED on a planted case; NOT COMPUTED outside SEES; a single carrier is
    SUBSET; a planted size bias fires N0 and makes R2 INCONCLUSIVE; refuses without the controls' PASS;
- **tables and submit:** the committed tables are the generator's; job B is every declared unfold once; every dump has
  its `--mcfile`; the lanes fit their limits; both submissions with their limits; the refusals.

**The existing suites still pass:** `test_fd_ct_periods.py` (85, 2 skipped) and `test_fd_ct_readers.py`.

## 4. What the tests found, and the calibration receipt

**The calibration gate does its job.** In the readout fixture (seed 31) with only 3 replicas per playlist, the
replica-resampled null had α̂(0) = 0.17. The gate refused it, so R2 came out INCONCLUSIVE. With 10 replicas, the same
fixture gave α̂ = 0.03. The fixture now uses 10 (`test_fd_rpd.Readout.build`).

**The receipt** `fd/receipts-rpd/calibration_spread.py` and `.log` (the director's request) uses the readers' test
metric, independent Gaussian replicas, 8 realizations of the replica set per count, and 300 null datasets each (Monte
Carlo error about ±0.013):

| replicas | α̂ by realization | min–max |
|---:|---|---|
| 3 | 0.040, 0.050, 0.040, 0.033, 0.033, 0.063, 0.047, 0.027 | 0.027–0.063 |
| 10 | 0.040, 0.053, 0.060, 0.043, 0.070, 0.077, 0.073, 0.047 | 0.040–0.077 |
| 30 | 0.047, 0.060, 0.053, 0.047, 0.043, 0.083, 0.067, 0.047 | 0.043–0.083 |

**Disclosed:** at the declared 30 replicas, two of eight realizations sit above the gate's 0.0646. One of them
(0.083) is above it by more than the Monte Carlo error.
- The permutation test under a replica-resampled null is close to nominal, but it varies by realization.
- So a real run can come out R2 INCONCLUSIVE on calibration alone, as part 1's rule provides.
- Part 1's rule is not changed here. Whether to accept that risk, or to ask for more replicas (part 1 §2 fixed 30), is
  the director's call.

## 5. Mutation receipt

<!-- absence-ok: describes what tests assert (R1 NOT COMPUTED is a declared outcome), not a claim that a result does not exist -->
`fd/receipts-rpd/mutants_rpd.py`, 67 mutants across `fd_rpd_inputs.py`, `fd_rpd.py` and the rpd submit stages, run
against `test_fd_rpd`: **killed 67 of 67, none survived, files restored** (`fd/receipts-rpd/mutants_rpd.log`, on the
final code).
- **The first full pass** killed 60 of 67. The survivors were: S1 not shrunk; σ₀ centred on the replica mean; both stage
  D rules inverted; C1's exact-zero weights unchecked; R1's t̄ gate removed; and the 5B block check removed.
- **Tests added for them:** S1's c equals its formula and is small on noise; σ₀ equals the RMS about s₀; the stage D
  rules agree with their probabilities; `scaled_equal` needs exact zeros; R1 is NOT COMPUTED without a step; and the
  rebuilt 5D block must equal the committed one, refusing a 1% difference.

## 6. What part 2 settles, and its deviations

<!-- absence-ok: design scoping (N0 is built in job A, after stage D), not a claim that a result does not exist -->
**Settled within part 1's text:**
- 5B's merge is bypassed (§1.3).
- The per-playlist flux is built by `fd_rpd_inputs.flux` from the staged copies with the pinned combiner unchanged
  (`BASE` reset). It is not built by 2D's `build_flux.py`, whose pinned path assertion would open the pre-existing
  files.
- C1's `flux` predicate compares the npz key with X's flux bin contents as F1 read them from the file. That is what
  `u2d.load_flux_bins` returns, since it reads the bin contents unchanged (`2d-unfolding/unfold_2d_omnifold_unbinned.py:129-145`).
- N0's pseudo-npz `measured_weights` are carried from ALL's rows. Config R does not read them (part 1 §2).
- T's MC variance in R1 is propagated by a numerical derivative (relative step 10⁻⁶) of each quantity in each member's
  region T.
- **N0's step reference:** each partition's pseudo-1A–1F (the pseudo-playlists at those shares), with the leave-one-out
  rule.
- **Stage D's R1 model** does not include N0's UNRESOLVED clause, because N0 does not exist at stage D.
- **The run directory** is named in the tables (`fd-rpd-20261103`). A later run date keeps that name.

**Deviation 1, for the director's acceptance: C1's `measured_weights` predicate.**
- Part 1 §4 says C1 "recomputes it from X's own arrays and requires equality to 10⁻¹² (self-consistency)". That is not
  achievable from the npz.
- The dump bins float64 coordinates (`nd-unfolding/nn_dump_inputs.py:75-82`, before `.astype(np.float32)` at `:84-86`) but stores
  them as float32, so a row on a bin edge can fall in another bin when recomputed.
- **The code instead** requires the share of rows that agree to 10⁻¹² to be at least 0.999 (`C1_MW_SHARE`) and prints
  the share per playlist.
- Config R does not read this key (part 1 §2), so no readout depends on it.

**Deviation 2, for the director's acceptance: stage D's α̂ at 200 inner datasets.**
- Part 1 §5 says "S0's α̂ at 200 inner is printed beside it, descriptive". Running S0's four scales for every outer
  dataset would roughly triple stage D's login-node time, which part 1 bounds at 2 h.
- **The code** prints S0's α̂ at each scale, averaged over the **first 25 outer datasets per truth**
  (`STAGE_D_ALPHA_OUTER`, under `R2_reachability.alpha_at_inner_descriptive`).
- It is descriptive and enters no rule, as part 1 says.

## 7. Pinned bytes

Git blob digests at commit `855febc2` (the code commit). The deploy verifies each with `git rev-parse <pin>:<path>`;
the ones not written by part 2 are the bound tools it calls unchanged.

| path | blob |
|---|---|
| `nd-unfolding/fd_rpd_inputs.py` | `e2fb919a863430e37ef381aebf8ae6bab160dfb2` |
| `nd-unfolding/fd_rpd.py` | `84ae1c64195a450760d07e6beda4da568bb694ce` |
| `nd-unfolding/submit_fd_ct.sh` | `a75bd8b3bdb5fbd62436efb6707ff55397813c06` |
| `nd-unfolding/tests/test_fd_rpd.py` | `211fe813621d043ee2d2eba467ef9a38f73882d2` |
| `nd-unfolding/fd_ct_period_inputs.py` | `81fc77890264e26ce38661a27e11c3da74c22284` |
| `nd-unfolding/fd_ct_periods.py` | `05c1a9b7f41f04d415306ad36840088c7233bd3f` |
| `nd-unfolding/fd_ct_readers.py` | `3abde33073a69fc3f11fc48a08497e2c1049a93c` |
| `nd-unfolding/fd_f0_regrade.py` | `e4c530b25afda48e0036de24416cea43e467dc45` |
| `nd-unfolding/s1_assemble.py` | `1542ed946f701bff62ec6fe8c08cdc7c2424c599` |
| `nd-unfolding/s5p_numerics.py` | `fa4781edab2447793156fc92ec71aacbba2470cd` |
| `nd-unfolding/nn_dump_inputs.py` | `10fe5671c224ba84c999d065075d049a387a3df5` |
| `nd-unfolding/s5p_input_dumps.py` | `1cd2f25c4f36b8ed68824d2c1748e8e6aee0f987` |
| `nd-unfolding/s5p_mc_truth_pred.py` | `f3c09fd542e43b22af0f835ff7fccc9f49fa80dd` |
| `nd-unfolding/fd_f1_lane.py` | `4ad51a28b58afda9fc21b1fa2a2b82e6ac9c1485` |
| `nd-unfolding/s5c_array.sh` | `327b97b47ac69902603cfd14223bf234c85e04e2` |
| `2d-unfolding/combine_flux_MEFHC.py` | `4f551e29dd35d1d6c7f391df559077c5456493f2` |
| `docs/orchestration/state/gpu-timing-20261023/tools/sbatch_timing_packed.sh` | `22589360aa55946d4a83cdba2af8d103504341d8` |
| `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-rpd/make_rpd_tables.py` | `2fb3ea7c010e56b333062a36fd41702e7c9df9d9` |
| `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-rpd/rpd-a-steps.tsv` | `a53daa3351bf0ded7a715b4a442033b822096621` |
| `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-rpd/rpd-b-steps.tsv` | `8869fab31a584cb1009fe4dbc1081a579743205f` |
| `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-rpd/tasks-rpd-a.tsv` | `c83be1f4a93becce95cd7d5e4288a66ac8f92403` |
| `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-rpd/tasks-rpd-b.tsv` | `3a4cb4381f661a69fa4d2c466a1070569cd212c4` |

`s5p_numerics.py`'s blob equals 5B's bound copy at `2c960659` (`fa4781ed` at both, checked); K2′ checks the result on the cluster.

## 8. Ledger and storage

As part 1 §8 and binding 1 ruling 4 (the HPSS deferral record extends to RPD).

Nothing is submitted, deposited or tagged.
