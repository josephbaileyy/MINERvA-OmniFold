# RECORD 1B gate-D pre-check: the per-cell, per-band attribution from committed readouts (2026-11-06)

**By** the `limitation-resolver` lane, for the director. This is Part 0 of the director's 2026-11-06 scope ruling on the
coverage pre-check diagnosis (`DECISION-20261106-joseph-diagnoses-jinst-corrections.md`, item 1.2). It cost 0 node-h.
It assembles five committed readouts and adds no measurement.

**CITABLE FOR:**
- where the methods draft's pre-check numbers come from (§1);
- which mechanism each committed record tested, what it ruled out, and what it cannot support (§2);
- the per-cell split of gate D's 11 failing cells by group, and each band's class in each cell (§3, §4);
- the two harness checks, cell by cell (§5): the toys reproduce the response-only block moved in the MC (I2's F_src),
  and full-universe pseudo-data reproduce S1's own universe block at the nominal truth (stage 0's κ). Both are inside
  [0.9, 1.1] in all 16 cells, for the interaction group;
- what stays open (§6).

**NOT CITABLE FOR:**
- any statement about the coverage of the reported intervals, in either direction;
- that S1's interaction block, or the response-only block, is the right one for the reported intervals;
- any harness statement about the flux or detector groups, which neither harness check covers;
- that S1's universe holds the response part plus a prior part: additivity fails (I2 §4.3), so "F_prior" names the
  ratio √(B/A), which involves no prior;
- why A and B differ, or how the additivity residual divides;
- a band's class read alone as its importance. A ratio against a small block can sit far from 1 and carry almost
  nothing; §4 gives each band's summed term beside its classes.

Gate D's FAIL, the diagnosis's NOT LOCALIZED, I0's H2 REJECTED, I2's H1 → O1 and stage 0's rule K PASS all stand.

## 1. The source of the draft's numbers

The methods draft (`paper_body.tex:241` @ `0de103f7`) and the note (`sec_fived16.tex:253` @ `0de103f7`) render them from
the `cov1b-*` keys. Those come from `make_values_fived16.py:56–57` and `:1020–1028` @ `869dc269`, which assert both
digests.

| the draft's number | the record | where |
|---|---|---|
| ratio outside 0.9–1.1 in 11 of 16 cells | `fd/receipts-1b/stage2/run/score/gate-d.json` (sha256 `e1838c0a…`) | `"rho"` at :35, `"window"` at :53, `"verdict": "FAIL"` at :113 |
| range 0.70–2.30 | the same `rho`: min 0.696 (R07), max 2.296 (R08) | :35 |
| any three or fewer of the 38 bands does not repair it | `fd/receipts-1b/diag/diag.json` (`6fd6669e…`) | `"k_max": 3` at :40; `L1_named_bands` FAIL, `n_sets` 0, at :2947–2950 |

These are the **original 1B's gate D** (stage 2, `FD-1B-STAGE2-REPORT.md`). The staged campaign on
`decl/1b-staged-a2-1-20261103` reached no σ-ratio gate.

**Gate D stated its own prediction.** `gate-d.json:114–115` @ `869dc269`:
- `what_it_measures`: "how far the fixed-truth mechanics (response only, truth kept in every fine cell) reproduce S1's
  blocks (prior and response): the first-order prior-part gap";
- `stop`: "STOP before any coverage toy: the control would be predicted to fail by construction".

## 2. What each record tested

The objects, as the records define them. All are diagonal entries in the 16 reporting cells.
- **M** is S1's drawn block at the data.
- **E** is the toys' block: S1's estimator on the noise-free fixed-truth derivation unfolds, carried by g = f / x_T
  (`FD-1B-STAGE2-REPORT.md:115–121`).
- **A** is S1's whole universe at the nominal truth, **B** the response alone moved in the MC, and **C** the fine-cell
  prior alone (`FD-1B-INV-DECLARATION.md:225–229`).
- **Dnom** is full-universe pseudo-data at the nominal truth, unfolded with the nominal simulation
  (`FD-1B-MODED-DECLARATION.md:57–61`), and A_unc = A / g².

Every citation below is @ `869dc269`; the reports are in `state/measurement-paper/5d-community-20261024/`.

| record | what it tested | what it ruled out, or found | CANNOT SUPPORT |
|---|---|---|---|
| **Gate D**, stage 2 (#622 series; `FD-1B-STAGE2-REPORT.md:109–150`) | ρ_c = √(E_d/M_d) per cell, and per group | FAIL: 11 of 16 cells outside [0.9, 1.1]. Stat, normalization and lateral blocks enter both sides unchanged (:119), so they contribute nothing to ρ_c² − 1 | coverage, either direction (:15–17); why the ratios depart from 1 (:162–163) |
| **DIAG** (#633; `FD-1B-DIAG-REPORT.md`) | whether at most 3 named bands, or the carry, account for every cell | NOT LOCALIZED (:10). ρ_c² − 1 = Σ_b (E_b − M_b)/M_d exactly (:45). R08 and R07 cannot close with any 3 bands even alone (:50–54) | coverage (:17–19); no mechanism is asserted or tested (:112) |
| **I0** (#645; `FD-1B-INV-I0-REPORT.md`) | H2: whether the departures are noise against the measured floor | **noise ruled out**: H2 REJECTED in all 11 failing cells (:10). Removing every noise-consistent term moves ρ_c² by at most 0.029 (:92–94) | which mechanism carries the mismatch; coverage (:17–19) |
| **I2** (#650; `FD-1B-INV-I2-REPORT.md`) | the interaction group's √(E/M) = F_src · F_prior · F_truth, at the nominal truth | **harness ruled out for the interaction group**: F_src = √(E/B) is 0.986–1.015 in every cell (:200). The departure is B against A: F_prior = √(B/A) is the dominant same-side factor in 14 of 15 cells (H1 → O1, :11–15). A ≠ B + C (:18–26) | that S1's universe is the response plus a prior part; why A and B differ; which block is right; R00 and R05, where flux carries part; coverage (:36–45) |
| **The director's I2 review** (`FD-1B-INV-I2-DIRECTOR-REVIEW.md`) | the labels | "F_prior" and "prior part" name √(B/A), which involves no prior, since additivity failed; F_truth is outside the window in 15 of 16 cells, so "H3 refuted" is a count, not a size (:43–46) | |
| **Staged stage 0** (#667; `FD-1B-STAGED-STAGE0-REPORT.md`) | rule K: κ = √(Dnom/A_unc), like-for-like at the nominal truth, interaction group | **the like-for-like control passes**: κ in [0.9, 1.1] in 16 of 16 cells, 0.9757–1.0570 (:12–16) | coverage; that the toy realizes S1's M (κ is read at the nominal truth); the flux and detector groups; the correlation structure; that S1's block is right or wrong (:36–40) |

**Joseph's ruling on that diagnosis** (`DECISION-20261101-joseph-1b-keep-block-redesign-test.md:37–42`): the reported
block stays S1's full-universe block, and B goes to the note as a sensitivity. The redesigned test that followed is
the staged campaign, which ended under rule (iii) (`OUTCOME-20261106-1b-stage1-receipt-stop.md`).

## 3. Gate D's failing cells, by group

ρ_c² − 1 is the sum of the 38 per-band terms (`diag.json`; the script checks the sum to 1e-9). The shares are each
group's terms over ρ_c² − 1. The interaction column equals I2's `interaction_share_of_rho2_minus_1` (checked to
1e-12).

| cell | ρ_c | ρ_c² − 1 | interaction | flux | detector | the three largest terms |
|---|---:|---:|---:|---:|---:|---|
| R00 | 1.157 | +0.338 | 0.565 | **0.410** | 0.025 | Flux +0.139, MaRES +0.130, MvRES +0.030 |
| R02 | 1.149 | +0.321 | 0.708 | 0.300 | −0.008 | MaRES +0.212, Flux +0.096, Rvp2pi +0.063 |
| R05 | 0.838 | −0.298 | 0.359 | **0.576** | 0.065 | Flux −0.171, MvRES −0.034, MinosEfficiency −0.024 |
| R07 | 0.696 | −0.516 | 0.839 | 0.140 | 0.022 | Rvn2pi −0.163, MvRES −0.080, Flux −0.072 |
| R08 | 2.296 | +4.271 | 0.955 | 0.051 | −0.006 | MaRES +2.098, MaCCQE +1.224, MvRES +0.602 |
| R09 | 1.113 | +0.240 | 0.999 | −0.072 | 0.073 | Rvn2pi +0.076, MFP_pi +0.076, BhtBY +0.067 |
| R10 | 1.780 | +2.170 | 0.962 | 0.047 | −0.009 | MaRES +1.611, MvRES +0.379, Flux +0.103 |
| R11 | 1.827 | +2.337 | 0.989 | 0.015 | −0.003 | MaRES +1.662, MvRES +0.351, Rvn2pi +0.160 |
| R12 | 1.251 | +0.564 | 1.060 | −0.040 | −0.021 | MaCCQE +0.281, MaRES +0.235, MvRES +0.072 |
| R13 | 1.314 | +0.728 | 1.062 | −0.055 | −0.007 | MaRES +0.596, Rvn2pi +0.059, MvRES +0.048 |
| R15 | 1.418 | +1.012 | 1.019 | −0.012 | −0.007 | MaRES +0.796, MvRES +0.219, Rvp2pi +0.056 |

- **Nine cells** are carried mostly by the interaction group (0.71 to 1.06 of ρ_c² − 1), which I2 decomposes.
- **R00 and R05** are carried in large part by the single Flux band (0.41 and 0.58), which no record decomposes.

**Each group's own ratio** (gate D's `per_group_sigma_ratio`), classed on [0.9, 1.1]:

| group | matching | over | under | cells outside |
|---|---:|---:|---:|---|
| interaction | 1 | 12 | 3 | all but R06 |
| flux | 7 | 6 | 3 | R00, R02, R03, R08, R10, R14 over; R05, R07, R13 under |
| detector | 13 | 2 | 1 | R03, R06 over; R05 under |

These counts agree with `FD-1B-STAGE2-REPORT.md:146–150` (15, 9 and 3 cells outside).

## 4. Each band, cell by cell

**The class rule**, fixed in `attribution.py` from values already in the records, for band b in cell c:
- **undefined:** the band's block is zero on both sides (`diag.json` `sigma_ratio` null; only NormDISCC);
- **noise:** I0 marks the band noise-consistent on both sides at the upper floor in that cell
  (`i0.json` `per_band.noise_consistent_upper`);
- otherwise, by the band's own σ ratio √(E_b/M_b) on gate D's window: **matching** in [0.9, 1.1], **over** above,
  **under** below.

**Band-cells by group:**

| group | bands | matching | over | under | noise | undefined |
|---|---:|---:|---:|---:|---:|---:|
| interaction | 33 | 15 | 148 | 155 | 194 | 16 |
| flux | 1 | 7 | 6 | 3 | 0 | 0 |
| detector | 4 | 15 | 21 | 23 | 5 | 0 |

**The bands that carry the departure**, by Σ_c |term| (the other 32 bands sum to 1.610 over all cells). The class
string runs R00 to R15: M matching, + over, − under, n noise.

| band | group | Σ_c \|term\| | classes R00…R15 |
|---|---|---:|---|
| MaRES | interaction | 7.634 | `+-+++-+-+-++++-+` |
| MvRES | interaction | 1.903 | `+-M-+-+-+-++++-+` |
| MaCCQE | interaction | 1.720 | `+---+M-++-++++-+` |
| Flux | flux | 1.218 | `+M++M-M-+M+MM-+M` |
| Rvn2pi | interaction | 0.799 | `+++---+-++++-+++` |
| Rvp2pi | interaction | 0.557 | `+-+-+-+-++++-+++` |

- **Few band-cells match.** For the interaction bands that are resolved from noise, 15 of 318 lie in the window. A
  per-band ratio against a small S1 block can be far from 1; MaRES runs from 0.160 to 184.4 (`FD-1B-DIAG-REPORT.md:106–109`).
  That is why the term, not the ratio, decides a cell.
- **Six bands are noise in all 16 cells:** EtaNCEL, FrPiProd_pi, MaNCEL, NormNCRES, RDecBR1gamma, and NormDISCC
  (undefined). This matches I0's six (`FD-1B-INV-I0-REPORT.md:92–94`), with NormDISCC's zero blocks counted there as
  noise-consistent.
- The full table, all 38 bands × 16 cells with each σ ratio, term and class, is in `attribution.json` (`per_band`)
  and printed in `attribution.out`.

## 5. The two harness checks

Both concern the interaction group.

| cell | F_src = √(E/B) (I2) | κ = √(Dnom/A_unc) (stage 0) |
|---|---:|---:|
| R00 | 0.994 | 1.0004 |
| R01 | 0.998 | 0.9757 |
| R02 | 1.006 | 0.9950 |
| R03 | 0.986 | 0.9931 |
| R04 | 0.989 | 1.0210 |
| R05 | 0.996 | 0.9882 |
| R06 | 0.997 | 0.9987 |
| R07 | 1.004 | 0.9916 |
| R08 | 1.003 | 1.0570 |
| R09 | 1.007 | 1.0062 |
| R10 | 0.987 | 0.9968 |
| R11 | 1.014 | 1.0008 |
| R12 | 1.012 | 1.0001 |
| R13 | 1.015 | 1.0367 |
| R14 | 0.997 | 1.0056 |
| R15 | 1.007 | 0.9974 |

- **F_src.** The toys move the response in the pseudo-data. B moves the same response on the MC side. They give the
  same block to within 1.5 % in σ in every cell. Per band-cell √(B/E) has median 0.995 and 10th–90th percentiles
  0.63–1.63, as I2 §4.2 quotes (`FD-1B-INV-I2-REPORT.md:202`).
- **κ.** Pseudo-data built from each full universe, unfolded with the nominal simulation, reproduce S1's own universe
  block at the nominal truth in every cell.
- **What they leave.** In the interaction group the departure is a comparison of unlike objects: B against A, and A
  at the nominal truth against M at the data. It is not the toys failing to realize what they draw. The flux and
  detector groups have neither check.

**I2's factors**, classed on the same window, for the interaction group:
- F_src matches in 16 of 16 cells.
- "F_prior" = √(B/A) is over in 13 cells, under in 3 (R03, R05, R07), and in the window in none.
- F_truth = √(A/M) is under in 15 and matches only in R08 (0.999).

## 6. Open, and how each is routed

<!-- absence-ok: this section lists questions the committed records do not answer, as each record's own CANNOT SUPPORT states; it claims no search beyond the five readouts named -->
- **(a) The flux and detector groups.** Flux carries 0.41 of ρ_c² − 1 at R00 and 0.58 at R05, and its own ratio is
  outside the window in 9 cells. Neither group has an F_src or a κ.
  - **Routing:** Part 1 of the director's ruling, a declared split for the Flux band and the four detector bands.
- **(b) The additivity residual.** B + C misses A by about B's own size at the group level (I2 §4.3), and I2 does not
  measure how the residual divides among completeness, second order and within-cell truth variation
  (`FD-1B-INV-I2-REPORT.md:267–269`).
  - **Routing:** listed as open; not now (the director's ruling).
- **(c) The truth dependence**, F_truth median 0.683.
  - **Routing:** excluded. It overlaps staged stage 1, which ended under rule (iii).
- **The surrogates and the undrawn terms.** The lateral and normalization surrogates carry 29.0 % of the toys'
  covariance trace and are not tested (`gate-d.json:6`). C_model and C_resp are not drawn. Nothing here changes that.

## 7. The run

- **Script:** `fd/receipts-1b/precheck-attribution/attribution.py`, run with `python3 -I -B attribution.py <repo root>
  attribution.json` on the Mac at 0 node-h.
  - It refuses unless each input has its pinned sha256: gate-d `e1838c0a…`, diag `6fd6669e…`, i0 `9a4142d3…`, i2
    `a9d3dc9c…` and stage 0's readout `05be73ee…`, as committed on main.
  - **Its controls:**
    - the five records share cells, window and ρ;
    - stage 0 and I2 name the pinned I0 and I2 digests;
    - the per-band terms sum to ρ_c² − 1 (1e-9) and equal I0's (1e-12);
    - each σ ratio² equals share_toys · ρ² / share_s1 (1e-12);
    - F_src · F_prior · F_truth equals I2's total (1e-12), and that total equals gate D's interaction ratio (1e-12);
    - the interaction share equals I2's (1e-12).
- **Outputs:** `attribution.json` and `attribution.out`. Digests are in `SHA256SUMS.txt`.
- **The binding inventory.** `attribution.json`'s five {path, sha256} pairs are new receipt bindings, all OK. So
  `verify_hash_bindings.py`'s inventory constant moves from 161 to 166 rows (digest `2ba0b27d` → `6a2ac974`). The
  delta and a power test of each pin are in `binding-delta.txt`.
- **No product, pscratch file or COV2D input was opened.** Nothing was drawn, and nothing ran on the cluster.

Nothing is submitted, deposited or tagged.
