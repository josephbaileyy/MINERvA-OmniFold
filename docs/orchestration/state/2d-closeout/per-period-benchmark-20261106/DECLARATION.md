# PER-PERIOD 2D BENCHMARK DECLARATION: each run-period group's refined 2D result against the published result (2026-11-06)

**Asked for by** the director, for Joseph. Joseph authorized "the per-period 2D benchmark"
(`docs/orchestration/DECISION-20261106-joseph-plateau-next-work.md`, "What is decided" item 1; on PR #865, head
`050f3a913`, **not yet on main** when this was drafted). It is declared, audited by coverage-5b-audit and bound by the
director before anything runs.

**Drafted by** the per-period 2D benchmark lane (Claude session `director-helper-2`). Read-only on origin/main
`d95ed6802`. No jobs, no cluster contact, no product read. Every `path:line` below is at that sha unless another is
named.

**CITABLE FOR:** the choice of estimator and products, the operands bound by digest, the controls, the readings and
bars fixed before any per-group comparison is computed, the licences, and the price.

**NOT CITABLE FOR:** any result; which run period is right; a cause of the 2D shape difference or of the run-period
step; any change to E_R, Q_R or C_PL; paper or note wording.

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
7.46 × 10⁻¹² over the 205 cells (`:26, :37`). The comparison key there is still spelled `CTRL_vs_E_U`, but its
reference is E_R's product (`:36-37`). That spelling is a label left over from the purity arm, and no number is
affected.

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

**Exposure shares** e_X, constant over p_T rows: P_A 0.533379, P_B 0.294541, P_C 0.172079 (`analysis.json`
`exposure_share_by_pt_row`; the definition is in `analyze_periods.py:16`).

## 3. Controls

Each control must pass, or the run stops and goes to the director. Each tolerance is stated with its basis.

| id | check | bar | basis |
|---|---|---|---|
| C-IN | every operand's O_NOATIME copy has its declared sha256; the 205-cell set from `StatOnlyCovariance` equals each product's stored set (`reported_cells.require_same_cells`, as `compare_to_paper_fullcov.py:32, 156` uses it) | exact | — |
| C-PUB | `chi2_with_cov(E_R − p, TotalCovariance)` reproduces the full-precision 465.4152721915331 | ≤ 1e-8 relative | `OUTCOME-20261106-ref-c2c1-read.md:16`. The full-precision operand is used, not the 4-decimal print |
| C-SUM | the eigenmode sum over all 205 modes equals `chi2_with_cov` on E_R | ≤ 1e-6 relative | the receipt itself measures 1.04e-8 (`tension_report.txt:14`), so 1e-8 would fail on the correct input |
| C-K | the number of modes with λ/λ_max > 1e-4 on the bound ROOT is **73**, and S₇₃(E_R)/205 is within 0.0005 of 0.662 | exact; print precision | `tension_report.txt:56`. On the rounded text release the 73rd eigenvalue is 1.026e-4 and the 74th is 9.34e-5, 2.6% from the cut (`spectrum_gap_txt.txt`, from the committed `spectrum_gap_txt.py`; covariance only, no comparison), so **k is fixed at 73 by number**. The rule is not re-applied |
| C-M | at eigh ranks {2, 9, 23, 79, 118, 121} (0 = smallest), λ/λ_max and \|c/√λ\| on E_R reproduce `tension_report.txt:18-23` | 4 significant figures; ±0.005 | identifies the mode set M (§4). Ranks 118 and 119 are 2.7% apart (`:20, :29`), so a rotated pair fails here rather than silently |
| C-CTRL | `pu_CTRL_s42` against E_R: per-cell maximum relative difference; S₇₃ and S₂₀₅ relative differences | ≤ 1e-8 cells; ≤ 1e-6 S₇₃; ≤ 1e-4 S₂₀₅ | RE-2's 1e-8 rule; part C measured 7.46e-12. S₂₀₅'s smallest modes amplify a 1e-11 change by up to about 10⁵ |
| C-STEP | (1 + st_B)/(1 + st_A) − 1, with st from §4 R4, equals 0.10235291689162862 | ≤ 1e-10 relative | it is an algebraic identity: p cancels exactly. It ties R4 to part C's frozen step |
| C-COMB | the integral of x_ABC = Σ_X e_X x_X against `pu_CTRL_s42` | \|Δ\| ≤ 0.5% | refined J36 is −0.0764% (`analysis.json` `comparisons.J36.integral_shift_pct`). R5 rests on this combination |

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
- **Noise** (#135's convention, `analyze_periods.py:265-267`), for any statistic f:
  - σ²(f) = mean_r (f(x_r) − f(x))² + (f(x′) − f(x))²;
  - for quadratic statistics, the noise term is n_K(x) = tr(A_K N)/|K|, where N = mean_r δ_rδ_rᵀ + δ′δ′ᵀ, with
    δ_r = x_r − x and δ′ = x′ − x, and A_K = Σ_{i∈K} u_iu_iᵀ/λ_i;
  - the debiased distance is T̃_K = T_K − n_K.
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
- The gap exists because σ comes from 10 replicas plus one seed draw. At N = 10, a σ is uncertain by about ±24%, so a
  nominal 3 means somewhere from about 2.4 to 4.
- In R3, 6 modes × 3 pairs = 18 tests at 3σ. Under Gaussian independence that is about 5% familywise.
- **The bars are declared, not calibrated.** Every reading is descriptive (REF-C2C1 §0: the analyses share data, so
  no distance here is a calibrated compatibility test).

**R5, the primary reading** (K₇₃; R5̄ reads the same on K̄):

| z₅ | class | licenses | does not license |
|---|---|---|---|
| ≥ 3 | **closer without 1G–1M** | "In the 73 best-determined directions of the published covariance, the combination of the other two run-period groups is closer to the published result than the three-group combination, by Δ₅, a fraction Δ₅/T̃₇₃(x_ABC)" | that the step **causes** or **explains** the shape difference; which period is right; that the published input lacks the step; dropping 1G–1M from any result |
| ≤ −3 | **farther without 1G–1M** | the same sentence, with "farther" | the same |
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

A poorly determined mode where σ_g,i exceeds z_ALL,i is reported as **"not resolved by the period groups"**, whatever
its Δ₃.

**R4, per group:**
- **"matches the published p_∥ high/low ratio"** if |z₄,g| ≤ 2;
- **"differs"** if |z₄,g| ≥ 3;
- **unresolved** otherwise.

**The combined statement this record may make, for the note:**
- **If** R5 reads "closer without 1G–1M", **and** R4 reads A and C "match" and B "differs", the record may say: *"In
  the best-determined directions, the published result is closer to the two run-period groups without the p_∥ step
  than to the pooled result, and the published p_∥ high/low ratio matches those groups and not the group with the
  step."*
- **If** R5 reads "no change", it may say: *"The run-period step does not account for the distance in the
  best-determined directions, at the resolved size."*
- **Any other combination:** the readings, each with its own class, and no combined sentence.

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
  - there is one seed pair per group.
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
  - the noise convention;
  - the combination weights;
  - the bars and the licences.

## 8. Preconditions, compute, calendar

**Before binding:**
1. #865 (the authority) is merged to main.
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

**Compute.** **0 node-h**: arithmetic on existing products in a login step, expected to take under 10 minutes. No
sbatch, no GPU, nothing written to CFS. The director prices it.

**Calendar.** The products were written on 2026-10-24. O_NOATIME reads leave their purge exposure unchanged. The read
must happen before their pscratch purge date, which the binding records from a fresh `stat`.

## 9. Code and tests (after binding, on this lane's branch)

**The script, `per_period_benchmark.py`.** It lives in this directory. It imports:
- `tmatrix_to_numpy`, `flatten_th2d`, `flatten_ours` and `chi2_with_cov` from `2d-unfolding/compare_to_paper_fullcov.py`;
- `proj_matrix` and `STEP_LO`/`STEP_HI` from `common.py`;
- `step_stat` from `analyze_periods.py`.

It contains no second χ² or step implementation. S_K is a restriction of the eigen-sum that C-SUM ties to
`chi2_with_cov`.

**Tests, each in both directions:**
- **Every control** fires on a mutated operand and is silent on the true one:
  - a digest byte;
  - a cell index;
  - k = 72;
  - a swapped mode pair;
  - a 1e-7 perturbation of `pu_CTRL_s42`;
  - an off-by-one step range;
  - weights that do not sum to 1.
- **Fixtures with known answers:**
  - an injected B-only step, where R5 must read "closer";
  - identical groups, where every pairwise reading must be "no group separates";
  - an injection exactly at z = 2.5, which must read "unresolved".
- **The fixtures are built from the declared formulas,** not from the script's own outputs.

**A mutation harness.** It has one mutant per control, bar, divisor and combination weight. The receipt is committed
before the read.

## 10. Open for the director before binding

1. **N = 10 replicas.** Ten replicas give a σ that is uncertain by about ±24%, and the 2σ/3σ gap absorbs part of that.
   More replicas would need the period inputs rebuilt (§1) and a priced run. **The recommendation is to read at
   N = 10.**
2. **The E_U arm** (#135's products, 0 node-h), as a printed-only cross-check of the background treatment. **The
   recommendation is not to add it** here (§1).
3. **The authority is still on #865.** Binding waits for its merge.
