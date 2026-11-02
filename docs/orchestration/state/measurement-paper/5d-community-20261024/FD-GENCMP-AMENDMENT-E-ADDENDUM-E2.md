# ADDENDUM E2 to GENCMP amendment E: C_model with CH shape ratios, and its effect on Stage G's χ² (2026-11-02)

**By** the limitation-resolver lane (Claude), for the director to bind by addendum to
[`FD-GENCMP-AMENDMENT-E-BINDING.md`](FD-GENCMP-AMENDMENT-E-BINDING.md).

**Under:**
- that binding's ruling 4: E2's cap of 0.5 node-h is bound, and its code is bound by an addendum after its own audit.
  Once bound, E2 runs whatever E-1 shows. Its report goes to Joseph in every outcome. If C_model on CH would change the
  reported covariance's χ² by more than the disclosed GiBUU rise (2.3), the director also brings Joseph the question of
  rebuilding the reported C_model on CH. No covariance changes without him.
- [`FD-GENCMP-AMENDMENT-E-DECLARATION.md`](FD-GENCMP-AMENDMENT-E-DECLARATION.md) §6, which priced E2, and §8, which fixed
  its outcome rows;
- `DECISION-20261101-joseph-gencmp-paper-adoption.md` (#651) item 6's "one stated caveat": C_model's shape ratios are
  still from the carbon generators.

**After:** E-1's readouts (#662, `fd/gencmp-e/rerun1/chain/chdefs/`), which supply the four corner predictions' g and
V_g.

**MEASURES:** C_model's NuWro and GiBUU vertices rebuilt with CH shape ratios, and the resulting change in Stage G's χ²
for the four "CH, analysis definitions" predictions.

**CANNOT AUTHORIZE:**
- any change to the reported covariance;
- a reading, a paper edit or a claim.

**NOT CITABLE FOR:**
- a new C_model;
- a validation of C_model's coverage.

`$P` = `/pscratch/sd/j/josephrb`; `$R` = `$P/gencmp-e2-20261102/`, absent before the first step.

## 0. What changes, and what does not

**How a C_model vertex is built** (`pv-ladder/build_cmodel5d.py:5-10`, `pv-ladder/DECLARATION.md` D3). Each vertex
is a real-data unfold of configuration (e). Its prior is reweighted by the vertex prediction's gated shape ratio to
GENIE 2.12 CV (`pvl_ratios.py`). Then s_k = X_k/X_tune_v1 − 1 on the 16 cells, and C_model = SᵀS.

**What E2 changes: only the NuWro and GiBUU predictions,** from the carbon files (`475a2871…`, `48917692…`) to
GENCMP step A's CH combination in the generator definitions, x_CH = (12/13) x_C + (1/13) x_H. These are the committed
`phase1/mp3b/…/mp3b_fine_nuwro.npz` and `phase1/mp3c/…/mp3c_fine_gibuu_frozen.npz`, whose carbon arrays are those
files bitwise (control V).

**Unchanged, so that only the target moves:**
- the reference (GENIE CV);
- the definitions (the generator's own, as C_model's are);
- GiBUU's p_∥ < 10 GeV/c domain (the config's `pz_max`);
- the gate and normalisation;
- the estimator, seed and threads;
- the GENIE+MEC vertex, which is already CH;
- the Tune v1 zero.

## 1. Inputs

**`fd/gencmp-e2/INPUTS.sha256`,** 18 pinned pscratch files. The first 15 were all present by `stat` on 2026-11-01
UTC−8; the three ratio files added after the audit are pinned the same way. Each digest is copied from a committed
record:

| family | what | count | pin source |
|---|---|---|---|
| C | the L-5D-PV rung's npz, background and P5, the reference, and the GENIE+MEC, NuWro and GiBUU vertex files | 7 | `pv-ladder/config.json` |
| R | the committed prep's seven L-5D-PV ratio files (`tune_v1`; `genie_mec`, `nuwro` and `gibuu`, each with its `_sq` fallback) | 7 | `pv-ladder/prep-SHA256SUMS` |
| V | the vertex products C_model was built from: `L-5D-PV_e_{tune_v1, genie_mec, nuwro, gibuu}` | 4 | `build_cmodel5d.EXPECT` |

**Committed inputs, each checked against a sha256 in the code:**
- step A's two products (`63dbfa40…`, `f9244ebc…`, as `fd/gencmp/INPUTS.sha256:244-245` pins them; S1);
- `cmodel_5d.json`;
- the with-block data product and `cpl_block.npz`;
- E-1's two Stage G readouts.

## 2. The steps

| step | where | what | controls |
|---|---|---|---|
| stage | login node | O_NOATIME copies of the 15 inputs to `$R/inputs/` (`fd_gencmp_e.cmd_stage`) | each copy is its pinned bytes; atime is compared and recorded |
| vertices | login node | the CH vertex files in the gen5d form `pvl_ratios` reads (the carbon file's edges, step A's x_CH and sumw2_CH); `config_carbon.json` (the committed config, every pscratch path at its staged copy); and `config_ch.json` (the same, with the two vertices at the CH files) | **V:** step A's products are their pinned bytes; step A's carbon arrays are the staged carbon files bitwise; x_CH (with its sumw2) is `fd_gencmp.combine` of carbon and hydrogen bitwise. Receipt `V.ok` |
| ratios | login node (after `V.ok`) | `pvl_ratios` on `config_carbon.json`, then on `config_ch.json`, rung L-5D-PV | **R1:** (i) the carbon run reproduces all seven committed ratio files' numbers (r, k, to 1e-12 relative; only `source` and `reference` differ, naming the staged paths). That checks the whole ratio path, GiBUU's truth-cut path included (B3). (ii) The CH run's `tune_v1` and `genie_mec` files equal the carbon run's. (iii) CH GiBUU's ratio carries the committed p_∥ < 10 truth cut, and CH NuWro's carries none. Receipt `R1.ok` |
| unfold | one regular CPU job, `-t 00:25:00`, `--exclusive --no-requeue`, output to `$R/logs/` (`fd/gencmp-e2/receipts/x_e2_unfold.sh`; B6); it refuses without `R1.ok` | three `pvl_unfold` runs, launched as the PV ladder launched its own (`sbatch_pvl.sh:58-83`): one `srun` step each, of 42 CPUs and an equal share of 95% of the job's memory, through `mnv_guarded_run.py`, with `--estimator-seed 42 --threads 32 --iters 5`. They are NuWro CH, GiBUU CH and NuWro carbon with the committed prep ratio | **R2:** the NuWro carbon rerun reproduces the committed `L-5D-PV_e_nuwro` product's `xsec_flat` bitwise. **B2:** `pvl_analyze.check_meta` passes on all three products: rung, arm, mode, inputs, ratio digest, features, seed, iterations, threads, the refinement at R's settings, both prior guards. The two CH products match the rerun's code and estimator parameters. The rerun's estimator parameters equal the committed vertex's, and its code differs only in `pvl_lib.py`, where `a307faca..` appended `classify_cells` and changed no existing line. Receipt `U.ok` |
| chi2 | login node (after `V.ok`, `R1.ok`, `U.ok`) | S_CH from the CH products, with GENIE+MEC's row and the Tune v1 zero unchanged (`build_cmodel5d`'s own `integrals` and `pv2d_lib.rel_shift`). Then each corner prediction's total and shape-only χ² under C_rest + diag(f) S_CHᵀ S_CH diag(f), in both arms: with, C_rest = C_e + C_resp + C_PL,5D; nopl, C_e + C_resp. g and V_g come from E-1's readout | **C1:** the carbon products give `cmodel_5d.json`'s S bitwise. **C2:** diag(f) Sᵀ S diag(f) from that S is the data product's C_model_abs (to 1e-12 of its largest entry). **C3:** with the carbon S, every χ² equals E-1's (1e-10) |

Any failed control stops E2, and no E2 number is used. A step refuses unless the receipts of every control before it
exist (B1). The χ² readout, where Δ first appears, is written only after C1–C3 pass.

## 3. The readout

`chi2/e2.json` holds:
- S_carbon and S_CH;
- for each of the four predictions (GENIE CV, GENIE+MEC, NuWro and GiBUU; MnvTune v1 is the prior and is not compared,
  as E §8's "four corner predictions"), each arm and each kind: the χ² with carbon S, the χ² with S_CH, and
  **Δ = χ²_CH − χ²_carbon**, every signed value printed;
- **Δ_max = max |Δ|** over the four predictions, both arms and both kinds (E §8);
- **the flag (A1).** Binding ruling 4's operand is "the reported covariance's χ²", so the flag reads one quantity: the
  largest |Δ| of the with arm's total χ² over the four predictions. Its threshold is 2.3, the GiBUU rise #651 item 1
  disclosed ("+2.3, from 45 to 48"). No other arm, kind or reading triggers it. A4: for GENIE+MEC, whose χ² is near
  229, a shift of about 1% exceeds it, so the flag is not discriminating for large χ²; this is fixed now;
- the unfold record, with R2.

## 4. Outcomes (fixed before any number is read)

| outcome | what follows |
|---|---|
| every control passes | E §8's row "E2 runs" (bound with E, so this addendum adds no paper edit): #651 item 6's caveat is replaced by "Taking C_model's NuWro and GiBUU shape ratios from CH instead of carbon changes the χ² by Δ_max in one realisation (one pair of unfolds; no noise floor estimated)", with every signed Δ in the report (S4). The report goes to Joseph |
| as above, with the flag's operand above 2.3 | the same, and the director also brings Joseph the question of rebuilding the reported C_model on CH. No covariance changes without him |
| any control fails (V, R1, R2, B2, C1, C2, C3), or any other stop (a pin, a staged digest, a missing receipt, a job failure or timeout, a product missing) | no E2 number is used, and the caveat stays as #651 item 6 words it. The report names the check, and goes to Joseph. **A stop is final: no rerun, re-staging or repair without a new binding (A2)** |

## 5. Host, cost, reads and writes, HPSS

- **Host and environment.** The login steps run on a saul login node. Every step runs in the environment the PV
  ladder ran in (RE-1's `setup_salloc_env.sh`, Python 3.11), from a fresh clone of the bound commit with empty
  porcelain before and after.
- **The unfold job: ≤ 0.5 node-h,** the cap binding ruling 4 bound. The measured basis is PV-ladder job J5 (60206336):
  five such unfolds together on one node in 811 s, for 0.2253 node-h (`pv-ladder/LEDGER.tsv:8`). Three together take
  about the same wall, and the job asks `-t 00:25:00` (≤ 0.42 node-h).
- **Writes** go only under `$R`, and nothing to CFS.
- **Reads:** every pscratch input file is read O_NOATIME by the stage step, and every later step reads the copies.
  The exceptions are not inputs and are stated (B9): the environment's activation script
  (`$P/MINERvA-OmniFold/setup_salloc_env.sh`) and the installed software it loads, read normally as in every PV-ladder
  job; and the deploy clone, made by `git clone` under `$R`.
- **HPSS:** `$R`, without the deploy clone, goes to `/home/j/josephrb/mnv-gencmp-e2-20261102/` after `hpssquota`,
  with an explicit list, `hashverify` and retrieval.

## 6. The code bound (blob digests at this branch's head, recorded in the PR and the addendum binding)

| path | what |
|---|---|
| `nd-unfolding/fd_gencmp_e2.py` | new: `stage`, `vertices`, `ratios`, `unfold` (the post-run check), `chi2` |
| `nd-unfolding/tests/test_fd_gencmp_e2.py` | new, 13 tests |
| `fd/gencmp-e2/INPUTS.sha256` | new (§1) |
| `fd/gencmp-e2/receipts/x_e2_unfold.sh` | the unfold job |

**Unchanged and called:**
- `pv-ladder/pvl_ratios.py`, `pvl_unfold.py`, `build_cmodel5d.py` (`load_definition`, `integrals`, `VERTICES`,
  `EXPECT`) and `pv2d_lib.rel_shift`;
- `mnv_guarded_run.py`;
- `fd_g_compare.compare`, `fd_gencmp.combine` and `fd_gencmp_e.cmd_stage`.

**Tests:** run locally, `python3 -B -m pytest tests/test_fd_gencmp_e2.py` gives 13 passed. They cover:
- V both ways (a carbon entry; a CH entry);
- the config's repointing;
- R1's comparison (paths ignored, numbers seen);
- S against `build_cmodel5d.factor` on the real geometry;
- the χ² rows against `fd_g_compare.compare`;
- every committed pin (step A's included) and the inputs file's path coverage (its digests are copied from the
  records named in §1);
- the receipt gate both ways, and the four predictions' names.

The cluster steps' run-time controls (V, R1, R2, C1–C3) are their guard. There is no end-to-end test.

## 7. Limits

- **What E2 measures is C_model's dependence on the target only.** Its definitions stay the generator's own, as
  C_model's are. The corner's predictions use the analysis definitions.
- **The positive control and the closures are not redone.** C_model's coverage stays unvalidated, as before
  (`cmodel_5d.json` labels).
- **GiBUU's CH prediction** carries its hydrogen sample's label: closure B3 failed on hydrogen, which enters with
  weight 1/13.

## 8. Review

A fresh Sonnet subagent (not sol) audited the addendum and the code at head `6815238f`. Its prompt and answer are
verbatim beside this file (`FD-GENCMP-AMENDMENT-E-ADDENDUM-E2-REVIEW-PROMPT.txt`, `-ANSWER.txt`). It found nothing
that blocks binding on its own; every finding is fixed or answered:

<!-- absence-ok: each row quotes an audit finding about this branch's own code at head 6815238f, with what now covers it -->
| finding | what was done |
|---|---|
| A1, the flag's operand open | fixed: the with arm's total χ² of the four predictions, against #651 item 1's disclosed +2.3; no other reading triggers it (§3) |
| A2, no rule after a stop | added: any stop is final, with no rerun or repair without a new binding, and the stop row now lists every stop (§4) |
| A3, the four predictions unnamed | named, with MnvTune v1's exclusion stated (§3); `CORNER` in code |
| A4, the flag barely discriminates for large χ² | stated (§3); it is fixed in advance |
| B1 (near-blocking), the controls did not gate | V, R1 and R2+B2 write receipts; the job and each later step refuse without them; `e2.json` is written only after C1–C3 |
| B2, the CH products skipped `check_meta` | `pvl_analyze.check_meta` on all three products; the CH products against the rerun's code and parameters; the rerun against the committed vertex, differing only in `pvl_lib.py`'s appended function |
| B3, GiBUU's domain had no run-time control | R1 now re-derives all seven committed ratio files with the carbon config (GiBUU's truth-cut path included), and checks CH GiBUU's truth cut against the committed one |
| B4, untested commands | the receipt gate and the pins are tested; the commands' controls run at run time (§6) |
| B6, job output outside `$R`; missing `--exclusive`, `--no-requeue`, `HOME` | all added, with `-o` under `$R/logs/` |
| B9, non-O_NOATIME reads of the environment | stated as the exception (§5) |
| S1, step A's products not pinned in code | pinned (`STEP_A_SHA256`) and tested |
| S2, "every committed pin" overstated | reworded (§6) |
| S3, R1's "equal" | stated as 1e-12 relative (§2) |
| S4, Δ_max read as a bound | reworded: one realisation, no noise floor (§3, §4) |
| S5, the paper row and CANNOT AUTHORIZE | the row is marked as E §8's, bound with E (§4) |
| S6, the date | stated as 2026-11-01 UTC−8 (§1) |
| S7, the login steps' environment | E2's login steps run in RE-1's environment, as the PV ladder's prep did. The import closure is checked on the cluster before the first step, and a failure is a stop |

Nothing is submitted, deposited or tagged.
