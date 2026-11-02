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

**What is already known (A3).** d is already known: C-R's committed readout holds both sums, both σ and C-R's bounded
reading. K, the cross covariance, is not, and the rule's outcome depends on it. Everything below was fixed before K was
computed.

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

**Committed inputs, each checked against a sha256 written into the code** (`fd_xcov_steps.COMMITTED`, and S1's
readout for its products):
- S1's universe and lateral products, `s1/readout/s1_assembly/`. Each is pinned by the S1 readout's
  `meta.inputs_sha256`.
- S1's `data_b1_j101.npz`, B0's reference.
- C-R's readout, the with-block `cpl_block.npz` and data product.
- `cmodel_5d.json` and `2d-unfolding/pv2d/cmodel/cmodel_2d.json`.
- `fd_ct_5b_periods.json` and RE-2's `playlist_term.json`.
- RE-2's `cmodel_R.json` (`partc-r2/SHA256SUMS:15`), which ties C_model,2D (§2.4).

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
- **If the projection is beyond the cap (A1),** the full run is not submitted and every band is bounded: K reads the
  probe's `within_full_cap: false` as "every band fails V1". No other choice is open.
- **If the full run ends without its readout** (a timeout, for example), K stops, and the stop is recorded. Nothing is
  rerun without a new binding.

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

**Order (S5).** B0 runs first, alone. Only if it holds do eight lanes run 1–13, 14–26, 27–39, 40–52, 53–64, 65–76,
77–88 and 89–100. Each lane writes a JSON of its products' digests. If B0 fails, no mapped replica is made, and the
statistical stream is route A. B0's reference is digest-checked against S1's readout before the comparison.

**When BOOT runs.** Only after V0 passes. If V0 fails, BOOT is not submitted.

### 2.4 K: the cross blocks and the rule

`fd_xcov.py k` runs on a login node, in omnifold_py310.

**K runs once (A2).** It runs after BOOT has ended (B0 failed, or all eight lanes have written their records), or
when BOOT was never due (V0 failed). It refuses otherwise. A stop is written into `k/k.json` with its reason, and that
file is never overwritten. So a stop under one route cannot be followed by a rerun under another.

**K0** (structural):
- the quadrant cells are the definition's;
- the 2D bin edges are read from `E_R`'s `hXSec2D` (S2);
- C_model,2D's cells are `C_PL_R`'s 205-cell index, the one C-R used. `Q_R`'s npz carries no index of its own (B2);
- `cmodel_R.json` was built from this `cmodel_2d.json`;
- the vertex order is the same on both sides;
- C-R's S₂D equals B x, and its S₁₆ equals A f plus the boxes, both to 1e-12;
- **the variances (B2):** √diag(C₁₆) equals C-R's σ₁₆, and √diag(B `Q_R` Bᵀ) equals C-R's 2D σ, both to 1e-12.

**K1** (each pairing's inputs reproduce each side's own block). The comparison is `fd_xcov.same_block`: equality to
1e-10 of the larger matrix's largest entry, with no absolute floor. That floor was the review's blocker B1: numpy's
default would have passed any block of size 1e-80. For every band, every lateral, the normalization, C_PL and C_model:
- the products K uses give the stated block: on the 5D side S1's `C_band_<b>`, `C_lat_<b>` and `C_normalization`, the
  block's `C_PL5D` and the data product's `C_model_abs`; on the 2D side S5_R's `band_<b>` and `band___Normalization_flat`,
  and `C_PL_R`;
- **C_model,2D's own tie (B2):** from its vertices and `E_R`, the per-cell σ of `Q_R` + C_model equals
  `cmodel_R.json`'s `per_cell` record, to 1e-10, in the unit in which its `sigma_Q_R` reproduces `Q_R`;
- **so each cross block is built from exactly the products inside both stated covariances.** A failure stops K.

**K2** (B3, the scoping's): the joint matrix [[C₁₆, K], [Kᵀ, C₂D]] of the paired blocks is PSD (smallest eigenvalue
≥ −1e-12 of the largest), or K stops. For route B's statistical block, which is not PSD by construction, the joint
matrix [[S₁₆, K_stat], [K_statᵀ, S₂D]] must be PSD. If it is not, the statistical stream falls back to route A, and
the readout says so.

**The statistical stream.** Route B holds iff V0 passed, B0 passed, all 100 paired products exist with their
recorded digests, and K2 holds for the statistical block. Otherwise the route is A, and the readout gives the
reason.

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
| statistical, route A, and any band failing V1 | r·M, with M = S₁₆^½ S₂D^½ for each such block. This keeps the joint matrix PSD for every r ∈ [0, 1] (`fd_xcov.bound_matrix`). **It is a one-parameter family, not every admissible correlation (A4):** a correlation outside it can make Var(d_q) smaller than r = 1 does. The paper text says "within this family" | each side's stated block |
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

**V_d must be positive definite.** Its smallest eigenvalue must exceed 1e-12 of its largest (B4), or the reading is a
stop.

**Route A, or bands bounded (A6).** The rule is read at every point of a 10,001-point grid on [0, 1].
- If the reading never changes, that is the reading.
- Otherwise it is "⟨reading at r = 0⟩ only if r < r*", with r* the first change. Every change is listed.

**Route B: R's sampling error (A5).** The readout also prints, for information only, the reading with route B's
diagonal correlations moved by −1 and +1 jackknife SE. The rule reads the point estimate. A reading that the ±SE
readings do not share is reported as SE-sensitive, beside the reading, and is not changed by it.

**Always printed:**
- d, S₁₆ and S₂D;
- z, χ²₄ and p;
- the 2×2 ρ_q = K_qq/√(C₁₆,qq C₂D,qq);
- each block's share of σ_d²: own blocks add, and a cross block subtracts twice its diagonal. Under route A the
  shares and ρ_q are printed at r = 0 and at r = 1, the bounded term included (B9);
- every cross block;
- R and its jackknife SE;
- the variant against `Q_R` alone (C_model,16 unpaired), labelled "printed";
- the sensitivity with the C_PL pair set to 0, labelled.

**No outcome is read from the variant or the sensitivity.** Either may stop on its own without stopping the primary
(B5). No tolerance or threshold here is relaxed after a run. A change needs a new declaration and binding.

## 5. Outcomes, and what the paper says in each (fixed before any number is read)

`paper_body.tex:119`'s first sentence stays until Joseph rules (#651 item 5). Every outcome goes to Joseph with C-R's
numbers (#662 §3.2, including QA's changed reading). The wording below is the minimum, and Joseph approves the final
text.

<!-- absence-ok: proposed paper text per outcome, fixed before any number is read; 'not measured' describes the route-A fallback's design -->
| outcome | the paper (minimum) |
|---|---|
| agree (route B) | "Summed over each of the four (p_T, p_∥) quadrants, the sixteen-cell result agrees with the two-dimensional result: their four differences give χ² = … for four degrees of freedom (p = …), and none exceeds 2.5 standard deviations of its difference. The covariance between the two results is computed from the systematic universes, lateral shifts, generator vertices and paired bootstrap replicas they share, with their run-period terms paired period by period by construction. The universes' signal weights were checked to agree event by event." |
| agree (route A, or bands bounded, at every r) | the same, with "The statistical correlation [and the correlation of …], which is not measured, is varied from 0 to 1 within a one-parameter family that keeps the joint covariance valid." |
| "agree only if r < r*" | "… agrees if [the statistical fluctuations / …], whose correlation is not measured, are correlated by less than r* in that family; above that, … differs." |
| "differ only if r < r*" | treated as a "differ" (the row below), with r* stated |
| differ (any form) | **No paper text until the director and Joseph rule.** If it stands, the minimum is "In the … quadrant[s] [or: jointly], the sixteen-cell sums differ from the two-dimensional result (χ² = … for four degrees of freedom, p = …; z = …), with the covariance between the two results computed from the components they share. The cause is not established." It may not be softened into a bound |
| any stop (K0, K1, K2, a non-positive-definite V_d, K run before BOOT ended) | no X number is used. The paper keeps its present sentence, and the report names the check. A stop is final under this binding |

## 6. Host, cost, reads and writes, HPSS

| step | host | env | cap | basis |
|---|---|---|---|---|
| V0 | login node | omnifold_py310 | 0 node-h | arithmetic and joins; 100 draw regenerations |
| V1 probe | 1 node | omnifold_py310 | 0.25 node-h (`-t 00:15:00`) | no like-for-like timing exists, so the probe measures it |
| V1 full | 1 node | omnifold_py310 | 1.75 node-h (`-t 01:45:00`) | submitted only if the probe projects within the cap |
| BOOT | 1 node: B0 alone, then 8 lanes × 32 threads | root_6_28 | **3.0 node-h** (`-t 03:00:00`; S4) | 101 unfolds (B0 plus 100) at 0.02281 node-h each, S1's seed job 60233154 (1.82500 for 80; `S1-REPORT.md:136`). That is 2.30 node-h. B0 then 13 unfolds at about 655 s each (`S1-REPORT.md:148-149`) take about 2.6 h of wall |
| K | login node | omnifold_py310 | 0 node-h | arithmetic |

- **The total cap is 5.0 node-h** (0.25 + 1.75 + 3.0), against the scoping's estimate of ≤ 4.5. The difference is
  B0's extra unfold, B0 running alone before the lanes, and the job's wall limit, said here. Half the group balance is
  1,037 node-h.
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
| `nd-unfolding/tests/test_fd_xcov.py` | new, 47 tests |
| `fd/xcov/INPUTS.sha256` | new (§1) |
| `fd/xcov/receipts/x_v1.sh`, `x_boot.sh` | the two job scripts |

**Unchanged and called:** `s5p_numerics.py`, `s5n_pseudo.py`, `s1_assemble.py`, `fd_gencmp.py` (`read_noatime`,
`Inputs`, `quadrant_cells`, `root_hist`) and re2_driver's draw law, which is reproduced and tested.

**Tests:** run locally, `python3 -B -m pytest tests/test_fd_xcov.py tests/test_fd_gencmp.py tests/test_fd_gencmp_e.py`
gives 141 passed and 1 skipped; `test_fd_xcov.py` alone has 47. Each control is tested both ways:
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
- the shares;
- the review's fixes: `same_block` at 1e-80; V1's `ratio_test` (a scale, one row, a non-finite quotient); K2's
  `joint_psd`; the route-A grid; a badly conditioned V_d; a non-adjacent duplicate in the join; a float64 MCgen; the
  ±SE band; K's order rules (`boot_state`, `v1_state`); every committed pin; the draw check's MC and background formats.

**Not tested end to end.** The cluster steps (`fd_xcov_steps.py`) have no end-to-end test on synthetic inputs. Their
controls (counts, MC rows, joins, the draw check, B0, K0, K1) are the run-time guard.
<!-- absence-ok: a statement about this branch's own new test suite, not a claim that a result does not exist -->

## 8. Limits

- **Unpaired blocks** (C_resp, the boxes, C08_R) enter V_d in full. That is correct within the stated covariances,
  and their shares are printed.
- **The C_PL pair** is a construction by the two blocks' shared rule, not a measurement. The z with it at 0 is
  printed.
- **V1 compares the signal-row weights,** not the denominator or background weights (§2.2). The paper text says
  "signal weights" (A7).
- **The join's ambiguous rows** are those whose (p_T, p_∥) occurs more than once in the 2D sample. They are counted and
  printed, and the greedy match may pair such a row with another event of the same coordinates (B8).
- **Route B's statistical block** scales a 100-pair correlation by σ from S1's 50 and RE-2's 300 replicas. R's
  estimation error is printed as its jackknife SE.
- **A "differ"** says the two estimators' quadrant sums disagree beyond their stated covariances and the cross
  covariance measured here. It does not say which is right, and neither covariance prices unfolding bias.

## 9. Review

A fresh Sonnet subagent (not sol) audited the declaration and code at head `a293dc3d`. Its prompt (with the worktree,
TMPDIR and head placeholders filled) and its answer are verbatim beside this file: `FD-GENCMP-X-REVIEW-PROMPT.txt` and
`FD-GENCMP-X-REVIEW-ANSWER.txt`. Every finding is fixed or answered:

<!-- absence-ok: each row quotes an audit finding about this branch's own code at head a293dc3d, with what now covers it -->
| finding | what was done | where |
|---|---|---|
| B1 (blocker), five K1 checks could not fail (numpy's default atol on ~1e-80 entries) | every K1 now uses `same_block`: relative to the largest entry, no absolute floor; tested at 1e-80 both ways | `fd_xcov.same_block`; `cmd_k` |
| A1, no rule if V1's probe projects beyond the cap | every band is bounded, read by K from the probe; a full run that ends without its readout stops K | §2.2; `v1_state` |
| A2, a non-PD stop could be followed by a rerun on another route; K's order not enforced | K runs once, after BOOT has ended or was not due; a stop is written into `k.json` and is final | §2.4; `boot_state`, `cmd_k` |
| A3, "before any number is read" is false for d | reworded: d is known (C-R); K is not, and everything was fixed before K | §0 |
| A4, route A's family is not every admissible correlation | said in §3 and in the paper text ("within a one-parameter family") | §3, §5 |
| A5, route B reads a 100-pair R point estimate | the ±1 SE readings are printed as information; an SE-sensitive reading is labelled, and the rule is unchanged | §4; `r_band` |
| A6, route A skipped the interior | the whole grid is read, and every change listed; "differ only if r < r*" has a row | `route_a`; §4, §5 |
| A7, the agree sentence overstated the C_PL pairing and V1's scope | reworded: run-period terms paired "by construction"; "signal weights" | §5, §8 |
| B2, no C_model,2D tie; K0 cells' source; variances not tied to C-R | K1 against `cmodel_R.json`'s per-cell σ; cells named as `C_PL_R`'s index; √diag tied to C-R's σ₁₆ and 2D σ | §2.4 |
| B3, scoping's K2 missing | added for the paired blocks (a stop) and the statistical block (fallback to route A) | §2.4; `joint_psd` |
| B4, the PD test was a sign test | the smallest eigenvalue must exceed 1e-12 of the largest | `verdict` |
| B5, a variant's stop aborted the primary | variants record their own stop | `evaluate` |
| B6, steps' controls untested in their direction | V1's comparison factored into `ratio_test` and tested; K's order rules and the committed pins tested; the cluster steps still have no end-to-end test (§7) | tests |
| B7, `mc_positional` compared float32 with an uncast MCgen | both sides cast to float32 | `mc_positional` |
| B8, ambiguity undercounted | now counts rows whose key occurs more than once anywhere in the 2D sample | `subsequence_join` |
| B9, route A's shares and ρ_q omitted the bounded term | printed at r = 0 and r = 1 | `k_compute` |
| S1, committed inputs not digest-checked | each is checked against a sha256 in the code; S1's products in V1 and K, and B0's reference, against S1's readout | `COMMITTED`; `weight_files`; `cmd_boot` |
| S2, 2D edges from the 5D fine grid | read from `E_R`'s `hXSec2D` | `k_compute` |
| S3, the job scripts' log and tmp directories were never created | both scripts `mkdir -p` them | `x_v1.sh`, `x_boot.sh` |
| S4, BOOT's cap (2.75) was below its wall request (3.0 h) | the cap is 3.0, and the total 5.0 | §6 |
| S5, V0 could not resume after staging; mapped lanes were not gated on B0 | V0 reuses a staged copy only if it is the pinned bytes; BOOT runs B0 alone first | `cmd_v0`; `x_boot.sh` |

Nothing is submitted, deposited or tagged.
