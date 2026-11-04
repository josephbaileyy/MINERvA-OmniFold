# SCOPE: the second referees' analysis requests (a)–(g), scoped and priced (2026-11-04)

**Asked for by** the director, for Joseph. Joseph asked for the new analysis requests of the 2026-11-04 referees to be
scoped and priced, as #713 did for the bias and the stabilisation.
- The director's brief names seven items.
- For each item it asks for: at least one design and "do nothing, and why"; what the design closes; the paper change,
  with the direction of the caveat count; compute; knock-on; admissibility; calendar; risk; and Joseph's decisions.
- The report ends with a ranked recommendation (§9).

**Done by** the limitation-resolver lane.
- Read-only, on a worktree of origin/main `c5e42840` (the merge of #757, which holds the referee records).
- No jobs, no cluster contact, no timing probe, no paper edits.
- One independent read (Gemini via agy, `--sandbox`) is recorded in §10.

**CITABLE FOR:**
- the designs;
- their prices, from measured unit costs, with the arithmetic labelled as mine;
- the knock-on lists;
- the admissibility readings;
- the evidence already on main that bears on each request, with its path and line.

**NOT CITABLE FOR:**
- a decision, a declaration or a campaign;
- any physics claim;
- a probability, or a caveat count. Every caveat direction here is my judgement: no blind coder measured them, unlike
  #713 §4, because this report drafts no paper text.

**Path legend.**
- `RR/` = `secondary-results/referee-rerun-20261104/`, at `c5e42840`. Referee 1 there is Sonnet, Referee 2 is Gemini.
- `SB/` = `secondary-results/scope-bias-stabilisation-20261102/` (#713).
- `INV` = `secondary-results/referee-and-qualifications-20261101/inventory-answer.txt` (the 11-01 inventory). Its Q
  numbers are used here.
- `5dc/` = `docs/orchestration/state/measurement-paper/5d-community-20261024/`; `LPA` = `5dc/LIMITATION-PLAN-ADDENDUM-20261028.md`.
- `IBU1` = `docs/orchestration/state/2d-closeout/stageF/methods/ibu1/REPORT.md`.
- `PB` = `docs/analysis-note/paper_body.tex` at `c5e42840`.
- `DEC-…` files are in `docs/orchestration/`.

**Unit costs used throughout:**
- the 5D estimator, configuration (e): **0.022828 CPU node-h per unfold**, packed 8 per node
  (`5dc/FD-1B-STAGED-DECLARATION.md:530`, as `SB/REPORT.md:71` cites it);
- 2D (RE-2's measured units, `5dc/COV2D-SCOPING.md:91-97`):
  - central run **0.0843**;
  - universe **0.1220**;
  - lateral **0.1715**;
  - statistical replica **0.0489**;
- binned IBU, IBU-1's whole run: **1.0652 node-h** (`IBU1:180-187`).

No design here needs GPU.

## 0. What the decisions already on main settle, before any design

- **No fake-data bias term.** Neither A1 (assigned) nor A2 (data-reweighted) is built. "Item A is decided with the
  measurement-or-methods-study framing, once coverage and the run-period diagnosis report. No cell merge is made"
  (`DEC-20261102-joseph-bias-and-stabilisation-routes.md:85-89`).
  - The run-period diagnosis has now reported (`DEC-20261104-joseph-rpd-sentence.md`). Coverage has not: 1B stage 1
    waits for the B4 probe (`DEC-20261102-…:81-84`), which is stopped until its addendum is bound.
  - So (a), (e) and (f) sit inside a decision Joseph has deferred, not one he has closed.
- **Cell merges after the data read.** "Cell merges or new cuts after the data read stay inadmissible"
  (`DEC-20261027-joseph-measurement-framing-and-limitation-scoping.md:45-46`). Joseph "may still change R00–R15, since
  the definition is his. Any such change is labelled post hoc wherever it is reported" (`5dc/FD-DIRECTOR-RULINGS.md:30-33`).
- **The low-stability cells are disclosed, with no stability rule, "for now"**
  (`DEC-20261024-joseph-h2-16-cell-definition.md:42-43`).
- **A reconstruction-level read of the data is a read.** It is admissible only with its recipe frozen and committed
  before the data/MC ratio is computed (`5dc/FD-DIRECTOR-RULINGS.md:63-68`, the F1-W ruling).
- **The estimator.** Any change after Stage G's read is admissible only if declared before any new data read, and chosen
  on simulation. "No hyperparameter search was performed on data" (`PB:57`) stays true only under that rule
  (`SB/REPORT.md:221-225`).
- **No independent generator with MINERvA's detector response exists in this project** (`2d-closeout/stageD-inputs/REPORT.md:68`,
  row 3: "No detector-simulated alternative-generator sample exists").
- **None of (a)–(g) touches the interval-coverage item.** Both referees list coverage among the items that disqualify the paper together
  (`RR/sonnet-referee-answer.txt:154-160`; `RR/gemini-referee-answer.txt:20-24`).

## 1. Calendar used by every item

| date | what | source |
|---|---|---|
| 11-06 17:00 | HPSS back | `RECORD-20261102-director-hpss-deferral.md:6` (as `SB/REPORT.md:229`) |
| 11-09 | 5D per-playlist universe loops exposed on pscratch. A verified CFS copy exists | `5dc/FD-CT-RETENTION.md:64`; `DEC-20261101-joseph-eventloops-copy-to-cfs.md:28, 40` |
| 11-22 | their merge exposed. No copy; it can be rebuilt from the twelve | `5dc/FD-CT-RETENTION.md:65`; the decision's `:33` |
| **12-01** | cov2d's latest bulk submission | `5dc/fd/receipts-cov2d/staging/STAGE-REPORT.md:13` |
| 12-03 | W2b dumps and loops exposed (CFS copy) | `5dc/FD-CT-RETENTION.md:59-60` |
| 12-09 / 12-10 | the 12 per-playlist 2D universe and CV omnifiles exposed | `5dc/COV2D-SCOPING.md:255-256` |
| 12-15 | MP-1 S1 loops and lateral dumps exposed (C_resp's species and RPD's zero loops). **No copy** | `5dc/FD-CT-RETENTION.md:61, 63`; `5dc/FD-RPD-DECLARATION.md:174` |
| **12-19** | `$UNI`, the 2D universe omnifile, exposed; it is cov2d's basis | `5dc/COV2D-SCOPING.md:252, 259` |

Exposure is atime plus 8 weeks (`5dc/COV2D-SCOPING.md:245-246`), and files are never touched to reset it.

## 2. (a) DATA-DRIVEN PRIOR (Sonnet 11)

**The request.** Reweight the prior to the unfolded data (or a smooth fit to it), re-unfold, and show the 16-cell
result is stable. Then run the bias tests with that prior as the simulation (`RR/sonnet-referee-answer.txt:111-115`).

**What is already known.**
- #713's A2 is the same reweight used as a covariance term. Joseph declined the term (§0).
- Sonnet's request is a stability test and a re-based fake-data table, not a term. It is a different object, built from
  the same reweight.
- The paper's iteration test is relevant here (`PB:59`). The estimator "keeps five iterations because 10, 15, or 20
  iterations did not reduce its model dependence".
  - **Reweighting the prior to the unfolded result and re-unfolding is, in binned IBU, exactly the next iteration.**
    For OmniFold it is so only approximately, because the trees are retrained on the new base density (my reading;
    the consult in §10 makes the same correction).
  - So a re-unfold on the unfolded result's own reweight is expected to move the data result about as K 5 → 10 does.
  - Only a reweight that differs from the unfolded weights, such as a smooth fit or a per-cell step, tests something
    new.

**Design a1. A declared stability test with a frozen per-cell or smooth prior reweight. Printed as a sensitivity, never as the reported value.**
- **Recipe, frozen and committed before any ratio is computed** (the F1-W rule):
  - the reweight's form: per-cell piecewise constant on R00–R15, or a declared smooth function;
  - its smoothing;
  - the iteration count;
  - the seeds.
- **Products:**
  1. the data re-unfold under the new prior;
  2. 50 paired bootstrap replicas, so the shift is judged against the noise of a difference, not σ;
  3. F0b's noise-free truths re-built about the new prior.
- **Closes:** Sonnet 11's "show the 16-cell result is stable". Product 3 also answers what the request is for, as
  the consult reads it (§10): whether the bias is an artifact of Tune v1's distance from the data (χ² 262). It does
  not close Gemini 1 or the IV H listing.
  - The listing grades truths against Tune v1's prior.
  - A re-based table answers a different question: the bias when the truth is near the data.
- **Paper change:** a sensitivity sentence or table row in Sec. IV H or VI. Caveat direction: **+1 to +2**, my
  judgement. #713 measured +3 for the same reweight used as a term (`SB/REPORT.md:349-350`).
- **Compute (CPU), arithmetic at 0.0228 per unfold:**

  | product | unfolds | node-h |
  |---|---:|---:|
  | data re-unfold | 1 | 0.02 |
  | paired bootstrap | 50 | 1.14 |
  | re-based truths | about 18 | 0.41 |
  | **total** | | **about 0.4–1.6** |

  The reweight build is unmeasured (`5dc/FD-PLAN.md:493`).
  <!-- absence-ok: restates FD-PLAN.md:493's own status for the F1-W build, as SB/REPORT.md:142 does -->
- **Knock-on:** none to the reported result or its covariance. It is beside them.
- **Admissibility:** a new data read, admissible with the frozen recipe. As a sensitivity it changes no estimator.
- **Calendar:** reads the 5D bkg-aware inputs. The pscratch copies are exposed from 11-09, after which it reads the CFS
  copies.
- **Risk:**
  - A small shift reads as "stable", but stability is not unbiasedness. The weakly identified directions that carry
    the bias move slowly under any prior change (§6).
  - A large shift is a new disclosure.

**Design a2. Adopt the data-driven prior as the reported prior.**
- **It is an estimator change after the read.** Its knock-on is #713's B list (`SB/REPORT.md:308-330`): a re-run of
  about 45–60 node-h at 1× per unfold (`SB/REPORT.md:267`), plus the laterals (which cannot be remade,
  `5dc/FD-1B-DECLARATION.md:99`) and s5p (208 node-h, or labelled).
- **Paper:** `PB:57` would need its qualification, so +1. Every χ² changes. 1B would have to run on the new prior.
- **Not recommended.** It is post hoc by construction, and it buys at most what a1 measures.

**a0. Do nothing.**
- **Why it is defensible:**
  - the paper already prints the prior's distance from the data: MINERvA Tune v1's χ² is 262 for 16 cells in Table III
    (`RR/manuscript.blind.txt:1131-1132`);
  - the referee's test is closest to "the bias when nature is near the data", which no one has measured;
  - Joseph's 11-02 answer defers A to the framing decision.
- **Residual:** Q35, unchanged.

**Joseph decides:** whether A is reopened now. If it is, a1's recipe, and whether a1 is printed in the paper or the note.

## 3. (b) VARIED-RESPONSE MOCK DATA (Sonnet 4)

**The request.** Mock data with a modified hadronic response, neutron content, resolution and species mix, plus
generators passed through the full detector simulation if available. Also an honest count of nontrivial tests
(`RR/sonnet-referee-answer.txt:52-58`).

**What is already known.**
- **3b ran response-mismatch closures** (`5dc/FD-CT-3B-REPORT.md:96-118`), at nominal truth, noise-free:
  - each species at its ±1σ: median |Δ|/σ 0.04–0.20, maximum 0.40;
  - a whole-recoil ±4% scale: median 0.50σ, maximum 0.97σ, Δᵀ M⁻¹ Δ ≈ 7.1.
  - The paper does not print them. `PB:182` still says "The simulated detector response is not probed".
  - No threshold is set, because Joseph deferred the closure settings on 10-14 (`5dc/FD-CT-3B-REPORT.md:79`).
- **C_resp's scope is a ±1σ scale per species.** It does not cover neutrons, muon deposits, energy dependence,
  resolution or a larger amplitude (`5dc/LIMITATION-PLAN-ADDENDUM-20261028.md:176-189`).
  - Neutrons are absent by construction: MAT turns neutron response off by default (`:184-185`).
- **Generators through the full detector simulation: UNAVAILABLE.** Only MINERvA could supply them
  (`2d-closeout/stageD-inputs/REPORT.md:68`). Asking is outward contact, which is Joseph's.

**Design b0. Print 3b's closures as a bounded statement** (INV Q38).
- **Closes:** the "not probed" half of Sonnet 4 for the tested forms only.
- **Paper change:** `PB:182`'s "not probed" becomes a sized statement with its scope. Caveat direction: **0**, my
  judgement: one negative becomes one scoped positive.
- **Compute:** 0. Knock-on: none.
- **Admissibility:** reporting a completed, bound run.
- **Joseph decides:** the threshold, or "descriptive, no threshold". Both are his after the 10-14 deferral.

**Design b1. 3c: new variants outside C_resp, each followed by 3b's closure** (`LPA:256-264`).
- **The variants:** the three neutron bins (in the tuples); a resolution smear; an energy-dependent scale; a larger
  amplitude.
- **Why each needs new event loops.** The 5D dumps store the five reconstructed observables but not the calorimetric q₀
  (`nd-unfolding/nn_dump_inputs.py:92-103`; `s5p_input_dumps.py:171-177`). Reconstructed q₃ and W combine the muon with
  q₀ (`PB:37`). A smear applied in the dumps alone would move E_avail without moving q₃ and W consistently.
- **Compute:**
  - about 0.86 node-h per ±1σ pair (`LPA:261-264`), so about 2.6 for neutron, smear and energy dependence
    (arithmetic);
  - plus 0.054 per data unfold if a C_resp extension is wanted;
  - plus development, which is unpriced. The event-loop code for a smear or an energy dependence does not exist
    (`LPA:263-264`).
  <!-- absence-ok: restates LPA:263-264's own pricing status, which calls that code development -->
  - Wall-clock up to 6.5 h per playlist, under 12 h.
- **Knock-on:** none if descriptive. If a component is added, every readout against the reported matrix (#713's A
  list, `SB/REPORT.md:91-99`) is recomputed at 0 node-h.
- **Admissibility:** forms, amplitudes and a threshold must be declared before any product is read
  (`LPA:280-281`). Adding a component is post-read and Joseph's (`LPA:285-286`).
- **Calendar:** new loops come from the AnaTuples. 3b's existing inputs (MP-1) are exposed from 12-15, with no copy.
- **Risk:** INV Q16 rates it "60% to get a number; under 10% to remove the sentence" (`INV:132`).
- **Joseph decides:** the forms, amplitudes and threshold; and, on a fail, whether a component is added.

**Design b2. Response mismatch at a non-nominal truth.** The GiBUU hybrid and the q₃ tilt, with W2b's ±4% response.
- **What it tests.** Whether the response mismatch and the prior bias add or cancel at the truths that fail. Sonnet's
  request implies this, and no run has tested it.
  <!-- absence-ok: scoped to 3b's declared design, nominal truth only (FD-CT-3B-REPORT.md:79, the readout's "what" label) -->
- **Compute:** 4 closures × 0.045 (`5dc/FD-PLAN.md:472`) = 0.18 node-h (arithmetic). W2b's dumps have a CFS copy.
- **Joseph decides:** whether to add it to a 3c declaration.

**b0′, the count.** Sonnet's "Report the count of nontrivial tests honestly" (`RR/sonnet-referee-answer.txt:56, 58`)
is wording in the IV H table. It needs no compute and belongs to the paper lane.

**Do nothing, and why.** "Not probed" is true and is stated. b0 costs nothing and changes the statement only in form.

## 4. (c) THE JOINT-TEST ESTIMATOR IN 2D, AND A BINNED CROSS-CHECK OF THE 2D SHAPE DIFFERENCE (Sonnet 9, Gemini 3)

> **Ownership note.** The director has said a Codex lane may own the diagnosis of (c), (d) and (e). If it does, this
> section's designs and prices stand, and the diagnosis is that lane's.

**The requests.**
- Sonnet: run the joint-test estimator in 2D against the published result; explain the shape difference by comparing
  with a binned unfolding; reconcile "No hyperparameter search was performed on data" with the learner choice
  (`RR/sonnet-referee-answer.txt:90-97`).
- Gemini: a differential comparison of the two pipelines, testing the background refinement, unmatched-event
  efficiency, the beam angle and the iteration count (`RR/gemini-referee-answer.txt:45-48`).

**What is already known.** The brief says nobody has worked on the difference. Several of Gemini's tests have in fact
been measured, but on an earlier estimator lineage.
- **Iteration count: negligible.** LightGBM 5 → 10 moves χ²/ndf by +0.01, 2.645 → 2.657
  (`docs/analysis-note/app_statmethods.tex:552`).
- **The background treatment moves it:**
  - 2.654 with purity subtraction;
  - 2.270 with the refined negative-weight subtraction (the quoted value);
  - both at seed 42 (`:540-549`).
- **The learner moves it by about one unit:**
  - exact-split 3.66;
  - HistGBT 2.70 ± 0.04 over 10 seeds;
  - LightGBM 2.65 (`:540-552`).
- **The integral agrees.** IBU on a 1D projection of the same inputs and 2D OmniFold each reproduce the published
  integral to ≤ 2.5% (IBU 0.988 on p_T and 0.976 on p_∥, OmniFold 1.005;
  `2d-unfolding/ibu_1d_projection/README.md:3-13`). That is integrals, not the shape.
- **The tension's location in (p_T, p_∥) was examined for the exact-split cross-check.** It is concentrated on the
  low-p_T peak, dominated by the flux and Muon_Energy bands (`docs/analysis-note/app_statmethods.tex:557`). It has
  not been examined for the quoted LightGBM value.
  <!-- absence-ok: scoped to app_statmethods.tex:557, whose conclusion separates the exact-split case from the LightGBM central value -->
- **A paired IBU-against-OmniFold design exists but has no committed result.**
  - `2d-unfolding/ibu_omnifold_paired_cdelta.py` is a paired-bootstrap C_delta on the 14 × 16 grid at five iterations.
    Its contract is `docs/STATVAL_REPAIR.md:165-171, 209-215`.
  - The hits are a precision-bias brief and a deploy manifest. No result was found.
    Search: git grep -n -iE 'cdelta|C_delta' -- docs/orchestration/state docs/orchestration/*.md KNOWN_ISSUES.md @ c5e42840
- **(e) and (f) differ little.** Both are LightGBM at five iterations, 100 trees and 8 leaves, with the same refined
  subtraction. (e) is the deterministic variant (`PB:55`).

**Design c1. (e) run in the 2D configuration against the published result.**
- **Products:** one central run, plus 50 paired statistical replicas of (e) − (f) on the same draws, so the two
  estimators' difference is judged against its own noise (Sonnet's "expected uncorrelated difference",
  `RR/sonnet-referee-answer.txt:93`).
- **Compute:** 0.08 + 50 × 0.049 ≈ **2.5 node-h** (arithmetic). A full universe ensemble for (e) in 2D adds 175 ×
  0.122 ≈ 21.4.
- **Expected information: low, in my judgement.** (e) and (f) share the learner, capacity and background treatment, and
  the learner band (2.27–3.66) is measured.
- **Closes:** Sonnet 9's literal request, and limitation 6's "not combined" in part.
- **Paper change:** `PB:55` "not combined" could become a measured agreement. Caveat direction: **0 to −1**.
- **Knock-on:** none.
- **Admissibility:** a descriptive comparison. It does not change (f).

**Design c2. A binned IBU on this analysis's own 2D inputs, against the published result and paired with (f).**
- **What it tells apart.** The input side (the open-data reprocessing, background, efficiency or flux) from the
  algorithm side. The 2.27 χ²/ndf is (f)'s descriptive distance from the published result (`PB:92-94`).
  - If this analysis's IBU on its own inputs sits about as far from the published result as (f) does, the difference
    is in the inputs, and Gemini's per-ingredient tests are next.
  - If the IBU sits close to the published result while (f) does not, the difference is algorithmic.
  - Either outcome localises the difference by one level. Neither identifies the cause.
- **Products:**
  - IBU on the published binning, with the published iteration count read from the published paper (not from memory);
  - the paired C_delta of `ibu_omnifold_paired_cdelta.py`, with 200 paired replicas and a rank cut declared in advance;
  - a second pass on the universes, if wanted.
- **Compute (arithmetic):**

  | part | node-h |
  |---|---:|
  | IBU side | ≈ 0, as RooUnfold is binned and fast |
  | (f) side, 200 replicas × 0.0489 | 9.8 |
  | universe pass, 175 × 0.122 | 21.4 |
  | **total** | **about 10, or about 31 with the universes** |

  Whether the existing 300 Q_R replicas can be re-drawn bit for bit for the IBU side is unchecked. If they can, the (f)
  side costs 0.
- **Inputs:**
  - the 2D CV omnifile;
  - `$UNI`, exposed from 12-19;
  - the RooUnfold build `unbinned_unfolding/build/libRooUnfold.so`, whose presence on the cluster is unverified.
    Checking it is a 0 node-h listing.
- **Paper change:** Q21's "The source of the shape difference has not been identified" (`PB:94`) narrows to one of two
  sized statements. Caveat direction: **0 to −1**, my judgement.
- **Knock-on:** none. It is descriptive, and the IBU is not a reported estimator.
- **Admissibility:**
  - the comparison is already printed;
  - the IBU is a diagnostic, declared before it is run;
  - the iteration count is the published one, so it is not tuned.
- **Calendar:** before 12-19. It reads `$UNI` read-only beside cov2d's bulk, which is due by 12-01.
- **Risk:** the paired C_delta has the finite-ensemble issue its brief records: factor 0.4925 at rank 100
  (`BRIEF-20260822-oi137-finite-N-precision-bias-exposure.md:235, 348-350`). The rank cut and the correction must be
  declared in advance.

**The data-choice sentence** (`PB:57` against `PB:96`) is a wording reconciliation with no compute. It belongs to the
paper lane, through the PRD read.

**Do nothing, and why.**
- Q21 is K in the inventory: "No recorded route" (`INV:78`).
- The paper prints the distance as descriptive.
- c2 is the recorded route, at about 10 node-h.

**Joseph decides:** c2's declaration; whether c1 rides with it; whether the Codex lane owns it.

## 5. (d) RUN-PERIOD CAUSE AT RECONSTRUCTION LEVEL (Sonnet 6)

> **Ownership note.** As in §4.

**The request.** "First compare the data and simulation per playlist at reconstruction level, before unfolding".
Establish data, simulation or unfolding; correct it or justify excluding periods; otherwise state a conservative
inflation (`RR/sonnet-referee-answer.txt:67-73`).

**What is already known.**
- **Reconstruction level, in muon kinematics only, has been compared.** `2d-closeout/playlist-spread-20261014/REPORT.md`
  does this, on the 2D (May CV) loops.
  - 1G–1M steps up at 8 GeV/c in p_∥: 0.954–0.989 below, 1.022–1.025 above (`:140`).
  - 1N–1P is a broad excess of about 5% (`:126-136`).
  - The 1N–1P step is in reconstructed fiducial events per POT (`:193-200`).
  - Flux files map 1A–1F → 1D, {1G, 1L, 1M} → 1M and 1N–1P → 1N (`:154-161`).
- **The 2D step survives unfolding at about its reco-level size**, +6.94% ± 0.41 in the double ratio
  (`2d-closeout/period-unfold-20261014/REPORT.md:3, 57`).
- **RPD (5D):**
  - SEES the step;
  - R1 OTHER, carried by {1L, 1M}, partial {1G, 1N, 1P};
  - R2 CLUSTERED, with p_flux = 1/9,240 against p_era = 5.17 × 10⁻³ (`DEC-20261104-joseph-rpd-sentence.md:11-19`).
  - No outcome supplies a cause, and Joseph's decision keeps "The cause is not known" (`:24, 51`).
- **Not yet done:** reco-level per-playlist comparisons in the hadronic axes, E_avail, q₃ and W, with the 5D selection.
  <!-- absence-ok: scoped to the two reports above, which compare p_T and p_∥ only (playlist-spread-20261014/REPORT.md:126-148; period-unfold-20261014/REPORT.md:50-60) -->

**Design d1. Five-observable reco-level data/MC per playlist, from RPD's staged per-playlist dumps.**
- **Inputs.** The 12 per-playlist lateral npz files and background dumps under `/pscratch/sd/j/josephrb/fd-rpd-20261103`.
  They hold `MCreco`, `w_reco`, `pass_reco`, `measured`, `data_pot` and the background arrays (`nn_dump_inputs.py:92-103`;
  `s5p_input_dumps.py:171-183`).
- **Products:** per-playlist data/MC ratios on the 16 cells and on each reco marginal. Each is normalised by POT and in
  shape, with bootstrap noise and declared bins.
- **What it can show.** Whether the 1L/1M carrier pattern exists before unfolding in E_avail, q₃ or W, or only in p_∥.
  That answers Sonnet's "data, simulation or the unfolding" for the unfolding branch only.
- **Compute:** **0 node-h**, login or DTN, every read O_NOATIME.
- **Paper change:** none directly. A localisation is wording that needs a declaration licensing it, as RPD's §6 did.
  Caveat direction: **0**.
- **Knock-on:** none.
- **Admissibility:** a reconstruction-level read of the data, admissible only with the recipe frozen first (§0).
- **Calendar:** RPD's job A wrote these dumps on or after 11-03. Their atimes are unmeasured: exposure would be about
  12-29 if the oldest atime is 11-03 (arithmetic).
  <!-- absence-ok: the atimes were not read because this scope made no cluster contact; the sentence prices a date, it claims no result is absent -->
- **Risk:** low. A positive result in the hadronic axes widens the problem rather than closing it.

**Design d1′ (from the consult, §10). Split d1 by the muon's momentum measurement.** The consult proposes separating
the checks by the muon spectrometer's reconstruction category, since the step sits in p_∥ near 8 GeV/c.
- I have not verified which category flag the 5D loops carry, or where its boundary falls in p_∥. The consult's
  premise about MINOS-matched acceptance is its own and is not checked here.
- **Compute:** 0 node-h if the flag is in the dumps; otherwise it rides on d2's E_ν pass.
  <!-- absence-ok: an unverified premise of a proposed design, stated as such; no claim that a result is absent -->

**Design d2. A flux-swap test at reco level.** Reweight each MC playlist from its own flux file to another group's flux,
by true E_ν, and see whether the 1G–1M p_∥ step follows the flux file.
- **Why it is sharp.** The flux grouping is the partition R2 rejects at its floor, and the 2D report infers that a
  flux-shape difference would produce the step (`playlist-spread-20261014/REPORT.md:139`). The inference is untested.
  <!-- absence-ok: the report itself labels §3.4's mechanisms inferences, not tested (playlist-spread-20261014/REPORT.md:33) -->
- **Inputs.** The dumps do not store E_ν (as d1), so the pass reads E_ν from:
  - the 12 zero loops (exposed from 12-15, no copy);
  - or the CFS bkg-aware copies.

  The 12 per-playlist baseline flux files exist (`5dc/FD-RPD-DECLARATION.md:153, 163`).
- **Compute:** a dump-with-E_ν pass, at about 0.027 per playlist dump, so about 0.33 for twelve (arithmetic, from
  `LPA:263`). Plus small code: a reweight by the flux ratio at true E_ν.
- **What it can and cannot show.**
  - It can show that the step tracks the simulation's flux-file assignment, or that it does not.
  - It cannot show which period is right.
  - Any paper sentence needs licensed wording declared before the run.
- **Admissibility:** as d1.
- **Risk:** the flux files may differ in more than shape (their integrals differ by +0.99% and −0.42%, `playlist-spread-20261014/REPORT.md:159-161`).
  The declaration must split shape from normalisation.

**Design d3. Correct or exclude.**
- **What it means.** Either a correction, if d2 finds the simulation's flux assignment at fault, or excluding periods.
- **Both are post hoc** after the read (`DEC-20261027-…:45-46`) and Joseph's.
- **Knock-on:** the central value, 5B and C_PL,5D, and every χ². That is the full 5D readout chain at 0 node-h, plus a
  re-run of the period unfolds (5B, 0.90 node-h, `5dc/FD-CT-5B-REPORT.md:59`). An exclusion also lowers the POT.
- **Not priced further** until d2 reports.

**d4. The prepared MINERvA question.** This is outward contact, and Joseph's alone. INV judges the chance of a cause
from this project's own analyses at 10–15% (`INV:133`); an outside explanation is the other route (`INV:179`).

**Do nothing, and why.** The licensed R2 sentence goes in. "The cause is not known" stays in every outcome. The block
stays "built from observed differences" (Q19, K) whatever d1–d2 find.

**Joseph decides:** d1's and d2's declarations (or the Codex lane's), and d4.

## 6. (e) FAKE-DATA BIAS: WHAT WOULD ACTUALLY REDUCE IT (Sonnet 3)

> **Ownership note.** As in §4, for the diagnosis of the cause.

**Sonnet's argument.** The paper interprets the residual as "regularization bias, because it persists over the tested
iteration numbers and classifier capacities" (`PB:131`). Sonnet says persistence under more iterations and more
capacity "is evidence against regularization bias, where the bias should shrink"
(`RR/sonnet-referee-answer.txt:44-50`).

**What the records measure** (binned, exact response, J cells, development departures):
- **D-ID** (`next-preparation-20261009/d-id/REPORT.md`):
  - At K = 5 the GBDT's J median residual equals exact binned IBU's (GiBUU 9.5% against 8.3%; W1 5.4% against 5.4%;
    `:432-440`).
  - **With longer exact iteration the GiBUU residual falls:** 3.3% at K = 200, 0.8% after 10⁵ iterations. W3 and q₃
    do not fall (`:441-452`).
  - Capacity 400/31 barely moves it (`:466`).
  - The residuals sit in functionals whose binned CR widths exceed 10%, median 31% (T1) and 58% (T2) (`:518`).
  - The verdict: "Finite-iteration regularization: consistent, and dominant at K = 5"; GBDT approximation is "not
    supported as the main cause" (`:524-533`).
- **IBU-1:** at the four generator-sized departures, IBU's median residual is 0.77–1.31 × OmniFold's
  (`IBU1:57-60`).

**My reading of the argument.**
- **Sonnet is right that the paper's stated ground does not carry the attribution.**
  - Persistence over K = 10–20 is what slow convergence in weakly identified directions also gives.
  - The paper cites no evidence that separates the two.
- **Sonnet's inference is not what the records show.**
  - In the binned exact case, the GiBUU residual does shrink with iteration. It shrinks slowly, by a factor of about 2.5
    from K = 5 to K = 200, while the functionals carrying it have >10% widths.
  - That is regularisation bias traded against variance, not its absence.
  - For W3 and q₃ it does not shrink, so the attribution does not hold uniformly.
- **The test Sonnet asks for** ("compare with a binned iterative Bayesian unfolding … to separate algorithm from
  classifier") **has been run**: D-ID and IBU-1. But it was run on J cells and development departures, not on the 16
  reported cells under (e)'s refined pipeline. (g) would run it there.
- **Two limits the consult raises (§10), which I accept:**
  - D-ID's convergence is exact binned algebra. A GBDT density ratio need not converge the same way, and many
    iterations in an unbinned estimator may mostly add variance.
  - Support mismatch (truth mass where Tune v1 has almost none) is a separate mechanism that more iterations cannot
    fix. Sonnet names it, and nothing here separates it.
- **Paper location:** `PB:131`'s attribution sentence. The change is to its ground (D-ID and IBU-1, scoped), not to
  its claim. Caveat direction: **0**. Drafting it is the paper lane's.

**Does (a) address it?** No, in my judgement.
- The listed failures grade truths against Tune v1's prior. A data-driven prior moves the prior, not the truths.
- A re-based table (a1) measures the bias at truths near the data. That is a different quantity.
- And re-unfolding on the unfolded result's own reweight is approximately more iterations (§2), which the records show
  trades bias for variance.

**What would actually reduce it, beyond #713's A1–A3:**

| route | expected effect | price | admissibility | recommendation |
|---|---|---|---|---|
| **e1, far more iterations, with the variance carried** | lowers the GiBUU-like residual where it is regularisation (D-ID), and raises σ in the weakly identified directions; does not help q₃ or W3 | probe: 18 noise-free F0b closures at K ∈ {20, 50, 100} ≈ 18 × (4 + 10 + 20) × 0.0228 = **14.0**, plus a 50-replica bootstrap at K = 50 ≈ **11.4**, so **about 25–40** (arithmetic; it **assumes cost ∝ K**, unmeasured). Adoption: about ×10 the 1× re-run, **about 450–600**, near half the balance (1,025.5, `SB/REPORT.md:332-333`) | an estimator change chosen on simulation, as B4. K must not be chosen on data | **not now.** At most, a K readout added to B4's successor |
| **e2, report identified functionals** (coarser cells, or D-ID's identified set) | removes the bias by not reporting what the data cannot fix | 0 node-h for linear combinations | a post hoc definitional change, Joseph's. Overlaps (f) | only under (f)'s decision |
| **e3, a different learner or architecture** (Gemini 1(i)) | **not expected to help.** D-ID's approximation share is 0.014, and exact binned IBU leaves the same residual | B4-sized probe | as B4 | no |
| **e4, a bias term** | removes the listing only by construction | 0 | **decided against** (§0) | no |
| **e5, cell merges** | not expected: R02 and R06 hold 38.1 of the χ² of 171.0, and the 8-cell variant still fails (`SB/REPORT.md:410-423`) | 0 | post hoc, Joseph's | see (f) |
<!-- absence-ok: 'assumes cost ∝ K, unmeasured' labels an assumption of this report's own hypothetical probe price -->

**Do nothing, and why.** The records say the bias is mainly a property of the information in the data at these truths,
not of the implementation. Only trading it for variance (e1) or not reporting the directions that carry it (e2) reduces
it, and neither is free. Q35 stays K.

**Joseph decides:** whether e1's readout joins B4's successor; whether e2 is considered under (f).

## 7. (f) THE LOW-STABILITY CELLS R02, R06, R10 AND R15 (Sonnet 7; Gemini 6)

**The request.** Redefine the cells with a defensible stability criterion, show by generator-sized closure that each
retained cell is recovered, and do not report failing cells as measurements (`RR/sonnet-referee-answer.txt:75-80`).
Gemini asks for merges to stability ≥ 50% (`RR/gemini-referee-answer.txt:60-63`).

**What "post hoc" means here.**
- **The 16 cells' rule ran before any H2-level quantity from an (e) data product.** It is a purity merge, on MC keys
  only, committed before it ran (`DEC-20261024-joseph-h2-16-cell-definition.md:15-20`).
- **Any change now comes after:**
  - the data result;
  - F0 and F0b (whose grades divide by quantities from data);
  - Stage G.

  So neither of the H2 rule's conditions can hold (`5dc/FD-DIRECTOR-RULINGS.md:23-29`).
- **A change is therefore Joseph's definitional act, labelled post hoc wherever reported** (`:30-33`). Its χ² and
  p-values are no longer predeclared, because the change is chosen knowing which cells fail.
- **#713's finding:** merging would not be expected to remove the GiBUU failure. Under the reported covariance R02 and
  R06 are the only |z| > 2 cells, but their z² sum to 38.1 against χ² 171.0. F0b's 8-cell variant without R06 and R07
  still gives 133.91 for 8 degrees of freedom (`SB/REPORT.md:410-423`).

**f0. Keep the disclosure (the decided state).**
- `PB:280` lists the four cells and the stability range.
- **Paper reports:** 16 cells, as now. Caveat direction: 0.

**f1. Flag the four rows in Table II.**
- **Compute:** 0. Wording only.
- **Paper reports:** 16 cells, with four marked "migration dominated". Caveat direction: **0 to +1** (my judgement).
  INV's §6.2 says to print the cells in the note first (`INV:220`).

**f2. Merge by a stability rule stated in simulation quantities, as a post hoc second table.**
- **Method.** A linear map f′ = A f, C′ = A C Aᵀ (`INV:138`).
  - The rule is written in MC quantities only, for example the H2 greedy merge with stability in place of purity at a
    declared floor, and committed before A is applied.
  - The merged-cell fake-data grades are linear maps of F0b's per-cell biases. If the committed readouts carry the bias
    vectors, they are recomputed at 0 node-h; otherwise F0b's products are re-graded.
- **Paper reports:** the 16-cell table, as declared, plus a merged table labelled post hoc. Whether the 16-cell table
  must stay is not stated by any ruling; I read the post hoc label as requiring it.
  <!-- absence-ok: scoped to FD-DIRECTOR-RULINGS.md §1 (:23-33) and DEC-20261027…:45-46, the two rulings on merges, read in full -->
- **Expected:** the GiBUU hybrid still listed (#713). The merged cells' σ is not computed here.
- **Compute:** 0 node-h.
- **Knock-on.** Every 16-cell readout gains a merged version at 0 node-h:
  - Stage G (Table III);
  - GENCMP;
  - X's quadrant sums;
  - J2's columns;
  - GiBUU's eight-cell set. R02 and R10 are in it, so its ndf drops.

  Not touched:
  - 1B's 16-cell gate. Its declaration would need an amendment if 1B ran on merged cells.
  - RPD's record. It was run on 16 cells and stays as run.
  - cov2d. It is 2D.
- **Caveat direction:** **0 to +1**. One caveat (Q42) narrows; one post hoc label is added; the listing stays.
- **Risk:** it reads as reshaping the grid to the failures, and it does not remove them.

**f3. Drop the four cells.**
- **Paper reports:** 12 cells.
- **Its cost to the result:** the dropped cells' signal joins the unreported share (Q13, now 0.47%, `INV:69`). GiBUU's
  comparison falls to 6 cells.
- **Compute:** 0. Knock-on: as f2.
- **Caveat direction: +1**, because the unreported share grows and is post hoc.
- **Not recommended.** A reader loses the four cells' values, which the paper now reports with their limitation.

**Do nothing, and why.** Joseph's 10-24 "no for now" stands. The merges #713 tested on paper do not remove the
failure. Both referees nonetheless call the cells disqualifying as reported (`RR/sonnet-referee-answer.txt:160`;
`RR/gemini-referee-answer.txt:101-104`).

**Joseph decides:** f0, f1 or f2. If f2, the stability floor and the rule, which must be written before A is computed.

## 8. (g) A BINNED UNFOLDING HEAD-TO-HEAD ON THE 16 CELLS (Sonnet 8)

**The request.** "Either a head-to-head comparison against a conventional binned unfolding (same cells, same data, same
systematics), or toning down the motivation" (`RR/sonnet-referee-answer.txt:82-88`).

**What is already known.**
- **The paper already concedes the limitation.** Its limitation 3 says the tests "show no evidence of additional
  discrimination beyond matched coarse projections" (`PB:281`).
- **IBU-1 exists, at J cells:** binned IBU against OmniFold on the same pseudo-experiments, with data comparators
  pinned (`IBU1:196`). Its run cost 1.07 node-h. The 16 reported cells are not in it.

**Design g1. Binned IBU on the 16 cells, beside (e).**
- **Setup:** same MC, same data, IBU's binned background subtraction (the refined negative-weight treatment is
  OmniFold's, so the two differ here), five iterations declared in advance (IBU-1's K), and a
  reco binning declared in advance (the 109 J cells or the fine map `930326a3`). Reuse `nd-unfolding/ibu1/ibu1.py`.
- **Products:**
  - the data central value;
  - 50 paired bootstrap replicas;
  - F0b's truths, noise-free (binned, ≈ 0 node-h);
  - the 3 C_model vertices;
  - flux, interaction and detector universes.

  The universes need histogram fills from the 12 per-playlist universe loops: pscratch until 11-09, then the CFS copies,
  or the merge until 11-22.
- **Carried, labelled:**
  - the lateral block, which cannot be remade (`5dc/FD-1B-DECLARATION.md:99`);
  - C_resp, unless the MP-1 dumps are read before 12-15;
  - C_PL,5D.
- **Compute: about 1–5 node-h**, my estimate from IBU-1's 1.07. The universe fill is I/O-bound and unmeasured. A CFS
  read is DVS-slow on compute, so it should run on a login node or DTN.
  <!-- absence-ok: an estimate for an unrun design; 'unmeasured' scopes the price, not a result -->
- **Closes:**
  - Sonnet 8's head-to-head, with "same systematics" except the carried blocks;
  - Sonnet 3's algorithm-or-classifier split at the reported cells;
  - Q26 in part.
- **Paper change:** a comparison paragraph, or a column in Table II. Caveat direction: **+1 to +2**, my judgement: the
  carried blocks and the different background treatment travel with it. It would be **−1** if it replaced the
  motivation's hedge.
- **Knock-on:** none to the reported result.
- **Admissibility:**
  - It is a second estimator's data result, after (e)'s read. It is admissible as a declared cross-check.
  - It must not become the reported estimator, because that would be a post hoc estimator choice, and `PB:57` would
    fail.
- **Risk:**
  - If IBU looks better at 16 cells, it will be read as a reason to switch.
  - If it looks the same, it confirms "inverse-problem limited", and the motivation must still be toned down.

**g0. Tone down the motivation.**
- **Compute:** 0.
- **The change:** the abstract and Sec. I. This is wording, so it is the paper lane's, through the PRD read.
- **Caveat direction: 0 to −1.**

**Do nothing, and why.** Limitation 3 already states the result. A referee has asked for one of the two remedies,
however, and "do nothing" answers neither.

**Joseph decides:** g0, g1, or both.

## 9. Ranked recommendation

Ranked by information per node-hour, under the decisions in §0. Probabilities are not given. Each item's "closes" line
says what it can change.

1. **0 node-h, now:**
   - **b0**, print 3b as a bounded statement. Joseph chooses a threshold or "descriptive".
   - **(e)'s ground for `PB:131`**, D-ID and IBU-1, scoped. Paper-lane wording.
   - **d1**, five-observable reco per playlist, from RPD's dumps. It needs a frozen recipe and a go.
2. **c2**, this analysis's own IBU on the 2D inputs, paired with (f).
   - **Price:** about 10 node-h, or about 31 with universes.
   - **Why second:** either outcome localises the 2.27 one level (inputs or algorithm).
   - **Date:** before 12-19.
   - Run **c1** (2.5 node-h) with it. It answers Sonnet 9 literally, and the consult ranks it first (§10).
3. **g1**, the 16-cell binned head-to-head.
   - **Price:** about 1–5 node-h.
   - **Why:** it answers Sonnet 8 and Sonnet 3 at the reported cells.
   - **Date:** before 11-22 if it reads the merge; otherwise from the CFS copies.
4. **g0** with or without g1, through the PRD read.
5. **d2**, the flux-swap.
   - **Price:** about 0.33 node-h plus code.
   - **Date:** before 12-15 if it reads the zero loops.
   - **Condition:** only with licensed wording declared first.
6. **a1** as a printed sensitivity (about 0.4–1.6 node-h), only if Joseph reopens A. **a2 not recommended.**
7. **b1 and b2** (about 2.6 + 0.18 node-h plus development), only with forms and a threshold declared.
8. **(f): f0 or f1.** f2 only as a post hoc second table, if Joseph wants a merged view; it is not expected to remove
   the listing. **f3 not recommended.**
9. **e1:** not now. At most a K readout in B4's successor. **e3 and e4 no.**

**Candid judgement.** None of (a)–(g) moves interval coverage or the rounding instability, both of which both referees
list in the disqualifying combination. The cheapest moves that change what the paper can say are b0, c2 and g1, at about 0–15 node-h together.
The rest either measure a different quantity (a1), cannot remove the failure (f2, e4), or cost an estimator change
(a2, e1).

## 10. The independent read (Gemini)

**What ran.** agy, `gemini-3.8-flash-high`, `--sandbox`, from an empty directory, on 2026-11-04. Both files are beside
this report and listed in `SHA256SUMS`:
- `CONSULT-GEMINI-PROMPT.txt` (sha256 `8dfc45ee…`);
- `CONSULT-GEMINI-ANSWER.txt` (`117b5576…`, 12,574 bytes, verbatim; stderr was empty).

**What the consult saw.**
- The director's task text, with the referees anonymised (Referee 1 is Sonnet, Referee 2 is Gemini).
- Both 11-04 referee reports.
- This report before §10, anonymised the same way.

**Checked by reversing the substitution:**
- Both referee sections are byte-identical to `RR/{sonnet,gemini}-referee-answer.txt`.
- The report section differs from §§0–9 as committed in only two ways, and in the changes listed below:
  - the five `absence-ok` comments and the Search line's format, added for the pre-commit check;
  - the path legend's line, which the substitution made read "Referee 1 there is Referee 1".

**Changes made after the consult, because I accept the point:**
- **§2.** The prior-as-iteration equivalence is exact only in binned IBU. Also, a1's re-based table answers whether the
  bias is an artifact of Tune v1's distance.
- **§4.** The tension's (p_T, p_∥) localisation already exists for the exact-split case only.
- **§5.** d1′ is added (a split by the muon's momentum measurement), with its premise marked unverified.
- **§6.** Two limits: D-ID's binned convergence may not transfer to the GBDT; support mismatch is not separated.
- **§9.** c1 runs with c2.

**Accuracy fixes after the consult, not prompted by it:** a0's citation for Tune v1's χ² (now Table III); d1's
calendar (the dumps are job A's); g1's background treatment; f2's σ (not computed) and f3's reason; the candid
judgement (coverage and the rounding instability); one more `absence-ok` comment in §7.

**Where the consult differs, and this report does not follow it:**
1. **(c): c1 first, "mandatory".** It ranks c1 above everything, as the procedural answer to Sonnet 9. I agree it
   should run and have paired it with c2. I still expect c2 to carry the information, since (e) and (f) share the
   learner, capacity and background treatment.
2. **(f): f2 as the primary result.** It calls f0 and f1 "hiding behind an administrative procedural barrier". It
   would present merged cells at a stability floor of 40% or 50% as the primary result, labelled post hoc.
   - The barrier is a ruling of Joseph's, not this lane's: post hoc changes are his (`5dc/FD-DIRECTOR-RULINGS.md:30-33`).
   - Its effect on the failure is measured: the merges do not remove the GiBUU listing (#713).
   - Joseph should see both views. Under the measurement framing, both referees' text points toward f2 or f3
     (`RR/sonnet-referee-answer.txt:80`; `RR/gemini-referee-answer.txt:63`).
3. **(e): e1 "unviable".** It expects variance to explode. That is consistent with this report's "not now", and §6
   now carries the limit.
4. **(g): the "defensive posture".** It reads g1's risk line as hesitation. The risk named is that adopting IBU after
   the read would be a post hoc estimator choice. Reporting g1's outcome, whatever it is, is the design.
5. **(b): b0 does not answer Sonnet 4.** Agreed. §3 says it closes "the tested forms only". Its proposed truth-level
   hadron smearing "prior to feature construction" is b1's smear: the feature construction happens in the event loop,
   which is why b1 needs new loops.

**Where it agrees:**
- None of (a)–(g), alone or together, changes either referee's verdict. Coverage and the rounding instability are
  untouched.
- d1 is the right first step for (d).
- a2, e3 and e4 are rejected.
- g1 and g0 together are right.
