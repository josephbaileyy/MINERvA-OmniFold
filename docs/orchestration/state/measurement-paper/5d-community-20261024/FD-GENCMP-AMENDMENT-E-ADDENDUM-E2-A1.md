# ADDENDUM E2-A1 to GENCMP addendum E2: R1 leg (iii) reads the domain the producer writes on L-5D-PV, and every E2 control is swept on real records (2026-11-02)

**By** the limitation-resolver lane (Claude), for the director to bind by addendum to
[`FD-GENCMP-AMENDMENT-E-BINDING.md`](FD-GENCMP-AMENDMENT-E-BINDING.md) (addendum E2, bound in #675 at M″ = `885e366e`).

**Under:** the director's ruling of 2026-11-02 on E2's R1 stop. It chose option (a), this addendum, with four conditions,
each met in §5.

**MEASURES:** nothing new. This repairs a control that could not pass on correct inputs, and records the sweep the
ruling asked for.

**CANNOT AUTHORIZE:**
- any change to E2's design, its reading or its flag;
- a reading, a paper edit or a claim.

`$R1` = `/pscratch/sd/j/josephrb/gencmp-e2-20261102/` (the first run, kept as the record of the stop).
`$R2` = `/pscratch/sd/j/josephrb/gencmp-e2a1-20261102/` (the rerun; absent before its first step).

## 1. The stop

E2's first run (from `$R1/deploy` at M″) passed stage (18 inputs, atime moved on 0), V, and R1 legs (i) and (ii). It
then stopped at R1 leg (iii): "CH GiBUU's ratio carries the p_par < 10 truth cut, as the committed one does: differs".
Under binding ruling 2 the stop is final. No unfold was submitted, 0 node-h were spent, and no E2 number exists.

## 2. The defect

`pvl_ratios` writes a GiBUU `truth_cut` only when p_∥ is not one of the rung's reweight axes (`cut_as_truth`,
`pvl_ratios.py:119`, written at `:130-131`). L-5D-PV's axes are [pt, pz, eavail, q3, W]. There the domain is a cell
restriction (`region &= pz_hi <= pz_max`, `:124-125`), recorded as `pz_max_cells` (`:132-133`).

Leg (iii) checked the `truth_cut` branch, so it could not pass on correct inputs. The fields, by key presence:

| file | `truth_cut` | `pz_max_cells` |
|---|---|---|
| committed `gibuu.json` | absent | 10.0 |
| first run's carbon `gibuu.json` | absent | 10.0 |
| first run's CH `gibuu.json` | absent | 10.0 |
| first run's CH `nuwro.json` | absent | absent |

**The domain itself was already verified.** R1 leg (i) re-derived the committed carbon `gibuu.json`, `pz_max_cells`
included, field by field.

## 3. The change

- **Leg (iii)** (`fd_gencmp_e2.domain_failures`): CH GiBUU carries `pz_max_cells` = 10.0 and no `truth_cut`, as the
  committed GiBUU ratio does; CH NuWro carries neither. `GIBUU_TRUTH_CUT` becomes `GIBUU_PZ_MAX_CELLS` = 10.0, citing
  the branch that runs.
- **Named helpers, so the sweep and the tests call the run's own comparisons:**
  - `c1_ok`, `c2_ok` and `c3_failures`;
  - `code_differ` (B2);
  - `rest_matrices` and `e1_readout` (the C0 pins).

  Each is the expression `cmd_chi2` or `provenance` used, unchanged. C3 now reports once per arm, listing any failing
  prediction and kind.

**Unchanged:** every other control, its tolerance, the job, `INPUTS.sha256`, the reading and the flag.

## 4. The sweep (the director's condition 2)

`fd/gencmp-e2/receipts/x_e2a1_sweep.tsv` lists each control with its real source, its result on the real record and where
that is shown. The probes and their outputs are in `fd/gencmp-e2/receipts/sweep-a1/`.

**How the probes ran:**
- on login37, in RE-1's environment (Python 3.11.14, numpy 1.26.4, lightgbm 4.6.0);
- from `$R1/deploy` at M″, whose code for these controls is this addendum's apart from leg (iii) and the naming;
- reading the first run's staged copies O_NOATIME, after their pins matched;
- writing only `/dev/shm` scripts, deleted after each run.

**In summary:**
- **On real data:**
  - stage, V, and R1 (i) and (ii) passed in the first run;
  - the new leg (iii) passes on the committed fields and on the first run's CH files;
  - B2 passes:
    - `check_meta` on all four committed vertex metas at seed 42;
    - at seed 43, it refuses the committed meta and accepts its seed-43 form (estimator `random_state` 43, refinement
      46);
    - the committed refinement's `random_state` is 45, confirming seed + 3;
    - a rerun's code record at M″ would differ from the committed vertex's only in `pvl_lib.py` (versions equal);
  - C1 passes on the four committed products;
  - C2 passes;
  - C3 passes in the run environment, with a largest relative difference of 5.2e-15 over 16 values.
- **The probe's own error.** My first B2 code probe left out `s5e_candidate.install("R")`, which pvl_unfold calls for
  arm (e) before it records the code (`pvl_unfold.py:156-160`). It reported four extra differing keys. With the call
  included (probe 2), only `pvl_lib.py` differs.
- **Platform finding (C3).** On macOS numpy, the shape-only χ² (matrix + 100 f fᵀ) of the committed inputs differs from
  E-1's by up to 1.7e-10, beyond C3's 1e-10. Summation order and the C_model_abs source each move it by exactly 0
  (measured), so the difference comes from the platform. In the run environment, where E-1's readouts were made, every
  shape-only value agrees exactly. C3's tolerance is unchanged. The local test asserts C3 exactly only in the run
  environment (Linux, numpy 1.26.4); elsewhere it allows shape-only differences only.
- **Not testable before the run:**
  - **R2's rerun side.** Its operand is checked: float64, 65,856 cells. A failure stops the run at R2, finally.
  - **The job itself.** A failed step leaves a product missing, and `unfold` stops at "all 5 products exist", finally.
  - **The products-as-recorded C0 checks.**

**The tests.** `tests/test_fd_gencmp_e2.py` class `RealFormat` has 7 tests on fixtures copied from these records
(`tests/fixtures/e2a1_real/PROVENANCE.tsv`). The file gives 26 passed locally. `x_e2a1_mutants.tsv` records:
- the control row passing;
- seven field mutants of leg (iii), each failing;
- five code mutants of the new helpers, each caught.

## 5. The director's conditions

| # | condition | where it is met |
|---|---|---|
| 1 | leg (iii) as worded; both ways on a fixture from the committed `gibuu.json`'s {axes, truth_cut, pz_max_cells}; mutants in a receipt | §3; `RealFormat`; `x_e2a1_mutants.tsv` |
| 2 | sweep R2, B2 (seed 42 and 43), C1–C3 on the real committed formats; tabulate; name what cannot be tested and how its failure shows | §4; `x_e2a1_sweep.tsv` |
| 3 | rerun from a fresh clone at this addendum's merge commit into a fresh run directory, from stage onward; `$R1` stays; cost unchanged | §6 |
| 4 | the report to Joseph gives both runs and this stop | the E2 report |

## 6. How it runs

Everything runs as addendum E2 declares (its §2 and §5), with two differences:
- `$R2` replaces `$R`;
- `$R2/deploy` is a fresh clone at this addendum's merge commit M‴.

The order is stage, V, R1 (with the new leg iii), the unfold job (five steps, `-t 00:25:00`, ≤ 0.5 node-h) with R2 and
B2, then χ² after C1–C3. Any stop is final. `$R1` is not touched.

**The job script.** `x_e2_unfold.sh` names the run directory literally in `R=` and in `#SBATCH -o` (an `#SBATCH`
line cannot expand a variable). Both named `$R1`; both now name `$R2`. That is the script's only change, and it stays
bound by blob.

## 7. The code (blob digests at this branch's head, recorded in the PR and the addendum binding)

| path | what |
|---|---|
| `nd-unfolding/fd_gencmp_e2.py` | leg (iii) (`domain_failures`, `GIBUU_PZ_MAX_CELLS`); the named helpers |
| `nd-unfolding/tests/test_fd_gencmp_e2.py` | adds `RealFormat`, `DOMAIN_MUTANTS` and `RUN_ENV` |
| `nd-unfolding/tests/fixtures/e2a1_real/` | three JSON fixtures and `PROVENANCE.tsv` |
| `fd/gencmp-e2/receipts/x_e2_unfold.sh` | `R=` and `#SBATCH -o` name `$R2` |
| `fd/gencmp-e2/receipts/x_e2a1_sweep.tsv`, `x_e2a1_mutants.tsv`, `sweep-a1/` | the sweep, the mutants, the probes and their outputs |

`fd/gencmp-e2/INPUTS.sha256` is unchanged.

**Review:** the director reviews the diff (ruling of 2026-11-02). There is no Sonnet audit.

Nothing is submitted, deposited or tagged.
