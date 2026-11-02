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

**`fd/gencmp-e2/INPUTS.sha256`,** 15 pinned pscratch files, all present (`stat`, 2026-11-02). Each digest is copied
from a committed record:

| family | what | count | pin source |
|---|---|---|---|
| C | the L-5D-PV rung's npz, background and P5, the reference, and the GENIE+MEC, NuWro and GiBUU vertex files | 7 | `pv-ladder/config.json` |
| R | the committed prep's `tune_v1`, `genie_mec`, `genie_mec_sq` and `nuwro` ratio files | 4 | `pv-ladder/prep-SHA256SUMS` |
| V | the vertex products C_model was built from: `L-5D-PV_e_{tune_v1, genie_mec, nuwro, gibuu}` | 4 | `build_cmodel5d.EXPECT` |

**Committed inputs, each checked against a sha256 in the code:**
- step A's two products;
- `cmodel_5d.json`;
- the with-block data product and `cpl_block.npz`;
- E-1's two Stage G readouts.

## 2. The steps

| step | where | what | controls |
|---|---|---|---|
| stage | login node | O_NOATIME copies of the 15 inputs to `$R/inputs/` (`fd_gencmp_e.cmd_stage`) | each copy is its pinned bytes; atime is compared and recorded |
| vertices | login node | the CH vertex files in the gen5d form `pvl_ratios` reads (the carbon file's edges, step A's x_CH and sumw2_CH), and `config_ch.json`: the committed config with every pscratch path at its staged copy and the two vertices at the CH files | **V:** step A's carbon arrays are the staged carbon files bitwise, and x_CH (with its sumw2) is `fd_gencmp.combine` of carbon and hydrogen bitwise |
| ratios | login node | `pvl_ratios` on `config_ch.json`, rung L-5D-PV | **R1:** `tune_v1.json`, `genie_mec.json` and `genie_mec_sq.json` hold the committed prep's numbers (r, k), every number equal. Only `source` and `reference` differ: they name the staged paths |
| unfold | one regular CPU job, `-t 00:25:00` (`fd/gencmp-e2/receipts/x_e2_unfold.sh`) | three `pvl_unfold` runs, launched as the PV ladder launched its own (`sbatch_pvl.sh:58-83`): one `srun` step each, of 42 CPUs and an equal share of 95% of the job's memory, through `mnv_guarded_run.py`, with `--estimator-seed 42 --threads 32 --iters 5`. They are NuWro CH, GiBUU CH and NuWro carbon with the committed prep ratio | **R2:** the NuWro carbon rerun reproduces the committed `L-5D-PV_e_nuwro` product's `xsec_flat` bitwise |
| chi2 | login node | S_CH from the CH products, with GENIE+MEC's row and the Tune v1 zero unchanged (`build_cmodel5d`'s own `integrals` and `pv2d_lib.rel_shift`). Then each corner prediction's total and shape-only χ² under C_rest + diag(f) S_CHᵀ S_CH diag(f), in both arms: with, C_rest = C_e + C_resp + C_PL,5D; nopl, C_e + C_resp. g and V_g come from E-1's readout | **C1:** the carbon products give `cmodel_5d.json`'s S bitwise. **C2:** diag(f) Sᵀ S diag(f) from that S is the data product's C_model_abs (to 1e-12 of its largest entry). **C3:** with the carbon S, every χ² equals E-1's (1e-10) |

Any failed control stops E2, and no E2 number is used.

## 3. The readout

`chi2/e2.json` holds:
- S_carbon and S_CH;
- for each of the four predictions, each arm and each kind: the χ² with carbon S, the χ² with S_CH, and
  **Δ = χ²_CH − χ²_carbon**, every signed value printed;
- **Δ_max = max |Δ|** over the four predictions, both arms and both kinds (E §8);
- the flag Δ_max > 2.3 (binding ruling 4);
- the unfold record, with R2.

## 4. Outcomes (fixed before any number is read)

| outcome | what follows |
|---|---|
| every control passes | E §8's row "E2 runs": #651 item 6's caveat is replaced by "Taking C_model's NuWro and GiBUU shape ratios from CH instead of carbon changes the χ² by at most Δ_max", with every signed Δ in the report. The report goes to Joseph |
| as above, with Δ_max > 2.3 | the same, and the director also brings Joseph the question of rebuilding the reported C_model on CH. No covariance changes without him |
| any control fails (V, R1, R2, C1, C2, C3) | no E2 number is used, and the caveat stays as #651 item 6 words it. The report names the check, and goes to Joseph |

## 5. Host, cost, reads and writes, HPSS

- **Host and environment.** The login steps run on a saul login node. Every step runs in the environment the PV
  ladder ran in (RE-1's `setup_salloc_env.sh`, Python 3.11), from a fresh clone of the bound commit with empty
  porcelain before and after.
- **The unfold job: ≤ 0.5 node-h,** the cap binding ruling 4 bound. The measured basis is PV-ladder job J5 (60206336):
  five such unfolds together on one node in 811 s, for 0.2253 node-h (`pv-ladder/LEDGER.tsv:8`). Three together take
  about the same wall, and the job asks `-t 00:25:00` (≤ 0.42 node-h).
- **Writes** go only under `$R`, and nothing to CFS.
- **Reads:** every pscratch original is read O_NOATIME by the stage step. Every later step reads the copies.
- **HPSS:** `$R`, without the deploy clone, goes to `/home/j/josephrb/mnv-gencmp-e2-20261102/` after `hpssquota`,
  with an explicit list, `hashverify` and retrieval.

## 6. The code bound (blob digests at this branch's head, recorded in the PR and the addendum binding)

| path | what |
|---|---|
| `nd-unfolding/fd_gencmp_e2.py` | new: `stage`, `vertices`, `ratios`, `unfold` (the post-run check), `chi2` |
| `nd-unfolding/tests/test_fd_gencmp_e2.py` | new, 11 tests |
| `fd/gencmp-e2/INPUTS.sha256` | new (§1) |
| `fd/gencmp-e2/receipts/x_e2_unfold.sh` | the unfold job |

**Unchanged and called:**
- `pv-ladder/pvl_ratios.py`, `pvl_unfold.py`, `build_cmodel5d.py` (`load_definition`, `integrals`, `VERTICES`,
  `EXPECT`) and `pv2d_lib.rel_shift`;
- `mnv_guarded_run.py`;
- `fd_g_compare.compare`, `fd_gencmp.combine` and `fd_gencmp_e.cmd_stage`.

**Tests:** run locally, `python3 -B -m pytest tests/test_fd_gencmp_e2.py` gives 11 passed. They cover:
- V both ways (a carbon entry; a CH entry);
- the config's repointing;
- R1's comparison (paths ignored, numbers seen);
- S against `build_cmodel5d.factor` on the real geometry;
- the χ² rows against `fd_g_compare.compare`;
- every committed pin, and the inputs file's coverage.

The cluster steps' run-time controls (V, R1, R2, C1–C3) are their guard. There is no end-to-end test.

## 7. Limits

- **What E2 measures is C_model's dependence on the target only.** Its definitions stay the generator's own, as
  C_model's are. The corner's predictions use the analysis definitions.
- **The positive control and the closures are not redone.** C_model's coverage stays unvalidated, as before
  (`cmodel_5d.json` labels).
- **GiBUU's CH prediction** carries its hydrogen sample's label: closure B3 failed on hydrogen, which enters with
  weight 1/13.

## 8. Review

Recorded after the audit: `FD-GENCMP-AMENDMENT-E-ADDENDUM-E2-REVIEW-PROMPT.txt` and `-ANSWER.txt`, each finding with
its disposition.

Nothing is submitted, deposited or tagged.
