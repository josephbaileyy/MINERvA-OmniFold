# REPORT: GENCMP amendment E, addendum E2 — C_model with CH shape ratios, and its effect on Stage G's χ² (2026-11-02)

**By** the limitation-resolver lane (Claude), for the director and for Joseph.

**Under** [`FD-GENCMP-AMENDMENT-E-BINDING.md`](FD-GENCMP-AMENDMENT-E-BINDING.md):
- addendum E2, bound in #675 at M″ = `885e366e`;
- addendum E2-A1, bound in #677 at M‴ = `372db765`.

**It reports:**
- [`FD-GENCMP-AMENDMENT-E-ADDENDUM-E2.md`](FD-GENCMP-AMENDMENT-E-ADDENDUM-E2.md);
- [`FD-GENCMP-AMENDMENT-E-ADDENDUM-E2-A1.md`](FD-GENCMP-AMENDMENT-E-ADDENDUM-E2-A1.md).

**MEASURES:**
- C_model's NuWro and GiBUU vertices rebuilt with CH shape ratios, and the change in Stage G's χ² for the four
  "CH, analysis definitions" predictions;
- the estimator-seed check the director added;
- the two sensitivity readouts of Joseph's decision #680 item 4 (§5): χ² with C_model removed and doubled, and the
  per-cell σ change from carbon to CH.

**CANNOT AUTHORIZE:**
- any change to the reported covariance. Joseph has ruled to keep C_model on carbon
  ([`DECISION-20261102-joseph-cmodel-keep-carbon-state-effect.md`](../../../DECISION-20261102-joseph-cmodel-keep-carbon-state-effect.md),
  #680);
- a reading, a paper edit or a claim. The paper's sentence goes through the paper lane's round, which the director
  reviews against that decision.

**NOT CITABLE FOR:**
- a new C_model;
- a validation of C_model's coverage;
- an unfold-to-unfold noise floor (§4).

**Records** are under `fd/gencmp-e2/`:
- `run1/`: the first run, which stopped;
- `rerun1/`: the E2-A1 rerun. It holds `chi2/e2.json`, `unfold/unfold.json`, logs, receipts, inventories, `sacct.txt`,
  `sens/` (§5) and `hpss/`.
- **Not in git: the four vertex configs** (`vertices/config_carbon.json` and `config_ch.json` of each run). They stay on
  pscratch and in the HPSS archive (§8).
  - The shared checker `verify_receipt_artifacts.py` gives a false MISSING for them. Each names RE-1's
    `k1_p5_rerun.npz` bare in a label, and the same receipt cites it by its full pscratch path.
  - `classify_bare` tests MISSING before BY-PATH, so the checker refuses the commit.
  - The director agreed to leave them out of git.

**Run directories:**
- `$R1` = `/pscratch/sd/j/josephrb/gencmp-e2-20261102/`;
- `$R2` = `/pscratch/sd/j/josephrb/gencmp-e2a1-20261102/`.

## 1. Outcome

**Every control passed in the rerun.** They are stage, V, R1 (with leg iii as E2-A1 words it), U, R2, B2, C0, C1, C2 and C3.

**The flag is exceeded.** The flag operand, the largest |Δ| of the with arm's total χ² over the four predictions, is
**5.560**: GENIE+MEC's total χ² goes from **229.09 to 223.53**. That is above the disclosed GiBUU rise of 2.3. Under binding
ruling 3 (the addendum-E2 section of the binding), the question of rebuilding the reported C_model on CH went to Joseph.
He has ruled to keep it on carbon and state the measured effect (#680; §6).

**Δ_max = 6.074,** largest for GENIE+MEC, shape-only, in the arm without C_PL. Every signed value is in §3.

**The seed check measured nothing.** Δ_noise is exactly 0, because the estimator does not depend on its seed (§4).

**The sensitivity readouts** (§5, computed after the run at 0 node-h):
- Removing C_model raises every corner χ². GiBUU's with-arm total rises most, from 47.78 to 166.83.
- Doubling C_model lowers every corner χ²; GENIE+MEC's with-arm total falls to 223.88.
- Moving C_model to CH shrinks its per-cell σ by at most 0.0168 of the cross-section, at R02. The whole with-arm matrix's
  largest per-cell σ change is a fall of 9.4%, also at R02.

## 2. The two runs and the stop

| run | from | what happened | node-h |
|---|---|---|---|
| first (`$R1`) | a fresh clone at M″ (4 blobs equal to the binding's; 19/19 tests; import closure OK) | **Ran:** stage (18 inputs, each its pinned bytes; atime moved on 0); V (both ways); R1 legs (i) (7 of 7 committed ratio files reproduced) and (ii). **Stopped** at R1 leg (iii): "CH GiBUU's ratio carries the p_par < 10 truth cut, as the committed one does: differs". The stop was final: no unfold ran | 0 |
| rerun (`$R2`) | a fresh clone at M‴ (4 blobs equal to the E2-A1 binding's; 26/26 tests in the run environment) | **Passed:** stage (18; atime moved on 0); V; R1 (13 of 13, the new leg iii included); the unfold job; then χ² | 0.2217 |

**The stop.** It was a defect in the control, not in the inputs:
- `pvl_ratios` writes a `truth_cut` only when p_∥ is not a reweight axis. L-5D-PV reweights in p_∥, so GiBUU's domain is the
  cell restriction `pz_max_cells` = 10.
- Every GiBUU file carries that field and no `truth_cut`: the committed file, the carbon rerun and the CH file.
- E2-A1 repaired the leg. Before the rerun, it swept every other E2 control against the real committed records
  (`receipts/x_e2a1_sweep.tsv`).

**The unfold job** (60680628, `rerun1/sacct.txt`):
- regular_1, one node, COMPLETED, exit 0, 13:18 elapsed: **0.2217 node-h** against the 0.5 cap;
- five steps of 42 CPUs, each with 92,682 MB, all started at 00:21:40 PST;
- step times 12:39 to 13:02, MaxRSS 16,185,872 to 16,712,756 KiB (15.4 to 15.9 GiB). The addendum's "17.26 GB" for J5
  was the same unit slip: sacct's 17,256,716 is KiB, which is 16.5 GiB;
- products as `unfold/unfold.json` records them.

**R2: PASS.** The seed-42 NuWro carbon rerun reproduces the committed `L-5D-PV_e_nuwro` product's `xsec_flat` bitwise.

**B2: PASS.**
- `check_meta` passed on all five products, with the seed-43 pair checked at seed 43.
- The pair's code is the rerun's, and so are its estimator parameters apart from `random_state`.
- The rerun's parameters are the committed vertex's, and its code differs from the vertex's only in `pvl_lib.py`.

**C1–C3: PASS** (`rerun1/logs/chi2.log`):
- C1: the carbon products give `cmodel_5d.json`'s S bitwise;
- C2: the C_model_abs reconstruction holds to 1e-12;
- C3: the carbon S reproduces E-1's χ² to 1e-10 for every prediction, arm and kind.

**The other cost:** the login steps, 0 node-h.

## 3. Every signed Δ and Δ_noise

Δ = χ²(S_CH) − χ²(S_carbon), and Δ_noise = χ²(S_carbon at seed 43) − χ²(S_carbon at seed 42).

**The two arms:**
- with: C_rest = C_e + C_resp + C_PL,5D, the reported covariance;
- nopl: C_e + C_resp.

g and V_g come from E-1's readouts. From `rerun1/chi2/e2.json` (sha256 `0aa73ebf…`):

| arm | kind | prediction | χ² carbon S | χ² CH S | Δ | Δ_noise |
|---|---|---|---|---|---|---|
| with | total | GENIE CV | 107.183 | 106.267 | −0.916 | 0 |
| with | total | GENIE+MEC | 229.094 | 223.533 | **−5.560** | 0 |
| with | total | NuWro | 127.692 | 127.860 | +0.169 | 0 |
| with | total | GiBUU | 47.779 | 45.098 | −2.681 | 0 |
| with | shape-only | GENIE CV | 102.115 | 101.577 | −0.537 | 0 |
| with | shape-only | GENIE+MEC | 228.999 | 223.334 | −5.665 | 0 |
| with | shape-only | NuWro | 107.524 | 108.068 | +0.544 | 0 |
| with | shape-only | GiBUU | 22.192 | 18.614 | −3.578 | 0 |
| nopl | total | GENIE CV | 111.218 | 110.395 | −0.822 | 0 |
| nopl | total | GENIE+MEC | 277.939 | 273.146 | −4.793 | 0 |
| nopl | total | NuWro | 180.616 | 183.196 | +2.580 | 0 |
| nopl | total | GiBUU | 61.406 | 57.725 | −3.681 | 0 |
| nopl | shape-only | GENIE CV | 110.320 | 109.683 | −0.637 | 0 |
| nopl | shape-only | GENIE+MEC | 263.745 | 257.671 | **−6.074** | 0 |
| nopl | shape-only | NuWro | 180.525 | 183.180 | +2.655 | 0 |
| nopl | shape-only | GiBUU | 24.660 | 20.612 | −4.048 | 0 |

**What moves.**
- Only the NuWro and GiBUU rows of S change. Their largest per-cell shift is 0.019 for NuWro and 0.017 for GiBUU.
- GENIE+MEC's row and the Tune v1 zero are unchanged.
- Every prediction's χ² moves anyway, GENIE+MEC's most, because C_model = SᵀS is one matrix shared by all of them.

## 4. The seed check, and what Δ is

**At the director's request**, E2 also unfolded the carbon NuWro and GiBUU vertices again at estimator seed 43, as a
noise floor (addendum E2 §3a).

**The seed-43 runs did use seed 43,** by their metadata:
- the unfold classifiers' `random_state` was 43;
- the refinement's was 46.

**Their `xsec_flat` is bitwise identical to the committed seed-42 products'** for both vertices. So S_carbon at seed 43
equals S_carbon, and every Δ_noise is exactly 0.

**The cause.** The estimator configuration is deterministic LightGBM with full binning and no bagging or feature
subsampling, so it does not depend on its seed. The seed check therefore measured nothing. The 0.22 node-h stands as
charged; the two seed-43 steps were part of it.

**What Δ is instead.** The carbon and CH vertices unfold the same data with the same deterministic estimator. Δ is
therefore not one draw of a noisy quantity. It is the exact effect, on this data, of changing the two vertices' target
from carbon to CH.
- It carries no unfold-to-unfold noise to compare against.
- The data's own statistical uncertainty on the vertex unfolds is not measured here. That would need resampling the
  inputs, which no addendum declared.
<!-- absence-ok: scoping statement about what E2's design measures (addendum E2 declares no input resampling), not a claim that a result does not exist -->

**The reading fixed in advance.** Addendum E2 §4, as amended, fixed this sentence: "changes the χ² by at most 6.07,
against a seed-to-seed change of 0.00". `within_seed_variation` is false. With Δ_noise ≡ 0, the clause "against a
seed-to-seed change of 0.00" states no floor. This report therefore does not offer that sentence as a reading. Which
sentence the paper carries, if any, waits for Joseph.

## 5. C_model removed and doubled, and per-cell σ (decision #680, item 4)

**What this is.** Joseph's decision asks for two readouts from existing products, and the director asked for them in this
report. No addendum declared them, so they are not a bound step. They use E2's bound functions, imported read-only from
`$R2/deploy` at M‴: `rest_matrices`, `e1_readout`, `chi2_rows`, `model_abs`, `c2_ok` and `c3_failures`.

**Where they ran:**
- on login37 in RE-1's environment (Python 3.11.14, numpy 1.26.4), at 0 node-h;
- from a script in `/dev/shm`, deleted after;
- reading the pinned committed inputs, and the run's own `e2.json` for S_CH (O_NOATIME, sha256 `0aa73ebf…` checked);
- writing nothing under `$R2`: a recursive listing's digest was equal before and after, and the deploy's porcelain stayed
  empty.

The script and its output are `rerun1/sens/x_e2_sens.py` and `x_e2_sens.out.txt`.

**How.**
- C_model removed: S = 0.
- C_model doubled: C_rest + C_model is passed as the rest, with the carbon S, so the matrix is C_rest + 2 C_model exactly.
- The reported matrix is C_model × 1 (carbon). The CH column repeats §3.

**Controls, 20, all PASS:**
- the carbon S is `cmodel_5d.json`'s, bitwise;
- C2;
- C3 for each arm;
- for each arm, prediction and kind, the carbon and CH χ² equal `e2.json`'s exactly.

**χ²** (`x_e2_sens.out.txt`):

| arm | kind | prediction | C_model × 0 | × 1 (reported) | × 2 | CH S |
|---|---|---|---|---|---|---|
| with | total | GENIE CV | 121.756 | 107.183 | 104.975 | 106.267 |
| with | total | GENIE+MEC | 261.545 | 229.094 | 223.881 | 223.533 |
| with | total | NuWro | 140.246 | 127.692 | 126.866 | 127.860 |
| with | total | GiBUU | 166.828 | 47.779 | 45.502 | 45.098 |
| with | shape-only | GENIE CV | 118.102 | 102.115 | 99.686 | 101.577 |
| with | shape-only | GENIE+MEC | 261.027 | 228.999 | 223.825 | 223.334 |
| with | shape-only | NuWro | 120.836 | 107.524 | 106.768 | 108.068 |
| with | shape-only | GiBUU | 139.763 | 22.192 | 18.999 | 18.614 |
| nopl | total | GENIE CV | 126.901 | 111.218 | 108.860 | 110.395 |
| nopl | total | GENIE+MEC | 316.625 | 277.939 | 271.626 | 273.146 |
| nopl | total | NuWro | 192.425 | 180.616 | 179.927 | 183.196 |
| nopl | total | GiBUU | 175.394 | 61.406 | 58.950 | 57.725 |
| nopl | shape-only | GENIE CV | 126.644 | 110.320 | 107.822 | 109.683 |
| nopl | shape-only | GENIE+MEC | 297.631 | 263.745 | 258.236 | 257.671 |
| nopl | shape-only | NuWro | 192.376 | 180.525 | 179.839 | 183.180 |
| nopl | shape-only | GiBUU | 143.868 | 24.660 | 21.199 | 20.612 |

What the table shows, without a reading:
- Every χ² falls as C_model grows from × 0 to × 2.
- GiBUU depends on C_model most: its with-arm total is 166.83 without it and 47.78 with it.
- In the with-arm total, the CH change is smaller than doubling's for GENIE CV (−0.92 against −2.21). It is slightly
  larger for GENIE+MEC (−5.56 against −5.21) and for GiBUU (−2.68 against −2.28). For NuWro the two have opposite signs
  (+0.17 against −0.83).

**Per-cell σ, carbon S against CH S** (16 cells, R00–R15; none has zero C_model σ):
- **C_model alone,** as σ/f (each cell's column norm of S):
  - the largest change is at R02, from 0.1136 to 0.0968 (−0.0168, −14.8%);
  - the largest relative change is at R12, where C_model is small: from 0.0051 to 0.0075 (+47.8%).
- **The whole matrix:**
  - with arm: the largest change is at R02, σ/f from 0.1405 to 0.1273 (−9.4%);
  - nopl: R02, from 0.1400 to 0.1268 (−9.5%).
  - With CH, the with-arm σ falls in 15 of the 16 cells and rises in R12 (+0.3%).

| cell | C_model σ/f, carbon | C_model σ/f, CH | with-arm σ, relative change |
|---|---|---|---|
| R00 | 0.0043 | 0.0040 | -0.0% |
| R01 | 0.0067 | 0.0051 | -0.2% |
| R02 | 0.1136 | 0.0968 | -9.4% |
| R03 | 0.0938 | 0.0798 | -7.8% |
| R04 | 0.0088 | 0.0081 | -0.3% |
| R05 | 0.0346 | 0.0305 | -2.1% |
| R06 | 0.0319 | 0.0283 | -2.6% |
| R07 | 0.0345 | 0.0214 | -5.3% |
| R08 | 0.0163 | 0.0151 | -0.5% |
| R09 | 0.0324 | 0.0309 | -1.0% |
| R10 | 0.0403 | 0.0347 | -2.8% |
| R11 | 0.1115 | 0.1034 | -4.6% |
| R12 | 0.0051 | 0.0075 | +0.3% |
| R13 | 0.0681 | 0.0651 | -1.6% |
| R14 | 0.0082 | 0.0061 | -0.5% |
| R15 | 0.0478 | 0.0349 | -8.1% |

## 6. What goes to whom

- **Joseph has ruled** (#680):
  - C_model stays on carbon;
  - #651 item 6's caveat becomes the measured, signed χ² change per prediction, quoted from `e2.json`, without the
    seed-variation clause;
  - GiBUU's "χ² rises with the CH correction" sentence is revised.
- **The paper lane's round** comes after this report and §5's readouts, reviewed by the director against the decision.
  This report makes no paper edit.

## 7. Limits

- **What E2 measures is C_model's dependence on the target only.** C_model's definitions stay the generators' own, while
  the corner's predictions use the analysis definitions.
- **C_model's positive control and closures are not redone,** so its coverage stays unvalidated, as before.
- **GiBUU's CH prediction carries its hydrogen sample's label.** Closure B3 failed on hydrogen, which enters with weight
  1/13.
- **No noise floor** (§4).

## 8. HPSS

**Not yet done: this section is filled before merge.** The archive is declared in addendum E2 §5. Its script is
`rerun1/receipts/x_e2_hpss.sh`, started on saul at 11:11:39 UTC on 2026-11-02. As of 16:05 UTC its first `hsi` call was
still waiting on HPSS's maintenance flag, so nothing had been written to HPSS.

**What the script does:**
- archives both run directories, without their deploy clones, to
  `/home/j/josephrb/mnv-gencmp-e2-20261102/gencmp-e2-20261102.tar`: 133 files from an explicit list, with htar's CRC and
  verify;
- runs `hsi hashcreate` and `hashverify`;
- retrieves five files and compares each one's sha256 with the original;
- records `hpssquota` before and after. Before, the quota stood at 449.25 of 512 GiB.

**Disclosed:** htar and the retrieval compare read the run directories' files without O_NOATIME. They are this run's
own outputs and staged copies, not the pinned originals.

Nothing is submitted, deposited or tagged.
