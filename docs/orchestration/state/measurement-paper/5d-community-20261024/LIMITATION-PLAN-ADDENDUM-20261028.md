# ADDENDUM to LIMITATION-PLAN: five costed scopes for Joseph before anything runs (2026-10-28)

**By** a read-only scoping agent, for the director.

**Under** [`DECISION-20261028-joseph-coverage-scoping.md`](../../../DECISION-20261028-joseph-coverage-scoping.md)
items 1–3 (Joseph: "Scope all four first"). It extends [`LIMITATION-PLAN.md`](LIMITATION-PLAN.md) and changes none
of it.

**MEASURES:** nothing.
- No job, declaration or binding. The only cluster commands were `ls` listings on login33 (2026-10-28), quoted where
  used.
- Every new number is either read from a cited record line or labelled **(arithmetic)** on cited inputs, or
  **(estimate)** with its basis.

**CANNOT AUTHORIZE:** a run, a declaration, a change to the reported covariance or to κ, a claim, or printed wording.
Each item needs its own declaration and binding. Joseph chooses what runs; this addendum recommends nothing.

**CITABLE FOR:** the five scopes; what exists for each, by record; their costs, as measured units or labelled
assumptions; which items can share runs; what is sunk from F1.

**NOT CITABLE FOR:** a coverage, calibration or χ² result; a size for any response or run-period effect on the 16
cells; any reading of the data; the Delta charging unit.

**Paths:** as in LIMITATION-PLAN.md:
- a bare `.md` or `.tsv` name is in this directory, and a bare `.tex` name is in `docs/analysis-note/`;
- `DECISION-*`, `OUTCOME-*` and `QUESTION-*` are in `docs/orchestration/`;
- paths beginning `docs/`, `nd-unfolding/` or `publication/` are from the repository root;
- every other path is relative to `docs/orchestration/state/`;
- a citation of the form `:N` is to the file named last; `$P` = `/pscratch/sd/j/josephrb`.

## 0. The five items in one table

All costs are CPU node-h on Perlmutter m3246 regular QOS unless marked. The ranges for 1, 2 and 4A standalone include
the development and verification ranges LIMITATION-PLAN took from the MP1-A-full analogue (`LIMITATION-PLAN.md:221-222`).

| item | what it answers | what it cannot | design in one line | cost (node-h, low–high; cap) | wall time | shares runs with | main risk |
|---|---|---|---|---|---|---|---|
| **1. 1B as designed** | whether the drawn-block intervals cover at the nominal truth (control), and whether the reported intervals undercover at G18_10a_02_11b and AR23_20i_00_000 | coverage at GiBUU-like or q3-tilt truths; coverage under another detector response; anything about C_model's adequacy | nominal control + both F1 truths, 300 nuisance-drawn toys each, S1-style draws of every C_e block, VL169-form rules | **44.5–145**; production 22.5, cap 35.2. F1's generation is sunk (0.718) | 3 nodes × 7.5 h production; 1–2 weeks with derivation, declaration and binding | item 4 (the same toys); item 3 (if C_resp is drawn) | an inconsistent nuisance ensemble; the development range dominates the cost |
| **2. Control + one predeclared GENIE v3 truth** | as 1B, at one held-out truth | as 1B; and the other v3 truth | 1B with one F1 truth, chosen and disclosed before the run | **37–133**; production 15.0, cap 23.4 | 2 nodes × 7.5 h; 1–2 weeks | item 4 | the truth is chosen after F1's bias result is known |
| **3a. ±4 % recoil data unfolds, projected** | how far the 16-cell data result moves for a ±4 % whole-recoil scale, beside C_resp | any bias under response mismatch; any response form other than a scale | integrate W2b's existing rr0/rr1/rrzero data unfolds onto R00–R15 | **0**, login node | hours | 3b (same products' dumps) | W2b's δ = 0 unfold is not bitwise production |
| **3b. Mismatch closures from existing shifted dumps** | the closure bias when pseudo-data carry a shifted response and the unfolding the nominal one, at C_resp's species ±1σ and at ±4 % | variants outside C_resp's species and the ±4 % scale | noise-free closures: shifted-dump pseudo-data, zero-dump response; optional 20 Poisson experiments each | **0.6–3.5**, cap 5.4 **(estimate)**, plus pilots | about 1 day of jobs | 1B (a C_resp draw would use the same dumps) | a closure mode with separate pseudo-data and response dumps is not built |
| **3c. New response variants beyond C_resp** | the same bias for neutron deposits, resolution, energy dependence or a larger scale | variants not built; the true response | MP-1-style event-loop variants per form, then 3b's closures | **about 0.86 per ±1σ pair (estimate)**, plus event-loop code (unpriced) | event loops ≤ 6.5 h per playlist; code days | 3b | the forms and amplitudes need a physics basis; no threshold is declared |
| **4A. χ² of each toy against its truth** | whether the 16-cell χ² under the drawn-block matrix follows χ²₁₆ at the tested truths | the reported C_total + C_resp + V_g χ² (C_model is not drawn); the Stage G p values at the compared generators | χ² of every 1B (or item 2) toy, declared before the run | **0** extra on 1B's toys; standalone control arm 29.5–122 | none extra | 1B, item 2 | flux and interaction draws reuse the inputs the matrix was built from |
| **4B. Toy calibration at the compared generators** | the toy distribution of the χ² at hybrid GENIE CV, GENIE+MEC, NuWro and GiBUU truths | p values below about 3/N; physical exclusions | 4 more arms of 300 on 1B's machinery | **+30**, cap 46.9, on top of 1B | +4 nodes × 7.5 h | 1B | the hybrids' bias dominates the χ² |
| **4C. Descriptive χ² from A7's existing products** | the χ² spread of 1,343–1,751 existing nuisance-drawn experiments per truth on the 16 cells | a calibration: A7's offset control failed and its draws differ from S1's | a login-node reader, as 1C | **0** | hours | 1C | descriptive only |
| **5A. The 2D C_PL projected onto the 16 cells** | a size, under the assumption that the period offset does not depend on E_avail, q3 or W | any run-period effect in the hadronic variables | map each cell's (p_T, p_∥) footprint onto the 2D block | **0**, login node | hours | 5B | the assumption is untestable without 5B |
| **5B. Per-period 5D unfolds** | whether the three period groups' 16-cell results are mutually consistent, and a C_PL,5D on R00–R15 | which period is right; the cause | 2D's period-unfold and playlist-term design on the 5D inputs | **about 1.0–1.9, cap about 3.0 (estimate)**, plus input development | about 1 day of jobs; development days | 1B's deploy only | per-period 5D inputs that reproduce S1's must be built and controlled |

<!-- absence-ok: the table's "not built", "unpriced" and "untestable" entries are scoping statements about designs proposed here; each is backed by the Search line in its section below -->

**How the items relate, in short** (§6). 4A costs nothing beyond 1B's or item 2's toys. 3a, 4C and 5A are login-node
readers at 0 node-h. 5B is the only item that adds a new kind of unfold at small cost. The largest cost in 1, 2 and
4A/4B is development, not production.

## 1. 1B as designed, re-costed after F1

### 1.1 What exists

- **The design** is `LIMITATION-PLAN.md:181-237`: a nominal control with intervals from the drawn blocks only, scored
  two-sided; two GENIE v3 test arms with the reported intervals, scored one-sided; N = 300 per arm; VL169's rule form.
- **F1 has run** (`FD-F1-REPORT.md:1-18`). It is "a bias test at two held-out GENIE v3 truths, not a coverage test"
  (`:7-9`).
  - Both truths are Joseph's choice: G18_10a_02_11b and AR23_20i_00_000 (`FD-F1-DECLARATION.md:45`).
  - The grade: 0 of 64 cells with |z| > 2 and 0 of 4 records with p < 0.01 against C_total + C_resp
    (`FD-F1-REPORT.md:35-40`, `:64-69`). These are reporting triggers, not gates (`:64`).
  - The largest |z| is 0.644 (AR23, R07) (`:39`, `:54`). **So no cell at either truth has |z| > 1,** and
    LIMITATION-PLAN §1.3's "whatever the spread" bound (`LIMITATION-PLAN.md:115-122`) does not bind there. At these
    truths a coverage test is informative on spread against width.
  - The overlaps: G18's 2p2h is the Valencia family of the GENIE+MEC vertex; both share Nieves CCQE; AR23's 2p2h is
    SuSAv2 (`FD-F1-REPORT.md:94-99`).
- **Other coverage evidence, beyond what LIMITATION-PLAN §1.1 lists:**
  - `LIMITATION-PLAN.md:78` calls VL169 "the project's one coverage test". The records also hold the 5D Tier-S test
    of candidate F2's bias-corrected statistical intervals: FAIL by futility (`OUTCOME-20260925-s5c-tier-s-futility-fail.md:1-5`,
    `:30-34`). That is not configuration (e).
  - For configuration (e), s5e's development-scale departure coverage is 0.017–0.157 against 0.68
    (`DECISION-20261023-joseph-gpu-test-and-campaign-criterion.md:20-22`).
  - Neither is a test of the 16-cell intervals. <!-- absence-ok: scoped to the two cited records; the 16-cell absence is LIMITATION-PLAN's own Search line (LIMITATION-PLAN.md:516) -->

### 1.2 What F1 made sunk or reusable

<!-- absence-ok: the first column quotes LIMITATION-PLAN.md's own pre-F1 status lines (:164, :178-179, :223); the second column records that F1 resolved them -->
| LIMITATION-PLAN §1.4 line | status now | record |
|---|---|---|
| "F1a and F1b, for 1B only: 0.2–0.5 node-h" (`LIMITATION-PLAN.md:223`) | **sunk.** F1a 0.104722, F1b 0.202778 (OOM STOP), F1a′ 0.100833, F1b′ 0.310000: **0.718333** in all, 0.22–0.52 above the estimate **(arithmetic)** | `FD-F1-REPORT.md:131-136`; `fd/LEDGER.tsv` row `F1 S4.7` ("F1 spent 0.718333") |
| "per-event throughput is unmeasured, and whether the CVMFS builds run on Perlmutter is unverified" (`LIMITATION-PLAN.md:178-179`) | **resolved.** F1a's gate was GO; F1b′'s 14 tasks of 160,000 events ran 554.66–1,022.80 s, so 3.5–6.4 ms per event **(arithmetic)** | `FD-F1-REPORT.md:131`, `:176-198` |
| the samples: "no GENIE v3 events exist yet" (`LIMITATION-PLAN.md:164`) | **reusable.** 1,120,000 events per tune; the gst, gen5d and prep files are on pscratch and in HPSS `mnv-5d-f1-20261028/stage0-inputs.tar` | `FD-F1-REPORT.md:108`, `:275-284` |
| the truth definition | **reusable.** Each truth is a gated, k-normalised per-fine-cell ratio r, bridged to `s5e-shape-ratio/1` | `FD-F1-DECLARATION.md:157-173`; `FD-F1-REPORT.md:110-118` |
| the chooser rule (`LIMITATION-PLAN.md:173-175`) | **met for 1B:** the truths are already Joseph's | `FD-F1-DECLARATION.md:45` |
| F1c's 42 products | **not reusable as 1B toys:** Poisson only, no nuisance draws | `FD-F1-REPORT.md:7-9`, `:32-33` |
| F1c's unit cost | **measured, for context:** 0.609167 node-h for 42 products, 0.0145 each; the 40 Poisson experiments' `seconds_unfold` median 319.9 s (312.5–397.2) at 8 × 32 **(arithmetic over the committed logs)** | `FD-F1-REPORT.md:138`; `fd/receipts-f1/run/cluster/f1c/line*-60439400.log` |

### 1.3 What 1B still needs

- **The S-3 derivation and the draw scheme** (`LIMITATION-PLAN.md:182-192`): every C_e block drawn, flux weighted by
  the constraint, the laterals applied, the expected spread derived and declared before binding.
- **A nuisance-drawn mode on an F1 truth.**
  - A7's `s5p_nullexp.py` draws nuisances, but its truths are generator-null ratio files, its flux draw is uniform,
    and its laterals and normalization are a downstream linear surrogate (`nd-unfolding/s5p_nullexp.py:1-30`).
  - F1's experiments use `s5e_candidate.py` with a `ratio_nd` truth and no draws (`FD-F1-DECLARATION.md:186-189`).
  - So 1B needs either a format bridge from F1's ratio to `s5p_nullexp`'s truth, plus the S-3 changes, or the draws
    added to the `ratio_nd` path (inference from the code's docstring).
- **The half-MC question.** A7 and F1 unfold with MC half A and draw pseudo-data from half B (`FD-PLAN.md:137`). The
  reported intervals are those of the full-MC data unfold. The declaration must say which estimator the toys
  represent.

Search: nuisance; universe; draw; ratio_nd; hypothesis in `nd-unfolding/s5e_candidate.py` and `nd-unfolding/s5p_nullexp.py`; "coverage test" in `OUTCOME-2026092*` and `DECISION-20261023-*` @ 3ae3c64c6

### 1.4 Cost, re-stated

| line | 1B | basis |
|---|---:|---|
| production | 900 × 0.025 = **22.5**, cap 35.2 at 1.5625× | A7's nuisance-drawn unit (`FD-PLAN.md:471`), an **ASSUMPTION** until a pilot measures S1-style draws (`LIMITATION-PLAN.md:219-220`) |
| development and admission | 15–40 | MP1-A-full analogue, **ASSUMPTION** (`measurement-paper/phase1/mp1/S1-REPORT.md:403`) |
| verification and repair | 7–70 | the same analogue, **ASSUMPTION** (`measurement-paper/phase1/mp1/S1-REPORT.md:405`) |
| F1a and F1b | **0 (sunk, 0.718333)** | §1.2 |
| **total** | **about 44.5–145** **(arithmetic)** | LIMITATION-PLAN's 45–146 less 0.2–0.5 |

- **The third arm's marginal cost** is 300 × 0.025 = 7.5 node-h, cap 11.7 **(arithmetic)**. The consult's 7.5 matches.
- **Unit context, all measured:** F1c's Poisson experiment 0.0145 (§1.2); S1's data-size unfold 0.0226
  (`FD-PLAN.md:474`); the 2026-10-23 timing of one recorded (e) unfold packed 8 × 32, 0.018509
  (`gpu-timing-20261023/REPORT.md:67`). The 0.025 unit is the largest of these.
- **Wall time:** about 40 unfolds per node-hour packed 8 × 32, so 3 nodes × 7.5 h, each job under 12 h
  (`LIMITATION-PLAN.md:225-226`); 1–2 weeks with the derivation, declaration and binding.

### 1.5 What it answers and cannot; what the paper could state

- **Answers:** whether the drawn-block intervals cover at the nominal truth (the machinery check), and whether the
  reported intervals undercover at two held-out GENIE-family truths, per cell and pooled.
- **Cannot:** the GiBUU-like and q3 truths (`LIMITATION-PLAN.md:139-144`); another detector response; C_model's
  adequacy, since a fixed-truth draw cannot produce C_model (`:193-203`). With N = 300 the per-cell SE at 0.683 is
  0.027 (`:213`), so deficits of a few points stay unresolved.
- **On a pass** (contents): the measured per-cell and pooled rates and windows at the two tested truths, under the
  nominal response; "no undercoverage detected at the study's sensitivity", with that sensitivity stated; nothing
  about GiBUU-like truths.
- **On a fail:** if the control fails, the machinery is ungraded and the test arms are not read; if a test arm fails,
  the measured undercoverage at that truth replaces "not validated".

## 2. Control plus one predeclared GENIE v3 truth

### 2.1 What exists

The consult proposes it (`2d-closeout/stageF/methods/secondary-results/astra-consult-coverage-20261028/answer.txt`, §5: "the nominal control plus
one predeclared GENIE v3 truth, with 300 toys each"). Everything in §1.1–1.2 applies; the samples and ratios for
both truths exist.

### 2.2 The design and the choice

- 1B's design with one test arm.
- **The choice of truth is new, and it is made after F1's grade is known.** The records give these facts for it,
  and no ranking:
  - G18_10a_02_11b: 2p2h in the Valencia family of the GENIE+MEC vertex; max |z| 0.623 (R11); χ² 11.836
    (`FD-F1-REPORT.md:37`, `:94-95`).
  - AR23_20i_00_000: 2p2h SuSAv2, not a vertex family; max |z| 0.644 (R07); χ² 16.863 (`:39`, `:96`).
  - Both share Nieves CCQE and are GENIE-family, so "partial evidence" (`:96-98`).
- The consult asks that the rationale be disclosed because the bias result is known (answer.txt §5). Under the
  chooser rule, the chooser is Joseph (`FD-DIRECTOR-RULINGS.md:59`).

### 2.3 Cost

- Production 600 × 0.025 = **15.0**, cap 23.4 **(arithmetic)**; development and verification as §1.4.
- **Total about 37–133**, the same as 1B′ (`LIMITATION-PLAN.md:224`). Against 1B it saves 7.5 (cap 11.7) of
  44.5–145.
- Wall time: 2 nodes × 7.5 h, plus the same 1–2 weeks.

### 2.4 Answers, cannot, pass and fail

- As §1.5, at one truth. It also cannot say whether the result holds at the other v3 tune.
- **Against 1B′** (control plus A7 GENIE CV): same cost; a truth held out of C_model's construction, where 1B′'s is
  the reference of every vertex ratio (`FD-G-REPORT.md:105-107`).
- **On a pass or a fail:** as §1.5, with the choice and its stated rationale beside the result.

## 3. Hadronic-response mismodeling beyond C_resp

### 3.1 What exists

**C_resp and its scope.**
- The 5D reported total is C_e + C_model,abs + C_resp (`DECISION-20261026-joseph-adopt-cresp.md:37-43`). C_resp's
  median per-cell σ is 2.14 % (0.70–3.71 %), raising the median of C_total from 6.74 % to 7.29 % (`:8-11`).
- It is the data result's response to a ±1σ scale of the simulation's reconstructed recoil, for proton, meson, EM and
  other deposits, from the MP-1 S1 data unfolds (`measurement-scoping/assigned-uncertainties/C-RESP-SPEC.md:239-243`). The sizes are
  proton 3.5 %, meson 5 %, EM 3 %, other 20 % (`measurement-paper/PLAN.md:47`).
- **It does not cover** (`measurement-scoping/assigned-uncertainties/C-RESP-SPEC.md:244-262`): the joint tests; neutron and muon deposits; species effects,
  energy dependence and resolution beyond a scale; a response difference applied before calibration; configuration
  (a)'s products; the 3D and 4D results.
  - Neutrons are absent by construction (`:101-102`). The tuples apply 10 % to all three neutron bins, and MAT turns
    neutron response off by default (`measurement-paper/PLAN.md:47`, `:86-89`).
- **Every fake-data test uses the simulation's response.** "None of these tests uses pseudo-data whose detector
  response differs from the unfolding response" (`docs/analysis-note/sec_validation.tex:39`); F1: "the detector
  response is not probed" (`FD-F1-REPORT.md:9`).

**The note's detector-response-mismatch closure.**
- It is listed as "protocol implemented, not yet run" (`docs/analysis-note/sec_intro.tex:72`;
  `app_response_mismatch.tex:1`; `sec_validation.tex:118-119`).
  - The acknowledgment: "We thank Kevin McFarland for suggesting a detector-response-mismatch closure targeting
    correlations among the reconstructed hadronic observables" (`docs/analysis-note/main_note.tex:154-155`). The
    appendix adds that he "proposed stressing the hadronic record, especially for quasielastic events, to inspect
    low-W bias" (`app_response_mismatch.tex:4`).
- **Its first arm:** pseudo-data reco E_avail → (1 + ε) E_avail, both signs, at an amplitude fixed in advance and
  justified by a documented variation; truth, weights, membership and the nominal response fixed
  (`app_response_mismatch.tex:6-11`). Primary observable: signed bias against W, W < 1.1 GeV reported separately
  (`:13`).
- **Its code** is the ROOT driver's `--closure-response-eavail-frac` (`nd-unfolding/unfold_nd_omnifold_unbinned.py:675-711`,
  `:937-941`, `:1133-1140`): closure only, exactly `--axes eavail,q3,W`, no truth-reweight injection, no bootstrap,
  output named `NONQUOTABLE-DIAGNOSTIC.*`.
  - S1 and F1 ran configuration (e) through the npz drivers (`s1/tasks-prod.tsv` line 2, `s5p_universe.py`;
    `FD-F1-DECLARATION.md:183-189`).
  - s5e's diagnosis compared the unmodified ROOT driver with the npz path: the same departure failure (EW29 73.8 %
    against 73.5 %), inputs identical once 2,801 sentinel rows are removed, and a difference at the estimator's
    rounding floor, about 1 % at most on data (`OUTCOME-20260926-s5e-oi192-diagnosis-and-candidate.md:25-32`). So the
    driver is close to, but not bitwise, the production path, and a closure through it needs its own δ = 0 control.
- **Its second arm**, the physically correlated follow-up (QE leading-nucleon shift, recompute E_avail, q3, W and the
  selection), needs event-loop diagnostic output that the current outputs lack, and is deferred unless the first arm
  shows material bias (`app_response_mismatch.tex:20`).
- **No pass threshold is set** and no output was produced (`app_response_mismatch.tex:22`). Its protocol file says
  the same, "implemented, not run, diagnostic only, no pass threshold adopted" (`nd-unfolding/RESPONSE_MISMATCH_CLOSURE.md:3`),
  and requires the amplitude frozen and both signs run before any look (`:63-72`).
- **Joseph deferred its settings** (the amplitude ε and the decision statistic) on 2026-10-14: "defer it"
  (`DECISION-20261014-joseph-2d-endpoint-and-open-items.md:29`). Every design in §3.2 that fixes an amplitude or a statistic reopens it.
Search: response-mismatch; response mismatch; mismatch closure; closure-response-eavail-frac; NONQUOTABLE; McFarland in `docs/analysis-note/*.tex`, `nd-unfolding/*.py` and `docs/orchestration/` @ 3ae3c64c6

**Existing response-shifted products that a design could reuse** (`ls` on login33, 2026-10-28):
- MP-1's 11 species variants (zero; proton, meson, EM, other and cross-talk at ±1σ): per-playlist event loops under
  `$P/measurement-paper/phase1/mp1/s1/evloop/<variant>/`, merged files, lateral dumps `lateral/lat_<variant>.npz`
  and the data unfolds `unf/mp1s1_<variant>_b-_j-.npz` (`measurement-paper/phase1/mp1/S1-REPORT.md:52`, `:136-152`).
- W2b's whole-recoil ±4 % and δ = 0: dumps `lat_w2b_rr{0,1,zero}.npz` and data unfolds `w2b_rr{0,1,zero}_b-_j-.npz`
  under `$P/w2-recoil-20261006/w2b/` (`publication/w2/W2B-REPORT-20261006.md:170-177`). The size is "the level of
  data–simulation agreement reported for test-beam protons, pions and electrons" (`docs/analysis-note/sec_joint.tex:284`).
  - W2b's δ = 0 unfold is not bitwise the frozen production product; its control passed by the fallback criterion
    (`publication/w2/W2B-REPORT-20261006.md:69-75`).
- **The prepared question** to a MINERvA hadronic-response expert is "PREPARED, NOT SENT"
  (`QUESTION-20260920-hadronic-response-coverage-for-eavail-w.md:3-8`). Sending it is outward-facing and Joseph's.

### 3.2 Designs

**3a. Project W2b's ±4 % data unfolds onto R00–R15. Cost 0.**
- A login-node reader integrates rr0, rr1 and rrzero onto the 16 cells with S1's integration rule, and prints the
  shifts against rrzero beside C_resp's per-cell σ.
- It is a data-side sensitivity at a second construction (whole recoil, one coherent scale), not a mismatch closure.
- Basis: the products exist (above); a declaration and a reader, as 3D's (`FD-FLUX-BOOT-REPORT.md:42-53`).

**3b. Mismatch closures from the existing shifted dumps.**
- Pseudo-data: a shifted dump's reco rows with the nominal truth; the unfolding: the zero dump's response. One
  noise-free closure per variant: 10 MP-1 variants, W2b's two, and a zero-on-zero control.
- What it adds over C_resp: C_resp shifts the unfolding's response and unfolds the data; 3b shifts the pseudo-data and
  keeps the nominal response. To first order the two agree **(inference)**; 3b measures where they do not, and the
  closure bias itself, at C_resp's own amplitudes and at ±4 %.
- **Development:** a closure mode taking pseudo-data and response from different dumps. Each of the three (e) drivers
  takes one `--npz` and one `--bkg` (`nd-unfolding/pv-ladder/pvl_unfold.py:100-109`; `nd-unfolding/s5p_numerics.py:121-124`;
  `nd-unfolding/s5n_pseudo.py`, which `s5e_candidate.py:54-60` wraps). Search: add_argument; npz; bkg; closure; pseudo;
  source in `nd-unfolding/pv-ladder/pvl_unfold.py`, `nd-unfolding/s5n_pseudo.py`, `nd-unfolding/s5e_candidate.py` and
  `nd-unfolding/s5p_numerics.py` @ 3ae3c64c6 <!-- absence-ok: scoped to the named drivers' argument lists at 3ae3c64c6 -->
- **Cost (estimate):** 13 closures × 0.045 (`FD-PLAN.md:472`) = 0.59, cap 0.91; with 20 Poisson experiments per
  variant at F1c's 0.0145, a further 12 × 20 × 0.0145 = 3.48 **(arithmetic)**. Range about 0.6–3.5 (cap 5.4), plus
  pilots (an **ASSUMPTION** of ≤ 0.5, from F1a's 0.10 pilot, `FD-F1-REPORT.md:131`).

**3c. New variants outside C_resp.**
- Candidate forms, each named in C-RESP-SPEC's "does not cover" list (`measurement-scoping/assigned-uncertainties/C-RESP-SPEC.md:249-251`): the three neutron bins (in the
  tuples, `measurement-paper/PLAN.md:47`); a resolution smear; an energy-dependent scale; a larger amplitude.
- Each needs an MP-1-style event-loop variant over 12 playlists, a merge, a dump, then 3b's closure (and, if wanted, a
  data unfold as C_resp's).
- **Cost per ±1σ pair (estimate):** MP-1's event loops were 3.913 node-h for 11 variants (`measurement-paper/phase1/mp1/S1-REPORT.md:100`),
  0.356 per variant; dumps 0.301/11 = 0.027 each and data unfolds 0.593/11 = 0.054 each (`:151-152`), on debug
  packing. A pair with closures is about 2 × (0.356 + 0.027 + 0.045) = 0.86 **(arithmetic)**. The event-loop code for
  a smear or energy dependence is unpriced (development).
- **Wall:** MP-1's per-playlist limits ran to 6.5 h (`measurement-paper/phase1/mp1/S1-REPORT.md:54`).

**3d. McFarland's QE leading-nucleon follow-up** (`app_response_mismatch.tex:20`): needs new event-loop output. No
record prices it. <!-- absence-ok: scoped to the Search line of §3.1 -->

**3e. The implemented reco-only E_avail arm** (`nd-unfolding/unfold_nd_omnifold_unbinned.py:675-711`): two closures, at about
0.045 each **(estimate)**, plus a δ = 0 closure through the same driver as its control (a third, about 0.045). The
driver's difference from the npz path is at the rounding floor (§3.1), which the declared amplitude must exceed.

### 3.3 Answers, cannot, pass and fail

- **Answers:** the 16-cell closure bias under the tested response mismatches, against the reported σ and against C_resp;
  for 3a, the data result's movement under a ±4 % scale.
- **Cannot:** the true detector response; untested forms; whether the ±4 % or species sizes are right; MINERvA's
  internal provenance (the prepared question is the route to that).
- **No threshold exists** (`app_response_mismatch.tex:22`). A threshold, the amplitudes and the forms must be declared
  before any product is read. <!-- absence-ok: quotes the appendix's own status ("no pass threshold has been set") -->
- **On a pass** (contents): the bias stays within a declared fraction of σ under the tested variants, so the result is
  stable within that response envelope only.
- **On a fail:** a measured bias outside C_resp, which "would require a decision on the response model or an
  uncertainty component, and would not be absorbed silently" (`app_response_mismatch.tex:22`). Adding a component now
  is post-read (§5.4).

## 4. Is the covariance suited to the quoted χ²?

### 4.1 What exists

- **The quoted χ²:** Stage G's total and shape-only χ² on M = C_total + C_resp + V_g: GENIE CV 109.35/16, GENIE+MEC
  272.12/16, NuWro 188.03/16, MnvTune v1 329.72/16, GiBUU 58.46/8 (`FD-G-REPORT.md:76-92`). "There is no reading of
  these numbers" (`:64`).
- **What M omits:** `not_included` "inflation D", "C_ML", "bounded envelope h", "Rvp1pi" (`S1-REPORT.md:294`); the seed
  block is exactly 0 (`:312`).
- **Its two sensitivities on record:**
  - G-SENS2's α = 0.1 flux weakening: −24 % to −48 % on 16 cells, −6 % for GiBUU (`LIMITATION-PLAN.md:404-412`).
  - 3D's bootstrap of the 100 flux universes: 16–84 % bands of, for example, 105.97–112.45 (GENIE CV) and
    314.90–350.00 (MnvTune) (`FD-FLUX-BOOT-REPORT.md:102-108`). Its labels say neither band "is an interval for the χ²
    under the true correlations" (`:82-90`).
- **A related check, at another scope:** s5e's A2 for configuration (e) passed a Mahalanobis-mean check, 43.06 in
  [33.6, 50.4], with a Hartlap factor, at nominal truth on the 42 (E_avail, W) cells against the statistical replicas
  (`s5e/cand/assess_receipt.json` key `A2`). It is statistical only.
- **The 16-cell χ²'s distribution under the full model is not on record.** <!-- absence-ok: scoped to the Search line below -->

Search: sampling distribution; calibrated significance; chi2 calibration; toy χ²; nominal distribution; mahalanobis in `docs/orchestration/state/measurement-paper/`, `docs/orchestration/state/measurement-scoping/`, `docs/analysis-note/paper_body.tex` and `docs/analysis-note/sec_5d.tex` @ 3ae3c64c6

### 4.2 Designs

**4A. The χ² of each toy against its truth, on 1B's or item 2's toys.**
- For toy i at truth T: χ²_i = (x̂_i − x_T)ᵀ M_d⁻¹ (x̂_i − x_T), with M_d the drawn-block matrix of the control
  intervals (`LIMITATION-PLAN.md:195-197`). Compare with χ²₁₆: the mean (16; SE over 300 toys 0.33), the fraction above
  26.30 (the 95th percentile; SE 0.013), and a KS or quantile comparison **(arithmetic)**.
- **This tests the full 16 × 16 drawn-block matrix**, correlations included, which the marginal rates do not.
- **Extra it needs:** the statistic, its window and the noise of x_T declared before the run; a ridge or
  eigenvalue-floor rule, if any, fixed in advance (C_e's condition is 1.87e-79/9.35e-84 ≈ 2.0e4, `S1-REPORT.md:279-284`,
  **(arithmetic)**). Cost 0 node-h beyond the toys: a login-node reader.
- **Its limits:**
  - At a test arm, M_d excludes C_model. The reported M includes it, so the reported χ² of a toy is expected to fall
    below χ²₁₆ by construction, as the intervals over-cover (`LIMITATION-PLAN.md:198-200`).
  - Flux draws from the same 100 weighted universes reproduce the flux block's correlations to first order **(inference)**.
    So 4A tests the propagation (nonlinearity, Poisson, the estimator), not whether PPFX's correlations are right; the
    same holds for the interaction bands' declared Gaussian interpolation.
  - It does not calibrate Stage G's comparisons, whose truths are the generators.
- **Standalone,** with only the control arm: 300 × 0.025 = 7.5, cap 11.7, plus §1.4's development: 29.5–122
  **(arithmetic)**.

**4B. Calibrate the Stage G χ² at hybrid generator truths.**
- Four more arms (GENIE CV, GENIE+MEC, NuWro, GiBUU on its 8 cells), the control serving MnvTune; each toy's χ² against
  its hypothesis on Stage G's M, as A7 calibrated its joint test on the J cells (`paper_body.tex:284`).
- **Cost:** 1,200 × 0.025 = 30, cap 46.9, on top of 1B **(arithmetic)**; wall 4 more nodes × 7.5 h.
- **Resolution:** with N = 300 and no exceedance, p ≤ about 0.01 at 95 % (3/N) **(arithmetic)**. Stage G's nominal p are
  9.3e-10 to 1.7e-60 (`FD-G-REPORT.md:76-92`), so 4B could show only whether each observed χ² lies outside its toy
  distribution.
- F0b measured large biases at A7's GiBUU-like truths (`LIMITATION-PLAN.md:99-105`), which would dominate the toys' χ²
  there.

**4C. A descriptive χ² from A7's existing nuisance-drawn products.** Row 5 holds 1,343–1,751 experiments at each of
MnvTune v1, GENIE CV, GENIE MEC, NuWro and GiBUU (`FD-PLAN.md:146`). A login-node reader, as 1C, at 0 node-h. It is
descriptive only: F0's offset control 7 failed at χ²₁₆ = 245.74, the draws differ from S1's, the truths are hybrids
on the J cells, and the products use half the MC (`LIMITATION-PLAN.md:153-157`).

### 4.3 Answers, cannot, pass and fail

- **Answers (4A):** whether the drawn-block 16 × 16 matrix describes the toys' scatter in all 16 dimensions at the
  tested truths. **(4B):** where the observed χ² lie in the toy distributions at the compared generators' hybrids.
- **Cannot:** whether C_model, V_g or the flux model's correlations are right; physical exclusions of the generators;
  p values below about 3/N.
- **On a pass** (contents): the drawn-block χ² follows χ²₁₆ within the declared window at the tested truths, so the
  matrix's correlations, as propagated, are consistent with the toys; nothing about C_model.
- **On a fail:** the measured mean and tail fraction, which would qualify every χ² quoted on M; if the control's χ² fails
  while its marginal rates pass, the failure is in the correlations.

## 5. The run-period inconsistency and the sixteen-cell uncertainty

### 5.1 What exists

- **The 2D result carries it.** The adopted 2D covariance is Q = S5 total + C_PL (`DECISION-20261017-joseph-2d-adopt-s5-plus-playlist.md:28`).
  C_PL is built from separate seed-42 unfolds of the period groups 1A–1F, 1G–1M and 1N–1P, each over its own MC
  truth, against their exposure-weighted mean; rank 2; median 2.09 % per bin, 1.97 % on the integral
  (`docs/analysis-note/sec_systematics.tex:165-168`; `2d-closeout/playlist-term/REPORT.md:3-9`).
- **The paper states the inconsistency** and the 2D block (`docs/analysis-note/paper_body.tex:156`): a p_∥ step of
  about 7 % near 8 GeV/c, cause unknown, and the block's "own consistency check cannot fail".
- **The 16-cell C_total carries no run-period block.**
  - S1's assembly lists 46 blocks: 38 bands (Flux, the interaction knobs, and the detector bands GEANT_Neutron, GEANT_Pion, GEANT_Proton and MinosEfficiency), 5 laterals, normalization,
    seed and stat; none is a run period (`s1/readout/s1_assembly.json` `meta.blocks`, sha256 `81e5ef3f…`, re-measured).
    The readout's groups are stat, flux, interaction, detector, lateral, normalization and seed (`S1-REPORT.md:255-277`).
  - `not_included` does not name it either (`S1-REPORT.md:294`).
  - The paper draft the consult read lists C_total's parts as "the statistical, flux, interaction, detector, lateral
    and normalization uncertainties … and Cmodel", then C_resp (`2d-closeout/stageF/methods/secondary-results/astra-consult-coverage-20261028/inputs/paper.txt:360-373`).
  - The flux block uses the 12 playlists' POT-weighted flux (`fd/receipts-f1/declaration/probes/probe9.out:143`), so the
    per-period flux differences enter only through that average.
- **No 5D per-period unfold is on record.** <!-- absence-ok: scoped to the Search line below -->

Search: run period; run-period; playlist; C_PL; playlist_term; period-unfold in `docs/orchestration/state/measurement-paper/`, `docs/orchestration/state/measurement-scoping/` and `nd-unfolding/`; `meta.blocks` and `not_included` of `s1/readout/s1_assembly.json` @ 3ae3c64c6
- **The consult's claim holds on the records:** "the text's discussion of a two-dimensional run-period block does not
  by itself establish that treatment" (answer.txt §6). The records establish more: there is no such treatment.

**Inputs that exist** (`ls` on login33, 2026-10-28; contents not read):
- MP-1's per-playlist 5D zero passes, `$P/measurement-paper/phase1/mp1/s1/evloop/zero/runEventLoopOmniFold_5D_<PL>_zero.root`,
  12 files, 2026-10-20. Their lateral dump passed `s5p_input_dumps.py lateral`, which requires the observed events to
  equal the CV npz's (`publication/w2/W2B-REPORT-20261006.md:50-51`); so they carry the data rows **(inference)**.
- The per-playlist universe event loops `$P/MINERvA-OmniFold/nd-unfolding/runEventLoopOmniFold_5D_<PL>_universes_full_bkgaware.root`,
  12 files, 2026-07-13.
- Which of these reproduces S1's inputs per period is not established; a pooled control decides it, as 2D's
  `pu_CTRL_s42` did (`2d-closeout/period-unfold-20261014/REPORT.md:28-37`).

### 5.2 Designs

**5A. Project the 2D C_PL onto the 16 cells. Cost 0.**
- The fine grid's (p_T, p_∥) bins are the published 14 × 16 (`docs/analysis-note/paper_body.tex:74`), so each cell's
  (p_T, p_∥) footprint is a union of 2D bins. Apply each period's 2D double-ratio offsets over that footprint,
  weighted by the cell's prior weight.
- **The ASSUMPTION** is that the offset does not depend on E_avail, q3 or W inside a 2D bin. Only 5B can test it.
- Inputs: `playlist_term.npz` (`c1723cb5…`, on CFS and pscratch, `2d-closeout/playlist-term/REPORT.md:30`); the cell
  definition and fine map (`FD-PLAN.md:151`).

**5B. Per-period 5D unfolds: the 2D design on the 5D inputs.**
- Merge per period PA, PB, PC and a pooled control (`2d-closeout/period-unfold-20261014/scripts/build_inputs.sh:1-35`),
  per-period flux files (`build_flux.py`), a per-period CV npz and background dump, then (e) at seed 42.
- **Noise reference,** as 2D: seed 43 and 10 bootstrap replicas per period (`2d-closeout/playlist-term/DESIGN.md:28-30`).
- **The control:** the pooled unfold reproduces S1's f on R00–R15 to a declared tolerance before any period result is
  read.
- **Readout:** the period double ratios on R00–R15 with χ² against the noise reference; then, optionally, C_PL,5D by
  2D's DESIGN §2–§4 (`2d-closeout/playlist-term/DESIGN.md:39-89`).
- **Cost (estimate):** 37 unfolds × 0.0226 (`FD-PLAN.md:474`) = 0.84, plus 4 dumps at 0.027–0.048
  (`measurement-paper/phase1/mp1/S1-REPORT.md:151`; `publication/w2/W2A-REPORT-20261006.md:28`): about 1.0 **(arithmetic)**. The 2D analogue
  charged 1.9414 for 37 jobs and 3 retries, against a median expectation of 1.04 (`2d-closeout/period-unfold-20261014/REPORT.md:132-133`).
  So **about 1.0–1.9, cap about 3.0** at 1.5625× the high end.
- **Development:** a per-period CV npz builder and per-period flux denominators for 5D; no analogue prices it in node-h.
  It is session-days of login work and test runs.

### 5.3 Answers, cannot, pass and fail

- **Answers (5B):** whether the run-period inconsistency appears on R00–R15, and its size there by 2D's construction.
  **(5A):** a size under a stated assumption.
- **Cannot:** the cause, which period is right, or a validated size: a block built from the observed differences
  contains them by construction (`2d-closeout/playlist-term/REPORT.md:19-20`).
- **On a consistent result** (contents): the period groups agree on the 16 cells within the noise reference, so the 2D
  inconsistency does not reach the cells at this precision.
- **On an inconsistent one:** the measured χ² and step on the 16 cells; a C_PL,5D printed beside C_total.

### 5.4 Adoption is post-read

Stage G read the data against the generators on 2026-10-26 (`LIMITATION-PLAN.md:262`). Any block added now lowers every
Stage G χ² or leaves it unchanged, since (C + A)⁻¹ ⪯ C⁻¹ for A ⪰ 0 (`:269-270`). U-PLAN's safeguard applies: "Deciding
after Stage G's χ² are seen would make the choice of matrix depend on the comparison" (`:266-268`). So for items 3 and 5,
printing a new block beside the total, rather than in it, keeps the reported matrix fixed. Either is Joseph's.

## 6. Combinations

| set | node-h (low–high) | addresses |
|---|---:|---|
| **0 node-h tier:** 3a + 4C + 5A | 0 | descriptive sizes for items 3, 4 and 5; no test |
| item 2 + 4A | 37–133 | coverage at one held-out truth; the drawn-block χ² there and at nominal |
| 1B + 4A | 44.5–145 | coverage at both v3 truths; the drawn-block χ² at three truths |
| 1B + 4A + 4B | 74.5–192 | as above, plus the toy distribution of Stage G's χ² at the four compared generators' hybrids |
| 3b + 5B | about 1.6–5.4 | the closure bias under existing response shifts; the run-period consistency on the 16 cells |
| item 2 + 4A + 3b + 5B | about 39–138 | items 2, 3 (at existing amplitudes), 4 and 5 |
| 1B + 4A + 3b + 3c (three pairs) + 5B | about 49–153, plus 3c's code | all five items with new response forms |

All sums are **(arithmetic)** on §1–§5's ranges. The high ends of 1B, item 2 and 4B use their production caps, as LIMITATION-PLAN's 1B range did; those of 3b, 3c and 5B are their ranges' high ends, without caps.

- **Shared development.** 1B, item 2, 4A and 4B share one nuisance-drawn mode and one S-3 derivation; that shared part
  is 22–110 of their cost.
- **A coupling between 1B and item 3.** 1B draws C_resp "only if the scheme re-runs the response's stochastic part"
  (`LIMITATION-PLAN.md:188`). Drawing species z_s per toy from MP-1's dumps is MP1-A-full's mode
  (`measurement-paper/phase1/mp1/S1-REPORT.md:394-399`). With it, 1B's control could include C_resp, and 3b's closure mode would be
  part of the same development.
- **What no set reaches:** the GiBUU-like and q3 bias (`LIMITATION-PLAN.md:139-141`), and C_model's adequacy.

## 7. Platforms

**Perlmutter m3246 CPU (the default).**
- **The last recorded balance:** 17,711.5 of 20,000 charged, so **2,288.5 node-h left** for the group, at
  2026-10-23T05:31:10Z (`measurement-scoping/iris-20261023.txt:2-5`; `measurement-scoping/SCOPING.md:133`). Joseph's own
  use was 2,097.3 of 10,000.
- The group pool is the binding limit, and the director keeps measurement work within half of what remains at each
  grant (`DECISION-20261019-joseph-methods-first-and-measurement-compute.md:47-53`). Half of 2,288.5 is 1,144
  **(arithmetic)**.
- The group drew 11–89 node-h a day in the readings before (`measurement-scoping/SCOPING.md:133`). **It must be re-measured with `iris`
  before any grant.** This addendum did not read `iris`.

**Perlmutter m3246_g (GPU nodes' CPUs).**
- 42,727.4 GPU node-h left at 2026-10-23 (`measurement-scoping/SCOPING.md:134`).
- The measured path is the GPU node's host CPUs: 0.028559 GPU node-h per recorded (e) unfold packed 4 × 32, against
  0.018509 CPU node-h on a CPU node the same day, 1.54× (`gpu-timing-20261023/REPORT.md:67-70`, `:111-116`).
  - At that ratio, 1B's production is about 34.7 GPU node-h and item 2's about 23.1 **(arithmetic, an ESTIMATE** that
    scales A7's unit by a ratio measured on another unit).
- **LightGBM GPU training is not available** in the analysis environment; no rebuild was made (`gpu-timing-20261023/REPORT.md:36-37`).
- Any use of `m3246_g` is Joseph's and Ben's decision (`measurement-scoping/SCOPING.md:150`), and a large GPU campaign needs reasonable
  grounds to expect a measurement-quality paper (`DECISION-20261023-joseph-gpu-test-and-campaign-criterion.md:20-22`).

**NCSA Delta (`bhvk`).**
- **Balance:** 1,401 CPU-hours of 6,000 and 635 GPU-hours of 1,000, measured 2026-10-28 by the director with `accounts`
  (as relayed for this addendum; not in a committed record). The earlier record: 1,480 h of 6,000 and 640 h of 1,000 on
  2026-10-20 (`DECISION-20261020-joseph-refined-estimator-shorten-delta.md:34-35`). Neither record says whether these
  are hours used or hours left.
- **The unit is not established by any record.** If the CPU-hours are core-hours and a Delta CPU node has 128 cores
  (an **ASSUMPTION**, not on record), 1,401 is about 10.9 node-h, under 1B's 22.5 of production **(arithmetic)**. It
  must be confirmed from NCSA's allocation documentation before any pricing.
- **No GPU or CPU timing of these unfolds on Delta is on record.** The project's Delta jobs were PET and full-event TF
  runs in July (`docs/orchestration/RUNS.tsv:225-231`); the GPU timing ran on Perlmutter only.
- **Delta holds no MINERvA inputs, and its environment is unvalidated.** Any use starts by copying inputs from NERSC
  and confirming that the environment reproduces a known product bitwise (`DECISION-20261020-joseph-refined-estimator-shorten-delta.md:39-40`).
  The specs that allow Delta require that reproduction control first (`2d-closeout/stageF/methods/RE1-SPEC.md:55`).
  For 1B the inputs include `of_inputs_5d.npz` (1.55 GB, `docs/publication/audit-20261008/REPORT-20261008-release-reproducibility-audit.md:360`),
  the background dump, the bank and the flux files.

Search: bhvk; delta-cpu; delta-gpu; core-hour; service unit; SU; accounts; Delta in `docs/` and `nd-unfolding/`; gpu-timing-20261023; iris receipts by `git ls-files` @ 3ae3c64c6

**Retention for reuse.** The pscratch list is to be re-raised before the 2026-11-20 purge window
(`HANDOFF-20261028-measurement-session.md:65`). F1's samples and prep are in HPSS (`FD-F1-REPORT.md:275-284`) and A7's
products in `s5p-archive-20261006.tar` (`FD-PLAN.md:146`). The HPSS status of MP-1's and W2b's dumps was not checked
here; 3b, 3c and 5B depend on them.

## Sources

- **Repository records:** read at `origin/main` `3ae3c64c6`, in a detached worktree.
- **Cluster:** `ls` only, on login33, 2026-10-28, under `$P/measurement-paper/phase1/mp1/s1/`,
  `$P/w2-recoil-20261006/w2b/` and `$P/MINERvA-OmniFold/nd-unfolding/`. Nothing was read under `fd-f1-20261027/f1b/`
  or `f1b2/`.
- **The consult** (`2d-closeout/stageF/methods/secondary-results/astra-consult-coverage-20261028/answer.txt`) was read
  as a source of questions; each claim used here is checked against the records cited beside it.
