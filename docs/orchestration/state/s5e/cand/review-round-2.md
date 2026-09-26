# s5e candidate R — independent review, round 2 (operand level)

**Reviewer.** An independent agent, read-only, in the isolated worktree `MINERvA-OmniFold-s5e-review2`
(detached at `843fc99e`), using its own code; it did not call `s5e_analyze_candidate.py` or
`s5e_next_design.py`.
**Scope.** No Slurm submission and no unfolds. Nothing was written outside
`/pscratch/sd/j/josephrb/s5e-20260925/review2/` and the session scratch. The worktree's
`git status --porcelain` was empty afterwards.
**Artifacts.** Scripts and JSON outputs are copied beside this file in `review2/`; the cached npz files
are not.

## Verdicts, as returned (abridged)

| check | verdict | reviewer's numbers |
|---|---|---|
| 1 products | CONFIRMED | 432 npz, counts as frozen; R 400/31 (random_state 45, 46 on the seed probe), B0 100/8; seeds only in 700000–702019 / 800000–805019; ratio sha256 GiBUU `45cc3e0a`, W1 `2a208df9`, W2 `80e16f95`, W3 `3455daf3`; bootstrap seeds exactly 1–100, all distinct; k5_b16's replicas b16–b20 logged rc 0 (last written 04:36:19Z; the crash at 04:37:04Z came in the post-run inventory step) |
| 2 development | CONFIRMED | K1 2.175 / 0 / 0 (max \|mean pull\| 0.474); B0 8.62 / 56 / 59; paired 13.15; K2 ratios 1.002 / 0.998, K3 1.035 / 0.987; K4 bitwise / ≤ 1.2e-10 σ, k4_base = K1 700000; K5 0.988, 3/153, 40.63; exit true under the amended rule, false under the original contract text |
| 3 assessment | CONFIRMED | A1 2.688 / 0 / 0; A2 1.0234, 6/153 (3.9%), 43.06; A3 probes ≤ 1.4e-10 σ, upcast = data_R bitwise, rounding probe median 0.783, max 2.584 (J145), 51 functionals > 1 σ → FAIL; A4 20 cells (smallest margin 7.8%); A5 0.982 / 1.491 (EW7) |
| 4 deformations | CONFIRMED | W2/W3 rebuild from the generator files with max difference 0.0; the W/nominal xtrue ratio equals c·ρ per 5D cell to 1.5e-14; in-grid total kept to 2e-6; no earlier product or task table (490 metas) used W1–W3; the analysis was frozen at `2f958652`, 40 s before the first job |
| spend | CONFIRMED | sacct: 1.311, 0.913, 2.258, 1.984; total 10.399 |
| next design | CONFIRMED | own Clopper–Pearson/Bonferroni reproduces every grid assurance; n-for-80% within the tool's 2% search resolution (the curve is sawtoothed) |
| 5 interpretation | PARTLY | M1–M4, L1–L5 |

## Findings and dispositions

| finding | severity | reviewer | disposition |
|---|---|---|---|
| M1 | MEDIUM | "A2 PASS" hides per-functional under-coverage. 6/153 functionals have a pull SD outside 3 SE, against ≈ 0.4 expected (p < 1/4000 if independent). EW41, **inside the A4 scope**, has pull SD 1.42 and 68% coverage 15/40 = 0.375. J206, J215 and EW41 repeat in development and assessment (the per-functional pull SDs correlate 0.48 between the two samples). A2 passes only by its 10% allowance | **ACCEPTED.** The outcome states it. A2 is a pooled-calibration pass, not per-functional calibration, and had A3 passed the qualified scope would have included EW41 at 37.5% empirical coverage. The next design's zero assurance at design values reflects exactly this (its minimum is EW41). |
| M2 | MEDIUM | The A3 failure was foreseeable at the freeze. On R's data-σ scale, B0's diagnosis probe gives median 0.795, max 2.48, against R's 0.783 / 2.58; R changes only the refinement, so no R-type candidate could meet 0.3 / 1.0 | **ACCEPTED.** The outcome says the failure is a property of the estimator family that R shares with B0, not a finding about R's repair, and that the diagnosis numbers predicted it. |
| M3 | MEDIUM | "no covariance carries it" is not established. The data bootstrap σ is 1.57× the pseudo-experiment σ (EW median; 1.87× over all 153), unexplained by exposure; the jitter spread (0.72–0.80 data-σ rms) equals √(1 − σ_pseudo²/σ_data²) ≈ 0.80. The per-replica refit bootstrap may already contain this noise; the alternative is data behaving as a model departure. Not proven either way; the next design's item 1 decides it | **ACCEPTED.** KNOWN_ISSUES 80, the outcome, the diagnosis consequences and the deliverables now say it is **not established** whether the data-bootstrap interval already absorbs the numerical spread. The A3 verdict (a reproducibility limit) is unaffected. |
| M4 | MEDIUM | The development-exit change turned a certain development failure into a pass: under the original text R fails (K2 median 1.002×, K3 1.035× B0). The change was declared before any candidate data and argued from D7; the +10% tolerance never came into play | **ACCEPTED.** The outcome states explicitly that it was a declared weakening of the campaign-internal screen and that R would have failed without it. |
| L1 | LOW | the A4 scope depends on the deformations counted: 20 cells with W1–W3; 16 with the GiBUU anchor added; 5 with q3 as well | **ACCEPTED**, reported. |
| L2 | LOW | the plan §6 5% projected-σ stability quantity (contract K4) was not computed; the seed probe is empty by construction | **ACCEPTED**, recorded as not computed. |
| L3 | LOW | the governing no-revision reason is the contract's: revisions happen only at development, and A_FAIL is terminal; "no fresh sample" is additional | **ACCEPTED**, corrected. |
| L4 | LOW | R − B0 on data (median 0.28%) sits at the rounding-noise level (0.777 data-σ against 0.783); only its tail (J161, B0's largest nominal bias) reads as a method effect | **ACCEPTED**, stated. |
| L5 | LOW | the k5_b16 crash cause is only partly identified (a segfault while printing an unseen exception in the post-run inventory); the products are unaffected | **ACCEPTED**, the incident record is updated. |
