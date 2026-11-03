# DECLARATION RPD, part 2 (code): the run-period diagnosis's code, tests, exact commands and pinned bytes (2026-11-02)

**By** the `limitation-resolver` lane, for the director's binding 2 after a fresh Sonnet audit.

**Revision 2 (2026-11-03)** answers that audit (prompt and answer verbatim in
`FD-RPD-PART2-AUDIT-SONNET-PROMPT.txt` and `-ANSWER.txt`; 5 MAJOR, 8 MINOR, 5 NIT). §9 gives each finding's
disposition. §4 records the director's ruling on the calibration risk.

**Revision 3 (2026-11-03)** applies the director's two rulings and answers its two asks before binding 2:
- **ruling 1 (a):** C1's `measured_weights` is printed per playlist, not graded, a declared deviation (§6 deviation 1);
- **ruling 2 (a):** F1 grades contents, both POTs and the edges, and prints the errors' max_rel only, as part 1 says
  (§6, deviation 3 resolved);
- **ask (1):** the calibration null rerun with T's MC-variance Gaussian (§4);
- **ask (2):** the L-region edge mutant, shown equivalent in every computed number and killed on the printed record
  (§9);
- **the director's permission:** the three suites of §2 ran on a login node in root_6_28, ROOT tests included (§3).

The mutation receipt is re-run on this code (§5).

**Revision 4 (2026-11-03), for binding 2's addendum A1,** answers stage S's stop (§6, "Stage S's stop and A1"):
- `flux` stopped at its first MnvH1D read, because root_6_28 by prefix has no PlotUtils dictionary;
- `flux` now runs only in the shared checkout's MAT environment, pinned by digest at run time (`mat_environment`,
  exit 7 before any read);
- `verify-staged` re-hashes the 79 staged copies before every later connect reads them, and `$R` is reused;
- a login-only test module reads the real staged files (`tests/test_fd_rpd_mat.py`), and each step's tests run in
  that step's environment (§2, §3);
- the mutation receipt is re-run (§5).

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
- **§6: what part 2 settles that part 1 left to it, and its deviations from part 1's text:** three, deviation 3
  having been resolved by ruling 2. The director has ruled on 1 and 2; 4 is declared.
- **§9: the disposition of each finding of part 2's audit.**

**Part 1's rules are unchanged.** Every section number below that is not part 2's own refers to part 1.

**MEASURES:** nothing physical. The code has run on synthetic fixtures and the committed H2 definition, locally and
on a login node (§3); stage S's first connect ran `stage` and stopped at `flux` (§6). Revision 4 also records the MAT
environment's digests, read through O_NOATIME (§1.4).

**CANNOT AUTHORIZE:** any run before binding 2; anything part 1 cannot authorize.

**Paths** are as in part 1. `$R` = `/pscratch/sd/j/josephrb/fd-rpd-20261103` (the tables' run directory). It must not
exist before stage S's first connect; every later connect requires it, with stage's record (binding 2 A1). `$D` is a
fresh clone at the bound commit in a new subdirectory of `$R` for each connect (`$R/deploy` for the first, `$R/deploy-2`
for the second, and so on).
`PY` = `env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I -B`, run with root_6_28 activated by prefix and no
`set -u`, as in 5B (§2.1 there).
`MATENV` = `source $P/MINERvA-OmniFold/setup_salloc_env.sh` (the shared checkout's, read-only, no `set -u`), then
`export TMPDIR=$R/tmp`, since that script exports TMPDIR=$SCRATCH/tmp. `PYM` = `env -u PYTHONPATH python3 -I -B` in
MATENV (§1.4).

## 1. The code

### 1.1 `fd_rpd_inputs.py`: stage S, job A's checks, N0's split and the unfolds

| subcommand | where | what | part 1 |
|---|---|---|---|
| `stage --r $R` | login | copies every input of `stage_sources()` into `$R/staged/` through an O_NOATIME descriptor while hashing. Each copy must equal its pin, or it is deleted and the step refuses. Records each source's atime before and after in `staged/STAGED.json` | §1 |
| `verify-staged --r $R` | login | re-hashes every staged copy; each must equal its pin and the staging record's digest, and the record must name exactly the deploy's sources at their paths. Writes nothing | binding 2 A1 |
| `flux --r $R` | login, MATENV | first `mat_environment` (§1.4; exit 7 before any read), then builds X's flux file from the staged baseline files with the pinned combiner's `read_playlist`, its module global `BASE` set to the staged copies, and the combiner's own arithmetic (`combine`). Reads each staged loop's POT. Decides **F1** (contents, both POTs and edges; the errors printed) and the loops' POT (`flux_decision`) and computes e. Writes `flux/F1.json` | §1, §4 F1, §5 |
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

### 1.4 `flux`'s pinned MAT environment (binding 2 A1)

The per-playlist flux histogram is a `PlotUtils::MnvH1D`, which PyROOT reads only with MAT's dictionary loaded. That
comes from the shared checkout's `setup_salloc_env.sh`: it activates root_6_28 and then sources the build tree's and
MINERvA101's setup scripts. These are build artifacts, not tracked in git, so they are absent from a fresh clone.

**The environment is the shared checkout's mutable state, pinned by digest at run time, not by git.**
`fd_rpd_inputs.mat_environment()` runs first in `flux`. It loads MnvH1D's dictionary (`TClass::GetClass`), then
reads `/proc/self/maps` and the pinned files' digests through O_NOATIME. It refuses with exit 7, before any staged file
is read, unless `mat_env_problems` finds nothing:
- the six setup scripts at their digests (`MAT_SETUP`): `setup_salloc_env.sh` `ea3c6998…`,
  `unbinned_unfolding/build/setup.sh` `40ff3a3d…`, and `MINERvA101/opt/bin/` `setup.sh` `e22a5b93…`, `setup_MAT.sh`
  `733e9cd8…`, `setup_MAT-MINERvA.sh` `c2591016…`, `setup_UnfoldUtils.sh` `bd305c17…`;
- the MAT files (`MAT_FILES`) at their digests: `libMAT.so` `5901f18a…`, `MATDict.rootmap` `bd669308…` (it names
  libMATDict.so for PlotUtils::MnvH1D) and `MAT_rdict.pcm` `9eedbfd9…`;
- the symlink `libMATDict.so` resolving to `libMAT.so` (recorded as resolved; its target is digested above);
- the shared libraries mapped into the process from MINERvA101/opt/lib equal to {libMAT.so};
- `PLOTUTILSROOT` and `MINERVA_PREFIX` equal to that checkout's `MINERvA101/opt/lib` and `MINERvA101/opt`;
- MnvH1D's dictionary loaded.

Everything is recorded in `F1.json` under `environment`. The digests were taken on 2026-11-03 through O_NOATIME,
read-only. Nothing is written into the shared checkout.

## 2. Exact commands, in order

**Each step's environment (binding 2 A1), and its tests run in it:**

| environment | steps | tests run in it |
|---|---|---|
| root_6_28 by prefix (`PY`) | `stage`, `verify-staged`, `stage0`, `staged`, `controls`, `readout` | `test_fd_rpd test_fd_ct_periods test_fd_ct_readers`; `test_fd_rpd_mat.ZeroLoops` |
| MATENV (`PYM`, §1.4) | `flux`, with its `loop_pots` | `test_fd_rpd`; `test_fd_rpd_mat` whole |
| `s5c_array.sh`'s (job A, job B) | the dumps, `check`, `n0-split`, `unfold` | `test_fd_rpd_mat.ZeroLoops` (`loop_pots`, `check`'s only ROOT read) |

`s5c_array.sh` sources the deploy's `setup_salloc_env.sh`. In a fresh clone both MAT sources fail ("No such file or
directory"), so job steps run in root_6_28 alone. 5B's 12 job env logs show exactly this (§6), and nothing 5B read
needed MAT. Job A is unchanged; its only ROOT read, `loop_pots`, is tested on the 12 staged zero loops in root_6_28.

```bash
# deploy and tests (login), root_6_28 by prefix
git clone -q <repo> $D && git -C $D checkout -q <pin> && git -C $D status --porcelain --ignored | wc -l   # 0
cd $D/nd-unfolding/tests && python3 -B -m unittest test_fd_rpd test_fd_ct_periods test_fd_ct_readers      # none skipped
# stage S's first connect (login), root_6_28 by prefix: ran 2026-11-03, stage rc 0, flux stopped (§6)
$PY $D/nd-unfolding/fd_rpd_inputs.py stage --r $R > $R/logs/stage.out 2>&1      # (mkdir -p $R/logs first)
# stage S's second connect (binding 2 A1), $D = $R/deploy-2
$PY $D/nd-unfolding/fd_rpd_inputs.py verify-staged --r $R --deploy $D > $R/logs/verify-staged-2.out 2>&1   # root_6_28
FD_RPD_R=$R python3 -B -m unittest test_fd_rpd_mat.ZeroLoops                                             # root_6_28
# then in MATENV: TMPDIR=$R/tmp re-exported
python3 -B -m unittest test_fd_rpd && FD_RPD_R=$R python3 -B -m unittest test_fd_rpd_mat                  # none skipped
$PYM $D/nd-unfolding/fd_rpd_inputs.py flux --r $R --deploy $D > $R/logs/flux.out 2>&1
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
- **Each run** is from a fresh clone at the bound commit (binding 1 ruling 6), in a new subdirectory of `$R`; every
  connect after stage S's first starts with `verify-staged` (binding 2 A1).
- **`flux` exit 7:** not the pinned MAT environment, nothing read or written.

## 3. Tests

**`tests/test_fd_rpd.py`, 121 tests.** Five need PyROOT and are skipped locally: the combiner-loading test and
`RootPaths`' four. On the cluster all must run. Locally the other 116 pass in about 100–180 s.

**The five ROOT tests use plain-TH1D and TParameter fixtures that they write themselves. They do not cover a MAT read.**
Stage S's first connect showed the gap: all five passed in root_6_28, and `flux` then stopped at the first real
MnvH1D (§6). `RootPaths` now says so, and stubs `mat_environment` with a value the F1 record must carry.

**`tests/test_fd_rpd_mat.py`, 3 tests, login only (revision 4),** the tested-language counterpart. It reads only
`$R/staged`, re-hashing each copy against the staging record first, and writes nothing. Without `FD_RPD_R` or ROOT,
every test errors rather than skips:
- `Mat` (in MATENV): `mat_environment` passes and returns the pinned digests and the resolved symlink; each of the 12
  staged baseline flux histograms is a `PlotUtils::MnvH1D`; and the pinned combiner reads all 12 to finite, positive
  contents and POTs, with non-negative errors;
- `ZeroLoops` (in both environments): `loop_pots` reads all 12 staged zero loops to finite, positive data and MC POTs.

**Added to `test_fd_rpd` in revision 4:**
- **`MatEnv`:** the pins name the six setup scripts and three MAT files. The pinned environment has no problem, and
  each single departure is exactly one problem: any setup or MAT digest wrong or missing, the symlink elsewhere or
  absent, an extra or a missing mapped MAT library, either variable wrong or unset, no dictionary. Mapped files
  outside MAT's lib do not count. `mat_environment` passes the pinned environment and records it, and refuses each
  departure with exit 7. The digests are read through O_NOATIME. The maps parser keeps paths with spaces. `flux`
  outside the environment exits 7 before any staged read, with nothing written;
- **`verify-staged`:** it passes the staged copies and refuses each one-entry defect: a changed byte, a missing copy,
  a moved pin, a moved source, a source the record lacks, a record row the deploy lacks, a record digest changed. It
  writes nothing.

**On a login node (revision 3, the director's permission of 2026-11-03).** `fd/receipts-rpd/root_tests_login.sh` runs
the three suites of §2 in root_6_28 from a /dev/shm clone. It activates the env by prefix with no `set -u` and puts
refusing `sbatch`, `srun` and `salloc` shims first on PATH. TMPDIR is in the clone, nothing reads pscratch or CFS, and
the clone is deleted at the end. root_6_28 has no uproot, and none of the three suites needs it. A precheck at
`c3e235b2` on login02 gave test_fd_rpd 110 OK, none skipped (the five ROOT tests ran); test_fd_ct_periods 85 OK, none
skipped; test_fd_ct_readers 77 OK. Porcelain and `squeue --me` were empty before and after. The receipt is the same
script on the head that carries this text, in `root_tests_login.log` (its HEAD and node lines).

**Revision 4:** `root_tests_login.sh` now runs each suite in its step's environment (§2), with `FD_RPD_R=$R`, so
`test_fd_rpd_mat` reads the staged copies. A precheck at `45b09d40` on login02 (19:37–20:25Z) gave, with nothing
skipped and no shim called:
- root_6_28 by prefix: the three suites 283 OK; `test_fd_rpd_mat.ZeroLoops` 1 OK;
- MATENV (`PLOTUTILSROOT` and `MINERVA_PREFIX` at the shared checkout): `test_fd_rpd` 121 OK; `test_fd_rpd_mat` 3 OK,
  so `mat_environment` passed in the real environment.

The full environment prints ROOT's rootmap warnings ("class RooUnfold… found in libUnfoldUtilsDict.so is already in
libRooUnfold.so"), which are known and harmless. The receipt is the same script on the head that carries this text.

**Added in revision 3:**
- **F1 (ruling 2):** an error defect of 10⁻³ passes and is printed at its size (`errors_max_rel_printed`); the graded keys
  are exactly contents, both POTs and edges; a 10⁻¹¹ defect in an edge or in the MC POT fails;
- **the regions, in both directions:** a fine cell has L (H) weight if and only if it is a reporting cell inside
  [1.5, 8) ([8, 15)); before, only the "only if" was asserted;
- **the region edges** are pinned with the declared sizes. The stage-0 record prints them.

**Added in revision 2, for the audit's test gaps:**
- **definitions:** stage D's and the readout's sizes and seeds; the era grouping;
- **the seeds in use:** every numpy generator stage D and the readout make is recorded while they run, and the set
  must be exactly the declared one (`SEED_OC`, `SEED_REACH`, `SEED_READOUT`, and `SEED_N0_EFFECT` when N0 fires);
- **stage S without ROOT:** `flux_decision` passes equal loop POTs, passes a 5 × 10⁻¹³ difference and fails a
  10⁻¹¹ one, and builds e from the loops' POT;
- **`read_truth`:** it refuses a NaN or inf in the truth or in its variance. Q3 never sees the variance;
- **helpers, each against its formula:**
  - the replica deviations are about their own mean and scaled by √(n/(n−1));
  - a noise draw is one replica deviation plus T's MC variance;
  - R1's gate;
  - SIZE-BIAS-g and SIZE-BIAS-t each force the small set UNRESOLVED;
  - N0-P's 5σ share bound;
  - stage D's truths: T1 is psd(C_PL5D/V2), T3 the half-amplitude mix;
  - R3's k₁₂, ρ_raw and ρ_deb;
  - p_era over the era partitions;
  - N0's effect re-runs the null with b̄ added;
- **T's MC variance:** the analytic first-order variance equals `t_noise`. Removing it from any R1 σ, or from R2's
  noise, changes the readout;
- **N0's reading:** the three-smallest set, its mean and its SE with ddof 1;
- **Q3:** a non-positive or non-finite integral in a replica, a region or an N0 vector refuses;
- **N0's forced UNRESOLVED reaches R1:** when N0 fires, exactly the three small playlists reach `classify` forced;
- **the readout's guard:** it refuses a planted absolute integral and a planted X/f − 1. Only the second tests the
  guard's integral list: the absolute integral is below `LEAK_FLOOR`, which any guard refuses;
- **the gates:** job A needs this deploy's stage 0 and stage D records, made on this F1; job B needs N0 receipts at the
  digests the controls recorded, and this F1;
- **C1:** the measured-weights share is printed, and graded only when switched on;
- **submit:** a step naming a path outside `$R/` refuses; so does a prefix collision (`$R-old/…`), and so does a step
  that names no path under `$R`;
- **ROOT (`RootPaths`, cluster only):**
  - the flux file round trip;
  - `loop_pots` reads the loop's parameters;
  - `run_flux` passes F1 and records the loops' POT and e;
  - `run_flux` fails when a loop's POT is not its flux file's.

**The suite as a whole covers:**
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
- **F1 and the flux:** the combiner's arithmetic; F1 in both directions (a 10⁻¹¹ defect fails in a period, in ALL,
  in either POT and in an edge; 5 × 10⁻¹³ passes; an error defect is printed, not graded); e is POT × flux;
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

**Disclosed in revision 2: the receipt's null is not exactly the readout's.** It resamples replica deviations scaled by
√(n/(n−1)), as the readout does. It does not add the independent Gaussian with T's MC variance that the readout's
noise adds (`make_noise`). Its docstring's "as fd_rpd.run_readout's noise does" overstates the match. The receipt is
kept as the director ruled on it; the term is measured below (the director's ask (1)).

**Pooled** (`fd/receipts-rpd/calibration_pooled.py` and `.log`, arithmetic on the log above):

| replicas | pooled α̂ | dispersion χ² (7 dof) | p |
|---:|---|---:|---:|
| 3 | 100/2400 = 0.0417 ± 0.0041 | 7.01 | 0.43 |
| 10 | 139/2400 = 0.0579 ± 0.0048 | 7.81 | 0.35 |
| 30 | 134/2400 = 0.0558 ± 0.0047 | 7.43 | 0.39 |

**The scatter across realizations is Monte Carlo error, not realization dependence.** The eight counts per row are
binomially dispersed about the pooled rate. Revision 1 said α̂ "varies by realization"; the χ² does not support that,
and this corrects it.

**At the 30-replica pooled rate 0.0558:**
- one 300-dataset α̂ exceeds the gate 0.06462 with probability 0.238, which is why two of eight did;
- one 2,000-dataset α̂, the readout's, exceeds it with probability 0.044 at each grid point.

That 0.044 is a floor, and it is correlated across the grid points, because they share one replica set.

**The director's ruling (2026-11-03, final at binding 2): part 1's rule stands unchanged.** It keeps 30 replicas, the
gate at 0.0646, and the readout at 2,000 datasets × 4 scales. There is no 10× synthetic run.

**An R2 INCONCLUSIVE on calibration is a legitimate, reported outcome.** Its risk is stated here, before anything runs:
about 4% per grid point at the measured pooled rate, as a floor.

**With T's MC-variance term (revision 3, the director's ask (1)).** `fd/receipts-rpd/calibration_tvar.py` and `.log`
rerun the same null with the Gaussian `make_noise` adds; `calibration_tvar_pooled.log` is `calibration_pooled.py` on it,
block by block (that script's output on `calibration_spread.log` is unchanged, byte for byte). T's MC sd has no
committed value, so it is bracketed at κ = 0.5, 1 and 2 times the replica sd, in two shapes: 1/√e (MC exposure
proportional to the data's) and flat (the median replica sd on every playlist). κ = 0 reproduces
`calibration_spread.log` exactly (asserted). Everything else is the receipt's: the metric, e, the seeds, 8 × 300.

| T's MC sd | pooled α̂ at 30 replicas | α̂ + 2σ at 3 / 10 / 30 | P(2,000-set α̂ > gate) |
|---|---|---|---:|
| none (the ruled receipt) | 134/2400 = 0.0558 ± 0.0047 | 0.0498 / 0.0675 / 0.0652 | 0.044 |
| 0.5 × 1/√e | 118/2400 = 0.0492 ± 0.0044 | 0.0489 / 0.0684 / 0.0580 | 0.001 |
| 1 × 1/√e | 125/2400 = 0.0521 ± 0.0045 | 0.0526 / 0.0648 / 0.0612 | 0.007 |
| 2 × 1/√e | 116/2400 = 0.0483 ± 0.0044 | 0.0539 / 0.0589 / 0.0571 | 0.001 |
| 0.5 × flat | 118/2400 = 0.0492 ± 0.0044 | 0.0471 / 0.0666 / 0.0580 | 0.001 |
| 1 × flat | 115/2400 = 0.0479 ± 0.0044 | 0.0462 / 0.0661 / 0.0566 | 0.000 |
| 2 × flat | 114/2400 = 0.0475 ± 0.0043 | 0.0453 / 0.0557 / 0.0562 | 0.000 |

- **No configuration puts the pooled α̂ + 2σ above 0.07.** The largest is 0.0684, at 10 replicas. At the readout's 30
  it is at most 0.0612 with the term, against 0.0652 without it.
- **The term does not raise α̂ in this bracket.** At 30 replicas every κ > 0 lies below the ruled 0.0558, by
  0.0037–0.0083 (0.8–1.8 of its σ, 0.0047). The rows share their replica sets and seeds, so they are correlated and
  not six independent confirmations.
- **So the ruled 4% floor stands as the conservative figure.** The rerun gives no reason to raise it.
- **Scope:** the synthetic metric and Gaussian replicas, as in the ruled receipt. κ is bracketed, not measured; the
  real T variance is computed from the npz only in the readout.

## 5. Mutation receipt

<!-- absence-ok: describes what tests assert (R1 NOT COMPUTED is a declared outcome), not a claim that a result does not exist -->
`fd/receipts-rpd/mutants_rpd.py`, 136 mutants across `fd_rpd_inputs.py`, `fd_rpd.py` and the rpd submit stages, run
against `test_fd_rpd` (each run stops at its first failure): **killed 136 of 136, none survived, none unapplied, files
restored** (`fd/receipts-rpd/mutants_rpd.log`, on revision 4's code `45b09d40` in a fresh clone; the log's first line
gives the three files' sha256 prefixes).

**Revision 1** had 67 mutants, killed 67 of 67 after a first pass left 7. The survivors were: S1 not shrunk; σ₀
centred on the replica mean; both stage D rules inverted; C1's exact-zero weights unchecked; R1's t̄ gate removed; and
the 5B block check removed. Tests were added for each.

**Revision 2.** The audit (M4) ran 37 more mutants and 28 survived. The list now includes every survivor it named
except the L-region edge (§9), plus mutants on the code added in answer to it.
- **The first full pass of 100** killed 94. The survivors were:
  - two inline seed offsets, stage D's OC table and the readout's;
  - the readout's guard built with no integrals;
  - `read_truth` accepting non-finite values;
  - F1 without the loops' POT check;
  - e from the flux files' POT.
- **Fixes:**
  - The four seed offsets are named constants (`SEED_OC`, `SEED_REACH`, `SEED_READOUT`, `SEED_N0_EFFECT`). They are
    pinned, and each reader's generators are checked against them while it runs.
  - The guard test plants X/f − 1, which only the integral list refuses.
  - `read_truth` is tested directly, on the variance as well.
  - The loops' POT decision moved into `flux_decision`, which needs no ROOT, and is tested locally.
- **Three mutants were added from the audit's list** after that pass:
  - stage D's inner datasets 200 → 20;
  - N0's seed offset;
  - N0's forced UNRESOLVED not passed to `classify`.

  The last survived, because the fixture's small playlists are UNRESOLVED on noise anyway. Its test now requires
  that exactly the three small playlists reach `classify` forced.
- With call-site mutants for each seed, that makes 106.

**Revision 3** adds 8, on the rulings' code and the director's ask (2): F1 ignoring the MC POT, the edges or the
contents; F1 grading the errors; the errors not printed; the L-region lower edge 1.0 (the audit's) and 2.0; H's upper
edge 20 (§9). The 8 were run first as a subset and all killed; the full 114 were then run on the final code.

**Revision 4** adds 22, on A1's code:
- `flux` without the environment check, or checking it after a staged read;
- in `mat_env_problems`, each clause removed: the setup digests, the MAT file digests, the symlink, the variables,
  MINERVA_PREFIX alone, the dictionary. Also the mapped-library comparison weakened to a subset, to a superset, or
  inverted (so the pinned environment would refuse), and mapped files outside MAT's lib counted;
- in `mat_environment`, the problems ignored, the exit code changed, and the dictionary assumed;
- the maps parser dropping paths with spaces, and the digests read without O_NOATIME;
- in `verify-staged`, each clause removed (the copy, the record's digest, the source path, the record's names) and
  mismatches passed.

A first subset run was stopped partway by the machine's memory reaper, with the 21st mutant still applied in the
working tree. That file was restored by hand and checked against the log's sha256 prefix (`200bc0ac…`). One survivor,
the digests read without O_NOATIME, got a test, and the remaining three were then killed in a scratch copy. The full 136
ran in a fresh clone.

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
- **e at stage S** uses each staged loop's data POT (`loop_pots`), as part 1 §5 says. `flux` requires it equal to the
  flux file's data POT to 10⁻¹² (`loops_data_pot_equal_flux_data_pot` in `F1.json`), so `loop_pots` first runs at
  stage S, not inside job A.
- **N0's small set** is the three smallest-share pseudo-playlists, as part 1 §4 defines it (`n0_small_set`). The reading
  prints whether all three are below 0.03, since part 1 §5 notes 1O's share is within 7% of that cut. The t₂₉
  thresholds hold because the set is always three.
- **N0's effect** (part 1 §4) re-runs R2's null with b̄ added to the three small playlists. It prints the null's median
  F and its share with p < 0.05, with and without b̄, beside the observed F and p (`n0_effect`, seed offset 4000).
- **Stage D's 2 h budget** runs from the start of the stage, not from the reachability loop.

**Deviation 1, ruled (a) by the director (2026-11-03, into binding 2): C1's `measured_weights` predicate is printed,
not graded.**
- Part 1 §4 says C1 "recomputes it from X's own arrays and requires equality to 10⁻¹² (self-consistency)". That is not
  achievable from the npz.
- The dump bins float64 coordinates (`nd-unfolding/nn_dump_inputs.py:75-82`, before `.astype(np.float32)` at `:84-86`) but stores
  them as float32, so a row on a bin edge can fall in another bin when recomputed.
- **Revision 1** graded the share of rows that agree to 10⁻¹² at ≥ 0.999 (`C1_MW_SHARE`). The director accepted that.
- **The audit (m1)** showed one crossing row changes the rule's target in two bins, so the share lost is
  (n_A + n_B)/N, not 1/N. Its toy put P(share < 0.999) at 0/20 for 5 × 10⁴ rows, 0/20 for 2.5 × 10⁵ (minimum
  0.99924) and 1/20 for 10⁶ (minimum 0.99874), a spurious stop before job B of order 0–5% per playlist. Measuring the
  share on the staged `lat_zero` first is barred: nothing runs before binding 2.
- **Revision 2** prints the share per playlist and does not grade it (`C1_MW_GRADED = False`). Config R does not read
  this key (part 1 §2), so no readout depends on it.
- **The ruling** keeps that: a declared deviation from part 1's "requires equality", since grading at 0.999 carries
  a measured 0–5% spurious-stop risk per playlist and nothing reads the key.

**Deviation 2, accepted by the director for printing: stage D's α̂ at 200 inner datasets.**
- Part 1 §5 says "S0's α̂ at 200 inner is printed beside it, descriptive". Running S0's four scales for every outer
  dataset would roughly triple stage D's login-node time, which part 1 bounds at 2 h.
- **The code** prints S0's α̂ at each scale, averaged over the **first 25 outer datasets per truth**
  (`STAGE_D_ALPHA_OUTER`, under `R2_reachability.alpha_at_inner_descriptive`). It is descriptive and enters no rule.
  Stage D's EC rule runs with the gate off, as part 1 §5 designs it.
- **The readout's calibration gate uses all 2,000 datasets** (`R2_GATE_N`; `run_readout` calls `r2.run` with the gate
  on). The director's acceptance requires this, and the 25-dataset limit applies only to stage D's print.

**Deviation 3, resolved by ruling 2 (a) (2026-11-03): F1 conforms to part 1.**
- Part 1 §4 F1 compares each combination with 5B's period flux and the production flux "bin by bin … with its POTs".
- Revision 2 also graded the bin errors to 10⁻¹². Revision 3's `f1_decide` grades contents, both POTs and the edges
  to 10⁻¹², and prints the errors' max_rel (`errors_max_rel_printed`) without grading it.
- Edges must agree for a bin-by-bin comparison to mean anything, and the director's ruling keeps them graded.

**Deviation 4, declared: the inputs driver's records do not pass the LeakGuard.**
- Part 1 says every output passes F0's `LeakGuard`. The readers' JSONs do. `fd_rpd_inputs.py`'s four records
  (`STAGED.json`, `F1.json`, each check receipt and each N0 receipt) are written directly.
- They hold digests, paths, POTs, the per-playlist flux bins and F1's deviations, exposure shares, row counts and
  atimes: no unfold-derived number.
- The MC-truth npz files under `$R` are unguarded, as in 5B.

**Stage S's stop and A1 (revision 4).**
- **The stop.** Stage S's first connect (script sha256 `3640f113…`, approved under binding 2) ran on login02 from
  18:57:05 to 19:06:22Z on 2026-11-03:
  - the deploy at M was clean, with 22 §7 blobs and 0 mismatches, and the three suites passed: "Ran 272 tests … OK";
  - `stage` returned rc 0: 79 copies at their pins, 6,709,613,302 bytes, `atime_unchanged_all` true;
  - `flux` returned rc 1 at `cf.read_playlist("1A")` → `fmc.Get("pTmu_reweightedflux_integrated")` on the staged copy,
    with `TypeError: 'PlotUtils' is not a known C++ class` after "no dictionary for class PlotUtils::MnvH1D". No F1
    was written, and the stop is final.
- **The cause** is part 2's. §2 gave `flux` root_6_28 by prefix, "as in 5B". But 5B's login steps imported no ROOT,
  and the five ROOT tests used TH1D fixtures, so nothing had read a MAT object in that environment.
- **5B's jobs ran without MAT.** All 12 job env logs under `$P/fd-ct-5b-20261030` (e.g.
  `lanes-inputs/logs/ct5b_a_lane1.env.log`) show both MAT sources of the deploy's `setup_salloc_env.sh` failing with
  "No such file or directory". Nothing 5B read needed MAT, so its steps passed in root_6_28 alone. Read 2026-11-03 with
  `dd iflag=noatime`.
- **The rulings (binding 2 A1, the director, 2026-11-03):**
  - `flux`, with its `loop_pots` in the same process, runs in the shared checkout's MAT environment, read-only, with
    TMPDIR re-exported to `$R/tmp`, under the run-time digest check of §1.4. The director's first reading, that
    `s5c_array.sh` provides MAT, rested on a false premise and was withdrawn after the measurement above;
  - **that environment is the shared checkout's mutable state, pinned by digest at run time, not by git**;
  - job A is unchanged (`s5c_array.sh`, root_6_28 alone);
  - each step's environment is pinned in §2, and its tests run in it;
  - `$R` is reused. "Must not exist" applies to stage S's first connect. Every later connect requires `$R` and stage's
    record, runs `verify-staged` before reading, and refuses on any mismatch. The next connect starts at `flux`, from
    a fresh clone at the new M in `$R/deploy-2`.

## 7. Pinned bytes

Git blob digests at commit `45b09d40` (revision 4's code commit; `fd_rpd_inputs.py` and `test_fd_rpd.py` changed
from revision 3, and `test_fd_rpd_mat.py` is new, so there are 23 rows). The deploy verifies each with
`git rev-parse <pin>:<path>`; the ones not written by part 2 are the bound tools it calls unchanged.

| path | blob |
|---|---|
| `nd-unfolding/fd_rpd_inputs.py` | `d33307076d4c1c0025dcd2cbada82aa697946afa` |
| `nd-unfolding/fd_rpd.py` | `fea4f5e49b06b926847a58c565e20e6b3fe245d4` |
| `nd-unfolding/submit_fd_ct.sh` | `031b1b62f46dcd4361e8b5a8547b63c9717e63ad` |
| `nd-unfolding/tests/test_fd_rpd.py` | `c840191b3946c33c9b63d4b0b8e2bfb03934c549` |
| `nd-unfolding/tests/test_fd_rpd_mat.py` | `a8a2508380835ea9e40f16eaca6759458b730aed` |
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

## 9. The audit's findings and their dispositions

The audit is `FD-RPD-PART2-AUDIT-SONNET-ANSWER.txt`, on revision 1 (sha256 `1555b653…`). Line numbers in it refer to
revision 1's code.

| finding | disposition |
|---|---|
| **M1** N0's effect is not part 1's | **Fixed to part 1's text** (§6, `n0_effect`); tested |
| **M2** five printed items absent | **Fixed.** The readout prints: the detectable bias in σ and in % of the real median \|g\| of the small set (`detectable_bias_pct_of_median_abs_g_small`, and in `n0_reading`); the null's F quantiles beside N0's F values (`F_null_quantiles_beside`; `R2.run` returns them); the OC table again at the readout's t̄ and σ(t̄) (`oc_at_readout_descriptive`); ρ_raw and ρ_deb with their replica-noise reference (`r3_numbers`). Each is asserted in `Readout`'s end-to-end test |
| **M3** no outside-path refusal | **Fixed.** Every absolute path token in a step must be `$R` or start with `$R/`; tested both ways, with the prefix collision |
| **M4** the mutation list is not representative | **Fixed.** The list grows from 67 to 106 in revision 2 and to 114 in revision 3, including every survivor the audit named; the L-region edge is added in revision 3 (below). The receipt is re-run on the final code (§5) |
| **M5** ROOT code never executed | **Tests added** (`RootPaths`), cluster-only. `loop_pots` now runs at stage S (§6). Revision 3: run on a login node in root_6_28 with the director's permission, none skipped (§3) |
| **m1** C1's 0.999 not derived | **Printed, not graded:** ruled (a) by the director (§6 deviation 1) |
| **m2** N0's set by e < 0.03 | **Fixed:** the three smallest, with "all below 0.03" printed (§6) |
| **m3** Q3 partial | **Fixed:** finite and > 0 on cells, L and H for every vector read: the 360 replicas, the seed-42 unfolds, the truths and N0's 120. `read_truth` refuses non-finite values |
| **m4** F1 stricter; e not from the loops | **e: fixed** (§6). **The errors:** printed, not graded (ruling 2 (a)); the edges stay graded (§6 deviation 3, resolved) |
| **m5** gates weaker than "this deploy's records" | **Fixed.** Gate a requires F1's PASS, stage 0's and stage D's code sha equal to this `fd_rpd.py`, and stage D's recorded F1 and stage 0 digests equal to the files on disk. Gate b adds F1's digest and each N0 receipt's digest |
| **m6** budget from the loop | **Fixed:** from the stage start |
| **m7** inputs driver unguarded | **Declared** (§6 deviation 4) |
| **m8** empty integral list in two guards | **Accepted as informational.** Stage D and the controls write no X-derived number |
| **n1** §2's test comment | **Fixed** |
| **n2** unreachable assertion | **Kept** as a guard |
| **n3** ν = 1.8250 against 1.824 | **Noted:** part 1's rounding |
| **n4** `$B` prefix | **Fixed** with M3 |
| **n5** `relatime` masks atime | **Noted.** `atime_unchanged` stays advisory; the O_NOATIME open is what part 1 requires |

**The L-region edge mutant** (1.5 → 1.0), the director's ask (2). `fd/receipts-rpd/lregion_edge.py` and `.log`:
- the fine p∥ grid's lowest edge is 1.5 (`s1.FINE["pz"]`), so no reporting fine cell has a lower edge in [1.0, 1.5);
- L's weights under the lower edge 1.0 are bitwise those under 1.5 (39,480 nonzero entries), and the definition and
  the grid are pinned, so the mutant is **equivalent in every number the readers compute**;
- it is **not equivalent in output:** the stage-0 record prints `regions`. The pin of `L_REGION` and `H_REGION`
  (`test_the_declared_sizes_and_seeds`) kills it there, and the region test alone does not (checked by applying it).

Two non-equivalent neighbours are also in the list: the lower edge 2.0 and H's upper edge 20 (the grid has an edge
at 20). Revision 2's region test asserted only that every weighted cell lies inside the edges, so the narrowed region
(2.0) passed it. It now asserts both directions, and kills both.

Nothing is submitted, deposited or tagged.
