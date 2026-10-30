# DECLARATION: the audit of the 5B run-period block C_PL,5D, with its stop condition fixed before it runs (2026-10-30)

**By** the measurement session `coverage-5b-audit` (ListAgents), for the director to bind.

**Under** [`DECISION-20261030-joseph-4b-not-now-5b-audit-then-add.md`](../../../DECISION-20261030-joseph-4b-not-now-5b-audit-then-add.md)
(sha256 `2c3031d1…`) item 2: "The 5B run-period block is audited, then added to the 16-cell reported covariance", with
an audit that "is declared and bound as usual" and "states before it runs what result would stop the addition". The
standing constraints are [`HANDOFF-20261029-coverage-session.md`](HANDOFF-20261029-coverage-session.md) §1.

**After:**
- [`FD-CT-5B-DECLARATION.md`](FD-CT-5B-DECLARATION.md) (`bdfb23fd…`), its binding, and
  [`FD-CT-5B-REPORT.md`](FD-CT-5B-REPORT.md) (`62ab9dea…`), whose readout `fd/readout/fd_ct_5b_periods.json`
  (`a5b17895…`) holds C_PL,5D;
- [`FD-CT-READERS-5A-REPORT.md`](FD-CT-READERS-5A-REPORT.md) and its readout `fd/readout/fd_ct_period.json` (`d7d518ac…`);
- 2D's construction, `2d-closeout/playlist-term/DESIGN.md` §2–§4.

**Declares:**
- the audit's four measurements, their methods and units, and a STOP CONDITION (§7);
- the exact revised covariance and every product it would flow into (§8);
- the reader `nd-unfolding/fd_ct_5b_audit.py`, its tests, a mutation receipt, an independent review, the exact
  commands and the pins (§9, §10, §14).

**The order.** §2–§8 were first committed as a design freeze (PR #546, `28499ab5`), in the order 2D's DESIGN used
(`2d-closeout/playlist-term/DESIGN.md` §5). The director then ruled by message, on 2026-10-30, that the code be folded
into this PR and bound once: "The STOP condition is accepted as frozen design: O, N and R, with a refused control
leaving the question undecided and the block not added. Don't change those thresholds while you write the code. If
the code shows one can't be computed as written, tell me before changing it." No threshold changed. §13 lists what
writing the code corrected or found, each item named.

**MEASURES:** nothing. No audit quantity has been computed; the code has run only on synthetic fixtures.

**CANNOT AUTHORIZE:**
- running the reader, which needs the director's binding;
- the addition itself. If the stop condition does not fire, the addition is its own declared step (§8.3);
- any write to the reported matrix C_total + C_resp, to `s1_assembly.npz`, to `cresp.npz` or to any committed readout;
- a generator χ², a reading of the data against any prediction, a claim or printed wording;
- new unfolds, event loops or Slurm jobs. The audit runs on a login node at 0 node-h.

**CITABLE FOR:** what the audit will compute, from which inputs, in which units, and which results stop the addition.

**NOT CITABLE FOR:**
- any result;
- a cause of the period differences, or which period is right;
- a validated size for C_PL,5D. A block built from the observed offsets contains them by construction
  (`2d-closeout/playlist-term/REPORT.md:20`), and this audit does not change that;
- a coverage or calibration statement.

**Paths:** as in `FD-CT-5B-DECLARATION.md`. A bare `.md` name is in this directory. Paths beginning `docs/`,
`nd-unfolding/`, `2d-unfolding/` or `publication/` are from the repository root. Every other path is relative to
`docs/orchestration/state/`. `$P` = `/pscratch/sd/j/josephrb`, and `$B5` = `$P/fd-ct-5b-20261030`.

### What this session read before writing the stop condition

The decision's third reason for the audit is that the block "was chosen after the data were seen". So the reads behind
this design are listed in full:
- **numbers already reported:** every table of `FD-CT-5B-REPORT.md` and `FD-CT-READERS-5A-REPORT.md`; S1's per-group
  σ table (`S1-REPORT.md` §6); 2D's committed noise share (`2d-closeout/playlist-term/outputs/playlist_term.json`
  `report.noise_share`);
- **structure only:** the key layout of the 5B and 5A readouts; the object names and classes in
  `fd/receipts-ct/5b/flux/runEventLoopMC_PA.root` and in two files of `$P/MINERvA-OmniFold/2d-unfolding/baseline_flux/`
  (copied to this session's scratchpad); `ls` of `$B5/unf/`, `$B5/truth/`, `$P/2d-closeout-period-unfold-20261014/out/`
  and `$P/tmp-playlist-term-20261016/`; the sha256 of the committed files pinned in §1;
- **arithmetic on constants only:** the χ² and Beta quantiles and the ν_eff interval quoted below.

**Not read:**
- no block of `s1_assembly.npz` or `cresp.npz`, and no eigenvector of any block;
- no overlap, no replica-built block and no 5A noise;
- no prediction or generator χ².
<!-- absence-ok: a scoping statement about this session's own reads, listed in full above -->

**What the reported numbers already imply, said before the run:**
- 5B reports C_PL,5D's σ at a median 9.0 times its noise floor. So clauses N and R (§7) are not expected to fire. They
  are declared because that floor comes from the same ten replicas, and the replica-built blocks test it directly.
- In the reported table, the two cells where PB's and PC's offsets are smallest, R00 and R08, are the two cells with
  E_avail < 0.8 GeV and p_∥ < 4.5 GeV/c. Any test of that is post hoc, and §5 labels it so.

## 0. Summary

**The object.** C_PL,5D is the 16 × 16 relative block P of the 5B readout (`C_PL5D.C_PL5D_rel`). It is DESIGN §2 on
R00–R15: m = Σ e_X r_X, g_X = r_X/m − 1, P = k Σ_X e_X g_X g_Xᵀ, with k = V2/(1 − V2) = 0.6691. Its rank is 2.

**The four measurements** (decision item 2's list; §3–§6):

| item | question | primary measurement | stop clause |
|---|---|---|---|
| 1, overlap | Is P already in the flux, detector-response or any other existing block? | identification of the period offsets' pattern by one existing component; the duplication bound OV per group | **O** |
| 2, noise and stability | Is P's size determined, given ten bootstrap replicas per period? | the spread of ten replica-built blocks; the floor's jackknife; the three-period interval | **N** |
| 3, 5A against 5B | Why do the cell patterns differ while the sizes agree? | the uniform share of each block; 5A's noise; the angle between the planes | none (§5.4) |
| 4, rank two | What can a rank-two block represent? | the plane's stability under the replicas; the largest χ² reduction it can cause | **R** |

**THE STOP CONDITION** (§7, fixed here): the block is **not added** if any one of these holds:
- **O:** one existing component of C_total + C_resp, at no more than 2σ of its own size, explains at least half of the
  noise-weighted pattern of both g_PB and g_PC, after a free normalization per period;
- **N:** the ten replica-built blocks' median per-cell σ has an SD over the replicas above half the observed median σ;
- **R:** in the median replica, less than half of the replica block's variance lies in the observed block's plane.

Any refused control is a STOP that leaves the condition undecided, and the block is not added until a bound rerun
decides it.

**Cost:** 0 node-h. One reader on a login node, under a 1,200 s timeout, CPU only. Nothing goes to CFS.

## 1. Inputs

Every pin will be in the reader's code, not its argv.

| input | where | pin |
|---|---|---|
| the 5B readout: P, g_X, the noise σ of g_X, the floor, σ_M | `fd/readout/fd_ct_5b_periods.json` (committed) | `a5b17895b1189543d773e94717e14cd9b1409535e366c96788f94bf6f40759db` |
| the 5B unfolds: per period, seed 42 and replicas 1001–1010 / 2001–2010 / 3001–3010 | `$B5/unf/{PA,PB,PC}/` (on pscratch; also in the HPSS tar `cf33e7ad…`) | each digest in the 5B readout's `inputs_sha256.unfolds` |
| the 5B MC truths | `$B5/truth/truth_{PA,PB,PC}.npz` | the 5B check receipts' digests, as the 5B reader's Q2 |
| the 5A readout: g_5A and C_PL,16 (central weighting) | `fd/readout/fd_ct_period.json` (committed) | `d7d518ac20acd90d9d411dbd1353c509e734e8588b6bc3965ae5f14cf9303728` |
| 2D's per-period unfolds: `pu_X_s42`, `pu_X_s43`, `pu_X_b01`–`b10` | `$P/2d-closeout-period-unfold-20261014/out/` | the sha256 in `2d-closeout/period-unfold-20261014/outputs/analysis.json` `_runs` |
| 2D's playlist term (the 205-cell g_X and x) | `playlist_term.npz`, as 5A read it | `c1723cb5…` (5A's pin) |
| 2D's committed noise share | `2d-closeout/playlist-term/outputs/playlist_term.json` | `5b023478eb5825a298fd3e851b614fd4780ab27b927214e253f5c4c0df52f7b9` |
| S1's assembly: f, U and every block of C_total | `$P/s1-20261024/s1_assembly.npz` | `db000707780d4d6da65389be9adedfd9a3ba6552a255f6ce81ccbdd0b8eb72a4` |
| C_resp and its four species | `$P/cresp-20261026/out/cresp.npz` | `4d8b579732b79cbbb8e6c9a4f6335c4bda4eae6dd4194241a0d8cd6e7ea8a20a` |
| C_model's three vertex vectors S (3 × 16, relative) | `nd-unfolding/pv-ladder/readouts/cmodel_5d.json` (committed), as G-DIAG reads them (`nd-unfolding/fd_g_diag.py:156`, `:316-317`) | `3cfdc6a5b8c6cea5f99b4678e27f6ca5f7973ee57a79b9d139798f0751cfcd60`; SᵀS must equal `C_model_frac` to 10⁻¹² |
| the cell definition | `nd-unfolding/pv-ladder/readouts/h2_definition.json` | `b67907615fe2e903e60ae6caa1c141fa007676c0a1b3ae9f42490d331bfdda89` |

**The blocks, by key.**
- `s1_assembly.npz`: `C_band_<b>` for the 38 bands, `C_lat_<b>` for the 5 laterals, `C_normalization`, `C_stat`,
  `C_seed` and `C_model_frac` (`nd-unfolding/s1_assemble.py:321-371`).
- `cresp.npz`: `C_resp_proton`, `C_resp_meson`, `C_resp_em`, `C_resp_other` and their sum `C_resp`
  (`nd-unfolding/build_cresp.py`).

**The groups** are S1's `group_of` (`nd-unfolding/s1_assemble.py:255-259`), plus two:
- `flux` = `band:Flux`;
- `detector` = GEANT_Neutron, GEANT_Pion, GEANT_Proton and MinosEfficiency;
- `lateral` = BeamAngleX, BeamAngleY, MuonResolution, Muon_Energy_MINERvA and Muon_Energy_MINOS;
- `interaction` = the other 33 bands;
- `normalization`, `stat` and `seed`;
- `C_model` = its three vertex blocks s_j s_jᵀ, from `cmodel_5d.json`'s S, as G-DIAG splits it (`nd-unfolding/fd_g_diag.py:16`, `:156`);
- `C_resp` = the four species.

"Detector response" in the decision is read as the union **DR = detector ∪ lateral ∪ C_resp**: the detector bands,
the muon and beam reconstruction, and the hadronic calorimetric response. Each group is also reported on its own.

## 2. Notation and units (fixed)

- **Relative units throughout.** Every matrix is relative to each cell: B_rel = B / (f fᵀ), with f being S1's f. P, the
  g_X, σ and every block are dimensionless fractions. M = (C_total + C_resp)/(f fᵀ), the 5B readout's metric.
- **Three inner products, each tied to one question:**
  - **Euclidean in relative units:** for the duplication bound OV, the uniform share, plane retention, and the 5A–5B
    angles. These are statements about per-cell fractional variance, the unit in which σ and the result table are
    quoted. It is G-DIAG's "relative to f" unit (`nd-unfolding/fd_g_diag.py:7-8`).
  - **Noise-weighted, with diag(σ_X)⁻²:** for identification (§3.3). The question there is whether a pattern is
    reproduced to within the offsets' own noise, so it is weighted by that noise. σ_X is the committed per-cell noise
    σ of g_X (`g_vs_5A.periods.X.g_5b_noise_sigma`). Its cell-to-cell correlations are not used: ten replicas cannot
    estimate a 16 × 16 noise matrix. This is disclosed.
  - **M-whitened:** only for the χ² bound (§6.2), since χ² lives in M.
- **Eigenvectors** are signed so that the largest-|loading| cell is positive, as G-DIAG's are.
- **Numerical zero:** a relative variance below 10⁻²⁴, as the 5B reader's Q5.

## 3. Item 1: overlap with the existing blocks

### 3.1 What the construction already rules out (an identity, tested, not measured)

Suppose a source changes every period's double ratio by the same factor (1 + ε) in a cell. Then r_X/m is unchanged and
g_X is unchanged, **exactly**. Every block of C_total + C_resp is built by applying one variation to the pooled MC
coherently, whether that is a universe, a lateral shift or a species shift. So **a source can be counted both in an
existing block and in P only through the part of its effect that differs between periods.** To first order,
g_X = ε_X − Σ_Y e_Y ε_Y.

The reader tests the identity: a planted common factor on all three periods leaves P unchanged to 10⁻¹²
(`test_a_period_common_factor_leaves_the_block_unchanged`).

**What this means for a uniform offset.** A period-dependent normalization offset, such as PB's or PC's mean, cannot be
attributed to a coherent block by its shape. Every coherent normalization-like block has a uniform shape, and none of
them can produce a period difference. Such an offset could come from the period-dependent flux, the POT, or a
playlist-dependent efficiency. Telling those apart needs each source's per-period variation.
- **The cheapest such test, a per-period flux-universe readout, is not available at 0 node-h:**
  - the per-period flux files hold the central-value TH1D only (`pTmu_reweightedflux_integrated`, read for its object
    list);
  - the per-playlist `runEventLoopMC_<pl>.root` hold an `MnvH1D` whose error bands need PlotUtils dictionaries;
  - no PlotUtils build was found under `$HOME` or `$P/MINERvA-OmniFold` (depth 5), and the root_6_28 environment
    could not stream the error bands.
  <!-- absence-ok: scoped to the find and the ROOT read named here, on login37, 2026-10-30 -->
- It is named in §11 item 4 as the test that could establish a cause, and it is not declared here.

### 3.2 The duplication bound OV (descriptive; no stop)

Write P = Σ_{i=1,2} λ_i u_i u_iᵀ, Euclidean, with unit u_i. For a group with relative block B, let b_i = u_iᵀ B u_i
be B's variance along P's mode i, which is G-DIAG's block share along a mode.

  **OV(B) = Σ_i min(λ_i, b_i) / Σ_i λ_i.**

- **What it bounds.** If B's source alone produced the period offsets, P and B would estimate the same variance along
  each u_i. The doubly counted variance along u_i is then at most min(λ_i, b_i). So OV is an upper bound on the share
  of P that duplicates B, **under the hypothesis that B's source caused the offsets.** It does not show that it did.
  §3.1 shows why a large OV is expected for any broad normalization-like block, flux included.
- **Written:** OV and the pairs (λ_i, b_i) for flux, detector, lateral, C_resp, DR, interaction, normalization,
  C_model and all of C_total + C_resp. OV is also written for P's pattern part (§3.3), which is built the same way from
  the intercept-removed offsets.
- **Tests:** a planted P = B gives OV = 1; a planted P orthogonal to B gives OV = 0; and the formula is recomputed by
  hand (`test_ov_in_both_directions`).

### 3.3 Identification of the pattern by one existing component (clause O)

**The candidates.** Every block in the partition of C_total + C_resp except stat and seed: 38 bands, 5 laterals,
normalization, the three C_model vertices and the four C_resp species.
- For each block, its Euclidean eigenvectors in relative units with λ ≥ 0.01 tr(B), at most three per block. Each is
  scaled to d = √λ v, so that d is the block's 1σ shift along that mode.
- A two-universe band or lateral, and a species, give exactly one candidate.
- The count N_cand is written.

**The fit, per candidate d and per period X ∈ {PB, PC}.** A weighted least-squares fit of g_X on the two regressors
(1, d), with weights σ_X⁻²:
- a_X is the coefficient on d, in units of d's own 1σ;
- χ²_res(1, d) is the residual at the minimum;
- χ²_res(1) is the residual with the intercept alone, which is the noise-weighted size of g_X's pattern;
- the explained share is **E_X(d) = 1 − χ²_res(1, d) / χ²_res(1)**.

The intercept is free because §3.1 shows a uniform part cannot be attributed by shape. With it free, a candidate is
judged only on the structure it adds beyond a period normalization. A candidate whose shape after the intercept has a
noise-weighted norm below 10⁻¹² of its own is written as "uniform, not identifiable by shape", with normalization
expected among them, and is excluded from O.

**Why PB and PC, not PA.** Σ_X e_X g_X = 0, so only two of the three offsets are independent. PB and PC carry the
offsets of the two smaller exposures. PA's fit is written beside them, with no role in O.

**Clause O fires** if some candidate d has **E_PB(d) ≥ 0.5 and E_PC(d) ≥ 0.5, with |a_PB| ≤ 2 and |a_PC| ≤ 2.**
- **Why these numbers:**
  - one component explaining most of both independent patterns is what identifying a source would look like at this
    precision;
  - 2σ bounds the period-dependent amplitude at twice the component's own pooled uncertainty. A larger one would mean
    that block's own size is wrong, which is a different finding from duplication;
  - the numbers are round and declared before any candidate's shape has been read. The director may bind others.
- **The look-elsewhere rate, arithmetic:** for a pattern in 15 dimensions and a random direction, the squared cosine
  is Beta(1/2, 7), and P(≥ 0.5) = 0.0022. If PB's and PC's patterns were identical, a chance firing over N_cand
  candidates is at most N_cand × 0.0022 (about 0.12 for 55), before the amplitude bound. If they were independent, it
  is about N_cand × 0.0022². The report writes this bound beside the clause, with N_cand as counted.
- **Also written, with no role in O:**
  - the three best candidates per group by min(E_PB, E_PC), with E, a and the residual against χ²₁₄'s 95 % quantile
    (23.685; corrected from χ²₁₅, §13 item 1). The residual answers whether the pattern is reproduced to within noise;
  - the same for the best pair within DR. A pair has no stop role, since pairs multiply the candidates about 1,500-fold.
- **Tests:** a planted g = 1.5 d′ + noise + a free normalization fires O; the same g at 3 d′ does not, by the amplitude
  bound; a g orthogonal to every candidate does not; a uniform candidate is excluded
  (`test_identification_fires_and_stays_silent`).

### 3.4 The noise inside P, against the stat block (descriptive)

Each period's offsets carry its own statistical noise, and the pooled stat block already carries the pooled share.
- **Under the Poisson model** (period variance s²/e_X, independent), the floor's expectation is 2k s², where s² is the
  pooled variance.
- **So the expected ratio** of the floor's σ to C_stat's is √(2k) = 1.157 (arithmetic).
- **Written:** that ratio per cell, and tr(floor)/tr(P), the share of P that is noise and so overlaps C_stat. C_stat is
  set A's 50 replicas of the (e) chain, and 5B's replicas also resample the MC and template rows, so the ratio is a
  check of the noise model, not a test.

## 4. Item 2: the noise treatment and the stability of P's size

**4.1 Replica-built blocks.** For k = 1…10, P^(k) is DESIGN §2 applied to (r_PA^(k), r_PB^(k), r_PC^(k)), where
r_X^(k) = X_X,b=k / T_X:
- the k-th replica of PA, PB and PC, from their independent seed blocks;
- each P^(k) is one joint draw of the block's estimator under the data's resampling. Its spread estimates the
  sampling spread of P's size.
- **Written:** per cell and in summary, the replicas' mean and SD of σ; the mean shift E_k[P^(k)] − P, which is the
  double-noise bias, beside the floor; and the trace share.
- **The statistic of clause N:** s_med = SD_k(median_c σ_c(P^(k))) / median_c σ_c(P). It fires at **s_med > 0.5**, when
  a replica's change moves the size by more than half of it. An SD from ten draws has a relative precision of about
  24 % (arithmetic, 1/√18), which 0.5 allows for.

**4.2 The floor and the noise expectations at ten replicas.**
- A leave-one-replica-out jackknife over k gives the SE of:
  - each cell's noise-floor σ;
  - the ratio σ(P)/σ(floor);
  - each comparison's noise E[χ²_M].
- A split-half check (replicas 1–5 against 6–10) is written beside it.
- These are descriptive.

**4.3 The noise-debiased block, a sensitivity only.** P − floor, made PSD by zeroing negative eigenvalues, with rank
≤ 2 asserted. Its per-cell σ is written over P's.
- **The block that would be added is P as constructed, not debiased,** as 2D's DESIGN §3 discloses ("does not subtract
  it, which is conservative").
- Cells with σ(P)/σ(floor) < 2 are flagged noise-dominated: R08 at 0.878 and R00 at 1.796 in the 5B report.

**4.4 Three periods, the dominant term, disclosed and not a clause.**
- The variance rests on about 1.83 effective dof (DESIGN §3). That is the Satterthwaite dof of the exposure-weighted
  spread, ν = (1 − V2)² / (V2 − 2 Σ e³ + V2²), which is 1.8244 at 5B's committed e (§13 item 2). It also gives
  DESIGN's "about 105 %" as √(2/ν).
- The 68 % interval for σ_true/σ̂ from χ²_ν at that ν is **[0.73, 2.56]** (arithmetic: 0.7339 to 2.5643).
- This depends only on e, and was known before 5B ran, so it cannot be a stop clause that any result decides. The
  report prints it beside the block, and §8.2 carries it into the block's label.
- The ten replicas test the data noise only, not this term. §11 item 3 names the test that would.

## 5. Item 3: why 5B's cell pattern differs from 5A's, while their sizes agree

### 5.1 What each construction assumes

| | 5A (projection of 2D) | 5B (per-period 5D unfolds) |
|---|---|---|
| where the offset comes from | 2D's per-period unfolds on 205 (p_T, p_∥) cells | (e)'s per-period 5D unfolds, on the 16 cells |
| its assumption about the hadronic variables | **the offset does not depend on E_avail, q3 or W inside a 2D bin** (5A label) | none: measured in 5D |
| its estimator and regularization | 2D's unfold and prior; each period pulled toward its own prior at 2D's iterations (DESIGN §3) | (e): config R, 5 iterations, seed 42; each period pulled toward its own 5D prior |
| its weighting onto the cells | the (e) central value's fine-cell content | none: integrated by S1's rule |
| its noise | 2D's bootstrap and seed noise, which the 5B report does not reference | ten bootstrap replicas per period; no seed term for (e) |
| its inputs | 2D's production chain | MP-1's zero loops: K1 and K2 bitwise MP-1's chain, K3 within τ of f |
| shared | the three flux-file periods, the same e and k, the exchangeable-offset model, a block built from the observed offsets | |

### 5.2 The hypotheses the measurements separate

- **H-a:** both sizes are dominated by a common per-period mean offset, which both constructions see, while the
  patterns about that mean differ.
- **H-b:** the offset depends on the hadronic variables inside a 2D bin, so 5A's assumption fails.
- **H-c:** the difference is within the combined noise. 5A's noise is not in the reported |Δ|/σ.
- **H-d:** the 2D and 5D estimators shrink the offsets differently, by regularization or prior pull.

### 5.3 The measurements

**(3a) Uniform share, for H-a.** With ū = 1/4 · (1, …, 1), the share is U(P) = ūᵀ P ū / tr P, for P_5B and for
P_5A = `variants.central.C_PL16_rel`. Also written:
- each period's cell-mean offset ḡ_X under 5A and 5B;
- the Euclidean correlation of the two constructions' patterns g_X − ḡ_X 1;
- the trace of each block with its uniform part removed.

H-a is supported if both U are large, the ḡ_X agree, and the pattern correlation is low. "Large" is not given a
threshold: no clause rides on it.

**(3b) 5A's noise, for H-c.** The reader projects 2D's per-period noise through 5A's own projection, with the central
weighting and 5A's code path in `nd-unfolding/fd_ct_readers.py`:
- per replica, d_X,k = x_X,b=k / x_X,s42 − 1 on the 205 cells;
- the seed term (x_X,s43 / x_X,s42 − 1)/√2, as DESIGN §4;
- the noise-only offsets d_X,k − Σ_Y e_Y d_Y,k, projected onto the 16 cells;
- σ_5A,X per cell, from the bootstrap and seed terms summed.

Then |Δ_X| / √(σ_5A,X² + σ_5B,X²) per cell, with its median, and the noise-weighted Σ_c of its square.
- **Control:** on the 205 cells, the reader's draws must reproduce 2D's committed bootstrap noise share,
  `report.noise_share.boot.median_cell_variance_share` = 0.08403191962585571, to 10⁻⁹. Otherwise exit 1, nothing
  written.

**(3c) An E_avail contrast, for H-b, POST HOC.** This contrast was chosen after seeing that R00 and R08 differ in the
5B table, and is labelled so in the readout. The cells, by their boxes in the definition:
- low E_avail {R00, R04, R08, R12}, with E_avail < 0.8 GeV;
- high E_avail {R02, R03, R06, R07, R10, R11, R15}, with E_avail ≥ 0.8 GeV;
- unrestricted, the q3 ≥ 2 cells {R01, R05, R09, R13, R14}.

Written, within each p_∥ half: the mean Δ_X of the low cells minus that of the high cells, and its combined-noise σ.

**(3d) The two planes.** The principal angles between span(P_5A) and span(P_5B). Also, the share of each g_5A,X
outside 5B's plane, and of each g_5B,X outside 5A's: ‖(I − Π)g‖² / ‖g‖². This is shared with §6.3.

**H-d is not measured.** It needs 5B's unfolds at another iteration count (§11 item 2).
<!-- absence-ok: a scoping statement about this audit's own method; 5B ran each period at 5 iterations only (FD-CT-5B-DECLARATION.md section 2) -->


### 5.4 Why item 3 carries no stop clause

5B is the direct measurement on the cells, and needs no assumption about the hadronic variables. So the outcomes
change only the block's label:
- if the pattern difference is noise (H-c), the two constructions agree;
- if it is H-b, 5A's assumption fails and 5B is the block that measures it;
- if it is H-d, a 5D shrinkage would make P too small in the shrunk cells, not too large.

None of these makes the addition overstate the uncertainty relative to omitting the block. So none stops it. The
readout carries the explanation that the measurements support, among H-a to H-c.

## 6. Item 4: what the rank-two construction can and cannot represent

### 6.1 What it represents, and what it cannot (the algebra, tested)

**It represents** variance in the two-dimensional plane spanned by the observed offsets g_PA, g_PB and g_PC (span(P),
since Σ e_X g_X = 0). Within the plane, each mode is fully correlated across cells.

**It cannot represent:**
1. any offset pattern outside that plane: a period effect with another shape, a fourth period, or future data;
2. uncertainty in the patterns themselves. The shapes are taken as known, and only their amplitude is uncertain, on
   about 1.83 dof (§4.4);
3. period-common effects, which cancel exactly (§3.1);
4. structure finer than the three flux-file groups, such as differences among the playlists within a group;
5. independent cell-to-cell scatter. A noise-like truth would be assigned to two fully correlated modes, which changes
   χ² only along them.

Tests:
- the block's column space equals span{g_X} (`test_rank_two_span`);
- the first-order reference bound of DESIGN §4 is recomputed on the 16 cells (`test_reference_bound`).

### 6.2 The largest χ² change it can cause (computed from P and M only)

Let λ̃_1 ≥ λ̃_2 be the eigenvalues of M^(−1/2) P M^(−1/2). Then for every vector v,
χ²_{M+P}(v) ≥ χ²_M(v) / (1 + λ̃_1) (Woodbury). So **no comparison's χ² can fall by more than the fraction
λ̃_1/(1 + λ̃_1),** and the change is confined to the plane.
- **Written:** λ̃_1, λ̃_2 and that fraction.
- **No prediction is read.** This bounds every Stage G χ² before any is recomputed. That matters because the block is
  post-read (addendum §5.4).
- **Test:** a planted v along the top whitened mode attains the bound.

### 6.3 Whether the plane is stable under the data's noise (clause R)

Π is the Euclidean projector onto span(P). For each replica-built P^(k) (§4.1), the plane retention is

  **R_k = tr(Π P^(k)) / tr(P^(k)),**

the share of the replica block's variance that lies in the observed block's plane.
- **Written:** the R_k, their median, and the principal angles between span(P) and span(P^(k)).
- **Clause R fires** if **median_k R_k < 0.5**. The block's correlation shape would then be set by the noise rather
  than by the offsets, and a rank-two block would impose spurious correlations.
- **Tests:** planted replicas whose plane is rotated 90° fire R; replicas with small noise do not
  (`test_plane_retention_in_both_directions`).

## 7. THE STOP CONDITION

Fixed in this record before any audit number is read. The reader writes one verdict, and nothing else decides it.

**`stop` = O ∨ N ∨ R:**
- **O** (§3.3): ∃ candidate d with E_PB(d) ≥ 0.5, E_PC(d) ≥ 0.5, |a_PB| ≤ 2 and |a_PC| ≤ 2;
- **N** (§4.1): s_med > 0.5;
- **R** (§6.3): median_k R_k < 0.5.

**Readout fields:** `stop_condition{O, N, R, stop, which}`, each clause with its statistic, threshold and the candidate
or replicas that decided it.

**Controls that leave the condition undecided** (exit 1, nothing written):
- any pin;
- the reader's P, rebuilt from the seed-42 unfolds and truths, differs from the committed `C_PL5D_rel` by more than
  10⁻¹², relative to its largest entry;
- its floor differs from the committed `noise_floor_sigma_rel` by more than 10⁻¹²;
- its σ_M differs from the committed `sigma_rel_M` by more than 10⁻¹²;
- the blocks do not sum to C_total + C_resp to 10⁻¹², as G-DIAG's D6;
- the 2D noise-share control of §5.3 fails;
- the leak guard refuses (exit 3).

The block is not added while the condition is undecided. A rerun needs the director.

**What follows each outcome:**
- **`stop` false:** the block is added, as §8 states, by its own declared step. The results are published with and
  without it, and the record says the decision followed the data, as decision item 2 requires.
- **`stop` true:** the block is not added. The report names the clause and its decider, with no repair, and the next
  step is Joseph's through the director. An O firing would name a candidate source, so a likely next question is
  whether that component's size, rather than an unexplained block, should carry the period dependence. That question
  is not this audit's.

**What the condition does not use:** any generator χ², any comparison of the data with a prediction, OV, the 5A
comparison, or the three-period interval. The reasons are in §3.2, §5.4 and §4.4.

## 8. The revised covariance, and every product it would flow into

### 8.1 The matrix, exactly

**C_rep,PL = C_e + C_model_abs + C_resp + C_PL,5D,abs,** in S1's absolute units (cm²/nucleon)², on R00–R15, where:
- C_e, C_model_abs and f are `s1_assembly.npz`'s (`db000707…`), and C_resp is `cresp.npz` key `C_resp` (`4d8b5797…`).
  Equivalently, `cresp.npz` key `C_total_resp` + C_PL,5D,abs;
- **(C_PL,5D,abs)_ij = f_i f_j P_ij,** with P being `C_PL5D.C_PL5D_rel` of `fd_ct_5b_periods.json` (`a5b17895…`),
  byte-pinned, not rebuilt. It is undebiased (§4.3) and of rank 2;
- in relative units, M′ = M + P. It is full rank, since M is and P ⪰ 0;
- **name:** "C_total + C_resp + C_PL,5D". For a prediction g, Stage G's matrix becomes C_total + C_resp + C_PL,5D + V_g.

### 8.2 Its label

The block's label is 5B's NOT CITABLE FOR, plus:
- "audited (FD-CT-5B-AUDIT-REPORT.md); added after the data were seen; published with and without";
- the three-period interval [0.73, 2.56] on its σ;
- the noise-dominated cells (§4.3).

### 8.3 The products it would flow into (the addition's own declared step, not this audit)

**Search:** `C_total_resp`, `cresp.npz`, `4d8b5797` and `C_total_plus_C_resp` over `nd-unfolding/`,
`docs/analysis-note/` and `docs/orchestration/state/`, at `91a27ad1b`. Each consumer is below.

**(A) Recomputed, with and without the block, each labelled with its matrix.** These are the decision's "result table,
the generator χ², and the F1 and flux-bootstrap readouts":
1. **The data product:** `nd-unfolding/fd_data_product.py`, which writes the reported matrix (`C_total_plus_C_resp`),
   its correlation matrix and the relative σ;
2. **The deposit candidate:** `nd-unfolding/fd_deposit_candidate.py`, which writes `covariance.csv` and
   `deposit.json` from the data product;
3. **The result table in the note and the paper:**
   - `docs/analysis-note/make_values_fived16.py` → `values_fived16.tex`, which gains a C_PL,5D row in the breakdown;
   - `docs/analysis-note/make_supplemental.py`;
   - the Stage F tools that read the matrix by name or digest: `2d-closeout/stageF/methods/fived16/tools/paper_blocks.py`,
     `build_chapter.py` and `apply_framing.py`; `note-n4/compose_f.py`; `r19/tools/apply_b3.py`;
     `r22/step2/check_ledger.py`;
   - the prose in `sec_fived16.tex`, `sec_systematics.tex`, `paper_body.tex` and `sec_execsummary.tex`;
4. **Stage G:**
   - `nd-unfolding/fd_g_compare.py` → `fd/readout/fd_g_readout.json`. The reported comparison moves to
     C_total + C_resp + C_PL,5D + V_g, with C_total + C_resp + V_g written beside it as the variant without the block;
   - G-DIAG (`fd_g_diag.py` → `fd_g_diag_readout.json`);
   - G-FOLLOWUP and G-SENS2 (`fd_g_followup.py` → `fd_g_followup_readout.json`, `fd_g_sens2_readout.json`);
   - the figures' error bars (`fd_g_figures.py`, which now checks σ² = σ(C_total)² + σ(C_resp)², and
     `fd_g_figures_check.py`);
5. **F1 and F0b:** `nd-unfolding/fd_f0_regrade.py --extra-block`, giving `fd_f1_readout.json` and
   `fd_f0b_readout.json`, graded against the reported matrix. F0's grades against C_total alone are unaffected;
6. **The flux bootstrap:** `nd-unfolding/fd_flux_boot.py` → `fd_flux_boot_readout.json`, whose matrix is
   C_total + C_resp + (C − C_0) + V_g.

**(B) Readouts that use M only as a metric for descriptive distances.** These are 3a (`fd_ct_chi2.json`), 4C
(`fd_ct_mismatch.json`), 3b (`fd_ct_recoil.json`), 5A (`fd_ct_period.json`) and 5B (`fd_ct_5b_periods.json`).
- **Recommended:** they stay as written, labelled "in M, without C_PL,5D".
- 5B's χ² and σ ratios in particular must stay in M, since measuring the periods in a metric that contains their own
  offsets would be circular.
- The director rules (§11 item 6).

**(C) Not recomputed:**
- 1B's coverage test uses the covariance as it stands when 1B is declared (decision item 3);
- the 2D result and its Q;
- κ.

**(D) Downstream of (A):**
- the paper and the note, through the usual truth and register checks: the claims register
  `docs/publication/CLAIMS-20261005-claim-to-evidence.md` and the note's build;
- the standalone `MINERvA-OmniFold-Analysis-Note` repository, synced by the director;
- the HPSS copy of the new matrix, by hashverify and retrieval, as for `cresp.npz`.

## 9. Controls and tests

**The reader** is `nd-unfolding/fd_ct_5b_audit.py`, a login reader. It imports, unchanged:
- `fd_ct_periods` (`receipt`, `unfold`, `unf_path`, `guarded`, `cell_sets_problems`, the seed blocks);
- `fd_ct_readers` (`common`, `footprint`, `write`, the 2D grid);
- `fd_f0_regrade` (`LeakGuard`, `Stop`, `report`, `require`).

**Leak guard.** Its table holds f and every 5B period unfold's and MC truth's cell integrals, each within LEAK_REL of f
dropped (`fd_ct_periods.guarded`). Every written number is relative to the cells' own values, or a ratio of relative
quantities. 2D's absolute values are not in the table (§13 item 4).

**Refusals.** It refuses an existing output, and every control in §7 and §13 item 3 refuses with nothing written.

**The tests,** `nd-unfolding/tests/test_fd_ct_5b_audit.py`: 48 tests, 2 of them ROOT-only. They run on synthetic
trees built by the 5B and readers' fixtures. The 5B periods readout in each tree is made by `fd_ct_periods` itself,
and 5A's readout by `fd_ct_readers period`. 2D's draws are planted through `load_2d`.

| declared item | test(s) |
|---|---|
| §3.1 the identity | `test_a_period_common_factor_leaves_the_block_unchanged` (also: a period-dependent factor is not cancelled) |
| §3.2 OV | `test_ov_in_both_directions` |
| §3.3 identification and O | `test_identification_by_hand`, `test_o_fires_and_stays_silent`, `test_the_clauses_at_their_thresholds`, `test_a_uniform_candidate_has_no_shape`; end to end, `test_o_fires_on_a_planted_detector_pattern` and `test_o_stays_silent_beyond_the_amplitude_bound` |
| §3.3 the look-elsewhere constant | `test_the_beta_tail_by_integration` |
| §4.1 N | `test_n_fires_when_the_replica_blocks_size_is_unstable`, `test_n_and_r_stay_silent_on_small_noise`, `test_n_is_silent_when_the_noise_is_as_large_as_the_offsets` (§13 item 5), and the boundaries |
| §4.4 ν and the interval | `test_nu_eff_and_the_interval` |
| §6.1 rank two | `test_rank_two_span`; the reference bound in `test_runs_and_is_recomputed_by_hand` |
| §6.2 the χ² bound | `test_the_chi2_bound_is_attained_along_the_top_mode` |
| §6.3 R | `test_r_fires_alone_on_a_rotated_plane`, `test_n_and_r_stay_silent_on_small_noise`, and the boundaries |
| §7 the decision | `test_the_clauses_at_their_thresholds` |
| §7 and §13 item 3 controls | `Refusals`: 19 tests, one per control, each by its message on a FAIL line, with nothing written |
| the written statistics | `HandChecks` (7 tests, each by its own route) and `test_runs_and_is_recomputed_by_hand`: s_med, R_k, 5A's σ, the uniform share, the E_avail contrast, the debiased block, the look-elsewhere and √(2k) numbers, the candidate set |
| the leak guard | `test_a_planted_leak_is_refused` (a 5B unfold's absolute integrals) |
| `load_2d` | `RootLoader`, 2 tests (cluster only): x and t against the formula by hand; another grid refuses |

**Mutation receipt:** `fd/receipts-ct/5b/audit/mutants_5b_audit.{py,log}`. Its 46 mutants cover every clause's
threshold, comparison and operand, the statistics behind the clauses, each refusing control, and the guard's table.

**Review:** an independent, read-only review in its own detached worktree, given the code and this record. Its
report and probes are kept under `fd/receipts-ct/5b/audit/review/`, and its findings are dispositioned in §13.

## 10. Order, cost, platform and storage

**The order:**
1. this declaration, with its code, bound once;
2. a deploy at the bound pin (§10.1);
3. the reader on a login node, once (§10.2);
4. `FD-CT-5B-AUDIT-REPORT.md` as a PR to the director, with the verdict and every number beside its reference.

### 10.1 Deploy and tests (login node)

`BA=$P/fd-ct-5b-audit-<date>`, which must not exist beforehand, and `D=$BA/deploy/<pin8>`. The deploy is as 5B's
`fd/receipts-ct/5b/run/s1_deploy.sh`, with:
- this record's digest list (§14);
- the test modules `test_fd_ct_5b_audit test_fd_ct_periods test_fd_ct_readers`, run with root_6_28 activated by
  prefix (the conda hook, then `conda activate`, with no `set -u`).

**It must show:** HEAD equal to the pin; 0 porcelain lines before and after; the §14 digests; and `tests rc=0` with
"Ran … tests … OK" and no skip, so that `RootLoader` and the 5B and readers' ROOT tests run.

### 10.2 The run (login node, after §10.1)

```bash
mkdir -p $BA/tmp $BA/logs && cd $BA && eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)" \
  && conda activate $HOME/.conda/envs/root_6_28 && TMPDIR=$BA/tmp timeout 1200 env -u PYTHONPATH python3 -I -B \
  $D/nd-unfolding/fd_ct_5b_audit.py \
  --definition $D/nd-unfolding/pv-ladder/readouts/h2_definition.json \
  --s1-npz $P/s1-20261024/s1_assembly.npz --cresp $P/cresp-20261026/out/cresp.npz \
  --cmodel-json $D/nd-unfolding/pv-ladder/readouts/cmodel_5d.json --b5 $P/fd-ct-5b-20261030 \
  --readout-5b $D/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/readout/fd_ct_5b_periods.json \
  --readout-5a $D/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/readout/fd_ct_period.json \
  --playlist-npz $P/tmp-playlist-term-20261016/out/playlist_term.npz \
  --playlist-json $D/docs/orchestration/state/2d-closeout/playlist-term/outputs/playlist_term.json \
  --analysis-2d $D/docs/orchestration/state/2d-closeout/period-unfold-20261014/outputs/analysis.json \
  --central $P/s5p-20260926/runs/s2/num/data/data_b-_j-.npz \
  --out-json $BA/fd_ct_5b_audit.json > $BA/logs/audit.out 2> $BA/logs/audit.err; echo "rc=$?" >> $BA/logs/audit.out
```

- **Exit codes:** 0 written; 1 a refused control, with nothing written and the condition undecided; 2 argparse; 3 the
  leak guard; 124 the timeout.
- **The paths:** the 5A inputs are the ones 5A's run read (`fd_ct_period.json` `argv`), and the 5B run directory is
  the one 5B's read (`fd_ct_5b_periods.json` `argv`). The 2D draws are the absolute paths in `analysis.json` `_roles`.
- **Committed in the report's PR:** the readout as `fd/readout/fd_ct_5b_audit.json`; the logs and step scripts under
  `fd/receipts-ct/5b/audit/run/`; a ledger row.

**Cost and platform:**
- 0 node-h, with no Slurm job;
- CPU only. (3b) reads 2D's `xsec.root` files (`hXSec2D`, as `2d-closeout/playlist-term/scripts/playlist_term.py:107-111`), so the reader runs with root_6_28 activated by prefix, as the 5B tests did;
- nothing goes to CFS. `playlist_term.npz` is read from its pscratch copy, as 5A's.

**Storage:**
- the audit's run directory joins the pscratch retention list;
- **risk:** 2D's 37 per-period unfold directories, `$P/2d-closeout-period-unfold-20261014/out/`, have no HPSS copy
  on record. They have been on pscratch since 2026-10-14. If they are purged before the run, (3b) stops at its control,
  and the report says so.
  <!-- absence-ok: scoped to the HPSS records named in the 5A and period-unfold reports -->

## 11. For the director

1. **The thresholds** (0.5, 0.5, 0.5 and 2σ) are round and declared blind to every audit number. Bind them or others.
   **Not proposed:** a stop on OV. OV ≥ 0.5 is expected for any broad normalization-like block (§3.1–3.2), so as a
   clause it would fire on geometry that cannot produce a period difference.
2. **Optional, not declared:** H-d, by 5B's period unfolds at a second iteration count. That is 3 period unfolds and
   ALL, CPU, about 0.1 node-h on the 5B unit (0.0226 node-h each, arithmetic), on the retained `$B5` dumps. It needs
   its own declaration.
3. **Optional, not declared:** the three-period term. Splitting the periods finer, within the flux-file groups (for
   example 1A–1C and 1D–1F), would add dof to the block's variance. That means new merges, dumps and unfolds at a
   similar per-unit cost, and its own declaration.
4. **Not available at 0 node-h:** a per-period flux-universe readout, which could attribute the uniform offsets to the
   flux or exclude it (§3.1). It needs PlotUtils, or per-period universe loops.
5. **Code in a second step: ruled.** On 2026-10-30 the director chose to bind once, with the code in this PR.
6. **Readouts in (B)** (§8.3): they stay in M, as recommended, or you rule otherwise.

## 13. What writing the code corrected, added or found

None of these changes a threshold of O, N or R, or what any clause measures. The director is told of each.

1. **Corrected: the residual's quantile (§3.3).** A fit of two parameters on 16 cells leaves 14 dof, so the residual is
   compared with χ²₁₄'s 95 % quantile, 23.685, not χ²₁₅'s 24.996. It has no stop role.
2. **Made exact: ν_eff (§4.4).** DESIGN's "about 1.83" is the Satterthwaite dof ν = (tr A)² / tr(A²), with
   A = diag(e) − e eᵀ. That is 1.8244 at 5B's committed e, and it gives DESIGN's 105 % as √(2/ν). The interval is
   unchanged at two decimals.
3. **Added: refusing controls beyond §7's list.** Each makes the reader refuse more often, and none changes a
   statistic:
   - A1: every 5B unfold and check receipt at the digest the 5B readout records; the unfold directories hold exactly
     the declared 11 files; each MC truth is `s5p_mc_truth_pred`'s of its own period's npz; every integral positive;
   - A2: S1 has 38 bands, 5 laterals, normalization, stat and seed; C_e is the sum of S1's blocks; C_model's vertices
     reproduce `C_model_frac` and `C_model_abs`; the blocks, vertices and species sum to M (an identity of the others);
   - A3: every 2D draw at its `analysis.json` digest; 2D's seed-42 r = x/t equals `playlist_term.npz`'s r_X; the
     central value integrates to f; 5A's g, reprojected through `footprint`, equals the committed 5A readout's;
   - S: the E_avail cell sets of (3c) are the definition's boxes;
   - assertions: A4, P's column space is span{g_X} (§6.1); A5, P − floor has at most two positive eigenvalues (Weyl).
4. **Corrected: the leak guard's table (§9).** It holds the 5B integrals only. 2D's values are on another grid (205
   cells, against the guard's 16) and in other units. No 2D absolute value, or ratio to one, is written; only the
   draws' fractional fluctuations are, projected onto the cells.
5. **Found: clause N's power.** In a synthetic test, replica noise as large as the offsets themselves (5 % per cell)
   gives s_med = 0.39, and N does not fire. That is because such noise inflates every replica block alike. N fires
   when the replica blocks' size is itself unstable (`test_n_fires_when_the_replica_blocks_size_is_unstable`). The
   threshold is unchanged, as the director ruled, and the test that records this is kept.
6. **Corrected: 5A's noise is on double ratios (§5.3, 3b).** It is d = (x/t)_b / (x/t)_s42 − 1, as 2D's own
   construction has it (`2d-closeout/playlist-term/scripts/playlist_term.py:201-205`), not x_b / x_s42 − 1 as §5.3
   wrote. The two are equal only if 2D's bootstrap leaves t unchanged. A3 reproduces 2D's committed noise share in this
   form.
7. **Chosen: 2D's loader is retyped, not imported.** `analyze_periods.py` puts cluster paths at `sys.path[0]` on
   import (`2d-closeout/period-unfold-20261014/scripts/analyze_periods.py:46-51`), the OI-136 hazard. So `load_2d`
   repeats its `load()` formula, in its operation order. Two guards check it: `RootLoader` tests it against the formula
   on a synthetic ROOT file, and A3's r check compares it on the real files with r as `analyze_periods.load` made it.
8. **Chosen: where §3–§6 were ambiguous** (review L5):
   - the 1 % candidate cut is λ ≥ 0.01 tr(B);
   - a candidate is uniform if its shape is below 10⁻¹² under either PB's or PC's weights;
   - OV's pattern part uses each offset's Euclidean cell mean, as (3a) does;
   - N's SD uses ddof = 1;
   - (3c)'s σ assumes independent cells;
   - §4.1's mean shift is written as diag(E_k P^(k)) − diag(P), beside diag(floor).
9. **Applied: §2's numerical zero in OV.** A block variance below 10⁻²⁴ along a mode of P is written as 0. Without it, an
   exactly uniform block against P's pattern part leaves residue of order 10⁻³⁶, which the guard's 10⁻³⁰ floor refuses
   (review L2).
10. **Test names.** §9's table supersedes the test names given in §3–§6.

### The review, and what was done

The review is kept verbatim as `fd/receipts-ct/5b/audit/review/REVIEW.txt`, with its five probes and their logs. It
found no defect that would make the stop verdict wrong on real inputs.
- **M1, the planted-leak test never reached the guard's table:** it now plants a ratio to f, which only the table
  refuses. The mutant "guard: no integrals" is killed.
- **M2, controls without a refusing test:** the floor, σ_M, the exposure shares, the A0 schema and the A4 span now
  each have one. A5 cannot fire on PSD inputs, and is kept as an assertion that guards the code.
- **M3, missing tests and unchecked statistics:** `HandChecks` recomputes by its own route:
  - the reference bound and the χ² bound;
  - the jackknife and split halves;
  - OV on every group and on the pattern;
  - the candidate population and the best pair;
  - the noise against stat;
  - the plane angles and the pattern correlations;
  - the mean shift.
- **M4 and M5:** named, as items 1 and 4.
- **L1, L2 and L5:** items 6, 9 and 8.
- **L3, A1's 10⁻¹² margin:** A1 rebuilds with 5B's own code in 5B's environment (root_6_28, numpy 1.26.4), where
  the rebuild is bitwise. Under another summation order the review measured up to 3.4 × 10⁻¹³. A failure would be a
  refusal, not a wrong verdict.
- **L4:** the 5B receipts are now compared with the 5B readout's. 2D's seed share is not added as a control, since the
  bootstrap share already reproduces the chain. The output path is the argv of §10.2.
- **L6:** the interval is tested at its values; OV and the candidate count are recomputed by hand; `HandChecks` builds
  its own bases with numpy.
- **L7:** item 5.

### Mutation passes

- **Pass 1** (`mutants_5b_audit-pass1.log`, at `93642cdd`): 41 of 46 killed. The five survivors were test gaps, each
  also found by the review:
  - R's stop;
  - the DR group's composition;
  - two refusals matched on a PASS line;
  - the guard's table.

  The tests were fixed, not the thresholds.
- **Pass 2** (`mutants_5b_audit.log`, at `5ea379b4`): **54 of 54 killed**, none unapplied, and the file restored to its pinned digest.

## 14. Pinned bytes

At this declaration's commit:

| file | sha256 |
|---|---|
| `nd-unfolding/fd_ct_5b_audit.py` | `d969d1ffbd06fec7254db029a5785080d4bd28613a3a9763fab5face99a8cdb6` |
| `nd-unfolding/tests/test_fd_ct_5b_audit.py` | `bd5f1f321a38b2098f4dfb822b54e3581ce11235cb7da11d58a421422920b627` |
| `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ct/5b/audit/mutants_5b_audit.py` | `0206b2d3579f396c908e17c64e2a57d6653b495ccc032b2cfbedf6ea3c207574` |
| `nd-unfolding/fd_ct_periods.py` | `ec6bc7f5b292195c7b3488ad9903c2ad7a5dc22746349e7c3fbb9737e283ed3e` (unchanged from main) |
| `nd-unfolding/fd_ct_readers.py` | `f4cc51c8fdba141b4ae3e289ee983d755c0cd5b90a82d40fe71d2e56a4447464` (unchanged from main) |
| `nd-unfolding/fd_f0_regrade.py` | `0dfa722c2b74abed09fb255ccb7c0e80e6c55eb922ea1326dd74e6c880697aa2` (unchanged from main) |
| `nd-unfolding/s1_assemble.py` | `b157250af21a2ef74e4164db6009a40ac596e225f33ac655475798ef49f613f7` (unchanged from main) |
| `nd-unfolding/s5p_stage1_inspect.py` | `26569afc0da46f21167e0908014712cd800c1e14ac63a4b245a0b493c76d3d71` (unchanged from main) |
| `nd-unfolding/fd_ct_period_inputs.py` | `4d005f265ea6abf4ee7cfec988fe7c06553556ca7984387929f77409dfc244b1` (unchanged from main) |
| `nd-unfolding/s5p_mc_truth_pred.py` | `e4518d0a75c82c7c232ec079e715d47a64111222e15fa60ac9d1ecec9265ddb5` (unchanged from main) |
| `nd-unfolding/s5p_numerics.py` | `7ad8ca0f73989128b783b59d55670687c293d186b2643ea799a3e67c047bf185` (unchanged from main) |
| `nd-unfolding/tests/test_fd_ct_periods.py` | `933c740d93f03e524906f161d2c4ee8e11a69bdd114cedd210832cbd1eb78d60` (unchanged from main) |
| `nd-unfolding/tests/test_fd_ct_readers.py` | `6ca4172937351ff60b8c5611403c0e519b2dbb6ae10a789baf8f578121a543a6` (unchanged from main) |
| `nd-unfolding/pv-ladder/readouts/h2_definition.json` | `b67907615fe2e903e60ae6caa1c141fa007676c0a1b3ae9f42490d331bfdda89` (unchanged from main) |
| `nd-unfolding/pv-ladder/readouts/cmodel_5d.json` | `3cfdc6a5b8c6cea5f99b4678e27f6ca5f7973ee57a79b9d139798f0751cfcd60` (unchanged from main) |
| `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/readout/fd_ct_5b_periods.json` | `a5b17895b1189543d773e94717e14cd9b1409535e366c96788f94bf6f40759db` (unchanged from main) |
| `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/readout/fd_ct_period.json` | `d7d518ac20acd90d9d411dbd1353c509e734e8588b6bc3965ae5f14cf9303728` (unchanged from main) |
| `docs/orchestration/state/2d-closeout/playlist-term/outputs/playlist_term.json` | `5b023478eb5825a298fd3e851b614fd4780ab27b927214e253f5c4c0df52f7b9` (unchanged from main) |
| `docs/orchestration/state/2d-closeout/period-unfold-20261014/outputs/analysis.json` | `05edff61673fed987f487f8c19ad25ec055db8118491815b9c263f3a7c3de72b` (unchanged from main) |

**Locally,** the audit's, 5B's and the readers' test modules ran 210 tests, OK, with 4 skipped: the ROOT-only tests
(`test_fd_ct_5b_audit` 2, `test_fd_ct_periods` 2). The deploy must run them with none skipped (§10.1).

## 12. Not changed

- every covariance, cell, readout and κ, and the reported matrix C_total + C_resp;
- the 5B and 5A readers and readouts;
- `docs/analysis-note/**` by hand;
- claims, KI-85 and publication, which are Joseph's.

Nothing is submitted, deposited or tagged.
