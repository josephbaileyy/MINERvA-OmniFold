# Candidate secondary results to move from the paper to the note (2026-10-25): a list for Joseph's decision

**Asked for by** Joseph (`DECISION-20261025-joseph-f0-limitation-stage-g-and-paper-scope.md` item 5): "this is something
that should be seriously considered, since caveats matter in a close read, which is what the note is for, but would
people reading the short paper care about them?"

**Drafted by** the paper rewrite lane, for the director.

**Nothing moves until Joseph decides.**

**Measured on** the paper after register round r18, which is merged: main `d1570c11`, `paper_body.tex` sha256
`fd1af760…`.

**Files:**
- `r18-paper-inventory.tsv`: the caveat inventory, coded under `caveat-study/CODEBOOK.md` with one extra column,
  `result`, which tags each caveat with the result it qualifies (`RESULTS-LIST.md`). It has 189 rows, and every quote
  was verified against the text.
- The blinded text that was coded has sha256 `bdb0f524…`, by the caveat study's rule. It is 8,663 words.

**CITABLE FOR:** which results carry which caveats, and the estimated effect of moving each.

**NOT CITABLE FOR:** what readers want. That is Joseph's judgment.

---

## 1. The headline: moving results changes the count of caveats, not the rate

| | caveat statements | distinct caveats | words | distinct per 1,000 words |
|---|---:|---:|---:|---:|
| the paper now (r18) | 189 | 104 | 8,663 | 12.0 |
| without the generator tests (S6) | 133 | 76 | about 7,000 | 10.9 |
| without all of Sec. VII (S5–S12) | 104 | 61 | about 6,240 | 9.8 |
| without every candidate below (S1–S12) | 85 | 49 | about 5,440 | 9.0 |
| PRD comparators (caveat study, set P) | | | 7,700–11,900 | 1.4–4.5 |

**Notes on the table:**
- The r18 inventory had a different coder from the caveat study's r17 inventory, and the study measured coder agreement
  at about ±25%. Its 12.0 per 1,000 words is therefore consistent with r17's 10.0.
- The main results (Secs. IV–VI, Table I) carry 73 of the 189 statements, and 12 qualify the paper as a whole.

**What follows:**
- **The comparators' rate needs fewer caveats per result.** Even moving every candidate leaves 9.0 distinct caveats
  per 1,000 words, and a paper of about 5,400 words, below the comparators' length band. The main validation results
  are themselves caveat-dense.
- **The absolute count is a different matter.** Moving Sec. VII removes 85 of the 189 caveat statements. A short-paper
  reader meets a paper about half as qualified. That is the question Joseph asked.

## 2. The candidates, ranked by caveat statements removed per claim lost

The "claims lost" column counts the distinct printed findings the paper would stop stating; the list is under each
entry.

**How the rate estimates are made:**
- words removed are the candidate's printed words, scaled to the blinded text;
- each pointer is assumed to add about 20 words;
- a candidate's unique caveats are those it alone carries, so they leave with it.

| rank | id | result | statements (distinct, unique) | claims lost | statements per claim | distinct per 1,000 words after | constraint |
|---|---|---|---|---:|---:|---|---|
| 1 | S6 | the generator joint tests (VII B–D, Table IV) | 56 (30, 28) | 10 | 5.6 | 12.0 → 10.9 | **the abstract and Table I state it; Sec. I frames the paper around it** |
| 2 | S10 | the ±4% recoil sensitivity study (VII D (ii)) | 5 (2, 2) | 1 | 5.0 | 12.0 → 11.9 | none |
| 3 | S7 | the target-corrected (CH) evaluations (VII E) | 5 (4, 3) | 2 | 2.5 | 12.0 → 11.7 | **DECISION-20261020 places them in VII E** |
| 4 | S4 | the binned-unfolding diagnostic, D-ID (VI, Table III) | 9 (4, 4) | 4 | 2.25 | 12.0 → 12.1 | its record requires its limits to travel with it |
| 5 | S2 | the run-period inconsistency (IV B ¶3) | 4 (2, 2) | 2 | 2.0 | 12.0 → 11.9 | **a block of the quoted covariance** |
| 5 | S9 | the matched projections and power (VII E) | 6 (4, 4) | 3 | 2.0 | 12.0 → 11.7 | **the abstract states "no evidence of gain over matched coarse projections" (K3)** |
| 7 | S8 | the multiplier scan and the null locations (VII E) | 3 (2, 1) | 2 | 1.5 | 12.0 → 12.0 | **Sec. VI's third result cites the null displacement** |
| 7 | S12 | the argument for unfolding before testing (VII lead) | 3 (3, 2) | 2 | 1.5 | 12.0 → 11.9 | **the note does not print it** |
| 9 | S5 | the descriptive comparisons and the (E_avail, W) map (VII A) | 6 (6, 2) | 5 | 1.2 | 12.0 → 12.1 | the paper's only data-against-generator description |
| 10 | S1 | the learner dependence and the exact-split cross-check (IV A ¶2) | 3 (3, 3) | 3 | 1.0 | 12.0 → 11.8 | **the post-selection disclosure (K5, D1) stays with the choice** |
| 10 | S11 | the matched (p_T, p_∥) projection check (VII D (ii)) | 1 (1, 1) | 1 | 1.0 | 12.0 → 11.9 | **it is condition (ii)'s evidence that the omission matters** |
| 12 | S3 | the generator-shape component C_model (IV B ¶4) | 3 (3, 3) | 4 | 0.75 | 12.0 → 11.9 | **Joseph's decision to report it beside the covariance (DECISION-20261024)** |

**Bundles:**
- **All of Sec. VII (S5–S12),** replaced by a pointer paragraph of about 120 words: 85 statements, 43 unique; 12.0 →
  9.8 per 1,000 words.
- **The VII E sensitivity results only (S7, S8, S9, S10):** 19 statements and 3 + 1 + 4 + 2 = 10 unique; about
  12.0 → 11.3.

## 3. Each candidate

For each candidate the entry gives:
- **caveats:** the issue labels from the inventory, with statement counts;
- **in the note:** where the result already prints;
- **pointer:** the one-line pointer the paper would keep, a draft;
- **stops claiming:** what the paper would stop stating.

### S6. The generator joint tests (VII B–D, Table IV)

- **Caveats (56):**
  - missing calorimetric recoil-response band (5 + 1);
  - below-fine-grid composition and convergence (5 + 1);
  - calibration valid only within simulation (4 + 1);
  - tests of hybrid nulls, not generators (3);
  - error control rests on A1 and A2 (3);
  - carbon against CH target difference (3);
  - half-simulation size difference (3);
  - size averaged over nuisance priors (2);
  - tests recover already-known disagreements (2);
  - GiBUU lacks high-energy neutrinos (2 + 1);
  - neutron-mass W in the predictions (2);
  - calibration fidelity not measured (2);
  - lost pseudo-experiments (2);
  - geometric convergence assumption (2);
  - and 12 others with one statement each.
- **In the note:** the whole chapter `sec_joint.tex` (sec:joint5d and its subsections) prints the design, calibration,
  decision rule, conditions, results, lost draws and power. Nothing is missing.
- **Pointer:** "As an illustration of inference with a biased estimator, the companion note calibrates tests of five
  generator predictions in simulation; all ten reject at the 5% familywise level, conditionally on the simulated
  detector and nuisance model (\nsec{sec:joint5d})." This one sentence keeps the abstract's claim supported.
- **Stops claiming:**
  - the hypotheses, the calibration and the Holm decision rule, and its familywise error control under A1 and A2;
  - the six conditions;
  - Table IV's ten decisions;
  - the null-distribution locations;
  - the CH, projection, power and recoil results (S7–S11).
- **What else changes:**
  - **Sec. I** frames the paper as "a case study of multidimensional unfolding and of inference with a biased
    estimator". The second half would rest on the pointer.
  - **Sec. VI's** last paragraph and third result would change.
  - **Table I's** last row would point to the note.
  - **The abstract's** last sentence is protected; its wording is Joseph's.

### S10. The ±4% recoil sensitivity study (VII D (ii) ¶2)

- **Caveats (5):** recoil scale study limited (3 + 2): no null regenerated; no other form of response change tested;
  neutrons and higher-momentum hadrons outside the test-beam sample.
- **In the note:** `sec_joint.tex` sec:joint5d-response.
- **Pointer:** "An exploratory recoil-energy scaling study is described in \nsec{sec:joint5d-response}."
- **Stops claiming:** that every rejection stays in place under a ±4% recoil scaling, and that the observed statistics
  move by up to about 11%.
- **Note:** condition (ii) would then state only the omission and its consequence.

### S7. The target-corrected (CH) evaluations (VII E ¶1)

- **Caveats (5):**
  - carbon against CH target difference (2 + 1);
  - GiBUU hydrogen DIS energy non-conservation (1);
  - target-corrected evaluations descriptive (1).
- **In the note:** `sec_joint.tex` sec:joint5d-ch.
- **Pointer:** "Descriptive target-corrected evaluations are in \nsec{sec:joint5d-ch}."
- **Stops claiming:**
  - that correcting NuWro and GiBUU to hydrocarbon moves both toward the data;
  - that NuWro's total-test rejection is not robust to that correction;
  - GiBUU's hydrogen DIS problem.
- **Constraint:** `DECISION-20261020-joseph-nuwro-ch-claim.md` (provisional) states the CH replays once, at a high
  level, in VII E. Moving them needs Joseph's ruling. Sec. II's statement of the uncorrected target difference stays.

### S4. The binned-unfolding diagnostic, D-ID (VI ¶2–3, Table III)

- **Caveats (9):**
  - the diagnostic's limited scope (5): binned, signal-only, noise-free, 38% of the residuals;
  - exact runs not converged (2);
  - a pooled fifth change with background (1);
  - exact iteration removes the residual only partly (1).
- **In the note:** `sec_5d.tex` sec:val-departure, paragraph "Comparison with exact binned unfolding". Every number
  and Table III's contents print there (the CLAIM-ADDITION comment says so).
- **Pointer:** "A binned diagnostic of this residual, in simulation, is in \nsec{sec:val-departure}."
- **Stops claiming:**
  - that exact binned unfolding with five iterations leaves about the same median residual;
  - that the tree approximation dominates only 15 of 144 residuals;
  - that 121 lie in weakly constrained quantities;
  - that the residual is consistent with regularization at this binning and prior;
  - Table III.
- **Constraint:** the source record (d-id/REPORT.md §11) requires the limits to travel with the outcome. They would
  travel together, to the note.

### S2. The run-period inconsistency (IV B ¶3)

- **Caveats (4):** run-period inconsistency (3); run-period block size not validated (1).
- **In the note:** `sec_systematics.tex` sec:uq-combine (`:304–330`).
- **Pointer:** IV B ¶1 already names the run-period block among the four. The pointer would add "whose construction is
  in \nsec{sec:uq-combine}".
- **Stops claiming:**
  - that one period group's p_∥ distribution differs from the earliest periods' by a step of about 7% near 8 GeV/c;
  - that its cause is unknown;
  - that the block is 2.0% on the integrated cross section;
  - that its size is not validated.
- **Constraint:** the block is one of the four blocks of the quoted covariance, and the step is a finding about the
  data. A reader of the 2D covariance may want it in the paper.
<!-- absence-ok: restates the paper's own printed sentence (IV B ¶3, "its size is not validated"); not a new absence claim -->

### S9. The matched coarse projections and the power studies (VII E ¶2)

- **Caveats (6):**
  - no gain over coarse projections (2);
  - low power for some alternatives (2);
  - projection tests uncorrected for multiplicity (1);
  - power only for chosen alternatives (1).
- **In the note:** `sec_joint.tex` sec:joint5d-projections and sec:joint5d-power.
- **Pointer:** "The matched coarse projections and the power studies are in \nsec{sec:joint5d-projections} and
  \nsec{sec:joint5d-power}."
- **Stops claiming:**
  - the projection p values;
  - "no evidence of additional discrimination from the joint five-observable information";
  - the power values.
- **Constraint:** the abstract states "no evidence of gain over matched coarse projections" (K3). The body would need
  to keep one supporting sentence, or the abstract would change. That is Joseph's call.

### S8. The multiplier scan and the null locations (VII E ¶1)

- **Caveats (3):** multiplier scan outside the decision rule (2); result retains part of its prior (1).
- **In the note:** `sec_joint.tex` sec:joint5d-kappa and sec:joint5d-results.
- **Pointer:** "A scan of the multiplier and the null distributions are in \nsec{sec:joint5d-results}."
- **Stops claiming:**
  - that all ten rejections are determined up to a multiplier of about 5.2;
  - that the external nulls are displaced upward by the estimator's pull toward its prior.
- **Constraint:** Sec. VI's third result cites that displacement, so VI would need to repoint to the note.

### S12. The argument for unfolding before testing (VII lead)

- **Caveats (3):**
  - higher-dimensional results lack validated intervals (1);
  - unfolding's advantage is smaller for tests (1);
  - no comparison with a reconstruction-level test (1).
- **In the note:** **missing.** No note section prints this argument or the statement that no reconstruction-level
  comparison was made. It would have to be added to the note first, at the head of `sec_joint.tex`.
- **Pointer:** none until it is.
- **Stops claiming:** that a reconstruction-level test would avoid the regularization bias but need the same response
  model; that the tests instead calibrate the bias into the null; that the power has not been compared with a
  reconstruction-level test. S9 of r17 was declined, so that statement stays in VII.
  Search: reconstruction-level test; reconstruction-level comparison; reconstruction-level alternative; folded through the analysis; test at reconstruction level, in the note's sources docs/analysis-note/*.tex (paper, primer, records and PET files excluded) @ d1570c11

### S5. The descriptive comparisons and the (E_avail, W) map (VII A)

- **Caveats (6), one each:**
  - higher-dimensional results lack validated intervals;
  - GiBUU lacks high-energy neutrinos;
  - carbon against CH target difference;
  - regularization bias under truth changes;
  - the map is descriptive only;
  - no closure with a mismodelled detector.
- **In the note:** `sec_eavailw.tex` sec:eavailw-map and sec:eavailw-band; `sec_3d.tex` sec:3d-2p2h and sec:4d.
- **Pointer:** "Descriptive comparisons of the higher-dimensional central values with the generators are in
  \nsec{sec:eavailw-map}."
- **Stops claiming:**
  - that every generator underpredicts at low E_avail;
  - where the positive difference relative to Tune v1 lies (two thirds at E_avail ≥ 0.8 GeV, a fifth in one cell);
  - the ratio ranges;
  - that the data lie above all four external predictions.
- **Note:** this is the paper's only data-against-generator description, apart from the tests.

### S1. The learner dependence and the exact-split cross-check (IV A ¶2)

- **Caveats (3):**
  - learner dependence of the 2D result (1);
  - learner chosen after the comparisons were known (1, the K5 disclosure);
  - cross-check confounds learner and background (1).
- **In the note:** `sec_method.tex` sec:method-config (exact-split paragraph).
- **Pointer:** the existing "Both estimators are described in \nsec{sec:method-config}" stays.
- **Stops claiming:**
  - that ten LightGBM seeds give 2.64–2.75 with purity subtraction, with the exact-split values;
  - that refined subtraction lowers the distance from \chiPaperPurity to \chiPaper;
  - the per-bin learner difference of 1.03% (maximum 17.6%).
- **Constraint:** the disclosure "This learner was chosen after both comparisons were known" is D1/K5 and stays with
  the choice. So does "the benchmark is therefore a reproduction".

### S11. The matched (p_T, p_∥) projection check (VII D (ii) ¶1)

- **Caveats (1):** a post-decision projection check (1).
- **In the note:** `sec_joint.tex:582`.
- **Stops claiming:** that the projection tests do not reject GENIE CV, so the information that rejects it involves
  the hadronic axes.
- **Constraint:** this is the evidence for condition (ii)'s "The omission matters for the rejections". Without it,
  that sentence would rest on the note.

### S3. The generator-shape component C_model (IV B ¶4)

- **Caveats (3):**
  - C_model is not a bound on the bias (1);
  - it omits the normalization's model dependence (1 + 1).
- **In the note:** `sec_systematics.tex` sec:uq-2d-scope (`:389–420`).
- **Stops claiming:**
  - C_model's definition and median;
  - the total with it;
  - its integral;
  - why the comparison with the published uncertainty leaves it out.
- **Constraint:** `DECISION-20261024-joseph-2d-model-dependence-component.md` has the paper report it beside the
  covariance, as the users' total. Moving it changes what the paper reports for the 2D result, so it is Joseph's.

## 4. For Joseph

1. **The measurement says moving secondary results cannot reach the comparators' caveat rate** (§1). Moving all of
   Sec. VII still leaves about 9.8 distinct caveats per 1,000 words, against 1.4–4.5. What it changes is how many
   caveats a short-paper reader meets: 85 fewer statements out of 189.
2. **The one large lever is S6, the generator tests.** It is the paper's stated secondary application, and the
   abstract, Table I and Sec. I's framing depend on it. Moving it makes the paper a validation study with a one-sentence
   illustration, and the note carries the tests.
3. **The cheap moves with no constraint:**
   - S10, the recoil sensitivity study;
   - S4, D-ID, whose limits travel with it.
4. **Every other move touches a decision Joseph already made, or a protected sentence:**
   - S7: DECISION-20261020;
   - S9: the abstract's K3;
   - S3: DECISION-20261024;
   - S1 and S11: disclosures and condition (ii).
5. **S12 cannot move** until the note prints its argument.
