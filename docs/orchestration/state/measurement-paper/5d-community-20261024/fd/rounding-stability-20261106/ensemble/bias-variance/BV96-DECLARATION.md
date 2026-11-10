# BV96 DECLARATION: the bias–variance (mean-squared-error) trade-off of E₉₆ against configuration (e), at two reserved truths (DRAFT, 2026-11-10)

**For audit by `coverage-5b-audit` (after the director's review of 2026-11-10, §12) and binding by the director.**
Nothing has run, and nothing runs before the binding.

**Written by** the `limitation-resolver` lane (a Claude session), at the director's request of 2026-11-10 (in
correspondence). All repository citations are at `origin/main` `fd107364` unless stated.

**Authority.**
- `DECISION-20261109-joseph-methods-baseline-and-plan.md` item 4 (`:59-66`): "The bias–variance study of E₉₆ (the
  strengthened option C) comes after the methods paper's compute." Its first sub-item: "It is declared, audited, priced
  and bound once FD-PRR and LL5D have ended". Its second: "The initial methods paper neither waits on it nor changes
  because of it."
- The consult's recommendation (`state/2d-closeout/stageF/methods/secondary-results/consult-astra-publishable-path-20261109/answer.txt:25`)
  is a prospective test of the trade-off, "using absolute bias, variance, mean squared error and the size of the
  intended physics contrasts. Fresh random seeds alone are insufficient: use genuinely reserved truth deformations and
  independent simulation partitions where feasible."
- The director's design rulings of 2026-11-10 (in correspondence; to be recorded with the binding):
  - the estimators are (e) and E₉₆ only;
  - the primary metric is MSE on s5e's 153 functionals in σ_rel units, with a cell-level harm guard;
  - the 16 cells are descriptive;
  - a readout at each truth of whether F's single float32 result is consistent with the 96-fit distribution;
  - M = 30.
- **Launch timing.** Item 4 places the launch after FD-PRR and LL5D have ended. This draft is written now; its binding
  and launch wait for that.

**CITABLE FOR:**
- the design, criteria, price and code plan of BV96, as declared;
- once its outcome record exists: the verdict of §6 at the two reserved truths, and the readouts of §7 as descriptions.

**NOT CITABLE FOR:**
- **anything in the initial methods paper.** Its result, whatever it is, belongs to the next paper. Nothing about it
  enters the methods paper without a new decision by Joseph (item 4);
- any result before the outcome record exists;
- the replacement of the reported estimator. That is Joseph's decision, whatever the verdict;
- any statement about the real data, or any coverage statement. Pseudo-experiments with no nuisance draws cannot test
  interval width;
- MSE, bias or variance at any truth other than the two of §3, or with nuisances drawn;
- a reinterpretation of `OUTCOME-20261109-ens1-stab-pass-bias-worse.md`. ENS1's BIAS_WORSE at Stage 0c GiBUU stands. The
  §7.3 readout is at BV96's own truths, not at ENS1's;
- a mechanism. RS1 alone can name one (`OUTCOME-20261108-rs1-rounding-mechanism.md`).

## 1. The question, and why the metric is not the 16 cells

**The question.** ENS1 found that E₉₆ meets FD-STAB's stability bars where (e) does not, and is worse in bias at one of
17 truths by its "no worse" criterion (`OUTCOME-20261109-ens1-stab-pass-bias-worse.md`). "No worse anywhere" is one
objective. The consult's is another: whether a small bias change is paid for by a variance reduction. **At truths
reserved from every earlier study, is E₉₆'s mean squared error lower than, higher than, or not resolvably different
from that of (e)?**

**1.1 The scale argument: on the 16 cells, MSE reads "no preference" by construction.** The figures are from committed
records:
- F's per-cell rounding SD on the 16 cells is FD-STAB's `cell_sd.control`
  (`fd/receipts-stab-a1r/readout/readout-2/fd_stab.json`, sha256 `653356ae…`): **0.0117–0.0647 %**, median 0.0323 %.
- The reported per-cell statistical σ is S1's `relative_sigma.stat` (`s1/readout/s1_assembly.json`, sha256
  `81e5ef3f…`): **0.139–0.368 %**, median 0.240 %.
- So s_F / σ_stat is **0.064–0.212**, median 0.143. F's rounding variance is **0.4–4.5 % of a cell's statistical
  variance, mean 2.0 %.** That is the most E₉₆ can gain in 16-cell MSE, even if it removed all of F's rounding variance
  and left its bias unchanged.

**Why the gain cannot be resolved.**
- MSE_E − MSE_F = (b_E² − b_F²) + (V_E − V_F). The variance gain is second order in the rounding SD (about s_F²).
- F's result at a truth is one rounding draw: b_F = b̄ + ε with SD(ε) = s_F. So b_E² − b_F² carries a first-order noise of
  about 2|b|·s_F per draw.
- At a cell with |b| = 1 %, and the median s_F and σ_stat, that noise is **1.13 statistical variances per draw**, against
  a gain of **0.018**.
- Resolving the gain at 3σ needs about **3.5 × 10⁴ independent F draws per truth**. At §9's unit that is about
  710 node-h per truth.
- Put another way: E₉₆ is MSE-better in a cell only if its bias moves by less than s_F² / (2|b|). At |b| = 1 % that is
  **5.2 × 10⁻⁶**. ENS1's 96-fit floors resolve differences of about 4 × 10⁻⁴.
- So at any reserved truth whose bias is not tiny, a 16-cell MSE comparison reads NO PREFERENCE whatever the estimators
  do. The illustrative |b| = 1 % uses no ENS1 GiBUU magnitude, which ENS1's licence forbids.

**1.2 Where the trade-off is real: s5e's 153 functionals.**
- These are the functionals on which (e)'s instability was found and graded: FD-STAB §4.3, ENS1 §4.1. They are finer
  than the 16 cells.
- In units of (e)'s pseudo-data bootstrap σ_rel, F's per-functional rounding SD over FD-STAB's base and 51 jitters is
  **sd51 median 0.581, maximum 2.515** (`fd_stab.json` `stability.control`; `estimator_stability_analyze.py:86`).
- That is a rounding variance of about 0.34 σ_rel² at the median functional and up to about 6.3 σ_rel².
- There the variance a stable estimator removes is comparable to the statistical variance. A paired pseudo-experiment
  comparison can resolve it (§8).
- **The 16 cells are therefore descriptive (§7.2) and carry a harm guard (§6.3), and the 153 functionals carry the
  primary metric.**

## 2. The estimators

- **F, configuration (e), as reported.** It is the bound control path of FD-STAB's closures, unchanged, including the
  float32 unfold of `s5p_nullexp.py:342` (`unfold_one(exp, np.float32, …)`).
- **E₉₆, exactly ENS1's estimator.** `ENS1-DECLARATION.md` §2.1, with `ENS1-ADDENDUM-A1.md` §2's edge zone:
  - the mean of 96 fits of F, each run in float64 coordinates on the input plus its internal jitter δ_k;
  - internal seeds 10001–10096;
  - the closure path's `unfold_one` rebound to float64 (ENS1 §2.2, §9).
  - E₉₆ is one deterministic estimator. Its seeds are part of its definition, not a choice of this study.
- **Nothing else is compared** (the director's ruling).
- **Disclosed, as in ENS1 §10:** E₉₆'s fits are float64 and F is float32. The comparison is with the reported estimator
  as it is, dtype included. It does not isolate the effect of averaging.

## 3. The reserved truths

**3.1 The two truths.** Two GENIE v3 tunes, each its generator's own 5D shape relative to GENIE 2.12 CV, with no
amplitude, as F1's truths were (`FD-F1-DECLARATION.md` §1):

| id | tune | genie_xsec | splines | record that they exist |
|---|---|---|---|---|
| **R1** | G18_02a_00_000 | v3_04_00, `NULL/G1802a00000-k250-e1000` | ready on CVMFS | `fd/receipts-f1/declaration/probes/probe9.out:133` (the v3_04_00 version table, login25, 2026-10-27) |
| **R2** | G18_10a_02_11a | v3_04_00, `NULL/G1810a0211a-k250-e1000` | ready on CVMFS | `probe9.out:134` |

**3.2 How they are built.** Each is built by F1's chain unchanged, and its spline header is checked the same way:
1. `gen5d_v3.py spline-check` (F1 §2): the reduced spline file's header must name the tune, and its source and README
   are pinned by sha256. The pins are measured in BV96's first login connect, as F1 measured its own (`probe10.out`).
2. `run_gevgen_v3.sh genie`, then `gen5d_v3.py convert`, to a gen5d/v1 npz on the 65,856 cells (F1 §2).
3. `pvl_ratios.main`, imported unchanged, gives the truth's gated, k-normalised shape ratio to GENIE CV per fine cell
   (F1 §3).
4. It is applied as F1's and LL5D's tune truths are: `s5n_pseudo.truth_weight("ratio_nd", …, 1.0, ratio)` with the
   gated, k-normalised ratio (`LL5D-DECLARATION.md:141-142`), entered in `s5p_nullexp` as `--alternative <ratio>
   --alternative-truth ratio_nd` on the nominal hypothesis (`NULL_J_MNVTUNE`, as every F0b closure,
   `estimator_stability_probe.py:315-336`). The audit confirms that this reproduces F1's truth definition (O5).

**3.3 Disjointness.** No earlier study used either truth. The excluded truths are:

| study | its truths | source |
|---|---|---|
| F0b (and FD-PRR's flagged two, which are among them) | the 18 of `CLOSURES`: nominal, W1–W3, q3, stage0c_gibuu, closure_nuwro, A7 ×5, P1r–P3r, P1g–P3g | `estimator_stability_probe.py:315-336` |
| FD-STAB | the stability truth (GiBUU-over-GENIE `eavail_shape`, pseudo-seed 990000) and F0b's closures | `estimator_stability_probe.py:305-308`; `FD-STAB-DECLARATION.md` §3 |
| ENS1 | FD-STAB's stability truth and F0b's 17 distinct truths | `ENS1-DECLARATION.md` §3 |
| F1, LL5D, COV2D | GENIE v3 G18_10a_02_11b and AR23_20i_00_000 | `FD-F1-DECLARATION.md:45`; `LL5D-DECLARATION.md:141-142`; `OUTCOME-20261108-cov2d-both-tunes-under-cover.md` |

- **R1** is not among them, and its model set, G18_02a, is used by no earlier study.
- **R2** is not among them either, but **its model set, G18_10a, is the one of F1's G18_10a_02_11b.** It is therefore
  not independent of F1's, LL5D's or COV2D's truth. This is disclosed, and the director's review decides it (§12, O3).
- Search: `git grep -n -E 'G18_02a|G1802a|G18_10a_02_11a|G1810a0211a'` at `fd107364`. It finds only
  `inelastic-high-region-20261011` planning text (an inventory and a proposal, with no product) and the
  probe9 listing.

**3.4 Why R2, and the cleaner alternatives.** The director asked for a second truth with ready splines whose model set
is neither G18_10a nor AR23. The committed records list these ready spline sets:
- G18_10a_02_11a and G18_10a_02_11b: G18_10a;
- AR23_20i_00_000;
- G18_02a_00_000: R1;
- the set with qualifier `GDNu2001a00000-k120-e200`: `probe9.out:136`;
- the sets with qualifiers `AR2520i` and `AR2522i`, at genie_xsec v3_06_02_sbn1/2: owner-listed, not probed
  (`inelastic-high-region-20261011/REPORT.md:1034`).

**None of them is from a model set other than G18_10a, AR23 and R1's G18_02a, as far as the records establish.**
- `AR2520i`'s and `AR2522i`'s relation to AR23 is not established in any committed record. Their qualifiers share AR23's prefix, so they are not
  offered as cleaner.
- `GDNu2001a00000`'s configuration is not established in any committed record, and its `k120-e200` differs from
  every other set's `k250-e1000`. It is excluded.

**Every candidate for R2 shares a model family with a held-out tune of F1, LL5D and COV2D.**
- G18_10a_02_11a shares G18_10a with G18_10a_02_11b.
- The `AR2520i` and `AR2522i` sets share AR23's prefix.
- G18_02a, the only other family with ready splines, is R1's.
- A truth from a fresh family needs a spline build, which is unpriced (R2″ below).

**R2 is G18_10a_02_11a (the director's ruling O3, 2026-11-10).** Its splines are ready and probed at v3_04_00, F1's own
software stack, so its generation repeats F1's measured chain. R2′ would add an unprobed software stack without being
cleaner. The alternatives, priced beside it:

| alternative | what it needs | price |
|---|---|---|
| R2 = G18_10a_02_11a (declared) | the chain of §3.2 | in §9 |
| R2′ = the `AR2520i` set (its full tune name read from its spline header at the probe) | GENIE v3.06.02 software and genie_xsec v3_06_02_sbn1, both unprobed: one login probe, at 0 node-h, as F1's probes 6, 9 and 10 were; then the chain of §3.2 | generation about F1's per tune, 0.21 node-h; the rest as R2. Not cleaner on the records (above) |
| R2″ = a model set outside G18_10a and AR23, chosen by the director or Joseph | a spline build first. No spline build has a measured rate here (`inelastic-high-region-20261011/REPORT.md:703`, "at a cost not measured here") | **not priceable from measured rates.** It needs a one-node spline-build pilot, capped at 2.0 node-h, to measure the rate before it can be priced |

**3.5 The partition.**
- Each pseudo-experiment's seed fixes both its MC half and its Poisson draws: `s5p_nullexp.py:318` sets
  `split = s5c_pseudo.split_key_for(seed)`, and `build` (`:240`) draws with that seed. In expectation mode the seed fixes
  only the split (`estimator_stability_probe.py:337`).
- BV96's seeds (§4) are reserved, so its MC halves are fresh partitions. They are drawn from the same simulation as every
  earlier study, so they are not independent of it. This is the feasible form of the consult's "independent simulation
  partitions where feasible". Disclosed (§11).

## 4. Seeds, fixed here

None of these is used by any committed script or task table. Search: `git grep -n -E '\b(62|63)0[0-6][0-9]\b'` in
`3d-unfolding/genie`, `nd-unfolding` and `docs/orchestration/state`, and `git grep -n -E '\b80[89]0[0-3][0-9]\b'` in
`3d-unfolding`, `nd-unfolding` and `docs/orchestration`, at `fd107364`: 0 hits each. Products on pscratch were not
searched. The binding's deploy step lists the BV96 output root, which must not exist.
<!-- absence-ok: scoped to the Search line above; products on pscratch are explicitly not covered -->

| use | R1 (G18_02a_00_000) | R2 (G18_10a_02_11a) | earlier ranges, for contrast |
|---|---|---|---|
| gevgen pilot | 62000 | 63000 | F1 60000, 61000 |
| gevgen production, seed = run number | 62001–62064 | 63001–63064 | F1 60001–60064, 61001–61064 |
| noise-free closure (§5.1; fixes the MC split) | 808000 | 809000 | FD-STAB/ENS1 991000 |
| pseudo-experiments (§5.2) | 808001–808030 | 809001–809030 | F1 806000–806019, 807000–807019 |
| estimator | 42 | 42 | every (e) product |
| E₉₆'s internal jitter | 10001–10096 | 10001–10096 | part of E₉₆'s definition (ENS1 §2.1) |

A REQUIRED test scans every committed `--pseudo-seed(s)` in a `.tsv` or `.sh` against BV96's pseudo-experiment seeds,
as `test_fd_f1.py` does for F1's.

## 5. The runs at each truth

**5.1 One noise-free closure.** `s5p_nullexp.py --expectation --no-nuisance --mc-fraction half` at seed 808000 (R1) or
809000 (R2), with FD-STAB's bank and detector directory (`fd/receipts-stab-a1r/connect/queue.tsv:58`):
- F once (1 unfold);
- the 96 single fits of E₉₆ (96 unfolds), which give E₉₆ and the 96-fit distribution of §7.3;
- **the determinism control:** E₉₆'s k = 1 fit again, in a separate task at the same 32 threads (1 unfold). Its
  `xsec_flat` and `xtrue_flat` must equal the first k = 1 bitwise, or the analysis stops (ENS1 §3.2).

**5.2 M = 30 Poisson pseudo-experiments.** The same command without `--expectation` (Poisson draws, no nuisances), at
seeds 808001–808030 (R1) or 809001–809030 (R2). Per pseudo-experiment m:
- F once on y_m (1 unfold);
- the 96 single fits F(y_m + δ_k), k = 1–96 (96 unfolds), whose mean is E₉₆(y_m).

**5.3 The jitter is applied after the Poisson draw.**
- In ENS1's closure path the internal jitter is added to the inputs before the bound `build`, outside its
  `ExpectationRNG` window (ENS1 §9). That is harmless in expectation mode, which draws nothing.
- In Poisson mode, jittering before the draw could change a drawn count through a rate's last bit. E₉₆'s fits would then
  see different pseudo-data from F's, and the pairing of §6 would be lost.
- So in §5.2, δ_k is added to the built experiment's four coordinate arrays after `build` returns, and before the
  wrapper's grid-membership check (ENS1 §2.3, A1 §3).
- **REQUIRED test:** within a pseudo-experiment, the drawn pseudo-data and MC weights are bitwise identical across
  F and all 96 k. **REQUIRED mutant:** one that jitters before `build`.

**5.4 Unfold counts.**
- Per truth: 98 for the closure and 30 × 97 = 2,910 for the pseudo-experiments, so 3,008.
- **Both truths: 6,016.**

## 6. The primary verdict, fixed before any number exists

**6.1 The errors.**
- Per truth T, pseudo-experiment m, estimator X ∈ {F, E₉₆} and functional j (s5e's 153, `estimator_stability_analyze.functionals`):

  e^X_mj = [ (U x̂^X_m)_j / (U x^true_m)_j − 1 ] / σ_rel,j

- x^true_m is the pseudo-experiment's own `xtrue_flat`. It must be bitwise equal across F and all 96 k of that
  experiment, or the analysis stops.
- σ_rel is (e)'s pseudo-data bootstrap σ, the pinned receipt that FD-STAB and ENS1 used (`state/s5e/cand/assess_receipt.json`
  `sigma_rel_pct`, sha256 `84266e30…`, pinned at `estimator_stability_analyze.py:67`).
- Disclosed, as in ENS1 §4.1: σ_rel is (e)'s, not E₉₆'s. Here it is only a fixed yardstick that makes functionals
  comparable. E₉₆'s own variance is measured (§7.1).

**6.2 The statistic.**
- Per truth and experiment: d_m = (1/153) Σ_j [ (e^E_mj)² − (e^F_mj)² ], the paired difference in mean squared error
  per functional, in σ_rel² units.
- A_T = mean over m of d_m, and SE_T = SD_m(d_m) / √M, with ddof 1. Taking the SD over experiments carries every
  correlation between functionals.
- A_T estimates MSE_E − MSE_F averaged over the 153 functionals. Negative means E₉₆ has the lower MSE.
- **Bounds:** L_T = A_T − 2.241·SE_T and U_T = A_T + 2.241·SE_T. 2.241 is the one-sided normal quantile at 0.0125: four
  one-sided claims (two truths, two directions) share a familywise 0.05.
- **Materiality margin m = 0.05 σ_rel².** That is 5 % of a functional's statistical variance, about one seventh of the
  median functional's rounding variance (§1.2). A smaller difference is not material, even when resolved.
  **A-priori ground:** a 5 % change in mean squared error is a change of under 2.5 % in the root-mean-square error
  (√1.05 = 1.025). That is below what an uncertainty quoted to two significant figures resolves.

**6.3 The harm guard, on the 16 cells.**
- **Harm** means that E₉₆ makes a reported cell's mean squared error worse than F's by more than a quarter of that cell's
  pseudo-experiment variance, and that the excess is resolved.
- Per truth T and cell c, with relative errors r^X_mc = x̂^X_mc / x^true_mc − 1:
  - D_Tc = mean over m of [ (r^E_mc)² − (r^F_mc)² ], and SE_Tc = SD_m / √M;
  - V^F_Tc = the sample variance over m of r^F_mc (ddof 1);
  - harm at (T, c) if **D_Tc − 2.955·SE_Tc > 0.25·V^F_Tc**. 2.955 is the one-sided quantile at 0.05/32, over 2 truths ×
    16 cells.
- By §1.1, the rounding gain in a cell is at most 4.5 % of its variance. The guard can therefore trigger only on a bias
  increase that matters at the statistical level, and never on the rounding term.
- **A-priori ground:** a 25 % increase in a cell's mean squared error is a 12 % increase in its root-mean-square error
  (√1.25 = 1.118), large enough to change the cell's quoted uncertainty visibly. The one-sided 0.05/32 keeps the chance
  of a false harm flag at any of the 32 truth-cells at or below 5 %.

**6.4 The verdict.**
- At truth T: **E-better** if U_T < −m; **F-better** if L_T > +m; otherwise **unresolved**.
- **PREFER_E96:** E-better at both truths, and no harm at any (T, c).
- **PREFER_F:** F-better at one or both truths, and E-better at neither.
- **NO_PREFERENCE:** every other case. The record names which:
  - unresolved at both;
  - E-better at one and unresolved at the other;
  - **mixed** (E-better at one, F-better at the other);
  - **E-better at both but blocked by harm**, with the harmed cells listed.
- **INVALID:** SE_T = 0 at a truth, or V^F_Tc = 0 at some cell. Terminal; to the director.
- **INCOMPLETE / STOP:** as in ENS1 §4.4. Nothing is graded.

**What a verdict does, and does not, do.** None changes the methods paper or the reported estimator.
- PREFER_E96 is evidence for the next paper's estimator choice, which is Joseph's.
- PREFER_F and NO_PREFERENCE leave (e) as the baseline. The record states the verdict.

## 7. Readouts with no criterion

**7.1 The decomposition, per functional and per cell, for both estimators.**
- Bias: the mean over experiments of e (or r), and the noise-free closure's error (§5.1).
- Variance: the sample variance over experiments.
- MSE as bias² plus variance, beside the direct mean of squares of §6.

E₉₆'s statistical σ relative to F's is printed. ENS1 assumed it unchanged and did not check it (ENS1 §10).

**7.2 The 16 cells, descriptive.** D_Tc, SE_Tc, V^F_Tc and V^E_Tc, and the two biases, per cell and truth.
- They are printed beside §1.1's scale figures, computed on BV96's own experiments: s_F,T (below) over V^F_Tc.
- No criterion uses them except the harm guard of §6.3.

**7.3 Is F's float32 result a draw from the 96-fit distribution?** The director's readout, at each truth.
- On the noise-free closure, per cell c and per functional j: z = (F − mean_k F_k) / SD_k F_k, with the 96 single fits
  F_k and ddof 1.
- On each experiment, the same z. Printed: the fraction of the 30 × 16 cell values and of the 30 × 153 functional values
  with |z| > 3, beside 0.0027, the normal reference.
- **The interpretation rule, fixed now, which never moves the verdict:**
  - if every |z| on the closure's 16 cells is ≤ 3, the record reads "at T, F's float32 result is consistent with a draw
    from E₉₆'s 96-fit distribution";
  - otherwise it reads "at T, F's float32 result lies outside that distribution in cells …".
  - The second reading admits the float32-versus-float64 difference of §2 and an input-dependent component (ENS1 §4.3's
    c). It does not separate them.

**7.4 How numerical-instability variance enters, and its share.**
- **It enters through the pseudo-experiments, once.** Each experiment's F fit carries its own rounding deviation,
  because each y_m is a different input. Each E₉₆(y_m) carries the deviation averaged over 96 fits. So V^F and V^E each
  already contain their estimator's rounding variance.
- No rounding variance is added separately. Adding FD-STAB's s_F² to V^F would count it twice.
- **The share is printed:**
  - s²_F,T, the mean over experiments of the variance over k of the 96 single fits;
  - its fraction of V^F;
  - E₉₆'s numerical variance s²_F,T / 96, against V^E, per functional and per cell.

## 8. Power

**The analytic approximation**, stated as an expectation and not part of any bar:
- Write e^F = e^E + ε_j, with ε the per-experiment rounding deviation of F (SD sd_j in σ_rel units).
- Then (e^E)² − (e^F)² = −2·e^E·ε − ε². Its mean is about −sd_j²(1 − 1/96)(1 − c), the gain. Its SD is about
  2·√(b_j² + 1)·sd_j per functional, with b_j the bias in σ_rel units.
- d_m averages 153 correlated such terms.
- The gain is first order in sd_j against the noise (unlike the 16 cells, §1.1). Power is good at truths whose biases
  are a few σ_rel or less, and falls as |b_j| grows.

**A declared power simulation is required before the audit closes (O1).**
- `bias-variance/power/bv96_power_sim.py`, seed 20261110, with output committed.
- Its inputs:
  - the per-functional sd_j from FD-STAB's control base and 51 jitters;
  - the per-functional bias distribution of (e) at F0b's 17 truths, in σ_rel units, from FD-STAB's control closures.
    These are development truths, so reading them for power is allowed; they are not BV96's.
- Those products are on pscratch: a read-only login read with O_NOATIME, at the director's go.
- It reports P(E-better at both), P(F-better), P(NO_PREFERENCE) and P(harm) at M ∈ {20, 30, 40, 60}.
- **M = 30 is declared (the director's ruling).** If the simulation gives P(E-better at both) < 0.8 under the model "E₉₆
  removes F's rounding variance and leaves its bias unchanged", BV96 returns to the director for M before the binding.

**The O1 result (2026-11-10; `power/receipts-o1/`, `power/bv96_power_sim.out.txt`). The power is far below 0.8 at
every M simulated, so M returns to the director.**
- The inputs are FD-STAB's 70 control products, read on login40 under O_NOATIME, each digest equal to its committed
  line. `bv96_power_derive.py` reproduces fd_stab.json's sd51 (0.5813 / 2.5153) and cell_sd.
- **The headline**, the minimum over ρ of the median over the 136 truth pairs of P(E-better at both): **0.001 at
  M = 20, 30, 40 and 60.** Without the two GiBUU truths, it is 0.0007 at M = 30 over the 105 remaining pairs.
- FD-STAB §5.3 keeps the GiBUU truths' bias magnitudes out of every criterion, and ENS1's licence keeps them out of any
  use beyond "no worse". The simulation's inputs include FD-STAB's control closures at A7 GiBUU and Stage 0c GiBUU, as
  development inputs for power planning only. The figures quoted below exclude them. Whether they may enter at all is
  the director's to rule (O6).
- Per truth at M = 30, P(E-better) is 1.000 at the nominal truth. At the 14 other non-GiBUU truths it is 0.015–0.12:
  at the false-claim level, except W2 (0.10–0.12) and P3r (0.05).
- **Why.** At F0b's non-nominal truths, (e)'s noise-free bias on the 153 functionals is large in σ_rel units: median
  |b_j| from 4.5 (W2) to 62 (A7 NuWro), against 0.46 at the nominal truth. E₉₆'s gain is at most mean sd51² = 0.78
  σ_rel². Its noise is about 2|b_j|·sd_j per experiment: SD(d_m) is 4.1–53 at those truths, against 0.55 at the nominal
  truth.
  - So §1.1's scale argument holds on the 153 functionals as well, once the truth's bias is many statistical σ.
  - Power 0.8 at one truth would need about 350 (W2) to about 28,000 (P1g) experiments, with a median over the 14 of
    about 5,800. That is about 700 to 55,000 node-h per truth.
- **What it means for BV96.** At generator-shape truths like F0b's, and so very likely at R1 and R2, an MSE comparison
  of E₉₆ with (e) reads NO_PREFERENCE by construction at any affordable M. The MSE preference there is decided by the
  bias term, which the estimator's own rounding draw prevents resolving at the second-order scale of the gain. The
  director decides how BV96 proceeds (O6, §12).

## 9. Compute

**The unit is ENS1 stage 2's measured charge:** 32.9389 node-h over its 1,626 full-run unfolds, **0.020258 node-h per
unfold** (`ensemble/receipts/stage2-a1/README.md:135`; `timing.unfolds` 1626 at `:241`).
- Those were float64 E₉₆ closure fits on the same path, on exclusive 8-lane nodes.
- The ceiling rate uses its slowest unfold, 792.827 s (`:241`): 792.827 / 3,600 / 8 = **0.027529 node-h**.
- F's float32 fits are faster (FD-STAB: 466 s per control closure unfold), so the unit is conservative for them.

**Generation** is F1's measured charge for two tunes: F1a 0.104722 plus F1b′ 0.310000, so **0.414722 node-h**
(`FD-F1-REPORT.md:128-143`).

| step | what | unfolds | expected node-h | `--time` | charge ceiling |
|---|---|---:|---:|---|---:|
| G | spline check and pilot (login, then 1 node), then production (1 node), both tunes | — | 0.41 | `00:30:00` + `01:00:00` | 1.50 |
| dry | 1 node: R1's closure F, k = 1–2 and the determinism control; R1 m = 1's F and k = 1–4 | 9 | 0.18 | `00:45:00` | 0.75 |
| full | the other 6,007, packed as ENS1 (2 internal seeds per task; one task per F fit), 23 one-node shards of at most 33 unfolds per lane | 6,007 | 121.69 | `07:30:00` each | 172.50 |
| **total** | | **6,016** | **122.28** | | **174.75; cap 175.0** |

- **At M = 30, the expected charge is 122.3 node-h and the ceiling 174.75.** The ceiling is the sum of the Slurm limits
  on exclusive single-node jobs, so Slurm binds the cap. At the slowest-unfold rate, the 6,016 unfolds alone come to
  165.6 node-h.
- **Other M**, unfolds and then expected node-h (ceiling rate): M = 20, 4,076 and 82.6 (112.2); M = 40, 7,956 and 161.2
  (219.0); M = 60, 11,836 and 239.8 (325.8).
- **Against the balance:** half the balance is 813 node-h (the director's figure, to be re-read from iris at the
  binding's connect). **BV96's cap of 175.0 is below it, so the launch does not go to Joseph on cost** (item 4). M = 60
  is also below it.
- **The projection gate.** The full run starts only if the dry run's measured per-unfold time t gives a per-shard wall
  (the largest lane load × t + 300 s) of at most 0.9 × 7.5 h = 6.75 h: **t ≤ 727 s** at 33 unfolds per lane. Otherwise it
  returns to the director for a reprice. ENS1's stage-2 median was 523.8 s and its dry-run t 603.1 s.
- The dry run's products carry into the full run, which skips them. **No resume without the director.**

**The consult's 497 node-h, checked.**
- `answer.txt:49`: 227 unfolds × 96 fits × 0.022828 node-h = **497.5 node-h**. The arithmetic is right.
- Its 227 is LL5D's unfolds per truth for one covariance rebuild (`LL5D-DECLARATION.md:291-303`), so it is one truth's
  rebuild. At ENS1's measured 0.020258 it is 441.5 node-h. Both of LL5D's truths would be twice that.
- **BV96 rebuilds no covariance,** so that figure does not price BV96. It prices an E₉₆ coverage study, which BV96 is
  not.

**Rules.**
- CPU only, QOS regular, `--exclusive`, `--no-requeue`. Every `--time` is in HH:MM:SS, with scontrol's TimeLimit
  checked.
- Nothing is written to CFS from a job. Products go to `/pscratch/sd/j/josephrb/bv96-<date>/`, which must not exist at
  deploy.
- Every pscratch read uses O_NOATIME, and FD-STAB's references are copied with `dd iflag=noatime`.
- Every connect:
  - a fresh clone at the bound sha;
  - the login survey and `cov2d_fence.sh`, recorded;
  - iris read;
  - ssh's rc read unpiped;
  - the connect script's sha256 sent to the director, with launch only on the director's go on that sha;
  - each receipt committed as a PR.
- **The COV2D fence:** BV96's inputs are the 5D bank, the s5p background dump, the bank sweep, the detector directory
  and two new GENIE v3 samples. None is a COV2D input. The check is still run and recorded.

## 10. Gates, before any reading

- **E1, one estimator:** every product carries a BV96 meta block with one code digest set, the declared input digests,
  the truth id, the seed and k (or "F"). Each of the 6,016 (truth, seed, k) cells is present exactly once.
- **E2, the perturbations survived:** for each experiment, the 96 fits' post-jitter coordinate digests are distinct, and
  each differs from F's input (ENS1 §4.5 E2).
- **E5, the grid held:** every product's `moved_rows` is zero (ENS1 A1, gate E5).
- **E6, the pairing:** within each experiment, the drawn weights and `xtrue_flat` are bitwise equal across F and the 96
  fits (§5.3, §6.1).
- **E7, the determinism control:** as in §5.1.
- **E8, dtypes:** F's product records float32 coordinates and E₉₆'s fits record float64.
- **E9, the truth samples:** each tune's spline header, flux check and strict sampling test pass, as in F1 §2. Their
  outputs and digests are recorded before any unfold reads them.
- **E10, the σ receipt:** it is the pinned file, and its functionals are s5c's 153 (ENS1 §4.5 E4).

## 11. Limits and disclosures

- **Two truths.** A verdict at R1 and R2 is not a verdict at other truths, on data, or with nuisances drawn.
- **R2 shares the G18_10a model set with F1's G18_10a_02_11b** (§3.3), so it is not independent of F1's, LL5D's or
  COV2D's truths.
- **The partitions are fresh but not independent** of the simulation every study used (§3.5).
- **σ_rel is (e)'s** (§6.1). The primary statistic is a paired difference, so the choice of yardstick scales but does not
  bias it.
- **Float32 against float64** (§2), as in ENS1 §10.
- **The power is modelled** (§8) until O1's simulation is committed.
- **The 16-cell scale argument** uses FD-STAB's `cell_sd.control`, measured on one input (the stability truth at
  pseudo-seed 990000), and S1's statistical σ on data. §7.2 measures both on BV96's own experiments.
- **N = 96 fits cost 96× one fit.** BV96 measures MSE, not cost.

## 12. Open items for the director's review and the audit

The director's rulings of 2026-11-10 (in correspondence; recorded with the binding):

- **O1, the power simulation (§8).** The read-only login read of FD-STAB's control closures on pscratch is approved,
  under O_NOATIME, with the script's sha256 sent to the director first. If P(E-better at both) is below 0.8 at M = 30,
  M returns to the director with the price at the M that reaches 0.8.
- **O2, the code.** F1's bound tables `gen5d_v3.TUNES` and `SPLINE_PINS` (`3d-unfolding/genie/gen5d_v3.py:48-56`) are
  not changed. A BV96 wrapper extends them at call time with R1 and R2. **REQUIRED test:** F1's tables, and the bytes of
  `gen5d_v3.py`, are identical after any BV96 run. The Poisson-mode jitter of §5.3 is a new rebinding point, with its
  test and mutant.
- **O3, R2.** G18_10a_02_11a, disclosed (§3.3, §3.4).
- **O4, the margin and the guard.** m = 0.05 σ_rel² (§6.2) and h = 0.25 of a cell's variance at one-sided 0.05/32
  (§6.3) go to audit as drafted, each with its a-priori ground.
- **O5, the truth's entry.** Accepted. F1's ratio is relative to GENIE CV. §3.2 enters it on the nominal hypothesis
  through `s5p_nullexp`'s alternative, where F1 used `s5e_candidate` and LL5D `fd_1b_toys.truth_ratio`. **REQUIRED
  test:** the weight equals F1's definition on a fixture, as FD-STAB's addendum A1 checked for `closure_nuwro`
  (`estimator_stability_probe.py:614`).
- **O6, the O1 power result (§8): open, for the director.** At M = 30 the headline is 0.001, and no M up to 60
  reaches 0.8. The lane does not change the design; the director decides.
- **Sequencing.** BV96 goes to `coverage-5b-audit` after LL5D's fix A1a.2, routed by the director. Per item 4, it is
  bound and launched only after LL5D ends. Its cap is under half the balance, so the launch is the director's after the
  binding, with Joseph told first.

## 13. Code plan (for the audit; the code follows the binding)

Bound modules are imported unchanged, apart from the rebindings below. If one needs a change, the lane stops and asks
the director (O2).

| file | role |
|---|---|
| `nd-unfolding/bv96_probe.py` | `closure --truth T --k LIST` and `pe --truth T --seed S --k LIST\|F`, through ENS1's `ensemble_estimator_probe` installs with §5.3's post-draw jitter in Poisson mode; `tasks`: the queue, shards and dry list |
| `nd-unfolding/bv96_analyze.py` | gates E1–E10; §6's A_T, SE_T, bounds, harm guard and verdict; §7's readouts |
| `nd-unfolding/sbatch_bv96.sh` | one node, modes `dry` and `shard <i>`; ENS1's refusals |
| `3d-unfolding/genie/bv96_gen5d.py` (O2) | a wrapper that extends `gen5d_v3.TUNES` and `SPLINE_PINS` at call time with R1 and R2, then runs F1's scripts; `gen5d_v3.py` is unchanged |
| `nd-unfolding/tests/test_bv96.py` | §5.3's pairing test, the seed scan of §4, O2's byte-identity test of F1's tables, O5's weight-equality test against F1's definition, the z readout, and a test in each direction for every gate and criterion |
| `nd-unfolding/tests/bv96_mutation.py` | the mutation harness: REQUIRED mutants for §5.3 (a jitter before `build`), for the verdict's four branches, for the harm guard's sign and threshold, and for a σ_rel that is not the pinned receipt |

Nothing is submitted, deposited or tagged.
