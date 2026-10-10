# D-ID — binned exact-response diagnostic of the scalar-5D GBDT residual

**CITABLE FOR:** the frozen D-ID implementation (`did.py`, `config.json`) and its synthetic controls
(`test_did.py`); the prospective amendments to gbdt REPORT §6 recorded here before any real input was
opened (§3); the resolution of the post-review branch-B route (§4); the meaning and limits of the
diagnostic labels (§5); and, once filled in, the results, the independent verification and the
disposition (§§8–12).
**NOT CITABLE FOR:** a measured cross section, an interval, a coverage result, an estimator, a
ratified gate, compute authority, or any regrading of s5c/s5n/s5e/s5p. Every result is
simulation-only. It is conditional on the fixed detector response, the signal-only binned
construction and the development departures. The 2.5% / 10% widths, the 5% allowance and the 2%
eligibility floor are **proposals carried from the gbdt lane, not gates**. This diagnostic does not
validate intervals, does not resolve the 2D pairing problem, and does not achieve a joint-5D
publication-ready measurement.

| field | content |
|---|---|
| `Lane` | D-ID owner (bounded local diagnostic) |
| `Decision` | At the declared response binning, truth resolutions and reporting functionals, which parts of the observed GBDT residual are consistent with finite-iteration regularization, GBDT approximation/bookkeeping, or weakly constrained response directions? Which conditional next step, if any, is justified? |
| `Branch` / `Base` | `study/d-id-20261009` / `a16d578646936a0cc6eca41e3e0350e756ee0dca`: the verified main pin, merge of PR #68, recorded in that PR's delivery comment; `origin/main` was equal to it at 2026-10-10T04:34Z |
| `Owned files` | `docs/orchestration/state/next-preparation-20261009/d-id/` only: this report, `did.py`, `config.json`, `test_did.py`, `outputs/` (numerical outputs and manifests) and the preserved review records |
| `Immutable inputs` | the `gbdt/` subtree (design, `comparator.py`, reviews, `results.json`); the committed nd-unfolding code, ratio files, receipts and synthesis operands named in `config.json`; the cluster products in §1 |
| `Authority` | Joseph's D-ID prompt (2026-10-09): implementation, one admission review, then (on PASS) the named local calculation. No training, no s5p extension, no Slurm/GPU/login-node computation |
| `Resources` | §7 |
| `Review` | §0; records in §8 and §10 |
| `Model / effort` | owner: Claude Opus 5.5 (`claude-opus-5-5`), Claude Code; effort not observable to the session |
| `Disposition` | §11 |
| `Next action` | §12 |

`Q` = `docs/orchestration/state/next-preparation-20261009`. "§6" alone means gbdt REPORT §6.

## 0. Setup (campaign review §1)

- **Roles.** One owner (this session) and one fresh read-only reviewer. CAMPAIGN-REVIEW §5 suggests
  Astra High for consequential review, but it is not reachable from this session. The reviewer is a
  fresh Claude subagent in its own detached worktree, so the review is not cross-provider
  independent. The prompt authorizes exactly this reviewer and no other workers or peer messages.
- **Review budget (whole session).** One admission review of the frozen commit, one final numerical
  verification after the run, and at most one focused repair/re-review. If a required design repair
  uses that allowance and a later material issue appears, the session ends INCONCLUSIVE.
- **Terminal outcomes.** Each of four questions gets its own PASS / FAIL / INCONCLUSIVE:
  implementation, admission, numerical verification and the discriminating question (§11). A
  scientifically supported no-go counts as a completed diagnostic.
- **Caps.**
  - 10 active hours.
  - Local CPU: preparation and synthetic work ≤ 2 core-h. The real diagnostic plus the independent
    numerical verification ≤ 8.8 core-h, with ≥ 20% protected, so the owner's run is capped at
    7.04 core-h (§7). Combined ceiling 10.8 core-h.
  - Two compute threads, 8 GiB RAM, 2 GiB scratch, 10 MiB tracked numerical evidence.
  - Cluster use: read-only `ls` and file copies only.

## 1. Inputs and identities

| role | object | identity (checked by the driver unless stated) |
|---|---|---|
| events | `of_inputs_5d.npz` (cluster `/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/`, 1,548,438,020 B, present 2026-10-10T04:3xZ) | sha256 `07fccc1a…` (A1); the MC keys only (A10, AM-17) |
| study-K traces | `s5p-20260926/runs/s2/conv/k_b0_{nominal,w3}.npz`, `k_b0_{gibuu,q3,w1}.npz.partial.npz`, `k_cap10_{gibuu,q3,w3}.npz` | sha256 equal to the synthesis `inventory.json` (A4). Sizes are equal to it at the listing |
| s5e diagnosis products | `s5e-20260925/runs/diag/asimov/asimov_{b0,cap,unity}_*.npz`; `trace/trace_{eavail,q3,nominal}_sig_s30x00{0–3}.npz` | no committed byte digest exists. Admitted by their embedded input digest and construction, and by reproducing the diag receipt's S_dep and λ_5D (AM-13); their sha256 is recorded |
| truth reweights | committed `s5n_pseudo.truth_weight` after `s5p_converge.install()` (+ `s5p_truths` for `cond_ratio`); ratio files `45cc3e0a…` (GiBUU), `2a208df9…` (W1), `80e16f95…` (W2), `3455daf3…` (W3), `9240e4b3…` (P1r), `6a36c9bc…` (P2r), `b3108969…` (P3r); q3 = `q3_given_eavail_w`, a = 0.3 | file digests (A3); module digests in `config.json`, which equal those recorded in the study-K products' `code_sha256` for every weight-path module; A5 (§3) checks the outcome |
| binning, extraction, functionals | `s5e_trace.flat_index`, `xsec_nd.extract_cross_section_nd`, `s5c_coverage.reported_functionals` + `s5p_converge.h2_rows` (185 rows, the traces' own) | module digests; name list equal to each complete trace's `functional_names` (A4) |
| labels and thresholds | `Q/gbdt/comparator.py` | sha256 `f5374fe0…`, imported, never copied |
| W2 comparator | `assessment_W2` / `assessment_W2_truth` of the synthesis `operands.npz` (`61c32477…`) | committed |
| receipts | s5p `stage2_receipt.json` (`0daa7cd8…`), s5e `diag_receipt.json` (`f0880725…`) | committed |

The real-data members of the event file (`measured`, `measured_weights`) are never read. No sealed
bank, no data file and no new simulation is used.

## 2. What the driver computes (§6 computations 1–5)

For each of nine weight sets (nominal, GiBUU, W1, W3, q3, W2, P1r, P2r, P3r), with truth grids T1 (J
cells), T2 (J split at the nearest interior fine edge) and T3 (fine), the two sample roles and the two
response weightings:

1. IBU from the nominal prior, K = 1…200 (sparse response). Residuals are taken on all 183 named
   functionals; the decision uses the 175 reported ones.
2. IBU to convergence at T1 and T2, same-sample, nominal-weighted. The stopping rule is a largest
   relative cell change < 1e-10, or 10⁵ iterations. Non-convergence is recorded and blocks branch B.
3. Fisher `F = Rᵀ diag(1/(R t + b)) R` at T1 and T2, same-sample, both weightings (18 at T2). The
   eigendecomposition is reused for the CR width and the invisible share. Each is tested equal to
   `comparator.cr_width` / `invisible_share`.
4. The invisible share of the GBDT's final fine-grid residual, aggregated to T1/T2, where such an
   estimate exists (AM-9).
5. Labels (`comparator.classify`), the pooled per-map aggregation (`comparator.branch_outcome`, through
   the stage-4 wrapper `declare`), the branch-B trace reading (§4) and the missed-event concentration
   (`comparator.missed_concentration`).

Admission checks (stage 1; any failure stops everything after it):

- A1: event digest.
- A2: the committed records and operands the run reads (receipts, inventory, definition, operands).
- A3: ratio-file digests.
- A4: trace digests, names and input digests. The committed functional rows must be exactly the 185
  study-K rows, equal to a list built from the operands (AM-32/M1).
- A5: the committed reweights reproduce every comparator's own truth functionals within 1e-9 relative.
- A6: each receipt-limited trace prefix reproduces the stage-2 receipt's per-K median series within
  1e-9.
- A7: 10,499 reco cells; S_dep within 0.1% and the GBDT fold λ_5D within 2% at K = 5, 15, 30 of the
  diag receipt; my fold equals the s5e file's within 1e-9.
- A8: 20,402,110 signal pair rows (s5e geometry's `rows_eligible`).
- A9: edges equal `definition.json`.
- A10: the list of keys read.
- A11: every reweight is exactly 1 outside the grid (AM-28).

Controls:

- C1 (gating): same-sample nominal returns |r_IBU| ≤ 1e-8 at every K and grid.
- C2 (gating at T1): with the departure-weighted response, IBU(∞) reaches the exact truth within
  0.01 σ_c on identified functionals. At T2 it is reported only.

## 3. Prospective amendments to §6 (recorded before any real input was opened)

None of these changes a threshold, a grid, a departure, an iteration limit or the aggregation of
`comparator.py`. Each fixes something §6 leaves open, or corrects a factual reading of its inputs.
Each is coded in `did.py` where its tag appears.

| tag | §6 says / leaves open | fixed here | why |
|---|---|---|---|
| AM-1 | the primary asimov_same comparators are "background-inclusive (`no_background: False`)", so confound (a) applies | **Correction:** asimov_same has no background on either side. `s5e_trace.asimov_same` uses the reco-passing *signal* MC rows reweighted by `r` as the measured side. "No Poisson, no background, no refinement" (docstring). `no_background: False` is the unused CLI default, which the tool refuses to change for non-pseudo constructions. Confound (a) therefore does not apply to the primary comparison. It still applies to the D3 `_bkg` runs (not used) and to any transfer to real data. It is preserved in §5 | the code is the authority for what the comparator measured |
| AM-2 | truth-passing rows whose truth lies outside the 5D grid (including the −9999 sentinels, which B0 did not drop) | their reco enters the pseudo-data, as in asimov_same. Their reweight is 1 in every construction, so the IBU carries their fold as a **known additive term b**. Same-sample this is exact; split-half takes it from half A | the reference IBU has no such term; dropping the rows would change the data |
| AM-3 | empty truth cells "dropped and listed"; nothing on zero-efficiency cells | a cell with truth weight but no reco keeps its prior (the reference would raise). It is an exact null direction of F, so every functional touching it is σ = ∞ | otherwise T2/T3 IBU cannot run |
| AM-4 | how an IBU estimate on T1/T2 becomes a functional value | each cell's estimate is spread over its fine cells in proportion to that weighting's own MC truth shape, then passed through the committed extraction and functional rows. The CR map is that same linear map. Relative σ = σ / \|h·t\| at that weighting | the only construction that is exact when the shape is right; tested both ways |
| AM-5 | the "binning bias" as "its own number" | r_IBU is relative to the exact fine-grid departure truth (the comparators' own `fn_true`). Binning bias = r_IBU(nominal-weighted) − r_IBU(departure-weighted), at the same grid and K | the GBDT residual is measured against the same truth |
| AM-6 | the content of each priority stage | (1) admission + C1; (2) T1: same-sample both weightings, K ≤ 200, Fisher, labels, convergence, exactness (C2); (3) T2: same-sample both weightings, Fisher, labels, K ≤ 200; (4) T2 convergence; (5) T3 same-sample and all split-half trajectories, then the T2 exactness report | the resolution-sensitivity rule needs the T2 departure-weighted labels, so they cannot wait for stage 5 |
| AM-7 | "a functional whose label changes between T1 and T2, or between nominal- and departure-weighted responses" | label = `classify`'s (iteration, identifiability) pair at K = 5. Compared T1 vs T2 (nominal, same-sample) and nominal vs departure weighting (T2, same-sample) | explicit operands |
| AM-8 | branch-B route (post-review, unreviewed) | §4 | the issue the prompt names |
| AM-9 | "the invisible share of the GBDT final-K residual" | computed from a fine-grid GBDT estimate where one exists. W3 and nominal use the K = 200 traces. GiBUU and q3 use the s5e D4 asimov_b0 products at K = 30 (same B0 asimov_same construction). W1 and W2 are **missing**: partial checkpoints carry no fine-grid estimate, and W2 has only an ensemble mean. The residual is converted to counts by the extraction's per-cell factor, and fine cells with no factor are set to zero | the partial checkpoints store functionals only (`s5p_converge.install_checkpoints`) |
| AM-10 | "each functional's missed-event fraction" | the share of the functional's departure-weighted truth carried by truth-passing, reco-failing rows. The concentration is computed per departure and map, over the reported functionals with a comparator. Excess = \|r_GBDT(5) − r_IBU(5)\| at T2, nominal, same-sample. Descriptive (§5) | |
| AM-11 | "the existing split key" | `half_mask(n_rows, key)` with key = `split_key_for(301000)` = 798,985,164,084,644, the first D3 signal-only E_avail trace's. It must equal that product's recorded `split_key` bitwise, or split-half is missing. Half B is the pseudo-data source, half A the response/prior/known-term half, both ×2 (s5n) | |
| AM-12 | P1r–P3r construction | a = 1, the s5p power construction (amendments 7/8). P1r/P3r through `ratio_nd` (`s5e_deform`), P2r through `cond_ratio` (`s5p_truths`) | |
| AM-13 | "digests equal to `inventory.json` and to the diag receipt's inputs" for the s5e secondaries | no byte digest of them is committed. They are admitted by embedded `input_npz_sha256` + construction and by A5/A7 reproduction; their sha256 is recorded | |
| AM-14 | the W2 comparator | the mean over the 20 R K = 5 experiments of `fhat/ftrue − 1` (the synthesis definition), at K = 5 only | |
| AM-15 | Fisher `F = Rᵀ diag(1/y) R` | **a correction, not a fill-in** (review m5): F is evaluated with that weighting's response at the departure's binned truth, `Rᵀ diag(1/(R t + b)) R`. This equals §6's formula for the departure-weighted response. For the nominal-weighted response it differs from it by the binning bias in the variance | local Fisher at the true parameter; b in the variance |
| AM-16 | cap enforcement | before each unit, priced in `config.json` `price_s`, and every 1,000 iterations inside long loops, against 7.04 owner core-h of process CPU (all threads + children). Failed attempts count (`--spent-before-s`) | |
| AM-17 | none | the event file's real-data keys are never read. A synthetic file whose real-data members are corrupt proves it end to end | the prompt forbids real data |
| AM-18 | "relative truth change < 1e-10" | the largest over active cells of \|Δt\|/t | |
| AM-19 | T2 split at "the fine edge nearest its midpoint" | lower edge on a tie (pz bin [3.5, 6]: 4.5 vs 5.0). T2 = 6·6·6·4·6 = 5,184 cells at most | |
| AM-20 | "if all three sets are small, record INCONCLUSIVE" | small = every share < 1/3 | |
| AM-21 | event/split convention | A8 checks the signal pair-row count against s5e geometry's `rows_eligible` (pass_reco ∧ pass_truth ∧ both in grid) | an independent committed count |
| AM-22 | "at T2 the exactness control is reported" | the departure-weighted T2 convergence it needs is unpriced in §6, so it runs last in stage 5 and never gates | |
| AM-23 | C2 at T1 | the gate is the frozen criterion (error ≤ 0.01 σ_c on identified functionals); convergence is reported beside it | |
| AM-25 | none (repository convention) | `config.json` stores expected digests as `expect_sha256` / `ratio_expect_sha256` with no sibling path key, and `results.json` stores observed ones as `observed_sha256`. The repository's binding collector therefore counts them as unpaired (printed, not gated). The driver verifies every one at run time (A1–A4). The first freeze attempt was refused by the pre-commit hook, which pairs `path` + `sha256`. That would have changed the pinned receipt-binding inventory in `verify_hash_bindings.py`, a shared guard this lane does not own. The event file is cited with a directory (`nd-unfolding/of_inputs_5d.npz`, relative to the inputs directory), not bare | the gbdt lane's precedent (`results.json` `integrity`); registering these bindings is an integration-owner choice |
| AM-24 | which trace iterations are evidence | the receipt-verified prefixes only: GiBUU 40, W1 40, q3 30 (of 100/125/100 present), W3 and nominal 200. A6 checks the per-K median series at the receipt's K points. Together with the A4 file digest, this identifies each prefix with the one study K recorded (wording corrected, review m5) | N1: later iterations have unverified provenance |
| AM-26 | convergence for branch B (review M2) | **per functional.** A functional counts as converged when its own last-step relative change \|Δ(h·t)\|/\|h·t\| is below 1e-10 at the stop, or when the whole run met AM-18. The run-level rule and flag are kept and reported, and each functional's last-step change is in the tables | gbdt §6 says "a T2 *functional* that has not converged". A per-run flag would let one slow cell outside every reported functional remove all of them, which makes B structurally unreachable at 5,184 cells |
| AM-27 | A8 (review m1) | `rows_eligible` is recounted with its producer's own rule (`s5e_geometry.in_grid`, upper edge excluded, digest-pinned). The pair-row count (edges closed) is recorded beside it | the two rules differ on upper-edge rows |
| AM-28 | AM-2 premise (review m4) | A11 gates, in stage 1, that every weight set's reweight is exactly 1 on rows outside the grid | AM-2 uses the nominal known term b for every departure |
| AM-29 | B without stage 4 (review m2) | `B-undeclarable` only when B is reachable, i.e. its candidates are ≥ 1/2 of the eligible functionals. Otherwise the map is `mixed`, with `b_reachable = false`, the candidates listed and `stage4 = missing`. AM-20 then bounds B by its candidate share | B cannot reach its share whatever stage 4 would give |
| AM-30 | W2 in the pool (review m3) | the frozen pooled outcome is unchanged. Beside it, the shares with W2 left out are reported (`without_w2`), because W2's comparator is the background-inclusive, split-MC, Poisson R ensemble (E2) | input-role transparency |
| AM-31 | σ = ∞ causes (review m6) | each width records whether the functional's map has weight on a zero-efficiency cell (`acceptance_hole`). A C label with an acceptance hole is an acceptance gap, not a weak response | label meaning |
| AM-32 | caps and failures (review M3) | the RAM cap is checked at every budget check (peak RSS against 8 GiB), so a peak cannot be pre-empted, only stopped at the next check. Stored trajectories keep only K and r. Row arrays are freed after binning. The committed row-wise `flat_index`/`in_grid` run in row chunks (identical output, tested). Any other exception marks its stage `error` (exit 6), later stages are `not-started`, and once stage 1 is complete the decision and tables are always written | memory accounting and crash safety |

## 4. The branch-B route (the post-review issue, resolved before execution)

The gbdt lane repaired branch B after its last review (N1, #8): branch B is "first read from D-ID's
matched-K comparison against the existing s5p study-K traces". That repair named no computation, and
the integration report left it unreviewed. Without a computation, a B outcome could be read as "more
GBDT iterations would remove the residual". That claim belongs to the GBDT side of study K, which
terminal s5p already measured and which this prompt forbids extending.

**Frozen rule (AM-8).**

1. **Declaration is unchanged:** `comparator.branch_outcome` at K = 5, T2, same-sample,
   nominal-weighted. B needs the functional to be identified at target, iteration-faithful, and to
   have |r_IBU(∞)| ≤ 0.5 |r_GBDT(5)|. r_IBU(∞) comes from stage 4 and must be *converged for that
   functional* (AM-26). Non-converged functionals enter with r_IBU(∞) = ∞. If stage 4 is incomplete
   at the cap, the map's outcome is C or A if either reaches its share alone. Otherwise it is
   `B-undeclarable` with the candidates listed, unless B is unreachable (AM-29). It is never
   silently folded into mixed.
2. **Trace reading.** For every functional counted toward B, the driver reports K_max (the
   receipt-verified trace length: W3 200, GiBUU 40, W1 40, q3 30), r_GBDT(K_max) and r_IBU(K_max) at
   T2. Each gets one reading, using only the frozen 0.3 tolerance and the 2% floor:
   - `tracks`: still iteration-faithful at K_max, or both residuals ≤ 2%;
   - `departs`: the GBDT leaves the exact iteration's path inside the traced range;
   - `untraced`: W2, which has no trace beyond K = 5.
3. **What B may then say.** Only what the existing traces show. A `tracks` reading says the GBDT
   followed exact IBU over the traced range. Whether it would keep doing so beyond K_max is
   **unresolved by existing evidence**, and extending the traces needs its own authorization
   (≈ 8.7 node-h admitted, gbdt §6). A `departs` reading says the existing traces already contradict
   "iteration count" as the whole mechanism for that functional. B is never an instruction to
   iterate further, and nothing here re-runs study K.

## 5. Meaning of the labels, and their limits

- **Same-sample oracle.** The IBU unfolds the very MC rows that make its data, with exact efficiency.
  It is a diagnostic oracle, not an estimator. Its residual at finite K is regularization by early
  stopping. Its residual at convergence on the nominal-weighted response is within-cell binning bias
  plus the effect of null directions.
- **σ_c is a local, binned, model- and grid-dependent Cramér–Rao width** at the departure's own truth.
  It assumes the Poisson Gaussian limit and unbiasedness in the regular directions. It is
  signal-only: no background variance, which makes it optimistic. It does not bound biased
  estimators, unbinned estimators, or estimators that use prior information. Binned reco
  information is conservative relative to the unbinned data. Coarse truth cells hide within-cell
  freedom and are optimistic. These errors run in opposite directions, so neither T1 nor T2 bounds
  the truth. A label that changes between T1 and T2, or between weightings, is excluded from every
  branch, and the full tables keep it.
- **"Weakly identified" (C)** means: for binned estimators at this reco binning and T2 resolution, at
  the analysis exposure, the functional's CR width exceeds 10%. It is not an impossibility theorem.
- **A finite null-direction search cannot prove identifiability.** The null fraction is computed at a
  relative eigenvalue cut of 1e-12 (the reference's). Functionals with σ = ∞ are flagged, never
  dropped.
- **Missed-event concentration** (≥ 2/3 of the summed excess in the top missed-fraction tercile) has
  no null calibration. The gbdt reviewer's fixtures gave a 5–7% false-positive rate. It is
  descriptive, reported beside the branch, and never decides one.
- **Confounds preserved.**
  - Background: not present in the traced (asimov_same) comparators of GiBUU, W1, W3 and q3 (AM-1).
    It **is** present in W2's comparator, the candidate-R assessment ensemble (background-inclusive,
    split MC, Poisson). W2 enters the pool only through E2's agreement of noise-free and ensemble
    means, so the pooled shares are also reported without W2 (AM-30). Background is also present in
    D3 `_bkg` and in real data, where s5e D3 measured signal-only 10.5% / 74.1% against background-inclusive
    10.7% / 74.5% (E_avail, median/max EW at K = 5).
  - Missed events: the GBDT fills reco-failing rows with a regressor, while the IBU uses exact
    efficiency. That difference is part of what "approximation/bookkeeping" means here, and it is
    measured, not removed.
- **Inconclusive by construction.** Mixed outcomes, undeclarable B, no eligible functional and
  failed controls are INCONCLUSIVE for the discriminating question, not evidence for any mechanism.

## 6. Synthetic controls (`test_did.py`: 22 tests at the freeze `9203add1`, 29 after the admission repairs, all pass)

Unit-level fixtures (dense, small) against `comparator.py`:

| mechanism | fires on the defect | silent on the clean case |
|---|---|---|
| sparse response construction | — | equals a brute-force dense response (1e-13); same-sample y = R t + b exactly; empty cell dropped and listed |
| T2 split / J map | — | T2 edges as in AM-19; T1 cell of every fine cell equals the support of the committed J rows |
| IBU | the reference refuses a zero-efficiency cell | equals `comparator.ibu` at every K (1e-12); with a known term the nominal closes exactly; a zero-efficiency cell keeps its prior |
| convergence / non-convergence | a 20-iteration cap reports `converged = False` | converges below 1e-10 |
| singular Fisher / null space | a duplicated response column makes the difference functional σ = ∞ (null fraction > 0.99) | the sum and an unrelated functional stay finite; Fisher, widths, null fractions and invisible share equal the reference (1e-12); a known term widens σ |
| functional projection | nominal shares on a within-cell departure give a > 0.1% bias | own shares are exact (1e-13); the fine grid has no binning freedom |
| branch aggregation | B-undeclarable when stage 4 is missing; non-converged B candidates fall out of B; tie listed | B, C declared when they should be; `b_counted` equals `branch_outcome`'s B count over 200 random label sets |
| sensitivity / trace reading | a changed label is flagged | `tracks` / `departs` / `untraced` each reached |
| receipt-prefix check (A6) | a 0.1% tampered median, a one-sided NaN and a shifted prefix are caught | exact series → 0 |
| cap / interruption | a 1e-9 core-h budget raises before work and inside an IBU loop; a 1-byte RAM cap raises at the next check | — |
| functional rows (M1) | — | the committed rows are exactly 185 and equal a name list written independently in the test from the operands; H2 is not stacked twice; the end-to-end traces use that independent 185-column layout |
| per-functional convergence (M2) | a functional on a slow, decoupled block stays unconverged | the run is not converged, but the two functionals away from the block are (last step < 1e-12) |
| B reachability (m2) | — | without stage 4 and with a 1/4 candidate share the map is `mixed` with `b_reachable = false` |
| chunked binning (M3) | — | chunked `flat_index` / `in_grid` equal the unchunked ones, including rows on upper edges |
| errors (M3) | an exception injected in stage 4 → exit 6, stage 4 `error`, stage 5 `not-started` | the decision and tables of stages 1–3 are still written; stored trajectories hold only K and r |

End to end, on a synthetic event file with the real 5D grid, the real functional rows and the real
reweight code (40,000 rows; truth in 32 J cells; 30% missed; 40 sentinel rows inside pass_truth), plus
GBDT stand-ins written as `factor × exact T2 IBU residual` at every K:

- **Resolution-sensitivity positive control** (factor 1). Every functional above 2% is
  iteration-faithful at the primary setting. Every one is excluded because the departure-weighted
  label differs (the residual is binning bias). Each map gives `no-eligible-functional`. All stages
  complete, every gating control passes, and the real-data members (deliberately corrupt) are never
  read.
- **Binning-bias negative control** (J-constant departures). Binning bias < 1e-9 everywhere, labels
  equal across weightings, A share 0.
- **Approximation** (factor 5, identified exposure) → J branch **A**.
- **Weak exposure** (same, weights × 1e-6) → J branch **C**.
- **Cap during stage 4** → stage 4 `cap`, stage 5 `not-started`, each map C, A, `B-undeclarable` or
  no-eligible. **Cap during stage 1** → no decision.
- **Tampered input digests** (event, a trace) → exit 4 at that check, later stages not started.
- **Thread limit above 2** → refused.

The small world cannot exercise A6 end to end (some reported functionals are empty there, so the
receipt medians are NaN). A6 has its own finite-valued control, and on the real inputs the driver
records the NaN-median count (expected 0). An end-to-end B case needs larger residuals that are
stable across T1/T2 than this world gives. B is controlled at the aggregation level instead.

Resources of the full suite: 79 s CPU (≈ 0.02 core-h), peak RSS 0.59 GB, two threads (after the repairs).

## 7. Cost, memory and the frozen fallbacks

- **Owner run cap:** 7.04 core-h, i.e. 8.8 minus max(20% = 1.76, the priced 1.0 verification). The
  run stops before a unit that cannot fit and keeps completed stages. The reviewer's verification
  must fit in the remaining ≥ 1.76 core-h.
- **Expected owner run**, from the §6 price, re-derived for T2 = 5,184 cells (not 7,776):
  - histograms ≈ 0.05–0.3 core-h;
  - trajectories ≈ 0.1;
  - T1 convergence + exactness ≤ 0.5 at the 10⁵ worst case;
  - T2 convergence ≤ 1.4 worst case;
  - 18 + 18 Fisher eighs at T1/T2 ≈ 0.2;
  - T2 exactness (stage 5, report only) ≤ 1.4 worst case.

  This is ≈ 1–4 core-h, below the cap with margin.
- **Memory (measured after the M3 repair).**
  - Method: stage-1 row work (load, binning, the nine reweights, the pair tables) in a fresh
    process, on synthetic files with the real per-row layout (58 B/row).
  - Peak RSS: 1.06 GB at 4 M rows and 1.57 GB at 8 M rows, i.e. ≈ 0.13 GB per million rows plus
    0.55 GB fixed.
  - Real file: the 1.548 GB file holds at most ≈ 26.7 M MC rows at that layout, so ≈ 4 GB. Adding
    ≈ 1 GB because the real file has more distinct signal pairs (76% of rows, against 46% in the
    synthetic file) gives ≈ 5 GB, below 8 GiB.
  - Later stages: the dense T2 Fisher is ≤ 215 MB (the cap rule drops T2 only above 6 GiB). A T3
    problem is ≈ 0.2–0.3 GB and is not retained.
  - The RSS guard stops the run at the next check if this estimate is wrong. Stage-1 CPU was 18 s at
    8 M rows, so ≈ 1 min at full size.
- **Scratch:** the event file 1.442 GiB, plus ≈ 30 MB of comparators and ≈ 0.1–0.2 GB of
  verification operands, below 2 GiB. All of it is deleted at delivery. The column-extract alternative
  would need login-node computation, so it is not used.
- **If a cap is reached:** the frozen stage rule of §4/§6 applies. Nothing is retuned.

## 8. Admission review

**Verdict at `9203add1`: ADMIT-WITH-REPAIRS** (record: [`review-admission.md`](review-admission.md)).
The reviewer was a fresh Claude Opus 5.5 subagent, read-only, in a detached worktree, and used
≈ 0.06 core-h. It reproduced with its own code:

- the IBU (with the known term and a zero-efficiency cell);
- Fisher, CR widths, null fractions and the invisible share;
- the T2 edges and the J map against the committed rows;
- the B count against `branch_outcome` (3,000 trials);
- end-to-end A, B (`tracks` and `departs`) and C cases through the library functions.

It found no numerical disagreement. It confirmed:

- AM-1: asimov_same is background-free;
- AM-3, AM-11, AM-12 and AM-14;
- that the study-K weights match;
- that the driver can neither fit nor extend s5p;
- that no threshold, grid, departure, iteration limit or aggregation changed.

It judged the CPU cap credible, with an overrun of at most ≈ 14 s. It judged the branch-B route
adequately specified once M2 is fixed.

| # | severity | finding | disposition (one repair batch, commit after `9203add1`) |
|---|---|---|---|
| M1 | MATERIAL | the H2 rows are stacked twice (217 rows), so the real 185-column traces fail A4; the fixture traces were derived from the driver's own list | **fixed:** the committed rows are used as returned. A4 now also checks they equal a list built from the operands. The test builds the name list independently and writes the end-to-end traces in that 185-column layout |
| M2 | MATERIAL | B convergence is judged per run, but §6 says per functional; one slow cell makes B unreachable | **fixed prospectively, AM-26**: per-functional last-step criterion, run-level flag kept; decoupled-slow-block control |
| M3 | MATERIAL | RAM cap unenforced; trajectories retain their operands; row count understated; generic exceptions lose the decision | **fixed, AM-32**: RSS guard; only K and r retained; row arrays freed; chunked binning; per-stage error capture with the decision always written; memory re-measured at 4 M and 8 M rows (§7) |
| m1 | MINOR | A8 in-grid rule differs from the producer's | **fixed, AM-27** |
| m2 | MINOR | B-undeclarable even when unreachable | **fixed, AM-29** |
| m3 | MINOR | W2's comparator is background-inclusive | **fixed, AM-30** and §5 |
| m4 | MINOR | AM-2's premise not gated | **fixed, AM-28** (A11) |
| m5 | MINOR | AM-15 and AM-24 described inaccurately | **fixed** (wording) |
| m6 | MINOR | C does not say why σ = ∞ | **fixed, AM-31** |

The session's one focused re-review is used on this batch.

## 9. Stage B results

*Pending: Stage B is not released.*

## 10. Final numerical verification

*Pending.*

## 11. Disposition

*Pending.* Verdict definitions, fixed now:

- **Implementation:** PASS when the frozen driver passes its synthetic controls and runs the admitted
  stages without a defect found by review.
- **Admission:** the reviewer's verdict on the frozen commit.
- **Numerical verification:** PASS when the reviewer's separately implemented recomputation agrees
  with the consequential reductions and branch outcomes; FAIL on a demonstrated disagreement;
  INCONCLUSIVE if it could not be done.
- **Discriminating question:** PASS when stages 1–3 complete with the gates passed and the J map (the
  joint endpoint at issue) returns C, A, B, or mixed with at least one share ≥ 1/3. Otherwise
  INCONCLUSIVE (failed gate, incomplete stages, `B-undeclarable` without C/A, no eligible functional,
  or all shares < 1/3). FAIL is not reachable under §6 (control failures are INCONCLUSIVE); EW and
  H2 are reported beside J.

## 12. Next decision

*Pending.*
