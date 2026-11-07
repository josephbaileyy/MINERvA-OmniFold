# PER-PERIOD 2D BENCHMARK DECLARATION: each run-period group's refined 2D result against the published result (2026-11-06)

**Asked for by** the director, for Joseph. Joseph authorized "the per-period 2D benchmark"
(`docs/orchestration/DECISION-20261106-joseph-plateau-next-work.md`, "What is decided" item 1, at origin/main: PR #865,
merge `6d0aca7f5`). It is declared, audited by coverage-5b-audit and bound by the director before anything runs.

**Revision 2** (2026-11-06) folds in the director's answers to §10 and two notes on revision 1 (`3f6c680f9`):
- N = 10 is accepted;
- there is no E_U arm;
- the control key is now stated with its digest (§1);
- R5's licence now says what a positive reading means (§5).

**Revision 3** (2026-11-06) answers coverage-5b-audit's blocking finding N1 on revision 2
(https://github.com/josephbaileyy/MINERvA-OmniFold/pull/868#issuecomment-6700734367) and a defect this lane found
while writing the code:
- **N1, the seed noise counted twice (§4).** The noise estimate is now unbiased under each of two declared noise
  models, and **a class is read only where both models give it.** Revision 2's estimator over-subtracted, which
  biased Δ₅ toward "closer without 1G–1M".
- **R4's power (§5).** Revision 2's combined sentence required R4 to read B "differs". The published covariance's own
  uncertainty on the step ratio is about 4.3% (`r4_power_txt.txt`), so "differs" needs a step of at least 14.7%.
  The refined B/A step is 10.24%, so that sentence was effectively unreachable. Its R4 clause is now conditional.
- **C-IN's cell source (§3).** E_R's driver stores no reported-cell histogram (`hReportedCells` is absent from
  `2d-unfolding/re2/re2_driver.py`), so each product's own positive-cell set is compared with the published one.
- **Exposure shares** are read at full precision. The six-decimal values sum to 0.999999 and are a check only (§2).
- **Code, tests and a mutation receipt** are on the branch (§9). Nothing has been run on the cluster.
<!-- absence-ok: a statement about this lane's own actions, not a claim that a result does not exist -->

**Drafted by** the per-period 2D benchmark lane (Claude session `director-helper-2`). Read-only on origin/main
`d95ed6802`. No jobs, no cluster contact, no product read. Every `path:line` below is at that sha unless another is
named. Every cited file is unchanged at `6d0aca7f5`: #865 touched only its DECISION record, CATALOG and the manifest.

**CITABLE FOR:** the choice of estimator and products, the operands bound by digest, the controls, the readings and
bars fixed before any per-group comparison is computed, the licences, and the price.

**NOT CITABLE FOR:**
- any result;
- which run period is right, that 1G–1M is wrong, or that the published result is right;
- a cause of the 2D shape difference or of the run-period step;
- any change to E_R, Q_R or C_PL;
- paper or note wording.

## 0. The question, and what is on record

**The benchmark.** E_R, the adopted 2D result (`DECISION-20261024-joseph-adopt-re2-2d-refined.md`, item 1), sits at
χ² = 465.4153 over the 205 reported cells against the published covariance, 2.270 per cell
(`stageF/methods/re2/run/partc_r2/partc-r2/receipts/figs/tension_report.txt:9, 14`). The integral agrees (ratio
1.0077, `:5`), and the distance is shape, not normalization (`:60`). The source of the shape difference has not been
identified (`docs/analysis-note/sec_results.tex:132`).

**Where the distance sits.** Keeping the 73 directions with λ/λ_max > 10⁻⁴, the existing scan prints 0.662
(`tension_report.txt:56`). That value divides by 205 (`2d-unfolding/diagnose_tension.py:193`), the divisor the round-4
referees objected to. **Per kept direction it is 0.662 × 205 / 73 = 1.859.** This is derived here by arithmetic and is
not a printed value. So about 29% of the χ² is in the 73 best-determined directions, and the rest is in the 132
poorly determined ones. Of the six largest contributors (`tension_report.txt:18-23`), three are at
λ/λ_max ≤ 3.6 × 10⁻⁹, in the highest-p_∥ cells (`sec_results.tex:128`).

**The run-period step.** In the 1G–1M group, p_∥ rises by about 7% above 8 GeV/c relative to 1A–1F, and the step
survives unfolding (`state/2d-closeout/period-unfold-20261014/REPORT.md:3, 63-64`, #135). The refined re-run of the
same period rows gives a raw P_B/P_A step of **+10.24%** (σ 0.48%) (`stageF/methods/re2/run/partc_r2/partc-r2/periods/analysis.json`,
sha256 `2ce5d5da…`, `comparisons["raw_PB/PA"].step.value` = 0.10235291689162862).

**The hypothesis to test** (Sonnet JINST reads 1 and 2, `secondary-results/referee-methods-round4-20261106/sonnet-jinst-methods-r4-1.txt:113, 116`;
`-2.txt:67`). The published result used every period and so averages over the step. If the published input lacks the
1G–1M anomaly, a group without it should sit closer to the published result than the pooled result does. If both
analyses carry the step, removing 1G–1M should not move the distance. **No record on main compares a run-period group
with the published result** (MAP row 5c, `secondary-results/referee-request-map-20261106/MAP.md`).

## 1. The estimator: E_R's own period products, reused (0 node-h)

The brief offered two choices: reuse #135's E_U products, or rerun the period unfolds with E_R's configuration. **A
third option exists, and this declaration takes it.** RE-2 part B already ran #135's 37 period rows with E_R's
configuration, as job J8 (`stageF/methods/re2/RE2-DECLARATION-B.md:182`; `run/partb_runs.tsv:609-645`;
`RE2-PARTB-REPORT.md:62`, COMPLETED 0:0). The argv is E_R's: `--bkg-mode negweight-refined --refine-n-estimators 400
--refine-num-leaves 31`, LightGBM, 5 iterations, seed 42, on each period's own omnifile and flux (`partb_runs.tsv:609`).

**Its control already passed in the refined arm** (`partc_r2/partc-r2/periods/control.json`, `"arm": "refined"`, `:42`).
The all-12-playlist run `pu_CTRL_s42` (`a6d3a691…`) reproduces **E_R `a5c13fc3…`** at a maximum relative difference of
7.46 × 10⁻¹² over the 205 cells (`:26, :37`).

**The key `CTRL_vs_E_U` in that file does not hold E_U.** Its reference is E_R:
- `ref.path` = `/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partb/out/ER/xsec.root`;
- `ref.sha256` = `a5c13fc38d64242bc9ee459fac87568a2f97fddf7a3ac97cc6f91eb4c2a31cef` (`control.json:36-37`).

It is not E_U's `4f5a1b6d…`. The spelling is a label carried over from the purity arm of `analyze_periods.py`
(`re2/run/partb_identities.tsv:65`, row PA-05a). Wherever this record or its outcome cites that comparison, it cites it as
"pu_CTRL_s42 against E_R `a5c13fc3…`".

**Why not the other two options:**
- **E_U (#135's products):** E_U is not the reported estimator. The background treatment alone moves the published
  distance from 2.654 to 2.270 per cell (`sec_results.tex:132`, `\chiPaperPurity`, `\chiPaper`). An E_U-based
  comparison would therefore benchmark a different estimator from the one the paper reports. The E_U arm is not run
  here. A later declaration may add it.
  <!-- absence-ok: a scoping statement about this declaration's own arms, not a claim that a result does not exist -->
- **A new E_R rerun:** it would repeat J8 at a cost. The staged period inputs were deleted under RE-2's B9 rule
  (`RE2-PARTB-REPORT.md:10`), so they would have to be rebuilt.

## 2. Operands, bound by digest

`INPUTS.sha256` in this directory lists all 39 operands with their sha256 and cluster path:
- the publication's precision reference, `cov_ptpl_minerva_inclusive_6GeV.root` `6c6dce72…`, which defines the 205
  cells (`StatOnlyCovariance` diagonal > 0) and supplies `TotalCovariance`, as bound in
  `REF-C2C1-DECLARATION.md:68`. The rounded text release is refused in its place;
- E_R, `ER/xsec.root` `a5c13fc3…`, object `hXSec2D`;
- the 37 refined period products, `partb/out/pu_*/xsec.root`. These are the control, P_A, P_B and P_C at seeds 42 and
  43, and 10 bootstrap replicas each (seeds 1001–1010, 2001–2010 and 3001–3010).

**Two records agree on all 37 period digests:** part C's `periods/analysis.json` (`_runs[*].sha256`) and the HPSS
member list `re2/run/hpss/members.sha256:2085-2121`. One driver digest covers every run (`38ff3705…`).

**Groups** (as in #135, `period-unfold-20261014/REPORT.md:41-44`):
- P_A = 1A–1F;
- P_B = 1G, 1L, 1M;
- P_C = 1N–1P;
- ALL = E_R, the control.

**Exposure shares** e_X, constant over p_T rows: P_A 0.533379, P_B 0.294541, P_C 0.172079 to six decimals
(`analysis.json` `exposure_share_by_pt_row`; the definition is in `analyze_periods.py:16`). The readings use the
full-precision values from that file, which is bound by its digest. Those values sum to 1 in every row, while the
six-decimal values above sum to 0.999999. The six-decimal values serve only as the C-PARTC check.

## 3. Controls

Each control must pass, or the run stops and goes to the director. Each tolerance is stated with its basis.

| id | check | bar | basis |
|---|---|---|---|
| C-IN | every operand's O_NOATIME copy has its declared sha256; the 205-cell set from `StatOnlyCovariance` equals each product's own positive-cell set (x > 0), compared by `reported_cells.require_same_cells`, as `compare_to_paper_fullcov.py:32, 156` uses it | exact | E_R's driver stores no `hReportedCells`. Part C recorded `n_reported_own` = 205 for all 37 period runs |
| C-PARTC | part C's `analysis.json` has sha256 `2ce5d5da…`; its shares are constant over rows, within 1e-6 of the six-decimal values above, and sum to 1 per row; its raw P_B/P_A step equals 0.10235291689162862; `n_boot_pairs` = 10 | exact; ≤ 1e-6; ≤ 1e-12 | the six-decimal values would fail a sum-to-1 test at 1e-6 (audit note); the full ones pass at 0.0 |
| C-PUB | `chi2_with_cov(E_R − p, TotalCovariance)` reproduces the full-precision 465.4152721915331 | ≤ 1e-8 relative | `OUTCOME-20261106-ref-c2c1-read.md:16`. The full-precision operand is used, not the 4-decimal print |
| C-SUM | the eigenmode sum over all 205 modes equals `chi2_with_cov` on E_R | ≤ 1e-6 relative | the receipt itself measures 1.04e-8 (`tension_report.txt:14`), so 1e-8 would fail on the correct input |
| C-K | the number of modes with λ/λ_max > 1e-4 on the bound ROOT is **73**, and S₇₃(E_R)/205 is within 0.0005 of 0.662 | exact; print precision | `tension_report.txt:56`. On the rounded text release the 73rd eigenvalue is 1.026e-4 and the 74th is 9.34e-5, 2.6% from the cut (`spectrum_gap_txt.txt`, from the committed `spectrum_gap_txt.py`; covariance only, no comparison), so **k is fixed at 73 by number**. The rule is not re-applied |
| C-M | at eigh ranks {2, 9, 23, 79, 118, 121} (0 = smallest), λ/λ_max and \|c/√λ\| on E_R reproduce `tension_report.txt:18-23` | 4 significant figures; ±0.005 | identifies the mode set M (§4). Ranks 118 and 119 are 2.7% apart (`:20, :29`), so a rotated pair fails here rather than silently |
| C-CTRL | `pu_CTRL_s42` against E_R: per-cell maximum relative difference; S₇₃ and S₂₀₅ relative differences | ≤ 1e-8 cells; ≤ 1e-6 S₇₃; ≤ 1e-4 S₂₀₅ | RE-2's 1e-8 rule; part C measured 7.46e-12. S₂₀₅'s smallest modes amplify a 1e-11 change by up to about 10⁵ |
| C-STEP | `step_stat(x_B, x_A)` equals 0.10235291689162862 | ≤ 1e-10 relative | (1 + st_B)/(1 + st_A) − 1 equals it by identity, because p cancels; a unit test checks that identity. It ties R4 to part C's frozen step without computing a per-group reading before the controls pass |
| C-GRAD | the range weights w_lo and w_hi used for σ_pub reproduce `step_stat` on E_R | ≤ 1e-12 relative | σ_pub differentiates the function `step_stat` computes |
| C-COMB | the per-row weights of x_ABC sum to 1, and the integral of x_ABC = Σ_X e_X x_X (Σ x·Δp_T·Δp_∥) matches `pu_CTRL_s42`'s | ≤ 1e-12; \|Δ\| ≤ 0.5% | refined J36 is −0.0764% (`analysis.json` `comparisons.J36.integral_shift_pct`). R5 rests on this combination |

## 4. Readings, fixed before any per-group comparison

**Notation:**
- **Groups and inputs.** g ∈ {A, B, C}. x_g is the group's seed-42 product; x_g,r (r = 1…10) are its replicas; x_g′
  is its seed-43 product. p is the published cross section, and V is `TotalCovariance` on the 205 cells.
- **Eigenmodes.** V = Σ λ_i u_i u_iᵀ, from `np.linalg.eigh` on the bound ROOT, as in `diagnose_tension.py:138-140`.
  Then S_K(d) = Σ_{i∈K} (u_i·d)²/λ_i over a mode set K. The sets are:
  - **K₇₃**: the 73 largest-λ modes;
  - **K̄**: the other 132;
  - **K₂₀₅**: all 205 modes. S₂₀₅ = `chi2_with_cov` by C-SUM.
- **The honest divisor.** T_K(x) = S_K(x − p) / |K|: the number of directions kept, not 205.
- **Noise (revision 3, coverage-5b-audit N1).**
  - **The fits.** The replicas x_r keep training seed 42 and resample the data (`--seed 42 --bootstrap-seed 10NN`,
    `re2/run/partb_runs.tsv:612, 621`). The seed draw x′ is the same data at seed 43. Write x = μ + s₄₂ and
    x′ = μ + s₄₃, with μ the fit's expectation on these data and s the seed's effect.
  - **The doubling.** For exchangeable seeds, δ′ = x′ − x = s₄₃ − s₄₂ has covariance 2·V_seed, so **δ′δ′ᵀ/2** is
    unbiased for V_seed. Revision 2 used δ′δ′ᵀ undivided.
  - **Replica centring.** Centring the replicas on x (#135's `analyze_periods.py:265-267`) adds x's own s₄₂ to every
    deviation whenever the seed's effect re-randomizes with the data. The replicas are therefore centred on their own
    mean, with divisor N − 1.
  - **Which regime holds** cannot be tested from one seed pair. It is the open rounding-instability question (MAP
    row 1a). Two noise models are therefore declared, and each is unbiased for the noise of one fit in its own regime:

    | model | N, the noise covariance of one fit | unbiased when |
    |---|---|---|
    | `replica` | the replicas' sample covariance (ddof 1, about their mean) | the seed's effect re-randomizes with the data, so it is inside the replica spread |
    | `replica+seed` | the same plus δ′δ′ᵀ/2 | the seed's effect is the same in every seed-42 replica |

    Each model is biased in the other's regime. The `replica+seed` model over-subtracts when the seed's effect
    re-randomizes, and the `replica` model under-subtracts when it does not. Both directions are tested
    (`test_n1_*`).
  - **Under each model:**
    - for any statistic f, σ²(f) = var_r(f(x_r)), ddof 1, plus (f(x′) − f(x))²/2 under `replica+seed`;
    - for quadratic statistics, n_K = tr(A_K N)/|K|, with A_K = Σ_{i∈K} u_iu_iᵀ/λ_i;
    - the debiased distance is T̃_K = T_K − n_K.
  - **Every reading and class below is computed under both models. A class is read only where the two give the same
    class.** Otherwise it reads **"unresolved (noise model)"**. Both models' values are printed.
  - A zero σ with a zero difference reads z = 0. A zero σ with a nonzero difference reads z = ±∞.
- **Independence.** The groups are disjoint in data and MC and use distinct bootstrap seeds, so their noise adds in
  quadrature in any pairwise difference. p is held fixed: these are distances to the published values, conditional on
  them.

**R1. The full χ², printed and read by nothing.** For each group, ABC and AC, and for E_R:
- T₂₀₅;
- n₂₀₅;
- T̃₂₀₅ with its σ.

#135 found the full 205-cell χ² unusable against VL175 (`REPORT.md:112`). Against V, the smallest modes have
√λ ~ 10⁻⁶ √λ_max, so a group's own noise there can dominate. That is why R1 grades nothing.

**R2. Per group, in the 73 best-determined directions.** For each group g:
- T̃₇₃,g ± σ_g.

Pairwise, for (B, A), (B, C) and (C, A):
- z₂(g,h) = (T̃₇₃,g − T̃₇₃,h)/√(σ_g² + σ_h²).

The same statistics on K̄, the 132 poorly determined directions, are reported as **R2̄** under the same bars.

**R3. In which modes** (the mode set M):
- **The set M.** M is E_R's six largest contributors: eigh ranks {23, 9, 118, 2, 79, 121}
  (`tension_report.txt:18-23`).
  - Ranks {23, 9, 2} are the three poorly determined, highest-p_∥ modes. Ranks {118, 79, 121} are the moderate-λ ones
    (`sec_results.tex:128`).
  - **M was chosen from the pooled result's own comparison.** It is the object the hypothesis names, and it is fixed
    here, before any group reading.
- **Signs.** Each u_i's sign is fixed so that E_R's component is positive.
- **Per mode i and group g:**
  - z_g,i = u_i·(x_g − p)/√λ_i, with σ_g,i;
  - Δ₃(g,h,i) = (z_g,i − z_h,i)/√(σ_g,i² + σ_h,i²).
- **Printed beside:** the components of ABC, AC and E_R.

**R4. The p_∥ step, against the published result.** For each group, ABC, AC and E_R:
- st = `analyze_periods.step_stat(x, p, met)` (`period-unfold-20261014/scripts/analyze_periods.py:152-163`), called
  unchanged, with `met.P["pz"] = common.proj_matrix("pz", cells)` (`playlist-spread-20261014/coverage/scripts/common.py:39-48`).
  The ranges are lo = [1.5, 8) and hi = [8, 15) GeV/c (`common.py:24`), and st = q_hi/q_lo − 1 with q = I(x)/I(p).
- **σ_pub²** = ∇_p stᵀ V ∇_p st. The variance is propagated linearly, with the exact gradient
  ∇_p st = −(1 + st)(w_hi/I_hi(p) − w_lo/I_lo(p)), where w_range is the row vector of P_pz weighted by Δp_∥ over the
  range.
- **The readings:**
  - z₄,g = st_g / √(σ_g² + σ_pub²);
  - pairwise, (st_g − st_h)/√(σ_g² + σ_h²), where p cancels to first order, so σ_pub is not included.
- **Printed and read by nothing:** each group's p_∥ marginal ratio to the published one per bin, with σ.

**R5. Without 1G–1M: the primary connection reading.**
- x_ABC = Σ_X e_X x_X and x_AC = (e_A x_A + e_C x_C)/(e_A + e_C).
- Their replicas and seed draws are combined index by index from the groups' own.
- Δ₅ = T̃₇₃(x_ABC) − T̃₇₃(x_AC). Its σ₅ comes from the paired differences, because x_ABC and x_AC share A and C.
- z₅ = Δ₅/σ₅.
- **R5̄** is the same reading on K̄.

**Sensitivity, printed and read by nothing:** R2 and R5 at K = the 139 and 176 largest-λ modes
(λ/λ_max > 1e-6 and > 1e-8; `tension_report.txt:55, 54`).

## 5. Bars and what each outcome licenses

**Bars:**
- **A positive class needs |z| ≥ 3. A null class needs |z| ≤ 2. Anything between is "unresolved".**
- The gap exists because **every σ, and so the noise behind every null class, comes from 10 bootstrap draws plus one
  seed draw per group.** At N = 10, a σ is uncertain by about ±24%, so a nominal 3 means somewhere from about 2.4 to
  4. The director accepted N = 10 on 2026-11-06, and the outcome record must say so beside every class it reports.
- In R3, 6 modes × 3 pairs = 18 tests at 3σ. Under Gaussian independence that is about 5% familywise.
- **The bars are declared, not calibrated.** Every reading is descriptive (REF-C2C1 §0: the analyses share data, so
  no distance here is a calibrated compatibility test).

**R5, the primary reading** (K₇₃; R5̄ reads the same on K̄):

| z₅ | class | licenses | does not license |
|---|---|---|---|
| ≥ 3 | **closer without 1G–1M** | **Removing 1G–1M changes the result's shape against the published result**, in the direction of agreement: "In the 73 best-determined directions of the published covariance, the combination of the other two run-period groups is closer to the published result than the three-group combination, by Δ₅, a fraction Δ₅/T̃₇₃(x_ABC), beyond noise estimated from 10 replicas" | **that 1G–1M is wrong; the cause** of the step or of the shape difference (the step neither "causes" nor "explains" it); **that the published result is right**; which period is right; that the published input lacks the step; dropping 1G–1M from any result |
| ≤ −3 | **farther without 1G–1M** | **Removing 1G–1M changes the result's shape against the published result**, away from agreement: the same sentence, with "farther" | the same |
| \|z₅\| ≤ 2 | **no change** | "Removing the 1G–1M group does not change the distance in these directions beyond noise; the smallest change resolved is 3σ₅ = …" | "the step is unrelated to the shape difference" outside these directions, or at a smaller size |
| otherwise | **unresolved** | Δ₅ and σ₅, as measured | any sentence above |

**R2, per group** (R2̄ the same):
- **"g farther"**: z₂(g,h) ≥ 3 against **both** other groups, and those two are within |z| ≤ 2 of each other. It
  licenses "group g is farther from the published result in these directions than the other two, beyond noise".
- **"no group separates"**: all three |z₂| ≤ 2. It licenses "the distance in these directions does not differ between
  run-period groups beyond noise", with the resolved size 3σ printed.
- **Any other pattern**: the values only.

**R3, per mode:**
- **group-dependent** where some |Δ₃| ≥ 3. It licenses "in mode i, groups g and h differ beyond noise".
- **group-independent at this resolution** where every |Δ₃| ≤ 2.
- **unresolved** otherwise.

A mode where any of the three groups has σ_g,i > z_ALL,i (E_R's component, positive by the sign convention) is
reported as **"not resolved by the period groups"**, whatever its Δ₃.

**R4, per group:**
- **"matches the published p_∥ high/low ratio"** if |z₄,g| ≤ 2;
- **"differs"** if |z₄,g| ≥ 3;
- **unresolved** otherwise.

**R4's power, measured before any reading** (`r4_power_txt.txt`, from `r4_power_txt.py`; covariance only, on the
rounded text release; the read re-measures σ_pub from the precision ROOT and prints it):
- The published total covariance gives the step ratio G = σ_pub(st = 0) = **4.28%**. The statistical part alone gives
  0.25%.
- With no group noise, "differs" needs st ≥ 3G/(1 − 3G) = **14.7%**, and "matches" holds up to st = 9.4%.
- R4 therefore cannot separate a group with a step of 7–10% from the published ratio. That is a property of the
  published uncertainty, not of this analysis. The pairwise R4 differences are unaffected, because p cancels in them.

**The combined statement this record may make, for the note** (the merged classes):
- **If R5 reads "closer without 1G–1M":** *"In the best-determined directions of the published covariance, the
  combination of the two run-period groups without 1G–1M is closer to the published result than the three-group
  combination."* One clause is added:
  - if R4 reads A and C "match" and B "differs": *"The published p_∥ high/low ratio matches those two groups and not
    the group with the step."*;
  - if R4 reads all three "match": *"At its own uncertainty, the published p_∥ high/low ratio does not distinguish
    the groups."*;
  - otherwise, no clause.
- **If R5 reads "no change":** *"The run-period step does not account for the distance in the best-determined
  directions, at the resolved size."*
- **Any other R5 class**, including "unresolved (noise model)": the readings, each with its own class, and no
  combined sentence.

**For every outcome:**
- No reading names a cause or says which period is right.
- A group that agrees does not say why.
- The result goes to the director and Joseph before any paper or note text uses it.
- The wording is theirs.

## 6. Limits carried to the outcome

These are stated here and must be repeated in the outcome record:
- **Noise is a lower bound:**
  - `--bootstrap-streams both` fluctuates data and signal MC, not the background template (`re2_driver.py:1512-1527`);
  - the universe systematics are not in σ. They are largely common to the groups, so pairwise readings are less
    affected than distances to p;
  - there is one seed pair per group;
  - each σ comes from 10 bootstrap draws (accepted by the director on 2026-11-06), so the σ itself is uncertain by
    about ±24% (§5).
- **Each group uses its own MC prior and response** (`period-unfold-20261014/REPORT.md:107-110`). At 5 iterations,
  each may be pulled toward its prior.
- P_A includes 1F (`:113`).
- k = 73 and the mode set M come from the published covariance and from the pooled comparison already on record. Each
  is fixed before any group reading.
- The published result's own period composition and processing are not measured here.
<!-- absence-ok: a scoping statement about what this test measures, not a claim that a result does not exist -->

## 7. Admissibility

- **This is a diagnostic.** Nothing here changes E_R, Q_R, C_PL or the reported cells.
- **No follow-up run** is made because of an outcome unless a new declaration binds it.
- **Fixed here:**
  - the products;
  - k = 73;
  - the mode set M;
  - the step ranges;
  - the two noise models and the both-models rule;
  - the combination weights;
  - the bars and the licences.

## 8. Preconditions, compute, calendar

**Before binding:**
1. #865 (the authority) is merged to main: **done**, merge `6d0aca7f5`.
2. coverage-5b-audit has audited this declaration, and its findings are answered.

**Before the read** (one login-node connect, after binding and after the code PR is merged and pinned):
3. **The COV2D fence:** `squeue -u josephrb` shows no `cov2d-*` job queued or running, checked immediately before the
   first read. If one appears, STOP.
4. **Copies:** each operand is copied with O_NOATIME to a new namespace,
   `/pscratch/sd/j/josephrb/per-period-benchmark-20261106/`, and its sha256 is compared in a separate step from the
   copy. Only the copies are opened.
   - If any operand is missing, STOP. HPSS retrieval (`re2-2d-rebuild-20261024.tar`) needs its own binding.
   - The import closure is checked for any other plain read of an operand.
5. **ssh:** its return code is read unpiped. A certificate failure goes to the director.
6. **Environment:** `/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3` (Python 3.11), the interpreter that
   read E_R's `hXSec2D` in REF-C2C1 (`receipts-ref-c2c1/step2/read-2/read.time:1`). Before the read, the test suite
   runs there on the pinned copy (the ROOT receipt), with BLAS at one thread, as the suite pins it.

**Compute.** **0 node-h**: arithmetic on existing products in a login step, expected to take under 10 minutes. No
sbatch, no GPU, nothing written to CFS. The director prices it.

**Calendar.** The products were written on 2026-10-24. O_NOATIME reads leave their purge exposure unchanged. The read
must happen before their pscratch purge date, which the binding records from a fresh `stat`.

## 9. Code and tests (written in revision 3, on this lane's branch; nothing run on the cluster)
<!-- absence-ok: a statement about this lane's own actions, not a claim that a result does not exist -->

**The script, `per_period_benchmark.py`** (sha256 `94fc5a3d…`; the binding pins the full digest). It has three
subcommands:
- `copy`: makes the O_NOATIME copies;
- `verify`: compares their digests, in a separate step;
- `read`: re-hashes the copies, runs every control, and computes the readings only if all of them pass.

Its exit codes are:
- 0: readings written;
- 3: STOP, with `STOP.json` holding each control's compared values;
- 4: refused (a digest, a missing operand, or the environment);
- 1: left to Python's own crash exit.

**What it imports, unchanged:**
- `tmatrix_to_numpy`, `flatten_th2d`, `flatten_ours` and `chi2_with_cov` from `2d-unfolding/compare_to_paper_fullcov.py`;
- `require_same_cells` from `2d-unfolding/uq/reported_cells.py`;
- `proj_matrix`, `area`, `PZ_A` and `STEP_LO`/`STEP_HI` from `common.py`;
- `step_stat` from `analyze_periods.py`.

It contains no second χ² or step implementation. S_K is a restriction of the eigen-sum that C-SUM ties to
`chi2_with_cov`, and C-GRAD ties σ_pub's range weights to `step_stat`.

**An import guard.** `analyze_periods.py` inserts a cluster path at `sys.path[0]` before `import common`, which is
OI-136's shape. The script therefore:
- imports the repo's `common` first;
- removes that cluster path afterwards;
- refuses unless every reused module resolves inside the repository and `analyze_periods` is bound to the repo's
  `common`.

**Tests: `test_per_period_benchmark.py`, 51 tests** (sha256 `8f3ccf8a…`). The fixture world is the publication's
rounded text release, so the conditioning is real.
- **Every control fires and stays silent:**
  - a digest byte, and a missing copy;
  - a cell index, extra or missing;
  - k = 72, and S₇₃ outside print precision;
  - a swapped and a rotated mode pair;
  - a 1e-7 perturbation of the control;
  - C-SUM between 1e-6 and 1e-4;
  - an off-by-one step range;
  - weights that do not sum to 1;
  - shares that are constant and within 1e-6 but sum to 1 + 1e-9;
  - a foreign module that only the path check sees.
- **N1:**
  - the `replica+seed` term is unbiased when the seed's effect is fixed in the replicas, and the `replica` term is
    unbiased when it re-randomizes (Monte Carlo over 300 synthetic fits, truth 2.0; the over-subtracting versions
    give 3.0);
  - each model is biased in the other's regime.
- **Known answers:**
  - identical groups give "no group separates" and "no change", with every z = 0;
  - an injected B-only step gives "closer without 1G–1M" and "PB farther". At 7%, R4 reads B "matches" and the
    sentence takes the "does not distinguish" clause. At 20%, R4 reads B "differs" and the sentence takes the
    "matches those two groups" clause;
  - an R4 injection solved for z = 2.5 reads "unresolved";
  - σ₅ equals an independent paired computation;
  - the C-STEP identity holds.
- **How the expected values are made.** They are built from the declared formulas, in independent matrix forms,
  never from the script's outputs.

**The mutation receipt, `mutants.txt`, from `mutate_per_period.py`:**
- **34 mutants, 34 killed.** They cover each control and tolerance, each bar and class rule, the divisor, k, the mode
  order, both N1 errors (the undivided seed term and centring on x), ddof, the weights and their renormalization,
  the combined seed draw, R5's replica pairing, σ_pub's (1 + st) factor and the import guard.
- **How it runs.** It mutates in place and checks that the original's sha256 is the same before and after. The child
  runs with `PYTHONDONTWRITEBYTECODE=1 -B`, and a run counts only if the runner printed the baseline's "Ran 51 tests".
- **The first run found a survivor** (the import path check). The test that kills it was added before this receipt.

**Not yet tested here:**
- **ROOT I/O** (`load_all`). This machine has no PyROOT, so the suite installs a stub `ROOT` module.
- **Python 3.11.** All five scripts parse under it, but the suite itself has not run under 3.11.
<!-- absence-ok: a statement about this lane's own actions, not a claim that a result does not exist -->

Both are covered by the ROOT receipt on the login node (§8 item 6), before the read.

## 10. The director's answers (2026-11-06)

1. **N = 10 replicas: accepted.** The disclosure is in §5 and §6. R2's noise debiasing is kept, and the deleted period
   inputs are not rebuilt.
2. **No E_U arm: agreed.**
3. **#865: merged**, at `6d0aca7f5`.

Nothing is open for the director before the audit.
