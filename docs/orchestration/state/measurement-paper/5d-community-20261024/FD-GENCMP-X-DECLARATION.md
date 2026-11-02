# DECLARATION GENCMP X: the covariance between the sixteen-cell result and the 2D result per (p_T, p_∥) quadrant, and the quadrant test it makes possible (2026-11-02)

**By** the limitation-resolver lane (Claude), for the director to bind.

**Under:**
- [`DECISION-20261101-joseph-gencmp-paper-adoption.md`](../../../DECISION-20261101-joseph-gencmp-paper-adoption.md)
  (#651) item 5: the 2D quadrant sentence (`paper_body.tex:119`) stays until this is resolved. The quadrant wording
  goes back to Joseph with the result.
- `DECISION-20261101-joseph-reopen-1b-and-compute-for-limitations.md` item 2, with the director's reading in
  `FD-GENCMP-BINDING.md`: CPU only, jobs under 12 h, regular QOS, nothing written to CFS.
- The scoping, [`FD-GENCMP-XCOV-SCOPING.md`](FD-GENCMP-XCOV-SCOPING.md) (#653, merged at `e9505ef4`).
- Amendment E, [`FD-GENCMP-AMENDMENT-E-DECLARATION.md`](FD-GENCMP-AMENDMENT-E-DECLARATION.md) (#657, merged at M =
  `6cd095d6`), with its binding (#658, #661) and its report (#662, `a4cd6ffc`). **E is merged first, as the director's
  split ruling requires.**
  - X cites E's `fd/gencmp-e/INPUTS.sha256` at M and does not re-pin `E_R`.
  - The code refuses unless that file is the bytes merged at M (sha256 `a5f8e3ae…`).
  - The sixteen-cell and `E_R` quadrant sums are read from step C-R's committed readout,
    `fd/gencmp-e/c-r/overlap_refined.json`.

**The director's rulings on the scoping (#653 §9), 2026-11-01, by message, applied here:**
1. **Route B.** Route A's V0, V1 and K come first.
   - If J or V0 fails, the statistical stream falls back to route A's r ∈ [0, 1] bound, at no route-B cost, and the
     readout says so.
   - A band that fails V1 joins the bounded set.
2. **C₂D = `Q_R` + C_model,2D, vertex-paired, as primary.** `Q_R` alone is printed beside it, labelled.
3. **The joint χ²₄ rule.** "Agree" requires the joint χ²₄ of the four d, under their full 4×4 σ_d covariance, to have
   p ≥ 0.05, and every quadrant to have |z| ≤ 2.50.
   - A quadrant with |z| > 2.50 is a "differ", and is named. So is a joint p < 0.05 with no single quadrant over.
   - Every "differ" goes to the director and Joseph before any text.
   - The readout prints the per-quadrant z, the 2×2 ρ_q, and each block's share of σ_d².
   - Under the route-A fallback, the rule is evaluated at r = 0 and r = 1 with the three-way reading, and r* is printed
     where it applies.
4. **The C_PL pair is constructed, as primary.** z with the pair set to 0 is printed as a labelled sensitivity.

**Declares:**
- V0, row order, the joins and the draw check;
- V1, weight equivalence;
- BOOT, the paired 5D replicas, with control B0;
- K, the cross blocks and the rule;
- the inputs (`fd/xcov/INPUTS.sha256`, beside E's);
- the controls, price and stops;
- the paper text for every outcome.

**MEASURES:** the covariance between the two results' quadrant sums, and the test of §4.

**CANNOT AUTHORIZE:**
- any paper edit or claim;
- any change to either result's reported covariance.

**NOT CITABLE FOR:**
- a validation of either covariance;
- a generator exclusion;
- the estimators' unfolding bias, which neither covariance prices.

`$P` = `/pscratch/sd/j/josephrb`. `$R` = `$P/gencmp-x-20261102/`, absent before the first step. `FD` =
`docs/orchestration/state/measurement-paper/5d-community-20261024`.

## 0. The test in brief

**The question.** For each quadrant q (QA–QD, `fd_gencmp.QUADRANTS`):
- d_q = S₁₆,q − S₂D,q;
- S₁₆ is the sum of the reported cells, plus QA/QB's unreported boxes at P5's value;
- S₂D is `E_R` integrated over the quadrant's 2D bins.

Both sums are C-R's, and K checks them to 1e-12.

**The covariance:** V_d = C₁₆ + C₂D − K − Kᵀ.
- C₁₆ is the reported matrix C_total + C_resp + C_PL,5D, plus the boxes' ±100% variance.
- C₂D is `Q_R` + C_model,2D.
- K is the cross covariance of the two results' quadrant sums. It is formed from every pairing the two
  constructions share (§3).

**What the scoping found** (each fact is cited there):
- the 175 universes and 5 laterals pair by name and index;
- the flux, constraint, X01, lateral and normalization inputs are identical;
- C_PL pairs by period, and C_model by vertex;
- the statistical replicas do not pair by seed. Route B makes 100 new 5D replicas whose draws are RE-2's replica
  draws, carried to the same events.

## 1. Inputs

**E's inputs file.** `fd/gencmp-e/INPUTS.sha256`, as merged at M (sha256 `a5f8e3aee79a250f…`, checked in code), pins:
- S1's assembly;
- `Q_R` (`b57d6c96…`), `E_R` (`a5c13fc3…`) and `C_PL_R` (`dbb067aa…`);
- the flux constraint file.

**X's own inputs file,** `fd/xcov/INPUTS.sha256`, 392 pins, every digest copied from a committed record (the file's
header names each record). `stat` on 2026-11-02 found all present. The families:

| family | what | count |
|---|---|---|
| O | RE-2's CV omnifile, on CFS (`re2_env.sh:9-10`; `43f8cc16…`). Part B's pscratch stage of it was removed (`partb/deletions.tsv:2`, same digest). Also the 2D universe omnifile (`220c479e…`) | 2 |
| I | `of_inputs_5d.npz` (`07fccc1a…`), `bkg_dump.npz` (`2addac8f…`) | 2 |
| S | S5_R `production_cov.npz` (`631cf255…`, which holds each 2D band's block), the X01 factors (`8912376e…`), the detector-dump receipt (`c52dca58…`) | 3 |
| U | RE-2's 175 universe products, 10 lateral products, replicas 1–100, and those replicas' logs (`re2/run/hpss/members.sha256`) | 385 |

**Committed inputs, each read with its committed digest:**
- S1's universe and lateral products, `s1/readout/s1_assembly/`. Each is pinned by the S1 readout's
  `meta.inputs_sha256`.
- S1's `data_b1_j101.npz`, B0's reference.
- C-R's readout, the with-block `cpl_block.npz` and data product.
- `cmodel_5d.json` and `2d-unfolding/pv2d/cmodel/cmodel_2d.json`.
- `fd_ct_5b_periods.json` and RE-2's `playlist_term.json`.

**V1's 5D weight files.** These are the files each S1 universe product read. They are named by that product's committed
metadata (`bank_weight_sha256`) and resolved through the sf1 manifest and the detector-dump receipt.

## 2. The steps

### 2.1 V0: row order, the joins and the draw check

`fd_xcov.py v0` runs on a login node, in omnifold_py310.

**What it reads and stages:**
- It stages O_NOATIME copies of the two 5D inputs to `$R/inputs/`, which BOOT reads.
- It reads the CV omnifile's `data`, `mc_signal_reco` and `mc_background` trees.

**What it checks:**
- **Counts.** The 2D side must have 4,091,707 data rows after `re2_driver.fill_data_reco_2d`'s mask (`fd_xcov.mask_2d_data`),
  658,227 background entries and 32,849,103 MC rows. The 5D side must have 4,091,579 observed rows and 621,445 template
  rows in `s5n_pseudo.fid_mask`'s window, and 32,849,103 MC rows. A different count fails V0.
- **MC rows.** (MC, MC_pz) must equal MCgen columns 0–1 as float32, row by row, except exactly 2,801 sentinel rows
  (`s5p_universe.py:72-75`). The w_truth ratio is recorded as a diagnostic.
- **Data join J.** Each 5D observed row is mapped to a 2D data row by ordered subsequence on (p_T, p_∥) as float32
  (`fd_xcov.subsequence_join`).
  - The map must be complete, order-preserving and injective.
  - Ambiguous rows are counted and printed. The greedy earliest match is used for them.
  - Each unmatched 2D row is classed: on the 5D window's upper p_T or p_∥ edge (the half-open bound), or excluded by
    the 5D window's other axes.
- **Background join.** The same, from each 5D template row to its `mc_background` entry.
- **The draw check.** For b = 1–100, the regenerated data, MC and background draw sums of RE-2's replica b
  (`fd_xcov.draw_sums_line`, in re2_driver's own print format) must all stand in that replica's log.

**V0 passes** iff the counts, the MC rows, both joins and all 100 draw checks hold. It then writes `v0/maps.npz`.
Otherwise the route is A (ruling 1).

### 2.2 V1: weight equivalence

`fd_xcov.py v1` runs as one regular CPU job, in omnifold_py310: a probe first, then the full run.

**Before any comparison:**
- The universe omnifile's digest is streamed through O_NOATIME and checked.
- Its `mc_signal_reco` rows are checked against the npz as in V0.

**The comparison.** For each of the 175 universes, take both sides' universe-to-CV ratios on the same rows: the 2D
side's `w_truth_<B>_<i>/w_truth` and `w_reco_<B>_<i>/w_reco`, and the 5D side's `wt/w_truth` and `wr/w_reco`. Their
quotient, row by row on rows with non-zero CV weights (sentinel rows excepted), must be one constant to 1e-6 relative.
- The constant is the POT scale, recorded, and its spread over the universes is printed.
- Non-finite quotients fail.

**A band passes** only if all its universes pass. A band that fails joins the bounded set (ruling 1).

**What V1 does not compare,** stated here: the truth-denominator weights (tdw, or the detector dump's `denom_nd`) and
the background weights (bkgw). They use the same per-event universe weights on other trees. A band whose signal-row
weights match but whose denominator or background implementation differs would therefore pass V1. §8 carries this.

**The probe** (cap 0.25 node-h, `-t 00:15:00`) runs MaRES's two universes and Flux 0–9, and prints the projected time
for 175. The full run is submitted only if the projection is within its cap (1.75 node-h, `-t 01:45:00`).

### 2.3 BOOT: the paired 5D replicas

`fd_xcov.py boot` runs as one regular CPU job, `-t 03:00:00`, in root_6_28, with eight lanes of 32 threads as S1's seed
job packed them.

**How each lane runs.**
- Each lane runs `s5p_numerics.main` exactly as S1's statistical replicas ran: `--config R --construction data --pairs
  b:100+b --estimator-seed 42 --threads 32`, on the staged copies.
- Only one thing changes: `s5n_pseudo.bootstrap_replica` is replaced by `fd_xcov.make_mapped_replica`.
  `s5p_numerics.py:200` resolves it at call time, and neither `s5e_candidate.install` nor `s5p_truths.install`
  touches it.

**Replica b's draws** are RE-2's replica-b draws:
- **data:** `default_rng(b)`, carried to each 5D observed row through J;
- **MC:** `default_rng(b + 10,000,000)`, by position;
- **background:** `default_rng(b + 20,000,000)`, through the background map.

The jitter seed is 100 + b, as in S1.

**Control B0** (lane 1, first): the unreplaced function at b = 1 must reproduce S1's committed `data_b1_j101.npz`
`xsec_flat` bitwise. Unit tests also show that the replacement given s5n_pseudo's own draws is s5n_pseudo's replica
bitwise (`test_native_draws_reproduce_s5n_pseudo_bitwise`).

**Lanes:** native b = 1 and then 1–13; then 14–26, 27–39, 40–52, 53–64, 65–76, 77–88 and 89–100. Each lane writes a
JSON of its products' digests.

**When BOOT runs.** Only after V0 passes. If V0 fails, BOOT is not submitted.

### 2.4 K: the cross blocks and the rule

`fd_xcov.py k` runs on a login node, in omnifold_py310.

**K0** (structural). The quadrant cells must be the definition's. C_model,2D's cells must be `Q_R`'s, and the vertex
order the same on both sides. C-R's S₂D must equal B x, and its S₁₆ must equal A f plus the boxes, both to 1e-12.

**K1** (each pairing's inputs reproduce each side's own block, to 1e-10). For every band, every lateral, the
normalization, C_PL and C_model:
- the products K uses give the stated block: on the 5D side S1's `C_band_<b>`, `C_lat_<b>` and `C_normalization`, the
  block's `C_PL5D` and the data product's `C_model_abs`; on the 2D side S5_R's `band_<b>` and `band___Normalization_flat`,
  and `C_PL_R`;
- **so each cross block is built from exactly the products inside both stated covariances.** A failure stops K.

**The statistical stream.** Route B holds iff V0 passed, B0 passed, and all 100 paired products exist with their
recorded digests. Otherwise the route is A.

## 3. The cross blocks

All are formed at quadrant level: A (4×16) holds the reported cells, and B (4×205) the 2D bins with their areas.

| block | rule | source |
|---|---|---|
| each of the 38 bands (175 universes) | K_b = Σ_u w_u (X₁₆,u − X̄₁₆)(X₂D,u − X̄₂D)ᵀ / Σ w. This is each side's own rule (`s1_assemble.mat_cov`, `build_repair.wcov`): Flux weighted by the constraint weights and centred on the weighted mean, every other band unweighted (`fd_xcov.cross_cov`) | X₁₆,u = A U x_u (S1's committed products); X₂D,u = B vec(`U_<b>_<u>`) |
| each of the 5 laterals | the same rule on the two endpoints. `Muon_Energy_MINOS` is rescaled on both sides by the same X01 factors, per p_T (`s1_assemble.x01_scale`) | S1's `lat_*`; RE-2's `S3_*` |
| normalization | (0.014 A f)(0.014 B x)ᵀ, the same rank-1 rule on both sides | f; x = `E_R` |
| C_PL (constructed; ruling 4) | Σ_X v₁₆,X v₂D,Xᵀ, with v₁₆,X = √(k₁₆ e₁₆,X) A(f∘g₁₆,X) and v₂D,X = √k₂D B(√e₂D,X ∘ x ∘ g₂D,X), over PA, PB, PC | `fd_ct_5b_periods.json`; `playlist_term.npz`/`.json` |
| C_model (vertex-paired; ruling 2) | Σ_k (A(f∘s₁₆,k))(B(x∘s₂D,k))ᵀ over GENIE+MEC, NuWro, GiBUU | `cmodel_5d.json`; `cmodel_2d.json` |
| statistical, route B | K_stat = R ⊙ (σ₁₆ σ₂Dᵀ). R is the 4×4 sample correlation of the 100 paired replicas' quadrant sums, and σ is each side's stated statistical σ (S1's `C_stat`, S5_R's `stat`). The diagonal ρ's jackknife SE is printed | BOOT; RE-2's replicas 1–100 |
| statistical, route A, and any band failing V1 | r·M, with M = S₁₆^½ S₂D^½ for each such block. This keeps the joint matrix PSD for every r ∈ [0, 1] (`fd_xcov.bound_matrix`) | each side's stated block |
| no partner | C_resp, the unreported boxes, and 2D's C08_R enter V_d in full. The 5D seed block is exactly 0 | — |

**The joint matrix is PSD by construction** for every block formed as paired outer products: the universes, laterals,
normalization, C_PL and C_model. Route B's statistical block is not, because its σ come from different replicas than R.
V_d must be positive definite, or K stops and reports.

## 4. The rule (ruling 3), fixed now

**The primary reading:** C₂D = `Q_R` + C_model,2D, the C_PL pair constructed, and route B.
- z_q = d_q/√V_d,qq, and χ²₄ = dᵀ V_d⁻¹ d, with p = e^(−χ²/2)(1 + χ²/2) (exact for 4 degrees of freedom).
- **"agree"** iff p ≥ 0.05 and every |z_q| ≤ 2.50.
- **"differ"** otherwise:
  - each quadrant with |z| > 2.50 is named;
  - a joint p < 0.05 with no quadrant over is named "joint".

**Route A, or bands bounded.** Evaluate at r = 0 and r = 1. If the two readings agree, that is the reading. Otherwise
the reading is "⟨reading at r = 0⟩ only if r < r*", with r* the first point of a 10,001-point grid on [0, 1] where the
reading changes.

**Always printed:**
- d, S₁₆ and S₂D;
- z, χ²₄ and p;
- the 2×2 ρ_q = K_qq/√(C₁₆,qq C₂D,qq);
- each block's share of σ_d²: own blocks add, and a cross block subtracts twice its diagonal;
- every cross block;
- R and its jackknife SE;
- the variant against `Q_R` alone (C_model,16 unpaired), labelled "printed";
- the sensitivity with the C_PL pair set to 0, labelled.

**No outcome is read from the variant or the sensitivity.** No tolerance or threshold here is relaxed after a run. A
change needs a new declaration and binding.

## 5. Outcomes, and what the paper says in each (fixed before any number is read)

`paper_body.tex:119`'s first sentence stays until Joseph rules (#651 item 5). Every outcome goes to Joseph with C-R's
numbers (#662 §3.2, including QA's changed reading). The wording below is the minimum, and Joseph approves the final
text.

<!-- absence-ok: proposed paper text per outcome, fixed before any number is read; 'not measured' describes the route-A fallback's design -->
| outcome | the paper (minimum) |
|---|---|
| agree (route B) | "Summed over each of the four (p_T, p_∥) quadrants, the sixteen-cell result agrees with the two-dimensional result: their four differences give χ² = … for four degrees of freedom (p = …), and none exceeds 2.5 standard deviations of its difference. The covariance between the two results is computed from the systematic universes, lateral shifts, run-period offsets, generator vertices and paired bootstrap replicas they share." |
| agree (route A, or bands bounded, at both r) | the same, with "The statistical correlation [and the correlation of …], which is not measured, is allowed anywhere from 0 to 1" |
| "⟨reading⟩ only if r < r*" | "… agrees if [the statistical fluctuations / …], whose correlation is not measured, are correlated by less than r*; above that, … differs." |
| differ (any form) | **No paper text until the director and Joseph rule.** If it stands, the minimum is "In the … quadrant[s] [or: jointly], the sixteen-cell sums differ from the two-dimensional result (χ² = … for four degrees of freedom, p = …; z = …), with the covariance between the two results computed from the components they share. The cause is not established." It may not be softened into a bound |
| any stop (V0's or K's controls, a non-positive-definite V_d) | no X number is used. The paper keeps its present sentence, and the report names the check |

## 6. Host, cost, reads and writes, HPSS

| step | host | env | cap | basis |
|---|---|---|---|---|
| V0 | login node | omnifold_py310 | 0 node-h | arithmetic and joins; 100 draw regenerations |
| V1 probe | 1 node | omnifold_py310 | 0.25 node-h (`-t 00:15:00`) | no like-for-like timing exists, so the probe measures it |
| V1 full | 1 node | omnifold_py310 | 1.75 node-h (`-t 01:45:00`) | submitted only if the probe projects within the cap |
| BOOT | 1 node, 8 lanes × 32 threads | root_6_28 | **2.75 node-h** (`-t 03:00:00`) | 101 unfolds (B0 plus 100) at 0.02281 node-h each, S1's seed job 60233154 (1.82500 for 80; `S1-REPORT.md:136`). That is 2.30 node-h. Lane 1's 14 unfolds at about 655 s each (`S1-REPORT.md:148-149`) take about 2.6 h of wall |
| K | login node | omnifold_py310 | 0 node-h | arithmetic |

- **The total cap is 4.75 node-h,** against the scoping's estimate of ≤ 4.5. The difference is B0's extra unfold and
  lane 1's longer wall, said here. Half the group balance is 1,037 node-h.
- **Runs:**
  - every run is from a fresh clone at the bound commit, with empty porcelain before and after;
  - writes go only under `$R`, and nothing to CFS;
  - every pscratch or CFS original is read O_NOATIME and checked against its pin;
  - a moved atime is a deviation, reported and not restored.
- **HPSS:** `$R` (without the deploy clone) goes to `/home/j/josephrb/mnv-gencmp-x-20261102/` after `hpssquota`, with
  an explicit list, `hashverify` and retrieval.

## 7. The code bound (blob digests at this branch's head, recorded in the PR and the binding)

| path | what |
|---|---|
| `nd-unfolding/fd_xcov.py` | new: the pure functions (joins, draws, mapped replica, cross blocks, bound matrix, rule, route A, route B's correlation, shares) and the CLI |
| `nd-unfolding/fd_xcov_steps.py` | new: v0, v1, boot and k, which read the declared files |
| `nd-unfolding/tests/test_fd_xcov.py` | new, 32 tests |
| `fd/xcov/INPUTS.sha256` | new (§1) |
| `fd/xcov/receipts/x_v1.sh`, `x_boot.sh` | the two job scripts |

**Unchanged and called:** `s5p_numerics.py`, `s5n_pseudo.py`, `s1_assemble.py`, `fd_gencmp.py` (`read_noatime`,
`Inputs`, `quadrant_cells`, `root_hist`) and re2_driver's draw law, which is reproduced and tested.

**Tests:** run locally, `python3 -B -m pytest tests/test_fd_xcov.py` gives 32 passed. Each control is tested both
ways:
- the joins: a subsequence, a row out of order, a row absent, an ambiguous row, float64 to float32;
- the mask at each edge;
- MC identity: a differing row, the sentinel count, the row count;
- the draws against RE-2's streams and against s5n_pseudo's replica, bitwise;
- the mapped replica, including a map of the wrong length;
- the draw-check format;
- `cross_cov` against `mat_cov`, and its transpose;
- the paired joint PSD, and the bound matrix's PSD at r = 0, ½ and 1;
- χ²₄'s survival function;
- every branch of the rule: agree; a named quadrant; exactly 2.50; a joint differ; a non-positive-definite V_d;
- route A's r*;
- route B's correlation;
- the shares.

**Not tested end to end.** The cluster steps (`fd_xcov_steps.py`) have no end-to-end test on synthetic inputs. Their
controls (counts, MC rows, joins, the draw check, B0, K0, K1) are the run-time guard.
<!-- absence-ok: a statement about this branch's own new test suite, not a claim that a result does not exist -->

## 8. Limits

- **Unpaired blocks** (C_resp, the boxes, C08_R) enter V_d in full. That is correct within the stated covariances,
  and their shares are printed.
- **The C_PL pair** is a construction by the two blocks' shared rule, not a measurement. The z with it at 0 is
  printed.
- **V1 compares the signal-row weights,** not the denominator or background weights (§2.2).
- **Route B's statistical block** scales a 100-pair correlation by σ from S1's 50 and RE-2's 300 replicas. R's
  estimation error is printed as its jackknife SE.
- **A "differ"** says the two estimators' quadrant sums disagree beyond their stated covariances and the cross
  covariance measured here. It does not say which is right, and neither covariance prices unfolding bias.

## 9. Review

Recorded after the audit: `FD-GENCMP-X-REVIEW-PROMPT.txt` and `-ANSWER.txt`, each finding with its disposition.

Nothing is submitted, deposited or tagged.
