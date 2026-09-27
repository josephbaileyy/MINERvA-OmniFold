# s5p independent review, round 2 (repair cycle 1 and the production admission draft)

**CITABLE FOR:** the independent reviewer's findings on amendments 6/6b, the F1 repair and its deliverable
corrections, the fine nulls, F4, the evaluator/controller, the nuisance model and the amendment-7 admission
DRAFT, verbatim. **NOT CITABLE FOR:** any repair or disposition; the campaign's responses are in amendment 8
and the state file.

- reviewer: independent session (general-purpose agent with two sub-reviewers for items 2 and 7; no authorship
  of the reviewed work), read-only worktree `../MINERvA-OmniFold-s5p-review2` detached at `7f05a413`, left clean
- scratch: `/pscratch/sd/j/josephrb/s5p-20260926/review2/` (nothing submitted to Slurm)
- received 2026-09-27T14:00Z; H1 checked by the campaign before acting (`s5p_nullexp.draw` picks one
  `model_bands` universe per experiment; the pilot metadata shows single bands); the running design pilot
  58950326 (31 products, the single-universe draw) was cancelled at 14:03Z

## Report (verbatim)

## s5p review round 2: amendments 6/6b repair cycle and the amendment-7 admission draft

The admission is not ready to freeze. The flux repair (F1), the fine nulls (F2), the shrinkage fix (F5), the GEANT double-count fix and the sequential stopping rule all check out under my own code. But the null's interaction-model prior is about 34 times too narrow in variance, which makes the calibration anti-conservative. Several claim and cost statements in the draft also overstate what the evidence supports.

I edited nothing and submitted nothing to Slurm. `git -C …/MINERvA-OmniFold-s5p-review2 status --porcelain` printed nothing (exit 0); HEAD is `7f05a413`. Two parallel sub-reviewers did items 2 and 7; I checked their key claims (for example, `pow.q` really does say `--pool cpu`).

### Verdict table

| # | Item | Verdict |
|---|---|---|
| 1 | Amendments 6/6b answer F1–F6 and the double count; frozen before any observed statistic | CONFIRMED |
| 1 | Re-specified T6 size clause (shift variants c·D, claim = largest p) | **FINDING, MEDIUM** (M2): it cannot fail and gives almost no protection |
| 1 | Power level moved to 0.005 under the claim rule | CONFIRMED (stricter, not a rescue) |
| 2 | F1: flux-average normalization, reweight unbiasedness, 50–100 GeV supplement merge, p∥ ratio, GiBUU convention, fine-null digests | CONFIRMED |
| 2 | F1 deliverables (VL156–VL160, text at `908ecce5`/`f5ed4704`) | Numbers CONFIRMED; five LOW wording items (L7) |
| 3 | F2 numbers; fine-null J integrals equal the generator's | CONFIRMED |
| 3 | Remaining within-fine-cell conditioning | **FINDING, MEDIUM** (M1) |
| 4 | F4: D and its use as the shift variant | **FINDING, MEDIUM** (M2) |
| 5 | Validity of the sequential p-value at a data-dependent B; Holm on claim p-values; seed disjointness | CONFIRMED |
| 5 | Evaluator: determinacy rule not implemented; power definition | **FINDING, MEDIUM** (M3, M4) |
| 5 | Queue logic | **FINDING, LOW–MEDIUM** (M6) |
| 6 | Nuisance model: interaction-model prior | **FINDING, HIGH** (H1) |
| 6 | Nuisance model: flux, detector, lateral, normalization, rounding, GEANT exclusion | CONFIRMED (one LOW domain caveat, L4) |
| 7 | Admission costs and placement | **FINDING, MEDIUM** (M5) |
| 7 | Reserves and cumulative caps; concurrency in meter units | CONFIRMED |
| 7 | Admission completeness against the handoff | **FINDING, LOW–MEDIUM** (L1–L3) |
| 8 | Claims overstated or result wrong | covered by H1, M1, M4 |

### H1 (HIGH): the null draws one interaction-model knob out of 69 per experiment

- **What the code does.** `s5p_nullexp.draw` (`s5p_nullexp.py:76-80`) picks a single universe uniformly from `model_bands`: 69 universes across 34 bands. The pilot metadata confirms this (for example seed 960000 drew only `EtaNCEL_1`; seed 960030 drew only `MaCCQE_0`).
- **Why that is wrong.** The analysis's own uncertainty model sums the bands. The note's `app_statmethods.tex` gives the MAT per-band covariance, and `assemble_gbdt5d_adopted.py:4-6` throws all vertical bands together. Flux (one PPFX universe, itself a joint throw) and the detector bands (each drawn independently) are handled correctly; only the model draw is not.
- **What I measured** (`r2_nuis.py`, a reco-level proxy over J-shaped reco cells with the same truth-preserving rule):
  - The band-sum variance is 34.43 times the drawn variance (per cell 34.0–34.5).
  - Median per-cell SD: 3.11% with the band sum against 0.53% as drawn. In statistical-error units that is 4.2σ against 0.71σ.
  - Shape-only, the band-sum model spread is 3.25σ_stat, the largest shape nuisance (flux shape is 2.65σ). Almost all of it comes through the signal response (2.9%), not the background (0.25%). The largest bands are MaRES, MaCCQE and MvRES.
- **Consequence.** The calibration under-represents the dominant shape nuisance, so it is anti-conservative: a data-vs-pseudo response difference can produce a rejection. The unfolded J-cell magnitude is inferred from the reco proxy; I did not re-unfold.
- **Disposition before freeze:**
  - Draw every band in each experiment (independent ±1 endpoints like the detector bands, or N(0,1) interpolation; 2p2h one of three), multiply the weight ratios, and apply the truth preservation to the combined factor.
  - Add a unit test that the drawn prior variance equals the band sum.
  - Correct the amendment text, and rebuild the V pilot, which uses the same draw (about 4–9 CPU node-h).

### M1 (MEDIUM): the within-fine-cell residual is unmeasured and matters because the external nulls are strongly non-central

- **Why it matters.** At an external null the full-MC asimov residual (unfolded result minus the generator's J-cell values) is large: median 3.2% for GENIE CV, 2.8% for MEC and 9.3% for GiBUU. The null T is therefore dominated by a bias term.
  - The non-centrality b′W⁻¹b is 236–1421, depending on the generator and on my metric proxy (stat-only, or pilot-based with shrinkage 0.08–0.3).
  - The null T standard deviation is then 34–76, against 12–15 for a central χ².
  - A process difference δ shifts T by about (b′W⁻¹δ)/√λ null standard deviations, bounded by the whitened norm of δ.
- **What that means for F2.** Going from coarse to fine nulls shifted T by 0.3–2.7 null standard deviations, so F2 was essential.
- **Why the draft wording is not enough.** Its phrase *"at a finer level than the effect it removes"* (admission conditions), and amendment 6's *"bounded by the fine null"*, do not bound what remains below the fine grid.
- **Disposition:** either measure it (an intermediate-resolution null nested between J and the fine grid, one asimov unfold per generator at about 0.2 node-h each, reporting the change in null-T units), or reword the condition as "unmeasured, potentially material" with these numbers.

### M2 (MEDIUM): the F4 variants c·D are noise-dominated and give almost no protection

- **Reproduction.** D reproduces bit-exactly (maximum difference 0). Median |D|/f is 0.029%, 0.057%, 0.049% and 0.173%. Median |D/se| is 0.58–0.86 against 0.76 expected from noise alone. A KS test against t with 3 degrees of freedom gives p = 0.017 (MnvTune) and 0.011 (GiBUU), but the cells are correlated, so this is only indicative.
- **Effect on T.** Across all my metrics the variants shift T by at most 0.09 null standard deviations at c = 1. The claim rule therefore almost never changes a p-value: it does no harm (negligible power cost) and gives little protection.
- **What four pairs do establish.** Projected onto the bias direction, the pairs give 0.03–0.08 ± 0.05–0.17 null standard deviations per unit c. The 95% upper bound is 0.19–0.56 at c = 1, or 0.09–0.28 at c = ½. By a normal approximation (inferred) that allows a worst-case size of about 0.066–0.086 at 0.05. So four pairs bound the magnitude but not the direction, and the draft's *"bracketed by the variants"* overstates it.
- **The half-to-full extrapolation** (1/n versus 1/√n) is a two-point heuristic. It is acceptable only as "consistent with zero, magnitude-bounded", not as an established law.
- **The re-specified T6 size clause has no failing outcome.** Not a rescue (the withdrawn size ensembles never ran), but it should say so.
- **Disposition:** use a bound-based variant (along the bias-aligned direction at the upper bound), or add pairs (about 0.03 CPU node-h per pair); reword.

### M3 (MEDIUM): the evaluator records rejections without the determinacy rule

- The admission requires that a rejection's 95% Clopper-Pearson interval lie entirely below its Holm threshold. The evaluator's `s5p_inference.holm` (`s5p_inference.py:114-124`), called at `s5p_joint.py:254`, uses only the point p-value. What happens when a Holm step is undetermined is not specified anywhere.
- Power (`s5p_joint.py:270-272`) uses the plain rank rule. At B = 800 and level 0.005 the rank rule accepts k ≤ 3, but the determinacy rule needs k = 0; at B = 1999 it needs k ≤ 3 (my Clopper-Pearson scan).
- My simulation of the frozen rule, after checking my implementation against `sequential_decision` on 300 random inputs:

  | level | P(p ≤ α) | with the 95% interval condition |
  |---:|---:|---:|
  | 0.005 | 0.00502 | 0.0020 |
  | 0.01 | 0.0100 | 0.0060 |
  | 0.05 | 0.0500 | 0.0405 |

  The expected B under H0 is 759. The p-value at a data-dependent B is valid, and the determinacy condition makes it conservative.
- **Disposition:** implement the determinacy check in Holm (an undetermined step stops it), apply the same rule to power, and add tests.

### M4 (MEDIUM): non-rejections would be reported with the wrong power

The draft says non-rejections are reported *"with the power of the same test"*, but power is measured only against the MnvTune null. The external nulls are non-central (M1), so their power against the same alternatives is lower (inferred, not measured). **Disposition:** run at least one external-null power set (for example GENIE CV with P1r), or restrict the sentence to the MnvTune test.

### M5 (MEDIUM): costs and placement (sub-reviewer, spot-checked)

- **Power lane on the wrong pool.** `prod-draft/queues/pow.q` submits `--pool cpu … -C cpu` under the production stage. There is no GPU queue, and `s5p_nullexp` has no GPU path.
- **Worst case exceeds the placement.** At the measured ~557–587 s per experiment, the worst case is about 228 CPU node-h against 150 placed.
- **The fallback is not implemented.** If the meter stops a null, no final status file is written and the evaluator refuses it.
- **Lines can time out.** Ten experiments per line with a 2 h limit overruns for slow lines (997 s per experiment observed). Seeds are then missing, so a null that needs all 1999 never writes its final status.
- **Wall clock is understated.** The generated queues give about 92 experiments per hour, so 46–68 h per null, not the 30–40 h stated.
- **Storage.** About 21 GiB projected against the 20 GiB cap (partly inferred), with no storage line in the admission.
- **Disposition:** substitute the measured times; set per-line to 8 or the time limit to about 2.5 h; either create a GPU queue and stage or price power on CPU; implement a "budget" stop status that the evaluator accepts; add a storage line.
- **Confirmed:** 278.564 ≤ 310.184 node-h in the pool; 313.65 ≤ 345.27 cumulative; the verification/repair reserves (62.037 CPU / 22.981 GPU node-h) are untouched; concurrency 0.75 node-equivalents.

### M6 (LOW–MEDIUM): queue robustness

- The wait line reads an empty or failed `squeue` as "the batch has left". A transient failure lets the controller evaluate a look on a partial batch.
- Temporary files (`*.partial-*.npz`) match the product globs, so a task killed mid-write leaves a counted file.
- The power ensemble's size is not checked.
- My own finding: the prediction-error draw for each simulated experiment is keyed by its position in the file list (`s5p_joint.py:146`), not by its seed. A late retry of a missing product re-assigns the draws of every later product.
- A null without a `process_shift` entry silently runs with c = 0 only (`s5p_joint.py:183`).

### LOW items

- **L1, NuWro freeze ordering.** The NuWro D and F2 products are first production jobs, yet `design.json` says their digests are *"FILLED AT FREEZE"*. The admission must say when the NuWro digest is committed: before NuWro's calibration and before any observed statistic.
- **L2, missing Stage-7 elements.** There is no seed/numerical stability check of the observed p-value (cheap: the 20 existing data jitter unfolds). The validation operand is not named now that the size ensembles are withdrawn. The admission should also argue that the joint branch is independent of measurement qualification (Stage 7 says "after measurement qualification"), and price delivery work.
- **L3, GiBUU domain.** GiBUU's fine null also carries the E_ν < 20 GeV-truncated truth outside its test domain (p∥ ≥ 6 GeV/c, ratio median 0.82) into the migrations. Probably small (inferred).
- **L4, recoil response.** No recoil energy-scale band exists in the analysis's systematic set; the note itself says hadronic-response completeness is not established (`app_statmethods.tex` ~259-262). Add this to the claim conditions.
- **L7, F1 deliverables.**
  - VL159's "σ_tot" values rest on the quarantined historical 3D covariance.
  - `sec_3d.tex:223` ("every GENIE and NuWro prediction … repaired") is too broad: the FSI dials and the NuWro-shaped FPS prior still use unrepaired samples.
  - GiBUU's "0.9966" is an energy-dependent reweight (0.990–1.001 by E_avail bin).
  - Convention and rounding: "≈1.6" is 1.553 measured; VL156 states data/generator − 1 while `sec_3d` uses the shortfall.
  - The E_ν > 100 GeV wording wrongly equates the predictions' truncation with the data's (only the flux integral stops at 100 GeV; negligible).

### Confirmed with my own measurements

- **F1 (sub-reviewer's own code):**
  - Φ_t matches `hFluxCV` to 5e-16.
  - GENIE sampling is content-proportional: χ² 106/121, against 126,044/121 for the density × width reading.
  - The 50–100 GeV supplement has no overlap and no gap.
  - The GENIE CV / MnvTune p∥ ratio is restored from 0.317/0.138/0.039 to 1.032/1.029/0.986 (9–10, 10–15, 20–40 GeV/c).
  - The nullsF numerator digests match the repaired products.
- **F2:** medians 0.652/0.650/2.797% and maxima 5.19/3.08/15.36% reproduce. The fine-null J integrals equal the generator's to under 1e-14.
- **F5:** the standardized Ledoit-Wolf code matches its docstring.
- **GEANT double count:** GEANT is excluded from the model bands, and `runs/s3/pilot` is empty (the defective code never ran).
- **Freeze order:** amendment 6 (`66cf3129`) precedes the F4 results (`4d30c8eb`). No V or evaluator output exists on the cluster.
- **Tests:** 33 pass locally.
- **Pilot spread** (25 products present): event-level 4.9% per cell, lateral 3.2%, rounding 0.24%.

### Context you should know about

I computed descriptive per-cell data residuals, median |f_data/μ_G − 1| over the 109 J cells: MnvTune 14.4%, GENIE CV 10.2%, GENIE MEC 10.0%, NuWro 20.7%, GiBUU 38.6% (GiBUU not restricted to its domain). This is not the frozen statistic, and similar deficits are already published in the note (VL156–VL160). Its implication is that validity (H1, M1), not power, is what decides these tests. The campaign may want to record this disclosure under its data-informed choices.

### Scratch files

- **Cluster `/pscratch/sd/j/josephrb/s5p-20260926/review2/`:**
  - `main/`: `r2_common.py`, `r2_nuis.py`, `r2_f4.py`, `r2_nc.py`, `r2_v21.py` and `r2_proj.py`, each with its output and log (`*_out.json`, `*.err`), plus a copy `s5c_contract.json`.
  - `f1/`: `r2f1_check.py`, `r2f1_check_out.json`, `r2f1_check.err`, `r2f1_eavail.py`, `r2f1_eavail_out.txt`.
  - `cost/`: `meter-measure.json`.
- **Local scratchpad** `/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/0f65cb75-7b8b-4df3-8592-8430238adac1/scratchpad/`: `r2_*.py` (including `r2_seq.py`), `r2f1_*.py`, `cost/seedcheck.py`, `cost/regen/`.